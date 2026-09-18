# VISUALIZATION SPECIFICATION — BOGOTÁ SOCIAL SIMULATOR

**Versión:** 0.1
**Fecha:** 18 de septiembre de 2026
**Estado:** Hito 1 construido y publicado. Hitos 2 a 5 especificados, sin construir.
**Documentos relacionados:** PROJECT_CONTEXT.md §31 y §51, ARCHITECTURE.md, POPULATION_SPECIFICATION.md, claude/ANALISIS_DISENO_MUESTRAL.md

---

# 1. POR QUÉ EXISTE ESTE DOCUMENTO

El proyecto cambió de orden, no de objetivo. Hasta el 17 de septiembre de 2026 la
secuencia era: población → red → modelo de opinión → experimentos → motor de
escenarios → (algún día) visualización. A partir del 18 de septiembre la
visualización deja de ser el último paso y pasa a ser **la superficie del
proyecto**: lo que se ve, lo que se muestra y lo que se navega.

Lo que **no** cambia: los datos, los métodos y los resultados ya obtenidos. La
capa visual se construye **sobre** la tubería validada, no en paralelo a ella.
Nada de lo que se dibuja se inventa para que se vea mejor.

Lo que sí cambia, y conviene decirlo sin rodeos: durante un tiempo el proyecto va
a **mostrar más de lo que concluye**. Eso está bien mientras la página diga
exactamente qué es cada cosa. El riesgo de una capa visual bonita sobre un
modelo honesto es que la gente le crea a la imagen más de lo que el modelo
soporta. Todo lo que sigue está diseñado contra ese riesgo.

---

# 2. LA ADVERTENCIA QUE GOBIERNA TODO ESTE DOCUMENTO

PROJECT_CONTEXT.md §31 ya lo decía, antes de que existiera ninguna página:

> un mapa de Bogotá coloreado por opinión simulada mostrará diferencias entre
> localidades que, según los datos reales, **no existen o son del tamaño del
> ruido muestral** […] Es el gráfico más vendedor del dashboard y el más
> engañoso.

Las mediciones del proyecto que sostienen esa advertencia:

| Hecho | Fuente |
|---|---|
| La localidad explica ~1 % de la varianza de opinión individual | D15, sección 39 |
| Entre 54 % y 63 % de la varianza observada *entre* localidades es error de muestreo | claude/ANALISIS_DISENO_MUESTRAL.md, 42 ítems de dos estudios del CNC |
| Efecto de diseño medido en la EPC: mediana 1,86 (rango 1,39–2,69) sobre 11 mediciones en 6 olas | claude/ANALISIS_DISENO_MUESTRAL.md v1.1 |
| Con la población sintética de 1.000 agentes, **el 100 %** de la dispersión de opinión entre localidades es ruido muestral | `src/viz/preparar_mapa.py`, salida del 18/09/2026 |

La última fila es nueva y es más fuerte que la advertencia original. Con 1.000
agentes repartidos proporcionalmente, una localidad mediana aporta ~30 agentes;
su error estándar corregido por efecto de diseño es de ±0,08 a ±0,33 sobre una
escala de 1 a 5. La desviación observada entre las 20 medias es 0,156, y la
desviación esperada **solo por ruido** es 0,183. No queda residuo: la dispersión
real estimada entre localidades es 0,00.

**Regla operativa que sale de ahí, y que aplica a toda página del proyecto:**

> **RV-1.** Ninguna capa de opinión por territorio se dibuja sin su margen de
> ruido al lado, y ninguna escala de color se estira al rango observado por
> defecto.

El hito 1 cumple RV-1 de una forma deliberada: trae **las dos** escalas y deja
al usuario producir el gráfico engañoso a propósito, con el texto que explica
qué acaba de hacer. Enseñar el error es más eficaz que esconderlo.

---

# 3. HITO 1 — LA CIUDAD Y SU POBLACIÓN *(construido)*

**Qué es.** Una página autocontenida con las 20 localidades de Bogotá, tres
capas conmutables y un inspector por localidad.

**Qué NO es.** No hay simulación. No hay tiempo. No hay red. Es la ciudad y la
población sintética en reposo, antes de que nada se mueva. Decirlo es parte del
producto.

## 3.1 Capas

| Capa | Qué dibuja | De dónde sale |
|---|---|---|
| **Población** | Coropleta por población de 18 años o más | `data/external/marginal_localidad_18mas.csv` (dato real, no simulado) |
| **Agentes** | 1.000 puntos, uno por agente sintético | `data/processed/poblacion_ecp2013.csv` v0.3-DI-M1 |
| **Opinión** | Coropleta por media de `opinion_t0`, con conmutador de escala | misma población |

## 3.2 Inspector

Al seleccionar una localidad: población 18+, peso en la ciudad, agentes
observados contra esperados (el diagnóstico territorial del muestreo, visible),
media de opinión, error estándar **con efecto de diseño**, diferencia con la
ciudad, una banda gráfica que muestra el margen de ruido sobre la escala 1–5, y
la composición por edad, sexo, estrato y nivel educativo.

La frase que aparece cuando la diferencia no es significativa —que es siempre—
no es un disclaimer al pie: es la conclusión de la ficha.

## 3.3 Decisiones de implementación

Están en el docstring de `src/viz/preparar_mapa.py`. Resumen:

- **DI-V1** — Geometría: capa `Localidad` del MapServer de la Unidad
  Administrativa Especial de Catastro Distrital, simplificada en el servidor a
  ~70 m y redondeada a 4 decimales (~11 m). Es resolución de pantalla. No sirve
  para calcular áreas ni para asignar manzanas.
- **DI-V2** — Los nombres de localidad vienen del marginal del proyecto, unidos
  por `COD_LOC`. El servicio geográfico los devuelve en mayúsculas y sin tildes;
  usar los suyos rompería el join con toda la tubería de población.
- **DI-V3** — **La posición de cada agente dentro de su localidad es
  arbitraria.** El modelo no tiene geografía por debajo de la localidad. Los
  puntos se sortean uniformemente dentro del polígono con semilla fija; no son
  domicilios, y la página lo dice en la leyenda y en el pie. Consecuencia
  visible y conocida: en Ciudad Bolívar, Usme y Suba los puntos se reparten
  también sobre la parte rural, donde no vive esa gente. Es el argumento más
  fuerte para el hito 3.
- **DI-V4** — El error estándar por localidad usa el efecto de diseño medido en
  la EPC (1,86), no muestreo aleatorio simple. Sin esa corrección las bandas
  saldrían ~36 % más angostas de lo que son.
- **DI-V5** — La escala de color de la capa de opinión se ancla al rango real de
  la pregunta (1 a 5), no al rango observado. Ver RV-1.
- **DI-V6** — La página es autocontenida: un solo archivo, sin peticiones de red
  salvo tipografías. Se abre desde el disco, se publica como artefacto o se
  sirve desde cualquier parte sin montar un backend. Principio 5: no se levanta
  PostgreSQL + PostGIS + FastAPI para dibujar 20 polígonos y 1.000 puntos.
- **DI-V7** — En la vista urbana se oculta Sumapaz: es el 78 % del área del
  Distrito y el 0,04 % de su población adulta, y dejarlo dibujado hunde la
  ciudad construida en una esquina del encuadre. El conmutador «Con Sumapaz»
  devuelve la forma real del Distrito, que también hay que poder ver.

## 3.4 Archivos

```
data/external/geo/localidades_bogota.geojson   geometría oficial simplificada (27 KB)
src/viz/preparar_mapa.py                       geometría + población → paquete de datos
src/viz/plantilla_mapa.html                    la página, con marcador /*__DATOS__*/
src/viz/construir_pagina.py                    plantilla + datos → archivo único
data/processed/viz/mapa_bogota.json            paquete de datos (69 KB)
data/processed/viz/mapa_bogota.html            la página lista (92 KB)
tests/test_viz_mapa.py                         12 pruebas
```

Reproducir de cero:

```
python3 src/viz/preparar_mapa.py
python3 src/viz/construir_pagina.py
python3 tests/test_viz_mapa.py
```

## 3.5 Qué verifican las pruebas

Estructura (20 localidades, códigos 01–20 completos, todas con nombre del
marginal), correspondencia agentes/localidad, **que ningún punto caiga fuera de
su polígono después de redondear** —si eso falla el mapa dibuja gente en la
localidad equivocada y el dibujo deja de ser verificable—, coherencia
estadística (la dispersión dentro supera a la de entre; el efecto de diseño
aplicado es el medido; la descomposición ruido/real cierra) y reproducibilidad
con semilla fija.

---

# 4. HITOS SIGUIENTES *(especificados, no construidos)*

## Hito 2 — El tiempo
Poner la serie de la EPC y de la ECP sobre el mapa y sobre una línea de tiempo:
qué se midió, cuándo, con cuántos casos y con qué margen. Sigue sin haber
simulación. Es el paso que convierte el mapa en un instrumento de lectura de los
datos reales que el proyecto ya cargó, y no cuesta modelo nuevo.

## Hito 3 — Geografía por debajo de la localidad
Es el hito que levanta DI-V3. Hay dos caminos y **no son equivalentes**:

- **UPZ** — hay geometría pública y hay proyecciones de población por UPZ en
  `data/raw/anexo-proyecciones-poblacion-bogota-desagreacion-loc-2018-2035-UPZ-2018-2024.xlsx`.
  Permite repartir agentes por peso poblacional real en vez de uniformemente, lo
  que arregla el problema visible del área rural.
- **Manzana** — Bogotá Cómo Vamos confirmó `MANZANA` en 6 olas de la EPC. Es el
  identificador de conglomerado del diseño muestral, **no** una coordenada, y
  vincularlo a geometría es un trabajo distinto y con implicaciones de
  confidencialidad que hay que tratar antes de tocarlo (R10).

Recomendación: UPZ primero. Es público, es suficiente para el problema visual y
no toca datos sensibles.

## Hito 4 — Los agentes en movimiento
Enganchar el motor de escenarios (`src/scenarios/`) al mapa: correr un escenario
declarado en YAML y ver la población cambiar en el tiempo. Aquí es donde la
advertencia de la sección 2 se vuelve crítica, porque una animación es mucho más
persuasiva que una tabla. Requisito de diseño: **el escenario nulo se dibuja
siempre al lado**, igual que el motor ya lo corre siempre.

## Hito 5 — La red
Dibujar la red social entre agentes. Es lo más vistoso y lo que menos sostiene
el proyecto: la red está medida (D15) pero **no explica** la dinámica observada
—siete experimentos pre-registrados lo dicen—. Si se dibuja, se dibuja como lo
que es: la estructura de contacto medida, no el mecanismo del cambio de opinión.

---

# 5. RESTRICCIONES QUE NO SE NEGOCIAN

1. **Nada de microdatos del CNC en una página.** R10 y el README de
   `data/raw/cnc/`. Solo agregados, con supresión bajo n<25 por celda y n<30 por
   estimación. La capa visual no cambia esa regla: la hace más fácil de violar,
   así que hay que revisarla en cada hito.
2. **Ningún agente sintético es una persona real**, y la página no puede sugerir
   lo contrario. DI-V3 existe por esto tanto como por rigor.
3. **RV-1** (sección 2) aplica a toda capa territorial de opinión.
4. **Toda cifra que aparece en pantalla tiene que poder rastrearse** hasta un
   archivo del repositorio. Si no se puede, no se muestra.

---

# 6. LO QUE ESTO NO RESUELVE

La capa visual **no** cierra ninguna pregunta abierta del modelo. Siguen
abiertas y siguen importando: A05 (el índice de confianza de la ECP promedia un
número variable de ítems — último defecto conocido de la tubería de población),
A06, A11 y A20 sin confirmar como D0X, A21 y A22 abiertas con Bogotá Cómo Vamos.

Que el proyecto se vea mejor no lo hace más cierto. Este documento existe en
parte para que esa frase quede escrita antes de que la página empiece a
convencer a nadie.
