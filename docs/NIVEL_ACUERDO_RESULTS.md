# ¿ESTARÍA BOGOTÁ DE ACUERDO? — resultados del paso 1 (sin API)

Corrido el **5 de octubre de 2026** contra `NIVEL_ACUERDO_SPECIFICATION.md` (pre-registro en `c0742df`,
código en `2e906c6`, antes de correr). Sin gasto. `python src/experiments/nivel_acuerdo.py` →
`data/processed/banco/nivel_acuerdo.json`.

## 1. Resultado

92 preguntas de práctica de acuerdo o de sí/no, en 25 familias; en **40** la mayoría real dijo «sí».
Cada pregunta, sin su familia:

| | EAM (puntos) | acierta el lado | decide con rango del 80 % | al decidir |
|---|---|---|---|---|
| referencia fija (el lado mayoritario del pozo) | — | **57 %** | — | — |
| M0, promedio | 19,7 | 57 % | 0 % | — |
| **M1, vecinos por texto** | **18,2** | **63 %** | 7 % (6 preguntas) | **6 de 6** («sí») |
| M2, forma | 22,6 | 41 % | 0 % | — |

## 2. Contra el pre-registro

| | predicción | resultado | |
|---|---|---|---|
| P1 | la referencia fija acierta el lado entre 60 % y 80 % | 57 % | **falla, por abajo** |
| P2 | ningún método cumple la regla | ninguno la cumple | se cumple |
| P3 | M2 tiene el menor EAM | M2 es el peor (22,6) | **falla** |
| P4 | el mejor método decide en < 30 % | M1 decide en 7 % | se cumple |

**Regla (§6): ningún método sirve para decir «sí o no» en la página.** El mejor, M1:
- acierta el lado 6 puntos más que la referencia; hacían falta 10;
- baja el EAM un 8 %; hacía falta un 20 %.

La página sigue sin decir «sí» o «no».

## 3. Qué quiere decir

- **Acotar a preguntas de acuerdo ayudó en algo, pero no lo suficiente.**
  - En este subconjunto la mayoría dice «sí» en 40 de 92, así que decir siempre «no» ya no acierta el
    72 %, sino el 57 %.
  - Las preguntas parecidas por texto suben eso a 63 % y aciertan las 6 veces que se atreven a decir
    «probablemente sí».
  - Con 6 casos, eso es una pista, no una prueba.
- **La forma de la pregunta no sirve aquí** (41 %, peor que el azar): dentro de este subconjunto las
  escalas se parecen y no explican el nivel.
- **El error típico sigue en 18-20 puntos.** Para decir algo útil sobre el lado (por ejemplo, «entre
  55 % y 75 %»), el error tendría que bajar a la mitad.

## 4. Lo que queda

1. **El paso con Sonnet sobre este subconjunto.** En la parte B, Sonnet fue el mejor eligiendo
   preguntas parecidas, y aquí el método que mejor va es justamente elegir parecidas. Serían unas 92
   llamadas, alrededor de USD 2; se pre-registra y se le consulta el gasto a Daniel antes.
2. **El camino 3:** preguntas de aprobación de medidas medidas por el CNC, que son las «hermanas» que
   más faltan.

## 5. Límites

1. 25 familias; las 6 llamadas acertadas de M1 son pocas.
2. La práctica ya se había mirado en otras pruebas, aunque nunca este subconjunto en particular.
3. «Sí/no» mezcla preguntas positivas («¿usaría el metro?») y negativas («¿se justifica desobedecer la
   ley…?»), y eso puede pesar como pesó en el tono (`TECHO_GRUPOS_LOTES_RESULTS.md` §3).
