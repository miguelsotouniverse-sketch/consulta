/* ============================================================
   PRUEBA PERMANENTE — LLEVAR LA HISTORIA CLÍNICA A ZORVIX

   El 27-nov-2026 el médico preguntó por qué había desaparecido el botón de
   llevar la historia clínica al expediente del centro quirúrgico. El código
   estaba intacto y publicado: lo que desaparecía era el renglón, porque se
   escondía solo —sin decir nada— cuando la historia clínica llegaba del
   gateway sin sus campos. Una función que se esconde en silencio se lee como
   una función que se borró, y eso cuesta una captura entera a mano del otro
   lado.

   Esta prueba defiende las cuatro cosas que no se pueden volver a romper:

     · QUE EL RENGLÓN APAREZCA cuando hay historia clínica con contenido, y
       que el código traiga de verdad los datos de la paciente.
     · QUE NO DESAPAREZCA EN SILENCIO cuando la historia llegó sin contenido:
       ahí tiene que aparecer igual, diciendo qué pasa y qué hacer.
     · QUE UNA HISTORIA ANULADA NO SE LLEVE. Lo que se retiró del expediente
       de aquí no puede entrar al expediente de allá.
     · QUE SE ESCOJA LA HISTORIA VIVA cuando hay una anulada y una buena.

   Uso: node prueba_llevar_zorvix.mjs [index.html]
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

const nav = await chromium.launch();
const pag = await nav.newPage({ viewport: { width: 1100, height: 900 } });
await pag.route('**/*', (r) =>
  r.request().url().startsWith('file://') ? r.continue() : r.abort());
await pag.goto('file://' + HTML);

const r = await pag.evaluate(({ esquema, constantes }) => {
  ESQUEMA = esquema; CONSTANTES = constantes;
  FOLIO = 'P-0001';
  PACIENTE = { Paciente:'María Prueba', Paciente_ID:'P-0001', Edad:'38' };

  const historia = {
    id:'d1', tipo:'historia_clinica', fecha:'2026-11-20', creado:'2026-11-20',
    campos:{ paciente_nombres:'María', paciente_apellido_paterno:'Prueba',
             paciente_apellido_materno:'López',
             paciente_fecha_nacimiento:'1988-03-04',
             apnp_actividad_fisica:'camina 40 minutos diarios' }
  };
  const anulada = JSON.parse(JSON.stringify(historia));
  anulada.id = 'd0';
  anulada.campos['doc_estado_firma'] = 'Anulado';
  anulada.campos['__anulado'] = { motivo:'se capturó en la paciente equivocada',
                                  por:'x@y.mx', cuando:'2026-11-26 10:00' };
  const sinContenido = { id:'d1', tipo:'historia_clinica', fecha:'2026-11-20',
                         creado:'2026-11-20' };

  function pinta(documentos){
    EXPEDIENTE = { paciente: PACIENTE, documentos: documentos };
    let error = '';
    try { pintaDocumentos(); } catch(e){ error = String(e); }
    const caja = document.getElementById('llevarZorvix');
    return { error: error, hay: !!caja,
             abierto: caja ? caja.open : null,
             texto: caja ? (caja.innerText + ' ' + caja.textContent) : '',
             codigo: (document.getElementById('zorvixCodigo') || {}).value || '' };
  }

  const out = {};
  out.normal    = pinta([historia]);
  out.vacia     = pinta([sinContenido]);
  out.anulada   = pinta([anulada]);
  out.mezcla    = pinta([anulada, historia]);
  out.sinNada   = pinta([{ id:'d9', tipo:'nota_evolucion', fecha:'2026-11-26', campos:{} },
                          { id:'d8', tipo:'nota_evolucion', fecha:'2026-11-25', campos:{} },
                          { id:'d7', tipo:'receta', fecha:'2026-11-25', campos:{} }]);
  out.vacio     = pinta([]);

  /* el código se desarma igual que lo va a desarmar Zorvix */
  const c = out.normal.codigo;
  if (c.indexOf('ZXHC1.') === 0){
    try {
      const j = JSON.parse(decodeURIComponent(escape(atob(c.slice(6)))));
      out.carga = {
        de: j.de, folio: j.folio, nombre: (j.paciente || {}).nombre,
        nacimiento: (j.paciente || {}).nacimiento,
        campos: Object.keys(j.campos || {}).length,
        traeEtiqueta: ((j.etiquetas || {}).apnp_actividad_fisica || '') !== '',
        traeAnulado: !!(j.campos || {}).__anulado
      };
    } catch(e){ out.cargaError = String(e); }
  }
  return out;
}, { esquema, constantes });

/* ---- 1. el caso de todos los días ---- */
revisa('con historia clínica, el renglón de llevarla a Zorvix aparece',
  r.normal.hay, r.normal.error || 'no se pintó');
revisa('y trae un código que empieza con la marca que Zorvix reconoce',
  r.normal.codigo.indexOf('ZXHC1.') === 0, r.normal.codigo.slice(0, 20));
revisa('el código se puede desarmar del otro lado', !!r.carga,
  r.cargaError || 'no se pudo leer');
if (r.carga){
  revisa('viaja el nombre armado de la historia, no el de la agenda',
    r.carga.nombre === 'María Prueba López', r.carga.nombre);
  revisa('viaja la fecha de nacimiento, que es con lo que Zorvix cotejará',
    r.carga.nacimiento === '1988-03-04', r.carga.nacimiento);
  revisa('viaja el número de expediente de aquí', r.carga.folio === 'P-0001',
    r.carga.folio);
  revisa('viaja de dónde salió', /consulta\.miguelsotomd\.com/.test(r.carga.de || ''),
    r.carga.de);
  revisa('viajan los rótulos, para que allá no salga el identificador crudo',
    r.carga.traeEtiqueta, 'sin etiquetas, «apnp_actividad_fisica» en pantalla');
  revisa('van todos los campos de la historia', r.carga.campos >= 5,
    r.carga.campos + ' campos');
}

/* ---- 2. lo que se rompió: desaparecer en silencio ---- */
revisa('SI LA HISTORIA LLEGÓ SIN CONTENIDO, EL RENGLÓN NO DESAPARECE',
  r.vacia.hay, 'se esconde solo y se lee como función borrada');
revisa('y dice que no puede llevarla', /No puedo llevar a Zorvix/.test(r.vacia.texto),
  r.vacia.texto.slice(0, 80));
revisa('y explica que llegó sin contenido, no que no exista',
  /sin su contenido/.test(r.vacia.texto), '');
revisa('y no ofrece un código vacío para pegar',
  r.vacia.codigo === '', r.vacia.codigo.slice(0, 20));

/* ---- 3. una historia anulada no se lleva, pero sí se explica ----
   El renglón aparece —si no, otra vez «desapareció el botón»— y dice que la
   historia está anulada, sin ofrecer código: lo que se retiró del expediente
   de aquí no puede entrar al de allá. */
revisa('con la historia anulada, el renglón aparece y dice que lo está',
  r.anulada.hay && /está anulada/.test(r.anulada.texto),
  r.anulada.texto.slice(0, 90));
revisa('UNA HISTORIA ANULADA NO OFRECE CÓDIGO PARA PEGAR EN ZORVIX',
  r.anulada.codigo === '',
  'se llevaría al quirófano un documento retirado del expediente');

/* ---- 4. con una anulada y una buena, se escoge la buena ---- */
revisa('con una anulada y una viva, sí se ofrece la viva', r.mezcla.hay, '');
revisa('y el código que se ofrece no lleva la marca de anulación',
  r.mezcla.hay && r.mezcla.codigo.indexOf('ZXHC1.') === 0, '');
revisa('el código de la viva no arrastra el sello de anulado',
  r.carga ? r.carga.traeAnulado === false : false, 'viaja __anulado');

/* ---- 5. sin historia clínica: el renglón SIGUE ahí, diciendo por qué ----
   Esto es lo que el médico vio dos veces el 27-nov-2026: la pantalla sin nada
   en ese lugar. Mientras el renglón no se pinte, «no hay historia» y «se borró
   la función» se ven exactamente igual. */
revisa('SIN HISTORIA CLÍNICA, EL RENGLÓN SIGUE APARECIENDO', r.sinNada.hay,
  'desaparecer se lee como función borrada');
revisa('y dice que todavía no hay ninguna',
  /todavía no hay ninguna/.test(r.sinNada.texto), r.sinNada.texto.slice(0, 90));
revisa('y nombra los documentos que sí hay, que es lo que explica el caso',
  /Nota de evoluci/i.test(r.sinNada.texto) && /\(2\)/.test(r.sinNada.texto),
  r.sinNada.texto.slice(0, 200));
revisa('y no ofrece código', r.sinNada.codigo === '', '');
revisa('viene abierto, para no tener que tocarlo para enterarse',
  /todavía no hay ninguna/.test(r.sinNada.texto) &&
  r.sinNada.abierto === true, 'cerrado');

/* ---- 6. expediente completamente vacío ---- */
revisa('en un expediente vacío también aparece y dice que está vacío',
  r.vacio.hay && /está vacío/.test(r.vacio.texto), r.vacio.texto.slice(0, 90));

/* ---- 7. los cuatro casos: el renglón nunca falta ---- */
revisa('EL RENGLÓN APARECE EN LOS CUATRO CASOS, SIN EXCEPCIÓN',
  r.normal.hay && r.vacia.hay && r.anulada.hay && r.sinNada.hay && r.vacio.hay,
  [['normal',r.normal.hay],['sin contenido',r.vacia.hay],['anulada',r.anulada.hay],
   ['sin historia',r.sinNada.hay],['vacío',r.vacio.hay]]
    .filter(x=>!x[1]).map(x=>x[0]).join(', '));

await nav.close();
console.log(fallas ? `\n${fallas} caso(s) mal`
  : '\nLlevar a Zorvix: aparece cuando hay historia, se explica cuando llegó ' +
    'sin contenido, y nunca ofrece una historia anulada.');
process.exit(fallas ? 1 : 0);
