# RANGO VARIABLE EN LA ESTIMACIÓN DE OPINIÓN

Pre-registro escrito el **8 de octubre de 2026**, antes de calcular nada con un rango variable. Lo pidió Daniel.
**Gasto: USD 0.** Las elecciones de Luna se recuperan de las cachés; si falta alguna, el código se detiene en vez de
llamar.

## 1. Por qué

Para una pregunta nueva, la página estima el porcentaje de acuerdo como la media real de 1 a 5 preguntas medidas que
elige Luna (D19). El rango es **fijo, ±23,4 puntos** (D20): el cuantil 80 % del error en la práctica.

Con ese rango, la página casi siempre dice «dividida». En las 129 guardadas con la configuración de hoy
(`NIVEL_ACUERDO_LOTE6_RESULTS.md`), dice «probablemente» en 11 (el 9 %) y acierta 10.

**La idea:** no todas las estimaciones son igual de inciertas. Si Luna elige cinco preguntas que dan casi lo mismo, la
estimación debería ser más confiable que si elige una sola o cinco que no coinciden. Un rango que dependa del caso sería
más estrecho donde hay acuerdo, y la página podría decidir más veces sin equivocarse más.

**La estimación no cambia,** solo su rango.

## 2. Método

**Cuatro formas del rango.** Todas se calibran en la práctica para cubrir el 80 %, como el rango fijo:
- **F0, fijo:** ±23,4, el de hoy.
- **F1, por cantidad:** un h por grupo según cuántas preguntas eligió Luna (1, 2, 3 o más). Cada h es el cuantil 80 % del
  error de su grupo en la práctica. Un grupo con menos de 10 preguntas de práctica usa el fijo.
- **F2, por dispersión:** h = c × σ, con σ la desviación estándar de los resultados reales de las elegidas.
  - **σ tiene un piso m:** la mediana de σ entre las de práctica con 2 o más elegidas. Con una sola elegida, σ = m.
  - **c** es el cuantil 80 % de error / σ en la práctica.
- **F3, por recorrido:** igual que F2, con σ = (máximo − mínimo de las elegidas) + m, y m la mediana del recorrido.

**La forma elegida se decide solo con la práctica:** la de menor ancho medio. Si otra más simple, en el orden F0, F1, F2,
F3, queda a menos de 0,5 puntos de ella, gana la más simple.

**La práctica** son las 92 preguntas de práctica de Luna (`NIVEL_ACUERDO_LUNA`), las mismas con que se fijó el ±23,4. Sus
candidatas eran las 109 de entonces. La página usa 139 (DI-RV1). Se declara la diferencia.

**Controles:**
- F0 reproduce el ±23,4 en la práctica;
- F0 reproduce, en las 129, las 11 decisiones con 10 aciertos de hoy.

Si alguno falla, el código se detiene.

## 3. La prueba

**Objetivos:** las 129 guardadas, con las 139 candidatas de la página (`nivel_acuerdo_lote6`, configuración C). Se usan
las mismas elegidas y la misma estimación.

**Medidas, para cada forma:**
- **ancho medio;**
- **cobertura:** el porcentaje con el real dentro de ±h;
- **cuántas veces decide:** «probablemente sí» si S − h > 50; «probablemente no» si S + h < 50;
- **cuántas de esas acierta el lado.**

## 4. Regla

**El rango variable entra a la página, con su forma y su calibración, si se cumplen las cuatro condiciones:**
1. **R1:** la forma elegida no es F0;
2. **R2:** en las 129, cobertura ≥ 75 %;
3. **R3:** decide en más preguntas que F0 (11);
4. **R4:** al decidir, acierta el lado en ≥ 90 %.

**Si no se cumplen,** la página sigue con ±23,4, y se anota.

## 5. Predicciones

- **PA1.** La forma elegida es F2 o F3, por dispersión.
- **PA2.** El rango variable cumple la regla.
- **PA3.** Decide en 20 o más de las 129.
- **PA4.** En la práctica, con 2 o más elegidas, la dispersión y el error van juntos (Spearman > 0).

## 6. Lo que ya se vio, y se declara

- **Con el rango fijo:** en las 129, EAM de 14,8, el lado en el 71 % y 10 de 11 al decidir. En la práctica, EAM de 14,5 y
  h de 23,4.
- **Para comprobar que la recuperación funcionaba,** se reconstruyeron sin gasto las elecciones de la práctica. Coinciden
  con la salida guardada. No se calculó ninguna dispersión ni su relación con el error.
- **Las 129 ya se usaron** para validar la configuración de hoy. Esta prueba las reusa. La forma se elige sin mirarlas,
  pero no son un conjunto virgen.

## 7. Lo que no se sube

Por D21:
- **Las elecciones y la salida** quedan en `data/processed/banco/`, ignoradas por git.
- **`RANGO_VARIABLE_RESULTS.md`** da solo cifras de ancho, cobertura y acierto.

## 8. Código

- **Código:** `src/experiments/rango_variable.py`. `--recuperar` guarda las elecciones de la práctica, sin API; sin
  argumentos, corre la evaluación.
- **Pruebas:** `tests/test_rango_variable.py`.
- **Resultados:** `RANGO_VARIABLE_RESULTS.md`.
