# NIVEL POR PREGUNTAS PARECIDAS — parte A, sin API

Pre-registro escrito el **2 de octubre de 2026**, antes de calcular nada. Sin gasto.
Es el «camino 2» que se le propuso a Daniel tras `TECHO_GRUPOS_RESULTS.md`.

## 1. Pregunta

Para una pregunta nueva, ¿se puede estimar **cuántos estarían de acuerdo** (el porcentaje
favorable de la ciudad) mirando el resultado real de **preguntas parecidas que sí se midieron**?

El nivel que proponía el modelo se quitó de la página (D18): dio 3,7 al metro y al Corredor Verde.
Esta parte A mide qué tan bien lo hace, **sin API**:
- una referencia ingenua;
- dos formas gratuitas de buscar preguntas parecidas.

La que salga mejor es la vara que tendrá que superar la parte B, con el modelo, que se
pre-registrará aparte.

## 2. Datos

Las preguntas de práctica del banco con resultado real y sin exclusión de estructura (DI-BR5), con
su porcentaje favorable de la ciudad (`total`, DI-BR1 y DI-BA3) en
`data/processed/banco/reales_practica.json`. Se esperan unas **96**. **Las 51 guardadas no se
tocan.** No se ha mirado la dispersión de esos porcentajes para escribir este documento.

## 3. Métodos (todos sin API)

**Regla común: cada pregunta se predice sin usar ninguna pregunta de su propia familia** (`familia`
del banco: preguntas hermanas de una misma serie). Si no, «confianza en la Policía» se predeciría
con «confianza en el Ejército» del mismo cuestionario, y eso no se parece a lo que pasa con una
pregunta de verdad nueva.

- **R0 — promedio:** la media de `total` de las preguntas de las otras familias.
- **R1 — mismo tema:** la media de las preguntas de otras familias con el mismo `tema` del banco;
  si no hay ninguna, R0.
- **R2 — vecinos por texto:** las **5** preguntas de otras familias cuyo `pregunta_pagina` más se
  parece, con similitud coseno de TF-IDF de n-gramas de caracteres de 3 a 5 (`char_wb`, en
  minúsculas y sin tildes). La predicción es la media de sus `total`.

## 4. Medida

**Error absoluto medio (EAM), en puntos porcentuales**, sobre todas las preguntas. Como
secundarias, sin peso en la decisión:
- la fracción de preguntas con error ≤ 10 puntos;
- R2 con k = 3 y k = 10;
- R2 dejando fuera solo la propia pregunta y no su familia, para medir cuánto ayudan las hermanas.

## 5. Predicciones (escritas antes de calcular)

- **P1.** El EAM de R0 está entre 12 y 20 puntos.
- **P2.** R1 tiene menor EAM que R0.
- **P3.** R2 **no** baja el EAM de R0 en un 20 % o más.
- **P4.** R2 sin dejar fuera la familia tiene menor EAM que R2 con la familia fuera.

## 6. Regla de decisión (escrita antes de calcular)

- **La vara de la parte B** es el menor EAM entre R0, R1 y R2. La parte B (el modelo elige las
  preguntas parecidas y se promedia su resultado real) tendrá que bajarlo **un 20 % o más** en la
  práctica, y después repetirlo en el banco guardado. Eso se pre-registrará antes de gastar.
- **Si R1 o R2 baja el EAM de R0 un 20 % o más,** existe un método gratuito que acerca el nivel.
  Se propone a Daniel llevarlo al banco guardado (pre-registrado) antes de pensar en la página.
- **Si ninguno lo baja un 20 %,** buscar preguntas parecidas sin el modelo no acerca el nivel más que
  el promedio, y la parte B tiene que superar al promedio.

## 7. Código

`src/experiments/nivel_parecidas.py`, con pruebas de datos inventados en
`tests/test_nivel_parecidas.py`. Los resultados van a `NIVEL_PARECIDAS_RESULTS.md`, contra este
pre-registro.
