# GEOGRAFÍA ELECTORAL — RESULTS

**La composición explica la mayor parte de cómo vota cada localidad, pero no todo, y lo que queda se repite de 2014 a 2022: hay territorio estable que la composición no ve.**

Proyecto: Bogotá Social Simulator
Versión: 0.1
Fecha: 29 de septiembre de 2026
Pre-registro: `docs/GEOGRAFIA_ELECTORAL_SPECIFICATION.md` (v0.1 y enmienda 1; código y mundos simulados subidos antes de la corrida, commit `4422073`)
Código: `src/experiments/geografia_electoral.py` · Pruebas: `tests/test_geografia_electoral.py` (15)
Salida: `data/processed/geografia_electoral/resultado.json`

---

## 1. Resultado, en una línea

El estrato medio de cada localidad explica, fuera de muestra, el **84 %** de la
diferencia entre localidades en el voto por Petro en 2022. El 16 % restante no es
ruido: **se repite con r = 0,87 entre 2018 y 2022**, y sigue un eje izquierda–derecha
que ya estaba en 2014. **Se cumplen las cinco predicciones y la regla de decisión da la
lectura B.**

---

## 2. La tabla

19 localidades (sin Sumapaz, §3.3). Proporción sobre votos por candidato.

| Resultado | sd entre localidades | R²_LOO M1 (estrato) | R²_LOO M2 (+ educación, edad) | `p_perm` |
|---|---|---|---|---|
| 2014 Zuluaga | 2,6 pp | −0,36 | 0,25 | 0,98 |
| 2014 Clara López | 4,4 pp | 0,62 | 0,64 | 0,0001 |
| 2014 Santos | 3,1 pp | 0,09 | −0,20 | 0,024 |
| 2018 Fajardo | 6,5 pp | 0,50 | 0,62 | 0,0001 |
| **2018 Petro** | **12,7 pp** | **0,85** | 0,84 | 0,0001 |
| 2018 Duque | 5,5 pp | 0,65 | 0,65 | 0,0001 |
| **2022 Petro** | **12,0 pp** | **0,84** | 0,80 | 0,0001 |
| 2022 Hernández | 3,4 pp | −0,29 | 0,09 | 0,87 |
| 2022 Gutiérrez | 8,8 pp | 0,89 | 0,86 | 0,0001 |

**Persistencia** del residuo de M1, Petro 2018 → Petro 2022: **r = 0,874** (p = 0,0001).

**Control de inscripción** (enmienda 1): correlación del residuo con la razón
inscritos / adultos, 0,21 (2018) y 0,23 (2022). Por debajo del umbral de 0,50: **la
persistencia se puede leer como territorio.**

---

## 3. Contra el pre-registro

| # | Predicción | Umbral | Resultado | |
|---|---|---|---|---|
| P1 | El estrato explica la geografía de Petro 2022 | R²_LOO ≥ 0,70 | 0,84 | se cumple *(no informativa, §2 del pre-registro)* |
| P2 | La composición explica buena parte del voto en general | mediana de R²_LOO ≥ 0,50 | 0,62 | se cumple |
| P3 | Educación y edad no agregan | ganancia < 0,10 | −0,04 | se cumple |
| P4 | Lo que el estrato no explica se repite | r > 0,5 | **0,87** | **se cumple** |
| P5 | La composición supera al azar en la mayoría | ≥ 6 de 9 | 7 de 9 | se cumple |

**Regla de decisión: B.** R²_LOO de 0,84 (≥ 0,50) y persistencia de 0,87 (≥ 0,50),
sin que la enmienda 1 la bloquee: **hay territorio estable que la composición no ve.**

Dos cosas de la tabla que conviene no pasar por alto:
- **Los dos resultados en los que la composición no explica nada** (Zuluaga 2014 y
  Hernández 2022, R² negativo) son los de menos geografía: 2,6 y 3,4 pp entre
  localidades. Es la salvedad anticipada en el §7 del pre-registro: casi no hay nada
  que explicar.
- **M2 no mejora a M1 en los resultados con más geografía** (Petro, Gutiérrez,
  Duque). El estrato ya contiene lo que aportan educación y edad.

---

## 4. Qué es ese territorio

### 4.1 Dónde está

Lo que el estrato no explica del voto por Petro 2022, en puntos porcentuales:

| Más a la izquierda de lo que predice su estrato | | Menos | |
|---|---|---|---|
| Teusaquillo | +8,0 | Suba | −6,9 |
| Santa Fe | +6,4 | Usaquén | −6,6 |
| Chapinero | +4,8 | Barrios Unidos | −3,8 |
| San Cristóbal | +4,4 | Engativá | −3,4 |
| Rafael Uribe Uribe | +3,3 | Los Mártires | −2,7 |
| La Candelaria | +2,1 | Ciudad Bolívar | −2,6 |

El centro (Teusaquillo, Santa Fe, Chapinero, La Candelaria) y el suroriente (San
Cristóbal, Rafael Uribe) votan más a la izquierda de lo que dice su estrato; el
noroccidente (Suba, Usaquén, Barrios Unidos, Engativá), menos. La desviación del
residuo es de unos 4 pp, contra 12 pp de geografía total.

### 4.2 No es Petro: es un eje que ya estaba en 2014

La matriz de correlaciones de residuos entre los nueve resultados (pre-registrada
como descriptiva, sin que decida nada) muestra que el patrón se repite con otros
candidatos:

| Residuo de… | contra Petro 2022 |
|---|---|
| Clara López 2014 | **+0,68** |
| Santos 2014 | +0,46 |
| Duque 2018 | **−0,80** |
| Gutiérrez 2022 | −0,64 |

Y entre elecciones, sin Petro de por medio: Zuluaga 2014 contra Duque 2018, **+0,80**;
Clara López 2014 contra Gutiérrez 2022, **−0,84**. Es un **eje izquierda–derecha con
geografía propia**, estable durante ocho años y tres elecciones, que la composición no
captura.

---

## 5. Un control que no estaba pre-registrado: la participación

**No pre-registrado.** Se añadió después de ver los resultados porque el pre-registro
controlaba la inscripción pero no la participación, y una participación distinta entre
localidades también podría fabricar un patrón estable.

- La participación 2018 (votos / inscritos) va de 59 % en Santa Fe a 74 % en Suba. Se
  correlaciona con el residuo de Petro: **−0,62 en 2018** (p = 0,005) y −0,45 en 2022
  (p = 0,055). Donde vota una parte menor de los inscritos, Petro saca más de lo que
  predice el estrato.
- **Pero no explica la persistencia.** Con la participación dentro del modelo, el
  R²_LOO de Petro 2022 sube a 0,87 y **la persistencia sigue en r = 0,84** (p = 0,0001).
  El eje izquierda–derecha incluso se hace más nítido: Clara López 2014 contra Petro
  2022, +0,77; Duque 2018 contra Petro 2022, −0,91.

La lectura B sobrevive a este control. Parte del residuo de algunas localidades sí
cambia: Los Mártires pasa de −2,7 a −6,3 y Chapinero de +4,8 a +1,2. El mapa de
residuos depende de si se controla la participación, y eso hay que decirlo al lado
de cualquier versión publicada.

---

## 6. Sumapaz

Quedó fuera del ajuste (§3.3). Con su estrato medio de 1,06, **por fuera** del rango
de las otras 19, M1 le predice 73 % para Petro en 2022; votó 80 %. La diferencia va en
el mismo sentido que el suroriente, pero es una extrapolación sobre 2.700 votantes y
no se interpreta.

---

## 7. Lo que este resultado NO dice

- **Nada sobre personas.** Es ecológico: dice cómo votan las localidades. Que Teusaquillo
  vote más a la izquierda de lo que dice su estrato no quiere decir que un habitante de
  Teusaquillo vote distinto a uno de Suba del mismo estrato. Puede ser eso, o que dentro
  de cada localidad haya composición que el estrato medio no ve (universitarios jóvenes
  en el centro, por ejemplo; M2 no lo captura en forma lineal, pero una variable mejor
  podría).
- **Nada sobre confianza ni gestión.** El voto es otro constructo. Que haya territorio
  estable en el voto hace **más creíble** el territorio que el paso 0b de A08 vio en la
  EPC —ya no parece ruido de muestra—, pero no mide cuánto hay en la opinión que el
  tablero muestra.
- **No distingue causa.** El «territorio» puede ser contexto (barrio, redes, historia
  local) o composición que las tres variables no miden. Para el mapa, el efecto es el
  mismo: un mapa por composición se equivoca siempre en los mismos lugares.
- **19 puntos.** Las cifras son claras (p = 0,0001 en todo lo que decide), pero los
  residuos de cada localidad tienen su propia incertidumbre, que aquí no se estima.

---

## 8. Consecuencias

1. **Un mapa por composición representa bien la mayor parte de la geografía política
   de Bogotá, pero se equivoca de manera sistemática**: le falta izquierda en el centro
   y el suroriente, y le sobra en el noroccidente. Es el primer resultado del proyecto
   sobre territorio que no depende de una muestra pequeña.
2. **El paso 0b se refuerza.** Su territorio no parece ruido: con un conteo completo,
   el territorio aparece, es estable y tiene dirección.
3. **Por la regla (lectura B), hay evidencia para reabrir DI-B10**: un donante que use
   la localidad. Queda como propuesta; es una decisión de proyecto.
4. **Publicable en el tablero**, con sus salvedades (§14.3 del inventario y §5 de este
   documento): el voto por localidad (medición) y el mapa de residuos («lo que el
   estrato no explica»), en sus dos versiones, con y sin participación.
5. **Pendiente del inventario:** Senado y Cámara 2018 (DI-EL1) darían un cuarto y un
   quinto punto en el tiempo para el mismo eje, y permitirían ver si vale también para
   voto de partido y no solo presidencial.
