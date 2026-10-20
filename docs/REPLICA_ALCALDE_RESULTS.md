# PLAN V4, PASO 1: ¿SE REPITE EL ACIERTO DE LOS AGENTES CON EL ALCALDE? — resultados

Corrido el **20 de octubre de 2026** contra `REPLICA_ALCALDE_SPECIFICATION.md` (pre-registro y código en `eedd9e8`, antes de llamar
al modelo). **Gasto: USD 0,167.** Respondieron todos los agentes; no se excluyó ningún objetivo.

## La respuesta corta

**No se repite.** El acierto con Galán 2025 es el único caso del alcalde en que los agentes le ganan a repetir el dato. En las 15
preguntas de gobierno, los agentes se equivocan 8,7 y la persistencia 7,4.

## Por pregunta

| Transición | Pregunta | P, persistencia | G, agentes | Real |
|---|---|---|---|---|
| 2022 → 2023 | rumbo (`AG1`) | 35,1 | 27,6 | 31,2 |
| 2022 → 2023 | corrupción aumentó (`GG7`) | 40,9 | 61,2 | 35,8 |
| 2022 → 2023 | **gestión de López** | **33,1** | 25,3 | **31,1** |
| 2022 → 2023 | gestión del Concejo | 16,5 | 14,8 | 12,8 |
| 2023 → 2024 | rumbo | 31,2 | 31,7 | 37,1 |
| 2023 → 2024 | corrupción aumentó | 35,8 | 53,0 | 45,4 |
| 2023 → 2024 | **gestión de Galán, recién llegado** | **31,1** (López 2023) | 31,1 | **42,3** |
| 2023 → 2024 | gestión del Concejo | 12,8 | 14,5 | 16,6 |
| 2024 → 2025 | rumbo | 37,1 | 35,6 | 48,2 |
| 2024 → 2025 | corrupción aumentó | 45,4 | 44,3 | 50,6 |
| 2024 → 2025 | **gestión de Galán** | **42,3** | 29,3 | **26,4** |
| 2024 → 2025 | gestión del Concejo | 16,6 | 20,9 | 14,9 |
| 2024 → 2025 | transparencia | 22,4 | 25,2 | 9,9 |
| 2024 → 2025 | respuesta a la ciudadanía | 17,2 | 22,7 | 6,9 |
| 2024 → 2025 | participación | 19,4 | 19,8 | 10,6 |

## Error y sesgo

| | Error medio | Sesgo |
|---|---|---|
| **P, persistencia** | **7,37** | +1,1 |
| G, agentes | 8,74 | +2,5 |

| Transición | Casos | P | G | Sesgo de G |
|---|---|---|---|---|
| 2022 → 2023 | 4 | **3,7** | 9,2 | +4,5 |
| 2023 → 2024 | 4 | 7,6 | **6,5** | −2,8 |
| 2024 → 2025 | 7 | **9,4** | 9,7 | +4,4 |

**Solo el alcalde:**

| Transición | Error de P | Error de G | Gana |
|---|---|---|---|
| 2022 → 2023 (López) | 2,0 | 5,8 | persistencia |
| 2023 → 2024 (llega Galán) | 11,2 | 11,2 | empate |
| 2024 → 2025 (Galán) | 15,9 | 2,9 | **agentes** |

## Reglas

| | Criterio | Resultado | |
|---|---|---|---|
| RP1 | G al menos 1 punto menor que P en los 15 | 8,74 contra 7,37 | **no se cumple** |
| RP2 | G menor que P en 2 de 3 transiciones | solo en 2023 → 2024 | **no se cumple** |
| RP3 | G menor que P sin sus dos mejores casos | no | **no se cumple** |
| RA | en el alcalde, G gana en 2 de 3 | 1 de 3 | **no se cumple** |

**Los agentes no se reproducen en gobierno.** Según §6, se informa que el acierto de 2025 no se repite, y en la página nada cambia
(decisión de producto).

**Sensibilidad sin los `MICE`** (12 objetivos): P 6,6, G 7,6. Tampoco cambia.

## Predicciones

| | Predicción | Resultado | |
|---|---|---|---|
| PR1 | RP1 no se cumple | no se cumple | se cumple |
| PR2 | en el alcalde, G gana en 1 de 3 o menos | 1 de 3 | se cumple |
| PR3 | el sesgo de G es positivo | +2,5 | se cumple |

## Qué se aprende

1. **El acierto con Galán 2025 parece un caso, no una capacidad.**
   - Con López (2022 → 2023), la opinión casi no se movió y los agentes la bajaron 8 puntos sin razón.
   - Cuando llegó Galán (2023 → 2024), la opinión subió 11 puntos y los agentes no lo vieron: repitieron el nivel de López.
   - En 2025 los agentes bajaron a Galán y la opinión también bajó. Coincide con su tendencia a bajar al alcalde, más que con
     una lectura del cambio.
2. **Los agentes tienden a castigar al alcalde de turno:** lo bajaron en 2023 y en 2025, y no lo subieron cuando subió. En 2025
   acertaron porque la opinión bajó.
   - **Corrección (20/10, después del plan v5):** «castigar al alcalde» es una lectura de más. Las tres cifras de los agentes
     (25, 31 y 29) se quedan cerca del 30 % mientras lo real va de 26 a 42: es tan compatible con un valor central como con
     pesimismo. Se prueba en `ALCALDE_SIN_NOMBRE_SPECIFICATION.md`.
3. **La corrupción es su error más grande:** dijeron 61 en 2023, cuando lo real fue 36. Ven más corrupción de la que la gente
   reporta.
4. **Comparación declarada en §5 (rumbo y corrupción 2023 → 2024):** con el perfil de la Fase B, sin el alcalde y el Concejo, los
   agentes dijeron 33,6 y 45,5. Con el perfil nuevo, 31,7 y 53,0. El perfil nuevo empeora estas dos: errores de 3,5 y 0,1 en la
   Fase B, contra 5,4 y 7,6 ahora.
5. **Con 15 casos y la filtración temporal posible** (el modelo puede saber lo que pasó), el resultado más claro es negativo: en
   gobierno, repetir el último dato acierta más que los agentes, igual que en el conjunto completo.

## Qué significa para el producto

- **La página no cambia** (decisión de Daniel): la cifra de Galán sigue siendo la de los agentes, como estimación exploratoria y
  con su error a la vista.
- **Lo que ya no se puede decir:** que los agentes «ven los cambios» en la opinión sobre el alcalde. En tres años lo hicieron una
  vez.
- **La prueba que queda es hacia adelante:** la EPC 2026 de diciembre, con los agentes de 2025 y la persistencia de 2025.
