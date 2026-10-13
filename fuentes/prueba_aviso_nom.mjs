/* ============================================================
   PRUEBA PERMANENTE — EL AVISO DE LO QUE FALTA ANTES DE IMPRIMIR

   Un campo vacío no deja hueco en la hoja: desaparece, y el documento sale
   pareciendo completo. Esta prueba comprueba que, antes de mandar a la
   impresora, el sistema diga en grande qué datos obligatorios de la NOM le
   faltan a la historia clínica —en particular el interrogatorio por aparatos
   y sistemas, que es lo que se perdió sin aviso.

   Uso: node prueba_aviso_nom.mjs [index.html] [campos.json]
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


const HTML   = resolve(process.argv[2] || 'index.html');
const CAMPOS = process.argv[3] ? resolve(process.argv[3]) : null;
const esquema = JSON.parse(CAMPOS ? readFileSync(CAMPOS, 'utf8') : dondeEste('campos.json'));

const navegador = await chromium.launch();
const pagina = await navegador.newPage();
await pagina.route('**/*', (r) =>
  r.request().url().startsWith('file://') ? r.continue() : r.abort());
await pagina.goto('file://' + HTML);

const r = await pagina.evaluate(({ esquema }) => {
  ESQUEMA = esquema;
  TIPO = DOCUMENTOS.filter(function (d) { return d.id === 'historia_clinica'; })[0];
  CONSTANTES = {}; VALORES = { paciente_sexo: 'Femenino' }; PENDIENTE_DICTADO = {};

  var vacia = faltantesNOM().map(function (c) { return c.id; });

  /* Ahora se llena todo MENOS el interrogatorio: es el caso real que se
     reportó —la historia se ve completa y sale sin él—. */
  camposDe(TIPO).forEach(function (c) {
    if (c.control === 'automatico') return;
    if (c.grupo === 'Interrogatorio por aparatos y sistemas') return;
    VALORES[c.id] = 'x';
  });
  var casi = faltantesNOM().map(function (c) { return c.id; });
  var agrupado = faltantesPorGrupo_(faltantesNOM());

  /* Y con el interrogatorio puesto, ya no debe faltar nada. */
  camposDe(TIPO).forEach(function (c) {
    if (c.grupo === 'Interrogatorio por aparatos y sistemas') VALORES[c.id] = 'Sdp';
  });
  var lleno = faltantesNOM().map(function (c) { return c.id; });

  return { vacia: vacia, casi: casi, agrupado: agrupado, lleno: lleno };
}, { esquema });

const AP = ['ap_cardiovascular','ap_respiratorio','ap_digestivo',
            'ap_urinario','ap_nervioso','ap_piel_anexos'];
let fallas = 0;
function revisa(nombre, bien, detalle){
  console.log((bien ? '✓ ' : '✗ ') + nombre + (bien ? '' : '  → ' + detalle));
  if (!bien) fallas++;
}

revisa('con la historia en blanco, el aviso incluye los 6 del interrogatorio',
  AP.every((id) => r.vacia.includes(id)), r.vacia.join(', '));
revisa('con todo lleno menos el interrogatorio, faltan exactamente esos 6',
  r.casi.length === 6 && AP.every((id) => r.casi.includes(id)), r.casi.join(', '));
revisa('el aviso nombra el grupo, no sólo un número',
  r.agrupado.length === 1 &&
  r.agrupado[0].startsWith('Interrogatorio por aparatos y sistemas: '),
  JSON.stringify(r.agrupado));
revisa('con el interrogatorio capturado ya no falta nada',
  r.lleno.length === 0, r.lleno.join(', '));

await navegador.close();
process.exit(fallas ? 1 : 0);
