/* ============================================================
   PRUEBA PERMANENTE — NOTA MÉDICA DE TEXTO LIBRE

   El 28-nov-2026 una paciente pidió una nota para tramitar su licencia en el
   ISSSTE. En vez de un formulario por destinatario, el médico pidió un solo
   documento: datos del establecimiento y texto libre.

   Un documento así es cómodo y por eso mismo es el más delicado del
   expediente: es el único donde el contenido no lo decide la aplicación. Lo
   que esta prueba defiende:

     · QUE NO SE IMPRIMA EN BLANCO. Una hoja con membrete y firma auténticos
       y sin texto es una hoja en blanco firmada. Es el peor papel que puede
       salir de un consultorio y no depende de la buena fe de nadie: el
       candado tiene que estar en el código.
     · QUE EL PAPEL IDENTIFIQUE A LA PACIENTE. Nombre, expediente y fecha
       salen del expediente, no se teclean. Una nota para una institución sin
       a quién se refiere no sirve.
     · QUE EL TÍTULO SEA EL ASUNTO, no «NOTA MÉDICA» nueve veces.
     · QUE LOS PÁRRAFOS SOBREVIVAN. Un resumen clínico dictado en párrafos
       que se imprime como un bloque corrido no lo lee nadie.
     · QUE NO SE CUELE NINGÚN OTRO CAMPO. El documento imprime lo suyo y
       nada más: el día que alguien agregue un campo al esquema, no puede
       aparecer solo en un papel que va al ISSSTE.

   Uso: node prueba_nota_libre.mjs [index.html]
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

/* ---- el esquema ---- */
const porId = {}; esquema.campos.forEach(c => porId[c.id] = c);
['nota_asunto', 'nota_texto'].forEach(id =>
  revisa('el campo ' + id + ' existe en el esquema', !!porId[id],
    'el documento lo declara y la app lo omitiría sin avisar'));
revisa('el texto de la nota se captura como párrafo, no como renglón',
  porId['nota_texto'] && porId['nota_texto'].control === 'parrafo',
  porId['nota_texto'] && porId['nota_texto'].control);
revisa('ninguno de los dos es obligatorio en el esquema',
  ['nota_asunto','nota_texto'].every(id => porId[id] && !porId[id].obligatorio),
  'el aviso de la NOM-004 es para las notas clínicas');
revisa('la nota no captura ningún dato de identificación de la paciente',
  !esquema.campos.some(c => c.grupo === 'Nota médica' &&
    /^paciente_/.test(c.id)), 'saldrían tecleados de memoria');

const CUERPO = [
  'Por medio de la presente hago constar que la paciente fue intervenida ' +
  'quirúrgicamente el 20 de noviembre de 2026.',
  'Diagnóstico: lipodistrofia abdominal.\nProcedimiento: abdominoplastia.',
  'Se recomienda reposo laboral por 21 días, del 20 de noviembre al 11 de ' +
  'diciembre de 2026.'
].join('\n\n');

const nav = await chromium.launch();
const pag = await nav.newPage({ viewport: { width: 816, height: 1056 } });
await pag.route('**/*', (r) =>
  r.request().url().startsWith('file://') ? r.continue() : r.abort());
await pag.goto('file://' + HTML);

const r = await pag.evaluate(async ({ esquema, constantes, CUERPO }) => {
  const out = {};
  ESQUEMA = esquema; CONSTANTES = constantes;
  FOLIO = 'P-0142'; DOC_ID = 'ffff'; CORREO = 'x@y.mx'; PENDIENTE_DICTADO = {};
  PACIENTE = { Paciente:'María Prueba López', Paciente_ID:'P-0142' };

  const T = DOCUMENTOS.filter(d => d.id === 'nota_libre')[0];
  out.existe = !!T;
  if (!T) return out;
  out.dicta   = T.dictado === true;
  out.grupo   = T.grupo;
  out.campos  = (T.campos || []).join(',');
  out.avisaISSSTE = /ISSSTE/.test(T.aviso || '') && /resumen clínico/i.test(T.aviso || '');
  out.avisaNOM = /padecimiento actual/i.test(T.aviso || '') &&
                 /pron[óo]stico/i.test(T.aviso || '');

  TIPO = T;
  VALORES = { expediente_folio:'P-0142', paciente_nombres:'María',
              paciente_apellido_paterno:'Prueba', paciente_apellido_materno:'López',
              paciente_sexo:'Femenino', paciente_edad:'38',
              doc_fecha:'2026-11-28',
              nota_asunto:'Resumen clínico', nota_texto:CUERPO };
  out.folio = folioDocumento();
  out.titulo = T.tituloImpreso();

  armaImpresion();
  const raiz = document.getElementById('impresion');
  out.papel = raiz.innerText;
  out.h1 = (raiz.querySelector('h1') || {}).textContent;
  out.parrafos = raiz.querySelectorAll('.parrafoLibre').length;
  out.saltos = raiz.querySelectorAll('.parrafoLibre br').length;
  /* ningún otro campo del esquema se coló */
  out.datos = raiz.querySelectorAll('.dato').length;

  /* sin asunto, el título cae en algo legible */
  VALORES['nota_asunto'] = '';
  out.tituloSinAsunto = T.tituloImpreso();
  return out;
}, { esquema, constantes, CUERPO });

revisa('la nota médica existe como documento del expediente', r.existe, '');

if (r.existe){
  revisa('se puede dictar, que es como él la va a escribir', r.dicta, '');
  revisa('declara sus dos campos y nada más',
    r.campos === 'nota_asunto,nota_texto', r.campos);
  revisa('su folio lleva su propia abreviatura', /-NOTLIB-/.test(r.folio || ''),
    r.folio);

  revisa('avisa en pantalla que la licencia la expide la institución, no él',
    r.avisaISSSTE, 'sin eso, la nota sale creyendo que es una incapacidad');
  revisa('y recuerda el contenido mínimo que pide la NOM-004', r.avisaNOM, '');

  revisa('EL TÍTULO IMPRESO ES EL ASUNTO, no «Nota médica»',
    r.h1 === 'RESUMEN CLÍNICO', r.h1);
  revisa('sin asunto no se queda sin título', r.tituloSinAsunto === 'Nota médica',
    r.tituloSinAsunto);

  revisa('el papel identifica a la paciente', /María Prueba López/.test(r.papel), '');
  revisa('y trae su número de expediente', /P-0142/.test(r.papel), '');
  revisa('y la fecha', /2026|noviembre/i.test(r.papel), '');

  revisa('LOS PÁRRAFOS SE RESPETAN AL IMPRIMIR', r.parrafos === 3,
    r.parrafos + ' párrafos en vez de 3');
  revisa('y dentro de un párrafo, los renglones sueltos también',
    r.saltos === 1, r.saltos + ' saltos de renglón');
  revisa('el texto completo salió impreso',
    /abdominoplastia/.test(r.papel) && /21 días/.test(r.papel), '');
  revisa('NINGÚN OTRO CAMPO DEL ESQUEMA SE COLÓ EN EL PAPEL', r.datos === 0,
    r.datos + ' campos automáticos impresos');
  revisa('la hoja se firma a mano, como todas las de este expediente',
    /[Ff]irma aut[óo]grafa/.test(r.papel), '');
}

/* ---- el candado: no se imprime en blanco ---- */
for (const caso of [
  { nombre:'sin texto',  v:{ nota_asunto:'Resumen clínico', nota_texto:'' },
    espera:'el texto' },
  { nombre:'sin asunto', v:{ nota_asunto:'', nota_texto:'algo escrito' },
    espera:'el asunto' },
  { nombre:'completamente en blanco', v:{ nota_asunto:'', nota_texto:'' },
    espera:'el asunto y el texto' }
]){
  const res = await pag.evaluate(({ v }) => {
    /* Se oprime el botón de verdad: el candado vive en su manejador, y una
       prueba que llamara a la función de armado por dentro se saltaría justo
       lo que hay que defender. */
    window.print = function(){ window.__imprimio = (window.__imprimio || 0) + 1; };
    window.__imprimio = 0;
    TIPO = DOCUMENTOS.filter(d => d.id === 'nota_libre')[0];
    VALORES = Object.assign({ expediente_folio:'P-0142',
      paciente_nombres:'María', paciente_apellido_paterno:'Prueba',
      doc_fecha:'2026-11-28' }, v);
    document.getElementById('impresion').innerHTML = '';
    document.getElementById('bImprimir').click();
    return { estado: document.getElementById('estado').textContent,
             aviso: document.getElementById('avisoPrefill').textContent,
             mando: window.__imprimio,
             papel: document.getElementById('impresion').innerHTML.length };
  }, { v: caso.v });
  revisa('NO IMPRIME UNA NOTA ' + caso.nombre.toUpperCase(),
    res.mando === 0 && res.papel === 0 && /No se imprime/.test(res.estado),
    res.estado || 'se mandó a la impresora');
  revisa('y dice que falta ' + caso.espera,
    res.estado.indexOf(caso.espera) >= 0, res.estado);
}

await nav.close();
console.log(fallas ? `\n${fallas} caso(s) mal`
  : '\nNota libre: no sale en blanco, el título es el asunto, los párrafos ' +
    'se respetan y no se cuela ningún otro campo.');
process.exit(fallas ? 1 : 0);
