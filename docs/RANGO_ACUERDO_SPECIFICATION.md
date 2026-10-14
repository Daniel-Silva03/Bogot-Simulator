# RANGO SEGÚN EL ACUERDO DE LAS PREGUNTAS DE APOYO — ¿puede la página comprometerse más sin perder aciertos?

Pre-registro escrito el **14 de octubre de 2026**, antes de calcular nada. Lo pidió Daniel (mejora 1 de las que no dependen de
datos nuevos). **Gasto: USD 0.**

## 1. Pregunta

**El defecto:** la página casi nunca dice «probablemente». En las 13 preguntas de 2026 salió «dividida» 11 veces.

**El rango de hoy (DI-CO33)** depende solo de cuántas preguntas eligió Luna:

| Elegidas | Rango |
|---|---|
| 1 | ±23,9 |
| 2 | ±22,9 |
| 3 o más | ±21,7 |

No mira si esas preguntas coinciden entre sí.

**La idea:** si las preguntas en que se apoya dan resultados parecidos (por ejemplo, 18 %, 20 % y 22 %), la estimación debería
ser más segura que si dan 10 %, 30 % y 60 %. **¿Un rango que depende de ese acuerdo deja que la página se comprometa más
veces sin perder aciertos?**

## 2. Datos

**Las 139 estimaciones de la página de hoy** (configuración E, `nivel_acuerdo_catalogo.json`): qué preguntas eligió Luna en
cada una (`ids`), con el resultado real de cada elegida y de la pregunta. No se llama a ningún modelo.

## 3. El rango nuevo

**El acuerdo** es la desviación estándar de los resultados reales de las preguntas elegidas. Si eligió una sola, no hay
acuerdo que medir.

**El rango se aprende fuera de muestra,** con validación cruzada de 5 grupos por familia. En cada pliegue, con las preguntas
de entrenamiento:
1. se cortan las de 2 o más elegidas en **tres tercios** según su desviación estándar;
2. el rango de cada tercio es el **cuantil 80 % del error absoluto** de las preguntas de ese tercio, el mismo criterio del rango
   de hoy;
3. a cada pregunta de prueba se le da el rango de su tercio, según los cortes del entrenamiento.

**Con una sola elegida,** se queda el ±23,9 de hoy.

**La estimación no cambia:** sigue siendo la media de las elegidas. Solo cambia el rango, y con él la llamada
(`nivel_acuerdo.llamada`).

## 4. Lo que se mide

**Contra el rango de hoy, en las mismas 139.** Con el rango de hoy, la página decide en 19 y acierta 17 (89 %):
`NIVEL_ACUERDO_CATALOGO_RESULTS.md` §5.
- **decide:** en cuántas dice «probablemente»;
- **acierta al decidir:** cuántas de esas acierta el lado;
- **cobertura:** en cuántas el real cae dentro del rango. Un rango del 80 % debería contenerlo en cerca del 80 %.
- **la relación** entre el acuerdo y el error: la correlación de Spearman entre la desviación estándar de las elegidas y el
  error absoluto.

## 5. Regla (escrita antes de calcular)

**La página pasa al rango según el acuerdo si se cumplen las tres:**
- **R1:** decide en **al menos 5 preguntas más** que con el rango de hoy (24 o más de 139).
- **R2:** al decidir, acierta **al menos el 90 %**.
- **R3:** la cobertura es de **al menos 75 %**: el rango no se angosta más de lo que debe.

**Si se cumplen,** es una decisión nueva (DI-CO40): la página calcula el rango por tercios, con los cortes y los rangos
aprendidos de las 139. El texto de la estimación cita las cifras fuera de muestra.

## 6. Predicciones

- **PA1.** Hay relación: más desacuerdo entre las elegidas, más error (Spearman de 0,2 o más).
- **PA2.** El tercio de más acuerdo tiene un rango de menos de ±18.
- **PA3.** Se cumplen las tres reglas.

## 7. Código

- **Código:** `src/experiments/rango_acuerdo.py`, con su prueba. Resultados en `RANGO_ACUERDO_RESULTS.md`.
- **D21:** las 139 incluyen preguntas del CNC, así que solo se reportan cifras agregadas.
