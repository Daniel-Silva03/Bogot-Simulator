# ESTADO DEL PROYECTO — punto de partida para una conversación nueva

Proyecto: Bogotá Social Simulator
Fecha de corte: **30 de septiembre de 2026** (geografía electoral cerrada; frente nuevo: escenarios con preguntas reales)
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
**Siguiente:** conectarla a la página (motor, y el aviso de qué años responden).

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
