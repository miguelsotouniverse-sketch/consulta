/* ============================================================
   PRUEBA PERMANENTE — LA FIRMA VISUAL

   El médico pidió poder mandar una receta en digital, ya firmada, sin
   imprimir-firmar-escanear. Y pidió que NO siempre: que el sistema deje
   escoger documento por documento.

   Esta prueba comprueba que:
     · sin encender nada, el documento sale como siempre: línea en blanco y
       el pie dice «Firma autógrafa»  ← lo de hoy no se rompe;
     · encendida, aparece la firma dibujada ENCIMA de la línea;
     · encendida, el pie ya NO dice «Firma autógrafa», porque no lo es;
     · la decisión se guarda en `doc_estado_firma`, que ya existía en el
       esquema — no en una columna nueva;
     · si no hay firma cargada en las constantes, no pasa nada y todo sigue
       siendo manual;
     · vale igual para las recetas y para el resto de los documentos.

   Uso: node prueba_firma_visual.mjs [index.html] [recetas.json]
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
const REC  = resolve(process.argv[3] || 'recetas.json');
const esquema = JSON.parse(dondeEste('campos.json'));
const cat = JSON.parse(dondeEste('recetas.json'));
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

revisa('las constantes traen una firma cargada',
  !!constantes['medico_firma'] && /^data:image\//.test(constantes['medico_firma']),
  String(constantes['medico_firma']).slice(0, 40));

const r = await pag.evaluate(async ({ esquema, cat, constantes }) => {
  const base = function(con){
    ESQUEMA = esquema; CONSTANTES = con;
    RECETAS = cat; RECETAS_AL = Date.now();
    TIPO = DOCUMENTOS.filter(function(d){ return d.id === 'receta_post'; })[0];
    PLANTILLA = cat.plantillas.filter(function(p){ return p.id === 'deep_plane'; })[0];
    VALORES = {
      expediente_folio:'P-PRUEBA', paciente_nombres:'María Fernanda',
      paciente_apellido_paterno:'Hernández', paciente_apellido_materno:'Villaseñor',
      paciente_sexo:'Femenino', paciente_edad:'48',
      rx_plantilla:'deep_plane', rx_peni:'no', rx_sulfa:'no', rx_bichat:'no',
      rx_blefaro:'no', rx_renal:'no', rx_sintram:'',
      rx_renglones: renglonesDe(PLANTILLA, estadoReceta())
    };
    PENDIENTE_DICTADO = {}; FOLIO='P-PRUEBA'; DOC_ID='ffff'; CORREO='x@y.mx';
  };
  const imprime = function(){
    armaImpresion();
    const i = document.getElementById('impresion');
    return { texto: i.innerText,
             rubricas: i.querySelectorAll('img.rubrica').length,
             firmas: i.querySelectorAll('.firma').length };
  };

  const out = {};

  /* --- 1. apagada: como siempre --- */
  base(constantes);
  out.apagadaEstado = VALORES['doc_estado_firma'];
  const a = imprime();
  out.apagadaRubricas = a.rubricas;
  out.apagadaDiceAutografa = /Firma autógrafa/.test(a.texto);
  out.apagadaFirmas = a.firmas;

  /* --- 2. encendida --- */
  VALORES['doc_estado_firma'] = 'Firmado';
  const b = imprime();
  out.encendidaRubricas = b.rubricas;
  out.encendidaDiceAutografa = /Firma autógrafa/.test(b.texto);
  out.encendidaPie = /medio electrónico/.test(b.texto);
  out.unaRubricaPorFirma = (b.rubricas === b.firmas);

  /* --- 3. la rúbrica va ENCIMA de la línea --- */
  const f = document.querySelector('#impresion .firma');
  const hijos = [...f.children].map(function(x){ return x.className || x.tagName; });
  out.ordenDentroDeLaFirma = hijos;

  /* --- 4. sin firma en las constantes, nada cambia --- */
  const sinFirma = JSON.parse(JSON.stringify(constantes));
  delete sinFirma['medico_firma'];
  base(sinFirma);
  VALORES['doc_estado_firma'] = 'Firmado';
  const c = imprime();
  out.sinConstanteRubricas = c.rubricas;
  out.sinConstanteDiceAutografa = /Firma autógrafa/.test(c.texto);

  /* --- 5. un documento que no es receta --- */
  base(constantes);
  TIPO = DOCUMENTOS.filter(function(d){ return d.id === 'nota_evolucion'; })[0];
  PLANTILLA = null;
  VALORES['doc_estado_firma'] = 'Firmado';
  arma(); vuelca();
  const d = imprime();
  out.notaRubricas = d.rubricas;
  out.notaDiceAutografa = /Firma autógrafa/.test(d.texto);

  return out;
}, { esquema, cat, constantes });

revisa('apagada, el documento arranca sin estado de firma',
  !r.apagadaEstado, String(r.apagadaEstado));
revisa('apagada, no se estampa ninguna firma', r.apagadaRubricas === 0,
  r.apagadaRubricas + ' rúbricas');
revisa('apagada, el pie sigue diciendo «Firma autógrafa»', r.apagadaDiceAutografa,
  'cambió el pie de un documento sin firmar');
revisa('encendida, la firma se estampa en cada pliego',
  r.encendidaRubricas > 0 && r.unaRubricaPorFirma,
  r.encendidaRubricas + ' rúbricas para ' + r.apagadaFirmas + ' firmas');
revisa('encendida, el pie ya NO dice «Firma autógrafa»', !r.encendidaDiceAutografa,
  'seguía afirmando que era autógrafa');
revisa('encendida, el pie dice que se emitió por medio electrónico', r.encendidaPie,
  'falta la aclaración');
revisa('la firma va ENCIMA de la línea',
  r.ordenDentroDeLaFirma[0] === 'rubrica' && r.ordenDentroDeLaFirma[1] === 'linea',
  r.ordenDentroDeLaFirma.join(' → '));
revisa('sin firma en las constantes no se estampa nada',
  r.sinConstanteRubricas === 0, r.sinConstanteRubricas + ' rúbricas');
revisa('sin firma en las constantes el pie vuelve a «Firma autógrafa»',
  r.sinConstanteDiceAutografa, 'el pie quedó mal');
revisa('también funciona fuera de las recetas', r.notaRubricas === 1,
  r.notaRubricas + ' rúbricas en la nota de evolución');
revisa('en la nota firmada tampoco dice «Firma autógrafa»', !r.notaDiceAutografa,
  'seguía diciendo autógrafa');

await nav.close();
console.log(fallas ? `\n${fallas} caso(s) mal`
                   : '\nFirma visual: se enciende documento por documento.');
process.exit(fallas ? 1 : 0);
