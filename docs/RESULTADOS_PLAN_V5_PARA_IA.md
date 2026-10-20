# Resultados del plan v5 del predictor de Bogotá — para la IA que lo propuso

**Fecha:** 20 de octubre de 2026
**Contexto:** de tu plan v5 (`PLAN_SIGUIENTE_PREDICTOR_BOGOTA_V5.md`) se hicieron los dos pasos que recomendaste primero: **congelar la
prueba hacia adelante con la EPC 2026** y **el diagnóstico del alcalde sin nombre.** La corrección del sesgo queda en espera, como
propusiste. Las dos líneas aparte (preguntas ocultas en la misma ola y paso de lo nacional a Bogotá) no se tocaron.

No trae cifras de las encuestas políticas propias. Todo es de la Encuesta de Percepción Ciudadana (EPC), pública.

---

## 1. Resumen en cinco líneas

1. **Las predicciones para la EPC 2026 están congeladas** y subidas con fecha (20/10/2026), antes de que exista la encuesta. Se
   evalúan en diciembre.
2. **Los agentes casi no se mueven de lo medido en 2025:** para Galán dicen 27 % (2025: 26,4 %).
3. **El diagnóstico del alcalde sin nombre no apoya ni el pesimismo ni el valor central:** quitar el nombre mueve la cifra 2 puntos,
   y cada agente repite lo que su persona respondió en 2025.
4. **Tu lectura corrigió la mía,** y quedó anotado: «castigan al alcalde» era de más. Pero tu hipótesis del valor central tampoco se
   sostuvo en esta prueba.
5. **Queda sin explicar** por qué en la réplica (por ejemplo, con López en 2023) los agentes sí se alejaron de la respuesta de su
   persona, y aquí no.

---

## 2. Decisiones de producto, que siguen

- **En las preguntas del alcalde ya medidas,** la cifra principal es la de los agentes.
- **No se muestra al lado la medición anterior.**
- **La página siempre da una cifra.**
- **Los agentes están encendidos con el modelo real,** como experimento declarado.
- **No se hace el texto de cobertura del rango** (Paso 3 del plan v4).

---

## 3. Paso 2 — La prueba hacia adelante con la EPC 2026 (congelada)

**Pre-registro:** `PROSPECTIVA_EPC2026_SPECIFICATION.md`, subido antes de llamar al modelo. **Costo:** USD 0,254.

**Diseño:**
- **7 preguntas:** gestión del alcalde, rumbo, corrupción, Concejo, transparencia, respuesta y participación.
- **P, persistencia:** el dato de la EPC 2025.
- **G, la principal:** el método de la Fase B y de la réplica del alcalde.
  - Los 200 agentes de la página, con perfiles de la EPC 2025 y sus pesos.
  - Una llamada por agente con las 7 preguntas, más la nota «las respuestas de arriba son de 2025; estas preguntas son de finales de
    2026: la persona puede haber cambiado de opinión».
  - Es el único método que sirve para las 7: el de la página solo acepta escalas de 5 opciones, y el rumbo tiene 2.
- **Página, la secundaria:** lo que vería quien usa la página, en las 4 preguntas de Galán que solo responden los agentes. Va sin
  nota.
- **Lo congelado** (`config/prospectiva_epc2026/`):
  - fecha y hora, modelo y versión, temperatura y razonamiento;
  - la semilla y las 200 personas;
  - la nota y la huella sha256 del mensaje de sistema y de los perfiles;
  - las predicciones.

  El código se niega a correr si ya existen.

**Las reglas, como las propusiste:**
- **RV1:** los agentes se equivocan al menos 1 punto menos que la persistencia en las preguntas que cuenten.
- **RV2:** lo mismo sin la pregunta del alcalde.
- **Si ganan solo en el alcalde,** el informe usa tu frase textual.
- **Antes de calcular nada en diciembre** se revisa el cuestionario de 2026: sale cualquier pregunta que cambie de concepto, de
  opciones o de alcalde. Con menos de 4 preguntas comparables, se informa por pregunta, sin reglas.

**Las predicciones congeladas:**

| Pregunta | P (2025) | G | Página |
|---|---|---|---|
| Gestión de Galán | 26,4 | 27,3 | 27,2 |
| Buen camino | 48,2 | 40,9 | — |
| Corrupción aumentó | 50,6 | 53,8 | — |
| Concejo | 14,9 | 19,6 | — |
| Transparencia | 9,9 | 19,9 | 14,3 |
| Respuesta a la ciudadanía | 6,9 | 18,6 | 14,0 |
| Participación | 10,6 | 17,8 | 15,0 |

**Lo que se ve:**
- **En Galán, G y P casi coinciden:** en la parte de la prueba que más importa, los agentes apuestan a que no cambia.
- **En transparencia, respuesta y participación, G va 7 a 12 puntos arriba de P.** Es el mismo sesgo hacia arriba que tuvieron en
  esas tres en 2025, cuando cayeron a la mitad.
- **En el rumbo, G va 7 puntos abajo.**

**Predicciones pre-registradas** (se juzgan en diciembre):
- **PP1:** los agentes no ganan.
- **PP2:** su cifra del alcalde queda entre 25 y 35 % (sí: 27,3).

---

## 4. Paso 3 — El alcalde sin nombre (hecho)

**Pre-registro:** `ALCALDE_SIN_NOMBRE_SPECIFICATION.md`. **Costo:** USD 0,043.

**Diseño:**
- **A:** la pregunta de la página, «¿Usted cómo califica la gestión del alcalde de Bogotá, Carlos Fernando Galán?».
- **B:** la misma, sin el nombre.
- **Lo demás es igual:** los mismos 200 perfiles de la EPC 2025, la escala de 5, el modelo y la temperatura, sin nota.
- **Declarado:** el perfil ya trae la respuesta de la persona en 2025 a «¿cómo califica la gestión del alcalde/sa?», sin nombre.

**Resultados:**

| | Buena o muy buena |
|---|---|
| A, con nombre | 27,2 % |
| B, sin nombre | 25,1 % |
| Las mismas 200 personas en la EPC 2025 | 25,8 % |

| Seguimiento (probabilidad de «buena») | Antes la calificó bien | Antes no | Diferencia |
|---|---|---|---|
| A | 80,2 | 8,6 | 71,6 |
| B | 85,2 | 4,6 | 80,6 |

**Lectura pre-registrada:**
- **El nombre no mueve la cifra:** 2,1 puntos, menos de 5.
- **Los agentes siguen su propia respuesta:** el seguimiento es mayor de 60.
- **No hay valor central:** las cifras quedan cerca de la del panel, no lejos.
- **No hay pesimismo:** A no queda por debajo de B ni del panel.

**Predicciones:** PN1 (el nombre no mueve) se cumple; PN2 (seguimiento menor de 60) **falla**.

---

## 5. Lo que se aprende

1. **Cuando el perfil trae la misma pregunta, los agentes hacen una persistencia persona por persona.** Por eso, en el alcalde, la
   página da casi lo mismo que la EPC 2025.
2. **Lo que el modelo sabe de Galán pesa poco:** 2 puntos.
3. **Ni tu hipótesis del valor central ni la mía del pesimismo** explican esta prueba.
4. **Queda una contradicción sin explicar:**
   - En la réplica del alcalde, con López (2022 → 2023), el perfil traía la respuesta de la persona y los agentes la bajaron 8
     puntos.
   - Aquí, con Galán y su respuesta en el perfil, no se mueven, con nota de fecha (G) y sin ella (página).
   - **Diferencias entre las dos:**
     - la persona, la ola y el alcalde;
     - en 2022 la respuesta se agregó al final del perfil, con el texto «la alcaldesa de Bogotá, Claudia López», y en 2025 viene
       con el texto original de la encuesta, «alcalde/sa»;
     - en la réplica iban 4 preguntas en la llamada, y aquí 7 (G) o 1 (página).

   No se probó nada más: haría falta un pre-registro nuevo.
5. **Para el producto:** la cifra de Galán en la página viene sobre todo de lo que esas personas respondieron en 2025. Hoy la página
   no lo dice.

---

## 6. Lo que te pido ahora

1. **La contradicción del punto 5.4:** ¿qué prueba barata (menos de USD 0,20) la separaría? Por ejemplo, poner la respuesta de 2022
   con el texto original, o cambiar el número de preguntas por llamada. ¿Vale la pena, o es un detalle que no cambia ninguna
   decisión?
2. **Si los agentes repiten la respuesta de 2025 en las preguntas medidas,** ¿qué aportan en la página frente a mostrar el dato
   medido? ¿Qué debería decir la página sobre esto, respetando que la cifra principal siga siendo la de los agentes?
3. **Para preguntas nuevas sobre Galán** (por ejemplo, sobre una decisión de esta semana), el perfil no trae la misma pregunta.
   ¿Cómo evaluarías ese caso, que es el uso real de la página, sin esperar a diciembre?
4. **Hasta diciembre,** ¿hay algo que valga la pena hacer, o lo correcto es esperar a la EPC 2026?

**Restricciones que siguen:**
- pre-registro antes de correr;
- la persistencia como vara;
- nada de respuestas individuales de las encuestas propias a ningún modelo de lenguaje;
- presupuesto chico (200 agentes, unos USD 0,05 por pregunta);
- las decisiones de producto de §2;
- las predicciones congeladas para 2026 no se tocan.
