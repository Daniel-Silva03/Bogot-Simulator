# VALIDACIÓN 2026 — resultados

Corrido el **14 de octubre de 2026** contra `VALIDACION_2026_SPECIFICATION.md` (pre-registro y código en `651134b`, antes de
hacer las preguntas).
- **Gasto:** USD 0,023.
- **Respuestas** en `data/processed/validacion_2026/`, sin subir.

## 1. Resultado

| # | Pregunta | Real | Página | Rango | Llamada | ¿Dentro? |
|---|---|---|---|---|---|---|
| V1 | ¿Cree que el metro mejorará la movilidad en Bogotá? | 93 | 62,2 | 40,5 – 83,9 | dividida | no |
| V2 | ¿Usaría el metro como su principal medio de transporte? | 70 | 59,5 | 37,8 – 81,2 | dividida | sí |
| V3 | ¿Confía en el proyecto del metro de Bogotá? | 80 | 56,0 | 34,3 – 77,7 | dividida | no |
| V4 | ¿El metro es un motivo de orgullo para Bogotá? | 88 | 56,4 | 34,7 – 78,1 | dividida | no |
| V5 | ¿Cree que el metro empezará a funcionar en 2028? | 56 | 54,8 | 31,9 – 77,7 | dividida | sí |
| V6 | ¿Tiene una imagen favorable del alcalde Galán? | 26 | 28,6 | 5,7 – 51,5 | dividida | sí |

Las seis fueron preguntas nuevas.

| | Criterio | Resultado | |
|---|---|---|---|
| R1 | dentro del rango en ≥ 4 de 6 | 3 | **no se cumple** |
| R2 | al decidir, falla en 1 como máximo | no decidió en ninguna | se cumple |
| R3 | error medio menor que decir 50 % (26,8) | 16,8 | se cumple |

**La página no pasa la validación 2026.**

| | Predicción | Resultado | |
|---|---|---|---|
| PV1 | Pasa | no pasa | **falla** |
| PV2 | En las del metro da menos que el real | menos en las cuatro, entre 10 y 32 puntos | se cumple |
| PV3 | La imagen de Galán no sale «probablemente sí» | dividida, 28,6 % | se cumple |
| PV4 | Ninguna va a «fuera» | ninguna | se cumple |

**Comparación aparte (§5):** «¿Aprueba la gestión del alcalde Galán?» fue al dato medido, 33,9 % de «buena o muy buena».
Guarumo midió 53,3 % que aprueba en abril de 2026. Como se dijo, son preguntas y muestras distintas.

## 2. Corrección: V5 sí estaba en el banco

**Lo que decía el pre-registro era falso.** Decía que V5 y V6 no estaban entre las 38 afirmaciones de la Encuesta Distrital
que hay en el banco (lote 5). **V5 sí está:** «Siento confianza en que la Primera Línea del Metro iniciará operación en
2028». La estimación se apoyó justo en ella, y por eso dio 54,8 contra 56. No lo revisé pregunta por pregunta antes de
escribirlo.

- **V5 no es una prueba:** la página encontró la misma pregunta medida.
- **Sin V5** (control no pre-registrado): dentro del rango en 2 de 5, y error medio de 19,9 contra 31,0 de decir 50 %.
- **V6 sí es limpia:** se apoyó en la gestión de Galán (33,9 %) y la imagen del Concejo (23,4 %), y dio 28,6 contra 26.

Lo de arriba no se borra (§45).

## 3. Qué se aprende

1. **Nunca se atrevió a decidir:** las seis salieron «dividida». Con un rango de unos ±22 puntos, la estimación tiene que
   quedar por debajo de 28 % o por encima de 72 % para decir «probablemente». Ninguna llegó.
2. **El defecto de siempre, ahora del otro lado:** cuando lo real es extremo, la estimación queda cerca del medio. En el
   metro, con reales de 80 % a 93 %, dio de 56 % a 62 %. Se apoyó en el optimismo frente al metro de la EPC y en las
   afirmaciones de la Encuesta Distrital, que son más bajas que el entusiasmo que midió el estudio del Metro.
3. **Parte de la diferencia es del estudio, no de la página:** se hizo en las 9 localidades de la línea 1, entre residentes,
   comerciantes y peatones. La página responde por toda la ciudad, y no hay forma de separar las dos cosas con estos datos.
4. **Le va mejor en los niveles bajos o medios:**
   - **V6, la imagen de Galán:** 28,6 contra 26. Encontró preguntas del mismo gobierno (DI-CO39).
   - **V2, usar el metro:** 59,5 contra 70, dentro del rango.

**En corto:** la página se equivoca menos que adivinar (16,8 contra 26,8 puntos), pero le cuesta acercarse a los resultados
extremos y no se compromete. Para cifras muy altas o muy bajas, el rango casi siempre cruza el 50 %.
