/* ============================================================
   PRUEBA PERMANENTE — ¿QUÉ CAMPOS CAPTURADOS LLEGAN AL PAPEL?

   El médico reportó: «capturamos las historias clínicas completas y cuando
   las imprimimos no salen completas». Esta prueba no opina: llena TODOS los
   campos que le tocan a un documento con una marca única por campo
   (VAL-<id>), manda imprimir, y revisa marca por marca si apareció en la
   hoja. Lo que no aparece, se perdió.

   Corre sin red y sin Google: se carga index.html desde el disco y se le
   inyectan ESQUEMA, CONSTANTES y VALORES a mano. Las funciones de impresión
   son declaraciones de función del script principal, así que existen aunque
   el arranque falle por no tener red.

   Uso:  node prueba_impresion_campos.mjs [ruta/index.html] [ruta/campos.json]
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


const HTML    = resolve(process.argv[2] || 'index.html');
const CAMPOS  = process.argv[3] ? resolve(process.argv[3]) : null;

/* Los documentos que se revisan y el sexo con el que se revisan. El sexo
   importa: los gineco-obstétricos no le tocan a un hombre. */
/* Campos que a propósito no salen como campo, porque ya están en el papel de
   otra forma. No son pérdidas y la prueba no los cuenta como tales:
     doc_tipo         -> es el título de la hoja (h1)
     doc_folio        -> se imprime al pie, armado por folioDocumento()
     doc_version      -> control interno, no se le entrega a nadie
     doc_estado_firma -> la hoja SIEMPRE sale sin firmar; la firma es autógrafa
     estab_propietario-> el membrete lleva nombre, tipo, domicilio y licencia
                         del establecimiento, y la firma lleva al médico con
                         sus dos cédulas; el propietario es la misma persona
     paciente_telefono-> en los documentos que no son historia clínica ni hoja
                         frontal la identificación no se repite en el cuerpo
   Si algo se agrega a esta lista, tiene que venir con su razón escrita. */
const A_PROPOSITO = {
  '*':                ['doc_tipo','doc_folio','doc_version','doc_estado_firma',
                       'estab_propietario'],
  nota_evolucion:     ['paciente_telefono']
};

const CASOS = [
  { tipo: 'historia_clinica', sexo: 'Femenino' },
  { tipo: 'hoja_frontal',     sexo: 'Femenino' },
  { tipo: 'nota_evolucion',   sexo: 'Femenino' }
];

const esquema = JSON.parse(CAMPOS ? readFileSync(CAMPOS, 'utf8') : dondeEste('campos.json'));

const navegador = await chromium.launch();
const pagina = await navegador.newPage();
/* Nada de red: ni Google, ni el Apps Script. La prueba es del papel. */
await pagina.route('**/*', (ruta) =>
  ruta.request().url().startsWith('file://') ? ruta.continue() : ruta.abort());
await pagina.goto('file://' + HTML);

let fallas = 0;

for (const caso of CASOS){
  const r = await pagina.evaluate(({ esquema, tipo, sexo }) => {
    ESQUEMA = esquema;
    TIPO = DOCUMENTOS.filter(function(d){ return d.id === tipo; })[0];
    if (!TIPO) return { error: 'no existe el documento ' + tipo };

    /* Constantes del consultorio: cualquier texto sirve, lo que se mide es
       si el campo llega al papel. */
    CONSTANTES = {};
    ESQUEMA.campos.forEach(function(c){
      if (['Médico','Establecimiento','Seguimiento'].indexOf(c.grupo) >= 0)
        CONSTANTES[c.id] = 'VAL-' + c.id;
    });

    VALORES = {};
    PENDIENTE_DICTADO = {};
    FOLIO = 'P-PRUEBA'; DOC_ID = 'ffff'; CORREO = 'prueba@ejemplo.mx';

    /* Una marca única por campo. Las listas y las fechas también: a la
       impresión le da igual, imprime texto. */
    var suyos = camposDe(TIPO).filter(function(c){ return c.control !== 'automatico'; });
    suyos.forEach(function(c){ VALORES[c.id] = 'VAL-' + c.id; });
    /* La marca del sexo tiene que seguir leyéndose como el sexo que se está
       probando: de eso depende si los gineco-obstétricos entran o no. */
    VALORES['paciente_sexo'] = (sexo === 'Masculino' ? 'VAL-masculino' : 'VAL-femenino');

    armaImpresion();
    /* En minúsculas: la receta imprime la vía «en minúsculas» a propósito
       («, vía oral»), y la marca no se perdió, sólo cambió de caja. */
    var papel = document.getElementById('impresion').innerText.toLowerCase();

    return {
      papel: papel,
      campos: suyos.filter(function(c){ return c.id !== 'paciente_sexo'; }).map(function(c){
        return { id: c.id, grupo: c.grupo, etiqueta: c.etiqueta || c.id,
                 sale: papel.indexOf(('VAL-' + c.id).toLowerCase()) >= 0 };
      })
    };
  }, { esquema, tipo: caso.tipo, sexo: caso.sexo });

  if (r.error){ console.log('✗ ' + r.error); fallas++; continue; }

  const perdonados = (A_PROPOSITO['*'] || []).concat(A_PROPOSITO[caso.tipo] || []);
  const perdidos = r.campos.filter((c) => !c.sale && !perdonados.includes(c.id));
  const marca = perdidos.length ? '✗' : '✓';
  console.log(`\n${marca} ${caso.tipo} — ${r.campos.length} campos capturados, ` +
              `${r.campos.filter((c) => c.sale).length} impresos, ` +
              `${perdonados.length} fuera a propósito, ${perdidos.length} perdidos`);
  for (const c of perdidos) console.log(`    ${c.grupo} | ${c.id} | ${c.etiqueta}`);
  if (process.env.DETALLE) for (const c of r.campos.filter((x)=>x.grupo===process.env.DETALLE))
    console.log(`    ${c.sale ? 'sale' : 'NO SALE'}  ${c.id}`);
  if (perdidos.length) fallas++;
}

await navegador.close();
process.exit(fallas ? 1 : 0);
