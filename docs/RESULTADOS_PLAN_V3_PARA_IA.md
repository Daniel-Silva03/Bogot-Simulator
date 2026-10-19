# Resultados del plan v3 del predictor de Bogotá — para la IA que lo propuso

**Fecha:** 19 de octubre de 2026
**Contexto:** tu plan v3 (`PLAN_SIGUIENTE_PREDICTOR_BOGOTA_V3.md`) se siguió fase por fase, respetando las tres decisiones de
producto. Este documento cuenta qué se hizo, qué salió y qué quedó pendiente, para que propongas los siguientes pasos.

No trae cifras de las encuestas políticas propias: no salen del equipo.

---

## 1. Resumen en cinco líneas

1. **Fase 0 hecha:** la página presenta a los agentes como «estimación exploratoria», con la fecha de la simulación, la encuesta
   de los perfiles, el error histórico y un rango «orientativo», sin prometer cobertura.
2. **Fase 1, ninguna regla de rango cubrió el 70 % en gobierno año a año.** La conservadora llegó al 69,6 % y quedó como «rango
   orientativo provisional».
3. **Fase 2, registro de 19 mediciones públicas del alcalde en 5 series que no se mezclan.** La prensa casi no publica la ficha
   técnica, y las series no se cruzan en el tiempo: no se pudo agregar nada.
4. **Fase 3, el contexto numérico estructurado mejora poco a los agentes (7,97 → 7,56) y no se conserva.** Su ventaja sobre la
   persistencia (9,0) depende de uno o dos casos.
5. **El caso que más importa:** en la gestión del alcalde en 2025 (cayó de 42 % a 26 %), los agentes dijeron 29 y la persistencia
   42.

---

## 2. Decisiones de producto, que siguen

- **En las preguntas del alcalde ya medidas,** la cifra principal es la de los agentes.
- **El responsable decidió no mostrar al lado la medición anterior** (§4.3 de tu plan), aun después de ver cómo se vería.
- **La página siempre da una cifra.**
- **Los agentes están encendidos con el modelo real,** como experimento declarado.

---

## 3. Fase 0 — Comunicación (hecha, sin costo)

**Lo que dice ahora el resultado de los agentes:**
- **Etiqueta:** «Estimación exploratoria de los agentes · no es una encuesta».
- **Título:** «En la simulación, la mayoría (no) respondería "buena gestión" o "muy buena gestión"». Usa las palabras de la escala
  porque «probablemente no» confundía.
- **Texto:** «Simulación con 200 perfiles de bogotanos reales de la Encuesta de Percepción Ciudadana 2025… No es una encuesta
  nueva a residentes de Bogotá. El rango de ±20 es orientativo: no es un margen de error ni garantiza que la cifra real caiga
  dentro».
- **Error histórico:** «en 17 preguntas políticas que no se habían usado, este método se equivocó en promedio 11 puntos, y cuando
  ya había un dato medido, repetirlo acertó más. Ese desempeño pasado no garantiza la precisión de esta estimación».
- **Al final:** «Simulado el [fecha], con perfiles de la EPC 2025».

**El dato medido** (preguntas no del alcalde) dice su antigüedad y su error como promedio pasado, sin «8 de cada 10».

**Separación por tema:**
- **lo político:** error de 11 y rango de ±19,5;
- **el botón de agentes en preguntas de ciudad:** error de 23 (el metro) y rango de ±22,8.

---

## 4. Fase 1 — Intervalos con origen móvil (hecha, sin costo)

**Datos:**
- la serie larga de la EPC de **gestión del alcalde y del Concejo** (2014-2025, 9 olas cada una, cuatro gobiernos);
- **el resto del catálogo** 2022-2025.

En total, **158 objetivos; 153 evaluados.** Cada año, el rango se armó solo con los errores de los años anteriores.

**Tres reglas fijas:**
- **R1:** percentil 80 del total.
- **R2:** agrupación parcial por dominio, w = n/(n+8).
- **R3:** R2 × 1,5 si hay salto de más de un año, cambio de gobierno o menos de 8 casos del dominio.

| Regla | Cubre en total | En gobierno (23) | En lo demás (130) | Ancho medio |
|---|---|---|---|---|
| R1 | 78 % | 61 % | 81 % | 14,4 |
| R2 | 78 % | 65 % | 80 % | 14,2 |
| **R3** | **84 %** | **69,6 %** | **86 %** | **19,7** |

**Por año objetivo:**

| Año | Casos | Cobertura de R1 | Cobertura de R3 |
|---|---|---|---|
| 2023 | 65 | 97 % | 98 % |
| 2024 | 52 | 65 % | 81 % |
| **2025** | 31 | **58 %** | **58 %** |

**Por tipo de transición:**
- **con cambio de gobierno** (54 casos): R1 65 %, R3 80 %;
- **sin salto ni cambio** (98): 85-86 %.

**Sensibilidad:** sin 2023, R3 cubre el 73 %.

**Ninguna regla cumplió lo pre-registrado** (75 % en total y 70 % en gobierno). R3 quedó en la página como «rango orientativo
provisional»:
- **gobierno:** ±10, que cubrió el 70 % de 23 casos;
- **lo demás:** ±7, que cubrió el 86 % de 130.

**Lo que se aprende:**
- **Ensanchar con el cambio de gobierno ayuda** (de 65 % a 80 %).
- **Pero 2025 fue movido sin cambio de gobierno** (58 %), y eso ningún rango del pasado lo anticipa.

---

## 5. Fase 2 — Registro de encuestas públicas (hecho, sin costo)

**19 mediciones del alcalde en 5 series que no se mezclan:**

| Serie | Concepto | Mediciones | Periodo |
|---|---|---|---|
| Invamer | aprobación de la gestión | 9 | feb. 2024 – jun. 2025 |
| Guarumo | aprobación de la gestión | 1 | abr. 2026 |
| CB Global Data | calificación de gestión, muy buena o buena, de 4 opciones | 6 | mar. – sep. 2026 |
| EPC | calificación de gestión, buena o muy buena, de 5 con «regular» | 2 | 2024, 2025 |
| EPC | imagen favorable | 1 | 2025 |

**Cómo está armado:**
- **Cada dato dice de dónde salió:** 1 del informe original, 13 de prensa, 1 de un resumen del buscador, 3 de microdato propio y 1
  derivado.
- **Lo que falta queda «pendiente»:** la pregunta exacta en 16 de 19, y el campo, la muestra de Bogotá y el método en unas 12.

**Lo que se aprendió:**
- **Los informes de Invamer son PDF de imágenes.** El de Guarumo sí trae texto: 664 encuestados en Bogotá, margen de ±4,5,
  probabilístico presencial y la pregunta literal.
- **Lo que CB llama «imagen positiva» es una calificación de gestión** de 4 opciones, online con cuotas: no es probabilística.
- **Guarumo mide a los adultos «con intención de votar».**
- **La escala de 5 de la EPC con «regular» da mucho menos «buena»** que la de 4 de CB: 26 % contra 43-49 %. No es un cambio de
  opinión.
- **Las series no se cruzan en el tiempo:** no hay dos encuestadoras midiendo el mismo concepto en el mismo mes. No se agregó
  nada (tu §8.2).

---

## 6. Fase 3 — Agentes con contexto numérico estructurado (hecha; no se conserva)

**Diseño (pre-registrado):**
- **Objetivos:** 9 preguntas de gobierno.
  - De EPC 2023 → 2024: rumbo y corrupción.
  - De EPC 2024 → 2025: rumbo, corrupción, gestión del alcalde, gestión del Concejo, transparencia, respuesta y participación.
- **Los mismos 200 agentes del año base,** en tres versiones:
  - **P:** persistencia;
  - **G:** agentes actuales;
  - **GC:** G más un bloque de cifras públicas anteriores al corte (1 de septiembre del año objetivo): el porcentaje de toda la
    ciudad en la EPC del año base para cada pregunta, y la serie de aprobación del alcalde en Invamer hasta el corte. Sin
    narrativa, y con «estas cifras son de toda la ciudad: esta persona puede pensar distinto».
- **Costo:** USD 0,18.

**Resultados:**

| | Error medio | Sesgo |
|---|---|---|
| P, persistencia | 9,0 | +1,9 |
| G, agentes | 7,97 | +3,0 |
| GC, con contexto | 7,56 | +4,0 |

| Pregunta (2025) | P | G | GC | Real |
|---|---|---|---|---|
| **Gestión del alcalde** | **42,3** | 29,3 | 29,4 | **26,4** |
| Rumbo de la ciudad | 37,1 | 35,6 | 34,1 | 48,2 |
| Corrupción aumentó | 45,4 | 44,3 | 53,0 | 50,6 |
| Transparencia | 22,4 | 25,2 | 24,1 | 9,9 |
| Respuesta a la ciudadanía | 17,2 | 22,7 | 20,1 | 6,9 |
| Participación | 19,4 | 19,8 | 18,5 | 10,6 |
| Concejo | 16,6 | 20,9 | 19,2 | 14,9 |

**Reglas:**
- **GC le gana a P en promedio y a G,** pero **no sin los dos casos en que más gana.** No se conserva, y la línea se cerró.

**Lo que se aprende:**
- **Lo decide la gestión del alcalde en 2025:** los agentes vieron la caída y la persistencia no.
- **El contexto casi no cambia a los agentes** y no corrige su sesgo hacia arriba en transparencia, respuesta y participación.
  Esas tres cayeron a la mitad en 2025, quizá en parte por un cambio de cuestionario.
- **Con la corrupción, el contexto los empujó hacia arriba.**

**Nota no pre-registrada:** sin la pregunta «¿conoce Bogotá Cómo Vamos?», los agentes actuales ya le ganaban en promedio a la
persistencia en estas 9 (7,97 contra 9,0). En la Fase B del plan anterior, con esa pregunta, perdían (9,03 contra 7,89).

---

## 7. Lo que te pido ahora

1. **Con estos resultados, ¿cuál es el siguiente paso con más valor esperado?** Propón de 2 a 4, con su diseño de prueba, costo y
   qué los haría fallar.
2. **El acierto en la gestión del alcalde 2025:** ¿cómo probarías si es suerte o algo que se repite, sin esperar a la EPC 2026 de
   diciembre?
   - Datos disponibles: la serie larga 2014-2025 de alcalde y Concejo; agentes de la EPC 2022, 2023 y 2024; la serie de
     Invamer.
   - Hay un problema: los perfiles anteriores a 2022 no están armonizados.
3. **¿Ves una forma de que los agentes dejen de sesgarse hacia arriba en lo del gobierno,** que no sea calibrar al total (ya
   falló) ni darles instrucciones (ya falló)?
4. **Para los intervalos:** con 23 casos de gobierno y un año movido sin aviso, ¿qué harías para que el rango de la página sea
   honesto sin volverse inútil?

**Restricciones que siguen:**
- pre-registro antes de correr;
- la persistencia como vara;
- nada de respuestas individuales de las encuestas propias a ningún modelo de lenguaje;
- presupuesto chico (200 agentes por pregunta, unos USD 0,05);
- las tres decisiones de producto.
