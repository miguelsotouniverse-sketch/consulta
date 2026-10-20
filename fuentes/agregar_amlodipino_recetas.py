#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EL AMLODIPINO DE LA VÍSPERA, DENTRO DE LAS RECETAS
===================================================

Por qué tiene que estar aquí
----------------------------
El médico indica amlodipino 5 mg la noche anterior a TODA cirugía abierta. Su
palabra: «el amlodipino siempre que sea cirugía abierta, es decir las únicas
que no llevan son las que no llevan incisión, por ejemplo un endolifting.
Todas las demás llevan».

No estaba en ninguna de las siete plantillas de receta. Salía a mano, o no
salía. Y es justo la que no admite olvido: se toma la víspera, así que una
receta que llega el día del procedimiento llega tarde para ella.

Lo que lo hace urgente ahora
----------------------------
La hoja preoperatoria dejó de decir «si su cirugía lleva incisión» y ahora
dice «si en sus recetas viene amlodipino 5 mg, tómelo hoy». Eso es mejor —la
paciente no tiene que clasificar su propia cirugía, sólo leer su receta— pero
convierte a la receta en la única fuente de verdad. Si el amlodipino no está
impreso ahí, nadie lo toma. Las dos cosas van juntas o ninguna.

Dónde entra y dónde no
----------------------
En las SEIS plantillas de cirugía abierta. En eCO₂ no: el láser no lleva
incisión, que es exactamente el límite que puso el médico.

Va como PRIMER renglón de la hoja general, antes que los postoperatorios,
porque es el primero en el tiempo: se toma antes de entrar a quirófano y todo
lo demás se toma al salir.

Y va encendido. Si un caso no lo lleva, se apaga con la casilla del renglón.

Uso:  python3 agregar_amlodipino_recetas.py [recetas.json]
      (al final de la cadena: necesita que las siete plantillas ya existan)
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'recetas.json'

# Cirugía abierta = lleva incisión = lleva amlodipino. eCO₂ es la única que no.
SIN_AMLODIPINO = {'eco2'}

AMLODIPINO = {
    'hoja': 'general',
    'nombre': 'Amlodipino 5 mg, tabletas.',
    'indicacion':
        'Tomar 1 tableta vía oral la NOCHE ANTERIOR a la cirugía, dosis única. '
        'Ayuda a mantener su presión estable durante el procedimiento y a '
        'reducir el sangrado y la inflamación. Es la única de sus recetas que '
        'se toma antes de la cirugía: cómprela en cuanto reciba sus recetas y '
        'no la deje para el último día.',
    'cantidad': '1 tableta',                                    # ←CONFIRMAR
    'duracion': 'Dosis única, la noche anterior',
    'horario': {'n': 'Amlodipino (víspera)', 'h': ['21:00']},   # ←CONFIRMAR
}

cat = json.load(open(RUTA, encoding='utf-8'))
P = {p['id']: p for p in cat['plantillas']}

ya = [i for i, p in P.items()
      if any('Amlodipino' in m['nombre'] for m in p['medicamentos'])]
if ya:
    raise SystemExit('ya estaba en ' + ', '.join(sorted(ya)) + '; no se duplica')


def version_de(p):
    return hashlib.sha256(json.dumps(
        {k: v for k, v in p.items() if k != 'version'},
        ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]


puestas = 0
for pid in sorted(P):
    if pid in SIN_AMLODIPINO:
        print('%-18s sin amlodipino (no lleva incisión)' % pid)
        continue
    p = P[pid]
    i = next((k for k, m in enumerate(p['medicamentos'])
              if m.get('hoja') == 'general'), len(p['medicamentos']))
    p['medicamentos'].insert(i, json.loads(json.dumps(AMLODIPINO, ensure_ascii=False)))
    antes = p['version']
    p['version'] = version_de(p)
    puestas += 1
    print('%-18s %s -> %s' % (pid, antes, p['version']))

if puestas != len(P) - len(SIN_AMLODIPINO & set(P)):
    raise SystemExit('no entró en todas las que debía')

cat['version'] = hashlib.sha256(json.dumps(
    {'plantillas': cat['plantillas'], 'hojas': cat['hojas'], 'horas': cat['horas']},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

print('catálogo de recetas  ' + cat['version'] +
      '  (' + str(puestas) + ' plantillas con amlodipino)')
