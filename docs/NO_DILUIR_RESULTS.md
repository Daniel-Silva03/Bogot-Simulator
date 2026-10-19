# QUE LOS AGENTES NO DILUYAN LA ENCUESTA — resultados

Corrido el **19 de octubre de 2026** contra `NO_DILUIR_SPECIFICATION.md` (pre-registro y código en `b267e93`, antes de llamar al
modelo). **Gasto: USD 0,193.**

## Parte 1. Desarrollo: la primera vuelta de 2026

Error medio absoluto (EAM) entre los candidatos, contra la Registraduría en Bogotá. Copiar la encuesta Invamer da 1,84.

| | EAM | Cepeda | De la Espriella | Valencia | López | Fajardo | Sin respuesta |
|---|---|---|---|---|---|---|---|
| C2, como antes | 3,49 | 38,8 | 22,8 | 16,0 | 8,0 | 7,2 | 2 |
| **C2i, con la instrucción** | **2,37** | 46,5 | 28,2 | 13,4 | 3,7 | 3,5 | 0 |
| C2k, calibrado | 1,84 | 46,4 | 32,8 | 14,6 | 2,3 | 2,5 | 2 |

**Por grupos** (contra el CNC de mayo; por D21, sin sus cifras): C2 6,6 y C2k 6,7. Ese resultado ya se había visto antes de subir
el pre-registro (§3 de la especificación); se repite igual con el ajuste repetido.

## Parte 2. Confirmación: la segunda vuelta en Bogotá

La parte de Cepeda entre los dos. **Lo real: 53,6.**

| | Cepeda | Error | ¿Gana Cepeda? |
|---|---|---|---|
| **S, sin la instrucción** | **50,2** | **3,4** | **sí** |
| Si, con la instrucción | 38,4 | 15,2 | no |
| Sk, calibrado a Guarumo | 46,1 | 7,5 | no |
| Copiar la encuesta nacional | 46,1 | 7,5 | no |
| Decir 50 % | 50,0 | 3,6 | empate |

## Reglas

| | Criterio | Resultado | |
|---|---|---|---|
| RN1 | C2i con EAM ≤ 2,99 | 2,37 | se cumple |
| RN2 | Si no peor que S en la segunda vuelta | 15,2 contra 3,4 | **no se cumple** |
| RK1 (no a ciegas) | C2k con menos error por grupos que C2 | 6,7 contra 6,6 | no se cumple |
| RK2 | Sk no peor que S en la segunda vuelta | 7,5 contra 3,4 | **no se cumple** |

**La instrucción no sirve y la calibración tampoco:** las dos mejoran la primera vuelta, que ya conocíamos, y empeoran la
segunda, que no.

## Predicciones

| | Predicción | Resultado | |
|---|---|---|---|
| PN1 | RN1 se cumple | 2,37 | se cumple |
| PN2 | RN2 no se cumple | 15,2 contra 3,4 | se cumple |
| PN3 | S le gana a copiar la encuesta nacional | 3,4 contra 7,5 | se cumple |
| PN4 | S acierta que Cepeda gana en Bogotá | 50,2 | se cumple |

Las cuatro se cumplen.

## Qué se aprende

1. **«Diluir» la encuesta no era solo un defecto.** Cuando la encuesta es de Bogotá, alejarse de ella empeora. Cuando es del país,
   alejarse de ella es justo lo que hace falta: los agentes bogotanos le dan a Cepeda 50,2, más que el país (46,1) y en la
   dirección de lo que votó Bogotá (53,6).
2. **Lo que más importa para D23:** sin instrucción, los agentes corrigen la encuesta nacional hacia Bogotá. Bajan el error de
   7,5 a 3,4 y aciertan que Cepeda gana en la ciudad. Es el primer caso en que los agentes le ganan a copiar la encuesta disponible.
3. **El límite:** S le gana a decir 50 % por muy poco (3,4 contra 3,6), y 50,2 es casi un empate. El ganador se acierta por un
   margen pequeño. Es una sola elección.
4. **La instrucción sobrecorrige:** con ella los agentes van más allá de la encuesta, hasta 38,4. «Inclínate por los candidatos que
   la encuesta pone adelante» los empuja hacia el puntero nacional, De la Espriella.
5. **La regla práctica que sale:** cuando hay encuesta de Bogotá, copiarla (o calibrar a ella) es lo mejor. Cuando solo hay
   encuesta nacional, los agentes sin instrucción aportan.
