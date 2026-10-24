#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONSTRUYE LA RECETA DE DEEP PLANE FACELIFT + LÁSER CO₂
=======================================================

Por qué
-------
Si a una paciente operada de lifting y tratada con láser el mismo día se le
imprimen las dos recetas que ya existen, se lleva **dos veces** la prednisona
—20 mg al día cada una, 40 mg en total durante catorce días— y dos hojas que
no se sabe si se suman o se sustituyen. Y si se le imprime sólo la del
lifting, se va a su casa sin el antiviral, que es justo el que no puede
faltar: empieza la víspera y evita que brote herpes sobre la piel tratada.

Cómo se arma
------------
Por UNIÓN SIN REPETIR, igual que la combinada facial:

    base Deep Plane     antibiótico (amoxi/clavulánico o clindamicina),
                        clorhexidina si hubo Bichat, hipromelosa si hubo
                        blefaroplastia, paracetamol, celecoxib o ketorolaco,
                        prednisona, pantoprazol, tramadol de rescate,
                        ondansetrón y laxantes
    + láser CO₂         valaciclovir, Clobesol, Cicaplast, vaselina y
                        protector solar

La prednisona del láser NO entra: ya viene en la del lifting, y el filtro de
abajo la descarta por nombre. Es la razón de que este archivo exista.

Nada se vuelve a teclear: los renglones se copian enteros de las dos
plantillas aprobadas. Si mañana se corrige la dosis del paracetamol en Deep
Plane, se corrige aquí sola.

Las preguntas se quedan completas, las ocho del lifting —Bichat,
blefaroplastia, alergias, función renal, ISRS y omitir tramadol—: esta
combinación no decide ninguna por definición, a diferencia de la combinada
facial, donde la blefaroplastia va siempre.

Uso:  python3 construir_receta_deep_co2.py [recetas.json]
      (después de agregar_prednisona.py y antes de agregar_amlodipino_recetas.py,
       que es el que le pone el amlodipino de la víspera a todas las abiertas)
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'recetas.json'

cat = json.load(open(RUTA, encoding='utf-8'))
P = {p['id']: p for p in cat['plantillas']}
for req in ('deep_plane', 'eco2'):
    if req not in P:
        raise SystemExit('falta la plantilla «' + req + '»: corra antes su constructor')
DP, E = P['deep_plane'], P['eco2']


def copia(o):
    return json.loads(json.dumps(o, ensure_ascii=False))


# El amlodipino se agrega al final de la cadena, a todas las plantillas de
# cirugía abierta de una sola pasada. Si ya estuviera aquí, este constructor
# estaría corriendo fuera de lugar y la paciente acabaría con dos.
if any('Amlodipino' in m['nombre'] for m in DP['medicamentos']):
    raise SystemExit(
        'La plantilla de Deep Plane ya trae amlodipino: este constructor va '
        'ANTES de agregar_amlodipino_recetas.py. Revise el orden de la cadena.')

# --------------------------------------------------------- medicamentos
# Del láser entra todo lo que el lifting no trae ya, comparando por nombre.
# Hoy eso descarta exactamente una cosa: la prednisona.
ya = {m['nombre'] for m in DP['medicamentos']}
CO2 = [copia(m) for m in E['medicamentos'] if m['nombre'] not in ya]
repetidos = [m['nombre'] for m in E['medicamentos'] if m['nombre'] in ya]

if not CO2:
    raise SystemExit('no quedó ningún renglón del láser; revise los nombres')
if 'Prednisona 20 mg, tabletas.' not in ya:
    raise SystemExit(
        'La plantilla de Deep Plane no trae prednisona. Este constructor va '
        'DESPUÉS de agregar_prednisona.py, que es quien la pone.')

# El orden importa: la impresión agrupa por hoja (antibiótico, general,
# controlado) y parte la hoja general en pliegos. Lo del láser va junto,
# después del antibiótico, para que la paciente lo lea como un bloque.
MEDS = []
puesto = False
for m in DP['medicamentos']:
    if m['hoja'] != 'antibiotico' and not puesto:
        MEDS += CO2
        puesto = True
    MEDS.append(copia(m))
if not puesto:
    MEDS += CO2

# ----------------------------------------------------------------- avisos
# Los del lifting, más los dos del láser que siguen aplicando. Se cae el del
# láser que dice «esta receta no lleva antibiótico oral»: ésta sí lo lleva, y
# dejarlo haría que el médico borrara un antibiótico que sí va.
AVISOS = (
    copia(DP['avisos'])
    + [copia(a) for a in E['avisos']
       if 'no lleva antibiótico oral' not in a['texto']]
    + [{'si': {}, 'tono': '', 'texto':
        'Plantilla combinada: la prednisona va una sola vez, la del lifting '
        '(20 mg al día, 14 días). No agregue la del láser.'}]
)

# ----------------------------------------------------------------- alarma
# La caja de la receta no es el catálogo completo —la hoja de indicaciones ya
# lleva la lista larga—: es la de «cuelgue y llame». Se copian los nueve del
# lifting y se agrega el del herpes, que es la complicación más frecuente del
# láser y la que la paciente puede confundir con granitos. El texto es el
# aprobado en la hoja `eco2`, no uno nuevo.
ALARMA = copia(DP['alarma']) + [
    {'t': 'Ampollas pequeñas agrupadas, en racimo, con ardor o picor intenso, '
          'sobre todo alrededor de la boca: avísenos el mismo día.'},
]

plantilla = {
    'id': 'deep_plane_co2',
    'nombre': 'Deep Plane Facelift completo + láser CO₂',
    # Vacío a propósito, igual que la hoja: si trajera "deep plane", un
    # lifting solo encontraría dos plantillas y se quedaría sin sugerencia.
    'coincide': [],
    'procedimiento': 'Ritidectomía Deep Plane y láser fraccionado de CO₂ '
                     '(eCO₂) en rostro y cuello',
    'procedimientoBichat': 'Ritidectomía Deep Plane, láser fraccionado de CO₂ '
                           '(eCO₂) en rostro y cuello, y lipectomía de bolas '
                           'de Bichat por vía intraoral',
    'preguntas': copia(DP['preguntas']),
    'medicamentos': MEDS,
    'profilaxis': copia(DP['profilaxis']),
    'profilaxisNota': DP['profilaxisNota'],
    'avisos': AVISOS,
    'alarma': ALARMA,
    'horaNota': DP['horaNota'],
}

plantilla['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in plantilla.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

cat['plantillas'] = [p for p in cat['plantillas'] if p['id'] != plantilla['id']]
pos = max(i for i, p in enumerate(cat['plantillas'])
          if p['id'] == 'facial_combinada') + 1
cat['plantillas'].insert(pos, plantilla)

cat['version'] = hashlib.sha256(json.dumps(
    {'plantillas': cat['plantillas'], 'hojas': cat['hojas'], 'horas': cat['horas']},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

print('receta deep_plane_co2  ·  versión ' + plantilla['version'] +
      '  ·  ' + str(len(MEDS)) + ' renglones (' + str(len(CO2)) + ' del láser)')
if repetidos:
    print('   no se duplicó: ' + ', '.join(repetidos))
print('catálogo  ·  versión ' + cat['version'] + '  ·  ' +
      str(len(cat['plantillas'])) + ' plantillas')
