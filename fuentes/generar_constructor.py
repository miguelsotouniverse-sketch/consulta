#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENERA `construir_indicaciones.py` A PARTIR DE `indicaciones_base.json`
=======================================================================

Por qué un generador y no transcribir a mano
--------------------------------------------
Las ocho hojas originales son 233 bloques de texto clínico. Teclearlas en un
archivo de Python es una tarde de trabajo y, lo que importa, una tarde de
oportunidades de equivocarse: una palabra cambiada en una indicación de alta
no la nota nadie hasta que una paciente hace lo que no era.

Así que no se transcriben: se LEEN del respaldo y se EMITEN como código. El
texto no pasa por manos humanas ni por las mías, pasa por `repr()`. Y después
se comprueba lo único que importa: que el constructor emitido reproduzca el
JSON original byte por byte.

Este archivo se corre UNA VEZ. Lo que queda para el día a día es
`construir_indicaciones.py`, que sí es el archivo que se edita cuando hay que
corregir una hoja.

Uso:  python3 generar_constructor.py [indicaciones_base.json] [salida.py]
"""

import json
import sys

ENTRADA = sys.argv[1] if len(sys.argv) > 1 else 'fuentes/indicaciones_base.json'
SALIDA  = sys.argv[2] if len(sys.argv) > 2 else 'construir_indicaciones.py'

cat = json.load(open(ENTRADA, encoding='utf-8'))


def txt(s, sangria):
    """Un string de Python, partido en renglones legibles si es largo."""
    s = str(s)
    if len(s) <= 70:
        return repr(s)
    # se parte por palabras, en trozos de ~68 caracteres, concatenación implícita
    palabras, lineas, actual = s.split(' '), [], ''
    for p in palabras:
        if len(actual) + len(p) + 1 > 68 and actual:
            lineas.append(actual + ' ')
            actual = p
        else:
            actual = (actual + ' ' + p) if actual else p
    if actual:
        lineas.append(actual)
    sep = '\n' + ' ' * sangria
    return sep.join(repr(l) for l in lineas)


def bloque(b, s=8):
    t = b['t']
    i = ' ' * s
    al = ', alarma=True' if b.get('alarma') else ''
    if t in ('h', 'h2'):
        return '%s%s(%s%s),' % (i, t, txt(b['x'], s + 3), al)
    if t == 'p':
        return '%sp(%s),' % (i, txt(b['x'], s + 2))
    if t == 'ul':
        dentro = ''.join('\n%s    %s,' % (i, txt(x, s + 6)) for x in b['x'])
        # los renglones ya terminan en coma, así que la bandera entra sin otra
        return '%sul(%s\n%s%s),' % (i, dentro, i,
                                    'alarma=True' if b.get('alarma') else '')
    if t == 'nota':
        extra = ', alarma=True' if b.get('alarma') else ''
        return '%snota(%s%s),' % (i, txt(b['x'], s + 5), extra)
    if t == 'firmas':
        return '%sfirmas(%s),' % (i, ', '.join(repr(x) for x in b['x']))
    if t == 'tabla':
        filas = ''.join('\n%s        [%s],' % (i, ', '.join(txt(c, s + 9) for c in f))
                        for f in b['x'])
        return ('%stabla(\n%s    [%s],\n%s    [%s\n%s    ],\n%s),'
                % (i, i, ', '.join(repr(c) for c in b['cols']), i, filas, i, i))
    if t == 'citas':
        filas = ''.join(
            '\n%s        {%s},' % (i, ', '.join('%r: %s' % (k, txt(v, s + 11))
                                                for k, v in c.items()))
            for c in b['x'])
        return ('%scitas(\n%s    [%s],\n%s    [%s\n%s    ],\n%s),'
                % (i, i, ', '.join(repr(c) for c in b['cols']), i, filas, i, i))
    # tipo que no conocía: se emite crudo, para no perderlo en silencio
    return '%scrudo(%s),  # ←REVISAR  tipo de bloque no previsto: %r' % (
        i, json.dumps(b, ensure_ascii=False), t)


partes = []
for h in cat['hojas']:
    campos = [
        "    'id': %r," % h['id'],
        "    'nombre': %s," % txt(h['nombre'], 8),
        "    'titulo': %s," % txt(h['titulo'], 8),
        "    'coincide': [%s]," % ', '.join(repr(c) for c in h['coincide']),
        "    'entrada': %s," % txt(h.get('entrada', ''), 8),
        "    'bloques': [",
    ]
    campos += [bloque(b) for b in h['bloques']]
    campos.append('    ],')
    partes.append(' {\n%s\n },' % '\n'.join(campos))

CUERPO = '\n'.join(partes)

PLANTILLA = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAS OCHO HOJAS ORIGINALES DE INDICACIONES
==========================================

Qué es esto
-----------
El texto de las ocho hojas que existían antes de octubre de 2026 —Deep Plane,
lipoescultura, mastopexia, rinoplastia, blefaroplastia, faja, preoperatorias y
laboratorios—, escrito como código en vez de como JSON.

Antes, corregir una palabra de una hoja significaba editar `indicaciones.json`
a mano, entre miles de renglones, sin manera de saber después por qué decía lo
que decía. Ahora se corrige AQUÍ, se vuelve a correr, y el JSON se regenera.

Este archivo se generó con `generar_constructor.py` leyendo
`indicaciones_base.json`: el texto nunca se retecleó, se emitió. Y se comprobó
que lo que produce es idéntico, byte por byte, al archivo del que salió.

Cómo encaja en la cadena
------------------------
Es el PRIMER paso. Sustituye al `cp indicaciones_base.json indicaciones.json`:

    python3 fuentes/construir_indicaciones.py        ← este archivo
    python3 fuentes/corregir_drenajes.py
    python3 fuentes/corregir_dieta_submandibular.py
    ... y el resto, en el orden del README

Los correctores que vienen después siguen funcionando igual: buscan un texto
exacto y fallan ruidosamente si ya no está. Si usted corrige aquí una frase que
un corrector busca, el corrector se queja —y hace bien, porque entonces el
parche ya no hace falta y hay que quitarlo de la cadena.

La versión de cada hoja y la del catálogo son hashes de su propio contenido: si
usted no cambia nada, salen idénticas; si cambia una coma, cambian solas.

Uso:  python3 construir_indicaciones.py [salida.json]
"""

import json
import hashlib
import datetime
import sys

SALIDA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'


# --- los ocho tipos de bloque que entiende la hoja ------------------------
def _al(b, alarma):
    """`alarma` pinta el bloque como signo de alarma. Va en encabezados,
       listas y notas: los tres pueden formar parte de esa caja."""
    if alarma:
        b['alarma'] = True
    return b

def h(x, alarma=False):       return _al({'t': 'h',  'x': x}, alarma)
def h2(x, alarma=False):      return _al({'t': 'h2', 'x': x}, alarma)
def p(x):                     return {'t': 'p',  'x': x}
def ul(*xs, **kw):            return _al({'t': 'ul', 'x': list(xs)}, kw.get('alarma'))
def firmas(*xs):              return {'t': 'firmas', 'x': list(xs)}
def tabla(cols, filas):       return {'t': 'tabla', 'cols': cols, 'x': filas}
def citas(cols, filas):       return {'t': 'citas', 'cols': cols, 'x': filas}
def nota(x, alarma=False):    return _al({'t': 'nota', 'x': x}, alarma)
def crudo(s):                 return json.loads(s)


HOJAS = [
%s
]


for _h in HOJAS:
    _h['version'] = hashlib.sha256(json.dumps(
        _h, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

_cat = {
    'hojas': HOJAS,
    'version': hashlib.sha256(json.dumps(
        {'hojas': HOJAS}, ensure_ascii=False, sort_keys=True
    ).encode('utf-8')).hexdigest()[:16],
    'generado': datetime.date.today().isoformat(),
}

with open(SALIDA, 'w', encoding='utf-8') as _f:
    json.dump(_cat, _f, ensure_ascii=False, indent=1)

print('%%d hojas  ·  catalogo %%s' %% (len(HOJAS), _cat['version']))
for _h in HOJAS:
    print('   %%-16s %%s' %% (_h['id'], _h['version']))
''' % CUERPO

open(SALIDA, 'w', encoding='utf-8').write(PLANTILLA)
print('emitido %s  (%d bytes, %d hojas)' % (SALIDA, len(PLANTILLA), len(cat['hojas'])))
