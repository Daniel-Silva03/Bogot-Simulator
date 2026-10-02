# NIVEL POR PREGUNTAS PARECIDAS — resultados de la parte A (sin API)

Corrido el **2 de octubre de 2026** contra `NIVEL_PARECIDAS_SPECIFICATION.md` (pre-registro en
`0cf74d7`, código en `02035ff`, antes de correr). Sin gasto.
`python src/experiments/nivel_parecidas.py` → `data/processed/banco/nivel_parecidas.json`.

## 1. Resultado

96 preguntas de práctica, 29 familias. Error absoluto medio (EAM) del porcentaje favorable de la
ciudad, en puntos, siempre sin la familia de la pregunta:

| | EAM | error ≤ 10 puntos |
|---|---|---|
| R0 — promedio | 23,0 | 23 % |
| R1 — mismo tema | 23,4 | 21 % |
| **R2 — vecinos por texto (k = 5)** | **22,0** | 25 % |

Secundarias: R2 con k = 3, 23,3; con k = 10, 22,6; **R2 dejando entrar a las hermanas de la misma
familia, 16,1**.

## 2. Contra el pre-registro

| | predicción | resultado | |
|---|---|---|---|
| P1 | EAM de R0 entre 12 y 20 | 23,0 | **falla** (por arriba) |
| P2 | R1 < R0 | 23,4 > 23,0 | **falla** |
| P3 | R2 no baja R0 un 20 % | 22,0 (−4 %) | se cumple |
| P4 | R2 con hermanas < R2 sin ellas | 16,1 < 22,0 | se cumple |

**Regla (§6):**
- Ningún método gratuito baja el EAM del promedio un 20 %: **buscar preguntas parecidas sin el
  modelo no acerca el nivel**.
- **La vara de la parte B es 22,0 puntos (R2).** Para pasar, la parte B tendrá que llegar a
  **17,6 o menos** en la práctica, y después repetirlo en el banco guardado.

## 3. Qué quiere decir

- **Los niveles del banco son muy distintos entre sí:** van del 4 % al 96 % favorable (media 36,
  desviación 26). Suponer el promedio se equivoca en 23 puntos.
- **Ni el tema ni el parecido del texto ayudan** cuando la pregunta no tiene hermanas en el banco.
  Lo que sí ayuda es tener **preguntas de la misma serie** (16,1 puntos): una pregunta nueva se
  puede acercar si hay una casi igual medida, no si solo hay una del mismo tema.
- **Para la parte B la vara es baja en términos absolutos** (22 puntos), pero el Experimento 9 y
  el nivel de 3,7 del puente dicen que el modelo no es bueno con cifras. Lo que se probaría no es
  que el modelo ponga el número, sino que **elija mejor cuáles preguntas son parecidas** y que el
  número salga de sus resultados reales.

## 4. Descriptivo, no pre-registrado

- **Por ámbito:** en las 32 preguntas sobre Bogotá, R0 16,1 y R2 16,4; en las 64 generales, R0
  26,5 y R2 24,8.
- **Metro y Corredor Verde:**
  - Corredor Verde: real 58,8 %. R2 da 56,2, porque uno de sus 5 vecinos es el metro. R0 da 36,0.
  - Metro elevado: real 65,7 %. R2 da 31,2 y R0 36,0.
- **Los peores casos** son preguntas generales de la ECP con niveles muy altos (77-96 %), que R2
  predice en 12-37 %.

## 5. Límites

1. El porcentaje favorable depende de cuántas categorías cuentan como favorables en cada
   pregunta (DI-BA3), así que preguntas de escalas distintas no son del todo comparables.
2. 29 familias es poco: dejar fuera una familia grande (12 preguntas) cambia bastante el pozo.
3. Solo práctica. Las 51 guardadas no se tocaron.
