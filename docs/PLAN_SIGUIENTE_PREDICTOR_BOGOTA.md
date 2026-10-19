# Siguiente plan del predictor de opinión pública de Bogotá

**Versión:** 2.0  
**Fecha:** 19 de octubre de 2026  
**Base:** resultados de `RESULTADOS_PLAN_MEJORAS_PARA_IA.md`  
**Objetivo:** acercarse a la opinión actual de Bogotá para preguntas políticas locales nuevas, respetando el preregistro, el presupuesto limitado y la regla de que las respuestas individuales de las encuestas políticas propias no se envían a modelos de lenguaje.

---

## 1. Conclusión ejecutiva

Los resultados exigen cambiar el enfoque. La persistencia ganó a los métodos temporales sencillos y a las combinaciones con agentes en las pruebas reportadas. En 81 preguntas con años reservados, la combinación `P + λ(G − P)` eligió `λ = 0`; la persistencia anual tuvo MAE de 4,3 puntos en 144 pares EPC, pero llegó a 7,0 en gobierno e instituciones y a 6,1 en el tramo 2024 → 2025. Los agentes sí mostraron utilidad en dos escenarios concretos: ocultar una pregunta dentro de la misma ola y trasladar información de una encuesta nacional a Bogotá.

**Decisión propuesta:** no seguir buscando una combinación general de agentes y persistencia. Construir primero una infraestructura de evidencia pública comparable, agregar encuestas solo cuando midan el mismo concepto y presentar una cifra con un intervalo que crezca con la antigüedad y la incertidumbre.

Para una pregunta política local nunca medida, sin encuestas comparables ni indicadores predictivos validados, no hay base suficiente para prometer una cifra precisa de hoy. En ese caso el producto debe presentar una estimación exploratoria de baja confianza o decir que no existe información suficiente para dar una estimación informada.

## 2. Separar claramente tres tipos de consulta

### Tipo A — Pregunta ya medida en Bogotá

1. Mostrar la medición comparable más reciente y su fecha de campo.
2. Si hay varias encuestas recientes que midan el mismo concepto, mostrar también un agregado de esas encuestas, siempre que superen las reglas de comparabilidad descritas abajo.
3. Usar la persistencia como benchmark obligatorio.
4. Incluir un intervalo de incertidumbre asociado con antigüedad, variación entre encuestadoras y errores históricos del dominio.

### Tipo B — Pregunta no medida, pero relacionada con conceptos medidos

1. Identificar de antemano las preguntas y variables que se consideran relacionadas; no aceptar únicamente una similitud semántica elegida por el modelo para cada caso.
2. Usar la regresión o el modelo de transferencia solo si supera retrospectivamente a una referencia simple en preguntas ocultas.
3. Mantener a los agentes como método candidato, no como opción predeterminada.
4. Ensanchar el intervalo porque el resultado es una transferencia hacia un concepto no medido.

### Tipo C — Pregunta política local nueva y sin indicadores adecuados

1. Buscar primero encuestas públicas comparables o parcialmente comparables.
2. Si no existen, no fingir que los perfiles demográficos revelan la opinión actual.
3. Si se muestra una estimación exploratoria de agentes, mostrarla por separado, señalar su error histórico para esa clase y dejar claro que no supera necesariamente a la persistencia.
4. El producto debe permitir declarar «información insuficiente para una estimación confiable».

---

## 3. Paso 1 — Crear un registro de encuestas públicas con trazabilidad

**Prioridad: máxima. Coste de API: cero o muy bajo.**

### Qué construir

Una tabla persistente de mediciones, con una fila por pregunta, respuesta y encuesta publicada. Campos mínimos:

- Encuestadora y entidad que financia o publica el estudio.
- Enlace al informe original y a la ficha técnica.
- Fecha de publicación y fechas de trabajo de campo.
- Población objetivo: Bogotá, nacional, probables votantes, adultos, etc.
- Tamaño de muestra total y tamaño de la submuestra de Bogotá, si aplica.
- Método de selección, modo de entrevista, ponderaciones y margen de error, cuando se publiquen.
- Texto exacto de la pregunta, opciones de respuesta, orden y denominador del porcentaje.
- Variable/concepto normalizado, manteniendo el texto original.
- Porcentaje reportado, categoría de respuesta y método de cálculo.
- Indicadores de comparabilidad y alertas sobre datos faltantes.

**Punto de partida útil:** Bogotá Cómo Vamos publica un tablero con más de 100 preguntas de la EPC y series desde 2014, además de desagregaciones por zona, género, estrato y edad. También se deben revisar las publicaciones originales y fichas técnicas de las encuestadoras, no depender de notas periodísticas que puedan omitir detalles metodológicos.

### Reglas de comparabilidad

Asignar una categoría manual o semiautomática que luego sea revisada:

- **A — Comparable:** mismo concepto, población, pregunta/opciones y denominador suficientemente similares.
- **B — Aproximada:** concepto parecido, pero con diferencias de población, redacción, opciones o modo; solo incluir en un análisis separado o con ajuste explícito validado.
- **C — No comparable:** por ejemplo, imagen favorable/desfavorable frente a aprobación de la gestión, o una pregunta nacional frente a una bogotana sin un método de transferencia validado.

No promediar automáticamente indicadores de «imagen», «favorabilidad» y «aprobación»: deben tener series independientes hasta que exista evidencia de que pueden equipararse.

### Control de calidad

- Detectar duplicados cuando el mismo estudio aparece en varios medios.
- Conservar una única observación por publicación/medición, no por cada sitio donde se republicó.
- Guardar por separado la fecha de campo y la fecha de publicación.
- Registrar cambios de cuestionario como rupturas potenciales de serie.
- Incluir la fuente y fecha de consulta para que otro analista pueda reconstruir cada cifra.

### Prueba preregistrada

Tomar las series con varias mediciones y simular la fecha de corte: para cada fecha histórica, usar solo publicaciones disponibles hasta ese día y predecir la medición objetivo posterior. Comparar contra la persistencia de la misma pregunta y contra una media simple de encuestas comparables.

**Regla de éxito:** el agregado no se incorpora como estimación principal si no reduce el MAE frente a persistencia de forma estable en pruebas walk-forward y sin depender de una sola serie o encuestadora.

---

## 4. Paso 2 — Agregar encuestas comparables con un modelo sencillo y conservador

**Prioridad: máxima para aprobación/imagen de Galán. Coste de API: cero.**

### Candidatos iniciales

Comparar, sin ajustar en la prueba final, cuatro métodos de complejidad creciente:

1. Última medición comparable.
2. Promedio simple de las encuestas comparables dentro de una ventana temporal preregistrada.
3. Promedio ponderado por actualidad y precisión, sin corrección por encuestadora.
4. Meta-análisis de efectos aleatorios o modelo temporal que reconozca diferencias entre encuestas y la antigüedad de cada observación.

No suponer que el método más elaborado será mejor. Elegir con pruebas retrospectivas.

### Esquema de ponderación candidato

Para un primer modelo, comparar una ponderación por recencia con una ponderación que tenga en cuenta la incertidumbre de cada medición. Una forma general es:

`peso_i ∝ recencia_i / (varianza_muestral_i + varianza_entre_encuestas + varianza_temporal_i)`

La recencia puede evaluarse con varias vidas medias predefinidas, por ejemplo 30, 60 y 90 días. No escoger la vida media mirando los resultados de prueba: seleccionarla en años/series de entrenamiento y evaluarla después en un periodo reservado.

La varianza muestral no siempre está disponible o es interpretable, en particular en muestras no probabilísticas. En esos casos no inventar un margen de error: marcar la limitación y evaluar pesos alternativos predefinidos.

### Efectos de encuestadora

**No estimaría todavía efectos de casa complejos.** Con 19 mediciones del alcalde de cuatro encuestadoras hay muy pocos datos para separar el sesgo de la firma de cambios reales, diferencias de pregunta y ruido. Si más adelante se estiman efectos, deben encogerse fuertemente hacia cero (regularización/hierarchical Bayes) y aprenderse solo de mediciones suficientemente comparables, incluidas las realizadas aproximadamente en las mismas fechas.

No ajustar una encuestadora porque una sola encuesta esté por encima o por debajo de otra. Puede ser un cambio real en fechas de campo, no un sesgo sistemático.

### Comparación preregistrada

- **Unidad temporal:** una predicción por pregunta-fecha; nunca usar una encuesta publicada después de la fecha simulada.
- **Benchmark obligatorio:** persistencia.
- **Métricas:** MAE, mediana del error absoluto, sesgo firmado y cobertura del intervalo.
- **Robustez:** reportar resultados globales y por dominio; hacer análisis dejando fuera cada encuestadora por turno.
- **Regla de adopción:** exigir mejora en más de una ventana temporal y que no dependa de una sola firma o de un único episodio. Si la diferencia es pequeña frente a la variación de los errores, conservar el método más simple.

---

## 5. Paso 3 — Tratar las noticias como señales candidatas, no como instrucciones para los agentes

**Prioridad: media; solo tras el registro de encuestas. Coste de API: bajo.**

Los resultados anteriores muestran que un resumen narrativo de noticias empujó las respuestas en una dirección pesimista y empeoró el error. No repetiría ese diseño.

### Diseño alternativo

1. Crear un registro estructurado de eventos e indicadores con fecha verificable: por ejemplo, seguridad registrada, avance o interrupciones de proyectos, tiempos de viaje, hechos de gestión y cambios presupuestales.
2. Vincular cada indicador solo a preguntas que conceptualmente pueda afectar.
3. Definir el signo, el rezago temporal y la transformación del indicador usando únicamente datos de entrenamiento.
4. Estimar si históricamente el indicador anticipa cambios posteriores de opinión.
5. Permitir una corrección solo si la relación se sostiene en pruebas fuera de muestra y añade valor frente a persistencia.

La IA puede extraer la fecha, clasificar el tema o localizar una fuente; no debe decidir libremente cuántos puntos cambia la opinión ni asumir que una noticia negativa produce necesariamente más pesimismo.

### Prueba preregistrada

Recrear un pronóstico histórico usando solo los datos publicados antes del campo de la encuesta objetivo. Comparar: persistencia, persistencia + indicador estructurado y resumen narrativo. No realizar la prueba usando indicadores que incorporen información del periodo de destino.

**Regla de abandono:** si los indicadores no superan a persistencia repetidamente, no actualizar el pronóstico con ellos. Una narrativa convincente no es evidencia predictiva.

---

## 6. Paso 4 — Crear intervalos honestos, especialmente para años movidos

**Prioridad: máxima para la credibilidad del producto. Coste de API: cero.**

Los intervalos actuales fallaron la cobertura de prueba: el percentil 80 histórico cubrió solo el 38 % de las preguntas de gobierno en el año reservado y el 65 % del resto. Por tanto, no deben etiquetarse como intervalos calibrados al 80 % en el producto.

### Diseño

1. Guardar residuos históricos: `error = valor observado − predicción`, separados por método, dominio, antigüedad de la última medición y tipo de pregunta.
2. Para cada consulta, seleccionar una clase con suficiente información; evitar crear celdas diminutas, como un grupo específico con apenas dos o tres errores.
3. Usar estimaciones agrupadas con regularización: los grupos pequeños se acercan a la distribución más amplia de su dominio, en vez de estimar percentiles propios poco estables.
4. Calcular un intervalo a partir de errores absolutos históricos y añadir una regla conservadora para evidencia vieja o con señales de cambio rápido.
5. Evaluar la cobertura mediante pruebas rolling-origin: calibrar con el pasado, congelar el método y evaluar el periodo siguiente.
6. Reportar junto al intervalo su base empírica, número de errores de validación y antigüedad del dato utilizado.

### Tratamiento de cambios de régimen

Un año movido puede quedar fuera de la distribución histórica. Con tan pocos años no es posible estimar con precisión la probabilidad de un shock de ese tipo. Para mitigar el problema:

- Usar intervalos más anchos para gobierno e instituciones que para dimensiones más estables, salvo que nueva evidencia justifique lo contrario.
- Aumentar la cautela cuando el dato tenga un año de antigüedad o más.
- Incluir un indicador de «riesgo de cambio» solo si sus reglas son verificables y preregistradas.
- Si existe una ruptura de cuestionario, conflicto entre encuestas o un acontecimiento importante sin precedentes en los datos, activar una alerta de baja confiabilidad y no fingir una cobertura nominal.

**Importante:** conformal prediction o los percentiles de errores no garantizan cobertura condicional en un año de shock si cambia la distribución de los errores. Con los datos actuales, mostraría rangos conservadores y transparentes, sin prometer una cobertura del 80 % hasta verificarla en más periodos.

### Salida recomendada para la página

- Estimación central.
- «Último dato comparable: [fecha de campo]».
- «Error histórico típico de esta clase: [valor]».
- «Rango orientativo, no garantía de cobertura: [límite inferior–superior]».
- Etiqueta explicativa: dato reciente / dato antiguo / concepto no medido / fuentes públicas discrepantes.

---

## 7. Paso 5 — ¿Retomar la Fase C? Sí, pero solo para distribución por grupos después de tener el total

**Prioridad: baja; no resuelve el porcentaje total de una pregunta jamás medida.**

La conclusión del informe es correcta: si nadie respondió una pregunta, un modelo factorial de respuestas previas no conoce por sí solo su nivel agregado. Puede aprender relaciones entre actitudes y ayudar a repartir una cifra previamente estimada entre grupos, pero no crear la cifra que falta.

### Cuándo vale la pena

Retomar la Fase C solamente si el producto necesita estimaciones por sexo, edad, estrato o localidad y si las encuestas disponibles proporcionan una cifra agregada o suficientes datos de esa pregunta para anclar el modelo.

### Diseño de prueba

1. Usar exclusivamente microdatos EPC donde las respuestas sí se observaron y las variables demográficas estén disponibles.
2. Entrenar un modelo jerárquico/MRP o una alternativa más sencilla para estimar porcentajes por grupo.
3. Ocultar de forma completa la respuesta objetivo en una ola o una pregunta de validación, respetando el diseño de la encuesta.
4. Comparar el error de los porcentajes por grupo con el baseline de asignar a cada grupo el porcentaje de Bogotá, que ya se probó como competitivo.
5. Evaluar tamaños efectivos por celda y agrupar categorías pequeñas para evitar estimaciones inestables.
6. No liberar estimaciones de grupos sin evidencia de mejora y sin advertir cuando provienen de pocos encuestados.

**Criterio de continuación:** la mejora debe verse en olas o preguntas reservadas, no solo en la reconstrucción del conjunto de entrenamiento. Si vuelve a perder frente al porcentaje general para todos los grupos, dejar la Fase C aplazada.

---

## 8. Paso 6 — ¿Retomar la Fase E? Solo para casos en los que los agentes ya demostraron valor

**Prioridad: baja y selectiva. No ampliar de entrada el panel.**

Los datos muestran que los agentes pueden aportar algo cuando se oculta una respuesta dentro de la misma ola y cuando se intenta trasladar una encuesta nacional hacia Bogotá. Pierden, en general, al estimar cambios posteriores y preguntas nuevas para las que no hay evidencia suficiente.

### Experimento pequeño recomendado

Antes de recalibrar todos los agentes, seleccionar un único caso de uso: transferencia nacional → Bogotá, donde existe evidencia previa de utilidad.

1. Ejecutar los agentes con perfiles y reglas congelados.
2. Calibrar, si es posible, solamente con errores agregados históricos del mismo tipo de tarea, nunca con respuestas individuales de las encuestas políticas propias enviadas al LLM.
3. Entrenar la calibración con periodos/preguntas anteriores y evaluarla en un periodo reservado.
4. Comparar con copiar la encuesta nacional y con la persistencia local cuando exista una medición local comparable.
5. Mantener el resultado de agentes fuera de la estimación principal si no mejora el error fuera de muestra.

### Qué no haría todavía

- No aumentaría de 200 a 1.520 agentes hasta demostrar que la variabilidad de la muestra o del muestreo de inferencia es una causa importante del error.
- No obligaría a los agentes a acercarse a la encuesta mediante instrucciones de texto: las pruebas anteriores empeoraron.
- No calibraría para igualar un total conocido como solución general: ya se observó que puede no mejorar el reparto por grupos y empeorar fuera de muestra.
- No usaría automáticamente resultados electorales por mesa como sustituto de opiniones actuales. Las relaciones electorales pueden ser variables auxiliares en un modelo separado, pero requieren validación específica y cuidado con la falacia ecológica.

**Coste:** 200 agentes cuestan aproximadamente USD 0,05 por pregunta, según los costos reportados. Un panel más grande solo se justifica después de un experimento de sensibilidad que demuestre una ganancia relevante.

---

## 9. Protocolo obligatorio para cada prueba nueva

Antes de ejecutar, registrar:

- Pregunta y dominio.
- Clase de consulta (A, B o C).
- Fecha de corte y fuentes que estaban disponibles en esa fecha.
- Baseline de persistencia y candidatos exactos.
- Método de separación de entrenamiento y prueba.
- Métrica primaria (MAE en puntos porcentuales) y métricas secundarias (mediana del error, sesgo, cobertura).
- Regla de éxito, regla de abandono y coste máximo.
- Criterios de comparabilidad y tratamiento de datos faltantes.

Después de la prueba, publicar el resultado agregado de la evaluación al equipo, incluso si no mejora. Las encuestas políticas propias no deben enviar sus respuestas individuales a modelos de lenguaje; los análisis de sus datos deben permanecer dentro de los sistemas autorizados del equipo.

## 10. Orden recomendado de trabajo

1. **Primero:** construir el registro de mediciones públicas y estandarizar pregunta, población, fechas de campo, fuente y ficha técnica.
2. **Segundo:** evaluar agregados de encuestas comparables frente a persistencia mediante predicciones walk-forward, empezando por imagen/aprobación del alcalde.
3. **Tercero:** corregir la presentación de incertidumbre: antigüedad visible, error histórico por tipo de consulta y rangos explícitamente orientativos hasta demostrar cobertura.
4. **Cuarto:** explorar indicadores estructurados únicamente cuando exista una hipótesis predictiva verificable; no volver a usar resúmenes de noticias como ajuste directo.
5. **Quinto:** reabrir la Fase E solo para transferencias nacional → Bogotá; mantener la Fase C aplazada salvo necesidad concreta de desagregación por grupos.

## 11. Referencias y recursos

- **Bogotá Cómo Vamos — Datos EPC:** https://bogotacomovamos.org/datos/  
  El sitio ofrece un tablero de más de 100 preguntas y series desde 2014 con desagregaciones por zona, género, estrato y edad.
- **AAPOR — A Journalist’s Guide to Understanding Polls & Surveys:** https://aapor.org/journalist-guide-to-understanding-polls-surveys/  
  Resume por qué deben revisarse redacción exacta, población, método y fecha de campo antes de comparar encuestas.
- **FiveThirtyEight / ABC News — How Our Polling Averages Work:** https://fivethirtyeight.com/methodology/how-our-polling-averages-work/  
  Como referencia metodológica histórica sobre ponderación por actualidad, ajustes de encuestadora y regularización; no copiar sus parámetros estadounidenses sin validación local.

---

## Conclusión

El objetivo inmediato no debería ser que los agentes «adivinen mejor». Debería ser dar la mejor cifra disponible **sin ocultar de dónde viene ni cuánto puede equivocarse**. Para preguntas medidas, la prioridad es conseguir y armonizar datos recientes. Para preguntas no medidas, solo se debe transferir información cuando haya una relación validada. Para preguntas políticas locales totalmente nuevas, el límite puede ser una estimación exploratoria con incertidumbre alta. Reconocer ese límite es preferible a producir una cifra con apariencia de precisión que los experimentos no respaldan.
