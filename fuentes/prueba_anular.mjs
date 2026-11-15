/* ============================================================
   PRUEBA PERMANENTE — ANULAR UN DOCUMENTO

   El 15-nov-2026 el Dr. Soto rehízo la funcionalidad de notas del expediente
   de Zorvix y pidió replicarla aquí: «ya sólo existe la funcionalidad de
   guardar, anular e imprimir». Guardar e imprimir ya estaban; anular no.

   Lo que esta prueba defiende, en orden de gravedad:

     · QUE NO SE BORRE NADA. Anular marca el documento y lo deja en el
       expediente. Si algún día alguien cambia esto por un borrado, aquí se
       cae: el expediente clínico se conserva cinco años (NOM-004 5.4).
     · QUE NO SE PUEDA EDITAR UN ANULADO. Ni a mano, ni con el guardado
       automático, ni completándolo con datos de la base. Un anulado que se
       deja editar revive por la puerta de atrás y el archivo acaba diciendo
       una cosa y la hoja de papel otra.
     · QUE NO SE ANULE SIN MOTIVO. El motivo es lo único que va a quedar
       explicando el hueco; el botón no se enciende sin él.
     · QUE LA HOJA IMPRESA LO DIGA. Una hoja anulada sin sello se ve idéntica
       a una vigente y acaba archivada como si contara.
     · QUE EL ANULADO NO DESAPAREZCA DE LA LISTA, pero tampoco cuente: ni en
       el conteo, ni como «ya existe» en el mosaico.
     · QUE UN GUARDADO FALLIDO NO DEJE LA PANTALLA MINTIENDO.

   Uso: node prueba_anular.mjs [index.html]
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

/* ---- 1. el esquema: la opción «Anulado» tiene que existir ya ---- */
const campoEstado = esquema.campos.filter(c => c.id === 'doc_estado_firma')[0];
revisa('el esquema tiene doc_estado_firma', !!campoEstado, 'no está');
revisa('y trae «Anulado» entre sus opciones — no se inventó un campo nuevo',
  !!campoEstado && (campoEstado.opciones || []).indexOf('Anulado') >= 0,
  campoEstado ? (campoEstado.opciones || []).join(', ') : '');

/* ---- 2. el comportamiento, en el navegador ---- */
const nav = await chromium.launch();
const pag = await nav.newPage({ viewport: { width: 430, height: 940 } });
await pag.route('**/*', (r) =>
  r.request().url().startsWith('file://') ? r.continue() : r.abort());
await pag.goto('file://' + HTML);

const r = await pag.evaluate(async ({ esquema, constantes }) => {
  const out = {};
  const espera = (ms) => new Promise(s => setTimeout(s, ms));

  /* El gateway, de mentiras. Se apunta cada llamada para poder afirmar que
     anular guardó UNA vez y que después ya no se guarda nada. */
  window.__llamadas = [];
  window.__falla = false;
  window.fetch = function(url, opc){
    const cuerpo = JSON.parse(opc.body);
    window.__llamadas.push(cuerpo);
    if (window.__falla){
      return Promise.resolve({ text: () => Promise.resolve(
        JSON.stringify({ error: 'el servidor no quiso' })) });
    }
    return Promise.resolve({ text: () => Promise.resolve(
      JSON.stringify({ doc_id: 'DOC-1', guardado: '15/11/2026 10:00',
                       por: 'dr@soto.mx' })) });
  };
  window.print = function(){ window.__imprimio = (window.__imprimio || 0) + 1; };
  window.alert = function(){};

  ESQUEMA = esquema; CONSTANTES = constantes; CRED = 'x'; CORREO = 'dr@soto.mx';
  PACIENTE = { 'Paciente': 'María Prueba', 'Paciente_ID': 'P-001', 'Edad': '50' };
  FOLIO = 'P-001'; COMO_SE_IDENTIFICO = 'por su número';
  VALORES = {}; PENDIENTE_DICTADO = {}; SIN_CONTENIDO = false; sucio = false;

  TIPO = DOCUMENTOS.filter(d => d.id === 'nota_evolucion')[0] ||
         DOCUMENTOS.filter(d => d.grupo === 'captura')[0];
  out.tipoUsado = TIPO && TIPO.id;

  EXPEDIENTE = { paciente: PACIENTE, documentos: [] };

  /* ── sin guardar todavía: no hay nada que anular ───────────────────── */
  DOC_ID = '';
  arma(); pinta();
  await espera(40);
  out.ocultoSinGuardar = $('bAnular').classList.contains('oculto');
  $('bAnular').onclick();
  await espera(40);
  out.avisoSinGuardar = $('avisoPrefill').innerText.slice(0, 90);
  out.cuadroCerradoSinGuardar = $('capaAnular').classList.contains('oculto');

  /* ── el documento ya existe: el botón aparece ──────────────────────── */
  DOC_ID = 'DOC-1';
  VALORES['doc_estado_firma'] = 'Firmado';   /* salía firmado, a propósito */
  VALORES['paciente_nombres'] = 'María';
  VALORES['paciente_apellido_paterno'] = 'Prueba';
  pinta();
  await espera(40);
  out.visibleConDocId = !$('bAnular').classList.contains('oculto');
  out.habilitado = !$('bAnular').disabled;

  /* ── el cuadro: sin motivo no se puede anular ───────────────────────── */
  $('bAnular').onclick();
  await espera(60);
  out.cuadroAbierto = !$('capaAnular').classList.contains('oculto');
  out.apagadoSinMotivo = $('anuSi').disabled;
  out.diceQueNoBorra = /no se borra/i.test($('anuTexto').innerText);
  out.avisoFirmada =/ir por ella|expediente de papel/i.test($('anuTexto').innerText);
  out.pistaDiceMinimo = /10 caracteres/.test($('anuPista').innerText);

  $('anuMotivo').value = 'se cayo';            /* 7 caracteres */
  $('anuMotivo').oninput();
  out.apagadoConMotivoCorto = $('anuSi').disabled;
  out.diceCuantoFalta = /Faltan 3 caracteres/.test($('anuInfo').innerText);

  $('anuMotivo').value = 'capturada en la paciente equivocada';
  $('anuMotivo').oninput();
  out.encendidoConMotivo = !$('anuSi').disabled;

  /* ── el guardado falla: la marca se retira ──────────────────────────── */
  window.__falla = true;
  const antesFalla = window.__llamadas.length;
  $('anuSi').onclick();
  await espera(400);
  window.__falla = false;
  out.trasFallaEstado = VALORES['doc_estado_firma'];
  out.trasFallaSinMarca = !VALORES['__anulado'];
  out.trasFallaGuardarVivo = !$('bGuardar').disabled;
  out.trasFallaIntento = window.__llamadas.length - antesFalla;
  out.trasFallaDice = $('anuInfo').innerText;

  /* ── ahora sí ───────────────────────────────────────────────────────── */
  const antes = window.__llamadas.length;
  $('anuSi').onclick();
  await espera(500);
  out.llamadasDeAnular = window.__llamadas.length - antes;
  const mandado = window.__llamadas[window.__llamadas.length - 1] || {};
  out.accionMandada = mandado.accion;
  out.campoMandado = mandado.campos && mandado.campos['doc_estado_firma'];
  out.marcaMandada = mandado.campos && mandado.campos['__anulado'];
  /* El contenido del documento viaja íntegro: anular no lo vacía. */
  out.contenidoConservado = !!(mandado.campos &&
    mandado.campos['paciente_nombres'] === 'María');

  out.cuadroCerrado = $('capaAnular').classList.contains('oculto');
  out.estadoFinal = VALORES['doc_estado_firma'];
  out.marca = VALORES['__anulado'];
  out.avisoFinal = $('avisoPrefill').innerText.slice(0, 200);

  /* ── los candados ───────────────────────────────────────────────────── */
  pinta();
  await espera(40);
  out.guardarApagado  = $('bGuardar').disabled;
  out.dictarApagado   = $('bDictar').disabled;
  out.firmarApagado   = $('chkFirmar').disabled;
  out.anularApagado   = $('bAnular').disabled;
  out.anularDiceYa    = /Ya está anulado/.test($('bAnular').title || '');

  /* guardar a mano ya no manda nada */
  const antesG = window.__llamadas.length;
  sucio = true;
  await guarda(false);
  out.guardarNoMando = window.__llamadas.length === antesG;
  out.selloDiceAnulado = /[Aa]nulado/.test($('selloGuardado').innerText);

  /* ── el papel ───────────────────────────────────────────────────────── */
  armaImpresion();
  const papel = $('impresion').innerText;
  out.papelSello  = /DOCUMENTO ANULADO/.test(papel);
  out.papelSinValor = /no tiene valor/i.test(papel);
  out.papelMotivo = /capturada en la paciente equivocada/.test(papel);
  out.papelQuien  = /dr@soto\.mx/.test(papel);
  out.papelSelloPrimero = /^\s*DOCUMENTO ANULADO/.test(papel);

  /* ── la lista del expediente ────────────────────────────────────────── */
  EXPEDIENTE.documentos = [
    { id:'DOC-1', tipo: TIPO.id, fecha:'2026-11-15',
      campos: { doc_estado_firma:'Anulado',
                __anulado:{ motivo:'capturada en la paciente equivocada',
                            por:'dr@soto.mx', cuando:'2026-11-15 10:00',
                            estaba:'Firmado' } } },
    { id:'DOC-2', tipo: TIPO.id, fecha:'2026-11-14', campos: { paciente_nombres:'María' } }
  ];
  pintaDocumentos();
  await espera(60);
  const lista = $('yaHechos').innerText;
  out.listaTieneSeccion = /Anulados \(1\)/.test(lista);
  out.listaExplica = /No cuentan como parte del expediente/.test(lista);
  out.listaMuestraMotivo = /capturada en la paciente equivocada/.test(lista);
  out.filasAnuladas = document.querySelectorAll('#yaHechos .hecho-fila.anulada').length;
  out.filasVivas = document.querySelectorAll('#yaHechos .hecho-fila:not(.anulada)').length;
  /* El anulado se puede abrir para leerlo: si no, no hay cómo auditar. */
  out.anuladaSeAbre = !!(document.querySelectorAll('#yaHechos .hecho-fila.anulada')[0] || {}).onclick;
  out.fichaCuenta = $('fichaPac').innerText;

  /* el mosaico no cuenta el anulado */
  const recuadros = [...document.querySelectorAll('#mosCaptura .ficha, #mosFirmar .ficha')];
  const mio = recuadros.filter(b => (b.querySelector('.n') || {}).textContent === TIPO.nombre)[0];
  out.mosaicoDice = mio ? (mio.querySelector('.c') || {}).textContent : '(no encontré el recuadro)';

  /* ── un documento que llegó vacío no se anula ───────────────────────── */
  VALORES = {}; SIN_CONTENIDO = true; DOC_ID = 'DOC-9';
  pinta();
  const antesV = window.__llamadas.length;
  $('bAnular').onclick();
  await espera(60);
  out.vacioNoAbrio = $('capaAnular').classList.contains('oculto');
  out.vacioNoMando = window.__llamadas.length === antesV;
  out.vacioDice = $('avisoPrefill').innerText.slice(0, 110);

  return out;
}, { esquema, constantes });

console.log('\n(documento usado para la prueba: ' + r.tipoUsado + ')\n');

revisa('sin guardar, el botón de anular no se ve', r.ocultoSinGuardar, '');
revisa('y si se fuerza, explica que no hay nada que anular todavía',
  /nada que anular/i.test(r.avisoSinGuardar || '') && r.cuadroCerradoSinGuardar,
  r.avisoSinGuardar);

revisa('con el documento ya guardado, el botón aparece y se puede tocar',
  r.visibleConDocId && r.habilitado, '');

revisa('el cuadro se abre', r.cuadroAbierto, '');
revisa('y dice, antes de nada, que el documento NO se borra', r.diceQueNoBorra, '');
revisa('avisa que una hoja ya firmada hay que ir a buscarla al papel',
  r.avisoFirmada, '');
revisa('la pista dice el mínimo del motivo', r.pistaDiceMinimo, '');
revisa('sin motivo no se puede anular', r.apagadoSinMotivo, '');
revisa('con un motivo demasiado corto tampoco', r.apagadoConMotivoCorto, '');
revisa('y dice cuántos caracteres faltan', r.diceCuantoFalta, '');
revisa('con motivo suficiente, se enciende', r.encendidoConMotivo, '');

revisa('si el guardado falla, la marca de anulado se RETIRA de la pantalla',
  r.trasFallaEstado === 'Firmado' && r.trasFallaSinMarca,
  'quedó en ' + r.trasFallaEstado);
revisa('y la pantalla vuelve a dejar guardar', r.trasFallaGuardarVivo, '');
revisa('y lo dice en el cuadro, sin cerrarlo',
  /No se anuló/.test(r.trasFallaDice || ''), r.trasFallaDice);

revisa('anular guarda exactamente una vez', r.llamadasDeAnular === 1,
  r.llamadasDeAnular + ' llamadas');
revisa('y lo hace por la vía que ya existía, documentoGuardar',
  r.accionMandada === 'documentoGuardar', r.accionMandada);
revisa('lo que se manda al gateway es doc_estado_firma = Anulado',
  r.campoMandado === 'Anulado', String(r.campoMandado));
revisa('con el motivo, quién y cuándo',
  !!r.marcaMandada && r.marcaMandada.motivo === 'capturada en la paciente equivocada' &&
  r.marcaMandada.por === 'dr@soto.mx' && !!r.marcaMandada.cuando,
  JSON.stringify(r.marcaMandada));
revisa('y recuerda que SALÍA FIRMADO, para poder decir que hay que ir por la hoja',
  !!r.marcaMandada && r.marcaMandada.estaba === 'Firmado',
  r.marcaMandada && r.marcaMandada.estaba);
revisa('ANULAR NO BORRA: el contenido del documento viaja íntegro',
  r.contenidoConservado, 'se perdieron los campos del documento');

revisa('el cuadro se cierra al terminar', r.cuadroCerrado, '');
revisa('y el aviso de arriba dice el motivo y la fecha',
  /ANULADO/.test(r.avisoFinal || '') &&
  /capturada en la paciente equivocada/.test(r.avisoFinal || ''), r.avisoFinal);

revisa('un anulado NO se puede guardar', r.guardarApagado && r.guardarNoMando,
  'el botón quedó ' + (r.guardarApagado ? 'apagado' : 'vivo') +
  ' y ' + (r.guardarNoMando ? 'no mandó' : 'MANDÓ al gateway'));
revisa('y el sello lo dice en vez de quedarse callado', r.selloDiceAnulado, '');
revisa('un anulado no se dicta', r.dictarApagado, '');
revisa('un anulado no se firma', r.firmarApagado, '');
revisa('un anulado no se vuelve a anular',
  r.anularApagado && r.anularDiceYa, '');

revisa('la hoja impresa lleva el sello DOCUMENTO ANULADO', r.papelSello, '');
revisa('y el sello va arriba de todo, antes del membrete', r.papelSelloPrimero, '');
revisa('la hoja dice que no tiene valor', r.papelSinValor, '');
revisa('la hoja dice el motivo', r.papelMotivo, '');
revisa('la hoja dice quién lo anuló', r.papelQuien, '');

revisa('en la lista, los anulados bajan a su propia sección contada',
  r.listaTieneSeccion, '');
revisa('la sección explica qué significa', r.listaExplica, '');
revisa('cada anulado muestra su motivo en el renglón', r.listaMuestraMotivo, '');
revisa('hay un renglón anulado y uno vivo, y el anulado NO desapareció',
  r.filasAnuladas === 1 && r.filasVivas === 1,
  r.filasAnuladas + ' anulados, ' + r.filasVivas + ' vivos');
revisa('un anulado se puede abrir para leerlo', r.anuladaSeAbre, '');
revisa('la ficha de la paciente cuenta 1 documento y 1 anulado, por separado',
  /1 documento/.test(r.fichaCuenta || '') && /1 anulado/.test(r.fichaCuenta || ''),
  (r.fichaCuenta || '').replace(/\n/g, ' | '));
revisa('el mosaico NO ofrece abrir el anulado como si estuviera hecho',
  !/ya existe/.test(r.mosaicoDice || ''), r.mosaicoDice);

revisa('un documento que llegó sin contenido no se puede anular',
  r.vacioNoAbrio && r.vacioNoMando, '');
revisa('y dice por qué', /llegó sin su contenido/.test(r.vacioDice || ''), r.vacioDice);

await nav.close();
console.log(fallas ? `\n${fallas} caso(s) mal`
  : '\nAnular retira el documento del expediente vivo sin borrarlo, con motivo, ' +
    'y lo deja ilegible como documento válido en pantalla y en papel.');
process.exit(fallas ? 1 : 0);
