# GEOGRAFÍA ELECTORAL — SPECIFICATION

**¿La composición de cada localidad explica cómo vota, o queda territorio que la composición no ve?**

Proyecto: Bogotá Social Simulator
Versión: 0.1 — **pre-registro**
Fecha: 29 de septiembre de 2026
Estado: **sin código y sin ningún cruce entre voto y composición**
Datos: `data/external/electoral/presidente_1v_*` (D16, `DATA_INVENTORY.md` §14) y el receptor de Multipropósito 2021
Origen: `A08_PASO0B_RESULTS.md` (la composición no reproduce la geografía de la EPC) y la llegada de los resultados electorales por mesa

---

## 1. La pregunta

El paso 0b de A08 encontró territorio real en la opinión de Bogotá (7 de 9 olas de
la EPC) que la composición no reproduce, ni en escala ni en dirección. Pero lo midió
con 60 a 80 personas por localidad y ola: con mucho ruido.

Los resultados electorales no tienen ese problema. Son un **conteo completo**, sin
error de muestreo: 2,5 a 3,8 millones de votos por elección, repartidos en las 20
localidades. Permiten hacer la misma pregunta con una variable política y sin ruido:

> **¿Cuánto de la diferencia entre localidades en el voto presidencial explica su
> composición demográfica? Y lo que no explica, ¿se repite de una elección a otra?**

Si lo que queda se repite, **hay territorio estable que la composición no ve**, que es
justo lo que un mapa construido por composición no puede mostrar.

---

## 2. Lo que ya sé antes de empezar (declarado para que se pueda descontar)

- **Vi las proporciones de voto por localidad** de los nueve candidatos (conversación
  del 29/09, al construir la tabla). Hay un gradiente fuerte: Petro 2022 va del 26 %
  en Usaquén al 66 % en Usme.
- **No he cruzado el voto con ninguna variable de composición.** Pero sé, como
  conocimiento general, que en Bogotá el estrato sigue un gradiente norte–sur
  parecido. Por eso P1 es casi segura, y **no es la predicción informativa**. Las que
  pueden fallar de verdad son P3, P4 y P5.

---

## 3. Datos

### 3.1 El voto

`presidente_1v_localidad.csv` y `presidente_1v_zonas.csv`. Por localidad, la
**proporción de votos por candidato** sobre `votos_candidatos` (DI-EL5).

**Nueve resultados**: los tres candidatos con más votos en Bogotá en cada elección.

| Elección | Candidatos |
|---|---|
| 2014 | Zuluaga, Clara López, Santos |
| 2018 | Fajardo, Petro, Duque |
| 2022 | Petro, Hernández, Gutiérrez |

### 3.2 La composición

Receptor de Multipropósito 2021, adultos de 18 años o más, cargado con
`load_multiproposito_receptor` y ponderado por `FEX_C`, igual que en el resto del
proyecto (estrato 0–6 con los códigos 8 y 9 fuera, DI-P3; educación en la escala 0–5).
Por localidad:

| Variable | Definición |
|---|---|
| `x1` | **estrato medio** |
| `x2` | proporción con educación universitaria o posgrado (niveles 4 y 5) |
| `x3` | edad media |

### 3.3 Las unidades

**19 localidades.** Quedan fuera:
- **Sumapaz**: es rural, tiene 2.700 votantes y un voto extremo (80 % Petro en 2022).
  En una regresión de 20 puntos domina el ajuste. Se reporta aparte.
- **Las zonas 90 (Corferias) y 98 (cárceles)**: no son localidades (§14.3).

Cada localidad pesa lo mismo: la pregunta es sobre el patrón territorial, no sobre el
total de la ciudad.

---

## 4. Método

Para cada uno de los nueve resultados:

| Cifra | Qué es |
|---|---|
| **M1** | Regresión lineal (MCO, con intercepto) de la proporción de voto sobre `x1` |
| M2 | La misma, sobre `x1`, `x2` y `x3` |
| **R²_LOO** | R² fuera de muestra, dejando una localidad fuera cada vez: 1 − PRESS / SC_total. Con 19 puntos, el R² dentro de muestra premia el sobreajuste; este no |
| `p_perm` | Se permutan los resultados entre localidades 10.000 veces y se recalcula R²_LOO: ¿la composición explica más que una asignación al azar? |
| `sd_loc` | Desviación estándar de la proporción entre localidades: cuánta geografía hay que explicar |
| **Residuo** | Observado menos lo predicho por M1, por localidad: el territorio que el estrato no ve |
| **Persistencia** | Correlación de Pearson de los residuos de M1 entre dos resultados, con `p` por permutación (10.000) |

La persistencia principal es la de **Petro 2018 contra Petro 2022**: el mismo
candidato en dos elecciones. Además se reporta, sin que decida nada, la matriz
completa de 9 × 9 correlaciones de residuos.

### 4.1 Verificación antes de tocar los datos reales

El código se prueba primero con **mundos simulados** de 19 localidades con la
composición real, en los que la respuesta se conoce:

| Mundo simulado | Lo que el método debe dar |
|---|---|
| El voto es solo composición, más ruido | R²_LOO alto y persistencia cercana a 0 |
| Composición más un efecto de localidad fijo entre elecciones | persistencia alta |
| El voto no tiene relación con la composición | R²_LOO ≤ 0 y `p_perm` < 0,05 en cerca del 5 % de los casos, no más |

**Si el método no pasa estas tres pruebas, no se corre sobre los datos reales.**

---

## 5. Predicciones pre-registradas

| # | Predicción | Umbral |
|---|---|---|
| **P1** | El estrato solo explica la mayor parte de la geografía de Petro 2022 | R²_LOO de M1 ≥ 0,70 |
| **P2** | La composición explica una parte importante de la geografía del voto en general | mediana de R²_LOO de M1 sobre los 9 resultados ≥ 0,50 |
| **P3** | Agregar educación y edad no mejora de forma material | R²_LOO(M2) − R²_LOO(M1) < 0,10 para Petro 2022 |
| **P4** | **Lo que el estrato no explica se repite**: hay territorio estable | persistencia Petro 2018 → Petro 2022: r > 0,5 |
| **P5** | La composición explica más que el azar en la mayoría de los resultados | `p_perm` < 0,05 en al menos 6 de los 9 |

**Por qué espero esto.** P1 y P2 porque el gradiente se parece al del estrato (§2).
P3 porque en Bogotá estrato, educación y edad van juntos, y con 19 puntos cada
variable extra le cuesta más al R²_LOO de lo que aporta. P4 es la que menos sé: la
espero porque el paso 0b encontró territorio en la EPC que la composición no ve, y el
voto debería mostrarlo más limpio. **Si P4 falla, el territorio que vio el paso 0b
podría haber sido ruido de muestra**, y eso cambiaría la lectura de A08.

---

## 6. Regla de decisión

```
    A. R²_LOO(M1, Petro 2022) ≥ 0,80  y  persistencia r < 0,30
         → A nivel de localidad, la geografía del voto es composición.
           Un mapa por composición podría representarla, y el problema del
           paso 0b sería el constructo o el donante, no el territorio.

    B. R²_LOO(M1, Petro 2022) ≥ 0,50  y  persistencia r ≥ 0,50
         → Hay territorio estable que la composición no ve. Un mapa por
           composición lo subestima siempre en los mismos lugares. El mapa de
           residuos es un resultado publicable («lo que el estrato no explica»),
           y es evidencia a favor de un donante con localidad (reabrir DI-B10).

    C. R²_LOO(M1, Petro 2022) < 0,50
         → La composición no explica la geografía del voto. Un mapa por
           composición la representaría mal. Refuerza el paso 0b.

    Cualquier otro caso (por ejemplo, R² entre 0,50 y 0,80 con persistencia
    entre 0,30 y 0,50)
         → Resultado intermedio: se reporta sin adoptar ninguna de las tres
           lecturas.
```

**Lo que esta regla no decide:** publicar el voto por localidad en el tablero. Eso es
una medición y se puede mostrar sea cual sea el resultado, con sus salvedades
(§14.3). Es una decisión aparte.

---

## 7. Límites, dichos antes

- **Es un análisis ecológico.** Dice cómo votan las localidades, no las personas. Que
  el estrato medio de una localidad prediga su voto no quiere decir que cada persona
  vote según su estrato.
- **El voto está donde se está inscrito; la composición, donde se vive** (§14.3). El
  centro tiene hasta 3 veces más inscritos que adultos. Esto mete ruido en la relación
  y, sobre todo, **puede crear persistencia falsa**: si el desajuste entre inscripción y
  residencia es estable, el mismo sesgo aparece en todas las elecciones. Para
  separarlo, el residuo se correlaciona también con la razón potencial / población
  (§14.3), y si esa correlación es fuerte, **P4 no se puede leer como territorio**.
  > **Enmienda 1 — 29/09/2026, antes de escribir el código y de cualquier cruce.**
  > «Fuerte» no estaba definido. Se fija: la razón es potencial electoral 2018
  > (hoja `DIVIPOL`) sobre población 18+ del marginal. Si |r| ≥ 0,50 entre esa razón
  > y el residuo de M1 de Petro 2018 **o** de Petro 2022, P4 se reporta como
  > **no interpretable como territorio**, y la lectura B de la regla de decisión
  > no se puede adoptar: el resultado pasa a intermedio.
- **La participación varía entre localidades.** La composición es de todos los adultos;
  el voto, solo de quienes votaron.
- **Composición de 2021 para elecciones de 2014 a 2022.** Se supone estable.
- **19 puntos.** Por eso se usa R²_LOO y permutación, y ningún umbral se lee como
  significancia fina.
- **Tres candidatos por año, elegidos por votos en Bogotá.** Los candidatos con poca
  variación entre localidades tendrán R² bajo aunque la composición no falle: `sd_loc`
  se reporta al lado de cada R².

---

## 8. Qué se construye después de este documento

1. `src/experiments/geografia_electoral.py` y `tests/test_geografia_electoral.py`,
   con los tres mundos simulados de §4.1.
2. Solo si pasan: la corrida sobre los datos reales.
3. `GEOGRAFIA_ELECTORAL_RESULTS.md`, **contra este pre-registro**.
