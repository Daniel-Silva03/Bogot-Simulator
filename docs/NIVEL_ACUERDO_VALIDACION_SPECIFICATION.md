# ¿ESTARÍA BOGOTÁ DE ACUERDO? — validación en el guardado

Pre-registro escrito el **5 de octubre de 2026**, **antes de calcular ningún resultado real del
guardado** y antes de hacer ninguna llamada. Gasto: **~USD 1,45, con tope de USD 2,50**, aprobado por
Daniel.

## 1. Pregunta

En la práctica (`NIVEL_ACUERDO_SONNET_RESULTS.md`), Claude Sonnet eligiendo preguntas parecidas cumplió
la regla: error de 13,9 puntos y lado de la mayoría acertado el 80 %; con rango, 16 de 16. **¿Se repite
en preguntas que nadie ha mirado?** Si se repite, se propone llevarlo a la página; si no, no se
muestra.

## 2. Datos

**Objetivo:** las preguntas del **guardado** de los lotes 1, 2 y 3 que son de acuerdo o de sí/no
(`nivel_acuerdo.tipo`). Son **75 preguntas en 20 familias**:
- Bienal de Culturas: 37 preguntas, 9 familias;
- ECP del DANE: 31 preguntas, 7 familias;
- Cultura Ambiental: 5 preguntas, 2 familias;
- EPC de coyuntura: 1;
- biblioteca del CNC: 1 («metro funcionando en 10 años»).

El lote 4 no entra.

**Resultados reales del guardado:** se calculan **después** de subir este documento, con el mismo código
que dio los de práctica:
- lote 1, `banco_reales.resultado` sobre la ECP y la EPC;
- lotes 2 y 3, `banco_lote2` y `banco_lote3`.

Solo se usa el porcentaje favorable de la ciudad (`total`). Las mismas reglas de estructura (DI-BR5)
sacan las que no sirvan.

**`CNC_METRO10`** (encuesta del CNC, 26-28/08/2023) no tiene microdato. Su total es el porcentaje que
responde «sí» en el informe público `opinion_publica_2023-08-29.pdf` (p. 33), leído con `pypdf`. Si el
informe no lo da sin ambigüedad, esa pregunta sale de la prueba y se informa.

**Candidatas:** **las mismas 92 preguntas de práctica** que vio Sonnet en el paso 2, con su texto y su
forma y sin resultados. Las otras preguntas del guardado no son candidatas: así el método es
exactamente el que se probó.

## 3. Método

El del paso 2, sin cambios:
- `nivel_parecidas_b.SISTEMA`, el mismo formato de pregunta y candidatas, y `parsear`;
- el reintento, y si falla dos veces, el promedio;
- `anthropic/claude-sonnet-5.5`, a temperatura 0, una llamada por pregunta;
- caché en `data/processed/banco/cache_nivel_acuerdo_validacion.json`, que no se sube.

**Predicción:** la media real de las candidatas elegidas.

**Rango fijo, escrito antes de ver nada del guardado: h = 21,9 puntos**, el cuantil 80 % del error de
Sonnet en las 92 de práctica.
- Si la predicción menos 21,9 queda sobre 50, dice «probablemente sí»; si la predicción más 21,9 queda
  bajo 50, «probablemente no»; si no, «dividida».

## 4. Medidas y regla (escrita antes de calcular)

- **Referencia fija:** decir siempre el lado mayoritario de las candidatas, que es «no» (40 de 92 con
  mayoría «sí»).
- **Sonnet pasa la validación** si cumple las tres condiciones:
  1. **EAM ≤ 15,8**, la cifra del paso 2;
  2. **acierta el lado ≥ 67 %**, la cifra del paso 2;
  3. **acierta el lado al menos 10 puntos más que la referencia fija en el guardado**, por si en el
     guardado la mayoría es «no» con más frecuencia.
- Se informa además cuántas veces decide y cuánto acierta al decidir.
- **Si pasa:** se propone a Daniel cómo mostrarlo en la página. Es una decisión de proyecto (D19), y
  siempre va rotulado como estimación.
- **Si no pasa:** la página sigue sin decir «sí» o «no», y queda el camino 3.

## 5. Predicciones (escritas antes de calcular)

- **P1.** Pasa la validación.
- **P2.** Su EAM en el guardado es mayor que en la práctica (13,9). Esperado por regresión a la media.
- **P3.** Al decidir con rango, acierta al menos el 85 %.
- **P4.** En las preguntas de la ECP (ámbito general), el EAM es mayor que en las de Bogotá.

## 6. Gasto

~75 llamadas a ~USD 0,019: **~USD 1,45**.
- **Antes de correr:** una llamada de prueba, cuyo costo se le confirma a Daniel.
- **Tope:** USD 2,50 registrados en esta caché; el código se detiene solo.

## 7. Código

`src/experiments/nivel_acuerdo_validacion.py`, con pruebas en
`tests/test_nivel_acuerdo_validacion.py`. Los resultados van a
`NIVEL_ACUERDO_VALIDACION_RESULTS.md`, contra este pre-registro.
