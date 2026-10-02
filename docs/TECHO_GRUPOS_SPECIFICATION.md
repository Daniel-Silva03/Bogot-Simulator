# TECHO DE LOS GRUPOS — ¿cuánto se puede acertar del orden entre grupos?

Pre-registro escrito el **2 de octubre de 2026**, antes de calcular nada. Sin gasto en API.

## 1. Pregunta

En las preguntas de práctica del banco (`BANCO_PREGUNTAS_NUEVAS.md` §9-10), el puente ordena bien
el 60-63 % de las 699 diferencias claras entre grupos, y el «tono general», sin API, el 62 %
(azar: 50 %). **¿Cuánto es lo máximo que se podría acertar?** Ni siquiera alguien que conociera
la opinión real de toda la población acertaría el 100 %, porque cada encuesta tiene ruido de
muestra y algunas «diferencias claras» salen al revés por azar.

- Si el techo está cerca del 62 %, no hay espacio para mejorar y se deja ese frente.
- Si está muy arriba, hay espacio, y lo que falta es información, no menos ruido.

Esto decide cuánto esfuerzo merece mejorar el orden de los grupos. El nivel (cuántos están de
acuerdo) es otra prueba (camino 2) y no entra aquí.

## 2. Datos

- Las preguntas de práctica que cuentan en la medida conjunta: **91 preguntas, 699 pares**
  (`data/processed/banco/reales_practica.json`, mismos grupos y regla que DI-BR1 a DI-BR5).
  **Las 51 guardadas no se tocan.**
- La medida 1 necesita microdato: entran las 89 de ECP y EPC (675 de los 699 pares en la muestra
  completa); quedan fuera las 2 del CNC (metro y Corredor Verde), que solo traen cifras agregadas. La medida 2 usa solo cifras agregadas y
  entran las 91.

## 3. Medidas

**Medida 1 — réplica por mitades (sin supuestos de modelo).** Se parte la muestra de cada fuente en
dos mitades al azar, **por conglomerado**:
- EPC 2019, 2023 y 2024: localidad × manzana (`diseno.CONGLOMERADO_POR_ANIO`, DI-D7).
- ECP 2023: el hogar (`DIRECTORIO`). El archivo público no trae el segmento.
- EPC 2017 y 2022: no tienen conglomerado (`diseno.SIN_CONGLOMERADO`); se parte por persona.

En la mitad A se calculan los porcentajes favorables por grupo y sus pares claros, con la regla
de siempre (z > 1,96, bases sin ponderar de la mitad; `banco_reales.pares_claros`). En la mitad B
se mira si cada par sale en el mismo orden; un empate cuenta como fallo. La medida conjunta es
aciertos / pares sobre todas las preguntas (como DI-PP5). Se repite con **200 particiones**
(semilla **20261002**) y se informa la media y el intervalo del 5 % al 95 %.

Responde a: «si una encuesta del mismo tamaño se repitiera, ¿cuántas de las diferencias claras
de la primera saldrían en el mismo orden?», pero con dos encuestas de **mitad de tamaño**. Por
eso es una cota **baja** del techo. Partir por hogar o por persona, y no por segmento, la sube un
poco.

**Medida 2 — oráculo por Bayes empírico (con un supuesto).** Responde a: «alguien que conociera
la opinión real de toda la población, ¿en cuántos de los 699 pares coincidiría con la encuesta?».
Para cada par de grupos (todos, no solo los claros), z = diferencia / error, con el error de la
regla. Se supone que, dentro de cada dimensión (sexo, edad, estrato), las diferencias verdaderas
se reparten normales con media 0 y varianza τ², y que el ruido de z tiene varianza D. Entonces:

- τ² = var(z) − D, por dimensión (mínimo 0);
- para un par claro con z observado, la probabilidad de que el orden real sea el observado es
  Φ(|z| · τ / √(D · (τ² + D)));
- el techo es el promedio sobre los 699 pares claros.

Se calcula con **D = 1** (la regla, sin efecto de diseño) y con **D = 2,03** (DEFF mediano de la
EPC, DI-D7), que es la cifra principal. El supuesto normal encoge mucho las diferencias grandes
(el estrato), así que tiende a dar un techo **más bajo** que el verdadero.

## 4. Predicciones (escritas antes de calcular)

- **P1.** Réplica por mitades: media entre 0,70 y 0,85.
- **P2.** Oráculo con D = 1: ≥ 0,85.
- **P3.** Oráculo con D = 2,03: entre 0,75 y 0,90.
- **P4.** La réplica por mitades queda por debajo del oráculo con D = 2,03.

## 5. Regla de lectura (escrita antes de calcular)

La cifra que decide es el **oráculo con D = 2,03**. Se compara con el 62 % del tono general:

- **A — hay espacio:** ≥ 0,80. El techo está al menos 18 puntos arriba. Lo que falta para acertar
  los grupos es información sobre la pregunta, no menos ruido. Mejorar requiere datos nuevos
  (camino 3); no otra versión del puente, por la regla ya escrita en §10.3 del banco.
- **B — espacio moderado:** entre 0,70 y 0,80.
- **C — casi no hay espacio:** < 0,70. El 62 % está cerca de lo posible y se deja definitivamente
  de trabajar en el orden de los grupos.

Si la réplica por mitades contradice la lectura (por ejemplo, oráculo en A y réplica < 0,65), se
informa y se discute. **No se cambia la regla.**

## 6. Código

`src/experiments/techo_grupos.py`: reutiliza `banco_reales` (carga de fuentes, `resultado`,
`pares_claros`). Las pruebas con datos inventados van en `tests/test_techo_grupos.py`. Los
resultados van a `TECHO_GRUPOS_RESULTS.md`, contra este pre-registro.
