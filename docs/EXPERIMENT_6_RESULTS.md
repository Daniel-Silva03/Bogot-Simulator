# EXPERIMENTO 6 — Resultados

Proyecto: Bogotá Social Simulator
Versión: 1.0
Fecha: 16 de septiembre de 2026
Reporta contra: `claude/EXPERIMENT_6_SPECIFICATION.md` (pre-registrada antes de correr)
Código: `src/experiments/experimento6.py`
Salidas: `data/processed/exp6/` — 612 corridas

---

## 1. Veredicto: las cinco predicciones se cumplen

| | Predicción | Resultado |
|---|---|---|
| **S1** — algún mecanismo hace la joroba | FALLA para todos | **FALLA** — 0 de 594 corridas con mecanismo |
| **S2** — el baseline acierta media y sd | PASA por construcción | **PASA** — error 2·10⁻¹⁵ y 9·10⁻⁷ |
| **S3** — los de solo-u ajustan peor que en el Exp. 4 | PASA | **PASA** — 0,1862 contra 0,0883 por año |
| **S4** — γ negativo primero, positivo después | PASA | **PASA** — −0,013 · +0,0044 · +0,0009 · +0,0211 |
| **S5** — ningún mecanismo le gana al baseline | PASA | **PASA** — el baseline gana por 23,5 % |

Es la primera vez en el proyecto que acierto las cinco. No es mérito: son predicciones sobre propiedades analíticas de modelos que ya conocíamos bien. **Lo interesante está en lo que ninguna de las cinco preguntaba** (§4).

## 2. Ningún mecanismo produce la joroba

La dispersión observada varía **+23,8 % · −3,3 % · −0,7 % · −14,8 %**: sube fuerte entre 2013 y 2017 y después baja.

| Familia | Corridas con joroba |
|---|---|
| Cognición motivada | **0 de 432** |
| Friedkin-Johnsen | **0 de 72** |
| Contracción de γ fijo | **0 de 72** |
| `traslación+u+γ` | 18 de 18 *(por construcción)* |

La razón es analítica y no admite calibración: con parámetros constantes, estas familias tienen un **signo fijo** de variación de dispersión. FJ y la contracción con γ>0 contraen siempre; la contracción con γ<0 y cognición motivada con ρ<1 expanden siempre. La mejor corrida con mecanismo varía la sd en **+4,3 % · +3,5 % · +4,2 % · +5,0 %** — expande de forma monótona donde lo observado sube y después baja.

Nadie podía producir esa forma, y ninguno la produjo.

## 3. El orden de mérito se da vuelta respecto del Experimento 4

| Familia | Mejor W1 total (4 años) | Mediana |
|---|---|---|
| **`traslación+u+γ`** (dos números exógenos, sin mecanismo) | **0,6032** | 0,6032 |
| Cognición motivada | 0,7450 | 1,2688 |
| **Traslación pura** | **0,7620** | 0,7620 |
| Contracción de γ fijo | 0,8860 | 2,3441 |
| Friedkin-Johnsen | 0,9011 | 1,1009 |

En el Experimento 4, Friedkin-Johnsen le ganaba a la traslación pura por 37 % y en las 360 configuraciones. **Aquí queda último, peor que no hacer nada.** No cambió el modelo: cambió el tramo de serie. Cuando el fenómeno empieza con una expansión, un mecanismo que solo contrae no es una ayuda parcial — es un estorbo.

El único mecanismo que roza a la traslación pura es cognición motivada con **ρ = 0,9**, el régimen de refuerzo, que expande. Le gana por 2,2 % porque acierta el primer tramo, y después sigue expandiendo cuando tendría que contraer.

Dispersión entre semillas en la mejor configuración de cada familia: 0,0106 (cognición motivada), 0,0074 (FJ), 0 (los deterministas). Las diferencias de la tabla están muy por encima de eso.

## 4. Lo que ninguna predicción preguntaba, y es el hallazgo

Se añadió después de ver los resultados, y por eso va etiquetado: **¿cuánto W1 es irreducible?** Es decir, ¿cuánto separa a dos muestras de 1.000 extraídas de la *misma* distribución observada? Ese es el piso que ningún modelo puede bajar.

| Año | Piso de ruido | `traslación+u+γ` | Mejor mecanismo | Traslación pura |
|---|---|---|---|---|
| 2017 | 0,0306 | 0,1421 | 0,2036 | 0,2086 |
| 2019 | 0,0338 | 0,1650 | 0,1972 | 0,2162 |
| 2021 | 0,0376 | 0,2035 | 0,2105 | 0,2450 |
| 2023 | 0,0329 | 0,0925 | 0,1337 | 0,0922 |
| **Total** | **0,1349** | **0,6032** | 0,7450 | 0,7620 |

> **Acertar la media y la desviación estándar exactamente, en los cuatro años, deja sin explicar el 78 % de la distancia.** El baseline queda a 4,5 veces el piso de ruido.

Esto refuta la hipótesis con la que entré al experimento —que la trayectoria fueran "dos números exógenos por periodo"— y la refuta en la dirección incómoda: **hacen falta más de dos**. La forma de la distribución cambia de un modo que una transformación afín no sigue.

Y no es culpa de la población sintética. La población construida con la ECP 2013 arranca prácticamente sobre lo observado: **W1(a₀, observado 2013) = 0,0436**, contra un piso de 0,034. Empieza bien y se desajusta durante la simulación.

**Por qué el baseline no puede hacerlo mejor, dicho con precisión:** trasladar y contraer hacia la media son, juntas, una **transformación afín** \(a \mapsto m + s\,(a - m_0)\). Una afín preserva la forma exactamente: mueve el centro y la escala, y no toca la asimetría, las colas ni la curtosis. Lo observado sí cambia de forma. Por eso el residuo no es ruido: es señal que este baseline no puede tocar por construcción.

Y los mecanismos, que **sí** pueden cambiar la forma, la cambian en la dirección equivocada: todos quedan por encima de 0,6032.

## 5. Qué queda establecido

1. **La dispersión también es exógena.** Ningún mecanismo disponible produce la joroba, y no por calibración sino por estructura.
2. **Dos números exógenos por periodo no alcanzan.** Queda el 78 % de la distancia sin explicar, muy por encima del ruido muestral.
3. **Nada de lo implementado captura el resto.** Cuatro familias, 612 corridas: el mejor mecanismo está un 23,5 % por detrás de no tener mecanismo.
4. **La población sintética no es el problema.** Arranca a 0,0436 del objetivo, casi sobre el piso.

Junto con los Experimentos 3, 4 y 5, y con las mediciones de `claude/ANALISIS_HOMOFILIA.md`, el cuadro es consistente: para confianza institucional en Bogotá, con datos públicos, **no hay mecanismo de dinámica de opinión identificable**, y ahora además sabemos que el objetivo no se reduce a los dos primeros momentos.

## 6. Qué sigue — y qué cambia de lo acordado

Lo pactado era: si S5 pasaba, los escenarios declaran nivel y dispersión como supuestos. **§4 lo complica**: con nivel y dispersión declarados sigue faltando el 78 %. Un motor de escenarios construido sobre dos perillas produciría distribuciones cuya forma no se parece a las reales.

Tres caminos, y no los ordeno yo:

- **(a) Caracterizar el residuo antes de diseñar escenarios.** ¿En qué se diferencian las distribuciones observadas más allá de media y sd — asimetría, colas, apilamiento en valores enteros? Si resulta ser una o dos dimensiones más, los escenarios necesitan tres o cuatro perillas, no dos, y eso es perfectamente viable. Es barato y es lo que yo haría primero.
- **(b) Aceptar el nivel de descripción que sí funciona.** Reportar escenarios como cambios de media y dispersión, diciendo explícitamente que la forma fina no se reproduce. Honesto y limitado.
- **(c) Volver a los datos.** Nada de esto se decide bien con cuatro transiciones. Una serie con más puntos —el pedido al CNC, Bogotá Cómo Vamos— sigue siendo la única vía que cambiaría el poder de estas comparaciones.

---

*Reportado contra el pre-registro. Las cinco predicciones se cumplieron y el hallazgo que importa —§4— no estaba en ninguna de ellas; se añadió después de ver los resultados y queda etiquetado como tal. Su efecto es debilitar la conclusión con la que entré, no reforzarla.*
