# MIROFISH ANTE LA SEGUNDA VUELTA DE 2026 EN BOGOTÁ — resultados

Corrido el **9 de octubre de 2026** contra `MIROFISH_SEGUNDA_VUELTA_SPECIFICATION.md` (pre-registro y código en `1d0067c`,
antes de correr). **Gasto: USD 0,0585**, dentro del tope de USD 1. Incluye dos informes, por el error de DI-MF4.

## 1. Qué hizo MiroFish

- **Agentes:** 16, sacados de las entidades del documento: movimientos políticos, medios, la autoridad electoral y los
  candidatos. **No son votantes de Bogotá.**
- **Simulación:** 10 rondas (MiroFish proponía 168), con 33 acciones en Twitter y 35 en Reddit.
- **El informe** está en chino, el idioma de MiroFish, y tiene tres secciones. Queda en
  `data/processed/mirofish/segunda_vuelta/informe.md`, sin subir. Es el informe `report_d8133f7341eb` (DI-MF4).

**Su cifra, textual:** «波哥大决选两位候选人的单点预测为：Iván Cepeda获得53%，Abelardo de la Espriella获得47%。比例以两位候选人的有效票合计为分母。»
Es decir: Cepeda 53 % y De la Espriella 47 %, sobre los votos por los dos.

**De dónde sale, según el propio informe:**
- «la entrevista no obtuvo ninguna respuesta válida de los agentes», y no hay voces directas de votantes;
- la cifra es «una estimación por proporción a partir de la geografía de la primera vuelta», sin datos de cómo se mueven
  los votos.

El informe pedido a mano, que quedó incompleto, lo dice aún más claro: tomar solo la proporción de los dos candidatos en
la primera vuelta da «unos 52,5 % y 47,5 %».

## 2. Contra el resultado real

**El resultado real en Bogotá** ([Semana](https://www.semana.com/nacion/articulo/asi-votaron-en-bogota-medellin-y-otras-capitales-en-colombia-en-la-segunda-vuelta-presidencial/202625/)):
Cepeda 2.235.514 votos (52,47 %) y De la Espriella 1.933.243 (45,37 %). **Sobre los dos: Cepeda 53,63 %.** El «52 %» del
jefe de Daniel es la cifra sobre todos los votos.

| Proporción de Cepeda sobre los dos | Error (puntos) |
|---|---|
| **MiroFish** (53,0) | **0,6** |
| La última encuesta del CNC, mayo de 2026 | 1,3 |
| El simulador (la página, DI-CO30) | 5,5 |
| La regla de bloques (47,3) | 6,3 |
| *No pre-registrada:* la primera vuelta reescalada a los dos (52,5) | *1,1* |

Las cifras del simulador y de la encuesta quedan en local (D21).

| | Predicción | Resultado | |
|---|---|---|---|
| PM1 | MiroFish da una cifra | 53 % | se cumple |
| PM2 | Acierta el ganador en Bogotá | Cepeda | se cumple |
| PM3 | Se equivoca más que la última encuesta | 0,6 contra 1,3 | **falla** |

**Regla (§4):** da cifra y su error (0,6) no es mayor que el del simulador (5,5). **MiroFish pasa a la segunda prueba.**

## 3. Lo que hay que decir antes de celebrarlo

1. **El acierto no viene de la simulación.** Los agentes no fueron votantes ni respondieron a las entrevistas. El informe
   repartió el resultado de la primera vuelta entre los dos candidatos, una cuenta que se hace con una calculadora. Esa
   cuenta da 52,5 %, y MiroFish lo redondeó a 53.
2. **Esa cuenta acertó por suerte del caso.** Supone que los votantes de Valencia, Fajardo y López se repartieron como los
   de los dos finalistas. Con el apoyo de Valencia a De la Espriella se esperaba lo contrario, y la regla de bloques, que lo
   asumía, se equivocó 6,3 puntos.
3. **Es una sola elección, con una sola corrida.**
4. **Lo que sí se aprende de nuestro simulador:** aquí se equivocó 5,5 puntos, porque promedió encuestas de enero a mayo
   que daban a Cepeda más ventaja. La última encuesta sola se equivocó 1,3. En el total del nivel 3, el promedio fue mejor
   que el peso por fecha (`VOTO_PESO_FECHA_RESULTS.md`), pero en esta elección pasó lo contrario.

**En resumen:** MiroFish no mostró que simular conversaciones sirva para estimar votos. Mostró que su redactor de informes
hace una cuenta razonable con los datos del documento. Para la prueba de Galán, el documento no traerá una cifra que se
pueda reescalar, y se verá qué aporta la simulación.

## 4. Errores del script (DI-MF4), sin efecto en la cifra

- **Al terminar, MiroFish deja la simulación esperando entrevistas,** en estado «running», y el script se quedó trabado.
  Se cerró a mano con `/stop`, que el informe exige.
- **Se pidieron dos informes:** uno a mano y otro el script. El script guardó una versión vieja del primero y cerró
  MiroFish antes de que terminara. El segundo sí terminó, y es el que se usa.

Los dos errores se corrigieron después, con su prueba.
