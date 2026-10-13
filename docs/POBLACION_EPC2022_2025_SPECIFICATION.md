# POBLACIÓN EPC 2022-2025 — SPECIFICATION

**La población 2022-2024 (`POBLACION_EPC2022_2024_SPECIFICATION.md`) más la ola de 2025: unas 330 personas por localidad en
vez de 250, y la gestión de Galán como dato medido.**

Proyecto: Bogotá Social Simulator
Versión: 0.1 — pre-registro, antes de construirla
Fecha: 13 de octubre de 2026
Origen: la verificación de la EPC 2025 contra su formulario (`DATA_INVENTORY.md` §13.10). Lo pidió Daniel.
Lo que no cambia: todo lo que no se diga aquí es igual a la población 2022-2024.

---

## 1. Qué cambia

| | Población 2022-2024 (la de la página) | Población 2022-2025 |
|---|---|---|
| Donantes | 4.522 | **~6.040**: más los 1.520 de 2025 |
| Personas por localidad | mediana 251 | **~330**. La Candelaria no gana: 2025 no la encuestó |
| Qué describe | Bogotá 2022-2024 | **Bogotá 2022-2025**, promediada |
| Preguntas | 102 | **107**: las 102, y 5 de la gestión de Galán (§3.2) |

Las poblaciones 2023 y 2022-2024 no se borran.

---

## 2. La ola de 2025

- **Demografía:** sexo (`DMO_1`: 1 hombre, 2 mujer), edad (`DMO_3_1`, años cumplidos), estrato (`DMO_4_1`, 1-6) y localidad
  (`LOCALIDAD`, 1-19). Verificado contra el formulario. 18 localidades: faltan La Candelaria y Sumapaz.
- **Pesos:** `Factor1`, con 60 valores distintos, reescalado por ola × localidad (DI-PO5).
- **Conglomerado:** 2025 no trae identificador de manzana. Como en 2022, cada persona es su propio conglomerado (DI-PO3).
- **Emparejamiento:** el mismo, sin educación: localidad exacta, sexo exacto, y edad y estrato por distancia.

---

## 3. Las preguntas y sus años

### 3.1 Las 102 del catálogo

Cada pregunta se responde con los donantes de los años en que se puede juntar:
- **2022-2024:** como hoy (`epc_armonizado/items.csv`, DI-AR1).
- **2025:** solo las 40 que entran según `verificacion_2025.csv` (14 coinciden exacto y 26 por revisión manual, cada una con
  su razón). Las 4 que no entran (`RC5_6`, `RC5_16`, `RC5_17` y `CV5`) y las 58 que no existen en 2025 siguen con sus años.

**Las evaluaciones del gobierno de turno se juntan solo dentro de la misma administración (DI-AR5):**
- `GG3` (gestión del alcalde/sa) y `CC5A` (gestión del Concejo): 2022-2023, como hoy. Son Claudia López y el Concejo
  2020-2023.
- `CV5` (inversión de recursos): 2022-2023, como hoy.
- **`MICE1` a `MICE3` (garantías del gobierno de la ciudad) pasan a solo 2023.** Hoy juntan 2023 y 2024, y eso mezcla a
  López con Galán. Es una corrección: la nota del gobierno de la página (DI-CO36) ya lo advertía.

### 3.2 Cinco preguntas nuevas: el gobierno de Galán

| Nueva | Pregunta | Años | Columna en 2024 / 2025 |
|---|---|---|---|
| `GG3_GALAN` | Gestión del alcalde Carlos Fernando Galán | 2024-2025 | `GG3` / `GOB_5` |
| `CC5A_GALAN` | Gestión del Concejo de Bogotá (2024-2027) | 2024-2025 | `CC5A` / `GOB_6` |
| `MICE1_GALAN` | Transparencia del gobierno de la ciudad | 2024-2025 | la de 2024 / `GOB_8` |
| `MICE2_GALAN` | Responde a las necesidades de la ciudadanía | 2024-2025 | la de 2024 / `GOB_10` |
| `MICE3_GALAN` | Espacios de participación | 2024-2025 | la de 2024 / `GOB_9` |

- **Las de 2024** tienen que coincidir en etiquetas con la de 2023 (DI-AR1, ya verificado en la armonización).
- **Las de 2025** las verificó `verificacion_2025.csv`.
- **En la página llevan su nota:** «Se midió en 2024 y 2025, con el alcalde Carlos Fernando Galán» (DI-CO36).

---

## 4. Lo que la página tiene que decir distinto

- «Opina como Bogotá **entre 2022 y 2025**».
- En cada respuesta del catálogo, de qué años sale.
- **La reformulación tiene que poder llevar a Galán a sus preguntas nuevas.** La versión 5 manda hoy «la gestión de Galán»
  a «nueva», porque no había dato (`REFORMULACION_GOBIERNO_RESULTS.md`). Con `GG3_GALAN` en el catálogo, lo correcto es el
  catálogo. Eso cambia lo que ve el modelo, así que va con su propia validación, después de construir esta población: la
  prueba de la versión 5, con lo que se espera de las 4 preguntas de Galán cambiado a `GG3_GALAN` y a las demás nuevas.

---

## 5. Verificación (antes de usarla)

**La misma de la población 2022-2024 (§5 de su especificación):**
1. **Demografía:** la peor diferencia por localidad, en sexo, edad y estrato.
2. **Opinión:** no más del 10 % de pares pregunta × localidad fuera del margen del 95 % de los donantes de sus años.
3. **Emparejamiento exacto:** por localidad y por año del donante.
4. **Mezcla de años por localidad:** se dice si una queda dominada por un solo año.
5. **Reproducibilidad:** con la misma semilla, la misma población.

**Además, para 2025:** las cinco cifras publicadas por BCV se reproducen con los donantes de 2025. Ya se comprobó con los
microdatos (§13.10); aquí se repite con los donantes de la población.

---

## 6. Predicciones (escritas antes de construirla)

- **PP1.** La verificación de opinión pasa (≤ 10 % de pares fuera del margen).
- **PP2.** La mediana de donantes por localidad queda entre 300 y 360.
- **PP3.** En ninguna localidad un solo año supera el 40 % de los agentes.
- **PP4.** En las cinco preguntas de la EPC 2025, el error medio de la página contra los microdatos de 2025 baja de 12,9
  puntos. **No es una prueba a ciegas:** 2025 entra a los datos. Se reporta como descripción del cambio, no como
  validación.

---

## 7. Qué se construye después

1. **`armonizar_epc.py`:** que use `verificacion_2025.csv` para 2025 y aplique la corrección de las `MICE`.
2. **`poblacion_epc_olas.py`:** con 2025 y las cinco preguntas de Galán, en una salida nueva
   (`data/processed/poblacion_epc2022_2025/`).
3. **La verificación de §5,** anotada aquí.
4. **La página:** el motor apunta a la población nueva; notas y textos de §4; la validación de la reformulación de §4,
   con su gasto (unos USD 0,06) y su visto bueno.

---

## Enmienda 1 (13/10/2026, antes de construirla): sin las evaluaciones del gobierno de Claudia López

**Lo pidió Daniel:** la gestión de López, que terminó en 2023, no le aporta al jefe. Hoy además es un riesgo: una pregunta
sobre «el alcalde» podía llegar al dato de López (lo corrigió la reformulación versión 5, DI-CO37).

**Qué sale de la población 2022-2025** (catálogo y donantes):
- `GG3` y `CC5A` (gestión del alcalde/sa y del Concejo, 2022-2023);
- `CV5` (inversión de los recursos públicos, 2022-2023). Su versión de 2025 no pasó la verificación, así que la inversión
  **desaparece del todo** de esta población;
- `MICE1` a `MICE3` de 2023 (garantías del gobierno de la ciudad). §3.1 ya las dejaba solo en 2023;
- `GP1N_1` a `GP1N_17` (17 evaluaciones por tema de «el último año del actual gobierno», solo 2023).

Son **23 preguntas**. El catálogo pasa de 107 a **84**: las 79 que quedan y las 5 de Galán (§3.2), que no cambian.

**Lo que no cambia:**
- **No se borra ningún dato.** Siguen en los archivos de BCV, en `epc_armonizado/items.csv` (las 102) y en las poblaciones
  2023 y 2022-2024.
- **Las 139 candidatas de la estimación (DI-CO29)** no se tocan: ese conjunto se validó así.
- La verificación (§5) y las predicciones PP1 a PP4 (§6), ahora sobre las 84.

**Lo que esto le añade a la validación de la reformulación (§4):** sin las preguntas de López en el catálogo, una pregunta
sobre López no puede responderse con las de Galán. La prueba de §4 lleva también las preguntas sobre López de la versión 5,
y pasa solo si ninguna termina en `GG3_GALAN` ni en las demás de Galán. Lo que se espera de cada una se escribe en esa prueba
antes de correrla.

---

## 8. Resultado de la construcción (13/10/2026), contra §5 y §6

Construida con `python src/population/poblacion_epc_olas.py --con-2025` (DI-PO6), después de la enmienda 1. Salida en
`data/processed/poblacion_epc2022_2025/` (sin subir). Sin gasto en API.

**La armonización (DI-AR6):** 35 preguntas suman 2025. Son las 40 verificadas menos las 5 del gobierno de turno, que van
a las de Galán. Fuera de 2025 solo cambian `MICE1` a `MICE3`, que pasan a solo 2023 (§3.1).

| | 2022-2024 | **2022-2025** |
|---|---|---|
| Donantes | 4.522 | **6.042** (1.520 de 2025) |
| Donantes por localidad | mediana 251; 86 a 456 | **mediana 312; 86 a 631**. La Candelaria sigue con 86 |
| Preguntas | 102 | **84**: 79, y las 5 de Galán |
| Demografía, peor diferencia (sexo / edad / estrato) | 2,9 / 3,5 / 2,1 puntos | **2,9 / 3,5 / 2,1 puntos** (no cambia: la ponen los agentes) |
| Opinión fuera del margen del 95 % | 23 de 1.938 (1,2 %) | **32 de 1.596 (2,0 %)** |
| Emparejamiento exacto | 98,2 % | **98,3 %**; por año del donante, 97,5 % a 99,7 % |
| Mayor fracción de un año en una localidad | 38,6 % | **36,9 %** (La Candelaria, 2022) |
| Reproducible con la misma semilla | sí | **sí** |

**Las cifras de BCV con los donantes de 2025** (los pesos `Factor1` de la ciudad): orgullo 56,6 %, satisfacción 61,4 %,
gestión de Galán sin «no sabe» 26,4 % y víctima 14,6 %. Son **exactamente** las de los microdatos (DATA_INVENTORY §13.10).

| | Predicción | Resultado | |
|---|---|---|---|
| PP1 | ≤ 10 % de pares fuera del margen | 2,0 % | se cumple |
| PP2 | mediana por localidad entre 300 y 360 | 312 | se cumple |
| PP3 | ningún año supera el 40 % en una localidad | 36,9 % como máximo | se cumple |
| PP4 | error de la página en las 5 de la EPC 2025 menor que 12,9 | pendiente: se mide con la página apuntando a esta población (§7.4) | — |

**Lo que se esperaba distinto:** «~330 por localidad» (§1) quedó en 312: 2025 encuestó menos en algunas localidades.
La Candelaria no gana donantes, como se previó.
