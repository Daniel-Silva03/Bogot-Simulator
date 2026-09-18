# EXPERIMENT 2 — Resultados: ¿cuánto importa la estructura de la red?

Proyecto: Bogotá Social Simulator
Documento: resultados del Experimento 2 de RESEARCH.md (sección 50) — insumo para cerrar A07
Versión: 0.1
Fecha: 15 de septiembre de 2026

---

## 1. Qué se corrió

Dos experimentos de 4.800 corridas cada uno, sobre la población sintética ponderada v2 (1.000 agentes, D14):

| | Friedkin-Johnsen | DeGroot (baseline, A11) |
|---|---|---|
| configuraciones de red | 24 | 24 |
| corridas por configuración | 200 | 200 |
| pasos por corrida | 100 | 100 |
| duración | 92 s | 125 s |

Población fija, opinión inicial fija, modelo fijo. **Lo único que cambia entre corridas es la realización de la red**, porque ambos modelos de opinión son deterministas. El barrido cubre \(\bar{k} \in \{5,10,15,20\}\) para los tres generadores, más \(h \in \{5,10,20,50\}\) para el territorial.

Reproducible con `python src/experiments/runner.py config/experiment_2.yaml`. Los resultados están en `experiments_output/`, con la configuración completa y el esquema de derivación de semillas en `run_metadata.json`.

## 2. El hallazgo principal

**La estructura de la red importa, pero no toda la estructura importa igual: lo que sostiene el desacuerdo es la homofilia demográfica, no la proximidad territorial.**

Desviación estándar final de la opinión, Friedkin-Johnsen (φ=0,7), media ± desviación entre las 200 corridas:

| \(\bar{k}\) | aleatoria | homofílica | territorial (h=20) |
|---|---|---|---|
| 5 | 0,2256 ± 0,0048 | **0,3535** ± 0,0050 | 0,2432 ± 0,0058 |
| 10 | 0,1989 ± 0,0023 | **0,2923** ± 0,0049 | 0,2070 ± 0,0030 |
| 20 | 0,1899 ± 0,0014 | **0,2300** ± 0,0037 | 0,1962 ± 0,0016 |

La diferencia entre la red homofílica y la aleatoria es de 27 a 41 veces la desviación entre corridas. La diferencia entre la territorial y la aleatoria existe y es consistente, pero es de apenas 4 veces esa desviación, y en magnitud absoluta es entre 7 y 15 veces menor que el efecto de la homofilia.

Es decir: sustituir "cada quien habla con cualquiera" por "cada quien habla con gente de su localidad" casi no cambia el resultado. Sustituirlo por "cada quien habla con gente parecida en edad, estrato y educación" lo cambia mucho.

## 3. El baseline lo muestra de forma más cruda

DeGroot es el modelo que fuerza consenso, y por eso sirve como vara: bajo DeGroot, la única estructura que impide que la opinión colapse es la homofilia.

| Red | sd final (DeGroot) | sd final (FJ) |
|---|---|---|
| aleatoria | 0,012 | 0,202 |
| territorial | 0,025 | 0,211 |
| homofílica | **0,176** | 0,282 |

Con red aleatoria o territorial, DeGroot borra prácticamente toda la variación en 100 pasos. Con red homofílica, conserva 0,176 — un orden de magnitud más.

Esto también se ve en la convergencia: DeGroot converge en el 86% de las corridas con red aleatoria (47 pasos en promedio) y en el 59% con territorial, pero **en ninguna** con red homofílica, donde a los 100 pasos todavía se está moviendo. La estructura de comunidades que produce la homofilia retrasa la mezcla lo suficiente como para que el horizonte de 100 pasos ni siquiera alcance.

Responde de paso la pregunta de RESEARCH.md sobre baselines (A11): el ABM con Friedkin-Johnsen sí aporta algo frente a DeGroot, pero **cuánto** depende de la red. Sobre red homofílica la diferencia entre los dos modelos se reduce a 0,106; sobre red aleatoria es de 0,190.

## 4. Lo que estos modelos NO pueden mostrar

El barrido midió cuatro índices de polarización, y conviene decir con claridad qué salió:

| | Friedkin-Johnsen | DeGroot |
|---|---|---|
| clusters de opinión (media) | 1,26 | 1,52 |
| fracción de corridas bimodales | 0,0000 | 0,1350 |

**Ninguna corrida de Friedkin-Johnsen produjo una distribución bimodal, en 4.800 intentos.** No es un defecto de la implementación: DeGroot y Friedkin-Johnsen son modelos de promediado, matemáticamente incapaces de separar a la población en bloques. Cada opinión es una combinación convexa de otras, así que el rango solo puede encogerse.

Lo que estos modelos permiten estudiar es **cuánto desacuerdo sobrevive**, no **si la población se parte en dos**. Es exactamente la limitación que MODEL_SPECIFICATION.md señala en su sección 2 y la razón por la que el marco de cognición motivada (Lorenz/Gestefeld) es el objetivo de la Fase 6. Si la pregunta de investigación involucra polarización en el sentido de fragmentación, este par de modelos no puede responderla por construcción, y ninguna cantidad de corridas lo va a cambiar.

Los índices se conservan igual en la salida: el día que entre un modelo capaz de fragmentar, la comparación contra estos números será directa.

## 5. Efecto de los parámetros de red

**Densidad (\(\bar{k}\)) importa más que el tipo de red**, en el rango barrido. Pasar de \(\bar{k}\)=5 a \(\bar{k}\)=20 reduce la dispersión final un 16% en la red aleatoria y un 35% en la homofílica — más que la diferencia entre aleatoria y territorial en cualquier \(\bar{k}\). Más vecinos, más mezcla, menos desacuerdo. Es un efecto esperado, pero su tamaño relativo sugiere que \(\bar{k}\) no debería tratarse como un parámetro de segundo orden.

**La homofilia territorial (\(h\)) tiene efecto monótono pero pequeño.** A \(\bar{k}\)=5, la desviación final va de 0,2288 (h=5) a 0,2619 (h=50): la segregación territorial se cuadruplica y el resultado se mueve un 14%. Es consistente con lo que ya advertía NETWORK_SPECIFICATION.md sección 9.1(b) — la segregación observada satura con \(h\), y el barrido \(h \in \{5,50\}\) cubre de 3,6× a 8,9× sobre un techo de 10,6×.

## 6. Qué significa esto para A07

El Experimento 2 se diseñó para informar la decisión, no para tomarla sola. Lo que aporta:

- Elegir entre red aleatoria y territorial es, a estos parámetros, casi indiferente para el resultado. Si el criterio fuera solo "qué cambia la dinámica", la territorial no se justifica por sí sola.
- La red homofílica sí cambia la dinámica de forma sustancial y consistente en todo el barrido.
- Pero el generador territorial es el único que permite leer resultados **por localidad**, que es la unidad territorial del proyecto (D01, sección 11 de PROJECT_CONTEXT.md) y lo que hace falta para la validación territorial de la Fase 7. Su valor no está en cuánto mueve la dispersión agregada.

La lectura razonable, sujeta a discusión, es que no se trata de elegir uno: el mecanismo que importa para la dinámica es la homofilia demográfica, y el territorio importa para poder interpretar y validar. Una red que combine ambos —homofilia demográfica dentro de bloques territoriales— no está especificada todavía en NETWORK_SPECIFICATION.md y sería el candidato natural a evaluar antes de cerrar A07.

## 7. Advertencias sobre estos resultados

Ninguna de estas invalida lo anterior, pero todas acotan qué se puede concluir.

**φ = 0,7 no está estimado.** Es el placeholder de ARCHITECTURE.md. Todos los resultados de Friedkin-Johnsen dependen de ese valor y ninguno debe leerse como una magnitud sobre Bogotá. Lo que sí es robusto es la *comparación entre redes*, porque φ es el mismo en las tres.

**La incertidumbre reportada está subestimada.** Los intervalos entre corridas capturan solo la variabilidad de la red. La población sintética es una sola muestra de 1.000 agentes de las 168.200 disponibles, y su propia variabilidad muestral no entra en ningún intervalo de este documento. Un experimento que remuestree la población daría intervalos más anchos.

**La opinión es independiente del estrato por construcción** (A15, POPULATION_SPECIFICATION.md 8.5). El generador homofílico pondera estrato en su distancia, así que parte del efecto de homofilia que se mide acá se apoya en una variable que no tiene relación con la opinión en los datos. Habría que repetir el Experimento 2 con pesos que excluyan estrato para separar las dos cosas.

**La opinión inicial es granulada** (POPULATION_SPECIFICATION.md 8.3): 45 valores únicos entre 1.000 agentes, con el 46% concentrado en cinco valores. Eso afecta directamente al conteo de clusters y probablemente subestima la dispersión inicial real.

**Horizonte de 100 pasos.** Con red homofílica, DeGroot no había convergido en ninguna corrida al llegar ahí. Las comparaciones de este documento son a 100 pasos, no en equilibrio. Friedkin-Johnsen sí converge siempre (tiene punto fijo analítico), así que esa advertencia aplica sobre todo al baseline.

## 8. Qué sigue

- Discutir A07 con esto en la mano, incluida la posibilidad de un cuarto generador que combine homofilia demográfica y bloques territoriales.
- Repetir el barrido homofílico con pesos que excluyan estrato, para separar el efecto de homofilia real del artefacto de A15.
- Ejecutar el Experimento 1 (¿reproduce el modelo una distribución objetivo?), que el runner ya soporta: falta la configuración y decidir contra qué distribución observada se compara.
- Cuando se aborde la Fase 6, usar estos números como punto de comparación para el modelo de cognición motivada — que es el que puede producir fragmentación y, por lo tanto, el que puede hacer que los cuatro índices de polarización digan algo.

---

*Documento vivo — la decisión final sobre A07 se registra en PROJECT_CONTEXT.md con formato D0X cuando se confirme.*
