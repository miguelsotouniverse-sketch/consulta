#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOS ANTIHIPERTENSIVOS DE BASE, 10 DÍAS, EN TODA CIRUGÍA ABIERTA
================================================================

Lo que pasó
-----------
El médico lo dijo así: «todas mis cirugías abiertas llevan en recomendaciones
de alta y recetas 2 antihipertensivos, el amlodipino y el metoprolol, pero
estamos siendo insuficientes». Y antes había quedado anotado el porqué: todas
se le descontrolaban de la presión a partir del día 2.

Al ir a cambiar la dosis me encontré con que el sistema no decía eso:

  · **El metoprolol no existía.** Ni a 25 mg ni a ninguna dosis, en ninguna de
    las nueve plantillas. No había nada que subir a 50: había que agregarlo.
  · **El amlodipino estaba mal escrito.** Decía «1 tableta la NOCHE ANTERIOR,
    dosis única» —que es lo que el médico indicó en octubre y lo que yo
    construí entonces—, y eso no es un antihipertensivo de base: es una
    premedicación. Una paciente que sigue su receta al pie de la letra se
    queda sin control de presión justo el día 2, que es cuando se descontrola.

Qué queda
---------
  amlodipino    5 mg cada 24 h, 10 días, empezando la MAÑANA ANTERIOR
  metoprolol   50 mg cada 12 h, 10 días, empezando el DÍA DEL ALTA

Los dos horarios de inicio los confirmó el médico el 28-oct-2026: «el
metoprolol inicia el día del alta, el amlodipino la mañana anterior». La
DURACIÓN de 10 días viene de lo que dejó anotado en octubre («por 10 días,
para mantener sistólica <130») y no se la volví a preguntar; si fuera otra,
se cambia aquí arriba y se vuelve a correr.     ←CONFIRMAR

Dónde entra
-----------
En las OCHO plantillas con incisión. Fuera queda sólo el láser eCO₂. El
médico dijo «todas mis cirugías abiertas» y la lipoescultura lleva incisiones,
así que Body360 entra; había una nota previa que decía «no lipos» y la
descarto por ser anterior y más vaga que lo que acaba de decir.   ←CONFIRMAR

Los dos renglones van ENCENDIDOS, como todo lo demás, y se apagan con la
casilla del renglón en la paciente que no los lleve.

En las hojas de alta
--------------------
Las hojas no nombraban ningún medicamento: decían «tome exclusivamente los de
su receta». Para dos fármacos que la paciente puede confundir con «los que
tomo si la siento alta», eso no alcanza. Se agrega un bloque corto que los
nombra, dice cuándo empieza cada uno y por qué no son opcionales.  ←NUEVO

Y la hoja preoperatoria decía «si en sus recetas viene amlodipino, tómelo
hoy». Ahora dice por la mañana, y que no es dosis única.

Uso:  python3 cambiar_antihipertensivos.py [recetas.json] [indicaciones.json]
      (al final de la cadena: necesita las nueve plantillas ya construidas)
"""

import json
import hashlib
import datetime
import sys

RUTA_RX  = sys.argv[1] if len(sys.argv) > 1 else 'recetas.json'
RUTA_IND = sys.argv[2] if len(sys.argv) > 2 else 'indicaciones.json'

DIAS = 10                      # ←CONFIRMAR (de lo anotado en octubre)
SIN_ANTIHIPERTENSIVO = {'eco2'}   # el láser no lleva incisión

AMLODIPINO_IND = (
    'Tomar 1 tableta vía oral cada 24 horas durante ' + str(DIAS) + ' días. '
    'La primera tableta se toma la MAÑANA ANTERIOR a la cirugía y de ahí en '
    'adelante una cada día, a la misma hora. Sirve para mantener su presión '
    'estable, que es lo que evita que se acumule sangre bajo la piel. No la '
    'suspenda porque se sienta bien ni porque su presión salga normal: es '
    'justamente lo que la mantiene normal.')
AMLODIPINO_CANT = str(DIAS) + ' tabletas'
AMLODIPINO_DUR  = str(DIAS) + ' días, desde la mañana anterior'
AMLODIPINO_HOR  = {'n': 'Amlodipino', 'h': ['08:00']}

METOPROLOL = {
    'hoja': 'general',
    'nombre': 'Metoprolol (tartrato) 50 mg, tabletas.',
    'indicacion':
        'Tomar 1 tableta vía oral cada 12 horas durante ' + str(DIAS) + ' días, '
        'empezando el DÍA DE SU ALTA. Es el segundo medicamento para la '
        'presión y trabaja junto con el amlodipino. Tómelo a sus horas los '
        + str(DIAS) + ' días completos, aunque se sienta bien.',
    'cantidad': str(DIAS * 2) + ' tabletas',
    'duracion': str(DIAS) + ' días, desde el día del alta',
    'horario': {'n': 'Metoprolol', 'h': ['08:00', '20:00']},
}

# ---------------------------------------------------------------- recetas
cat = json.load(open(RUTA_RX, encoding='utf-8'))
P = {p['id']: p for p in cat['plantillas']}

if any('Metoprolol' in m['nombre'] for p in cat['plantillas'] for m in p['medicamentos']):
    raise SystemExit('el metoprolol ya está en alguna plantilla; no se duplica')


def version_de(p):
    return hashlib.sha256(json.dumps(
        {k: v for k, v in p.items() if k != 'version'},
        ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]


tocadas, sin_amlo = [], []
for pid in sorted(P):
    p = P[pid]
    i = next((k for k, m in enumerate(p['medicamentos'])
              if m['nombre'].startswith('Amlodipino')), None)
    if pid in SIN_ANTIHIPERTENSIVO:
        if i is not None:
            raise SystemExit(pid + ' no debería traer amlodipino y lo trae')
        print('%-18s sin antihipertensivos (no lleva incisión)' % pid)
        continue
    if i is None:
        sin_amlo.append(pid)
        continue

    m = p['medicamentos'][i]
    if 'NOCHE ANTERIOR' not in m['indicacion']:
        raise SystemExit('el renglón del amlodipino de ' + pid + ' ya no es el '
                         'que esperaba; revíselo a mano antes de seguir')
    m['indicacion'] = AMLODIPINO_IND
    m['cantidad']   = AMLODIPINO_CANT
    m['duracion']   = AMLODIPINO_DUR
    m['horario']    = json.loads(json.dumps(AMLODIPINO_HOR))

    p['medicamentos'].insert(i + 1, json.loads(json.dumps(METOPROLOL, ensure_ascii=False)))
    antes = p['version']
    p['version'] = version_de(p)
    tocadas.append(pid)
    print('%-18s %s -> %s  (amlodipino corregido + metoprolol)' % (pid, antes, p['version']))

if sin_amlo:
    raise SystemExit('estas plantillas de cirugía abierta no traían amlodipino y '
                     'deberían: ' + ', '.join(sin_amlo))
if len(tocadas) != len(P) - len(SIN_ANTIHIPERTENSIVO & set(P)):
    raise SystemExit('no entró en todas las que debía')

cat['version'] = hashlib.sha256(json.dumps(
    {'plantillas': cat['plantillas'], 'hojas': cat['hojas'], 'horas': cat['horas']},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()
with open(RUTA_RX, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)
print('catálogo de recetas  ' + cat['version'] + '  (' + str(len(tocadas)) +
      ' plantillas con los dos antihipertensivos)')

# -------------------------------------------------------------- hojas
# El bloque va en las hojas de alta de cirugía: las que la paciente se lleva a
# su casa después de operarse. Fuera quedan la faja, las preoperatorias, los
# laboratorios y el láser, que no llevan estos medicamentos.
HOJAS_ALTA = ['deep_plane', 'lipoescultura', 'mastopexia', 'rinoplastia',
              'blefaroplastia', 'facial_combinada', 'deep_plane_co2', 'otoplastia']

TITULO_PRESION = 'Sus dos medicamentos para la presión'
BLOQUE_PRESION = [                                                      # ←NUEVO
    'Su receta incluye DOS medicamentos para la presión: amlodipino y '
    'metoprolol. No son opcionales y no se toman «si la siente alta»: se '
    'toman a sus horas los ' + str(DIAS) + ' días completos, aunque su presión '
    'salga normal. Mantenerla baja y estable es lo que evita que se acumule '
    'sangre bajo la piel.',
    'El amlodipino empieza la mañana anterior a su cirugía.',
    'El metoprolol empieza el día de su alta.',
    'Si tiene mareo al ponerse de pie, levántese despacio y en dos tiempos. '
    'Si se marea estando acostada, se siente muy débil o nota el corazón muy '
    'lento, llámenos antes de saltarse una toma: la dosis se ajusta, no se '
    'suspende por su cuenta.',
]

ind = json.load(open(RUTA_IND, encoding='utf-8'))
H = {h['id']: h for h in ind['hojas']}

puestas = 0
for hid in HOJAS_ALTA:
    if hid not in H:
        raise SystemExit('falta la hoja ' + hid)
    h = H[hid]
    if any(b['t'] == 'h2' and b.get('x') == TITULO_PRESION for b in h['bloques']):
        raise SystemExit('el bloque de presión ya estaba en ' + hid)

    # Va justo después de la sección de las primeras horas, que es donde la
    # paciente todavía está leyendo con atención, y antes de los cuidados.
    pos = None
    for i, b in enumerate(h['bloques']):
        if b['t'] == 'h' and 'rimeras' in str(b.get('x', '')):
            # el final de esa sección: hasta el siguiente encabezado 'h'
            for j in range(i + 1, len(h['bloques'])):
                if h['bloques'][j]['t'] == 'h':
                    pos = j
                    break
            break
    if pos is None:
        raise SystemExit('no encontré dónde poner el bloque de presión en ' + hid)

    h['bloques'].insert(pos, {'t': 'ul', 'x': list(BLOQUE_PRESION)})
    h['bloques'].insert(pos, {'t': 'h2', 'x': TITULO_PRESION})
    antes = h['version']
    h['version'] = hashlib.sha256(json.dumps(
        {k: v for k, v in h.items() if k != 'version'},
        ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]
    puestas += 1
    print('%-18s %s -> %s  (bloque de presión)' % (hid, antes, h['version']))

# La hoja preoperatoria: el amlodipino ya no es dosis única ni por la noche.
VIEJO = ('Si en sus recetas viene amlodipino 5 mg, tómelo hoy: una tableta. '
         'Ayuda a mantener su presión estable durante la cirugía y a reducir '
         'el sangrado y la inflamación.')
NUEVO = ('Si en sus recetas viene amlodipino 5 mg, tómelo HOY POR LA MAÑANA: '
         'una tableta. No es de una sola vez —sigue después, como dice su '
         'receta—. Ayuda a mantener su presión estable durante la cirugía y a '
         'reducir el sangrado y la inflamación.')

pre = H['preoperatorias']
hecho = False
for b in pre['bloques']:
    if b['t'] != 'ul':
        continue
    for k, x in enumerate(b['x']):
        if x == VIEJO:
            b['x'][k] = NUEVO
            hecho = True
if not hecho:
    raise SystemExit('no encontré la línea del amlodipino en la hoja preoperatoria')

antes = pre['version']
pre['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in pre.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]
print('%-18s %s -> %s  (amlodipino por la mañana)' % ('preoperatorias', antes, pre['version']))

ind['version'] = hashlib.sha256(json.dumps(
    {'hojas': ind['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
ind['generado'] = datetime.date.today().isoformat()
with open(RUTA_IND, 'w', encoding='utf-8') as f:
    json.dump(ind, f, ensure_ascii=False, indent=1)
print('catálogo de indicaciones  ' + ind['version'] + '  (' + str(puestas) +
      ' hojas con el bloque de presión)')
