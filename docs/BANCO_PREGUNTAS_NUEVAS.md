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
