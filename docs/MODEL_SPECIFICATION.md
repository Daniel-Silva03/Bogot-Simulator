# MODEL SPECIFICATION — Selección del modelo de dinámica de opinión

Proyecto: Bogotá Social Simulator
Documento: ETAPA 4 del roadmap — no depende de respuesta del CNC
Versión: 0.1 — Borrador
Fecha: Septiembre de 2026

---

## 1. Objetivo

Comparar formalmente los modelos de opinion dynamics candidatos (sección 15 de PROJECT_CONTEXT.md) contra criterios explícitos, y recomendar uno para el prototipo — sin descartar los demás sin evidencia (Principio 4: toda decisión metodológica debe justificarse).

**Criterios de selección** (los mismos de PROJECT_CONTEXT.md §15): interpretabilidad, evidencia científica de calibración empírica, datos requeridos, complejidad, calibrabilidad, aplicabilidad a Bogotá/CNC, capacidad de representar heterogeneidad (pluralidad de opinión, no solo consenso).

---

## 2. Modelos evaluados

### MODELO — DeGroot
- **Qué representa:** consenso por promediado repetido de opiniones vecinas
- **Supuestos:** influencia social simétrica y estable en el tiempo; sin resistencia individual al cambio
- **Variables:** opinión continua por agente; matriz de pesos de influencia
- **Ecuación:** \(a_i(t+1) = \sum_j p_{ij}\, a_j(t)\), con \(\sum_j p_{ij}=1\)
- **Ventajas:** lineal, matemáticamente bien entendido (álgebra de matrices), fácil de implementar y depurar primero
- **Desventajas:** converge casi siempre a consenso — no reproduce pluralidad ni polarización, que es justamente lo que el proyecto quiere poder explorar
- **Datos necesarios:** solo la red de interacción (pesos)
- **Complejidad:** baja
- **Interpretabilidad:** alta
- **Validación:** débil — su principal falla (consenso forzado) lo hace difícil de contrastar contra encuestas reales, que casi nunca muestran consenso total
- **Aplicabilidad a Bogotá:** limitada como modelo final, útil como *baseline* (A11 — comparar el ABM contra algo más simple)
- **Recomendación:** usar como **baseline de comparación**, no como modelo final

### MODELO — Friedkin-Johnsen (FJ)
- **Qué representa:** DeGroot + un término de "anclaje" a la opinión inicial (persistencia / tozudez del agente)
- **Supuestos:** cada agente tiene un grado de apego a su propia opinión inicial que no desaparece
- **Variables:** opinión continua; matriz de influencia; parámetro de persistencia por agente
- **Ecuación:** \(a_i(t+1) = \phi_i \sum_j p_{ij}\, a_j(t) + (1-\phi_i)\, a_i(0)\)
- **Ventajas:** sigue siendo lineal y analíticamente tratable; ya no fuerza consenso total — permite desacuerdo persistente, lo cual es más realista
- **Desventajas:** el parámetro de persistencia \(\phi_i\) por agente hay que estimarlo — no es trivial sin datos longitudinales
- **Datos necesarios:** red de interacción + alguna forma de estimar persistencia individual
- **Complejidad:** baja-media
- **Interpretabilidad:** alta
- **Validación:** mejor que DeGroot — es una de las pocas familias de modelos con tratamiento analítico (no solo simulación) fuera del paradigma de confianza acotada
- **Aplicabilidad a Bogotá:** buena como segundo paso tras el baseline DeGroot
- **Recomendación:** candidato fuerte para el prototipo inicial por su balance simplicidad/realismo

### MODELO — Bounded Confidence (Hegselmann-Krause)
- **Qué representa:** los agentes solo se dejan influir por otros cuya opinión está dentro de un umbral de "confianza" \(\varepsilon\)
- **Supuestos:** homofilia de opinión — ignoramos completamente a quien piensa muy distinto
- **Variables:** opinión continua; umbral \(\varepsilon\) de confianza
- **Ecuación:** \(a_i(t+1) = \dfrac{1}{|I_i(t)|}\sum_{j\in I_i(t)} a_j(t)\), donde \(I_i(t)=\{j : |a_i(t)-a_j(t)|\le\varepsilon\}\)
- **Ventajas:** el único de los "clásicos" que produce fragmentación/polarización de forma natural — justo el fenómeno que RESEARCH.md identificó como relevante
- **Desventajas:** es un sistema **no lineal** (la red de influencia cambia en cada paso), mucho menos tratable analíticamente — casi todo el trabajo con este modelo es por simulación, no por análisis matemático
- **Datos necesarios:** ninguno adicional a DeGroot, pero calibrar \(\varepsilon\) contra datos reales es notoriamente difícil
- **Complejidad:** media
- **Interpretabilidad:** media — el resultado macro (cuántos clusters, dónde) es sensible a \(\varepsilon\) de forma poco intuitiva
- **Validación:** débil en la literatura clásica — Gestefeld & Lorenz (2023) señalan explícitamente que este tipo de modelo se valida casi siempre solo a nivel fenomenológico ("¿produce polarización?"), no contra distribuciones de encuestas reales
- **Aplicabilidad a Bogotá:** interesante conceptualmente, riesgoso como primer modelo por su dificultad de calibración
- **Recomendación:** guardar como línea de exploración, no como primer modelo

### MODELO — Deffuant-Weisbuch
- **Qué representa:** variante de confianza acotada pero con interacción de a pares (no todos contra todos)
- **Supuestos:** iguales a Hegselmann-Krause en el umbral de confianza, distinto en el mecanismo de encuentro
- **Ecuación:** si \(|a_i-a_j|\le\varepsilon\): \(a_i \leftarrow a_i + \mu(a_j-a_i)\), \(a_j \leftarrow a_j + \mu(a_i-a_j)\)
- **Ventajas:** computacionalmente más liviano que HK para poblaciones grandes (interacción por pares, no por vecindario completo)
- **Desventajas:** mismas limitaciones de calibración que HK
- **Complejidad:** media
- **Interpretabilidad:** media
- **Validación:** igual de débil que HK en el sentido empírico
- **Aplicabilidad a Bogotá:** buena opción de eficiencia computacional si se decide ir por confianza acotada más adelante
- **Recomendación:** sustituto de HK si el rendimiento a 100.000 agentes lo exige, no un modelo distinto en fondo

### MODELO — Marco de cognición motivada (Lorenz, Neumann & Schröder 2021; calibrado por Gestefeld & Lorenz 2023)
- **Qué representa:** generalización de confianza acotada con base psicológica explícita: combina fuerza de cambio, grado de asimilación, "cognición motivada" (ignorar gradualmente, no de golpe, las opiniones muy distantes) y cambio idiosincrático (el agente regresa con cierta probabilidad a su opinión inicial)
- **Supuestos:** la opinión se forma en la juventud y persiste con una tendencia a "regresar" a ese punto de anclaje; la influencia social decae suavemente con la distancia de opinión, no de golpe como en HK
- **Ecuación (núcleo):** \(\Delta a_i = \dfrac{\lambda^k}{\lambda^k+|a_j-a_i|^k}\,\alpha\,(a_j-\rho\, a_i)\), más un término de reversión idiosincrática con probabilidad \(\theta\)
- **Ventajas:** es, de los cinco, el **único con evidencia directa de calibración exitosa contra datos de encuesta reales** — Gestefeld & Lorenz (2023) lo ajustaron a 1.235 distribuciones de confianza institucional de la European Social Survey (mediana \(R^2>0.8\)) y a datos de panel del Swiss Household Panel, incluyendo probabilidades de transición individuales, no solo la distribución agregada
- **Desventajas:** más parámetros que calibrar (6, más el conteo de pasos de tiempo por período real); mayor complejidad de implementación
- **Datos necesarios:** distribuciones de opinión repetidas en el tiempo (varias rondas de una misma pregunta) — exactamente lo que ofrecen Bogotá Cómo Vamos (serie desde 1998) y, si el CNC confirma series tipo "Termómetro de Opinión", también esa fuente
- **Complejidad:** media-alta
- **Interpretabilidad:** media — más parámetros, pero cada uno tiene interpretación psicológica clara
- **Validación:** la más fuerte encontrada en toda la revisión — es literalmente el paper que responde a la advertencia de RESEARCH.md de "no validar solo a nivel fenomenológico"
- **Aplicabilidad a Bogotá:** alta, condicionada a tener al menos una serie repetida de la misma pregunta de opinión (BCV lo ofrece)
- **Recomendación:** **candidato objetivo para la Fase 4 (calibración)**, no necesariammente para el primer prototipo de 1.000 agentes

---

## 3. Tabla comparativa

| Modelo | Interpretabilidad | Evidencia empírica de calibración | Complejidad | Produce pluralidad/polarización | Aplicabilidad Bogotá |
|---|---|---|---|---|---|
| DeGroot | Alta | Débil | Baja | No (fuerza consenso) | Baseline únicamente |
| Friedkin-Johnsen | Alta | Media | Baja-media | Parcial (desacuerdo persistente) | Buena para prototipo |
| Hegselmann-Krause | Media | Débil (solo fenomenológica) | Media | Sí | Riesgosa como 1er modelo |
| Deffuant-Weisbuch | Media | Débil (solo fenomenológica) | Media | Sí | Igual que HK, más eficiente |
| Lorenz/Gestefeld (cognición motivada) | Media | **Fuerte (R²>0.8 en ESS+SHP)** | Media-alta | Sí | Alta, si hay series repetidas |

---

## 4. Recomendación

**Para el primer prototipo (1.000 agentes, 1–2 variables, ETAPA 6 de la Fase 2):** usar **Friedkin-Johnsen** simplificado. Es lo suficientemente simple para validar primero que la arquitectura del ABM funciona (Principio 5: evitar complejidad prematura), y ya evita el defecto más obvio de DeGroot (consenso forzado) sin pagar el costo de calibración de los modelos de confianza acotada.

**Como modelo objetivo de la Fase 4 (calibración con datos reales):** el marco de **cognición motivada de Lorenz et al. (2021) / Gestefeld & Lorenz (2023)**. Es el único de los cinco que tiene un precedente publicado de ajuste exitoso contra distribuciones de opinión reales *y* contra transiciones individuales de panel — que es exactamente el estándar de éxito que RESEARCH.md y PROJECT_CONTEXT.md exigen (D07, D08). Su requisito de datos (una pregunta medida varias veces en el tiempo) coincide con lo que ya sabemos que existe en Bogotá Cómo Vamos.

**DeGroot** se mantiene como baseline obligatorio (A11) para poder responder honestamente la pregunta de RESEARCH.md: ¿el ABM aporta algo frente a algo mucho más simple?

**Hegselmann-Krause / Deffuant** no se descartan — quedan como línea de exploración si, tras calibrar el modelo de cognición motivada, se necesita representar fragmentación en más de una dimensión de opinión.

## 5. Qué queda abierto

- Confirmar si Bogotá Cómo Vamos publica (o puede compartir bajo solicitud) la matriz de transición implícita entre rondas, o solo distribuciones agregadas por año — determina si se puede replicar la metodología de calibración a nivel micro (transición) o solo a nivel macro (distribución).
- Si el CNC confirma un estudio tipo tracking/panel (p. ej. el Termómetro de Opinión), evaluarlo como fuente adicional o alternativa para la calibración de la Fase 4.
- El diseño de la red de interacción (A07) sigue pendiente — todos estos modelos necesitan una matriz de pesos \(p_{ij}\) que todavía no se ha definido.

---

*Documento vivo — decisión final (A06) se registra en PROJECT_CONTEXT.md con formato D0X cuando se confirme tras el prototipo.*
