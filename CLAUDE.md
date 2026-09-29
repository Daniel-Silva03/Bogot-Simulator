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
| `docs/` | especificaciones, resultados y `ESTADO_DEL_PROYECTO.md` |

## Frente activo: Experimento 9

`docs/EXPERIMENT_9_SPECIFICATION.md` (pre-registro y enmiendas 1 a 3). ¿Puede un LLM
proponer el cambio de **nivel** y **dispersión** de un periodo mejor que suponer que nada
cambia? 12 transiciones reales, dos brazos, sonda de memoria, baselines «sin cambio»,
«tendencia» y oráculo.

- **Hecho:** los 12 dossiers en `config/experimento9/dossiers/`, congelados, con huellas
  en `HUELLAS.txt`. **No se editan**: cualquier cambio a un dossier invalida el pre-registro.
- **Siguiente:** `src/experiments/experimento9.py` + `tests/test_experimento9.py`. Las
  pruebas corren con un **modelo simulado**, sin red, **antes de la primera llamada
  real**. Reutiliza el cliente con caché de `donante_llm.py` y el ladeo de
  `forzamiento_categorico.py`. La métrica principal es W1 sobre el piso de ruido.
- **Antes de gastar llamadas reales**, confirma con Daniel el costo estimado.

## Git

- Commits en español que expliquen el porqué, no solo el qué.
- Nunca `git push --force` ni reescribir historia publicada.
- Al terminar la sesión, `git push`, para que el otro computador quede igual.
- Si cambias el rumbo o cierras un hito, actualiza `docs/ESTADO_DEL_PROYECTO.md` en el mismo commit.
