/* ============================================================
   PRUEBA PERMANENTE — CADA RECETA CABE EN SU HOJA, CON SU FIRMA

   Una hoja con medicamentos y sin firma no es una receta: la farmacia no
   tiene por qué adivinar que la firma venía atrás. Ya pasó dos veces al
   crecer el contenido.

   La prueba NO mide la altura en pantalla. Se intentó así y mentía: en
   pantalla el texto tiene todo el ancho de la ventana, y al imprimir la
   columna se angosta por los márgenes de @page y el relleno de #impresion,
   así que el texto envuelve más y el pliego crece. Un pliego medía 940 px
   "de sobra" y en el PDF se pasaba a la hoja siguiente.

   Así que se imprime de verdad a PDF y se cuenta: cada pliego arranca en
   hoja nueva (`page-break-before: always`), de modo que si el PDF trae más
   páginas que pliegos, alguno se desbordó. Ésa es la prueba, y no admite
   discusión.

   Uso: node prueba_recetas_paginas.mjs [index.html] [recetas.json]
   ============================================================ */
import playwright from '/opt/npm-tools/node_modules/playwright/index.js';
const { chromium } = playwright;
import { PDFDocument } from '/opt/npm-tools/node_modules/pdf-lib/cjs/index.js';
import { readFileSync, mkdtempSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { tmpdir } from 'node:os';

/* Busca un archivo de apoyo donde esté: junto al script, en la raíz del
   repositorio, o en la carpeta de trabajo de la sesión donde se construyó.
   Así la prueba corre igual recién clonado el repositorio que aquí. */
function dondeEste(nombre){
  const sitios = [nombre, '../' + nombre, '/home/claude/' + nombre,
                  '/mnt/user-data/outputs/' + nombre];
  for (const s of sitios){ try { return readFileSync(resolve(s), 'utf8'); } catch(e){} }
  throw new Error('No encuentro ' + nombre + '. Lo busqué en: ' + sitios.join(', '));
}


const HTML = resolve(process.argv[2] || 'index.html');
const REC  = resolve(process.argv[3] || 'recetas.json');
const esquema = JSON.parse(dondeEste('campos.json'));
const cat = JSON.parse(readFileSync(REC, 'utf8'));
let constantes = {};
try { constantes = JSON.parse(dondeEste('constantes.json')); } catch(e){}
if (constantes.campos) constantes = constantes.campos;
const dir = mkdtempSync(join(tmpdir(), 'rx-'));

/* Varios escenarios por plantilla: según la alergia y la edad cambian los
   renglones, y el que produce la hoja más larga no siempre es el mismo. */
const ESCENARIOS = [
  { nombre: 'sin alergias, con Bichat, 52 años',
    v: { rx_bichat:'si', rx_peni:'no', rx_sulfa:'no', rx_renal:'no',
         rx_isrs:'no', rx_sintram:'no' }, edad: '52' },
  { nombre: 'sin alergias, sin Bichat, 52 años',
    v: { rx_bichat:'no', rx_peni:'no', rx_sulfa:'no', rx_renal:'no',
         rx_isrs:'no', rx_sintram:'no' }, edad: '52' },
  { nombre: 'alergia grave a penicilina y a sulfas, 70 años',
    v: { rx_bichat:'si', rx_peni:'grave', rx_sulfa:'si', rx_renal:'si',
         rx_isrs:'no', rx_sintram:'no' }, edad: '70' }
];

const nav = await chromium.launch();
const pag = await nav.newPage({ viewport: { width: 816, height: 1056 } });
await pag.route('**/*', (r) =>
  r.request().url().startsWith('file://') ? r.continue() : r.abort());
await pag.goto('file://' + HTML);

let fallas = 0;

for (const p of cat.plantillas)
for (const [n, esc] of ESCENARIOS.entries()){
  const r = await pag.evaluate(({ esquema, cat, id, constantes, esc }) => {
    ESQUEMA = esquema; RECETAS = cat; CONSTANTES = constantes;
    TIPO = DOCUMENTOS.filter(function(d){ return d.id === 'receta_post'; })[0];
    PLANTILLA = cat.plantillas.filter(function(x){ return x.id === id; })[0];
    VALORES = {
      expediente_folio: 'P-PRUEBA',
      /* Nombre largo a propósito: si envuelve en dos renglones, la ficha
         crece y el pliego con ella. */
      paciente_nombres: 'María Fernanda Guadalupe',
      paciente_apellido_paterno: 'Hernández',
      paciente_apellido_materno: 'Villaseñor',
      paciente_sexo: 'Femenino', proc_fecha: '2026-10-10',
      rx_plantilla: PLANTILLA.id, rx_plantilla_version: PLANTILLA.version,
      rx_blefaro: 'si', paciente_edad: esc.edad
    };
    Object.keys(esc.v).forEach(function(k){ VALORES[k] = esc.v[k]; });
    PENDIENTE_DICTADO = {}; FOLIO='P-PRUEBA'; DOC_ID='ffff';
    CORREO='consultorio@ejemplo.mx';
    VALORES['rx_renglones'] = renglonesDe(PLANTILLA, estadoReceta());

    armaImpresion();
    const raiz = document.getElementById('impresion');
    raiz.style.display = 'block';
    const pliegos = [...raiz.querySelectorAll('.receta')].map(function(el){
      return { firma: !!el.querySelector('.firma'),
               titulo: ((el.querySelector('h1')||{}).textContent || '').slice(0,56) };
    });
    return { renglones: VALORES['rx_renglones'].length, pliegos };
  }, { esquema, cat, id: p.id, constantes, esc });

  const ruta = join(dir, p.id + '-' + n + '.pdf');
  await pag.pdf({ path: ruta, format: 'Letter',
    margin: { top:'8mm', right:'4mm', bottom:'12mm', left:'4mm' },
    printBackground: true });
  const paginas = (await PDFDocument.load(readFileSync(ruta))).getPageCount();

  const sinFirma = r.pliegos.filter((x) => !x.firma);
  const mal = paginas !== r.pliegos.length || sinFirma.length;
  console.log(`${mal ? '✗' : '✓'} ${p.id.padEnd(17)} ${esc.nombre.padEnd(46)} ` +
              `${String(r.renglones).padStart(2)} renglones · ` +
              `${r.pliegos.length} pliegos · ${paginas} páginas`);
  if (paginas !== r.pliegos.length)
    console.log(`      ✗ se desbordó: ${paginas - r.pliegos.length} página(s) de más`);
  for (const x of sinFirma) console.log(`      ✗ sin firma: ${x.titulo}`);
  if (mal) fallas++;
}

await nav.close();
console.log(fallas ? `\n${fallas} caso(s) mal` : '\nTodos los pliegos caben en su hoja, con su firma.');
process.exit(fallas ? 1 : 0);
