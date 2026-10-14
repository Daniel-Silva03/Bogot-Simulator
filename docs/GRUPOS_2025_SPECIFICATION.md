# PRECISIÓN POR GRUPOS — ¿acierta la página por sexo, edad y estrato, y no solo en el total?

Pre-registro escrito el **14 de octubre de 2026**, antes de calcular nada. Lo pidió Daniel: es la prueba de «distribuciones
por subgrupos» del marco de validación de Artificial Societies (arXiv 2609.30030). **Gasto: USD 0.**

## 1. Pregunta

La página muestra cada pregunta medida en tres grupos: estrato (1-2, 3-4, 5-6), edad (cinco tramos) y sexo. **¿Esas cifras
por grupo aciertan lo que respondió ese grupo después, o la página solo acierta el total?**

**La prueba es a ciegas, como la del peso por año** (`PESO_ANIO_RECIENTE`):
- con la **población 2022-2024**, que no tiene a nadie de 2025, se adivina por grupo lo que respondió la EPC 2025;
- en las **35 preguntas** que 2025 midió igual.

**Fuera de alcance:** las preguntas nuevas. Allí la página no da cifras por grupo (DI-CO2).

## 2. Lo que se mide

Todo en la escala de 0 a 100 de `PESO_ANIO_RECIENTE` (0 = primera respuesta, 100 = la última), sin «no sabe».

**La página, por grupo:** la media de los agentes del grupo, con su peso, como la calcula hoy (`motor._grupos`, DI-CO5).

**El real, por grupo:** la media de los encuestados de 2025 del grupo, con `Factor1`. Los grupos se arman igual:
- estrato con `DMO_4_1`;
- edad con `DMO_3_1` en los tramos de la página;
- sexo con `DMO_1`.

**Tres cifras:**
- **E_grupo:** el error medio de la página por grupo, sobre las 35 preguntas y los 10 grupos.
- **E_ciudad:** el error medio de usar la cifra de la ciudad para todos los grupos. Es lo que da una página que no
  distingue grupos.
- **Las brechas:** la correlación entre la diferencia de cada grupo con la ciudad según la página y la misma diferencia en
  2025. Si la página ve bien quién está más de acuerdo, la correlación es alta.

**Por dimensión:** las tres cifras, también por separado para estrato, edad y sexo.

**Lo que se declara:**
- **Los grupos de 2025 son chicos.** Con 1.520 encuestados, el estrato 5-6 tiene unos 150, y cada tramo de edad unos
  300. Las cifras reales por grupo tienen su propio ruido, que sube E_grupo y baja la correlación.
- **Ya se conoce el error de la ciudad en esta prueba:** 4,43 (`PESO_ANIO_RECIENTE_RESULTS.md`).

## 3. Regla (escrita antes de calcular)

**Las cifras por grupo de la página aportan información si se cumplen las dos:**
- **R1:** E_grupo es al menos **0,5 puntos menor** que E_ciudad. Es decir: distinguir grupos acierta más que dar a todos la
  cifra de la ciudad.
- **R2:** la correlación de las brechas es **0,5 o más**.

**Si no se cumplen,** la página podría advertir que sus grupos son menos confiables que el total. Eso sería otra decisión.

## 4. Predicciones

- **PG1.** Se cumplen las dos.
- **PG2.** Lo que mejor ve es el estrato, y lo que peor, el sexo. Las diferencias por sexo son pequeñas y se pierden en el
  ruido.
- **PG3.** E_grupo queda entre 5 y 8 puntos, por encima del error de la ciudad (4,43), por el ruido de los grupos chicos.

## 5. Código

- **Código:** `src/experiments/grupos_2025.py`, con su prueba. Reutiliza `peso_anio_reciente` (escala, datos y preguntas).
- **Resultados** en `GRUPOS_2025_RESULTS.md`. Las cifras por pregunta y grupo quedan en `data/processed/grupos_2025/`: la EPC
  es pública, así que se podrían subir; se dejan fuera por tamaño.
