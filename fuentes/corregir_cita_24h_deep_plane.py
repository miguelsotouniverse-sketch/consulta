#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA CITA DE LAS 24 HORAS NO EXISTE: ES EL PASE DE VISITA
========================================================

Qué estaba mal
--------------
Las hojas de Deep Plane citaban a la paciente «a las 24 horas» para descartar
hematoma y retirar el vendaje, como si tuviera que regresar al consultorio al
día siguiente de operarse.

No es así. El médico lo corrigió el 1-nov-2026: **todas sus pacientes de Deep
Plane se quedan a dormir una noche en la clínica**, y esa revisión es el pase
de visita de la mañana siguiente, antes del alta. Cuando la paciente recibe
esta hoja, esa revisión ya ocurrió.

Por qué importa
---------------
Una hoja que inventa una cita hace daño en los dos sentidos. A la paciente la
manda a buscar un día y un lugar que no existen, o la deja creyendo que se
saltó algo. Y a recepción le mete en la agenda una cita fantasma que nadie
programó. La primera cita de verdad es la de las 72 horas, cuando se retira la
malla hemostática.

Lo que NO se pierde
-------------------
El renglón que se borra decía algo que sí hay que decir: que en esa revisión
se descarta hematoma y que los drenajes se retiran por gasto y características
del líquido, no por calendario. Eso se conserva, movido a un párrafo antes de
la tabla de citas, donde queda claro que es parte del internamiento.

Dónde se aplica y dónde no
--------------------------
En `deep_plane` y `deep_plane_co2`, que son el Deep Plane facelift completo.

En `facial_combinada` NO se toca: ésa es el Deep Plane **de cuello**, otra
cirugía —sin malla hemostática— y el médico no dijo que esa paciente también
se quede la noche. Si también se queda, se agrega a la lista de abajo y se
vuelve a correr.                                                 ←CONFIRMAR

Uso:  python3 corregir_cita_24h_deep_plane.py [indicaciones.json]
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'

HOJAS = ['deep_plane', 'deep_plane_co2']

# El texto de la cita que se elimina, para no borrar otra por error.
VIEJA = ('Revisión de la herida para descartar hematoma y retiro del vendaje. '
         'Si trae drenajes, se revisan: se retiran cuando el gasto y las '
         'características del líquido lo permiten, no por calendario')

# Lo que ocupa su lugar, antes de la tabla de citas.                 ←NUEVO
NOCHE = ('Usted pasa la primera noche en la clínica. A la mañana siguiente, '
         'antes de irse a casa, la revisamos: ahí se descarta hematoma y, si '
         'trae drenajes, se revisan —se retiran cuando el gasto y las '
         'características del líquido lo permiten, no por calendario—. Esa '
         'revisión es parte de su internamiento, no una cita: cuando usted '
         'lee esta hoja, ya ocurrió. Su primera cita en el consultorio es a '
         'las 72 horas.')

ANCLA_P = 'Todas son obligatorias.'

cat = json.load(open(RUTA, encoding='utf-8'))
H = {h['id']: h for h in cat['hojas']}

for hid in HOJAS:
    if hid not in H:
        raise SystemExit('falta la hoja ' + hid)
    h = H[hid]

    if any(b['t'] == 'p' and str(b.get('x', '')).startswith('Usted pasa la primera noche')
           for b in h['bloques']):
        raise SystemExit('la corrección ya estaba en ' + hid)

    # 1) fuera la cita de las 24 horas
    quitadas = 0
    for b in h['bloques']:
        if b['t'] != 'citas':
            continue
        antes = len(b['x'])
        b['x'] = [c for c in b['x']
                  if not (c.get('cita') == '24 horas' and c.get('que', '').startswith(VIEJA[:40]))]
        quitadas += antes - len(b['x'])
        if b['x'] and b['x'][0]['cita'] != '72 horas':
            raise SystemExit('en ' + hid + ' la primera cita quedó siendo «' +
                             b['x'][0]['cita'] + '» y esperaba «72 horas»')
    if quitadas != 1:
        raise SystemExit('en ' + hid + ' quité ' + str(quitadas) +
                         ' citas de 24 horas y esperaba exactamente 1')

    # 2) el párrafo del internamiento, antes de la tabla de citas
    pos = None
    for i, b in enumerate(h['bloques']):
        if b['t'] == 'p' and str(b.get('x', '')).startswith(ANCLA_P):
            pos = i
            break
    if pos is None:
        raise SystemExit('no encontré dónde poner el párrafo de la noche en ' + hid)
    h['bloques'].insert(pos, {'t': 'p', 'x': NOCHE})

    # 3) la regla de los drenajes no se puede haber perdido
    todo = json.dumps(h, ensure_ascii=False)
    if 'no por calendario' not in todo:
        raise SystemExit('se perdió la regla de los drenajes en ' + hid)
    if '24 horas' in json.dumps([b for b in h['bloques'] if b['t'] == 'citas'], ensure_ascii=False):
        raise SystemExit('quedó viva una cita de 24 horas en ' + hid)

    antes = h['version']
    h['version'] = hashlib.sha256(json.dumps(
        {k: v for k, v in h.items() if k != 'version'},
        ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]
    print('%-18s %s -> %s  (fuera la cita de 24 h, dentro el pase de visita)'
          % (hid, antes, h['version']))

cat['version'] = hashlib.sha256(json.dumps(
    {'hojas': cat['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

print('catálogo  ' + cat['version'])
