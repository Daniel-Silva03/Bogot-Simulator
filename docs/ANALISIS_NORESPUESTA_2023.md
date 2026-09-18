# ¿El rebote de 2023 es opinión o es no-respuesta?

Proyecto: Bogotá Social Simulator
Versión: 1.0
Fecha: 16 de septiembre de 2026
Origen: advertencia abierta en `claude/DATA_INVENTORY.md` §10.3, elevada a prioridad por `claude/EXPERIMENT_4_RESULTS.md` §8
Datos: ECP DANE 2017 / 2019 / 2021 / 2023, Bogotá (`REGION = 1`), 18+, ponderada por `FEX_P`

---

## 1. La pregunta y la respuesta corta

La no-respuesta a la batería de confianza institucional es estable en 2017–2021 (1,8 % / 2,4 % / 1,8 % de personas sin índice válido) y **salta a 4,8 % en 2023**. Y 2023 es justo la ola donde pasan las dos cosas que sostienen todo el trabajo reciente: la media rebota (+0,185) y la dispersión se contrae (−14,8 %).

Si ese movimiento fuera composición y no opinión, el Experimento 4 estaría explicando un artefacto: la contracción de dispersión es *lo único* que el modelo consigue reproducir.

> **No lo es.** El rebote y la contracción sobreviven a todas las pruebas, incluida la más exigente —restringir a quienes contestaron los 13 ítems—, que reproduce ambos casi exactamente. La no-respuesta explica, como mucho, un 12 % del rebote y un 19 % de la contracción, y la corrección por composición mueve las dos cifras **en la dirección contraria** a la sospecha.

---

## 2. Cómo cambió la no-respuesta

| Año | n | Con índice (≥7 ítems) | Excluidos | 13 de 13 ítems | 1–6 ítems | **0 ítems** |
|---|---|---|---|---|---|---|
| 2017 | 5.137 | 5.046 | 1,8 % | 93,97 % | 0,55 % | 1,23 % |
| 2019 | 5.429 | 5.298 | 2,4 % | 91,97 % | 0,79 % | 1,62 % |
| 2021 | 4.945 | 4.858 | 1,8 % | 95,11 % | 0,47 % | 1,29 % |
| **2023** | **4.451** | **4.238** | **4,8 %** | **88,16 %** | **1,71 %** | **3,08 %** |

El salto es real y tiene dos partes: se duplica la gente que no contesta **nada** (1,3 % → 3,1 %) y se triplica la que contesta **algo pero poco** (0,5 % → 1,7 %).

**Y cambió de carácter, no solo de tamaño.** En 2017 y 2019 quien no contestaba nada era mayor que el promedio (57,1 y 52,6 años contra ~42,7 de los incluidos). En 2023 es **más joven** (40,1 contra 44,8) y de **estrato más bajo** (2,06 contra 2,70). Eso es un hallazgo sobre el trabajo de campo que vale la pena registrar por sí mismo, aunque, como se ve abajo, su magnitud no alcanza para mover los agregados.

---

## 3. La primera pista apunta al revés de lo temido

Quienes contestan entre 1 y 6 ítems —y por eso quedan fuera del índice— son **sistemáticamente más confiados** que los incluidos:

| Año | Índice de los incluidos | Índice parcial de los 1–6 ítems | Diferencia |
|---|---|---|---|
| 2017 | 2,503 | 2,857 | **+0,354** |
| 2019 | 2,362 | 2,722 | **+0,360** |
| 2021 | 2,245 | 2,348 | +0,103 |
| 2023 | 2,430 | 2,686 | **+0,256** |

La regla de exclusión (mínimo 7 ítems, DI-C6) está sacando gente **más confiada que el promedio**. O sea que sesga la media **hacia abajo**, no hacia arriba: trabaja **en contra** del rebote, no a su favor. Si la sospecha fuera correcta, el signo tendría que ser el opuesto.

---

## 4. Las cuatro pruebas

### (a) Relajar el mínimo a 1 ítem

Usa a los parciales en vez de descartarlos.

| Año | media | Δ | sd | Δ |
|---|---|---|---|---|
| 2017 | 2,505 | +0,002 | 0,936 | +0,002 |
| 2019 | 2,365 | +0,003 | 0,910 | +0,007 |
| 2021 | 2,245 | +0,001 | 0,900 | +0,002 |
| 2023 | 2,435 | **+0,005** | 0,769 | +0,005 |

El rebote **crece** ligeramente. Coherente con §3.

### (b) Peor caso: los que no contestaron nada, al mínimo de la escala

Se les asigna 1,0 —la desconfianza máxima posible— en todos los años, que es el supuesto más hostil que se puede hacer contra el rebote:

| | Publicado | Peor caso |
|---|---|---|
| Rebote 2021 → 2023 | **+0,1853** | **+0,1630** |
| Contracción de sd 2021 → 2023 | **−14,8 %** | **−12,0 %** |

Bajo el supuesto más extremo imaginable, sobrevive el **88 % del rebote** y el **81 % de la contracción**.

### (c) Solo casos completos — la prueba decisiva

Restringir a quienes contestaron **los 13 ítems** elimina de raíz cualquier efecto de no-respuesta por ítem: todo el mundo en la comparación respondió exactamente lo mismo.

| Año | n | media | sd | Δ media | Δ sd |
|---|---|---|---|---|---|
| 2017 | 4.827 | 2,485 | 0,937 | — | — |
| 2019 | 4.993 | 2,344 | 0,898 | −0,141 | −4,2 % |
| 2021 | 4.703 | 2,239 | 0,898 | −0,105 | 0,0 % |
| **2023** | **3.924** | **2,425** | **0,774** | **+0,186** | **−13,8 %** |

Contra lo publicado (+0,185 y −14,8 %): **prácticamente idéntico**. La V de la media y la contracción tardía de la dispersión están enteras dentro del subconjunto que no tiene ningún dato faltante.

Y de paso confirma el perfil que el modelo no reproduce: −4,2 % / 0,0 % / −13,8 %. La contracción **no empieza hasta 2023**.

### (d) Reponderar 2023 a la composición de 2021

Sexo × edad (4 tramos) × estrato (3 tramos), llevando 2023 a la estructura demográfica de 2021:

| | media | sd |
|---|---|---|
| 2023 tal cual | 2,430 | 0,764 |
| 2023 con composición de 2021 | **2,436** | **0,762** |

Corregir la composición **aumenta** el rebote y **profundiza** la contracción. Otra vez en la dirección contraria a la sospecha.

---

## 5. Qué queda cerrado y qué no

**Cerrado:** el rebote de la media y la contracción de la dispersión de 2023 son cambios en las respuestas, no artefactos de quién dejó de responder. El Experimento 4 no está ajustando ruido de no-respuesta. La advertencia de `DATA_INVENTORY.md` §10.3 —"antes de leer 2023 como recuperación hay que mirar quién se cayó"— queda atendida, y la respuesta es que mirarlo no cambia la lectura.

**Lo que esto NO descarta:** la no-respuesta que se puede medir es la de quien aceptó la encuesta y no contestó unos ítems. **La no-respuesta de unidad —quien nunca abrió la puerta— es invisible aquí**, y el tamaño de muestra sí cayó (5.137 → 4.451 entre 2017 y 2023). Si en 2023 dejó de contestar la encuesta entera un tipo de persona distinto, ningún análisis sobre los respondentes lo detecta. Corregirlo exigiría las tasas de respuesta y el marco muestral de DANE, que no están en el microdato.

Es una limitación real, pero de segundo orden frente a lo medido: la corrección por composición **sobre lo que sí se observa** empuja en contra de la sospecha en las cuatro pruebas, no a favor.

**Y un hallazgo lateral que conviene no perder:** el perfil de la no-respuesta se invirtió, de gente mayor a gente joven y de estrato bajo. No afecta a los agregados, pero si el CNC o DANE usan la ECP para desagregaciones por edad o estrato en 2023, ahí sí importa.

---

## 6. Consecuencia para el modelado

El objetivo del Experimento 4 queda confirmado como real:

- La **contracción tardía** (−4,2 % / 0,0 % / −13,8 % entre casos completos) es el fenómeno a reproducir, y es genuinamente tardía. La predicción Q3 fallaba contra un patrón verdadero, no contra un artefacto.
- Friedkin-Johnsen contrae de forma **anticipada y decelerante**, y la heterogeneidad de φ lo empeora. Queda descartada la salida fácil —"el perfil raro era ruido de medición"— y en pie la pregunta de qué mecanismo produce contracción que **no empieza** hasta el tercer periodo.
- Eso refuerza la prioridad de **cognición motivada** (A18): su término de reversión idiosincrática con probabilidad θ es, de los mecanismos disponibles, el único que en principio puede mantener la dispersión y después colapsarla.

---

*Análisis de amenazas a la validez, previo a seguir modelando. La conclusión es negativa —no encontró el artefacto que buscaba— y por eso mismo es la que permite seguir.*
