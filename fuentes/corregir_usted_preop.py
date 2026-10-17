#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA HOJA PREOPERATORIA, TODA DE USTED
====================================

Por qué
-------
Todo el material para la paciente se escribe de USTED. En la hoja de
recomendaciones preoperatorias se colaron dos títulos de tú:

  · "Lo que debes suspender"            →  "Lo que debe suspender"
  · "Medicamentos que debes informarnos" →  "Medicamentos que debe informarnos"

El cuerpo de la hoja ya estaba de usted; sólo eran los dos encabezados.

Esta hoja es además la que ve la paciente en la App de Pacientes y la que
imprime el Cotizador: las tres salen de aquí, así que se corrige una sola vez.

Uso:  python3 corregir_usted_preop.py [indicaciones.json]
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'

CAMBIOS = [
    ('Lo que debes suspender', 'Lo que debe suspender'),
    ('Medicamentos que debes informarnos', 'Medicamentos que debe informarnos'),
]

cat = json.load(open(RUTA, encoding='utf-8'))
h = [x for x in cat['hojas'] if x['id'] == 'preoperatorias'][0]

hechos = 0
for viejo, nuevo in CAMBIOS:
    encontrados = [b for b in h['bloques'] if b['t'] in ('h', 'h2') and b.get('x') == viejo]
    if not encontrados:
        if any(b.get('x') == nuevo for b in h['bloques']):
            continue                      # ya estaba corregido
        raise SystemExit('no encontré el título «' + viejo + '»')
    for b in encontrados:
        b['x'] = nuevo
        hechos += 1

if not hechos:
    raise SystemExit('ya estaba corregido; no se toca')

antes = h['version']
h['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in h.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]
cat['version'] = hashlib.sha256(json.dumps(
    {'hojas': cat['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

print('preoperatorias  ' + antes + ' -> ' + h['version'] + '  (' + str(hechos) + ' títulos a usted)')
print('catálogo        ' + cat['version'])
