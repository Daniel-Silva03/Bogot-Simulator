# TECHO DE LOS GRUPOS EN EL BANCO AMPLIADO — resultados

Corrido el **5 de octubre de 2026** contra `TECHO_GRUPOS_LOTES_SPECIFICATION.md` (pre-registro en
`4ec8c8f`, código en `36ff93f`, arreglo DI-TL3 en el commit siguiente). Sin gasto.
`python src/experiments/techo_grupos_lotes.py` → `data/processed/banco/techo_grupos_lotes.json`.

## 1. Resultado

| | lote 1 (`TECHO_GRUPOS_RESULTS.md`) | **lotes 2 y 3** | lote 4 (no representativo) |
|---|---|---|---|
| preguntas / pares claros | 91 / 699 | **101 / 960** | 1 / 7 |
| oráculo, D = 1 | 0,992 | **0,994** | — |
| **oráculo, D = 2,03** | 0,952 | **0,960** | 0,901 |
| réplica por mitades | 0,856 | **0,863** (p5 0,830 – p95 0,891) | 0,553 (197 particiones con pares) |
| **tono general del simulador** | 0,62 | **0,466** (447 / 960) | 7 / 7 |

Por lote, el tono acierta 0,367 en el lote 2 (11 / 30) y 0,469 en el lote 3 (436 / 930). τ² con
D = 2,03: sexo 1,33; edad 2,95; estrato 10,01.

## 2. Contra el pre-registro

| | predicción | resultado | |
|---|---|---|---|
| P1 | oráculo D = 2,03 ≥ 0,90 | 0,960 | se cumple |
| P2 | réplica ≥ 0,85 | 0,863 | se cumple |
| P3 | tono entre 0,55 y 0,70 | 0,466 | **falla, por abajo: peor que el azar** |
| P4 | oráculo − tono ≥ 20 puntos | 49 puntos | se cumple |

**Lectura (§5): A, hay espacio**, igual que en el lote 1. **El tono acierta menos de 0,70**, así que
por la regla escrita la cifra de la página se mantiene, con la del banco ampliado al lado. Pero hay algo
que la regla no previó: el tono queda **por debajo del azar**. Eso se informa a Daniel antes de tocar la
página (§4).

## 3. Descriptivo, no pre-registrado

**Por qué falla el tono (análisis hecho después de ver el 0,466).** El tono mide quién suele responder
de forma *positiva* (DI-PP4). En el banco, «favorable» es estar de acuerdo con la pregunta tal como está
escrita (DI-BA3).
- En el lote 1, casi todas las preguntas eran positivas: confianza, satisfacción, imagen.
- En la Bienal, muchas son **afirmaciones negativas**: no querer de vecino a alguien, que más de la
  mitad sean corruptos, frases machistas, que sea justificable evadir impuestos. Ahí «de acuerdo» no es
  una respuesta positiva.

Al separar las familias de práctica del lote 3 por el sentido de su afirmación (lo hizo Claude, a
mano, por el texto, después de ver el resultado):

| familias | pares | acierto del tono | invertido |
|---|---|---|---|
| afirmaciones negativas (28, 38, 58, 59, 62, 69, 75, 77, 83) | 364 | **0,360** | 0,640 |
| afirmaciones positivas (las 17 restantes) | 566 | **0,539** | 0,461 |

- **En las negativas, el tono acierta al revés.** Invertido llega a 0,64, cerca del 0,62 del lote 1.
- **En las positivas apenas pasa el azar** (0,54).

## 4. Qué quiere decir

1. **El techo se repite con otra encuesta.** Las diferencias claras entre grupos son reales (~96 %) y
   el simulador está muy lejos. Hay espacio, y lo que falta es información.
2. **El «62 %» de la página no se generaliza.**
   - Fuera del lote 1, el tono solo funciona si se sabe hacia dónde apunta la pregunta, y aun así
     ronda el 54-64 %.
   - Para una pregunta de **aprobación de una medida** (positiva por construcción), lo comparable es
     la fila de las afirmaciones positivas: **0,54**.
3. **Decisión pendiente para Daniel:** qué hacer con el «tono por grupo» que la página muestra en las
   preguntas nuevas (D18). Las opciones van en el mensaje de la sesión: dejarlo con las dos cifras,
   como dice la regla; quitarlo; o mostrarlo solo cuando se sepa el sentido de la pregunta.

## 5. Límites

1. La partición por persona hace la réplica algo optimista (pre-registro §3).
2. La clasificación en positivas y negativas se hizo a mano y después de ver el resultado: es una
   explicación posible, no una prueba. Para confirmarla habría que pre-registrarla en el guardado.
3. El lote 4 es una sola pregunta de una muestra no representativa: sus cifras no pesan.
4. El arreglo DI-TL3 (particiones sin pares en el lote 4) se hizo al correr y no toca la cifra
   principal.
