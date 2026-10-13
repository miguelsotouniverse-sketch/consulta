#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONSTRUYE LA PLANTILLA DE RECETAS PARA LA CIRUGÍA FACIAL COMBINADA
==================================================================

Por qué
-------
Mismo problema que con las hojas de indicaciones, y peor: si a una paciente
operada de Deep Plane + blefaroplastia + rinoplastia + CO₂ se le imprimen las
tres recetas que ya existen, se lleva **tres veces** paracetamol, celecoxib,
pantoprazol, tramadol, ondansetrón, polietilenglicol y senósidos, y **tres
veces** el antibiótico. Una paciente con analgésicos encima leyendo tres hojas
con el mismo medicamento repetido es una sobredosis esperando a pasar.

Cómo se arma
------------
Las cuatro plantillas comparten el mismo esqueleto analgésico, así que la
combinada se construye por UNIÓN SIN REPETIR, tomando como base la de Deep
Plane y agregando únicamente lo que es exclusivo de cada procedimiento:

    base Deep Plane        amoxi/clavulánico o clindamicina, clorhexidina (si
                           Bichat), paracetamol, celecoxib o ketorolaco,
                           pantoprazol, tramadol, ondansetrón, laxantes
    + blefaroplastia       hipromelosa — en Deep Plane colgaba de la pregunta
                           "¿blefaro en el mismo tiempo?"; aquí la respuesta es
                           sí por definición, así que la pregunta se quita y el
                           renglón queda fijo
    + rinoplastia          ungüento de bacitracina/neomicina/polimixina,
                           Avamys, oximetazolina de rescate
    + láser CO₂            clobetasol, Cicaplast, vaselina y protector solar

Nada se escribe dos veces: los renglones se copian por índice de las plantillas
que ya están aprobadas, no se vuelven a teclear.

La pregunta de blefaroplastia desaparece — y por eso hay que tocar también los
signos de alarma: dos de ellos colgaban de `si: {blefaro: true}`, y sin esa
pregunta `cumple_()` nunca los dejaría pasar. Quedan fijos.

Lo único redactado aquí son los cuatro renglones del CO₂ y los avisos nuevos.

El límite de Clobesol
---------------------
El médico lo indicó "cada 12 horas" sin fecha de término. Clobetasol es un
esteroide de potencia muy alta y sin tope, en cara y cuello, atrofia la piel.
La receta lleva un tope de CLOBESOL_DIAS, marcado abajo para cambiarlo con una
palabra, y un aviso en pantalla que lo dice.

Uso:  python3 construir_receta_combinada.py [recetas.json]
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'recetas.json'

CLOBESOL_DIAS = 7     # confirmado por el médico (13-oct-2026)

# Profilaxis antiviral del resurfacing ablativo. El médico pidió agregarla y
# confirmó la propuesta tal cual (13-oct-2026): valaciclovir 500 mg cada 12 h
# por 10 días, empezando la víspera. Valaciclovir y no aciclovir por la
# posología: dos tomas al día en vez de cinco, que en una paciente con la cara
# en carne viva es la diferencia entre que lo tome y que no.
ANTIVIRAL_DIAS = 10   # confirmado por el médico (13-oct-2026)
ANTIVIRAL = {
    'hoja': 'general',
    'nombre': 'Valaciclovir 500 mg, tabletas.',
    'indicacion':
        'Tomar 1 tableta vía oral cada 12 horas durante '
        + str(ANTIVIRAL_DIAS) + ' días, '
        'empezando el día ANTES del procedimiento. No la suspenda aunque la piel '
        'se vea bien: sirve para evitar que brote herpes sobre la piel tratada '
        'con láser, que es la complicación más frecuente de este tratamiento.',
    'cantidad': str(ANTIVIRAL_DIAS * 2) + ' tabletas',
    'duracion': str(ANTIVIRAL_DIAS) + ' días',
    'horario': {'n': 'Valaciclovir', 'h': ['08:00', '20:00']},
}

cat = json.load(open(RUTA, encoding='utf-8'))
P = {p['id']: p for p in cat['plantillas']}
DP, RI = P['deep_plane'], P['rinoplastia']


def med(plantilla, i, **cambios):
    """Un renglón aprobado, copiado. `cambios` permite soltarle la condición."""
    m = json.loads(json.dumps(plantilla['medicamentos'][i], ensure_ascii=False))
    for k, v in cambios.items():
        if v is None:
            m.pop(k, None)
        else:
            m[k] = v
    return m


# ---------------------------------------------------------------- CO₂
CO2 = [
    ANTIVIRAL,
    {
        'hoja': 'general',
        'nombre': 'Clobetasol propionato 0.05 %, crema (Clobesol®), tubo de 30 g.',
        'indicacion':
            'Aplicar una capa delgada sobre la piel tratada con láser cada 12 '
            'horas durante ' + str(CLOBESOL_DIAS) + ' días y suspender. No lo '
            'use más días de los indicados, no lo aplique en los párpados y no '
            'lo use por su cuenta más adelante: es un esteroide de potencia muy '
            'alta y el uso prolongado adelgaza la piel de la cara.',
        'cantidad': '1 tubo de 30 g',
        'duracion': str(CLOBESOL_DIAS) + ' días',
        'horario': {'n': 'Clobesol (piel del láser)', 'h': ['08:00', '20:00']},
    },
    {
        'hoja': 'general',
        'nombre': 'Cicaplast Baume B5, bálsamo reparador, tubo de 100 mL.',
        'indicacion':
            'Aplicar una capa sobre toda la piel tratada con láser cada 12 '
            'horas, y después de cada lavado, hasta que la piel cierre por '
            'completo (7 a 10 días). Manos limpias cada vez.',
        'cantidad': '1 tubo de 100 mL',
        'duracion': 'Hasta que cierre la piel',
        'horario': {'n': 'Cicaplast', 'h': ['08:00', '20:00']},
    },
    {
        'hoja': 'general',
        'nombre': 'Vaselina sólida pura, frasco de 100 g.',
        'indicacion':
            'Aplicar encima del bálsamo las veces que haga falta para que la '
            'piel tratada nunca se sienta tirante ni se vea seca, de día y de '
            'noche. La piel no debe quedar sin nada encima ni un momento.',
        'cantidad': '1 frasco de 100 g',
        'duracion': 'Hasta que cierre la piel',
        'horario': {'n': 'Vaselina', 't': 'Las veces que haga falta'},
    },
    {
        'hoja': 'general',
        'nombre': 'Protector solar FPS 50+ de amplio espectro, para piel sensible.',
        'indicacion':
            'Aplicar en rostro y cuello todos los días EN CUANTO la piel esté '
            'completamente cerrada, reaplicando cada 3 horas si está al aire '
            'libre, durante 12 meses. Antes de que cierre, el sol se evita con '
            'sombra y gorra, no con protector.',
        'cantidad': '1 envase, resurtible',
        'duracion': '12 meses',
    },
]

# ------------------------------------------------------------ medicamentos
# El orden importa: la impresión agrupa por hoja (antibiótico, general,
# controlado) y parte la hoja general en pliegos de 7 renglones.
MEDS = [
    med(DP, 0),                     # amoxicilina / clavulánico   (si peni = no)
    med(DP, 1),                     # clindamicina                (si alergia)
    med(DP, 2),                     # clorhexidina                (si Bichat)
    med(RI, 2),                     # ungüento en heridas         — rinoplastia
    med(DP, 3, si={}),              # hipromelosa — fija: la blefaro va siempre
    med(RI, 3),                     # Avamys                      — rinoplastia
    med(RI, 4),                     # oximetazolina de rescate    — rinoplastia
] + CO2 + [
    med(DP, 4),                     # paracetamol
    med(DP, 5),                     # celecoxib c/12 h
    med(DP, 6),                     # celecoxib c/24 h
    med(DP, 7),                     # ketorolaco                  (si sulfas)
    med(DP, 8),                     # pantoprazol
    med(DP, 9),                     # tramadol                    (controlado)
    med(DP, 10),                    # ondansetrón
    med(DP, 11),                    # polietilenglicol
    med(DP, 12),                    # senósidos
]

# ----------------------------------------------------------------- avisos
AVISOS = (
    [{'si': {}, 'tono': 'ojo', 'texto':
      'Clobesol es un esteroide de potencia muy alta. Esta receta lo limita a ' +
      str(CLOBESOL_DIAS) + ' días sobre la piel tratada y lo prohíbe en los '
      'párpados. Si su protocolo es otro plazo, edite el renglón antes de '
      'imprimir.'},
     {'si': {}, 'tono': '', 'texto':
      'Plantilla combinada: la hipromelosa va fija porque la blefaroplastia '
      'forma parte de esta combinación. Si en este caso no la hizo, borre ese '
      'renglón.'}]
    + [a for a in DP['avisos']]
    + [a for a in RI['avisos'] if a['texto'] not in
       {x['texto'] for x in DP['avisos']}]
)

# ----------------------------------------------------------------- alarma
# La caja de alarma de la receta NO es el catálogo completo: es la lista de
# "cuelgue el teléfono y llame". La hoja de indicaciones ya lleva la lista
# larga, partida en «de inmediato» y «el mismo día». Pegar las dos listas
# enteras daba 20 renglones, y medido en el papel eso empujaba la última hoja
# de la receta a 983 px —por encima de los 965 utilizables—, que es
# exactamente el defecto que esta caja existe para evitar: la firma saliéndose
# a la hoja siguiente.
#
# Así que se escoge. Entra lo que puede costar un ojo, la vía aérea, una
# hemorragia o una necrosis; se quedan fuera los duplicados y lo que no es una
# urgencia (la férula que se mueve, el dolor que "empeora" sin más).
ALARMA = [
    # de la blefaroplastia: fijos, porque aquí la blefaro va siempre
    {'t': 'Pérdida o disminución repentina de la visión, o visión doble que no '
          'se quita al parpadear.'},
    {'t': 'Dolor intenso en un ojo, que no mejora y va en aumento.'},
    # del lifting
    {'t': 'Aumento rápido de volumen, dolor intenso o moretón que crece en un '
          'solo lado de la cara o del cuello.'},
    {'t': 'Dificultad para respirar o tragar.'},
    {'t': 'Sangrado que no cede con presión.'},
    {'t': 'Piel del cuello, bajo el mentón o de la cara que se pone oscura o morada.'},
    {'t': 'Fiebre mayor de 38 °C.'},
    {'t': 'Salida de pus por las heridas.'},
    {'t': 'Mal sabor persistente o salida de pus dentro de la boca.',
     'si': {'bichat': True}},
    # de la rinoplastia
    {'t': 'Sangrado rojo brillante por la nariz o por la garganta que no se '
          'detiene después de 15 minutos sentada, con la cabeza ligeramente '
          'hacia adelante.'},
    {'t': 'Golpe fuerte en la nariz.'},
    {'t': 'Salida abundante de líquido claro y aguado por la nariz, sobre todo '
          'al inclinarse hacia adelante.'},
    {'t': 'Piel de la nariz que se torna oscura, morada o con ampollas bajo la '
          'férula.'},
    # del láser
    {'t': 'Piel tratada con láser que duele más cada día, huele mal o escurre pus.'},
    # tromboembolia: cuatro procedimientos y varias horas de quirófano
    {'t': 'Falta de aire, dolor en el pecho o desmayo.'},
]

plantilla = {
    'id': 'facial_combinada',
    'nombre': 'Combinada facial — Deep Plane de cuello (contorno) + '
              'blefaroplastia 4 cuadrantes + rinoplastia + CO₂',
    # Vacío a propósito, igual que la hoja: si trajera "deep plane", un lifting
    # solo encontraría dos plantillas y se quedaría sin sugerencia.
    'coincide': [],
    'procedimiento': 'Deep Plane de cuello (contorno cervical), blefaroplastia '
                     'de 4 cuadrantes, rinoplastia ultrasónica y láser CO₂ en '
                     'rostro y cuello',
    'procedimientoBichat': 'Deep Plane de cuello (contorno cervical), '
                           'blefaroplastia de 4 cuadrantes, rinoplastia '
                           'ultrasónica, láser CO₂ en rostro y cuello, y '
                           'lipectomía de bolas de Bichat por vía intraoral',
    # Las mismas de Deep Plane menos "blefaro", que aquí es sí por definición.
    'preguntas': [q for q in DP['preguntas'] if q['id'] != 'blefaro'],
    'medicamentos': MEDS,
    'profilaxis': json.loads(json.dumps(DP['profilaxis'], ensure_ascii=False)),
    'profilaxisNota': DP['profilaxisNota'],
    'avisos': AVISOS,
    'alarma': ALARMA,
    'horaNota': DP['horaNota'],
}

plantilla['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in plantilla.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

cat['plantillas'] = [p for p in cat['plantillas'] if p['id'] != plantilla['id']]
pos = max(i for i, p in enumerate(cat['plantillas']) if p['id'] == 'rinoplastia') + 1
cat['plantillas'].insert(pos, plantilla)

cat['version'] = hashlib.sha256(json.dumps(
    {'plantillas': cat['plantillas'], 'hojas': cat['hojas'], 'horas': cat['horas']},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

print('plantilla facial_combinada · versión ' + plantilla['version'] +
      ' · ' + str(len(MEDS)) + ' renglones, ' + str(len(ALARMA)) + ' signos de alarma')
print('catálogo · versión ' + cat['version'] + ' · ' +
      str(len(cat['plantillas'])) + ' plantillas')
