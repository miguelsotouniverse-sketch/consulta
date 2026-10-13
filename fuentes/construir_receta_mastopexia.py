#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA RECETA DE MASTOPEXIA QUE FALTABA
====================================

Por qué faltaba
---------------
Mastopexia era el único procedimiento con hoja de recomendaciones y sin
plantilla de receta. Quien operaba una mastopexia tenía que escribir la receta
a mano, renglón por renglón, o tomar prestada la de otra cirugía y corregirla.

De dónde sale cada renglón
--------------------------
Casi todo se COPIA POR ÍNDICE de la plantilla de Deep Plane, que es la que el
médico ya revisó y aprobó: el antibiótico con su rama de alergia a penicilina,
el celecoxib con su rama de sulfas y su variante cada 24 horas, el paracetamol,
la prednisona, el protector gástrico, el tramadol en hoja de controlado, el
ondansetrón y los dos laxantes. Copiado, no reescrito: si él corrige el
paracetamol allá, se corrige aquí.

Lo que se deja fuera, y por qué
-------------------------------
  · Clorhexidina — es para la incisión intraoral del Bichat.
  · Hipromelosa  — es para el ojo de la blefaroplastia.
  · Rivaroxabán  — él lo dijo textual: «Ribaroxaban solo lo doy en mis
                   pacientes de contorno corporal». Mastopexia no lo lleva.

Lo que es nuevo y necesita su revisión renglón por renglón
----------------------------------------------------------
  1. EL RELAJANTE MUSCULAR.  Él lo pidió «en casos de pacientes con cirugia de
     mama en plano retromuscular», y pidió poder quitarlo cuando el plano no fue
     retromuscular. Entra ENCENDIDO, como él lo describió, y se apaga con un
     clic en la casilla del renglón. La molécula, la dosis y los días son
     propuesta mía y van marcadas  # ←CONFIRMAR.

     Ciclobenzaprina y no clorzoxazona: la clorzoxazona en México viene casi
     siempre en combinación fija con paracetamol (Tafirol Flex y similares), y
     eso apilaría paracetamol sobre el gramo cada 8 horas que ya lleva la
     receta. La ciclobenzaprina existe sola en tabletas de 10 mg.

  2. LOS SIGNOS DE ALARMA.  Los de Deep Plane son faciales y no sirven aquí.
     Estos nueve se escribieron para mama y van marcados  # ←NUEVO.

Uso:  python3 construir_receta_mastopexia.py [recetas.json]
      (correr DESPUÉS de agregar_prednisona.py, de quien copia ese renglón)
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'recetas.json'

# --- los números que no me dio ---------------------------------------------
RELAJANTE_DIAS = 7     # ←CONFIRMAR  días de ciclobenzaprina por la noche

cat = json.load(open(RUTA, encoding='utf-8'))
P = {p['id']: p for p in cat['plantillas']}

if 'mastopexia' in P:
    raise SystemExit('ya existe la plantilla de mastopexia; no se duplica')

DP = P['deep_plane']


def copia(lista, *indices):
    """Elementos aprobados, copiados por índice. Nunca se vuelven a teclear."""
    return [json.loads(json.dumps(lista[i], ensure_ascii=False)) for i in indices]


def med(nombre_parcial, **cambios):
    """Un medicamento de Deep Plane, buscado por nombre y copiado."""
    i = next(k for k, m in enumerate(DP['medicamentos'])
             if nombre_parcial.lower() in m['nombre'].lower())
    m = json.loads(json.dumps(DP['medicamentos'][i], ensure_ascii=False))
    for k, v in cambios.items():
        if v is None:
            m.pop(k, None)
        else:
            m[k] = v
    return m


def pregunta(pid):
    return json.loads(json.dumps(
        next(q for q in DP['preguntas'] if q['id'] == pid), ensure_ascii=False))


def aviso(clave_si):
    return json.loads(json.dumps(
        next(a for a in DP['avisos'] if a['si'] == clave_si), ensure_ascii=False))


# ------------------------------------------------------------ el relajante
RELAJANTE = {
    'hoja': 'general',
    'nombre': 'Ciclobenzaprina 10 mg, tabletas.',                 # ←CONFIRMAR
    'indicacion':
        'Tomar 1 tableta vía oral por la noche, al acostarse, durante '
        + str(RELAJANTE_DIAS) + ' días. Es para el espasmo del músculo '          # ←CONFIRMAR
        'pectoral, que es lo que aprieta y arde cuando el implante quedó por '
        'detrás del músculo. Da sueño: tómela sólo de noche y no maneje '
        'después de tomarla.',
    # El "quítele la marca si no fue retromuscular" NO va aquí: esta
    # indicación se imprime y la lee la paciente. Va en los avisos, que son
    # de pantalla y los lee el médico.
    'cantidad': str(RELAJANTE_DIAS) + ' tabletas',
    'duracion': str(RELAJANTE_DIAS) + ' días',
    'horario': {'n': 'Ciclobenzaprina (noche)', 'h': ['22:00']},
}

# --------------------------------------------------------------- la plantilla
MASTO = {
    'id': 'mastopexia',
    'nombre': 'Mastopexia',
    'coincide': ['mastopexia', 'pexia mamaria', 'mastopexia con implante',
                 'mastopexia de aumento', 'levantamiento de busto',
                 'pexia de mama'],
    'procedimiento': 'Mastopexia',
    'preguntas': [pregunta('peni'), pregunta('sulfa'), pregunta('otras'),
                  pregunta('renal'), pregunta('isrs'), pregunta('sintram')],
    'medicamentos': [
        med('Amoxicilina'),
        med('Clindamicina'),
        med('Paracetamol'),
        # las dos variantes del celecoxib y la rama de ketorolaco, tal cual
        [m for m in DP['medicamentos']
         if 'Celecoxib' in m['nombre'] and m['si'].get('c24') is False][0],
        [m for m in DP['medicamentos']
         if 'Celecoxib' in m['nombre'] and m['si'].get('c24') is True][0],
        med('Ketorolaco'),
        RELAJANTE,
        med('Prednisona'),
        med('Pantoprazol'),
        med('Tramadol'),
        med('Ondansetrón'),
        med('Polietilenglicol'),
        med('Senósidos'),
    ],
    'profilaxis': [
        {'si': {'peni': ['grave']}, 'texto': 'Clindamicina 900 mg IV'},
        {'si': {}, 'texto': 'Cefazolina 2 g IV'},
    ],
    'profilaxisNota': 'Repetir si la cirugía pasa de 4 h (cefazolina) o de 6 h '
                      '(clindamicina).',
    'avisos': [
        {'si': {}, 'tono': '', 'texto':
         'El relajante muscular entra encendido porque esta plantilla supone '
         'plano retromuscular. Si el implante quedó subglandular, o no hubo '
         'implante, quítele la marca al renglón de ciclobenzaprina.'},
        {'si': {'isrs': True}, 'tono': 'malo', 'texto':
         'Ciclobenzaprina + ISRS/IRSN: riesgo de síndrome serotoninérgico, y se '
         'suma al que ya trae el tramadol. Si deja los dos, explíquele los '
         'síntomas a la paciente; si no, quite uno.'},
        aviso({'c24': True}),
        aviso({'sulfa': True}),
        aviso({'renal': True}),
        aviso({'isrs': True, 'sintram': False}),
        aviso({'sintram': True}),
        aviso({'peni': ['leve']}),
        aviso({'peni': ['grave']}),
        aviso({'menor': True}),
    ],
    # ←NUEVO  los nueve signos de alarma, escritos para mama
    'alarma': [
        {'t': 'Un seno que crece rápido, se pone duro y duele cada vez más, '
              'sobre todo si es sólo uno de los dos.'},
        {'t': 'Sangrado que empapa el apósito o que no se detiene al hacer '
              'presión.'},
        {'t': 'Temperatura de 38 °C o más, medida con termómetro.'},
        {'t': 'Enrojecimiento que se va extendiendo alrededor de la herida, '
              'calor, o salida de líquido turbio o con mal olor.'},
        {'t': 'Piel del pezón o de la areola que se pone morada oscura, negra, '
              'o blanca y fría.'},
        {'t': 'Una herida que se abre o cuyos bordes se separan, en especial '
              'donde se juntan las cicatrices por debajo de la areola.'},
        {'t': 'Dolor, hinchazón o endurecimiento en una pantorrilla.'},
        {'t': 'Dificultad para respirar, dolor en el pecho al respirar hondo, o '
              'tos con sangre.'},
        {'t': 'Vómito que no para y no le permite tomar los medicamentos.'},
    ],
    'horaNota': DP['horaNota'],
}

MASTO['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in MASTO.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

# Entra después de body360, para que las de cuerpo queden juntas en el menú.
i = next((k for k, p in enumerate(cat['plantillas']) if p['id'] == 'body360'), -1)
cat['plantillas'].insert(i + 1 if i >= 0 else len(cat['plantillas']), MASTO)

cat['version'] = hashlib.sha256(json.dumps(
    {'plantillas': cat['plantillas'], 'hojas': cat['hojas'], 'horas': cat['horas']},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

print('plantilla mastopexia · versión ' + MASTO['version'] + ' · ' +
      str(len(MASTO['medicamentos'])) + ' renglones, ' +
      str(len(MASTO['alarma'])) + ' signos de alarma')
print('catálogo de recetas  ' + cat['version'] + ' · ' +
      str(len(cat['plantillas'])) + ' plantillas')
