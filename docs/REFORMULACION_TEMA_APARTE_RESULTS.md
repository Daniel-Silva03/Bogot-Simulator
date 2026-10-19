# EL TEMA EN UNA LLAMADA APARTE — resultados

Corrido el **19 de octubre de 2026** contra `REFORMULACION_TEMA_APARTE_SPECIFICATION.md` (pre-registro y código en `69751b3`,
antes de llamar al modelo). Comando: `python src/consulta/reformular.py --validar-tema-aparte`, con `openai/gpt-6-luna`.
**Gasto: USD 0,025.**

## Resultado

**Las 30 salieron con el tema correcto,** como en la versión 6, pero ahora con la versión 5 intacta.

**Las políticas:**
- **cuatro fueron al catálogo**, con tema político por la lista: el trabajo del alcalde (`GG3_GALAN`), la corrupción (`GG7`),
  la opinión del Concejo (`CC2`) y la transparencia de Galán (`MICE1_GALAN`);
- **las otras doce salieron como nuevas**, con tema político por la llamada aparte: la Fiscalía, el Ejército, la Secretaría de
  Seguridad, Petro, los congresistas, Galán frente al racionamiento, la Procuraduría, las elecciones, el alcalde local, el
  rumbo del país, la Contraloría y el plan de seguridad de Galán (A16).

**Las de ciudad:**
- **cinco fueron al catálogo**, con tema de ciudad: basuras, seguridad en Bogotá, cultura, ríos y vivir en Bogotá;
- **las nueve nuevas** salieron de ciudad, incluidas las cinco aprobaciones de una medida (la Séptima, la tarifa de estudiantes,
  edificios más altos, la ciclovía y los peajes).

Ninguna respuesta inválida. Ninguna política fue a «fuera» ni a «voto».

## Reglas

| | Criterio | Resultado | |
|---|---|---|---|
| RA1 | «politica» en ≥ 14 de 16 | 16 | se cumple |
| RA2 | «ciudad» en ≥ 12 de 14 | 14 | se cumple |
| RA3 | válida en ≥ 28 de 30 | 30 | se cumple |

**Pasa.** Es la primera validación de la condición 1 de D22.

## Predicciones

| | Predicción | Resultado | |
|---|---|---|---|
| PA1 | Pasa | pasa | se cumple |
| PA2 | Los errores, si los hay, en A16 o en las aprobaciones | no hubo errores | se cumple |
| PA3 | Al menos 3 políticas al catálogo con tema político | 4 | se cumple |

## Qué se aprende y qué sigue

1. **Separar el tema de la reformulación funciona:** 30 de 30, con la versión 5 sin tocar.
2. **Entre las dos pruebas, 60 de 60 con el tema correcto,** con las mismas definiciones.
3. **Lo que sigue (§5 del pre-registro):** conectar el tema al motor, con su DI-CO y mostrándoselo a Daniel antes. Las nuevas de
   tema político irían a los agentes, que siguen apagados con el modelo real hasta la segunda validación de D22: una prueba de
   los agentes con preguntas políticas nuevas que no se hayan usado.
