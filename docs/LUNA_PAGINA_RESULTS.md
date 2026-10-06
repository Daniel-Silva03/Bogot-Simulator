# LA PÁGINA CON GPT-6 LUNA — la reformulación y el puente: resultados

Corrido el **6 de octubre de 2026** contra `LUNA_PAGINA_SPECIFICATION.md` (pre-registro y código en `1ade6a2`,
antes de llamar).
- **Comando:** `python src/experiments/luna_pagina.py`.
- **Salidas:** `data/processed/banco/luna_pagina.json` y `data/processed/puente_sin_base/luna/resultado.json`.

**Gasto: USD 0,283**, más USD 0,0009 de la llamada de prueba, dentro del tope de USD 0,75. Se reparte así:
- partes 1 y 2: 119 reformulaciones y 90 estimaciones, USD 0,214;
- puente: 126 llamadas, USD 0,069.

**Veredicto: las dos piezas pasan.** La reformulación y el puente pueden pasar a Luna.

## Parte 1 — la reformulación, con su validación

| | Criterio | Umbral | Luna | mimo (`REFORMULACION_RESULTS.md`) |
|---|---|---|---|---|
| R1 | Alcance esperado | ≥ 20 de 24 | **24 de 24** | 24 de 24 |
| R2 | Código esperado en las del catálogo | ≥ 6 de 8 | **8 de 8** | 8 de 8 |
| R3 | Fuera de alcance detectadas, ninguna como catálogo | ≥ 5 de 6, 0 | **6 de 6, 0** | 6 de 6, 0 |
| R4 | Respuesta válida | ≥ 23 de 24 | **24 de 24** | 24 de 24 |

**Cumple.**

## Parte 2 — la reformulación, por lo que le hace a la estimación

Sobre las 83 de las 95 guardadas que quedan como `nueva` y con estimación en los dos flujos. La estimación es con Luna
y h = 23,4.

| | Reformulación con Luna | Reformulación con mimo | Regla |
|---|---|---|---|
| EAM | 16,5 | 16,2 | ≤ 16,2 + 0,5: **cumple** |
| Acierto del lado | 64 % | 64 % | ≥ 64 % − 5: **cumple** |
| Decide (acierta) | 4 (3) | 6 (5) | |
| Real dentro del rango | 76 % | 77 % | |
| …en las extremas | 51 % | 54 % | |

**Lo que se reporta, sin regla:**
- **Alcances:**
  - con Luna: 90 `nueva` y 5 `catalogo`;
  - con mimo: 84 `nueva`, 6 `catalogo`, 4 `fuera` y 1 `invalida`.
- **La llamada coincide** en el 90 % de las preguntas.

**Lectura:**
- **Reformular con Luna no empeora la estimación, pero tampoco la arregla.**
- **Corrigió uno de los peores casos de mimo:** el de residuos, «da igual si se separan…», que mimo había invertido.
  Luna conserva el sentido («Separar los residuos… no tiene utilidad porque luego se mezclan») y la estimación baja de
  61 a 39 (real, 18).
- **Pero repite el otro defecto,** convertir una idea general en un juicio sobre Bogotá. Por ejemplo: «En Bogotá… la
  democracia contribuye al desarrollo económico de la ciudad» (49; real, 77).
- **La pérdida frente al texto original sigue ahí** (`NIVEL_ACUERDO_REDACCION_RESULTS.md`): no depende del modelo que
  reformula.

## Parte 3 — el puente, con su validación

| | Criterio | Umbral | Luna | mimo (`PUENTE_SIN_BASE_RESULTS.md`) |
|---|---|---|---|---|
| R1 | «Sin base» en las 12 escondidas | ≤ 1 | **0** | 0 |
| R2 | Ordena a las personas mejor que el azar y la demografía | ≥ 9 de 12 | **12 de 12** (ρ_ind de 0,21 a 0,65) | 12 de 12 (de 0,23 a 0,64) |
| P2 | «Sin base» en las 10 A | ≤ 1 | **0** | 0 |
| P1 | «Sin base» en las 10 C (se reporta) | | 5 de 10 | 5 de 10 |
| P3 | La fuerza distingue A de B | | A 10 de 10, B 10 de 10 | A 10 de 10, B 8 de 10 |

**Cumple.**
- Hubo una B que salió «sin base» por mayoría (B8). mimo no marcó ninguna.
- La página no usa «sin base», así que esto no la afecta.

## Contra el pre-registro

| | Predicción | Resultado | |
|---|---|---|---|
| PL1 | La reformulación con Luna cumple R1 a R4 | 24, 8, 6 y 0, 24 | se cumple |
| PL2 | No hace peor la estimación | 16,5 contra 16,2; 64 % y 64 % | se cumple |
| PL3 | El puente con Luna cumple R1, R2 y P2 | 0, 12 de 12 y 0 | se cumple |
| PL4 | Luna dice «sin base» en más C que mimo (más de 5) | 5 | **falla** |

**Por la regla (§5):**
- **la reformulación pasa a Luna:** cumple las partes 1 y 2;
- **el puente pasa a Luna:** cumple la parte 3.

Con eso, toda la página usa GPT-6 Luna.

**Costo de una pregunta nueva:**
- **hoy:** ~USD 0,009, con mimo para reformular y para el puente, y Luna para estimar;
- **todo con Luna:** ~USD 0,003, porque la reformulación y el puente cuestan ~USD 0,0009 cada uno.
