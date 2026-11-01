#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA VENDA UNA SEMANA, Y LA FAJA DESPUÉS
=======================================

Lo que cambia y por qué
-----------------------
El médico lo razonó así (1-nov-2026): al retirar la malla hemostática la
paciente queda con más riesgo de sangrado, y es justo entonces cuando la
compresión hace más falta. Antes la hoja hacía lo contrario de lo que su
razonamiento pide: la faja de tiempo completo terminaba el día 7, cuatro
días después de quitar la malla, y de ahí en adelante sólo era para dormir.

    antes   faja facial 24 h los días 1–7 · sólo para dormir del 8 al 21
    ahora   VENDA toda la semana 1 · faja 24 h la semana 2 ·
            faja sólo para dormir la semana 3, y se suspende

Son los mismos 21 días de compresión, repartidos distinto: ahora la más
firme cae sobre la semana en que sale la malla y la que sigue.

Lo que esto arrastra
--------------------
1. **El baño.** La hoja decía «puede bañarse y lavarse el cabello a partir
   del día 3». Con venda hasta el día 7 eso es imposible, y dejarlo ahí
   sería dejar dos renglones que se contradicen en la misma hoja. Ahora el
   baño completo y el lavado de cabello empiezan al retirarse la venda.
   **Eso significa una semana sin lavarse el cabello.**            ←CONFIRMAR
   Si prefiere lavárselo usted en la cita de las 72 horas al abrir la venda,
   se escribe así y se cambia en un renglón.

2. **Las citas.** La venda se abre en la cita de las 72 horas (malla) y en
   la del día 5 (puntos), y se vuelve a poner. El médico lo dijo: «no es el
   fin del mundo quitar la venda y volver a ponerla». Pero la paciente tiene
   que saberlo de antemano o va a creer que algo salió mal.

3. **«Acuda con su faja puesta»** ya no aplica la primera semana, cuando lo
   que trae es la venda.

Dónde se aplica y dónde NO
--------------------------
Sólo en `deep_plane`, el facelift sin láser.

En `deep_plane_co2` y en `facial_combinada` NO se toca, y no por descuido:
en esas dos la piel va tratada con láser de CO₂, y el protocolo del láser
—confirmado por el médico en octubre— manda lavarla dos veces al día y
mantenerla con Cicaplast y vaselina, «nunca seca ni un momento». Una venda
ocluida una semana sobre esa piel contradice eso de frente, y no me toca a
mí decidir cuál de las dos indicaciones gana.                      ←CONFIRMAR

Uso:  python3 cambiar_venda_y_faja_deep_plane.py [indicaciones.json]
      (después de corregir_cita_24h_deep_plane.py)
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'

HOJAS = ['deep_plane']

VIEJA_FAJA = ('Faja facial: úsela las 24 horas durante los primeros 7 días; '
              'solo se retira para bañarse. Del día 8 al 21 úsela únicamente '
              'para dormir.')

NUEVA_VENDA = (
    'Venda: se queda puesta toda la primera semana. No se la quite, no la '
    'afloje y no la moje. En sus citas se la abrimos para revisarla y hacer '
    'lo que toque, y se la volvemos a poner nosotros: eso es parte del '
    'tratamiento y no significa que algo vaya mal. Si se le afloja o se le '
    'recorre en casa, no intente acomodarla usted: avísenos.')

NUEVA_FAJA = (
    'Faja facial: empieza el día 8, al retirarse la venda. Úsela las 24 '
    'horas del día durante toda la segunda semana —sólo se la quita para '
    'bañarse—. La tercera semana úsela únicamente para dormir, y al terminar '
    'el día 21 se suspende. La compresión no se suelta cuando sale la malla: '
    'ahí es cuando más se necesita.')

VIEJO_BANO = ('Puede bañarse y lavarse el cabello a partir del día 3 (72 '
              'horas), con agua tibia —nunca caliente— y champú de bebé. No '
              'frote las incisiones; deje correr el agua y seque con toques '
              'suaves con una toalla limpia.')

NUEVO_BANO = ('Mientras traiga la venda —toda la primera semana— báñese de '
              'la cintura para abajo y no se moje la cabeza. El baño completo '
              'y el lavado de cabello empiezan el día 8, al retirarse la '
              'venda, con agua tibia —nunca caliente— y champú de bebé. No '
              'frote las incisiones; deje correr el agua y seque con toques '
              'suaves con una toalla limpia.')

VIEJA_INCISION = ('Limpie las incisiones 2 veces al día con agua y jabón '
                  'neutro, seque con gasa y aplique una capa delgada del '
                  'ungüento indicado en su receta, hasta el retiro de todos '
                  'los puntos.')

NUEVA_INCISION = ('Mientras traiga la venda no toque las incisiones ni meta '
                  'nada debajo: las revisamos y las curamos nosotros en cada '
                  'cita. A partir del día 8, al retirarse la venda, límpielas '
                  'usted 2 veces al día con agua y jabón neutro, seque con '
                  'gasa y aplique una capa delgada del ungüento indicado en '
                  'su receta, hasta el retiro de todos los puntos.')

VIEJO_CITAS = ('Todas son obligatorias. Recepción agenda y confirma cada cita '
               'con usted por WhatsApp. Acuda con su faja puesta y con un '
               'acompañante a las citas de las primeras 2 semanas.')

NUEVO_CITAS = ('Todas son obligatorias. Recepción agenda y confirma cada cita '
               'con usted por WhatsApp. Acuda con lo que traiga puesto esa '
               'semana —la venda la primera, la faja después— y con un '
               'acompañante a las citas de las primeras 2 semanas.')

cat = json.load(open(RUTA, encoding='utf-8'))
H = {h['id']: h for h in cat['hojas']}


def cambia_en_ul(hoja, viejo, nuevos):
    """Sustituye un renglón de lista por uno o varios. Devuelve cuántas veces."""
    hechos = 0
    for b in hoja['bloques']:
        if b['t'] != 'ul':
            continue
        for k, x in enumerate(list(b['x'])):
            if x == viejo:
                b['x'][k:k + 1] = list(nuevos)
                hechos += 1
    return hechos


def cambia_en_p(hoja, viejo, nuevo):
    hechos = 0
    for b in hoja['bloques']:
        if b['t'] == 'p' and b.get('x') == viejo:
            b['x'] = nuevo
            hechos += 1
    return hechos


for hid in HOJAS:
    if hid not in H:
        raise SystemExit('falta la hoja ' + hid)
    h = H[hid]

    if NUEVA_VENDA in json.dumps(h, ensure_ascii=False):
        raise SystemExit('ya estaba aplicado en ' + hid)

    n1 = cambia_en_ul(h, VIEJA_FAJA, [NUEVA_VENDA, NUEVA_FAJA])
    if n1 != 1:
        raise SystemExit('en ' + hid + ' encontré ' + str(n1) +
                         ' renglones de faja y esperaba 1')

    n2 = cambia_en_ul(h, VIEJO_BANO, [NUEVO_BANO])
    if n2 != 1:
        raise SystemExit('en ' + hid + ' encontré ' + str(n2) +
                         ' renglones de baño y esperaba 1')

    n4 = cambia_en_ul(h, VIEJA_INCISION, [NUEVA_INCISION])
    if n4 != 1:
        raise SystemExit('en ' + hid + ' encontré ' + str(n4) +
                         ' renglones de cuidado de incisiones y esperaba 1')

    n3 = cambia_en_p(h, VIEJO_CITAS, NUEVO_CITAS)
    if n3 != 1:
        raise SystemExit('en ' + hid + ' encontré ' + str(n3) +
                         ' párrafos de citas y esperaba 1')

    # Red de seguridad: que no quede viva ninguna promesa del esquema viejo.
    todo = json.dumps(h, ensure_ascii=False)
    for frase in ('lavarse el cabello a partir del día 3',
                  'las 24 horas durante los primeros 7 días',
                  'con su faja puesta'):
        if frase in todo:
            raise SystemExit('quedó viva la frase: «' + frase + '» en ' + hid)

    antes = h['version']
    h['version'] = hashlib.sha256(json.dumps(
        {k: v for k, v in h.items() if k != 'version'},
        ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]
    print('%-18s %s -> %s  (venda 1 semana · faja semanas 2 y 3 · baño al día 8)'
          % (hid, antes, h['version']))

cat['version'] = hashlib.sha256(json.dumps(
    {'hojas': cat['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

print('catálogo  ' + cat['version'])
