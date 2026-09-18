# EXPERIMENTO 5 — Resultados

Proyecto: Bogotá Social Simulator
Versión: 1.0
Fecha: 16 de septiembre de 2026
Reporta contra: `claude/EXPERIMENT_5_SPECIFICATION.md` (pre-registrada antes de correr el barrido)
Código: `src/opinion/cognicion_motivada.py`, `src/experiments/experimento5.py`
Salidas: `data/processed/exp5/` — 2.034 corridas

---

## 1. Veredicto

| | Predicción | Resultado | |
|---|---|---|---|
| **R1** — le gana a Friedkin-Johnsen en W1 | PASA (confianza alta) | **FALLA** — 0,2811 contra 0,2652 | **fallida, y es el resultado** |
| **R2** — produce contracción tardía (≥5 % de corridas) | PASA | **FALLA por un pelo** — 4,53 % | fallida en la letra, matizada en el fondo (§3) |
| **R3** — le gana al control sin red | PASA por poco (confianza baja) | **FALLA** — pierde por 2,2 % | fallida |
| **R4** — sin bimodalidad espuria en las mejores | PASA en las mejores, falla en >10 % de la malla | **PASA** (0,398) y solo **4,4 %** fragmenta | acertada la primera mitad, fallida la segunda |
| **R5** — mejora el error de dispersión del Exp. 4 | PASA | **PASA** — 0,0343 contra 0,0453 | acertada |

**Tres de cinco fallan, y falla la que tenía confianza alta.**

## 2. R1 — el modelo con mejor evidencia publicada pierde con 108 configuraciones contra 2

| Familia | Mejor W1 total | Mediana | Configuraciones |
|---|---|---|---|
| **Friedkin-Johnsen** | **0,2652** | **0,2765** | 2 |
| Contracción uniforme (sin red) | 0,2750 | 0,7014 | 2 |
| **Cognición motivada** | **0,2811** | 0,4014 | **108** |
| Traslación pura | 0,4262 | 0,4262 | 1 |

Había predicho que ganaría, *"con poco mérito"*, porque barre cinco parámetros contra uno. Perdió igual. Y no por poco en la mediana: 0,4014 contra 0,2765, es decir que la configuración típica de cognición motivada es **bastante peor** que Friedkin-Johnsen con φ = 0,08.

Escribí en el pre-registro que un fallo de R1 sería *"una señal seria de que el modelo está mal implementado, más que un resultado sobre Bogotá"*. Revisado: el kernel, la fórmula de cambio y el signo de ρ están verificados contra valores calculados a mano, y el modelo hace exactamente lo que §3 muestra que hace. No es un error de implementación: **es que la libertad extra no compra ajuste en estos datos.**

## 3. R2 — el matiz que importa: la forma es alcanzable, la magnitud no

En la letra, R2 falla: 88 corridas tardías de 1.944 son el **4,53 %**, por debajo del 5 % pre-registrado. Con un umbral elegido antes de ver nada, eso es un fallo y así se cuenta.

Pero el fondo es más interesante que el umbral, en las dos direcciones.

**A favor del modelo:** es la **única familia que produce el perfil tardío, en absoluto**.

| Familia | Corridas con contracción tardía |
|---|---|
| Cognición motivada | **88 de 1.944** |
| Friedkin-Johnsen | **0 de 36** |
| Contracción uniforme | **0 de 36** |
| Traslación | 0 de 18 |

Y en el ajuste del **perfil** en sí —error cuadrático de los tres tramos de contracción contra los observados (0,0326 / 0,0066 / 0,1480)— cognición motivada es la mejor de las cuatro familias:

| Familia | Mejor error de perfil | Mediana |
|---|---|---|
| **Cognición motivada** | **0,00954** | 0,02021 |
| Friedkin-Johnsen | 0,01237 | 0,01324 |
| Contracción uniforme | 0,01473 | 0,11100 |
| Traslación | 0,02301 | 0,02301 |

**En contra del modelo, y esto es lo decisivo:** las corridas que producen la forma correcta son **las que peor ajustan**.

| | Mejor W1 total |
|---|---|
| Corridas **tardías** | **0,4993** |
| Corridas no tardías | 0,2811 |
| Friedkin-Johnsen | 0,2652 |

La mejor corrida tardía deja sd 2023 en **0,549** contra **0,764** observado, con tramos de −15,3 % / −17,6 % / −20,8 %. O sea: **el mecanismo consigue que la contracción acelere, pero solo contrayendo tres veces más de lo que hay que contraer.** La aceleración y la magnitud vienen pegadas y no se pueden separar con esta parametrización.

Eso es más informativo que el 4,53 %, y es peor para el modelo que el número del veredicto. Vale la pena decirlo así: el criterio falló por poco, pero el diagnóstico detrás falla por mucho.

**Qué activa el perfil tardío**, por si sirve más adelante:

| Parámetro | % de corridas tardías |
|---|---|
| k = 2 · 3 · 6 | 8 % · 5 % · **0 %** |
| θ = 0 · 0,02 | **8 %** · 1 % |
| ρ = 1,0 · 1,1 | 3 % · 6 % |
| S = 5 · 15 | 3 % · 6 % |

Dos lecturas contraintuitivas: el kernel **afilado** (k=6) no produce nunca el perfil —con λ pequeño, casi ningún par entra y no pasa nada en absoluto, así que no hay nada que acelerar— y el retorno idiosincrático θ **destruye** la aceleración (8 % → 1 %), porque tira constantemente hacia el anclaje y borra la realimentación.

## 4. R3 — pierde contra un encogimiento sin ninguna red

0,2811 contra 0,2750: **−2,2 %**. Predije que ganaría por poco, con confianza baja, y perdió por poco.

Es la tercera medición independiente que apunta igual. El Experimento 3 midió que la estructura de red casi no afecta el ajuste; el Experimento 4 cuantificó su aporte en 2,8 %; y ahora el modelo con mejor evidencia publicada, corriendo *sobre* esa red, tampoco supera a un encogimiento uniforme de un solo parámetro.

## 5. R4 y R5 — las dos que salieron bien

**R4 pasa, y mejor de lo esperado.** Predije que más del 10 % de la malla fragmentaría; fragmenta el **4,4 %** de las corridas evaluables (con la guarda de sd ≥ 0,3 que faltaba en el Experimento 4). Las cinco mejores configuraciones llegan a 0,398, por debajo del umbral de Sarle. El modelo **no** compra ajuste fragmentando una población que no se fragmentó.

**R5 pasa.** Mejor error de dispersión 0,0343, contra 0,0453 del Experimento 4. La mejor configuración (α=0,1 · λ=0,3 · k=2 · ρ=1,1 · θ=0,02) reproduce sd 0,930 / 0,871 / 0,807 contra 0,903 / 0,897 / 0,764 observados.

Nótese que esa configuración es de **α mínimo y λ mínimo**: el mejor cognición motivada es el que menos cognición motivada hace. Con α=0,1 y λ=0,3 el kernel apaga casi todo y lo que queda es, otra vez, un encogimiento suave.

## 6. Lo que este experimento cierra

Se han probado ahora **las tres familias** que `MODEL_SPECIFICATION.md` puso sobre la mesa, incluida la que ese mismo documento designó como objetivo por tener la mejor evidencia publicada. Con el nivel controlado por un forzamiento exógeno y contra un baseline de un solo parámetro:

| Modelo | Mejor W1 total | Parámetros barridos |
|---|---|---|
| Friedkin-Johnsen | 0,2652 | 1 |
| Contracción uniforme, sin red | 0,2750 | 1 |
| Cognición motivada | 0,2811 | 5 |
| Traslación pura | 0,4262 | 0 |
| *(Experimento 3)* DeGroot | peor que el ruido | 0 |

**Ninguna familia endógena mejora materialmente sobre "traslación + encogimiento".** Y ahora la afirmación sí está respaldada: el fallo 8 del diagnóstico —"se probó una familia, y estructuralmente no podía"— queda saldado. Se probaron las tres, la que podía también, y el resultado no cambia.

**La vía endógena queda agotada con los datos actuales.** No con los datos posibles: siguen siendo **3 transiciones**, y con 3 transiciones ninguna comparación entre modelos tiene poder real. La conclusión correcta no es "la opinión en Bogotá no tiene mecanismo social", sino **"con cuatro olas bienales no se puede identificar uno, y el que mejor ajusta es el más simple"**.

## 7. Lo que queda

1. **Ampliar la serie** (ECP 2008–2015, `claude/DIAGNOSTICO_Y_ALTERNATIVAS.md` §5.1) — de 3 transiciones a 7. Es lo único que cambiaría el poder de estas comparaciones, y el cargador ya existe. Con verificación de comparabilidad ítem por ítem antes de apilar nada.
2. **Pedir en el CNC una serie con pregunta repetida**, y solicitar el microdato de Bogotá Cómo Vamos.
3. **Fase 8 — escenarios.** Ahora sí, y sin la reserva con la que lo retiré en el diagnóstico: entonces la conclusión "no hay modelo generativo identificable" venía de probar un solo modelo incapaz por estructura. Hoy viene de tres familias, con el nivel controlado y con criterios pre-registrados. El motor de escenarios debe construirse sobre lo que sí funciona: **forzamiento exógeno explícito + encogimiento**, con la red reportada como sensibilidad y no como mecanismo.
4. **Registrar A06 y A18** en `PROJECT_CONTEXT.md` con este resultado.

## 8. Una nota sobre el método

De las cinco predicciones, fallaron tres, incluida la que llevaba "confianza alta". El pre-registro es lo que hace que eso se pueda decir: sin él, 0,2811 contra 0,2652 se cuenta como "resultados comparables" y 4,53 % se cuenta como "aproximadamente el 5 % esperado".

También se arreglaron aquí los dos criterios mal escritos del Experimento 4 —perfil tardío con umbral de magnitud y proporción, bimodalidad con guarda de dispersión— y los dos corregidos funcionaron: uno falló por poco y el otro pasó limpio, en vez de dar veredictos absurdos.

Y una corrección quedó atrapada antes de contaminar nada: había escrito que ρ < 1 "modera" cuando en realidad refuerza. Lo detectó una aserción del test sobre un valor calculado a mano, antes de correr una sola configuración.

---

*Reportado contra el pre-registro, con las tres predicciones fallidas en primer plano. El matiz de §3 empeora la lectura del modelo respecto del veredicto automático, no la mejora.*
