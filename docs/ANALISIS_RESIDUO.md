# ¿De qué está hecho el residuo? — y cuántas perillas necesita un escenario

Proyecto: Bogotá Social Simulator
Versión: 1.0
Fecha: 16 de septiembre de 2026
Origen: `claude/EXPERIMENT_6_RESULTS.md` §6, opción (a)
Datos: ECP 2013 · 2017 · 2019 · 2021 · 2023 (Bogotá, ponderada) y `poblacion_ecp2013.csv`

---

> ## ⚠ Nota de revocación — 17 de septiembre de 2026
>
> **La conclusión de §6 —"tres perillas, y la tercera atada a la primera"— queda revocada.** No por un error de medición sino por un error de forma funcional: todo este análisis, como los Experimentos 4 a 7, descansa en un forzamiento **afín**, y la variable de la ECP no vive en un continuo — el índice toma 154 valores discretos determinados por el instrumento.
>
> Con un **ladeo exponencial sobre el soporte propio de la variable**, dos números exógenos por periodo llevan el ajuste a \(W_1 = 0{,}1788\) contra un piso de ruido de 0,1835: **por debajo del piso**. El afín encadenado daba 0,5775. La deriva de forma que este documento describe —PC1, r = −0,886— **no hay que declararla ni derivarla del nivel: sale sola del ladeo**.
>
> **Qué de este documento sigue en pie.** Todo lo que mide: que el residuo es deriva de forma y no defecto de la población (§1), la corrección a mi lectura del Experimento 6 (§2), la descomposición en componentes principales (§3) y el anexo sobre A17. Midió bien **que** faltaba algo y **cuánto**. Lo que no consideró es que lo que faltaba no fuera un parámetro sino una forma funcional.
>
> Ver `claude/FORZAMIENTO_CATEGORICO.md`.

---

## 0. Las tres cosas que salieron

1. **El residuo es deriva de forma en los datos, no un defecto de la población sintética.**
2. **Yo sobreestimé el residuo en el Experimento 6.** Buena parte del 78 % venía de arrancar en 2013, que resulta ser el año de forma más atípica de los cinco. Con la forma promedio, dos perillas dejan menos de la mitad de ese residuo.
3. **La respuesta a "¿dos perillas o cuatro?" es tres — y la tercera no es libre**: el 70 % de la deriva de forma es una sola dimensión, y esa dimensión está atada al nivel.

---

## 1. La población no es el problema

El baseline del Experimento 6 aplica a la población de 2013 una traslación y una contracción hacia la media. Las dos juntas son una **transformación afín**, y para una afín vale exactamente

$$W_1(aX+b,\; aY+b) = |a|\; W_1(X, Y)$$

así que el residuo de cada año se descompone sin aproximaciones:

$$\text{residuo}_t = \sigma_t \cdot W_1\big(z(a_0),\, z(\text{obs}_t)\big)$$

donde \(z(\cdot)\) es la distribución estandarizada — es decir, **la forma**.

| Año | \(W_1\) de formas, \(a_0\) vs obs | \(W_1\) de formas, obs 2013 vs obs | σ | residuo |
|---|---|---|---|---|
| 2017 | 0,1527 | 0,1473 | 0,933 | 0,1424 |
| 2019 | 0,1802 | 0,1694 | 0,908 | 0,1637 |
| 2021 | 0,2268 | 0,2154 | 0,897 | 0,2035 |
| 2023 | 0,1209 | 0,1276 | 0,765 | 0,0925 |
| | | | **suma** | **0,6020** |

Reproduce el 0,6032 que dio el Experimento 6 por simulación. Y las dos columnas centrales son casi idénticas: **el residuo es la diferencia de forma entre 2013 y cada año**, no algo que la población agregue.

Confirmado por el otro lado: el error de forma de la población inicial es \(W_1 = 0{,}0522\) contra un piso de ruido de 0,0387. La población arranca con la forma prácticamente correcta.

## 2. La corrección a mi lectura del Experimento 6

Escribí ahí que acertar media y desviación estándar deja **el 78 % de la distancia sin explicar**. Es cierto para ese diseño, pero le atribuí al problema algo que era del punto de partida.

2013 es, de los cinco años, **el de forma más atípica**: su puntaje en la primera componente de forma es −2,21, contra +0,45, +0,97, +1,81 y −1,02 de los demás. Propagar *esa* forma hacia adelante arrastra el error.

Si en vez de la forma de 2013 se usa la **forma promedio de los cinco años**, la misma receta de dos perillas (media + desviación) da:

| | \(W_1\) total, 2017–2023 |
|---|---|
| Media + sd, propagando la forma de 2013 *(Exp. 6)* | 0,6020 |
| **Media + sd, con la forma promedio** | **0,2845** |
| Piso de ruido | 0,1328 |

**Menos de la mitad.** El residuo real de "dos momentos" no es el 78 % sino el 114 % sobre el piso — alto, pero no lo que dije.

## 3. Cuántas dimensiones tiene la deriva de forma

Se estandariza la función cuantil de cada año (media 0, sd 1) y se hace componentes principales sobre las cinco curvas. Si la forma no cambiara, serían la misma curva.

| | PC1 | PC2 | PC3 | PC4 |
|---|---|---|---|---|
| Varianza explicada | **69,8 %** | 18,6 % | 6,3 % | 5,2 % |

**Una sola dimensión explica el 70 %**, dos explican el 88 %. La amplitud de la deriva es 0,105 en unidades de desviación estándar de la opinión, contra un piso de ruido de 0,023: real, unas cuatro veces el ruido, y modesta.

### Y esa dimensión está atada al nivel

| Año | media | puntaje PC1 |
|---|---|---|
| 2013 | 2,81 | **−2,21** |
| 2017 | 2,50 | +0,45 |
| 2019 | 2,36 | +0,97 |
| 2021 | 2,25 | **+1,81** |
| 2023 | 2,43 | −1,02 |

Correlación **r = −0,886** (p = 0,045). Cuanto más baja la confianza media, más alto el puntaje de forma — y eso tiene una lectura sustantiva sencilla: la asimetría acompaña al nivel (−0,22 en 2013, +0,33 en 2019, −0,18 en 2023). Sobre una escala acotada, cuando la media se acerca al piso la masa se apila abajo y la cola apunta a la derecha.

**Consecuencia para el diseño: PC1 no es una perilla libre. Es, en buena medida, una función del nivel.**

## 4. La escalera de perillas

\(W_1\) total sobre 2017–2023, reconstruyendo cada año con distintos grados de libertad:

| Receta | \(W_1\) | sobre el piso |
|---|---|---|
| 2 perillas: media + sd | 0,2845 | +114 % |
| **2 perillas + forma predicha por el nivel** | **0,2151** | **+62 %** |
| 3 perillas: media + sd + PC1 libre | 0,1768 | +33 % |
| 4 perillas: + PC2 libre | 0,1198 | −10 % |
| Piso de ruido | 0,1328 | — |

**El de cuatro perillas queda por debajo del piso, y eso no es un logro: es sobreajuste.** Son cuatro parámetros libres ajustados sobre cuatro años, con las componentes estimadas de esos mismos cinco años. La fila útil es la de tres.

## 5. Una hipótesis que probé y no funcionó

Si la forma acompaña al nivel porque la escala está acotada en 1–5, entonces **respetar los bordes** debería bastar, sin perillas de forma. Se probó un mapa monótono de un solo parámetro que preserva el rango (llevar a [0,1], elevar a \(t\), volver):

| | \(W_1\) total |
|---|---|
| Afín de 2 parámetros | 0,6020 |
| Potencia acotada de 1 parámetro | 0,6741 |

**Pierde**, y por una razón diagnosticable: reproduce el nivel pero deja la desviación estándar clavada en ~0,75 cuando lo observado sube a 0,93. El borde de la escala no genera la expansión de dispersión. Esa expansión es un fenómeno aparte y sigue necesitando su propia perilla.

## 6. Qué implica para el motor de escenarios

**Tres perillas, y la tercera atada a la primera:**

1. **Nivel** — exógeno, por periodo. Es el que carga casi todo el trabajo (Exp. 3 y 4).
2. **Dispersión** — exógeno, por periodo. Ningún mecanismo disponible la produce (Exp. 6), y hace una joroba, no una contracción monótona.
3. **Forma** — *no se declara*: se deriva del nivel con la relación de §3, y se revisa cuando haya más años.

Un escenario se especifica entonces con dos números por periodo, no cuatro, y la distribución resultante ya no es una simple traslación-y-escalado de la inicial.

**Lo que esto no autoriza a decir.** Es una descripción, no un mecanismo: dice cuántos parámetros hacen falta para *describir* el cambio, no por qué ocurre. Y descansa sobre **cinco años**, con las componentes estimadas dentro de la muestra y una correlación de r = −0,886 apoyada en cinco puntos (p = 0,045, justo bajo el umbral convencional). Con dos años más la relación §3 puede cambiar de pendiente o disolverse. Es la mejor lectura disponible, no un resultado asentado.

---

## Anexo — A17 queda cerrada, y el arreglo obvio no servía

`NVCBP11AA` toma 0–6 pero también **8 y 9**, que en Multipropósito son códigos de no-respuesta. La especificación proponía "codificarlos como faltante y excluirlos de la componente de estrato en la distancia". **Las dos formas de hacer eso introducen un sesgo propio**, medidas sobre una población con 30 agentes marcados y \(\bar{k}=5\):

| Tratamiento | Grado de los marcados | Grado del resto |
|---|---|---|
| Omitir la componente y reescalar por el peso disponible | **10,1** | 4,9 |
| Imputar la media en el espacio estandarizado | **0,6** | 5,2 |

El primero los sobreconecta: con una dimensión menos la distancia tiene más varianza, y como \(p_{ij}=e^{-\beta d}\) es convexa, más varianza a igual media da más enlaces. El segundo los aísla: `estrato` es **discreta**, su media cae entre dos niveles, y el agente imputado nunca queda a distancia 0 de nadie mientras que un estrato 3 coincide exacto con todos los demás estratos 3. En un kernel exponencial el grado lo fijan los vecinos más cercanos, no la distancia media — y la distancia media de los marcados era de hecho *menor* que la del resto (2,09 contra 2,21).

**Se resolvió en el origen** (DI-P3): `loader.py` descarta esos registros al construir el receptor —39 de 168.200, un 0,02 %—, y el generador homofílico ahora **rechaza con un mensaje explícito** cualquier población que los traiga, en vez de parchearlos. Arreglar el dato donde nace y hacer que lo de abajo falle fuerte es más barato que compensar aguas abajo.

*El 0 se conserva: la ECP lo etiqueta "conexión ilegal - pirata", que es una categoría real y no una no-respuesta.*
