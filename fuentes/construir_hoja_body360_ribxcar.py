#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA HOJA DE ALTA DE BODY360 5D
==============================
lipoescultura + RibXcar (remodelación costal)

Por qué existe
--------------
El 25-nov-2026 el médico preguntó si había indicaciones de alta para una
paciente de Body360 + RibXcar. Las había sólo de nombre: la paciente se
llevaba la hoja de lipoescultura, que cubre 4D y 5D, y todo el corset se
despachaba en UN renglón metido en la lista de la faja.

Lo que a esa paciente le faltaba, comparado con la hoja de RibXcar sola:

  · que el corset sigue hasta el MES 6 — el renglón terminaba en la semana 8,
    así que quien sólo leyera esa hoja entendía que ahí se acababa;
  · que no se aprieta más rápido de un broche por semana, y por qué;
  · la camiseta de algodón debajo, los dos corsets para alternar, volver a
    ponérselo enseguida después de bañarse;
  · el signo de alarma propio del corset —que de pronto apriete mucho más o
    ya no cierre en el broche en el que iba—;
  · y todo lo de la caja torácica, que es lo que de verdad la limita los
    primeros días: respirar hondo cada hora, abrazar una almohada para toser,
    no estirar los brazos por encima de la cabeza dos semanas.

Lo que él definió el 26-nov-2026, y que no se inventó
------------------------------------------------------
  · El corset empieza el DÍA 3. «Cuando hay combinación de lipo con ribxcar,
    el corset se inicia en día 3 en lugar de día 1.» (El día 1 es el de la
    RibXcar sola.) La hoja de lipoescultura decía día 4 y quedó corregida en
    `corregir_dia_corset_5d.py`.
  · Sí aplica el MES 6, igual que en la RibXcar sola.
  · El corset va POR ENCIMA de la faja.
  · La faja conserva su esquema de siempre: 6 semanas día y noche y luego
    6 semanas 12 horas. El corset no le cambia nada.

De dónde sale el resto
----------------------
Se fusionan las dos hojas que ya existen, copiando bloques por índice. La
base es la de lipoescultura, porque la lipo es la que manda: es la que tiene
incisiones, faja y anticoagulante. De la de RibXcar se trae lo del tórax y
el corset. Donde las dos dicen lo mismo se copia una vez; donde los plazos
difieren, manda el más lento de los dos — y los dos valores ya estaban
aprobados, así que aquí no hay ningún plazo inventado.

EL CHOQUE QUE HUBO QUE RESOLVER
-------------------------------
Las dos hojas mandan levantarse distinto:

    lipoescultura: «Levantarse despacio: primero siéntese en la orilla de la
                    cama 1–2 minutos»
    RibXcar:       «sin empujarse con los brazos: ruede de lado y use las
                    piernas»

No se contradicen, pero la de lipo se queda corta: empujarse con los brazos
es justo lo que tira de las costillas recién remodeladas. Se conserva la de
RibXcar, que es la que incluye las dos cosas.

Y el baño: la hoja de RibXcar permite regadera a las 24 horas porque no hay
heridas, sólo punciones. Aquí sí las hay, las de la lipo, así que manda el
plazo de la lipo — 48 horas. El más conservador de los dos, y por una razón,
no por precaución genérica.

LA RECETA NO CAMBIA
-------------------
Se cotejaron las dos plantillas: la de RibXcar es subconjunto estricto de la
de Body360 —le faltan amlodipino, metoprolol, captopril, clonazepam y
rivaroxabán—. O sea que la paciente de 5D se lleva la receta de Body360 tal
cual, y no hubo que crear ninguna plantilla nueva.

Uso:  python3 construir_hoja_body360_ribxcar.py [indicaciones.json]
      (correr DESPUÉS de corregir_dia_corset_5d.py)
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'

DIA_CORSET = 3          # [stated] 26-nov-2026

cat = json.load(open(RUTA, encoding='utf-8'))
H = {h['id']: h for h in cat['hojas']}

if 'body360_ribxcar' in H:
    raise SystemExit('ya existe la hoja de Body360 5D')

LIPO = H['lipoescultura']
RIB = H['ribxcar']


def copia(x):
    return json.loads(json.dumps(x, ensure_ascii=False))


def bl(hoja, n):
    """Un bloque aprobado, copiado por índice. Nunca se vuelve a teclear."""
    return copia(hoja['bloques'][n])


def pts(hoja, n, quitar=()):
    xs = copia(hoja['bloques'][n])['x']
    for q in quitar:
        antes = len(xs)
        xs = [x for x in xs if q.lower() not in x.lower()]
        if len(xs) == antes:
            raise SystemExit('no encontré el renglón a quitar: «%s»' % q)
    return xs


def punto(hoja, n, empieza):
    """Un renglón concreto de una lista aprobada, buscado por su principio."""
    hits = [x for x in hoja['bloques'][n]['x'] if x.startswith(empieza)]
    if len(hits) != 1:
        raise SystemExit('esperaba un solo renglón que empiece con «%s», hay %d'
                         % (empieza, len(hits)))
    return hits[0]


B = []

# ---------------------------------------------------------------- portada
B.append({'t': 'h2', 'x': 'Datos del procedimiento'})
B.append({'t': 'tabla', 'x': [
    ['Procedimiento', 'Body360® 5D — Lipoescultura + RibXcar® '
                      '(remodelación costal)'],
    ['Zonas tratadas', ''],
]})

# ------------------------------------------------------- primeras 72 horas
B.append({'t': 'h', 'x': 'Primeras 72 horas'})
B.append({'t': 'p', 'x':
    'Caminar desde el mismo día de la cirugía es la medida más importante '
    'para prevenir coágulos en las piernas, y respirar hondo cada hora es la '
    'más importante para sus pulmones. Las costillas remodeladas molestan al '
    'respirar hondo, al toser, al reír y al incorporarse: eso es lo esperado, '
    'y no es razón para respirar corto.'})
B.append({'t': 'ul', 'x': [
    punto(RIB, 4, 'RESPIRE HONDO'),
    punto(RIB, 4, 'Si necesita toser'),
    punto(RIB, 4, 'Tome sus analgésicos'),
    punto(LIPO, 4, 'Caminar 5–10 minutos'),
    # De las dos formas de levantarse manda la de RibXcar: incluye lo de la
    # hoja de lipo y además prohíbe empujarse con los brazos, que es lo que
    # tira de las costillas.
    punto(RIB, 4, 'Levántese en dos tiempos'),
    punto(RIB, 4, 'No estire los brazos'),
    punto(RIB, 4, 'Duerma boca arriba'),
    punto(LIPO, 4, 'Mover tobillos'),
    punto(LIPO, 4, 'Salida de líquido'),
    punto(LIPO, 4, 'Siempre acompañada'),
]})

# --------------------------------------------- presión arterial (idénticas)
B.append(bl(LIPO, 5)); B.append(bl(LIPO, 6))
B.append(bl(LIPO, 7)); B.append(bl(LIPO, 8))

# ------------------------------------------------ las DOS prendas, juntas
B.append({'t': 'h', 'x': 'Sus dos prendas: faja y corset'})
B.append({'t': 'p', 'x':
    'Usted trae dos prendas y hacen cosas distintas. La faja moldea y baja la '
    'inflamación de lo que se liposuccionó. El corset no es un accesorio: es '
    'el tratamiento, lo que mantiene en su lugar los cartílagos que se '
    # Nada de etiquetas HTML aquí: estos párrafos se imprimen como texto y un
    # <b> sale literal en el papel. El énfasis de estas hojas son mayúsculas,
    # como en «SI LA CIFRA DE ARRIBA BAJA DE 90».
    'remodelaron mientras consolidan. EL CORSET VA POR ENCIMA DE LA FAJA. La '
    'faja empieza desde el primer día; el corset empieza el día '
    + str(DIA_CORSET) + '. El orden, de adentro hacia afuera, es: su piel, la '
    'camiseta de algodón, la faja y hasta arriba el corset.'})
B.append({'t': 'tabla', 'x': [
    ['FAJA · semanas 1–6', 'Día y noche', 'Retirar solo para bañarse'],
    ['FAJA · semanas 7–12', '12 horas al día',
     'Usted elige el horario: de día o de noche'],
    ['CORSET · día ' + str(DIA_CORSET) + ' a semana 8', 'Día y noche, encima '
     'de la faja. Sólo se lo quita para bañarse', 'Un broche más cada semana'],
    ['CORSET · semana 8 al mes 6', 'Día y noche',
     'Ya no se aprieta más: se queda en el broche al que llegó'],
]})
B.append({'t': 'ul', 'x': [
    punto(RIB, 8, 'Ajuste:'),
    punto(RIB, 8, 'Un broche por semana'),
    # Los dos renglones que la fusión obligó a reescribir, porque las hojas de
    # origen hablan de UNA prenda y aquí son dos.
    'Pliegues: revise que ni la faja ni el corset formen arrugas, sobre todo '
    'en cintura, ingles y axilas; un pliegue marca la piel.',
    'Higiene: tenga dos fajas y dos corsets, para alternarlos y lavarlos a '
    'mano.',
    # En la RibXcar sola la camiseta va contra la piel porque no hay faja.
    # Aquí la faja ya va debajo, así que el renglón tenía que decir el orden
    # completo o dejaba a la paciente adivinando dónde va cada cosa.
    'Use una camiseta de algodón de tirantes contra la piel, debajo de la '
    'faja: evita que la faja le lastime la piel y que las varillas y los '
    'broches del corset se le marquen.',
    punto(RIB, 8, 'Si se lo quitó para bañarse'),
]})

# ------------------------------------------- baño: manda el plazo de la lipo
B.append(bl(LIPO, 13)); B.append(bl(LIPO, 14))
# El renglón del secado habla de volver a poner «la faja». Aquí son dos
# prendas y la que queda contra la piel húmeda es la faja, pero el corset
# también se vuelve a poner: se nombran las dos.
B.append({'t': 'ul', 'x': [
    ('Secado a toques con toalla limpia; seque bien las incisiones antes de '
     'volver a ponerse la faja y el corset.')
    if y.startswith('Secado a toques') else y
    for y in pts(LIPO, 15)
]})

# --------------------------------------------------------- alimentación
B.append(bl(LIPO, 16)); B.append(bl(LIPO, 17)); B.append(bl(LIPO, 18))

# ------------------------------------------------------------- calendario
# El más lento de los dos en cada renglón, y los renglones que sólo tiene
# RibXcar copiados con su propio plazo. Ningún número es nuevo.
B.append({'t': 'h', 'x': 'Calendario de actividades'})
B.append({'t': 'p', 'x':
    'Son dos procedimientos en un mismo tiempo quirúrgico, así que en cada '
    'renglón manda el plazo más largo de los dos. Lo que desplaza un '
    'cartílago recién remodelado es cargar, torcer el tronco y estirar los '
    'brazos: por eso esos tres son los que más esperan.'})
B.append({'t': 'tabla', 'x': [
    ['Caminar', 'Día 0', 'Obligatorio, varias veces al día'],
    ['Trabajo de escritorio / home office', 'Día 7–10',
     'Pararse y caminar cada hora'],
    ['Manejar', 'Día 7–10',
     'Sin analgésicos que den sueño, y sólo cuando pueda girar el tronco y '
     'frenar sin molestia'],
    ['Estirar los brazos por encima de la cabeza', 'Semana 2',
     'Antes de eso, todo a la altura del pecho'],
    ['Viaje en avión corto (< 3 h)', 'Semana 2',
     'Con faja y corset, medias de compresión y caminando en el vuelo; '
     'avísenos antes'],
    ['Relaciones sexuales', 'Semana 2–3',
     'Sin presión sobre el tórax ni sobre las zonas tratadas'],
    ['Ejercicio ligero (caminadora, bicicleta fija)', 'Semana 3',
     'Intensidad baja, sin impacto y sin usar los brazos'],
    ['Viaje largo (> 3 h)', 'Semana 3–4', 'Solo con autorización'],
    ['Girar el tronco, agacharse a recoger', 'Semana 4',
     'Doble las rodillas en lugar de torcer la cintura'],
    ['Alberca, mar, tina, vapor', 'Semana 4',
     'Con las incisiones completamente cerradas'],
    ['Cargar objetos pesados (> 5 kg)', 'Semana 6', 'Incluye cargar niños'],
    ['Sol directo / bronceado', 'Semana 6–8',
     'Protector solar FPS 50 en cicatrices por 12 meses'],
    ['Ejercicio completo (pesas, correr, abdomen)', 'Semana 8',
     'Nada de abdomen ni de pecho antes'],
    ['Deporte de contacto', 'Mes 6',
     'Hasta que el cartílago haya consolidado'],
]})
B.append({'t': 'p', 'x':
    'Postura: no duerma boca abajo ni de lado las primeras 2 semanas.'})

# ----------------------------------------------------------- qué es normal
B.append({'t': 'h', 'x': 'Qué es normal'})
B.append({'t': 'p', 'x':
    'El resultado no se ve en las primeras semanas. La inflamación baja de '
    'forma progresiva y la cintura se va definiendo a lo largo de los meses, '
    'conforme el cartílago consolida en su nueva posición y usted sigue '
    'usando el corset.'})
B.append({'t': 'ul', 'x': pts(LIPO, 25) + [
    punto(RIB, 19, 'Molestia en las costillas'),
    punto(RIB, 19, 'Sensación de opresión'),
    punto(RIB, 19, 'Tronidos o chasquidos'),
]})

# ------------------------------------------------- garganta (la de siempre)
for n in (26, 27, 28, 29):
    B.append(bl(LIPO, n))

# -------------------------------------------------------- signos de alarma
B.append(bl(LIPO, 30)); B.append(bl(LIPO, 31))
B.append(bl(LIPO, 32))
B.append({'t': 'ul', 'x': pts(LIPO, 33) + [
    punto(RIB, 27, 'Dolor que aumenta cada vez que respira'),
    punto(RIB, 27, 'Un burbujeo o crujido'),
]})
B.append(bl(LIPO, 34))
B.append({'t': 'ul', 'x': pts(LIPO, 35) + [
    punto(RIB, 29, 'El corset le aprieta'),
]})

# ------------------------------------------------------------------ cierre
for n in (36, 37, 38, 39):
    B.append(bl(LIPO, n))

hoja = {
    'id': 'body360_ribxcar',
    'nombre': 'Body360 5D — Lipoescultura + RibXcar',
    'titulo': 'Recomendaciones postoperatorias — Body360 5D '
              '(lipoescultura y RibXcar)',
    # Sin `coincide`, como las demás combinadas: se escoge a mano. Si se
    # propusiera sola por la palabra «lipoescultura», una paciente de 4D se
    # llevaría a casa un corset que no tiene.
    'coincide': [],
    'entrada': LIPO['entrada'],
    'preguntas': copia(LIPO['preguntas']),
    'bloques': B,
}

# ---------------------------------------------------------------------------
# Redes de seguridad
# ---------------------------------------------------------------------------
plano = json.dumps(B, ensure_ascii=False)

# Lo que él definió el 26-nov-2026. Si alguno se pierde, la hoja no sirve.
if 'día ' + str(DIA_CORSET) not in plano:
    raise SystemExit('no quedó el día %d del corset' % DIA_CORSET)
if 'día 1' in plano or 'día 4' in plano:
    raise SystemExit('quedó un día de corset que no es el 3')
if 'mes 6' not in plano.lower():
    raise SystemExit('falta la estabilización hasta el mes 6')
if 'por encima de la faja' not in plano.lower():
    raise SystemExit('falta decir que el corset va encima de la faja')
for t in ['FAJA · semanas 1–6', 'FAJA · semanas 7–12']:
    if t not in plano:
        raise SystemExit('se perdió el esquema de la faja: %s' % t)

# Estos párrafos se imprimen como TEXTO: una etiqueta HTML sale literal en la
# hoja que recibe la paciente. Pasó al escribir esta hoja.
for etiqueta in ['<b>', '</b>', '<i>', '<br', '<p>']:
    if etiqueta in plano:
        raise SystemExit('hay HTML literal en el texto: «%s»' % etiqueta)

# Trae dos prendas: ningún renglón que hable de las dos puede nombrar sólo
# una, porque entonces la paciente no sabe qué hacer con la otra.
if 'ni la faja ni el corset formen arrugas' not in plano:
    raise SystemExit('el renglón de los pliegues sigue hablando de una prenda')
if 'volver a ponerse la faja y el corset' not in plano:
    raise SystemExit('el renglón del secado sigue hablando de una prenda')
if 'contra la piel, debajo de la faja' not in plano:
    raise SystemExit('la camiseta de algodón no dice dónde va, y aquí hay dos '
                     'prendas encimadas')

# El choque: no puede quedar la versión corta de levantarse, la que no
# prohíbe empujarse con los brazos.
if 'Levantarse despacio' in plano:
    raise SystemExit('quedó la forma de levantarse de la hoja de lipo, que no '
                     'prohíbe empujarse con los brazos')

# El baño manda el plazo de la lipo, que sí tiene incisiones.
if '48 horas' not in plano:
    raise SystemExit('el baño debe seguir el plazo de la lipo, 48 horas')
if '24 horas, con el corset quitado' in plano:
    raise SystemExit('se coló el plazo de baño de la RibXcar sola')

# Lo que ninguna de las dos hojas sueltas le daba completo.
for obliga in ['RESPIRE HONDO', 'almohada contra el pecho', 'camiseta de '
               'algodón', 'Un broche por semana', 'burbujeo']:
    if obliga not in plano:
        raise SystemExit('falta «%s» en la hoja' % obliga)

# Ningún bloque puede colgar de una pregunta que la hoja no hace.
ids = {q['id'] for q in hoja['preguntas']}
for b in B:
    for clave in (b.get('si') or {}):
        if clave not in ids:
            raise SystemExit('un bloque depende de «%s», que nadie pregunta'
                             % clave)

# Un renglón repetido palabra por palabra en la misma lista es descuido.
for b in B:
    if b['t'] == 'ul' and len(b['x']) != len(set(b['x'])):
        raise SystemExit('hay renglones duplicados en una lista')

# Que no se haya colado texto facial ni de mama.
for palabra in ['párpado', 'facelift', 'rinoplastia', 'faja de cuello',
                'pezón', 'areola', 'brasier']:
    if palabra in plano.lower():
        raise SystemExit('texto que no es de esta cirugía: «%s»' % palabra)

hoja['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in hoja.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

# Entra junto a las otras dos de contorno corporal, después de la de RibXcar.
pos = next(i for i, h in enumerate(cat['hojas']) if h['id'] == 'ribxcar') + 1
cat['hojas'].insert(pos, hoja)

cat['version'] = hashlib.sha256(json.dumps(
    {'hojas': cat['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

n = sum(len(b['x']) if b['t'] in ('ul', 'tabla', 'citas') else 1 for b in B)
print('hoja body360_ribxcar · versión %s · %d bloques, %d renglones'
      % (hoja['version'], len(B), n))
print('catálogo de indicaciones  %s · %d hojas'
      % (cat['version'], len(cat['hojas'])))
