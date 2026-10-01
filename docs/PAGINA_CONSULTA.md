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
una nueva, dos (reformulación y puente, unos USD 0,006). Las respuestas se guardan en
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
| **Ya medida** (catálogo) | % en la mitad alta de la escala, la distribución completa y el mismo % por estrato, edad, sexo y educación | Promedio por localidad en la escala completa, con su margen del 95 % en la ficha |
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

## 6. Límites que la página dice

No predice ni reemplaza una encuesta; ~~opina como Bogotá en 2023; unas 80 personas por
localidad~~ opina como Bogotá entre 2022 y 2024 (v0.3); unas 250 personas por localidad en
las preguntas que se juntan, y 80 en las que solo tiene 2023, dan márgenes anchos (la
confiabilidad de las medias por localidad es baja, `PUENTE_RESULTS.md` §4); Sumapaz no tiene
encuestados; el nivel de una pregunta nueva lo propone el modelo y se puede cambiar.
