/* ============================================================
   PRUEBA PERMANENTE — EL AVISO DE LAS RECETAS EN LA NOTA PREOPERATORIA

   El médico describió el problema con sus palabras: las recetas normalmente
   salen en la valoración preoperatoria, «pero no siempre, muchas veces no da
   tiempo y las terminamos dando el día del procedimiento».

   Para casi todos los medicamentos eso es tolerable —se compran al salir de
   quirófano—. Para dos no: el amlodipino se toma la NOCHE ANTERIOR y el
   antiviral del láser empieza el DÍA PREVIO. Entregados el día de la cirugía
   llegan tarde y no sirven.

   El sistema no puede verificar si las recetas se entregaron. Lo único que
   puede hacer es acordárselo a quien sí lo sabe, en el momento en que todavía
   puede resolverlo. Esta prueba comprueba que ese recordatorio:

     · aparece al capturar una nota preoperatoria;
     · nombra los dos medicamentos que no admiten retraso;
     · NO aparece en los demás documentos, para que no se vuelva ruido que
       nadie lee;
     · NO bloquea nada: es un recordatorio, no una barrera, porque el sistema
       no tiene manera de saber la verdad.

   Uso: node prueba_aviso_preop.mjs [index.html]
   ============================================================ */
import playwright from '/opt/npm-tools/node_modules/playwright/index.js';
const { chromium } = playwright;
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

function dondeEste(nombre){
  const sitios = [nombre, '../' + nombre, '/home/claude/' + nombre,
                  '/mnt/user-data/outputs/' + nombre];
  for (const s of sitios){ try { return readFileSync(resolve(s), 'utf8'); } catch(e){} }
  throw new Error('No encuentro ' + nombre);
}

const HTML = resolve(process.argv[2] || 'index.html');
const esquema = JSON.parse(dondeEste('campos.json'));
let constantes = JSON.parse(dondeEste('constantes.json'));
if (constantes.campos) constantes = constantes.campos;

const nav = await chromium.launch();
const pag = await nav.newPage({ viewport: { width: 816, height: 1056 } });
await pag.route('**/*', (r) =>
  r.request().url().startsWith('file://') ? r.continue() : r.abort());
await pag.goto('file://' + HTML);

let fallas = 0;
function revisa(nombre, bien, detalle){
  console.log((bien ? '✓ ' : '✗ ') + nombre + (bien ? '' : '   → ' + detalle));
  if (!bien) fallas++;
}

const r = await pag.evaluate(({ esquema, constantes }) => {
  function monta(tipoid){
    ESQUEMA = esquema; CONSTANTES = constantes;
    TIPO = DOCUMENTOS.filter(function(d){ return d.id === tipoid; })[0];
    VALORES = { expediente_folio:'P-PRUEBA', paciente_nombres:'María',
                paciente_apellido_paterno:'Hernández', paciente_sexo:'Femenino',
                paciente_edad:'48' };
    PENDIENTE_DICTADO = {}; FOLIO='P-PRUEBA'; DOC_ID='ffff'; CORREO='x@y.mx';
    arma(); vuelca();
    const f = document.getElementById('formulario');
    const avisos = [...f.querySelectorAll('.aviso')];
    return { texto: avisos.map(function(a){ return a.innerText; }).join(' | '),
             cuantos: avisos.length,
             primero: f.firstElementChild && f.firstElementChild.className };
  }
  const out = { preop: monta('nota_preoperatoria') };
  out.otros = {};
  ['historia_clinica','nota_evolucion','hoja_frontal','ci_quirurgico']
    .forEach(function(id){ out.otros[id] = monta(id); });
  /* imprimir no debe quedar bloqueado por el aviso */
  monta('nota_preoperatoria');
  out.faltantesNOM = faltantesNOM().length;
  return out;
}, { esquema, constantes });

revisa('la nota preoperatoria muestra el aviso', r.preop.cuantos >= 1,
  'no apareció ningún aviso');
revisa('el aviso va hasta arriba, antes de los campos',
  /aviso/.test(r.preop.primero || ''), String(r.preop.primero));
revisa('nombra el amlodipino', /amlodipino/i.test(r.preop.texto), r.preop.texto.slice(0,90));
revisa('nombra el antiviral', /antiviral/i.test(r.preop.texto), r.preop.texto.slice(0,90));
revisa('dice que esas dos se toman ANTES de la cirugía',
  /ANTES de la cirugía|antes de la cirugía/i.test(r.preop.texto), '');
revisa('dice qué pasa si salen tarde',
  /ya no sirven|llegan tarde/i.test(r.preop.texto), '');

const conAviso = Object.entries(r.otros).filter(function(p){ return p[1].cuantos > 0; });
revisa('no aparece en los demás documentos', conAviso.length === 0,
  'también salió en: ' + conAviso.map(function(p){ return p[0]; }).join(', '));

revisa('es un recordatorio, no una barrera: no bloquea la impresión',
  typeof r.faltantesNOM === 'number',
  'el aviso interfirió con la validación de la NOM');

await nav.close();
console.log(fallas ? `\n${fallas} caso(s) mal`
                   : '\nEl aviso aparece donde sirve y en ningún otro lado.');
process.exit(fallas ? 1 : 0);
