# ¿ESTARÍA BOGOTÁ DE ACUERDO? — ¿mejora la estimación con las candidatas del lote 8?

Pre-registro escrito el **14 de octubre de 2026**, antes de calcular los resultados del guardado del lote 8 y antes de
hacer ninguna llamada. Gasto: **~USD 0,20, con tope de USD 0,60**. Falta el visto bueno de Daniel para correr. El costo se
confirma con una llamada de prueba.

## 1. Pregunta

La página estima con Luna (D20) y **139 candidatas** (configuración C, `NIVEL_ACUERDO_LOTE6_RESULTS.md`). El lote 8
(`BANCO_PREGUNTAS_NUEVAS.md` §17) agrega **15 preguntas de práctica de la EPC 2025** que no están en el catálogo:
- colegio;
- sanciones;
- comportamiento frente a las normas;
- impactos de la inteligencia artificial;
- imagen de Galán.

**¿Estima mejor Luna con 154 candidatas (configuración D) que con las 139 de hoy (C)?**

## 2. Datos

**Objetivos: unas 139 preguntas guardadas.**
- **Las 129 de la prueba del lote 6.** Sus resultados reales ya están calculados.
- **Las 10 guardadas del lote 8.** Sus resultados reales se calculan **después** de subir este documento, con el mismo
  cálculo del lote 8 y la regla de 300 respuestas válidas. Las que no la pasen quedan fuera.

**Candidatas:**
- **C:** las 139 de la página (`nivel_acuerdo_lote6.candidatas()[1]`);
- **D:** esas 139 más las 15 de práctica del lote 8, con su resultado real de Bogotá.

**Ninguna familia guardada está entre las candidatas.** Las 373 del lote 7 (electorales) no entran ni como objetivo ni
como candidata (D21).

## 3. Método

El de `NIVEL_ACUERDO_LOTE6`, sin cambios:
- `nivel_parecidas_b` con `openai/gpt-6-luna` a temperatura 0;
- el texto y las categorías originales de cada encuesta;
- **un rango fijo de ±23,4 para las dos**, para que la comparación sea del pozo de candidatas.

**Lo que se reutiliza y lo que se llama:**
- **C en las 129** ya está corrida (`nivel_acuerdo_lote6.json`) y se reutiliza sin llamar;
- **llamadas nuevas:** C en las guardadas del lote 8, y D en todas.
- **Caché nueva:** `data/processed/banco/cache_nivel_acuerdo_lote8.json`, que no se sube.

**El mismo límite de siempre.** La página estima con el texto de la persona y la escala de la reformulación (DI-CO28).
Esta prueba usa el texto y las categorías de la encuesta: mide el pozo de candidatas, no la reformulación.

## 4. Regla (escrita antes de calcular)

**D reemplaza a C en la página si se cumplen las tres condiciones en todos los objetivos:**
1. **D pasa la regla de la validación:** EAM ≤ 15,8; acierto del lado ≥ 67 % y ≥ referencia fija + 10 puntos.
2. **D no estima peor que C:** EAM de D ≤ EAM de C en los mismos objetivos.
3. **Al decidir, D acierta al menos el 90 %.**

**Si no se cumplen, sigue C.**

**Secundario, sin peso en la decisión:** las mismas cifras solo en las guardadas del lote 8, donde D tiene preguntas de la
misma encuesta como candidatas, y solo en las 129.

## 5. Predicciones (escritas antes de calcular)

Lo que se espera, por lo que pasó con el lote 6: una mejora pequeña y concentrada en las preguntas de la misma encuesta.

- **P1.** Se cumplen las tres condiciones: D reemplaza a C.
- **P2.** En las guardadas del lote 8, el EAM de D es al menos 2 puntos menor que el de C.
- **P3.** En las 129, el EAM de D queda a menos de 1 punto del de C (14,8).
- **P4.** D no decide en más preguntas que C. Con el lote 6, más candidatas hicieron que decidiera menos.

## 6. Gasto

**Unas 150 llamadas a ~USD 0,0013:** unas 10 de C y unas 139 de D, más los reintentos.
- **Total:** unos USD 0,20, con tope de USD 0,60.
- **Antes de correr,** una llamada de prueba.
- **El código se detiene solo** al llegar al tope o si el servicio falla.

## 7. Datos que se suben

- **Sí se suben:** los resultados reales del guardado del lote 8 (`reales_guardado_lote8.json`), porque la EPC es pública.
- **No se sube:** la salida de la prueba (`nivel_acuerdo_lote8.json`). Trae los porcentajes de las preguntas del lote 6,
  que son del CNC (D21). `NIVEL_ACUERDO_LOTE8_RESULTS.md` da solo cifras de error y acierto.

## 8. Código

- **Código:** `src/experiments/nivel_acuerdo_lote8.py`.
- **Pruebas:** `tests/test_nivel_acuerdo_lote8.py`.
- **Resultados:** `NIVEL_ACUERDO_LOTE8_RESULTS.md`, contra este pre-registro.
