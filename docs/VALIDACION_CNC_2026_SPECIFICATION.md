# VALIDACIÓN CNC 2026 — ¿acierta la página en preguntas de opinión de las encuestas del CNC de 2026?

**La página, tal como está hoy, frente a siete preguntas de opinión de las encuestas del CNC para Revista Cambio de 2026
que no están en el banco ni en el catálogo.**

Proyecto: Bogotá Social Simulator
Versión: 0.1 — pre-registro, antes de hacerle ninguna de estas preguntas a la página
Fecha: 14 de octubre de 2026
Origen: Daniel pidió preguntas recientes y del CNC, y que la prueba cuente como validación.

---

## 1. Las preguntas

Se escriben en la página **tal como están aquí**. Ninguna se ha hecho todavía.

| # | Pregunta | Original | Lo que se cuenta |
|---|---|---|---|
| K1 | ¿Cree que Colombia está progresando? | CC891901 P21, enero de 2026 | «Está progresando» (frente a «igual» o «retrocediendo») |
| K2 | ¿A usted personalmente el aumento del 23 % del salario mínimo lo beneficia? | CC891901 P22, enero de 2026 | «Lo beneficia» |
| K3 | ¿Se debe incrementar la exploración de petróleo en Colombia? | CC893401 P13, abril de 2026 | 4 o 5: incrementar la exploración |
| K4 | ¿Se debe persistir en los diálogos de paz con los grupos armados? | CC893401 P14, abril de 2026 | 1 o 2: persistir en los diálogos |
| K5 | ¿Colombia debería tener un Estado más grande que haga más inversión social? | CC893401 P15, abril de 2026 | 1 o 2: Estado más grande |
| K6 | ¿Colombia debe tener relaciones cercanas con Estados Unidos? | CC893401 P16, abril de 2026 | 4 o 5: relaciones cercanas |
| K7 | ¿El sistema de salud lo debe manejar solo el Estado? | CC893401 P17, abril de 2026 | 1 o 2: lo maneja el Estado |

**El resultado real:**
- el porcentaje de lo que se cuenta, entre los encuestados de Bogotá (`DANE` = 11001), con el factor de expansión;
- **sin «no sabe»** (el 9);
- K3 a K7 son escalas de 1 a 5 entre dos frases, y **el 3 cuenta como «no»**.

**Unos 336 encuestados en Bogotá en enero y 342 en abril:** el resultado real tiene un margen propio de unos ±5 puntos.

**Lo que se declara antes de correr:**
- **Nadie de este análisis vio los resultados.** Por D21, los porcentajes de las encuestas del CNC no pasan por un modelo de
  lenguaje: el script los calcula en el equipo, no los imprime y guarda solo cifras de error y acierto. Daniel tiene los
  resultados en un archivo local.
- **Las preguntas no están en el banco** (`sorteo*.csv`) **ni en el catálogo.** Se revisó por su código antes de escribir
  esto. Lo que sí hay en el banco de estas mismas encuestas es intención de voto (lote 7).
- **Son temas nacionales, no de Bogotá.** La página está hecha para opinión sobre la ciudad, y su reformulación puede
  mandar alguna a «fuera de alcance».
- **La redacción es mía.** En K3 a K7, la original pide ubicarse entre dos frases. La página puede reformularlas con otra
  escala, así que la comparación es aproximada.
- **Quedan fuera:**
  - «¿el resultado de las elecciones será positivo o negativo para el país?», que roza lo electoral (D21);
  - el principal problema del país, que es de selección múltiple;
  - las de Venezuela, cuyo texto depende de una pregunta anterior.

**Una nota añadida antes de subir este documento (14/10).** Al probar el circuito en modo simulado, sin gasto, el script
imprimió una cifra agregada de los resultados reales:
- **el error de decir 50 % para todo en estas siete: 10,6 puntos.** Quiere decir que, en promedio, los resultados están
  cerca del 50 %;
- también imprimió, para una pregunta, que su resultado real queda fuera de un rango simulado de 32,7 a 76,1.

No se vio ningún porcentaje. Las predicciones de §4 ya estaban escritas y no se cambiaron.

## 2. Cómo se corre

Igual que la validación 2026 (`validacion_2026.preguntar`):
- reformulación;
- si es nueva, la estimación con el texto original (DI-CO28);
- si va al catálogo, el dato medido.

**Detalles:**
- modelo real de la página, las 223 candidatas de hoy, caché propia (`data/processed/validacion_cnc_2026/`), una sola
  corrida.

## 3. Regla de decisión

**Para cada pregunta, igual que la validación 2026:**
- si el real cae dentro del rango;
- si la llamada acierta: «sí» si el real supera 50 %, y «no» si queda por debajo; «dividida» no decide;
- la diferencia entre el porcentaje de la página y el real.

**Los casos especiales:**
- **Si va al catálogo,** cuenta su error, pero no el rango ni la llamada.
- **Si va a «fuera»,** cuenta como fallo en las tres.

**La página pasa la validación CNC 2026 si se cumplen las tres:**
- **R1:** el real cae dentro del rango en **al menos 5 de las 7**.
- **R2:** cuando dice «probablemente», **falla en una como máximo**.
- **R3:** su error medio es **menor que el de decir 50 % para todo** en estas siete. Se calcula en la corrida, porque nadie
  ha visto los resultados.

**Lo que se reporta** (D21):
- de cada pregunta: la reformulación, la estimación de la página, si el real cae dentro del rango y si la llamada acertó;
- **ni el resultado real ni el error de cada pregunta:** juntos con la estimación, revelarían el porcentaje del CNC;
- el error medio y el de decir 50 %, solo de las siete juntas.

**Pase o no, la página no cambia.**

## 4. Predicciones

- **PK1.** La página no pasa. En la validación 2026 tampoco pasó, y aquí los temas son nacionales.
- **PK2.** Al menos una de las siete va a «fuera de alcance».
- **PK3.** Dice «probablemente» en dos o menos de las siete.
- **PK4.** Su error medio es menor que el de decir 50 % (R3 se cumple).

## 5. Gasto y datos

- **Gasto:** 7 preguntas nuevas, de 2 a 3 llamadas cada una. Unos **USD 0,04, con tope de USD 0,15**. Falta el visto bueno de
  Daniel.
- **Al modelo** van solo los textos de las preguntas (D21). Ningún resultado de las encuestas del CNC.
- **No se suben:** los resultados reales y la salida con los reales, que quedan en `data/processed/validacion_cnc_2026/`,
  ignorados por git. `VALIDACION_CNC_2026_RESULTS.md` da lo de §3.
- **Código:** `src/experiments/validacion_cnc_2026.py`, con su prueba.
