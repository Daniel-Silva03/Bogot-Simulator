# PUENTE — RESULTS

**El puente ordena a las personas mucho mejor que la demografía y que el azar, en las 12 preguntas. Las localidades no: lectura B. Y la razón principal es que, con 80 personas por localidad, la propia encuesta casi no tiene geografía que se pueda reproducir.**

Proyecto: Bogotá Social Simulator
Versión: 0.1
Fecha: 30 de septiembre de 2026
Pre-registro: `docs/PUENTE_SPECIFICATION.md` (commit `9b75bac`, enmienda 1 en `0e7bceb`; código en `9f8a5a9` y `93e6128`, todo antes de la corrida)
Código: `src/experiments/puente.py` · Pruebas: `tests/test_puente.py` (11)
Salida: `data/processed/puente/resultado.json`
Gasto: **36 llamadas, USD 0,051**, las 36 atendidas por `xiaomi/mimo-v2.6-pro`. La corrida se hizo en dos tandas: la primera se cayó en la llamada 22 por un error de OpenRouter que el cliente no leía (corregido en `93e6128`); las 21 anteriores quedaron en la caché y no se repitieron.

---

## 1. Resultado, en una línea

Con el puente, el orden de las personas se parece al real con ρ entre 0,23 y 0,66
(mediana 0,44); la demografía da entre −0,03 y 0,31 (mediana 0,04). Por localidad, el
puente le gana a la demografía en 7 de 12 y hacían falta 8. El nivel propuesto le gana
al tono general en 8 de 12, justo el umbral. **Regla: B en el orden; nivel del modelo,
editable.**

---

## 2. La tabla

ρ_ind y r_loc son la mediana de las tres llamadas. «Azar 95» es el percentil 95 de 200
puentes al azar. «Conf. loc» es la correlación de las medias por localidad entre dos
mitades al azar de los encuestados (descriptiva, §8 del pre-registro).

| Pregunta | ρ_ind | azar 95 | demo | r_loc | demo | conf. loc | e_nivel | tono |
|---|---|---|---|---|---|---|---|---|
| Satisfacción con Bogotá (`CV1`) | **0,43** | 0,27 | 0,05 | **0,53** | 0,41 | 0,11 | **0,054** | 0,141 |
| Orgullo de Bogotá (`AG2`) | **0,36** | 0,21 | −0,01 | **0,60** | 0,31 | 0,32 | **0,059** | 0,147 |
| Seguridad en el barrio (`VS8`) | **0,31** | 0,25 | 0,06 | **0,50** | 0,42 | 0,47 | 0,098 | 0,060 |
| Seguridad en la ciudad (`VS10`) | **0,41** | 0,26 | 0,05 | **0,32** | 0,05 | 0,15 | **0,064** | 0,102 |
| Corrupción (`GG7`) | **0,23** | 0,13 | 0,05 | **0,24** | 0,09 | 0,15 | 0,091 | 0,084 |
| Gestión del alcalde (`GG3`) | **0,66** | 0,28 | 0,04 | 0,49 | 0,53 | 0,14 | 0,015 | 0,002 |
| Satisfacción con su transporte (`MV4`) | **0,29** | 0,21 | −0,02 | 0,08 | 0,30 | 0,17 | **0,133** | 0,145 |
| Servicios de salud (`SA4`) | **0,44** | 0,22 | 0,03 | 0,34 | 0,58 | −0,08 | **0,084** | 0,147 |
| Calidad del aire (`MA3_1`) | **0,55** | 0,33 | −0,03 | **0,45** | 0,00 | 0,18 | **0,041** | 0,072 |
| Nivel de ruido (`MA3_3`) | **0,53** | 0,30 | 0,01 | 0,32 | 0,35 | 0,03 | **0,129** | 0,142 |
| Oferta cultural (`CR2`) | **0,47** | 0,24 | 0,04 | 0,62 | 0,68 | 0,26 | **0,133** | 0,170 |
| Situación económica del hogar (`CO2`) | **0,47** | 0,21 | 0,31 | **0,52** | 0,31 | 0,24 | 0,031 | 0,007 |

En negrita, donde el puente cumple el criterio de su columna.

---

## 3. Contra el pre-registro

| # | Predicción | Umbral | Resultado | |
|---|---|---|---|---|
| **P1** | El puente ordena a las personas | ρ_ind > azar 95 y > demografía, en ≥ 9 de 12 | **12 de 12** | se cumple |
| **P2** | El puente ordena las localidades | r_loc > demografía, en ≥ 8 de 12 | **7 de 12** | **no se cumple** |

> **Anotación (30/09, después; `PUENTE_LOCALIDADES_RESULTS.md` §4).** Este r_loc se calcula con el
> puntaje y la respuesta real de las mismas personas. Cuando el puente acierta por persona, el ruido
> de muestreo de las medias por localidad sale igual en los dos lados y sube r_loc sin que haya
> geografía; a la demografía casi no le pasa. Los 7 de 12 tienen ese sesgo a favor del puente (no se
> recalcularon). La lectura B no cambia: con el sesgo ya no alcanzaba.
| P3 | El sentido es el correcto | ρ_ind > 0, en ≥ 11 de 12 | 12 de 12 | se cumple |
| **P4** | El nivel propuesto es mejor que el tono general | e_nivel < tono, en ≥ 8 de 12 | **8 de 12** | se cumple, **justo** |

**Regla de decisión:**
- **Orden: B.** *El puente ordena personas pero no localidades: para preguntas nuevas, la
  página muestra diferencias entre grupos (estrato, edad…), y el mapa solo para preguntas
  del catálogo.*
- **Nivel:** *el nivel por defecto es el que propone el modelo, rotulado y editable.*

35 de las 36 respuestas del modelo fueron válidas; una de ruido (`MA3_3`) no se pudo usar y
contó como puente vacío (DI-PU3). Con temperatura 0, las tres llamadas de una misma pregunta
no dieron el mismo puente: el modelo no es determinista en OpenRouter.

---

## 4. Lo que el resultado precisa: las localidades casi no tienen señal medible

**Descriptivo; la cifra estaba pre-registrada para reportarse sin decidir.** La
confiabilidad de las medias por localidad (dos mitades de la muestra, 200 veces) tiene
**mediana 0,16**, y va de −0,08 a 0,47. Con la corrección de Spearman-Brown, que estima lo
que daría la muestra entera, la mediana sube a unos 0,28. Es decir: **si se repitiera la
EPC 2023 con otras 80 personas por localidad, el orden de las localidades en una pregunta
cualquiera cambiaría casi por completo.**

Eso explica el fallo de P2 mejor que cualquier defecto del puente: se compara con un
blanco que es sobre todo ruido. En las preguntas donde la encuesta sí tiene algo de
geografía (seguridad en el barrio, 0,47; orgullo, 0,32), el puente le gana a la
demografía. Donde no tiene casi nada (salud, −0,08; ruido, 0,03), gana o pierde por azar.

**Y tiene una consecuencia que va más allá del puente:** el mapa de **una pregunta del
catálogo** con una sola ola también es, sobre todo, ruido. La regla B dice «el mapa solo
para preguntas del catálogo»; con esta cifra, ese mapa tiene que mostrar su margen de forma
muy visible, o juntar olas (§7).

---

## 5. Lo que dice el nivel

P4 pasa por el mínimo (8 de 12), y la advertencia de §8 del pre-registro se sostiene: el
modelo pudo recordar resultados publicados por Bogotá Cómo Vamos. Donde más acierta es en
la gestión del alcalde (propone 2,8, la real es 2,86) y la situación del hogar, que son de
las cifras más publicadas; donde más falla es en el transporte y la oferta cultural (propone
~2,9-3,0 donde la real es 3,4-3,5). **Por eso el nivel queda editable, como dice la regla,
y la página tiene que decir de dónde sale.**

---

## 6. Lo que este resultado NO dice

- **No dice que el puente funcione con una pregunta realmente nueva.** Las 12 escondidas
  son de la misma encuesta y siempre tenían preguntas vecinas en el catálogo (el aire
  tenía al agua, los árboles y las basuras). Una pregunta como «¿apoyaría cobrar por
  entrar en carro al centro?» puede estar más lejos de todo.
- **No dice que las localidades no difieran en la realidad.** Dice que 80 personas por
  localidad no alcanzan para medir esas diferencias con precisión, en una sola ola.
- **Nada sobre personas reales individuales:** el puntaje ordena en promedio (ρ ≈ 0,44),
  no dice qué respondería alguien en particular.

---

## 7. Consecuencias

1. **Para la página (D17):** una pregunta nueva se responde con el puente mostrando
   **diferencias entre grupos** (estrato, edad, sexo, educación), con el nivel propuesto por
   el modelo como suposición editable. **El mapa por localidad queda para las preguntas del
   catálogo**, con su margen muy visible.
2. **Para el mapa, la vía de mejora es de datos, no de modelo:** juntar varias olas de la
   EPC (2022-2025 dan unas 300 personas por localidad) para las preguntas que se repiten.
   Es una decisión para después, y cambiaría la población (una sola ola hoy).
3. **La reformulación sugerida** (D17, pieza 3) sigue sin probar; el siguiente paso de
   producto puede ser construirla sobre este puente.
