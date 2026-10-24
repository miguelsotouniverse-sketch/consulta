#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONSTRUYE LA HOJA DE INDICACIONES DE OTOPLASTIA
================================================

Por qué existe
--------------
No había ninguna. La otoplastia se operaba y la paciente se iba con las
indicaciones dichas de palabra, o con la hoja de otra cirugía que no habla ni
del vendaje, ni de la banda, ni de la única complicación que de verdad corre
prisa en esta cirugía: el hematoma de una oreja.

Qué está copiado y qué es nuevo
-------------------------------
Esta hoja NO es una fusión como la de Deep Plane + CO₂: la otoplastia no se
parece a ninguna de las que ya estaban, así que buena parte hubo que
escribirla. Para que se revise sabiendo qué es qué:

  COPIADO de `deep_plane`, palabra por palabra —texto ya aprobado—:
    reposo relativo · no agacharse ni cargar · medicamentos prohibidos 14 días
    · tabaco · alcohol · cuidado de las incisiones · baño y lavado de cabello
    · secadora y tinte · prendas que abren por delante · aretes 6 semanas ·
    lentes sin presionar detrás de las orejas · dolor que no cede · sangrado
    que empapa · fiebre · infección de la herida · la nota de urgencias ·
    la constancia de entrega

  CONFIRMADO por el médico (24-oct-2026), preguntado expresamente:
    vendaje 24 a 48 h · banda día y noche la primera semana y sólo para
    dormir tres semanas más · retiro de puntos al día 10 · alberca semana 4 ·
    deporte de contacto y dormir sobre la oreja, semana 6 · hoja de adultos,
    escrita de usted

  ESCRITO AQUÍ y pendiente de su revisión  → marcado  ←NUEVO
    el apartado de la banda, la posición para dormir, lo que no se apoya
    sobre la oreja, los ocho renglones de «lo que es normal» y los cinco
    signos de alarma propios de la oreja.

  PROPUESTO POR MÍ, un número que él no dijo  → marcado  ←CONFIRMAR
    regreso al trabajo, manejar, ejercicio ligero, acompañante la primera
    noche y hasta qué cita se cita.

Lo que deliberadamente NO lleva
-------------------------------
Frío local. Las demás hojas faciales lo indican, pero aquí la oreja va
vendada las primeras 48 horas y después con banda, y el médico no ha indicado
frío en esta cirugía. Antes que inventar un esquema, no se escribe nada y se
pregunta.

Uso:  python3 construir_hoja_otoplastia.py [indicaciones.json]
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'

# --- lo que confirmó el médico el 24-oct-2026 ------------------------------
BANDA_DIA_NOCHE  = 'la primera semana'
BANDA_NOCTURNA   = 'de la segunda a la cuarta semana'
PUNTOS_DIA       = 10
ALBERCA_SEMANA   = 4
CONTACTO_SEMANA  = 6      # deporte de contacto y dormir sobre la oreja

cat = json.load(open(RUTA, encoding='utf-8'))
H = {h['id']: h for h in cat['hojas']}
if 'deep_plane' not in H:
    raise SystemExit('falta la hoja «deep_plane»: corra antes construir_indicaciones.py')
DP = H['deep_plane']


def bl(hoja, i):
    return json.loads(json.dumps(hoja['bloques'][i], ensure_ascii=False))


def li(hoja, i, *js):
    xs = hoja['bloques'][i]['x']
    return [xs[j] for j in js]


def ul(*listas, **kw):
    out = []
    for l in listas:
        out += l
    b = {'t': 'ul', 'x': out}
    if kw.get('alarma'):
        b['alarma'] = True
    return b


# Si alguien reordena los bloques de la hoja de origen, los índices de abajo
# copiarían otra cosa sin que nadie se entere.
ANCLAS = [
    (2,  'ul', 'Reposo relativo.'),
    (14, 'ul', 'Puede bañarse y lavarse el cabello'),
    (16, 'ul', 'Limpie las incisiones'),
    (21, 'ul', 'Use prendas que se abotonen'),
    (31, 'ul', 'Presión sistólica mayor de 130'),
]
for i, t, inicio in ANCLAS:
    b = DP['bloques'][i]
    if b['t'] != t or not str(b['x'][0]).startswith(inicio):
        raise SystemExit(
            'El bloque ' + str(i) + ' de «deep_plane» ya no es el que era '
            '(esperaba «' + inicio + '…»). Revise los índices de este '
            'constructor antes de seguir.')

B = []

# ---------------------------------------------------------------- portada
# Sin tabla de «datos del procedimiento»: esa tabla existe en las hojas
# combinadas, donde hace falta enumerar cuatro cirugías. Aquí el título ya lo
# dice todo y la tabla sólo dejaría un renglón medio vacío.

# ←NUEVO — la caja de lo imprescindible. Todo lo que dice está más abajo.
B.append({'t': 'nota', 'x':
    'SI HOY SÓLO PUEDE LEER UNA COSA, LEA ESTO. '
    '1) No toque el vendaje, no lo afloje y no lo moje: se retira en su cita '
    'de las 24 a 48 horas. '
    '2) Duerma boca arriba, con la cabeza elevada. No se acueste sobre las '
    'orejas. '
    '3) Después del vendaje, la banda: día y noche ' + BANDA_DIA_NOCHE + '. '
    '4) Si una sola oreja le duele cada vez más, o se ve más hinchada o tensa '
    'que la otra, llame de inmediato: no espere a su cita. '
    '5) No se apoye nada sobre las orejas: ni audífonos de diadema, ni '
    'cubrebocas de resorte, ni lentes pesados. '
    'Lo demás de esta hoja lo puede leer con calma mañana.'})

# ------------------------------------------------- 1. primeras 48 horas
B.append({'t': 'h', 'x': '1. Primeras 48 horas'})
B.append({'t': 'p', 'x':
    'Las orejas salen de quirófano con un vendaje que las mantiene en su '
    'posición nueva y evita que se acumule sangre debajo de la piel. Ese '
    'vendaje es el tratamiento de estas primeras horas: no se toca.'})     # ←NUEVO
B.append(ul(
    [   # ←NUEVO — el vendaje y lo que no se hace con él
        'Vendaje: no lo afloje, no lo recorra, no meta nada debajo —ni el '
        'dedo, ni un cotonete, ni papel— y no lo moje. Si se le aflojó o se '
        'le cayó solo, avísenos el mismo día.',
        'Si siente comezón bajo el vendaje, no se rasque ni introduzca nada: '
        'es normal mientras cicatriza.',
    ],
    li(DP, 2, 0, 1),                        # reposo relativo · no agacharse, no cargar, no pujar
    [   # ←NUEVO — posición, con el plazo de dormir de lado que él confirmó
        'Posición: duerma y descanse boca arriba, con la cabeza elevada sobre '
        'dos almohadas. No se acueste sobre las orejas ni duerma de lado '
        'durante ' + str(CONTACTO_SEMANA) + ' semanas.',
        # ←CONFIRMAR — el médico no indicó cuánto acompañamiento pide en esta
        # cirugía. Lo de abajo es lo mínimo razonable, no una indicación suya.
        'Acompañante: salga del procedimiento acompañada por un adulto y no '
        'se quede sola la primera noche.',
    ],
))

# ------------------------------------------------------- 2. medicamentos
B.append({'t': 'h', 'x': '2. Medicamentos'})
B.append(bl(DP, 6))                         # tome exclusivamente los de su receta
B.append(bl(DP, 7))                         # prohibidos 14 días (título)
B.append(bl(DP, 8))                         # la lista de prohibidos
B.append(bl(DP, 9))                         # tabaco y nicotina
B.append(bl(DP, 10))                        # alcohol

# ---------------------------------------------------- 3. cuidados diarios
B.append({'t': 'h', 'x': '3. Cuidados diarios'})

B.append({'t': 'h2', 'x': 'Banda compresiva'})
B.append({'t': 'p', 'x':
    'La banda sostiene las orejas en su posición nueva mientras cicatrizan. '
    'Es la indicación más importante de todo el mes: quitársela antes de '
    'tiempo es la forma más común de que una oreja regrese hacia afuera.'})  # ←NUEVO
B.append({'t': 'ul', 'x': [                                                  # ←NUEVO
    'Se la colocamos nosotros en su cita de las 24 a 48 horas, al retirar el '
    'vendaje.',
    'Úsela día y noche ' + BANDA_DIA_NOCHE + '; sólo se la retira para '
    'bañarse.',
    'Después, ' + BANDA_NOCTURNA + ', úsela únicamente para dormir.',
    'Debe quedar firme pero sin apretar: no debe doler, ni dejarle una marca '
    'profunda, ni ponerle la oreja pálida. Si eso pasa, aflójela y avísenos.',
    'Lávela a mano con agua y jabón neutro y déjela secar al aire. Si tiene '
    'dos, altérnelas.',
]})

B.append({'t': 'h2', 'x': 'Heridas detrás de las orejas'})
B.append(ul(li(DP, 16, 0, 1, 2, 3)))

B.append({'t': 'h2', 'x': 'Baño y cabello'})
B.append({'t': 'p', 'x':
    'El baño empieza cuando el vendaje ya no está, es decir después de su '
    'cita de las 24 a 48 horas.'})                                           # ←NUEVO
B.append(ul(li(DP, 14, 0, 1, 2)))

B.append({'t': 'h2', 'x': 'Ropa y accesorios'})
B.append(ul(
    li(DP, 21, 0, 1, 2),                    # prendas que abren · aretes · lentes sin presionar
    [   # ←NUEVO — lo que específicamente no se apoya sobre una oreja operada
        'No apoye nada sobre las orejas durante ' + str(CONTACTO_SEMANA) +
        ' semanas: ni audífonos de diadema, ni audífonos que se metan al '
        'oído, ni cubrebocas con resorte sobre la oreja —use uno que se '
        'amarre detrás de la cabeza—, ni lentes pesados.',
        'Al peinarse, no jale el cabello hacia atrás con fuerza ni use '
        'diademas o coletas apretadas.',
    ],
))

# ------------------------------------------------------- 4. calendario
B.append({'t': 'h', 'x': '4. Calendario de actividades'})
B.append({'t': 'tabla', 'cols': ['Actividad', 'A partir de', 'Nota'], 'x': [
    ['Caminar dentro de casa', 'Día 1', '5 minutos cada 2 horas'],
    ['Bañarse y lavarse el cabello', 'Día 3',
     'Con el vendaje ya retirado, con agua tibia y champú de bebé'],
    # ←CONFIRMAR — el médico no dio estos tres plazos. Son propuesta mía.
    ['Manejar', 'Día 3', 'Sin analgésicos que den sueño'],
    ['Trabajo de oficina y vida social', 'Día 7', 'Con la banda puesta'],
    ['Ejercicio ligero (caminata, bicicleta fija suave)', 'Semana 2', ''],
    # confirmados por el médico
    ['Alberca y mar', 'Semana ' + str(ALBERCA_SEMANA), ''],
    ['Secadora con aire caliente, plancha o tenazas', 'Semana 4',
     'Antes, sólo aire frío'],
    ['Dormir sobre la oreja o de lado', 'Semana ' + str(CONTACTO_SEMANA), ''],
    ['Deportes de contacto, con pelota, lucha o artes marciales',
     'Semana ' + str(CONTACTO_SEMANA), 'Riesgo de golpe directo en la oreja'],
    ['Usar aretes', 'Semana 6', ''],
    ['Tinte, decoloración, keratina o permanente', 'Semana 6', ''],
    ['Audífonos de diadema, cubrebocas de resorte y lentes pesados',
     'Semana ' + str(CONTACTO_SEMANA), 'Nada que se apoye sobre la oreja'],
]})

# ------------------------------------------------------------- 5. citas
B.append({'t': 'h', 'x': '5. Citas de seguimiento'})
# El renglón del lifting, con una palabra cambiada: decía «acuda con su faja
# puesta», y en otoplastia lo que se trae puesto es la banda.
_citas_p = bl(DP, 26)
if 'con su faja puesta' not in _citas_p['x']:
    raise SystemExit('el texto de las citas del lifting cambió; revise este cambio')
_citas_p['x'] = _citas_p['x'].replace('con su faja puesta', 'con su banda puesta')
B.append(_citas_p)
B.append({'t': 'citas', 'cols': ['Cita', 'Qué se hace', 'Fecha asignada'], 'x': [
    {'cita': '24 a 48 horas',
     'que': 'Retiro del vendaje, revisión de las orejas y colocación de la banda'},
    {'cita': 'Día ' + str(PUNTOS_DIA),
     'que': 'Retiro de los puntos de detrás de las orejas'},
    # ←CONFIRMAR — hasta qué cita se cita. Esto es el esquema del lifting
    # recortado; él no dijo si en otoplastia cita a los 12 meses.
    {'cita': 'Mes 1',
     'que': 'Revisión de cicatrices, inicio de silicona y fotografías'},
    {'cita': 'Mes 3', 'que': 'Revisión y fotografías'},
    {'cita': 'Mes 6', 'que': 'Resultado y fotografías'},
]})

# ----------------------------------------------------- 6. lo que es normal
# ←NUEVO — los ocho renglones. Ninguno sale de una hoja aprobada.
B.append({'t': 'h', 'x': '6. Lo que es normal y no debe preocuparle'})
B.append({'t': 'ul', 'x': [
    'Inflamación y moretones en las orejas y a su alrededor. Aumentan hasta el '
    'día 3 y después bajan de forma progresiva.',
    'Orejas rojas, calientes o de color morado claro durante las primeras '
    'semanas.',
    'Adormecimiento del pabellón de la oreja. Se recupera poco a poco entre 2 '
    'y 6 meses.',
    'Más sensibilidad al frío en las orejas durante varios meses.',
    'Comezón y pequeños piquetes mientras cicatriza.',
    'Diferencia entre una oreja y la otra en las primeras semanas, mientras '
    'baja la inflamación. Las dos orejas nunca son idénticas, tampoco lo eran '
    'antes de la cirugía.',
    'Una pequeña zona endurecida detrás de la oreja, donde están los puntos '
    'internos. Se suaviza en 2 a 3 meses.',
    'El resultado se aprecia desde el mes 1; el definitivo, entre los 3 y los '
    '6 meses.',
]})

# -------------------------------------------------------- 7. signos de alarma
B.append({'t': 'h', 'alarma': True,
          'x': '7. Signos de alarma: llame de inmediato al teléfono de urgencias'})
B.append(ul(
    [   # ←NUEVO — el hematoma de la oreja va primero: es lo que corre prisa.
        'Dolor intenso en UNA sola oreja que aumenta con las horas, sobre todo '
        'si esa oreja se ve más hinchada, tensa o brillante que la otra. No '
        'espere a su cita: llame.',
        'Piel de la oreja de color morado oscuro, negro o muy pálido.',
    ],
    li(DP, 31, 2, 3, 5, 6),                 # dolor que no cede · sangrado · fiebre · infección
    [   # ←NUEVO — lo propio del vendaje y la banda
        'El vendaje se aflojó, se recorrió o se cayó solo antes de su cita.',
        'La banda le aprieta, le duele o le deja la oreja pálida o con una '
        'marca profunda.',
    ],
    alarma=True,
))
B.append(bl(DP, 32))                        # la nota de urgencias

# --------------------------------------------------- 8. constancia de entrega
B.append({'t': 'h', 'x': '8. Constancia de entrega'})
B.append(bl(DP, 34))
B.append(bl(DP, 35))

hoja = {
    'id': 'otoplastia',
    'nombre': 'Otoplastia',
    'titulo': 'Recomendaciones postoperatorias — Otoplastia',
    # Aquí sí se puede sugerir sola: ninguna otra hoja responde a estas
    # palabras, así que `hojaSugerida()` encuentra una y sólo una.
    'coincide': ['otoplastia', 'otoplastía', 'cirugia de orejas',
                 'cirugía de orejas', 'orejas prominentes', 'orejas de soplillo'],
    'entrada': DP['entrada'],
    'bloques': B,
}

hoja['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in hoja.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

cat['hojas'] = [h for h in cat['hojas'] if h['id'] != hoja['id']]
# Después de las faciales y antes de las hojas de apoyo (faja, preoperatorias…)
pos = max(i for i, h in enumerate(cat['hojas']) if h['id'] == 'eco2') + 1
cat['hojas'].insert(pos, hoja)

cat['version'] = hashlib.sha256(json.dumps(
    {'hojas': cat['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

n = sum(len(b['x']) if b['t'] in ('ul', 'tabla', 'citas') else 1 for b in B)
print('hoja otoplastia  ·  versión ' + hoja['version'] +
      '  ·  ' + str(len(B)) + ' bloques, ' + str(n) + ' renglones')
print('catálogo  ·  versión ' + cat['version'] + '  ·  ' +
      str(len(cat['hojas'])) + ' hojas')
