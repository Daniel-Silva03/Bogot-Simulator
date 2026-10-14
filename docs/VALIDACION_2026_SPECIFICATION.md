# VALIDACIÓN 2026 — ¿acierta la página en preguntas nuevas que se midieron en 2026?

**La página, tal como está hoy, frente a seis preguntas de Bogotá con resultado publicado en 2026 que la EPC no midió.**

Proyecto: Bogotá Social Simulator
Versión: 0.1 — pre-registro, antes de hacerle ninguna de estas preguntas a la página
Fecha: 14 de octubre de 2026
Origen: Daniel pidió preguntas recientes, de 2026, cuyo resultado ya se sepa, y que la prueba cuente como validación.

---

## 1. Las preguntas

Se escriben en la página **tal como están aquí**, sin cambiar una palabra. Ninguna se ha hecho todavía, ni en la página ni
en este análisis.

| # | Pregunta | Resultado conocido | Fuente |
|---|---|---|---|
| V1 | ¿Cree que el metro mejorará la movilidad en Bogotá? | 93 % | Estudio de Cultura Ciudadana del Metro 2026 |
| V2 | ¿Usaría el metro como su principal medio de transporte? | 70 % (publicado: «más del 70 %») | ídem |
| V3 | ¿Confía en el proyecto del metro de Bogotá? | 80 % | ídem |
| V4 | ¿El metro es un motivo de orgullo para Bogotá? | 88 % | ídem |
| V5 | ¿Cree que el metro empezará a funcionar en 2028? | 56 % | Encuesta Distrital de Percepción, Planeación |
| V6 | ¿Tiene una imagen favorable del alcalde Galán? | 26 % | ídem |

**Las fuentes:**
- **Estudio de Cultura Ciudadana del Metro (Empresa Metro de Bogotá):**
  - trabajo de campo de marzo a mayo de 2026;
  - 4.683 personas: residentes, comerciantes y peatones de las **9 localidades de la línea 1** (Bosa, Kennedy, Puente
    Aranda, Antonio Nariño, Santa Fe, Los Mártires, Teusaquillo, Chapinero y Barrios Unidos);
  - no publicó el texto de las preguntas.
- **Encuesta Distrital de Percepción 2025-2027 (Secretaría Distrital de Planeación):**
  - presentada el 16 de abril de 2026, con 13.082 encuestados;
  - el trabajo de campo es de 2025.

**Lo que se declara antes de correr:**
- **No es a ciegas para mí:** elegí las preguntas sabiendo sus resultados, que son públicos. Las elegí porque fueron las que
  encontré medidas en Bogotá en 2026, no por cómo creo que le irá a la página.
- **El estudio del Metro no es toda Bogotá:** solo las 9 localidades de la línea 1, e incluye comerciantes y peatones. La
  página responde por toda la ciudad. Su redacción es mía, porque el estudio no publicó la suya.
- **La Encuesta Distrital está en parte en el banco** de la estimación (lote 5: 38 afirmaciones de acuerdo de su edición
  2025). V5 y V6 no están entre esas 38, pero son de la misma encuesta y de la misma ola.
- **El 70 % de V2 es un piso:** se publicó «más del 70 %».

## 2. Cómo se corre

Igual que la página (`pagina.html`, `preguntar`):
1. **Reformulación:** `Motor.reformular(texto)`.
2. **Si es nueva:** `responder_nueva(reformulada, escala, original=texto)` (DI-CO28), y se toma su estimación: porcentaje,
   rango y llamada.
3. **Si va al catálogo:** `responder_catalogo(codigo)`, y se toma el porcentaje del lado favorable de la ciudad.

**Detalles:**
- Con el modelo real de la página (`openai/gpt-6-luna`) y las 223 candidatas de hoy (DI-CO39).
- Con una caché propia (`data/processed/validacion_2026/`), para que no se mezcle con lo que se pregunte en la página.
- **Una sola corrida.** Si una llamada falla por la red, se repite solo esa.

## 3. Regla de decisión

**Para cada pregunta:**
- **Dentro del rango:** el resultado real cae en el rango de la estimación.
- **La llamada:** «probablemente sí» acierta si el real es mayor que 50 %, y «probablemente no» si es menor. «Dividida» no
  decide.
- **El error:** la diferencia entre el porcentaje de la página y el real.

**Si la reformulación la manda al catálogo,** cuenta su error, pero no entra en el rango ni en la llamada, porque el dato
medido no trae ese rango. **Si la manda a «fuera»,** cuenta como fallo en las tres.

**La página pasa la validación 2026 si se cumplen las tres:**
- **R1:** el real cae dentro del rango en **al menos 4 de las 6**.
- **R2:** cuando dice «probablemente», **acierta en todas menos una como máximo**.
- **R3:** su error medio es **menor que el de decir 50 % para todo**, que es de 26,8 puntos en estas seis.

**Lo que se hace con el resultado:** se reporta, pase o no. **No cambia nada de la página.** Una prueba de seis preguntas
dice si lo que se validó en el banco se sostiene con preguntas de 2026, no alcanza para recalibrar.

## 4. Predicciones

- **PV1.** La página pasa la validación.
- **PV2.** En las cuatro del metro (V1 a V4), la página da menos que el resultado real. Responde por toda la ciudad, y el
  estudio se hizo cerca de la línea 1.
- **PV3.** En V6, la imagen de Galán, la página dice «probablemente no» o «dividida», nunca «probablemente sí».
- **PV4.** Ninguna de las seis va a «fuera».

## 5. Una comparación aparte, sin regla

**«¿Aprueba la gestión del alcalde Galán?»** va al dato medido de la página: «buena o muy buena», unos 34 %. Guarumo y
Ecoanalítica midieron en abril de 2026 un 53,3 % que aprueba.
- **No es la misma pregunta:** Guarumo pregunta «aprueba o desaprueba», con dos opciones; la EPC pregunta por la gestión de
  1 a 5, y «regular» no cuenta como buena.
- **No es la misma muestra:** la de Guarumo es nacional, de 74 municipios, con votantes potenciales; la cifra de Bogotá es
  su submuestra.
- **Se reporta para mostrar cuánto cambia la cifra con la forma de preguntar.** No es una prueba de la página.

## 6. Gasto y datos

- **Gasto:** 6 preguntas nuevas, de 2 a 3 llamadas cada una (reformulación, puente y estimación), más 1 del catálogo.
  Unos **USD 0,06, con tope de USD 0,20**. Falta el visto bueno de Daniel.
- **Datos:** al modelo solo van las preguntas de arriba y el catálogo. Ningún microdato. Los resultados son de fuentes
  públicas.
- **Código:** `src/experiments/validacion_2026.py`, con su prueba. Resultados en `VALIDACION_2026_RESULTS.md`.
