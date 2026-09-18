# Bogotá Social Simulator

Laboratorio computacional para representar una **población sintética de Bogotá** y
explorar cómo podría moverse la opinión pública bajo distintos supuestos.
Modelado basado en agentes (ABM) sobre microdatos reales.

Proyecto de investigación aplicada del **Centro Nacional de Consultoría (CNC)**.

> **No es un predictor.** El objetivo no es acertar el futuro ni representar
> personas reales. Siete experimentos pre-registrados dicen, con sus umbrales
> escritos de antemano, que este sistema no reproduce la trayectoria observada
> mejor que dos números exógenos por periodo. Eso es un resultado del proyecto,
> no una falla que esté pendiente de arreglar. Ver `docs/PROJECT_CONTEXT.md` §43.

---

## Qué hay acá

| Módulo | Qué hace |
|---|---|
| `src/population/` | Construye la población sintética por *hot-deck nearest-neighbour* a partir de la Encuesta Multipropósito 2021 y donantes de opinión (ECP del DANE, EPC de Bogotá Cómo Vamos) |
| `src/network/` | Generadores de red: aleatoria, territorial, homofílica |
| `src/opinion/` | Modelos de dinámica: DeGroot, Friedkin-Johnsen, cognición motivada, y el forzamiento exógeno (ladeo categórico) |
| `src/experiments/` | Los siete experimentos pre-registrados, con su *runner* y sus métricas |
| `src/scenarios/` | Motor de escenarios declarativos en YAML, con incertidumbre descompuesta e informe HTML |
| `src/viz/` | Capa visual: geometría de Bogotá y el mapa interactivo |
| `src/utils/` | Semillas, configuración y estimación con diseño muestral complejo |

## Método

Todo experimento se **pre-registra**: hipótesis, umbrales numéricos y criterio de
falla se escriben y se fechan *antes* de correr nada; después se reporta contra
eso, incluidas las predicciones que fallan. La vara es el **piso de ruido**: la
distancia de Wasserstein-1 entre dos muestras de la *misma* población observada.
Un modelo que queda por debajo de ese piso es indistinguible de una muestra real;
uno que queda por encima, no.

Ese diseño es lo que ha producido los hallazgos del proyecto — incluidos tres
errores de forma que ninguna revisión de código encontró y que aparecieron al
contrastar contra una referencia externa.

## Arrancar

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

Las pruebas corren solas, sin pytest:

```bash
python tests/test_population_matching.py
python tests/test_viz_mapa.py
```

### El mapa interactivo

```bash
python src/viz/preparar_mapa.py      # geometría + población -> paquete de datos
python src/viz/construir_pagina.py   # plantilla + datos -> página autocontenida
```

Produce `data/processed/viz/mapa_bogota.html`: un solo archivo, sin servidor ni
base de datos, que se abre con doble clic.

### Un escenario

```bash
python -m src.scenarios.motor config/escenarios/ejemplo_polarizacion.yaml
```

## Los datos no están en el repositorio

Y es a propósito. Ver `.gitignore`, que explica por qué, y
`docs/DATA_SPECIFICATION.md` y `docs/DATA_INVENTORY.md`, que dicen qué se usa,
de dónde sale y cómo se reconstruye. Resumen:

- **DANE** — Encuesta Multipropósito 2021, Encuesta de Cultura Política
  2013-2023. Públicas en el portal de microdatos del DANE.
- **Bogotá Cómo Vamos** — Encuesta de Percepción Ciudadana 2014-2025.
- **Catastro Distrital** — geometría de localidades. *Esta sí está* en
  `data/external/geo/`: son 27 KB y es la única que el código necesita para dibujar.
- **CNC** — dos estudios agregados. **No salen del equipo.** R10 y
  `docs/PROJECT_CONTEXT.md` §32.

## Documentación

`docs/` tiene la especificación completa. Los tres de entrada:

- `docs/PROJECT_CONTEXT.md` — el documento vivo: estado, decisiones tomadas (D01…),
  decisiones abiertas (A01…), riesgos y roadmap. Si vas a leer uno solo, es este.
- `docs/POPULATION_SPECIFICATION.md` — cómo se construye la población sintética.
- `docs/VISUALIZATION_SPECIFICATION.md` — la capa visual y la regla que la gobierna.

## Convenciones

- Código, nombres y *docstrings* en **español**.
- Importaciones absolutas desde la raíz: `from src.population.matching import ...`
- Cada decisión de implementación que no sea obvia se anota como **DI-xx** en el
  *docstring* del módulo, con su razón. No se corrigen cosas en silencio: si algo
  estuvo mal, queda anotado que estuvo mal.
