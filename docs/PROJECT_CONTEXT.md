# PROJECT CONTEXT — BOGOTÁ SOCIAL SIMULATOR

**Proyecto:** Bogotá Social Simulator  
**Organización:** Centro Nacional de Consultoría (CNC)  
**Tipo:** Investigación aplicada / simulación social / ciencia de datos  
**Estado:** Método cerrado; el proyecto se reorienta hacia una capa visual e interactiva (ver sección 51)  
**Versión del contexto:** 0.18  
**Fecha:** Septiembre de 2026 (actualizado: reorientación hacia la capa visual — el mapa interactivo de Bogotá pasa a ser el frente principal)  
**Ciudad piloto:** Bogotá D.C., Colombia

---

# 1. RESUMEN DEL PROYECTO

**Bogotá Social Simulator** es una propuesta de investigación y desarrollo para construir un entorno computacional capaz de representar una población sintética de Bogotá y simular la evolución de determinadas variables sociales, inicialmente enfocadas en **opinión pública**.

El proyecto utilizará un enfoque de **Agent-Based Modeling (ABM)**, en el cual cada agente representa una persona sintética con determinadas características demográficas, sociales y de opinión.

El objetivo no es crear una representación individual de personas reales ni afirmar que el sistema puede predecir el futuro con certeza.

El objetivo inicial es construir un:

> **laboratorio computacional para explorar escenarios sociales y estudiar posibles cambios en la opinión pública bajo diferentes supuestos.**

**Nota de la v0.7.** Esa frase — "laboratorio", no "predictor" — dejó de ser una precaución retórica y pasó a ser el resultado de una medición. El Experimento 3 mostró que el modelo no reproduce la trayectoria observada de confianza institucional en Bogotá mejor que congelarla, salvo marginalmente; y tres fuentes independientes mostraron que no hay atributo observable —ni demográfico ni territorial— que estructure la opinión individual en Bogotá. Ver secciones 25, 39 (D15) y 43.

---

# 2. CONTEXTO

El proyecto surge como una posible línea de innovación dentro del Centro Nacional de Consultoría.

El CNC cuenta con experiencia en investigación de opinión pública, encuestas y análisis social.

La propuesta busca explorar cómo complementar estas capacidades mediante:

- población sintética;
- simulación basada en agentes;
- modelos de dinámica de opinión;
- datos demográficos;
- datos territoriales;
- simulaciones de escenarios;
- análisis de incertidumbre.

La hipótesis general es que la simulación computacional podría complementar la medición tradicional permitiendo formular preguntas del tipo:

> **"¿Qué podría pasar si...?"**

---

# 3. PROBLEMA

Las encuestas permiten observar:

- opinión;
- percepción;
- preferencias;
- comportamiento declarado;
- diferencias entre segmentos;
- cambios entre periodos.

Sin embargo, una encuesta normalmente representa una observación de la población en un momento determinado.

El proyecto busca complementar esta capacidad con un entorno donde sea posible:

1. representar una población sintética;
2. definir un escenario;
3. ejecutar una simulación;
4. observar diferentes trayectorias;
5. repetir el experimento;
6. analizar la incertidumbre;
7. comparar posteriormente contra datos reales.

---

# 4. OBJETIVO GENERAL

Desarrollar un prototipo de simulación basada en agentes que represente estadísticamente la población de Bogotá mediante una población sintética construida a partir de datos reales y permita explorar la evolución de determinadas variables de opinión pública ante diferentes escenarios hipotéticos.

---

# 5. PREGUNTA DE INVESTIGACIÓN

Pregunta actualmente propuesta:

> **¿Es posible construir una población sintética de Bogotá, calibrada mediante datos de encuestas y variables sociodemográficas, capaz de reproducir dinámicas observadas de opinión pública y permitir la exploración de escenarios hipotéticos mediante simulación basada en agentes?**

### Estado

**Respondida parcialmente, y en parte por la negativa.**

La primera mitad —construir una población sintética calibrada— está resuelta afirmativamente y verificada (secciones 35 y 38, Fase 3). La segunda mitad —reproducir dinámicas observadas— tiene ahora una respuesta empírica, y es que **no**, al menos para confianza institucional con los datos públicos disponibles: ver el Experimento 3 (`claude/EXPERIMENT_3_RESULTS.md`) y la sección 25.

Eso no anula la pregunta; la vuelve más precisa. La versión que el proyecto puede efectivamente responder es la tercera parte: **explorar escenarios hipotéticos bajo supuestos explícitos**, que no requiere que el modelo reproduzca la historia por sí solo.

---

# 6. HIPÓTESIS DE TRABAJO

Hipótesis inicial:

> Una población sintética construida a partir de datos demográficos y de opinión, combinada con un modelo de interacción social calibrado con datos históricos, puede reproducir determinados patrones agregados observados de opinión pública y utilizarse para explorar escenarios hipotéticos.

Esta hipótesis debe ser sometida a validación.

No asumir que será cierta.

**Estado (Septiembre 2026):** sometida a validación, y **rechazada en su parte central**. De cinco predicciones pre-registradas del Experimento 3, el modelo acierta una (ausencia de bimodalidad) y falla cuatro, incluida la del nivel. Los "determinados patrones agregados" que sí reproduce son de forma de la distribución, no de trayectoria. Detalle en la sección 25.

---

# 7. ALCANCE ACTUAL

## 7.1 Geográfico

El proyecto estará limitado inicialmente a:

**Bogotá D.C.**

No se contempla inicialmente:

- Colombia completa;
- otras ciudades;
- otros países.

Bogotá funcionará como caso piloto.

---

## 7.2 Fenómeno

El primer fenómeno será:

**Dinámica de opinión pública.**

No se pretende inicialmente modelar toda la sociedad.

---

## 7.3 Unidad principal

La unidad fundamental será:

**Agente sintético.**

Cada agente representará una persona hipotética estadísticamente plausible.

---

# 8. QUÉ NO ES EL PROYECTO

El proyecto NO debe considerarse inicialmente como:

- una herramienta que predice el futuro de Bogotá;
- una copia digital de personas reales;
- una plataforma de vigilancia;
- una herramienta para identificar individuos;
- una simulación 3D de Bogotá;
- un videojuego;
- un chatbot;
- un sistema basado exclusivamente en LLM;
- una predicción determinista de opinión pública.

---

# 9. CONCEPTO DE AGENTE

Un agente representa una persona sintética.

Su estructura inicial podrá contener:

### Variables demográficas

- edad;
- sexo;
- localidad;
- eventualmente UPZ;
- educación;
- situación laboral;
- variables socioeconómicas disponibles.

### Variables sociales

- percepción;
- confianza;
- preferencias;
- opinión;
- exposición;
- afinidad.

### Variables dinámicas

Algunas variables podrán cambiar durante la simulación.

Ejemplo conceptual:

```text
opinión_actual
        ↓
interacciones
        ↓
exposición
        ↓
evento
        ↓
actualización
        ↓
nueva_opinión
```

La lista definitiva de variables quedó fijada en D12 para el prototipo.

---

# 10. POBLACIÓN SINTÉTICA

Se propone inicialmente una población de:

**100.000 agentes.**

### Estado

**Hipótesis de diseño.**

No es todavía una decisión técnica definitiva.

Se deberá evaluar experimentalmente si:

- 10.000;
- 50.000;
- 100.000;
- 500.000;
- 1.000.000

agentes son adecuados.

El tamaño deberá justificarse en función de:

- precisión;
- representatividad;
- rendimiento;
- memoria;
- tiempo de ejecución;
- número de simulaciones.

---

# 11. REPRESENTACIÓN TERRITORIAL

Primera granularidad:

**Localidad.**

Bogotá será representada inicialmente mediante sus localidades.

Posteriormente podría incorporarse:

**UPZ.**

La estructura prevista es:

```text
Bogotá
│
├── Localidad
│   ├── Agentes
│
├── Localidad
│   ├── Agentes
│
└── ...
```

Posteriormente:

```text
Bogotá
 ↓
Localidad
 ↓
UPZ
 ↓
Agentes
```

**Nota de la v0.7 — importante.** La localidad sigue siendo la unidad territorial de la **población sintética** (y ahí es indispensable: es contra el marginal por localidad que se controla el sesgo de muestreo, D14). Pero **dejó de ser una unidad plausible de la dinámica de opinión**. Medido sobre 42 ítems de opinión en dos estudios del CNC con las 20 localidades, la localidad explica ~1 % de la varianza y más de la mitad de eso es error muestral. Ver D15 y `claude/ANALISIS_HOMOFILIA.md` §8. Bajar a UPZ no ayudaría: el problema no es de resolución.

---

# 12. FUENTES DE DATOS

Se han identificado tres grandes grupos.

## 12.1 CNC

Fuente potencialmente principal para:

- opinión;
- percepción;
- preferencias;
- confianza;
- comportamiento declarado;
- variables sociodemográficas;
- segmentación.

### Estado

**Recibida (Septiembre 2026) — cierra A02.**

El CNC entregó cuatro encuestas con microdato: Salud Mental Bogotá 2023 (n = 15.151), Sustancias Psicoactivas Bogotá 2022 (n = 10.912), Apropiación Digital Colombia 2024 (n = 3.614) y SABE Colombia 2015 (n = 23.877).

**Ninguna mide confianza institucional y no hay panel** — son cuatro cortes transversales de temas distintos, sin una pregunta repetida entre olas. No reemplazan al donante de opinión (D11) ni a la ECP como serie de validación.

Lo que sí aportaron: las dos de Bogotá tienen las 20 localidades con diseño muestral complejo documentado, lo que permitió medir por primera vez cuánta opinión explica el territorio (respuesta: casi nada — D15), y una librería de estimación con diseño (`svy_prop`) que el proyecto debería adoptar.

**Restricción de uso — vigente y estricta:** las copias entregadas son idénticas a las del cliente e incluyen nombres, direcciones y coordenadas GPS. No salen del equipo de Daniel ni se suben a ningún servicio, y desde el 16/09/2026 **tampoco viven dentro del repositorio**. Lo único que circula son agregados con supresión de celdas pequeñas. Ver `claude/DATA_INVENTORY.md` §12.4.

---

## 12.2 DANE

Potencial fuente para:

- población;
- edad;
- sexo;
- hogares;
- vivienda;
- proyecciones;
- estructura demográfica.

### Estado

**Confirmada y en uso.** Multipropósito 2021 (microdato completo), proyecciones de población por localidad, y la Encuesta de Cultura Política (ECP) 2017/2019/2021/2023 — esta última es la serie temporal contra la que se validó el modelo, y la fuente de la medición empírica de la red (Capital Social). Ver `claude/DATA_INVENTORY.md` §10.

---

## 12.3 Datos Abiertos Bogotá / SDP

Potenciales fuentes para:

- población;
- localidades;
- UPZ;
- hogares;
- vivienda;
- territorio;
- indicadores sociales;
- movilidad;
- infraestructura.

### Estado

**Confirmada y en uso.** Encuesta de Percepción de Confianza Institucional (Veeduría Distrital) como donante de opinión; proyecciones de población localidad/UPL 2005-2035 (revisión 2025) como marginal territorial vigente.

---

## 12.4 Bogotá Cómo Vamos — Encuesta de Percepción Ciudadana *(nueva, 17/09/2026)*

**Recibida.** Bogotá Cómo Vamos entregó el empaquetado completo de la EPC: **diez olas de microdato** (2014-2019 y 2022-2025; no hubo levantamiento en 2020 ni 2021), formularios, tablas de salida y un diccionario maestro, la "EPC Suprema", que mapea cada variable al nombre que tuvo en cada año.

**Lo que NO aporta.** La batería de *confianza* institucional existe solo en **2024 y 2025**, y con escalas distintas entre sí. La indicación del correo —"son preguntas anuales"— no se sostiene contra el diccionario ni contra los datos. La validación cruzada de 0,09 puntos contra la ECP sigue siendo de **una sola ola**.

**Lo que sí aporta, y es más de lo esperado.** Dos ítems de evaluación institucional en escala 1-5, con la dirección enunciada en la propia pregunta, y **nueve olas cada uno**:

| Ítem | Olas | Rango de la media |
|---|---|---|
| `GG3` — gestión del alcalde/sa | 9 | 2,105 – 3,180 |
| `CC5` — gestión del Concejo | 9 | 2,234 – 2,670 |

Y como los dos los contesta **la misma persona en el mismo cuestionario**, existe la **diferencia individual** \(d_i = GG3_i - CC5_i\) en escala −4 a +4, que elimina no solo un efecto aditivo de periodo sino el estilo de respuesta individual.

**Tres advertencias que no se pueden perder:**

1. **Los ítems de imagen (`GP1_*`, `GG1`) tienen los códigos 1 y 2 invertidos entre 2014-2023 y 2024**, contra lo que dicen el formulario y el diccionario. Verificado contra la tabla de salida que la propia BCV publicó para 2023, y confirmado por el cambio de signo de la correlación con `GG3`. Quien arme la serie de imagen siguiendo el diccionario publica un salto de 45 puntos que no ocurrió. `src/population/epc_bcv.py` **bloquea** esos ítems con una excepción explícita (DI-B2).
2. **`CC5` no es un control independiente**: correlaciona +0,62 en cambios con `GG3`, y en 2017→2019 los dos suben exactamente lo mismo (+0,439 y +0,436) mientras la ECP bajaba. Hay un componente común que puede ser clima de opinión o efecto de campo.
3. **La cobertura cae en escalón de ~95 % a ~81 %** entre 2019 y 2022, sin explicación identificada; tres de las ocho transiciones de `GG3` no son robustas a la no respuesta.

**Factores de expansión: los diez años los traen y ninguno es constante.** El `FACTOR1 ≡ 1,0` del empaquetado web de 2025 era un defecto de ese empaquetado, no de la encuesta.

**Constructo, y esto importa:** la serie larga es de **gestión**, no de **confianza**. Es otro constructo sobre la misma escala y sobre instituciones que se solapan. Ver A20.

Detalle en `claude/ANALISIS_EPC_BCV.md` y `claude/ANALISIS_NORESPUESTA_EPC.md`. Cargador en `src/population/epc_bcv.py` con 17 pruebas.

---

# 13. DATOS DE MOVILIDAD

Se ha identificado la Encuesta de Movilidad de Bogotá como posible fuente futura.

Podría utilizarse posteriormente para representar:

- desplazamientos;
- origen/destino;
- actividades;
- patrones de movilidad;
- relación entre características socioeconómicas y viajes.

### Estado

**Fuera del MVP inicial.**

Podrá incorporarse posteriormente.

---

# 14. MODELO DE DINÁMICA DE OPINIÓN

La formulación conceptual del proyecto es:

```text
Nueva opinión =
    opinión actual
    + influencia social
    + exposición a eventos
    + características individuales
    + contexto
    + variabilidad
```

**Lo que el Experimento 3 dice sobre esa suma.** El prototipo implementó los dos primeros términos (opinión actual + influencia social, vía Friedkin-Johnsen sobre una red). Contra cuatro olas reales de la ECP, ese par **no mueve el nivel agregado**: el movimiento máximo simulado de la media fue 0,029 puntos contra 0,258 observados, casi un orden de magnitud menos, y el error de nivel es idéntico se corra o se congele el modelo. En cambio, **un solo escalar por año** —un término exógeno común a todos los agentes, sin mecanismo ni red— reduce el error de nivel el doble que todo el ABM.

Es decir: el término que falta (`exposición a eventos` / `contexto`) no es un refinamiento, es el que carga casi todo el trabajo. Esto es evidencia para la sección 22 (calibración) y para cualquier diseño futuro de escenarios: el mecanismo de escenario debe ser un shock exógeno explícito, no una consecuencia emergente de la influencia social.

---

# 15. MODELOS A INVESTIGAR

Antes de seleccionar el modelo se deberán estudiar al menos:

- DeGroot;
- Friedkin-Johnsen;
- Hegselmann-Krause;
- Bounded Confidence;
- modelos de influencia social;
- modelos de homofilia;
- modelos de difusión de opinión;
- otros modelos relevantes encontrados en literatura científica.

La selección debe considerar:

- interpretabilidad;
- evidencia científica;
- datos disponibles;
- complejidad;
- calibrabilidad;
- aplicabilidad al contexto colombiano;
- capacidad de representar heterogeneidad.

**Estado (Septiembre 2026):** DeGroot y Friedkin-Johnsen están implementados y evaluados contra datos reales (sección 25). **Hegselmann-Krause / Deffuant (confianza limitada) no están implementados y son ahora la línea con más respaldo empírico**, porque la única homofilia fuerte medida en Bogotá es la de opinión (39,5 % del círculo cercano comparte opiniones políticas) y no la demográfica ni la territorial. Ver A18.

---

# 16. INTERACCIÓN ENTRE AGENTES

No se utilizará una interacción completamente conectada.

Se investigó una red de interacción basada en:

- proximidad territorial;
- características demográficas;
- similitud;
- afinidad;
- homofilia.

### Estado

**Implementada y medida — ver D15.** Los tres generadores (aleatoria, homofílica demográfica, territorial) existen como variantes intercambiables. Lo nuevo de la v0.7 es que el grado y la composición de la red **dejaron de ser supuestos**: la ECP los mide (grado medio 5,35, mediana 4, 26 % sin red; composición del círculo en 11 ejes). Ver `NETWORK SPECIFICATION.md` §2.1 y §4.1.

---

# 17. ESCENARIOS

Una función fundamental será permitir definir escenarios hipotéticos.

Ejemplo:

> "Aumento significativo de la percepción de inseguridad."

Los escenarios podrán tener potencialmente:

- variable afectada;
- intensidad;
- duración;
- población afectada;
- territorio;
- distribución del impacto.

La estructura definitiva está pendiente de diseño.

**Nota de la v0.7:** esta sección subió de prioridad. Si la dinámica endógena no reproduce la historia (sección 25) pero un shock exógeno por periodo sí explica el grueso del movimiento (sección 14), entonces **el escenario no es una función más del sistema: es el mecanismo principal**. Conviene diseñarla sabiendo eso, en vez de tratarla como capa de presentación sobre una dinámica que se creía autosuficiente.

---

# 18. SIMULACIONES REPETIDAS

Un escenario no deberá ejecutarse solamente una vez.

Se plantea realizar:

**múltiples simulaciones por escenario.**

Inicialmente se considera:

**100–1.000 simulaciones.**

### Estado

**Hipótesis de diseño, con una medición a favor.** En el Experimento 3 la dispersión entre semillas de la misma configuración fue 0,0045 en la métrica de ajuste, contra 0,015 de rango entre nueve configuraciones distintas. Con ese nivel de ruido, unas pocas decenas de corridas bastan para separar configuraciones; el rango 100–1.000 es holgado y sigue siendo razonable.

---

# 19. INCERTIDUMBRE

Los resultados deben representar incertidumbre.

No queremos una salida determinista del tipo:

> "El 53% de Bogotá pensará X."

La salida debe ser más parecida a:

```text
Cambio central: +6.1 puntos

Intervalo de simulación:
+4.7 a +7.4 puntos
```

El lenguaje final deberá diferenciar:

- dato observado;
- supuesto;
- parámetro;
- resultado simulado;
- estimación;
- predicción.

**Advertencia metodológica añadida en la v0.7.** El proyecto viene calculando **medias ponderadas ingenuas** en todas partes (ECP, donante, diagnósticos), lo que subestima los errores estándar por un factor del orden de \(\sqrt{DEFF}\); el DEFF mediano medido en los estudios del CNC es 2,5. Un intervalo de simulación honesto no puede apoyarse en una estimación de entrada cuyo intervalo está mal. Adoptar estimación con diseño complejo (`svy_prop`, linealización de Taylor) es requisito previo, no refinamiento. Ver `claude/DATA_INVENTORY.md` §12.5.

**Resuelto el 17/09/2026 (A19).** `src/utils/diseno.py` da medias, diferencias y DEFF con linealización de Taylor. El DEFF medido **sobre la variable del proyecto** es 1,39-2,69, mediana **1,95**: los errores que se venían usando estaban subestimados por ~1,4. Toda diferencia entre olas que el proyecto reporte lleva intervalo desde ahora. La ECP no trae variables de diseño y su error se infla por un DEFF prestado, **marcado como prestado**. Ver `claude/ANALISIS_DISENO_MUESTRAL.md`.

---

# 20. VALIDACIÓN

La validación será una parte central del proyecto.

Se plantea utilizar:

**Backtesting.**

Conceptualmente:

```text
Datos históricos
       ↓
Calibración
       ↓
Modelo
       ↓
Simulación
       ↓
Periodo futuro conocido
       ↓
Comparación con datos reales
```

**Estado (Septiembre 2026): ejecutado por primera vez.** El Experimento 3 comparó el modelo contra las cuatro olas de la ECP (2017, 2019, 2021, 2023) con cinco predicciones **pre-registradas antes de correrlo** (`claude/EXPERIMENT_3_SPECIFICATION.md`, versionado antes de los resultados). Es el primer punto del proyecto en el que el modelo podía fallar públicamente, y falló. El registro de qué se predijo, qué pasó y qué se enmendó está en `claude/EXPERIMENT_3_RESULTS.md`.

---

# 21. MÉTRICAS DE VALIDACIÓN

Se investigará el uso de:

- MAE;
- RMSE;
- MAPE cuando sea estadísticamente apropiado;
- correlación;
- error por segmento;
- error territorial;
- cobertura de intervalos;
- métricas probabilísticas;
- estabilidad.

**Usadas efectivamente en el Experimento 3:** distancia de Wasserstein-1 entre distribución simulada y observada (métrica principal de ajuste), error de media y de desviación estándar por ola, coeficiente de bimodalidad de Sarle, y proporción de corridas que exhiben cada patrón cualitativo pre-registrado. La lista definitiva de A12 sigue abierta, pero W1 quedó como la métrica de referencia por comparar distribuciones completas y no solo momentos.

---

# 22. CALIBRACIÓN

El modelo tendrá parámetros potenciales como:

```text
influencia_social
peso_evento
peso_contexto
homofilia
tasa_de_actualización
ruido
```

Se deberá investigar cómo calibrar ABM mediante:

- búsqueda de parámetros;
- optimización;
- métodos bayesianos;
- Approximate Bayesian Computation;
- otras técnicas pertinentes.

No seleccionar un método de calibración sin justificarlo.

**Lo que el Experimento 3 acota antes de empezar a calibrar.** Dos de esos parámetros ya no son libres:

- **`homofilia`** — el grado está medido (\(\bar{k} \approx 5\)) y la composición de la red también (11 ejes). No hay que calibrarlos; hay que respetarlos (D15).
- **`influencia_social`** (\(\phi\) de Friedkin-Johnsen) — barrido en 0,3 / 0,5 / 0,7 / 0,9. El mejor ajuste es el valor más bajo, y su ventaja sobre congelar la opinión es marginal y viene **enteramente de una sola ola (2023)**. Calibrar \(\phi\) más finamente sobre estos datos sería ajustar ruido.

Lo que sí quedó identificado como el parámetro que importa es `peso_evento` / `peso_contexto` — el término exógeno por periodo (sección 14). Eso es lo que hay que calibrar primero, y no requiere ABM para hacerlo.

---

# 23. ANÁLISIS DE SENSIBILIDAD

Se deberá evaluar qué parámetros tienen mayor impacto en los resultados.

Objetivo:

> Determinar qué supuestos del modelo son realmente relevantes.

**Primer resultado, del Experimento 3:** la estructura de red **no** es un supuesto relevante para el ajuste a datos (rango 0,015 entre nueve configuraciones contra 0,0045 de ruido entre semillas), aunque sí lo es para el comportamiento interno del modelo (Experimento 2). Es exactamente el tipo de hallazgo que esta sección existe para producir: un supuesto sobre el que se había invertido mucho diseño resulta no mover el resultado que importa.

---

# 24. VALIDACIÓN DE LA POBLACIÓN SINTÉTICA

Antes de validar la dinámica de opinión debemos validar la población.

Se compararán distribuciones de:

- edad;
- sexo;
- localidad;
- educación;
- variables socioeconómicas;
- otras variables disponibles.

Métodos candidatos:

- Iterative Proportional Fitting;
- raking;
- entropy balancing;
- muestreo probabilístico;
- reconstrucción sintética;
- otros métodos estadísticos.

**Avance (Septiembre 2026, D14):** para el prototipo se adoptó muestreo probabilístico proporcional al factor de expansión de la encuesta. `src/population/muestreo.py` incluye `diagnostico_territorial()`, que compara la composición territorial de cualquier muestra contra el marginal real de las proyecciones DANE-SDP.

**Avance adicional (Experimento 3A):** la población sintética reproduce bien la **distribución** de confianza institucional observada (W1 = 0,048). Pero, como se documenta en `claude/ANALISIS_HOMOFILIA.md` §4, **no coloca la confianza sobre los individuos correctos** — reproduce el histograma, no el mapa de quién piensa qué. Es una distinción que esta sección no hacía y que conviene que haga: validar la población es validar marginales, no validar la asociación entre atributos y opinión.

---

# 25. BASELINES

No debemos asumir que ABM es automáticamente mejor.

El modelo deberá compararse contra modelos simples.

**Ejecutado en el Experimento 3.** Siete modelos, misma población, mismas redes, misma métrica (W1 total contra las cuatro olas de la ECP), medianas:

| Modelo | W1 total (mediana) |
|---|---|
| **Friedkin-Johnsen φ = 0,3** | **0,5310** |
| Congelado (la opinión no cambia) | 0,6265 |
| Ruido puro | 0,6287 |
| Friedkin-Johnsen φ = 0,5 | 0,6404 |
| Friedkin-Johnsen φ = 0,7 | 0,8053 |
| Friedkin-Johnsen φ = 0,9 | 0,9177 |
| DeGroot | 0,9387 |

Tres lecturas, ninguna cómoda:

1. **FJ con influencia baja gana, pero por poco y no donde se esperaría.** Los siete modelos dan exactamente el mismo W1 para 2019 (0,1600): en la ola más cercana al punto de partida, **la mejor jugada es no moverse**. Toda la ventaja de FJ viene de 2023.
2. **DeGroot es peor que el ruido, y FJ con influencia alta también.** Promediar opiniones sin anclaje las colapsa hacia el centro mucho más rápido de lo que Bogotá se movió. Esto responde A11 de forma útil: el baseline que discrimina no es DeGroot, es **congelar**.
3. **Un escalar por año le gana al ABM completo.** Descomponiendo el error de nivel: FJ solo lo reduce 16 %; un único término exógeno por año lo reduce 32 %; ambos juntos, 45 %. **Un número por año explica el doble que toda la maquinaria de agentes y redes.**

La pregunta de esta sección —"¿el ABM aporta información adicional frente a modelos más simples?"— tiene entonces respuesta parcial y honesta: **para reproducir la trayectoria agregada de confianza institucional en Bogotá 2017-2023, no de forma material.** Aporta otras cosas (distribución, heterogeneidad, capacidad de escenario), pero no eso.

## Actualización de la v0.12 — un baseline nuevo, y una corrección que cambia los números

**El Experimento 6 (16/09/2026) introdujo el baseline más duro que el proyecto ha tenido.** Con la serie de la ECP extendida a 2013, la dispersión observada deja de contraerse de forma monótona y **hace una joroba**: sube de 0,754 a 0,934 y vuelve a 0,764. Eso obligó a un baseline que acierta media **y** desviación por construcción: `traslación + u + γ`, dos escalares exógenos por periodo y ninguna red. Las cinco predicciones pre-registradas se cumplieron: **ningún mecanismo produce la joroba** (0 de 594 corridas) y ninguno le gana al baseline. Friedkin-Johnsen queda **último, peor que no hacer nada**. Ver `claude/EXPERIMENT_6_RESULTS.md`.

**Y el 17/09/2026 se descubrió que la población sintética tenía un defecto que favorecía a los mecanismos.** El desempate del hot-deck era determinista y apelmazaba la opinión en pocos valores donados (DI-M1, sección 33). Re-corridos los tres experimentos con la población corregida y las mismas mallas:

| Modelo (Exp. 4, 12 modelos comunes, 5.040 corridas) | antes | después |
|---|---|---|
| **traslación** (sin mecanismo) | 0,4262 | **0,3517** |
| **ruido** | 0,4188 | **0,3461** |
| FJ φ=0,1 | 0,2663 | 0,3063 |
| FJ φ=0,3 | 0,3435 | 0,5362 |
| FJ φ=0,9 | 0,5273 | 0,7819 |
| DeGroot | 0,5093 | 0,7245 |

**El deterioro crece monótonamente con φ**, es decir, con cuánta influencia social aplica el modelo; los dos únicos que mejoran son los que no tocan la forma de la distribución. Los modelos de influencia estaban cobrando crédito por reparar un artefacto de nuestro propio generador de población.

Consecuencia para esta sección: la mejora de FJ sobre la traslación pura baja de **37,5 % a 12,9 %**, y la contracción uniforme **sin red** iguala al mejor mecanismo (0,2954). Donde la red aportaba 2,8 %, ahora **no aporta nada medible**. El veredicto del Experimento 6 no se mueve. Detalle en `claude/REEJECUCION_DI-M1.md`.

## Actualización de la v0.13 — el Experimento 7, y el baseline que faltaba

Con la EPC de Bogotá Cómo Vamos el proyecto pasó de **cuatro transiciones a ocho**, en dos objetivos: la serie cruda de gestión del alcalde (A) y la diferencia individual \(GG3_i - CC5_i\) (B), que elimina el estilo de respuesta individual. 1.224 corridas.

**Los mecanismos le ganaron al baseline duro por 8,8 %, en los dos objetivos.** Cognición motivada primero, Friedkin-Johnsen segundo, `traslación+u+γ` tercero — y el mismo modelo ganando los dos con casi los mismos parámetros. Era el primer resultado claramente a favor del ABM en todo el proyecto.

**Y un control post-hoc lo deshizo.** El baseline es una transformación afín: mueve los cinco picos enteros de la población fuera de la grilla 1-5 y los deja ahí. Cualquier modelo que **difumine** los picos ajusta mejor contra una distribución observada que sí vive en los enteros. Se probó lo mínimo que también difumina — el mismo baseline más **ruido gaussiano, sin red, un solo parámetro**:

| | Objetivo A | Objetivo B |
|---|---|---|
| `traslación+u+γ` | 2,6590 | 2,2211 |
| Mejor mecanismo (33 modelos, 5 parámetros) | 2,4260 | 2,0247 |
| **`traslación+u+γ+ruido`, σ=0,2–0,3** | **2,3136** | **1,9183** |

**El ruido gana**, por 4,6 % y 5,3 %, y en toda la meseta σ ∈ [0,05 · 0,8]. La ventaja del 8,8 % no era influencia social: era suavizado.

**Lo que esto le agrega a esta sección es un baseline nuevo y mejor.** El conjunto mínimo pasa a ser **`traslación + u + γ + ruido`**: tres números exógenos por periodo —nivel, dispersión y ancho de difuminado— sin ninguna red. Es el listón contra el que hay que medir cualquier afirmación futura sobre el ABM, y el que el proyecto no tenía. Ver `claude/EXPERIMENT_7_RESULTS.md`.

## Actualización de la v0.15 — el baseline definitivo, y era un problema de forma funcional

Ese baseline duró unas horas. **El forzamiento que el proyecto venía usando —una transformación afín— es la forma funcional equivocada para variables que no viven en un continuo**, y casi todas las del proyecto lo son: los ítems de la EPC tienen 5 categorías, el índice de la ECP toma 154 valores fijados por el instrumento.

Con un **ladeo exponencial sobre el soporte propio de la variable** —\(q_k \propto p_k e^{\lambda_1 k + \lambda_2 k^2}\), dos parámetros para dos momentos, exactamente la misma información que usaba el afín—:

| | afín | **ladeo categórico** | piso de ruido |
|---|---|---|---|
| ECP, índice de confianza, 2013→2023 | 0,5775 · 3,15× | **0,1788 · 0,97×** | 0,1835 |
| EPC A, gestión del alcalde, 2014→2025 | 2,6590 · 6,15× | **0,6808 · 1,57×** | 0,4323 |
| EPC B, diferencia individual | 2,2211 · 4,90× | **0,6789 · 1,50×** | 0,4537 |

**En la ECP queda por debajo del piso de ruido: indistinguible de dos muestras de la misma distribución.**

**El conjunto mínimo de baselines queda entonces: `{ladeo categórico, traslación+u+γ, traslación+u, DeGroot}`**, con el ladeo como el exigente. Y el ruido desaparece: era el parche de un error de forma, no un término que faltara.

**Consecuencia para esta sección, y es la más fuerte que ha tenido:** si dos números exógenos por periodo llegan al piso de ruido muestral, **no queda residuo que un mecanismo social pueda explicar**. La pregunta "¿el ABM aporta información adicional frente a modelos más simples?" pasa de "casi nada" a **"no hay dónde aportar"**.

Ver `claude/FORZAMIENTO_CATEGORICO.md`. Los Experimentos 3 a 7 no se invalidan: todos sus modelos compartían el forzamiento afín, así que el defecto era común y las comparaciones entre ellos siguen siendo válidas.

---

# 26. ARQUITECTURA TECNOLÓGICA INICIAL

Arquitectura candidata:

```text
Datos
 ↓
Python
 ↓
Población sintética
 ↓
ABM
 ↓
PostgreSQL/PostGIS
 ↓
FastAPI
 ↓
React
 ↓
Dashboard
```

Tecnologías candidatas: Python (procesamiento, estadística y simulación), Mesa (framework ABM), PostgreSQL + PostGIS (persistencia y componente espacial), FastAPI (API), React (frontend), Leaflet / Mapbox (visualización geográfica).

Estas herramientas son propuestas y pueden cambiar.

---

# 27. UNITY / 3D

Unity NO forma parte del MVP.

La visualización 3D se considera una posibilidad futura.

Prioridad:

```text
Datos
 ↓
Modelo
 ↓
Validación
 ↓
Simulación
 ↓
Dashboard
 ↓
3D
```

No:

```text
3D
 ↓
Modelo
```

---

# 28. LLM / IA GENERATIVA

Los LLM no serán el núcleo del MVP.

Primero debe existir un modelo:

- estadístico;
- interpretable;
- reproducible;
- calibrable.

Posteriormente se puede investigar el uso de LLM para:

- decisiones de agentes;
- interpretación de eventos;
- generación de interacciones;
- comportamiento;
- memoria;
- comunicación.

Su inclusión dependerá de evidencia experimental.

---

# 29. MVP

El MVP actualmente planteado es:

```text
Ciudad:
Bogotá

Agentes:
≈100.000

Unidad territorial:
Localidad

Fenómeno:
Dinámica de opinión

Simulaciones:
100–1.000

Motor:
ABM

Lenguaje:
Python

Visualización:
Dashboard web
```

El MVP deberá demostrar:

1. Generación de población sintética. ✅
2. Distribución territorial. ✅
3. Asignación de características. ✅
4. Estado de opinión. ✅
5. Interacción. ✅
6. Escenario. ⬜ pendiente — y ahora es la pieza central (sección 17)
7. Simulación repetida. ✅
8. Agregación. ✅
9. Visualización. ⬜
10. Comparación contra datos reales. ✅ Experimento 3

---

# 30. PROTOTIPO INICIAL

No comenzar directamente con 100.000 agentes.

El primer experimento deberá ser pequeño.

Propuesta:

```text
1.000 agentes
↓
1–2 variables
↓
modelo simple
↓
interacción
↓
100 iteraciones
```

Después:

```text
1.000
 ↓
10.000
 ↓
100.000
```

Cada incremento debe evaluarse.

**Estado:** el prototipo de 1.000 está construido, corrido y validado contra datos reales. Escalar a 10.000 resolvería de paso dos artefactos conocidos de muestra chica (Antonio Nariño y Sumapaz en el diagnóstico territorial).

---

# 31. DASHBOARD

> **Actualización del 18/09/2026.** Esta sección describía un dashboard futuro.
> El primer pedazo ya existe: ver sección 51 y `VISUALIZATION_SPECIFICATION.md`.
> La advertencia de diseño que está más abajo en esta misma sección dejó de ser
> una precaución y pasó a ser una medición: **con la población sintética de
> 1.000 agentes, el 100 % de la dispersión de opinión entre localidades es ruido
> muestral** (desviación observada 0,156; esperada solo por ruido 0,183; residuo
> real 0,00). La página construida trae las dos escalas de color y deja producir
> el gráfico engañoso a propósito, con el texto que explica qué acaba de pasar.

El dashboard deberá permitir potencialmente:

### Escenario
Seleccionar o crear escenario.

### Parámetros
Modificar parámetros permitidos.

### Simulación
Ejecutar múltiples runs.

### Resultados
Mostrar evolución temporal, distribución, promedio, mediana, intervalos, percentiles.

### Territorio
Mapa de Bogotá.

### Segmentación
Comparar grupos.

### Validación
Mostrar:

**observado vs simulado.**

**Advertencia de diseño (v0.7):** un mapa de Bogotá coloreado por opinión simulada mostrará diferencias entre localidades que, según los datos reales, **no existen o son del tamaño del ruido muestral** (sección 11, D15). Es el gráfico más vendedor del dashboard y el más engañoso. Si se incluye, debe llevar la escala real de variación entre localidades (sd ≈ 0,05–0,07 sobre escalas de 1–5) y no una escala de color estirada al rango observado.

---

# 32. PRIVACIDAD

Principio obligatorio:

> Los agentes deben ser sintéticos y no representar individuos reales identificables.

No se deben incorporar datos personales identificables.

El uso de información interna del CNC debe cumplir:

- políticas internas;
- requisitos legales;
- gobierno de datos;
- anonimización;
- minimización;
- controles de acceso.

**Caso concreto (Septiembre 2026).** Los estudios entregados por el CNC son copias idénticas a las del cliente: sustancias trae 50 columnas con nombres y direcciones, SABE trae 30 incluidas 8 de GPS. El régimen adoptado:

1. Esos archivos **no salen del equipo de Daniel** — no se adjuntan a conversaciones, no se suben a servicios, no se copian a otra máquina.
2. Lo único que circula son **agregados** producidos por `src/population/cnc_agregar.py`, con supresión de estimaciones con n < 30 y celdas con n < 25.
3. El filtro de PII del CNC es **por nombre de columna** y tiene un hueco conocido (fechas de nacimiento del listado del hogar en sustancias). `cnc_agregar.py` selecciona por lista blanca, no por exclusión.
4. **Los microdatos viven fuera del repositorio** (movidos el 16/09/2026), no simplemente ignorados por `.gitignore`. Un `.gitignore` protege contra `git push`; no protege contra un servicio de sincronización que mire la carpeta. Verificado: `data/raw/cnc/` ya no existe, y el directorio de usuario del equipo no tiene carpeta de OneDrive, Drive ni Dropbox — Escritorio y Documentos no están redirigidos a la nube.
5. **La ruta de esa carpeta no está escrita en el código** (DI-N7 de `cnc_agregar.py`). Se pasa con `--cnc <ruta>` o con la variable de entorno `BSS_CNC_DIR`, y el script avisa en pantalla si la ruta que resuelve queda dentro del repositorio. Volver a meterla ahí requiere ignorar un aviso explícito, no simplemente olvidarse.

Detalle en `claude/DATA_INVENTORY.md` §12.4.

---

# 33. SESGOS

El proyecto debe estudiar explícitamente:

- sesgo de muestra;
- sesgo de cobertura;
- sesgo de respuesta;
- sesgo territorial;
- sesgo socioeconómico;
- sesgo introducido por el modelo;
- sesgo de parametrización.

No asumir que una población sintética es automáticamente representativa.

**Caso concreto documentado (D14):** la primera versión de la población sintética heredó entero el sobre-muestreo de localidades pequeñas del diseño de Multipropósito. Santa Fe tenía 45 agentes donde le correspondían 13; Bosa, 38 donde le correspondían 87. El sesgo no era visible en el archivo de agentes ni en su metadata: solo apareció al compararlo contra un marginal externo.

**Segundo caso, de sesgo de respuesta — investigado y descartado (16/09/2026):** en la ECP la proporción de personas sin índice válido es estable en 2017–2021 (1,8 % / 2,4 % / 1,8 %) y **salta a 4,8 % en 2023**, justo la ola donde la confianza rebota y la dispersión se contrae. Era la amenaza más concreta a los Experimentos 3 y 4.

**No es un artefacto.** Cuatro pruebas, todas en la misma dirección: relajar el mínimo de ítems *aumenta* el rebote; el peor caso imaginable (quien no contestó nada, en el mínimo de la escala) conserva el 88 % del rebote y el 81 % de la contracción; restringir a los **casos completos, 13 de 13 ítems** —que elimina de raíz la no-respuesta por ítem— reproduce ambos casi exactamente (+0,186 y −13,8 % contra +0,185 y −14,8 %); y reponderar 2023 a la composición de 2021 *profundiza* el fenómeno en vez de disolverlo. Además, quienes contestan pocos ítems son **más confiados** que el promedio, así que la regla de exclusión sesga la media hacia abajo: trabaja en contra del rebote.

Reproducible con `python src/population/norespuesta.py`. Detalle en `claude/ANALISIS_NORESPUESTA_2023.md`.

**Lo que sigue sin poder medirse:** la no-respuesta de **unidad** —quien nunca abrió la puerta— es invisible en el microdato, y el tamaño de muestra sí cayó (5.137 → 4.451). Exigiría las tasas de respuesta y el marco muestral de DANE.

**Hallazgo lateral que conviene no perder:** el perfil de quien no contesta se invirtió, de gente mayor (57,1 años en 2017) a gente joven y de estrato bajo (40,1 años y estrato 2,06 en 2023). No mueve los agregados, pero sí importa para cualquier desagregación por edad o estrato de la ECP 2023.

**Cuarto caso, de sesgo introducido por el método — encontrado y corregido (17/09/2026, DI-M1):** `hot_deck_match` pedía un solo vecino y se quedaba con el primero. Con empates —masivos cuando las variables de distancia son discretas— **todos los receptores de una celda recibían el mismo valor**, y la opinión sintética dejaba de ser una muestra de la distribución del donante para ser una docena de individuos replicada por el tamaño de cada celda.

Lo detectó el control T6 **pre-registrado** del Experimento 7, antes de correr nada: la población base construida con la EPC 2014 daba \(W_1 = 0{,}2172\) contra un piso de ruido de 0,0580 — 3,75 veces el piso, con un umbral declarado de 2. Era el defecto que A05 tenía anotado desde hacía tres iteraciones como "el desempate determinista aplana la variable de opinión".

**El arreglo:** se sortea entre los empatados a la distancia mínima, con probabilidad proporcional al factor de expansión del donante. Lo segundo importa tanto como lo primero: el objetivo contra el que se compara es la distribución *ponderada*, así que sortear uniforme habría metido un sesgo propio.

| Población base | \(W_1\) antes | \(W_1\) después | piso |
|---|---|---|---|
| ECP 2013 | 0,0442 · 1,05× | **0,0205 · 0,49×** | 0,0422 |
| ECP 2017 | 0,0497 · 1,08× | **0,0303 · 0,65×** | 0,0462 |
| EPC 2014 | 0,2172 · 3,75× | **0,0528 · 0,91×** | 0,0580 |

Las tres quedan **por debajo del piso de ruido**. El efecto sobre los resultados está en la sección 25 y en `claude/REEJECUCION_DI-M1.md`. Regresor en `tests/test_population_matching.py`.

**Lo que este caso enseña, y conviene no olvidarlo:** el defecto llevaba meses en el código, estaba **anotado** en A05, y no lo encontró una revisión sino un **control pre-registrado con umbral numérico**. Sin ese umbral, la población de la EPC habría entrado al Experimento 7 y el resultado habría sido ininterpretable.

**Tercer caso, de sesgo introducido por el método (A15):** el donante de confianza no trae estrato, así que el hot-deck lo excluye de la distancia y `opinion_t0` queda **estadísticamente independiente de `estrato` por construcción**. Cualquier hallazgo del simulador que relacione estrato con opinión sería un artefacto.

---

# 34. CAUSALIDAD

No interpretar automáticamente relaciones estadísticas como relaciones causales.

Si un mecanismo del simulador representa causalidad debe existir:

- hipótesis;
- mecanismo explícito;
- evidencia;
- literatura o justificación.

**Aplicación concreta (v0.7).** La homofilia medida en la ECP —39,5 % del círculo cercano comparte opiniones políticas— es una correlación de corte transversal. **No dice quién influyó a quién.** Puede ser que el círculo moldee la opinión (lo que el modelo supone) o que la gente elija su círculo por opinión (selección), y lo más probable es que sean las dos. Un ABM que solo implemente influencia está tomando partido por una de las dos sin evidencia. Queda anotado como el supuesto más fuerte de `NETWORK SPECIFICATION.md` (§8).

---

# 35. REPRODUCIBILIDAD

Cada experimento debe registrar:

```text
experiment_id
fecha
versión_modelo
dataset
número_agentes
número_simulaciones
parámetros
seed
escenario
resultados
métricas
observaciones
```

Las simulaciones deben poder reproducirse.

**Estado (Septiembre 2026):** el pipeline de población es reproducible de punta a punta. Con los archivos crudos en `data/raw/` más los scripts versionados, `loader → muestreo → hot-deck → build_agents` regenera la población sintética de forma determinista dada la semilla. Verificado: la reconstrucción de la corrida de septiembre reprodujo la población anterior idéntica agente por agente. El marginal territorial se regenera desde el anexo oficial byte por byte.

**Práctica nueva y que conviene mantener:** el Experimento 3 se **pre-registró**. `claude/EXPERIMENT_3_SPECIFICATION.md` fija las cinco predicciones y sus umbrales antes de correr nada; `claude/EXPERIMENT_3_RESULTS.md` reporta contra esa especificación, incluidas las predicciones que el autor había marcado como probables y fallaron, y una enmienda de umbral documentada como tal. Sin ese registro previo, cuatro fracasos se habrían podido narrar como tres aciertos.

---

# 36. VERSIONAMIENTO

El modelo deberá versionarse.

```text
v0.1
v0.2
v0.3
...
```

Cada versión debe documentar:

- cambios;
- parámetros;
- datos;
- metodología;
- resultados.

---

# 37. CRITERIOS DE ÉXITO

El MVP será considerado exitoso si:

### Población
La población sintética reproduce razonablemente las distribuciones objetivo. **✅ Cumplido** (TVD territorial 0,032; W1 de la distribución de opinión 0,048).

### Modelo
La dinámica producida es coherente con los supuestos. **✅ Cumplido** — el modelo hace lo que Friedkin-Johnsen dice que hace.

### Calibración
Los parámetros pueden calibrarse utilizando datos reales. **⚠️ Parcial** — se pueden calibrar, pero la calibración no mejora materialmente el ajuste (sección 22).

### Validación
El modelo reproduce algunos patrones observados mejor que determinados baselines. **❌ No cumplido, y ya se puede decir sin ambigüedad.** Este criterio estaba redactado con holgura suficiente ("algunos patrones", "determinados baselines") como para declararse cumplido, y en la v0.7 se dejó en "marginal" por eso. Con siete experimentos pre-registrados, dos constructos, ocho transiciones y el baseline correcto —`traslación+u+γ+ruido`, sin red—, la respuesta es que **no**: ningún modelo con mecanismo social supera a tres escalares exógenos por periodo. Declararlo cumplido por la holgura de la redacción sería exactamente lo que la sección 45 prohíbe.

### Reproducibilidad
Los resultados pueden reproducirse. **✅ Cumplido.**

### Incertidumbre
Los resultados pueden expresarse como distribuciones y no solamente como valores únicos. **✅ Cumplido en la salida**, ⚠️ pendiente en la entrada (sección 19: faltan errores estándar con diseño).

### Utilidad
Los escenarios generan información potencialmente útil para investigación social. **⚠️ Construido, sin evaluar con usuarios.** El motor existe y produce informes (Fase 8), y el escenario de polarización muestra algo que un promedio esconde: la distribución se parte sin que el nivel se mueva. Pero **que sea útil lo dicen los investigadores del CNC usándolo, no este documento**. Es lo que queda, y no es trabajo de código.

---

# 38. ROADMAP ACTUAL

**Nota de unificación (Septiembre 2026, D13):** esta sección usa la numeración de 11 fases (0-10) acordada en D13, que reemplaza tanto la numeración de 8 fases que tenía originalmente este documento como la de 11 fases originales de PROMPT_MAESTRO.md (cuyo orden interno se corrigió — ver D13 en sección 39). PROMPT_MAESTRO.md no se reescribe retroactivamente porque es la instrucción original del proyecto, no un documento vivo; este documento es la fuente de verdad del roadmap activo.

## FASE 0 — Investigación

Estado: **Completada.** Documento: RESEARCH.md.

---

## FASE 1 — Auditoría de datos

Estado: **Completada.** A02 cerrada en septiembre de 2026 con la recepción de los estudios del CNC (sección 12.1 y sección 40).

Documento: DATA_SPECIFICATION.md, claude/DATA_INVENTORY.md.

---

## FASE 2 — Especificación de datos

Estado: **Completada.** Fuentes confirmadas y **efectivamente descargadas**: Multipropósito 2021 completo y extracto, Encuesta de Confianza Institucional, proyecciones DANE-SDP (anexo 2021 + revisión 2025), ECP DANE 2017/2019/2021/2023 con sus módulos de Participación y Capital Social. El inventario operativo se lleva en `claude/DATA_INVENTORY.md`.

---

## FASE 3 — Diseño de población sintética

Estado: **Completada y auditada.** Variables definidas (D12); hot-deck nearest-neighbour implementado (`src/population/`), corrido con Multipropósito 2021 real (168.200 personas) y el donante real (4.458 personas); muestreo resuelto (D14); validación de rangos/tipos y diagnóstico territorial contra marginal externo.

Abierto: A05 (el método de fusión sigue sin confirmarse como D0X), A15 (vacío de estrato en el donante), A17 (códigos 8/9).

Documento: POPULATION_SPECIFICATION.md.

---

## FASE 4 — Diseño de modelo de opinión y red

Estado: **Completada en su primera iteración, y reabierta por evidencia.** Modelo y generadores especificados e implementados. La red dejó de tener parámetros supuestos: grado y composición están medidos (D15). El modelo de opinión tiene ahora un resultado de validación que apunta fuera de la familia elegida (A18).

Documentos: MODEL_SPECIFICATION.md, NETWORK SPECIFICATION.md, claude/ANALISIS_HOMOFILIA.md.

---

## FASE 5 — Primer ABM (arquitectura + implementación)

Estado: **Completada, con una desviación deliberada de ARCHITECTURE.md.** Implementados y probados: `src/population/`, `src/network/`, `src/opinion/` (DeGroot y Friedkin-Johnsen), `src/experiments/` (runner y métricas) y `config/`. Experimentos 1, 2 y 3 ejecutados.

**`src/model/` no existe, y es a propósito (DI-E1, docstring de `src/experiments/runner.py`).** ARCHITECTURE.md preveía `BogotaAgent` y `BogotaSocialModel` sobre Mesa. Al quedar los modelos de opinión vectorizados, Mesa habría añadido mil objetos Python y un par de órdenes de magnitud de lentitud para envolver una multiplicación de matrices, y la preocupación original por el scheduler (sesgo de orden en la actualización simultánea) quedó resuelta por construcción. Mesa entra cuando haga falta de verdad —heterogeneidad de comportamiento por agente, scheduling no trivial, eventos de la Fase 8—, no antes. Principio 5.

*Corrección:* la v0.7 de este documento afirmaba que `src/model/` estaba "implementado y probado". No lo está ni tiene por qué estarlo. Queda anotado en vez de corregido en silencio, por la misma razón que la nota de la v0.6 de `claude/DATA_INVENTORY.md`.

---

## FASE 6 — Calibración

Estado: **Reorientada antes de empezar.** Ver sección 22: los parámetros de red ya no son libres (están medidos) y \(\phi\) no discrimina. Lo que hay que calibrar es el término exógeno por periodo. Pendiente elegir método (A10).

---

## FASE 7 — Validación

Estado: **Primera vuelta completada** — Experimento 3, con pre-registro. Pendiente: validación por segmento, cerrar A12, y analizar el salto de no-respuesta de 2023 (sección 33) antes de dar por buena la única ola favorable.

---

## FASE 8 — Escenarios

Estado: **Construida (17/09/2026).** `src/scenarios/` con 13 pruebas; especificación en `claude/SCENARIO_SPECIFICATION.md`.

Un escenario se declara en YAML con **dos números por periodo** —nivel y dispersión, cada uno con su incertidumbre, que es obligatoria—, se ejecuta con N corridas que sortean población, supuestos y reparto por separado, y sale como un informe HTML autocontenido. El forzamiento es el **ladeo categórico**; la red no interviene.

Tres cosas que el motor hace y no son opcionales: **el escenario nulo se corre siempre** (la pregunta útil es cuánto más que no hacer nada, no cuánto da), **la incertidumbre se descompone** en la parte que viene del supuesto y la que viene del tamaño de la población —porque deciden cosas distintas—, y **los escenarios imposibles se rechazan al cargar**, incluidos los bordes de la incertidumbre declarada, con el rango alcanzable en el mensaje.

Dos escenarios de ejemplo en `config/escenarios/`. El de polarización es el argumento de por qué existe el simulador: el nivel no se mueve (diferencia de 0,1 veces el error) y sin embargo las categorías extremas pasan de 19 % a 32 % y de 12 % a 25 % mientras las centrales se vacían. Un informe que reportara la media no vería nada.

Lo que **no** se construyó, y es deliberado: base de datos, API y frontend separados. Hoy nada en el modelo los necesita — un escenario es un YAML, una corrida son segundos, la salida es un archivo. Principio 5, la misma razón por la que no hay capa Mesa. Ver §6 de la especificación.

---

## FASE 9 — Escalamiento

Pendiente: benchmark de tamaño de población (A08), de 1.000 a 100.000+ agentes; aproximación k-d tree/blocking para el generador homofílico; representación sparse.

**Nota del 18/09/2026.** El escalamiento deja de ser una optimización abstracta y pasa a tener un motivo visible: con 1.000 agentes ninguna diferencia entre localidades sobrevive al ruido, y el mapa lo muestra. A 100.000 agentes el error estándar por localidad cae por un factor de 10. Esa es ahora la razón para hacer A08, y es mejor razón que "correr más rápido".

---

## FASE 10 — Dashboard / plataforma

**Reordenada y empezada (18/09/2026).** Deja de ser la última fase y pasa a ser el frente principal de trabajo, por decisión del CNC. Hito 1 construido y publicado: mapa interactivo de las 20 localidades con los 1.000 agentes sintéticos, composición demográfica e intervalos de ruido. Hitos 2 a 5 especificados.

Sigue sin construirse —y sigue siendo deliberado— la pila de `ARCHITECTURE.md` (PostgreSQL + PostGIS + FastAPI + frontend separado): la página es un solo archivo autocontenido, DI-V6. Principio 5.

Documento: `VISUALIZATION_SPECIFICATION.md`. Ver también la sección 51 y la advertencia de la sección 31.

---

## Extensiones futuras (fuera de la numeración de fases)

Posibles, condicionadas a evidencia experimental (D10): movilidad, comportamiento, eventos sociales, LLM, 3D, otras ciudades.

---

# 39. DECISIONES CONFIRMADAS

### D01
El caso piloto será exclusivamente **Bogotá D.C.**

### D02
El primer fenómeno será **dinámica de opinión pública**.

### D03
La arquitectura conceptual utilizará **población sintética**.

### D04
Se utilizará como enfoque principal **Agent-Based Modeling**.

### D05
Los agentes serán sintéticos y no representarán personas reales.

### D06
El proyecto debe utilizar datos reales para fundamentar la población.

### D07
La validación mediante datos reales será un componente fundamental.

### D08
El proyecto debe representar incertidumbre.

### D09
Unity/3D no será prioridad del MVP.

### D10
LLM no será el núcleo del MVP.

### D11 — Variable de opinión del primer experimento (resuelve A13)

**Fecha:** Septiembre de 2026
**Decisión:** La variable de opinión del primer experimento será **confianza institucional**.
**Justificación:** De los candidatos evaluados en Bogotá Cómo Vamos contra los seis criterios de RESEARCH.md (sección 55), dos quedaron como candidatos fuertes: percepción de seguridad y confianza institucional. El desempate lo dio la alineación con MODEL_SPECIFICATION.md: el único modelo con evidencia publicada de calibración exitosa contra datos reales (Gestefeld & Lorenz, 2023) fue calibrado específicamente contra distribuciones de confianza institucional.
**Alternativas consideradas:** Percepción de seguridad (ventaja: segunda fuente independiente vía ECSC de DANE, pero sin el mismo respaldo de calibración publicada). Satisfacción con la ciudad, optimismo/orgullo, evaluación de gestión del alcalde y percepción sobre proyectos específicos fueron descartados por al menos un criterio débil.
**Impacto:** Cierra el campo `opinion_t0` de D12. Determina qué donante alimenta el hot-deck.
**Actualización (Septiembre 2026):** el "pendiente dentro de esta decisión" —índice compuesto vs. institución específica— queda resuelto a favor del **índice compuesto**, y no por conveniencia sino por medición: en la ECP, quitando el nivel propio de cada ítem, el **81 % de la variación entre años cae en un único componente** con las 13 cargas del mismo signo. Los ítems se mueven como uno solo; modelar 13 series separadas no aportaría información. **Nota factual:** son **8** actores en el donante de la Veeduría, no 7 — verificado; DATA_SPECIFICATION.md dice "7" pero enumera 8, y queda por corregir ahí.
**Estado:** APPROVED (confirmada en conversación).

### D12 — Estructura de variables del agente para el prototipo de 1.000 (resuelve A01)

**Fecha:** Septiembre de 2026
**Decisión:** El agente del prototipo tendrá exactamente estos campos:

```text
agent_id
edad
sexo
localidad
estrato
nivel_educativo
opinion_t0        ← confianza institucional (ver D11)
```

**Justificación:** Cada variable debe cumplir tres condiciones: fuente confirmada, rol funcional trazable (variable puente del matching, insumo de homofilia/red, o la variable dinámica), y no duplicar información.
**Alternativas descartadas para esta iteración:** situación laboral; UPZ; confianza o percepción de seguridad como atributos adicionales; participación asociativa del capítulo J de Multipropósito.
**Impacto:** Fija la distancia \(d(x_i,x_j)\) del generador homofílico y el conjunto de variables puente del hot-deck.
**Advertencia añadida en la v0.7 — esta decisión envejeció mal, y conviene decirlo.** Las tres variables sobre las que se construyó la distancia homofílica (edad, estrato, nivel educativo) explican en conjunto **~3 %** de la varianza de la confianza institucional en la ECP, y ningún otro atributo observable estable lo mejora de forma reproducible entre olas. D12 no está mal como estructura mínima del agente; lo que está mal es la expectativa de que esas variables pudieran estructurar la opinión. Ver D15 y `claude/ANALISIS_HOMOFILIA.md` §2.
**Estado:** APPROVED (confirmada en conversación).

### D13 — Unificación de la numeración de fases del roadmap

**Fecha:** Septiembre de 2026
**Decisión:** Adoptar una numeración única de 11 fases (0-10) como roadmap activo, reemplazando la de 8 fases de este documento y la de PROMPT_MAESTRO.md sección 19 (que se mantiene sin editar). La nueva numeración corrige el orden lógico: modelo de opinión y red antes que la arquitectura del ABM, que es como ocurrió en la práctica.
**Justificación:** Tres documentos vivos habían adoptado sin coordinación la numeración de PROMPT_MAESTRO.md mientras este documento usaba la suya, generando referencias cruzadas inconsistentes. Además, la numeración de 8 fases no reconocía **Validación** como fase propia, pese a que D07/D08 la establecen como componente central.
**Impacto:** Reescribe la sección 38. Las referencias vigentes de fase viven únicamente aquí.
**Estado:** APPROVED (confirmada en conversación).

### D14 — Estrategia de muestreo del prototipo (resuelve A16)

**Fecha:** 15 de septiembre de 2026
**Decisión:** Los N agentes se seleccionan del receptor completo con **probabilidad proporcional al factor de expansión** (`FEX_C` de Multipropósito 2021), mediante **PPS sistemático**. Caídas documentadas: estratificación por localidad contra el marginal DANE-SDP si no hay ponderador; muestreo aleatorio simple si tampoco hay marginal, advirtiendo que la muestra no es representativa. Implementado en `src/population/muestreo.py`.

**Justificación:** El muestreo aleatorio simple hereda entero el sobre-muestreo de localidades pequeñas que Multipropósito aplica a propósito. Santa Fe tenía 45 agentes donde le correspondían 13 y Bosa 38 donde le correspondían 87 — factor de 17 entre la más sobre- y la más sub-representada. No era cosmético: los \(n_l\) por localidad alimentan el despeje de \(p_{intra}\)/\(p_{inter}\) del generador territorial. Se eligió el ponderador sobre la estratificación territorial porque corrige **todas** las dimensiones a la vez.

**Decisión de implementación:** PPS sistemático y **no** `numpy.random.choice(..., replace=False, p=pesos)`, cuyas probabilidades de inclusión no son proporcionales a los pesos y sub-representan a las unidades pesadas — la diferencia crece con la dispersión de los pesos, y `FEX_C` va de 1,18 a 245,70. Verificado sobre 4.000 repeticiones en `tests/test_muestreo.py`. Las unidades con peso mayor a \(W/n\) se tratan como unidades de certeza.

**Evidencia:** corrida real (15/09/2026), receptor 168.200, N=1.000, semilla 42. Distancia territorial al marginal **0,172 → 0,041**. Sesgo por localidad de 0,44–3,54 a 0,78–1,29. Corrigió también las dimensiones no territoriales: educación media 2,75 → 2,62; estrato medio 2,83 → 2,65; edad media 46,6 → 44,9.

**Actualización (16/09/2026):** el marginal se regeneró contra la **revisión 2025** de las proyecciones DANE-SDP (Contrato Interadministrativo 500 de 2025), que reemplaza la proyección hecha en 2021. Bogotá 18+ pasa de 6.386.051 a **6.201.042** (−2,9 %); distancia L1 entre marginales 0,0371. La población v2, **sin rehacerse**, ajusta mejor contra el marginal revisado: TVD 0,041 → **0,032**. Esto resuelve el pendiente (a) de abajo en la dirección correcta: el marginal ya no es una proyección pre-COVID.

**Pendiente dentro de esta decisión:** (b) las localidades diminutas siguen sujetas a ruido de muestreo (Sumapaz tiene 0,4 agentes esperados sobre 1.000) — se atenúa al escalar N; (c) no se ha evaluado el efecto de la varianza de los pesos sobre el tamaño efectivo de muestra.

**Estado:** APPROVED (confirmada en conversación).

### D15 — Qué se hace con la red de interacción (resuelve A07)

**Fecha:** 16 de septiembre de 2026
**Decisión, en cuatro partes:**

1. **Fijar \(\bar{k} = 5\)** como grado promedio central del prototipo, con 4 y 8 como sensibilidad. Deja de ser un parámetro de diseño barrido a ciegas: está medido.
2. **Los tres generadores dejan de ser candidatos a "el correcto" y pasan a ser variantes de sensibilidad**: la aleatoria como control, la territorial como contrafáctico de segregación, la homofílica demográfica como contrafáctico de estratificación. Ninguno se elimina; ninguno se declara ganador.
3. **Reportar siempre el rango de resultados entre generadores**, no el de uno solo.
4. **Abrir la homofilia de opinión (confianza limitada) como línea propia** — es la única con respaldo empírico y la única que cambiaría el diagnóstico del Experimento 3. Ver A18.

**Justificación — tres fuentes independientes, misma conclusión:**

| Evidencia | Medición | Fuente |
|---|---|---|
| La estructura de red casi no afecta el ajuste a datos | rango 0,015 entre nueve configuraciones, contra 0,0045 de dispersión entre semillas | Experimento 3 §5 |
| La demografía no estructura la opinión | \(\eta^2 = 3\,\%\) (edad × sexo × educación × estrato, 66 celdas); ningún atributo observable estable replica entre olas | ECP 2017/2023 |
| El territorio tampoco | localidad explica 0,4–2,6 % (mediana ~1 %) de la varianza en 42 ítems; **54 % / 63 % de eso es error de muestreo**; sd real entre localidades 0,073 / 0,046 contra ~1,05 dentro | CNC, Salud Mental 2023 (n=15.151) y Sustancias 2022 (n=10.912) |

Y una medición en positivo, del módulo de Capital Social de la ECP: **el 39,5 % del círculo cercano comparte opiniones políticas, contra el 12,4 % que comparte cuadra.** La homofilia existe y es fuerte; simplemente no es demográfica ni territorial. El grado empírico es **5,35 de media, mediana 4, con 26 % de personas sin red**.

**Por qué la decisión no es "elegir el mejor generador".** La v0.2 de `NETWORK SPECIFICATION.md` dejaba A07 a lo que dijera el Experimento 2. El Experimento 2 dijo que la red importa mucho para lo que el modelo hace; el Experimento 3 dijo que no importa para si el modelo acierta. Elegir por ajuste es imposible cuando los tres ajustan casi igual. La evidencia que discrimina no salió de los experimentos sino de las mediciones, y discrimina **en contra de dos de los tres**.

**Alternativas consideradas:**
- *Elegir el generador territorial* — descartada: no tiene objetivo empírico que reproducir. El valor de \(h\) compatible con los datos está cerca de 1, que es la red aleatoria.
- *Elegir el homofílico demográfico con pesos calibrados* — descartada: no hay peso que rescate un eje que explica el 3 %.
- *Dejar A07 abierta y reportar sensibilidad sin decidir* — descartada por acumulación: llevaba tres iteraciones abierta y la evidencia ya alcanza para acotar el espacio, aunque no para coronar un ganador.
- *Eliminar el generador territorial del código* — descartada: la pregunta "¿y si Bogotá estuviera territorialmente segregada?" es exactamente el contrafáctico para el que existe el laboratorio.

**Impacto:** modifica `NETWORK SPECIFICATION.md` (v0.3, §2.1, §4.1, §5.1, §7); obliga a ajustar el barrido de `config/` de \(\bar{k} \in \{4,8,16\}\) a \(\{4,5,8\}\) y a re-verificar que el Experimento 3 no cambia; abre A18; y reencuadra D12 (ver la advertencia añadida ahí).

**Lo que esta decisión NO afirma:** no afirma que la red no importe socialmente, ni que Bogotá no tenga estructura social. Afirma que, **para confianza institucional y con los datos públicos disponibles**, la estructura de red construida sobre atributos observables no discrimina entre modelos ni mejora el ajuste. Es un resultado sobre nuestra capacidad de medir, no un hecho sobre la ciudad.

**Evidencia:** `claude/EXPERIMENT_3_RESULTS.md` §5 y §8.3; `claude/ANALISIS_HOMOFILIA.md` §2, §5.2, §8; `claude/DATA_INVENTORY.md` §10.7 y §12.3; `NETWORK SPECIFICATION.md` v0.3.

**Ejecución (16/09/2026), al confirmarse:**

- `src/experiments/experimento3.py`: `K_MEDIOS = [4, 8, 16]` → **`[4, 5, 8]`**, con el porqué en el código.
- `config/experiment_2.yaml` y `config/experiment_2_degroot.yaml`: `k_promedio: [5, 10, 15, 20]` → **`[4, 5, 8]`** en los tres generadores. El barrido pasa de 24 a **18 configuraciones**.
- Se re-corrió el Experimento 3 completo con el barrido nuevo para comprobar que el veredicto no depende del rango de \(\bar{k}\). **el veredicto no cambia: las cuatro predicciones siguen fallando.**

| | Pre-registro \(\bar{k} \in \{4,8,16\}\) | Re-corrida \(\bar{k} \in \{4,5,8\}\) | Umbral |
|---|---|---|---|
| P1 — movimiento máx. de la media | 0,0290 (6,5× *menos* que lo observado: 8,9×) | **0,0398** (6,5×) | ≥ 0,05 · **falla en las dos** |
| P2 — mejor error de sd | 0,0751 | **0,0692** | < 0,05 · **falla en las dos** |
| P3 — corridas con mínimo interior | 0 / 720 | **0 / 720** | ≥ 1 · **falla en las dos** |
| P4 — corridas con máximo interior en la cola baja | 0 / 720 | **0 / 720** | ≥ 1 · **falla en las dos** |
| FJ φ=0,3 (mejor modelo), W1 total | 0,5310 | **0,5291** | — |
| Congelado | 0,6265 | **0,6265** | — |
| Ruido | 0,6287 | **0,6288** | — |
| DeGroot | 0,9387 | **0,8490** | — |

Tres cosas sí se movieron, y conviene decirlas en vez de reportar solo "no cambió":

1. **Con redes más ralas el modelo se mueve algo más** (0,029 → 0,040) y la razón contra lo observado baja de 8,9× a 6,5×. Dirección correcta, magnitud insuficiente: sigue sin alcanzar el umbral de 0,05.
2. **DeGroot mejora y adelanta a FJ φ=0,9** (0,8490 contra 0,8651). Con menos vecinos promedia más lento y colapsa menos. La afirmación que importa no cambia: **sigue siendo peor que el ruido.**
3. **"Congelado" da exactamente el mismo número** (0,6265). Tenía que darlo —no depende de la red— y sirve de control de que la re-corrida no alteró nada más.

La corrida pre-registrada sigue siendo **la reportada** en `claude/EXPERIMENT_3_RESULTS.md`; esta es una verificación de robustez y no la reemplaza. Salidas en `data/processed/exp3_k_d15/` (1.260 corridas, 33 min).

**Estado:** **APPROVED** (confirmada en conversación, 16 de septiembre de 2026).

### D16 — Los resultados electorales que entregó el CNC quedan fuera del régimen R10

**Fecha:** 29 de septiembre de 2026
**Decisión:** Los archivos electorales que el CNC entregó el 29/09/2026 (inventario en
`DATA_INVENTORY.md` §14) **no se rigen por R10**: se pueden usar en el proyecto y su
contenido **se puede leer con un modelo de lenguaje** (Claude en Claude Code). Viven
**fuera del repositorio**, en una carpeta propia, y el código la encuentra por la
variable de entorno `BSS_ELECTORAL_DIR`, sin escribir su ruta. **No se copian al
repositorio**, ni siquiera a `data/raw/`.

**R10 no cambia para nada más.** Los estudios de `DATA_INVENTORY.md` §12 (Salud
Mental, Sustancias, Apropiación Digital, SABE) siguen exactamente igual: no se abren,
no se leen con un LLM, no salen del equipo.

**Justificación.**
- **No hay datos de personas.** Revisión del 29/09, primero de estructura sin imprimir
  valores y después de conteos agregados: ninguna cédula, dirección de ciudadano,
  teléfono, correo ni coordenada. Las columnas con nombres son de **candidatos,
  partidos y puestos de votación**; lo confirman las etiquetas de las variables de
  los `.dta` («Nombres completos del candidato o del partido…»).
- **Son agregados.** La unidad más fina es la **mesa de votación**. El más fino de los
  productos propios del CNC es el municipio.
- **Casi todo es de origen público** (Registraduría Nacional; los CSV de Senado y
  Cámara 2018 parecen descargas de datos abiertos del 30/05/2025). Lo producido por
  el CNC son consolidaciones y el índice de ideología por municipio.
- **Autorización:** Daniel confirma que el CNC autorizó su uso en el proyecto, y
  autorizó expresamente que Claude los revise directamente.

**Alternativas consideradas:**
- *Mantenerlos bajo R10 y revisarlos con un script local que muestre solo la
  estructura* — propuesta por Claude; Daniel eligió la revisión directa. Sigue siendo
  el camino para cualquier archivo que traiga datos de personas.
- *Copiarlos a `data/raw/`* — descartada: pesan 1,8 GB, y un error en `.gitignore` los
  subiría. Es la misma razón por la que los estudios del CNC salieron del repositorio
  (DI-N7).

**Límites de la decisión.**
1. Vale para **los archivos listados en §14**. Un archivo nuevo en la carpeta no entra
   solo: se revisa igual, estructura primero, antes de leer valores.
2. **Publicar** en el tablero derivados de los resultados de la Registraduría es
   publicar datos públicos. Publicar los **productos propios del CNC** (índice de
   ideología, consolidaciones) queda **pendiente de confirmar** con el CNC.
3. El voto **no es** confianza institucional ni evaluación del alcalde: es otro
   constructo. Entra como referencia territorial, no como sustituto (A20).

**Evidencia:** `DATA_INVENTORY.md` §14; revisión en la conversación del 29/09/2026.

**Estado:** **APPROVED** (Daniel, en conversación, 29 de septiembre de 2026).

---

### D17 — Reestructuración: una población para consultar, con respuestas rotuladas como suposición

**Fecha:** 30 de septiembre de 2026
**Decisión:** El proyecto se reorienta a una página donde cualquiera le hace a la
población sintética una pregunta **de opinión o de aprobación de un cambio en la
ciudad**, y ve cómo «respondería» esa población, en total y **por localidad en el
mapa**. **Nada de lo que responde es verdad: es una suposición**, y la página lo dice
en cada respuesta. No predice ni pretende probar nada. Cinco piezas:

1. **La población lleva a la persona completa de la EPC** (Bogotá Cómo Vamos). Cada
   agente hereda, por hot-deck, a una persona real con **todas sus respuestas**, y el
   emparejamiento incluye la **localidad**. Esto **reabre DI-B10** (donante con
   localidad), aprobado por Daniel en esta decisión.
2. **Una pregunta nueva se responde con un «puente».** Un modelo de lenguaje **no
   contesta por los agentes** (Experimento 8): propone qué preguntas medidas se
   relacionan con la nueva y en qué sentido. Cada agente responde a partir de **sus
   propias respuestas reales** a esas preguntas. La página muestra el puente.
3. **Reformulación sugerida.** Cuando alguien escribe su pregunta, la página le
   propone automáticamente una versión reformulada que el simulador pueda responder
   bien: sobre opinión o aprobación, con una escala clara y relacionada con lo que la
   EPC mide. Si la pregunta no se puede acercar a nada medido, lo dice en vez de
   inventar.
4. **Cada consulta es independiente.** Todas parten de la misma población; ninguna la
   modifica ni deja rastro.
5. **Validación con respuestas conocidas.** Se apartan preguntas que la EPC sí midió;
   la población no las ve al construirse; se le hacen como si fueran nuevas, por el
   mismo camino del puente, y se comparan con lo que respondió la gente real, en la
   ciudad y por localidad. Se **pre-registra** antes de correr. La página publica el
   puntaje.

**Justificación.**
- Es lo que el proyecto sabe hacer bien: reproducir la **distribución** de opiniones
  medidas (por debajo del piso de ruido), no predecir individuos (R² ≈ 0,02).
- El puente pone la **variedad entre personas y localidades en los datos**, no en el
  modelo de lenguaje, que es lo que falló en el Experimento 8 (aplanaba a las personas,
  0,30× la variación real). El Experimento 9 dejó permitido usar el LLM para texto y
  estructura, nunca para fijar cifras; el puente y la reformulación caben ahí.
- La EPC es la única fuente pública de opinión con localidad (DI-B10); sin ella el
  mapa mostraría composición, no geografía (paso 0b de A08).

**Alternativas consideradas:**
- *Que un LLM responda como cada agente* (estilo MiroFish) — descartada por el
  Experimento 8.
- *Solo un catálogo de preguntas medidas, sin preguntas nuevas* — más seguro, pero no
  responde a lo que Daniel quiere (aprobación de cambios hipotéticos). Queda como el
  modo base: una pregunta que la EPC midió se responde con el dato, sin puente.

**Límites.**
1. **No se usa nada del CNC con datos de personas** (R10 sigue igual).
2. **Gasto:** el puente y la reformulación llaman a un LLM por pregunta, con la clave de
   OpenRouter del jefe de Daniel (aprobado por Daniel). El costo se registra por
   llamada, como en el Experimento 9.
3. **Que el puente funcione no está probado.** Lo decide la validación (pieza 5).

**Evidencia:** conversación del 30/09/2026; inventario de la EPC en
`DATA_INVENTORY.md` §13.8.

**Estado:** **APPROVED** (Daniel, en conversación, 30 de septiembre de 2026: «sí a las
tres» —el diseño del puente, reabrir DI-B10 y el gasto en LLM—, y la reformulación
sugerida).

**Actualización (30/09/2026): las preguntas nuevas siguen sin mapa (lectura B).** La
prueba de localidades con 2022-2024 (`PUENTE_LOCALIDADES_RESULTS.md`) cumplió su regla
escrita (lectura A, 11 de 11), pero un control no pre-registrado mostró que r_loc estaba
inflado por el ruido de muestreo compartido; con el control, el puente no le gana a la
demografía (6 de 11). Daniel, en conversación: «mantenemos B». La población 2022-2024 se
construye para el mapa de las preguntas del catálogo.

---

### D18 — Preguntas nuevas: el tono general por grupo y las preguntas relacionadas con su dato real, sin nivel

**Fecha:** 2 de octubre de 2026
**Decisión:** En una pregunta nueva (sin dato en la EPC), la página deja de mostrar lo
que el puente supone y muestra solo datos medidos, rotulados por lo que son:

1. **Grupos:** el **tono general** por grupo, a la vista, con el rótulo «Así suelen
   responder estos grupos en la encuesta» y la aclaración de que no es una medición de
   la pregunta y es el mismo para toda pregunta nueva. Reemplaza las barras del puente.
2. **Preguntas relacionadas:** el modelo sigue eligiendo qué preguntas del catálogo se
   relacionan y en qué sentido; junto a cada una se muestra lo que la gente respondió de
   verdad (ciudad, con sus años), con enlace a verla completa con su mapa.
3. **Sin nivel:** el nivel que propone el modelo se descarta. Una pregunta nueva no tiene
   cifra propia.
4. **Sin fuerza:** el rótulo «base fuerte / media / débil» se quita, porque medía qué tan
   bien sostenía el puente unas barras que ya no se muestran.

**Justificación.**
- **Regla de salida escrita antes de correr** (`BANCO_PREGUNTAS_NUEVAS.md` §10.2-10.3): el
  puente tenía que ordenar bien al menos el 67 % de las 699 diferencias claras entre
  grupos de la práctica. Tres versiones dieron 60-63 % (la última, 0,627); el tono
  general, sin API, 62 %. La regla dijo parar y adoptar el «camino 2».
- **El nivel no distingue:** con el metro elevado y el Corredor Verde
  (`PREGUNTAS_REALES_NUEVAS_RESULTS.md`) propuso 3,7 en las dos.
- El Experimento 9 ya dejaba al LLM fuera de fijar cifras; con esto, en una pregunta
  nueva **ninguna cifra que se ve sale del modelo**.

**Alternativas consideradas:**
- *Seguir mejorando el puente para el orden de los grupos* — descartada por la regla
  escrita: no se prueban más versiones para eso. El banco guardado (51 preguntas) queda
  para una idea nueva de verdad, pre-registrada.
- *Mantener las barras del puente escondidas* (DI-CO13) — descartada: muestran algo que
  no le gana al tono general y lo presentan como específico de la pregunta.
- *Dejar la fuerza como «qué tan parecidas son las relacionadas»* — descartada por
  simple: cada relacionada se ve con su texto y su dato, y quien lee juzga el parecido.

**Límites.**
1. El 62 % es de los cortes de la práctica (estrato 1, 2, 3, 4, 5-6); la página usa
   1-2, 3-4, 5-6.
2. El gasto por consulta no cambia: el puente se sigue pidiendo para elegir las
   relacionadas.

**Evidencia:** `BANCO_PREGUNTAS_NUEVAS.md` §10; `PREGUNTAS_REALES_NUEVAS_RESULTS.md`;
DI-CO14 a DI-CO16 en `src/consulta/motor.py`; `PAGINA_CONSULTA.md` §5.8.

**Estado:** **APPROVED** (Daniel, en conversación, 2 de octubre de 2026: «apruebo» la
propuesta de tres puntos, sin cifra propia para las preguntas nuevas y sin la fuerza).

**Actualización (5/10/2026): el tono por grupo queda como contexto, sin cifra de acierto.** En el banco
ampliado (`TECHO_GRUPOS_LOTES_RESULTS.md`), el tono acertó 0,466 de las diferencias claras de los lotes 2 y
3, peor que el azar; el «62 %» del lote 1 no se generaliza. Daniel eligió seguir mostrándolo como contexto
descriptivo («Así responden estos grupos en general») y sin decir que sirve para predecir (opción 3). Claude
había recomendado quitarlo (opción 2). DI-CO21 en `src/consulta/motor.py`.

---

### D19 — Una pregunta nueva trae una estimación de si Bogotá estaría de acuerdo

**Fecha:** 5 de octubre de 2026
**Decisión:** Para una pregunta nueva, la página da una **estimación del porcentaje que estaría de acuerdo**:
- se calcula con Claude Sonnet 5.5 eligiendo preguntas parecidas entre las 92 de acuerdo o sí/no medidas de
  la práctica del banco; el porcentaje es la media real de las elegidas;
- se muestra con un rango de ±21,9 puntos;
- dice **«probablemente sí» o «probablemente no» solo cuando el rango no cruza el 50 %**; si lo cruza, dice
  «dividida»;
- siempre va rotulada como estimación, con las preguntas en que se apoya y su resultado real, y sin mapa.

Es la configuración validada, sin cambios. Reemplaza el «no podemos decir…» de DI-CO20, que queda como
respaldo si la estimación falla.

**Justificación.**
- Pasó la regla pre-registrada en la práctica (`NIVEL_ACUERDO_SONNET_RESULTS.md`: error 13,9; lado de la
  mayoría 80 %; al decidir, 16 de 16).
- La repitió en el guardado, con 74 preguntas que nadie había mirado
  (`NIVEL_ACUERDO_VALIDACION_RESULTS.md`: error 12,5; lado 77 %, contra 51 % de decir siempre «no»; al
  decidir, 12 de 12).
- El modelo no responde por nadie ni pone cifras (Experimentos 8 y 9): solo elige preguntas medidas.

**Alternativas consideradas:**
- *Seguir sin estimación* (D18): honesto, pero Daniel lo pidió y ya hay evidencia validada.
- *Usar mimo, el modelo de la página*: más barato, pero nunca se probó para esto.
- *Sumar como candidatas las 74 del guardado*: es una configuración no probada; queda para una prueba propia.

**Límites.**
1. En ~5 de cada 6 preguntas la respuesta es «dividida».
2. El rango es ancho (±22).
3. En las tres preguntas guardadas sobre el metro, el lado de la mayoría quedó sin decidir.
4. Las candidatas son 92 fijas: una pregunta sin ninguna parecida entre ellas recibe una estimación pobre.
5. Cuesta ~USD 0,02 por pregunta nueva, además de la reformulación y el puente.

**Evidencia:** la de la justificación; DI-CO22 en `src/consulta/motor.py`.

**Estado:** **APPROVED** (Daniel, en conversación, 5 de octubre de 2026: «apruebo las tres como las
propones»: Sonnet, las 92 candidatas validadas y la forma de mostrarlo).

**Actualización (5/10/2026): 109 candidatas.** Con las 17 preguntas de práctica del lote 5 (Encuesta Distrital de
Percepción 2025, mismo formato que la página), en 95 preguntas guardadas el error bajó de 12,8 a 11,9 y, al decir
«probablemente», acertó 17 de 17 contra 12 de 12 (`NIVEL_ACUERDO_LOTE5_RESULTS.md`). La regla pre-registrada pedía
reemplazar la configuración, y Daniel aprobó llevarlo a la página. DI-CO23 en `src/consulta/motor.py`.

**Actualización (6/10/2026): el modelo pasa a GPT-6 Luna** por D20. Lo demás de D19 sigue igual.

### D20 — La estimación de una pregunta nueva usa GPT-6 Luna, aunque no igualó a Sonnet

**Fecha:** 6 de octubre de 2026
**Decisión:** La estimación de D19 pasa de Claude Sonnet 5.5 a `openai/gpt-6-luna`.
- Mismo método y mismas 109 candidatas.
- El rango pasa a **±23,4 puntos**: es el h de Luna, el cuantil 80 % de su error en la práctica.
- La página cita las cifras de Luna, no las de Sonnet.

**Justificación.** El jefe de Daniel pidió bajar el gasto en la API. Luna cuesta **unas 20 veces menos** por
pregunta nueva (~USD 0,0012 contra ~0,024). En su prueba pre-registrada (`NIVEL_ACUERDO_LUNA_RESULTS.md`)
cumplió las tres condiciones de la regla con que se validó Sonnet:
- error 14,5 en la práctica y 14,3 en el guardado;
- lado de la mayoría 83 % y 69 %;
- 26 de 28 al decir «probablemente».

**Lo que se acepta perder, dicho tal cual.** Luna **no** cumplió la cuarta condición del pre-registro: no
perder más de 1,5 puntos de error frente a Sonnet en el guardado. Pierde 2,4 (14,3 contra 11,9). Además:
- decide menos (11 de 95 contra 17);
- al decidir se equivocó 2 veces (10 de 11), y Sonnet ninguna (17 de 17).

**Esto no es un «pasó».** Es una decisión de proyecto: se cambia precisión por costo, con la pérdida medida y
a la vista.

**Alternativas consideradas:**
- *Seguir con Sonnet*: la mejor precisión medida, pero al costo que el jefe objetó.
- *mimo*: no cumplió la regla (16,2 de error en la práctica, 86 % al decidir).
- *Volver a D18, sin estimación*: costo cero de Sonnet, pero se pierde una estimación que acierta el lado
  de la mayoría 7 de cada 10 veces.

**Límites.**
1. Valen los de D19, con el rango algo más ancho (±23,4).
2. La cifra que cita la página se midió con el texto original de cada encuesta, no con la reformulación.
   Medir eso es la parte A de `NIVEL_ACUERDO_REDACCION`, que debe terminarse con Luna, el modelo de la página.
3. Los conjuntos de la prueba de Luna ya se habían usado para Sonnet y mimo, así que no es una validación con
   preguntas nuevas.

**Evidencia:**
- `NIVEL_ACUERDO_LUNA_RESULTS.md`;
- DI-CO25 en `src/consulta/motor.py`.

**Estado:** **APPROVED** (Daniel, en conversación, 6 de octubre de 2026: «cambiemos a luna», después de ver
las cifras de los dos modelos lado a lado y la advertencia de que no era un «pasó»).

**Corrección (6/10/2026): las cifras que cita la página.** Las de arriba (69 %; 10 de 11) se midieron con el texto
original de cada encuesta. Con la página tal como funciona, que reformula primero y desde DI-CO26 lo hace con Luna, en 90
preguntas guardadas acierta el lado el **63 %** y, al decir «probablemente», **3 de 4**
(`NIVEL_ACUERDO_REDACCION_RESULTS.md` y `LUNA_PAGINA_RESULTS.md`). La página cita estas desde DI-CO27.

**Actualización (6/10/2026): la estimación usa el texto de la persona.** Así se recupera parte de lo perdido: 68 % y 5 de 5
en 90 guardadas (`TEXTO_PERSONA_RESULTS.md`), medido con el texto de la encuesta, que es el mejor caso. La página lo dice.
DI-CO28.

**Actualización (6/10/2026): 139 candidatas.** Entran las 30 de práctica del lote 6, de opinión política de las encuestas
del CNC (D21). En 129 guardadas, error 14,8 contra 15,0, acierta el lado el 71 % y 10 de 11 al decidir
(`NIVEL_ACUERDO_LOTE6_RESULTS.md`). Cumple la regla pre-registrada y Daniel aprobó llevarlo a la página. Decide menos
veces. DI-CO29.


### D21 — Las encuestas políticas del CNC entran al proyecto, incluida la intención de voto

**Fecha:** 6 de octubre de 2026
**Decisión:** Entran al proyecto 10 encuestas del CNC con su diccionario. Son nacionales, de 2.000 a 4.600
encuestados, con 256 a 545 en Bogotá y factor de expansión:
- cinco para Semana, de 2021 y 2022;
- cinco para Revista Cambio, de 2026.

Viven fuera del repositorio, en la carpeta de `BSS_CNC_POLITICA_DIR` (en el PC del CNC,
`Desktop\CNC_datos_nuevos`). Inventario en `DATA_INVENTORY.md` §16. Daniel y su jefe decidieron tres cosas:
- **A. Qué puede ir a una API, incluidos los modelos de lenguaje:**
  - **sí** el texto de las preguntas de opinión y sus escalas;
  - **no** las respuestas individuales;
  - **no** las preguntas abiertas;
  - los porcentajes agregados se calculan en el equipo.
  Es una excepción a R10 limitada a estos 10 estudios. R10 sigue igual para los estudios del CNC con datos de
  personas (§12).
- **B. La intención de voto entra en tres niveles:**
  1. la opinión política (aprobación, imagen, el paro, la migración) como preguntas del banco;
  2. la intención de voto como dato histórico medido, con fecha y fuente;
  3. la simulación de la intención de voto ante una pregunta nueva.
- **C. El inventario de preguntas** (textos, escalas y tamaños de muestra, sin ningún dato) se sube al repositorio.

**Justificación:** el jefe de Daniel pidió incluir todo lo relacionado con política e intención de voto. La revisión
de estructura (6/10, sin imprimir valores) no encontró columnas de datos personales, y todas las bases traen factor
de expansión.

**Condiciones, que son parte de la decisión:**
1. **Nada electoral se muestra en la página (niveles 2 y 3) antes de que el área jurídica del CNC lo revise.** En
   Colombia, la publicación de encuestas electorales está regulada, y una cifra simulada de intención de voto podría
   quedar cubierta.
2. **El nivel 3 se valida pre-registrado antes de usarse,** como todo lo demás. La prueba de la segunda vuelta de
   2026 (`SEGUNDA_VUELTA_2026_SPECIFICATION.md`) sigue igual. Si estas encuestas se usan en ella, va como enmienda
   fechada.
3. **El nivel 3 cambia el propósito del proyecto.** Hasta aquí, «no es un predictor». Con D21, la intención de voto
   simulada es la excepción, y donde se muestre debe decir que es una suposición, con su error medido.
4. **Estas encuestas no sirven por localidad:** solo traen municipio. Valen para Bogotá en total, y por sexo, edad y
   estrato.

**Alternativas consideradas:** solo el nivel 1 (lo recomendado, junto con el 2); los niveles 1 y 2, sin simular. Daniel
eligió los tres.

**Estado:** **APPROVED** (Daniel, en conversación, 6 de octubre de 2026: «A sí, B sí, C sí» y, sobre el alcance de B,
«los tres niveles»).

**Actualización (7/10/2026): revisión jurídica aprobada.** Daniel informa que hizo la revisión jurídica con el equipo del
CNC y que queda aprobado mostrar en la página la intención de voto, medida y simulada («ya hice la revision juridica con el
equipo y queda aprobado para que quede subido en la pagina»). Se cumple así la condición 1. Antes, el nivel 3 se validó:
- **contra las 215 guardadas del lote 7:** cumple la regla (`VOTO_SIMULADO_RESULTS.md`);
- **contra la Registraduría:** 4,2 puntos de error en tres elecciones en Bogotá (`VOTO_REGISTRADURIA_RESULTS.md`).

Cómo se lleva a la página va en `PAGINA_CONSULTA.md`.

**Llevado a la página (7/10/2026, `PAGINA_CONSULTA.md` §5.22, DI-CO30).** Daniel eligió:
- que la página reconozca sola las preguntas de voto. La reformulación versión 3 pasó su validación pre-registrada
  (`REFORMULACION_VOTO_RESULTS.md`);
- mostrar la estimación más las encuestas del CNC en que se apoya, con su fecha y su resultado en Bogotá, sin mapa;
- dejar fuera las consultas interpartidistas y la tendencia.

Se muestra solo la intención de voto **simulada**, con su error medido y la banda de suposición. La medida aparece únicamente
como apoyo de cada estimación.

**Los grupos (8/10/2026).** Daniel confirma que la aprobación jurídica cubre también la intención de voto por sexo, edad y
estrato («sí, la aprobación jurídica cubre los grupos»). Antes de mostrarlos se validan con su pre-registro
(`VOTO_GRUPOS_SPECIFICATION.md`).


### D22 — Las preguntas nuevas políticas e institucionales se estiman con agentes armados con la encuesta de cada persona

**Fecha:** 16 de octubre de 2026
**Decisión:** Para las preguntas **nuevas** de tema **político o institucional**, la página estimará con **agentes**: 200
encuestados reales de la EPC 2025, cada uno con sus 40 respuestas del catálogo y sus cuatro datos demográficos. Un modelo de
lenguaje responde como cada persona, con la probabilidad de cada opción.
- **Las demás preguntas nuevas** siguen con la estimación de hoy (D19, D20, DI-CO39).
- **Lo que la página muestra con los agentes:**
  - la cifra de Bogotá con un rango;
  - las cifras por estrato, edad y sexo;
  - sin mapa por localidad.

**Justificación:** en las pruebas pre-registradas, los agentes le ganan a la página en lo político y lo institucional.
- **`PERSONAS_POLITICA_RESULTS.md`:** 10 preguntas de gobierno y del alcalde, error del total de 7,4 a 7,8 contra 14,3 de la
  página; acierta casi exacto la gestión de Galán (26,2 contra 26,4).
- **`AGENTES_2026_RESULTS.md`:** 7 preguntas de opinión política nacional del CNC de 2026, nunca hechas a esas personas, error
  de 9,0 contra 12,7 de la página y 10,6 de decir 50 %; acierta el lado en 6 de 7.

Daniel y su jefe priorizan lo político y lo institucional.

**Lo que se acepta, dicho tal cual:**
- **No es un «pasó».** Ninguna prueba cumplió todas sus reglas.
  - En lo político, la TVD quedó en 0,164; la regla pedía 0,15 o menos.
  - En las 13 preguntas de 2026, los agentes empataron con la página (15,2 contra 14,6), porque perdieron en las del metro.
- **Exagera en algunas preguntas:** sobreestima la imagen de Galán y la transparencia, y subestima el rumbo de la ciudad.
- **Fuera de lo político tiene un sesgo pesimista** (`PERSONAS_PULIDAS_RESULTS.md`). Por eso se limita a lo político e
  institucional.

**Alternativas consideradas:**
- *Seguir solo con la estimación de hoy*: más débil en lo político.
- *Agentes para todas las preguntas nuevas*: peor fuera de lo político.
- *Completar el perfil* con datos de su vida, un resumen o una vida inventada: no cambia nada en lo político
  (`PERSONAS_POLITICA_RESULTS.md`).
- *Promediar dos modelos*: empeora con DeepSeek (`AGENTES_2026_RESULTS.md`).

**Condiciones, que son parte de la decisión:**
1. **Antes de abrirlo en la página,** hacen falta dos validaciones pre-registradas, con el modelo real:
   - que la reformulación reconozca cuándo una pregunta es política o institucional;
   - una prueba de los agentes con preguntas políticas nuevas que no se hayan usado.
2. **Mientras tanto,** se construye y se prueba solo en modo simulado.
3. **Los agentes salen solo de la EPC,** pública y anónima. Con las encuestas del CNC no, mientras siga D21: sus respuestas
   individuales no van a un modelo de lenguaje.
4. **La intención de voto no se estima con agentes.**
5. **La página dice cómo se estimó:** con 200 bogotanos reales de 2025, que responden según sus otras respuestas, con un
   modelo de lenguaje. Es una suposición, no una medición.

**Evidencia:**
- `PERSONAS_CON_ENCUESTA_RESULTS.md`, `PERSONAS_PULIDAS_RESULTS.md`, `PERSONAS_POLITICA_RESULTS.md` y
  `AGENTES_2026_RESULTS.md`;
- el código en `src/consulta/agentes.py`.

**Estado:** **APPROVED para construir en modo simulado** (Daniel, en conversación, 16 de octubre de 2026: «nos interesa más lo
político y lo institucional» y «sí, empieza por lo que no gasta»). Abrirlo en la página espera las dos validaciones de la
condición 1, y que se recargue la cuenta de OpenRouter.


### D23 — En lo político, el proyecto busca acercarse lo más posible a predecir 2026

**Fecha:** 16 de octubre de 2026
**Decisión:** Para la percepción política y la intención de voto, el objetivo del proyecto pasa a ser **acercarse lo más
posible a lo que la gente responde en 2026**: una estimación cercana, con su error medido, no una cifra exacta.
- **Las preguntas de percepción política** (el alcalde, el gobierno, las instituciones) se tratan como **nuevas**: las
  responden los agentes de D22, aunque la EPC haya medido algo parecido en 2024 y 2025. El dato medido se muestra al lado,
  como punto de partida.
- **La intención de voto también se prueba con agentes,** además de la estimación de hoy (D21, nivel 3).
- **Se prueban, cada uno con su pre-registro:**
  - más agentes (los 1.520 de la EPC 2025);
  - el ajuste del total a la última encuesta publicada;
  - un resumen de noticias para los agentes.
- **La prueba más limpia:** pre-registrar lo que los agentes predicen para la EPC 2026 antes de que se publique (diciembre de
  2026).

**Justificación:** Daniel y su jefe buscan un «predictor» de lo político («acercarnos lo que más se pueda a un predictor,
obviamente no podemos acercarnos a algo que nos dé una respuesta casi que acertada, pero sí que sea muy cercano»). En las
pruebas, los agentes fueron lo que más se acercó en lo político (D22).

**Lo que cambia del proyecto, dicho tal cual:** hasta aquí, «no es un predictor», salvo la intención de voto simulada (D21).
Con D23, la percepción política entra en la misma excepción. Toda cifra de este tipo:
- va con su error medido;
- dice que es una suposición, no una medición;
- **nunca se llama predicción sin su error al lado.**

**Lo que no se promete:**
- **una cifra casi exacta.** Con 200 agentes, el azar de la muestra ya da unos ±7 puntos, y en las pruebas el error fue de unos
  8;
- **ver un cambio brusco antes de que alguien lo mida.** Los agentes son personas de 2025.

**Alternativas consideradas:**
- *Seguir con el dato medido para la percepción del alcalde*: más exacto para 2024-2025, pero no dice nada de 2026.
- *Las redes sociales para actualizar a los agentes:* quien opina en redes no representa a Bogotá, los datos son caros o están
  cerrados, y son datos personales. Se deja para después, como señal agregada y solo si se valida contra encuestas.

**Condiciones:**
1. **Cada pieza se valida pre-registrada** antes de llegar a la página. La primera es la intención de voto con agentes
   (`VOTO_AGENTES_SPECIFICATION.md`).
2. **D21 sigue igual:**
   - los agentes salen de la EPC;
   - las respuestas individuales del CNC no van a un modelo de lenguaje;
   - sus cifras agregadas solo se usan dentro del equipo.
3. **La intención de voto con agentes es una simulación más.** La revisión jurídica del 7/10 cubre la intención de voto simulada
   (D21). Antes de mostrar la de los agentes en la página, conviene confirmarlo con el área jurídica.

**Estado:** **APPROVED** (Daniel, en conversación, 16 de octubre de 2026: «lo que nos interesa es que la percepción del alcalde
no esté medida, que la mayoría de preguntas de percepción política e intenciones de voto sean nuevas y que nuestros agentes se
acerquen a las respuestas del 2026», y «sí, escribe la D23»).

---

# 40. DECISIONES ABIERTAS

### ~~A01~~ — RESUELTA → ver D12

### ~~A02~~ — RESUELTA (hallazgo, no decisión)
~~¿Qué datos internos del CNC están disponibles?~~

**Respuesta (Septiembre 2026):** cuatro encuestas con microdato — Salud Mental Bogotá 2023 (n=15.151), Sustancias Psicoactivas Bogotá 2022 (n=10.912), Apropiación Digital Colombia 2024 (n=3.614), SABE Colombia 2015 (n=23.877).

Contra las cinco preguntas técnicas de DATA_SPECIFICATION.md §6:
1. **Desagregación geográfica:** las dos de Bogotá llegan a **localidad** (20), con n mediano por localidad de 776 y 460.
2. **Estructura longitudinal:** **no hay panel ni tracking.** Cuatro cortes transversales de temas distintos, sin una pregunta repetida entre olas. La validación de nivel 3 sigue dependiendo enteramente de la ECP.
3. **Variables puente:** sí — sexo, edad, educación, estrato, localidad.
4. **Factores de expansión:** sí, con diseño muestral complejo documentado (estratos, UPM) y una librería de estimación (`svy_prop`, linealización de Taylor) que el proyecto debería adoptar.
5. **Restricciones de uso:** severas y vigentes. Copias idénticas a las del cliente con nombres, direcciones y GPS. No salen del equipo; solo circulan agregados. Ver sección 32.

**Ninguna mide confianza institucional**, así que A02 se cierra con "sí, pero no sirve para lo que se esperaba de él". Lo que sí aportaron fue decisivo por otra vía: la evidencia territorial que sustenta D15.

### A03
¿Qué datasets específicos de DANE utilizaremos?

**Avance:** Multipropósito 2021 (microdato completo), proyecciones de población por localidad (anexo 2021 + revisión 2025), y ECP 2017/2019/2021/2023 con sus módulos de Democracia, Participación y Capital Social — todos descargados y en uso.

### A04
¿Qué datasets específicos de Bogotá utilizaremos?

**Avance:** Encuesta de Percepción de Confianza Institucional (Veeduría Distrital) como donante; proyecciones localidad/UPL 2005-2035 (revisión 2025) como marginal vigente.

### A05
¿Cuál será el método para construir la población sintética?

**Avance (no decisión final):** hot-deck nearest-neighbour implementado, auditado y corriendo con datos reales, pendiente de confirmación como D0X.

**El desempate determinista quedó resuelto (17/09/2026, DI-M1)** y su costo resultó ser mucho mayor de lo que esta entrada suponía. No eran "131 agentes apilados en 1,0": con variables de distancia discretas el defecto degrada la población entera, y estaba inflando el desempeño de todos los modelos de influencia social. Ver sección 33 y `claude/REEJECUCION_DI-M1.md`.

Sigue abierto el índice de confianza que promedia un número variable de ítems.

**Lo que esta entrada debería haber dicho antes:** un defecto anotado durante tres iteraciones como pendiente menor resultó ser el que más movía los resultados. La lección no es "arreglar antes"; es que **no sabíamos cuánto valía hasta que un control con umbral numérico lo midió**.

### A06
¿Cuál será el modelo de dinámica de opinión?

**Avance (no decisión final), con evidencia nueva y desfavorable:** Friedkin-Johnsen con \(\phi = 0{,}3\) es el mejor de siete modelos evaluados (W1 total 0,5310 contra 0,6265 de congelar), pero:

- falla **4 de 5** predicciones pre-registradas del Experimento 3 (nivel, dispersión, no-monotonicidad, colas), y acierta solo la ausencia de bimodalidad;
- empata con los otros seis en 2019 — toda su ventaja viene de 2023, la ola con el salto de no-respuesta sin analizar (sección 33);
- es superado por **un escalar por año** en la descomposición del error de nivel (32 % vs 16 %).

**Actualización tras el Experimento 4 (16/09/2026) — cambia el cuadro.** Añadido el término exógeno que faltaba, FJ con φ=0,1 le gana a la traslación pura por **37,5 %**, y en **360 de 360 configuraciones**. El Experimento 3 estaba midiendo la ausencia de un término, no el fracaso de un mecanismo.

Pero el control post-hoc acota lo que se puede reclamar: un modelo de **contracción uniforme hacia la media, sin ninguna red**, llega a 0,2725 contra 0,2650 de FJ. La descomposición es traslación 0,4262 → +encogimiento sin red 0,2725 (−36 %) → +red social 0,2650 (−2,8 %).

**Lo que los datos piden es traslación más encogimiento; la influencia social por la red aporta 2,8 %.**

**Cierre definitivo tras el Experimento 7 (17/09/2026).** Con ocho transiciones y dos objetivos —el doble de puntos que todo lo anterior—, el orden de mérito es **cognición motivada · Friedkin-Johnsen · baseline · traslación · contracción**, idéntico en los dos objetivos (Spearman 0,90). Cognición motivada gana con el mismo modelo y casi los mismos parámetros en ambos.

**Y aun así la recomendación operativa no es un mecanismo.** El control de ruido (A11) les gana a todos. Lo que los mecanismos aportan sobre el baseline afín es difuminado de la distribución, que un solo parámetro exógeno produce más barato y sin supuestos sobre influencia social.

**A06 se puede cerrar así como D0X:** para el prototipo, **`traslación + u + γ + ruido`** —tres escalares exógenos por periodo, sin red—, reportando al lado cognición motivada con `α=0,3 λ=0,5 k=2,0 ρ≈1` como la mejor alternativa endógena y la distancia que la separa. Lo que **no** se puede afirmar, después de siete experimentos pre-registrados, es haber identificado un mecanismo social.

**Corrección de la v0.15, el mismo día.** La recomendación cambia: **el ladeo categórico**, dos escalares exógenos por periodo sobre el soporte de la variable (`src/opinion/forzamiento_categorico.py`). Llega al piso de ruido donde lo anterior quedaba a 3-6 veces, con un parámetro menos y sin ningún término de ruido. Lo que no cambia es la parte que importa: sigue sin haber mecanismo social identificado, y ahora con menos margen que nunca.

*(Se conserva abajo el cierre provisional de la v0.11, sin editar.)*

**Cierre provisional tras el Experimento 5 (16/09/2026).** Se probó por fin cognición motivada, la familia que `MODEL_SPECIFICATION.md` §4 había designado como objetivo por tener la mejor evidencia publicada. Con 108 configuraciones contra 2, **pierde**:

| Modelo | Mejor W1 total | Parámetros barridos |
|---|---|---|
| Friedkin-Johnsen | **0,2652** | 1 |
| Contracción uniforme, sin red | 0,2750 | 1 |
| Cognición motivada | 0,2811 | 5 |
| Traslación pura | 0,4262 | 0 |
| DeGroot (Exp. 3) | peor que el ruido | 0 |

**Ninguna de las tres familias mejora materialmente sobre "traslación + encogimiento".** Ahora la afirmación sí está respaldada: no es que se probara una familia incapaz por estructura, es que se probaron las tres.

Para el prototipo, la recomendación operativa es **Friedkin-Johnsen con φ bajo (0,08–0,1) más forzamiento exógeno por periodo**, reportando siempre al lado el baseline de encogimiento sin red, que queda a 2–4 % — no porque FJ sea el mecanismo correcto, sino porque es el más simple de los que ajustan y su ventaja sobre el baseline es honesta y medible. A06 se puede cerrar así como D0X cuando se confirme; lo que **no** se puede afirmar es haber identificado el mecanismo.

### ~~A07~~ — RESUELTA → ver D15
~~¿Cómo se construirá la red de interacción?~~

### A08
¿Cuál será el tamaño óptimo de la población?

### A09
¿Cuántas simulaciones necesita cada escenario?

**Avance:** dispersión entre semillas de 0,0045 en W1, contra 0,015 de rango entre configuraciones. El rango propuesto (100–1.000) es holgado.

### A10
¿Cómo se calibrará el modelo?

**Avance:** reorientada — ver sección 22. Los parámetros de red están medidos y \(\phi\) no discrimina; lo que hay que calibrar es el término exógeno por periodo.

### A11
¿Cuáles serán los baselines?

**Avance sustantivo (Experimento 3):** DeGroot quedaba fijado como baseline obligatorio, pero medido resultó **peor que el ruido** (0,9387 vs 0,6287). El baseline que discrimina es **congelar la opinión** (0,6265).

**Avance mayor (Experimento 4):** apareció un baseline mucho más exigente, y es el que hay que adoptar. **Traslación + contracción uniforme, ambas con forzamiento exógeno ajustado por periodo**: acierta el nivel por construcción y produce el 97 % del ajuste del mejor ABM sin usar red alguna. Cualquier afirmación futura de que el ABM aporta tiene que medirse contra eso, no contra congelar ni contra DeGroot.

Propuesta de conjunto mínimo: **{traslación+u, contracción+u, ruido+u, DeGroot}**, con los dos primeros como los exigentes. Falta confirmarlo como D0X.

**Avance definitivo (Experimento 7, 17/09/2026) — el baseline que faltaba.** `traslación+u+γ` no era suficientemente duro: acierta media y desviación, pero deja la distribución como **cinco picos enteros trasladados fuera de la grilla**, y cualquier modelo que difumine le gana por eso solo. Con ocho transiciones, cognición motivada y Friedkin-Johnsen le ganaron por 8,8 % — y **ruido gaussiano sin red, con un parámetro, les ganó a los dos**.

**El baseline correcto es `traslación + u + γ + ruido`:** tres escalares exógenos por periodo —nivel, dispersión y ancho de difuminado— y ninguna red. Es el listón contra el que hay que medir cualquier afirmación futura sobre el aporte del ABM, y lleva todo el proyecto faltando. **Conjunto mínimo revisado: {traslación+u, traslación+u+γ, traslación+u+γ+ruido, DeGroot}.**

**Corrección de la v0.15, el mismo día.** Ese baseline no era el correcto: el ruido era el parche de un error de **forma funcional**, no un término que faltara. El baseline definitivo es el **ladeo categórico** —dos escalares exógenos por periodo sobre el soporte propio de la variable— que llega a **0,97× el piso de ruido en la ECP** y 1,5× en la EPC. **Conjunto mínimo definitivo: {ladeo categórico, traslación+u+γ, traslación+u, DeGroot}**, con el ladeo como el exigente. Ver `claude/FORZAMIENTO_CATEGORICO.md`.

### A12
¿Cuáles serán las métricas de validación?

**Avance:** W1 (Wasserstein-1) quedó como métrica de referencia por comparar distribuciones completas. Ver sección 21.

### ~~A13~~ — RESUELTA → ver D11

### A14
¿Qué arquitectura tecnológica definitiva se utilizará?

**Avance:** ARCHITECTURE.md define la arquitectura del prototipo y está implementada y probada de punta a punta (`src/population/`, `src/network/`, `src/opinion/`, `src/experiments/`, `config/`). Sigue sin ser decisión D0X formal, y ya tiene una desviación registrada respecto del documento: **no hay capa Mesa ni `src/model/`** (DI-E1, Fase 5). Confirmar A14 implica decidir si esa desviación se adopta en ARCHITECTURE.md o se revierte cuando llegue la Fase 8.

### A15 — Vacío de estrato en el donante de confianza institucional

La Encuesta de Confianza Institucional (Veeduría Distrital) no trae estrato socioeconómico. La corrida actual excluye `estrato` de las variables de distancia del matching para este donante. Pendiente decidir: (a) homologar `ingresos` como proxy, (b) conseguir un donante alternativo con estrato, o (c) aceptar la exclusión.

**Consecuencia mientras siga abierta:** `opinion_t0` es estadísticamente independiente de `estrato` **por construcción**. Cualquier resultado que relacione estrato con opinión sería un artefacto del método.

**Nota de la v0.7 que baja su urgencia:** medido en la ECP, el estrato explica **1,3–1,7 %** de la varianza de la confianza. La asociación que el hot-deck destruye es real pero muy pequeña; la opción (c) —aceptar la exclusión y documentarla— es más defendible de lo que parecía. Lo que **no** cambia es la consecuencia: el artefacto sigue siendo artefacto.

### ~~A16~~ — RESUELTA → ver D14

### A17 — Códigos de no-respuesta tratados como estrato ordinal

`NVCBP11AA` toma valores 0–6 pero también 8 y 9, que son códigos de no-respuesta, no estratos. 39 sobreviven al receptor final de 168.200, y `validar_agentes` los acepta (rango 0–9). En la distancia homofílica, `estrato = 9` se trata como más extremo que estrato 6, y `estrato = 0` como por debajo de estrato 1.

**Evidencia a favor de tratarlos como faltantes:** en la ECP el estrato (`P4031S1A1`) va de 0 a 6 **sin códigos 8/9**, con el 0 etiquetado como *"conexión ilegal - pirata"* y la no-respuesta como celda vacía. Otra encuesta DANE sobre la misma población codifica la no-respuesta como faltante.

Pendiente: descartar esos agentes, o codificarlos como faltante y excluirlos de la componente de estrato en la distancia.

### A18 — ¿Se evalúa la familia de confianza limitada (Hegselmann-Krause / Deffuant)? *(nueva)*

Abierta por D15. La única homofilia fuerte medida en Bogotá es la de opinión (39,5 % del círculo cercano comparte opiniones políticas), y esa es precisamente la que los modelos de confianza limitada implementan como mecanismo: se interactúa con quien piensa parecido.

A favor: es la única línea con respaldo empírico sobre la composición de la red; y es la única que podría cambiar el diagnóstico del Experimento 3, porque produce dinámicas cualitativamente distintas de las de FJ.

En contra, y hay que decirlo antes de invertir: los modelos de confianza limitada tienden a producir **fragmentación**, y la ECP muestra que Bogotá **nunca se fragmentó** (bimodalidad 0,35–0,45, siempre por debajo del umbral de 0,555). Es decir, la predicción característica de esa familia es justamente la que los datos contradicen. Habría que evaluarla en el régimen de umbral alto (donde converge en vez de fragmentar), que es el régimen menos distintivo.

### ~~A18~~ — CERRADA el 17/09/2026 con el Experimento 7 → es la mejor de las tres, y lo que aporta es difuminado

**Ahora sí, y con ocho transiciones en vez de tres.** Cognición motivada resultó **la mejor familia en los dos objetivos** del Experimento 7 (2,4260 y 2,0247), ganándole al baseline duro por 8,8 % y con **el mismo modelo y casi los mismos parámetros** en ambos (`α=0,3 λ=0,5 k=2,0`, ρ=0,9 y 1,0). Esa consistencia es real y vale anotarla: ninguna otra familia la tuvo.

**Pero pierde contra un parámetro de ruido.** El control post-hoc —`traslación+u+γ+ruido`, sin red, un parámetro— llega a 2,3136 y 1,9183, mejor que el mejor mecanismo en los dos objetivos. Lo que cognición motivada aporta sobre el baseline afín es **difuminado de la distribución**, no dinámica social.

**Cierre:** de las tres familias evaluadas es la que mejor ajusta y la única consistente entre objetivos, y aun así **no aporta nada que un término de ruido no aporte más barato**. La pregunta "¿probamos todas las familias razonables?" queda respondida: sí, y ninguna sobrevive al control correcto.

*(Se conservan abajo la reapertura del 17/09 y el cierre del 16/09, sin editar.)*

### ~~A18~~ — REABIERTA el 17/09/2026 → la re-ejecución revoca el cierre *(superada por el Experimento 7, ver arriba)*

**El cierre de abajo queda revocado.** Con la población corregida (DI-M1), cognición motivada es **la única familia cuyo desempeño no se mueve** (0,2811 → 0,2817): su ajuste no descansaba en el artefacto. Como Friedkin-Johnsen (0,2652 → 0,2978) y la contracción sin red (0,2750 → 0,3463) sí empeoran, pasa a ganarles, y tres predicciones del Experimento 5 cambian de signo:

| Predicción | antes | después |
|---|---|---|
| R1 — le gana a Friedkin-Johnsen | FALLA | **PASA** (en el mejor) |
| R2 — produce contracción tardía | FALLA (4,53 %) | **PASA** (5,25 %) |
| R3 — le gana al control sin red | FALLA (−2,2 %) | **PASA (+18,7 %)** |
| R5 — error de dispersión | PASA | **FALLA** |

**Y hay que decir los dos lados.** R1 pasa **en el mejor** pero no en la mediana (0,4180 contra 0,3151 de FJ): su mejor configuración gana, la familia en conjunto sigue siendo más errática, y barre cinco parámetros contra uno. R2 pasa por 0,25 puntos porcentuales sobre un umbral de 5 %. R5 se cae.

**Lo que no depende del margen:** cognición motivada es la única familia que produce contracción tardía (102 corridas contra 0 de FJ y 0 de contracción) y la única indiferente a la calidad de la población.

**Por qué queda abierta y no cerrada a favor.** Gana sobre la serie que arranca en 2017 (3 transiciones) y **pierde por 20 % sobre la que arranca en 2013** (4 transiciones, Experimento 6), donde ningún mecanismo le gana a dos números exógenos. Una familia que cambia de veredicto según el tramo que se mire **no está identificada: está siendo medida sin poder.** Lo resuelve el Experimento 7, con ocho transiciones y dos objetivos.

*(Se conserva abajo el cierre anterior, sin editar.)*

### ~~A18~~ — cerrada el 16/09/2026 → probada y no mejora *(revocada, ver arriba)*

**Resultado:** cognición motivada quedó implementada (`src/opinion/cognicion_motivada.py`) y evaluada con pre-registro (`claude/EXPERIMENT_5_SPECIFICATION.md` / `_RESULTS.md`). **Tres de cinco predicciones fallan**, incluida la de confianza alta. Es la **única familia que produce el perfil de contracción tardío** —88 corridas, contra 0 de Friedkin-Johnsen y 0 del control sin red— y es la mejor en el ajuste del perfil en sí (error 0,00954 contra 0,01237 de FJ). Pero las corridas que logran la forma correcta son **las que peor ajustan** (mejor W1 0,4993 contra 0,2811): consigue que la contracción acelere solo contrayendo tres veces más de lo que hay que contraer. La forma es alcanzable; la forma **con la magnitud correcta**, no.

Queda además descartado que el modelo comprara ajuste fragmentando: solo el 4,4 % de la malla evaluable supera el umbral de Sarle, y las cinco mejores no lo superan.

**Historial de esta pregunta abierta, que vale conservar:**

**Reformulada (16/09/2026), y el candidato cambió.** El diagnóstico mostró que `MODEL_SPECIFICATION.md` §4 ya había designado el **marco de cognición motivada** (Lorenz et al. 2021 / Gestefeld & Lorenz 2023) como modelo objetivo de la fase de calibración — único de los cinco con calibración publicada contra distribuciones reales de confianza institucional (ESS, R² > 0,8) y contra transiciones de panel — y **nunca se implementó**. El argumento en contra de Hegselmann-Krause sigue en pie; no aplica a cognición motivada, que tiene decaimiento suave y fue calibrada contra distribuciones no fragmentadas.

El Experimento 4 le da además una tarea concreta: es la única familia con dinámica capaz, en principio, de producir el **perfil de contracción tardío** que ni FJ ni la heterogeneidad de φ reproducen.

Pendiente: implementarla.

### A20 — ¿Cuál es el constructo del proyecto? *(nueva, 17/09/2026)*

D11 fijó **confianza institucional**, y todo lo construido hasta el Experimento 6 se validó contra la ECP del DANE, que la mide. Pero la única serie larga disponible —nueve olas anuales, ocho transiciones— es de **evaluación de gestión** (EPC de Bogotá Cómo Vamos, sección 12.4). Son dos constructos distintos sobre la misma escala y sobre instituciones que se solapan, y en los años en que se pueden comparar **se mueven en direcciones opuestas**: 2017→2019 la ECP baja 0,141 y la EPC sube 0,439.

Tres opciones, y no son equivalentes:

- **(a) Mantener confianza institucional como constructo y usar la EPC solo como serie auxiliar de dinámica.** Conservador, pero deja el veredicto principal apoyado en cuatro transiciones para siempre.
- **(b) Adoptar evaluación de gestión como el fenómeno a reproducir.** Ocho transiciones y poder real, a costa de cambiar lo que el proyecto dice medir. Obligaría a revisar D11.
- **(c) Tratarlos como dos casos del mismo laboratorio** y exigir que un mecanismo funcione en los dos antes de aceptarlo.

El Experimento 7 aporta la evidencia para decidir, pero no decide: eso es una decisión de alcance, no de datos. Mi inclinación es **(c)**, porque un mecanismo que solo funciona en un constructo no es un mecanismo, es un ajuste.

**Insumo del Experimento 7 (17/09/2026), y favorece (c):** los dos objetivos de la EPC —gestión cruda y diferencia individual— dan **el mismo veredicto** que la ECP daba para confianza institucional, con el mismo orden de mérito entre familias (Spearman 0,90). El resultado **replica entre constructos**. Eso es justo lo que (c) pide como criterio, y quita urgencia a elegir entre (a) y (b): por ahora los dos constructos dicen lo mismo.

### ~~A19~~ — RESUELTA (17/09/2026) → adoptada, implementada aparte, y con una limitación de fuente que conviene conocer

**Implementada en `src/utils/diseno.py`** (12 pruebas), **no copiando `svy_prop` del CNC** (DI-D1): esa librería estima proporciones y el proyecto necesita medias y diferencias de medias; la ECP no trae variables de diseño, así que no se le podría aplicar; y meter código interno del CNC en un repositorio que puede compartirse es una decisión de atribución que no corresponde tomar por conveniencia técnica.

**La limitación que hay que conocer: en la ECP no se puede.** Los microdatos del DANE publican `FEX_P` y `REGION` y nada más — ni estrato, ni UPM, ni pesos replicados, en ninguna de las cinco olas. Sin conglomerado no hay linealización. Para la ECP lo único honesto es inflar el error por un DEFF **prestado** y que el código deje constancia de que es prestado, que es lo que hace `deff_prestado()`.

**En la EPC sí, en cuatro olas** (`MANZANA` como UPM), y el efecto de diseño queda medido **sobre la variable del proyecto**: **DEFF 1,39 a 2,69, mediana 1,95**. Coincide con el 2,5 que el CNC midió en otros estudios, pero ahora medido aquí, que es lo que autoriza a usarlo.

**Y cambió una lectura sustantiva.** De las ocho transiciones de la serie de gestión del alcalde, **siete son distinguibles de cero y una no: 2022→2023 (z = −1,78)**. Es exactamente la que `claude/ANALISIS_NORESPUESTA_EPC.md` §3 había marcado como no establecida, por un camino completamente distinto. Dos métodos independientes señalan la misma transición y ninguno señala otra. **Ningún veredicto puede apoyarse en si un modelo acierta ese tramo.**

Detalle, la tabla completa y la prueba de sensibilidad sobre 2022 en `claude/ANALISIS_DISENO_MUESTRAL.md`.

**Lo que queda por pedir:** las variables de diseño — a DANE para la ECP, a Bogotá Cómo Vamos la manzana de 2015-2018, 2022 y 2025. Es barato y convertiría "prestado" en "medido" en toda la serie.

### ~~A19~~ — enunciado original *(conservado)*

El proyecto calcula medias ponderadas ingenuas en todas partes. Los estudios del CNC traen `svy_prop` (varianza por linealización de Taylor con estratos y conglomerados, IC en escala logit), validado internamente. El DEFF mediano medido es **2,5**, con máximos de 45–53: los errores estándar actuales del proyecto están subestimados por un factor del orden de 1,6 en el caso típico.

Afecta a todo lo que hoy se reporta sin intervalo, y en particular a la lectura de las diferencias entre olas de la ECP. Es barato de adoptar. Pendiente decidir si se copia la librería del CNC (con atribución) o se implementa aparte.

---

# 41. RIESGOS PRINCIPALES

## R01 — Datos insuficientes
Podría no existir información suficiente para construir una población sintética adecuada. **Estado: no se materializó para la población, sí para la dinámica.** Los datos alcanzan para construir y validar la población; no alcanzan para identificar un modelo generativo de opinión a nivel individual.

## R02 — Representatividad
Las encuestas pueden no representar determinadas características de la población.

## R03 — Sobreajuste
El modelo podría ser calibrado demasiado bien para datos históricos pero fallar fuera de ellos. **Estado: riesgo invertido.** El problema actual no es sobreajuste sino subajuste — el modelo no logra seguir la historia ni siquiera dentro de muestra.

## R04 — Complejidad
Un ABM demasiado complejo puede ser imposible de calibrar o validar.

## R05 — Interpretación
Los usuarios podrían interpretar escenarios como predicciones. **Estado: riesgo elevado.** Ahora sabemos que el modelo no predice esta variable. Todo material que salga del proyecto debe decirlo, y el dashboard es el punto de mayor exposición (sección 31).

## R06 — Causalidad
Podrían confundirse asociaciones estadísticas con mecanismos causales. Ver sección 34.

## R07 — Sesgo
El modelo puede reproducir o amplificar sesgos existentes en los datos. Ver sección 33.

## R08 — Rendimiento
Miles de simulaciones con cientos de miles de agentes pueden generar altos costos computacionales.

## R09 — Validación
Puede ser difícil demostrar que el ABM es superior a modelos más simples. **Estado: materializado, y medido.** Sección 25. No es una dificultad de demostración: es que, para esta variable, la superioridad es marginal.

## R10 — Confidencialidad de datos del CNC *(nuevo)*
Los estudios entregados contienen nombres, direcciones y coordenadas GPS de personas reales. Una copia accidental a un servicio de sincronización sería un incidente de datos personales, no un descuido de repositorio. **Estado (16/09/2026): mitigado, no eliminado.** La carpeta salió del repositorio, la ruta salió del código y el equipo no tiene carpetas de sincronización en el directorio de usuario (sección 32). Lo que queda es que el riesgo es permanente mientras los archivos existan: cualquier copia futura —a un USB, a un correo, a una carpeta de trabajo compartida— lo reinstala. No se cierra; se vigila.

---

# 42. PRINCIPIO DE DESARROLLO

El orden de desarrollo debe ser:

```text
INVESTIGACIÓN
     ↓
DATOS
     ↓
POBLACIÓN SINTÉTICA
     ↓
MODELO
     ↓
PROTOTIPO
     ↓
CALIBRACIÓN
     ↓
VALIDACIÓN
     ↓
ESCENARIOS
     ↓
DASHBOARD
     ↓
ESCALAMIENTO
```

No saltar etapas sin justificarlo.

---

# 43. ESTADO ACTUAL DEL PROYECTO

## Estado general

**Prototipo completo y validado. Resultado de validación mayormente negativo, y eso reorienta el proyecto.**

## Lo que ya sabemos

- Bogotá es el caso piloto; el foco es opinión pública; el enfoque es ABM sobre población sintética.
- La variable de opinión es **confianza institucional** (D11), y se modela como **índice compuesto** — los 13 ítems se mueven como uno solo (81 % de la variación entre años en un componente).
- La estructura del agente está fijada (D12) y los agentes se muestrean por PPS con el factor de expansión (D14), contra un marginal territorial que ahora es la revisión 2025 de las proyecciones DANE-SDP.
- El pipeline de población es reproducible de punta a punta y ajusta bien: TVD territorial **0,032**, W1 de la distribución de opinión **0,048**.
- Los tres generadores de red están implementados, y su grado y composición **ya no son supuestos**: \(\bar{k} \approx 5\), 26 % sin red, 11 ejes de composición medidos. **A07 está cerrada (D15):** los tres generadores pasan a ser variantes de sensibilidad, no candidatos a "el correcto".
- DeGroot y Friedkin-Johnsen están implementados y evaluados contra cuatro olas reales de la ECP, con pre-registro.
- **El CNC entregó sus datos (A02): cuatro encuestas, sin panel, sin confianza institucional**, pero con la evidencia territorial que cierra A07.

## Lo que ahora sabemos y no queríamos saber

- **El modelo sin forzamiento no reproduce la trayectoria observada.** 4 de 5 predicciones pre-registradas fallan — pero las cuatro son la misma ausencia estructural, no cuatro fallos (`claude/DIAGNOSTICO_Y_ALTERNATIVAS.md` §1).
- **Con el término exógeno añadido, sí la reproduce** (Experimento 4) — pero **mucho menos de lo que se creyó hasta el 17/09/2026**. Con la población corregida la mejora sobre la traslación pura baja de 37,5 % a **12,9 %**, la predicción de dispersión pasa a fallar, y una contracción uniforme **sin red** iguala al mejor mecanismo: la influencia social por la red **no aporta nada medible**, donde antes se le atribuía 2,8 %. Ver `claude/REEJECUCION_DI-M1.md`.
- **Ningún mecanismo produce la joroba de dispersión** de la serie 2013-2023, y no por calibración sino por estructura: con parámetros constantes estas familias tienen signo fijo de variación de dispersión (Experimento 6, 0 de 594 corridas). Ahí Friedkin-Johnsen queda **último, peor que no hacer nada**.
- **Parte de lo que parecía influencia social era el modelo reparando un artefacto nuestro.** El desempate determinista del hot-deck apelmazaba la opinión sintética; los modelos que suavizan cobraban por arreglarlo. El deterioro al corregirlo crece monótonamente con φ (sección 33).
- **Y el resto de lo que parecía influencia social era difuminado.** Con ocho transiciones los mecanismos por fin le ganan al baseline (8,8 %), pero **ruido gaussiano sin red, con un parámetro, les gana a ellos** (Experimento 7). Lo que faltaba no era un mecanismo — y, según se vio unas horas después, tampoco era un tercer término: era una **forma funcional**.
- **Con el forzamiento correcto, dos números exógenos por periodo llegan al piso de ruido muestral.** El ladeo categórico da 0,97× el piso en la ECP y ~1,5× en la EPC, contra 3,15× y 6,15× del afín. **No queda residuo que un mecanismo social pueda explicar.** Es la conclusión más fuerte del proyecto y la que menos margen deja.
- **Con el doble de transiciones, el veredicto no cambia — y eso es lo que faltaba saber.** La duda razonable sobre los Experimentos 3 a 6 era si "ningún mecanismo gana" significaba "no hay mecanismo" o "no hay poder". Ocho transiciones, dos objetivos y dos constructos distintos dan el mismo resultado.
- **El perfil temporal de la contracción sigue sin reproducirse**, y la heterogeneidad de φ no lo arregla — predicho y confirmado.
- **DeGroot es peor que el ruido.**
- **Nada observable estructura la opinión individual en Bogotá**: demografía ~3 %, territorio ~1 % (y la mitad de eso es ruido muestral), ningún atributo estable replica entre olas. Lo único que predice opinión es otra opinión (10–25 %).
- La homofilia real existe y es fuerte, pero es **de opinión** (39,5 %), no territorial (12,4 %) ni demográfica.

## Lo que todavía NO sabemos

- ~~Si alguna familia de modelo endógeno disponible puede reproducir estos datos (A18)~~ — **respondido el 17/09/2026 por el Experimento 7, y es que no.** Con ocho transiciones y dos objetivos, cognición motivada es la mejor y la única consistente entre objetivos, y aun así pierde contra un parámetro de ruido sin red. Ya no es falta de poder: es el doble de puntos que todo lo anterior.
- **Por qué la distribución es tanto más difusa que lo que produce una afín.** El ancho de difuminado que gana (σ ≈ 0,2-0,3) es un parámetro exógeno sin interpretación: no sabemos si representa heterogeneidad de respuesta, cambio individual no correlacionado, o error de medición. Es la pregunta abierta que deja el Experimento 7.
- **Cuál es el constructo del proyecto** (A20, nueva): confianza institucional tiene cuatro transiciones; evaluación de gestión tiene ocho. En los años comparables se mueven en direcciones opuestas.
- Método de calibración del término exógeno (A10).
- Método de población sintética definitivo (A05) y arquitectura definitiva (A14) como decisiones formales.
- Tamaño definitivo de la población (A08).
- ~~Qué explica el rebote de 2023~~ — resuelto: es opinión, no no-respuesta (sección 33). Lo que sigue sin saberse es **qué mecanismo produce una contracción que no empieza hasta el tercer periodo**.
- Primer escenario concreto. Es lo que queda por construir, y ahora es lo principal.

---

# 44. PRÓXIMA ACCIÓN

**Nota histórica:** la acción original de esta sección (estado del arte) se completó — ver RESEARCH.md. La de la v0.6 (implementar `src/opinion/`, `src/model/`, `src/experiments/`) también. Se conservan las anteriores sin eliminarlas, según la regla de la sección 45.

## Próxima acción vigente (18 de septiembre de 2026) — reemplaza todas las anteriores

**El proyecto se reorienta hacia lo visual.** No cambia el objetivo ni se tira nada de lo hecho: cambia el orden. Primero Bogotá se ve, después los agentes se mueven encima. Ver sección 51 y `VISUALIZATION_SPECIFICATION.md`.

**Hecho el 18/09/2026:** hito 1 de la capa visual — geometría oficial de Catastro Distrital, paquete de datos reproducible, página autocontenida con tres capas e inspector por localidad, 12 pruebas. `src/viz/`, `data/external/geo/`, `data/processed/viz/`.

**En este orden:**

- **(i) Hito 2 — el tiempo.** Poner la serie de la EPC y de la ECP sobre el mapa y sobre una línea de tiempo. Sigue sin haber simulación, y no cuesta modelo nuevo: los datos ya están cargados y validados.
- **(ii) Hito 3 — geografía por debajo de la localidad, por UPZ.** Es lo que levanta DI-V3, el defecto visible del hito 1: hoy los puntos se reparten uniformemente dentro de cada localidad, lo que pone gente en el área rural de Ciudad Bolívar y Usme. Hay geometría pública y hay proyecciones de población por UPZ ya descargadas. **La manzana no** — es identificador de conglomerado, no coordenada, y toca R10.
- **(iii) A08 — escalar la población.** Ahora tiene un motivo que se ve: a 1.000 agentes el mapa no puede distinguir ninguna localidad de otra.
- **(iv) Saldar A05** — el índice de confianza de la ECP promedia un número variable de ítems. Es el último defecto conocido de la tubería de población, y no se vuelve menos importante porque ahora estemos dibujando.

**Lo que NO hay que hacer:** dibujar opinión simulada por localidad con escala estirada, en ninguna página, en ninguna presentación. Ver sección 31, RV-1 de `VISUALIZATION_SPECIFICATION.md` §2, y el propio conmutador de la página, que existe para enseñar el error, no para usarlo.

*(Se conservan abajo las acciones anteriores, sin editar.)*

## Próxima acción vigente (16 de septiembre de 2026)

Con los Experimentos 1, 2 y 3 corridos y la evidencia consolidada, hay tres frentes y **no son igual de urgentes**:

**1. ~~Verificar la confidencialidad de `data/raw/cnc/`~~ — hecho el 16/09/2026.** La carpeta salió del repositorio, la ruta salió del código (`--cnc` / `BSS_CNC_DIR`, DI-N7) y el equipo no tiene carpetas de sincronización en el directorio de usuario. Ver sección 32 y R10. Queda como vigilancia permanente, no como tarea.

**2. ~~Confirmar o rechazar D15~~ — aprobada el 16/09/2026.** El barrido de \(\bar{k}\) ya está en \(\{4,5,8\}\) en `experimento3.py` y en los dos YAML, y el Experimento 3 se re-corrió para comprobar que el veredicto no dependía del rango anterior. Queda suelto de aquel paquete un solo ajuste, que es de A17 y no de D15: **excluir los códigos 8/9 de estrato de la distancia homofílica**.

**2.bis — hecho el 16/09/2026.** Ejecutados los pasos 1 y 2 de `claude/DIAGNOSTICO_Y_ALTERNATIVAS.md` §6: término exógeno y φ heterogéneo implementados (`src/opinion/forzamiento.py`), Experimento 4 pre-registrado y corrido. Ver `claude/EXPERIMENT_4_RESULTS.md`.

**Lo que sigue, en este orden:**

- **(i) ~~Analizar la no-respuesta de 2023~~ — hecho el 16/09/2026, y descartada como explicación.** Ver sección 33 y `claude/ANALISIS_NORESPUESTA_2023.md`. El fenómeno es real, así que el objetivo del Experimento 4 también lo es.
- **(ii) ~~Implementar cognición motivada~~ — hecho el 16/09/2026 (A18).** Probada con pre-registro; no mejora. Con eso **se agota la vía endógena con los datos actuales**: tres familias, nivel controlado, criterios fijados de antemano.
- **(iii) Ampliar la serie con la ECP 2008–2015**, verificando comparabilidad ítem por ítem. **Sube a prioridad uno del lado de los datos:** de 3 transiciones a 7. Es lo único que cambiaría el poder de estas comparaciones, y el cargador ya existe.
- **(iv) Pedir en el CNC cualquier serie con pregunta repetida** y solicitar el microdato de Bogotá Cómo Vamos.

## Próxima acción vigente (17 de septiembre de 2026, noche) — reemplaza todas las anteriores

**La Fase 8 tiene su especificación completa y no queda nada que la bloquee.**

**Un escenario se declara con dos números por periodo: nivel y dispersión.** La tercera perilla se disolvió — ver la actualización de la sección 25. El forzamiento es el **ladeo categórico** (`src/opinion/forzamiento_categorico.py`, 16 pruebas), que sirve igual para ítems de 5 categorías, para índices de 154 valores y para la diferencia individual de 9.

**En este orden:**

- **(i) Fase 8 — el motor de escenarios.** Sobre dos perillas, con el ladeo como forzamiento, la red reportada como sensibilidad y **nunca** como mecanismo. Requisito de diseño que salió del módulo nuevo: el motor tiene que **rechazar escenarios imposibles** — en una escala acotada no todo par (media, sd) existe, y `rango_de_sd()` da los límites. Un laboratorio tiene que poder decir "esa combinación no existe en esta escala" en vez de devolver algo.
- **(ii) Confirmar A06, A11 y A20 como D0X.** A11 ya tiene su conjunto definitivo; A06 cambia de recomendación (el ladeo, no `traslación+u+γ+ruido`).
- **(iii) Responder a Bogotá Cómo Vamos** — el correo está redactado, con la inversión de códigos y la petición de la manzana.
- **(iv) Saldar A05**: el índice de confianza de la ECP promedia un número variable de ítems (de 1 a 8 actores, indistinguibles entre sí). Es el último defecto conocido del pipeline de población.

**Lo que NO hay que hacer:** re-correr los Experimentos 3 a 7 con el forzamiento nuevo. Sus comparaciones siguen siendo válidas porque el defecto era común a todos los modelos, y re-correrlos solo produciría números más bajos con el mismo veredicto. El esfuerzo va al motor.

*(Se conserva abajo la acción de la tarde del 17/09, sin editar.)*

## Próxima acción de la tarde del 17 de septiembre de 2026 *(superada)*

**El Experimento 7 cerró la pregunta que bloqueaba la Fase 8.** Con ocho transiciones y dos objetivos no hay mecanismo social identificable, y ya no por falta de poder. El motor de escenarios **se desbloquea**, y además sale de aquí con su especificación:

**Tres perillas exógenas por periodo — nivel, dispersión y difusión.** Es la primera vez que las tres aparecen desde **dos fuentes independientes**: `claude/ANALISIS_RESIDUO.md` §4 llegó a "tres perillas, no dos" desde la ECP por descomposición de la forma, y el Experimento 7 llega a lo mismo desde la EPC por un control de ruido. Que dos caminos distintos den tres es lo más cerca que ha estado el proyecto de un resultado asentado.

**En este orden:**

- **(i) Comprobar si la tercera perilla es una sola.** `ANALISIS_RESIDUO.md` la describe como forma derivada del nivel (PC1, r = −0,886); el Experimento 7 la describe como un ancho de difuminado σ ≈ 0,2-0,3. Puede que sean la misma vista de dos maneras, y saberlo cambia el diseño del motor. Es barato: se prueba sobre las series que ya están cargadas.
- **(ii) Fase 8 — escenarios**, sobre las tres perillas, con la red reportada como sensibilidad y **nunca** como mecanismo. Ver sección 17.
- **(iii) Responder a Bogotá Cómo Vamos** con la inversión de códigos de sus ítems de imagen.
- **(iv) ~~Adoptar estimación con diseño complejo (A19)~~ — hecho el 17/09/2026.** Queda pendiente pedir las variables de diseño a DANE y a BCV.
- **(v) Confirmar A06 y A11 como D0X** con lo que el Experimento 7 dejó, y decidir A20.

*(Se conserva abajo la acción de la mañana del 17/09, sin editar.)*

## Próxima acción de la mañana del 17 de septiembre de 2026 *(superada)*

**Lo hecho desde la última actualización**, en orden:

1. **Experimento 6** corrido y pre-registrado: con la serie de la ECP extendida a 2013 la dispersión hace una joroba, ningún mecanismo la produce (0 de 594) y el baseline de dos escalares exógenos gana. Las cinco predicciones se cumplieron. Ver `claude/EXPERIMENT_6_RESULTS.md` y `claude/ANALISIS_RESIDUO.md`.
2. **La EPC de Bogotá Cómo Vamos entró al proyecto** (sección 12.4): nueve olas anuales, cargador con 17 pruebas, inversión de códigos detectada y bloqueada, análisis de no respuesta hecho.
3. **El Experimento 7 quedó pre-registrado** (`claude/EXPERIMENT_7_SPECIFICATION.md`), con dos objetivos: la serie cruda y la diferencia individual `GG3ᵢ − CC5ᵢ`.
4. **Su control T6 falló y detuvo el experimento**, destapando DI-M1 (sección 33). Arreglado, con regresor.
5. **Los Experimentos 4, 5 y 6 se re-corrieron** con el pipeline corregido (`claude/REEJECUCION_DI-M1.md`). El 4 pierde dos tercios de su titular, el 5 cambia tres predicciones de signo a favor de cognición motivada, el 6 no se mueve.

**Lo que sigue, en este orden:**

- **(i) Correr el Experimento 7.** Es lo único que resuelve si cognición motivada es un mecanismo o un ajuste: gana con tres transiciones y pierde con cuatro; hay ocho disponibles. Falta escribir `src/experiments/experimento7.py` y construir la población base 2014 — ya hecha y verificada contra T6 (\(W_1 = 0{,}0528\), 0,91× el piso).
- **(ii) Decidir A20** — el constructo. No lo deciden los datos.
- **(iii) Responder a Bogotá Cómo Vamos** con la inversión de códigos de sus ítems de imagen. Es un hallazgo que le sirve a ellos y a cualquiera que use ese empaquetado.
- **(iv) Adoptar estimación con diseño complejo (A19)**, que sigue pendiente y sigue siendo barato.

**Lo que NO conviene hacer todavía:** arrancar la Fase 8. La recomendación de la v0.11 —construir el motor de escenarios porque la vía endógena estaba agotada— **se apoyaba en un resultado que la re-ejecución revocó**. No está agotada; está sin medir. Construir el motor sobre "no hay mecanismo" cuando eso volvió a estar en duda sería fijar en el diseño una conclusión que puede caerse en una semana.

*(Se conserva abajo la acción de la v0.11, sin editar.)*

**3. Fase 8 — escenarios. Ahora sí, y sin la reserva con la que la retiré en el diagnóstico.** Entonces "no hay modelo generativo identificable" venía de probar un solo modelo incapaz por estructura; hoy viene de tres familias, con el nivel controlado y con criterios pre-registrados. El motor de escenarios se construye sobre lo que sí funciona —**forzamiento exógeno explícito + encogimiento**— con la red reportada como sensibilidad, no como mecanismo.

*(Se conserva abajo la bifurcación tal como estaba planteada antes del Experimento 5.)*

**Bifurcación anterior, ya resuelta a favor de (a):**

- **(a) Fase 8 — escenarios.** Es a donde apunta la evidencia: si el movimiento real es exógeno y por periodo (sección 14), el escenario es el mecanismo principal, no una capa de presentación. Convierte el resultado negativo del Experimento 3 en el diseño del producto.
- **(b) A18 — evaluar confianza limitada.** Cierra la pregunta "¿probamos todas las familias razonables?" antes de concluir que ninguna funciona. Pero su predicción característica —fragmentación— es justamente la que los datos contradicen, así que la expectativa de éxito es baja.

Recomendación: **(a) primero, (b) como validación de cierre.**

**En paralelo, y baratos:** adoptar estimación con diseño complejo (A19); analizar quién dejó de responder en 2023 (sección 33) — sin eso, el único resultado favorable del Experimento 3 queda en el aire; sacar `Claude Setup.exe` de `data/processed/` e instalar `pyarrow`.

---

# 45. REGLA DE ACTUALIZACIÓN DE ESTE DOCUMENTO

Este archivo debe considerarse la **fuente de verdad del estado del proyecto**.

Cada vez que tomemos una decisión importante:

1. Registrar la decisión.
2. Asignarle un identificador.
3. Indicar su justificación.
4. Registrar evidencia.
5. Registrar fecha.
6. Indicar qué decisiones futuras afecta.

No eliminar decisiones anteriores.

Si una decisión cambia, conservar el historial:

```text
D11 v1 → propuesta
D11 v2 → modificación
D11 v3 → decisión final
```

**Corolario añadido en la v0.7:** lo mismo vale para las **expectativas fallidas**. Cuando una decisión envejece mal —como D12 frente a la medición de \(\eta^2\)— se anota la advertencia dentro de la decisión y no se reescribe la justificación original. Y cuando un experimento falla contra lo pre-registrado, se reporta contra el pre-registro, no contra lo que resultó. Es lo que hace que este documento sirva como evidencia y no solo como narración.

---

# 46. REGLA FUNDAMENTAL DEL PROYECTO

El proyecto debe responder siempre a la siguiente secuencia:

> **¿Qué datos tenemos?**

↓

> **¿Qué fenómeno podemos representar con esos datos?**

↓

> **¿Qué modelo representa mejor ese fenómeno?**

↓

> **¿Cómo podemos validarlo?**

↓

> **¿Qué escenarios podemos explorar?**

No invertir esta lógica.

El problema y los datos deben guiar la tecnología.

**Aplicación literal, Septiembre 2026.** Esta secuencia se siguió y produjo una respuesta incómoda en el segundo paso: con los datos disponibles **no podemos representar la dinámica individual de opinión**, porque nada observable la estructura. Lo que sí podemos representar es la **población** y la **distribución**, y explorar escenarios sobre supuestos explícitos. Seguir adelante como si el segundo paso hubiera salido bien sería exactamente la inversión de lógica que esta sección prohíbe.

---

# 47. VISIÓN FINAL

La visión a largo plazo es construir una plataforma que permita al CNC explorar escenarios sociales de Bogotá mediante una población sintética dinámica.

```text
                   BOGOTÁ REAL
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
       CNC            DANE       DATOS BOGOTÁ
        │              │              │
        └──────────────┼──────────────┘
                       ↓
               POBLACIÓN SINTÉTICA
                       ↓
                   AGENTES
                       ↓
                DINÁMICA SOCIAL
                       ↓
                  ESCENARIOS
                       ↓
               MÚLTIPLES RUNS
                       ↓
                  RESULTADOS
                       ↓
                VALIDACIÓN
                       ↓
                  DASHBOARD
```

La visión final NO debe interpretarse como:

> "una máquina que sabe qué va a pasar".

Debe entenderse como:

> **un laboratorio computacional que permite explorar cómo diferentes supuestos podrían producir diferentes resultados sociales.**

---

# 48. DEFINICIÓN CORTA DEL PROYECTO

> **Bogotá Social Simulator es un entorno de simulación basada en agentes que utiliza una población sintética de Bogotá, construida a partir de datos reales, para explorar escenarios de evolución de la opinión pública y evaluar sus resultados frente a evidencia observada.**

---

# 49. PALABRAS CLAVE

```text
Agent-Based Modeling
ABM
Synthetic Population
Opinion Dynamics
Computational Social Science
Social Simulation
Urban Simulation
Scenario Simulation
Public Opinion
Social Digital Twin
Synthetic Agents
Statistical Calibration
Backtesting
Uncertainty
Bogotá
CNC
DANE
Datos Abiertos Bogotá
```

---

# 50. ESTADO DE ESTE DOCUMENTO

**Versión:** 0.18  
**Estado:** En evolución activa — Fases 0 a 8 completadas; **Fase 10 (visualización) reordenada al frente y empezada**: hito 1 construido y publicado  
**Última actualización:** 16 de septiembre de 2026 — se cerró **A02** con la recepción de los cuatro estudios del CNC (sin panel, sin confianza institucional); se propuso **D15** para cerrar A07 sobre evidencia de tres fuentes independientes; se incorporó el veredicto del **Experimento 3** a las secciones 6, 14, 20, 22, 23, 25, 37 y 43, y a A06/A11; se adoptó la **revisión 2025** del marginal territorial dentro de D14; se abrieron **A18** (confianza limitada) y **A19** (estimación con diseño complejo); se añadió **R10** (confidencialidad de los datos del CNC) y el régimen de la sección 32; y se anotó en **D12** que sus variables explican ~3 % de la varianza de opinión.  
**Actualización 0.7.1 (16/09/2026):** los microdatos del CNC salieron del repositorio y su ruta salió del código; secciones 12.1, 32, 41 (R10) y 44 actualizadas en consecuencia.  
**Actualización 0.8 (16/09/2026):** **D15 aprobada** — A07 queda cerrada. Aplicado en código el barrido \(\bar{k} \in \{4,5,8\}\) y re-corrido el Experimento 3 para verificarlo. Corregida la Fase 5: `src/model/` no existe y no debe existir todavía (DI-E1); A14 recoge la desviación.  
**Actualización 0.9 (16/09/2026):** **Experimento 4** — con forzamiento exógeno el modelo sí ajusta (37,5 % sobre el mejor baseline), pero un control sin red consigue el 97 % de esa mejora: la influencia social aporta 2,8 %. A06 y A11 actualizadas; A11 gana un baseline mucho más exigente. Ver `claude/EXPERIMENT_4_SPECIFICATION.md` y `claude/EXPERIMENT_4_RESULTS.md`.  
**Actualización 0.10 (16/09/2026):** el salto de no-respuesta de 2023 queda **descartado** como explicación del rebote y de la contracción, con cuatro pruebas convergentes (sección 33). El fenómeno que el modelo no reproduce es real.  
**Actualización 0.11 (16/09/2026):** **Experimento 5** — cognición motivada implementada y probada; pierde contra Friedkin-Johnsen y contra un encogimiento sin red, pese a barrer cinco parámetros contra uno. **A18 cerrada.** Con las tres familias probadas, la vía endógena queda agotada con los datos actuales, y la Fase 8 (escenarios) pasa a ser el camino, sin la reserva del diagnóstico. Ver `claude/EXPERIMENT_5_RESULTS.md`.  
**Actualización 0.16 (17/09/2026):** **Fase 8 construida.** `src/scenarios/` —especificación declarativa en YAML, motor con incertidumbre en tres fuentes separadas, informe HTML autocontenido—, 13 pruebas, dos escenarios de ejemplo y `claude/SCENARIO_SPECIFICATION.md`. El criterio de éxito "Utilidad" pasa de sin evaluar a construido-sin-evaluar: lo que falta ahora no es código, es que alguien del CNC lo use. Se dejaron fuera a propósito la base de datos, la API y el frontend de `ARCHITECTURE.md`.  
**Actualización 0.15 (17/09/2026):** **El forzamiento era la forma funcional equivocada.** Todo el proyecto venía aplicando una transformación **afín** a variables que no viven en un continuo (5 categorías en la EPC, 154 valores en el índice de la ECP). Con un **ladeo exponencial sobre el soporte propio de la variable** —dos parámetros para dos momentos, exactamente la misma información— el ajuste pasa de 3,15× a **0,97× el piso de ruido en la ECP** y de 6,15× a 1,57× en la EPC. **Queda revocada la tercera perilla**: la forma no se declara ni se deriva del nivel, sale sola (notas de revocación en `claude/ANALISIS_RESIDUO.md` y `claude/ANALISIS_TERCERA_PERILLA.md`). El conjunto mínimo de baselines se rehace con el ladeo como el exigente (A11), A06 cambia de recomendación, y la conclusión sobre el ABM llega a su forma más fuerte: **si dos números exógenos alcanzan el piso de ruido, no queda residuo que un mecanismo social pueda explicar.** La Fase 8 queda sin bloqueos. Ver `claude/FORZAMIENTO_CATEGORICO.md`.  
**Actualización 0.14 (17/09/2026):** **A19 resuelta.** Estimación con diseño implementada aparte de la librería del CNC (DI-D1..DI-D5), con la limitación de que la ECP **no publica variables de diseño** y solo admite un DEFF prestado. DEFF medido en la EPC: 1,39-2,69, mediana 1,95. Resultado sustantivo: **siete de ocho transiciones son distinguibles de cero**, y la que no —2022→2023— es la misma que el análisis de no respuesta había marcado, por un camino independiente. Ver `claude/ANALISIS_DISENO_MUESTRAL.md`.  
**Actualización 0.13 (17/09/2026):** **Experimento 7** — ocho transiciones en vez de cuatro, dos objetivos (la serie cruda de gestión y la diferencia individual `GG3ᵢ − CC5ᵢ`), 1.224 corridas. **Cuatro de seis predicciones fallaron.** Los mecanismos le ganaron al baseline duro por 8,8 % en los dos objetivos —habría sido el primer resultado a favor del ABM— y **un control post-hoc de ruido gaussiano sin red les ganó a todos**. La ventaja era difuminado, no influencia social. **A18 se cierra** (cognición motivada es la mejor y la única consistente entre objetivos, y aun así pierde contra un parámetro de ruido), **A06 y A11 quedan listas para D0X** con un baseline nuevo —`traslación+u+γ+ruido`— y la **Fase 8 se desbloquea** con tres perillas confirmadas desde dos fuentes independientes. Ver `claude/EXPERIMENT_7_RESULTS.md`.  
**Actualización 0.12 (17/09/2026):** cuatro cosas. **(a)** Entró la **EPC de Bogotá Cómo Vamos** (sección 12.4): nueve olas anuales de evaluación institucional, más del doble de transiciones que la ECP, con una inversión de códigos detectada y bloqueada en el cargador. **(b)** Se incorporó por fin el **Experimento 6** a este documento (sección 25). **(c)** Se encontró y corrigió **DI-M1**, el desempate determinista del hot-deck (sección 33), que estaba inflando el desempeño de todos los modelos de influencia social; lo detectó un control pre-registrado, no una revisión. **(d)** Se **re-corrieron los Experimentos 4, 5 y 6**: el titular del 4 baja de 37,5 % a 12,9 %, **A18 se reabre** a favor de cognición motivada, el 6 no se mueve. Se abre **A20** (cuál es el constructo). La Fase 8 **se retira de la próxima acción** hasta que el Experimento 7 resuelva si hay mecanismo. Ver `claude/ANALISIS_EPC_BCV.md`, `claude/REEJECUCION_DI-M1.md` y `claude/EXPERIMENT_7_SPECIFICATION.md`.  
**Actualización 0.18 (18/09/2026):** **reorientación hacia la capa visual** (sección 51 y `VISUALIZATION_SPECIFICATION.md`). El proyecto pasa a construirse desde la superficie: primero Bogotá se ve, después los agentes se mueven encima. La Fase 10 se reordena al frente y su hito 1 queda construido —geometría oficial de Catastro Distrital, 1.000 agentes sobre el mapa, composición por localidad, bandas de ruido con efecto de diseño, 12 pruebas—. De construirlo salió una medición nueva y más fuerte que la advertencia de la sección 31: **con 1.000 agentes el 100 % de la dispersión de opinión entre localidades es ruido muestral**, lo que convierte a A08 (escalar la población) en una tarea con motivo visible. Queda escrita **RV-1**, que gobierna toda capa territorial de opinión del proyecto. No se tocó ningún resultado ni ningún método anterior.  
**Próxima actualización:** cuando el hito 2 (el tiempo sobre el mapa) esté construido, o cuando alguien del CNC haya usado el motor con un escenario propio.

**Principio:** Este documento debe evolucionar junto con el proyecto y registrar las decisiones reales, no solamente las ideas iniciales — incluidas las que no salieron.

---

# 51. CAPA VISUAL

**Fecha de apertura:** 18 de septiembre de 2026. **Documento:** `VISUALIZATION_SPECIFICATION.md`.

## 51.1 Qué cambió

El CNC pidió reorientar el proyecto hacia lo **visual e interactivo**, y aprovechar el perfil del equipo (ingeniería multimedia). El orden pasa a ser: **primero Bogotá se ve, después los agentes se mueven encima.** La precisión predictiva deja de ser el frente prioritario — que es coherente con lo que siete experimentos pre-registrados vienen diciendo: este sistema no es un predictor y nunca prometió serlo.

Lo que **no** cambia: los datos, los métodos y los resultados. La capa visual se construye sobre la tubería validada. Nada de lo que se dibuja se inventa para que se vea mejor.

Lo que sí hay que decir en voz alta: durante un tiempo el proyecto va a **mostrar más de lo que concluye**. Eso está bien mientras cada página diga exactamente qué es cada cosa.

## 51.2 Hito 1 — construido

Mapa interactivo de las 20 localidades (geometría oficial de Catastro Distrital), con tres capas —población real, los 1.000 agentes sintéticos punto a punto, y opinión— e inspector por localidad con composición demográfica, error estándar corregido por efecto de diseño y banda de ruido.

Archivos: `src/viz/preparar_mapa.py`, `src/viz/plantilla_mapa.html`, `src/viz/construir_pagina.py`, `data/external/geo/localidades_bogota.geojson`, `data/processed/viz/`, `tests/test_viz_mapa.py` (12 pruebas).

Decisiones DI-V1 a DI-V7 en el docstring de `preparar_mapa.py` y en §3.3 de la especificación.

## 51.3 El hallazgo que salió de construirlo

Al calcular las bandas de la página apareció una medición que no estaba: **con 1.000 agentes, el 100 % de la dispersión de opinión entre localidades es ruido muestral.** Desviación observada entre las 20 medias: 0,156. Desviación esperada solo por ruido, con el efecto de diseño medido en la EPC: 0,183. Residuo real: 0,00.

Es más fuerte que la advertencia de la sección 31 —que decía "no existen o son del tamaño del ruido"— y que el 54-63 % medido en los dos estudios del CNC, porque aquí no queda nada. También es una consecuencia directa del tamaño de la población, no una propiedad de Bogotá: es el argumento visible para A08.

## 51.4 Regla que gobierna toda página del proyecto

> **RV-1.** Ninguna capa de opinión por territorio se dibuja sin su margen de ruido al lado, y ninguna escala de color se estira al rango observado por defecto.

La página del hito 1 la cumple de una forma deliberada: trae **las dos** escalas y deja al usuario producir el gráfico engañoso a propósito, con el texto que explica qué acaba de hacer. Enseñar el error es más eficaz que esconderlo.
