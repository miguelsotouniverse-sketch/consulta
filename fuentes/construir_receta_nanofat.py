#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA RECETA DE MICRO Y NANOFAT FACIAL
====================================

El médico la definió el 12-nov-2026, textualmente:

    «Antibiotico, analgesico, cicalfate y protector solar porque el nanofat
     lleva micropunciones»

De dónde sale cada renglón
--------------------------
Nada se escribe a mano: el antibiótico y los analgésicos se copian de la
plantilla de **otoplastia** —con sus dos ramas de alergia, a penicilina y a
sulfas— y el protector solar de la de **Morpheus8**. El Cicalfate es el único
renglón nuevo, y va redactado a partir del de Cicaplast de Morpheus8.

Lo que NO lleva, y por qué
--------------------------
· **Antihipertensivos.** El médico los pide en cirugía abierta, para sostener
  la presión baja y que no se acumule sangre bajo la piel despegada. Aquí no
  hay piel despegada.
· **Dexametasona.** Sus otras dos recetas de consultorio —eCO₂ y Morpheus8—
  la traen en la lista pero APAGADA por omisión. Aquí no la puse ni apagada,
  porque él enumeró cuatro cosas y ésa no estaba.          ←CONFIRMAR
  Si la quiere disponible para la paciente que amanezca muy inflamada, es un
  renglón copiado de Morpheus8.
· **Vaselina.** Va con el Cicaplast en las hojas de láser, para oclusión
  permanente. Aquí él pidió Cicalfate solo.

EL REPARADOR ES CICAPLAST BAUME
-------------------------------
Él escribió «Cicalfate» (Avène) al definir la receta y lo marqué, porque sus
otras dos hojas de consultorio usan Cicaplast (La Roche-Posay). El 12-nov-2026
lo resolvió: «cicaplast baume esta bien». Era un lapsus.

LOS ANALGÉSICOS VAN A 7 DÍAS
----------------------------
Venían copiados de otoplastia, a 14 días, y él los acortó el mismo día:
«analgesicos 7 dias suficiente». Se recalcularon las cantidades desde la
posología, y el protector gástrico se recortó con ellos —a 7 literales, en vez
del token `{diasPPI}` que habría seguido diciendo 14 y habría contradicho al
antiinflamatorio en la misma hoja—. El ketorolaco se queda en 5 días: ése es
un tope del fármaco, no una comodidad.

Uso:  python3 construir_receta_nanofat.py [recetas.json]
      (después de construir_hoja_nanofat.py)
"""

import json
import hashlib
import datetime
import sys

RUTA_RX = sys.argv[1] if len(sys.argv) > 1 else 'recetas.json'

cat = json.load(open(RUTA_RX, encoding='utf-8'))
P = {p['id']: p for p in cat['plantillas']}

if 'nanofat' in P:
    raise SystemExit('la plantilla de nanofat ya existe')
for req in ('otoplastia', 'morpheus8'):
    if req not in P:
        raise SystemExit('falta la plantilla ' + req + ', de donde se copia')

O = P['otoplastia']
M = P['morpheus8']


def med(plant, fragmento, cuantos=1):
    """Renglones de una plantilla, buscados por el nombre del medicamento."""
    hallados = [dict(m) for m in plant['medicamentos'] if fragmento in m['nombre']]
    if len(hallados) != cuantos:
        raise SystemExit('busqué «' + fragmento + '» en ' + plant['id'] +
                         ' y hallé ' + str(len(hallados)) + '; esperaba ' +
                         str(cuantos))
    return hallados


# ---------------------------------------------------------------------------
# LOS ANALGÉSICOS VAN A 7 DÍAS, NO A 14
# ---------------------------------------------------------------------------
# Se copian de otoplastia, donde duran 14 días porque son de una cirugía
# abierta. El médico lo acortó el 12-nov-2026: «analgesicos 7 dias
# suficiente». Las cantidades se recalculan de la propia posología para que no
# queden diciendo 7 días con tabletas para 14.
#
# El protector gástrico se recorta CON ellos. En las demás plantillas su plazo
# lo calcula el programa (`{diasPPI}`, que siempre da 14 porque dura lo que
# dure el antiinflamatorio). Aquí se escribe 7 literal: si se dejara el token,
# la receta diría antiinflamatorio 7 días y protector 14, que es justo la
# contradicción que el recorte venía a evitar. Ninguna otra plantilla se toca.
def plazo(m, dias, cantidad):
    m = dict(m)
    m['indicacion'] = m['indicacion'].replace('durante 14 días', 'durante ' + str(dias) + ' días')
    m['duracion'] = str(dias) + ' días'
    m['cantidad'] = cantidad
    if '14' in m['duracion'] or '{diasPPI}' in json.dumps(m, ensure_ascii=False):
        raise SystemExit('quedó un plazo de 14 días o un {diasPPI} sin sustituir')
    return m


meds = []
meds += med(O, 'Amoxicilina')          # rama: no alérgica a penicilina
meds += med(O, 'Clindamicina 300 mg')  # rama: alérgica
# 2 tabletas cada 8 h = 6 al día × 7 días
meds += [plazo(med(O, 'Paracetamol')[0], 7, '42 tabletas')]
cele = med(O, 'Celecoxib', 2)
for c in cele:
    if c['si'].get('c24'):
        meds.append(plazo(c, 7, '7 cápsulas'))    # 1 al día × 7
    else:
        meds.append(plazo(c, 7, '14 cápsulas'))   # 2 al día × 7
# El ketorolaco NO se toca: sus 5 días son un tope de seguridad del fármaco,
# no una comodidad, y ya son menos de 7.
meds += med(O, 'Ketorolaco')
pan = dict(med(O, 'Pantoprazol')[0])
pan['indicacion'] = pan['indicacion'].replace('{diasPPI}', '7')
pan['cantidad'] = '7 tabletas'
pan['duracion'] = '7 días'
meds.append(pan)

# El reparador es el MISMO producto que en eCO₂ y Morpheus8. El médico lo
# confirmó el 12-nov-2026: «cicaplast baume esta bien» —había escrito
# Cicalfate, de otra marca, y era un lapsus—. Se copia el nombre de allá, pero
# NO su indicación: la de Morpheus8 dice «piel tratada con láser» y aquí no
# hubo láser; además hay que decir que no se masajee, que es lo propio del
# injerto.
cic = dict(med(M, 'Cicaplast')[0])
cic['indicacion'] = ('Aplique una capa delgada sobre la zona tratada de la cara '
                     'cada 12 horas, y después de cada lavado, sin masajear: '
                     'sólo apoyar y extender. La grasa recién injertada no '
                     'admite presión. Manos limpias cada vez.')
cic['duracion'] = 'Mientras lo indique el Dr. Soto'
meds.append(cic)
meds += med(M, 'Protector solar')

plant = {
    'id': 'nanofat',
    'nombre': 'Micro y nanofat facial',
    'coincide': ['nanofat', 'microfat', 'micro/nanofat', 'nanograsa',
                 'lipoinjerto facial', 'injerto de grasa facial'],
    'procedimiento': 'Micro y nanofat — injerto de grasa propia, con micropunciones',
    # Se copian las preguntas de otoplastia porque de ellas cuelgan las ramas
    # de alergia que acabamos de traer. Sin ellas, los renglones condicionados
    # no sabrían cuál encender. La del tubo se excluye: esto va con sedación.
    'preguntas': [dict(q) for q in O.get('preguntas', []) if q['id'] != 'tubo'],
    'medicamentos': meds,
    'profilaxis': [dict(x) for x in O.get('profilaxis', [])],
    'avisos': [dict(a) for a in O.get('avisos', [])
               if 'tubo' not in json.dumps(a.get('si', {}))],
    'alarma': [dict(a) for a in M.get('alarma', [])],
    'horaNota': O.get('horaNota', ''),
}
if O.get('profilaxisNota'):
    plant['profilaxisNota'] = O['profilaxisNota']

# ←NUEVO: que en la pantalla del médico quede dicho qué NO trae y por qué.
plant['avisos'].insert(0, {
    'si': {}, 'tono': '',
    'texto': ('Micro/nanofat no lleva antihipertensivos ni dexametasona: no hay '
              'piel despegada y no es cirugía abierta. Los analgésicos vienen '
              'copiados de otoplastia, a 14 días; si para este caso son muchos, '
              'acórtelos aquí. Y recuerde que sobre la zona injertada no va '
              'frío ni presión: eso está en su hoja de indicaciones.')})

i = [k for k, p in enumerate(cat['plantillas']) if p['id'] == 'morpheus8'][0]
cat['plantillas'].insert(i + 1, plant)


# ---------------------------------------------------------------------------
# Redes de seguridad
# ---------------------------------------------------------------------------
def plano(t):
    import unicodedata
    t = unicodedata.normalize('NFD', str(t).lower())
    return ''.join(c for c in t if unicodedata.category(c) != 'Mn').strip()


for proc in ('Nanofat', 'Microfat facial'):
    p = plano(proc)
    halladas = [x['id'] for x in cat['plantillas']
                if any(p.find(plano(c)) >= 0 for c in x.get('coincide', []))]
    if halladas != ['nanofat']:
        raise SystemExit('«' + proc + '» coincide con ' + str(halladas) +
                         ' y esperaba sólo con nanofat')

nombres = ' | '.join(m['nombre'] for m in meds)
for sobra in ('Amlodipino', 'Metoprolol', 'Captopril', 'Rivaroxab',
              'Dexametasona', 'Clonazepam', 'Vaselina',
              'Bencidamina', 'Cicalfate'):
    if sobra in nombres:
        raise SystemExit('quedó «' + sobra + '» en la receta de nanofat')
for falta in ('Amoxicilina', 'Clindamicina', 'Paracetamol', 'Celecoxib',
              'Ketorolaco', 'Pantoprazol', 'Cicaplast', 'Protector solar'):
    if falta not in nombres:
        raise SystemExit('falta «' + falta + '» en la receta de nanofat')
# Las dos ramas de alergia tienen que seguir decidiéndose solas.
ids = [q['id'] for q in plant['preguntas']]
for q in ('peni', 'sulfa'):
    if q not in ids:
        raise SystemExit('falta la pregunta «' + q + '»: sin ella los renglones '
                         'de alergia no saben cuál encenderse')
if 'tubo' in ids:
    raise SystemExit('esta receta no debe preguntar por el tubo')
if not any(m['hoja'] == 'antibiotico' for m in meds):
    raise SystemExit('la receta de nanofat se quedó sin pliego de antibiótico')

plant['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in plant.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

cat['version'] = hashlib.sha256(json.dumps(
    {'plantillas': cat['plantillas'], 'hojas': cat['hojas'],
     'horas': cat.get('horas')},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA_RX, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

print('receta     nanofat            nueva -> %s  (%d medicamentos)'
      % (plant['version'], len(meds)))
print('catálogo   ' + cat['version'])
