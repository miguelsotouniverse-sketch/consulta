/* ============================================================
   PRUEBA PERMANENTE — LA COMBINADA DE CUERPO
   abdominoplastia + lipoescultura + mastopexia con implantes

   El 24-nov-2026 el médico operó esa combinación y al ir a imprimir no había
   nada que le sirviera: abdominoplastia no existía en el sistema.

   Lo que esta prueba defiende, en orden de gravedad:

     · QUE EL RELAJANTE NO ENTRE SOLO. Él lo corrigió ese día con estas
       palabras: «estos quedaron retromusculares pero pudieron haber quedado
       retroglandulares, entonces tendrías que preguntar». La ciclobenzaprina
       cuelga de la pregunta del plano, aquí Y en la mastopexia sola.
     · QUE NO SE PIERDA EL ANTICOAGULANTE. Es contorno corporal: abdominoplastia
       más lipo es el escenario trombótico más alto de su consultorio. Si
       alguien reconstruye esta plantilla copiando de la mastopexia, el
       rivaroxabán desaparece sin que nadie lo note.
     · QUE LA HOJA NO HABLE DE DRENAJES. Él dijo que esta paciente no los
       lleva; una hoja que los menciona la deja buscándose algo que no tiene.
     · QUE NO VUELVA EL CHOQUE DE LAS DOS HOJAS. La de mastopexia manda
       apoyarse en las piernas y no en los brazos; la abdominoplastia pide lo
       contrario. Las dos juntas se anulan, y la paciente escoge la que le
       acomoda. La hoja resuelve por la tercera vía: que la ayuden.
     · QUE ESTÉ LO DEL ABDOMEN, que es lo único que ninguna de las dos hojas
       que ya existían podía decir.

   Uso: node prueba_cuerpo_combinada.mjs [index.html]
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
const rec     = JSON.parse(dondeEste('recetas.json'));
const ind     = JSON.parse(dondeEste('indicaciones.json'));
let constantes = JSON.parse(dondeEste('constantes.json'));
if (constantes.campos) constantes = constantes.campos;

let fallas = 0;
function revisa(nombre, bien, detalle){
  console.log((bien ? '✓ ' : '✗ ') + nombre + (bien ? '' : '   → ' + (detalle || '')));
  if (!bien) fallas++;
}

/* ============ 1. LA RECETA, sin navegador ============ */
const P = {}; rec.plantillas.forEach(p => P[p.id] = p);
const C = P['cuerpo_combinada'];
const M = P['mastopexia'];
const B = P['body360'];

revisa('la plantilla combinada de cuerpo existe', !!C, 'no está en el catálogo');
if (C){
  const nombres = C.medicamentos.map(m => m.nombre).join(' | ');
  const cic = C.medicamentos.filter(m => /Ciclobenzaprina/.test(m.nombre))[0];
  const riv = C.medicamentos.filter(m => /Rivaroxab/.test(m.nombre))[0];

  revisa('lleva el anticoagulante: es contorno corporal', !!riv, '');
  revisa('lleva el relajante muscular: hay implantes', !!cic, '');
  revisa('EL RELAJANTE NO ENTRA SOLO: cuelga de la pregunta del plano',
    !!cic && (cic.si || {}).retro === true,
    cic ? JSON.stringify(cic.si) : '');
  revisa('y la pregunta del plano de verdad se hace',
    C.preguntas.some(q => q.id === 'retro'),
    C.preguntas.map(q => q.id).join(', '));
  revisa('la pregunta es obligatoria y se estampa en el pliego impreso',
    C.preguntas.filter(q => q.id === 'retro').every(q => q.obligatoria && q.enPie), '');
  revisa('el anticoagulante NO cuelga de nada: no es opcional',
    !!riv && !riv.si, riv ? JSON.stringify(riv.si) : '');

  ['Amoxicilina','Clindamicina','Paracetamol','Celecoxib','Dexametasona',
   'Pantoprazol','Amlodipino','Metoprolol'].forEach(n =>
    revisa('la receta conserva ' + n, nombres.includes(n), ''));

  /* Ningún renglón puede colgar de algo que esta plantilla no pregunta: si
     cuelga, nunca aparece y la paciente se queda sin el medicamento. */
  const ids = new Set(C.preguntas.map(q => q.id).concat(['c24','menor']));
  const huerfanos = C.medicamentos.filter(m =>
    Object.keys(m.si || {}).some(k => !ids.has(k)));
  revisa('ningún renglón cuelga de una pregunta que nadie hace',
    huerfanos.length === 0, huerfanos.map(m => m.nombre).join(', '));

  /* La combinada es la unión de las dos que ya existían. Si algún día alguien
     le quita un renglón a una de las dos, esto lo detecta. */
  const soloB = B.medicamentos.map(m => m.nombre).filter(n => !nombres.includes(n));
  const soloM = M.medicamentos.map(m => m.nombre).filter(n => !nombres.includes(n));
  revisa('no se perdió ningún renglón de Body360', soloB.length === 0, soloB.join(', '));
  revisa('no se perdió ningún renglón de la mastopexia', soloM.length === 0, soloM.join(', '));

  const alarma = C.alarma.map(a => a.t).join(' ');
  revisa('los signos de alarma cubren el abdomen y el ombligo',
    /ombligo/i.test(alarma), '');
  revisa('cubren la mama', /seno|pezón|areola/i.test(alarma), '');
  revisa('cubren la trombosis', /pantorrilla/i.test(alarma), '');
  revisa('y ninguno se repite palabra por palabra',
    new Set(C.alarma.map(a => a.t)).size === C.alarma.length, '');
}

/* ============ 2. LA MASTOPEXIA SOLA, que también se corrigió ============ */
if (M){
  const cicM = M.medicamentos.filter(m => /Ciclobenzaprina/.test(m.nombre))[0];
  revisa('en la mastopexia sola el relajante TAMBIÉN se pregunta',
    !!cicM && (cicM.si || {}).retro === true,
    cicM ? JSON.stringify(cicM.si) : 'no hay ciclobenzaprina');
  revisa('y ya no queda el aviso de «quítele la marca»',
    !M.avisos.some(a => /quítele la marca/.test(a.texto)), '');
}

/* ============ 3. LA HOJA ============ */
const H = {}; ind.hojas.forEach(h => H[h.id] = h);
const HC = H['cuerpo_combinada'];
revisa('la hoja combinada de cuerpo existe', !!HC, '');

if (HC){
  const plano = JSON.stringify(HC.bloques);
  const titulos = HC.bloques.filter(b => b.t === 'h' || b.t === 'h2').map(b => b.x);

  /* Lo que él definió el 24-nov-2026. */
  revisa('NO menciona drenajes en ninguna parte',
    !/drenaj|penrose/i.test(plano), 'esta paciente no lleva drenajes');
  revisa('manda caminar semiflexionada una semana',
    /7 días/.test(plano) && /inclinada hacia adelante/.test(plano), '');
  revisa('conserva la faja con su esquema de siempre',
    /Faja etapa 1, día y noche/.test(plano) &&
    /Faja etapa 1, 12 horas al día/.test(plano), '');
  revisa('conserva el brasier postquirúrgico',
    /Brasier postquirúrgico, día y noche/.test(plano), '');
  /* Esta combinación no lleva RibXcar: ofrecerle un corset que no tiene
     la deja buscando una prenda inexistente. */
  revisa('no le ofrece el corset de RibXcar, que no lleva',
    !/RibXcar/i.test(plano), '');

  /* EL CHOQUE. Las dos hojas se contradicen y la combinada no puede heredarlo. */
  revisa('NO queda el renglón que manda apoyarse en los brazos',
    !/empújese con los brazos|apóyese en los brazos/i.test(plano), '');
  revisa('NO queda el renglón que manda apoyarse en las piernas',
    !/apóyese en las piernas/i.test(plano), '');
  revisa('y en su lugar dice que la ayuden a levantarse',
    /pida que la ayuden/i.test(plano), '');

  /* Lo propio de la abdominoplastia, que ninguna hoja anterior tenía. */
  revisa('tiene una sección propia para el abdomen',
    titulos.some(t => /abdomen/i.test(t)), titulos.join(' · '));
  revisa('explica el ombligo', /ombligo/i.test(plano), '');
  revisa('dice qué hacer al toser o reírse', /abrace una almohada/i.test(plano), '');
  revisa('dice cuándo empieza a enderezarse', /día 8/i.test(plano), '');

  /* Las tres secciones de prenda y herida tienen que convivir. */
  ['Prenda de compresión','Brasier postquirúrgico','Baño, heridas y cicatrices',
   'Calendario de actividades','Qué es normal','Signos de alarma'].forEach(s =>
    revisa('conserva la sección «' + s + '»', titulos.includes(s), titulos.join(' · ')));

  /* Los plazos de la combinada no pueden ser más cortos que los de las dos
     cirugías por separado: son tres en un mismo tiempo quirúrgico. */
  const cal = HC.bloques.filter(b => b.t === 'tabla')
    .filter(b => b.x.some(f => /Caminar/.test(f[0])))[0];
  revisa('el calendario existe y es uno solo', !!cal, '');
  if (cal){
    const fila = n => (cal.x.filter(f => f[0].startsWith(n))[0] || [])[1];
    revisa('el trabajo de escritorio se alarga respecto de lipo y mastopexia',
      fila('Trabajo de escritorio') === 'Día 10–14', fila('Trabajo de escritorio'));
    revisa('el ejercicio completo se alarga a la semana 8',
      /Semana 8/.test(fila('Ejercicio completo') || ''), fila('Ejercicio completo'));
    revisa('los abdominales son lo último', !!fila('Abdominales'), '');
    revisa('el calendario manda caminar desde el día 0',
      fila('Caminar') === 'Día 0', fila('Caminar'));
  }

  /* La pregunta del tubo sigue viva: de ella depende el texto de la garganta. */
  revisa('sigue preguntando si hubo tubo', HC.preguntas.some(q => q.id === 'tubo'), '');
  const garganta = HC.bloques.filter(b => /garganta/i.test(JSON.stringify(b.x || '')));
  revisa('y todo lo de la garganta cuelga de esa respuesta',
    garganta.length > 0 && garganta.every(b => (b.si || {}).tubo === true),
    garganta.length + ' bloques');

  /* No se escoge sola: una combinación propuesta por una palabra suelta le
     daría a una paciente de lipo sola una semana de caminar encorvada. */
  revisa('no se propone sola por una palabra del procedimiento',
    (HC.coincide || []).length === 0, (HC.coincide || []).join(', '));

  /* Ningún renglón repetido dentro de una misma lista. */
  const dup = HC.bloques.filter(b => b.t === 'ul' && new Set(b.x).size !== b.x.length);
  revisa('ninguna lista repite un renglón', dup.length === 0, '');

  /* Que no se haya colado texto de las hojas faciales. */
  revisa('no tiene texto facial',
    !/párpado|facelift|rinoplastia|faja de cuello/i.test(plano), '');
}

/* ============ 4. EN EL NAVEGADOR: que de verdad se arme e imprima ============ */
const nav = await chromium.launch();
const pag = await nav.newPage({ viewport: { width: 816, height: 1056 } });
await pag.route('**/*', (r) =>
  r.request().url().startsWith('file://') ? r.continue() : r.abort());
await pag.goto('file://' + HTML);

const r = await pag.evaluate(async ({ esquema, rec, ind, constantes }) => {
  const out = {};
  const espera = (ms) => new Promise(s => setTimeout(s, ms));
  ESQUEMA = esquema; CONSTANTES = constantes;
  RECETAS = rec; RECETAS_AL = Date.now();
  INDICACIONES = ind; INDICACIONES_AL = Date.now();
  FOLIO = 'P-PRUEBA'; DOC_ID = 'ffff'; CORREO = 'x@y.mx';
  PENDIENTE_DICTADO = {};

  /* --- la receta, con el plano contestado que NO --- */
  TIPO = DOCUMENTOS.filter(d => d.id === 'receta_post')[0];
  VALORES = {
    expediente_folio:'P-PRUEBA', paciente_nombres:'María', paciente_apellido_paterno:'Prueba',
    paciente_sexo:'Femenino', paciente_edad:'42',
    rx_plantilla:'cuerpo_combinada',
    rx_peni:'no', rx_sulfa:'no', rx_renal:'no', rx_sintram:'', rx_tubo:'si',
    rx_retro:'no'
  };
  armaReceta();
  await espera(150);
  let r1 = (VALORES['rx_renglones'] || []);
  out.sinRetro_ciclo = r1.some(x => /Ciclobenzaprina/.test(x.nombre) && !x.fuera);
  out.sinRetro_riva  = r1.some(x => /Rivaroxab/.test(x.nombre) && !x.fuera);
  out.sinRetro_total = r1.filter(x => !x.fuera).length;

  /* --- y con el plano contestado que SÍ ---
     Por el camino real: el médico CAMBIA la respuesta en el selector de la
     pantalla. Volver a llamar armaReceta() no recalcula —eso se comprobó al
     escribir esta prueba— y habría dado un falso negativo. Lo que importa
     defender es justo esto: que corregir la respuesta vuelva a meter el
     renglón, porque el médico se puede equivocar al contestar. */
  const sel = document.querySelector('[data-campo="rx_retro"]');
  out.haySelectorDelPlano = !!sel;
  sel.value = 'si';
  sel.dispatchEvent(new Event('change', { bubbles: true }));
  await espera(250);
  let r2 = (VALORES['rx_renglones'] || []);
  out.conRetro_ciclo = r2.some(x => /Ciclobenzaprina/.test(x.nombre) && !x.fuera);
  out.conRetro_total = r2.filter(x => !x.fuera).length;

  /* --- sin contestar el plano: la receta no se imprime --- */
  sel.value = '';
  sel.dispatchEvent(new Event('change', { bubbles: true }));
  await espera(250);
  out.faltaPlano = faltantesReceta().join(' | ');

  /* --- la hoja --- */
  TIPO = DOCUMENTOS.filter(d => d.id === 'indicaciones_alta')[0];
  VALORES = {
    expediente_folio:'P-PRUEBA', paciente_nombres:'María',
    paciente_apellido_paterno:'Prueba', paciente_sexo:'Femenino',
    ind_tubo: 'si'
  };
  HOJA = INDICACIONES.hojas.filter(h => h.id === 'cuerpo_combinada')[0];
  out.hojaCargada = !!HOJA;
  armaImpresion();
  const papel = document.getElementById('impresion').innerText;
  out.papelAbdomen   = /SU ABDOMEN/i.test(papel);
  out.papelFaja      = /Faja etapa 1/.test(papel);
  out.papelBrasier   = /Brasier postquirúrgico/.test(papel);
  out.papelGarganta  = /Molestia de garganta/.test(papel);
  out.papelOmbligo   = /ombligo/i.test(papel);
  out.papelSinDrenaje= !/drenaj/i.test(papel);
  out.papelTitulo    = /ABDOMINOPLASTIA/i.test(papel);
  out.papelLargo     = papel.length;

  /* sin contestar el tubo, la hoja no se imprime */
  VALORES['ind_tubo'] = '';
  out.faltaTubo = sinContestarHoja().join(' | ');

  return out;
}, { esquema, rec, ind, constantes });

revisa('la receta se arma en la aplicación', r.sinRetro_total > 10,
  r.sinRetro_total + ' renglones');
revisa('con plano NO retromuscular, el relajante no sale',
  r.sinRetro_ciclo === false, 'salió la ciclobenzaprina sin indicación');
revisa('pero el anticoagulante sí, pase lo que pase con el plano',
  r.sinRetro_riva === true, '');
revisa('la pregunta del plano se dibuja en la pantalla', r.haySelectorDelPlano, '');
revisa('al CORREGIR la respuesta a retromuscular, el relajante entra',
  r.conRetro_ciclo === true, 'corregir la respuesta no volvió a meter el renglón');
revisa('y es exactamente un renglón de diferencia',
  r.conRetro_total === r.sinRetro_total + 1,
  r.sinRetro_total + ' → ' + r.conRetro_total);
revisa('sin contestar el plano la receta NO se imprime',
  /plano|retromuscular/i.test(r.faltaPlano || ''), r.faltaPlano);

revisa('la hoja carga en la aplicación', r.hojaCargada, '');
revisa('el papel lleva el título de la combinada', r.papelTitulo, '');
revisa('el papel trae la sección del abdomen', r.papelAbdomen, '');
revisa('el papel trae la faja', r.papelFaja, '');
revisa('el papel trae el brasier', r.papelBrasier, '');
revisa('el papel explica el ombligo', r.papelOmbligo, '');
revisa('el papel trae la garganta cuando hubo tubo', r.papelGarganta, '');
revisa('y el papel NO habla de drenajes', r.papelSinDrenaje, '');
revisa('sin contestar el tubo la hoja no se imprime',
  (r.faltaTubo || '').length > 0, r.faltaTubo);

await nav.close();
console.log(fallas ? `\n${fallas} caso(s) mal`
  : '\nLa combinada de cuerpo existe, el relajante se pregunta en vez de suponerse, ' +
    'el anticoagulante no se pierde y la hoja dice lo del abdomen sin hablar de drenajes.');
process.exit(fallas ? 1 : 0);
