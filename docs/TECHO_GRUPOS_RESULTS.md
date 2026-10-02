# TECHO DE LOS GRUPOS — resultados

Corrido el **2 de octubre de 2026** contra `TECHO_GRUPOS_SPECIFICATION.md` (pre-registro en el
commit `31dd680`, código en `014c4ca`, antes de correr). Sin gasto en API.
`python src/experiments/techo_grupos.py` → `data/processed/banco/techo_grupos.json`.

## 1. Resultado

| | aciertos sobre los pares claros |
|---|---|
| azar | 0,503 |
| tono general (sin API) | 0,619 |
| mejor versión del puente | 0,627 |
| **réplica por mitades** (89 preguntas, ~513 pares por partición) | **0,856** (p5 0,813 – p95 0,889) |
| oráculo, D = 1 (91 preguntas, 699 pares) | 0,992 |
| **oráculo, D = 2,03** (cifra que decide) | **0,952** |

Varianza de las diferencias verdaderas entre grupos (τ², en unidades de z, D = 2,03): sexo 1,84,
edad 2,47, estrato 7,91. El estrato es lo que más separa.

## 2. Contra el pre-registro

| | predicción | resultado | |
|---|---|---|---|
| P1 | réplica entre 0,70 y 0,85 | 0,856 | **falla** (por arriba, por poco) |
| P2 | oráculo D = 1 ≥ 0,85 | 0,992 | se cumple |
| P3 | oráculo D = 2,03 entre 0,75 y 0,90 | 0,952 | **falla** (por arriba) |
| P4 | réplica < oráculo D = 2,03 | 0,856 < 0,952 | se cumple |

Las dos predicciones que fallan lo hacen en el mismo sentido: el techo es **más alto** de lo que
esperaba.

**Lectura (§5): A — hay espacio.** El oráculo con D = 2,03 da 0,952, muy por encima de 0,80. La
réplica no la contradice: aun dos encuestas de **mitad de tamaño** coinciden en el 86 % de las
diferencias claras.

## 3. Qué quiere decir

- Las diferencias claras entre grupos del banco **son reales casi todas**: no son ruido. Quien
  conociera la opinión de la población acertaría ~95 %; otra encuesta, aun más chica, ~86 %.
- El tono general y el puente aciertan ~62 %. **La distancia (23-33 puntos) no es ruido de la
  encuesta: es información que el simulador no tiene.** Que una pregunta nueva divida a los
  grupos de cierta forma depende de cosas de esa pregunta que no están en las respuestas que
  guarda la población.
- Por la regla ya escrita (`BANCO_PREGUNTAS_NUEVAS.md` §10.3), esto **no** reabre otra versión
  del puente para el orden de los grupos. Lo que este resultado justifica es buscar **datos**:
  casos reales parecidos con su resultado por grupo (camino 3) o, para el nivel, el camino 2.

## 4. Límites

1. **El oráculo depende de un supuesto:** diferencias verdaderas normales por dimensión. Con colas
   más pesadas, el techo sería aun más alto; con un DEFF mayor que 2,03, algo más bajo. Con
   D = 1 da 0,992, así que el rango razonable es 0,95-0,99.
2. **La réplica parte la ECP por hogar** (el archivo público no trae el segmento) y la EPC 2017 y
   2022 por persona: las mitades se parecen un poco más de lo que se parecerían dos encuestas
   distintas. Es la razón anunciada en el pre-registro para no usarla como cifra principal.
3. **Ambas miden contra la misma regla de pares claros** (z > 1,96 sin efecto de diseño) con que
   se midieron el puente y el tono, así que las cifras son comparables entre sí.
4. Solo las preguntas de práctica. Las 51 guardadas no se tocaron.

## 5. Incidencia al correr

La primera corrida se detuvo porque en el PC del CNC faltaba `EPC_2017_microdatos.dta` (y el de
2015, que esta prueba no usa). Daniel los copió desde el PC de casa y se corrió tal como se
pre-registró, sin enmienda. El oráculo, que no necesita microdato, ya había salido en la corrida
detenida, con la misma cifra.
