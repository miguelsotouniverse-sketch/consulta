#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEXAMETASONA 4 mg EN LUGAR DE PREDNISONA 20 mg
===============================================

Qué cambia
----------
El médico lo indicó el 28-oct-2026: «vamos a cambiar la prednisona 20 mg por
dexametasona 4 mg (Decorex) cada 24 horas por 10 días».

    antes   Prednisona 20 mg · 1 al día · 14 días
    ahora   Dexametasona 4 mg (Decorex) · 1 al día · 10 días

Dónde
-----
En las NUEVE plantillas que llevan esteroide, el láser eCO₂ incluido. El
esteroide va en prácticamente todas sus cirugías, así que el cambio es
global: dejar una sola plantilla con prednisona sería garantizar que algún
día salga la receta vieja sin que nadie lo note.

Lo que se conserva del renglón viejo
------------------------------------
Las dos advertencias que no son de la molécula sino del esteroide, y que
siguen valiendo igual: que no se alargue ni se suspenda por cuenta propia, y
que avise si tiene diabetes porque sube el azúcar mientras lo toma. Eso no se
vuelve a redactar: se conserva.

Lo que NO se tocó
-----------------
El pantoprazol. Sigue en 14 días porque cubre al antiinflamatorio, que no
cambió, no al esteroide.

Uso:  python3 cambiar_esteroide_dexametasona.py [recetas.json]
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'recetas.json'

DIAS = 10          # confirmado por el médico (28-oct-2026)

VIEJO_NOMBRE = 'Prednisona 20 mg, tabletas.'
NUEVO_NOMBRE = 'Dexametasona 4 mg, tabletas (Decorex®).'
NUEVA_IND = (
    'Tomar 1 tableta (4 mg) vía oral cada 24 horas, por la mañana y con '
    'alimento, durante ' + str(DIAS) + ' días; al terminar los ' + str(DIAS) +
    ' días se suspende. Sirve para bajar la inflamación de los tejidos '
    'operados. No la alargue ni la suspenda antes por su cuenta, y si tiene '
    'diabetes avísenos: el esteroide sube el azúcar mientras lo toma.')

cat = json.load(open(RUTA, encoding='utf-8'))

if any('Dexametasona' in m['nombre']
       for p in cat['plantillas'] for m in p['medicamentos']):
    raise SystemExit('ya hay dexametasona en alguna plantilla; no se repite')


def version_de(p):
    return hashlib.sha256(json.dumps(
        {k: v for k, v in p.items() if k != 'version'},
        ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]


cambiadas = []
for p in cat['plantillas']:
    hits = [m for m in p['medicamentos'] if m['nombre'] == VIEJO_NOMBRE]
    if not hits:
        print('%-18s no traía prednisona' % p['id'])
        continue
    if len(hits) > 1:
        raise SystemExit(p['id'] + ' trae la prednisona dos veces; revíselo')
    m = hits[0]
    m['nombre']     = NUEVO_NOMBRE
    m['indicacion'] = NUEVA_IND
    m['cantidad']   = str(DIAS) + ' tabletas'
    m['duracion']   = str(DIAS) + ' días'
    if m.get('horario'):
        m['horario']['n'] = 'Dexametasona'
    antes = p['version']
    p['version'] = version_de(p)
    cambiadas.append(p['id'])
    print('%-18s %s -> %s' % (p['id'], antes, p['version']))

if not cambiadas:
    raise SystemExit('no cambié ninguna: ¿ya estaba hecho?')

# El aviso de pantalla de la plantilla Deep Plane + CO₂ nombra el esteroide
# por su nombre, porque su razón de ser es que no se dupliquen dos esteroides
# en la misma paciente. Si se queda hablando de prednisona, contradice a la
# receta que acompaña, que es el peor lugar donde puede quedar una palabra
# vieja. La red de seguridad de abajo existe por esto: lo encontró ella.
AVISO_VIEJO = ('Plantilla combinada: la prednisona va una sola vez, la del '
               'lifting (20 mg al día, 14 días). No agregue la del láser.')
AVISO_NUEVO = ('Plantilla combinada: el esteroide va una sola vez, el del '
               'lifting (dexametasona 4 mg al día, ' + str(DIAS) + ' días). '
               'No agregue el del láser.')
avisos_tocados = 0
for p in cat['plantillas']:
    aqui = 0
    for a in p.get('avisos', []):
        if a.get('texto') == AVISO_VIEJO:
            a['texto'] = AVISO_NUEVO
            aqui += 1
    if aqui:
        p['version'] = version_de(p)
        avisos_tocados += aqui
        print('%-18s aviso de pantalla actualizado -> %s' % (p['id'], p['version']))

# Red de seguridad: que no quede viva una sola prednisona.
todo = json.dumps(cat, ensure_ascii=False)
if 'Prednisona' in todo or 'prednisona' in todo:
    raise SystemExit('quedó prednisona viva en el catálogo')

cat['version'] = hashlib.sha256(json.dumps(
    {'plantillas': cat['plantillas'], 'hojas': cat['hojas'], 'horas': cat['horas']},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

print('catálogo de recetas  ' + cat['version'] + '  (' + str(len(cambiadas)) +
      ' plantillas con dexametasona)')
