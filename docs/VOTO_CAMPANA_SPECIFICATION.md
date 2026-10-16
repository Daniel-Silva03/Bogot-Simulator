# INTENCIÓN DE VOTO CON AGENTES QUE CONOCEN LA CAMPAÑA — ¿se acercan si saben lo que pasó antes del 31 de mayo?

Pre-registro escrito el **16 de octubre de 2026**, antes de llamar al modelo. Segunda pieza de D23. Gasto: **unos USD 0,15, con
tope de USD 1**. Falta el visto bueno de Daniel.

## 1. Pregunta

**En la prueba anterior** (`VOTO_AGENTES_RESULTS.md`), los 200 agentes acertaron el ganador, pero se equivocaron 8,1 puntos y no
vieron la polarización. El centro les salió en 34 % contra 9 % real. Según el control de memoria, el modelo no conoce la campaña
de 2026.

**¿Se acercan si se les cuenta lo que se sabía antes de la elección?**

## 2. Los textos que se les dan (escritos antes de correr)

**Resumen de la campaña (C1 y C2).** Solo hechos de antes del 31 de mayo de 2026, con fuente pública. Se agrega al perfil de
cada agente:

> Lo que se sabía de la campaña presidencial a mediados de mayo de 2026, antes de la primera vuelta del 31 de mayo:
> - Iván Cepeda es el candidato del Pacto Histórico, el partido de izquierda del presidente Gustavo Petro. Ganó la consulta de su
>   partido en octubre de 2025. Su fórmula es Aída Quilcué.
> - Abelardo de la Espriella es abogado y candidato del movimiento Defensores de la Patria, de derecha. Su fórmula es José Manuel
>   Restrepo.
> - Paloma Valencia es senadora del Centro Democrático, de derecha. Su fórmula es Juan Daniel Oviedo.
> - Sergio Fajardo es un candidato de centro.
> - Claudia López, exalcaldesa de Bogotá, es candidata de centro. Su fórmula es Leonardo Huerta.

**La encuesta (solo C2).** Se agrega después del resumen:

> Según la encuesta nacional de Invamer publicada el 21 de mayo de 2026 (trabajo de campo del 13 al 20 de mayo, 3.800
> entrevistas en todo el país), la intención de voto era: Iván Cepeda 44,6 %, Abelardo de la Espriella 31,6 %, Paloma Valencia
> 14,0 %, Sergio Fajardo 2,4 %, Claudia López 2,2 %, Santiago Botero 1,4 %, y los demás, menos de 1 % cada uno. Es una encuesta
> nacional, no solo de Bogotá.

**Lo que se declara:**
- **Los textos los escribí yo, conociendo el resultado.**
  - Para no filtrarlo, solo traen hechos públicos de antes de la elección, de fuentes citadas: noticias de la campaña, y la
    encuesta Invamer en Noticias Caracol.
  - **No dicen** quién ganó, ni que la elección se polarizó, ni nada de Bogotá en particular.
- **La encuesta es nacional.** En Bogotá, el resultado fue distinto: Cepeda 42,4 y De la Espriella 38,4.
- **Ningún dato del CNC va al modelo:** las encuestas del CNC de mayo tienen cifras de Bogotá, pero D21 no deja mandar ni sus
  agregados.

## 3. Los brazos

**Los mismos 200 agentes, la misma pregunta y las mismas opciones** que en `VOTO_AGENTES`, con probabilidades.
- **A:** sin contexto (ya corrido: EAM 8,14).
- **C1:** con el resumen de la campaña.
- **C2:** con el resumen y la encuesta.

**Referencia:** «copiar la encuesta», es decir, la encuesta Invamer tal cual, normalizada entre los 11 candidatos, con los demás
en 0. Si C2 no le gana, los agentes no le agregan nada a la encuesta en Bogotá.

**Lo que se vio antes de subir este documento (16/10).** Al probar el circuito sin gasto, se calculó la referencia: **copiar la
encuesta se equivoca 1,84 puntos** contra Bogotá, y acierta el primero y el segundo. No depende de los agentes: sale de las cifras
públicas de Invamer y de la Registraduría. Quiere decir que H3 es muy exigente: la encuesta nacional ya quedó muy cerca de
Bogotá. Las reglas y predicciones no se cambiaron.

## 4. Reglas (escritas antes de calcular)

**Los agentes sirven para la intención de voto si el mejor de C1 y C2 cumple las tres de `VOTO_AGENTES`:**
- **R1:** EAM ≤ 5,4.
- **R2:** Cepeda primero.
- **R3:** Cepeda y De la Espriella, primero y segundo.

**Las hipótesis:**
- **H1:** C1 mejora a A si su EAM es al menos 1 punto menor (7,14 o menos).
- **H2:** C2 mejora a C1 en al menos 1 punto.
- **H3:** C2 le gana a copiar la encuesta (EAM menor).

## 5. Predicciones

- **PC1.** H1 se cumple: saber quién es de izquierda y de derecha concentra el voto.
- **PC2.** H2 se cumple: la encuesta acerca más.
- **PC3.** C2 cumple R1 a R3.
- **PC4.** H3 no se cumple: C2 queda cerca de la encuesta, pero no le gana. La encuesta ya es la mejor información, y los agentes
  la repiten.

## 6. Gasto y código

- **Gasto:** 400 llamadas nuevas (200 de C1 y 200 de C2): unos USD 0,15, con tope de USD 1.
- **Al modelo** van los perfiles de la EPC (pública, anónima), los nombres de los candidatos y los dos textos de §2. Ningún dato
  del CNC.
- **Código:** `src/experiments/voto_campana.py`, que reutiliza `voto_agentes`, con su prueba. Resultados en
  `VOTO_CAMPANA_RESULTS.md`.
