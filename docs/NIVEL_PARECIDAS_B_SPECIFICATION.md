# NIVEL POR PREGUNTAS PARECIDAS — parte B, con modelos de lenguaje más fuertes

Pre-registro escrito el **2 de octubre de 2026**, antes de hacer ninguna llamada. Hay gasto, con un
**tope de USD 4** aprobado por Daniel. Sigue a `NIVEL_PARECIDAS_RESULTS.md` (parte A) y a
`NIVEL_FORMA_RESULTS.md` (alternativa 1).

## 1. Pregunta

¿Un modelo de lenguaje **más fuerte** que el que usamos (`xiaomi/mimo-v2.6-pro`) elige preguntas
parecidas cuyo resultado real se acerque al de una pregunta nueva, mejor que los métodos sin API?

**El modelo nunca pone la cifra:** elige preguntas, y la predicción es el promedio de sus
porcentajes favorables reales (D18, Experimento 9).

## 2. Modelos

Vía OpenRouter, con la misma clave y el mismo cliente (`experimento9.cliente_real`, que registra el
costo de cada llamada):

- **`deepseek/deepseek-v4-pro`**: modelo abierto fuerte, más barato que el actual.
- **`anthropic/claude-sonnet-5.5`**: modelo de primera línea, precio medio.

**Temperatura 0 y una sola llamada por pregunta y modelo.** Se cambió de 3 repeticiones a 1, antes
de llamar, para que los dos modelos tengan el mismo diseño y para bajar el costo.

## 3. Datos y tarea

Las mismas **96 preguntas de práctica (29 familias)** de la parte A. **Las 51 guardadas no se
tocan.**

Para cada pregunta (la «nueva»), el modelo recibe:
- **la pregunta nueva:** su texto y su forma (categorías y cuáles cuentan como favorables);
- **las candidatas:** todas las preguntas de práctica de **otras familias**, con su identificador,
  texto y forma, en orden por `id`. **No ve ningún resultado.**

Se le pide elegir **de 1 a 5 candidatas** cuyo porcentaje favorable probablemente se parezca más al
de la nueva, teniendo en cuenta el tema, quién responde y la forma de la escala. Responde en JSON:
`{"ids": [...], "razon": "..."}`.

**Predicción:** la media del `total` real de las candidatas elegidas que sean válidas (que existan y
no sean de la propia familia).

**Si la respuesta no trae ninguna candidata válida:**
- se pide una vez más con la misma instrucción y una nota del error;
- si vuelve a fallar, la predicción es el promedio (R0) y se cuenta como **fallo del modelo**.

## 4. Medida y vara

El error absoluto medio (EAM) en puntos, por modelo. **La vara es 17,6**, que es 0,8 × 22,0, el
mejor método sin API de la parte A (pre-registro de la parte A, §6). Como referencia: promedio
23,0; vecinos por texto 22,0; forma de la pregunta 22,3.

**Secundarias,** sin peso en la decisión:
- cuántos fallos tuvo cada modelo;
- error ≤ 10 puntos;
- el metro y el Corredor Verde;
- las preguntas sobre Bogotá.

## 5. Gasto

**Estimado: unas 192 llamadas, alrededor de USD 1,50.**
- Sonnet: ~USD 1,25.
- DeepSeek: ~USD 0,20.

El prompt pesa unos 5.000 tokens, porque lleva el texto y la forma de ~90 candidatas.

Antes de la corrida se hace **una llamada de prueba por modelo**, que cuenta dentro del tope. Si
esa llamada muestra que el costo de la corrida pasaría el tope, se para y se consulta a Daniel.

**El código se detiene solo si lo registrado llega a USD 4.** Las respuestas quedan en caché en
`data/processed/banco/cache_nivel_b.json`, que no se sube.

## 6. Predicciones (escritas antes de llamar)

- **P1.** DeepSeek V4 Pro **no** llega a 17,6.
- **P2.** Claude Sonnet 5.5 **no** llega a 17,6.
- **P3.** Los dos tienen EAM < 23,0 (algo mejor que el promedio).
- **P4.** Sonnet tiene menor EAM que DeepSeek.

## 7. Regla de decisión (escrita antes de llamar)

- **Si un modelo llega a 17,6 o menos en la práctica:** se propone a Daniel repetir la prueba con
  ese modelo en el **banco guardado**, pre-registrada y con su costo. Solo si pasa ahí se habla de
  la página.
- **Si ninguno llega:** se cierra el camino 2 con modelos de lenguaje. Con este resultado, la
  conclusión de las cuatro pruebas es que lo que acerca el nivel son datos (camino 3). No se prueba
  Opus ni Fable salvo que Daniel lo pida con esta evidencia a la vista.

## 8. Código

`src/experiments/nivel_parecidas_b.py`, con pruebas de modelo simulado en
`tests/test_nivel_parecidas_b.py`. Los resultados van a `NIVEL_PARECIDAS_B_RESULTS.md`, contra este
pre-registro.
