# REFORMULACIÓN — SPECIFICATION

**Cuando alguien escribe una pregunta, la página le sugiere una versión que el simulador pueda responder bien, o le dice que no hay con qué.**

Proyecto: Bogotá Social Simulator
Versión: 0.1 — **pre-registro** de la validación
Fecha: 30 de septiembre de 2026
Estado: **código probado con un modelo simulado (`src/consulta/reformular.py`, 7 pruebas); sin ninguna llamada al modelo real**
Decisión que la origina: D17, pieza 3
Depende de: `POBLACION_EPC2023_SPECIFICATION.md` (el catálogo de 102 preguntas) y `PUENTE_RESULTS.md` (qué se puede responder y cómo)

---

## 1. Qué hace

Quien usa la página escribe lo que quiere saber, con sus palabras. Un modelo de lenguaje
recibe esa pregunta y el catálogo de 102 preguntas de la EPC 2023, y devuelve **una de
tres respuestas**:

| Alcance | Cuándo | Lo que la página hace después |
|---|---|---|
| **catálogo** | La pregunta ya la midió la encuesta (aunque esté dicha de otra forma) | Muestra el dato medido: ciudad, grupos y mapa por localidad con su margen |
| **nueva** | Es de opinión o de aprobación de un cambio en la ciudad, y no está medida | Muestra la versión reformulada; si quien pregunta la acepta, la responde con el puente: diferencias entre grupos y nivel propuesto, editable, **sin mapa** (`PUENTE_RESULTS.md`, lectura B) |
| **fuera** | No es de opinión ni de aprobación: un dato, una predicción electoral, intención de voto, lo que piensa una persona concreta, información sensible | Dice por qué, y si puede, sugiere una pregunta cercana que sí esté en el alcance |

**La reformulación de una pregunta nueva** sigue cuatro reglas: una sola idea por
pregunta, redacción neutral (sin inducir la respuesta), en el contexto de Bogotá, y una
escala de cinco puntos con sus etiquetas. **Quien pregunta siempre ve la versión
reformulada antes de que se responda, y puede editarla o rechazarla.**

**Todo lo que la página responde después es una suposición**, y lo dice (D17).

### 1.1 Lo que el modelo recibe y lo que no

Recibe la pregunta tal como se escribió y el catálogo (código, texto, etiquetas). **No
recibe datos de personas ni cifras de la encuesta**, igual que el puente. La pregunta de
quien usa la página se guarda solo en la caché local de la consulta.

---

## 2. Formato de la respuesta del modelo

```json
{"alcance": "catalogo" | "nueva" | "fuera",
 "codigo": "VS8" o null,
 "reformulada": "texto de la pregunta, o de la alternativa sugerida si es fuera",
 "escala": ["...", "...", "...", "...", "..."],
 "razon": "una frase"}
```

Es **inválida** si: no es JSON; el alcance no es uno de los tres; con alcance
`catalogo` el código no está en el catálogo; con alcance `nueva` no trae una
reformulada de 1 a 300 caracteres y exactamente cinco etiquetas. Una respuesta inválida
se le muestra a quien pregunta como «no pude reformular esta pregunta», nunca como una
respuesta.

---

## 3. La validación: 24 preguntas de prueba, escritas antes de cualquier llamada

Redactadas como las escribiría alguien que no conoce la encuesta. El alcance y el código
esperados se fijan aquí.

**Ocho que ya están en el catálogo, dichas de otra forma:**

| # | Pregunta de prueba | Esperado |
|---|---|---|
| 1 | ¿La gente se siente segura caminando por su barrio? | catálogo, `VS8` |
| 2 | ¿Qué tan contentos están los bogotanos de vivir en la ciudad? | catálogo, `CV1` |
| 3 | ¿La gente cree que la corrupción ha aumentado? | catálogo, `GG7` |
| 4 | ¿Cómo califica la gente la gestión del alcalde? | catálogo, `GG3` |
| 5 | ¿Están satisfechos con la recolección de basuras? | catálogo, `SP4` |
| 6 | ¿Qué piensan de la calidad del aire en Bogotá? | catálogo, `MA3_1` |
| 7 | ¿Las cosas en la ciudad van por buen camino? | catálogo, `AG1` |
| 8 | ¿Qué tan orgullosos se sienten de Bogotá? | catálogo, `AG2` |

**Diez de opinión o aprobación de un cambio, que no están medidas:**

| # | Pregunta de prueba | Esperado |
|---|---|---|
| 9 | ¿Estarían de acuerdo con cobrar por entrar en carro al centro? | nueva |
| 10 | ¿Apoyarían extender el pico y placa a todo el día? | nueva |
| 11 | ¿Les gustaría que el metro funcionara las 24 horas? | nueva |
| 12 | ¿Aprobarían subir el predial para pagar más policías? | nueva |
| 13 | ¿Estarían de acuerdo con prohibir las motos en las ciclorrutas? | nueva |
| 14 | ¿Apoyarían volver peatonal toda la carrera séptima? | nueva |
| 15 | ¿Qué opinan de poner más cámaras de vigilancia en los parques? | nueva |
| 16 | ¿Estarían a favor de cerrar los bares a medianoche? | nueva |
| 17 | ¿Les parecería bien hacer más ciclorrutas aunque se quiten carriles a los carros? | nueva |
| 18 | ¿Apoyarían un toque de queda para menores de edad? | nueva |

**Seis fuera de alcance:**

| # | Pregunta de prueba | Esperado | Por qué |
|---|---|---|---|
| 19 | ¿Por quién van a votar para la alcaldía? | fuera | intención de voto |
| 20 | ¿Cuántos habitantes tiene Bogotá? | fuera | un dato, no una opinión |
| 21 | ¿Qué piensa mi vecino Carlos de la alcaldía? | fuera | una persona concreta |
| 22 | ¿Cuánto cuesta el pasaje de TransMilenio? | fuera | un dato |
| 23 | ¿Cuántas personas en Suba tienen VIH? | fuera | dato sensible de salud |
| 24 | ¿Va a ganar Abelardo las elecciones? | fuera | predicción electoral |

---

## 4. Criterios

Una llamada por pregunta, temperatura 0, el mismo modelo del puente
(`xiaomi/mimo-v2.6-pro`). 24 llamadas; costo estimado por debajo de USD 0,05.

| # | Criterio | Umbral |
|---|---|---|
| **R1** | El alcance es el esperado | al menos **20 de 24** |
| **R2** | En las 8 del catálogo, el código es el esperado | al menos **6 de 8** |
| **R3** | Las fuera de alcance se detectan | al menos **5 de 6**, y **ninguna** clasificada como catálogo |
| R4 | La respuesta es válida (§2) | al menos 23 de 24 |

**Además, sin umbral:** se leen las diez reformulaciones de preguntas nuevas y se anota
si alguna es tendenciosa, junta dos ideas o cambia el sentido de lo preguntado.

**Regla:**
- **R1 a R4 se cumplen** → la reformulación entra a la página como está.
- **Falla alguno** → se ajusta la instrucción al modelo, con enmienda fechada, y se
  vuelve a validar con **otras 24 preguntas nuevas**, no con estas: ajustar la
  instrucción mirando estas y volver a medirla con ellas sería hacer trampa.

---

## 5. Límites, dichos antes

- **24 preguntas escritas por quien diseñó la prueba.** Las de la gente real serán más
  variadas y peor redactadas. La prueba dice si la regla funciona con casos claros.
- **«Catálogo» con el código equivocado es un error que se nota poco:** la página
  mostraría el dato de otra pregunta. Por eso R2 se mide aparte, y la página muestra
  siempre el texto de la pregunta del catálogo que usó.
- **Neutralidad:** se revisa leyendo, no con una cifra.

---

## 6. Qué se construye después de este documento

1. `src/consulta/reformular.py` y `tests/test_reformular.py`, con un modelo simulado.
2. Las 24 llamadas reales (con confirmación de gasto) y `REFORMULACION_RESULTS.md`, contra
   este documento.
