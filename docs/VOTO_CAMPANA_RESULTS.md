# INTENCIÓN DE VOTO CON AGENTES QUE CONOCEN LA CAMPAÑA — resultados

Corrido el **16 de octubre de 2026** contra `VOTO_CAMPANA_SPECIFICATION.md` (pre-registro y código en `60704c4`, antes de
llamar al modelo). **Gasto: USD 0,144.**

## 1. Resultado

**Los mismos 200 agentes, normalizado entre los 11 candidatos, contra la Registraduría en Bogotá:**

| Candidato | Real | A, sin contexto | C1, con el resumen | **C2, con el resumen y la encuesta** | Copiar la encuesta |
|---|---|---|---|---|---|
| Iván Cepeda | 42,4 | 21,8 | 24,1 | **38,8** | 46,4 |
| Abelardo de la Espriella | 38,4 | 14,3 | 16,0 | **22,8** | 32,8 |
| Paloma Valencia | 9,3 | 13,6 | 18,1 | **16,0** | 14,6 |
| Sergio Fajardo | 6,4 | 18,0 | 15,3 | **7,2** | 2,5 |
| Claudia López | 2,5 | 15,6 | 16,9 | **8,0** | 2,3 |
| **Error medio (EAM)** | | 8,14 | 7,40 | **3,49** | 1,84 |
| Primero y segundo correctos | | solo el primero | solo el primero | **los dos** | los dos |

| | Criterio, en C2 | Resultado | |
|---|---|---|---|
| R1 | EAM ≤ 5,4 | 3,49 | se cumple |
| R2 | Cepeda primero | sí | se cumple |
| R3 | Cepeda y De la Espriella, primero y segundo | sí | se cumple |

**Con la campaña y la encuesta, los agentes sirven para la intención de voto, por la regla.** Su error (3,49) es casi el de la
estimación de voto de hoy (3,4).

| | Hipótesis | Resultado | |
|---|---|---|---|
| H1 | C1 mejora a A en 1 punto | 7,40 contra 8,14: 0,7 | no se cumple |
| H2 | C2 mejora a C1 en 1 punto | 3,49 contra 7,40 | se cumple |
| H3 | C2 le gana a copiar la encuesta | 3,49 contra 1,84 | no se cumple |

| | Predicción | Resultado | |
|---|---|---|---|
| PC1 | El resumen solo mejora en 1 punto | 0,7 | **falla** |
| PC2 | La encuesta acerca más | sí | se cumple |
| PC3 | C2 cumple la regla | sí | se cumple |
| PC4 | C2 no le gana a la encuesta | no le gana | se cumple |

## 2. Qué se aprende

1. **Lo que acerca a los agentes es la encuesta, no saber quién es de izquierda o de derecha.** El resumen solo baja el error de
   8,1 a 7,4. Con la encuesta baja a 3,5, y el primero y el segundo quedan en su lugar.
2. **Pero los agentes no le ganan a la encuesta: la diluyen hacia el centro.**
   - **Lo que hacen:** a De la Espriella le quitan 10 puntos (22,8 contra 32,8 de la encuesta y 38,4 real), y a Fajardo y López
     les suben 5.
   - **Por qué:** los agentes son bogotanos con opiniones de ciudad. Esas opiniones los llevan hacia el centro, y Bogotá votó
     más a la derecha de lo que eso sugiere.
   - **En esta elección,** la encuesta nacional sola (1,84) estuvo más cerca de Bogotá que los agentes.
3. **Para qué servirían, entonces:** no para la cifra de Bogotá, que la encuesta ya da mejor, sino para repartirla por grupos:
   - por estrato, edad y sexo, que la encuesta publicada no trae para Bogotá;
   - o para escenarios que no tienen encuesta.

   Eso no se midió aquí, y sería la siguiente prueba.

**En corto:** los agentes, actualizados con la última encuesta, llegan casi al mismo error que la estimación de voto de hoy, y
aciertan el orden de los dos primeros. No le agregan precisión a la encuesta en el total. Su valor posible está en lo que la
encuesta no trae.
