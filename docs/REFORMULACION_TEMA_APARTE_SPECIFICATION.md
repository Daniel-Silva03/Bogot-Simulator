# EL TEMA EN UNA LLAMADA APARTE: ¿RECONOCE LO POLÍTICO SIN TOCAR LA VERSIÓN 5?

Pre-registro escrito el **19 de octubre de 2026**, antes de llamar al modelo. Sigue a `REFORMULACION_TEMA_RESULTS.md`: la
versión 6 acertó el tema en 30 de 30, pero el párrafo nuevo movió un caso de alcance («caminando por su barrio» dejó de ir a
`VS8`) y no pasó. Sigue siendo la **primera validación de la condición 1 de D22**. Lo pidió Daniel. Gasto: **unos USD 0,03,
con tope de USD 0,30.**

## 1. El cambio

La versión 5 queda **intacta**: misma instrucción, mismo catálogo, mismas notas. Después de ella:
- **Si va al catálogo:** el tema sale de una lista fija, sin llamar al modelo. Son políticas las nueve de gobierno del catálogo
  2022-2025: `AG1` (rumbo), `GG7` (corrupción), `CC2` (imagen del Concejo), `PE_EL1` (votar), `GG3_GALAN`, `CC5A_GALAN` y
  las tres `MICE_GALAN`. Las demás son de ciudad.
- **Si es nueva:** una llamada aparte, corta, con la pregunta como la escribió la persona y como quedó reformulada. Las
  definiciones son las mismas de la versión 6 (§2 de `REFORMULACION_TEMA_SPECIFICATION.md`), al pie de la letra. Responde
  `{"tema": "politica|ciudad"}`.
- **Si es «voto» o «fuera»:** no lleva tema.

Una nueva cuyo tema no se puede leer cuenta como respuesta inválida.

**Por qué no hace falta repetir las 63 anteriores:** la versión 5 no cambia, y la caché da lo mismo con la misma entrada. Lo
garantiza la construcción, no una prueba. Una prueba del código comprueba que la instrucción de la 5 sigue igual.

## 2. La prueba: 30 preguntas que no se usaron antes

Ninguna está en las pruebas anteriores de la reformulación (lo comprueba el código).

| # | Pregunta | Tema esperado |
|---|---|---|
| A1 | ¿Qué tan bien está haciendo su trabajo el alcalde? | politica |
| A2 | ¿Ha aumentado la corrupción en Bogotá en el último año? | politica |
| A3 | ¿La gente tiene buena opinión del Concejo? | politica |
| A4 | ¿La administración de Galán es transparente? | politica |
| A5 | ¿Confían los bogotanos en la Fiscalía? | politica |
| A6 | ¿Qué tanto confía la gente en el Ejército? | politica |
| A7 | ¿Cómo califican el trabajo de la Secretaría de Seguridad? | politica |
| A8 | ¿Qué opinan del gobierno de Gustavo Petro? | politica |
| A9 | ¿Creen que los congresistas representan bien a los ciudadanos? | politica |
| A10 | ¿Cómo califican la gestión de Galán frente al racionamiento de agua? | politica |
| A11 | ¿Confían los bogotanos en la Procuraduría? | politica |
| A12 | ¿Creen que las elecciones en Colombia son limpias? | politica |
| A13 | ¿Qué tan satisfechos están con la gestión de su alcalde local? | politica |
| A14 | ¿Cree la gente que el país va por buen camino? | politica |
| A15 | ¿Qué imagen tiene la gente de la Contraloría? | politica |
| A16 | ¿Les gustaría que el próximo alcalde mantenga el plan de seguridad de Galán? | politica |
| A17 | ¿Qué tan satisfechos están con la recolección de basuras? | ciudad |
| A18 | ¿Qué tan seguros se sienten en Bogotá? | ciudad |
| A19 | ¿Están contentos con la oferta cultural de la ciudad? | ciudad |
| A20 | ¿Estarían de acuerdo con peatonalizar la carrera Séptima? | ciudad |
| A21 | ¿Apoyarían una tarifa más baja de TransMilenio para estudiantes? | ciudad |
| A22 | ¿Qué tan satisfechos están con los hospitales públicos? | ciudad |
| A23 | ¿A la gente le cuesta llegar a fin de mes? | ciudad |
| A24 | ¿Apoyarían construir edificios más altos en su barrio? | ciudad |
| A25 | ¿Qué tan limpios creen que están los ríos de Bogotá? | ciudad |
| A26 | ¿A la gente le gusta vivir en Bogotá? | ciudad |
| A27 | ¿Apoyarían que cierren más vías los domingos para la ciclovía? | ciudad |
| A28 | ¿Qué tan satisfechos están con los jardines infantiles? | ciudad |
| A29 | ¿Estarían de acuerdo con cobrar peajes a la salida de Bogotá? | ciudad |
| A30 | ¿Qué opinan del ruido de las fiestas en los barrios? | ciudad |

**Lo que se declara:**
- **El alcance no se juzga,** solo el tema.
- **Una política que la versión 5 mande a «fuera» o a «voto»** cuenta como error del tema: en la página no llegaría a los
  agentes.
- **A16** es de continuidad, como la pregunta del jefe, pero nombra una medida (el plan de seguridad). Por §1 es política.
- **A20, A21, A24, A27 y A29** son aprobaciones de una medida en Bogotá: ciudad.

## 3. Reglas (escritas antes de llamar al modelo)

**Pasa si se cumplen las tres:**
- **RA1:** «politica» en **al menos 14 de las 16** políticas (A1-A16).
- **RA2:** «ciudad» en **al menos 12 de las 14** de ciudad (A17-A30).
- **RA3:** respuesta válida en **al menos 28 de las 30**.

## 4. Predicciones

- **PA1.** Pasa.
- **PA2.** Los errores, si los hay, caen en A16 o en las aprobaciones de una medida.
- **PA3.** Al menos 3 de las políticas van al catálogo con tema político (A1, A2, A3 o A4).

## 5. Qué pasa después

- **Si pasa:** la página sigue en la versión 5 y le suma el tema. El motor manda a los agentes las nuevas de tema político; los
  agentes siguen apagados con el modelo real (`AGENTES_CON_MODELO_REAL = False`) hasta la segunda validación de D22. Ese cambio
  va con su propio DI-CO y se le muestra a Daniel antes.
- **Si no pasa:** se anota qué falló y la página no cambia.

## 6. Gasto y código

- **Gasto:** 30 llamadas de la versión 5 y una llamada corta por cada nueva (unas 22), unos USD 0,03, con tope de USD 0,30.
- **Al modelo** va lo de siempre: la pregunta y el catálogo, sin datos de personas.
- **Código:** `TEMA_POLITICO_CATALOGO`, `SISTEMA_TEMA`, `clasificar_tema`, `tema_de`, `PRUEBA_TEMA_APARTE` y
  `validar_tema_aparte` en `src/consulta/reformular.py`, con `python src/consulta/reformular.py --validar-tema-aparte`.
  Prueba en `tests/test_reformular_tema.py`. Resultados en `REFORMULACION_TEMA_APARTE_RESULTS.md`.
