# EXPERIMENT 8 — RESULTS

**¿Un LLM le gana al hot-deck como donante de opinión? No. Y lo que hace en su lugar es lo interesante.**

Proyecto: Bogotá Social Simulator
Versión: 0.1
Fecha: 24 de septiembre de 2026
Pre-registro: `claude/EXPERIMENT_8_SPECIFICATION.md` (escrito antes de correr el brazo LLM)
Modelo: `xiaomi/mimo-v2.6-pro` vía OpenRouter, temperatura 1.0
Cobertura: **1.266 de 1.269** personas del retenido (99,8 %); 3 fallos de proveedor
Costo: ~USD 0,48

---

## 1. Resultado, en una línea

El LLM **pierde en los dos ejes**: es peor que predecir una constante en acierto
por persona (MAE 0,720 contra 0,622) y peor que el hot-deck en forma de la
distribución por un factor de diez (W1 0,570 contra 0,057). La regla de decisión
pre-registrada falla por ambos lados. **El hot-deck se queda.**

---

## 2. La tabla, sobre las mismas 1.266 personas

| brazo | MAE | RMSE | corr | sd pred | sd ratio | W1 | sesgo |
|---|---|---|---|---|---|---|---|
| media | 0,6221 | 0,7761 | — | 0,000 | 0,000 | 0,6238 | +0,029 |
| regresión | **0,6152** | 0,7663 | 0,162 | 0,096 | 0,124 | 0,5493 | +0,026 |
| hot-deck | 0,8357 | 1,0730 | 0,003 | 0,743 | **0,958** | **0,0566** | +0,043 |
| **llm** | 0,7201 | 0,8704 | 0,118 | 0,231 | 0,297 | 0,5700 | **−0,375** |

*(sd real 0,776; media real 2,410)*

---

## 3. Contra el pre-registro

| # | Predicción | Umbral | Resultado | |
|---|---|---|---|---|
| P1 | El LLM gana al hot-deck en MAE | < 0,83 | 0,7201 | ✅ se cumple |
| P2 | No iguala la forma del hot-deck | W1 > 0,10 | 0,5700 | ✅ se cumple, por 10× |
| P3 | Aplana la distribución | sd ratio < 0,80 | 0,297 | ✅ se cumple |
| P4 | No mejora el MAE de la regresión | > 0,595 | 0,7201 | ✅ se cumple |
| P5 | Reparte peor el error entre subgrupos | peor en ≥2 de 4 | 2 de 4 | ⚠️ empate |

**Regla de decisión:**

```
    MAE_llm ≤ MAE_regresión   →   0,7201 ≤ 0,6152   NO
    W1_llm  ≤ 1,5 × W1_hotdeck →   0,5700 ≤ 0,0849   NO
```

Falla las dos. El LLM no reemplaza al hot-deck.

### 3.1 Dos correcciones a mi propia expectativa

**Subestimé cuánto pierde.** El pre-registro decía «el LLM va a ganar en el eje
que no importa y perder en el que sí». Ganó contra el hot-deck en MAE, sí — pero
**perdió también contra predecir una constante** (0,720 contra 0,622). El sesgo
de −0,375 arrastra el acierto por persona hasta por debajo del predictor más
tonto posible. Eso es peor de lo que anticipé.

**P5 estaba mal formulada.** «Peor en ≥2 de 4» con cuatro agrupaciones se cumple
con un empate 2–2, que es lo que pasó: el LLM reparte peor por sexo (0,019 vs
0,009) y por estrato (0,256 vs 0,197), y **mejor** por educación (0,085 vs 0,162)
y por edad (0,050 vs 0,146). Un umbral que se satisface con un empate no
discrimina nada. Queda anotado como defecto del pre-registro, no como hallazgo.

---

## 4. El hallazgo: aplana personas y exagera instituciones

Lo que importa no es que el LLM falle, sino **qué pone en lugar de la gente**.

| dispersión | real | LLM | ratio |
|---|---|---|---|
| entre **personas** | 0,776 | 0,231 | **0,30 ×** — aplana |
| entre **instituciones** | 0,221 | 0,737 | **3,33 ×** — exagera |

Las dos al mismo tiempo, y en direcciones opuestas.

### 4.1 Por institución

| real | LLM | dif | institución |
|---|---|---|---|
| 2,03 | **1,00** | −1,03 | Partidos o movimientos políticos |
| 2,02 | **1,01** | −1,01 | Congreso de la República |
| 2,31 | 1,52 | −0,80 | Concejos municipales/distritales |
| 2,46 | 1,70 | −0,76 | Fiscalía General de la Nación |
| 2,44 | 1,75 | −0,69 | Contraloría |
| 2,46 | 1,89 | −0,57 | Procuraduría General de la Nación |
| 2,29 | 1,77 | −0,52 | Jueces y magistrados |
| 2,55 | 2,07 | −0,47 | Alcaldía Municipal/Distrital |
| 2,67 | 2,22 | −0,45 | Defensoría del Pueblo |
| 2,32 | 2,07 | −0,24 | Presidencia de la República |
| 2,42 | **2,80** | +0,38 | Policía |
| 2,65 | **3,15** | +0,50 | Registraduría Nacional del Estado Civil |
| 2,74 | **3,44** | +0,70 | Fuerzas Militares |

**El orden lo acierta: Spearman 0,771 (p = 0,002), Pearson 0,834.** El modelo
sabe quién genera más desconfianza que quién en Colombia, y coincide con la
jerarquía que el proyecto verificó por su cuenta en DI-C10 —partidos y Congreso
abajo, Fuerzas Militares y Registraduría arriba—.

**Las magnitudes las inventa.** La amplitud real entre la institución más y la
menos confiada es de **0,72 puntos**; la del modelo, **2,44**. Y `Partidos
políticos` sale con media **1,00**: es el piso exacto de la escala, o sea que
prácticamente *todas* las personas sintéticas respondieron 1. Eso no es una
distribución, es una constante, y explica buena parte del colapso de varianza.

### 4.2 Qué significa

El modelo no está simulando personas: está aplicando **un relato nacional sobre
instituciones** a las 1.266 por igual. Por eso las dos dispersiones se mueven al
revés — toda la variación que debería estar entre individuos se traslada a las
diferencias entre instituciones, amplificada hasta la caricatura.

Para este proyecto eso es lo contrario de lo que se necesita. El donante existe
para producir **heterogeneidad plausible** en una población; el hot-deck la
produce casi perfecta (sd ratio 0,958, W1 0,057) precisamente porque no opina:
copia a una persona real parecida. El LLM opina, y opina lo mismo para todos.

---

## 5. Lo que este resultado NO dice

- **No dice que los LLM no sirvan para simulación social.** Dice que *este* LLM,
  con *estas* cuatro variables y *este* prompt, no reemplaza al hot-deck en el
  trabajo concreto de donar opinión.
- **Es una prueba con un solo modelo, y así queda.** Hay una corrida previa con
  `anthropic/claude-opus-5.5` sobre 10 personas que apunta en la misma dirección
  (sesgo −0,64/−0,69, sd ratio 0,22/0,31), pero n = 10 no concluye. Repetirla
  sobre las 1.269 costaría ~USD 4,80 y cerraría el punto.

  **Decidido el 25/09/2026: no se corre.** No es un olvido ni falta de
  presupuesto — es que la conclusión operativa no cambia. Si Opus se comportara
  igual, el hot-deck se queda; si se comportara mejor, seguiría sin pasar la
  regla de decisión por un margen enorme (el LLM barato falla W1 por 10×, no por
  poco). El experimento se reabre si alguien propone usar un LLM como donante,
  y entonces el segundo modelo es el primer paso, no una confirmación.
- **No descarta memorización en la otra dirección.** El acierto de orden
  (Spearman 0,771) puede venir de que los microdatos y los informes de la ECP son
  públicos. No afecta la conclusión —el modelo pierde igual— pero sí impide leer
  ese 0,771 como «el modelo entiende a Colombia».

---

## 6. Consecuencias

1. **D28 se mantiene y ahora tiene medición detrás**, no solo argumento. El LLM
   no entra al pipeline como donante.
2. **El hot-deck queda confirmado en lo que hace**, que no es predecir: su
   correlación con la verdad es 0,003 y su W1 es 0,057. Es un emparejador de
   distribuciones y es muy bueno en eso.
3. **La falla documentada se reprodujo.** Bisbee et al. reportan varianza *"far
   too low"* en LLM simulando encuestas; acá salió 0,30× la real. Y es la misma
   familia de defecto que DI-M1, donde el desempate determinista aplanaba la
   opinión y los modelos cobraban crédito por repararlo.
4. **Queda una pregunta nueva, y es barata:** el modelo acierta el *orden* de las
   instituciones. Si esa señal sobrevive a un control de memorización, podría
   servir para algo distinto del donante — por ejemplo como prior sobre qué
   instituciones se mueven juntas. No es el experimento de hoy.

---

*Reportado contra el pre-registro. Las predicciones que fallaron —P5, y mi
subestimación de cuánto pierde el LLM en MAE— quedan como estaban escritas.*
