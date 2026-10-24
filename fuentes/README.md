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
python3 fuentes/construir_indicaciones.py     # las 8 hojas originales
python3 fuentes/construir_recetas.py          # las 4 plantillas originales

python3 fuentes/corregir_drenajes.py
python3 fuentes/corregir_dieta_submandibular.py
python3 fuentes/corregir_a_donde_llamar.py
python3 fuentes/agregar_antiviral_preop.py
python3 fuentes/corregir_medicamentos_preop.py
python3 fuentes/construir_hoja_combinada.py
python3 fuentes/construir_receta_combinada.py
python3 fuentes/construir_eco2.py
python3 fuentes/agregar_prednisona.py
python3 fuentes/construir_receta_mastopexia.py
python3 fuentes/construir_hoja_deep_co2.py
python3 fuentes/construir_receta_deep_co2.py
python3 fuentes/construir_hoja_otoplastia.py
python3 fuentes/construir_receta_otoplastia.py
python3 fuentes/agregar_amlodipino_recetas.py
python3 fuentes/corregir_usted_preop.py
```

Ya no hay ningún `cp` en la cadena: las dos mitades arrancan de un constructor
en Python, no de un respaldo. Los `_base.json` se quedan sólo como testigo de
que el constructor reproduce lo que había.

**El orden importa.** Los constructores copian renglones ya aprobados de las
hojas y plantillas anteriores —por índice o por nombre, nunca retecleados—, así
que si corre uno antes de tiempo copia una versión vieja. `construir_eco2.py`
copia de la hoja combinada; `construir_receta_mastopexia.py` copia de la receta
de Deep Plane **ya con la prednisona dentro**; `agregar_amlodipino_recetas.py`
va hasta el final porque necesita que existan las siete plantillas.

Los scripts son idempotentes en el sentido útil: si el cambio ya está hecho, se
niegan a duplicarlo y lo dicen. No son acumulativos: siempre se arranca de los
dos constructores.

Al terminar, los dos archivos de la raíz deben quedar con el **mismo contenido**
que los publicados —mismo catálogo, mismas versiones de hoja—. Si no quedan,
algo cambió y hay que averiguar qué antes de subir nada.

Hoy la cadena produce: indicaciones `44db91ce85e20d32` (12 hojas) y recetas
`cf84ba3e3846028b` (9 plantillas).

**Corra la cadena completa, siempre.** Si se salta un paso, el catálogo que
suba no trae esa corrección y el texto viejo vuelve a producción sin que nadie
lo note. Ya pasó una vez, con `corregir_usted_preop.py`: una reconstrucción que
lo omitió devolvió al sitio dos títulos escritos de tú. El catálogo de arriba
es la manera de darse cuenta: si lo que reconstruyó no da esa versión, le falta
un paso o le sobra un cambio.

## Los archivos

### El punto de partida

`construir_indicaciones.py` tiene el texto de las **ocho hojas originales**
—Deep Plane, lipoescultura, mastopexia, rinoplastia, blefaroplastia, faja,
preoperatorias y laboratorios— escrito como código, con un ayudante por tipo de
bloque (`h`, `h2`, `p`, `ul`, `tabla`, `citas`, `nota`, `firmas`).
`construir_recetas.py` hace lo mismo con las **cuatro plantillas originales**
—Deep Plane, Body360, blefaroplastia y rinoplastia—, con un ayudante `med()`
por renglón de medicamento y un `al()` por signo de alarma. **Ésos son los dos
archivos que se editan cuando hay que corregir algo original.**

Ninguno se transcribió a mano. Los emitieron `generar_constructor.py` y
`generar_constructor_recetas.py` leyendo los respaldos, y en los dos casos se
comprobó que lo que producen tiene exactamente el mismo contenido y las mismas
versiones que el original. Se corrieron una vez y se guardan sólo como prueba
de procedencia; no se vuelven a correr.

Que el texto se **emita** y no se teclee no es un lujo de programador: son 51
renglones de medicamento con sus dosis y sus condiciones, y una tarde de
transcripción es una tarde de oportunidades de convertir un «cada 8 horas» en
un «cada 12» sin que nadie lo note.

| archivo | qué es |
|---|---|
| `construir_indicaciones.py` | las 8 hojas originales, editables · catálogo `e9cd69b0cedb662c` |
| `construir_recetas.py` | las 4 plantillas originales, editables · catálogo `d52a8784e7313b41` |
| `indicaciones_base.json` | el JSON del que se emitió el primero, como testigo. No se toca |
| `recetas_base.json` | el JSON del que se emitió el segundo, como testigo. No se toca |
| `generar_constructor.py` | emitió `construir_indicaciones.py`. Ya corrió |
| `generar_constructor_recetas.py` | emitió `construir_recetas.py`. Ya corrió |

Una advertencia que importa: el original de las indicaciones tenía el orden de
llaves inconsistente —en unos bloques de alarma `alarma` iba antes de `x` y en
otros después—. El constructor lo normaliza. El contenido y todas las versiones
son idénticos; lo único que cambia es el orden en que se escriben catorce
bloques, cosa que el sistema no mira porque lee JSON, no bytes.

### Correctores — arreglan texto que ya estaba y estaba mal

| script | qué corrige |
|---|---|
| `corregir_drenajes.py` | los drenajes salen por gasto y características, no a las 24 h |
| `corregir_dieta_submandibular.py` | la dieta es de glándula submandibular, y se dice así |
| `corregir_a_donde_llamar.py` | la paciente llama al consultorio, nunca a urgencias de otro hospital |
| `agregar_antiviral_preop.py` | el antiviral del láser se avisa en la hoja preoperatoria, que es cuando da tiempo de comprarlo |
| `corregir_medicamentos_preop.py` | **la hoja decía que el consultorio entrega los medicamentos. Es falso**: entrega recetas, y la paciente compra |
| `agregar_prednisona.py` | prednisona 20 mg × 14 días, que no estaba en ninguna plantilla |
| `agregar_amlodipino_recetas.py` | el amlodipino de la víspera, que se indicaba de palabra y no estaba impreso en ninguna receta |
| `corregir_usted_preop.py` | dos títulos de la hoja preoperatoria que se habían quedado de tú. Va al final, después de todo lo que toca esa hoja |

Los correctores existen porque antes no había constructor: eran la única forma
de dejar rastro de un cambio. Ahora que los dos constructores existen, una
corrección NUEVA a una hoja o plantilla original se hace allí directamente, no
con un corrector más. Los que están aquí se quedan porque la cadena ya depende
de ellos y porque cada uno explica una decisión clínica que conviene no perder.

Dos de ellos van juntos y no se pueden separar: la hoja preoperatoria dejó de
decir «si su cirugía lleva incisión» —la paciente no tiene por qué clasificar
su propia cirugía— y ahora dice «si en sus recetas viene amlodipino, tómelo».
Eso vuelve a la receta la única fuente de verdad, así que
`agregar_amlodipino_recetas.py` tiene que correr siempre que corra
`corregir_medicamentos_preop.py`. Si el amlodipino no está impreso en la
receta, nadie lo toma.

### Constructores — crean hojas y plantillas nuevas

| script | qué construye |
|---|---|
| `construir_hoja_combinada.py` | hoja de Deep Plane de cuello + blefaroplastia + rinoplastia + CO₂ |
| `construir_receta_combinada.py` | la receta de esa misma combinación |
| `construir_eco2.py` | hoja y receta del láser eCO₂ por separado |
| `construir_receta_mastopexia.py` | la receta de mastopexia |
| `construir_hoja_deep_co2.py` | hoja de Deep Plane Facelift **completo** + láser CO₂ |
| `construir_receta_deep_co2.py` | la receta de esa misma combinación |
| `construir_hoja_otoplastia.py` | hoja de otoplastia — la única que no sale de fusionar otras |
| `construir_receta_otoplastia.py` | la receta de otoplastia, el esqueleto del lifting sin Bichat ni blefaro |

Los dos últimos van **antes** de `agregar_amlodipino_recetas.py`, para que el
amlodipino de la víspera les entre solo con todas las demás, y **después** de
`agregar_prednisona.py`, porque la receta copia la prednisona del lifting en
vez de traer la suya: ésa es justamente la razón de que existan. Imprimir
sueltas la receta del Deep Plane y la del láser le daba a la paciente 40 mg
diarios de prednisona durante catorce días.

No confunda esta combinación con `facial_combinada`, que es Deep Plane **de
cuello**: aquélla no lleva malla hemostática ni puntos delante de la oreja, y
entregarla a una paciente de lifting completo le quita dos citas.

La otoplastia es el caso distinto: no se parece a ninguna hoja anterior, así
que buena parte hubo que escribirla. Su constructor dice arriba, en tres
listas, qué está **copiado** de la hoja del lifting, qué **confirmó el
médico** el 24-oct-2026 (vendaje, banda, puntos al día 10, alberca y deporte)
y qué está **escrito ahí y pendiente de revisión** —`←NUEVO` para el texto
clínico nuevo, `←CONFIRMAR` para los cinco plazos que propuse yo—. Mientras
esas marcas sigan en el archivo, la hoja no está revisada del todo.

### La solicitud de laboratorios, como PDF fijo

`generar_laboratorios_pdf.mjs` produce `laboratorios.pdf`, que se publica en la
raíz del sitio. Es el único documento que no depende de la paciente: los mismos
siete estudios para todas. Se manda por WhatsApp pegando la liga
`consulta.miguelsotomd.com/laboratorios.pdf`, sin abrir el expediente.

El texto no está escrito ahí: sale de la hoja `laboratorios` de
`indicaciones.json`, armada por el propio `index.html`, de modo que el PDF
hereda el membrete y los estilos reales. Lo que el script hace encima es
quitarle la ficha de la paciente —un PDF para todas no puede traer el nombre de
una—, cambiar el cuadro de firma autógrafa por la firma visual, y quitarle el
folio de documento, que no existe sin expediente. Al pie queda la versión de la
hoja, que es como se sabe después qué texto exacto se mandó.

```bash
node fuentes/generar_laboratorios_pdf.mjs index.html indicaciones.json laboratorios.pdf
```

Se vuelve a correr cada vez que cambie la hoja de laboratorios. El script
revisa lo que produjo —que quepa en una página, que estén los diez renglones de
la hoja, que no haya quedado ningún hueco por llenar a mano, que vaya firmado—
y truena si algo falta.

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
| `prueba_aviso_preop.mjs` | que la nota preoperatoria recuerde entregar las recetas, nombrando las dos que no admiten retraso, y que ese recordatorio no aparezca en los demás documentos ni bloquee nada |

`render_hoja.mjs`, `render_receta.mjs` y `render_impresion.mjs` son auxiliares:
imprimen un documento a PDF para verlo.

Las pruebas necesitan `campos.json` —está en la raíz del repositorio— y
opcionalmente `constantes.json`, que **no está aquí a propósito**: vive en la
carpeta `esquema` de Drive, la sirve el gateway, y trae cédulas y teléfonos que
no tienen por qué estar en un repositorio público. Sin él las pruebas corren
igual, con el membrete vacío. `generar_laboratorios_pdf.mjs` sí lo necesita de
verdad: sin firma en las constantes se niega a producir el PDF.

## Dos documentos que son dos a propósito

La **orden de internamiento** va a la unidad quirúrgica y lleva todo lo
clínico. La **constancia de acompañante** va al patrón de quien acompaña a
la paciente, y no lleva nada: ni diagnóstico, ni procedimiento, ni
antecedentes. Un patrón no tiene por qué enterarse de qué cirugía se hizo la
madre de su empleada para justificarle el día.

El candado no es la buena intención de quien edite el archivo: la constancia
trae su **propia función de impresión**, así que sólo sale lo que está escrito
ahí dentro. Un campo nuevo que alguien agregue mañana al expediente no se
cuela, porque el cuerpo automático —el que recorre todos los campos con
valor— ni siquiera corre para este documento.

Esa fue la segunda versión del candado. La primera declaraba la lista de campos
vacía, y resultó peor que inútil: impedía también capturar el nombre y la fecha
que la constancia necesita, así que el documento salía sin decir a quién ampara
ni de qué día. El candado correcto limita lo que se **imprime**, no lo que se
puede escribir.

## Reglas que conviene no romper

1. **Copiar, no reteclear.** Si un renglón ya existe aprobado en otra hoja, se
   copia por índice o por nombre. Así una corrección se propaga sola.
2. **Lo que no dijo el médico va marcado.** Cualquier número que haya puesto
   quien escribió el script y no el médico lleva `←CONFIRMAR` en el código y se
   nombra al entregarlo. Nunca se inventa en silencio —ni en el texto, ni en el
   comentario que lo explica.
3. **Lo nuevo va marcado.** El contenido clínico escrito desde cero —signos de
   alarma, sobre todo— lleva `←NUEVO` para que se revise renglón por renglón.
4. **El texto que imprime la paciente no lleva instrucciones para el médico.**
   Esas van en los avisos, que son de pantalla.
5. **Un documento no imprime lo que su lector no debe ver.** Si una hoja va a
   manos de un tercero, el candado es su propia función de impresión, no el
   cuidado de quien la edita.
6. **A la paciente no se le pide que clasifique su caso.** No «si su cirugía
   lleva incisión», sino «si en sus recetas viene». Lo que decide es un dato que
   ella tiene en la mano, no un juicio clínico.
7. **La hoja no promete lo que el consultorio no hace.** Se entregan recetas, no
   medicamentos. Una frase amable y falsa le cuesta a la paciente su primera
   noche sin analgésico.
8. **Versión por contenido.** La versión de cada hoja y de cada catálogo es un
   hash de su propio contenido. Dos reconstrucciones del mismo material dan la
   misma versión; si la versión cambió, el contenido cambió.
