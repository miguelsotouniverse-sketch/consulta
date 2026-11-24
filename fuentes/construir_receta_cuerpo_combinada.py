#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA RECETA DE LA COMBINADA DE CUERPO
====================================
abdominoplastia + lipoescultura + mastopexia con implantes

Por qué existe
--------------
El 24-nov-2026 el médico operó esa combinación y al ir a imprimir la receta
no había ninguna que le sirviera: tenía que escoger Body360 y quedarse sin el
relajante del pectoral, o escoger Mastopexia y quedarse sin el rivaroxabán,
que es justo lo que una paciente con abdominoplastia más lipo más implantes no
puede dejar de llevar.

De dónde sale cada renglón, y por qué no se escribió nada nuevo
---------------------------------------------------------------
Se cotejaron las dos plantillas que ya existen, renglón por renglón. Son
IDÉNTICAS salvo por dos renglones:

    Body360     tiene rivaroxabán   y no tiene ciclobenzaprina
    Mastopexia  tiene ciclobenzaprina y no tiene rivaroxabán

O sea que la receta de esta combinación es exactamente la unión de las dos, y
no hubo que inventar ni una dosis. Todo se COPIA de las plantillas aprobadas:
si él corrige el paracetamol en Deep Plane, se corrige aquí.

  · El rivaroxabán se queda porque es contorno corporal, que es la única
    indicación con la que él lo da. Y aquí pesa más que nunca: abdominoplastia
    más lipoescultura más tiempo quirúrgico largo es el escenario de riesgo
    trombótico más alto de su consultorio.
  · La ciclobenzaprina se queda porque hay implantes, pero NO entra encendida:
    entra condicionada a la pregunta del plano, por lo que él dijo ese mismo
    día — «estos quedaron retromusculares pero pudieron haber quedado
    retroglandulares, entonces tendrías que preguntar».

Los signos de alarma
--------------------
Son los nueve de Body360 más los tres de mama que Body360 no tiene y que esta
paciente sí necesita (seno que crece, piel del pezón, herida de la areola).
Los que se repetían entre las dos listas —fiebre, sangrado, enrojecimiento,
pantorrilla, falta de aire— se dejan UNA vez, en la redacción de Body360.
Una lista de alarma con el mismo signo dicho dos veces se lee peor y se
obedece menos.

Uso:  python3 construir_receta_cuerpo_combinada.py [recetas.json]
      (correr DESPUÉS de preguntar_plano_mastopexia.py, de quien copia la
       pregunta del plano y el renglón ya condicionado)
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'recetas.json'

cat = json.load(open(RUTA, encoding='utf-8'))
P = {p['id']: p for p in cat['plantillas']}

if 'cuerpo_combinada' in P:
    raise SystemExit('ya existe la plantilla combinada de cuerpo')

B = P['body360']
M = P['mastopexia']


def copia(x):
    return json.loads(json.dumps(x, ensure_ascii=False))


def de(plantilla, parcial):
    """Un renglón aprobado, buscado por nombre y copiado tal cual."""
    hits = [m for m in plantilla['medicamentos'] if parcial.lower() in m['nombre'].lower()]
    if not hits:
        raise SystemExit('no encontré «%s» en %s' % (parcial, plantilla['id']))
    return [copia(m) for m in hits]


# --------------------------------------------------------------- la plantilla
# El orden es el de Body360, que es el que el médico ya lee de memoria, con la
# ciclobenzaprina insertada donde la tiene la mastopexia: después del AINE y
# antes del esteroide.
MEDS = []
for m in B['medicamentos']:
    MEDS.append(copia(m))
    if 'Ketorolaco' in m['nombre']:
        MEDS.extend(de(M, 'Ciclobenzaprina'))

if not any('Ciclobenzaprina' in m['nombre'] for m in MEDS):
    raise SystemExit('la ciclobenzaprina no se insertó: ¿cambió el ketorolaco?')

# Las preguntas: las de Body360 más la del plano, que vive en la mastopexia.
PREGS = [copia(q) for q in B['preguntas']]
PREGS.append(copia(next(q for q in M['preguntas'] if q['id'] == 'retro')))

# Los avisos: los de Body360 más el de ISRS + ciclobenzaprina de la mastopexia,
# que aquí aplica igual y allá ya quedó condicionado al plano.
AVISOS = [copia(a) for a in B['avisos']]
AVISOS.insert(1, copia(next(a for a in M['avisos']
                            if a['si'] == {'isrs': True, 'retro': True})))

# Los signos de alarma de mama que Body360 no cubre. Se copian de la
# mastopexia, sin reescribirlos.
SOLO_MAMA = ['Un seno que crece', 'Piel del pezón', 'Una herida que se abre']
ALARMA = [copia(a) for a in B['alarma']]
for frase in SOLO_MAMA:
    hits = [a for a in M['alarma'] if a['t'].startswith(frase)]
    if len(hits) != 1:
        raise SystemExit('esperaba un solo signo que empiece con «%s»' % frase)
    ALARMA.append(copia(hits[0]))

# ←NUEVO  el único signo que ninguna de las dos plantillas podía tener, porque
# ninguna de las dos incluye abdominoplastia. La piel del ombligo es la que
# peor se irriga después de levantar el colgajo abdominal.
ALARMA.append({'t': 'Piel del abdomen, sobre todo alrededor del ombligo, que '
                    'se pone morada oscura, gris o negra.'})

COMB = {
    'id': 'cuerpo_combinada',
    'nombre': 'Combinada de cuerpo — abdominoplastia + lipoescultura + '
              'mastopexia con implantes',
    # Sin `coincide`: igual que las dos combinadas faciales, esta plantilla se
    # escoge a mano. Una combinación no se adivina de una palabra suelta del
    # procedimiento, y proponerla por error sería ofrecer rivaroxabán y
    # relajante a quien no los necesita.
    'coincide': [],
    'procedimiento': 'Abdominoplastia + lipoescultura + mastopexia con implantes',
    'preguntas': PREGS,
    'medicamentos': MEDS,
    'profilaxis': copia(B['profilaxis']),
    'profilaxisNota': B['profilaxisNota'],
    'avisos': AVISOS,
    'alarma': ALARMA,
    'horaNota': B['horaNota'],
}

# ---------------------------------------------------------------------------
# Redes de seguridad
# ---------------------------------------------------------------------------
nombres = ' | '.join(m['nombre'] for m in MEDS)
for obliga in ['Rivaroxabán', 'Ciclobenzaprina', 'Paracetamol', 'Pantoprazol',
               'Dexametasona', 'Amoxicilina', 'Clindamicina']:
    if obliga not in nombres:
        raise SystemExit('falta %s en la receta combinada' % obliga)

# Ningún renglón puede colgar de una pregunta que esta plantilla no hace.
ids = {q['id'] for q in PREGS}
for m in MEDS:
    for clave in (m.get('si') or {}):
        if clave not in ids and clave not in ('c24', 'menor'):
            raise SystemExit('«%s» depende de «%s», que nadie pregunta'
                             % (m['nombre'][:30], clave))

# El relajante NO puede entrar encendido: ésa es toda la corrección del día.
cic = [m for m in MEDS if 'Ciclobenzaprina' in m['nombre']][0]
if (cic.get('si') or {}).get('retro') is not True:
    raise SystemExit('la ciclobenzaprina tiene que colgar de la pregunta del plano')

# Un signo de alarma repetido palabra por palabra sería descuido, no énfasis.
textos = [a['t'] for a in ALARMA]
if len(textos) != len(set(textos)):
    raise SystemExit('hay signos de alarma duplicados')

# Que no se cuele texto facial en una hoja de cuerpo.
prohibido = ['facial', 'párpado', 'parpado', 'nariz', 'rostro', 'cuello',
             'mentón', 'oreja']
for t in textos:
    for p in prohibido:
        if p in t.lower():
            raise SystemExit('signo de alarma con texto facial: «%s»' % t[:60])

COMB['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in COMB.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

# Entra después de la mastopexia, para que las tres de cuerpo queden juntas.
i = next(k for k, p in enumerate(cat['plantillas']) if p['id'] == 'mastopexia')
cat['plantillas'].insert(i + 1, COMB)

cat['version'] = hashlib.sha256(json.dumps(
    {'plantillas': cat['plantillas'], 'hojas': cat['hojas'], 'horas': cat['horas']},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

print('plantilla cuerpo_combinada · versión %s · %d renglones, %d preguntas, '
      '%d signos de alarma' % (COMB['version'], len(MEDS), len(PREGS), len(ALARMA)))
print('catálogo de recetas  %s · %d plantillas'
      % (cat['version'], len(cat['plantillas'])))
