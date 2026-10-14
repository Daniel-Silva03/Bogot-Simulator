# VALIDACIÓN CNC 2026 — resultados

Corrido el **14 de octubre de 2026** contra `VALIDACION_CNC_2026_SPECIFICATION.md` (pre-registro y código en `3798769`,
antes de hacer las preguntas).
- **Gasto:** USD 0,031.
- **Lo que se reporta** (D21, §3 del pre-registro): por pregunta, lo que dio la página, si el real cae dentro del rango y si
  la llamada acertó; el error medio, solo de las siete juntas. **Ningún porcentaje de las encuestas del CNC.** Los reales
  están en `data/processed/validacion_cnc_2026/`, sin subir.

## 1. Resultado

| # | Pregunta | Página | Rango | Llamada | ¿Real dentro? | ¿Llamada acierta? |
|---|---|---|---|---|---|---|
| K1 | ¿Cree que Colombia está progresando? | 27,8 | 6,1 – 49,5 | **no** | sí | **sí** |
| K2 | ¿A usted personalmente el aumento del 23 % del salario mínimo lo beneficia? | 28,9 | 6,0 – 51,8 | dividida | **no** | — |
| K3 | ¿Se debe incrementar la exploración de petróleo en Colombia? | 37,6 | 15,9 – 59,3 | dividida | sí | — |
| K4 | ¿Se debe persistir en los diálogos de paz con los grupos armados? | 44,8 | 23,1 – 66,5 | dividida | sí | — |
| K5 | ¿Colombia debería tener un Estado más grande que haga más inversión social? | 50,7 | 29,0 – 72,4 | dividida | sí | — |
| K6 | ¿Colombia debe tener relaciones cercanas con Estados Unidos? | 36,9 | 15,2 – 58,6 | dividida | **no** | — |
| K7 | ¿El sistema de salud lo debe manejar solo el Estado? | 45,8 | 24,1 – 67,5 | dividida | sí | — |

Las siete fueron preguntas nuevas: ninguna fue a «fuera de alcance» ni al catálogo.

| | Criterio | Resultado | |
|---|---|---|---|
| R1 | dentro del rango en ≥ 5 de 7 | 5 | se cumple |
| R2 | al decidir, falla en 1 como máximo | decidió en 1 y acertó | se cumple |
| R3 | error medio menor que decir 50 % | 12,7 contra 10,6 | **no se cumple** |

**La página no pasa la validación CNC 2026.**

| | Predicción | Resultado | |
|---|---|---|---|
| PK1 | No pasa | no pasa | se cumple |
| PK2 | Al menos una va a «fuera» | ninguna | **falla** |
| PK3 | Dice «probablemente» en dos o menos | en una | se cumple |
| PK4 | Su error medio es menor que el de decir 50 % | 12,7 contra 10,6 | **falla** |

## 2. Qué se aprende

1. **El rango funciona mejor que la cifra.** El resultado real cayó dentro del rango en 5 de 7, y la única vez que se
   comprometió («probablemente no» en el progreso del país) acertó.
2. **La cifra central se equivoca más que decir 50 %.** Ese 10,6 es una vara exigente: estos siete resultados están, en
   promedio, a unos 11 puntos de la mitad. La página quedó a 12,7. En temas divididos, apostar por la mitad es difícil de
   superar.
3. **Los temas nacionales sí entran.** La reformulación no mandó ninguna a «fuera de alcance»: las tomó como preguntas de
   opinión de los bogotanos. Ahí falló PK2.
4. **Dos quedaron fuera del rango:** el salario mínimo y la relación con Estados Unidos. Las dos dependen de la coyuntura de
   2026: el aumento del 23 % y la política exterior. Ninguna pregunta medida del banco ni de la EPC habla de eso.

**En corto**, junto con la validación 2026 (`VALIDACION_2026_RESULTS.md`): con preguntas nuevas de 2026, la página casi nunca se
compromete. Cuando lo hace, acierta, y su rango contiene la cifra real en 8 de 13. Pero su cifra central no le gana a decir
50 % cuando los resultados reales están cerca de la mitad.
