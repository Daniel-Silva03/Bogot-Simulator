# AGENTES CON SU ENCUESTA EN PREGUNTAS DE 2026 — resultados

Corrido el **16 de octubre de 2026** contra `AGENTES_2026_SPECIFICATION.md`:
- pre-registro y código en `aab4671`; enmienda 1 en `1e0989b`, antes de ver ningún resultado;
- cerrado con lo que había (enmienda 1): Luna con 200 personas, DeepSeek con 150;
- **gasto:** USD 0,85, dentro del tope de USD 1. DeepSeek costó nueve veces lo previsto;
- **las 7 del CNC** se reportan solo como error medio y lados acertados (D21).

## 1. Resultado

| | Error en las 13 | Sin V5 | Las 6 públicas | Las 7 del CNC | Lado acertado (de 13) | En las del CNC (de 7) |
|---|---|---|---|---|---|---|
| **L, Luna** | **15,2** | **15,5** | 22,5 | **9,0** | 9 | 6 |
| S, DeepSeek (150 personas) | 18,4 | 17,6 | 26,2 | 11,6 | 7 | 4 |
| M, los dos promediados | 16,1 | 15,8 | 23,9 | 9,4 | 8 | 5 |
| Página | 14,6 | 15,7 | **16,8** | 12,7 | **10** | 4 |
| Decir 50 % | 18,1 | 19,1 | 26,8 | 10,6 | 6 | 5 |

**Las 6 públicas, pregunta por pregunta:**

| Pregunta | Real | Luna | Los dos | Página |
|---|---|---|---|---|
| El metro mejorará la movilidad | 93 | **75,9** | 72,0 | 62,2 |
| Usaría el metro como transporte principal | 70 | 48,4 | 48,0 | **59,5** |
| Confía en el proyecto del metro | 80 | 48,2 | 47,4 | **56,0** |
| El metro es motivo de orgullo | 88 | 56,5 | 57,6 | 56,4 |
| El metro funcionará en 2028 | 56 | 43,8 | 37,3 | **54,8** (estaba en su banco) |
| Imagen favorable de Galán | 26 | 46,6 | 44,7 | **28,6** |

| | Criterio | Resultado | |
|---|---|---|---|
| R1 | el mejor (L) se equivoca menos que la página en las 13 y sin V5 | 15,2 contra 14,6; sin V5, 15,5 contra 15,7 | **no se cumple** |
| R2 | acierta el lado en al menos tantas como la página | 9 contra 10 | **no se cumple** |
| Hipótesis | M mejora a L en 1 punto | 16,1 contra 15,2: peor | no se cumple |

**Los agentes no le ganan a la página en preguntas nuevas.**

| | Predicción | Resultado | |
|---|---|---|---|
| PA1 | L le gana a la página en las 13 | 15,2 contra 14,6 | **falla** |
| PA2 | M mejora a L | empeora | **falla** |
| PA3 | En el metro, los agentes quedan más cerca que la página | solo en una de cuatro | **falla** |
| PA4 | En las del CNC, los agentes no le ganan a decir 50 % | Luna 9,0 contra 10,6: le gana | **falla** |

## 2. Qué se aprende

1. **En las preguntas del CNC, los agentes ganan.** Luna se equivoca 9,0, frente a 12,7 de la página y 10,6 de decir 50 %, y
   acierta el lado en 6 de 7 (la página, en 4). Son temas nacionales de 2026: petróleo, paz, salud, Estados Unidos. Es la
   primera vez que algo le gana a decir 50 % en estas siete.
2. **En las públicas pierden.** En el metro, la página quedó más cerca en tres de cuatro, aunque las dos se quedan cortas. El
   estudio del Metro se hizo en las 9 localidades de la línea 1, entre residentes y comerciantes. La EPC es toda Bogotá, y ahí el
   entusiasmo por el metro es menor.
3. **La imagen de Galán revela un problema de la vara, no solo de los agentes.**
   - **Los agentes dan 47 %,** y la cifra «real» de 26 % es de la Encuesta Distrital de Planeación.
   - **La EPC 2025, de donde salen los agentes, midió 45 %** (`PERSONAS_POLITICA_RESULTS.md`).
   - Los agentes reproducen la EPC: la diferencia es entre las dos encuestas. Contra la EPC, el error de los agentes aquí sería de
     1,6 y no de 20,6. **No se cambia la vara después de ver el resultado;** se anota.
4. **Promediar con DeepSeek empeora.** DeepSeek se equivoca más que Luna (18,4) y es nueve veces más caro. La idea de varios
   modelos no ayuda con este segundo modelo.

**En corto:** en preguntas de verdad nuevas, los agentes empatan con la página. Ganan en las de opinión política nacional, pierden
en las del metro, y en la imagen de Galán chocan con una diferencia entre encuestas. No alcanza para reemplazar a la página.
