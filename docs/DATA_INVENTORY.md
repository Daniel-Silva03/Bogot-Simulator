# DATA INVENTORY — Qué está especificado vs. qué está realmente en disco

Proyecto: Bogotá Social Simulator
Documento: complemento operativo de DATA_SPECIFICATION.md
Versión: 0.13 — BCV responde la consulta (§13.7): confirma que la batería de confianza es nueva, aporta dos olas de conglomerado que no habíamos visto, y explica por qué faltan las otras
Versión 0.12 — llega el empaquetado completo de Bogotá Cómo Vamos, 2014-2025 (§13.6). **La batería de confianza NO es anual** —corrige la v0.11— pero hay nueve olas de evaluación de gestión, y una inversión de códigos que hay que reportarle a BCV
Versión 0.11 — entra Bogotá Cómo Vamos 2025 (§13): **sí tiene batería de confianza**, anual, y con localidad
Versión 0.10 — descargadas ECP 2013 y 2015. **2013 entra; 2015 NO**, y la razón corrige la v0.9 (§10.8)
Versión 0.9 — verificación previa contra metadatos: parecía que 2013 y 2015 eran apilables
Versión 0.8 — los estudios del CNC salieron de `data/raw/` y su ruta deja de estar escrita en el código (§12.4, DI-N7)
Versión 0.7 — entraron los cuatro estudios del CNC (§12), sus agregados derivados y el régimen de confidencialidad que los gobierna; se cerró el bloqueo del cuestionario de la ECP (§10.4); ECP Capital Social documentada (§10.7)
Fecha: 16 de septiembre de 2026

---

## 1. Por qué existe este documento

`DATA_SPECIFICATION.md` inventaría ocho fuentes y marca varias como "Confirmado". Ese "confirmado" significa **"verificamos que el dataset existe y sirve"**, no **"lo tenemos descargado"**. Son dos cosas distintas y la diferencia se había vuelto invisible: el prototipo de 1.000 agentes había corrido con datos reales, pero los archivos que usó no estaban en el repositorio.

Este documento separa las dos cosas explícitamente y no vuelve a usar la palabra "confirmado" sin decir para qué.

**Nota heredada de la v0.6.** Este documento llevaba las proyecciones DANE-SDP como faltantes desde la v0.2, cuando en realidad el anexo estaba en `data/raw/` y el marginal territorial se regenera desde él byte por byte. Es el error opuesto al que el documento existe para evitar: decir que falta algo que está. Queda anotado en vez de corregido en silencio, porque el punto de esta bitácora es que la diferencia entre "verificado" y "supuesto" sea visible también cuando el equivocado es este archivo.

**Nota sobre la v0.7.** Entra una fuente que **no se descarga ni se versiona ni se sube a ninguna parte**: los cuatro estudios que el CNC entregó. Es el primer dato del proyecto con restricción de circulación real, y por eso §12 no es una fila más de la tabla sino una sección con su propio régimen.

**Estado al 16/09/2026:** el pipeline de población es reproducible de punta a punta y está anclado a un marginal territorial oficial; la serie temporal de confianza que hacía falta para validar dinámica está en disco, cargada por código y ya usada para falsear el modelo (Experimento 3); y hay medición empírica del grado y la composición de la red.

## 2. Estado real, dataset por dataset

| Dataset | Rol en el proyecto | ¿Está en el repo? | Qué falta |
|---|---|---|---|
| **Multipropósito 2021** (microdato completo) | Origen del extracto | ✅ `data/raw/em2021.csv` (1,25 GB) | — |
| **Multipropósito 2021** (extracto) | Receptor del hot-deck | ✅ `data/raw/em2021_receptor_v2.csv` (292.281 filas) | — (cerrado como D14) |
| Script de extracción | Genera el extracto y el marginal | ✅ `src/population/extraer_columnas_em2021.py` | — |
| **Confianza Institucional** (Veeduría Distrital) | Donante de opinión (D11) | ✅ `data/raw/base_encuestaconfianza_2024-2025.csv` (5.287 filas) | — |
| **Proyecciones DANE-SDP por localidad** (anexo 2021) | Marginal territorial | ✅ `data/raw/anexo-proyecciones-poblacion-bogota-...xlsx` (2,7 MB) | — |
| **Proyecciones DANE-SDP, revisión 2025** (CSV) | Marginal territorial vigente | ✅ `data/raw/osb_demografia-poblacion-localidad.csv` | — (adoptada, §11.3) |
| Marginal territorial derivado | Objetivo del muestreo PPS y del diagnóstico | ✅ `data/external/marginal_localidad_18mas.csv` | — (regenerado contra la revisión 2025) |
| **ECP DANE 2017 / 2019 / 2021 / 2023** | Serie temporal de confianza (validación nivel 3) | ✅ `data/raw/ecp/<año>/` — 3 módulos por año | — |
| **ECP DANE 2013** (cat. 283) | Alarga la serie: 3 → 4 transiciones | ✅ `data/raw/ecp/2013/` | — verificado contra los datos, §10.8 |
| **ECP DANE 2015** (cat. 406) | — | ⚠️ descargada pero **excluida** | Los códigos apuntan a otras instituciones — §10.8 |
| ECP DANE 2011 / 2008 / 2007 | Extender más atrás | ❌ No | Instrumento distinto — **no apilar sin crosswalk**, §10.8 |
| **ECP — Participación y Capital Social** 2019/2021/2023 | Grado y composición empírica de la red | ✅ `data/raw/ecp/<año>/` — 2 módulos más por año | No existe en 2017 |
| Cargador de la ECP | Lee y valida los cuatro años + Capital Social | ✅ `src/population/ecp.py` + `tests/test_ecp.py` (11 tests, 60 aserciones) | — |
| **Cuestionario ECP 2023** (nombres de los 15 ítems) | Alinear la ECP con los 8 actores del donante | ✅ recuperado del PDF publicado por DANE — §10.4 | — |
| **Estudios del CNC** (4 encuestas) | Evidencia territorial; librería de estimación con diseño | ⚠️ en el equipo de Daniel, **fuera del repositorio** (movidos el 16/09/2026) — §12 | No se versionan ni se suben nunca |
| Agregados derivados del CNC | Lo único que sale de esos estudios | ✅ `data/external/cnc/` (8 archivos) | — |
| Ponderación del donante (raking/IPF) | Corrige el sesgo educativo | ❌ No | El Anexo de `DATA_SPECIFICATION.md` reporta resultados (n efectivo 2.409) — ese cálculo existió pero no quedó como código |
| **Bogotá Cómo Vamos 2025** (Empaquetado Web) | Validación externa · opinión **por localidad** | ✅ `data/raw/bogota_como_vamos/Empaquetado-Web/` | Solo la ola 2025 — pedir las anteriores, §13 |
| **Cartografía IDECA** | Capa geográfica del dashboard | ❌ No | No se necesita hasta la Fase 10 |
| **OSM — vías arteriales de la región** | Capa base del mapa (solo dibujo) | ✅ `data/external/geo/osm/vias.geojson` (5,1 MB) | — |
| **OSM — áreas verdes de la región** | Capa base del mapa (solo dibujo) | ✅ `data/external/geo/osm/verde.geojson` (5,0 MB) | — |
| **OSM — agua de la región** | Capa base del mapa (solo dibujo) | ❌ No | Llegó pegada como texto en el chat, no como archivo; falta dejarla en `data/external/geo/osm/agua.geojson` — DI-V14 |
| **CNPV 2018 / GEIH / ECSC** | Marginales y percepción de seguridad | ❌ No | No se necesitan para los experimentos en curso |

## 3. Qué se necesita para cada cosa

**Para correr los Experimentos 1 y 2 (generadores de red + Friedkin-Johnsen):** nada nuevo. Solo consumen `data/processed/poblacion_sintetica_v2.csv`.

**Para regenerar la población sintética desde cero:** ya está todo. Verificado.

**Para que los resultados territoriales signifiquen algo:** resuelto en lo técnico (el marginal existe y la población v2 lo replica, §11.2) y **cerrado en lo sustantivo por la negativa**: los estudios del CNC muestran que no hay fenómeno territorial que reproducir (§12.3). El diagnóstico territorial sigue siendo obligatorio como control de sesgo de la población, no como objetivo del modelo.

**Para validar dinámica (nivel 3):** hecho. El donante de la Veeduría **no tiene dos olas** (trabajo de campo continuo 2024-12-04 → 2025-02-09), así que no había un "antes y después". La ECP da cuatro mediciones de la misma pregunta con el mismo código de variable. Ver §10. El Experimento 3 ya corrió contra ella.

**Para calibrar la red con datos en vez de supuestos:** resuelto. §10.7.

**Para el backtesting de la Fase 8:** Bogotá Cómo Vamos, y confirmar si hay microdatos bajo solicitud. No es urgente, pero el tiempo de respuesta de una solicitud formal sí lo es — conviene pedirlo temprano aunque se use tarde.

## 4. El problema de la ponderación (cerrado como D14)

El extracto `em2021_receptor_v2.csv` tenía cinco columnas: `NOMBRE_LOCALIDAD, NVCBP11AA, NPCEP4, SEXO, NPCHP4`. **Ninguna era un factor de expansión.** Multipropósito sobre-muestrea localidades pequeñas para poder estimar a nivel de localidad; sin ponderar, esa distorsión pasaba entera a la población sintética:

| Localidad | Agentes (de 1.000) | Tamaño real |
|---|---|---|
| Bosa | 38 | de las más pobladas |
| Teusaquillo | 56 | de las menos pobladas |
| Santa Fe | 45 | pequeña |
| Chapinero | 51 | pequeña |

Importa directamente para el generador territorial de `NETWORK SPECIFICATION.md`: los \(n_l\) por localidad alimentan el despeje de \(p_{intra}\) y \(p_{inter}\).

**Cerrado como D14** — muestreo PPS sistemático con el factor de expansión. Distancia territorial al marginal 0,172 → 0,041 (y 0,032 contra el marginal revisado de 2025, §11.3).

Queda la simetría incómoda del otro lado: el Anexo de `DATA_SPECIFICATION.md` documenta la ponderación del **donante** (raking por localidad × educación, n efectivo 2.409), pero ese cálculo no quedó como código.

## 5. Códigos de no-respuesta tratados como estrato (A17)

En el extracto, `NVCBP11AA` toma valores 0–6 pero también **8 (8 casos) y 9 (197 casos)**, que en Multipropósito son códigos de no-respuesta, no estratos. El loader los deja pasar y `validar_agentes` los acepta explícitamente (rango 0–9). Sobreviven 39 en el receptor final de 168.200.

Son pocos, pero en la distancia homofílica del generador de red un agente con `estrato = 9` se trata como *más extremo que estrato 6*, y uno con `estrato = 0` ("sin estratificar", típicamente rural) como *por debajo de estrato 1*.

**Evidencia a favor de tratarlos como faltantes**, de la ECP: el estrato (`P4031S1A1`) va de **0 a 6 sin códigos 8/9**, con el 0 etiquetado explícitamente como *"conexión ilegal - pirata"*, y la no-respuesta viene como celda vacía (13 casos en Bogotá 2017). Otra encuesta DANE sobre la misma población codifica la no-respuesta como faltante, no como un valor en la escala.

## 6. Convención para `data/`

```text
data/
├── raw/          # descargas originales, sin modificar, nunca versionadas (gitignore)
│   ├── em2021.csv                                          ✅ 1,25 GB
│   ├── em2021_receptor_v2.csv                              ✅ extracto
│   ├── base_encuestaconfianza_2024-2025.csv                ✅ donante
│   ├── anexo-proyecciones-poblacion-bogota-...xlsx         ✅ 2,7 MB
│   ├── osb_demografia-poblacion-localidad.csv              ✅ revisión 2025
│   └── ecp/{2017,2019,2021,2023}/                          ✅ 3–5 módulos por año
├── external/     # marginales y tablas de referencia pequeñas, SÍ versionadas
│   ├── marginal_localidad_18mas.csv                        ✅ derivado, reproducible
│   ├── cnc/                                                ✅ solo agregados — §12.2
│   └── geo/osm/                                            ✅ extractos OSM para la capa base (ODbL)
└── processed/    # salidas del pipeline, regenerables
    ├── poblacion_sintetica_v2.csv
    └── poblacion_sintetica_v2_metadata.json
```

`data/raw/` va en `.gitignore`, lo que hace obligatorio que los scripts que reconstruyen los extractos sí estén versionados. Lo están. `data/external/` sí se versiona: son pocos kilobytes y es lo que permite correr el muestreo sin el anexo de 2,7 MB.

**Los microdatos del CNC ya no están bajo `data/`.** Se sacaron del repositorio el 16/09/2026 y viven fuera de él; `data/external/cnc/` conserva solo los agregados. Un `.gitignore` habría protegido contra `git push`, no contra un servicio de sincronización que mire la carpeta. Ver §12.4.

Dos cosas para limpiar: `data/processed/` contiene un `Claude Setup.exe` de 7 MB que no pertenece ahí, y la salida se guarda como `.csv` porque `pyarrow` no estaba instalado al correr, mientras `ARCHITECTURE.md` espera `.parquet`.

## 7. Dónde se consiguen

- **Multipropósito 2021** — [microdatos.dane.gov.co, catálogo 743](https://microdatos.dane.gov.co/index.php/catalog/743/get-microdata), también en [Datos Abiertos Bogotá](https://datosabiertos.bogota.gov.co/dataset/encuesta-multiproposito-2021-sdp).
- **Confianza Institucional (Veeduría Distrital)** — [Base de Datos Encuesta Confianza Entidades Distritales](https://datosabiertos.bogota.gov.co/dataset/base-de-datos-encuesta-confianza-entidades-distritales). Licencia CC BY-SA 4.0.
- **ECP DANE** — sección 10.
- **Proyecciones de población por localidad** — sección 11.
- **Estudios del CNC** — no se descargan: los entrega el CNC. Sección 12.
- **Bogotá Cómo Vamos** — bogotacomovamos.org publica informes; el microdato requiere solicitud.

## 8. Verificación del donante

El export de la Veeduría viene con los encabezados en cp850 mal decodificado, y `loader.py` localiza sus columnas por fragmentos de texto que dependen de esos bytes. El script de extracción tiene un modo que comprueba, antes del hot-deck, que cada fragmento localice exactamente una columna:

```
python src/population/extraer_columnas_em2021.py confianza
```

Resultado contra el archivo publicado (15/09/2026): 144 columnas, 5.287 filas, las 4 columnas de identificación y los **8** actores del núcleo de confianza localizados sin ambigüedad. Eso resolvió una inconsistencia abierta: `DATA_SPECIFICATION.md` decía "7 actores evaluados por separado" pero enumeraba 8. **Son 8.**

## 9. Qué hacer, en orden

1. ~~Re-extraer Multipropósito con el factor de expansión~~ ✅ D14.
2. ~~Descargar y cargar la ECP~~ ✅ los cuatro años, §10.
3. ~~Marginal territorial DANE-SDP~~ ✅ ya estaba, §11; adoptada la revisión 2025.
4. ~~Experimento 3 — validación de nivel 3 contra la ECP~~ ✅ corrido. Ver `claude/EXPERIMENT_3_RESULTS.md`.
5. ~~Conseguir el cuestionario de la ECP~~ ✅ §10.4.
6. ~~Cargar Participación y Capital Social de la ECP~~ ✅ §10.7.
7. ~~Explorar los estudios del CNC sin sacar microdatos del equipo~~ ✅ §12.
8. Resolver los códigos 8/9 de estrato (A17, §5).
9. Adoptar `svy_prop` (varianza por linealización de Taylor) en lugar de las medias ponderadas ingenuas del proyecto — §12.5.
10. Recuperar como código la ponderación del donante.
11. Solicitar microdatos de Bogotá Cómo Vamos — temprano, porque la respuesta puede tardar.
12. Sacar `Claude Setup.exe` de `data/processed/` e instalar `pyarrow`.

---

## 10. ECP DANE — descargada y verificada

### 10.1 Mapa de módulos y de nombres

Verificado contra los diccionarios, el DDI/XML y el microdato de los cuatro catálogos.

| Año | Catálogo | Carpeta de viviendas, tal como viene | Democracia | Formatos |
|---|---|---|---|---|
| 2017 | 515 | `Tabla viviendas` (F1) | F6 | `.sav` + `.txt` (tab) |
| 2019 | 644 | `Viviendas` (F15) | F20 | `.sav` + `.dta` + `.csv` |
| 2021 | 730 | `Viviendas` (F7) | F12 | `.sav` + `.dta` + `.csv` |
| 2023 | 822 | `Tabla de viviendas` (F15) | F20 | `.sav` + `.dta` + `.csv` |

URL: `https://microdatos.dane.gov.co/index.php/catalog/<catálogo>/get-microdata`

**Nada de esto es estable entre años**, y por eso `src/population/ecp.py` no tiene ni una ruta escrita a mano. Cambian: el identificador de archivo (`F6`/`F20`/`F12`/`F20` para el mismo módulo), el nombre de la carpeta (tres variantes para viviendas), el nombre del archivo — incluida una errata de DANE, `Caracteríasticas generales.csv` en 2023 —, el separador (2017 sale en `.txt` por tabuladores, el resto en `.csv` por comas) y la ubicación del ponderador. Los módulos se localizan por **nombre normalizado** (sin tildes, sin mayúsculas, solo letras) buscando las raíces `vivienda`, `caracteri` y `democracia`, más `participacion` y `capitalsocial` como módulos opcionales.

**El ponderador es `FEX_P` de Viviendas, en los cuatro años.** Es la única regla que aplica a todos: en el archivo de personas aparece en 2017 (los tres módulos lo traen), solo como `FEX_P_CENSO_2018` en 2019, y en ninguno en 2021 y 2023. En 2017, donde se puede comparar, el `FEX_P` de personas y el de viviendas **coinciden exactamente** en las 38.761 filas.

2019 trae además `FEX_P_CENSO_2018`, reponderado contra el Censo 2018, que da un total distinto para Bogotá (5.810.318 contra 6.088.233). El cargador lo expone pero **no lo usa**: mezclar dos bases censales dentro de una misma serie mete un salto que no es cambio de opinión.

### 10.2 El panel de Bogotá

`REGION == 1` es Bogotá. Los merges se validan, no se asumen: personas × Democracia por las cuatro claves, y × Viviendas por `DIRECTORIO`. **Cero pérdidas y cero huérfanas en los cuatro años.**

| Año | Personas 18+ en Bogotá | Población expandida |
|---|---|---|
| 2017 | 5.137 | 5.866.820 |
| 2019 | 5.429 | 6.088.233 |
| 2021 | 4.945 | 6.069.474 |
| 2023 | 4.451 | 6.233.947 |

Total del panel: **19.962 personas**. Comparable en tamaño al donante de la Veeduría (5.287), y con la misma escala 1–5.

**No es un panel en sentido estricto** — son cuatro cortes transversales independientes de la misma encuesta, no las mismas personas seguidas en el tiempo. El nombre se conserva porque así se llama en el código (`cargar_panel`), pero no permite trayectorias individuales.

### 10.3 Los ítems: 13 de 15, y una trayectoria en V

**`P5263S6` y `P5263S12` vienen vacíos en los cuatro años** — cero respuestas, no "pocas". La razón está en §10.4 y no es un defecto de datos. La serie utilizable son los otros **13 ítems**, y como el vacío es consistente, la intersección es estable.

Medias ponderadas, escala 1–5, con el código 99 (No sabe/No informa) fuera:

| Ítem | 2017 | 2019 | 2021 | 2023 | | Ítem | 2017 | 2019 | 2021 | 2023 |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | 2,487 | 2,356 | 2,226 | 2,511 | | S9 | 2,391 | 2,293 | 2,266 | 2,438 |
| S2 | 2,428 | 2,406 | 2,404 | 2,537 | | S10 | 1,988 | 1,952 | 1,947 | 2,020 |
| S3 | 2,916 | 2,860 | 2,650 | 2,771 | | S11 | 2,669 | 2,713 | 2,393 | 2,703 |
| S4 | 2,280 | 2,036 | 1,998 | 2,035 | | S13 | 2,670 | 2,310 | 2,207 | 2,471 |
| S5 | 2,430 | 2,114 | 2,112 | 2,333 | | S14 | 2,998 | 2,722 | 2,366 | 2,657 |
| S7 | 2,448 | 2,277 | 2,193 | 2,474 | | S15 | 2,383 | 2,348 | 2,157 | 2,308 |
| S8 | 2,426 | 2,291 | 2,260 | 2,340 | | | | | | |

**Hallazgo 1 — los 13 ítems tocan su mínimo en 2021.** Los trece, sin una sola excepción, y se recuperan en 2023. El índice agregado (media de los 13) recorre **2,501 → 2,360 → 2,244 → 2,431**.

**Hallazgo 2 — los ítems se mueven como uno solo.** Quitando el nivel propio de cada ítem, el **81 % de la variación entre años** cae en un único componente, y las 13 cargas tienen el mismo signo. Consecuencia práctica: el objetivo dinámico es esencialmente **un número por año**.

**Hallazgo 3 — la forma de la distribución también cambia, y no como la media.** Índice de confianza por persona (media de los ítems válidos, mínimo 7 de 13), ponderado:

| Año | n | media | sd | bimodalidad | % < 2,0 | % > 3,5 |
|---|---|---|---|---|---|---|
| 2017 | 5.046 | 2,503 | 0,934 | 0,420 | 27,4 % | 14,2 % |
| 2019 | 5.298 | 2,362 | 0,903 | 0,405 | 34,3 % | 9,7 % |
| 2021 | 4.858 | 2,245 | 0,897 | 0,447 | 37,1 % | 7,1 % |
| 2023 | 4.238 | 2,430 | **0,764** | 0,349 | 23,2 % | **5,3 %** |

- La **dispersión se contrae** un 18 % hacia 2023.
- **Nunca hay bimodalidad** (0,35–0,45, muy por debajo del umbral de 0,555). Que FJ y DeGroot no fragmenten no es una falla contra estos datos — Bogotá tampoco se fragmentó. Es la única de las cinco predicciones del Experimento 3 que el modelo acierta.
- La V **no es simétrica**: la cola de alta confianza se vacía de forma monótona (14,2 % → 5,3 %, sin rebote) mientras la masa de baja confianza hace la V. La "recuperación" de 2023 es gente desconfiada moviéndose al centro, no confiados volviendo.

**Advertencia sobre 2023:** la no-respuesta promedio es estable en 2017–2021 (2,2 % / 3,0 % / 2,1 %) y **salta a 5,6 % en 2023**. Parte del rebote puede ser gente que dejó de contestar. Antes de leer 2023 como recuperación hay que mirar quién se cayó. Sigue pendiente.

La caída hasta 2021 coincide con el paro nacional de 2021 y el ciclo electoral, pero **este documento no afirma causalidad**: son dos series puestas una al lado de la otra.

### 10.4 Los nombres de los ítems — resuelto, y por qué faltaban dos

Los nombres de las 15 instituciones **no están en ningún metadato**: no en el DDI de ninguno de los cuatro años; no en las etiquetas de variable de los `.sav` (las 15 comparten literalmente la misma etiqueta genérica de 149–151 caracteres); no en "Materiales relacionados" del catálogo; no en los ZIP descargados.

Se recuperaron del **formulario publicado** de la ECP 2023 (`Formulario_ECP_2023 _VF.pdf` — el nombre del archivo lleva un espacio antes de `_VF`, que es por lo que la primera búsqueda daba 404). El orden de las opciones a…o mapea a S1…S15:

| Código | Institución | | Código | Institución |
|---|---|---|---|---|
| S1 | Procuraduría General de la Nación | | S9 | Policía |
| S2 | Alcaldía Municipal/Distrital | | S10 | Partidos o movimientos políticos |
| S3 | Fuerzas Militares | | S11 | Defensoría del Pueblo |
| S4 | Congreso de la República | | **S12** | **Gobernación** |
| S5 | Jueces y magistrados | | S13 | Fiscalía General de la Nación |
| **S6** | **Asamblea departamental** | | S14 | Registraduría Nacional del Estado Civil |
| S7 | Contraloría | | S15 | Presidencia de la República |
| S8 | Concejos municipales/distritales | | | |

**Y eso explica el vacío de §10.3.** `S6` es *Asamblea departamental* y `S12` es *Gobernación*: **Bogotá D.C. no tiene ninguna de las dos.** No es dato faltante, es un hecho institucional. Verificación cruzada: en 2023 esos mismos ítems tienen 37.143 y 38.203 respuestas válidas a nivel nacional, y cero en Bogotá.

El mapeo letra→código se verificó por tres anclas independientes que coinciden con las medias de §10.3: **S10 es el ítem más desconfiado de los cuatro años** (1,95–2,02) y es *Partidos políticos*; **S3 y S14 son los más confiados** y son *Fuerzas Militares* y *Registraduría*; y S6/S12 son exactamente las dos instituciones departamentales. `ETIQUETAS_ITEMS` en `src/population/ecp.py` lo fija, con test.

### 10.5 Limitación estructural

La ECP da profundidad temporal (4 puntos, 2017–2023) a cambio de resolución territorial: llega a *Bogotá* como región, no a localidad. Sirve para validar la **dinámica agregada** del modelo, no la territorial. Esa depende de Multipropósito, del marginal de §11 y — para opinión — de los estudios del CNC (§12.3).

### 10.6 Cómo se usa

```python
from src.population.ecp import (cargar_panel, serie_confianza, cobertura_items,
                                cargar_capital_social, describir_items)

panel = cargar_panel("data/raw/ecp")          # 19.962 personas, 4 años, Bogotá
serie = serie_confianza(panel)                 # 13 ítems × 4 años, ponderado
cobertura_items(panel)                         # chequeo previo a construir series
cs = cargar_capital_social("data/raw/ecp", 2023)
```

```
python src/population/ecp.py     # resumen por consola
python3 tests/test_ecp.py        # 11 tests, 60 aserciones, todos pasan (16/09/2026)
```

### 10.7 Participación y Capital Social — la red, medida

Dos módulos más por año (2019, 2021 y 2023; **no existen en 2017**), que resultaron ser la fuente más útil de toda la ECP para el diseño del simulador, porque miden directamente lo que `NETWORK SPECIFICATION.md` venía suponiendo.

| Variable | Qué mide | Bogotá 2023 |
|---|---|---|
| **`P2047` + `P2049`** | tamaño del círculo cercano (visitas mutuas + apoyo/confianza) | **media 5,35 · mediana 4 · 26 % sin red** |
| **`P2051S1`…`S11`** | composición de ese círculo (11 descripciones) | 39,5 % comparte opiniones políticas · 12,4 % comparte cuadra |
| `P2025S1`…`S6` | confianza interpersonal (familia, amistades, colegas, vecinos, extranjeros, desconocidos) | r ≈ +0,25 con confianza institucional |
| `P2001S1`…`S17` | pertenencia a organizaciones | cruza con el capítulo J de Multipropósito |

La correspondencia `P2051S*` → descripción **no está publicada**. Se estableció reproduciendo el Cuadro 9 del anexo `anex-ECP-CapitalSocial-2023.xls` (nacional / cabeceras / rural), con una discrepancia máxima de **0,04 pp sobre 33 comparaciones**, tras corregir dos errores propios: faltaba el ítem "Hombres" y el denominador correcto es `P2047 + P2049`, no `P2047`. Está fijada en `ETIQUETAS_COMPOSICION_RED` y `CUADRO9_PUBLICADO_2023` de `src/population/ecp.py`, con un test que compara contra el cuadro publicado.

**Advertencias:** `P2047` está topeada en 10; 2021 está contaminado por la pandemia (la pregunta es sobre visitas); y la pregunta mide lazos fuertes de sociabilidad doméstica, no influencia política. Detalle en `NETWORK SPECIFICATION.md` §2.1 y §4.1.

### 10.8 La serie se puede casi duplicar — y qué años no

El Experimento 5 dejó claro que el límite ya no es el modelo sino el poder estadístico: **tres transiciones** (2017→2019→2021→2023) no permiten discriminar entre familias de modelos. Lo más barato que existe para arreglarlo es bajar las olas anteriores de la misma encuesta.

**La v0.9 de este documento dijo que 2013 y 2015 eran apilables "sin armonizar nada". Era correcto sobre los metadatos y falso sobre los datos.** Los catálogos de los dos años declaran las mismas variables `P5263S1`…`S15`, la misma pregunta y la misma escala — y eso se verificó. Lo que no se podía ver ahí es **qué institución hay detrás de cada código**, porque los 15 ítems comparten una sola etiqueta genérica (§10.4). Al cargar los datos, 2015 se cayó.

Queda anotado en vez de corregido en silencio, que es la regla de este documento, y con una consecuencia práctica: *verificar metadatos no es verificar comparabilidad.*

Verificado ahora contra los metadatos **y contra los datos**:

| Año | Catálogo DANE | Variables de confianza | Escala | ¿Apilable? |
|---|---|---|---|---|
| 2013 | **283** | `P5263S1`…`S15` | 1–5, *"1 significa que no confía y 5 que confía mucho"* | ✅ **sí** — pasa las tres anclas |
| 2015 | **406** | `P5263S1`…`S15` | idéntica | ❌ **no** — los códigos apuntan a otras instituciones |
| 2017 / 2019 / 2021 / 2023 | 515 / 644 / 730 / 822 | `P5263S1`…`S15` | idéntica | ✅ ya en disco |
| 2011 | (IHSN 5289) | **`I46_A`…`I46_S` — 19 instituciones** | sin verificar | ❌ **no**, requiere crosswalk 19→15 |
| 2008 | 104 | `E35A_EPP`… | otro formato | ❌ no |
| 2007 | 106 | sin verificar | — | ❌ no |

**Por qué 2015 se cae (DI-C10).** Tres señales, todas en la misma dirección:

| Señal | 2013 · 2017 · 2019 · 2021 · 2023 | **2015** |
|---|---|---|
| `S4` (Congreso) / `S6` (Asamblea departamental) | S4 poblado · **S6 vacío** (Bogotá no tiene Asamblea) | **S4 vacío · S6 poblado** — exactamente al revés |
| Ítem más desconfiado | `S10` (Partidos políticos), en los cinco años | **`S2`** (1,99) |
| Ítem más confiado | `S3` o `S14` (Fuerzas Militares / Registraduría) | **`S9`** (3,20) |

Un año donde Bogotá "sí tiene Asamblea departamental" y donde la Policía pasa de media tabla (2,27–2,44) a ser lo más confiado de todo es un año donde el código dejó de apuntar a la misma institución. Apilarlo produciría una serie cuyos saltos serían cambios de cuestionario.

**La frontera real del instrumento**: 2013 sí, 2015 no, 2017 en adelante sí. No es una frontera temporal limpia — es una ola suelta con los códigos corridos.

**Qué se gana igual:** con 2013 la serie pasa de 4 olas / 3 transiciones a **5 olas / 4 transiciones**. Menos de lo que prometía la v0.9, pero real.

**Y aparece algo que con cuatro puntos no se veía:**

| Año | media | sd |
|---|---|---|
| 2013 | **2,808** | **0,754** |
| 2017 | 2,503 | 0,934 |
| 2019 | 2,362 | 0,903 |
| 2021 | 2,245 | 0,897 |
| 2023 | 2,430 | 0,764 |

La media cae de forma monótona 2013→2021 y rebota en 2023. Pero la **dispersión hace una joroba**: se expande de 0,754 a 0,934 entre 2013 y 2017, y vuelve a 0,764 en 2023 — casi exactamente donde empezó. Los Experimentos 4 y 5 arrancaban en 2017, o sea **en la cima de la joroba**, y estaban ajustando la bajada tratándola como si fuera todo el fenómeno. Ningún modelo que solo contraiga puede producir la subida. Hay que rehacerlos desde 2013.

**Ojo con el espaciado:** la serie queda 2013 · 2017 · 2019 · 2021 · 2023, con saltos de 4, 2, 2 y 2 años. Los pasos por periodo tienen que ser proporcionales al tiempo real, no iguales.

Verificado además que 2015 trae en `Tabla viviendas` las tres columnas de las que depende el cargador: **`FEX_P`** (ponderador), **`DIRECTORIO`** (clave) y **`REGION`** (Bogotá = 1), más `P4031S1A1` (estrato). Y que 2013 tiene los mismos seis módulos, con `Democracia` y `Características Generales` separados. **El cargador no necesita cambios**: resuelve módulos por nombre normalizado.

**Qué se gana:** la serie pasa de 4 olas / 3 transiciones a **6 olas / 5 transiciones**, un 67 % más de puntos de comparación, sin ningún riesgo de armonización.

**Qué hacer:**

```
https://microdatos.dane.gov.co/index.php/catalog/283/get-microdata   # ECP 2013
https://microdatos.dane.gov.co/index.php/catalog/406/get-microdata   # ECP 2015
```

Ya descargadas. 2015 se conserva en disco: `anios_en_disco()` la detecta, avisa por qué no se apila y **no la devuelve**, así que no hay que borrarla ni recordar excluirla.

**DI-C9 — las claves de merge también cambian.** En 2013 las dos últimas claves de persona se llaman `V3` y `V4` en vez de `HOGAR_NUMERO` y `PERSONA_NUMERO` (nombres genéricos de export antiguo, sin etiqueta). El cargador las renombra al nombre canónico **y verifica** que la tupla identifique a cada persona una sola vez: si el alias elegido no fuera la variable que se cree, el merge duplicaría filas en silencio.

**DI-C10 — la prueba de anclas.** `verificar_anclas()` comprueba, año por año: que `S6` y `S12` estén vacíos, que el mínimo sea `S10` y que el máximo esté entre `S3` y `S14`. Hay un test que lo exige para todos los años en disco. Es barato y es lo único que detecta un corrimiento de códigos, porque el DDI no puede.

**DI-C8 — la lista de años dejó de estar escrita a mano.** `ecp.py` tenía la tupla `(2017, 2019, 2021, 2023)` como constante, y habría que acordarse de editarla al bajar una ola. Ahora `anios_en_disco()` mira el disco, y avisa —sin fallar— si encuentra carpetas de años cuyo instrumento es otro. Es el mismo modo de fallo que la nota de la v0.6 de este documento registra en sentido contrario: una lista escrita a mano que afirmaba algo que el disco desmentía.

---

## 13. Bogotá Cómo Vamos — Encuesta de Percepción Ciudadana 2025

### 13.1 Qué trae

El paquete `Empaquetado-Web` tiene tres archivos: el microdato en SPSS (`Microdatos`, sin extensión pero es un `.sav`), `Tablas.xlsx` —cuya hoja `Base` es el **mismo microdato en Excel**, que es la vía cómoda para leerlo— y el cuestionario en `.docx`.

| | |
|---|---|
| n | **1.520** |
| Variables | 162 |
| Localidades | **18 de 20** (faltan La Candelaria y Sumapaz) |
| n por localidad | mín 32 · mediana 67 · máx 175 (Suba) |
| Ponderador | `FACTOR1` **está en el archivo pero vale 1,0 en todos los casos** — *resuelto en §13.6: era un defecto de este empaquetado; el archivo de 2025 de la entrega completa trae pesos reales* |

### 13.2 Sí hay batería de confianza institucional — pero NO es anual

> **Corrección de la v0.12 (17/09/2026).** El subtítulo original de esta sección decía "y es anual". **Es falso**, y la evidencia está en §13.6: la batería `CON_4`…`CON_7` existe solo en **2024 y 2025**. La marca `PRIORITARIA | ANUAL` del formulario describe la intención del instrumento, no la historia del levantamiento. Se conserva el texto original abajo, sin editar, porque la conclusión que se sacó de él —pedir las olas anteriores— fue la correcta y produjo la entrega de §13.6.

Buscar "confianza" en las etiquetas de variable no la encuentra: las cuatro variables se llaman solo `CON_4`…`CON_7` y su etiqueta es el nombre de la entidad. La pregunta madre está en el cuestionario:

> *"De 1 a 5, donde 1 es «no confío nada» y 5 «confío plenamente», ¿qué tanto confía estas instituciones democráticas?"*

Y cada ítem viene marcado en el formulario como **`PRIORITARIA | ANUAL`**, o sea que es instrumento permanente, no una pregunta de coyuntura de 2025.

Los cuatro ítems **mapean uno a uno contra la ECP**:

| BCV 2025 | ECP | BCV 2025 (media) | ECP 2023 (media) | dif |
|---|---|---|---|---|
| `CON_4` Alcaldía | `S2` Alcaldía Municipal/Distrital | 2,472 | 2,537 | −0,065 |
| `CON_5` Concejo local | `S8` Concejos municipales/distritales | 2,340 | 2,340 | **0,000** |
| `CON_6` Congreso de la República | `S4` Congreso de la República | 2,123 | 2,035 | +0,088 |
| `CON_7` Gobierno Nacional (presidencia) | `S15` Presidencia de la República | 2,303 | 2,308 | −0,005 |

**Las cuatro coinciden dentro de 0,09 puntos**, pese a ser encuestas distintas, casas de campo distintas, dos años de diferencia y anclas verbales de la escala redactadas distinto (la ECP dice "no confía / confía mucho"; BCV usa cinco etiquetas nombradas). Es la primera **validación externa de la medición** que tiene el proyecto: hasta ahora toda la serie venía de una sola fuente y no había con qué contrastarla.

*Cautela antes de celebrarlo:* la comparación es entre una media **ponderada** (ECP) y una **sin ponderar** (BCV, porque `FACTOR1` ≡ 1). Que aun así coincidan a dos decimales es buena señal, pero antes de usarlo como validación formal hay que construir el ponderador de BCV con los totales poblacionales de la hoja `Demosgraficos` y repetirla.

### 13.3 Qué aporta que no teníamos, y qué no

**Aporta dos cosas nuevas:**

1. **Opinión con localidad identificada.** La ECP solo llega a "Bogotá" como región (§10.5). Este es el primer microdato de confianza institucional con localidad que entra al proyecto. Con n mediano de 67 por localidad y sin ponderador, no alcanza para estimaciones por localidad publicables — y la evidencia del CNC (§12.3) dice que ahí no hay casi nada que encontrar — pero sirve como chequeo independiente de esa conclusión con la variable de opinión que sí es la del proyecto.
2. **Un punto en 2025**, dos años después del final de la serie ECP.

**No aporta** lo que fuimos a buscar: **es una sola ola**. Sigue habiendo cuatro transiciones. Un solo punto extra, medido con otro instrumento y sin ponderar, no se apila a la serie ECP sin un trabajo de armonización que hoy no se justifica.

### 13.4 Qué pedir

Que el paquete traiga los ítems marcados `ANUAL` significa que **las olas anteriores deberían tener las mismas cuatro variables**. Eso es lo que hay que pedir a Bogotá Cómo Vamos:

> El `Empaquetado Web` (microdato + tablas + formulario) de las ediciones anteriores de la Encuesta de Percepción Ciudadana, y la documentación del diseño muestral y del factor de expansión.

Con cinco o seis olas anuales de `CON_4`…`CON_7` **con ponderador**, el proyecto pasaría de 4 transiciones bienales a una decena de transiciones anuales — que es exactamente lo que `claude/EXPERIMENT_6_RESULTS.md` §6 identifica como la única vía que cambiaría el poder de las comparaciones entre modelos.

### 13.5 Los informes anuales en PDF no reemplazan al paquete

Revisado el de 2024 (126 páginas). **No sirve como objetivo de los experimentos**, por tres razones que conviene no volver a chequear:

1. **Publica una sola categoría colapsada, no la distribución.** La batería aparece como *"% Confía mucho"*: Alcaldía 12,3 % · Gobierno Nacional 11,7 % · Concejo 7,1 % · Congreso 4,7 %. Los Experimentos 4 a 6 comparan distribuciones completas (W1); de una proporción de la categoría superior no se recupera ni la media ni la forma.
2. **No se puede decodificar qué categoría es.** Contra el microdato 2025: el informe da 12,3 % para Alcaldía, y el microdato da **2,9 %** en "Confío plenamente" (=5) y **20,0 %** en 4+5. No coincide con ninguna, y la razón entre informe y 4+5 tampoco es constante entre instituciones (0,62 · 0,63 · 0,53 · 0,53). Puede ser ponderación, cambio real 2024→2025 o un colapso distinto: sin el microdato del mismo año no se distingue. **Pegar cifras de informes a la escala del microdato no es seguro.**
3. **La batería de confianza no tiene serie publicada** en el informe — solo el corte de 2024. Lo que sí tiene serie larga (2008–2024, 15 puntos) es otro indicador: *"% Buena"* sobre la **gestión** del Concejo y del Alcalde. Es un indicador vecino, no el mismo, y también viene colapsado a una categoría.

**Lo que sí aporta el informe, y es útil:** la ficha técnica. n = 1.521, muestreo **probabilístico multietápico estratificado de conglomerados**, margen de error 2,6 %, campo presencial. Es decir, **el diseño sí es complejo y por tanto el ponderador existe** — el `FACTOR1 ≡ 1,0` del paquete es una omisión del empaquetado, no un diseño sin pesos. Hay que pedirlo explícitamente.

**Dos pistas concretas que deja el informe:**

- Hay un **tablero interactivo** (diapositiva 6) con resultados agregados **2014–2024** por módulo e indicador, incluidos los módulos "Alcalde y Concejo" y "Entidades", con desagregación por año. Vale la pena mirar si expone el desglose por las cinco categorías o permite descargar los datos: sería el camino más barato a una serie anual.
- Los años 2020 y 2021 **no tienen dato** ("no se presentan datos por su recolección no presencial"), así que cualquier serie anual de BCV tendrá ese hueco.

### 13.6 La entrega completa, 2014-2025 *(17/09/2026)*

Bogotá Cómo Vamos entregó el empaquetado de **todas** las ediciones: microdatos en `.dta`, formularios, tablas de salida y un diccionario maestro, la **"EPC Suprema"**, que mapea cada variable al nombre que tuvo en cada año (los códigos cambian todos los años). En `data/raw/bogota_como_vamos/empaquetado_2026-09/`.

| | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|
| n | 1.502 | 1.712 | 1.502 | 1.506 | 1.500 | 1.521 | 1.500 | 1.501 | 1.521 | 1.520 |
| factor | `PON` | `FEXP` | `PON` | `PON` | `PON` | `PONDERA` | `PONDERA` | `FEXP` | `PONDERADOR` | `Factor1` |
| suma | n | n | n | n | n | n | 6,15 M | 6,21 M | 6,29 M | 6,33 M |

No hay 2020 ni 2021. **Los diez factores existen y ninguno es constante**: el `FACTOR1 ≡ 1,0` de §13.1 era un defecto de aquel empaquetado web, no de la encuesta. 2014-2019 traen el factor normalizado a la muestra y 2022-2025 expandido a población; para medias ponderadas da lo mismo.

**Aviso sobre 2022:** su `PONDERA` toma solo **10 valores distintos**, contra 60-527 en los demás años. Posestratificación mucho más gruesa; cualquier cifra de 2022 merece más desconfianza que la de sus vecinos.

#### Lo que NO hay

La batería de confianza (`MICC5`-`MICC8`) aparece **solo en 2024 y 2025**, y ni entre esas dos es directamente comparable: 2024 está en escala 1-4 sin código de no respuesta, 2025 en 1-5 con `90`. La hoja `VALORES` del diccionario las describe con tres niveles — esa es la recodificación del tablero, **no** la escala del microdato.

#### Lo que sí hay, y es más de lo que se fue a buscar

Dos ítems de evaluación institucional en escala 1-5, con la dirección enunciada en la propia pregunta (*"1 muy mala gestión y 5 muy buena gestión"*), **nueve olas cada uno**:

| Ítem | media, primera → última ola | rango |
|---|---|---|
| `GG3` gestión del alcalde/sa | 2,845 → 2,753 | 2,105 – 3,180 |
| `CC5` gestión del Concejo | 2,635 → 2,564 | 2,234 – 2,670 |

Y como los contesta la misma persona en el mismo cuestionario, existe la **diferencia individual** \(d_i = GG3_i - CC5_i\) (escala −4 a +4, 8 olas), que elimina el estilo de respuesta individual además de cualquier efecto aditivo de periodo.

**Verificado contra las tablas de salida publicadas por la propia BCV** (`verificar_anclas_bcv()`): 2023, gestión del Concejo, 42,9 % en 1-2 en el microdato contra 44,1 % publicado.

#### La inversión de códigos — hay que reportarla a BCV

Los ítems de imagen (`GP1_*`, `GG1`) tienen los códigos **1 y 2 invertidos entre 2014-2023 y 2024**, contra lo que dicen el formulario **y** el diccionario. CADEs, proporción en el código 1: 72 · 72 · 73 · 71 · 74 · 74 · 65 · 62 · **23** %.

Tres verificaciones concordantes: la tabla publicada por BCV para 2023 da Favorable 64,8 % donde el microdato tiene 62 % en el código 1; lo mismo con `GG1`; y la correlación con `GG3` pasa de −0,16 a **+0,19** exactamente en 2024, conservando la magnitud.

`src/population/epc_bcv.py` **bloquea** esos ítems con una excepción que explica la inversión (DI-B2). Quien arme la serie de imagen siguiendo el diccionario publica un salto de 45 puntos que no ocurrió.

> **Es la segunda vez que el diccionario de una fuente miente sobre sus propios códigos.** La primera fue la ECP 2015 (§10.8). La regla queda: **ningún diccionario se acepta sin contrastarlo contra una cifra publicada o contra la estructura de los datos.**

#### Dos advertencias antes de usar la serie

1. **La cobertura cae en escalón**, de ~95 % (2014-2019) a ~81 % (2022-2025), sin explicación identificada — no es cambio de formulario ni filtro. Tres de las ocho transiciones de `GG3` no son robustas a la no respuesta. Ver `claude/ANALISIS_NORESPUESTA_EPC.md`.
2. **`CC5` no es un control independiente**: correlaciona +0,62 en cambios con `GG3`, y en 2017→2019 los dos suben exactamente lo mismo (+0,439 y +0,436) mientras la ECP bajaba. En la diferencia individual ese salto conjunto se evapora (−0,001), que es justo lo que uno esperaría de un componente común.

#### Constructo

La serie larga es de **gestión**, no de **confianza**. Otro constructo sobre la misma escala y sobre instituciones que se solapan; en los años comparables **se mueven en direcciones opuestas**. Es la decisión abierta A20 de `PROJECT_CONTEXT.md`.

**Cargador:** `src/population/epc_bcv.py`, 17 pruebas en `tests/test_epc_bcv.py`. Análisis completo en `claude/ANALISIS_EPC_BCV.md`.

### 13.7 Lo que respondió BCV, y qué queda establecido *(18/09/2026)*

Se les consultó por la inversión de códigos, por el identificador de conglomerado y por la batería de confianza. La respuesta confirma unas cosas, corrige otras y explica una que veníamos tratando como anomalía.

#### Confirmado por la fuente

**La batería de confianza es genuinamente nueva.** El formulario de la EPC cambió hace poco para toda la Red de Ciudades Cómo Vamos, y esas preguntas entraron con ese cambio. La marca `PRIORITARIA | ANUAL` significa *de aquí en adelante se hará todos los años*, no *se ha hecho todos los años*. Nuestra inferencia de §13.6 era correcta y ahora está confirmada en la fuente.

**El cambio de escala 2024→2025 lo tienen identificado.** De una Likert 1-4 a 1-5 más el código 90. Tanto que su propio tablero público **no incluye 2024** por comparabilidad, solo 2025.

**La inversión de códigos la aceptan.** Y dan la explicación de procedencia: una encuesta de tantos años, con mucha rotación del equipo técnico, acumula huecos de documentación.

> **Alerta que hay que darles:** proponen arreglarlo *invirtiendo los valores en la EPC Suprema*. Eso arreglaría 2014-2023 y **rompería 2024**, que ya está bien. El arreglo tiene que ser por año.

#### Corregido, y el error era nuestro

**Son seis olas con identificador de conglomerado, no cuatro.** 2015 y 2018 también traen `MANZANA`. No las revisamos: el escaneo original cubrió una muestra de años. Ver `claude/ANALISIS_DISENO_MUESTRAL.md` §2.

#### Explicado: por qué la serie es tan irregular

**La firma que levanta la encuesta cambia casi todos los años**, y el equipo técnico ha rotado varias veces. En algunos años el identificador de conglomerado quedó fuera de la base por negociación con la firma, o simplemente no se agregó, y no hay documentación del diseño para reconstruirlo.

Eso deja de ser una anomalía y pasa a ser una **propiedad estructural de la fuente**: los cambios de código entre años, las escalas que se mueven, los ponderadores de granularidad distinta y los identificadores que aparecen y desaparecen tienen todos el mismo origen. Es la razón por la cual la EPC Suprema existe, y también por la cual hay que verificar cada ola contra los datos y no contra el diccionario.

#### Descartado: los proxies de conglomerado

BCV propuso `LOCALIDAD + GRUPO_ESTRATOS` para 2016, `LOCALIDAD_COMUNA + NSE` para 2017 y `Zona + SEG_1` para 2025, señalando con honestidad que eran hipótesis sin documentación. **Se validaron en las seis olas donde sí hay manzana y no sirven**: inflan el efecto de diseño por un factor mediano de 1,94. Son mucho más plausiblemente la estratificación que la conglomeración. Detalle en `claude/ANALISIS_DISENO_MUESTRAL.md` §4.bis.

#### Dos ofrecimientos, sin usar todavía

- **Microdatos anteriores a 2014, hasta 1998, en xlsx.** Con la advertencia del propio BCV de que "esos datos ni los tocamos". Más n a cambio de mucha verificación.
- **La Encuesta de Percepción Distrital de la Secretaría Distrital de Planeación**, edición del año pasado: <https://www.sdp.gov.co/gestion-estudios-estrategicos/informacion-estadisticas/encuesta-distrital-percepcion>. No estaba en el inventario del proyecto.

#### Y una pregunta que nos devuelven

BCV pregunta si, con el n que manejamos, podemos estimar la hipótesis de **capital social**: que la confianza interpersonal (vecinos, amigos, familia) se asocia con la confianza institucional, la percepción de corrupción y la participación. Ellos corrieron correlaciones de Pearson y no les resultó concluyente; lo atribuyen a un n bajo.

**El proyecto tiene con qué responderla**, y probablemente mejor: la ECP trae `P2025S1`…`S6` —confianza interpersonal en seis objetos— en el **mismo cuestionario** que la batería institucional, unibles a nivel de persona (§10.7). Son 43.000-46.000 casos nacionales por ola, ~4.200 en Bogotá, en 2019, 2021 y 2023. La medición preliminar de `claude/ANALISIS_HOMOFILIA.md` ya da **r ≈ +0,25**. Queda como decisión abierta A21 en `PROJECT_CONTEXT.md`.

### 13.8 Inventario por pregunta, para la reestructuración de D17 *(30/09/2026)*

`src/population/inventario_epc.py` contrasta el diccionario (EPC Suprema, hoja
`VARIABLES`) con los diez microdatos, pregunta por pregunta y año por año. Salida en
`data/processed/epc_inventario/` (`items.csv`: pregunta × año; `resumen.csv`: una fila
por pregunta, con su texto, módulo, años y personas por localidad). Solo metadatos y
conteos: ningún microdato.

**Qué hay.** 295 preguntas (sin los filtros): 272 de respuesta única y 23 de respuesta
múltiple. Cuántos años tiene cada una de respuesta única:

| Olas con datos | 10 | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 1 |
|---|---|---|---|---|---|---|---|---|---|---|
| Preguntas | 26 | 20 | 7 | 7 | 8 | 12 | 14 | 10 | 18 | 150 |

- **Las 150 de una sola ola son casi todas de 2024** (108), y de esas, la mayoría son del
  módulo de **Educación** (104 preguntas, casi todas solo en 2024): satisfacción de
  padres con cada servicio escolar, respondidas por una submuestra (mediana de 9
  personas por localidad). No sirven para el mapa.
- **Preguntas que responde al menos el 80 % de la muestra**, por año: 59 a 70 entre
  2014 y 2019, 86 en 2022, 114 en 2023, 92 en 2024 y 62 en 2025. Esas tienen **mediana
  de 67 a 81 personas por localidad**, en 19 localidades (18 en 2025; nunca Sumapaz).
- **Las 26 de las diez olas** son el núcleo de opinión urbana: satisfacción con Bogotá,
  orgullo, optimismo, seguridad en el barrio y en la ciudad, victimización,
  corrupción, calidad del aire, ruido, agua, satisfacción con el transporte, con la
  salud, con cada servicio público, situación económica del hogar, pobreza, hambre,
  oferta cultural y recreativa. Les siguen, con nueve olas, la gestión del alcalde
  (`GG3`) y del Concejo, el manejo de basuras y escombros, los árboles y la batería de
  respeto hacia grupos (mayores, mujeres, diversidad sexual y étnica, desplazados,
  reinsertados).

**Por módulo** (respuesta única): Movilidad 16 preguntas (12 con cinco olas o más),
Participación Ciudadana 22 (18), Medio Ambiente 7 (7), Servicios Públicos 6 (6),
Seguridad 6 (5), Clima económico 5 (5), Gestión Global 4 (4), Gestión Pública 33 (8),
Confianza 8 (0: solo 2024-2025) y Estado Abierto 7 (0).

**Lo que el diccionario dice y el archivo no tiene: 93 casos pregunta × año**, repartidos
en todos los años (5 a 14 por ola), sobre todo en Participación Ciudadana (23) y
Cultura (18). Es la regla de §13.6 otra vez: el diccionario no basta. Esos casos no
entran al catálogo hasta revisarlos uno por uno.

**Tres advertencias para el catálogo:**
1. **`GG1` y los `GP1_*` (imagen) tienen códigos invertidos** entre 2014-2023 y 2024
   (§13.6, DI-B2). El inventario los cuenta porque existen; no se usan hasta
   recodificarlos por año.
2. **Las escalas cambian entre años** (confianza: 1-4 en 2024, 1-5 en 2025) y los
   códigos de no respuesta también. El inventario cuenta como válido 1-10 (DI-IN2),
   que es una cota: cada pregunta que entre al catálogo necesita su escala verificada.
3. **Con 60-80 personas por localidad, el mapa de una sola ola es ruidoso.** Es lo que
   ya se midió en el paso 0b de A08 (hay territorio en 7 de 9 olas, pero con márgenes
   anchos). La página tendrá que mostrar el margen de cada localidad.

**Lo que implica para D17.** Una población construida con la ola de 2023 (114
preguntas generales, 80 personas por localidad) o de 2024 (92) lleva a cada agente con
casi cien respuestas reales: material de sobra para el puente. Las 26 preguntas de las
diez olas son las candidatas naturales para la validación con respuesta conocida.

### 13.9 Juntar olas para el mapa: 2022-2024 *(30/09/2026)*

`src/population/armonizar_epc.py` compara cada pregunta del catálogo de 2023 con la misma
pregunta en 2022, 2024 y 2025 (código, etiquetas de valor normalizadas y códigos presentes
en los datos) y mide cuánto mejora la confiabilidad de las medias por localidad al juntarlas.
Salida en `data/processed/epc_armonizado/` (solo metadatos y confiabilidades).

**Qué se puede juntar.** De las 102 preguntas del catálogo: ~~48 en tres olas~~ **45 en tres olas** (2022, 2023 y
2024), ~~26~~ 29 en dos y 28 solo en 2023. *(Corrección 30/09: el texto decía 48 y 26; `resumen.json`
siempre dijo 45 y 29. La diferencia son las tres evaluaciones del gobierno de turno, DI-AR5.)* Lo que deja fuera cada año:
- 2022: 28 no están en el archivo, 7 tienen otras etiquetas, 1 otra escala (1-6).
- 2024: 33 no están, 13 tienen otras etiquetas.
- **2025: ninguna.** Sus variables no traen etiquetas ni textos, así que no hay cómo verificar
  en el archivo que la escala sea la misma, y BCV dijo que el formulario cambió (§13.7). Queda
  fuera hasta verificarlo contra `EPC2025_Formulario.pdf`. *Corrección antes del primer
  commit:* una primera versión aceptaba 2025 comparando el texto del diccionario, que es uno
  solo para todos los años: esa comprobación no verificaba nada.
- **Las evaluaciones del gobierno de turno solo se juntan dentro de la misma administración**
  (DI-AR5): la gestión del alcalde, la del Concejo y la inversión de recursos públicos juntan
  2022 y 2023 (Claudia López), no 2024 (Carlos Fernando Galán).

**Cuánto mejora** (74 preguntas con dos olas o más; mediana):

| | Solo 2023 | 2022-2024 juntas |
|---|---|---|
| Personas por localidad | ~80 | **~250** |
| Confiabilidad de las medias por localidad (dos mitades) | 0,19 | **0,37** |
| La misma, para la muestra completa (Spearman-Brown) | 0,32 | **0,54** |

La confiabilidad **casi se duplica**, pero no es uniforme: 28 preguntas quedan en 0,6 o más
(seguridad en el barrio 0,82, hambre 0,82, bancas y canecas 0,81, internet 0,80), 22 entre
0,4 y 0,6, y 24 por debajo de 0,4 (el ruido y la corrupción siguen sin geografía medible,
incluso juntando años).

**Qué cambia al juntar:** la población dejaría de ser «Bogotá en 2023» y sería «Bogotá
2022-2024»; si algo cambió entre esos años, el mapa lo promedia.

---

## 11. Marginal territorial — estado real

### 11.1 Qué hay y cómo se reproduce

`data/raw/anexo-proyecciones-poblacion-bogota-desagreacion-loc-2018-2035-UPZ-2018-2024.xlsx` (2,7 MB) es el anexo oficial de DANE, publicado el 4 de noviembre de 2021 sobre base Censo 2018. Hoja `Localidades`: 1.080 filas × 310 columnas, años 2018–2035, edades simples 0–100+ por sexo, y tres valores de `AREA` (Cabecera Municipal / Centros Poblados y Rural Disperso / **Total**).

El marginal se deriva con:

```
python src/population/extraer_columnas_em2021.py proyecciones
```

Dos detalles que importan y están en el código:

- `AREA = "Total"` y no `"Cabecera Municipal"`: Sumapaz es casi enteramente rural y con cabecera quedaría en cero.
- Crosswalk de nombres: el anexo escribe "Ciudad Bolivar" sin tilde y el receptor usa "Ciudad Bolívar". Sin normalizar, el marginal no cruza y el error aparecería recién al ponderar, como localidades con peso 0.

### 11.2 Qué tan bien lo replica la población sintética

Diagnóstico de `poblacion_sintetica_v2.csv` (1.000 agentes, muestreo PPS de D14) contra el marginal derivado del anexo de 2021:

| Localidad | Esperado | Observado | Sesgo | | Localidad | Esperado | Observado | Sesgo |
|---|---|---|---|---|---|---|---|---|
| Suba | 168,2 | 158 | 0,94 | | Puente Aranda | 33,3 | 43 | 1,29 |
| Kennedy | 131,1 | 143 | 1,09 | | Chapinero | 24,0 | 21 | 0,88 |
| Engativá | 106,6 | 109 | 1,02 | | Teusaquillo | 22,0 | 19 | 0,86 |
| Bosa | 87,3 | 78 | 0,89 | | Tunjuelito | 22,0 | 22 | 1,00 |
| Usaquén | 77,3 | 77 | 1,00 | | Barrios Unidos | 20,5 | 18 | 0,88 |
| Ciudad Bolívar | 76,4 | 74 | 0,97 | | Santa Fe | 12,7 | 15 | 1,18 |
| Fontibón | 52,4 | 48 | 0,92 | | Los Mártires | 10,3 | 8 | 0,78 |
| San Cristóbal | 48,2 | 51 | 1,06 | | Antonio Nariño | 10,2 | **17** | **1,67** |
| Usme | 47,5 | 52 | 1,09 | | La Candelaria | 2,5 | 3 | 1,20 |
| Rafael Uribe Uribe | 47,0 | 44 | 0,94 | | Sumapaz | 0,4 | **0** | **0,00** |

Distancia agregada 0,041, contra 0,172 antes de D14. Las quince localidades grandes quedan entre 0,86 y 1,09. Los dos casos fuera de rango son de muestra chica y esperables con n = 1.000: **Antonio Nariño** (17 donde tocaban 10) y **Sumapaz**, que con 0,4 agentes esperados no puede salir bien — o sale 0 o sale 1, y ninguna de las dos es 0,4. Sumapaz es además la única localidad mayoritariamente rural, así que su ausencia sesga el generador territorial en la dirección de una Bogotá enteramente urbana. Con n = 10.000 ambos se resuelven solos.

### 11.3 La revisión de 2025 — adoptada

El anexo original es la proyección **hecha en 2021** para el año 2025. La revisión posterior — *"Proyecciones de población, localidad y Bogotá, UPL 2005-2035. Contrato Interadministrativo 500 de 2025 — DANE, SDP y Región Metropolitana Bogotá Cundinamarca, agosto de 2025"* — está descargada y es la fuente vigente.

Esquema: `ANO;CODIGO_LOCALIDAD;NOMBRE_LOCALIDAD;SEXO;EDAD;CURSODEVIDA;GRUPOEDAD;POBLACION`, separador `;`, edades simples, años 2005–2035, y una fila agregada con `CODIGO_LOCALIDAD = 0` (Bogotá) que **hay que excluir para no contar doble**.

`extraer_columnas_em2021.py proyecciones` ahora **prefiere la revisión de 2025** cuando está presente y cae al anexo de 2021 si no. Avisa cuando el marginal regenerado se mueve más de L1 = 0,01 respecto del anterior — y se movió:

| | 18+ en Bogotá | Distancia L1 al marginal anterior | Ajuste de la población v2 |
|---|---|---|---|
| Anexo 2021 (proyección) | 6.386.051 | — | TVD 0,041 |
| **Revisión 2025** | **6.201.042** (−2,9 %) | **0,0371** | **TVD 0,032** |

La revisión incorpora el post-COVID y los cambios migratorios que la proyección de 2021 no podía ver. Que la población sintética ajuste **mejor** contra el marginal revisado sin haber sido reajustada es una señal a favor de la revisión, no del muestreo.

Archivo: [`osb_demografia-poblacion-localidad.csv`](https://datosabiertos.bogota.gov.co/dataset/85bf790d-84d1-4eda-bd6f-40af62e71d95/resource/37e58cb3-c870-4608-8c37-ce45db0eb7c1/download/osb_demografia-poblacion-localidad.csv), del conjunto [Población en Bogotá D.C. 2005-2035](https://datosabiertos.bogota.gov.co/dataset/piramide-poblacional-bogota-d-c).

---

## 12. Estudios del CNC — la fuente que no entra al repositorio

El CNC entregó cuatro encuestas con microdato. Cierran A02 de PROJECT_CONTEXT.md, aunque no de la forma esperada.

### 12.1 Qué son

| Estudio | Año | n | Cobertura | Localidades |
|---|---|---|---|---|
| **Salud Mental Bogotá** (UNODC) | 2023 | 15.151 | Bogotá | 20 |
| **Sustancias Psicoactivas Bogotá** (PNUD/SDS) | 2022 | 10.912 | Bogotá | 20 |
| Apropiación Digital Colombia (CNC) | 2024 | 3.614 | nacional | — |
| SABE Colombia | 2015 | 23.877 | nacional | — |

**Ninguno mide confianza institucional**, así que no reemplazan al donante de D11 ni a la ECP como serie de validación. Y **no hay panel**: son cuatro cortes transversales de temas distintos, sin una pregunta repetida entre olas. **A02 se cierra con un "sí, pero no sirve para lo que se esperaba de él."**

Lo que sí tienen, y no tenía ninguna otra fuente: **muestras grandes de Bogotá con las 20 localidades y diseño muestral complejo documentado**. Eso permitió hacerle al eje territorial la misma pregunta que se le había hecho a la demografía.

### 12.2 Lo único que sale de ahí: agregados

`src/population/cnc_agregar.py` corre **en el equipo de Daniel**, lee los `.sav` con las columnas estrictamente necesarias (21 de 696 en salud mental; 34 de 645 en sustancias) y escribe a `data/external/cnc/` solo:

- `<estudio>_localidad.csv` — proporciones por localidad con error estándar de diseño, IC 95 %, n y DEFF
- `<estudio>_varianza.csv` — descomposición de varianza cruda y estandarizada por composición
- `<estudio>_composicion.csv` — composición demográfica por localidad
- `<estudio>_meta.json` — parámetros de la corrida

Supresión: estimaciones con **n < 30** y celdas de estandarización con **n < 25** no se escriben. La estandarización usa una escalera de celdas (de `sexo × edad × educación × estrato6` hasta `edad` sola) que baja de nivel cuando la cobertura cae por debajo del 60 %, porque con ~300 personas por localidad las celdas finas quedan casi todas vacías.

**Ningún registro individual, ninguna coordenada, ningún nombre ha salido ni puede salir de ese equipo por esta vía.**

**Dónde está la carpeta (DI-N7).** Desde el 16/09/2026 los estudios viven **fuera del repositorio** y su ruta **no está escrita en el código**. El script la resuelve, en este orden: el argumento `--cnc <ruta>`, la variable de entorno `BSS_CNC_DIR`, y por último la ubicación heredada dentro de `data/raw/` — que se conserva solo para no romper un equipo que todavía la tenga ahí, y que hace que el script avise en pantalla si la encuentra dentro del repositorio.

```
python src/population/cnc_agregar.py --cnc "<ruta fuera del repo>" salud_mental
setx BSS_CNC_DIR "<ruta fuera del repo>"     # de una vez por todas, en Windows
```

### 12.3 El resultado: la localidad no estructura la opinión

Sobre **42 ítems de opinión**, cuatro baterías, dos estudios, dos años:

- La localidad explica entre **0,4 % y 2,6 %** de la varianza, mediana **~1 %**.
- Estandarizar por composición **casi no lo mueve**: lo poco que hay tampoco es composicional.
- Y **54 % (salud mental) / 63 % (sustancias) de esa varianza aparente es error de muestreo**. La desviación *real* entre localidades es **0,073 y 0,046** puntos de escala, contra ~1,05 dentro de cada localidad — entre el 5 % y el 7 %.

Los ítems con más señal territorial son los de percepción de riesgo de la marihuana (`T29_9`, `T29_10`, `T29_11`: 1,6–2,0 %, solo ~20 % de ruido). Tiene sentido: la exposición varía por territorio. Aun ahí la sd real es 0,16 sobre una escala de 1 a 4.

*Nota metodológica que refuerza el resultado:* en salud mental el estrato de diseño es el socioeconómico, así que al estimar **dentro** de una localidad quedan estratos con un solo conglomerado, que `svy_prop` omite. Eso **subestima** la varianza — el porcentaje de ruido real es todavía mayor. DEFF mediano 2,5, con máximos de 45–53 en los ítems más raros.

Consecuencias registradas en `claude/ANALISIS_HOMOFILIA.md` §8 y en `NETWORK SPECIFICATION.md` §5.1: el generador territorial no tiene objetivo empírico que reproducir.

### 12.4 Confidencialidad — el régimen, textual

El `README.md` del CNC dice, sobre las carpetas `input/`:

> "La copia en `input/` es **idéntica a la del cliente**: sustancias trae 50 columnas con nombres y direcciones, y SABE 30, incluidas 8 de **GPS**. No sacar estas carpetas del equipo ni subirlas a ningún servicio."

> "`carga.cargar()` y los xlsx excluyen la PII **por nombre de columna**. Ese filtro **no detecta** las fechas de nacimiento del listado del hogar en sustancias (`EDAD_DD_*`, `EDAD_AAAA_*`, `FECHA_*`), que siguen en el xlsx."

> "Nada de lo que sale de aquí hacia un reporte o hacia la bóveda puede llevar registros individuales: solo agregados."

Reglas operativas adoptadas por este proyecto, que valen mientras `data/raw/cnc/` exista. **No aplican a los resultados electorales de §14**, que tienen su propio régimen (D16):

1. **Ningún `.sav`, `.dta` ni `<estudio>_base.xlsx` del CNC sale del equipo de Daniel.** Nada de eso se adjunta a una conversación, se sube a un servicio ni se copia a otra máquina.
2. Lo único que cruza es `data/external/cnc/*`, que son agregados con supresión.
3. `.gitignore` **no era suficiente**, y por eso la carpeta salió del repositorio (16/09/2026) en vez de quedarse ignorada. Lo que hay que seguir verificando en su nueva ubicación es que no esté dentro de OneDrive, Google Drive, Dropbox, iCloud ni de una copia de respaldo automática. **A favor:** el directorio de usuario de este equipo no tiene carpeta de OneDrive, Drive ni Dropbox — Windows no está redirigiendo Escritorio ni Documentos a la nube. La única carpeta sincronizada presente es `Creative Cloud Files` (Adobe), que sincroniza solo su propio contenido. Verificado por listado del directorio de usuario el 16/09/2026; **no** es una auditoría de servicios instalados.
4. El filtro de PII del CNC es por nombre de columna y tiene un hueco conocido (fechas de nacimiento en sustancias). No confiar en él como única barrera: `cnc_agregar.py` selecciona columnas por lista blanca, no por exclusión.

### 12.5 Lo que los estudios aportan aparte de la evidencia territorial

`estudios/<estudio>/src/estimacion.py` trae `svy_prop`: proporción ponderada con **varianza por linealización de Taylor** (estratos y conglomerados, con reemplazo), IC 95 % en escala logit, más `diff_prop`, `deff`, `resumen_peso` y `resumen_diseno` (que cuenta los "lonely PSU"). Es copia literal de la librería interna del CNC, validada contra su propia bóveda.

**El proyecto viene calculando medias ponderadas ingenuas en todas partes** — en la ECP, en el donante, en los diagnósticos. Eso subestima los errores estándar por un factor del orden de \(\sqrt{DEFF}\), y el DEFF mediano medido aquí es 2,5. Adoptar `svy_prop` (o su equivalente para medias) es barato y cambia la lectura de cualquier diferencia que hoy se reporte sin intervalo. Está en la lista de §9.

**Nota de ejecución:** `carga.py` del CNC importa `pyreadstat`, que no está en el intérprete del repositorio (sí en el venv del CNC). `cnc_agregar.py` trae un stub que permite importar `carga.py` sin `pyreadstat` — para conservar su filtro de PII — y cae a `<estudio>_base.xlsx` cuando no puede leer el `.sav`.

---

## 14. Resultados electorales entregados por el CNC *(29/09/2026)*

**Régimen: D16, no R10.** Sin datos de personas; se pueden leer con un LLM y usar en el
proyecto. Viven fuera del repositorio, en la carpeta a la que apunta
`BSS_ELECTORAL_DIR` (en el PC personal, `Desktop\CNC_datos`: **no** es la carpeta de
los estudios de §12, y no deben mezclarse). En el PC del CNC no están.

### 14.1 Qué hay

| Archivo | Nivel | Contenido | Filas |
|---|---|---|---|
| `MMV_PRESIDENTE_2014_1ERA_VUELTA.xlsx` | **mesa** | presidente 2014, 1.ª vuelta | 704.177 |
| `MMV_PRESIDENTE_2018_1ERA_VUELTA.xlsx` | **mesa** | presidente 2018, 1.ª vuelta; hojas: escrutinio antes de modificaciones, final y `DIVIPOL` (puestos, mesas, potencial electoral por sexo) | 745.470 |
| `MMV_NACIONAL_PRESIDENTE_2018_1v.xlsx` | **mesa** | lo mismo, más hojas de candidatos y partidos. **Tres copias idénticas** (sha256 `f5ecc623…`) | 745.469 |
| `MMV_NACIONAL_PRESIDENTE_2022_1v.csv` | **mesa** | presidente 2022, 1.ª vuelta, con nombre de puesto. `latin-1`, separador `;`. **Dos copias idénticas** (`976fa0da…`) | 727.510 |
| `RESULTADOS_ELECTORALES_2018_SENADO_DE_LA_REPUBLICA_20250530.csv` | **mesa** | Senado 2018 por candidato | 5.191.659 |
| `RESULTADOS_ELECTORALES_2018_CAMARA_DE_REPRESENTANTES_20250530.csv` | **mesa** | Cámara 2018 por candidato | 4.135.369 |
| `2018_presidencia_{primera,segunda}_vuelta.dta` | municipio | presidente 2018, con censo electoral por sexo | 12.725 / 5.802 |
| `2022_presidencia_{primera,segunda}_vuelta.dta` | municipio | presidente 2022 | 13.068 / 5.940 |
| `2018_camara.dta.csv` | municipio | Cámara 2018 por candidato, con curules y censo | 146.084 |
| `2018 Camara.xlsx`, `2018 Senado.xlsx`, `2018 Consulta.xlsx` | municipio | votos por partido y censo, con color de partido | — |
| `Datos_Camara.xlsx`, `Datos_Senado.xlsx` | municipio | **2022** (no 2018): votos por partido; hoja de totales (votantes, nulos, no marcados, blancos) | 76.095 / 29.701 |
| `Data_Total_Coaliciones.xlsx` | municipio | 2022, votos de tres coaliciones (una hoja por coalición) | 5.941 × 3 |
| `indice por municipio.xlsx` | municipio | **índice de ideología 0 (derecha) – 6 (izquierda)**, producto del CNC. Bogotá = 4 | 1.123 |

Origen: Registraduría Nacional (resultados), consolidaciones del CNC (coaliciones,
totales, índice).

### 14.2 Lo que importa para este proyecto: Bogotá por dentro

Los cinco archivos por mesa traen Bogotá (código de departamento de la Registraduría
**16**, no el 11 del DANE) con **22 zonas**: 1 a 20, 90 y 98.

| Archivo | Puestos | Mesas | Votos |
|---|---|---|---|
| Presidente 2022, 1.ª vuelta | **901** | **14.935** | 3.801.013 |
| Senado 2018 | 642 | 15.462 | 2.809.019 |
| DIVIPOL 2018 | 642 | 14.420 | potencial 5.702.805 |

*Corrección (29/09):* la primera versión de esta tabla decía 1.296 puestos y 14.937 mesas
en 2022. Era un artefacto de lectura: tres puestos de Kennedy tienen código alfanumérico
(«A1», «A2», «A3») y pandas, al inferir tipos, leyó la columna mezclando números y texto
y contó duplicados. Leída como texto: 901 puestos y 14.935 mesas.

### 14.3 Zona = localidad: verificado (29/09/2026)

**Las zonas 1–20 de la Registraduría son las localidades 1–20, con la numeración del
DANE.** Dos pruebas independientes:

1. **Tamaño.** Potencial electoral 2018 por zona (hoja `DIVIPOL`) contra población 18+
   de la localidad del mismo código (`data/external/marginal_localidad_18mas.csv`):
   **r = 0,991** (rangos 0,981). Con los códigos barajados 10.000 veces, la
   correlación nunca pasa de 0,77 (p99 = 0,54). Sumapaz: 2.669 potenciales contra 2.757
   adultos.
2. **Nombres.** Toda localidad cuyo nombre aparece en nombres de puesto cae en la zona
   de su código, en 2018 y en 2022 (Suba: 16 de 16 puestos en la zona 11; Bosa 7 de 7
   en la 7; igual Kennedy, Usme, Tunjuelito, San Cristóbal, Engativá, Fontibón,
   Teusaquillo, Puente Aranda, Rafael Uribe, Sumapaz). Los únicos cruces son palabras
   genéricas: el barrio Santa Fe (en Los Mártires) y colegios «Antonio Nariño» y
   «Simón Bolívar» en otras zonas.

**Tres cosas que viajan con el dato:**

- **La zona 90 no es una localidad.** Es un solo puesto, «PUESTO CENSO (FERIA
  EXPOSICIÓN)» (Corferias), con el **7,6 % del potencial electoral** (361 mesas).
  La 98 son las cárceles (Buen Pastor, La Picota, Modelo, Distrital). Ese 7,6 % no se
  puede ubicar en ninguna localidad.
- **La zona es dónde se está inscrito, no dónde se vive.** La razón potencial / población
  18+ va de **0,70 (Suba, Bosa)** a **1,74 (Antonio Nariño) y 3,04 (La Candelaria)**:
  el centro tiene más votantes que adultos y la periferia menos. Lectura probable:
  gente que se mudó a la periferia sin cambiar la inscripción. El mapa electoral queda
  **suavizado hacia el centro**, y eso hay que decirlo al lado de cualquier mapa.
- **2022 tiene más puestos que 2018 en todas las zonas** (+25 % a +80 %; 901 contra
  642 — *corregido el 29/09: decía 1.296, ver §14.2*). El aumento parejo apunta a una ampliación real de la Registraduría, no a una
  recodificación. **Comparar por zona entre años es seguro; por puesto, no.**

**Sin verificar todavía:** el archivo de 2014 (`MMV_PRESIDENTE_2014_1ERA_VUELTA.xlsx`)
usa otros nombres de columna (`COD_ZZ`); la correspondencia se probó en 2018 y 2022.

Con esto, esta es la **primera fuente del proyecto con geografía real dentro de
Bogotá**, en tres elecciones, que es el vacío que dejó `A08_PASO0B_RESULTS.md`.

### 14.4 La tabla por localidad (29/09/2026)

`src/population/electoral.py` (13 pruebas en `tests/test_electoral.py`) lee los tres
archivos de primera vuelta presidencial y escribe en `data/external/electoral/`, que
**sí se sube** (agregados de resultados públicos):

| Archivo | Qué es |
|---|---|
| `presidente_1v_localidad.csv` | votos por año × zona × opción, con `cod_loc`, `localidad`, `clave` estable entre años (`petro` en 2018 y 2022) y `tipo` (candidato, blanco, nulo, no_marcado, promotores_blanco) |
| `presidente_1v_zonas.csv` | por año × zona: puestos, mesas, `votos_total` y `votos_candidatos` |
| `presidente_1v_meta.json` | huella sha256 de cada fuente, hoja usada, verificación y notas |

| Año | Puestos | Mesas | Votos | Contra el archivo municipal |
|---|---|---|---|---|
| 2014 | 490 | 14.232 | 2.510.384 | sin archivo para contrastar |
| 2018 | 642 | 14.420 | 3.705.960 | coincide, salvo 27 votos conocidos (DI-EL3) |
| 2022 | 901 | 14.935 | 3.801.013 | coincide exacto |

Para calcular proporciones de candidato, usar `votos_candidatos` como base (DI-EL5).

### 14.5 Senado y Cámara 2018, por partido (29/09/2026)

`congreso_2018_localidad.csv` y `congreso_2018_zonas.csv`: votos por corporación ×
circunscripción × localidad × partido (votos de lista y de candidato juntos), con
`votos_partidos` como base para proporciones.

**Las 723 filas «duplicadas» de la Cámara no son duplicados** (DI-EL8). Están todas
en las circunscripciones especiales, con el candidato vacío: son candidatos distintos
de una lista cuyo nombre no viene. La prueba: con todas las filas, la circunscripción
indígena suma 74.176, exactamente el archivo municipal; sin ellas, 73.603. No se
descarta ninguna fila.

| Corporación | Circunscripción | Votos en Bogotá | Verificación |
|---|---|---|---|
| Cámara | territorial | 2.653.552 | **exacta, partido por partido** (`2018 Camara.xlsx`) |
| Cámara | indígena | 74.176 | exacta en el total (`2018_camara.dta.csv`) |
| Cámara | afrodescendiente | 72.042 | diferencia conocida: el municipal suma 6.345 más, casi exactamente los votos de lista sin candidato (6.344); parece doble conteo del municipal |
| Senado | nacional | 2.714.213 | aproximada: ≤ 0,6 % por partido, 0,05 % en el total (`2018 Senado.xlsx`; cortes distintos del escrutinio). Tolerancia fijada: 1 % y 0,1 % |
| Senado | indígena | 94.806 | sin archivo municipal para contrastar |

Primera lectura, sin análisis: la Lista de la Decencia (la de Petro) va del 4 % en
Usaquén al 16 % en Ciudad Bolívar; el Centro Democrático, del 33 % al 15 %. El mismo
gradiente norte–sur que el voto presidencial (`GEOGRAFIA_ELECTORAL_RESULTS.md`).
**Los productos del CNC de 2022 (`Datos_Senado`, `Datos_Camara`, coaliciones) no
entran**: son por municipio, sin geografía dentro de Bogotá.

### 14.6 Presidente 2026, primera vuelta (30/09/2026)

**Fuente: la Registraduría directamente, no el CNC.** Escrutinios publicados en
`escrutiniospresidente2026.registraduria.gov.co`, comisión general de Bogotá (1009).
Mismo régimen que el resto de §14 (D16): resultados públicos, sin datos de personas.
Descargados con permiso de Daniel a `BSS_ELECTORAL_DIR\registraduria_2026\`:

| Archivo | Qué es | Tamaño |
|---|---|---|
| `MMV_XXX_16_000_XXX_XX_XX_XXX_1009.csv` | votos mesa a mesa, todo Bogotá (UTF-8, `;`) | 24,6 MB |
| `MMS_XXX_16_000_XXX_XX_XX_XXX_1009.csv` | novedades por mesa: sufragantes, recuentos, exclusiones; **no trae votos** | 2,6 MB |
| `E26_PRE_16_001_XXX_XX_XX_XXX_1009.pdf` | acta general del escrutinio; **imagen escaneada, sin texto** | 1,1 MB |

Lo que **no** se descargó: las actas E-14 de cada mesa (unos 17.000 PDF escaneados),
el E-24 y el documento AGE (84 MB): no hacen falta.

**Revisión por estructura, antes de calcular proporciones** (DI-EL10 en `electoral.py`):
- Primera vuelta: 11 candidatos, corporación PRESIDENTE, archivos del 2 al 10 de junio.
- 17.157 mesas, 1.083 puestos, 22 zonas. **Zona = localidad confirmado por la propia
  fuente**: el MMV trae el código de localidad de cada puesto, y coincide con la zona
  en los 1.078 puestos de las zonas 1–20.
- Verificación: 4.128.330 votos en el MMV contra 4.130.103 sufragantes de las mesas no
  excluidas del MMS (0,04 %; tolerancia 0,1 %). Es el mismo escrutinio, no una fuente
  independiente. Las 7 mesas excluidas no están en el MMV.
- Las filas de 2014–2022 de la tabla quedaron idénticas al agregar 2026.

2026 no entra a la capa de Voto del tablero (`preparar_voto.py` sigue con 2014–2022).
Lo usa `POLOS_2026_SPECIFICATION.md`.

---

*Documento vivo — actualizar el estado de la tabla de la sección 2 cada vez que un dataset entre al repositorio, y §12.4 cada vez que cambie algo del régimen de los datos del CNC.*

---

## 15. Biblioteca pública del CNC *(1/10/2026)*

**Qué es.** La Biblioteca Digital de la página del CNC
(https://www.centronacionaldeconsultoria.com/biblioteca-cnc) publica informes de estudios, «con
fines informativos y académicos». Son **informes en PDF con cifras agregadas**, no microdatos. La
sugirió el jefe de Daniel como fuente para hacer más sólido el laboratorio.

**Revisión (1/10).** Se leyeron las fichas de los 158 documentos (descripción y enlace), sin
descargar. Quedaron fuera los electorales (intención de voto, imagen de candidatos), los que no son
de opinión (ratings, minería, petróleo, empresas) y los de la pandemia. **Salud mental 2023 y
sustancias psicoactivas en Bogotá 2022 no se tocaron:** son los estudios cuyos microdatos restringe
R10 (§12); usar sus informes publicados queda para una decisión de Daniel.

**Descargados con permiso de Daniel (1/10), fuera del repo**, en
`C:\Users\User\Desktop\CNC_datos\biblioteca_publica\` (7,4 MB). Se leen con `pypdf`, instalado en el
venv para esto.

| Archivo | Qué es | Bogotá | Sirve para |
|---|---|---|---|
| `opinion_publica_bogota_2023-08-15.pdf` | Encuesta de opinión para Red+ y Caracol Radio, 15/08/2023, **4.275 personas en Bogotá**. Margen total 1,5 %; por localidad, 3,8 % a 9,4 % | **Toda la encuesta.** Cruces por sexo, edad (4 tramos), estrato (1 a 6) y **13 localidades + «Otra»**, que agrupa Usaquén, Chapinero, San Cristóbal, Teusaquillo, Antonio Nariño y La Candelaria | **Preguntas nuevas con respuesta conocida:** «¿Estás de acuerdo con mantener el metro elevado?» (65,7 % sí) y «¿…con el Corredor Verde por la carrera séptima?» (58,8 % sí). La EPC no las hizo. También preocupaciones de la localidad y victimización en 6 meses |
| `opinion_publica_2023-08-29.pdf` | La misma serie, 26 a 28/08/2023, **4.575 personas en Bogotá**, 14 preguntas | Toda; cruces por sexo y edad, y por las 15 localidades más pobladas | Contraste externo: victimización en 12 meses (`VS15`), «¿Bogotá tendrá metro en 10 años?» (cerca de `MV150`), «¿Bogotá es una ciudad…?», confianza en los parques. El resto es conducta (uso de TransMilenio y bicicarriles, colarse, desempleo) |
| `plataformas_digitales.pdf` | Percepción sobre plataformas digitales y sus trabajadores, mayo 2024, 1.076 personas | **Columna de Bogotá (448)** | Tema que la EPC no mide; solo ciudad, sin estrato ni localidad |
| `ciudadania_y_democracia_2023.pdf` | Problemas, participación y asambleas ciudadanas, sept. 2023, nacional | Columna de Bogotá (522) | Contraste: problemas principales del país y de la ciudad |
| `sistema_pensional_andi_2024.pdf` | Percepción del sistema pensional, abril 2024, 2.791 personas | Bogotá solo como región de la muestra | Poco: no separa Bogotá en los resultados |
| `termometro_cambio_cnc_2026-01.pdf` | Termómetro de opinión, enero 2026, 2.202 personas; propósito electoral | 340 en Bogotá, como región | Poco: casi todo es electoral o nacional |

**Hechos que pesan en cualquier uso:**
- **Método distinto al de la EPC.** Las dos de Bogotá son **encuestas en línea, autoaplicadas en el
  celular**, con invitación por SMS a usuarios de Claro, selección aleatoria del directorio de
  líneas móviles y factores calibrados. La EPC es cara a cara en el hogar. Una diferencia de nivel
  entre las dos no prueba que la población sintética esté mal.
- **Los estratos altos son pocos** en la del 15/08: 97 personas en estrato 5 y 26 en el 6. Sus
  porcentajes por estrato 5-6 son muy inestables.
- **Un error del informe:** en la del 15/08, la gráfica por localidad del metro elevado (p. 14)
  lleva el título de la de victimización. Los valores son otros (Suba 76,2 %, total 65,7 %), así que
  es el metro con el título equivocado.
- **Son de 2023**, el año central de la población 2022-2024.

**Lo que habilita.** Por primera vez hay **preguntas de verdad nuevas**, sin pariente directo en el
catálogo, con resultados reales de Bogotá por grupo y por localidad: el metro elevado y el Corredor
Verde. Sirven para un pre-registro que mida lo que la validación del puente no pudo medir (si
acierta el nivel y el orden de los grupos en una pregunta realmente nueva), con el aviso del método
distinto.

## 16. Encuestas políticas del CNC: Semana y Revista Cambio *(6/10/2026, D21)*

**Régimen: D21, una excepción limitada a R10.**
- **Pueden ir a una API, incluidos los modelos de lenguaje,** el texto de las preguntas de opinión y sus escalas.
- **Nunca van** las respuestas individuales ni las preguntas abiertas.
- **Los porcentajes agregados** se calculan en el equipo.
- **Dónde viven:** fuera del repositorio, en la carpeta de `BSS_CNC_POLITICA_DIR` (en el PC del CNC, `Desktop\CNC_datos_nuevos`).
  No se mezclan con los estudios de §12 ni con los resultados de §14.

**La revisión (6/10/2026)** fue solo de estructura: nombres de columnas, filas y diccionarios, sin imprimir ningún valor.
- **Ninguna base tiene columnas de datos personales.** No hay nombre, teléfono, dirección, documento ni coordenadas.
- **Todas traen** factor de expansión (`factor` o `FACTOR`).
- **Geografía:** solo municipio, sin localidad.

| Estudio | Cliente | Fecha | Encuestados | En Bogotá | Lo político |
|---|---|---|---|---|---|
| CC355801 | Semana | feb 2021 | 2.283 | 384 | migración venezolana (afirmaciones de acuerdo) |
| CC871401 | Semana | may 2021 | 2.001 | 256 | intención de voto presidencial 2022 y segundas vueltas; imagen de 50 personajes; paro nacional |
| CC871801 | Semana | jun 2021 | 2.077 | 260 | intención de voto, segundas vueltas, imagen de personajes y funcionarios, el paro |
| CC873501 | Semana | 2021-22 («Semana 11») | 4.093 | 411 | probabilidad de votar, intención de voto, segundas vueltas, expresidentes |
| CC875701 | Semana | abr 2022 | 4.599 | 439 | intención de voto y segundas vueltas |
| CC891901 | Revista Cambio | ene 2026 | 2.202 | 336 | probabilidad de votar, presidencial 2026, consultas del 8 de marzo |
| CC892901 | Revista Cambio | 2026 | 3.684 | 545 | consultas interpartidistas, presidencial (base en CSV) |
| CC893201 | Revista Cambio | 2026 | 2.157 | 285 | fórmulas presidenciales, segundas vueltas |
| CC893401 | Revista Cambio | 2026 | 2.157 | 342 | fórmulas, «nunca votaría», segundas vueltas |
| CC893701 | Revista Cambio | 2026 | 2.202 | 305 | fórmulas, «nunca votaría», segundas vueltas |

**El anexo** `docs/anexos/inventario_cnc_politica.csv` trae cada pregunta (estudio, variable, tema y texto), unas 450.
Los temas se asignaron por palabras clave y son aproximados:
- unas 100 de intención de voto;
- unas 90 de imagen de personajes;
- el resto, sobre el paro de 2021, la migración, la aprobación del gobierno y los expresidentes.

**Lo que no traen o no sirven:**
- **Localidad,** así que no van al mapa.
- **Preguntas abiertas,** como «¿qué políticos promueven el paro?»: quedan fuera por D21.
- **Fechas exactas** de los estudios de Cambio de 2026: hay que leerlas de `FECHAINI` cuando se usen.

