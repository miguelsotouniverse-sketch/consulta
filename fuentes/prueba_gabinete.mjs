/* ============================================================
   PRUEBA PERMANENTE — SOLICITUD DE ESTUDIOS DE GABINETE

   El 12-nov-2026 el médico necesitaba pedirle una TAC a una paciente y no
   había dónde: «no existe ese apartado, lo insertamos porfavor».

   Lo que esta prueba defiende:

     · que el documento exista y declare sus cinco campos;
     · que esos campos existan de verdad en el esquema —si el documento
       nombra un campo que no está, la aplicación no lo dibuja y no avisa:
       el médico ve un formulario con huecos y no sabe por qué—;
     · que NO se imprima una solicitud sin estudio o sin región, que es una
       hoja firmada que no pide nada;
     · que ningún campo sea «obligatorio» en el esquema, porque entonces el
       aviso de la NOM-004 reclamaría datos de nota clínica en una solicitud;
     · y que el esquema no haya encogido, porque la aplicación lo sube sola
       a Drive y un archivo corto ahí se lleva campos del expediente.

   Uso: node prueba_gabinete.mjs [index.html]
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

let fallas = 0;
function revisa(nombre, bien, detalle){
  console.log((bien ? '✓ ' : '✗ ') + nombre + (bien ? '' : '   → ' + (detalle || '')));
  if (!bien) fallas++;
}

/* ---- 1. el esquema, sin navegador ---- */
const IDS = ['gab_estudios','gab_region','gab_contraste','gab_otros','gab_indicacion'];
const porId = {}; esquema.campos.forEach(c => porId[c.id] = c);

revisa('el grupo «Estudios de gabinete» está en el esquema',
  esquema.grupos.indexOf('Estudios de gabinete') >= 0, esquema.grupos.join(', '));
IDS.forEach(id => revisa('existe el campo ' + id, !!porId[id], 'no está'));
revisa('los estudios son casillas, con las cuatro opciones',
  porId.gab_estudios && porId.gab_estudios.control === 'casillas' &&
  porId.gab_estudios.opciones.length === 4,
  porId.gab_estudios ? porId.gab_estudios.opciones.join(', ') : '');
revisa('el contraste es una lista con «No aplica»',
  porId.gab_contraste && porId.gab_contraste.control === 'lista' &&
  porId.gab_contraste.opciones.indexOf('No aplica') >= 0, '');
revisa('la indicación clínica es un párrafo dictable',
  porId.gab_indicacion && porId.gab_indicacion.control === 'parrafo', '');
/* Si fueran obligatorios, el aviso de la NOM-004 —que habla de notas
   clínicas— reclamaría en una solicitud. El candado de este documento es
   propio y vive en index.html. */
revisa('ningún campo de gabinete es obligatorio en el esquema',
  IDS.every(id => porId[id] && !porId[id].obligatorio),
  IDS.filter(id => porId[id] && porId[id].obligatorio).join(', '));
revisa('todos los campos traen la misma forma que el resto del esquema',
  IDS.every(id => {
    const a = Object.keys(porId[id] || {}).sort().join(',');
    const b = Object.keys(esquema.campos[0]).sort().join(',');
    return a === b;
  }), '');
/* La app sube el esquema sola a Drive y se niega si encogió. */
revisa('el esquema trae más de 150 campos', esquema.campos.length > 150,
  String(esquema.campos.length));

/* ---- 2. el comportamiento, en el navegador ---- */
const nav = await chromium.launch();
const pag = await nav.newPage({ viewport: { width: 420, height: 900 } });
await pag.route('**/*', (r) =>
  r.request().url().startsWith('file://') ? r.continue() : r.abort());
await pag.goto('file://' + HTML);

const r = await pag.evaluate(async ({ esquema, constantes }) => {
  const out = {};
  const espera = (ms) => new Promise(s => setTimeout(s, ms));
  window.fetch = () => Promise.resolve({ text: () => Promise.resolve(
    JSON.stringify({ doc_id: 'DOC-G', guardado: '12/11/2026 10:00' })) });
  window.print = function(){ window.__imprimio = (window.__imprimio || 0) + 1; };

  ESQUEMA = esquema; CONSTANTES = constantes; CRED = 'x'; CORREO = 'x@y.mx';
  PACIENTE = { 'Paciente': 'María Prueba', 'Paciente_ID': 'P-001', 'Edad': '50' };
  FOLIO = 'P-001'; COMO_SE_IDENTIFICO = 'por su número';
  EXPEDIENTE = { paciente: PACIENTE, documentos: [] };
  VALORES = {}; DOC_ID = ''; PENDIENTE_DICTADO = {};

  TIPO = DOCUMENTOS.filter(d => d.id === 'estudios_gabinete')[0];
  out.existeTipo = !!TIPO;
  if (!TIPO) return out;
  out.enGrupoFirma = TIPO.grupo === 'firma';
  out.noEsHoja = !TIPO.hoja && !TIPO.receta;

  /* Que los campos que declara existan de verdad: camposDe los resuelve
     contra el esquema y descarta en silencio los que no están. */
  out.camposResueltos = camposDe(TIPO).map(c => c.id);
  out.camposDeclarados = TIPO.campos.slice();

  arma();
  await espera(60);
  out.controlesDibujados = ['gab_estudios','gab_region','gab_contraste',
    'gab_otros','gab_indicacion'].filter(id =>
      !!document.querySelector('[data-campo="' + id + '"]')).length;

  /* ---- sin estudio y sin región: NO imprime ---- */
  window.__imprimio = 0;
  document.getElementById('bImprimir').click();
  await espera(350);
  out.imprimioVacio = window.__imprimio;
  out.avisoVacio = document.getElementById('avisoPrefill').innerText.slice(0, 120);
  out.claseVacio = document.getElementById('avisoPrefill').className;

  /* ---- con estudio pero sin región: tampoco ---- */
  VALORES['gab_estudios'] = 'Tomografía (TAC)';
  window.__imprimio = 0;
  document.getElementById('bImprimir').click();
  await espera(350);
  out.imprimioSinRegion = window.__imprimio;
  out.avisoSinRegion = document.getElementById('avisoPrefill').innerText.slice(0, 120);

  /* ---- completa: sí imprime, y el papel dice lo que debe ---- */
  VALORES['gab_region'] = 'senos paranasales';
  VALORES['gab_contraste'] = 'Con contraste';
  VALORES['gab_indicacion'] = 'Descartar sinusitis previa a rinoplastia.';
  armaImpresion();
  const papel = document.getElementById('impresion').innerText;
  out.papelEstudio   = /Tomografía \(TAC\)/.test(papel);
  out.papelRegion    = /senos paranasales/.test(papel);
  out.papelContraste = /Con contraste/.test(papel);
  out.papelIndicacion= /Descartar sinusitis/.test(papel);
  out.papelPreambulo = /solicito a quien corresponda/.test(papel);
  out.papelPaciente  = /María Prueba/.test(papel);
  out.papelSinCasillas = !/☐|\[ \]/.test(papel);
  out.papelTitulo = /SOLICITUD DE ESTUDIOS DE GABINETE/.test(papel);

  window.__imprimio = 0;
  document.getElementById('bImprimir').click();
  await espera(600);
  out.imprimioCompleta = window.__imprimio;

  return out;
}, { esquema, constantes });

revisa('el tipo de documento existe en la aplicación', r.existeTipo, '');
revisa('vive en el grupo de documentos que se firman', r.enGrupoFirma, '');
revisa('no se confunde con una hoja ni con una receta', r.noEsHoja, '');
revisa('los cinco campos que declara existen en el esquema',
  (r.camposResueltos || []).length === (r.camposDeclarados || []).length,
  'declara ' + (r.camposDeclarados || []).length + ', resuelve ' +
  (r.camposResueltos || []).length);
revisa('y los cinco se dibujan en el formulario',
  r.controlesDibujados === 5, r.controlesDibujados + ' de 5');

revisa('sin estudio y sin región NO imprime', r.imprimioVacio === 0,
  'imprimió ' + r.imprimioVacio);
revisa('y dice qué falta, arriba y en rojo',
  /No imprimí la solicitud/.test(r.avisoVacio || '') && /malo/.test(r.claseVacio || ''),
  (r.claseVacio || '') + ' · ' + (r.avisoVacio || ''));
revisa('con estudio pero sin región tampoco imprime',
  r.imprimioSinRegion === 0, 'imprimió ' + r.imprimioSinRegion);
revisa('y ahí ya sólo reclama la región',
  /de qué región/.test(r.avisoSinRegion || '') &&
  !/qué estudio pide/.test(r.avisoSinRegion || ''), r.avisoSinRegion);

revisa('completa, sí imprime', r.imprimioCompleta === 1, '');
revisa('el papel lleva el título', r.papelTitulo, '');
revisa('el papel lleva el nombre de la paciente', r.papelPaciente, '');
revisa('el papel va dirigido a quien corresponda', r.papelPreambulo, '');
revisa('el papel dice el estudio escogido', r.papelEstudio, '');
revisa('el papel dice la región', r.papelRegion, '');
revisa('el papel dice el contraste', r.papelContraste, '');
revisa('el papel lleva la indicación clínica para el radiólogo', r.papelIndicacion, '');
/* La regla que el médico fijó para la hoja de laboratorios: una casilla
   impresa en blanco no se puede marcar en un PDF que va por WhatsApp. */
revisa('y NO imprime casillas vacías: los estudios salen como texto',
  r.papelSinCasillas, '');

await nav.close();
console.log(fallas ? `\n${fallas} caso(s) mal`
  : '\nLa solicitud de gabinete existe, no sale vacía, y lo que se marca en la app sale como texto en el papel.');
process.exit(fallas ? 1 : 0);
