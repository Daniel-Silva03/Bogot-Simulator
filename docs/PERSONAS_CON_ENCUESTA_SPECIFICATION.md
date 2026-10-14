# PERSONAS CON SU ENCUESTA — ¿responde bien un modelo de lenguaje como cada encuestado real, si conoce todas sus respuestas?

Pre-registro escrito el **14 de octubre de 2026**, antes de calcular nada y de llamar al modelo. Lo propuso Daniel: en vez de
que MiroFish o TinyTroupe se inventen a la persona, armarla con todo lo que esa persona respondió en la encuesta. Gasto:
**unos USD 0,15, con tope de USD 1**; falta su visto bueno.

## 1. Pregunta

**Lo que ya falló:**
- **El Experimento 8:** un modelo de lenguaje respondía como cada persona conociendo solo cuatro datos de ella. Se equivocó
  más que una constante y aplanó las respuestas (desviación estándar al 30 % de la real).
- **MiroFish y TinyTroupe:** se inventaban a la persona.

**Lo nuevo:** el agente conoce **unas 40 respuestas reales** de esa persona a la EPC 2025, más su sexo, edad, estrato y
localidad.

**¿Responde bien preguntas que esa persona respondió pero que el modelo no ve?** ¿Y su total se acerca más a Bogotá que la
estimación de la página?

## 2. Datos

**La muestra:** 200 encuestados de la EPC 2025, sorteados con la semilla **20261014**, sin mirar sus respuestas.

**El perfil de cada uno:**
- sus respuestas a las preguntas del catálogo que se juntan con 2025 (`verificacion_2025.csv`: «coincide» o «entra»), con el
  texto de la pregunta y la etiqueta de su respuesta;
- su sexo, edad, estrato y localidad;
- **nada más.** Sin identificador de ningún tipo.

**Las 6 preguntas escondidas:** de las 10 guardadas del lote 8, que no están en el catálogo y que la página ya estimó como
nuevas (`NIVEL_ACUERDO_CATALOGO_RESULTS.md` §3):

| # | Variable | Pregunta |
|---|---|---|
| E1 | `CON_4` | ¿Qué tanto confía en la Alcaldía de Bogotá? |
| E2 | `CON_5` | ¿Qué tanto confía en el Concejo de Bogotá? |
| E3 | `CON_7` | ¿Qué tanto confía en el Gobierno Nacional (la Presidencia)? |
| E4 | `GOB_7` | ¿Cómo califica la gestión del Congreso? |
| E5 | `MOV_6` | ¿Qué tan satisfecho(a) está con el estado de las vías vehiculares de Bogotá? |
| E6 | `FIN_3` | ¿Qué tanto confía en los servicios financieros digitales? |

Los textos y escalas son los de `banco_lote8.PREGUNTAS`. **Ninguna de las 6 está en el perfil.**

**Lo que se declara:**
- **Ya se conoce la cifra de Bogotá de estas 6** (`NIVEL_ACUERDO_LOTE8_RESULTS.md` §3) **y el error de la página en ellas:
  12,2 puntos**. No se conocen las respuestas de las 200 personas.
- **Mandar respuestas individuales al modelo es una decisión, no una regla:**
  - la EPC es pública y anónima, y no es del CNC: no la cubren R10 ni D21;
  - el Experimento 8 mandó solo cuatro datos por prudencia, con otra fuente;
  - aquí van unas 44 respuestas por persona, sin identificador.
- **Posible memorización:** la EPC 2025 es reciente. Si el modelo la hubiera visto, acertaría de más; se reporta y no se
  puede descartar del todo.

## 3. Los brazos

**Para cada persona y cada pregunta escondida:**
- **Agente (Luna):** recibe el perfil y las 6 preguntas con sus escalas, y responde como esa persona, una opción por pregunta.
  - una llamada por persona;
  - `openai/gpt-6-luna`, temperatura 1, como el Experimento 8, para no forzar a todos a la respuesta más probable;
  - razonamiento bajo.
- **Constante:** la media ponderada de los otros 1.320 encuestados de 2025.
- **Regresión (referencia, no disponible en la vida real):** para cada pregunta escondida, una regresión lineal sobre las
  mismas respuestas del perfil, entrenada con los otros 1.320 encuestados. Dice cuánto se puede adivinar con estos datos.
  Para una pregunta de verdad nueva no existiría, porque nadie la habría respondido.

**Para el total de Bogotá:** el porcentaje del lado favorable de cada brazo entre las 200, con `Factor1`, contra la cifra de
los 1.520. Se compara también con la estimación de la página.

## 4. Lo que se mide

En la escala de 0 a 100 de `PESO_ANIO_RECIENTE`, sin «no sabe»:
- **error individual:** la media de la diferencia absoluta por persona y pregunta;
- **error del total:** la media, sobre las 6, de la diferencia entre el porcentaje favorable del brazo y el de Bogotá;
- **aplanamiento:** la desviación estándar de las respuestas del brazo entre la real, por pregunta y en promedio.

## 5. Regla (escrita antes de calcular)

**Vale la pena seguir con agentes armados con su encuesta si se cumplen las tres:**
- **R1:** su error individual es **menor que el de la constante**.
- **R2:** su error del total es **menor que el de la página (12,2)**.
- **R3:** **no aplana:** la razón de desviaciones es de 0,6 o más (en el Experimento 8 fue 0,3).

**Si pasa,** lo siguiente sería otra prueba pre-registrada con preguntas de verdad nuevas, antes de tocar la página. **Si no
pasa,** queda descartado con esta fuente.

## 6. Predicciones

- **PP1.** R1 se cumple: con 40 respuestas reales, el agente sabe más que la constante.
- **PP2.** La regresión le gana al agente en error individual.
- **PP3.** R3 no se cumple: el agente aplana (razón menor de 0,6).
- **PP4.** No pasa la regla.

## 7. Gasto y código

- **Gasto:** 200 llamadas, cada una con un perfil de unas 44 respuestas: unos USD 0,15, con tope de USD 1.
- **No se suben:** las respuestas del agente y la caché. La EPC es pública, pero son 200 perfiles individuales.
- **Código:** `src/experiments/personas_con_encuesta.py`, con su prueba. Resultados en `PERSONAS_CON_ENCUESTA_RESULTS.md`.
