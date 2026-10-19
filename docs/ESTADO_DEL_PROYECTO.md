# ESTADO DEL PROYECTO — punto de partida para una conversación nueva

Proyecto: Bogotá Social Simulator
Fecha de corte: **2 de octubre de 2026** (D18: preguntas nuevas sin cifra propia; frente activo: la página D17)
Para qué sirve: leer **este documento solo** basta para retomar. Los demás se
leen cuando el trabajo los toque, no antes.

---

## 1. Dónde está el proyecto, en seis líneas

- El **pipeline de población** funciona, es reproducible y está validado: la opinión sintética es indistinguible de la encuesta real (por debajo del piso de ruido).
- El **modelo de opinión** falló contra lo pre-registrado, y ese resultado definió el producto: **escenarios**, no predicción. El motor de escenarios está construido (Fase 8).
- La **capa visual** es el frente principal desde el 18/09 (decisión del jefe de Daniel). Hitos 1 y 2 completos; la página está en GitHub.
- **A08 (escalar a 100.000 agentes) quedó sin argumento visual** el 25/09: más agentes dibujarían nítida la composición demográfica, y la composición no reproduce la geografía real de la opinión.
- **La IA generativa como fuente de opinión se descartó** con datos (Experimento 8). El **Experimento 9** —la IA como proponente de escenarios, inspirado en MiroFish— **se corrió y también falló** (29/09): el LLM no le gana a suponer que nada cambia, acierta donde recuerda, y el dossier no ayuda. **Los números de un escenario los sigue escribiendo una persona.**
- La **geografía electoral** (29–30/09) dio la primera geografía real dentro de la ciudad: hay un resto territorial estable, con dos polos, que la composición no ve. Cerrada; está en el tablero.
- **Reestructuración (D17, 30/09):** una página para hacerle preguntas de opinión a la población y verlas por localidad en el mapa, todo rotulado como suposición. Lo que sigue, en §6.

---

## 2. Cómo trabajar con Daniel

Daniel es ingeniero multimedia en el CNC. **Prefiere avanzar un frente a la vez,
confirmando antes de pasar al siguiente, y detenerse a resolver lo que falla antes
de acumular avances.**

### Dos máquinas, un repo

Repo: `github.com/Daniel-Silva03/Bogot-Simulator` (privado). **Todo se sincroniza
por GitHub**: antes de trabajar, `git pull`; al terminar, `git push`. Al 29/09 las
dos máquinas y el repo están iguales (ver `git log`; este documento no fija un hash).

| | PC personal | PC del CNC |
|---|---|---|
| Carpeta | `C:\Users\User\Desktop\bogota_social_simulator` *(confirmar que es clon del repo: `git remote -v`)* | `C:\Users\CNC.DSP-17291\Desktop\Bogot-Simulator` |
| Claude | **puede operar directo** si el chat está vinculado al computador | no: Daniel aplica cambios a mano y corre los comandos |
| Microdatos del CNC | **sí**, fuera del repo; nunca se tocan ni se suben (R10) | no |
| `data/raw/` público | sí (Multipropósito, ECP, EPC en su ruta por defecto) | sí, descargado del DANE el 25/09; EPC en `data\raw\Encuesta de Percepción Ciudadana` → requiere `$env:BSS_EPC_DIR` |

Terminal: PowerShell en VS Code. `.\venv\Scripts\Activate.ps1`; el intérprete es
`python`, no `python3`. `python src/utils/revisar_datos.py` dice qué datos hay en
una máquina y qué se puede correr.

**Regla R10 / DATA_INVENTORY §12.4:** los microdatos del CNC no salen de su equipo
ni se suben a ningún servicio, **tampoco a una API de LLM**. La ECP y la EPC sí
son públicas. Antes de cada commit, revisar `git status` por si se cuela algo de
`data/raw/`, del CNC o de `cache/`.

---

## 3. Lo que se cerró en estas dos tandas (18–29 de septiembre)

### A05 — el índice de confianza (POPULATION_SPECIFICATION §8.4)
Umbral de 7 ítems medido, no heredado; el denominador viaja por fila y la página lo publica.

### Hito 2 — el tiempo (VISUALIZATION_SPECIFICATION §Hito 2)
Línea de tiempo con la ECP (2013–2023) y la EPC (2014–2025), mapa por año conectado, capa de Crecimiento.

### DI-V45 → DI-V52: la corrección de la semana
DI-V45 (18–24/09) concluyó «no hay señal territorial» comparando la corrida
publicada contra 20 semillas del mismo pipeline. **DI-V52 (25/09) lo corrigió:**
la corrida publicada sale del mismo proceso que las semillas, así que su percentil
es uniforme; el criterio «detecta» ~5 % de las veces **haya o no efecto**
(simulado: 4 % con un efecto enorme; una permutación, 100 %). Lo que se sostiene
de DI-V45: una sola corrida es inestable. La página ya no afirma «no hay señal»;
da la razón válida: **el donante no trae localidad**.

> **Un null tiene que poder fallar.**

### A08 — escalar la población: cerrado como argumento visual
- **Paso 0** (`A08_PASO0_RESULTS.md`): el límite con N infinito se calcula exacto
  sin construir poblaciones. La composición separa las localidades en 2017–2023
  (no en 2013), con el patrón del estrato; verlo exige 100.000 agentes. Las cinco
  predicciones fallaron (P2 por usar R² lineal como proxy del emparejamiento).
- **Paso 0b** (`A08_PASO0B_RESULTS.md`): con la EPC, que sí trae localidad, **hay
  territorio real** (7 de 9 olas) pero **la composición no lo reproduce** ni en
  escala (R = 2,1; 1,37 con DEFF) ni en dirección (r = 0,33).
- **Decisión:** un mapa nítido de la composición sería un mapa preciso de otra
  cosa. Si se quiere geografía de opinión, el problema es de **datos** (un donante
  con localidad; reabrir DI-B10), no de escala.

### Experimento 8 — LLM como donante: descartado
El LLM pierde en los dos ejes. **Aplana a las personas (0,30× la variación real) y
exagera las instituciones (3,3×)**, con Partidos en 1,00. No se repite con otro
modelo. Informe para no técnicos: doc de Claude «IA generativa como fuente de
opinión: qué probamos y por qué seguimos sin ella» (28/09).

### MiroFish y el Experimento 9
El jefe de Daniel recomendó MiroFish (agentes LLM que parten de un documento y
simulan reacciones en redes). Evaluación: su núcleo —LLM como personas— es lo que
el Experimento 8 ya descartó; sin validación publicada; AGPL-3.0; choca con R10.
**Lo aprovechable es «del documento al escenario»:** que un LLM lea lo que pasó y
proponga los dos números del escenario (nivel y dispersión).
`EXPERIMENT_9_SPECIFICATION.md`: 12 transiciones reales (ECP 4 + EPC 8), dos
brazos (memoria propia / dossier), baselines «sin cambio», «tendencia» y oráculo,
**sonda de memoria**, seis predicciones y regla de decisión. **Enmienda 1 (28/09):**
dossier desde las cronologías anuales de Wikipedia en español.

### Experimento 9 — el LLM como proponente de escenarios: descartado
`EXPERIMENT_9_RESULTS.md`. 12 transiciones, dos brazos, 262 llamadas, USD 0,18.
**Falla el criterio 1 de la regla**: mediana de W1/piso 5,17 (brazo con dossier)
contra 5,78 de «sin cambio»; hacía falta 4,63. Cobertura de sus intervalos del
90 %: 50 %. Fuera de memoria no se separa de «sin cambio». El brazo **sin**
dossier (4,72) queda por delante del brazo con dossier: leer el documento no es
lo que ayuda. El control por permutación (enmienda 5, añadido antes de correr
porque un proponente aleatorio le ganaba a «sin cambio» el 55 % de las veces)
da *p* = 0,39: la ventaja no se distingue de proponer las mismas cifras en otro
periodo. Permitido por la regla: usar el LLM para **redactar** la descripción de
un escenario, nunca para fijar sus cifras.

### Material para la dirección
Presentación de 7 diapositivas (artefacto de Claude, 25/09). **A Daniel no lo
convenció: parecía que no hubiera avances.** El enfoque que sí sirve para la
dirección: lo construido y validado primero —población validada, cuatro fuentes
integradas (incluido el error de códigos invertidos encontrado en la EPC de BCV),
serie con márgenes de diseño, tablero publicado, motor de escenarios (polarización:
promedio quieto, extremos de 19 % a 32 %), evidencia propia sobre IA—, y los
límites después, como conocimiento ganado.

---

## 4. Los números que hay que tener en la cabeza

1. **Las variables puente explican R² ≈ 0,02** de la opinión individual. Ningún motor —LLM incluido— crea información que no está en los datos.
2. **El hot-deck no predice individuos** (r = 0,003) y reproduce la distribución casi perfecto (W1 0,057, sd ratio 0,958). Es un emparejador de distribuciones.
3. **La opinión sintética no tiene geografía propia** (el donante no trae localidad), y **la composición no reproduce la geografía real** (paso 0b).
4. **Dos números exógenos por periodo** (nivel y dispersión, con ladeo categórico) llevan el ajuste al piso de ruido. Es la base del motor de escenarios y del Experimento 9.
5. **Nadie sabe predecir esos dos números mejor que «sin cambio»**: ni el LLM (Exp. 9, 5,17 contra 5,78 veces el piso) ni la tendencia, que es **peor** que no suponer nada (6,82). Para un escenario escrito a mano, extrapolar el último cambio es peor supuesto por defecto que no suponer ninguno.

---

## 5. La distinción que el tablero enseña

**El tiempo se puede leer; la geografía no — salvo donde se mide.** La confianza
medida (ECP) recorre 2,81 → 2,50 → 2,36 → 2,24 → 2,43 con márgenes de ±0,03.
*(Hasta el 29/09 aquí se citaban las medias de la población sintética publicada,
2,81 → 2,53 → 2,39 → 2,24 → 2,45; eran de una corrida que no se podía reproducir
(DI-M2) y ahora, regeneradas, son 2,78 → 2,55 → 2,41 → 2,23 → 2,42. La serie medida
es la cifra que no depende de ninguna corrida.)* La variación entre localidades en la
capa de opinión es composición, no medición (DI-V52, paso 0b). Las capas de
**Crecimiento** y **Voto** sí afirman geografía: proyecciones oficiales y votos contados.

---

## 6. Qué sigue

**Frente activo desde el 30/09 (tarde): reestructuración D17** (`PROJECT_CONTEXT.md`
§39). La página deja de ser solo un tablero: cualquiera le pregunta a la población algo
de opinión o de aprobación de un cambio en la ciudad, y ve la respuesta en total y por
localidad, rotulada como suposición. Cinco piezas: población con la persona completa de
la EPC y emparejada por localidad (reabre DI-B10); preguntas nuevas por «puente» (el LLM
elige qué preguntas medidas se relacionan; cada agente responde con sus propios datos);
reformulación sugerida de la pregunta; consultas independientes; validación
pre-registrada con preguntas de respuesta conocida.
**Hecho el 30/09:** inventario de la EPC por pregunta (`DATA_INVENTORY.md` §13.8,
`src/population/inventario_epc.py`). 272 preguntas de respuesta única; 26 en las diez
olas (el núcleo de opinión urbana) y 60-114 preguntas generales por ola, con 67-81
personas por localidad. 93 casos que el diccionario da y el archivo no tiene.
**Ola base: 2023** (Daniel, 30/09): 114 preguntas generales, 80 personas por localidad.
**Especificado el 30/09, sin código:** `POBLACION_EPC2023_SPECIFICATION.md` (20.000
agentes, localidad como bloque exacto, cada agente guarda el identificador de su
donante, margen de la encuesta por bootstrap de conglomerados) y el pre-registro
`PUENTE_SPECIFICATION.md` (12 preguntas escondidas; el puente tiene que ganarle a la
demografía y al azar al ordenar personas y localidades; el nivel se prueba aparte y,
aun si pasa, queda editable). **Población construida y verificada el 30/09** (`src/population/poblacion_epc.py`, 9
pruebas; §6.1 de su especificación): 20.000 agentes, 1.000 por localidad (Sumapaz sin
donante); 67 de 1938 pares pregunta × localidad fuera del margen (3.5 %,
umbral 10 %); reproducible. Catálogo de 102 preguntas. Tercer error de documentación de
BCV: la etiqueta de `GG3` 2023 (corregida, DI-PE7). El puente quedó con 91 preguntas
(enmienda 1). **Código del puente listo el 30/09** (`src/experiments/puente.py`, 11 pruebas con datos
inventados; §8.1 del pre-registro). **Corrido el 30/09** (`PUENTE_RESULTS.md`, 36 llamadas, USD 0,051): **lectura B.** El puente
ordena a las personas mucho mejor que la demografía y el azar en las 12 preguntas (ρ mediana
0,44 contra 0,04), pero en localidades le gana a la demografía en 7 de 12 (hacían falta 8).
El nivel pasa justo (8 de 12) y queda editable. Lo que más pesa: **la confiabilidad de las
medias por localidad de la propia EPC es de 0,16 (mediana, dos mitades)**; con 80 personas
por localidad y una sola ola, casi no hay geografía que reproducir, tampoco en el mapa de
las preguntas del catálogo. Consecuencia para la página: preguntas nuevas por grupos, mapa
solo para el catálogo y con su margen muy visible; la mejora del mapa es de datos (juntar
olas), no de modelo. **Siguiente, elegido por Daniel:** la reformulación sugerida.
**Reformulación (30/09):** pre-registrada en `REFORMULACION_SPECIFICATION.md` (24 preguntas de
prueba con su alcance esperado: 8 del catálogo dichas de otra forma, 10 nuevas, 6 fuera de
alcance) y con código (`src/consulta/reformular.py`, 7 pruebas con modelo simulado).
**Validada el 30/09** (`REFORMULACION_RESULTS.md`, 24 llamadas, USD 0,081): **24 de 24**, las
cuatro condiciones se cumplen y entra a la página. Las diez reformulaciones de preguntas nuevas
salen neutrales; las alternativas que sugiere para lo que está fuera de alcance no siempre
(dos tendenciosas), así que en la página una alternativa vuelve a pasar por la reformulación
antes de responderse. **Consulta de punta a punta y página nueva (30/09)** (`PAGINA_CONSULTA.md`, `src/consulta/`):
un servidor local (`python src/consulta/servidor.py`, en `127.0.0.1:8765`) une las tres
piezas y sirve una página rehecha por completo, a pedido de Daniel: portada con qué es y
cómo usarlo, espacio para preguntar con sugerencia editable, resultado y mapa grande con
información general por localidad. **Sin los botones de capas del tablero.** Una pregunta
del catálogo tiene mapa con margen; una nueva, grupos y nivel editable, sin mapa; una fuera
de alcance, su razón y una alternativa que se vuelve a reformular. 8 pruebas; revisada en
el navegador en modo simulado. **Siguiente:** abrirla con el modelo real y probarla con
preguntas de verdad. Pendiente para después: juntar olas de la EPC para el mapa.
**Página rediseñada (30/09, tarde):** sistema de diseño de Daniel (`DESIGN.md`, Metaview), la
composición de su referencia de Refero, un solo clic para responder, nada encima del mapa y
una tabla de localidades; pautas de la skill ui-ux-pro-max (`PAGINA_CONSULTA.md` §5.1-5.4).
**Opción 1, juntar olas (30/09):** `DATA_INVENTORY.md` §13.9. Juntando 2022-2024, 74 preguntas
pasan de ~80 a ~250 personas por localidad y la confiabilidad de sus medias por localidad casi
se duplica (0,19 → 0,37; muestra completa 0,32 → 0,54). 2025 queda fuera (sin etiquetas que
verificar) y las evaluaciones del gobierno de turno solo juntan 2022-2023. **Especificado y pre-registrado el 30/09:**
`POBLACION_EPC2022_2024_SPECIFICATION.md` (~4.500 donantes, ~250 por localidad, emparejados
sin educación porque 2024 no la pregunta) y `PUENTE_LOCALIDADES_SPECIFICATION.md` (las 11
escondidas del catálogo, con los 36 puentes ya guardados, sin gasto; P1: el puente le gana a
la demografía por localidad en 8 de 11; declara que no es del todo a ciegas). **Corrida el 30/09,
sin gasto** (`PUENTE_LOCALIDADES_RESULTS.md`): contra el pre-registro, 11 de 11 (lectura A). Pero
el ruido, sin geografía, dio r_loc 0,77: el puntaje y la respuesta salen de las mismas personas y
el ruido de muestreo se correlaciona solo. Con un control de mitades (no pre-registrado), el puente
gana 6 de 11 y 3 de las 7 con geografía. **Daniel: «mantenemos B»** (D17 actualizada).
**Población 2022-2024 construida y verificada el 30/09** (`src/population/poblacion_epc_olas.py`,
§7 de su especificación): 4.522 donantes, 1,2 % de pares fuera del margen, 98 % de
emparejamiento exacto. Al construirla apareció que el `PONDERA` de 2022 no corrige el
sobremuestreo de las localidades pequeñas; se reescala por ola × localidad (DI-PO5).
**Conectada a la página el 30/09** (`PAGINA_CONSULTA.md` §5.5): cada pregunta del catálogo
responde con los donantes de sus años y lo dice; sin grupo de educación; el puente estandariza
por año. ~~**Siguiente:** abrir la página con el modelo real (pocas llamadas, con permiso).~~
Probada con el modelo real el 30/09 (4 preguntas, USD 0,010; `PAGINA_CONSULTA.md` §5.5) y
arreglados sus detalles (DI-CO9 a DI-CO11). **Pre-registrado el 1/10:**
`PUENTE_SIN_BASE_SPECIFICATION.md`, que deja al puente decir «no hay con qué» cuando una pregunta
nueva no se parece a nada de la encuesta, y lo prueba con 30 preguntas (10 con pariente directo,
10 solo del tema general, 10 sin pariente) más la regresión de las 12 escondidas; 126 llamadas.
Clases revisadas por Daniel sin cambios. **Corrido el 1/10** (126 llamadas, USD 0,27;
`PUENTE_SIN_BASE_RESULTS.md`): el modelo nunca dijo «sin base» donde había base, pero solo en 5 de
las 10 sin pariente (P1 falla): **la página no usará sin_base**. La fuerza sí separa los casos (P3):
**la página mostrará «base fuerte / media / débil»**. Nada de lo validado se rompió (12 de 12).
Daniel eligió la opción 1: si el v2 dice «sin base», se pide el puente de siempre y se muestra
como **base débil**. **Llevado a la página el 1/10** (`PAGINA_CONSULTA.md` §5.6, DI-CO12).
**Biblioteca pública del CNC (1/10):** revisada y con seis informes descargados fuera del repo
(`DATA_INVENTORY.md` §15). Una encuesta de Bogotá de agosto de 2023 trae dos preguntas que la EPC no
hizo (metro elevado, Corredor Verde) con resultados por grupo y localidad. **Pre-registrado el 1/10:**
`PREGUNTAS_REALES_NUEVAS_SPECIFICATION.md` (P1: el puente acierta ≥ 70 % de las 24 diferencias
claras entre grupos y le gana al azar). **Corrido el 1/10** (6 llamadas, USD 0,014;
`PREGUNTAS_REALES_NUEVAS_RESULTS.md`): **P1 falla, 8 de 24**, menos que el azar; en el Corredor
Verde el puente invirtió el orden (2 de 13): eligió preguntas del mismo tema (árboles, zonas verdes)
que no predicen quién lo apoyaba. Por la regla, la página debe dejar de mostrar de entrada las
barras por grupo en preguntas nuevas: **aplicado el 1/10** (`PAGINA_CONSULTA.md` §5.7, DI-CO13).
**Rumbo acordado con Daniel (1/10):** que las preguntas nuevas se acerquen a resultados reales,
usando la API cuando ayude. Plan: un banco de preguntas nuevas con respuesta real, separado en
práctica y guardado; mejoras al puente en el de práctica; prueba final pre-registrada en el guardado.
**Inventario del banco el 1/10** (`BANCO_PREGUNTAS_NUEVAS.md`): ~100 candidatas en cuatro fuentes (EPC de
otros años, preguntas sueltas de la EPC, Cultura Política del DANE, biblioteca del CNC).
Diccionario de la ECP descargado; 336 candidatas clasificadas con la API (USD 0,09): **171 útiles**.
**Sorteo hecho el 1/10** (semilla 20261001, `BANCO_PREGUNTAS_NUEVAS.md` §8): 114 de práctica y 51
guardadas (solo 5 de Bogotá). Resultados reales de la práctica calculados (1/10, `BANCO_PREGUNTAS_NUEVAS.md` §9): **96 preguntas,
699 diferencias claras**, tras una regla de estructura que sacó 18. **Práctica corrida el 1/10** (USD 1,39;
`BANCO_PREGUNTAS_NUEVAS.md` §10.1): las dos versiones del puente ordenan bien el 60-61 % de las
diferencias entre grupos; el **tono general**, sin API, el 62 %. El puente no aporta sobre «quién suele
responder favorable». Último intento (perfiles del catálogo y ejemplos
resueltos, validación cruzada; §10.3): **0,627 < 0,67, se para por la regla escrita.** En total la
práctica costó USD 2,33. ~~**Siguiente:** llevar a la página el camino 2 (tono general por grupo en
preguntas nuevas) y escribirlo como decisión de proyecto.~~
**D18, aprobada y en la página el 2/10** (`PROJECT_CONTEXT.md` §39, `PAGINA_CONSULTA.md` §5.8): una
pregunta nueva no tiene cifra propia. Muestra las preguntas medidas que el modelo relaciona, con lo que
la gente respondió de verdad y enlace a su mapa, y el tono general por grupo rotulado «Así suelen
responder estos grupos en la encuesta». Sin nivel ni fuerza. **Ninguna cifra que se ve sale del modelo.**
Ese mismo día, tras verla Daniel: la respuesta empieza diciendo «No podemos decir si Bogotá estaría de
acuerdo» (DI-CO20); escalas numéricas, lado favorable y «no tiene opinión» arreglados (DI-CO17 a CO19).
**Techo de los grupos (2/10, pre-registrado, sin gasto; `TECHO_GRUPOS_RESULTS.md`): lectura A, hay
espacio.** Quien conociera la opinión real acertaría ~95 % de las diferencias claras entre grupos; otra
encuesta de mitad de tamaño, 86 %; el simulador, 62 %. La distancia es información que no tenemos, no
ruido. **Siguiente, propuesto a Daniel:** camino 2 (el nivel con preguntas parecidas de respuesta
conocida) y camino 3 (pedir al CNC resultados agregados de preguntas de aprobación en Bogotá).
**Camino 2, parte A sin API (2/10, pre-registrada; `NIVEL_PARECIDAS_RESULTS.md`):** el promedio del banco
se equivoca 23 puntos en el porcentaje favorable; ni el mismo tema (23,4) ni los vecinos por texto (22,0)
lo bajan un 20 %. Con hermanas de la misma serie, 16,1. **Vara de la parte B (con el modelo): 17,6 o menos.**
**Alternativa 1, la forma de la pregunta (2/10, pre-registrada, sin gasto; `NIVEL_FORMA_RESULTS.md`):** una
regresión con fracción favorable, tipo, «no conoce» y Bogotá da 22,3: **no pasa** (umbral 18,4). Patrón de las
tres pruebas: con una pregunta hermana medida, ~16 puntos; sin ella, ~22-23 (el promedio). **Lo que acerca el
nivel son datos (preguntas casi iguales ya medidas), no un método.** Opciones abiertas para Daniel: camino 3
(resultados agregados del CNC) o probar un modelo de lenguaje más fuerte (con costo).
**Parte B, modelos más fuertes (2-5/10, pre-registrada, USD 2,38; `NIVEL_PARECIDAS_B_RESULTS.md`):** Claude
Sonnet 5.5 eligiendo preguntas parecidas da 18,1 puntos (vara 17,6): **no pasa, por 0,5**. Toda su ventaja está
en las preguntas generales; en las de Bogotá no mejora. DeepSeek V4 Pro sin razonar, 21,6. **Se cierra el
camino 2 con modelos de lenguaje.** El banco se amplía con fuentes públicas: lote 2, Cultura Ambiental 2021
(16 preguntas); lotes 3 y 4, Bienal de Culturas 2025 y Barrios Vivos 2025, pre-registrados el 5/10.
**Techo en el banco ampliado (5/10, pre-registrado, sin gasto; `TECHO_GRUPOS_LOTES_RESULTS.md`):** lectura A otra
vez (oráculo 0,960, réplica 0,863), pero **el tono general del simulador acierta 0,466 en los lotes 2 y 3: peor que el
azar**. Explicación posible, no pre-registrada: en afirmaciones negativas el tono acierta al revés (0,36) y en las
positivas apenas pasa el azar (0,54). **El «62 %» de la página no se generaliza: decisión pendiente para Daniel**
sobre el tono por grupo de D18. **Resuelta el 5/10 (opción 3):** se muestra como contexto descriptivo, sin cifra de acierto (DI-CO21).
**¿Estaría Bogotá de acuerdo? Paso 1 (5/10, pre-registrado, sin gasto; `NIVEL_ACUERDO_RESULTS.md`):** en 92 preguntas
de acuerdo o sí/no, el mejor método (vecinos por texto) acierta el lado de la mayoría el 63 %, contra 57 % de decir
siempre el lado mayoritario, y yerra 18 puntos en el porcentaje. **No llega a la regla:** la página sigue sin decir
«sí» o «no». Lo siguiente, a decidir por Daniel: Sonnet sobre este subconjunto (~USD 2) o el camino 3.
**Paso 2, Sonnet (5/10, pre-registrado, USD 1,73; `NIVEL_ACUERDO_SONNET_RESULTS.md`): pasa la regla.** Error 13,9
puntos, acierta el lado de la mayoría el 80 % (contra 57 % de la referencia) y, cuando su rango no cruza el 50 %,
acierta 16 de 16. Primer método que cruza la vara. **No va a la página todavía:** sigue la validación pre-registrada
en el guardado.
**Validación en el guardado (5/10, pre-registrada, USD 1,47; `NIVEL_ACUERDO_VALIDACION_RESULTS.md`): pasa.** En 74
preguntas que nadie había mirado: error 12,5, lado de la mayoría 77 % (referencia 51 %), y al decidir 12 de 12 (28 de
28 entre práctica y guardado). ~~**Siguiente: D19, cómo mostrarlo en la página (decisión de Daniel).**~~ **D19 aprobada y en la página el
5/10:** «probablemente sí / no / dividida», con porcentaje, rango de ±21,9 y las preguntas en que se apoya (DI-CO22).
**¿Alcanza mimo? (5/10, pre-registrado, USD 0,54; `NIVEL_ACUERDO_MIMO_RESULTS.md`): no.** Se acerca (error 16,2 y
13,5; lado 73 % y 72 %), pero falla la práctica por 0,4 puntos y, al decir «probablemente», acierta 18 de 21 contra
28 de 28 de Sonnet. Sigue Sonnet. **Banco ampliado con el lote 5** (Encuesta Distrital de Percepción 2025, SDP): 38
afirmaciones de acuerdo; banco en 411 preguntas.
**Candidatas con el lote 5 (5/10, pre-registrado, USD 2,73; `NIVEL_ACUERDO_LOTE5_RESULTS.md`): B (109 candidatas)
reemplaza a A (92).** En 95 guardadas: error 11,9 contra 12,8; al decir «probablemente», 17 de 17 contra 12 de 12; en
las 21 del lote 5, error 9,9 contra 13,6. **En la página desde el 5/10 (DI-CO23).**
**Rediseño de la página (5/10, variante B; `PAGINA_CONSULTA.md` §5.16).** El mapa se colorea frente a la ciudad.
**La estimación, tal como la sirve la página (5/10, `NIVEL_ACUERDO_REDACCION_*`):**
- **Parte B (sin gasto):** estirar o corregir la estimación no ayuda.
- **Parte A** (la reformulación de la página): quedó a medias porque la cuenta se quedó sin saldo. Las 46 preguntas con
  estimación, sin evaluar, apuntan a una pérdida de precisión.
- **Arreglos (DI-CO24, DI-NB6):** los errores del servicio ya se dicen como tales, y ya no se pierden las respuestas
  en que el modelo se corrige.

**GPT-6 Luna (6/10, pre-registrado, USD 0,19; `NIVEL_ACUERDO_LUNA_RESULTS.md`; D20).**
- **En la prueba:** cumple las tres condiciones de la regla de Sonnet, pero se equivoca 2,4 puntos más en el guardado
  (14,3 contra 11,9) y no pasa la cuarta.
- **Decisión de Daniel:** cambiar igual, por costo (20 veces menos por pregunta). La página cita sus cifras: 69 % del
  lado de la mayoría; 10 de 11 al decir «probablemente»; ±23,4.
- ~~**Siguiente:** terminar la parte A con Luna (~USD 0,10).~~ Hecho (6/10):
  - **La parte A con Luna no se sostiene.** Con la reformulación de la página, la estimación empeora: error 16,2 contra 14,0;
    lado 63 % contra 69 %; 5 de 6 al decidir. La pérdida está en las extremas, porque la reformulación a veces cambia el sentido.
  - **La reformulación y el puente pasan a Luna** (`LUNA_PAGINA_RESULTS.md`, USD 0,28, DI-CO26), y pasan su validación.
    Toda la página va con Luna, a ~USD 0,003 por pregunta nueva.
  - ~~**Siguiente:** corregir el texto de la página con las cifras con reformulación, y pre-registrar darle al modelo el
    texto de la persona.~~ Hecho:
    - el texto pasó a 63 % (DI-CO27);
    - estimar con el texto de la persona pasó su prueba (`TEXTO_PERSONA_RESULTS.md`, USD 0,10): error 15,6 contra 16,7, lado 68 %;
    - la página lo hace desde DI-CO28.
  - **Siguiente:** medir la ganancia con preguntas escritas por personas, no copiadas de una encuesta.

**Encuestas políticas del CNC (6/10, D21):** 10 estudios para Semana y Revista Cambio, solo de Bogotá.
- **Lote 6, opinión política:** 64 preguntas, con dos enmiendas (mínimo de 200 respuestas; CC355801 sí trae edad).
- **Lote 7, intención de voto:** 373 preguntas, electorales. Fuera de la página hasta la revisión jurídica; su guardado
  queda para el nivel 3.
- **La estimación usa ahora 139 candidatas,** con las 30 del lote 6 (`NIVEL_ACUERDO_LOTE6_RESULTS.md`, DI-CO29).
- **Los resultados agregados de estas encuestas no se suben a GitHub;** viajan con el traslado.
- ~~**Siguiente:** el pre-registro del nivel 3, simular la intención de voto.~~ **Nivel 3, parte 1 (7/10,
  `VOTO_SIMULADO_RESULTS.md`, USD 0,41): cumple la regla.**
  - Error de 3,7 con su encuesta y 4,3 sin ella; acierta quién va adelante en el 94 % de las segundas vueltas.
  - Pero el promedio lo bajan los candidatos pequeños: con los de más del 15 %, el error es de unos 6 a 7 puntos.
  - Nada se muestra sin revisión jurídica.
  - Por el camino, la caché con punto de corte (DI-E11) bajó el costo por llamada un 80 %.
  - ~~**Siguiente:** la parte 2, contra la Registraduría, en el PC personal; y la revisión jurídica.~~
  - **Parte 2, contra la Registraduría** (`VOTO_REGISTRADURIA_RESULTS.md`, USD 0,024): se corrió en este PC con
    `Desktop\CNC_datos`. En tres elecciones en Bogotá, la simulación se equivoca 4,2 puntos y la última encuesta 3,8, y las
    dos aciertan al ganador.
  - **La caché en la página no pasó su regla** (`CACHE_PAGINA_RESULTS.md`): al decidir acierta 13 de 15. La página sigue
    sin caché.
  - ~~**Siguiente:** la revisión jurídica del nivel 3.~~ **Revisión jurídica aprobada (7/10, D21).**
  - **La intención de voto está en la página** (7/10, `PAGINA_CONSULTA.md` §5.22, DI-CO30). La reformulación v3 la reconoce
    sola (`REFORMULACION_VOTO_RESULTS.md`, 13 de 13). Muestra la estimación con ±7 puntos y las encuestas del CNC en que se
    apoya, sin mapa. Las consultas y la tendencia quedan fuera.
  - ~~**Siguiente:** probarla con el modelo real.~~ **Probada con Luna (8/10):** Cepeda, 36 % (29–43 %), apoyado en sus dos
    encuestas de 2026. De paso se corrigió un defecto de la caché del modo simulado (DI-CO31).
  - **El peso por fecha no pasó (8/10, `VOTO_PESO_FECHA_RESULTS.md`, USD 0).** La práctica eligió τ = ∞, el promedio
    simple, así que la página sigue igual. En las guardadas, ninguna τ finita mejora (4,0 contra 3,7) ni acierta más
    segundas vueltas (30 de 32).
  - **La reformulación pasa a la versión 4 (8/10, `REFORMULACION_MATIZ_RESULTS.md`, USD 0,052).** Reconoce una pregunta
    del catálogo dicha con un matiz («caminando por su barrio» → `VS8`) y no manda al catálogo las que son distintas.
  - **Versión 5 (8/10, `REFORMULACION_GOBIERNO_RESULTS.md`, USD 0,065):** no confunde a Galán con Claudia López. La EPC no
    mide a Galán, y la página dice qué gobierno midió cada pregunta. Además, las respuestas medidas se pueden ver como
    negativa, neutral y positiva (DI-CO36). Lo pidió el jefe de Daniel.
  - **MiroFish ante la segunda vuelta 2026 (9/10, `MIROFISH_SEGUNDA_VUELTA_RESULTS.md`, USD 0,06).** Instalado en local,
    fuera del repositorio. Dio Cepeda 53 % en Bogotá; el real fue 53,6 % sobre los dos. Pero la cifra no salió de la
    simulación: sus agentes eran actores del documento, no votantes, y el informe reescaló la primera vuelta. Pasa a la
    segunda prueba, la percepción de Galán.
  - **MiroFish ante la aprobación de Galán (9/10, `MIROFISH_GALAN_RESULTS.md`, USD 0,05): no pasa.** Dio 46 %; el real
    (EPC 2025 de Bogotá Cómo Vamos) fue 26 %. El simulador dio 47,3 % («dividida», rango 25,6 a 69,0). La aprobación de
    Claudia López en la EPC anterior (33,1 %) se equivocó menos que los dos. MiroFish queda para explorar narrativas, no
    para dar cifras: sus agentes son instituciones, no residentes.
  - **MiroFish no distingue entre alcaldes (9/10, `MIROFISH_DISCRIMINACION_RESULTS.md`, USD 0,13).** Contra Invamer de junio
    de 2025: Medellín 79 % → dijo 50; Bogotá 42 % → 45; Cali 30 % → 51. A todos les da «la mitad», y a Cali la cifra más
    alta. No sirve para porcentajes. **Siguiente, si se quiere seguir:** agentes con perfiles de residentes, entrevistados
    antes de cerrar la simulación.
  - **MiroFish con residentes de Bogotá, entrevistados (9/10, `MIROFISH_RESIDENTES_RESULTS.md`, USD 0,15): no pasa.** Error
    30,8 contra 17,2 de decir 50 % para todo. Luna se sale del personaje y se niega a opinar: 10 de 11 «no tengo
    información» sobre Galán. Con lo medido, el simulador ordena las cinco preguntas de la EPC 2025 (Spearman 0,70, error
    15,1). **MiroFish queda para explorar narrativas, no para cifras.**
  - **TinyTroupe con residentes de Bogotá (13/10, `TINYTROUPE_RESIDENTES_RESULTS.md`, USD 0,46): no pasa.** A diferencia de
    MiroFish, sus residentes sí opinan, pero en bloque: orgullo 100 %, buen camino 0 % a 9 % (real 59 %). Error 27,2 con 12
    residentes y 29,1 con 24 generados por su fábrica, contra 15,1 del simulador. **Las herramientas de personas
    sintéticas quedan descartadas para cifras de opinión.**
  - **La EPC 2025 entra al simulador (13/10).** Paso 1 hecho: verificada contra su formulario (`DATA_INVENTORY.md` §13.10),
    40 preguntas se pueden juntar, y los datos reproducen lo publicado por BCV. Paso 2, pre-registrado:
    `POBLACION_EPC2022_2025_SPECIFICATION.md`, con ~330 personas por localidad y la gestión de Galán como dato medido
    (2024-2025).
    - **Paso 3, construida (13/10, USD 0, §8 de su especificación).** Enmienda 1, a pedido de Daniel: sin las 23
      evaluaciones del gobierno de Claudia López (los datos no se borran). 6.042 donantes, mediana 312 por localidad,
      84 preguntas (79 y 5 de Galán). Pasa la verificación: 2,0 % de pares fuera del margen. Los donantes de 2025
      reproducen exacto las cifras de BCV. PP1 a PP3 se cumplen.
    - ~~**Siguiente (paso 4):** la página apunta a la población nueva, con la validación de la reformulación (§4 y
      enmienda 1, unos USD 0,06, con visto bueno) y PP4.~~ **Paso 4 hecho (13/10, USD 0,053, DI-CO38,
      `REFORMULACION_2025_RESULTS.md`).** La página usa la población 2022-2025 y su catálogo de 84 preguntas. La
      reformulación pasa 12 de 12: Galán va a sus preguntas medidas y López queda como «nueva». La aprobación de Galán
      sale de un dato medido: 33,9 % (real 2025: 26,4 %; antes, la estimación daba 47,3 %). En las cinco de la EPC 2025, el
      error medio baja de 12,9 a 8,3 (PP4, no es a ciegas). Falta que Daniel revise la página.
    - **Peso por año reciente: no pasa (13/10, USD 0, `PESO_ANIO_RECIENTE_RESULTS.md`).** Adivinando 2025 con la
      población 2022-2024, la media vida de un año baja el error de la ciudad de 4,43 a 4,06. Es menos de 0,5, así que
      la página sigue juntando los años igual. En cinco preguntas 2025 se movió más de lo que ningún peso alcanza (buen
      camino, hambre, victimización). La cifra de Galán por año, que proponía el pre-registro, no se hace: Daniel la descartó.
    - **Lote 8 del banco (EPC 2025): no pasa (14/10, USD 0,220, `NIVEL_ACUERDO_LOTE8_RESULTS.md`).** Sumar 15 preguntas
      de la EPC 2025 a las candidatas deja el error igual (15,6 contra 15,7) y acierta menos al decidir (80 %). La página
      sigue con las 139. Lo que mostró: la estimación se queda cerca del 50 % cuando no hay una pregunta casi igual. En
      confianza en instituciones (reales de 10 % a 19 %) dio cerca de 50 %, y se equivocó por 30 a 44 puntos.
    - **El catálogo como candidatas: pasa (14/10, USD 0,277, `NIVEL_ACUERDO_CATALOGO_RESULTS.md`, DI-CO39).** Con las 84
      preguntas del catálogo entre las candidatas, el error baja de 15,6 a 15,3, y en las 10 de la EPC 2025 de 25,9 a 14,2;
      en las 129 de siempre sube de 14,8 a 15,4. La confianza en el Concejo pasa de 53 % a 20 % (real 13 %). La página ya
      estima con las 223.
    - **Validación 2026: no pasa (14/10, USD 0,023, `VALIDACION_2026_RESULTS.md`).** Seis preguntas nuevas con resultado
      publicado en 2026: cuatro del metro y dos de la Encuesta Distrital. El real cae en el rango en 3 de 6 (la regla pedía
      4). Se equivoca menos que decir 50 % (16,8 contra 26,8), pero no decidió en ninguna. En el metro, con reales de 80 % a
      93 %, dio de 56 % a 62 %. Corrección: una de las seis (el metro en 2028) sí estaba en el banco; el pre-registro decía
      que no.
    - **Validación CNC 2026: no pasa (14/10, USD 0,031, `VALIDACION_CNC_2026_RESULTS.md`).** Siete preguntas de opinión de
      las encuestas del CNC para Revista Cambio de enero y abril de 2026. El real cae en el rango en 5 de 7, y la única vez
      que dijo «probablemente» acertó. Pero su error (12,7) no le gana a decir 50 % (10,6). Por D21 no se reporta ningún
      porcentaje del CNC.
    - **Estimación aprendida (opción A): no pasa (14/10, USD 0,0002, `ESTIMACION_APRENDIDA_RESULTS.md`).** Un modelo entrenado
      con las 238 preguntas con resultado, sobre embeddings del texto, se equivoca más que la de hoy (18,0 contra 15,3) y
      nunca se compromete. Luna elige mejor que el parecido del texto, y 238 ejemplos son pocos para aprender. La página
      sigue igual. Lo que queda es la opción B (gemelos con entrevistas), que es decisión de Daniel y su jefe.
    - **Compresión hacia el medio (14/10, USD 0, `COMPRESION_RESULTS.md`).** Es la prueba de amplitud del marco de
      Artificial Societies. Las estimaciones se mueven menos que los reales (16,5 contra 23,9), pero la pendiente es 0,95:
      no es una escala aplanada, es falta de información. Estirarlas no baja el error (15,6 contra 15,3) y la página no cambia.
    - **Efecto de la redacción: robusta (14/10, USD 0,075, `REDACCION_RESULTS.md`).** Diez preguntas escritas de tres formas.
      La cifra cambia 2,2 puntos en promedio; en el benchmark de Artificial Societies, el mejor modelo de lenguaje cambia
      6,2 y su sistema 1,4. Lo frágil es el alcance: una pregunta nacional salió «fuera» en dos de tres redacciones.
    - **Precisión por grupos (14/10, USD 0, `GRUPOS_2025_RESULTS.md`).** Adivinando 2025 por estrato, edad y sexo, la página
      se equivoca 4,73 por grupo y 4,82 con la cifra de la ciudad para todos: no pasa la regla. Pero acierta la dirección de
      las brechas (correlación 0,58; en edad, 91 % cuando la brecha pasa de 3 puntos). Los grupos de Bogotá se parecen: se
      apartan 2,3 puntos de la ciudad, menos que el error de nivel.
    - **Rango según el acuerdo de las elegidas: no pasa (14/10, USD 0, `RANGO_ACUERDO_RESULTS.md`).** Un rango más angosto
      cuando las preguntas de apoyo coinciden hace que la página se comprometa en 32 de 139 en vez de 19, pero acierta el 84 %
      en vez del 89 % (la regla pedía 90 %). La página sigue con el rango de hoy. Es un intercambio que podría decidirse como
      producto.
    - **Mapa apoyado en la ciudad: no pasa (14/10, USD 0, `MAPA_ENCOGIDO_RESULTS.md`).** El encogimiento de áreas pequeñas
      baja el error por localidad de 7,94 a 7,65, menos que el medio punto pedido. El hallazgo es otro: el orden de las
      localidades que da el mapa con 2022-2024 casi no se relaciona con el de 2025 (Spearman 0,045). El mapa no sirve para
      decir qué localidad está mejor o peor.
      Daniel pidió que la página lo diga en el mapa (`PAGINA_CONSULTA.md` §5.30).
    - **Personas con su encuesta: no pasa por poco, pero es lo más cerca que se ha llegado (14/10, USD 0,056,
      `PERSONAS_CON_ENCUESTA_RESULTS.md`).** Idea de Daniel: un agente por encuestado real de la EPC 2025, con sus 40
      respuestas. En 6 preguntas escondidas acierta a cada persona mejor que una constante y que una regresión (21,9 contra
      26,3 y 23,8), y el total mejor que la página (10,0 contra 12,2). Pero conserva solo el 56 % de la variación (la regla
      pedía 60 %): en tres preguntas dijo que nadie confía o está satisfecho.
    - **EPC 2026: descartada por ahora** (14/10, Daniel). No ha salido; la de 2025 se presentó el 4 de diciembre de 2025.
    - **Personas pulidas: no pasa la prueba final (14-15/10, USD 0,80, `PERSONAS_PULIDAS_RESULTS.md`).** Pedir
      probabilidades en vez de una opción corrige el «nadie confía»: en el desarrollo, el error del total baja de 20,8 a 9,5.
      En la prueba final, con personas y preguntas nuevas, queda en 15,3 contra 15,0 de la página. Acierta muy bien en 4 de 8,
      y en las otras 4 queda 23 a 31 puntos por debajo: supone a la gente menos satisfecha de lo que está.
    - **Personas en lo político (15/10, USD 0,43, `PERSONAS_POLITICA_RESULTS.md`).** En 10 preguntas de gobierno y del
      alcalde, con 200 personas nuevas, el agente con su encuesta se equivoca 7,4 a 7,8 en el total contra 14,3 de la
      página, y acierta casi exacto la gestión de Galán (26,2 contra 26,4). Completar el perfil con su vida real, un resumen o
      una vida inventada no cambia nada. Falla por poco la regla de reparto (TVD 0,164; pedía 0,15). Las encuestas del CNC
      quedan de lado por ahora (D21).
    - **Agentes en preguntas nuevas de 2026: no le ganan a la página (16/10, USD 0,85, `AGENTES_2026_RESULTS.md`).** Con las
      13 preguntas de 2026, Luna se equivoca 15,2 contra 14,6 de la página. En las 7 del CNC gana (9,0 contra 12,7 y 10,6 de
      decir 50 %), y en las del metro pierde. Promediar con DeepSeek empeora y cuesta nueve veces más. Cerrada con DeepSeek en
      150 de 200 (enmienda 1).
    - **Saldo de OpenRouter (16/10):** a la cuenta le quedan unos USD 0,24. Hay que recargarla antes de usar el modelo real.
    - **D22 (16/10): las preguntas nuevas políticas e institucionales se estimarán con agentes.** Decisión escrita en
      `PROJECT_CONTEXT.md` §39. Construido en modo simulado (`agentes.py`, DI-CO40, `PAGINA_CONSULTA.md` §5.31): un botón en el
      resultado de una pregunta nueva, con la cifra, un rango de ±12,6 y los grupos. **Falta:** las dos validaciones de D22,
      con el modelo real, después de recargar la cuenta: que la reformulación reconozca lo político, y una prueba con preguntas
      políticas nuevas.
    - **D23 (16/10): en lo político, el proyecto busca acercarse lo más posible a predecir 2026.** La percepción política se
      trata como pregunta nueva, respondida por agentes, con el dato medido al lado; la intención de voto también se prueba con
      agentes. Primera pieza pre-registrada: `VOTO_AGENTES_SPECIFICATION.md`, los agentes de la EPC contra la Registraduría en la
      primera vuelta de 2026 en Bogotá. ~~**Espera la recarga de OpenRouter** (unos USD 0,90).~~
    - **Voto con agentes: no sirven todavía (16/10, USD 0,064, `VOTO_AGENTES_RESULTS.md`).** Con 200 agentes, error de 8,1
      entre los 11 candidatos (la regla pedía 5,4; la estimación de hoy, 3,4). Aciertan el ganador, Cepeda, pero reparten el voto
      como en una elección abierta: no ven la polarización (Cepeda y De la Espriella, 81 % real). El modelo no conoce la campaña
      de 2026. Siguiente, según D23: un resumen neutral de la campaña, o el ajuste a la última encuesta.
    - **Voto con agentes que conocen la campaña: pasa la regla (16/10, USD 0,144, `VOTO_CAMPANA_RESULTS.md`).** Con un resumen
      de la campaña y la encuesta Invamer del 21 de mayo, los 200 agentes se equivocan 3,5 (la estimación de hoy, 3,4) y aciertan
      a Cepeda primero y a De la Espriella segundo. No le ganan a copiar la encuesta (1,8): la diluyen hacia el centro. Su valor
      posible es repartir la cifra por grupos o en escenarios sin encuesta; eso falta medirlo.
    - **Grupos y Galán 2026 (16/10, USD 0,092, `GRUPOS_Y_GALAN_2026_RESULTS.md`).** Por grupos, los agentes no reparten bien el voto:
      error 6,6 contra 5,5 de no distinguir grupos, y solo el estrato en la dirección correcta. En Galán, el error medio queda en 6,6
      (la regla pedía menos que el 4,5 de la EPC 2025). Sin opiniones de gobierno aciertan la aprobación de Guarumo (54,9 contra 53,3);
      con ellas, la imagen de Global CB (46,9 contra 44,3).
    - **Que no diluyan la encuesta: ni la instrucción ni la calibración (19/10, USD 0,193, `NO_DILUIR_RESULTS.md`).** Las dos
      mejoran la primera vuelta (2,37 y 1,84 contra 3,49) y empeoran la segunda vuelta en Bogotá (15,2 y 7,5 contra 3,4). Lo
      importante: sin instrucción, con solo la encuesta nacional de Guarumo, los agentes dan a Cepeda 50,2 en Bogotá (real 53,6):
      corrigen la encuesta del país (46,1) hacia la ciudad y aciertan el ganador. Le ganan a copiar la encuesta, pero apenas a decir
      50 % (3,4 contra 3,6).
  - **El rango variable pasó por poco (8/10, `RANGO_VARIABLE_RESULTS.md`, USD 0).** El rango depende de cuántas preguntas
    eligió Luna: ±23,9, ±22,9 o ±21,7. En las 129, la página decide en 13 en vez de 11, y acierta 12. Que las elegidas
    coincidan no predice el error (Spearman 0,00). Para decidir más haría falta una estimación más precisa.
  - **La intención de voto por grupos (8/10, `VOTO_GRUPOS_RESULTS.md`, USD 0): pasa solo la edad.** Error 4,8 contra 6,2
    del total, y el sentido acertado en 93 %. El estrato acierta el sentido en 96 %, pero no baja el error lo suficiente
    (0,93 contra 0,9), y el sexo no aporta.
    - ~~**Siguiente:** el diseño de la edad en la página.~~ **En la página** (8/10, `PAGINA_CONSULTA.md` §5.25, DI-CO34),
      revisada por Daniel.
**Traslado a la oficina (1/10):** `docs/TRASLADO.md`; `requirements.txt` completo (faltaban scipy y
openpyxl), `revisar_datos.py` revisa ya lo de la página, y `empacar_traslado.py` lleva lo que no
va a GitHub (cachés, poblaciones; ~4 MB).

**En espera:** la segunda vuelta de 2026 (`SEGUNDA_VUELTA_2026_SPECIFICATION.md`, con
código) no está publicada mesa a mesa; Daniel la pedirá al CNC.

**Frente anterior (30/09): escenarios con preguntas reales.** Las piezas ya funcionan de
punta a punta (población, tablero, motor); lo que falta es que el motor responda una
pregunta de un proyecto real del CNC y que el informe le sirva a quien pregunta. Hecho
el 30/09, antes de empezar:
- `tests/test_scenarios.py` fallaba en esta máquina porque al `venv` le faltaba
  `pyyaml` (estaba en `requirements.txt`; se instaló). Pasan las 14.
- **El motor solo leía `.csv`** y las poblaciones reproducibles (DI-M2) solo existen en
  `.parquet`: no podía usar ninguna. Corregido (DI-E5 en `especificacion.py`, con prueba).

Lo que sigue en este frente:
1. Daniel trae una o dos preguntas de proyectos del CNC: **solo el texto y el
   contexto**, nunca respuestas de personas (R10).
2. Ver si alguna fuente pública (ECP, EPC) mide esa pregunta. La población lleva una
   sola variable (`opinion_t0`: confianza institucional en la ECP, gestión del alcalde
   en la EPC 2014); otra variable es otra población, con `build_agents` y el mismo
   donante.
3. Escribir el escenario (los números los pone una persona, no el LLM: Exp. 9),
   correrlo y revisar el informe con quien hizo la pregunta.

**Primera pregunta real (30/09), del jefe de Daniel:** ¿el simulador acierta que la
población votaría por Abelardo de la Espriella y que ganaría? Así no se puede
responder (el resultado ya se conoce, la población no tiene intención de voto y el
proyecto es de Bogotá, no del país). Se reformuló en una que sí puede fallar:
**¿el polo de derecha de 2014–2022 anticipa en qué localidades le fue mejor y peor a
Abelardo de lo que dice su estrato, primera vuelta 2026?** Pre-registrada en
`POLOS_2026_SPECIFICATION.md`, con la predicción localidad por localidad (§4), antes
de descargar ni mirar nada de 2026. Es también la prueba pendiente de los dos polos.
Código y mundos simulados listos el 30/09 (`src/experiments/polos_2026.py`, 15
pruebas; A 94 % con polo, 0 % sin polo; §8.1). Siguen: descarga de los escrutinios por mesa de la
Registraduría (con permiso, fuera del repo); corrida y resultados.
**Corrido el 30/09** (`POLOS_2026_RESULTS.md`), con la tabla de 2026 bajada de la
Registraduría (`DATA_INVENTORY.md` §14.6): **lectura B, en el borde.** El resto de
Abelardo sigue al polo de derecha con r = 0,51 (P1 pasa por 0,006), pero el polo le
añade al estrato 0,047 fuera de muestra y hacía falta 0,05 (P3 falla). 7 de las 9
localidades nombradas salieron en el sentido previsto; 9 de 19 en total. P2 falla con
claridad: su geografía se parece más al revés de la izquierda (0,84) que al polo de
derecha, así que **la lectura de dos polos se debilita**. No pre-registrado: la derecha
se repartió con Valencia (sumada daría A) y el polo de izquierda se transfirió a Cepeda
(r = 0,93).
**En el tablero desde el 30/09 (DI-V60):** el aviso de residuos dice «en 2014–2022
fueron dos polos» y que la prueba pre-registrada de 2026 no lo confirmó, con sus cifras.

**Segunda pregunta del jefe (30/09): la segunda vuelta de 2026, localidad por localidad.**
Pre-registrada en `SEGUNDA_VUELTA_2026_SPECIFICATION.md` antes de mirar nada de la segunda
vuelta. Predicción: sumando la primera vuelta por bloques, Abelardo gana 10 localidades
(norte, occidente, centro ampliado) y Cepeda 10 (sur y suroriente); Kennedy es una moneda
al aire; **Abelardo gana Bogotá (Cepeda 47,3 %)**. La regla ingenua (cada uno conserva lo
suyo) da los mismos ganadores por localidad, así que lo que decide es el margen y la
ciudad. Código y mundos simulados listos el 30/09 (`segunda_vuelta_2026.py`, 13 pruebas; A
100 % en el mundo de bloques, C 100 % en el ingenuo). Siguen: revisar y descargar la
segunda vuelta; corrida.

**Geografía electoral de Bogotá: cerrada el 30/09.** El 29/09 el CNC entregó
resultados electorales por mesa (presidente 2014, 2018 y 2022; Senado y Cámara 2018)
y por municipio, sin datos de personas. **D16** los saca de R10 (se pueden leer con un
LLM; viven fuera del repo, en `BSS_ELECTORAL_DIR`); inventario en `DATA_INVENTORY.md`
§14. Bogotá viene en 22 zonas: si las 1–20 son las localidades, es la primera
geografía real dentro de la ciudad que tiene el proyecto. **Verificado el 29/09:
zona = localidad** (r = 0,991 en tamaño; nombres de puesto coinciden; §14.3), con
la zona 90 (Corferias, 7,6 %) sin localidad y un sesgo de inscripción hacia el centro.
**Tabla construida el 29/09:** `data/external/electoral/presidente_1v_*` (2014, 2018,
2022 por localidad; verificada contra los archivos municipales; §14.4).
**Corrido el 29/09** (`GEOGRAFIA_ELECTORAL_RESULTS.md`): el estrato explica el 84 % de
la geografía del voto por Petro 2022 (R² fuera de muestra), y lo que no explica **se
repite** (r = 0,87 entre 2018 y 2022) como un eje izquierda–derecha estable desde 2014:
el centro y el suroriente, más a la izquierda de lo que dice su estrato; el
noroccidente, menos. Cinco de cinco predicciones; **lectura B: hay territorio estable
que la composición no ve.** Sobrevive a la inscripción (pre-registrado) y a la
participación (no pre-registrado). Refuerza el paso 0b y es evidencia para reabrir
DI-B10.
**En el tablero desde el 29/09:** capa **Voto** (DI-V53 a DI-V56), con el voto por
localidad de los 9 candidatos y «lo que el estrato no explica», más una vista
exploratoria con participación. 35 pruebas en `tests/test_viz_voto.py`.
**Senado y Cámara 2018 en la tabla electoral (29/09):** por partido y circunscripción,
verificados contra los archivos municipales (`DATA_INVENTORY.md` §14.5). Las 723 filas
«duplicadas» de la Cámara eran candidatos sin nombre. Permiten probar el eje
izquierda–derecha con voto por partido; no se han cruzado con la composición.
**Pre-registrado el 30/09:** `EJE_PARTIDOS_SPECIFICATION.md` — ¿el resto territorial del
voto presidencial aparece en el voto por partido? La prueba que decide es el Centro
Democrático (P2), no la Lista de la Decencia, que es la de Petro.
**Corrido el 30/09** (`EJE_PARTIDOS_RESULTS.md`): cinco de cinco predicciones, **lectura A**
—el resto territorial aparece en el voto por partido, en la Lista de la Decencia (+0,77)
y en contra en el Centro Democrático (−0,56, por poco), replicado en la Cámara—. Lo que
precisa (descriptivo, no pre-registrado): son **dos polos con geografía propia**, no un
eje simétrico. El del Centro Democrático es el de la derecha presidencial (0,81–0,86 con
Zuluaga, Duque y Gutiérrez); el de la Lista, el de la izquierda. La Alianza Verde no
sigue ninguno; el Polo y el Liberal siguen la inscripción.
**En el tablero desde el 30/09 (DI-V59):** la capa de Voto trae los dos partidos del
Senado 2018 y el aviso de residuos habla de dos polos, declarado como descriptivo.
**Pruebas del tablero arregladas (29/09)**, con dos defectos reales detrás:
`cargar_bcv` descartaba la manzana, así que con el microdato en disco la serie de la
EPC caía al DEFF prestado en todas las olas sin avisar; y `preparar_mapa` solo leía
`.csv` aunque `build_agents` escribe `.parquet` donde hay pyarrow. Las 7 suites pasan.
**Dos hallazgos que quedan abiertos:**
- ~~Las opiniones de la población sintética no se reproducen entre máquinas~~ —
  **resuelto el 29/09 (DI-M2 en `matching.py`, DI-V57).** El sorteo de empates del
  hot-deck dependía del orden en que `NearestNeighbors` devuelve a los empatados, que
  cambia con el algoritmo y la versión de scikit-learn (52–62 % de las opiniones
  cambiaban). Ahora el orden es canónico y el conjunto nunca se recorta: los cuatro
  algoritmos dan la misma población, con datos reales. Las cinco poblaciones, el piso
  territorial y el mapa se regeneraron (versión `v0.5-dim2`).
  **En el PC del CNC:** después de `git pull`, no reconstruir poblaciones con código
  anterior; con este código, las de las dos máquinas son iguales.
- ~~Error con diseño de la EPC en 2018 y 2019~~ — **resuelto el 29/09, y destapó
  algo mayor (DI-D7, `ANALISIS_DISENO_MUESTRAL.md` v1.2).** La manzana de la EPC se
  numera dentro de cada localidad: el conglomerado es localidad × manzana. El DEFF
  mediano pasa de 1,86 a **2,03**; los márgenes que lo usan se ensanchan 4,5 %;
  ninguna transición cambia de veredicto. Los dos CSV de la EPC ahora tienen script
  (`src/utils/medir_deff_epc.py`) y se versionan: las dos máquinas publican la misma
  serie. Serie y mapa regenerados. También se regeneraron y versionan las transiciones
  y la validación del proxy (§4.bis): el proxy infla el DEFF un 21 %, no un 94 %, y se
  equivoca lo mismo que el prestado; la decisión (prestado) se mantiene con esa razón. Ganó a «escenarios con preguntas reales» como
siguiente frente, porque resolvía un vacío de datos que ningún otro frente resolvía. *(Cerrado el
30/09: lo que dio es referencia territorial y evidencia para DI-B10; no acerca más el
motor a una pregunta real, que es lo que falta.)*

**Experimento 9: cerrado.** Se cerró el 29/09
(`EXPERIMENT_9_RESULTS.md`): dossiers, código con 52 pruebas sin red, enmiendas
4 y 5, sonda, brazos y evaluación. Lo que queda de él:
- Las respuestas crudas y su costo están en `data/processed/exp9/cache.json`
  (no se sube; se regenera solo con llamadas). El veredicto sí se sube.
- La clave de OpenRouter usada es de la cuenta del jefe de Daniel: el costo se
  mide desde el script (DI-E9), sin acceso a la página de actividad.

**Otros frentes, sin elegir:**

| | por qué |
|---|---|
| **Reabrir DI-B10** (donante con localidad) | La geografía electoral la respalda (resto territorial estable, dos polos). Decisión de proyecto, de Daniel o su jefe |
| **Pre-registrar los dos polos** | Sobre una elección que no se haya mirado (`EJE_PARTIDOS_RESULTS.md` §6.4) |
| **Simulación sobre la serie** | Poner una corrida del modelo junto a la serie medida en el tablero |
| **Hito 3 — bajo la localidad** | UPZ; ahora con la advertencia del paso 0b: sin donante con localidad, no hay geografía de opinión que bajar |

**Pendientes menores, conocidos:**
- `data/external/marginal_localidad_18mas_serie.csv` (capa de Crecimiento) está bloqueado por `.gitignore`: falta la excepción.
- **D28** se cita en EXPERIMENT_8 y EVALUACION_AGENTES_GENERATIVOS pero **no existe** en PROJECT_CONTEXT §39 (la última es D15; lo que cita equivale a D10). Registrar o corregir.
- Duplicados en el proyecto de Claude: `ESTADO_DEL_PROYECTO.md` y `POPULATION_SPECIFICATION.md` aparecen dos veces.
- La simulación con N finito del paso 0 da `sd_entre` 10–20 % menor que el piso por semillas del pipeline completo. No afecta el límite; sin explicar.

---

## 7. Mapa de documentos

Todos en `docs/` del repo; en el proyecto de Claude, los de trabajo están bajo `claude/`.

| Si vas a tocar… | lee |
|---|---|
| la página / el mapa | `VISUALIZATION_SPECIFICATION.md` (v0.16, DI-V1 a DI-V52) |
| la población sintética | `POPULATION_SPECIFICATION.md` (v0.5) |
| qué datos hay y dónde | `DATA_INVENTORY.md` |
| decisiones del proyecto | `PROJECT_CONTEXT.md` §39 (formato D0X) |
| escalar / geografía | `A08_PASO0_*`, `A08_PASO0B_*` |
| LLM / agentes generativos | `EVALUACION_AGENTES_GENERATIVOS.md`, `EXPERIMENT_8_*`, `EXPERIMENT_9_SPECIFICATION.md` |
| escenarios | `SCENARIO_SPECIFICATION.md` |

**Convención que sostiene todo esto:** las decisiones se registran con
identificador, fecha y justificación; los experimentos se **pre-registran** y se
reportan contra el pre-registro, y **las expectativas fallidas no se reescriben**
(PROJECT_CONTEXT §45).

---

*Actualizar este documento cuando cierre un hito o cambie el rumbo. Si queda
desactualizado deja de servir para lo que existe.*
