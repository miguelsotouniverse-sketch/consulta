#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EL PROTECTOR SOLAR DE MORPHEUS8 Y NANOFAT NO ESPERA A QUE «CIERRE» NADA
=======================================================================

Qué estaba mal
--------------
El renglón del protector solar se escribió primero para las tres hojas de
láser ablativo —eCO₂, Deep Plane + CO₂ y la combinada facial—, donde la piel
queda en carne viva y de verdad hay que esperar a que cierre:

    «Aplicar en rostro y cuello todos los días EN CUANTO la piel esté
     completamente cerrada… Antes de que cierre, el sol se evita con sombra
     y gorra, no con protector.»

De ahí se copió, palabra por palabra, a las recetas de **Morpheus8** y de
**nanofat**, donde la piel NUNCA queda abierta. En esos dos la receta le pide
a la paciente esperar a que cierre algo que nunca se abrió — y su propia hoja,
en la misma bolsa, le dice que empiece desde mañana. Dos papeles que se
entregan juntos diciendo cosas distintas: el que pierde es el protector.

Y pierde justo donde más cuesta. Después de Morpheus8 o de nanofat la paciente
sale a la calle al día siguiente con la piel inflamada, que es la condición en
la que se mancha. La hiperpigmentación postinflamatoria es el riesgo principal
de esos dos tratamientos en fototipos III y IV, que son los de sus pacientes.

La segunda discordancia
-----------------------
La hoja decía «durante las 4 semanas siguientes» y la receta «12 meses». Las
dos cifras son correctas y miden cosas distintas: 4 semanas es el periodo
estricto —el de la pigmentación— y 12 meses es el frasco resurtible. Aquí se
escriben las dos en la misma frase, en los dos papeles, en vez de que cada
papel enseñe una.

Qué NO toca
-----------
Las tres hojas y las tres recetas de láser ablativo se quedan intactas: ahí
«en cuanto la piel esté completamente cerrada» es la indicación correcta, y
cambiarla sería poner protector solar sobre una herida abierta.

Uso:  python3 unificar_protector_solar.py [indicaciones.json] [recetas.json]
"""

import json
import hashlib
import datetime
import sys

RUTA_IND = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'
RUTA_RX  = sys.argv[2] if len(sys.argv) > 2 else 'recetas.json'

CERRADA = 'completamente cerrada'

VIEJO_HOJA = ('Protector solar FPS 50+ de amplio espectro, todos los días '
              'desde mañana y reaplicado cada 3 horas si está al aire libre, '
              'durante las 4 semanas siguientes. Hoy, mejor sombra y gorra.')

NUEVO_HOJA = ('Protector solar FPS 50+ de amplio espectro: todos los días '
              'desde mañana, reaplicado cada 3 horas si está al aire libre. '
              'Las primeras 4 semanas sin falta —es cuando la piel inflamada '
              'se mancha— y de ahí en adelante, todos los días como hábito. '
              'Su frasco es resurtible por 12 meses. Hoy, mejor sombra y gorra.')

NUEVA_INDICACION = ('Aplicar en rostro y cuello todos los días a partir del '
                    'día siguiente al tratamiento, reaplicando cada 3 horas si '
                    'está al aire libre. Las primeras 4 semanas sin falta; '
                    'después, todos los días. El mismo día del tratamiento, '
                    'sombra y gorra en vez de protector.')

HOJAS   = ('morpheus8', 'nanofat')
ABIERTA = ('eco2', 'deep_plane_co2', 'facial_combinada')

# ---------------------------------------------------------------------------
# 1. las hojas
# ---------------------------------------------------------------------------
cat = json.load(open(RUTA_IND, encoding='utf-8'))
H = {h['id']: h for h in cat['hojas']}

for hid in HOJAS:
    hoja = H[hid]
    tocado = False
    for b in hoja['bloques']:
        if b['t'] != 'ul':
            continue
        for k, y in enumerate(b['x']):
            if y == VIEJO_HOJA:
                b['x'][k] = NUEVO_HOJA
                tocado = True
    if not tocado:
        raise SystemExit('no encontré el renglón del protector en la hoja de '
                         '%s; ¿ya se cambió?' % hid)

    plano = json.dumps(hoja, ensure_ascii=False)
    if CERRADA in plano:
        raise SystemExit('la hoja de %s habla de piel «completamente cerrada», '
                         'y en este tratamiento la piel no se abre' % hid)
    if 'desde mañana' not in plano:
        raise SystemExit('la hoja de %s se quedó sin el arranque de mañana' % hid)

    hoja['version'] = hashlib.sha256(json.dumps(
        {k: v for k, v in hoja.items() if k != 'version'},
        ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]
    print('hoja       %-18s -> %s' % (hid, hoja['version']))

# Red de seguridad al revés: donde la piel SÍ se abre, la frase debe seguir.
for hid in ABIERTA:
    if CERRADA not in json.dumps(H[hid], ensure_ascii=False):
        raise SystemExit('la hoja de %s perdió la espera al cierre de la piel, '
                         'y ahí la piel sí queda abierta' % hid)

cat['version'] = hashlib.sha256(json.dumps(
    {'hojas': cat['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()
with open(RUTA_IND, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)
print('catálogo de indicaciones  %s' % cat['version'])

# ---------------------------------------------------------------------------
# 2. las recetas
# ---------------------------------------------------------------------------
rx = json.load(open(RUTA_RX, encoding='utf-8'))
P = {p['id']: p for p in rx['plantillas']}

for pid in HOJAS:
    plant = P[pid]
    solares = [m for m in plant['medicamentos']
               if m['nombre'].lower().startswith('protector solar')]
    if len(solares) != 1:
        raise SystemExit('esperaba un solo protector solar en la receta de %s, '
                         'encontré %d' % (pid, len(solares)))
    solares[0]['indicacion'] = NUEVA_INDICACION
    solares[0]['cantidad'] = '1 envase, resurtible'
    solares[0]['duracion'] = '12 meses'

    plano = json.dumps(plant, ensure_ascii=False)
    if CERRADA in plano:
        raise SystemExit('la receta de %s sigue esperando un cierre que no '
                         'existe en este tratamiento' % pid)
    if 'día siguiente al tratamiento' not in plano:
        raise SystemExit('la receta de %s se quedó sin el arranque' % pid)

    plant['version'] = hashlib.sha256(json.dumps(
        {k: v for k, v in plant.items() if k != 'version'},
        ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]
    print('receta     %-18s -> %s' % (pid, plant['version']))

# Y donde la piel sí se abre, la receta tampoco puede haber cambiado.
for pid in ABIERTA:
    if CERRADA not in json.dumps(P[pid], ensure_ascii=False):
        raise SystemExit('la receta de %s perdió la espera al cierre de la '
                         'piel' % pid)

# Que el protector no se haya caído de ninguna de las cinco.
for pid in HOJAS + ABIERTA:
    if not any(m['nombre'].lower().startswith('protector solar')
               for m in P[pid]['medicamentos']):
        raise SystemExit('la receta de %s se quedó SIN protector solar' % pid)

rx['version'] = hashlib.sha256(json.dumps(
    {'plantillas': rx['plantillas'], 'hojas': rx['hojas'],
     'horas': rx.get('horas')},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]
rx['generado'] = datetime.date.today().isoformat()
with open(RUTA_RX, 'w', encoding='utf-8') as f:
    json.dump(rx, f, ensure_ascii=False, indent=1)
print('catálogo de recetas       %s' % rx['version'])
