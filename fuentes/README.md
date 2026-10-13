# Fuentes — de dónde salen `indicaciones.json` y `recetas.json`

Esta carpeta **no la usa el sitio**. El sistema lee `indicaciones.json` y
`recetas.json` de la raíz del repositorio y nada más. Lo que hay aquí es el
material con el que esos dos archivos se construyen, para que una corrección
futura no tenga que hacerse a mano sobre miles de líneas de JSON.

## Por qué existe

Las hojas de recomendaciones y las recetas se editaron durante un tiempo
directamente sobre el JSON. Eso funciona una vez. A la tercera corrección ya
nadie sabe por qué un renglón dice lo que dice, y una frase que vive en dos
hojas se corrige en una y se olvida en la otra —ya pasó, con la regla de los
aretes y con el texto de a dónde llamar.

Aquí cada cambio es un script con nombre, con su explicación arriba de por qué
se hizo, y con una afirmación que falla ruidosamente si el texto que esperaba
encontrar ya no está. Los catálogos se **regeneran**, no se parchan.

## Cómo reconstruir todo, desde cero

```bash
python3 fuentes/construir_indicaciones.py      # las 8 hojas originales, desde su fuente
cp fuentes/recetas_base.json recetas.json      # las recetas todavía parten del respaldo

python3 fuentes/corregir_drenajes.py
python3 fuentes/corregir_dieta_submandibular.py
python3 fuentes/corregir_a_donde_llamar.py
python3 fuentes/agregar_antiviral_preop.py
python3 fuentes/construir_hoja_combinada.py
python3 fuentes/construir_receta_combinada.py
python3 fuentes/construir_eco2.py
python3 fuentes/agregar_prednisona.py
python3 fuentes/construir_receta_mastopexia.py
```

**El orden importa.** Los constructores copian renglones ya aprobados de las
hojas y plantillas anteriores —por índice o por nombre, nunca retecleados—, así
que si corre uno antes de tiempo copia una versión vieja. `construir_eco2.py`
copia de la hoja combinada; `construir_receta_mastopexia.py` copia de la receta
de Deep Plane **ya con la prednisona dentro**.

Los scripts son idempotentes en el sentido útil: si el cambio ya está hecho, se
niegan a duplicarlo y lo dicen. No son acumulativos: siempre se arranca de los
dos `_base.json`.

Al terminar, los dos archivos de la raíz deben quedar **byte por byte** iguales
a los publicados. Si no quedan, algo cambió y hay que averiguar qué antes de
subir nada.

## Los archivos

### El punto de partida

`construir_indicaciones.py` tiene el texto de las **ocho hojas originales**
—Deep Plane, lipoescultura, mastopexia, rinoplastia, blefaroplastia, faja,
preoperatorias y laboratorios— escrito como código, con un ayudante por tipo de
bloque (`h`, `h2`, `p`, `ul`, `tabla`, `citas`, `nota`, `firmas`). **Ése es el
archivo que se edita cuando hay que corregir una hoja original.**

No se transcribió a mano: lo emitió `generar_constructor.py` leyendo
`indicaciones_base.json`, y se comprobó que lo que produce tiene exactamente el
mismo contenido y las mismas ocho versiones que el original. `generar_constructor.py`
se corrió una vez y se guarda sólo como prueba de procedencia; no se vuelve a correr.

| archivo | qué es |
|---|---|
| `construir_indicaciones.py` | las 8 hojas originales, editables · catálogo `e9cd69b0cedb662c` |
| `indicaciones_base.json` | el JSON del que se emitió, como testigo. No se toca |
| `recetas_base.json` | 4 plantillas · catálogo `d52a8784e7313b41`. Todavía sin constructor |

Una advertencia que importa: el original tenía el orden de llaves inconsistente
—en unos bloques de alarma `alarma` iba antes de `x` y en otros después—. El
constructor lo normaliza. El contenido, las ocho versiones de hoja y la versión
del catálogo son idénticos; lo único que cambia es el orden en que se escriben
catorce bloques, cosa que el sistema no mira porque lee JSON, no bytes.

Lo que falta para cerrar el círculo: un `construir_recetas.py` equivalente para
las cuatro plantillas originales. Mientras no exista, esa mitad arranca del
respaldo.

### Correctores — arreglan texto que ya estaba y estaba mal

| script | qué corrige |
|---|---|
| `corregir_drenajes.py` | los drenajes salen por gasto y características, no a las 24 h |
| `corregir_dieta_submandibular.py` | la dieta es de glándula submandibular, y se dice así |
| `corregir_a_donde_llamar.py` | la paciente llama al consultorio, nunca a urgencias de otro hospital |
| `agregar_antiviral_preop.py` | el antiviral del láser se avisa en la hoja preoperatoria, que es cuando da tiempo de comprarlo |
| `agregar_prednisona.py` | prednisona 20 mg × 14 días, que no estaba en ninguna plantilla |

Los correctores existen porque antes no había constructor: eran la única forma
de dejar rastro de un cambio. Ahora que `construir_indicaciones.py` existe, una
corrección NUEVA a una hoja original se hace allí directamente, no con un
corrector más. Los cinco que están aquí se quedan porque la cadena ya depende
de ellos y porque cada uno explica una decisión clínica que conviene no perder.

### Constructores — crean hojas y plantillas nuevas

| script | qué construye |
|---|---|
| `construir_hoja_combinada.py` | hoja de Deep Plane de cuello + blefaroplastia + rinoplastia + CO₂ |
| `construir_receta_combinada.py` | la receta de esa misma combinación |
| `construir_eco2.py` | hoja y receta del láser eCO₂ por separado |
| `construir_receta_mastopexia.py` | la receta de mastopexia |

### Pruebas

Corren con Node y Playwright. Imprimen a PDF de verdad y cuentan páginas
reales: medir alturas en pantalla miente, porque la columna de impresión es más
angosta que la ventana y el texto se acomoda distinto.

| prueba | qué defiende |
|---|---|
| `prueba_impresion_campos.mjs` | que ningún campo capturado se quede sin imprimir |
| `prueba_aviso_nom.mjs` | que el aviso de campos faltantes nombre los grupos de la NOM-004 |
| `prueba_recetas_paginas.mjs` | que cada pliego quepa en su hoja y lleve firma, en toda plantilla y todo escenario de alergia |
| `prueba_receta_consultorio.mjs` | que la receta de consultorio acepte varios medicamentos |
| `prueba_casilla_renglones.mjs` | que la casilla saque un renglón de la receta y que lo deseleccionado no resucite al recalcular |
| `prueba_firma_visual.mjs` | que la firma visual se estampe sólo cuando se enciende, y que un documento sin firmar siga diciendo «Firma autógrafa» |
| `prueba_internamiento.mjs` | **el candado de la constancia**: que la hoja que va a manos de un patrón no pueda imprimir el diagnóstico ni el procedimiento, con el expediente lleno |

`render_hoja.mjs`, `render_receta.mjs` y `render_impresion.mjs` son auxiliares:
imprimen un documento a PDF para verlo.

Las pruebas necesitan `campos.json` —está en la raíz del repositorio— y
opcionalmente `constantes.json`, que **no está aquí a propósito**: vive en la
carpeta `esquema` de Drive, la sirve el gateway, y trae cédulas y teléfonos que
no tienen por qué estar en un repositorio público. Sin él las pruebas corren
igual, con el membrete vacío.

## Dos documentos que son dos a propósito

La **orden de internamiento** va a la unidad quirúrgica y lleva todo lo
clínico. La **constancia de acompañante** va al patrón de quien acompaña a
la paciente, y no lleva nada: ni diagnóstico, ni procedimiento, ni
antecedentes. Un patrón no tiene por qué enterarse de qué cirugía se hizo la
madre de su empleada para justificarle el día.

El candado no es la buena intención de quien edite el archivo: la constancia
declara su lista de campos VACÍA, así que no puede imprimir un dato clínico
aunque el expediente lo tenga. `prueba_internamiento.mjs` lo verifica con un
expediente lleno a propósito, y truena si alguien le agrega campos.

## Reglas que conviene no romper

1. **Copiar, no reteclear.** Si un renglón ya existe aprobado en otra hoja, se
   copia por índice o por nombre. Así una corrección se propaga sola.
2. **Lo que no dijo el médico va marcado.** Cualquier número que haya puesto
   quien escribió el script y no el médico lleva `←CONFIRMAR` en el código y se
   nombra al entregarlo. Nunca se inventa en silencio.
3. **Lo nuevo va marcado.** El contenido clínico escrito desde cero —signos de
   alarma, sobre todo— lleva `←NUEVO` para que se revise renglón por renglón.
4. **El texto que imprime la paciente no lleva instrucciones para el médico.**
   Esas van en los avisos, que son de pantalla.
5. **Un documento no imprime lo que su lector no debe ver.** Si una hoja va a
   manos de un tercero, su lista de campos es el candado, no el cuidado de
   quien la edita.
6. **Versión por contenido.** La versión de cada hoja y de cada catálogo es un
   hash de su propio contenido. Dos reconstrucciones del mismo material dan la
   misma versión; si la versión cambió, el contenido cambió.
