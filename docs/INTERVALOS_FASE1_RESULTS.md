# PLAN V3, FASE 1: ¿QUÉ REGLA DE RANGO CUBRE AÑO A AÑO? — resultados

Corrido el **19 de octubre de 2026** contra `INTERVALOS_FASE1_SPECIFICATION.md` (pre-registro y código en `6ee9375`, antes de
calcular ninguna cobertura). **Gasto: USD 0.** Cifras por objetivo en `data/processed/benchmark/intervalos_fase1.csv`.

**Los casos:** 158 objetivos; 153 evaluados. Los otros 5 no tenían 5 errores anteriores para armar el rango.

## Cobertura

| Regla | Total | Gobierno (23) | Lo demás (130) | Alcalde y Concejo | Ancho medio |
|---|---|---|---|---|---|
| R1, percentil del total | 78 % | 61 % | 81 % | 73 % | 14,4 |
| R2, agrupación parcial | 78 % | 65 % | 80 % | 73 % | 14,2 |
| **R3, conservadora** | **84 %** | **70 % (69,6)** | **86 %** | 73 % | **19,7** |

### Por año objetivo

| Año | Casos | Error medio de la persistencia | R1 | R3 |
|---|---|---|---|---|
| 2018 | 1 | 4,0 | 100 % | 100 % |
| 2019 | 2 | 5,1 | 100 % | 100 % |
| 2022 | 2 | 7,3 | 50 % | 50 % |
| 2023 | 65 | 3,2 | 97 % | 98 % |
| 2024 | 52 | 4,8 | 65 % | 81 % |
| **2025** | 31 | 6,1 | **58 %** | **58 %** |

### Con cambio de gobierno o con salto

| | Casos | Error medio | R1 | R3 |
|---|---|---|---|---|
| Con cambio de gobierno | 54 | 4,9 | 65 % | 80 % |
| Con salto de más de un año, sin cambio | 1 | 7,3 | 100 % | 100 % |
| Sin salto ni cambio | 98 | 4,1 | 85 % | 86 % |

**Sensibilidad.** R3 en total, quitando cada año: entre 83 % y 90 %, **salvo sin 2023: 73 %**. El 2023 fue tranquilo y tiene
65 casos: sostiene buena parte de la cobertura.

## Regla de decisión

**Ninguna regla cumple las dos condiciones** (75 % en total y 70 % en gobierno): R3 se queda en 69,6 % en gobierno. Como decía la
regla, se queda la de mayor cobertura en gobierno, **R3**, presentada como **«referencia empírica provisional»**.

## Predicciones

| | Predicción | Resultado | |
|---|---|---|---|
| PI1 | R1 no llega al 70 % en gobierno | 61 % | se cumple |
| PI2 | R3 cumple las dos condiciones | 69,6 % en gobierno | **falla**, por poco |
| PI3 | Los objetivos con cambio de gobierno tienen el error medio más alto | 4,9, contra 7,3 del único con salto | **falla** |

## Qué se aprende

1. **Ensanchar con el cambio de gobierno ayuda** (65 % → 80 % en esos 54 casos), pero **no rescata 2025**: entre 2024 y 2025 no
   cambió el gobierno, y aun así fue el año más movido (58 % con cualquier regla). Un año movido sin aviso previo es justo lo que
   ningún rango hecho con el pasado anticipa.
2. **La cobertura total se apoya en 2023:** sin ese año baja a 73 %.
3. **La serie larga aportó pocos casos evaluables** (2018, 2019 y 2022), porque las primeras olas no tenían 5 errores anteriores.
   En gobierno, la prueba sigue siendo de 23 casos.

## Lo que cambió en la página (DI-CO45)

El dato del catálogo agrega su rango con la regla R3 y todos los errores hasta 2025:
- **gobierno e instituciones:** «Rango orientativo provisional: ±10 puntos; en una prueba año a año cubrió el 70 % de 23
  casos»;
- **lo demás:** ±7, que cubrió el 86 % de 130 casos.

Hoy, con el dato de 2025 y el mismo gobierno, no se aplica el ensanche por cambio de gobierno. Si hubiera cambiado, sería ±15 y
±10.
