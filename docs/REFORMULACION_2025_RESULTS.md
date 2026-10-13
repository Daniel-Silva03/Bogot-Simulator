# REFORMULACIÓN CON EL CATÁLOGO 2022-2025 — resultados

Corrido el **13 de octubre de 2026** contra `REFORMULACION_2025_SPECIFICATION.md`, pre-registrado en `45b9e18` antes de
llamar.
- **Gasto:** USD 0,053 por 63 llamadas a `openai/gpt-6-luna`; se esperaban unos USD 0,07.
- **Respuestas** en `data/processed/reformulacion/catalogo_2025/`, sin subir.
- Código: `reformular.validar_2025`.

## 1. Contra la regla (§3)

| | Criterio | Resultado | |
|---|---|---|---|
| R1 | alcance correcto en ≥ 36 de 40 | 40 | se cumple |
| R2 | código correcto en ≥ 6 de 8 | 8 (la gestión del alcalde va a `GG3_GALAN`) | se cumple |
| R3 | «fuera» en ≥ 8 de 9, ninguna como catálogo | 9, ninguna | se cumple |
| R4 | válida en ≥ 39 de 40 | 40 | se cumple |
| R5 | «voto» en ≥ 12 de 13; tipo y candidatos en ≥ 11 | 13 y 13 | se cumple |
| R6 | ninguna que no es de voto como «voto» | 0 | se cumple |
| R7 | matiz: catálogo con su código en ≥ 7 de 8 | 7 | se cumple |
| R8 | ninguna de las 6 cercanas como catálogo; «nueva» en ≥ 5 | 0 y 6 | se cumple |
| R9 | «caminando por su barrio» → `VS8` | sí | se cumple |
| R10 | Galán: G1-G3 con su código en ≥ 2 de 3; G4 y G5 ninguna como catálogo | 3 de 3; ninguna | se cumple |
| R11 | López: ninguna en un código de Galán; «nueva» en ≥ 2 de 3 | ninguna; 3 de 3 | se cumple |
| R12 | el Concejo → `CC5A_GALAN` | sí | se cumple |

**Pasa: 12 de 12.** La página usa la población 2022-2025 y este catálogo (DI-CO38).

| | Predicción | Resultado | |
|---|---|---|---|
| PR1 | Pasa | pasa | se cumple |
| PR2 | G1 y G2 van a `GG3_GALAN` | 2 de 2 | se cumple |
| PR3 | Las tres de López son «nueva» | 3 de 3 | se cumple |

**Lo único distinto de lo esperado:** «¿Qué tan seguros se sienten los bogotanos cuando andan por las calles…?» salió
«nueva». Se esperaba `VS10`, y con el catálogo anterior acertó. R7 se cumple igual (7 de 8). Ninguna otra respuesta de las
54 cambió de alcance.

## 2. PP4 de la población (§5, sin gasto)

El dato medido de la página, con la población 2022-2025, contra los microdatos de la EPC 2025:

| Pregunta | EPC 2025 | Página 2022-2024 | **Página 2022-2025** |
|---|---|---|---|
| Satisfecho con Bogotá (`CV1`) | 61,4 % | 51,2 % | **54,1 %** |
| Orgulloso (`AG2`) | 56,6 % | 48,7 % | **50,4 %** |
| Buen camino (`AG1`) | 48,2 % | 33,3 % | **37,0 %** |
| Aprueba a Galán | 26,4 % | 47,3 % (estimación) | **33,9 %** (`GG3_GALAN`, medido) |
| Víctima de delito (`VS15`) | 14,6 % | 25,3 % | **23,9 %** |
| **Error medio** | | 12,9 | **8,3** |
| **Spearman** | | 0,90 | **1,00** |

**PP4 se cumple** (8,3 < 12,9). **No es una prueba a ciegas:** 2025 está en los datos. La mejora mayor es Galán: pasa de una
estimación (47,3 %) a un dato medido (33,9 %).

**Por qué no da la cifra de 2025:** la página promedia los años. En Galán junta 2024 y 2025, y en las otras cuatro junta
2022 a 2025. Por eso las cuatro de la ciudad quedan por debajo de lo que dijo 2025, y la victimización por encima.
