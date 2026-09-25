# POPULATION SPECIFICATION — Nota metodológica: fusión estadística

Proyecto: Bogotá Social Simulator
Documento: Extiende DATA_SPECIFICATION.md (Fase 2 del roadmap — Población sintética)
Versión: 0.5 — **8.4 cerrada con el donante ECP (A05)**: el umbral de 7 ítems se midió en vez de heredarse, y el denominador del índice quedó registrado por fila y publicado en la página
Versión 0.4 — **8.3 cerrada (DI-M1)**: el desempate determinista era el defecto más caro del pipeline, y se midió. Entra el donante EPC (§9)
Versión 0.3 — Método implementado, probado y auditado (A05 sigue abierta formalmente)
Fecha: 23 de septiembre de 2026

---

## 1. El problema, en una frase

Ninguna fuente identificada trae, en el mismo registro, **demografía completa** (edad, sexo, localidad, estrato, educación) **y** **opinión/percepción** (seguridad, confianza, satisfacción). El "Agente #18452" del prompt maestro —con las dos cosas a la vez— no existe todavía en ningún dataset: hay que construirlo combinando al menos dos fuentes que **nunca entrevistaron a las mismas personas**.

Esto no es un detalle técnico menor: es la primera decisión metodológica que condiciona todo lo que sigue (A05).

## 2. Cómo se llama este problema y qué dice la literatura

Se conoce como **statistical matching** o **data fusion**: integrar dos muestras que comparten variables comunes ("variables puente") pero no comparten las variables de interés, sin haber entrevistado a las mismas unidades. Es una práctica establecida en estadística oficial (paquete `StatMatch` de R, usado en institutos de estadística europeos) y en investigación de opinión (Pew Research construye así su "población sintética" para calibrar paneles online).

### Métodos candidatos

**A. Hot-deck / nearest-neighbour matching**
Por cada persona de la fuente "receptora" (ej. Encuesta Multipropósito), buscar la persona más parecida en la fuente "donante" (ej. Bogotá Cómo Vamos) según las variables comunes (edad, sexo, localidad, estrato, educación) y copiarle la variable de opinión.
- Ventaja: simple, no paramétrico, es el estándar en estadística oficial.
- Limitación central: **asume independencia condicional** — que, dadas las variables comunes, la variable de opinión no depende de nada más que no esté en ambas encuestas. Esta asunción casi nunca es verificable con los datos disponibles.

**B. Imputación por regresión / mass imputation**
Modelar la variable de opinión como función de las variables comunes en la fuente donante, y usar ese modelo para predecirla en la fuente receptora.
- Ventaja: permite introducir ruido/incertidumbre explícita en la imputación (variabilidad real del proyecto, no solo copiar un valor).
- Limitación: la calidad depende de qué tan bien las variables comunes predicen la opinión — si predicen poco, se imputa esencialmentre la media, aplanando la variabilidad real de opinión.

**C. Synthetic reconstruction / Iterative Proportional Fitting (IPF)**
No fusiona variables distintas; ajusta una tabla multivariada a marginales conocidas (ej. cuadrar edad×sexo×localidad a las proyecciones DANE-SDP). Es complementario a A o B, no sustituto: sirve para la fase de validación de la población (sección 22 del prompt maestro), no para pegar la opinión.

**D. Bayesian bootstrap combinando encuestas (Dong et al., 2014)**
Genera poblaciones sintéticas a partir de cada encuesta por separado y combina las estimaciones ponderando por precisión. Pensado para estimar cantidades agregadas, no para producir un archivo de microdatos fusionado agente-por-agente.
- Uso más natural aquí: para la **validación macro** (comparar distribuciones agregadas), no para construir el agente individual.

**E. Modelos generativos profundos (GANs) para síntesis conjunta multi-fuente**
Literatura reciente (2026) explora fusión con modelos generativos que preservan diversidad y factibilidad conjunta mejor que los métodos estadísticos clásicos.
- Descartado para el MVP: exactamente el tipo de "complejidad prematura" que el Principio 5 del proyecto pide evitar. Se anota como línea experimental de Fase 7, no de Fase 2.

## 3. Recomendación provisional (no definitiva — A05 sigue abierta)

Para el prototipo inicial (1.000 agentes, sección 30 de PROJECT_CONTEXT.md):

1. Usar la **Encuesta Multipropósito** como fuente receptora / esqueleto demográfico (trae edad, sexo, localidad, UPZ, estrato, educación, situación laboral).
2. Usar **Bogotá Cómo Vamos** (serie larga, para calibración temporal futura — Fase 6) y/o la **Encuesta de Confianza Institucional** (Veeduría Distrital, ver DATA_SPECIFICATION.md) como fuente(s) donante(s) de opinión. **Actualización (Septiembre 2026):** la implementación real del prototipo usó la Encuesta de Confianza Institucional como donante — es la que llega a nivel de localidad, resolviendo la limitación que este documento señalaba en la sección 4 sobre BCV. Ver sección 7 para el detalle completo de la implementación.
3. Aplicar **hot-deck nearest-neighbour** (método A) sobre variables puente comunes a ambas fuentes — es el método más simple, más transparente y más fácil de auditar para un primer prototipo, coherente con el Principio 5 (evitar complejidad prematura) y con el Principio 3 (separar dato observado de supuesto: aquí el supuesto de independencia condicional debe quedar explícito y documentado, no oculto).
4. Documentar explícitamente la asunción de independencia condicional como **supuesto del modelo**, no como hecho — y priorizar, en la validación (Fase 8), comprobar si esta asunción distorsiona los resultados de forma importante.

## 4. Variables puente a confirmar

Para que el matching funcione, ambas fuentes deben compartir variables con **la misma definición operacional**. Pendiente de verificar en los diccionarios de datos completos (no confirmado todavía en este audit):
- ¿Bogotá Cómo Vamos captura localidad de residencia, o solo estrato/edad/zona?
- ¿La definición de estrato y grupos de edad es comparable entre Multipropósito y BCV?
- Si BCV no llega a nivel de localidad, el matching tendrá que hacerse a nivel de ciudad o estrato, no de localidad — lo cual limitaría la resolución territorial de la variable de opinión aunque la resolución demográfica sea más fina.

**Respondidas el 17/09/2026, con la entrega completa de BCV — y las tres respuestas importan:** BCV **sí** captura localidad (19 códigos, sin Sumapaz), **no** trae nivel educativo del informante, y su edad viene en **cinco bandas**, no en años. Ver §9.

## 5. Por qué esto no depende de que el CNC responda

Este análisis y esta recomendación se pueden avanzar y hasta prototipar con Multipropósito + Bogotá Cómo Vamos, que ya están confirmados como accesibles. Cuando el CNC responda las preguntas de la sección 6 de DATA_SPECIFICATION.md, su fuente se evalúa como **donante alternativo o adicional** dentro del mismo marco metodológico — no cambia el método, solo la fuente.

## 6. Próximo paso

Con esta nota más DATA_SPECIFICATION.md, ya hay base suficiente para avanzar en paralelo a ETAPA 4 (selección formal del modelo de opinión, comparando DeGroot / Friedkin-Johnsen / Bounded Confidence–Hegselmann-Krause / Deffuant contra los criterios de RESEARCH.md), que tampoco depende de datos del CNC.

## 7. Implementación real (Septiembre 2026)

El método A (hot-deck nearest-neighbour) se implementó como código (`src/population/loader.py`, `matching.py`, `build_agents.py` — ver ARCHITECTURE.md) y se corrió de punta a punta con datos reales. Esto refinó el método más allá de lo que decía la sección 3, en formas que quedan documentadas aquí:

### 7.1 Variables puente — nombres reales confirmados

| Variable D12 | Fuente | Nombre real de la columna | Nota |
|---|---|---|---|
| localidad | Multipropósito 2021 | `NOMBRE_LOCALIDAD` | — |
| sexo | Multipropósito 2021 | `SEXO` | Imputado, 1=Hombre/2=Mujer |
| edad | Multipropósito 2021 | `NPCEP4` | Años cumplidos, continua |
| estrato | Multipropósito 2021 | `NVCBP11AA` ("Estrato para tarifa") | **Corrección real**: se intentó primero con `ESTRATO2021`, que resultó ser un código interno de unidad de muestreo (valores de 8 dígitos), no el estrato socioeconómico. Detectado por un chequeo de rango, corregido antes de usar en producción. |
| nivel_educativo | Multipropósito 2021 | `NPCHP4` (15 categorías) | Recodificada a la escala 0-5 de D12/NETWORK_SPECIFICATION.md |

### 7.2 Refinamiento del método: emparejamiento exacto + distancia (no solo "nearest-neighbour" genérico)

La sección 3 no especificaba cómo tratar cada variable puente dentro del hot-deck. La implementación real decidió:
- **Emparejamiento exacto (bloques):** `localidad` y `sexo` — no tiene sentido metodológico asignar opinión de otra localidad o sexo cuando esa información está disponible en ambas fuentes.
- **Distancia euclidiana estandarizada:** `edad`, `estrato`, `nivel_educativo`, dentro de cada bloque exacto.
- **Escalera de relajación documentada:** si un bloque localidad×sexo no tiene donantes, se relaja primero sexo, luego localidad, con el nivel de relajación usado registrado por cada agente (nunca oculto).

Esto es una decisión de implementación, no una decisión D0X formal — debe revisarse antes de considerarse definitiva.

### 7.3 Vacío real encontrado: el donante no trae estrato

La Encuesta de Confianza Institucional (Veeduría Distrital) — el donante usado en la práctica por su resolución de localidad — **no trae estrato** (ver DATA_SPECIFICATION.md). La corrida real del prototipo excluyó `estrato` de las variables de distancia para este donante específico, como decisión explícita tomada y registrada en el metadata de cada corrida (`poblacion_sintetica_metadata.json`), no como solución de fondo. **Pregunta abierta nueva (A15, ver PROJECT_CONTEXT.md):** ¿se homologa `ingresos` (que sí trae este donante) como proxy de estrato, se consigue un donante alternativo que sí lo traiga, o se acepta la exclusión de forma permanente?

### 7.4 Resultado de la corrida real (prototipo, N=1.000)

- Receptor completo: 168.200 personas adultas de Bogotá (Multipropósito 2021, tras filtrar nulos de sexo/edad/estrato/educación).
- Donante: 4.458 personas (Confianza Institucional, tras homologar sexo a F/M y descartar género no binario — limitación real, no cosmética).
- Muestra del prototipo: 1.000 agentes, muestreo **aleatorio simple** con semilla fija (42) — **no está decidido si debería ser estratificado por localidad**, proporcional a la población real (como se hizo para el marginal de ponderación en DATA_SPECIFICATION.md). Nueva pregunta abierta (A16, ver PROJECT_CONTEXT.md).
- Resultado: 100% de los 1.000 agentes emparejados en nivel 0 (coincidencia exacta localidad+sexo) — el donante, pese a sus limitaciones, tiene cobertura suficiente en las 20 localidades para que esto funcione bien en la muestra probada.

## 8. Revisión de código y correcciones (15 de septiembre de 2026)

Se auditaron los tres módulos línea por línea y se verificó el resultado contra el archivo real ya producido. El pipeline funciona y la población generada es válida, pero aparecieron dos defectos de implementación que ya están **corregidos**, y varios hallazgos metodológicos que siguen **abiertos**.

### 8.1 Corregido — el emparejamiento usaba etiquetas de índice donde debía usar posiciones

`hot_deck_match` construía las claves de bloque con `receptor.iloc[pendientes][vars]`, conservando el índice de etiquetas del DataFrame, y luego las usaba como posiciones de fila. Funcionaba solo porque `load_multiproposito_receptor` termina con `reset_index(drop=True)`.

Con un receptor de índice no trivial — lo que produce cualquier `.sample(1000)` sin resetear, que es exactamente el paso siguiente natural del pipeline — el resultado era, en el mejor caso, un `IndexError`; y en el peor, **opiniones asignadas a la persona equivocada, violando el bloque exacto localidad+sexo, mientras `resumen_relajacion` seguía reportando 100% en nivel 0**. Es decir, la garantía central del método se rompía sin dejar rastro en el metadata.

Corregido reescribiendo el bucle para trabajar exclusivamente con posiciones (`.to_numpy()` descarta el índice) y normalizando el índice a la entrada. Verificado de dos formas: un test de regresión que corre el mismo caso con cuatro índices distintos (normal, permutado, fuera de rango, etiquetas de texto) y exige el mismo resultado correcto en los cuatro; y una comparación directa de la implementación vieja contra la nueva sobre el receptor real de 168.200 personas, que da resultados **idénticos** en opinión asignada, donante elegido y nivel de relajación — o sea, la corrección no altera la corrida ya producida.

### 8.2 Corregido — `exact_match_vars` se validaba pero no se usaba

El parámetro existía y su docstring invocaba explícitamente la regla de la sección 25 del prompt maestro ("no hardcodear"), pero el bucle iteraba sobre una constante `NIVELES_RELAJACION` fija. Pasar `exact_match_vars=["sexo"]` no cambiaba nada: el emparejamiento seguía priorizando localidad.

Corregido con `construir_escalera_relajacion(exact_match_vars)`, que deriva la escalera soltando la última variable primero. Con el default D12 `["localidad", "sexo"]` reproduce exactamente la escalera que estaba escrita a mano, así que el comportamiento por defecto no cambia. **Consecuencia:** el orden en que se pasan las variables de bloque ahora es significativo — van de la que más importa conservar a la que menos.

Como la escalera ya no es fija, `MatchingResult` guarda la escalera realmente usada y `guardar_poblacion_sintetica` la escribe en el metadata: sin eso, `resumen_relajacion_hotdeck` sería ilegible a futuro, porque "nivel 1" no significaría lo mismo entre corridas.

### 8.3 CERRADO el 17/09/2026 (DI-M1) — y era el defecto más caro del pipeline

**El diagnóstico de la v0.3 era correcto y su estimación del daño se quedaba corta.** Decía: `hot_deck_match` crea `rng = np.random.default_rng(random_state)` y **nunca lo usa**; los empates los rompe el orden de filas de sklearn; con `distance_vars = [edad, nivel_educativo]` el donante tiene ~30 puntos distintos por bloque, los empates son masivos y siempre gana el mismo donante. Medido entonces: 45 valores únicos de `opinion_t0` para 1.000 agentes, con los 5 más frecuentes concentrando el 46,4 %.

Quedó anotado como "decisión pendiente" durante tres iteraciones. **Lo que faltaba no era la decisión: era saber cuánto valía.**

#### Cómo se midió

Lo detectó el control **T6 pre-registrado** del Experimento 7 (`claude/EXPERIMENT_7_SPECIFICATION.md`), que exigía \(W_1(a_0, \text{obs}) < 2\times\) el piso de ruido antes de correr nada. Con el donante EPC —cuya edad viene en bandas, o sea aún más discreta— la población base dio **0,2172 contra un piso de 0,0580: 3,75 veces**. El experimento se detuvo.

#### El arreglo

Se consultan `k_empates` vecinos, se toman todos los que están a la distancia mínima (tolerancia 1e-9) y se sortea entre ellos **con probabilidad proporcional al factor de expansión del donante**.

Lo segundo importa tanto como lo primero, y no estaba en el diagnóstico original: el objetivo contra el que se compara es la distribución **ponderada** del donante, así que sortear uniformemente entre empatados habría introducido un sesgo propio. Sin empates, el resultado es idéntico al anterior.

| Población base | \(W_1\) antes | \(W_1\) después | piso de ruido |
|---|---|---|---|
| ECP 2013 | 0,0442 · 1,05× | **0,0205 · 0,49×** | 0,0422 |
| ECP 2017 | 0,0497 · 1,08× | **0,0303 · 0,65×** | 0,0462 |
| EPC 2014 | 0,2172 · 3,75× | **0,0528 · 0,91×** | 0,0580 |

Las tres quedan **por debajo del piso de ruido**: indistinguibles de una muestra fresca de lo observado.

#### Lo que costó, y esto es lo que hay que recordar

Los Experimentos 4, 5 y 6 se re-corrieron con las mismas mallas (`claude/REEJECUCION_DI-M1.md`). Con la población corregida:

- **Todas** las variantes de Friedkin-Johnsen y DeGroot **empeoran**, y el deterioro crece monótonamente con \(\phi\) — con cuánta influencia social aplica el modelo (FJ φ=0,1: +0,040; φ=0,3: +0,193; φ=0,9: +0,255).
- **Traslación y ruido**, los dos únicos modelos que no tocan la forma de la distribución, **mejoran** (−0,075 y −0,073).

La población vieja tenía la opinión apelmazada en pocos valores donados, con la dispersión inflada; los modelos de influencia suavizan y contraen. **Estaban cobrando crédito por reparar un artefacto de nuestro propio generador de población.** El titular del Experimento 4 bajó de 37,5 % a 12,9 % y una de sus predicciones pasó a fallar; tres predicciones del Experimento 5 cambiaron de signo.

**La lección de método, que vale más que el arreglo:** el defecto llevaba meses en el código y estaba documentado aquí mismo. No lo encontró una revisión — lo encontró **un control pre-registrado con umbral numérico**, aplicado a una fuente nueva que lo hacía imposible de ignorar. Un "abierto" en un documento no es una salvaguarda; un umbral que detiene la corrida, sí.

Implementación en `src/population/matching.py` (DI-M1). Regresor en `tests/test_population_matching.py`.

### 8.4 CERRADO con el donante ECP — el índice de confianza promedia un número variable de ítems

**El defecto original, y a qué donante pertenece.** `df[cols].apply(pd.to_numeric).mean(axis=1)` ignora los NaN sin umbral mínimo de respuesta. Verificando los denominadores implícitos en `opinion_t0` de la **población de la Veeduría**, aparecen valores de **1 a 8**: hay agentes cuyo "índice compuesto de confianza institucional" proviene de **un solo actor** evaluado, y es indistinguible del de alguien que evaluó los ocho. Eso explica buena parte de los 172 agentes con valor exactamente 3,000 y los 157 con exactamente 2,000. Ese diagnóstico sigue vigente **para ese donante**, y por eso el bloque `escala_opinion` de esa rama lo dice en el metadata en vez de callarlo.

**Con el donante ECP el umbral ya existía, pero nunca se había medido.** `ecp.py` exige `INDICE_MIN_ITEMS = 7` de 13 desde DI-C6. Lo que faltaba era saber si 7 es el número correcto, y dejar registrado el denominador de cada índice. Medido sobre la ECP 2013 en Bogotá (5.917 personas, 13 ítems utilizables):

| ítems respondidos | 0 | 1-6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|---|---|
| personas | 68 | 62 | 15 | 19 | 31 | 48 | 135 | 407 | **5.132** |

| umbral | conserva | media ponderada | sd |
|---|---|---|---|
| `min_items = 1` | 5.849 (98,9 %) | 2,8150 | 0,7632 |
| `min_items = 7` (actual) | 5.787 (97,8 %) | **2,8076** | 0,7557 |
| `min_items = 13` | 5.132 (86,7 %) | 2,8008 | 0,7637 |

**El umbral se queda en 7, ahora por medición y no por inercia.** Exigir los 13 mueve la media 0,007 puntos sobre una escala de 4 y cuesta el 11 % de la muestra donante — y ese 11 % no es aleatorio, es quien contesta menos, que es precisamente el perfil que no conviene borrar. La distribución está tan concentrada (86,7 % contesta las 13) que el denominador variable **no** es, con esta fuente, el problema que sí es con la Veeduría.

**Lo que sí faltaba, y es lo que se cerró:** registrar el denominador.

- `ecp.py` expone `n_items_confianza()` y emite la columna `n_items_confianza` en el donante (DI-C11), de modo que el número de ítems promediados viaja **con cada fila**, no como promedio de la corrida.
- `resumen_n_items()` resume esa distribución y `construir_poblacion.py` la pasa a `guardar_poblacion_sintetica(..., escala_opinion=...)`.
- El metadata de la población trae ahora un bloque `escala_opinion` con la pregunta, el rango, las anclas verbales (*1 = no confía, 5 = confía mucho*), la dirección, cómo se construye el índice, las 13 instituciones, la distribución de denominadores y una línea explícita de **lo que la escala no es** (no es un porcentaje: 3,0 es el punto medio, no "30 % de confianza").
- `donante_fuente` decía "13 ítems de P5263S\*" como si todos hubieran respondido los 13. Ahora dice *hasta* 13, con el mínimo exigido y el porcentaje que respondió todo.
- El mapa copia ese bloque tal cual al paquete de visualización (DI-V34) y la página lo publica: la escala 1-5 dejó de ser una columna de números sin etiqueta.

**Sigue abierto, acotado:** la rama de la Veeduría. El docstring de `loader.py` habla de 7 actores y `_FRAGMENTOS_ACTORES_CONFIANZA` lista 8 (DATA_SPECIFICATION.md dice 7 pero enumera 8 nombres) — inconsistencia a resolver contra el cuestionario real; y si un fragmento no encuentra su columna, la función solo emite un `warning` y continúa. Esa rama no tiene umbral ni columna de denominador, y su `escala_opinion` lo declara así en vez de fingir que sí. Ese donante ya no alimenta ningún experimento vigente, así que la deuda queda enunciada y priorizada por debajo, no disimulada.

### 8.5 Abierto — `opinion_t0` es independiente de estrato por construcción

Consecuencia directa de 7.3 que conviene dejar escrita antes de correr los experimentos, no después: `estrato` **está** en la tabla de agentes pero **no** intervino en asignar la opinión. La correlación medida es −0,06, y ese residuo viene únicamente del bloqueo por localidad.

Cualquier resultado del Experimento 2 que relacione estrato con opinión será por lo tanto un artefacto del método de construcción, no un hallazgo sobre Bogotá. Aplica en particular al generador de red homofílico, que pondera estrato en su distancia.

*Nota de la v0.4: con el donante EPC este vacío no aplica — la EPC sí trae estrato, y es una de las dos variables de distancia (§9). El vacío que aparece en su lugar es el de educación.*

### 8.6 CERRADO — códigos de no-respuesta tratados como estrato

`NVCBP11AA` trae valores 8 y 9, que en Multipropósito son códigos de no-respuesta, no estratos; 39 sobreviven al receptor final. `validar_agentes` los aceptaba explícitamente (rango 0–9), y en la distancia homofílica un agente con `estrato = 9` se trataba como más extremo que estrato 6.

**Resuelto en el origen (DI-P3):** `loader.py` descarta esos registros al construir el receptor —39 de 168.200, un 0,02 %— y el generador homofílico **rechaza con un mensaje explícito** cualquier población que los traiga, en vez de parchearlos. Las dos formas "obvias" de arreglarlo aguas abajo introducían un sesgo propio y opuesto: omitir la componente sobreconecta a los marcados (grado 10,1 contra 4,9) y imputar la media los aísla (0,6 contra 5,2). Detalle en `claude/ANALISIS_RESIDUO.md`, anexo.

### 8.7 CERRADO — el receptor entró sin ponderar

El extracto de Multipropósito no incluía factor de expansión, así que el sobre-muestreo de localidades pequeñas propio del diseño pasaba entero a la población sintética. **Resuelto en D14:** muestreo PPS sistemático proporcional a `FEX_C`. La distancia territorial al marginal bajó de 0,172 a 0,041, y a 0,032 contra el marginal revisado de 2025.

### 8.8 Lo que la revisión confirmó que está bien

El diseño de bloque exacto + distancia es correcto y superior a un nearest-neighbour genérico. La escalera de relajación con trazabilidad por fila es buena práctica. `validar_agentes` reporta todos los problemas de una vez en vez del primero. El manejo del mojibake y el crosswalk de localidades funciona contra el archivo real. Y la detección de que `ESTRATO2021` era un código de muestreo —documentada en el propio mensaje de error del loader— es exactamente el tipo de control que el Principio 3 pide. El matching resolvió 100% en nivel 0 sobre datos reales, lo cual es un buen resultado.

---

## 9. El donante EPC — Bogotá Cómo Vamos (17 de septiembre de 2026)

El Experimento 7 necesita una población base construida sobre la Encuesta de Percepción Ciudadana. Se agregó como tercer donante (`--donante epc:<año>[:<ítem>]`), y las tres diferencias respecto del donante ECP son reales y quedan como decisiones de implementación en `src/population/epc_bcv.py`:

**DI-B8 — no hay nivel educativo.** La EPC no lo pregunta al informante. La distancia queda en `edad_banda` + `estrato`, y se pierde una de las tres variables. Es una pérdida real pero acotada: las tres juntas explican ~3 % de la varianza de opinión (D12), así que quitar una de tres no puede costar mucho. Se documenta en vez de disimularse.

**DI-B9 — la edad viene en cinco bandas** (18-25, 26-35, 36-45, 46-55, 55+), no en años. El receptor, que sí trae años, se bandea con esos mismos cortes. Bandear pierde resolución dentro de banda; emparejar años del receptor contra códigos 1-5 del donante sería mucho peor, porque la distancia estandarizada mezclaría dos escalas distintas sin avisar.

**DI-B10 — `localidad` NO se usa, aunque la EPC la trae y la ECP no.** El mapa de códigos está verificado: los 19 del formulario reproducen el marginal territorial en 2024 con TVD 0,029 y r = 0,995. Pero en 2014 y 2019 los factores de expansión **no** reproducen ese marginal (TVD 0,178 y 0,170), con Suba y Engativá sub-representadas y las localidades pequeñas sobre-representadas. Usar localidad como variable de emparejamiento exacto importaría esa distorsión de diseño al decidir quién dona a quién, y el premio sería pequeño: la localidad explica ~1 % de la varianza de opinión, la mitad de eso ruido muestral (D15).

**Decidido antes de construir la población, no después de ver el ajuste.** Es la diferencia entre una decisión de diseño y un ajuste post-hoc, y con un control pre-registrado de por medio conviene que quede escrito de qué lado está.

### Resultado

Población `poblacion_epc2014.csv`: 1.000 agentes, 100 % emparejados en nivel 0 (sexo exacto), distancia territorial al marginal 0,045, y \(W_1(a_0, \text{obs}_{2014}) = 0{,}0528\) contra un piso de ruido de 0,0580 — **por debajo del piso**. T6 pasa.

---

*Estado de A05 (23 de septiembre de 2026): la parte medible quedó cerrada — §8.4. Lo que sigue abierto es la rama de la Veeduría, que ya no alimenta ningún experimento vigente.*

*Documento vivo — decisión final sobre el método de fusión (A05) se registra en PROJECT_CONTEXT.md con formato D0X cuando se confirme, siguiendo la convención establecida ahí (nota: la versión anterior de este documento decía "se registra en MODEL_SPECIFICATION.md", lo cual era inconsistente con la convención real del proyecto — corregido aquí).*
