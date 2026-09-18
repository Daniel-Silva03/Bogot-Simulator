# EXPERIMENTO 4 — Resultados

Proyecto: Bogotá Social Simulator
Versión: 1.0
Fecha: 16 de septiembre de 2026
Reporta contra: `claude/EXPERIMENT_4_SPECIFICATION.md` (pre-registrada antes de correr el barrido)
Código: `src/opinion/forzamiento.py`, `src/experiments/experimento4.py`
Salidas: `data/processed/exp4/`

---

## 1. Veredicto

| | Predicción | Resultado | |
|---|---|---|---|
| **Q1** — el mecanismo le gana a la traslación pura | PASA, margen < 15 % | **PASA, margen 37,5 %** | predicción acertada, magnitud subestimada |
| **Q2** — dispersión dentro del umbral | PASA | **PASA** (error 0,0453 < 0,05) | acertada |
| **Q3** — perfil de contracción tardío | FALLA | **1 de 3.960 corridas** | acertada en sustancia; el criterio estaba mal escrito (§4) |
| **Q4** — sin bimodalidad espuria | PASA | **FALLA** (máx. 0,997) | fallida — pero es un artefacto de medición (§5) |
| **Q5** — cuánto explica el recorte de escala | error sd < 0,15 | **0,1617** | fallida por poco, y en la dirección favorable |

Barrido: 5.040 corridas (10 modelos × 5 valores de \(S\) × 3 redes × 3 grados × 8 semillas, más las variantes con recorte), unos 10 minutos.

**El titular, sin embargo, no es ninguna de esas cinco.** Es el control post-hoc de §6.

## 2. Q1 — el mecanismo social gana, y no por poco

| Modelo | W1 total (mediana) | W1 total (mejor) |
|---|---|---|
| **FJ φ = 0,1** | **0,2778** | **0,2663** |
| traslación + recorte | 0,3510 | 0,3510 |
| ruido | 0,4260 | 0,4188 |
| traslación pura | 0,4262 | 0,4262 |
| FJ φ = 0,2 | 0,4612 | 0,2873 |
| FJ heterogéneo (m 0,5 · d 0,6) | 0,6762 | 0,3014 |
| FJ φ = 0,3 | 0,7131 | 0,3435 |
| FJ φ = 0,5 | 1,1125 | 0,4477 |
| DeGroot | 1,6140 | 0,5093 |
| FJ φ = 0,9 | 1,6289 | 0,5273 |

**Y no es un artefacto de quedarse con lo mejor del barrido.** FJ φ=0,1 le gana a la traslación pura en **360 de 360 configuraciones**, en los cinco valores de \(S\), las tres redes, los tres grados y las ocho semillas. La mediana le gana a la mediana por 35 %.

Comparado con el Experimento 3, donde el mejor modelo apenas superaba a congelar (0,5310 contra 0,6265) y empataba en tres de cuatro olas, esto es un cambio de régimen. **El diagnóstico era correcto: lo que faltaba era el término exógeno, no otro mecanismo.**

La mejor corrida (FJ φ=0,1, \(S\)=2, red territorial, \(\bar{k}\)=4) reproduce así la dispersión:

| | simulado | observado | error |
|---|---|---|---|
| inicio (2017) | 0,994 | 0,934 | +0,060 *(la población sintética arranca más dispersa)* |
| 2019 | 0,904 | 0,903 | **+0,001** |
| 2021 | 0,828 | 0,897 | **−0,070** |
| 2023 | 0,763 | 0,764 | **−0,002** |

Clava 2019 y 2023 y se equivoca en 2021. Eso no es azar: es Q3 (§4) apareciendo en concreto.

## 3. Q2 — la dispersión final se alcanza

Mejor error de sd con mecanismo: **0,0453**, por debajo del umbral de 0,05. La traslación pura falla por construcción: 0,2292, porque conserva la dispersión exactamente y los datos piden contraerla un 23 %.

## 4. Q3 — el perfil de contracción sigue sin reproducirse, y mi criterio estaba mal escrito

Lo observado se contrae **−3,3 % / −0,7 % / −14,8 %**: casi nada en los dos primeros tramos y casi todo en el último. De 3.960 corridas con mecanismo, **1 sola** exhibe ese perfil.

Formalmente el criterio era "al menos una corrida", así que el veredicto automático dice "pasa". **No pasa.** Una de 3.960 es ruido, y el criterio estaba mal escrito — el mismo defecto que ya había aparecido en P3/P4 del Experimento 3, donde un umbral puramente numérico dejaba pasar rebotes de orden 10⁻⁵. Se corrige aquí para futuras especificaciones: un criterio cualitativo necesita **umbral de magnitud y proporción mínima de corridas**, no existencia.

La predicción sustantiva era FALLA y se cumple. La razón es analítica: Friedkin-Johnsen converge geométricamente, así que su contracción es anticipada y decelerante — la forma opuesta.

**La sub-predicción contraintuitiva también se cumple.** Había registrado que el φ heterogéneo *no* arreglaría Q3 y probablemente lo empeoraría, porque una mezcla de exponenciales está dominada al principio por sus componentes rápidos. Las tres variantes heterogéneas quedan **peor** que FJ φ=0,1 homogéneo (medianas 0,676 · 0,867 · 0,983 contra 0,278). Entró al experimento como candidato a arreglar el perfil y no lo arregla.

Había tres explicaciones posibles para el perfil tardío. Dos quedaron descartadas el mismo día: **el salto de no-respuesta de 2023** (ver §8 y `claude/ANALISIS_NORESPUESTA_2023.md` — entre casos completos el perfil es −4,2 % / 0,0 % / −13,8 %, o sea todavía más tardío) y **el borde de la escala** (Q5: la traslación con recorte llega a un error de sd de 0,1617, muy lejos del 0,0453 del mecanismo). Queda **un mecanismo con dinámica distinta**, y el candidato es cognición motivada.

## 5. Q4 — falla, pero por una falla del indicador, no del modelo

Bimodalidad máxima simulada 0,997, muy por encima del umbral de Sarle (0,555). Predije que pasaría.

Al mirar **quién** la dispara: solo **DeGroot y FJ φ=0,9**, y en esas 83 corridas la desviación estándar final tiene mediana **0,057** (máximo 0,153). Es decir, la distribución ya colapsó a casi un punto. El coeficiente de Sarle es \((\text{sesgo}^2+1)/\text{curtosis}\) y sobre una distribución casi degenerada no mide bimodalidad: mide ruido numérico dividido por ruido numérico.

Entre los modelos que ajustan bien (φ ≤ 0,3, más traslación, ruido y contracción) el máximo es **0,411**, por debajo del umbral.

**Conclusión honesta: Q4 falla por un criterio sin guarda.** Hay que exigir una dispersión mínima antes de calcular bimodalidad. No es que el modelo produzca fragmentación espuria: es que se le midió fragmentación a una distribución que ya no existía. Corregido el indicador, la predicción original se sostiene.

## 6. El control que decide la interpretación

Q1 salió a favor del modelo. Eso obliga a buscarle un baseline mejor, no a darlo por bueno.

Con φ pequeño, el punto fijo de Friedkin-Johnsen es aproximadamente \(a(0) + \phi\,(W a(0) - a(0))\): cada agente se mueve un poco hacia el promedio de sus vecinos. En agregado, eso es **encoger la dispersión hacia la media**. La pregunta que quedaba es si hacía falta la red para eso.

Se añadió, **después de ver los resultados y etiquetado como post-hoc**, un modelo sin ninguna estructura social:

$$a(t+1) = a(t) + \gamma\,\big(\bar{a}(t) - a(t)\big)$$

Todos se acercan a la media global en la misma proporción. Sin red, sin vecinos, sin homofilia. Y para que la comparación fuera justa, se le dio a cada familia una grilla propia de tamaño comparable (7 valores de γ contra 6 de φ):

| Familia | Mejor W1 total | Mediana |
|---|---|---|
| Friedkin-Johnsen (**con** red) | **0,2650** | 0,3089 |
| Contracción uniforme (**sin** red) | **0,2725** | 0,3190 |
| Traslación pura | 0,4262 | 0,4262 |

La dispersión entre semillas en la mejor configuración de FJ es 0,0023.

**La descomposición completa:**

| Paso | W1 total | Aporte |
|---|---|---|
| Traslación sola | 0,4262 | — |
| + encogimiento, **sin ninguna red** | 0,2725 | **−36 %** |
| + influencia social por la red (FJ) | 0,2650 | **−2,8 %** |

> **Lo que los datos piden es traslación más encogimiento. La red social aporta un 2,8 % adicional** — tres veces la dispersión entre semillas, así que es real y medible, y aun así es casi nada frente al 36 %.

Esto es consistente con todo lo anterior y lo vuelve más preciso. El Experimento 3 §5 ya había medido que la estructura de red casi no afecta el ajuste; ahora se puede decir cuánto: **2,8 %**, con el nivel controlado y contra un baseline que hace lo mismo sin red.

## 7. Qué se aprendió, en orden de importancia

1. **El diagnóstico era correcto y la corrección funciona.** Con un escalar por periodo, el ajuste mejora un 37,5 % sobre el mejor baseline y la dispersión cae dentro del umbral. El Experimento 3 estaba midiendo la ausencia de un término, no el fracaso de un mecanismo.
2. **Pero el mecanismo que hace el trabajo es el encogimiento, no la influencia social.** Un modelo sin red llega al 97 % del camino. La red aporta 2,8 %.
3. **El perfil temporal sigue sin reproducirse** y la heterogeneidad de φ no lo arregla, tal como se predijo.
4. **El borde de la escala no es la explicación.** La traslación con recorte llega a 0,3510 y a un error de sd de 0,1617; el mecanismo llega a 0,2650 y 0,0453. La alternativa "es un artefacto del instrumento" queda descartada como explicación principal, aunque el recorte sí mejora algo.
5. **Dos criterios del pre-registro estaban mal escritos** (Q3 sin proporción mínima, Q4 sin guarda de dispersión). Quedan corregidos para las próximas especificaciones.

## 8. Lo que esto NO dice

- **No dice que el modelo sea correcto.** Siguen siendo 3 transiciones; un ajuste bueno significa "no descartado", no "identificado". La limitación de poder de `claude/DIAGNOSTICO_Y_ALTERNATIVAS.md` §3 no la arregla ningún modelo.
- **No valida la red ni la homofilia.** El aporte de 2,8 % es el techo de lo que la estructura social puede reclamar aquí, y no distingue entre los tres generadores.
- ~~Sigue viva la amenaza de 2023.~~ **Resuelta el mismo día, y a favor.** La no-respuesta de 2023 no explica ni el rebote ni la contracción: restringido a los **casos completos (13 de 13 ítems)**, el rebote es +0,186 y la contracción −13,8 %, contra +0,185 y −14,8 % publicados. Ver `claude/ANALISIS_NORESPUESTA_2023.md`. Lo que Q2 reproduce es un fenómeno real, y lo que Q3 no reproduce, también.

## 9. Qué sigue

1. ~~Analizar la no-respuesta de 2023~~ ✅ **hecho el 16/09/2026, y descartada como explicación.** Entre casos completos el perfil observado es **−4,2 % / 0,0 % / −13,8 %**: la contracción no empieza hasta el tercer periodo. El objetivo de Q3 es real.
2. **Implementar cognición motivada** (Lorenz/Gestefeld) — ahora lo primero. Es la única familia con una dinámica capaz, en principio, de producir contracción tardía, y sigue siendo lo que `MODEL_SPECIFICATION.md` §4 mandaba.
3. **Ampliar la serie** (ECP 2008–2015) — con 3 transiciones ningún resultado de ajuste es concluyente.
4. Registrar en `PROJECT_CONTEXT.md` que A11 cambia: el baseline obligatorio deja de ser DeGroot y pasa a ser **traslación + contracción con forzamiento ajustado**, que es mucho más exigente y es el que discrimina.

---

*Reportado contra el pre-registro, incluidas las dos predicciones fallidas y los dos criterios mal escritos. El control de §6 se añadió después de ver los resultados y está etiquetado como tal: es un baseline más duro, no un candidato, y su efecto es debilitar la lectura favorable de Q1, no reforzarla.*
