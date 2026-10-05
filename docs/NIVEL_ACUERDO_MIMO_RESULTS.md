# ¿ESTARÍA BOGOTÁ DE ACUERDO? — resultados con mimo

Corrido el **5 de octubre de 2026** contra `NIVEL_ACUERDO_MIMO_SPECIFICATION.md` (pre-registro y código en
`0cc32a2`, antes de llamar). `python src/experiments/nivel_acuerdo_mimo.py` →
`data/processed/banco/nivel_acuerdo_mimo.json`.

**Gasto: USD 0,54 en 167 llamadas**, dentro del tope de USD 1,50. Sin respuestas inválidas. Una llamada
pasó los 5 minutos de espera y se reintentó; ese intento cortado, si se cobró, no quedó registrado (menos de
USD 0,01).

## 1. Resultado, mimo frente a Sonnet

| | Sonnet, práctica | **mimo, práctica** | Sonnet, guardado | **mimo, guardado** | regla |
|---|---|---|---|---|---|
| error (EAM) | 13,9 | **16,2** | 12,5 | **13,5** | ≤ 15,8 |
| acierta el lado de la mayoría | 80 % | **73 %** | 77 % | **72 %** | ≥ 67 % (y en el guardado, ≥ referencia + 10) |
| referencia fija | 57 % | 57 % | 51 % | 51 % | |
| rango (h) | 21,9 | 24,4 | 21,9 | 24,4 | |
| al decidir | 16 de 16 | **9 de 12** («sí» 8/10, «no» 1/2) | 12 de 12 | **9 de 9** | juntas ≥ 90 % |
| costo por llamada | USD 0,019 | **USD 0,003** | | | |

En los dos conjuntos juntos, mimo decide en 21 preguntas y acierta 18 (86 %); Sonnet, 28 de 28.

## 2. Contra el pre-registro

**La regla (§3) no se cumple:**
- **práctica:** no cumple, porque el EAM es 16,2 > 15,8, aunque el lado (73 %) sí pasa;
- **guardado:** cumple (13,5 y 72 %, sobre 51 % + 10);
- **al decidir:** no cumple (86 % < 90 %).

| | predicción | resultado | |
|---|---|---|---|
| P1 | mimo no cumple la regla | no la cumple | se cumple |
| P2 | EAM en práctica mayor que Sonnet | 16,2 > 13,9 | se cumple |
| P3 | lado en práctica menor que Sonnet | 73 % < 80 % | se cumple |
| P4 | al menos una respuesta inválida | ninguna | **falla** |

**Por la regla: sigue Sonnet en la página.** Lo siguiente, si se quiere bajar el costo, sería otro modelo
barato (Gemini 3.8 Flash), también pre-registrado.

## 3. Qué quiere decir

- **mimo se acerca bastante** al porcentaje y al lado de la mayoría: está 2-3 puntos de error y 5-7
  puntos de acierto por detrás de Sonnet. En el guardado incluso cumpliría solo.
- **Donde falla es en lo que más importa para la página: el «probablemente».** De 21 veces que se atrevió
  a decir «probablemente sí» o «probablemente no», se equivocó en 3. Sonnet no se ha equivocado en 28. La
  página promete que, cuando dice «probablemente», casi siempre acierta, y con mimo esa promesa no se
  sostiene.
- **El costo es la diferencia real:** USD 0,003 contra 0,019 por pregunta. Con el volumen actual de la
  página (pocas preguntas al día), la diferencia es de centavos. Si el uso crece mucho, vale la pena
  probar otro modelo barato.

## 4. Límites

1. Los dos conjuntos ya se habían usado para validar a Sonnet (pre-registro §3).
2. Una sola llamada por pregunta y temperatura 0: no se midió cuánto varía mimo entre llamadas.
