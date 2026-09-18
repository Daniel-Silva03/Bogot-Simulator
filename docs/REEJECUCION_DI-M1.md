# Re-ejecución de los Experimentos 4, 5 y 6 con el pipeline corregido

Proyecto: Bogotá Social Simulator
Versión: 1.0
Fecha: 17 de septiembre de 2026
Motivo: DI-M1 — el desempate del hot-deck era determinista y aplanaba la variable de opinión
Corridas: 5.040 (Exp. 4) · 2.034 (Exp. 5) · 612 (Exp. 6), mallas idénticas a las originales
Salidas: `data/processed/exp4|exp5|exp6`; las anteriores se conservan en `data/processed/_predim1/`

---

## 0. El resultado en una frase

**El defecto de la población estaba favoreciendo sistemáticamente a los mecanismos de influencia.** Con la población corregida, *todas* las variantes de Friedkin-Johnsen y DeGroot empeoran, la traslación y el ruido mejoran, y **cognición motivada queda exactamente igual**. Dos veredictos cambian.

## 1. Qué se corrigió

`hot_deck_match` pedía un solo vecino y se quedaba con el primero. Con empates —masivos cuando las variables de distancia son discretas— todos los receptores de una celda recibían **el mismo valor**, y la opinión sintética dejaba de ser una muestra de la distribución del donante. Ahora se sortea entre los empatados con probabilidad proporcional al factor de expansión (DI-M1 en `src/population/matching.py`).

| Población base | \(W_1\) antes | \(W_1\) después | piso de ruido |
|---|---|---|---|
| ECP 2013 (Exp. 6) | 0,0442 · 1,05× | **0,0205 · 0,49×** | 0,0422 |
| ECP 2017 (Exp. 4 y 5) | 0,0497 · 1,08× | **0,0303 · 0,65×** | 0,0462 |

Las dos quedan **por debajo del piso**: indistinguibles de una muestra fresca de lo observado. La desviación estándar inicial de 2017 pasa de 0,9937 a 0,9129, contra 0,9336 observada — antes estaba inflada.

## 2. El patrón, y es lo más informativo de todo esto

Experimento 4, **mismos 12 modelos, mismas 5.040 corridas**, lo único que cambia es la población:

| Modelo | antes | después | Δ |
|---|---|---|---|
| **traslación** (sin mecanismo) | 0,4262 | **0,3517** | **−0,075** |
| **ruido** | 0,4188 | **0,3461** | **−0,073** |
| FJ φ=0,1 | 0,2663 | 0,3063 | +0,040 |
| FJ φ=0,2 | 0,2873 | 0,4162 | +0,129 |
| FJ φ=0,3 | 0,3435 | 0,5362 | +0,193 |
| FJ φ=0,5 | 0,4477 | 0,7115 | +0,264 |
| FJ φ=0,7 | 0,5123 | 0,7881 | +0,276 |
| FJ φ=0,9 | 0,5273 | 0,7819 | +0,255 |
| DeGroot | 0,5093 | 0,7245 | +0,215 |

**El deterioro crece monótonamente con φ**, es decir, con cuánta influencia social aplica el modelo. Los dos modelos que no tocan la forma de la distribución —traslación y ruido— son los únicos que mejoran.

La lectura es incómoda y directa: la población vieja tenía la opinión **apelmazada** en pocos valores donados, con la dispersión inflada. Los modelos de influencia suavizan y contraen distribuciones. Estaban cobrando crédito por reparar un artefacto que había introducido nuestro propio generador de población.

## 3. Experimento 4 — el titular se reduce a un tercio, y Q2 falla

| | Original | Re-ejecución |
|---|---|---|
| Mejor mecanismo | 0,2663 | 0,2954 |
| Traslación pura | 0,4262 | 0,3517 |
| **Mejora del mecanismo** | **37,5 %** | **12,9 %** |
| Q2 — error de sd con mecanismo | 0,0453 · **PASA** | 0,0950 · **FALLA** (umbral 0,05) |

La afirmación "FJ con φ=0,1 le gana a la traslación pura por 37,5 % en 360 de 360 configuraciones" queda en **12,9 %**. Dos tercios de aquella ventaja eran el modelo arreglando nuestro artefacto.

Y el control post-hoc que ya acotaba la contribución de la red sigue acotándola: la contracción uniforme **sin ninguna red** llega a 0,2954, el mismo número que el mejor mecanismo. Es decir, con la población corregida **la red no aporta nada medible sobre una contracción sin red**, donde antes aportaba 2,8 %.

## 4. Experimento 5 — tres predicciones cambian de signo, y a favor de cognición motivada

Malla idéntica, 2.034 corridas.

| Familia | antes | después | Δ |
|---|---|---|---|
| Friedkin-Johnsen | 0,2652 | 0,2978 | +0,033 |
| Contracción sin red | 0,2750 | 0,3463 | +0,071 |
| **Cognición motivada** | 0,2811 | **0,2817** | **+0,0006** |
| Traslación | 0,4262 | 0,3517 | −0,075 |

**Cognición motivada es la única familia cuyo desempeño no se mueve.** Su ajuste no descansaba en el artefacto. Y como las otras dos empeoran, pasa a ganarles:

| Predicción | antes | después |
|---|---|---|
| R1 — le gana a Friedkin-Johnsen | FALLA | **PASA** (en el mejor: 0,2817 contra 0,2978) |
| R2 — produce contracción tardía | FALLA (4,53 %) | **PASA** (5,25 %, umbral 5 %) |
| R3 — le gana al control sin red | FALLA (−2,2 %) | **PASA (+18,7 %)** |
| R5 — error de dispersión | PASA (0,0343) | **FALLA** (0,0495) |

**Hay que decir los dos lados.** R1 pasa **en el mejor** pero no en la mediana: la mediana de cognición motivada es 0,4180 contra 0,3151 de FJ. Es decir, su mejor configuración gana, pero la familia en conjunto sigue siendo más errática — y barre cinco parámetros contra uno. R2 pasa por 0,25 puntos porcentuales sobre un umbral de 5 %, que es un margen incómodo. Y R5 se cae.

Lo que sí queda establecido y no depende del margen: **cognición motivada es la única familia que produce contracción tardía** (102 corridas contra 0 de FJ y 0 de contracción) y la única indiferente a la calidad de la población.

## 5. Experimento 6 — el veredicto no se mueve

| Familia | antes | después |
|---|---|---|
| `traslación+u+γ` (baseline duro) | 0,6032 | **0,5786** |
| Cognición motivada | 0,7450 | 0,6956 |
| Traslación pura | 0,7620 | 0,7429 |
| Contracción | 0,8860 | 0,8615 |
| Friedkin-Johnsen | 0,9011 | 0,9067 |

**Las cinco predicciones siguen cumpliéndose.** Ningún mecanismo hace la joroba (0 de 594), el baseline acierta media y sd por construcción, γ es negativo primero y positivo después, y ningún mecanismo le gana al baseline — ahora por 20,2 % en vez de 23,5 %. Friedkin-Johnsen sigue **último, peor que no hacer nada**.

El orden de mérito es idéntico. Este experimento era el más exigente de los tres y es el que menos se mueve.

## 6. Qué cambia en las conclusiones del proyecto

**Lo que se debilita.** El Experimento 4 era el único resultado claramente favorable al ABM. Su titular baja de 37,5 % a 12,9 %, pierde la predicción de dispersión, y la contribución de la red sobre un control sin red pasa de 2,8 % a **cero medible**. La afirmación honesta ahora es: *con forzamiento exógeno el modelo ajusta, y la influencia social por la red no aporta nada distinguible.*

**Lo que se fortalece.** Cognición motivada —la familia que `MODEL_SPECIFICATION.md` §4 había designado *a priori* como la de mejor evidencia publicada— es la única que no dependía del artefacto, la única que produce contracción tardía, y con la población corregida le gana tanto a Friedkin-Johnsen como al control sin red sobre la serie 2017-2023. El cierre del Experimento 5 —"pierde con 108 configuraciones contra 2"— **queda revocado**.

**Lo que no cambia.** El Experimento 6, sobre la serie que arranca en 2013, sigue diciendo que ningún mecanismo —cognición motivada incluida— le gana a dos números exógenos por periodo, y por un margen amplio.

**Y eso deja el proyecto exactamente donde el Experimento 7 lo va a poner a prueba.** Cognición motivada gana sobre la serie de tres transiciones y pierde sobre la de cuatro. Una familia que cambia de veredicto según el tramo que se mire no está identificada: está siendo medida sin poder. Las ocho transiciones de la EPC son la forma de resolverlo, y el pre-registro ya está escrito.

## 7. Nota de método

Los tres documentos de resultados originales (`EXPERIMENT_4_RESULTS.md`, `_5_`, `_6_`) **no se modifican**. Reportan lo que se obtuvo contra su pre-registro con el pipeline de entonces, y reescribirlos borraría la evidencia de que el defecto existió y de cuánto valía. Este documento es un reporte aparte contra las mismas especificaciones pre-registradas.

Las salidas anteriores se conservan en `data/processed/_predim1/`.

**Una comparación que hubo que hacer con cuidado.** La malla del Experimento 4 había crecido desde la corrida original —se le añadieron los tres modelos `contraccion_g*` al implementar el control post-hoc—, así que comparar los archivos de veredicto directamente mezclaba dos cambios. Las cifras de §2 y §3 son sobre los **12 modelos comunes y las mismas 5.040 corridas**. Las mallas de los Experimentos 5 y 6 sí eran idénticas.
