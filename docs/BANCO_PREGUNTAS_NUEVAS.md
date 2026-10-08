# BANCO DE PREGUNTAS NUEVAS — INVENTARIO

**Preguntas de opinión que el simulador no tiene en su catálogo pero cuya respuesta real conocemos: el material para mejorar el puente y para probarlo.**

Proyecto: Bogotá Social Simulator
Versión: 0.1 — inventario (no es un pre-registro)
Fecha: 1 de octubre de 2026
Origen: `PREGUNTAS_REALES_NUEVAS_RESULTS.md` (el puente falló en dos preguntas reales) y el rumbo
acordado con Daniel el 1/10: que las preguntas nuevas se acerquen a resultados reales, usando la API
cuando ayude.

---

## 1. Para qué

El puente se validó con preguntas escondidas de la misma encuesta, y falló en las dos primeras
preguntas reales nuevas. Mejorarlo mirando esas dos sería ajustarlo a respuestas que ya vimos. Hace
falta un **banco grande**, separado en dos:

- **Práctica:** para probar mejoras al puente, todas las veces que haga falta.
- **Guardado:** nadie le hace estas preguntas al simulador hasta la prueba final pre-registrada.

## 2. Qué hace buena a una pregunta del banco

1. **Es de opinión o de aprobación**, no de conducta («¿usa la cicla?») ni de conocimiento.
2. **No está en el catálogo** de 102 preguntas del simulador.
3. **Tiene resultado de Bogotá**, idealmente por sexo, edad y estrato (lo que la página muestra), y
   mejor si también por localidad.
4. **Es independiente de la población:** que las personas que la respondieron no sean donantes del
   simulador (los encuestados de la EPC 2022, 2023 y 2024 lo son). Si comparten personas, al comparar
   por grupos aparece el ruido compartido de `PUENTE_LOCALIDADES_RESULTS.md` §4, aunque en grupos
   grandes es pequeño.
5. **No es electoral** (intención de voto, candidatos, partidos).

## 3. Las fuentes

| Fuente | Cuántas, aproximado | Grupos | Localidad | Independiente | Estado |
|---|---|---|---|---|---|
| **A. EPC de otros años, preguntas armonizadas que no están en el catálogo** | ~30: imagen de entidades distritales (CADE, Secretarías, TransMilenio, IDRD…, 2014-2024), confianza en las personas y en las instituciones (`MICC1-8`, 2024-2025), satisfacción con la salud (`SA4`), imagen del alcalde (`GG1`) | sexo, edad, estrato | sí | **sí en 2014-2019 y 2025**; no en 2022-2024 | en disco, con diccionario |
| **B. EPC de otros años, preguntas sueltas de coyuntura** | ~15: migración venezolana (2018, `COY10`), castigar por mano propia (2019 `JCV4`, 2022 `JCV4B`), quién debe cuidar en la vejez (2022, `VE3_*`), frases sobre la ciudad (2017 `PI*`, 2022 `VE2_*`), gestión de la alcaldía (2022-2023 `PC20_*`), 2016 `COY1` | sexo, edad, estrato | sí | 2016-2019 sí; 2022-2023 no | en disco; **las etiquetas vienen cortadas** a ~80 caracteres: hay que completar el texto con los formularios |
| **C. Encuesta de Cultura Política del DANE (ECP)** | módulos de democracia (172 variables), capital social (53) y participación (83) en 2023, más 2017-2021; probablemente decenas de preguntas de opinión. El módulo de elecciones y partidos queda fuera | sexo, edad; estrato por confirmar | **no** | **sí** (otra encuesta; 4.451 adultos de Bogotá en 2023) | microdato en disco; **los textos de las preguntas no vienen en los archivos**: hace falta el diccionario del DANE (descarga, con permiso) |
| **D. Biblioteca del CNC** (`DATA_INVENTORY.md` §15) | metro elevado y Corredor Verde (ya vistos), y 2-3 de opinión del 29/08/2023 | sexo, edad, estrato | sí (13-15) | sí (otra encuesta, en línea por SMS) | en disco |

**En total, del orden de 100 preguntas candidatas**, la mayoría independientes de la población. Es
suficiente para separar práctica y guardado con varias decenas en cada uno.

## 4. Hechos que pesan

- **Métodos distintos.** La EPC es cara a cara; la ECP también, pero con otro cuestionario y otra
  muestra; la del CNC es en línea por SMS. Una diferencia de nivel puede ser del método. Por eso la
  medida principal es **el orden de los grupos**, que la página muestra, más que el nivel.
- **Años distintos.** La población describe 2022-2024; la EPC de 2014-2019 y la ECP de 2017-2021
  describen otra Bogotá. Las preguntas de 2023 (ECP, CNC) son las más comparables.
- **El metro elevado y el Corredor Verde ya se vieron:** solo pueden ir a práctica.
- **Lo que aprendimos de esas dos:** «del mismo tema» no es «predice quién está de acuerdo». Un
  banco con preguntas de muchos temas permite ver en cuáles el puente funciona y en cuáles no.

## 5. Dónde ayuda la API (lo que pidió Daniel)

| Paso | Uso | Costo aproximado |
|---|---|---|
| Armar el banco | Clasificar cada candidata (¿opinión o conducta?, ¿electoral?) y escribirla como pregunta de la página. Una persona lo revisa | ~100 llamadas cortas, < USD 0,30 |
| Práctica | Probar variantes del puente: instruir al modelo a pensar en **quién se ve afectado** y **quién propone** el cambio; darle ejemplos de práctica con su resultado; varias repeticiones | unas cuantas centenas de llamadas, USD 1-3 |
| Prueba final | La mejor variante, una vez, sobre el banco guardado, pre-registrada | ~150 llamadas, < USD 1 |

La API ayuda a **elegir mejor las preguntas en que se apoya el puente**. La regla del Experimento 8
sigue en pie: el modelo nunca responde por las personas.

## 6. Qué falta para cerrarlo

1. **Permiso para descargar el diccionario de la ECP 2023 del DANE** (el XML/DDI del catálogo 822),
   para leer los textos de las preguntas.
2. Completar los textos cortados de la fuente B con los formularios de la EPC, si están en la carpeta
   de Bogotá Cómo Vamos.
3. Armar la lista definitiva con su clasificación (con la API, revisada por Daniel) y **sortear
   práctica y guardado con una semilla fija**, antes de hacerle ninguna al simulador. El sorteo se sube
   antes de seguir.

---

## 7. Avance (1/10)

- **Diccionario de la ECP 2023 descargado** con permiso de Daniel: `DANE-DIMPE-ECP-2023.xml` (982 KB,
  `microdatos.dane.gov.co/index.php/metadata/export/822/ddi`), en `data/raw/ecp/2023/` (no se sube).
  Confirma que la ECP trae estrato (`P4031S1A1`), sexo (`P220`) y edad (`P5785`).
- **`src/experiments/banco.py`** arma las candidatas solo con metadatos (DI-BA1 a DI-BA4):
  **336** (282 ECP, 29 EPC armonizada, 21 EPC de coyuntura, 4 de la biblioteca del CNC); **307
  independientes** de la población; 16 con el texto cortado. En `data/processed/banco/candidatas.csv`.
- La clasificación con la API (paso 2) está probada con un modelo simulado. Falta correrla.
- **Clasificación con la API (1/10, corrida de Daniel):** 329 llamadas, USD 0,091. Válidas 333 de 336;
  **útiles 171** (opinión, no electorales), 143 independientes. Las 3 inválidas son de la serie «a quién
  no quisiera tener de vecino» (`P2041`), que conserva 10 válidas.
- **Revisión de Daniel (1/10), tres reglas aprobadas** (DI-BA5): fuera 6 preguntas que el texto
  cortado dejó sin sentido; ámbito «Bogotá» o «general»; sorteo por familia, con lo no independiente
  y lo ya visto siempre en práctica.

## 8. El sorteo (1/10, semilla 20261001)

`data/processed/banco/sorteo.csv`, subido antes de hacerle ninguna pregunta del banco al simulador.

| | Bogotá | General (ECP) | Total |
|---|---|---|---|
| **Práctica** | 37 preguntas, 15 familias | 77 preguntas, 16 familias | 114 |
| **Guardado** | **5 preguntas, 5 familias** | 46 preguntas, 17 familias | 51 |

En práctica, 25 preguntas van por no ser independientes y 2 por ya vistas (metro, Corredor).

**Un límite que dejó el sorteo:** el guardado de Bogotá quedó con solo 5 preguntas (funcionamiento de
la ciudad, oportunidades, migración venezolana, servicio de salud, metro en 10 años), porque la familia
más grande de Bogotá (imagen de 7 entidades distritales, 2019) cayó en práctica. No se repite el sorteo:
elegir otro a conveniencia anularía su sentido. La prueba final dirá poco de Bogotá por sí sola; su
peso estará en el total y en el ámbito general.

**El guardado no se le pregunta al simulador hasta la prueba final pre-registrada.** Los experimentos
de práctica leen el banco solo con `banco.practica()`, que nunca devuelve una pregunta guardada.

## 9. Resultados reales de la práctica (1/10)

`src/experiments/banco_reales.py` → `data/processed/banco/reales_practica.json` (solo cifras
agregadas). Para cada pregunta de práctica: porcentaje ponderado «de acuerdo» en la ciudad y por sexo,
edad (18-25, 26-35, 36-45, 46-55, 56+, los tramos de la población), estrato (1, 2, 3, 4, 5-6) y, en la
EPC, localidad; las bases y los pares de grupos con diferencia clara. **El guardado no se calcula.**

**Regla de estructura (DI-BR5), puesta al ver la primera corrida:** fuera las preguntas con menos de
300 respuestas válidas o con un solo código válido en los datos. Sacó 18: la serie de vecinos
(`P2041`, casillas en las que solo queda quien marcó), «quién debe cuidarlo en la vejez» (`VE3_*`,
respuesta múltiple), la confianza en la Asamblea y la Gobernación (vacías en Bogotá) y una de
participación con base de 176. Es de estructura, no de resultado: se aplicará igual al guardado mirando
solo bases y códigos.

**Quedan 96 preguntas de práctica (32 de Bogotá), con 699 diferencias claras entre grupos** (mediana de
7 por pregunta; 5 sin ninguna). 32 traen localidad.

## 10. La práctica del puente (1/10)

`src/experiments/practica_puente.py` (DI-PP1 a DI-PP5). No es un pre-registro: compara versiones
del puente sobre las **91 preguntas de práctica** con al menos una diferencia clara (699 pares; 31 de
Bogotá con 226 pares, 60 generales con 473). Medida: fracción de diferencias claras bien ordenadas.

- **Versiones:** «actual» (el prompt de la página) y «afectados» (el mismo más un párrafo que pide
  pensar en a quién afecta, quién lo propone y qué valores lo sostienen; la lección del Corredor
  Verde).
- **Referencias sin API, ya calculadas:** el azar ordena bien el 50 % (p95: 55 %) y el **tono general
  el 62 %** (66 % en Bogotá). El tono supone que los grupos que en la encuesta suelen responder de forma
  favorable también lo harán aquí. **Es la vara:** un puente que no la supere no aporta.

### 10.1 Resultados de la práctica (1/10)

Corridas de Daniel; 580 llamadas en total, **USD 1,39** (las dos versiones). Fracción de las 699
diferencias claras entre grupos que cada método ordena bien:

| Método | Todas | Bogotá (226) | General (473) | r por localidad (31 preguntas de la EPC) |
|---|---|---|---|---|
| Azar (media / p95) | 0,50 / 0,55 | 0,50 / 0,58 | 0,51 / 0,56 | — |
| **Tono general** (sin API) | **0,62** | **0,66** | 0,60 | — |
| Puente «actual» | 0,61 | 0,62 | 0,62 | 0,20 |
| Puente «afectados» | 0,60 | 0,62 | 0,60 | 0,19 |
| Los 3 puentes juntos (cualquier versión) | 0,62 | | | |
| Los 3 puentes juntos + tono | 0,63 | | | |

**Lectura.** El puente le gana al azar, pero **no le gana al tono general**: en una pregunta nueva, el
orden de los grupos que da es, en la práctica, el de «quién suele responder de forma favorable». Pedirle
que piense en a quién afecta y quién propone no cambió nada (solo bajó los «sin base», de 32 a 5
llamadas). Por pregunta, el puente supera al tono en 29, empata en 28 y pierde en 34.

**Un análisis que no sirvió, anotado para no repetirlo:** «la mejor pregunta del catálogo para cada
pregunta nueva, mirando el resultado» acierta el 100 %. No es un techo: con 102 preguntas y dos sentidos,
siempre hay alguna que ordena bien unos 7 pares por azar. No dice si la información está en la población.

### 10.2 Último intento: perfiles y ejemplos resueltos (regla escrita el 1/10, antes de correr)

Daniel eligió el camino 1. **Versión «ejemplos»** (`src/experiments/practica_ejemplos.py`):

- **El perfil de cada pregunta del catálogo** se le muestra al modelo, calculado con la población
  (en qué estratos, edades y sexo es más favorable). Sin él, un ejemplo no le enseña nada: el modelo
  elige por tema porque no sabe qué preguntas separan a qué grupos.
- **Ejemplos resueltos de la práctica**: la pregunta, su perfil real ~~y un puente que la ordena bien~~.
  *Cambio (1/10, antes de correr nada real):* el «puente que ordena bien» de cada ejemplo salía de elegir
  las 2 preguntas del catálogo que más pares del ejemplo aciertan, y era ruido (para la confianza en el
  Congreso: «respeto por los reinsertados +, respeto por la diversidad sexual −»): con pocos pares,
  alguna pareja siempre acierta por azar. Enseñaría relaciones falsas. Los ejemplos quedan con la
  pregunta y su perfil real.
- **Validación cruzada por familia, 3 partes con semilla fija**: cada pregunta se evalúa con ejemplos
  sacados solo de las otras dos partes. Nunca ve su propio resultado ni el de sus hermanas.
- 91 preguntas × 3 llamadas, como las otras versiones; unos USD 0,6-0,9.

**Regla de salida, escrita antes de correr:** si la versión «ejemplos» no ordena bien **al menos el
67 %** de las 699 diferencias claras (el tono general más 5 puntos), **se para**: la página adopta el
camino 2 (mostrar el tono general por grupo como «así suelen responder estos grupos») y no se prueban
más versiones del puente para el orden de los grupos. Si lo supera, va al banco guardado, pre-registrado.

### 10.3 Resultado del último intento (1/10)

273 llamadas, USD 0,95 (la caché de la práctica suma 853 llamadas y **USD 2,33** en total). Validación
cruzada por familia:

| | Todas (699) | Bogotá (226) | General (473) | r por localidad |
|---|---|---|---|---|
| Azar (media / p95) | 0,50 / 0,55 | 0,50 / 0,58 | 0,51 / 0,56 | — |
| Tono general | 0,62 | 0,66 | 0,60 | — |
| Puente «actual» | 0,61 | 0,62 | 0,62 | 0,20 |
| Puente «afectados» | 0,60 | 0,62 | 0,60 | 0,19 |
| **Puente «ejemplos»** | **0,63** | 0,61 | 0,63 | 0,19 |

**Regla de salida (§10.2): 0,627 < 0,67 → se para.** Ver los perfiles del catálogo y ejemplos con su
resultado real subió el puente un punto o dos, al nivel del tono general, sin superarlo de verdad; en
Bogotá quedó por debajo. Por la regla escrita: **no se prueban más versiones del puente para el orden de
los grupos**, y la página adopta el camino 2: en una pregunta nueva muestra el tono general por grupo,
rotulado como «así suelen responder estos grupos en la encuesta».

**Lo que se aprendió, en una frase:** para una pregunta que la encuesta no hizo, el simulador no sabe
qué grupos estarían más de acuerdo mejor de lo que ya dice el patrón general de cada grupo; ninguna
forma de elegir preguntas del catálogo con el modelo de lenguaje lo mejoró. El banco guardado queda sin
usar, disponible para probar cualquier idea nueva de verdad, pre-registrada.

## 11. Segundo lote: Encuesta de Cultura Ambiental 2021 (pre-registro, 5/10, antes de sortear)

**Fuente.** Encuesta de Cultura Ambiental (ECA) 2021 de la Secretaría de Cultura, Recreación y Deporte
de Bogotá (datos abiertos, CC BY-SA 4.0), descargada con permiso de Daniel el 5/10 a
`data/raw/scrd/eca_2021_scrd.xlsx` (2,6 MB; no se sube).
- Muestreo probabilístico estratificado por conglomerados, con factor de expansión (`FACTOR PERSONAS`).
- 2.282 encuestas desde los 13 años; se usan solo las de 18 o más.
- Trae estrato, localidad, sexo y edad.
- Es **independiente** de la población del simulador: otra encuesta, otras personas.

**Lo que se miró antes de escribir esto:** el diccionario, los encabezados y los códigos presentes en
cada columna. **Ningún porcentaje.**

**El lote no toca el primero:** `sorteo.csv` y `reales_practica.json` quedan iguales, y las pruebas ya
corridas dan lo mismo si se repiten. El lote 2 va en `sorteo_lote2.csv` y
`reales_practica_lote2.json`; un experimento lo usa solo si lo pide.

**Las 16 preguntas, en 7 familias.** Solo opinión: se dejan fuera las de conducta (si separa, recicla,
reutiliza, tiene mascotas) y las de hecho (si pasa la ruta de reciclaje). El texto de la página y los
códigos favorables siguen DI-BA3: favorable es estar de acuerdo con la pregunta tal como queda escrita.
NS/NR (99) es «no sabe» (DI-BR1).

| id | familia | columna | pregunta en la página | escala | favorables |
|---|---|---|---|---|---|
| ECA21_P13A | ECA21_P13 | 47 | ¿Está de acuerdo con que «da igual si se separan o no los residuos porque al final todo termina revuelto»? | 1 De acuerdo, 2 En desacuerdo | 1 |
| ECA21_P13B | ECA21_P13 | 48 | ¿Está de acuerdo con que «da igual si se separan o no los residuos porque eso lo hacen los recicladores»? | igual | 1 |
| ECA21_P14AA | ECA21_P14A | 53 | ¿Está de acuerdo con que confía en las personas recicladoras de oficio? | igual | 1 |
| ECA21_P14AB | ECA21_P14A | 54 | ¿Está de acuerdo con que la población recicladora de oficio es fundamental para el aprovechamiento de residuos en Bogotá? | igual | 1 |
| ECA21_P14AC | ECA21_P14A | 55 | ¿Está de acuerdo con que las personas recicladoras de oficio son peligrosas? | igual | 1 |
| ECA21_P15 | ECA21_P15 | 56 | ¿Cree que la mayoría de las personas en Bogotá separa los residuos en sus hogares? | 1 Sí, 2 No | 1 |
| ECA21_P19A | ECA21_P19 | 70 | ¿Está de acuerdo con que «el río Bogotá está tan sucio que da igual si le tiran más residuos»? | 1 Totalmente en desacuerdo … 4 Totalmente de acuerdo | 3, 4 |
| ECA21_P19B | ECA21_P19 | 71 | ¿Está de acuerdo con que «como no existen sistemas de reciclaje en toda la ciudad, da igual si separo o no los residuos en mi casa»? | igual | 3, 4 |
| ECA21_P19C | ECA21_P19 | 72 | ¿Está de acuerdo con que «como las industrias son las que más contaminan, los esfuerzos que haga por cuidar el ambiente son insignificantes»? | igual | 3, 4 |
| ECA21_P22 | ECA21_P22 | 76 | ¿Qué tanto cuidan las personas en Bogotá a los animales silvestres que viven en la ciudad? | 1 Mucho, 2 Poco, 3 Nada | 1 |
| ECA21_P32 | ECA21_P32 | 103 | ¿El estado de la mayoría de los ríos, humedales y espacios naturales de Bogotá es bueno? | 1 Muy bueno, 2 Bueno, 3 Malo, 4 Muy malo | 1, 2 |
| ECA21_P33A | ECA21_P33 | 104 | ¿Qué tanto puede hacer usted mismo para cuidar el ambiente? | 1 Mucho, 2 Poco, 3 Nada | 1 |
| ECA21_P33B | ECA21_P33 | 105 | ¿Qué tanto puede hacer el resto de la ciudadanía para cuidar el ambiente? | igual | 1 |
| ECA21_P33C | ECA21_P33 | 106 | ¿Qué tanto puede hacer el gobierno de la ciudad para cuidar el ambiente? | igual | 1 |
| ECA21_P33D | ECA21_P33 | 107 | ¿Qué tanto puede hacer el gobierno nacional para cuidar el ambiente? | igual | 1 |
| ECA21_P33E | ECA21_P33 | 108 | ¿Qué tanto pueden hacer las fábricas y empresas en general para cuidar el ambiente? | igual | 1 |

(Columnas de la hoja `NUM`, contadas desde 0.)

**El sorteo.** La misma regla 3 de DI-BA5:
- se sortea por familia, en el ámbito «Bogotá», con la semilla **20261005**;
- la mitad de las familias, redondeando hacia arriba, va al guardado: **4 al guardado y 3 a práctica**;
- todas son independientes y ninguna se ha visto, así que las 7 entran al sorteo;
- el guardado del lote 2 no se calcula ni se le pregunta al simulador hasta una prueba final
  pre-registrada.

**Resultados reales, solo de las de práctica.** Mismo cálculo que `banco_reales.resultado`, con estas
piezas:
- **Peso:** `FACTOR PERSONAS`.
- **Sexo:** `FC`. 1 es Hombres y 2 Mujeres; los demás códigos no entran en el grupo, sí en el total.
- **Edad:** `FD_MAYOR`, en los tramos de la población. Solo personas de 18 o más.
- **Estrato:** `FB`, en 1, 2, 3, 4 y 5-6. El 99 no entra.
- **Localidad:** `FA`, de 1 a 19.
- **Pares claros:** regla DI-BR5 de estructura y z > 1,96, como en el primer lote.

**Código:** `src/experiments/banco_lote2.py`, con pruebas en `tests/test_banco_lote2.py`.

### 11.1 Sorteo y resultados de práctica del lote 2 (5/10)

- **Sorteo** (`sorteo_lote2.csv`, commit antes de calcular): práctica, familias P14A, P15 y P22
  (5 preguntas); guardado, P13, P19, P32 y P33 (11 preguntas).
- **Resultados de práctica** (`reales_practica_lote2.json`): ninguna queda fuera por estructura; entre
  2.133 y 2.257 respuestas válidas por pregunta; **30 pares claros** entre grupos.
- Con el lote 2, el banco suma 181 preguntas: práctica 119 (101 con resultado utilizable) y guardado
  62.
- Ninguna de las 16 es de aprobación de una medida, así que el lote no cambia lo que concluyeron las
  pruebas del nivel: hacen falta preguntas hermanas de medidas de ciudad (camino 3).

## 12. Tercer lote: Encuesta Bienal de Culturas 2025 (pre-registro, 5/10, antes de sortear)

**Fuente.** Encuesta de Indicadores de Cultura Ciudadana y Garantía de Derechos 2025, módulo de la
Encuesta Bienal de Culturas (Secretaría de Cultura, Recreación y Deporte). Daniel la compartió el 5/10
como dato público.
- Probabilística en hogares, por manzanas estratificadas: 5.860 personas desde los 13 años, con
  factor de expansión.
- Es **independiente** de la población del simulador.

**Datos sensibles: no se leen ni se copian.** La base original trae dirección, coordenadas, manzana,
sector, teléfono, datos de cada miembro del hogar y preguntas sobre sexualidad. Se guardó una copia
reducida, `data/raw/scrd/bienal_culturas_2025_reducida.xlsx` (no se sube), con solo las secciones de
opinión (3 a 11), localidad, estrato, sexo, edad, grupo de edad y factor. La descarga completa se borró.

**Lo que se miró antes de escribir esto:** preguntas, subpreguntas y etiquetas de respuesta. **Ningún
porcentaje.**

**Reglas de selección (opción 1, a mano, sin API):**
1. **Entra** lo que es opinión, actitud o percepción.
2. **No entra:**
   - lo que es conducta, experiencia, conocimiento o un hecho («¿participa?», «¿presenció…?»,
     «¿hay parques cerca?», «¿separa residuos?»);
   - las preguntas nominales sin orden (motivos, emociones, medios de transporte);
   - las condicionadas a una respuesta previa (73, 103, 131);
   - las de selección múltiple sin escala (142);
   - las de votar (42, 53), por el criterio 5 de §2;
   - las que tienen las etiquetas fuera del orden de sus códigos (49, 57, 81);
   - las abiertas.
3. **No entra lo que repite una pregunta del catálogo**, mismo objeto y mismo alcance:
   - seguridad en la ciudad, 104 = `VS10`;
   - satisfacción con la movilidad, 133 = `MV4`;
   - orgullo de vivir en Bogotá, 84 = `AG2`;
   - satisfacción con vivir en Bogotá, `P61.1` = `CV1`;
   - satisfacción con la vivienda, `P61.3` = `VS7`;
   - seguridad en la zona, `P66.8` = `VS8`.

   Tampoco entra «no tiene problemas con ningún vecino» (`P5.17`), que es un resumen de las demás
   opciones.
4. **Favorable** (DI-BA3): estar de acuerdo con la pregunta tal como queda en la página.
   - Escalas ordenadas: la mitad alta. Con 4 puntos, 3 y 4; con 3 puntos (nada, poco, mucho), 3;
     binarias de acuerdo, «de acuerdo».
   - Sí/No: «sí». «Menos/más de la mitad»: «más de la mitad».
   - Escalas de 1 a 10 («de 10 personas, ¿cuántas…?»): de 6 a 10.
   - 109 («la ciudad, respecto al año pasado, es…»): «más segura».
   - Los «NS/NR» de la etiqueta son «no sabe» (DI-BR1).
5. **Familia** = una pregunta de la encuesta con todas sus subpreguntas (`indice_pregunta`).

**Resultado de las reglas: 52 familias, 190 preguntas.** La lista exacta (pregunta y favorables) está
en `src/experiments/banco_lote3.py` (`INCLUIR`, `EXCLUIR_SUB`), subida antes del sorteo.

**Sorteo.** La regla 3 de DI-BA5, por familia, con la semilla **20261006**: la mitad, redondeando
hacia arriba, al guardado.

**Resultados reales, solo de práctica.** Mismo cálculo que los lotes 1 y 2:
- **Peso:** el factor.
- **Edad:** solo personas de 18 o más, en los tramos de la población.
- **Estrato:** 1, 2, 3, 4 y 5-6.
- **Localidad:** de 1 a 19.
- **Pares claros:** regla DI-BR5 de estructura y z > 1,96.

## 13. Cuarto lote: Barrios Vivos 2025 (pre-registro, 5/10, antes de sortear)

**Fuente.** «Barrios Vivos: Orgullo, Confianza e Identidad» (Secretaría de Cultura, dic. 2024 - ene.
2025), compartida por Daniel el 5/10 como dato público. Se usa a pedido suyo, por su columna de
localidad.

**No es representativa de Bogotá.**
- La muestra es de **9 barrios intervenidos en 5 localidades** (Barrios Unidos, Bosa, La Candelaria,
  Suba y Usme), con muestreo aleatorio simple en cada barrio.
- Su `total` no es el de la ciudad: **no entra en las pruebas del nivel de la ciudad**. Sirve para
  comparar grupos y esas 5 localidades, y se reporta aparte.

**Datos personales: no se leen ni se copian.** Se quitaron el nombre de quien responde, el nombre del
encuestador, quién subió el registro, los identificadores del formulario y las coordenadas. Copia
reducida en `data/raw/scrd/barrios_vivos_2025_reducida.xlsx` (no se sube).

**Las preguntas (2, en 2 familias).** El orgullo de vivir en Bogotá (P2) no entra porque repite `AG2`;
las abiertas tampoco.

| id | pregunta en la página | favorables |
|---|---|---|
| BV25_P3 | ¿Cree que podría confiar en más de la mitad de las personas que viven en Bogotá? | «Más de la mitad» |
| BV25_P6 | ¿Qué tan orgulloso/a se siente de vivir en su barrio? | «Muy orgulloso/a», «Orgulloso/a» |

Los «Ns/Nr» y «Sin información» son «no sabe». Las filas sin factor de expansión («Sin información»)
no entran.

**Sorteo.** Por familia, con la semilla **20261007**: 1 al guardado y 1 a práctica.

### 13.1 Sorteo y resultados de práctica de los lotes 3 y 4 (5/10)

- **Sorteo** (commit `05dd598`, antes de calcular):
  - lote 3: 26 familias y 99 preguntas a práctica; 26 familias y 91 preguntas al guardado;
  - lote 4: `BV25_P3` y `BV25_P6`, una en cada conjunto.
- **Lote 3, práctica** (`reales_practica_lote3.json`):
  - 97 preguntas utilizables y **930 pares claros**.
  - 2 quedan fuera por la regla de estructura (DI-BR5). Son la séptima opción de las listas de
    derechos vulnerados (preguntas 75 y 77, probablemente «otro»): `P48.7` solo tiene «No» en los datos
    y `P49.7` está vacía.
  - Entre 5.437 y 5.639 respuestas válidas por pregunta utilizable: casi toda la muestra adulta.
- **Lote 4, práctica** (`reales_practica_lote4.json`): 1 pregunta, 2.031 respuestas válidas y 7 pares
  claros. Sigue marcada como no representativa de la ciudad.
- **El banco, en total:**
  - 373 preguntas;
  - práctica: lote 1, 96 utilizables; lote 2, 5; lote 3, 97; lote 4, 1;
  - guardado: 51 + 11 + 91 + 1 = 154.
- Las preguntas de **valoración de proyectos de ciudad** (el metro: orgullo, necesidad, si lo usaría;
  la bicicleta) quedaron repartidas entre práctica y guardado según su familia.

## 14. Quinto lote: Encuesta Distrital de Percepción 2025 (pre-registro, 5/10, antes de sortear)

**Fuente.** Encuesta Distrital de Percepción (EDP), año móvil 2025, de la Secretaría Distrital de
Planeación. Microdatos públicos y anonimizados, que Daniel encontró y cuya descarga autorizó el 5/10:
`data/raw/sdp/base_ano_movil_2025.csv` (9,8 MB) y su diccionario (no se suben).
- Probabilística, en hogares y presencial: **13.082 personas adultas**, una por fila, con factor de
  expansión calibrado (`fexp_calp_anu`).
- Las 19 localidades urbanas (`Cod_Locali`, numeración oficial) y UPL.
- Es **independiente** de la población del simulador.

**Datos personales.** El formulario pregunta documento y fecha de nacimiento, pero la base publicada no
los trae; se revisó por nombre de columna antes de leer valores. Las `DIRECTORIO_*` son identificadores
de la encuesta (manzana, predio, hogar y persona), no ubicaciones.

**Lo que se miró antes de escribir esto:** diccionario, nombres de columnas, códigos presentes y la
correspondencia de localidades. **Ningún porcentaje.**

**Preguntas: las 40 afirmaciones de acuerdo de 1 a 5** (`[A-J]x104`, `x105`, `x408`, `x503`, `x602`,
`x603`, `x604`, `x704`).
- Escala: 1 Totalmente en desacuerdo … 5 Totalmente de acuerdo; 99 = Ns/Nr, que es «no sabe».
- **No entran dos, por repetir el catálogo** (regla 3 de §12):
  - `Hx704`, «me siento orgulloso/a de vivir en Bogotá» = `AG2`;
  - `Ax602`, «me siento satisfecho con el principal medio de transporte» = `MV4`.
- **Quedan 38.**
- **Favorable:** 4 y 5 (de acuerdo y totalmente de acuerdo).
- **Familia:** el bloque, es decir, las 8 preguntas del formulario.
- **Texto en la página:** «¿Está de acuerdo con que «<afirmación del diccionario>»?».

**Sorteo.** Regla 3 de DI-BA5, por familia, con la semilla **20261009**: 4 familias al guardado y 4 a
práctica.

**Resultados reales, solo de práctica.** Como en los demás lotes:
- **Peso:** `fexp_calp_anu`.
- **Sexo:** `D1`, sexo al nacer (1 Hombre, 2 Mujer; el 3 no entra en el grupo).
- **Edad:** `A6x3`, en años, en los tramos de la población.
- **Estrato:** `H1`, en 1, 2, 3, 4 y 5-6; 7 («no tiene servicio») y 99 no entran.
- **Localidad:** `Cod_Locali`.
- **Pares claros:** regla DI-BR5 y z > 1,96.

**Código:** `src/experiments/banco_lote5.py`, con pruebas en `tests/test_banco_lote5.py`.

### 14.1 Sorteo y resultados de práctica del lote 5 (5/10)

- **Sorteo** (commit `1f05bad`, antes de calcular):
  - práctica: bloques 104, 602, 603 y 604 (áreas verdes; movilidad y obras; metro y espacio público;
    ambiente), 17 preguntas;
  - guardado: bloques 105, 408, 503 y 704 (mascotas; seguridad y justicia; economía y turismo;
    confianza), 21 preguntas.
- **Resultados de práctica** (`reales_practica_lote5.json`): ninguna queda fuera por estructura; entre
  12.121 y 13.058 respuestas válidas por pregunta; **162 pares claros**.
- **Con el lote 5, el banco suma 411 preguntas.**
- **Las preguntas de acuerdo o sí/no que usa la estimación de D19** pasan de 92 a 109 en práctica y de
  74 a 95 en el guardado.
- **Las candidatas de D19 no cambian solas:** siguen siendo las 92 validadas. Usar estas nuevas como
  candidatas es otra configuración, que necesita su propia prueba pre-registrada.

## 15. Sexto lote: encuestas políticas del CNC, nivel 1 de D21 (pre-registro, 6/10, antes de sortear)

**Fuente.** Cuatro encuestas del CNC para Semana (`DATA_INVENTORY.md` §16; carpeta de `BSS_CNC_POLITICA_DIR`). Son
nacionales; **solo se usan los encuestados de Bogotá** (`DANE` = 11001), con su factor de expansión (`factor`):

| Estudio | Fecha | En Bogotá | Lo que entra |
|---|---|---|---|
| CC355801 | feb 2021 | 384 | migración: afirmaciones y medidas (preguntas 1, 2, 4 y 5) |
| CC871401 | may 2021 | 256 | el paro nacional (preguntas 9 a 12, 14, 19, 20 y 24) |
| CC871801 | jun 2021 | 260 | el paro (13, 16 y 17); aprobación de Iván Duque (23) |
| CC873501 | 2021-22 | 411 | el país y la seguridad de la ciudad por buen camino (3 y 4); aprobación de Duque (19); aborto y vacunación (28 a 30) |

Los cinco estudios de 2022 y 2026 no entran: lo suyo es intención de voto (nivel 2). CC891901 trae dos preguntas sobre
Venezuela que no entran, porque su texto depende de una pregunta anterior («¿eso puede ser positivo…?»).

**Lo que se miró antes de escribir esto:** la estructura de las bases y los diccionarios (preguntas, categorías y
conteo de encuestados de Bogotá). **Ningún porcentaje.**

**Las preguntas.** Entran las de una escala con un lado favorable claro y texto propio:
- **acuerdo de 1 a 5** (1 Totalmente de acuerdo … 5 Totalmente en desacuerdo); favorable: 1 y 2;
- **acuerdo/desacuerdo** de dos opciones; favorable: 1, acuerdo;
- **sí/no**; favorable: 1, sí;
- **aprueba/desaprueba**; favorable: 1, aprueba;
- **«no sabe»:** el 9 (NS/NR), como en los demás lotes.

**No entran:**
- **la intención de voto y lo electoral:** la probabilidad de votar, los candidatos, las coaliciones, y la propuesta de
  un candidato (CC873501 P26). Es el nivel 2 de D21.
- **la imagen de personajes y de funcionarios** (CC871401 T22, CC871801 T9 y T11, CC873501 P17): se acerca a lo
  electoral y queda con el nivel 2, bajo revisión jurídica.
- **las preguntas abiertas** (D21);
- **lo que no es opinión:**
  - si tiene contacto con migrantes;
  - si vivió fuera del país;
  - si alguien en su hogar se vacunó;
  - si participa en política en redes;
  - las autorizaciones y los filtros.
- **las que repiten el catálogo** (regla 3 de §12):
  - CC873501 P2, «¿su ciudad va por buen camino?», es `AG1`;
  - CC871801 P1 y CC873501 P1, «¿aprueba el desempeño del alcalde de su ciudad?», son `GG3`.

**Familias:** la pregunta numerada de cada estudio, como en los lotes 2, 3 y 5. Las subpreguntas de una misma
pregunta (1.A a 1.G; 24.1 a 24.16) son una familia.

**Texto en la página:** el del diccionario, sin el número, sin las instrucciones al encuestador («LEA», «(E: …)»,
«R.U.») y con la subpregunta dentro de la frase. Por ejemplo: «¿Cree que la presencia de la Fiscalía General de la
Nación es importante para la solución del paro?».

**Quedan 64 preguntas en 22 familias** (`python src/experiments/banco_lote6.py --tabla`, que no lee datos). Dos
cosas del armado se declaran antes de sortear:
- **Nueve textos van escritos a mano** (DI-BL14). Tres etiquetas del diccionario están cortadas y otras traen
  erratas; el sentido no cambia.
- **El año de CC873501 es un supuesto, 2022** (DI-BL13). No trae fecha en ningún lado, y por su contenido es de
  finales de 2021 o comienzos de 2022. ~~**Confirmado por Daniel el 6/10: 2022.**~~ **Corregido el 8/10: finales de 2021**
  («corrige con finales del 2021»). El sorteo no cambia, porque va por familia. En `sorteo_lote6.csv` y `sorteo_lote7.csv`
  solo cambian el año y el texto («A finales de 2021: …»). Las pruebas del lote 6 y del nivel 3 se corrieron con 2022.
- **Los estudios de 2026 llevan su mes en el texto** (DI-BL19, corregido el 8/10). Antes decían «En la encuesta de 2026».
  - **Leídos de la base:** CC893401, abril; CC893701, mayo.
  - **Supuestos por el contenido:** CC892901, «a comienzos de 2026», y CC893201, «entre marzo y abril de 2026».

**Sorteo.** Regla 3 de DI-BA5, por familia, con la semilla **20261010**: la mitad de las familias, redondeando hacia
arriba, al guardado.

**Resultados reales, solo de práctica.** Como en los demás lotes:
- **Peso:** `factor`.
- **Sexo:** `GENERO` (1 Hombres, 2 Mujeres).
- **Estrato:** `ESTRATO`, en 1, 2, 3, 4 y 5-6; el 0 («sin estrato») no entra.
- **Edad:** `EDAD` o `REDAD`, en los grupos de cada encuesta (18-25, 26-40, 41-55, 56 o más). No coinciden con los de la
  población; se dice en `cortes_edad`. ~~CC355801 no trae edad en la base.~~ Falso: la trae en `EDAD_RANGO` (§15.3).
- **Localidad: no hay.** Estas preguntas no entran al mapa ni a la parte de localidades.
- **Pares claros:** regla DI-BR5 y z > 1,96.

**Un límite que se declara antes de sortear.** Con unos 250 a 410 encuestados de Bogotá por estudio, el margen de cada
porcentaje es de unos ±5 a ±6 puntos. Es más ancho que en la EDP (13.000) o la Bienal (5.500).

**Lo que este lote no cambia solo:** las candidatas de D19. Sumarlas es otra configuración, con su prueba pre-registrada.

**Código:** `src/experiments/banco_lote6.py`, con pruebas en `tests/test_banco_lote6.py`.

### 15.1 Sorteo y resultados de práctica del lote 6 (6/10)

- **Sorteo** (commit `91288b6`, antes de calcular):
  - **práctica:** 11 familias y 30 preguntas:
    - migración, las preguntas 1, 2 y 4;
    - el paro, CC871401 P11 y P19, y CC871801 P13, P16 y P17;
    - CC873501 P3, P4 y P30.
  - **guardado:** 11 familias y 34 preguntas:
    - migración P5;
    - el paro, CC871401 P9, P10, P12, P14, P20 y P24;
    - la aprobación de Duque, CC871801 P23 y CC873501 P19;
    - CC873501 P28 y P29.
- **Resultados de práctica** (`reales_practica_lote6.json`): **6 de 30 quedan fuera por la regla de estructura**
  (DI-BR5: menos de 300 respuestas válidas). Son todas las de CC871401 y CC871801, del paro: esas encuestas tienen 256 y
  260 encuestados en Bogotá, y sus preguntas quedan entre 242 y 258 respuestas válidas.
  - **Quedan 24 utilizables**, con entre 374 y 408 respuestas válidas y **88 pares claros**.
  - **La regla no se cambia después de ver esto.** El guardado de esos dos estudios también quedará fuera cuando se
    calcule: de las 34 guardadas, solo serán utilizables unas 12 (migración P5 y CC873501 P19, P28 y P29).
- **Los resultados no se suben al repositorio.** D21 no dice si los agregados de estas encuestas pueden ir a GitHub.
  Quedan en `data/processed/banco/`, ignorados, y viajan con `empacar_traslado.py`.
- **Con el lote 6, el banco suma 475 preguntas.**

### 15.2 Enmienda 1 del lote 6 (6/10/2026, después de ver los resultados de práctica)

**Daniel pidió incluir las preguntas con menos de 300 respuestas válidas.** La regla de estructura de todos los lotes
(DI-BR5) dejaba fuera las 6 de práctica del paro, con entre 242 y 258 respuestas.
- **En el lote 6, el mínimo baja a 200 respuestas válidas** (DI-BL15). Las que quedan entre 200 y 299 se marcan
  `bajo_300`.
- **Es un cambio posterior a ver qué quedaba fuera, y queda dicho así.** No se miró ningún porcentaje para decidirlo.
  Las 6 tienen un margen de unos ±6 puntos, más ancho que el resto del banco.
- **La regla de 300 sigue igual en los lotes 1 a 5.**
- **El guardado** del lote 6 se calculará con el mismo mínimo de 200.
- **Resultado:** quedan las 30 de práctica utilizables, con entre 242 y 408 respuestas válidas y 130 pares claros.

### 15.3 Enmienda 2 del lote 6 (6/10/2026): CC355801 sí trae edad

**Lo que estaba escrito era falso.** El pre-registro decía «CC355801 no trae edad en la base», pero la trae en `EDAD_RANGO`,
con tres grupos (18-34, 35-54 y 55 o más) y NR. Al revisar los nombres de columna de los otros estudios se vio que el
nombre era distinto.
- **Se corrige:** el grupo de edad de sus 21 preguntas de práctica se calcula con esos tres grupos (DI-BL16).
- **Qué cambia:** solo los resultados por edad y sus pares claros, no los totales. El guardado aún no se ha calculado.
- **Resultado:** 30 de práctica utilizables y 145 pares claros (antes, 130).

## 16. Séptimo lote: intención de voto de las encuestas del CNC, niveles 2 y 3 de D21 (pre-registro, 6/10, antes de sortear)

**Lo pidió Daniel** («incluye intención de voto»). **Es material electoral.** Por D21, nada de este lote se muestra en la
página ni entra a las candidatas de la estimación antes de la revisión jurídica del CNC.
`tests/test_banco_lote7.py` comprueba que no entre. Su guardado queda para validar el nivel 3 (simular la intención de
voto), con su propio pre-registro.

**Fuente.** Las nueve encuestas del CNC de `DATA_INVENTORY.md` §16 que preguntan por el voto, solo con los encuestados de
Bogotá (`DANE` = 11001) y su factor de expansión:
- **para Semana:** mayo y junio de 2021, 2022 y abril de 2022;
- **para Revista Cambio:** enero de 2026, más cuatro de 2026 sin mes en el nombre.

**Lo que se miró antes de escribir esto:** diccionarios, etiquetas de valor y nombres de columnas. **Ningún porcentaje.**

**Las preguntas** (lista explícita en `banco_lote7.ESTUDIOS`):
- **intención de voto presidencial en primera vuelta** y por fórmulas (2026);
- **segundas vueltas** entre dos candidatos;
- **escenarios de primera vuelta** con candidatos dados (CC891901 P6 a P9);
- **consultas interpartidistas** y los precandidatos de cada consulta;
- **«nunca votaría por…»** (2026);
- **la tendencia** por la que votaría (izquierda, centro izquierda, centro derecha, derecha; CC873501 P25);
- **la probabilidad de votar** (F1).

**No entran:**
- **las preguntas condicionadas a una respuesta anterior**, porque no las contestó toda la muestra: CC873501 P21 a P23
  («si piensa votar por la coalición…») y CC891901 P2 («si no se presenta…»);
- **la pregunta abierta** CC871801 P21 («¿por cuál candidato jamás votaría?»);
- **la imagen de personajes,** que tampoco está en el lote 6 y queda para después.

**Cómo se arma cada pregunta del banco** (DI-BL17):
- **una por cada opción con nombre:** candidato, fórmula, consulta, coalición o tendencia;
- **lo favorable** es esa opción;
- **«otro», el voto en blanco y «ninguno»** son respuestas válidas que no son esa opción;
- **NS/NR** es «no sabe»;
- **la probabilidad de votar** es una sola pregunta, y lo favorable es «definitivamente» o «probablemente» sí;
- **el texto empieza por la fecha** («En mayo de 2021: en una segunda vuelta entre Sergio Fajardo y Gustavo Petro, ¿votaría
  por Gustavo Petro?»). Si el estudio no dice el mes, solo el año.

**En abril de 2022 (CC875701) solo contestaron quienes piensan votar.** Su texto lo dice («entre quienes piensan votar»).

**Quedan 373 preguntas en 94 familias** (`python src/experiments/banco_lote7.py --tabla`, que no lee datos). La familia es
la pregunta numerada de cada estudio.

**Sorteo.** Regla 3 de DI-BA5, por familia, con la semilla **20261011**.

**Resultados reales, solo de práctica.** Igual que el lote 6:
- **peso:** `factor` o `FACTOR`;
- **sexo:** `GENERO`;
- **estrato:** `ESTRATO`, en 1, 2, 3, 4 y 5-6;
- **edad:** en los grupos de cada encuesta. En 2021-2022: 18-25, 26-40, 41-55 y 56+. En 2026: 18-24, 25-34, 35-44, 45-54
  y 55+;
- **sin localidad.**
- **Mínimo de respuestas:** 200 desde el principio, como pidió Daniel para el lote 6 (§15.2). Con 256 a 545 encuestados de
  Bogotá por estudio, el margen de cada porcentaje es de unos ±4 a ±6 puntos.

**Los resultados no se suben al repositorio**, como en el lote 6.

**Código:** `src/experiments/banco_lote7.py`, con pruebas en `tests/test_banco_lote7.py`.

### 16.1 Sorteo y resultados de práctica del lote 7 (6/10)

- **Sorteo** (commit `6404b29`, antes de calcular): 47 familias y 158 preguntas a práctica; 47 familias y 215 al
  guardado.
- **Un arreglo de lectura** (DI-BL21): el factor de expansión de la base en CSV (CC892901) trae coma decimal, y en la
  primera pasada sus 31 preguntas de práctica salieron con 0 respuestas válidas. Corregido, no cambia nada del diseño.
- **Resultados de práctica** (`reales_practica_lote7.json`, no se sube): las 158 son utilizables, con entre 203 y 540
  respuestas válidas.
- **El guardado no se ha calculado.** Queda para la validación pre-registrada del nivel 3.
- **Con el lote 7, el banco suma 848 preguntas.** Las 373 del lote 7 son electorales y quedan fuera de la página (D21).

