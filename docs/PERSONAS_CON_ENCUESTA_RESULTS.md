# PERSONAS CON SU ENCUESTA — resultados

Corrido el **14 de octubre de 2026** contra `PERSONAS_CON_ENCUESTA_SPECIFICATION.md` (pre-registro y código en `a6ed132`,
antes de llamar al modelo).
- **Gasto:** USD 0,056 por 200 llamadas, con la de prueba incluida. Se esperaban unos USD 0,15.
- **Las respuestas del agente** están en `data/processed/personas_con_encuesta/`, sin subir.

## 1. Resultado

**Por pregunta**, porcentaje del lado favorable en el total de Bogotá:

| Pregunta | Real (EPC 2025) | Agente | Regresión | Página | Variación que conserva el agente |
|---|---|---|---|---|---|
| Confía en la Alcaldía | 19,1 | **25,7** | 21,4 | 31,6 | 84 % |
| Confía en el Concejo | 13,5 | **15,7** | 15,0 | 19,6 | 78 % |
| Confía en el Gobierno Nacional | 18,3 | **0,0** | 18,8 | 31,6 | 34 % |
| Buena gestión del Congreso | 11,8 | **0,0** | 14,6 | 24,8 | 60 % |
| Satisfecho con las vías | 22,4 | **4,6** | 26,5 | 35,6 | 45 % |
| Confía en los servicios financieros digitales | 36,0 | **39,4** | 38,5 | 50,9 | 37 % |

**En conjunto:**

| | Agente | Constante | Regresión (referencia) | Página |
|---|---|---|---|---|
| Error individual (por persona y pregunta) | **21,9** | 26,3 | 23,8 | — |
| Error del total de Bogotá | **10,0** | — | 2,3 | 12,2 |
| Variación que conserva | 56 % | — | — | — |

En 52 pares persona × pregunta, el agente no respondió con un código de la escala; quedan fuera.

| | Criterio | Resultado | |
|---|---|---|---|
| R1 | error individual menor que la constante | 21,9 contra 26,3 | se cumple |
| R2 | error del total menor que la página (12,2) | 10,0 | se cumple |
| R3 | conserva al menos el 60 % de la variación | 56 % | **no se cumple**, por poco |

**No pasa la regla.**

| | Predicción | Resultado | |
|---|---|---|---|
| PP1 | Le gana a la constante | 21,9 contra 26,3 | se cumple |
| PP2 | La regresión le gana al agente en error individual | el agente gana: 21,9 contra 23,8 | **falla** |
| PP3 | El agente aplana | conserva el 56 % | se cumple |
| PP4 | No pasa la regla | no pasa | se cumple |

## 2. Qué se aprende

1. **Es lo más cerca que hemos llegado.**
   - **A cada persona:** la acierta mejor que una constante, y mejor que una regresión entrenada con 1.320 personas (21,9
     contra 23,8). Con 40 respuestas reales, el modelo sí entiende algo de cada persona.
   - **En el total:** se equivoca menos que la página (10,0 contra 12,2).
   - **Frente a las pruebas anteriores:** MiroFish, TinyTroupe y el Experimento 8 perdían contra la constante.
2. **Pero cae en el estereotipo en la mitad de las preguntas.** En la confianza en el Gobierno Nacional y la gestión del
   Congreso, el agente dijo que **nadie** confía (0 %), cuando el real es 12 % a 18 %. En las vías, 4,6 % contra 22,4 %. A una
   persona descontenta con la ciudad la vuelve descontenta con todo. Es el aplanamiento de siempre, ahora hacia el extremo
   negativo: no hacia la mitad, sino hacia lo «coherente».
3. **Donde la pregunta se parece a su perfil, acierta muy bien:** la confianza en la Alcaldía (25,7 contra 19,1) y en el
   Concejo (15,7 contra 13,5), porque el perfil trae su opinión sobre Galán y el Concejo.
4. **La regresión es mucho mejor en el total** (2,3), pero solo existe porque esas 1.320 personas respondieron la pregunta.
   Para una pregunta de verdad nueva no habría con qué entrenarla. El agente sí funcionaría.

**En corto:** un agente armado con la encuesta real de la persona es la primera forma de «persona sintética que responde» que
le gana a la constante y a la página. Le falta no exagerar. Lo siguiente, si se sigue, sería otra prueba pre-registrada que
ataque eso, con preguntas de verdad nuevas antes de tocar la página.
