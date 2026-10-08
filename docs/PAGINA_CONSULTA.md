# PÁGINA DE CONSULTA — Bogotá Sintética

**La página nueva del proyecto (D17): cualquiera le hace una pregunta de opinión a la población sintética y ve cómo respondería, en total, por grupos y, cuando hay con qué, por localidad. Todo rotulado como suposición.**

Proyecto: Bogotá Social Simulator
Versión: 0.3 (población 2022-2024, 30/09/2026; §5.5)
Fecha: 30 de septiembre de 2026
Código: `src/consulta/` (`motor.py`, `servidor.py`, `pagina.html`, `reformular.py`) · Pruebas: `tests/test_consulta.py` (8), `tests/test_reformular.py` (7)
Reemplaza, como cara del proyecto, al tablero de `src/viz/` (que se conserva, sin cambios)

---

## 1. Cómo se abre

Es un **servidor local**, no un HTML suelto: la página llama a un modelo de lenguaje y la
clave de OpenRouter no puede viajar al navegador. Solo escucha en `127.0.0.1`.

```
.\venv\Scripts\Activate.ps1
$env:OPENROUTER_API_KEY = Read-Host "Clave de OpenRouter"
python src/consulta/servidor.py              # http://127.0.0.1:8765
python src/consulta/servidor.py --simulado   # sin clave ni gasto, para mirar la página
```

Necesita la población EPC 2022-2024 construida (`python src/population/poblacion_epc_olas.py`,
que a su vez usa `poblacion_epc.py` y la armonización) y el microdato de la EPC en su ruta
(`BSS_EPC_DIR`). *Hasta el 30/09 usaba la población 2023; ver §5.5.*

**Gasto:** una pregunta del catálogo cuesta una llamada (la reformulación, unos USD 0,003);
una nueva, dos (reformulación y puente, unos USD 0,006). ~~Más la estimación con Sonnet (~USD 0,024).~~ Más la
estimación con GPT-6 Luna (~USD 0,0012, §5.17): ~~una nueva cuesta en total unos USD 0,009~~. Desde el 6/10 todo va con
Luna (§5.18): una del catálogo cuesta ~USD 0,0009 y una nueva ~USD 0,003. Las respuestas se guardan en
`data/processed/consulta/cache.json`, que no se sube: repetir una pregunta no cuesta.

---

## 2. Qué tiene la página

1. **Portada:** qué es («¿Qué opinaría Bogotá si…?»), tres cifras (20.000 personas
   sintéticas, 1.501 encuestados reales, 19 localidades) y el aviso de que es un
   experimento, no una encuesta ni una predicción.
2. **Cómo funciona:** cuatro pasos ilustrados y los tres tipos de pregunta (ya medida,
   nueva, fuera de alcance), con un ejemplo de cada una.
3. **Pregúntale a Bogotá:** el campo de la pregunta con ejemplos; la sugerencia de
   reformulación (editable); el resultado; y el mapa grande al lado.
4. **Qué hay detrás:** la población, el puente y los límites.

**Lo que ya no está:** los botones de capas (opinión, población, crecimiento, voto) y la
línea de tiempo del tablero. El mapa muestra por defecto **información general**: adultos
por localidad (en color), estrato medio y cuántos encuestados de la EPC viven ahí.

---

## 3. Qué muestra cada tipo de respuesta

| Tipo | Resultado | Mapa |
|---|---|---|
| **Ya medida** (catálogo) | % en la mitad alta de la escala, la distribución completa y el mismo % por estrato, edad, sexo y educación | ~~Promedio por localidad en la escala completa~~ Cada localidad frente a la ciudad (por encima, sin diferencia clara o por debajo, según su margen del 95 %; §5.16, 5/10), con su promedio y margen en la tabla y la ficha |
| **Nueva** (puente) | Nivel de la ciudad propuesto por el modelo, **editable** con un deslizador; cuánto más o menos de acuerdo estaría cada grupo (en desviaciones estándar); las preguntas medidas en las que se apoya | **No se dibuja por localidad** (lectura B del puente), y la página dice por qué |
| **Fuera de alcance** | La razón, y una alternativa que, si se elige, vuelve a pasar por la reformulación (DI-CO4) | — |

En todas: una banda que dice que es una suposición, no una medición.

---

## 4. Decisiones (detalle en los docstrings)

- **DI-CO1:** el margen de una localidad es el de la encuesta (remuestreo de manzanas),
  no el de los 20.000 agentes.
- **DI-CO2:** una pregunta nueva no tiene mapa, y sus grupos van en desviaciones
  estándar, no en porcentajes: el puente ordena, no dice cuántos.
- **DI-CO3:** en la página el puente usa las 102 preguntas del catálogo.
- **DI-CO4:** una alternativa sugerida no se responde directo; se reformula.
- **DI-SE1 a DI-SE3:** solo localhost, sin librerías nuevas, cada consulta independiente.
- **La escala del mapa es la de la pregunta completa** (como DI-V34 del tablero), no la
  del mínimo al máximo observado.

---

## 5. Verificación (30/09/2026)

- `tests/test_consulta.py`, 8 pruebas con el modelo simulado: la respuesta del catálogo
  (distribución que suma 1, 19 localidades, cada media dentro de su margen, márgenes de
  más de 0,2 puntos), el «no sabe» fuera de la media, la pregunta nueva sin mapa y con
  grupos que promedian cero, un puente roto que se dice y no se responde, y el servidor
  con sus tres rutas, solo en `127.0.0.1` y sin los botones de antes.
- Revisada en el navegador en modo simulado: escritorio y celular (375 px, sin
  desplazamiento horizontal), claro y oscuro, los cuatro recorridos (catálogo, nueva,
  fuera de alcance con alternativa, respuesta inválida), sin errores en la consola.
- **No se ha abierto con el modelo real todavía.**

---

## 5.1 Rediseño con el sistema de Daniel (30/09/2026, v0.2)

Daniel entregó un `DESIGN.md` («bioluminescent control room»): oscuro, bicromático
(neutros casi negros + menta), titulares en peso 300 con tracking negativo, botones
siempre en píldora, tarjetas planas sin sombra, y un brillo verde radial solo detrás de la
«vitrina» (aquí, el espacio de preguntar). Se aplicó completo, con tres adaptaciones:

- **Tipografías:** Inter y JetBrains Mono, los sustitutos que nombra el propio documento
  (Euclid Circular A y Onsite SemiMono son de pago).
- **Colores del mapa:** el sistema no admite otros tonos, así que la rampa de datos va del
  pino a la menta pálida; la menta eléctrica queda para la acción principal y la
  localidad seleccionada.
- **Texto secundario más claro** que el gris del documento (#5e6262), que sobre #000a06 no
  se lee.

La página es ahora solo oscura. La portada va centrada, con dos botones (menta + fantasma).

**Tres defectos que se corrigieron en el camino:**
1. **El «amarillo» al tocar una localidad** (lo reportó Daniel): el foco del teclado dibuja
   un contorno, y en un SVG que mide en grados ese contorno se agranda miles de veces y
   tapa todo el mapa. Ahora la selección y el foco se marcan con el borde de la localidad.
2. **Los nombres de las localidades se veían como letras sueltas:** el tracking negativo
   del sistema, heredado dentro del SVG en grados, amontonaba las letras. El mapa usa
   tracking 0.
3. **La sección de preguntar se corría de lado** al saltar al mapa: su brillo de fondo es
   más ancho que la pantalla y `overflow:hidden` deja que el navegador la desplace. Se
   cambió a `overflow:clip`. De paso, parques y vías se recortan al contorno de la ciudad.

**El mapa con cada pregunta:** con una del catálogo se colorea con la respuesta; con una
nueva se apaga y dice en el centro por qué no se dibuja (lectura B del puente). Esto
último es a propósito.

## 5.2 Un solo paso (30/09/2026)

Daniel: «selecciono una de las preguntas y le doy preguntar pero no me dice nada». La página
pedía dos clics: el primero mostraba solo la sugerencia de reformulación, y había que dar un
segundo botón para ver la respuesta; en una ventana angosta, además, la sugerencia quedaba
fuera de la vista. Ahora:

- **Preguntar responde de una vez:** reformulación, respuesta y mapa, sin segundo clic.
- **La reformulación se muestra arriba de la respuesta**, como «así entendimos tu
  pregunta». En una pregunta nueva hay un botón «Editar y volver a suponer».
- **Fuera de alcance** no da respuesta: dice por qué y ofrece «Preguntar esto» con la
  alternativa, que vuelve a pasar por la reformulación (DI-CO4).
- **Cuando llega la respuesta**, en pantallas angostas la página baja hasta ella; en las
  anchas, el mapa de al lado parpadea en menta para decir que cambió.

Esto cambia una frase de `REFORMULACION_SPECIFICATION.md` §1 («siempre ve la versión
reformulada antes de que se responda»); quedó anotado allí.

## 5.3 Piezas copiadas de la referencia de Refero (30/09/2026)

Daniel pasó la página de Refero del mismo sistema (Metaview) para copiar su composición, no
solo sus colores. Se adaptaron:

- **Franja de aviso** arriba de todo, con lo aprendido en la prueba del puente.
- **Portada alineada a la izquierda**, con botón blanco y botón oscuro.
- **La vitrina:** una franja de aurora verde azulada a todo lo ancho, con la «maqueta del
  producto» encima: un **riel de temas** (Seguridad, La ciudad, Medio ambiente, Cambios en
  la ciudad; cada uno lanza su pregunta de ejemplo), el campo de la pregunta con **botón
  circular**, y la respuesta encabezada por el «asistente» con sus cifras en monoespaciada.
- **Fichas de filtro** sobre la respuesta de una pregunta del catálogo: Todas, Por encima,
  Por debajo y Sin diferencia clara, que atenúan en el mapa las demás localidades. **Una
  localidad cuenta como «por encima» o «por debajo» solo si su margen del 95 % no incluye
  el promedio de la ciudad**: la ficha no exagera diferencias que caben en el error.
- **Declaración centrada con esfera luminosa** y un **muro de fuentes** (en oscuro, no en
  blanco como la referencia, para no romper el sistema).
- Se respeta `prefers-reduced-motion` en las animaciones.

**La skill ui-ux-pro-max** que pidió Daniel no se instaló desde aquí: no está en el
directorio revisado de plugins, y trae scripts que habría que ejecutar. Se le explicó cómo
instalarla él mismo.

## 5.4 El mapa sin nada encima, y revisado con la skill ui-ux-pro-max (30/09/2026)

Daniel instaló la skill `ui-ux-pro-max` (v2.13.0). Antes de usar su buscador se revisó que
solo lee sus archivos locales. Tres pautas suyas se aplicaron:

- **Nada tapa el contenido** («focus not obscured»): la ficha de la localidad y la leyenda
  salen de encima del mapa y van debajo, en dos columnas (una en celular).
- **Un estado sin datos explica y ofrece una acción** («empty states»): el aviso de una
  pregunta nueva va arriba del mapa, en lenguaje llano, con un botón «Ver una pregunta con
  mapa».
- **Un mapa de colores lleva una tabla de regiones** («sortable region table», la
  alternativa accesible del coropletas): debajo del mapa, las localidades de mayor a menor,
  con su intervalo del 95 % y una línea para la ciudad. Tocar una fila la selecciona en el
  mapa, y los filtros la atenúan igual que en el mapa.

**Por qué los temas distintos de Seguridad no dibujaban:** en modo simulado, el asistente
de prueba solo reconoce las 24 preguntas de la validación, y los ejemplos de «La ciudad» y
«Medio ambiente» estaban redactados distinto, así que salían como preguntas nuevas. Los
ejemplos ahora usan esa misma redacción. «Cambios en la ciudad» es siempre una pregunta
nueva, no tiene mapa, y el botón lo dice («sin mapa»).

## 5.5 La población 2022-2024 (30/09/2026, v0.3)

Daniel mantuvo la lectura B (`PUENTE_LOCALIDADES_RESULTS.md`): las preguntas nuevas siguen sin
mapa. Lo que cambia es la población detrás de las preguntas del catálogo
(`POBLACION_EPC2022_2024_SPECIFICATION.md`; DI-CO5 a DI-CO8 en `motor.py`):

- **Cada pregunta del catálogo responde con los donantes de sus años.** 45 con 2022-2024 (~250
  encuestados por localidad), 29 con dos años y 28 solo con 2023 (~80, con los márgenes de
  siempre). La insignia dice «EPC 2022–2024» (o los años que sean) y la nota, cuántos
  encuestados hay por localidad.
- **Los grupos ya no incluyen educación:** la población no empareja por educación, así que ese
  grupo solo repetiría estrato y edad.
- **En una pregunta nueva, cada pregunta del puente se estandariza dentro de su año.**
- **Textos:** 4.522 encuestados entre 2022 y 2024; «opina como Bogotá entre 2022 y 2024»; las
  fuentes y el pie. El prompt de la reformulación no cambió (DI-CO8).

Verificado: 11 pruebas de `tests/test_consulta.py` (3 nuevas: años por pregunta,
estandarización por año, sin educación) y la página en modo simulado. En seguridad en el
barrio el mapa colorea las 19 localidades y la nota dice «unas 251 personas encuestadas por
localidad». ~~Sigue sin probarse con el modelo real.~~

**Primera prueba con el modelo real (30/09, servidor abierto por Daniel; 5 llamadas, USD 0,010):**
- «¿La gente se siente segura caminando por su barrio?» → `VS8`, EPC 2022–2024, 44 % algo o muy
  seguro, mapa con las 19 localidades.
- «¿Qué tan probable cree la gente que es que un delito sea castigado en Bogotá?» → `VS18`, **EPC
  2023**, unas 79 personas por localidad.
- «¿Les gustaría que el metro funcionara las 24 horas?» → nueva, bien reformulada; puente de 4
  preguntas, nivel propuesto 3,8 de 5, diferencias entre grupos de 0,10 DE o menos; sin mapa.
- «¿Quién va a ganar las próximas elecciones?» → fuera de alcance (predicción electoral), con una
  alternativa de opinión.

**Detalles vistos** *(1 y 2 arreglados el 30/09, DI-CO9 y DI-CO10: la frase dice cuántos
respondieron —19.000 en una pregunta de tres años, 6.492 en `VS18`, «las que heredan a alguien
encuestado en 2023»— y las etiquetas salen sin número; el 3, por decisión de Daniel, se deja y
se dice en la respuesta, DI-CO11)*:
1. La frase «Consulté a 20.000 personas sintéticas» sale igual en una pregunta que solo tiene
   2023, donde responden solo los agentes con donante de 2023 (~un tercio).
2. Algunas etiquetas traen el número del código («4. alta o 5. muy alta»).
3. El puente del metro eligió dos preguntas que solo existen en 2023 (optimismo con el metro y la
   evaluación del gobierno en movilidad): para los donantes de 2022 y 2024 valen 0 (DI-CO7), así
   que las diferencias entre grupos salen sobre todo de los de 2023.
   *Corrección (30/09, al implementar DI-CO11): solo la evaluación del gobierno en movilidad
   (`GP1N_11`) es de 2023; el optimismo con el metro (`MV150`) está en 2023 y 2024. El puente
   conserva el 38 % de su peso en 2022 y el 75 % en 2024, y ahora la respuesta lo dice: marca
   cada pregunta con sus años («solo 2023») y explica qué queda en cada año.*

## 5.6 La fuerza del puente (1/10/2026)

`PUENTE_SIN_BASE_RESULTS.md`: el puente ahora usa el prompt v2 y la respuesta a una pregunta nueva
dice qué tan sólida es su base (DI-CO12):

- Una insignia «Base fuerte», «Base media» o «Base débil» junto a «Suposición con puente», y una
  frase debajo del aviso. La débil se marca con borde punteado y texto en blanco, dentro de la
  paleta de `DESIGN.md`: se nota más, no menos.
- Si el v2 dice «sin base», se pide el puente de siempre y se muestra como débil (opción 1 de
  Daniel). Una llamada más solo en esos casos.

Verificado: 15 pruebas de `tests/test_consulta.py` (2 nuevas: la fuerza llega a la respuesta; con
«sin base» se reintenta con el prompt de siempre y sale débil) y la página en modo simulado, con
«media» y «débil». Sin probar con el modelo real.

## 5.7 Las diferencias por grupo de las preguntas nuevas, escondidas (1/10/2026)

Por la regla de `PREGUNTAS_REALES_NUEVAS_SPECIFICATION.md` §7 (P1 falló: 8 de 24, y el Corredor Verde
al revés; DI-CO13):

- En una pregunta nueva, las barras por grupo quedan dentro de «Diferencias por grupo: ver de todos
  modos», cerrado de entrada, con el aviso del resultado de la prueba antes de las barras.
- La frase de la fuerza añade: «Esto dice qué tan cerca está el tema de lo que la encuesta midió, no
  si la suposición acierta».
- Los textos fijos dejan de prometer diferencias entre grupos en las preguntas nuevas: la barra de
  anuncio, la tarjeta «Preguntas sobre un cambio», la de «El puente» y el aviso del mapa.

Verificado: 16 pruebas de `tests/test_consulta.py` (1 nueva) y la página en modo simulado (cerrado
de entrada; abierto, el aviso y luego las barras).

*Reemplazado el 2/10 por §5.8 (D18).*

## 5.8 Preguntas nuevas sin cifra propia (2/10/2026, D18)

Por la regla de salida de `BANCO_PREGUNTAS_NUEVAS.md` §10.3 (el puente no le gana al tono
general) y D18 (DI-CO14 a DI-CO16 en `motor.py`), una pregunta nueva muestra:

- **Preguntas medidas que se relacionan**, elegidas por el modelo, cada una con su sentido
  (+/−), el porcentaje en la parte alta de su escala, la distribución de la ciudad, sus años
  y «Ver completa, con su mapa», que la abre como pregunta del catálogo.
- ~~**«Así suelen responder estos grupos en la encuesta»**~~ (cambiado el 5/10, §5.12): el tono general por grupo, a la
  vista, con la aclaración de que no mide la pregunta, es el mismo para toda pregunta nueva
  y acertó el 62 % de las diferencias de la práctica (azar, 50 %).
- **Se quitan** el nivel propuesto y su barra deslizante, la fuerza del puente, las barras
  del puente tras «ver de todos modos» y el texto de peso por año (DI-CO11).
- Textos fijos ajustados: tarjeta «Preguntas sobre un cambio», paso 04, «El puente», los
  límites y el aviso del mapa.

Verificado: 16 pruebas de `tests/test_consulta.py` (tres nuevas o rehechas: sin nivel ni
fuerza y tono fijo; el tono es el mismo de `practica_puente.tono_general`; las relacionadas
traen el dato de `responder_catalogo`) y la página en modo simulado en Chrome (respuesta
nueva completa; «Ver completa» abre la pregunta del catálogo con su mapa; sin errores de
consola). Tono por estrato: 1-2 −0,07, 3-4 +0,05, 5-6 +0,24.

**Prueba con el modelo real (2/10, en el PC del CNC; 6 llamadas, USD 0,022).** Se estimaron USD
0,010-0,015 con un tope de 0,02, y el gasto real lo pasó: cada llamada costó USD 0,0033-0,0043
(~7.300 tokens de entrada), cerca del doble de lo que se calculó con la prueba del 30/09. Tres preguntas, las tres
nuevas:

- *TransMilenio las 24 horas*: 4 relacionadas (satisfacción con el transporte, optimismo con el
  metro, evaluación del gobierno en movilidad, paraderos), todas «+».
- *Prohibir el parrillero hombre*: 5 relacionadas (respeto y control de las normas de tránsito,
  seguridad), todas «−»; el v2 dio base débil sin pedir reintento.
- *¿La gente confía en la policía de su barrio?*: se esperaba del catálogo y salió **nueva**. Es
  correcto: el catálogo no tiene confianza en la policía. Relacionadas: seguridad en el barrio,
  victimización, sanción del delito, evaluación del gobierno en seguridad.

Hallazgo, corregido: **la justificación del modelo citaba el nivel** («se espera un apoyo
mayoritario (media ≈ 3.8)», «la media esperada…») y la página la mostraba. Ya no se muestra
(DI-CO16); repetido desde la caché, sin gasto: la respuesta no menciona media ni fuerza y «Ver
completa» abre `MV4` con su mapa. Visto de paso: algunas etiquetas del catálogo son solo
un número (`MV13_7`: «4 o muy satisfecho»); arreglado en §5.9.

## 5.9 Escalas numéricas (2/10/2026, DI-CO17)

47 de las 102 preguntas usan escalas de 1 a 5 en que la EPC solo nombró los extremos. No se
inventan nombres para el 2, el 3 y el 4: se muestran «1 · Muy insatisfecho», 2, 3, 4, «5 · Muy
satisfecho», y la parte alta como «4 o 5 (muy satisfecho)». También «NADA» → «Nada», y en `SP1`
«5 Muy satisfecho» → «Muy satisfecho». Solo cambia lo que se muestra.

Verificado: 17 pruebas de `tests/test_consulta.py` (1 nueva, que recorre las 102 preguntas) y la
página en modo simulado con `MV13_7`.

Visto de paso, sin tocar: en escalas que no van de peor a mejor, «la parte alta» es la de los
códigos, no la favorable (`AG1`: «mal camino»; `CC2`: «no tiene opinión o no lo conoce»). Lo que
dice es cierto, pero no siempre es lo más útil de mostrar. Arreglado en §5.10.

## 5.10 El porcentaje cuenta el lado favorable (2/10/2026, DI-CO18)

El «% que respondería…» (ciudad, grupos, ficha de la localidad y preguntas relacionadas) cuenta
el lado favorable cuando `puente.direccion` (DI-PU4) lo sabe, sin contar las categorías que no son
una opinión. Cambian dos preguntas: `AG1` → «33 % respondería "buen camino"» (antes «mal camino»)
y `CC2` → «16 % respondería "favorable"» (antes «no tiene opinión o no lo conoce»). Las 23 sin lado
favorable conocido (probabilidad de sanción, corrupción, si vota…) siguen con la mitad alta.

Verificado: 18 pruebas de `tests/test_consulta.py` (1 nueva).

~~**Queda abierto:** el mapa de `CC2` se colorea con la media de los códigos 1 a 4 (2,27), pero
3 y 4 son «No tiene opinión» y «No lo conoce»: esa media no mide nada. Arreglarlo cambia el dato
que se muestra (sacar 3 y 4 de la media, como el «no sabe»), así que se deja para decidirlo aparte.~~
Arreglado en §5.11.

## 5.11 «No tiene opinión» y «No lo conoce» cuentan como «no sabe» (2/10/2026, DI-CO19)

En `CC2` (imagen del Concejo), esas dos categorías salen de la media, el margen, el mapa, la
distribución y el porcentaje, como el «no sabe». Queda una escala de dos: **22 % favorable, 78 %
desfavorable**, de quienes tienen opinión (antes la página decía 16 % favorable sobre todos y la
media del mapa era 2,27 en 1-4). Para no esconder a quienes quedan fuera, **la página dice el
porcentaje que no cuenta cuando pasa del 5 %**, en cualquier pregunta (5 de las 102; en `CC2`,
28 %), y en las preguntas relacionadas lo pone junto al dato. El catálogo, lo que ve el modelo y el
puente no cambian.

Verificado: 19 pruebas de `tests/test_consulta.py` (1 nueva) y la página por HTTP en modo simulado
(el aviso está en la página; `CC2` responde Favorable / Desfavorable en las 19 localidades). No se
pudo mirar en Chrome: la extensión no estaba conectada en esta sesión.

Queda anotado, sin tocar: el puente estandariza `CC2` con sus cuatro códigos (así se validó); si
el modelo la eligiera como relacionada, «no lo conoce» pesaría como lo más desfavorable.

## 5.12 El tono por grupo, como contexto (5/10/2026, DI-CO21)

En los lotes 2 y 3 del banco, el tono acertó 0,466 de las diferencias claras entre grupos, peor que el azar
(`TECHO_GRUPOS_LOTES_RESULTS.md`). Por decisión de Daniel (opción 3), la página lo sigue mostrando en las
preguntas nuevas, pero:
- con el título **«Así responden estos grupos en general»** (antes: «Así suelen responder estos grupos en la
  encuesta»);
- con un texto que dice que es contexto, igual para toda pregunta nueva, y que **no sirvió para anticipar** qué
  grupos estarían más de acuerdo. Ya no cita «acertó el 62 %»;
- la tarjeta «El puente» deja de compararlo con el tono.

Verificado: 19 pruebas de `tests/test_consulta.py` (el texto no lleva ningún porcentaje).

## 5.13 Una pregunta nueva trae una estimación (5/10/2026, D19, DI-CO22)

Lo primero de la respuesta a una pregunta nueva pasa a ser **la estimación**:
- «**Probablemente sí**», «**Probablemente no**» o «**Dividida**»;
- el porcentaje que estaría de acuerdo y su rango (± 21,9) sobre una barra con la línea del 50 %;
- un texto que dice que es una estimación, cómo se hizo y cuánto acertó en las pruebas;
- debajo, **«En qué se apoya la estimación»**: las preguntas medidas que eligió Sonnet, con su resultado real
  y su fuente.

Después siguen, como contexto, las preguntas relacionadas de la EPC (con mapa) y el tono por grupo. Si la
estimación falla, se muestra el «No podemos decir…» de §5.11-DI-CO20. También cambian la tarjeta «Preguntas
sobre un cambio» y la línea de límites.

**Costo:** una llamada a Sonnet por pregunta nueva (~USD 0,02), además de la reformulación y el puente.

Verificado:
- 21 pruebas de `tests/test_consulta.py` (2 nuevas: la estimación validada y la caída al aviso anterior) y
  las 7 de la reformulación;
- la página y `/api/responder` por HTTP en modo simulado.

No se miró en el navegador, porque la extensión de Chrome no estaba conectada.

## 5.14 La estimación usa 109 candidatas (5/10/2026, DI-CO23)

- **Candidatas:** las 92 validadas más las 17 de práctica del lote 5 (Encuesta Distrital de Percepción 2025);
  su fuente aparece como «Encuesta Distrital de Percepción, Secretaría de Planeación».
- **El texto cita la prueba que justificó el cambio:** «En una prueba con 95 preguntas reales que no se habían
  usado para armarla, acertó si la mayoría estaba de acuerdo en el 72 % de los casos, y las 17 veces que dijo
  "probablemente" acertó».
- **El rango no cambia:** ±21,9.
- **Costo:** ~USD 0,024 por pregunta nueva.

Verificado: 21 pruebas de `tests/test_consulta.py` (109 candidatas, 17 del lote 5, todas con fuente).

## 5.15 Auditoría de diseño: textos viejos y la respuesta a una pregunta nueva (5/10/2026)

Daniel pidió una auditoría del diseño de la página. Se hizo leyendo el código, sin el navegador: la
extensión de Chrome no estaba conectada.
- **Lo que está bien:**
  - el sistema de diseño se aplica con coherencia;
  - **todo el texto pasa el contraste WCAG AA**: texto secundario 7,7-8,6:1, gris más tenue 4,6-5,4:1,
    botones 16-19:1;
  - el mapa tiene la tabla como alternativa, y los estados vacíos explican qué pasa.
- **Arreglado (hallazgos 1 a 5):**
  1. **La franja de arriba** decía que las preguntas nuevas eran «todavía una suposición floja».
     Ahora dice que se estiman con preguntas parecidas y que acertaron el lado de la mayoría en 7 de
     cada 10 casos (D19).
  2. **«20.000 personas sintéticas» → 19.000** en las tres apariciones: Sumapaz no tiene encuestados,
     y la propia respuesta dice «consulté a 19.000».
  3. **«Unas 80 personas por localidad»**, que era de la población 2023, pasa a «unas 250 en la
     mayoría de las preguntas (unas 80 en las que solo se hicieron en 2023)».
  4. **Las dos listas de «preguntas parecidas»** de una pregunta nueva se distinguen:
     - «En qué se apoya la estimación · preguntas de otras encuestas y su resultado real»;
     - «Para explorar · Preguntas de la Encuesta de Percepción Ciudadana que se relacionan (con mapa)»;
     - el tono por grupo pasa a «Para explorar · Así responden estos grupos en general».
  5. **En «Dividida», el porcentaje pierde peso:** baja de 44 a 30 px, pasa a gris y el texto dice
     primero el rango («…entre 31 % y 75 %: el rango cruza la mitad»), para que no se lea como «sí».
- **Pendiente, sin arreglar:**
  - el SVG del mapa con `role="img"` esconde de los lectores de pantalla las localidades, que son
    botones;
  - el parpadeo del mapa y el desplazamiento suave no respetan «menos movimiento»;
  - textos de 11-12 px;
  - fuentes de Google sin respaldo local;
  - la clase `e-sí` con tilde;
  - la revisión en pantalla a varios anchos.

Verificado: 21 pruebas de `tests/test_consulta.py` y la página servida por HTTP en modo simulado, con
las seis frases nuevas presentes.

## 5.16 Rediseño con el sistema nuevo, variante B (5/10/2026)

Daniel pidió este rediseño como «§5.8», pero ese número ya era D18. Va aquí, como el siguiente libre.

**El sistema.** `DESIGN.md` de la raíz («terminal de fósforo») reemplaza al de §5.1. Lo que cambia:
- **Color:**
  - fondo negro puro, superficies `#181818` y `#212525`, bordes `#485346` y `#1f2a33`;
  - texto en la escala de salvia (`#8cab87`, `#aed2a4`, `#9cbf93`, `#859984`);
  - los títulos van en `#ddffdc`.
- **Se van:** el blanco puro, la aurora y la esfera verde azulado, el brillo del punto «vivo» y el avatar luminoso.
- **El lima `#7fee64` rellena un solo elemento por pantalla:**
  - en la portada, «Hacer una pregunta»;
  - en la sección de preguntar, «Preguntar».
  - Los demás botones (la barra, «Preguntar esto», «Volver a suponer») son oscuros con borde.
- **Tipografía:**
  - títulos en Inter Tight 400/500, el sustituto de Goga que nombra el documento;
  - texto en Inter 400/500 con `cv11` y tracking negativo;
  - el mono queda solo para los datos.
- **Forma:**
  - botones con radio de 12 px; la píldora queda solo para el botón principal y las etiquetas;
  - tarjetas de 8 px con relleno de 32 px (20 px en celular);
  - barra de 64 px con desenfoque, sin sombras.
- **Rampa de datos:** de `#243322` a `#ddffdc`, sin otro tono.

**La disposición (variante B, elegida por Daniel entre dos maquetas):** de arriba abajo:
1. **Barra de la pregunta** a todo el ancho: temas, campo, «Preguntar» y ejemplos. Debajo, «así entendimos tu pregunta».
2. **Franja de resumen.**
   - Con una pregunta medida, tres paneles:
     - la cifra (64 px, sin cortes de línea);
     - cómo se reparte, con una leyenda en lista y no en cinco columnas que se pisaban;
     - los contadores que filtran: todas, ▲ por encima, sin diferencia clara, ▼ por debajo.
   - Con una nueva:
     - la estimación con una barra de rango grande y la línea del 50 %;
     - las preguntas de apoyo en tarjetas, cada una con su cifra real.
3. **La banda «es una suposición, no una medición»,** ahora también en las preguntas nuevas, como dice §3. Antes faltaba ahí.
4. **El mapa y una segunda columna al mismo nivel.** La segunda columna cambia según el caso:
   - con una pregunta medida, la tabla de localidades, que deja de ser un anexo debajo del mapa;
   - con una nueva, «Para explorar»;
   - sin pregunta, un estado vacío que dice qué aparecerá.
5. **Los grupos,** en columnas.

**Lo que no cambió:**
- los rótulos honestos;
- los años de cada pregunta;
- los márgenes;
- el mapa apagado con su explicación, que va en el encabezado y nunca encima;
- ~~la escala completa en el color del mapa~~ (cambió después, a pedido de Daniel: ver «Actualización» al final de esta sección).

Siguen los tres arreglos de §5.1: el foco del SVG por borde, el tracking 0 en el mapa y el `overflow:clip`. La fuerza del puente y «ver de todos modos» ya no existían (D18, DI-CO21), así que no se restituyeron.

**Decisiones nuevas:**
- **El eje de la tabla** va del margen más bajo al más alto, redondeado a una décima (2,3 a 4,0 en la seguridad del barrio), y no de 1 a 5. Con la escala completa, las 19 localidades quedaban apiñadas en el centro. Los márgenes se dibujan en el mismo eje y el eje va escrito en el encabezado, así que no exagera nada.
- **El mapa** se dibuja con proporción 3:4, porque limitarlo por el alto lo dejaba pequeño.
- **En el mapa apagado**, la localidad seleccionada se marca tenue y no en lima, para que no parezca un dato.
- **Las filas de la tabla** llevan ▲/▼ y una etiqueta para lector de pantalla con el margen.
- **El mapa pasa de `role="img"` a `role="group"`.** Era uno de los pendientes de §5.15: escondía a los lectores de pantalla las localidades, que son botones.
- **Estados:**
  - cargando, en un panel con estado para lector de pantalla;
  - error, con «Intentar de nuevo»;
  - vacío;
  - el tema o el ejemplo en uso queda marcado.

**Movimiento (skill emil-design-eng):**
- **Lo nuevo entra** con opacidad y 6 px, en 220 ms con `cubic-bezier(.23,1,.32,1)`: el resultado, la tabla, los grupos, la reformulación y la edición. Usa la Web Animations API, así que una consulta nueva cancela la entrada anterior.
- **El mapa cambia de color** en 240 ms.
- **Al presionar**, los botones se achican a `scale(.97)` en 160 ms.
- **El hover** solo aplica con puntero fino.
- **Se fueron** el parpadeo del mapa (1,2 s), el relleno de 600 ms y la esfera flotante.
- **Con «menos movimiento»** nada se anima, el desplazamiento no es suave y el indicador de carga queda quieto. Era el otro pendiente de §5.15.

**Accesibilidad:**
- **Contraste:** todo el texto pasa AA. El más tenue, `#859984`, da 6,9:1 sobre negro, 5,8:1 sobre `#181818` y 5,1:1 sobre `#212525`.
- **Foco:** contorno de 2 px en `#ddffdc`.
- **Objetivos táctiles:** todos los botones y enlaces de la página miden 44 px o más (medido en celular).

**Verificado:**
- las 21 pruebas de `tests/test_consulta.py`;
- en modo simulado, en escritorio (1280 px) y en celular (390 px, dentro de un marco):
  - una pregunta medida y una nueva;
  - editar y volver a suponer;
  - el error, simulando que el servidor falla;
  - sin desplazamiento horizontal;
  - sin errores en la consola.

**Pendiente:**
- textos de 11 a 12 px en notas y ejes;
- fuentes de Google sin copia local;
- la clase `e-sí` con tilde;
- ~~el mapa sigue casi uniforme con la escala completa. Es a propósito, y ahora lo compensa la tabla.~~ Resuelto en la actualización de abajo.

**Actualización (5/10/2026): el mapa se colorea frente a la ciudad.** Daniel vio que los colores no se
distinguían. Había dos causas:
- con la escala completa, las 19 localidades caían en el mismo tramo de la rampa (de 2,8 a 3,6 sobre 1 a 5);
- la rampa solo tenía verdes.

Le propuse dos caminos: colorear frente a la ciudad o estirar el gradiente al rango de los datos. Eligió el primero, en
verde y ámbar.
- **Tres clases, con la misma regla de los contadores:**
  - **por encima** de la ciudad, en verde claro `#9fe08a`;
  - **sin diferencia clara**, en gris `#3c413c` (en la tabla el punto va en `#9aa29a`, porque el gris del mapa no se ve sobre el fondo);
  - **por debajo**, en ámbar `#c7782a`.
  - La regla es la de siempre: cuenta como diferencia solo si el margen del 95 % no incluye el promedio de la ciudad. Así el color no muestra
    nada que el margen no respalde. El promedio y el margen de cada localidad siguen en la tabla y en la ficha.
- **Los tres tonos difieren en luminosidad, no solo en tono,** y se distinguen también con daltonismo rojo-verde.
  Además, el mapa y la tabla ponen ▲/▼ junto al nombre, y los filtros llevan la muestra del color.
- **La leyenda** pasa de la rampa a tres filas con su conteo y la regla.
- **La localidad seleccionada** se marca en fósforo y no en lima, para no confundirla con «por encima».
- **Excepción al DESIGN.md:** el ámbar rompe el «solo verde». Vale solo para estos datos; la interfaz sigue en verde.
- **Sin cambios:**
  - la rampa verde se queda en la distribución de respuestas y en el mapa de información general (adultos);
  - las preguntas nuevas siguen con el mapa apagado.

Verificado: las 21 pruebas y la página en modo simulado. Con la pregunta de seguridad, 5 localidades salen en verde, 11 en gris y 3 en ámbar, y coinciden con los
contadores y con la tabla.

## 5.17 La estimación pasa a GPT-6 Luna (6/10/2026, D20, DI-CO25)

El jefe de Daniel pidió bajar el gasto. La estimación de una pregunta nueva pasa de Claude Sonnet 5.5 a
`openai/gpt-6-luna`, que cuesta unas 20 veces menos: ~USD 0,0012 contra ~0,024.
- **No pasó su prueba completa** (`NIVEL_ACUERDO_LUNA_RESULTS.md`). Cumplió la regla con que se validó Sonnet, pero en el
  guardado se equivoca 2,4 puntos más que él (14,3 contra 11,9). Daniel decidió cambiar igual (D20).
- **Lo que cambia en la página:**
  - el rango pasa de ±21,9 a ±23,4;
  - el texto de la estimación cita las cifras de Luna: «…acertó si la mayoría estaba de acuerdo en el 69 % de los casos, y
    de las 11 veces que dijo "probablemente" acertó 10»;
  - «Qué hay detrás» dice ±23.
- **Lo que no cambia:** el método, las 109 candidatas, la forma de mostrarlo ni la franja de arriba. «7 de cada 10» sigue
  valiendo para el 69 %.
- **Verificado:** las 22 pruebas de `tests/test_consulta.py`, que ahora revisan el modelo, el rango y las cifras del texto.
- **Pendiente:** la cifra que cita la página se midió con el texto original de cada encuesta. Cuánto cambia con la
  reformulación de la página es la parte A de `NIVEL_ACUERDO_REDACCION`, que falta terminar con Luna.

## 5.18 La reformulación y el puente también pasan a Luna (6/10/2026, DI-CO26)

Pasaron su validación con Luna (`LUNA_PAGINA_RESULTS.md`):
- **la reformulación:** 24 de 24 en su prueba, y no empeora la estimación de las 95 guardadas;
- **el puente:** cumple R1, R2 y P2, como mimo.

Toda la página usa ahora `openai/gpt-6-luna`. Una pregunta nueva cuesta ~USD 0,003, contra ~0,03 con Sonnet y mimo.
- **Verificado:** las pruebas de `tests/test_consulta.py` (22) y `tests/test_luna_pagina.py` (3).
- **Pendiente:**
  - corregir el texto de la estimación con lo medido con la reformulación (`NIVEL_ACUERDO_REDACCION_RESULTS.md`);
  - probar la página en vivo con el modelo real.

## 5.19 El texto de la estimación cita lo medido con la página (6/10/2026, DI-CO27)

- **El texto de la estimación:** decía «…acertó si la mayoría estaba de acuerdo en el 69 % de los casos, y de las 11 veces
  que dijo "probablemente" acertó 10». Eso se midió con el texto original de cada encuesta. Ahora dice «En una prueba con
  90 preguntas reales…, pasadas por esta misma página (reformuladas y estimadas), acertó… en el 63 % de los casos, y de las 4
  veces que dijo "probablemente" acertó 3».
- **La franja de arriba:** pasa de «7 de cada 10» a «6 de cada 10».
- **Verificado:** las 22 pruebas de `tests/test_consulta.py`, que revisan las cifras nuevas.

## 5.20 La estimación usa lo que escribió la persona (6/10/2026, DI-CO28)

La prueba `TEXTO_PERSONA` mostró que estimar con el texto original, más la escala de la reformulación, es mejor que
estimar con la reformulada:
- error 15,6 contra 16,7;
- lado de la mayoría 68 % contra 63 %;
- 5 de 5 al decir «probablemente».

Cumple su regla, por poco.
- **Qué hace ahora la página:**
  - manda al servidor lo que escribió la persona, o lo que editó en «Editar y volver a suponer», junto con la reformulada;
  - la estimación usa ese texto;
  - lo que se muestra (el título, el puente y la escala) sigue siendo la reformulada.
- **Texto de la estimación:** «…acertó si la mayoría estaba de acuerdo en el 68 % de los casos, y las 5 veces que dijo
  "probablemente" acertó. Esa prueba usó el texto original de cada encuesta, más claro que una pregunta escrita aquí: con
  la tuya puede acertar algo menos».
- **Franja:** «unos 2 de cada 3».
- **Verificado:** las 23 pruebas de `tests/test_consulta.py`, una nueva que revisa qué texto ve el modelo que estima.
- **Pendiente:** medir la ganancia con preguntas escritas por personas, no con las de una encuesta.

## 5.21 Las candidatas de la estimación pasan a 139: entra la opinión política (6/10/2026, DI-CO29)

Se suman a las candidatas las 30 preguntas de práctica del lote 6: opinión política de las encuestas del CNC para
Semana, solo de Bogotá (migración, el paro de 2021, el rumbo del país, la vacunación). Pasó su prueba pre-registrada
(`NIVEL_ACUERDO_LOTE6_RESULTS.md`): en 129 guardadas, error 14,8 contra 15,0, y 10 de 11 al decir «probablemente».
- **Lo que mejora:** las preguntas políticas, con error de 14,1 contra 16,9.
- **Lo que se pierde:** dice «probablemente» menos veces, 11 contra 26 en las 129.
- **Texto de la estimación:** «…en una prueba con 129 preguntas reales…, acertó… en el 71 % de los casos, y de las 11 veces
  que dijo "probablemente" acertó 10», con la advertencia de que se midió con el texto de la encuesta.
- **Franja:** «unos 7 de cada 10».
- **«En qué se apoya la estimación»** puede mostrar ahora preguntas de las encuestas del CNC para Semana, con su porcentaje
  de Bogotá. Son de opinión, no de voto. Lo electoral (lote 7) no entra (D21).
- **Los resultados del lote 6 no están en GitHub:** viajan con `empacar_traslado.py`. Sin ellos, la página usa las 109 de
  antes y avisa en la terminal.
- **Verificado:**
  - las 23 pruebas de `tests/test_consulta.py`;
  - las de los lotes 6 y 7 y de las pruebas de la estimación;
  - la página cargó las 139 candidatas, todas con su fuente.

## 5.22 La intención de voto entra a la página (7/10/2026, D21, DI-CO30)

La pidió el CNC y la aprobó la revisión jurídica (D21). Daniel eligió cómo se muestra:
- **Entrada:** la página reconoce sola las preguntas de voto. La reformulación pasa a la versión 3 (`SISTEMA_V3`), que
  pasó su validación pre-registrada (`REFORMULACION_VOTO_RESULTS.md`: 13 de 13 de voto, ninguna de opinión como voto).
- **Contenido:** la estimación más las encuestas en que se apoya, con su fecha y su resultado en Bogotá. Sin mapa.
- **Fuera:** las consultas interpartidistas y la tendencia (izquierda o derecha), cuyo error en el nivel 3 fue de 11 a
  23 puntos. La reformulación las deja «fuera», con su razón.

**Qué responde:** la intención de voto **presidencial** en Bogotá, en cuatro formas: primera vuelta («¿votaría por X?»),
segunda vuelta entre dos, «nunca votaría por X» y la probabilidad de votar.

**Cómo estima:** con el método validado en el nivel 3 (`VOTO_SIMULADO_RESULTS.md`).
- Luna elige de 1 a 5 de las 373 preguntas del lote 7, con las candidatas primero y la caché marcada; la estimación es el
  promedio de su resultado real en Bogotá.
- La pregunta se ancla a la encuesta más reciente: «En mayo de 2026: …».
- **Rango:** ±7,1 puntos, el cuantil 80 % del error en la práctica.
- **Segunda vuelta:** cada candidato se estima por separado, así que no tienen por qué sumar 100. Dice «Probablemente
  gana X» solo si la diferencia pasa de 16 puntos; si no, «Reñida».

**Qué muestra:**
- la cifra y el rango de cada candidato, con la barra de rango (y la línea del 50 % en segunda vuelta);
- el texto con el error medido: 3,7 puntos en 215 guardadas (6 a 7 en candidatos grandes), 30 de 32 segundas vueltas,
  y 4,2 puntos contra la Registraduría, con el ganador acertado en 3 de 3;
- «En qué se apoya la estimación»: cada encuesta del CNC elegida, con su fecha en el texto, su resultado en Bogotá y su
  fuente (Semana o Revista Cambio);
- la banda «es una suposición, no una encuesta ni un pronóstico».

**Qué no muestra:** el mapa queda apagado con su explicación («las encuestas del CNC solo traen el total de Bogotá»), sin
leyenda, sin tabla por localidad y sin grupos.

**Los resultados del lote 7 no están en GitHub:** viajan con el traslado. Si faltan, la página dice que no puede estimar
la intención de voto.

**Verificado:**
- las 28 pruebas de `tests/test_consulta.py` (5 nuevas: voto con su rango y sus encuestas, segunda vuelta y su umbral,
  voto mal formado, la versión 3 en la página y la página sin mapa), las 9 de `test_reformular.py` y las 4 de
  `test_banco_lote7.py`;
- en el navegador, en modo simulado: primera y segunda vuelta, el mapa apagado, los grupos ocultos y sin errores en la
  consola.
- ~~**Falta:** probarla con el modelo real.~~ **Con Luna (8/10):** «¿Cuántos bogotanos votarían por Iván Cepeda?» dio 36 %
  (29–43 %), apoyado en las dos encuestas del CNC para Revista Cambio sobre Cepeda (30 % en enero de 2026 y 42 % en la de
  2026 sin mes). Daniel: «muy buenos resultados».
  - **Antes salió 2 %,** por un defecto de la caché: el modo simulado guardaba con el nombre de Luna. Se corrigió (DI-CO31).
  - ~~**Pendiente menor:** una encuesta aparece como «la encuesta de 2026» sin mes; el banco del lote 7 no lo trae.~~
    Corregido (8/10, DI-BL19): cada estudio lleva su fecha. Esa era CC892901, «a comienzos de 2026».
- **Las otras formas, con Luna (8/10, con las fechas nuevas):**
  - **Primera vuelta,** Cepeda: 36,6 % (29,5–43,8). Ahora se apoya solo en la más reciente, la fórmula de mayo de 2026.
  - **Segunda vuelta,** Cepeda contra De la Espriella: 53,6 % contra 37,1 %, «Probablemente gana Iván Cepeda». Se apoya en las
    cinco encuestas de enero a mayo de 2026.
  - **«Nunca votaría por Paloma Valencia»:** 13,1 % (6,0–20,2), con tres encuestas de 2026.
  - **«¿Quién va a ganar la consulta de la izquierda?»:** fuera de alcance, con su razón. Es lo esperado.
  - **Debilidad vista:** la estimación promedia por igual encuestas de enero y de mayo. En la segunda vuelta, la de mayo da
    47,8 contra 43,5, mucho más cerrada, y el «probablemente gana» (16,5 puntos, apenas sobre el umbral de 16) lo sostienen
    las más viejas. Darle más peso a la más reciente es un cambio de método. Antes de llevarlo a la página habría que
    pre-registrarlo y validarlo contra las 215 guardadas y la Registraduría.
    **Se probó y no pasó** (`VOTO_PESO_FECHA_RESULTS.md`): en general, el promedio simple se equivoca menos. La página no
    cambia.

## 5.23 La reformulación pasa a la versión 4 (8/10/2026, DI-CO32)

**El defecto.** La versión 3 mandaba a «nueva» «¿La gente se siente segura caminando por su barrio?», que la encuesta mide
como `VS8`. La página estimaba con preguntas parecidas lo que ya estaba medido, y no mostraba el dato real con su mapa.

**El arreglo.** La versión 4 agrega una frase a la instrucción: un matiz que no cambia lo medido sigue siendo del catálogo.

**Su validación pre-registrada** (`REFORMULACION_MATIZ_RESULTS.md`, USD 0,052):
- las 40 de la versión 3, todas bien, incluida la del barrio;
- 7 de 8 preguntas nuevas con matiz, al catálogo con su código;
- ninguna de 6 preguntas cercanas pero distintas, al catálogo. Ese es el error que más engaña.

**Lo que sigue pasando:** el modelo es conservador con los matices. «¿Qué tan seguros se sienten cuando andan por las
calles?» quedó como nueva, no como `VS10`. Así la página estima en vez de mostrar como medido algo que quizá no lo es.

**Verificado:** las 29 pruebas de `tests/test_consulta.py`, que ahora comprueban que la página usa la versión 4, y las 11
de `test_reformular.py`.

## 5.24 El rango de la estimación depende de cuántas preguntas eligió Luna (8/10/2026, DI-CO33)

**Antes:** ±23,4 fijo. **Ahora:** ±23,9 con una pregunta elegida, ±22,9 con dos y ±21,7 con tres o más.

**Validado** en `RANGO_VARIABLE_RESULTS.md`, con pre-registro y sin gasto. En las 129 guardadas, la página decide en 13 en
vez de 11 y acierta 12, con una cobertura del 79 %.

**El texto de la estimación** cita ahora «de las 13 veces que dijo "probablemente" acertó 12». El 71 % del lado no
cambia, porque la estimación es la misma.

**Lo que no cambia:** la página sigue diciendo «dividida» en 9 de cada 10 preguntas nuevas. La idea de un rango más
estrecho cuando las elegidas coinciden no se sostuvo: esa coincidencia no predice el error.

**Verificado:** las 29 pruebas de `tests/test_consulta.py` y las 7 de `test_rango_variable.py`.

## 5.25 La intención de voto por edad (8/10/2026, D21, DI-CO34)

**Qué muestra:** bajo la estimación de voto, un panel «Por edad · estimación, ±9,5 puntos». Tiene una barra por candidato
para 18 a 24 años, 25 a 54 y 55 o más. La nota dice el error medido, que 2021-2022 cortan la edad un año después, y que por
sexo y por estrato no se muestra.

**Por qué solo la edad** (`VOTO_GRUPOS_RESULTS.md`, pre-registrada, USD 0):
- **edad:** se equivoca 4,8 puntos contra 6,2 de poner el total, y acierta el sentido entre jóvenes y mayores en 66 de 71;
- **estrato:** acierta el sentido en 96 %, pero no bajó el error lo suficiente (0,93 contra 0,9);
- **sexo:** no aporta.

**Cómo se calcula:** con las mismas preguntas que eligió Luna para el total, la media de cada grupo de edad. No hay
llamadas nuevas.

**Verificado:**
- las 29 pruebas de `tests/test_consulta.py`, con la edad, su rango y el texto;
- la página, en simulado y con Luna: sin errores en la consola ni scroll horizontal. Daniel la revisó y la aprobó.

## 5.26 Una pregunta de voto incompleta dice cómo escribirla (8/10/2026, DI-CO35)

**Lo que se vio en la demo** con el jefe de Daniel: no logró preguntar por Cepeda en segunda vuelta.
- «¿En una segunda vuelta, votaría por Iván Cepeda?» sale como segunda vuelta con un solo candidato.
- «¿Cepeda o De la Espriella?» sale como primera vuelta con dos.

La lectura estricta las rechaza, y la página solo decía «No pude reformular». Lo que sí respondía era la primera vuelta
(36,6 %), que se comparó con un resultado de segunda (52 %).

**Ahora** el mensaje pide los dos candidatos, con un ejemplo hecho con el candidato que se nombró. No se reinterpreta
nada: la clasificación validada no cambia.

**Para comparar con la Registraduría:** la segunda vuelta Cepeda contra De la Espriella da 53,6 % contra 37,1 %. Sobre los
votos por los dos, como cuenta la Registraduría, son 59 % para Cepeda, unos 7 puntos por encima del 52 %, en el borde de
su rango (±7,1).

**Verificado:** las 30 pruebas de `tests/test_consulta.py`.

## 5.27 Opciones de respuesta agrupadas y el gobierno que midió cada pregunta (8/10/2026, DI-CO36)

**Lo pidió el jefe de Daniel:** poder leer, por ejemplo, la gestión del alcalde como «positiva o negativa».

**Las opciones.** En una pregunta medida, «Cómo se reparte» tiene ahora un selector: las respuestas de la escala, o tres
grupos con las mismas respuestas reales. Por ejemplo, en `GG3`:
- **negativa:** muy mala o mala;
- **neutral:** regular;
- **positiva:** buena o muy buena.

Los nombres «positiva» y «negativa» solo se usan si se sabe de qué lado está lo favorable (DI-CO18). Si no, como en la
corrupción, se usan «lado bajo», «en el medio» y «lado alto». Las preguntas de dos respuestas no tienen selector.

**El gobierno.** Ninguna pregunta de la EPC mide solo a Galán:
- `GG3` (gestión del alcalde/sa) y `CV5` (2022-2023), y `GP1N_*` (2023), son del gobierno de Claudia López;
- `MICE*` (2023-2024) mezcla los dos gobiernos.

La página lo dice con un «Ojo», al reformular y en el resultado.

~~**Lo que falta:** que la reformulación no mande «la gestión del alcalde Galán» a `GG3`. Eso cambia lo que ve el modelo:
es la versión 5, con su pre-registro.~~ **Hecho** (8/10, DI-CO37, `REFORMULACION_GOBIERNO_RESULTS.md`, USD 0,065). La
versión 5 pasó las 12 condiciones: las 4 preguntas de Galán son nuevas, y las 3 de Claudia López van a su código.

**Verificado:** las 31 pruebas de `tests/test_consulta.py`. En el navegador, `GG3` con el selector y la nota, sin errores.

## 6. Límites que la página dice

No predice ni reemplaza una encuesta; ~~opina como Bogotá en 2023; unas 80 personas por
localidad~~ opina como Bogotá entre 2022 y 2024 (v0.3); unas 250 personas por localidad en
las preguntas que se juntan, y 80 en las que solo tiene 2023, dan márgenes anchos (la
confiabilidad de las medias por localidad es baja, `PUENTE_RESULTS.md` §4); Sumapaz no tiene
encuestados; ~~el nivel de una pregunta nueva lo propone el modelo y se puede cambiar~~ ~~una
pregunta nueva no tiene cifra propia (D18)~~ en una pregunta nueva, la cifra es una estimación con un rango de
~±22 puntos (D19).
