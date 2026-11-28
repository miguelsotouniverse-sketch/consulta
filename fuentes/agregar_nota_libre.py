#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NOTA MÉDICA DE TEXTO LIBRE
===========================

Qué pidió
---------
El 28-nov-2026: una paciente le pidió una nota médica para tramitar su
licencia en el ISSSTE. Se le propuso construir un documento «Resumen clínico»
con campos propios —padecimiento, diagnósticos, evolución, pronóstico— y él
contestó: «¿por qué no uno únicamente a datos del establecimiento y a texto
libre?».

Tiene razón, y por una razón de fondo: los documentos de este expediente que
van dirigidos a un tercero son todos distintos entre sí —el ISSSTE, una
aseguradora, otro médico, un patrón— y cada uno pide algo que no se puede
prever. Un formulario por cada destinatario es una carrera que no se gana.
Lo que no cambia es el membrete, la identificación de la paciente, la fecha,
la cédula y la firma: eso es lo que hace válido el papel, y eso ya lo pone la
aplicación sola.

Qué sí se agrega además del texto libre
----------------------------------------
Dos campos, no uno:

· `nota_asunto` — de qué es la nota. Se imprime como el título del documento
  en lugar de «NOTA MÉDICA», y es lo que se va a ver en la lista del
  expediente. Sin él, al tercer mes el expediente tiene nueve renglones que
  dicen «Nota médica» y hay que abrirlos uno por uno para saber cuál es cuál.
· `nota_texto` — el cuerpo, con dictado.

Lo que NO se agrega, a propósito
---------------------------------
Ningún campo de la paciente. Nombre, sexo, edad, número de expediente y fecha
ya salen del expediente y se imprimen en la ficha de todos los documentos: en
un papel que va a una institución, un dato tecleado de memoria es justo el que
sale mal.

Ninguno de los dos es obligatorio en el esquema: el candado de datos
obligatorios de la NOM-004 está hecho para las notas clínicas, y si estos
campos lo fueran, el aviso de «faltan datos» aparecería en un documento que no
es una nota de atención. El candado propio —que no se imprima una nota en
blanco— va en index.html.

Uso:  python3 agregar_nota_libre.py [campos.json]
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'campos.json'

GRUPO = 'Nota médica'
ETIQUETA = 'Nota médica'

CAMPOS = [
    {
        'id': 'nota_asunto',
        'etiqueta': 'Asunto de la nota',
        'grupo': GRUPO,
        'control': 'texto',
        'opciones': [],
        'pista': 'Resumen clínico, Constancia médica, Carta a la aseguradora…',
        'sistema': 'App expediente',
        'captura': 'Teclado',
        'obligatorio': False,
        'aparece': ETIQUETA,
        'notas': ('Se imprime como título del documento y es lo que distingue '
                  'una nota de otra en la lista del expediente.'),
        'valoracion': False,
    },
    {
        'id': 'nota_texto',
        'etiqueta': 'Texto de la nota',
        'grupo': GRUPO,
        'control': 'parrafo',
        'opciones': [],
        'pista': '',
        'sistema': 'App expediente',
        'captura': 'Dictado',
        'obligatorio': False,
        'aparece': ETIQUETA,
        'notas': ('Texto libre. Los renglones en blanco se respetan al '
                  'imprimir: lo que se escribe en párrafos sale en párrafos.'),
        'valoracion': False,
    },
]

e = json.load(open(RUTA, encoding='utf-8'))
antes_campos = len(e['campos'])
antes_grupos = len(e['grupos'])

ids = {c['id'] for c in e['campos']}
for c in CAMPOS:
    if c['id'] in ids:
        raise SystemExit('el campo «%s» ya existe en el esquema' % c['id'])

if GRUPO not in e['grupos']:
    e['grupos'].append(GRUPO)
e['campos'].extend(CAMPOS)

# ---------------------------------------------------------------------------
# Redes de seguridad
# ---------------------------------------------------------------------------
# 1. El esquema nunca debe encoger: la app se niega a subir uno más corto, y
#    con razón —se llevaría campos del expediente—.
if len(e['campos']) != antes_campos + len(CAMPOS):
    raise SystemExit('el esquema no creció lo que debía')
if len(e['grupos']) < antes_grupos:
    raise SystemExit('se perdió un grupo del esquema')

# 2. Ninguno obligatorio, por lo explicado arriba.
for c in CAMPOS:
    if c['obligatorio']:
        raise SystemExit('la nota libre no debe traer campos obligatorios: el '
                         'aviso de la NOM-004 es para las notas clínicas')

# 3. Que no se haya colado un campo de la paciente. Esta nota no captura
#    ningún dato de identificación: todos salen del expediente.
for c in CAMPOS:
    if c['id'].startswith('paciente_'):
        raise SystemExit('esta nota no captura datos de la paciente')

e['generado'] = datetime.date.today().isoformat()
sin = {k: v for k, v in e.items() if k not in ('version', 'generado')}
e['version'] = hashlib.sha256(
    json.dumps(sin, ensure_ascii=False, sort_keys=True).encode('utf-8')
).hexdigest()[:16]

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(e, f, ensure_ascii=False, indent=1)

print('grupo nuevo   %s' % GRUPO)
print('campos        %d -> %d' % (antes_campos, len(e['campos'])))
for c in CAMPOS:
    print('   + %-14s %-8s %s' % (c['id'], c['control'], c['etiqueta']))
print('esquema       %s' % e['version'])
