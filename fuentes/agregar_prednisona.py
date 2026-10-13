#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA PREDNISONA QUE FALTABA EN TODAS LAS RECETAS
===============================================

El hallazgo
-----------
El médico da prednisona 20 mg durante 2 semanas en prácticamente todas sus
cirugías. No estaba en NINGUNA de las seis plantillas. No era que estuviera mal
escrita: no existía. Cada receta postoperatoria que salió del sistema salió sin
ella, y el esteroide se agregaba a mano o se quedaba en la indicación verbal.

Lo que él dijo, textual:  «practicamente todas deben tener 20 miligramos de
prednisona por 2 semanas».

Lo que escribí y lo que decidí yo
---------------------------------
Dosis, duración y universalidad son suyas. Tres cosas las decidí yo y van
dichas aquí para que las pueda revertir con una palabra:

  1. SIN REDUCCIÓN ESCALONADA. Él dijo «20 mg por 2 semanas» y nada más. Un
     esteroide a 20 mg durante 14 días se puede suspender de golpe —el eje
     suprarrenal no se frena en menos de tres semanas—, así que el renglón dice
     tomar y suspender. Si él baja escalonadamente, el renglón cambia aquí.

  2. POR LA MAÑANA Y CON ALIMENTO. No lo especificó. Es la hora habitual del
     esteroide (sigue el ritmo del cortisol y estorba menos para dormir).

  3. NO ENTRA ENCENDIDA EN LA HOJA DE LÁSER eCO₂. El láser no es una cirugía, y
     catorce días de esteroide sistémico en una paciente que sólo recibió láser
     es una decisión distinta a la de una paciente operada. Así que en esa
     plantilla el renglón va PRESENTE PERO APAGADO: se ve en la lista y se
     enciende con un clic cuando él lo quiera. En las cinco plantillas
     quirúrgicas entra encendido.

El efecto secundario que esto provocó
-------------------------------------
El protector gástrico duraba lo que durara el antiinflamatorio:
`diasPPI = sulfa ? 5 : 14`. En una paciente alérgica a sulfas el AINE es
ketorolaco por 5 días, así que el pantoprazol se iba a 5 días —y ahora el
esteroide sigue hasta el día 14 sin protección. Esa ventana la abre esta
prednisona, no existía antes. El arreglo va en index.html, no aquí, y está
marcado para que él lo confirme.

Uso:  python3 agregar_prednisona.py [recetas.json]
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'recetas.json'

# Prednisona 20 mg en tabletas existe en México (Meticorten 20 mg, Nosipren
# 20 mg, cajas de 30). Se piden 14, que es lo que dura el tratamiento; la caja
# comercial trae 30 y sobran 16, y eso es mejor que una receta por 30 tabletas
# que invite a seguir tomándolas.
PREDNISONA = {
    'hoja': 'general',
    'nombre': 'Prednisona 20 mg, tabletas.',
    'indicacion':
        'Tomar 1 tableta (20 mg) vía oral cada 24 horas, por la mañana y con '
        'alimento, durante 14 días; al terminar los 14 días se suspende. Sirve '
        'para bajar la inflamación de los tejidos operados. No la alargue ni la '
        'suspenda antes por su cuenta, y si tiene diabetes avísenos: el '
        'esteroide sube el azúcar mientras lo toma.',
    'cantidad': '14 tabletas',
    'duracion': '14 días',
    'horario': {'n': 'Prednisona', 'h': ['08:00']},
}

# Dónde entra apagada por omisión.
APAGADA_EN = {'eco2'}

cat = json.load(open(RUTA, encoding='utf-8'))
P = {p['id']: p for p in cat['plantillas']}

ya = [i for i, p in P.items()
      if any('Prednisona' in m['nombre'] for m in p['medicamentos'])]
if ya:
    raise SystemExit('ya estaba en ' + ', '.join(sorted(ya)) + '; no se duplica')


def version_de(p):
    return hashlib.sha256(json.dumps(
        {k: v for k, v in p.items() if k != 'version'},
        ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]


for pid in sorted(P):
    p = P[pid]
    fila = json.loads(json.dumps(PREDNISONA, ensure_ascii=False))
    if pid in APAGADA_EN:
        fila['fuera'] = True

    # Va justo antes del protector gástrico: el orden de lectura queda
    # «antiinflamatorio → esteroide → protector», que es la lógica clínica. Si
    # no hubiera pantoprazol, va al final de los renglones de la hoja general.
    i = next((k for k, m in enumerate(p['medicamentos'])
              if 'Pantoprazol' in m['nombre']), None)
    if i is None:
        generales = [k for k, m in enumerate(p['medicamentos'])
                     if m.get('hoja') == 'general']
        i = (generales[-1] + 1) if generales else len(p['medicamentos'])
    p['medicamentos'].insert(i, fila)

    antes = p['version']
    p['version'] = version_de(p)
    print('%-18s %s -> %s%s' % (pid, antes, p['version'],
                                '   (apagada por omisión)' if pid in APAGADA_EN else ''))

cat['version'] = hashlib.sha256(json.dumps(
    {'plantillas': cat['plantillas'], 'hojas': cat['hojas'], 'horas': cat['horas']},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

print('catálogo de recetas  ' + cat['version'])
