# PREGUNTAS REALES NUEVAS — RESULTS

**El puente no acertó el orden de los grupos: 8 de 24 diferencias claras, menos que el azar. En el Corredor Verde lo invirtió casi por completo. Por la regla escrita, la página deja de mostrar de entrada las barras por grupo en las preguntas nuevas.**

Proyecto: Bogotá Social Simulator
Fecha: 1 de octubre de 2026
Pre-registro: `PREGUNTAS_REALES_NUEVAS_SPECIFICATION.md` (commit b126d6d). Código: `src/experiments/preguntas_reales.py`
(ed126a5), subido antes de correr. Corrida de Daniel en su terminal.
Gasto: **6 llamadas, USD 0,014**; ningún reintento: el modelo nunca dijo «sin base».
Resultado: `data/processed/preguntas_reales/resultado.json`

---

## 1. Lo que propuso el modelo

| | Puente (llamada 1; las otras dos muy parecidas) | Fuerza | Nivel |
|---|---|---|---|
| **Metro elevado** | + optimismo con el metro (`MV150`, peso 3), + evaluación del gobierno en movilidad, + satisfacción con el transporte, − optimismo con Bogotá | media, las 3 | 3,7 |
| **Corredor Verde** | + satisfacción con los árboles (`MA3_4`, 3), + zonas verdes (`EP1B_6`, 3), + bicicarriles, + gobierno en espacio público, + calidad del aire | media, las 3 | 3,7 |

## 2. Los grupos: simulador frente a la encuesta real

Índice del simulador (llamada 1, en desviaciones estándar) y porcentaje real de «sí».

| | Metro: simulador | Metro: real | Corredor: simulador | Corredor: real |
|---|---|---|---|---|
| Hombres / Mujeres | +0,07 / −0,06 | 61,5 / 69,4 | +0,03 / −0,03 | 53,7 / 63,3 |
| 18-24 / 25-34 / 35-54 / 55+ | +0,05 / +0,01 / −0,05 / +0,05 | 61,5 / 56,8 / 69,8 / 70,9 | −0,03 / −0,04 / −0,03 / +0,09 | 67,7 / 63,7 / 59,0 / 49,2 |
| Estrato 1 / 2 / 3 / 4 / 5-6 | +0,04 / −0,04 / +0,02 / +0,09 / −0,05 | 69,7 / 64,2 / 63,0 / 69,4 / 74,6 | −0,07 / −0,03 / −0,02 / +0,11 / +0,27 | 69,0 / 65,2 / 57,1 / 45,9 / 51,5 |

## 3. Contra el pre-registro

| # | Predicción | Umbral | Resultado | |
|---|---|---|---|---|
| **P1** | Acierta el orden de los grupos | ≥ 0,70 de los 24 pares y > p95 del azar (0,67) | **0,33 (8 de 24)** | **no se cumple** |
| P2 | En cada pregunta | ≥ 0,60 en cada una | metro 0,55; **Corredor 0,15** | no se cumple |
| P3 | El nivel va en la dirección real | > 3 en las dos, mayor en el metro | 3,7 y 3,7 | no se cumple (empate) |
| P4 | Las localidades | Pearson en 13 (se reporta) | metro −0,12; Corredor −0,15 | — |

**Regla de decisión (§7): P1 no se cumple.** En las preguntas nuevas, la página deja de mostrar las
barras por grupo de entrada: solo si la persona lo pide, con el aviso de que en una prueba con
preguntas reales el orden de los grupos no se sostuvo. El nivel y en qué se apoya la suposición se
siguen mostrando.

## 4. Lo que el resultado precisa (descriptivo)

- **En el Corredor Verde, el puente apunta al revés.** Lo apoyaban más los estratos bajos, los jóvenes
  y las mujeres; el puente dice lo contrario en casi todo (2 de 13 pares). La mediana de los puentes
  al azar es 0,46, así que esto está muy por debajo del azar: no es ruido, es una dirección equivocada.
- **Por qué, probablemente:** el modelo eligió preguntas **del mismo tema** (árboles, zonas verdes,
  bicicarriles) y supuso que quien está satisfecho con lo verde apoya un corredor verde. Pero el
  apoyo real no dependía de eso, sino, muy probablemente, de quién se ve afectado y de la política: la
  séptima pasa por el norte, y era un proyecto de la alcaldía de entonces. **Parecerse en el tema no es
  lo mismo que predecir quién está de acuerdo.** Esa es la diferencia con las preguntas escondidas,
  donde el tema y la respuesta sí iban juntos.
- **En el metro, cerca del azar** (0,55, mediana del azar 0,55). Las mujeres lo apoyaban más; el puente
  dice que los hombres.
- **Las diferencias son mínimas de todos modos:** los índices por grupo van de −0,07 a +0,27
  desviaciones estándar. Aun cuando el orden fuera correcto, el puente casi no separa a los grupos.
- **La fuerza dijo «media» en las dos.** Mide qué tan cerca está el tema del catálogo, no si el puente
  acierta. La página tiene que decirlo así.
- **El nivel** salió igual en las dos (3,7), por encima del punto medio como el real, sin distinguir que
  el metro tenía más apoyo.

## 5. Qué cambia para el proyecto (para discutir con Daniel)

Esta es la primera prueba de una pregunta de verdad nueva contra datos reales, y salió mal en lo que
la página promete para esas preguntas: qué grupos estarían más o menos de acuerdo. La regla escrita
solo esconde las barras. Queda abierta una pregunta más grande, de proyecto: **¿la página debe seguir
respondiendo preguntas nuevas, y con qué?**

## 6. Límites

- **Dos preguntas.** Un fallo tan claro en una (el Corredor) dice mucho; aun así, son dos.
- **Métodos distintos:** la encuesta real fue en línea por SMS y la EPC cara a cara. Puede mover los
  grupos, pero no explica que el Corredor salga invertido en estrato, edad y sexo a la vez.
- **Agosto de 2023, en campaña:** los dos temas eran de campaña a la Alcaldía, lo que favorece justo
  el tipo de división que la EPC no mide.
- **Ignorar el efecto de diseño** hace pasar por claras algunas diferencias; no cambia el resultado,
  que queda lejos de todos los umbrales.
