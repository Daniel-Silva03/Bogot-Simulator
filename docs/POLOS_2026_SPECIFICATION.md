# POLOS 2026 — SPECIFICATION

**¿El polo de derecha que se vio en 2014–2022 anticipa el mapa de Abelardo de la Espriella en Bogotá, primera vuelta de 2026?**

Proyecto: Bogotá Social Simulator
Versión: 0.1 — **pre-registro**
Fecha: 30 de septiembre de 2026
Estado: **código probado en mundos simulados (§8.1); sin ningún dato de 2026 abierto.** Nadie en este proyecto ha descargado ni mirado los resultados de 2026 por mesa o por localidad
Datos: `data/processed/geografia_electoral/resultado.json` (residuos 2014–2022, ya publicados), receptor de Multipropósito 2021 y, después de este documento, los escrutinios por mesa de la Registraduría (primera vuelta, 31 de mayo de 2026)
Origen: la primera pregunta real del frente de escenarios (el jefe de Daniel, 30/09) y `EJE_PARTIDOS_RESULTS.md` §6.4 (probar los dos polos en una elección no mirada)

---

## 1. La pregunta, y por qué no es la que se hizo

La pregunta que llegó fue: *¿el simulador acierta que la población votaría por Abelardo
y que sería el ganador?* No se puede responder honestamente por tres razones, que
quedan escritas para no volver a ellas:

1. **El resultado ya se conoce.** Cualquier supuesto que se escriba hoy está
   contaminado por él; un «acierto» no probaría nada (es el mismo problema que el
   Experimento 9 encontró en el LLM: acertaba donde recordaba).
2. **La población sintética no tiene intención de voto.** Lleva una sola variable de
   opinión, y ninguna fuente pública del proyecto pregunta por candidatos de 2026. Las
   variables demográficas explican R² ≈ 0,02 de la opinión individual.
3. **El proyecto es de Bogotá.** Quién gana es una pregunta nacional.

La pregunta que sí se puede acertar o fallar, porque su respuesta **por localidad** no
la conoce nadie en el proyecto:

> **Con lo que se sabía antes de 2026 —el estrato de cada localidad y la geografía de
> la derecha en 2014, 2018 y 2022—, ¿se puede anticipar en qué localidades de Bogotá
> a Abelardo le fue mejor y peor de lo que dice su estrato?**

Si se puede, la geografía política que encontraron los dos análisis anteriores no es
una descripción del pasado: **sirve para anticipar el mapa de un candidato nuevo**.
Eso le importa al CNC para diseñar muestras y leer encuestas por localidad, aunque no
diga quién gana.

---

## 2. Lo que ya sé antes de empezar (declarado para que se pueda descontar)

- **Del 2026:** mi conocimiento general llega a junio de 2026. Sé que la primera vuelta
  fue el 31 de mayo y que Abelardo de la Espriella fue candidato desde la derecha, por
  fuera de los partidos tradicionales. Daniel dice que ganó la elección. **No sé ni
  recuerdo cómo votó Bogotá por localidad**, no he abierto la página de la
  Registraduría y no voy a buscar resultados en internet antes de subir este
  documento y el código.
- **De 2014–2022:** conozco los residuos de los nueve candidatos presidenciales y de los
  seis partidos del Senado 2018, y la lectura de dos polos (`EJE_PARTIDOS_RESULTS.md`
  §4). Con eso está construida la predicción de §4; no hay otra información.
- **Un riesgo que se ve venir:** si en 2026 hubo más de un candidato de derecha con
  votos importantes en Bogotá, el polo se reparte entre ellos y el resto de Abelardo
  puede parecerse solo a una parte. Eso no cambia la predicción; es una razón por la
  que puede fallar.

---

## 3. Datos

### 3.1 El voto de 2026

Escrutinios por mesa de la **primera vuelta presidencial del 31 de mayo de 2026**,
publicados por la Registraduría. Se descargan (con permiso de Daniel, diciendo
cuántos archivos, de dónde y cuánto pesan) a la carpeta de `BSS_ELECTORAL_DIR`, fuera
del repo, y se agregan con el mismo procedimiento de `src/population/electoral.py`:

- Proporción de **Abelardo** sobre `votos_candidatos` (sin blancos, nulos ni no
  marcados; DI-EL5). El candidato se identifica por nombre en el archivo.
- **Antes de calcular ninguna proporción** se verifica solo la estructura: que las
  zonas 1–20 siguen siendo las localidades (por tamaño contra 2022, como en §14.3 del
  inventario), y que el total de votos de Bogotá cuadra con el que publica la
  Registraduría. El script de construcción imprime estructura y totales, no votos por
  candidato.
- Si la página solo tuviera segunda vuelta, se anota como enmienda antes de abrir nada.

### 3.2 La referencia: el polo de derecha

Los residuos de M1 de `resultado.json`, **sin recalcular**. Cada uno se estandariza
entre las 19 localidades y se promedia:

| Polo | Residuos que lo forman |
|---|---|
| **Derecha** (el que decide) | Zuluaga 2014, Duque 2018, Gutiérrez 2022 |
| Izquierda (para P2) | Clara López 2014, Petro 2018, Petro 2022 |

Se usan solo presidenciales porque la pregunta es presidencial. El polo del Senado
(Centro Democrático 2018) se reporta como secundario, sin umbral. Los tres
residuos de derecha se parecen a su promedio con r = 0,86, 0,96 y 0,84; los dos
polos presidenciales, entre sí, r = −0,70.

### 3.3 La composición y las unidades

Las mismas de `GEOGRAFIA_ELECTORAL_SPECIFICATION.md` §3.2 y §3.3: estrato medio de
Multipropósito 2021 (`x1`), **19 localidades** (sin Sumapaz, que se reporta aparte; sin
las zonas 90 y 98), cada una con el mismo peso.

---

## 4. La predicción, localidad por localidad (escrita antes de ver 2026)

El polo de derecha estandarizado, de mayor a menor. **Se predice que el resto de
Abelardo (lo que el estrato no explica) sigue este orden**: por encima de lo que dice
el estrato arriba de la tabla, por debajo abajo.

| Localidad | Polo derecha | | Localidad | Polo derecha |
|---|---|---|---|---|
| Usaquén | +1,99 | | Tunjuelito | −0,19 |
| Ciudad Bolívar | +1,25 | | Antonio Nariño | −0,22 |
| Los Mártires | +1,00 | | Puente Aranda | −0,25 |
| Suba | +0,90 | | La Candelaria | −0,46 |
| Usme | +0,88 | | Rafael Uribe Uribe | −0,48 |
| Chapinero | +0,57 | | Engativá | −0,59 |
| Bosa | +0,22 | | Fontibón | −0,85 |
| Barrios Unidos | 0,00 | | San Cristóbal | −0,89 |
| Kennedy | −0,13 | | Santa Fe | −1,02 |
| | | | **Teusaquillo** | **−1,72** |

En palabras: **a Abelardo le debería ir mejor de lo que dice el estrato en Usaquén,
Ciudad Bolívar, Los Mártires, Suba y Usme, y peor en Teusaquillo, Santa Fe, San
Cristóbal y Fontibón.**

---

## 5. Método

| Cifra | Qué es |
|---|---|
| **Residuo** | Proporción de Abelardo menos la predicha por M1 (MCO sobre `x1`), como en los dos análisis anteriores |
| **r_der** | Pearson entre el residuo de Abelardo y el polo de derecha; `p` por permutación, 10.000, **una cola** (se predice el signo) |
| r_izq | Pearson entre el residuo de Abelardo y el polo de izquierda |
| **ΔR²_LOO** | R²_LOO de M1 + polo de derecha (dos regresores) menos R²_LOO de M1. Es lo que el polo **añade al estrato fuera de muestra**; el polo está fijo desde antes, así que no se ajusta con los datos de 2026 |
| r_gut | Pearson entre el residuo de Abelardo y el de Gutiérrez 2022 solo: la predicción ingenua «le irá como al último candidato de derecha» |
| Signos | En cuántas de las 19 localidades el residuo tiene el signo que predice §4 (descriptivo) |

**Control de inscripción**, el mismo de los dos análisis anteriores: correlación del
residuo de Abelardo con la razón inscritos 2018 / población 18+.

Las funciones de `geografia_electoral.py` (residuo, R²_LOO, permutación) se reutilizan
sin cambios. Lo nuevo —el polo, el ΔR²_LOO con dos regresores y la lectura de la
regla— se prueba primero en mundos simulados (§8), con la composición real y los polos
reales, antes de abrir 2026.

---

## 6. Predicciones pre-registradas

| # | Predicción | Umbral |
|---|---|---|
| **P1** | **El resto de Abelardo sigue al polo de derecha** | r_der > 0,5 y p < 0,05 |
| P2 | Se parece más a la derecha que al negativo de la izquierda (dos polos, no espejo) | r_der > −r_izq |
| **P3** | **El polo le añade al estrato poder de predicción fuera de muestra** | ΔR²_LOO ≥ 0,05 |
| P4 | El polo promediado no es peor que el último candidato de derecha | r_der ≥ r_gut |
| **P5** | La inscripción no bloquea la lectura | \|r\| < 0,50 |
| P6 | El estrato explica buena parte de su mapa | R²_LOO de M1 ≥ 0,50 *(no informativa: el gradiente norte–sur de la derecha es conocido)* |

**Por qué espero esto.** P1 y P3 porque los tres candidatos de derecha de 2014–2022 y el
Centro Democrático comparten el mismo resto (0,81 a 0,96), y Abelardo se presentó en
ese mismo lugar político. P2 porque el Senado 2018 mostró dos polos; pero los polos
presidenciales están a −0,70 entre sí, así que **P2 tiene poca potencia** y por eso no
decide. P4 porque promediar tres elecciones debería quitar ruido de un candidato. P1 es
la que más puede fallar: Abelardo no venía del Centro Democrático, y si su voto en
Bogotá es otra coalición, su geografía puede ser otra.

---

## 7. Regla de decisión

```
    A. P1, P3 y P5 se cumplen
         → El polo de derecha anticipa el mapa de un candidato nuevo: la
           geografía política de Bogotá no es una descripción del pasado, sirve
           para prever dónde le va mejor o peor a un candidato de derecha, más
           allá de su estrato. Refuerza DI-B10.
           · Con P2: se sostiene la lectura de dos polos (ya no solo descriptiva).
           · Sin P2: el polo funciona, pero esta elección no distingue dos polos
             de un eje.
           · Sin P4: el último candidato predice igual o mejor que el promedio;
             la geografía útil es la reciente.

    B. P1 y P5 se cumplen, P3 no
         → El resto de Abelardo tiene la forma del polo, pero es pequeño frente
           a lo que explica el estrato: para anticipar su mapa basta el estrato.

    C. P1 no se cumple (con P5)
         → El polo no se transfiere a un candidato nuevo. La geografía de la
           derecha de 2014–2022 era la de sus candidatos, no una propiedad
           estable de las localidades. Debilita la lectura de dos polos y el
           uso del mapa de residuos para anticipar elecciones.

    Si P5 falla
         → Intermedio: el patrón puede ser la inscripción. No se adopta lectura.

    Cualquier otro caso → intermedio, reportado sin adoptar lectura.
```

---

## 8. Verificación antes de abrir 2026

`tests/test_polos_2026.py`, con la composición real, los polos reales y votos de
Abelardo **inventados**; 200 semillas por mundo:

| Mundo simulado | Lo que el método debe dar |
|---|---|
| Abelardo = estrato + polo de derecha + ruido | **A** en la gran mayoría |
| Abelardo = estrato + ruido, sin polo | **C** en la gran mayoría; A en ≤ 5 % |
| Abelardo = estrato + el negativo del polo de izquierda | P2 falla más veces que en el primer mundo |
| La «señal» es la razón de inscripción | intermedio, siempre |

El tamaño del ruido de los mundos se fija con el de los residuos reales de 2014–2022.
**Si el método no pasa estas pruebas, no se abre 2026.** Los porcentajes que salgan se
anotan aquí, con fecha, antes de la corrida real.

### 8.1 Resultado de la verificación (30/09/2026, antes de descargar 2026)

`tests/test_polos_2026.py`, 15 pruebas. Composición real, polos reales, base del estrato
tomada del ajuste de M1 de Gutiérrez 2022 y ruido del tamaño de los residuos reales de la
derecha; en el mundo «con polo» el resto de Abelardo se parece al polo con peso 0,85 (lo
que se parecen entre sí los candidatos de derecha, §3.2). 200 semillas por mundo:

| Mundo simulado | Lecturas | P2 se cumple | |
|---|---|---|---|
| Con polo | **A 94 %**, B 5,5 %, intermedio 0,5 % | 99 % | pasa |
| Sin polo | **C 94 %**, intermedio 5 %, B 1 %, **A 0 %** | — | pasa |
| Espejo de la izquierda | — | **0,5 %** | pasa |
| La señal es la inscripción | **intermedio 100 %** | — | pasa |

Las pruebas verifican además que el polo calculado es exactamente la tabla de §4
(DI-P26-3), que Abelardo se busca por nombre y el análisis se detiene si no aparece o
aparece dos veces, y que hoy, sin tabla de 2026, el script falla sin calcular nada.

**Dos cosas que la verificación enseña, sin cambiar la regla:**
- **P2 tiene más potencia de la que §6 suponía**: en estos mundos separa polo de espejo
  casi siempre (99 % contra 0,5 %). Sigue sin decidir, como quedó escrito.
- **La lectura A es exigente cuando el polo es moderado.** Descriptivo, fuera de las
  pruebas: con peso 0,7 sale A el 52 % y B el 41 %; con 0,6, A el 32 %; con 0,5, A el
  13 %. Lo que la frena es P3 (ΔR²_LOO ≥ 0,05): con 19 localidades y un estrato que ya
  explica mucho, un resto que se parece al polo pero no mucho no alcanza a mejorar la
  predicción fuera de muestra. **Un resultado B no querrá decir que el polo no está**;
  querrá decir que no alcanza para mejorar lo que ya dice el estrato.

---

## 9. Límites, dichos antes

- **Todo lo de los análisis anteriores vale aquí:** ecológico (localidades, no
  personas), el voto está donde se está inscrito, la participación varía, la
  composición es de 2021 y hay 19 puntos.
- **No dice nada de quién gana**, ni en Bogotá ni en el país, ni de cuántos votos saca
  Abelardo: la predicción es sobre la **forma** del mapa una vez descontado el estrato.
- **Una sola elección nueva.** Si A se cumple, dice que el polo anticipó 2026, no que
  siempre lo haga.
- **El polo se eligió mirando 2014–2022.** Eso está bien: es la información que había
  antes. Lo que no se puede hacer es cambiar su definición después de ver 2026.
- **La lectura de dos polos entra aquí por primera vez como predicción** (P2), pero con
  poca potencia (§6). Un P2 fallido no la refuta; uno cumplido la apoya poco.

---

## 10. Qué se construye después de este documento

1. `src/experiments/polos_2026.py` y `tests/test_polos_2026.py`, con los mundos de §8.
   Sus porcentajes se anotan en §8.
2. La tabla de 2026: descarga (con permiso), agregación y verificación de estructura y
   totales, sin mirar votos por candidato.
3. La corrida real.
4. `POLOS_2026_RESULTS.md`, **contra este pre-registro**, falle o no.
