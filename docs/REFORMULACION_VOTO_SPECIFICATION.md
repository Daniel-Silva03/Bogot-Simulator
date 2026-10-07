# LA REFORMULACIÓN RECONOCE LA INTENCIÓN DE VOTO

Pre-registro escrito el **7 de octubre de 2026**, antes de hacer ninguna llamada. Gasto: **~USD 0,04, con tope de USD 0,15**.
Lo pidió Daniel tras la aprobación jurídica de D21: que la página reconozca sola las preguntas de voto («la reconoce sola»).

## 1. Qué cambia

Hoy la reformulación (`reformular.SISTEMA`, validada en `REFORMULACION_RESULTS.md`) clasifica en «catálogo», «nueva» o
«fuera», y pone la intención de voto en «fuera».

**La versión 2 (`SISTEMA_V2`) agrega un cuarto alcance, «voto»,** para la intención de voto **presidencial** en Bogotá. Lo
que cubre lo validó el nivel 3 (`VOTO_SIMULADO_RESULTS.md`):
- **primera vuelta:** «¿votaría por X?»;
- **segunda vuelta:** «¿quién ganaría entre A y B?»;
- **«nunca votaría por X»;**
- **la probabilidad de votar.**

**Con alcance «voto», la respuesta trae:**
- **el `tipo`:** «primera», «segunda», «nunca» o «participacion»;
- **los `candidatos` nombrados:** uno, o dos en segunda vuelta;
- **la `reformulada`,** como pregunta de encuesta neutral.

**Siguen «fuera», con su razón:**
- **las consultas interpartidistas y la tendencia** (izquierda o derecha): en la validación del nivel 3 su error fue de 11 a 23
  puntos;
- **otras elecciones** (alcaldía, Congreso): no hay encuestas en el banco;
- **el resultado nacional** como cifra;
- **lo de siempre:** datos, personas concretas, información sensible.

Todo lo demás de la versión 1 sigue igual.

**El modelo** es `openai/gpt-6-luna` (DI-CO26).

## 2. La prueba

**40 preguntas**, escritas antes de llamar (`reformular.PRUEBA_VOTO`):
- **las 24 de la validación original,** con una sola expectativa cambiada: «¿Va a ganar Abelardo las elecciones?» pasa de
  «fuera» a «voto», primera vuelta, Abelardo de la Espriella. «¿Por quién van a votar para la alcaldía?» sigue «fuera»;
- **12 de voto,** con su tipo y sus candidatos;
- **4 electorales que deben quedar «fuera»:** una consulta, una tendencia, el Congreso y el Concejo.

**En total:** 8 del catálogo, 10 nuevas, 9 «fuera» y 13 de voto.

## 3. Regla

**La versión 2 entra a la página si se cumplen las seis condiciones:**
1. **R1:** alcance correcto en ≥ 36 de 40;
2. **R2:** código correcto en ≥ 6 de las 8 del catálogo;
3. **R3:** «fuera» en ≥ 8 de las 9 que lo esperan, y ninguna como catálogo;
4. **R4:** respuesta válida en ≥ 39 de 40;
5. **R5:** de las 13 de voto, «voto» en ≥ 12, y con el tipo y los candidatos correctos en ≥ 11. Un candidato es correcto si
   trae su primer nombre y su apellido;
6. **R6:** ninguna pregunta que no es de voto queda como «voto».

**Si no se cumplen,** la página sigue con la versión 1 y la intención de voto no se muestra. Se ajusta la instrucción con
enmienda fechada y se valida con preguntas nuevas.

## 4. Predicciones

- **PRV1.** La versión 2 cumple la regla.
- **PRV2.** Falla a lo sumo en una pregunta de voto.

## 5. Gasto y código

- **Gasto:** 40 llamadas a ~USD 0,0009: unos USD 0,04, con tope de USD 0,15.
- **Código:** `src/consulta/reformular.py` (`SISTEMA_V2`, `parsear_v2`, `PRUEBA_VOTO`, `evaluar_voto`, `--validar-voto`).
- **Pruebas:** `tests/test_reformular.py`.
- **Resultados:** `REFORMULACION_VOTO_RESULTS.md`.

## 6. Enmienda 1 (7/10/2026, después de la primera validación): versión 3

La versión 2 no cumplió R5: reconoció 11 de 13 preguntas de voto (`REFORMULACION_VOTO_RESULTS.md`). Las dos fallas vienen de
la instrucción, que mandaba «fuera» el resultado de una elección y las cifras.

**La versión 3 (`SISTEMA_V3`) cambia solo esas dos líneas:**
- también es «voto» preguntar cuánta gente o qué porcentaje votaría, o nunca votaría, por un candidato;
- también es «voto» preguntar si un candidato «va a ganar» o «ganaría». Se responde como intención de voto en Bogotá y así se
  dice en la reformulada;
- «fuera» queda para las cifras que no son intención de voto: población, precios, resultados oficiales ya publicados.

**Se valida con preguntas nuevas, como pide §3** (`PRUEBA_VOTO_V3`):
- **las 24 originales,** para ver que nada se rompa, con «¿va a ganar Abelardo?» como voto, que ahora sí corresponde;
- **16 electorales nuevas:** 12 de voto, que incluyen las formas que fallaron («cuántos», «va a ganar», «qué porcentaje»), y 4
  que deben quedar «fuera». Ninguna repite las 16 de la versión 2.

**En total:** 8 del catálogo, 10 nuevas, 13 de voto y 9 «fuera». La regla (§3) no cambia. **Gasto:** unas 40 llamadas, ~USD
0,04. Lo ya gastado (USD 0,037) cuenta dentro del tope de USD 0,15.
