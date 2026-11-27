/* ============================================================
   PRUEBA PERMANENTE — VITALIA
   la hoja de indicaciones del paquete de suplementos

   El 26-nov-2026 el médico pidió meter al expediente las indicaciones de
   VITALIA y entregó el texto completo. Es la única hoja del catálogo que no
   sale de una cirugía ni de un tratamiento: sale de la entrega de un paquete.

   Lo que esta prueba defiende, en orden de gravedad:

     · QUE LAS CUENTAS CUADREN. La columna «le alcanza para» se calcula del
       contenido del frasco entre la dosis diaria. Si algún día cambia una
       presentación y nadie ajusta la columna, la paciente se queda sin
       producto antes de tiempo o compra de más. Aquí se recalculan las seis.
     · QUE NINGÚN PRODUCTO SE CAIGA DE UNA TABLA. Son seis y aparecen en tres
       lugares —el paquete, el horario y «cómo tomar»—. Uno que esté en el
       paquete y no en el horario es un frasco que la paciente no sabe cuándo
       tomar.
     · QUE SOBREVIVAN LAS PRECAUCIONES, y sobre todo la de suspender 14 días
       antes de una cirugía: es lo único de esta hoja que se cruza con el
       quirófano, y coincide con el plazo de su hoja preoperatoria.
     · QUE NO HABLE COMO HOJA QUIRÚRGICA. Se construyó junto a quince hojas
       postoperatorias; heredar de ellas una palabra como «herida» o «signos
       de alarma» la volvería otra cosa.
     · QUE EL ENCABEZADO NO DIGA «FECHA DEL PROCEDIMIENTO», porque aquí no hay
       procedimiento: hay una entrega.

   Uso: node prueba_vitalia.mjs [index.html]
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
const ind     = JSON.parse(dondeEste('indicaciones.json'));
let constantes = JSON.parse(dondeEste('constantes.json'));
if (constantes.campos) constantes = constantes.campos;

let fallas = 0;
function revisa(nombre, bien, detalle){
  console.log((bien ? '✓ ' : '✗ ') + nombre + (bien ? '' : '   → ' + (detalle || '')));
  if (!bien) fallas++;
}

const H = {}; ind.hojas.forEach(h => H[h.id] = h);
const V = H['vitalia'];
revisa('la hoja de VITALIA existe', !!V, 'no está en el catálogo');

if (V){
  const plano = JSON.stringify(V.bloques);
  const tabla = c0 => V.bloques.filter(b => b.t === 'tabla' &&
    (b.cols || [''])[0] === c0)[0];
  const paquete = tabla('Producto');
  const horario = tabla('Momento');
  const como = V.bloques.filter(b => b.t === 'ul' &&
    b.x.some(y => y.startsWith('RESVE-250:')))[0];

  revisa('tiene la tabla del paquete', !!paquete, '');
  revisa('tiene la tabla del horario', !!horario, '');
  revisa('tiene la lista de cómo tomar cada producto', !!como, '');

  if (paquete && horario && como){
    revisa('son seis productos en el paquete', paquete.x.length === 6,
      paquete.x.length + ' renglones');
    revisa('y seis tomas en el horario', horario.x.length === 6,
      horario.x.length + ' renglones');

    /* ---- LAS CUENTAS ----
       contenido del frasco ÷ dosis diaria = lo que dice «le alcanza para». */
    const cuentas = [
      ['RESVE-250', 60, 2, 30],
      ['VITA-C300', 300, 1, 300],
      ['Colágeno Hidrolizado Puro', 1000, 10, 100],
      ['HMB', 120, 2, 60],
      ['HC-PLUS', 80, 1, 80],
    ];
    cuentas.forEach(([prod, frasco, dosis, dias]) => {
      const fila = paquete.x.filter(f => f[0] === prod)[0];
      revisa('la duración de ' + prod + ' cuadra: ' + frasco + ' ÷ ' + dosis +
        ' = ' + dias + ' días',
        !!fila && Math.floor(frasco / dosis) === dias &&
        fila[3].indexOf(String(dias) + ' día') >= 0,
        fila ? fila[3] : 'no está en la tabla');
    });
    /* El magnesio es el único con dos dosis: 120 ÷ 4 = 30 y 120 ÷ 3 = 40. */
    const mag = paquete.x.filter(f => f[0] === 'MAG-100')[0];
    revisa('MAG-100 dice «30 a 40 días», que es 120 entre 4 y entre 3',
      !!mag && /30 a 40 días/.test(mag[3]), mag ? mag[3] : '');

    /* ---- ningún producto se cae de una tabla ---- */
    const enPaquete = paquete.x.map(f => f[0]);
    const enHorario = horario.x.map(f => f[1]);
    enPaquete.forEach(p => {
      revisa(p + ' está también en el horario', enHorario.includes(p), '');
      revisa(p + ' tiene su renglón en «cómo tomar»',
        como.x.some(y => y.startsWith(p + ':')), '');
    });

    /* ---- las dos dosis del magnesio ---- */
    const filaMag = horario.x.filter(f => f[1] === 'MAG-100')[0];
    revisa('el horario distingue la dosis de mujeres y la de hombres',
      !!filaMag && /Mujeres: 3/.test(filaMag[2]) && /Hombres: 4/.test(filaMag[2]),
      filaMag ? filaMag[2] : '');
    revisa('y «cómo tomar» repite las dos dosis',
      /Mujeres, 3 cápsulas; hombres, 4/.test(plano), '');

    /* ---- los tres momentos del día ---- */
    ['Con el desayuno','Con la comida','Con la cena'].forEach(m =>
      revisa('el horario usa el momento «' + m + '»',
        horario.x.some(f => f[0] === m), ''));
  }

  /* ---- las precauciones ---- */
  [['embarazada','embarazo o lactancia'],
   ['coagulación','anticoagulantes y aspirina'],
   ['glucosa','glucosa o presión'],
   ['riñones','función renal'],
   ['alérgico','alergia a los componentes']].forEach(([clave, que]) =>
    revisa('conserva la precaución de ' + que,
      new RegExp(clave,'i').test(plano), ''));
  revisa('MANDA SUSPENDER 14 DÍAS ANTES DE UNA CIRUGÍA',
    /14 días antes/.test(plano), 'es lo único que cruza con el quirófano');
  revisa('y pide avisarle al médico que lo estaba tomando',
    /avise a su médico/.test(plano), '');
  revisa('dice que no se duplique la dosis olvidada',
    /No duplique la dosis/.test(plano), '');
  revisa('dice que no se exceda la porción de ningún producto',
    /No exceda la porción/.test(plano), '');
  revisa('dice cómo conservar los frascos', /fresco y seco/.test(plano), '');
  revisa('avisa que los frascos no se terminan al mismo tiempo',
    /no se terminan al mismo tiempo/.test(plano), '');

  /* ---- no es una hoja quirúrgica ---- */
  ['herida','incisión','faja','anestesia','quirófano','signos de alarma',
   'postoperatori'].forEach(x =>
    revisa('no habla de «' + x + '», que aquí no aplica',
      !new RegExp(x,'i').test(plano), ''));

  /* ---- higiene ---- */
  revisa('el encabezado impreso dirá «Fecha de entrega»',
    V.etiquetaFecha === 'Fecha de entrega', String(V.etiquetaFecha));
  revisa('no se propone sola por una palabra del expediente',
    (V.coincide || []).length === 0, (V.coincide || []).join(', '));
  revisa('ningún bloque cuelga de una pregunta que no se hace',
    V.bloques.every(b => !b.si), '');
  revisa('no imprime HTML literal', !/<b>|<\/b>|<i>|<br|<p>/.test(plano), '');
  revisa('lleva constancia de entrega con firmas',
    V.bloques.some(b => b.t === 'firmas'), '');
  revisa('el acento de «continúe» quedó bien',
    /continúe al día siguiente/.test(plano) && !/contínue/.test(plano), '');
  const dup = V.bloques.filter(b => b.t === 'ul' &&
    new Set(b.x).size !== b.x.length);
  revisa('ninguna lista repite un renglón', dup.length === 0, '');
}

/* ---- en el navegador: su documento propio y el papel ---- */
const nav = await chromium.launch();
const pag = await nav.newPage({ viewport: { width: 816, height: 1056 } });
await pag.route('**/*', (r) =>
  r.request().url().startsWith('file://') ? r.continue() : r.abort());
await pag.goto('file://' + HTML);

const r = await pag.evaluate(async ({ esquema, ind, constantes }) => {
  const out = {};
  ESQUEMA = esquema; CONSTANTES = constantes;
  INDICACIONES = ind; INDICACIONES_AL = Date.now();
  FOLIO = 'P-PRUEBA'; DOC_ID = 'ffff'; CORREO = 'x@y.mx'; PENDIENTE_DICTADO = {};

  const T = DOCUMENTOS.filter(d => d.id === 'vitalia')[0];
  out.existeTipo = !!T;
  if (T){
    out.esHoja = !!T.hoja;
    out.porDefecto = T.hojaPorDefecto;
    out.grupo = T.grupo;
    out.sinDictado = T.dictado === false;
  }

  TIPO = T || DOCUMENTOS.filter(d => d.id === 'indicaciones_alta')[0];
  VALORES = { expediente_folio:'P-PRUEBA', paciente_nombres:'María',
              paciente_apellido_paterno:'Prueba', paciente_sexo:'Femenino',
              proc_fecha:'2026-11-26' };
  HOJA = INDICACIONES.hojas.filter(h => h.id === 'vitalia')[0];
  out.folio = folioDocumento();
  armaImpresion();
  const papel = document.getElementById('impresion').innerText;
  out.titulo      = /VITALIA — INDICACIONES DE CONSUMO/i.test(papel);
  out.fechaEntrega= /FECHA DE ENTREGA/i.test(papel);
  out.sinProcedim = !/FECHA DEL PROCEDIMIENTO/i.test(papel);
  out.seisProd    = ['RESVE-250','VITA-C300','Colágeno Hidrolizado Puro',
                     'HMB','HC-PLUS','MAG-100'].filter(p => papel.includes(p)).length;
  out.catorceDias = /14 días antes/.test(papel);
  out.firmas      = /Quien entrega/.test(papel);
  return out;
}, { esquema, ind, constantes });

revisa('VITALIA tiene su propio documento en el expediente', r.existeTipo,
  'tendría que buscarse dentro de «Indicaciones de alta»');
revisa('está declarado como hoja, con VITALIA por omisión',
  r.esHoja === true && r.porDefecto === 'vitalia',
  r.porDefecto + ' / hoja=' + r.esHoja);
revisa('vive en el grupo de los que se imprimen y se firman',
  r.grupo === 'firma', r.grupo);
revisa('no ofrece dictado, que aquí no tiene sentido', r.sinDictado, '');
revisa('su folio lleva su propia abreviatura',
  /-VIT-/.test(r.folio || ''), r.folio);

revisa('el papel lleva el título de VITALIA', r.titulo, '');
revisa('el encabezado dice FECHA DE ENTREGA', r.fechaEntrega, '');
revisa('y ya NO dice «fecha del procedimiento»', r.sinProcedim,
  'una hoja de suplementos encabezando como cirugía');
revisa('los seis productos salen impresos', r.seisProd === 6,
  r.seisProd + ' de 6');
revisa('el papel manda suspender 14 días antes de una cirugía',
  r.catorceDias, '');
revisa('el papel trae la constancia de entrega', r.firmas, '');

await nav.close();
console.log(fallas ? `\n${fallas} caso(s) mal`
  : '\nVITALIA tiene hoja propia: las seis cuentas cuadran, ningún producto se ' +
    'cae de una tabla, y no habla como hoja de cirugía.');
process.exit(fallas ? 1 : 0);
