/* Imprime a PDF un documento guardado de verdad, para verlo con los ojos.
   Uso: node render_impresion.mjs <index.html> <expediente.json> <tipo> <salida.pdf> */
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


const HTML   = resolve(process.argv[2]);
const EXP    = resolve(process.argv[3]);
const TIPOID = process.argv[4];
const SALIDA = resolve(process.argv[5]);
const CAMPOS = null;

const esquema  = JSON.parse(dondeEste('campos.json'));
const expe     = JSON.parse(readFileSync(EXP, 'utf8'));
const doc      = expe.documentos.find((d) => d.tipo === TIPOID);
if (!doc) { console.error('ese expediente no tiene ' + TIPOID); process.exit(1); }
let constantes = {};
try { constantes = JSON.parse(dondeEste('constantes.json')); } catch (e) {}
if (constantes.campos) constantes = constantes.campos;

const navegador = await chromium.launch();
const pagina = await navegador.newPage({ viewport: { width: 816, height: 1056 } });
await pagina.route('**/*', (r) =>
  r.request().url().startsWith('file://') ? r.continue() : r.abort());
await pagina.goto('file://' + HTML);

const info = await pagina.evaluate(({ esquema, campos, constantes, tipo, folio }) => {
  ESQUEMA = esquema;
  TIPO = DOCUMENTOS.filter(function (d) { return d.id === tipo; })[0];
  CONSTANTES = constantes;
  VALORES = campos;
  PENDIENTE_DICTADO = {};
  FOLIO = folio; DOC_ID = 'ffff'; CORREO = 'consultorio@ejemplo.mx';
  armaImpresion();
  var i = document.getElementById('impresion');
  i.style.display = 'block';
  return { alto: i.scrollHeight, texto: i.innerText };
}, { esquema, campos: doc.campos, constantes, tipo: TIPOID, folio: expe.folio });

await pagina.pdf({ path: SALIDA, format: 'Letter',
  margin: { top: '8mm', right: '4mm', bottom: '12mm', left: '4mm' },
  printBackground: true });

console.log('alto en pantalla a 816 px: ' + info.alto + ' px');
console.log('--- texto impreso ---\n' + info.texto);
await navegador.close();
