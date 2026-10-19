# REFORMULACIÓN, VERSIÓN 6: ¿RECONOCE CUÁNDO UNA PREGUNTA ES POLÍTICA O INSTITUCIONAL? — resultados

Corrido el **19 de octubre de 2026** contra `REFORMULACION_TEMA_SPECIFICATION.md` (pre-registro y código en `6f6c6de`, antes de
llamar al modelo). Comando: `python src/consulta/reformular.py --validar-tema`, con `openai/gpt-6-luna`. **Gasto: USD 0,078**
por 93 llamadas.

## B. El tema, en 30 preguntas nuevas

**Las 30 salieron con el tema correcto:** 16 de 16 políticas y 14 de 14 de ciudad.

- **Las políticas que ya estaban en el catálogo** fueron a su código con tema político:
  - la gestión de Galán → `GG3_GALAN`;
  - el rumbo → `AG1`;
  - la imagen del Concejo → `CC2`;
  - si la Alcaldía escucha → `MICE3_GALAN`.
- **Las demás políticas** salieron como nuevas, con tema político:
  - la Policía, la Registraduría, la Personería, la justicia, los partidos;
  - el presidente, la democracia, la corrupción en la Alcaldía, Galán en movilidad, Claudia López, los ediles;
  - la pregunta del jefe (T11).
- **Las cuatro aprobaciones de una medida en Bogotá** (cobro por entrar al centro, segunda línea del metro, pólvora, pico y placa)
  salieron como ciudad.

## A. Las 63 de la validación anterior

Se cumplen R1 a R8 y R10 a R12. **R9 no se cumple:** «¿La gente se siente segura caminando por su barrio?» salió como nueva
(tema ciudad), y debía ir a `VS8`. Con la versión 5 y el mismo catálogo había ido a `VS8`.

Lo curioso: T18, «¿Se siente segura la gente caminando por su barrio?», casi la misma pregunta, sí fue a `VS8`.

## Reglas

| | Criterio | Resultado | |
|---|---|---|---|
| RP1 | «politica» en ≥ 14 de 16 | 16 | se cumple |
| RP2 | «ciudad» en ≥ 12 de 14 | 14 | se cumple |
| RP3 | válida en ≥ 28 de 30 | 30 | se cumple |
| RP4 | R1 a R12 en las 63 | falla R9 | **no se cumple** |

**Por la regla, la versión 6 no pasa.** La página se queda en la versión 5 (§6 del pre-registro).

## Predicciones

| | Predicción | Resultado | |
|---|---|---|---|
| PP1 | La versión 6 pasa | no pasa, por R9 | **falla** |
| PP2 | Los errores de ciudad caen en las aprobaciones de una medida | no hubo errores | se cumple |
| PP3 | La pregunta del jefe sale «politica» | «politica» | se cumple |

## Qué se aprende

1. **Reconocer el tema funciona:** 30 de 30, incluidas las cuatro aprobaciones de medidas, que eran las difíciles.
2. **El costo fue un cambio en otra parte:** agregar el párrafo del tema movió una decisión de alcance que no tenía que ver con el
   tema («caminando por su barrio» dejó de ir a `VS8`). Con temperatura 0, cambiar el texto de la instrucción mueve los casos
   que están en el borde.
3. **Lo que podría evitarlo:** marcar el tema en una llamada aparte, después de la versión 5. Así el alcance no cambia, porque
   la versión 5 queda intacta. Sería una prueba nueva, con su propio pre-registro.
