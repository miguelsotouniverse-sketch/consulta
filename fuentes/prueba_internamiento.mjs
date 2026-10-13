/* ============================================================
   PRUEBA PERMANENTE — ORDEN DE INTERNAMIENTO Y CONSTANCIA DE ACOMPAÑANTE

   El médico pidió una orden de internamiento para mandar a Renasté o a
   Zorvix, y mencionó que a su paciente le servía además para que su hija la
   justificara en el trabajo. Son dos documentos distintos, y la razón de que
   sean dos es lo que esta prueba defiende:

     EL CANDADO — la constancia que va a manos de un patrón NO puede imprimir
     el diagnóstico ni el procedimiento, aunque el expediente los tenga
     capturados. Se comprueba con el expediente LLENO: si algún día alguien le
     agrega campos a ese documento sin pensarlo, esta prueba truena.

   Además comprueba que:
     · la orden sí lleva lo que la unidad necesita para recibir a la paciente;
     · las dos caben en UNA hoja, firmadas, que es como se mandan por correo;
     · la orden empieza por el procedimiento, no por el contacto de urgencia;
     · la hora de ingreso se calcula hacia atrás desde el inicio programado;
     · ninguno de los dos documentos captura un campo que no exista ya en el
       esquema de Base Datos.

   Uso: node prueba_internamiento.mjs [index.html]
   ============================================================ */
import playwright from '/opt/npm-tools/node_modules/playwright/index.js';
const { chromium } = playwright;
import { PDFDocument } from '/opt/npm-tools/node_modules/pdf-lib/cjs/index.js';
import { readFileSync, mkdtempSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { tmpdir } from 'node:os';

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
const dir = mkdtempSync(join(tmpdir(), 'ord-'));

/* Un expediente COMPLETO. Si la constancia filtrara algo, aquí hay de dónde. */
const SECRETOS = {
  diagnosticos: 'Lipodistrofia localizada de abdomen, flancos y espalda.',
  preop_riesgo: 'ASA II. Riesgo quirúrgico bajo.',
  proc_nombre: 'Lipoescultura Body360®',
  app_alergicos: 'Niega alergia a medicamentos.',
  caprini_profilaxis: 'Deambulación temprana y medias de compresión.',
  app_quirurgicos: 'Cesárea hace 20 años.',
  evolucion_cuadro: 'Paciente estable, sin cambios desde la valoración.'
};
const EXPEDIENTE = Object.assign({
  expediente_folio:'P-2026-0418', paciente_nombres:'María Fernanda',
  paciente_apellido_paterno:'Hernández', paciente_apellido_materno:'Villaseñor',
  paciente_sexo:'Femenino', paciente_edad:'52',
  proc_establecimiento:'Clínicas Renasté', proc_fecha:'2026-10-14',
  proc_hora_inicio:'08:00', proc_anestesia:'General', sv_peso:'68',
  caprini_riesgo:'Moderado (2)',
  urgencia_nombre:'Ana Sofía Robles Hernández', urgencia_parentesco:'Hija',
  urgencia_telefono:'55 2244 8890'
}, SECRETOS);

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

async function arma(tipoid, firmar){
  const r = await pag.evaluate(({ esquema, constantes, valores, tipoid, firmar }) => {
    ESQUEMA = esquema; CONSTANTES = constantes;
    TIPO = DOCUMENTOS.filter(function(d){ return d.id === tipoid; })[0];
    if (!TIPO) return { falta: true };
    VALORES = JSON.parse(JSON.stringify(valores));
    if (firmar) VALORES['doc_estado_firma'] = 'Firmado';
    PENDIENTE_DICTADO = {}; FOLIO = 'P-2026-0418'; DOC_ID = 'ffff';
    CORREO = 'consultorio@miguelsotomd.com';
    armaImpresion();
    const i = document.getElementById('impresion');
    i.style.display = 'block';
    return {
      texto: i.innerText,
      encabezados: [...i.querySelectorAll('h2')].map(function(x){ return x.textContent; }),
      campos: (TIPO.campos || null),
      rubricas: i.querySelectorAll('img.rubrica').length
    };
  }, { esquema, constantes, valores: EXPEDIENTE, tipoid, firmar });
  if (r.falta) return r;
  const ruta = join(dir, tipoid + '.pdf');
  await pag.pdf({ path: ruta, format:'Letter',
    margin:{ top:'8mm', right:'4mm', bottom:'12mm', left:'4mm' }, printBackground:true });
  r.paginas = (await PDFDocument.load(readFileSync(ruta))).getPageCount();
  return r;
}

const orden = await arma('orden_internamiento', true);
const cons  = await arma('constancia_acompanante', true);

revisa('existe el tipo «orden de internamiento»', !orden.falta, 'no está en DOCUMENTOS');
revisa('existe el tipo «constancia de acompañante»', !cons.falta, 'no está en DOCUMENTOS');

/* ---- el candado ---- */
const filtrados = Object.entries(SECRETOS).filter(function(par){
  return cons.texto.indexOf(par[1]) >= 0;
});
revisa('LA CONSTANCIA NO FILTRA NINGÚN DATO CLÍNICO',
  filtrados.length === 0,
  'se filtró: ' + filtrados.map(function(p){ return p[0]; }).join(', '));
revisa('la constancia no imprime encabezados de grupos clínicos',
  cons.encabezados.length === 0, cons.encabezados.join(' | '));
revisa('la constancia declara su lista de campos vacía',
  Array.isArray(cons.campos) && cons.campos.length === 0, JSON.stringify(cons.campos));
revisa('la constancia sí nombra al acompañante y su parentesco',
  /Ana Sofía Robles Hernández/.test(cons.texto) && /hija/i.test(cons.texto), '');
revisa('la constancia dice por qué no trae el diagnóstico',
  /secreto profesional/.test(cons.texto), 'falta la aclaración');

/* ---- la orden ---- */
const debeTraer = ['Lipoescultura Body360®', 'Clínicas Renasté', 'General',
                   'Lipodistrofia', 'ASA II', 'Niega alergia',
                   'Moderado (2)', 'Ana Sofía Robles Hernández'];
const faltan = debeTraer.filter(function(x){ return orden.texto.indexOf(x) < 0; });
revisa('la orden lleva todo lo que la unidad necesita', faltan.length === 0,
  'falta: ' + faltan.join(', '));
revisa('la orden va dirigida al establecimiento por su nombre',
  /solicito el internamiento[\s\S]*Clínicas Renasté/.test(orden.texto), '');
revisa('la orden empieza por el procedimiento',
  orden.encabezados[0] === 'Procedimiento', orden.encabezados.join(' | '));
revisa('la hora de ingreso se calcula hacia atrás desde el inicio',
  /a las 06:00 h/.test(orden.texto), 'inicio 08:00 menos 2 h debería dar 06:00');

/* ---- las dos son de una hoja, firmadas ---- */
revisa('la orden cabe en una hoja, firmada',
  orden.paginas === 1 && orden.rubricas === 1,
  orden.paginas + ' páginas, ' + orden.rubricas + ' firmas');
revisa('la constancia cabe en una hoja, firmada',
  cons.paginas === 1 && cons.rubricas === 1,
  cons.paginas + ' páginas, ' + cons.rubricas + ' firmas');

/* ---- ningún campo inventado ---- */
const idsEsquema = new Set(esquema.campos.map(function(c){ return c.id; }));
const inventados = (orden.campos || []).filter(function(id){ return !idsEsquema.has(id); });
revisa('la orden no inventa ningún campo fuera del esquema',
  inventados.length === 0, inventados.join(', '));

await nav.close();
console.log(fallas ? `\n${fallas} caso(s) mal`
                   : '\nLa orden va a la unidad; la constancia, sin un solo dato clínico.');
process.exit(fallas ? 1 : 0);
