# EXPERIMENTO 4 — Especificación pre-registrada

Proyecto: Bogotá Social Simulator
Versión: 1.0
Fecha: 16 de septiembre de 2026
Estado: **pre-registro — escrito y guardado antes de ejecutar el barrido**
Origen: `claude/DIAGNOSTICO_Y_ALTERNATIVAS.md` §1 y §6, paso 1
Código: `src/opinion/forzamiento.py`, `src/experiments/experimento4.py`

---

## 1. La pregunta

El Experimento 3 preguntó si Friedkin-Johnsen reproduce la trayectoria de confianza institucional de Bogotá. Respondió que no, con 4 de 5 predicciones fallidas. El diagnóstico posterior mostró que **las cuatro son la misma ausencia**: FJ es un sistema cerrado que promedia, su punto fijo es una combinación convexa de las opiniones iniciales, y por lo tanto no puede mover el nivel, ni producir una V, ni vaciar una cola. Se le pidió que ganara masa.

Este experimento le da el término que le faltaba y hace la pregunta que sí es informativa:

> **Una vez que el nivel está explicado por un forzamiento exógeno, ¿el mecanismo social aporta algo?**

## 2. El diseño

$$a(t+1) = M(a(t)) + u(t)\,\mathbf{1}$$

Se ajusta un escalar \(u_k\) por periodo (2017→2019, 2019→2021, 2021→2023) para que la **media simulada iguale exactamente la media observada** de la ECP en cada año objetivo. Tres parámetros ajustados contra tres objetivos: ajuste exacto y sin holgura.

Con eso, **el nivel deja de estar en disputa**, y el forzamiento no puede tocar nada más: es una traslación en bloque. Todo lo que quede por explicar —dispersión, colas, bimodalidad, la distribución completa— tiene que venir del mecanismo.

### El baseline, que es lo importante del diseño

`traslacion+u` es un modelo donde **no pasa nada socialmente**: cada agente conserva su opinión y toda la población se desplaza en bloque la cantidad ajustada. Acierta el nivel por construcción y **conserva la desviación estándar exactamente**.

Es el baseline más exigente que ha tenido este proyecto. En el Experimento 3 el baseline a vencer era "congelar", que acertaba por no moverse; aquí el baseline acierta el nivel *y* el modelo tiene que ganarle en otra cosa. Si un modelo con mecanismo social no le gana a una traslación rígida, el mecanismo no está aportando.

### Lo que se barre (no se ajusta)

| Dimensión | Valores |
|---|---|
| Pasos por periodo \(S\) | 1, 2, 5, 15, 40 |
| Modelo | traslación · FJ φ ∈ {0,1 · 0,2 · 0,3 · 0,5 · 0,7 · 0,9} · FJ con φ heterogéneo (3 combinaciones) · DeGroot · ruido |
| Red | aleatoria · homofílica · territorial (h=20) |
| Grado \(\bar{k}\) | 4, 5, 8 (D15) |
| Semillas | 8 |
| Recorte a la escala 1–5 | no · sí (solo traslación y FJ φ=0,5) |

\(\phi\) y \(S\) **no se ajustan a los datos**: se barren y se reporta el rango. El mapeo temporal se fija en \(S\) pasos iguales por periodo, y no se busca el que mejor le venga a cada corrida como hacía el Experimento 3 — con \(u\) ajustado por tramo, elegir además dónde termina cada tramo serían dos grados de libertad sobre el mismo dato.

## 3. Lo que ya se sabe antes de predecir

**Esto es una declaración de honestidad del pre-registro.** Se corrió una prueba de humo sobre **una sola configuración** (red aleatoria, \(\bar{k}=5\), una semilla, \(S=5\)) para verificar que la maquinaria funciona. Mostró cuatro cosas, y las predicciones de §4 se escriben sabiéndolas:

1. El ajuste del nivel funciona: error de media del orden de 10⁻¹⁶.
2. \(u\) **cambia de signo** (−, −, +), o sea que la V de la media se reproduce por construcción. Deja de ser una predicción y pasa a ser una verificación.
3. Con \(S=5\), **todas las variantes de FJ se contraen de más**: sd 2023 entre 0,12 y 0,43, contra 0,764 observado. La traslación deja 0,994. La verdad está en medio y más cerca de la traslación.
4. En esa configuración, `traslacion+u` (W1 total 0,426) le ganaba a **todas** las variantes de FJ, y `traslacion+u` con recorte (0,351) le ganaba a todo.

Por eso el barrido incluye \(S \in \{1, 2\}\) y φ ∈ {0,1 · 0,2}, que no estaban en la versión original: un barrido que no llegue a la región donde el mecanismo es suave estaría condenando al modelo por no poder alcanzarla, que es el error que este experimento existe para no repetir.

**Un dato del punto de partida que conviene tener presente:** la población sintética arranca con sd = 0,994 mientras la ECP 2017 observada tiene sd = 0,934. El modelo empieza más disperso de lo real, así que para llegar a 0,764 en 2023 necesita contraer un 23 %, no el 18 % que muestra la serie observada.

## 4. Predicciones

Se registran **antes** de correr el barrido completo. Se reportarán todas, incluidas las que fallen.

### Q1 — El mecanismo social le gana a la traslación pura
**Predicción: PASA, por poco.** Algún modelo con mecanismo debería alcanzar un W1 total menor que el mejor `traslacion+u`, porque la contracción de dispersión que los datos exigen (23 %) es real y una traslación no puede producirla en absoluto. Espero que el ganador sea FJ con φ bajo (0,1–0,3) y \(S\) pequeño (1–2), y que el margen sea **menor al 15 %**.

*Confianza: media.* La prueba de humo mostró lo contrario en su única configuración, pero en una región del barrido donde FJ no podía competir.

### Q2 — La dispersión final cae dentro del umbral
**Predicción: PASA.** Con φ y \(S\) suficientemente bajos, el mejor error de sd debería quedar por debajo de 0,05 en los tres años. La traslación fallará este criterio por construcción (mantiene 0,994 contra 0,764 observado en 2023, error 0,23).

*Confianza: media-alta.* Es un problema de una sola dimensión y el barrido cubre el rango.

### Q3 — El perfil de contracción es tardío
**Predicción: FALLA.** La contracción observada es de −3,3 % / −0,7 % / −14,8 %: casi toda al final. FJ converge geométricamente, así que su contracción es **anticipada y decelerante**, la forma opuesta.

Y añado la parte contraintuitiva: **la heterogeneidad de φ no lo va a arreglar, y probablemente lo empeore.** Un φ heterogéneo hace que la trayectoria sea una *mezcla* de exponenciales, y en una mezcla los componentes rápidos dominan al principio — o sea que anticipa la contracción todavía más. Registro esto explícitamente porque φ heterogéneo entró al experimento como candidato a arreglar Q3, y estoy prediciendo que no lo hace.

*Confianza: alta.* Es una propiedad analítica, no empírica.

### Q4 — No aparece bimodalidad espuria
**Predicción: PASA.** Ninguna configuración debería superar el umbral de Sarle (0,555). Es la única predicción que el Experimento 3 acertó y no hay razón para que el forzamiento uniforme la cambie.

*Confianza: alta.*

### Q5 — ¿Cuánto de la contracción lo explica el recorte de escala, sin mecanismo alguno?
**Descriptivo, no pasa/falla.** La prueba de humo ya mostró que `traslacion+u` **con recorte** mejora el ajuste. Si resulta que el recorte por sí solo produce la contracción que los datos piden, entonces la respuesta honesta a Q1 no es "el mecanismo social sirve" sino **"el borde de la escala sirve"** — que es un hallazgo sobre el instrumento de medición, no sobre la sociedad.

**Predicción: el recorte explicará una parte apreciable de la contracción, pero no toda.** Espero que `traslacion+u` con recorte reduzca el error de sd por debajo de 0,15 sin llegar a 0,05.

*Confianza: baja.* Es lo que menos sé de todo el experimento, y es lo que más podría cambiar la interpretación.

## 5. Qué significará cada resultado

| Resultado | Lectura |
|---|---|
| Q1 pasa y Q2 pasa, con recorte apagado | El mecanismo social aporta sobre la forma. Justifica seguir con el ABM y pasar a cognición motivada. |
| Q1 pasa pero el margen lo iguala el recorte (Q5) | La contracción es un artefacto del borde de la escala. El ABM sigue sin justificarse para esta variable. |
| Q1 falla | Ni con el nivel resuelto el mecanismo aporta. Refuerza fuertemente la conclusión del diagnóstico y empuja hacia escenarios con supuestos explícitos. |
| Q3 pasa (contra lo predicho) | El perfil de contracción sí es alcanzable y hay que entender por qué; revisar el análisis de convergencia. |

**Lo que este experimento NO puede decidir.** Sigue habiendo solo 3 transiciones. Un ajuste bueno aquí no es evidencia fuerte de que el mecanismo sea el correcto — es evidencia de que no está descartado. La limitación de poder estadístico de `claude/DIAGNOSTICO_Y_ALTERNATIVAS.md` §3 no la arregla ningún modelo, solo más datos.

**Y una amenaza que sigue viva:** el salto de no-respuesta de 2023 (2,1 % → 5,6 %). Si la contracción de sd de ese año es composición y no opinión, Q2 y Q3 están midiendo un artefacto. Sigue sin analizarse.

---

*Este documento se guarda en el proyecto antes de ejecutar el barrido completo. Los resultados se reportarán en `claude/EXPERIMENT_4_RESULTS.md` contra esta especificación, no contra lo que resulte.*
