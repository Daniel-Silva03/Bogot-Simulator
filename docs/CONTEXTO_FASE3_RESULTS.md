# PLAN V3, FASE 3: ¿MEJORA A LOS AGENTES UN CONTEXTO NUMÉRICO ESTRUCTURADO? — resultados

Corrido el **19 de octubre de 2026** contra `CONTEXTO_FASE3_SPECIFICATION.md` (pre-registro y código en `0b1fe8b`, antes de llamar
al modelo). **Gasto: USD 0,183.** Respondieron todos los agentes.

## Por pregunta

| Par | Pregunta | P, persistencia | G, agentes | GC, con contexto | Real |
|---|---|---|---|---|---|
| 2023 → 2024 | rumbo (`AG1`) | 31,2 | 33,6 | 35,2 | 37,1 |
| 2023 → 2024 | corrupción aumentó (`GG7`) | 35,8 | 45,5 | 52,5 | 45,4 |
| 2024 → 2025 | rumbo (`AG1`) | 37,1 | 35,6 | 34,1 | 48,2 |
| 2024 → 2025 | gestión del Concejo | 16,6 | 20,9 | 19,2 | 14,9 |
| 2024 → 2025 | **gestión de Galán** | **42,3** | 29,3 | 29,4 | **26,4** |
| 2024 → 2025 | corrupción aumentó (`GG7`) | 45,4 | 44,3 | 53,0 | 50,6 |
| 2024 → 2025 | transparencia | 22,4 | 25,2 | 24,1 | 9,9 |
| 2024 → 2025 | respuesta a la ciudadanía | 17,2 | 22,7 | 20,1 | 6,9 |
| 2024 → 2025 | participación | 19,4 | 19,8 | 18,5 | 10,6 |

## Error y sesgo en los 9

| | Error medio | Sesgo |
|---|---|---|
| P, persistencia | 9,0 | +1,9 |
| G, agentes | 7,97 | +3,0 |
| **GC, con contexto** | **7,56** | **+4,0** |

## Reglas

| | Criterio | Resultado | |
|---|---|---|---|
| RC1 | GC menor que P | 7,56 contra 9,0 | se cumple |
| RC2 | GC menor que P sin los dos objetivos en que más le gana | no | **no se cumple** |
| RC3 | GC menor que G | 7,56 contra 7,97 | se cumple |

**GC no se conserva.** Le gana a la persistencia en promedio, pero solo por uno o dos casos. Como dice el plan (§7.3), se cierra
esta línea: no se agrega más contexto ni se agranda el panel.

## Predicciones

| | Predicción | Resultado | |
|---|---|---|---|
| PC1 | GC se equivoca menos que G | 7,56 contra 7,97 | se cumple |
| PC2 | GC no le gana a P | sí le gana en promedio (no de forma robusta) | **falla** |
| PC3 | El sesgo de GC entre −3 y +3 | +4,0 | **falla** |

## Qué se aprende

1. **Lo que decide es la gestión de Galán en 2025.** Cayó de 42 a 26. La persistencia dijo 42 (16 de error), y los agentes, con o
   sin contexto, dijeron 29 (3 de error).
   - En esa pregunta los agentes vieron la caída; en las demás no le ganan a la persistencia con claridad.
   - Es un solo caso, pero es justo el que más le importa al jefe de Daniel.
2. **El contexto mejora poco a los agentes** (7,97 → 7,56) **y no corrige su sesgo,** que sube a +4,0.
   - Siguen altos en transparencia, respuesta y participación, que cayeron a la mitad en 2025. Parte de esa caída puede ser del
     cambio de cuestionario.
   - Con la corrupción, el contexto los empujó hacia arriba en los dos años.
3. **Una nota sobre la comparación con la Fase B:** sin `CC9` (si la persona conoce Bogotá Cómo Vamos), los agentes actuales ya le
   ganaban en promedio a la persistencia en estas 9 (7,97 contra 9,0). En la Fase B, con `CC9`, perdían (9,03 contra 7,89). La
   exclusión de `CC9` estaba en este pre-registro, pero esa comparación con la Fase B es posterior y no está pre-registrada.
4. **Con 9 casos, todo esto es provisional** (plan v3 §3.4). El resultado más claro es negativo: el contexto numérico no cambia
   lo que hacen los agentes.
