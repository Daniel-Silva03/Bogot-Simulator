# Resultados del plan de mejoras del predictor de Bogotá — para la IA que lo propuso

**Fecha:** 19 de octubre de 2026
**Contexto:** tu plan (`PLAN_MEJORAS_PREDICTOR_BOGOTA.md`, v1.0) se siguió fase por fase. Este documento cuenta qué se hizo, qué
salió y qué se apartó del plan, para que propongas los siguientes pasos.

No trae cifras de las encuestas políticas propias: por la restricción del proyecto, sus resultados no salen del equipo. De ellas
solo van errores, sin sesgo.

---

## 1. Resumen en cinco líneas

1. **La persistencia (repetir el último dato comparable) ganó en todo lo que se midió:** a los agentes, a las combinaciones y a
   los métodos temporales sencillos.
2. **La combinación persistencia + λ·(agentes − persistencia) aprendió λ = 0** en 81 preguntas con años reservados.
3. **Ningún método temporal sencillo le ganó a la persistencia,** ni en la encuesta anual ni en series bimestrales o mensuales.
4. **Los agentes solo ganan en dos casos:** cuando la pregunta se esconde dentro de la misma ola de encuesta, y cuando la única
   referencia es una encuesta de otra población (nacional frente a Bogotá).
5. **El error de la persistencia depende de la antigüedad del dato,** no del método: unos 3 puntos con el mes anterior y de 4 a 7
   con un año. Los intervalos aprendidos con el pasado no cubrieron un año movido.

---

## 2. Fase A — Benchmark único (hecha, sin costo)

Se juntaron 290 predicciones de 12 pruebas previas en una tabla única: problema A (pregunta ya medida) frente a B (nunca medida),
por dominio y método. Se agregó un benchmark nuevo de persistencia en la encuesta anual (EPC 2022-2025): **144 pares
pregunta-año, 73 preguntas.**

**Persistencia anual en la EPC:**

| | Pares | Error medio | Mediana |
|---|---|---|---|
| 2022 → 2023 | 63 | 3,2 | 2,5 |
| 2023 → 2024 | 50 | 4,7 | 3,2 |
| 2024 → 2025 | 31 | 6,1 | 5,2 |
| **Total** | **144** | **4,3** | **3,2** |

**Por dominio:**
- espacio público, 2,7; servicios, 2,9; ambiente, 3,4; economía y hogar, 3,5; movilidad, 4,0; seguridad, 4,2;
- cultura ciudadana, 4,9; ciudad en general, 6,4;
- **gobierno e instituciones, 7,0: lo más movedizo.**

**Los cambios más grandes:**
- el orgullo por la ciudad, +18 en 2023;
- respeto en cultura ciudadana, +15 a +17 en 2024;
- **la gestión del alcalde, −16 en 2025;**
- la transparencia de su gobierno, −13 en 2025.

Varios coinciden con cambios de cuestionario.

**Todos los métodos, por problema:**

| Problema | Dominio | Método | Preguntas | Error medio |
|---|---|---|---|---|
| A, ya medida | gobierno | persistencia (EPC del año anterior) | 19 | 7,2 |
| A | gobierno | agentes | 8 | 8,6 (sesgo +6) |
| A | gobierno | agentes + resumen de noticias | 5 | 10,1 (sesgo +10) |
| B escondida (misma ola) | gobierno | **agentes** | 10 | **7,4-7,8** |
| B escondida | gobierno | estimación por regresión | 10 | 14,3 |
| B nunca medida | movilidad (metro) | regresión / agentes | 5 | 19,6 / 22,8-28,3 |
| B nunca medida | política nacional | agentes | 7 + 5 | 9,0-11,6 / 14,8 |
| B nunca medida | varios | regresión | 74 | 12,5 |
| Voto, 1.ª vuelta | — | **copiar la encuesta de Bogotá** / agentes + resumen + encuesta | 11 candidatos | **1,8** / 3,5 |
| Voto, 2.ª vuelta | — | **agentes + encuesta nacional** / copiar la nacional / decir 50 % | 1 | **3,4** / 7,5 / 3,6 |

---

## 3. Fase B — Selector y combinador (hecha; **no pasó**)

**Diseño (pre-registrado):**
- Agentes de la EPC del año base (200, con todas sus respuestas, incluida la suya del año base a la pregunta objetivo) predicen
  todas las preguntas medidas en el año siguiente.
- Dos pares: 2023 → 2024 (50 preguntas) y 2024 → 2025 (31).
- C = P + λ(G − P), con λ en una rejilla de 0 a 1, elegido en un par y evaluado en el otro.
- Cd: un λ para gobierno y otro para lo demás.
- Costo: USD 0,69.

**Resultados:**

| | 2023 → 2024 | 2024 → 2025 | Juntos | Gobierno |
|---|---|---|---|---|
| **P, persistencia** | **4,70** | **6,09** | **5,23** | **7,89** |
| G, agentes | 5,75 | 8,33 | 6,73 | 9,03 |
| C, λ único | 4,70 | 6,14 | 5,25 | 7,96 |
| Cd, λ por dominio | 4,70 | 6,59 | 5,42 | 9,23 |

**Lo que se aprende:**
- **λ elegido:** 0 y 0,05; con los dos pares, 0.
- **Cd aprendió λ = 0,95 en gobierno** con las pocas preguntas de 2023 → 2024, y en 2025 empeoró gobierno de 7,9 a 9,2. Es
  exactamente el riesgo de reglas falsas que advertías.
- **La única casilla donde los agentes ganaron:** cultura ciudadana (17 preguntas, 6,1 contra 6,9). Sin regla pre-registrada; no
  se usa.

---

## 4. Fase C — Modelo conjunto de relaciones (aplazada)

No se hizo. Un modelo factorial o de factorización aprende de quienes respondieron cada pregunta: **frente a una pregunta que
nadie respondió no puede dar su nivel** (el porcentaje de la ciudad). Solo serviría para repartir por grupos y localidades una
cifra ya conocida. Quedó aplazada para después.

---

## 5. Fase D — Modelo temporal (hecha; **no pasó**)

**Diseño (pre-registrado, sin nada que ajustar).** Predecir cada medición con al menos dos anteriores de su serie:
- **M0:** persistencia.
- **M1:** promedio de las dos últimas.
- **M2:** tendencia amortiguada (xₜ + 0,5·(xₜ − xₜ₋₁)).
- **M3:** encogimiento (0,5·xₜ + 0,5·media).

**Las series:**
- EPC anual: 80 objetivos en 2024 y 2025;
- aprobación del alcalde en Invamer, bimestral, 2024-2025: 7 objetivos;
- imagen del alcalde en CB, mensual, 2026: 4 objetivos.

| | M0 | M1 | M2 | M3 |
|---|---|---|---|---|
| **EPC (80)** | **4,59** | 4,80 | 5,33 | 4,69 |
| EPC, gobierno | 6,26 | 6,79 | **5,86** | 6,36 |
| **Alcalde, Invamer + CB (11)** | 3,40 | 3,32 | 4,23 | 3,54 |
| Invamer (7) | **3,86** | 4,29 | 4,57 | 4,43 |
| CB (4) | 2,60 | **1,63** | 3,63 | 1,99 |

**Ninguno pasó la regla** (ganarle a M0 y seguir ganando sin los dos mejores casos). M1 ganó por 0,08 en las series del alcalde,
solo por dos casos.

**Lo que se ve:**
- En CB (mensual), promediar ayuda: parece ruido que se devuelve.
- En Invamer (bimestral), los cambios se quedan.
- En gobierno de la EPC ganó la tendencia, sin regla por dominio.

Todo con muy pocos casos.

---

## 6. Fase E — Experimentos con agentes (no hecha)

No se hizo: calibración de probabilidades, tamaño del panel ni resultados electorales como auxiliar. Con λ = 0 en la Fase B, no
prometía mucho para su costo.

---

## 7. Fase F — Incertidumbre (hecha)

Error por tipo de evidencia, con todas las pruebas:

| Clase | Casos | Error medio | Percentil 80 |
|---|---|---|---|
| Dato del mes anterior | 4 | 2,6 | — |
| Dato de dos meses antes | 7 | 3,9 | — |
| Dato de un año antes, gobierno | 14 | 7,0 | 10,6 |
| Dato de un año antes, lo demás | 130 | 4,0 | 6,8 |
| Agentes, política nunca medida | 17 | 11,3 | 19,5 |
| Agentes, ciudad nunca medida (metro) | 5 | 22,8 | — |
| Regresión, política nunca medida | 9 | 12,3 | 20,9 |
| Regresión, ciudad nunca medida | 79 | 13,0 | — |

**Cobertura con un año reservado.** El percentil 80 aprendido con 2022-2024, probado en 2025:
- gobierno: cubrió el **38 %** (8 preguntas);
- lo demás: el **65 %** (23 preguntas).

**2025 fue un año movido, y los intervalos del pasado se quedaron cortos.**

**En la página:**
- El dato medido dice su antigüedad y cuánto se equivoca como «cifra de hoy».
- Los agentes llevan su error y su rango por tema: ±19,5 en lo político, en vez del ±12,6 que venía de pruebas dentro de muestra.

**Lo que se dejó:**
- **Un registro de mediciones publicadas con fecha y fuente** (19 mediciones del alcalde, de cuatro encuestadoras).
- **No se hizo el registro de cada predicción** (§14 del plan): choca con una regla del producto, «cada consulta no deja rastro».

---

## 8. Decisiones de producto tomadas, incluso contra la evidencia

- **Los agentes están encendidos con el modelo real** como experimento declarado, con su error a la vista. Sus validaciones
  pre-registradas no pasaron.
- **En las cuatro preguntas del alcalde que la encuesta ya midió, responden solo los agentes, sin mostrar el dato medido.** Lo
  decidió el responsable del proyecto, aun sabiendo que repetir el dato acertó más (0,5 contra 1,4 en la imagen; λ = 0 en la Fase
  B).

---

## 9. Lo que se probó antes del plan y tampoco funcionó

- **Un resumen narrativo de noticias para los agentes** (EPC 2024 → 2025): 10,1 contra 7,7 de la persistencia. Movió poco y hacia
  el pesimismo.
- **Una instrucción de «no te alejes de la encuesta»:** sobrecorrigió (2.ª vuelta, de 3,4 a 15,2 de error).
- **Calibrar al total de la encuesta:** iguala el total, no mejora grupos y empeora fuera de muestra.
- **Más contexto en el perfil o mezclar modelos:** sin mejora en lo político.

---

## 10. Lo que te pido ahora

Con estos resultados:
1. **¿Qué harías distinto o después?** Propón de 3 a 6 pasos concretos, ordenados por lo que esperas que ayude, con cómo
   probarlos con lo que hay, su costo aproximado (200 agentes por pregunta cuestan unos USD 0,05) y qué los haría fallar.
2. **El objetivo sigue siendo acercarse a la cifra de hoy en preguntas políticas locales nuevas, sin esperar datos nuevos.**
   Si crees que con estos datos el techo es «la medición más reciente, más un intervalo honesto», dilo, y propón cómo sacarle el
   máximo a eso. Por ejemplo: cómo conseguir, ordenar y combinar mediciones recientes de varias encuestadoras.
3. **¿Vale la pena retomar la Fase C (reparto por grupos y localidades) o la Fase E?** ¿Con qué diseño?
4. **¿Cómo harías intervalos que cubran en años movidos,** con tan pocos casos?

**Restricciones que siguen:**
- **Pre-registro** antes de correr.
- **La vara es la persistencia.**
- **Las respuestas individuales de las encuestas propias no van a ningún modelo de lenguaje.**
- **Presupuesto chico.**
