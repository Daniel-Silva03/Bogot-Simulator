# FASE B DEL PLAN DE MEJORAS: ¿DEBEN LOS AGENTES MOVER UN DATO YA MEDIDO? — resultados

Corrido el **19 de octubre de 2026** contra `SELECTOR_FASE_B_SPECIFICATION.md` (pre-registro en `824dedb` y enmienda 1 en
`d2e4630`, antes de llamar al modelo). **Gasto: USD 0,686**, dentro del tope de USD 1. Respondieron todos los agentes en las 81
preguntas. Cifras por pregunta en `data/processed/benchmark/selector_fase_b.csv`.

## Error medio

| | P1: 2023 → 2024 (50) | P2: 2024 → 2025 (31) | Juntos (81) | Gobierno (11) |
|---|---|---|---|---|
| **P, repetir el dato** | **4,70** | **6,09** | **5,23** | **7,89** |
| G, agentes | 5,75 | 8,33 | 6,73 | 9,03 |
| C, P + λ·(G − P) | 4,70 | 6,14 | 5,25 | 7,96 |
| Cd, un λ para gobierno y otro para lo demás | 4,70 | 6,59 | 5,42 | 9,23 |

**Los λ elegidos** (cada uno con el otro par):

| Para evaluar | C | Cd, gobierno | Cd, lo demás |
|---|---|---|---|
| P1 | 0 | 0 | 0 |
| P2 | 0,05 | **0,95** | 0,05 |

Con los dos pares juntos, el λ de C es **0**.

## Reglas

| | RS1: gana en los dos pares | RS2: sin las dos mejores | RS3: no empeora gobierno | |
|---|---|---|---|---|
| C | no (empata en P1, pierde en P2) | no | sí | **no pasa** |
| Cd | no | no | no (9,23 contra 7,89) | **no pasa** |

## Por dominio, agentes contra persistencia (sin regla)

| Dominio | Preguntas | P | G |
|---|---|---|---|
| Cultura ciudadana | 17 | 6,9 | **6,1** |
| Economía y hogar | 17 | 4,3 | 6,2 |
| Movilidad | 16 | 4,7 | 7,0 |
| Gobierno e instituciones | 11 | 7,9 | 9,0 |
| Espacio público | 6 | 2,5 | 3,8 |
| Seguridad | 6 | 3,9 | 4,9 |
| Ciudad en general | 4 | 2,8 | 5,7 |
| Cultura y recreación | 4 | 5,2 | 12,8 |

## Predicciones

| | Predicción | Resultado | |
|---|---|---|---|
| PS1 | λ de 0,2 o menos en los dos ajustes | 0 y 0,05 | se cumple |
| PS2 | C no pasa | no pasa | se cumple |
| PS3 | G peor que P en todo dominio con 5 o más | en cultura ciudadana, G es mejor (6,1 contra 6,9) | **falla** |

## Qué se aprende

1. **Con un dato medido, lo mejor es mostrar el dato.** El λ aprendido es 0: mover la cifra hacia los agentes no ayuda, ni en
   general ni en gobierno. Es la respuesta de la Fase B, con 81 preguntas y años reservados.
2. **El λ por dominio muestra el riesgo que advertía el plan.** Con las pocas preguntas de gobierno de 2023 → 2024, el selector
   aprendió λ = 0,95 («hazle caso a los agentes»), y en 2025 eso empeoró gobierno de 7,9 a 9,2. Una regla aprendida con pocos
   casos puede ser falsa.
3. **Los agentes, con todo su perfil, no están lejos:** 6,7 contra 5,2. Más cerca que en `ACTUALIDAD_EPC` (10,9), donde iban solo
   siete preguntas en la llamada. Pero no traen la señal del cambio: si la trajeran, λ subiría.
4. **La excepción es la cultura ciudadana** (cómo se comporta la gente en Bogotá): ahí los agentes ganan (6,1 contra 6,9). Es una
   sola casilla, sin regla; para usarla habría que probarla aparte.

## Lo que esto dice para la página

La regla de producto que respalda la Fase B: **si la pregunta ya está medida, se muestra la última medición**; los agentes quedan
para lo que no tiene dato. Hoy la página hace lo contrario en las cuatro preguntas de Galán del catálogo (DI-CO41, por decisión
de Daniel): ahí la evidencia dice que la cifra medida es mejor.
