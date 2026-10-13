#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A QUIÉN LLAMA LA PACIENTE CUANDO ALGO SALE MAL
===============================================

Qué decía
---------
El cierre de la hoja de Deep Plane —y por herencia el de la combinada— mandaba
a la paciente al hospital más cercano si no lograba comunicarse. El médico lo
corrigió: su consultorio está disponible y resuelve lo de sus propias
pacientes, y mandarlas a un servicio que no sabe cómo quedó la cirugía es
peor atención, no más seguridad.

Qué dice ahora, y por qué no es sólo borrar el renglón
------------------------------------------------------
La instrucción nueva es "llámenos siempre". Pero hay un signo de alarma en esa
misma hoja que no admite esperar sentada a que suene el teléfono: la dificultad
para respirar o para tragar después de un lifting de cuello es compromiso de
vía aérea, y ahí los minutos cuentan. Dejar sólo "llámenos" convierte un
renglón de seguridad en una paciente parada junto al teléfono.

Así que se escribe de modo que las dos cosas sean ciertas a la vez: llama
SIEMPRE al consultorio, y si no puede respirar o tragar, llama Y SE PONE EN
CAMINO mientras el consultorio le dice a dónde llegar. Nadie queda esperando y
nadie acaba en un servicio que el consultorio no escogió.

La hoja del láser de CO₂ ya se corrigió aparte, con su propio texto: ahí no hay
urgencia de vía aérea y la instrucción es simplemente insistir hasta localizar
al consultorio.

Uso:  python3 corregir_a_donde_llamar.py [indicaciones.json]
      python3 construir_hoja_combinada.py [indicaciones.json]   ← después
      python3 construir_eco2.py           [indicaciones.json] [recetas.json]
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'

VIEJA = ('Si no logra comunicarse y presenta dificultad para respirar, sangrado '
         'abundante o inflamación rápida del cuello, acuda a urgencias del '
         'hospital más cercano e informe que tiene una cirugía de estiramiento '
         'facial reciente.')
NUEVA = ('Llámenos a cualquier hora, de día o de noche: su cirugía la resolvemos '
         'nosotros, que sabemos exactamente cómo quedó. No acuda a otro servicio '
         'ni se automedique sin avisarnos antes. Si no contestamos a la primera, '
         'insista y escriba también al WhatsApp del consultorio. Y si tiene '
         'dificultad para respirar o para tragar, llame y póngase en camino al '
         'mismo tiempo: le decimos en ese momento a dónde llegar.')

cat = json.load(open(RUTA, encoding='utf-8'))
dp = [h for h in cat['hojas'] if h['id'] == 'deep_plane'][0]

cambios = 0
for b in dp['bloques']:
    if b['t'] == 'nota' and b.get('x') == VIEJA:
        b['x'] = NUEVA
        cambios += 1

if cambios != 1:
    raise SystemExit('Esperaba 1 cambio y encontré ' + str(cambios) +
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

print('deep_plane  ' + antes + ' -> ' + dp['version'])
print('catálogo    ' + cat['version'])
