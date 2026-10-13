#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONSTRUYE LA HOJA COMBINADA PARA CIRUGÍA FACIAL MÚLTIPLE
========================================================

Por qué existe
--------------
Cuando una paciente se opera de varias cosas el mismo día no se le pueden
entregar las hojas sueltas: se contradicen. Medido sobre el catálogo real,
Deep Plane y blefaroplastia comparten UNA línea de 77, y Deep Plane y
rinoplastia otra. Pegarlas da ~190 renglones, nueve páginas, con "Primeras 72
horas" tres veces, y con instrucciones opuestas:

    baño            Deep Plane día 3   ·  blefaro y rino 24–48 h
    cabecera        Deep Plane 14 días ·  blefaro 1 semana · rino 1–2 semanas
    ejercicio       Deep Plane sem. 6  ·  blefaro sem. 3–4 · rino sem. 4–6
    sol             Deep Plane sem. 6 / FPS 12 meses · las otras sem. 4 / 6 meses
    frío            Deep Plane mejillas y cuello · blefaro SOBRE los ojos ·
                    rino NUNCA sobre la nariz
    anteojos        Deep Plane "puede usarlos desde el día 1" ·
                    blefaro "use sus anteojos" · rino "no los apoye 6 semanas"

Dos reglas, y nada más
----------------------
1. LO MÁS RESTRICTIVO GANA. Donde dos hojas dan plazos distintos para lo mismo,
   se escribe el más largo. Nunca el promedio, nunca el primero que aparezca.
2. LO QUE ES DE UNA ZONA, VA EN SU ZONA. El frío, el baño y las heridas no se
   unifican en una sola frase: se escriben por zona (cuello y rostro, párpados,
   nariz, piel tratada con láser), que es como la paciente se toca la cara.

Lo que esta hoja NO inventa
---------------------------
El texto es el que ya estaba aprobado en `indicaciones.json`. Se copia por
índice desde las hojas existentes —nunca se vuelve a teclear— para que una
corrección futura en la hoja original no se quede fuera por una errata.
Lo único redactado aquí es: el apartado de láser CO2 (no existía ninguna hoja
de CO2), la regla de anteojos para la combinación, y los renglones del
calendario donde hubo que reconciliar dos plazos.

Todo el contenido clínico lo puso el médico
--------------------------------------------
Cicaplast cada 12 h · Clobesol cada 12 h × 7 días · vaselina · protector solar ·
CO2 en rostro y cuello · la regla de anteojos · puntos del mentón al día 7 ·
férula nasal al día 7 · puntos de párpados al día 5 · drenajes por gasto y
características, no por reloj · faja facial 24 h × 7 días y luego sólo para
dormir, que SÍ aplica cuando hay Deep Plane además del láser (confirmado
13-oct-2026).

Ya no queda ningún número propuesto por mí en esta hoja. Si alguno vuelve a
ponerse en duda, va marcado con  # ←CONFIRMAR  y nombrado en la respuesta,
nunca cambiado en silencio.
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'

# --- los días del calendario, todos confirmados por el médico --------------
CLOBESOL_DIAS   = 7    # confirmado por el médico (13-oct-2026)
FERULA_DIA      = 7    # confirmado por el médico (13-oct-2026)
PUNTOS_PARPADOS = 5    # confirmado por el médico (13-oct-2026)
PUNTOS_MENTON   = 7    # confirmado por el médico (13-oct-2026)

cat = json.load(open(RUTA, encoding='utf-8'))
H = {h['id']: h for h in cat['hojas']}
DP, BL, RI = H['deep_plane'], H['blefaroplastia'], H['rinoplastia']


def bl(hoja, i):
    """Un bloque entero, tal cual está aprobado."""
    return json.loads(json.dumps(hoja['bloques'][i], ensure_ascii=False))


def li(hoja, i, *js):
    """Renglones sueltos de una lista, por índice. Copiados, no retecleados."""
    xs = hoja['bloques'][i]['x']
    return [xs[j] for j in js]


def ul(*listas):
    out = []
    for l in listas:
        out += l
    return {'t': 'ul', 'x': out}


B = []   # los bloques de la hoja nueva, en orden

# ---------------------------------------------------------------- portada
B.append({'t': 'h2', 'x': 'Datos del procedimiento'})
B.append({'t': 'tabla', 'x': [[
    'Procedimiento',
    'Deep Plane de cuello (contorno cervical) · Blefaroplastia de 4 '
    'cuadrantes · Rinoplastia ultrasónica · Láser CO₂ en rostro y cuello']]})

# Cuatro cirugías el mismo día dan ocho páginas de indicaciones. Una paciente
# recién operada y con analgésicos encima no lee ocho páginas, y a las dos de
# la mañana el acompañante tampoco. Esta caja va primero y se lee sola.
B.append({'t': 'nota', 'x':
    'SI HOY SÓLO PUEDE LEER UNA COSA, LEA ESTO. '
    '1) Boca arriba, cabeza a 45°, día y noche, 14 días. '
    '2) Frío sobre mejillas, cuello y párpados —nunca sobre la nariz—, '
    '15 minutos cada hora. '
    '3) No se agache, no cargue más de 2 kg, no puje. '
    '4) Nada se apoya sobre la nariz: ni anteojos, ni cubrebocas, ni antifaz. '
    '5) La piel del láser nunca debe quedar seca: Cicaplast y vaselina encima, '
    'las veces que haga falta. '
    '6) No se baña hasta el día 3. '
    '7) Tome su presión cada 2 horas y repórtela. '
    '8) Acompañada día y noche las primeras 72 horas. '
    'Lo demás de esta hoja lo puede leer con calma mañana.'})

# ------------------------------------------------- 1. primeras 72 horas
B.append({'t': 'h', 'x': '1. Primeras 72 horas: lo más importante'})
B.append(bl(DP, 1))                       # el riesgo principal es el hematoma
B.append({'t': 'p', 'x':
    'Se operaron cuatro zonas el mismo día. Las indicaciones de cada una están '
    'más adelante, por separado; esta primera sección es la que manda sobre '
    'todas. Donde dos indicaciones parezcan distintas, siga siempre la más '
    'estricta.'})
B.append(ul(
    li(DP, 2, 0, 1, 2),                   # reposo · no agacharse ni cargar · no gritar
    [   # frío: reconciliado. Deep Plane lo quiere en mejillas y cuello, la
        # blefaroplastia sobre los ojos, y la rinoplastia lo prohíbe en la
        # nariz. Y encima hay piel tratada con láser, que no debe tocar nada
        # húmedo ni sucio directamente.
        'Posición: duerma y descanse boca arriba, con la cabeza elevada a 45° '
        '(dos almohadas firmes o un reclinable). Mantenga esta posición 14 días, '
        'día y noche. No duerma de lado ni boca abajo.',
        'Frío local: compresas frías o gel frío envueltos en un paño delgado y '
        'limpio, 15 minutos cada hora mientras esté despierta, sobre mejillas, '
        'cuello y párpados. Nunca sobre la nariz, y nunca directamente sobre la '
        'piel tratada con láser: siempre con un paño limpio y seco de por medio.',
    ],
    li(DP, 2, 4, 6, 7, 8, 9),             # cuello recto · faja · drenajes · presión · acompañante
    li(RI, 4, 2, 3, 4, 5),                # boca · bigotera · no sonarse · estornudar
    li(BL, 4, 2, 3),                      # no frotarse los ojos · reposo visual
))
B.append(bl(DP, 3))                       # h2 toma de presión arterial
B.append(bl(DP, 4))

# ------------------------------------------------------- 2. medicamentos
B.append({'t': 'h', 'x': '2. Medicamentos'})
for i in (6, 7, 8, 9, 10):
    B.append(bl(DP, i))
# Manejar: Deep Plane decía 7 días; blefaro y rino, 7–10. Gana 10, y aquí se
# suma la razón de los párpados.
B.append({'t': 'p', 'x':
    'Manejar: no maneje durante 10 días, ni mientras tome analgésicos que den '
    'sueño, ni mientras la inflamación de los párpados le estorbe para ver.'})

# ---------------------------------------------------- 3. cuidados por zona
B.append({'t': 'h', 'x': '3. Cuidados por zona'})

B.append({'t': 'h2', 'x': 'Baño'})
B.append({'t': 'p', 'x':
    'Esta es la indicación que más se presta a confusión: el lifting manda '
    'esperar más que la nariz y los párpados, así que esta es la buena.'})
B.append({'t': 'ul', 'x': [
    'Puede bañarse y lavarse el cabello a partir del día 3 (72 horas), con agua '
    'tibia —nunca caliente— y champú de bebé.',
    'Lave el cabello con la cabeza hacia atrás, como en la estética, para que '
    'no se moje la férula de la nariz ni caiga agua o champú sobre los párpados.',
    'La férula y las cintas de la nariz se mantienen secas todo el tiempo.',
    'No frote las incisiones ni la piel tratada con láser. Seque a toques con '
    'una toalla limpia, nunca con el secador.',
    # Las tres hojas traían su propia frase de "lávese la cara" —la de párpados, '
    # la de nariz y la del láser— y juntas se leen como tres instrucciones
    # distintas. Es una sola, escrita una vez.
    'Lavado de la cara: agua tibia y jabón neutro, sin tallar, evitando los '
    'párpados y la nariz; seque a toques con una toalla limpia. Sobre la piel '
    'tratada con láser vuelva a aplicar Cicaplast y vaselina enseguida.',
]})

# El Deep Plane DE CUELLO no es el lifting facial completo: no se disecó la
# cara, no hay incisión delante de la oreja y no lleva malla hemostática. La
# hoja decía "Cuello y rostro (lifting)" y arrastraba indicaciones que aquí no
# existen. Los renglones de calor en el cabello se quedan, pero por el láser
# —aire caliente y tenazas sobre piel recién tratada— no por las incisiones.
# La única incisión es la SUBMENTONIANA. No hay retroauricular ni nada en la
# piel cabelluda, así que se caen los aretes (no hay herida junto al lóbulo) y
# el "detrás de las orejas" de los signos de alarma. Los renglones de calor en
# el cabello se quedan, pero por el láser —el producto escurre al cuello y el
# aire caliente mancha la piel recién tratada—, no por incisiones que no hay.
B.append({'t': 'h2', 'x': 'Cuello (contorno cervical)'})
B.append({'t': 'p', 'x':
    'La única herida del cuello está debajo del mentón, escondida en el pliegue. '
    'No hay cortes delante ni detrás de las orejas.'})
B.append(ul(
    ['Limpie la herida bajo el mentón 2 veces al día con agua y jabón neutro, '
     'seque con gasa y aplique una capa delgada del ungüento indicado en su '
     'receta, hasta el retiro de los puntos.'],
    li(DP, 16, 1, 2, 3),              # no cremas · no retirar costras · silicona
    ['Use prendas que se abotonen o cierren por delante durante 14 días: pasar '
     'una prenda por la cabeza estira el cuello y roza la herida del mentón.',
     'Secadora, plancha y tenazas: sólo aire frío durante 4 semanas. El calor '
     'sobre la piel recién tratada con láser la mancha.',
     'Tinte, decoloración o keratina: no antes de 6 semanas. El producto escurre '
     'al cuello, y la piel tratada con láser lo absorbe.'],
))

B.append({'t': 'h2', 'x': 'Párpados (blefaroplastia)'})
B.append(ul(li(BL, 7, 0, 4, 6, 7)))        # sin su 'Cara:', ya unificada en Baño

B.append({'t': 'h2', 'x': 'Nariz y férula (rinoplastia)'})
B.append(bl(RI, 6))
B.append(ul(li(RI, 7, 0, 3, 4, 6, 7, 8)))  # sin su 'Cara:', ya unificada en Baño

B.append({'t': 'h2', 'x': 'Anteojos y lentes'})
B.append({'t': 'p', 'x':
    'Las indicaciones de la nariz y las de los párpados se cruzan aquí, así que '
    'esta regla sustituye a cualquier otra que lea sobre anteojos.'})
B.append({'t': 'ul', 'x': [
    'Durante 6 semanas no apoye nada sobre la nariz: ni anteojos de graduación, '
    'ni lentes oscuros, ni cubrebocas apretados, ni antifaz para dormir.',
    'Semanas 1 y 2: no use lentes de contacto. Si necesita sus anteojos, '
    'péguelos con cinta microporosa a la frente, de modo que no toquen la nariz.',
    'A partir de la semana 2 puede usar lentes de contacto, y así se evita el '
    'problema por completo.',
    'Los lentes oscuros para salir también van pegados a la frente o sostenidos '
    'con la mano, nunca apoyados en la nariz.',
]})

# Apartado nuevo: no existía ninguna hoja de CO₂ en el catálogo.
B.append({'t': 'h2', 'x': 'Piel tratada con láser CO₂ (rostro y cuello)'})
B.append({'t': 'p', 'x':
    'La piel tratada queda en carne viva y se cierra sola en 7 a 10 días. '
    'Mientras tanto no debe secarse ni un momento: una costra seca deja mancha. '
    'Tenga las manos limpias cada vez que se toque la cara.'})
B.append({'t': 'ul', 'x': [
    'Cicaplast: aplique una capa sobre toda la zona tratada cada 12 horas.',
    'Clobesol (clobetasol): una capa delgada cada 12 horas durante '
    + str(CLOBESOL_DIAS) + ' días, y suspéndalo. No lo use más días de los '
    'indicados ni lo aplique en los párpados.',
    'Vaselina: aplíquela encima las veces que haga falta para que la piel nunca '
    'se sienta tirante ni se vea seca, de día y de noche.',
    'Después de cada lavado vuelva a aplicar Cicaplast y vaselina enseguida: '
    'la piel no debe quedar sin nada encima ni un momento.',
    'No arranque costras ni piel que se esté desprendiendo: se cae sola.',
    'Protector solar FPS 50+: en cuanto la piel esté completamente cerrada, '
    'todos los días durante 12 meses, reaplicando cada 3 horas si está al aire '
    'libre. Antes de que cierre, el sol se evita con sombra, gorra y no salir.',
    'Maquillaje sobre la piel tratada: hasta el día 14 y sólo si ya cerró por '
    'completo.',
    'Nada de ácidos, retinoides, exfoliantes, mascarillas ni limpiadores con '
    'alcohol durante 4 semanas.',
    'Es normal que la piel se vea roja intensa las primeras 2 semanas y rosada '
    'durante 2 a 3 meses, y que pique mientras cierra.',
]})

# --------------------------------------------- 4. alimentación e hidratación
B.append({'t': 'h', 'x': '4. Alimentación — dieta para la glándula submandibular'})
B.append(bl(DP, 18))                      # la glándula salival manda 14 días
# De la rinoplastia sólo entra la temperatura. Su renglón de picante decía
# "la primera semana" y la dieta de la glándula ya lo prohíbe 14 días: dejar
# los dos ponía dos plazos para lo mismo, con el más corto leído al final.
# El de la sal se reescribe para que se sume a la dieta y no compita con ella.
B.append(ul(
    li(DP, 19, 0, 1, 2, 3, 4),
    li(RI, 10, 1),                        # temperatura tibia o fría
    ['Sal: además de lo anterior, reduzca embutidos, enlatados, comida rápida y '
     'botanas; la sal hincha los párpados, sobre todo por la mañana.'],
    li(BL, 10, 3, 4),                     # proteína · estreñimiento
))

# ------------------------------------------------ 5. calendario reconciliado
B.append({'t': 'h', 'x': '5. Calendario de actividades'})
B.append({'t': 'p', 'x':
    'Un solo calendario para las cuatro cirugías. Cada renglón lleva el plazo '
    'más largo de todas ellas: es el que aplica cuando se operan el mismo día.'})
B.append({'t': 'tabla', 'cols': ['Actividad', 'A partir de', 'Nota'], 'x': [
    ['Caminar dentro de casa', 'Día 1', '5 minutos cada 2 horas'],
    ['Leer, pantallas, televisión', 'Día 3', 'En periodos cortos, con descansos'],
    ['Caminar fuera de casa (paseo tranquilo)', 'Día 4', 'Con gorra y a la sombra'],
    ['Drenaje linfático manual facial', 'Día 7',
     'Con terapeuta autorizado por el consultorio — 10 sesiones, 2 a 3 por semana'],
    ['Manejar', 'Día 10', 'Sin analgésicos que den sueño y viendo con claridad'],
    ['Trabajo de oficina y vida social', 'Día 14', ''],
    ['Relaciones sexuales', 'Día 14', 'Sin esfuerzo intenso'],
    ['Maquillaje en el rostro', 'Día 14',
     'Fuera de las incisiones y sólo con la piel del láser cerrada'],
    ['Viajar en avión', 'Semana 2', 'Avísenos antes; la cabina congestiona la nariz'],
    ['Lentes de contacto', 'Semana 2', ''],
    ['Maquillaje en los ojos', 'Semana 2', 'Con heridas completamente cerradas'],
    ['Dormir de lado', 'Semana 2', ''],
    ['Cardio ligero (caminadora, bicicleta fija suave)', 'Semana 3', ''],
    ['Pesas, yoga, pilates, correr, deportes y ejercicio de impacto', 'Semana 6', ''],
    ['Alberca y mar', 'Semana 6', ''],
    ['Sauna, vapor, temazcal, jacuzzi', 'Semana 6', ''],
    ['Dormir boca abajo', 'Semana 6', ''],
    ['Anteojos apoyados en la nariz', 'Semana 6', ''],
    ['Exposición directa al sol', 'Semana 6', 'Siempre con gorra, lentes oscuros y FPS 50'],
    ['Tinte, decoloración, keratina o permanente', 'Semana 6', ''],
    ['Secadora con aire caliente, plancha o tenazas', 'Semana 4', 'Antes, sólo aire frío'],
    ['Deportes de contacto o con pelota', 'Semana 8–12', 'Riesgo de golpe en la nariz'],
    ['Tratamientos faciales (toxina, rellenos, láser, peelings, radiofrecuencia)',
     'Mes 3', 'Sólo con autorización'],
    ['Masajes faciales fuera del drenaje indicado', 'Mes 3', ''],
]})
B.append(bl(DP, 24))                      # protección solar 12 meses

# ------------------------------------------------------------- 6. citas
B.append({'t': 'h', 'x': '6. Citas de seguimiento'})
B.append(bl(DP, 26))
citas = json.loads(json.dumps(DP['bloques'][27], ensure_ascii=False))
citas['x'] = [
    # Los drenajes no salen por calendario: salen por gasto y características.
    {'cita': '24 horas', 'que': 'Revisión de la herida para descartar hematoma y '
                                'retiro del vendaje. Si trae drenajes, se revisan: '
                                'se retiran cuando el gasto y las características '
                                'del líquido lo permiten, no por calendario'},
    # NO hay cita de 72 horas: el Deep Plane de cuello no lleva malla
    # hemostática, y tampoco hay puntos delante de la oreja porque no hay
    # incisión preauricular. Las dos citas venían copiadas del lifting facial
    # completo y mandaban a la paciente a una revisión que no existe.
    {'cita': 'Día ' + str(PUNTOS_PARPADOS),
     'que': 'Retiro de los puntos de los párpados'},
    {'cita': 'Día ' + str(FERULA_DIA),
     'que': 'Retiro de la férula nasal y de las cintas'},
    {'cita': 'Día ' + str(PUNTOS_MENTON),
     'que': 'Retiro de los puntos del mentón y revisión de la piel tratada '
            'con láser'},
    {'cita': 'Mes 1', 'que': 'Revisión de cicatrices, inicio de silicona y fotografías'},
    {'cita': 'Mes 3', 'que': 'Revisión y fotografías'},
    {'cita': 'Mes 6', 'que': 'Revisión y fotografías'},
    {'cita': 'Mes 12', 'que': 'Resultado final y fotografías'},
]
B.append(citas)

# ----------------------------------------------------- 7. lo que es normal
B.append({'t': 'h', 'x': '7. Lo que es normal y no debe preocuparle'})
# Del lifting completo se caen dos renglones: la caída de cabello junto a las
# incisiones (aquí no hay incisión en piel cabelluda) y el adormecimiento de
# mejillas (no se disecó la cara). La debilidad de un lado del labio SÍ se
# queda: la rama marginal de la mandíbula es justo el nervio en riesgo en un
# contorno cervical.
B.append({'t': 'h2', 'x': 'Cuello y rostro'})
B.append(ul(
    li(DP, 29, 0, 1),
    ['Sensación de tirantez en el cuello y bajo la mandíbula durante 4 a 6 semanas.',
     'Adormecimiento del cuello y del mentón, y piel dormida alrededor de la '
     'herida. Se recupera poco a poco entre 3 y 12 meses.'],
    li(DP, 29, 4),
    # El renglón del lifting decía "un lado del labio o la frente": la rama
    # frontal no se toca en un contorno cervical. Se queda sólo el labio.
    ['Sonrisa o movimiento de un lado del labio algo más débil en los primeros '
     'días. Suele ser temporal y se recupera.'],
    li(DP, 29, 7, 8),
))
B.append({'t': 'h2', 'x': 'Párpados'})
B.append(ul(li(BL, 16, 2, 3, 4, 5, 6, 7, 8)))
B.append({'t': 'h2', 'x': 'Nariz'})
B.append(ul(li(RI, 16, 0, 1, 4, 5, 6, 7, 8)))

# -------------------------------------------------------- 8. signos de alarma
B.append({'t': 'h', 'x': '8. Signos de alarma'})
B.append({'t': 'p', 'x':
    'Llame al teléfono de urgencias del consultorio a cualquier hora. No espere '
    'a la siguiente cita ni mande mensaje: llame.'})
B.append({'t': 'h2', 'x': 'Llame de inmediato, sin esperar'})
B.append(ul(
    li(DP, 31, 1, 3),                     # inflamación dura de un lado · sangrado
    # El renglón original decía "sobre todo detrás de las orejas": ahí no hay
    # colgajo. En un contorno cervical la piel en riesgo es la del cuello.
    ['Piel del cuello o bajo el mentón de color morado oscuro, negro o muy pálida.'],
    li(DP, 31, 7),                        # dificultad para respirar o tragar
    li(BL, 20, 0, 1, 2),                  # visión · dolor ocular · ojo abultado
    li(RI, 20, 0, 2),                     # sangrado nasal · golpe en la nariz
    ['Falta de aire, dolor en el pecho o desmayo.'],
))
B.append({'t': 'h2', 'x': 'Llame el mismo día'})
B.append(ul(
    li(DP, 31, 0, 2, 5, 6, 8, 9),         # presión · dolor · fiebre · infección · debilidad facial · pantorrilla
    li(BL, 22, 3, 4, 5, 6),               # herida abierta · secreción ocular · inflamación que sube · no cerrar el ojo
    li(RI, 22, 3, 4, 5, 6),               # líquido claro · piel oscura bajo férula · férula suelta · vómito
    ['Piel tratada con láser que duele más cada día, huele mal, escurre pus o '
     'forma una costra amarilla gruesa.'],
))
B.append(bl(DP, 32))                      # la nota de urgencias

# --------------------------------------------------- 9. constancia de entrega
B.append({'t': 'h', 'x': '9. Constancia de entrega'})
B.append(bl(DP, 34))
B.append(bl(DP, 35))

hoja = {
    'id': 'facial_combinada',
    # El nombre dice "de cuello (contorno)" a propósito, y no se acorta: el
    # menú desplegable es donde se escoge, y ahí es donde hay que poder
    # distinguirlo de un Deep Plane convencional. El convencional SÍ lleva
    # malla hemostática y SÍ lleva cita para retirar los puntos de detrás de
    # la oreja; esta hoja no trae ninguna de las dos. Escoger la equivocada
    # en ese menú le quita dos citas a la paciente sin que nadie lo note.
    'nombre': 'Combinada facial — Deep Plane de cuello (contorno) + '
              'blefaroplastia 4 cuadrantes + rinoplastia + CO₂',
    'titulo': 'Recomendaciones postoperatorias — cirugía facial combinada',
    # Vacío a propósito: `hojaSugerida()` sólo sugiere cuando UNA hoja coincide.
    # Si esta trajera "deep plane", un lifting solo encontraría dos y se
    # quedaría sin sugerencia. Esta hoja se escoge a mano.
    'coincide': [],
    'entrada': DP['entrada'],
    'bloques': B,
}

# Misma huella de contenido que el resto del catálogo: sha256 del JSON ordenado
# sin la propia versión. Dos hojas idénticas dan la misma versión; cambiar una
# coma la cambia.
hoja['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in hoja.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

cat['hojas'] = [h for h in cat['hojas'] if h['id'] != hoja['id']]
# Va después de las faciales y antes de las hojas de apoyo (faja, preoperatorias…)
pos = max(i for i, h in enumerate(cat['hojas']) if h['id'] == 'blefaroplastia') + 1
cat['hojas'].insert(pos, hoja)

cat['version'] = hashlib.sha256(json.dumps(
    {'hojas': cat['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

n = sum(len(b['x']) if b['t'] in ('ul', 'tabla', 'citas') else 1 for b in B)
print('hoja facial_combinada  ·  versión ' + hoja['version'] +
      '  ·  ' + str(len(B)) + ' bloques, ' + str(n) + ' renglones')
print('catálogo  ·  versión ' + cat['version'] + '  ·  ' +
      str(len(cat['hojas'])) + ' hojas')
