# MIROFISH CON RESIDENTES DE BOGOTÁ, ENTREVISTADOS

Pre-registro escrito el **9 de octubre de 2026**, antes de correr nada. Lo pidió Daniel: mejorar MiroFish para que sus
agentes sean residentes, y probarlo solo en Bogotá. **Gasto: unos USD 0,10, con tope de USD 1.**

## 1. La pregunta

En las tres pruebas anteriores, los agentes de MiroFish fueron los actores del documento (políticos, medios, entidades) y
nunca respondieron entrevistas, porque el informe exige cerrar la simulación. Sin datos, sus informes dijeron «la mitad»
para todo (`MIROFISH_DISCRIMINACION_RESULTS.md`).

**Dos cambios:**
1. **La semilla trae doce residentes de Bogotá,** descritos sin ninguna opinión, para que MiroFish los convierta en
   agentes.
2. **Se les entrevista antes de cerrar la simulación,** con cinco preguntas de sí o no, y se cuentan sus respuestas. No se
   pide informe.

**La pregunta:** así, ¿distingue MiroFish entre preguntas con resultados muy distintos en Bogotá? ¿Cómo le va frente a
nuestro simulador?

**Ojo:** esto es dejar que el modelo de lenguaje conteste por personas inventadas, lo que descartamos en el Experimento 8.
Se mide igual, contra cifras reales.

## 2. Método

**La semilla:** `docs/anexos/mirofish_semilla_bogota_residentes.md`. Son los hechos de la gestión de Galán (los mismos de
la prueba de Galán) más una tabla de doce residentes con nombre, edad, localidad, estrato y oficio. Sin opiniones.
- **Los residentes van en proporción a los estratos de Bogotá:** 6 de estratos 1-2, 4 de estrato 3 y 2 de estratos 4-6.
- **Al contar, cada uno pesa según la población adulta de su nivel** (`PESO_NIVEL`, población sintética de la
  Multipropósito 2021): 1-2: 48,9 %, 3: 34,7 % y 4-6: 16,3 %.

**MiroFish,** con la misma instalación, modelo y tope: Luna y 10 rondas.
- **Se corre con** `python src/experiments/mirofish_segunda_vuelta.py --caso bogota_residentes`.
- **La petición** (`REQUERIMIENTO_RESIDENTES`): simular la conversación de los habitantes adultos de Bogotá sobre la vida
  en la ciudad y la gestión del alcalde en el segundo semestre de 2025.
- **Al terminar las rondas,** con la simulación todavía abierta, se hacen las cinco preguntas a todos los agentes
  (`/interview/all`), solo en Reddit, cada una precedida de: «Responda empezando con una sola palabra, SÍ o NO, y después
  una frase corta que explique por qué».

**Las cinco preguntas y su resultado en la Encuesta de Percepción Ciudadana 2025 de Bogotá Cómo Vamos**
([El Tiempo](https://www.eltiempo.com/amp/bogota/bogotanos-se-sienten-mas-inseguros-pero-mas-optimistas-resultados-de-la-encuesta-de-percepcion-ciudadana-2025-3514151)):

| Clave | Pregunta | EPC 2025 |
|---|---|---|
| satisfaccion | ¿Está usted satisfecho(a) con Bogotá como un lugar para vivir? | 61 % |
| orgullo | ¿Se siente usted orgulloso(a) de Bogotá? | 57 % |
| buen_camino | ¿Cree usted que las cosas en Bogotá van por buen camino? | 59 % |
| aprobacion | ¿Aprueba usted la gestión del alcalde Carlos Fernando Galán? | 26 % |
| victima | Durante el último año, ¿fue usted víctima de algún delito en Bogotá? | 15 % |

## 3. Cómo se cuenta

- **Cada respuesta** es «sí» o «no» según su primera palabra (`leer_si_no`). Si no empieza por ninguna, no cuenta.
- **Solo cuentan los doce residentes,** reconocidos por su nombre. Las instituciones no.
- **El porcentaje** es el de «sí», ponderado por estrato (`porcentaje_residentes`). Si responden menos de 9 residentes,
  esa pregunta queda sin cifra y cuenta como fallo.

## 4. Con qué se compara

1. **La EPC 2025** (la tabla de §2): es el resultado real.
2. **El simulador:** lo que da hoy la página para esas preguntas.
   - **Satisfacción, orgullo, buen camino y víctima de delito:** el dato medido del catálogo (`CV1`, `AG2`, `AG1`,
     `VS15`; EPC 2022-2024), con el lado favorable de DI-CO18.
   - **Aprobación:** la estimación del 9/10 para Galán (47,3 %, `MIROFISH_GALAN_RESULTS.md`).
3. **Decir 50 % para todo:** error medio de 17,2 puntos.

## 5. Regla y predicciones

**MiroFish con residentes distingue si se cumplen las tres condiciones:**
1. **R1, el orden:** la correlación de Spearman entre sus cinco cifras y las de la EPC 2025 es de 0,7 o más;
2. **R2, la separación:** entre su cifra más alta y la más baja hay al menos 20 puntos (en la realidad, 46);
3. **R3, el error:** su error medio es menor que el de decir 50 % para todo (17,2 puntos).

**Se reporta además el error del simulador,** sin que decida.

**Predicciones:**
- **PR1.** MiroFish con residentes no cumple la regla.
- **PR2.** El simulador se equivoca menos, en promedio, que MiroFish.
- **PR3.** MiroFish exagera la victimización: da más de 25 % (el real es 15 %).

## 6. Lo que ya se sabe, y se declara

- **Los cinco resultados de la EPC 2025.**
- **La estimación del simulador para Galán** (47,3 %).
- **Los datos del catálogo para las otras cuatro** no los he mirado. Se calculan después de subir este documento, igual
  que siempre.
- **Los residentes los inventé yo,** sabiendo los resultados. Para no sesgarlos, solo tienen datos de quién son, ninguna
  opinión; una prueba lo verifica.

## 7. Gasto, datos y código

- **Gasto:**
  - la simulación, unos USD 0,05;
  - las cinco entrevistas a todos los agentes, unas 125 llamadas cortas, unos USD 0,05.

  **Tope de USD 1.**
- **Nada del CNC** sale hacia MiroFish, Zep ni el modelo. De la EPC solo sale, en la semilla, el peso de cada estrato,
  que es un agregado público.
- **Las salidas** (respuestas de cada agente, registro, log) quedan en `data/processed/mirofish/residentes/`, ignoradas
  por git.
- **Código:** `src/experiments/mirofish_segunda_vuelta.py` (`bogota_residentes`, `entrevistar`, `porcentaje_residentes`).
- **Pruebas:** `tests/test_mirofish_segunda_vuelta.py`.
- **Resultados:** `MIROFISH_RESIDENTES_RESULTS.md`.
