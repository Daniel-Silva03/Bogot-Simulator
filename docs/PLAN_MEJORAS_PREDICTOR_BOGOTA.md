# Plan de implementación para mejorar el predictor de opinión pública de Bogotá

**Versión:** 1.0  
**Fecha:** 19 de octubre de 2026  
**Base:** contexto técnico y resultados de pruebas descritos en `PROMPT_IDEAS_PREDICTOR.md`.

## 1. Objetivo y principio de diseño

Construir un predictor híbrido que estime qué respondería hoy la población de Bogotá ante preguntas nuevas de actualidad, especialmente sobre política local, gestión del alcalde e instituciones. El sistema debe aprovechar las mediciones disponibles, incorporar información reciente cuando aporte señal y utilizar agentes de IA únicamente cuando las pruebas demuestren que agregan valor.

La meta no es que el modelo genere una respuesta convincente, sino minimizar el error medido fuera de muestra. Cada método nuevo debe competir con una referencia difícil: **repetir el último dato medido comparable**.

### Qué sugieren las pruebas actuales

- Los agentes reconstruyeron algunas preguntas conocidas mejor que la regresión actual, pero eso no demuestra que predigan cambios de opinión.
- En la prueba retrospectiva EPC 2024 → EPC 2025, repetir el dato anterior tuvo un error de 7,7 puntos, frente a 10,1 con agentes y resumen de noticias.
- Para la imagen de Galán comparada con CB en septiembre de 2026, repetir la EPC 2025 tuvo un error de 0,5 puntos. En ese caso, usar perfiles y agentes no fue necesario para obtener un buen resultado.
- Los agentes sí parecieron aportar valor cuando el punto de referencia disponible era una encuesta nacional y el objetivo era Bogotá, como en la segunda vuelta presidencial de 2026.
- Igualar el porcentaje total de una encuesta mediante calibración no mejoró la distribución por grupos ni el desempeño fuera de muestra.
- Las respuestas individuales de las encuestas políticas propias **no se pueden enviar a ningún modelo de lenguaje**. Esta restricción aplica a prompts, archivos, herramientas externas y servicios de terceros.

Estas observaciones hacen recomendable desarrollar primero un mecanismo para seleccionar y combinar métodos, antes de aumentar el número de agentes.

## 2. Arquitectura propuesta

El flujo objetivo debe separar seis componentes:

1. **Interpretación de la pregunta:** identificar tema, población, territorio, periodo, opciones de respuesta y si existe una pregunta comparable.
2. **Repositorio de evidencia:** buscar mediciones previas, encuestas públicas agregadas, indicadores relevantes y su fecha efectiva de disponibilidad.
3. **Métodos candidatos:** persistencia, regresión, modelo conjunto de respuestas EPC, modelo temporal y agentes.
4. **Selector/combinador:** elegir o ponderar los métodos con reglas aprendidas únicamente de validaciones históricas.
5. **Estimación de incertidumbre:** comunicar la confiabilidad empírica para casos parecidos y detectar preguntas fuera del alcance.
6. **Registro de auditoría:** guardar la predicción, las fuentes usadas, la versión del código/modelo, la fecha de corte y el resultado cuando se conozca.

### Flujo de predicción

```text
Pregunta nueva
    ↓
Clasificar tema, población, periodo y tipo de respuesta
    ↓
Buscar equivalentes, mediciones recientes e indicadores disponibles
    ↓
Calcular predicciones candidatas
    ├── Última medición comparable
    ├── Regresión actual
    ├── Modelo de relaciones entre preguntas
    ├── Actualización temporal
    └── Agentes, cuando estén justificados
    ↓
Selector validado fuera de muestra
    ↓
Estimación final + intervalo de incertidumbre + diagnóstico de soporte
    ↓
Guardar predicción antes de observar el resultado
```

## 3. Reglas comunes de evaluación

Antes de desarrollar los métodos nuevos, fijar un protocolo que impida que una mejora aparente provenga de filtraciones de información o de haber elegido el método después de conocer el resultado.

### 3.1 Separar dos problemas

**Problema A: pregunta ya medida.** Se busca predecir una nueva medición de una pregunta previamente observada. La referencia principal es repetir la última medición comparable.

**Problema B: pregunta nunca medida.** Se busca predecir una pregunta nueva a partir de otras preguntas, características semánticas, datos auxiliares o agentes. En este caso no siempre existe una referencia de persistencia directa. Debe compararse con las mejores alternativas disponibles: regresión actual, predicción neutral previamente definida y, cuando pueda construirse una comparación válida, un proxy histórico bien especificado.

No reportar el error de A y B como si fueran un único problema. Informar los resultados por separado y por dominio (ciudad, gestión del alcalde, instituciones, política nacional, intención de voto).

### 3.2 Métricas

- **Métrica principal:** error absoluto medio (MAE) en puntos porcentuales, usando el mismo cálculo para todos los métodos.
- **Métricas secundarias:** sesgo medio (sobre/subestimación), error por pregunta y por dominio; Brier o log-loss si se guardan probabilidades por opción; cobertura de los intervalos de incertidumbre.
- **Resultados electorales multiclase:** error por candidato y una métrica agregada predefinida. No cambiar la métrica después de ver cuál favorece a un método.
- **Incertidumbre:** reportar por separado el error del punto estimado y la cobertura del intervalo. Un intervalo más amplio no mejora el punto pronosticado, pero puede ser una señal más honesta de riesgo.

### 3.3 Separación entre ajuste y evaluación

- No dividir aleatoriamente filas de una misma pregunta si sus observaciones de distintos años pueden filtrarse entre entrenamiento y prueba.
- Reservar preguntas completas, años completos o familias de preguntas, según el experimento.
- En pruebas temporales, usar solamente información que habría estado disponible en la fecha de emisión del pronóstico. Distinguir fecha del acontecimiento, fecha de publicación y fecha en que el dato estuvo disponible para el equipo.
- Ajustar parámetros y seleccionar hiperparámetros dentro del conjunto de entrenamiento. El conjunto final de evaluación debe permanecer intacto.
- Repetir el análisis con distintas particiones predefinidas cuando el número de casos lo permita, pero reportar también cada caso y no solo el promedio.
- Mantener el preregistro existente: pregunta objetivo, fecha de corte, datos permitidos, método, métrica y regla de decisión deben quedar escritos antes de correr la predicción.

### 3.4 Regla de aceptación

Una mejora solo pasa a producción si:

1. supera la referencia predefinida en datos reservados;
2. la diferencia no depende de una o dos preguntas atípicas;
3. no empeora de forma importante otro dominio que también se vaya a utilizar;
4. respeta las restricciones de privacidad;
5. su costo operativo es razonable para la reducción de error obtenida.

Cuando el conjunto de evaluación sea pequeño, tratar el resultado como evidencia provisional y no como garantía de generalización.

## 4. Mejora 1 — Selector automático de métodos

**Prioridad:** máxima.  
**Costo incremental de API:** prácticamente cero, si se reutilizan resultados ya calculados.

### Problema que resuelve

Hoy se usan métodos distintos según la clasificación de la pregunta, pero no necesariamente existe una regla aprendida para decidir cuándo un método agrega valor. Las pruebas muestran que los agentes son útiles en algunos escenarios y peores en otros.

### Implementación

1. Crear una tabla histórica con una fila por pronóstico retrospectivo y método, con columnas como:
   - identificador de pregunta y familia temática;
   - fecha del pronóstico y fecha de medición objetivo;
   - si había medición comparable previa;
   - edad de la última medición;
   - coincidencia territorial (Bogotá, nacional, localidad);
   - número de preguntas EPC relacionadas;
   - disponibilidad de indicadores o encuestas públicas recientes;
   - predicción de cada método y su error posterior.
2. Construir primero un selector interpretable con pocas variables y regularización. No empezar con una red neuronal ni con un algoritmo complejo.
3. Comparar dos formas de selección:
   - **Selector discreto:** escoge un método candidato.
   - **Combinador:** mezcla predicciones, por ejemplo:

   `pred_final = pred_base + lambda * (pred_agentes - pred_base)`

   Donde `pred_base` es el mejor método de referencia disponible y `lambda` se aprende con datos pasados y se restringe a un rango razonable. Si no hay evidencia de que los agentes mejoren casos semejantes, `lambda` debe tender a cero.
4. Comparar contra cada método individual y contra la persistencia, no solo contra una combinación débil.
5. Guardar la razón de la selección para poder auditar las predicciones.

### Prueba retrospectiva

- Construir predicciones fuera de muestra con los resultados de las pruebas ya hechas.
- Entrenar el selector sin usar los resultados de las preguntas que va a evaluar.
- Separar preguntas políticas de preguntas de ciudad; probar también una evaluación que deje fuera un año completo.
- Informar MAE, sesgo y diferencia frente al mejor método individual.

### Criterio de éxito

El selector debe reducir el MAE en datos reservados frente al mejor método individual, o demostrar una mejora fiable en un dominio específico para el que se activará. No aprobarlo solamente porque mejora el promedio de entrenamiento.

### Riesgo principal

Con pocas preguntas históricas, el selector puede aprender reglas espurias. Mitigación: pocas variables, regularización, validación por bloques y regla de retroceso al método base.

## 5. Mejora 2 — Modelo temporal de opinión (*nowcasting*)

**Prioridad:** alta para temas con varias mediciones a lo largo del tiempo.  
**Costo incremental de API:** cero para el cálculo estadístico; puede existir costo de recopilación o extracción de datos.

### Problema que resuelve

Los perfiles de agentes no reciben automáticamente información fiable sobre lo ocurrido después de su entrevista. Los resúmenes de noticias ya probados apenas movieron a los agentes y además tendieron a empeorar el pronóstico.

### Implementación

1. Crear una serie cronológica para cada indicador comparable: aprobación o imagen de Galán, rumbo de la ciudad, percepción de seguridad y otros temas con mediciones repetidas.
2. Para cada observación, guardar la fecha del trabajo de campo, fecha de publicación, población objetivo, método, tamaño de muestra, margen de error disponible y redacción exacta de la pregunta.
3. No mezclar porcentajes de conceptos distintos como si fueran mediciones idénticas. Crear un mapa de equivalencia de preguntas y un nivel de comparabilidad: exacta, cercana o no comparable.
4. Empezar con modelos simples:
   - persistencia (último dato);
   - tendencia lineal regularizada, solo si hay suficientes puntos;
   - modelo de espacio de estados o actualización bayesiana sencilla cuando exista una serie adecuada;
   - combinación con encuestas públicas comparables, respetando diferencias de población y metodología.
5. Mostrar la magnitud de la actualización temporal por separado de la última medición. La actualización no debe quedar oculta dentro de un número generado por el LLM.
6. Solo transferir un movimiento temporal a una pregunta relacionada cuando exista una relación histórica validada. No asumir, por ejemplo, que un cambio en imagen del alcalde implica el mismo cambio en seguridad o movilidad.

### Prueba retrospectiva

- Reconstruir lo que era conocido antes de cada fecha objetivo.
- Para la EPC 2025, usar únicamente datos que estuvieran disponibles antes de su trabajo de campo de septiembre–noviembre de 2025.
- Para encuestas políticas con varias fechas, ocultar la fecha objetivo y predecirla a partir de fechas anteriores.
- Comparar con persistencia y medir también el error de la magnitud del cambio (`predicción - último dato`).

### Criterio de éxito

Mejorar de forma repetida la predicción temporal frente a persistencia en fechas no usadas para ajustar el modelo. Si la ventaja no existe, mantener la persistencia como estimación predeterminada.

### Riesgo principal

Las cuatro olas anuales de la EPC no bastan para justificar un modelo temporal complejo. Usar complejidad baja y aprovechar series externas solo cuando su comparabilidad esté documentada.

## 6. Mejora 3 — Modelo conjunto de relaciones entre preguntas EPC

**Prioridad:** alta para preguntas nuevas relacionadas con conceptos ya medidos.  
**Costo incremental de API:** casi cero para el modelo estadístico; puede necesitar clasificación semántica puntual.

### Problema que resuelve

La regresión actual selecciona preguntas parecidas y combina resultados, con un error medio reportado de aproximadamente 15 puntos en 139 preguntas de prueba. Puede haber información adicional en las relaciones conjuntas entre respuestas que el enfoque actual no aprovecha.

### Implementación

1. Armonizar variables y opciones de respuesta entre olas de la EPC. Documentar los cambios de cuestionario; no tratar opciones diferentes como idénticas sin una regla explícita.
2. Preparar una matriz encuestado × pregunta, junto con pesos y variables demográficas. Mantener identificadores y columnas de respuestas dentro del entorno autorizado del equipo.
3. Comparar métodos sencillos:
   - modelo factorial o de variables latentes;
   - factorización de matrices para respuestas faltantes;
   - modelo de respuesta al ítem cuando la estructura de preguntas lo permita;
   - regresión actual como baseline.
4. Usar el texto de las preguntas para identificar conceptos y mapear una pregunta nueva a dimensiones aprendidas. El LLM puede clasificar la redacción, pero no debe inventar las correlaciones estadísticas.
5. Cuando cambie el cuestionario, mapear solo preguntas compatibles y documentar las exclusiones.

### Prueba retrospectiva

- Ocultar por completo una pregunta y estimar su distribución con las demás respuestas permitidas.
- Repetir dejando fuera familias temáticas completas para medir transferencia a preguntas menos similares.
- Realizar una prueba temporal adicional: entrenar con olas anteriores y evaluar en la ola siguiente.
- Comparar contra la regresión actual, agentes y persistencia cuando corresponda.

### Criterio de éxito

Reducir el error en preguntas no vistas y mantener resultados razonables al dejar fuera familias o años. Una mejora solo en preguntas casi duplicadas no basta para afirmar que el método resuelve preguntas nuevas de actualidad.

### Riesgo principal

El modelo puede reconstruir bien las preguntas ya relacionadas, pero fallar al extrapolar a asuntos realmente nuevos o a una situación política que cambió después del trabajo de campo.

## 7. Mejora 4 — Calibración de probabilidades de los agentes

**Prioridad:** media; ejecutar después de determinar en qué escenarios los agentes aportan señal.  
**Costo de referencia:** con la cifra reportada de USD 0,05 por 200 agentes, 80 preguntas costarían aproximadamente USD 4 por una ejecución de 200 agentes por pregunta.

### Diferencia frente a lo ya probado

No se propone volver a forzar que la suma agregada de agentes coincida con el total de una encuesta conocida. La propuesta es corregir la relación entre probabilidades emitidas por los agentes y frecuencias observadas en preguntas históricas, usando predicciones hechas sin conocer las respuestas objetivo.

### Implementación

1. Para cada pregunta histórica de validación, guardar las probabilidades por opción emitidas por agente, el resultado de referencia y el peso de encuesta utilizado.
2. Comparar probabilidades originales con un calibrador simple (por ejemplo, calibración logística o isotónica cuando haya suficientes casos).
3. Evitar calibrar un modelo independiente por pregunta si los datos son escasos. Considerar calibración agrupada por familia temática y tipo de respuesta.
4. Aplicar el calibrador antes de agregar las probabilidades con los pesos de encuesta.
5. Medir calibración de probabilidades y error final de la cifra agregada. Una probabilidad individual mejor calibrada no garantiza por sí sola un menor MAE agregado.

### Prueba retrospectiva

- Generar predicciones de forma que las respuestas objetivo permanezcan ocultas a los agentes y al calibrador durante la predicción.
- Separar preguntas completas o familias temáticas entre ajuste y evaluación.
- Comparar agentes sin calibración, agentes calibrados, referencia histórica y regresión.

### Criterio de éxito

Mejora del MAE agregado fuera de muestra y, como señal complementaria, mejor Brier score o log-loss cuando se conserven probabilidades. Si solo mejora la calibración individual pero no el resultado agregado, no justificaría introducirlo al pipeline principal.

### Riesgo principal

La corrección aprendida en preguntas de gestión no tiene por qué funcionar en voto o imagen presidencial. Calibrar solo dentro de grupos con suficiente evidencia y usar regularización.

## 8. Mejora 5 — Sustituir resúmenes narrativos por indicadores estructurados

**Prioridad:** media.  
**Costo incremental de API:** bajo y controlable; el costo principal puede ser recopilación y limpieza de datos.

### Problema que resuelve

Un resumen neutral de noticias no logró desplazar las predicciones hacia la opinión real; en una prueba las movió poco y hacia el pesimismo. Una instrucción de neutralidad no garantiza que el cambio de opinión simulado tenga la dirección correcta.

### Implementación

1. Definir una lista limitada de fuentes e indicadores públicos por tema, por ejemplo seguridad, movilidad, servicios y gestión de la ciudad.
2. Guardar cada dato en una tabla con campos:
   - indicador y unidad;
   - valor actual y referencia anterior;
   - territorio y población cubierta;
   - fecha del hecho, fecha de publicación y fecha de disponibilidad;
   - fuente, enlace y posibles revisiones;
   - concepto de opinión al que podría relacionarse.
3. Usar un LLM solo para extraer campos o clasificar noticias cuando sea útil. Comprobar de manera automática y/o manual los valores extraídos antes de usarlos.
4. Estimar con modelos históricos la relación entre cada indicador y las respuestas de encuesta. No traducir de manera manual un cambio objetivo en puntos porcentuales de opinión.
5. Dejar que el selector temporal use el indicador solo cuando su relación con la pregunta haya mostrado valor predictivo fuera de muestra.

### Prueba retrospectiva

- Reconstruir el conjunto de indicadores que estaba disponible antes del campo de la EPC 2025.
- Predecir preguntas objetivo usando solo esos valores y comparar con la prueba ya registrada de resumen de noticias.
- Hacer ablación: retirar un indicador por vez para verificar si la mejora depende de una fuente concreta.

### Criterio de éxito

Mejora sobre persistencia y sobre el resumen narrativo en datos reservados. Si el indicador no añade señal incremental, no mantenerlo solo porque sea intuitivamente relevante.

### Riesgo principal

Los indicadores administrativos no miden directamente la percepción ciudadana. Puede haber desfases temporales, cambios en la denuncia o relaciones que varíen según el tema.

## 9. Mejora 6 — Usar resultados electorales como información auxiliar restringida

**Prioridad:** media-baja y limitada a tareas políticas concretas.  
**Costo incremental de API:** cero para el cálculo estadístico si los datos están disponibles.

### Implementación

1. Construir variables territoriales a partir de resultados oficiales por mesa, verificando cómo se relacionan las mesas con localidades u otras zonas de análisis.
2. Mantener separados los niveles individual, mesa y localidad. No inferir que una persona concreta votó por un candidato a partir del resultado de su zona (falacia ecológica).
3. Evaluar si variables agregadas electorales ayudan a estimar resultados políticos en Bogotá cuando el dato de encuesta disponible corresponde a una población nacional.
4. Limitar inicialmente el uso a preguntas donde exista una justificación conceptual clara, como intención de voto o diferencias políticas territoriales. No transferir de forma automática a satisfacción con servicios, seguridad o movilidad.
5. Comparar un modelo con variables electorales contra el mismo modelo sin ellas.

### Prueba retrospectiva

- Establecer qué resultados electorales estaban disponibles en la fecha de cada predicción histórica.
- Evaluar en mesas, zonas, elecciones o preguntas no usadas para ajustar el modelo cuando la cantidad de casos lo permita.
- Controlar que el modelo no esté usando resultados de la misma elección que intenta predecir.

### Criterio de éxito

Reducción del error fuera de muestra en una clase de preguntas política claramente especificada. Si solo mejora cuando se incluyen resultados que no se habrían conocido a la fecha del pronóstico, la prueba debe considerarse inválida.

### Riesgo principal

El voto y la opinión sobre una política no son equivalentes. Usar resultados electorales fuera de su ámbito de validez puede introducir asociaciones engañosas.

## 10. Mejora 7 — Medir y optimizar el tamaño del panel de agentes

**Prioridad:** media-baja; no aumentar el panel sin medir primero la fuente de error.  
**Costo según precio reportado:** 200 agentes ≈ USD 0,05; cinco paneles independientes de 200 ≈ USD 0,25 por pregunta; 1.520 agentes equivaldrían a aproximadamente USD 0,38 si el costo escala linealmente.

### Implementación

1. Escoger un conjunto fijo y preregistrado de preguntas que cubra varios temas.
2. Para cada pregunta, crear varias muestras independientes de 200 perfiles con el diseño muestral documentado. Comparar muestreo simple y selección estratificada si esta última es compatible con los pesos y el diseño de la EPC.
3. Repetir algunas ejecuciones con los mismos perfiles para separar la variación por selección de personas de la variación producida por el modelo.
4. Medir la dispersión de las predicciones entre paneles y compararla con el error frente a la encuesta real.
5. Simular el efecto esperado de aumentar el panel antes de pagar por una muestra mayor.

### Cómo interpretar el resultado

- Si las distintas muestras de 200 dan resultados muy diferentes, un panel mayor o un diseño de muestra más eficiente puede ayudar.
- Si dan resultados parecidos, pero todos quedan lejos del valor real, aumentar el tamaño probablemente reducirá poco el error: el problema es sesgo del modelo, información desactualizada o falta de variables relevantes.
- No confundir la dispersión entre paneles con el intervalo de error total de la predicción.

### Criterio de éxito

Aumentar el panel solo si las pruebas demuestran una reducción de incertidumbre relevante para el costo adicional. No asumir que 1.520 agentes es mejor simplemente porque se aproxima al tamaño de la EPC original.

## 11. Mejora 8 — Estimar cuándo no hay evidencia suficiente

**Prioridad:** importante para el producto, aunque no reduzca por sí sola el error del punto estimado.  
**Costo incremental de API:** prácticamente cero después de entrenar el sistema.

### Implementación

1. Crear un índice de soporte de evidencia con variables como:
   - existencia y antigüedad de una pregunta comparable;
   - coincidencia territorial y poblacional;
   - cantidad y calidad de preguntas relacionadas;
   - disponibilidad de indicadores recientes validados;
   - tipo de pregunta y error histórico de métodos similares.
2. Usar validación fuera de muestra para estimar el error típico de predicciones con distintos niveles de soporte. No presentar el índice como una probabilidad de acierto hasta verificar su calibración.
3. Construir intervalos de incertidumbre basados en errores históricos de casos comparables. Comprobar su cobertura en el conjunto reservado.
4. Establecer reglas de alcance: por ejemplo, avisar cuando la pregunta requiere datos inexistentes, se refiere a una población no cubierta o carece de una relación validada con los indicadores disponibles.
5. Mostrar en el resultado el tipo de evidencia utilizada: medición exacta, extrapolación entre preguntas, actualización temporal, encuesta externa o agentes.

### Criterio de éxito

Los intervalos deben tener una cobertura razonable en validación y ser más amplios cuando los errores históricos lo justifiquen. No debe usarse una etiqueta de “alta confianza” si el error real en ese grupo no se ha medido.

## 12. Política de privacidad y límites de uso de datos

Esta sección es obligatoria para todos los experimentos:

1. **Nunca enviar respuestas individuales de las encuestas políticas propias a modelos de lenguaje**, ya sea en texto, CSV, JSON, imágenes, ejemplos, resúmenes individualizados o solicitudes de depuración.
2. Se puede diseñar la interpretación de preguntas con el texto de estas, tal como permite la restricción descrita, sin adjuntar respuestas individuales.
3. Usar resultados agregados de las encuestas propias solo conforme a las reglas internas y acuerdos de uso del equipo. Antes de enviar cifras agregadas a servicios externos, comprobar que las políticas aplicables lo permitan.
4. Mantener separados datos identificables, microdatos de EPC y datos agregados que se decidan usar externamente.
5. Registrar qué datos se enviaron a cada proveedor, para qué objetivo y con qué versión del prompt/modelo.
6. No inventar biografías, preferencias ni comportamientos de agentes para llenar información ausente. La población sintética debe conservar una trazabilidad clara a los atributos observados permitidos.

## 13. Orden recomendado de ejecución

### Fase A — Dejar una evaluación fiable

- Consolidar todas las pruebas históricas y sus predicciones en un formato único.
- Separar pregunta ya medida de pregunta nunca medida.
- Definir métricas, fechas de corte y reglas de exclusión.
- Crear una tabla de resultados por método y dominio.

**Resultado de salida:** benchmark reproducible con persistencia como referencia principal donde corresponda.

### Fase B — Selector y combinador

- Entrenar un selector interpretable usando solo resultados históricos.
- Comparar método único, selector y combinación conservadora.
- Añadir regla de retroceso al método base.

**Resultado de salida:** primera mejora desplegable sin aumentar necesariamente el gasto de API.

### Fase C — Modelo conjunto EPC

- Armonizar preguntas por año.
- Probar modelos factoriales o factorización de matrices.
- Evaluar preguntas ocultas y olas futuras.

**Resultado de salida:** candidato estadístico para preguntas nuevas relacionadas con la EPC.

### Fase D — Actualización temporal

- Normalizar series de encuestas externas e indicadores públicos.
- Reconstruir disponibilidad histórica de los datos.
- Evaluar persistencia, tendencias sencillas y modelos dinámicos.

**Resultado de salida:** ajuste temporal validado para las preguntas que tengan evidencia suficiente.

### Fase E — Experimentos específicos de agentes

- Calibración de probabilidades.
- Variación del tamaño y selección del panel.
- Uso auxiliar de resultados electorales.

**Resultado de salida:** reglas empíricas sobre dónde los agentes ayudan, cuánto panel se necesita y qué correcciones son estables.

### Fase F — Incertidumbre y monitorización

- Estimar el error condicional según el nivel de soporte.
- Crear alertas de cambio de distribución o aumento de error.
- Registrar los errores una vez se publiquen los resultados reales.

**Resultado de salida:** predicciones con trazabilidad y límites explícitos.

## 14. Registro mínimo por cada predicción

Guardar un registro con al menos estos campos:

```json
{
  "prediction_id": "identificador_unico",
  "question_text": "texto exacto de la pregunta",
  "question_family": "tema o familia",
  "target_population": "Bogotá",
  "target_date": "fecha objetivo",
  "forecast_cutoff": "fecha y hora hasta la que se permite usar información",
  "response_options": ["opción A", "opción B"],
  "candidate_methods": {
    "persistence": null,
    "regression": null,
    "latent_model": null,
    "temporal_model": null,
    "agents": null
  },
  "selected_method": "método elegido",
  "final_estimate": null,
  "uncertainty_interval": null,
  "evidence_sources": [],
  "model_and_prompt_versions": {},
  "preregistration_reference": "referencia al registro previo",
  "observed_result": null,
  "absolute_error_pp": null
}
```

Los valores `null` indican campos a completar, no cifras supuestas. Para una respuesta con varias opciones, guardar la distribución completa además de la cifra principal.

## 15. Decisiones de producto recomendadas

- Si existe una pregunta comparable y no hay evidencia fiable de cambio, el valor de referencia debe ser la última medición, no el resultado de los agentes.
- Si existen señales temporales, el sistema solo debe apartarse de esa medición en la magnitud que haya sido validada históricamente.
- Si la pregunta es nueva pero se relaciona con dimensiones EPC conocidas, probar primero el modelo estadístico conjunto.
- Si la pregunta es política y la referencia disponible es nacional, los agentes pueden ser candidatos para transferir información a Bogotá, pero deben competir contra la encuesta nacional y cualquier método estadístico disponible.
- Si no existe evidencia pertinente, ofrecer una estimación marcada como exploratoria y un intervalo amplio; no presentar una cifra precisa como si fuera una medición.
- No invertir en más llamadas a agentes hasta medir si el error dominante proviene del muestreo o de sesgo/falta de información.

## 16. Conclusión

La mejora prioritaria no es hacer los agentes más sofisticados ni darles perfiles más largos. Es aprender, con pruebas retrospectivas estrictas, **cuándo cada método merece confianza**.

El camino de menor riesgo es: evaluación reproducible → selector de métodos → modelo conjunto EPC → actualización temporal → experimentos dirigidos con agentes → estimación de incertidumbre. Cada módulo debe poder desactivarse si no supera la referencia en datos reservados.

El límite fundamental permanece: con datos anuales y sin nueva evidencia pertinente, no siempre es posible descubrir un cambio de opinión ocurrido hoy. El objetivo alcanzable es aprovechar al máximo la información que sí existe, actualizar solo con señales verificables y comunicar claramente la incertidumbre.

## Lecturas complementarias

Estas publicaciones pueden servir para orientar el diseño; sus resultados deben interpretarse dentro de sus respectivos contextos y no como garantía de desempeño en Bogotá:

- Kim y Lee, *AI-Augmented Surveys: Using Large Language Models to Emulate Human Respondents* (arXiv): https://arxiv.org/abs/2305.09620
- *Improving Small-Area Estimates of Public Opinion by Calibrating to Known Population Quantities* (Political Analysis, referencia sobre calibración con cantidades conocidas): https://www.cambridge.org/core/journals/political-analysis/article/improving-smallarea-estimates-of-public-opinion-by-calibrating-to-known-population-quantities/8322170F190E327E3B0E91DC207016BF
- Trabajo sobre heterogeneidad del desempeño de respuestas sintéticas de encuestas (arXiv): https://arxiv.org/abs/2509.09871
