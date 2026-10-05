# ¿ESTARÍA BOGOTÁ DE ACUERDO? — el nivel en preguntas de acuerdo y de sí o no (paso 1, sin API)

Pre-registro escrito el **5 de octubre de 2026**, antes de calcular nada. Sin gasto.

## 1. Pregunta

Daniel quiere que, ante una pregunta nueva, la página diga si la población **estaría o no de acuerdo**.
Las pruebas del nivel (`NIVEL_PARECIDAS_*`, `NIVEL_FORMA_*`) mezclaban escalas muy distintas (confianza,
satisfacción, «¿cuántos son corruptos?»), cada una con su nivel típico. Además, el «sí o no» de esas
preguntas no le ganó a decir siempre «no» (exploración del 5/10, no pre-registrada: 72 % contra 72 %).

La página siempre pregunta «¿qué tan de acuerdo está…?», así que el problema real es más acotado:
**¿se puede estimar el porcentaje de acuerdo, y el lado de la mayoría, de una pregunta nueva de acuerdo
o de sí o no, con preguntas parecidas de ese mismo tipo ya medidas?**

## 2. Datos

Las preguntas de **práctica** de los lotes 1, 2 y 3 del banco, utilizables y sin exclusión de
estructura, cuyas categorías son de **acuerdo** (alguna etiqueta dice «acuerdo») o de **sí o no** (`1=Sí`
y una opción «No»): **92 preguntas en 25 familias, 76 de Bogotá**.
- El lote 4 no entra: no representa a la ciudad.
- Los guardados (75 preguntas en 20 familias) no se tocan: son la validación final si algo pasa.
- Se miró solo la estructura para contarlas; ningún porcentaje del subconjunto.

**Lo que se mide:** el porcentaje favorable de la ciudad (`total`, DI-BA3): el «de acuerdo» o el «sí».
**El lado de la mayoría** es «sí» si `total` > 50.

## 3. Métodos (sin API; cada pregunta sin su familia, y el pozo es solo este subconjunto)

- **M0, promedio:** la media del pozo.
- **M1, vecinos por texto:** las 5 más parecidas por TF-IDF de caracteres, como R2 de la parte A
  (`nivel_parecidas.similitudes`).
- **M2, forma:** regresión `total ~ 1 + F1 + tipo + Bogotá`, donde F1 es la fracción favorable (como
  en `nivel_forma`) y tipo es acuerdo o sí/no.

**Sonnet no entra en este paso:** sus elecciones de la parte B se hicieron con otro pozo y solo para el
lote 1.

## 4. Medidas

1. **EAM** (error absoluto medio) del porcentaje, en puntos.
2. **Lado:** fracción de preguntas en que el método acierta el lado de la mayoría. Se compara con la
   **referencia fija**: decir siempre el lado mayoritario del pozo, sin la familia.
3. **Llamada con rango.** El rango es la predicción ± h, con h el cuantil 80 % del error absoluto del
   método en las **otras** familias.
   - Si todo el rango queda sobre 50, dice «probablemente sí»; si todo queda bajo 50, «probablemente
     no»; si cruza 50, «dividida».
   - Se informan cuántas veces se decide y cuánto se acierta al decidir, por separado para «sí» y «no».

## 5. Predicciones (escritas antes de calcular)

- **P1.** La referencia fija acierta el lado entre 60 % y 80 %.
- **P2.** Ningún método cumple la regla de §6.
- **P3.** M2 (forma) tiene el menor EAM de los tres.
- **P4.** Con el rango del 80 %, el mejor método decide (dice «sí» o «no») en menos del 30 % de las
  preguntas.

## 6. Regla de decisión (escrita antes de calcular)

Un método **sirve para decir «sí o no» en la página** si en la práctica cumple las dos condiciones:
1. **acierta el lado al menos 10 puntos más que la referencia fija**;
2. **su EAM es ≤ 0,8 × el de M0.**

- **Si alguno sirve:** se propone a Daniel validarlo, pre-registrado, en el guardado (20 familias),
  antes de mostrar nada en la página.
- **Si ninguno sirve:** se informa, y la página sigue sin decir «sí» o «no». Lo siguiente sería la
  prueba con Sonnet sobre este mismo subconjunto (con costo, que se le consultaría a Daniel) o el
  camino 3.

## 7. Código

`src/experiments/nivel_acuerdo.py`, con pruebas en `tests/test_nivel_acuerdo.py`. Los resultados van a
`NIVEL_ACUERDO_RESULTS.md`, contra este pre-registro.
