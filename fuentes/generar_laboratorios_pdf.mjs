/* ============================================================
   LA SOLICITUD DE LABORATORIOS, COMO PDF FIJO
   ============================================================

   Para qué
   --------
   La solicitud de laboratorios preoperatorios es el único documento del
   sistema que no depende de la paciente: los mismos siete estudios, las
   mismas instrucciones de ayuno y el mismo número de WhatsApp para todas.
   Hoy, para mandársela a alguien, hay que abrir el expediente, buscarla,
   imprimirla o generar el PDF por paciente. Eso convierte un «mándame los
   laboratorios» de WhatsApp en cinco minutos de sistema.

   Este archivo produce UN PDF, el mismo para todas, publicado en
   `consulta.miguelsotomd.com/laboratorios.pdf`. Se manda por WhatsApp
   pegando la liga, sin abrir nada.

   De dónde sale el texto
   ----------------------
   De `indicaciones.json`, hoja `laboratorios` — el mismo texto aprobado que
   se imprime desde el expediente, leído del catálogo y nunca retecleado
   aquí. Si mañana cambia un estudio en la hoja, se vuelve a correr esto y el
   PDF cambia con ella.

   Qué se le quita y qué se le pone, respecto de la hoja del expediente
   -------------------------------------------------------------------
   · Se le quita la ficha de la paciente (nombre, expediente, fecha del
     procedimiento). Un PDF que sirve para todas no puede traer el nombre de
     una, y una ficha con guiones se lee como un documento a medio llenar.
     La propia entrada de la hoja ya dice que aplica a todos los pacientes.
   · Se le quita el cuadro de firma autógrafa y en su lugar va la firma
     visual del médico, con el pie de «documento emitido y enviado por medio
     electrónico» — es exactamente el caso para el que se hizo esa firma:
     un documento que se manda digital y que nadie va a imprimir para firmar.
   · Se le quita el folio de documento. No hay expediente del cual sacarlo.
     Al pie queda la versión de la hoja, que es lo que permite saber después
     qué texto exacto se mandó.

   Nada de esto se toca en `index.html`: la hoja impresa desde el expediente
   sigue igual, con su ficha y su firma autógrafa. Los cambios se hacen aquí,
   sobre el documento ya armado por el sistema, para que el PDF herede el
   membrete, los estilos y el texto reales y no una copia que se desactualiza.

   Uso:  node generar_laboratorios_pdf.mjs [index.html] [indicaciones.json] [salida.pdf]
   ============================================================ */
import playwright from '/opt/npm-tools/node_modules/playwright/index.js';
const { chromium } = playwright;
import pdflib from '/opt/npm-tools/node_modules/pdf-lib/cjs/index.js';
const { PDFDocument } = pdflib;
import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';

function dondeEste(nombre){
  const sitios = [nombre, '../' + nombre, '/home/claude/' + nombre,
                  '/mnt/user-data/outputs/' + nombre];
  for (const s of sitios){ try { return readFileSync(resolve(s), 'utf8'); } catch(e){} }
  throw new Error('No encuentro ' + nombre + '. Lo busqué en: ' + sitios.join(', '));
}

const HTML = resolve(process.argv[2] || 'index.html');
const IND  = resolve(process.argv[3] || 'indicaciones.json');
const OUT  = resolve(process.argv[4] || 'laboratorios.pdf');

const esquema = JSON.parse(dondeEste('campos.json'));
const cat = JSON.parse(readFileSync(IND, 'utf8'));
let constantes = JSON.parse(dondeEste('constantes.json'));
if (constantes.campos) constantes = constantes.campos;

if (!constantes['medico_firma'])
  throw new Error('No hay firma visual en las constantes; el PDF saldría sin firmar.');

const nav = await chromium.launch();
const pag = await nav.newPage({ viewport: { width: 816, height: 1056 } });
/* Sólo file://: el membrete carga `ms-horizontal.png` de junto al HTML y nada
   más debe salir a la red mientras se arma el documento. */
await pag.route('**/*', (r) =>
  r.request().url().startsWith('file://') ? r.continue() : r.abort());
await pag.goto('file://' + HTML);

const info = await pag.evaluate(({ esquema, cat, constantes }) => {
  ESQUEMA = esquema; INDICACIONES = cat; CONSTANTES = constantes;
  TIPO = DOCUMENTOS.filter(function(d){ return d.id === 'indicaciones_alta'; })[0];
  HOJA = cat.hojas.filter(function(h){ return h.id === 'laboratorios'; })[0];
  if (!HOJA) throw new Error('no existe la hoja laboratorios en el catálogo');

  /* Sin paciente, y firmado: las dos cosas que distinguen este PDF de la
     misma hoja impresa desde un expediente. */
  VALORES = { indicaciones_hoja: 'laboratorios', doc_estado_firma: 'Firmado' };
  PENDIENTE_DICTADO = {}; FOLIO = ''; DOC_ID = ''; CORREO = '';

  armaImpresion();
  var raiz = document.getElementById('impresion');

  /* --- fuera la ficha de la paciente --- */
  var ficha = raiz.querySelector('table.ficha');
  if (!ficha) throw new Error('no encontré la ficha; cambió pintaHojaImpresa');
  ficha.remove();

  /* --- fuera el cuadro de firma autógrafa, dentro la firma visual --- */
  var autografa = raiz.querySelector('.firmasHoja');
  if (!autografa) throw new Error('no encontré el cuadro de firmas de la hoja');
  autografa.remove();

  function div(clase, texto){
    var e = document.createElement('div');
    if (clase) e.className = clase;
    if (texto !== undefined) e.textContent = texto;
    return e;
  }
  var f = div('firma');
  var r = rubrica_();
  if (!r) throw new Error('rubrica_() no devolvió nada: el documento saldría sin firma');
  f.appendChild(r);
  f.appendChild(div('linea'));
  f.appendChild(div('n', CONSTANTES['medico_nombre'] || ''));
  var ced = [CONSTANTES['medico_cedula_prof'] ? 'Cédula profesional ' + CONSTANTES['medico_cedula_prof'] : '',
             CONSTANTES['medico_cedula_esp'] ? 'Cédula de especialidad ' + CONSTANTES['medico_cedula_esp'] : ''
            ].filter(Boolean).join('  ·  ');
  if (ced) f.appendChild(div('c', ced));
  if (CONSTANTES['medico_consejo']) f.appendChild(div('c', CONSTANTES['medico_consejo']));
  f.appendChild(div('c', pieFirma_()));

  /* --- el pie, sin folio de documento --- */
  var pie = raiz.querySelector('.pieimp');
  if (!pie) throw new Error('no encontré el pie de la hoja');
  pie.parentNode.insertBefore(f, pie);
  pie.innerHTML = '';
  pie.appendChild(div('f', HOJA.nombre + ' · versión ' + HOJA.version +
                           ' · solicitud general, sin folio de documento'));
  /* Para quien tenga el PDF guardado y quiera asegurarse de que es el
     vigente: la liga donde siempre está el último. */
  pie.appendChild(div(null, 'consulta.miguelsotomd.com/laboratorios.pdf'));

  raiz.style.display = 'block';
  return { texto: raiz.innerText, version: HOJA.version,
           titulo: HOJA.titulo, firma: pieFirma_(),
           sinFicha: !raiz.querySelector('table.ficha'),
           sinFirmaAutografa: !raiz.querySelector('.firmasHoja'),
           conRubrica: !!raiz.querySelector('.firma .rubrica') };
}, { esquema, cat, constantes });

await pag.pdf({ path: OUT, format: 'Letter',
  margin: { top:'8mm', right:'4mm', bottom:'12mm', left:'4mm' }, printBackground: true });
await nav.close();

/* ---- revisión de lo que salió ---- */
const doc = await PDFDocument.load(readFileSync(OUT));
const paginas = doc.getPageCount();

let fallas = 0;
function revisa(nombre, bien, detalle){
  console.log((bien ? '✓ ' : '✗ ') + nombre + (bien ? '' : '   → ' + (detalle || '')));
  if (!bien) fallas++;
}

const T = info.texto;
revisa('cabe en una hoja', paginas === 1, paginas + ' páginas');
revisa('trae el título de la hoja', /SOLICITUD DE LABORATORIOS/i.test(T), T.slice(0, 80));

/* Los siete estudios, leídos del catálogo y no de una lista escrita aquí:
   así la revisión sigue valiendo si mañana se agrega o se quita uno. */
const hoja = cat.hojas.filter((h) => h.id === 'laboratorios')[0];
const estudios = hoja.bloques.filter((b) => b.t === 'ul')
  .reduce((a, b) => a.concat(b.x), []);
const faltan = estudios.filter((e) => T.indexOf(e) < 0);
revisa('trae los ' + estudios.length + ' renglones de la hoja, completos',
  faltan.length === 0, faltan.join(' | ').slice(0, 160));

revisa('no trae la ficha de ninguna paciente', info.sinFicha, 'quedó la ficha');
/* Un dato vacío se imprime como un guión largo solo en su renglón; el guión
   del membrete («Dr. Miguel Soto — Cirugía Plástica…») no cuenta. */
const huecos = T.split('\n').filter((l) => l.trim() === '—' || /\t\s*$/.test(l));
revisa('no quedó ningún hueco por llenar a mano',
  info.sinFirmaAutografa && huecos.length === 0,
  huecos.join(' / ').slice(0, 120));
revisa('no trae un folio de documento inventado',
  !/-INDALT-|P-PRUEBA|ffff/.test(T), '');
revisa('va firmado, y lo dice',
  info.conRubrica && /medio electrónico/.test(T), info.firma);
revisa('trae la cédula del médico', /Cédula profesional/.test(T), '');
revisa('dice a dónde se mandan los resultados', /55\s?6223\s?4133/.test(T), '');
revisa('deja constancia de la versión del texto',
  T.indexOf(info.version) >= 0, info.version);

console.log('\n' + OUT + '  ·  ' + paginas + ' página(s)  ·  hoja versión ' + info.version);
console.log(fallas ? fallas + ' caso(s) mal' : 'El PDF está listo para mandarse.');
process.exit(fallas ? 1 : 0);
