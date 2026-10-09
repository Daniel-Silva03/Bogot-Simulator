# ¿DISTINGUE MIROFISH ENTRE ALCALDES BIEN Y MAL CALIFICADOS? — resultados

Corrido el **9 de octubre de 2026** contra `MIROFISH_DISCRIMINACION_SPECIFICATION.md` (pre-registro y código en `18564a6`,
antes de llamar). **Gasto total: USD 0,134**, dentro del tope de USD 1. Incluye el paso 0 y dos informes rehechos por cortes
de internet (§4).

## 1. Paso 0

Luna no conoce ninguna de las tres cifras: «No lo sé con certeza y no quiero adivinar el porcentaje», con frases parecidas
para las tres ciudades. Se corren las tres.

## 2. Lo que dio MiroFish

Cada informe está en chino y queda en `data/processed/mirofish/discriminacion/<ciudad>/informe.md`, sin subir.

| Ciudad | Su cifra, textual | Real (Invamer, junio de 2025) | Error |
|---|---|---|---|
| Medellín | «我估计**50%**的成年居民会认可市长的治理表现» | 79 % | 29 |
| Bogotá | «本次预测将批准比例估计为 **45%**» | 42 % | 3 |
| Cali | «预估成年居民认可率为51%» | 30 % | 21 |

**Error medio: 17,7 puntos.**

**Lo que dicen los propios informes:**
- **Medellín:** el 50 % «debe entenderse como una estimación central con evidencia limitada, no como una predicción
  precisa».
- **Cali:** «los logros visibles y las dudas sobre la agenda social se compensan».

## 3. Contra la regla

| | Criterio | Resultado | |
|---|---|---|---|
| R1 | Orden: Medellín > Bogotá > Cali | Cali 51 > Medellín 50 > Bogotá 45 | **no se cumple** |
| R2 | Separación ≥ 20 puntos | 6 (51 − 45) | **no se cumple** |
| R3 | Error medio menor que decir 50 % para todos (19,0) | 17,7 | se cumple |

**MiroFish no distingue** (§3). Se confirma que no sirve para dar porcentajes de aprobación.

| | Predicción | Resultado | |
|---|---|---|---|
| PD1 | No acierta el orden | no lo acierta | se cumple |
| PD2 | Separación menor de 20 | 6 | se cumple |
| PD3 | Su error medio no baja de 19,0 | 17,7 | **falla** |

**PD3 falla por una razón que confirma el resto.** MiroFish casi dice «50 % para todos»: sus cifras van de 45 a 51. Por eso
su error es casi el de esa respuesta fija, apenas por debajo.

## 4. Qué se aprende

1. **MiroFish da la misma respuesta a todo: alrededor de la mitad.** A Cali, el alcalde con peor aprobación de los tres,
   le dio la cifra más alta (51 %). A Medellín, el mejor calificado del país, 50 %.
2. **El 45 % de Bogotá cerca del 42 % fue casualidad,** igual que el 46 % de la prueba anterior frente a las encuestas de
   2026. Una herramienta que siempre dice «la mitad» va a coincidir con cualquier alcalde que esté cerca de la mitad.
3. **Las tres pruebas cuentan lo mismo:**
   - **segunda vuelta:** acertó reescalando una cifra del documento;
   - **Galán:** sin cifra, dijo «la mitad»;
   - **aquí:** sin cifras, «la mitad» para los tres.

   Sus agentes son los actores del documento, no residentes, y sus informes lo reconocen.
4. **Para que MiroFish sirva de algo en cifras,** habría que cambiar cómo arma la población: agentes con perfiles de
   residentes, entrevistados antes de cerrar la simulación (la segunda mejora propuesta). Así como está, sirve para
   ordenar los temas y los marcos de la discusión, no para estimar.

## 5. Lo que pasó en las corridas (DI-MF7)

- **La red se cayó cuatro veces** durante la prueba.
- **Medellín y Bogotá** terminaron su simulación, pero el informe falló. Se rehízo con `--informe`, sin repetir la
  simulación: Medellín `report_bcafecf297cb`, Bogotá `report_0778a71c3d7d`.
- **Cali** corrió completa de una vez: `report_b66ba78220c4`.
- **El script se corrigió** para que una caída no pierda el registro ni deje seguir sin saldo.
- **Ninguna cifra cambió por eso:** cada ciudad tiene una sola simulación y un solo informe completo.
