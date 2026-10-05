# ¿ESTARÍA BOGOTÁ DE ACUERDO? — ¿mejora la estimación con las candidatas del lote 5?

Pre-registro escrito el **5 de octubre de 2026**, antes de calcular los resultados del guardado del lote 5 y
antes de hacer ninguna llamada. Gasto: **~USD 2,50, con tope de USD 3,50**, a confirmar con Daniel tras
una llamada de prueba.

## 1. Pregunta

La estimación de D19 (Sonnet eligiendo preguntas parecidas) usa **92 candidatas**: las preguntas de
práctica de acuerdo o sí/no de los lotes 1 a 3. El lote 5 (Encuesta Distrital de Percepción 2025,
`BANCO_PREGUNTAS_NUEVAS.md` §14) agrega 17 preguntas de práctica en el mismo formato que la página, varias
sobre obras, metro y transporte.

**¿Estima mejor Sonnet con 109 candidatas (configuración B) que con las 92 validadas (configuración A)?**

## 2. Datos

**Objetivos: las 95 preguntas guardadas de acuerdo o sí/no.**
- 74 de los lotes 1 a 3, las mismas de la validación de D19. Sus resultados reales ya están en
  `reales_guardado_acuerdo.json`.
- 21 del lote 5. Sus resultados reales se calculan **después** de subir este documento, con
  `banco_lote5.base_edp` y el mismo cálculo de los otros lotes.

**Candidatas:**
- **A**, las 92 de `nivel_acuerdo.tabla()`;
- **B**, esas 92 más las 17 de práctica del lote 5.

Ninguna familia guardada está entre las candidatas.

## 3. Método

El de D19 en todo lo demás: `nivel_parecidas_b` (instrucciones, formato, lectura, reintento),
`anthropic/claude-sonnet-5.5`, temperatura 0 y una llamada por pregunta.
- **A en los 74** ya está corrida (`nivel_acuerdo_validacion.json`, caché incluida): se reutiliza sin
  llamar.
- **Llamadas nuevas:** A en los 21 del lote 5, y B en los 95.
- **Rango fijo de ±21,9 para las dos**, el validado; no se recalcula, para que la comparación sea del
  pozo de candidatas y no del rango.
- Caché nueva: `data/processed/banco/cache_nivel_acuerdo_lote5.json`, que no se sube.

## 4. Regla (escrita antes de calcular)

**B reemplaza a A en la página si se cumplen las tres condiciones en los 95 objetivos:**
1. **B pasa la regla de la validación:** EAM ≤ 15,8, lado ≥ 67 % y lado ≥ referencia fija + 10 puntos.
2. **B no estima peor que A:** EAM de B ≤ EAM de A en los mismos 95.
3. **Al decidir, B acierta al menos el 90 %.**

**Si no se cumplen, sigue A.**

**Secundario, sin peso en la decisión:** las mismas cifras solo en los 21 del lote 5, donde B tiene
preguntas de la misma encuesta como candidatas.

## 5. Predicciones (escritas antes de calcular)

- **P1.** Se cumplen las tres condiciones: B reemplaza a A.
- **P2.** En los 21 del lote 5, el EAM de B es al menos 2 puntos menor que el de A.
- **P3.** En los 74 de los lotes 1 a 3, el EAM de B queda a menos de 1 punto del de A (12,5).
- **P4.** B decide («probablemente sí/no») en más preguntas que A.

## 6. Gasto

- **Llamadas:** 21 (A) más 95 (B), es decir, 116 a ~USD 0,021: **~USD 2,50**.
- **Antes de correr:** una llamada de prueba de B.
- **Tope:** USD 3,50; el código se detiene solo.

## 7. Código

`src/experiments/nivel_acuerdo_lote5.py`, con pruebas en `tests/test_nivel_acuerdo_lote5.py`. Los resultados
van a `NIVEL_ACUERDO_LOTE5_RESULTS.md`, contra este pre-registro.
