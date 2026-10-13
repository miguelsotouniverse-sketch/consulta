#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HOJA Y RECETA DEL LÁSER eCO₂, POR SEPARADO
===========================================

De dónde sale
-------------
El cuidado de la piel ya estaba escrito y aprobado dentro de la hoja combinada
facial: Cicaplast, Clobesol, vaselina, protector solar, no arrancar costras, no
ácidos, el maquillaje hasta el día 14 y qué es normal. Esos nueve renglones se
copian AQUÍ POR ÍNDICE desde esa hoja —no se vuelven a teclear— para que una
corrección futura no se quede a medias entre las dos.

Lo que NO estaba, porque allá lo ponía la cirugía
-------------------------------------------------
Una hoja suelta necesita cosas que en la combinada venían del Deep Plane: las
primeras 72 horas, el calendario de actividades, las citas y los signos de
alarma. Eso se redactó aquí, y va marcado con  # ←NUEVO  para que el médico lo
revise renglón por renglón. Nada de eso es copia de otra hoja.

La receta y lo que lleva
------------------------
Los cuatro productos que el médico indicó para el CO₂ —Cicaplast, Clobesol,
vaselina y protector solar— más la profilaxis antiviral, que él autorizó
después de que se la planteé: valaciclovir 500 mg cada 12 h × 10 días
empezando la víspera (confirmado 13-oct-2026). Los cinco renglones se copian
por nombre desde la receta combinada, no se teclean aquí.

Lo que esta hoja NO lleva, a propósito
--------------------------------------
No lleva faja facial. La faja es del Deep Plane, no del láser: un eCO₂ solo no
la requiere, y cuando el láser va junto con el Deep Plane la paciente recibe la
hoja combinada, que sí la trae (confirmado por el médico, 13-oct-2026). Si
alguna vez aparece un renglón de faja aquí, está mal copiado.

Uso:  python3 construir_eco2.py [indicaciones.json] [recetas.json]
"""

import json
import hashlib
import datetime
import sys

RUTA_IND = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'
RUTA_RX  = sys.argv[2] if len(sys.argv) > 2 else 'recetas.json'

CLOBESOL_DIAS = 7     # confirmado por el médico (13-oct-2026); el mismo tope que en la hoja combinada

# ============================================================ la hoja
cat = json.load(open(RUTA_IND, encoding='utf-8'))
H = {h['id']: h for h in cat['hojas']}
FC = H['facial_combinada']


def bloque_co2():
    """Los renglones del CO₂ tal como están aprobados en la hoja combinada."""
    for i, b in enumerate(FC['bloques']):
        if b['t'] == 'h2' and 'CO₂' in str(b.get('x', '')):
            return (json.loads(json.dumps(FC['bloques'][i + 1], ensure_ascii=False)),
                    json.loads(json.dumps(FC['bloques'][i + 2], ensure_ascii=False)))
    raise SystemExit('no encontré el apartado de CO₂ en la hoja combinada')


intro_co2, cuidados_co2 = bloque_co2()

B = []

B.append({'t': 'h2', 'x': 'Datos del procedimiento'})
B.append({'t': 'tabla', 'x': [['Procedimiento', 'Láser fraccionado de CO₂ (eCO₂)']]})

# ←NUEVO — la caja de arriba
B.append({'t': 'nota', 'x':
    'SI HOY SÓLO PUEDE LEER UNA COSA, LEA ESTO. '
    '1) La piel tratada NUNCA debe quedar seca: Cicaplast y vaselina encima, '
    'las veces que haga falta. '
    '2) No arranque costras ni piel que se desprende. '
    '3) Manos limpias cada vez que se toque la cara. '
    '4) Nada de sol hasta que la piel cierre; después, protector FPS 50 todos '
    'los días durante 12 meses. '
    '5) Es normal verse roja e hinchada los primeros días: eso no es una '
    'complicación, es el tratamiento.'})

B.append({'t': 'h', 'x': '1. Primeras 72 horas'})
B.append(intro_co2)                       # el párrafo aprobado: carne viva, 7–10 días
# ←NUEVO — todo este bloque
B.append({'t': 'ul', 'x': [
    'Inflamación: la cara se hincha más entre el día 2 y el 3, sobre todo al '
    'despertar. Duerma con la cabeza elevada (dos almohadas) la primera semana.',
    'Frío local: compresas frías sobre una gasa limpia y seca, 10 a 15 minutos '
    'cada hora mientras esté despierta. Nunca hielo directo sobre la piel '
    'tratada, y nunca una compresa que ya se usó.',
    'Ardor: es normal las primeras horas y cede solo. Si le arde de forma '
    'intensa y creciente, llámenos.',
    'No se exponga al viento, al polvo, al humo ni a la cocina caliente.',
    'Beba al menos 2 litros de agua al día: la piel tratada pierde mucha agua.',
]})

# ←NUEVO — el antiviral empieza ANTES del procedimiento, así que la paciente
# tiene que leerlo en algún lado que no sea sólo la receta.
B.append({'t': 'h', 'x': '2. Sus medicamentos'})
B.append({'t': 'ul', 'x': [
    'Tome los medicamentos de su receta en los horarios indicados, hasta '
    'terminarlos.',
    'El antiviral empieza el día ANTES del procedimiento y se toma completo, '
    'aunque la piel se vea bien: sirve para evitar que brote herpes sobre la '
    'piel tratada, que es la complicación más frecuente de este tratamiento. '
    'Si se le olvidó empezarlo, avísenos antes de venir.',
    'La crema con esteroide (Clobesol) se usa sólo los días indicados y se '
    'suspende. No la use por su cuenta más adelante.',
]})

B.append({'t': 'h', 'x': '3. Cuidado de la piel, todos los días'})
B.append({'t': 'p', 'x':
    'Esto es el tratamiento: la piel cierra bien o cierra mal según cómo se '
    'cuide estos diez días.'})
B.append(cuidados_co2)                    # los nueve renglones aprobados

# ←NUEVO — el lavado, adaptado del renglón unificado de la hoja combinada
B.append({'t': 'h2', 'x': 'Cómo lavarse la cara'})
B.append({'t': 'ul', 'x': [
    'Agua tibia y jabón neutro, con la mano limpia y sin tallar, 2 veces al día. '
    'Nada de esponjas, cepillos ni toallitas desmaquillantes.',
    'Seque a toques con una toalla limpia, nunca frotando y nunca con secadora.',
    'Vuelva a aplicar Cicaplast y vaselina enseguida, con la piel todavía húmeda.',
    'Toalla y funda de almohada limpias todos los días mientras la piel esté abierta.',
]})

# ←NUEVO — todo el calendario
B.append({'t': 'h', 'x': '4. Calendario de actividades'})
B.append({'t': 'p', 'x':
    'Lo que manda es el cierre de la piel: hasta que no haya cerrado por '
    'completo, nada de sudor, agua de alberca ni sol.'})
B.append({'t': 'tabla', 'cols': ['Actividad', 'A partir de', 'Nota'], 'x': [
    ['Salir de casa a la sombra', 'Día 1', 'Con gorra o sombrero de ala ancha'],
    ['Trabajo de oficina / home office', 'Día 3', 'La cara se ve roja e hinchada'],
    ['Vida social', 'Día 10–14', 'Cuando la piel haya cerrado'],
    ['Maquillaje sobre la piel tratada', 'Día 14', 'Sólo con la piel cerrada por completo'],
    ['Ejercicio ligero (caminata)', 'Día 7', 'Sin sudar'],
    ['Ejercicio completo, sudor', 'Semana 3', 'Con la piel cerrada'],
    ['Alberca, mar, vapor, sauna, jacuzzi', 'Semana 4', ''],
    ['Sol directo', 'Semana 6', 'Siempre con gorra y FPS 50; el sol antes de '
                                'tiempo mancha la piel tratada'],
    ['Ácidos, retinoides, exfoliantes, mascarillas', 'Semana 4', ''],
    ['Depilación con cera o láser en la zona tratada', 'Semana 6', 'Sólo con autorización'],
    ['Toxina botulínica, rellenos u otros tratamientos faciales', 'Mes 3',
     'Sólo con autorización'],
]})

# ←NUEVO — citas
B.append({'t': 'h', 'x': '5. Citas de seguimiento'})
B.append({'t': 'p', 'x':
    'Recepción agenda y confirma cada cita con usted por WhatsApp.'})
B.append({'t': 'citas', 'cols': ['Cita', 'Qué se hace', 'Fecha asignada'], 'x': [
    {'cita': 'Día 7 a 10', 'que': 'Revisión del cierre de la piel y alta de los '
                                  'cuidados intensivos'},
    {'cita': 'Mes 1', 'que': 'Revisión del color y la textura; fotografías'},
    {'cita': 'Mes 3', 'que': 'Revisión y fotografías; se decide si hay una '
                             'segunda sesión'},
    {'cita': 'Mes 6', 'que': 'Resultado y fotografías'},
]})

# ←NUEVO — qué es normal
B.append({'t': 'h', 'x': '6. Lo que es normal y no debe preocuparle'})
B.append({'t': 'ul', 'x': [
    'Ardor y sensación de quemadura de sol las primeras horas.',
    'Inflamación de la cara, mayor entre el día 2 y el 3, y más marcada al '
    'despertar. Baja en una semana.',
    'Piel roja intensa las primeras 2 semanas y rosada durante 2 a 3 meses.',
    'Costras finas y descamación entre el día 3 y el 10. Se caen solas.',
    'Comezón mientras la piel cierra.',
    'Piel tirante, áspera o con los poros marcados durante algunas semanas.',
    'Brotes de granitos o puntos blancos pequeños al cerrar la piel.',
    'El resultado final del colágeno se ve entre los 3 y los 6 meses.',
]})

# ←NUEVO — alarma
B.append({'t': 'h', 'x': '7. Signos de alarma: llame al teléfono de urgencias'})
B.append({'t': 'ul', 'x': [
    'Dolor que aumenta cada día en lugar de ceder.',
    'Ampollas pequeñas agrupadas, en racimo, con ardor o picor intenso, sobre '
    'todo alrededor de la boca: avísenos el mismo día.',
    'Zonas que se ponen amarillas, con costra gruesa, pus o mal olor.',
    'Enrojecimiento que se extiende fuera de la zona tratada, con calor.',
    'Fiebre de 38 °C o más.',
    'Una zona de piel que se pone blanca, gris u oscura.',
    'Sangrado que no cede con presión suave.',
]})
# El cierre que tenía esta hoja mandaba al paciente a urgencias del hospital
# más cercano si no lograba comunicarse. Eso está copiado del Deep Plane, donde
# sí tiene sentido —ahí el riesgo es la vía aérea y un hematoma que crece—.
# Después de un láser no hay nada que un servicio de urgencias vaya a resolver
# mejor, y sí hay mucho que se arruina si lo trata quien no sabe cómo quedó la
# piel. Aquí la instrucción es la contraria: insista hasta localizarnos.
B.append({'t': 'nota', 'alarma': True, 'x':
    'Llámenos a cualquier hora, de día o de noche. La piel tratada con láser la '
    'tiene que ver quien la trató: no se automedique ni acuda a otro consultorio '
    'sin avisarnos antes. Si no contestamos a la primera, insista y escriba '
    'también al WhatsApp del consultorio — le devolvemos la llamada.'})

B.append({'t': 'h', 'x': '8. Constancia de entrega'})
B.append({'t': 'p', 'x': 'Recibí esta hoja de indicaciones y mi receta.'})
B.append({'t': 'firmas', 'x': ['Paciente', 'Médico que entrega']})

hoja = {
    'id': 'eco2',
    'nombre': 'Láser eCO₂',
    'titulo': 'Recomendaciones posteriores al láser de CO₂',
    'coincide': ['eco2', 'e co2', 'co2', 'laser co2', 'laser de co2',
                 'resurfacing', 'rejuvenecimiento con laser'],
    'entrada': FC['entrada'],
    'bloques': B,
}
hoja['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in hoja.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

cat['hojas'] = [h for h in cat['hojas'] if h['id'] != 'eco2']
pos = max(i for i, h in enumerate(cat['hojas']) if h['id'] == 'facial_combinada') + 1
cat['hojas'].insert(pos, hoja)
cat['version'] = hashlib.sha256(json.dumps(
    {'hojas': cat['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()
with open(RUTA_IND, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

# ============================================================ la receta
rx = json.load(open(RUTA_RX, encoding='utf-8'))
P = {p['id']: p for p in rx['plantillas']}
COMB = P['facial_combinada']

# Los cuatro productos del CO₂, copiados por índice de la plantilla combinada.
# El antiviral se copia de la plantilla combinada como los demás: una sola
# definición, para que no se desincronicen si el médico corrige la dosis.
nombres_co2 = ['Valaciclovir', 'Clobetasol', 'Cicaplast', 'Vaselina',
               'Protector solar']
meds = []
for m in COMB['medicamentos']:
    if any(m['nombre'].startswith(n) for n in nombres_co2):
        c = json.loads(json.dumps(m, ensure_ascii=False))
        c.pop('si', None)
        meds.append(c)
if len(meds) != 5:
    raise SystemExit('esperaba 5 renglones del CO₂ y encontré ' + str(len(meds)))

plantilla = {
    'id': 'eco2',
    'nombre': 'Láser eCO₂',
    'coincide': [],
    'procedimiento': 'Láser fraccionado de CO₂ (eCO₂)',
    # Sólo lo que decide de verdad qué se receta aquí. Las preguntas de
    # penicilina y sulfas eran para los antibióticos y antiinflamatorios de la
    # cirugía; esta receta no lleva ninguno, así que preguntarlas sería pedirle
    # al médico que conteste algo que no cambia nada.
    'preguntas': [q for q in COMB['preguntas'] if q['id'] == 'otras'],
    'medicamentos': meds,
    'profilaxis': [],
    'profilaxisNota': '',
    'avisos': [
        {'si': {}, 'tono': 'ojo', 'texto':
         'Clobesol es un esteroide de potencia muy alta. Esta receta lo limita '
         'a ' + str(CLOBESOL_DIAS) + ' días sobre la piel tratada y lo prohíbe '
         'en los párpados. Si su protocolo es otro plazo, edite el renglón.'},
        {'si': {}, 'tono': 'ojo', 'texto':
         'El valaciclovir empieza el día ANTES del procedimiento: si la receta '
         'se entrega el mismo día, dígaselo en voz alta o entréguela antes.'},
        {'si': {}, 'tono': '', 'texto':
         'Esta receta no lleva antibiótico oral porque no se indicó. Si en este '
         'caso lo usa, agréguelo con el botón de abajo antes de imprimir.'},
    ],
    # Sin caja de signos de alarma en la receta: la hoja de indicaciones los
    # lleva completos y en esta receta sólo hay tópicos.
    'alarma': [],
    'horaNota': '',
}
plantilla['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in plantilla.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

rx['plantillas'] = [p for p in rx['plantillas'] if p['id'] != 'eco2']
pos = max(i for i, p in enumerate(rx['plantillas']) if p['id'] == 'facial_combinada') + 1
rx['plantillas'].insert(pos, plantilla)
rx['version'] = hashlib.sha256(json.dumps(
    {'plantillas': rx['plantillas'], 'hojas': rx['hojas'], 'horas': rx['horas']},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]
rx['generado'] = datetime.date.today().isoformat()
with open(RUTA_RX, 'w', encoding='utf-8') as f:
    json.dump(rx, f, ensure_ascii=False, indent=1)

print('hoja eco2       · versión ' + hoja['version'] + ' · ' +
      str(len(B)) + ' bloques')
print('plantilla eco2  · versión ' + plantilla['version'] + ' · ' +
      str(len(meds)) + ' renglones')
print('catálogo hojas  · ' + cat['version'] + ' · ' + str(len(cat['hojas'])) + ' hojas')
print('catálogo recetas· ' + rx['version'] + ' · ' + str(len(rx['plantillas'])) + ' plantillas')
