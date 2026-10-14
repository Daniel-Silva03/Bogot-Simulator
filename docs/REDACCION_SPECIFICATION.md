# EFECTO DE LA REDACCIÓN — ¿cuánto cambia la respuesta de la página si la misma pregunta se escribe distinto?

Pre-registro escrito el **14 de octubre de 2026**, antes de hacerle ninguna de estas redacciones a la página. Lo pidió Daniel:
es la prueba de «efecto de redacción» del marco de validación de Artificial Societies (arXiv 2609.30030). Ahí reportan un
cambio de 1,4 puntos para su sistema y de 6,2 para el mejor modelo de lenguaje. Gasto: **unos USD 0,10, con tope de USD
0,25**; falta el visto bueno de Daniel.

## 1. Las preguntas

**Diez preguntas, cada una con tres redacciones del mismo significado:**
- la **A** es la de siempre;
- la **B** y la **C** son como podría escribirlas otra persona.

Se escriben **tal cual**.

**Cuatro del catálogo:** deberían ir siempre a su pregunta medida.

| # | Código esperado | A | B | C |
|---|---|---|---|---|
| C1 | `AG2` | ¿Qué tan orgullosos se sienten de Bogotá? | ¿La gente siente orgullo de vivir en Bogotá? | ¿Los bogotanos están orgullosos de su ciudad? |
| C2 | `CV1` | ¿Qué tan satisfechos están con Bogotá como lugar para vivir? | ¿A la gente le gusta vivir en Bogotá? | ¿Los bogotanos están contentos con la ciudad para vivir? |
| C3 | `GG3_GALAN` | ¿Cómo califica la gente la gestión del alcalde Galán? | ¿Qué tan buena es la gestión de Carlos Fernando Galán según los bogotanos? | ¿Los bogotanos creen que Galán lo está haciendo bien como alcalde? |
| C4 | `VS8` | ¿La gente se siente segura en su barrio? | ¿Qué tan seguros se sienten los bogotanos en el barrio donde viven? | ¿Se siente seguridad en los barrios de Bogotá? |

**Seis nuevas:** se estiman.

| # | A | B | C |
|---|---|---|---|
| N1 | ¿Cree que el metro mejorará la movilidad en Bogotá? | ¿El metro va a mejorar la movilidad de la ciudad? | ¿Los bogotanos creen que con el metro se va a mover mejor la ciudad? |
| N2 | ¿Confía en el proyecto del metro de Bogotá? | ¿La gente confía en que el metro de Bogotá salga bien? | ¿Qué tanta confianza le tienen los bogotanos al proyecto del metro? |
| N3 | ¿Tiene una imagen favorable del alcalde Galán? | ¿La gente tiene buena imagen de Carlos Fernando Galán? | ¿Qué tan favorable es la opinión de los bogotanos sobre el alcalde Galán? |
| N4 | ¿Galán ha manejado bien la seguridad? | ¿Cómo ven los bogotanos el manejo de la seguridad por parte del alcalde Galán? | ¿La gente aprueba lo que ha hecho Galán en seguridad? |
| N5 | ¿Se debe persistir en los diálogos de paz con los grupos armados? | ¿Los bogotanos apoyan seguir con los diálogos de paz con los grupos armados? | ¿Hay que continuar las negociaciones de paz con los grupos armados? |
| N6 | ¿Colombia debe tener relaciones cercanas con Estados Unidos? | ¿Los bogotanos quieren que Colombia sea cercana a Estados Unidos? | ¿Está de acuerdo con que Colombia mantenga una relación cercana con Estados Unidos? |

**Lo que se declara:**
- **Las redacciones B y C son mías,** escritas para decir lo mismo con otras palabras. Algunas suenan más coloquiales («¿a la
  gente le gusta vivir en Bogotá?»), a propósito: así escribe la gente en la página.
- **Ya conozco la respuesta de la página a algunas redacciones A:** N1, N2 y N3 son de la validación 2026, N4 la hizo
  Daniel, y N5 y N6 son de la validación del CNC. Aquí se corren de nuevo con su propia caché, junto con las B y C.
- **No hace falta el resultado real:** se mide cuánto cambia la página, no si acierta.

## 2. Cómo se corre

Igual que la página, con `validacion_2026.preguntar`:
- reformulación;
- estimación con el texto original si es nueva (DI-CO28);
- dato medido si va al catálogo.

Modelo real, las 223 candidatas de hoy, caché propia (`data/processed/redaccion/`), una sola corrida.

## 3. Lo que se mide

**Catálogo (C1 a C4):** cuántas de las 12 redacciones van a su código esperado. Si todas van, su cifra es la misma, porque
es el dato medido.

**Nuevas (N1 a N6):**
- **El efecto de redacción:** la media, sobre las 6, de la diferencia absoluta entre la estimación de B y la de A, y entre la
  de C y la de A. Es la cifra comparable con los 1,4 y 6,2 puntos de Artificial Societies.
- **La amplitud:** la diferencia entre la estimación más alta y la más baja de las tres redacciones.
- **La llamada:** si alguna redacción da «probablemente sí» y otra «probablemente no».

**Si una nueva cambia de alcance** (va al catálogo o a «fuera» en alguna redacción), se cuenta aparte. Si la estimación queda
sin cifra, esa diferencia no entra en la media.

## 4. Regla (escrita antes de calcular)

**La página es robusta a la redacción si se cumplen las tres:**
- **R1:** al menos 11 de las 12 redacciones del catálogo van a su código.
- **R2:** el efecto de redacción en las nuevas es de **6,2 puntos o menos**, lo del mejor modelo de lenguaje en el benchmark de
  Artificial Societies.
- **R3:** ninguna pregunta nueva cambia de «probablemente sí» a «probablemente no» entre redacciones.

**El resultado se reporta y no cambia la página.** Si no es robusta, el texto de la página podría advertirlo; eso sería otra
decisión.

## 5. Predicciones

- **PR1.** R1 se cumple: el catálogo es estable.
- **PR2.** El efecto de redacción en las nuevas queda entre 4 y 10 puntos. Luna elige preguntas distintas según la
  redacción.
- **PR3.** R3 se cumple: casi todas salen «dividida», así que no hay sí/no que voltear.
- **PR4.** La página es robusta (las tres reglas).

## 6. Gasto y código

- **Gasto:** 12 del catálogo (1 llamada cada una) y 18 nuevas (unas 3 cada una): unas 66 llamadas a Luna. Cerca de **USD
  0,10, con tope de USD 0,25**.
- **Al modelo** van solo los textos de las preguntas.
- **Código:** `src/experiments/redaccion.py`, con su prueba. Resultados en `REDACCION_RESULTS.md`.
