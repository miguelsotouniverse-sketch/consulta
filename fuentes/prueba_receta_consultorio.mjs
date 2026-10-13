/* ============================================================
   PRUEBA PERMANENTE — LA RECETA DE CONSULTORIO LLEVA VARIOS MEDICAMENTOS

   Antes era un solo medicamento por receta. Esta prueba escribe tres —uno
   general, un antibiótico y un controlado—, imprime a PDF y comprueba que:
     · los tres salen,
     · el antibiótico y el controlado van en su propia hoja, como pide la ley,
     · cada pliego cabe en su hoja y trae su firma,
     · la ficha no inventa un «Procedimiento» (esto no sale de una cirugía) y
       sí imprime las alergias,
     · una receta vieja, de cinco campos sueltos, se convierte en un renglón
       en vez de perderse.

   Uso: node prueba_receta_consultorio.mjs [index.html] [recetas.json]
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
const dir = mkdtempSync(join(tmpdir(), 'rxc-'));

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

/* ---- 1. tres medicamentos, repartidos por hoja ---- */
const r = await pag.evaluate(({ esquema, cat, constantes }) => {
  ESQUEMA = esquema; RECETAS = cat; CONSTANTES = constantes; PLANTILLA = null;
  TIPO = DOCUMENTOS.filter(function(d){ return d.id === 'receta'; })[0];
  VALORES = {
    expediente_folio: 'P-PRUEBA',
    paciente_nombres: 'María Fernanda Guadalupe',
    paciente_apellido_paterno: 'Hernández',
    paciente_apellido_materno: 'Villaseñor',
    paciente_sexo: 'Femenino', paciente_edad: '48',
    rx_otras: 'penicilina',
    rx_renglones: [
      { hoja:'general', nombre:'Paracetamol 500 mg, tabletas.',
        indicacion:'Tomar 2 tabletas vía oral cada 8 horas durante 5 días.',
        cantidad:'30 tabletas', duracion:'5 días', rescate:false, horario:null },
      { hoja:'antibiotico', nombre:'Amoxicilina 500 mg, cápsulas.',
        indicacion:'Tomar 1 cápsula vía oral cada 8 horas durante 7 días.',
        cantidad:'21 cápsulas', duracion:'7 días', rescate:false, horario:null },
      { hoja:'controlado', nombre:'Tramadol 50 mg, cápsulas.',
        indicacion:'Tomar 1 cápsula cada 8 horas sólo si hay dolor intenso.',
        cantidad:'9 cápsulas', duracion:'3 días', rescate:true, horario:null }
    ]
  };
  PENDIENTE_DICTADO = {}; FOLIO='P-PRUEBA'; DOC_ID='ffff'; CORREO='consultorio@ejemplo.mx';

  const falta = faltantesReceta();
  armaImpresion();
  const raiz = document.getElementById('impresion');
  raiz.style.display = 'block';
  const pliegos = [...raiz.querySelectorAll('.receta')].map(function(el){
    return { titulo: ((el.querySelector('h1')||{}).textContent||'').trim(),
             firma: !!el.querySelector('.firma'),
             alarma: !!el.querySelector('.rxAlarma') };
  });
  return { falta, pliegos, texto: raiz.innerText };
}, { esquema, cat, constantes });

const ruta = join(dir, 'consultorio.pdf');
await pag.pdf({ path: ruta, format:'Letter',
  margin:{ top:'8mm', right:'4mm', bottom:'12mm', left:'4mm' }, printBackground:true });
const paginas = (await PDFDocument.load(readFileSync(ruta))).getPageCount();

revisa('no falta nada para imprimir', r.falta.length === 0, JSON.stringify(r.falta));
revisa('los tres medicamentos salen impresos',
  ['Paracetamol','Amoxicilina','Tramadol'].every((m) => r.texto.includes(m)),
  'faltó alguno');
revisa('son tres pliegos: general, antibiótico y controlado',
  r.pliegos.length === 3, r.pliegos.map((p)=>p.titulo).join(' | '));
revisa('cada pliego cabe en su hoja', paginas === r.pliegos.length,
  paginas + ' páginas para ' + r.pliegos.length + ' pliegos');
revisa('cada pliego va firmado', r.pliegos.every((p) => p.firma), 'falta una firma');
revisa('sin caja de signos de alarma (es del postoperatorio)',
  r.pliegos.every((p) => !p.alarma), 'apareció una caja de alarma');
revisa('la ficha no inventa un procedimiento',
  !r.texto.includes('PROCEDIMIENTO'), 'imprimió un renglón de procedimiento');
revisa('la ficha imprime las alergias', r.texto.toLowerCase().includes('penicilina'),
  'no salieron las alergias');

/* ---- 2. una receta vieja se convierte en un renglón ---- */
const m = await pag.evaluate(({ esquema, cat, constantes }) => {
  ESQUEMA = esquema; RECETAS = cat; CONSTANTES = constantes; PLANTILLA = null;
  TIPO = DOCUMENTOS.filter(function(d){ return d.id === 'receta'; })[0];
  VALORES = { rx_medicamento:'Ibuprofeno 400 mg', rx_dosis:'1 tableta',
              rx_via:'Oral', rx_frecuencia:'cada 8 horas', rx_duracion:'5 días' };
  migraRecetaVieja_();
  return VALORES['rx_renglones'];
}, { esquema, cat, constantes });

revisa('la receta vieja de cinco campos se convierte en un renglón',
  m.length === 1 && m[0].nombre === 'Ibuprofeno 400 mg' &&
  m[0].indicacion === '1 tableta, vía oral, cada 8 horas, durante 5 días.' &&
  m[0].duracion === '5 días',
  JSON.stringify(m));

/* ---- 3. el editor: se escribe uno y se agrega otro ---- */
const e = await pag.evaluate(async ({ esquema, cat, constantes }) => {
  ESQUEMA = esquema; CONSTANTES = constantes; PLANTILLA = null;
  /* Se precarga el catálogo para que cargaRecetas() no salga a la red: esta
     prueba corre sin servidor. */
  RECETAS = cat; RECETAS_AL = Date.now();
  TIPO = DOCUMENTOS.filter(function(d){ return d.id === 'receta'; })[0];
  VALORES = { paciente_nombres:'Ana', paciente_apellido_paterno:'Ruiz' };
  PENDIENTE_DICTADO = {}; FOLIO='P-PRUEBA'; DOC_ID='ffff'; CORREO='x@y.mx';

  armaReceta();
  await new Promise(function(r){ setTimeout(r, 60); });

  const antes = (VALORES['rx_renglones'] || []).length;
  const campos = [...document.querySelectorAll('#formulario label')]
    .map(function(l){ return l.textContent; });
  const botones = [...document.querySelectorAll('#formulario button')]
    .map(function(b){ return b.textContent; });
  const agregar = [...document.querySelectorAll('#formulario button')]
    .filter(function(b){ return /Agregar un medicamento/.test(b.textContent); })[0];
  if (agregar) agregar.click();
  await new Promise(function(r){ setTimeout(r, 60); });
  const despues = (VALORES['rx_renglones'] || []).length;

  const quitar = [...document.querySelectorAll('#formulario button')]
    .filter(function(b){ return /Quitar este medicamento/.test(b.textContent); })[0];
  if (quitar) quitar.click();
  await new Promise(function(r){ setTimeout(r, 60); });

  return { antes: antes, despues: despues,
           tras_quitar: (VALORES['rx_renglones'] || []).length,
           campos: campos, botones: botones,
           sinPlantilla: !document.body.innerText.includes('Plantilla de receta') };
}, { esquema, cat, constantes });

revisa('el editor arranca con un renglón listo para escribir', e.antes === 1, String(e.antes));
revisa('«Agregar un medicamento» agrega otro renglón', e.despues === 2,
  e.antes + ' → ' + e.despues);
revisa('«Quitar este medicamento» quita uno', e.tras_quitar === 1, String(e.tras_quitar));
revisa('el renglón pide medicamento, indicación, cantidad y duración',
  ['Medicamento','Cantidad','Duración del tratamiento'].every(function(x){
    return e.campos.some(function(c){ return c.indexOf(x) === 0; }); }),
  e.campos.join(' | '));
revisa('deja escoger si va en la hoja de antibiótico o de controlado',
  e.campos.some(function(c){ return /Va en la receta/.test(c); }), e.campos.join(' | '));
revisa('no pide escoger plantilla', e.sinPlantilla, 'apareció el selector de plantilla');
revisa('no ofrece «Volver a la plantilla»',
  !e.botones.some(function(b){ return /Volver a la plantilla/.test(b); }),
  e.botones.join(' | '));

await nav.close();
console.log(fallas ? `\n${fallas} caso(s) mal` : '\nLa receta de consultorio lleva varios medicamentos.');
process.exit(fallas ? 1 : 0);
