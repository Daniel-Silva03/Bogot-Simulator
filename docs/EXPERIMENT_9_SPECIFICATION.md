# EXPERIMENT 9 — SPECIFICATION

**¿Puede un modelo de lenguaje proponer el escenario de un periodo —cuánto se mueve la opinión y cuánto se divide— mejor que suponer que no cambia nada?**

Proyecto: Bogotá Social Simulator
Versión: 0.1 — **pre-registro**
Fecha: 28 de septiembre de 2026
Estado: **sin código y sin ninguna llamada al modelo**. Se escribe antes de las dos cosas.
Origen: recomendación de revisar MiroFish (motor de simulación con agentes LLM que parte de un documento semilla); evaluación en la conversación del 28/09/2026.

---

## 1. La pregunta, acotada

El proyecto estableció que la opinión en Bogotá cambia por el **contexto de cada
periodo**, y que dos números por periodo —cambio de **nivel** y de **dispersión**—
reproducen la distribución observada al nivel del error de muestreo
(`FORZAMIENTO_CATEGORICO.md`). El motor de escenarios funciona con esos dos
números, pero **hoy los escribe una persona a mano**.

MiroFish propone que un modelo de lenguaje lea un documento del mundo real y
simule lo que viene. Su parte de simular personas ya la probamos y falla: el
Experimento 8 mostró que un LLM aplana la variación entre personas (0,30×) y
exagera la variación entre instituciones (3,3×). **La parte que no hemos probado
es la otra: si un LLM puede leer el contexto y estimar esos dos números.**

> **Dado el estado de la opinión al inicio de un periodo y lo que pasó en Bogotá
> durante ese periodo, ¿propone un LLM un cambio de nivel y de dispersión que,
> aplicado con el motor del proyecto, se acerque a lo que la encuesta midió al
> final, más que suponer que nada cambió?**

Es la versión falsable de «del documento al escenario». **El LLM no produce la
opinión de ninguna persona**: solo propone los dos números. La población, el
forzamiento y la comparación son los del proyecto.

---

## 2. Las transiciones

Doce transiciones medidas, las mismas contra las que se evaluaron los
Experimentos 3 a 7. El LLM **nunca** ve el valor final de ninguna.

| Serie | Variable | Transiciones |
|---|---|---|
| **ECP** (DANE) | Confianza institucional, índice de 13 ítems, 1–5 | 2013→2017 · 2017→2019 · 2019→2021 · 2021→2023 |
| **EPC** (Bogotá Cómo Vamos) | Gestión del alcalde, 1–5 | 2014→2015 · 2015→2017 · 2017→2018 · 2018→2019 · 2019→2022 · 2022→2023 · 2023→2024 · 2024→2025 |

Para referencia (no se le muestran al modelo), los cambios de nivel observados van
de −0,43 (EPC 2014→2015) a +0,41 (EPC 2019→2022). La transición EPC 2022→2023
**no es distinguible de cero** (z = −1,78, `ANALISIS_DISENO_MUESTRAL.md`) y se
reporta, pero no se usa para juzgar el signo.

---

## 3. Diseño

### 3.1 Lo que recibe el LLM, por transición

1. **La variable**, con la pregunta textual y las anclas de la escala.
2. **El estado inicial**: media, desviación estándar y distribución por categorías
   (o por quintiles, en el índice de la ECP) del año de partida, ponderados.
3. **El periodo**: año de inicio y de fin, y quién gobernaba Bogotá y el país.
4. **Solo en el brazo B**: el dossier del periodo (§3.3).

Y se le pide, en JSON: cambio de nivel, cambio de dispersión, un intervalo del
90 % para cada uno y una justificación de no más de 150 palabras. Temperatura
0,7, **10 repeticiones por transición**; la propuesta del brazo es la mediana y la
dispersión entre repeticiones se reporta.

### 3.2 Los dos brazos

| Brazo | Qué sabe el modelo | Qué mide |
|---|---|---|
| **A — memoria propia** | Solo §3.1, puntos 1 a 3 | Si el conocimiento general del modelo sobre Bogotá alcanza |
| **B — semilla documental** | Además, el dossier del periodo | La idea de MiroFish: leer un documento y proponer lo que viene |

### 3.3 El dossier del brazo B

Se arma **antes** de cualquier llamada, con una regla fija, y se versiona en el
repositorio:

- Entre 10 y 20 hechos por periodo, tomados de una sola fuente de referencia
  general (cronologías anuales de Bogotá y Colombia en una enciclopedia o en un
  medio de referencia), elegida y escrita en este documento antes de armarlo.
- **Se elimina cualquier línea que mencione encuestas, aprobación, favorabilidad,
  confianza o percepción ciudadana.** El dossier describe lo que pasó, no lo que
  la gente opinó.
- Mismo formato y extensión en los doce periodos.

*Pendiente dentro del pre-registro:* nombrar la fuente concreta. Se añade como
enmienda fechada **antes** de armar el primer dossier.

> **Enmienda 1 — 28/09/2026, antes de armar ningún dossier.** Fuente fijada,
> aprobada por Daniel: **las cronologías anuales de Wikipedia en español** para
> Colombia y para Bogotá de cada año del periodo. Si para un año no existe
> cronología propia de Bogotá, se usan solo los hechos de Bogotá de la de
> Colombia, y eso se anota en el dossier. Se aplican sin excepción las reglas de
> arriba (10 a 20 hechos, sin encuestas ni aprobación, mismo formato).

> **Enmienda 2 — 29/09/2026, antes de abrir ninguna cronología.** Decisiones de
> Daniel. Motivo: quien arma el dossier **conoce los cambios observados** (§2), así
> que la selección no puede depender de su criterio.
>
> 1. **Fuente concreta.** Wikipedia en español no tiene cronología anual de
>    Bogotá (solo `Anexo:Cronología de Bogotá`, general). Se usa la cláusula de
>    respaldo de la enmienda 1 en **los doce** dossiers: la fuente es
>    `Anexo:Colombia en AAAA`, y los hechos de Bogotá salen de ahí. Se anota la
>    fecha de consulta.
> 2. **Años.** Del año de inicio al año final de la transición, **inclusive**
>    (2018→2019 usa 2018 y 2019). Limitación aceptada: pueden entrar hechos
>    posteriores al trabajo de campo de la encuesta final, o anteriores al de la
>    inicial.
> 3. **Unidad.** Cada entrada fechada de la sección de acontecimientos. Se
>    excluyen nacimientos, fallecimientos, deportes y espectáculos.
> 4. **Filtro de opinión** (antes de seleccionar): se descarta toda entrada que
>    contenga, sin distinguir mayúsculas ni tildes, *encuesta, sondeo,
>    aprobación, favorabilidad, confianza* o *percepción*.
> 5. **Selección: 15 hechos exactos por dossier.** Son de Bogotá las entradas que
>    contienen *Bogotá, bogotano/a, Distrito Capital* o *TransMilenio*.
>    - Si hay 15 o más de Bogotá, se toman 15 **espaciadas parejo** en orden
>      cronológico: posiciones `round(i·(n−1)/14)`, i = 0…14.
>    - Si hay menos, entran todas, y el resto hasta 15 sale de las demás
>      entradas con la misma regla de espaciado.
>    - La selección la hace un script sobre la extracción guardada, no una
>      persona.
> 6. **Texto.** Fecha y primera oración de la entrada, sin enlaces ni notas y
>    **sin reescribir**.
> 7. **Versionado.** Por transición se guardan en el repositorio la extracción
>    completa (todas las entradas elegibles, para auditar) y el dossier final.
>    Atribución: Wikipedia en español, CC BY-SA 4.0.

> **Enmienda 3 — 29/09/2026, después de ver los dossiers y antes de cualquier
> llamada al modelo.** Decisiones de Daniel.
>
> 1. **Texto: entrada completa**, no primera oración (cambia el punto 6 de la
>    enmienda 2). Motivo técnico: cortar en el primer punto rompía dos entradas
>    («Tigres F.» por la abreviatura F. C.; y el racionamiento de agua de abril
>    de 2024, cuya primera oración en Wikipedia es un fragmento). **La selección
>    no cambia**: el filtro y la marca de Bogotá ya se aplicaban a la entrada
>    completa. Verificado: los doce conteos son idénticos antes y después.
> 2. **La regla de selección se congela sin cambios**, aunque trae sobre todo
>    conciertos, festivales y ferias, con pocos hechos de gobierno. Cambiarla
>    después de ver el contenido, conociendo los resultados, sería elegir a
>    criterio. **Limitación registrada:** el dossier refleja lo que la
>    cronología nacional de Wikipedia dice de Bogotá, que no es lo que un
>    analista pondría. En 2014→2015 (3 de Bogotá), 2022→2023 (6) y 2023→2024
>    (8) el resto sale de hechos nacionales. El contraste brazo A / brazo B
>    dirá si un dossier así aporta.
> 3. **Versionado (ajusta el punto 7 de la enmienda 2).** En vez de copiar la
>    extracción completa (~200 KB) al repositorio, se versionan las
>    **revisiones fijas** de cada página y el **script exacto**
>    (`config/experimento9/extraer_dossiers.js`), que la regenera y aplica la
>    regla. `config/experimento9/dossiers/HUELLAS.txt` guarda la huella
>    SHA-256 de cada dossier; volver a correr el script debe reproducirlas.
>
> Lo que va al modelo en el brazo B es solo la sección «Hechos» de cada
> dossier; el encabezado (fuente, conteos) es para auditoría.

### 3.4 Cómo se evalúa

La propuesta del LLM se aplica a la distribución inicial con el **ladeo
categórico** del proyecto (`src/opinion/forzamiento_categorico.py`), el mismo
forzamiento del motor de escenarios. Resultado: una distribución predicha para el
año final.

| Métrica | Qué es | Papel |
|---|---|---|
| **W1 / piso** | Wasserstein-1 entre la distribución predicha y la observada, dividido por el piso de ruido muestral de esa transición | **Principal**: la misma vara de los Experimentos 6 y 7 |
| Error de nivel | \|Δ̂ − Δ\| | Secundaria |
| Error de dispersión | \|Δ̂sd − Δsd\| | Secundaria |
| Signo | ¿acierta la dirección del nivel? | Secundaria; excluye 2022→2023 |
| Cobertura | fracción de transiciones cuyo cambio observado cae en el intervalo del 90 % declarado | Calibración |

### 3.5 Los baselines

Cualquier resultado del LLM se compara contra estos, sobre las mismas transiciones:

| Baseline | Propuesta | Por qué |
|---|---|---|
| **Sin cambio** | nivel 0, dispersión 0 | El nulo: lo que asume hoy quien no escribe escenario |
| **Tendencia** | el cambio de la transición anterior de la misma serie | Lo que haría una persona mirando solo la serie. No existe para la primera transición de cada serie |
| **Oráculo** | el cambio observado | El mejor caso posible del método: el piso contra el que nada puede ganar |

### 3.6 Memoria: el control que decide si el resultado vale

Los microdatos y los informes de la ECP y la EPC son públicos, y pueden estar en
el entrenamiento del modelo. Un LLM que **recuerda** la cifra de 2021 no está
leyendo el contexto.

**Sonda de memoria, antes del experimento y por transición:** se le pregunta
directamente al modelo cuál fue la media publicada de la variable en el año final.
Si acierta a menos de 0,10, la transición se marca **«en memoria»**. Todos los
resultados se reportan en total y **separados en «en memoria» y «fuera de
memoria»**. Si no queda ninguna transición fuera de memoria, el experimento no
puede responder su pregunta, y así se reporta.

### 3.7 Enmienda 4 — lo que el pre-registro dejaba abierto

> **Enmienda 4 — 29/09/2026, antes de escribir el código y antes de cualquier
> llamada al modelo.** Daniel aprobó el plan de implementación y delegó en
> Claude estas decisiones. Todas se toman sin haber visto ninguna respuesta del
> modelo; los cambios observados (§2) sí se conocen, y por eso cada decisión
> se toma por una razón que no depende de ellos.
>
> 1. **Cobertura (§3.4, P5, regla 2).** Con 10 repeticiones hay 10 intervalos
>    por transición. El intervalo del brazo es la **mediana de los límites
>    inferiores y la mediana de los superiores** de las repeticiones válidas:
>    es el intervalo de la propuesta que se evalúa, que también es una
>    mediana. La **cobertura principal es la del nivel**, sobre las 12
>    transiciones: §3.4 habla de «el cambio observado», en singular, y el
>    nivel es el número que las demás predicciones juzgan. Se reportan además,
>    como secundarias, la cobertura de la dispersión y la cobertura por
>    repetición (fracción de los ~120 intervalos individuales que cubren).
> 2. **Sonda de memoria (§3.6).** Ninguna de las dos variables tiene una
>    «media publicada» en la escala 1–5: el índice de 13 ítems de la ECP lo
>    construye el proyecto, y Bogotá Cómo Vamos publica proporciones
>    (1–2 / 3 / 4–5; `epc_bcv.ANCLAS_PUBLICADAS`). Se decide:
>    - **Sonda principal (pre-registrada):** se describe la variable con
>      exactitud y se pide su media ponderada en la escala 1–5 del año final;
>      se compara con la media ponderada de los microdatos públicos, que es la
>      cifra que cualquiera puede calcular y publicar. Umbral: 0,10. Una
>      llamada por transición, **temperatura 0**: es la condición en la que un
>      modelo reproduce mejor lo que recuerda, así que marca memoria de más y
>      no de menos, que es el error seguro para P6.
>    - **Sonda complementaria (no pre-registrada), solo EPC:** se pide el
>      porcentaje que calificó la gestión como buena o muy buena (4–5), que es
>      la cifra que BCV sí publica. Acierto: a menos de 5 puntos
>      porcentuales. Sirve **solo como análisis de sensibilidad**: P6 y la
>      regla 3 se recalculan marcando «en memoria» a la transición que caiga en
>      cualquiera de las dos sondas. El veredicto oficial usa la principal.
>    - **Limitación registrada:** la ECP no tiene cifra publicada comparable al
>      índice, así que su memoria solo se sondea por la media.
>    - Costo: 12 + 8 llamadas.
> 3. **W1 y piso (§3.4).** La propuesta ladeada es una distribución exacta
>    sobre la grilla, y la observada es la distribución ponderada del año
>    final sobre la misma grilla. **W1 se calcula exacto entre las dos**, sin
>    sortear agentes: la métrica es determinista y la diferencia entre brazos
>    no carga ruido de reparto sobre doce puntos. **El piso** es el de DI-X4:
>    W1 medio entre dos muestras de **n = 1000** (el tamaño de las poblaciones
>    de los Experimentos 6 y 7) de la distribución observada del año final,
>    200 réplicas, semilla fija. Consecuencia que se acepta: el oráculo puede
>    quedar por debajo de 1× el piso, porque la predicción no lleva ruido de
>    mil agentes. El piso es la unidad de medida, no un umbral.
> 4. **Grilla de la ECP.** La teórica: todas las medias de *n* ítems en 1–5
>    con *n* de 7 a 13 (233 valores; `FORZAMIENTO_CATEGORICO.md` §3 mostró
>    que da lo mismo que las grillas empíricas). Verificado: los cinco años
>    de la ECP caen exactos sobre ella.
> 5. **«Tendencia» no existe en la primera transición de cada serie.** Las
>    comparaciones contra «tendencia» (P3, regla 1) se hacen sobre las **10
>    transiciones comunes**, recalculando la mediana del brazo sobre ese mismo
>    subconjunto. La tendencia es el cambio crudo de la transición anterior,
>    sin reescalar por años (§3.5 no lo pide).
> 6. **Casos borde.** Un Δ de nivel propuesto exactamente 0 cuenta como signo
>    fallado (P1). Un objetivo infactible en la grilla se proyecta al borde
>    alcanzable y se cuenta (DI-M3s del motor). Una respuesta que no se puede
>    leer no es un dato: se pide otra repetición hasta tener 10 válidas, con
>    un tope de 20 intentos por transición y brazo; si quedan menos de 10, se
>    usa la mediana de las que haya y se reporta.
> 7. **Qué recibe el modelo, en concreto (§3.1).** En la EPC, la distribución
>    por las cinco categorías; en la ECP, los quintiles ponderados del índice.
>    El texto de la pregunta de la EPC se arma con las anclas del formulario
>    (1 = muy mala gestión, 5 = muy buena), porque el repositorio no guarda el
>    enunciado literal. Quién gobernaba: tabla fija en el código.

---

## 4. Predicciones pre-registradas

| # | Predicción | Umbral |
|---|---|---|
| **P1** | El LLM acierta la **dirección** del cambio de nivel en la mayoría de los casos | signo correcto en ≥ 8 de 11 (brazo B) |
| **P2** | El LLM **le gana a «sin cambio»** en el conjunto | mediana de W1/piso del brazo B < la de «sin cambio» |
| **P3** | **Pero no le gana a la tendencia** por un margen material | mejora del brazo B sobre «tendencia» < 20 % en W1/piso |
| **P4** | El LLM **no predice la dispersión**: su error de dispersión no es menor que el de «sin cambio» | error mediano de dispersión del brazo B ≥ el de «sin cambio» |
| **P5** | El LLM está **sobreconfiado**: sus intervalos son demasiado estrechos | cobertura del 90 % declarado < 70 % |
| **P6** | Lo que gana, lo gana **por memoria** | fuera de memoria, el brazo B no le gana a «sin cambio» |

**Por qué espero esto.** Un LLM conoce los grandes relatos (un alcalde
impopular, la pandemia) y debería acertar direcciones. Pero el Experimento 8
mostró que no calibra magnitudes; la dispersión es algo sobre lo que ningún
relato habla; y la literatura documenta que estos modelos son *"more certain than
they should be"*. P6 es la que más me importa: si el modelo solo gana donde
recuerda, no sirve para escenarios nuevos, que es justo para lo que lo
queremos.

**Lo que falsaría mi expectativa, y sería una buena noticia:** que el brazo B le
gane a «sin cambio» y a «tendencia» **fuera de memoria**, con cobertura
razonable. Significaría que el paso «del documento al escenario» es
automatizable.

---

## 5. Regla de decisión

El LLM se adopta como **asistente para proponer escenarios** —la propuesta
siempre la revisa una persona antes de correrla— **solo si se cumplen las tres**:

```
    1. W1/piso mediana del brazo B  ≤  0,8 × la de «sin cambio»
                                  y ≤  0,9 × la de «tendencia»
    2. cobertura del intervalo del 90 %  ≥  70 %
    3. fuera de memoria, el brazo B no es peor que «sin cambio»
```

- **Si falla 1:** el LLM no aporta números. Se puede usar para redactar la
  descripción de un escenario, nunca para fijar sus cifras.
- **Si pasa 1 pero falla 2:** puede proponer la dirección y el tamaño central,
  pero la incertidumbre la fija una persona.
- **Si pasa 1 y 2 pero falla 3:** el resultado es memoria. Sirve para
  reconstruir el pasado y no para escenarios nuevos; no se adopta.
- **Brazo A contra brazo B:** si A iguala a B, el dossier no aporta y la idea de
  MiroFish —leer un documento— no es lo que explica el resultado.

---

## 6. Costo y límites

- **Llamadas:** 12 transiciones × 2 brazos × 10 repeticiones = 240, más 12 de la
  sonda de memoria. Con el modelo del Experimento 8 son unos pocos dólares.
- **Modelo:** el mismo del Experimento 8 (`xiaomi/mimo-v2.6-pro` vía OpenRouter),
  por comparabilidad. Un resultado con un solo modelo no cierra la pregunta para
  todos, y así se dirá.
- **R10:** solo viajan agregados públicos (medias y distribuciones de la ECP y la
  EPC) y el dossier. **Ningún dato del CNC**, ni agregado.
- **Doce transiciones son pocas.** Las medianas se reportan con su rango y no se
  hace ninguna prueba de significancia que doce puntos no sostengan.
- **Dos constructos distintos** (confianza y gestión, A20). Se reportan juntos y
  por serie.

---

## 7. Qué se construye después de este documento

1. **Enmienda con la fuente del dossier** (§3.3), fechada.
2. **Los doce dossiers**, versionados.
3. `src/experiments/experimento9.py`: arma los mensajes, llama al modelo
   con caché, aplica el ladeo y calcula las métricas. Con pruebas sobre un modelo
   simulado **antes** de gastar una sola llamada real.
4. La sonda de memoria, y después los dos brazos.

Los resultados van a `EXPERIMENT_9_RESULTS.md`, **contra este pre-registro**.
