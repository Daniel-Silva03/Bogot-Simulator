# ESTADO DEL PROYECTO — punto de partida para una conversación nueva

Proyecto: Bogotá Social Simulator
Fecha de corte: **25 de septiembre de 2026**
Para qué sirve: leer **este documento solo** basta para retomar. Los demás se
leen cuando el trabajo los toque, no antes.

---

## 1. Dónde está el proyecto, en cinco líneas

- El **pipeline de población** funciona, es reproducible y está validado contra datos reales.
- El **modelo de opinión** falló contra lo pre-registrado, y ese resultado negativo definió el producto: **escenarios**, no predicción (Fase 8, construida).
- La **capa visual pasó a ser el frente principal** por decisión del jefe de Daniel (18/09). Hitos 1 y 2 completos.
- La **página ya está publicada** en GitHub.
- Lo que sigue está en §6.

---

## 2. Cómo trabajar con Daniel (importante, ahorra fricción)

| | |
|---|---|
| Máquina | PC del CNC, `C:\Users\CNC.DSP-17291\Desktop\Bogot-Simulator`, clon de GitHub |
| **Qué tiene** | el código y `data/external/` |
| **Qué NO tiene** | `data/raw/` (microdatos) ni `data/processed/` — están en `.gitignore` a propósito |
| Consecuencia | **no puede correr los preparadores.** Hay que mandarle el código *y* los paquetes ya construidos |
| Cómo aplica cambios | a mano. No puede instalar Claude Code ahí. Pide un ZIP + **lista explícita de qué reemplazar y qué añadir** + los comandos |
| Terminal | PowerShell (VS Code). `.\venv\Scripts\Activate.ps1`, y el intérprete es `python` (no `python3`) |

`python src/utils/revisar_datos.py` dice qué hay en una máquina y qué falta.

**Regla R10 / DATA_INVENTORY §12.4:** los microdatos del CNC no salen de su
equipo ni se suben a ningún servicio. La ECP y la EPC sí son públicas.

---

## 3. Lo que se cerró en esta tanda (18–25 de septiembre)

### A05 — el índice de confianza (POPULATION_SPECIFICATION §8.4)
Se **midió** el umbral en vez de heredarlo: con 13 ítems, exigir 7 conserva el
97,8 % del donante y exigir los 13 conserva el 86,7 %, moviendo la media 0,007
sobre una escala de 4. Se queda en 7. Lo que faltaba era **registrar el
denominador**, y ahora viaja por fila (`n_items_confianza`), entra al metadata
(`escala_opinion`) y la página lo publica.

### Hito 2 — el tiempo (VISUALIZATION_SPECIFICATION §Hito 2)
Línea de tiempo con las dos series medidas (ECP 2013–2023, EPC 2014–2025) y
mapa por año conectado a ella. Cuatro capas, todas responden al año.

**Y destapó DI-V45, el hallazgo de la tanda:** el error estándar analítico
**subestima el ruido territorial**. `ee = sd/√n·√DEFF` supone independencia, y el
hot-deck agrupa la opinión por localidad **por construcción** (dos agentes de la
misma celda pueden recibir el mismo donante). Rehaciendo el pipeline con 20
semillas, ningún año supera su propio piso — incluido 2021, que con la fórmula
analítica parecía tener señal territorial y no la tiene.

> **El piso de ruido de un pipeline se mide rehaciéndolo, no derivándolo.**
> Una prueba de permutación NO sirve: rompe a la vez el vínculo
> localidad→demografía y el agrupamiento del hot-deck, y da p = 0,0005 para un
> efecto inexistente. Se intentó; está documentado para que no se repita.

Otros: DI-V36 (la rampa verde usaba raíz cuadrada sin declararlo), DI-V48 a
DI-V51 (población por año, capa de Crecimiento).

### Experimento 8 — LLM como donante (EXPERIMENT_8_RESULTS.md)
Pre-registrado, corrido con `xiaomi/mimo-v2.6-pro` sobre 1.266 de 1.269
personas retenidas, ~USD 0,48. **El LLM pierde en los dos ejes** y la regla de
decisión falla por ambos lados. El hot-deck se queda; **D28 se mantiene**.

Lo interesante es *qué* hace en su lugar: **aplana la variación entre personas
(0,30×) y exagera la entre instituciones (3,3×)**, con `Partidos políticos` en
media 1,00 — el piso exacto de la escala. Acierta el orden (Spearman 0,771) e
inventa las magnitudes: no simula personas, aplica un relato nacional sobre
instituciones a las 1.266 por igual.

Decidido el 25/09: **no se corre con un segundo modelo.** Se reabre solo si
alguien propone usar un LLM como donante.

---

## 4. Los tres números que hay que tener en la cabeza

1. **Las variables puente explican R² = 0,02** de la varianza de opinión
   individual. Una regresión lineal ya está en el piso teórico del MAE. Ningún
   motor —LLM incluido— crea información que no está en los datos.
2. **El hot-deck no predice individuos** (correlación 0,003) y reproduce la
   distribución casi perfecto (W1 0,057, sd ratio 0,958). Es un emparejador de
   distribuciones. Evaluarlo por MAE es evaluar algo que nunca intentó hacer.
3. **Con 1.000 agentes ninguna diferencia entre localidades sobrevive al ruido.**
   Es la mejor razón para escalar (A08), mejor que "correr más rápido".

---

## 5. La distinción que el tablero enseña

**El tiempo se puede leer; la geografía no.** La media de ciudad recorre
2,81 → 2,53 → 2,39 → 2,24 → 2,45 sobre márgenes de ±0,03: señal robusta. La
variación entre localidades dentro de cualquier año cabe dentro del ruido del
método. Por eso los agentes se colorean por opinión individual y la coropleta
carga la advertencia — y por eso la capa de **Crecimiento** sí puede afirmar
geografía: son proyecciones de población, no estimaciones de una muestra.

---

## 6. Qué sigue (ninguna elegida)

| | por qué |
|---|---|
| **Material para el CNC** | tiene que presentarle esto a su equipo, que no tiene contexto |
| **Escalar la población (A08)** | 10.000 o 100.000 agentes; el error por localidad cae por √10 y el mapa dejaría de estar dominado por ruido |
| **Hito 3 — bajo la localidad** | UPZ o manzana; exige datos y decisiones de modelo nuevas |
| **Simulación sobre la serie** | poner una corrida del modelo al lado de la serie medida; es lo que falta para que el tablero deje de ser solo lectura de datos |

---

## 7. Mapa de documentos

| Si vas a tocar… | lee |
|---|---|
| la página / el mapa | `claude/VISUALIZATION_SPECIFICATION.md` (v0.15, DI-V1 a DI-V51) |
| la población sintética | `POPULATION_SPECIFICATION.md` (v0.5) |
| qué datos hay y dónde | `claude/DATA_INVENTORY.md` |
| decisiones del proyecto | `PROJECT_CONTEXT.md` §39 (formato D0X) |
| LLM / agentes generativos | `claude/EVALUACION_AGENTES_GENERATIVOS.md` + `EXPERIMENT_8_*` |
| escenarios | `claude/SCENARIO_SPECIFICATION.md` |

**Convención que sostiene todo esto:** las decisiones se registran con
identificador, fecha y justificación, y **las expectativas fallidas no se
reescriben** — se reporta contra el pre-registro, no contra lo que resultó
(PROJECT_CONTEXT §45).

---

*Actualizar este documento cuando cierre un hito o cambie el rumbo. Si queda
desactualizado deja de servir para lo que existe.*
