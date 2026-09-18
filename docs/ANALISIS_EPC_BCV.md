# La EPC de Bogotá Cómo Vamos — qué contiene, qué no, y una inversión de códigos que hay que reportar

Proyecto: Bogotá Social Simulator
Versión: 1.0
Fecha: 17 de septiembre de 2026
Fuente: entrega de Bogotá Cómo Vamos del 17/09/2026 (correo del analista técnico), `data/raw/bogota_como_vamos/empaquetado_2026-09/`
Contenido: 10 olas de microdatos (2014-2019, 2022-2025), formularios, tablas de salida y el diccionario "EPC Suprema"

---

## 0. Las cuatro cosas que salieron

1. **La batería de *confianza* institucional NO es anual.** Existe solo en 2024 y 2025, y con escalas distintas entre sí. La indicación del correo —"son preguntas anuales, todos los años las va a encontrar"— no se sostiene contra el diccionario ni contra los datos.
2. **Pero hay algo mejor de lo que esperaba:** dos ítems de evaluación institucional en escala 1-5 con **nueve olas cada uno**, verificados.
3. **Los factores de expansión existen y son reales en los diez años.** El `FACTOR1 ≡ 1,0` del empaquetado web de 2025 era un defecto de ese empaquetado, no de la encuesta: el archivo nuevo trae pesos que van de 3,2 a 54.612 y suman 6.328.419.
4. **Los ítems de imagen favorable/desfavorable tienen los códigos 1 y 2 invertidos entre 2014-2023 y 2024**, contra lo que dicen el formulario y el diccionario. Apilar esos años sin verificar produce un salto artificial de ~45 puntos en 2024.

---

## 1. Qué hay, año por año

| | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|
| n | 1.502 | 1.712 | 1.502 | 1.506 | 1.500 | 1.521 | 1.500 | 1.501 | 1.521 | 1.520 |
| variables | 1.025 | 833 | 238 | 224 | 411 | 296 | 441 | 479 | 771 | 177 |
| factor | `PON` | `FEXP` | `PON` | `PON` | `PON` | `PONDERA` | `PONDERA` | `FEXP` | `PONDERADOR` | `Factor1` |
| suma del factor | n | n | n | n | n | n | 6,15 M | 6,21 M | 6,29 M | 6,33 M |

No hay 2020 ni 2021. 2014-2019 traen el factor normalizado a la muestra y 2022-2025 expandido a población; para medias ponderadas da lo mismo.

**Un aviso sobre 2022:** su `PONDERA` toma solo **10 valores distintos** (los demás años van de 60 a 527). Es una posestratificación muy gruesa. Cualquier estimación de 2022 merece más desconfianza que la de sus vecinos.

## 2. La batería de confianza no es una serie

`MICC5`-`MICC8` (confianza en Alcaldía, Concejo, Gobierno Nacional y Congreso) aparecen **solo en 2024 y 2025**, y ni siquiera entre sí son comparables sin trabajo:

| | 2024 (`IC3_1`…`IC3_4`) | 2025 (`CON_4`…`CON_7`) |
|---|---|---|
| categorías | 1-4, sin código de no respuesta | 1-5, más `90` = no sabe/no responde |

La hoja `VALORES` del diccionario las describe con tres niveles (Desconfío / Ni / Confío): esa es la recodificación del tablero, **no** la escala del microdato. El microdato de 2025 está en 1-5, que es lo que ya habíamos medido contra la ECP.

**Conclusión:** la validación cruzada de 0,09 puntos contra la ECP sigue en pie para 2025, pero sigue siendo **una sola ola**. La confianza institucional no gana puntos de serie con esta entrega.

## 3. Lo que sí es una serie: dos ítems de gestión en escala 1-5

La pregunta es explícita en el formulario —*"en una escala de 1 a 5, siendo 1 muy mala gestión y 5 muy buena gestión"*— así que la dirección no depende del diccionario. Verificada contra las tablas de salida publicadas de 2023 (CC5: 42,9 % en 1-2 en el microdato contra 44,1 % publicado).

### GG3 — gestión del alcalde o alcaldesa · 9 olas

| Año | 2014 | 2015 | 2017 | 2018 | 2019 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|
| media | 2,845 | 2,408 | 2,105 | 2,367 | 2,544 | 2,952 | 2,859 | **3,180** | 2,753 |
| sd | 1,273 | 1,179 | 1,108 | 1,156 | 1,129 | 1,212 | 1,148 | 1,126 | 1,119 |
| % válida | 93,0 | 95,4 | 96,3 | 97,1 | 93,8 | 85,0 | 84,2 | 82,8 | 81,8 |

Trayectoria no monótona, con tres puntos de giro, y legible contra los periodos de alcaldía. La dispersión se mueve arriba y abajo sin patrón monótono: el mismo tipo de fenómeno que la joroba de la ECP.

### CC5 — gestión del Concejo · 9 olas

| Año | 2014 | 2015 | 2016 | 2017 | 2019 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|
| media | 2,635 | 2,613 | 2,531 | 2,234 | 2,670 | 2,595 | 2,534 | 2,645 | 2,564 |
| sd | 1,033 | 0,895 | 1,009 | 1,018 | 0,991 | 1,058 | 0,965 | 1,056 | 1,005 |
| % válida | 77,6 | 77,8 | 65,7 | 86,5 | 89,2 | 74,8 | 86,0 | 88,4 | 77,3 |

Prácticamente plana: 0,44 puntos de rango en once años, contra 1,08 de GG3. **Sirve como control**: una institución cuya evaluación casi no se mueve, medida con el mismo instrumento, en la misma muestra, en los mismos años.

**Advertencia pendiente.** La tasa de respuesta válida cae de ~95 % en 2014-2019 a ~82 % en 2022-2025. Es la misma amenaza que se analizó y se descartó para la ECP 2023 (`claude/ANALISIS_NORESPUESTA_2023.md`), y hay que repetir ese análisis aquí antes de usar la serie: 13 puntos de caída es más de lo que se movió allá.

## 4. La inversión de códigos de 2024

`GP1_*` (imagen de entidades) y `GG1` (imagen del alcalde) son items de dos categorías. El formulario de 2023 y el de 2024 dicen **lo mismo**: *"una imagen desfavorable (1) o favorable (2)"*. El diccionario dice lo mismo. Los datos dicen otra cosa.

**CADEs / SuperCADEs, código 1:** 72 % · 72 % · 73 % · 71 % · 74 % · 74 % · 65 % · 62 % · **23 %** (2014 → 2024).

Tres verificaciones independientes, todas concordantes:

1. **La tabla de salida publicada por BCV para 2023** dice: Desfavorable 20,1 %, Favorable 64,8 %, No conoce 15,1 %. El microdato de 2023 tiene 62 % en el código 1 y 21 % en el código 2. Es decir: en 2023, **código 1 = Favorable**, al revés del formulario.
2. **Lo mismo con `GG1` en 2023:** la tabla publica Desfavorable 44,4 % / Favorable 39,6 %; el microdato tiene 39 % en el código 1 y 45 % en el código 2.
3. **Señal independiente:** la correlación entre `GP1_1` y `GG3` es −0,107 · −0,167 · −0,163 en 2019, 2022 y 2023, y **+0,194** en 2024. El signo se da vuelta y la magnitud se conserva.

**Conclusión:** en 2014-2023 los ítems de imagen están codificados 1 = Favorable, 2 = Desfavorable, al revés de su propio formulario y de la EPC Suprema; en 2024 siguen el formulario. Verificado directamente para 2023 contra la tabla publicada, e inferido por el signo de la correlación para 2019 y 2022.

**Es la segunda vez que el diccionario de una fuente miente sobre sus propios códigos** (la primera fue la ECP 2015, `claude/DATA_INVENTORY.md` §10). La regla queda: *ningún diccionario se acepta sin contrastarlo contra una cifra publicada o contra la estructura de los datos.*

Esto merece reportarse a Bogotá Cómo Vamos: cualquiera que use el superdiccionario tal como está para armar la serie de imagen institucional va a publicar un salto de 45 puntos que no ocurrió.

## 5. Qué habilita y qué no

**Habilita.** Nueve olas anuales de una evaluación institucional en escala 1-5, con factor de expansión, más un ítem de control casi plano medido en paralelo. Contra las cuatro transiciones de la ECP, son **ocho transiciones y un contraste dentro de la misma encuesta**. Los Experimentos 3, 4, 5 y 6 se pueden volver a correr con eso, y el veredicto "no hay mecanismo social identificable" —que hoy descansa en cuatro transiciones— pasa a ser comprobable en serio.

**No habilita.** La serie es de *gestión*, no de *confianza*: es otro constructo, aunque sobre la misma escala y sobre instituciones que se solapan. La población sintética sigue construyéndose con la ECP, y este material entra como objetivo dinámico, no como donante. El salto 2019 → 2022 cubre tres años con una sola observación en cada extremo, y la pandemia queda adentro sin medición.

## 6. El control no es un control: hay un componente común

Se agregó después de construir las series, y por eso va etiquetado.

`GG3` (alcalde) y `CC5` (Concejo) **se mueven juntos**: r = +0,66 en niveles y **+0,62 en cambios** sobre los ocho años comunes. Un ítem que iba a servir de contraste resulta estar correlacionado con el que se quiere explicar.

Y hay un tramo donde la coincidencia es demasiado exacta:

| Cambio | alcalde | Concejo |
|---|---|---|
| →2015 | −0,437 | −0,022 |
| →2017 | −0,304 | −0,379 |
| **→2019** | **+0,439** | **+0,436** |
| →2022 | +0,408 | −0,075 |
| →2023 | −0,093 | −0,062 |
| →2024 | +0,321 | +0,111 |
| →2025 | −0,428 | −0,081 |

Dos instituciones distintas subiendo **+0,44 exactamente la misma cantidad** no es la firma de dos cambios de opinión independientes; es la firma de un componente común de periodo o de campo. Y la ECP del DANE, una encuesta independiente, se movió **al revés** en ese mismo tramo:

| 2017→2019 | ECP-DANE (confianza) | EPC alcalde | EPC Concejo |
|---|---|---|---|
| | **−0,141** | +0,439 | +0,436 |

No puedo decir si el componente común es real (un clima de opinión que sube para todo lo público a la vez) o instrumental (un cambio de campo en 2019). Con dos ítems no se identifica un modelo de factores. Lo que sí se puede hacer sin supuestos es **restar**: cualquier componente aditivo común desaparece en la diferencia.

| Año | 2014 | 2015 | 2017 | 2019 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| alcalde − Concejo | +0,210 | −0,205 | −0,129 | −0,126 | +0,357 | +0,325 | +0,535 | +0,189 |

El salto conjunto de 2017→2019 se evapora (−0,129 → −0,126, plano), y lo que queda es una serie de amplitud mucho menor —0,74 de rango contra 1,08— dominada por el contraste entre los periodos de alcaldía.

**Qué implica para los experimentos.** Hay dos objetivos posibles y no son el mismo fenómeno:

- **La serie cruda de `GG3`.** Amplitud grande, ocho transiciones, pero con un componente común que puede ser artefacto.
- **La diferencia `GG3 − CC5`.** Limpia de cualquier efecto aditivo común de periodo o de casa, a costa de amplitud y de interpretabilidad directa.

Correr los Experimentos 3 a 6 contra la cruda y declarar victoria o derrota sin mirar la diferencia sería repetir el error del Experimento 4: ajustar un fenómeno y llamarlo *el* fenómeno. **La recomendación es correrlos contra las dos y reportar ambos**, con el pre-registro escrito antes de ver cuál de las dos favorece qué modelo.

---

*Todas las cifras son agregados ponderados calculados sobre los microdatos entregados por BCV. Ningún registro individual sale de este análisis.*
