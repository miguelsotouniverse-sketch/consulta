#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA HOJA DE ALTA DE LA COMBINADA DE CUERPO
==========================================
abdominoplastia + lipoescultura + mastopexia con implantes

Por qué existe
--------------
El 24-nov-2026 el médico operó esa combinación y pidió la hoja de alta. No
había ninguna que sirviera, y el hueco era más grande de lo que parecía:
**abdominoplastia no existía en el sistema**, ni sola ni combinada. Entregarle
la hoja de lipoescultura habría dejado a la paciente sin una sola línea sobre
lo único que de verdad la limita los primeros días, que es el abdomen.

Lo que él definió ese día, y que no se inventó
-----------------------------------------------
  · NO lleva drenajes. Por eso esta hoja no los menciona en ninguna parte.
  · Camina semiflexionada y duerme con las piernas elevadas UNA SEMANA.
  · La prenda es la misma de siempre: faja Marena de primera etapa con su
    esquema de 6 + 6 semanas, y el brasier postquirúrgico de la mastopexia,
    los dos tal cual, sin cambios.

De dónde sale el resto
----------------------
Se fusionan la hoja de lipoescultura y la de mastopexia, copiando bloques por
índice. Donde las dos dicen lo mismo —presión arterial, garganta, citas— se
copia UNA vez. Donde cada una aporta lo suyo —faja y brasier, heridas y
cicatrices— van las dos secciones completas. Donde los plazos difieren, manda
el más lento de los tres procedimientos.

EL CHOQUE QUE HUBO QUE RESOLVER, y que es la razón de leer la hoja entera
--------------------------------------------------------------------------
Las dos hojas se contradicen de frente en cómo levantarse de la cama:

    mastopexia:      «apóyese en las piernas, NO en los brazos»
                     (para no jalar el pectoral ni las cicatrices)
    abdominoplastia: lo habitual es girarse de lado y empujarse CON LOS BRAZOS
                     (para no usar la prensa abdominal)

Una paciente con las dos cirugías no puede hacer ninguna de las dos cosas. Si
se copiaban las dos hojas sin leerlas, la paciente acababa con dos renglones
que se anulan entre sí — y cuando dos instrucciones se contradicen, la
paciente escoge la que le acomoda. Aquí se resuelve por la tercera vía, que es
la única que no fuerza ni el pecho ni el abdomen: que la levanten, y que la
cama ya esté inclinada para no tener que incorporarse desde plano.

Lo que es nuevo y necesita su revisión renglón por renglón
-----------------------------------------------------------
Todo lo del abdomen va marcado  # ←NUEVO. Los plazos que él no dio van
marcados  # ←CONFIRMAR: son los del calendario de actividades, donde la
abdominoplastia obliga a alargar lo que lipoescultura y mastopexia tenían.

Uso:  python3 construir_hoja_cuerpo_combinada.py [indicaciones.json]
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'

# --- los plazos que él no dio ----------------------------------------------
DIAS_FLEXIONADA = 7          # [stated] 24-nov-2026: una semana
DIA_ENDEREZARSE = 8          # ←CONFIRMAR  el día que empieza a enderezarse
OFICINA = 'Día 10–14'        # ←CONFIRMAR  lipo decía 7–10, mastopexia 5–7
MANEJAR = 'Día 10–14'        # ←CONFIRMAR  frenar de golpe usa el abdomen
AVION_CORTO = 'Semana 3'     # ←CONFIRMAR  las dos decían semana 2
EJ_LIGERO = 'Semana 4'       # ←CONFIRMAR  las dos decían semana 3
EJ_COMPLETO = 'Semana 8'     # ←CONFIRMAR  lipo 6, mastopexia 6–8

cat = json.load(open(RUTA, encoding='utf-8'))
H = {h['id']: h for h in cat['hojas']}

if 'cuerpo_combinada' in H:
    raise SystemExit('ya existe la hoja combinada de cuerpo')

LIPO = H['lipoescultura']
MAST = H['mastopexia']


def copia(x):
    return json.loads(json.dumps(x, ensure_ascii=False))


def bl(hoja, n):
    """Un bloque aprobado, copiado por índice. Nunca se vuelve a teclear."""
    return copia(hoja['bloques'][n])


def puntos(hoja, n, quitar=(), desde=0):
    """Los renglones de una lista ya aprobada, menos los que aquí no aplican."""
    xs = copia(hoja['bloques'][n])['x'][desde:]
    for q in quitar:
        antes = len(xs)
        xs = [x for x in xs if q.lower() not in x.lower()]
        if len(xs) == antes:
            raise SystemExit('no encontré el renglón a quitar: «%s»' % q)
    return xs


B = []

# ---------------------------------------------------------------- portada
B.append({'t': 'h2', 'x': 'Datos del procedimiento'})
B.append({'t': 'tabla', 'x': [
    ['Procedimiento', 'Abdominoplastia + Lipoescultura Body360® + '
                      'Mastopexia con implantes'],
    ['Zonas tratadas', ''],
]})

# ------------------------------------------------------- primeras 72 horas
B.append({'t': 'h', 'x': 'Primeras 72 horas'})
B.append({'t': 'p', 'x':
    'Descanse boca arriba, con la espalda elevada y las rodillas dobladas, y '
    'camine varias veces al día desde el mismo día de la cirugía. Caminar es '
    'la medida más importante para prevenir coágulos en las piernas; la '
    'postura es lo que protege su abdomen.'})
B.append({'t': 'ul', 'x': [
    # ←NUEVO  la postura, que ahora tiene que servir a las tres cirugías
    'Posición para dormir y descansar: boca arriba, con la espalda elevada '
    '30–45° (dos o tres almohadas o un respaldo) y una o dos almohadas bajo '
    'las rodillas, para que el abdomen quede sin tensión. No duerma de lado '
    'ni boca abajo.',
    'Caminar 5–10 minutos cada 1–2 horas mientras esté despierta, siempre '
    'acompañada los primeros días.',
    # ←NUEVO  la resolución del choque entre las dos hojas
    'Para levantarse: pida que la ayuden y suba primero el respaldo de la '
    'cama. No se impulse con los brazos —jalan el pecho— ni haga fuerza con '
    'el abdomen para incorporarse. Ya sentada en la orilla, espere 1–2 '
    'minutos antes de ponerse de pie: es común sentir mareo.',
    'Brazos pegados al cuerpo: no los levante por arriba de los hombros ni '
    'empuje o jale con ellos. Puede comer, peinarse con cuidado y usar el '
    'celular.',
    # ←NUEVO  abdominoplastia
    'Al toser, estornudar o reírse, abrace una almohada contra el abdomen: '
    'sostiene la herida y duele mucho menos.',
    'Mover tobillos en círculos y de arriba abajo 10 veces cada hora mientras '
    'esté acostada.',
    'Respiraciones profundas: 10 cada hora, para mantener los pulmones bien '
    'expandidos.',
    'Salida de líquido teñido de sangre por las incisiones es normal y '
    'esperado las primeras 24–72 horas. Use toallas sanitarias o gasas y '
    'proteja cama y asientos.',
    'Siempre acompañada las primeras 24–48 horas; no se bañe sola la primera '
    'vez.',
]})

# --------------------------------------------- presión arterial (idénticas)
B.append(bl(LIPO, 5)); B.append(bl(LIPO, 6))
B.append(bl(LIPO, 7)); B.append(bl(LIPO, 8))

# ------------------------------------------------------- ←NUEVO  el abdomen
B.append({'t': 'h', 'x': 'Su abdomen: cómo moverse la primera semana'})
B.append({'t': 'p', 'x':
    'En la abdominoplastia se tensa la piel del abdomen. Enderezarse por '
    'completo los primeros días tira de esa piel justo donde está la herida, '
    'y es lo que hace que una cicatriz se abra o se ensanche. Por eso la '
    'primera semana se camina un poco encorvada, a propósito.'})
B.append({'t': 'ul', 'x': [
    'Camine ligeramente inclinada hacia adelante, con las rodillas un poco '
    'dobladas, durante los primeros ' + str(DIAS_FLEXIONADA) + ' días. No se '
    'estire ni se enderece de golpe, ni siquiera para alcanzar algo de un '
    'estante.',
    'Duerma y descanse con las piernas elevadas y las rodillas dobladas toda '
    'esa primera semana.',
    'A partir del día ' + str(DIA_ENDEREZARSE) + ' enderécese poco a poco, un '
    'poco más cada día, sin forzar. Si siente que tira, todavía no es tiempo.',
    'No cargue nada, no empuje puertas pesadas y no haga ningún esfuerzo que '
    'le apriete el abdomen.',
    'Tenga a la mano lo que vaya a necesitar, a la altura de la cintura: '
    'agacharse y estirarse son los dos movimientos que hay que evitar.',
    'El ombligo puede verse amoratado, con costras y con algún punto. '
    'Manténgalo limpio y seco y no le ponga nada: se acomoda solo.',
]})

# ------------------------------------------------------------------- faja
# Se quita el renglón del corset de RibXcar: esta combinación no lo lleva, y
# ofrecerle una prenda que no tiene sólo la confunde.
B.append(bl(LIPO, 9)); B.append(bl(LIPO, 10)); B.append(bl(LIPO, 11))
B.append({'t': 'ul', 'x': puntos(LIPO, 12, quitar=['RibXcar'])})

# ---------------------------------------------------------------- brasier
B.append(bl(MAST, 9)); B.append(bl(MAST, 10)); B.append(bl(MAST, 11))
B.append(bl(MAST, 12))

# -------------------------------------------- baño, heridas y cicatrices
B.append({'t': 'h', 'x': 'Baño, heridas y cicatrices'})
B.append(bl(LIPO, 14))
B.append({'t': 'ul', 'x': [
    'Regadera, no tina, alberca, jacuzzi, mar ni vapor por 4 semanas.',
    'Agua tibia, nunca caliente: el calor aumenta la inflamación y puede '
    'marear. Dé la espalda al chorro para que el agua no golpee directo sobre '
    'las mamas ni sobre la herida del abdomen.',
    'Jabón neutro; deje correr el agua sobre las heridas sin tallarlas.',
    'Secado a toques con toalla limpia; seque muy bien todas las heridas '
    'antes de volver a ponerse la faja y el brasier. Una herida húmeda bajo '
    'la faja se macera.',
    'Cintas adhesivas (si las tiene): no las retire; se caen solas o se '
    'retiran por el equipo médico.',
    'Heridas: manténgalas limpias y secas. No aplique cremas, pomadas, '
    'alcohol ni remedios caseros salvo indicación.',
    'Cicatrices: una vez cerradas por completo, protéjalas del sol con ropa y '
    'protector FPS 50 durante 12 meses. Es normal que se vean rojizas y '
    'firmes los primeros meses.',
    'Calor y frío local: no aplique compresas calientes, bolsas de agua ni '
    'hielo directo. La piel tratada y la del pezón tienen menos sensibilidad '
    'y pueden quemarse sin que lo note.',
]})

# ------------------------------------------------- alimentación (la de lipo)
# La entrada de la hoja de lipo dice «después de una lipoescultura». Aquí son
# tres cirugías y la pérdida de líquido es mayor, no menor: la frase se
# reescribe para que no suene a hoja copiada de otra.
B.append(bl(LIPO, 16))
B.append({'t': 'p', 'x':
    'Beba de 2 a 3 litros de líquidos al día. Después de una cirugía de '
    'contorno corporal el cuerpo pierde líquido por las incisiones, y la '
    'deshidratación causa mareo y desmayos justo cuando usted necesita '
    'levantarse a caminar.'})
B.append({'t': 'ul', 'x': puntos(LIPO, 18, quitar=['Tabaco y vapeador']) + [
    # el renglón de tabaco de la mastopexia dice más y aplica igual aquí
    [x for x in copia(MAST['bloques'][18])['x'] if x.startswith('Tabaco')][0],
]})

# ------------------------------------------------------------- calendario
B.append({'t': 'h', 'x': 'Calendario de actividades'})
B.append({'t': 'p', 'x':
    'Son tres cirugías en un mismo tiempo quirúrgico, así que los plazos son '
    'más largos que los de cualquiera de ellas por separado. La mayoría de '
    'las pacientes vuelve a trabajo de escritorio en 10–14 días y al '
    'ejercicio completo hacia la semana 8.'})
B.append({'t': 'tabla', 'x': [
    ['Caminar', 'Día 0', 'Obligatorio, varias veces al día; semiflexionada la '
                         'primera semana'],
    ['Enderezarse por completo', 'Día ' + str(DIA_ENDEREZARSE),
     'Poco a poco, sin forzar'],                                  # ←CONFIRMAR
    ['Trabajo de escritorio / home office', OFICINA,
     'Pararse y caminar cada hora; sin cargar ni levantar los brazos'],
    ['Manejar', MANEJAR,
     'Sin analgésicos que den sueño, y cuando pueda girar el volante y frenar '
     'de golpe sin dolor'],
    ['Levantar los brazos por arriba de los hombros', 'Semana 3',
     'De forma progresiva'],
    ['Viaje en avión corto (< 3 h)', AVION_CORTO,
     'Con faja y brasier, medias de compresión y caminando en el vuelo; '
     'avísenos antes'],
    ['Viaje largo (> 3 h)', 'Semana 4', 'Solo con autorización'],  # ←CONFIRMAR
    ['Cargar objetos pesados (> 5 kg)', 'Semana 6',
     'Incluye cargar niños, bolsas del súper y maletas'],          # ←CONFIRMAR
    ['Ejercicio ligero (caminadora, bicicleta fija)', EJ_LIGERO,
     'Intensidad baja, sin impacto ni rebote'],
    ['Ejercicio de piernas', 'Semana 5',
     'Sin usar brazos, pecho ni abdomen'],                         # ←CONFIRMAR
    ['Ejercicio completo (pesas, correr, saltar)', EJ_COMPLETO,
     'Con brasier deportivo firme'],
    ['Abdominales', 'Semana 12',
     'Es lo último que se reanuda; pregúntenos antes'],            # ←CONFIRMAR
    ['Dormir de lado', 'Semana 4–6', ''],
    ['Dormir boca abajo', 'Semana 8', ''],
    ['Relaciones sexuales', 'Semana 3',
     'Sin presión sobre el abdomen ni manipulación de las mamas'],  # ←CONFIRMAR
    ['Alberca, mar, tina, vapor', 'Semana 4',
     'Con todas las heridas completamente cerradas'],
    ['Sol directo / bronceado', 'Semana 6–8',
     'Cicatrices cubiertas o con FPS 50 por 12 meses'],
]})

# ----------------------------------------------------------- qué es normal
B.append({'t': 'h', 'x': 'Qué es normal'})
B.append({'t': 'p', 'x':
    'El resultado no se ve en las primeras semanas. La inflamación baja de '
    'forma progresiva, las mamas descienden y se redondean, y el contorno '
    'final se aprecia entre los 3 y los 6 meses.'})
B.append({'t': 'ul', 'x': puntos(LIPO, 25) + [
    'Mamas altas y apretadas las primeras semanas. Descienden y se redondean '
    'de forma progresiva.',
    'Asimetría leve entre un lado y otro mientras baja la inflamación; cada '
    'mama se desinflama a su ritmo.',
    'Sensibilidad del pezón y la areola aumentada, disminuida o con '
    'hormigueo. Suele recuperarse en semanas a meses.',
    'Punzadas o «toques eléctricos» breves: son parte de la recuperación de '
    'los nervios.',
    'Cicatrices rojizas y firmes los primeros 3–6 meses; se aclaran y '
    'suavizan durante el primer año.',
    # ←NUEVO  lo propio de la abdominoplastia
    'Sensación de tirantez en el abdomen al intentar enderezarse. Cede '
    'conforme la piel se adapta, durante las primeras semanas.',
    'Adormecimiento de la piel del abdomen, sobre todo entre el ombligo y la '
    'cicatriz. Es casi constante después de una abdominoplastia y puede durar '
    'muchos meses.',
    'El ombligo amoratado y con costras las primeras semanas.',
]})

# ------------------------------------------------- garganta (la de siempre)
for n in (26, 27, 28, 29):
    B.append(bl(LIPO, n))

# -------------------------------------------------------- signos de alarma
B.append(bl(LIPO, 30)); B.append(bl(LIPO, 31))
B.append(bl(LIPO, 32))
B.append({'t': 'ul', 'x': puntos(LIPO, 33) + [
    'Una mama que crece rápido, se pone tensa, dura y muy dolorosa, mucho más '
    'que la otra.',
    'Pezón o areola que se torna morada oscura, gris o negra, o que se siente '
    'fría.',
    # ←NUEVO  la piel del abdomen y el ombligo
    'Piel del abdomen, sobre todo alrededor del ombligo, que se pone morada '
    'oscura, gris o negra.',
]})
B.append(bl(LIPO, 34))
B.append({'t': 'ul', 'x': puntos(LIPO, 35) + [
    'Una herida que se abre, deja ver tejido o cuyos bordes se separan.',
    # La «bolsa de líquido» ya la dice el renglón que viene de la hoja de
    # lipoescultura. Decirla dos veces con otras palabras no insiste: hace
    # dudar de si son dos cosas distintas.
    'Salida de líquido abundante por cualquier herida.',
]})

# ------------------------------------------------------------------ cierre
for n in (36, 37, 38, 39):
    B.append(bl(LIPO, n))

hoja = {
    'id': 'cuerpo_combinada',
    'nombre': 'Combinada de cuerpo — abdominoplastia + lipoescultura + '
              'mastopexia con implantes',
    'titulo': 'Recomendaciones postoperatorias — Abdominoplastia, '
              'lipoescultura y mastopexia con implantes',
    # Sin `coincide`, igual que las dos combinadas faciales: una combinación
    # se escoge a mano. Si se propusiera sola por la palabra «lipoescultura»,
    # una paciente de lipo sola se llevaría a casa una semana de caminar
    # encorvada que nadie le indicó.
    'coincide': [],
    'entrada': LIPO['entrada'],
    'preguntas': copia(LIPO['preguntas']),
    'bloques': B,
}

# ---------------------------------------------------------------------------
# Redes de seguridad
# ---------------------------------------------------------------------------
plano = json.dumps(B, ensure_ascii=False)

# El médico dijo que esta paciente NO lleva drenajes. Que no se cuele ni la
# palabra: una hoja que habla de drenajes a quien no los trae la deja
# buscándose algo que no tiene.
for palabra in ['drenaje', 'drena', 'penrose', 'succión']:
    if palabra in plano.lower():
        raise SystemExit('la hoja menciona «%s» y esta paciente no lleva '
                         'drenajes' % palabra)

# Que no se haya colado texto facial de las hojas de rostro.
for palabra in ['párpado', 'rostro', 'facelift', 'nariz', 'faja de cuello']:
    if palabra in plano.lower():
        raise SystemExit('texto facial en una hoja de cuerpo: «%s»' % palabra)

# El choque de las dos hojas: no puede quedar el renglón de la mastopexia que
# manda apoyarse en las piernas si también está el del abdomen.
if 'apóyese en las piernas' in plano:
    raise SystemExit('quedó el renglón de la mastopexia que contradice al '
                     'del abdomen')

# Lo que esta hoja existe para decir.
for obliga in ['semiflexionada', 'ombligo', 'Brasier postquirúrgico',
               'Faja etapa 1', 'abdomen']:
    if obliga.lower() not in plano.lower():
        raise SystemExit('falta «%s» en la hoja' % obliga)

# Ningún bloque puede colgar de una pregunta que la hoja no hace.
ids = {q['id'] for q in hoja['preguntas']}
for b in B:
    for clave in (b.get('si') or {}):
        if clave not in ids:
            raise SystemExit('un bloque depende de «%s», que nadie pregunta'
                             % clave)

# Un renglón repetido palabra por palabra en la misma lista es descuido.
for b in B:
    if b['t'] == 'ul' and len(b['x']) != len(set(b['x'])):
        raise SystemExit('hay renglones duplicados en una lista')

hoja['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in hoja.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

# Entra después de la mastopexia, para que las de cuerpo queden juntas.
pos = next(i for i, h in enumerate(cat['hojas']) if h['id'] == 'mastopexia') + 1
cat['hojas'].insert(pos, hoja)

cat['version'] = hashlib.sha256(json.dumps(
    {'hojas': cat['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

n = sum(len(b['x']) if b['t'] in ('ul', 'tabla', 'citas') else 1 for b in B)
print('hoja cuerpo_combinada · versión %s · %d bloques, %d renglones'
      % (hoja['version'], len(B), n))
print('catálogo de indicaciones  %s · %d hojas'
      % (cat['version'], len(cat['hojas'])))
