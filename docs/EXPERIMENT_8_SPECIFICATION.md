# EXPERIMENT 8 — SPECIFICATION

**¿Un LLM le gana al hot-deck como donante de opinión?**

Proyecto: Bogotá Social Simulator
Versión: 0.1 — **pre-registro**
Fecha: 24 de septiembre de 2026
Estado: **baselines medidos; brazo LLM sin correr**
Origen: `claude/EVALUACION_AGENTES_GENERATIVOS.md` §6

---

## 1. La pregunta, acotada

El pipeline le pide al donante exactamente una cosa: dadas cuatro variables
puente —sexo, edad, estrato, educación—, producir un valor de confianza
institucional en 1–5. Hoy lo hace un hot-deck.

> **¿Un LLM hace ese trabajo mejor, sobre las mismas personas retenidas?**

No es «¿sirven los agentes generativos?». Es la versión falsable y barata de esa
pregunta. El LLM entra donde ya hay un método, con la misma entrada y la misma
métrica, y o gana o no gana.

**El LLM recibe exactamente lo que recibe el hot-deck, ni un dato más.** Con
localidad, ocupación o cualquier otra cosa dejaríamos de comparar dos métodos
sobre el mismo problema.

---

## 2. Diseño

| | |
|---|---|
| Datos | ECP (DANE), submuestra de Bogotá. Principal: 2023. Réplicas: 2013, 2017, 2019, 2021 |
| Partición | 70 % entrenamiento / 30 % retenido, semilla 42 |
| Retenido 2023 | 1.269 personas |
| Brazos | `media`, `regresion`, `hotdeck`, `llm` |
| Al LLM se le piden | **los 13 ítems**, no el índice (ver §2.1) |

### 2.1 Por qué se piden los 13 ítems y no el índice

Pedir «el índice de confianza de esta persona» invita al modelo a responder 3
—el centro de la escala— y a que la varianza colapse por construcción. Pidiendo
los ítems, el promedio se arma igual que en el dato real y la dispersión sale de
las respuestas. Es además lo único que hace comparable el resultado con la forma
en que `confianza_institucional` se construye (DI-C6, DI-C11).

### 2.2 Temperatura alta, deliberadamente

A temperatura 0 el modelo da la misma respuesta modal a todas las personas
parecidas y la distribución se aplana. El donante tiene que producir una
**población**, no una predicción puntual, así que se muestrea. Queda registrada
en la salida.

---

## 3. Los dos ejes, y por qué no basta uno

Un método puede ganar en error medio simplemente prediciendo la media a todo el
mundo. Eso no es un modelo mejor: es el defecto que este proyecto ya sufrió
—DI-M1 / POPULATION_SPECIFICATION §8.3, donde el desempate determinista aplanó
la opinión y los modelos de influencia cobraban crédito por repararlo— y es
también la falla número uno documentada de los LLM en simulación de encuestas
(Bisbee et al.: varianza *"far too low"*).

| eje | métrica | qué detecta |
|---|---|---|
| **Acierto** | MAE, RMSE, correlación | qué tan cerca cae de cada persona |
| **Forma** | sd predicha / sd real, W1 | si conserva la dispersión o la aplana |
| **Equidad** | MAE por subgrupo, DPD | si el aplanamiento golpea a unos más que a otros |

---

## 4. Los baselines, ya medidos

**Medidos antes de tocar el LLM**, sobre el retenido de 2023 (n = 1.269):

| brazo | MAE | RMSE | corr | sd pred | sd ratio | W1 | sesgo |
|---|---|---|---|---|---|---|---|
| media | 0,6215 | 0,7755 | — | 0,000 | 0,000 | 0,6233 | +0,028 |
| regresión | 0,6148 | 0,7657 | 0,161 | 0,096 | 0,124 | 0,5490 | +0,026 |
| **hot-deck** | **0,8344** | 1,0719 | 0,003 | 0,743 | **0,958** | **0,0574** | +0,043 |

*(sd real del retenido: 0,7753)*

Estable en 15 combinaciones (5 años × 3 semillas). Medianas: MAE media 0,734,
regresión 0,723, hot-deck 0,988; sd ratio del hot-deck 0,995; W1 regresión
0,637, hot-deck 0,034.

### 4.1 Dos hallazgos que reencuadran el experimento

**El hot-deck no predice individuos, y no pretende hacerlo.** Su correlación con
la verdad es **0,003** — cero. Es peor que adivinar la media en error por
persona (0,83 contra 0,62) y a la vez reproduce la distribución casi
perfectamente (W1 = 0,057, sd ratio 0,96). Es un dispositivo de emparejamiento
de distribuciones, no un predictor. Cualquier comparación que solo mire MAE
está evaluando algo que el hot-deck nunca intentó hacer.

**En acierto por persona ya no queda nada que ganar.** Con R² = 0,02 sobre las
cuatro variables puente, el mejor predictor posible deja un residuo de
sd·√(1−R²); si fuera normal, el piso del MAE es sd·√(1−R²)·√(2/π):

| año | sd | R² | piso MAE | MAE regresión | margen |
|---|---|---|---|---|---|
| 2013 | 0,754 | 0,001 | 0,602 | 0,575 | −0,027 |
| 2017 | 0,927 | 0,027 | 0,730 | 0,752 | +0,022 |
| 2019 | 0,890 | 0,018 | 0,704 | 0,723 | +0,019 |
| 2021 | 0,900 | 0,003 | 0,717 | 0,757 | +0,040 |
| 2023 | 0,775 | 0,024 | 0,611 | 0,615 | +0,004 |

**Una regresión lineal de cuatro variables ya está en el piso.** El margen
máximo que un LLM podría ganar en MAE es de 0,02–0,04 puntos sobre una escala
de 4 — y eso suponiendo que alcance un piso derivado de una aproximación
normal. La información no está en las variables; ningún motor la crea.

---

## 5. Predicciones pre-registradas

Se registran **antes** de correr el brazo LLM. Cada una con su umbral numérico.

| # | Predicción | Umbral | Espero |
|---|---|---|---|
| **P1** | El LLM **gana** al hot-deck en MAE | MAE_llm < 0,83 | **Sí** |
| **P2** | El LLM **no** iguala la forma del hot-deck | W1_llm > 0,10 (3× el del hot-deck) | **Sí** |
| **P3** | El LLM aplana la distribución | sd ratio < 0,80 | **Sí** |
| **P4** | El LLM **no** mejora el MAE de la regresión de forma material | MAE_llm > 0,595 (piso − 0,02) | **Sí** |
| **P5** | El LLM reparte peor el error entre subgrupos | DPD_llm > DPD_hotdeck en ≥ 2 de 4 agrupaciones | **Sí** |

**Estoy prediciendo que el LLM gana en el eje que no importa y pierde en el que
sí.** Si P1 se cumple y P2 no, el resultado es interesante de verdad y el
experimento habría encontrado algo. Si se cumplen las cinco, el resultado es el
esperado y la utilidad está en tenerlo medido en vez de argumentado.

**Lo que falsaría mi expectativa:** W1_llm ≤ 0,10 **y** sd ratio ≥ 0,80. Eso
significaría que el LLM muestrea de la distribución condicional correcta, que es
justamente lo que la literatura dice que no hace.

---

## 6. Regla de decisión

El LLM reemplaza al hot-deck **solo si gana en los dos ejes**:

```
    MAE_llm  ≤  MAE_regresion          (acierto: al menos el piso)
        Y
    W1_llm   ≤  1,5 × W1_hotdeck       (forma: no aplana)
```

Ganar solo en MAE **no cuenta**, y esta regla existe para que ese resultado no
se pueda vender como un éxito. Es exactamente lo que pasó en el Experimento 4
antes de DI-M1.

Un resultado intermedio —gana en forma, pierde en acierto— tampoco reemplaza al
hot-deck, pero sí abriría una pregunta nueva que hoy no tenemos: un donante
híbrido.

---

## 7. Costo y límites

- **400 llamadas** al modelo para el brazo principal (submuestra estable del
  retenido de 2023). Se puede correr con `--n 100` primero: la submuestra es un
  prefijo, así que la corrida chica sigue valiendo al ampliarla.
- **No sale ningún dato del CNC.** La ECP es microdato público del DANE y lo
  único que viaja son cuatro variables demográficas por persona, sin
  identificador. Este arnés **no se debe usar** con los estudios del CNC:
  violaría R10 / DATA_INVENTORY §12.4.
- **Contaminación posible.** Los microdatos de la ECP son públicos y pueden
  estar en el entrenamiento del modelo. Si el LLM acertara mucho, hay que
  descartar memorización antes de celebrarlo — por ejemplo comparando su
  desempeño en 2023 contra un año cuyo patrón difiera.
- **Un solo modelo no decide.** Un resultado negativo con un modelo no cierra la
  pregunta para todos.

---

## 8. Cómo se corre

```
python src/experiments/experimento8.py --anio 2023                    # baselines
set ANTHROPIC_API_KEY=...
python src/experiments/donante_llm.py --anio 2023 --n 400
python src/experiments/experimento8.py --anio 2023 \
       --llm data/processed/exp8/llm_respuestas_2023.json             # los cuatro brazos
```

`donante_llm.py` cachea: reanudar una corrida interrumpida no repite llamadas.

---

*Los resultados van a `claude/EXPERIMENT_8_RESULTS.md`, reportados contra este
pre-registro y no contra lo que haya salido.*
