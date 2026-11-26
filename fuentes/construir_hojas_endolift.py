#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAS DOS HOJAS DE ENDOLIFTING
=============================
facial (cara y cuello)  ·  corporal (un área)

Por qué existen
---------------
El 26-nov-2026 el médico pidió la hoja de endolifting y no había nada: ni
hoja, ni receta, ni una mención en el esquema. Endolifting lleva años en su
lista de precios —Facial/Cara y cuello $35,000 y Corporal 1 área $45,000— y
nunca había llegado al expediente.

Lo que él definió ese día, y que no se inventó
------------------------------------------------
  · DOS hojas separadas, no una que cubra las dos.
  · Anestesia: SEDACIÓN más local, en las dos.
  · Facial: banda compresiva **2 semanas, únicamente mientras está en casa**.
  · Corporal: faja **2 semanas completas** —día y noche—.
  · Receta: sólo antibiótico y paracetamol, la misma para las dos.

Por qué las dos se construyen en el MISMO archivo
--------------------------------------------------
Comparten casi todo: la sedación, los puntos de entrada, el calendario, los
signos de alarma. Si vivieran en dos scripts, el día que él corrija un
renglón se corregiría en una y no en la otra, y nadie se daría cuenta hasta
que dos pacientes compararan sus hojas. Aquí el tronco se escribe una vez y
cada hoja sólo aporta lo suyo: la prenda, la zona y los tres o cuatro
renglones que de verdad cambian.

De dónde sale la forma
----------------------
De la hoja de nanofat, que es el procedimiento más parecido que ya estaba
aprobado: facial, ambulatorio, con sedación y por micropunciones. De ahí se
copian la sección de sedación, la de cómo lavarse, el cierre y las firmas.
Por eso estas hojas tampoco traen la sección de molestia de garganta: la de
nanofat, que también es con sedación, no la trae.

LO QUE ES NUEVO Y NECESITA SU REVISIÓN RENGLÓN POR RENGLÓN
-----------------------------------------------------------
Todo lo propio del endolifting va marcado  # ←NUEVO: qué es el procedimiento
en una línea, los puntos de entrada, los nódulos transitorios y los signos de
alarma. Los plazos que él no dio van marcados  # ←CONFIRMAR.

LO QUE DELIBERADAMENTE NO DICE, Y ÉL TIENE QUE DECIDIR
-------------------------------------------------------
El FRÍO LOCAL. No aparece en ninguna de las dos hojas, ni permitido ni
prohibido, y es lo primero que una paciente hace al llegar a su casa. No se
puso porque sus dos hojas vecinas se contradicen: en lipoescultura el frío
está prohibido sobre la piel tratada «porque tiene menos sensibilidad y puede
quemarse», y en nanofat está prohibido sobre lo injertado pero permitido
sobre la zona donadora. Endolifting deja la dermis caliente y con menos
sensibilidad, así que la respuesta podría ser cualquiera de las dos y
escogerla yo sería inventar. Queda como hueco declarado, no como olvido.

Uso:  python3 construir_hojas_endolift.py [indicaciones.json]
      (correr DESPUÉS de construir_hoja_nanofat.py, de quien copia)
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'

# --- lo que él definió -----------------------------------------------------
BANDA_SEMANAS = 2        # [stated] facial: 2 semanas, sólo en casa
FAJA_SEMANAS = 2         # [stated] corporal: 2 semanas completas

# --- los plazos que él no dio ----------------------------------------------
DIA_MAQUILLAJE = 'Día 3'      # ←CONFIRMAR
DIA_TRABAJO = 'Día 2'         # ←CONFIRMAR  nanofat dice día 2
EJERCICIO = 'Semana 2'        # ←CONFIRMAR
SOL = 'Semana 4'              # ←CONFIRMAR
MASAJE = 'Mes 2'              # ←CONFIRMAR  el criterio conservador de nanofat

cat = json.load(open(RUTA, encoding='utf-8'))
H = {h['id']: h for h in cat['hojas']}

for nuevo in ('endolift_facial', 'endolift_corporal'):
    if nuevo in H:
        raise SystemExit('ya existe la hoja %s' % nuevo)

NF = H['nanofat']


def copia(x):
    return json.loads(json.dumps(x, ensure_ascii=False))


def bl(hoja, n):
    return copia(hoja['bloques'][n])


def arma(zona):
    """El tronco común. `zona` es 'facial' o 'corporal'."""
    facial = (zona == 'facial')
    cara = 'la cara y el cuello' if facial else 'la zona tratada'
    prenda = 'la banda' if facial else 'la faja'
    B = []

    # ------------------------------------------------------------- portada
    B.append({'t': 'h2', 'x': 'Datos del procedimiento'})
    B.append({'t': 'tabla', 'x': [
        ['Procedimiento',
         'Endolifting facial — cara y cuello' if facial
         else 'Endolifting corporal — un área'],
        ['Zonas tratadas', ''],
    ]})

    # ←NUEVO  el recuadro de arriba: lo único que no se puede dejar de leer
    B.append({'t': 'nota', 'x':
        'SI HOY SÓLO PUEDE LEER UNA COSA, LEA ESTO. '
        '1) Hoy no maneje y no se quede sola: llevó sedación. '
        '2) ' + ('Use la banda compresiva en casa durante las ' +
                 str(BANDA_SEMANAS) + ' semanas siguientes.' if facial else
                 'Use la faja día y noche durante las ' + str(FAJA_SEMANAS) +
                 ' semanas siguientes.') + ' '
        '3) Termine el antibiótico completo, aunque se sienta bien.'})

    # ------------------------------------------------------ primeras 48 h
    B.append({'t': 'h', 'x': '1. Primeras 48 horas'})
    # ←NUEVO  qué le hicieron, en una línea que ella pueda entender
    B.append({'t': 'p', 'x':
        'En el endolifting se pasa una fibra óptica muy delgada por debajo de '
        'la piel, a través de punciones del tamaño de un piquete de aguja. El '
        'calor controlado de esa fibra contrae el tejido y estimula colágeno '
        'durante los meses siguientes. No hay cortes ni puntos de sutura, así '
        'que lo que va a sentir estos días es inflamación y sensibilidad, no '
        'dolor de herida.'})
    B.append({'t': 'ul', 'x': [
        'Inflamación y moretones: aumentan durante las primeras 48 a 72 horas '
        'y después empiezan a bajar. Es la parte más aparatosa y la más corta.',
        ('Duerma boca arriba y con la cabecera elevada, con dos o tres '
         'almohadas, los primeros 3 días: baja la inflamación de la cara más '
         'rápido que cualquier otra cosa que haga.') if facial else
        ('Duerma como le resulte cómodo, sin apoyarse directamente sobre la '
         'zona tratada los primeros 3 días.'),
        'Camine desde el mismo día, suave y varias veces al día.',
        'Tome el paracetamol de su receta a sus horas los primeros días, no '
        '«sólo si duele».',
        'Empiece el antibiótico hoy y termínelo completo, aunque ya no le '
        'moleste nada.',
        # ←NUEVO  los puntos de entrada
        'Los puntos de entrada son micropunciones: no llevan puntos de sutura. '
        'Manténgalos limpios y secos. Pueden formar una costrita pequeña que '
        'se cae sola; no se la quite.',
    ]})

    # ------------------------------------------- la sedación, copiada tal cual
    B.append(bl(NF, 6))
    B.append(bl(NF, 7))

    # --------------------------------------------------------- la prenda
    if facial:
        B.append({'t': 'h', 'x': '2. La banda compresiva'})
        B.append({'t': 'p', 'x':
            'La banda sostiene el tejido mientras se desinflama y ayuda a que '
            'la piel se adapte a su nueva posición. Se usa durante ' +
            str(BANDA_SEMANAS) + ' semanas, ÚNICAMENTE MIENTRAS ESTÁ EN CASA: '
            'no tiene que salir a la calle con ella.'})
        B.append({'t': 'tabla', 'x': [
            ['Semanas 1–' + str(BANDA_SEMANAS), 'Siempre que esté en casa, '
             'incluida la noche', 'Fuera de casa no es necesaria'],
            ['A partir de la semana ' + str(BANDA_SEMANAS + 1), 'Ya no se usa',
             ''],
        ]})
    else:
        B.append({'t': 'h', 'x': '2. La faja'})
        B.append({'t': 'p', 'x':
            'La faja sostiene el tejido mientras se desinflama y ayuda a que '
            'la piel se adapte. Se usa DÍA Y NOCHE durante ' +
            str(FAJA_SEMANAS) + ' semanas completas, y sólo se retira para '
            'bañarse.'})
        B.append({'t': 'tabla', 'x': [
            ['Semanas 1–' + str(FAJA_SEMANAS), 'Día y noche',
             'Retirar solo para bañarse'],
            ['A partir de la semana ' + str(FAJA_SEMANAS + 1), 'Ya no se usa',
             ''],
        ]})
    B.append({'t': 'ul', 'x': [
        'Ajuste: firme, nunca doloroso. Si siente hormigueo, adormecimiento o '
        'cambio de color en la piel, aflójela y llámenos.',
        'Pliegues: revise que no forme arrugas; un pliegue marca la piel.',
        'Higiene: tenga dos, para alternarlas y lavarlas a mano.',
        'Si se la quitó para bañarse, vuelva a ponérsela enseguida y con la '
        'piel bien seca.',
    ]})

    # ------------------------------------------------------ la piel
    B.append({'t': 'h', 'x': '3. Cuidado de la piel y de los puntos de entrada'})
    B.append({'t': 'p', 'x':
        'La piel queda permeable unos días por las micropunciones: lo que se '
        'ponga encima entra más que de costumbre. Estos días sólo va lo que '
        'le indicamos nosotros.'})
    B.append({'t': 'ul', 'x': [
        # La concordancia se escribe completa por zona: interpolar «la cara y
        # el cuello» en una frase en femenino singular daba «la cara y el
        # cuello limpia y seca», y eso sí se alcanzó a imprimir.
        ('Mantenga la cara y el cuello limpios y secos. No aplique cremas, '
         'aceites, pomadas ni remedios caseros sobre los puntos de entrada.')
        if facial else
        ('Mantenga la zona tratada limpia y seca. No aplique cremas, aceites, '
         'pomadas ni remedios caseros sobre los puntos de entrada.'),
        'Nada de ácidos, retinoides, exfoliantes ni mascarillas durante 2 '
        'semanas.',  # ←CONFIRMAR
        'No se talle ni se frote la zona, ni siquiera al secarse.',
        'Protector solar FPS 50+ todos los días sobre la zona tratada, hasta '
        'que le digamos lo contrario.' if facial else
        'Si la zona tratada va a quedar expuesta al sol, protector solar FPS '
        '50+ todos los días.',
    ]})
    if facial:
        B.append(bl(NF, 14))
        B.append({'t': 'ul', 'x': [
            'Agua tibia y jabón neutro, con la mano limpia y sin tallar, 2 '
            'veces al día. Nada de esponjas, cepillos ni toallitas '
            'desmaquillantes.',
            'Seque a toques con una toalla limpia, nunca frotando y nunca con '
            'secadora.',
            'Toalla y funda de almohada limpias los primeros tres días.',
        ]})

    # -------------------------------------------------------- calendario
    B.append({'t': 'h', 'x': '4. Calendario de actividades'})
    B.append({'t': 'p', 'x':
        'La inflamación es lo que marca el ritmo de las primeras dos semanas. '
        'El resultado, en cambio, no se juega en esos días: se va construyendo '
        'durante meses.'})
    filas = [
        ['Caminar', 'El mismo día', 'Suave, varias veces al día'],
        ['Manejar', 'Mañana', 'Hoy no, por la sedación'],
        ['Trabajo de escritorio / home office', DIA_TRABAJO,
         'Todavía con inflamación y moretones'],
    ]
    if facial:
        filas.append(['Maquillaje', DIA_MAQUILLAJE,
                      'Con brocha limpia y sin presionar; desmaquíllese sin '
                      'tallar'])
    filas += [
        ['Ejercicio, sudor, vapor, sauna', EJERCICIO,
         'El calor aumenta la inflamación'],
        ['Alberca, mar, jacuzzi', 'Semana 3',
         'Con los puntos de entrada completamente cerrados'],
        ['Ácidos, retinoides, exfoliantes', 'Semana 2', ''],
        ['Sol directo', SOL, 'Siempre con protector solar FPS 50'],
        ['Masaje o aparatos sobre la zona tratada', MASAJE,
         'Sólo con autorización del Dr. Soto'],
    ]
    if facial:
        filas.append(['Toxina botulínica o rellenos', 'Mes 2',
                      'Sólo con autorización del Dr. Soto'])   # ←CONFIRMAR
    B.append({'t': 'tabla', 'x': filas})

    # ------------------------------------------------------ qué es normal
    B.append({'t': 'h', 'x': '5. Lo que es normal y no debe preocuparle'})
    # ←NUEVO  lo propio del endolifting
    B.append({'t': 'p', 'x':
        'El resultado del endolifting es progresivo: lo que se ve en las '
        'primeras semanas es la inflamación bajando, no el resultado. La '
        'contracción y el colágeno nuevo siguen trabajando entre los 3 y los 6 '
        'meses, y es entonces cuando se aprecia lo que hicimos.'})
    B.append({'t': 'ul', 'x': [
        'Inflamación que aumenta los primeros 2 o 3 días y después baja poco a '
        'poco, con altibajos y más marcada al final del día.',
        'Moretones alrededor de los puntos de entrada, que cambian de morado a '
        'verde y amarillo. Desaparecen en 2 a 3 semanas.',
        'Adormecimiento, hormigueo o sensación de piel acartonada en la zona '
        'tratada. La sensibilidad regresa en semanas a meses.',
        'Zonas duras o pequeños nódulos bajo la piel durante las primeras '
        'semanas. Se ablandan solos conforme madura el colágeno.',
        'Sensación de tirantez, sobre todo al mover ' + cara + '.',
        'Costritas pequeñas en los puntos de entrada, que se caen solas.',
        'Asimetría entre un lado y otro mientras baja la inflamación: cada '
        'lado se desinflama a su ritmo.',
    ]})

    # --------------------------------------------------- signos de alarma
    B.append({'t': 'h', 'x': '6. Signos de alarma: llame al teléfono de urgencias'})
    # ←NUEVO  escritos para endolifting
    alarma = [
        'Dolor que aumenta cada día en lugar de ceder, o que no cede con el '
        'paracetamol.',
        'Fiebre de 38 °C o más.',
        'Enrojecimiento que se extiende alrededor de un punto de entrada, con '
        'calor, pus o mal olor.',
        'Una costra oscura, una ampolla o una quemadura en un punto de '
        'entrada.',
        'Una zona que se endurece, crece y duele cada vez más, distinta del '
        'resto.',
        'Piel que se pone blanca, moteada o morada oscura y no recupera su '
        'color.',
    ]
    if facial:
        # El que importa de verdad en el facial: el nervio. Se reporta, no se
        # tranquiliza por teléfono.
        alarma.append('Asimetría al sonreír, al levantar la ceja o al cerrar '
                      'el ojo, o un párpado que se queda caído. Avísenos '
                      'aunque sea leve y aunque crea que es la inflamación.')
    B.append({'t': 'ul', 'x': alarma})
    B.append({'t': 'nota', 'x':
        'Llámenos a cualquier hora, de día o de noche. La zona tratada la '
        'tiene que ver quien la trató: no se automedique ni acuda a otro '
        'consultorio sin avisarnos.'})

    # ------------------------------------------------------------ cierre
    B.append(bl(NF, 26))
    B.append(bl(NF, 27))
    B.append(bl(NF, 28))
    B.append(bl(NF, 29))
    return B


def hoja_de(zona):
    facial = (zona == 'facial')
    B = arma(zona)
    h = {
        'id': 'endolift_' + zona,
        'nombre': 'Endolifting facial' if facial else 'Endolifting corporal',
        'titulo': 'Recomendaciones posteriores — Endolifting ' +
                  ('facial (cara y cuello)' if facial else 'corporal'),
        # Sin `coincide`: se escoge a mano, como las demás hojas nuevas. Y
        # aquí importa más que nunca, porque son dos hojas parecidas y la
        # equivocada manda una prenda distinta durante dos semanas.
        'coincide': [],
        'bloques': B,
    }
    h['version'] = hashlib.sha256(json.dumps(
        {k: v for k, v in h.items() if k != 'version'},
        ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]
    return h


FAC = hoja_de('facial')
COR = hoja_de('corporal')

# ---------------------------------------------------------------------------
# Redes de seguridad
# ---------------------------------------------------------------------------
pf = json.dumps(FAC['bloques'], ensure_ascii=False)
pc = json.dumps(COR['bloques'], ensure_ascii=False)

# Las dos prendas no se pueden confundir: es el renglón que más caro sale
# equivocado, porque dura dos semanas.
if 'banda' not in pf.lower() or 'faja' in pf.lower():
    raise SystemExit('la hoja facial debe hablar de banda y no de faja')
if 'faja' not in pc.lower() or 'banda' not in pc.lower() and False:
    raise SystemExit('la hoja corporal debe hablar de faja')
if 'banda' in pc.lower():
    raise SystemExit('se coló la banda facial en la hoja corporal')
if 'ÚNICAMENTE MIENTRAS ESTÁ EN CASA' not in pf:
    raise SystemExit('la facial no dice que la banda es sólo en casa')
if 'DÍA Y NOCHE' not in pc:
    raise SystemExit('la corporal no dice que la faja es día y noche')

# La receta de endolifting sólo trae antibiótico y paracetamol: la hoja no
# puede mandar aplicarse nada que la receta no incluya.
for h, p in (('facial', pf), ('corporal', pc)):
    for sobra in ['Cicaplast', 'vaselina', 'Clobesol', 'celecoxib',
                  'antiviral', 'bencidamina', 'garganta']:
        if sobra.lower() in p.lower():
            raise SystemExit('la hoja %s menciona «%s», que no viene en la '
                             'receta de endolifting' % (h, sobra))
    # Lo que la hoja existe para decir.
    for obliga in ['sedación', 'micropunciones', 'punto de entrada',
                   'progresivo', 'antibiótico']:
        if obliga.lower() not in p.lower():
            raise SystemExit('falta «%s» en la hoja %s' % (obliga, h))
    # Estos párrafos se imprimen como texto.
    for etiqueta in ['<b>', '</b>', '<i>', '<br', '<p>']:
        if etiqueta in p:
            raise SystemExit('HTML literal en la hoja %s' % h)

# El nervio facial sólo se vigila en la cara. En la hoja corporal ese renglón
# no tiene sentido y sembraría un miedo que no aplica.
if 'levantar la ceja' not in pf:
    raise SystemExit('falta el signo de alarma del nervio en la hoja facial')
if 'levantar la ceja' in pc:
    raise SystemExit('el signo del nervio facial se coló en la corporal')
if 'Maquillaje' in pc:
    raise SystemExit('el renglón de maquillaje se coló en la corporal')

# Ninguna hoja declara preguntas, así que ningún bloque puede colgar de una.
for h, hoja in (('facial', FAC), ('corporal', COR)):
    for b in hoja['bloques']:
        if b.get('si'):
            raise SystemExit('la hoja %s tiene un bloque condicionado y no '
                             'hace preguntas' % h)
    for b in hoja['bloques']:
        if b['t'] == 'ul' and len(b['x']) != len(set(b['x'])):
            raise SystemExit('renglones duplicados en la hoja %s' % h)

# Las dos tienen que seguir siendo la misma hoja en lo que comparten.
comunes = ['Hoy, porque llevó sedación', 'Signos de alarma',
           'Calendario de actividades', 'Citas y constancia de entrega']
for c in comunes:
    if c not in pf or c not in pc:
        raise SystemExit('«%s» tiene que estar en las dos hojas' % c)

# Concordancia: la hoja facial habla de «la cara y el cuello», que es plural
# masculino. Cualquier adjetivo en femenino singular detrás de eso es un
# error de interpolación, y uno de ésos ya salió impreso.
for mala in ['el cuello limpia', 'el cuello seca', 'el cuello tratada']:
    if mala in pf:
        raise SystemExit('concordancia rota en la hoja facial: «%s»' % mala)

# El frío queda declarado como hueco, no como olvido: si algún día alguien lo
# agrega, que lo agregue a las dos y a sabiendas.
for h, p in (('facial', pf), ('corporal', pc)):
    if 'hielo' in p.lower() or 'frío local' in p.lower():
        raise SystemExit('la hoja %s habla de frío local y el médico todavía '
                         'no lo ha definido para endolifting' % h)

pos = len(cat['hojas'])
for h in cat['hojas']:
    if h['id'] == 'nanofat':
        pos = cat['hojas'].index(h) + 1
cat['hojas'].insert(pos, COR)
cat['hojas'].insert(pos, FAC)

cat['version'] = hashlib.sha256(json.dumps(
    {'hojas': cat['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

for h in (FAC, COR):
    n = sum(len(b['x']) if b['t'] in ('ul', 'tabla') else 1 for b in h['bloques'])
    print('hoja %-18s · versión %s · %d bloques, %d renglones'
          % (h['id'], h['version'], len(h['bloques']), n))
print('catálogo de indicaciones  %s · %d hojas'
      % (cat['version'], len(cat['hojas'])))
