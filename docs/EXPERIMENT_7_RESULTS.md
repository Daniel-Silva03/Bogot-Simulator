# EXPERIMENTO 7 — Resultados

Proyecto: Bogotá Social Simulator
Versión: 1.0
Fecha: 17 de septiembre de 2026
Reporta contra: `claude/EXPERIMENT_7_SPECIFICATION.md` (pre-registrada antes de correr)
Código: `src/experiments/experimento7.py`
Salidas: `data/processed/exp7/` — 1.224 corridas (612 por objetivo)

---

## 1. Veredicto: dos de seis predicciones se cumplen, y la que falla se deshace en un control

| | Predicción | Objetivo A | Objetivo B |
|---|---|---|---|
| **T1** — algún mecanismo reproduce el perfil de dispersión | FALLA para todos | *"pasa"* — **pero el criterio está roto**, ver §5 | **FALLA** (0 de 594) |
| **T2** — el baseline acierta media y sd | PASA por construcción | **PASA** (2·10⁻¹⁵ y 9·10⁻⁷) | **PASA** |
| **T3** — ningún mecanismo le gana al baseline · *la decisiva* | PASA | **FALLA** (−8,8 %) | **FALLA** (−8,8 %) |
| **T4** — el objetivo B es más difícil | PASA | **FALLA** — B es *más fácil* (4,46× el piso contra 5,61×) | |
| **T5** — el orden de mérito NO coincide entre A y B | PASA (no coincide) | **FALLA** — coincide casi exactamente (Spearman **0,90**) | |
| **T6** — la población arranca cerca del piso | PASA | **PASA** (0,91×) | **PASA** (1,52×) |

**T3 falló en los dos objetivos: los mecanismos le ganan al baseline duro por 8,8 %.** Habría sido el primer resultado claramente a favor del ABM en todo el proyecto.

**No lo es.** El control post-hoc de §4 lo desarma: **ruido gaussiano puro, sin red y con un solo parámetro, le gana a los mecanismos en los dos objetivos.**

## 2. Qué se midió

Nueve olas anuales de la EPC de Bogotá Cómo Vamos, base 2014.

| Objetivo | Qué es | Transiciones | Piso de ruido | Cobertura |
|---|---|---|---|---|
| **A** | `GG3`, gestión del alcalde, escala 1-5 | 8 | 0,4323 | 95 % → 81 % |
| **B** | \(d_i = GG3_i - CC5_i\), diferencia individual, escala −4 a +4 | 7 | 0,4537 | 72 % → 71 % |

Contra las **cuatro** transiciones de la ECP con las que se cerraron los Experimentos 3 a 6. Es el doble de puntos, y por primera vez con un objetivo limpio de estilo de respuesta individual.

## 3. Lo que salió: el orden de mérito, idéntico en los dos objetivos

| Familia | A (8 transiciones) | B (7 transiciones) |
|---|---|---|
| **Cognición motivada** | **2,4260** | **2,0247** |
| Friedkin-Johnsen | 2,5091 | 2,0322 |
| `traslación+u+γ` *(baseline duro)* | 2,6590 | 2,2211 |
| Traslación pura | 3,0215 | 2,8856 |
| Contracción de γ fijo | 3,1893 | 2,5281 |

Y el mismo modelo gana los dos, con casi los mismos parámetros: `cm α=0,3 λ=0,5 k=2,0`, con ρ=0,9 en A y ρ=1,0 en B.

**T5 predecía que el orden NO se conservaría, y se conserva** (Spearman 0,90). Lo registré con confianza baja diciendo que, si coincidía, sería "la señal más fuerte de que el ranking mide algo del modelo y no del objetivo". Coincidió. Y §4 dice **qué** del modelo mide.

La ventaja tampoco viene de un solo año: en A el mecanismo gana en 6 de 8 años, en B en 6 de 7.

## 4. El control que deshace el resultado

El baseline es una transformación **afín**: mueve los cinco picos enteros de la población fuera de la grilla 1-5 y los deja ahí. Cualquier modelo que **difumine** los picos va a ajustar mejor contra una distribución observada que sí vive en los enteros. Cognición motivada difumina. Friedkin-Johnsen difumina.

Así que se probó lo mínimo que también difumina: **el mismo baseline más ruido gaussiano, sin red, sin mecanismo, con un solo parámetro σ.**

| | Objetivo A | Objetivo B |
|---|---|---|
| `traslación+u+γ` | 2,6590 | 2,2211 |
| Mejor mecanismo (33 modelos, 5 parámetros) | 2,4260 | 2,0247 |
| **`traslación+u+γ+ruido`, σ=0,2–0,3** | **2,3136** | **1,9183** |

**El ruido gana.** Le saca 4,6 % al mejor mecanismo en A y 5,3 % en B, con un parámetro contra cinco y sin tocar la red. Y le gana en todo el rango σ ∈ [0,05 · 0,8]: no es un punto afortunado del barrido, es una meseta.

Dispersión entre semillas del control: 0,015–0,023. Las diferencias de la tabla están muy por encima.

> **La ventaja del 8,8 % de los mecanismos no era influencia social. Era suavizado.** Lo que faltaba no era un mecanismo: era un término de dispersión en el baseline.

Eso explica T5 sin misterio: el orden de mérito coincide entre los dos objetivos porque está ordenando modelos por **cuánto difuminan**, que es una propiedad del modelo y no del fenómeno.

## 5. T1 pasó en A por un defecto de mi criterio, y hay que decirlo

El criterio pre-registrado era: acertar el **signo** del cambio de dispersión en ≥6 de los 8 tramos.

Los signos observados en A son `[− − + − + − − −]`: **seis de ocho son negativos.** Un modelo que contraiga *siempre* acierta 6 de 8 sin hacer nada. Friedkin-Johnsen contrae siempre, así que el **100 %** de sus corridas "pasa" — y el mejor mecanismo acierta exactamente 6, es decir, **ninguno le gana a la estrategia trivial.**

En B los signos están balanceados (`[− − + + − + −]`, 4 y 3) y el criterio funciona: **ninguna corrida llega a 6 de 7**, y el máximo con mecanismo es 5.

**El criterio era malo y el objetivo B lo demuestra.** La lectura correcta de T1 es la de B: **ningún mecanismo con parámetros fijos reproduce el perfil de dispersión**, consistente con los Experimentos 5 y 6. Queda como corrección de método: un criterio de conteo de signos necesita que los signos estén balanceados, o exige superar la línea base trivial explícitamente.

## 6. T4 falló, y en la dirección que la especificación decía perseguir

Predije que el objetivo limpio sería **más difícil** para los mecanismos. Es **más fácil**: 4,46 veces el piso contra 5,61 en A. La especificación decía que si salía al revés "sería el primer resultado claramente a favor del ABM, y habría que perseguirlo".

Se persiguió, y es §4: en B el ruido también gana. El objetivo B es más fácil para **todos** los modelos, mecanismos y controles por igual — es una propiedad del objetivo, no del ABM.

## 7. Qué queda establecido

1. **Con ocho transiciones, sigue sin haber mecanismo social identificable.** Ya no es un problema de poder: es el doble de puntos que en los Experimentos 3 a 6, en dos objetivos distintos, y el resultado es el mismo.
2. **El baseline estaba mal especificado, y ese es el hallazgo aprovechable.** Nivel y dispersión no alcanzan: hace falta un tercer término que controle **cuán difusa** es la distribución. Es exactamente lo que `claude/ANALISIS_RESIDUO.md` había concluido por otra vía —tres perillas, no dos— y ahora aparece por segunda vez, desde otros datos.
3. **Cognición motivada sigue siendo la mejor de las tres familias**, en los dos objetivos y con los mismos parámetros. Eso es consistencia real y merece anotarse. Pero pierde contra un parámetro de ruido, así que lo que aporta es difuminado, no dinámica.
4. **Nada reproduce los datos.** El mejor de todos queda a 4,2–5,4 veces el piso de ruido muestral. La distancia sigue siendo enorme.
5. **El objetivo B funciona como se esperaba de un control**: elimina el componente común (el salto conjunto de 2017→2019 pasa de +0,44 a −0,001) y da un veredicto concordante con A. Que los dos objetivos coincidan es lo que le da fuerza a este experimento.

## 8. Qué sigue

**Para el motor de escenarios.** Las tres perillas quedan confirmadas desde dos fuentes independientes: **nivel, dispersión y difusión de la forma**. La tercera no es "forma libre": aquí se comporta como un ancho de difuminado de un parámetro. Vale la pena probar si la relación forma-nivel de `claude/ANALISIS_RESIDUO.md` §3 y este ancho son la misma perilla vista de dos maneras.

**Lo que NO hay que hacer.** Reportar el 8,8 % como aporte del ABM. Estuvo a un control de distancia de entrar al proyecto como el primer resultado positivo.

**Lo que queda abierto.** A20 (el constructo) sigue sin decidirse, y este experimento le da un insumo: los dos objetivos de la EPC dan el mismo veredicto que la ECP, con constructos distintos. Eso favorece la opción (c) —tratarlos como dos casos del mismo laboratorio— porque el resultado replica.

---

*Reportado contra el pre-registro. Cuatro de seis predicciones fallaron, una "pasó" por un defecto del criterio que el segundo objetivo dejó a la vista, y el control post-hoc de §4 se añadió después de ver los resultados y queda etiquetado como tal. Su efecto es **destruir** el único resultado favorable del experimento, no reforzarlo.*
