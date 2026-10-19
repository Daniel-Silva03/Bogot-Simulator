# FASE F DEL PLAN DE MEJORAS: LA INCERTIDUMBRE CON LOS ERRORES REALES

Hecho el **19 de octubre de 2026**, siguiendo `PLAN_MEJORAS_PREDICTOR_BOGOTA.md` §11 y §13 (Fase F). **Gasto: USD 0.** No pone a
prueba un método nuevo: mide cuánto se equivoca cada tipo de evidencia y lo pone en la página.

**Código:** `src/evaluacion/incertidumbre_fase_f.py` → `config/incertidumbre.json`, que se sube porque solo trae errores (D21). La
página lo lee (DI-CO43, DI-AG-P7).

## 1. Cuánto se equivoca cada tipo de evidencia

| Clase | Casos | Error medio | 8 de cada 10, menos de |
|---|---|---|---|
| Dato del mes anterior (CB, Galán 2026) | 4 | 2,6 | pocos casos |
| Dato de dos meses antes (Invamer, Galán) | 7 | 3,9 | pocos casos |
| Dato de un año antes, gobierno e instituciones (EPC) | 14 | 7,0 | 10,6 |
| Dato de un año antes, lo demás (EPC) | 130 | 4,0 | 6,8 |
| **Agentes, pregunta política nunca medida** | 17 | **11,3** | **19,5** |
| Agentes, pregunta de ciudad nunca medida (el metro) | 5 | 22,8 | pocos casos |
| Estimación de la página, política nunca medida | 9 | 12,3 | 20,9 |
| Estimación de la página, de ciudad nunca medida | 79 | 13,0 | pocos casos por pregunta |

**Cómo se contó:**
- **Los agentes son solo los de la página (Luna).** Entran también las 7 preguntas del CNC de `AGENTES_2026`, que solo guardaron
  su total.
- **«Pocos casos»:** con menos de 8 cifras por pregunta no se calcula el percentil 80; queda el error medio.

## 2. ¿Cubren los intervalos lo que deben? Un año reservado

El percentil 80 del error de repetir el dato, aprendido con 2022 → 2023 y 2023 → 2024, puesto a prueba en 2024 → 2025:

| | Percentil 80 hasta 2024 | Preguntas de 2025 | Las cubrió |
|---|---|---|---|
| Gobierno e instituciones | 5,9 | 8 | **38 %** |
| Lo demás | 6,3 | 23 | **65 %** |

**No cubrieron lo que debían (80 %).** En 2025 la opinión se movió más que en los años anteriores, sobre todo en lo político (la
gestión de Galán cayó 16 puntos). Un intervalo hecho con el pasado puede quedarse corto si el año es movido. La página usa el
percentil con todos los años, 2025 incluido, que ya es más ancho (10,6 en gobierno), y lo dice como «en 8 de cada 10 casos
pasados».

## 3. Lo que cambió en la página

1. **El dato del catálogo dice qué tan viejo es** y cuánto se equivoca usarlo como cifra de hoy. Por ejemplo: «Como cifra de hoy:
   el dato más reciente es de 2025, de hace un año. En la EPC, repetir el dato del año anterior se equivocó en promedio 7 puntos
   en preguntas de gobierno e instituciones, y en 8 de cada 10 casos, menos de 11.»
2. **Los agentes llevan el error y el rango de su tema.**
   - **En lo político:** error de 11 puntos y rango de ±19,5 (antes ±12,6).
   - **En el botón de las preguntas de ciudad:** error de 23 puntos (el metro) y rango de ±22,8, con el aviso de que ahí es
     menos fiable.
3. **Se corrigió lo que decía antes:** «entre 10 y 12 puntos» valía para lo político, no para el botón de ciudad. El rango de
   ±12,6 venía de pruebas dentro de muestra. Las dos correcciones están anotadas en DI-AG-P6, sin borrar lo anterior.

## 4. El registro de mediciones publicadas

`config/mediciones_publicadas.csv` reúne, con fecha y fuente, todas las mediciones de Galán de 2024 a 2026: Invamer, Guarumo, CB y
la EPC. **La página no lo muestra todavía:** Daniel decidió que en las preguntas de Galán respondan solo los agentes (DI-CO41). Si
se decide mostrar el último dato publicado, este es el archivo.

## 5. Lo que no se hizo

**El registro de cada predicción** (plan §14) choca con D17: «cada consulta es independiente y no deja rastro». Queda para que
Daniel decida.
