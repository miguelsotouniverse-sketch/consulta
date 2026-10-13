/* Imprime a PDF el juego de recetas de una plantilla, para verlo.
   Uso: node render_receta.mjs <index.html> <recetas.json> <id> <salida.pdf> */
import playwright from '/opt/npm-tools/node_modules/playwright/index.js';
const { chromium } = playwright;
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

/* Busca un archivo de apoyo donde esté: junto al script, en la raíz del
   repositorio, o en la carpeta de trabajo de la sesión donde se construyó.
   Así la prueba corre igual recién clonado el repositorio que aquí. */
function dondeEste(nombre){
  const sitios = [nombre, '../' + nombre, '/home/claude/' + nombre,
                  '/mnt/user-data/outputs/' + nombre];
  for (const s of sitios){ try { return readFileSync(resolve(s), 'utf8'); } catch(e){} }
  throw new Error('No encuentro ' + nombre + '. Lo busqué en: ' + sitios.join(', '));
}


const HTML = resolve(process.argv[2]);
const REC  = resolve(process.argv[3]);
const ID   = process.argv[4];
const OUT  = resolve(process.argv[5]);
const esquema = JSON.parse(dondeEste('campos.json'));
const cat = JSON.parse(readFileSync(REC,'utf8'));
let constantes = {};
try { constantes = JSON.parse(dondeEste('constantes.json')); } catch(e){}
if (constantes.campos) constantes = constantes.campos;

const nav = await chromium.launch();
const pag = await nav.newPage({ viewport:{ width:816, height:1056 } });
await pag.route('**/*', (r) =>
  r.request().url().startsWith('file://') ? r.continue() : r.abort());
await pag.goto('file://' + HTML);

const info = await pag.evaluate(({ esquema, cat, id, constantes }) => {
  ESQUEMA = esquema; RECETAS = cat; CONSTANTES = constantes;
  TIPO = DOCUMENTOS.filter(function(d){ return d.id === 'receta_post'; })[0];
  PLANTILLA = cat.plantillas.filter(function(x){ return x.id === id; })[0];
  VALORES = {
    expediente_folio:'P-PRUEBA', paciente_nombres:'María Fernanda',
    paciente_apellido_paterno:'Hernández', paciente_apellido_materno:'Villaseñor',
    paciente_sexo:'Femenino', paciente_edad:'52', proc_fecha:'2026-10-10',
    rx_plantilla:PLANTILLA.id, rx_plantilla_version:PLANTILLA.version,
    rx_bichat:'no', rx_blefaro:'si', rx_peni:'no', rx_sulfa:'no',
    rx_renal:'no', rx_isrs:'no', rx_sintram:'no'
  };
  PENDIENTE_DICTADO = {}; FOLIO='P-PRUEBA'; DOC_ID='ffff'; CORREO='consultorio@ejemplo.mx';
  VALORES['rx_renglones'] = renglonesDe(PLANTILLA, estadoReceta());
  armaImpresion();
  const i = document.getElementById('impresion');
  i.style.display = 'block';
  return { renglones: VALORES['rx_renglones'].length, texto: i.innerText.length };
}, { esquema, cat, id: ID, constantes });

await pag.pdf({ path:OUT, format:'Letter',
  margin:{ top:'8mm', right:'4mm', bottom:'12mm', left:'4mm' }, printBackground:true });
console.log('renglones: ' + info.renglones);
await nav.close();
