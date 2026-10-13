# PESO POR AÑO RECIENTE EN EL DATO MEDIDO — resultados

Corrido el **13 de octubre de 2026** contra `PESO_ANIO_RECIENTE_SPECIFICATION.md`:
- pre-registro en `a968d85` y código en `3c1c64f`, los dos subidos antes de correr;
- **gasto: USD 0**;
- cifras por pregunta en `data/processed/peso_anio_reciente/resultado.json`, sin subir.

## 1. Resultado

Se adivina la EPC 2025 con la población 2022-2024 en 35 preguntas. Las 35 tienen dos o más años, así que todas deciden.
El error es en puntos de una escala de 0 a 100.

| Regla | Error en la ciudad | Error por localidad | Gana a A en la ciudad |
|---|---|---|---|
| **A**, la de hoy | 4,43 | 7,94 | — |
| **B**, media vida de un año | 4,06 | 7,81 | 23 de 35 |
| **C**, solo el último año | 3,85 | 8,04 | 21 de 35 |

| | Criterio | Resultado | |
|---|---|---|---|
| R1 | B al menos 0,5 menor que A en la ciudad | 0,37 menor | **no se cumple** |
| R2 | B no sube más de 0,5 por localidad | baja 0,13 | se cumple |

**Por la regla (§3), la página sigue con A.**

| | Predicción | Resultado | |
|---|---|---|---|
| PA1 | B se equivoca menos que A en la ciudad | 4,06 contra 4,43 | se cumple |
| PA2 | C, menos que A en la ciudad y más por localidad | 3,85 y 8,04, contra 4,43 y 7,94 | se cumple |
| PA3 | B cumple la regla | no | **falla** |

## 2. Qué se aprende

1. **Pesar lo reciente ayuda, pero poco.** B mejora en 23 de 35 preguntas, y en promedio 0,37 puntos. Es menos de lo que
   se fijó para cambiar la página.
2. **Lo que falla no lo arregla ningún peso.** En cinco preguntas, 2025 se movió más que cualquier año anterior:

   | Pregunta | Error con A |
   |---|---|
   | Buen camino (`AG1`) | 14,8 |
   | Hambre (`AL1`) | 12,4 |
   | Victimización (`VS15`) | 10,7 |
   | Optimismo frente al metro (`MV150`) | 8,8 |
   | Seguridad en el barrio (`VS8`) | 7,5 |

   Ni con solo el último año baja de 9 puntos en `AG1`, `AL1` ni `VS15`. En las otras 30, el error con A es de 3,4.
3. **En el mapa, los años casi no importan.** Por localidad, las tres reglas quedan entre 7,8 y 8,0. El ruido de unas 80
   personas por localidad en 2025 pesa más que la regla.

**En corto:** el dato medido describe bien el año siguiente, con unos 4 puntos de error en la ciudad. Pero no anticipa un
cambio brusco: si la opinión se mueve, la página lo ve cuando entra la encuesta nueva.

**Lo que sigue según el pre-registro (§3):** la cifra de Galán se acompaña con lo que dijo cada año. Es un cambio en la
página, y espera el visto bueno de Daniel.
