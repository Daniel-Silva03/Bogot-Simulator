# EXPERIMENTO 7 — Especificación pre-registrada

Proyecto: Bogotá Social Simulator
Versión: 1.0
Fecha: 17 de septiembre de 2026
Estado: **pre-registro — escrito y guardado antes de correr el barrido**
Origen: la serie de la EPC de Bogotá Cómo Vamos (`claude/ANALISIS_EPC_BCV.md`) duplica el número de transiciones
Código: `src/experiments/experimento7.py` *(por escribir)*

---

## 1. Por qué hay un experimento más, y por qué este sí tiene poder

Los Experimentos 3 a 6 concluyeron que **no hay mecanismo de dinámica de opinión identificable** para confianza institucional en Bogotá. El veredicto descansaba en la ECP: cinco olas, **cuatro transiciones**. Con cuatro puntos, "ningún mecanismo gana" y "no hay poder para distinguir" son prácticamente indistinguibles.

La EPC aporta **ocho transiciones** en una serie anual, y algo que la ECP no podía dar: **dos ítems de evaluación institucional contestados por la misma persona en el mismo cuestionario**, lo que permite construir un objetivo limpio de estilo de respuesta.

## 2. Los dos objetivos, y por qué son dos

### Objetivo A — la serie cruda `GG3` (gestión del alcalde), 9 olas

| Año | 2014 | 2015 | 2017 | 2018 | 2019 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|
| media | 2,845 | 2,408 | 2,105 | 2,367 | 2,544 | 2,952 | 2,859 | 3,180 | 2,753 |
| sd | 1,273 | 1,179 | 1,108 | 1,156 | 1,129 | 1,212 | 1,148 | 1,126 | 1,119 |
| cobertura | 94,7 | 94,9 | 96,5 | 97,4 | 94,7 | 84,9 | 84,0 | 81,6 | 80,6 |

Amplitud grande (1,08 de rango) y ocho transiciones. **Contaminado**: `GG3` y `CC5` (Concejo) correlacionan +0,62 en cambios, y en 2017→2019 suben exactamente lo mismo (+0,439 y +0,436) mientras la ECP, encuesta independiente, bajaba. Hay un componente común que puede ser clima de opinión real o efecto de campo, y con dos ítems no se identifica.

### Objetivo B — la diferencia individual \(d_i = GG3_i - CC5_i\), 8 olas

Cada encuestado contesta ambos ítems, así que la diferencia existe **persona por persona**, en escala −4 a +4. Sustantivamente es *cuánto mejor o peor califica esta persona al alcalde que al Concejo*, y elimina no solo un efecto aditivo de periodo sino el **estilo de respuesta individual** — aquiescencia, uso de la escala, tendencia central.

| Año | 2014 | 2015 | 2017 | 2019 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| media | +0,237 | −0,150 | −0,126 | −0,127 | +0,335 | +0,334 | +0,470 | +0,147 |
| sd | 1,353 | 1,237 | 1,127 | 1,132 | 1,203 | 1,138 | 1,163 | 0,937 |
| cobertura | 72,2 | 73,0 | 86,3 | 87,9 | 68,2 | 71,9 | 74,1 | 71,2 |

**Y hace exactamente lo que se esperaba de un control:** el salto conjunto de 2017→2019 pasa de +0,44 a **−0,001**. Se evapora entero. Lo mismo con 2022→2023 (−0,062 y −0,093 en las series crudas, **−0,001** en la diferencia).

Lo que **sobrevive** son cuatro movimientos, y se alinean con los cambios de alcaldía: −0,387 (2014→2015), **+0,462** (2019→2022, entrada de López), +0,136 (2023→2024, entrada de Galán) y −0,323 (2024→2025). Eso no prueba que la diferencia sea el constructo correcto, pero es lo que uno esperaría si lo fuera.

**Costo del objetivo B:** cobertura más baja (68-88 %, porque exige ambos ítems) y amplitud menor (0,86 de rango contra 1,08). Se paga a cambio de un objetivo sin el confundidor.

**Los dos se corren, y los dos se reportan.** Correr solo el A y declarar veredicto sería repetir el error del Experimento 4 —ajustar un fenómeno y llamarlo *el* fenómeno—; correr solo el B sería elegir el objetivo que más conviene después de haberlo visto.

## 3. El diseño

Igual que el Experimento 6, con estas precisiones.

**DI-X1 — los tramos duran distinto y los pasos son proporcionales.** La serie está espaciada 1·2·1·1·3·1·1·1 años (objetivo A) y 1·2·2·3·1·1·1 (objetivo B). \(S\) pasos por año; un tramo de 3 años lleva \(3S\).

**DI-X2 — población base nueva, `poblacion_epc2014.csv`.** Construida con el mismo pipeline (PPS sobre el receptor de Multipropósito 2021 + hot-deck) usando la EPC 2014 como donante de opinión. Variables puente: sexo, edad, estrato, localidad. **Se verifica antes de correr** que \(W_1(a_0, \text{obs}_{2014})\) quede cerca del piso de ruido, como en los experimentos anteriores; si no lo queda, el experimento se detiene y se arregla la población primero.

**DI-X3 — para el objetivo B la escala es −4 a +4 y está centrada en 0.** Cognición motivada usa `centro = 0`; el clipping sigue desactivado (DI-F2).

**DI-X4 — la cobertura viaja con cada comparación.** Ninguna tabla de resultados reporta un W1 sin la cobertura del año objetivo al lado (DI-B1). Tres de las ocho transiciones del objetivo A no son robustas a la no respuesta (`claude/ANALISIS_NORESPUESTA_EPC.md` §3) y **se marcan como tales en los resultados**, no se excluyen.

### La malla

| Dimensión | Valores |
|---|---|
| Objetivos | **A** (`GG3` crudo, 8 transiciones) · **B** (diferencia individual, 7 transiciones) |
| Base | 2014 |
| \(S\) (pasos por año) | 3 · 8 |
| Baselines | traslación+u · **traslación+u+γ** |
| Encogimiento fijo | γ ∈ {±0,02 · ±0,05} |
| Friedkin-Johnsen | φ ∈ {0,08 · 0,1 · 0,2 · 0,3} |
| Cognición motivada | α ∈ {0,1 · 0,3} · λ ∈ {0,3 · 0,5} · k ∈ {2 · 3} · ρ ∈ {0,9 · 1,0 · 1,1} |
| Red | aleatoria · homofílica · territorial (h=20) |
| \(\bar{k}\) | 5 (D15) |
| Semillas | 3 |

---

## 4. Predicciones

### T1 — Ningún mecanismo con parámetros fijos reproduce el perfil de dispersión
**Predicción: FALLA para todos.** En el objetivo A la sd cambia **−7,4 % · −6,0 % · +4,3 % · −2,3 % · +7,3 % · −5,3 % · −1,9 % · −0,6 %**: el signo alterna cinco veces. Con parámetros constantes estas familias tienen signo fijo. *Confianza: muy alta*, y es analítica.

Criterio: una corrida "acierta el perfil" si el signo de su cambio de sd coincide con el observado en ≥6 de los 8 tramos; se espera 0 corridas con mecanismo.

### T2 — `traslación+u+γ` acierta media y sd en los dos objetivos
**Predicción: PASA por construcción.** Error por debajo de 10⁻³ en todos los años, en A y en B. Es verificación del ajuste, no prueba.

### T3 — Con ocho transiciones, ningún mecanismo le gana al baseline · **la decisiva**
**Predicción: PASA (ningún mecanismo gana), en los dos objetivos.** *Confianza: media-alta.*

Aquí es donde este experimento vale la pena. En el Experimento 4 (3 transiciones) FJ ganaba por 37,5 %; en el Experimento 6 (4 transiciones) FJ quedaba **último**. Esa inversión con un cambio de tramo es la firma de un resultado sin poder. Con ocho transiciones, si FJ vuelve a ganar es evidencia real; si vuelve a perder, la conclusión de los Experimentos 3-6 deja de descansar en cuatro puntos.

Si **alguno gana**, el margen es lo único que aporta el mecanismo social medido contra el baseline más duro posible, y con el mayor número de transiciones que el proyecto ha tenido.

### T4 — El objetivo B es *más* difícil para los mecanismos, no menos
**Predicción: PASA.** Medido como W1 relativo al piso de ruido de cada objetivo, el mejor mecanismo quedará **peor** en B que en A. *Confianza: media.*

El razonamiento: si parte de lo que los mecanismos aprovechan en A es el componente común —que es suave y monótono por tramos, y por tanto fácil de imitar con una contracción o una influencia constante—, quitarlo deja un objetivo más abrupto. Si saliera al revés —los mecanismos ajustando **mejor** el objetivo limpio— sería el primer resultado claramente a favor del ABM en todo el proyecto, y habría que perseguirlo.

### T5 — El orden de mérito coincide entre A y B
**Predicción: FALLA.** Espero que el ranking de familias **no** se conserve entre los dos objetivos (correlación de Spearman entre los dos órdenes por debajo de 0,7). *Confianza: baja* — la registro precisamente porque no sé qué va a pasar, y porque si el orden **sí** se conserva es la señal más fuerte de que el ranking mide algo del modelo y no del objetivo.

### T6 — La población base arranca cerca del piso
**Predicción: PASA.** \(W_1(a_0, \text{obs}_{2014}) < 2\times\) el piso de ruido, como en los Experimentos 4 y 6. Es un control: si falla, lo que sigue no es interpretable.

---

## 5. Qué significará cada resultado

| | Lectura |
|---|---|
| T3 pasa en A y en B | El veredicto de los Experimentos 3-6 deja de ser un problema de poder. Con ocho transiciones y dos objetivos, **no hay mecanismo social identificable con datos públicos de Bogotá**, y el motor de escenarios se construye sobre perillas exógenas sin reserva. |
| T3 falla en A pero pasa en B | Lo que el mecanismo capturaba era el componente común, no opinión. Resultado incómodo y probablemente el más informativo. |
| T3 falla en B | Hay un aporte real del mecanismo social sobre el objetivo limpio. Sería el primer resultado a favor del ABM, y habría que medirlo con cuidado antes de celebrarlo. |
| T1 pasa para alguna familia | Existe un mecanismo capaz del perfil de dispersión alternante. Merece perseguirse. |
| T6 falla | Se detiene el experimento y se arregla la población. Nada de lo demás se lee. |

## 6. Lo que este experimento sigue sin poder decidir

- **El tramo 2019→2022 cubre tres años con una sola observación en cada extremo**, y adentro está la pandemia. Es la transición más grande de las dos series y la peor medida.
- **La cobertura cae 14 puntos a mitad de serie** y no sabemos por qué (`claude/ANALISIS_NORESPUESTA_EPC.md` §1). Tres transiciones del objetivo A no son robustas.
- **El constructo cambió respecto de los Experimentos 3-6**: aquello era confianza institucional, esto es evaluación de gestión. Un veredicto coincidente sería más fuerte por venir de dos constructos; uno discrepante no se resuelve con estos datos.
- **`GG3` y `CC5` son dos ítems.** Con dos no se identifica un modelo de factores; la diferencia elimina un componente aditivo común, no uno multiplicativo ni uno que afecte distinto a cada ítem.

---

*Guardado en el proyecto antes de ejecutar. Los resultados se reportarán en `claude/EXPERIMENT_7_RESULTS.md` contra esta especificación, incluidas las predicciones que fallen.*
