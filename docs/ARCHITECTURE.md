# ARCHITECTURE — Prototipo de 1.000 agentes (Bogotá Social Simulator)

Proyecto: Bogotá Social Simulator
Documento: Fase 5 del roadmap (numeración D13) — traduce D12 + NETWORK_SPECIFICATION.md + MODEL_SPECIFICATION.md + POPULATION_SPECIFICATION.md en una arquitectura de software concreta
Versión: 0.2 — actualizado con lo efectivamente implementado en `src/population/`, `src/network/` y `src/opinion/`
Fecha: Septiembre de 2026

---

## 1. Alcance deliberado

Solo lo necesario para correr el Experimento 1 y el Experimento 2 de RESEARCH.md con 1.000 agentes, en local. **Explícitamente fuera de esta fase** (Principio 5 — evitar complejidad prematura; sección 26 de PROJECT_CONTEXT.md): PostgreSQL/PostGIS, FastAPI, React, cualquier interfaz web. Esas piezas pertenecen a la Fase 10 (Dashboard), no a la Fase 5. El prototipo corre como scripts/notebooks Python configurables, con salidas a disco versionadas.

## 2. Decisión técnica importante que no estaba explícita en los documentos anteriores

DeGroot y Friedkin-Johnsen están definidos matemáticamente como **actualización síncrona**: \(a_i(t+1)\) depende de \(a_j(t)\) para *todos* los \(j\), no de valores ya actualizados en la misma ronda. Si se implementa con el scheduler por defecto de Mesa (`RandomActivation`, que actualiza agente por agente y muta el estado en el momento), el orden de actualización introduce un sesgo que no está en la ecuación original — un error de implementación silencioso y fácil de cometer.

**Decisión:** usar `mesa.time.SimultaneousActivation`, que separa `step()` (calcula el valor nuevo sin mutar todavía) de `advance()` (aplica el cambio a todos a la vez). Esto no es una preferencia estética — es lo que exige la fidelidad a las fórmulas ya aprobadas en MODEL_SPECIFICATION.md.

**Actualización (Septiembre 2026):** con `src/opinion/` implementado en forma matricial (ver sección 5.3), la actualización síncrona quedó garantizada *por construcción*: `paso(a) -> a'` calcula el vector nuevo entero a partir del viejo, sin mutar nada en el camino, así que el sesgo de orden es imposible de introducir. `SimultaneousActivation` sigue siendo la decisión correcta para cuando `src/model/` envuelva esto en Mesa, pero la fidelidad a la fórmula ya no depende de que nadie se equivoque de scheduler.

## 3. Estructura de carpetas

Estado real al 15 de septiembre de 2026. ✅ = implementado y probado.

```text
bogota_social_simulator/
├── config/
│   ├── experiment_1.yaml
│   └── experiment_2.yaml
├── data/
│   ├── raw/                       # descargas originales — sin versionar (gitignore)   ✅
│   ├── external/                  # marginales y tablas de referencia — SÍ versionadas ✅
│   │   └── marginal_localidad_18mas.csv
│   └── processed/
│       ├── poblacion_sintetica_v2.csv        ✅ (parquet cuando haya pyarrow)
│       └── poblacion_sintetica_v2_metadata.json  ✅
├── src/
│   ├── population/                                          ✅
│   │   ├── extraer_columnas_em2021.py  # prepara y verifica data/raw/
│   │   ├── loader.py                   # carga receptor + donante
│   │   ├── matching.py                 # hot-deck nearest-neighbour
│   │   ├── muestreo.py                 # selección de los N agentes (D14)
│   │   ├── build_agents.py             # construye los 7 campos de D12
│   │   └── construir_poblacion.py      # pipeline de punta a punta
│   ├── network/                                             ✅
│   │   ├── base.py                     # NetworkGenerator, NetworkResult, diagnósticos
│   │   ├── random_network.py           # Erdős–Rényi
│   │   ├── homophilic_network.py
│   │   └── territorial_network.py
│   ├── opinion/                                             ✅
│   │   ├── base.py                     # OpinionModel, Trayectoria
│   │   ├── degroot.py
│   │   └── friedkin_johnsen.py
│   ├── model/                                               ← pendiente
│   │   ├── agent.py                    # BogotaAgent(mesa.Agent)
│   │   └── model.py                    # BogotaSocialModel(mesa.Model)
│   ├── experiments/                                         ← pendiente
│   │   ├── runner.py                   # ejecuta N runs, barre parámetros, registra reproducibilidad
│   │   └── metrics.py                  # media, mediana, polarización, distribución
│   └── utils/
│       ├── seeds.py
│       └── config.py                   # carga y valida YAML
├── experiments_output/
│   └── {experiment_id}/
│       ├── run_metadata.json
│       └── run_{i}.parquet
├── tests/                                                   ✅
│   ├── test_population_matching.py
│   ├── test_muestreo.py
│   ├── test_network_generators.py
│   └── test_opinion_models.py
├── notebooks/
│   ├── 01_explorar_poblacion.ipynb
│   ├── 02_experimento_1.ipynb
│   └── 03_experimento_2_comparar_redes.ipynb
├── ARCHITECTURE.md
└── requirements.txt
```

Dos carpetas nuevas respecto a la versión 0.1: `data/external/` (tablas de referencia derivadas, chicas y versionadas — a diferencia de `data/raw/`, que va en gitignore y por eso obliga a versionar los scripts que la reconstruyen), y los módulos `muestreo.py` y `construir_poblacion.py` en `src/population/`, que no existían cuando se escribió este documento.

## 4. Mapeo documento → módulo (trazabilidad explícita)

| Documento | Módulo | Qué implementa |
|---|---|---|
| POPULATION_SPECIFICATION.md | `src/population/matching.py` | hot-deck (Multipropósito receptor + Confianza Institucional donante) |
| D14 (PROJECT_CONTEXT.md) | `src/population/muestreo.py` | muestreo proporcional al factor de expansión |
| NETWORK_SPECIFICATION.md | `src/network/` | los tres generadores, interfaz común |
| MODEL_SPECIFICATION.md | `src/opinion/` | DeGroot (baseline) y Friedkin-Johnsen |
| D12 (PROJECT_CONTEXT.md) | `src/model/agent.py` | los 7 campos del agente |
| RESEARCH.md §49-50 | `src/experiments/` | Experimento 1 y 2 |
| Sección 35 PROJECT_CONTEXT.md | `experiments_output/*/run_metadata.json` | reproducibilidad obligatoria |

## 5. Componentes principales

### 5.1 `BogotaAgent(mesa.Agent)`

```text
atributos fijos (D12):
    agent_id, edad, sexo, localidad, estrato, nivel_educativo
atributos dinámicos:
    opinion_actual       # a_i(t)
    opinion_inicial       # a_i(0), necesaria para el término de persistencia de Friedkin-Johnsen
    opinion_siguiente     # buffer para actualización síncrona (ver sección 2)

step():
    calcula opinion_siguiente
    # NO muta opinion_actual todavía

advance():
    opinion_actual = opinion_siguiente
```

**Nota de implementación:** con `src/opinion/` trabajando sobre vectores, `BogotaSocialModel` puede avanzar a todos los agentes con una sola llamada a `paso()` y luego repartir el resultado a los objetos `BogotaAgent`, en vez de que cada agente calcule lo suyo. Los agentes siguen existiendo (para el `DataCollector`, la segmentación territorial y la futura heterogeneidad individual), pero no son el lugar donde ocurre la aritmética.

### 5.2 `NetworkGenerator` (interfaz común, `src/network/base.py`)

```text
clase abstracta NetworkGenerator:
    generar(agentes, k_promedio, seed, **params) -> NetworkResult
```

`NetworkResult` trae `adjacency` (la red realizada) y `W` (la matriz de pesos de influencia, normalizada por filas) — ver DI-N1 en NETWORK_SPECIFICATION.md sección 9. Cada uno de los tres generadores implementa esta interfaz, y eso es lo que permite que sean "variantes intercambiables" tal como se definió en A07: el modelo no necesita saber cuál generador se usó, solo recibe \(W\).

### 5.3 `OpinionModel` (interfaz común, `src/opinion/base.py`)

```text
clase abstracta OpinionModel:
    __init__(W)
    paso(a) -> a'                    # un paso, sobre todos los agentes a la vez
    calcular_agente(i, a) -> float   # la misma ecuación para un solo agente
    simular(a0, n_pasos) -> Trayectoria
```

**Cambio respecto a la versión 0.1 de este documento.** La interfaz era `calcular(agente, vecinos, pesos) -> nueva_opinion`, es decir agente por agente. El Experimento 2 son ~4.800 corridas × 100 pasos × 1.000 agentes: 480 millones de llamadas en Python puro, inviable. Las dos ecuaciones de MODEL_SPECIFICATION.md son productos matriz-vector, y la forma vectorizada las expresa con una sola operación de numpy por paso — medido, 6,8 ms por corrida de 100 pasos, o medio minuto para el barrido completo.

`calcular_agente(i, a)` se conserva escribiendo la ecuación literalmente como aparece en el documento. **No se usa en producción:** existe para que los tests verifiquen, agente por agente, que la versión matricial computa exactamente lo mismo (coinciden con error de 9e-16). Así la optimización queda auditada en vez de asumida.

`DeGrootModel` y `FriedkinJohnsenModel` implementan la interfaz. Igual que con la red, `BogotaSocialModel` no necesita saber cuál está corriendo — que es exactamente lo que pide el Experimento 4 de RESEARCH.md (comparar el ABM contra baselines).

**Propiedades que vale la pena conocer antes de leer resultados**, verificadas en `tests/test_opinion_models.py`:

- Friedkin-Johnsen tiene punto fijo analítico \(a^* = (I - \Phi W)^{-1}(I - \Phi)\,a(0)\), y la simulación converge a él con error < 1e-7. Haber elegido un modelo lineal sirve para esto: los resultados se pueden comprobar contra la solución exacta en vez de creerle al bucle.
- Ambos modelos son **deterministas**. Dada la red y \(a(0)\), la trayectoria es única. La variabilidad entre corridas del Experimento 2 viene enteramente de la realización de la RED, no de la dinámica — es un punto a tener presente al diseñar el runner y al interpretar las distribuciones de resultados que pide RESEARCH.md sección 32.
- DeGroot **no converge en redes bipartitas** (con diagonal cero, alterna entre dos estados). No afecta a las tres redes del proyecto, que son aleatorias y tienen ciclos impares con probabilidad prácticamente 1, pero si alguna corrida de DeGroot no converge, esa es la primera hipótesis a revisar antes de buscar un bug.
- Los agentes aislados conservan exactamente su opinión inicial en ambos modelos, como consecuencia de \(w_{ii}=1\) (DI-N3).

### 5.4 `BogotaSocialModel(mesa.Model)`

```text
__init__(agentes_df, network_generator, opinion_model, params, seed):
    fijar semillas  # reproducibilidad obligatoria
    construir agentes (BogotaAgent) desde agentes_df
    red = network_generator.generar(agentes_df, **params)
    self.opinion_model = opinion_model(red.W, **params_opinion)
    self.schedule = mesa.time.SimultaneousActivation(self)
    self.datacollector = mesa.DataCollector(
        model_reporters={"media_opinion": ..., "std_opinion": ..., "indice_polarizacion": ...},
        agent_reporters={"opinion": "opinion_actual", "localidad": "localidad"}
    )

step():
    self.schedule.step()   # step() + advance() de todos los agentes, síncrono
    self.datacollector.collect(self)
```

### 5.5 `experiments/runner.py` — reproducibilidad no negociable

Cada corrida registra exactamente los campos que pide la sección 35 de PROJECT_CONTEXT.md y la sección 26 del prompt maestro:

```text
experiment_id
timestamp
dataset_version        # versión de poblacion_sintetica_v2
model_version           # ej. "friedkin_johnsen_v0.1"
network_generator       # ej. "territorial"
parametros              # k_promedio, h o beta, phi, etc.
random_seed
numero_agentes
numero_runs
numero_pasos
resultados              # serie de media_opinion, std_opinion por paso, por run
```

Esto no es opcional — sin esto, RESEARCH.md sección 32 ("incertidumbre") no se puede cumplir: un escenario tiene que devolver una *distribución* de resultados across runs, no un solo número, y eso solo es interpretable si cada run quedó trazado.

`NetworkResult.metadata()` y `Trayectoria.metadata()` ya devuelven sus bloques listos para volcar ahí, y `muestreo` y `diagnostico_territorial` hacen lo propio en el metadata de la población. El runner los compone; no tiene que reconstruir nada.

**Cuánta memoria guardar.** La trayectoria completa de una corrida son 800 KB (100 pasos × 1.000 agentes × 8 bytes); a 4.800 corridas, casi 4 GB. Por eso `simular()` registra por defecto solo un resumen por paso (media, desviación, mínimo, máximo) más el vector final, y guarda la trayectoria entera solo cuando se le pide explícitamente, para analizar una corrida concreta.

### 5.6 Config-driven, no hardcoded (Regla de PROMPT MAESTRO sección 25)

```yaml
# config/experiment_2.yaml — comparación de generadores de red
experiment_id: "exp2_comparacion_redes_v1"
poblacion: "data/processed/poblacion_sintetica_v2.csv"
n_agentes: 1000
opinion_model: "friedkin_johnsen"
opinion_model_params:
  phi: 0.7   # persistencia — placeholder, NO estimado con datos (ver pendientes)
n_pasos: 100
n_runs: 200
seed_base: 42
network_sweep:
  - {tipo: "aleatoria", k_promedio: [5, 10, 15, 20]}
  - {tipo: "homofilica", k_promedio: [5, 10, 15, 20]}
  - {tipo: "territorial", k_promedio: [5, 10, 15, 20], h: [5, 10, 20, 50]}
```

Los strings `tipo` y `opinion_model` se resuelven con `src.network.crear_generador()` y `src.opinion.crear_modelo()`, que fallan con la lista de opciones válidas si el YAML trae un nombre desconocido.

## 6. Flujo de datos de punta a punta

```text
data/raw/ (Multipropósito, Confianza Institucional, proyecciones DANE-SDP)
        ↓
src/population/extraer_columnas_em2021.py   [extrae, verifica, arma el marginal]
        ↓
src/population/construir_poblacion.py       [loader → muestreo → hot-deck → build_agents]
        ↓
data/processed/poblacion_sintetica_v2.csv   [1.000 agentes, 7 campos D12]
        ↓
src/network/{generador}.py  →  NetworkResult (adjacency + W)
        ↓
src/opinion/{modelo}.py     →  Trayectoria
        ↓
src/model/model.py  (BogotaSocialModel, SimultaneousActivation)
        ↓
src/experiments/runner.py  (barre parámetros × N runs, fija seeds)
        ↓
experiments_output/{experiment_id}/  (resultados + metadata de reproducibilidad)
        ↓
notebooks/  (análisis, gráficos, comparación contra distribución observada)
```

## 7. Cómo corren los Experimentos 1 y 2 con esta arquitectura

- **Experimento 1** (¿puede el modelo reproducir una distribución objetivo?): correr `runner.py` con un solo generador de red y Friedkin-Johnsen, comparar la distribución de opinión simulada en t=100 contra la distribución observada en el donante.
- **Experimento 2** (¿cuánto importa la estructura de red?): correr `runner.py` con el `network_sweep` de la config de arriba — misma población, mismo modelo de opinión, solo cambia el generador — y comparar las distribuciones resultantes entre sí. El resultado de esto es lo que finalmente cierra A07.

**Primer indicio, con la población v2 real** (una corrida por combinación, k̄=10, φ=0,7 — no es el experimento, es una verificación de que el sistema corre de punta a punta):

| Red | DeGroot (sd final) | Friedkin-Johnsen (sd final) |
|---|---|---|
| aleatoria | 0,000 | 0,198 |
| homofílica | 0,193 | 0,284 |
| territorial | 0,006 | 0,204 |

Las dos cosas que sugiere: Friedkin-Johnsen conserva desacuerdo donde DeGroot lo borra (lo esperado, y la razón de la recomendación de MODEL_SPECIFICATION.md), y la red homofílica sostiene dispersión incluso bajo DeGroot, mientras la aleatoria y la territorial colapsan a consenso. Si eso se sostiene con 200 runs por configuración, sería un resultado del Experimento 2 — con una corrida no es evidencia de nada.

## 8. Qué queda pendiente antes de poder ejecutar esto

- `src/model/` y `src/experiments/`, más `config/`, que sigue vacío.
- `phi` (persistencia de Friedkin-Johnsen) **no está estimado**. Para el prototipo se trata como parámetro a explorar, no como valor conocido; el módulo lo registra explícitamente como `phi_estimado_con_datos: false` en la metadata de cada corrida, para que ningún resultado se lea como si 0,7 fuera un dato.
- Falta decidir el **índice de polarización** concreto del `DataCollector` (varianza, bimodalidad, número de clusters). `src/opinion/` deliberadamente no lo calcula: pertenece a `src/experiments/metrics.py`, y elegirlo en silencio cerraría por la puerta de atrás una decisión que afecta directamente cómo se lee el Experimento 2.
- Como ambos modelos son deterministas, "200 runs por configuración" significa **200 realizaciones de la red**, no 200 trayectorias de la dinámica. El runner tiene que variar la semilla de la red entre runs; si la fija, las 200 corridas serán idénticas.
- `pyarrow` no está instalado en el entorno, así que las salidas se escriben como `.csv` aunque este documento especifique `.parquet`.

---

*Documento vivo — actualizar con cada decisión de implementación siguiendo la convención establecida en PROJECT_CONTEXT.md.*
