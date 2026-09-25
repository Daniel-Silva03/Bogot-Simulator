# A08 — PASO 0b: ¿la composición exagera la diferencia entre localidades?

Proyecto: Bogotá Social Simulator
Versión: 0.1 — **pre-registro**
Fecha: 25 de septiembre de 2026
Estado: **código escrito y probado con datos simulados; sin correr sobre la EPC**
Código: `src/experiments/a08_paso0b.py` · Pruebas: `tests/test_a08_paso0b.py`
Origen: `A08_PASO0_RESULTS.md` §5, punto 2

---

## 1. La pregunta

El paso 0 mostró que, en la población sintética, la composición demográfica
separa las localidades con una dispersión de 0,07 a 0,12 (escala 1–5). Verlo
exige 100.000 agentes. Antes de construirlos:

> **¿La composición predice la diferencia territorial que la gente realmente
> reporta, o la exagera?**

Si la exagera, un mapa por composición mostraría un Bogotá más partido de lo que
es, y con la apariencia de precisión que dan 100.000 puntos.

La ECP no trae localidad y no puede responder. **La EPC sí**: localidad, sexo,
edad en bandas, estrato y opinión, en las mismas personas.

---

## 2. Método

Por ola de la EPC, para el ítem de gestión del alcalde (y, como réplica, el del
Concejo):

| Cifra | Qué es |
|---|---|
| `m_obs[l]` | Media ponderada medida en la localidad |
| `m_comp[l]` | Predicción por composición: cada persona recibe la media de su celda (sexo × edad × estrato) **estimada con las otras 18 localidades**, y se promedia con los pesos de la localidad |
| `sd_obs`, `sd_comp` | Dispersión entre localidades de cada una, **corregida por ruido de muestreo** con bootstrap dentro de localidad |
| **`R = sd_obs / sd_comp`** | < 1: la composición exagera · > 1: se queda corta |
| `r` | Correlación entre `m_obs` y `m_comp`: ¿apuntan a las mismas localidades? |
| `p_territorio` | Permutación de la localidad: ¿la EPC mide territorio más allá del azar? |

La celda se estima fuera de la propia localidad para que su ruido no entre en
las dos cifras a la vez y las haga parecer más iguales de lo que son.

### 2.1 Verificado antes de tocar la EPC (`tests/test_a08_paso0b.py`)

| Mundo simulado | Resultado |
|---|---|
| Solo composición | R = **1,04**, r = 0,86 |
| Contexto opuesto a la composición | R = **0,57** |
| Sin territorio | dispersión corregida 0,010 (cruda 0,141); 0 % de falsos positivos |

En el segundo caso, el contexto por sí solo daría 0,4. Sale 0,57 porque las celdas
se estiman con datos que ya traen el contexto mezclado. El pipeline real hace lo
mismo con el donante, así que R mide justo la discrepancia que tendría el mapa.

---

## 3. Predicciones pre-registradas

| # | Predicción | Umbral |
|---|---|---|
| **P1** | La composición apunta a las mismas localidades que lo medido | `r` mediana > 0,5 |
| **P2** | La composición predice la escala correcta, sin exagerar ni quedarse corta | `R` mediana entre 0,67 y 1,5 |
| **P3** | La EPC mide diferencias territoriales reales | `p_territorio` < 0,05 en al menos 5 de las 9 olas |

**Lo que las haría fallar, y qué significaría:**
- **P2 por debajo (R < 0,67):** personas del mismo perfil opinan distinto según
  dónde viven y ese contexto compensa la composición. El mapa por composición
  exageraría.
- **P2 por encima (R > 1,5):** hay territorio que la composición no ve. El mapa
  por composición lo subestimaría, y lo correcto sería un donante que use la
  localidad (reabrir DI-B10).

---

## 4. Regla de decisión

```
    R mediana en [0,67 ; 1,5]  y  r mediana > 0,5
        → la composición reproduce el patrón territorial a la escala correcta.
          La capa por composición a 100.000 agentes es defendible,
          rotulada como tal (A08_PASO0_RESULTS §4).

    R mediana < 0,67
        → la composición exagera. NO se publica la capa por composición
          tal como sale del pipeline. A08 pierde su argumento visual.

    R mediana > 1,5   o   r mediana ≤ 0,5
        → hay territorio que la composición no captura, o no apunta a las
          mismas localidades. La capa por composición no representa bien
          la ciudad. El camino es un donante con localidad (reabrir DI-B10).
```

---

## 5. Límites, dichos antes

- **Es otro constructo.** La EPC mide *gestión* del alcalde y del Concejo; el
  mapa muestra *confianza institucional* de la ECP (A20). Lo que se prueba es el
  mecanismo —si la composición predice bien el territorio en una encuesta de
  opinión de Bogotá—, no el número exacto de la ECP. Es la mejor evidencia
  disponible, no una prueba directa.
- **Poco n por localidad** (~60–80 por ola). Cada ola es ruidosa; la decisión
  usa la mediana sobre las nueve. El ruido se corrige con un bootstrap simple
  que ignora el diseño (A19): queda subestimado del orden de √DEFF ≈ 1,4, lo que
  **favorece** encontrar territorio en `sd_obs` más que en `sd_comp`.
- **Sumapaz no está** en el marco muestral de la EPC: 19 localidades.
- **Factores de expansión de 2014 y 2019** no reproducen el marginal territorial
  (DI-B10). Aquí importan menos: los promedios son *dentro* de cada localidad.

---

## 6. Cómo se corre

Necesita la EPC en la ruta que muestra `python src/utils/revisar_datos.py`
(`data/raw/bogota_como_vamos/empaquetado_2026-09/Encuesta de Percepción Ciudadana/Microdatos 2014 - 2025`)
o la variable `BSS_EPC_DIR` apuntando a donde esté.

```powershell
python tests/test_a08_paso0b.py                                  # ~2 min, sin datos reales
python src/experiments/a08_paso0b.py                             # gestión del alcalde
python src/experiments/a08_paso0b.py --item gestion_concejo      # réplica
```

Salida: `data/processed/a08/paso0b_<ítem>.json`. Los resultados van a
`A08_PASO0B_RESULTS.md`, **contra este pre-registro**.
