# DATA SPECIFICATION — BOGOTÁ SOCIAL SIMULATOR

Proyecto: Bogotá Social Simulator
Organización: Centro Nacional de Consultoría (CNC)
Documento: Puente entre RESEARCH.md y el futuro MODEL_SPECIFICATION.md
Versión: 0.2 — Data Audit inicial, **corregido tras trabajar con los archivos reales**
Fecha: Septiembre de 2026 (revisión del 15/09/2026)

---

## 0. Correcciones de la revisión del 15 de septiembre de 2026

Al descargar y procesar los datasets reales aparecieron tres afirmaciones de la versión 0.1 que no se sostienen. Se corrigen abajo en su lugar correspondiente y se listan acá para que nadie las arrastre desde una copia vieja del documento:

1. **La Encuesta de Confianza Institucional NO tiene dos olas.** Es una sola recolección continua del 4 de diciembre de 2024 al 9 de febrero de 2025. La separación "2024 / 2025" es un corte de calendario dentro de un único trabajo de campo. Ver sección 5 y la sección 8.
2. **Son 8 actores institucionales, no 7.** La versión 0.1 decía "7" y a continuación enumeraba ocho. Verificado contra el archivo publicado.
3. **La columna de fechas del archivo está dañada** por un round-trip de hoja de cálculo, con tres formatos mezclados. Recuperable, pero no era un dato limpio. Ver sección 5.

La corrección 1 es la de mayor impacto: elimina la única fuente de variación temporal que el proyecto creía tener, y con ella la posibilidad de validar la dinámica del modelo con los datos actuales (ver EXPERIMENT_1_SPECIFICATION.md).

---

## 1. Objetivo de este documento

Responder, con evidencia verificable, la pregunta que abre la Fase 1 del roadmap:

> ¿Qué datos existen realmente para construir la población sintética de Bogotá y para calibrar/validar un modelo de dinámica de opinión pública?

Este documento **no toma decisiones de modelamiento**. Solo inventaría fuentes, evalúa su utilidad y señala qué falta. Las decisiones A03–A05 (datasets definitivos, método de generación de la población) se toman después.

**Nota sobre el alcance de la palabra "confirmado" en este documento:** significa "verificamos que el dataset existe y sirve", no "lo tenemos descargado". El estado operativo de cada fuente —qué está efectivamente en `data/raw/`— se lleva en DATA_INVENTORY.md.

## 2. Metodología del data audit

Se investigaron fuentes oficiales y verificables (DANE, Secretaría Distrital de Planeación — SDP, IDECA, microdatos.dane.gov.co, datosabiertos.bogota.gov.co) más una fuente independiente de opinión pública (Bogotá Cómo Vamos) y la huella pública de metodología del CNC. No se asumió la existencia de ningún dataset sin confirmarlo; cada entrada abajo tiene URL verificable.

**Importante:** no se tuvo acceso a los sistemas internos del CNC. La sección 6 (Datos del CNC) es una hipótesis informada a partir de la metodología pública que el CNC usa en sus estudios de opinión — debe confirmarse directamente con el equipo de investigación del CNC.

---

## 3. Fuentes DANE — demografía y estructura poblacional

### DATASET — Censo Nacional de Población y Vivienda (CNPV) 2018
- **Fuente:** DANE — dane.gov.co
- **Año:** 2018 (base de todas las proyecciones vigentes)
- **Cobertura:** Nacional, con desagregación hasta localidad/UPZ en Bogotá
- **Granularidad:** Persona/hogar/vivienda; agregable a localidad y UPZ
- **Variables disponibles:** edad, sexo, estado civil, nivel educativo, condición étnica, ocupación, características de la vivienda y el hogar
- **Variables útiles:** distribución basal de edad/sexo/educación por localidad — insumo directo para calibrar la población sintética
- **Variables faltantes:** opinión, percepción, confianza — el censo no mide actitudes
- **Calidad:** alta, es la operación estadística de referencia del país
- **Sesgos potenciales:** desactualización natural (2018) — por eso existen las proyecciones post-COVID descritas abajo
- **Uso recomendado:** distribución basal demográfica de los agentes
- **Limitaciones:** no captura dinámica social ni cambios posteriores a 2018
- **¿Usarlo?** Sí — como fundamento, no como única fuente

### DATASET — Proyecciones y retroproyecciones de población por localidad/UPZ/UPL (2005–2035)
- **Fuente:** DANE + Secretaría Distrital de Planeación (SDP), convenio interadministrativo (095/2020 y 479/2024) — "Visor de Población"
- **URL:** sdp.gov.co/gestion-estudios-estrategicos/.../proyecciones-de-poblacion ; dane.gov.co/.../proyecciones-de-poblacion-bogota
- **Año:** actualizado en 2024–2025, incorpora ajuste post-COVID
- **Cobertura:** Bogotá D.C. completa
- **Granularidad:** Localidad (2005–2035) y UPZ/UPL (2018–2024), por grupo de edad y sexo
- **Variables disponibles:** población proyectada por localidad/UPZ, edad **simple** (año a año, 0 a 100+) y sexo, por año
- **Variables útiles:** exactamente lo que el proyecto necesita para distribuir agentes territorialmente por localidad
- **Variables faltantes:** estrato, educación, situación laboral a ese nivel de desagregación (hay que cruzar con otra fuente)
- **Calidad:** alta — es la fuente oficial que usa la propia SDP en sus diagnósticos por localidad
- **Sesgos potenciales:** es una proyección, no una medición directa; supuestos demográficos del modelo DANE
- **Uso recomendado:** distribución territorial (localidad) del tamaño de la población sintética
- **Limitaciones:** disponible en Excel vía visor interactivo, no siempre como API
- **¿Usarlo?** Sí — es la pieza central de la capa territorial
- **Estado operativo (15/09/2026):** descargado y en uso. El marginal de población adulta por localidad para 2025 está en `data/external/marginal_localidad_18mas.csv`. **Nota de cruce:** el anexo escribe "Ciudad Bolivar" sin tilde mientras el resto del proyecto usa "Ciudad Bolívar"; sin normalizar, esa localidad queda con peso cero al ponderar.

### DATASET — Gran Encuesta Integrada de Hogares (GEIH)
- **Fuente:** DANE (microdatos.dane.gov.co)
- **Año:** serie continua, mensual/anual (2023, 2024, 2025, 2026 disponibles)
- **Cobertura:** Nacional, con representatividad para Bogotá como ciudad (no confirmado a nivel de localidad)
- **Granularidad:** Persona/hogar; ~240.000 hogares/año a nivel nacional
- **Variables disponibles:** empleo, desempleo, ingresos, sexo, edad, estado civil, nivel educativo, productos financieros del hogar
- **Variables útiles:** situación laboral y nivel socioeconómico — dos atributos centrales del agente
- **Variables faltantes:** opinión, percepción
- **Calidad:** alta, es la encuesta de mercado laboral de referencia en Colombia
- **Sesgos potenciales:** diseño muestral pensado para indicadores agregados de ciudad, no para 20 localidades — la desagregación a localidad puede tener error muestral alto
- **Uso recomendado:** calibrar situación laboral y variables socioeconómicas a nivel ciudad; evaluar si el tamaño de muestra permite bajar a localidad
- **Limitaciones:** confirmar con el DANE el nivel de desagregación geográfica real disponible para Bogotá
- **¿Usarlo?** Evaluar

---

## 4. Fuentes Bogotá / SDP / IDECA — territorio y condiciones socioeconómicas

### DATASET — Encuesta Multipropósito (EM) Bogotá–Cundinamarca
- **Fuente:** DANE + SDP (microdatos.dane.gov.co, datosabiertos.bogota.gov.co)
- **Año:** aplicada en 2011, 2014, 2017 y 2021 (serie histórica reutilizable para backtesting)
- **Cobertura:** Bogotá + municipios de Cundinamarca
- **Granularidad:** Hogar/persona, desagregable a UPZ (más fino que localidad)
- **Variables disponibles:** vivienda y entorno, condiciones habitacionales, servicios públicos y TIC, composición del hogar, salud, cuidado infantil, educación, uso de TIC, **y un capítulo J de "Participación en organizaciones y redes sociales"**
- **Variables útiles:** es la fuente socioeconómica más rica y específica de Bogotá que se encontró — cubre casi todos los atributos demográficos del agente, y el capítulo J roza variables de capital social relevantes para la red de interacción
- **Variables faltantes:** no mide opinión política ni percepción de temas de ciudad directamente
- **Calidad:** alta — es la encuesta socioeconómica oficial de referencia de la ciudad, con tres rondas históricas anteriores útiles para backtesting de la población
- **Sesgos potenciales:** periodicidad irregular (2011/14/17/21) — la ronda más reciente ya tiene ~5 años. **Sobre-muestrea localidades pequeñas por diseño**, para poder estimar a nivel de localidad: usar el microdato sin ponderar traslada esa distorsión a cualquier muestra derivada (ver D14 en PROJECT_CONTEXT.md)
- **Uso recomendado:** columna vertebral de la población sintética a nivel UPZ/localidad; su serie histórica es candidata natural para el backtesting de la población
- **Limitaciones:** confirmar si el capítulo J es suficiente para inferir una red de interacción o solo participación asociativa
- **¿Usarlo?** Sí — fuente prioritaria junto con las proyecciones de población
- **Estado operativo (15/09/2026):** descargada y en uso como fuente receptora del hot-deck. **Factor de expansión confirmado: la columna se llama `FEX_C`** y va de 1,18 a 245,70, expandiendo a 5.480.551 adultos (2021). Variables puente confirmadas: `NOMBRE_LOCALIDAD`, `SEXO`, `NPCEP4` (edad), `NVCBP11AA` (estrato para tarifa), `NPCHP4` (nivel educativo, 15 categorías). **Advertencia:** `ESTRATO2021` NO es el estrato socioeconómico sino un código interno de unidad de muestreo; y `NVCBP11AA` incluye los códigos 8 y 9, que son no-respuesta y no estratos (ver A17).

### DATASET — Cartografía de localidades y UPZ (IDECA / Mapa de Referencia)
- **Fuente:** IDECA — Infraestructura de Datos Espaciales de Bogotá (ideca.gov.co, datosabiertos.bogota.gov.co)
- **Año:** actualización continua
- **Cobertura:** Bogotá D.C. completa, incluida la ruralidad (Sumapaz y las 7 localidades con área rural)
- **Granularidad:** polígonos de localidad y UPZ/UPL, en formatos SHP, GeoJSON, KML, GeoPackage
- **Variables disponibles:** geometría, nombre y código de localidad/UPZ
- **Variables útiles:** capa territorial para PostGIS y el mapa del dashboard
- **Variables faltantes:** ninguna — es puramente geográfico
- **Calidad:** alta, licencia de uso abierta
- **Sesgos potenciales:** ninguno relevante
- **Uso recomendado:** base geográfica del sistema (localidad → UPZ → agentes)
- **Limitaciones:** ninguna significativa
- **¿Usarlo?** Sí — no se necesita hasta la fase de dashboard

---

## 5. Opinión pública — fuentes externas independientes (clave para validación)

Este es el hallazgo más importante del audit: **existe una fuente pública, independiente y con serie histórica de más de 25 años que mide exactamente el tipo de variable que el proyecto quiere simular.**

### DATASET — Encuesta de Percepción Ciudadana — Bogotá Cómo Vamos (BCV)
- **Fuente:** Bogotá Cómo Vamos (alianza Fundación Corona, El Tiempo Casa Editorial, Cámara de Comercio de Bogotá, Universidad Javeriana) — bogotacomovamos.org
- **Año:** serie anual continua desde 1998
- **Cobertura:** zona urbana de Bogotá, representativa de ciudad (confirmar desagregación por localidad/estrato/edad — los informes sí publican cortes por edad y nivel socioeconómico)
- **Granularidad:** encuesta presencial, ~1.500 personas/año, error muestral ~2.7–3%
- **Variables disponibles:** satisfacción con la ciudad, optimismo sobre el futuro, orgullo por Bogotá, percepción de seguridad (propia y de barrio), confianza institucional, evaluación de gestión del alcalde, prioridades ciudadanas (salud, seguridad, movilidad, economía), percepción sobre proyectos específicos (p. ej. Metro)
- **Variables útiles:** es el mejor candidato encontrado como **variable dependiente observada** para calibrar y para backtesting del modelo de opinión — mide exactamente "percepción de seguridad", "opinión sobre gestión pública", etc., con serie temporal
- **Variables faltantes:** no está confirmado si desagrega por localidad (probablemente solo por estrato/edad/zona) — a verificar en las fichas técnicas de cada ronda
- **Calidad:** alta — es descrita como "el estudio más sistemático y riguroso de opinión pública sobre Bogotá", metodológicamente estable durante 25+ años
- **Sesgos potenciales:** al ser una alianza privada (no oficial/estatal), su diseño muestral y preguntas han evolucionado con el tiempo; verificar comparabilidad año a año
- **Uso recomendado:** fuente externa de validación — permite comparar la salida del ABM contra una serie observada real, independiente de los datos usados para calibrar
- **Limitaciones:** no da microdatos por agente, sino resultados agregados publicados en informes/PDF — falta confirmar si hay microdatos disponibles bajo solicitud
- **¿Usarlo?** Sí, y **conseguir su microdato es ahora la prioridad crítica del proyecto**: tras la corrección de la entrada siguiente, es la única fuente conocida con la profundidad temporal que la validación de la dinámica exige. Ver sección 9.

### DATASET — Encuesta de Percepción de Confianza Institucional en Bogotá (Veeduría Distrital)
- **Fuente:** Veeduría Distrital de Bogotá — publicada en Datos Abiertos Bogotá, dataset "Base de Datos Encuesta Confianza Entidades Distritales", archivo `Base_EncuestaConfianza_2024-2025.csv`, licencia CC BY-SA 4.0
- **Periodo de recolección:** **⚠️ CORREGIDO 15/09/2026.** Una sola recolección continua, del **4 de diciembre de 2024 al 9 de febrero de 2025** (68 días, con solo dos días sin respuestas). La versión 0.1 de este documento la describía como "dos olas — 2024 (línea base, n=2.128) y 2025 (n=3.159)". **Los dos n son correctos, la interpretación no:** corresponden a partir un único trabajo de campo por el cambio de año, no a dos mediciones separadas. Hay respuestas a ambos lados del 1 de enero sin ninguna interrupción (31-dic: 40 respuestas; 2-ene: 60).
- **Cobertura:** Bogotá D.C., las 20 localidades (incluye Sumapaz)
- **Granularidad:** persona, autoadministrada (formulario digital), 5.287 registros totales, 4.878 con localidad válida dentro de Bogotá, 144 columnas
- **Variables disponibles:** edad (rangos: 18-25, 26-35, 36-45, 46-55, 56+), género (7 categorías, incluye no binario/trans), localidad de residencia, nivel educativo (6 categorías), ocupación principal, ingresos mensuales (rangos en SMMLV), grupo étnico, condición de discapacidad; núcleo de confianza institucional con **8 actores** evaluados por separado en escala 1-5 (Secretarías Distritales, Servidores Públicos, Alcaldías Locales, Policía Metropolitana, Organismos Distritales de Control, Entidades adscritas e institutos, Órganos de justicia distritales, Comisarías de Familia), más módulos temáticos opcionales (seguridad, salud, transparencia, gestión pública)
- **Variables útiles:** localidad con las 20 unidades representadas — es la primera fuente de opinión/confianza que llega a esa granularidad, algo que BCV no tenía confirmado y que era el vacío más importante identificado en este audit
- **Variables faltantes:** **no trae estrato socioeconómico** (usa ingresos mensuales en rangos de SMMLV como proxy, con categorización propia no directamente homologable a Multipropósito/GEIH); no trae factor de expansión/ponderación propio
- **Calidad:** estructuralmente limpia en la pregunta núcleo (99.3% de respuesta), pero con tres problemas reales documentados al procesarla:
  - **sesgo de representatividad severo sin corregir**: 84% de la muestra tiene educación técnica, universitaria o de posgrado, frente a una distribución real de Bogotá mucho menos concentrada en educación alta (ver Anexo) — patrón típico de autoselección en encuestas digitales voluntarias;
  - **encabezados en cp850 mal decodificado**, con tildes corruptas que cambian entre exportaciones del formulario: las columnas hay que localizarlas por fragmentos de texto y verificarlas antes de cada corrida;
  - **columna `Marca temporal` dañada** por un round-trip de hoja de cálculo: tres formatos mezclados (`Y/m/d h:M:S a.m. GMT-5` en 649 filas; `m/d/Y H:M:S` en 2.888, todas con día > 12; `m/d/Y H:M` en 1.750, todas con día ≤ 12). La frontera exacta en "día > 12" delata que las filas cuyo día cabía como mes fueron reinterpretadas por el programa y reescritas sin segundos. Recuperable en su totalidad — ver `parsear_marca_temporal()` en `src/population/loader.py`.
- **Sesgos potenciales:** autoselección hacia población con mayor educación y probable mayor acceso digital/interés cívico; localidades pequeñas con muestra frágil (Sumapaz, La Candelaria, Los Mártires); **y, sobre todo, ausencia total de variación temporal** — al ser una sola recolección de 68 días, no sirve para backtesting de ningún tipo
- **Uso recomendado:** donante de opinión del hot-deck (rol que cumple hoy) y validación territorial fina de la población sintética, **siempre ponderado** (ver Anexo), nunca en crudo
- **Limitaciones:** **no sirve para calibración ni validación temporal**, por la corrección de arriba. Tampoco es el mismo constructo que "confianza institucional general" de BCV — homologar requiere decisión explícita (¿promedio de los 8 actores como índice compuesto, o modelar por actor?). Nota adicional: el índice compuesto tal como está implementado promedia un número variable de ítems respondidos (de 1 a 8) sin umbral mínimo — ver POPULATION_SPECIFICATION.md 8.4
- **¿Usarlo?** Sí como donante, condicionado a ponderación. **No** como fuente de validación de la dinámica.

### DATASET — Encuesta de Convivencia y Seguridad Ciudadana (ECSC)
- **Fuente:** DANE (microdatos.dane.gov.co)
- **Año:** serie anual, 2023 confirmada
- **Cobertura:** nacional, con representatividad para ciudades principales incluida Bogotá
- **Granularidad:** persona/hogar
- **Variables disponibles:** percepción de seguridad, victimización, confianza en autoridades, y específicamente una variable de **"percepción del aporte a la seguridad"**
- **Variables útiles:** variable de percepción de seguridad oficial y con metodología DANE — complementa a BCV
- **Variables faltantes:** opinión sobre otros temas de ciudad (economía, movilidad, gestión)
- **Calidad:** alta, operación estadística oficial
- **Sesgos potenciales:** foco exclusivo en seguridad/convivencia, no es una encuesta de opinión general
- **Uso recomendado:** segunda fuente de percepción de seguridad, para triangular con BCV
- **Limitaciones:** confirmar nivel de desagregación geográfica dentro de Bogotá
- **¿Usarlo?** **Reevaluado al alza (15/09/2026).** Es la única fuente de opinión con serie anual y microdatos de descarga inmediata. Mide percepción de seguridad, no confianza institucional (la variable fijada en D11), así que usarla implicaría reabrir D11 o tratarla como un segundo fenómeno de prueba para validar la maquinaria mientras llega el microdato de BCV. Ver EXPERIMENT_1_SPECIFICATION.md sección 5.1

---

## 6. Datos del CNC — hipótesis a confirmar (A02)

No se tuvo acceso a los sistemas internos del CNC. A partir de su metodología pública (estudios de intención de voto, "Termómetro de Opinión CAMBIO-CNC", fichas técnicas publicadas) se puede inferir lo siguiente, **pendiente de confirmación directa con el equipo del CNC**:

- El CNC usa **diseño muestral probabilístico estratificado multietápico**, basado en el **Marco Geoestadístico Nacional del DANE**, y calibra sus resultados con proyecciones demográficas y variables socioeconómicas — es decir, ya existe una práctica interna de integración con datos DANE que el proyecto puede aprovechar metodológicamente.
- Sus estudios de opinión (p. ej. el Termómetro de Opinión) miden típicamente: imagen/gestión de figuras públicas, intención de voto, principales preocupaciones ciudadanas (salud, inseguridad, corrupción, economía), y en algunos estudios, percepción y reconocimiento sobre temas específicos.
- No hay evidencia pública de que estos estudios estén desagregados de forma rutinaria a nivel de localidad de Bogotá — sus universos suelen ser nacionales o urbanos generales.

**Preguntas concretas para el equipo del CNC (pendiente):**
1. ¿Existen estudios del CNC específicos para Bogotá, con desagregación por localidad o estrato?
2. ¿Hay **series longitudinales** (mismo ítem medido varias veces) que sirvan para backtesting, similares al Termómetro de Opinión? **Esta pregunta subió de prioridad tras la corrección de la sección 5:** es hoy uno de los dos caminos conocidos para desbloquear la validación de la dinámica.
3. ¿Qué variables de percepción/opinión se preguntan de forma recurrente y podrían mapearse al "estado de opinión" del agente?
4. ¿Qué restricciones de privacidad, licenciamiento y uso interno aplican a estos microdatos?
5. ¿Existen factores de expansión que permitan ponderar por localidad?

---

## 7. Matriz de cobertura: atributo del agente → fuente candidata

| Atributo del agente | Fuente candidata | Estado |
|---|---|---|
| Edad, sexo | CNPV 2018 / Proyecciones DANE-SDP | Confirmado, descargado |
| Localidad / UPZ | Proyecciones DANE-SDP + IDECA (geometría) | Confirmado, descargado (IDECA no se necesita aún) |
| Nivel educativo | CNPV 2018 / Encuesta Multipropósito | Confirmado, descargado |
| Estrato socioeconómico | Encuesta Multipropósito / GEIH | Confirmado, descargado |
| Situación laboral | GEIH | Confirmado (verificar nivel de desagregación) |
| Percepción de seguridad | ECSC (DANE) + Bogotá Cómo Vamos | Confirmado, no descargado |
| Confianza institucional | Bogotá Cómo Vamos | Confirmado (agregado, no microdato) |
| Confianza institucional (desagregación por localidad) | Encuesta de Confianza Institucional — Veeduría Distrital | Confirmado, descargado, condicionado a ponderación |
| **Variación temporal de la opinión** | **BCV (microdato) o CNC** | **Ninguna fuente disponible hoy — bloqueador de la Fase 7** |
| Opinión política / imagen de figuras | CNC (hipotético) | Pendiente de confirmar |
| Red de interacción / afinidad social | Encuesta Multipropósito, capítulo J | Parcial — insuficiente por sí sola |

---

## 8. Limitaciones y sesgos identificados en este audit

- **Ninguna fuente disponible hoy ofrece la misma variable de opinión medida en dos momentos separados.** Esta es la limitación central del proyecto tras la revisión del 15/09/2026, y no se resuelve con código: bloquea los niveles 3, 4 y 5 de validación de RESEARCH.md sección 29, y con ellos el criterio de éxito de PROJECT_CONTEXT.md sección 37.
- Las fuentes de percepción/opinión (BCV, ECSC) publican principalmente **resultados agregados**, no microdatos por persona — hay que confirmar si hay acceso a bases desagregadas antes de asumir que sirven para calibrar agente por agente.
- Ninguna fuente encontrada combina, en un mismo registro, variables demográficas completas **y** variables de opinión — la población sintética se construye fusionando estadísticamente al menos dos fuentes, lo cual introduce un problema metodológico propio (statistical matching) tratado en POPULATION_SPECIFICATION.md.
- No está confirmada la desagregación a nivel de localidad para GEIH, ECSC ni CNC — puede forzar a trabajar a nivel de ciudad, no de localidad, para las variables de opinión.
- Este audit se basó en información pública de portales; no reemplaza la revisión directa de los diccionarios de datos completos. **La revisión del 15/09/2026 mostró el costo de esa limitación:** tres afirmaciones de la versión 0.1 solo se pudieron corregir al procesar los archivos reales.
- La Encuesta de Confianza Institucional requiere ponderación obligatoria por el sesgo de autoselección educativa documentado; usarla sin ponderar sobreestimaría la confianza institucional real de Bogotá (ver Anexo).

---

## 9. Recomendación de próximo paso

**Reordenada tras la revisión del 15/09/2026.**

1. **Solicitar formalmente el microdato de Bogotá Cómo Vamos.** Pasó de "conviene pedirlo temprano" a ruta crítica: es el único camino conocido que permite validar la variable elegida en D11 con profundidad temporal. El tiempo de respuesta de una solicitud es incierto, así que el costo de demorarla es alto y el de pedirla es cero.
2. **Insistir con A02**, en particular la pregunta 2 de la sección 6 (series longitudinales). Si el CNC tiene un tracking con la misma pregunta repetida, resolvería el bloqueador y además habilitaría validación de transiciones individuales — el estándar de Gestefeld & Lorenz, que BCV al ser corte transversal repetido no permite.
3. **Recuperar la ponderación del donante como código.** El Anexo de este documento reporta el resultado del raking (n efectivo 2.409), pero el cálculo no quedó versionado. Es prerrequisito de la validación del estado inicial (EXPERIMENT_1_SPECIFICATION.md sección 4).
4. **Evaluar la ECSC como segundo fenómeno de prueba**, dado que es descargable de inmediato y tiene serie anual. Permitiría validar la maquinaria mientras llegan los datos de la variable principal.
5. Descargar la cartografía IDECA cuando se aborde el dashboard, no antes.

---

## Anexo — Ponderación de la Encuesta de Confianza Institucional (Veeduría Distrital)

**Método:** raking / Iterative Proportional Fitting (IPF) en dos dimensiones (localidad × nivel educativo), con recorte de pesos (cap-and-rake, tope = 4× el peso promedio) para controlar varianza.

**Marginales objetivo (reales, no supuestos):**
- Localidad: DANE-SDP, Proyecciones y retroproyecciones de Población 2005-2035, año 2025, población adulta 18+ por localidad (datosabiertos.bogota.gov.co)
- Nivel educativo: Encuesta Multipropósito 2021 (SDP/DANE), población adulta 18+ residente en Bogotá D.C., variable NPCHP4 ("nivel educativo más alto alcanzado"), recategorizada de 15 a 6 niveles para homologar con la encuesta de confianza

**Resultado:**

| Métrica | Sin ponderar | Con ponderación (recorte 4×) |
|---|---|---|
| n nominal | 4.877 | 4.877 |
| n efectivo (Kish) | 4.877 | 2.409 |
| Pérdida de eficiencia | 0% | 50.6% |
| Razón peso máx/mín | 1 | 16.0× |
| Confianza en Secretarías Distritales (escala 1-5) | 3.089 | 3.035 |

**Calibración lograda por dimensión:**
- Localidad: las 20 localidades quedan dentro de ±0.02 p.p. del objetivo real — sin distorsión relevante.
- Educación: 5 de 6 categorías calibran razonablemente; **"educación primaria" queda sub-corregida** (5.9% ponderado vs. 15.0% real) — el recorte de pesos impide que las ~63 personas de esa categoría en la muestra absorban todo el ajuste necesario. Es un sesgo conocido y acotado, aceptado a cambio de estabilidad estadística (sin recorte, el n efectivo caía a 1.498, pérdida de 69.3%).

**Regla de uso:** cualquier estimación derivada de este dataset debe reportarse junto con el n efectivo (2.409), no el n nominal (4.877) — los márgenes de error reales son ~1.4× más anchos que los que sugeriría el tamaño de muestra bruto. Análisis desagregados que dependan fuertemente del segmento de educación primaria deben señalar esta limitación explícitamente.

**Estado del cálculo (15/09/2026):** estos resultados existen como reporte pero **no como código versionado**. Hay que reconstruirlos antes de poder usarlos en el pipeline — ver sección 9, punto 3, y DATA_INVENTORY.md.

**Documentado como supuesto, no como hecho** (consistente con el Principio 3 del prompt maestro): la independencia condicional entre localidad, educación y la variable de confianza — más allá de lo que capturan las dos dimensiones de ponderación — no está verificada.

---

*Documento vivo — actualizar con cada decisión (formato D0X) siguiendo la convención establecida en PROJECT_CONTEXT.md.*
