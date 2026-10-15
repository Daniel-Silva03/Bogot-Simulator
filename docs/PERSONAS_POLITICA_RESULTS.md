# PERSONAS CON SU ENCUESTA, EN LO POLÍTICO — resultados

Corrido el **15 de octubre de 2026** contra `PERSONAS_POLITICA_SPECIFICATION.md` (pre-registro y código en `1aa07c6`, antes de
llamar al modelo).
- **Gasto:** USD 0,43, dentro del tope de USD 2.
- **Las respuestas** están en `data/processed/personas_politica/`, sin subir.

## 1. Resultado

**200 personas nuevas, 10 preguntas políticas escondidas:**

| Perfil | Error individual (constante 27,8) | Error del total (página 14,3) | TVD | Sin respuesta |
|---|---|---|---|---|
| A, opiniones | 27,4 | 7,8 | 0,161 | 8 |
| B, más su vida real | 27,4 | 7,7 | 0,158 | 0 |
| C, más un resumen de la IA | 27,3 | 7,8 | 0,160 | 0 |
| D, más una vida inventada | 27,4 | **7,4** | 0,164 | 0 |

**Por pregunta** (porcentaje del lado favorable; la EPC es pública):

| Pregunta | Real | A | B | D | Página |
|---|---|---|---|---|---|
| Gestión de Galán, buena o muy buena | 26,4 | 25,4 | **26,2** | 24,5 | 15,8 |
| Gestión del Concejo | 14,9 | **14,0** | **14,0** | **14,0** | 28,6 |
| Confía en la Alcaldía | 19,1 | 16,3 | 16,5 | 16,7 | 31,6 |
| La corrupción ha aumentado | 50,6 | 57,7 | 58,7 | **54,8** | 73,3 |
| El gobierno abre espacios de participación | 10,6 | 15,1 | 14,9 | 14,9 | 26,9 |
| Confía en el Gobierno Nacional | 18,3 | 10,2 | 10,6 | 10,5 | 33,5 |
| El gobierno responde a la ciudadanía | 6,9 | 16,3 | 16,1 | 16,6 | 21,1 |
| Transparencia del gobierno | 9,9 | 22,7 | 22,8 | 22,5 | 26,6 |
| Bogotá va por buen camino | 48,2 | 32,9 | 32,8 | 35,1 | 43,1 |
| Imagen favorable de Galán | 45,0 | 60,9 | 60,6 | 61,7 | 28,6 |

## 2. Contra el pre-registro

| | Hipótesis | Resultado | |
|---|---|---|---|
| H1 | B mejora a A (1 punto menos de error del total) | 7,7 contra 7,8 | **no se cumple** |
| H2 | C mejora a B | 7,8 contra 7,7 | no se cumple |
| H3 | D no mejora a A | 7,4 contra 7,8: menos de 1 punto | se cumple |

**Útil para preguntas políticas:** la de menor error del total es D. Cumple dos de las tres reglas:
- le gana a la constante por persona;
- le gana a la página en el total.

Su TVD es 0,164, y la regla pedía 0,15 o menos. **Por la regla, no es útil, aunque por poco.**

| | Predicción | Resultado | |
|---|---|---|---|
| PQ1 | La vida real ayuda | no cambia nada | **falla** |
| PQ2 | El resumen agrega poco | no agrega | se cumple |
| PQ3 | Inventar empeora | D queda igual o un poco mejor | **falla** |
| PQ4 | La mejor es útil | falla la TVD por 0,014 | **falla** |

## 3. Qué se aprende

1. **En lo político, el agente se equivoca casi la mitad que la página en el total** (7,4 a 7,8 contra 14,3). Lo logra sin
   ninguna opinión sobre el gobierno en el perfil, solo con lo que la persona dijo de su ciudad, sus servicios y la
   convivencia.
2. **En la gestión de Galán y del Concejo acierta casi exacto:** 26,2 contra 26,4, y 14,0 contra 14,9. La página, en cambio,
   da 15,8 y 28,6.
3. **Pero no en todo.**
   - **Exagera lo favorable** en la imagen de Galán (61 contra 45) y en la transparencia del gobierno (23 contra 10).
   - **Exagera lo desfavorable** en el rumbo de la ciudad (33 contra 48) y en la confianza en el Gobierno Nacional (10 contra
     18).

   Por eso la TVD queda justo encima del límite.
4. **Completar el perfil no cambia nada en lo político:** ni la vida real, ni el resumen, ni la vida inventada. Las cuatro
   variantes quedan a menos de medio punto. Lo que informa son sus opiniones; el colegio de sus hijos o los libros que lee
   dicen poco de lo que piensa de Galán.
5. **Inventar la vida no empeoró, contra lo que predije.** Tampoco ayudó de forma que cuente: 0,4 puntos, dentro del ruido. El
   modelo usa sobre todo las respuestas reales, y la biografía inventada no le agrega ni le quita.

**En corto:** para preguntas sobre el gobierno de la ciudad, el agente armado con la encuesta real de cada persona es la mejor
forma de estimar que ha probado el proyecto, con la mitad del error de la página. Falla por poco la regla de cómo reparte las
respuestas. Lo que no hace falta es completar el perfil: ni con datos reales de su vida ni con una vida inventada.
