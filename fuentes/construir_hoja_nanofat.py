#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA HOJA DE MICRO Y NANOFAT FACIAL
==================================

Qué pidió
---------
El 12-nov-2026, el día del procedimiento: «hoy voy a hacer un tratamiento de
micro/nanofat. Me ayudas a subir las recomendaciones postoperatorias». No
existía nada: «nanofat», «microfat» y «lipoinjerto» no aparecían en ningún
catálogo.

LO MÁS IMPORTANTE DE ESTA HOJA
-------------------------------
Hay dos zonas con cuidados OPUESTOS, y es la primera hoja del sistema donde
pasa eso:

  · la zona DONADORA, de donde se tomó la grasa, se cuida como una lipo
    pequeña: frío sí, compresión sí;
  · la zona INJERTADA no admite ni frío ni presión.

El médico lo confirmó el 12-nov-2026 cuando se lo pregunté de frente:
**«Nada de frío ni presión sobre lo injertado.»** Y lo pregunté porque las
cinco hojas faciales del sistema —Deep Plane, combinada, CO₂, eCO₂,
Morpheus8— mandan todas «frío local 15 minutos cada hora», y yo estaba a punto
de copiar ese renglón aquí. Habría sido un error silencioso: el renglón se lee
perfectamente bien y la paciente lo habría obedecido enfriando justo el tejido
que necesita que le lleguen vasos para sobrevivir.

Por eso la hoja no se limita a omitir el frío: lo PROHÍBE por escrito sobre lo
injertado y lo permite por escrito sobre la donadora. Una paciente que ya tuvo
otro procedimiento facial suyo trae la costumbre del hielo cada hora.

Lo demás que el médico confirmó ese día
----------------------------------------
· **Sedación**, siempre. Por eso el bloque de «no maneje, no se quede sola» va
  fijo y no condicionado: aquí no hace falta preguntarlo.
· **Zona donadora: sólo apósito compresivo unos días.** No faja, así que la
  donadora es un párrafo y no una sección entera.
· **Receta: antibiótico, analgésico, Cicalfate y protector solar**, «porque el
  nanofat lleva micropunciones».

Lo que escribí yo y necesita su visto bueno                        ←CONFIRMAR
-------------------------------------------
· Los plazos del calendario de actividades, todos.
· La expectativa de reabsorción: que al principio se vea de más y que el
  volumen final se juzgue a los 3 a 6 meses. Sin eso, la paciente entra en
  pánico la tercera semana, cuando baja la inflamación.

Sin pregunta del tubo                                              ←CONFIRMAR
---------------------
Esta hoja NO entra en `agregar_molestia_garganta.py` y por eso no pregunta por
el tubo: el médico dijo «sedación» sin matizar, y en Morpheus8 —donde dijo que
variaba— sí la lleva. Si algún micro/nanofat llega a ir con tubo o mascarilla,
es agregar `nanofat` a dos listas de ese script.

Uso:  python3 construir_hoja_nanofat.py [indicaciones.json]
      (después de construir_receta_morpheus8.py)
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'

cat = json.load(open(RUTA, encoding='utf-8'))
H = {h['id']: h for h in cat['hojas']}

if 'nanofat' in H:
    raise SystemExit('la hoja de nanofat ya existe')
for req in ('morpheus8', 'lipoescultura'):
    if req not in H:
        raise SystemExit('falta la hoja ' + req + ', de donde se copia')

M = H['morpheus8']
L = H['lipoescultura']


def ren(hoja, fragmento):
    """Un renglón de lista, buscado por su texto. Si allá cambia, truena."""
    hallados = [x for b in hoja['bloques'] if b['t'] == 'ul'
                for x in b['x'] if fragmento in x]
    if len(hallados) != 1:
        raise SystemExit('busqué «' + fragmento + '» en ' + hoja['id'] +
                         ' y hallé ' + str(len(hallados)) + '; esperaba 1')
    return hallados[0]


def parr(hoja, fragmento):
    hallados = [str(b['x']) for b in hoja['bloques']
                if b['t'] in ('p', 'nota') and fragmento in str(b.get('x', ''))]
    if len(hallados) != 1:
        raise SystemExit('busqué el párrafo «' + fragmento + '» en ' +
                         hoja['id'] + ' y hallé ' + str(len(hallados)))
    return hallados[0]


# El médico escribió «Cicalfate» al definir la receta, y lo marqué porque sus
# otras dos hojas de consultorio usan Cicaplast, que es de otra marca. El
# 12-nov-2026 lo resolvió: «cicaplast baume esta bien». Era un lapsus, así que
# aquí va el mismo producto que en eCO₂ y Morpheus8.
CICA = 'Cicaplast Baume'

hoja = {
    'id': 'nanofat',
    'nombre': 'Micro y nanofat facial',
    'titulo': 'Recomendaciones posteriores al micro y nanofat facial',
    'coincide': ['nanofat', 'microfat', 'micro/nanofat', 'nanograsa',
                 'lipoinjerto facial', 'injerto de grasa facial'],
    'bloques': [

        {'t': 'h2', 'x': 'Datos del procedimiento'},
        {'t': 'tabla', 'cols': ['Campo', 'Dato'], 'x': [
            ['Procedimiento',
             'Micro y nanofat — injerto de grasa propia, con micropunciones'],
            ['Zona injertada', ''],
            ['Zona donadora', ''],
        ]},

        # ---------------- lo que no se puede leer mal ----------------
        {'t': 'nota', 'x': (
            'SI HOY SÓLO PUEDE LEER UNA COSA, LEA ESTO. Su cara y la zona de '
            'donde tomamos la grasa se cuidan DISTINTO, casi al revés. '
            '1) Sobre la cara injertada: NADA de hielo, nada de presión y nada '
            'de masaje. 2) Sobre la zona donadora: frío sí, y el apósito '
            'compresivo puesto. 3) Duerma boca arriba.')},

        {'t': 'h', 'x': '1. Primeras 48 horas'},
        {'t': 'p', 'x': (
            'La grasa que le pusimos todavía no tiene vasos propios: durante '
            'los primeros días se alimenta del tejido que la rodea, y sólo '
            'después le crecen vasos que la mantienen viva. Todo lo que apriete, '
            'enfríe o mueva esa zona juega en contra de que prenda. Por eso las '
            'indicaciones de abajo no son de comodidad: son el tratamiento.')},
        {'t': 'ul', 'x': [
            # ←NUEVO: el corazón de la hoja, y lo contrario de lo que dicen las
            # otras cinco hojas faciales del sistema.
            'NO se ponga hielo ni compresas frías sobre la zona injertada, '
            'aunque en otros procedimientos se lo hayamos indicado. El frío '
            'cierra los vasos que tienen que alimentar la grasa nueva.',
            # ←NUEVO
            'No se presione, no se masajee y no se frote la cara. Nada de '
            'masaje facial, drenaje linfático en la cara, aparatos ni rodillos, '
            'hasta que la revisemos.',
            # ←NUEVO ←CONFIRMAR el plazo
            'Duerma boca arriba y con la cabeza elevada —dos almohadas— las '
            'primeras 2 semanas. No duerma de lado ni boca abajo: el peso de su '
            'propia cara sobre la almohada es presión.',
            # ←NUEVO
            'Nada que apriete sobre la zona injertada: ni cubrebocas ajustado, '
            'ni anteojos que se apoyen donde se injertó, ni antifaz para dormir. '
            'Si usa anteojos, díganos dónde se apoyan y le decimos qué hacer.',
            ren(M, 'Manos limpias siempre que se toque la cara').replace(
                'los puntitos son canales abiertos hacia la dermis',
                'las micropunciones son canales abiertos hacia la dermis'),
            ren(M, 'Inflamación: la cara se hincha sobre todo al despertar'),
            ren(M, 'No se exponga al viento, al polvo, al humo'),
            # El de Morpheus8 termina en «una piel que acaba de recibir
            # radiofrecuencia». Aquí no hubo radiofrecuencia, y además el
            # motivo es otro: el calor dilata y sangra sobre un injerto que
            # todavía no tiene vasos. Se reescribe la razón, no la regla.
            ren(M, 'Nada de calor sobre la cara las primeras 48 horas').split(
                '. El calor')[0] + '. El calor sobre una cara recién '
            'injertada aumenta la inflamación y el sangrado.',
        ]},

        # ---------------- sedación: siempre, sin preguntar ----------------
        {'t': 'h2', 'x': 'Hoy, porque llevó sedación'},
        {'t': 'ul', 'x': [
            ren(M, 'Hoy no maneje, no tome decisiones importantes'),
            ren(M, 'Que alguien la acompañe de regreso a casa'),
            ren(M, 'No tome alcohol hoy'),
        ]},

        # ---------------- la zona donadora ----------------
        {'t': 'h', 'x': '2. La zona de donde tomamos la grasa'},
        # ←NUEVO: aquí sí va el frío, y se dice que aquí sí para que el
        # contraste con la cara quede explícito y no parezca una errata.
        {'t': 'p', 'x': (
            'De esa zona se aspiró grasa por unas punciones muy pequeñas. Trae '
            'un apósito compresivo que se queda puesto los días que le '
            'indicamos. Aquí sí puede ponerse frío: es la cara injertada la que '
            'no lo admite.')},
        {'t': 'ul', 'x': [
            ren(L, 'Salida de líquido teñido de sangre por las incisiones'),
            ren(L, 'Incisiones: manténgalas limpias y secas'),
            # ←NUEVO ←CONFIRMAR los días del apósito
            'Mantenga el apósito compresivo los días que le indicamos. Si se '
            'despega o se moja, cámbielo por uno limpio y avísenos.',
            ren(L, 'Moretones extensos, que cambian de morado a verde'),
            ren(L, 'Adormecimiento u hormigueo de la piel tratada'),
        ]},

        # ---------------- piel y micropunciones ----------------
        {'t': 'h', 'x': '3. Cuidado de la piel de la cara'},
        {'t': 'p', 'x': (
            'El nanofat entra por micropunciones, así que la piel queda '
            'permeable unos días: lo que se ponga encima entra más que de '
            'costumbre. Estos días sólo va lo que viene en su receta.')},
        {'t': 'ul', 'x': [
            CICA + ': aplique una capa delgada sobre toda la zona tratada '
            'cada 12 horas, sin masajear — sólo apoyar y extender.',
            ren(M, 'No se ponga NADA más estos días').replace(
                'cremas «para después del láser»', 'cremas «para después»'),
            ren(M, 'Protector solar FPS 50+'),
            ren(M, 'Nada de ácidos, retinoides, exfoliantes ni mascarillas'),
            ren(M, 'Toalla y funda de almohada limpias'),
        ]},
        {'t': 'h2', 'x': 'Cómo lavarse la cara'},
        {'t': 'ul', 'x': [
            ren(M, 'Agua tibia y jabón neutro, con la mano limpia'),
            ren(M, 'Seque a toques con una toalla limpia'),
            'Vuelva a aplicar ' + CICA + ' enseguida, con la piel todavía '
            'húmeda y sin frotar.',
        ]},

        # ---------------- actividades ----------------
        {'t': 'h', 'x': '4. Calendario de actividades'},
        {'t': 'p', 'x': (
            'Lo que manda es que la grasa prenda. El sudor, el calor y '
            'cualquier cosa que presione la cara son lo que hay que posponer.')},
        {'t': 'tabla', 'cols': ['Actividad', 'A partir de', 'Nota'], 'x': [
            # ←CONFIRMAR todos estos plazos: son míos.
            ['Caminar', 'El mismo día', 'Suave, varias veces al día'],
            ['Trabajo de escritorio / home office', 'Día 2',
             'La cara se ve hinchada y con moretones'],
            ['Maquillaje sobre la cara', 'Día 5',
             'Con brocha limpia y sin presionar; desmaquíllese sin tallar'],
            ['Ejercicio, sudor, vapor, sauna', 'Semana 2',
             'El calor y el sudor juegan en contra de la grasa nueva'],
            ['Dormir de lado', 'Semana 2', 'Antes, siempre boca arriba'],
            ['Masaje facial, drenaje linfático en la cara, aparatos', 'Mes 2',
             'Sólo con autorización del Dr. Soto'],
            ['Alberca, mar, jacuzzi', 'Semana 3', ''],
            ['Ácidos, retinoides, exfoliantes', 'Semana 2', ''],
            ['Sol directo', 'Semana 4', 'Siempre con gorra y FPS 50'],
            ['Toxina botulínica o rellenos', 'Mes 3',
             'Sólo con autorización del Dr. Soto'],
        ]},
        # ←NUEVO ←CONFIRMAR: propio del injerto de grasa y de nada más.
        {'t': 'p', 'x': (
            'Peso: la grasa injertada se comporta como la grasa del resto de su '
            'cuerpo. Si baja de peso en los meses siguientes, parte del '
            'resultado se va con eso. Procure mantener su peso estable los '
            'primeros 6 meses.')},

        # ---------------- lo normal ----------------
        {'t': 'h', 'x': '5. Lo que es normal y no debe preocuparle'},
        # ←NUEVO ←CONFIRMAR: la expectativa que evita el pánico de la semana 3.
        {'t': 'p', 'x': (
            'Al principio se va a ver MÁS llena de lo que va a quedar. Eso es a '
            'propósito y es inflamación, no el resultado. Conforme baja, parte '
            'de la grasa injertada se reabsorbe —le pasa a todo injerto de '
            'grasa— y la que se queda ya es definitiva. El volumen final se '
            'juzga entre los 3 y los 6 meses, no antes.')},
        {'t': 'ul', 'x': [
            # ←NUEVO
            'Inflamación de la cara que es mayor al segundo y tercer día y más '
            'marcada al despertar.',
            # ←NUEVO
            'Moretones en la cara y en la zona donadora, que cambian de morado '
            'a verde y amarillo. Desaparecen en 2 a 3 semanas.',
            # ←NUEVO
            'Bolitas o irregularidades pequeñas al tacto en las primeras '
            'semanas, que se van suavizando. No se las masajee para '
            'deshacerlas: avísenos y las revisamos.',
            # ←NUEVO
            'Puntitos rojos o costritas muy finas donde entraron las '
            'micropunciones, que se caen solas en pocos días.',
            ren(M, 'Comezón mientras la piel cierra'),
            ren(L, 'Cansancio las primeras 1–2 semanas'),
            ren(L, 'Cambios de ánimo los primeros días'),
        ]},

        # ---------------- alarma ----------------
        {'t': 'h', 'x': '6. Signos de alarma: llame al teléfono de urgencias',
         'alarma': True},
        {'t': 'ul', 'x': [
            # Aquí iba un renglón sobre cambios en la vista, que yo había
            # puesto por la oclusión vascular del injerto facial. El médico lo
            # quitó el 12-nov-2026: «creo que alerta de más». Es su llamada y
            # era mía, marcada para confirmar desde el principio.
            #
            # Lo que SÍ se queda es el renglón de abajo, que cubre el mismo
            # problema por su signo en la piel —y ése sí es algo que la
            # paciente puede ver en el espejo sin ponerse a buscar síntomas.
            # ←NUEVO
            'Una zona de la cara que se pone blanca, moteada, morada o muy '
            'dolorosa, distinta del resto.',
            ren(M, 'Dolor que aumenta cada día en lugar de ceder'),
            ren(M, 'Fiebre de 38 °C o más'),
            ren(M, 'Zonas que se ponen amarillas, con costra gruesa'),
            ren(M, 'Enrojecimiento que se extiende fuera de la zona tratada'),
            ren(L, 'Enrojecimiento que se extiende, calor, pus o mal olor en una incisión'),
            # ←NUEVO
            'Inflamación de un solo lado de la cara que crece rápido y se '
            'siente dura.',
        ]},
        {'t': 'nota', 'alarma': True, 'x': (
            'Llámenos a cualquier hora, de día o de noche. La cara injertada la '
            'tiene que ver quien la trató: no se automedique ni acuda a otro '
            'consultorio sin avisarnos.')},

        {'t': 'h', 'x': '7. Citas y constancia de entrega'},
        {'t': 'p', 'x': parr(M, 'Recepción agenda y confirma cada cita')},
        {'t': 'p', 'x': parr(M, 'Recibí esta hoja de indicaciones y mi receta')},
        {'t': 'firmas', 'x': ['Paciente', 'Médico que entrega']},
    ],
}

i = [k for k, h in enumerate(cat['hojas']) if h['id'] == 'morpheus8'][0]
cat['hojas'].insert(i + 1, hoja)


# ---------------------------------------------------------------------------
# Redes de seguridad
# ---------------------------------------------------------------------------
def plano(t):
    import unicodedata
    t = unicodedata.normalize('NFD', str(t).lower())
    return ''.join(c for c in t if unicodedata.category(c) != 'Mn').strip()


for proc in ('Nanofat', 'Microfat facial', 'micro/nanofat'):
    p = plano(proc)
    halladas = [h['id'] for h in cat['hojas']
                if any(p.find(plano(c)) >= 0 for c in h.get('coincide', []))]
    if halladas != ['nanofat']:
        raise SystemExit('«' + proc + '» coincide con ' + str(halladas) +
                         ' y esperaba sólo con nanofat')

todo = json.dumps(hoja, ensure_ascii=False)

# LA RED QUE DE VERDAD IMPORTA: que no se haya colado el renglón de frío de las
# otras hojas faciales. Es el error que esta hoja existe para no cometer.
if 'Frío local' in todo or 'compresas frías sobre una gasa' in todo:
    raise SystemExit('se coló el renglón de frío local de las otras hojas '
                     'faciales: sobre lo INJERTADO no va frío')
if 'NO se ponga hielo ni compresas frías sobre la zona injertada' not in todo:
    raise SystemExit('falta la prohibición explícita del frío sobre el injerto')
if 'Aquí sí puede ponerse frío' not in todo:
    raise SystemExit('falta decir que en la zona donadora el frío SÍ se vale: '
                     'sin ese contraste la prohibición parece una errata')

# Lo que esta hoja no lleva.
for sobra in ('Cicalfate', 'faja', 'Vaselina', 'valaciclovir', 'Clobesol',
              # Se coló al copiar de Morpheus8 y lo destapó el PDF, no el
              # código: un renglón que explicaba el calor «sobre una piel que
              # acaba de recibir radiofrecuencia». Aquí no hubo ninguna.
              'radiofrecuencia', 'microagujas', 'retícula', 'láser'):
    if sobra in todo:
        raise SystemExit('se coló «' + sobra + '» en la hoja de nanofat')
# Y lo que sí.
for falta in (CICA, 'FPS 50', 'boca arriba', 'reabsorbe',
              'peso estable', 'apósito compresivo'):
    if falta not in todo:
        raise SystemExit('falta «' + falta + '» en la hoja de nanofat')
# El médico quitó el renglón de la vista el 12-nov-2026 por alertar de más.
# Que no regrese solo si alguien reconstruye la hoja.
if 'Cambios en la vista' in todo or 'perder visión' in todo:
    raise SystemExit('volvió a entrar el renglón de cambios en la vista, que '
                     'el médico quitó')

# El bloque de la sedación va FIJO, no condicionado: aquí siempre hay sedación.
if any(b.get('si') for b in hoja['bloques']):
    raise SystemExit('esta hoja no debe tener bloques condicionados')

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
print('hoja       nanofat            nueva -> %s  (%d bloques, %d renglones)'
      % (hoja['version'], len(hoja['bloques']), n))
print('catálogo   ' + cat['version'])
