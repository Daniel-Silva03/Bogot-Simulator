# ¿ESTARÍA BOGOTÁ DE ACUERDO? — resultados con GPT-6 Luna

Corrido el **6 de octubre de 2026** contra `NIVEL_ACUERDO_LUNA_SPECIFICATION.md` (pre-registro y código en
`273a443`, antes de llamar).
- **Comando:** `python src/experiments/nivel_acuerdo_luna.py`.
- **Salida:** `data/processed/banco/nivel_acuerdo_luna.json`.

**Gasto: USD 0,185 en 187 llamadas**, más USD 0,0008 de la llamada de prueba. Queda dentro del tope de USD 0,75.
- **Práctica:** ~USD 0,0008 por pregunta.
- **Guardado:** ~USD 0,0012 por pregunta, contra ~USD 0,024 de Sonnet. Es 20 veces menos.
- **Sin respuestas inválidas.**

## 1. Resultado, Luna frente a Sonnet y mimo

| | Sonnet, práctica | **Luna, práctica** | mimo, práctica | Sonnet, guardado (95, 109 candidatas) | **Luna, guardado** | regla |
|---|---|---|---|---|---|---|
| error (EAM) | 13,9 | **14,5** | 16,2 | 11,9 | **14,3** | ≤ 15,8; en el guardado, ≤ 13,4 |
| acierta el lado | 80 % | **83 %** | 73 % | 72 % | **69 %** | ≥ 67 % (guardado: ≥ 54 % + 10) |
| rango (h) | 21,9 | 23,4 | 24,4 | 21,9 | 23,4 | |
| decide («probablemente») | 16 | **17** | 12 | 17 | **11** | |
| acierta al decidir | 16 de 16 | **16 de 17** | 9 de 12 | 17 de 17 | **10 de 11** | las dos juntas ≥ 90 % |

- **Luna elige pocas candidatas:** en promedio 2,8 por pregunta en el guardado (en 8 elige una sola). Sonnet
  suele elegir 5.
- **Sus errores al decidir:** los dos son «probablemente sí» en preguntas con menos de 50 % de acuerdo.

## 2. Contra el pre-registro

| Condición | Resultado | |
|---|---|---|
| 1. Práctica: EAM ≤ 15,8 y lado ≥ 67 % | 14,5 y 83 % | cumple |
| 2. Guardado: EAM ≤ 15,8, lado ≥ 67 % y ≥ 64 % | 14,3 y 69 % | cumple |
| 3. Al decidir, juntas, ≥ 90 % | 26 de 28 (93 %) | cumple |
| 4. Guardado: EAM ≤ 11,9 + 1,5 = 13,4 | 14,3 | **no cumple** |

**Por la regla, sigue Sonnet en la página.** Luna pasa las tres condiciones de la regla con que se validó
Sonnet, y que mimo no pasó. Falla la cuarta, añadida en este pre-registro para no perder precisión por
ahorrar: en el guardado, su error es 2,4 puntos mayor que el de Sonnet.

| | Predicción | Resultado | |
|---|---|---|---|
| P1 | Luna no cumple la regla | no la cumple (solo por la condición 4) | se cumple |
| P2 | EAM en práctica mayor que Sonnet (13,9) | 14,5 | se cumple |
| P3 | Lado en práctica menor que Sonnet (80 %) | 83 % | **falla** |
| P4 | Al menos una respuesta inválida | ninguna | **falla** |

## 3. Lo que queda por decidir (fuera de la regla)

La regla responde «¿estima igual de bien que Sonnet?», y la respuesta es no, por poco. No responde «¿vale la pena el ahorro?».
Esa es una decisión de proyecto, de Daniel y su jefe, y si se toma va como D0X en `PROJECT_CONTEXT.md`.
**No es un «pasó».**
- **A favor de cambiar a Luna:**
  - cuesta 20 veces menos;
  - en la práctica estima casi igual que Sonnet;
  - acierta el lado tanto o más.
- **En contra:**
  - en el guardado se equivoca 2,4 puntos más;
  - decide menos (11 contra 17);
  - al decidir se equivocó 2 veces, y Sonnet ninguna.
- **Si se cambia,** la página tendría que citar las cifras de Luna y no las de Sonnet:
  - el lado de la mayoría, 69 % en lugar de 72 %;
  - al decir «probablemente», 10 de 11 en lugar de 17 de 17;
  - el rango, ±23,4 en lugar de ±21,9.
