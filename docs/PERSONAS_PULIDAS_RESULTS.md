# PERSONAS CON SU ENCUESTA, PULIDAS — resultados

Corrido el **14 y 15 de octubre de 2026** contra `PERSONAS_PULIDAS_SPECIFICATION.md` (pre-registro y código en `42c8154`,
antes de llamar al modelo). **Gasto: USD 0,80**, dentro del tope de USD 2.

**Dos cortes ajenos al código:**
- **la caída del internet** en medio de V4 del desarrollo;
- **la falta de memoria del computador** durante la prueba final, que detuvo el proceso.

Las dos veces se retomó desde la caché, sin volver a pagar ni cambiar nada.

## 1. Desarrollo: las 200 personas de antes y 12 preguntas

| Variante | Error individual (constante) | Error del total (página: 12,1) | TVD | Sin respuesta |
|---|---|---|---|---|
| V0, una opción | 23,2 (28,4) | 20,8 | 0,425 | 57 |
| V1, una opción con la instrucción | 23,2 (28,4) | 19,8 | 0,423 | 46 |
| **V2, probabilidades** | 25,4 (28,3) | **9,5** | **0,174** | 8 |
| V3, probabilidades con la instrucción | 25,6 (28,3) | 10,3 | 0,186 | 50 |
| V4, probabilidades, instrucción y ancla | 26,0 (28,4) | 9,4 | 0,185 | 32 |

**Elegida: V2.** Todas le ganan a la constante. V4 y V2 empatan en error del total (9,4 y 9,5, a menos de 0,5), y gana la de
menor TVD.

## 2. Prueba final: 200 personas nuevas y 8 preguntas que no se usaron

| | V2 (la elegida) | Referencia | Condición | |
|---|---|---|---|---|
| Error individual | 27,5 | constante 26,0 | R1: menor | **no se cumple** |
| Error del total | 15,3 | página 15,0 | R2: menor | **no se cumple**, por 0,3 |
| TVD | 0,224 | — | R3: ≤ 0,15 | **no se cumple** |

**La variante elegida no pasa la prueba final.**

**Por pregunta** (porcentaje del lado favorable; la EPC es pública):

| Pregunta | Real | V2 | V0 | Página |
|---|---|---|---|---|
| Confía en el Congreso | 9,8 | **7,0** | 0,0 | 29,4 |
| Satisfecho con la justicia | 19,4 | **18,9** | sin cifra | 16,7 |
| Satisfecho con el servicio de salud | 49,9 | **48,9** | 70,2 | 70,9 |
| La IA le dificultará conseguir trabajo | 29,1 | **25,4** | 2,0 | 41,7 |
| Confía en la inteligencia artificial | 51,6 | 28,2 | 0,0 | 47,5 |
| Probable sanción por dañar el espacio público | 40,6 | 11,3 | 0,0 | 13,4 |
| Satisfecho con los profesores del colegio | 78,0 | 46,6 | 0,0 | 63,5 |
| Satisfecho con los procesos académicos del colegio | 75,4 | 44,5 | 0,0 | 57,1 |

**Secundario, sin peso** (las 6 preguntas del desarrollo, en las personas nuevas):

| | Error individual (constante) | Error del total (página: 8,1) | TVD |
|---|---|---|---|
| V2 | 22,5 (25,7) | **4,2** | 0,167 |
| V0 | 20,7 (25,9) | 9,2 | 0,394 |

**Un defecto del código, en lo secundario:** en V0 de la prueba final, el total y la TVD salen sin cifra. En la justicia, ninguna
de las respuestas de V0 fue un código válido, probablemente porque eligió «no aplica» para todos, y el promedio de las 8 quedó
vacío. No afecta la regla, que mira V2.

## 3. Contra el pre-registro

| | Predicción | Resultado | |
|---|---|---|---|
| PP1 | En el desarrollo, las de probabilidades tienen menos error del total | 9,4 a 10,3 contra 19,8 a 20,8 | se cumple |
| PP2 | Gana V4 | gana V2, por el desempate | **falla** |
| PP3 | La instrucción sola mejora menos de 2 puntos | 1,0 | se cumple |
| PP4 | La elegida pasa la prueba final | no pasa | **falla** |

## 4. Qué se aprende

1. **Pedir probabilidades corrige el «nadie confía».** Al elegir una sola opción por persona desaparecía la minoría: V0 da
   0 % en seis de las ocho preguntas finales. Con probabilidades, el total se acerca, y en las 6 del desarrollo lo hace con
   personas nuevas (4,2 contra 8,1 de la página).
2. **Pero tiene un sesgo pesimista que no se ve en el desarrollo.** En la prueba final acierta muy bien en cuatro preguntas
   (Congreso, justicia, salud, IA y trabajo: errores de 0,5 a 3,7 puntos). En las otras cuatro queda 23 a 31 puntos por debajo
   de lo real: la confianza en la IA, la sanción por dañar el espacio público y la satisfacción con el colegio. **Supone que la
   gente está menos satisfecha de lo que está.**
3. **Las preguntas donde falla tienen algo en común:**
   - **en dos, el lado favorable es el de una minoría satisfecha:** la del colegio solo la responden quienes tienen hijos en
     él, y la de la IA solo quienes la usan;
   - **la tercera,** la sanción por dañar el espacio público, depende de una creencia sobre las autoridades que nada del perfil
     anticipa.

   El perfil trae sobre todo opiniones sobre la ciudad, que en Bogotá son críticas, y el agente las extiende a todo.
4. **La instrucción contra la exageración no lo arregló,** ni en el desarrollo ni en la V3. Decirle que no extrapole no basta.

**En corto:** la idea funciona a medias. En lo que el perfil «habla» (instituciones y servicios de la ciudad) el agente acierta
muy bien, mejor que la página. En lo que el perfil no toca, contagia el pesimismo de la ciudad y se equivoca por 25 a 30 puntos.
Por la regla, no pasa, y la página no cambia.
