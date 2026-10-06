# ¿ESTARÍA BOGOTÁ DE ACUERDO? — ¿mejora la estimación con las candidatas del lote 6?: resultados

Corrido el **6 de octubre de 2026** contra `NIVEL_ACUERDO_LOTE6_SPECIFICATION.md` (pre-registro y código en `7cc8bed`,
antes de calcular el guardado del lote 6 y antes de llamar).
- **Comando:** `python src/experiments/nivel_acuerdo_lote6.py`.
- **Gasto:** USD 0,210, con la llamada de prueba incluida, dentro del tope de USD 0,60.
- **Las 34 guardadas del lote 6** son utilizables.
- **No se sube ningún resultado de las encuestas del CNC:** aquí solo hay cifras de error y acierto (D21).

## 1. Resultado

| En las 129 | B: 109 candidatas (la página hoy) | **C: 139, con las 30 del lote 6** | Regla |
|---|---|---|---|
| Error (EAM) | 15,0 | **14,8** | C ≤ 15,8 y C ≤ B: **cumple** |
| Acierto del lado | 72 % | **71 %** | ≥ 67 % y ≥ 46 % + 10: **cumple** |
| Decide («probablemente») | 26 (20 %) | **11 (9 %)** | |
| Acierta al decidir | 24 de 26 (92 %) | **10 de 11 (91 %)** | ≥ 90 %: **cumple** |

| Por grupo | B | C |
|---|---|---|
| Las 34 del lote 6: EAM / lado / al decidir | 16,9 / 79 % / 14 de 15 | **14,1** / 82 % / 4 de 4 |
| Las 95 de siempre: EAM / lado / al decidir | 14,3 / 69 % / 10 de 11 | 15,0 / 66 % / 6 de 7 |

## 2. Contra el pre-registro

| | Predicción | Resultado | |
|---|---|---|---|
| P1 | C reemplaza a B (las tres condiciones) | se cumplen las tres | se cumple |
| P2 | En las del lote 6, C al menos 2 puntos mejor | 14,1 contra 16,9 | se cumple |
| P3 | En las 95, C a menos de 1 punto de B | 15,0 contra 14,3 (0,7) | se cumple |
| P4 | C decide en más preguntas que B | 11 contra 26 | **falla** |

**Por la regla (§4), C reemplaza a B.**

## 3. Lo que hay que tener en cuenta

1. **La mejora está toda en las preguntas políticas:** en las 34 del lote 6, el error baja 2,8 puntos. En las 95 de siempre,
   C es 0,7 peor. La regla mira las 129 juntas, y en conjunto gana C por 0,2.
2. **C dice «probablemente» la mitad de veces o menos:** 11 contra 26. Con 30 candidatas más, Luna elige más preguntas
   intermedias, y la estimación se queda más a menudo «dividida». La página informaría menos, aunque acierta igual
   cuando decide (91 %).
3. **Si C va a la página,** «En qué se apoya la estimación» podría mostrar porcentajes de Bogotá de las encuestas del CNC
   para Semana: opinión, no voto. D21 no lo prohíbe, pero es mostrar resultados de un cliente del CNC.
4. **El texto de la página cita las cifras de B con el texto de la persona** (68 %; 5 de 5; `TEXTO_PERSONA`). Para C no hay
   una medición con el texto de la persona. Si C va a la página, hay que citar estas, medidas con el texto de la encuesta
   (71 %; 10 de 11) y decirlo.
