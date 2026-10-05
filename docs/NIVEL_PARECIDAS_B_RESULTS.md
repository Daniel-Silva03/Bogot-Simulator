# NIVEL POR PREGUNTAS PARECIDAS — resultados de la parte B (modelos más fuertes)

Corrido del **2 al 5 de octubre de 2026** contra `NIVEL_PARECIDAS_B_SPECIFICATION.md` (pre-registro en
`a561ec6`, enmienda 1 en `d3e65e4`). `python src/experiments/nivel_parecidas_b.py` →
`data/processed/banco/nivel_parecidas_b.json`.

**Gasto: USD 2,38 en 218 llamadas**, dentro del tope de USD 4. Incluye:
- las 23 respuestas de DeepSeek con razonamiento, que no se evalúan;
- las llamadas de prueba.

El uso de la clave en OpenRouter subió lo mismo que se registró, con el retraso con que OpenRouter lo
anota.

## 1. Resultado

96 preguntas de práctica. El modelo elige de 1 a 5 preguntas parecidas de otras familias sin ver sus
resultados, y la predicción es la media real de las elegidas. Error absoluto medio (EAM) del
porcentaje favorable, en puntos:

| | EAM | error ≤ 10 | Bogotá (32) | general (64) |
|---|---|---|---|---|
| promedio (R0, parte A) | 23,0 | 23 % | 16,1 | 26,5 |
| vecinos por texto (R2, parte A) | 22,0 | 25 % | 16,4 | 24,8 |
| **DeepSeek V4 Pro, sin razonar** | **21,6** | 32 % | 16,6 | 24,1 |
| **Claude Sonnet 5.5** | **18,1** | 42 % | 17,8 | **18,3** |
| vara | 17,6 | | | |

Ninguno tuvo respuestas inválidas. Los dos eligieron 5 preguntas en la mediana. Sonnet le gana a R2 en
58 de las 96 preguntas; DeepSeek, en 49.

## 2. Contra el pre-registro

| | predicción | resultado | |
|---|---|---|---|
| P1 | DeepSeek no llega a 17,6 | 21,6 | se cumple |
| P2 | Sonnet no llega a 17,6 | 18,1 | se cumple (por 0,5 puntos) |
| P3 | los dos < 23,0 | 21,6 y 18,1 | se cumple |
| P4 | Sonnet < DeepSeek | 18,1 < 21,6 | se cumple |

**Regla (§7): ninguno llega a 17,6, así que se cierra el camino 2 con modelos de lenguaje.** No se
prueba Opus ni Fable salvo que Daniel lo pida con esta evidencia a la vista.

## 3. Qué quiere decir

- **Sonnet es el primer método que se acerca de verdad:** baja el error un 18 % respecto del mejor
  método sin API. Hacía falta un 20 %, y no llega.
- **Toda su ventaja está en las preguntas generales de la ECP** (18,3 contra 24,8). **En las de Bogotá
  no mejora; queda peor** (17,8 contra 16,4). Las preguntas de Bogotá son las que le importan a la
  página, así que para la página el resultado es nulo.
- **Metro y Corredor Verde:**
  - Sonnet acierta el metro (real 65,7 %, da 67,1 %, apoyándose en el Corredor) pero falla el
    Corredor (real 58,8 %, da 38,8 %).
  - DeepSeek hace casi lo contrario: Corredor 65,7 % (real 58,8) y metro 41,0 % (real 65,7).
  - Con dos preguntas, ninguno de los dos aciertos dice mucho.
- **DeepSeek sin razonar no se separa de los métodos gratuitos.** Por la enmienda 1, esto no dice cómo
  le iría razonando.
- **Junto con la parte A y la forma de la pregunta:** el único avance claro sale de un modelo fuerte
  eligiendo bien entre preguntas que existen. Lo que limita, sobre todo en Bogotá, sigue siendo que
  falten preguntas casi iguales ya medidas. Ese es el sentido de ampliar el banco (lotes 2 a 4) y de
  pedirle datos al CNC (camino 3).

## 4. Incidencias

1. **2/10:** primero se cayó la red y después la corrida fue lenta. Con 90 s de espera, DeepSeek tardaba
   ~8 minutos por respuesta; el tiempo de espera pasó a 300 s, un modelo a la vez (DI-NB4).
2. **2/10:** la cuenta de OpenRouter, que es compartida, se quedó sin saldo con 24 de 96 preguntas de
   Sonnet (error 402). El jefe de Daniel recargó USD 10 el 5/10 y se retomó desde la caché.
3. **5/10:** DeepSeek con razonamiento seguía tardando ~5 minutos por respuesta. Enmienda 1: sin
   razonamiento (DI-NB5).
4. **El precio de DeepSeek varió entre proveedores:** OpenRouter repartió las llamadas entre 10
   proveedores, con costos de USD 0,0004 a 0,0125 por llamada.
5. El script imprime el error de cada modelo al cerrar su bloque. El de Sonnet se vio antes de decidir
   la enmienda 1; queda escrito en ella.
