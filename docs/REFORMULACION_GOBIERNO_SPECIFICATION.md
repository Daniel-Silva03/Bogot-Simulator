# LA REFORMULACIÓN NO CONFUNDE A GALÁN CON CLAUDIA LÓPEZ

Pre-registro escrito el **8 de octubre de 2026**, antes de hacer ninguna llamada. Lo pidió Daniel, tras una sugerencia de su
jefe. **Gasto: ~USD 0,06, con tope de USD 0,15.**

## 1. Qué cambia

**El problema.** La EPC no mide al alcalde Carlos Fernando Galán (DI-CO36):
- `GG3` («¿Usted cómo califica la gestión del alcalde/sa?») y `CV5` se midieron en 2022-2023, con la alcaldesa Claudia
  López;
- `GP1N_*`, en 2023, el último año de su gobierno;
- `MICE*` (2023-2024) mezcla los dos gobiernos.

Con la versión 4 (`SISTEMA_V4`), «¿Cómo califica la gente la gestión del alcalde Galán?» probablemente iría a `GG3`, y la
página mostraría como medida la calificación de Claudia López. No se ha probado; es la predicción PRG1.

**La versión 5 (`SISTEMA_V5`)** cambia dos cosas:
1. **En el catálogo que ve el modelo,** las 22 preguntas del gobierno llevan entre corchetes la nota que ya muestra la
   página (`nota_gobierno`). Por ejemplo: «[Se midió en 2022 y 2023, cuando la alcaldesa era Claudia López: no es sobre
   el gobierno de Galán.]». Las demás quedan iguales.
2. **Se agrega una frase al alcance «catalogo»:**

> Algunas preguntas del catálogo dicen entre corchetes qué gobierno midieron: si la persona nombra a otro gobernante, no
> es esa pregunta, es "nueva".

**Una pregunta sobre «el alcalde», sin nombre,** puede seguir yendo a `GG3`. La página la muestra con su «Ojo».

**El modelo** es `openai/gpt-6-luna`, a temperatura 0.

## 2. La prueba

**62 preguntas,** escritas antes de llamar:
- **las 54 de la validación de la versión 4,** para ver que nada se rompa;
- **8 nuevas** (`PRUEBA_GOBIERNO`).

**Cuatro sobre Galán.** Deben ser «nuevas»:
- ¿Cómo califica la gente la gestión del alcalde Galán?
- ¿Aprueban los bogotanos la gestión de Carlos Fernando Galán?
- ¿Qué tan satisfechos están con cómo la alcaldía de Galán invierte la plata de la ciudad?
- ¿Cómo evalúan la gestión de Galán en seguridad?

**Tres sobre Claudia López.** Deben ir a su código:

| Pregunta | Código |
|---|---|
| ¿Cómo calificaba la gente la gestión de la alcaldesa Claudia López? | `GG3` |
| ¿Qué tan satisfechos estaban con cómo la alcaldía de Claudia López invertía los recursos? | `CV5` |
| ¿Cómo evaluaron la gestión de Claudia López en seguridad en su último año? | `GP1N_8` |

**Una de control,** sin gobernante: ¿Cómo califican la gestión del Concejo de Bogotá? → `CC5A`.

## 3. Regla

**La versión 5 entra a la página si se cumplen las doce condiciones:**
- **R1 a R9,** iguales a las de `REFORMULACION_MATIZ_SPECIFICATION.md` §3, sobre las 54;
- **R10:** ninguna de las 4 de Galán como catálogo, y «nueva» en ≥ 3. Que una de Galán vaya al catálogo es el error que
  más engaña;
- **R11:** las de Claudia López con su código en ≥ 2 de 3;
- **R12:** la del Concejo va a `CC5A`.

**Si no se cumplen,** la página sigue con la versión 4 y el «Ojo» como única defensa.

## 4. Predicciones

- **PRG1.** La versión 5 cumple la regla.
- **PRG2.** Ninguna de las 4 de Galán va al catálogo.
- **PRG3.** Las 3 de Claudia López van a su código.

## 5. Lo que ya se vio, y se declara

- **Los resultados de la versión 4** en las 54.
- **Las notas del gobierno y los años de cada pregunta** (DI-CO36).
- **No se ha probado ninguna pregunta sobre Galán** con ninguna versión.

## 6. Gasto y código

- **Gasto:** 62 llamadas a ~USD 0,001, unos USD 0,06, con tope de USD 0,15.
- **Código:** `src/consulta/reformular.py` (`SISTEMA_V5`, `prompt(..., notas)`, `PRUEBA_GOBIERNO`, `evaluar_gobierno`,
  `notas_gobierno`, `validar_voto(5)`).
- **Pruebas:** `tests/test_reformular.py`.
- **Resultados:** `REFORMULACION_GOBIERNO_RESULTS.md`.
