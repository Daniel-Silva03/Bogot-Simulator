# EFECTO DE LA REDACCIÓN — resultados

Corrido el **14 de octubre de 2026** contra `REDACCION_SPECIFICATION.md` (pre-registro y código en `ae4f931`, antes de hacer
las redacciones). **Gasto: USD 0,075.** Las respuestas están en `data/processed/redaccion/`.

## 1. Resultado

**Catálogo:**

| # | Código | A | B | C |
|---|---|---|---|---|
| C1 orgullo | `AG2` | catálogo, 50,4 | catálogo, 50,4 | catálogo, 50,4 |
| C2 satisfacción | `CV1` | catálogo, 54,1 | catálogo, 54,1 | catálogo, 54,1 |
| C3 gestión de Galán | `GG3_GALAN` | catálogo, 33,9 | catálogo, 33,9 | catálogo, 33,9 |
| C4 seguridad en el barrio | `VS8` | **nueva**, 43,6 | catálogo, 43,6 | catálogo, 43,6 |

**Nuevas** (estimación, con la llamada):

| # | A | B | C | Amplitud |
|---|---|---|---|---|
| N1 el metro y la movilidad | 61,0 dividida | 61,0 dividida | 59,4 dividida | 1,6 |
| N2 confianza en el metro | 52,8 dividida | 54,8 dividida | 52,8 dividida | 2,0 |
| N3 imagen de Galán | 28,6 dividida | 24,3 **no** | 24,8 **no** | 4,3 |
| N4 Galán y la seguridad | 18,1 no | 19,7 no | 19,7 no | 1,6 |
| N5 diálogos de paz | 44,8 dividida | 45,5 dividida | 51,0 dividida | 6,2 |
| N6 relación con Estados Unidos | **fuera** | 36,8 dividida | **fuera** | — |

| | Criterio | Resultado | |
|---|---|---|---|
| R1 | ≥ 11 de 12 del catálogo a su código | 11 | se cumple |
| R2 | efecto de redacción ≤ 6,2 | **2,2 puntos** | se cumple |
| R3 | ninguna voltea de «sí» a «no» | ninguna | se cumple |

**La página es robusta a la redacción.**

| | Predicción | Resultado | |
|---|---|---|---|
| PR1 | El catálogo es estable | 11 de 12 | se cumple |
| PR2 | El efecto en las nuevas está entre 4 y 10 puntos | 2,2: menos | **falla** |
| PR3 | Nada se voltea | nada | se cumple |
| PR4 | Es robusta | lo es | se cumple |

## 2. Qué se aprende

1. **La cifra casi no depende de la redacción: 2,2 puntos.**
   - En el benchmark de Artificial Societies, el mejor modelo de lenguaje cambia 6,2 puntos y su sistema 1,4.
   - Estamos cerca de lo mejor que reportan. La razón: la cifra sale de respuestas reales, y redacciones parecidas llevan
     a Luna a elegir las mismas preguntas medidas.
2. **Donde sí cambia es en el alcance, no en la cifra.**
   - **«¿La gente se siente segura en su barrio?»** fue a pregunta nueva en vez de al catálogo. Igual dio 43,6, el mismo
     dato medido: la estimación eligió solo esa pregunta del catálogo (DI-CO39).
   - **La relación con Estados Unidos** salió «fuera de alcance» en dos de tres redacciones. La A es idéntica a la que en
     la validación del CNC, horas antes, salió «nueva». **Con temperatura 0, la reformulación no es del todo determinista**
     en una pregunta de borde: nacional, no de Bogotá.
3. **El compromiso sí puede cambiar:** la imagen de Galán salió «dividida» con una redacción y «probablemente no» con las
   otras dos. Está a unos 25-29 %, justo en el borde donde el rango deja de cruzar el 50 %.

**En corto:** cambiar las palabras no cambia la cifra. Lo frágil es decidir si una pregunta es de Bogotá o no, y en el
borde del rango, si dice «probablemente».
