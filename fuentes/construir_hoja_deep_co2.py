#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONSTRUYE LA HOJA DE DEEP PLANE FACELIFT + LÁSER CO₂
=====================================================

Por qué existe
--------------
En el catálogo había tres hojas que tocaban esta combinación y ninguna era
ésta:

  · `deep_plane`        el lifting completo, sin una palabra de láser
  · `eco2`              el láser solo, sin una palabra de lifting
  · `facial_combinada`  Deep Plane **de cuello** + blefaroplastia +
                        rinoplastia + CO₂ — otra cirugía

Entregar las dos sueltas no es una opción: se contradicen en el frío (el
lifting lo quiere sobre mejillas y cuello; el láser prohíbe la compresa
directa sobre la piel tratada), en el baño (lifting día 3, láser lavado de
cara desde el primer día), en el ejercicio (lifting semana 6, láser semana 3),
en el maquillaje y en el calendario entero. Y repiten tres veces «Primeras 72
horas».

Escoger `facial_combinada` por parecido es peor que no tener hoja: esa es de
Deep Plane **de cuello**, que no lleva malla hemostática ni incisión delante
de la oreja. Una paciente de lifting completo que reciba esa hoja se queda sin
la cita de las 72 horas para retirar la malla y sin el retiro de puntos
preauriculares.

Las dos reglas, las mismas de siempre
-------------------------------------
1. LO MÁS RESTRICTIVO GANA. Donde los dos protocolos dan plazos distintos para
   lo mismo, se escribe el más largo. Nunca el promedio.
2. LO QUE ES DE UNA ZONA, VA EN SU ZONA. Las incisiones del lifting y la piel
   tratada con láser se cuidan distinto y se escriben por separado, que es
   como la paciente se toca la cara.

Lo que esta hoja NO inventa
---------------------------
Ni un renglón clínico. Todo se copia por índice de `deep_plane` y de `eco2`,
que ya están aprobadas. Lo único redactado aquí es la caja de «si hoy sólo
puede leer una cosa», los renglones donde hubo que reconciliar dos plazos y
tres frases que dicen cuál de las dos instrucciones manda.

Lo que queda por confirmar
--------------------------
La FAJA FACIAL sobre la piel tratada con láser. El médico confirmó que la faja
sí va cuando el láser acompaña a un Deep Plane (13-oct-2026), y el renglón de
la faja se copia tal cual. Lo que nadie ha dicho es qué se pone entre la faja
y la piel en carne viva, ni si hay que aplicar Cicaplast antes de colocarla.
No me lo invento: va marcado abajo con ←CONFIRMAR y nombrado al entregar. El
mismo hueco existe hoy en `facial_combinada`.

Uso:  python3 construir_hoja_deep_co2.py [indicaciones.json]
      (después de construir_eco2.py: copia de esa hoja)
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'

CLOBESOL_DIAS = 7    # confirmado por el médico (13-oct-2026)

cat = json.load(open(RUTA, encoding='utf-8'))
H = {h['id']: h for h in cat['hojas']}
for req in ('deep_plane', 'eco2'):
    if req not in H:
        raise SystemExit('falta la hoja «' + req + '»: corra antes su constructor')
DP, E = H['deep_plane'], H['eco2']


def bl(hoja, i):
    """Un bloque entero, tal cual está aprobado."""
    return json.loads(json.dumps(hoja['bloques'][i], ensure_ascii=False))


def li(hoja, i, *js):
    """Renglones sueltos de una lista, por índice. Copiados, no retecleados."""
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


# Red de seguridad: si alguien reordena los bloques de las hojas de origen,
# los índices de abajo copiarían otra cosa y nadie se enteraría. Se comprueba
# que cada bloque del que se copia siga siendo el que era.
ANCLAS = [
    (DP, 2, 'ul', 'Reposo relativo.'),
    (DP, 14, 'ul', 'Puede bañarse y lavarse el cabello'),
    (DP, 16, 'ul', 'Limpie las incisiones'),
    (DP, 19, 'ul', 'Evite: limón'),
    (DP, 21, 'ul', 'Use prendas que se abotonen'),
    (DP, 29, 'ul', 'Inflamación y moretones'),
    (DP, 31, 'ul', 'Presión sistólica mayor de 130'),
    (E, 5, 'ul', 'Inflamación: la cara se hincha'),
    (E, 7, 'ul', 'Tome los medicamentos de su receta'),
    (E, 10, 'ul', 'Cicaplast: aplique una capa'),
    (E, 12, 'ul', 'Agua tibia y jabón neutro'),
    (E, 20, 'ul', 'Ardor y sensación de quemadura'),
    (E, 22, 'ul', 'Dolor que aumenta cada día'),
]
for hoja, i, t, inicio in ANCLAS:
    b = hoja['bloques'][i]
    if b['t'] != t or not str(b['x'][0]).startswith(inicio):
        raise SystemExit(
            'El bloque ' + str(i) + ' de la hoja «' + hoja['id'] + '» ya no es '
            'el que era (esperaba «' + inicio + '…»). Los índices de este '
            'constructor copiarían el texto equivocado: revíselos antes de seguir.')

B = []   # los bloques de la hoja nueva, en orden

# ---------------------------------------------------------------- portada
B.append({'t': 'h2', 'x': 'Datos del procedimiento'})
B.append({'t': 'tabla', 'x': [[
    'Procedimiento',
    'Ritidectomía Deep Plane (lifting facial y de cuello) · Láser fraccionado '
    'de CO₂ (eCO₂) en rostro y cuello']]})

# Una paciente recién operada, con analgésicos encima, no lee ocho páginas; y
# a las dos de la mañana su acompañante tampoco. Esta caja va primero y se lee
# sola. No trae nada que no esté más abajo: es el resumen de lo que no puede
# esperar a mañana, tomado de las dos hojas aprobadas.
B.append({'t': 'nota', 'x':
    'SI HOY SÓLO PUEDE LEER UNA COSA, LEA ESTO. '
    '1) Boca arriba, cabeza a 45°, día y noche, 14 días. '
    '2) Frío sobre mejillas y cuello, 15 minutos cada hora, siempre con un '
    'paño limpio y seco de por medio: nunca directo sobre la piel del láser. '
    '3) No se agache, no cargue más de 2 kg, no puje. '
    '4) La piel tratada con láser nunca debe quedar seca: Cicaplast y vaselina '
    'encima, las veces que haga falta, con las manos limpias. '
    '5) No se baña hasta el día 3; la cara sí se lava desde hoy. '
    '6) Tome su presión cada 2 horas y repórtela. '
    '7) Acompañada por un adulto día y noche las primeras 72 horas. '
    'Lo demás de esta hoja lo puede leer con calma mañana.'})

# ------------------------------------------------- 1. primeras 72 horas
B.append({'t': 'h', 'x': '1. Primeras 72 horas: lo más importante'})
B.append(bl(DP, 1))                        # el riesgo principal es el hematoma
B.append({'t': 'p', 'x':
    'Se hicieron dos cosas el mismo día: la cirugía y el láser. Las '
    'indicaciones de cada una están más adelante, por separado; esta primera '
    'sección manda sobre las dos. Donde algo parezca distinto, siga siempre lo '
    'más estricto.'})
B.append(ul(
    li(DP, 2, 0, 1, 2, 3, 4),              # reposo · no agacharse · no gritar · posición · cuello
    [   # Frío: reconciliado. El lifting lo quiere sobre mejillas y cuello; el
        # láser prohíbe la compresa directa sobre la piel tratada y prohíbe
        # reutilizar una compresa. Se escriben las dos condiciones en un solo
        # renglón, porque son el mismo gesto.
        'Frío local: compresas frías o gel frío envueltos en un paño delgado, '
        'limpio y seco, 15 minutos cada hora mientras esté despierta, sobre '
        'mejillas y cuello. Nunca hielo directo sobre la piel, nunca '
        'directamente sobre la piel tratada con láser, y nunca una compresa o '
        'un paño que ya se usó. Suspenda el frío a las 72 horas.',
    ],
    # ←CONFIRMAR: la faja va tal como está aprobada en la hoja del lifting. Lo
    # que nadie ha indicado es qué se interpone entre la faja y la piel en
    # carne viva, ni si se aplica Cicaplast antes de colocarla. No se inventa.
    li(DP, 2, 6, 7, 8, 9),                 # faja · drenajes · presión · acompañante
    li(E, 5, 2, 3, 4),                     # ardor · viento y polvo · 2 litros de agua
))
B.append(bl(DP, 3))                        # h2 toma de presión arterial
B.append(bl(DP, 4))

# ------------------------------------------------------- 2. medicamentos
B.append({'t': 'h', 'x': '2. Medicamentos'})
B.append(ul(
    li(DP, 6, 0),                          # tome exclusivamente los de su receta
    li(E, 7, 1, 2),                        # el antiviral empieza la víspera · Clobesol sólo los días indicados
))
for i in (7, 8, 9, 10, 11):
    B.append(bl(DP, i))                    # prohibidos · tabaco · alcohol · manejar

# ---------------------------------------------------- 3. cuidados por zona
B.append({'t': 'h', 'x': '3. Cuidados por zona'})

B.append({'t': 'h2', 'x': 'Baño y cabello'})
B.append({'t': 'p', 'x':
    'Aquí los dos tratamientos dicen cosas distintas y conviene no confundirse: '
    'lo que espera hasta el día 3 es el baño de regadera y el lavado del '
    'cabello. La cara se lava desde el primer día, como dice el apartado de la '
    'piel tratada con láser.'})
B.append(ul(
    li(DP, 14, 0, 1, 2),                   # baño día 3 · secadora aire frío · tinte
))

B.append({'t': 'h2', 'x': 'Incisiones del lifting'})
B.append(ul(li(DP, 16, 0, 1, 2, 3)))

# El apartado del láser entero, copiado de su hoja: es un tratamiento, no una
# recomendación, y de él depende que la piel cierre con o sin mancha.
B.append({'t': 'h2', 'x': 'Piel tratada con láser CO₂ (rostro y cuello)'})
B.append(bl(E, 4))                         # queda en carne viva, cierra en 7-10 días
B.append(bl(E, 9))                         # esto es el tratamiento
B.append(ul(li(E, 10, 0, 1, 2, 3, 4, 5, 6, 7, 8)))
B.append({'t': 'h2', 'x': 'Cómo lavarse la cara'})
B.append(ul(li(E, 12, 0, 1, 2, 3)))

B.append({'t': 'h2', 'x': 'Alimentación — dieta para la glándula submandibular'})
B.append(bl(DP, 18))
B.append(ul(li(DP, 19, 0, 1, 2, 3, 4)))

B.append({'t': 'h2', 'x': 'Ropa y accesorios'})
B.append(ul(
    li(DP, 21, 0, 1, 2),                   # prendas que abren · aretes · lentes
    [   # Maquillaje: el lifting lo permite el día 14 fuera de las incisiones;
        # el láser, el día 14 y sólo con la piel cerrada por completo. Gana el
        # del láser, que es el que puede costar una infección.
        'Maquillaje en el rostro: a partir del día 14, fuera de las incisiones '
        'y sólo si la piel tratada con láser ya cerró por completo.',
    ],
))

# ------------------------------------------------ 4. calendario reconciliado
B.append({'t': 'h', 'x': '4. Calendario de actividades'})
B.append({'t': 'p', 'x':
    'Un solo calendario para la cirugía y el láser. Cada renglón lleva el plazo '
    'más largo de los dos: es el que aplica cuando se hacen el mismo día.'})
B.append({'t': 'tabla', 'cols': ['Actividad', 'A partir de', 'Nota'], 'x': [
    ['Caminar dentro de casa', 'Día 1', '5 minutos cada 2 horas'],
    ['Salir al patio o al balcón, a la sombra', 'Día 1',
     'Con gorra o sombrero de ala ancha'],
    ['Caminar fuera de casa (paseo tranquilo)', 'Día 4',
     'A la sombra, con gorra o sombrero de ala ancha'],
    ['Drenaje linfático manual facial', 'Día 7',
     'Con terapeuta autorizado por el consultorio — 10 sesiones, 2 a 3 por semana'],
    ['Manejar', 'Día 8', 'Sin analgésicos que den sueño'],
    ['Viajar en avión', 'Día 10', ''],
    ['Trabajo de oficina y vida social', 'Día 14',
     'Antes la cara se ve roja e hinchada; el trabajo desde casa puede retomarse '
     'en cuanto se sienta bien'],
    ['Relaciones sexuales', 'Día 14', 'Sin esfuerzo intenso'],
    ['Maquillaje en el rostro', 'Día 14',
     'Fuera de las incisiones y sólo con la piel del láser cerrada por completo'],
    ['Cardio ligero (caminadora, bicicleta fija suave)', 'Semana 3',
     'Sin sudar hasta que la piel haya cerrado'],
    ['Alberca y mar', 'Semana 4', ''],
    ['Ácidos, retinoides, exfoliantes, mascarillas y limpiadores con alcohol',
     'Semana 4', ''],
    ['Secadora con aire caliente, plancha o tenazas', 'Semana 4',
     'Antes, sólo aire frío'],
    ['Pesas, yoga, pilates, correr, deportes y ejercicio de impacto', 'Semana 6', ''],
    ['Sauna, vapor, temazcal, jacuzzi', 'Semana 6', ''],
    ['Tinte, decoloración, keratina o permanente', 'Semana 6', ''],
    ['Depilación con cera o láser en la zona tratada', 'Semana 6',
     'Sólo con autorización'],
    ['Exposición directa al sol', 'Semana 6',
     'Siempre con sombrero de ala ancha y protector FPS 50+'],
    ['Tratamientos faciales (toxina botulínica, rellenos, peelings, láser, '
     'radiofrecuencia)', 'Mes 3', 'Sólo con autorización del Dr. Soto'],
    ['Masajes faciales fuera del drenaje indicado', 'Mes 3', ''],
]})
B.append(bl(DP, 24))                       # protección solar 12 meses

# ------------------------------------------------------------- 5. citas
B.append({'t': 'h', 'x': '5. Citas de seguimiento'})
B.append(bl(DP, 26))
citas = bl(DP, 27)
# Las ocho citas del lifting, intactas. Tres mencionan además la piel del
# láser, porque el calendario del cierre (7 a 10 días) cae justo entre la cita
# del día 5 y la del día 10: no hace falta una cita extra, hace falta que en
# esas se revise.
citas['x'] = [
    citas['x'][0],                         # 24 horas — hematoma y drenajes
    {'cita': '72 horas',
     'que': 'Retiro de la malla hemostática y primera revisión de la piel '
            'tratada con láser'},
    citas['x'][2],                         # día 5 — puntos del rostro
    {'cita': 'Día 10',
     'que': 'Retiro de puntos detrás de la oreja y grapas del cuero cabelludo, '
            'y revisión del cierre de la piel tratada con láser'},
    citas['x'][4],                         # mes 1 — cicatrices y silicona
    {'cita': 'Mes 3',
     'que': 'Revisión y fotografías; se decide si hay una segunda sesión de láser'},
    citas['x'][6],                         # mes 6
    citas['x'][7],                         # mes 12
]
if citas['x'][0]['cita'] != '24 horas' or citas['x'][2]['cita'] != 'Día 5':
    raise SystemExit('las citas del lifting cambiaron de orden; revise este bloque')
B.append(citas)

# ----------------------------------------------------- 6. lo que es normal
B.append({'t': 'h', 'x': '6. Lo que es normal y no debe preocuparle'})
B.append({'t': 'h2', 'x': 'Rostro y cuello (lifting)'})
B.append(ul(li(DP, 29, 0, 1, 2, 3, 4, 5, 6, 7, 8)))
B.append({'t': 'h2', 'x': 'Piel tratada con láser'})
# Se cae el renglón 1 del láser (inflamación de la cara): el del lifting ya lo
# dice, con más detalle y con su propio plazo.
B.append(ul(li(E, 20, 0, 2, 3, 4, 5, 6, 7)))

# -------------------------------------------------------- 7. signos de alarma
B.append({'t': 'h', 'alarma': True,
          'x': '7. Signos de alarma: llame de inmediato al teléfono de urgencias'})
B.append(ul(
    li(DP, 31, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    # Del láser entran los cuatro que no están ya arriba. Fuera quedan su
    # fiebre, su enrojecimiento que se extiende y su sangrado: duplicados.
    li(E, 22, 0, 1, 2, 5),
    alarma=True,
))
B.append(bl(DP, 32))                       # la nota de urgencias

# --------------------------------------------------- 8. constancia de entrega
B.append({'t': 'h', 'x': '8. Constancia de entrega'})
B.append(bl(DP, 34))
B.append(bl(DP, 35))

hoja = {
    'id': 'deep_plane_co2',
    # El nombre dice «completo» a propósito: en el menú hay que poder
    # distinguirla de la combinada, que es Deep Plane DE CUELLO y no lleva ni
    # malla hemostática ni puntos delante de la oreja.
    'nombre': 'Deep Plane Facelift completo + láser CO₂',
    'titulo': 'Recomendaciones postoperatorias — Deep Plane Facelift y láser de CO₂',
    # Vacío a propósito: `hojaSugerida()` sólo sugiere cuando UNA hoja
    # coincide. Si ésta trajera "deep plane", un lifting solo encontraría dos
    # y se quedaría sin sugerencia. Esta hoja se escoge a mano.
    'coincide': [],
    'entrada': DP['entrada'],
    'bloques': B,
}

hoja['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in hoja.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

cat['hojas'] = [h for h in cat['hojas'] if h['id'] != hoja['id']]
pos = max(i for i, h in enumerate(cat['hojas']) if h['id'] == 'facial_combinada') + 1
cat['hojas'].insert(pos, hoja)

cat['version'] = hashlib.sha256(json.dumps(
    {'hojas': cat['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

n = sum(len(b['x']) if b['t'] in ('ul', 'tabla', 'citas') else 1 for b in B)
print('hoja deep_plane_co2  ·  versión ' + hoja['version'] +
      '  ·  ' + str(len(B)) + ' bloques, ' + str(n) + ' renglones')
print('catálogo  ·  versión ' + cat['version'] + '  ·  ' +
      str(len(cat['hojas'])) + ' hojas')
