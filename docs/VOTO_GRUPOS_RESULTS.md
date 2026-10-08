# INTENCIÓN DE VOTO SIMULADA POR GRUPOS — resultados

Corrido el **8 de octubre de 2026** contra `VOTO_GRUPOS_SPECIFICATION.md` (pre-registro y código en `809920d`, antes de
calcular). **Gasto: USD 0.** Solo cifras de error y acierto, sin porcentajes de ningún candidato ni grupo (D21).

## 1. Contra la regla (las 215 guardadas)

| Corte | Pares (base mediana) | EAM grupos | EAM poniendo el total | Proporción | Diferencias claras | Sentido | Rango (h) | Cobertura | Se muestra |
|---|---|---|---|---|---|---|---|---|---|
| Sexo | 430 (172) | 4,0 | 4,3 | 0,93 | 27 | 85 % | ±8,2 | 83 % | **no** (R1) |
| Estrato | 645 (115) | 5,0 | 5,4 | 0,93 | 77 | 96 % | ±8,9 | 83 % | **no** (R1) |
| Edad | 612 (102) | 4,8 | 6,2 | **0,77** | 71 | 93 % | ±9,5 | 85 % | **sí** |

- **R1:** la proporción debe ser ≤ 0,9.
- **R2:** al menos 10 diferencias claras, y el sentido acertado en ≥ 80 %. Los tres cortes cumplen R2.

**Por la regla (§4), solo la edad entra a la página,** con ±9,5.

| | Predicción | Resultado | |
|---|---|---|---|
| PG1 | Estrato se muestra | no se muestra | **falla** |
| PG2 | Sexo no se muestra | no se muestra | se cumple |
| PG3 | Edad se muestra | se muestra | se cumple |

**En la práctica** (158), donde se fijó h, la edad también es la que más mejora: 5,9 contra 7,6.

## 2. Qué se aprende

- **La edad sí separa,** y el simulador lo capta: los grupos se equivocan un 23 % menos que el total, y aciertan hacia dónde
  va la diferencia entre jóvenes y mayores en 66 de 71 preguntas.
- **El estrato acierta el sentido** en 74 de 77 diferencias claras, la mejor marca de los tres, **pero no pasa R1** por poco:
  0,93 contra 0,9. Una explicación posible, sin comprobar: muchas preguntas son de candidatos pequeños, donde todos los
  estratos están cerca del total, y eso diluye la ventaja en el promedio. La regla no se cambia después de ver el
  resultado. Si se quiere mostrar el estrato, va con un pre-registro nuevo, por ejemplo, con el sentido de la diferencia
  como criterio principal y preguntas que no sean estas 215.
- **El sexo no aporta:** hombres y mujeres votan parecido en Bogotá, y hay pocas diferencias claras (27).
