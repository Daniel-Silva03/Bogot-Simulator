# Diagnóstico: qué está fallando, por qué, y qué alternativas hay

Proyecto: Bogotá Social Simulator
Versión: 1.0
Fecha: 16 de septiembre de 2026
Origen: pedido explícito de revisar los fallos y buscar alternativas —incluidas fuentes de datos nuevas— antes de seguir avanzando
Documentos que revisa: `claude/EXPERIMENT_3_RESULTS.md`, `claude/ANALISIS_HOMOFILIA.md`, `MODEL_SPECIFICATION.md`, `PROJECT_CONTEXT.md`

---

## 0. La conclusión primero

Hay **ocho fallos**. Al separarlos por causa aparece algo que no se veía cuando se miraban juntos:

| # | Fallo | Causa | ¿Se arregla con…? |
|---|---|---|---|
| 1 | El modelo no mueve el nivel (P1) | **Estructural del modelo** | Modelo |
| 2 | Perfil de dispersión equivocado (P2) | **Estructural del modelo** | Modelo |
| 3 | Sin no-monotonía (P3) | **Estructural del modelo** | Modelo |
| 4 | Sin comportamiento de colas (P4) | **Estructural del modelo** | Modelo |
| 5 | Nada observable estructura la opinión (η² ≈ 3 %) | **Conjunto de variables incompleto** | Datos |
| 6 | Solo 4 puntos en el tiempo, cada 2 años | **Poder estadístico** | Datos |
| 7 | Sin panel → influencia y selección son indistinguibles | **Diseño de las fuentes** | Datos |
| 8 | El modelo con mejor evidencia nunca se implementó | **Omisión nuestra** | Trabajo pendiente |

Y dos correcciones incómodas a lo que este proyecto venía afirmando:

> **Los fallos 1 a 4 son un solo fallo.** Los cuatro se derivan de que Friedkin-Johnsen no tiene ningún término exógeno variable en el tiempo. Un sistema cerrado que promedia no puede producir un movimiento de nivel, ni una V, ni un vaciado de cola. Decir "el modelo falló 4 de 5 predicciones" es contar cuatro veces la misma ausencia.

> **Nunca probamos el modelo que nuestro propio documento señaló como el bueno.** `MODEL_SPECIFICATION.md` §4 designó el marco de cognición motivada (Lorenz et al. 2021 / Gestefeld & Lorenz 2023) como **modelo objetivo de la fase de calibración**, por ser el único de los cinco evaluados con calibración publicada contra distribuciones reales de confianza institucional (ESS, mediana R² > 0,8) *y* contra transiciones individuales de panel (Swiss Household Panel). Implementamos Friedkin-Johnsen y DeGroot. La afirmación "ninguna familia endógena reproduce estos datos" no está respaldada: se probó una familia, y estructuralmente no podía.

Esto **no borra** el resultado de los baselines —FJ φ=0,3 apenas le gana a congelar, y un escalar por año explica el doble que todo el ABM— pero sí cambia qué se concluye de él. Lo medido es: *un modelo sin forzamiento no reproduce una dinámica forzada*. Eso está muy cerca de una tautología, y es distinto de *el ABM no sirve aquí*.

---

## 1. Los fallos del modelo (1–4): una sola causa

Friedkin-Johnsen es

$$a(t+1) = \Phi W a(t) + (I - \Phi)\, a(0), \qquad a^* = (I - \Phi W)^{-1}(I - \Phi)\, a(0)$$

Todo lo que aparece del lado derecho existía en \(t = 0\). El punto fijo es una combinación convexa de las opiniones iniciales, así que:

- **La media apenas puede moverse** (fallo 1). El movimiento máximo simulado fue 0,029 con \(\bar{k} \in \{4,8,16\}\) y 0,040 con \(\{4,5,8\}\), contra 0,258 observados. No es que esté mal calibrado: no hay de dónde salga el movimiento.
- **La trayectoria es monótona hacia el punto fijo** (fallos 3 y 4). Una V exige que el forzamiento cambie de signo. Sin forzamiento no hay signo que cambiar. 0 de 720 corridas, en las dos ejecuciones — y seguirá siendo 0 en todas.
- **La contracción es geométrica y por tanto anticipada** (fallo 2). Lo observado se contrae tarde (−3,3 % / −0,7 % / −14,8 %). Ningún valor de \(\phi\) convierte una curva que decelera en una que acelera.

**Qué hacer, en orden de costo:**

**(a) Añadir un término exógeno por periodo.** Es la corrección mínima y va directo al diagnóstico:

$$a(t+1) = \Phi W a(t) + (I - \Phi)\, a(0) + u(t)\,\mathbf{1}$$

con \(u(t)\) un escalar por periodo. Sabemos de antemano que va a funcionar para el nivel, porque el diagnóstico del Experimento 3 ya lo midió por separado: un escalar por año reduce el error de nivel un 32 %, contra 16 % de FJ solo, y 45 % los dos juntos. Lo que **no** sabemos, y es la pregunta interesante, es si con el nivel resuelto el mecanismo social aporta algo en la **forma** de la distribución —que es lo único que no puede dar un escalar. Un día de trabajo, y convierte el Experimento 3 en una prueba que el modelo puede pasar o fallar por razones informativas.

**(b) Heterogeneidad en \(\phi\).** Hoy \(\phi\) es un escalar. Con \(\phi_i\) variable —gente más y menos tozuda— la contracción deja de ser una exponencial limpia y puede llegar tarde. Ataca el fallo 2, que es el único que (a) no resuelve. Ya está previsto en la ecuación original de `MODEL_SPECIFICATION.md`, que escribe \(\phi_i\) con subíndice; la implementación lo aplanó.

**(c) Implementar cognición motivada (fallo 8).** Ver §4.

---

## 2. El fallo 5: "nada observable estructura la opinión"

Esta es la conclusión más consecuente que ha producido el proyecto — cerró A07, reencuadró D12 y puso en duda el aporte del ABM. Merece que se la someta a la misma exigencia que le pusimos al modelo.

**Lo que está sólido:** se midió sobre la ECP directamente, no sobre agentes sintéticos, así que el hot-deck no es el culpable. Se replicó en dos olas. Y coincide con la evidencia territorial del CNC, que es una fuente independiente.

**Lo que no está sólido — y es serio:** la ECP **no pregunta autoubicación ideológica ni identificación partidista**. Son, en la literatura comparada, los dos predictores más fuertes de confianza institucional. Concluimos "ningún atributo observable estructura la opinión" a partir de un conjunto de variables que excluye justamente los dos mejores candidatos. La conclusión honesta hasta aquí es más estrecha:

> *Ningún atributo **sociodemográfico** estructura la confianza institucional en Bogotá.*

Que es un hallazgo real y útil, pero no el que escribimos.

**Segunda reserva, menor:** η² está atenuado por error de medición en el índice (PC1 explica 35 %, no 80 %). Corregir por atenuación subiría las cifras, aunque no de 3 % a 30 %.

**Cómo se falsea:** LAPOP/Barómetro de las Américas trae escala ideológica (L1) y batería de confianza institucional para Colombia, en muchas olas. Si la ideología explica 20–30 % de la varianza de confianza donde la demografía explica 3 %, la conclusión de `ANALISIS_HOMOFILIA.md` §2 hay que reescribirla, y la homofilia del simulador tendría una base observable después de todo. Si no la explica, la conclusión sale reforzada por una vía independiente. **Las dos respuestas sirven**, que es la definición de una buena prueba.

---

## 3. Los fallos 6 y 7: el problema más profundo, y el que menos habíamos mirado

Estamos ajustando una trayectoria a **3 transiciones** (2017→2019→2021→2023). Con tres transiciones:

- Cualquier modelo con 3 o más parámetros libres puede ajustarlas.
- La comparación entre modelos casi no tiene poder.
- El rango de 0,015 entre nueve configuraciones de red contra 0,0045 de ruido entre semillas se leyó como *"la red no importa"*. La lectura correcta y más modesta es **"este diseño no puede detectar si importa"**.

Y sin panel, ninguna cantidad de cortes transversales distingue **influencia** de **selección** — la advertencia que `PROJECT_CONTEXT.md` §34 ya registra como el supuesto más fuerte del proyecto. La gente comparte opiniones con su círculo; los datos que tenemos no pueden decir si el círculo la convenció o si eligió el círculo.

Esto no se arregla con mejor modelado. Se arregla con más puntos en el tiempo, o con panel. Ver §5.

---

## 4. El fallo 8: el modelo que no construimos

`MODEL_SPECIFICATION.md` §2 y §4, escrito **antes** de cualquier experimento, dice del marco de cognición motivada:

- Es el **único de los cinco** con evidencia directa de calibración exitosa contra datos de encuesta reales.
- Gestefeld & Lorenz (2023) lo ajustaron a **1.235 distribuciones de confianza institucional** de la European Social Survey, con mediana R² > 0,8, y a transiciones individuales del Swiss Household Panel.
- Recomendación literal: *"candidato objetivo para la Fase 4 (calibración)"*.

Su núcleo es

$$\Delta a_i = \frac{\lambda^k}{\lambda^k + |a_j - a_i|^k}\,\alpha\,(a_j - \rho\,a_i)$$

más reversión idiosincrática con probabilidad \(\theta\). Tres cosas que FJ no tiene y que corresponden exactamente a los fallos 2, 3 y 4: influencia que **decae suavemente** con la distancia de opinión (no de golpe como Hegselmann-Krause, no uniforme como FJ), un **anclaje con reversión estocástica** que permite trayectorias no monótonas, y parámetros que controlan la **forma** de la distribución y no solo su varianza.

No es una promesa de que vaya a funcionar. Es que decir "probamos lo razonable" sin haberlo implementado no es cierto, y era nuestro propio documento el que lo señalaba.

**Nota sobre A18.** Estaba planteada como "¿evaluamos Hegselmann-Krause / Deffuant?", y argumenté en contra porque su predicción característica —fragmentación— es justo la que los datos contradicen. Ese argumento sigue en pie para HK/Deffuant puros. **No aplica a cognición motivada**, que es una generalización con decaimiento suave y que fue calibrada precisamente contra distribuciones no fragmentadas. A18 estaba mal formulada: el candidato correcto no era HK.

---

## 5. Fuentes de datos — qué hay, verificado

### 5.1 Olas anteriores de la ECP — lo más barato que existe

La ECP no empieza en 2017. Verificado en los catálogos:

| Año | Catálogo | Bogotá como dominio propio | Batería de confianza institucional |
|---|---|---|---|
| 2008 | DANE 104 | — | sí (Democracia), **códigos distintos** (`E35A_EPP`…) |
| 2011 | IHSN 5289 | — | sí (Democracia) |
| 2013 | IHSN 5299 | **sí**, 280 segmentos | sí (Democracia) |
| 2015 | DANE 406 | **sí**, 280 segmentos | sí, capítulo I (28 preguntas) |
| 2017 / 2019 / 2021 / 2023 | 515 / 644 / 730 / 822 | sí | sí, `P5263S1`…`S15` — **ya cargadas** |

Potencialmente **de 4 puntos a 8**, con `src/population/ecp.py` ya escrito y probado, y con el mismo mecanismo de resolución de módulos por nombre normalizado que ya resolvió las variaciones entre 2017 y 2023.

**El riesgo, y hay que tomarlo en serio:** 2008 usa nombres de variable distintos (`E35A_EPP`), lo que confirma que el instrumento cambió en algún punto. Antes de apilar olas hay que verificar, **ítem por ítem**, que la pregunta, la lista de instituciones y la escala sean las mismas. Si no lo son y las apilamos igual, fabricamos una tendencia que es un cambio de cuestionario. Sería exactamente el error que este proyecto lleva tres documentos intentando no cometer. Si solo un subconjunto de instituciones es comparable, se usa ese subconjunto y se dice.

**Costo:** descarga + un día de verificación de comparabilidad. **Es lo primero que haría.**

### 5.2 ELCA / ELCO — el panel que no sabíamos que estaba ahí

Encuesta Longitudinal Colombiana (Uniandes) y su continuación ELCO, **en el mismo catálogo de DANE del que ya descargamos todo**:

| Ola | Catálogo |
|---|---|
| ELCA 2010 | 816 |
| ELCA 2013 | 817 |
| ELCA 2016 | 818 |
| ELCO 2019 | 814 |
| ELCO 2022 | 902 |

- **Es panel de verdad**: sigue a los mismos hogares y personas en el tiempo, con atrición documentada (19.685 hogares en 2019 → 16.336 en 2022; 59.992 personas).
- **Bogotá es estrato geográfico identificable** por separado.
- Tiene **Capítulo Q** (participación en grupos, organizaciones y movimientos) y **Capítulo R — "Política"**: cultura política, fuentes de información, y actitudes frente a situaciones personales y comunitarias.

**Lo que hay que verificar antes de ilusionarse:** si el Capítulo R trae un ítem de actitud **repetido entre olas** y utilizable como variable de opinión. Si lo trae, esto es lo único en todo el inventario que permite distinguir influencia de selección (fallo 7) y estimar transiciones individuales — que es el estándar contra el que Gestefeld & Lorenz validaron su modelo. Si no lo trae, sigue sirviendo para el capítulo de redes y participación.

**Costo:** descarga gratuita + revisión del DDI. Alto potencial, riesgo medio.

### 5.3 LAPOP / Barómetro de las Américas — para falsear el fallo 5

Datos crudos públicos y gratuitos (hay además un nivel de suscripción para archivos fusionados y soporte). Colombia tiene olas desde 2004. Trae **escala ideológica** y batería de confianza institucional.

**Limitación que hay que anticipar:** la muestra colombiana es nacional, del orden de 1.500 casos; el submuestreo de Bogotá quedaría en un par de cientos. **No sirve para dinámica bogotana.** Sirve exactamente para una cosa, y es la prueba de §2: ¿la ideología y el partidismo explican la confianza institucional donde la demografía no? Para esa pregunta la muestra nacional alcanza.

**Costo:** bajo. **Alto valor por ser una prueba de falsación de nuestra conclusión más consecuente.**

### 5.4 Bogotá Cómo Vamos — la serie larga

Encuesta de Percepción Ciudadana, **corriendo desde 1998**, anual, sobre Bogotá. `MODEL_SPECIFICATION.md` ya la identificaba como la fuente que haría viable calibrar cognición motivada. Publican informes; el microdato no está publicado abierto y la página metodológica no detalla tamaño de muestra ni representatividad por localidad.

**Acción:** solicitud formal, cuanto antes, porque el tiempo de respuesta es el costo real. No bloquea nada mientras llega.

### 5.5 Lo que puedes conseguir adentro del CNC

A02 se cerró con cuatro cortes transversales de temas distintos. Pero el CNC hace medición de opinión de forma continua. **Lo que falta es exactamente una pregunta repetida en el tiempo**, y es lo que un instituto de opinión tiene por definición.

Vale la pena pedir explícitamente, con este criterio: *cualquier estudio donde la misma pregunta de opinión se haya hecho en dos o más momentos, con muestra de Bogotá.* Aunque sean agregados publicados y no microdato, una serie de 20 puntos trimestrales vale más para calibrar dinámica que cuatro puntos bienales con microdato.

Es, de toda esta lista, la fuente con mejor relación entre lo que aportaría y lo que cuesta conseguirla — y la única que depende de una conversación y no de una descarga.

### 5.6 Descartadas o de baja prioridad

- **Invamer / Gallup Colombia** — frecuencia mensual, que sería ideal, pero publicación en PDF y acceso al microdato comercial.
- **Latinobarómetro** — anual desde 1995, pero muestra nacional pequeña; mismo límite que LAPOP y con menos variables útiles.
- **Hegselmann-Krause / Deffuant puros** — ver §4: su predicción característica está contradicha por los datos.

---

## 6. Orden recomendado

Sin prisa, y ordenado por evidencia obtenida sobre trabajo invertido.

**Primero — arreglar lo que es nuestro, no de los datos (una semana)**

1. **Término exógeno en FJ + \(\phi_i\) heterogéneo**, y re-correr el Experimento 3. Convierte una prueba que el modelo no podía pasar en una que sí. Hasta hacerlo, el veredicto del Experimento 3 dice menos de lo que parece.
2. **Implementar cognición motivada** (Lorenz/Gestefeld). Es lo que nuestro propio `MODEL_SPECIFICATION.md` mandaba y no se hizo.

**Segundo — multiplicar los puntos en el tiempo (una a dos semanas)**

3. **ECP 2015, 2013, 2011, 2008**, con verificación de comparabilidad ítem por ítem antes de apilar nada.
4. **Pedir en el CNC cualquier serie con pregunta repetida** sobre Bogotá.
5. **Solicitar el microdato de Bogotá Cómo Vamos** — ponerlo a correr ya, porque la demora es el costo.

**Tercero — atacar la identificación (según lo que revele el DDI)**

6. **ELCO/ELCA**: verificar el Capítulo R. Si hay ítem de actitud repetido, es la pieza que falta.
7. **LAPOP**: probar ideología y partidismo contra confianza. Falsa o refuerza el fallo 5.

**Lo que NO haría todavía:** Fase 8 (escenarios). Es lo que recomendé antes de este diagnóstico, y lo retiro por ahora. Construir el motor de escenarios sobre la conclusión "no hay modelo generativo identificable" sería construir sobre una conclusión que se sacó probando un solo modelo, incapaz por estructura, contra tres transiciones. Los escenarios siguen siendo el destino probable; solo que todavía no está demostrado que sean el único.

---

## 7. Qué cambia en los documentos si esto se acepta

- `claude/EXPERIMENT_3_RESULTS.md` — añadir que los fallos P1, P3 y P4 son consecuencia estructural de la ausencia de forzamiento, no evidencia independiente. **No reescribir el pre-registro.**
- `claude/ANALISIS_HOMOFILIA.md` §2 y §8 — acotar la conclusión a "ningún atributo **sociodemográfico**", y registrar la prueba pendiente con LAPOP.
- `PROJECT_CONTEXT.md` — A06 sigue abierta con más razón que antes; **A18 reformulada** (el candidato es cognición motivada, no Hegselmann-Krause); A12 sin cerrar; §43 matizar "no hay modelo generativo identificable".
- `claude/DATA_INVENTORY.md` — entran §5.1 a §5.5 como fuentes candidatas con su estado real de verificación.
- `MODEL_SPECIFICATION.md` — registrar que su recomendación de Fase 4 quedó sin ejecutar, y con qué prioridad se retoma.

---

*Este documento existe porque se pidió revisar los fallos antes de seguir avanzando. Dos de sus hallazgos corrigen afirmaciones que yo mismo escribí en documentos anteriores de este proyecto: que el modelo había fallado cuatro predicciones independientes, y que ningún atributo observable estructura la opinión. Quedan anotados como corrección y no reescritos en silencio, por la misma regla de la sección 45 de `PROJECT_CONTEXT.md`.*

## Fuentes

- [Colombia — ECP 2015, catálogo DANE 406](https://microdatos.dane.gov.co/index.php/catalog/406/study-description)
- [Colombia — ECP 2013, IHSN 5299](https://catalog.ihsn.org/index.php/catalog/5299)
- [Colombia — ECP 2011, IHSN 5289](https://catalog.ihsn.org/index.php/catalog/5289)
- [Colombia — ECP 2008, variable E35A_EPP, catálogo DANE 104](https://microdatos.dane.gov.co/catalog/104/variable/V661)
- [DANE — Información histórica de la Encuesta de Cultura Política](https://www.dane.gov.co/index.php/estadisticas-por-tema/cultura/cultura-politica/informacion-historica-encuesta-de-cultura-politica)
- [Colombia — ELCO 2022, catálogo DANE 902](https://microdatos.dane.gov.co/index.php/catalog/902)
- [Colombia — ELCA 2016, catálogo DANE 818](https://microdatos.dane.gov.co/index.php/catalog/818)
- [Colombia — ELCA 2013 / 2010, catálogos DANE 817 y 816](https://microdatos.dane.gov.co/index.php/catalog/817)
- [LAPOP — acceso libre a datos](https://www.vanderbilt.edu/lapop/free-access.php)
- [LAPOP — Colombia](https://www.vanderbilt.edu/lapop/colombia.php)
- [Bogotá Cómo Vamos — Encuesta de Percepción Ciudadana](https://bogotacomovamos.org/encuestas-de-percepcion-ciudadana/)
