# ¿Es una sola la tercera perilla? — especificación pre-registrada

Proyecto: Bogotá Social Simulator
Versión: 1.0
Fecha: 17 de septiembre de 2026
Estado: **pre-registro — escrito y guardado antes de correr**
Origen: `PROJECT_CONTEXT.md` §44 (i). Las tres perillas llegaron por dos caminos y la tercera no se describe igual en cada uno.
Código: `src/experiments/tercera_perilla.py` *(por escribir)*

---

## 1. La pregunta

Dos análisis independientes concluyeron que hacen falta **tres** parámetros y no dos. Pero describen el tercero distinto:

| | Qué dice el tercero | Sobre qué datos |
|---|---|---|
| `claude/ANALISIS_RESIDUO.md` §3 | **Forma derivada del nivel.** PC1 explica el 70 % de la deriva de forma y correlaciona r = −0,886 con la media. No es libre. | ECP (DANE) |
| `claude/EXPERIMENT_7_RESULTS.md` §4 | **Ancho de difuminado.** Un σ gaussiano ≈ 0,2-0,3, exógeno e independiente. | EPC (BCV) |

Si son lo mismo, el motor de escenarios toma **dos números por periodo** y el tercero se deriva. Si son dos cosas distintas, toma tres, y uno de ellos —el σ— **no tiene interpretación sustantiva**: habría que pedirle al usuario que declare "cuán difusa" quiere la distribución, que es difícil de justificar.

## 2. Un hecho que cambia las expectativas, y que verifiqué antes de escribir esto

Las dos series no tienen la misma estructura:

| | Valores distintos | Concentración en los 5 más frecuentes |
|---|---|---|
| Índice de confianza, ECP 2013 | **154** | 24,7 % |
| Índice de confianza, ECP 2023 | **146** | 33,8 % |
| `GG3` gestión del alcalde, EPC | **5** | 100 % |
| Diferencia individual, EPC | **9** | 100 % |

El índice de la ECP promedia hasta 13 ítems y sale **casi continuo**. Los ítems de la EPC son **una sola pregunta en cinco categorías enteras**.

Eso importa porque el baseline es una transformación **afín**: con \(u \neq 0\) mueve los cinco picos enteros fuera de la grilla y los deja ahí. Contra un objetivo que vive en los enteros, eso paga una penalización en \(W_1\) que **cualquier difuminado reduce**. Contra un objetivo casi continuo, no hay tal penalización.

**Hipótesis de trabajo: el σ del Experimento 7 no es una perilla de escenario, es una compensación de la discretización de la escala.** Y la forma-desde-el-nivel de la ECP sería otra cosa: deriva real de asimetría.

## 3. Predicciones

### P1 — σ no necesita variar por periodo
**Predicción: PASA.** Ajustar un σ por tramo no mejora más de **5 %** sobre un σ único para toda la corrida. *Confianza: alta* — en el Experimento 7 el σ ya era constante y ganó.

Si falla, σ sí es una perilla por periodo y hay que tratarla como tal.

### P2 — el ruido está compensando la discretización · **la decisiva**
**Predicción: PASA.** Un forzamiento que opera **sobre las categorías enteras** —cada agente sube o baja un escalón con cierta probabilidad, el soporte nunca sale de la grilla— iguala o supera a `afín + ruido` en los dos objetivos de la EPC, **con dos parámetros en vez de tres**.

Criterio: \(W_1\) total del modelo categórico ≤ el de `afín+ruido` con σ óptimo.

*Confianza: media-alta.* El modelo categórico tiene los mismos dos grados de libertad que el baseline afín (dos parámetros para media y desviación), así que si gana, gana **sin** el tercero.

### P3 — en la ECP el ruido aporta mucho menos
**Predicción: PASA.** La mejora relativa de añadir el σ óptimo al baseline será, sobre la serie de la ECP, **menos de un tercio** de la que da sobre la EPC. *Confianza: alta*, por el mismo argumento de §2.

### P4 — la forma-desde-el-nivel sobrevive
**Predicción: PASA.** Sobre la ECP, la receta "dos momentos + forma predicha por el nivel" seguirá mejorando sobre "dos momentos" en una magnitud parecida a la de `ANALISIS_RESIDUO.md` §4 (allí: 0,2845 → 0,2151, un 24 %). *Confianza: alta* — es una re-verificación, no un hallazgo nuevo; entra para que P5 tenga contra qué compararse.

### P5 — σ y la forma-desde-el-nivel NO son la misma perilla
**Predicción: PASA (no son la misma).** Aplicadas juntas sobre la misma serie, cada una **conserva al menos el 70 %** de la mejora que da por separado. Si fueran la misma, se solaparían: la segunda casi no aportaría sobre la primera.

*Confianza: media.* Es la predicción que menos sé.

## 4. Qué significará cada resultado

| | Lectura |
|---|---|
| **P2 y P3 pasan** | σ es un **artefacto de escala discreta**, no una perilla. El motor toma **dos números por periodo** más la forma derivada del nivel — y el forzamiento debe hacerse sobre categorías, no como traslación de un continuo. Además obliga a revisar el Experimento 7: su control de ruido seguiría siendo válido como refutación del aporte del ABM, pero por una razón distinta de la que se escribió. |
| **P2 falla** | El difuminado es real y no se explica por la grilla. Hay que entender qué es antes de ponerlo en el motor. |
| **P5 falla (se solapan)** | Son la misma perilla y el motor toma **dos números**. Sería el resultado más cómodo, y por eso conviene desconfiar de él: habría que verificar que el solapamiento no viene de que las dos correcciones simplemente añaden varianza. |
| **P1 falla** | σ es por periodo, y entonces sí es una tercera perilla con todas las letras. |

## 5. Lo que este análisis no puede decidir

- **Qué *es* el difuminado sustantivamente**, si resultara real. Heterogeneidad de respuesta, cambio individual no correlacionado y error de medición producen todos lo mismo a nivel agregado, y con datos transversales no se separan.
- **Si la relación forma-nivel se sostiene.** Descansa en cinco años y una correlación con p = 0,045. Este análisis la usa, no la vuelve a probar.
- **Nada sobre mecanismos sociales.** Eso está cerrado por los Experimentos 3 a 7 y no se toca aquí.

---

*Guardado en el proyecto antes de ejecutar. Se reportará contra esta especificación, incluidas las predicciones que fallen.*
