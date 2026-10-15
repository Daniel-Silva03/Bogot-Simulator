# PERSONAS CON SU ENCUESTA, EN LO POLÍTICO — ¿mejora el agente con datos reales de su vida, con un resumen o con una vida inventada?

Pre-registro escrito el **15 de octubre de 2026**, antes de calcular nada y de llamar al modelo. Lo pidió Daniel: combinar los
agentes armados con la encuesta con un perfil más personal hecho por la IA, con foco en lo político (el alcalde y el
gobierno), que es lo que le interesa a su jefe. Gasto: **unos USD 0,50, con tope de USD 2**; falta su visto bueno.

## 1. Pregunta

**Lo que se sabe** (`PERSONAS_PULIDAS_RESULTS.md`): el agente con las respuestas de cada persona, con probabilidades, acierta muy
bien cuando la pregunta se parece a lo que su perfil dice. Cuando no, rellena con un estereotipo pesimista. El perfil solo trae
opiniones, casi todas sobre la ciudad.

**Tres formas de completar el perfil:**
- **con datos reales de su vida** que la EPC 2025 trae y no usábamos;
- **con un resumen** de la persona que escribe la IA a partir de sus respuestas, sin inventar;
- **con una vida inventada por la IA,** la idea de Daniel tal cual: la IA escribe su trabajo, su familia y su día a día.

**¿Cuál ayuda en preguntas políticas?**

## 2. Datos

**Las personas:** 200 encuestados nuevos de la EPC 2025, sorteados con la semilla **20261016** entre los 1.120 que no se usaron
en las pruebas anteriores.

**Las 10 preguntas escondidas, todas políticas:**

| # | En 2025 | Pregunta | En el catálogo |
|---|---|---|---|
| P1 | `GOB_5` | Gestión del alcalde Galán | `GG3_GALAN` |
| P2 | `GOB_6` | Gestión del Concejo | `CC5A_GALAN` |
| P3 | `GOB_8` | Transparencia del gobierno de la ciudad | `MICE1_GALAN` |
| P4 | `GOB_10` | El gobierno responde a la ciudadanía | `MICE2_GALAN` |
| P5 | `GOB_9` | El gobierno abre espacios de participación | `MICE3_GALAN` |
| P6 | `GOB_1` | Bogotá va por buen camino | `AG1` |
| P7 | `CON_1` | La corrupción ha aumentado | `GG7` |
| P8 | `GOB_4` | Imagen favorable de Galán | (lote 8) |
| P9 | `CON_4` | Confianza en la Alcaldía | (lote 8) |
| P10 | `CON_7` | Confianza en el Gobierno Nacional | (lote 8) |

**Los textos, escalas y lado favorable:**
- de P1 a P7, los del catálogo de la página (`motor.vista` y `motor.lado`);
- de P8 a P10, los de `banco_lote8`.

**Ninguna está en el perfil:** las siete del catálogo se sacan de él.

**El perfil de opiniones (A):** las preguntas del catálogo que se miden en 2025, menos las siete escondidas (unas 33), más
sexo, edad, estrato y localidad. Quedan opiniones sobre la ciudad, los servicios y la convivencia, pero ninguna sobre el
gobierno.

**Los datos de su vida (B):** las respuestas reales de la persona a seis preguntas de la EPC 2025 que no son de opinión, con
el texto de su formulario:
- `EDU_3`: tipo de colegio de los estudiantes del hogar;
- `HOG_4`: horas de cuidado al día;
- `FIN_1`: de dónde sacó un préstamo;
- `CUL_3`: libros leídos en el año;
- `SEG_5`: si denunció el delito;
- `CTI_2_1` a `CTI_2_3`: para qué usa la IA. Sus opciones van a mano, porque el PDF no deja leerlas.

**Quedaron fuera al revisar los datos, antes de correr:**
- **el medio de transporte (`MOV_2`) y si el vehículo es eléctrico (`MOV_3`):** los códigos de Bogotá no siguen la numeración
  del formulario. El código 1, «Metro», lo tienen 596 personas, en una ciudad sin metro;
- **si conoce Bogotá Cómo Vamos (`GCV_1`):** ya está en el catálogo.

**Lo que se declara:**
- **P8 a P10 ya se usaron** en las pruebas de las personas, con otras personas. Sus cifras de Bogotá se conocen.
- **De P1 a P7 se conocen las cifras de la ciudad:** son preguntas del catálogo.
- **No se conoce lo que respondió ninguna de estas 200 personas.**
- **La intención de voto no entra:** la EPC no la pregunta, y las encuestas del CNC que sí lo hacen no pueden ir persona por
  persona a un modelo (D21).

## 3. Las variantes

**Todas con probabilidades**, la forma que funcionó (V2 de `PERSONAS_PULIDAS`): sin la instrucción contra la exageración y sin
ancla. Una llamada por persona para responder sus 10 preguntas.

| | Perfil | Llamadas extra |
|---|---|---|
| **A** | opiniones | — |
| **B** | opiniones y datos de su vida | — |
| **C** | B, más un resumen de la persona escrito por la IA | 1 por persona: «resume en 3 o 4 frases quién es esta persona según sus respuestas. No inventes nada que no esté en ellas» |
| **D** | A, más una vida inventada por la IA | 1 por persona: «escribe una biografía breve de esta persona, su trabajo, su familia, su barrio y su día a día, coherente con sus respuestas. Puedes inventar los detalles» |

## 4. Lo que se mide

Lo mismo que en `PERSONAS_PULIDAS`:
- el error individual, contra la constante;
- el error del total de Bogotá;
- la TVD;
- **la página:** su estimación de cada pregunta como pregunta nueva (`Motor.estimar`, con el texto de la encuesta). De P1 a
  P7 se quita de las candidatas la misma pregunta (`CAT_<código>`), para que no la encuentre.

## 5. Reglas (escritas antes de calcular)

**No hay elección entre variantes:** cada hipótesis se decide por separado. Una variante **mejora** a otra si su error del
total es al menos **1 punto menor** y su error individual **no es mayor**.
- **H1:** B mejora a A. Los datos reales de la vida ayudan.
- **H2:** C mejora a B. El resumen ayuda.
- **H3:** D **no** mejora a A. Inventar no ayuda.

**Útil para preguntas políticas:** la variante con menor error del total es útil si cumple las tres reglas de la prueba
anterior:
- error individual menor que la constante;
- error del total menor que la página;
- TVD de 0,15 o menos.

## 6. Predicciones

- **PQ1.** H1 se cumple: los datos de la vida ayudan.
- **PQ2.** H2 no se cumple: el resumen no agrega mucho sobre B.
- **PQ3.** H3 se cumple, y D es peor que A: inventar empeora.
- **PQ4.** La mejor variante es útil para preguntas políticas, porque en las de gobierno el perfil de opiniones dice mucho.

## 7. Gasto y código

**Llamadas:**
- 200 personas × 4 variantes;
- 400 llamadas extra para C y D;
- unas 10 de la página.

**En total,** unas 1.200 llamadas a Luna: cerca de USD 0,50, con tope de USD 2.

**Datos:** al modelo van perfiles de la EPC, pública y anónima, como antes. No se sube nada individual.

**Código:** `src/experiments/personas_politica.py`, con su prueba. Resultados en `PERSONAS_POLITICA_RESULTS.md`.
