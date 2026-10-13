#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA DIETA DE LA SECCIÓN DE ALIMENTACIÓN ES LA DE LA GLÁNDULA SUBMANDIBULAR
=========================================================================

Qué pasaba
----------
La hoja de Deep Plane ya traía la dieta correcta, pero sin nombrarla: el
encabezado decía sólo "Alimentación" y el texto hablaba de "la glándula salival
bajo la mandíbula". Quien lee la hoja —la paciente, su acompañante, la
enfermera que la revisa— no tiene cómo saber que eso es una indicación
quirúrgica concreta y no un consejo general de comer ligero. Se nombra.

Y en la hoja combinada había algo peor, que es culpa de la fusión: al traer los
renglones de alimentación de la rinoplastia, entró

    "Picante: evitarlo la primera semana; congestiona la nariz."

debajo de un renglón que ya prohíbe el picante 14 DÍAS por la glándula. Dos
plazos para lo mismo en la misma lista, y el más corto leído al final. Se quita
el de la rinoplastia: el de la glándula es más estricto y lo cubre.

El renglón de la sal de la blefaroplastia sí se queda, pero reescrito para que
se lea como algo que SE SUMA a la dieta de la glándula y no como una regla
alterna más suave.

Uso:  python3 corregir_dieta_submandibular.py [indicaciones.json]
      python3 construir_hoja_combinada.py [indicaciones.json]    ← después
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'

VIEJO_H2 = 'Alimentación'
NUEVO_H2 = 'Alimentación — dieta para la glándula submandibular'

VIEJO_P = ('Durante su cirugía se trató parte de la glándula salival bajo la '
           'mandíbula. Para que cicatrice bien, durante 14 días debe seguir una '
           'dieta que no estimule la saliva.')
NUEVO_P = ('Durante su cirugía se trató parte de la glándula submandibular, la '
           'glándula salival que está bajo la mandíbula. Todo lo que estimula la '
           'saliva la hace trabajar y retrasa su cicatrización, así que durante '
           '14 días la dieta es parte del tratamiento, no una recomendación.')

cat = json.load(open(RUTA, encoding='utf-8'))
dp = [h for h in cat['hojas'] if h['id'] == 'deep_plane'][0]

cambios = 0
for b in dp['bloques']:
    if b['t'] == 'h2' and b.get('x') == VIEJO_H2:
        b['x'] = NUEVO_H2
        cambios += 1
    elif b['t'] == 'p' and b.get('x') == VIEJO_P:
        b['x'] = NUEVO_P
        cambios += 1

if cambios != 2:
    raise SystemExit('Esperaba 2 cambios y encontré ' + str(cambios) +
                     '. El texto cambió; revísalo a mano antes de seguir.')

antes = dp['version']
dp['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in dp.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]
cat['version'] = hashlib.sha256(json.dumps(
    {'hojas': cat['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

print('deep_plane  ' + antes + ' -> ' + dp['version'] + '  (' + str(cambios) + ' renglones)')
print('catálogo    ' + cat['version'])
