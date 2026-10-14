# MAPA POR LOCALIDAD APOYADO EN LA CIUDAD — resultados

Corrido el **14 de octubre de 2026** contra `MAPA_ENCOGIDO_SPECIFICATION.md` (pre-registro y código en `e51ba82`, antes de
calcular). **Gasto: USD 0.** Control: el error de hoy reproduce el 7,94 de `PESO_ANIO_RECIENTE`.

## 1. Resultado

**35 preguntas × 18 localidades = 630 pares.**

| | Hoy | S1, hacia la ciudad | S2, hacia las parecidas por estrato |
|---|---|---|---|
| Error por localidad | 7,94 | 7,65 | 7,67 |
| Orden medio de las localidades (Spearman con 2025) | 0,045 | 0,043 | 0,038 |

| | R1: error ≤ 7,44 | R2: el orden no baja | |
|---|---|---|---|
| S1 | 7,65: no | 0,043: no | no pasa |
| S2 | 7,67: no | 0,038: no | no pasa |

**Ninguna pasa: el mapa sigue como está.**

| | Predicción | Resultado | |
|---|---|---|---|
| PM1 | S1 baja el error entre 0,5 y 1,5 | baja 0,29 | **falla** |
| PM2 | S2 baja más que S1 | baja 0,27 | **falla** |
| PM3 | Ninguna baja el orden | las dos lo bajan, apenas | **falla** |

## 2. Control no pre-registrado: cuánto difieren las localidades

**Se calculó después de ver §1 y no decide nada.**

| | Mediana por pregunta |
|---|---|
| Diferencia entre localidades en el mapa de hoy (desviación estándar) | 3,9 puntos |
| La misma diferencia en 2025 | 7,4 puntos |
| El ruido de una localidad en el mapa (desviación estándar) | 2,2 puntos |
| Preguntas donde el método concluyó que las localidades no difieren de verdad | 1 de 35 |

## 3. Qué se aprende: el orden de las localidades no se sostiene de un año a otro

**El hallazgo importante no es el error, es el orden.** La correlación entre el orden de las localidades que da el mapa con
2022-2024 y el que midió 2025 es **0,045**: prácticamente cero. La localidad que el mapa pone más satisfecha, más segura o más
optimista no es, en promedio, la que 2025 encontró así.

**Por qué puede pasar:**
1. **Las diferencias reales entre localidades son pequeñas** frente al ruido de los dos lados: unos 250 donantes por localidad
   en 2022-2024 y unos 80 encuestados en 2025. Ya se sabía que la confiabilidad de las medias por localidad es baja
   (`PUENTE_RESULTS.md` §4).
2. **O cambian de un año a otro** más que entre ellas.

Con estos datos no se pueden separar las dos causas.

**El encogimiento sí ayuda un poco al error** (0,3 puntos), pero no al orden. Acercar las localidades a la ciudad las hace
menos ruidosas, pero no hace aparecer un orden que no está.

**Qué implica para la página:** el mapa ya muestra los márgenes y dice que son anchos. Este resultado es más fuerte: **el mapa
no sirve para ordenar localidades ni para decir cuál está mejor o peor**, al menos para predecir el año siguiente. Proponer
que la página lo diga así es una decisión aparte, para Daniel.
