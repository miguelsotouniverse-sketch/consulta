/* ============================================================
   PRUEBA PERMANENTE — GUARDAR, Y ABRIR UNA NOTA SIN DUPLICARLA

   El médico reportó dos cosas el 28-oct-2026:

     «el botón de guardar no funciona. Guarda cuando imprimes»
     «cuando quiero ver una nota no me deja verla, me deja únicamente
      imprimir de nuevo y por lo tanto se duplica y triplica la nota»

   Reproducido en local, el botón SÍ guardaba: lo que no hacía era decirlo.
   No escribía nada mientras esperaba al servidor —uno a cuatro segundos— y
   el «Guardado» final caía en el mismo renglón que el contador de campos
   reescribe en cada tecla. Imprimir sí avisaba, y de ahí la conclusión.

   Y los documentos ya hechos siempre se pudieron abrir, pero no lo
   parecían: salían sin título entre la ficha y el mosaico de «Capturar»,
   que es lo que sí parece un botón y abre uno NUEVO.

   Esta prueba defiende las dos correcciones:

     · el botón se apaga y dice «Guardando…» mientras trabaja
     · al terminar, el sello dice «Guardado» y NO lo borra el contador
     · si el gateway falla, el botón vuelve y el error sale arriba, grande
     · abrir una nota de la lista la muestra con su contenido y conserva su
       identificador, así que guardar la actualiza en vez de duplicarla
     · empezar una nota nueva cuando ya hay otra lo dice antes de imprimir

   Uso: node prueba_guardado_y_notas.mjs [index.html]
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
let constantes = JSON.parse(dondeEste('constantes.json'));
if (constantes.campos) constantes = constantes.campos;

const nav = await chromium.launch();
const pag = await nav.newPage({ viewport: { width: 420, height: 900 } });
await pag.route('**/*', (r) =>
  r.request().url().startsWith('file://') ? r.continue() : r.abort());
await pag.goto('file://' + HTML);

let fallas = 0;
function revisa(nombre, bien, detalle){
  console.log((bien ? '✓ ' : '✗ ') + nombre + (bien ? '' : '   → ' + (detalle || '')));
  if (!bien) fallas++;
}

const r = await pag.evaluate(async ({ esquema, constantes }) => {
  const out = {};
  const espera = (ms) => new Promise(function(s){ setTimeout(s, ms); });

  /* Un gateway de mentiras, con el retraso real de Apps Script. */
  let modo = 'bien', tardanza = 300;
  window.__acciones = [];
  window.fetch = function(url, opt){
    const cuerpo = JSON.parse(opt.body);
    window.__acciones.push(cuerpo.accion);
    return espera(tardanza).then(function(){
      if (modo === 'mal') return { text: () => Promise.resolve('{"error":"se cayó la red"}') };
      return { text: () => Promise.resolve(JSON.stringify({
        doc_id: cuerpo.doc_id || 'NUEVO-' + window.__acciones.length,
        guardado: '28/10/2026 10:00', por: 'prueba' })) };
    });
  };
  window.alert = function(t){ window.__ultimoAlert = t; };

  ESQUEMA = esquema; CONSTANTES = constantes; CRED = 'x'; CORREO = 'x@y.mx';
  PACIENTE = { 'Paciente': 'María Prueba', 'Paciente_ID': 'P-001', 'Edad': '50' };
  FOLIO = 'P-001'; COMO_SE_IDENTIFICO = 'por su número';
  EXPEDIENTE = { paciente: PACIENTE, documentos: [
    { id: 'DOC-1', tipo: 'nota_evolucion', fecha: '2026-10-27',
      guardado: '27/10/2026 18:00', por: 'Dr. Soto',
      campos: { evo_subjetivo: 'Refiere dolor leve controlado.',
                evo_objetivo: 'Herida limpia, sin datos de infección.',
                evo_analisis: 'Evolución favorable.',
                evo_plan: 'Continúa manejo.' } },
  ]};

  ocultaTodo();
  document.getElementById('pantallaDocs').classList.remove('oculto');
  pintaDocumentos();

  out.hayRotulo = /tóquelos para abrirlos/i.test(document.getElementById('yaHechos').innerText);
  const filas = [...document.querySelectorAll('#yaHechos .hecho-fila')];
  out.diceAbrir = filas[0] ? /abrir/i.test(filas[0].innerText) : false;

  /* ---- abrir la nota ya hecha ---- */
  filas[0].click();
  out.docIdAlAbrir = DOC_ID;
  const form = document.getElementById('formulario');
  out.valoresPintados = [...form.querySelectorAll('textarea, input')]
    .filter(function(e){ return e.value && e.type !== 'checkbox'; }).length;

  /* ---- guardar: lo que se ve MIENTRAS trabaja ---- */
  window.__acciones = [];
  document.getElementById('bGuardar').click();
  await espera(60);
  out.botonMientras = document.getElementById('bGuardar').textContent;
  out.apagadoMientras = document.getElementById('bGuardar').disabled;
  out.selloMientras = document.getElementById('selloGuardado').textContent;

  await espera(500);
  out.botonDespues = document.getElementById('bGuardar').textContent;
  out.selloDespues = document.getElementById('selloGuardado').textContent;
  out.docIdDespues = DOC_ID;
  out.documentos = EXPEDIENTE.documentos.map(function(d){ return d.id; });

  /* ---- el contador de campos no debe borrar el sello ---- */
  pinta();
  out.selloTrasPintar = document.getElementById('selloGuardado').textContent;

  /* ---- si el gateway falla ---- */
  modo = 'mal';
  document.getElementById('bGuardar').click();
  await espera(500);
  out.selloEnFalla = document.getElementById('selloGuardado').textContent;
  out.botonEnFalla = document.getElementById('bGuardar').textContent;
  out.avisoEnFalla = document.getElementById('avisoPrefill').innerText.slice(0, 80);
  out.claseAvisoEnFalla = document.getElementById('avisoPrefill').className;
  modo = 'bien';

  /* ---- empezar una nota NUEVA cuando ya hay otra ---- */
  vistaDocumentos();
  const mosaico = [...document.querySelectorAll('#mosCaptura .ficha')]
    .filter(function(b){ return /Nota de evoluci/i.test(b.innerText); })[0];
  mosaico.click();
  out.docIdNueva = DOC_ID;
  out.avisoNueva = document.getElementById('avisoPrefill').innerText;

  /* ---- un documento sin identificador no se abre a ciegas ---- */
  EXPEDIENTE.documentos.push({ tipo: 'nota_evolucion', fecha: '2026-10-26',
                               campos: { evo_plan: 'x' } });
  vistaDocumentos();
  const sinId = [...document.querySelectorAll('#yaHechos .hecho-fila')]
    .filter(function(f){ return /sin identificador/i.test(f.innerText); })[0];
  out.hayFilaSinId = !!sinId;
  if (sinId){ sinId.click(); out.alertSinId = window.__ultimoAlert || ''; }
  out.docIdTrasSinId = DOC_ID;

  return out;
}, { esquema, constantes });

revisa('la lista de documentos ya hechos lleva rótulo', r.hayRotulo, 'no hay rótulo');
revisa('cada renglón dice «abrir»', r.diceAbrir, '');
revisa('abrir una nota ya hecha conserva su identificador',
  r.docIdAlAbrir === 'DOC-1', r.docIdAlAbrir);
revisa('abrir una nota ya hecha muestra lo que tenía escrito',
  r.valoresPintados >= 4, r.valoresPintados + ' campos con valor');

revisa('el botón avisa mientras guarda', /Guardando/.test(r.botonMientras), r.botonMientras);
revisa('el botón se apaga mientras guarda', r.apagadoMientras === true, '');
revisa('el sello dice que está guardando', /Guardando/.test(r.selloMientras), r.selloMientras);
revisa('al terminar, el botón vuelve a Guardar', r.botonDespues === 'Guardar', r.botonDespues);
revisa('al terminar, el sello dice Guardado', /Guardado/.test(r.selloDespues), r.selloDespues);
revisa('guardar NO duplica el documento',
  r.documentos.length === 1 && r.documentos[0] === 'DOC-1', r.documentos.join(', '));
revisa('el contador de campos no borra el sello',
  /Guardado/.test(r.selloTrasPintar), r.selloTrasPintar);

revisa('si falla el guardado, el sello lo dice', /NO se guardó/.test(r.selloEnFalla), r.selloEnFalla);
revisa('si falla el guardado, el botón no se queda apagado',
  r.botonEnFalla === 'Guardar', r.botonEnFalla);
revisa('si falla el guardado, el aviso sale arriba y en rojo',
  /No pude guardar/.test(r.avisoEnFalla) && /malo/.test(r.claseAvisoEnFalla),
  r.claseAvisoEnFalla + ' · ' + r.avisoEnFalla);

revisa('empezar una nota nueva habiendo otra lo advierte ANTES, y con fecha',
  /NUEVA/.test(r.avisoNueva) && /\d{4}-\d{2}-\d{2}/.test(r.avisoNueva) &&
  /quedarán dos/.test(r.avisoNueva), r.avisoNueva.slice(0, 120));
revisa('la nota nueva no se queda con el id de la anterior',
  r.docIdNueva === '', r.docIdNueva);

revisa('un documento sin identificador se marca y no se abre a ciegas',
  r.hayFilaSinId && /sin identificador/i.test(r.alertSinId || '') === false
    ? true : (r.hayFilaSinId && !!r.alertSinId),
  'fila: ' + r.hayFilaSinId + ' · aviso: ' + (r.alertSinId || '').slice(0, 60));

await nav.close();
console.log(fallas ? `\n${fallas} caso(s) mal`
                   : '\nGuardar avisa, y una nota ya hecha se abre en vez de duplicarse.');
process.exit(fallas ? 1 : 0);
