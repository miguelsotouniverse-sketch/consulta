#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENERA `construir_recetas.py` A PARTIR DE `recetas_base.json`
==============================================================

El mismo método que se usó para las diez hojas de indicaciones, aplicado
ahora a las cuatro plantillas de receta originales: Deep Plane, Body360,
blefaroplastia y rinoplastia.

Por qué generar y no transcribir
--------------------------------
Son 51 renglones de medicamento con sus dosis, sus condiciones y sus
cantidades, más 39 signos de alarma y 30 avisos. Teclear eso a mano es una
tarde entera de oportunidades de cambiar un «cada 8 horas» por un «cada 12».
Aquí el texto no pasa por manos: se lee del respaldo y se emite con `repr()`,
y después se comprueba que lo emitido reproduzca el JSON original —contenido
y las cuatro versiones— exactamente.

Se corre UNA VEZ. Lo que queda para el día a día es `construir_recetas.py`.

Uso:  python3 generar_constructor_recetas.py [recetas_base.json] [salida.py]
"""

import json
import sys

ENTRADA = sys.argv[1] if len(sys.argv) > 1 else 'fuentes/recetas_base.json'
SALIDA  = sys.argv[2] if len(sys.argv) > 2 else 'construir_recetas.py'

cat = json.load(open(ENTRADA, encoding='utf-8'))


def txt(s, sangria):
    """Un string, partido en renglones legibles si es largo."""
    s = str(s)
    if len(s) <= 64:
        return repr(s)
    palabras, lineas, actual = s.split(' '), [], ''
    for p in palabras:
        if len(actual) + len(p) + 1 > 62 and actual:
            lineas.append(actual + ' ')
            actual = p
        else:
            actual = (actual + ' ' + p) if actual else p
    if actual:
        lineas.append(actual)
    sep = '\n' + ' ' * sangria
    return sep.join(repr(l) for l in lineas)


def plit(o):
    """Literal de Python, no de JSON: `True`, no `true`. repr() de un dict con
       llaves y valores simples produce exactamente eso, y conserva el orden."""
    return repr(o)


def med(m, s=8):
    i = ' ' * s
    partes = ['%smed(%r,' % (i, m['hoja']),
              '%s    %s,' % (i, txt(m['nombre'], s + 8)),
              '%s    %s,' % (i, txt(m['indicacion'], s + 8)),
              '%s    cantidad=%s,' % (i, txt(m['cantidad'], s + 13)),
              '%s    duracion=%s,' % (i, txt(m['duracion'], s + 13))]
    if m.get('si'):
        partes.append('%s    si=%s,' % (i, plit(m['si'])))
    if m.get('rescate'):
        partes.append('%s    rescate=True,' % i)
    if m.get('horario'):
        partes.append('%s    horario=%s,' % (i, plit(m['horario'])))
    partes.append('%s),' % i)
    return '\n'.join(partes)


def simple(o, s=8):
    return '%s%s,' % (' ' * s, plit(o))


def alarma(a, s=8):
    i = ' ' * s
    if a.get('si'):
        return '%sal(%s,\n%s   si=%s),' % (i, txt(a['t'], s + 4), i, plit(a['si']))
    return '%sal(%s),' % (i, txt(a['t'], s + 4))


partes = []
for p in cat['plantillas']:
    bloque = [
        " {",
        "  'id': %r," % p['id'],
        "  'nombre': %s," % txt(p['nombre'], 12),
        "  'coincide': [%s]," % ', '.join(repr(c) for c in p['coincide']),
        "  'procedimiento': %s," % txt(p['procedimiento'], 18),
    ]
    if 'procedimientoBichat' in p:
        bloque.append("  'procedimientoBichat': %s," % txt(p['procedimientoBichat'], 24))
    bloque.append("  'preguntas': [")
    bloque += [simple(q, 3) for q in p['preguntas']]
    bloque.append("  ],")
    bloque.append("  'medicamentos': [")
    bloque += [med(m, 3) for m in p['medicamentos']]
    bloque.append("  ],")
    bloque.append("  'profilaxis': [")
    bloque += [simple(x, 3) for x in p['profilaxis']]
    bloque.append("  ],")
    bloque.append("  'profilaxisNota': %s," % txt(p['profilaxisNota'], 20))
    bloque.append("  'avisos': [")
    bloque += [simple(x, 3) for x in p['avisos']]
    bloque.append("  ],")
    bloque.append("  'alarma': [")
    bloque += [alarma(x, 3) for x in p['alarma']]
    bloque.append("  ],")
    bloque.append("  'horaNota': %s," % txt(p['horaNota'], 15))
    bloque.append(" },")
    partes.append('\n'.join(bloque))

PLANTILLA = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAS CUATRO PLANTILLAS DE RECETA ORIGINALES
===========================================

Qué es esto
-----------
El texto de las recetas que existían antes de octubre de 2026 —Deep Plane,
Body360, blefaroplastia y rinoplastia— escrito como código en vez de como
JSON: cada medicamento con su indicación, su cantidad, su duración, la
condición que lo enciende y su horario.

**Éste es el archivo que se edita cuando hay que corregir una receta
original.** Antes había que editar `recetas.json` a mano entre miles de
renglones, sin manera de saber después por qué decía lo que decía.

Se generó con `generar_constructor_recetas.py` leyendo `recetas_base.json`:
el texto nunca se retecleó, se emitió, y se comprobó que lo que produce es
idéntico —contenido y las cuatro versiones— al archivo del que salió.

Cómo encaja en la cadena
------------------------
Es el primer paso del lado de las recetas. Sustituye al
`cp recetas_base.json recetas.json`:

    python3 fuentes/construir_indicaciones.py     ← las 10 hojas
    python3 fuentes/construir_recetas.py          ← este archivo
    python3 fuentes/corregir_drenajes.py
    ... y el resto, en el orden del README

Los constructores que vienen después —la combinada, eCO₂, mastopexia— copian
renglones de estas cuatro por índice o por nombre. Si usted cambia aquí el
paracetamol, cambia en las siete.

Uso:  python3 construir_recetas.py [salida.json]
"""

import json
import hashlib
import datetime
import sys

SALIDA = sys.argv[1] if len(sys.argv) > 1 else 'recetas.json'


def med(hoja, nombre, indicacion, cantidad, duracion,
        si=None, rescate=False, horario=None):
    """Un renglón de receta. El orden de las llaves es el del archivo original."""
    m = {'hoja': hoja, 'nombre': nombre, 'indicacion': indicacion}
    if si is not None:
        m['si'] = si
    m['cantidad'] = cantidad
    m['duracion'] = duracion
    if horario is not None:
        m['horario'] = horario
    if rescate:
        m['rescate'] = True
    return m


def al(t, si=None):
    """Un signo de alarma, con su condición si la tiene."""
    a = {'t': t}
    if si is not None:
        a['si'] = si
    return a


PLANTILLAS = [
%s
]

HOJAS = %s

HORAS = %s


for _p in PLANTILLAS:
    _p['version'] = hashlib.sha256(json.dumps(
        _p, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

_cat = {
    'plantillas': PLANTILLAS,
    'hojas': HOJAS,
    'horas': HORAS,
    'version': hashlib.sha256(json.dumps(
        {'plantillas': PLANTILLAS, 'hojas': HOJAS, 'horas': HORAS},
        ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16],
    'generado': datetime.date.today().isoformat(),
}

with open(SALIDA, 'w', encoding='utf-8') as _f:
    json.dump(_cat, _f, ensure_ascii=False, indent=1)

print('%%d plantillas  ·  catalogo %%s' %% (len(PLANTILLAS), _cat['version']))
for _p in PLANTILLAS:
    print('   %%-16s %%s  (%%d renglones)' %% (_p['id'], _p['version'],
                                            len(_p['medicamentos'])))
''' % ('\n'.join(partes),
       plit(cat['hojas']),
       plit(cat['horas']))

open(SALIDA, 'w', encoding='utf-8').write(PLANTILLA)
print('emitido %s  (%d bytes, %d plantillas)' % (SALIDA, len(PLANTILLA),
                                                 len(cat['plantillas'])))
