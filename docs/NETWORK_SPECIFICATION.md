# NETWORK SPECIFICATION — Generadores de red de interacción

Proyecto: Bogotá Social Simulator
Documento: ETAPA 4 del roadmap (junto con MODEL_SPECIFICATION.md) — **A07 resuelta** por D15 de PROJECT_CONTEXT.md
Versión: 0.4 — **A07 cerrada**: D15 aprobada el 16/09/2026 y aplicada en código (§7)
Versión 0.3 — el grado y la composición de la red dejaron de ser supuestos y pasaron a ser mediciones (§2.1, §4.1); se registró que el generador territorial no tiene objetivo empírico (§5.1); se reescribió §7 a la luz de los Experimentos 2 y 3
Fecha: 16 de septiembre de 2026

---

## 1. Objetivo

Especificar formalmente los generadores de red candidatos identificados en PROJECT_CONTEXT.md (sección 16) y RESEARCH.md (secciones 22 y 50, Experimento 2), de manera que puedan implementarse como módulos intercambiables del prototipo de 1.000 agentes, sin elegir todavía un único generador definitivo (ver sección 7 — por qué la decisión de A07 cambió de forma).

Todos los generadores producen el mismo objeto matemático: una matriz de pesos de influencia \(p_{ij}\), que es el insumo que requieren por igual DeGroot, Friedkin-Johnsen y, si se explora más adelante, Hegselmann-Krause/Deffuant (ver MODEL_SPECIFICATION.md sección 2).

**Cambio de estado respecto de la v0.2.** Esta especificación se escribió declarando que "no existe dato Bogotá-específico" para el grado promedio ni para los pesos de homofilia, y tratando ambos como parámetros a barrer. Eso dejó de ser cierto: el módulo de **Capital Social de la ECP** mide las dos cosas sobre Bogotá, y el análisis de `claude/ANALISIS_HOMOFILIA.md` las extrajo. Las secciones 2.1 y 4.1 recogen la medición. Las secciones que quedaron como supuesto se marcan explícitamente como tales en §8.

## 2. Elementos comunes a los tres generadores

**Población base:** los \(N = 1.000\) agentes del prototipo, con la estructura de variables fijada en PROJECT_CONTEXT.md (decisión D12): `agent_id, edad, sexo, localidad, estrato, nivel_educativo, opinion_t0`.

**Parámetro común — grado promedio objetivo \(\bar{k}\):**
La v0.2 proponía barrer \(\bar{k} \in \{5, 10, 15, 20\}\) por falta de dato. Ahora hay dato — ver 2.1.

### 2.1 El grado promedio, medido (ECP Capital Social, Bogotá)

La ECP pregunta por el tamaño del círculo cercano en dos variables que se suman:

| Variable | Qué pregunta |
|---|---|
| `P2047` | personas con las que se visita mutuamente con frecuencia |
| `P2049` | personas a las que podría pedir apoyo / en las que confía |

`red_cercana = P2047 + P2049`, Bogotá 2023, ponderada:

| Estadístico | Valor |
|---|---|
| media | **5,35** |
| mediana | **4** |
| % con red de tamaño 0 | **26 %** |

**Implicación directa:** \(\bar{k} \approx 5\). El barrido de la v0.2 empezaba justo en ese valor y subía hasta cuadruplicarlo; el barrido que efectivamente se corrió en los Experimentos 2 y 3 fue \(\bar{k} \in \{4, 8, 16\}\), y la medición cae entre los dos primeros. **El rango adoptado (D15) es \(\bar{k} \in \{4, 5, 8\}\)**, con 5 como valor central y 4 y 8 como sensibilidad a cada lado, no como candidatos equiprobables. El 16 sale del barrido: cuadruplica la medición.

**Tres advertencias que hay que arrastrar con este número:**

- `P2047` está **topeada en 10**. La media real es algo mayor que 5,35; la mediana de 4 es más robusta a ese techo.
- **2021 está contaminado por la pandemia** — la pregunta es literalmente sobre visitas mutuas. Calibrar con **2019 o 2023**, no con 2021.
- El módulo de Capital Social **no existe en 2017**, así que no hay serie de cuatro puntos para el grado.
- La pregunta mide **lazos fuertes de sociabilidad doméstica**, no "quién influye en tu opinión política". Deja fuera trabajo, redes sociales y vínculos débiles, que es donde la literatura ubica buena parte de la difusión. Es un piso del grado de influencia, no una medida directa de él.

**Codificación numérica de variables ordinales** (necesaria para el generador homofílico, sección 4):
- `estrato`: 1–6, ya es ordinal numérico en la fuente (Encuesta Multipropósito). Ver A17 de PROJECT_CONTEXT.md — los códigos 8/9 son no-respuesta y no deben entrar en la distancia.
- `nivel_educativo`: se mapea a una escala 0–5, en el mismo orden usado para el marginal de educación en DATA_SPECIFICATION.md (sin educación formal=0, primaria=1, secundaria=2, técnica/tecnológica=3, universitaria=4, posgrado=5)
- `edad`: continua; se estandariza (z-score) junto con las dos anteriores para que ninguna domine la distancia por efecto de escala

## 3. Generador 1 — Red aleatoria (Erdős–Rényi)

### Qué representa
Ausencia total de estructura social — cada par de agentes tiene la misma probabilidad de estar conectado, independientemente de sus atributos. Es el control experimental, no una hipótesis sobre cómo funciona realmente la sociedad.

### Fórmula
$$p_{ij} = \frac{\bar{k}}{N-1} \quad \text{para todo } i \neq j$$

### Pseudocódigo
```text
función generar_red_aleatoria(agentes, k_promedio):
    N = len(agentes)
    p = k_promedio / (N - 1)
    aristas = []
    para cada par (i, j) con i < j:
        si random() < p:
            aristas.append((i, j))
    retornar aristas
```

### Parámetros libres
Solo \(\bar{k}\).

### Fundamento en literatura
Ninguno — deliberadamente no lo tiene. Sirve como baseline de red, en el mismo rol que DeGroot juega como baseline de modelo (MODEL_SPECIFICATION.md sección 4).

### Costo computacional
O(N²) pares evaluados. A N=1.000 son ~500.000 pares — trivial. Escala mal a poblaciones grandes (A08), pero al ser el generador más simple, es también el más fácil de optimizar si hiciera falta (muestreo directo del número de aristas sin recorrer todos los pares).

## 4. Generador 2 — Red homofílica

### Qué representa
Los agentes tienen mayor probabilidad de interactuar con otros que se les parecen demográficamente — el mecanismo de homofilia documentado en RESEARCH.md sección 22 a partir de la literatura de poblaciones sintéticas geográficamente explícitas (Jiang et al., 2022).

### 4.1 Sobre qué ejes hay homofilia en Bogotá, medido

`P2051S1`…`S11` de la ECP describen la **composición del círculo cercano** definido en §2.1. Es, literalmente, la medición de sobre qué se construye la red real. Bogotá 2023, ponderado:

| % del círculo cercano | Eje |
|---|---|
| 72,9 | Se graduaron de bachillerato |
| 70,3 | Tienen un empleo |
| 50,2 | Miembros de su familia |
| 40,7 | Hombres |
| **39,5** | **Tienen opiniones políticas parecidas a las suyas** |
| 32,3 | Son de su grupo étnico |
| 30,5 | Asisten a su grupo u organización religiosa |
| 22,6 | Sienten que perdieron oportunidades por trabajadores extranjeros |
| 19,2 | Le han prestado dinero (o usted a ellos) |
| **12,4** | **Viven en su misma cuadra** |
| 2,6 | Son extranjeros |

La correspondencia `P2051S*` → descripción no está publicada por DANE; se estableció reproduciendo el Cuadro 9 del anexo de Capital Social 2023, con una discrepancia máxima de **0,04 pp sobre 33 comparaciones**. Vive en `ETIQUETAS_COMPOSICION_RED` de `src/population/ecp.py`, con un test que la fija.

**Lo que esto dice del generador homofílico tal como está especificado abajo.** La distancia se construye sobre edad, estrato y nivel educativo. De esos tres ejes, el único que aparece medido en la composición del círculo es la educación (72,9 % comparte bachillerato) — y ese porcentaje es en buena parte la prevalencia de base, no homofilia: en Bogotá la mayoría de los adultos es bachiller. **La opinión política estructura la red tres veces más que el vecindario y muy por encima de lo que explican los atributos demográficos** (\(\eta^2 \approx 3\,\%\) sobre la confianza institucional — ver `claude/ANALISIS_HOMOFILIA.md` §2). Este generador sigue siendo válido como **variante comparativa**, pero ya no puede presentarse como la hipótesis empíricamente respaldada: la evidencia respalda homofilia **de opinión** (confianza limitada: Hegselmann-Krause / Deffuant), no demográfica.

### Distancia entre agentes
Sobre las tres variables numéricas fijadas en D12 (excluyendo localidad, que se trata aparte en el generador 3):
$$d(i,j) = \sqrt{w_e \left(z^{edad}_i - z^{edad}_j\right)^2 + w_s \left(z^{estrato}_i - z^{estrato}_j\right)^2 + w_v \left(z^{educ}_i - z^{educ}_j\right)^2}$$

donde \(z^{(\cdot)}\) son los valores estandarizados (media 0, desviación estándar 1) de cada variable, y \(w_e, w_s, w_v\) son pesos por variable.

**Supuesto explícito (no hecho):** por defecto \(w_e = w_s = w_v = 1\) — pesos iguales. La v0.2 decía "sin evidencia todavía para preferir una variable sobre otra"; hoy la evidencia disponible dice algo más fuerte y más incómodo: **ninguna de las tres merece un peso alto**, porque las tres juntas explican ~3 % de la varianza de la opinión simulada. Dejar los pesos en (1,1,1) no es peor que cualquier otra combinación, y eso mismo es el diagnóstico.

### Probabilidad de conexión
Kernel exponencial, decae con la distancia:
$$p_{ij} \propto e^{-\beta \, d(i,j)}$$

\(\beta\) no tiene interpretación directa por sí solo — es el parámetro libre que se calibra numéricamente para que el grado promedio resultante de la red iguale a \(\bar{k}\).

### Pseudocódigo
```text
función generar_red_homofilica(agentes, k_promedio, pesos=(1,1,1)):
    calcular z_edad, z_estrato, z_educ para todos los agentes (estandarizados)
    para cada par (i, j) con i < j:
        d[i,j] = distancia_ponderada(i, j, pesos)
    beta = calibrar_beta(d, k_promedio)
        # búsqueda binaria sobre beta hasta que el grado promedio
        # resultante de la red converja a k_promedio
    aristas = []
    para cada par (i, j):
        p_ij = exp(-beta * d[i,j])
        si random() < normalizar(p_ij):
            aristas.append((i, j))
    retornar aristas
```

### Parámetros libres
\(\bar{k}\), \(\beta\) (derivado por calibración numérica, no fijado a mano), pesos \(w_e, w_s, w_v\).

### Costo computacional
O(N²) — a N=1.000, ~500.000 distancias a calcular, manejable. **Advertencia explícita para A08 (escalamiento):** a 100.000 agentes esto implica ~5.000 millones de pares, 10.000 veces más caro. Ahí sí haría falta una aproximación (k-d tree, blocking por rangos de variables) en vez de fuerza bruta — no es un problema para el prototipo de 1.000, pero se deja anotado para que no se repita, al escalar, un error de diseño que "funciona en el prototipo pero es inviable en producción".

## 5. Generador 3 — Red territorial (bloques por localidad)

### Qué representa
Los agentes interactúan con mayor probabilidad dentro de su propia localidad que con agentes de otras localidades — operacionalización directa de "proximidad territorial" (PROJECT_CONTEXT.md sección 16, RESEARCH.md sección 22). Es un *stochastic block model* con las 20 localidades como bloques.

### 5.1 Advertencia mayor: este generador no tiene objetivo empírico que reproducir

Dos mediciones independientes, ninguna disponible cuando se escribió la v0.2:

1. **ECP Capital Social (§4.1):** solo el **12,4 %** del círculo cercano vive en la misma cuadra. El vecindario estructura la red **tres veces menos** que la opinión política.
2. **Estudios del CNC (Salud Mental Bogotá 2023, n = 15.151; Sustancias Bogotá 2022, n = 10.912), 42 ítems de opinión, 20 localidades:** la localidad explica entre **0,4 % y 2,6 %** de la varianza de opinión, mediana ~1 %. Y **54 % / 63 % de esa varianza aparente es error de muestreo**: la desviación real entre localidades es **0,073 y 0,046** puntos de escala, contra ~1,05 dentro de cada localidad. Estandarizar por composición casi no lo mueve. Detalle en `claude/ANALISIS_HOMOFILIA.md` §8.

**Consecuencia para esta especificación.** El generador territorial está correctamente implementado y sus propiedades matemáticas (9.1) son válidas. Lo que no tiene es un valor de \(h\) que se pueda calibrar contra algo: no hay una segregación de opinión observada en Bogotá a la que apuntar, porque la segregación de opinión por localidad es del orden del ruido muestral. **El barrido \(h \in \{5,10,20,50\}\) sigue siendo útil como análisis de sensibilidad — "¿cuánto cambiaría el resultado si Bogotá estuviera territorialmente segregada?" — pero no como búsqueda del valor correcto.** Ese valor, según los datos, está cerca de \(h \approx 1\), que es la red aleatoria.

Esto se registra aquí y no se borra el generador: la pregunta "¿y si lo estuviera?" es exactamente el tipo de escenario contrafáctico para el que existe el laboratorio.

### Fórmula
$$p_{ij} = \begin{cases} p_{intra} & \text{si localidad}_i = \text{localidad}_j \\ p_{inter} & \text{si localidad}_i \neq \text{localidad}_j \end{cases}$$

### Parámetro de diseño — razón de homofilia territorial
$$h = \frac{p_{intra}}{p_{inter}}$$

Se barre \(h \in \{5, 10, 20, 50\}\), con la lectura de 5.1: es un barrido de sensibilidad, no una calibración.

### Calibración de \(p_{intra}, p_{inter}\) dado \(\bar{k}\) y \(h\)
Con \(n_l\) = número de agentes en la localidad \(l\) dentro de la muestra de 1.000 (proporcional a las poblaciones reales de las proyecciones DANE-SDP ya usadas en DATA_SPECIFICATION.md):

$$\bar{k} = \frac{1}{N}\sum_l n_l \left[ p_{intra}(n_l - 1) + p_{inter}(N - n_l) \right], \qquad p_{intra} = h \cdot p_{inter}$$

Esta es una ecuación lineal en \(p_{inter}\): se despeja directamente, sin necesidad de búsqueda numérica (a diferencia de \(\beta\) en el generador homofílico).

### Pseudocódigo
```text
función generar_red_territorial(agentes, k_promedio, h):
    n_l = tamaño de cada localidad dentro de la muestra de agentes
    p_inter = resolver_ecuacion_lineal(k_promedio, h, n_l, N)
    p_intra = h * p_inter
    aristas = []
    para cada par (i, j) con i < j:
        p_ij = p_intra si localidad[i] == localidad[j] sino p_inter
        si random() < p_ij:
            aristas.append((i, j))
    retornar aristas
```

### Parámetros libres
\(\bar{k}\), \(h\).

### Costo computacional
O(N²) en el peor caso, pero optimizable de forma directa: agrupando primero por localidad, las conexiones intra-localidad solo requieren recorrer pares dentro de cada bloque (mucho más chico que N²), y las inter-localidad pueden muestrearse de forma agregada sin evaluar cada par individualmente.

## 6. Tabla comparativa

| Generador | Parámetros libres | Fundamento empírico (v0.3) | Costo a N=1.000 | Costo a N=100.000 (A08) |
|---|---|---|---|---|
| Aleatoria (Erdős–Rényi) | \(\bar{k}\) | Ninguno por diseño — es el control. Irónicamente, es el que más se parece a lo medido en el eje territorial (§5.1) | Trivial | Trivial |
| Homofílica (demográfica) | \(\bar{k}\), \(\beta\) (derivado), pesos \(w_e,w_s,w_v\) | RESEARCH.md §22 (Jiang et al., 2022) como mecanismo general; **para Bogotá, los tres ejes explican ~3 % de la opinión** (§4.1) | Manejable (~500K pares) | Requiere aproximación (k-d tree / blocking) |
| Territorial (bloques por localidad) | \(\bar{k}\), \(h\) | RESEARCH.md §22; **sin objetivo empírico — 12,4 % de cuadra compartida, ~1 % de varianza por localidad y la mitad es ruido** (§5.1) | Manejable, optimizable por agrupación | Manejable con agrupación por bloques |
| *(candidato nuevo)* Homofilia de opinión — confianza limitada | \(\bar{k}\), umbral \(\varepsilon\) | **39,5 % del círculo cercano comparte opiniones políticas** (§4.1) — el único eje con respaldo | Igual que la homofílica | Igual que la homofílica |

La cuarta fila **no está implementada**. Se lista porque es a lo que apunta la evidencia y porque dejarla fuera de la tabla comparativa haría parecer que el campo de opciones sigue siendo el de la v0.2. Requiere además cambiar de familia de modelo (Hegselmann-Krause / Deffuant en vez de Friedkin-Johnsen), así que su costo real no es el del generador sino el de `src/opinion/`.

## 7. Cómo cambió la decisión de A07

La v0.2 decía: implementar los tres generadores y **dejar que el Experimento 2 informe la decisión**. Eso se hizo. El resultado no fue el previsto, en dos pasos:

- **Experimento 2:** la homofilia dominaba el resultado del modelo. Parecía que la red importaba mucho.
- **Experimento 3** (validación contra la ECP, cuatro olas reales): la estructura de red **casi no afecta el ajuste a datos** — rango 0,015 entre nueve configuraciones, contra 0,0045 de dispersión entre semillas del mismo generador. La red mueve el resultado interno del modelo, pero no mueve su acuerdo con Bogotá.

La conjunción de los dos es lo que reorienta A07: **el generador importa para lo que el modelo hace, y no importa para si el modelo acierta.** Elegir entre los tres por ajuste no es posible, porque los tres ajustan casi igual de bien.

La evidencia que sí discrimina no vino del experimento sino de las mediciones de §2.1, §4.1 y §5.1. Y discrimina en contra de dos de los tres candidatos: el territorial no tiene fenómeno que reproducir, y el demográfico se construye sobre un eje casi ortogonal a la opinión.

**Decisión, registrada como D15 en PROJECT_CONTEXT.md y aprobada el 16 de septiembre de 2026:**

1. Fijar \(\bar{k} = 5\) como valor central del prototipo (medido, §2.1), conservando 4 y 8 como sensibilidad.
2. Mantener los tres generadores implementados como **variantes de sensibilidad**, no como candidatos a "el correcto": la aleatoria como control, la territorial como contrafáctico de segregación, la homofílica demográfica como contrafáctico de estratificación.
3. Reportar siempre resultados con el rango entre generadores, en vez de reportar uno solo.
4. Abrir como línea propia la homofilia de opinión (confianza limitada), que es la única con respaldo empírico y la única que cambiaría el diagnóstico del Experimento 3.

Esto cierra A07 en el sentido de que **ya no hay una elección pendiente entre los tres**, y la abre en otro: cuál es el mecanismo, no cuál es el generador. Esa segunda pregunta queda registrada como **A18** en PROJECT_CONTEXT.md.

### 7.1 Qué cambió en el código al aprobarse D15

| Archivo | Antes | Ahora |
|---|---|---|
| `src/experiments/experimento3.py` | `K_MEDIOS = [4, 8, 16]` | `K_MEDIOS = [4, 5, 8]` |
| `config/experiment_2.yaml` | `k_promedio: [5, 10, 15, 20]` ×3 | `k_promedio: [4, 5, 8]` ×3 |
| `config/experiment_2_degroot.yaml` | ídem | ídem |

El barrido del Experimento 2 baja de **24 a 18 configuraciones** (3 + 3 + 3×4). El Experimento 3 se re-corrió completo con el barrido nuevo: **el veredicto no cambia: las cuatro predicciones siguen fallando.**

| | Pre-registro \(\bar{k} \in \{4,8,16\}\) | Re-corrida \(\bar{k} \in \{4,5,8\}\) | Umbral |
|---|---|---|---|
| P1 — movimiento máx. de la media | 0,0290 (6,5× *menos* que lo observado: 8,9×) | **0,0398** (6,5×) | ≥ 0,05 · **falla en las dos** |
| P2 — mejor error de sd | 0,0751 | **0,0692** | < 0,05 · **falla en las dos** |
| P3 — corridas con mínimo interior | 0 / 720 | **0 / 720** | ≥ 1 · **falla en las dos** |
| P4 — corridas con máximo interior en la cola baja | 0 / 720 | **0 / 720** | ≥ 1 · **falla en las dos** |
| FJ φ=0,3 (mejor modelo), W1 total | 0,5310 | **0,5291** | — |
| Congelado | 0,6265 | **0,6265** | — |
| Ruido | 0,6287 | **0,6288** | — |
| DeGroot | 0,9387 | **0,8490** | — |

Tres cosas sí se movieron, y conviene decirlas en vez de reportar solo "no cambió":

1. **Con redes más ralas el modelo se mueve algo más** (0,029 → 0,040) y la razón contra lo observado baja de 8,9× a 6,5×. Dirección correcta, magnitud insuficiente: sigue sin alcanzar el umbral de 0,05.
2. **DeGroot mejora y adelanta a FJ φ=0,9** (0,8490 contra 0,8651). Con menos vecinos promedia más lento y colapsa menos. La afirmación que importa no cambia: **sigue siendo peor que el ruido.**
3. **"Congelado" da exactamente el mismo número** (0,6265). Tenía que darlo —no depende de la red— y sirve de control de que la re-corrida no alteró nada más.

La corrida pre-registrada sigue siendo **la reportada** en `claude/EXPERIMENT_3_RESULTS.md`; esta es una verificación de robustez y no la reemplaza. Salidas en `data/processed/exp3_k_d15/` (1.260 corridas, 33 min).

## 8. Supuestos explícitos (no hechos) que quedan documentados

- ~~Los rangos propuestos para \(\bar{k}\) (5–20) no derivan de datos observados de Bogotá~~ — **resuelto en §2.1**: \(\bar{k} \approx 5\) está medido. Quedan las cuatro advertencias de esa sección (tope en 10, 2021 contaminado, sin dato en 2017, lazos fuertes únicamente).
- ~~Pesos iguales en la distancia homofílica por falta de evidencia~~ — **reformulado en §4.1**: hay evidencia, y dice que los tres ejes importan poco. Los pesos siguen en (1,1,1) por falta de razón para diferenciarlos, no por falta de información.
- El rango de \(h\) (5–50) es un barrido de sensibilidad sin objetivo empírico (§5.1).
- Ningún generador incorpora todavía una capa de hogar (lazos fuertes intra-hogar, disponible en principio vía el capítulo J de Multipropósito) — se mantiene fuera del prototipo por el Principio 5 (evitar complejidad prematura), no por falta de datos. Nota: `P2047`/`P2049` incluyen familia (50,2 % del círculo), así que parte de esa capa ya está adentro del \(\bar{k}\) medido.
- La independencia entre los tres mecanismos (edad/estrato/educación por un lado, localidad por otro) es un supuesto de diseño del generador homofílico, no una propiedad verificada de la población real.
- **Supuesto nuevo, y el más fuerte de todos:** que la composición del círculo cercano medida por la ECP (§4.1) describe la red de *influencia de opinión*. La ECP mide con quién se convive, no quién convence a quién. Un corte transversal no revela dirección de influencia: puede que la gente comparta opiniones con su círculo porque el círculo la influyó, o que haya elegido el círculo por sus opiniones. El modelo supone lo primero.

## 9. Implementación — decisiones tomadas al escribir el código

Los tres generadores están implementados en `src/network/` (`base.py`, `random_network.py`, `homophilic_network.py`, `territorial_network.py`), con pruebas en `tests/test_network_generators.py`. Escribir el código obligó a cerrar seis puntos que la especificación dejaba abiertos. Siguiendo la Regla 3 del prompt maestro, se registran aquí como **decisiones de implementación (DI)**, no como decisiones metodológicas D0X: son revisables sin reabrir la especificación, y están documentadas también en el docstring de cada módulo.

| ID | Punto abierto | Decisión |
|---|---|---|
| DI-N1 | La especificación llama \(p_{ij}\) tanto a la probabilidad de conexión como al peso de influencia | `generar()` devuelve un `NetworkResult` con **ambos**: `adjacency` (red realizada, booleana y simétrica) y `W` (adyacencia normalizada por filas, lo que consumen DeGroot/Friedkin-Johnsen). La normalización queda en un solo lugar, y la red realizada queda disponible para medir propiedades estructurales en el Experimento 2 |
| DI-N2 | Representación de la red | `numpy` denso. A N=1.000 una matriz float64 pesa 8 MB — trivial, y el código queda verificable por inspección. Al abordar A08 habrá que pasar a `scipy.sparse`; queda anotado en el código |
| DI-N3 | Agentes con grado 0 (aparecen con \(\bar{k}\)=5, y son ~15% con \(\bar{k}\)=2) | Peso propio \(w_{ii}=1\): el agente aislado **conserva su opinión**. No se le inventan aristas y el conteo queda en la metadata. La alternativa (fila de ceros) haría colapsar su opinión a 0 por un artefacto de implementación, no por el modelo. **Nota v0.3:** esto dejó de ser solo una salvaguarda técnica — el 26 % de los bogotanos declara red de tamaño 0 (§2.1), así que los aislados son un hecho de la población, no un residuo del muestreo de la red |
| DI-N4 | ¿Red dirigida o no dirigida? | No dirigida: las tres definiciones de \(p_{ij}\) son simétricas. Se muestrea el triángulo superior y se simetriza. **`W` sí es asimétrica**, porque cada fila se normaliza por el grado de ese agente — dos agentes conectados se influyen mutuamente, pero no con la misma intensidad si tienen distinto número de vecinos. Es lo esperado en DeGroot/Friedkin-Johnsen |
| DI-N5 | Qué significa `normalizar(p_ij)` en el pseudocódigo de la sección 4 | Lectura directa: \(p_{ij} = e^{-\beta d(i,j)}\), sin constante adicional. Como \(d \geq 0\), ya es una probabilidad válida en \((0,1]\). Añadir una segunda constante multiplicativa volvería el par \((c, \beta)\) no identificable con una sola condición (\(\bar{k}\)) |
| DI-N6 | Límite del kernel exponencial con variables discretas | Si la distancia se calcula solo sobre `estrato` y `nivel_educativo` (discretas), ~23% de los pares queda a distancia exactamente 0 y se conecta con probabilidad 1 por alto que sea \(\beta\): existe un **grado mínimo alcanzable** (~234 en la prueba) por debajo del cual no se puede calibrar. Con los pesos por defecto (1,1,1) no ocurre porque `edad` rompe los empates. Cuando ocurre, el generador **falla explícitamente** en vez de devolver una red mucho más densa de la pedida, que arruinaría la comparabilidad del Experimento 2 sin avisar |

### 9.1 Dos propiedades del modelo territorial que conviene tener presentes al leer el Experimento 2

Ninguna de las dos es un error: son consecuencias de la fórmula de la sección 5, y se detectaron al verificar el código.

**(a) El grado no es homogéneo entre localidades.** Con \(p_{intra}\) constante, un agente de Suba (~17% de la muestra) tiene muchos más vecinos potenciales dentro de su localidad que uno de Sumapaz (~0,1%), y termina con más vecinos. Con \(\bar{k}\)=10 y \(h\)=20, el grado esperado va de ~3,6 (Sumapaz) a ~15,0 (Suba). \(\bar{k}\) es el promedio poblacional, no el grado de cada quien. Si en el Experimento 2 la opinión de las localidades grandes converge más rápido, puede deberse a esto y no a la dinámica de opinión. El código registra `grado_esperado_por_localidad` en la metadata para que el efecto sea visible.

**(b) La segregación territorial tiene un techo, y el barrido \(h\) satura.** Cuando \(h \to \infty\), \(p_{intra}\) no crece indefinidamente: tiende a \(\bar{k}N / \sum_l n_l(n_l-1)\), porque las localidades no tienen suficientes pares internos para absorber todo el grado. Medido sobre una población de prueba con proporciones del orden de las de Bogotá (\(\bar{k}\)=10):

| \(h\) | \(p_{intra}\) | \(p_{inter}\) | % del techo | segregación observada |
|---|---|---|---|---|
| 5 | 0,0363 | 0,0073 | 34% | 3,6× |
| 10 | 0,0541 | 0,0054 | 51% | 5,4× |
| 20 | 0,0717 | 0,0036 | 68% | 7,2× |
| 50 | 0,0890 | 0,0018 | 84% | 8,9× |
| ∞ | 0,1060 | 0 | 100% | 10,6× |

("segregación observada" = fracción de aristas intra-localidad dividida por la fracción de pares intra-localidad que habría por azar.)

El barrido propuesto \(h \in \{5,10,20,50\}\) cubre de 3,6× a 8,9× sobre un máximo de 10,6×, así que **es un rango adecuado** — no hace falta ampliarlo. Pero la relación entre \(h\) y la segregación real es fuertemente cóncava: pasar de \(h\)=20 a \(h\)=50 no duplica la segregación, la sube un 24%. Leer los resultados como función de \(h\) sin tener esto presente llevaría a subestimar el efecto de la estructura territorial. El código guarda `saturacion_h` (la columna "% del techo") en la metadata de cada corrida.

### 9.2 Diagnósticos de red

`src/network/base.py` incluye `diagnosticos_red()`, que mide, para cualquiera de los tres generadores y contra la línea base del azar: fracción de aristas intra-localidad y razón de segregación territorial; y, para edad, estrato y nivel educativo, la diferencia media entre agentes conectados dividida por la diferencia media entre todos los pares (valores < 1 = homofilia). Sirve para **verificar**, en vez de suponer, que cada generador induce la estructura que dice inducir, y es el insumo descriptivo del Experimento 2 junto con las métricas de opinión.

Verificado en las pruebas: la red aleatoria da ~1,0 en todos los índices (no induce ninguna estructura — es el control); la homofílica baja la razón a 0,16–0,28 en las tres variables; la territorial da 7,1× de segregación con \(h\)=20 pero deja la homofilia por edad en 0,97, es decir, no induce homofilia demográfica salvo la que ya viene correlacionada con el territorio.

### 9.3 Costo medido

~10 ms por red a N=1.000, en los tres generadores, tras memoizar lo que no depende de la semilla (la matriz de distancias y \(\beta\) en el homofílico, la máscara de localidad en el territorial, los índices de pares en los tres). El barrido completo del Experimento 2 (24 configuraciones × 200 runs ≈ 4.800 redes) toma menos de un minuto en generación de redes — el costo dominante de la corrida estará en la dinámica de opinión, no aquí. Sin la memoización, el generador homofílico costaba 110 ms por red.

## 10. Qué queda pendiente

- ~~Registrar la decisión de §7 como D0X~~ ✅ **D15, aprobada el 16/09/2026.**
- ~~Ajustar `config/` y `experimento3.py` al barrido \(\bar{k} \in \{4,5,8\}\) y re-verificar el Experimento 3~~ ✅ **§7.1.**
- Re-correr el **Experimento 2** con el barrido nuevo. No se ha hecho: los resultados guardados en `experiments_output/exp2_*` son del barrido viejo (\(\bar{k}\) hasta 20) y ya no corresponden a la configuración vigente.
- Evaluar la implementación de un generador de homofilia de opinión (confianza limitada), que requiere a su vez un modelo de la familia Hegselmann-Krause / Deffuant en `src/opinion/`.
- Excluir los códigos 8/9 de `estrato` de la componente de estrato de la distancia (A17 de PROJECT_CONTEXT.md). Son 39 agentes de 168.200 en el receptor, pero hoy entran a la distancia como si fueran estratos extremos.
- Al interpretar cualquier resultado territorial, controlar el efecto descrito en 9.1(a) — grado heterogéneo por tamaño de localidad — antes de atribuir diferencias entre localidades a la dinámica de opinión.
- Diseñar, en una fase posterior, la aproximación computacional (k-d tree / blocking) y la representación sparse necesarias para escalar más allá de N=1.000 (relevante cuando se aborde A08).

---

*Documento vivo — la decisión de A07 se registra en PROJECT_CONTEXT.md con formato D0X, siguiendo la misma convención usada para A05 y A06. Fuentes de las mediciones de esta versión: `claude/ANALISIS_HOMOFILIA.md` (§2, §5.2, §8), `claude/EXPERIMENT_3_RESULTS.md` (§5), `src/population/ecp.py`.*
