# RESEARCH.md — BOGOTÁ SOCIAL SIMULATOR

**Proyecto:** Bogotá Social Simulator  
**Organización:** Centro Nacional de Consultoría (CNC)  
**Versión:** 0.1  
**Fecha:** Septiembre de 2026  
**Estado:** Investigación inicial / Estado del arte

---

# 1. OBJETIVO DEL DOCUMENTO

Este documento reúne la investigación inicial relacionada con el proyecto **Bogotá Social Simulator**.

Su propósito es responder cinco preguntas principales:

1. ¿Existen proyectos similares?
2. ¿Cómo se construyen poblaciones sintéticas para simulación social?
3. ¿Cómo se modela la dinámica de opinión mediante agentes?
4. ¿Cómo se calibran y validan estos modelos?
5. ¿Qué metodologías podemos adaptar al caso de Bogotá?

Este documento NO define todavía la arquitectura definitiva del proyecto.

Las decisiones definitivas deberán registrarse posteriormente en:

`PROJECT_CONTEXT.md`

---

# 2. RESUMEN EJECUTIVO

La investigación inicial muestra que la idea de Bogotá Social Simulator tiene antecedentes sólidos en diferentes áreas científicas.

Existen trabajos que combinan:

- poblaciones sintéticas;
- modelos basados en agentes;
- redes sociales;
- datos censales;
- datos de encuestas;
- dinámica de opinión;
- simulación de escenarios;
- movilidad urbana;
- calibración con datos reales.

Sin embargo, también encontramos algo importante:

> **No existe un único modelo estándar que resuelva exactamente nuestro problema.**

La literatura está dividida en diferentes líneas.

Por un lado:

**Synthetic Population + ABM**

permite construir representaciones geográficas y demográficas de ciudades.

Por otro:

**Opinion Dynamics + ABM**

permite estudiar cómo cambian las opiniones mediante interacción social.

Y otra línea trabaja:

**Empirical Data + Opinion Dynamics**

para conectar modelos de opinión con encuestas reales.

La oportunidad del proyecto está precisamente en integrar estas líneas.

---

# 3. MAPA DEL ESTADO DEL ARTE

La arquitectura conceptual que emerge de la literatura puede representarse así:

```text
                 DATOS REALES
                      │
          ┌───────────┼───────────┐
          ↓           ↓           ↓
       CENSO       ENCUESTAS    TERRITORIO
          │           │           │
          └───────────┼───────────┘
                      ↓
              POBLACIÓN SINTÉTICA
                      │
                      ↓
                  AGENTES
                      │
              ┌───────┴───────┐
              ↓               ↓
        CARACTERÍSTICAS     RED SOCIAL
              │               │
              └───────┬───────┘
                      ↓
              DINÁMICA DE OPINIÓN
                      │
                      ↓
                  ESCENARIO
                      │
                      ↓
              MÚLTIPLES RUNS
                      │
                      ↓
                 RESULTADOS
                      │
                      ↓
                 VALIDACIÓN
```

Esta estructura es compatible con el planteamiento inicial de Bogotá Social Simulator.

---

# 4. LÍNEA DE INVESTIGACIÓN 1
# POBLACIONES SINTÉTICAS

## 4.1 ¿Qué es una población sintética?

Una población sintética es una población artificial construida estadísticamente para reproducir determinadas características de una población real.

Los individuos sintéticos no son necesariamente personas reales.

Su objetivo es permitir simulaciones cuando no se dispone de microdatos individuales completos.

La literatura identifica la generación de poblaciones sintéticas como una parte importante de los modelos de simulación social y urbana. Chapuis, Taillandier y Drogoul realizaron una revisión específica de metodologías para generar poblaciones sintéticas en simulación social y señalan que los atributos de los agentes tienen una influencia importante sobre los resultados del modelo.

---

# 5. REVISIÓN SOBRE GENERACIÓN DE POBLACIONES SINTÉTICAS

### Referencia

**Chapuis, K., Taillandier, P. & Drogoul, A.**

"Generation of Synthetic Populations in Social Simulations: A Review of Methods and Practices"

Journal of Artificial Societies and Social Simulation, 2022.

### Hallazgo principal

La revisión identifica diferentes enfoques para construir poblaciones sintéticas y señala problemas recurrentes:

- datos incompletos;
- datos inconsistentes;
- diferentes escalas geográficas;
- falta de información individual;
- dificultad para evaluar la calidad de la población generada.

También diferencia enfoques basados en:

- replicación / combinación de registros;
- muestreo de distribuciones;
- modelos estadísticos;
- técnicas como copulas;
- otros métodos de reconstrucción.

### Relevancia para Bogotá

Esto confirma que no debemos simplemente crear:

```text
edad = random()
sexo = random()
localidad = random()
```

Eso produciría una población artificial sin garantía de coherencia.

La población debe construirse utilizando restricciones y distribuciones observadas.

---

# 6. POBLACIÓN SINTÉTICA + REDES SOCIALES

## Referencia

**Jiang et al. (2022)**

"A method to create a synthetic population with social networks for geographically-explicit agent-based models"

Computational Urban Science.

Este trabajo es especialmente relevante para Bogotá Social Simulator.

Los autores desarrollan una población sintética geográficamente explícita para el área metropolitana de Nueva York e incorporan:

- características demográficas;
- localización;
- hogares;
- lugares de trabajo;
- redes sociales.

Posteriormente utilizan esa población en modelos ABM de:

- tráfico;
- respuesta ante desastres;
- propagación de enfermedades.

---

# 7. LECCIÓN DEL CASO JIANG ET AL.

Una conclusión especialmente importante es:

> **La población sintética puede ser desacoplada del modelo específico.**

Es decir:

```text
Población sintética
       │
       ├── modelo de tráfico
       ├── modelo de desastre
       ├── modelo epidemiológico
       └── otros modelos
```

Esto tiene una consecuencia importante para nuestro proyecto.

No deberíamos construir una población sintética específicamente "para una encuesta".

Deberíamos intentar construir una:

> **infraestructura reutilizable de población sintética de Bogotá.**

Después podemos utilizarla para:

- opinión;
- movilidad;
- comportamiento;
- eventos;
- otros fenómenos.

---

# 8. ESCALA NACIONAL DE POBLACIONES SINTÉTICAS

Un trabajo posterior de Jiang et al. (2024) presenta una población sintética geográficamente explícita de gran escala para Estados Unidos.

Utiliza datos abiertos, incluyendo información del censo de 2020, y genera poblaciones sintéticas con redes asociadas a:

- hogares;
- trabajo;
- escuelas.

El trabajo está orientado a aplicaciones de geo-simulación y futuros urban digital twins.

### Relevancia

Demuestra que la generación de poblaciones sintéticas a gran escala es técnicamente viable.

También muestra que Python puede utilizarse como infraestructura para este tipo de generación.

---

# 9. SINGAPUR — POBLACIÓN SINTÉTICA ESPACIALMENTE DETALLADA

Otro trabajo relevante construye una población sintética para Singapur incorporando:

- heterogeneidad individual;
- hogares;
- características socioeconómicas;
- distribución espacial;
- edificios;
- viviendas;
- establecimientos.

El objetivo es representar un sistema urbano completo a una resolución espacial alta.

### Lección

Una población sintética puede evolucionar desde:

```text
personas
```

hacia:

```text
personas
+
hogares
+
lugares
+
territorio
+
actividades
+
redes
```

Pero esto NO significa que debamos implementar todo en el MVP.

---

# 10. CONCLUSIÓN SOBRE POBLACIÓN SINTÉTICA

La literatura respalda fuertemente la utilización de población sintética para ABM urbanos.

Sin embargo, hay una advertencia importante:

> La calidad de la simulación depende en gran medida de la calidad de la población utilizada para inicializarla.

Por lo tanto:

**La población sintética será un componente científico central del proyecto, no simplemente una estructura de datos.**

---

# 11. MÉTODOS CANDIDATOS

Debemos investigar con mayor profundidad:

### Iterative Proportional Fitting — IPF

Permite ajustar una población a distribuciones marginales conocidas.

### Raking

Método relacionado con el ajuste iterativo de pesos.

### Combinatorial Optimization

Busca una combinación de registros que reproduzca restricciones conocidas.

### Synthetic Reconstruction

Construye agentes a partir de información agregada.

### Copulas

Permiten representar relaciones entre variables.

### Modelos probabilísticos

Permiten generar individuos a partir de distribuciones conjuntas.

### Métodos híbridos

Combinan diferentes fuentes y técnicas.

---

# 12. DECISIÓN PROVISIONAL SOBRE POBLACIÓN SINTÉTICA

No seleccionar todavía el método definitivo.

Primero necesitamos conocer:

- qué microdatos tiene el CNC;
- qué datos agregados existen en DANE;
- qué información existe a nivel localidad;
- qué información existe a nivel UPZ;
- qué variables de opinión están disponibles.

Después se podrá seleccionar el método.

---

# 13. LÍNEA DE INVESTIGACIÓN 2
# AGENT-BASED MODELING

## Concepto

El ABM representa un sistema mediante agentes individuales que poseen:

- atributos;
- estados;
- reglas;
- interacciones.

Los patrones agregados aparecen como resultado de las interacciones individuales.

En nuestro caso:

```text
Agentes
 ↓
Interacción
 ↓
Cambio individual
 ↓
Agregación
 ↓
Patrón social
```

---

# 14. POR QUÉ ABM ES ADECUADO PARA EL PROYECTO

El ABM es especialmente interesante para nuestra propuesta porque queremos representar:

- heterogeneidad;
- diferencias entre individuos;
- redes sociales;
- territorio;
- influencia;
- eventos;
- evolución temporal.

Un modelo agregado tradicional podría representar directamente:

```text
opinión Bogotá = 53%
```

pero tendría dificultades para representar:

```text
individuo A
influye en B

B influye en C

C pertenece a otro grupo

D cambia su opinión después de un evento
```

El ABM permite representar este nivel micro.

---

# 15. LIMITACIÓN DEL ABM

ABM no significa automáticamente realismo.

Un modelo con:

```text
100.000 agentes
```

puede ser peor que uno con:

```text
1.000 agentes
```

si sus reglas son arbitrarias.

La complejidad computacional no sustituye la evidencia empírica.

Esta será una regla importante para el proyecto.

---

# 16. LÍNEA DE INVESTIGACIÓN 3
# OPINION DYNAMICS

La dinámica de opinión estudia cómo las opiniones individuales evolucionan como consecuencia de:

- interacción social;
- influencia;
- información;
- experiencia;
- contexto.

La literatura distingue modelos:

- discretos;
- continuos;
- basados en consenso;
- basados en polarización;
- basados en confianza limitada;
- modelos con agentes resistentes al cambio.

Una revisión de modelos no estratégicos de dinámica de opinión incluye modelos como:

- DeGroot;
- Friedkin-Johnsen;
- Hegselmann-Krause;
- Deffuant;
- voter model;
- threshold models.

---

# 17. MODELO DEGROOT

En términos conceptuales:

Cada agente actualiza su opinión como una combinación ponderada de las opiniones de otros agentes.

```text
opinión nueva =
Σ peso_j × opinión_j
```

### Ventajas

- simple;
- interpretable;
- matemáticamente estudiado;
- fácil de implementar;
- útil como baseline.

### Problema

Puede producir consenso bajo determinadas condiciones.

Eso puede ser poco realista para determinados fenómenos de opinión.

### Uso recomendado

**Baseline inicial.**

No necesariamente modelo final.

---

# 18. MODELO FRIEDKIN-JOHNSEN

Introduce la idea de que algunas personas mantienen parte de su opinión inicial.

Conceptualmente:

```text
opinión nueva =
influencia social
+
persistencia de opinión propia
```

Esto permite representar individuos más resistentes al cambio.

### Ventaja

Más realista que un modelo donde todos cambian de la misma manera.

### Relevancia para Bogotá

Podría ser interesante si las encuestas muestran grupos con alta estabilidad actitudinal.

---

# 19. BOUNDED CONFIDENCE

Los agentes no necesariamente escuchan a todo el mundo.

Solo consideran opiniones suficientemente cercanas a la propia.

Conceptualmente:

```text
si |opinión_i - opinión_j| < umbral
        interactúan
```

Esto puede producir:

- consenso;
- clusters;
- fragmentación.

La literatura identifica este tipo de modelos como una de las principales familias de dinámica de opinión.

---

# 20. HEGSELMANN-KRAUSE

Es una formulación de bounded confidence donde los agentes consideran el conjunto de opiniones dentro de un determinado rango.

Puede producir agrupaciones de opinión.

### Utilidad

Podría utilizarse para estudiar:

- polarización;
- segmentación;
- formación de clusters;
- convergencia.

### Riesgo

Puede ser demasiado abstracto si no se incorporan características empíricas.

---

# 21. DEFFUANT

Otro enfoque de confianza limitada basado en interacciones por pares.

Puede ser útil para construir un prototipo pequeño.

---

# 22. MODELOS CON HOMOFILIA

Una idea importante para nuestro proyecto es:

> Las personas no interactúan aleatoriamente con toda la población.

Pueden tener mayor probabilidad de interacción con personas:

- similares;
- cercanas;
- pertenecientes al mismo grupo;
- relacionadas laboralmente;
- pertenecientes al mismo entorno social.

La literatura de población sintética geográficamente explícita muestra la importancia de incorporar redes sociales a los agentes urbanos.

---

# 23. OPINIÓN + DATOS EMPÍRICOS

Uno de los trabajos más relevantes para nuestro proyecto es:

**Stefanelli & Seidl (2017)**

"Opinion Communication on Contested Topics"

El estudio combina:

- ABM;
- datos empíricos;
- teoría sociopsicológica;
- dinámica de opinión.

Utilizaron datos de un cuestionario online de 841 participantes para inicializar el modelo.

### Por qué es importante

Demuestra que es posible conectar:

```text
encuesta real
      ↓
agentes
      ↓
modelo de interacción
      ↓
simulación
```

Esto se parece directamente a la lógica propuesta para el CNC.

---

# 24. OPINIÓN + CASO REAL

Otro trabajo:

**"Opinions on contested energy infrastructures: An empirically based simulation approach"**

utilizó un caso real relacionado con infraestructura energética en Suiza.

Los autores utilizaron un cuestionario longitudinal para inicializar el modelo y representar cambios de opinión a lo largo del tiempo.

### Lección

El modelo no tiene por qué empezar con opiniones aleatorias.

Puede partir de una distribución observada.

Esto es fundamental para nuestro proyecto.

---

# 25. OPINIÓN + POLARIZACIÓN

Li & Jager (2023) desarrollaron un ABM sobre opinión respecto a vacunación contra COVID-19.

El modelo incorporó:

- miedo;
- heurística de disponibilidad;
- sesgo de confirmación;
- procesamiento de información.

Además evaluó diferentes escenarios para estudiar su impacto sobre la polarización.

### Lección

El simulador puede representar escenarios modificando mecanismos específicos.

Por ejemplo:

```text
Escenario A:
baja exposición

Escenario B:
alta exposición

Escenario C:
alta polarización

Escenario D:
autoridad moderadora
```

Esto se parece mucho al concepto de laboratorio de escenarios que queremos desarrollar.

---

# 26. OPINIÓN + ENCUESTAS A GRAN ESCALA

Un trabajo reciente desarrolló un ABM que integra dinámica de opinión con un modelo epidemiológico.

Los autores calibraron el modelo utilizando:

- datos de encuestas YouGov;
- datos de la OMS;
- 15 países.

El modelo estudió cómo las opiniones sobre intervenciones preventivas afectaban el comportamiento y, posteriormente, los resultados epidemiológicos.

### Lección principal

La opinión puede ser tratada como una variable dinámica que interactúa con otros fenómenos.

Esto abre la posibilidad futura de pasar de:

```text
opinión
```

a:

```text
opinión
 ↓
comportamiento
 ↓
evento social
```

Pero no debemos implementar esa complejidad inicialmente.

---

# 27. CALIBRACIÓN DE OPINION DYNAMICS

Encontramos un trabajo especialmente importante:

**Gestefeld & Lorenz (2023)**

"Calibrating an Opinion Dynamics Model to Empirical Opinion Distributions and Transitions"

El trabajo destaca que muchos modelos de opinión se validan únicamente mostrando que producen fenómenos como:

- consenso;
- polarización;
- fragmentación.

Pero eso no necesariamente significa que reproduzcan datos reales.

Los autores proponen calibrar el modelo utilizando:

- distribuciones de opiniones observadas;
- transiciones de opinión observadas.

---

# 28. IMPLICACIÓN PARA NUESTRO PROYECTO

Esta es probablemente una de las conclusiones más importantes del estado del arte.

No será suficiente demostrar:

> "Nuestro modelo produce polarización."

Debemos intentar demostrar:

> "Nuestro modelo reproduce razonablemente patrones observados de opinión."

Esto cambia completamente el enfoque de validación.

---

# 29. VALIDACIÓN

La validación debería tener varias capas.

## Nivel 1 — Población

¿La población sintética reproduce Bogotá?

```text
edad real vs sintética
sexo real vs sintética
localidad real vs sintética
```

---

## Nivel 2 — Estado inicial

¿La distribución inicial de opiniones coincide con los datos?

```text
opinión real
vs
opinión sintética
```

---

## Nivel 3 — Dinámica

¿El modelo reproduce cambios observados?

```text
t0 → t1 → t2
```

---

## Nivel 4 — Escenario

¿Los resultados responden de manera coherente cuando cambian los supuestos?

---

## Nivel 5 — Generalización

¿Funciona el modelo fuera del periodo utilizado para calibrarlo?

---

# 30. BACKTESTING

La estrategia propuesta:

```text
Datos históricos
      ↓
Periodo de entrenamiento
      ↓
Calibración
      ↓
Simulación
      ↓
Periodo no utilizado
      ↓
Comparación
```

Esto permite evitar una validación circular.

---

# 31. MÉTRICAS

Las métricas dependerán de la variable de opinión.

Posibles:

### MAE

Error absoluto medio.

### RMSE

Penaliza errores grandes.

### Correlación

Evalúa si el modelo sigue correctamente la tendencia.

### Error por segmento

Por ejemplo:

```text
Localidad
Edad
Sexo
Educación
```

### Cobertura

Si generamos intervalos:

```text
¿El valor observado cae dentro del intervalo?
```

---

# 32. INCERTIDUMBRE

La literatura y la naturaleza estocástica del ABM hacen necesario ejecutar múltiples simulaciones.

Por ejemplo:

```text
Escenario A

Run 1 → 48%
Run 2 → 52%
Run 3 → 49%
...
Run 500 → 51%
```

La salida debe ser:

```text
Distribución de resultados
```

y no únicamente:

```text
resultado = 51%
```

---

# 33. POBLACIÓN SINTÉTICA Y VALIDACIÓN

La población sintética debe validarse independientemente del modelo social.

Esto significa que:

```text
Población sintética
```

debe ser validada antes de:

```text
Población sintética
+
modelo de opinión
```

Esto permite separar errores.

Si el modelo falla:

### Posibilidad A

La población sintética está mal.

### Posibilidad B

La red social está mal.

### Posibilidad C

La regla de opinión está mal.

### Posibilidad D

Los datos no son suficientes.

---

# 34. DIGITAL TWINS

La literatura muestra un creciente interés en los llamados:

**Urban Digital Twins**

Estos pueden integrar:

- datos urbanos;
- modelos;
- simulación;
- infraestructura;
- movilidad;
- comportamiento.

Sin embargo, el término Digital Twin debe utilizarse con cuidado.

Una revisión reciente sobre digital twins urbanos señala que los ABM pueden aportar una dimensión social mediante representación de actividades humanas y poblaciones sintéticas.

---

# 35. DIGITAL TWIN DE MOVILIDAD

Un trabajo reciente sobre Washington D.C. construyó una población sintética de más de cuatro millones de residentes utilizando datos públicos y la integró con MATSim para crear un "Digital Urban Mobility Twin".

El modelo fue comparado contra:

- tráfico real;
- flujos de transporte público.

Los resultados mostraron similitud entre flujos simulados y observados.

### Lección

Esto demuestra que el enfoque:

```text
datos públicos
 ↓
población sintética
 ↓
ABM
 ↓
validación contra datos reales
```

es aplicable a ciudades reales.

---

# 36. BOGOTÁ — OPORTUNIDAD

El caso Bogotá es interesante porque podemos combinar potencialmente:

```text
DANE
+
Datos Bogotá
+
Encuestas CNC
```

Esto permitiría construir diferentes capas:

```text
DEMOGRAFÍA
TERRITORIO
OPINIÓN
```

y posteriormente:

```text
MOVILIDAD
COMPORTAMIENTO
EVENTOS
```

---

# 37. ARQUITECTURA DE DATOS PROPUESTA

La investigación sugiere una arquitectura por capas.

```text
                 DATOS
                   │
       ┌───────────┼───────────┐
       ↓           ↓           ↓
     DANE         CNC       BOGOTÁ
       │           │           │
       └───────────┼───────────┘
                   ↓
             DATA LAYER
                   ↓
         POBLACIÓN SINTÉTICA
                   ↓
             AGENT LAYER
                   ↓
          SOCIAL NETWORK
                   ↓
          OPINION MODEL
                   ↓
             SCENARIOS
                   ↓
             SIMULATION
                   ↓
             VALIDATION
```

---

# 38. LÍNEA DE INVESTIGACIÓN 4
# ESCENARIOS

Una característica común en los modelos ABM es la posibilidad de modificar parámetros y estudiar resultados emergentes.

Para Bogotá Social Simulator esto debería convertirse en una función central.

Ejemplo:

```text
ESCENARIO BASE
```

vs.

```text
ESCENARIO A
Aumento de inseguridad
```

vs.

```text
ESCENARIO B
Aumento de confianza institucional
```

vs.

```text
ESCENARIO C
Evento de alto impacto
```

---

# 39. TIPOS DE ESCENARIO

Podemos clasificarlos como:

### Escenario externo

Modifica el entorno.

### Escenario informativo

Modifica exposición a información.

### Escenario social

Modifica interacción.

### Escenario territorial

Afecta determinadas localidades.

### Escenario demográfico

Modifica composición.

### Escenario institucional

Introduce actores o mensajes institucionales.

---

# 40. ESCENARIOS NO SON PREDICCIONES

Esta distinción debe permanecer en toda la plataforma.

Un escenario significa:

> "Si asumimos X, Y y Z, ¿qué comportamiento produce el modelo?"

No significa:

> "Esto va a suceder."

---

# 41. LÍNEA DE INVESTIGACIÓN 5
# LLM Y AGENTES GENERATIVOS

La investigación reciente muestra un crecimiento importante de sistemas de agentes basados en LLM para simulación de opinión pública.

Un trabajo publicado en 2026 propone utilizar sistemas multiagente basados en LLM para simular difusión de opinión pública.

También existen trabajos recientes que exploran poblaciones sintéticas y agentes LLM para inteligencia de reputación y simulación social.

---

# 42. DECISIÓN SOBRE LLM

A pesar de esta tendencia:

**NO utilizar LLM como núcleo del MVP.**

Razones:

1. Mayor costo computacional.
2. Menor reproducibilidad.
3. Mayor dificultad de calibración.
4. Mayor dificultad para validar causalmente.
5. Mayor complejidad metodológica.

Primero:

```text
ABM clásico
+
datos reales
+
calibración
+
validación
```

Después:

```text
ABM
+
LLM
```

como experimento.

---

# 43. COMPARACIÓN DE ENFOQUES

| Enfoque | Ventaja | Problema | Relevancia |
|---|---|---|---|
| Modelo agregado | Simple | Pierde heterogeneidad | Alta como baseline |
| Regresión | Interpretable | Limitada para interacción | Alta como baseline |
| DeGroot | Simple | Puede converger a consenso | Alta |
| Friedkin-Johnsen | Persistencia | Requiere parámetros | Alta |
| Bounded Confidence | Polarización/clusters | Puede ser abstracto | Muy alta |
| ABM empírico | Flexible | Más complejo | Muy alta |
| ABM + población sintética | Escalable | Requiere buenos datos | Muy alta |
| ABM + LLM | Comportamiento rico | Difícil validar | Futura |

---

# 44. PROYECTOS / TRABAJOS MÁS RELEVANTES

## R01 — Jiang et al. 2022

**Synthetic Population + Social Networks + ABM**

Área:

Urban simulation.

Aporte:

Población sintética geográfica con redes sociales.

Aplicaciones:

- tráfico;
- desastres;
- enfermedades.

Relevancia:

★★★★★



---

## R02 — Chapuis et al. 2022

**Synthetic Population Review**

Área:

Social simulation.

Aporte:

Revisión metodológica de generación de poblaciones sintéticas.

Relevancia:

★★★★★



---

## R03 — Stefanelli & Seidl 2017

**Opinion Communication on Contested Topics**

Área:

Opinión pública.

Aporte:

ABM + encuesta real + teoría sociopsicológica.

Relevancia:

★★★★★



---

## R04 — Opinions on Contested Energy Infrastructures

Área:

Opinión pública.

Aporte:

ABM empíricamente basado + cuestionario longitudinal.

Relevancia:

★★★★★



---

## R05 — Gestefeld & Lorenz 2023

**Calibrating an Opinion Dynamics Model to Empirical Opinion Distributions and Transitions**

Área:

Calibración.

Aporte:

Conectar ABM de opinión con datos empíricos reales.

Relevancia:

★★★★★



---

## R06 — Li & Jager 2023

**COVID Vaccination Opinion Dynamics**

Área:

Polarización.

Aporte:

Escenarios sobre miedo, sesgo de confirmación y autoridad.

Relevancia:

★★★★☆



---

## R07 — Opinion + Epidemic ABM

Área:

Opinión + comportamiento.

Aporte:

Calibración con YouGov y OMS en 15 países.

Relevancia:

★★★★☆



---

## R08 — Washington D.C. Urban Mobility Twin

Área:

Digital Twin / movilidad.

Aporte:

Población sintética de millones de agentes + ABM + validación contra movilidad real.

Relevancia:

★★★★☆



---

# 45. PATRÓN COMÚN EN LOS CASOS EXITOSOS

Los proyectos más sólidos siguen una estructura parecida:

```text
DATOS
 ↓
POBLACIÓN / AGENTES
 ↓
REGLAS
 ↓
SIMULACIÓN
 ↓
VALIDACIÓN
```

Los proyectos más interesantes para nosotros agregan:

```text
DATOS EMPÍRICOS
 ↓
CALIBRACIÓN
 ↓
SIMULACIÓN
```

Esto refuerza la decisión de no empezar por una interfaz o una visualización 3D.

---

# 46. LO QUE NO DEBEMOS HACER

La revisión también muestra varios riesgos.

## No crear agentes aleatorios

```text
random(age)
random(opinion)
```

sin restricciones.

---

## No validar únicamente visualmente

Que una gráfica "se vea realista" no es validación.

---

## No demostrar únicamente polarización

Un modelo que produce polarización no demuestra que la sociedad real funcione así.

---

## No utilizar únicamente datos sintéticos

La población sintética debe estar fundamentada en datos observados.

---

## No introducir LLM prematuramente

El realismo aparente no sustituye la validación.

---

## No asumir causalidad

Correlación en encuestas ≠ causalidad.

---

# 47. PROPUESTA METODOLÓGICA DERIVADA DEL RESEARCH

A partir de la literatura, la arquitectura metodológica que parece más defendible es:

```text
                 DANE
                   │
                   ├──── Demografía
                   │
                 BOGOTÁ
                   │
                   ├──── Territorio
                   │
                  CNC
                   │
                   ├──── Opinión
                   │
                   └──── Sociodemografía
                        │
                        ↓
              POBLACIÓN SINTÉTICA
                        │
                        ↓
                 RED SOCIAL
                        │
                        ↓
              OPINION DYNAMICS
                        │
                        ↓
                   ESCENARIO
                        │
                        ↓
                 100+ RUNS
                        │
                        ↓
                  RESULTADOS
                        │
                        ↓
                   VALIDACIÓN
```

---

# 48. PROPUESTA DE MVP METODOLÓGICO

No iniciar con 100.000 agentes.

Primero:

```text
1.000 agentes
```

con:

### Variables

- edad;
- sexo;
- localidad;
- una variable socioeconómica;
- una variable de opinión.

### Interacción

Una red simple.

### Modelo

Comparar:

- DeGroot;
- Friedkin-Johnsen;
- bounded confidence.

### Simulación

100–500 runs.

### Salidas

- distribución;
- media;
- mediana;
- evolución;
- polarización;
- segmentación territorial.

---

# 49. EXPERIMENTO 1

## Pregunta

¿Puede un modelo simple de opinión reproducir una distribución objetivo?

### Entrada

Población sintética.

### Estado inicial

Distribución de opinión basada en datos.

### Interacción

Red social simple.

### Modelo

Primer modelo candidato.

### Salida

Distribución después de:

```text
10
20
50
100
```

iteraciones.

### Evaluación

Comparar:

```text
distribución inicial
vs
distribución final
```

y posteriormente:

```text
modelo
vs
datos históricos
```

---

# 50. EXPERIMENTO 2

## Pregunta

¿Cómo cambia el resultado cuando modificamos la estructura social?

Comparar:

```text
Red aleatoria
```

vs.

```text
Red homofílica
```

vs.

```text
Red territorial
```

### Objetivo

Determinar cuánto importa la estructura de interacción.

---

# 51. EXPERIMENTO 3

## Pregunta

¿Cuánto importa la heterogeneidad individual?

Comparar:

```text
Modelo homogéneo
```

vs.

```text
Modelo heterogéneo
```

Por ejemplo, permitir diferentes:

- tasas de cambio;
- susceptibilidad;
- confianza;
- influencia.

---

# 52. EXPERIMENTO 4

## Pregunta

¿El ABM aporta información adicional respecto a modelos simples?

Comparar:

```text
Baseline histórico
```

```text
Regresión
```

```text
DeGroot
```

```text
Friedkin-Johnsen
```

```text
ABM con heterogeneidad
```

La comparación será fundamental para justificar el proyecto.

---

# 53. EXPERIMENTO 5

## Escenarios

Después de validar el modelo:

```text
Escenario Base
```

vs.

```text
Escenario Evento
```

vs.

```text
Escenario Evento + Alta Influencia
```

vs.

```text
Escenario Evento + Baja Influencia
```

El objetivo no es encontrar "el futuro".

Es estudiar:

> cómo cambian los resultados cuando cambian los supuestos.

---

# 54. VARIABLES INICIALES RECOMENDADAS

No todas están confirmadas.

### Alta prioridad

- edad;
- sexo;
- localidad;
- opinión inicial.

### Prioridad media

- educación;
- situación laboral;
- estrato / indicador socioeconómico.

### Futuras

- confianza institucional;
- exposición a información;
- afinidad;
- movilidad;
- actividad;
- red social.

---

# 55. VARIABLES DE OPINIÓN

No debemos elegir arbitrariamente una pregunta de encuesta.

El primer fenómeno debe cumplir:

1. Tener datos suficientes.
2. Tener mediciones en más de un momento si es posible.
3. Tener suficiente variación.
4. Tener relevancia para el CNC.
5. Tener una interpretación clara.
6. Poder convertirse en una variable dinámica.

Idealmente:

```text
t0
t1
t2
t3
```

para poder estudiar transiciones.

---

# 56. DATO IDEAL DEL CNC

La investigación permite establecer qué sería especialmente valioso obtener del CNC.

Idealmente necesitamos:

### Identificador anónimo

Para relacionar observaciones dentro de un panel, si existe.

### Tiempo

Fecha o periodo.

### Opinión

Variable objetivo.

### Sociodemografía

Variables para segmentación.

### Territorio

Localidad o granularidad compatible.

### Expansión

Factor de expansión / ponderación si existe.

### Repetición

Preferiblemente datos longitudinales o varias mediciones comparables.

---

# 57. DATO MÍNIMO DEL CNC

Si no existe panel longitudinal, todavía podemos trabajar.

Mínimo:

```text
opinión
+
fecha
+
sociodemografía
+
territorio
```

pero la validación será más limitada.

---

# 58. GRANULARIDAD TERRITORIAL

Primera versión:

**Localidad.**

Motivo:

- relativamente interpretable;
- manejable;
- facilita visualización;
- permite segmentación.

Posteriormente:

**UPZ**

si los datos lo permiten.

---

# 59. NÚMERO DE AGENTES

La propuesta inicial era:

**100.000.**

La investigación NO permite todavía afirmar que este sea el número correcto.

Se debe hacer benchmark:

```text
1K
10K
50K
100K
500K
```

evaluando:

- tiempo;
- memoria;
- estabilidad;
- precisión;
- resultados.

---

# 60. NÚMERO DE RUNS

Propuesta inicial:

```text
100–1.000
```

Pero tampoco está decidido.

Se debe estudiar convergencia:

```text
10 runs
50 runs
100 runs
250 runs
500 runs
1000 runs
```

y observar cuándo las estadísticas dejan de cambiar significativamente.

---

# 61. ARQUITECTURA TECNOLÓGICA

La investigación no obliga a utilizar una tecnología específica.

Sin embargo, la propuesta inicial continúa siendo:

### Python

Motor científico.

### Mesa

Framework candidato ABM.

### PostgreSQL/PostGIS

Datos espaciales.

### FastAPI

API.

### React

Dashboard.

### Leaflet/Mapbox

Mapas.

---

# 62. TECNOLOGÍAS QUE DEBEN INVESTIGARSE

Antes de construir el sistema comparar:

### Mesa

ABM en Python.

### MASON

ABM en Java.

### GAMA

Plataforma de simulación espacial.

### NetLogo

Muy utilizado para simulación social.

### Repast

Framework ABM.

### MATSim

Especialmente relevante si posteriormente incorporamos movilidad.

---

# 63. RECOMENDACIÓN TECNOLÓGICA PROVISIONAL

Para el MVP:

**Python + Mesa**

es una opción razonable debido a:

- integración con ciencia de datos;
- facilidad de experimentación;
- ecosistema Python;
- posibilidad de conectar NumPy/Pandas/SciPy;
- facilidad de integración posterior con API.

Pero debe compararse formalmente antes de fijarla.

---

# 64. ARQUITECTURA FUTURA

La visión futura puede ser:

```text
                    DATA SOURCES
                         │
             ┌───────────┼───────────┐
             ↓           ↓           ↓
            DANE        CNC       BOGOTÁ
             │           │           │
             └───────────┼───────────┘
                         ↓
                  DATA PLATFORM
                         ↓
                SYNTHETIC POPULATION
                         ↓
                    ABM ENGINE
                         ↓
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
     OPINION         BEHAVIOR         MOBILITY
        │                │                │
        └────────────────┼────────────────┘
                         ↓
                    SCENARIOS
                         ↓
                    SIMULATIONS
                         ↓
                    ANALYTICS
                         ↓
                    DASHBOARD
```

---

# 65. PRINCIPALES VACÍOS DE INVESTIGACIÓN

La revisión revela que todavía necesitamos estudiar:

### G01

¿Cómo construir población sintética específicamente para Bogotá?

### G02

¿Cómo combinar datos agregados DANE con datos de encuestas CNC?

### G03

¿Cómo asignar opiniones individuales cuando las encuestas no contienen suficiente información?

### G04

¿Cómo construir una red social plausible sin disponer de redes sociales individuales?

### G05

¿Cómo calibrar la dinámica de opinión?

### G06

¿Cómo validar escenarios hipotéticos?

### G07

¿Cómo medir incertidumbre estructural?

### G08

¿Cómo demostrar valor adicional frente a modelos estadísticos tradicionales?

---

# 66. PRINCIPAL DESAFÍO CIENTÍFICO

El desafío no es:

> "Crear 100.000 agentes."

El verdadero desafío es:

> **Crear agentes que representen razonablemente la heterogeneidad de la población y cuyas interacciones produzcan dinámicas que puedan compararse con evidencia real.**

---

# 67. PRINCIPAL DESAFÍO DE DATOS

El mayor riesgo actualmente es no conocer todavía:

> **qué información del CNC estará disponible para alimentar y validar el modelo.**

Por eso la siguiente etapa debe incluir una auditoría de datos.

---

# 68. PRINCIPAL DESAFÍO DE MODELADO

El modelo debe resolver el problema:

```text
¿Qué hace que una persona cambie de opinión?
```

No basta con:

```text
opinión nueva = promedio de vecinos
```

Debemos determinar si existen variables que permitan representar:

- susceptibilidad;
- confianza;
- afinidad;
- persistencia;
- exposición;
- contexto;
- experiencia.

---

# 69. PRINCIPAL DESAFÍO DE VALIDACIÓN

La pregunta más importante será:

> ¿Cómo sabemos que el simulador está haciendo algo útil?

La respuesta no puede ser:

> "Porque genera resultados razonables."

Debe existir comparación cuantitativa contra datos observados.

---

# 70. DECISIONES PROVISIONALES DERIVADAS DEL RESEARCH

## R01

La población sintética será un componente central del proyecto.

## R02

La población deberá validarse independientemente del modelo de opinión.

## R03

El modelo de opinión debe estar fundamentado en literatura científica.

## R04

El primer modelo debería ser relativamente simple e interpretable.

## R05

Debemos comparar varios modelos antes de elegir uno.

## R06

El ABM debe compararse contra baselines simples.

## R07

La calibración con datos reales será prioritaria.

## R08

La validación debe incluir backtesting cuando los datos lo permitan.

## R09

Los escenarios deben generar distribuciones de resultados.

## R10

LLM queda como extensión futura.

## R11

La movilidad queda fuera del MVP.

## R12

La población sintética debe diseñarse para poder reutilizarse posteriormente.

---

# 71. MODELO CONCEPTUAL RECOMENDADO

Por ahora, la mejor hipótesis de arquitectura metodológica es:

```text
              POBLACIÓN REAL
                    │
           ┌────────┴────────┐
           ↓                 ↓
      DEMOGRAFÍA          OPINIÓN
           │                 │
           └────────┬────────┘
                    ↓
           POBLACIÓN SINTÉTICA
                    ↓
                  AGENTES
                    ↓
             RED DE INTERACCIÓN
                    ↓
             OPINION DYNAMICS
                    ↓
                ESCENARIO
                    ↓
             MULTIPLE RUNS
                    ↓
              DISTRIBUCIÓN
                    ↓
               VALIDACIÓN
                    ↓
             DATOS OBSERVADOS
```

---

# 72. PRÓXIMA INVESTIGACIÓN

La siguiente etapa debe abandonar temporalmente la literatura general y concentrarse en **Bogotá y Colombia**.

Necesitamos investigar específicamente:

### DANE

- proyecciones de población;
- censos;
- hogares;
- vivienda;
- variables sociodemográficas.

### Bogotá

- localidades;
- UPZ;
- población;
- indicadores;
- datos abiertos;
- movilidad.

### CNC

Determinar qué información sería necesaria para:

- inicialización;
- calibración;
- validación.

---

# 73. DATA AUDIT

La siguiente investigación debe producir una tabla:

| Fuente | Dataset | Año | Variables | Granularidad | Tipo | Uso |
|---|---|---:|---|---|---|---|
| DANE | Por investigar | | | | Demografía | Población |
| Bogotá | Por investigar | | | | Territorial | Spatial |
| CNC | Por investigar | | | | Opinión | Modelo |
| Bogotá | Movilidad | | | | Movilidad | Futuro |

---

# 74. CRITERIO PARA SELECCIONAR DATASETS

Un dataset será evaluado mediante:

```text
Cobertura
Granularidad
Actualidad
Calidad
Representatividad
Disponibilidad
Compatibilidad
Privacidad
Utilidad
```

---

# 75. REFERENCIAS PRINCIPALES

## Población sintética

Jiang, N., Crooks, A. T., Kavak, H., Burger, A. et al. (2022).  
"A method to create a synthetic population with social networks for geographically-explicit agent-based models."  
Computational Urban Science.

Chapuis, K., Taillandier, P., & Drogoul, A. (2022).  
"Generation of Synthetic Populations in Social Simulations: A Review of Methods and Practices."  
Journal of Artificial Societies and Social Simulation.

Jiang, N., Yin, F., Wang, B., Crooks, A. T. et al. (2024).  
"A Large-Scale Geographically Explicit Synthetic Population with Social Networks for the United States."  
Scientific Data.

---

## Opinion Dynamics

" A Survey on Nonstrategic Models of Opinion Dynamics."  
Games, 2020.

Gestefeld, M. & Lorenz, J. (2023).  
"Calibrating an Opinion Dynamics Model to Empirical Opinion Distributions and Transitions."  
Journal of Artificial Societies and Social Simulation.

Stefanelli, A. & Seidl, R. (2017).  
"Opinion Communication on Contested Topics: How Empirics and Arguments can Improve Social Simulation."  
Journal of Artificial Societies and Social Simulation.

"Opinions on contested energy infrastructures: An empirically based simulation approach."  
Journal of Environmental Psychology, 2017.

Li, T. & Jager, W. (2023).  
"How Availability Heuristic, Confirmation Bias and Fear May Drive Societal Polarisation."  
Journal of Artificial Societies and Social Simulation.

---

## Urban Simulation

"Synthetic population and urban mobility modeling using open and publicly available data — a Washington, DC COVID case study."  
Computational Urban Science, 2025.

"Creating spatially-detailed heterogeneous synthetic populations for agent-based microsimulation."  
Computers, Environment and Urban Systems.

---

# 76. ESTADO DEL RESEARCH

## Lo que ya sabemos

Existe evidencia científica suficiente para justificar investigar:

**Synthetic Population + ABM + Opinion Dynamics + Empirical Data.**

---

## Lo que todavía NO sabemos

No sabemos todavía:

- qué modelo será mejor para Bogotá;
- qué variables tenemos disponibles;
- qué población sintética podremos construir;
- qué red social podremos representar;
- qué variable de opinión será el primer caso;
- qué tan bien podremos validar el modelo.

---

# 77. CONCLUSIÓN

La investigación inicial respalda la viabilidad conceptual del proyecto.

Sin embargo, el mayor aprendizaje es que el proyecto no debería venderse inicialmente como:

> **"Una IA que predice lo que pensará Bogotá."**

La formulación científicamente más defendible es:

> **"Una plataforma de simulación social basada en agentes y una población sintética de Bogotá que permite explorar escenarios de opinión pública y contrastar sus dinámicas con datos observados."**

El valor diferencial potencial del proyecto estaría en conectar:

```text
DATOS REALES
     +
POBLACIÓN SINTÉTICA
     +
DINÁMICA SOCIAL
     +
ESCENARIOS
     +
VALIDACIÓN
```

Esto puede convertirse en una capacidad complementaria para investigación social y opinión pública dentro del CNC.

---

# 78. SIGUIENTE PASO RECOMENDADO

La siguiente etapa NO debería ser todavía programar el ABM.

Debe ser:

# DATA AUDIT — BOGOTÁ

Investigar y documentar exactamente:

1. Qué datos demográficos existen para Bogotá.
2. Qué datos territoriales existen.
3. Qué datos de opinión pública pueden utilizarse.
4. Qué datos históricos permiten calibración.
5. Qué variables debería solicitarse al CNC.
6. Qué granularidad tienen los datos.
7. Qué variables pueden combinarse.
8. Qué restricciones de privacidad existen.

El resultado debe convertirse en:

**`DATA_SPECIFICATION.md`**

Este documento será el puente entre:

```text
RESEARCH.md
       ↓
DATA_SPECIFICATION.md
       ↓
MODEL_SPECIFICATION.md
```

Solo después de completar esa etapa deberíamos seleccionar definitivamente el método de población sintética y el modelo de dinámica de opinión.