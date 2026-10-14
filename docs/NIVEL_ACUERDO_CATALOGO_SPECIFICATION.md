# ¿ESTARÍA BOGOTÁ DE ACUERDO? — ¿mejora la estimación si el catálogo de la página entra a las candidatas?

Pre-registro escrito el **14 de octubre de 2026**, antes de hacer ninguna llamada. Gasto: **~USD 0,30, con tope de USD
0,80**, aprobado por Daniel («sí, escribe el pre-registro y córrela»). El costo se confirma con una llamada de prueba.

## 1. Pregunta

**El problema** (`NIVEL_ACUERDO_LOTE8_RESULTS.md` §3): cuando no hay una pregunta casi igual entre las candidatas, la
estimación se queda cerca del 50 %. En la confianza en las instituciones, con reales de 10 % a 19 %, dio cerca de 50 %.

**El arreglo propuesto:** las candidatas de hoy (139, configuración C) vienen de otras encuestas. **Las 84 preguntas medidas
del catálogo de la página no están entre ellas**, aunque son de Bogotá y del tema de la página. Ahí están la imagen del
Concejo, la gestión del Concejo y de Galán, la corrupción y la transparencia del gobierno.

**¿Estima mejor Luna con 223 candidatas (configuración E: las 139 y las 84 del catálogo) que con las 139 de hoy (C)?**

La regla de siempre no cambia: **Luna solo elige preguntas parecidas; nunca ve resultados ni pone cifras.** La cifra es la
media de lo que respondió la gente en las elegidas.

## 2. Datos

**Objetivos: los mismos 139 de la prueba del lote 8.** Son las 129 de la prueba del lote 6 y las 10 guardadas del lote 8.
Sus resultados reales ya están calculados.

**Candidatas:**
- **C:** las 139 de la página (`nivel_acuerdo_lote6.candidatas()[1]`).
- **E:** esas 139 y las 84 del catálogo de la población 2022-2025, cada una con:
  - **texto:** el de la encuesta;
  - **categorías:** las de la escala que muestra la página (`motor.vista`, DI-CO19);
  - **lado favorable:** el de la página (`motor.lado`, DI-CO18);
  - **resultado real:** el porcentaje de ese lado en la ciudad, como lo da hoy la página (`responder_catalogo`).

  Cada una es su propia familia.

**Ningún objetivo está en el catálogo.** Los bancos excluyen las preguntas que repiten el catálogo (regla 3 de §12). Se
revisó el texto de los 139 contra el catálogo antes de escribir esto.

**Lo más cercano son tres de la Encuesta Distrital de Percepción 2025:**
- `EDP25_Gx503` y `EDP25_Hx503`, la situación económica del hogar y de la ciudad, se parecen a `CO2`;
- `EDP25_Ix503`, el optimismo sobre el futuro económico, se parece a `CO1_2`.

Son de otra encuesta y con otra redacción, y quedan. Se reporta también la cifra sin ellas.

**Un límite que se declara:** los encuestados de la EPC 2025 son a la vez donantes de la población y la fuente de las 10
guardadas del lote 8. Para el nivel, que usa la cifra de la ciudad de otras preguntas, no es la misma respuesta. Pero en esas
10 la ventaja del catálogo puede ser mayor que en una pregunta de otra encuesta.

## 3. Método

El de `NIVEL_ACUERDO_LOTE8`, sin cambios:
- `nivel_parecidas_b` con `openai/gpt-6-luna` a temperatura 0;
- un rango fijo de ±23,4.

**Lo que se reutiliza:** C en los 139 ya está corrida (`nivel_acuerdo_lote8.json`) y se reutiliza sin llamar.

**Lo que se llama:** E en los 139. Caché nueva: `cache_nivel_acuerdo_catalogo.json`, que no se sube.

## 4. Regla (escrita antes de calcular)

**E reemplaza a C en la página si se cumplen las tres condiciones en los 139 objetivos:**
1. **E pasa la regla de la validación:** EAM ≤ 15,8; acierto del lado ≥ 67 % y ≥ referencia fija + 10 puntos.
2. **E no estima peor que C:** EAM de E ≤ EAM de C (15,6).
3. **Al decidir, E acierta al menos el 90 %.**

**Si no se cumplen, sigue C.**

**Secundario, sin peso en la decisión:**
- las mismas cifras en las 10 guardadas del lote 8 y en las 129;
- los 139 sin las tres de la Encuesta Distrital de Percepción de §2.

## 5. Predicciones (escritas antes de calcular)

- **P1.** Se cumplen las tres condiciones: E reemplaza a C.
- **P2.** En las 10 guardadas del lote 8, el EAM de E baja de 20 (C: 25,9).
- **P3.** En las 129, el EAM de E queda a menos de 1 punto del de C (14,8).
- **P4.** E decide («probablemente sí» o «no») en más preguntas que C (11 de 139).

## 6. Gasto

**Unas 139 llamadas,** más largas que las de C, porque el catálogo va en cada una.
- **Total:** unos USD 0,30, con tope de USD 0,80.
- **Antes de correr,** una llamada de prueba.
- **El código se detiene solo** al llegar al tope o si el servicio falla.

## 7. Datos que se suben

- **No se suben:** la salida y las candidatas del catálogo. La salida trae porcentajes de las preguntas del CNC (D21), y las
  cifras del catálogo salen de la población, que no se sube.
- **`NIVEL_ACUERDO_CATALOGO_RESULTS.md`** da cifras de error y acierto, y pregunta por pregunta solo las del lote 8, que son
  públicas.

## 8. Código

- **Código:** `src/experiments/nivel_acuerdo_catalogo.py`.
- **Pruebas:** `tests/test_nivel_acuerdo_catalogo.py`.
