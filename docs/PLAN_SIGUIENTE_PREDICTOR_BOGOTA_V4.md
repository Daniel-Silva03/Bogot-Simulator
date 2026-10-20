# Plan v4 — siguientes pasos del predictor de opinión pública de Bogotá

**Fecha:** 20 de octubre de 2026  
**Base:** resultados del plan v3 y decisiones de producto comunicadas por el equipo.

## Resumen ejecutivo

La siguiente inversión debería centrarse en verificar si los agentes pueden anticipar cambios de opinión de forma reproducible, en lugar de aumentar el tamaño del panel o seguir probando variantes de instrucciones sin una hipótesis medible.

Los resultados del plan v3 dejan tres conclusiones:

1. En la pregunta de gestión del alcalde para 2025, la persistencia predijo aproximadamente 42 %, los agentes 29 % y el resultado observado fue 26 %. Es un caso favorable a los agentes, pero no demuestra por sí solo una capacidad generalizable.
2. El contexto numérico estructurado redujo el error medio de 7,97 a 7,56 puntos en nueve preguntas, pero la ventaja desapareció al retirar los dos casos en los que más ayudó. La variante no se conserva como método validado.
3. Los intervalos siguen teniendo una cobertura insuficiente para gobierno: la regla más conservadora cubrió 69,6 % de 23 casos; la cobertura de los casos objetivo de 2025 fue 58 %.

**Prioridad recomendada:** (1) comprobar si el resultado favorable de Galán se reproduce; (2) investigar y, solo si la prueba lo permite, corregir el sesgo positivo de los agentes; (3) mejorar la comunicación y evaluación de los rangos de incertidumbre.

El plan respeta las decisiones actuales: los agentes siguen generando la cifra principal en el producto, siempre se devuelve una cifra y los agentes continúan activos como experimento declarado.

---

## Paso 1. Comprobar si el acierto de Galán en 2025 se generaliza

### Objetivo

Determinar si los agentes son capaces de anticipar cambios de opinión en preguntas de gobierno de manera reproducible o si el caso de 2025 fue fortuito.

### Datos y diseño

Evaluar las transiciones para las que hay perfiles históricos utilizables:

| Corte de información | Resultado objetivo |
|---|---|
| EPC 2022 | EPC 2023 |
| EPC 2023 | EPC 2024 |
| EPC 2024 | EPC 2025 |

Para cada transición, comparar principalmente:

- **Persistencia:** repetir el último dato medido y comparable.
- **Agentes actuales:** ejecutar el método existente con los perfiles del año base.

La variante de contexto numérico estructurado no entra en la comparación principal, porque ya se decidió no conservarla. Podrá plantearse como una hipótesis nueva en otra prueba, siempre con un preregistro separado.

### Prerregistro obligatorio

Antes de ejecutar las llamadas, registrar:

1. La lista completa de preguntas objetivo y los criterios para decidir si sus textos y escalas son comparables.
2. Las exclusiones justificadas por cambios de cuestionario, aplicadas antes de mirar el error.
3. El modelo, prompt, temperatura, tamaño del panel, ponderaciones y cualquier regla de agregación.
4. La métrica principal: error absoluto medio en puntos porcentuales. Métricas secundarias: sesgo firmado y error por transición anual.
5. Una regla de aceptación. Propuesta: el método de agentes debe superar a la persistencia en el conjunto completo, mostrar una ventaja en más de una transición y mejorar el error absoluto medio al menos un punto porcentual. El umbral es una decisión de diseño que debe quedar fijada antes de ejecutar.
6. Una regla contra la selección posterior: la evaluación incluye todos los objetivos elegibles; no se puede conservar una variante solo porque acierte la pregunta de gestión del alcalde.

### Riesgo de filtración temporal

Los años evaluados ya pasaron y el modelo actual podría conocer, directa o indirectamente, parte de los acontecimientos o resultados. Enmascarar fechas y limitar el contexto reduce el riesgo, pero no garantiza eliminar el conocimiento incorporado durante el entrenamiento.

Por eso, los resultados retrospectivos pueden demostrar consistencia entre preguntas y periodos históricos, pero no prueban por sí solos que el sistema anticipe acontecimientos que todavía no conoce. Para esa afirmación se necesita, con el tiempo, una evaluación prospectiva.

### Costo

Aproximadamente **USD 0,05 por pregunta por ejecución de 200 agentes**, según la tarifa indicada por el equipo. Una variante nueva en 20 preguntas costaría alrededor de **USD 1,00**, sin contar repeticiones.

### Qué haría descartar la hipótesis

- Los agentes no mejoran a la persistencia en el conjunto completo.
- La ventaja depende de una sola pregunta o transición.
- El resultado desaparece al aplicar reglas razonables de comparabilidad.
- No se puede descartar una filtración temporal que invalide la prueba.

---

## Paso 2. Investigar el sesgo positivo antes de corregirlo

### Objetivo

Comprobar si existe un sesgo positivo estable en preguntas de gobierno y si una corrección aprendida con datos pasados puede mejorar el error en preguntas y periodos reservados.

En las nueve preguntas del experimento anterior, el sesgo firmado fue de +3 puntos para los agentes y +4 con contexto numérico. Esas medias son pequeñas frente a algunos errores concretos y pueden ocultar comportamientos distintos por tema o por cambio de cuestionario. No se debe asumir que una constante general de tres puntos puede restarse a todas las respuestas.

### Diseño

**Primero, auditar las preguntas.** Revisar el texto literal, las opciones de respuesta, el orden de las preguntas, la definición del porcentaje informado y los cambios entre olas. No comparar como idénticas dos mediciones que no sean conceptualmente comparables.

**Después, probar una corrección estadística sencilla:**

1. Aprender el sesgo con preguntas y periodos distintos de los que se usarán para la evaluación.
2. Si el volumen de datos es reducido, usar una corrección regularizada o contraída hacia cero para evitar sobreajuste.
3. Aplicarla a preguntas o periodos reservados que no hayan participado en el ajuste.
4. Comparar tres métodos: agentes sin corregir, agentes corregidos y persistencia.
5. Informar por separado el sesgo firmado y el error absoluto medio.

Esta hipótesis es diferente de calibrar el resultado para que coincida con el total conocido de una encuesta. La calibración al total ya se intentó y no produjo una mejora fuera de muestra.

También puede examinarse el resultado al excluir la pregunta «¿conoce Bogotá Cómo Vamos?», dado que el desempeño relativo cambió cuando se la excluyó. Esa comparación es exploratoria porque surgió después de ver resultados; no debe utilizarse como prueba confirmatoria ni cambiar la muestra principal del Paso 1.

### Regla de aceptación

La corrección solo se conserva si, en datos reservados:

- reduce el error absoluto medio;
- reduce el sesgo positivo sin generar otro sesgo sistemático;
- no empeora frente a la persistencia en la evaluación principal.

Acercar el sesgo medio a cero no basta si el error absoluto aumenta.

### Costo

El cálculo estadístico cuesta prácticamente cero llamadas. El costo de API depende de cuántas preguntas adicionales sean necesarias para obtener predicciones comparables.

### Qué haría descartar la hipótesis

- El sesgo no se repite fuera de muestra.
- La corrección solo funciona al aplicarse a los mismos datos que la originaron.
- Disminuye el sesgo, pero aumenta el error absoluto.
- Los cambios de cuestionario explican una parte importante del sesgo aparente.

---

## Paso 3. Hacer que los rangos sean honestos sin volverlos inútiles

### Situación observada

Los resultados del plan v3 indican que ninguna regla preregistrada alcanzó los objetivos de cobertura: 75 % global y 70 % en gobierno. La regla más conservadora cubrió 69,6 % de 23 casos de gobierno, mientras que la cobertura de los casos de 2025 fue 58 %. El rango más amplio mejora la cobertura en algunas transiciones, pero tampoco anticipó el año movido de 2025.

### Qué hacer en la página ahora

Mantener los rangos actuales como **referencias orientativas provisionales**, pero comunicar explícitamente la cobertura observada y sus limitaciones. No describirlos como intervalos que garantizan una cobertura futura.

Texto sugerido:

> **Rango orientativo provisional: ±10 puntos porcentuales**
>
> En la validación histórica de preguntas de gobierno, este rango cubrió aproximadamente 7 de cada 10 casos. La cobertura fue menor en periodos de cambios importantes. El rango no es un margen de error de encuesta ni garantiza que la cifra real de hoy esté dentro.

Este texto debe actualizarse si cambia el rango o la evaluación. Para otras categorías, se puede mostrar la cobertura correspondiente a sus casos históricos, sin generalizar la cobertura de una categoría a otra.

### Evaluación retrospectiva de origen móvil

Continuar usando una evaluación de origen móvil: cada rango se calcula exclusivamente con errores que habrían estado disponibles en la fecha de predicción. Informar al menos:

- cobertura global y por dominio;
- cobertura por año objetivo;
- cobertura en transiciones con y sin cambio de gobierno;
- ancho medio del rango;
- sensibilidad al retirar cada año de la evaluación;
- número de casos, dado que 23 casos de gobierno es una muestra pequeña.

No escoger retrospectivamente un rango para cubrir el desplome de 2025 y luego presentar el mismo año como validación independiente.

### Segundo rango de estrés

Como análisis separado, evaluar una regla preregistrada de rango de estrés que use errores históricos grandes o una ampliación bajo condiciones definidas de antemano. Debe evaluarse con datos reservados y presentarse como una alternativa, no como una garantía de cobertura.

No basta con ensanchar todos los rangos hasta obtener una buena cobertura retrospectiva: eso puede volverlos poco útiles y no garantiza que cubran un cambio futuro sin precedentes.

### Sobre métodos nuevos

Se pueden estudiar métodos secuenciales o conformales para series temporales, pero no deben presentarse como una garantía automática. Su cobertura depende de las condiciones y de la estabilidad de los datos; un cambio de distribución puede degradar el desempeño.

### Costo

**Cero llamadas adicionales a agentes** para calcular los rangos a partir de predicciones y errores históricos ya disponibles.

---

## Decisiones de producto y comunicación

Las decisiones actuales se mantienen:

1. En preguntas del alcalde ya medidas, la cifra principal sigue siendo la de los agentes.
2. La página siempre devuelve una cifra.
3. Los agentes permanecen activos en el modelo real como experimento declarado.

Para no confundir una decisión de interfaz con evidencia predictiva, los informes internos deben separar tres estados:

- **Resultado predictivo validado:** el método superó a la persistencia en una prueba preregistrada y fuera de muestra.
- **Resultado exploratorio:** los agentes generan una cifra útil para explorar, pero su ventaja predictiva no está demostrada.
- **Rango provisional:** descripción empírica de errores pasados, sin prometer cobertura futura.

La cifra de los agentes puede permanecer como resultado principal por decisión de producto, pero debe seguir identificada como simulación exploratoria y acompañarse de una explicación del error histórico pertinente. No se debe afirmar que reemplaza una encuesta actual o que es el mejor estimador disponible si la evaluación no lo respalda.

---

## Restricciones que deben mantenerse

- Prerregistrar los diseños, las métricas, las exclusiones y las reglas de decisión antes de ejecutar.
- Usar la persistencia como benchmark obligatorio.
- No enviar respuestas individuales de las encuestas políticas propias a ningún modelo de lenguaje.
- Mantener bajo el gasto de API y justificar cada experimento adicional.
- No presentar resultados exploratorios como validaciones aprobadas.
- No cambiar la muestra principal ni las reglas después de observar los resultados.

## Orden de ejecución recomendado

1. **Paso 1:** evaluar la generalización del acierto de gestión del alcalde de 2025 en todas las preguntas comparables disponibles.
2. **Paso 3:** mantener y documentar rangos provisionales mientras se amplía su evaluación de origen móvil.
3. **Paso 2:** solo después, probar una corrección de sesgo con datos reservados, sin calibrar al total conocido.

El Paso 3 puede ejecutarse en paralelo con el Paso 1 porque no requiere nuevas llamadas a agentes.

## Regla final para decidir inversiones

No aumentar el tamaño del panel ni abrir una nueva ronda amplia de prompts hasta demostrar qué parte del error proviene de variación de muestreo, qué parte de sesgo sistemático y qué parte de falta de información sobre acontecimientos posteriores. Si el método de agentes no supera a la persistencia en la prueba general, puede mantenerse por decisión de producto como estimación exploratoria, pero no debe describirse como una mejora predictiva validada.
