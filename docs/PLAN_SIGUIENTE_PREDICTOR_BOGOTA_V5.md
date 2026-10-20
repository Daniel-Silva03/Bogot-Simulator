# Siguientes pasos para el predictor de opinión pública de Bogotá — plan v5

## 1. Qué enseñan los resultados del plan v4

La conclusión es más firme que en las rondas anteriores: **no seguir intentando corregir el simulador para que prediga mejor la evolución de la opinión política sin identificar primero qué señal está utilizando y por qué se equivoca.**

En la prueba de 15 preguntas de gobierno, la persistencia obtuvo un error absoluto medio de 7,37 puntos, frente a 8,74 de los agentes. Los agentes ganaron en una de las tres transiciones, precisamente la de 2024 a 2025, cuando cayó la evaluación de Galán. Tampoco superaron ninguna de las reglas preregistradas.

Hay dos matices importantes:

- El subconjunto de gobierno se seleccionó después de conocer los resultados desfavorables de la Fase B. Aunque se preregistró la ejecución de esta nueva prueba, esa selección posterior hace que deba considerarse principalmente un análisis diagnóstico, no una confirmación independiente de capacidad predictiva.
- Los agentes no necesariamente están siendo pesimistas con el alcalde en sentido estricto. Sus tres predicciones de gestión fueron 25,3%, 31,1% y 29,3%, mientras que los resultados reales fueron 31,1%, 42,3% y 26,4%. Las predicciones se mantuvieron alrededor del 29–31% aunque la opinión real subió y bajó bastante. Eso parece compatible con una tendencia a concentrarse alrededor de un valor central y no seguir los cambios. Tres casos no permiten establecer la causa.

La investigación externa mencionada en el análisis previo —Pew Research Center, septiembre de 2026— encontró que sus encuestados sintéticos no captaron una caída de la aprobación presidencial estadounidense entre enero y abril de 2026. Es evidencia de otro contexto, no una estimación para Bogotá, pero ilustra un tipo de fallo relevante: los agentes pueden permanecer estables mientras la opinión humana cambia.

## 2. ¿Tiene sentido corregir el sesgo?

**No aplicar ahora una corrección al resultado publicado. Sí probar si existe un patrón de error que pueda corregirse de forma prospectiva.**

Los resultados no muestran un sesgo uniforme:

| Pregunta | Predicción de los agentes menos resultado real | Interpretación |
|---|---:|---|
| Gestión de López, 2023 | −5,8 puntos | Subestimación |
| Gestión de Galán, 2024 | −11,2 puntos | Subestimación |
| Gestión de Galán, 2025 | +2,9 puntos | Sobreestimación |
| Corrupción, 2023 | +25,4 puntos | Sobreestimación de la percepción de aumento |
| Corrupción, 2024 | +7,6 puntos | Sobreestimación |
| Corrupción, 2025 | −6,3 puntos | Subestimación |

Por eso, restar tres puntos al porcentaje del simulador o aplicar una corrección negativa a toda la categoría de gobierno no estaría justificado.

### Experimento para estudiar una corrección

Probar una corrección estadística con contracción hacia cero (*shrinkage*), primero en un backtest de las predicciones históricas ya guardadas, sin llamar al modelo.

Si \(e=\hat p-p\) representa el error firmado, una corrección candidata sería:

\[
\hat p_{\text{corregido}}=\operatorname{clip}(\hat p-\lambda\bar e_k,0,100)
\]

Aquí, \(\bar e_k\) sería el error medio histórico de una categoría de preguntas y \(\lambda\) controlaría cuánto se aplica la corrección. La categoría podría ser gestión del alcalde, corrupción u otro tema predefinido.

Los errores usados para calcular \(\bar e_k\) deben ser anteriores a la predicción que se corrige. No se puede calcular la corrección con el error de 2025 y luego afirmar que mejoró la predicción de 2025.

Con tan pocos casos, usar una regla conservadora: si no hay suficientes errores históricos independientes para estimar el sesgo de una categoría, la corrección será cero. Solo probar una corrección específica de gobierno si supera a los agentes sin corregir y a la persistencia en datos reservados.

**Recomendación actual:** no conservar ninguna corrección. Retomar el paso cuando haya suficiente evidencia independiente, sin gastar dinero en más agentes por ahora.

## 3. ¿Cómo comprobar si los agentes son pesimistas con los alcaldes?

La prueba debe separar dos hipótesis:

- **Pesimismo hacia el gobernante:** el modelo tiende a reducir la evaluación del alcalde, incluso cuando los perfiles y la información disponible no justifican una reducción.
- **Regresión hacia un valor central:** el modelo produce resultados cercanos a un porcentaje típico, sin captar cuánto sube o baja realmente la opinión.

Por ahora, los resultados son más compatibles con la segunda hipótesis: las predicciones de los tres años se concentran alrededor del 30%, aunque los valores reales van del 26% al 42%. No es suficiente para demostrarlo, pero ofrece una hipótesis concreta que se puede falsar.

### Diseño de la prueba

Usar los mismos 200 perfiles de la EPC 2025 y una sola pregunta: la calificación de la gestión del alcalde. Comparar dos condiciones:

| Condición | Qué recibe el modelo |
|---|---|
| A. Producción | El prompt actual, con Galán identificado por su nombre. |
| B. Identidad neutralizada | Los mismos perfiles y la misma pregunta, pero sin mencionar el nombre del alcalde. |

Todo lo demás permanece fijo: fecha objetivo, instrucciones, opciones de respuesta, temperatura, modelo y ponderación.

Medir:

1. La diferencia entre las estimaciones agregadas de A y B.
2. El cambio simulado respecto a la respuesta anterior de cada perfil.
3. Si el modelo sigue generando porcentajes cercanos al 30% independientemente de que los perfiles originales evaluaran mejor o peor al alcalde.

La segunda condición es diagnóstica: al anonimizar al gobernante, la pregunta deja de medir exactamente la misma situación política. Por eso, no utilizar B como sustituto de la predicción de producción ni elegir después la variante que más se acerque al resultado real.

**Interpretación preregistrada:** si quitar el nombre cambia sustancialmente la cifra, hay evidencia de que la identidad o el conocimiento previo del modelo influyen en la simulación. Si ambas variantes permanecen concentradas alrededor del mismo porcentaje y no responden a las calificaciones anteriores de los perfiles, aumenta la plausibilidad de una atracción hacia un valor central.

Ninguno de esos resultados, por sí solo, demostraría cuál es la opinión real de Bogotá. La prueba identifica el comportamiento del modelo, no valida una predicción.

**Costo estimado:** alrededor de USD 0,05 para los 200 agentes de la condición adicional de una pregunta, reutilizando la ejecución de producción como referencia. No cambiar el modelo en funcionamiento con base únicamente en este diagnóstico.

## 4. Prueba prospectiva con la EPC 2026

Esta es la tarea que más valor tiene porque puede aportar evidencia prospectiva, en vez de otro backtest afectado por el conocimiento actual del modelo.

La fecha de preparación del plan es el **20 de octubre de 2026**. Congelar el diseño ahora, antes de acceder a los resultados de la EPC 2026.

### Protocolo propuesto: EPC 2025 → EPC 2026

**Perfiles y ejecución**

- Los mismos 200 perfiles de la EPC 2025, con selección reproducible y pesos originales.
- El modelo, prompt de producción, temperatura y nivel de razonamiento congelados.
- Un lote de predicciones antes de conocer los porcentajes de la EPC 2026.
- Sin noticias añadidas, variantes de prompt ni selección posterior de los agentes más acertados.

**Preguntas candidatas**

- Gestión del alcalde.
- Rumbo de la ciudad.
- Percepción de corrupción.
- Gestión del Concejo.
- Transparencia.
- Respuesta a la ciudadanía.
- Participación ciudadana.

Solo entrarán en el cálculo principal las preguntas que se repitan en 2026 con una formulación, opciones de respuesta y definición del porcentaje suficientemente comparables con 2025. La regla para excluir preguntas no comparables se registrará antes de examinar sus resultados.

**Métodos enfrentados**

- **P: persistencia**, repitiendo el porcentaje de la EPC 2025.
- **G: agentes**, estimación con perfiles de 2025.

**Costo previsto:** aproximadamente USD 0,35 para siete preguntas a USD 0,05 por pregunta, con 200 agentes.

### Reglas para declarar una victoria

La métrica principal será el error absoluto medio en puntos porcentuales sobre todas las preguntas comparables, calculado tanto para P como para G.

Preinscribir estas condiciones:

- **Mejora general:** los agentes deben reducir el error absoluto medio al menos un punto respecto a la persistencia en el conjunto completo.
- **Robustez:** la mejora debe mantenerse al excluir la pregunta sobre la gestión del alcalde; de lo contrario, no se habrá demostrado una mejora general.
- **Resultado por pregunta:** publicar cuántas preguntas gana cada método, el error individual de cada una y el sesgo firmado, sin seleccionar únicamente los casos favorables.

El segundo criterio es deliberadamente exigente. El objetivo es descubrir si los agentes aportan información para predecir cambios en la opinión, no validar un método general porque haya acertado una sola caída de la aprobación.

Si los agentes ganan únicamente en la gestión de Galán, el informe debe decir:

> Los agentes superaron a la persistencia en la pregunta sobre la gestión del alcalde, pero no demostraron una mejora general en las preguntas de gobierno evaluadas. El resultado es específico de esa pregunta y necesita replicación.

No cambiar las reglas después de conocer el resultado, incluso si la cifra de Galán resulta llamativa.

El protocolo debe registrar también el nombre y versión exactos del modelo, el prompt, las ponderaciones, el conjunto de perfiles, las preguntas excluidas y la fecha en que se generaron las predicciones. Estos resultados experimentales pueden almacenarse de forma controlada para evaluar la prueba sin modificar la regla de producto de no dejar un registro de cada consulta de los usuarios.

La prueba prospectiva no elimina toda incertidumbre sobre lo que el modelo ya sabe acerca de la actualidad. Sí evita la filtración más importante del backtesting histórico: conocer el resultado de la encuesta que se intenta predecir.

## 5. ¿Dónde pueden aportar valor los agentes además de las preguntas nunca medidas?

Veo dos usos potencialmente útiles, con niveles de evidencia diferentes.

### A. Reconstruir una respuesta oculta dentro de la misma ola

En pruebas anteriores, los agentes reconstruyeron preguntas de gobierno ocultas de la misma ola con un error de 7,4–7,8 puntos, frente a 14,3 de la regresión. Es una tarea diferente de predecir la opinión un año después: las respuestas de las demás preguntas permiten inferir cómo respondería una persona a otra pregunta ya aplicada.

Investigar como herramienta de imputación de respuestas ausentes y análisis de relaciones entre actitudes. No presentarlo como evidencia de capacidad para anticipar cambios de opinión de Bogotá.

### B. Transportar una referencia nacional a Bogotá

En la prueba anterior de segunda vuelta presidencial, los agentes combinados con una encuesta nacional tuvieron un error aproximado de 3,4 puntos en Bogotá, mejor que copiar directamente la cifra nacional, cuyo error fue de 7,5 puntos. Ese resultado apunta a una utilidad posible cuando la fuente disponible corresponde a otra población.

Un caso no demuestra que esta capacidad se generalice. Hacer una prueba independiente con otras preguntas políticas para las que se disponga de una referencia humana local reservada. No enviar respuestas individuales de las encuestas políticas propias a ningún modelo de lenguaje.

Para preguntas completamente nuevas, el error histórico de unos 11 puntos en el dominio político puede seguir siendo útil como referencia exploratoria. Sin embargo, no describirlo como precisión demostrada de un pronóstico actual.

También reservar los agentes para tareas auxiliares que no exigen afirmar una cifra representativa de la población: clasificar preguntas, localizar mediciones históricas relacionadas, detectar cambios de formulación y generar hipótesis que luego se evalúen estadísticamente.

Las respuestas generadas por IA no son participantes humanos y deben identificarse como sintéticas, sin describirse como una encuesta o sondeo humano.

## 6. Orden de ejecución recomendado

1. **Congelar el experimento prospectivo para la EPC 2026**, utilizando los 200 perfiles de la EPC 2025, y no modificarlo cuando empiecen a conocerse los resultados.
2. Ejecutar la prueba de identidad neutralizada como diagnóstico barato del comportamiento del modelo, sin utilizarla para seleccionar retroactivamente una variante ganadora.
3. Dejar la corrección estadística del sesgo en espera hasta disponer de suficientes errores históricos anteriores. Los datos actuales no justifican una corrección por categoría.
4. Mantener como líneas de investigación distintas la reconstrucción de preguntas ocultas de la misma ola y el transporte de información nacional a Bogotá. No mezclarlas con la evaluación de predicción temporal.

## 7. Restricciones y principios que se mantienen

- Prerregistro antes de ejecutar cada prueba.
- La persistencia sigue siendo el benchmark mínimo.
- Las respuestas individuales de las encuestas políticas propias no se envían a ningún modelo de lenguaje.
- Presupuesto reducido: unos USD 0,05 por pregunta con 200 agentes.
- Los agentes continúan activos en producción como experimento declarado, conforme a las decisiones de producto.
- La página siempre produce una cifra; debe seguir identificándola como simulación exploratoria cuando corresponda.
- No afirmar que los agentes aportan una mejora predictiva general sin una prueba prospectiva que supere a la persistencia.

## Conclusión

El siguiente avance no debe medirse por cuánto conseguimos modificar la cifra de los agentes, sino por cuánto conseguimos demostrar que mejora una predicción futura frente a la persistencia. La prioridad es congelar una evaluación prospectiva para la EPC 2026 y usar los resultados para decidir en qué tareas los agentes realmente aportan valor.
