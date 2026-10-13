# REFORMULACIÓN CON EL CATÁLOGO 2022-2025 — SPECIFICATION

**La reformulación versión 5, sin cambiar una palabra de su instrucción, con el catálogo de la población 2022-2025: ¿lleva
a Galán a sus preguntas nuevas, y deja de mandar a López a algún código?**

Proyecto: Bogotá Social Simulator
Versión: 0.1 — pre-registro, antes de llamar al modelo
Fecha: 13 de octubre de 2026
Origen: `POBLACION_EPC2022_2025_SPECIFICATION.md` §4, §7.4 y su enmienda 1. Lo aprobó Daniel («sí, sigue con el paso 4»).

---

## 1. Qué cambia en lo que ve el modelo

- **La instrucción:** ninguno. Es `SISTEMA_V5` (`REFORMULACION_GOBIERNO_RESULTS.md`).
- **El catálogo:** pasa de las 102 preguntas de la población 2023 a las **84 de la población 2022-2025**. Salen las 23 del
  gobierno de López y entran `GG3_GALAN`, `CC5A_GALAN` y `MICE1_GALAN` a `MICE3_GALAN`.
- **Las notas entre corchetes (DI-CO36):** las de Galán dicen «Se midió en 2024 y 2025, con el alcalde Carlos Fernando
  Galán». La del Concejo dice «Se midió en 2024 y 2025: es el Concejo de 2024-2027, durante la alcaldía de Carlos Fernando
  Galán». Las de López ya no están, porque sus preguntas tampoco.

## 2. Las preguntas (63)

- **Las 54 de la validación de la versión 5:** 40 de voto y 14 de matiz. Lo esperado es lo mismo, salvo una:
  «¿Cómo califica la gente la gestión del alcalde?» iba a `GG3` (López, que ya no existe) y pasa a **`GG3_GALAN`**: el
  alcalde de hoy.
- **9 del gobierno**, que reemplazan a las 8 de la versión 5:

| # | Pregunta | Se espera |
|---|---|---|
| G1 | ¿Cómo califica la gente la gestión del alcalde Galán? | catálogo `GG3_GALAN` |
| G2 | ¿Aprueban los bogotanos la gestión de Carlos Fernando Galán? | catálogo `GG3_GALAN` |
| G3 | ¿Cree la gente que el gobierno de Galán abre espacios de participación ciudadana? | catálogo `MICE3_GALAN` |
| G4 | ¿Qué tan satisfechos están con cómo la alcaldía de Galán invierte la plata de la ciudad? | nueva (la inversión no está) |
| G5 | ¿Cómo evalúan la gestión de Galán en seguridad? | nueva |
| L1 | ¿Cómo calificaba la gente la gestión de la alcaldesa Claudia López? | nueva |
| L2 | ¿Qué tan satisfechos estaban con cómo la alcaldía de Claudia López invertía los recursos? | nueva |
| L3 | ¿Cómo evaluaron la gestión de Claudia López en seguridad en su último año? | nueva |
| C1 | ¿Cómo califican la gestión del Concejo de Bogotá? | catálogo `CC5A_GALAN` |

## 3. Regla de decisión

**Pasa si se cumplen todas:**
- **R1 a R9:** las de la versión 5, con sus mismos umbrales (`reformular.evaluar_voto` y `evaluar_matiz`, y R9).
- **R10, Galán medido:** G1 a G3 con su código en **≥ 2 de 3**; G4 y G5, **ninguna** como catálogo.
- **R11, López:** **ninguna** de L1 a L3 en un código de Galán (`*_GALAN`), y «nueva» en **≥ 2 de 3**.
- **R12, el Concejo:** C1 → `CC5A_GALAN`.

**Si pasa,** la página usa la población 2022-2025 y este catálogo. **Si no pasa,** sigue con la 2022-2024 y lo que falló
se estudia antes de proponer otra cosa.

## 4. Predicciones

- **PR1.** Pasa.
- **PR2.** G1 y G2 van a `GG3_GALAN` (2 de 2).
- **PR3.** Las tres de López son «nueva» (3 de 3).

## 5. PP4 de la población (sin gasto)

Con la página apuntando a la población 2022-2025, las cinco preguntas de la prueba de residentes se responden con el dato
medido del catálogo, igual que en `MIROFISH_RESIDENTES_SPECIFICATION.md` §4: `CV1`, `AG2`, `AG1` y `VS15`, y ahora
`GG3_GALAN` para la aprobación (antes era una estimación, 47,3 %). Se toma el lado favorable de DI-CO18, sin «no sabe».
Se compara con los microdatos de 2025 (61,4; 56,6; 48,2; 26,4; 14,6). **PP4 se cumple si el error medio baja de 12,9.**
**No es una prueba a ciegas:** 2025 está en los datos.

## 6. Gasto y datos

- **63 llamadas a `openai/gpt-6-luna`**, temperatura 0. La versión 5 costó USD 0,064 por 62 llamadas: se esperan **unos
  USD 0,07**. Daniel ya aprobó el gasto.
- Al modelo van solo las preguntas de prueba y el catálogo (textos y escalas de la EPC, públicos). Ningún microdato.
- Respuestas y caché en `data/processed/reformulacion/catalogo_2025/`, sin subir.
