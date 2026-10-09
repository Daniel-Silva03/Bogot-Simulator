# ¿DISTINGUE MIROFISH ENTRE ALCALDES BIEN Y MAL CALIFICADOS?

Pre-registro escrito el **9 de octubre de 2026**, antes de correr nada. Lo pidió Daniel.
**Gasto: unos USD 0,15, con tope de USD 1 para las tres corridas juntas.**

## 1. La pregunta

En la prueba de Galán, MiroFish dio 46 %, cerca de la mitad, sin ninguna base (`MIROFISH_GALAN_RESULTS.md`). Ese número
coincide con encuestas de aprobar o desaprobar de 2026 (44 a 47 %), pero «más o menos la mitad» es lo que diría un modelo
que no sabe. Acercarse a una cifra no prueba nada.

**La prueba de verdad es si distingue.** Con tres alcaldes de aprobación muy distinta en la misma encuesta, ¿les da
MiroFish cifras distintas, en el orden correcto?

## 2. Método

**La referencia, fija:** la encuesta **Invamer de junio de 2025**. Es la misma encuesta y la misma pregunta para los tres
alcaldes ([Asuntos Legales](https://www.asuntoslegales.com.co/actualidad/encuesta-invamer-de-alcaldes-junio-de-2025-4160449)):

| Ciudad | Alcalde | Aprobación |
|---|---|---|
| Medellín | Federico Gutiérrez | 79 % |
| Bogotá | Carlos Fernando Galán | 42 % |
| Cali | Alejandro Éder | 30 % |

**MiroFish,** con la misma instalación, modelo y topes: Luna y 10 rondas. Se corre una vez por ciudad:
`python src/experiments/mirofish_segunda_vuelta.py --caso alcalde_medellin` (igual con `alcalde_bogota` y `alcalde_cali`).

**La misma petición para las tres** (`requerimiento_alcalde`): simular la conversación de los adultos de la ciudad sobre la
gestión del alcalde en el primer semestre de 2025, y estimar qué porcentaje la aprueba, con una sola cifra.

**Las semillas,** con hechos públicos hasta mayo de 2025 y sus fuentes:
- `docs/anexos/mirofish_semilla_medellin.md`;
- `docs/anexos/mirofish_semilla_cali.md`;
- Bogotá: la misma semilla de la prueba de Galán (`mirofish_semilla_galan.md`). Sus hechos llegan hasta abril de 2025.

**Las tres semillas siguen las mismas reglas:**
- ningún porcentaje de encuestas ni de votación (Gutiérrez ganó con 73 % de los votos, y esa cifra se habría podido
  reescalar);
- un número parecido de hechos a favor y en contra;
- ningún dato del CNC.

**Paso 0:** preguntarle a Luna si conoce la aprobación de cada alcalde en Invamer de junio de 2025. Si conoce alguna, esa
ciudad no se corre.

**Cómo se lee la cifra:** la que dé el informe, copiada textualmente. Si es un rango, el punto medio. Si no da cifra, «no da
cifra», y esa ciudad cuenta como fallo.

## 3. Regla

**MiroFish distingue si se cumplen las tres condiciones:**
1. **R1, el orden:** Medellín > Bogotá > Cali;
2. **R2, la separación:** entre la cifra más alta y la más baja hay al menos 20 puntos (en la realidad, 49);
3. **R3, el error:** su error medio en las tres es menor que el de decir 50 % para todos (19,0 puntos).

**Si no se cumplen,** se confirma que MiroFish no sirve para dar porcentajes de aprobación.

## 4. Predicciones

- **PD1.** No acierta el orden de los tres.
- **PD2.** La separación es menor de 20 puntos.
- **PD3.** Su error medio no baja de 19,0.

## 5. Lo que ya se sabe, y se declara

- **Las tres cifras reales,** y que Medellín es la ciudad del alcalde con más aprobación desde 2024.
- **Las semillas las escribí yo,** sabiendo las cifras. Para no sesgarlas, siguen las reglas de §2, y cada hecho tiene su
  fuente. Igual, quien las escribe sabe el resultado: se declara.
- **Luna puede saber de 2024** (su conocimiento llega a junio de 2024): por ejemplo, que Gutiérrez empezó con alta
  aprobación. Es información que cualquiera tenía en 2025, y se acepta.
- **El resultado de MiroFish con Galán** (46 %, con otra petición y otro periodo).

## 6. Gasto, datos y código

- **Gasto:** tres corridas a unos USD 0,05, unos USD 0,15, y el paso 0, unos USD 0,0003. **Tope de USD 1** para las tres
  juntas: si la suma pasa, no se corren las que faltan.
- **Nada del CNC ni de la EPC** sale hacia MiroFish, Zep ni el modelo.
- **Las salidas** quedan en `data/processed/mirofish/discriminacion/`, ignoradas por git.
- **Código:** `src/experiments/mirofish_segunda_vuelta.py` (`ALCALDES`, `requerimiento_alcalde`).
- **Pruebas:** `tests/test_mirofish_segunda_vuelta.py`.
- **Resultados:** `MIROFISH_DISCRIMINACION_RESULTS.md`.
