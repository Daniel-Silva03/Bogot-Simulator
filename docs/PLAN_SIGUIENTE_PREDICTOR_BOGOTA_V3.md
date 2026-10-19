# Plan v3: mejorar el predictor de opinión pública de Bogotá

**Fecha:** 19 de octubre de 2026  
**Estado:** propuesta de trabajo sujeta a preregistro  
**Prioridad:** transparencia del resultado, validación de intervalos y uso prudente de agentes

## 1. Contexto y decisiones de producto

Este plan parte de los resultados registrados en `RESULTADOS_PLAN_MEJORAS_PARA_IA.md` y de tres decisiones de producto que se mantienen por ahora:

1. Para preguntas del alcalde Carlos Fernando Galán que ya cuentan con una medición, la página mostrará como resultado principal la estimación de los agentes, no el último dato medido.
2. La página debe mostrar siempre una cifra, incluso para preguntas políticas nuevas sin una medición o referencia comparable.
3. Los agentes siguen habilitados en el producto real como experimento declarado, aunque sus validaciones preregistradas no hayan superado a la persistencia.

También se mantienen estas restricciones:

- Registrar el diseño y las reglas antes de ejecutar cada prueba.
- Usar la persistencia —repetir el último dato comparable— como referencia principal.
- No enviar respuestas individuales de las encuestas políticas propias a ningún modelo de lenguaje. Como máximo, se utilizarán los textos de las preguntas y resultados agregados permitidos.
- Mantener bajo el presupuesto de API.
- No presentar una prueba fallida como una validación aprobada.

## 2. Diagnóstico que guía el plan

Los resultados anteriores indican lo siguiente:

- En las pruebas retrospectivas, la persistencia ganó a los agentes y a las combinaciones evaluadas.
- En la Fase B, el combinador `P + λ(G − P)` aprendió `λ = 0` en el conjunto evaluado.
- Los métodos temporales sencillos no superaron de forma consistente a la persistencia.
- Los agentes parecen más útiles cuando reconstruyen una respuesta oculta dentro de la misma ola o cuando la referencia disponible corresponde a otra población, por ejemplo una encuesta nacional usada para estimar Bogotá.
- El error de la persistencia aumenta con la antigüedad de la medición y es mayor en gobierno e instituciones que en varios temas de ciudad.
- Los intervalos existentes no alcanzaron la cobertura esperada en 2025.
- Las series públicas sobre Galán apenas se solapan en el tiempo y miden conceptos no siempre equivalentes: aprobación, imagen y evaluación de gestión no deben tratarse automáticamente como la misma variable.

**Conclusión operativa:** no invertir de momento en más agentes o en un agregador complejo. Primero hay que mejorar la comunicación del resultado, validar los intervalos con datos históricos y ordenar la evidencia pública disponible.

## 3. Objetivos

1. Mantener la cifra generada por los agentes como salida principal cuando así lo requiere el producto, pero identificarla explícitamente como una estimación exploratoria.
2. Comunicar el desempeño histórico sin confundir error medio, percentiles de error e intervalos de confianza o cobertura.
3. Estimar rangos de incertidumbre que se comporten mejor en distintos años y temas, con especial atención a gobierno e instituciones.
4. Crear un registro verificable de mediciones públicas sobre el alcalde y otros temas de interés.
5. Ejecutar un experimento pequeño y preregistrado que compruebe si un contexto numérico estructurado mejora los agentes frente al sistema actual.
6. Mantener la persistencia como vara para decidir si una variante realmente aporta valor predictivo.

## 4. Fase 0: corregir la comunicación en el producto

**Prioridad:** inmediata.  
**Costo de API:** USD 0.

### 4.1 Etiquetar las cifras de los agentes

Cuando la cifra proceda de agentes, usar una etiqueta visible, por ejemplo:

> **Estimación exploratoria de los agentes**  
> Resultado generado mediante simulación de perfiles con IA. No es una nueva encuesta a residentes de Bogotá.

Incluir, como mínimo:

- fecha en que se ejecutó la simulación;
- ola o año de los perfiles de referencia;
- descripción breve del procedimiento;
- error histórico pertinente y número de pruebas que lo respaldan;
- una advertencia de que el error histórico no garantiza la precisión de esa pregunta concreta.

### 4.2 Mostrar el desempeño histórico correctamente

Para las pruebas reportadas de preguntas políticas nunca medidas, el resultado disponible fue de 17 casos, con error absoluto medio de 11,3 puntos porcentuales y percentil 80 del error de 19,5 puntos. Este dato debe conservar su contexto: es una referencia histórica limitada, no una garantía para cada consulta.

No describir el error medio como “margen de error”. El error absoluto medio no es un margen muestral. Tampoco afirmar “en 8 de cada 10 casos, el error será menor que X” hasta que la cobertura se haya evaluado con un diseño temporal adecuado y sus resultados respalden esa afirmación.

### 4.3 Qué mostrar cuando existe una medición anterior

La cifra principal puede seguir siendo la de los agentes por decisión de producto. Sin embargo, la interfaz debe hacer visible que:

- la salida es una simulación experimental;
- existe una medición comparable anterior, si efectivamente existe;
- se puede consultar su fecha, fuente y valor;
- las pruebas actuales favorecen la persistencia en ese tipo de problema, cuando así lo indican los resultados.

No es imprescindible que el dato histórico tenga el mismo tamaño visual que la cifra de los agentes, pero no se debe ocultar esa evidencia de la documentación metodológica ni dar a entender que el método elegido es el que mejor predice.

### 4.4 Texto recomendado para una pregunta política sin datos

> **Estimación exploratoria: [X]%**  
> Esta cifra procede de una simulación de perfiles con IA; no procede de una encuesta actual. No se encontró una medición comparable que permita verificar directamente el resultado para esta pregunta y fecha. En pruebas históricas de preguntas políticas nunca medidas, el sistema tuvo un error absoluto medio de [valor] puntos porcentuales en [n] casos. Este desempeño pasado no garantiza la precisión de esta estimación.

La página puede entregar siempre un número, pero debe evitar presentar el resultado como “el porcentaje de Bogotá que piensa X” o “la aprobación actual de X” si no existe una medición que respalde esa interpretación.

## 5. Fase 1: validar los intervalos con la EPC 2014–2025

**Prioridad:** primera tarea técnica.  
**Costo de API:** USD 0 para el análisis estadístico.

La serie anual de gestión del alcalde y del Concejo desde 2014 ofrece más puntos de evaluación que la prueba que reservó únicamente 2025. Se debe aprovechar sin asumir que doce años o diez transiciones resuelven por completo el problema de muestras pequeñas.

### 5.1 Preparar series comparables

Para cada pregunta, construir una tabla con:

- identificador estable de la pregunta;
- texto exacto por año;
- opciones de respuesta y definición del porcentaje publicado;
- fecha de campo;
- año de la medición;
- tema o dominio;
- indicador de cambios de cuestionario;
- porcentaje observado;
- fuente y notas metodológicas.

No tratar automáticamente como idénticas preguntas cuyo texto, opciones, orden, población o tratamiento de “no sabe” cambió de manera relevante. Marcar la comparabilidad como `alta`, `media` o `baja` y definir la regla antes de observar los errores de predicción.

### 5.2 Validación de origen móvil

Evaluar cada año objetivo utilizando exclusivamente la información disponible antes de esa ola:

1. Para predecir el año `t`, usar únicamente mediciones y errores conocidos hasta `t-1`.
2. Calcular la predicción de persistencia con la última observación comparable.
3. Construir el intervalo a partir de errores históricos disponibles hasta `t-1`.
4. Comparar el intervalo con el valor observado en `t`.
5. Repetir para cada año posible con suficiente historial.

El tamaño y nivel del intervalo deben fijarse antes de correr la evaluación. No se permite usar el error de 2025 para calibrar un intervalo que luego se evalúa en 2025.

### 5.3 Desgloses obligatorios

Reportar, al menos:

- cobertura empírica total;
- cobertura por dominio;
- cobertura para gestión del alcalde y Concejo;
- ancho medio y mediano de los intervalos;
- error absoluto medio de la persistencia;
- resultados por año objetivo;
- cantidad de casos en cada grupo;
- cantidad y tratamiento de cambios de cuestionario.

La cobertura debe leerse junto con el ancho: rangos muy amplios pueden cubrir casi todo sin ofrecer información útil. No afirmar que la cobertura futura está garantizada solo porque la cobertura histórica se acerque a un objetivo.

### 5.4 Años movidos y muestras pequeñas

Predefinir un análisis de sensibilidad para años con errores excepcionalmente altos. Por ejemplo, comparar la cobertura general con la cobertura excluyendo cada año por turno, sin seleccionar retrospectivamente la versión que parezca mejor.

Se pueden comparar tres reglas de rango:

- percentil de errores históricos disponibles hasta ese momento;
- percentil histórico con agrupación parcial por dominios, si el tamaño de muestra es suficiente;
- regla conservadora que ensancha el rango cuando el dominio tiene pocos casos o la comparabilidad histórica es débil.

No se debe prometer una cobertura del 80% hasta disponer de evidencia que la respalde. Si la muestra es demasiado pequeña, comunicar el rango como “referencia empírica provisional” y presentar su cobertura histórica observada con el número de casos.

## 6. Fase 2: registro mínimo de encuestas públicas

**Prioridad:** en paralelo con la Fase 1.  
**Costo de API:** puede ser cero; la extracción inicial puede requerir trabajo manual.

No se intentará crear de inmediato una base exhaustiva de todas las encuestas colombianas. El piloto comenzará con las mediciones públicas de imagen, aprobación o evaluación de la gestión de Galán, separando los conceptos que no sean equivalentes.

### 6.1 Campos mínimos

Cada registro debe incluir:

- encuestadora y nombre del estudio;
- URL de la fuente primaria y, si existe, de la ficha técnica;
- fecha de publicación;
- fechas de trabajo de campo;
- texto exacto de la pregunta;
- concepto medido: aprobación, imagen favorable/desfavorable, evaluación de gestión u otro;
- población objetivo y ámbito geográfico;
- tamaño de muestra total y de la submuestra de Bogotá, cuando corresponda;
- método de recolección;
- ponderaciones o diseño muestral, si está documentado;
- opciones y porcentaje de cada opción;
- tratamiento de “no sabe/no responde”;
- precisión publicada, si existe;
- cambios o dudas de comparabilidad;
- responsable y fecha de verificación manual.

### 6.2 PDFs de imágenes

Si un informe de Invamer está disponible únicamente como PDF de imágenes y la extracción automática falla, registrar manualmente los campos esenciales desde el informe original o una nota de prensa verificable. Marcar cada dato como `verificado en informe`, `verificado en nota de prensa` o `pendiente de verificación`.

No inferir fechas de campo a partir de la fecha de publicación ni reconstruir cifras que no estén visibles en una fuente verificable.

### 6.3 No mezclar series no equivalentes

Las series disponibles tienen poco solapamiento temporal: Invamer mide aprobación en una serie bimestral de 2024–2025, CB mide imagen en 2026, Guarumo aporta un punto y la EPC es anual. Por tanto:

- no promediar automáticamente aprobación e imagen;
- no interpretar diferencias entre encuestadoras como cambio real sin considerar diseño, población, pregunta y fechas;
- no ajustar por un efecto de encuestadora con un solo punto o sin solapamiento suficiente;
- documentar las mediciones aunque todavía no sea posible agregarlas.

## 7. Fase 3: experimento barato para los agentes de Galán

**Prioridad:** después de iniciar las fases 1 y 2.  
**Costo máximo inicial estimado:** USD 0,50–1,00 para 10–20 preguntas con 200 agentes en una variante adicional, usando el costo informado de USD 0,05 por pregunta.

### 7.1 Hipótesis

Un contexto numérico y temporal estructurado podría ayudar a los agentes a distinguir su punto de partida histórico de la evidencia disponible para actualizarlo. La hipótesis es nueva y no debe confundirse con la prueba anterior de resumir noticias, que no mejoró los resultados.

### 7.2 Diseño

Antes de ejecutar, preregistrar:

- lista de preguntas elegibles;
- fechas de corte;
- criterios de comparabilidad;
- fuentes públicas admisibles;
- prompts exactos;
- método de agregación y pesos;
- métrica principal;
- análisis por año y tema;
- regla de aceptación o descarte.

Comparar tres métodos sobre las mismas preguntas y fechas:

1. persistencia;
2. sistema de agentes actual;
3. agentes con contexto estructurado.

El contexto puede incluir la última respuesta histórica del perfil, su fecha y datos públicos verificables que ya existían a la fecha de corte. Debe distinguir claramente hechos observados de interpretaciones. No se deben inventar experiencias ni actitudes individuales para forzar una actualización.

### 7.3 Evaluación y regla de decisión

La métrica principal será el error absoluto medio en puntos porcentuales. También se reportará el sesgo medio y los resultados por año. La variante solo se conserva si mejora frente a la persistencia en un conjunto reservado y no debe depender de uno o dos casos excepcionales.

Si no supera la persistencia, se documenta el resultado y se detiene la línea de experimentación. No ampliar el panel ni añadir más contexto automáticamente.

### 7.4 Privacidad

No incluir respuestas individuales de las encuestas políticas propias en prompts, archivos adjuntos, herramientas o llamadas a modelos de lenguaje. Las pruebas deben operar con la EPC permitida, datos públicos y resultados agregados admisibles. Si se necesita usar algún resumen interno, verificar que no contenga respuestas individuales o información que permita reconstruirlas.

## 8. Fase 4: decidir si vale la pena agregar encuestas

**Prioridad:** posterior al registro de fuentes; no ejecutar un promedio complejo aún.

Antes de agregar, determinar si existen mediciones suficientemente comparables y con solapamiento temporal.

### 8.1 Candidatos para una futura prueba

- último dato comparable;
- media simple de mediciones comparables;
- promedio ponderado por antigüedad;
- promedio ponderado por precisión publicada, si la precisión es comparable y está disponible;
- modelo con efectos de encuestadora, solo si hay suficiente solapamiento para estimarlos.

No escoger la regla mirando cuál obtiene el menor error sobre los mismos casos que luego se reportan como prueba. Si hay datos suficientes, ajustar pesos en años o encuestadoras de entrenamiento y probarlos en fechas posteriores reservadas.

### 8.2 Condiciones mínimas antes de agregar

- correspondencia conceptual razonable entre preguntas;
- población objetivo comparable o ajuste explícito y justificable;
- fechas de campo disponibles;
- tratamiento transparente de diferencias de metodología;
- suficientes mediciones superpuestas para estimar cualquier ajuste;
- evaluación frente a persistencia y a cada fuente por separado.

Si estas condiciones no se cumplen, mantener el registro y mostrar las mediciones separadas con sus fechas y fuentes. La falta de datos para agregar no debe resolverse con ponderaciones arbitrarias.

## 9. Decisiones sobre las fases C y E anteriores

### Fase C: modelo de relaciones entre preguntas

No es prioritaria para estimar el nivel de una pregunta que nunca fue respondida por nadie. Un modelo factorial puede aprender dimensiones latentes y ayudar a repartir una cifra conocida por grupos, pero no identifica por sí solo el porcentaje total de una pregunta completamente nueva sin un ancla observada o supuestos adicionales.

Retomarla solo si hay un caso de uso explícito de desagregación por grupos/localidades y se puede evaluar fuera de muestra. La prueba debe comparar el reparto estimado con el observado y contrastarlo con una alternativa simple que asigne a todos los grupos el total de la ciudad. No retomar solo por el deseo general de mejorar la predicción.

### Fase E: calibración de probabilidades o aumento del panel

No retomarla todavía de forma general. El resultado de `λ = 0` sugiere que los agentes no añadieron señal suficiente al predictor de persistencia en esas pruebas, aunque no demuestra que nunca puedan servir en otros escenarios.

Primero realizar el experimento acotado de contexto estructurado. Solo después considerar calibración de probabilidades, paneles mayores o auxiliares electorales, siempre con una hipótesis separada y una comparación preregistrada frente a la persistencia.

## 10. Reglas de preregistro y reporte

Antes de cada experimento guardar un documento con:

- hipótesis y mecanismo esperado;
- datos permitidos y fechas de corte;
- unidad de análisis y criterios de exclusión;
- método base y competidores;
- prompts, parámetros y versiones de modelo;
- métrica primaria y métricas secundarias;
- partición entrenamiento/prueba;
- regla exacta para aceptar o descartar;
- costo máximo de API;
- riesgos de filtración temporal;
- responsable y fecha del preregistro.

El reporte final debe incluir también resultados negativos, tamaño de muestra, error del método de persistencia y cualquier desviación del protocolo. No elegir posteriormente solo los temas o años que favorecen una variante.

Si una regla del producto impide conservar el registro de cada consulta, separar el registro permanente de mediciones públicas de un conjunto de pruebas controlado. Las consultas de usuarios no necesitan convertirse en registros personales para poder mantener un protocolo reproducible en evaluaciones históricas.

## 11. Orden de ejecución recomendado

| Orden | Trabajo | Motivo | Costo de API aproximado |
|---|---|---|---:|
| 0 | Corregir etiquetas, descripción del error y afirmaciones de cobertura | Reduce el riesgo de que una simulación se confunda con una encuesta validada | USD 0 |
| 1 | Validar intervalos con EPC 2014–2025 usando origen móvil | Hay datos disponibles y el problema de cobertura afecta directamente la interpretación | USD 0 |
| 2 | Crear un registro mínimo de encuestas públicas de Galán | Ordena la evidencia antes de intentar combinar series poco solapadas | USD 0 en API; trabajo manual posible |
| 3 | Ejecutar experimento de contexto numérico estructurado | Prueba una modificación concreta y barata de los agentes | USD 0,50–1,00 estimados |
| 4 | Revaluar agregación de encuestas cuando haya datos comparables | Evita ajustar pesos con muy pocos casos | Depende del método; puede ser USD 0 |
| 5 | Decidir si se retoman C o E | Solo si aparece un caso de uso o evidencia que lo justifique | No asignar presupuesto antes del diseño |

## 12. Criterios para considerar que el plan está funcionando

El plan no se considera exitoso simplemente porque la página siempre entrega una cifra o porque mejora la presentación visual. Debe evaluarse según criterios verificables:

- la página distingue claramente estimaciones simuladas y mediciones reales;
- el error histórico se comunica sin confundirlo con un margen de error o una garantía;
- las afirmaciones de cobertura están respaldadas por pruebas retrospectivas y acompañadas por el número de casos;
- cada variante nueva se compara con la persistencia bajo reglas preregistradas;
- las encuestas públicas tienen fuentes, fechas de campo y metadatos rastreables;
- no se envían respuestas individuales de las encuestas políticas propias a modelos de lenguaje;
- las variantes que no superan la vara se documentan y no se promocionan como mejoras demostradas.

## 13. Referencias y límites

Este plan se basa principalmente en los resultados experimentales descritos por el equipo en `RESULTADOS_PLAN_MEJORAS_PARA_IA.md`. Los valores de error, tamaño de las pruebas y resultados por fase deben conservarse como datos del propio proyecto y no extrapolarse más allá de lo que permiten sus muestras.

La recomendación de separar error medio, percentiles de error y cobertura de intervalos es una distinción estadística general. Los detalles exactos de la cobertura futura no pueden darse por establecidos sin la validación retrospectiva propuesta.

Las decisiones de producto de mostrar una cifra siempre y mantener los agentes activos se respetan en este plan, pero no equivalen a evidencia de que la cifra tenga precisión suficiente para cada pregunta.
