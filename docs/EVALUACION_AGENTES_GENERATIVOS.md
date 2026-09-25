# EVALUACIÓN — Agentes generativos y datos sintéticos

Proyecto: Bogotá Social Simulator
Documento: evaluación de tres fuentes traídas el 24/09/2026, contra D28 (LLM fuera del núcleo del MVP) y §41–42 de RESEARCH.md
Versión: 0.1
Fecha: 24 de septiembre de 2026

---

## 1. Qué se evaluó

| Fuente | Qué es | Veredicto |
|---|---|---|
| [Stanford HAI — *Simulating Human Behavior with AI Agents*](https://hai.stanford.edu/policy/simulating-human-behavior-with-ai-agents) | Resumen de política del trabajo de Park et al. (agentes generativos de 1.052 personas) | **Relevante y con evidencia.** Es el estado del arte de la línea que el proyecto tiene aplazada |
| [iaexplore — *Simulaciones del mundo real, IA generativa y datos sintéticos*](https://www.iaexplore.com/html/es/blog/ia/simulaciones-mundo-real-ia-generativa-datos-sinteticos.html) | Divulgación sobre sim-to-real en robótica y visión | **No aplica.** Ver §5 |
| Video de YouTube (`1p-DD7_w5_Y`) | — | **No pude leerlo:** la página devolvió 429 dos veces y pidió no reintentar |

---

## 2. El trabajo de Stanford, y el número que importa

Park et al. entrevistaron a **1.052 personas** representativas de EE. UU. durante **dos horas cada una**, con un entrevistador de IA y protocolo semiestructurado. La transcripción completa de cada entrevista se inyecta en el prompt del LLM, y ese agente responde como esa persona.

La métrica es buena y vale la pena entenderla: **precisión normalizada** = qué tan bien el agente predice a la persona, dividido por qué tan bien **la persona se predice a sí misma** dos semanas después. Un 1,0 significa que el agente acierta tanto como la propia persona al repetir el cuestionario.

| Instrumento | Precisión normalizada |
|---|---|
| General Social Survey (actitudes) | **0,85** (sd 0,11) |
| Big Five (personalidad) | **0,80** (sd 1,88) |
| Juegos económicos (**conducta**) | **0,66** (sd 2,83) |
| Réplica de 5 experimentos (tamaños de efecto) | r = 0,98 |

El titular que circula es el 0,85. **El número que decide si esto sirve para este proyecto es el 0,66 — y sobre todo lo que viene con él.**

### 2.1 Las entrevistas no compraron nada para la conducta

Park et al. comparan tres arquitecturas: agentes con entrevista, agentes **solo con demografía**, y agentes con una descripción de persona.

| | GSS |
|---|---|
| Con entrevista de 2 horas | 0,85 |
| **Solo demografía** | **0,71** |
| Descripción de persona | 0,70 |

En actitudes, la entrevista gana claramente (p < 0,001). Pero en los juegos económicos:

> *"there was no significant difference in MAE between the agents for the economic games (F(2, 3153) = 0,12, p = 0,89)."*

**Dos horas de entrevista por persona no predijeron la conducta mejor que la demografía sola.** Ese resultado es el más importante de los tres documentos para nosotros, y va en contra de la lectura entusiasta.

### 2.2 Qué significa para nuestro techo

Nuestros agentes son, exactamente, agentes de demografía: edad, sexo, estrato, educación. El paralelo con el 0,71 de Park no es literal —otra población, otro instrumento, otra métrica— pero marca el orden de magnitud de lo que un LLM añadiría **sin entrevistas**: pasar de un hot-deck sobre variables puente a un LLM sobre las mismas variables puente.

Y ya medimos cuánto pueden esas variables: **las tres juntas explican ~3 % de la varianza de opinión** (D12). Ese techo no lo levanta cambiar el motor que las consume.

### 2.3 Lo bueno que sí aporta, y no es el LLM

Park et al. usan como denominador la **replicación del propio sujeto a dos semanas**. Es un buen patrón de validación, independiente de los LLM: en vez de preguntar "¿cuánto acierta el modelo?", pregunta "¿cuánto acierta comparado con lo que la propia persona logra?".

**No lo podemos aplicar hoy**, y conviene dejarlo escrito: la ECP son **cortes transversales independientes**, no un panel (DATA_INVENTORY §10.2, textual: *"No es un panel en sentido estricto"*). Sin las mismas personas medidas dos veces no hay denominador. Si alguna vez el CNC levanta una ola con re-entrevista, ese diseño se vuelve posible y sería la mejor vara que podríamos tener.

---

## 3. Los modos de falla documentados, y uno que ya nos pasó

La literatura crítica sobre *silicon sampling* documenta fallas que aplican directamente a lo que este proyecto mide:

1. **Varianza artificialmente baja.** Bisbee et al.: las estimaciones de LLM tienen varianza *"far too low"*, lo que produce pruebas de hipótesis y conclusiones incorrectas, con estimaciones *"more certain than they should be"*.
2. **Aplanamiento de subgrupos.** Wang et al.: los LLM *"flatten the representation of identity groups and ignore variation within those groups"*, con respuestas que caen en estereotipo.
3. **Relaciones entre variables mal estimadas**, a veces con **signo opuesto** al de la referencia.
4. **Predicción pobre de preguntas no formuladas**: Kim y Lee reportan acierto en ~12 % de las respuestas reales, y con precisión que varía por nivel socioeconómico y raza.

**El punto 1 ya nos pasó, sin LLM de por medio.** Es DI-M1 / §8.3 de POPULATION_SPECIFICATION: el desempate determinista del hot-deck aplanaba la opinión, los modelos de influencia se veían bien porque *suavizan*, y estaban **cobrando crédito por reparar un artefacto de nuestro propio generador**. El titular del Experimento 4 cayó de 37,5 % a 12,9 % al arreglarlo.

Un proyecto al que ya le pasó eso debería mirar con desconfianza particular a un método cuya falla documentada número uno es la misma. No es razón para descartarlo; es razón para que **cualquier prueba con LLM traiga el control de varianza desde el primer día**, no como verificación posterior.

---

## 4. El obstáculo que no es metodológico

El método de Park requiere **inyectar la transcripción completa de una entrevista de dos horas en el prompt de un LLM**. Aplicado en el CNC, eso choca de frente con R10 y con §12.4 de DATA_INVENTORY, que dice, textual, sobre los microdatos del CNC:

> *"No sacar estas carpetas del equipo ni subirlas a ningún servicio."*

Una transcripción de dos horas es el microdato más identificable que existe: nombres, barrio, trabajo, familia, salud, política, todo en prosa libre. **No hay versión de esto que use una API externa y respete la regla.** Las salidas posibles son un modelo local, o una autorización explícita que hoy no existe. Cualquier conversación sobre agentes generativos en el CNC empieza ahí, no por la metodología.

Y el costo de campo tampoco es menor: 1.052 entrevistas × 2 horas.

---

## 5. Por qué el artículo de iaexplore no aplica

Habla de **sim-to-real**: NeRF, world models, domain randomization, Omniverse, Waymo, Earth-2. Su "dato sintético" son **imágenes y física simuladas para entrenar percepción y control de robots**. Entrenar un robot en un simulador funciona porque la física es conocida y se puede escribir; el problema es cerrar la brecha visual.

Nuestro "dato sintético" es una **población sintética**: personas plausibles construidas por fusión estadística de encuestas reales. La palabra coincide, el problema no. No hay transferencia de método entre los dos.

Además, el artículo **no cita ni una fuente**. Las afirmaciones fuertes —*"la mayoría de los datos de entrenamiento serán sintéticos a fin de esta década"*— van sin respaldo. Como lectura de tendencia está bien; como insumo de diseño no sirve.

---

## 6. Recomendación

**D28 se mantiene: el LLM no entra al núcleo.** Nada en estas fuentes cambia el orden del proyecto, y una de ellas lo refuerza — el hallazgo de que demografía ≈ entrevista para conducta dice que nuestra arquitectura actual no es la parte débil.

Pero hay **una prueba barata, acotada y que responde algo real**, y vale la pena registrarla como candidata:

> **Experimento propuesto — el LLM como donante alterno.**
> Dadas edad, sexo, estrato y educación de una persona de la ECP, pedirle a un LLM el índice de confianza institucional (1–5). Comparar contra el hot-deck **sobre los mismos datos retenidos**, con la misma métrica y el mismo pre-registro.
>
> Responde exactamente una pregunta: *¿un LLM le gana al hot-deck en el único trabajo que el proyecto necesita hoy?*
>
> Controles obligatorios, por §3: comparar **la varianza** de lo donado, no solo la media; y comparar por subgrupo, porque el aplanamiento aparece ahí antes que en el agregado. Si la varianza sale baja, es el defecto conocido y no un modelo mejor.
>
> No requiere entrevistas, no toca microdato del CNC (la ECP es pública) y la población retenida ya existe.

**Lo que NO recomiendo**, y conviene dejarlo escrito para no volver a discutirlo: montar entrevistas de dos horas para construir agentes tipo Park. Aunque el presupuesto apareciera, el resultado de §2.1 dice que lo que compraría es precisión en **actitudes declaradas**, y el cuello de botella del proyecto no es ese.

Ese cuello está medido y está en otra parte: **el movimiento de opinión es exógeno y por periodo**, y cuando dos números exógenos por periodo llegan al piso de ruido muestral, *"no hay dónde aportar"* para un mecanismo social (PROJECT_CONTEXT §25). Agentes más ricos no crean residuo donde no lo hay. Lo que sí levantaría el techo es más resolución —escalar a 100.000 agentes (A08)— o una fuente con panel real.

---

## 7. Qué hacer con esto

1. Anotar en `RESEARCH.md` §41–42 el resultado de §2.1: es evidencia empírica que respalda la decisión que ese documento ya había tomado por argumento.
2. Registrar el experimento del donante alterno como candidato, sin fecha.
3. No abrir la línea de entrevistas.

---

*Documento vivo. Si aparece una fuente con panel real de Bogotá, la sección 2.3 cambia de estado.*
