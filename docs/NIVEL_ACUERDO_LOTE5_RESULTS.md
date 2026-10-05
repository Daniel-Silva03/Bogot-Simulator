# ¿MEJORA LA ESTIMACIÓN CON LAS CANDIDATAS DEL LOTE 5? — resultados

Corrido el **5 de octubre de 2026** contra `NIVEL_ACUERDO_LOTE5_SPECIFICATION.md`.
- Pre-registro en `c951220`, código antes de llamar y resultados reales del guardado del lote 5 en
  `3db3cef`.
- `python src/experiments/nivel_acuerdo_lote5.py` → `data/processed/banco/nivel_acuerdo_lote5.json`.

**Gasto: USD 2,73 en 116 llamadas a Sonnet**, dentro del tope de USD 3,50. Sin respuestas inválidas.

## 1. Resultado

95 preguntas guardadas de acuerdo o sí/no:
- 74 de los lotes 1 a 3, ya usadas en la validación de D19;
- 21 del lote 5, que nadie había mirado.

Rango fijo de ±21,9 para las dos configuraciones.

| | A: 92 candidatas (la de hoy) | **B: 109 (con el lote 5)** | regla para B |
|---|---|---|---|
| error (EAM), 95 | 12,8 | **11,9** | ≤ 15,8 y ≤ A |
| acierta el lado de la mayoría | 74 % | 72 % | ≥ 67 % y ≥ 54 % + 10 |
| decide («probablemente sí/no») | 13 % (12) | **18 % (17)** | |
| al decidir | 12 de 12 | **17 de 17** («sí» 9/9, «no» 8/8) | ≥ 90 % |
| error, solo las 21 del lote 5 | 13,6 | **9,9** | |
| error, solo las 74 de los lotes 1 a 3 | 12,5 | 12,5 | |

En B, 25 de las 95 preguntas eligieron al menos una candidata del lote 5.

## 2. Contra el pre-registro

| | predicción | resultado | |
|---|---|---|---|
| P1 | B reemplaza a A (las tres condiciones) | se cumplen las tres | se cumple |
| P2 | en las 21 del lote 5, B al menos 2 puntos mejor | 9,9 contra 13,6 | se cumple |
| P3 | en las 74, B a menos de 1 punto de A | 12,5 y 12,5 | se cumple |
| P4 | B decide en más preguntas | 18 % contra 13 % | se cumple |

**Regla (§4): B reemplaza a A en la página.**

## 3. Qué quiere decir

- **Sumar preguntas medidas del mismo formato mejora la estimación sin empeorar nada.**
  - En las preguntas de la misma encuesta, el error baja de 13,6 a 9,9 puntos.
  - En las demás queda igual.
  - Además, se atreve a decir «probablemente» en más casos (17 contra 12), y acierta todos.
- **El acierto del lado bajó 2 puntos** (74 % → 72 %): una pregunta. La regla no lo exige, pero se
  informa.
- **Es la confirmación más clara de lo que venían diciendo todas las pruebas:** lo que acerca al
  simulador a la Bogotá real son **datos de preguntas parecidas ya medidas**. Cada lote nuevo de
  preguntas de acuerdo (y, sobre todo, de aprobación de medidas) debería mejorar la estimación.

## 4. Incidencias y límites

1. **Al probar el código en modo simulado, antes de la corrida real,** el script imprimió cifras de las
   21 guardadas del lote 5 calculadas con elecciones falsas. Dejaban ver algo de cómo se reparten sus
   resultados reales. La regla y las predicciones ya estaban subidas y no cambiaron; se deja escrito.
2. Las 74 de los lotes 1 a 3 ya se habían usado para validar A. Para B son nuevas como objetivos, pero
   no son datos que nadie hubiera mirado.
3. Las 17 decisiones acertadas de B son pocas para afirmar una tasa.
