# EXPERIMENT 9 — RESULTS

**¿Puede un LLM proponer el escenario de un periodo mejor que suponer que nada cambia? No. Acierta donde recuerda, y el dossier no ayuda.**

Proyecto: Bogotá Social Simulator
Versión: 0.1
Fecha: 29 de septiembre de 2026
Pre-registro: `docs/EXPERIMENT_9_SPECIFICATION.md` (v0.1 del 28/09, enmiendas 1 a 5, todas anteriores a cualquier respuesta del modelo en los brazos)
Modelo: `xiaomi/mimo-v2.6-pro` vía OpenRouter; brazos a temperatura 0,7 y sonda a 0
Llamadas: 20 de sonda + 242 de brazos; **12 × 2 × 10 respuestas válidas**, sin huecos
Costo: USD 0,177 medido en los brazos (la sonda es anterior al registro de costo; es menor)
Código y datos: `src/experiments/experimento9.py`, `data/processed/exp9/veredicto.json`

---

## 1. Resultado, en una línea

La regla de decisión falla desde el primer criterio en los dos brazos: la mediana
de W1/piso del brazo B es **5,17** contra **5,78** de «sin cambio», y hacía falta
bajar de 4,63. La cobertura de sus intervalos del 90 % es del **50 %**. Fuera de
memoria, el brazo B es **peor** que «sin cambio» (6,03 contra 5,92). Y el brazo sin
dossier (A, 4,72) queda por delante del brazo con dossier (B, 5,17). **El LLM no
fija los números de un escenario.**

---

## 2. La tabla

Mediana de W1/piso sobre las transiciones de cada serie, con el rango entre paréntesis.

| fuente | total (12) | ECP (4) | EPC (8) |
|---|---|---|---|
| oráculo | **0,96** (0,25–1,29) | 1,16 | 0,77 |
| **brazo A** — memoria propia | 4,72 (0,85–14,10) | 3,19 | 5,34 |
| **brazo B** — con dossier | 5,17 (0,77–15,66) | 3,60 | 5,90 |
| sin cambio | 5,78 (1,69–8,20) | 4,46 | 5,98 |
| tendencia *(10)* | 6,82 (1,18–14,35) | 5,88 | 7,78 |

Por transición:

| transición | A | B | sin cambio | tendencia | oráculo | Δ observado | Δ propuesto (B) | memoria |
|---|---|---|---|---|---|---|---|---|
| ECP 2013→2017 | 4,58 | 4,65 | 6,57 | — | 0,50 | −0,31 | −0,12 | |
| ECP 2017→2019 | 1,79 | 2,10 | 3,28 | 5,88 | 1,20 | −0,14 | −0,09 | **sí** |
| ECP 2019→2021 | 1,13 | 2,56 | 2,59 | 1,18 | 1,11 | −0,12 | −0,20 | **sí** |
| ECP 2021→2023 | 7,21 | 6,03 | 5,65 | 7,77 | 1,24 | +0,19 | +0,02 | |
| EPC 2014→2015 | 6,72 | 6,82 | 8,01 | — | 0,87 | −0,44 | −0,07 | |
| EPC 2015→2017 | 14,10 | 15,66 | 5,92 | 2,67 | 1,05 | −0,30 | **+0,50** | |
| EPC 2017→2018 | 4,85 | 5,69 | 4,85 | 10,47 | 0,66 | +0,26 | −0,05 | |
| EPC 2018→2019 | 5,83 | 6,11 | 3,36 | 1,84 | 0,29 | +0,18 | −0,15 | |
| EPC 2019→2022 | 3,35 | 3,99 | 7,09 | 4,16 | 1,17 | +0,41 | +0,23 | |
| EPC 2022→2023 | 1,15 | 2,22 | 1,69 | 9,08 | 1,29 | −0,09 | −0,14 | |
| EPC 2023→2024 | 0,85 | 0,77 | 6,03 | 7,78 | 0,25 | +0,32 | +0,32 | **sí** |
| EPC 2024→2025 | 6,76 | 6,28 | 8,20 | 14,35 | 0,51 | −0,43 | −0,10 | |

El oráculo en 0,96× el piso reproduce lo que midió `FORZAMIENTO_CATEGORICO.md`
(0,97×): la tubería de evaluación está bien.

---

## 3. Contra el pre-registro

### 3.1 Las predicciones (el pre-registro juzga el brazo B)

| # | Predicción | Umbral | Brazo B | ¿se cumple? | Brazo A |
|---|---|---|---|---|---|
| P1 | Acierta la dirección | signo en ≥ 8 de 11 | 8 de 11 | **sí**, justo en el umbral | 7 de 11 — no |
| P2 | Le gana a «sin cambio» | mediana < la de «sin cambio» | 5,17 < 5,78 | **sí** | 4,72 < 5,78 — sí |
| P3 | Pero no a «tendencia» por un margen material | mejora < 20 % | mejora del 29 % | **no** | 40 % — no |
| P4 | No predice la dispersión | error mediano ≥ el de «sin cambio» | 0,057 ≥ 0,056 | **sí** | 0,036 < 0,056 — no |
| P5 | Está sobreconfiado | cobertura del 90 % < 70 % | 50 % | **sí** | 42 % — sí |
| P6 | Lo que gana, lo gana por memoria | fuera de memoria no le gana a «sin cambio» | 6,03 ≥ 5,92 (9 transiciones) | **sí** | 5,83 < 5,92 — no |

Cinco de seis se cumplen en el brazo B. **Cómo leer las que se cumplen está en §3.3:
dos de ellas son más débiles de lo que parecen.**

### 3.2 La regla de decisión (§5)

| Criterio | Brazo B | Brazo A |
|---|---|---|
| 1. mediana ≤ 0,8 × «sin cambio» (4,63) **y** ≤ 0,9 × «tendencia» en las 10 comunes (6,14) | 5,17 y 4,84 → **falla** | 4,72 y 4,10 → **falla** (por 0,09) |
| 2. cobertura ≥ 70 % | 50 % → **falla** | 42 % → **falla** |
| 3. fuera de memoria, no peor que «sin cambio» | 6,03 > 5,92 → **falla** | 5,83 ≤ 5,92 → pasa |

**Veredicto, tal como lo fijó §5: falla 1. El LLM no aporta números. Se puede usar
para redactar la descripción de un escenario, nunca para fijar sus cifras.**

Brazo A contra brazo B: A no solo iguala a B, lo supera en el total y en las dos
series. Por la regla de §5, **el dossier no aporta**, y leer un documento —la
idea de MiroFish— no es lo que explica lo poco que el modelo acierta.

### 3.3 Dos correcciones a mi propia expectativa

**P2 se cumple, pero no discrimina.** Antes de correr se midió que un proponente
que no sabe nada le gana a «sin cambio» en el 55 % de las semillas (enmienda 5).
El control por permutación lo confirma sobre las respuestas reales: repartir las
mismas propuestas del modelo entre otros periodos de la misma serie da una
mediana igual o mejor que la del brazo **en el 39 % de las permutaciones** (brazo
B; 25 % en el A). Con *p* = 0,39 y 0,25, la lectura pre-registrada es literal:
**la ventaja del brazo sobre «sin cambio» no se distingue de proponer las mismas
cifras en otro periodo.** Ninguna permutación del brazo A y el 0,05 % de las del
B habrían pasado la regla completa.

**P3 falla, pero por el baseline, no por el modelo.** Esperaba que «tendencia»
fuera una heurística razonable, difícil de superar. Es lo contrario: es **peor que
«sin cambio»** (6,82 contra 5,78). La opinión en estas dos series no persiste de un
periodo al siguiente, y repetir el último cambio suele ir en contra del siguiente.
Superar a «tendencia» por un 29 % no dice nada a favor del modelo. La expectativa
equivocada es mía y queda escrita así.

**Y P6 se sostiene por poco.** Fuera de memoria, el brazo B pierde contra «sin
cambio» por 0,11 de W1/piso y el brazo A gana por 0,09. Con la sensibilidad no
pre-registrada (unión de las dos sondas, 6 transiciones fuera de memoria), los dos
brazos se invierten: B gana por 0,09 y A pierde por 0,50. **Lo robusto no es el
signo de P6 sino su tamaño:** fuera de memoria, ningún brazo se separa de «sin
cambio» en más de medio piso en ninguna de las dos definiciones.

---

## 4. Qué hace el modelo en su lugar

**Acierta donde recuerda.** Las tres transiciones marcadas «en memoria» son de
las mejores del brazo B: 2,10, 2,56 y **0,77** (EPC 2023→2024, donde propone
+0,32 y se observó +0,32). En las nueve fuera de memoria, la mediana es 6,03. En
signo: 3 de 3 en memoria, 5 de 8 fuera.

**Aplana los cambios grandes.** Las cuatro caídas o subidas mayores de la EPC
(−0,44, −0,43, +0,41, −0,30) las propone de −0,07, −0,10, +0,23 y **+0,50**. Es el
mismo patrón del Experimento 8 en otra escala: el modelo tiende a la
estabilidad.

**Y cuando se aleja del cero, puede ser en la dirección equivocada.** El peor
caso de todo el experimento es EPC 2015→2017: el modelo propone +0,50 (brazo B;
+0,42 en el A) y la calificación del alcalde cayó 0,30. W1/piso de 15,7, casi el
triple que no proponer nada. *Hipótesis, no verificada:* el modelo aplica el
relato de «luna de miel de un alcalde nuevo» (Peñalosa asumió en 2016) a una
transición que la encuesta no registró así. Las justificaciones están en la caché
para quien quiera verificarlo.

**La dispersión no la mueve.** Propone cambios de ±0,02 a ±0,06; los observados
van de −0,13 a +0,18. Su error mediano es el de «sin cambio» (brazo B) o algo
menor (brazo A, 0,036 contra 0,056). La cobertura de dispersión es alta (83 %)
porque los intervalos, de ±0,1, son anchos frente a cambios de ese tamaño; no
porque el modelo sepa algo de la dispersión.

**Sobreconfianza en el nivel.** Cobertura del 50 % (B) y 42 % (A) con intervalos
declarados del 90 %; por repetición, 53 %. P5 se cumple con margen.

---

## 5. Cómo corrió

- **Sonda:** 3 de 12 transiciones «en memoria» con la regla pre-registrada (ECP
  2017→2019, ECP 2019→2021, EPC 2023→2024). La complementaria de BCV, no
  pre-registrada, marca además 3 de la EPC.
- **Una advertencia sobre la sonda de la ECP:** el modelo respondió casi lo mismo
  en los cuatro años (2,28 a 2,38) contra observados de 2,25 a 2,50. Sus dos
  «memorias» en la ECP parecen una cifra fija que cae cerca, no un recuerdo. La
  marca se mantuvo, porque la regla está pre-registrada y el error va en la
  dirección conservadora para P6.
- **Fallos:** 6 de 246 intentos en los brazos. Dos respuestas llegaron cortadas
  (el JSON se interrumpe en la justificación) y cuatro fueron errores del
  proveedor sin contenido. Todos se descartaron y se reemplazaron con otra
  repetición; las 24 combinaciones de transición y brazo tienen 10 válidas.
- **Ninguna propuesta** cayó fuera de lo alcanzable en la escala: cero
  proyecciones.
- **Modelo servido:** `xiaomi/mimo-v2.6-pro` en las 242 llamadas de los brazos,
  atendidas por el proveedor GMICloud (registrado desde DI-E9). Las 20 de la
  sonda son anteriores a ese registro: solo consta el modelo pedido.

---

## 6. Lo que este resultado NO dice

- **No dice nada de otros modelos.** Es un modelo, el mismo del Experimento 8 por
  comparabilidad. Un modelo más grande podría recordar más —lo que según P6
  tampoco serviría para escenarios nuevos— o razonar mejor; este experimento no
  lo distingue.
- **No dice que ningún documento sirva.** Dice que *este* dossier no sirvió: 15
  hechos elegidos por una regla mecánica sobre la cronología nacional de
  Wikipedia, con muchos conciertos y festivales y pocos hechos de gobierno
  (limitación registrada en la enmienda 3). Un dossier escrito por un analista
  sería otra pregunta, y más difícil de hacer limpia, porque el analista conoce
  los resultados.
- **Doce transiciones son pocas.** Por eso el pre-registro no pidió pruebas de
  significancia, y por eso P1 en el umbral exacto y P6 por 0,11 no deben leerse
  como hallazgos.
- **No dice que el modelo no sepa nada de Bogotá.** Acierta direcciones cuando la
  historia es conocida. Lo que no hace es convertir eso en los dos números del
  motor mejor que no hacer nada.

---

## 7. Consecuencias

1. **Los números de un escenario los sigue escribiendo una persona.** El motor
   de escenarios no incorpora al LLM como proponente de cifras. Queda permitido,
   por la rama de §5, usarlo para redactar la descripción de un escenario, con
   las cifras puestas por otra vía.
2. **Para MiroFish**, las dos partes del enfoque quedan medidas en este proyecto:
   el LLM como personas (Experimento 8: aplana personas, exagera instituciones) y
   el LLM que lee un documento y propone lo que viene (Experimento 9: no supera
   a suponer que nada cambia, y el documento no ayuda).
3. **Un hallazgo que sirve fuera de este experimento:** «tendencia» es peor que
   «sin cambio» en las dos series. Para cualquier escenario que se escriba a
   mano, **extrapolar el último cambio es peor supuesto por defecto que no
   suponer ninguno.**
4. **El control por permutación (enmienda 5)** debería acompañar a cualquier
   experimento futuro que compare una propuesta contra «sin cambio» sobre pocas
   transiciones: sin él, P2 se habría leído como un acierto.
