# ¿ESTARÍA BOGOTÁ DE ACUERDO? — ¿mejora la estimación con las candidatas del lote 8?: resultados

Corrido el **14 de octubre de 2026** contra `NIVEL_ACUERDO_LOTE8_SPECIFICATION.md`:
- pre-registro y código en `cbeff07`, y guardado en `d795b21`, los dos antes de llamar;
- **comando:** `python src/experiments/nivel_acuerdo_lote8.py`;
- **gasto:** USD 0,220 con la llamada de prueba, dentro del tope de USD 0,60;
- **las 10 guardadas del lote 8** son utilizables.

Aquí van solo cifras de error y acierto en el total, porque el total incluye preguntas del CNC (D21). Las del lote 8 son
de la EPC, que es pública, y van pregunta por pregunta en §3.

## 1. Resultado

| En los 139 objetivos | C: 139 candidatas (la página hoy) | D: 154, con las 15 del lote 8 | Regla |
|---|---|---|---|
| Error (EAM) | 15,6 | 15,7 | D ≤ 15,8: cumple; **D ≤ C: no cumple** |
| Acierto del lado | 70 % | 70 % | ≥ 67 % y ≥ 49 % + 10: cumple |
| Decide («probablemente») | 11 (8 %) | 15 (11 %) | |
| Acierta al decidir | 10 de 11 (91 %) | 12 de 15 (80 %) | **≥ 90 %: no cumple** |

| Por grupo | C | D |
|---|---|---|
| Las 10 del lote 8: EAM / lado | 25,9 / 60 % | 27,9 / 30 % |
| Las 129 de siempre: EAM | 14,8 | 14,8 |

**Por la regla (§4), sigue C. La página no cambia.**

## 2. Contra el pre-registro

| | Predicción | Resultado | |
|---|---|---|---|
| P1 | D reemplaza a C | no cumple dos condiciones | **falla** |
| P2 | En las del lote 8, D al menos 2 puntos mejor | 27,9 contra 25,9: peor | **falla** |
| P3 | En las 129, D a menos de 1 punto de C | 14,8 y 14,8 | se cumple |
| P4 | D no decide en más preguntas que C | 15 contra 11 | **falla** |

## 3. Qué se aprende: la estimación no sabe que Bogotá desconfía

Las 10 preguntas escondidas de la EPC 2025, con la cifra real (porcentaje del lado favorable):

| Pregunta | Real | C | D |
|---|---|---|---|
| Confía en la Alcaldía | 19,1 | 53,2 | 44,4 |
| Confía en el Concejo | 13,4 | 53,2 | 53,2 |
| Confía en el Congreso | 9,8 | 53,2 | 53,2 |
| Confía en el Gobierno Nacional | 18,3 | 49,0 | 50,5 |
| Buena gestión del Congreso | 11,8 | 38,0 | 49,9 |
| Satisfecho con la justicia | 19,4 | 47,3 | 70,3 |
| Satisfecho con el estado de las vías | 22,4 | 39,9 | 31,5 |
| Confía en los servicios financieros digitales | 36,0 | 53,4 | 53,4 |
| Confía en la inteligencia artificial | 51,5 | 53,2 | 49,7 |
| Satisfecho con el servicio de salud | 49,9 | 30,1 | 70,3 |

1. **Cuando no encuentra nada parecido, la estimación se queda cerca de la mitad.** Seis de las diez reales están entre 10 %
   y 22 %: la desconfianza en las instituciones y en la justicia. Las dos configuraciones dieron entre 38 % y 53 %. El error
   de esas preguntas va de 26 a 44 puntos.
2. **Más preguntas parecidas no lo corrigieron, y a veces lo empeoraron.** Con el lote 8, la justicia y la salud se
   acercaron a las preguntas de satisfacción con el colegio, que son altas, y subieron a 70 %. Solo la Alcaldía y las vías
   mejoraron.
3. **En las 129 de siempre no cambia nada** (14,8 y 14,8). Como con el lote 6, más candidatas no ayudan fuera de su tema.

**El defecto que muestra:** la estimación necesita una pregunta medida casi igual para alejarse del 50 %. Para las preguntas
de confianza en instituciones, que son las que más le preguntaría un jefe o un cliente, se equivoca por 30 a 40 puntos.
Ampliar el banco no lo arregla. Haría falta otra forma de estimar, con su propio pre-registro.
