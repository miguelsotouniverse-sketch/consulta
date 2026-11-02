#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA RECETA DE RIBXCAR SOLA
==========================

Por qué hace falta
------------------
La plantilla de Body360 traía `ribxcar` entre sus palabras de coincidencia, así
que a una paciente de RibXcar sola el sistema le proponía la receta completa de
una lipoescultura: rivaroxabán 10 días, amlodipino, metoprolol y captopril de
rescate, para un procedimiento percutáneo de quince minutos.

El médico lo cerró el 2-nov-2026: **«no llevan anticoagulación, es una cirugía
de 15 minutos y es percutánea»**.

Qué se copia y qué se quita
---------------------------
Esta plantilla es la de Body360 —copiada renglón por renglón, no reteclada—
menos cinco cosas:

  FUERA  Rivaroxabán 10 mg        · él lo quitó explícitamente
  FUERA  Amlodipino 5 mg          · ←CONFIRMAR, ver abajo
  FUERA  Metoprolol 50 mg         · ←CONFIRMAR, ver abajo
  FUERA  Captopril 25 mg          · rescate de los dos anteriores; sin ellos
                                    no tiene a qué rescatar
  FUERA  Clonazepam en gotas      · ←CONFIRMAR, ver abajo

Y se queda todo lo demás: el antibiótico oral según alergia a penicilina, el
paracetamol, el celecoxib —o ketorolaco si hay alergia a sulfas—, la
dexametasona, el pantoprazol, el tramadol de rescate, el ondansetrón y los dos
laxantes que acompañan al tramadol.

Los tres ←CONFIRMAR
-------------------
1. **Amlodipino y metoprolol.** Los lleva toda su cirugía abierta y también la
   lipoescultura. Los quité aquí por la misma lógica con la que él quitó la
   anticoagulación: están para mantener la sistólica baja y evitar que se
   acumule sangre bajo la piel despegada, y aquí no hay piel despegada. Si los
   quiere, van los tres renglones juntos —los dos de base y el captopril— y
   además los tres bloques correspondientes en la hoja, porque una receta con
   antihipertensivos y una hoja que no los explica es peor que ninguna de las
   dos.
2. **Clonazepam.** Su regla dice «rescate de ansiedad en toda cirugía
   ABIERTA», y ésta no lo es.
3. **La profilaxis intravenosa.** Se copia la de Body360 (cefazolina 2 g, o
   clindamicina 900 mg si hay alergia grave), pero la nota de redosificación
   de Body360 habla de cirugías que pasan de 4 o 6 horas. En quince minutos eso
   no se alcanza nunca, así que la nota se reescribe en vez de copiarse: dejarla
   igual sería dejar una instrucción que no aplica.

Uso:  python3 construir_receta_ribxcar.py [recetas.json] [indicaciones.json]
      (después de construir_hoja_ribxcar.py y ANTES de
       agregar_molestia_garganta.py, que le pone la pregunta del tubo y el spray)
"""

import json
import hashlib
import datetime
import sys

RUTA_RX = sys.argv[1] if len(sys.argv) > 1 else 'recetas.json'

cat = json.load(open(RUTA_RX, encoding='utf-8'))
P = {p['id']: p for p in cat['plantillas']}

if 'ribxcar' in P:
    raise SystemExit('la plantilla de ribxcar ya existe')
if 'body360' not in P:
    raise SystemExit('falta la plantilla de body360, de donde se copia')

B = P['body360']

# Lo que no va. Se identifica por el principio activo del nombre, no por el
# índice: si mañana se agrega un renglón a Body360, los índices se corren y
# esto seguiría sacando lo correcto.
QUITAR = ('Rivaroxab', 'Amlodipino', 'Metoprolol', 'Captopril', 'Clonazepam')


def se_queda(m):
    return not any(q in m['nombre'] for q in QUITAR)


meds = [dict(m) for m in B['medicamentos'] if se_queda(m)]

quitados = len(B['medicamentos']) - len(meds)
if quitados != len(QUITAR):
    raise SystemExit('esperaba quitar ' + str(len(QUITAR)) + ' renglones de la '
                     'receta de Body360 y quité ' + str(quitados) +
                     ': revisa si alguno cambió de nombre')

# El renglón del spray de la garganta lo pone agregar_molestia_garganta.py más
# adelante en la cadena, para que su texto y su dosis vivan en un solo lugar.
# Si se copiara aquí, habría dos fuentes del mismo renglón y un día dirían
# cosas distintas.
meds = [m for m in meds if not (m.get('si') or {}).get('tubo')]

# Los avisos de Body360 que hablan del anticoagulante ya no aplican.
avisos = [dict(a) for a in B['avisos']
          if 'rivaroxab' not in a['texto'].lower()]
if len(avisos) != len(B['avisos']) - 3:
    raise SystemExit('esperaba quitar 3 avisos de rivaroxabán y quité ' +
                     str(len(B['avisos']) - len(avisos)))
# El de sulfas se queda, pero sin la frase del rivaroxabán que ya no existe.
for a in avisos:
    if 'Con rivaroxabán encima' in a['texto']:
        raise SystemExit('quedó un aviso que menciona el rivaroxabán')

# ←NUEVO: el aviso que sustituye al del anticoagulante, para que quede escrito
# en la pantalla del médico por qué esta receta NO lo lleva.
avisos.insert(0, {
    'si': {}, 'tono': '',
    'texto': ('RibXcar sola no lleva anticoagulación: es percutánea y de unos '
              'quince minutos. Tampoco lleva los dos antihipertensivos de base '
              'ni el clonazepam de rescate, porque no hay piel despegada ni es '
              'cirugía abierta. Si este caso los necesita, agréguelos a mano.')})

# La lista de alarma de la receta pierde el renglón del anticoagulante.
alarma = [dict(a) for a in B['alarma']
          if 'anticoagulante' not in a['t'].lower()]
if len(alarma) != len(B['alarma']) - 1:
    raise SystemExit('esperaba quitar 1 renglón de alarma por el anticoagulante')
# Y gana el que distingue a esta cirugía, el mismo que va en la hoja.
alarma.insert(1, {'t': 'Dolor que aumenta cada vez que respira, o que ya no la '
                       'deja llenar el pecho de aire.'})

plant = {
    'id': 'ribxcar',
    'nombre': 'RibXcar — remodelación costal',
    'coincide': ['ribxcar', 'rib xcar', 'remodelacion costal',
                 'remodelación costal'],
    'procedimiento': 'RibXcar® — remodelación costal guiada por ultrasonido',
    'preguntas': [dict(q) for q in B['preguntas']
                  if q['id'] != 'tubo'],   # la del tubo la pone la cadena
    'medicamentos': meds,
    'profilaxis': [dict(x) for x in B['profilaxis']],
    # ←NUEVO: la nota de Body360 habla de redosificar a las 4 y 6 horas.
    'profilaxisNota': ('Dosis única: una remodelación costal no alcanza las 4 '
                       'horas que obligarían a redosificar.'),
    'avisos': avisos,
    'alarma': alarma,
    'horaNota': B['horaNota'],
}

# `ribxcar` deja de apuntar a la receta de Body360, por lo mismo que en la hoja.
antes = list(B.get('coincide', []))
B['coincide'] = [c for c in antes
                 if 'ribxcar' not in c.lower().replace(' ', '')]
if len(B['coincide']) == len(antes):
    raise SystemExit('esperaba quitar «ribxcar» de la receta de Body360 y no '
                     'estaba')

i = [k for k, p in enumerate(cat['plantillas']) if p['id'] == 'body360'][0]
cat['plantillas'].insert(i + 1, plant)


# ---------------------------------------------------------------------------
# Redes de seguridad
# ---------------------------------------------------------------------------
def plano(t):
    import unicodedata
    t = unicodedata.normalize('NFD', str(t).lower())
    return ''.join(c for c in t if unicodedata.category(c) != 'Mn').strip()


# Igual que `plantillaSugerida()`: debe coincidir EXACTAMENTE una.
for proc in ('RibXcar', 'Remodelación costal'):
    p = plano(proc)
    halladas = [x['id'] for x in cat['plantillas']
                if any(p.find(plano(c)) >= 0 for c in x.get('coincide', []))]
    if halladas != ['ribxcar']:
        raise SystemExit('«' + proc + '» coincide con ' + str(halladas) +
                         ' y esperaba sólo con ribxcar')

todo = json.dumps(plant, ensure_ascii=False)
for sobra in QUITAR:
    if sobra in todo:
        raise SystemExit('quedó «' + sobra + '» en la receta de ribxcar')
# El analgésico y el antibiótico sí tienen que estar, en los dos escenarios de
# alergia: una receta de la que se quitaron cinco renglones es el momento justo
# para quedarse sin lo importante.
for falta in ('Paracetamol', 'Dexametasona', 'Tramadol', 'Pantoprazol',
              'Amoxicilina', 'Clindamicina 300 mg', 'Celecoxib', 'Ketorolaco'):
    if falta not in todo:
        raise SystemExit('falta «' + falta + '» en la receta de ribxcar')
if not any(m['hoja'] == 'antibiotico' for m in meds):
    raise SystemExit('la receta de ribxcar se quedó sin pliego de antibiótico')
if any(m['hoja'] == 'psicotropico' for m in meds):
    raise SystemExit('quedó un pliego de psicotrópico sin medicamento')

plant['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in plant.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]
B['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in B.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

cat['version'] = hashlib.sha256(json.dumps(
    {'plantillas': cat['plantillas'], 'hojas': cat['hojas'],
     'horas': cat.get('horas')},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA_RX, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

print('receta     ribxcar            nueva -> %s  (%d medicamentos, %d menos '
      'que Body360)' % (plant['version'], len(meds), quitados + 1))
print('receta     body360            -> %s  (ya no responde a «ribxcar»)'
      % B['version'])
print('catálogo   ' + cat['version'])
