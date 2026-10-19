# FASE D DEL PLAN DE MEJORAS: ¿LE GANA ALGÚN MÉTODO SENCILLO A REPETIR EL ÚLTIMO DATO EN EL TIEMPO?

Pre-registro escrito el **19 de octubre de 2026**, antes de calcular ningún error. Sigue `PLAN_MEJORAS_PREDICTOR_BOGOTA.md` §5
(Fase D, modelo temporal) y `SELECTOR_FASE_B_RESULTS.md`. Lo pidió Daniel. **Gasto: USD 0**: no llama a ningún modelo.

## 1. Pregunta

La Fase B dijo que, con un dato medido, lo mejor es mostrarlo. Pero el dato puede ser viejo. **¿Hay un método sencillo que, con
las mediciones anteriores de la misma serie, prediga la siguiente mejor que repetir la última?**

## 2. Las series

**S1. Invamer, aprobación de Galán en Bogotá** (unos 400 encuestados en Bogotá, ±5 puntos):

| Fecha | Aprueba | Fuente |
|---|---|---|
| feb. 2024 | 54 | Noticias Caracol |
| abr. 2024 | 59 | Noticias Caracol |
| jun. 2024 | 47 | El Espectador |
| ago. 2024 | 50 | Infobae, 29/8/2024 |
| oct. 2024 | 52 | El Tiempo; El Colombiano (campo del 4 al 13 de octubre) |
| dic. 2024 | 47 | Infobae, 19/12/2024 |
| feb. 2025 | 44 | Valora Analitik; Qhubo (campo del 14 al 23 de febrero) |
| abr. 2025 | 42 | El Espectador; Infobae, 2/5/2025 |
| jun. 2025 | 42 | Agencia PI (campo del 7 al 16 de junio, 400 en Bogotá) |

Después de junio de 2025 no se encontró medición de alcaldes de Invamer.

**S2. CB Global Data, imagen positiva de Galán, ranking de alcaldes de capitales de 2026** (`GALAN_ACTUAL_RESULTS.md`):

| Fecha | Positiva |
|---|---|
| mar. 2026 | 43,2 |
| abr. 2026 | 46,5 |
| jun. 2026 | 44,3 |
| jul. 2026 | 45,3 |
| ago. 2026 | 49,0 |
| sep. 2026 | 45,5 (derivada: agosto menos la caída de 3,5) |

No se encontró la de mayo. El ranking de CB de Sudamérica (septiembre de 2025, 55,3) es otra serie y no entra.

**S3. La EPC, por año:** todas las preguntas del catálogo, con el lado y el peso de `persistencia_epc.py`, en 2022, 2023, 2024 y
2025.

## 3. Lo que se predice

Cada medición que tenga **al menos dos anteriores en su serie**, solo con esas anteriores:
- **S1:** siete objetivos (de junio de 2024 a junio de 2025);
- **S2:** cuatro (de junio a septiembre de 2026);
- **S3:** 2024 (con 2022 y 2023) y 2025 (con las olas anteriores que tenga), en cada pregunta medida en esos años.

## 4. Los métodos (fijos, sin ajustar nada a los datos)

Con x₁ … xₜ las mediciones anteriores, la última xₜ:

| | Método | Predicción |
|---|---|---|
| **M0** | persistencia | xₜ |
| **M1** | promedio de las dos últimas | (xₜ + xₜ₋₁) / 2 |
| **M2** | tendencia amortiguada | xₜ + 0,5 · (xₜ − xₜ₋₁) |
| **M3** | encogimiento a la media | 0,5 · xₜ + 0,5 · promedio(x₁ … xₜ) |

**Por qué estos:**
- **M1 y M3** suponen que parte del cambio de una medición a otra es ruido de la muestra y se devuelve.
- **M2** supone que el cambio sigue.
- Si la opinión fuera un paseo al azar sin ruido, ninguno le ganaría a M0.

## 5. Lo que se declara antes de calcular

- **Las series ya se vieron:** son los datos. Los métodos se escriben antes de calcular cualquier error, y no tienen nada que
  ajustar.
- **S1 y S2 son de Galán; S3 son todas las preguntas.** Una regla para las series de Galán no se pasa sola a otras preguntas
  (plan §5, punto 6).
- **Septiembre de 2026 en S2 es derivada** (`GALAN_ACTUAL`).
- **Pocas mediciones:** 11 objetivos en S1 y S2, y cuatro olas en la EPC. El plan advierte que no alcanzan para un modelo complejo;
  por eso son cuatro reglas fijas.

## 6. Reglas (escritas antes de calcular)

Dos decisiones separadas, una por tipo de serie:
- **RD1, la EPC (S3):** un método reemplaza a la persistencia en la página si su error medio es **menor que el de M0, juntando
  2024 y 2025**, y sigue siéndolo **sin los dos objetivos en que más le gana**.
- **RD2, las series de Galán (S1 y S2 juntas):** lo mismo, con sus 11 objetivos.

Si más de un método pasa, se queda el de menor error. Si ninguno pasa, se queda la persistencia.

## 7. Predicciones

- **PD1.** En las series de Galán, M3 le gana a M0: con unos 400 encuestados, parte del cambio entre mediciones es ruido.
- **PD2.** En la EPC, ninguno le gana a M0, y M2 es el peor.
- **PD3.** RD1 no pasa; RD2 pasa con M3.

## 8. Código

`src/evaluacion/temporal_fase_d.py`, con su prueba. Resultados en `TEMPORAL_FASE_D_RESULTS.md`.
