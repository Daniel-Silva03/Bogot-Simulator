# PESO POR AÑO RECIENTE EN EL DATO MEDIDO — SPECIFICATION

**Hoy la página junta los años de cada pregunta con el mismo peso por persona. ¿Se acerca más a lo que la gente responde
después si pesan más los años recientes?**

Proyecto: Bogotá Social Simulator
Versión: 0.1 — pre-registro, antes de calcular
Fecha: 13 de octubre de 2026
Origen: Daniel. La aprobación de Galán da 33,9 % porque junta 2024 y 2025, y en 2025 fue 26,4 %
(`REFORMULACION_2025_RESULTS.md` §2). Lo que se busca es que la página describa la Bogotá de hoy, no la de hace tres años.
Antecedente: en la intención de voto, el peso por fecha no mejoró nada (`VOTO_PESO_FECHA_RESULTS.md`). Esta es otra
fuente, con otra pregunta: un año de encuesta, no una fecha de sondeo.

---

## 1. La prueba: adivinar 2025 sin 2025

- **Con qué se adivina:** la población 2022-2024 (`data/processed/poblacion_epc2022_2024/`), que no tiene a nadie de 2025.
- **Qué se adivina:** las **35 preguntas que 2025 midió igual** (`verificacion_2025.csv` y DI-AR6), en la ciudad y en sus
  18 localidades.
- **El valor real:** la media de los encuestados de 2025, con su peso `Factor1`, sin «no sabe».
- **La medida:** la media de la escala llevada a 0-100 (0 = la primera respuesta, 100 = la última), para que todas las
  preguntas se comparen igual. Se reporta también el porcentaje del lado favorable (DI-CO18) donde se conoce.
- **Se decide con las preguntas que tienen 2 o más años en 2022-2024.** En las de un solo año, ninguna regla cambia nada.
  Se reportan todas.

## 2. Las tres reglas

Cada agente pesa lo que pesa hoy, por un factor según el año de su donante. Dentro de cada localidad, los pesos se
reescalan para que la localidad pese lo mismo que hoy: cambia la mezcla de años, no el peso de cada localidad.

| | Regla | Factor del año *a* | En la ciudad |
|---|---|---|---|
| **A** | la de hoy | 1 | cada año pesa lo que encuestó |
| **B** | media vida de un año | 2^−(último − *a*) | el último año pesa el doble que el anterior |
| **C** | solo el último año | 1 en el último, 0 en los demás | referencia: con un año hay unas 80 personas por localidad |

«Último» es el año más reciente en que se midió **esa** pregunta.

## 3. Regla de decisión

**La página pasa a B si se cumplen las dos condiciones:**
- **R1, la ciudad:** el error medio de B contra 2025 es al menos **0,5 puntos** menor que el de A.
- **R2, las localidades:** el error medio de B por localidad no sube más de **0,5 puntos** frente a A. Pesar más un año es
  tener menos personas, y el mapa ya tiene márgenes anchos.

**C no se adopta, aunque gane:** deja unas 80 personas por localidad. Se reporta para saber cuánto se pierde o se gana con
cada paso.

**Si B no cumple,** la página sigue con A, y la cifra de Galán se acompaña con lo que dijo cada año.

## 4. Predicciones

- **PA1.** B se equivoca menos que A en la ciudad.
- **PA2.** C se equivoca menos que A en la ciudad, pero más que A por localidad.
- **PA3.** B cumple la regla.

## 5. Lo que ya se sabe, y se declara

- **Cinco cifras de 2025:** satisfacción, orgullo, buen camino, aprobación del alcalde y víctima. Con A, la página queda
  por debajo de 2025 en cuatro (§2 de `REFORMULACION_2025_RESULTS.md`). Esa tabla usaba la población 2022-2025, no esta.
- **Las otras 30 preguntas** no las he comparado año por año.
- **El sentido:** entre 2024 y 2025 algunas cosas mejoraron y otras empeoraron. Si cada año salta al azar, pesar más el
  reciente puede no servir. Es lo que mide la prueba.

## 6. Gasto y datos

- **USD 0:** no llama a ningún modelo.
- Solo se suben las cifras agregadas por pregunta, ciudad y localidad. Ningún microdato.
- Código: `src/experiments/peso_anio_reciente.py`, con su prueba. Resultados en `PESO_ANIO_RECIENTE_RESULTS.md`.
