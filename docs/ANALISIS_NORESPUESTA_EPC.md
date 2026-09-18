# La no respuesta en la serie EPC — qué transiciones aguantan y cuáles no

Proyecto: Bogotá Social Simulator
Versión: 1.0
Fecha: 17 de septiembre de 2026
Origen: `claude/ANALISIS_EPC_BCV.md` §3, advertencia pendiente
Método: el mismo de `claude/ANALISIS_NORESPUESTA_2023.md`, aplicado a las nueve olas de cada ítem

---

## 0. El resultado, sin adornos

**Esta vez la amenaza no se descarta.** En la ECP 2023 la no respuesta resultó inocua; aquí es **específica de cada transición**: los cinco movimientos grandes de 2014-2022 son imposibles de explicar por no respuesta, y los tres más recientes **no lo son**.

Conviene decirlo al revés de como suele decirse: el problema no es que la cobertura sea baja, es que en los últimos años la cobertura bajó **y** los movimientos se hicieron pequeños. Las dos cosas juntas.

## 1. La cobertura cae y cae en un escalón

Porcentaje ponderado con respuesta válida en `GG3` (gestión del alcalde):

| 2014 | 2015 | 2017 | 2018 | 2019 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| 94,7 | 94,9 | 96,5 | 97,4 | 94,7 | **84,9** | 84,0 | 81,6 | 80,6 |

No es una deriva: es un escalón de diez puntos entre 2019 y 2022 que después no se recupera.

**No es un cambio del instrumento.** El formulario de 2023 presenta la pregunta igual que siempre, con la escala impresa de 1 a 5 y **sin** opción de "no sabe" a la vista; el código `90` lo agrega la codificación, no la tarjeta. **Tampoco es un filtro**: en 2023 solo 51 personas dicen no conocer a la alcaldesa, contra 237 sin respuesta válida en `GG3`.

Queda como fenómeno sin explicar, y hay dos lecturas que estos datos no separan: que haya menos gente con opinión formada sobre la gestión de su alcalde, o que haya cambiado el trabajo de campo. La primera sería sustantiva e interesante; la segunda, un artefacto. **No lo sé, y no conviene elegir la conveniente.**

## 2. Lo observable no explica nada

Reponderando los válidos a la composición de la muestra completa por sexo × edad × estrato:

| | corrimiento máximo de la media |
|---|---|
| `GG3`, nueve olas | **0,011** |
| `CC5`, nueve olas | **0,010** |

Es decir: **cero**. Los excluidos no se distinguen de los incluidos en nada que la encuesta mida. Eso no es una absolución —si hay sesgo, está en lo no observado— pero cierra la vía barata de corregirlo con pesos.

## 3. La prueba que sí discrimina

En vez de cotas de Manski, que siempre salen anchas y nunca deciden nada, la pregunta útil es: **¿qué media tendrían que tener los excluidos para que el cambio observado desaparezca?** Si la respuesta cae fuera de [1, 5], el cambio es robusto por aritmética.

### GG3 — gestión del alcalde

| Transición | Δ observado | Media requerida de los excluidos | |
|---|---|---|---|
| 2014→2015 | −0,437 | 10,96 | **robusto** |
| 2015→2017 | −0,304 | 10,89 | **robusto** |
| 2017→2018 | +0,262 | −7,60 | **robusto** |
| 2018→2019 | +0,177 | −0,82 | **robusto** |
| 2019→2022 | +0,408 | 0,25 | **robusto** |
| 2022→2023 | −0,093 | 3,44 | *frágil* |
| 2023→2024 | +0,321 | 1,43 | *frágil, pero exigente* |
| 2024→2025 | −0,428 | 4,96 | *frágil, pero al límite* |

### CC5 — gestión del Concejo

Solo **2017→2019** (+0,436) es robusto; las otras siete transiciones requieren valores perfectamente posibles (2,70 · 2,76 · 4,59 · 2,89 · 2,94 · 1,72 · 2,92).

Era de esperarse y no es un defecto del ítem: `CC5` es casi plano, y un cambio pequeño siempre es frágil frente a un 20 % de no respuesta. Sigue sirviendo como control; lo que no sirve es leer sus subidas y bajadas de un año a otro como señal.

## 4. Qué se puede usar, entonces

1. **El tramo 2014-2022 de `GG3` es utilizable tal cual.** Cinco transiciones, todas robustas, cobertura por encima del 94 % salvo el último punto. Es el material para reproducir dinámica.
2. **Las tres transiciones recientes de `GG3` entran con etiqueta.** El salto de 2023→2024 (+0,321) exigiría que los excluidos promediaran 1,43 —casi todos en "muy mala gestión"— lo cual es improbable pero no imposible. La caída de 2024→2025 exigiría 4,96, prácticamente todos en el máximo: más improbable todavía. La baja de 2022→2023 (−0,093) **no está establecida** y no debe contarse como un movimiento.
3. **`CC5` se usa como control de nivel, no de trayectoria.** Su valor es mostrar que otra institución, medida en la misma muestra y el mismo año, no se mueve como el alcalde.
4. **La cobertura se registra como serie propia.** Pasa de ~95 % a ~81 %: si el motor de escenarios habla alguna vez de "la opinión de Bogotá", tiene que decir de cuál Bogotá —la que opina— y esa fracción cambió.

## 5. Decisión de implementación

**DI-B1 — el objetivo se define sobre quienes tienen opinión.** La distribución que los experimentos intentan reproducir es la de las respuestas válidas 1-5, ponderada. Los `90` y faltantes no se imputan: quien no tiene opinión formada no está escondiendo un valor, y rellenarlo inventaría la mitad del fenómeno. La cobertura de cada año se reporta junto a la media y la desviación, siempre, y ninguna comparación entre años se hace sin ella.

---

*Agregados ponderados sobre los microdatos de BCV. Ningún registro individual sale de este análisis.*
