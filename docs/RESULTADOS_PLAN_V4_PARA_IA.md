# Resultados del plan v4 del predictor de Bogotá — para la IA que lo propuso

**Fecha:** 20 de octubre de 2026
**Contexto:** de tu plan v4 (`PLAN_SIGUIENTE_PREDICTOR_BOGOTA_V4.md`) se hizo el **Paso 1**. El responsable decidió **no hacer el
Paso 3** (el texto del rango en la página): no le interesa. El Paso 2 está pendiente.

No trae cifras de las encuestas políticas propias: no salen del equipo. Todo lo de abajo es de la Encuesta de Percepción Ciudadana
(EPC), pública.

---

## 1. Resumen en cinco líneas

1. **El acierto con el alcalde en 2025 no se repite.** De tres años, los agentes le ganaron a repetir el dato solo en ese.
2. **En las 15 preguntas de gobierno,** los agentes se equivocan 8,7 puntos y la persistencia 7,4. No se cumplió ninguna regla.
3. **Los agentes tienden a bajarle la nota al alcalde de turno:** lo bajaron cuando la opinión no se movió, y no lo subieron cuando
   subió. En 2025 acertaron porque la opinión justo bajó.
4. **Su error más grande es la corrupción:** en 2023 dijeron 61 % y lo real fue 36 %.
5. **La página no cambia** (decisión de producto). Ya no se puede decir que los agentes «ven los cambios» en la opinión sobre el
   alcalde.

---

## 2. Decisiones de producto, que siguen

- **En las preguntas del alcalde ya medidas,** la cifra principal es la de los agentes.
- **No se muestra al lado la medición anterior.**
- **La página siempre da una cifra.**
- **Los agentes están encendidos con el modelo real,** como experimento declarado.
- **Nuevo: no se hace el Paso 3** de tu plan (comunicar la cobertura del rango en la página).

---

## 3. Lo que ya se sabía antes de correr, y que cambió el diseño

**La regla de tu Paso 1 para el conjunto completo ya no se podía cumplir.** En la Fase B del plan anterior, con todas las preguntas
comparables (unas 80), los agentes perdieron contra la persistencia en las dos transiciones con perfiles:

| Transición | Persistencia | Agentes |
|---|---|---|
| 2023 → 2024 | 4,7 | 5,75 |
| 2024 → 2025 | 6,1 | 8,3 |

Sumar 2022 → 2023 no podía cambiar eso. **Por eso la prueba se hizo solo en gobierno,** donde estaba el caso del alcalde. El
pre-registro declara que ese subconjunto se eligió después de ver la Fase B.

---

## 4. Diseño (pre-registrado antes de llamar al modelo)

**15 objetivos de gobierno en tres transiciones:**

| Transición | Perfiles | Preguntas | Llamadas |
|---|---|---|---|
| EPC 2022 → 2023 | 200 agentes de 2022 | rumbo de la ciudad, corrupción, gestión de la alcaldesa (López), gestión del Concejo | nuevas |
| EPC 2023 → 2024 | 200 agentes de 2023 | las mismas, con el alcalde nuevo (Galán) | nuevas |
| EPC 2024 → 2025 | 200 agentes de 2024 | rumbo, corrupción, Galán, Concejo, transparencia, respuesta, participación | reusadas de la Fase B |

**El método:** el de la Fase B, sin cambios.
- `openai/gpt-6-luna`, temperatura 1, razonamiento bajo.
- Una llamada por agente, con todas las preguntas de su transición.
- Una nota: «las respuestas de arriba son de {año base}; la persona puede haber cambiado de opinión».
- Se cuenta «buena» o «muy buena», ponderado con el peso de la encuesta.

**Un cambio en el perfil, para que los tres años sean iguales:** el perfil de 2024 ya traía la calificación de la persona al
alcalde y al Concejo; a los de 2022 y 2023 se les agregó.

**La persistencia del alcalde en 2023 → 2024** repite el dato de López 2023 para Galán 2024.

**Lo declarado:**
- 9 de los 15 reales ya se habían visto.
- El modelo puede saber qué pasó en esos años (filtración temporal).
- Con el alcalde son solo 3 casos.

**Costo:** USD 0,167, por 400 llamadas.

---

## 5. Resultados

**En total y por transición:**

| | Error medio | Sesgo |
|---|---|---|
| **Persistencia** | **7,37** | +1,1 |
| Agentes | 8,74 | +2,5 |

| Transición | Casos | Persistencia | Agentes | Sesgo de los agentes |
|---|---|---|---|---|
| 2022 → 2023 | 4 | **3,7** | 9,2 | +4,5 |
| 2023 → 2024 | 4 | 7,6 | **6,5** | −2,8 |
| 2024 → 2025 | 7 | **9,4** | 9,7 | +4,4 |

**El alcalde, que es lo que más le importa al jefe del equipo:**

| Transición | Persistencia | Agentes | Real | Gana |
|---|---|---|---|---|
| 2022 → 2023 (López) | 33,1 | 25,3 | 31,1 | persistencia (2,0 contra 5,8) |
| 2023 → 2024 (llega Galán) | 31,1 | 31,1 | 42,3 | empate (11,2) |
| 2024 → 2025 (Galán) | 42,3 | 29,3 | 26,4 | **agentes** (2,9 contra 15,9) |

**La corrupción** («¿aumentó?»):

| Transición | Persistencia | Agentes | Real |
|---|---|---|---|
| 2022 → 2023 | 40,9 | **61,2** | 35,8 |
| 2023 → 2024 | 35,8 | **53,0** | 45,4 |
| 2024 → 2025 | 45,4 | 44,3 | 50,6 |

**Reglas pre-registradas:**

| | Criterio | Resultado |
|---|---|---|
| RP1 | Los agentes, al menos 1 punto mejor que la persistencia en los 15 | no (8,74 contra 7,37) |
| RP2 | Mejores en 2 de 3 transiciones | no (solo en 1) |
| RP3 | Mejores sin sus dos mejores casos | no |
| RA | En el alcalde, mejores en 2 de 3 | no (1 de 3) |

**Sensibilidad sin transparencia, respuesta y participación,** que pueden haber cambiado de cuestionario en 2025: persistencia 6,6,
agentes 7,6. No cambia nada.

**Las tres predicciones se cumplieron:** que no ganarían por un punto, que en el alcalde ganarían en 1 de 3 o menos, y que su sesgo
sería positivo.

**Una comparación declarada en el pre-registro:** en rumbo y corrupción 2023 → 2024, agregar al perfil la calificación del
alcalde y del Concejo empeoró a los agentes:
- con el perfil de la Fase B, errores de 3,5 y 0,1;
- con el perfil nuevo, 5,4 y 7,6.

---

## 6. Lo que se aprende

1. **Lo de 2025 parece un caso, no una capacidad.**
   - Con López (2022 → 2023), la opinión casi no se movió y los agentes la bajaron 8 puntos.
   - Con la llegada de Galán, la opinión subió 11 y los agentes no lo vieron: repitieron el nivel de López.
   - En 2025, bajaron a Galán y la opinión también bajó.
2. **Los agentes tienden a bajarle la nota al alcalde de turno.** No es un sesgo hacia arriba en todo el gobierno: con el alcalde,
   el error fue hacia abajo en 2 de 3 años. Hacia arriba están en transparencia, respuesta y participación, y en la corrupción (que, al ser
   negativa, es un sesgo pesimista).
3. **La corrupción da el error más grande, pero no es estable:** 25 puntos de más en 2023, 8 de más en 2024 y 6 de menos en 2025.
4. **Dar más información de la misma persona no ayuda:** su calificación del alcalde empeoró rumbo y corrupción.
5. **Con lo que hay, en gobierno, repetir el último dato acierta más que los agentes,** igual que en el conjunto completo. Y la
   filtración temporal impide leer cualquier acierto hacia atrás como capacidad de anticipar.

---

## 7. Lo que te pido ahora

1. **¿Sigue teniendo sentido el Paso 2 (corregir el sesgo)?** Los sesgos van en direcciones distintas según la pregunta: abajo con
   el alcalde, arriba con la corrupción y con las preguntas de transparencia. ¿Una corrección por tipo de pregunta, con tan pocos
   casos, tiene alguna posibilidad? ¿Cómo la diseñarías para no sobreajustar?
2. **La tendencia a «bajar al alcalde de turno»:** ¿cómo probarías si es un rasgo del modelo (un pesimismo hacia el gobierno), sin
   gastar mucho? Por ejemplo, con el mismo perfil y preguntas sobre gobiernos distintos.
3. **La prueba hacia adelante con la EPC 2026 (diciembre):** propón cómo dejarla pre-registrada desde ahora para que cuente. Qué
   preguntas, con qué perfiles (EPC 2025), qué fecha de congelamiento, qué regla, y qué reportar si los agentes ganan solo en el
   alcalde.
4. **Dado que los agentes no le ganan a la persistencia en nada medido,** ¿hay algún uso donde sí aporten valor, más allá de
   preguntas que nunca se midieron? En esas, su error histórico es de unos 11 puntos en lo político.

**Restricciones que siguen:**
- pre-registro antes de correr;
- la persistencia como vara;
- nada de respuestas individuales de las encuestas propias a ningún modelo de lenguaje;
- presupuesto chico (200 agentes, unos USD 0,05 por pregunta);
- las decisiones de producto de §2.
