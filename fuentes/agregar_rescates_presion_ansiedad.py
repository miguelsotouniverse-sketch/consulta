#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOS DOS RESCATES Y LA REGLA PARA SUSPENDER LA PRESIÓN
======================================================

Lo que pidió el médico (28-oct-2026)
------------------------------------
1. Que los antihipertensivos se suspendan en orden: «primero el metoprolol y
   luego el amlodipino, cuando la sistólica baje de 90».
2. Captopril 25 mg sublingual como opcional, «en caso de TA por encima de 130
   a pesar de los otros dos medicamentos».
3. Clonazepam en gotas como opcional, «porque es super frecuente que se les
   venga ataque de ansiedad».

Las dosis las confirmó él: clonazepam 5 gotas (0.5 mg) sublinguales en la
crisis, hasta 2 veces al día; captopril repetible una vez a los 30 minutos,
máximo 2 dosis, y después llamar.

POR QUÉ EL CLONAZEPAM NO PUEDE IR EN EL PLIEGO DEL TRAMADOL
------------------------------------------------------------
Parecen el mismo caso y legalmente no lo son:

  tramadol      artículo 226 fracción III de la Ley General de Salud:
                la receta se surte hasta TRES veces y la farmacia la retiene
                en la TERCERA.
  clonazepam    es benzodiazepina, Grupo III del artículo 245, y le aplica el
                artículo 251: se surte UNA SOLA VEZ y la farmacia la retiene
                en la PRIMERA.

Si los dos fueran en el mismo pliego, la farmacia se quedaría con la hoja al
surtir el clonazepam y la paciente perdería su tramadol —el medicamento que
precisamente existe para el dolor que no cede a media noche—. Por eso este
script crea un pliego aparte, `psicotropico`, con su propia nota legal.

Eso obliga a un cambio en `index.html`: la lista `HOJAS_RX` del selector «Va
en la receta» está escrita a mano ahí. Se agrega el pliego nuevo en los dos
lugares o el renglón no se puede mover de hoja desde la pantalla.

LA REGLA DE SUSPENSIÓN NECESITA QUE ALGUIEN MIDA
-------------------------------------------------
«Suspenda si la sistólica baja de 90» y «tome captopril si pasa de 130» son
instrucciones que sólo sirven si la paciente se está midiendo la presión. Esa
sección existía únicamente en las tres hojas de facelift. Ahora que toda
cirugía abierta sale con dos antihipertensivos y dos reglas colgadas de una
cifra, la toma de presión en casa se copia a las ocho hojas de alta —el mismo
texto aprobado, copiado de la hoja de Deep Plane, no uno nuevo.

Uso:  python3 agregar_rescates_presion_ansiedad.py [recetas.json] [indicaciones.json]
      (después de cambiar_antihipertensivos.py)
"""

import json
import hashlib
import datetime
import sys

RUTA_RX  = sys.argv[1] if len(sys.argv) > 1 else 'recetas.json'
RUTA_IND = sys.argv[2] if len(sys.argv) > 2 else 'indicaciones.json'

SIN_RESCATES = {'eco2'}        # el láser no lleva antihipertensivos ni cirugía

# --------------------------------------------------------------- el pliego
HOJA_PSICO = {
    'id': 'psicotropico',
    'titulo': 'Receta — psicotrópico',
    'nota': 'Clonazepam: benzodiazepina del Grupo III del artículo 245 de la '
            'Ley General de Salud. Conforme al artículo 251, esta receta se '
            'surte UNA SOLA VEZ y la farmacia la retiene al surtirla. Por eso '
            'va en pliego aparte del tramadol, que sí admite tres surtidos.',
    'paraPaciente': 'Esta hoja se queda en la farmacia al surtirla.',
}

CAPTOPRIL = {
    'hoja': 'general',
    'nombre': 'Captopril 25 mg, tabletas.',
    'indicacion':
        'SÓLO si al medirse la presión la cifra de arriba (la sistólica) está '
        'por encima de 130 a pesar del amlodipino y del metoprolol: coloque 1 '
        'tableta DEBAJO DE LA LENGUA y déjela deshacerse, no la trague ni la '
        'mastique. Vuelva a medirse a los 30 minutos. Si sigue por encima de '
        '130, puede tomar una segunda tableta igual. Si después de esa segunda '
        'tableta sigue alta, llámenos: no tome una tercera.',
    'cantidad': '10 tabletas',
    'duracion': 'Sólo en caso necesario, máximo 2 tabletas seguidas',
    'rescate': True,
}

CLONAZEPAM = {
    'hoja': 'psicotropico',
    'nombre': 'Clonazepam 2.5 mg/mL, solución en gotas, frasco de 10 mL.',
    'indicacion':
        'SÓLO si tiene una crisis de ansiedad: 5 gotas (0.5 mg) debajo de la '
        'lengua. Puede repetirlo una vez más en el día si vuelve a pasar, sin '
        'exceder 2 tomas en 24 horas. Da sueño: no maneje ni se levante sola '
        'después de tomarlo, y si ese día tomó tramadol espere al menos 4 '
        'horas entre uno y otro. Sentir ansiedad los primeros días después de '
        'una cirugía es frecuente y pasa; esto es para los momentos malos, no '
        'para tomarlo de horario.',
    'cantidad': '1 frasco de 10 mL',
    'duracion': 'Sólo en caso necesario, máximo 2 tomas al día',
    'rescate': True,
}

# Se agrega a la indicación de los dos antihipertensivos: la regla de retirada
# va escrita en el medicamento mismo, no sólo en la hoja, porque la receta es
# lo que la paciente tiene en la mano cuando se mide la presión.
RETIRADA_METOPROLOL = (
    ' Si la cifra de arriba baja de 90, suspenda ESTE primero y siga con el '
    'amlodipino; avísenos el mismo día.')
RETIRADA_AMLODIPINO = (
    ' Si la cifra de arriba baja de 90, lo primero que se suspende es el '
    'metoprolol, no éste; si en la siguiente toma sigue por debajo de 90, '
    'entonces suspenda también el amlodipino y avísenos.')

cat = json.load(open(RUTA_RX, encoding='utf-8'))

if any(h['id'] == 'psicotropico' for h in cat['hojas']):
    raise SystemExit('el pliego de psicotrópico ya existe; no se duplica')
if any('Captopril' in m['nombre'] or 'Clonazepam' in m['nombre']
       for p in cat['plantillas'] for m in p['medicamentos']):
    raise SystemExit('ya hay captopril o clonazepam en alguna plantilla')

# El pliego nuevo va después del controlado y antes de la receta general, que
# es el orden en que se imprimen.
pos = [i for i, h in enumerate(cat['hojas']) if h['id'] == 'controlado']
if not pos:
    raise SystemExit('no encontré el pliego «controlado»')
cat['hojas'].insert(pos[0] + 1, json.loads(json.dumps(HOJA_PSICO, ensure_ascii=False)))


def version_de(p):
    return hashlib.sha256(json.dumps(
        {k: v for k, v in p.items() if k != 'version'},
        ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]


def copia(o):
    return json.loads(json.dumps(o, ensure_ascii=False))


tocadas = []
for p in cat['plantillas']:
    if p['id'] in SIN_RESCATES:
        print('%-18s sin rescates' % p['id'])
        continue

    amlo = [m for m in p['medicamentos'] if m['nombre'].startswith('Amlodipino')]
    meto = [m for m in p['medicamentos'] if m['nombre'].startswith('Metoprolol')]
    if len(amlo) != 1 or len(meto) != 1:
        raise SystemExit(p['id'] + ' no trae los dos antihipertensivos; corra '
                         'antes cambiar_antihipertensivos.py')
    if 'baja de 90' in amlo[0]['indicacion']:
        raise SystemExit('la regla de retirada ya estaba en ' + p['id'])
    amlo[0]['indicacion'] += RETIRADA_AMLODIPINO
    meto[0]['indicacion'] += RETIRADA_METOPROLOL

    # El captopril va junto a los otros dos de la presión, no al final entre
    # los laxantes: se lee como lo que es, el tercero del mismo asunto.
    i = p['medicamentos'].index(meto[0])
    p['medicamentos'].insert(i + 1, copia(CAPTOPRIL))
    p['medicamentos'].append(copia(CLONAZEPAM))

    p['version'] = version_de(p)
    tocadas.append(p['id'])
    print('%-18s -> %s  (retirada + captopril + clonazepam)' % (p['id'], p['version']))

if len(tocadas) != len(cat['plantillas']) - len(SIN_RESCATES):
    raise SystemExit('no entró en todas las que debía')

cat['version'] = hashlib.sha256(json.dumps(
    {'plantillas': cat['plantillas'], 'hojas': cat['hojas'], 'horas': cat['horas']},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()
with open(RUTA_RX, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)
print('catálogo de recetas  ' + cat['version'] + '  ·  ' +
      str(len(cat['hojas'])) + ' pliegos')

# =========================================================== las hojas
ind = json.load(open(RUTA_IND, encoding='utf-8'))
H = {h['id']: h for h in ind['hojas']}
DP = H['deep_plane']

HOJAS_ALTA = ['deep_plane', 'lipoescultura', 'mastopexia', 'rinoplastia',
              'blefaroplastia', 'facial_combinada', 'deep_plane_co2', 'otoplastia']

VIEJO_MAREO = ('Si tiene mareo al ponerse de pie, levántese despacio y en dos '
               'tiempos. Si se marea estando acostada, se siente muy débil o '
               'nota el corazón muy lento, llámenos antes de saltarse una '
               'toma: la dosis se ajusta, no se suspende por su cuenta.')

NUEVOS = [
    'Mídase la presión como dice el apartado de aquí abajo y anote cada cifra. '
    'Los dos medicamentos se manejan con esos números, no con cómo se siente.',

    'SI LA CIFRA DE ARRIBA BAJA DE 90: suspenda primero el metoprolol y siga '
    'con el amlodipino. Si en la siguiente toma sigue por debajo de 90, '
    'suspenda también el amlodipino. En los dos casos avísenos el mismo día.',

    'SI LA CIFRA DE ARRIBA SE MANTIENE ARRIBA DE 130 a pesar de los dos: '
    'coloque una tableta de captopril 25 mg debajo de la lengua —viene en su '
    'receta, para eso es— y vuelva a medirse a los 30 minutos. Puede repetirla '
    'una sola vez. Si después de la segunda sigue alta, llámenos.',

    'Si tiene mareo al ponerse de pie, levántese despacio y en dos tiempos. Si '
    'se marea estando acostada, se siente muy débil o nota el corazón muy '
    'lento, llámenos.',
]

ANSIEDAD = ('Ansiedad, llanto fácil o la sensación de que algo malo va a pasar '
            'en los primeros días. Es frecuente después de una cirugía y se '
            'pasa. Su receta trae unas gotas para los momentos malos; úselas '
            'sólo si las necesita.')


def rehash(h):
    h['version'] = hashlib.sha256(json.dumps(
        {k: v for k, v in h.items() if k != 'version'},
        ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]


# El bloque de toma de presión, tal como está aprobado en la hoja del lifting.
i_h2 = [i for i, b in enumerate(DP['bloques'])
        if b['t'] == 'h2' and str(b.get('x', '')).startswith('Toma de presión arterial')]
if not i_h2:
    raise SystemExit('no encontré el apartado de toma de presión en deep_plane')
TOMA_H2 = copia(DP['bloques'][i_h2[0]])
TOMA_UL = copia(DP['bloques'][i_h2[0] + 1])
if TOMA_UL['t'] != 'ul':
    raise SystemExit('lo que sigue al título de toma de presión no es una lista')

for hid in HOJAS_ALTA:
    h = H[hid]
    bloques = h['bloques']

    # 1) las tres reglas nuevas, dentro del bloque de la presión
    puesto = False
    for b in bloques:
        if b['t'] == 'ul' and VIEJO_MAREO in b['x']:
            k = b['x'].index(VIEJO_MAREO)
            b['x'][k:k + 1] = list(NUEVOS)
            puesto = True
            break
    if not puesto:
        raise SystemExit('no encontré el bloque de presión en ' + hid)

    # 2) la toma de presión en casa, si esta hoja no la tenía
    tiene = any(b['t'] == 'h2' and str(b.get('x', '')).startswith('Toma de presión arterial')
                for b in bloques)
    if not tiene:
        j = [k for k, b in enumerate(bloques)
             if b['t'] == 'h2' and b.get('x') == 'Sus dos medicamentos para la presión']
        if not j:
            raise SystemExit('no encontré dónde poner la toma de presión en ' + hid)
        ins = j[0] + 2          # después del título y de su lista
        bloques.insert(ins, copia(TOMA_UL))
        bloques.insert(ins, copia(TOMA_H2))

    # 3) la ansiedad, entre lo que es normal
    for k, b in enumerate(bloques):
        if b['t'] == 'h' and 'normal' in str(b.get('x', '')).lower():
            sig = bloques[k + 1] if k + 1 < len(bloques) else None
            if sig and sig['t'] == 'ul' and ANSIEDAD not in sig['x']:
                sig['x'].append(ANSIEDAD)
            break

    rehash(h)
    print('%-18s -> %s  (reglas de presión%s + ansiedad)'
          % (hid, h['version'], '' if tiene else ' + toma en casa'))

ind['version'] = hashlib.sha256(json.dumps(
    {'hojas': ind['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
ind['generado'] = datetime.date.today().isoformat()
with open(RUTA_IND, 'w', encoding='utf-8') as f:
    json.dump(ind, f, ensure_ascii=False, indent=1)
print('catálogo de indicaciones  ' + ind['version'])
