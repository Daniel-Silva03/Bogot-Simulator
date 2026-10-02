# NIVEL POR LA FORMA DE LA PREGUNTA — alternativa 1, sin API

Pre-registro escrito el **2 de octubre de 2026**, antes de calcular nada. Sin gasto.
Sigue a `NIVEL_PARECIDAS_RESULTS.md`: ni el tema ni el parecido del texto acercan el nivel.

## 1. Pregunta

¿El porcentaje favorable de una pregunta depende más de **cómo está hecha** que de su tema?
- cuántas opciones cuentan como favorables;
- si «no conoce» es una respuesta válida;
- si pregunta por confianza, imagen, satisfacción o acuerdo;
- si es sobre Bogotá.

Si es así, un modelo pequeño con esos rasgos estimaría el nivel de una pregunta nueva mejor que el
promedio, sin API.

## 2. Datos

Las mismas **96 preguntas de práctica (29 familias)** de la parte A, con su `total`. **Las 51
guardadas no se tocan.** Los rasgos salen solo de la estructura de cada pregunta (categorías,
códigos favorables y texto), que se revisó para escribir este documento; los resultados, no.
Observación al revisarla: el campo `tema` del banco es casi único (85 temas para 96 preguntas),
lo que explica por qué «mismo tema» no ayudó.

## 3. Rasgos (definidos antes de calcular)

- **F1 — fracción favorable:** códigos favorables / códigos válidos (`banco_reales.validos`).
- **F2 — «no conoce» válido:** 1 si alguna categoría válida dice «no conoce» o «no lo conoce».
- **F3 — tipo,** por expresión regular sobre `pregunta_pagina`, en este orden (gana la primera):
  - `corrup` → corrupción;
  - `conf[ií]a` → confianza;
  - `imagen|favorable` → imagen;
  - `satisf` → satisfacción;
  - `acuerdo` → acuerdo;
  - lo demás → otro.

  Entra como variables indicadoras, con «otro» de base.
- **F4 — Bogotá:** 1 si `ambito` es «Bogotá».

## 4. Modelo y medida

Regresión lineal por mínimos cuadrados: `total ~ 1 + F1 + F2 + F3 + F4` (8 coeficientes), con la
solución de norma mínima si a una exclusión le falta un tipo. La predicción se recorta a [0, 100].

**Validación como en la parte A:** cada pregunta se predice con un modelo ajustado **sin su
familia**. La medida es el error absoluto medio (EAM) en puntos.

**Secundarias,** sin peso en la decisión:
- el modelo solo con F1;
- el modelo completo quitando cada rasgo por turno;
- dejando fuera solo la pregunta y no su familia;
- los coeficientes ajustados con las 96.

## 5. Referencias (de la parte A)

- Promedio (R0): 23,0.
- Vecinos por texto (R2): 22,0.
- Umbral de «método gratuito que sirve» (0,8 × R0): **18,4**.

## 6. Predicciones (escritas antes de calcular)

- **P1.** El modelo solo con F1 tiene EAM < 23,0.
- **P2.** El modelo completo tiene EAM < 22,0.
- **P3.** El modelo completo llega a 18,4 o menos.
- **P4.** Con las 96, el coeficiente de F1 es positivo.

## 7. Regla de decisión (escrita antes de calcular)

- **Si el modelo completo llega a 18,4 o menos:** la forma de la pregunta explica parte del nivel.
  Se propone a Daniel probarlo, pre-registrado, en el banco guardado. Si ahí también pasa, se
  discute cómo mostrarlo en la página (un rango, nunca una cifra sola).
- **Si no llega:** la forma tampoco explica el nivel lo bastante. Lo que queda es más datos
  (camino 3) o la prueba con un modelo de lenguaje más fuerte, que Daniel decide.

## 8. Código

`src/experiments/nivel_forma.py`, con pruebas de datos inventados en `tests/test_nivel_forma.py`.
Los resultados van a `NIVEL_FORMA_RESULTS.md`, contra este pre-registro.
