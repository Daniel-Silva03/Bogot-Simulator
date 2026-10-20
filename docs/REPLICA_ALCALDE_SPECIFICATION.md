# PLAN V4, PASO 1: ¿SE REPITE EL ACIERTO DE LOS AGENTES CON EL ALCALDE?

Pre-registro escrito el **20 de octubre de 2026**, antes de llamar al modelo. Sigue `PLAN_SIGUIENTE_PREDICTOR_BOGOTA_V4.md`, Paso 1.
Lo pidió Daniel; el Paso 3 del plan no se hace, por decisión suya. Gasto: **unos USD 0,20, con tope de USD 1.**

## 1. La pregunta

En la gestión de Galán 2025, la persistencia dijo 42, los agentes 29 y lo real fue 26 (Fase 3). **¿Es algo que se repite en las
preguntas de gobierno, o fue un caso?**

## 2. Lo que ya se sabe, y por qué la prueba es solo de gobierno

- **En el conjunto completo, la respuesta ya está y es no.** En la Fase B, con todas las preguntas comparables, los agentes perdieron
  con la persistencia en las dos transiciones: 5,75 contra 4,7 (2023 → 2024) y 8,3 contra 6,1 (2024 → 2025). La regla del plan v4
  («superar a la persistencia en el conjunto completo y en más de una transición») ya no se puede cumplir. Así se informa.
- **Lo que queda abierto es gobierno**, donde está el caso de Galán. **Este subconjunto se elige después de ver la Fase B y la
  Fase 3**: es una prueba de si el resultado de gobierno se sostiene al sumar casos nuevos, no una prueba general.

## 3. Los objetivos (15)

| Transición | Perfiles | Preguntas | De dónde |
|---|---|---|---|
| **T0:** EPC 2022 → 2023 | 200 agentes de 2022 | rumbo (`AG1`), corrupción (`GG7`), gestión de la alcaldesa Claudia López, gestión del Concejo | **nuevo** |
| **T1:** EPC 2023 → 2024 | 200 agentes de 2023 | rumbo, corrupción, gestión del alcalde Galán (recién llegado), gestión del Concejo | **nuevo** |
| **T2:** EPC 2024 → 2025 | 200 agentes de 2024 | rumbo, corrupción, Galán, Concejo, transparencia, respuesta, participación (`MICE1-3`) | **Fase B, no se vuelve a llamar** |

- **Se excluye `CC9`** («¿conoce Bogotá Cómo Vamos?»): no es percepción política. La misma regla que en la Fase 3.
- **Las preguntas del alcalde y del Concejo de T0 y T1 no están en el catálogo 2022-2025** (el catálogo las tiene desde 2024). Su
  dato sale de la serie larga de la EPC (`serie_epc_bcv.csv`, «buena» más «muy buena» de 5 opciones), la misma de la Fase 1. En
  2024 y 2025 la serie y el catálogo coinciden (diferencia 0,0).
- **En T1, la persistencia del alcalde repite el dato de López 2023** para Galán 2024: es lo que habría dicho quien repite el último
  dato medido del alcalde.
- **Exclusiones** (fijadas ahora): solo se excluye un objetivo si ningún agente lo responde. Los `MICE` se quedan en la muestra
  principal; como sensibilidad, se informa el resultado sin ellos, porque pueden haber cambiado de cuestionario en 2025.

## 4. El método

**El de la Fase B**, sin cambios:
- `selector_fase_b.estimar`, con su nota («las respuestas de arriba son de {base}… la persona puede haber cambiado de opinión»);
- los mismos 200 agentes del año base (semilla de la página);
- `openai/gpt-6-luna`, temperatura 1, razonamiento bajo;
- una llamada por agente con las 4 preguntas de su transición;
- lo que se cuenta es «buena» o «muy buena» (o el lado de `motor.lado`), ponderado con el peso de la encuesta.

**Un cambio en el perfil, para que T0 y T1 sean como T2.** El perfil de 2024 ya lleva lo que la persona respondió sobre el alcalde
y el Concejo ese año. El de 2022 y 2023 no, porque esas preguntas no están en el catálogo de esos años. Se agregan al perfil
(`GG3` y `CC5`, con la escala de 5). Sin esto, en T0 los agentes no sabrían qué pensaba la persona de López.

**El alias de sexo, edad y estrato de 2022** es el mismo que el de 2023 (`CS1`, `CS2`, `CS21`), revisado en las etiquetas del
archivo.

## 5. Lo que se declara antes de correr

- **Lo real ya se vio en 9 de los 15:** T2 entero (Fase B y Fase 3) y rumbo y corrupción de 2023 → 2024 (Fase B). La serie larga
  del alcalde y del Concejo se usó en la Fase 1, para calcular errores de la persistencia.
- **T1 de rumbo y corrupción se vuelve a llamar**, ahora con el perfil que lleva al alcalde y al Concejo. El resultado de la Fase B
  para esas dos se informa como comparación.
- **Filtración temporal:** el modelo puede saber qué pasó en 2023 y 2024. Una prueba hacia atrás muestra consistencia; no prueba que
  los agentes anticipen lo que no conocen (plan v4). Eso solo lo dirá una prueba hacia adelante, como la EPC 2026.
- **Son pocos casos:** 15, y el alcalde solo 3. El resultado del alcalde es descriptivo.

## 6. Reglas (escritas antes de llamar)

**Los agentes «se reproducen» en gobierno si cumplen las tres:**
- **RP1:** su error medio en los 15 es **al menos 1 punto menor que el de la persistencia.**
- **RP2:** su error medio es menor que el de la persistencia **en al menos 2 de las 3 transiciones.**
- **RP3:** sigue siendo menor **sin los dos objetivos en que más le ganan.**

**Para el alcalde (descriptivo):**
- **RA:** los agentes se equivocan menos que la persistencia en la gestión del alcalde **en al menos 2 de las 3 transiciones.**

**Qué se hace con el resultado:**
- **Si se reproducen:** se informa como resultado exploratorio fuerte en gobierno. Sigue sin ser un predictor validado, por la
  filtración temporal (§5).
- **Si no:** se informa que el acierto de 2025 no se repite, y en la página nada cambia (decisión de producto).

## 7. Predicciones

- **PR1.** RP1 no se cumple: los agentes no le ganan a la persistencia por un punto en los 15.
- **PR2.** En el alcalde, los agentes ganan en 1 de 3 o menos (RA no se cumple).
- **PR3.** El sesgo de los agentes en los 15 es positivo: ven al gobierno mejor de lo que es.

## 8. Gasto y código

- **Gasto:** 400 llamadas (200 en T0 y 200 en T1), unos **USD 0,20**, con **tope de USD 1.**
- **Al modelo** van los perfiles de la EPC 2022 y 2023 (pública, anónima), las preguntas y la nota. Nada de las encuestas propias.
- **Código:** `src/evaluacion/replica_alcalde.py`, con `tests/test_replica_alcalde.py`. Resultados en `REPLICA_ALCALDE_RESULTS.md`.
