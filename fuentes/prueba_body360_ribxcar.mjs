/* ============================================================
   PRUEBA PERMANENTE — BODY360 5D
   lipoescultura + RibXcar (remodelación costal)

   El 25-nov-2026 el médico preguntó si había indicaciones de alta para esa
   combinación. Las había sólo de nombre: la paciente se llevaba la hoja de
   lipoescultura y todo el corset se despachaba en un renglón.

   Lo que esta prueba defiende, en orden de gravedad:

     · QUE EL CORSET LLEGUE AL MES 6. El renglón viejo terminaba en la semana
       8, así que quien leyera esa hoja entendía que ahí se acababa el
       tratamiento. Es el hueco que motivó la hoja.
     · QUE EL CORSET EMPIECE EL DÍA 3. Él lo fijó el 26-nov-2026: en la
       combinación es el día 3, no el día 1 de la RibXcar sola ni el día 4 que
       decía la hoja de lipoescultura, que quedó corregida.
     · QUE SE DIGA EL ORDEN DE LAS DOS PRENDAS. Trae faja y corset a la vez;
       si la hoja no dice cuál va encima, lo adivina.
     · QUE NO SE IMPRIMA HTML. El párrafo de las prendas llevaba un <b> y
       salió literal en el papel al construirla.
     · QUE RESPIRAR HONDO SIGA SIENDO LA PRIMERA INDICACIÓN. Es lo que la hoja
       de lipoescultura no tenía y lo que de verdad previene la complicación
       pulmonar de una caja torácica que duele.
     · QUE EL BAÑO ESPERE 48 HORAS. La RibXcar sola permite 24 porque no hay
       heridas; aquí sí las hay, las de la lipo.

   Uso: node prueba_body360_ribxcar.mjs [index.html]
   ============================================================ */
import playwright from '/opt/npm-tools/node_modules/playwright/index.js';
const { chromium } = playwright;
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

function dondeEste(n){
  for (const s of [n, '../' + n, '/home/claude/' + n, '/mnt/user-data/outputs/' + n]){
    try { return readFileSync(resolve(s), 'utf8'); } catch(e){}
  }
  throw new Error('No encuentro ' + n);
}

const HTML = resolve(process.argv[2] || 'index.html');
const esquema = JSON.parse(dondeEste('campos.json'));
const ind     = JSON.parse(dondeEste('indicaciones.json'));
const rec     = JSON.parse(dondeEste('recetas.json'));
let constantes = JSON.parse(dondeEste('constantes.json'));
if (constantes.campos) constantes = constantes.campos;

let fallas = 0;
function revisa(nombre, bien, detalle){
  console.log((bien ? '✓ ' : '✗ ') + nombre + (bien ? '' : '   → ' + (detalle || '')));
  if (!bien) fallas++;
}

const H = {}; ind.hojas.forEach(h => H[h.id] = h);
const C = H['body360_ribxcar'];
const L = H['lipoescultura'];
const R = H['ribxcar'];

revisa('la hoja de Body360 5D existe', !!C, 'no está en el catálogo');
revisa('siguen existiendo las dos de origen', !!L && !!R, '');

if (C){
  const plano = JSON.stringify(C.bloques);
  const titulos = C.bloques.filter(b => b.t === 'h' || b.t === 'h2').map(b => b.x);

  /* ---- lo que él definió ---- */
  revisa('el corset empieza el DÍA 3', /día 3/.test(plano), '');
  revisa('y no queda ningún otro día de corset',
    !/día 1\b/.test(plano) && !/día 4/.test(plano), '');
  revisa('EL CORSET LLEGA AL MES 6', /mes 6/i.test(plano),
    'el hueco que motivó esta hoja');
  revisa('y de la semana 8 al mes 6 ya no se aprieta',
    /Ya no se aprieta más/.test(plano), '');
  revisa('dice que el corset va POR ENCIMA de la faja',
    /por encima de la faja/i.test(plano), '');
  revisa('y dice el orden completo de las capas',
    /su piel, la camiseta de algodón, la faja y hasta arriba el corset/.test(plano), '');
  revisa('la faja conserva su esquema de 6 + 6 semanas',
    /FAJA · semanas 1–6/.test(plano) && /FAJA · semanas 7–12/.test(plano) &&
    /12 horas al día/.test(plano), '');
  revisa('un broche por semana, hasta la semana 8',
    /Un broche más cada semana/.test(plano) &&
    /Un broche por semana, no más rápido/.test(plano), '');

  /* ---- lo que ninguna de las dos hojas sueltas le daba ---- */
  revisa('RESPIRE HONDO está, y es el primer renglón de las 72 horas',
    (C.bloques.filter(b => b.t === 'ul')[0] || {x:[]}).x[0]
      .startsWith('RESPIRE HONDO'), '');
  revisa('dice abrazar una almohada para toser',
    /almohada contra el pecho/.test(plano), '');
  revisa('prohíbe estirar los brazos 2 semanas',
    /No estire los brazos por encima de la cabeza/.test(plano), '');
  revisa('trae el signo de alarma propio del corset',
    /El corset le aprieta de pronto/.test(plano), '');
  revisa('trae los dos signos de alarma del tórax',
    /Dolor que aumenta cada vez que respira/.test(plano) &&
    /burbujeo o crujido/.test(plano), '');
  revisa('la camiseta de algodón dice dónde va',
    /contra la piel, debajo de la faja/.test(plano), '');

  /* ---- el choque entre las dos hojas ---- */
  revisa('NO queda la forma corta de levantarse, la que permite los brazos',
    !/Levantarse despacio/.test(plano), '');
  revisa('y sí la que prohíbe empujarse con los brazos',
    /sin empujarse con los brazos/.test(plano), '');

  /* ---- el baño: manda el plazo de la lipo ---- */
  revisa('el baño espera 48 horas, no 24', /48 horas/.test(plano) &&
    !/24 horas, con el corset quitado/.test(plano), '');
  revisa('y el secado nombra las DOS prendas',
    /volver a ponerse la faja y el corset/.test(plano), '');
  revisa('los pliegues también nombran las dos',
    /ni la faja ni el corset formen arrugas/.test(plano), '');

  /* ---- el papel no puede llevar etiquetas ---- */
  revisa('no hay HTML literal en el texto',
    !/<b>|<\/b>|<i>|<br|<p>/.test(plano), 'saldría impreso tal cual');

  /* ---- el calendario: el más lento de los dos, sin inventar ---- */
  const cal = C.bloques.filter(b => b.t === 'tabla')
    .filter(b => b.x.some(f => /^Caminar/.test(f[0])))[0];
  revisa('el calendario existe', !!cal, '');
  if (cal){
    const f = n => (cal.x.filter(r => r[0].startsWith(n))[0] || [])[1];
    revisa('escritorio toma el plazo largo, el de la lipo',
      f('Trabajo de escritorio') === 'Día 7–10', f('Trabajo de escritorio'));
    revisa('cargar peso toma el plazo largo, el de RibXcar',
      f('Cargar objetos pesados') === 'Semana 6', f('Cargar objetos pesados'));
    revisa('ejercicio completo toma el plazo largo, el de RibXcar',
      f('Ejercicio completo') === 'Semana 8', f('Ejercicio completo'));
    revisa('el deporte de contacto espera al mes 6',
      f('Deporte de contacto') === 'Mes 6', f('Deporte de contacto'));
    revisa('y estirar los brazos entra en el calendario',
      !!f('Estirar los brazos'), '');
  }

  /* ---- higiene general de la hoja ---- */
  revisa('sigue preguntando si hubo tubo', C.preguntas.some(q => q.id === 'tubo'), '');
  const garganta = C.bloques.filter(b => /garganta/i.test(JSON.stringify(b.x || '')));
  revisa('y lo de la garganta cuelga de esa respuesta',
    garganta.length > 0 && garganta.every(b => (b.si || {}).tubo === true), '');
  revisa('no se propone sola por una palabra del procedimiento',
    (C.coincide || []).length === 0, (C.coincide || []).join(', '));
  const dup = C.bloques.filter(b => b.t === 'ul' && new Set(b.x).size !== b.x.length);
  revisa('ninguna lista repite un renglón', dup.length === 0, '');
  revisa('no tiene texto facial ni de mama',
    !/párpado|facelift|pezón|areola|brasier/i.test(plano), '');
  ['Primeras 72 horas','Sus dos prendas: faja y corset','Baño y cuidado de heridas',
   'Calendario de actividades','Qué es normal','Signos de alarma']
    .forEach(s => revisa('conserva la sección «' + s + '»',
      titulos.includes(s), titulos.join(' · ')));
}

/* ---- la hoja de lipoescultura, que también se corrigió ---- */
if (L){
  const pl = JSON.stringify(L.bloques);
  revisa('la hoja de lipoescultura ya NO dice día 4', !/día 4/.test(pl), '');
  revisa('dice día 3 y que el corset sigue al mes 6',
    /día 3/.test(pl) && /mes 6/.test(pl), '');
  revisa('y manda a la hoja completa de 5D',
    /hoja de Body360 5D/.test(pl), '');
}

/* ---- la receta: se comprobó que no hacía falta una nueva ---- */
const P = {}; rec.plantillas.forEach(p => P[p.id] = p);
const nB = new Set(P['body360'].medicamentos.map(m => m.nombre));
const soloRib = P['ribxcar'].medicamentos.map(m => m.nombre).filter(n => !nB.has(n));
revisa('la receta de RibXcar sigue siendo subconjunto de la de Body360, ' +
  'así que la 5D no necesita plantilla propia',
  soloRib.length === 0, 'RibXcar ya trae algo que Body360 no: ' + soloRib.join(', '));

/* ---- en el navegador: que de verdad se imprima ---- */
const nav = await chromium.launch();
const pag = await nav.newPage({ viewport: { width: 816, height: 1056 } });
await pag.route('**/*', (r) =>
  r.request().url().startsWith('file://') ? r.continue() : r.abort());
await pag.goto('file://' + HTML);

const r = await pag.evaluate(async ({ esquema, ind, constantes }) => {
  const out = {};
  ESQUEMA = esquema; CONSTANTES = constantes;
  INDICACIONES = ind; INDICACIONES_AL = Date.now();
  FOLIO = 'P-PRUEBA'; DOC_ID = 'ffff'; CORREO = 'x@y.mx'; PENDIENTE_DICTADO = {};
  TIPO = DOCUMENTOS.filter(d => d.id === 'indicaciones_alta')[0];
  VALORES = { expediente_folio:'P-PRUEBA', paciente_nombres:'María',
              paciente_apellido_paterno:'Prueba', paciente_sexo:'Femenino',
              ind_tubo: 'si' };
  HOJA = INDICACIONES.hojas.filter(h => h.id === 'body360_ribxcar')[0];
  out.cargada = !!HOJA;
  armaImpresion();
  const papel = document.getElementById('impresion').innerText;
  out.titulo    = /BODY360 5D/i.test(papel);
  out.corsetDia3= /el corset empieza el día 3/i.test(papel);
  out.mes6      = /mes 6/i.test(papel);
  out.encima    = /EL CORSET VA POR ENCIMA DE LA FAJA/.test(papel);
  out.respire   = /RESPIRE HONDO/.test(papel);
  out.sinHTML   = !/<b>|<\/b>/.test(papel);
  out.garganta  = /Molestia de garganta/.test(papel);
  out.largo     = papel.length;

  VALORES['ind_tubo'] = '';
  out.faltaTubo = sinContestarHoja().join(' | ');
  return out;
}, { esquema, ind, constantes });

revisa('la hoja carga en la aplicación', r.cargada, '');
revisa('el papel lleva el título de Body360 5D', r.titulo, '');
revisa('el papel dice que el corset empieza el día 3', r.corsetDia3, '');
revisa('el papel dice el mes 6', r.mes6, '');
revisa('el papel dice que el corset va encima de la faja', r.encima, '');
revisa('el papel abre con RESPIRE HONDO', r.respire, '');
revisa('el papel NO imprime etiquetas HTML', r.sinHTML,
  'salieron <b> en la hoja de la paciente');
revisa('el papel trae la garganta cuando hubo tubo', r.garganta, '');
revisa('sin contestar el tubo la hoja no se imprime',
  (r.faltaTubo || '').length > 0, r.faltaTubo);

await nav.close();
console.log(fallas ? `\n${fallas} caso(s) mal`
  : '\nLa hoja de Body360 5D existe: corset desde el día 3, encima de la faja, ' +
    'hasta el mes 6, y con todo lo del tórax que la hoja de lipo no tenía.');
process.exit(fallas ? 1 : 0);
