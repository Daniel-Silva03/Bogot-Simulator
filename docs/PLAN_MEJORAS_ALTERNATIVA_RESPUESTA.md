Es un excelente ejercicio de rigor empírico. Los datos que muestran son contundentes: si los agentes replican su identidad pero no actualizan su percepción del entorno, el puente temporal se rompe. La persistencia es una vara durísima porque la opinión pública, especialmente en indicadores institucionales, tiene una inercia estructural que los modelos de lenguaje suelen subestimar al sobre-reaccionar a las noticias recientes.

Avanzar con el **Panel de Expertos Sintéticos** como prueba pre-registrada para diciembre de 2026 tiene sentido empírico y económico. Aquí está el diseño detallado del módulo 4, respetando el presupuesto, la fecha de corte (20/10/2026) y la restricción absoluta de no usar microdatos.

---

### 1. Los 5 perfiles de experto

**¿Por qué 5 distintos y no uno con 5 repeticiones (temperature > 0)?**
Si usas un solo perfil ("experto en encuestas") con temperatura alta, el modelo generará variaciones aleatorias sobre el mismo sesgo analítico (ruido). Si usas 5 perfiles con roles distintos, fuerzas al LLM a ponderar diferentes subconjuntos de datos en cada llamada. Es un ensamble o "mezcla de expertos": uno penalizará la inercia, otro sobrerreaccionará a la economía y otro a los medios. El promedio de errores ortogonales reduce el error total.

**Los 5 perfiles (para incluir en el prompt del sistema):**
1. **El Analista de Tendencias (Cuantitativo):** "Eres un estadístico puro. Tu regla de oro es la reversión a la media y la inercia estructural. Sabes que la opinión pública en Bogotá es rígida. Asignas poco peso a escándalos recientes y mucho a la pendiente histórica de los últimos 5 años de la EPC."
2. **El Sociólogo Urbano:** "Evalúas el clima de opinión a través de las condiciones materiales. Tu foco principal son los datos del DANE (desempleo, inflación, pobreza). Si el bolsillo y el empleo mejoran, ajustas la opinión ciudadana al alza; si empeoran, a la baja."
3. **El Politólogo de Coyuntura:** "Mides el desgaste del capital político. Te enfocas en las encuestas de prensa recientes (ej. Invamer) para capturar el 'momentum'. Entiendes cómo la desaprobación del alcalde arrastra otros indicadores como 'rumbo de la ciudad'."
4. **El Experto en Instituciones:** "Conoces la burocracia bogotana. Sabes que instituciones como el Concejo o la percepción de 'participación' y 'respuesta a la ciudadanía' tienen bajísima saliencia (a la gente no le importan en el día a día) y rara vez cambian más de 1 o 2 puntos por año, independientemente de quién sea el alcalde."
5. **El Economista Comportamental:** "Modelas sesgos cognitivos. Sabes que en temas de 'corrupción', la ciudadanía tiene un sesgo de negatividad casi inamovible. Asumes que las buenas noticias no mejoran la percepción de transparencia, pero un solo escándalo la hunde."

---

### 2. Los datos y el formato (Corte: Octubre 2026)

Para mantener el costo bajo (USD 0,05 por pregunta), el prompt debe ser ultracompacto y evitar prosa innecesaria. El formato ideal es **JSON minimizado** o **CSV en bloque**, que los LLMs procesan perfectamente.

**Datos a entregar por prompt:**
1. **Serie histórica EPC:** Solo la de la pregunta objetivo.
2. **Anclas externas (Prensa):** Últimas 3 mediciones públicas.
3. **Contexto DANE:** 3 indicadores clave trimestrales.

**Ejemplo de formato de inyección en el prompt (aprox. 150-200 tokens):**

```text
[HISTORICO_EPC_PREGUNTA: "Gestión del Alcalde"]
Escala: Buena, Regular, Mala (Omito NS/NR).
2022: B:22, R:30, M:48
2023: B:19, R:28, M:53
2024: B:35, R:35, M:30
2025: B:26, R:35, M:39

[ENCUESTAS_PRENSA_2026]
- Invamer (Oct 2026, Presencial, Margen error 3%): Aprobación Alcalde 38%, Desaprobación 55%.
- CNC (Sep 2026, Telefónica, Margen 4%): Aprobación Alcalde 41%, Desaprobación 51%.

[CONTEXTO_MACRO_DANE_BOGOTA]
- Desempleo (Trimestre Jul-Sep 2026): 10.2% (vs 10.5% en 2025).
- Inflación interanual (Sep 2026): 4.8% (vs 8.2% en 2025).
```
*Instrucción de salida obligatoria:* Retornar un JSON exacto: `{"B": [numero], "R": [numero], "M": [numero]}` que sume 100 (sin NS/NR).

---

### 3. Agregación: La Media Truncada (Trimmed Mean)

Debes pre-registrar la **Media de los 3 valores centrales** (excluyendo el valor máximo y el mínimo de los 5 expertos para cada categoría). 

**¿Por qué?**
Los LLMs sufren de alucinaciones esporádicas. Si 4 expertos predicen que la "buena gestión" será 25, 26, 24, y 27, pero el perfil Sociólogo alucina un 45 por un error de lectura de escala, la media aritmética tradicional (29.4) se contamina y perderás contra la persistencia. Descartar los dos extremos (el mayor y el menor) y promediar los 3 del medio te da máxima robustez frente a errores de inferencia del modelo.

---

### 4. Hipótesis de falla y expectativas vs. Persistencia

El modelo fallará principalmente por el "sesgo de actualidad" *(recency bias)*: leer una noticia de prensa de octubre de 2026 y asumir que el ciudadano de a pie actualizará sus creencias en la misma proporción, ignorando que la EPC es probabilística en hogares y captura gente totalmente desconectada de la política.

**Expectativas pre-registradas para las 7 preguntas:**

1. **Gestión del alcalde:** *Posible victoria del Panel.* Aquí las encuestas de prensa son un excelente proxy direccional. La persistencia (usar el dato de finales de 2025) ignoraría todo el desgaste (o repunte) del tercer año de mandato de Galán en 2026. El panel debería leer bien el ajuste.
2. **Rumbo de la ciudad:** *Empate técnico.* Es un proxy del estado de ánimo general, muy anclado a la economía. Si los datos del DANE muestran una inflación controlada pero estancamiento económico en 2026, el panel sociológico/macro podría hacer un ajuste fino mejor que la persistencia.
3. **Corrupción:** *Gana la persistencia.* Es una métrica estructural. Los expertos sobre-reaccionarán a cualquier escándalo mediático de 2026, mientras que la EPC históricamente muestra que la percepción de corrupción siempre es altísima y se mueve como una tortuga.
4. **Concejo:** *Gana la persistencia por goleada.* Es una institución de bajísima saliencia. La gente responde con la inercia de la desafección institucional. El "Politólogo" intentará buscar correlaciones con el alcalde, introduciendo ruido donde solo hay quietud.
5. **Transparencia:** *Gana la persistencia.* Igual que corrupción. El ciudadano promedio no tiene nuevos elementos de juicio empíricos para cambiar de opinión de 2025 a 2026.
6. **Respuesta a la ciudadanía:** *Gana la persistencia.* Métrica hiper-rígida. Los expertos asumirán que si el alcalde cae, esto cae. No siempre es así.
7. **Participación:** *Gana la persistencia.* Los modelos asocian esto con datos formales, pero en la EPC es un tema de sensación de inclusión comunitaria, que rara vez presenta quiebres anuales mayores al margen de error.

**Conclusión estratégica para el experimento:** Si el Panel de Expertos logra ganarle a la Persistencia en *Gestión* y *Rumbo*, pero pierde en las institucionales, el experimento será un éxito metodológico: demostrará que los LLMs sirven para estimar percepciones de alta saliencia mediática/económica, pero son inútiles (frente a un simple rezago $t-1$) para predecir percepciones estructurales de baja saliencia.