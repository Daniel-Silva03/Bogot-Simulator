# EXPERIMENTO 5 — Especificación pre-registrada

Proyecto: Bogotá Social Simulator
Versión: 1.0
Fecha: 16 de septiembre de 2026
Estado: **pre-registro — escrito y guardado antes de correr el barrido**
Origen: `claude/DIAGNOSTICO_Y_ALTERNATIVAS.md` §4 (fallo 8) y `claude/EXPERIMENT_4_RESULTS.md` §9
Código: `src/opinion/cognicion_motivada.py`, `src/experiments/experimento5.py`

---

## 1. La pregunta

`MODEL_SPECIFICATION.md` §4 designó el **marco de cognición motivada** (Lorenz, Neumann & Schröder 2021; calibrado por Gestefeld & Lorenz 2023) como modelo objetivo de la fase de calibración, antes de que existiera un solo experimento, por ser el único de los cinco evaluados con ajuste publicado contra datos reales: 1.235 distribuciones de confianza institucional de la ESS con mediana R² > 0,8, y transiciones individuales del Swiss Household Panel.

**Nunca se implementó.** El prototipo llegó hasta Friedkin-Johnsen y DeGroot. Por eso la conclusión "ninguna familia endógena reproduce estos datos" no estaba respaldada.

El Experimento 4 dejó una tarea concreta y medible para esta familia:

> **Lo observado se contrae tarde** — −4,2 % / 0,0 % / −13,8 % entre casos completos. Friedkin-Johnsen converge geométricamente, así que su contracción es **anticipada y decelerante**, la forma opuesta, y la heterogeneidad de φ la anticipa todavía más. ¿Puede cognición motivada producir contracción que **no empiece** hasta el tercer periodo?

Hay una razón mecanística para pensar que sí, y es lo que hace que valga la pena correrlo: mientras la distribución es ancha, la mayoría de los pares está lejos y el kernel los apaga, así que casi no pasa nada; a medida que parte de la masa entra dentro de λ, la influencia se enciende y la contracción **acelera**. Es realimentación positiva, no una exponencial decreciente.

## 2. El modelo

$$\Delta a_i = \underbrace{\frac{\lambda^k}{\lambda^k + |a_j - a_i|^k}}_{\text{cognición motivada}} \cdot\; \alpha \,(a_j - \rho\, a_i)$$

más, con probabilidad θ por paso, retorno idiosincrático al anclaje a(0). Interacción por pares sobre la red; actualización simultánea; escala centrada en 3,0 (punto medio de 1–5).

**Una corrección ya registrada en el código.** Escribí primero que ρ < 1 "modera"; es al revés. Si dos agentes ya piensan igual, Δ = peso·α·c·(1−ρ), así que **ρ < 1 aleja del centro (refuerzo)**, ρ = 1 es asimilación pura y ρ > 1 modera. Lo atrapó una aserción del test antes de llegar a ningún resultado. El signo de ρ decide si el modelo polariza o modera, así que no es un detalle de parametrización.

## 3. El diseño

Idéntico al Experimento 4, para que los números sean directamente comparables: se ajusta un escalar \(u_k\) por periodo para que la **media simulada iguale exactamente la observada** en 2019, 2021 y 2023. El nivel queda fuera de discusión y todo se juega en la forma.

| Dimensión | Valores |
|---|---|
| α (fuerza de cambio) | 0,1 · 0,3 · 0,5 |
| λ (distancia de media influencia) | 0,3 · 0,5 · 0,8 |
| k (nitidez del kernel) | 2 · 3 · 6 |
| ρ (asimilación) | 1,0 · 1,1 |
| θ (retorno idiosincrático) | 0,0 · 0,02 |
| Pasos por periodo \(S\) | 5 · 15 |
| Red | aleatoria · homofílica · territorial (h=20) |
| Grado \(\bar{k}\) | 5 (el valor medido, D15) |
| Semillas | 3 |

**Referencias del Experimento 4, corridas de nuevo en la misma malla:** traslación pura, contracción uniforme (γ = 0,02 y 0,05) y Friedkin-Johnsen (φ = 0,08 y 0,1).

### Un sesgo del diseño que hay que declarar por adelantado

Cognición motivada tiene **cinco parámetros** barridos; Friedkin-Johnsen tiene uno y la contracción uniforme tiene uno. Quedarse con el mejor de cada malla favorece mecánicamente al modelo con más parámetros. Por eso:

1. Se reporta **el mejor y la mediana** de cada familia, no solo el mejor.
2. El criterio decisivo es **R2**, que es **cualitativo** (¿la contracción llega tarde?) y no se compra con más parámetros: FJ no lo logra con ningún valor de φ, porque es una propiedad analítica de la familia, no de su calibración.

### Criterios corregidos respecto del Experimento 4

Dos criterios de aquel pre-registro estaban mal escritos, y se arreglan aquí:

- **Perfil tardío** ahora exige magnitud *y* proporción: la contracción del tercer tramo debe superar a cada una de las dos anteriores **por al menos 3 puntos porcentuales**, y eso debe ocurrir en **al menos el 5 % de las corridas** — no en una de 3.960.
- **Bimodalidad** solo se evalúa en corridas con **sd final ≥ 0,3**. El coeficiente de Sarle sobre una distribución colapsada no mide bimodalidad.

## 4. Predicciones

### R1 — Cognición motivada le gana a Friedkin-Johnsen en W1
**Predicción: PASA.** *Confianza: alta, y con poco mérito* — cinco parámetros contra uno. Si fallara sería una señal seria de que el modelo está mal implementado, más que un resultado sobre Bogotá. Lo informativo será el **margen** y la **mediana**, no el hecho.

### R2 — Produce contracción tardía · **el criterio decisivo**
**Predicción: PASA**, en al menos el 5 % de las corridas, con el criterio corregido. *Confianza: media-alta.* Una prueba exploratoria sobre una configuración (α=0,3 · λ=0,5 · k=3 · ρ=1 · θ=0, sin forzamiento) dio **+13,8 % / +15,8 % / +19,9 %**: contracción que acelera monótonamente. Queda por ver si sobrevive con el forzamiento puesto y en una fracción apreciable de la malla.

Si R2 pasa, es lo primero en todo el proyecto que reproduce un rasgo **cualitativo** de la trayectoria que ningún baseline puede producir por construcción.

### R3 — Le gana al control sin red (contracción uniforme)
**Predicción: PASA, por poco.** *Confianza: baja.* Es la pregunta que de verdad importa y la que menos sé. El kernel hace que la influencia dependa de la **distancia de opinión** entre pares concretos, algo que un encogimiento uniforme hacia la media no puede imitar. Pero el Experimento 4 ya mostró que en estos datos casi todo lo que hay que explicar es "traslación + encogimiento", y que la red aporta un 2,8 %. Espero un margen del mismo orden: **menos del 10 %**.

Si **falla**, la conclusión se endurece: ni siquiera el modelo con mejor evidencia publicada mejora sobre un encogimiento sin estructura social, y eso cierra la pregunta del mecanismo para esta variable con estos datos.

### R4 — No aparece bimodalidad espuria en las configuraciones que ajustan bien
**Predicción: PASA para las mejores, FALLA para una parte apreciable de la malla.** *Confianza: media.* Los kernels de este tipo fragmentan cuando λ es pequeño y α grande, y Bogotá **nunca se fragmentó** (bimodalidad observada 0,35–0,45, siempre bajo 0,555). Espero que **más del 10 % de la malla** supere el umbral, y que las cinco mejores configuraciones por W1 **no** lo superen. Registro las dos mitades por separado porque solo la segunda sería un problema para el modelo.

### R5 — El error de dispersión mejora sobre el 0,0453 del Experimento 4
**Predicción: PASA.** *Confianza: media.* Si R2 se cumple, el perfil correcto debería traer consigo un mejor ajuste de sd en los tres años, no solo en el último.

## 5. Qué significará cada resultado

| | Lectura |
|---|---|
| R2 pasa **y** R3 pasa | El mecanismo social aporta algo que ningún baseline sin estructura reproduce. Justifica el ABM para esta variable y abre la calibración formal. |
| R2 pasa, R3 falla | El **kernel** importa, la **red** no. Apuntaría a un modelo de campo medio con cognición motivada, sin grafo — más barato y más honesto que un ABM. |
| R2 falla | Ninguna de las tres familias disponibles reproduce el rasgo temporal. Se agota la vía endógena con los datos actuales y el camino queda en escenarios con supuestos explícitos. |
| R4 falla también en las mejores | El modelo compra ajuste fragmentando una población que no se fragmentó. Descalifica el ajuste, aunque los números de W1 sean buenos. |

**Lo que este experimento no puede decidir, otra vez:** siguen siendo **3 transiciones**. Un ajuste bueno significa "no descartado", nunca "identificado", y con cinco parámetros la advertencia pesa más que en el Experimento 4, no menos.

---

*Guardado en el proyecto antes de ejecutar el barrido. Los resultados se reportarán en `claude/EXPERIMENT_5_RESULTS.md` contra esta especificación, incluidas las predicciones que fallen.*
