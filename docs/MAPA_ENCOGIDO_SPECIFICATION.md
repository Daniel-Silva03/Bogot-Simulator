# MAPA POR LOCALIDAD APOYADO EN LA CIUDAD — ¿acierta mejor cada localidad si se acerca a un ancla según su ruido?

Pre-registro escrito el **14 de octubre de 2026**, antes de calcular nada. Lo pidió Daniel (mejora 2 de las que no dependen
de datos nuevos). **Gasto: USD 0.**

## 1. Pregunta

**Hoy cada localidad del mapa usa solo a sus encuestados:** unos 250 en 2022-2024, y menos en las preguntas de un solo año.
Adivinando 2025 con la población 2022-2024, el error por localidad es de **7,94 puntos**, casi el doble que en la ciudad
(4,43; `PESO_ANIO_RECIENTE_RESULTS.md`).

**La técnica estándar de áreas pequeñas** («encogimiento», como en el estimador de Fay-Herriot): la cifra de cada localidad se
acerca a un ancla, más cuanto más ruidosa es.

**¿Acierta mejor el mapa?**

## 2. Las dos variantes

Para cada pregunta y cada localidad *l*:
- **la cifra de hoy**, *m_l*: la media de los agentes de la localidad, en la escala de 0 a 100 de `PESO_ANIO_RECIENTE`
  (regla A);
- **su ruido**, *v_l*: la varianza de las respuestas de los donantes de la localidad, dividida por cuántos donantes
  distintos respondieron;
- **cuánto difieren de verdad las localidades**, τ²: la varianza de las *m_l* entre localidades menos el ruido medio, con
  mínimo 0, por el método de momentos;
- **el peso propio:** *w_l = τ² / (τ² + v_l)*. Si las localidades casi no difieren, o la localidad tiene mucho ruido, *w_l*
  es bajo y la cifra se acerca al ancla;
- **la cifra apoyada:** *w_l · m_l + (1 − w_l) · ancla*.

**Las anclas:**
- **S1, la ciudad:** la cifra de la ciudad de la página.
- **S2, las localidades parecidas por estrato:** lo que predice una regresión lineal de las *m_l* sobre el estrato medio de
  la localidad, el de sus agentes. Una localidad de estrato alto se acerca a lo que dicen las de estrato alto, no a la ciudad.

**Todo se calcula con los datos de 2022-2024.** Nada de 2025 entra en el cálculo.

## 3. Lo que se mide

**Contra las medias de cada localidad en 2025** (`Factor1`; 18 localidades: 2025 no tiene La Candelaria), en las 35
preguntas:
- **el error por localidad:** la media sobre preguntas y localidades de la diferencia absoluta;
- **el orden:** el Spearman entre las cifras de las localidades y las de 2025, en cada pregunta, y su media.

**Lo que se declara:** cada localidad de 2025 tiene unos 80 encuestados. Su cifra real también tiene ruido, así que ningún
método puede llegar a 0 de error.

## 4. Regla (escrita antes de calcular)

**El mapa pasa a la variante que gane si se cumplen las dos:**
- **R1:** el error por localidad baja **al menos 0,5 puntos** (7,44 o menos).
- **R2:** el orden medio de las localidades no baja.

**Si las dos variantes cumplen,** gana la de menor error. La cifra de la ciudad no cambia en ningún caso: el encogimiento
solo mueve el mapa.

**Si gana una,** pasar a la página es otra decisión (DI-CO40). Habría que recalcular también el margen de cada localidad, y
eso va con su propio diseño.

## 5. Predicciones

- **PM1.** S1 baja el error entre 0,5 y 1,5 puntos.
- **PM2.** S2 baja el error más que S1.
- **PM3.** Ninguna baja el orden de las localidades.

## 6. Código

- **Código:** `src/experiments/mapa_encogido.py`, con su prueba. Reutiliza `peso_anio_reciente`.
- **Resultados** en `MAPA_ENCOGIDO_RESULTS.md`. La EPC es pública; las cifras quedan en `data/processed/mapa_encogido/`.
