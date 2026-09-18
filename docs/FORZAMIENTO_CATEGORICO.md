# El forzamiento categórico — y por qué disuelve la tercera perilla

Proyecto: Bogotá Social Simulator
Versión: 1.0
Fecha: 17 de septiembre de 2026
Origen: `claude/ANALISIS_TERCERA_PERILLA.md` §3 dejó la tarea: "el modelo categórico probado aquí es el más tosco posible; uno que transporte masa entre categorías sujeto a restricciones de momentos debería ganarle a los dos".
Código: `src/opinion/forzamiento_categorico.py` (DI-G1..DI-G5) · `tests/test_forzamiento_categorico.py`, 16 pruebas

---

## 0. El resultado

**Dos números exógenos por periodo, aplicados como un ladeo exponencial sobre el soporte propio de la variable, reproducen las distribuciones observadas dentro del ruido muestral.** En las dos fuentes, con las dos escalas.

| | afín (lo que el proyecto usaba) | **ladeo categórico** | piso de ruido |
|---|---|---|---|
| ECP — índice de confianza, 2013→2023 | 0,5775 · **3,15×** | **0,1788 · 0,97×** | 0,1835 |
| EPC A — gestión del alcalde, 2014→2025 | 2,6590 · 6,15× | **0,6808 · 1,57×** | 0,4323 |
| EPC B — diferencia individual | 2,2211 · 4,90× | **0,6789 · 1,50×** | 0,4537 |

En la ECP queda **por debajo del piso**: indistinguible de dos muestras de la misma distribución.

**No hace falta una tercera perilla.** Ni la forma derivada del nivel, ni el ancho de difuminado. Las dos estaban compensando la misma cosa: que el forzamiento era una transformación afín sobre una variable que no vive en un continuo.

---

## 1. Qué se construyó

Dada la distribución actual `p` sobre el soporte de la variable y dos momentos objetivo, encontrar la distribución `q` **sobre el mismo soporte** que los acierta y que es la más cercana a `p`; después repartir los agentes en ella.

Dos métodos, y no dan lo mismo:

**Ladeo exponencial** (por defecto, DI-G1): \(q_k \propto p_k \cdot e^{\lambda_1 k + \lambda_2 k^2}\). Dos parámetros para dos momentos, igual que el afín. Se eligió por tres propiedades, no por conveniencia: es la distribución de **máxima entropía** entre las que cumplen las restricciones —la que menos información añade—, **preserva los ceros** (una categoría que nadie eligió sigue vacía), y con \(\lambda_2\) pequeño **preserva el orden estocástico** (subir el nivel no puede engordar la categoría más baja).

**Transporte de mínimo movimiento** (DI-G2): un programa lineal que minimiza \(W_1(p,q)\) sujeto a los momentos. La restricción de varianza es lineal en `q` una vez fijada la media, así que es un LP exacto, no una aproximación.

**Los agentes se reparten preservando el rango** (DI-G3): quien estaba más arriba queda más arriba, igual que bajo una transformación afín. Sin un mecanismo que justifique los cruces, inventarlos sería meter dinámica social por la puerta de atrás — justo lo que siete experimentos dicen que no está identificado.

## 2. El transporte pierde, y la razón es interesante

| | Objetivo A | Objetivo B |
|---|---|---|
| **Ladeo** | **0,6808** | **0,6789** |
| Transporte de mínimo movimiento | 3,7668 | 3,1000 |

El LP hace exactamente lo que se le pide —las pruebas verifican que mueve menos masa que el ladeo— y aun así ajusta cuatro veces peor. La razón es estructural: las soluciones de un programa lineal están en los vértices del polítopo, o sea que son **dispersas**. Mover la menor masa posible sujeto a dos momentos produce distribuciones con picos artificiales.

> **Lo que hay que minimizar es información, no masa.** El ladeo, que minimiza la divergencia respecto de la distribución actual, conserva la forma; el transporte, que minimiza el movimiento, la destruye concentrando.

Se conservan los dos en el módulo porque la comparación es el argumento: sin el transporte, elegir el ladeo sería una preferencia y no un resultado.

## 3. Por qué esto no es trampa

Tres controles, porque el resultado es grande y conviene desconfiar de él.

**El ladeo usa exactamente la misma información que el afín**: la media y la desviación estándar observadas del año objetivo. Ni un dato más. Lo único que cambia es la forma funcional del forzamiento.

**Los momentos se aciertan exactamente** — error máximo del orden de 10⁻¹⁶ en las dos escalas y en todos los años, igual que el afín. No hay grados de libertad escondidos.

**La grilla no filtra información.** La preocupación legítima es que el soporte de la ECP se estimó de los datos, incluidos los años objetivo. Se repitió con tres grillas:

| Grilla | \(W_1\) total |
|---|---|
| Unión de los soportes de los cinco años | 0,1788 |
| **Solo el año base, 2013** | **0,1788** |
| **Teórica: todas las medias de k de 13 ítems en 1-5** *(no usa ningún dato)* | **0,1788** |

Idéntico a cuatro decimales en las tres. El soporte es una propiedad del instrumento, no de la muestra.

## 4. Qué queda revocado, y qué se sostiene

**Se revoca la tercera perilla.** `claude/ANALISIS_RESIDUO.md` concluyó "tres perillas, y la tercera atada al nivel"; `claude/ANALISIS_TERCERA_PERILLA.md` confirmó que la forma-desde-el-nivel y el ancho de difuminado eran cosas distintas. **Las dos eran parches del mismo error de especificación.** Con el forzamiento correcto, la forma no hay que declararla ni derivarla: sale sola del ladeo.

Conviene decir qué tenían de correcto esos análisis: **midieron bien que faltaba algo, y midieron bien cuánto.** Lo que ninguno de los dos consideró es que lo que faltaba no fuera un parámetro sino una forma funcional. Es el mismo error de forma que DI-M1: buscar el arreglo aguas abajo de donde está el problema.

**Se sostiene el veredicto sobre el ABM, y se refuerza mucho.** Los Experimentos 3 a 7 compararon mecanismos contra baselines que **todos** usaban forzamiento afín, así que el defecto era común y las comparaciones siguen siendo válidas. Pero ahora el listón está mucho más alto: si dos números exógenos por periodo llegan al piso de ruido, **no queda residuo que un mecanismo social pueda explicar.** La pregunta "¿aporta el ABM?" pasa de "casi nada" a "no hay dónde aportar".

**Lo que este resultado NO dice.** Es descriptivo, no generativo: dice que la distribución de cada año es alcanzable desde la anterior con dos números, **no** que esos dos números se puedan predecir. El motor de escenarios sigue necesitando que alguien los declare como supuesto. Y no dice nada sobre por qué la opinión se mueve.

## 5. Qué cambia en el diseño del motor

1. **Un escenario se declara con dos números por periodo**: nivel y dispersión. Se acabó la discusión de la tercera perilla.
2. **El forzamiento es el ladeo sobre el soporte de la variable.** Para ítems de 5 categorías, para índices de 154 valores, y para la diferencia individual de 9: el mismo código, la misma interfaz.
3. **El motor tiene que rechazar escenarios imposibles.** En una escala acotada no todo par (media, sd) existe: fijada la media, la desviación tiene un máximo y un mínimo. `rango_de_sd()` los da y el módulo levanta `ForzamientoInfactible` con el rango, en vez de devolver algo. Un laboratorio de escenarios tiene que poder decir "esa combinación no existe en esta escala".
4. **`src/opinion/forzamiento.py` queda para variables continuas** y para reproducir los experimentos históricos. No se borra: los Experimentos 4 a 7 se reportan contra él.

---

*16 pruebas en `tests/test_forzamiento_categorico.py`, incluidas las tres propiedades que justifican elegir el ladeo (preserva ceros, preserva orden estocástico, no mueve una distribución que ya cumple) y el control de que el reparto por rango no invierte ningún par.*
