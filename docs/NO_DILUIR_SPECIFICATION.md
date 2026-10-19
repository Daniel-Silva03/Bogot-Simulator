# QUE LOS AGENTES NO DILUYAN LA ENCUESTA — ¿se corrige, y se sostiene en otra elección?

Pre-registro escrito el **19 de octubre de 2026**, antes de llamar al modelo. Mejora 1 del daily: con la encuesta, los agentes le
quitan votos a los punteros y se los pasan al centro (`VOTO_CAMPANA_RESULTS.md`). Gasto: **unos USD 0,20, con tope de USD 1**.
Falta el visto bueno de Daniel.

## 1. Pregunta

**En la primera vuelta de 2026,** los agentes con el resumen y la encuesta (C2) se equivocaron 3,49 en Bogotá. Copiar la encuesta
se equivocó 1,84. A De la Espriella le quitaron 10 puntos frente a la encuesta, y a Fajardo y López les subieron 5.

**Dos formas de corregirlo:**
- **una instrucción:** que no corran el voto hacia los candidatos con poca intención;
- **una calibración, sin llamar al modelo:** ajustar las probabilidades de cada agente para que el total coincida con la encuesta.
  Cada agente conserva cómo se aparta del promedio.

**Lo importante es que se sostenga en otra elección,** no solo en la que ya conocemos.

## 2. La instrucción (escrita antes de correr)

Se agrega al final del contexto de campaña:

> Cuando tengas una encuesta, úsala como punto de partida para personas como esta. No corras su voto hacia los candidatos que la
> encuesta muestra con poca intención. Si sus respuestas no dicen claramente otra cosa, inclínate por los candidatos que la
> encuesta pone adelante.

No dice quién ganó ni nombra a ningún candidato.

## 3. Parte 1, desarrollo: la primera vuelta de 2026 (ya conocida)

**Los 200 agentes, con el resumen y la encuesta Invamer de `VOTO_CAMPANA`:**
- **C2:** como antes, leído de la caché. EAM 3,49.
- **C2i:** C2 más la instrucción. 200 llamadas.
- **C2k:** las respuestas de C2, calibradas.
  - **El ajuste:** la probabilidad de cada candidato se multiplica, en todos los agentes, por la razón entre la encuesta y el total
    de los agentes; luego se renormaliza cada agente. Como al renormalizar el total se mueve, el ajuste se repite hasta que el
    total quede en la encuesta (a 0,01 puntos).
  - **Sin llamar al modelo.**
  - **Lo que da en el total:** queda casi igual a copiar la encuesta (1,84). Lo que cambia es cómo reparte por grupos. Por eso
    también se mide su error por grupo con el CNC de mayo (`GRUPOS_Y_GALAN_2026`, parte A).

**Se declara:** el desarrollo es la misma elección con que se vio el problema, así que cualquier mejora ahí puede ser a la medida.
Por eso la parte 2 decide.

**Se declara también, antes de subir este pre-registro:** al probar el código en modo simulado, por un descuido, se leyó la caché
real de C2. Así se vio la calibración **en un solo paso**: EAM 1,86, y error por grupos de 6,7 contra 6,6 de C2. Después se cambió
el ajuste a repetido, porque la prueba del código mostró que un solo paso no deja el total en la encuesta, no por ese número.
Aun así, **RK1 ya no es a ciegas:** se reporta, pero la calibración se decide por RK2, que nadie ha visto. El modo simulado ya no
lee la caché real.

## 4. Parte 2, confirmación: la segunda vuelta de 2026 (Bogotá)

**Lo real:** el preconteo de la Registraduría en Bogotá, publicado por El Tiempo: Cepeda 2.235.514 y De la Espriella 1.933.243.
Entre los dos, **Cepeda 53,6 %.**

**El contexto para los agentes:** solo lo que se sabía antes del 21 de junio.
- **El mismo resumen de la campaña**, más una línea: «En la primera vuelta del 31 de mayo, en todo el país, De la Espriella sacó
  44,1 % y Cepeda 41,3 %; los dos pasaron a la segunda vuelta del 21 de junio.»
- **La encuesta:** «Según la encuesta nacional de Guarumo y Ecoanalítica para El Tiempo (trabajo de campo del 8 al 11 de junio de
  2026, 2.073 adultos en 54 municipios), la intención de voto para la segunda vuelta era: Abelardo de la Espriella 52,6 % e Iván
  Cepeda 45,0 %. Es una encuesta nacional, no solo de Bogotá.»
- **Nada de Bogotá en particular,** ni de la primera vuelta ni de la segunda.

**La pregunta:** «Si la segunda vuelta presidencial de 2026 fuera hoy, entre Iván Cepeda y Abelardo de la Espriella, ¿por quién
votaría?». Opciones: los dos, «Votaría en blanco» y «No votaría».

**Los brazos:**
- **S:** sin la instrucción. 200 llamadas.
- **Si:** con la instrucción. 200 llamadas.
- **Sk:** S calibrado a la encuesta de Guarumo. Sin llamadas.

**Las referencias:**
- **copiar la encuesta nacional:** Cepeda 45,0 / 97,6 = 46,1 %, un error de 7,5 contra Bogotá;
- **decir 50 %:** un error de 3,6.

**La medida:** el error en la parte de Cepeda entre los dos, y si el ganador en Bogotá (Cepeda) es el correcto.

## 5. Reglas (escritas antes de calcular)

**La instrucción sirve si se cumplen las dos:**
- **RN1, desarrollo:** C2i tiene un EAM al menos 0,5 menor que C2 (2,99 o menos).
- **RN2, confirmación:** Si no se equivoca más que S en la segunda vuelta.

**La calibración sirve si se cumple RK2** (RK1 se reporta, pero ya no es a ciegas, §3):
- **RK1, desarrollo, no a ciegas:** C2k reparte por grupos con menos error que C2. Error contra el CNC de mayo, la parte A de
  `GRUPOS_Y_GALAN_2026`.
- **RK2, confirmación:** Sk no se equivoca más que S en la segunda vuelta.

**Lo que más importa para D23, sin peso en las reglas:** si en la segunda vuelta los agentes, con o sin instrucción, le ganan a
copiar la encuesta nacional. Es decir: si corrigen la encuesta del país hacia lo que votó Bogotá.

## 6. Predicciones

- **PN1.** RN1 se cumple: la instrucción acerca a los agentes a la encuesta en la primera vuelta.
- **PN2.** RN2 no se cumple: en la segunda vuelta, la instrucción los acerca a la encuesta nacional y los aleja de Bogotá.
- **PN3.** S le gana a copiar la encuesta nacional: los agentes bogotanos dan a Cepeda más que el país.
- **PN4.** S acierta que Cepeda gana en Bogotá.

## 7. Gasto y código

- **Gasto:** 600 llamadas (C2i, S y Si), unos USD 0,20, con tope de USD 1.
- **Al modelo** van los perfiles de la EPC (pública, anónima) y los textos de §2 y §4. Ningún dato del CNC: la parte A de grupos
  usa sus cifras solo dentro del equipo, sin imprimirlas.
- **Código:** `src/experiments/no_diluir.py`, con su prueba. Resultados en `NO_DILUIR_RESULTS.md`.
