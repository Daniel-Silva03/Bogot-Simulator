# EXPERIMENTO 6 — Especificación pre-registrada

Proyecto: Bogotá Social Simulator
Versión: 1.0
Fecha: 16 de septiembre de 2026
Estado: **pre-registro — escrito y guardado antes de correr el barrido**
Origen: la serie ampliada a 2013 (`claude/DATA_INVENTORY.md` §10.8) cambia el fenómeno a reproducir
Código: `src/experiments/experimento6.py`

---

## 1. Por qué hay un experimento más

Los Experimentos 4 y 5 arrancaban en 2017 y trataban la contracción de dispersión como el fenómeno. Con 2013 adentro, la serie es:

| Año | media | sd |
|---|---|---|
| **2013** | **2,808** | **0,754** |
| 2017 | 2,503 | 0,934 |
| 2019 | 2,362 | 0,903 |
| 2021 | 2,245 | 0,897 |
| 2023 | 2,430 | 0,764 |

La media cae de forma monótona hasta 2021 y rebota. Pero la dispersión **hace una joroba**: sube de 0,754 a 0,934 y vuelve a 0,764, casi exactamente donde empezó.

**2017 era la cima.** Los dos experimentos anteriores estaban ajustando la bajada y llamándola "el fenómeno". Ningún modelo capaz solo de contraer —Friedkin-Johnsen, encogimiento uniforme, cognición motivada en la región donde ajustaba— puede producir la subida, así que la pregunta cambia:

> **¿Puede algún mecanismo producir expansión y después contracción, o la dispersión también hay que ponerla a mano?**

## 2. El diseño

Igual que los Experimentos 4 y 5 —u ajustado por periodo para que la media simulada iguale exactamente la observada— con dos cambios.

**DI-W1 — los tramos duran distinto.** La serie queda espaciada **4 · 2 · 2 · 2** años. Darle a todos los tramos los mismos pasos correría el reloj del modelo al doble de velocidad en el primero. Los pasos son proporcionales al tiempo real: \(S\) pasos por cada 2 años, así que el primer tramo lleva \(2S\).

**DI-W2 — entra un baseline nuevo, y es el duro.** `traslación + u + γ`: además del escalar de nivel \(u_k\), un escalar de dispersión \(\gamma_k\) por periodo, ajustado para que la sd simulada iguale exactamente la observada. Con γ > 0 contrae hacia la media y con **γ < 0 expande**; en los dos casos conserva la media exactamente, así que los dos ajustes son independientes y ninguno roba grados de libertad al otro.

Es **el modelo sin ninguna dinámica social que acierta los dos primeros momentos por construcción**: dos números exógenos por periodo y nada más. Cualquier mecanismo tiene que ganarle en lo que queda — la forma de la distribución más allá de media y dispersión, que es lo que mide W1.

### La malla

| Dimensión | Valores |
|---|---|
| Base / objetivos | 2013 → 2017 · 2019 · 2021 · 2023 |
| \(S\) (pasos por 2 años) | 5 · 15 |
| Baselines | traslación+u · **traslación+u+γ** |
| Encogimiento fijo | γ ∈ {0,02 · 0,05} y **γ ∈ {−0,02 · −0,05}** (expansión) |
| Friedkin-Johnsen | φ ∈ {0,08 · 0,1 · 0,2 · 0,3} |
| Cognición motivada | α ∈ {0,1 · 0,3} · λ ∈ {0,3 · 0,5} · k ∈ {2 · 3} · **ρ ∈ {0,9 · 1,0 · 1,1}** |
| Red | aleatoria · homofílica · territorial (h=20) |
| \(\bar{k}\) | 5 (D15) |
| Semillas | 3 |

ρ = 0,9 entra a propósito: es el régimen de **refuerzo**, el único de cognición motivada que expande la dispersión en vez de contraerla (ver el docstring del módulo — ρ<1 aleja del centro).

**Población base nueva:** `poblacion_ecp2013.csv`, construida con la ECP 2013 como donante (hot-deck, 100 % en nivel 0, distancia territorial al marginal 0,0324).

## 3. Predicciones

### S1 — Ningún mecanismo con parámetros fijos reproduce la joroba
**Predicción: FALLA para todos.** Ninguna configuración de FJ, encogimiento fijo o cognición motivada producirá expansión en el primer tramo y contracción en los demás. *Confianza: alta*, y es analítica: con parámetros constantes, estas familias tienen un signo fijo de variación de dispersión. El único que podría es cognición motivada con ρ<1, y ese expande **siempre**, no solo al principio.

Criterio: primer tramo con sd creciente **y** último tramo con sd decreciente, en ≥5 % de las corridas de la familia.

### S2 — `traslación+u+γ` acierta media y sd en los cuatro años
**Predicción: PASA por construcción.** Es una verificación de que el ajuste funciona, no una prueba. Error de media y de sd por debajo de 10⁻³ en los cuatro años.

### S3 — Los modelos de solo-u ajustan peor que en el Experimento 4
**Predicción: PASA.** Ahora tienen que producir también la expansión, que ninguno puede. Espero que el mejor W1 por año objetivo suba respecto de los 0,2650 de Friedkin-Johnsen en el Experimento 4. *Confianza: alta.*

### S4 — El γ ajustado es negativo en el primer tramo y positivo después
**Predicción: PASA.** Es la joroba dicha como parámetro: γ₁ < 0 (expansión 2013→2017) y γ₂, γ₃, γ₄ > 0. *Confianza: alta* — es casi una redescripción de la tabla de §1, pero conviene tenerla registrada porque si saliera distinto significaría que el ajuste está mal hecho.

### S5 — Ningún mecanismo le gana a `traslación+u+γ` en W1 · **la decisiva**
**Predicción: PASA (ningún mecanismo gana).** *Confianza: media.* El baseline acierta dos momentos por construcción; a los mecanismos les queda solo la forma. En los Experimentos 4 y 5, lo que los mecanismos aportaban era precisamente contracción de dispersión — que aquí ya está puesta a mano. Espero que ninguno gane, y que los mejores queden dentro de un 5 % del baseline.

Si **alguno gana**, ese margen es lo único que el mecanismo social aporta en toda la serie, y por primera vez estaría medido contra un baseline que no le regala ni el nivel ni la dispersión.

## 4. Qué significará cada resultado

| | Lectura |
|---|---|
| S5 pasa (ningún mecanismo gana) | La trayectoria de confianza en Bogotá 2013-2023 son **dos números exógenos por periodo**. No hay mecanismo social identificable con estos datos, y el simulador no puede pretender generar la dinámica: los escenarios tienen que declarar nivel y dispersión como supuestos. |
| S5 falla por poco (<5 %) | Hay un aporte real pero pequeño, y queda cuantificado contra el baseline más duro posible. |
| S5 falla por mucho | Habría que revisar el ajuste del baseline antes de celebrar: un margen grande contra un modelo que acierta dos momentos es más sospechoso que alentador. |
| S1 pasa para alguna familia | Existe un mecanismo capaz de la joroba y merece perseguirse. Sería el primer resultado claramente a favor del ABM en todo el proyecto. |

**Lo que sigue sin poder decidirse.** Cuatro transiciones en vez de tres: mejor, pero sigue siendo poco para discriminar entre familias. Y el primer tramo cubre cuatro años con una sola observación en los extremos, así que lo que pase entre 2013 y 2017 —incluida la ola 2015, que quedó fuera por tener los códigos corridos— es invisible.

---

*Guardado en el proyecto antes de ejecutar. Los resultados se reportarán en `claude/EXPERIMENT_6_RESULTS.md` contra esta especificación, incluidas las predicciones que fallen.*
