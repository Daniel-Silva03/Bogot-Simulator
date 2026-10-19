# PLAN V3, FASE 1: ¿QUÉ REGLA DE RANGO CUBRE AÑO A AÑO? — validación de origen móvil con la EPC 2014-2025

Pre-registro escrito el **19 de octubre de 2026**, antes de calcular ninguna cobertura. Sigue `PLAN_SIGUIENTE_PREDICTOR_BOGOTA_V3.md`
§5 e `INCERTIDUMBRE_FASE_F.md` (los intervalos del pasado no cubrieron 2025). Lo pidió Daniel. **Gasto: USD 0.**

## 1. Pregunta

Cuando la página usa un dato medido como cifra de hoy, ¿qué ancho de rango cubre de verdad el valor siguiente? Se prueba **año a
año**: para cada año objetivo, el rango se arma solo con los errores de los años anteriores.

## 2. Los datos

**A. La serie larga de la EPC** (`data/processed/serie_epc_bcv.csv`):
- **qué mide:** la gestión del alcalde y la del Concejo, en porcentaje de «buena» o «muy buena» (p4 + p5);
- **cuándo:** alcalde en 2014, 2015, 2017, 2018, 2019 y 2022 a 2025; Concejo en 2014 a 2017, 2019 y 2022 a 2025;
- **por qué gobiernos pasa:** Petro (hasta 2015), Peñalosa (2016-2019), López (2020-2023) y Galán (desde 2024); el Concejo cambia
  en los mismos años.

**B. Las demás preguntas del catálogo 2022-2025** (`persistencia_epc.csv`), sin `GG3_GALAN` ni `CC5A_GALAN`, que ya están en A.

**El objetivo:** cada medición que tenga una anterior en su serie. **La predicción:** persistencia, el dato anterior.

**Lo que se marca en cada objetivo:**
- **salto:** pasó más de un año desde el dato anterior (2015 → 2017, 2019 → 2022, etc.);
- **cambio de gobierno:** el alcalde o el Concejo cambiaron entre el dato anterior y el objetivo.

## 3. Las tres reglas de rango (fijas)

El rango es ± h alrededor de la persistencia. Para un objetivo del año t, h se calcula **solo con los errores de los objetivos de
años anteriores a t**:

| | Regla | h |
|---|---|---|
| **R1** | percentil del total | percentil 80 de todos los errores anteriores |
| **R2** | agrupación parcial por dominio | w · p80(dominio) + (1 − w) · p80(total), con w = n_dominio / (n_dominio + 8) |
| **R3** | conservadora | R2 × 1,5 si hay salto, cambio de gobierno o menos de 8 errores anteriores del dominio; si no, R2 |

**Los dominios** son dos: gobierno e instituciones, y lo demás.

**Un año entra a la evaluación** solo si hay al menos 5 errores anteriores.

## 4. Lo que se declara antes de calcular

- **Ya vi la serie larga entera** (sus 18 valores) al revisar el archivo, y la Fase A mostró los errores medios de la persistencia
  en 2022-2025. Las reglas no tienen nada que ajustar y se escriben antes de calcular cualquier cobertura.
- **Hay pocos objetivos de gobierno antes de 2022:** unos 9 entre alcalde y Concejo. La prueba es más útil que la del año único,
  pero sigue siendo pequeña (plan v3 §5).
- **El factor de expansión de 2022** toma solo 10 valores distintos (DI-B5). Se usa igual.

## 5. Lo que se mide

- **cobertura:** qué fracción de los objetivos cae dentro de ± h;
- **ancho medio:** 2h;
- **el desglose:** en total, en gobierno, en lo demás, en alcalde y Concejo, por año objetivo, y con salto o cambio de gobierno;
- **sensibilidad:** la cobertura sacando cada año objetivo por turno.

## 6. Regla de decisión (escrita antes de calcular)

**Se queda para la página la regla que:**
1. cubra **al menos el 75 % en total** y **al menos el 70 % en gobierno**;
2. entre las que cumplan 1, tenga el **menor ancho medio**.

**Si ninguna cumple,** se queda la de mayor cobertura en gobierno. La página la presenta como «referencia empírica provisional»,
con su cobertura observada y su número de casos, sin prometer un porcentaje.

## 7. Predicciones

- **PI1.** R1 no llega al 70 % en gobierno.
- **PI2.** R3 cumple las dos condiciones.
- **PI3.** Los objetivos con cambio de gobierno tienen el error medio más alto.

## 8. Código

`src/evaluacion/intervalos_fase1.py`, con su prueba. Resultados en `INTERVALOS_FASE1_RESULTS.md`.
