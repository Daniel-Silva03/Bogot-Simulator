# POLOS 2026 — RESULTS

**El polo de derecha de 2014–2022 anticipó la forma del mapa de Abelardo en Bogotá, pero apenas: lectura B. Y su geografía se parece más al revés de la izquierda que al polo de derecha.**

Proyecto: Bogotá Social Simulator
Versión: 0.1
Fecha: 30 de septiembre de 2026
Pre-registro: `docs/POLOS_2026_SPECIFICATION.md` (commit `8e77b00`; código y mundos simulados en `f0a4164`; tabla de 2026 en `5e78beb`, todo antes de la corrida)
Código: `src/experiments/polos_2026.py` · Pruebas: `tests/test_polos_2026.py` (15)
Datos: primera vuelta presidencial 2026, escrutinio mesa a mesa de la Registraduría (`DATA_INVENTORY.md` §14.6)
Salida: `data/processed/polos_2026/resultado.json`

---

## 1. Resultado, en una línea

Lo que el estrato no explica del voto por Abelardo se parece al polo de derecha con
**r = 0,51** (p = 0,014): pasa P1 por 0,006. Pero añadir el polo al estrato mejora la
predicción fuera de muestra en **0,047**, y hacía falta 0,05: P3 falla por 0,003. La
regla da **B**: el mapa de Abelardo tiene la forma del polo, pero para anticiparlo
basta el estrato. Las dos cifras que deciden están en el borde; §3 dice cómo leerlo.

Contexto, sin predicción: en Bogotá, Cepeda sacó el 42,4 % de los votos por candidato
y Abelardo el 38,4 %. Paloma Valencia, el 9,3 %.

---

## 2. Contra el pre-registro

| # | Predicción | Umbral | Resultado | |
|---|---|---|---|---|
| **P1** | El resto de Abelardo sigue al polo de derecha | r_der > 0,5 y p < 0,05 | **0,506**, p = 0,014 | se cumple, **por 0,006** |
| P2 | Se parece más a la derecha que al negativo de la izquierda | r_der > −r_izq | 0,51 contra **0,84** | **no se cumple** |
| **P3** | El polo le añade al estrato fuera de muestra | ΔR²_LOO ≥ 0,05 | **0,047** (0,59 → 0,64) | **no se cumple, por 0,003** |
| P4 | El polo no es peor que el último candidato de derecha | r_der ≥ r con Gutiérrez 2022 | 0,51 contra 0,34 | se cumple |
| **P5** | La inscripción no bloquea | \|r\| < 0,50 | −0,18 | se cumple |
| P6 | El estrato explica buena parte | R²_LOO(M1) ≥ 0,50 | 0,59 | se cumple *(no informativa)* |

**Regla de decisión: B**, tal como quedó escrita: *el resto de Abelardo tiene la forma
del polo, pero es pequeño frente a lo que explica el estrato: para anticipar su mapa
basta el estrato.*

Secundarios pre-registrados, sin umbral: con el residuo del Centro Democrático en el
Senado 2018, r = 0,34. Signos: el resto de Abelardo tiene el signo que predecía §4 en
**9 de las 19** localidades. Sumapaz, aparte: 15,7 % observado contra 21,9 % que
predice el estrato.

---

## 3. Cómo leer un B en el borde

- **No se redondea hacia A.** P3 falla por 0,003, y la regla no tiene margen. Si se
  hubiera cumplido, la lectura sería A; no se cumplió.
- **Tampoco se lee como «el polo no está».** §8.1 del pre-registro lo dejó dicho antes:
  con un polo moderado, B es lo más probable aunque el polo exista. Con peso 0,5, los
  mundos simulados daban B el 42 % de las veces, A el 13 % y C el 41 %. Un r de 0,51 es
  justo ese mundo.
- **Lo que sí dice:** el polo de 2014–2022 contiene información real sobre dónde le fue
  mejor o peor a un candidato nuevo de derecha, pero poca. Con 19 localidades y un
  estrato que ya explica el 59 %, no alcanza para mejorar la predicción de forma
  apreciable.

---

## 4. La predicción, localidad por localidad

§4 del pre-registro nombró nueve localidades. Resto de Abelardo en puntos porcentuales
sobre lo que predice su estrato:

| Se predijo mejor que su estrato | Observado | | Se predijo peor que su estrato | Observado |
|---|---|---|---|---|
| Usaquén | **+5,2** ✓ | | Teusaquillo | **−8,1** ✓ |
| Ciudad Bolívar | +0,8 ✓ | | Santa Fe | **−6,8** ✓ |
| Los Mártires | **+6,4** ✓ | | San Cristóbal | **−4,7** ✓ |
| Suba | **+5,3** ✓ | | Fontibón | +2,1 ✗ |
| Usme | −1,8 ✗ | | | |

**Siete de las nueve localidades nombradas salieron en el sentido previsto**, incluidas
las tres más marcadas de cada lado. Pero en toda la tabla son 9 de 19: las localidades
del medio del polo (Kennedy, Tunjuelito, Antonio Nariño, Puente Aranda, Engativá) salen
todas por encima de su estrato, y la predicción las tenía un poco por debajo. Y hay un
error grande: **Chapinero**, que el polo ponía por encima (+0,57), sale en −8,0.

La lista de nueve se escribió para comunicar la predicción, no para decidir; lo que
decide es §2. Se reporta aquí porque es la frase que se le llevó a la dirección.

---

## 5. Lo que dice P2

P2 falla con claridad: el resto de Abelardo se parece **más al revés del polo de
izquierda (0,84) que al polo de derecha (0,51)**. §6 del pre-registro suponía que P2
tenía poca potencia; §8.1, antes de la corrida, mostró que sí la tiene: en los mundos
simulados separaba un polo propio de un espejo el 99 % contra el 0,5 % de las veces.
Así que este fallo informa.

**Qué significa:** en 2026, el voto por Abelardo en Bogotá se ubica, sobre todo, donde
no se votó por la izquierda. Es la lectura de **un eje**, no de dos polos. La lectura de
dos polos salió del Senado 2018 y era descriptiva (`EJE_PARTIDOS_RESULTS.md` §4); esta
es la primera vez que se ponía a prueba, y **en 2026 no se sostiene**. §9 del
pre-registro dijo que un P2 fallido no la refuta, y es cierto: puede ser de 2018 y no
de 2026. Pero la debilita.

---

## 6. Descriptivo, no pre-registrado: por qué el polo se quedó corto

Todo lo de esta sección se calculó **después** de ver el resultado. Sirve para
entenderlo, no como prueba.

**La derecha se repartió**, que es el riesgo que el pre-registro anotó en §2. En los
lugares donde el polo predecía más derecha y Abelardo falló (Chapinero, sobre todo), el
voto de derecha fue a Paloma Valencia (Centro Democrático). Si se suma la derecha de
2026 (Abelardo + Valencia + Uribe Londoño):

| | r_der | r_izq | ΔR²_LOO |
|---|---|---|---|
| Abelardo solo (lo pre-registrado) | 0,51 | −0,84 | 0,047 |
| Derecha de 2026 sumada | 0,67 | −0,92 | 0,067 |

Con esa suma, el resultado habría sido A. **No se adopta**: el pre-registro fijó a
Abelardo, y la suma se eligió viendo los datos.

**El polo de izquierda sí se transfirió a Cepeda**: su resto se parece al polo de
izquierda con r = 0,93. En 2026, la geografía de la izquierda fue más estable que la
de la derecha. Tampoco estaba pre-registrado.

| Candidato 2026 | % en Bogotá | R²_LOO del estrato | r con el polo de derecha | r con el polo de izquierda |
|---|---|---|---|---|
| Iván Cepeda | 42,4 | 0,82 | −0,58 | **+0,93** |
| Abelardo de la Espriella | 38,4 | 0,59 | +0,51 | −0,84 |
| Paloma Valencia | 9,3 | 0,77 | +0,42 | −0,03 |
| Sergio Fajardo | 6,4 | 0,75 | −0,35 | −0,35 |

---

## 7. Lo que este resultado NO dice

- **Nada sobre quién ganó, ni en Bogotá ni en el país.** La pregunta era sobre la forma
  del mapa una vez descontado el estrato.
- **Nada sobre personas.** Es ecológico: localidades, no votantes.
- **No dice que el polo de derecha no exista.** Dice que en 2026 predijo poco del mapa
  de un candidato que compartió la derecha con otros.
- **No convierte en prueba lo de §6.** La derecha sumada y el resultado de Cepeda son
  pistas para el próximo pre-registro, no hallazgos.

---

## 8. Consecuencias

1. **Para la pregunta del jefe de Daniel.** El simulador no dice quién gana, y el
   pre-registro explicó por qué. Lo que sí se probó: con lo que se sabía antes de 2026,
   se anticipó la forma del mapa de Abelardo en Bogotá **en parte**. Siete de las nueve
   localidades nombradas salieron en el sentido previsto, pero la prueba formal da B:
   el polo añadió muy poco a lo que ya dice el estrato. Es un resultado honesto y
   ganado a ciegas: la predicción estaba en GitHub antes de abrir los datos.
2. **Para la lectura de dos polos:** se debilita. En 2026 la geografía se parece más a
   un eje izquierda–no izquierda. El tablero (DI-V59) la presenta como descriptiva; si
   se mantiene, conviene añadir que 2026 no la confirmó.
3. **Para la geografía electoral en general:** se refuerza que hay territorio estable,
   sobre todo en la izquierda (Cepeda, r = 0,93 con el polo, no pre-registrado). La
   evidencia para DI-B10 no cambia de fondo.
4. **Si se quiere seguir probando:** el siguiente pre-registro debería fijar por
   adelantado cómo se trata una derecha repartida (sumar a los candidatos de un lado,
   con una regla escrita antes), y probar el polo de izquierda, que es el que se
   transfirió. La próxima elección que no se haya mirado sería la segunda vuelta de
   2026 o las locales.
