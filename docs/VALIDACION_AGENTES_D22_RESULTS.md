# SEGUNDA VALIDACIÓN DE D22: LOS AGENTES CON PREGUNTAS POLÍTICAS QUE NUNCA SE USARON — resultados

Corrido el **19 de octubre de 2026** contra `VALIDACION_AGENTES_D22_SPECIFICATION.md` (pre-registro y código en `dcb60cf`,
antes de llamar al modelo y de calcular los reales). **Gasto: USD 0,383** por 1.800 llamadas. Por D21, se reportan la cifra de
los agentes, el lado y los errores medios, no el real de cada pregunta.

## Lo que dijeron los agentes

| # | Pregunta | Agentes | Lado |
|---|---|---|---|
| J1 | Imagen positiva de Petro, enero | 39,1 | acierta |
| J2 | comienzos de 2026 | 38,1 | **falla** |
| J3 | marzo-abril | 40,6 | **falla** |
| J4 | finales de abril | 39,3 | **falla** |
| J5 | mayo | 38,7 | acierta |
| H1 | Habló de política ayer, comienzos de 2026 | 25,3 | acierta |
| H2 | marzo-abril | 25,9 | acierta |
| H3 | finales de abril | 26,1 | acierta |
| H4 | mayo | 26,6 | acierta |

Respondieron los 200 agentes en las nueve.

**Errores medios:**

| | Error |
|---|---|
| Las 9 | 12,2 |
| Imagen de Petro (5) | 14,8 |
| Habló de política (4) | 8,9 |
| Decir 50 % en las 9 | 9,1 |

## Reglas

| | Criterio | Resultado | |
|---|---|---|---|
| RV1 | error medio ≤ 10 | 12,2 | **no se cumple** |
| RV2 | menor que decir 50 % (9,1) | 12,2 | **no se cumple** |
| RV3 | lado correcto en ≥ 6 de 9 | 6 | se cumple |

**No pasa.** Los agentes siguen apagados con el modelo real (`AGENTES_CON_MODELO_REAL = False`, §7 del pre-registro).

## Predicciones

| | Predicción | Resultado | |
|---|---|---|---|
| PV1 | Pasan | no pasan | **falla** |
| PV2 | Las cinco de Petro a menos de 5 puntos entre sí | de 38,1 a 40,6 | se cumple |
| PV3 | Más error en «habló de política» que en Petro | 8,9 contra 14,8 | **falla** |

## Qué se aprende

1. **La imagen de Petro es donde fallan:** los agentes la ponen en unos 39 % todo el año. Se equivocan 14,8 en promedio, y en
   tres de las cinco fechas quedan del lado equivocado de la mitad. El real, en esas tres, queda por encima del 50 %.
2. **No siguen el tiempo:** las cinco cifras de Petro van de 38,1 a 40,6, aunque la fecha cambia en la pregunta. Lo mismo en
   «habló de política» (25 a 27). Responden con la persona de 2025, no con el momento.
3. **En conducta les fue mejor de lo esperado:** «habló de política ayer» queda a 8,9 y con el lado correcto en las cuatro.
4. **El perfil de la EPC no trae opiniones nacionales.** Las 40 preguntas del catálogo son de Bogotá: gestión local, servicios,
   seguridad. Para el presidente, el modelo tiene que adivinar desde el estrato, la edad y lo local, y se queda abajo.
5. **Lo que esto dice para la página:** las preguntas de Galán y las políticas nuevas siguen mostrando el aviso con el modelo
   real. Con lo que hay, los agentes no se ganaron mostrar cifras de opinión nacional. Para lo local (Galán) la evidencia es
   otra (`PERSONAS_POLITICA`, `GALAN_ACTUAL`), pero esta validación era la condición pre-registrada y no pasó.
