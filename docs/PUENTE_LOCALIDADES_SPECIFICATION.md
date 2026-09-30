# PUENTE POR LOCALIDADES — SPECIFICATION

**Con unas 250 personas por localidad en vez de 80, ¿el puente ordena las localidades mejor que la demografía?**

Proyecto: Bogotá Social Simulator
Versión: 0.1 — **pre-registro**
Fecha: 30 de septiembre de 2026
Estado: ~~sin código; ninguna correlación entre el puente y las respuestas de 2022 o 2024 calculada~~
**Corrida el 30/09** (`PUENTE_LOCALIDADES_RESULTS.md`): P1 11 de 11 (lectura A escrita), pero un
control no pre-registrado muestra que r_loc estaba inflado por ruido de muestreo compartido; con él,
6 de 11. Lectura pendiente de Daniel.
Origen: `PUENTE_RESULTS.md` (lectura B: P2 falló, 7 de 12) y `DATA_INVENTORY.md` §13.9 (juntar 2022-2024)

---

## 1. La pregunta

La primera prueba del puente encontró que ordena bien a las personas (12 de 12) pero no a
las localidades: le ganó a la demografía en 7 de 12 preguntas y hacían falta 8. Y encontró
por qué, en parte: con 80 personas por localidad, las medias por localidad de la propia
encuesta casi no se repiten (confiabilidad mediana 0,16). El blanco era sobre todo ruido.

Juntando 2022, 2023 y 2024 hay unas 250 personas por localidad y la confiabilidad sube. Esta
prueba repite **solo la parte de las localidades**, con el blanco más firme.

> **¿Las medias por localidad del puntaje del puente se parecen a las medias reales, en
> 2022-2024, más que las de la demografía?**

**Si sí, las preguntas nuevas pasan a tener mapa** (lectura A de `PUENTE_SPECIFICATION.md`).

---

## 2. Lo que ya sé antes de empezar (declarado para que se pueda descontar)

Esta prueba no es tan a ciegas como la primera, y hay que decirlo:

- **Conozco los 36 puentes** que propuso el modelo (qué preguntas eligió para cada una de las
  12) y su resultado con 2023. Por localidad, el puente le ganó a la demografía en satisfacción
  con Bogotá, orgullo, seguridad en el barrio y en la ciudad, corrupción, aire y situación del
  hogar; perdió en gestión del alcalde, transporte, ruido y oferta cultural (y salud).
- **Conozco la confiabilidad juntando años de cada pregunta escondida** (armonización, §13.9),
  que no involucra al puente. Con la muestra completa: seguridad en el barrio 0,82,
  transporte 0,76, situación del hogar 0,71, oferta cultural 0,64, orgullo 0,57, satisfacción
  0,56, seguridad en la ciudad 0,56, gestión del alcalde 0,37, aire 0,35, ruido 0,00 y
  corrupción −0,35. **En ruido y corrupción no hay geografía que acertar**, así que es casi
  seguro que ahí nadie gana: los umbrales de §5 se fijaron sabiendo esto.
- **No he calculado** ninguna correlación entre el puntaje del puente y las respuestas de
  2022 o 2024, ni la de la demografía con esos años.

---

## 3. Qué se usa

- **Las 11 preguntas escondidas** de la primera prueba que están en el catálogo, cada una con
  los años en que se puede juntar (§13.9): 8 con 2022-2024 y 3 con 2022-2023 (gestión del
  alcalde, aire, ruido). **La satisfacción con la salud (`SA4`) queda fuera:** no está en el
  catálogo (la responde el 78 %) y no se armonizó.
- **Los 36 puentes ya guardados**, sin llamar otra vez al modelo: **esta prueba no gasta nada.**
  Son los mismos que se juzgaron en la primera prueba; así lo único que cambia es el blanco.
- **Los encuestados de esos años** (~4.500), no la población sintética.

---

## 4. Cómo se mide

**El puntaje de cada persona** se calcula como en la primera prueba, con dos precisiones:

- Cada pregunta del puente se estandariza **dentro de cada año** (media 0, desviación 1,
  ponderadas). Así un cambio de nivel de un año a otro no se vuelve una diferencia entre
  localidades.
- Si una pregunta del puente no existe en el año de una persona (o no se puede juntar), cuenta
  como 0, igual que un «no sabe». Se reporta qué fracción del peso del puente está disponible
  en cada año.

| Cifra | Qué es |
|---|---|
| **r_loc** | Pearson entre las medias por localidad del puntaje y las medias reales, en 19 localidades, con los pesos de cada año reescalados a su tamaño de muestra (DI-AR2). Mediana de las tres llamadas |
| **Demografía** | La misma de la primera prueba (regresión con validación cruzada de 5 partes), sobre sexo, tramo de edad y estrato, **sin educación** (2024 no la trae) |
| ρ_ind | La correlación por persona, como en la primera prueba (se reporta, no decide) |
| Techo | La confiabilidad de las medias reales (dos mitades), de §13.9 (se reporta) |

---

## 5. Predicciones pre-registradas

| # | Predicción | Umbral |
|---|---|---|
| **P1** | **El puente ordena las localidades mejor que la demografía** | r_loc > demografía en **al menos 8 de las 11** |
| P2 | Sigue ordenando a las personas | ρ_ind > demografía en al menos 8 de las 11 *(control: si falla, algo se rompió al juntar años)* |
| P3 | Donde hay geografía, el puente la encuentra | mediana de r_loc ≥ 0,5 en las 7 preguntas con confiabilidad ≥ 0,5 (§2) |

**Por qué espero esto, con poca seguridad.** Con 2023 el puente ganó en 7 de 12 contra un
blanco ruidoso; con uno más firme debería ganar en más. Pero las 2 preguntas sin geografía
(ruido, corrupción) son casi derrotas seguras, así que P1 necesita 8 de las 9 restantes. Es
exigente, y así quedó a propósito: el umbral es el mismo de la primera prueba (dos tercios).

---

## 6. Regla de decisión

```
    P1 se cumple (y P2)
      → Las preguntas nuevas pasan a tener mapa, con la población 2022-2024,
        rotulado como suposición y con los filtros de margen de la página.

    P1 no se cumple
      → Se mantiene la lectura B: las preguntas nuevas se responden por grupos,
        sin mapa. Juntar años sigue sirviendo para el mapa de las preguntas del
        catálogo.

    P2 no se cumple
      → No se adopta ninguna lectura: hay que revisar cómo se juntaron los años.
```

P3 se reporta siempre y no decide.

---

## 7. Límites, dichos antes

- **No es a ciegas del todo** (§2): los umbrales se fijaron sabiendo qué preguntas tienen
  geografía.
- **Los puentes se eligieron mirando el catálogo de 2023**; algunas de sus preguntas no
  existen en 2022 o 2024 y cuentan como 0. Eso juega en contra del puente.
- **Juntar años promedia cambios reales** entre 2022 y 2024.
- **Una sola muestra de 11 preguntas**, todas de la misma encuesta; una pregunta realmente
  nueva puede estar más lejos del catálogo.

---

## 8. Qué se construye después

1. `src/experiments/puente_localidades.py` y sus pruebas, con encuestados inventados de tres
   años: un mundo donde la geografía de las preguntas del puente se transmite a la escondida
   (P1 se cumple) y uno donde no (no se cumple).
2. La corrida (sin gasto) y `PUENTE_LOCALIDADES_RESULTS.md`, contra este documento.
