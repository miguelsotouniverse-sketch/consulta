#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA RECETA DE MORPHEUS8 FACIAL
==============================

Es la del eCO₂ menos dos cosas, y el médico decidió las dos el 6-nov-2026:

  FUERA  Valaciclovir 500 mg   · «No lleva» profilaxis antiviral. El eCO₂ sí
                                 la lleva porque deja la piel abierta; el
                                 Morpheus8 no. El herpes se queda únicamente
                                 como signo de alarma en la hoja.
  FUERA  Clobetasol (Clobesol) · escogió «Cicaplast, vaselina y FPS 50, sin
                                 Clobesol».

Queda: Cicaplast, vaselina, protector solar y la dexametasona oral que el eCO₂
ya traía APAGADA por omisión —visible en la lista, se enciende con un clic si
esa paciente amanece muy inflamada—. El spray de la garganta lo agrega
`agregar_molestia_garganta.py` más adelante en la cadena, con la pregunta del
tubo, para que su texto y su dosis vivan en un solo lugar.

LO QUE NO LLEVA Y QUIZÁ DEBERÍA                                   ←CONFIRMAR
-------------------------------
**No lleva analgésico.** No lo puse porque la receta del eCO₂ tampoco lo
lleva, y el eCO₂ duele más que esto: me pareció que inventar un renglón que
usted no da en el procedimiento más agresivo sería decidir por usted. Si
quiere paracetamol para las primeras horas de ardor, es un renglón.

Uso:  python3 construir_receta_morpheus8.py [recetas.json]
      (después de construir_hoja_morpheus8.py y ANTES de
       agregar_molestia_garganta.py)
"""

import json
import hashlib
import datetime
import sys

RUTA_RX = sys.argv[1] if len(sys.argv) > 1 else 'recetas.json'

cat = json.load(open(RUTA_RX, encoding='utf-8'))
P = {p['id']: p for p in cat['plantillas']}

if 'morpheus8' in P:
    raise SystemExit('la plantilla de morpheus8 ya existe')
if 'eco2' not in P:
    raise SystemExit('falta la plantilla del eCO₂, de donde se copia')

E = P['eco2']

QUITAR = ('Valaciclovir', 'Clobetasol')


def se_queda(m):
    return not any(q in m['nombre'] for q in QUITAR)


meds = [dict(m) for m in E['medicamentos'] if se_queda(m)]
quitados = len(E['medicamentos']) - len(meds)
if quitados != len(QUITAR):
    raise SystemExit('esperaba quitar ' + str(len(QUITAR)) + ' renglones de la '
                     'receta del eCO₂ y quité ' + str(quitados) +
                     ': revisa si alguno cambió de nombre')

# El renglón del spray lo pone la cadena más adelante, en un solo lugar.
meds = [m for m in meds if not (m.get('si') or {}).get('tubo')]

# Los avisos del eCO₂ que hablan de lo que ya no va.
avisos = [dict(a) for a in E.get('avisos', [])
          if not any(q.lower() in a['texto'].lower()
                     for q in ('valaciclovir', 'clobesol', 'clobetasol',
                               'antiviral'))]

# ←NUEVO: que quede escrito en la pantalla del médico por qué esta receta es
# más corta que la del eCO₂, y no parezca que se olvidó algo.
avisos.insert(0, {
    'si': {}, 'tono': '',
    'texto': ('Morpheus8 no lleva profilaxis antiviral ni esteroide tópico: '
              'la radiofrecuencia con microagujas no deja la piel abierta como '
              'un láser ablativo. Tampoco lleva analgésico, igual que la receta '
              'del eCO₂. La dexametasona oral está en la lista, apagada: '
              'enciéndala si esta paciente lo necesita.')})

plant = {
    'id': 'morpheus8',
    'nombre': 'Morpheus8 facial',
    'coincide': ['morpheus8', 'morpheus 8', 'morpheus',
                 'radiofrecuencia con microagujas', 'microneedling con rf'],
    'procedimiento': 'Morpheus8® facial — radiofrecuencia fraccionada con microagujas',
    'preguntas': [dict(q) for q in E.get('preguntas', []) if q['id'] != 'tubo'],
    'medicamentos': meds,
    'profilaxis': [dict(x) for x in E.get('profilaxis', [])],
    'avisos': avisos,
    'alarma': [dict(a) for a in E.get('alarma', [])],
    'horaNota': E.get('horaNota', ''),
}
for k in ('profilaxisNota',):
    if E.get(k):
        plant[k] = E[k]

i = [k for k, p in enumerate(cat['plantillas']) if p['id'] == 'eco2'][0]
cat['plantillas'].insert(i + 1, plant)


# ---------------------------------------------------------------------------
# Redes de seguridad
# ---------------------------------------------------------------------------
def plano(t):
    import unicodedata
    t = unicodedata.normalize('NFD', str(t).lower())
    return ''.join(c for c in t if unicodedata.category(c) != 'Mn').strip()


for proc in ('Morpheus8', 'Morpheus 8 facial'):
    p = plano(proc)
    halladas = [x['id'] for x in cat['plantillas']
                if any(p.find(plano(c)) >= 0 for c in x.get('coincide', []))]
    if halladas != ['morpheus8']:
        raise SystemExit('«' + proc + '» coincide con ' + str(halladas) +
                         ' y esperaba sólo con morpheus8')

nombres = ' | '.join(m['nombre'] + ' ' + m['indicacion'] for m in meds)
for sobra in QUITAR:
    if sobra in nombres:
        raise SystemExit('quedó «' + sobra + '» en la receta de morpheus8')
for falta in ('Cicaplast', 'Vaselina', 'Protector solar'):
    if falta not in nombres:
        raise SystemExit('falta «' + falta + '» en la receta de morpheus8')
# La dexametasona tiene que seguir APAGADA, como en el eCO₂: encenderla por
# omisión sería dar un esteroide sistémico a toda paciente de un procedimiento
# de consultorio.
dexa = [m for m in meds if 'Dexametasona' in m['nombre']]
if len(dexa) != 1 or not dexa[0].get('fuera'):
    raise SystemExit('la dexametasona de morpheus8 tiene que estar en la lista '
                     'y apagada por omisión')
if any(m['hoja'] != 'general' for m in meds):
    raise SystemExit('morpheus8 no debería necesitar pliegos de antibiótico, '
                     'controlado ni psicotrópico')

plant['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in plant.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

cat['version'] = hashlib.sha256(json.dumps(
    {'plantillas': cat['plantillas'], 'hojas': cat['hojas'],
     'horas': cat.get('horas')},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA_RX, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

print('receta     morpheus8          nueva -> %s  (%d medicamentos)'
      % (plant['version'], len(meds)))
print('catálogo   ' + cat['version'])
