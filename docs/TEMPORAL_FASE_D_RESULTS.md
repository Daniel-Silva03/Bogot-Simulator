# FASE D DEL PLAN DE MEJORAS: MÉTODOS TEMPORALES SENCILLOS — resultados

Corrido el **19 de octubre de 2026** contra `TEMPORAL_FASE_D_SPECIFICATION.md` (pre-registro y código en `b18f393`, antes de
calcular ningún error). **Gasto: USD 0.** Cifras por objetivo en `data/processed/benchmark/temporal_fase_d.csv`.

## Error medio

| | Objetivos | M0, persistencia | M1, promedio de dos | M2, tendencia | M3, encogimiento |
|---|---|---|---|---|---|
| **EPC (RD1)** | 80 | **4,59** | 4,80 | 5,33 | 4,69 |
| EPC 2024 | | 4,50 | 4,61 | 5,41 | 4,48 |
| EPC 2025 | | 4,71 | 5,04 | 5,22 | 4,96 |
| EPC, gobierno e instituciones | | 6,26 | 6,79 | 5,86 | 6,36 |
| **Galán, Invamer y CB (RD2)** | 11 | 3,40 | **3,32** | 4,23 | 3,54 |
| Invamer | 7 | **3,86** | 4,29 | 4,57 | 4,43 |
| CB | 4 | 2,60 | **1,63** | 3,63 | 1,99 |

## Reglas

| | Resultado | |
|---|---|---|
| RD1, EPC | ninguno le gana a M0 | **queda la persistencia** |
| RD2, Galán | M1 gana por 0,08, pero no sin los dos objetivos en que más gana | **queda la persistencia** |

## Predicciones

| | Predicción | Resultado | |
|---|---|---|---|
| PD1 | En Galán, M3 le gana a M0 | 3,54 contra 3,40 | **falla** |
| PD2 | En la EPC ninguno le gana a M0, y M2 es el peor | así | se cumple |
| PD3 | RD1 no pasa y RD2 pasa con M3 | ninguna pasa | **falla** |

## Qué se aprende

1. **Repetir el último dato sigue siendo lo mejor,** también frente a métodos que suavizan o siguen la tendencia. Ninguno pasa.
2. **Las dos series de Galán se comportan distinto:**
   - en CB, mes a mes, promediar las dos últimas ayuda (1,6 contra 2,6): ahí parece haber ruido que se devuelve;
   - en Invamer, cada dos meses, repetir gana: los cambios se quedaron (de 59 a 47, de 52 a 44).

   Con 4 y 7 objetivos no se puede saber si es la encuestadora, la frecuencia o el azar.
3. **En gobierno de la EPC, la tendencia ganó** (5,9 contra 6,3): en 2025 la caída de Galán y su gobierno siguió la de 2024. No
   era una regla pre-registrada por dominio, y con tan pocas preguntas no se usa.
4. **El error de repetir el dato depende de qué tan viejo es:** unos 3 puntos con el mes anterior, unos 4 con dos meses, de 4,5 a
   6 con un año. **Lo que más acerca a la cifra de hoy es tener una medición reciente,** no un método.
