# LA PÁGINA CON GPT-6 LUNA — la reformulación y el puente

Pre-registro escrito el **6 de octubre de 2026**, antes de hacer ninguna llamada. Gasto: **~USD 0,30, con tope
de USD 0,75**. Daniel lo pidió («sí, todo a Luna»), pero con prueba: cada pieza cambia solo si pasa su regla.

## 1. Pregunta

Por D20, la estimación ya usa `openai/gpt-6-luna`. La reformulación y el puente siguen con `xiaomi/mimo-v2.6-pro`,
y son la mayor parte del costo de una pregunta nueva: ~USD 0,008 de ~0,009.
- **La pregunta:** ¿hace Luna esas dos tareas tan bien como mimo, medido con las mismas pruebas que validaron a mimo?
- **Si las dos pasan,** una pregunta nueva bajaría a unos USD 0,003.

## 2. Parte 1 — la reformulación, con su validación

- **Las mismas 24 preguntas** de `reformular.PRUEBA` (`REFORMULACION_SPECIFICATION.md` §3): 8 del catálogo,
  10 nuevas y 6 fuera de alcance.
- **Mismas instrucciones y misma lectura:** `reformular.SISTEMA`, `prompt` y `parsear`, a temperatura 0. Solo cambia
  el modelo.
- **La misma regla, R1 a R4** (`reformular.evaluar`):
  - R1: alcance correcto en ≥ 20 de 24;
  - R2: código correcto en ≥ 6 de 8;
  - R3: fuera de alcance detectadas en ≥ 5 de 6, ninguna como catálogo;
  - R4: respuesta válida en ≥ 23 de 24.
- **Referencia:** mimo sacó 24 de 24 (`REFORMULACION_RESULTS.md`).

## 3. Parte 2 — la reformulación, por lo que le hace a la estimación

La parte A de `NIVEL_ACUERDO_REDACCION` mostró que la reformulación puede cambiar el sentido de una pregunta y
mover la estimación. Por eso no basta con R1 a R4: se mide también lo que pasa después.
- **Objetivos:** las mismas 95 guardadas.
- **Flujo con Luna en la reformulación:**
  - se reformula cada pregunta con Luna (`reformular.reformular`, modelo Luna);
  - si el alcance es `nueva`, se estima con `Motor.estimar`, que ya usa Luna, con h = 23,4.
- **Comparación:** con el flujo con mimo en la reformulación, es decir, la parte A con Luna en la estimación (enmienda 2).
  Se compara sobre las preguntas que quedan como `nueva` y con estimación **en los dos flujos**.
- **Regla.** La reformulación con Luna no hace peor la estimación si se cumplen las dos condiciones:
  1. EAM con Luna ≤ EAM con mimo + 0,5;
  2. acierto del lado con Luna ≥ con mimo − 5 puntos.
- **Se reporta, sin regla:**
  - cuántas quedan `nueva`, `catalogo` o `fuera` con cada modelo;
  - en cuántas coincide la llamada («sí», «no» o «dividida»);
  - la cobertura del rango.
- **Lo que se sabe antes de correr.** El resultado de la columna con mimo (la parte A) se conocerá antes de correr
  esta parte. La regla ya queda fija aquí, y no se ajusta después.

## 4. Parte 3 — el puente, con su validación

**La prueba de `PUENTE_SIN_BASE_SPECIFICATION.md`, con Luna:**
- el prompt v2 que usa la página, 3 repeticiones;
- las 30 preguntas (clases A, B y C) y la regresión de las 12 preguntas escondidas;
- `puente_sin_base.main`, con el modelo como parámetro y la salida en una carpeta aparte.

**La regla son las condiciones que pasó mimo y que sostienen lo que la página muestra hoy:**
- **R1:** dice «sin base» en ≤ 1 de las 12 escondidas;
- **R2:** ordena a las personas mejor que el azar (p95) y que la demografía en ≥ 9 de las 12;
- **P2:** dice «sin base» en ≤ 1 de las 10 de clase A.

Se reporta además P1 (las C), que mimo no pasó (5 de 10) y que hoy no se usa en la página. Referencia: mimo pasó R1
con 0 de 12, R2 con 12 de 12 y P2 con 0 de 10.

## 5. Decisión

**Cada pieza por separado:**
- **la reformulación** pasa a Luna si cumple la parte 1 **y** la parte 2;
- **el puente** pasa a Luna si cumple la parte 3.

**Si una no cumple, se queda con mimo.** Cualquier cambio se le propone a Daniel con las cifras de los dos modelos, y
va como DI-CO en `motor.py` (o en `reformular.py`).

## 6. Predicciones (escritas antes de llamar)

- **PL1.** La reformulación con Luna cumple R1 a R4.
- **PL2.** La reformulación con Luna no hace peor la estimación: cumple la parte 2.
- **PL3.** El puente con Luna cumple R1, R2 y P2.
- **PL4.** Luna dice «sin base» en más preguntas C que mimo (más de 5 de 10).

## 7. Gasto

| Parte | Llamadas | Costo estimado |
|---|---|---|
| 1 | 24 | ~USD 0,02 |
| 2 | 95 reformulaciones y ~85 estimaciones | ~USD 0,20 |
| 3 | 126 | ~USD 0,07 |

- **Total: ~USD 0,30, con tope de USD 0,75.**
- **Antes de correr,** una llamada de prueba de la reformulación, cuyo costo se le confirma a Daniel.
- **El código se detiene solo** al llegar al tope o si el servicio falla.

## 8. Código

- **Orquestador:** `src/experiments/luna_pagina.py`.
- **Cambio en `puente_sin_base.py`:** se le agregan `--modelo` y la carpeta de salida, sin cambiar lo que ya hace por
  defecto.
- **Pruebas:** `tests/test_luna_pagina.py`.
- **Resultados:** `LUNA_PAGINA_RESULTS.md`, contra este pre-registro.
