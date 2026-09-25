# A08 — PASO 0: RESULTADOS

**La composición demográfica sí separa las localidades en cuatro de cinco años. Verlo en el mapa exige 100.000 agentes, y solo puede mostrarse como lo que es: composición, no medición.**

Proyecto: Bogotá Social Simulator
Versión: 0.1
Fecha: 25 de septiembre de 2026
Pre-registro: `A08_PASO0_SPECIFICATION.md` (en el repo antes de que existieran los datos en disco)
Corrida: PC del CNC, datos públicos del DANE (Multipropósito 2021, catálogo 743; ECP 2013–2023) descargados el mismo día. 200 bootstrap, 200 permutaciones, 50 corridas por tamaño.
Datos: `data/processed/a08/paso0.json`

---

## 1. La tabla

| año | `S_lim` | IC bootstrap | nulo p95 | p | ¿supera? | N = 1.000 | N = 10.000 | N = 100.000 |
|---|---|---|---|---|---|---|---|---|
| 2013 | 0,026 | 0,018–0,047 | 0,033 | 0,164 | **no** | 0,182 | 0,088 | 0,039 |
| 2017 | 0,117 | 0,094–0,148 | 0,042 | 0,005 | **sí** | 0,257 | 0,157 | 0,120 |
| 2019 | 0,104 | 0,078–0,129 | 0,037 | 0,005 | **sí** | 0,227 | 0,152 | 0,107 |
| 2021 | 0,068 | 0,048–0,087 | 0,037 | 0,005 | **sí** | 0,230 | 0,140 | 0,074 |
| 2023 | 0,105 | 0,082–0,125 | 0,037 | 0,005 | **sí** | 0,195 | 0,135 | 0,106 |

*`S_lim`: dispersión entre localidades con N infinito. Nulo: la que produce el ruido del donante sin relación opinión–demografía. p = 0,005 es el mínimo posible con 200 permutaciones.*

---

## 2. Contra el pre-registro

| # | Predicción | Resultado | |
|---|---|---|---|
| P1 | `S_lim` entre 0,03 y 0,12 en los cinco años | 2013 = 0,026 | ❌ falla por 2013 |
| P2 | Supera en 2017, 2019, 2023; **no** en 2013 ni 2021 | 2021 **sí** supera | ❌ falla en la más arriesgada |
| P3 | N = 1.000: mediana ≥ 2 × `S_lim` | 2023: 0,195 contra 0,210 | ❌ falla por 2023 |
| P4 | N = 100.000: dentro de ±10 % de `S_lim` | 2013: +50 % | ❌ falla por 2013 |
| P5 | Ancho del IC ≥ 0,5 × `S_lim` | 2017, 2019, 2023 por debajo | ❌ falla en 3 de 5 |

**Fallan las cinco.** Cuatro por un año o por poco margen (P3 por 0,015; P5 en 2019 por 0,001). Se reportan como estaban escritas.

### 2.1 Lo que las fallas enseñan

**P2 descansaba en un supuesto equivocado.** Tomé el R² de una regresión *lineal* como medida de cuánto predice la demografía. El hot-deck no es lineal: empareja por celda, y la esperanza por celda capta interacciones que una regresión de cuatro variables no ve. En 2021 el R² lineal es 0,003, pero la estructura por celda alcanza para separar localidades más allá del ruido del donante (p = 0,005). La predicción falló por el instrumento con el que la construí, no por azar.

**P1 y P4 fallan por el mismo año y por la misma razón.** En 2013 la señal es tan chica (0,026) que ni con 100.000 agentes el ruido de la corrida deja de pesar. Es consistente con que 2013 no supere el nulo.

**P5 subestimó cuánto informan unos 5.000 encuestados.** El intervalo del donante quedó más angosto de lo esperado. Hay que recordar que es optimista: la ECP no publica su diseño muestral (A19). Con el DEFF prestado de 1,86 los anchos crecen ~1,36× y P5 se cumpliría en los cinco años. Pero ese no era el criterio registrado.

---

## 3. Las dos dudas que había que resolver

### 3.1 ¿2021 es Sumapaz? No.

La sospecha era que una localidad rural y atípica inflaba sola la dispersión. Quitando localidades:

| año | `S_lim` | sin Sumapaz | sin Chapinero | sin las dos | nulo p95 |
|---|---|---|---|---|---|
| 2013 | 0,026 | 0,025 | 0,020 | 0,019 | 0,033 |
| 2017 | 0,117 | 0,116 | 0,102 | 0,101 | 0,042 |
| 2019 | 0,104 | 0,097 | 0,093 | 0,085 | 0,037 |
| 2021 | 0,068 | 0,060 | 0,057 | **0,047** | 0,037 |
| 2023 | 0,105 | 0,106 | 0,083 | 0,084 | 0,037 |

Sin las dos localidades extremas, 2021 sigue por encima del nulo. Queda más débil que los otros años, pero repartido en la ciudad. *(Comparación aproximada: el nulo se calculó con las 20 localidades.)*

### 3.2 Es un solo patrón, y es el del estrato

| año | Chapinero / Teusaquillo / Usaquén | Usme / Ciudad Bolívar / Bosa |
|---|---|---|
| 2013 | +0,07 / +0,04 / +0,03 | −0,02 / −0,02 / +0,01 |
| 2017 | +0,26 / +0,26 / +0,20 | −0,11 / −0,10 / −0,08 |
| 2019 | +0,22 / +0,12 / +0,13 | −0,16 / −0,17 / −0,09 |
| 2021 | +0,16 / +0,02 / +0,07 | −0,05 / −0,08 / +0,04 |
| 2023 | +0,28 / +0,20 / +0,19 | −0,08 / −0,08 / −0,07 |

El norte de estrato alto queda arriba y el sur abajo, todos los años. Las diferencias por localidad correlacionan entre años de 0,56 a 0,98. Es lo que la composición tiene que producir si la confianza sube con estrato y educación: **la geografía que aparece es la geografía del estrato**.

---

## 4. Decisión, por la regla pre-registrada

- **2013:** no supera el nulo → no justifica A08.
- **2017, 2019, 2021, 2023:** superan → A08 se justifica para el mapa **solo** como «diferencia esperada por composición demográfica», con la banda del donante.
- **N necesario: 100.000 en los cuatro.** Con 10.000 la mediana de `sd_entre` sigue entre 29 % y 106 % por encima del límite.

**Lo que esto NO autoriza, y hay que decirlo en la página:** que Chapinero *confía* más que Usme. Dice que la gente con el perfil demográfico de Chapinero confía más, en promedio, en toda la ciudad, y que Chapinero tiene más gente con ese perfil. Si en Usme las personas de estrato alto confiaran distinto que en Chapinero, este método no lo vería: el donante no trae localidad.

---

## 5. Lo que queda abierto

1. **La simulación con N = 1.000 da `sd_entre` 10–20 % más bajo que el piso por semillas** medido con el pipeline completo (0,18 contra 0,23 en 2013; 0,26 contra 0,29 en 2017; 0,23 contra 0,28 en 2019; 0,23 contra 0,27 en 2021; 0,20 contra 0,22 en 2023). La dirección y la magnitud coinciden y el límite está validado contra el `hot_deck_match` real (dif. máx. 0,007), así que **no afecta a `S_lim` ni a la decisión**. Sí afecta a los números con N finito. Candidato principal: la simulación muestrea el receptor con reemplazo ∝ FEX_C y el pipeline usa PPS sistemático con unidades de certeza (D14). No está verificado.
2. **La magnitud de `S_lim` (0,07–0,12) es comparable o mayor que la dispersión real entre localidades** que midieron los estudios del CNC para otras variables (sd real 0,046–0,073, D15). Son variables distintas y no se pueden comparar directamente. Pero si la composición predijera más diferencia territorial de la que las encuestas observan, el mapa por composición exageraría. Es la pregunta a resolver antes de publicar la capa.
3. **La otra mitad de A08** —rendimiento de la red y de los modelos a 100.000 agentes— sigue sin tocarse.

---

*Reportado contra el pre-registro. Las cinco predicciones fallaron y quedan como estaban escritas.*
