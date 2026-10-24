#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONSTRUYE LA RECETA DE OTOPLASTIA
==================================

De dónde sale
-------------
El médico lo tiene dicho: «la receta del Deep Plane facelift es la base; las
demás cirugías son esa misma receta con diferencias puntuales». Así que esta
es la del lifting, copiada renglón por renglón, con tres cambios y ninguno
inventado:

  SE CAE   la clorhexidina — es el enjuague de la incisión intraoral de las
           bolas de Bichat, que aquí no existe
  SE CAE   la hipromelosa — es el lubricante de la blefaroplastia
  ENTRA    el ungüento con antibiótico sobre las heridas, copiado tal cual de
           la receta de rinoplastia, porque la hoja de indicaciones manda
           «aplique una capa delgada del ungüento indicado en su receta» y sin
           este renglón esa frase apunta a un medicamento que no está  ←CONFIRMAR

Se queda todo lo demás: antibiótico oral, paracetamol, celecoxib o ketorolaco
según la alergia a sulfas, prednisona, pantoprazol, tramadol de rescate,
ondansetrón y los dos laxantes. El amlodipino de la víspera se lo pone al
final `agregar_amlodipino_recetas.py`, porque la otoplastia lleva incisión.

Las preguntas
-------------
Las del lifting menos dos: «Bichat intraoral» y «blefaroplastia en el mismo
tiempo quirúrgico» no tienen sentido aquí. Quitarlas obliga a limpiar lo que
colgaba de ellas —dos renglones, dos avisos, dos signos de alarma y las dos
variantes de profilaxis con metronidazol—, porque una condición que apunta a
una pregunta que ya no existe nunca se cumple y el renglón se queda mudo.

Los signos de alarma de la oreja
--------------------------------
La caja de la receta no es el catálogo completo: es la de «cuelgue y llame».
Se copian los del lifting que aplican y se agregan dos escritos aquí  ←NUEVO,
el hematoma de una oreja y el color de la piel del pabellón. Son los mismos
dos que encabezan los signos de alarma de la hoja.

Uso:  python3 construir_receta_otoplastia.py [recetas.json]
      (después de agregar_prednisona.py y antes de agregar_amlodipino_recetas.py)
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'recetas.json'

cat = json.load(open(RUTA, encoding='utf-8'))
P = {p['id']: p for p in cat['plantillas']}
for req in ('deep_plane', 'rinoplastia'):
    if req not in P:
        raise SystemExit('falta la plantilla «' + req + '»')
DP, RI = P['deep_plane'], P['rinoplastia']


def copia(o):
    return json.loads(json.dumps(o, ensure_ascii=False))


def uno(plantilla, prefijo):
    """El renglón aprobado que empieza así. Uno y sólo uno: si hay cero o dos,
       es que la plantilla cambió y hay que mirar, no adivinar."""
    hits = [m for m in plantilla['medicamentos'] if m['nombre'].startswith(prefijo)]
    if len(hits) != 1:
        raise SystemExit('busqué «' + prefijo + '» en ' + plantilla['id'] +
                         ' y encontré ' + str(len(hits)) + ' renglones')
    return copia(hits[0])


if any('Amlodipino' in m['nombre'] for m in DP['medicamentos']):
    raise SystemExit(
        'La plantilla de Deep Plane ya trae amlodipino: este constructor va '
        'ANTES de agregar_amlodipino_recetas.py. Revise el orden de la cadena.')
if not any('Prednisona' in m['nombre'] for m in DP['medicamentos']):
    raise SystemExit(
        'La plantilla de Deep Plane no trae prednisona: este constructor va '
        'DESPUÉS de agregar_prednisona.py.')

# --------------------------------------------------------- medicamentos
# Todo lo del lifting menos lo que colgaba de Bichat y de blefaroplastia.
FUERA = ('Clorhexidina', 'Hipromelosa')
UNGUENTO = uno(RI, 'Bacitracina') if any(
    m['nombre'].startswith('Bacitracina') for m in RI['medicamentos']) else None
if UNGUENTO is None:
    # El nombre comercial puede estar escrito de otra forma; se busca por lo
    # que la hoja promete, no por una marca.
    hits = [m for m in RI['medicamentos']
            if 'ungüento' in m['nombre'].lower() or 'crema' in m['nombre'].lower()]
    hits = [m for m in hits if 'Clobetasol' not in m['nombre']]
    if len(hits) != 1:
        raise SystemExit('no encontré el ungüento de heridas en la receta de '
                         'rinoplastia; revise cómo se llama ahora')
    UNGUENTO = copia(hits[0])

# El renglón viene de la rinoplastia y termina con «No lo introduzca en las
# fosas nasales». Aquí no hay nariz operada: esa frase sobra y, peor, delata
# que la receta se copió de otra cirugía.
_NASAL = ' No lo introduzca en las fosas nasales.'
if _NASAL in UNGUENTO['indicacion']:
    UNGUENTO['indicacion'] = UNGUENTO['indicacion'].replace(_NASAL, '')
elif 'nasal' in UNGUENTO['indicacion'].lower():
    raise SystemExit('el renglón del ungüento sigue hablando de la nariz y no '
                     'reconozco la frase; revísela a mano')

MEDS = []
puesto = False
for m in DP['medicamentos']:
    if any(m['nombre'].startswith(f) for f in FUERA):
        continue
    if m['hoja'] != 'antibiotico' and not puesto:
        MEDS.append(UNGUENTO)          # ←CONFIRMAR — el ungüento, copiado de rinoplastia
        puesto = True
    MEDS.append(copia(m))
if not puesto:
    MEDS.append(UNGUENTO)

# ----------------------------------------------------------- preguntas
PREGUNTAS = [q for q in copia(DP['preguntas']) if q['id'] not in ('bichat', 'blefaro')]
IDS = {q['id'] for q in PREGUNTAS} | {'c24', 'menor'}   # c24 y menor los calcula el sistema


def aplica(cond):
    """Una condición sólo sirve si todas sus llaves son preguntas que existen."""
    return all(k in IDS for k in (cond or {}).keys())


MEDS = [m for m in MEDS if aplica(m.get('si'))]

# ----------------------------------------------------------- profilaxis
# Se caen las dos variantes con metronidazol y ampicilina/sulbactam: eran para
# la incisión intraoral del Bichat. Quedan la cefazolina y, en alergia grave,
# la clindamicina.
PROFILAXIS = [p for p in copia(DP['profilaxis']) if aplica(p.get('si'))]
PROFILAXIS_NOTA = ('Repetir si la cirugía pasa de 4 h (cefazolina) o de 6 h '
                   '(clindamicina).')

# -------------------------------------------------------------- avisos
AVISOS = [a for a in copia(DP['avisos']) if aplica(a.get('si'))]

# -------------------------------------------------------------- alarma
# Tres de los del lifting no son de esta cirugía y se caen: hablan del cuello
# y de la cara, que aquí no se tocan. Dejarlos manda a la paciente a buscarse
# un síntoma que no le puede pasar, y le resta peso al que sí importa.
NO_APLICAN = {
    'Dificultad para respirar o tragar.',
    'Piel de la cara que se pone oscura o morada.',
    'Aumento rápido de volumen, dolor intenso o moretón que crece en un solo '
    'lado de la cara o del cuello.',
}
ALARMA = [
    # ←NUEVO — los dos de la oreja, los mismos que encabezan la hoja
    {'t': 'Dolor intenso en UNA sola oreja que aumenta con las horas, sobre '
          'todo si esa oreja se ve más hinchada, tensa o brillante que la otra.'},
    {'t': 'Piel de la oreja de color morado oscuro, negro o muy pálido.'},
] + [a for a in copia(DP['alarma'])
     if aplica(a.get('si')) and a['t'] not in NO_APLICAN]

sobrantes = NO_APLICAN - {a['t'] for a in DP['alarma']}
if sobrantes:
    raise SystemExit('estos signos de alarma ya no existen tal cual en la '
                     'receta del lifting, así que no se están quitando: ' +
                     ' | '.join(sorted(sobrantes)))

plantilla = {
    'id': 'otoplastia',
    'nombre': 'Otoplastia',
    'coincide': ['otoplastia', 'otoplastía', 'cirugia de orejas',
                 'cirugía de orejas', 'orejas prominentes', 'orejas de soplillo'],
    'procedimiento': 'Otoplastia',
    'preguntas': PREGUNTAS,
    'medicamentos': MEDS,
    'profilaxis': PROFILAXIS,
    'profilaxisNota': PROFILAXIS_NOTA,
    'avisos': AVISOS,
    'alarma': ALARMA,
    'horaNota': DP['horaNota'],
}

plantilla['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in plantilla.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

cat['plantillas'] = [p for p in cat['plantillas'] if p['id'] != plantilla['id']]
pos = max(i for i, p in enumerate(cat['plantillas']) if p['id'] == 'eco2') + 1
cat['plantillas'].insert(pos, plantilla)

cat['version'] = hashlib.sha256(json.dumps(
    {'plantillas': cat['plantillas'], 'hojas': cat['hojas'], 'horas': cat['horas']},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

print('receta otoplastia  ·  versión ' + plantilla['version'] +
      '  ·  ' + str(len(MEDS)) + ' renglones, ' + str(len(PREGUNTAS)) + ' preguntas')
print('   ungüento tomado de rinoplastia: ' + UNGUENTO['nombre'])
print('catálogo  ·  versión ' + cat['version'] + '  ·  ' +
      str(len(cat['plantillas'])) + ' plantillas')
