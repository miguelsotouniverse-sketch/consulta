#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EL GRUPO DE WHATSAPP YA NO EXISTE: AHORA ES UN NÚMERO
======================================================

Qué pasó
--------
Las hojas mandaban a la paciente a reportar su presión «en el grupo de
WhatsApp de seguimiento». Ese grupo ya no existe: el seguimiento
postoperatorio es ahora uno a uno, por WhatsApp, al 55 7215 5958 (confirmado
por el médico el 28-oct-2026).

Por qué importa más de lo que parece
------------------------------------
Esa frase no es decorativa: es a donde se manda una sistólica de 145 o de 85
a las tres de la mañana. Una paciente que busca un grupo que ya no existe no
reporta nada, y el dato que sirve para decidir si se suspende el metoprolol
no llega a nadie.

Y acababa de multiplicarse: el apartado de toma de presión en casa se copió
a las ocho hojas de alta, así que la frase vieja pasó de tres hojas a ocho.
Se corrige en todas de una sola pasada.

Dónde estaba
------------
Once renglones, dos frases distintas, en ocho hojas. Ni en las recetas ni en
el código de la aplicación aparecía.

Uso:  python3 corregir_whatsapp_seguimiento.py [indicaciones.json]
      (al final de la cadena, después de agregar_rescates_presion_ansiedad.py,
       que es el que reparte el apartado de la presión a las ocho hojas)
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'

WHATSAPP = '55 7215 5958'       # confirmado por el médico (28-oct-2026)

CAMBIOS = [
    ('Reporte de inmediato en el grupo de WhatsApp de seguimiento si la '
     'presión sistólica (el número de arriba) es mayor de 130 o menor de 90 mmHg.',

     'Reporte de inmediato por WhatsApp al ' + WHATSAPP + ' —seguimiento '
     'postoperatorio— si la presión sistólica (el número de arriba) es mayor '
     'de 130 o menor de 90 mmHg.'),

    ('Presión sistólica mayor de 130 o menor de 90 mmHg (repórtela en el grupo '
     'de WhatsApp de seguimiento).',

     'Presión sistólica mayor de 130 o menor de 90 mmHg (repórtela por WhatsApp '
     'al ' + WHATSAPP + ', seguimiento postoperatorio).'),
]

cat = json.load(open(RUTA, encoding='utf-8'))

# El número también queda como dato del catálogo, no sólo dentro del texto.
# De ahí lo toma el cuadro de arriba de cada hoja impresa, donde antes se
# repetía el teléfono de urgencias que ya viene en el membrete.
#
# Por qué aquí y no en las constantes del consultorio, que es donde viven los
# teléfonos: las constantes se sirven desde Drive y cambiarlas obliga a
# reemplazar un archivo de 20 KB que carga la firma del médico dentro. Este
# número pertenece a las hojas de alta, viaja con ellas y se publica con
# ellas. Si algún día se agrega `seg_whatsapp` a las constantes, la hoja lo
# prefiere: el código busca primero ahí.
cat['contacto'] = {'whatsapp_seguimiento': WHATSAPP}

hechos = 0
tocadas = []
for h in cat['hojas']:
    antes_de_esta = hechos
    for b in h['bloques']:
        if b['t'] != 'ul':
            continue
        for k, x in enumerate(b['x']):
            for viejo, nuevo in CAMBIOS:
                if x == viejo:
                    b['x'][k] = nuevo
                    hechos += 1
    if hechos > antes_de_esta:
        antes = h['version']
        h['version'] = hashlib.sha256(json.dumps(
            {k: v for k, v in h.items() if k != 'version'},
            ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]
        tocadas.append(h['id'])
        print('%-18s %s -> %s  (%d renglón/es)'
              % (h['id'], antes, h['version'], hechos - antes_de_esta))

if not hechos:
    raise SystemExit('no encontré ninguna mención del grupo; ¿ya estaba hecho?')

# Red de seguridad: que no quede ni una. Si mañana alguien escribe la frase
# otra vez en un constructor, este script truena al correr la cadena.
todo = json.dumps(cat, ensure_ascii=False)
if 'grupo de WhatsApp' in todo or 'grupo de seguimiento' in todo:
    raise SystemExit('quedó viva una mención al grupo de WhatsApp')

cat['version'] = hashlib.sha256(json.dumps(
    {'hojas': cat['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

print('%d renglones corregidos en %d hojas' % (hechos, len(tocadas)))
print('catálogo  ' + cat['version'])
