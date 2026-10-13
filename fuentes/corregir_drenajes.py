#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORRIGE LO QUE LAS HOJAS DECÍAN SOBRE LOS DRENAJES
==================================================

Lo que decían, y por qué estaba mal
-----------------------------------
La hoja de Deep Plane afirmaba en dos lugares que los drenajes se retiran en la
cita de las 24 horas:

    · Primeras 72 horas → "Drenajes: si se le colocaron, se retiran en su cita
      de las 24 horas."
    · Citas → "24 horas — … retiro de vendaje y drenajes (si los hay)"

No es así: los drenajes se retiran según el GASTO y las CARACTERÍSTICAS del
líquido, no por calendario. Decirle a la paciente una fecha fija tiene dos
consecuencias feas: si llega a su cita y no se los quitan, cree que algo salió
mal; y si se los quitan tarde, cree que se le olvidó al médico. Ninguna de las
dos debería nacer de su propia hoja de indicaciones.

Ninguna de las dos frases era suya: las escribí yo. Esta corrección las
sustituye por lo que sí decide el retiro, sin inventar un umbral de mililitros
que el médico no ha dado.

Qué toca
--------
Sólo la hoja `deep_plane`. La hoja `facial_combinada` copia ese renglón por
índice desde Deep Plane, así que se corrige sola al volver a construirla con
`construir_hoja_combinada.py` — que es justo para lo que se copia por índice en
vez de reteclear.

Uso:  python3 corregir_drenajes.py [indicaciones.json]
      python3 construir_hoja_combinada.py [indicaciones.json]    ← después
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'

VIEJO_BULLET = ('Drenajes: si se le colocaron, se retiran en su cita de las '
                '24 horas. No los jale ni los desconecte.')
NUEVO_BULLET = ('Drenajes: si se le colocaron, no se retiran en una fecha fija. '
                'Se quitan cuando la cantidad y el aspecto del líquido lo '
                'permiten, y eso se revisa en cada cita. Mientras los traiga: no '
                'los jale, no los desconecte, no los destape y no los deje '
                'colgando —sujételos a su ropa—. Avísenos si uno se sale solo, '
                'deja de salir líquido o el líquido se vuelve rojo brillante.')

VIEJA_CITA = ('Revisión de la herida para descartar hematoma, retiro de vendaje '
              'y drenajes (si los hay)')
NUEVA_CITA = ('Revisión de la herida para descartar hematoma y retiro del '
              'vendaje. Si trae drenajes, se revisan: se retiran cuando el gasto '
              'y las características del líquido lo permiten, no por calendario')

cat = json.load(open(RUTA, encoding='utf-8'))
dp = [h for h in cat['hojas'] if h['id'] == 'deep_plane'][0]

cambios = 0
for b in dp['bloques']:
    if b['t'] == 'ul':
        for i, x in enumerate(b['x']):
            if x == VIEJO_BULLET:
                b['x'][i] = NUEVO_BULLET
                cambios += 1
    elif b['t'] == 'citas':
        for f in b['x']:
            if f.get('que') == VIEJA_CITA:
                f['que'] = NUEVA_CITA
                cambios += 1

if cambios != 2:
    # Si el texto ya no es el esperado, no se adivina: se detiene y se avisa.
    raise SystemExit('Esperaba 2 cambios y encontré ' + str(cambios) +
                     '. El texto cambió; revísalo a mano antes de seguir.')

antes = dp['version']
dp['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in dp.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]
cat['version'] = hashlib.sha256(json.dumps(
    {'hojas': cat['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

print('deep_plane  ' + antes + ' -> ' + dp['version'] + '  (' + str(cambios) + ' renglones)')
print('catálogo    ' + cat['version'])
