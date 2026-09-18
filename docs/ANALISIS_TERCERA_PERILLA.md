# ¿Es una sola la tercera perilla? — Resultados

Proyecto: Bogotá Social Simulator
Versión: 1.0
Fecha: 17 de septiembre de 2026
Reporta contra: `claude/ANALISIS_TERCERA_PERILLA_SPEC.md` (pre-registrada antes de correr)
Código: `src/experiments/tercera_perilla.py`

---

> ## ⚠ Nota de revocación — 17 de septiembre de 2026, misma tarde
>
> **§5 queda revocada: no hay tercera perilla, ni derivada ni declarada.**
>
> Este análisis terminó pidiendo "un modelo categórico que transporte masa sujeto a restricciones de momentos, que debería ganarle a los dos". Se construyó (`src/opinion/forzamiento_categorico.py`), y ganó por mucho más de lo previsto: **0,6808** en el objetivo A y **0,6789** en el B, contra 1,2171 del modelo tosco de ±1 y 2,3132 del afín con ruido. En la ECP llega a 0,1788, **por debajo del piso de ruido**.
>
> Con el forzamiento correcto, la forma no se declara ni se deriva del nivel: **sale sola**. Las dos descripciones de la "tercera perilla" que este documento probó que eran distintas —forma-desde-el-nivel y ancho de difuminado— resultaron ser **parches del mismo error de especificación**.
>
> **Qué sigue en pie:** P1, P3 y el diagnóstico de §2 y §3 se confirmaron y son los que llevaron al arreglo. La conclusión de §3 —"respetar la grilla vale más que acertar el segundo momento"— es exactamente la pista correcta, y el módulo nuevo la lleva hasta el final acertando además los momentos.
>
> Ver `claude/FORZAMIENTO_CATEGORICO.md`.

---

## 1. Veredicto

| | Predicción | Resultado |
|---|---|---|
| **P1** — σ no necesita variar por periodo | PASA | **PASA** — ajustarlo por tramo mejora 2,2 % y 2,7 % (umbral 5 %) |
| **P2** — el ruido compensa la discretización · *la decisiva* | PASA | **PASA en el objetivo A, FALLA en el B** — y con un matiz que cambia su significado (§3) |
| **P3** — en la ECP el ruido aporta mucho menos | PASA | **PASA** — 3,6 % contra 13,2 % en la EPC |
| **P4** — la forma-desde-el-nivel sobrevive | PASA | **PASA** — 14,7 % de mejora |
| **P5** — σ y la forma NO son la misma perilla | PASA | **PASA, y de más: son super-aditivas** |

**Respuesta a la pregunta: no son la misma perilla, y una de las dos no es una perilla.**

- La **forma derivada del nivel** es real, reproduce, y hay que ponerla en el motor.
- El **σ del Experimento 7 no es un parámetro de escenario**: es el parche de un forzamiento mal especificado para una variable de cinco categorías. Con el forzamiento correcto desaparece — y el ajuste **mejora casi a la mitad**.

---

## 2. P1 · P3 — σ es una constante, y solo hace falta donde la escala es discreta

| | afín (2 par) | + σ global (3 par) | + σ por tramo | ganancia del ruido |
|---|---|---|---|---|
| EPC objetivo A — `GG3`, **5 categorías** | 2,6590 | **2,3132** (σ*=0,20) | 2,2615 | **13,0 %** |
| EPC objetivo B — diferencia, **9 categorías** | 2,2211 | **1,9220** (σ*=0,25) | 1,8698 | **13,5 %** |
| ECP — índice de confianza, **~150 valores** | 0,3135 | **0,3023** (σ*=0,05) | — | **3,6 %** |

Dos cosas se leen de golpe. **Ajustar σ por tramo casi no aporta** (2,2 % y 2,7 %): no es un parámetro que el escenario tenga que declarar periodo a periodo. Y **su utilidad depende de la granularidad de la escala**: en la ECP, cuyo índice promedia hasta 13 ítems y sale casi continuo, el σ óptimo cae a 0,05 y la ganancia a 3,6 %, menos de un tercio.

Eso es exactamente lo que predice la hipótesis de §2 del pre-registro: el baseline afín, con \(u \neq 0\), saca los picos enteros de la grilla; cualquier difuminado reduce la penalización en \(W_1\); y donde no hay grilla, no hay penalización que reducir.

## 3. P2 — confirmada en la dirección, con un matiz que la hace más interesante

Se probó un forzamiento **sobre la grilla**: cada agente sube o baja **un escalón** con probabilidad ajustada, y el soporte nunca sale de las categorías. Dos parámetros por tramo, igual que el baseline afín.

| | Objetivo A (5 categorías) | Objetivo B (diferencia, 9) |
|---|---|---|
| afín (2 par) | 2,6590 | 2,2211 |
| afín + ruido (3 par) | 2,3132 | **1,9220** |
| **categórico (2 par)** | **1,2171** | 2,7517 |
| *mejor modelo del Experimento 7* | *2,4260* | *2,0247* |

**En el objetivo A el modelo categórico deja el error a la mitad** — 47 % mejor que afín+ruido, 54 % mejor que el afín solo, y **la mitad del mejor de los 33 modelos del Experimento 7**. Con un parámetro menos.

**En el objetivo B pierde**, y la razón es sustantiva: la diferencia individual está fuertemente apilada en 0 (entre 43 % y 58 % de la masa), y un modelo de saltos de ±1 no puede reproducir un pico así — mover masa un escalón lo destruye. Además la diferencia no es una respuesta ordinal: sus "categorías" no son opciones de un cuestionario, son el resultado de una resta.

### El matiz, y hay que decirlo

**El modelo categórico no acierta los momentos.** El baseline afín los acierta por construcción (error 10⁻¹⁵ y 10⁻⁷); el categórico se queda corto en dispersión de forma sistemática:

| | error de media | error de sd |
|---|---|---|
| Objetivo A | −0,03 a +0,04 | **+0,05 a +0,17** |
| Objetivo B | −0,04 a +0,11 | **+0,27 a +0,69** |

Un modelo de saltos de ±1 tiene poca capacidad de contraer, y el recorte en los bordes añade varianza. Así que **la comparación no es apples-to-apples como la especificación suponía**: el categórico no gana "con los mismos dos grados de libertad", gana **a pesar de no alcanzar el objetivo de dispersión**.

Eso hace la lección más fuerte, no más débil:

> **Respetar la grilla vale más que acertar el segundo momento.** Contra un objetivo discreto, un modelo que se equivoca 0,17 en la desviación estándar pero mantiene el soporte en las categorías ajusta al doble de bien que uno que acierta la desviación exactamente y deja los picos entre enteros.

Y deja una tarea clara: el modelo categórico probado aquí es **el más tosco posible**. Uno que transporte masa entre categorías sujeto a las restricciones de momentos debería ganarle a los dos, y es lo que el motor de escenarios debería usar.

## 4. P4 · P5 — la forma derivada del nivel es real, y es otra cosa

Reproducción de `claude/ANALISIS_RESIDUO.md` §3, como control:

| | Este análisis | `ANALISIS_RESIDUO.md` |
|---|---|---|
| Varianza explicada por PC1 | **69,7 %** | 69,8 % |
| Correlación PC1 con la media | **−0,888** | −0,886 |

Reproduce. Y sobre la ECP, con las cuatro recetas en el mismo marco:

| Receta | \(W_1\) total | Mejora sobre A |
|---|---|---|
| **A** — dos momentos, forma promedio | 0,3135 | — |
| **B** — + forma derivada del nivel | 0,2674 | **14,7 %** |
| **C** — + ruido (σ*=0,05) | 0,3023 | 3,6 % |
| **D** — las dos | **0,2451** | **21,8 %** |
| *piso de ruido* | *0,1835* | |

**P5 pasa, y por más margen del pedido.** Si fueran la misma perilla, la segunda casi no aportaría sobre la primera. Lo que pasa es lo contrario: juntas ganan 21,8 % donde la suma de sus efectos individuales daría 18,3 %. **Son super-aditivas** — cada una ayuda a la otra.

La lectura: corregir la forma deja un residuo cuya parte fina el ruido alisa mejor que antes, y viceversa. No se solapan porque no describen lo mismo — una mueve la **asimetría** con el nivel, el otro alisa la **granularidad**.

## 5. Qué implica para el motor de escenarios

**Un escenario se declara con dos números por periodo: nivel y dispersión.** La tercera perilla no se declara:

1. **Forma** — se deriva del nivel con la relación de `ANALISIS_RESIDUO.md` §3. Es real, reproduce, y aporta ~15 %.
2. **Granularidad** — **no es una perilla**: es una propiedad del forzamiento. Si la variable es categórica, el forzamiento opera sobre la grilla y el problema desaparece; si es continua, no existía.

Eso responde la pregunta que bloqueaba la Fase 8: **dos números por periodo**, no tres. Y añade un requisito de diseño que no estaba: **el motor necesita dos modos de forzamiento**, uno para variables ordinales de pocas categorías (la mayoría de los ítems de encuesta) y otro para índices casi continuos.

## 6. Qué obliga a revisar del Experimento 7

Su control post-hoc sigue en pie: el ruido le ganaba a los mecanismos, así que el 8,8 % de ventaja no era influencia social. **Eso no cambia — se refuerza**, porque el modelo categórico les gana por mucho más (1,2171 contra 2,4260).

Lo que sí hay que corregir es la **interpretación** que se escribió ahí: se dijo que "lo que faltaba no era un mecanismo, era un término de dispersión en el baseline". Es más preciso decir que **lo que faltaba era un forzamiento que respetara la escala**. El término de ruido era el parche, no el arreglo.

Y queda una consecuencia incómoda que conviene no esconder: **los Experimentos 4 a 7 se corrieron con un forzamiento afín sobre variables que, en el caso de la EPC, son categóricas.** Eso no invalida sus veredictos —todos los modelos comparados sufrían el mismo problema, y los mecanismos perdían igual— pero sí significa que las magnitudes absolutas de \(W_1\) de esos experimentos están infladas, y que ninguno de ellos estaba midiendo contra el mejor baseline disponible.

---

*Reportado contra el pre-registro. Cuatro de cinco predicciones se cumplieron enteras y la quinta se cumplió en un objetivo y falló en el otro. El control de momentos de §3 se añadió después de ver el resultado de P2 y queda etiquetado como tal; su efecto es matizar la interpretación de la predicción que pasó, no la que falló.*
