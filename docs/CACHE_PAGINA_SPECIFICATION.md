# LA CACHÉ EN LA PÁGINA — ¿estima igual con las candidatas primero?

Pre-registro escrito el **7 de octubre de 2026**, antes de hacer ninguna llamada. Gasto: **~USD 0,07, con tope de USD 0,30**.
Lo pidió Daniel («aplica la caché a la página»). El costo se confirma tras una llamada de prueba.

## 1. Pregunta

En el voto simulado, poner primero la lista fija de candidatas y marcar la caché en el corte (`nivel_parecidas_b` DI-NB7,
`experimento9` DI-E11) bajó el costo de cada estimación un 80 %. La página estima con el orden de siempre: la pregunta nueva
primero. Cambiar el orden puede cambiar lo que el modelo elige.

**¿Estima la página igual de bien con las candidatas primero?**

## 2. Diseño

**Igual que la configuración C de `NIVEL_ACUERDO_LOTE6`**, que es la página de hoy:
- **objetivos:** las mismas 129 guardadas (las 95 de siempre y las 34 del lote 6);
- **candidatas:** las mismas 139;
- **el método:** Luna, el texto y las categorías de cada encuesta, y h = 23,4.
- **Lo único que cambia:** el orden del mensaje. Las candidatas van primero, con la marca de caché.

**La comparación es contra C con el orden de siempre, que ya está corrida** (`nivel_acuerdo_lote6.json`) y se reutiliza sin
llamar.

**En la página, la pregunta nueva no tiene familia entre las candidatas,** así que el mensaje no lleva la nota «no elijas…».
En estas 129 guardadas tampoco, porque ninguna familia guardada está entre las candidatas. El mensaje es el mismo que vería la
página.

## 3. Regla (escrita antes de llamar)

**La página pasa al orden nuevo con caché si, en las 129, se cumplen las tres condiciones:**
1. EAM con el orden nuevo ≤ EAM con el de siempre (14,8) + 0,5;
2. acierto del lado ≥ el de siempre (71 %) − 5 puntos;
3. al decidir, acierta ≥ 90 %. Si decide menos de 5 veces, se reporta pero no cuenta.

**Si no se cumplen,** la página sigue con el orden de siempre, sin caché.

## 4. Predicciones

- **PC1.** Se cumple la regla.
- **PC2.** La llamada («sí», «no» o «dividida») coincide en ≥ 85 % de las 129.
- **PC3.** El costo promedio por llamada, sin contar la primera, es ≤ 30 % del que tenía con el orden de siempre.

## 5. Gasto y código

- **Gasto:** 129 llamadas; la primera escribe la caché y las demás la leen. Unos USD 0,07, con tope de USD 0,30.
- **Código:** `src/experiments/cache_pagina.py`.
- **Prueba:** `tests/test_cache_pagina.py`.
- **Resultados:** `CACHE_PAGINA_RESULTS.md`. Solo cifras de error y costo, sin porcentajes de las encuestas del CNC.
