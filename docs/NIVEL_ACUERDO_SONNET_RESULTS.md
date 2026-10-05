# ¿ESTARÍA BOGOTÁ DE ACUERDO? — resultados del paso 2 (Claude Sonnet)

Corrido el **5 de octubre de 2026** contra `NIVEL_ACUERDO_SONNET_SPECIFICATION.md` (pre-registro y código
en `8857ded`, antes de llamar). `python src/experiments/nivel_acuerdo_sonnet.py` →
`data/processed/banco/nivel_acuerdo_sonnet.json`.

**Gasto: USD 1,73 en 93 llamadas** (92 más la de prueba), dentro del tope de USD 3. Sin respuestas
inválidas.

## 1. Resultado

92 preguntas de práctica de acuerdo o de sí/no, en 25 familias. Cada pregunta, sin su familia:

| | error (EAM) | acierta el lado de la mayoría | decide con rango del 80 % | al decidir |
|---|---|---|---|---|
| decir siempre el lado más común | — | 57 % | — | — |
| promedio (M0, paso 1) | 19,7 | 57 % | 0 % | — |
| vecinos por texto (M1, paso 1) | 18,2 | 63 % | 7 % | 6 de 6 |
| **Claude Sonnet 5.5** | **13,9** | **80 %** | **17 %** (16 preguntas) | **16 de 16** («sí» 10/10, «no» 6/6) |
| regla | ≤ 15,8 | ≥ 67 % | | |

Sonnet tiene menos error que M1 en 56 de las 92 preguntas. El rango típico (h, cuantil 80 % de sus
errores en las otras familias) es de **±22 puntos**.

## 2. Contra el pre-registro

| | predicción | resultado | |
|---|---|---|---|
| P1 | Sonnet no cumple la regla | **la cumple** | **falla** |
| P2 | EAM menor que M1 (18,2) | 13,9 | se cumple |
| P3 | acierta el lado más que M1 (63 %) | 80 % | se cumple |
| P4 | decide en menos del 30 % | 17 % | se cumple |

**Regla (§3): Sonnet sirve para decir «sí o no»** en la práctica. Por la regla escrita, **todavía no
va a la página**: se propone validarlo, pre-registrado y con su costo, en el **guardado** (20 familias
de acuerdo o sí/no que nadie ha mirado).

## 3. Qué quiere decir

- **Es la primera vez que algo cruza la vara** en todas las pruebas del nivel. Funcionó al acotar el
  problema al tipo de pregunta que hace la página (acuerdo o sí/no) y con el banco ampliado (la Bienal
  aporta muchas preguntas de ese tipo, de Bogotá).
- **Lo que podría decir la página:**
  - «Probablemente sí» o «probablemente no» solo cuando el rango no cruza el 50 %, lo que en la
    práctica pasó en 1 de cada 6 preguntas, todas acertadas.
  - En las demás, «dividida», con el porcentaje estimado y su rango.
- **Por qué validar antes:** la práctica ya se usó en muchas pruebas, y P1 falló a favor. Un resultado
  que sorprende hay que repetirlo con datos que no se han visto antes de creerlo.

## 4. Límites

1. 25 familias; las 16 llamadas acertadas son pocas para afirmar una tasa.
2. Las candidatas que ve Sonnet son solo las de práctica de este subconjunto. En la página serían todas
   las medidas de este tipo.
3. Un rango de ±22 puntos es ancho. Por eso la mayoría de las preguntas quedan «divididas».
