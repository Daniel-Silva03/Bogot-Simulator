# ¿ESTARÍA BOGOTÁ DE ACUERDO? — la redacción de la página y el estiramiento

Pre-registro escrito el **5 de octubre de 2026**, antes de correr nada. Tiene dos partes:
- **parte A:** con gasto, que Daniel aprueba aparte;
- **parte B:** sin gasto.

## 1. Por qué

Daniel probó en la página dos preguntas guardadas del lote 5 con resultado conocido. Las dos salieron «dividida» y en las dos el valor real
quedó fuera del rango.

| | Real | Página | Prueba del lote 5 (`NIVEL_ACUERDO_LOTE5_RESULTS.md`, B) |
|---|---|---|---|
| `EDP25_Ex408` (los delitos se juzgan con justicia) | 9,9 | 36,6, dividida | 26,6, «no» |
| `EDP25_Dx503` (la marca Bogotá) | 71,4 | 42,5, dividida | 47,2, dividida |

De ahí salen dos preguntas:
- **A. ¿Cuánto cambia la estimación por la reformulación de la página?** La prueba del lote 5 le dio a Sonnet el
  texto y la escala originales de la encuesta. La página le da la versión reformulada. En `Ex408`, con la
  reformulación, eligió 2 preguntas distintas de 5 y la estimación subió 10 puntos. La cifra que muestra la página
  (72 % de acierto del lado, 17 de 17 al decidir) se midió sin reformular.
- **B. ¿Sirve estirar la estimación hacia los extremos?** La media de las preguntas parecidas tiende al medio.

**Lo que ya se miró, y se declara.** Las predicciones de abajo están informadas por estos tres análisis,
hechos el 5/10 antes de escribir esto:
1. **En las 95 guardadas de la prueba del lote 5 (configuración B):**
   - el real cayó fuera de ±21,9 en 16 de 95;
   - con real extremo (menos de 25 o más de 65; 40 preguntas), el error promedio fue 16,3 y hubo 14 fuera del rango;
   - con real intermedio (55 preguntas), el error promedio fue 8,7.
2. **En las 92 de práctica con Sonnet (`nivel_acuerdo_sonnet.json`):**
   - la recta de mínimos cuadrados es real = 4,4 + 0,85 × S;
   - la desviación estándar de S es 17,1 y la del real, 21,7.
3. **Las dos consultas de Daniel** de la tabla de arriba.

Por eso **la parte B no es una validación independiente.** Las guardadas ya se usaron y el umbral de
«extremo» (25 y 65) se eligió después de verlas. Una mejora en B solo justificaría proponer una
validación con preguntas nuevas, que hoy no existen (las 95 guardadas de acuerdo o sí/no ya están usadas).
No justificaría cambiar la página.

## 2. Parte A — estabilidad ante la reformulación (con gasto)

**Objetivos:** las mismas 95 guardadas de la prueba del lote 5 (`nivel_acuerdo_lote5.objetivos()`).
**Candidatas:** las 109 de la página (`motor._candidatas_estimacion()`), que son la configuración B.

**El flujo es el de la página, paso por paso:**
1. **Reformulación:** `reformular.reformular(pregunta_pagina, catálogo, ...)` con el modelo de la página
   (`reformular.MODELO`), igual que `motor.reformular`.
2. **Si el alcance es `nueva`, estimación:** se usa `motor.Motor.estimar` sobre la pregunta y la escala
   reformuladas. Es la misma función que llama la página, con las mismas candidatas y el mismo modelo (`MODELO_ESTIMACION`).
3. **Si el alcance es `catalogo`, `fuera` o `invalida`,** la página no estima. Se cuenta, pero no entra a las medidas.

**Medidas, sobre las preguntas que quedan como `nueva`.** Cada medida se compara con la misma pregunta en la prueba del lote 5 (S original):
- **estabilidad:** el promedio de |S reformulada − S original| y el porcentaje con la misma llamada («sí», «no» o «dividida»);
- **rendimiento:**
  - error absoluto medio (EAM), acierto del lado, cuántas veces decide y acierto al decidir, con h = 21,9 fijo (`nivel_acuerdo_validacion.evaluar`);
  - lo mismo para la S original, sobre el mismo subconjunto;
- **cobertura:** el porcentaje con el real dentro de ±21,9, en total y en las extremas.

**Regla: la cifra de la página «se sostiene» si se cumplen las tres:**
1. EAM reformulada ≤ EAM original + 1,5;
2. acierto del lado reformulado ≥ acierto original − 5 puntos;
3. al decidir, acierta ≥ 90 % (si no decide nunca, esta condición no se cuenta).

**Qué se hace con el resultado:**
- **Si se sostiene:** el texto de la página no cambia, y se le agrega la estabilidad medida.
- **Si no se sostiene:** se propone a Daniel cambiar el texto de la página por las cifras medidas con la
  reformulación, que es lo que la página hace de verdad. Como siguiente prueba (otro pre-registro), se
  propone darle a Sonnet el texto que escribió la persona en lugar del reformulado.

**Predicciones:**
- **PA1.** El promedio de |S reformulada − S original| es ≥ 4 puntos.
- **PA2.** La llamada coincide en ≥ 80 % de las preguntas.
- **PA3.** El EAM con reformulación es mayor que el original.
- **PA4.** La regla **no** se cumple.
- **PA5.** ≥ 90 % de las 95 quedan como `nueva`.

**Gasto:**
- 95 reformulaciones (~USD 0,004) y hasta 95 estimaciones con Sonnet (~USD 0,024): **~USD 2,7, con tope de USD 3,50**.
- **Antes de correr,** una llamada de prueba de cada tipo, que cuenta dentro del tope. Su costo se le confirma a Daniel.
- **El código se detiene solo** si lo registrado en la caché llega al tope.
- **La caché** va en `data/processed/banco/cache_nivel_redaccion.json`, que no se sube.

## 3. Parte B — estirar o encoger la estimación (sin gasto)

**Datos, todos ya guardados; no hay llamadas nuevas:**
- **práctica:** las 92 estimaciones de Sonnet de `nivel_acuerdo_sonnet.json`, sin fallos. Cada una se
  hizo sin ver su familia;
- **guardadas:** las 95 estimaciones B de `nivel_acuerdo_lote5.json`, sin fallos.

**Métodos.** S es la media real de las elegidas, lo que usa hoy la página. Los parámetros salen solo de la práctica:
- **S:** sin cambios.
- **E1, estirar:** S′ = m + (dₜ / dₛ)(S − m). Aquí m es la media de S en la práctica, y dₜ y dₛ son las desviaciones estándar
  del real y de S en la práctica. Iguala la dispersión de la estimación a la del real.
- **E2, recta:** S′ = a + b·S, por mínimos cuadrados en la práctica.
- **En todos:** S′ se recorta a [0, 100], y h es el cuantil 80 % de |S′ − real| en la práctica. Es la regla con
  que se fijó el 21,9, que es exactamente el h de S.

**Dónde se evalúa:**
- **práctica, por validación cruzada:** dejando fuera una familia a la vez. Los parámetros y h salen de las otras familias.
- **guardadas:** con los parámetros y h de toda la práctica.
- **Advertencia:** la práctica se estimó con las 92 candidatas (A) y las guardadas con 109 (B). Se declara, no se corrige.

**Medidas en cada lugar:**
- EAM, acierto del lado, cuántas veces decide y acierto al decidir;
- cobertura (real dentro de ±h) en total, en las extremas (real < 25 o > 65) y en las intermedias.

**Reglas:**
- **E1 se propone para validar con preguntas nuevas** solo si, en la práctica **y** en las guardadas, se cumplen las tres:
  1. EAM ≤ EAM de S + 0,5;
  2. cobertura en las extremas ≥ la de S + 10 puntos;
  3. acierto al decidir ≥ 90 %.
- **E2 se propone** solo si, en los dos lugares:
  1. EAM ≤ EAM de S − 0,5;
  2. el acierto del lado no baja;
  3. acierto al decidir ≥ 90 %.
- **En ningún caso cambia la página** con esta parte sola (§1).

**Predicciones:**
- **PB1.** E1 no se propone: su EAM sube más de 0,5 en algún lugar.
- **PB2.** E1 sube la cobertura en las extremas y la baja en las intermedias.
- **PB3.** E2 no se propone: su mejora de EAM es menor que 0,5 en algún lugar.
- **PB4.** S sigue siendo la mejor opción disponible, y lo que falta es información, no una corrección
  (como en `TECHO_GRUPOS_RESULTS.md`).

## 4. Código y orden

- **El código** va en `src/experiments/nivel_acuerdo_redaccion.py`, con prueba simulada en `tests/test_nivel_acuerdo_redaccion.py`.
- **El orden:**
  1. se sube este pre-registro;
  2. se corre la parte B (`--estirar`, sin gasto);
  3. con el sí de Daniel, la llamada de prueba de la parte A y, después, la corrida.
- **Los resultados** van a `NIVEL_ACUERDO_REDACCION_RESULTS.md`, contra este pre-registro.

## 5. Enmienda 1 (5/10/2026, después de la primera corrida de la parte A y antes de evaluarla)

La primera corrida de la parte A terminó sin cumplir el diseño. La cuenta de OpenRouter se quedó sin saldo
(HTTP 402) más o menos a la mitad; la estimación de la página atrapaba cualquier error, así que 37 preguntas
quedaron sin estimar sin avisar. Además, 1 pregunta perdió su estimación porque Sonnet se corrigió dentro
de la misma respuesta y la lectura no lo aceptó. Gasto: USD 1,51. Se vieron cifras parciales de 46 preguntas
(se declara: EAM 16,0 con reformulación contra 12,8 original). **No se evalúan contra la regla.**

Cambios, pedidos por Daniel:
1. **Lectura de las respuestas** (`nivel_parecidas_b` DI-NB6): si hay varios JSON, vale el último con ids
   válidos.
   - Se aplica igual a las dos columnas.
   - En la caché de la prueba del lote 5, de donde sale la S original, no cambia ninguna de las 116 respuestas,
     así que la columna original queda igual.
2. **Errores del servicio** (`motor` DI-CO24): un error de red o de HTTP ya no se convierte en «sin estimación».
   Detiene la corrida (DI-NR4).
3. **La corrida se retoma desde la caché** cuando haya saldo. Lo pagado no se vuelve a pedir.
4. **Si alguna pregunta queda como `nueva` sin estimación** porque el modelo no dio ids válidos (DI-CO20, igual que en la
   página), se cuenta y se deja fuera de las dos columnas.
   - En las 95 ya no puede quedar ninguna sin estimar por error del servicio.

Las medidas, la regla, las predicciones y el tope (USD 3,50 en total, contado lo ya gastado) no cambian.
