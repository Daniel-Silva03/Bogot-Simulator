# PUENTE POR LOCALIDADES — RESULTS

**Contra el pre-registro, el puente gana: 11 de 11, lectura A. Pero un control que añadí después de ver los datos muestra que casi toda esa ventaja es un artefacto de la medida. Quitado el artefacto, el puente no ordena las localidades mejor que la demografía. Recomiendo no adoptar A; la decisión es de Daniel.**

Proyecto: Bogotá Social Simulator
Fecha: 30 de septiembre de 2026
Pre-registro: `PUENTE_LOCALIDADES_SPECIFICATION.md` (commit 22df058). Código: `src/experiments/puente_localidades.py`,
subido antes de correr (0957ddf); el control de §4 se añadió después (DI-PL6).
Gasto: **ninguno.** Los 36 puentes salieron de la caché de la primera prueba; ninguna llamada nueva.
Resultado: `data/processed/puente_localidades/resultado.json`

---

## 1. Qué se corrió

4.522 encuestados (1.500 de 2022, 1.501 de 2023, 1.521 de 2024), 11 preguntas escondidas y los
mismos 36 puentes de la primera prueba. 35 de los 36 son válidos; el de ruido que ya había
fallado sigue contando como puente vacío (DI-PU3).

Una parte de cada puente no existe en 2022 o en 2024 y cuenta como 0 (§4). En 2023 siempre está
completo; en 2022 y 2024 (donde la escondida se usa), entre el 39 % y el 100 % del peso, con
varios cerca de la mitad.
Eso juega en contra del puente, como anticipaba §7.

## 2. Las cifras

r_loc y ρ_ind son la mediana de las tres llamadas. «Conf.» es la confiabilidad de la muestra
entera (§13.9). Las dos últimas columnas son el control de §4, **no pre-registrado**.

| Pregunta | años | n/loc | conf. | r_loc | demo | ρ_ind | demo | *mitades: puente* | *demo* |
|---|---|---|---|---|---|---|---|---|---|
| Satisfacción con Bogotá (`CV1`) | 22-24 | 251 | 0,56 | 0,44 | 0,32 | 0,42 | 0,03 | *0,18* | *0,26* |
| Orgullo (`AG2`) | 22-24 | 251 | 0,57 | 0,34 | 0,03 | 0,39 | 0,01 | *0,14* | *0,01* |
| Seguridad en el barrio (`VS8`) | 22-24 | 251 | 0,82 | 0,61 | 0,55 | 0,30 | 0,12 | *0,43* | *0,51* |
| Seguridad en la ciudad (`VS10`) | 22-24 | 251 | 0,56 | 0,63 | 0,24 | 0,37 | 0,07 | *0,32* | *0,19* |
| Corrupción (`GG7`) | 22-24 | 251 | −0,35 | 0,54 | 0,20 | 0,20 | 0,08 | *0,23* | *0,07* |
| Gestión del alcalde (`GG3`) | 22-23 | 131 | 0,37 | 0,51 | 0,35 | 0,62 | 0,10 | *0,03* | *0,22* |
| Transporte (`MV4`) | 22-24 | 251 | 0,76 | 0,67 | 0,66 | 0,29 | 0,14 | *0,44* | *0,58* |
| Aire (`MA3_1`) | 22-23 | 163 | 0,35 | 0,42 | 0,11 | 0,58 | 0,05 | *0,08* | *0,06* |
| Ruido (`MA3_3`) | 22-23 | 163 | 0,00 | 0,77 | 0,26 | 0,57 | 0,04 | *0,20* | *0,16* |
| Oferta cultural (`CR2`) | 22-24 | 251 | 0,64 | 0,782 | 0,780 | 0,50 | 0,08 | *0,47* | *0,68* |
| Situación del hogar (`CO2`) | 22-24 | 251 | 0,71 | 0,77 | 0,67 | 0,43 | 0,27 | *0,55* | *0,52* |

## 3. Contra el pre-registro

| # | Predicción | Umbral | Resultado | |
|---|---|---|---|---|
| **P1** | El puente ordena las localidades | r_loc > demografía en ≥ 8 de 11 | **11 de 11** | se cumple |
| P2 | Sigue ordenando a las personas (control) | ρ_ind > demografía en ≥ 8 de 11 | 11 de 11 | se cumple |
| P3 | Donde hay geografía, la encuentra | mediana de r_loc ≥ 0,5 en las 7 con conf. ≥ 0,5 | 0,63 | se cumple (se reporta) |

**Regla de decisión escrita (§6): lectura A**, las preguntas nuevas pasan a tener mapa.

Dos victorias son por nada: transporte (0,669 contra 0,665) y oferta cultural (0,782 contra
0,780).

## 4. Por qué no me fío: el control de mitades (NO PRE-REGISTRADO)

**Lo que vi.** El ruido (`MA3_3`) no tiene geografía que acertar: su confiabilidad por
localidad es 0,00. Aun así, el puente dio r_loc = 0,77. La corrupción, con confiabilidad
negativa, dio 0,54. Ningún puntaje puede parecerse a una geografía que no existe.

**La explicación.** El puntaje del puente y la respuesta real se calculan sobre **las mismas
personas**. Con ~250 por localidad, la media de cada localidad tiene ruido de muestreo: por
azar, a una localidad le tocaron personas algo más molestas con el ruido. Si el puente acierta
por persona (ρ_ind 0,57 en ruido), esas mismas personas también tienen un puntaje más alto. El
ruido de muestreo sale igual en los dos lados y las medias se correlacionan solas. **Es
acierto por persona disfrazado de acierto por localidad.** La demografía casi no lo sufre,
porque acierta poco por persona (ρ_ind 0,01 a 0,27).

**El control.** Se parte a los encuestados en dos mitades al azar. El puntaje se promedia por
localidad en una mitad y la respuesta real en la otra, y se repite 200 veces. Así el ruido de
muestreo ya no es compartido y solo queda lo que se repite: la geografía. Se hace igual para la
demografía, así que ambos pierden por igual la mitad de la muestra. En `tests/` hay un mundo
inventado sin geografía donde el r_loc de siempre pasa de 0,5 y el de mitades se queda cerca
de 0.

**Qué da:**

| | puente | demografía |
|---|---|---|
| Cuánto baja r_loc al quitar el ruido compartido (mediana) | **0,30** | 0,08 |
| Gana el puente, con mitades | **6 de 11** (umbral de P1: 8) | |
| Gana el puente en las 7 con geografía | **3 de 7** | |
| Mediana de r_loc con mitades, en las 7 con geografía | 0,43 | **0,51** |

De las 6 victorias, dos son en preguntas sin geografía (ruido y corrupción) y una es
0,08 contra 0,06. **Sin el artefacto, el puente no ordena las localidades mejor que la
demografía.** Donde la geografía es más firme (seguridad en el barrio, transporte, oferta
cultural), pierde claramente. Esas son justo las preguntas donde la geografía la explican el
estrato y la ubicación, que la demografía ve directamente.

**Esto también toca la primera prueba.** `PUENTE_RESULTS.md` usó el mismo r_loc, así que sus 7 de 12
tienen el mismo sesgo a favor del puente (no lo recalculé). La lectura B no cambia (ahí ya fallaba), pero la anoto
allá.

## 5. Qué recomiendo, y qué no decido yo

La regla escrita dice A. El control, que no estaba pre-registrado, dice que la A descansa en
un artefacto que el pre-registro no previó. Lo que el protocolo del proyecto permite es
reportar las dos cosas; cambiar la lectura es una decisión de proyecto.

**Recomiendo mantener la lectura B:** las preguntas nuevas se responden por grupos, sin mapa.
Si se adoptara A, la página dibujaría un mapa que, por lo que muestra el control, no dice más
que un mapa de estrato y edad. Rotularlo como suposición no lo arregla.

Lo que sí queda en pie:
- **El puente ordena bien a las personas** (P2, 11 de 11, ρ_ind mediana 0,42 contra 0,08).
  Las diferencias entre grupos que la página muestra para preguntas nuevas siguen respaldadas.
- **Juntar 2022-2024 sirve para el mapa de las preguntas del catálogo.** Ese mapa es la
  respuesta real, sin puente, así que no le afecta este artefacto.
- **Una salida posible para dar mapa a las preguntas nuevas, sin prometerla:** un mapa por
  localidad que diga explícitamente «esto es lo que se esperaría solo por la composición de
  cada localidad (estrato, edad, sexo)». No es la opinión supuesta, es demografía, y hay que
  decirlo así. Necesitaría su propio pre-registro.

## 6. Límites

- El control de §4 se diseñó **después** de ver la primera corrida. Lo motivó una cifra
  imposible (r_loc 0,77 sin geografía), no el deseo de que el resultado saliera de una forma;
  aun así, cuenta como análisis no pre-registrado.
- Con mitades cada lado tiene ~125 personas por localidad: los r_loc bajan para los dos, y
  la comparación entre puente y demografía es lo que importa, no su nivel.
- Todo lo de `PUENTE_LOCALIDADES_SPECIFICATION.md` §7 sigue valiendo.
