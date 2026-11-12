/* ============================================================
   PRUEBA PERMANENTE — MICRO Y NANOFAT FACIAL

   Esta prueba existe por UNA cosa sobre todas las demás.

   Las cinco hojas faciales del sistema —Deep Plane, combinada, Deep Plane
   con CO₂, eCO₂ y Morpheus8— mandan todas «frío local, 15 minutos cada
   hora». La de micro/nanofat NO puede decir eso: el frío cierra los vasos
   que tienen que alimentar la grasa recién injertada. El médico lo confirmó
   el 12-nov-2026: «Nada de frío ni presión sobre lo injertado».

   El peligro no es olvidarlo hoy: es que alguien reconstruya esta hoja
   copiando de las otras faciales, como se copia todo en este repositorio, y
   el renglón del hielo entre sin que nadie lo note. Se lee perfectamente
   bien. La paciente lo obedecería.

   Uso: node prueba_nanofat.mjs
   ============================================================ */
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

function dondeEste(n){
  for (const s of [n, '../' + n, '/home/claude/' + n, '/mnt/user-data/outputs/' + n]){
    try { return readFileSync(resolve(s), 'utf8'); } catch(e){}
  }
  throw new Error('No encuentro ' + n);
}

const ind = JSON.parse(dondeEste('indicaciones.json'));
const rx  = JSON.parse(dondeEste('recetas.json'));
const H = {}; ind.hojas.forEach(h => H[h.id] = h);
const P = {}; rx.plantillas.forEach(p => P[p.id] = p);

let fallas = 0;
function revisa(nombre, bien, detalle){
  console.log((bien ? '✓ ' : '✗ ') + nombre + (bien ? '' : '   → ' + (detalle || '')));
  if (!bien) fallas++;
}

const plano = (t) => String(t || '').toLowerCase()
  .normalize('NFD').replace(/[̀-ͯ]/g, '').trim();
function sugiere(lista, proc){
  const p = plano(proc);
  return lista.filter(x => (x.coincide || []).some(c => p.indexOf(plano(c)) >= 0))
              .map(x => x.id);
}

revisa('la hoja de nanofat existe', !!H.nanofat, '');
revisa('la receta de nanofat existe', !!P.nanofat, '');
if (!H.nanofat || !P.nanofat) process.exit(1);

const hoja = JSON.stringify(H.nanofat);
const meds = P.nanofat.medicamentos.map(m => m.nombre).join(' | ');

/* ======== LO QUE ESTA PRUEBA EXISTE PARA DEFENDER ======== */
revisa('EL FRÍO: la hoja NO copió el renglón de frío local de las faciales',
  hoja.indexOf('Frío local') < 0 && hoja.indexOf('compresas frías sobre una gasa') < 0,
  'se coló el renglón de hielo cada hora');
revisa('EL FRÍO: la hoja lo prohíbe por escrito sobre lo injertado',
  /NO se ponga hielo ni compresas frías sobre la zona injertada/.test(hoja), '');
revisa('EL FRÍO: y dice que en la zona donadora sí se vale',
  /Aquí sí puede ponerse frío/.test(hoja),
  'sin el contraste, la prohibición se lee como errata');
revisa('LA PRESIÓN: prohíbe masaje y presión sobre la cara',
  /No se presione, no se masajee/.test(hoja), '');
/* y que las otras faciales SIGAN mandando frío: si un día alguien "arregla"
   esto quitándoselo a todas, también es un error. */
revisa('las otras hojas faciales conservan su frío local',
  ['deep_plane','facial_combinada','deep_plane_co2','eco2','morpheus8']
    .every(id => /Frío local/.test(JSON.stringify(H[id]))), '');

/* ======== sugerencia ======== */
revisa('«Nanofat» sugiere su hoja y sólo ésa',
  JSON.stringify(sugiere(ind.hojas, 'Nanofat')) === '["nanofat"]',
  sugiere(ind.hojas, 'Nanofat').join(', '));
revisa('«Nanofat» sugiere su receta y sólo ésa',
  JSON.stringify(sugiere(rx.plantillas, 'Nanofat')) === '["nanofat"]',
  sugiere(rx.plantillas, 'Nanofat').join(', '));

/* ======== lo que el médico definió ======== */
revisa('la sedación va fija, sin preguntar',
  !(H.nanofat.preguntas || []).length &&
  !H.nanofat.bloques.some(b => b.si) &&
  /no maneje/.test(hoja), '');
revisa('la zona donadora lleva apósito compresivo, no faja',
  /apósito compresivo/.test(hoja) && !/faja/i.test(hoja), '');
revisa('la receta lleva antibiótico, con sus dos ramas de alergia',
  /Amoxicilina/.test(meds) && /Clindamicina/.test(meds) &&
  (P.nanofat.preguntas || []).some(q => q.id === 'peni'), '');
revisa('la receta lleva analgésico, con la rama de sulfas',
  /Paracetamol/.test(meds) && /Celecoxib/.test(meds) && /Ketorolaco/.test(meds) &&
  (P.nanofat.preguntas || []).some(q => q.id === 'sulfa'), '');
revisa('la receta lleva Cicaplast Baume y protector solar',
  /Cicaplast/.test(meds) && /Protector solar/.test(meds), '');
revisa('y NO Cicalfate, que fue un lapsus corregido el 12-nov-2026',
  !/Cicalfate/.test(meds) && !/Cicalfate/.test(hoja), '');
/* El médico acortó los analgésicos a 7 días. El protector gástrico tiene que
   ir con ellos: si alguien devuelve el token {diasPPI}, la receta diría
   antiinflamatorio 7 días y protector 14, en la misma hoja. */
const an = P.nanofat.medicamentos;
revisa('los analgésicos duran 7 días, no 14',
  an.filter(m => /Paracetamol|Celecoxib/.test(m.nombre)).every(m => m.duracion === '7 días'),
  an.filter(m => /Paracetamol|Celecoxib/.test(m.nombre)).map(m => m.duracion).join(', '));
revisa('y el protector gástrico se recortó con ellos',
  an.filter(m => /Pantoprazol/.test(m.nombre)).every(m => m.duracion === '7 días'), '');
revisa('no quedó ningún {diasPPI} sin sustituir',
  JSON.stringify(an).indexOf('diasPPI') < 0, '');
revisa('las cantidades concuerdan con los 7 días',
  an.some(m => /Paracetamol/.test(m.nombre) && m.cantidad === '42 tabletas'), '');
revisa('el ketorolaco conserva su tope de 5 días',
  an.filter(m => /Ketorolaco/.test(m.nombre)).every(m => m.duracion === '5 días'), '');

/* ======== lo que no le toca ======== */
['Amlodipino','Metoprolol','Captopril','Rivaroxab','Dexametasona','Clonazepam']
  .forEach(m => revisa('la receta no lleva ' + m, meds.indexOf(m) < 0, ''));
revisa('no pregunta por el tubo: esto va con sedación',
  !(P.nanofat.preguntas || []).some(q => q.id === 'tubo') &&
  !(H.nanofat.preguntas || []).some(q => q.id === 'tubo'), '');

/* ======== lo propio del injerto ======== */
revisa('la hoja manda dormir boca arriba', /boca arriba/.test(hoja), '');
revisa('la hoja explica la reabsorción y el plazo del resultado',
  /reabsorbe/.test(hoja) && /3 y los 6 meses/.test(hoja), '');
revisa('la hoja pide peso estable', /peso estable/.test(hoja), '');
/* El renglón de cambios en la vista lo había puesto yo por la oclusión
   vascular del injerto facial; el médico lo quitó el 12-nov-2026 porque
   «alerta de más». Que no regrese solo al reconstruir. */
revisa('la hoja NO lleva el renglón de cambios en la vista',
  !/Cambios en la vista/.test(hoja) && !/perder visión/.test(hoja), '');
revisa('la receta tampoco',
  !(P.nanofat.alarma || []).some(a => /Cambios en la vista/.test(a.t)), '');
revisa('pero sí queda el signo en la piel, que cubre lo mismo y se ve al espejo',
  /se pone blanca, moteada, morada/.test(hoja), '');
revisa('la receta deja escrito en pantalla qué no trae y por qué',
  (P.nanofat.avisos || []).some(a => /no lleva antihipertensivos/.test(a.texto)), '');

/* ======== forma, como todas ======== */
revisa('la hoja cierra con constancia y firmas',
  H.nanofat.bloques[H.nanofat.bloques.length - 1].t === 'firmas', '');
revisa('la hoja está escrita de usted',
  !/\b(tienes|debes|acude|tu cara|tu piel)\b/i.test(hoja), '');
revisa('manda llamar al consultorio, no a urgencias externas',
  /teléfono de urgencias/.test(hoja) && !/911|cruz roja/i.test(hoja), '');

console.log(fallas ? `\n${fallas} caso(s) mal`
  : '\nLa zona injertada no lleva frío ni presión, y la hoja lo dice en vez de callarlo.');
process.exit(fallas ? 1 : 0);
