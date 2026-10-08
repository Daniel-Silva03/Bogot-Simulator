# PESO POR FECHA EN LA INTENCIÓN DE VOTO SIMULADA — resultados

Corrido el **8 de octubre de 2026** contra `VOTO_PESO_FECHA_SPECIFICATION.md` (pre-registro y código en `b55ffb3`, antes de
calcular). **Gasto: USD 0.** Las elecciones de Luna salieron de las cachés: 158 de práctica, 215 guardadas y 21 candidatos
de la Registraduría.

**Control (§2):** con τ = ∞ se reproduce el nivel 3: EAM de 3,74 y h de 7,1.

## 1. La τ elegida con la práctica

| τ (días) | 0 | 15 | 30 | 60 | 120 | 240 | 480 | ∞ |
|---|---|---|---|---|---|---|---|---|
| EAM en la práctica | 4,40 | 4,28 | 4,22 | 4,16 | 4,12 | 4,11 | 4,11 | 4,14 |

**La menor es 4,11, y ∞ queda a 0,03,** dentro del empate de 0,05 (§2). **τ\* = ∞:** el promedio simple de hoy.

## 2. Contra la regla

| | Criterio | Resultado | |
|---|---|---|---|
| R1 | τ\* no es ∞ | es ∞ | **no se cumple** |
| R2 | EAM ≥ 0,3 menor | igual (3,74) | **no se cumple** |
| R3 | adelante, al menos igual | 30 de 32, igual | se cumple |
| R4 | «probablemente», ≥ 90 % | 25 de 27 (93 %) | se cumple |

**Por la regla (§4), la página sigue con el promedio simple.**

**Registraduría (§5):** con τ\* = ∞ no cambia nada. EAM de 3,8, 5,5 y 3,4 en las tres elecciones, con el primero acertado
en las tres.

| | Predicción | Resultado | |
|---|---|---|---|
| PF1 | τ\* finita y ≤ 120 días | ∞ | **falla** |
| PF2 | cumple la regla | no | **falla** |
| PF3 | mejora más en 2026 | no hay mejora | **falla** |
| PF4 | baja el EAM en E3 | igual | **falla** |

## 3. Control no pre-registrado: las guardadas con cada τ

**Se calculó después de ver §1 y no decide nada.** Responde si la regla, al elegir con la práctica, dejó pasar una mejora
real.

| τ (días) | 0 | 15 | 30 | 60 | 120 | 240 | 480 | ∞ |
|---|---|---|---|---|---|---|---|---|
| EAM, las 215 | 4,08 | 4,04 | 4,01 | 4,01 | 4,03 | 4,04 | 4,00 | **3,74** |
| EAM, las de 2026 | 3,99 | 3,96 | 3,95 | 3,97 | 3,99 | 4,00 | 4,01 | 4,00 |
| Adelante, de 32 | 30 | 30 | 30 | 30 | 30 | 30 | 30 | 30 |

**No la dejó pasar.**
- **En las guardadas,** el promedio simple es lo mejor.
- **En 2026,** el peso por fecha da lo mismo.
- **En 2021-2022 empeora:** el peso casi descarta las elegidas de otros años, y esas ayudaban.

## 4. Qué se aprende

- **El ejemplo que motivó la prueba** (Cepeda contra De la Espriella, §1 del pre-registro) es un caso, no un patrón. En las
  32 segundas vueltas guardadas, darle más peso a lo reciente no acierta ninguna más.
- **Promediar varias encuestas sí ayuda:** reduce el ruido de cada una, y eso pesa más que la cercanía en el tiempo.
- **Queda lo que la página ya dice:** el «probablemente gana» se dice solo con más de 16 puntos de diferencia. En la
  guardadas acertó 25 de 27 veces.

## 5. Un arreglo de la salida, sin efecto en el resultado

En la primera corrida, la τ elegida y las medidas con esa τ se guardaban en el mismo campo, y la línea «τ\* =» salió con las
medidas. La regla y las predicciones usaron el valor correcto, que es una variable aparte. Se renombró el campo
(`tau_elegida`) y se volvió a correr: los resultados son los mismos.
