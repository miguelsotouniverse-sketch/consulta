/* ============================================================
   PRUEBA PERMANENTE — ENDOLIFTING
   dos hojas (facial y corporal) y una receta

   El 26-nov-2026 el médico pidió la hoja de endolifting y no había nada en
   el sistema: ni hoja, ni receta, ni una mención en el esquema, aunque
   endolifting lleva años en su lista de precios.

   Lo que esta prueba defiende, en orden de gravedad:

     · QUE NO SE CRUCEN LAS DOS PRENDAS. La facial es banda y se usa SÓLO EN
       CASA dos semanas; la corporal es faja y va DÍA Y NOCHE dos semanas.
       Son dos hojas casi idénticas: entregar la equivocada manda una prenda
       distinta durante catorce días, y es el error más fácil de cometer.
     · QUE LA RECETA NO ENGORDE SOLA. Él dijo «sólo antibiótico y
       paracetamol». La plantilla se copió de nanofat, que además trae
       celecoxib y pantoprazol: si alguien la reconstruye copiando sin leer,
       esos dos se cuelan.
     · QUE LA HOJA NO PROMETA LO QUE LA RECETA NO TRAE. La de nanofat manda
       Cicaplast y protector solar porque vienen en su receta; la de
       endolifting no puede heredar esos renglones.
     · QUE SOBREVIVA EL SIGNO DEL NERVIO. En la hoja facial hay un renglón
       que pide avisar ante asimetría al sonreír o al cerrar el ojo. Es el
       único signo que no es de infección y el que no se puede perder.
     · QUE EL FRÍO SIGA SIN APARECER. Él no lo ha definido para endolifting y
       sus dos hojas vecinas se contradicen. Mientras no lo decida, ninguna
       de las dos puede permitirlo ni prohibirlo por su cuenta.

   Uso: node prueba_endolift.mjs [index.html]
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

/* ============ 1. LA RECETA ============ */
const P = {}; rec.plantillas.forEach(p => P[p.id] = p);
const R = P['endolift'];
revisa('la plantilla de endolifting existe', !!R, '');

if (R){
  const nombres = R.medicamentos.map(m => m.nombre).join(' | ');
  revisa('lleva antibiótico con su rama de alergia a penicilina',
    /Amoxicilina/.test(nombres) && /Clindamicina/.test(nombres), nombres);
  revisa('lleva paracetamol', /Paracetamol/.test(nombres), '');
  revisa('son exactamente tres renglones, como él pidió',
    R.medicamentos.length === 3, R.medicamentos.length + ' renglones');

  /* «Sólo antibiótico y paracetamol» — estos cinco son los que se colarían
     si alguien copiara de nanofat o de body360 sin leer. */
  ['Celecoxib','Ketorolaco','Pantoprazol','Tramadol','Bencidamina',
   'Dexametasona','Cicaplast'].forEach(x =>
    revisa('la receta NO lleva ' + x, !new RegExp(x,'i').test(nombres), ''));

  revisa('pregunta la alergia a penicilina',
    R.preguntas.some(q => q.id === 'peni'), '');
  /* Sin AINE no hay nada que decidir con sulfas ni con la función renal: una
     pregunta obligatoria sin consecuencia se contesta sin leer. */
  revisa('y NO pregunta sulfas ni función renal, que aquí no deciden nada',
    !R.preguntas.some(q => ['sulfa','renal','sintram','isrs'].includes(q.id)),
    R.preguntas.map(q => q.id).join(', '));

  const ids = new Set(R.preguntas.map(q => q.id).concat(['c24','menor']));
  revisa('ningún renglón cuelga de una pregunta que nadie hace',
    R.medicamentos.every(m => Object.keys(m.si || {}).every(k => ids.has(k))), '');

  /* La paciente no puede quedarse sin antibiótico conteste lo que conteste. */
  ['no','leve','grave'].forEach(v => {
    const cubre = R.medicamentos.some(m => m.hoja === 'antibiotico' &&
      ((m.si || {}).peni || []).includes(v));
    revisa('con alergia a penicilina «' + v + '» sí queda antibiótico', cubre, '');
  });

  const al = R.alarma.map(a => a.t).join(' ');
  revisa('los signos de alarma cubren la quemadura del punto de entrada',
    /ampolla|quemadura/.test(al), '');
  revisa('y el nervio', /levantar la ceja/.test(al), '');
  revisa('ninguno se repite',
    new Set(R.alarma.map(a => a.t)).size === R.alarma.length, '');
}

/* ============ 2. LAS DOS HOJAS ============ */
const H = {}; ind.hojas.forEach(h => H[h.id] = h);
const F = H['endolift_facial'];
const C = H['endolift_corporal'];
revisa('existe la hoja de endolifting facial', !!F, '');
revisa('existe la hoja de endolifting corporal', !!C, '');

if (F && C){
  const pf = JSON.stringify(F.bloques);
  const pc = JSON.stringify(C.bloques);

  /* ---- LAS PRENDAS, que es lo que no se puede cruzar ---- */
  revisa('la facial manda BANDA y no faja',
    /banda/i.test(pf) && !/faja/i.test(pf), '');
  revisa('la corporal manda FAJA y no banda',
    /faja/i.test(pc) && !/banda/i.test(pc), '');
  revisa('la banda facial es sólo en casa, 2 semanas',
    /ÚNICAMENTE MIENTRAS ESTÁ EN CASA/.test(pf) && /Semanas 1–2/.test(pf), '');
  revisa('la faja corporal es día y noche, 2 semanas',
    /DÍA Y NOCHE/.test(pc) && /Semanas 1–2/.test(pc), '');
  revisa('las dos dicen cuándo se deja de usar',
    /A partir de la semana 3/.test(pf) && /A partir de la semana 3/.test(pc), '');

  /* ---- lo que la receta no trae, la hoja no lo manda ---- */
  [['facial',pf],['corporal',pc]].forEach(([n,p]) => {
    ['Cicaplast','vaselina','Clobesol','celecoxib','antiviral','bencidamina']
      .forEach(x => revisa('la hoja ' + n + ' no menciona ' + x,
        !new RegExp(x,'i').test(p), ''));
  });

  /* ---- el nervio: sólo en la facial ---- */
  revisa('la facial pide avisar ante asimetría al sonreír o cerrar el ojo',
    /levantar la ceja/.test(pf), 'es el signo que no se puede perder');
  revisa('y pide avisar aunque sea leve', /aunque sea\s*leve/.test(pf), '');
  revisa('la corporal NO trae ese renglón, que ahí no aplica',
    !/levantar la ceja/.test(pc), '');
  revisa('ni el de maquillaje', !/Maquillaje/.test(pc), '');

  /* ---- el frío sigue sin decidirse ---- */
  revisa('ninguna habla de hielo ni de frío local',
    !/hielo|frío local/i.test(pf) && !/hielo|frío local/i.test(pc),
    'él todavía no lo ha definido para endolifting');

  /* ---- lo que las dos tienen que decir ---- */
  [['facial',pf],['corporal',pc]].forEach(([n,p]) => {
    ['sedación','micropunciones','punto de entrada','progresivo','antibiótico',
     'no maneje'].forEach(x =>
      revisa('la hoja ' + n + ' dice «' + x + '»',
        new RegExp(x,'i').test(p), ''));
    revisa('la hoja ' + n + ' no imprime HTML',
      !/<b>|<\/b>|<i>|<br|<p>/.test(p), '');
    const dup = ind.hojas.find(h => h.id === 'endolift_' + n)
      .bloques.filter(b => b.t === 'ul' && new Set(b.x).size !== b.x.length);
    revisa('la hoja ' + n + ' no repite renglones', dup.length === 0, '');
  });

  /* Concordancia: ya salió impreso «la cara y el cuello limpia y seca». */
  revisa('la facial no tiene el error de concordancia del cuello',
    !/el cuello limpia|el cuello seca/.test(pf), '');

  /* ---- ninguna se propone sola ---- */
  revisa('ninguna de las dos se propone por una palabra del procedimiento',
    (F.coincide || []).length === 0 && (C.coincide || []).length === 0, '');

  /* ---- ninguna declara preguntas, así que nada puede colgar ---- */
  revisa('ningún bloque cuelga de una pregunta que no se hace',
    F.bloques.every(b => !b.si) && C.bloques.every(b => !b.si), '');

  /* ---- siguen siendo la misma hoja en lo que comparten ---- */
  ['Hoy, porque llevó sedación','4. Calendario de actividades',
   '6. Signos de alarma: llame al teléfono de urgencias',
   '7. Citas y constancia de entrega'].forEach(s =>
    revisa('«' + s + '» está en las dos',
      pf.includes(s) && pc.includes(s), ''));
}

/* ============ 3. EN EL NAVEGADOR ============ */
const nav = await chromium.launch();
const pag = await nav.newPage({ viewport: { width: 816, height: 1056 } });
await pag.route('**/*', (r) =>
  r.request().url().startsWith('file://') ? r.continue() : r.abort());
await pag.goto('file://' + HTML);

const r = await pag.evaluate(async ({ esquema, ind, rec, constantes }) => {
  const out = {};
  const espera = (ms) => new Promise(s => setTimeout(s, ms));
  ESQUEMA = esquema; CONSTANTES = constantes;
  INDICACIONES = ind; INDICACIONES_AL = Date.now();
  RECETAS = rec; RECETAS_AL = Date.now();
  FOLIO = 'P-PRUEBA'; DOC_ID = 'ffff'; CORREO = 'x@y.mx'; PENDIENTE_DICTADO = {};

  /* --- las dos hojas --- */
  TIPO = DOCUMENTOS.filter(d => d.id === 'indicaciones_alta')[0];
  out.papel = {};
  ['endolift_facial','endolift_corporal'].forEach(id => {
    VALORES = { expediente_folio:'P-PRUEBA', paciente_nombres:'María',
                paciente_apellido_paterno:'Prueba', paciente_sexo:'Femenino' };
    HOJA = INDICACIONES.hojas.filter(h => h.id === id)[0];
    armaImpresion();
    out.papel[id] = document.getElementById('impresion').innerText;
  });

  /* --- la receta, sin alergia y con alergia grave --- */
  TIPO = DOCUMENTOS.filter(d => d.id === 'receta_post')[0];
  VALORES = { expediente_folio:'P-PRUEBA', paciente_nombres:'María',
              paciente_apellido_paterno:'Prueba', paciente_sexo:'Femenino',
              paciente_edad:'44', rx_plantilla:'endolift', rx_peni:'no' };
  armaReceta();
  await espera(150);
  out.sinAlergia = (VALORES['rx_renglones']||[]).filter(x=>!x.fuera)
    .map(x=>x.nombre);

  const sel = document.querySelector('[data-campo="rx_peni"]');
  out.haySelector = !!sel;
  sel.value = 'grave';
  sel.dispatchEvent(new Event('change', { bubbles:true }));
  await espera(250);
  out.conAlergia = (VALORES['rx_renglones']||[]).filter(x=>!x.fuera)
    .map(x=>x.nombre);
  return out;
}, { esquema, ind, rec, constantes });

const pF = r.papel['endolift_facial'] || '';
const pC = r.papel['endolift_corporal'] || '';
revisa('la hoja facial se imprime', /ENDOLIFTING FACIAL/i.test(pF), '');
revisa('la hoja corporal se imprime', /ENDOLIFTING\s+CORPORAL/i.test(pC), '');
revisa('en el papel facial sale la banda y no la faja',
  /banda compresiva/i.test(pF) && !/faja/i.test(pF), '');
revisa('en el papel corporal sale la faja y no la banda',
  /LA FAJA/i.test(pC) && !/banda/i.test(pC), '');
revisa('el papel facial trae el signo del nervio',
  /levantar la ceja/.test(pF), '');
revisa('el papel explica que el resultado es progresivo',
  /progresivo/.test(pF) && /progresivo/.test(pC), '');

/* Tres renglones en la plantilla, dos en el papel: las dos ramas del
   antibiótico son excluyentes y sólo sale la que corresponde a la respuesta.
   Esta prueba esperaba tres y se cayó; lo que estaba mal era la prueba. */
revisa('en el papel salen dos renglones: un antibiótico y el paracetamol',
  (r.sinAlergia||[]).length === 2, (r.sinAlergia||[]).join(' · '));
revisa('sin alergia sale amoxicilina y no clindamicina',
  (r.sinAlergia||[]).some(n=>/Amoxicilina/.test(n)) &&
  !(r.sinAlergia||[]).some(n=>/Clindamicina/.test(n)),
  (r.sinAlergia||[]).join(' · '));
revisa('al cambiar a alergia grave, cambia el antibiótico',
  (r.conAlergia||[]).some(n=>/Clindamicina/.test(n)) &&
  !(r.conAlergia||[]).some(n=>/Amoxicilina/.test(n)),
  (r.conAlergia||[]).join(' · '));
revisa('y el paracetamol se queda en los dos casos',
  (r.sinAlergia||[]).some(n=>/Paracetamol/.test(n)) &&
  (r.conAlergia||[]).some(n=>/Paracetamol/.test(n)), '');

await nav.close();
console.log(fallas ? `\n${fallas} caso(s) mal`
  : '\nEndolifting existe: dos hojas que no se cruzan las prendas, una receta ' +
    'de tres renglones, y el signo del nervio donde tiene que estar.');
process.exit(fallas ? 1 : 0);
