# ¿ESTARÍA BOGOTÁ DE ACUERDO? — ¿mejora la estimación con las candidatas del lote 6?

Pre-registro escrito el **6 de octubre de 2026**, antes de calcular los resultados del guardado del lote 6 y antes de
hacer ninguna llamada. Gasto: **~USD 0,20, con tope de USD 0,60**, aprobado por Daniel («haz la prueba de sumar el
lote 6»). El costo se confirma tras una llamada de prueba.

## 1. Pregunta

La página estima con Luna (D20) y **109 candidatas** (configuración B). El lote 6 (`BANCO_PREGUNTAS_NUEVAS.md` §15)
agrega **30 preguntas de práctica** de opinión política de las encuestas del CNC para Semana, solo de Bogotá: migración,
el paro de 2021, el rumbo del país y la vacunación.

**¿Estima mejor Luna con 139 candidatas (configuración C) que con las 109 de hoy (B)?**

## 2. Datos

**Objetivos: 129 preguntas guardadas.**
- **Las 95 de la prueba del lote 5 y de la de Luna.** Sus resultados reales ya están calculados.
- **Las 34 guardadas del lote 6.** Sus resultados reales se calculan **después** de subir este documento, con el mismo
  cálculo del lote 6, incluido el mínimo de 200 respuestas válidas de su enmienda 1. Las que no pasen la regla de
  estructura quedan fuera.

**Candidatas:**
- **B:** las 109 de la página (`nivel_acuerdo_lote5.candidatas()[1]`);
- **C:** esas 109 más las 30 de práctica del lote 6, con su resultado real de Bogotá.

**Ninguna familia guardada está entre las candidatas.** Las 373 del lote 7 (electorales) no entran ni como objetivo ni
como candidata (D21).

## 3. Método

El de `NIVEL_ACUERDO_LUNA`, sin cambios:
- `nivel_parecidas_b` (instrucciones, lectura con DI-NB6, reintento), con `openai/gpt-6-luna` a temperatura 0;
- el texto y las categorías originales de cada encuesta;
- **un rango fijo de ±23,4 para las dos**, el de Luna, para que la comparación sea del pozo de candidatas.

**Lo que se reutiliza y lo que se llama:**
- **B en las 95** ya está corrida (`nivel_acuerdo_luna.json`, guardado) y se reutiliza sin llamar;
- **llamadas nuevas:** B en las 34 del lote 6, y C en las 129.
- **Caché nueva:** `data/processed/banco/cache_nivel_acuerdo_lote6.json`, que no se sube.

**Un límite que se declara.** La página estima con el texto de la persona y la escala de la reformulación (DI-CO28). Esta
prueba, como la de Luna, usa el texto y las categorías de la encuesta. Mide el pozo de candidatas, no la reformulación.

## 4. Regla (escrita antes de calcular)

**C reemplaza a B en la página si se cumplen las tres condiciones en los 129 objetivos:**
1. **C pasa la regla de la validación:** EAM ≤ 15,8; acierto del lado ≥ 67 % y ≥ referencia fija + 10 puntos.
2. **C no estima peor que B:** EAM de C ≤ EAM de B en los mismos 129.
3. **Al decidir, C acierta al menos el 90 %.**

**Si no se cumplen, sigue B.**

**Secundario, sin peso en la decisión:** las mismas cifras solo en las guardadas del lote 6, donde C tiene preguntas de
las mismas encuestas como candidatas, y solo en las 95.

**Por D21,** el texto de estas preguntas puede ir a la API; sus resultados se calculan en el equipo. **No se sube ningún
resultado de las encuestas del CNC** (`NIVEL_ACUERDO_LOTE6_RESULTS.md` da solo cifras de error y acierto, no porcentajes
de las preguntas).

## 5. Predicciones (escritas antes de calcular)

- **P1.** Se cumplen las tres condiciones: C reemplaza a B.
- **P2.** En las guardadas del lote 6, el EAM de C es al menos 2 puntos menor que el de B.
- **P3.** En las 95, el EAM de C queda a menos de 1 punto del de B (14,3).
- **P4.** C decide («probablemente sí» o «no») en más preguntas que B.

## 6. Gasto

**Unas 163 llamadas a ~USD 0,0013:** 34 de B y 129 de C, más los reintentos.
- **Total:** unos USD 0,20, con tope de USD 0,60.
- **Antes de correr,** una llamada de prueba.
- **El código se detiene solo** al llegar al tope o si el servicio falla.

## 7. Código

- **Código:** `src/experiments/nivel_acuerdo_lote6.py`.
- **Pruebas:** `tests/test_nivel_acuerdo_lote6.py`.
- **Resultados:** `NIVEL_ACUERDO_LOTE6_RESULTS.md`, contra este pre-registro.
