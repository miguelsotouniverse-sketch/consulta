#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA GARGANTA DESPUÉS DEL TUBO
=============================

De dónde sale
-------------
El médico lo planteó el 1-nov-2026: es muy frecuente que sus pacientes
operadas con intubación refieran dolor o ardor de garganta los días
siguientes, y hasta hoy ninguna hoja decía nada al respecto. La paciente
llegaba a casa con un síntoma que nadie le había anunciado y sin nada que
hacer con él.

Por qué es una PREGUNTA y no texto fijo
---------------------------------------
Porque el consejo sólo aplica si hubo tubo o mascarilla laríngea. A una
paciente que fue con sedación, el mismo texto le explica un síntoma que no
tuvo y le receta un spray que no necesita. El médico lo cerró así:

    «al igual que las recetas con antibiótico, todas deberíamos de preguntar
     antes de desplegar las recomendaciones postoperatorias si fue con tubo
     o sin tubo. Las recomendaciones preoperatorias sí deberán ser genéricas
     pero las postoperatorias no»

Así que la hoja preoperatoria lo dice siempre —ahí todavía no se sabe— y las
nueve hojas postoperatorias lo traen condicionado a la pregunta `tubo`, que
el médico contesta al imprimir. Sin contestarla la hoja no se imprime.

DOS COLISIONES QUE ME OBLIGARON A ESCRIBIR DOS VERSIONES
---------------------------------------------------------
1. **Los caramelos.** El borrador decía «puede chupar caramelos o pastillas
   para la garganta». En `deep_plane`, `deep_plane_co2` y `facial_combinada`
   la hoja YA prohíbe «dulces ácidos, chicles y caramelos» durante 14 días,
   porque en esas tres se trató la glándula submandibular y todo lo que
   estimula la saliva retrasa su cicatrización. Imprimir las dos cosas en la
   misma hoja la vuelve inservible: la paciente elige la que le conviene.
   En esas tres la lista va en versión SUBMANDIBULAR, que manda el alivio a
   lo que su propia dieta ya permite y explica por qué no hay caramelos.

2. **El alcohol y el tabaco.** El borrador decía «evite alcohol, tabaco,
   bebidas muy calientes y comida picante MIENTRAS TENGA MOLESTIA». Las nueve
   hojas ya prohíben el alcohol 14 días y la nicotina 4 semanas. «Mientras
   tenga molestia» es un plazo más corto, y puesto al lado del otro se lee
   como permiso para volver a fumar al cuarto día. Aquí sólo van las bebidas
   calientes y el picante; el alcohol y el tabaco se mencionan como lo que ya
   están: suspendidos por la cirugía, no por la garganta.

LO QUE DEJÉ FUERA DEL BORRADOR, A PROPÓSITO
-------------------------------------------
· «Suspenda el cigarro al menos 2 semanas antes.» La hoja preoperatoria ya
  pide 4 semanas antes y 4 después. Meter 2 semanas al lado es rebajar una
  indicación que ya estaba mejor. En su lugar, al renglón de 4 semanas que ya
  existe se le agrega el motivo nuevo: también irrita menos la garganta.
· «Manténgase bien hidratada los días previos, respetando el ayuno.» Ya está
  dicho dos veces en esa hoja: «Tome al menos 2 litros de agua al día» y la
  sección de ayuno completa. Repetirlo no agrega nada.
· El protocolo con anestesia (presión del globo, calibre del tubo,
  dexametasona IV, extubación) NO entra en ningún archivo de este sistema:
  no es material de vista a paciente. El médico lo dijo explícitamente.

LA DOSIS
--------
El borrador pedía «4 a 8 disparos hasta 6 veces al día». La etiqueta del
frasco con atomizador de 40 ml dice 4 atomizaciones, 4 veces al día (PLM,
Reg. 140M88 SSA VI). Se le preguntó y escogió la de etiqueta.

La receta nombra el frasco CON ATOMIZADOR de 40 ml y no sólo «Vantal»: el
mismo nombre comercial se vende en frasco de 360 ml para gárgaras, que no
atomiza y se dosifica distinto. Sin el calibre, la farmacia puede entregar el
equivocado.

Uso:  python3 agregar_molestia_garganta.py [recetas.json] [indicaciones.json]
      (al final de la cadena)
"""

import json
import hashlib
import datetime
import re
import sys

RUTA_RX = sys.argv[1] if len(sys.argv) > 1 else 'recetas.json'
RUTA_IND = sys.argv[2] if len(sys.argv) > 2 else 'indicaciones.json'

# Las nueve hojas postoperatorias. La de faja y la de laboratorios no son
# hojas de alta, y la preoperatoria lleva su propio texto, genérico.
POSTOP = ['deep_plane', 'lipoescultura', 'mastopexia', 'rinoplastia',
          'blefaroplastia', 'facial_combinada', 'deep_plane_co2', 'eco2',
          'otoplastia']

# La hoja y la receta de la misma cirugía no siempre se llaman igual: la hoja
# es «lipoescultura» y su receta es «body360». Si la hoja promete un spray que
# su receta no lleva, la paciente se va sin él, así que el par se declara aquí
# y más abajo se comprueba renglón por renglón.
RECETA_DE = {
    'deep_plane': 'deep_plane',
    'lipoescultura': 'body360',
    'mastopexia': 'mastopexia',
    'rinoplastia': 'rinoplastia',
    'blefaroplastia': 'blefaroplastia',
    'facial_combinada': 'facial_combinada',
    'deep_plane_co2': 'deep_plane_co2',
    'eco2': 'eco2',
    'otoplastia': 'otoplastia',
}

# Las tres donde se trató la glándula submandibular y los caramelos están
# prohibidos 14 días. Se comprueba contra el texto, no se da por hecho.
SUBMANDIBULAR = ['deep_plane', 'deep_plane_co2', 'facial_combinada']

WHATSAPP = '55 7215 5958'

PREGUNTA = {
    'id': 'tubo',
    'etiqueta': 'La anestesia fue con tubo o mascarilla laríngea',
    'tipo': 'sino',
    'obligatoria': True,
    'enPie': True,
    'pieSi': 'anestesia general con vía aérea instrumentada',
    'pieNo': 'sin vía aérea instrumentada',
    'ayuda': ('Decide si se imprime la sección de molestia de garganta y si la '
              'receta lleva el spray. Con sedación sin tubo ni mascarilla, esa '
              'molestia no aplica y el texto sobraría.'),
}

TITULO = 'Molestia de garganta'

ENTRADA = ('Durante la anestesia se coloca un tubo o una mascarilla en la vía '
           'aérea para que usted respire. Es normal que los 2 o 3 días '
           'siguientes sienta la garganta irritada, con ardor, molestia al '
           'pasar saliva o la voz ronca. Cede sola y no tiene nada que ver con '
           'su cirugía ni con su resultado.')

# --- los renglones comunes a las nueve hojas ---------------------------------
SPRAY = ('Aplique 4 atomizaciones del spray para la garganta que viene en su '
         'receta (bencidamina, Vantal®), dirigidas al fondo de la garganta, '
         '4 veces al día, mientras tenga molestia.')

SORBOS = ('Tome agua a pequeños sorbos con frecuencia: una garganta seca duele '
          'más.')

MIEL = 'Puede tomar una cucharada de miel sola o en té tibio, nunca caliente.'

HUMIDIFICADOR = ('Use un humidificador en su habitación por las noches, sobre '
                 'todo si está respirando por la boca.')

VOZ = ('Hable poco las primeras 24 a 48 horas. No grite, y tampoco susurre: '
       'susurrar fuerza las cuerdas vocales más que hablar en voz baja.')

IRRITANTES = ('Las bebidas muy calientes y la comida picante irritan más una '
              'garganta lastimada: evítelas mientras le moleste. El alcohol y '
              'el tabaco ya están suspendidos por su cirugía, con los plazos '
              'que vienen en esta hoja.')

# --- lo que cambia entre las dos versiones -----------------------------------
FRIO_GENERAL = ('Lo frío alivia: nieve, paletas de hielo, gelatina fría o agua '
                'fresca. Los primeros días prefiera sabores no ácidos '
                '—vainilla, coco, fresa, mango—: el limón y los cítricos arden '
                'en una garganta irritada.')

CARAMELOS_GENERAL = 'Puede chupar caramelos o pastillas para la garganta.'

FRIO_SUBMANDIBULAR = (
    'Lo frío alivia, pero use sólo lo que su dieta de la glándula '
    'submandibular ya permite: gelatina fría, yogur natural, papaya, purés '
    'tibios o fríos y agua fresca a sorbos. Nada ácido.')

CARAMELOS_SUBMANDIBULAR = (
    'En su caso NO chupe caramelos, pastillas para la garganta ni chicles, '
    'aunque sean para esto: su dieta de la glándula submandibular los prohíbe '
    'durante 14 días porque estimulan la saliva. Con el spray y lo frío de '
    'esta lista es suficiente; desde el día 15 ya los puede usar.')

AVISO = ('Avísenos por el WhatsApp de seguimiento (' + WHATSAPP + ') si la '
         'ronquera dura más de 3 días o si el dolor de garganta empeora en '
         'lugar de mejorar. Si siente dificultad para respirar o un ruido '
         'agudo al respirar, llame de inmediato al teléfono de urgencias: eso '
         'no espera.')


def renglones(submandibular):
    return [
        SPRAY,
        FRIO_SUBMANDIBULAR if submandibular else FRIO_GENERAL,
        MIEL,
        CARAMELOS_SUBMANDIBULAR if submandibular else CARAMELOS_GENERAL,
        SORBOS,
        HUMIDIFICADOR,
        VOZ,
        IRRITANTES,
    ]


def version_de(obj):
    return hashlib.sha256(json.dumps(
        {k: v for k, v in obj.items() if k != 'version'},
        ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]


# =============================================================================
# 1) LAS RECETAS — el spray, en las nueve plantillas
# =============================================================================
rx = json.load(open(RUTA_RX, encoding='utf-8'))
P = {p['id']: p for p in rx['plantillas']}

VANTAL = {
    'hoja': 'general',
    'nombre': ('Bencidamina 0.15 %, solución bucofaríngea, frasco CON '
               'ATOMIZADOR de 40 ml (Vantal® spray).'),
    'indicacion': ('4 atomizaciones dirigidas al fondo de la garganta, 4 veces '
                   'al día, mientras tenga molestia por el tubo de la '
                   'anestesia. No se traga; si queda la boca adormecida un '
                   'momento, es esperado.'),
    'cantidad': '1 frasco con atomizador de 40 ml',
    'duracion': 'Mientras tenga molestia, habitualmente 3 a 5 días',
    'rescate': True,
    'si': {'tubo': True},
}

for pid in sorted(set(RECETA_DE.values())):
    if pid not in P:
        raise SystemExit('falta la plantilla de receta ' + pid)
    p = P[pid]

    if any(m.get('si', {}).get('tubo') for m in p.get('medicamentos', [])):
        raise SystemExit('ya estaba aplicado en la receta ' + pid)

    preg = p.setdefault('preguntas', [])
    if any(q['id'] == 'tubo' for q in preg):
        raise SystemExit('la pregunta tubo ya existe en la receta ' + pid)
    preg.append(dict(PREGUNTA))

    # El spray va al final de la hoja general, después de los de horario y
    # junto a los demás de «según necesidad».
    p['medicamentos'].append(dict(VANTAL))

    antes = p.get('version')
    p['version'] = version_de(p)
    print('receta     %-18s %s -> %s' % (pid, antes, p['version']))

rx['version'] = hashlib.sha256(json.dumps(
    {'plantillas': rx['plantillas'], 'hojas': rx['hojas'],
     'horas': rx.get('horas')},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:16]
rx['generado'] = datetime.date.today().isoformat()

with open(RUTA_RX, 'w', encoding='utf-8') as f:
    json.dump(rx, f, ensure_ascii=False, indent=1)
print('catálogo de recetas       ' + rx['version'])


# =============================================================================
# 2) LAS HOJAS POSTOPERATORIAS — la pregunta y el bloque condicionado
# =============================================================================
ind = json.load(open(RUTA_IND, encoding='utf-8'))
H = {h['id']: h for h in ind['hojas']}

ALARMA = re.compile(r'Signos de alarma', re.I)

for hid in POSTOP:
    if hid not in H:
        raise SystemExit('falta la hoja ' + hid)
    h = H[hid]

    if any(b.get('si', {}).get('tubo') for b in h['bloques']):
        raise SystemExit('ya estaba aplicado en la hoja ' + hid)

    preg = h.setdefault('preguntas', [])
    if any(q['id'] == 'tubo' for q in preg):
        raise SystemExit('la pregunta tubo ya existe en la hoja ' + hid)
    preg.append(dict(PREGUNTA))

    # ¿Esta hoja prohíbe los caramelos? No se da por hecho por el id: se lee.
    todo = json.dumps(h, ensure_ascii=False)
    prohibe = ('chicles y caramelos' in todo)
    if prohibe != (hid in SUBMANDIBULAR):
        raise SystemExit(
            'en ' + hid + ' la prohibición de caramelos ' +
            ('apareció' if prohibe else 'desapareció') +
            ' y la lista SUBMANDIBULAR dice lo contrario: revísala antes de '
            'imprimir una hoja que se contradiga')

    # El bloque va al final de «lo que es normal», justo antes de los signos
    # de alarma: la molestia de garganta ES normal, y ahí no hay que renumerar
    # ninguna sección —entra como subtítulo de la que ya existe—.
    pos = None
    for i, b in enumerate(h['bloques']):
        if b['t'] == 'h' and ALARMA.search(str(b.get('x', ''))):
            pos = i
            break
    if pos is None:
        raise SystemExit('no encontré los signos de alarma en ' + hid)

    nuevos = [
        {'t': 'h2', 'x': TITULO, 'si': {'tubo': True}},
        {'t': 'p', 'x': ENTRADA, 'si': {'tubo': True}},
        {'t': 'ul', 'x': renglones(hid in SUBMANDIBULAR), 'si': {'tubo': True}},
        {'t': 'nota', 'x': AVISO, 'alarma': True, 'si': {'tubo': True}},
    ]
    h['bloques'][pos:pos] = nuevos

    antes = h['version']
    h['version'] = version_de(h)
    print('hoja       %-18s %s -> %s  (%s)'
          % (hid, antes, h['version'],
             'dieta submandibular' if hid in SUBMANDIBULAR else 'general'))


# =============================================================================
# 3) LA HOJA PREOPERATORIA — genérica, sin pregunta
# =============================================================================
pre = H['preoperatorias']
if any(b['t'] == 'h' and 'garganta' in str(b.get('x', '')).lower()
       for b in pre['bloques']):
    raise SystemExit('ya estaba aplicado en la hoja preoperatoria')

VIEJO_TABACO = ('Tabaco, vapeo, IQOS, parches, chicles y bolsitas de nicotina: '
                'suspéndalos 4 semanas antes y 4 semanas después de la '
                'cirugía. El vapeo y los parches también cuentan.')
NUEVO_TABACO = ('Tabaco, vapeo, IQOS, parches, chicles y bolsitas de nicotina: '
                'suspéndalos 4 semanas antes y 4 semanas después de la '
                'cirugía. El vapeo y los parches también cuentan. Dejarlo '
                'también le irrita menos la garganta con el tubo de la '
                'anestesia.')

cambiados = 0
for b in pre['bloques']:
    if b['t'] != 'ul':
        continue
    for k, x in enumerate(b['x']):
        if x == VIEJO_TABACO:
            b['x'][k] = NUEVO_TABACO
            cambiados += 1
if cambiados != 1:
    raise SystemExit('en la preoperatoria encontré ' + str(cambiados) +
                     ' renglones de tabaco y esperaba 1')

PRE_BLOQUES = [
    {'t': 'h', 'x': 'Su garganta después de la anestesia'},
    {'t': 'p', 'x': ('Si su cirugía se hace con anestesia general, durante el '
                     'procedimiento se coloca un tubo o una mascarilla en la vía '
                     'aérea para que usted respire. Conviene que lo sepa de '
                     'antemano para que no la tome por sorpresa.')},
    {'t': 'ul', 'x': [
        'Es normal sentir la garganta irritada, con ardor, molestia al pasar '
        'saliva o la voz ronca durante los 2 o 3 días siguientes a la cirugía. '
        'Cede sola.',
        'No lo confunda con el dolor de garganta de la lista de abajo: ése es '
        'el de ANTES de la cirugía, y ése sí hay que avisarnos, porque puede '
        'ser una infección y obligarnos a cambiar la fecha.',
        'Si le molesta, sus indicaciones de alta le dirán exactamente qué '
        'hacer, y su receta traerá un spray para la garganta si lo necesita.',
    ]},
]

pos = None
for i, b in enumerate(pre['bloques']):
    if b['t'] == 'h' and str(b.get('x', '')).startswith('Cuándo avisarnos'):
        pos = i
        break
if pos is None:
    raise SystemExit('no encontré «Cuándo avisarnos» en la preoperatoria')
pre['bloques'][pos:pos] = PRE_BLOQUES

antes = pre['version']
pre['version'] = version_de(pre)
print('hoja       %-18s %s -> %s  (genérica, sin pregunta)'
      % ('preoperatorias', antes, pre['version']))


# =============================================================================
# Redes de seguridad
# =============================================================================
for hid in POSTOP:
    todo = json.dumps(H[hid], ensure_ascii=False)
    # Nada de protocolo de anestesiología en material de paciente. La lista es
    # literal y específica a propósito: un primer intento buscaba «manómetro»
    # y reventó contra el «baumanómetro digital» con el que la paciente se toma
    # la presión en casa. Una red que grita donde no debe se acaba apagando, y
    # entonces ya no cuida nada.
    for prohibido in ('presión del globo', 'cmH₂O', 'cmH2O', 'i-gel',
                      'taponamiento faríngeo', 'tubo preformado',
                      'óxido nitroso', 'extubación', 'extubar',
                      'gárgara de regaliz', 'dexametasona 8 mg',
                      'Dexametasona 8 mg'):
        if prohibido in todo:
            raise SystemExit('se colló algo del protocolo interno («' +
                             prohibido + '») en la hoja ' + hid)
    # La promesa del spray tiene que existir en la receta de la misma cirugía,
    # y con la MISMA dosis. Una hoja que dice 4 atomizaciones y una receta que
    # dijera otra cosa es peor que no decir nada: la paciente tiene las dos
    # hojas en la mano al mismo tiempo.
    p = P[RECETA_DE[hid]]
    spray = [m for m in p['medicamentos'] if m.get('si', {}).get('tubo')]
    if 'Vantal' in todo and not spray:
        raise SystemExit('la hoja ' + hid + ' promete el spray y su receta (' +
                         RECETA_DE[hid] + ') no lo lleva')
    if '4 atomizaciones' not in todo:
        raise SystemExit('la hoja ' + hid + ' no dice la dosis del spray')
    if not any('4 atomizaciones' in m['indicacion'] for m in spray):
        raise SystemExit('la receta ' + RECETA_DE[hid] +
                         ' no dice la misma dosis que su hoja')

ind['version'] = hashlib.sha256(json.dumps(
    {'hojas': ind['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
ind['generado'] = datetime.date.today().isoformat()

with open(RUTA_IND, 'w', encoding='utf-8') as f:
    json.dump(ind, f, ensure_ascii=False, indent=1)

print('catálogo de indicaciones  ' + ind['version'])
