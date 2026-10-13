/* ============================================================
   PRUEBA PERMANENTE — LA PLANTILLA ES UNA PROPUESTA, NO UNA ORDEN

   El médico pidió poder deseleccionar un medicamento que este caso no lleva
   —el relajante muscular cuando el plano no fue retromuscular, por ejemplo—
   sin borrarlo de la plantilla. Esta prueba comprueba que:

     · cada renglón trae su casilla, visible sin abrir el renglón;
     · quitarle la marca lo saca de la receta impresa;
     · marcar la casilla NO abre ni cierra el renglón (el clic no se propaga);
     · lo deseleccionado NO vuelve cuando se cambia una respuesta de arriba y
       la plantilla se recalcula  ← esto es lo que no se podía hacer antes;
     · una receta sin ningún medicamento dentro no se imprime;
     · a un renglón que está fuera no se le exige la duración.

   Uso: node prueba_casilla_renglones.mjs [index.html] [recetas.json]
   ============================================================ */
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


const HTML = resolve(process.argv[2] || 'index.html');
const REC  = resolve(process.argv[3] || 'recetas.json');
const esquema = JSON.parse(dondeEste('campos.json'));
const cat = JSON.parse(readFileSync(REC, 'utf8'));
let constantes = {};
try { constantes = JSON.parse(dondeEste('constantes.json')); } catch(e){}
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

const r = await pag.evaluate(async ({ esquema, cat, constantes }) => {
  ESQUEMA = esquema; CONSTANTES = constantes;
  RECETAS = cat; RECETAS_AL = Date.now();
  TIPO = DOCUMENTOS.filter(function(d){ return d.id === 'receta_post'; })[0];
  VALORES = {
    expediente_folio:'P-PRUEBA',
    paciente_nombres:'María Fernanda', paciente_apellido_paterno:'Hernández',
    paciente_apellido_materno:'Villaseñor',
    paciente_sexo:'Femenino', paciente_edad:'48',
    rx_plantilla:'deep_plane',
    rx_peni:'no', rx_sulfa:'no', rx_bichat:'no', rx_blefaro:'no',
    rx_renal:'no', rx_sintram:''
  };
  PENDIENTE_DICTADO = {}; FOLIO='P-PRUEBA'; DOC_ID='ffff'; CORREO='x@y.mx';

  armaReceta();
  await new Promise(function(f){ setTimeout(f, 120); });

  const esp = function(){ return new Promise(function(f){ setTimeout(f, 80); }); };
  const casillas = function(){
    return [...document.querySelectorAll('#formulario details.grupo > summary input[type=checkbox]')];
  };

  const out = {};
  out.renglones  = (VALORES['rx_renglones'] || []).length;
  out.casillas   = casillas().length;
  out.todasDentro = (VALORES['rx_renglones'] || []).every(function(x){ return !x.fuera; });
  out.todasMarcadas = casillas().every(function(c){ return c.checked; });

  /* --- se deselecciona el paracetamol, que es un renglón fijo de la plantilla --- */
  const rs = VALORES['rx_renglones'];
  const iPara = rs.findIndex(function(x){ return /Paracetamol/i.test(x.nombre); });
  out.encontroParacetamol = iPara >= 0;
  const nombreQuitado = iPara >= 0 ? rs[iPara].nombre : '';
  out.nombreQuitado = nombreQuitado;

  const det = [...document.querySelectorAll('#formulario details.grupo')]
    .filter(function(d){ return /Paracetamol/i.test(d.querySelector('.titulo').textContent); })[0];
  const abiertoAntes = det.open;
  det.querySelector('summary input[type=checkbox]').click();
  await esp();
  out.clicNoAbrio = (det.open === abiertoAntes);
  out.quedoFuera = !!(VALORES['rx_renglones'] || [])
    .filter(function(x){ return x.nombre === nombreQuitado; })[0].fuera;

  /* --- no se imprime --- */
  armaImpresion();
  const imp = document.getElementById('impresion');
  out.noSaleImpreso = !/Paracetamol/i.test(imp.innerText);
  out.saleOtro = /Amoxicilina|Celecoxib/i.test(imp.innerText);

  /* --- el contador de pantalla no lo cuenta --- */
  out.encabezado = ([...document.querySelectorAll('#formulario .seccion')]
    .filter(function(e){ return /^Medicamentos/.test(e.textContent); })[0] || {}).textContent || '';

  /* --- se cambia una respuesta de arriba: la plantilla se recalcula --- */
  const sel = document.querySelector('[data-campo="rx_renal"]');
  sel.value = 'si';
  sel.dispatchEvent(new Event('change', { bubbles:true }));
  await esp();
  const tras = (VALORES['rx_renglones'] || [])
    .filter(function(x){ return x.nombre === nombreQuitado; })[0];
  out.recalculo = /cada 24 horas/i.test(JSON.stringify(VALORES['rx_renglones']));
  out.sigueFuera = !!(tras && tras.fuera);

  /* --- la duración vacía de un renglón fuera no estorba --- */
  tras.duracion = '';
  out.faltaConFuera = faltantesReceta().join(' | ');

  /* --- si se deselecciona todo, no se imprime --- */
  (VALORES['rx_renglones'] || []).forEach(function(x){ x.fuera = true; });
  out.faltaTodoFuera = faltantesReceta().join(' | ');

  return out;
}, { esquema, cat, constantes });

revisa('la plantilla arranca con todos los renglones dentro',
  r.renglones > 0 && r.todasDentro, r.renglones + ' renglones');
revisa('cada renglón trae su casilla en el resumen, sin abrirlo',
  r.casillas === r.renglones && r.todasMarcadas,
  r.casillas + ' casillas para ' + r.renglones + ' renglones');
revisa('marcar la casilla no abre ni cierra el renglón', r.clicNoAbrio,
  'el clic se propagó al summary');
revisa('quitarle la marca lo saca de la receta', r.quedoFuera, r.nombreQuitado);
revisa('el renglón deseleccionado no se imprime', r.noSaleImpreso,
  'el paracetamol siguió saliendo en el PDF');
revisa('los demás medicamentos sí se imprimen', r.saleOtro,
  'se perdió todo, no sólo el deseleccionado');
revisa('el contador de pantalla lo reporta fuera',
  /fuera de la receta/.test(r.encabezado), r.encabezado);
revisa('cambiar una respuesta de arriba sí recalcula la plantilla', r.recalculo,
  'el celecoxib no cambió a cada 24 horas');
revisa('lo deseleccionado NO vuelve tras el recálculo', r.sigueFuera,
  'el paracetamol resucitó al cambiar la respuesta');
revisa('a un renglón fuera no se le exige la duración',
  !/duración/i.test(r.faltaConFuera), r.faltaConFuera);
revisa('con todo deseleccionado no se puede imprimir',
  /al menos un medicamento/.test(r.faltaTodoFuera), r.faltaTodoFuera);

await nav.close();
console.log(fallas ? `\n${fallas} caso(s) mal`
                   : '\nLa plantilla propone y el médico decide.');
process.exit(fallas ? 1 : 0);
