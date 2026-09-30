# SEGUNDA VUELTA 2026 — SPECIFICATION

**¿La primera vuelta, sumada por bloques, anticipa en qué localidades de Bogotá gana cada candidato en la segunda vuelta de 2026, y por cuánto?**

Proyecto: Bogotá Social Simulator
Versión: 0.1 — **pre-registro**
Fecha: 30 de septiembre de 2026
Estado: **sin código y sin ningún dato de la segunda vuelta abierto.** Nadie en este proyecto ha descargado ni mirado la segunda vuelta de 2026
Datos: `data/external/electoral/presidente_1v_*` (primera vuelta 2026, `DATA_INVENTORY.md` §14.6) y, después de este documento, el escrutinio mesa a mesa de la segunda vuelta (21 de junio de 2026)
Origen: la segunda pregunta del jefe de Daniel (30/09), después de `POLOS_2026_RESULTS.md`

---

## 1. La pregunta

En la segunda vuelta solo hay dos candidatos: Iván Cepeda y Abelardo de la Espriella.
La pregunta del jefe de Daniel es **en qué localidades gana cada uno**.

Con los datos de la primera vuelta, esa pregunta es fácil en la mayoría de las
localidades y difícil en unas pocas. Para que la prueba informe, se compara una regla
que usa lo que se sabía el 1 de junio con una regla ingenua, y se mide dónde difieren.

> **¿Sumar la primera vuelta por bloques (la derecha junta, el centro repartido)
> anticipa la segunda vuelta mejor que suponer que cada candidato conserva lo suyo?**

---

## 2. Lo que ya sé antes de empezar (declarado para que se pueda descontar)

- **La primera vuelta de 2026 por localidad**: la miré al correr `POLOS_2026`. Es la
  información que cualquiera tenía el 1 de junio, antes de la segunda vuelta, y es
  la base legítima de la predicción.
- **De la segunda vuelta:** mi conocimiento general llega a junio de 2026. Sé que
  existió, el 21 de junio, entre Cepeda y Abelardo. Daniel dice que Abelardo ganó la
  elección nacional. **No sé ni recuerdo cómo votó Bogotá**, ni en total ni por
  localidad, y no voy a buscarlo antes de subir este documento y el código.
- **Una corrección antes de escribir** (no es enmienda, nada estaba subido): le dije a
  Daniel que las dos reglas de §4 predecirían ganadores distintos en varias
  localidades. Al calcularlas, **coinciden en las 20**. Por eso lo que decide (§6) no
  es contar ganadores por localidad, sino el margen y el ganador de la ciudad.

---

## 3. Datos

### 3.1 La primera vuelta (la base)

Proporciones sobre `votos_candidatos` (DI-EL5) por localidad, primera vuelta 2026.
Los candidatos se asignan a bloques **aquí, antes de ver nada**:

| Bloque | Candidatos | % en Bogotá (1ª vuelta) |
|---|---|---|
| **Izquierda** | Iván Cepeda | 42,43 |
| **Derecha** | Abelardo de la Espriella, Paloma Valencia, Miguel Uribe Londoño | 47,76 |
| **Resto** (se reparte mitad y mitad) | Sergio Fajardo, Claudia López, Raúl Santiago Botero, Óscar Mauricio Lizcano, Sondra Macollins Garvin, Roy Barreras, Gustavo Matamoros | 9,81 |

Los candidatos menores cuya ubicación no es clara van al resto, y el resto se reparte
por igual: es el supuesto neutral, y juntos suman menos del 1 %.

### 3.2 La segunda vuelta (lo que se predice)

Escrutinio mesa a mesa de la Registraduría (el MMV de la comisión general de Bogotá,
como en la primera vuelta), descargado con permiso de Daniel a `BSS_ELECTORAL_DIR`, agregado con
`src/population/electoral.py` y verificado como la primera vuelta (DI-EL10), antes de
calcular ninguna proporción. Lo que se predice es **la proporción de Cepeda sobre los
votos por los dos candidatos** (sin blancos, nulos ni no marcados).

### 3.3 Las unidades

**Las 20 localidades, Sumapaz incluida**: aquí no hay regresión que Sumapaz pueda
dominar. Sin las zonas 90 (Corferias) y 98 (cárceles), que no son localidades. Para el
ganador de la ciudad, **todo Bogotá, incluidas 90 y 98**.

---

## 4. Las dos reglas

| Regla | Proporción de Cepeda en la segunda vuelta |
|---|---|
| **Bloques** (la que se pone a prueba) | izquierda + ½ · resto, de la primera vuelta |
| **Ingenua** (contra la que se compara) | Cepeda / (Cepeda + Abelardo), de la primera vuelta |

La ingenua supone que cada candidato conserva lo suyo y los demás votantes se reparten
como los de los dos primeros. La de bloques supone que la derecha de la primera vuelta
se junta detrás de Abelardo.

---

## 5. La predicción, localidad por localidad (escrita antes de ver la segunda vuelta)

Proporción de Cepeda sobre los votos de los dos candidatos.

| Localidad | Bloques | Ingenua | Gana (las dos reglas) |
|---|---|---|---|
| Usaquén | 27,0 | 29,2 | Abelardo |
| Chapinero | 30,6 | 36,2 | Abelardo |
| Barrios Unidos | 36,9 | 40,3 | Abelardo |
| Suba | 38,7 | 42,6 | Abelardo |
| Fontibón | 41,7 | 45,8 | Abelardo |
| Teusaquillo | 42,1 | 47,7 | Abelardo |
| Puente Aranda | 42,3 | 45,9 | Abelardo |
| Los Mártires | 42,4 | 45,9 | Abelardo |
| Engativá | 44,4 | 48,9 | Abelardo |
| Antonio Nariño | 45,3 | 49,9 | Abelardo |
| **Kennedy** | **50,2** | 55,0 | **Cepeda** |
| Tunjuelito | 53,1 | 58,2 | Cepeda |
| Rafael Uribe Uribe | 56,8 | 62,3 | Cepeda |
| La Candelaria | 58,7 | 65,8 | Cepeda |
| Santa Fe | 59,7 | 66,8 | Cepeda |
| Bosa | 61,4 | 67,0 | Cepeda |
| San Cristóbal | 62,4 | 68,7 | Cepeda |
| Ciudad Bolívar | 62,7 | 68,4 | Cepeda |
| Usme | 65,6 | 71,5 | Cepeda |
| Sumapaz | 78,6 | 83,1 | Cepeda |

**En palabras: Abelardo gana en el norte, el occidente y el centro ampliado (10
localidades); Cepeda gana en el sur y el suroriente (10).** Las más disputadas:
**Kennedy** (50,2 por la regla de bloques: una moneda al aire), Antonio Nariño y
Engativá.

**Bogotá en total** (con las zonas 90 y 98): la regla de bloques da **Cepeda 47,3 %:
gana Abelardo**. La ingenua da Cepeda 52,5 %: gana Cepeda.

---

## 6. Predicciones pre-registradas

| # | Predicción | Umbral |
|---|---|---|
| **P1** | **Abelardo gana Bogotá en total** (lo que dice la regla de bloques y no la ingenua) | proporción de Cepeda en la ciudad < 50 % |
| **P2** | **La regla de bloques se equivoca menos en el margen** | error absoluto medio de la proporción de Cepeda en las 20 localidades: bloques < ingenua |
| P3 | Los ganadores por localidad salen como en §5 | al menos 18 de 20 *(no informativa: las dos reglas dicen lo mismo)* |
| P4 | El orden de las localidades se conserva | Spearman entre §5 y lo observado ≥ 0,90 *(no informativa: la geografía de Cepeda es muy estable, `POLOS_2026_RESULTS.md` §6)* |

**Por qué espero esto.** Abelardo y Valencia compartían electorado, y en la primera
vuelta la derecha sumada pasó a la izquierda en Bogotá. Lo que puede fallar: que los
votantes de Valencia no fueran a votar, que parte del centro votara en bloque por
Cepeda, o que la participación cambiara distinto en el norte y en el sur. **P1 es la que
más puede fallar**, porque depende de todo el nivel de la ciudad.

**Lo que P1 y P2 miden, dicho claro:** las dos reglas difieren casi solo en un
desplazamiento parejo de unos 5 puntos. Así que las dos predicciones miden, sobre todo,
**una sola cosa: si la derecha de la primera vuelta se juntó detrás de Abelardo.**

---

## 7. Regla de decisión

```
    A. P1 y P2 se cumplen
         → El voto se movió por bloques: la derecha de la primera vuelta se juntó
           detrás de Abelardo, y sumar por bloques anticipa la segunda vuelta mejor
           que suponer que cada candidato conserva lo suyo.

    B. P2 se cumple, P1 no
         → Los márgenes por localidad los anticipa mejor la regla de bloques, pero
           el nivel de la ciudad quedó del lado de Cepeda: la derecha se juntó solo
           en parte.

    C. Ni P1 ni P2
         → La regla ingenua anticipa mejor: la derecha de la primera vuelta no se
           juntó detrás de Abelardo en Bogotá.

    Cualquier otro caso (P1 sin P2) → intermedio, reportado sin adoptar lectura.
```

P3 y P4 se reportan siempre, con la advertencia de que no deciden.

---

## 8. Verificación antes de abrir la segunda vuelta

`tests/test_segunda_vuelta_2026.py`, con la primera vuelta real y segundas vueltas
**inventadas**:

| Mundo inventado | Lo que el método debe dar |
|---|---|
| La segunda vuelta es exactamente la regla de bloques, más ruido | **A** |
| Es exactamente la regla ingenua, más ruido | **C** |
| A mitad de camino entre las dos reglas | la lectura que corresponda a sus cifras, calculada a mano en la prueba |

**B es rara por construcción:** como las dos reglas difieren en un desplazamiento
casi parejo (§6), mejorar el margen en las localidades y perder la ciudad a la vez
exige que el voto se mueva distinto en las localidades que en las zonas 90 y 98. Se
deja en la regla porque puede pasar, no porque se espere.

Las pruebas verifican también que la tabla de §5 sale del código tal cual (si alguien
cambia la primera vuelta o la asignación a bloques, falla), y que sin datos de la
segunda vuelta el análisis se detiene sin calcular nada.

---

## 9. Límites, dichos antes

- **Ecológico:** localidades, no personas. Que una localidad vote por bloques no dice
  que cada votante lo haga.
- **La participación cambia entre vueltas**, y ninguna de las dos reglas la modela.
- **El voto está donde se está inscrito**, como en todos los análisis electorales del
  proyecto.
- **Una sola elección.**
- **Los ganadores por localidad no distinguen las reglas** (§2): lo que se le puede
  mostrar a la dirección, localidad por localidad, es fácil de acertar. Lo que decide
  es el margen y la ciudad.

---

## 10. Qué se construye después de este documento

1. `src/experiments/segunda_vuelta_2026.py` y `tests/test_segunda_vuelta_2026.py`, con los
   mundos de §8.
2. Revisar si la Registraduría publicó la segunda vuelta mesa a mesa (solo estructura),
   y pedir permiso para descargarla.
3. La tabla, verificada; la corrida; `SEGUNDA_VUELTA_2026_RESULTS.md`, **contra este
   pre-registro**, falle o no.
