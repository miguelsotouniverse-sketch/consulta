#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA HOJA DE INDICACIONES DE VITALIA
===================================
el paquete de seis suplementos alimenticios

Por qué es distinta a todas las demás de este catálogo
-------------------------------------------------------
Las otras quince hojas son postoperatorias o preoperatorias: salen de una
cirugía. Ésta sale de una compra. No habla de heridas, ni de prendas, ni de
signos de alarma, y no se entrega al alta: se entrega con el paquete.

Por eso tiene su propio documento en el expediente —como la de faja y la
preoperatoria— y no es una hoja más dentro de «Indicaciones de alta». Buscar
las indicaciones de un suplemento dentro de un documento que se llama «de
alta» es el mismo tipo de confusión que ya costó una impresión en blanco.

De dónde sale el contenido
--------------------------
TODO el texto lo escribió el médico y se transcribe tal cual, el 26-nov-2026.
Aquí no hay contenido propuesto: ni una dosis, ni un plazo, ni una
precaución. Lo único que se hizo fue darle la forma que ya tienen las demás
hojas —tablas, listas, recuadro, firmas— para que se imprima igual que el
resto del juego.

Lo único que se tocó de su texto
--------------------------------
Un acento: «contínue» por «continúe». Es texto que se imprime y se entrega.

LAS CUENTAS, COMPROBADAS Y NO SUPUESTAS
----------------------------------------
Cada «le alcanza para» se verificó contra el contenido del frasco y la dosis
diaria antes de escribir nada. Las seis cuadran:

    RESVE-250    60 cáps  ÷ 2/día  =  30 días   ✓
    VITA-C300   300 tabs  ÷ 1/día  = 300 días   ✓
    Colágeno      1000 g  ÷ 10 g   = 100 días   ✓
    HMB         120 cáps  ÷ 2/día  =  60 días   ✓
    HC-PLUS      80 cáps  ÷ 1/día  =  80 días   ✓
    MAG-100     120 cáps  ÷ 3 o 4  =  40 o 30   ✓  («30 a 40 días»)

La verificación vive además en las redes de seguridad de abajo, así que si
algún día cambia una presentación y nadie ajusta la columna, el script se
detiene en vez de imprimir una hoja que promete un mes de más.

Uso:  python3 construir_hoja_vitalia.py [indicaciones.json]
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'

# Lo que dice cada frasco, para poder comprobar la columna de duración.
# (producto, unidades del frasco, dosis diaria, lo que dice la hoja)
CUENTAS = [
    ('RESVE-250', 60, 2, 30),
    ('VITA-C300', 300, 1, 300),
    ('Colágeno Hidrolizado Puro', 1000, 10, 100),
    ('HMB', 120, 2, 60),
    ('HC-PLUS', 80, 1, 80),
]

cat = json.load(open(RUTA, encoding='utf-8'))
H = {h['id']: h for h in cat['hojas']}

if 'vitalia' in H:
    raise SystemExit('ya existe la hoja de VITALIA')

B = []

# ---------------------------------------------------------------- portada
B.append({'t': 'h2', 'x': 'Datos del paquete'})
B.append({'t': 'tabla', 'x': [
    ['Paquete', 'VITALIA — seis suplementos alimenticios'],
]})

B.append({'t': 'p', 'x':
    'Su paquete VITALIA contiene seis suplementos alimenticios. Tómelos todos '
    'los días, repartidos en tres momentos: desayuno, comida y cena.'})

# --------------------------------------------------- qué contiene el paquete
B.append({'t': 'h', 'x': 'Qué contiene su paquete'})
B.append({'t': 'tabla',
          'cols': ['Producto', 'Contenido del frasco',
                   'Qué aporta cada dosis diaria', 'Le alcanza para'],
          'x': [
    ['RESVE-250', '60 cápsulas',
     '500 mg de resveratrol, con extracto de semilla de uva, ácido alfa '
     'lipoico y espirulina', '30 días'],
    ['VITA-C300', '300 tabletas',
     '300 mg de vitamina C, con semilla de uva y escaramujo', '300 días'],
    ['Colágeno Hidrolizado Puro', '1 kg en polvo',
     '10 g de colágeno hidrolizado', '100 días'],
    ['HMB', '120 cápsulas', '1,000 mg de HMB', '60 días'],
    ['HC-PLUS', '80 cápsulas',
     '100 mg de ácido hialurónico y 90 mg de colágeno hidrolizado', '80 días'],
    ['MAG-100', '120 cápsulas',
     'Glicinato de magnesio con L-teanina', '30 a 40 días'],
]})
B.append({'t': 'p', 'x':
    'Los frascos no se terminan al mismo tiempo. Reponga cada producto cuando '
    'se le acabe, sin esperar a los demás.'})

# ------------------------------------------------------------ el horario
B.append({'t': 'h', 'x': 'Su horario diario'})
B.append({'t': 'tabla',
          'cols': ['Momento', 'Qué tomar', 'Cantidad'],
          'x': [
    ['Con el desayuno', 'RESVE-250', '2 cápsulas'],
    ['Con el desayuno', 'VITA-C300', '1 tableta'],
    ['Con el desayuno', 'Colágeno Hidrolizado Puro',
     '10 g disueltos en agua, café, jugo o licuado'],
    ['Con la comida', 'HMB', '2 cápsulas'],
    ['Con la comida', 'HC-PLUS', '1 cápsula'],
    ['Con la cena', 'MAG-100', 'Mujeres: 3 cápsulas · Hombres: 4 cápsulas'],
]})
B.append({'t': 'p', 'x':
    'Tómelos siempre con alimentos y con un vaso de agua. Si un día olvida una '
    'toma, continúe al día siguiente con la cantidad de siempre. No duplique '
    'la dosis.'})

# ------------------------------------------------- cómo tomar cada producto
B.append({'t': 'h', 'x': 'Cómo tomar cada producto'})
B.append({'t': 'ul', 'x': [
    'RESVE-250: 2 cápsulas juntas con el desayuno. Al acompañarlas con '
    'alimentos el estómago lo tolera mejor.',
    'VITA-C300: 1 tableta al día con el desayuno. No exceda 1 tableta diaria.',
    'Colágeno Hidrolizado Puro: 1 porción de 10 g al día. Se disuelve en agua '
    'o en cualquier bebida, fría o caliente; puede agregarlo a su café de la '
    'mañana. No tiene sabor.',
    'HMB: 2 cápsulas juntas con la comida. Los días que haga ejercicio puede '
    'tomarlas después de entrenar, en lugar de con la comida.',
    'HC-PLUS: 1 cápsula al día con la comida.',
    'MAG-100: con la cena, entre 30 y 60 minutos antes de dormir. Mujeres, 3 '
    'cápsulas; hombres, 4. Si nota heces blandas, baje a 2 cápsulas por unos '
    'días.',
]})
B.append({'t': 'p', 'x':
    'No exceda la porción indicada de ningún producto. Conserve los frascos '
    'bien cerrados, en un lugar fresco y seco, sin luz directa del sol.'})

# ---------------------------------------------------------- precauciones
B.append({'t': 'h', 'x': 'Precauciones'})
B.append({'t': 'p', 'x':
    'Antes de empezar, consulte a su médico en cualquiera de estos casos:'})
B.append({'t': 'ul', 'x': [
    'Está embarazada o en periodo de lactancia.',
    'Toma medicamentos para la coagulación de la sangre, incluida la aspirina '
    'diaria.',
    'Toma medicamentos para controlar la glucosa o la presión arterial.',
    'Su médico le ha indicado cuidar la función de sus riñones.',
    'Es alérgico a alguno de los componentes.',
]})
# El recuadro: es lo único de esta hoja que puede cruzarse con una cirugía, y
# coincide con el plazo de 14 días de su hoja preoperatoria.
B.append({'t': 'nota', 'x':
    'SI TIENE PROGRAMADA UNA CIRUGÍA, suspenda todo el paquete 14 días antes y '
    'avise a su médico que lo estaba tomando. Reanude cuando su médico se lo '
    'indique.'})
B.append({'t': 'p', 'x':
    'Si nota alguna molestia que relacione con estos productos, suspenda su '
    'consumo y comuníquese con nosotros.'})

# ------------------------------------------------------------- constancia
B.append({'t': 'h', 'x': 'Constancia de entrega'})
B.append({'t': 'p', 'x': 'Recibí este paquete y estas indicaciones de consumo.'})
B.append({'t': 'firmas', 'x': ['Paciente', 'Quien entrega']})

hoja = {
    'id': 'vitalia',
    'nombre': 'VITALIA — indicaciones de consumo',
    'titulo': 'VITALIA — Indicaciones de consumo',
    # Sin `coincide`: no sale de un procedimiento, así que no hay palabra en el
    # expediente que deba proponerla. Se escoge a mano, al entregar el paquete.
    'coincide': [],
    # El encabezado impreso de las hojas dice «Fecha del procedimiento». Aquí
    # no hay procedimiento: hay una entrega.
    'etiquetaFecha': 'Fecha de entrega',
    'bloques': B,
}

# ---------------------------------------------------------------------------
# Redes de seguridad
# ---------------------------------------------------------------------------
plano = json.dumps(B, ensure_ascii=False)

# Las tablas se buscan por su encabezado, no por su posición: contar bloques
# a mano ya falló al escribir esto, y un índice equivocado deja la red de
# seguridad vigilando el bloque que no es.
def tabla_con(col0):
    hits = [b for b in B if b['t'] == 'tabla' and (b.get('cols') or [''])[0] == col0]
    if len(hits) != 1:
        raise SystemExit('esperaba una sola tabla con la columna «%s»' % col0)
    return hits[0]


def lista_que_empieza(prefijo):
    hits = [b for b in B if b['t'] == 'ul'
            and any(y.startswith(prefijo) for y in b['x'])]
    if len(hits) != 1:
        raise SystemExit('esperaba una sola lista con «%s»' % prefijo)
    return hits[0]


T_PAQUETE = tabla_con('Producto')
T_HORARIO = tabla_con('Momento')
L_COMO = lista_que_empieza('RESVE-250:')

# LAS CUENTAS. Si algún día cambia una presentación y nadie ajusta la columna,
# que se detenga aquí en vez de imprimir un mes de más.
contenido = {f[0]: f for f in T_PAQUETE['x']}
for prod, frasco, dosis, dias in CUENTAS:
    fila = contenido.get(prod)
    if not fila:
        raise SystemExit('falta %s en la tabla del paquete' % prod)
    if str(dias) + ' día' not in fila[3]:
        raise SystemExit('%s: la tabla dice «%s» y la cuenta da %d días'
                         % (prod, fila[3], dias))
    if frasco // dosis != dias:
        raise SystemExit('%s: %d ÷ %d = %d, no %d'
                         % (prod, frasco, dosis, frasco // dosis, dias))
# El magnesio es el único con dos dosis, por eso va aparte.
mag = contenido.get('MAG-100')
if not mag or '30 a 40 días' not in mag[3]:
    raise SystemExit('MAG-100 debe decir «30 a 40 días»: 120 ÷ 4 = 30 y '
                     '120 ÷ 3 = 40')

# Los seis productos tienen que estar en las dos tablas: si uno aparece en el
# paquete y no en el horario, la paciente no sabe cuándo tomarlo.
horario = [f[1] for f in T_HORARIO['x']]
for prod, *_ in CUENTAS:
    if prod not in horario:
        raise SystemExit('%s está en el paquete y no en el horario' % prod)
if 'MAG-100' not in horario:
    raise SystemExit('MAG-100 no está en el horario')
if len(T_PAQUETE['x']) != 6 or len(T_HORARIO['x']) != 6:
    raise SystemExit('el paquete son seis productos en las dos tablas')

# Y cada uno tiene que tener su renglón en «cómo tomar cada producto».
comollevar = L_COMO['x']
for prod in [f[0] for f in T_PAQUETE['x']]:
    if not any(y.startswith(prod + ':') for y in comollevar):
        raise SystemExit('%s no tiene renglón en «cómo tomar»' % prod)

# Las precauciones no se pueden perder: son lo único de esta hoja que puede
# cruzarse con un medicamento o con una cirugía.
for obliga in ['embarazada', 'coagulación', 'glucosa', 'riñones', 'alérgico',
               '14 días antes']:
    if obliga.lower() not in plano.lower():
        raise SystemExit('falta la precaución de «%s»' % obliga)

# Esta hoja no es de una cirugía: no debe hablar como si lo fuera.
for sobra in ['herida', 'incisión', 'faja', 'anestesia', 'quirófano',
              'signos de alarma', 'urgencias']:
    if sobra.lower() in plano.lower():
        raise SystemExit('«%s» no va en una hoja de suplementos' % sobra)

# El texto se imprime como texto.
for etiqueta in ['<b>', '</b>', '<i>', '<br', '<p>']:
    if etiqueta in plano:
        raise SystemExit('HTML literal en el texto')

# El acento que se corrigió de su documento.
if 'contínue' in plano:
    raise SystemExit('quedó «contínue»; va «continúe»')

# Sin preguntas declaradas, ningún bloque puede estar condicionado.
for b in B:
    if b.get('si'):
        raise SystemExit('hay un bloque condicionado y la hoja no pregunta nada')
for b in B:
    if b['t'] == 'ul' and len(b['x']) != len(set(b['x'])):
        raise SystemExit('renglones duplicados')

hoja['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in hoja.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

# Al final del catálogo, con las hojas que no salen de un procedimiento.
cat['hojas'].append(hoja)

cat['version'] = hashlib.sha256(json.dumps(
    {'hojas': cat['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

n = sum(len(b['x']) if b['t'] in ('ul', 'tabla', 'firmas') else 1 for b in B)
print('hoja vitalia · versión %s · %d bloques, %d renglones · 6 productos, '
      'cuentas verificadas' % (hoja['version'], len(B), n))
print('catálogo de indicaciones  %s · %d hojas'
      % (cat['version'], len(cat['hojas'])))
