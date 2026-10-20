#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LOS MEDICAMENTOS LOS COMPRA LA PACIENTE, NO SE LOS DAMOS
=========================================================

Qué decía y por qué importa
---------------------------
La hoja de recomendaciones preoperatorias afirmaba, con todas sus letras:

    «Los medicamentos de su cirugía se los entregamos nosotros, junto con sus
     indicaciones para después de la cirugía: no necesita comprar nada.»

Y más abajo pedía dejar listo «un lugar a la mano junto a su cama para los
medicamentos que le entregaremos».

No es cierto. El médico lo señaló textual: «eso es mentira».

Esto no es una imprecisión de redacción, es un daño concreto a la paciente.
Una paciente que lee esa frase NO compra nada, sale de quirófano sin
analgésico, sin antibiótico y sin antiemético en su casa, y descubre el hueco
la primera noche —que es exactamente cuando no puede ir a la farmacia y cuando
más duele—. Varios medicamentos de sus recetas se empiezan ese mismo día.

Qué dice ahora
--------------
Lo contrario y con la consecuencia explícita: usted los compra, con las
recetas que le entregamos, y los tiene en casa ANTES del día de la cirugía.
Se dice el porqué, porque una instrucción sin motivo se pospone.

El amlodipino, que se me escapó en la primera pasada
----------------------------------------------------
Decía «si le entregamos amlodipino 5 mg…». Lo di por bueno porque estaba
escrito como condición y no como promesa, y me equivoqué: el consultorio no
entrega amlodipino, entrega una RECETA de amlodipino. Son cosas distintas y la
diferencia la paga la paciente, que llega a la víspera de su cirugía sin la
tableta que debía tomar esa noche. Ahora dice «si le recetamos… cómprelo con
tiempo».

Lo que NO se tocó
-----------------
El renglón del antiviral del láser ya era correcto: decía «le entregamos la
receta del antiviral» y «cómprelo con tiempo». Siempre habló de la receta, no
del medicamento.

Uso:  python3 corregir_medicamentos_preop.py [indicaciones.json]
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'

CAMBIOS = [
    ('Los medicamentos de su cirugía se los entregamos nosotros, junto con sus '
     'indicaciones para después de la cirugía: no necesita comprar nada.',

     'Los medicamentos de su cirugía los compra usted, con las recetas que le '
     'entregamos en la valoración preoperatoria. Téngalos comprados y en casa '
     'ANTES del día del procedimiento: varios se empiezan el mismo día que sale '
     'de quirófano, y ese día usted no va a estar en condiciones de ir a la '
     'farmacia.'),

    ('Un lugar a la mano junto a su cama para los medicamentos que le entregaremos.',

     'Sus medicamentos ya comprados, en un lugar a la mano junto a su cama.'),

    # El amlodipino tampoco se entrega: se RECETA. El médico lo señaló aparte
    # («lo que les entregamos es una receta para que compren amlodipino, que es
    # totalmente diferente»), y tenía razón en que se me había escapado: lo di
    # por bueno en la primera pasada porque estaba escrito como condición, y
    # una condición falsa sigue siendo falsa.
    ('Si le entregamos amlodipino 5 mg, tome una tableta el día anterior a su '
     'cirugía, como le indicamos. Ayuda a mantener su presión estable y a '
     'reducir el sangrado y la inflamación.',

     # Ni «si le entregamos» (no se entrega) ni «si su cirugía lleva incisión»
     # (la paciente no tiene por qué saberlo). La condición es la receta.
     'Si en sus recetas viene amlodipino 5 mg, tómelo hoy: una tableta. Ayuda a '
     'mantener su presión estable durante la cirugía y a reducir el sangrado y '
     'la inflamación.'),
]

# Renglón NUEVO, que se inserta justo después del anterior.
#
# El médico describió cómo pasa de verdad: «normalmente las recetas se las
# damos en la valoración preoperatoria, pero no siempre, muchas veces no da
# tiempo y las terminamos dando el día del procedimiento».
#
# Una hoja que sólo dijera «téngalos comprados antes» le estaría pidiendo a la
# paciente algo imposible justo en los casos en que la receta llega tarde. Y
# callarlo no lo arregla: la deja descubriéndolo sola, el día de su cirugía,
# en ayunas y sin tiempo. Así que se nombra el caso y se le da salida —el
# acompañante compra mientras ella está en quirófano— que es lo que de hecho
# acaba ocurriendo, nada más que improvisado y a las prisas.
TARDE = ('Si llega el día de su cirugía y todavía no tiene sus recetas, '
         'pídanoslas al llegar: su acompañante puede comprar los medicamentos '
         'mientras usted está en quirófano, para que estén en casa cuando '
         'usted llegue. Avísele con tiempo para que vaya preparado.')

cat = json.load(open(RUTA, encoding='utf-8'))
h = [x for x in cat['hojas'] if x['id'] == 'preoperatorias'][0]

hechos = 0
for b in h['bloques']:
    if b['t'] != 'ul':
        continue
    for k, x in enumerate(b['x']):
        for viejo, nuevo in CAMBIOS:
            if x == viejo:
                b['x'][k] = nuevo
                hechos += 1

# Se inserta el renglón del caso tardío justo después del de los medicamentos.
anclaje = CAMBIOS[0][1]
puesto = False
for b in h['bloques']:
    if b['t'] != 'ul':
        continue
    for k, x in enumerate(b['x']):
        if x == anclaje and TARDE not in b['x']:
            b['x'].insert(k + 1, TARDE)
            puesto = True
            break
    if puesto:
        break
if not puesto:
    raise SystemExit('no pude insertar el renglón del caso tardío')

if hechos != len(CAMBIOS):
    raise SystemExit(
        'Esperaba ' + str(len(CAMBIOS)) + ' cambios y encontré ' + str(hechos) +
        '. El texto cambió desde que se escribió este parche; revíselo a mano '
        'antes de seguir, porque el renglón que falta puede ser el que miente.')

# Red de seguridad: que no quede NINGUNA promesa de entregar medicamentos.
todo = json.dumps(h, ensure_ascii=False)
for frase in ('no necesita comprar nada',
              'medicamentos que le entregaremos',
              'se los entregamos nosotros',
              'le entregamos amlodipino'):
    if frase in todo:
        raise SystemExit('Quedó viva la frase: «' + frase + '»')

antes = h['version']
h['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in h.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]
cat['version'] = hashlib.sha256(json.dumps(
    {'hojas': cat['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

print('preoperatorias  ' + antes + ' -> ' + h['version'] +
      '  (' + str(hechos) + ' renglones)')
print('catálogo        ' + cat['version'])
