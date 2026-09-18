# EXPERIMENT 1 — Especificación: ¿reproduce el modelo una distribución observada?

Proyecto: Bogotá Social Simulator
Documento: especificación del Experimento 1 de RESEARCH.md (sección 49)
Versión: **0.2 — rehecha tras descubrir que el donante no tiene dos olas**
Fecha: 15 de septiembre de 2026

---

## 1. Qué cambió respecto a la versión 0.1

La versión 0.1 de este documento proponía un backtest 2024 → 2025 usando las "dos olas" del donante de la Veeduría Distrital. **Ese diseño no es viable**, y conviene entender por qué antes de leer el resto.

El primer paso del plan era el más barato: parsear las fechas y medir si había señal entre las olas. Se hizo, y lo que apareció fue esto:

```text
trabajo de campo: 2024-12-04  ->  2025-02-09   (68 días, continuos)

respuestas alrededor del "corte entre olas":
  2024-12-30    66
  2024-12-31    40
  2025-01-01     2
  2025-01-02    60
  2025-01-03    86
```

**No hay dos olas.** Hay una sola recolección continua de 68 días, con apenas dos días sin respuestas (un fin de semana). La separación "2024 / 2025" que `DATA_SPECIFICATION.md` describe como dos olas —línea base n=2.128 y seguimiento n=3.159— es un corte de calendario dentro de un único trabajo de campo, no dos mediciones separadas en el tiempo.

Los tamaños documentados sí son correctos: el parser reproduce exactamente 2.128 y 3.159, por un camino independiente. Lo que no es correcto es la interpretación de que se trate de dos mediciones comparables.

**Consecuencia:** no hay, en los datos que hoy tiene el proyecto, ninguna medición de opinión separada en el tiempo. Y sin separación temporal no se puede validar una dinámica. Es el hallazgo más importante de esta iteración, y la buena noticia es que costó una tarde y no un mes de trabajo sobre un experimento que no habría significado nada.

### 1.1 De paso: la columna de fechas estaba dañada

Para llegar a lo anterior hubo que resolver tres formatos mezclados en `Marca temporal`, y el patrón de la mezcla es informativo:

| familia | n | formato | días presentes |
|---|---|---|---|
| ISO/GMT | 649 | `Y/m/d h:M:S a.m. GMT-5` | 1–31 |
| con segundos | 2.888 | `m/d/Y H:M:S` | **13–31** |
| sin segundos | 1.750 | `m/d/Y H:M` | **1–12** |

Que la frontera entre las dos últimas familias sea exactamente "día > 12" contra "día ≤ 12" es la firma de un round-trip por hoja de cálculo: al abrirse el CSV, las filas cuyo día cabía como mes fueron reinterpretadas como fecha y reescritas sin segundos; las demás quedaron como texto. No es un archivo con dos convenciones, es un archivo dañado de forma sistemática.

La ambigüedad día/mes de la familia "sin segundos" no se puede resolver fila por fila —ningún componente pasa de 12— pero sí en conjunto: su primer componente solo toma los valores {1, 2, 12}, exactamente los meses de campo confirmados por las otras familias. Es `m/d/Y`.

Implementado en `parsear_marca_temporal()` (`src/population/loader.py`), con pruebas en `tests/test_donante_fechas.py` que fijan la interpretación: si alguien "arregla" el parser asumiendo `d/m/Y`, el reparto por año deja de coincidir con lo documentado y el test lo dice. El loader acepta ahora `desde` / `hasta` para recortar por fecha, con la advertencia explícita de que eso recorta una recolección, no selecciona olas.

## 2. Qué se puede validar hoy y qué no

`RESEARCH.md` sección 29 define cinco niveles de validación. Conviene separarlos, porque el proyecto está en condiciones de hacer dos y no los otros tres.

| Nivel | Qué pregunta | ¿Se puede hoy? |
|---|---|---|
| 1 — Población | ¿la población sintética reproduce Bogotá? | **Sí** |
| 2 — Estado inicial | ¿la distribución inicial de opinión coincide con lo observado? | **Sí**, con matices |
| 3 — Dinámica | ¿el modelo reproduce cambios observados? | **No** — falta separación temporal |
| 4 — Escenario | ¿responde de forma coherente al cambiar supuestos? | No (depende del 3) |
| 5 — Generalización | ¿funciona fuera del periodo de calibración? | No (depende del 3) |

El Experimento 1, tal como lo plantea `RESEARCH.md` sección 49, mezcla los tres primeros. Esta especificación los separa: **1A y 1B se corren ahora; 1C queda bloqueado y declarado como tal.**

## 3. Experimento 1A — Validación de la población (nivel 1)

**Pregunta:** ¿la población sintética de 1.000 agentes reproduce las distribuciones demográficas de Bogotá?

Es validación de verdad, con datos externos, y hoy es ejecutable. `PROJECT_CONTEXT.md` sección 24 la exige explícitamente antes de validar la dinámica, y `muestreo.diagnostico_territorial()` ya cubre una de las cuatro dimensiones.

**Marginales objetivo:**

| Dimensión | Fuente | Estado |
|---|---|---|
| localidad | proyecciones DANE-SDP 2025, 18+ | ✅ `data/external/marginal_localidad_18mas.csv` |
| edad × sexo | mismas proyecciones, hoja `Localidades` (tiene edad simple y sexo) | falta extraer |
| nivel educativo | Multipropósito 2021 ponderada por `FEX_C` | calculable con lo que hay |
| estrato | Multipropósito 2021 ponderada por `FEX_C` | calculable con lo que hay |

**Métricas:** distancia total de variación por dimensión (la misma que ya usa el diagnóstico territorial), más el detalle por categoría.

**Qué esperar:** el muestreo ponderado (D14) corrige por construcción las dimensiones que el ponderador cubre, así que un buen ajuste en edad, sexo, educación y estrato **no sería un hallazgo** — sería una comprobación de que la ponderación se aplicó bien. El valor está en encontrar dónde *no* ajusta: ahí aparecen los límites del ponderador y del tamaño de muestra.

**Nota honesta:** las proyecciones DANE-SDP son de 2025 y Multipropósito es de 2021. La población sintética hereda la estructura de 2021 ponderada hacia el total de 2021, comparada contra marginales territoriales de 2025. Es una inconsistencia menor de años ya anotada en D14, y en esta comparación hay que declararla.

## 4. Experimento 1B — Validación del estado inicial (nivel 2)

**Pregunta:** ¿la distribución de `opinion_t0` de los agentes coincide con la distribución observada de confianza institucional en Bogotá?

**Por qué no es completamente circular, y por qué tampoco es fuerte.** `opinion_t0` se copió del donante por hot-deck, así que algo de circularidad hay. Pero entre el donante y la población sintética pasaron tres cosas: el muestreo ponderado por `FEX_C`, el emparejamiento por bloques localidad × sexo, y el vecino más cercano en edad y educación. La población resultante **no** es una copia de la distribución del donante: es esa distribución reponderada hacia la estructura demográfica real de Bogotá.

Entonces la comparación correcta no es contra el donante crudo —eso sí sería circular— sino contra el **donante ponderado** por raking, que es la mejor estimación disponible de la distribución real. Si las dos coinciden, el hot-deck y el muestreo se están componiendo bien. Si difieren, hay un sesgo en la composición que ninguno de los dos corrigió.

**Prerrequisito duro:** la ponderación del donante (raking localidad × educación) está documentada en el Anexo de `DATA_SPECIFICATION.md` con su n efectivo de 2.409, pero **no existe como código**. Hay que recuperarla. Sin ella, esta comparación sería contra una distribución con 84% de educación técnica o superior, que no es Bogotá.

**Métricas:** Wasserstein-1 (en unidades de la escala 1–5), KS, y error por localidad restringido a las localidades con muestra suficiente en ambos lados.

**Segundo prerrequisito:** arreglar la pérdida de varianza del hot-deck. `opinion_t0` tiene hoy 45 valores únicos entre 1.000 agentes, con el 46% concentrado en cinco, porque el desempate entre donantes empatados es determinista (`POPULATION_SPECIFICATION.md` 8.3). Una comparación de distribuciones contra una entrada granulada mide la granulación.

## 5. Experimento 1C — Validación de la dinámica (nivel 3): BLOQUEADO

**Pregunta:** ¿predice el modelo el cambio observado en la distribución de opinión?

**No se puede ejecutar hoy.** Requiere al menos dos mediciones de la misma variable separadas en el tiempo, y el proyecto no tiene ninguna. Es la restricción real, y no se resuelve con más código.

Conviene decirlo sin rodeos porque afecta al criterio de éxito del MVP: `PROJECT_CONTEXT.md` sección 37 pide que "el modelo reproduzca algunos patrones observados mejor que determinados baselines", y hasta que exista 1C eso no se puede afirmar ni negar. Todo lo construido —población, redes, modelos de opinión, runner— es maquinaria verificada internamente y sin validar contra la realidad.

### 5.1 Qué desbloquearía 1C

| Fuente | Qué aportaría | Cómo se consigue | Plazo |
|---|---|---|---|
| **Bogotá Cómo Vamos** | serie anual desde 1998 de percepción y confianza — la mejor opción por lejos | los informes son públicos; el **microdato requiere solicitud formal** | semanas o meses |
| **CNC** (A02) | posible tracking/panel; permitiría además validación micro (transiciones) | pendiente de recepción | desconocido |
| **ECSC (DANE)** | serie anual de percepción de seguridad, microdatos públicos | descarga directa | días |

La ECSC es la única descargable de inmediato, pero mide **percepción de seguridad**, no confianza institucional — que es la variable fijada en D11. Usarla implicaría o bien cambiar la variable del primer experimento (reabriendo D11), o bien tratarla como un segundo fenómeno de prueba. Ninguna de las dos es gratis, pero la segunda es defendible: validar la maquinaria sobre una variable con datos temporales, y aplicar después el método a confianza institucional cuando lleguen sus datos.

### 5.2 Recomendación de prioridad

**Solicitar el microdato de Bogotá Cómo Vamos pasa a ser crítico, no "conviene pedirlo temprano".** Es el único camino conocido que valida la variable que el proyecto eligió (D11) con la profundidad temporal que la metodología exige (`RESEARCH.md` secciones 27-30). Mientras no llegue, el nivel 3 de validación está detenido, y con él los niveles 4 y 5.

Segunda prioridad: insistir con A02. Si el CNC tiene un tracking con la misma pregunta repetida, resolvería 1C y además habilitaría validación de transiciones individuales, que es el estándar de Gestefeld & Lorenz y que BCV, al ser corte transversal repetido, no permite.

## 6. Criterio de éxito, fijado antes de correr

**1A (población):** exitoso si la distancia total de variación es menor a 0,05 en localidad, edad, sexo y educación. Se espera que sí — sería raro que no, dado D14 — y el interés está en qué dimensión queda peor.

**1B (estado inicial):** exitoso si el Wasserstein-1 entre `opinion_t0` y el donante ponderado es menor que el Wasserstein-1 entre `opinion_t0` y el donante **sin** ponderar. Es decir: la población sintética debe parecerse más a la mejor estimación de Bogotá que a la muestra sesgada de la que salió. Si no, el muestreo ponderado no está aportando lo que se supone.

Ese criterio es deliberadamente exigente y puede fallar. Si falla, el resultado es que la cadena hot-deck + muestreo no propaga bien la corrección de sesgo, y eso es información sobre A05.

**1C:** no aplica hasta que haya datos.

## 7. Plan de trabajo

1. ~~Parsear fechas y medir señal entre olas~~ — **hecho; resultado: no hay olas.**
2. Recuperar la ponderación del donante como código (prerrequisito de 1B).
3. Arreglar la pérdida de varianza del hot-deck (prerrequisito de 1B).
4. Extraer los marginales de edad × sexo, educación y estrato (prerrequisito de 1A).
5. Correr 1A y 1B; reportar contra el criterio de la sección 6.
6. En paralelo y con prioridad: solicitud del microdato de Bogotá Cómo Vamos.

Los pasos 2 y 3 son los mismos que el review de septiembre dejó abiertos en `POPULATION_SPECIFICATION.md` sección 8. No son deuda menor: son los que hoy separan a la población sintética de poder validarse.

## 8. Qué NO demuestran 1A y 1B

Ninguno de los dos dice nada sobre el modelo de opinión. Validan la **población**: que reproduce la demografía de Bogotá y que su estado inicial de opinión es una estimación razonable del observado. La dinámica —lo que el proyecto quiere simular— sigue sin validar y seguirá así hasta que exista 1C.

Vale la pena que esto quede escrito tal cual en cualquier presentación de resultados: es exactamente la distinción entre "el simulador funciona" y "el simulador se parece a Bogotá", y confundirlas es el riesgo R05 del proyecto.

---

*Documento vivo — los resultados se registran en EXPERIMENT_1_RESULTS.md. El hallazgo de la sección 1 requiere corregir la descripción de las "dos olas" en DATA_SPECIFICATION.md.*
