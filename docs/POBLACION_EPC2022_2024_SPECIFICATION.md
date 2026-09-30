# POBLACIÓN EPC 2022-2024 — SPECIFICATION

**La misma población de `POBLACION_EPC2023_SPECIFICATION.md`, pero con las encuestas de 2022, 2023 y 2024 juntas: unas 250 personas por localidad en vez de 80.**

Proyecto: Bogotá Social Simulator
Versión: 0.2 — construida y verificada el 30/09 (`src/population/poblacion_epc_olas.py`, §7)
Fecha: 30 de septiembre de 2026
Origen: opción 1 para el mapa (`PUENTE_RESULTS.md` §7) y la armonización de `DATA_INVENTORY.md` §13.9
Lo que no cambia: todo lo que no se diga aquí es igual a la población 2023

---

## 1. Qué cambia

| | Población EPC 2023 | Población EPC 2022-2024 |
|---|---|---|
| Donantes | 1.501 encuestados de 2023 | **~4.500**: los de 2022, 2023 y 2024 |
| Personas por localidad | ~80 | **~250** (19 localidades; Sumapaz sigue sin donantes) |
| Variables para emparejar | localidad, sexo, edad, estrato, educación | **localidad, sexo, edad, estrato** (sin educación, §2) |
| Qué describe | Bogotá en 2023 | **Bogotá 2022-2024**, promediada |
| Preguntas | 102 del catálogo 2023 | las mismas 102, cada una con los años en que se puede juntar (§3) |

La población 2023 no se borra: queda como la versión de un solo año.

---

## 2. Emparejamiento sin educación

**Hecho:** la EPC 2024 no pregunta la educación de quien responde. La única variable de
educación de ese año (`ED13`) es la de los hijos en edad escolar. 2022 sí la trae (`CS4`).

**Decisión:** para todos los donantes, el emparejamiento usa localidad (bloque exacto, nunca
se suelta), sexo (exacto) y tramo de edad y estrato (distancia). Usar la educación solo en
los donantes que la tienen haría que los de 2024 se emparejaran peor que los demás, y que la
mezcla de años cambiara según la educación del agente.

**Costo, dicho antes:** la población 2023 usaba la educación y se parecía más a cada
encuestado (64 % de los agentes idénticos a su donante en las cuatro variables). Esta se
parecerá en tres. La verificación de §5 dice si eso se nota en las respuestas.

**Donantes y pesos:** cada año con su factor de expansión (`PONDERA`, `FEXP`, `PONDERADOR`),
reescalado para que cada ola sume su tamaño de muestra (DI-AR2). El conglomerado es
año × localidad × manzana.

> *Corrección (30/09, al construirla).* **Pesos:** reescalar por ola no bastó. El `PONDERA`
> de 2022 no corrige el sobremuestreo de las localidades pequeñas, y el 74 % de los agentes
> de La Candelaria heredaba a alguien de 2022. Se reescala por **ola × localidad**
> (DI-PO5). **Conglomerado:** 2022 no trae manzana; ese año cada persona es su propio
> conglomerado (DI-PO3), lo que subestima un poco su margen.

---

## 3. Las preguntas y sus años

Cada pregunta del catálogo se responde con los donantes de los años en que se puede juntar
(`data/processed/epc_armonizado/items.csv`, DI-AR1 y DI-AR5):

- ~~48 preguntas con tres años y 26 con dos~~ **45 preguntas con tres años y 29 con dos** *(corregido el
  30/09: la cifra venía mal copiada de §13.9)*: tienen ~250 (o ~160) personas por localidad.
- **28 solo con 2023:** para esas, solo responden los agentes cuyo donante es de 2023, y el
  mapa tiene los márgenes de siempre.
- **Evaluaciones del gobierno de turno** (gestión del alcalde, del Concejo, inversión de
  recursos públicos): solo 2022 y 2023, la misma administración.
- **2025 no entra** (sin etiquetas que verificar, §13.9).

Un agente cuyo donante no respondió una pregunta queda «sin dato» en esa pregunta; no se le
inventa respuesta.

---

## 4. Lo que la página tiene que decir distinto

- «Opina como Bogotá **entre 2022 y 2024**», no «en 2023».
- En cada respuesta del catálogo, **de qué años sale** y cuántas personas por localidad hay.

---

## 5. Verificación (antes de usarla)

La misma de §6 de la población 2023, con estos cambios:

1. **Demografía:** igual, por localidad, sin educación.
2. **Opinión:** para cada pregunta y localidad, la media de los agentes cae dentro del margen
   de la media ponderada de los donantes de sus años. Umbral: no más del 10 % de pares fuera
   del margen del 95 %.
3. **Emparejamiento:** porcentaje de agentes idénticos a su donante en las tres variables, por
   localidad y por año del donante.
4. **Mezcla de años por localidad:** qué fracción de los donantes de cada localidad es de
   cada año. Si una localidad queda dominada por un solo año, se dice.
5. **Reproducibilidad:** misma semilla, misma población.

---

## 6. Qué se construye después

1. Extender `src/population/poblacion_epc.py` para varias olas (sin tocar la de 2023).
2. La verificación de §5, anotada aquí.
3. La prueba de localidades del puente se corre **sobre los encuestados**, no sobre esta
   población (`PUENTE_LOCALIDADES_SPECIFICATION.md`), así que no depende de este paso.

---

## 7. Resultado de la verificación (30/09)

`data/processed/poblacion_epc2022_2024/verificacion.json`. 20.000 agentes (1.000 por localidad;
Sumapaz sin donante), 4.522 donantes (1.500 de 2022, 1.501 de 2023, 1.521 de 2024).

| §5 | Resultado | Población 2023, para comparar |
|---|---|---|
| 1. Demografía, peor diferencia por localidad | sexo 2,9 pts, edad 3,5, estrato 2,1 | iguales (mismo receptor) |
| 2. Opinión fuera del margen del 95 % | **23 de 1.938 pares (1,2 %)**, umbral 10 %: **pasa** | 3,5 % |
| 3. Emparejamiento exacto (sexo, edad, estrato) | **98,2 %**; 97,8 / 98,2 / 98,7 % según el año | 64 % (con educación, cuatro variables) |
| 4. Mayor fracción de un solo año en una localidad | **39 %** (antes de DI-PO5: 74 %) | — |
| 5. Reproducible con la misma semilla | sí | sí |

Donantes por localidad: de 86 (La Candelaria) a 456 (Suba); mediana 251.

**Lectura.** Sin la educación, el emparejamiento es casi siempre exacto, porque quedan menos
variables que igualar. Lo que se pierde es que dentro de un mismo sexo, edad y estrato ya no
se distingue la educación; la verificación de opinión no muestra que eso se note en las
medias por localidad. La «mayor diferencia de media en la ciudad» (0,07) compara agentes con
donantes cuyos pesos ya no reproducen el tamaño de cada localidad (DI-PO5); no dice nada de
la población.

~~**Falta:** conectarla a la página (el motor y el aviso «Bogotá 2022-2024» con los años de cada
respuesta, §4).~~ Conectada el 30/09 (`PAGINA_CONSULTA.md` §5.5).
