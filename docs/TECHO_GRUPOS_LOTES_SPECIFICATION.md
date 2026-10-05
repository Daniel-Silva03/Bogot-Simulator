# TECHO DE LOS GRUPOS EN EL BANCO AMPLIADO (lotes 2 a 4)

Pre-registro escrito el **5 de octubre de 2026**, antes de calcular nada. Sin gasto en API.
Repite `TECHO_GRUPOS_SPECIFICATION.md` (lectura A en el lote 1: oráculo 0,952, réplica 0,856, contra
0,62 del simulador) con las preguntas de práctica de los lotes nuevos (`BANCO_PREGUNTAS_NUEVAS.md`
§11-13). Lo pidió Daniel.

## 1. Pregunta

En las preguntas nuevas del banco (sobre todo la Bienal de Culturas 2025, de Bogotá):
1. **¿cuál es el techo** de las diferencias claras entre grupos que se pueden ordenar bien?
2. **¿cuánto acierta el tono general del simulador** en esos mismos pares?

La segunda no estaba en la prueba del lote 1, porque allí el 62 % ya se conocía. Sin ella, el techo de
los lotes nuevos no tiene con qué compararse.

## 2. Datos

Preguntas de práctica con pares claros y sin exclusión de estructura:
- **lote 2** (Cultura Ambiental 2021), 5 preguntas;
- **lote 3** (Bienal de Culturas 2025), 97;
- **lote 4** (Barrios Vivos 2025), 1.

**La cifra principal junta los lotes 2 y 3.** El lote 4 no representa a la ciudad y se informa aparte.
Los guardados no se tocan.

## 3. Medidas

**Las tres, iguales a la prueba del lote 1** (`techo_grupos.py`, `practica_puente.py`).

1. **Oráculo por Bayes empírico.** τ² por dimensión, con todos los pares de los lotes 2 y 3, y
   D = 1 y **D = 2,03** (la cifra que decide). No se conoce el efecto de diseño de estas encuestas; se
   usa el de la EPC, como en la prueba anterior.
2. **Réplica por mitades.** 200 particiones con semilla **20261008**; pares claros en una mitad y su
   orden en la otra.
   - **Partición por persona**, en los tres lotes: la copia reducida de la Bienal no trae la manzana
     (se quitó por ser un dato de ubicación) y las otras no traen conglomerado.
   - Como en el lote 1, esto vuelve las mitades algo más parecidas: la réplica queda optimista.
3. **Tono general del simulador.** El tono de DI-PP4 (`practica_puente.tono_general`), los grupos de los
   agentes con los cortes del banco (`grupos_agentes`, sin cortes del CNC) y la medida conjunta de
   aciertos / pares (DI-PP5).

## 4. Predicciones (escritas antes de calcular)

- **P1.** Oráculo con D = 2,03 en los lotes 2 y 3: ≥ 0,90. La Bienal tiene más de 5.400 respuestas por
  pregunta, así que sus pares claros deberían ser aun más sólidos que los del lote 1.
- **P2.** Réplica por mitades en los lotes 2 y 3: ≥ 0,85.
- **P3.** Tono general del simulador en los lotes 2 y 3: entre 0,55 y 0,70.
- **P4.** La distancia entre el oráculo y el tono es de al menos 20 puntos, como en el lote 1 (33).

## 5. Regla de lectura (la misma del lote 1, escrita antes de calcular)

La cifra que decide es el oráculo con D = 2,03 en los lotes 2 y 3:
- **A, hay espacio:** ≥ 0,80.
- **B, espacio moderado:** entre 0,70 y 0,80.
- **C, casi no hay espacio:** < 0,70.

Si la réplica la contradice, se informa y se discute. No se cambia la regla.

Además, para leer el tono: **si en los lotes 2 y 3 acierta 0,70 o más, el «62 %» del lote 1 no se
generaliza**, y se revisa por qué antes de usar esa cifra en la página («acertó el 62 %…»). Si acierta
menos de 0,70, la cifra de la página se mantiene, con la del banco ampliado al lado.

## 6. Código

`src/experiments/techo_grupos_lotes.py`, con pruebas en `tests/test_techo_grupos_lotes.py`. Reutiliza
`techo_grupos` (oráculo, réplica), `practica_puente` (tono) y las lecturas de `banco_lote2` y
`banco_lote3`. Los resultados van a `TECHO_GRUPOS_LOTES_RESULTS.md`, contra este pre-registro.
