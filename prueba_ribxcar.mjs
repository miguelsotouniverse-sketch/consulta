/* ============================================================
   PRUEBA PERMANENTE — LA HOJA Y LA RECETA DE RIBXCAR SOLA

   El 2-nov-2026 el médico pidió «una hoja de recomendaciones postoperatorias
   de ribxcar, paciente que solo le hicieron ribxcar», y al preguntarle cerró
   cuatro cosas:

     · percutánea, sin herida que curar
     · ambulatoria, se va el mismo día y sin radiografía de control
     · «como solo es ribxcar se van desde dia 1 con el corset puesto, mismo
        esquema un broche hasta semana 8 luego estabilizar hasta mes 6»
     · «no llevan anticoagulacion, es una cirugia de 15 minutos y es
        percutanea»

   LO QUE ESTA PRUEBA DEFIENDE DE VERDAD no es que la hoja exista: es que la
   palabra «ribxcar» no vuelva a apuntar a la lipoescultura. Hasta ese día,
   `lipoescultura.coincide` y `body360.coincide` incluían `ribxcar`, así que a
   una paciente de RibXcar sola el sistema le PROPONÍA la hoja de una
   lipoescultura completa —faja tres meses, curación de heridas— y la receta
   con rivaroxabán 10 días y dos antihipertensivos, para un procedimiento
   percutáneo de quince minutos. No era un hueco: era una sugerencia activa y
   equivocada, y es el tipo de cosa que vuelve sola si alguien reconstruye el
   catálogo sin acordarse.

   Uso: node prueba_ribxcar.mjs
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

/* Misma normalización que `plano_()` en la aplicación. */
const plano = (t) => String(t || '').toLowerCase()
  .normalize('NFD').replace(/[̀-ͯ]/g, '').trim();

/* Y la misma regla de `hojaSugerida()` / `plantillaSugerida()`: se sugiere
   sólo cuando coincide EXACTAMENTE una. */
function sugiere(lista, proc){
  const p = plano(proc);
  return lista.filter(x => (x.coincide || []).some(c => p.indexOf(plano(c)) >= 0))
              .map(x => x.id);
}

revisa('la hoja de ribxcar existe', !!H.ribxcar, 'no está en el catálogo');
revisa('la receta de ribxcar existe', !!P.ribxcar, 'no está en el catálogo');
if (!H.ribxcar || !P.ribxcar){ process.exit(1); }

const hoja = JSON.stringify(H.ribxcar);
const rec  = JSON.stringify(P.ribxcar);

/* ---- lo que tiene que ser verdad de la SUGERENCIA ---- */
revisa('«RibXcar» sugiere la hoja de ribxcar y sólo ésa',
  JSON.stringify(sugiere(ind.hojas, 'RibXcar')) === '["ribxcar"]',
  sugiere(ind.hojas, 'RibXcar').join(', '));
revisa('«RibXcar» sugiere la receta de ribxcar y sólo ésa',
  JSON.stringify(sugiere(rx.plantillas, 'RibXcar')) === '["ribxcar"]',
  sugiere(rx.plantillas, 'RibXcar').join(', '));
revisa('la hoja de lipoescultura ya NO responde a «ribxcar»',
  !(H.lipoescultura.coincide || []).some(c => /ribxcar/i.test(c.replace(/\s/g,''))),
  JSON.stringify(H.lipoescultura.coincide));
revisa('la receta de Body360 ya NO responde a «ribxcar»',
  !(P.body360.coincide || []).some(c => /ribxcar/i.test(c.replace(/\s/g,''))),
  JSON.stringify(P.body360.coincide));
revisa('y una lipoescultura sigue sugiriendo lo suyo',
  JSON.stringify(sugiere(ind.hojas, 'Lipoescultura Body360 4D')) === '["lipoescultura"]' &&
  JSON.stringify(sugiere(rx.plantillas, 'Lipoescultura Body360 4D')) === '["body360"]',
  sugiere(ind.hojas, 'Lipoescultura Body360 4D').join(', '));

/* ---- percutánea: lo que NO debe aparecer ---- */
/* Se revisan los MEDICAMENTOS, no el JSON entero de la plantilla: la
   plantilla trae a propósito un aviso que NOMBRA lo que no lleva, para que el
   médico lo vea al escoger, y un primer intento de esta prueba se cayó contra
   ese aviso. Lo que no debe existir es el renglón, no la palabra. */
const nombres = P.ribxcar.medicamentos
  .map(m => m.nombre + ' ' + m.indicacion).join(' | ');
[['rivaroxab',  'anticoagulante'],
 ['amlodipino', 'antihipertensivo de base'],
 ['metoprolol', 'el segundo antihipertensivo'],
 ['captopril',  'el rescate de presión'],
 ['clonazepam', 'el rescate de ansiedad'],
].forEach(function(par){
  const re = new RegExp(par[0], 'i');
  revisa('la hoja no menciona ' + par[1], !re.test(hoja), par[0]);
  revisa('la receta no lleva ' + par[1], !re.test(nombres), par[0]);
});
revisa('y la receta deja escrito en pantalla QUÉ no lleva y por qué',
  P.ribxcar.avisos.some(a => /no lleva anticoagulación/.test(a.texto) &&
                             /antihipertensivos/.test(a.texto) &&
                             /clonazepam/.test(a.texto)), '');
revisa('la hoja no habla de retirar puntos', !/retiro de puntos|retirar los puntos/i.test(hoja), '');
revisa('la hoja no manda curar heridas', !/cure las? (heridas|incisiones)/i.test(hoja), '');
revisa('la hoja dice que no hay heridas que curar',
  /No tiene heridas que curar/.test(hoja), '');
revisa('la hoja no habla de faja ni de drenajes',
  !/faja|drenaje/i.test(hoja), '');
revisa('la receta no quedó con un pliego de psicotrópico vacío',
  !P.ribxcar.medicamentos.some(m => m.hoja === 'psicotropico'), '');
revisa('ningún aviso de la receta menciona el anticoagulante',
  !P.ribxcar.avisos.some(a => /rivaroxab|anticoagulante/i.test(a.texto)), '');
revisa('ningún signo de alarma de la receta menciona el anticoagulante',
  !P.ribxcar.alarma.some(a => /anticoagulante/i.test(a.t)), '');
revisa('la nota de profilaxis ya no habla de redosificar a las 4 o 6 horas',
  !/Repetir si/.test(P.ribxcar.profilaxisNota) &&
  /Dosis única/.test(P.ribxcar.profilaxisNota), P.ribxcar.profilaxisNota);

/* ---- lo que SÍ debe aparecer ---- */
revisa('el corset entra desde el día 1, no el día 4',
  /Día 1 a semana 8/.test(hoja) && !/día 4/i.test(hoja), '');
revisa('el ajuste es un broche por semana hasta la semana 8',
  /Un broche más cada semana/.test(hoja), '');
revisa('y de la semana 8 al mes 6 ya no se aprieta',
  /Semana 8 al mes 6/.test(hoja) &&
  /se queda en el broche al que llegó/.test(hoja), '');
revisa('la hoja dice que es percutánea y ambulatoria',
  /percutáneo/.test(hoja) && /se va a casa el mismo día/.test(hoja), '');

/* La indicación que previene la complicación más probable de una cirugía de
   costillas: si duele, uno respira corto, y respirar corto días colapsa
   pulmón. Va en mayúsculas y primera en la lista a propósito. */
const prim = H.ribxcar.bloques.filter(b => b.t === 'ul')[0];
revisa('«RESPIRE HONDO» es el PRIMER renglón de la hoja',
  /^RESPIRE HONDO/.test(prim.x[0]), prim.x[0].slice(0, 50));
revisa('y dice abrazar una almohada para toser',
  /abrace una almohada/.test(hoja), '');

/* Signos de alarma propios del tórax. Esta paciente se va a casa el mismo día
   y sin radiografía de control: la hoja es lo único que la va a hacer llamar. */
revisa('alarma: falta de aire y dolor en el pecho, de inmediato',
  /Falta de aire, dolor en el pecho/.test(hoja), '');
revisa('alarma: dolor que aumenta al respirar',
  /aumenta cada vez que respira/.test(hoja), '');
revisa('alarma: enfisema subcutáneo, en palabras que se reconozcan al tacto',
  /burbujeo o crujido al tocarse/.test(hoja), '');
revisa('alarma: el corset que ya no cierra en su broche',
  /ya no puede cerrarlo en el broche/.test(hoja), '');
revisa('y la trombosis sigue ahí, justamente porque no lleva anticoagulante',
  /una sola pantorrilla o pierna/.test(hoja), '');
revisa('la receta también lleva el dolor que aumenta al respirar',
  P.ribxcar.alarma.some(a => /aumenta cada vez que respira/.test(a.t)), '');

/* La receta conserva lo que sí le toca. */
['Paracetamol','Dexametasona','Tramadol','Pantoprazol','Amoxicilina',
 'Clindamicina 300 mg','Celecoxib','Ketorolaco','Bencidamina'].forEach(function(m){
  revisa('la receta conserva ' + m, rec.indexOf(m) >= 0, '');
});
revisa('la receta conserva su pliego de antibiótico',
  P.ribxcar.medicamentos.some(m => m.hoja === 'antibiotico'), '');
revisa('la receta pregunta por el tubo, como todas',
  (P.ribxcar.preguntas || []).some(q => q.id === 'tubo'), '');
revisa('la hoja pregunta por el tubo, como todas',
  (H.ribxcar.preguntas || []).some(q => q.id === 'tubo'), '');

/* Y lo mínimo de forma que comparte con el resto de las hojas de alta. */
revisa('la hoja trae la misma entrada que las demás',
  H.ribxcar.entrada === H.lipoescultura.entrada, '');
revisa('la hoja cierra con constancia de entrega y firma',
  H.ribxcar.bloques[H.ribxcar.bloques.length - 1].t === 'firmas', '');
revisa('las citas se coordinan con recepción, no se imprimen fechas',
  /se coordinan con recepción/.test(hoja) &&
  !H.ribxcar.bloques.some(b => b.t === 'citas'), '');
revisa('la hoja está escrita de usted, no de tú',
  !/\b(tienes|debes|puedes tu|tu cirugía|acude)\b/i.test(hoja), '');

console.log(fallas ? `\n${fallas} caso(s) mal`
  : '\nRibXcar sola tiene su hoja y su receta, y «ribxcar» ya no apunta a una lipo.');
process.exit(fallas ? 1 : 0);
