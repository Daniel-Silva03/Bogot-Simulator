# PUENTE — SPECIFICATION

**¿Puede la población EPC 2023 «responder» una pregunta que no conoce, a partir de las respuestas reales que sí tiene, mejor que la demografía y que el azar?**

Proyecto: Bogotá Social Simulator
Versión: 0.1 — **pre-registro**
Fecha: 30 de septiembre de 2026
Estado: **sin código y sin ninguna correlación entre preguntas de la EPC calculada.** Lo único visto de la EPC 2023 es el inventario (qué preguntas existen, cuántas respuestas tienen y cuántas personas por localidad), no sus valores
Decisión que la origina: D17, piezas 2 y 5
Población: `POBLACION_EPC2023_SPECIFICATION.md`

---

## 1. La pregunta

D17 propone responder una pregunta nueva con un **puente**: un modelo de lenguaje elige
qué preguntas medidas se relacionan con la nueva y en qué sentido, y cada agente
responde a partir de **sus propias respuestas** a esas preguntas. Así, la variedad
entre personas y localidades sale de los datos y no del modelo, que es lo que falló en
el Experimento 8.

Que funcione no está probado. Esta prueba lo decide con **preguntas cuya respuesta se
conoce**: se esconden, se le hacen al puente como si fueran nuevas y se compara con lo
que respondió la gente real.

> **¿El puente reconstruye una pregunta escondida —quién está más de acuerdo, en qué
> localidades y en qué nivel— mejor que la demografía sola y que un puente al azar?**

---

## 2. Lo que ya sé antes de empezar

- **El inventario de la EPC** (`DATA_INVENTORY.md` §13.8): textos, años, conteos.
- **No he calculado ninguna media, distribución ni correlación** de las preguntas de
  2023, ni por localidad.
- **Conocimiento general:** en Bogotá la inseguridad y la corrupción se perciben alto,
  y la satisfacción con la ciudad suele ser media. Es lo mismo que sabe el modelo de
  lenguaje, y es la razón de la advertencia de §8 sobre el nivel.

---

## 3. Las 12 preguntas escondidas (fijadas aquí)

Todas existen en 2023, escala 1-5, y todas se esconden **a la vez**: ningún puente
puede usar ninguna de las 12.

| Código | Pregunta |
|---|---|
| `CV1` | Satisfacción con Bogotá |
| `AG2` | Orgullo de Bogotá |
| `VS8` | Percepción de seguridad en el barrio |
| `VS10` | Percepción de seguridad en la ciudad |
| `GG7` | Percepción de la corrupción |
| `GG3` | Gestión del alcalde |
| `MV4` | Satisfacción con su modo de transporte |
| `SA4` | Satisfacción con los servicios de salud |
| `MA3_1` | Calidad del aire |
| `MA3_3` | Nivel de ruido |
| `CR2` | Oferta cultural |
| `CO2` | Situación económica del hogar |

Cubren ciudad, seguridad, gobierno, movilidad, salud, ambiente, cultura y economía.
El catálogo que el puente puede usar son las otras **103** preguntas generales de 2023
(§4 de la especificación de la población).

---

## 4. El puente

**Lo que recibe el modelo de lenguaje:** el texto de la pregunta escondida con sus
etiquetas de respuesta, y el catálogo (código, texto y etiquetas de las 103). **Nunca
recibe datos de personas ni cifras de la encuesta.**

**Lo que devuelve** (JSON validado):
- de 1 a 5 preguntas del catálogo, cada una con un **sentido** (+ o −, referido a los
  códigos de la escala) y un **peso** (1, 2 o 3);
- el **nivel** que propone: la media esperada en la escala de la pregunta escondida.

**Cómo responde cada persona:** cada pregunta del puente se estandariza (media 0,
desviación 1, ponderadas por `FEXP`); el puntaje es la suma de esas respuestas por su
sentido y su peso. Una respuesta «no sabe» cuenta como 0 (la media). El puntaje ordena
a las personas; el nivel lo pone la propuesta.

**Modelo:** el mismo de `donante_llm.py` (OpenRouter, se registra el modelo que
atendió cada llamada, DI-E9). Temperatura 0. **Tres llamadas por pregunta**; cada
métrica se calcula para las tres y se usa la **mediana**. Costo estimado: 36 llamadas,
unos centavos de dólar.

---

## 5. Cómo se mide

Todo sobre los **1.501 encuestados de 2023** (los donantes), ponderados por `FEXP`: la
población de agentes son copias de ellos y no agrega información a esta prueba.

| Cifra | Qué es |
|---|---|
| **ρ_ind** | Correlación de Spearman ponderada entre el puntaje y la respuesta real a la pregunta escondida, por persona |
| **r_loc** | Pearson entre las medias por localidad del puntaje y las medias reales, en 19 localidades |
| **e_nivel** | Error del nivel: \|media propuesta − media real\| / (máx − mín de la escala) |

**Las líneas base:**

| Línea base | Qué es |
|---|---|
| **Demografía** | Regresión ponderada de la pregunta escondida sobre sexo, tramo de edad, estrato y educación, **con validación cruzada de 5 partes** (se ajusta con 4/5 y se predice el otro quinto). Es lo que haría una población por composición, con la ventaja de ajustarse a la respuesta real |
| **Azar** | 200 puentes al azar: de 1 a 5 preguntas del catálogo, sentido y peso al azar. Se toma el percentil 95 de cada cifra |
| **Nivel ingenuo** | La posición media de las 103 preguntas del catálogo, cada una llevada a 0-1 y con la dirección «favorable» arriba según sus etiquetas: el «tono general» de Bogotá en 2023 |

---

## 6. Predicciones pre-registradas

| # | Predicción | Umbral |
|---|---|---|
| **P1** | **El puente ordena a las personas** | ρ_ind > percentil 95 del azar **y** > demografía, en **al menos 9 de las 12** |
| **P2** | **El puente ordena las localidades** | r_loc > demografía, en **al menos 8 de las 12** |
| P3 | El sentido es el correcto | ρ_ind > 0 en al menos 11 de las 12 |
| **P4** | **El nivel propuesto es mejor que el tono general** | e_nivel < el del nivel ingenuo, en **al menos 8 de las 12** |

**Por qué espero esto.** P1 porque las actitudes se parecen entre sí mucho más que a la
demografía: quien se siente inseguro en el barrio suele sentirse inseguro en la ciudad.
P2 es más difícil: con 80 personas por localidad, las medias reales tienen ruido, y la
demografía captura bien el gradiente del estrato. P4 es la más incierta: el Experimento
9 mostró que un LLM no fija bien los números de un escenario.

---

## 7. Regla de decisión

```
    Sobre el orden (P1, P2):
    A. P1 y P2 → Las preguntas nuevas se responden con el puente, con mapa por
                 localidad, rotulado como suposición.
    B. P1 sin P2 → El puente ordena personas pero no localidades: para preguntas
                 nuevas la página muestra diferencias entre grupos (estrato, edad),
                 y el mapa solo para preguntas del catálogo.
    C. Sin P1 → El puente no sirve: la página responde solo preguntas del catálogo.

    Sobre el nivel (P4), por separado:
    · P4 → El nivel por defecto es el que propone el modelo, rotulado y editable.
    · Sin P4 → El nivel lo fija quien pregunta (por defecto, el tono general), como
               dice el Experimento 9: los números los pone una persona.
```

P3 se reporta siempre. Si falla en más de una pregunta, se revisa el formato de las
etiquetas antes de leer lo demás.

---

## 8. Límites, dichos antes

- **El nivel puede venir de la memoria del modelo.** BCV publica sus resultados de 2023,
  y el modelo pudo leerlos: el Experimento 9 encontró que acierta donde recuerda. **Un
  P4 cumplido no prueba que el modelo sepa proponer el nivel de una pregunta nueva**;
  por eso, aun con P4, el nivel queda editable. El orden (P1, P2) es mucho menos
  memorizable: nadie publica correlaciones entre preguntas.
- **Las preguntas escondidas son de la misma encuesta y el mismo año.** Una pregunta
  realmente nueva («¿apoyaría cobrar por entrar en carro al centro?») puede estar más
  lejos del catálogo que cualquiera de estas 12. La prueba dice si el puente funciona
  cuando hay preguntas parecidas; no cuando no las hay.
- **80 personas por localidad**: r_loc tiene un techo por ruido. Se reporta, sin
  decidir, la confiabilidad de las medias por localidad (dos mitades al azar de los
  encuestados, 200 veces).
- **La línea base demográfica está favorecida**: se ajusta a la respuesta real. Si el
  puente le gana, le gana a lo mejor que puede hacer la composición.
- **La reformulación sugerida (D17, pieza 3) no se prueba aquí.**

---

## 9. Qué se construye después de este documento

1. La población (`POBLACION_EPC2023_SPECIFICATION.md`), verificada.
2. `src/experiments/puente.py` y `tests/test_puente.py`, con un modelo de lenguaje
   simulado y dos mundos inventados: uno donde la pregunta escondida es la suma de dos
   del catálogo (el puente correcto tiene que ganar) y uno donde es ruido (nada gana).
3. La corrida real (36 llamadas) y `PUENTE_RESULTS.md`, **contra este pre-registro**.
