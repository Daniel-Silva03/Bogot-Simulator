# RANGO VARIABLE EN LA ESTIMACIÓN DE OPINIÓN — resultados

Corrido el **8 de octubre de 2026** contra `RANGO_VARIABLE_SPECIFICATION.md` (pre-registro y código en `4ac7c8c`, antes de
calcular). **Gasto: USD 0.** Las 92 elecciones de la práctica salieron de la caché de Luna, y las de las 129 guardadas,
de la salida del lote 6.

**Controles (§2):** F0 reproduce el ±23,4 en la práctica y las 11 decisiones con 10 aciertos en las 129.

## 1. La forma elegida con la práctica

| | F0, fijo | **F1, por cantidad** | F2, por dispersión | F3, por recorrido |
|---|---|---|---|---|
| Ancho medio en la práctica | 23,4 | **22,5** | 25,6 | 22,9 |

**F1 es la más estrecha,** y F0 queda a más de 0,5 puntos. Su calibración: ±23,9 con una elegida, ±22,9 con dos y ±21,7
con tres o más.

## 2. Las 129 guardadas, contra la regla

| | F0, fijo (hoy) | **F1 (elegida)** | F2 | F3 |
|---|---|---|---|---|
| Ancho medio | 23,4 | **22,3** | 25,7 | 23,5 |
| Cobertura | 81 % | **79 %** | 84 % | 75 % |
| Decide | 11 | **13** | 24 | 40 |
| Acierta al decidir | 10 (91 %) | **12 (92 %)** | 23 (96 %) | 34 (85 %) |

| | Criterio | Resultado | |
|---|---|---|---|
| R1 | La forma no es F0 | F1 | se cumple |
| R2 | Cobertura ≥ 75 % | 79 % | se cumple |
| R3 | Decide en más de 11 | 13 | se cumple |
| R4 | Al decidir, ≥ 90 % | 92 % | se cumple |

**Por la regla (§4), F1 entra a la página** (`motor.py`, DI-CO33). Con el redondeo a un decimal da lo mismo: 13 y 12.

| | Predicción | Resultado | |
|---|---|---|---|
| PA1 | La elegida es F2 o F3 | F1 | **falla** |
| PA2 | Cumple la regla | la cumple | se cumple |
| PA3 | Decide en 20 o más | 13 | **falla** |
| PA4 | Dispersión y error van juntos en la práctica | Spearman 0,00 | **falla** |

## 3. Qué se aprende

- **La mejora es chica:** dos decisiones más, las dos acertadas. La página sigue diciendo «dividida» en 9 de cada 10.
- **La idea de fondo no se sostuvo.** Que las preguntas que elige Luna coincidan entre sí no predice el error: en la
  práctica, la correlación es 0,00. El error de la estimación viene sobre todo de que las elegidas, aunque parecidas, no
  son la pregunta, y eso no se ve en su dispersión.
- **F2 decide 24 veces en las guardadas, con 23 aciertos.** Se vio después y no cuenta: en la práctica, F2 era la más ancha,
  y elegirla ahora sería escoger mirando el resultado. Si se quiere probar, va con un pre-registro nuevo y preguntas que no
  sean estas 129.
- **Para decidir más de verdad,** el rango no basta. Haría falta una estimación más precisa: mejores candidatas, o preguntas
  medidas más cercanas a las que la gente escribe.
