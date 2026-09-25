# A08 — PASO 0: ¿qué mostraría el mapa con más agentes?

Proyecto: Bogotá Social Simulator
Versión: 0.1 — **pre-registro**
Fecha: 25 de septiembre de 2026
Estado: **código escrito y probado con datos simulados; sin correr sobre datos reales**
Código: `src/experiments/a08_paso0.py` · Pruebas: `tests/test_a08_paso0.py`
Origen: DI-V52 (VISUALIZATION_SPECIFICATION.md) y el reencuadre de A08 en ESTADO_DEL_PROYECTO §6

---

## 1. La pregunta

A08 se justificaba así: *con 1.000 agentes ninguna diferencia entre localidades
sobrevive al ruido; con 100.000 el error cae por √100 y el mapa deja de estar
dominado por ruido.* Dos cosas cambian esa cuenta:

- **El donante (ECP) no registra la localidad.** En la población sintética, la
  opinión solo difiere entre localidades por su composición demográfica. Al
  escalar, cada localidad converge a un valor fijo, y el mapa se vería preciso
  sobre algo que es construcción del método.
- **La incertidumbre de ese valor fijo viene del donante**, unos pocos miles de
  encuestados por año, y **no baja al escalar**.

> **¿Las diferencias entre localidades que produce la composición demográfica
> son mayores que las que produciría el ruido del donante solo? Y si lo son,
> ¿cuántos agentes hacen falta para verlas?**

Se responde **sin construir ninguna población grande**.

---

## 2. Método

| Pieza | Qué es | Por qué |
|---|---|---|
| **Límite con N infinito** (`S_lim`) | Dispersión entre localidades de la media a la que converge cada una. Exacta: el hot-deck sortea entre los empatados a la menor distancia con peso ∝ FEX del donante, así que su esperanza por celda es una media ponderada; se promedia con los FEX_C del receptor por localidad | Es lo que mostraría el mapa con infinitos agentes |
| **Nulo de permutación en el donante** | Se baraja la opinión entre donantes y se recalcula `S_lim`. Conserva composición del receptor, celdas, empates y pesos; rompe solo opinión↔demografía | Responde si la composición produce algo más que el ruido del donante. **Puede fallar**, a diferencia del piso por semillas (DI-V52) |
| **Bootstrap del donante** | Intervalo de `S_lim` y de cada localidad, remuestreando encuestados | La incertidumbre que no baja al escalar. **Optimista**: la ECP no publica diseño (A19), falta un factor del orden de √DEFF |
| **N finito** | `sd_entre` simulado con 1.000, 10.000 y 100.000 agentes | Cuánto del mapa es ruido de una corrida y cuánto es el límite |

Estadística: `sd_entre` = desviación estándar, sin ponderar, de las medias por
localidad, la misma que usan `piso_territorial.py` y el tablero.

### 2.1 Verificado antes de tocar datos reales (`tests/test_a08_paso0.py`)

| Prueba | Resultado |
|---|---|
| El límite coincide con el promedio de 30 corridas del `hot_deck_match` real | diferencia máxima **0,007** en escala 1–5; máx z = 2,29 |
| Nulo sin efecto opinión–demografía (40 donantes simulados) | rechaza **2 %** (esperado ~5 %) |
| Nulo con efecto | rechaza **100 %** |
| `sd_entre` con N finito converge al límite | 0,191 → 0,143 → 0,138 con límite 0,137 |

Costo: unos 3 segundos por año a tamaño real, más la carga de los datos.

---

## 3. Predicciones pre-registradas

Se registran **antes** de correr sobre datos reales. Los R² son los de las
cuatro variables puente medidos en el Experimento 8 (§4.1 de su especificación).

| # | Predicción | Umbral | Por qué lo espero |
|---|---|---|---|
| **P1** | La composición produce diferencias chicas | `S_lim` entre 0,03 y 0,12 en los cinco años | las variables puente explican R² ≈ 0,02 y solo una parte de su varianza está entre localidades |
| **P2** | La señal por composición supera al ruido del donante **solo donde las variables puente explican algo** | supera el p95 del nulo en 2017, 2019 y 2023 (R² 0,018–0,027) y **no** en 2013 ni 2021 (R² 0,001 y 0,003) | si la demografía no predice opinión, la composición no puede separar localidades |
| **P3** | Con 1.000 agentes el mapa es sobre todo ruido | mediana de `sd_entre` a N = 1.000 ≥ 2 × `S_lim` en todos los años | los `sd_entre` publicados van de 0,15 a 0,34 |
| **P4** | Con 100.000 el mapa ya está en el límite | mediana a N = 100.000 dentro de ±10 % de `S_lim` | el ruido de una corrida cae como 1/√N |
| **P5** | La incertidumbre del donante no es despreciable | ancho del IC bootstrap de `S_lim` ≥ 0,5 × `S_lim`, aun siendo optimista | unos 3.000 encuestados repartidos en miles de celdas |

**P2 es la que más arriesga**, y la que más informa si falla. Si 2021 superara
el nulo, habría estructura por composición donde la demografía casi no predice
opinión, y habría que entender de dónde sale antes de dibujarla.

---

## 4. Regla de decisión

Por año, y después para el proyecto:

```
    si  S_lim ≤ p95 del nulo:
        la composición no produce nada distinguible del ruido del donante.
        Escalar solo convertiría ese ruido en precisión aparente.
        → ese año NO justifica A08 para el mapa.

    si  S_lim > p95 del nulo:
        hay diferencias por composición, y se pueden mostrar SOLO como
        «diferencia esperada por composición demográfica», con la banda del
        bootstrap del donante —no la del ruido de la corrida—.
        N necesario = el menor de {1.000, 10.000, 100.000} cuya mediana de
        sd_entre queda dentro de 1,1 × S_lim.
```

**Para el proyecto:**

- **Ningún año supera el nulo:** A08 deja de tener argumento visual. Queda solo
  como tema de rendimiento, si alguna simulación lo pide.
- **Al menos un año lo supera:** A08 se hace al N necesario, y la capa de
  opinión cambia de lectura. Deja de decir «no leer geografía» y pasa a decir
  «esto es lo que la composición demográfica predice, con esta incertidumbre;
  no es una medición por localidad». Esa capa necesita su propio aviso, como
  la de Crecimiento (DI-V51).

En ningún caso el resultado autoriza a decir que una localidad **confía** más
que otra: el donante no la midió ahí.

---

## 5. Cómo se corre

En la máquina con `data/raw/`: el receptor de Multipropósito con FEX_C y la ECP.

```powershell
.\venv\Scripts\Activate.ps1
python tests/test_a08_paso0.py            # ~1 min, no necesita datos
python src/experiments/a08_paso0.py       # los cinco años
```

Salida: una tabla en pantalla y `data/processed/a08/paso0.json`. Los resultados
van a `A08_PASO0_RESULTS.md`, reportados **contra este pre-registro**.

---

## 6. Lo que este paso no responde

- **Si Bogotá tiene diferencias de confianza entre localidades.** La ECP no
  llega a localidad. Para eso haría falta un donante que sí llegue —la EPC de
  Bogotá Cómo Vamos trae localidad, pero sus factores de expansión no
  reproducen el marginal en 2014 y 2019 (DI-B10)—, y es otra pregunta.
- **El rendimiento de la red o de los modelos a 100.000 agentes.** Es la otra
  mitad de A08 (matriz W densa → sparse, k-d tree en el generador homofílico) y
  solo importa si la simulación sobre la serie lo pide.
