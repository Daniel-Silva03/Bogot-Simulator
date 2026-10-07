# INTENCIÓN DE VOTO SIMULADA — nivel 3 de D21

Pre-registro escrito el **7 de octubre de 2026**, antes de calcular el guardado del lote 7 y antes de hacer ninguna
llamada. Daniel eligió:
- **el método:** el de D19;
- **la validación:** las 215 guardadas y la Registraduría;
- **la regla:** la propuesta;
- **sin la imagen de personajes.**

Gasto de la parte 1: **~USD 0,90, con tope de USD 1,50**, a confirmar tras una llamada de prueba.

**Nada de lo que salga se muestra en la página antes de la revisión jurídica del CNC (D21),** pase o no pase.

## 1. Pregunta

Alguien escribe una pregunta de voto que nunca se midió, o no hace poco. Por ejemplo: «¿votaría por Paloma Valencia en una
segunda vuelta contra Iván Cepeda?».

**¿Puede el simulador estimar qué porcentaje de Bogotá votaría así, con un error comparable al de una encuesta?**

## 2. Método (el de D19, con el banco electoral)

**La estimación:**
- `nivel_parecidas_b` (instrucciones, lectura con DI-NB6, reintento), con `openai/gpt-6-luna` a temperatura 0, el texto y
  las categorías de cada pregunta del lote 7;
- **candidatas:** las 158 de práctica del lote 7 (`BANCO_PREGUNTAS_NUEVAS.md` §16), con su resultado real de Bogotá;
- **la estimación es la media real de las elegidas.** El modelo no pone cifras ni contesta por nadie.

**El rango (h)** es el cuantil 80 % del error en la práctica, con cada pregunta de práctica estimada con las otras familias
de práctica. Se fija antes de evaluar el guardado.

**Dos versiones, las dos sobre las mismas preguntas:**
- **«con su encuesta»:** pueden elegirse preguntas de la misma encuesta, salvo las de su misma familia. Es el caso de una
  pregunta nueva en plena campaña, cuando hay una encuesta reciente.
- **«sin su encuesta»:** solo preguntas de otras encuestas. Es el caso de un momento sin medición reciente.

**Dos referencias simples:**
- **M0:** el promedio real de las 158 de práctica.
- **Último dato:** la media de las preguntas de práctica que nombran a la misma opción (mismo candidato, fórmula, consulta
  o tendencia), de la encuesta más cercana en el tiempo. Si no hay ninguna, M0. En «sin su encuesta» no cuenta la misma
  encuesta.

## 3. Parte 1 — las 215 guardadas del lote 7 (en este PC)

**Objetivos:** las 215 guardadas del lote 7. Su resultado real se calcula **después** de subir este documento, con el mismo
cálculo del lote 7. Las que no pasen la regla de estructura quedan fuera.

**Medidas, en cada versión:**
- **EAM**, en puntos porcentuales, contra el resultado real;
- **segundas vueltas:**
  - para cada segunda vuelta guardada con sus dos candidatos, ¿la estimación pone adelante al mismo que el resultado real?;
  - **«probablemente gana X»** se dice cuando la diferencia estimada entre los dos supera h₂, el cuantil 80 % del error de la
    diferencia en la práctica;
  - el acierto se cuenta sobre esas;
- **cobertura:** el porcentaje de preguntas con el real dentro de ±h;
- **lo mismo para M0 y el último dato.**

**Regla: la simulación sirve si, en la versión «con su encuesta», se cumplen las tres condiciones:**
1. **EAM ≤ 6 puntos;**
2. **en las segundas vueltas,** acierta quién va adelante en ≥ 80 % y, al decir «probablemente gana», en ≥ 90 %. Si lo dice
   menos de 5 veces, esta segunda parte se reporta pero no cuenta;
3. **EAM ≤ 0,8 × el menor EAM** entre M0 y el último dato.

**La versión «sin su encuesta» se reporta.** Si no cumple, la simulación solo podría usarse cuando hay una encuesta reciente
que nombra a los candidatos, y así lo diría.

## 4. Parte 2 — contra la Registraduría (en el PC personal de Daniel)

**Los resultados reales en Bogotá** (`BSS_ELECTORAL_DIR`, D16): primera y segunda vuelta de 2022, y primera vuelta de 2026.
**La segunda vuelta de 2026 no se toca:** tiene su propio pre-registro (`SEGUNDA_VUELTA_2026_SPECIFICATION.md`).

**Qué se simula:** para cada elección, cada candidato con pregunta medida en una encuesta **anterior a la elección**, con
las candidatas de práctica de encuestas anteriores a la elección y sin la familia de esa pregunta.

**Con qué se compara.** El porcentaje de cada candidato **sobre los votos por candidatos y en blanco** en Bogotá.
- **La estimación se normaliza igual:** se divide por la suma de las opciones con nombre y el blanco de esa pregunta.
- **La encuesta misma, normalizada así, es la referencia:** muestra cuánto se equivoca una encuesta contra el resultado.

**Medida:**
- el EAM de la simulación;
- el EAM de la propia encuesta;
- si la simulación acierta quién va primero.

**Esta parte se reporta, sin regla.** Son pocas elecciones, y la distancia entre encuesta y resultado depende de más cosas
que el simulador. Se escribe después en un documento propio, con su enmienda fechada si hace falta.

## 5. Predicciones (escritas antes de calcular)

- **PV1.** En «con su encuesta», el EAM queda entre 4 y 8 puntos.
- **PV2.** «Con su encuesta» cumple la regla.
- **PV3.** «Sin su encuesta» tiene un EAM al menos 3 puntos mayor que «con su encuesta».
- **PV4.** En las segundas vueltas, el último dato acierta quién va adelante casi tan bien como la simulación: a menos de
  10 puntos.

## 6. Gasto

**Unas 746 llamadas a ~USD 0,0012:**
- la práctica (158) y el guardado (215);
- cada uno en las dos versiones.

**Total:** ~USD 0,90, con tope de USD 1,50.
- **Antes de correr,** una llamada de prueba.
- **El código se detiene solo** al llegar al tope o si el servicio falla.

## 7. Lo que no se sube

Los resultados de las encuestas del CNC, por D21:
- **el guardado del lote 7 y la salida** quedan en `data/processed/banco/`, ignorados;
- **`VOTO_SIMULADO_RESULTS.md`** da solo cifras de error y acierto, sin porcentajes de ningún candidato.

## 8. Código

- **Código:** `src/experiments/voto_simulado.py`.
- **Pruebas:** `tests/test_voto_simulado.py`.
- **Resultados:** `VOTO_SIMULADO_RESULTS.md`.
