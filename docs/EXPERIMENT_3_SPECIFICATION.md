# EXPERIMENT 3 — Validación de la dinámica (nivel 3)

Proyecto: Bogotá Social Simulator
Versión: 0.1 — especificación previa a la ejecución
Fecha: 16 de septiembre de 2026
Depende de: `claude/DATA_INVENTORY.md` §10 · `claude/EXPERIMENT_1_SPECIFICATION.md` §5 · `MODEL_SPECIFICATION.md` · `RESEARCH.md` §29

---

## 0. Por qué existe este documento, y por qué ahora

`EXPERIMENT_1_SPECIFICATION.md` §5 declaró el nivel 3 **bloqueado**: validar dinámica exige la misma variable medida en dos momentos separados, y el donante de la Veeduría resultó ser una recolección continua, no dos olas. Con eso quedaban bloqueados también los niveles 4 y 5, y con ellos el criterio de éxito del MVP (`PROJECT_CONTEXT.md` §37).

La ECP del DANE desbloquea el nivel 3: la misma pregunta de confianza institucional, mismo código de variable, misma escala 1–5, en **2017, 2019, 2021 y 2023**, con Bogotá identificable y factores de expansión. Cuatro puntos, no dos.

Este documento fija el diseño **antes** de correr nada. Esa es toda la gracia: si las predicciones se escriben después de ver el ajuste, no son predicciones. Las cifras que aparecen abajo salen de análisis ya hechos sobre los datos observados y sobre el comportamiento analítico del modelo, no de corridas de ajuste.

---

## 1. Lo que hay, y lo que sigue sin haber

### 1.1 Cuatro cortes transversales, no un panel

La ECP entrevista una muestra distinta cada año. **No hay transiciones individuales.** Esto importa más de lo que parece: Gestefeld & Lorenz (2023), que es la referencia de calibración que `RESEARCH.md` §27 adoptó, calibran contra distribuciones **y** transiciones, y sostienen que las distribuciones solas son un criterio débil porque muchos mecanismos distintos producen la misma distribución agregada.

Entonces el Experimento 3 valida contra **distribuciones repetidas**, que es el nivel de evidencia disponible. No es el estándar completo de Gestefeld & Lorenz y este documento no va a fingir que lo es. Lo que sí permite es **falsear**: un modelo que no puede producir la secuencia observada de distribuciones queda descartado sin necesidad de transiciones.

### 1.2 Lo que hay que reproducir

Índice de confianza por persona = media de los 13 ítems válidos de `P5263S*` (mínimo 7 de 13), escala 1–5, código 99 excluido. Ponderado por `FEX_P`.

| Año | n | media | sd | bimodalidad (Sarle) | % < 2,0 | % > 3,5 |
|---|---|---|---|---|---|---|
| 2017 | 5.046 | 2,503 | 0,934 | 0,420 | 27,4 % | 14,2 % |
| 2019 | 5.298 | 2,362 | 0,903 | 0,405 | 34,3 % | 9,7 % |
| 2021 | 4.858 | 2,245 | 0,897 | 0,447 | 37,1 % | 7,1 % |
| 2023 | 4.238 | 2,430 | **0,764** | 0,349 | 23,2 % | **5,3 %** |

Cuatro rasgos, y hay que separarlos porque el modelo se comporta distinto frente a cada uno:

1. **La media hace una V**: −0,258 hasta 2021 y +0,185 de vuelta. Los 13 ítems tocan mínimo en 2021, los trece, sin excepción.
2. **La dispersión se contrae** 18,2 % de punta a punta, y de forma casi toda concentrada en el último tramo.
3. **Nunca hay bimodalidad** (0,35–0,45, contra el umbral de 5/9 ≈ 0,555).
4. **Las colas son asimétricas**: la de alta confianza se vacía de forma **monótona** (14,2 → 9,7 → 7,1 → 5,3), la de baja confianza hace la **V** (27,4 → 34,3 → 37,1 → 23,2).

### 1.3 El cambio observado no es recomposición demográfica

Amenaza obvia a la validez: cada ola es gente distinta, y Bogotá envejece y cambia. Si la V fuera composición y no opinión, el modelo no tendría nada que reproducir.

**Comprobado y descartado.** Estandarizando cada año a la composición de 2017 por celdas de edad (4) × sexo (2) × educación (3) × estrato (3) — 66 celdas pobladas, 98 % de la muestra de 2017 sobrevive a exigir las cuatro variables:

| Año | media cruda | media estandarizada a 2017 | parte composicional |
|---|---|---|---|
| 2017 | 2,5032 | 2,5032 | — |
| 2019 | 2,3630 | 2,3669 | −0,0040 |
| 2021 | 2,2449 | 2,2331 | +0,0118 |
| 2023 | 2,4303 | 2,4135 | +0,0168 |

La composición explica **como máximo 0,017 de un recorrido de 0,258** — menos del 7 %. El resto es cambio de opinión dentro de composiciones comparables. Hay algo real que reproducir.

---

## 2. El problema del reloj, y cómo se resuelve sin hacer trampa

El modelo no tiene tiempo. Un paso de Friedkin-Johnsen no es un mes ni un año; es una iteración. Para comparar una trayectoria simulada contra cuatro años observados hace falta un mapeo pasos → años, y ese mapeo es un parámetro libre. Ajustarlo hasta que la curva calce es exactamente la validación circular que `RESEARCH.md` §30 quiere evitar.

**La salida es probar propiedades invariantes a la reparametrización temporal.**

Una reparametrización monótona del tiempo puede estirar o comprimir una trayectoria, pero **no puede cambiar su forma cualitativa**. En particular: si la trayectoria simulada de una cantidad es monótona en el tiempo, ninguna elección de "cuántos pasos son un año" la vuelve no monótona. Y la media observada **no es monótona**.

Esto convierte P3 (abajo) en una prueba que el modelo pasa o falla sin ningún parámetro libre. Es la prueba central del experimento.

Para las predicciones que sí dependen de la escala temporal, el mapeo se trata como parámetro libre **explícito y único**: se busca el mejor ajuste alcanzable sobre todos los mapeos monótonos posibles, y se reporta como techo, no como resultado. Si el modelo falla en su mejor caso, falla.

---

## 3. Experimento 3A — Población inicializada en 2017

### 3.1 Qué cambia respecto de la población actual

`poblacion_sintetica_v2.csv` tiene `opinion_t0` traído del donante de la Veeduría (campo 2024-12 → 2025-02). Para el Experimento 3 el estado inicial tiene que ser **2017**, o no hay nada que proyectar hacia adelante.

Se reconstruye la población con el mismo pipeline (loader → hot-deck → build_agents) cambiando **solo el donante**: la submuestra de Bogotá de la ECP 2017 (n = 5.137).

### 3.2 El intercambio que esto implica, dicho de frente

| | Donante Veeduría | Donante ECP 2017 |
|---|---|---|
| localidad | ✅ | ❌ (la ECP solo llega a `REGION = Bogotá`) |
| estrato | ❌ (A15) | ✅ `P4031S1A1`, 0–6 |
| edad, sexo, educación | ✅ | ✅ |
| separación temporal | ninguna | 4 puntos, 2017–2023 |

Se gana estrato —que cierra para este experimento el vacío de A15— y se pierde localidad. La pérdida es real y acota el alcance: **el Experimento 3 no valida nada territorial.** Eso sigue dependiendo de Multipropósito y del marginal de `DATA_INVENTORY.md` §11. Lo que el generador territorial aporta acá es una estructura de red alternativa, no un objetivo de validación.

Consecuencia operativa: las variables de emparejamiento del hot-deck pasan a ser edad × sexo × educación × estrato, y la escalera de relajación se reconstruye sobre esas cuatro.

### 3.3 Criterio de aceptación de 3A (nivel 2 para este donante)

3A es prerrequisito, no hallazgo. Se acepta si la distribución de `opinion_t0` de los 1.000 agentes reproduce la distribución observada ponderada de 2017 con **Wasserstein-1 < 0,10** en la escala 1–5 (≈ 2,5 % del rango). Si 3A no pasa, 3B no significa nada y hay que arreglar el matching antes de seguir.

Se reporta además el aplanamiento conocido del hot-deck (desempate determinista, `POPULATION_SPECIFICATION.md` §8): si el estado inicial simulado tiene menos dispersión que el observado, **parte de la contracción que P2 vaya a medir ya estaba ahí antes de correr el modelo**, y hay que descontarla.

---

## 4. Experimento 3B — Las predicciones, fijadas de antemano

Friedkin-Johnsen es \(a(t+1) = \Phi W a(t) + (I - \Phi) a(0)\), con punto fijo \(a^* = (I - \Phi W)^{-1}(I - \Phi)a(0)\). De ahí salen predicciones que no son opinables.

Se verificaron numéricamente sobre la población v2 con un estado inicial extraído de la ECP 2017, para las tres redes y φ ∈ {0,3 · 0,5 · 0,7 · 0,9}:

| Red | Δmedia (máx sobre φ) | Contracción de sd en el punto fijo |
|---|---|---|
| aleatoria | −0,006 | 30 % → 88 % |
| homofílica | −0,004 | 25 % → 59 % |
| territorial | −0,016 | 29 % → 86 % |

### P1 — El nivel. **Predicción: FALLA.**

FJ conserva la media casi exactamente: el mayor desplazamiento sobre 12 combinaciones de red × φ es **0,016**. Lo observado recorre **0,258**. Son **16 veces** más.

*Criterio:* falla si |Δmedia simulada| < 0,05 mientras |Δmedia observada| = 0,258. Con los números de arriba, falla por un orden de magnitud, no por poco.

### P2 — La dispersión. **Predicción: PASA**, con el mapeo temporal como parámetro libre.

Lo observado se contrae 18,2 %. El punto fijo de FJ contrae entre 25 % y 88 %. O sea que **lo observado está por debajo incluso del punto fijo más suave**, y FJ puede reproducirlo deteniéndose antes de converger. Eso es ajustar el reloj, no un acierto estructural — pero es una contracción del signo correcto y de magnitud alcanzable, que es más de lo que se puede decir de P1.

*Criterio:* pasa si existe un mapeo monótono pasos → años bajo el cual el error de sd en los tres años objetivo queda por debajo de 0,05.

### P3 — La no monotonía. **Predicción: FALLA. Es la prueba central.**

La media simulada bajo FJ es monótona en el tiempo (converge a \(a^*\) sin sobrepasarlo). La media observada **no lo es**: baja hasta 2021 y sube. Ninguna reparametrización monótona del tiempo reconcilia una trayectoria monótona con una que no lo es.

*Criterio:* falla si la media observada tiene un mínimo interior (lo tiene, en 2021) y la simulada no lo tiene bajo **ninguna** combinación de red × φ × número de pasos. Sin parámetros libres que ajustar.

### P4 — Las colas. **Predicción: FALLA en la cola baja.**

FJ contrae hacia el consenso, así que predice que **ambas** colas se vacíen de forma monótona. Lo observado: la cola alta sí (14,2 → 5,3, monótona), la baja no (27,4 → 37,1 → 23,2).

*Criterio:* falla si la masa simulada bajo 2,0 es monótona decreciente y la observada tiene un máximo interior.

### P5 — La bimodalidad. **Predicción: PASA.**

Ni FJ ni DeGroot producen bimodalidad (Experimento 2: cero corridas bimodales en 9.600). Lo observado tampoco es bimodal en ninguno de los cuatro años (0,35–0,45).

Esto **reencuadra el resultado del Experimento 2**: la incapacidad de fragmentar se había anotado como una limitación del modelo, y contra estos datos es un acierto. Bogotá, en confianza institucional y en este periodo, tampoco se fragmentó.

---

## 5. Baselines obligatorios

`PROJECT_CONTEXT.md` A11 exige DeGroot como baseline. Se agrega uno más exigente y más incómodo:

| Baseline | Qué hace | Por qué está |
|---|---|---|
| **B0 — congelado** | `opinion_t0` sin tocar, para todos los años | El modelo tiene que ganarle a *no hacer nada*. Si no le gana, la dinámica no aporta. |
| **B1 — DeGroot** | consenso puro, sin anclaje | A11 |
| **B2 — ruido** | perturbación aleatoria de la misma magnitud que el cambio observado | Controla que el ajuste no venga de mover cosas al azar |
| **M — Friedkin-Johnsen** | el modelo candidato | |

**Predicción explícita y desagradable:** FJ probablemente **pierde contra B0**. El cambio observado está sobre todo en la media, que FJ no mueve, mientras que FJ sí contrae la varianza, alejándose de la distribución observada en la única dimensión en la que se mueve. Si esto se confirma, es el resultado más importante del experimento y hay que reportarlo como tal.

---

## 6. Métricas

Por año objetivo (2019, 2021, 2023), simulado contra observado ponderado:

- **Wasserstein-1** — métrica principal, compara distribuciones completas y está en unidades de la escala.
- **Error de media** y **error de sd** por separado — porque el punto del experimento es mostrar *dónde* falla, no solo cuánto.
- **KS** y **distancia de variación total** — secundarias, para robustez.
- **Forma:** signo de la primera diferencia de la media y de la masa bajo 2,0 en cada tramo (2017→2019→2021→2023). Es lo que evalúa P3 y P4, y es una comparación de signos, no de magnitudes.

Todas ya están en `src/experiments/metrics.py` salvo las de forma.

**Incertidumbre:** `RESEARCH.md` §32 exige distribución de resultados, no un número. Cada combinación corre con múltiples semillas y se reporta mediana e intervalo intercuartílico. Una diferencia entre modelos solo cuenta si supera la dispersión entre corridas del mismo modelo — el mismo criterio que usó el Experimento 2.

---

## 7. Diseño del barrido

| Factor | Valores | n |
|---|---|---|
| red | aleatoria, homofílica, territorial (h = 20) | 3 |
| k̄ | 4, 8, 16 | 3 |
| modelo | FJ (φ = 0,3 / 0,5 / 0,7 / 0,9), DeGroot, congelado, ruido | 7 |
| semillas | 20 | 20 |

**1.260 corridas.** Cada una guarda la trayectoria de media, sd y masa de colas paso a paso, para poder evaluar cualquier mapeo temporal sin volver a correr. Órdenes de magnitud por debajo del Experimento 2 (9.600), porque acá lo que se barre es el ajuste, no la estructura.

φ se barre en vez de calibrarse: calibrar φ contra los mismos datos con los que se valida sería circular. Si el mejor φ resulta ser un extremo del rango, se dice.

---

## 8. Criterio de éxito, fijado antes de correr

El experimento es **exitoso como experimento** si produce un veredicto claro sobre cada predicción, gane o pierda el modelo. No es un experimento cuyo éxito sea que FJ ajuste.

**Resultado esperado:** P2 y P5 pasan, P1, P3 y P4 fallan. Es decir: **el modelo acierta la forma de la distribución y falla el nivel.** Si eso se confirma, el diagnóstico queda localizado con precisión — a FJ le falta un término que mueva el centro de masa, no un mecanismo de influencia distinto.

**Qué haría falsa esta especificación:** que FJ mueva la media más de 0,05 en alguna configuración, o que produzca un mínimo interior. Cualquiera de las dos invalidaría el razonamiento analítico de §4 y obligaría a reescribirlo antes de interpretar nada.

---

## 9. Qué sigue si el resultado es el esperado

**Fuera del alcance de este experimento**, anotado para no improvisarlo después con los resultados a la vista:

Un término exógeno \(s(t)\) —un shock, una señal mediática, un componente común— convertiría a FJ en \(a(t+1) = \Phi W a(t) + (I-\Phi)(a(0) + s(t))\). Eso sí puede producir la V. Pero introduce una tentación seria: \(s(t)\) con suficientes grados de libertad reproduce **cualquier** trayectoria, incluida una generada al azar, y el ajuste dejaría de ser evidencia de nada.

Si se llega ahí, la regla se fija ahora, antes de tener los resultados: \(s(t)\) tiene que estar **anclado a una serie externa medida de forma independiente** (un indicador de coyuntura, no un parámetro ajustado), y el modelo con \(s(t)\) tiene que validarse en un periodo distinto del usado para fijarlo — el backtesting de `RESEARCH.md` §30. Con cuatro puntos temporales eso es apretado y quizá no alcance; también hay que decirlo.

---

## 10. Amenazas a la validez

1. **No-respuesta en 2023.** Salta de ~2 % a 5,6 %. Parte del rebote de 2023 puede ser gente que dejó de contestar, no gente que confía más. Se analiza quién se cayó antes de leer 2023 como recuperación. Si el rebote sobrevive a corregir por no-respuesta, la V es más sólida; si no, P3 se apoya sobre todo en el tramo de bajada.
2. **Recomposición demográfica.** Descartada en §1.3 (≤ 7 % del cambio).
3. **Aplanamiento del hot-deck.** El desempate determinista reduce la variedad de `opinion_t0`. Se mide en 3A y se descuenta de P2.
4. **13 ítems, no 15.** `P5263S6` y `P5263S12` vienen vacíos en los cuatro años. El índice es consistente entre años, pero no es "los 15 actores".
5. **Los ítems no tienen nombre.** Sin el cuestionario no se sabe qué institución es cada serie. **No afecta a este experimento**: el 81 % de la variación entre años cae en un único componente con las 13 cargas del mismo signo, así que el objetivo dinámico es un número por año. Sí impide interpretar *de qué* institución habla el resultado.
6. **Distribuciones sin transiciones.** §1.1. El experimento puede falsear un modelo pero no puede confirmar un mecanismo.
7. **n = 1.000 agentes.** Ruido de muestreo en las colas. Si los intervalos entre semillas se solapan demasiado como para resolver P4, se repite con n = 10.000 antes de concluir.

---

*Especificación cerrada antes de la ejecución. Cualquier cambio posterior a correr 3B se anota con fecha y motivo, o los criterios de §4 dejan de valer.*
