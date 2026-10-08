# INTENCIÓN DE VOTO SIMULADA POR GRUPOS

Pre-registro escrito el **8 de octubre de 2026**, antes de calcular ninguna estimación por grupo. Lo pidió Daniel. La
revisión jurídica cubre los grupos (D21, nota del 8/10).
**Gasto: USD 0.** Se usan las elecciones de Luna del nivel 3, ya recuperadas (`voto_peso_fecha --recuperar`).

## 1. Qué se quiere mostrar

Hoy la página da la intención de voto simulada solo para todo Bogotá (DI-CO30). Las encuestas del CNC no sirven por
localidad, pero sí traen sexo, estrato y edad. La pregunta es si la página puede decir algo como «Cepeda, más fuerte en
estrato 1-2 que en 4-6», con un error medido.

## 2. Método

**La estimación de un grupo** es la media del resultado real de ese grupo en las mismas preguntas que Luna eligió para el
total (DI-VG3). Luna no cambia, ni lo que elige.

**Los grupos son gruesos**, porque las bases son chicas (DI-VG1):
- **sexo:** hombres, mujeres;
- **estrato:** 1-2, 3 y 4-6;
- **edad:** joven (18-25 en 2021-2022, 18-24 en 2026), media (26-55 o 25-54) y mayor (56+ o 55+).

**El rango (h) de cada corte** es el cuantil 80 % del error por grupo en la práctica: las 158 de práctica del lote 7, cada
una con las elecciones de las otras familias.

**Un grupo real cuenta** si su base es de 30 personas o más (DI-VG2).

## 3. La prueba

**Objetivos:** las 215 guardadas del lote 7, versión «con su encuesta», la del nivel 3.

**Medidas, por corte:**
- **EAM de los grupos:** cada estimación de grupo contra el resultado real de ese grupo;
- **EAM de la referencia:** el total simulado puesto en cada grupo. Es lo que diría la página sin desglose;
- **cobertura** de ±h;
- **el sentido de la diferencia:** entre los dos grupos extremos (mujeres − hombres; estrato 1-2 − 4-6; joven − mayor),
  en las preguntas donde la diferencia real es de 10 puntos o más, ¿la estimada va en el mismo sentido?

## 4. Regla

**Cada corte se decide por separado. Se muestra en la página si cumple las dos condiciones:**
1. **R1:** EAM de los grupos ≤ 0,9 × EAM de la referencia. El desglose dice algo más que el total;
2. **R2:** hay al menos 10 preguntas con diferencia real clara, y en ≥ 80 % la estimada va en el mismo sentido.

**Un corte que no cumple no se muestra,** y se anota por qué.

## 5. Predicciones

- **PG1.** Estrato se muestra.
- **PG2.** Sexo no se muestra: hay pocas diferencias claras entre hombres y mujeres.
- **PG3.** Edad se muestra.

## 6. Lo que ya se vio, y se declara

- **Los tamaños de las bases por grupo y los cortes de edad de cada estudio** (DI-VG1), para definir los grupos. No se
  miraron porcentajes por grupo.
- **Los resultados del nivel 3 para el total** y el ejemplo de Cepeda contra De la Espriella en la página.
- **Las 215 guardadas ya se usaron** para el total (nivel 3) y para el peso por fecha. Aquí se miden por primera vez por
  grupo.

## 7. Lo que no se sube

Por D21:
- **La salida** queda en `data/processed/banco/`, ignorada por git.
- **`VOTO_GRUPOS_RESULTS.md`** da solo cifras de error y acierto, sin porcentajes de ningún candidato ni grupo.

## 8. Código

- **Código:** `src/experiments/voto_grupos.py`.
- **Pruebas:** `tests/test_voto_grupos.py`.
- **Resultados:** `VOTO_GRUPOS_RESULTS.md`.
- **Si algún corte pasa,** el diseño en la página va aparte y se muestra a Daniel antes de publicarlo.
