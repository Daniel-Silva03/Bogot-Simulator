# REFORMULACIÓN — RESULTS

**24 de 24: la reformulación clasifica bien las preguntas de prueba y entra a la página. Las reformulaciones de preguntas nuevas salen neutrales; las alternativas que sugiere para lo que está fuera de alcance, no siempre.**

Proyecto: Bogotá Social Simulator
Versión: 0.1
Fecha: 30 de septiembre de 2026
Pre-registro: `docs/REFORMULACION_SPECIFICATION.md` (commit `45eebf4`; código en `0b3ed7a`, antes de la corrida)
Código: `src/consulta/reformular.py` · Pruebas: `tests/test_reformular.py` (7)
Salida: `data/processed/reformulacion/resultado.json`
Gasto: **24 llamadas, USD 0,081**, las 24 atendidas por `xiaomi/mimo-v2.6-pro`

---

## 1. Contra el pre-registro

| # | Criterio | Umbral | Resultado | |
|---|---|---|---|---|
| R1 | El alcance es el esperado | ≥ 20 de 24 | **24 de 24** | se cumple |
| R2 | En las del catálogo, el código es el esperado | ≥ 6 de 8 | **8 de 8** | se cumple |
| R3 | Las fuera de alcance se detectan, ninguna como catálogo | ≥ 5 de 6, 0 | **6 de 6, 0** | se cumple |
| R4 | Respuesta válida | ≥ 23 de 24 | **24 de 24** | se cumple |

**Regla: la reformulación entra a la página como está.**

Las ocho del catálogo las encontró aunque estaban dichas de otra forma («¿qué tan
contentos están los bogotanos de vivir en la ciudad?» → `CV1`, satisfacción con Bogotá
como lugar para vivir). Las seis fuera de alcance las detectó con la razón correcta:
intención de voto, dato demográfico, persona concreta, precio, dato sensible de salud,
predicción electoral.

---

## 2. La lectura de las diez reformulaciones (sin umbral, §4)

**Las diez son neutrales:** todas preguntan «qué tan de acuerdo o en desacuerdo» (o
«favorable u opuesto»), con escala equilibrada de cinco puntos y punto medio. Ninguna
cambia el sentido de lo preguntado.

Dos observaciones:
- **Dos preguntas originales ya traían dos ideas** y la reformulación las conserva como una
  propuesta con su costo: «subir el predial *para* pagar más policías» y «más ciclorrutas
  *aunque* se quiten carriles». Es fiel a lo que se preguntó: la pregunta es justamente por
  el intercambio. Se deja así; la página puede advertir que la respuesta es por el paquete
  completo.
- **Las etiquetas de la escala varían** entre preguntas («Muy» o «Totalmente de acuerdo»;
  «favorable / opuesto»). Todas son escalas válidas de cinco puntos; la página puede
  unificarlas al mostrarlas.

---

## 3. Lo que no está bien: las alternativas para lo que está fuera de alcance

La instrucción pide, para una pregunta fuera de alcance, «si existe, una pregunta cercana
que sí sea de opinión». El modelo siempre sugirió una, y **no todas son buenas**:

| Pregunta | Alternativa sugerida | Problema |
|---|---|---|
| ¿Cuántos habitantes tiene Bogotá? | ¿Cómo cree que ha afectado el crecimiento de la población la calidad de vida…? | supone que la afectó; no es neutral |
| ¿Cuántas personas en Suba tienen VIH? | ¿Qué tan de acuerdo está con que la ciudad realiza acciones suficientes…? | pide acuerdo con una afirmación favorable (sesgo de aquiescencia) |
| ¿Va a ganar Abelardo…? | ¿Qué tan satisfecho está con el rumbo…? | dice que es `AG1`, pero no es el texto de `AG1` |

Las de intención de voto, el vecino y el pasaje sí son razonables (llevan a la gestión del
alcalde o a la satisfacción con la tarifa).

**Qué se hace (no estaba en los criterios, así que no cambia el resultado):** en la página,
**una alternativa sugerida no se responde directamente.** Si quien pregunta la elige, pasa
otra vez por la reformulación como pregunta nueva, y así recibe la redacción neutral y su
escala, o su código del catálogo. Es un cambio de flujo, no de instrucción.

---

## 4. Lo que este resultado NO dice

- **Que funcione igual con preguntas reales.** Las 24 las escribió quien diseñó la prueba:
  son casos claros. Las de la gente serán más ambiguas (por ejemplo, «¿qué opinan del
  metro?», que puede ser satisfacción o aprobación).
- **Que el puente responda bien estas preguntas nuevas.** La reformulación solo prepara la
  pregunta; la respuesta sigue teniendo los límites de `PUENTE_RESULTS.md` (ordena
  personas, no localidades; nivel editable). Y estas diez están más lejos del catálogo que
  las doce escondidas de esa prueba.

---

## 5. Consecuencias

1. **La reformulación entra a la página**, con el cambio de flujo de §3 para las
   alternativas.
2. **Con esto están las tres piezas que responden una pregunta:** la población (dato del
   catálogo), el puente (pregunta nueva) y la reformulación (de la pregunta escrita a una de
   las dos). Lo siguiente es unirlas en una consulta de punta a punta y llevarla a la
   página.
