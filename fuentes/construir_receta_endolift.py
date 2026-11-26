#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA RECETA DE ENDOLIFTING
=========================

Por qué existe
--------------
El 26-nov-2026 el médico pidió la hoja de indicaciones de endolifting y se
encontró que no había NADA en el sistema: ni hoja ni receta. Endolifting está
en su lista de precios desde hace tiempo —Facial/Cara y cuello y Corporal (1
área)— pero nunca llegó al expediente.

Lo que él definió ese día
--------------------------
  · Anestesia: SEDACIÓN más local.
  · Receta: **sólo antibiótico y analgésico**. Se le ofreció copiar la de
    nanofat completa —que trae además celecoxib y pantoprazol— y dijo que no:
    sólo esos dos.
  · La misma receta sirve para el facial y para el corporal.

De dónde sale cada renglón
--------------------------
Los tres se COPIAN de la plantilla de nanofat, que es el procedimiento más
parecido que ya tenía aprobado: facial, ambulatorio, con sedación y por
micropunciones. Mismo antibiótico con su rama de alergia a penicilina, mismo
paracetamol. Ni una dosis nueva.

Lo que se deja fuera a propósito
---------------------------------
  · Celecoxib / ketorolaco y pantoprazol — él dijo «sólo antibiótico y
    paracetamol». Por eso tampoco se preguntan las alergias a sulfas ni la
    función renal: esas preguntas existen para escoger el AINE, y sin AINE no
    tienen a quién servir. Una pregunta obligatoria sin consecuencia es una
    pregunta que el médico aprende a contestar sin leer.
  · Tramadol — no hay renglón de rescate, así que tampoco la pregunta de
    omitirlo ni el aviso de ISRS.
  · El spray de la garganta (bencidamina) — va en las cirugías con vía aérea
    instrumentada. Nanofat, que también es con sedación, tampoco lo lleva, y
    su hoja tampoco trae la sección de molestia de garganta. Endolifting
    sigue ese mismo criterio. Si él llega a usar mascarilla laríngea en estos
    casos, se agregan los dos a la vez —renglón y sección— para que la hoja
    no prometa un spray que la receta no trae.

Uso:  python3 construir_receta_endolift.py [recetas.json]
      (correr DESPUÉS de construir_receta_nanofat.py, de quien copia)
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'recetas.json'

cat = json.load(open(RUTA, encoding='utf-8'))
P = {p['id']: p for p in cat['plantillas']}

if 'endolift' in P:
    raise SystemExit('ya existe la plantilla de endolifting')

NF = P['nanofat']


def copia(x):
    return json.loads(json.dumps(x, ensure_ascii=False))


def med(parcial):
    hits = [m for m in NF['medicamentos'] if parcial.lower() in m['nombre'].lower()]
    if len(hits) != 1:
        raise SystemExit('esperaba un solo «%s» en nanofat, hay %d' % (parcial, len(hits)))
    return copia(hits[0])


def preg(pid):
    return copia(next(q for q in NF['preguntas'] if q['id'] == pid))


def aviso(clave):
    return copia(next(a for a in NF['avisos'] if a['si'] == clave))


ENDO = {
    'id': 'endolift',
    'nombre': 'Endolifting (facial o corporal)',
    # Sin `coincide`: endolifting se escoge a mano. Las palabras que lo
    # nombrarían —«lifting», «láser»— apuntan a otras cosas en su catálogo, y
    # proponer la receta equivocada es peor que no proponer ninguna.
    'coincide': [],
    'procedimiento': 'Endolifting',
    # Sólo las dos preguntas que de verdad cambian algo: la alergia a
    # penicilina, que escoge el antibiótico, y las otras alergias, que el
    # médico lee antes de firmar.
    'preguntas': [preg('peni'), preg('otras')],
    'medicamentos': [
        med('Amoxicilina'),
        med('Clindamicina'),
        med('Paracetamol'),
    ],
    'profilaxis': copia(NF['profilaxis']),
    'profilaxisNota': NF['profilaxisNota'],
    'avisos': [
        aviso({'peni': ['leve']}),
        aviso({'peni': ['grave']}),
        aviso({'menor': True}),
    ],
    # ←NUEVO  escritos para endolifting. Los de nanofat son de injerto de
    # grasa y no sirven aquí; lo que se vigila en endolifting es la quemadura
    # del punto de entrada, la infección y —en el facial— el nervio.
    'alarma': [
        {'t': 'Dolor que aumenta cada día en lugar de ceder, o que no cede con '
              'el paracetamol.'},
        {'t': 'Fiebre de 38 °C o más.'},
        {'t': 'Enrojecimiento que se extiende alrededor de un punto de entrada, '
              'con calor, pus o mal olor.'},
        {'t': 'Una costra oscura, una ampolla o una quemadura en un punto de '
              'entrada.'},
        {'t': 'Una zona que se endurece, crece y duele cada vez más, distinta '
              'del resto.'},
        {'t': 'Asimetría al sonreír, al levantar la ceja o al cerrar el ojo.'},
    ],
    'horaNota': NF['horaNota'],
}

# ---------------------------------------------------------------------------
# Redes de seguridad
# ---------------------------------------------------------------------------
nombres = ' | '.join(m['nombre'] for m in ENDO['medicamentos'])

for obliga in ['Amoxicilina', 'Clindamicina', 'Paracetamol']:
    if obliga not in nombres:
        raise SystemExit('falta %s' % obliga)

# Lo que él dijo que NO lleva. Si alguien reconstruye esta plantilla copiando
# de nanofat sin leer, se cuelan solos.
for sobra in ['Celecoxib', 'Ketorolaco', 'Pantoprazol', 'Tramadol',
              'Bencidamina', 'Dexametasona', 'Cicaplast', 'Protector solar']:
    if sobra.lower() in nombres.lower():
        raise SystemExit('«%s» no va en la receta de endolifting: él dijo sólo '
                         'antibiótico y paracetamol' % sobra)

# Ningún renglón puede colgar de una pregunta que esta plantilla no hace, y
# ninguna pregunta puede quedarse sin renglón que dependa de ella.
ids = {q['id'] for q in ENDO['preguntas']}
usadas = set()
for m in ENDO['medicamentos']:
    for clave in (m.get('si') or {}):
        if clave not in ids and clave not in ('c24', 'menor'):
            raise SystemExit('«%s» depende de «%s», que nadie pregunta'
                             % (m['nombre'][:30], clave))
        usadas.add(clave)
for q in ENDO['preguntas']:
    if q['id'] not in usadas and q['id'] != 'otras':
        raise SystemExit('se pregunta «%s» y ningún renglón la usa' % q['id'])

# La paciente no puede quedarse sin antibiótico conteste lo que conteste.
for respuesta in (['no'], ['leve'], ['grave']):
    cubre = [m for m in ENDO['medicamentos']
             if m.get('hoja') == 'antibiotico' and
             set(respuesta) & set((m.get('si') or {}).get('peni', []))]
    if not cubre:
        raise SystemExit('con peni=%s no queda antibiótico' % respuesta)

if len(set(a['t'] for a in ENDO['alarma'])) != len(ENDO['alarma']):
    raise SystemExit('hay signos de alarma duplicados')

ENDO['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in ENDO.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

# Entra junto a las demás de consultorio, después de nanofat.
i = next(k for k, p in enumerate(cat['plantillas']) if p['id'] == 'nanofat')
cat['plantillas'].insert(i + 1, ENDO)

cat['version'] = hashlib.sha256(json.dumps(
    {'plantillas': cat['plantillas'], 'hojas': cat['hojas'], 'horas': cat['horas']},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

print('plantilla endolift · versión %s · %d renglones, %d preguntas, '
      '%d signos de alarma'
      % (ENDO['version'], len(ENDO['medicamentos']), len(ENDO['preguntas']),
         len(ENDO['alarma'])))
print('catálogo de recetas  %s · %d plantillas'
      % (cat['version'], len(cat['plantillas'])))
