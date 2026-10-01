# PUENTE SIN BASE — SPECIFICATION

**Cuando una pregunta nueva no se parece a nada de lo que la encuesta midió, ¿el simulador puede reconocerlo y decirlo, en vez de forzar una respuesta?**

Proyecto: Bogotá Social Simulator
Versión: 0.1 — **pre-registro**
Fecha: 1 de octubre de 2026
Estado: ~~con código; ninguna llamada real hecha con el prompt nuevo~~ **corrida el 1/10**
(`PUENTE_SIN_BASE_RESULTS.md`): P1 no se cumple (5 de 10); P2, R1, R2 y P3 sí. No se usa sin_base;
la página muestra la fuerza.
Origen: pregunta de Daniel del 1/10 («¿y si una pregunta nueva no está medida en ningún lado?») y
`PUENTE_SPECIFICATION.md` §7 / `PUENTE_LOCALIDADES_SPECIFICATION.md` §7 («una pregunta realmente nueva
puede estar más lejos del catálogo»)

---

## 1. El problema

Hoy el puente **siempre** apoya una pregunta nueva en 1 a 5 preguntas del catálogo. El prompt no deja
decir «no hay nada relacionado»: una respuesta vacía se trata como error (DI-PU3). Ante una pregunta
sin parientes en la encuesta, el modelo se agarra de lo más cercano y la página muestra diferencias
entre grupos que suenan razonables, sobre una relación floja. Lo único que la protege es que muestra
en qué se apoyó.

La validación del puente (12 preguntas escondidas) no tocó este caso: todas tenían parientes claros
en el catálogo.

## 2. Qué se cambia: el prompt del puente, versión 2

Dos cosas nuevas en la respuesta del modelo: **`sin_base`** (no hay con qué) y **`fuerza`** (qué
tan buena es la base). El texto exacto, que se usará tal cual:

```
Eres un asistente de métodos de encuesta. Te doy una PREGUNTA NUEVA y un CATÁLOGO de preguntas
que ya se hicieron a las mismas personas en Bogotá (Encuesta de Percepción Ciudadana 2023).
Tu tarea es construir un PUENTE: elegir de 1 a 5 preguntas del catálogo cuyas respuestas
permitan ordenar a las personas según cómo responderían la pregunta nueva, y proponer la
media esperada de la pregunta nueva en Bogotá.
Para cada pregunta elegida da: su código; el sentido, '+' si los códigos más altos de esa
pregunta van con códigos más altos de la pregunta nueva, '-' si van con códigos más bajos;
y un peso de 1 a 3 según qué tan relacionada está.
Califica la FUERZA del puente: "fuerte" si el catálogo mide el mismo objeto o servicio que la
pregunta nueva; "media" si mide algo muy cercano; "debil" si solo comparte el tema general
(por ejemplo, la evaluación del gobierno en un sector frente a una medida concreta de ese sector).
Si ninguna pregunta del catálogo permite razonablemente ordenar a las personas para la pregunta
nueva, porque depende de gustos, valores o temas que el catálogo no mide, NO fuerces un puente:
responde con "preguntas": [] y "sin_base": true, y explica por qué en la justificación.
Responde SOLO con un JSON, sin texto alrededor, con esta forma:
{"preguntas": [{"codigo": "XX", "sentido": "+", "peso": 2}], "fuerza": "media", "sin_base": false,
"nivel": 3.1, "justificacion": "una o dos frases"}
El nivel es la media esperada en la escala de códigos de la pregunta nueva; si sin_base es true,
usa null.
```

Es el prompt actual (`puente.SISTEMA`) con el párrafo de la fuerza y el de `sin_base` añadidos, y el
formato extendido. **Válida** con `sin_base: true` es: lista vacía, nivel nulo o ausente. Con
`sin_base: false`: lo de siempre (DI-PU3) más una `fuerza` en {fuerte, media, debil}. Todo lo demás
cuenta como respuesta rota, como hoy.

## 3. Las preguntas de prueba

**30 preguntas nuevas, escritas antes de correr nada**, todas con la misma escala de acuerdo de 5
puntos (Totalmente en desacuerdo, En desacuerdo, Ni de acuerdo ni en desacuerdo, De acuerdo,
Totalmente de acuerdo). Diez de cada clase. La clase la asigné yo con esta regla, y **Daniel la revisa
antes de la corrida** (§8):

- **A, pariente directo:** el catálogo mide el mismo objeto, lugar o servicio.
- **B, solo el tema general:** el catálogo toca el sector (sobre todo con la evaluación del gobierno
  por sector, `GP1N_*`) pero no el objeto concreto.
- **C, sin pariente:** depende de gustos o valores que la encuesta no mide; ninguna pregunta del
  catálogo ordenaría a las personas con un argumento que un analista defendería.

Todas empiezan por «¿Qué tan de acuerdo está con que…».

| # | Clase | …la pregunta | Pariente en el catálogo |
|---|---|---|---|
| A1 | A | se construyan más ciclorrutas en Bogotá? | `MV13_10` bicicarriles |
| A2 | A | se instalen más luminarias en calles y parques? | `EP1B_8` luminarias |
| A3 | A | se aumente el número de policías que patrullan los barrios? | `VS8` seguridad en el barrio |
| A4 | A | se siembren más árboles en las calles de la ciudad? | `MA3_4` cantidad de árboles |
| A5 | A | se instalen más baños públicos en la ciudad? | `EP1B_4` baños públicos |
| A6 | A | se pongan más canecas de basura en el espacio público? | `EP1B_5` canecas |
| A7 | A | se aumente la frecuencia de recolección de basuras en los barrios? | `SP4` aseo y basura |
| A8 | A | se controle con más rigor el ruido de bares y vecinos? | `MA3_3` ruido, `RC5_16` |
| A9 | A | se cambien los buses por eléctricos para mejorar la calidad del aire? | `MA3_1` aire |
| A10 | A | haya más agentes de tránsito en las vías principales? | `MV13_3` agentes de tránsito |
| B1 | B | todos los colegios públicos tengan jornada única? | solo `GP1N_3` educación |
| B2 | B | se prohíba la venta y el uso de pólvora en diciembre? | solo convivencia en general |
| B3 | B | cada localidad tenga un hospital público abierto las 24 horas? | solo `GP1N_4` salud |
| B4 | B | el Distrito subsidie el arriendo de los jóvenes? | solo `GP1N_9` vivienda |
| B5 | B | el Distrito dé una renta básica a los hogares pobres? | `GP1N_1` pobreza, `CO4` |
| B6 | B | se formalice a los vendedores ambulantes con puestos fijos? | solo `GP1N_12` espacio público |
| B7 | B | el Distrito cree empleos temporales para jóvenes? | `CO1_1` empleo, `GP1N_7` |
| B8 | B | se cobre un impuesto a las viviendas desocupadas? | solo vivienda en general |
| B9 | B | se cree un sistema público de cuidado para personas mayores? | solo `RC4_1` respeto por mayores |
| B10 | B | haya un día sin carro particular cada semana en toda la ciudad? | solo movilidad en general (`MV4`, `MV2`) |
| C1 | C | vuelvan las corridas de toros a la Plaza de La Santamaría? | — |
| C2 | C | se cambie el himno de Bogotá? | — |
| C3 | C | Bogotá tenga un día festivo propio por su cumpleaños? | — |
| C4 | C | se permita tener gallinas en las casas de la ciudad? | — |
| C5 | C | suene reguetón en los eventos oficiales del Distrito? | — |
| C6 | C | la ciudad vuelva a llamarse oficialmente «Santa Fe de Bogotá»? | — |
| C7 | C | se permita entrar con perros a los restaurantes? | — |
| C8 | C | Bogotá adelante su hora oficial para aprovechar más la luz del día? | — |
| C9 | C | se construya un monumento a los deportistas olímpicos colombianos? | — |
| C10 | C | la ciudad adopte un animal símbolo oficial, como el oso de anteojos? | — |

## 4. Qué se corre

- **Las 30 preguntas** con el prompt v2 y el catálogo completo de la página (102), modelo
  `xiaomi/mimo-v2.6-pro`, temperatura 0, **3 llamadas por pregunta**, como el puente original. El
  veredicto de una pregunta es el de la mayoría de sus 3 llamadas (2 de 3); una llamada rota cuenta
  como «no sin_base, fuerza débil».
- **Regresión:** las 12 preguntas escondidas de `PUENTE_SPECIFICATION.md` con el prompt v2 y el
  catálogo de 91 (enmienda 1), 3 llamadas cada una, medidas igual que entonces sobre los encuestados
  de 2023 (`puente.analizar`). Sirve para comprobar que el cambio no estropea lo que ya funcionaba.
- **Gasto:** 90 + 36 = **126 llamadas**, unos USD 0,25 a 0,50 (entre 7.300 y 8.000 tokens cada una).
  Se pide permiso antes.

## 5. Predicciones pre-registradas

| # | Predicción | Umbral |
|---|---|---|
| **P1** | Reconoce cuando no hay base | `sin_base` en **≥ 7 de las 10** de clase C |
| **P2** | No la niega cuando sí hay | `sin_base` en **≤ 1 de las 10** de clase A |
| **R1** | El cambio no rompe lo validado: no dice «sin base» donde la había | `sin_base` en **≤ 1 de las 12** escondidas |
| **R2** | Sigue ordenando a las personas | ρ_ind > p95 del azar y > demografía en **≥ 9 de 12** (el P1 de `PUENTE_SPECIFICATION.md`) |
| P3 | La fuerza distingue A de B | fuerza «fuerte» o «media» en ≥ 8 de las 10 A; «debil» o `sin_base` en ≥ 6 de las 10 B |
| P4 | Las B no se descartan en bloque | se reporta cuántas B salen `sin_base` (no decide) |

**Por qué espero esto, con poca seguridad.** Los modelos tienden a complacer: con un catálogo de 102
preguntas, puede que siempre encuentre algo y casi nunca diga `sin_base` (P1 falla). También puede
pasar lo contrario, que el párrafo nuevo lo vuelva demasiado prudente y empiece a negar puentes que
sí funcionaban (R1 falla). La clase B no tiene respuesta correcta: ahí solo se mira qué hace.

## 6. Regla de decisión

```
    R1 o R2 no se cumple
      → No se adopta el prompt v2: rompe lo validado. La página sigue igual, y añade un aviso
        general: «si la pregunta no se parece a nada de lo que la encuesta midió, la suposición
        es más floja».

    R1 y R2 se cumplen, y P1 y P2 también
      → Se adopta el prompt v2. Si el modelo dice sin_base, la página no responde: dice «No hay
        en la encuesta con qué suponer esta pregunta» y su razón.

    R1 y R2 se cumplen, pero P1 o P2 no
      → No se usa sin_base en la página (no es confiable).

    En los dos últimos casos, si P3 se cumple
      → La página muestra la fuerza («base fuerte / media / débil»). Si no, no la muestra.
```

## 7. Límites, dichos antes

- **Las clases las puse yo.** La prueba mide si el modelo coincide con ese criterio, no con una
  verdad. Por eso Daniel las revisa antes (§8), y lo que él cambie queda anotado aquí con fecha.
- **No mide si la suposición acierta.** Para una pregunta de verdad nueva no hay dato real con qué
  compararla. Solo mide si el simulador reconoce cuándo no tiene con qué.
- **Algunas C se pueden discutir.** Por ejemplo, el orgullo por Bogotá (`AG2`) podría tener algo que
  ver con el himno o con el nombre de la ciudad. Si el modelo propone un puente así con fuerza
  «debil», no es un error grave; por eso P1 pide 7 de 10 y no 10 de 10.
- **El prompt v2 sigue diciendo «EPC 2023»,** como el que se validó, para no cambiar dos cosas a la
  vez.
- **Una sola formulación por pregunta** y una sola escala.

## 8. Qué se hace después

1. **Daniel revisa las 30 preguntas y sus clases.** Los cambios se anotan aquí antes de seguir. *Hecho el 1/10: «las clases están bien», sin cambios.*
2. Código: `src/experiments/puente_sin_base.py` y sus pruebas, con un modelo simulado (sin gasto).
3. Con permiso, la corrida (126 llamadas) y `PUENTE_SIN_BASE_RESULTS.md`, contra este documento.
