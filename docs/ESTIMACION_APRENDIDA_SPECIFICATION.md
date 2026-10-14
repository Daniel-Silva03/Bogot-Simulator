# ESTIMACIÓN APRENDIDA — ¿predice mejor un modelo entrenado con todo el banco que elegir 5 preguntas parecidas?

Pre-registro escrito el **14 de octubre de 2026**, antes de calcular nada. Lo pidió Daniel (opción A de la búsqueda del
estado del arte). Gasto: **menos de USD 0,01, con tope de USD 0,05**; falta su visto bueno.

## 1. Pregunta

**Hoy (configuración E, DI-CO39):** Luna elige hasta 5 de las 223 candidatas que cree parecidas, y la cifra es la media de
sus resultados reales. En las validaciones de 2026 se vio su defecto: se queda cerca del 50 % y casi nunca se compromete.

**La idea:** la que siguen los estudios que ajustan modelos con miles de encuestas (SubPOP, 2025). En vez de promediar 5
preguntas, un modelo estadístico aprende de **todas** las preguntas con resultado real cómo se relaciona el texto de una
pregunta con su porcentaje.

**¿Estima mejor que E, en las mismas 139 preguntas escondidas?**

**La regla de siempre no cambia:** el modelo de lenguaje nunca pone cifras ni contesta por nadie. Aquí solo convierte el
texto en un vector («embedding», `intfloat/multilingual-e5-large`). La cifra la pone un modelo estadístico entrenado con
resultados reales.

## 2. Datos

**Entrenamiento: 238 preguntas con resultado real de Bogotá.**
- **Las 223 candidatas de E:** 84 del catálogo y 139 de los lotes 1 a 6.
- **Las 15 de práctica del lote 8** (EPC 2025).
- **Ninguna comparte familia con un objetivo.**

**Objetivos: los mismos 139 de las pruebas del lote 8 y del catálogo.** Eso permite la comparación directa con E, que ahí
tiene EAM 15,3, acierto del lado de 73 % y 13 de 14 al decidir.

**Prueba secundaria, sin peso en la decisión:** las 13 preguntas de las validaciones 2026 (`VALIDACION_2026` y
`VALIDACION_CNC_2026`):
- con su texto y una escala de acuerdo, con el «sí» como favorable;
- V5 se reporta aparte, porque está en el banco;
- en las 7 del CNC solo se reporta el error medio (D21).

**El texto de cada pregunta para el embedding:** `query: <texto> | <categorías válidas, con * en las favorables>`, con la
forma de `nivel_parecidas_b.forma`.

## 3. Los modelos

Todos usan los mismos embeddings, normalizados:
- **M1, regresión ridge:** predice el porcentaje favorable a partir del embedding.
- **M2, vecinos semánticos:** la media de los k entrenamientos más parecidos por coseno. Es lo de E, pero eligiendo por
  significado en vez de con Luna.
- **M3, la media de M1 y E:** combina lo aprendido con la elección de Luna.

**Los parámetros se eligen solo con el entrenamiento,** por validación cruzada de 5 grupos por familia:
- ridge con α en {1, 10, 100, 1000};
- k en {5, 10, 20}.

**El rango de cada modelo:** el cuantil 80 % de su error absoluto en esa validación cruzada, igual que el ±23,4 de Luna.
- **M3:** el de M1, porque E no tiene validación cruzada en el entrenamiento.
- **La llamada:** «probablemente sí», «no» o «dividida», con `nivel_acuerdo.llamada`.

## 4. Regla (escrita antes de calcular)

**Un modelo reemplaza a E en la página si se cumplen las cuatro condiciones en los 139:**
1. **EAM al menos 1 punto menor que el de E:** ≤ 14,3. Un punto, y no medio, porque se prueban tres modelos.
2. **Acierto del lado ≥ 70 %** (E: 73 %).
3. **Al decidir, acierta al menos el 90 %**, con su propio rango.
4. **Pasa la regla de la validación de siempre** (EAM ≤ 15,8; lado ≥ referencia + 10).

**Si más de uno cumple,** gana el de menor EAM. **Si ninguno cumple, sigue E.**

## 5. Predicciones (escritas antes de calcular)

- **P1.** Ninguno reemplaza a E. Con 238 ejemplos hay poco que aprender; SubPOP usó decenas de miles.
- **P2.** M3 tiene el menor EAM de los tres.
- **P3.** M1 queda a menos de 1 punto de E (entre 14,3 y 16,3).
- **P4.** En las 5 públicas de 2026 sin V5, ningún modelo baja el error medio de la página (19,9).

## 6. Gasto y datos

- **Embeddings:** unos 390 textos con `intfloat/multilingual-e5-large` por OpenRouter. Menos de USD 0,01, con tope de USD
  0,05.
- **D21:**
  - al servicio de embeddings van solo los textos de las preguntas;
  - los resultados de las encuestas del CNC se usan para entrenar aquí, en el equipo, y no se imprimen;
  - los resultados se reportan solo como cifras de error y acierto.
- **No se suben:** la caché de embeddings y la salida, que trae porcentajes del CNC.
- **Código:** `src/experiments/estimacion_aprendida.py`, con su prueba. Resultados en `ESTIMACION_APRENDIDA_RESULTS.md`.
