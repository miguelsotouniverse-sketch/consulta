#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LA HOJA DE RIBXCAR SOLA
========================

Qué pidió
---------
El 2-nov-2026: «podemos incluir una hoja de recomendaciones postoperatorias de
ribxcar, paciente que solo le hicieron ribxcar».

Lo que había antes era un riesgo, no un hueco
---------------------------------------------
La hoja de lipoescultura traía `ribxcar` entre sus palabras de coincidencia, y
la plantilla de receta de Body360 también. O sea: a una paciente de RibXcar
SOLA el sistema ya le proponía la hoja y la receta de una lipoescultura
completa —faja tres meses, cuidado de heridas, rivaroxabán 10 días,
antihipertensivos— para un procedimiento percutáneo de quince minutos. No
faltaba una hoja: sobraba una equivocada.

Lo que el médico confirmó (2-nov-2026)
--------------------------------------
· Es **percutánea**, sin herida que curar.
· Es **ambulatoria**: se va el mismo día, y no hay radiografía de control.
· **El corset entra desde el día 1** —no el día 4 como cuando acompaña una
  lipo—, se ajusta un broche por semana hasta la semana 8 y de ahí se
  estabiliza hasta el mes 6.
· **No lleva anticoagulación**: «es una cirugía de 15 minutos y es percutánea».

De eso se desprende el resto de la hoja: sin heridas no hay curación ni retiro
de puntos; sin internamiento la hoja carga sola todo el peso de los signos de
alarma de la primera noche; y al no haber radiografía, la alarma respiratoria
no puede apoyarse en un estudio previo que descarte nada.

Lo que NO está en esta hoja, y por qué              ←CONFIRMAR (los dos puntos)
------------------------------------------
1. **Los antihipertensivos y la toma de presión en casa.** Las ocho hojas de
   alta los traen, y la receta de Body360 también. Aquí los dejé fuera por la
   misma razón por la que el médico quitó la anticoagulación: el amlodipino y
   el metoprolol están ahí para mantener la sistólica baja y evitar que se
   acumule sangre bajo la piel despegada, y en un procedimiento percutáneo de
   quince minutos no hay piel despegada. Si los quiere, son estos tres bloques
   —los dos medicamentos, la toma cada 2 horas y el captopril de rescate— y se
   copian de la hoja de lipoescultura tal cual.
2. **El clonazepam de rescate.** Su regla dice «rescate de ansiedad en toda
   cirugía ABIERTA». Ésta no lo es, así que no lo puse. Si considera que seis
   meses de corset lo justifican, se agrega en un renglón.

Lo que viene COPIADO y lo que es NUEVO
--------------------------------------
Todo lo que ya existía aprobado se copia de la hoja de lipoescultura buscándolo
por su texto, no reteclándolo: si allá cambia una palabra, este script se
detiene en vez de copiar algo distinto a lo aprobado. Lo nuevo es lo propio del
tórax —respirar hondo, abrazar la almohada al toser, el enfisema subcutáneo, el
corset que de pronto ya no cierra— y va marcado abajo con ←NUEVO.

Los plazos del calendario de actividades son MÍOS y van todos ←CONFIRMAR. Los
puse conservadores a propósito: en una remodelación costal lo que desplaza un
cartílago es cargar, torcerse y estirar los brazos por encima de la cabeza, y
preferí pecar de prudente y que usted los recorte.

Uso:  python3 construir_hoja_ribxcar.py [indicaciones.json]
      (después de cambiar_venda_y_faja_deep_plane.py y ANTES de
       agregar_molestia_garganta.py, que le pone la pregunta del tubo)
"""

import json
import hashlib
import datetime
import sys

RUTA = sys.argv[1] if len(sys.argv) > 1 else 'indicaciones.json'

cat = json.load(open(RUTA, encoding='utf-8'))
H = {h['id']: h for h in cat['hojas']}

if 'ribxcar' in H:
    raise SystemExit('la hoja de ribxcar ya existe')
if 'lipoescultura' not in H:
    raise SystemExit('falta la hoja de lipoescultura, de donde se copia')

LIPO = H['lipoescultura']


# ---------------------------------------------------------------------------
# Copiar, no reteclear. Si el original cambió, esto truena.
# ---------------------------------------------------------------------------
def ren(fragmento):
    """Un renglón de lista de la hoja de lipoescultura, buscado por su texto."""
    hallados = [x for b in LIPO['bloques'] if b['t'] == 'ul'
                for x in b['x'] if fragmento in x]
    if len(hallados) != 1:
        raise SystemExit('en lipoescultura busqué «' + fragmento + '» y hallé ' +
                         str(len(hallados)) + ' renglones; esperaba 1')
    return hallados[0]


def parr(fragmento):
    """Un párrafo de la hoja de lipoescultura, buscado por su texto."""
    hallados = [str(b['x']) for b in LIPO['bloques']
                if b['t'] == 'p' and fragmento in str(b.get('x', ''))]
    if len(hallados) != 1:
        raise SystemExit('en lipoescultura busqué el párrafo «' + fragmento +
                         '» y hallé ' + str(len(hallados)) + '; esperaba 1')
    return hallados[0]


def masculino(t):
    """«la faja» → «el corset», con la concordancia que arrastra.

    Los renglones de la prenda se copian de la hoja de lipoescultura, donde la
    prenda es una FAJA y todo concuerda en femenino. Aquí la prenda es un
    CORSET. Cada sustitución se verifica: si una deja de aplicar porque allá
    cambió la redacción, es mejor que truene aquí que imprimir la hoja con una
    falta de concordancia.
    """
    pares = [('dos fajas', 'dos corsets'), ('la faja', 'el corset'),
             ('alternarlas', 'alternarlos'), ('lavarlas', 'lavarlos'),
             ('aflójela', 'aflójelo')]
    hechos = 0
    for viejo, nuevo in pares:
        if viejo in t:
            t = t.replace(viejo, nuevo)
            hechos += 1
    if not hechos:
        raise SystemExit('nada que concordar en «' + t[:60] + '»: ese renglón '
                         'ya no habla de la faja, revísalo a mano')
    return t


def fila(primera_celda):
    """Una fila del calendario de actividades de lipoescultura."""
    for b in LIPO['bloques']:
        if b['t'] != 'tabla':
            continue
        for f in b['x']:
            if f and f[0] == primera_celda:
                return list(f)
    raise SystemExit('no hallé la fila «' + primera_celda + '» en lipoescultura')


# ---------------------------------------------------------------------------
# La hoja
# ---------------------------------------------------------------------------
hoja = {
    'id': 'ribxcar',
    'nombre': 'RibXcar — remodelación costal',
    'titulo': 'Recomendaciones postoperatorias — RibXcar',
    'coincide': ['ribxcar', 'rib xcar', 'remodelacion costal',
                 'remodelación costal'],
    # La entrada es la misma de todas las hojas de alta: copiada, no escrita.
    'entrada': LIPO['entrada'],
    'bloques': [

        {'t': 'h2', 'x': 'Datos del procedimiento'},
        {'t': 'tabla', 'cols': ['Campo', 'Dato'], 'x': [
            ['Procedimiento', 'RibXcar® — remodelación costal guiada por ultrasonido'],
            ['Zonas tratadas', ''],
        ]},

        # ---------------- primeras 72 horas ----------------
        {'t': 'h', 'x': 'Primeras 72 horas'},
        # ←NUEVO: el encuadre del procedimiento. La paciente tiene que saber
        # que no tiene heridas y que lo que va a sentir es la caja torácica,
        # o va a buscar una herida que no existe y a asustarse de un dolor
        # que sí es esperado.
        {'t': 'p', 'x': (
            'Su procedimiento fue percutáneo: los cartílagos de las costillas '
            'se remodelaron a través de punciones, guiadas por ultrasonido, sin '
            'abrir la piel y sin heridas que curar. Dura alrededor de quince '
            'minutos y usted se va a casa el mismo día. Lo que más va a sentir '
            'es la caja torácica: molestia al respirar hondo, al toser, al reír '
            'y al incorporarse. Eso es lo esperado.')},
        {'t': 'ul', 'x': [
            # ←NUEVO y deliberadamente primero: es la indicación que previene
            # la complicación más probable de una cirugía de costillas.
            'RESPIRE HONDO: 10 respiraciones profundas y lentas cada hora '
            'mientras esté despierta, aunque le moleste. Es la indicación más '
            'importante de esta hoja. Cuando algo duele, uno respira corto sin '
            'darse cuenta, y respirar corto durante días deja zonas del pulmón '
            'sin abrir.',
            # ←NUEVO
            'Si necesita toser o estornudar, abrace una almohada contra el '
            'pecho y sosténgala firme: duele mucho menos y le permite toser de '
            'verdad, que es lo que limpia el pulmón.',
            # ←NUEVO
            'Tome sus analgésicos a sus horas los primeros días, no «sólo si '
            'duele». El dolor controlado es lo que le permite respirar hondo y '
            'caminar.',
            ren('Caminar 5–10 minutos cada 1–2 horas'),
            ren('Mover tobillos en círculos'),
            # ←NUEVO: en lipoescultura el mareo al levantarse es por pérdida
            # de líquido; aquí el problema es distinto —empujarse con los
            # brazos tira de las costillas—, así que el renglón se reescribe.
            'Levántese en dos tiempos y sin empujarse con los brazos: siéntese '
            'primero en la orilla de la cama 1 o 2 minutos y luego póngase de '
            'pie. Para incorporarse, ruede de lado y use las piernas.',
            # ←NUEVO ←CONFIRMAR el plazo de 2 semanas
            'Duerma boca arriba o semisentada, con almohadas que le sostengan '
            'la espalda. No duerma boca abajo ni de lado las primeras 2 '
            'semanas.',
            # ←NUEVO ←CONFIRMAR el plazo de 2 semanas
            'No estire los brazos por encima de la cabeza ni alcance cosas '
            'altas las primeras 2 semanas: ese movimiento tira directamente de '
            'las costillas. Todo a la altura del pecho, y pida ayuda.',
            # ←CONFIRMAR: en lipoescultura son 24–48 horas; aquí lo dejé en 24
            # porque es ambulatoria y de quince minutos.
            'Acompañada las primeras 24 horas, y no se bañe sola la primera vez.',
        ]},

        # ---------------- el corset ----------------
        {'t': 'h', 'x': 'El corset'},
        # ←NUEVO, pero el contenido es el que él confirmó el 2-nov-2026.
        {'t': 'p', 'x': (
            'El corset es el tratamiento, no un accesorio: es lo que mantiene '
            'en su lugar lo que se remodeló mientras el cartílago consolida. Se '
            'lo colocamos el mismo día y lo trae puesto desde el día 1.')},
        {'t': 'tabla', 'cols': ['Periodo', 'Uso', 'Ajuste'], 'x': [
            ['Día 1 a semana 8', 'Día y noche. Sólo se lo quita para bañarse',
             'Un broche más cada semana'],
            # ←CONFIRMAR: «luego estabilizar hasta mes 6» lo escribí como día y
            # noche todo ese tiempo. Si después de la semana 8 puede bajar a
            # medio tiempo —como la faja de la lipo, que pasa a 12 horas—, se
            # cambia esta celda y nada más.
            ['Semana 8 al mes 6', 'Día y noche',
             'Ya no se aprieta más: se queda en el broche al que llegó'],
        ]},
        {'t': 'ul', 'x': [
            # La faja es femenina y el corset no. Los renglones copiados traen
            # «aflójela», «alternarlas», «lavarlas»; dejarlos así imprime una
            # hoja con faltas de concordancia en manos de la paciente, y la
            # primera versión de este script lo hizo. Las sustituciones van
            # explícitas y abajo hay una red que revienta si sobrevive alguna.
            masculino(ren('Ajuste: firme, nunca doloroso')),
            # ←NUEVO
            'Un broche por semana, no más rápido. Apretarlo antes de tiempo no '
            'adelanta el resultado, y sí puede dolerle y hacerla respirar corto.',
            masculino(ren('Pliegues: revise que la faja no forme arrugas')),
            masculino(ren('Higiene: tenga dos fajas para alternarlas')),
            # Preferencia que él ya tenía documentada para la faja y que aplica
            # igual aquí.
            'Use una camiseta de algodón de tirantes debajo del corset, para '
            'que las varillas y los broches no le marquen la piel.',
            # ←NUEVO
            'Si se lo quitó para bañarse, vuelva a ponérselo enseguida y con la '
            'piel bien seca. No pase el día sin él.',
        ]},

        # ---------------- baño ----------------
        {'t': 'h', 'x': 'Baño'},
        # ←NUEVO: la buena noticia de un procedimiento percutáneo, dicha de
        # frente para que no busque curaciones que no le tocan.
        {'t': 'p', 'x': (
            'No tiene heridas que curar: fueron punciones. No hay puntos que '
            'retirar ni curaciones que hacer en casa.')},
        {'t': 'ul', 'x': [
            # ←CONFIRMAR el plazo de 24 horas
            'Puede bañarse en regadera a partir de las 24 horas, con el corset '
            'quitado y acompañada la primera vez.',
            ren('Agua tibia, nunca caliente'),
            # ←CONFIRMAR las 4 semanas (copiado de lipoescultura)
            ren('Regadera, no tina, alberca, jacuzzi, mar ni vapor'),
            # ←NUEVO, adaptado del de lipoescultura: aquí lo que hay que secar
            # bien es la piel bajo el corset.
            'Secado a toques con una toalla limpia; seque muy bien la piel '
            'antes de volver a ponerse el corset.',
            # ←NUEVO, adaptado: en lipoescultura habla de incisiones.
            'No aplique cremas, pomadas, alcohol ni remedios caseros sobre los '
            'puntos de punción, salvo indicación.',
            ren('Calor y frío local: no aplique compresas calientes'),
        ]},

        # ---------------- alimentación ----------------
        {'t': 'h', 'x': 'Alimentación e hidratación'},
        {'t': 'ul', 'x': [
            ren('Primer día: dieta blanda'),
            ren('Proteína en cada comida'),
            # ←NUEVO: propio del tórax.
            'Evite las bebidas con gas los primeros días: distienden el abdomen '
            'y empujan las costillas desde abajo.',
            ren('Estreñimiento: es frecuente por los analgésicos'),
            ren('Alcohol: ninguno por al menos 2 semanas'),
            ren('Tabaco y vapeador: ninguno por al menos 4 semanas'),
        ]},

        # ---------------- actividades ----------------
        {'t': 'h', 'x': 'Calendario de actividades'},
        # ←NUEVO ←CONFIRMAR: el párrafo resume los plazos de la tabla, que son
        # míos. Si corrige la tabla, este párrafo se corrige con ella.
        {'t': 'p', 'x': (
            'Lo que desplaza un cartílago recién remodelado es cargar, torcerse '
            'y estirar los brazos por encima de la cabeza. Esos tres son los '
            'plazos que más importan de esta tabla.')},
        {'t': 'tabla', 'cols': ['Actividad', 'A partir de', 'Nota'], 'x': [
            fila('Caminar'),
            # ←CONFIRMAR todas las filas de aquí abajo: los plazos son míos.
            ['Trabajo de escritorio / home office', 'Día 3–5',
             'Pararse y caminar cada hora'],
            ['Manejar', 'Día 5–7',
             'Sin analgésicos que den sueño, y sólo cuando pueda girar el '
             'tronco y frenar sin molestia'],
            ['Estirar los brazos por encima de la cabeza', 'Semana 2',
             'Antes de eso, todo a la altura del pecho'],
            ['Relaciones sexuales', 'Semana 2', 'Sin presión sobre el tórax'],
            ['Ejercicio ligero (caminadora, bicicleta fija)', 'Semana 3',
             'Sin impacto y sin usar los brazos'],
            ['Girar el tronco, agacharse a recoger', 'Semana 4',
             'Doble las rodillas en lugar de torcer la cintura'],
            ['Alberca, mar, tina, vapor', 'Semana 4', ''],
            ['Cargar objetos pesados (más de 5 kg)', 'Semana 6',
             'Incluye cargar niños'],
            ['Ejercicio completo (pesas, correr, abdomen)', 'Semana 8',
             'Nada de abdomen ni de pecho antes'],
            ['Deporte de contacto', 'Mes 6',
             'Hasta que el cartílago haya consolidado'],
        ]},

        # ---------------- lo normal ----------------
        {'t': 'h', 'x': 'Qué es normal'},
        # ←NUEVO ←CONFIRMAR el plazo del día 5 al 7
        {'t': 'p', 'x': (
            'El contorno final no se ve pronto. La cintura se va definiendo a '
            'lo largo de los meses, conforme el cartílago consolida en su nueva '
            'posición y usted sigue usando el corset.')},
        {'t': 'ul', 'x': [
            # ←NUEVO ←CONFIRMAR el plazo
            'Molestia en las costillas al respirar hondo, toser, reír, '
            'estornudar o incorporarse. Es lo esperado y mejora de forma clara '
            'a partir del día 5 al 7.',
            # ←NUEVO
            'Sensación de opresión o de traer algo apretado alrededor del '
            'tórax. Parte es el corset y parte la inflamación.',
            # ←NUEVO, adaptado del renglón de moretones de lipoescultura.
            'Moretones en los flancos y por debajo de las mamas, que cambian de '
            'morado a verde y amarillo. Desaparecen en 2 a 4 semanas.',
            ren('Inflamación que aumenta al final del día'),
            # ←NUEVO, adaptado: en lipoescultura dice «la piel tratada».
            'Adormecimiento u hormigueo de la piel de los flancos. La '
            'sensibilidad regresa en semanas a meses.',
            # ←NUEVO ←CONFIRMAR: los tronidos son frecuentes después de
            # trabajar cartílago costal, pero no se lo he oído a usted.
            'Tronidos o chasquidos aislados al moverse o estirarse las primeras '
            'semanas.',
            ren('Cansancio las primeras 1–2 semanas'),
            ren('Cambios de ánimo los primeros días'),
        ]},

        # ---------------- alarma ----------------
        {'t': 'h', 'x': 'Signos de alarma', 'alarma': True},
        {'t': 'p', 'x': parr('llámenos al teléfono de urgencias del consultorio')},
        {'t': 'h2', 'x': 'Llámenos de inmediato, sin esperar'},
        {'t': 'ul', 'x': [
            ren('Falta de aire, dolor en el pecho, tos con sangre'),
            # ←NUEVO: lo que distingue a esta cirugía. Un dolor que crece con
            # cada respiración, o que ya no deja llenar el pecho, es el aviso
            # de que algo pasó en la pleura, y esta paciente no trae
            # radiografía de control que lo haya descartado.
            'Dolor que aumenta cada vez que respira, o que ya no la deja '
            'llenar el pecho de aire.',
            # ←NUEVO: enfisema subcutáneo, dicho en palabras que se puedan
            # reconocer con los dedos.
            'Un burbujeo o crujido al tocarse la piel del tórax o del cuello, '
            'como si hubiera burbujas o papel celofán debajo.',
            ren('Desmayo, confusión o somnolencia excesiva'),
        ]},
        {'t': 'h2', 'x': 'Llámenos el mismo día'},
        {'t': 'ul', 'x': [
            ren('Fiebre de 38 °C o más'),
            ren('Dolor que empeora en lugar de mejorar'),
            # ←NUEVO, adaptado: en lipoescultura dice «una zona».
            'Una zona del flanco que crece rápido, se pone tensa y muy '
            'dolorosa, o que se siente como una bolsa de líquido.',
            # ←NUEVO, adaptado: aquí no hay incisiones, hay punciones.
            'Enrojecimiento que se extiende, calor, pus o mal olor en alguno de '
            'los puntos de punción.',
            # Se queda a propósito aunque no lleve anticoagulante: justamente
            # porque no lo lleva.
            ren('Dolor, hinchazón o calor en una sola pantorrilla o pierna'),
            # ←NUEVO: el corset es el tratamiento, así que un corset que
            # cambió es un dato clínico y no una molestia de la prenda.
            'El corset le aprieta de pronto mucho más que antes, o ya no puede '
            'cerrarlo en el broche en el que iba.',
            ren('Náusea o vómito que no le permite tomar líquidos'),
            ren('Mareo persistente, palidez marcada').replace(
                ' u orina muy escasa', ''),
        ]},

        # ---------------- cierre ----------------
        {'t': 'h', 'x': 'Citas y constancia de entrega'},
        {'t': 'p', 'x': parr('Sus citas de control se coordinan con recepción')},
        {'t': 'p', 'x': parr('Recibí y entendí estas indicaciones')},
        {'t': 'firmas', 'x': ['Paciente']},
    ],
}

# ---------------------------------------------------------------------------
# `ribxcar` deja de apuntar a la hoja de lipoescultura
# ---------------------------------------------------------------------------
# Si se queda en las dos, la aplicación no sugiere NINGUNA —`hojaSugerida()`
# sólo sugiere cuando coincide exactamente una— y el médico escoge a mano.
# Peor sería dejarla sólo en lipoescultura: ahí sí le propondría activamente la
# hoja equivocada.
#
# CONSECUENCIA QUE HAY QUE SABER: una paciente de Body360 5D —lipo CON
# RibXcar— escrita como «Body360 5D (RibXcar)» va a coincidir con las dos
# hojas, y entonces la aplicación no sugiere ninguna. Hoy sí sugiere la de
# lipoescultura, que es la correcta para ella. Se recupera nombrando el
# procedimiento de la paciente de RibXcar sola como «RibXcar aislada» y dejando
# sólo ese término aquí.                                         ←CONFIRMAR
antes = list(LIPO.get('coincide', []))
LIPO['coincide'] = [c for c in antes if 'ribxcar' not in c.lower().replace(' ', '')]
if len(LIPO['coincide']) == len(antes):
    raise SystemExit('esperaba quitar «ribxcar» de la hoja de lipoescultura y '
                     'no estaba: revisa si alguien ya lo movió')

# La hoja nueva va junto a la de lipoescultura, que es su familia.
i = [k for k, h in enumerate(cat['hojas']) if h['id'] == 'lipoescultura'][0]
cat['hojas'].insert(i + 1, hoja)


# ---------------------------------------------------------------------------
# Redes de seguridad
# ---------------------------------------------------------------------------
def plano(t):
    import unicodedata
    t = unicodedata.normalize('NFD', str(t).lower())
    return ''.join(c for c in t if unicodedata.category(c) != 'Mn').strip()


# Igual que `hojaSugerida()` en la aplicación: debe coincidir EXACTAMENTE una.
for proc in ('RibXcar', 'ribxcar', 'Remodelación costal'):
    p = plano(proc)
    halladas = [h['id'] for h in cat['hojas']
                if any(p.find(plano(c)) >= 0 for c in h.get('coincide', []))]
    if halladas != ['ribxcar']:
        raise SystemExit('«' + proc + '» coincide con ' + str(halladas) +
                         ' y esperaba sólo con ribxcar')

todo = json.dumps(hoja, ensure_ascii=False)
# Nada de lo que esta cirugía no tiene.
for sobra in ('rivaroxab', 'retiro de puntos', 'amlodipino', 'metoprolol',
              'drenaje', 'faja etapa'):
    if sobra.lower() in todo.lower():
        raise SystemExit('quedó «' + sobra + '» en una hoja que no lo lleva')
# Y ninguna concordancia en femenino heredada de la faja.
for falta in ('faja', 'aflójela', 'alternarlas', 'lavarlas'):
    if falta in todo:
        raise SystemExit('quedó «' + falta + '» en la hoja: la prenda de '
                         'RibXcar es un corset, no una faja')
# Y sí lo que sí: respirar hondo es la razón de ser de la primera sección.
for falta in ('RESPIRE HONDO', 'día 1', 'mes 6', 'burbujeo o crujido'):
    if falta not in todo:
        raise SystemExit('falta «' + falta + '» en la hoja de ribxcar')

hoja['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in hoja.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]
LIPO['version'] = hashlib.sha256(json.dumps(
    {k: v for k, v in LIPO.items() if k != 'version'},
    ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()[:8]

cat['version'] = hashlib.sha256(json.dumps(
    {'hojas': cat['hojas']}, ensure_ascii=False, sort_keys=True
).encode('utf-8')).hexdigest()[:16]
cat['generado'] = datetime.date.today().isoformat()

with open(RUTA, 'w', encoding='utf-8') as f:
    json.dump(cat, f, ensure_ascii=False, indent=1)

n = sum(len(b['x']) if isinstance(b['x'], list) else 1 for b in hoja['bloques'])
print('hoja       ribxcar            nueva -> %s  (%d bloques, %d renglones)'
      % (hoja['version'], len(hoja['bloques']), n))
print('hoja       lipoescultura      -> %s  (ya no responde a «ribxcar»)'
      % LIPO['version'])
print('catálogo   ' + cat['version'])
