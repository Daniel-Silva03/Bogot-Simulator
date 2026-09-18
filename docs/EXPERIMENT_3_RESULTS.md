# EXPERIMENT 3 — Resultados

Proyecto: Bogotá Social Simulator
Versión: 1.0
Fecha: 16 de septiembre de 2026
Especificación: `claude/EXPERIMENT_3_SPECIFICATION.md` (cerrada antes de correr)
Código: `src/experiments/experimento3.py` · `src/population/ecp.py`
Datos: `data/processed/exp3/` · población `data/processed/poblacion_ecp2017.csv`

---

## 1. El resultado en una línea

**Friedkin-Johnsen falla cuatro de las cinco predicciones, y un único escalar por año explica el doble de lo que explica toda la maquinaria de redes y dinámica social junta.**

Es la primera vez que este proyecto confronta el modelo con la realidad y obtiene un veredicto. El veredicto es negativo, y es útil.

---

## 2. Veredicto, predicción por predicción

| | Qué prueba | Predicho | Resultado | ¿Acertamos? |
|---|---|---|---|---|
| **P1** | mover el nivel | FALLA | **FALLA** | sí |
| **P2** | contraer la dispersión | PASA | **FALLA** | **no** |
| **P3** | producir la no monotonía | FALLA | **FALLA** | sí |
| **P4** | asimetría de colas | FALLA | **FALLA** | sí |
| **P5** | no inventar bimodalidad | PASA | **PASA** | sí |

Una predicción de las cinco salió al revés, y conviene que quede escrita: **P2 se predijo como acierto del modelo y resultó fallo.** Esa es la razón de haber cerrado la especificación antes de correr. La sección 4 explica por qué falló, y la explicación es más interesante que el acierto que esperábamos.

### P1 — El nivel. **FALLA por un factor de 8,9.**

Sobre las 720 corridas de FJ, el mayor desplazamiento de la media en toda la trayectoria es **0,029**. Lo observado recorre **0,258**.

Y hay una forma más contundente de decirlo. El error de media en el mapeo óptimo, por modelo:

| Modelo | 2019 | 2021 | 2023 |
|---|---|---|---|
| congelado | 0,1431 | 0,2600 | 0,0747 |
| FJ φ=0,3 | 0,1431 | 0,2586 | 0,0733 |
| FJ φ=0,9 | 0,1431 | 0,2562 | 0,0704 |
| DeGroot | 0,1431 | 0,2558 | 0,0698 |

**El error de nivel es el mismo corras el modelo o no lo corras.** Las diferencias aparecen en la tercera o cuarta cifra decimal. La dinámica social, tal como está especificada, no contribuye absolutamente nada al nivel de confianza agregado.

### P2 — La dispersión. **FALLA. Y falla por una razón que no habíamos visto.**

Predijimos que pasaría porque lo observado se contrae 18,2 % y el punto fijo de FJ contrae entre 25 % y 88 %: el objetivo parecía estar dentro del alcance. El mejor error de sd alcanzable, evaluado bajo el mapeo temporal que minimiza ese error —o sea, dándole al modelo su mejor caso— es **0,0748**, contra un umbral de 0,05.

El problema no es la magnitud. Es el **perfil temporal** de la contracción:

| Tramo | Contracción observada |
|---|---|
| 2017 → 2019 | −3,3 % |
| 2019 → 2021 | **−0,7 %** |
| 2021 → 2023 | **−14,8 %** |

La dispersión observada se queda prácticamente quieta durante cuatro años y después se desploma. La contracción de Friedkin-Johnsen hace lo contrario: es máxima al principio y se desacelera al acercarse al punto fijo. **Está cargada al frente donde los datos la cargan al final.**

Y esto es, otra vez, invariante a la reparametrización temporal: estirar o comprimir el reloj puede cambiar cuándo ocurre la contracción, pero no puede convertir un perfil decelerante en uno acelerante. Es el mismo tipo de fallo que P3, sobre otra cantidad. No lo habíamos anticipado.

### P3 — La no monotonía. **FALLA. 0 de 720.**

Ninguna de las 720 corridas de FJ —ninguna red, ningún φ, ningún número de pasos— produce un mínimo interior material en la media. Lo observado lo tiene, en 2021, con un rebote de 0,185.

Es la prueba central y no tiene parámetros libres: una reparametrización monótona del tiempo no puede volver no monótona una trayectoria monótona. El modelo está descartado para reproducir esta forma, y no por haber elegido mal el reloj.

### P4 — Las colas. **FALLA. 0 de 720.**

Ninguna corrida produce un máximo interior en la masa bajo 2,0. Lo observado va 27,4 → 34,3 → **37,1** → 23,2. FJ contrae hacia el centro de forma monótona, así que vacía las dos colas a la vez y en la misma dirección; no puede engordar una cola y después vaciarla.

### P5 — La bimodalidad. **PASA.**

1.488 estados simulados medidos con el coeficiente de Sarle: **máximo 0,408**, mediana 0,368, **cero** por encima del umbral de 5/9 ≈ 0,556. Lo observado va de 0,349 a 0,448. Los dos rangos se solapan.

Esto **reencuadra un resultado del Experimento 2**. Allí se anotó como limitación que ni FJ ni DeGroot fragmentan la opinión en 9.600 corridas. Contra estos datos no es una limitación: **Bogotá tampoco se fragmentó.** Un modelo que produjera polarización bimodal estaría equivocado sobre este fenómeno en este periodo.

---

## 3. Contra los baselines: el resultado que más pesa

Mediana de Wasserstein-1 sumado sobre los tres años objetivo, 180 corridas por fila, menor es mejor:

| Modelo | mediana | Q1 | Q3 |
|---|---|---|---|
| **FJ φ=0,3** | **0,5310** | 0,5260 | 0,5362 |
| congelado | 0,6265 | 0,6265 | 0,6265 |
| ruido | 0,6287 | 0,6277 | 0,6294 |
| FJ φ=0,5 | 0,6404 | 0,6078 | 0,7068 |
| FJ φ=0,7 | 0,8053 | 0,7513 | 0,9405 |
| FJ φ=0,9 | 0,9177 | 0,8033 | 1,1001 |
| DeGroot | 0,9387 | 0,7815 | 1,1292 |

Habíamos predicho que FJ perdería contra no hacer nada. **Se cumple para φ ≥ 0,5 y no se cumple para φ = 0,3.** Con poca influencia social FJ le gana a congelado por 0,096, muy por fuera de la dispersión entre semillas (sd = 0,0045). La mejora es real.

Pero mirando de dónde sale, se desarma:

| Modelo | W1 2019 | W1 2021 | W1 2023 |
|---|---|---|---|
| FJ φ=0,3 | **0,1600** | 0,2715 | **0,0995** |
| congelado | **0,1600** | **0,2603** | 0,2062 |
| DeGroot | **0,1600** | 0,4350 | 0,3449 |

Dos cosas saltan:

1. **El W1 de 2019 es idéntico —0,1600— para los siete modelos.** Para el primer año objetivo, el mejor movimiento posible de cualquier modelo es no moverse: el mapeo óptimo elige el paso 0 en todos los casos. Ningún modelo mejora sobre el estado inicial para 2019.
2. **Toda la ventaja de FJ φ=0,3 viene de 2023**, donde reduce el error a menos de la mitad (0,0995 contra 0,2062). En 2021 **pierde** contra congelado. Es decir: lo único que FJ aporta es la contracción tardía de la dispersión, que es justamente lo que P2 mostró que reproduce mal — la reproduce lo bastante bien para 2023 y no para el camino hasta ahí.

DeGroot es el peor de todos, peor incluso que el ruido. Cierra A11: el baseline obligatorio queda comparado y el modelo candidato le gana, pero eso dice poco cuando los dos pierden contra congelado en el año intermedio.

---

## 4. Cuánto valdría arreglar el nivel

Diagnóstico directo: en vez de un modelo, sumarle a la opinión inicial **un solo número por año** —el desplazamiento que iguala la media observada— y medir cuánto del error desaparece.

| Año | W1 congelado | + desplazamiento óptimo | cuánto del error era nivel |
|---|---|---|---|
| 2019 | 0,1600 | 0,0939 | **41 %** |
| 2021 | 0,2603 | 0,1213 | **53 %** |
| 2023 | 0,2062 | 0,2109 | **−2 %** |

Y combinando ambas cosas (homofílica, k̄ = 8, φ = 0,3, mediana de 8 semillas):

| | W1 total | mejora sobre congelado |
|---|---|---|
| congelado | 0,6265 | — |
| **FJ solo** | 0,5254 | **16 %** |
| **nivel solo** | 0,4262 | **32 %** |
| **FJ + nivel** | 0,3437 | **45 %** |

**Un escalar por año explica el doble que toda la maquinaria de redes, homofilia, territorio y dinámica de influencia junta.** Los dos aportes son casi aditivos, lo que confirma que atacan errores distintos: FJ la forma, el nivel el nivel.

El −2 % de 2023 es igual de informativo: para ese año la media **ya volvió** a estar cerca de la de 2017, así que corregir el nivel no ayuda y el error restante es enteramente de forma. La lectura completa es:

- **2019 y 2021 fallan por nivel.** El modelo no puede mover el centro de masa.
- **2023 falla por forma.** El nivel está bien; lo que falta es la contracción tardía y brusca de la dispersión.

Son dos carencias distintas, y un término exógeno de nivel solo resuelve la primera. Incluso con las dos correcciones queda **55 % del error sin explicar**.

---

## 5. La estructura de red casi no importa acá

W1 total de FJ φ=0,3, mediana por configuración:

| | k̄=4 | k̄=8 | k̄=16 |
|---|---|---|---|
| aleatoria | 0,5288 | 0,5369 | 0,5396 |
| homofílica | 0,5270 | 0,5255 | 0,5294 |
| territorial | 0,5244 | 0,5325 | 0,5364 |

El rango completo entre las nueve celdas es 0,015, contra una dispersión entre semillas de 0,0045: unas 3,4 desviaciones. Detectable, pero minúsculo.

**Contraste con el Experimento 2**, donde la diferencia entre red homofílica y aleatoria era de 27 a 41 desviaciones. Allí la estructura de red dominaba el resultado; acá casi no se nota. La explicación es coherente con todo lo anterior: el error está dominado por el nivel, y **ninguna estructura de red arregla un nivel que el mecanismo no mueve.** La red decide cómo se reparte la opinión entre agentes, no dónde queda el promedio.

Esto no invalida el Experimento 2 — mide otra cosa (la persistencia del desacuerdo, no el ajuste a datos). Pero sí acota su alcance: la sensibilidad a la estructura de red era sensibilidad de una cantidad que, contra los datos, resultó ser de segundo orden.

---

## 6. Experimento 3A — la población, que sí pasó

Prerrequisito, y quedó holgado. Población reconstruida con la ECP 2017 como donante (n = 5.002 donantes válidos, 97,4 % de la submuestra de Bogotá), emparejamiento exacto por sexo y distancia sobre edad × estrato × educación armonizada:

| | simulado t₀ | observado 2017 |
|---|---|---|
| media | 2,5049 | 2,5030 |
| sd | 0,9937 | 0,9336 |
| % < 2,0 | 27,8 % | 27,4 % |
| % > 3,5 | 14,7 % | 14,2 % |
| bimodalidad | 0,408 | 0,420 |

**W1 = 0,0476** contra un criterio de 0,10. KS = 0,0263. El 100 % de los agentes se emparejó en el nivel 0 de la escalera (coincidencia exacta en sexo).

Dos cosas que conviene registrar:

**El aplanamiento del hot-deck salió al revés de lo temido.** La especificación (amenaza 3) advertía que el desempate determinista podía comprimir la dispersión inicial y contaminar P2. Lo medido es lo contrario: **sd simulada / sd observada = 1,064**, el estado inicial es 6 % *más* disperso. El 1-NN determinista repite donantes extremos —131 agentes (13,1 %) quedan exactamente en 1,0, el piso de la escala— y eso infla la dispersión en vez de reducirla. No salva a P2: el exceso de dispersión inicial hace el objetivo de 2019 un poco más fácil y el de 2023 un poco más difícil, y el fallo de P2 es de perfil, no de magnitud.

**Se cerró A15 para este experimento.** La ECP trae estrato (`P4031S1A1`), así que por primera vez el hot-deck lo usó como variable de distancia. Se perdió localidad, que la ECP no tiene: **el Experimento 3 no valida nada territorial.**

---

## 7. Enmienda a la especificación

Registrada acá y en el código porque cambiar un criterio después de correr es exactamente lo que la especificación intenta impedir.

**Qué se cambió, cuándo y por qué.** 16/09/2026, *antes* de correr 3B completo, durante la prueba del código. La especificación redactó P3 y P4 como "¿hay un mínimo (o máximo) interior en la trayectoria?", sin umbral de magnitud. Con tolerancia puramente numérica (1e-4), P3 daba "pasa" para corridas cuya media se mueve 0,004 en total y cuyo "rebote" es de orden 1e-5 — aritmética de punto flotante en la convergencia, no una V.

Se agregó un umbral de magnitud igual al de P1 (**0,05**): un mínimo interior cuenta solo si el rebote posterior lo supera. Lo observado rebota 0,185, casi cuatro veces el umbral, así que el criterio no se ablandó a favor del modelo — se le exigió que la V fuera una V. Con el umbral, 0 de 720 corridas califican; sin él, calificaban por ruido numérico.

Segunda corrección, también antes de correr: el baseline de ruido estaba escalado contra el primer checkpoint y a 500 pasos multiplicaba por 20 la dispersión inicial. Se reescaló para que la caminata aleatoria alcance la magnitud del cambio observado alrededor del paso 50.

---

## 8. Qué significa esto para el proyecto

### 8.1 Lo que queda establecido

`EXPERIMENT_1_SPECIFICATION.md` §5 decía que todo lo construido era "maquinaria verificada internamente y sin validar contra la realidad". Ya no: **la maquinaria se validó y no reprodujo el fenómeno.** El criterio de éxito de `PROJECT_CONTEXT.md` §37 —"reproducir algunos patrones observados mejor que determinados baselines"— se cumple de forma estrecha y poco satisfactoria: FJ φ=0,3 le gana a congelado y a DeGroot, pero le pierde a un escalar por año, y le pierde a congelado en el año intermedio.

### 8.2 Lo que hay que decidir, y lo que no hay que hacer

El diagnóstico apunta a un término exógeno \(s(t)\) que mueva el nivel. **La especificación fijó la regla antes de ver esto, y sigue valiendo:** \(s(t)\) con suficientes grados de libertad reproduce cualquier trayectoria, incluida una generada al azar. La sección 4 de este documento es una demostración de eso — tres números libres ya explican el 32 % del error sin ningún modelo detrás. Ajustar \(s(t)\) contra estos mismos datos y reportar el ajuste no sería evidencia de nada.

Para que \(s(t)\) sea defendible tiene que estar **anclado a una serie externa medida de forma independiente** y validarse fuera del periodo usado para fijarlo. Con cuatro puntos temporales eso es apretado.

Además, \(s(t)\) **no resuelve 2023**, donde el error es de forma. Hace falta pensar por separado qué produce una contracción de dispersión tardía y brusca.

### 8.3 Preguntas abiertas que este experimento genera

- **A06 / MODEL_SPECIFICATION.** Friedkin-Johnsen queda confirmado como incapaz de reproducir la dinámica observada por sí solo. La pregunta deja de ser "¿FJ o DeGroot?" —DeGroot es peor que el ruido— y pasa a ser "¿qué le falta al marco?".
- **A07 / estructura de red.** La red importa poco para el ajuste a datos. Elegir generador por el Experimento 2 sigue siendo válido para la pregunta que el Experimento 2 hizo, pero no puede justificarse por poder predictivo.
- **No-respuesta de 2023.** Sigue pendiente (amenaza 1 de la especificación): salta de ~2 % a 5,6 %. Si el rebote de 2023 se debilita al corregirlo, P3 se apoyaría sobre todo en el tramo de bajada. No cambia el veredicto de P3 —0 de 720 no depende de cuán grande sea la V— pero sí cuánta V hay que explicar.
- **n = 1.000.** La dispersión entre semillas (0,0045) es chica frente a todos los efectos reportados, así que las conclusiones no parecen limitadas por el tamaño. Repetir con n = 10.000 confirmaría las colas.

---

## 9. Reproducir

```
python src/population/construir_poblacion.py --donante ecp:2017 \
       --nombre-base poblacion_ecp2017 --version v0.3-exp3a-ecp2017
python3 tests/test_ecp.py
```

El barrido de 3B (1.260 corridas, ~27 min) se lanza desde `src/experiments/experimento3.py`:
`cargar_observado()` → `correr()` → `evaluar_predicciones()` / `comparar_baselines()`.
Salidas en `data/processed/exp3/`: `resultados.csv`, `veredicto.json`, `baselines.csv`, `p2_propio_mapeo.csv`.

Semilla base 20260916; cada corrida deriva la suya con `semilla_para()`.
