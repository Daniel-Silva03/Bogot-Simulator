# AGENTES CON SU ENCUESTA EN PREGUNTAS DE 2026 — ¿le ganan a la página en preguntas de verdad nuevas?

Pre-registro escrito el **16 de octubre de 2026**, antes de llamar al modelo. Lo pidió Daniel: el paso 1 de llevar los agentes a
la página, con una variante de dos modelos promediados, idea tomada de Expected Parrot. Gasto: **unos USD 0,20, con tope de
USD 1**, aprobado («sí, sigue con el paso 1 y agrégale esa variante»).

## 1. Pregunta

**Hasta ahora,** los agentes armados con la encuesta de cada persona se probaron con preguntas que esas mismas personas
respondieron. En lo político se equivocaron la mitad que la página (`PERSONAS_POLITICA_RESULTS.md`).

**Aquí van preguntas que ninguna de esas personas respondió:** las 13 de las validaciones de 2026, donde la página ya se
equivocó entre 13 y 17 puntos. **¿Les ganan los agentes a la página?** ¿Y promediar dos modelos baja la exageración?

## 2. Datos

**Los agentes:** 200 encuestados de la EPC 2025, sorteados con la semilla **20261017** entre los 920 que no se usaron en las
pruebas anteriores.
- **Su perfil:** las 40 preguntas del catálogo que se miden en 2025, más sexo, edad, estrato y localidad (el perfil A de las
  pruebas anteriores, completo, porque ninguna de las 13 está en la EPC).
- **El total:** con `Factor1`.

**Las 13 preguntas,** con el texto de las validaciones y una escala para el agente:

| # | Pregunta | Escala para el agente | Lo que se cuenta | Real |
|---|---|---|---|---|
| V1 | ¿Cree que el metro mejorará la movilidad en Bogotá? | 1=Sí; 2=No | Sí | 93 |
| V2 | ¿Usaría el metro como su principal medio de transporte? | 1=Sí; 2=No | Sí | 70 |
| V3 | ¿Confía en el proyecto del metro de Bogotá? | 1=Sí; 2=No | Sí | 80 |
| V4 | ¿El metro es un motivo de orgullo para Bogotá? | 1=Sí; 2=No | Sí | 88 |
| V5 | ¿Cree que el metro empezará a funcionar en 2028? | 1=Sí; 2=No | Sí | 56 |
| V6 | ¿Tiene una imagen favorable del alcalde Galán? | 1=Desfavorable; 2=Favorable | Favorable | 26 |
| K1 a K7 | las del CNC de 2026 (`VALIDACION_CNC_2026_SPECIFICATION.md`), con el texto completo de su cuestionario | la de su cuestionario | lo mismo que en esa validación | sin imprimir (D21) |

**Las escalas de K1 a K7 son las del CNC:**
- **K1:** progresando, igual o retrocediendo.
- **K2:** lo beneficia o lo perjudica.
- **K3 a K7:** 1 a 5 entre las dos frases de cada pregunta.

Al modelo va el texto de la pregunta, que D21 permite. Los resultados reales se calculan en el equipo con
`validacion_cnc_2026.reales()` y no se imprimen.

**Lo que se declara:**
- **El estudio del Metro (V1 a V4) no es toda Bogotá:** solo las 9 localidades de la línea 1. La redacción de V1 a V5 es mía.
- **Los perfiles son de 2025 y las preguntas de 2026.** Para el salario mínimo o la relación con Estados Unidos, eso es una
  desventaja.
- **El agente no da un rango.** Se compara la cifra del total, no el rango, con la de la página.

## 3. Los brazos

**Todos con probabilidades, una llamada por persona con las 13 preguntas:**
- **L, Luna:** `openai/gpt-6-luna`, temperatura 1, razonamiento bajo.
- **S, DeepSeek:** `deepseek/deepseek-v4-pro` sin razonamiento, con la etiqueta `#sin-razonar` (DI-NB5), temperatura 1.
- **M, los dos promediados:** para cada persona y pregunta, la media de las probabilidades de L y S. Si uno de los dos falla,
  se usa el otro.

**La referencia:** la página, con lo que dio en las validaciones de 2026: `validacion_2026` y `validacion_cnc_2026`, mismo texto.

## 4. Lo que se mide

**El error del total** (porcentaje de lo que se cuenta) en las 13, y también:
- **sin V5,** que está en el banco de la página;
- **por grupo:** las 6 públicas y las 7 del CNC.

**El lado:** en cuántas acierta si la mayoría está del lado contado, más o menos del 50 %.

**Las referencias,** en estas 13:
- **la página:** 14,6 de error medio (16,8 en las públicas y 12,7 en las del CNC); sin V5, 15,7;
- **decir 50 % para todo:** 18,1 (26,8 y 10,6).

## 5. Reglas (escritas antes de calcular)

**Los agentes le ganan a la página en preguntas nuevas si el mejor de L y M cumple las dos:**
- **R1:** su error medio en las 13 es **menor que el de la página (14,6)**, y también sin V5.
- **R2:** acierta el lado en **al menos tantas** como la página.

**La hipótesis de los dos modelos:** M mejora a L si su error medio es al menos **1 punto menor**.

S solo se reporta.

## 6. Predicciones

- **PA1.** L le gana a la página en las 13.
- **PA2.** M mejora a L.
- **PA3.** En las del metro (V1 a V4), los agentes quedan más cerca de lo real que la página, que dio de 56 % a 62 %.
- **PA4.** En las 7 del CNC, los agentes no le ganan a decir 50 % (10,6).

## 7. Gasto y código

- **Gasto:** 400 llamadas (200 personas × 2 modelos): unos USD 0,20, con tope de USD 1.
- **Al modelo** van los perfiles de la EPC (pública, anónima) y el texto de las 13 preguntas. Ningún dato individual del CNC.
- **Se reportan:**
  - las 6 públicas, pregunta por pregunta;
  - las 7 del CNC, solo su error medio y cuántas aciertan el lado.
- **Código:** `src/experiments/agentes_2026.py`, con su prueba. Resultados en `AGENTES_2026_RESULTS.md`.

---

## Enmienda 1 (16/10/2026, antes de ver ningún resultado): se cierra con lo que hay

**Qué pasó:**
- **El computador se quedó sin memoria** y Claude Code detuvo la corrida.
- **Hasta ahí:**
  - **Luna:** las 200 personas;
  - **DeepSeek:** 150 de 200.
- **DeepSeek costó nueve veces lo previsto** (unos USD 0,0046 por llamada): el gasto llegó a USD 0,77, contra USD 0,20
  estimados.
- **A la cuenta de OpenRouter le quedan unos USD 0,24.**

**Decisión de Daniel:** cerrar la prueba con lo que hay, sin gastar más.

**Qué cambia:**
- **S (DeepSeek)** se calcula con sus 150 personas.
- **M (los dos promediados)** usa, en las 50 personas sin DeepSeek, solo a Luna. Es lo que ya decía DI-AG2 para cuando uno de los
  dos falla. Así M queda más cerca de L de lo que estaría con las 200 completas.
- **La regla, las referencias y las predicciones no cambian.** La hipótesis de los dos modelos (M mejora a L en 1 punto) se
  evalúa igual, sabiendo que con 50 personas sin DeepSeek es más difícil que se cumpla.

**Cómo se calcula:** con `--solo-cache`, el script lee solo la caché y no llama al modelo. Lo que no está en la caché queda sin
respuesta.
