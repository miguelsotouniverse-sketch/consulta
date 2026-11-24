#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EL PLANO DEL IMPLANTE SE PREGUNTA, NO SE SUPONE
================================================

Qué estaba mal
--------------
La plantilla de mastopexia metía la ciclobenzaprina SIEMPRE, y lo explicaba
con un aviso de pantalla: «entra encendida porque esta plantilla supone plano
retromuscular; si quedó subglandular, quítele la marca al renglón».

Eso es una suposición disfrazada de valor por omisión. El médico lo corrigió
el 24-nov-2026, con estas palabras, hablando de su paciente de ese día:
«estos quedaron retromusculares pero pudieron haber quedado retroglandulares,
entonces tendrías que preguntar».

Por qué importa y no es un detalle de forma
-------------------------------------------
Un relajante muscular que entra solo se queda. El renglón se puede
deseleccionar, sí, pero hay que acordarse de hacerlo — y lo que se olvida es
justo lo que entró sin que nadie lo pidiera. La ciclobenzaprina da sueño, se
suma al tramadol, y con un ISRS de base eleva el riesgo de síndrome
serotoninérgico. No es un renglón que convenga dar por sentado.

Es la misma regla que el médico ya había fijado para el antibiótico y para el
spray de la garganta: lo que cambia el contenido de la receta se pregunta
antes de desplegarla. Aquí no se agrega un mecanismo nuevo; se usa el que ya
existe (`preguntas` + `si`).

Qué hace este script
--------------------
  1. Agrega la pregunta `retro` a la plantilla de mastopexia, con la misma
     forma que `tubo`: obligatoria, sin respuesta por omisión, y marcada
     `enPie` para que el pliego impreso diga con qué respuesta se armó.
  2. Condiciona la ciclobenzaprina a `retro = sí`.
  3. Quita el aviso de «quítele la marca», que ya no describe nada.
  4. Condiciona también el aviso de ISRS, porque sólo tiene sentido cuando la
     ciclobenzaprina de verdad está en la receta.

Uso:  python3 preguntar_plano_mastopexia.py [recetas.json]
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'recetas.json'

cat = json.load(open(RUTA, encoding='utf-8'))
P = {p['id']: p for p in cat['plantillas']}

M = P['mastopexia']

if any(q['id'] == 'retro' for q in M.get('preguntas', [])):
    raise SystemExit('la mastopexia ya pregunta el plano')

# La pregunta se copia de `tubo`, que es la que el médico ya aprobó, y se le
# cambia el texto. Así hereda la forma exacta que la aplicación sabe dibujar.
TUBO = next(q for q in P['body360']['preguntas'] if q['id'] == 'tubo')
RETRO = json.loads(json.dumps(TUBO, ensure_ascii=False))
RETRO.update({
    'id': 'retro',
    'etiqueta': 'El implante quedó en plano retromuscular',
    'pieSi': 'implante retromuscular',
    'pieNo': 'implante subglandular o subfascial',
    'ayuda': 'Decide si la receta lleva el relajante muscular. El espasmo del '
             'pectoral es de las pacientes con el implante por detrás del '
             'músculo; en plano subglandular ese renglón no aplica. Si no hubo '
             'implante, conteste que no.',
})

# `tubo` va al final de la lista de preguntas; `retro` entra junto a ella.
M['preguntas'].append(RETRO)

ciclo = [m for m in M['medicamentos'] if 'Ciclobenzaprina' in m['nombre']]
if len(ciclo) != 1:
    raise SystemExit('esperaba un solo renglón de ciclobenzaprina, hay %d' % len(ciclo))
if 'si' in ciclo[0]:
    raise SystemExit('la ciclobenzaprina ya venía condicionada')
ciclo[0]['si'] = {'retro': True}

antes = len(M['avisos'])
M['avisos'] = [a for a in M['avisos']
               if 'quítele la marca' not in a['texto']]
if len(M['avisos']) != antes - 1:
    raise SystemExit('no se encontró el aviso de «quítele la marca»')

isrs = [a for a in M['avisos'] if a['si'] == {'isrs': True}]
if len(isrs) != 1:
    raise SystemExit('esperaba un solo aviso de ISRS propio de la mastopexia')
isrs[0]['si'] = {'isrs': True, 'retro': True}

# ---------------------------------------------------------------------------
# Redes de seguridad
# ---------------------------------------------------------------------------
# Que el renglón no quede huérfano: si se condiciona a una respuesta que la
# plantilla no pregunta, nunca aparece y la paciente se queda sin él.
ids = {q['id'] for q in M['preguntas']}
for m in M['medicamentos']:
    for clave in (m.get('si') or {}):
        if clave not in ids and clave not in ('c24', 'menor'):
            raise SystemExit('el renglón «%s» depende de «%s», que nadie pregunta'
                             % (m['nombre'][:30], clave))

# Que siga habiendo analgésico y antibiótico pase lo que pase con el plano.
sin_relajante = [m for m in M['medicamentos'] if (m.get('si') or {}).get('retro') is not True]
if not any('Paracetamol' in m['nombre'] for m in sin_relajante):
    raise SystemExit('la receta se quedó sin paracetamol')

M['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in M.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

cat['version'] = hashlib.sha256(json.dumps(
    {'plantillas': cat['plantillas'], 'hojas': cat['hojas'], 'horas': cat['horas']},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

print('mastopexia · versión %s · %d preguntas, ciclobenzaprina condicionada'
      % (M['version'], len(M['preguntas'])))
print('catálogo de recetas  %s' % cat['version'])
