#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EL CORSET DE LA 5D EMPIEZA EL DÍA 3, NO EL DÍA 4
=================================================

Qué estaba mal
--------------
La hoja de lipoescultura despachaba a la paciente de Body360 5D con un solo
renglón dentro de la lista de la faja:

    «Pacientes Body360® 5D (RibXcar®): el corset inicia en el día 4 y se
     ajusta 1 broche por semana hasta la semana 8.»

El 26-nov-2026 el médico corrigió el día, con estas palabras: «cuando hay
combinación de lipo con ribxcar, el corset se inicia en día 3 en lugar de
día 1». El día 1 es el de la RibXcar sola, que sí trae el corset desde que
sale de quirófano; la combinación espera, pero espera tres días, no cuatro.

Qué más hace este script
------------------------
Deja el renglón apuntando a la hoja completa. Desde hoy la paciente de 5D
tiene su propia hoja —`body360_ribxcar`— con la sección entera del corset:
los plazos hasta el mes 6, el orden con la faja, la camiseta de algodón y el
signo de alarma propio. Un renglón suelto dentro de la lista de la faja no
puede sostener eso, y lo peor que hacía era terminar en la semana 8: quien
sólo leyera esta hoja entendía que ahí se acababa el corset.

Se deja el renglón —corregido— en vez de borrarlo, para que si alguien le
entrega la hoja de 4D a una paciente de 5D, por lo menos el dato esté y sepa
que hay otra hoja.

Uso:  python3 corregir_dia_corset_5d.py [indicaciones.json]
      (correr ANTES de construir_hoja_body360_ribxcar.py, que copia esta
       lista ya corregida)
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'

cat = json.load(open(RUTA, encoding='utf-8'))
H = {h['id']: h for h in cat['hojas']}
LIPO = H['lipoescultura']

VIEJO = ('Pacientes Body360® 5D (RibXcar®): el corset inicia en el día 4 y se '
         'ajusta 1 broche por semana hasta la semana 8.')
NUEVO = ('Pacientes Body360® 5D (RibXcar®): el corset inicia en el día 3, se '
         'ajusta 1 broche por semana hasta la semana 8 y de ahí sigue hasta el '
         'mes 6 sin apretarlo más. Va por encima de la faja. Sus indicaciones '
         'completas del corset vienen en su hoja de Body360 5D.')

encontrado = False
for b in LIPO['bloques']:
    if b['t'] != 'ul':
        continue
    for k, y in enumerate(b['x']):
        if y == VIEJO:
            b['x'][k] = NUEVO
            encontrado = True

if not encontrado:
    raise SystemExit('no encontré el renglón del día 4; ¿ya se corrigió?')

plano = json.dumps(LIPO, ensure_ascii=False)

# ---------------------------------------------------------------------------
# Redes de seguridad
# ---------------------------------------------------------------------------
if 'día 4' in plano:
    raise SystemExit('todavía queda un «día 4» en la hoja de lipoescultura')
if 'día 3' not in plano:
    raise SystemExit('no quedó el día 3')
# Que no se haya roto la lista de la faja, que es donde vive el renglón.
if 'Faja etapa 1' not in plano:
    raise SystemExit('se perdió la tabla de la faja')

LIPO['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in LIPO.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

cat['version'] = hashlib.sha256(json.dumps(
    {'hojas': cat['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

print('hoja lipoescultura · versión %s · corset del 5D: día 4 -> día 3'
      % LIPO['version'])
print('catálogo de indicaciones  %s' % cat['version'])
