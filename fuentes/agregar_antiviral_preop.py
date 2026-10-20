#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EL ANTIVIRAL DEL LÁSER, EN LA HOJA PREOPERATORIA
=================================================

Por qué aquí
------------
La profilaxis antiviral del láser de CO₂ empieza el día ANTES del
procedimiento. Eso significa que la receta tiene que estar en manos de la
paciente desde la cita de valoración, no el día del láser. Puesto sólo en la
hoja postoperatoria y en la receta, la instrucción llega tarde por diseño: la
paciente la lee cuando ya se la hicieron.

Así que entra en dos lugares de la hoja de recomendaciones preoperatorias:

  · "Antes de empezar" — para que la vea al recibir la hoja y pueda comprar el
    medicamento con tiempo.
  · "Un día antes" — que es el momento exacto de la primera dosis, junto al
    renglón del amlodipino, que ya funciona igual.

Va escrito como condición ("si su procedimiento incluye láser de CO₂") porque
esta hoja es la misma para todas las cirugías, y las hojas no tienen reglas:
lo que decide es la frase, no el programa.

Uso:  python3 agregar_antiviral_preop.py [indicaciones.json]
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'

# LA CONDICIÓN SE LEE EN LA RECETA, NO EN LA CABEZA DE LA PACIENTE.
#
# Decía «si su procedimiento incluye láser de CO₂…», y el médico lo corrigió:
# «eso suena a que el paciente debe decidir; simplemente si va en las recetas
# que lo tome, si no, pues no».
#
# Tiene razón y es más que estilo. Una paciente no sabe si lo que le van a
# hacer «incluye láser de CO₂» ni si su cirugía «lleva incisión»; le pusimos
# una decisión clínica disfrazada de instrucción. La regla verdadera es la
# receta: lo que está escrito ahí se toma, lo que no, no. Eso lo puede
# verificar cualquiera, de un vistazo y sin equivocarse.
ANTES = ('Si en sus recetas viene un antiviral, cómprelo en cuanto se las '
         'entreguemos: se empieza el día ANTES del procedimiento, no el mismo '
         'día.')

UN_DIA = ('Si en sus recetas viene un antiviral, hoy empieza. Es la dosis que '
          'más importa de todo el tratamiento: sirve para evitar que brote '
          'herpes sobre la piel tratada con láser. Si no lo consiguió o se le '
          'olvidó, avísenos hoy mismo.')

cat = json.load(open(RUTA, encoding='utf-8'))
h = [x for x in cat['hojas'] if x['id'] == 'preoperatorias'][0]

if ANTES in json.dumps(h, ensure_ascii=False):
    raise SystemExit('ya estaba puesto; no se duplica')


def lista_tras(titulo):
    """La primera lista que sigue a un encabezado dado."""
    visto = False
    for b in h['bloques']:
        if b['t'] in ('h', 'h2'):
            visto = (b.get('x') == titulo)
        elif visto and b['t'] == 'ul':
            return b
    raise SystemExit('no encontré la lista de «' + titulo + '»')


lista_tras('Antes de empezar')['x'].append(ANTES)

# En "Un día antes" va junto al amlodipino, que es el otro medicamento que se
# toma la víspera: los dos renglones se leen de corrido.
ul = lista_tras('Un día antes')
i = next((k for k, x in enumerate(ul['x']) if x.startswith('Si le entregamos amlodipino')), -1)
ul['x'].insert(i + 1 if i >= 0 else len(ul['x']), UN_DIA)

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

print('preoperatorias  ' + antes + ' -> ' + h['version'])
print('catálogo        ' + cat['version'])
