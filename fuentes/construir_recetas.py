#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LAS CUATRO PLANTILLAS DE RECETA ORIGINALES
===========================================

Qué es esto
-----------
El texto de las recetas que existían antes de octubre de 2026 —Deep Plane,
Body360, blefaroplastia y rinoplastia— escrito como código en vez de como
JSON: cada medicamento con su indicación, su cantidad, su duración, la
condición que lo enciende y su horario.

**Éste es el archivo que se edita cuando hay que corregir una receta
original.** Antes había que editar `recetas.json` a mano entre miles de
renglones, sin manera de saber después por qué decía lo que decía.

Se generó con `generar_constructor_recetas.py` leyendo `recetas_base.json`:
el texto nunca se retecleó, se emitió, y se comprobó que lo que produce es
idéntico —contenido y las cuatro versiones— al archivo del que salió.

Cómo encaja en la cadena
------------------------
Es el primer paso del lado de las recetas. Sustituye al
`cp recetas_base.json recetas.json`:

    python3 fuentes/construir_indicaciones.py     ← las 10 hojas
    python3 fuentes/construir_recetas.py          ← este archivo
    python3 fuentes/corregir_drenajes.py
    ... y el resto, en el orden del README

Los constructores que vienen después —la combinada, eCO₂, mastopexia— copian
renglones de estas cuatro por índice o por nombre. Si usted cambia aquí el
paracetamol, cambia en las siete.

Uso:  python3 construir_recetas.py [salida.json]
"""

import json
import hashlib
import datetime
import sys

SALIDA = sys.argv[1] if len(sys.argv) > 1 else 'recetas.json'


def med(hoja, nombre, indicacion, cantidad, duracion,
        si=None, rescate=False, horario=None):
    """Un renglón de receta. El orden de las llaves es el del archivo original."""
    m = {'hoja': hoja, 'nombre': nombre, 'indicacion': indicacion}
    if si is not None:
        m['si'] = si
    m['cantidad'] = cantidad
    m['duracion'] = duracion
    if horario is not None:
        m['horario'] = horario
    if rescate:
        m['rescate'] = True
    return m


def al(t, si=None):
    """Un signo de alarma, con su condición si la tiene."""
    a = {'t': t}
    if si is not None:
        a['si'] = si
    return a


PLANTILLAS = [
 {
  'id': 'deep_plane',
  'nombre': 'Deep Plane Facelift',
  'coincide': ['deep plane', 'deep plain', 'ritidectomia', 'estiramiento facial', 'lifting facial', 'facelift'],
  'procedimiento': 'Ritidectomía Deep Plane',
  'procedimientoBichat': 'Ritidectomía Deep Plane, y lipectomía de bolas de Bichat por '
                        'vía intraoral',
  'preguntas': [
   {'id': 'bichat', 'etiqueta': 'Bichat intraoral', 'tipo': 'sino', 'obligatoria': True, 'ayuda': 'Decide el enjuague bucal y el texto del procedimiento. El antibiótico oral va en los dos casos.'},
   {'id': 'blefaro', 'etiqueta': 'Blefaroplastia en el mismo tiempo quirúrgico', 'tipo': 'sino', 'obligatoria': True, 'ayuda': 'Decide el lubricante ocular y los signos de alarma del ojo.'},
   {'id': 'peni', 'etiqueta': 'Alergia a penicilina', 'tipo': 'lista', 'obligatoria': True, 'opciones': [['no', 'No alérgica'], ['leve', 'Leve — rash sin datos de gravedad'], ['grave', 'Grave — anafilaxia, angioedema, broncoespasmo o Stevens-Johnson']]},
   {'id': 'sulfa', 'etiqueta': 'Alergia a sulfonamidas', 'tipo': 'sino', 'obligatoria': True, 'ayuda': 'Si es sí, el celecoxib queda contraindicado.'},
   {'id': 'otras', 'etiqueta': 'Otras alergias', 'tipo': 'texto'},
   {'id': 'renal', 'etiqueta': 'Función renal disminuida', 'tipo': 'sino', 'obligatoria': True, 'ayuda': 'Cambia el celecoxib de cada 12 a cada 24 horas.'},
   {'id': 'isrs', 'etiqueta': 'Toma ISRS / IRSN', 'tipo': 'casilla'},
   {'id': 'sintram', 'etiqueta': 'Omitir tramadol', 'tipo': 'casilla', 'ayuda': 'Por omisión SÍ se imprime, para que la paciente la tenga en casa si la necesita y no tenga que regresar por ella.'},
  ],
  'medicamentos': [
   med('antibiotico',
       'Amoxicilina / ácido clavulánico 875/125 mg, tabletas.',
       'Tomar 1 tableta vía oral cada 12 horas, con alimentos, durante '
           '5 días.',
       cantidad='10 tabletas',
       duracion='5 días',
       si={'peni': ['no']},
       horario={'n': 'Amoxicilina / clavulanato', 'h': ['09:00', '21:00']},
   ),
   med('antibiotico',
       'Clindamicina 300 mg, cápsulas.',
       'Tomar 1 cápsula vía oral cada 8 horas, con un vaso completo de '
           'agua, durante 5 días. Si presenta diarrea frecuente o con '
           'moco, avise.',
       cantidad='15 cápsulas',
       duracion='5 días',
       si={'peni': ['leve', 'grave']},
       horario={'n': 'Clindamicina', 'h': ['06:00', '14:00', '22:00']},
   ),
   med('antibiotico',
       'Clorhexidina 0.12 %, solución bucal.',
       'Enjuagar 15 mL durante 30 segundos después de cada comida, 3 '
           'veces al día, durante 7 días. No tragar. No comer ni beber en '
           'los 30 minutos siguientes.',
       cantidad='1 frasco',
       duracion='7 días',
       si={'bichat': True},
       horario={'n': 'Clorhexidina (enjuague)', 't': 'Después de desayuno, comida y cena'},
   ),
   med('general',
       'Hipromelosa 5 mg/mL (0.5 %), solución oftálmica estéril.',
       'Instilar 2 gotas en cada ojo cada 2 horas mientras esté '
           'despierta, durante 14 días. No toque el gotero con el ojo ni '
           'con los dedos.',
       cantidad='2 frascos de 15 mL',
       duracion='14 días',
       si={'blefaro': True},
       horario={'n': 'Hipromelosa (gotas)', 't': 'Cada 2 horas mientras esté despierta'},
   ),
   med('general',
       'Paracetamol 500 mg, tabletas.',
       'Tomar 2 tabletas (1 g) vía oral cada 8 horas durante 14 días. '
           'No tome otros productos que contengan paracetamol.',
       cantidad='84 tabletas',
       duracion='14 días',
       horario={'n': 'Paracetamol', 'h': ['08:00', '16:00', '24:00']},
   ),
   med('general',
       'Celecoxib 200 mg, cápsulas.',
       'Tomar 1 cápsula vía oral cada 12 horas, con alimentos, durante '
           '14 días.',
       cantidad='28 cápsulas',
       duracion='14 días',
       si={'sulfa': False, 'c24': False},
       horario={'n': 'Celecoxib', 'h': ['12:00', '20:00']},
   ),
   med('general',
       'Celecoxib 200 mg, cápsulas.',
       'Tomar 1 cápsula vía oral cada 24 horas, con alimentos, durante '
           '14 días.',
       cantidad='14 cápsulas',
       duracion='14 días',
       si={'sulfa': False, 'c24': True},
       horario={'n': 'Celecoxib', 'h': ['14:00']},
   ),
   med('general',
       'Ketorolaco 10 mg, tabletas.',
       'Tomar 1 tableta vía oral cada 8 horas, con alimentos, '
           'alternando con el paracetamol, durante 5 días. No tomar más de '
           '5 días.',
       cantidad='15 tabletas',
       duracion='5 días',
       si={'sulfa': True},
       horario={'n': 'Ketorolaco', 'h': ['12:00', '20:00', '04:00*']},
   ),
   med('general',
       'Pantoprazol 40 mg, tabletas.',
       'Tomar 1 tableta en ayunas, 30 minutos antes del desayuno, cada '
           '24 horas durante {diasPPI} días.',
       cantidad='{diasPPI} tabletas',
       duracion='{diasPPI} días',
       horario={'n': 'Pantoprazol', 'h': ['07:00']},
   ),
   med('controlado',
       'Tramadol 50 mg, cápsulas.',
       'Tomar 1 cápsula cada 8 horas solo si hay dolor intenso que no '
           'cede con lo anterior. Máximo 3 al día. No maneje ni tome '
           'alcohol mientras lo use.',
       cantidad='9 cápsulas',
       duracion='3 días',
       si={'sintram': False},
       rescate=True,
   ),
   med('general',
       'Ondansetrón 8 mg, tabletas.',
       'Tomar 1 tableta cada 8 horas solo si hay náusea o vómito.',
       cantidad='10 tabletas',
       duracion='Según necesidad',
       rescate=True,
   ),
   med('general',
       'Polietilenglicol 3350, sobres de 17 g.',
       'Disolver 1 sobre en un vaso de agua (240 mL) cada 24 horas '
           'durante 7 días, o mientras tome tramadol. Suspender si las '
           'evacuaciones son blandas.',
       cantidad='7 sobres',
       duracion='7 días',
       horario={'n': 'Polietilenglicol', 'h': ['09:00']},
   ),
   med('general',
       'Senósidos A-B 8.6 mg, tabletas.',
       'Tomar 2 tabletas por la noche solo si no ha evacuado en 48 '
           'horas.',
       cantidad='20 tabletas',
       duracion='Según necesidad',
       rescate=True,
   ),
  ],
  'profilaxis': [
   {'si': {'peni': ['grave']}, 'texto': 'Clindamicina 900 mg IV'},
   {'si': {'bichat': True, 'peni': ['leve']}, 'texto': 'Cefazolina 2 g IV + metronidazol 500 mg IV'},
   {'si': {'bichat': True, 'peni': ['no']}, 'texto': 'Ampicilina/sulbactam 3 g IV'},
   {'si': {}, 'texto': 'Cefazolina 2 g IV'},
  ],
  'profilaxisNota': 'Repetir si la cirugía pasa de 4 h (cefazolina, '
                    'ampicilina/sulbactam) o de 6 h (clindamicina).',
  'avisos': [
   {'si': {'bichat': False}, 'tono': '', 'texto': 'Sin Bichat: lleva antibiótico oral igual, pero no lleva clorhexidina — el enjuague es para la incisión intraoral.'},
   {'si': {'c24': True}, 'tono': '', 'texto': 'Celecoxib cada 24 horas por edad ≥ 65 años o función renal disminuida.'},
   {'si': {'sulfa': True}, 'tono': 'ojo', 'texto': 'Alergia a sulfas: celecoxib contraindicado. Se usa ketorolaco, con tope de 5 días sumando lo intravenoso y lo oral.'},
   {'si': {'renal': True}, 'tono': 'malo', 'texto': 'Si la TFG es menor de 30 mL/min, quite el AINE de la receta y deje paracetamol con tramadol de rescate.'},
   {'si': {'isrs': True, 'sintram': False}, 'tono': 'malo', 'texto': 'Tramadol + ISRS/IRSN: riesgo de síndrome serotoninérgico y de convulsiones. Considere omitirlo.'},
   {'si': {'sintram': True}, 'tono': '', 'texto': 'Tramadol omitido. El dolor intenso se maneja por consulta.'},
   {'si': {'peni': ['leve']}, 'tono': '', 'texto': 'Alergia leve a penicilina: cefazolina IV aceptable (reactividad cruzada menor al 2 %). Por vía oral, clindamicina, porque la amoxicilina sí está contraindicada.'},
   {'si': {'peni': ['grave']}, 'tono': 'ojo', 'texto': 'Alergia grave a penicilina: ningún betalactámico.'},
   {'si': {'menor': True}, 'tono': 'ojo', 'texto': 'Paciente menor de 18 años: revise todas las dosis.'},
  ],
  'alarma': [
   al('Pérdida o disminución repentina de la visión, o visión doble '
       'que no se quita al parpadear.',
      si={'blefaro': True}),
   al('Dolor intenso en un ojo, que no mejora y va en aumento.',
      si={'blefaro': True}),
   al('Aumento rápido de volumen, dolor intenso o moretón que crece '
       'en un solo lado de la cara o del cuello.'),
   al('Dificultad para respirar o tragar.'),
   al('Sangrado que no cede con presión.'),
   al('Fiebre mayor de 38 °C.'),
   al('Piel de la cara que se pone oscura o morada.'),
   al('Salida de pus por las heridas.'),
   al('Mal sabor persistente o salida de pus dentro de la boca.',
      si={'bichat': True}),
  ],
  'horaNota': 'Si la paciente está dormida, no la despierten: que tome esa '
               'dosis al despertar y continúe el horario.',
 },
 {
  'id': 'body360',
  'nombre': 'Body360 / Lipoescultura',
  'coincide': ['lipoescultura', 'lipo escultura', 'liposuccion', 'body360', 'body 360', 'ribxcar'],
  'procedimiento': 'Lipoescultura Body360®',
  'preguntas': [
   {'id': 'peni', 'etiqueta': 'Alergia a penicilina', 'tipo': 'lista', 'obligatoria': True, 'opciones': [['no', 'No alérgica'], ['leve', 'Leve — rash sin datos de gravedad'], ['grave', 'Grave — anafilaxia, angioedema, broncoespasmo o Stevens-Johnson']]},
   {'id': 'sulfa', 'etiqueta': 'Alergia a sulfonamidas', 'tipo': 'sino', 'obligatoria': True, 'ayuda': 'Si es sí, el celecoxib queda contraindicado.'},
   {'id': 'otras', 'etiqueta': 'Otras alergias', 'tipo': 'texto'},
   {'id': 'renal', 'etiqueta': 'Función renal disminuida', 'tipo': 'sino', 'obligatoria': True, 'ayuda': 'Cambia el celecoxib de cada 12 a cada 24 horas.'},
   {'id': 'isrs', 'etiqueta': 'Toma ISRS / IRSN', 'tipo': 'casilla'},
   {'id': 'sintram', 'etiqueta': 'Omitir tramadol', 'tipo': 'casilla', 'ayuda': 'Por omisión SÍ se imprime, para que la paciente la tenga en casa si la necesita y no tenga que regresar por ella.'},
  ],
  'medicamentos': [
   med('antibiotico',
       'Amoxicilina / ácido clavulánico 875/125 mg, tabletas.',
       'Tomar 1 tableta vía oral cada 12 horas, con alimentos, durante '
           '5 días.',
       cantidad='10 tabletas',
       duracion='5 días',
       si={'peni': ['no']},
       horario={'n': 'Amoxicilina / clavulanato', 'h': ['09:00', '21:00']},
   ),
   med('antibiotico',
       'Clindamicina 300 mg, cápsulas.',
       'Tomar 1 cápsula vía oral cada 8 horas, con un vaso completo de '
           'agua, durante 5 días. Si presenta diarrea frecuente o con '
           'moco, avise.',
       cantidad='15 cápsulas',
       duracion='5 días',
       si={'peni': ['leve', 'grave']},
       horario={'n': 'Clindamicina', 'h': ['06:00', '14:00', '22:00']},
   ),
   med('general',
       'Rivaroxabán 10 mg, tabletas.',
       'Tomar 1 tableta vía oral cada 24 horas durante 10 días, a la '
           'misma hora. No la suspenda por su cuenta ni tome aspirina ni '
           'antiinflamatorios que no estén en esta receta.',
       cantidad='10 tabletas',
       duracion='10 días',
       horario={'n': 'Rivaroxabán', 'h': ['08:00']},
   ),
   med('general',
       'Paracetamol 500 mg, tabletas.',
       'Tomar 2 tabletas (1 g) vía oral cada 8 horas durante 14 días. '
           'No tome otros productos que contengan paracetamol.',
       cantidad='84 tabletas',
       duracion='14 días',
       horario={'n': 'Paracetamol', 'h': ['08:00', '16:00', '24:00']},
   ),
   med('general',
       'Celecoxib 200 mg, cápsulas.',
       'Tomar 1 cápsula vía oral cada 12 horas, con alimentos, durante '
           '14 días.',
       cantidad='28 cápsulas',
       duracion='14 días',
       si={'sulfa': False, 'c24': False},
       horario={'n': 'Celecoxib', 'h': ['12:00', '20:00']},
   ),
   med('general',
       'Celecoxib 200 mg, cápsulas.',
       'Tomar 1 cápsula vía oral cada 24 horas, con alimentos, durante '
           '14 días.',
       cantidad='14 cápsulas',
       duracion='14 días',
       si={'sulfa': False, 'c24': True},
       horario={'n': 'Celecoxib', 'h': ['14:00']},
   ),
   med('general',
       'Ketorolaco 10 mg, tabletas.',
       'Tomar 1 tableta vía oral cada 8 horas, con alimentos, '
           'alternando con el paracetamol, durante 5 días. No tomar más de '
           '5 días.',
       cantidad='15 tabletas',
       duracion='5 días',
       si={'sulfa': True},
       horario={'n': 'Ketorolaco', 'h': ['12:00', '20:00', '04:00*']},
   ),
   med('general',
       'Pantoprazol 40 mg, tabletas.',
       'Tomar 1 tableta en ayunas, 30 minutos antes del desayuno, cada '
           '24 horas durante {diasPPI} días.',
       cantidad='{diasPPI} tabletas',
       duracion='{diasPPI} días',
       horario={'n': 'Pantoprazol', 'h': ['07:00']},
   ),
   med('controlado',
       'Tramadol 50 mg, cápsulas.',
       'Tomar 1 cápsula cada 8 horas solo si hay dolor intenso que no '
           'cede con lo anterior. Máximo 3 al día. No maneje ni tome '
           'alcohol mientras lo use.',
       cantidad='9 cápsulas',
       duracion='3 días',
       si={'sintram': False},
       rescate=True,
   ),
   med('general',
       'Ondansetrón 8 mg, tabletas.',
       'Tomar 1 tableta cada 8 horas solo si hay náusea o vómito.',
       cantidad='10 tabletas',
       duracion='Según necesidad',
       rescate=True,
   ),
   med('general',
       'Polietilenglicol 3350, sobres de 17 g.',
       'Disolver 1 sobre en un vaso de agua (240 mL) cada 24 horas '
           'durante 7 días, o mientras tome tramadol. Suspender si las '
           'evacuaciones son blandas.',
       cantidad='7 sobres',
       duracion='7 días',
       horario={'n': 'Polietilenglicol', 'h': ['09:00']},
   ),
   med('general',
       'Senósidos A-B 8.6 mg, tabletas.',
       'Tomar 2 tabletas por la noche solo si no ha evacuado en 48 '
           'horas.',
       cantidad='20 tabletas',
       duracion='Según necesidad',
       rescate=True,
   ),
  ],
  'profilaxis': [
   {'si': {'peni': ['grave']}, 'texto': 'Clindamicina 900 mg IV'},
   {'si': {}, 'texto': 'Cefazolina 2 g IV'},
  ],
  'profilaxisNota': 'Repetir si la cirugía pasa de 4 h (cefazolina, '
                    'ampicilina/sulbactam) o de 6 h (clindamicina).',
  'avisos': [
   {'si': {}, 'tono': 'ojo', 'texto': 'Esta receta lleva rivaroxabán junto con un AINE durante 14 días. La ficha técnica autorizada pide usarlos juntos sólo si el beneficio supera el riesgo de sangrado.'},
   {'si': {'sulfa': True}, 'tono': 'malo', 'texto': 'Alergia a sulfas: la receta cambia celecoxib por ketorolaco, y el ketorolaco está contraindicado en hemostasia incompleta y diátesis hemorrágica. Con rivaroxabán encima, reconsidere el AINE.'},
   {'si': {'renal': True}, 'tono': 'malo', 'texto': 'El rivaroxabán se elimina por vía renal. Verifique la depuración antes de recetarlo: por debajo de 30 mL/min su uso es desaconsejado y por debajo de 15 no debe usarse.'},
   {'si': {'c24': True}, 'tono': '', 'texto': 'Celecoxib cada 24 horas por edad ≥ 65 años o función renal disminuida.'},
   {'si': {'sulfa': True}, 'tono': 'ojo', 'texto': 'Alergia a sulfas: celecoxib contraindicado. Se usa ketorolaco, con tope de 5 días sumando lo intravenoso y lo oral.'},
   {'si': {'renal': True}, 'tono': 'malo', 'texto': 'Si la TFG es menor de 30 mL/min, quite el AINE de la receta y deje paracetamol con tramadol de rescate.'},
   {'si': {'isrs': True, 'sintram': False}, 'tono': 'malo', 'texto': 'Tramadol + ISRS/IRSN: riesgo de síndrome serotoninérgico y de convulsiones. Considere omitirlo.'},
   {'si': {'sintram': True}, 'tono': '', 'texto': 'Tramadol omitido. El dolor intenso se maneja por consulta.'},
   {'si': {'peni': ['leve']}, 'tono': '', 'texto': 'Alergia leve a penicilina: cefazolina IV aceptable (reactividad cruzada menor al 2 %). Por vía oral, clindamicina, porque la amoxicilina sí está contraindicada.'},
   {'si': {'peni': ['grave']}, 'tono': 'ojo', 'texto': 'Alergia grave a penicilina: ningún betalactámico.'},
   {'si': {'menor': True}, 'tono': 'ojo', 'texto': 'Paciente menor de 18 años: revise todas las dosis.'},
  ],
  'alarma': [
   al('Falta de aire, dolor en el pecho, tos con sangre o sensación '
       'de que el corazón late muy rápido.'),
   al('Dolor, hinchazón o calor en una sola pantorrilla o pierna.'),
   al('Sangrado que no para, sangre en la orina o en las '
       'evacuaciones, moretones que aparecen solos o encías que '
       'sangran: está tomando un anticoagulante.'),
   al('Sangrado rojo brillante que empapa gasas o toallas en menos de '
       '1 hora.'),
   al('Una zona que crece rápido, se pone tensa y muy dolorosa, o que '
       'se siente como bolsa de líquido.'),
   al('Fiebre de 38 °C o más.'),
   al('Enrojecimiento que se extiende, calor, pus o mal olor en una '
       'incisión.'),
   al('Piel que se torna oscura, morada intensa o negra, o ampollas.'),
   al('Mareo persistente, palidez marcada u orina muy escasa.'),
  ],
  'horaNota': 'Si la paciente está dormida, no la despierten: que tome esa '
               'dosis al despertar y continúe el horario.',
 },
 {
  'id': 'blefaroplastia',
  'nombre': 'Blefaroplastia',
  'coincide': ['blefaroplastia', 'blefaro', 'cirugia de parpados'],
  'procedimiento': 'Blefaroplastia',
  'preguntas': [
   {'id': 'peni', 'etiqueta': 'Alergia a penicilina', 'tipo': 'lista', 'obligatoria': True, 'opciones': [['no', 'No alérgica'], ['leve', 'Leve — rash sin datos de gravedad'], ['grave', 'Grave — anafilaxia, angioedema, broncoespasmo o Stevens-Johnson']]},
   {'id': 'sulfa', 'etiqueta': 'Alergia a sulfonamidas', 'tipo': 'sino', 'obligatoria': True, 'ayuda': 'Si es sí, el celecoxib queda contraindicado.'},
   {'id': 'otras', 'etiqueta': 'Otras alergias', 'tipo': 'texto'},
   {'id': 'renal', 'etiqueta': 'Función renal disminuida', 'tipo': 'sino', 'obligatoria': True, 'ayuda': 'Cambia el celecoxib de cada 12 a cada 24 horas.'},
   {'id': 'isrs', 'etiqueta': 'Toma ISRS / IRSN', 'tipo': 'casilla'},
   {'id': 'sintram', 'etiqueta': 'Omitir tramadol', 'tipo': 'casilla', 'ayuda': 'Por omisión SÍ se imprime, para que la paciente la tenga en casa si la necesita y no tenga que regresar por ella.'},
  ],
  'medicamentos': [
   med('antibiotico',
       'Amoxicilina / ácido clavulánico 875/125 mg, tabletas.',
       'Tomar 1 tableta vía oral cada 12 horas, con alimentos, durante '
           '5 días.',
       cantidad='10 tabletas',
       duracion='5 días',
       si={'peni': ['no']},
       horario={'n': 'Amoxicilina / clavulanato', 'h': ['09:00', '21:00']},
   ),
   med('antibiotico',
       'Clindamicina 300 mg, cápsulas.',
       'Tomar 1 cápsula vía oral cada 8 horas, con un vaso completo de '
           'agua, durante 5 días. Si presenta diarrea frecuente o con '
           'moco, avise.',
       cantidad='15 cápsulas',
       duracion='5 días',
       si={'peni': ['leve', 'grave']},
       horario={'n': 'Clindamicina', 'h': ['06:00', '14:00', '22:00']},
   ),
   med('general',
       'Hipromelosa 5 mg/mL (0.5 %), solución oftálmica estéril.',
       'Instilar 2 gotas en cada ojo cada 2 horas mientras esté '
           'despierta, durante 14 días. No toque el gotero con el ojo ni '
           'con los dedos.',
       cantidad='2 frascos de 15 mL',
       duracion='14 días',
       horario={'n': 'Hipromelosa (gotas)', 't': 'Cada 2 horas mientras esté despierta'},
   ),
   med('general',
       'Paracetamol 500 mg, tabletas.',
       'Tomar 2 tabletas (1 g) vía oral cada 8 horas durante 14 días. '
           'No tome otros productos que contengan paracetamol.',
       cantidad='84 tabletas',
       duracion='14 días',
       horario={'n': 'Paracetamol', 'h': ['08:00', '16:00', '24:00']},
   ),
   med('general',
       'Celecoxib 200 mg, cápsulas.',
       'Tomar 1 cápsula vía oral cada 12 horas, con alimentos, durante '
           '14 días.',
       cantidad='28 cápsulas',
       duracion='14 días',
       si={'sulfa': False, 'c24': False},
       horario={'n': 'Celecoxib', 'h': ['12:00', '20:00']},
   ),
   med('general',
       'Celecoxib 200 mg, cápsulas.',
       'Tomar 1 cápsula vía oral cada 24 horas, con alimentos, durante '
           '14 días.',
       cantidad='14 cápsulas',
       duracion='14 días',
       si={'sulfa': False, 'c24': True},
       horario={'n': 'Celecoxib', 'h': ['14:00']},
   ),
   med('general',
       'Ketorolaco 10 mg, tabletas.',
       'Tomar 1 tableta vía oral cada 8 horas, con alimentos, '
           'alternando con el paracetamol, durante 5 días. No tomar más de '
           '5 días.',
       cantidad='15 tabletas',
       duracion='5 días',
       si={'sulfa': True},
       horario={'n': 'Ketorolaco', 'h': ['12:00', '20:00', '04:00*']},
   ),
   med('general',
       'Pantoprazol 40 mg, tabletas.',
       'Tomar 1 tableta en ayunas, 30 minutos antes del desayuno, cada '
           '24 horas durante {diasPPI} días.',
       cantidad='{diasPPI} tabletas',
       duracion='{diasPPI} días',
       horario={'n': 'Pantoprazol', 'h': ['07:00']},
   ),
   med('controlado',
       'Tramadol 50 mg, cápsulas.',
       'Tomar 1 cápsula cada 8 horas solo si hay dolor intenso que no '
           'cede con lo anterior. Máximo 3 al día. No maneje ni tome '
           'alcohol mientras lo use.',
       cantidad='9 cápsulas',
       duracion='3 días',
       si={'sintram': False},
       rescate=True,
   ),
   med('general',
       'Ondansetrón 8 mg, tabletas.',
       'Tomar 1 tableta cada 8 horas solo si hay náusea o vómito.',
       cantidad='10 tabletas',
       duracion='Según necesidad',
       rescate=True,
   ),
   med('general',
       'Polietilenglicol 3350, sobres de 17 g.',
       'Disolver 1 sobre en un vaso de agua (240 mL) cada 24 horas '
           'durante 7 días, o mientras tome tramadol. Suspender si las '
           'evacuaciones son blandas.',
       cantidad='7 sobres',
       duracion='7 días',
       horario={'n': 'Polietilenglicol', 'h': ['09:00']},
   ),
   med('general',
       'Senósidos A-B 8.6 mg, tabletas.',
       'Tomar 2 tabletas por la noche solo si no ha evacuado en 48 '
           'horas.',
       cantidad='20 tabletas',
       duracion='Según necesidad',
       rescate=True,
   ),
  ],
  'profilaxis': [
   {'si': {'peni': ['grave']}, 'texto': 'Clindamicina 900 mg IV'},
   {'si': {}, 'texto': 'Cefazolina 2 g IV'},
  ],
  'profilaxisNota': 'Repetir si la cirugía pasa de 4 h (cefazolina, '
                    'ampicilina/sulbactam) o de 6 h (clindamicina).',
  'avisos': [
   {'si': {'c24': True}, 'tono': '', 'texto': 'Celecoxib cada 24 horas por edad ≥ 65 años o función renal disminuida.'},
   {'si': {'sulfa': True}, 'tono': 'ojo', 'texto': 'Alergia a sulfas: celecoxib contraindicado. Se usa ketorolaco, con tope de 5 días sumando lo intravenoso y lo oral.'},
   {'si': {'renal': True}, 'tono': 'malo', 'texto': 'Si la TFG es menor de 30 mL/min, quite el AINE de la receta y deje paracetamol con tramadol de rescate.'},
   {'si': {'isrs': True, 'sintram': False}, 'tono': 'malo', 'texto': 'Tramadol + ISRS/IRSN: riesgo de síndrome serotoninérgico y de convulsiones. Considere omitirlo.'},
   {'si': {'sintram': True}, 'tono': '', 'texto': 'Tramadol omitido. El dolor intenso se maneja por consulta.'},
   {'si': {'peni': ['leve']}, 'tono': '', 'texto': 'Alergia leve a penicilina: cefazolina IV aceptable (reactividad cruzada menor al 2 %). Por vía oral, clindamicina, porque la amoxicilina sí está contraindicada.'},
   {'si': {'peni': ['grave']}, 'tono': 'ojo', 'texto': 'Alergia grave a penicilina: ningún betalactámico.'},
   {'si': {'menor': True}, 'tono': 'ojo', 'texto': 'Paciente menor de 18 años: revise todas las dosis.'},
  ],
  'alarma': [
   al('Pérdida o disminución repentina de la visión, o visión doble '
       'que no se quita al parpadear.'),
   al('Dolor intenso en un ojo, que no mejora y va en aumento.'),
   al('Un ojo que se abulta o se sale hacia adelante, con el párpado '
       'muy tenso, duro y morado.'),
   al('Sangrado que no se detiene después de 10 minutos de presión '
       'suave con una gasa.'),
   al('Fiebre de 38 °C o más.'),
   al('Enrojecimiento que se extiende, calor, pus o mal olor en una '
       'herida.'),
   al('Una herida que se abre.'),
   al('Secreción amarilla o verde en el ojo, o ojo rojo con dolor.'),
   al('Inflamación que aumenta después del día 3 en lugar de bajar.'),
   al('Incapacidad para cerrar el ojo que no mejora, con ardor intenso.'),
  ],
  'horaNota': 'Si la paciente está dormida, no la despierten: que tome esa '
               'dosis al despertar y continúe el horario.',
 },
 {
  'id': 'rinoplastia',
  'nombre': 'Rinoplastia',
  'coincide': ['rinoplastia', 'septorrinoplastia', 'rinoseptoplastia'],
  'procedimiento': 'Rinoplastia ultrasónica',
  'preguntas': [
   {'id': 'peni', 'etiqueta': 'Alergia a penicilina', 'tipo': 'lista', 'obligatoria': True, 'opciones': [['no', 'No alérgica'], ['leve', 'Leve — rash sin datos de gravedad'], ['grave', 'Grave — anafilaxia, angioedema, broncoespasmo o Stevens-Johnson']]},
   {'id': 'sulfa', 'etiqueta': 'Alergia a sulfonamidas', 'tipo': 'sino', 'obligatoria': True, 'ayuda': 'Si es sí, el celecoxib queda contraindicado.'},
   {'id': 'otras', 'etiqueta': 'Otras alergias', 'tipo': 'texto'},
   {'id': 'renal', 'etiqueta': 'Función renal disminuida', 'tipo': 'sino', 'obligatoria': True, 'ayuda': 'Cambia el celecoxib de cada 12 a cada 24 horas.'},
   {'id': 'isrs', 'etiqueta': 'Toma ISRS / IRSN', 'tipo': 'casilla'},
   {'id': 'sintram', 'etiqueta': 'Omitir tramadol', 'tipo': 'casilla', 'ayuda': 'Por omisión SÍ se imprime, para que la paciente la tenga en casa si la necesita y no tenga que regresar por ella.'},
  ],
  'medicamentos': [
   med('antibiotico',
       'Amoxicilina / ácido clavulánico 875/125 mg, tabletas.',
       'Tomar 1 tableta vía oral cada 12 horas, con alimentos, durante '
           '5 días.',
       cantidad='10 tabletas',
       duracion='5 días',
       si={'peni': ['no']},
       horario={'n': 'Amoxicilina / clavulanato', 'h': ['09:00', '21:00']},
   ),
   med('antibiotico',
       'Clindamicina 300 mg, cápsulas.',
       'Tomar 1 cápsula vía oral cada 8 horas, con un vaso completo de '
           'agua, durante 5 días. Si presenta diarrea frecuente o con '
           'moco, avise.',
       cantidad='15 cápsulas',
       duracion='5 días',
       si={'peni': ['leve', 'grave']},
       horario={'n': 'Clindamicina', 'h': ['06:00', '14:00', '22:00']},
   ),
   med('antibiotico',
       'Bacitracina / neomicina / polimixina B, ungüento dermatológico '
           '(Nebapol® o Neosporin® dérmico), tubo de 30 g.',
       'Aplicar una capa delgada sobre las heridas 3 veces al día '
           'durante 7 días. No lo use más de 7 días. No lo introduzca en '
           'las fosas nasales.',
       cantidad='1 tubo de 30 g',
       duracion='7 días',
       horario={'n': 'Ungüento en heridas', 't': 'Mañana, tarde y noche'},
   ),
   med('general',
       'Furoato de fluticasona 27.5 µg por atomización, suspensión '
           'nasal (Avamys®), frasco con 120 atomizaciones.',
       'Aplicar 2 atomizaciones en cada fosa nasal por la noche, '
           'durante 6 meses. Resurtible 5 veces: cada frasco de 120 '
           'atomizaciones alcanza un mes.',
       cantidad='1 frasco al mes, 6 en total',
       duracion='6 meses',
       horario={'n': 'Avamys (nasal)', 'h': ['22:00']},
   ),
   med('general',
       'Oximetazolina 0.05 % (0.5 mg/mL), solución para atomización '
           'nasal, frasco de 20 mL.',
       'Aplicar 1 atomización en cada fosa nasal SOLO si hay '
           'congestión importante. NUNCA por más de 4 días seguidos: '
           'usarla más tiempo produce congestión de rebote que empeora la '
           'nariz.',
       cantidad='1 frasco de 20 mL',
       duracion='Máximo 4 días',
       rescate=True,
   ),
   med('general',
       'Paracetamol 500 mg, tabletas.',
       'Tomar 2 tabletas (1 g) vía oral cada 8 horas durante 14 días. '
           'No tome otros productos que contengan paracetamol.',
       cantidad='84 tabletas',
       duracion='14 días',
       horario={'n': 'Paracetamol', 'h': ['08:00', '16:00', '24:00']},
   ),
   med('general',
       'Celecoxib 200 mg, cápsulas.',
       'Tomar 1 cápsula vía oral cada 12 horas, con alimentos, durante '
           '14 días.',
       cantidad='28 cápsulas',
       duracion='14 días',
       si={'sulfa': False, 'c24': False},
       horario={'n': 'Celecoxib', 'h': ['12:00', '20:00']},
   ),
   med('general',
       'Celecoxib 200 mg, cápsulas.',
       'Tomar 1 cápsula vía oral cada 24 horas, con alimentos, durante '
           '14 días.',
       cantidad='14 cápsulas',
       duracion='14 días',
       si={'sulfa': False, 'c24': True},
       horario={'n': 'Celecoxib', 'h': ['14:00']},
   ),
   med('general',
       'Ketorolaco 10 mg, tabletas.',
       'Tomar 1 tableta vía oral cada 8 horas, con alimentos, '
           'alternando con el paracetamol, durante 5 días. No tomar más de '
           '5 días.',
       cantidad='15 tabletas',
       duracion='5 días',
       si={'sulfa': True},
       horario={'n': 'Ketorolaco', 'h': ['12:00', '20:00', '04:00*']},
   ),
   med('general',
       'Pantoprazol 40 mg, tabletas.',
       'Tomar 1 tableta en ayunas, 30 minutos antes del desayuno, cada '
           '24 horas durante {diasPPI} días.',
       cantidad='{diasPPI} tabletas',
       duracion='{diasPPI} días',
       horario={'n': 'Pantoprazol', 'h': ['07:00']},
   ),
   med('controlado',
       'Tramadol 50 mg, cápsulas.',
       'Tomar 1 cápsula cada 8 horas solo si hay dolor intenso que no '
           'cede con lo anterior. Máximo 3 al día. No maneje ni tome '
           'alcohol mientras lo use.',
       cantidad='9 cápsulas',
       duracion='3 días',
       si={'sintram': False},
       rescate=True,
   ),
   med('general',
       'Ondansetrón 8 mg, tabletas.',
       'Tomar 1 tableta cada 8 horas solo si hay náusea o vómito.',
       cantidad='10 tabletas',
       duracion='Según necesidad',
       rescate=True,
   ),
   med('general',
       'Polietilenglicol 3350, sobres de 17 g.',
       'Disolver 1 sobre en un vaso de agua (240 mL) cada 24 horas '
           'durante 7 días, o mientras tome tramadol. Suspender si las '
           'evacuaciones son blandas.',
       cantidad='7 sobres',
       duracion='7 días',
       horario={'n': 'Polietilenglicol', 'h': ['09:00']},
   ),
   med('general',
       'Senósidos A-B 8.6 mg, tabletas.',
       'Tomar 2 tabletas por la noche solo si no ha evacuado en 48 '
           'horas.',
       cantidad='20 tabletas',
       duracion='Según necesidad',
       rescate=True,
   ),
  ],
  'profilaxis': [
   {'si': {'peni': ['grave']}, 'texto': 'Clindamicina 900 mg IV'},
   {'si': {}, 'texto': 'Cefazolina 2 g IV'},
  ],
  'profilaxisNota': 'Repetir si la cirugía pasa de 4 h (cefazolina, '
                    'ampicilina/sulbactam) o de 6 h (clindamicina).',
  'avisos': [
   {'si': {}, 'tono': '', 'texto': 'La oximetazolina va como rescate y con tope de 4 días. La ficha técnica de Afrin dice 3 y la de Iliadin oscila entre 3 y 7; el tope de esta receta es el que usted indicó.'},
   {'si': {}, 'tono': '', 'texto': 'Avamys: la dosis de 2 atomizaciones por fosa es la de inicio. La ficha autorizada permite bajar a 1 por fosa cuando los síntomas estén controlados; si lo decide en consulta, edite el renglón.'},
   {'si': {'c24': True}, 'tono': '', 'texto': 'Celecoxib cada 24 horas por edad ≥ 65 años o función renal disminuida.'},
   {'si': {'sulfa': True}, 'tono': 'ojo', 'texto': 'Alergia a sulfas: celecoxib contraindicado. Se usa ketorolaco, con tope de 5 días sumando lo intravenoso y lo oral.'},
   {'si': {'renal': True}, 'tono': 'malo', 'texto': 'Si la TFG es menor de 30 mL/min, quite el AINE de la receta y deje paracetamol con tramadol de rescate.'},
   {'si': {'isrs': True, 'sintram': False}, 'tono': 'malo', 'texto': 'Tramadol + ISRS/IRSN: riesgo de síndrome serotoninérgico y de convulsiones. Considere omitirlo.'},
   {'si': {'sintram': True}, 'tono': '', 'texto': 'Tramadol omitido. El dolor intenso se maneja por consulta.'},
   {'si': {'peni': ['leve']}, 'tono': '', 'texto': 'Alergia leve a penicilina: cefazolina IV aceptable (reactividad cruzada menor al 2 %). Por vía oral, clindamicina, porque la amoxicilina sí está contraindicada.'},
   {'si': {'peni': ['grave']}, 'tono': 'ojo', 'texto': 'Alergia grave a penicilina: ningún betalactámico.'},
   {'si': {'menor': True}, 'tono': 'ojo', 'texto': 'Paciente menor de 18 años: revise todas las dosis.'},
  ],
  'alarma': [
   al('Sangrado rojo brillante por la nariz o por la garganta que no '
       'se detiene después de 15 minutos sentada, con la cabeza '
       'ligeramente hacia adelante.'),
   al('Golpe fuerte en la nariz.'),
   al('Pérdida o disminución repentina de la visión.'),
   al('Falta de aire, dolor en el pecho o desmayo.'),
   al('Fiebre de 38 °C o más.'),
   al('Dolor que empeora en lugar de mejorar.'),
   al('Enrojecimiento que se extiende, calor, pus o mal olor en la '
       'nariz o en la herida.'),
   al('Salida abundante de líquido claro y aguado por la nariz, sobre '
       'todo al inclinarse hacia adelante.'),
   al('Piel de la nariz que se torna oscura, morada o con ampollas '
       'bajo la férula.'),
   al('Férula que se despega o se mueve.'),
  ],
  'horaNota': 'Si la paciente está dormida, no la despierten: que tome esa '
               'dosis al despertar y continúe el horario.',
 },
]

HOJAS = [{'id': 'antibiotico', 'titulo': 'Receta — antibiótico', 'nota': 'La farmacia retiene esta receta al surtir la cantidad completa (Acuerdo DOF 27-V-2010). Por eso va separada de las demás.', 'paraPaciente': 'Esta hoja se queda en la farmacia. Las otras son suyas.'}, {'id': 'controlado', 'titulo': 'Receta — medicamento controlado', 'nota': 'Tramadol: artículo 226 fracción III de la Ley General de Salud desde el 14 de julio de 2026. Hasta 3 surtidos, vigencia 6 meses, la farmacia lo registra en sus libros de control.', 'paraPaciente': 'Consérvela. Solo la use si la necesita.'}, {'id': 'general', 'titulo': 'Receta', 'nota': '', 'alarma': True, 'paraPaciente': 'Consérvela hasta terminar el tratamiento.'}]

HORAS = ['04:00', '06:00', '07:00', '08:00', '09:00', '12:00', '14:00', '16:00', '20:00', '21:00', '22:00', '24:00']


for _p in PLANTILLAS:
    _p['version'] = hashlib.sha256(json.dumps(
        _p, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

_cat = {
    'plantillas': PLANTILLAS,
    'hojas': HOJAS,
    'horas': HORAS,
    'version': hashlib.sha256(json.dumps(
        {'plantillas': PLANTILLAS, 'hojas': HOJAS, 'horas': HORAS},
        ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16],
    'generado': datetime.date.today().isoformat(),
}

with open(SALIDA, 'w', encoding='utf-8') as _f:
    json.dump(_cat, _f, ensure_ascii=False, indent=1)

print('%d plantillas  ·  catalogo %s' % (len(PLANTILLAS), _cat['version']))
for _p in PLANTILLAS:
    print('   %-16s %s  (%d renglones)' % (_p['id'], _p['version'],
                                            len(_p['medicamentos'])))
