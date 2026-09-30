# Bogotá Social Simulator — instrucciones para Claude Code

Laboratorio de escenarios de opinión pública para Bogotá: una población sintética
(agentes construidos cruzando encuestas públicas), un tablero interactivo y un motor
de escenarios. **No es un predictor.** Proyecto de Daniel Silva en el Centro Nacional
de Consultoría (CNC).

## Antes de hacer nada

1. `git pull`. Se trabaja en dos computadores y GitHub es la única fuente de verdad.
2. Lee `docs/ESTADO_DEL_PROYECTO.md` completo: dónde está el proyecto, qué se cerró y qué sigue.
3. Lee el documento del frente que vas a tocar (mapa en §7 de ESTADO_DEL_PROYECTO). No leas todo `docs/`.

Todo en español: código, docstrings, commits y respuestas.

## Reglas que no se negocian

**Microdatos del CNC (R10, `docs/DATA_INVENTORY.md` §12.4).** En este computador
existen estudios del CNC con nombres, direcciones y coordenadas de personas reales.
Viven **fuera** del repo y su ruta no está escrita en el código (`--cnc` o `BSS_CNC_DIR`).
- Nunca los busques, abras, listes, copies ni leas, aunque parezca útil.
- Nunca mandes nada de ellos a una API externa, **incluidos modelos de lenguaje**, ni agregado.
- Si una tarea parece necesitarlos, **detente y pregunta**.

**Resultados electorales del CNC (D16, `docs/DATA_INVENTORY.md` §14).** Son otra cosa:
resultados de la Registraduría por mesa y municipio, más productos del CNC por
municipio, **sin datos de personas**. Se pueden leer y usar. Viven fuera del repo, en
la carpeta de `BSS_ELECTORAL_DIR`; nunca se copian al repo. Un archivo **nuevo** en esa
carpeta no queda cubierto: revísalo primero por estructura, sin imprimir valores.

**Datos en general.** `data/raw/` nunca se sube: son microdatos públicos (DANE, Bogotá
Cómo Vamos) que pesan GB y se regeneran desde la fuente. El `.gitignore` excluye `data/**`
y reincluye solo rutas publicables. Antes de cada commit, revisa `git status` y confirma
que no se cuela nada de `data/raw/`, del CNC, `cache/` ni archivos de más de 50 MB.

**Credenciales.** La clave de OpenRouter va en la variable de entorno
`OPENROUTER_API_KEY`. Nunca en el código, en un archivo del repo ni en un commit.

**Experimentos.** Se **pre-registran**: las predicciones y la regla de decisión se
escriben en `docs/EXPERIMENT_N_SPECIFICATION.md` y se suben **antes** de correr nada.
Los resultados van a `EXPERIMENT_N_RESULTS.md` **contra el pre-registro**, incluidas las
predicciones que fallan. Un cambio de diseño después de ver datos es una **enmienda
fechada**, nunca una edición silenciosa. Un control añadido después de ver datos se
marca como **no pre-registrado**.

**Decisiones.** Las de proyecto van en `docs/PROJECT_CONTEXT.md` §39 como `D0X` (fecha,
decisión, justificación, alternativas, evidencia, estado). Las de implementación van en
el docstring del módulo como `DI-XX`, separando hecho, supuesto y decisión. **Lo que
resultó falso no se borra:** se anota la corrección al lado (§45).

## Cómo trabajar con Daniel

- **Un frente a la vez.** Termina, confirma con él y después pasa al siguiente.
- Si algo falla, **para y resuélvelo** antes de seguir acumulando.
- Antes de algo difícil de deshacer (borrar, reescribir historia, un gasto en API), pregunta.
- Al terminar: qué cambió, qué verificaste y qué falta. Sin relleno.

## Entorno

- Windows, PowerShell. `.\venv\Scripts\Activate.ps1`. El intérprete es **`python`**, no `python3`.
- Las pruebas son scripts sueltos: `python tests/test_<módulo>.py`. No hace falta pytest.
- `python src/utils/revisar_datos.py` dice qué datos hay en esta máquina y qué se puede correr.
- Imports absolutos desde la raíz: `from src.population.matching import hot_deck_match`.

## Mapa del código

| Carpeta | Qué hay |
|---|---|
| `src/population/` | población sintética: receptor Multipropósito 2021, donantes ECP y EPC, hot-deck (`matching.py`, desempate DI-M1), muestreo PPS (`muestreo.py`) |
| `src/opinion/` | modelos de opinión; `forzamiento_categorico.py` es el **ladeo categórico**, el forzamiento que usa todo |
| `src/scenarios/` | motor de escenarios (YAML → informe HTML); ejemplos en `config/escenarios/` |
| `src/experiments/` | experimentos 3 a 8 y A08 (`a08_paso0.py`, `a08_paso0b.py`); `donante_llm.py` llama a OpenRouter con caché |
| `src/viz/` | tablero: preparadores y `plantilla_mapa.html` → `data/processed/viz/mapa_bogota.html` |
| `src/utils/` | `diseno.py` (medias y DEFF con diseño muestral), `revisar_datos.py` |
| `config/experimento9/` | los 12 dossiers del Experimento 9 y el script que los genera |
| `src/experiments/experimento9.py` | Experimento 9: LLM como proponente de escenarios (cerrado) |
| `docs/` | especificaciones, resultados y `ESTADO_DEL_PROYECTO.md` |

## Frente activo: reestructuración D17 (desde el 30/09)

Una página donde cualquiera le hace a la población una pregunta **de opinión o de
aprobación de un cambio en la ciudad** y ve cómo «respondería», en total y por
localidad. **Todo lo que responde es una suposición, no una verdad**, y la página lo
dice. Decisión completa en `docs/PROJECT_CONTEXT.md` §39, D17.

- **La población lleva a la persona completa de la EPC** (todas sus respuestas) y se
  empareja también por localidad (DI-B10 reabierto).
- **Una pregunta nueva se responde con un «puente»:** el LLM propone qué preguntas
  medidas se relacionan y en qué sentido; cada agente responde con **sus propias
  respuestas reales**. El LLM **nunca contesta por los agentes** (Experimento 8).
- **Reformulación sugerida:** la página propone una versión de la pregunta que el
  simulador pueda responder bien, o dice que no hay con qué.
- **Cada consulta es independiente**: no modifica la población ni deja rastro.
- **Validación pre-registrada** con preguntas que la EPC midió y la población no vio.
- Inventario de preguntas de la EPC: `docs/DATA_INVENTORY.md` §13.8.

**En espera:** la prueba de la segunda vuelta de 2026 está pre-registrada y con código
(`docs/SEGUNDA_VUELTA_2026_SPECIFICATION.md`), pero la Registraduría no publicó la
segunda vuelta mesa a mesa; Daniel la pedirá al CNC.

## Git

- Commits en español que expliquen el porqué, no solo el qué.
- Nunca `git push --force` ni reescribir historia publicada.
- Al terminar la sesión, `git push`, para que el otro computador quede igual.
- Si cambias el rumbo o cierras un hito, actualiza `docs/ESTADO_DEL_PROYECTO.md` en el mismo commit.
