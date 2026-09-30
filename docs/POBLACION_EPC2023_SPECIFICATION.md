# POBLACIÓN EPC 2023 — SPECIFICATION

**Una población sintética de Bogotá en la que cada agente lleva a una persona real de la Encuesta de Percepción Ciudadana 2023, con todas sus respuestas, emparejada dentro de su localidad.**

Proyecto: Bogotá Social Simulator
Versión: 0.1 — especificación, sin código
Fecha: 30 de septiembre de 2026
Decisión que la origina: D17 (`PROJECT_CONTEXT.md` §39), pieza 1; reabre DI-B10
Datos: receptor de Multipropósito 2021 (el de siempre) y EPC 2023 de Bogotá Cómo Vamos (`DATA_INVENTORY.md` §13.6 y §13.8)

---

## 1. Qué cambia respecto de la población actual

| | Población actual (v0.5-dim2) | Población EPC 2023 |
|---|---|---|
| Donante | ECP (DANE) | **EPC 2023 (Bogotá Cómo Vamos)** |
| Opinión que lleva cada agente | una variable (`opinion_t0`) | **todas las respuestas de su donante** (≈ 100 preguntas generales) |
| Localidad del donante | no existe (la ECP llega a «Bogotá») | **la misma que la del agente** |
| Geografía de la opinión en el mapa | solo composición (DI-V52, paso 0b) | **medida**: sale de personas que viven en esa localidad |

La población actual no se borra: sigue sirviendo a la serie de tiempo y al motor de
escenarios. Esta es otra, con otro donante y otro propósito.

---

## 2. Datos

### 2.1 Donante: EPC 2023

1.501 personas, 19 localidades (sin Sumapaz), mediana de 80 por localidad. Ponderador
`FEXP` (expandido a población, §13.6). Conglomerado: `Manzana`, que se numera dentro de
cada localidad (DI-D7): el conglomerado es localidad × manzana.

Variables para emparejar, con su código de 2023 verificado en las etiquetas del
archivo (no en el diccionario):

| Variable | Código 2023 | Categorías |
|---|---|---|
| Localidad | `CS0A` | 1-19 |
| Sexo | `CS1` | 1-2 |
| Edad | `CS2` (años) y `CS2A` (5 tramos: 18-25, 26-35, 36-45, 46-55, 56+) | |
| Estrato | `CS21` | 0 (sin estrato/rural) a 6 |
| Educación | `CS4` | 0 no sabe · 1 ninguno · 2 preescolar · 3 primaria · 4 secundaria · 5 media · 6 superior · 8 técnico/tecnológico · 9 posgrado |

### 2.2 Receptor: Multipropósito 2021

El mismo de toda la población sintética (`load_multiproposito_receptor`, ponderado por
`FEX_C`), adultos de 18 años o más, con localidad, sexo, edad, estrato y educación.

---

## 3. Construcción

1. **Muestreo del receptor:** 20.000 agentes por PPS con el método de `muestreo.py`.
   Con ≈ 80 donantes por localidad, más agentes no agregan información (lección de
   A08), pero 1.000 por localidad dejan el ruido de sorteo muy por debajo del de la
   encuesta.
2. **Emparejamiento por hot-deck, con la localidad como bloque exacto:** un agente de
   Kennedy solo puede heredar a un encuestado de Kennedy. Dentro del bloque, vecino
   más cercano en sexo, tramo de edad, estrato y educación armonizada (§3.1), con
   desempate ponderado por `FEXP` (DI-M1) y orden canónico (DI-M2).
3. **Escalera de relajación**, si una celda no tiene donantes: primero se suelta la
   educación, después el estrato, después la edad. **La localidad nunca se suelta.**
   Cada agente registra en qué escalón quedó.
4. **Sumapaz no tiene donantes.** Sus agentes quedan marcados «sin datos» y el mapa lo
   dice; no se les asigna un donante de otra localidad.
5. **Cada agente guarda el identificador de su donante**, no una copia de sus
   respuestas. Las respuestas se leen del microdato cuando se consultan: así hay una
   sola fuente de verdad y el archivo de la población no se vuelve un microdato
   duplicado.

### 3.1 Educación armonizada

Cuatro niveles comparables entre las dos encuestas: básica o menos (EPC 1-4), media
(5), técnica o tecnológica (8), universitaria o posgrado (6 y 9). `CS4 = 0` (no sabe)
se trata como faltante y solo cuenta en el último escalón. La correspondencia con el
receptor se escribe en el código y se prueba.

---

## 4. El catálogo de preguntas

Una pregunta de 2023 entra al catálogo si:
- es de respuesta única;
- la responde al menos el 80 % de la muestra (§13.8: 114 preguntas);
- su código existe en el archivo (no solo en el diccionario);
- **no es de imagen** (`GG1`, `GP1_*`: códigos invertidos en 2023, DI-B2);
- su escala y sus códigos de no respuesta se leen de las **etiquetas de valor del
  archivo de 2023**, y se guardan con la pregunta. Una pregunta cuyas etiquetas no
  permitan saber la dirección de la escala se deja fuera.

---

## 5. Cómo se responde una pregunta del catálogo

Distribución ponderada de las respuestas de los donantes de los agentes, en la ciudad
y por localidad. **El margen de error es el de la encuesta, no el de la población**:
se estima con bootstrap de conglomerados (localidad × manzana) sobre los donantes, no
sobre los 20.000 agentes, que son copias.

---

## 6. Verificación de la población (antes de usarla para nada)

Se escribe antes de construirla; los resultados se anotan aquí con fecha:

1. **Demografía:** la distribución de sexo, edad, estrato y educación de los agentes
   reproduce la del receptor por localidad (es por construcción; si no, hay un error).
2. **Opinión:** para cada pregunta del catálogo, la media de los agentes en la ciudad y
   en cada localidad cae dentro del margen de la media ponderada de la EPC 2023. Es
   casi mecánico, porque los agentes heredan a los encuestados, pero no del todo: el
   receptor pesa las celdas de otra forma que `FEXP`. Si más del 10 % de los pares
   pregunta × localidad cae fuera del margen del 95 %, se revisa antes de seguir.
3. **Escalera:** qué porcentaje de agentes quedó en cada escalón, por localidad.
4. **Reproducibilidad:** dos construcciones con la misma semilla dan la misma
   población, en las dos máquinas (DI-M2).

---

## 7. Límites, dichos antes

- **80 personas por localidad.** El mapa de una sola ola tiene márgenes anchos (paso 0b
  de A08); la página los muestra.
- **Sin Sumapaz.**
- **Es 2023.** La población opina como Bogotá en 2023; la página lo dice.
- **Los agentes de un mismo donante opinan igual.** 20.000 agentes son ≈ 1.500 personas
  repetidas; la variedad real es la de la encuesta.

---

## 8. Qué se construye después de este documento

1. `src/population/poblacion_epc.py` (construcción y catálogo) y sus pruebas.
2. La verificación de §6, anotada aquí.
3. Después, el puente (`PUENTE_SPECIFICATION.md`).
