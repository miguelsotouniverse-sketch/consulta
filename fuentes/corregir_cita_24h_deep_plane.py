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

Dónde se aplica
---------------
En las TRES hojas que llevan Deep Plane: el facelift completo, el facelift
con láser CO₂ y la combinada facial —que es Deep Plane de cuello—. El médico
lo cerró el 1-nov-2026: «todo lo que lleva deep plane duerme en la clínica».

La frase de cuál es la primera cita NO se escribe a mano: se lee de la propia
tabla después de quitar el renglón. En el facelift completo queda «a las 72
horas», que es el retiro de la malla; en la combinada no hay malla y queda
«al día 5». Escribirla a mano habría mandado a la paciente de la combinada a
una cita de 72 horas que no existe — el mismo error que este script corrige.

Uso:  python3 corregir_cita_24h_deep_plane.py [indicaciones.json]
"""

import json
import hashlib
import datetime
import re
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'

HOJAS = ['deep_plane', 'deep_plane_co2', 'facial_combinada']

# El texto de la cita que se elimina, para no borrar otra por error.
VIEJA = ('Revisión de la herida para descartar hematoma y retiro del vendaje. '
         'Si trae drenajes, se revisan: se retiran cuando el gasto y las '
         'características del líquido lo permiten, no por calendario')

# Lo que ocupa su lugar, antes de la tabla de citas.                 ←NUEVO
def noche(primera):
    return ('Usted pasa la primera noche en la clínica. A la mañana '
            'siguiente, antes de irse a casa, la revisamos: ahí se descarta '
            'hematoma y, si trae drenajes, se revisan —se retiran cuando el '
            'gasto y las características del líquido lo permiten, no por '
            'calendario—. Esa revisión es parte de su internamiento, no una '
            'cita: cuando usted lee esta hoja, ya ocurrió. Su primera cita '
            'en el consultorio es ' + primera + '.')


def como_se_dice(cita):
    """«72 horas» → «a las 72 horas»; «Día 5» → «al día 5». Se arma de la
       tabla y no a mano: en la combinada no hay malla y su primera cita no
       es la misma que en el facelift completo."""
    c = str(cita).strip()
    m = re.match(r'^D[ií]a\s+(\d+)$', c, re.I)
    if m:
        return 'al día ' + m.group(1)
    m = re.match(r'^(\d+)\s*horas?$', c, re.I)
    if m:
        return 'a las ' + m.group(1) + ' horas'
    raise SystemExit('no sé cómo nombrar la primera cita: «' + c + '»')

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
    primera = None
    for b in h['bloques']:
        if b['t'] != 'citas':
            continue
        antes = len(b['x'])
        b['x'] = [c for c in b['x']
                  if not (c.get('cita') == '24 horas' and c.get('que', '').startswith(VIEJA[:40]))]
        quitadas += antes - len(b['x'])
        if b['x']:
            primera = como_se_dice(b['x'][0]['cita'])
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
    if not primera:
        raise SystemExit('no pude leer cuál es la primera cita de ' + hid)
    h['bloques'].insert(pos, {'t': 'p', 'x': noche(primera)})

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
