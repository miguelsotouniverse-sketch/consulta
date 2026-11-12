#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SOLICITUD DE ESTUDIOS DE GABINETE
==================================

Qué pidió
---------
El 12-nov-2026: «necesitamos agregar en el expediente la opción de solicitar
estudios de gabinete. Tengo una paciente por ejemplo que necesita que le
pidamos una TAC y no existe ese apartado».

Dónde encajaba el hueco
-----------------------
La solicitud de laboratorios ya existía, pero es otra cosa: es una hoja fija,
igual para todas, con los siete estudios preoperatorios de siempre. Termina
diciendo, literalmente, **«Si su médico le solicita algún estudio adicional, se
lo indicará por separado.»** Ese «por separado» no existía. Esto lo es.

Por qué es un documento del expediente y no una hoja más
---------------------------------------------------------
Las hojas de `indicaciones.json` son texto fijo que se escoge y se imprime
igual para toda paciente. Una solicitud de gabinete es lo contrario: cambia en
cada caso —qué estudio, de qué región, con o sin contraste, qué se está
buscando—. Eso son campos que se capturan, así que vive en el esquema y en la
lista de documentos, junto a la orden de internamiento y la constancia de
acompañante, que son los otros dos documentos dirigidos a un tercero.

Lo que el médico definió el mismo día
--------------------------------------
· **Los cuatro estudios** de la lista: TAC, ultrasonido, radiografía y
  resonancia. Lo que no esté se escribe en el renglón de «otro estudio».
· **Sí lleva indicación clínica, con campo propio.** Se le preguntó
  expresamente porque es información clínica de su paciente que sale hacia un
  tercero —el mismo cuidado que separó la constancia de acompañante de la
  orden de internamiento—. Decidió que sí: el radiólogo necesita saber qué se
  busca para poder leer el estudio.
· **Genérica**, como la de laboratorios: sirve en cualquier centro de imagen,
  porque muchas de sus pacientes son foráneas.

POR QUÉ LAS CASILLAS AQUÍ SÍ Y EN LABORATORIOS NO
--------------------------------------------------
Cuando se hizo la hoja de laboratorios, el médico pidió que fuera «sin
casillas para marcar, porque se envía por medio digital»: una casilla vacía en
un PDF que va por WhatsApp no se puede marcar y no sirve de nada.

Esa regla sigue viva y aquí se respeta. Las casillas de este documento se
marcan EN LA APLICACIÓN, antes de imprimir, y lo que sale en el papel son los
estudios escogidos escritos como texto. En el PDF no hay ni una casilla.

Uso:  python3 agregar_estudios_gabinete.py [campos.json]
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'campos.json'

GRUPO = 'Estudios de gabinete'
ETIQUETA = 'Solicitud de estudios de gabinete'

CAMPOS = [
    {
        'id': 'gab_estudios',
        'etiqueta': 'Estudios solicitados',
        'grupo': GRUPO,
        'control': 'casillas',
        'opciones': ['Tomografía (TAC)', 'Ultrasonido', 'Radiografía simple',
                     'Resonancia magnética'],
        'pista': '',
        'sistema': 'App expediente',
        'captura': 'Casilla',
        'obligatorio': False,
        'aparece': ETIQUETA,
        'notas': ('Se marcan aquí, no en el papel: la solicitud se manda por '
                  'medio digital y una casilla impresa en blanco no se puede '
                  'marcar. Lo que no esté en la lista va en «otro estudio».'),
        'valoracion': False,
    },
    {
        'id': 'gab_region',
        'etiqueta': 'Región o zona a estudiar',
        'grupo': GRUPO,
        'control': 'texto',
        'opciones': [],
        'pista': 'senos paranasales, tórax, mama izquierda, abdomen…',
        'sistema': 'App expediente',
        'captura': 'Teclado',
        'obligatorio': False,
        'aparece': ETIQUETA,
        'notas': ('Sin región, el centro de imagen no sabe qué tomar. Es el '
                  'dato que más seguido falta en una solicitud.'),
        'valoracion': False,
    },
    {
        'id': 'gab_contraste',
        'etiqueta': 'Contraste',
        'grupo': GRUPO,
        'control': 'lista',
        'opciones': ['No aplica', 'Sin contraste', 'Con contraste',
                     'Con y sin contraste'],
        'pista': '',
        'sistema': 'App expediente',
        'captura': 'Lista',
        'obligatorio': False,
        'aparece': ETIQUETA,
        'notas': ('Para TAC y resonancia. El centro de imagen necesita saberlo '
                  'de antemano: cambia la preparación de la paciente y el '
                  'tiempo de estudio.'),
        'valoracion': False,
    },
    {
        'id': 'gab_otros',
        'etiqueta': 'Otro estudio no listado',
        'grupo': GRUPO,
        'control': 'texto',
        'opciones': [],
        'pista': 'densitometría, mastografía, espirometría…',
        'sistema': 'App expediente',
        'captura': 'Teclado',
        'obligatorio': False,
        'aparece': ETIQUETA,
        'notas': '',
        'valoracion': False,
    },
    {
        'id': 'gab_indicacion',
        'etiqueta': 'Indicación clínica: qué se busca o qué se descarta',
        'grupo': GRUPO,
        'control': 'parrafo',
        'opciones': [],
        'pista': 'descartar colección en flanco derecho…',
        'sistema': 'App expediente',
        'captura': 'Dictado',
        'obligatorio': False,
        'aparece': ETIQUETA,
        'notas': ('El radiólogo lee el estudio buscando algo. Sin esto, lo '
                  'reporta a ciegas. El médico lo decidió el 12-nov-2026 '
                  'sabiendo que es dato clínico que sale hacia un tercero.'),
        'valoracion': False,
    },
]

e = json.load(open(RUTA, encoding='utf-8'))

if GRUPO in e['grupos']:
    raise SystemExit('el grupo «' + GRUPO + '» ya existe')
ya = [c['id'] for c in e['campos'] if c['id'].startswith('gab_')]
if ya:
    raise SystemExit('ya hay campos de gabinete: ' + ', '.join(ya))

antes_campos = len(e['campos'])
antes_grupos = len(e['grupos'])

# El grupo va junto a «Procedimiento», que es su vecino lógico en el orden de
# lectura del expediente: lo que se le hizo y lo que se le pidió.
i = e['grupos'].index('Procedimiento') + 1
e['grupos'].insert(i, GRUPO)
e['campos'].extend(CAMPOS)

# ---------------------------------------------------------------------------
# Redes de seguridad
# ---------------------------------------------------------------------------
if len(e['campos']) != antes_campos + len(CAMPOS):
    raise SystemExit('no se agregaron todos los campos')
if len(e['grupos']) != antes_grupos + 1:
    raise SystemExit('no se agregó el grupo')

# Cada campo tiene que traer las mismas llaves que los demás, o la aplicación
# lo dibuja a medias sin decir nada.
llaves = set(e['campos'][0].keys())
for c in CAMPOS:
    faltan = llaves - set(c.keys())
    sobran = set(c.keys()) - llaves
    if faltan or sobran:
        raise SystemExit('el campo ' + c['id'] + ' no tiene la forma de los '
                         'demás: faltan ' + str(sorted(faltan)) +
                         ', sobran ' + str(sorted(sobran)))

# `esquemaSano_()` en la aplicación se niega a subir un esquema que haya
# encogido. Que no encoja nunca por culpa de este script.
if len(e['campos']) < antes_campos:
    raise SystemExit('el esquema encogió')

# Ninguno es obligatorio: si lo fueran, el candado de la NOM-004 reclamaría
# «faltan datos obligatorios» en un documento que no es una nota clínica. El
# candado propio de este documento va en index.html, con su propio mensaje.
for c in CAMPOS:
    if c['obligatorio']:
        raise SystemExit('ningún campo de gabinete debe ser obligatorio: el '
                         'aviso de la NOM no aplica a una solicitud')

# La versión es el hash del esquema SIN `version` ni `generado` —así lo
# calculaba el que ya estaba, y así lo compara la app contra el del gateway
# para decidir si sube el nuevo.
e['generado'] = datetime.date.today().isoformat()
sin = {k: v for k, v in e.items() if k not in ('version', 'generado')}
e['version'] = hashlib.sha256(
    json.dumps(sin, ensure_ascii=False, sort_keys=True).encode('utf-8')
).hexdigest()[:16]

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(e, f, ensure_ascii=False, indent=1)

print('grupo nuevo   %s' % GRUPO)
print('campos        %d -> %d' % (antes_campos, len(e['campos'])))
for c in CAMPOS:
    print('   + %-16s %-10s %s' % (c['id'], c['control'], c['etiqueta'][:45]))
print('esquema       %s' % e['version'])
