/* ============================================================
   PRUEBA PERMANENTE — MORPHEUS8 FACIAL

   El 6-nov-2026 el médico pidió la hoja y la receta de Morpheus8 facial, que
   no existían, y al preguntarle cerró cuatro cosas:

     · la anestesia VARÍA de una paciente a otra, de tópica sola a sedación
     · NO lleva profilaxis antiviral
     · Cicaplast, vaselina y FPS 50, SIN Clobesol
     · la serie también varía: no hay número de sesiones ni intervalo fijo

   La hoja se construye copiando de la del eCO₂, que es la pariente más
   cercana, y ahí está el riesgo que esta prueba vigila: el eCO₂ deja la piel
   EN CARNE VIVA y su hoja está escrita alrededor de eso —doce meses de
   protector solar, maquillaje hasta el día 14, «mientras la piel esté
   abierta»—. Copiar de más no se nota al leer: produce una hoja que suena
   bien y le describe a la paciente una recuperación que no es la suya.

   Uso: node prueba_morpheus8.mjs
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

revisa('la hoja de morpheus8 existe', !!H.morpheus8, '');
revisa('la receta de morpheus8 existe', !!P.morpheus8, '');
if (!H.morpheus8 || !P.morpheus8) process.exit(1);

const hoja = JSON.stringify(H.morpheus8);
const meds = P.morpheus8.medicamentos
  .map(m => m.nombre + ' ' + m.indicacion).join(' | ');

/* ---- sugerencia ---- */
revisa('«Morpheus8» sugiere su hoja y sólo ésa',
  JSON.stringify(sugiere(ind.hojas, 'Morpheus8')) === '["morpheus8"]',
  sugiere(ind.hojas, 'Morpheus8').join(', '));
revisa('«Morpheus8» sugiere su receta y sólo ésa',
  JSON.stringify(sugiere(rx.plantillas, 'Morpheus8')) === '["morpheus8"]',
  sugiere(rx.plantillas, 'Morpheus8').join(', '));
revisa('y no le roba la sugerencia al eCO₂',
  JSON.stringify(sugiere(ind.hojas, 'Láser eCO2 facial')) === '["eco2"]',
  sugiere(ind.hojas, 'Láser eCO2 facial').join(', '));

/* ---- lo que el médico decidió que NO lleva ---- */
/* Se busca el FÁRMACO, no la palabra «antiviral»: la hoja la usa a propósito
   para decir que NO lo lleva —abajo se comprueba esa frase—, y una primera
   versión de esta prueba se contradecía con ella misma. */
revisa('la hoja no receta ningún antiviral',
  !/valaciclovir|aciclovir|famciclovir/i.test(hoja) &&
  !/El antiviral empieza/.test(hoja), '');
revisa('la receta no lleva valaciclovir', !/valaciclovir/i.test(meds), '');
revisa('la hoja no menciona esteroide tópico',
  !/clobesol|clobetasol/i.test(hoja), '');
revisa('la receta no lleva Clobesol', !/clobesol|clobetasol/i.test(meds), '');

/* ---- lo que NO debe haberse copiado del eCO₂ ----
   Son plazos y frases del láser ablativo. Cada una describiría una
   recuperación distinta de la que esta paciente va a tener. */
[['durante 12 meses',            'los 12 meses de protector solar del láser'],
 ['hasta el día 14',             'el maquillaje al día 14'],
 ['en carne viva',               'la piel en carne viva'],
 ['mientras la piel esté abierta','la piel abierta'],
 ['7 a 10 días',                 'el cierre de 7 a 10 días'],
].forEach(function(par){
  revisa('no se copió ' + par[1], hoja.indexOf(par[0]) < 0, par[0]);
});

/* ---- lo propio del Morpheus8 ---- */
revisa('la hoja nombra la retícula de puntitos', /retícula/.test(hoja), '');
revisa('la hoja prohíbe el calor las primeras 48 horas',
  /Nada de calor sobre la cara las primeras 48 horas/.test(hoja), '');
revisa('la hoja advierte de la quemadura en UN punto aislado',
  /UN punto aislado/.test(hoja), '');
revisa('la hoja explica por qué no lleva antiviral ni esteroide',
  /NO lleva antiviral ni crema con esteroide/.test(hoja), '');
revisa('la hoja NO inventa un calendario de sesiones',
  !H.morpheus8.bloques.some(b => b.t === 'citas') &&
  /no son iguales para todas/.test(hoja), '');
revisa('y deja en blanco el número de sesión y la siguiente',
  /"Número de sesión","?"?/.test(hoja.replace(/\s/g,'')) ||
  JSON.stringify(H.morpheus8.bloques[1]).indexOf('Número de sesión') >= 0, '');

/* ---- la pregunta de la sedación ---- */
const q = (H.morpheus8.preguntas || []).filter(x => x.id === 'sedacion');
revisa('la hoja pregunta si llevó sedación, y es obligatoria',
  q.length === 1 && q[0].obligatoria === true && q[0].enPie === true,
  JSON.stringify(q));
const cond = H.morpheus8.bloques.filter(b => (b.si || {}).sedacion === true);
revisa('el acompañante y el no manejar van condicionados a la sedación',
  cond.length === 2, cond.length + ' bloques');
revisa('y ese bloque sí dice no manejar y no quedarse sola',
  /no maneje/.test(JSON.stringify(cond)) &&
  /no se quede sola/.test(JSON.stringify(cond)), '');
revisa('la hoja también pregunta por el tubo, como todas',
  (H.morpheus8.preguntas || []).some(x => x.id === 'tubo'), '');
revisa('la receta también pregunta por el tubo',
  (P.morpheus8.preguntas || []).some(x => x.id === 'tubo'), '');

/* ---- la receta ---- */
['Cicaplast','Vaselina','Protector solar'].forEach(function(m){
  revisa('la receta lleva ' + m, meds.indexOf(m) >= 0, '');
});
revisa('la receta lleva el spray de la garganta, condicionado',
  P.morpheus8.medicamentos.some(m => (m.si || {}).tubo === true), '');
const dexa = P.morpheus8.medicamentos.filter(m => /Dexametasona/.test(m.nombre));
revisa('la dexametasona está en la lista pero APAGADA por omisión',
  dexa.length === 1 && dexa[0].fuera === true,
  dexa.length ? String(dexa[0].fuera) : 'no está');
revisa('la receta no necesita pliego de antibiótico, controlado ni psicotrópico',
  P.morpheus8.medicamentos.every(m => m.hoja === 'general'), '');
revisa('la receta deja escrito en pantalla por qué es más corta que la del eCO₂',
  (P.morpheus8.avisos || []).some(a => /no lleva profilaxis antiviral/.test(a.texto)), '');

/* ---- forma, como todas las hojas ---- */
revisa('la hoja cierra con constancia de entrega y firmas',
  H.morpheus8.bloques[H.morpheus8.bloques.length - 1].t === 'firmas', '');
revisa('la hoja está escrita de usted, no de tú',
  !/\b(tienes|debes|acude|tu cara|tu piel)\b/i.test(hoja), '');
revisa('la hoja manda llamar al consultorio, no a urgencias externas',
  /teléfono de urgencias/.test(hoja) && !/911|cruz roja/i.test(hoja), '');

console.log(fallas ? `\n${fallas} caso(s) mal`
  : '\nMorpheus8 tiene hoja y receta propias, y no heredó la recuperación de un láser.');
process.exit(fallas ? 1 : 0);
