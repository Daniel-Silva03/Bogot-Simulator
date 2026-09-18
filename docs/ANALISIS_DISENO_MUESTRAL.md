# A19 — Estimación con diseño muestral complejo: qué se puede, qué no, y qué cambia

Proyecto: Bogotá Social Simulator
Versión: 1.1 — seis olas con diseño, no cuatro; y el proxy de conglomerado queda descartado con medición
Versión 1.0 — 17 de septiembre de 2026
Fecha: 18 de septiembre de 2026
Resuelve: A19 de `PROJECT_CONTEXT.md`
Código: `src/utils/diseno.py` (DI-D1..DI-D5) · `tests/test_diseno.py`, 12 pruebas

---

## 0. Las tres cosas que salieron

1. **En la ECP no se puede.** Los microdatos del DANE publican `FEX_P` y `REGION` y nada más — ni estrato de muestreo, ni UPM, ni pesos replicados, en ninguna de las cinco olas. Sin identificador de conglomerado no hay linealización posible. Es una limitación de la fuente, no del código.
2. **En la EPC sí, en seis olas**, y el efecto de diseño queda **medido sobre la variable del proyecto**: **DEFF entre 1,39 y 2,69, mediana 1,86** sobre 11 mediciones. Los errores estándar que el proyecto venía usando estaban subestimados por un factor de ~1,4.
3. **Y cambia una lectura sustantiva:** de las ocho transiciones de la serie de gestión del alcalde, **siete son distinguibles de cero y una no** — la de 2022→2023. Es exactamente la misma que el análisis de no respuesta había marcado como no establecida, por un camino completamente distinto.

---

## 1. La decisión: implementar aparte, no copiar la librería del CNC

A19 planteaba copiar `svy_prop` del CNC (con atribución) o implementar aparte. **Se implementó aparte (DI-D1)**, por tres razones en orden de peso:

1. **La librería del CNC estima proporciones; el proyecto necesita medias y diferencias de medias.** Es otra linealización, no un ajuste de la misma.
2. **La ECP no trae variables de diseño**, así que la librería no se le podría aplicar aunque se copiara — y la ECP es la serie principal de validación.
3. **Meter código interno del CNC en un repositorio que puede compartirse es una decisión de atribución** que no corresponde tomar por conveniencia técnica.

La librería del CNC sigue siendo la referencia si alguna vez hace falta una proporción con diseño.

## 2. Qué trae cada fuente

| Fuente | Peso | UPM | Estrato | ¿Diseño? |
|---|---|---|---|---|
| **ECP 2013·2017·2019·2021·2023** | `FEX_P` | — | — | **No** |
| EPC 2014 | `PON` | `MANZANA` | `GRUPO_ESTRATOS` | **Sí** |
| **EPC 2015** | `FEXP` | **`MANZANA`** | `D1_ORIGINAL` | **Sí** |
| **EPC 2018** | `PON` | **`MANZANA`** | `NSE` | **Sí** |
| EPC 2019 | `PONDERA` | `MANZANA` | `LOCALIDAD_COMUNA` | **Sí** |
| EPC 2023 | `FEXP` | `Manzana` | `CS0A` | **Sí** |
| EPC 2024 | `PONDERADOR` | `Manzana` | `Localidad` | **Sí** |
| EPC 2016·2017·2022·2025 | sí | — | — | **No** |

> **Corrección de la v1.1.** La v1.0 decía cuatro olas. Son **seis**: 2015 y 2018 también traen `MANZANA`, y no los revisé — el escaneo original cubrió una muestra de años, no todos. Lo señaló el equipo técnico de Bogotá Cómo Vamos al responder la consulta. Es, otra vez, una referencia externa encontrando lo que una revisión propia no encontró.

**Qué es realmente esa variable.** Tiene entre 41 y 54 valores distintos con unas 30 observaciones cada uno. Eso **no es una manzana**: una manzana real en una muestra de 1.500 daría cientos de grupos de 5 a 10 personas. Es más plausiblemente un segmento o sector de campo. Funciona igual como unidad de conglomerado para estimar varianza —que es lo que se necesita— pero conviene no llamarla por un nombre que no le corresponde.

**Por qué faltan cuatro años.** Según BCV, **la firma que levanta la encuesta cambia casi todos los años**, y el equipo técnico ha rotado. En algunos años el identificador quedó fuera de la base por negociación con la firma o simplemente no se agregó, y no hay documentación del diseño para reconstruirlo. Es una explicación de procedencia que vale registrar: no es descuido puntual, es una propiedad estructural de cómo se produce esta serie.

## 3. El efecto de diseño, medido

Linealización de Taylor sobre el estimador de razón, varianza acumulada entre UPM dentro de estrato (DI-D2):

| Ola | Ítem | Media | ee con diseño | ee SRS | **DEFF** |
|---|---|---|---|---|---|
| 2014 | gestión alcalde | 2,845 | 0,0503 | 0,0341 | **2,18** |
| 2014 | gestión Concejo | 2,635 | 0,0463 | 0,0302 | **2,35** |
| 2019 | gestión alcalde | 2,544 | 0,0382 | 0,0299 | **1,63** |
| 2019 | gestión Concejo | 2,670 | 0,0384 | 0,0269 | **2,04** |
| 2023 | gestión alcalde | 2,859 | 0,0440 | 0,0323 | **1,86** |
| 2023 | gestión Concejo | 2,534 | 0,0324 | 0,0269 | **1,46** |
| 2024 | gestión alcalde | 3,180 | 0,0521 | 0,0317 | **2,69** |
| 2024 | gestión Concejo | 2,645 | 0,0339 | 0,0288 | **1,39** |

**Mediana 1,95.** Coincide bien con el 2,5 que el CNC midió en otros estudios, pero ahora está medido **en esta encuesta y sobre esta variable**, que es lo que autoriza a usarlo.

Ninguna ola tuvo estratos con una sola UPM, así que el tratamiento de "lonely PSU" (DI-D3) no llegó a activarse.

## 4. Lo que cambia: siete de ocho transiciones, no ocho

Con el error de diseño donde se puede y el DEFF prestado donde no (marcado como prestado, DI-D1):

| Transición | Δ | ee | z | |
|---|---|---|---|---|
| 2014→2015 | −0,437 | 0,0647 | −6,75 | **significativa** |
| 2015→2017 | −0,304 | 0,0575 | −5,28 | **significativa** |
| 2017→2018 | +0,262 | 0,0587 | +4,47 | **significativa** |
| 2018→2019 | +0,177 | 0,0570 | +3,11 | **significativa** |
| 2019→2022 | +0,408 | 0,0600 | +6,81 | **significativa** |
| **2022→2023** | **−0,093** | **0,0639** | **−1,46** | **no distinguible de 0** |
| 2023→2024 | +0,321 | 0,0682 | +4,71 | **significativa** |
| 2024→2025 | −0,428 | 0,0677 | −6,32 | **significativa** |

*(Cifras de la v1.1, con seis olas de diseño real. El veredicto es idéntico al de la v1.0 y la única transición no distinguible se debilita todavía más, de z = −1,78 a −1,46.)*

> **Dos métodos independientes señalan la misma transición.** `claude/ANALISIS_NORESPUESTA_EPC.md` §3 concluyó que 2022→2023 no está establecida porque bastaría con que los excluidos promediaran 3,44 —perfectamente posible— para anularla. Aquí, por el lado del error muestral y sin tocar la no respuesta, sale a z = −1,78. **Es la única transición que ambos descartan, y ninguno descarta ninguna otra.**

Esa convergencia es lo que convierte a 2022→2023 de "sospechosa" en "no debe contarse como un movimiento". Los Experimentos 6 y 7 la incluyen entre los tramos a reproducir; no está mal hacerlo —el modelo tiene que pasar por ahí de todos modos— pero **ningún veredicto puede apoyarse en si un modelo acierta ese tramo**.

## 4.bis Por qué NO se usa un proxy para las olas que faltan

La salida natural para 2016, 2017, 2022 y 2025 es armar un conglomerado con lo que sí hay — `localidad × estrato`, por ejemplo. Es lo que propuso el propio equipo de BCV, y era también nuestra primera idea.

**Se validó donde se puede validar**: en las seis olas que sí traen manzana se calculó el DEFF de las dos maneras.

| Ola | DEFF con manzana | DEFF con el proxy | razón |
|---|---|---|---|
| 2014 | 2,79 | 5,60 | 2,01 |
| 2015 | 2,73 | 5,09 | 1,86 |
| 2018 | 1,37 | 3,42 | 2,50 |
| 2019 | 1,50 | 2,53 | 1,68 |
| 2023 | 0,93 | 2,95 | 3,16 |
| 2024 | 2,47 | 2,15 | 0,87 |
| | | **mediana** | **1,94** |

**El proxy infla el efecto de diseño por un factor cercano a dos, y de forma errática.** La razón es estructural y no de ajuste: `localidad × estrato` es mucho más plausiblemente la **estratificación** que la conglomeración, y tratar un estrato como conglomerado cuenta como variabilidad de muestreo lo que en realidad son diferencias sistemáticas entre estratos — justo lo que un diseño estratificado elimina.

Lo mismo ocurre con la hipótesis para 2025, `Zona + SEG_1`: da **DEFF 4,94**, casi el doble del techo observado en las olas con manzana. `Localidad + SEG_1` queda en 2,90, más cerca del rango, pero sin documentación no hay cómo confirmarlo.

**Conclusión: para las olas sin identificador se usa el DEFF prestado, no un proxy inventado.** Un factor prestado y marcado como tal es honesto; un proxy que duplica el error sin decirlo, no.

## 5. Una advertencia sobre 2022, y por qué no cambia nada

El DEFF medido de 2022 da **0,70**, por debajo de 1. Es posible —la posestratificación puede reducir varianza— pero aquí es sospechoso por dos razones: la UPM disponible es `BARRIO_ENC`, más gruesa que la manzana, y el ponderador de esa ola toma solo 10 valores distintos (`claude/ANALISIS_EPC_BCV.md` §1). Lo más probable es que subestime.

**Se probó la alternativa conservadora** —descartar el diseño de 2022 y usar el DEFF prestado de 1,95—, y **las ocho transiciones dan el mismo veredicto en las dos variantes**. El resultado no depende de esa decisión. Ambas variantes quedan en `data/processed/transiciones_epc_con_diseno.csv`.

## 6. Qué hay que hacer con esto

1. **Toda diferencia entre olas que el proyecto reporte lleva intervalo.** Es la regla que A19 existía para establecer, y ahora hay con qué cumplirla.
2. **Para la ECP, el error se infla por un DEFF prestado de 1,95 y se dice que es prestado.** `deff_prestado()` devuelve una estimación que lo deja escrito en sus notas y que **no** se declara "con diseño". Un intervalo así es una corrección aproximada, no una estimación con diseño, y confundirlas sería peor que no corregir.
3. **Pedir las variables de diseño.** A DANE, para la ECP; a Bogotá Cómo Vamos, la manzana de 2015-2018, 2022 y 2025. Es una petición barata y convertiría "prestado" en "medido" en toda la serie.
4. **Lo que NO hay que hacer:** recalcular hacia atrás los veredictos de los Experimentos 3 a 7. Esos comparan **distribuciones completas** con W1 contra una muestra de 200.000 de lo observado, no medias con intervalo; el error de muestreo de la fuente entra ahí por otra vía —el piso de ruido, que ya se calcula y ya se reporta— y no por el DEFF.

---

*Agregados ponderados sobre los microdatos entregados. Ningún registro individual sale de este análisis.*
