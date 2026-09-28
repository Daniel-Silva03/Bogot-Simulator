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
