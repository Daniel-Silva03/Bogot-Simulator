# FASE B DEL PLAN DE MEJORAS: ¿DEBEN LOS AGENTES MOVER UN DATO YA MEDIDO, Y CUÁNTO?

Pre-registro escrito el **19 de octubre de 2026**, antes de llamar al modelo. Sigue `PLAN_MEJORAS_PREDICTOR_BOGOTA.md` §4 (Fase
B, selector y combinador) y `BENCHMARK_FASE_A.md`. Lo pidió Daniel. Gasto: **unos USD 0,70, con tope de USD 2.**

## 1. Pregunta

En una pregunta ya medida (problema A del plan), la Fase A mostró que repetir el último dato les gana a los agentes. Pero puede
que los agentes traigan algo de señal del cambio, aunque solos se equivoquen más. **¿Mejora la persistencia si se mueve una
fracción λ hacia lo que dicen los agentes?**

> predicción = persistencia + λ · (agentes − persistencia)

Si λ debe ser cero, la regla de la página es clara: con dato medido, se muestra el dato. Es la decisión que más importa para el
producto (por ejemplo, en Galán).

## 2. Por qué así y no un selector con todas las pruebas

El selector de la Fase A se diseñó mirando todas las pruebas que ya existen: evaluarlo con ellas no sería a ciegas. Aquí se
generan predicciones nuevas en un conjunto amplio y reservado por año, como pide el plan (§3.3: dejar fuera años completos).

## 3. Los datos

**Dos pares de años de la EPC, con todas las preguntas del catálogo medidas en los dos años:**

| Par | Agentes | Preguntas |
|---|---|---|
| P1 | 200 encuestados de la **EPC 2023**, frente a la **EPC 2024** | 50 |
| P2 | 200 encuestados de la **EPC 2024**, frente a la **EPC 2025** | 31 |

**Cómo se arman los agentes:**
- con la regla y la semilla del panel de la página (`agentes.Agentes`);
- con todas sus respuestas del año base, incluida su propia respuesta del año base a cada pregunta objetivo, como en la página.

**La llamada:**
- la de la página: `openai/gpt-6-luna`, temperatura 1, razonamiento bajo, probabilidades por opción;
- las preguntas van en tandas de hasta 20 por llamada;
- después del perfil va la nota de `ACTUALIDAD_EPC`, con los años de cada par: «Las respuestas de arriba son de {año base}.
  Estas preguntas son de finales de {año objetivo}, casi un año después: la persona puede haber cambiado de opinión.»

**Los textos:** los del catálogo. Las de Galán, con el alcalde nombrado (`motor.GALAN_SOLO_AGENTES`), y la del Concejo, como en
`ACTUALIDAD_EPC`.

**Lo que se cuenta:** el lado de la escala que muestra la página (`motor.lado`), sin «no sabe», con el peso. Es lo mismo que en
`persistencia_epc.py`.

## 4. Los métodos

| | Método |
|---|---|
| **P** | persistencia: el dato del año base |
| **G** | agentes |
| **C** | P + λ·(G − P), con un solo λ |
| **Cd** | lo mismo, con un λ para gobierno e instituciones y otro para lo demás |

**Cómo se elige λ:** en la rejilla 0; 0,05; …; 1, el que minimiza el error medio **en el otro par**. Se ajusta en P1 y se evalúa
en P2, y al revés: ningún λ se evalúa en los datos con que se eligió.

## 5. Lo que se declara antes de correr

- **Lo real ya se vio en parte:** la Fase A imprimió el error medio de la persistencia por par y por dominio, y los ocho cambios
  más grandes. Es la vara, no el método que se prueba.
- **Los agentes de P2 ya se vieron en 7 preguntas** (`ACTUALIDAD_EPC`, brazo A): quedaron peor que la persistencia. Aquí van con
  otra tanda de preguntas en la llamada, así que no son las mismas cifras.
- **El perfil de 2023 trae 79 preguntas y el de 2024, 55.** La EPC cambió de cuestionario.
- **Algunas preguntas cambiaron de redacción entre años**, y el catálogo las trata como la misma. Eso afecta a todos los métodos
  por igual.

## 6. Reglas (escritas antes de llamar)

**C pasa si se cumplen las tres:**
- **RS1:** su error medio es **menor que el de P en los dos pares**, cada uno evaluado con el λ del otro.
- **RS2, que no dependa de una o dos preguntas:** juntando los dos pares, sigue siendo menor que P sin las dos preguntas en que C
  más le gana a P.
- **RS3, que no empeore lo político:** en gobierno e instituciones, juntando los dos pares, su error no supera el de P en más de
  0,5 puntos.

**Cd** se juzga con las mismas tres. **G contra P** se reporta por dominio, sin regla.

**Si C o Cd pasan,** su λ (ajustado con los dos pares) se propone para la página en las preguntas ya medidas. **Si no,** con dato
medido se muestra el dato, y los agentes quedan para lo que no tiene dato.

## 7. Predicciones

- **PS1.** El λ elegido es 0,2 o menos en los dos ajustes.
- **PS2.** C no pasa: o no cumple RS1, o gana por menos de 0,3 puntos.
- **PS3.** G se equivoca más que P en todos los dominios con 5 preguntas o más.

## 8. Gasto y código

- **Gasto:** P1 son 3 llamadas por agente y P2 son 2: 1.000 llamadas, unos USD 0,70, con tope de USD 2.
- **Al modelo** van los perfiles de la EPC 2023 y 2024 (pública, anónima), las preguntas y la nota.
- **Código:** `src/evaluacion/selector_fase_b.py`, con su prueba. Resultados en `SELECTOR_FASE_B_RESULTS.md`; las cifras por
  pregunta, en `data/processed/benchmark/selector_fase_b.csv`.

## Enmienda 1 (19/10/2026, antes de llamar al modelo): tope de USD 1

Daniel pidió correrla con tope de USD 1, en vez de 2. Nada más cambia. Si se llega al tope antes de terminar, la corrida se
detiene, lo respondido queda en la caché y se reporta como incompleta: no se evalúa con una parte de las preguntas.
