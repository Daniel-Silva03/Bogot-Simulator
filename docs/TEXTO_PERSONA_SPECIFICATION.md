# ¿ESTIMAR CON EL TEXTO DE LA PERSONA O CON EL REFORMULADO?

Pre-registro escrito el **6 de octubre de 2026**, antes de hacer ninguna llamada. Gasto: **~USD 0,11, con tope de
USD 0,40**, aprobado por Daniel («pre-registra la prueba»). Para correr, falta su sí al costo de la llamada de prueba.

## 1. Pregunta

La página reformula la pregunta y le pasa la versión reformulada al modelo que estima. La parte A de
`NIVEL_ACUERDO_REDACCION` mostró que eso empeora la estimación (14,0 → 16,2 de error), sobre todo en las preguntas
extremas, porque la reformulación a veces cambia el sentido. Reformular con Luna no lo arregla (`LUNA_PAGINA_RESULTS.md`).

**¿Estima mejor la página si le da al modelo el texto que escribió la persona, con la escala que propone la
reformulación?**

## 2. Diseño

- **Objetivos:** las 90 de las 95 guardadas que la reformulación con Luna deja como `nueva` (`LUNA_PAGINA`, parte 2).
- **Brazo R, el de hoy:** la pregunta reformulada con Luna y su escala, estimada con `Motor.estimar` (Luna, h = 23,4). Ya
  está medido: EAM 16,7; lado 63 %; 3 de 4 al decidir. Se reutiliza desde la caché, sin llamadas.
- **Brazo T, el texto de la persona:** el texto de la pregunta tal como entró (`pregunta_pagina`), **con la escala de la
  reformulación**. En la página, la persona escribe sin escala.
  - Se estima con `Motor.estimar`: mismo modelo, mismas 109 candidatas y mismo h.
  - Las reformulaciones se leen de la caché de `LUNA_PAGINA`, sin llamadas nuevas.
- **Medidas:** EAM, acierto del lado, cuántas veces decide y acierto al decidir (`nivel_acuerdo_redaccion.medir`, h = 23,4).
  Se reporta además la cobertura, total y en extremas e intermedias.

## 3. Regla

**La página pasa a estimar con el texto de la persona si el brazo T cumple las tres condiciones:**
1. EAM de T ≤ EAM de R − 1,0;
2. acierto del lado de T ≥ el de R;
3. al decidir, T acierta ≥ 90 %. Si decide en menos de 5 preguntas, esta condición se reporta pero no cuenta.

**Si cumple:**
- se propone a Daniel el cambio en `motor.py` y `servidor.py`: la página manda al servidor el texto original junto con el
  reformulado;
- se corrige el texto de la página con las cifras de T.

**Si no cumple:** la página sigue igual y su texto ya cita lo medido (DI-CO27).

## 4. Límites, dichos antes

1. **El texto de la persona es, aquí, el de la encuesta.** En las 95 guardadas no hay una versión escrita por alguien en
   la página. El texto de una encuesta es más limpio y más parecido a las candidatas que lo que escribe cualquiera, así
   que T es el mejor caso.
   - **Si T no gana ni así,** el cambio no sirve.
   - **Si gana,** la ganancia real en la página será menor.
2. **Lo que ya se sabe.** Con el texto **y la escala** originales, Luna sacó 14,0 de error en las 84 de la parte A, contra 16,2
   con la reformulación de mimo. Este brazo T solo cambia la escala por la de la reformulación. Por eso se espera que T
   gane.
3. **Las 95 guardadas ya se usaron varias veces.**

## 5. Predicciones (escritas antes de llamar)

- **PT1.** El EAM de T es menor que el de R.
- **PT2.** T cumple la regla.
- **PT3.** T decide en más preguntas que R (más de 4).
- **PT4.** La mayor parte de la mejora está en las extremas: el EAM de las extremas baja más que el de las intermedias.

## 6. Gasto y código

- **Gasto:** ~90 estimaciones con Luna a ~USD 0,0012, unos **USD 0,11, con tope de USD 0,40**.
  - **Antes de correr,** una llamada de prueba.
  - **El código se detiene solo** al llegar al tope o si el servicio falla.
- **Código:** `src/experiments/texto_persona.py`, con su prueba simulada en `tests/test_texto_persona.py`.
- **Caché:** `data/processed/banco/cache_texto_persona.json`.
- **Resultados:** `TEXTO_PERSONA_RESULTS.md`, contra este pre-registro.
