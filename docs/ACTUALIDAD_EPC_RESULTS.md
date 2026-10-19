# UN RESUMEN DE ACTUALIDAD PARA LOS AGENTES — resultados

Corrido el **19 de octubre de 2026** contra `ACTUALIDAD_EPC_SPECIFICATION.md` (pre-registro y código en `96baa87`, antes de
llamar al modelo y de calcular los reales). **Gasto: USD 0,176.** Ningún agente quedó sin respuesta.

## Lo que salió

Porcentaje de lo que se cuenta (§3 del pre-registro). A: la gente de 2024 con la nota; B: con la nota y el resumen de 2025.

| # | Pregunta | EPC 2024 | **EPC 2025** | A | B |
|---|---|---|---|---|---|
| A1 | La corrupción ha aumentado | 45,4 | **50,6** | 54,1 | 56,0 |
| A2 | Gestión del Concejo, buena | 16,6 | **14,9** | 22,2 | 21,8 |
| A3 | El gobierno es transparente (4-5) | 22,4 | **9,9** | 26,6 | 25,3 |
| A4 | El gobierno responde (4-5) | 17,2 | **6,9** | 23,7 | 21,6 |
| A5 | El gobierno abre participación (4-5) | 19,4 | **10,6** | 20,7 | 18,5 |
| A6 | Gestión de Galán, buena (no decide) | 42,3 | **26,4** | 29,3 | 28,8 |
| A7 | La ciudad va por buen camino (no decide) | 37,1 | **48,2** | 34,5 | 28,2 |

**Errores medios en las cinco que deciden:**

| | Error |
|---|---|
| Repetir 2024 | **7,7** |
| A, sin resumen | 10,9 |
| B, con resumen | 10,1 |

## Reglas

| | Criterio | Resultado | |
|---|---|---|---|
| RA1 | B menor que repetir 2024 | 10,1 contra 7,7 | **no se cumple** |
| RA2 | B menor que A | 10,1 contra 10,9 | se cumple |
| RA3 | dirección del cambio en ≥ 3 de 5 | 2 | **no se cumple** |

**El resumen no sirve, por la regla.** Los agentes siguen apagados con el modelo real.

## Predicciones

| | Predicción | Resultado | |
|---|---|---|---|
| PA1 | A a menos de 3 puntos de repetir 2024 | 10,9 contra 7,7 | **falla** |
| PA2 | RA1 no se cumple | no se cumple | se cumple |
| PA3 | B más pesimista que A en ≥ 4 de 5 | sí | se cumple |

## Qué se aprende

1. **El resumen mueve poco y hacia el pesimismo.** B queda a 1 o 2 puntos de A, siempre hacia el lado negativo. En 2025, Bogotá
   se movió en las dos direcciones: el gobierno y el Concejo, peor calificados; el rumbo de la ciudad, mejor (de 37 a 48). Los
   agentes con resumen bajaron el rumbo a 28: al revés.
2. **Los agentes quedan altos en todo lo del gobierno.** En transparencia, respuesta y participación, la EPC 2025 cayó a la mitad
   (de 17-22 a 7-11) y los agentes se quedaron en 19-27. Una caída tan grande puede ser también del cambio de cuestionario entre
   2024 y 2025 (otra variable, `PC20N` frente a `GOB_8-10`); eso ningún resumen lo enseña.
3. **Lo que sí acertaron, sin que decida:** la gestión de Galán, de 42 en 2024 a 26 en 2025. Los agentes dijeron 29, más cerca
   que repetir 2024. Pero esa cifra ya la conocía, y no cuenta.
4. **Repetir el último dato sigue siendo lo más difícil de superar** (7,7). Es la tercera prueba en que pasa (`GALAN_ACTUAL`,
   `VALIDACION_AGENTES_D22`).
5. **Para el uso que busca Daniel, preguntas nuevas sobre la actualidad:** con lo medido hasta hoy, los agentes se equivocan unos
   10 puntos en lo político, y un resumen de noticias no los corrige.
