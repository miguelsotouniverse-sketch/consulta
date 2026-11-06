#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA HOJA DE MORPHEUS8 FACIAL
============================

Qué pidió
---------
El 6-nov-2026: «creo que no tenemos recomendaciones ni recetas de morpheus8
facial, me ayudas porfavor». Verificado: no existía nada. La palabra
«Morpheus», «microagujas» y «microneedling» no aparecían en ningún catálogo.

Lo que el médico confirmó ese día
---------------------------------
· **La anestesia varía** según la paciente: a veces tópica sola, a veces con
  sedación. Por eso la hoja pregunta antes de imprimir, igual que pregunta por
  el tubo.
· **No lleva profilaxis antiviral.** El eCO₂ sí —valaciclovir 10 días desde la
  víspera—, pero el Morpheus8 no abre la piel de la misma manera. El herpes se
  queda únicamente como signo de alarma.
· **Cicaplast, vaselina y protector solar FPS 50. Sin Clobesol.** El esteroide
  tópico del eCO₂ no entra aquí.
· **La serie varía**: no hay un número fijo de sesiones ni un intervalo fijo,
  así que la hoja NO inventa un calendario. El número de sesión y la fecha de
  la siguiente van en renglones en blanco, para escribirse a mano, igual que
  las fechas de las citas.

De dónde sale el texto
----------------------
De la hoja del eCO₂, que es la pariente más cercana: un procedimiento facial
por energía, sin incisiones y ambulatorio. Todo lo que ya estaba aprobado allá
se copia buscándolo por su texto —si allá cambia una palabra, este script se
detiene en vez de copiar otra cosa—. Lo nuevo es lo propio de la
radiofrecuencia con microagujas y va marcado con ←NUEVO.

LO QUE NO SE COPIÓ DEL eCO₂, Y POR QUÉ
---------------------------------------
El eCO₂ deja la piel «en carne viva» y su hoja está construida alrededor de
eso: no secarse ni un momento, costras que no se arrancan, diez días de cierre,
maquillaje hasta el día 14, sol hasta la semana 6. El Morpheus8 deja puntos de
punción en retícula y enrojecimiento, no una superficie abierta. Copiar esos
plazos habría sido escribirle a la paciente una recuperación que no es la suya
—y, peor, una que suena mucho más grave—, así que los plazos propios van
acortados y marcados ←CONFIRMAR uno por uno.

SOBRE LOS PLAZOS                                                  ←CONFIRMAR
-----------------
Ninguno de los plazos de la tabla de actividades me los dijo el médico. Los
puse en el rango habitual de la radiofrecuencia con microagujas y del lado
prudente. Los que más me importaría que revise son tres: sudor y ejercicio
(día 3), maquillaje (día 3) y activos —retinoides y ácidos— (semana 2). Ese
último lo dejé en 2 semanas y no en las 4 del eCO₂ porque aquí la barrera se
recupera mucho antes, pero es una decisión mía.

Uso:  python3 construir_hoja_morpheus8.py [indicaciones.json]
      (después de construir_receta_ribxcar.py y ANTES de
       agregar_molestia_garganta.py, que le pone la pregunta del tubo)
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'

cat = json.load(open(RUTA, encoding='utf-8'))
H = {h['id']: h for h in cat['hojas']}

if 'morpheus8' in H:
    raise SystemExit('la hoja de morpheus8 ya existe')
if 'eco2' not in H:
    raise SystemExit('falta la hoja del eCO₂, de donde se copia')

E = H['eco2']


def ren(fragmento):
    """Un renglón de lista de la hoja del eCO₂, buscado por su texto."""
    hallados = [x for b in E['bloques'] if b['t'] == 'ul'
                for x in b['x'] if fragmento in x]
    if len(hallados) != 1:
        raise SystemExit('en eco2 busqué «' + fragmento + '» y hallé ' +
                         str(len(hallados)) + ' renglones; esperaba 1')
    return hallados[0]


def parr(fragmento):
    hallados = [str(b['x']) for b in E['bloques']
                if b['t'] in ('p', 'nota') and fragmento in str(b.get('x', ''))]
    if len(hallados) != 1:
        raise SystemExit('en eco2 busqué el párrafo «' + fragmento +
                         '» y hallé ' + str(len(hallados)) + '; esperaba 1')
    return hallados[0]


# ---------------------------------------------------------------------------
# La pregunta que la hoja se hace a sí misma
# ---------------------------------------------------------------------------
# El médico lo dijo: la anestesia varía. Una paciente que fue con crema
# anestésica se va manejando sola, y una que fue sedada no puede. Imprimir
# «no maneje y venga acompañada» a la primera es ruido que le resta autoridad
# al resto de la hoja; no imprimírselo a la segunda es un problema de verdad.
PREGUNTA_SEDACION = {
    'id': 'sedacion',
    'etiqueta': 'Llevó sedación o anestesia general',
    'tipo': 'sino',
    'obligatoria': True,
    'enPie': True,
    'pieSi': 'con sedación',
    'pieNo': 'con anestesia tópica',
    'ayuda': ('Si fue sólo con crema anestésica, conteste que NO: la hoja deja '
              'fuera el acompañante y el no manejar. La pregunta del tubo, más '
              'abajo, es aparte y decide la sección de la garganta.'),
}

hoja = {
    'id': 'morpheus8',
    'nombre': 'Morpheus8 facial',
    'titulo': 'Recomendaciones posteriores al Morpheus8 facial',
    'coincide': ['morpheus8', 'morpheus 8', 'morpheus',
                 'radiofrecuencia con microagujas', 'microneedling con rf'],
    'preguntas': [dict(PREGUNTA_SEDACION)],
    'bloques': [

        {'t': 'h2', 'x': 'Datos del procedimiento'},
        # Los renglones en blanco se escriben a mano, igual que las fechas de
        # las citas: el médico dijo que la serie varía, y una hoja que imprime
        # «sesión 1 de 3» cuando no hay un 3 fijo compromete algo que no es
        # cierto.
        {'t': 'tabla', 'cols': ['Campo', 'Dato'], 'x': [
            ['Procedimiento',
             'Morpheus8® facial — radiofrecuencia fraccionada con microagujas'],
            ['Zonas tratadas', ''],
            ['Número de sesión', ''],
            ['Siguiente sesión', ''],
        ]},

        # ---------------- lo primero ----------------
        {'t': 'nota', 'x': (
            'SI HOY SÓLO PUEDE LEER UNA COSA, LEA ESTO. 1) La piel queda con '
            'una retícula de puntitos: no se la toque, no se la talle y no la '
            'cubra con maquillaje hoy. 2) Cicaplast y vaselina encima, para que '
            'no se sienta tirante. 3) Nada de sudor, calor ni sol hasta que los '
            'puntitos hayan desaparecido.')},

        {'t': 'h', 'x': '1. Primeras 48 horas'},
        # ←NUEVO: lo que de verdad va a ver y sentir, dicho de frente. La
        # paciente de Morpheus8 se asusta con la retícula si nadie se la
        # anunció.
        {'t': 'p', 'x': (
            'La radiofrecuencia entró por microagujas muy finas, así que la '
            'piel le queda con una retícula de puntitos rojos y con calor, '
            'como una quemadura de sol. Eso es lo esperado y no es una '
            'complicación. La retícula se desvanece en 2 a 4 días y la piel '
            'queda cerrada mucho antes que con un láser.')},
        {'t': 'ul', 'x': [
            # ←NUEVO
            'Manos limpias siempre que se toque la cara, y no se la toque sin '
            'necesidad las primeras 24 horas: los puntitos son canales abiertos '
            'hacia la dermis.',
            # ←NUEVO ←CONFIRMAR
            'Inflamación: la cara se hincha sobre todo al despertar del primer '
            'y el segundo día. Duerma con la cabeza elevada —dos almohadas— las '
            'dos primeras noches.',
            ren('Frío local: compresas frías sobre una gasa limpia'),
            ren('Ardor: es normal las primeras horas'),
            ren('No se exponga al viento, al polvo, al humo'),
            # ←NUEVO
            'Nada de calor sobre la cara las primeras 48 horas: ni vapor, ni '
            'secadora caliente, ni agua caliente en la regadera. El calor sobre '
            'una piel que acaba de recibir radiofrecuencia la inflama más.',
        ]},

        # ---------------- acompañante, sólo si hubo sedación ----------------
        {'t': 'h2', 'x': 'Porque llevó sedación', 'si': {'sedacion': True}},
        {'t': 'ul', 'si': {'sedacion': True}, 'x': [
            'Hoy no maneje, no tome decisiones importantes y no se quede sola: '
            'la sedación tarda el resto del día en salir de su cuerpo, aunque '
            'usted se sienta bien.',
            'Que alguien la acompañe de regreso a casa y se quede con usted '
            'las primeras horas.',
            'No tome alcohol hoy.',
        ]},

        # ---------------- medicamentos ----------------
        {'t': 'h', 'x': '2. Sus medicamentos'},
        {'t': 'ul', 'x': [
            ren('Tome los medicamentos de su receta en los horarios indicados'),
            # ←NUEVO: el contraste con el eCO₂ dicho a propósito, porque muchas
            # pacientes han oído de la otra hoja y preguntan por qué a ellas no
            # les tocó antiviral.
            'Esta hoja NO lleva antiviral ni crema con esteroide. El Morpheus8 '
            'no abre la piel como un láser de CO₂, y agregar medicamentos que '
            'no hacen falta sólo le quita atención a los que sí.',
        ]},

        # ---------------- cuidado de la piel ----------------
        {'t': 'h', 'x': '3. Cuidado de la piel'},
        {'t': 'p', 'x': (
            'Los primeros tres días la piel está permeable: lo que se ponga '
            'encima entra más que de costumbre. Por eso estos días sólo va lo '
            'que viene en su receta.')},
        {'t': 'ul', 'x': [
            ren('Cicaplast: aplique una capa sobre toda la zona tratada'),
            ren('Vaselina: aplíquela encima las veces que haga falta'),
            # ←NUEVO
            'No se ponga NADA más estos días: ni sueros, ni vitamina C, ni '
            'mascarillas, ni cremas «para después del láser» que no le hayamos '
            'dado nosotros.',
            ren('No arranque costras ni piel que se esté desprendiendo'),
            # El renglón del protector solar NO se copia del eCO₂. Allá dice
            # «en cuanto la piel esté completamente cerrada… durante 12 meses»:
            # los 12 meses son profilaxis de mancha después de un láser
            # ablativo, y «cuando cierre» describe una piel que aquí no se abre
            # así. Copiarlo le habría escrito a esta paciente un año de
            # instrucción que no le toca.                     ←NUEVO ←CONFIRMAR
            'Protector solar FPS 50+ de amplio espectro, todos los días desde '
            'mañana y reaplicado cada 3 horas si está al aire libre, durante '
            'las 4 semanas siguientes. Hoy, mejor sombra y gorra.',
            # ←NUEVO ←CONFIRMAR: el eCO₂ dice 4 semanas; aquí lo bajé a 2.
            'Nada de ácidos, retinoides, exfoliantes ni mascarillas durante 2 '
            'semanas.',
        ]},
        {'t': 'h2', 'x': 'Cómo lavarse la cara'},
        {'t': 'ul', 'x': [
            ren('Agua tibia y jabón neutro, con la mano limpia'),
            ren('Seque a toques con una toalla limpia'),
            ren('Vuelva a aplicar Cicaplast y vaselina enseguida'),
            # El del eCO₂ termina en «mientras la piel esté abierta». Aquí la
            # piel no queda abierta, así que esa condición nunca se cumpliría
            # y la paciente leería el renglón como que no le aplica.  ←NUEVO
            'Toalla y funda de almohada limpias los primeros tres días.',
        ]},

        # ---------------- actividades ----------------
        {'t': 'h', 'x': '4. Calendario de actividades'},
        # ←NUEVO ←CONFIRMAR
        {'t': 'p', 'x': (
            'Lo que manda son los puntitos: mientras se vean, la piel todavía '
            'no termina de cerrar, y el sudor, el agua de alberca y el sol son '
            'lo que puede mancharla o infectarla.')},
        {'t': 'tabla', 'cols': ['Actividad', 'A partir de', 'Nota'], 'x': [
            # ←CONFIRMAR todos estos plazos: son míos.
            ['Salir de casa', 'El mismo día',
             'Con gorra o sombrero y protector solar'],
            ['Trabajo de oficina / home office', 'Día 1',
             'La cara se ve roja; muchas pacientes prefieren esperar al día 3'],
            ['Maquillaje sobre la piel tratada', 'Día 3',
             'Con brocha limpia, y desmaquíllese sin tallar'],
            ['Ejercicio, sudor, vapor, sauna', 'Día 3',
             'El sudor sobre los puntitos irrita y puede infectar'],
            ['Alberca, mar, jacuzzi', 'Semana 2', ''],
            ['Ácidos, retinoides, exfoliantes', 'Semana 2', ''],
            ['Sol directo', 'Semana 4',
             'Siempre con gorra y FPS 50; el sol antes de tiempo mancha'],
            ['Depilación con cera o láser en la zona tratada', 'Semana 4',
             'Sólo con autorización'],
            ['Toxina botulínica o rellenos', 'Semana 2',
             'Sólo con autorización del Dr. Soto'],
        ]},

        # ---------------- citas ----------------
        {'t': 'h', 'x': '5. Citas y siguiente sesión'},
        {'t': 'p', 'x': parr('Recepción agenda y confirma cada cita')},
        # ←NUEVO: aquí NO va una tabla de citas con plazos fijos. El médico
        # dijo que la serie varía, y el número de sesión y la fecha de la
        # siguiente ya tienen su renglón en blanco en la ficha de arriba.
        {'t': 'p', 'x': (
            'El número de sesiones y el tiempo entre una y otra no son iguales '
            'para todas: dependen de su piel y de lo que vayamos viendo. En la '
            'ficha del principio de esta hoja está anotada su siguiente sesión. '
            'El resultado del colágeno no se juzga antes de los 3 meses, y por '
            'eso la revisión de fotografías se hace entonces.')},

        # ---------------- lo normal ----------------
        {'t': 'h', 'x': '6. Lo que es normal y no debe preocuparle'},
        {'t': 'ul', 'x': [
            # ←NUEVO
            'La retícula de puntitos rojos, que se desvanece en 2 a 4 días.',
            ren('Ardor y sensación de quemadura de sol las primeras horas'),
            # ←NUEVO ←CONFIRMAR
            'Inflamación de la cara el primer y el segundo día, más marcada al '
            'despertar. Puede verse algo «llenita»; baja sola.',
            # ←NUEVO
            'Piel áspera, como lija fina, y descamación discreta entre el día 2 '
            'y el 5.',
            ren('Comezón mientras la piel cierra'),
            ren('Brotes de granitos o puntos blancos pequeños'),
            # ←NUEVO ←CONFIRMAR
            'Sentir la piel más firme a las pocas semanas y seguir viendo '
            'cambios hasta el tercer mes: el colágeno nuevo tarda en formarse.',
        ]},

        # ---------------- alarma ----------------
        {'t': 'h', 'x': '7. Signos de alarma: llame al teléfono de urgencias',
         'alarma': True},
        {'t': 'ul', 'x': [
            ren('Dolor que aumenta cada día en lugar de ceder'),
            # ←NUEVO: la complicación propia de la radiofrecuencia. No es la
            # mancha ni la infección: es la quemadura en un punto donde entró
            # más energía de la cuenta, y se distingue porque es UNA zona y no
            # el patrón parejo de toda la cara.
            'Una ampolla, una costra gruesa o una zona hundida en UN punto '
            'aislado, distinta del resto de la cara.',
            ren('Ampollas pequeñas agrupadas, en racimo'),
            ren('Zonas que se ponen amarillas, con costra gruesa'),
            ren('Enrojecimiento que se extiende fuera de la zona tratada'),
            ren('Fiebre de 38 °C o más'),
            ren('Una zona de piel que se pone blanca, gris u oscura'),
        ]},
        # El párrafo del eCO₂ dice «la piel tratada con láser»; aquí no hubo
        # láser. Se reescribe la frase, no la idea.
        {'t': 'nota', 'alarma': True, 'x': (
            'Llámenos a cualquier hora, de día o de noche. La piel tratada la '
            'tiene que ver quien la trató: no se automedique ni acuda a otro '
            'consultorio sin avisarnos.')},

        # ---------------- cierre ----------------
        {'t': 'h', 'x': '8. Constancia de entrega'},
        {'t': 'p', 'x': parr('Recibí esta hoja de indicaciones y mi receta')},
        {'t': 'firmas', 'x': ['Paciente', 'Médico que entrega']},
    ],
}

# La hoja nueva va junto al eCO₂, que es su familia.
i = [k for k, h in enumerate(cat['hojas']) if h['id'] == 'eco2'][0]
cat['hojas'].insert(i + 1, hoja)


# ---------------------------------------------------------------------------
# Redes de seguridad
# ---------------------------------------------------------------------------
def plano(t):
    import unicodedata
    t = unicodedata.normalize('NFD', str(t).lower())
    return ''.join(c for c in t if unicodedata.category(c) != 'Mn').strip()


# Igual que `hojaSugerida()`: debe coincidir EXACTAMENTE una.
for proc in ('Morpheus8', 'Morpheus 8 facial', 'morpheus8'):
    p = plano(proc)
    halladas = [h['id'] for h in cat['hojas']
                if any(p.find(plano(c)) >= 0 for c in h.get('coincide', []))]
    if halladas != ['morpheus8']:
        raise SystemExit('«' + proc + '» coincide con ' + str(halladas) +
                         ' y esperaba sólo con morpheus8')

todo = json.dumps(hoja, ensure_ascii=False)
# Nada de lo que este procedimiento NO lleva. El riesgo real aquí es que se
# cuele algo del eCO₂ al copiar: son hojas parecidas y los renglones se buscan
# por fragmento.
#
# La lista es de FRASES, no de palabras sueltas. Un primer intento prohibía
# «láser» a secas y reventó contra dos frases mías que nombran el láser a
# propósito, para contrastar. Pero el aviso sirvió: al revisar salió que el
# renglón del protector solar que estaba copiando traía los 12 meses del láser
# ablativo. La red tiene que apuntar a lo que sería un error, no a un tema.
for sobra in ('valaciclovir', 'Valaciclovir', 'Clobesol', 'clobetasol',
              'en carne viva', 'durante 12 meses', 'hasta el día 14',
              'piel tratada con láser', 'mientras la piel esté abierta'):
    if sobra in todo:
        raise SystemExit('se coló «' + sobra + '» del eCO₂ en la hoja de '
                         'morpheus8, que no lo lleva')
# Y sí lo que sí.
for falta in ('retícula', 'Cicaplast', 'Vaselina', 'FPS 50',
              'UN punto aislado', 'sedación'):
    if falta not in todo:
        raise SystemExit('falta «' + falta + '» en la hoja de morpheus8')
# El bloque de la sedación tiene que estar condicionado, o se le imprime a
# toda paciente que vino con crema anestésica.
cond = [b for b in hoja['bloques'] if (b.get('si') or {}).get('sedacion')]
if len(cond) != 2:
    raise SystemExit('esperaba 2 bloques condicionados a la sedación y hay ' +
                     str(len(cond)))

hoja['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in hoja.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

cat['version'] = hashlib.sha256(json.dumps(
    {'hojas': cat['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

n = sum(len(b['x']) if isinstance(b['x'], list) else 1 for b in hoja['bloques'])
print('hoja       morpheus8          nueva -> %s  (%d bloques, %d renglones)'
      % (hoja['version'], len(hoja['bloques']), n))
print('catálogo   ' + cat['version'])
