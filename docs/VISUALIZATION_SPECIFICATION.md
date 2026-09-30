# VISUALIZATION SPECIFICATION — BOGOTÁ SOCIAL SIMULATOR

**Versión:** 0.21
**Fecha:** 29 de septiembre de 2026 · v0.21: 30 de septiembre (DI-V60)
**Estado:** Hito 1 completo. **Hito 2 completo** (24/09/2026): la línea de tiempo y el mapa por año, conectados; cuatro capas, todas responden al año, y una de ellas —Crecimiento— es la primera que **sí** puede afirmar geografía. Construirlo destapó DI-V45 — el error estándar analítico subestima el ruido territorial y el único año que parecía tener señal no la tiene. **Corrección del 25/09 (DI-V52):** la primera mitad de DI-V45 se sostiene; «no hay señal» no, porque la prueba que la sostenía no podía detectar señal. La capa de opinión sigue sin poder leerse por territorio, pero por otra razón: el donante no trae localidad. Hitos 3 a 5 especificados, sin construir. **29/09 — capa de Voto (DI-V53 a DI-V56):** la primera vuelta presidencial de 2014, 2018 y 2022 por localidad, un conteo completo que sí puede afirmar geografía, y «lo que el estrato no explica» (`GEOGRAFIA_ELECTORAL_RESULTS.md`).
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
| **Voto** *(29/09/2026)* | Coropleta por proporción de voto de un candidato, o por lo que el estrato no explica de ese voto | `data/processed/viz/voto_bogota.json` ← resultados de la Registraduría (D16) y `GEOGRAFIA_ELECTORAL_RESULTS.md` |
| **Base urbana** *(conmutador aparte)* | Vías arteriales y áreas verdes sobre la coropleta, con detalle progresivo | OpenStreetMap vía Overpass, extracto del 21/09/2026, ODbL |

Sobre las tres capas se navega: arrastre para mover, Ctrl + rueda o pellizco
para acercar, doble clic, botones `+` / `−` / «Ajustar», teclas `+` `−` `0` y
flechas, y un botón «Encuadrar» en la ficha de cada localidad.

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

### Capa base urbana (añadida el 21/09/2026)

El hito 1 dibujaba 20 polígonos sin nada dentro. Quien conoce Bogotá no
reconocía Bogotá: sin la Autopista Norte, la Caracas, la Boyacá ni el Simón
Bolívar, ubicar una localidad exigía sabérselas de memoria. La capa base
resuelve ese problema concreto y **ninguno más**. Se dibuja por encima de la
coropleta, por debajo de los agentes, apagada por defecto, sin eventos de
puntero y sin ninguna etiqueta de OpenStreetMap en el paquete: no se puede
hacer clic sobre ella porque no hay nada que consultar.

- **DI-V8** — Fuente: OpenStreetMap vía Overpass, extracto del 21/09/2026,
  bajo ODbL. La atribución va en el pie de la página; es obligación de la
  licencia, no cortesía. Los archivos crudos quedan versionados en
  `data/external/geo/osm/` para que el paquete se reproduzca sin volver a
  consultar Overpass.
- **DI-V9** — Simplificación Douglas-Peucker a 0,0002° (~22 m) en vías y
  0,00015° (~17 m) en polígonos, y redondeo final a cuatro decimales (~11 m),
  la misma resolución que DI-V1. Es resolución de dibujo: **esta capa no sirve
  para medir distancias, áreas ni accesibilidad.**
- **DI-V10** — Overpass devuelve las vías partidas en cada cambio de etiqueta:
  5.429 tramos en el extracto. Antes de simplificar se reencadenan por extremo
  compartido y quedan **178 polilíneas**. Sin ese paso el paquete pesa diez
  veces más y Douglas-Peucker no tiene nada que simplificar dentro de un tramo
  de dos puntos.
- **DI-V11** — El recorte es por caja envolvente de las 19 localidades urbanas
  más 0,01°, **no por el límite político del Distrito**. Consecuencia
  deliberada: dentro del encuadre se ven vías y parques de Soacha, Mosquera,
  Funza y Chía. La ciudad no se acaba en el borde de Bogotá; fingir que sí es
  peor que mostrarlo. La página dice que la capa base es regional y que lo
  único que delimita el Distrito son los polígonos de localidad.
- **DI-V12** — Se descartan las áreas verdes menores de 2 ha: a la escala de la
  ciudad entera un parque de barrio mide menos de tres píxeles y solo aporta
  ruido visual. De 4.189 polígonos del extracto quedan 206.
- **DI-V13** — Codificación delta en enteros de 1e-4 grados. Un punto pasa de
  18 caracteres a 3 y el paquete de ~120 KB a 30 KB, sin perder un solo punto.
  La página lo decodifica sumando.
- **DI-V15** — Detalle progresivo. Las vías `trunk` y las áreas verdes de 2 ha
  o más se dibujan siempre; `primary` y los parques de 0,5 a 2 ha aparecen al
  pasar de ×2,6. No es solo peso de archivo: a escala de ciudad entera las 129
  polilíneas de `primary` se cruzan entre sí y tapan la coropleta, que es el
  dato. El detalle aparece cuando hay resolución para leerlo, y por la misma
  razón la capa base sube de opacidad al acercar: de lejos tiene que ceder
  ante el color, de cerca el color es plano y lo único que informa es la calle.
- **DI-V14** — Si falta una de las tres capas de origen, el preparador no
  falla: emite esa capa vacía y lo declara en los metadatos. **Hoy falta
  `agua.geojson`** —llegó pegado como texto en el chat, no como archivo— así
  que la capa de agua va vacía. El agua es la capa que más ayuda a reconocer
  Bogotá (el río Bogotá, el Fucha, el Tunjuelo, los humedales de Tibabuyes y
  Córdoba); el código ya la dibuja, solo falta dejar el archivo en
  `data/external/geo/osm/agua.geojson` y volver a correr el preparador.

### Navegación (añadida el 22/09/2026)

Sin zoom, la capa base era desperdicio: se cargó geometría a 22 m para
dibujarla a una escala donde una arteria mide un píxel. El mapa ahora se
arrastra y se acerca hasta ×24, con barra de escala, encuadre por localidad y
control por teclado.

- **DI-V17** — El zoom se hace moviendo el `viewBox`, no con un `transform`
  sobre un grupo. Así los trazos con `vector-effect: non-scaling-stroke`
  siguen midiéndose en píxeles de pantalla y no hay que compensar nada a mano;
  los puntos de agente y las etiquetas se reescalan explícitamente para
  conservar su tamaño en pantalla, porque si crecieran con el zoom acercarse
  no separaría nada.
- **DI-V18** — El lienzo tiene altura propia (`clamp(440px, 74vh, 880px)`) y
  **ya no toma la forma del *bounding box* de la ciudad**. Bogotá urbana es un
  corredor norte-sur larguísimo: atar la altura del panel a esa forma producía
  un lienzo de 1.500 × 3.800 px en el que, al acercar, solo se veía una franja
  vertical. El encuadre inicial se calcula para caber dentro del lienzo, y el
  rectángulo resultante —el «mundo»— es a la vez el tope del alejamiento y el
  límite del paneo: la ciudad no se puede perder de vista.
- **DI-V16** — La rueda sola **no** hace zoom: deja scrollear la página. El
  zoom pide Ctrl (o ⌘), que es además lo que el navegador envía cuando alguien
  hace el gesto de pellizco en un trackpad, así que el gesto natural funciona
  sin saber la tecla. Atrapar la rueda a secas es de las cosas que más
  molestan de un mapa embebido, y aquí el mapa es una columna dentro de un
  documento que se lee de arriba abajo. Quien prefiera no usar modificadores
  tiene doble clic y los botones `+` / `−`.
- **DI-V19** — Un arrastre que termina encima de una localidad no cuenta como
  clic. Sin ese guardia, mover el mapa cambiaría la selección cada vez.
- **DI-V20** — **El acercamiento se usa para enseñar DI-V3, no para taparlo.**
  A partir de ×5, con la capa de agentes activa, la leyenda dice que hay
  puntos sobre el aeropuerto, sobre el río y sobre el área rural, y explica
  por qué: el modelo no tiene geografía por debajo de la localidad. Es el
  mismo criterio de la sección 2 —enseñar el error es más eficaz que
  esconderlo— aplicado a la herramienta que más podría disimularlo. El zoom
  hace que la página parezca más precisa; esta es la contrapartida que lo
  compensa.

### Una sola identidad visual (22/09/2026)

El proyecto tiene **dos modos de mirar**, no dos identidades:

| | Para qué | Color |
|---|---|---|
| **Tablero, vista Datos** | Leer población y opinión con sus márgenes | Codifica: la rampa *es* el dato |
| **Tablero, vista Ciudad** · **pósters** | Mirar y reconocer Bogotá | No codifica nada |

- **DI-V24** — La identidad del tablero es la paleta **«Páramo»**: verde de
  los cerros sobre papel de sabana (`#e9ece7` en el lienzo, `#f7f9f6` en los
  paneles, tinta `#16211c`, acento teja `#b2452c`). La vista Ciudad y los
  pósters conservan la paleta de prettymaps, y ese salto de color es
  precisamente lo que marca el cambio de modo: de leer a mirar.

  Se eligió tras renderizar cuatro candidatas sobre el mapa real —Páramo,
  Ladrillo a la vista, Bandera del Distrito y Cielo de sabana—, validando cada
  una contra su propio papel. Decidir viendo y no por nombres de color es
  parte del método: las cuatro eran legales, así que la elección fue de gusto,
  y eso solo se sabe después de comprobar que ninguna era ilegible.
- **DI-V25** — Las rampas **se rediseñaron y se validaron contra el papel
  nuevo**, no se ajustaron a ojo. La secuencial de población es de un solo
  tono (vino, OKLCH H=18) con lightness monótona y paso mínimo de 0,06. La
  divergente de opinión son dos brazos de un tono cada uno —índigo y
  terracota— con un **gris neutro** en el centro, que es lo que separa una
  divergente legítima de un arcoíris. El requisito que obligó a rehacerlas
  enteras: sobre un fondo de color, el extremo claro tiene que despegarse del
  papel (≥ 2:1).

  **Este check destapó un defecto que el tablero llevaba desde el hito 1.** La
  rampa verde original arrancaba en `#e9eee8` sobre un papel `#e9ece7`: un
  contraste de **1,01:1**. La localidad menos poblada no era el extremo claro
  de una escala, era un agujero en el mapa — y nadie lo notó en meses, porque
  el ojo rellena el hueco con el contorno. La rampa verde de hoy arranca en
  `#87b099` y da 2,02:1; la divergente, 3,5:1 o más en cada brazo. «Sin dato»
  tiene su propio gris a 2,17:1, porque una localidad sin medición tampoco
  puede confundirse con el fondo.
- Los agentes pasan al coral `#FF5E5B` del preset, el único acento saturado
  del lienzo, y «sin dato» tiene su propio gris: una localidad sin medición
  —La Candelaria— no puede confundirse con el fondo.

**Lo que no cambió, y es el punto:** la capa de opinión sigue viéndose casi
plana, con todas las localidades alrededor del gris del centro. El rediseño de
la paleta no tapó la conclusión de la sección 2; si la hubiera tapado, estaría
mal hecho.

- **DI-V26** — El paneo **no** usa `setPointerCapture`. Capturar el puntero en
  el `<svg>` hace que el evento `click` se dispare sobre el `<svg>` y no sobre
  el `<path>` de la localidad: el mapa se movía pero el inspector dejaba de
  abrirse. El arrastre se sigue en `window` en su lugar, que da el mismo
  comportamiento fuera del lienzo sin quitarle el clic a nadie.

  *Y una lección de método que vale más que el arreglo:* el defecto vivió tres
  versiones porque las pruebas disparaban el clic con `dispatchEvent`, que se
  salta `pointerdown` por completo. Una prueba que no pasa por el mismo camino
  que el usuario no está probando lo que el usuario hace. Las pruebas de
  interacción ahora usan clics reales.

- **DI-V27** — En la vista Ciudad las localidades **siguen siendo
  consultables**. El aviso de que «el color no codifica nada» se refiere al
  relleno del mapa, no al inspector: la ficha de la derecha —población,
  composición, media de opinión con su banda de error— es la misma en las dos
  vistas. Por eso el límite punteado tiene presencia suficiente para verse y
  para invitar al clic, y hay realce al pasar el cursor: si algo se puede
  pulsar, tiene que parecerlo.

- **DI-V23** *(revisada el 22/09/2026)* — La vista «Ciudad» adopta la paleta
  exacta del preset `barcelona` de prettymaps (papel `#F2F4CB`, verde
  `#8BB174`, agua `#a8e1e6`, tinta `#2F3737`) y **nada más**: es la misma
  herramienta con otro papel. Las tres capas de dato —población, agentes,
  opinión— funcionan igual en las dos vistas.

  **En Ciudad las localidades van sin relleno de dato:** se pintan del color
  del papel, así que siguen siendo objetivo de clic —un `fill:none` solo
  respondería en el borde— pero no se ven, y lo que queda es el trazado urbano.
  La capa de agentes sí funciona, porque son puntos y no relleno; los botones
  de Población y Opinión se ocultan en esta vista, ya que sin coropleta no
  pintarían nada y un botón que no hace nada visible es peor que un botón
  ausente. El verde oliva de los parques baja a 0,55 de opacidad y el agua a
  0,7 para que la base no se coma el papel.

  Esta decisión fue de ida y vuelta, y vale la pena dejar el recorrido: primero
  Ciudad aplanaba la coropleta y escondía los controles; luego se le devolvieron
  las tres capas de dato; y finalmente se le quitó el relleno otra vez, esta vez
  porque **se veía mal**, no por un argumento metodológico. El resultado se
  parece al primero, pero la razón es distinta y el mecanismo también: las
  localidades no están «aplanadas a un relleno neutro», están sin pintar.

- **DI-V31** — Se eliminó el conmutador «Base urbana». La capa base está
  siempre, y su presencia la gradúan el zoom (DI-V15) y la vista. Un botón que
  el usuario lee como equivalente a otro botón es un botón de más.

- **DI-V32** — La localidad seleccionada se marca con un trazo verde `#0e9b62`
  sobre un halo del color del papel, en un grupo propio por encima de la capa
  base. **En la vista Ciudad se añade un tinte** `rgba(72,187,128,.28)`, que es
  el único color de esa vista; se dibuja **debajo** de la capa base, para que
  tiña la localidad sin tapar sus vías ni sus parques — que es lo que lo hace
  translúcido de verdad y no solo transparente. En Datos no hay tinte: sobre la
  coropleta alteraría el color que lleva el dato. Dos razones, las dos medidas: un trazo verde *de la rampa* sobre una
  coropleta verde no se ve —el mejor candidato daba 1,06:1 contra el paso más
  oscuro—, y si la marca fuera el borde del propio polígono, las localidades
  vecinas y las vías se dibujarían encima y se la comerían a medias.
- **DI-P11** (en `src/viz/poster.py`) — Los pósters usan los presets de
  prettymaps **tal cual**, sin adaptarlos a la paleta del proyecto. Son dos
  identidades visuales a propósito: una para leer y otra para mirar.
- **DI-P12** — La zona «ciudad» del generador de pósters no puede usar un
  preset sin tocarlo: con 11 km de radio, pedir las huellas de edificios son
  cientos de miles de polígonos y Overpass se cae por tiempo de espera. Se
  dibuja sin edificios y con el agua añadida, que a esa escala es lo que
  estructura la ciudad.

El límite de localidad se dibuja punteado en la vista Ciudad. Compite con las
vías —ambos son líneas oscuras y finas— y además no es un objeto de la ciudad
sino una convención administrativa; el punteado dice eso sin tener que
explicarlo.

### Movimiento (22/09/2026)

El tablero anima **cuatro cosas y ninguna más**. El criterio no es estético: a
más veces se ve algo, menos puede moverse, porque el movimiento que sorprende
la primera vez estorba la centésima.

| Qué | Por qué | Cuánto |
|---|---|---|
| Salto de cámara por clic en `+`/`−`/«Ajustar»/«Encuadrar»/doble clic | Evitar el teletransporte: sin puente, al encuadrar una localidad se pierde la referencia de dónde estaba | 240 ms, `cubic-bezier(0.23, 1, 0.32, 1)` |
| Pulsación de botón | Confirmar que el botón oyó | `scale(.97)`, 120 ms |
| Relevo del panel inspector | Veinte filas cambian a la vez; sin puente el ojo pierde el hilo | opacidad, 140 ms |
| ~~Conmutar Datos ↔ Ciudad~~ | **Retirada.** Ver DI-V33 | — |

- **DI-V28** — **La rueda, el arrastre, el pellizco y el teclado NO se
  animan.** Los tres primeros siguen el gesto 1:1: cualquier suavizado se
  percibe como retraso. El teclado se excluye por frecuencia — una tecla que se
  repite se vuelve lenta si cada pulsación arrastra una animación de por medio.
  Tocar el mapa o girar la rueda **cancela** el salto en curso: el gesto manda.
- **DI-V29** — El `viewBox` no es animable por CSS, así que se interpola a
  mano. El reloj es una animación WAAPI sobre un elemento desconectado, de la
  que solo se lee el progreso: da la curva exacta del navegador sin implementar
  un bézier propio, y es cancelable. Durante la interpolación no se vuelve a
  pintar la leyenda — reescribir su HTML sesenta veces por segundo es justo el
  tipo de coste que hace que una animación se sienta pesada.
- **DI-V33** — **La transición de paleta al conmutar de vista se retiró.**
  Costaba más de lo que arreglaba, y el camino hasta entenderlo vale la pena
  dejarlo escrito:

  1. Con `transition` sobre los ~1.400 paths de la capa base, el navegador
     tenía que interpolar 1.400 colores a la vez y el cambio de vista tardaba
     **segundos** en aparecer.
  2. Reducida a un solo nodo, el papel seguía sin cambiar: se transicionaba el
     atajo `background`, que arrastra `background-image`, `-position` y
     `-size`, y Chromium deja el valor atascado en el color viejo hasta que
     algo fuerza un recálculo. *«Nombra las propiedades exactas» no era una
     regla de estilo, evitaba esto.*
  3. Ya con `background-color`, quedaba un desfase visible: añadir la clase al
     contenedor obliga a recalcular el estilo de ~2.500 nodos del SVG, y ese
     trabajo retrasa el arranque de la transición.

  Conmutar de vista es un cambio de modo, y que salte es correcto. A veces la
  mejor animación es ninguna.

- **DI-V34** — **La página no describe la variable: la copia.** Durante todo el
  Hito 1 el tablero publicó una coropleta y un inspector llenos de números
  entre 1 y 5 sin decir en ninguna parte qué medían. Alguien que llegara a la
  página podía leer «2,81 / 5» y no tener forma de saber si era confianza,
  aprobación, ideología o satisfacción, ni en qué dirección, ni de qué encuesta
  ni de qué año. Es exactamente el defecto que §31 de PROJECT_CONTEXT advierte
  para los mapas, aplicado a la leyenda en vez de al color.

  La ficha (`escala_opinion`) se escribe **una sola vez**, en el metadata de la
  población que produjo `opinion_t0`; `preparar_mapa.py` la copia al paquete y
  la página la formatea. No hay texto descriptivo escrito a mano en la
  plantilla. La razón es concreta: el pipeline sirve tres donantes —ECP,
  EPC/Bogotá Cómo Vamos y Veeduría— y con el donante EPC la variable **no es
  confianza institucional**, es evaluación de gestión del alcalde. Una
  descripción escrita en el HTML seguiría diciendo «confianza» el día que se
  cambie el donante, y nadie se daría cuenta. Si el paquete no trae la ficha,
  el bloque no se dibuja: mejor sin ficha que con una inventada.

  La ficha publica la pregunta textual, las anclas verbales (*1 = no confía,
  5 = confía mucho*), la rampa, cómo se construye el índice, **la distribución
  del denominador** (POPULATION_SPECIFICATION §8.4), las 13 instituciones
  evaluadas y una línea de *lo que no es*: un 3,0 es el punto medio de la
  escala, no «30 % de confianza». Va en un `<details>` cerrado —no empuja el
  mapa hacia abajo— pero siempre presente, no escondido detrás de un modal.

- **DI-V35** — Las anclas verbales solo acompañan a los extremos **cuando son
  los extremos reales de la pregunta**. Con «Escala al rango» activada los topes
  son 2,54 y 3,23, y poner «no confía» junto a un 2,54 sería mentir con más
  énfasis que el propio estirado de color. Por la misma razón el 1 y el 5 se
  imprimen sin decimales en la escala real —«1,00» sugiere una precisión que la
  pregunta no tiene— y con dos decimales en la estirada, donde hacen falta.

- **DI-V36** — **La coropleta de población nunca fue lineal, y la leyenda decía
  que sí.** El color se calcula con `Math.sqrt(población / máximo)` desde el
  Hito 1. La leyenda imprimía `0 ————— 991.096` y nada más, así que la única
  lectura disponible era la proporcional, y era falsa:

  | localidad | población | proporción real | dónde caía el color |
  |---|---|---|---|
  | Kennedy | 852.417 | 86 % | 93 % |
  | Los Mártires | 59.740 | 6 % | 25 % |
  | La Candelaria | 14.082 | 1,4 % | 12 % |

  **La raíz se queda.** No es un adorno: sin ella las quince localidades por
  debajo de 300.000 personas caen todas en el mismo verde claro y el mapa deja
  de distinguir Sumapaz de Los Mártires, que se diferencian en veinte veces. La
  compresión de la cola es exactamente lo que hace legible un mapa de conteos
  sobre áreas de tamaño muy desigual. Lo que no se queda es la leyenda que la
  ocultaba: ahora lleva marcas en 50.000, 200.000 y 500.000, **colocadas con la
  misma transformación que pinta el color**, de modo que la curvatura se ve en
  el espaciado de las marcas, y el texto dice «color en escala de raíz».

  La decisión de implementación que importa es la otra: la transformación tiene
  ahora un nombre (`tPob`) y **un solo cuerpo**, que consumen el color y la
  leyenda. Mientras fueran dos expresiones separadas, cualquiera podía cambiar
  una y dejar el mapa contradiciendo su propia leyenda sin que nada fallara. La
  prueba comprueba justamente eso: que `Math.sqrt` aparezca **una sola vez** en
  toda la página.

  Es el mismo defecto que DI-V34, en la otra capa: una rampa que no dice cómo
  se lee. Que aparecieran los dos el mismo día, uno buscando el otro, sugiere
  revisar cada codificación visual con la misma pregunta — *¿un lector puede
  saber cómo se convierte el dato en el color?*— antes de agregar capas nuevas.

- **DI-V41** — **Decisiones del gráfico de la serie** (`dibujarSerie`, Hito 2).
  Las cuatro que no son obvias:

  1. **Los dos colores se validaron, no se eligieron mirando.** El verde
     `--paramo` del proyecto falla el piso de croma (C = 0,066: a ese nivel un
     tono deja de hacer trabajo de identidad y se lee como gris) y su
     separación bajo protanopía contra el `--teja` es ΔE 7,1, dentro de la
     banda que solo es admisible con codificación secundaria. Los que quedaron
     —`#14588a` y `#b8531f` en claro, `#3f92cc` y `#d4713f` en oscuro— pasan
     las cinco comprobaciones, con ΔE 19,8 bajo protanopía y 25,6 en visión
     normal. Los pasos oscuros son propios, no una inversión automática.
  2. **Y aun así cada serie lleva su forma**: círculo la ECP, cuadrado la EPC.
     Impreso en gris o en una pantalla mala, el color es lo primero que se
     pierde; la forma no.
  3. **El área de clic mide 28 px y el punto 9.** La primera versión ponía el
     marcador encima del área, así que apuntar *bien* al punto era lo único
     que no funcionaba: el dibujo interceptaba el puntero. `pointer-events:none`
     en el marcador.
  4. **La lectura no es un globo flotante**, es un bloque fijo bajo el gráfico
     con `aria-live`. Se llega con el tabulador, no se escapa al mover el
     ratón, y la tabla de «Ver los números» deja los valores copiables sin
     cursor de por medio. Un globo habría sido más vistoso y menos usable.

  El eje vertical va de 1 a 5 por defecto, con el mismo botón de «Escala al
  rango» que el mapa y por la misma razón (§31): con la escala real el gráfico
  se ve tranquilo, y esa tranquilidad es el dato.

- **DI-V43** — **Las cinco olas son la misma muestra**, y eso es lo que hace
  que el mapa por año signifique algo. Las cinco poblaciones se construyen con
  la misma semilla y el mismo método, así que los 1.000 agentes son las mismas
  1.000 personas sintéticas en 2013 y en 2023 y lo único que cambia entre años
  es `opinion_t0` (verificado: las seis columnas demográficas son idénticas
  entre olas). Tres consecuencias: la geometría, las posiciones de los puntos y
  la composición por localidad se guardan una sola vez —el paquete pasa de 71 a
  98 KB para cinco años, no a 355—; cualquier diferencia que el lector vea
  entre dos años es del dato y no del sorteo; y `preparar_mapa.py` **verifica**
  esa identidad en vez de confiarse, porque compartir posiciones entre
  poblaciones distintas dibujaría a una persona de Suba en Kennedy sin que nada
  avisara.

- **DI-V44** — El ruido se recalcula por año y la página lo muestra al cambiar
  de año. El mapa por año es exactamente el gráfico que §31 advierte: cinco
  cortes que parpadean y parecen movimiento territorial.

- **DI-V45** — **El error estándar analítico subestima el ruido territorial.**
  Es el hallazgo del Hito 2, y apareció construyéndolo.

  Desde el Hito 1 el proyecto descomponía la dispersión entre localidades con
  `sd_ruido² = promedio(ee²)`, con `ee = sd/√n · √DEFF` (DI-V4). Esa fórmula
  supone que las 1.000 opiniones son extracciones independientes. **No lo son.**
  El hot-deck empareja por celda demográfica y el desempate ponderado de DI-M1
  permite que dos agentes de la misma celda reciban el valor del **mismo**
  encuestado. Los agentes de una localidad comparten celdas más que dos agentes
  cualesquiera, así que la opinión queda agrupada por localidad **por
  construcción**, y ese agrupamiento no entra en `ee`.

  Se vio en la ECP 2021, el único año que parecía distinto:

  | | analítico (DI-V4) | medido (20 semillas) |
  |---|---|---|
  | dispersión entre localidades | 0,341 | 0,341 |
  | ruido | 0,246 (52 %) | rango 0,148–0,515, p95 = 0,413 |
  | «dispersión real» | **0,236** | **ninguna** — percentil 85 del propio piso |

  Rehaciendo el pipeline con otras semillas —mismo año, mismos datos, mismo
  método—, la dispersión entre localidades de 2021 recorre 0,148 a 0,515. La
  corrida publicada vale 0,341. No hay señal territorial: hay una semilla
  afortunada. Y lo mismo, sin excepción, en los cinco años.

  **Una prueba de permutación no sirve para esto, y se intentó.** Remezclar la
  opinión entre agentes rompe a la vez el vínculo localidad→demografía **y** el
  agrupamiento del hot-deck, así que da p = 0,0005 para un efecto que no
  existe. El null correcto conserva las dos cosas y solo cambia la semilla. Es
  la misma lección de §8.3 de POPULATION_SPECIFICATION en otra forma: *el piso
  de ruido de un pipeline se mide rehaciéndolo, no derivándolo.*

  `src/viz/piso_territorial.py` lo mide, `piso_territorial.json` lo transporta y
  **la página usa ese, no el analítico**, para cualquier afirmación territorial.
  El analítico se conserva en el paquete porque sigue siendo el que corresponde
  a las barras del inspector de cada localidad, renombrado a
  `fraccion_ruido_analitica` para que nadie lo vuelva a usar por descuido. La
  prueba exige que el piso medido sea mayor que el analítico: si algún día
  dejara de serlo, el argumento estaría al revés y habría que revisarlo.

- **DI-V46** — **El año es un solo estado, con una sola puerta.** `C()` y
  `opDe()` son las únicas dos formas de leer un dato de opinión, las dos son
  funciones del año seleccionado, y `irAlAnio()` es el único camino para
  cambiarlo —lo usen los botones de la barra o un clic en la línea de tiempo—.
  La prueba comprueba lo contrario de lo habitual: que **no** queden en la
  página lecturas de `D.ciudad.`, `l.opinion_media` ni `l.opinion_ee`, que son
  las formas sin año. Con dos caminos, media pantalla acabaría mostrando 2013 y
  la otra media 2021, y nadie lo notaría hasta que los números no cuadraran.

  Solo los puntos de la serie **ECP** llevan al mapa a su año: son los cinco con
  población sintética. Un punto de la EPC que moviera el mapa haría creer que el
  mapa colorea gestión del alcalde, y no la colorea.

- **DI-V47** — **La capa de Agentes sí colorea por opinión, y la coropleta no
  puede.** Son la misma variable y admiten lecturas distintas: la media de
  ciudad recorre 2,81 → 2,24 sobre márgenes de ±0,03, así que el cambio entre
  años es señal robusta; la variación *entre localidades* dentro de un año no
  supera el piso (DI-V45). Por eso los 1.000 puntos se colorean por la opinión
  individual —donde el movimiento es real y se ve— mientras la coropleta carga
  la advertencia. Es la distinción que el tablero tiene que enseñar, no
  esconder: **el tiempo se puede leer, la geografía no.**

- **DI-V48** — **Los dos marginales viven separados.** Al hacer que la capa de
  población respondiera al año apareció una ambigüedad que no existía antes:
  «población de la localidad» pasa a significar dos cosas.

  `marginal_localidad_18mas.csv` es el objetivo del muestreo PPS (D14): la
  revisión DANE-SDP de 2025, uno solo, y es contra ese que se sortearon los
  1.000 agentes. La columna «esperados» sigue siendo de ese marginal y de
  ningún otro, porque describe **el sorteo**, no la ciudad — y el inspector
  ahora lo dice en la propia fila.

  `marginal_localidad_18mas_serie.csv` es población 18+ por localidad y año, y
  existe **solo para dibujar**. Si la serie hubiera reemplazado al marginal de
  muestreo, cada corrida de la población tendría que elegir un año y
  «esperados» dejaría de significar lo mismo entre corridas.

  Lo produce `extraer_columnas_em2021.py marginal-serie`, que reutiliza el
  mismo lector que `proyecciones` —el que excluye la fila agregada de Bogotá,
  verifica que las 20 localidades sumen ese agregado y cruza los nombres contra
  D12— en vez de volver a parsear el archivo.

- **DI-V49** — La rampa verde se ancla al máximo de **todos** los años, no al
  del año en pantalla. Reescalarla año a año haría que el mapa se viera
  idéntico en los cinco y escondería lo único que cambia.

- **DI-V50** — **Y aun así la coropleta de población casi no se mueve. Se midió
  después de construirla, y el resultado se publica en vez de disimularse.**

  Diferencia máxima de color entre 2013 y 2023: **13 sobre 255 por canal**. Lado
  a lado, los dos mapas se ven iguales. No es un defecto de implementación, es
  el dato:

  | | |
  |---|---|
  | crecimiento de Bogotá 18+, 2013→2023 | **+16,4 %** |
  | movimiento del reparto entre localidades (L1) | **0,0201** |
  | recorrido sobre la rampa (√1,164) | **+8 %** |

  Crece el total, no el reparto — y la rampa dibuja el reparto. La raíz
  cuadrada de DI-V36 comprime lo que queda, y las localidades grandes ya están
  cerca del extremo oscuro sin a dónde oscurecerse.

  Lo que sí cambia de forma legible son las **cifras**: 5.221.648 en 2013 contra
  6.077.736 en 2023, en el encabezado y en el panel. Así que el paquete lleva
  `poblacion_resumen` y **la leyenda lo dice**: *«el color apenas se mueve entre
  años, y eso es el dato»*. Un control que hace algo invisible no es mucho mejor
  que uno que no hace nada; lo que lo salva es nombrar lo invisible.

  **Lo que sí es visible está en DI-V51**: una capa de *crecimiento* en vez de
  nivel, construida el mismo día.

- **DI-V51** — **La capa de Crecimiento, y por qué esta sí puede afirmar
  geografía.**

  Es la contracara de DI-V45 y por eso vale la pena tenerlas juntas en el mismo
  tablero. La coropleta de *opinión* no puede sostener una lectura territorial
  porque la variación entre localidades no supera el ruido que el propio
  pipeline produce. La de *crecimiento* sí puede, y la razón no es que sea más
  bonita: **son proyecciones oficiales de población, no estimaciones de una
  muestra**. No traen error de muestreo que descontar. Dos capas, dos permisos
  distintos — y el aviso de cada una lo dice con esas palabras.

  Cinco decisiones:

  1. **Rampa propia, no la de opinión.** Reusar `RAMPA_OP` habría hecho que un
     azul significara «poca confianza» en una capa y «pierde población» en
     otra. Los polos son teal `#008f89` ↔ ocre `#ab5e00`, validados contra el
     lienzo: ΔE 14,3 bajo deuteranopía y 21,3 en visión normal, con croma,
     banda de luminosidad y contraste en verde. Frío = pierde, cálido = gana,
     la misma dirección que `RAMPA_OP`, para no obligar a reaprender el mapa.
  2. **Dominio simétrico ±máximo, con el gris exactamente en el 0.** Un dominio
     asimétrico (de −2,1 % a +26,9 %) habría usado toda la rampa y pintado a
     Barrios Unidos, con su −2,1 %, tan saturado como a Usme con su +24,2 %.
     Con el dominio simétrico un −2 % se ve casi neutro, que es lo que es.
  3. **Acumulado desde el año base, no interanual.** En 2013 el mapa está
     neutro en todas partes y la leyenda lo explica en vez de dejar que parezca
     un error. Avanzando de año se ve la divergencia acumularse, que es la
     lectura interesante.
  4. **El dominio es el mismo en los cinco años** — DI-V49 otra vez. Reescalarlo
     por año haría que todos los cortes se vieran igual de contrastados y la
     acumulación sería invisible.
  5. **El aviso da el cambio absoluto además del porcentaje**, y se calcula de
     los mismos datos que colorean el mapa, no de una cifra precalculada.
     Importa: por porcentaje el titular es Sumapaz (+26,9 %), que son **559
     personas** sobre 2.078. El mayor aumento real es Suba, con 162.884 sobre
     808.093, y el mapa lo pinta con el mismo tono que a Sumapaz. El porcentaje
     premia a las localidades chicas; decirlo es más barato que construir una
     codificación que lo resuelva.

- **DI-V52** — **Corrección de DI-V45: el piso por semillas no es una prueba de
  señal.** *(25/09/2026. DI-V45 se conserva arriba sin editar, por la regla de
  PROJECT_CONTEXT §45.)*

  DI-V45 hizo dos afirmaciones. La primera se sostiene: el `ee` analítico
  subestima cuánto varía `sd_entre` de una corrida a otra, y rehacer la
  población con 20 semillas lo mide bien — en 2021 la cifra recorre 0,148 a
  0,515, así que una sola corrida no es una medida estable.

  **La segunda no se sostiene:** que «la corrida publicada cabe dentro del
  piso» signifique «no hay señal territorial». Las 20 semillas no son un null
  sin fenómeno: salen del mismo proceso que la corrida publicada, con los
  mismos datos, y la primera de ellas *es* la publicada. Un valor comparado
  contra la distribución de la que salió cae en un percentil uniforme, así que
  supera el p95 alrededor del 5 % de las veces **haya o no efecto, y sea del
  tamaño que sea**. Los percentiles publicados —25, 10, 10, 85 y 35— son
  exactamente lo que se espera de un criterio que no mide nada.

  Se verificó con una ciudad simulada con efecto por localidad conocido
  (`src/viz/simular_prueba_piso.py`):

  | efecto real (sd entre localidades) | lo «detecta» el criterio del piso | lo detecta una permutación |
  |---|---|---|
  | 0 | 3 % | 2 % |
  | 0,1 | 2 % | 23 % |
  | 0,2 | 2 % | 88 % |
  | 0,4 | 5 % | 100 % |
  | 0,8 | 4 % | 100 % |

  Tres consecuencias:

  1. **La permutación que DI-V45 descartó no estaba equivocada.** Su
     p = 0,0005 detectaba estructura por localidad real *en la población
     sintética*. Lo que no puede decir es de dónde viene esa estructura.
  2. **Y de dónde viene sí se sabe, sin prueba:** el donante (ECP) no registra
     la localidad, así que la única vía por la que la opinión sintética difiere
     entre localidades es su **composición demográfica** —edad, sexo,
     educación, estrato—. Es una consecuencia del método, no una medición de
     Bogotá. Esa es la razón válida por la que la capa de opinión no se lee por
     territorio, y es más sólida que la anterior porque no depende de ningún
     umbral. DI-V47 («el tiempo se puede leer, la geografía no») sigue en pie
     con esta justificación.
  3. **Para A08:** con el criterio anterior, ni 100.000 agentes habrían hecho
     «aparecer» señal — el percentil seguiría siendo uniforme. Cualquier
     comparación de tamaños de población necesita otro criterio: comparar la
     diferencia por composición contra la incertidumbre del **donante**, que es
     la que no baja al escalar.

  **Qué cambió en el código.** La página ya no lee `hay_senal_territorial`: la
  cifra del encabezado muestra el rango por semilla como medida de
  estabilidad, y el aviso de la capa de opinión y el de Crecimiento dan la
  razón de fondo (el donante no trae localidad). `piso_territorial.py` y
  `preparar_mapa.py` conservan el cálculo y el nombre del campo para no romper
  el paquete, con la corrección escrita en su docstring; la conclusión que
  emite el script dejó de afirmar nada sobre señal. En las pruebas se retiró
  «ningún año se sale de su piso — el mapa no puede afirmar geografía», que
  convertía el resultado circular en afirmación, y se añadió una que impide que
  la página vuelva a leer ese campo.

  **La lección, y es la misma de DI-V45 dada vuelta:** *un null tiene que
  poder fallar.* Rehacer el pipeline mide bien la variabilidad; no sirve como
  null de «sin efecto» si el efecto viaja dentro del mismo pipeline.

- **DI-V30** — El `:hover` de los botones se gatea con
  `@media (hover: hover) and (pointer: fine)`. En táctil, un toque dejaba el
  estado de hover pegado hasta tocar otra cosa.
- Con `prefers-reduced-motion: reduce` no hay interpolación de cámara ni
  fundido de panel: el estado salta al destino. Reducir movimiento es tener
  menos, no tener cero — las transiciones de color se conservan.

**Lo que se descartó, y es la parte que importa:** animar la coropleta al
cambiar de capa más allá de lo que ya hacía, la entrada escalonada de las 20
localidades, la aparición de los 1.000 agentes, y el dibujado progresivo de la
banda de error. Todos son dato que alguien está leyendo. Un tablero que se
mueve mientras lo lees es peor tablero, por bonito que se vea la primera vez.

Dos defectos que la navegación dejó a la vista y quedaron corregidos:

- **DI-V21** — Los colores del lienzo dejan de seguir al tema del sistema. Las
  rampas de la coropleta son RGB fijos, así que no cambian en modo oscuro;
  todo lo que se dibuja encima —bordes de localidad, etiquetas, vías, verde,
  agua, barra de escala— seguía a `--ink` y `--surface` y en modo oscuro
  quedaba claro sobre relleno claro. Ahora hay cinco variables de lienzo
  (`--lienzo-borde`, `--lienzo-tinta`, `--base-via`, `--base-verde`,
  `--base-agua`) que se definen una sola vez y no se redefinen nunca.
- **DI-V22** — La plantilla declara `<meta charset="utf-8">`. Sin eso, un
  navegador que abra el archivo desde el disco no recibe cabecera
  `Content-Type` y asume Latin-1: «Los Mártires» salía «Los MÃ¡rtires».
  Publicada como artefacto no fallaba, porque el servidor sí manda el charset,
  y por eso el defecto podía vivir meses sin que nadie lo notara — lo destapó
  encender los nombres de localidad para revisar el modo oscuro.

Lo que el zoom **no** arregla: la geometría sigue simplificada a resolución de
pantalla (DI-V1, DI-V9). A ×24 se ven los vértices. Sirve para ubicarse, no
para medir, y la barra de escala está ahí para dar orden de magnitud, no para
tomar distancias.

**Lo que la capa base no cambia.** Nada de lo que dice la sección 2. Un mapa
con calles se parece más a un mapa de verdad, y eso lo hace *más* persuasivo,
no más cierto: la capa de opinión sigue siendo plana y el 100 % de su
dispersión entre localidades sigue siendo ruido muestral. Por eso la capa base
va apagada por defecto y el pie dice, con esas palabras, que ninguna cifra de
la página se calcula con ella.

### Capa de Voto (añadida el 29/09/2026)

El detalle está en el docstring de `src/viz/preparar_voto.py`. Resumen:

- **DI-V53** — **La tercera capa que sí puede afirmar geografía**, junto con
  Población y Crecimiento, y por la misma razón que Crecimiento (DI-V51): es un
  conteo completo, sin error de muestreo. Carga dos salvedades propias, que el
  aviso dice **con cifras del paquete**, no con texto fijo: el voto se cuenta
  donde se está inscrito (La Candelaria tiene 3 inscritos por adulto residente) y
  una parte de los votos (Corferias y cárceles, 1,6 % a 3,2 % según el año) no
  tiene localidad. La barra de años se oculta con esta capa: sus años son los de la
  ECP, no los de las elecciones, y el selector de elección vive en la leyenda.
- **DI-V54** — Proporción sobre votos por candidato (DI-EL5), y **un solo dominio
  de color para las nueve combinaciones** de elección y candidato, de 0 al máximo
  observado (80 %). Reescalar por candidato haría que uno con 3 pp de geografía se
  viera tan partido como uno con 12 (DI-V49 otra vez). Rampa propia, violeta, que
  no usa ninguna otra capa.
- **DI-V55** — **Los residuos son los del análisis pre-registrado, sin
  recalcularse**, con rampa divergente violeta/café y el gris en el 0. La versión
  que añade la participación **no estaba pre-registrada**: está como vista
  exploratoria, lo dice su botón y su aviso, y nunca es la de entrada.
- **DI-V56** — Sumapaz tiene voto pero no residuo (quedó fuera del ajuste): va en
  gris en la vista de residuos y la ficha dice por qué.

### Poblaciones regeneradas (29/09/2026)

- **DI-V57** — **Las poblaciones del mapa se regeneraron después de DI-M2, y las
  cifras sintéticas citadas antes son de una corrida que ya no se puede
  reproducir.** *Hecho:* con la misma semilla, dos máquinas daban los mismos agentes
  con otras opiniones, porque el sorteo de empates del hot-deck dependía del orden en
  que scikit-learn devuelve a los empatados (`matching.py`, DI-M2). *Decisión:* se
  corrigió el emparejamiento y se regeneraron las cinco poblaciones (versión
  `v0.5-dim2`), el piso territorial (20 semillas) y el paquete.

  | año | media antes → ahora | dispersión entre localidades | rango del piso |
  |---|---|---|---|
  | 2013 | 2,809 → 2,781 | 0,156 → 0,146 | 0,10–0,48 → 0,12–0,57 |
  | 2017 | 2,525 → 2,552 | 0,196 → 0,187 | 0,16–0,53 → 0,14–0,43 |
  | 2019 | 2,393 → 2,409 | 0,147 → 0,175 | 0,14–0,59 → 0,14–0,56 |
  | 2021 | 2,241 → 2,227 | **0,341 → 0,221** | 0,15–0,51 → 0,16–0,50 |
  | 2023 | 2,448 → 2,421 | 0,170 → 0,168 | 0,13–0,48 → 0,15–0,49 |

  Los agentes y la capa de Crecimiento quedan idénticos. **Las cifras de corridas
  anteriores que citan este documento y PROJECT_CONTEXT (0,156 en §2 y en §3.2;
  0,341 en DI-V45) se conservan sin editar (§45)**: describen la corrida de entonces.
  Ninguna conclusión cambia: la media de ciudad sigue a la medida dentro de ±0,03, y
  la dispersión entre localidades sigue dentro del rango del piso en los cinco años
  (percentiles 10 a 45), que es lo que ya decía DI-V52. El caso de 2021, que DI-V45
  miró con atención por su 0,341, era una semilla alta: con la población nueva vale
  0,221.

- **DI-V59** — **La capa de Voto enseña los dos polos** (30/09/2026). Se agregan la
  Lista de la Decencia y el Centro Democrático del Senado 2018, con su voto y su
  residuo tal como quedaron en `EJE_PARTIDOS_RESULTS.md`, y el aviso de la vista de
  residuos deja de hablar de «un eje izquierda–derecha»: dice que el resto no es de un
  candidato (lectura A, pre-registrada) y que son **dos polos con geografía propia**
  (§4 de ese informe, descriptivo, y así lo declara la página). Cada opción dice en qué
  polo está y cuánto se parece a su partido; Fajardo, Santos y Hernández no están en
  ninguno, y la página lo dice con sus cifras. La pertenencia a un polo vive en el
  paquete, no en la plantilla, y una prueba exige que cada opción de un polo se parezca
  a su partido con r ≥ 0,69. Los botones se agrupan por elección («Senado 2018» es un
  grupo más) y los textos dicen la elección, no solo el año.

- **DI-V60** — **La página dice que 2026 no confirmó los dos polos** (30/09/2026). La
  lectura de DI-V59 se puso a prueba, pre-registrada, en la primera vuelta de 2026
  (`POLOS_2026_RESULTS.md`): lectura B, y el resto de Abelardo se parece más al revés
  del polo de izquierda que al polo de derecha. El aviso de residuos pasa de «Son dos
  polos, no un eje» a «En 2014–2022 fueron dos polos, no un eje», y agrega un párrafo
  «Puesta a prueba en 2026, no se confirmó» con las cifras de la prueba, que vienen del
  paquete (`polos.prueba_2026`, leído de `data/processed/polos_2026/resultado.json`),
  no de la plantilla. La vista de voto y el pie dicen lo mismo en una frase. 2026 no
  entra como opción del mapa: la capa sigue siendo 2014–2022 y Senado 2018.
  **Tres decimales para la mejora del polo:** redondeada a dos, 0,047 se leía «0,05»,
  que es exactamente el umbral que no alcanzó; se encontró revisando la página y una
  prueba lo vigila.

- **DI-V58** — **El DEFF de la página pasa de 1,86 a 2,03** (29/09/2026, DI-D7 en
  `diseno.py`). El conglomerado de la EPC es localidad × manzana, no la manzana sola,
  que se numera dentro de cada localidad. DI-V4 se conserva sin editar. Efecto: el
  error estándar de cada localidad en la capa de Opinión y los márgenes de la serie de
  la ECP se ensanchan un 4,5 %; en la serie de la EPC, 2014, 2015 y 2018 toman su
  error con el diseño corregido (2015: 0,042 → 0,052). Ninguna media cambia. La página
  ya no lleva el DEFF escrito: `preparar_mapa.py` lo lee de `DEFF_MEDIDO_EPC`.

La regla de §2 se aplica al revés aquí, y el aviso lo enseña: la capa de Opinión no
puede decir «el sur confía menos»; esta sí puede decir «el sur votó más por Petro»,
y además decir **dónde el estrato no alcanza a explicarlo**. Lo que no puede decir
es nada sobre personas: el análisis es ecológico.

## 3.4 Archivos

```
data/external/geo/localidades_bogota.geojson   geometría oficial simplificada (27 KB)
data/external/geo/osm/vias.geojson             extracto Overpass: trunk + primary (5,1 MB)
data/external/geo/osm/verde.geojson            extracto Overpass: leisure=park (5,0 MB)
data/external/geo/osm/agua.geojson             extracto Overpass: agua — PENDIENTE (DI-V14)
src/viz/preparar_mapa.py                       geometría + población → paquete de datos
src/viz/preparar_serie.py                      ECP + EPC → serie temporal con márgenes (Hito 2)
src/viz/piso_territorial.py                    rehace la población con 20 semillas → estabilidad de una corrida (DI-V45, DI-V52; lee .parquet o .csv desde el 29/09)
src/viz/simular_prueba_piso.py                 ciudad simulada: el criterio del piso no detecta señal (DI-V52)
data/external/marginal_localidad_18mas_serie.csv  población 18+ por localidad y año, solo para dibujar (DI-V48)
src/utils/revisar_datos.py                     qué datos hay en esta máquina y dónde va cada cosa
src/viz/preparar_base.py                       extractos OSM → capa base recortada y simplificada
src/viz/plantilla_mapa.html                    la página, con marcadores /*__DATOS__*/ y /*__BASE__*/
src/viz/preparar_voto.py                       tabla electoral + resultado del análisis → capa de voto (DI-V53)
src/viz/construir_pagina.py                    plantilla + datos + base + serie + voto → archivo único
data/processed/viz/mapa_bogota.json            paquete de 5 olas, con `escala_opinion` y el piso (98 KB)
data/processed/viz/piso_territorial.json       el piso de ruido medido, 20 semillas × 5 años
data/processed/viz/serie_bogota.json           la serie medida, 14 puntos con intervalo (4,6 KB)
data/processed/viz/voto_bogota.json            la capa de voto: 9 candidatos × 20 localidades, residuos y salvedades (16 KB)
data/processed/viz/base_bogota.json            capa base, dos niveles de detalle (71 KB)
data/processed/viz/mapa_bogota.html            la página lista (252 KB)
tests/test_viz_mapa.py                         72 pruebas
tests/test_viz_base.py                         81 pruebas de la capa base, la navegación, la ficha, la rampa y el año
tests/test_viz_serie.py                        43 pruebas de la serie temporal y su gráfico
tests/test_viz_voto.py                         35 pruebas de la capa de voto: el paquete contra sus fuentes y la página
```

Reproducir de cero:

```
for a in 2013 2017 2019 2021 2023; do
  python3 src/population/construir_poblacion.py --donante ecp:$a --n 1000 --seed 42 \
          --nombre-base poblacion_ecp$a --version v0.4-hito2-$a
done
python3 src/population/extraer_columnas_em2021.py marginal-serie
python3 src/viz/piso_territorial.py        # ~4 min; produce el piso de ruido
python3 src/viz/preparar_mapa.py
python3 src/viz/preparar_base.py
python3 src/viz/preparar_serie.py
python3 src/viz/preparar_voto.py          # necesita data/external/electoral y el resultado de la geografía electoral
python3 src/viz/construir_pagina.py
python3 tests/test_viz_mapa.py
python3 tests/test_viz_base.py
python3 tests/test_viz_serie.py
```

## 3.5 Qué verifican las pruebas

Estructura (20 localidades, códigos 01–20 completos, todas con nombre del
marginal), correspondencia agentes/localidad, **que ningún punto caiga fuera de
su polígono después de redondear** —si eso falla el mapa dibuja gente en la
localidad equivocada y el dibujo deja de ser verificable—, coherencia
estadística (la dispersión dentro supera a la de entre; el efecto de diseño
aplicado es el medido; la descomposición ruido/real cierra) y reproducibilidad
con semilla fija.

De la capa base (`tests/test_viz_base.py`): que la codificación delta sea la
identidad al decodificar —si se desalinea, las vías aparecen corridas sobre las
localidades y el lector ubica una avenida en la localidad equivocada—, que casi
todo punto caiga dentro de la caja de recorte, **que ninguna etiqueta de
OpenStreetMap sobreviva en el paquete** (si llevara nombres o anchos, alguien
acabaría calculando algo con ella), que el reencadenado de tramos funcione, que
Douglas-Peucker colapse rectas y conserve esquinas, y que la página construida
lleve la atribución ODbL, la frase de que no entra en ningún cálculo y ninguna
petición de red fuera de las tipografías.

De la ficha de la escala (A05, en los dos archivos): que el paquete traiga
`escala_opinion`, que su rango coincida con el de `ciudad.escala`, que existan
anclas verbales para los dos extremos, que el denominador quede registrado y que
el mínimo observado nunca baje del mínimo exigido; y, del lado de la página, que
el bloque se dibuje **desde el metadata** (`D.escala_opinion`) y no desde texto
escrito a mano, y que las anclas y la advertencia de «no es un porcentaje»
lleguen efectivamente al HTML. La prueba que importa es la del origen: impide
que alguien "arregle" la ficha escribiéndola en la plantilla, que es como
volvería el defecto.

De la rampa de población (DI-V36): que la transformación tenga nombre, que el
color y las marcas de la leyenda usen esa misma, que la leyenda declare la
escala de raíz, y —la que de verdad protege— **que `Math.sqrt` aparezca una sola
vez en toda la página**. Dos raíces separadas es como empezó el defecto.

De la serie temporal (`tests/test_viz_serie.py`): que cada intervalo sea
exactamente ±1,96 EE —dibujar uno más angosto sería mentir justo donde
importa—, que ningún punto de la ECP se declare estimado con diseño, que los
años marcados con diseño en la EPC coincidan con los que la lista declara, que
el salto se marque **exactamente** cuando la brecha supera dos años, que 2015
siga excluido con su motivo, y que el paquete no traiga ninguna comparación
precalculada entre las dos series.

---

# 4. HITOS SIGUIENTES *(especificados, no construidos)*

## Hito 2 — El tiempo  *(completo, 24/09/2026)*

**Construido, segunda mitad — el mapa por año.** Cinco poblaciones sintéticas,
una por ola de la ECP, construidas con la misma muestra (DI-V43). Botones de
año en la barra del mapa; un clic en un punto de la serie ECP lleva el mapa a
ese año; el año activo se marca en el gráfico. La capa de Agentes colorea cada
punto por su propia opinión, así que al cambiar de año se ve la distribución
moverse (DI-V47).

**Y lo que el mapa por año enseñó sobre el proyecto.** Construirlo obligó a
mirar cinco veces la misma descomposición ruido/señal, y ahí apareció DI-V45:
el error estándar analítico venía subestimando el ruido territorial desde el
Hito 1, y el único año que parecía tener señal (2021) no la tiene. Es el
segundo defecto de esta fase que encuentra **un control numérico y no una
revisión** — el primero fue la rampa verde (DI-V36).

**Construido, primera mitad:** la línea de tiempo. Catorce mediciones reales con su margen:
confianza institucional (ECP, 2013–2023, cinco puntos) y gestión del alcalde
(EPC, 2014–2025, nueve puntos). Cada punto trae n, intervalo al 95 % y si ese
intervalo se estimó con el diseño de la muestra o con un DEFF prestado.
Decisiones DI-V37 a DI-V41; datos en `src/viz/preparar_serie.py`.

Lo que la serie muestra, y que no se veía antes en ninguna parte del proyecto:
la confianza institucional cae de 2,81 (2013) a 2,24 (2021) y rebota a 2,43 en
2023 — un movimiento de 0,57 puntos frente a márgenes de ±0,03, así que es
señal, no ruido. La evaluación del alcalde recorre un rango mayor (2,10 en 2017
a 3,18 en 2024) y **no** se mueve en fase con la confianza: entre 2019 y 2023 la
gestión sube mientras la confianza sigue bajando. Son dos instrumentos y dos
conceptos, y el gráfico existe para que eso se vea en vez de suponerse.

**Lo que queda pendiente, y no es del Hito 2:** el tablero ya puede mostrar
cinco cortes del mismo instrumento, pero sigue sin haber simulación. El
siguiente paso que cambia de naturaleza es poner una corrida del modelo al lado
de la serie medida, para que se vea qué tan lejos cae.

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
