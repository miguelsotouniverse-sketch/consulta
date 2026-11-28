/* ============================================================
   PRUEBA PERMANENTE — EL PROTECTOR SOLAR

   El 28-nov-2026 el médico preguntó si la receta recetaba protector solar.
   Sí lo recetaba, en cinco plantillas. El problema era otro: la frase se
   escribió para el láser ablativo —«en cuanto la piel esté completamente
   cerrada»— y se copió tal cual a Morpheus8 y a nanofat, donde la piel nunca
   queda abierta. Ahí la receta mandaba esperar un cierre que no iba a ocurrir,
   mientras la hoja de la misma bolsa decía «desde mañana». Dos papeles que se
   entregan juntos, diciendo cosas distintas, sobre lo único que previene la
   mancha.

   Esta prueba defiende tres cosas:

     · QUE EL PROTECTOR NO SE CAIGA de ninguna de las cinco recetas. Es el
       tratamiento de la hiperpigmentación postinflamatoria, no un extra.
     · QUE LA HOJA Y LA RECETA DIGAN EL MISMO ARRANQUE, tratamiento por
       tratamiento. Esta es la que falló.
     · QUE LA ESPERA AL CIERRE SIGA donde la piel sí se abre, y NO esté donde
       no se abre. Las dos direcciones importan: poner protector sobre una
       herida abierta es tan malo como retrasarlo cuatro días sin motivo.

   Uso: node prueba_protector_solar.mjs
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

let fallas = 0;
function revisa(nombre, bien, detalle){
  console.log((bien ? '✓ ' : '✗ ') + nombre + (bien ? '' : '   → ' + (detalle || '')));
  if (!bien) fallas++;
}

/* La piel abierta es la del láser ablativo: ahí se quita la epidermis y hay
   que esperar a que cierre. En los otros dos la piel nunca se abre. */
const ABIERTA = ['eco2', 'deep_plane_co2', 'facial_combinada'];
const CERRADA = ['morpheus8', 'nanofat'];
const TODOS   = ABIERTA.concat(CERRADA);

const H = {}; ind.hojas.forEach(h => H[h.id] = h);
const P = {}; rx.plantillas.forEach(p => P[p.id] = p);

function textoHoja(id){ return JSON.stringify(H[id] || {}); }
function solarDe(id){
  return (P[id] ? P[id].medicamentos : []).filter(
    m => /^protector solar/i.test(m.nombre || ''));
}
/* «cierre» si el papel espera a que la piel cierre; «mañana» si arranca al
   día siguiente. Lo que se compara es esto, no las palabras. */
function arranque(t){
  if (/completamente cerrada/i.test(t)) return 'cierre';
  if (/desde mañana|día siguiente al tratamiento/i.test(t)) return 'mañana';
  return 'sin arranque';
}

TODOS.forEach(id => {
  revisa('la hoja de ' + id + ' existe', !!H[id], '');
  revisa('la receta de ' + id + ' existe', !!P[id], '');
});

/* ---- 1. el protector no se cae de ninguna receta ---- */
TODOS.forEach(id => {
  const s = solarDe(id);
  revisa('la receta de ' + id + ' RECETA protector solar', s.length === 1,
    s.length + ' renglones de protector');
  if (s.length === 1){
    revisa('y es FPS 50+ de amplio espectro',
      /50\+/.test(s[0].nombre) && /amplio espectro/i.test(s[0].nombre),
      s[0].nombre);
    revisa('y es resurtible, porque un envase no dura el año',
      /resurtible/i.test(s[0].cantidad || ''), s[0].cantidad);
  }
});

/* ---- 2. la hoja y la receta dicen el mismo arranque ---- */
TODOS.forEach(id => {
  const s = solarDe(id)[0];
  if (!s) return;
  const aH = arranque(textoHoja(id)), aR = arranque(JSON.stringify(s));
  revisa('EN ' + id.toUpperCase() + ', LA HOJA Y LA RECETA ARRANCAN IGUAL',
    aH === aR && aH !== 'sin arranque',
    'hoja dice «' + aH + '» y receta dice «' + aR + '»');
});

/* ---- 3. la espera al cierre, donde debe y sólo donde debe ---- */
ABIERTA.forEach(id => {
  revisa(id + ': la hoja espera al cierre de la piel, que ahí sí se abre',
    /completamente cerrada/i.test(textoHoja(id)), '');
  const s = solarDe(id)[0];
  revisa(id + ': la receta también espera al cierre',
    !!s && /completamente cerrada/i.test(s.indicacion || ''),
    s ? s.indicacion : '');
  revisa(id + ': y mientras tanto manda sombra y gorra, no protector',
    !!s && /sombra y gorra/i.test(s.indicacion || ''), '');
});

CERRADA.forEach(id => {
  revisa(id.toUpperCase() + ': LA HOJA NO ESPERA UN CIERRE QUE NO EXISTE',
    !/completamente cerrada/i.test(textoHoja(id)),
    'la piel no se abre en este tratamiento');
  const s = solarDe(id)[0];
  revisa(id.toUpperCase() + ': LA RECETA TAMPOCO',
    !!s && !/completamente cerrada/i.test(s.indicacion || ''),
    s ? s.indicacion : '');
  revisa(id + ': la receta arranca al día siguiente',
    !!s && /día siguiente al tratamiento/i.test(s.indicacion || ''), '');
  revisa(id + ': las 4 semanas estrictas siguen escritas en la hoja',
    /4 semanas/.test(textoHoja(id)), '');
  revisa(id + ': y también en la receta',
    !!s && /4 semanas/.test(s.indicacion || ''), '');
});

/* ---- 4. el día del tratamiento, nadie manda ponerse protector ---- */
CERRADA.forEach(id => {
  const s = solarDe(id)[0];
  revisa(id + ': el mismo día es sombra y gorra',
    /sombra y gorra/i.test(textoHoja(id)) &&
    !!s && /sombra y gorra/i.test(s.indicacion || ''), '');
});

console.log(fallas ? `\n${fallas} caso(s) mal`
  : '\nProtector solar: recetado en las cinco, con el mismo arranque en la ' +
    'hoja y en la receta, y la espera al cierre sólo donde la piel se abre.');
process.exit(fallas ? 1 : 0);
