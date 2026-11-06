/* ============================================================
   PRUEBA PERMANENTE — LA PREGUNTA DEL TUBO

   El 1-nov-2026 el médico pidió agregar a sus hojas la molestia de garganta
   por la intubación, y al plantearlo lo corrigió él mismo:

     «al igual que las recetas con antibiótico, todas deberíamos de preguntar
      antes de desplegar las recomendaciones postoperatorias si fue con tubo
      o sin tubo. Las recomendaciones preoperatorias sí deberán ser genéricas
      pero las postoperatorias no»

   Eso convirtió a las hojas de indicaciones en algo que antes no eran: un
   texto que depende de una respuesta. Lo que esta prueba defiende:

     · una hoja con la pregunta sin contestar NO se imprime, y lo dice
     · contestando «no», el bloque de garganta no aparece en el papel
     · contestando «sí», aparece completo y la respuesta queda impresa en el
       pie, porque la versión de la hoja ya no alcanza para saber qué se
       entregó
     · la receta trae el spray sólo cuando hubo tubo
     · la hoja y la receta imprimen la MISMA dosis
     · en las tres hojas con dieta de la glándula submandibular el texto NO
       ofrece caramelos, que esa misma hoja prohíbe 14 días
     · la hoja preoperatoria lo dice siempre, sin preguntar nada

   Uso: node prueba_garganta.mjs [index.html]
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
const catIND  = JSON.parse(dondeEste('indicaciones.json'));
const catRX   = JSON.parse(dondeEste('recetas.json'));
let constantes = JSON.parse(dondeEste('constantes.json'));
if (constantes.campos) constantes = constantes.campos;

let fallas = 0;
function revisa(nombre, bien, detalle){
  console.log((bien ? '✓ ' : '✗ ') + nombre + (bien ? '' : '   → ' + (detalle || '')));
  if (!bien) fallas++;
}

/* ---------- 1. El catálogo, sin navegador ---------- */
const POSTOP = ['deep_plane','lipoescultura','ribxcar','mastopexia',
                'rinoplastia','blefaroplastia','facial_combinada',
                'deep_plane_co2','eco2','morpheus8','otoplastia'];
const SUBMAND = ['deep_plane','deep_plane_co2','facial_combinada'];
const RECETA_DE = { deep_plane:'deep_plane', lipoescultura:'body360',
  ribxcar:'ribxcar', morpheus8:'morpheus8',
  mastopexia:'mastopexia', rinoplastia:'rinoplastia',
  blefaroplastia:'blefaroplastia', facial_combinada:'facial_combinada',
  deep_plane_co2:'deep_plane_co2', eco2:'eco2', otoplastia:'otoplastia' };

const H = {}; catIND.hojas.forEach(h => H[h.id] = h);
const P = {}; catRX.plantillas.forEach(p => P[p.id] = p);

POSTOP.forEach(function(hid){
  const h = H[hid];
  const preg = (h.preguntas || []).filter(q => q.id === 'tubo');
  revisa(hid + ': tiene la pregunta del tubo, obligatoria',
    preg.length === 1 && preg[0].obligatoria === true && preg[0].enPie === true,
    JSON.stringify(preg));

  const cond = (h.bloques || []).filter(b => b.si && b.si.tubo === true);
  revisa(hid + ': el bloque de garganta va condicionado',
    cond.length === 4, cond.length + ' bloques con si.tubo');

  const texto = JSON.stringify(cond);
  const ofrece = /chupar caramelos o pastillas para la garganta/.test(texto);
  const prohibe = /NO chupe caramelos/.test(texto);
  if (SUBMAND.indexOf(hid) >= 0){
    revisa(hid + ': con dieta submandibular NO ofrece caramelos',
      prohibe && !ofrece, 'ofrece=' + ofrece + ' prohibe=' + prohibe);
  } else {
    revisa(hid + ': sin dieta submandibular sí puede chupar caramelos',
      ofrece && !prohibe, 'ofrece=' + ofrece + ' prohibe=' + prohibe);
  }

  /* Que el bloque esté DENTRO de «lo que es normal» y no después de los
     signos de alarma: una molestia normal impresa debajo de la lista de
     urgencias se lee como una urgencia más. */
  const iAlarma = (h.bloques || []).findIndex(
    b => b.t === 'h' && /Signos de alarma/i.test(String(b.x || '')));
  const iGarganta = (h.bloques || []).findIndex(
    b => b.si && b.si.tubo === true);
  revisa(hid + ': el bloque va antes de los signos de alarma',
    iGarganta >= 0 && iAlarma >= 0 && iGarganta < iAlarma,
    'garganta=' + iGarganta + ' alarma=' + iAlarma);

  /* La hoja promete un spray; la receta de la MISMA cirugía tiene que
     llevarlo, y con la misma dosis. */
  const spray = (P[RECETA_DE[hid]].medicamentos || [])
    .filter(m => m.si && m.si.tubo === true);
  revisa(hid + ': su receta (' + RECETA_DE[hid] + ') lleva el spray condicionado',
    spray.length === 1, spray.length + ' renglones');
  revisa(hid + ': la hoja y la receta dicen la misma dosis',
    /4 atomizaciones/.test(texto) &&
    spray.length === 1 && /4 atomizaciones/.test(spray[0].indicacion), '');
  revisa(hid + ': el spray va en el pliego que la paciente conserva',
    spray.length === 1 && spray[0].hoja === 'general',
    spray.length === 1 ? spray[0].hoja : '');

  /* Lo que el médico dijo que NO va en papel de paciente. */
  const todo = JSON.stringify(h);
  revisa(hid + ': no se colló el protocolo de anestesia',
    !/presión del globo|cmH₂O|cmH2O|i-gel|taponamiento faríngeo|extubaci/i.test(todo),
    'hay texto de protocolo interno');

  /* Y que no se rebaje el plazo del alcohol ni del tabaco por la garganta. */
  revisa(hid + ': el bloque no vuelve a permitir alcohol ni tabaco',
    !/evite (el )?alcohol, (el )?tabaco/i.test(texto) &&
    /ya están suspendidos por su cirugía/.test(texto), '');
});

const pre = H['preoperatorias'];
revisa('la preoperatoria NO pregunta nada',
  !(pre.preguntas || []).length, JSON.stringify(pre.preguntas));
revisa('la preoperatoria trae la sección de garganta, sin condición',
  (pre.bloques || []).some(b => b.t === 'h' && /garganta/i.test(String(b.x || ''))) &&
  !(pre.bloques || []).some(b => b.si), '');
revisa('la preoperatoria conserva las 4 semanas de nicotina',
  /suspéndalos 4 semanas antes y 4 semanas después/.test(JSON.stringify(pre)) &&
  !/cigarro al menos 2 semanas/.test(JSON.stringify(pre)), '');
revisa('la preoperatoria distingue el dolor de garganta de ANTES',
  /ése sí hay que avisarnos/.test(JSON.stringify(pre)), '');
revisa('las hojas que no son de alta se quedan sin pregunta',
  !['faja','laboratorios'].some(id => (H[id].preguntas || []).length), '');

/* ---------- 2. El comportamiento, en el navegador ---------- */
const nav = await chromium.launch();
const pag = await nav.newPage({ viewport: { width: 420, height: 900 } });
await pag.route('**/*', (r) =>
  r.request().url().startsWith('file://') ? r.continue() : r.abort());
await pag.goto('file://' + HTML);

const r = await pag.evaluate(async ({ esquema, constantes, catIND }) => {
  const out = {};
  const espera = (ms) => new Promise(s => setTimeout(s, ms));
  window.fetch = function(url){
    if (String(url).indexOf('indicaciones.json') >= 0){
      return Promise.resolve({ ok: true, json: () => Promise.resolve(catIND) });
    }
    return Promise.resolve({ text: () => Promise.resolve(
      JSON.stringify({ doc_id: 'DOC-X', guardado: '01/11/2026 10:00' })) });
  };
  window.print = function(){ window.__imprimio = (window.__imprimio || 0) + 1; };

  ESQUEMA = esquema; CONSTANTES = constantes; CRED = 'x'; CORREO = 'x@y.mx';
  PACIENTE = { 'Paciente': 'María Prueba', 'Paciente_ID': 'P-001', 'Edad': '50' };
  FOLIO = 'P-001'; COMO_SE_IDENTIFICO = 'por su número';
  EXPEDIENTE = { paciente: PACIENTE, documentos: [] };
  VALORES = {}; DOC_ID = '';
  TIPO = DOCUMENTOS.filter(t => t.hoja)[0];
  VALORES['proc_fecha'] = '2026-10-28';

  armaHoja();
  await espera(60);

  const sel = document.querySelector('[data-campo="indicaciones_hoja"]');
  sel.value = 'deep_plane';
  sel.dispatchEvent(new Event('change', { bubbles: true }));
  await espera(40);

  out.hayPregunta = !!document.querySelector('[data-campo="ind_tubo"]');
  out.arrancaVacia = document.querySelector('[data-campo="ind_tubo"]').value === '';
  out.estadoSinContestar = document.getElementById('estado').textContent;
  out.progresoSinContestar = document.getElementById('progreso').style.width;
  out.resumenSinContestar = document.querySelector('#formulario .aviso').textContent.slice(0, 160);

  /* No debe imprimir mientras no esté contestada. */
  window.__imprimio = 0;
  document.getElementById('bImprimir').click();
  await espera(400);
  out.imprimioSinContestar = window.__imprimio;
  out.avisoSinContestar = document.getElementById('avisoPrefill').innerText.slice(0, 120);
  out.claseAvisoSinContestar = document.getElementById('avisoPrefill').className;

  /* Contestada «no»: el bloque no sale. */
  const q = document.querySelector('[data-campo="ind_tubo"]');
  q.value = 'no'; q.dispatchEvent(new Event('change', { bubbles: true }));
  await espera(40);
  out.estadoCon_no = document.getElementById('estado').textContent;
  out.progresoCon_no = document.getElementById('progreso').style.width;
  armaImpresion();
  const papel = () => document.getElementById('impresion').innerText;
  out.papelCon_no = /Molestia de garganta/.test(papel());
  out.pieCon_no = (papel().match(/sin vía aérea instrumentada/) || []).length;

  /* Contestada «sí»: sale completo y queda en el pie. */
  q.value = 'si'; q.dispatchEvent(new Event('change', { bubbles: true }));
  await espera(40);
  armaImpresion();
  const t = papel();
  out.papelCon_si = /Molestia de garganta/.test(t);
  out.dosisEnPapel = /4 atomizaciones/.test(t);
  out.avisoRonquera = /ronquera dura más de 3 días/.test(t);
  out.ruidoAlRespirar = /ruido\s+agudo al respirar/.test(t);
  out.pieCon_si = /anestesia general con vía aérea instrumentada/.test(t);
  out.caramelosProhibidos = /NO chupe caramelos/.test(t);
  out.caramelosOfrecidos = /chupar caramelos o pastillas/.test(t);
  out.dietaSigueAhi = /chicles y caramelos/.test(t);

  /* Y que de verdad imprima ya contestada. */
  window.__imprimio = 0;
  document.getElementById('bImprimir').click();
  await espera(600);
  out.imprimioContestada = window.__imprimio;

  /* En una hoja sin preguntas nada de esto estorba. */
  sel.value = 'faja'; sel.dispatchEvent(new Event('change', { bubbles: true }));
  await espera(40);
  out.fajaSinPregunta = !document.querySelector('[data-campo="ind_tubo"]');
  out.fajaProgreso = document.getElementById('progreso').style.width;

  return out;
}, { esquema, constantes, catIND });

revisa('la hoja muestra la pregunta del tubo', r.hayPregunta, '');
revisa('la pregunta arranca sin contestar', r.arrancaVacia, '');
revisa('sin contestar, el estado lo dice',
  /Falta contestar/.test(r.estadoSinContestar), r.estadoSinContestar);
revisa('sin contestar, la hoja no se marca lista',
  r.progresoSinContestar === '0%', r.progresoSinContestar);
revisa('sin contestar, el resumen explica por qué no se imprime',
  /No se imprime todavía/.test(r.resumenSinContestar), r.resumenSinContestar);
revisa('sin contestar, NO imprime',
  r.imprimioSinContestar === 0, 'imprimió ' + r.imprimioSinContestar + ' veces');
revisa('sin contestar, el aviso sale arriba y en rojo',
  /No imprimí la hoja/.test(r.avisoSinContestar) && /malo/.test(r.claseAvisoSinContestar),
  r.claseAvisoSinContestar + ' · ' + r.avisoSinContestar);

revisa('contestada «no», la hoja queda lista',
  r.progresoCon_no === '100%' && /lista para imprimir/.test(r.estadoCon_no),
  r.progresoCon_no + ' · ' + r.estadoCon_no);
revisa('contestada «no», el bloque de garganta NO sale en el papel',
  r.papelCon_no === false, 'salió');
revisa('contestada «no», el pie lo deja asentado',
  r.pieCon_no === 1, r.pieCon_no + ' menciones en el pie');

revisa('contestada «sí», el bloque sale en el papel', r.papelCon_si, '');
revisa('contestada «sí», sale la dosis', r.dosisEnPapel, '');
revisa('contestada «sí», sale cuándo avisar por ronquera', r.avisoRonquera, '');
revisa('contestada «sí», el ruido al respirar va aparte y es urgente',
  r.ruidoAlRespirar, '');
revisa('contestada «sí», el pie dice que hubo vía aérea instrumentada',
  r.pieCon_si, '');
revisa('en Deep Plane el papel prohíbe los caramelos y no los ofrece',
  r.caramelosProhibidos && !r.caramelosOfrecidos,
  'prohibe=' + r.caramelosProhibidos + ' ofrece=' + r.caramelosOfrecidos);
revisa('y la dieta submandibular sigue impresa en la misma hoja',
  r.dietaSigueAhi, '');
revisa('contestada, sí imprime',
  r.imprimioContestada === 1, 'imprimió ' + r.imprimioContestada + ' veces');

revisa('una hoja sin preguntas no muestra ninguna', r.fajaSinPregunta, '');
revisa('una hoja sin preguntas sigue lista en cuanto se escoge',
  r.fajaProgreso === '100%', r.fajaProgreso);

await nav.close();
console.log(fallas ? `\n${fallas} caso(s) mal`
  : '\nLa hoja pregunta antes de imprimir, y lo que sale en el papel es lo que se contestó.');
process.exit(fallas ? 1 : 0);
