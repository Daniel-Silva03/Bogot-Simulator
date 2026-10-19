# PLAN V3, FASE 3: ¿MEJORA A LOS AGENTES UN CONTEXTO NUMÉRICO ESTRUCTURADO?

Pre-registro escrito el **19 de octubre de 2026**, antes de llamar al modelo. Sigue `PLAN_SIGUIENTE_PREDICTOR_BOGOTA_V3.md` §7. Lo
pidió Daniel. Gasto: **unos USD 0,20, con tope de USD 1.**

## 1. Hipótesis

Los agentes no saben qué pasó después de su encuesta. Un resumen narrativo de noticias los movió poco y hacia el pesimismo
(`ACTUALIDAD_EPC`). **¿Les ayuda, en cambio, ver cifras públicas fechadas?**
- el resultado de toda la ciudad en la encuesta anterior;
- la serie de aprobación del alcalde hasta la fecha de corte.

**El mecanismo esperado:**
- **El primer dato es un ancla:** debería corregir su sesgo hacia arriba en lo del gobierno (+6 en la Fase A).
- **La serie es señal del cambio:** dice hacia dónde se movió la opinión.

## 2. Los objetivos

Las preguntas de gobierno e instituciones de la Fase B (`data/processed/benchmark/selector_fase_b.csv`), **sin `CC9`**, que
pregunta si la persona conoce Bogotá Cómo Vamos y no es percepción política. Son 9:

| Par | Preguntas |
|---|---|
| P1: EPC 2023 → EPC 2024 | `AG1` (rumbo), `GG7` (corrupción) |
| P2: EPC 2024 → EPC 2025 | `AG1`, `GG7`, `GG3_GALAN` (gestión), `CC5A_GALAN` (Concejo), `MICE1_GALAN`, `MICE2_GALAN`, `MICE3_GALAN` |

## 3. Los métodos

| | Método | De dónde |
|---|---|---|
| **P** | persistencia: el dato del año base | ya calculado en la Fase B |
| **G** | agentes actuales: perfil más la nota de la Fase B | ya calculado en la Fase B |
| **GC** | G más el contexto de §4 | nuevo: 200 agentes por par, una llamada por agente con todas las preguntas del par |

Lo demás es igual a G:
- los mismos 200 agentes del año base;
- el mismo modelo, la misma temperatura y el mismo razonamiento;
- la misma nota y los mismos textos de las preguntas.

## 4. El contexto (escrito antes de correr)

**La fecha de corte es el 1 de septiembre del año objetivo,** antes del campo de la EPC de ese año. Solo entran cifras publicadas
antes de esa fecha.

Va después de la nota de la Fase B, con esta forma:

> DATOS PÚBLICOS DISPONIBLES ANTES DE ESTAS PREGUNTAS (cifras de toda la ciudad, no de esta persona):
> - En la Encuesta de Percepción Ciudadana de {año base}, en Bogotá: {para cada pregunta: su texto corto} → {x} % respondió {lo
>   que se cuenta}.
> - Aprobación de la gestión del alcalde Carlos Fernando Galán en las encuestas de Invamer en Bogotá: {mes y año}, {x} %; … (solo
>   las publicadas antes de la fecha de corte).
>
> Estas cifras son de toda la ciudad: esta persona puede pensar distinto. Responde como ella.

**Lo que entra en cada par:**
- **El dato de la ciudad:** el mismo que usa P (`persistencia_epc.py`), redondeado a entero.
- **La serie de Invamer**, de `config/mediciones_publicadas.csv`:
  - en P1 (corte en septiembre de 2024): febrero, abril, junio y agosto de 2024;
  - en P2 (corte en septiembre de 2025): las nueve, de febrero de 2024 a junio de 2025.

El contexto no dice cómo usar las cifras ni hacia dónde va la opinión.

## 5. Lo que se declara antes de correr

- **Lo real ya se vio:** los nueve objetivos salieron en la Fase B (por pregunta, en su archivo) y siete en `ACTUALIDAD_EPC`.
  Las cifras del contexto son todas anteriores a la fecha de corte y se eligieron por regla (el registro completo de Invamer y el
  dato de la ciudad), no por su efecto. Aun así, no es una prueba a ciegas del lado de lo real.
- **G y GC tienen pocas preguntas:** 9, y 7 de un solo año (2025). Como dice el plan, es evidencia provisional.
- **El dato de la ciudad que va en el contexto es justo lo que predice P.** Si los agentes se limitan a repetirlo, GC se parecerá
  a P. Lo que se mide es si añaden algo.

## 6. Reglas (escritas antes de llamar)

**GC se conserva si cumple las tres:**
- **RC1:** su error medio es **menor que el de P** en los 9.
- **RC2:** sigue siendo menor que el de P **sin los dos objetivos en que más le gana.**
- **RC3:** su error medio es **menor que el de G.**

**Si no se conserva,** se documenta y se cierra esta línea: no se agrega más contexto ni se agranda el panel (plan v3 §7.3).

## 7. Predicciones

- **PC1.** GC se equivoca menos que G: el ancla corrige el sesgo hacia arriba.
- **PC2.** GC no le gana a P (RC1 no se cumple).
- **PC3.** El sesgo de GC, en promedio, queda entre −3 y +3 (el de G era positivo).

## 8. Gasto y código

- **Gasto:** 400 llamadas, unos USD 0,20, con tope de USD 1.
- **Al modelo** van los perfiles de la EPC 2023 y 2024 (pública, anónima), las preguntas, la nota y cifras públicas.
- **Código:** `src/evaluacion/contexto_fase3.py`, con su prueba. Resultados en `CONTEXTO_FASE3_RESULTS.md`.
