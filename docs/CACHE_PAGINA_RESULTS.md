# LA CACHÉ EN LA PÁGINA — resultados

Corrido el **7 de octubre de 2026** contra `CACHE_PAGINA_SPECIFICATION.md` (pre-registro y código en `47de465`, antes de
llamar).
- **Comando:** `python src/experiments/cache_pagina.py`.
- **Gasto:** USD 0,046 en 129 llamadas, más USD 0,002 de la prueba, dentro del tope de USD 0,30.
- **Solo cifras de error y costo,** sin porcentajes de las encuestas del CNC.

## 1. Resultado

| En las 129 guardadas | Orden nuevo, con caché | Orden de siempre (la página hoy) | Regla |
|---|---|---|---|
| EAM | 15,2 | 14,8 | ≤ 14,8 + 0,5: **cumple** |
| Acierto del lado | 73 % | 71 % | ≥ 71 % − 5: **cumple** |
| Decide («probablemente») | 15 | 11 | |
| Acierta al decidir | **13 de 15 (87 %)** | 10 de 11 (91 %) | ≥ 90 %: **no cumple** |
| Misma llamada que el orden de siempre | 94 % | | |
| Costo por llamada | **USD 0,00035** | USD 0,00129 | |

**Por la regla (§3), la página sigue con el orden de siempre, sin caché.** Las dos primeras condiciones se cumplen. La tercera
falla: con el orden nuevo dice «probablemente» más veces (15 contra 11) y se equivoca en 2 de ellas, las dos al decir
«probablemente sí».

| | Predicción | Resultado | |
|---|---|---|---|
| PC1 | Se cumple la regla | no se cumple (al decidir, 87 %) | **falla** |
| PC2 | La llamada coincide en ≥ 85 % | 94 % | se cumple |
| PC3 | Costo por llamada ≤ 30 % del de siempre | 27 % | se cumple |

## 2. Lectura

- **La caché funciona en la página:** cada estimación cuesta un 73 % menos.
- **La estimación cambia poco con el orden:** coincide en el 94 % de las llamadas, el error sube 0,4 y el lado sube 2 puntos.
- **Lo que falla:** decide más veces y acierta menos al hacerlo, por 2 preguntas de 15. Con tan pocas decisiones, la
  diferencia puede ser azar. Pero la regla se escribió antes, y no se mueve.
- **Para cambiarlo de todos modos,** como con D20, sería una decisión de proyecto (costo contra acierto al decidir), no un
  «pasó».
