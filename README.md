# Bogotá Social Simulator

**Una población sintética de Bogotá a la que se le pueden hacer preguntas de opinión, con la respuesta en total, por
grupos y por localidad.**

Proyecto de investigación aplicada del **Centro Nacional de Consultoría (CNC)**.

> **Todo lo que responde es una suposición, no una medición, y la página lo dice.** No reemplaza una encuesta. Cada
> método se pre-registró y se validó contra datos reales antes de entrar a la página. Ver los resultados en `docs/`.

---

## Qué hace

Uno escribe una pregunta en la página, por ejemplo «¿aprueban los bogotanos la gestión de Galán?», y ve cómo
«respondería» la ciudad.

- **La población:** 19.000 personas sintéticas, con las proporciones de la Encuesta Multipropósito 2021 del DANE. Cada una
  hereda a un bogotano real de la **Encuesta de Percepción Ciudadana 2022-2025** (Bogotá Cómo Vamos), de su misma
  localidad y parecido en sexo, edad y estrato: 6.042 encuestados en total.
- **Quién responde:** la gente real. Cada persona sintética responde con las respuestas de su encuestado. El modelo de
  lenguaje solo entiende la pregunta y elige qué preguntas medidas se relacionan; **nunca contesta por nadie**.

| Tipo de pregunta | Cómo se responde | Mapa por localidad |
|---|---|---|
| **Ya medida** (84 en el catálogo) | Las respuestas reales, reponderadas por la población | Sí, con su margen de error |
| **Nueva** | Una estimación a partir de preguntas reales parecidas, con un rango de unos ±22 puntos | No: no hay dato por localidad |
| **Intención de voto** | Estimación a partir de las encuestas del CNC | No |
| **Fuera de alcance** (un dato, lo que piensa una persona…) | La página lo dice y, si puede, propone una pregunta cercana | — |

## Qué tan bien funciona

| Prueba | Resultado |
|---|---|
| Cinco preguntas de la EPC 2025, adivinadas sin 2025 | Error medio de 12,9 puntos; decir «50 %» para todo da 15,8 |
| Las mismas cinco, con la población 2022-2025 | Error de 8,3, en el mismo orden que la realidad (no es a ciegas) |
| Preguntas nuevas, en 129 preguntas reales escondidas | Dice de qué lado está la mayoría en 11, y acierta 10 |
| Intención de voto, contra la Registraduría | Unos 4 puntos de error |

**Comparado con otras herramientas** de personas sintéticas, en las mismas cinco preguntas:

| | Error medio |
|---|---|
| MiroFish (red social simulada) | 28,7 |
| TinyTroupe de Microsoft (personas inventadas) | 25 a 27 |
| **Este simulador** | **12,9** |

Cuando el modelo de lenguaje opina por la gente, la cifra sale peor que decir 50 % para todo. Detalle en
`docs/COMPARACION_HERRAMIENTAS.md`.

**Lo que no hace:** no anticipa un cambio brusco de opinión. Junta los años de cada pregunta, así que describe la Bogotá de
2022-2025; un cambio se ve cuando entra la encuesta nueva (`docs/PESO_ANIO_RECIENTE_RESULTS.md`).

## Arrancar

Requiere Python 3.11 y git, en Windows con PowerShell.

```powershell
git clone <url del repositorio>
cd <carpeta del repositorio>
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**La página necesita además el paquete del traslado** (poblaciones y resultados guardados, unos 5 MB), que no está en
GitHub. Se pide al equipo y se extrae desde la raíz del repositorio:

```powershell
python src/utils/empacar_traslado.py --extraer <ruta>\bss_traslado_<fecha>.zip
python src/utils/revisar_datos.py      # la sección «LA PÁGINA ACTUAL» debe estar en [OK ]
```

**Abrir la página:**

```powershell
python src/consulta/servidor.py --simulado     # sin clave ni gasto: respuestas de prueba
$env:OPENROUTER_API_KEY = "..."                # una clave propia de OpenRouter, solo en esa terminal
python src/consulta/servidor.py                # con el modelo real
```

y abrir `http://127.0.0.1:8765`. Una pregunta medida cuesta unos USD 0,003, y una nueva desde unos USD 0,006. La clave
nunca va al navegador, a un archivo ni a un commit.

Más detalle, y cómo pasar el proyecto completo a otro computador: `docs/TRASLADO.md`.

**Pruebas** (scripts sueltos, sin pytest):

```powershell
python tests/test_consulta.py
python tests/test_reformular.py
```

## Qué hay acá

| Carpeta | Qué hay |
|---|---|
| `src/consulta/` | **La página:** `servidor.py` (local), `motor.py` (une reformulación, catálogo y estimación), `pagina.html`, `reformular.py` |
| `src/population/` | La población sintética: receptor Multipropósito 2021, donantes EPC, emparejamiento; la de la página es `poblacion_epc_olas.py --con-2025` |
| `src/experiments/` | Los experimentos y validaciones, incluidas las pruebas de MiroFish y TinyTroupe |
| `src/opinion/`, `src/network/`, `src/scenarios/` | El laboratorio anterior: modelos de dinámica de opinión, redes y escenarios en YAML |
| `src/viz/` | El tablero anterior (mapa 2013-2023), que se conserva |
| `src/utils/` | Estimación con diseño muestral, revisión de datos y traslado |
| `docs/` | Pre-registros (`*_SPECIFICATION.md`), resultados (`*_RESULTS.md`) y el estado del proyecto |

## Método

Todo se **pre-registra**: las predicciones y la regla de decisión se escriben y se suben **antes** de correr nada.
Después se reporta contra eso, incluidas las predicciones que fallan. Un cambio después de ver datos es una enmienda
fechada, y lo que resultó falso no se borra: se anota la corrección al lado.

**La historia:** el proyecto empezó como un modelo de agentes que simulaba cómo se mueve la opinión. Siete experimentos
pre-registrados mostraron que no reproducía la trayectoria observada mejor que dos números exógenos por periodo
(`docs/PROJECT_CONTEXT.md` §43). De ahí salió el diseño actual (D17): no simular la opinión, sino dejar que responda
la gente real.

## Los datos

**Los microdatos no están en el repositorio**, a propósito (`.gitignore`, `docs/DATA_INVENTORY.md`):

- **DANE:** Encuesta Multipropósito 2021 y Encuesta de Cultura Política. Públicas.
- **Bogotá Cómo Vamos:** Encuesta de Percepción Ciudadana 2014-2025. Pública.
- **Catastro Distrital:** geometría de las localidades. Esta sí está, en `data/external/geo/`.
- **CNC:**
  - los estudios con datos de personas **nunca salen del equipo** ni van a ninguna API;
  - los resultados de las encuestas políticas y electorales se usan agregados, viajan solo por canales internos del CNC y
    nunca van a GitHub.

## Documentación

- `docs/ESTADO_DEL_PROYECTO.md`: dónde va el proyecto, qué se cerró y qué sigue. Si se lee uno solo, es este.
- `docs/PAGINA_CONSULTA.md`: la página, qué muestra cada respuesta y sus límites.
- `docs/COMPARACION_HERRAMIENTAS.md`: MiroFish, TinyTroupe y este simulador.
- `docs/PROJECT_CONTEXT.md` §39: las decisiones del proyecto (D01…).

## Convenciones

- Código, nombres, *docstrings* y commits en **español**.
- Importaciones absolutas desde la raíz: `from src.population.matching import hot_deck_match`.
- Cada decisión de implementación que no sea obvia va como **DI-xx** en el *docstring* del módulo, con su razón.
