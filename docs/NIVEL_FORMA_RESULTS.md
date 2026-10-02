# NIVEL POR LA FORMA DE LA PREGUNTA — resultados (alternativa 1, sin API)

Corrido el **2 de octubre de 2026** contra `NIVEL_FORMA_SPECIFICATION.md` (pre-registro en
`62ac35a`, código en `b618972`, antes de correr). Sin gasto.
`python src/experiments/nivel_forma.py` → `data/processed/banco/nivel_forma.json`.

## 1. Resultado

96 preguntas de práctica, 29 familias. Error absoluto medio (EAM) del porcentaje favorable, cada
pregunta predicha sin su familia:

| | EAM (puntos) |
|---|---|
| R0 — promedio (parte A) | 23,0 |
| R2 — vecinos por texto (parte A) | 22,0 |
| **Modelo con la forma de la pregunta (F1-F4)** | **22,3** |
| umbral para «sirve» (0,8 × R0) | 18,4 |

Secundarias:
- Solo con la fracción favorable (F1): 22,6.
- Quitando cada rasgo: sin F1, 24,1; sin F2, 21,1; sin F3, 24,9; sin F4, 21,7.
- Dejando fuera solo la pregunta (con sus hermanas dentro): 16,2.

Coeficientes con las 96, en puntos:
- F1: +108,8. Pasar de 1 de 5 opciones favorables a 2 de 5 sube ~22 puntos.
- Tipo, frente a «otro»: corrupción +38,2; imagen +30,8; satisfacción +29,1; acuerdo +22,8;
  confianza +4,7.
- Bogotá: +3,3. «No conoce» válido: +0,5.

Tipos asignados: confianza 26, acuerdo 19, corrupción 16, imagen 14, otro 12, satisfacción 9.

## 2. Contra el pre-registro

| | predicción | resultado | |
|---|---|---|---|
| P1 | solo F1, EAM < 23,0 | 22,6 | se cumple (por poco) |
| P2 | modelo completo < 22,0 | 22,3 | **falla** |
| P3 | modelo completo ≤ 18,4 | 22,3 | **falla** |
| P4 | coeficiente de F1 positivo | +108,8 | se cumple |

**Regla (§7): no llega a 18,4.** La forma de la pregunta tampoco explica el nivel lo bastante. Lo
que queda es más datos (camino 3) o la prueba con un modelo de lenguaje más fuerte, que decide
Daniel.

## 3. Qué quiere decir

- **La forma sí mueve el nivel:** con más opciones favorables, el porcentaje sube (F1), y el tipo
  de pregunta pesa. Pero ajustado con todas las preguntas, eso no se traslada a familias que el
  modelo no vio: con 29 familias, lo que aprende de unas no sirve para otras.
- **El patrón de las tres pruebas de hoy es el mismo:** cuando la pregunta tiene hermanas de la
  misma serie en el banco, el error baja a ~16 puntos (vecinos por texto, 16,1; este modelo,
  16,2). Sin hermanas, todo queda en 22-23, que es suponer el promedio. **Lo que acerca el nivel es
  tener medida una pregunta casi igual, no un mejor método.**

## 4. Límites

1. 29 familias son pocos casos para cualquier modelo.
2. El tipo sale de una expresión regular sobre el texto. Es grueso: «¿qué tanto confía en la
   corrupción…?» es corrupción por el orden pre-registrado.
3. Solo práctica. Las 51 guardadas no se tocaron.

## 5. Incidencia al correr

La primera corrida calculó todo y falló al guardar el JSON (un `bool` de numpy en P4). Se corrigió
la conversión y se volvió a correr. Las cifras son idénticas, porque el cálculo no tiene azar.
