# ¿Sobre qué debería construirse la red? — Análisis de bases de homofilia

Proyecto: Bogotá Social Simulator
Versión: 1.2 — añadida la evidencia territorial de los estudios del CNC (§8), que cierra A07
Fecha: 16 de septiembre de 2026
Origen: pregunta abierta por `claude/EXPERIMENT_3_RESULTS.md` §5 y §8.3 (A07)
Datos: ECP 2017–2023 (Bogotá, ponderada); DDI de EM-2021; Salud Mental Bogotá 2023 y Sustancias Bogotá 2022 (CNC), vía agregados

---

## 1. La pregunta y la respuesta corta

El Experimento 3 mostró que la estructura de red casi no afecta el ajuste a datos (rango 0,015 entre nueve configuraciones, contra 0,0045 de dispersión entre semillas), mientras que en el Experimento 2 la homofilia dominaba el resultado. La hipótesis: **la homofilia de `NETWORK SPECIFICATION.md` se construye sobre edad, estrato y nivel educativo, y esas variables podrían no tener nada que ver con la opinión.**

Se confirmó, y después se confirmó dos veces más, sobre ejes distintos y con datos distintos:

| Eje | Cuánta varianza de opinión explica | Fuente |
|---|---|---|
| **Demografía** (edad × sexo × educación × estrato, 66 celdas) | **3 %** | ECP, confianza institucional |
| **Atributos observables estables** (medios, religión, estado conyugal, participación…) | **≤ 4 %, y no replican entre olas** | ECP |
| **Territorio** (20 localidades) | **~1 %, y la mitad es ruido muestral** | CNC, 42 ítems de opinión |
| Actitudes (satisfacción con la democracia, etc.) | 10–25 % | ECP |

**No hay ningún atributo observable —ni personal ni territorial— que estructure la opinión en Bogotá.** Lo único que predice opinión es otra opinión.

Y hay un dato que apunta a la salida: en la ECP, **el 39,5 % del círculo cercano de un bogotano comparte sus opiniones políticas** (§5.2). O sea que la homofilia de opinión existe y es fuerte — simplemente **no es demográfica ni territorial**. Los grupos de opinión cruzan localidades y estratos.

---

## 2. Cuánta varianza explica cada cosa (ECP)

Métrica: η², participación de la varianza *entre* grupos en la varianza total ponderada del índice de confianza.

### 2.1 Referencia demográfica

| Variable | η² 2017 | η² 2023 |
|---|---|---|
| estrato (3 grupos) | 1,71 % | 1,29 % |
| edad (4 grupos) | 0,96 % | 0,25 % |
| educación (3 grupos) | 0,60 % | 0,50 % |
| sexo | 0,03 % | 0,08 % |
| **las cuatro cruzadas (66 celdas)** | **4,5 %** | **2,9 %** |

### 2.2 Rasgos estables — los candidatos a reemplazo

| Variable | η² 2017 | η² 2023 |
|---|---|---|
| medio de información S7 | **4,26 %** | **0,00 %** |
| estado conyugal | **3,00 %** | **0,05 %** |
| etnia / raza | 2,38 % | 0,41 % |
| cantidad de medios que usa | 1,78 % | **3,89 %** |
| religión | 0,75 % | 0,84 % |
| se informa sobre política | **0,28 %** | **3,30 %** |
| hizo un trámite con el Estado | 0,51 % | 0,06 % |

**Ninguna replica.** Con n ≈ 5.000 y η² de 2–4 % sobre variables de pocas categorías, esto es ruido de muestreo.

### 2.3 Actitudes — lo único que sí predice

| Variable | η² 2017 | η² 2023 |
|---|---|---|
| satisfacción con la democracia | **25,26 %** | **14,32 %** |
| efectividad de los instrumentos de derechos | 14,84 % | 12,05 % |
| ¿Colombia es un país…? | 8,54 % | 12,71 % |
| calidad del servicio público | 6,62 % | 10,74 % |
| el Congreso representa las tendencias | 9,78 % | 4,46 % |

---

## 3. Hay una postura latente hacia las instituciones

Componentes principales sobre el índice de confianza más las seis actitudes:

| | PC1 | PC2 | PC3 |
|---|---|---|---|
| 2017 (n = 4.007) | **35,1 %** | 14,5 % | 13,4 % |
| 2023 (n = 3.660) | **35,3 %** | 14,4 % | 13,6 % |

El primer componente explica **35 % en los dos años, con tres decimales de diferencia**, y la confianza carga entre las dos más altas en ambos. Correlación directa con satisfacción con la democracia: **0,508 en 2017, 0,364 en 2023**.

*Cautela:* "calidad del servicio público" invierte el signo de su correlación entre olas (−0,253 → +0,325). Casi con seguridad es un cambio de codificación. No afecta al PC1.

---

## 4. Qué implica para el diseño del simulador

`D12` fijó seis campos del agente y `NETWORK SPECIFICATION.md` construyó la distancia homofílica sobre tres de ellos. **No existe un reemplazo observable.**

La red homofílica conecta agentes que se parecen en algo que explica el 3 % de la variable que el modelo simula. Eso explica el §5 del Experimento 3 — la red casi no movió el ajuste porque la dimensión sobre la que se construye es casi ortogonal a la opinión.

Y acota lo que se puede afirmar de la población sintética: reproduce bien la **distribución** de confianza (Experimento 3A: W1 = 0,048) pero **no coloca la confianza sobre los individuos correctos**.

---

## 5. El cruce con Multipropósito, y lo que apareció ahí

### 5.1 Lo que sí hay en Multipropósito

| Archivo | Contenido relevante | Variables |
|---|---|---|
| **F53 — capítulo J** | Pertenencia a organizaciones (17 tipos) | `NPCJP1A`…`NPCJP1Q` |
| F53 | Asistió a reuniones o contacto con organizaciones | `NPCJP2` |
| F53 | A quién recurre ante problemas económicos | `NPCJP9B` |
| F52 | Frecuencia y usos de internet | `NPCIP4`, `NPCIP8*` |
| F48 | Estado civil | `NPCEP7` |

**No tiene confianza interpersonal ni tamaño de red.** El único puente al receptor es pertenencia a organizaciones, que es el predictor más débil de todos (r ≈ 0,05–0,08).

### 5.2 El módulo de Capital Social de la ECP: la red, medida

| Variable | Qué mide | Bogotá 2023 |
|---|---|---|
| **`P2047 + P2049`** | **tamaño de la red cercana de apoyo y confianza** | **media 5,35 · mediana 4 · 26 % sin red** |
| **`P2051S1`…`S11`** | **composición de ese círculo** | ver abajo |
| `P2025S1`…`S6` | confianza interpersonal (familia, amistades, colegas, vecinos, extranjeros, desconocidos) | r ≈ +0,25 con confianza institucional |
| `P2001S1`…`S17` | pertenencia a organizaciones | cruza con el capítulo J |

Composición del círculo cercano, Bogotá 2023:

| % | Descripción |
|---|---|
| 72,9 | Se graduaron de bachillerato |
| 70,3 | Tienen un empleo |
| 50,2 | Miembros de su familia |
| 40,7 | Hombres |
| **39,5** | **Tienen opiniones políticas parecidas a las suyas** |
| 32,3 | Son de su grupo étnico |
| 30,5 | Asisten a su grupo u organización religiosa |
| 22,6 | Sienten que perdieron oportunidades por trabajadores extranjeros |
| 19,2 | Le han prestado dinero (o usted a ellos) |
| **12,4** | **Viven en su misma cuadra** |
| 2,6 | Son extranjeros |

Dos cifras para el diseño:

- **El grado empírico es ~5**, no 8 ni 16. `NETWORK SPECIFICATION.md` barre \(\bar{k} \in \{4, 8, 16\}\); la medición cae entre los dos primeros. Advertencia: `P2047` está topeado en 10 y 2021 está contaminado por la pandemia (la pregunta es sobre visitas); calibrar con 2019 o 2023.
- **Solo el 12,4 % del círculo cercano vive en la misma cuadra**, contra el 39,5 % que comparte opiniones políticas. El vecindario estructura la red **tres veces menos** que la opinión.

La correspondencia `P2051S*` → descripción no está publicada; se estableció reproduciendo los porcentajes del Cuadro 9 del anexo de DANE, con una discrepancia máxima de **0,04 pp sobre 33 comparaciones**. Ver `ETIQUETAS_COMPOSICION_RED` en `src/population/ecp.py`.

### 5.3 Límites

`P2047` pregunta por **visitas mutuas frecuentes**: lazos fuertes de sociabilidad doméstica, no "quién influye en tu opinión política". Deja fuera trabajo, redes sociales y vínculos débiles, que es donde la literatura ubica buena parte de la difusión. Y **Capital Social no existe en 2017**.

---

## 6. Las salidas, y lo que cuesta cada una

**A. Calibrar la red con Capital Social.** Ya es posible: \(\bar{k} \approx 5\) y los 11 pesos de homofilia están medidos. Es la única opción que reemplaza un supuesto por una medición.

**B. Homofilia sobre la opinión misma** (confianza limitada: Hegselmann-Krause, Deffuant). **Es la que la evidencia respalda**: el 39,5 % de homofilia política medida, contra 12,4 % territorial y ~3 % demográfica. Sigue siendo un supuesto sobre el mecanismo —los cortes transversales no revelan quién influye a quién— pero es un supuesto con respaldo sobre la *composición* de la red.

**C. Agente con postura latente** (PC1 de §3). El agente carga una variable que covaría con el resultado, pero el PC1 es 44 % confianza: es en buena medida la opción B con otro nombre.

**D. Dejar de tratar la red como decisión a validar** y reportar sensibilidad. Honesto y barato; deja A07 abierta para siempre.

**E. Reconsiderar qué aporta el ABM para esta variable.** Ver §8.3.

---

## 7. Lo que sigue sin cerrar

- Las actitudes no se probaron como base de homofilia. Se descartaron por circularidad, y esa decisión merece discutirse: en redes reales la homofilia *sí* es en parte actitudinal.
- El módulo de Capital Social no existe en 2017, así que la red solo se puede calibrar con 2019, 2021 o 2023.

---

## 8. La evidencia territorial (CNC) — y el cierre de A07

Los cuatro estudios que el CNC entregó no miden confianza institucional, así que no reemplazan al donante de D11. Pero dos son de **Bogotá con las 20 localidades**, y eso permitió por primera vez preguntarle al eje territorial lo mismo que le habíamos preguntado a la demografía.

Los microdatos no salieron del equipo: `src/population/cnc_agregar.py` corre allá y escribe solo agregados (medias por localidad con error de diseño, descomposición de varianza y composición), con supresión de celdas con n < 30.

| Estudio | n | Localidades | n mediano por localidad | Ítems de opinión |
|---|---|---|---|---|
| Salud Mental Bogotá 2023 (UNODC) | 15.151 | 20 | 776 | M1 satisfacción (11), M41 APGAR familiar (5) |
| Sustancias Bogotá 2022 (PNUD/SDS) | 10.912 | 20 | 460 | T150 política pública (6), T29 percepción de riesgo (20) |

### 8.1 El resultado

**La localidad explica entre 0,4 % y 2,6 % de la varianza de opinión, con mediana ~1 %.** Sobre 42 ítems, cuatro baterías, dos estudios, dos años.

Y la estandarización por composición **casi no lo mueve** (mediana cruda ~1 %, estandarizada ~1 %): lo poco que hay tampoco es composicional. Simplemente es poco.

Peor aún: **la mitad o más de esa variación aparente es error de muestreo.** Comparando la varianza observada entre localidades contra la que explican los errores estándar de diseño:

| | varianza entre localidades que es ruido | sd real entre localidades | sd dentro de localidad |
|---|---|---|---|
| Salud Mental | **54 %** | **0,073** | ~1,05 |
| Sustancias | **63 %** | **0,046** | ~1,05 |

En puntos de escala: **las localidades de Bogotá difieren entre sí en centésimas de punto**, sobre escalas de 1–5 y 1–4. La desviación entre localidades es el **5–7 % de la desviación entre personas**.

Los ítems con más señal territorial son los de percepción de riesgo de la marihuana (`T29_9`, `T29_10`, `T29_11`: 1,6–2,0 %, y solo ~20 % de ruido) — tiene sentido, la exposición varía por territorio. Pero aun ahí la sd real es 0,16 sobre una escala de 1 a 4.

*Nota metodológica:* en salud mental el estrato de diseño es el socioeconómico, así que al estimar dentro de una localidad quedan estratos con un solo conglomerado, que `svy_prop` omite. Eso **subestima** la varianza, o sea que el porcentaje de ruido real es todavía mayor. El DEFF mediano de estas estimaciones es 2,5, con máximos de 45–53 en los ítems más raros.

### 8.2 Qué cierra esto

**A07 queda cerrada, y no por elección sino por falta de fenómeno.** El generador territorial no está mal implementado: **no tiene un objetivo empírico que reproducir.** La localidad estructura la opinión veinte veces menos que la variación individual, y la mitad de ese poco no se distingue del ruido.

La cadena de evidencia es consistente y viene de tres fuentes independientes:

1. **Experimento 3 §5:** la estructura de red casi no afecta el ajuste (rango 0,015 entre nueve configuraciones, contra 0,0045 entre semillas).
2. **§2 de este documento:** la demografía explica el 3 % de la confianza; ningún atributo observable estable lo mejora de forma reproducible.
3. **§8.1:** la localidad explica ~1 % de la opinión, y la mitad es ruido.

**Ni los atributos ni el territorio estructuran la opinión en Bogotá.** Es idiosincrática a nivel individual, y lo único que la predice es otra opinión (§2.3) — coherente con que el 39,5 % del círculo cercano comparta opiniones políticas mientras solo el 12,4 % comparta cuadra (§5.2).

Eso deja **la opción B como la única con respaldo empírico**: si hay que construir una red sobre algo, ese algo es la opinión, no el barrio ni la demografía.

### 8.3 Y lo que obliga a reconsiderar

Tres hallazgos independientes apuntan igual: el mecanismo no aporta al nivel (Exp. 3, P1), la red casi no afecta el ajuste (Exp. 3 §5), y nada observable —ni personal ni territorial— predice la opinión individual (§2, §8.1).

Para *opinión en Bogotá con los datos públicos disponibles*, **no hay un modelo generativo identificable a nivel individual.** No es un problema de implementación ni de elegir mejor las variables: la señal estructural no está en los datos.

Eso **no invalida el proyecto**, pero reordena dónde está su valor. La descripción dice "laboratorio computacional para explorar escenarios sociales", no predictor. La población sintética es sólida y reproducible; la maquinaria de redes y dinámica está construida y probada; y ahora el grado y la composición de la red tienen anclaje empírico (§5.2). Lo que cambia es que los escenarios se apoyan en **supuestos explícitos que el usuario fija**, no en una dinámica emergente que reproduzca la historia por sí sola.

Un laboratorio de "¿qué pasaría si…?" sigue en pie. Un "esto es lo que va a pasar" no, y conviene decirlo antes de que alguien lo espere.

### 8.4 Lo que los estudios del CNC sí destraban, aparte de esto

- **Cierran A02 con un no.** No hay panel ni tracking con la misma pregunta repetida: cuatro cortes transversales de temas distintos. La validación de nivel 3 sigue dependiendo de la ECP.
- **`estimacion.py` del CNC** trae `svy_prop` con varianza por linealización de Taylor y DEFF. El proyecto venía calculando medias ponderadas ingenuas en todas partes; conviene adoptarlo.
- **Advertencia de confidencialidad:** `data/raw/cnc/` contiene copias exactas del cliente con nombres, direcciones y GPS. El README del CNC prohíbe sacarlas del equipo. Verificar que esa carpeta esté fuera de cualquier sincronización o repositorio remoto.

---

*Análisis de evidencia previo a decidir, según el Principio 4 del prompt maestro: no elegir mecanismo sin evidencia. La evidencia acá es mayormente negativa, y eso también es evidencia — de hecho es la que más ha cambiado el diseño del proyecto.*
