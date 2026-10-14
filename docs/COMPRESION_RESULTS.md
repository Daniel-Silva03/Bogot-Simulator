# COMPRESIÓN HACIA EL MEDIO — resultados

Corrido el **14 de octubre de 2026** contra `COMPRESION_SPECIFICATION.md` (pre-registro y código en `f86e115`, antes de
calcular). **Gasto: USD 0.**

**Un arreglo del código antes del primer cálculo:** la evaluación pedía la fuente de cada pregunta, y el código le pasaba
una tabla sin ella. Falló sin calcular nada. Se le pasaron los objetivos completos (`nivel_acuerdo_lote8.objetivos`). Nada
del diseño cambió.

Solo hay cifras agregadas (D21).

## 1. Resultado

**La compresión:**

| | Estimaciones | Reales |
|---|---|---|
| Desviación estándar | 16,5 | 23,9 |
| Pendiente del real sobre la estimación | 0,95 | |
| Intercepto | 7,5 | |

**La corrección, fuera de muestra:**

| En las 139 | Hoy (rango ±23,4) | Estirada (rango ±22,3) |
|---|---|---|
| Error (EAM) | **15,3** | 15,6 |
| Acierto del lado | 73 % | 73 % |
| Decide | 14 (10 %) | 20 (14 %) |
| Acierta al decidir | 13 de 14 | 18 de 20 (90 %) |

**Prueba externa (errores medios):**

| | Hoy | Estirada |
|---|---|---|
| Las 5 públicas de 2026 sin V5 | 19,9 | 17,3 |
| V5 (está en el banco) | 1,2 | 3,8 |
| Las 7 del CNC de 2026 | 12,7 | 13,0 |

| | Criterio | Resultado | |
|---|---|---|---|
| 1 | error fuera de muestra al menos 0,5 menor | 15,6 contra 15,3: sube | **no se cumple** |
| 2 | el acierto del lado no baja | 73 % y 73 % | se cumple |
| 3 | al decidir, ≥ 90 % | 18 de 20 | se cumple |
| 4 | en las 5 públicas de 2026, el error no sube | baja de 19,9 a 17,3 | se cumple |

**No se cumple la regla: la página no estira la estimación.**

| | Predicción | Resultado | |
|---|---|---|---|
| PC1 | Está aplanada: menos dispersión y pendiente > 1 | menos dispersión, pero pendiente 0,95 | **falla** |
| PC2 | Estirar baja el error menos de 1 punto | lo sube 0,3 | se cumple |
| PC3 | La estirada decide en más preguntas | 20 contra 14 | se cumple |
| PC4 | No se cumple la regla | no se cumple | se cumple |

## 2. Qué se aprende

**El defecto no es una escala aplanada que se pueda estirar: es falta de información.**
- **Hay menos dispersión:** las estimaciones se mueven menos que los reales (16,5 contra 23,9).
- **Pero la pendiente es 0,95, casi 1.** Si la estimación fuera la verdad encogida hacia el 50 %, la pendiente pasaría
  de 1 y estirar la corregiría. Con una pendiente de 1, la estimación está bien calibrada en promedio: cuando dice 40, el
  real anda en promedio por 40.
- **Lo que le falta** es la variación que no puede ver: la parte de cada pregunta que ninguna pregunta medida anticipa.
  Ningún ajuste lineal recupera eso.

**El intercepto de 7,5 con pendiente 0,95** quiere decir que la estimación queda unos 5 puntos por debajo de lo real, en
promedio. Por eso mejora un poco en las preguntas del metro. Pero en las 139 no alcanza para bajar el error.

**Para el marco de Artificial Societies,** el resultado es útil: nuestra estimación no tiene el sesgo de escala que ellos
encontraron en los modelos de lenguaje. Tiene el límite de no saber lo que no se ha medido.
