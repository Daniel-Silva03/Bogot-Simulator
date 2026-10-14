# PRECISIÓN POR GRUPOS — resultados

Corrido el **14 de octubre de 2026** contra `GRUPOS_2025_SPECIFICATION.md` (pre-registro y código en `22adbff`, antes de
calcular). **Gasto: USD 0.**
- **Control:** el error de la ciudad en estas 35 preguntas es 4,43, el mismo de `PESO_ANIO_RECIENTE`.
- **Las cifras por pregunta y grupo** están en `data/processed/grupos_2025/`.

## 1. Resultado

**35 preguntas × 10 grupos = 350 pares.** Error en la escala de 0 a 100.

| | E_grupo (la página por grupo) | E_ciudad (la cifra de la ciudad para todos) | Correlación de las brechas | Encuestados 2025 por grupo (mediana) |
|---|---|---|---|---|
| **Total** | **4,73** | **4,82** | **0,58** | — |
| Estrato | 5,11 | 5,06 | 0,50 | 488 |
| Edad | 4,62 | 4,78 | 0,61 | 274 |
| Sexo | 4,46 | 4,55 | 0,82 | 746 |

| | Criterio | Resultado | |
|---|---|---|---|
| R1 | E_grupo al menos 0,5 menor que E_ciudad | 0,09 menor | **no se cumple** |
| R2 | correlación de las brechas ≥ 0,5 | 0,58 | se cumple |

**No se cumplen las dos: por la regla, las cifras por grupo no aportan sobre la de la ciudad.**

| | Predicción | Resultado | |
|---|---|---|---|
| PG1 | Se cumplen las dos | solo R2 | **falla** |
| PG2 | Lo que mejor ve es el estrato, y lo que peor, el sexo | al revés: sexo 0,82, estrato 0,50 | **falla** |
| PG3 | E_grupo entre 5 y 8 | 4,73 | **falla** |

## 2. Control no pre-registrado: el tamaño de las brechas

**Se calculó después de ver §1 y no decide nada.** La brecha es cuánto se aparta cada grupo de la cifra de la ciudad.

| | Brecha real media | Brecha de la página | Error en la brecha | Mismo signo, cuando la brecha real pasa de 3 puntos |
|---|---|---|---|---|
| Total | 2,3 | 2,4 | 2,2 | 80 % (96 casos) |
| Edad | 2,3 | 2,3 | 2,1 | 91 % (46) |
| Estrato | 3,0 | 2,8 | 3,0 | 66 % (44) |
| Sexo | 1,5 | 1,7 | 1,0 | 6 de 6 |

## 3. Qué se aprende

1. **En Bogotá, los grupos se parecen mucho entre sí en estas preguntas.** En promedio, un grupo se aparta 2,3 puntos de la
   ciudad, mientras que el error de nivel de la ciudad es de 4,4. Aunque la página acertara las brechas a la perfección, el
   error por grupo bajaría poco. Por eso R1 no se cumple: es una regla difícil de pasar cuando las brechas son menores que el
   error de nivel.
2. **La página sí ve quién está más de acuerdo.**
   - **Edad:** cuando un grupo se aparta más de 3 puntos, la página acierta hacia qué lado en el 91 %.
   - **Sexo:** 6 de 6.
   - **Estrato:** el más débil, 66 %. Contra lo que predije, es donde peor le va, aunque es la dimensión con brechas más
     grandes.
3. **Lo que no hay que hacer:** leer las diferencias pequeñas entre grupos como hallazgos. Una brecha de 2 puntos está dentro
   del error.

**Para el marco de Artificial Societies:** en su benchmark, la medida de subgrupos es la distancia entre distribuciones. Aquí
la conclusión equivalente es esta: la página acierta la dirección de las diferencias entre grupos, en edad y sexo sobre todo,
pero en Bogotá esas diferencias son chicas comparadas con cuánto cambia la ciudad de un año a otro.
