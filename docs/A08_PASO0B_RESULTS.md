# A08 — PASO 0b: RESULTADOS

**La composición no exagera el territorio: no lo reproduce. En la EPC hay diferencias reales entre localidades, pero no son las que predicen el estrato, la edad y el sexo.**

Proyecto: Bogotá Social Simulator
Versión: 0.1
Fecha: 25 de septiembre de 2026
Pre-registro: `A08_PASO0B_SPECIFICATION.md` (en el repo antes de correr sobre la EPC)
Corrida: PC del CNC, EPC de Bogotá Cómo Vamos. 200 bootstrap, 500 permutaciones.

---

## 1. Las tablas

### Gestión del alcalde (el ítem principal)

| año | n | sd medida | sd por composición | **R** | **r** | p territorio | R con DEFF* |
|---|---|---|---|---|---|---|---|
| 2014 | 1.397 | 0,265 | 0,121 | 2,20 | −0,04 | 0,004 | 1,60 |
| 2015 | 1.634 | 0,274 | 0,102 | 2,70 | 0,08 | 0,002 | 2,34 |
| 2017 | 1.450 | 0,204 | 0,074 | 2,77 | 0,55 | 0,008 | 1,70 |
| 2018 | 1.446 | 0,177 | 0,135 | 1,32 | 0,60 | 0,030 | 0,70 |
| 2019 | 1.427 | 0,176 | 0,088 | 2,01 | 0,48 | 0,024 | 1,14 |
| 2022 | 1.275 | 0,161 | 0,000 | — | 0,46 | 0,008 | — |
| 2023 | 1.264 | 0,100 | 0,000 | — | 0,12 | 0,357 | — |
| 2024 | 1.259 | 0,039 | 0,000 | — | −0,14 | 0,709 | — |
| 2025 | 1.244 | 0,203 | 0,162 | 1,25 | 0,33 | 0,008 | 0,75 |
| **mediana** | | | | **2,10** | **0,33** | **7 de 9 < 0,05** | *1,37* |

2016 se omite: esa ola no trae el ítem ni la edad. Desde 2018 la edad viene en
años y se bandea con los cortes de DI-B9. Las dispersiones están corregidas por
ruido de muestreo; «—» es composición sin dispersión detectable.

\* **Sensibilidad no pre-registrada**, añadida después de ver 2014, 2015 y 2017:
la varianza de muestreo se infla por el DEFF medido en la EPC para esta variable
(1,95). La decisión usa R.

### Gestión del Concejo (réplica)

| año | sd medida | sd por composición | R | r | p territorio |
|---|---|---|---|---|---|
| 2014 | 0,177 | 0,000 | — | −0,37 | 0,088 |
| 2015 | 0,044 | 0,000 | — | −0,41 | 0,647 |
| 2017 | 0,203 | 0,000 | — | −0,07 | 0,022 |
| 2019 | 0,147 | 0,067 | 2,21 | 0,03 | 0,052 |
| 2022 | 0,061 | 0,009 | 6,87 | 0,04 | 0,315 |
| 2023 | 0,079 | 0,000 | — | 0,13 | 0,545 |
| 2024 | 0,113 | 0,000 | — | −0,34 | 0,254 |
| 2025 | 0,000 | 0,000 | — | 0,11 | 0,822 |

2016 y 2018 se omiten: no traen la edad o el ítem. **Con el Concejo no hay casi
nada que medir**: territorio en 1 de 8 olas, composición sin dispersión en 6. No
confirma ni contradice lo del alcalde; es un ítem sin estructura por localidad.

---

## 2. Contra el pre-registro

| # | Predicción | Umbral | Resultado | |
|---|---|---|---|---|
| P1 | La composición apunta a las mismas localidades | r mediana > 0,5 | **0,33** | ❌ falla |
| P2 | La composición predice la escala correcta | R mediana en [0,67 ; 1,5] | **2,10** | ❌ falla, por encima |
| P3 | La EPC mide territorio real | p < 0,05 en ≥ 5 de 9 olas | **7 de 9** | ✅ se cumple |

**Con la sensibilidad al DEFF** (no pre-registrada), R baja a 1,37 y quedaría
dentro del rango. Pero **P1 no depende del DEFF**: la correlación es la misma, y
en tres olas (2014, 2015, 2024) es nula o negativa.

### 2.1 Lo que falló de mi expectativa

El paso 0b existía porque yo temía que la composición **exagerara** el
territorio. Pasó lo contrario, en las dos dimensiones:

- **Escala:** lo medido es mayor que lo predicho (R = 2,1), o parecido si se
  descuenta el diseño (1,37). En ningún caso menor.
- **Dirección:** la composición apunta a las localidades correctas solo en
  algunas olas (2017, 2018, 2019, con r cercano a 0,5–0,6). En otras no apunta a
  nada. Y en 2022–2024 la composición no predice ninguna diferencia, mientras la
  EPC sí mide territorio en 2022.

---

## 3. Decisión, por la regla pre-registrada

La regla dice: *R mediana > 1,5 o r mediana ≤ 0,5 → hay territorio que la
composición no captura, o no apunta a las mismas localidades. La capa por
composición no representa bien la ciudad.* **Se cumplen las dos condiciones**, y
la segunda aunque se descuente el diseño.

**Para A08:**

- **Se cae el argumento visual de escalar.** El paso 0 mostró que con 100.000
  agentes el mapa dibujaría con nitidez las diferencias por composición. El paso
  0b muestra que, al menos en la EPC, **esas no son las diferencias que existen**.
  Un mapa nítido de la composición sería un mapa preciso de otra cosa.
- **El tablero ya dice lo correcto.** «El tiempo se puede leer, la geografía no»
  (DI-V47) sigue en pie, ahora con una razón más: la geografía que puede
  producir la población sintética es la de la composición, y la composición no
  reproduce la geografía medida.
- **El camino, si alguna vez se quiere geografía de opinión**, es un donante que
  **sí** use la localidad. Eso significa reabrir DI-B10 para la EPC, con el
  cuidado de sus pesos de 2014 y 2019, o conseguir una fuente de confianza
  institucional con localidad. No es escalar.

---

## 4. Lo que este resultado NO dice

- **No dice nada directo sobre la confianza institucional de la ECP.** Es otro
  constructo (A20). La evaluación de un alcalde puede tener una geografía
  política propia —el voto, el origen del gobernante, las obras en cada zona—
  que la confianza en las instituciones no tenga. Lo que sí dice es que, en la
  única encuesta de Bogotá donde se puede comprobar, **la composición demográfica
  no basta para reconstruir el territorio**.
- **El territorio está sobre-detectado.** La permutación ignora el diseño
  muestral: con conglomerados por manzana dentro de cada localidad, los p son
  optimistas. Aun así, las diferencias medidas sobreviven a la corrección por
  DEFF en 5 de las 6 olas con composición no nula.
- **La composición de la EPC es más pobre que la del pipeline.** No trae
  educación (DI-B8): las celdas son sexo × edad × estrato. Con educación, la
  composición podría predecir algo más. Es poco probable que eso cambie el signo
  de r en 2014 y 2015.
- **Es poco territorio.** Una dispersión real de 0,15–0,27 sobre una escala de 1
  a 5, con una desviación individual cercana a 1,2, es del orden del 2–5 % de la
  varianza. Es consistente con D15: la localidad explica poco, y lo poco que
  explica no es composición.

---

## 5. Qué sigue

1. **A08 queda sin argumento visual.** Su otra mitad —rendimiento de la red y
   los modelos a 100.000 agentes— solo vuelve si una simulación lo pide.
2. **El tablero no cambia**: ya no afirma geografía de opinión (DI-V52), y esto
   lo refuerza.
3. Si se quiere geografía de opinión, la pregunta es de **datos**, no de
   escala: un donante con localidad.

---

*Reportado contra el pre-registro. P1 y P2 fallaron —y fallaron en la dirección
contraria a la que motivó el paso— y quedan como estaban escritas.*
