# ¿ESTIMAR CON EL TEXTO DE LA PERSONA O CON EL REFORMULADO? — resultados

Corrido el **6 de octubre de 2026** contra `TEXTO_PERSONA_SPECIFICATION.md` (pre-registro y código en `6ab4271`,
antes de llamar).
- **Comando:** `python src/experiments/texto_persona.py`.
- **Salida:** `data/processed/banco/texto_persona.json`.

**Gasto: USD 0,102 en 90 estimaciones** (la llamada de prueba incluida), dentro del tope de USD 0,40. Las 90 tienen
estimación en los dos brazos.

## 1. Resultado

| En las 90 | R: reformulada (la página hoy) | **T: texto de la persona + escala reformulada** | Regla |
|---|---|---|---|
| EAM | 16,7 | **15,6** | ≤ 16,7 − 1,0 = 15,7: **cumple**, por 0,1 |
| Acierto del lado | 63 % | **68 %** | ≥ 63 %: **cumple** |
| Decide (acierta) | 4 (3) | **5 (5)** | ≥ 90 %, con al menos 5 decisiones: **cumple** |
| Real dentro del rango | 74 % | 76 % | |
| …en las extremas | 50 % | 55 % | |
| …en las intermedias | 94 % | 92 % | |
| EAM en extremas / intermedias | 23,9 / 11,0 | **20,5** / 11,7 | |

**Pregunta por pregunta:** T se acerca más al real en 40 preguntas, R en 33, y en 17 quedan igual.

## 2. Contra el pre-registro

| | Predicción | Resultado | |
|---|---|---|---|
| PT1 | El EAM de T es menor que el de R | 15,6 < 16,7 | se cumple |
| PT2 | T cumple la regla | cumple las tres | se cumple |
| PT3 | T decide en más preguntas que R | 5 > 4 | se cumple |
| PT4 | La mejora está sobre todo en las extremas | extremas −3,4; intermedias +0,7 | se cumple |

**Por la regla (§3), se propone a Daniel que la página estime con el texto de la persona.** Para eso:
- `pagina.html` debe mandar al servidor el texto original junto con el reformulado;
- `servidor.py` debe pasarlo;
- `motor.py` debe estimar con él y la escala reformulada.

El texto de la página cambiaría a las cifras de T: 68 % del lado de la mayoría y 5 de 5 al decir «probablemente».

## 3. Lo que este resultado no dice

- **Pasa por muy poco:** 0,1 puntos por debajo del umbral de error. Con otra muestra de preguntas podría no pasar.
- **Es el mejor caso** (pre-registro §4). Aquí el «texto de la persona» es el de la encuesta, más limpio y más parecido a
  las candidatas que lo que escribe alguien en la página. Con preguntas escritas a mano, la ganancia será menor, y podría
  desaparecer.
- **En las intermedias, T es un poco peor** (11,7 contra 11,0). Toda la ganancia viene de las extremas, donde la
  reformulación cambiaba el sentido.
- **Ninguno de los dos brazos arregla del todo las extremas.** Por ejemplo, la marca Bogotá (real 71 %) sale en 31 % con T y
  en 47 % con R.
