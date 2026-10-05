# ¿ESTARÍA BOGOTÁ DE ACUERDO? — paso 2, Claude Sonnet eligiendo preguntas parecidas

Pre-registro escrito el **5 de octubre de 2026**, antes de hacer ninguna llamada. Hay gasto: **~USD 2,
con tope de USD 3**, aprobado por Daniel («solo Sonnet»).

## 1. Pregunta

En el paso 1 (`NIVEL_ACUERDO_RESULTS.md`), el mejor método para las preguntas de acuerdo o de sí/no fue
**elegir preguntas parecidas** (por texto): 63 % de acierto en el lado de la mayoría y 18,2 puntos de
error, sin llegar a la regla. En la parte B (`NIVEL_PARECIDAS_B_RESULTS.md`), Claude Sonnet 5.5 fue el
mejor eligiendo parecidas. **¿Llega Sonnet a la regla en este subconjunto?**

## 2. Datos y tarea

- **Las mismas 92 preguntas de práctica, en 25 familias**, de `nivel_acuerdo.tabla()`. Los guardados no
  se tocan.
- **La misma tarea, instrucciones y lectura de respuestas que la parte B** (`nivel_parecidas_b`:
  `SISTEMA`, `prompt`, `parsear`, el reintento y el fallo). El modelo recibe la pregunta nueva y, como
  candidatas, las otras preguntas de este subconjunto que **no** son de su familia, con su texto y su
  forma y **sin ningún resultado**. Elige de 1 a 5.
- **La predicción** es la media real de las elegidas. Si falla dos veces, se usa el promedio (M0) y
  cuenta como fallo.
- **Modelo:** `anthropic/claude-sonnet-5.5` en OpenRouter, a temperatura 0, una llamada por pregunta.
  La caché va en `data/processed/banco/cache_nivel_acuerdo.json`, que no se sube.

## 3. Medidas y regla (las del paso 1, §4 y §6)

- EAM; acierto del lado; llamada con rango del 80 % («sí», «no» o «dividida»), con h tomado de los
  errores de Sonnet en las otras familias.
- **Sirve para decir «sí o no» en la página** si:
  1. acierta el lado **≥ 67 %**: la referencia fija del paso 1 (57 %) más 10 puntos;
  2. su EAM es **≤ 15,8**: 0,8 × 19,7, el de M0 en el paso 1.
- **Si sirve:** se propone a Daniel validarlo, pre-registrado, en el guardado (20 familias), con su
  costo, antes de mostrar nada en la página.
- **Si no sirve:** la página sigue sin decir «sí» o «no», y lo que queda es el camino 3.

## 4. Predicciones (escritas antes de llamar)

- **P1.** Sonnet **no** cumple la regla.
- **P2.** Su EAM es menor que el de M1 (18,2).
- **P3.** Acierta el lado más que M1 (63 %).
- **P4.** Con el rango del 80 %, decide en menos del 30 % de las preguntas.

## 5. Gasto

92 llamadas (más reintentos, si los hay), a ~USD 0,022: **~USD 2**.
- **Antes de correr:** una llamada de prueba, que cuenta dentro del tope. Su costo se le confirma a
  Daniel antes de seguir.
- **El código se detiene solo** si lo registrado en esta caché llega a USD 3.

## 6. Código

`src/experiments/nivel_acuerdo_sonnet.py`, con pruebas de modelo simulado en
`tests/test_nivel_acuerdo_sonnet.py`. Los resultados van a `NIVEL_ACUERDO_SONNET_RESULTS.md`, contra
este pre-registro.
