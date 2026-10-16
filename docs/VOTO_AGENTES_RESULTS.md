# INTENCIÓN DE VOTO CON AGENTES — resultados

Corrido el **16 de octubre de 2026** contra `VOTO_AGENTES_SPECIFICATION.md`:
- pre-registro en `3de47bf`, y enmienda 1 (solo 200 agentes) en `e8660f7`, antes de correr;
- **gasto:** USD 0,064;
- un primer intento falló sin cobrar nada, porque la cuenta de OpenRouter estaba en cero. Se corrió después de la recarga.

## 1. Control de memoria (§3)

Luna, sin perfil, a la pregunta por el resultado en Bogotá: **«No lo sé. La primera vuelta presidencial del 31 de mayo de 2026
todavía no se ha celebrado.»** El modelo no conoce el resultado: la prueba vale.

## 2. Resultado

**200 agentes de la EPC 2025, normalizado entre los 11 candidatos:**

| Candidato | Real (Registraduría, Bogotá) | Agentes |
|---|---|---|
| Iván Cepeda | 42,4 | **21,8** |
| Abelardo de la Espriella | 38,4 | 14,3 |
| Paloma Valencia | 9,3 | 13,6 |
| Sergio Fajardo | 6,4 | 18,0 |
| Claudia López | 2,5 | 15,6 |
| Miguel Uribe Londoño | 0,1 | 5,1 |

**Fuera de los 11:** en blanco, 10,7 %, y no votaría, 7,5 %.

| | Criterio | Resultado | |
|---|---|---|---|
| R1 | EAM ≤ 5,4 | **8,14** | **no se cumple** |
| R2 | Cepeda primero | sí, con 21,8 | se cumple |
| R3 | Cepeda y De la Espriella, primero y segundo | segundo queda Fajardo; De la Espriella, cuarto | **no se cumple** |

**Los agentes no sirven todavía para la intención de voto.** Como referencia, la estimación de voto de hoy se equivocó 3,4.

| | Predicción | Resultado | |
|---|---|---|---|
| PV1 | No sirven: el EAM pasa de 5,4 | 8,14 | se cumple |
| PV2 | Cepeda queda primero | sí | se cumple |
| PV3 | Más agentes no mejoran | no se evaluó (enmienda 1) | — |
| PV4 | El modelo no sabe el resultado | no lo sabe | se cumple |

## 3. Qué se aprende

1. **Los agentes no ven la polarización de la campaña.**
   - **En la realidad,** Bogotá se partió entre dos: Cepeda y De la Espriella sumaron 81 %.
   - **Los agentes** reparten el voto como en una elección abierta: los cinco primeros entre 14 % y 22 %.
   - **El centro queda muy por encima:** Fajardo y Claudia López suman 34 %, contra 9 % real.
2. **La razón más probable: el modelo no conoce la campaña de 2026.** Su conocimiento termina antes de la elección, como dijo el
   control de memoria. No sabe quiénes crecieron ni cómo se ordenó la contienda, así que reparte según una imagen vieja de los
   candidatos. El perfil de la persona dice qué opina de Bogotá, pero no de quién es en política nacional.
3. **Pero acierta el ganador,** solo con opiniones sobre la ciudad y sin ninguna pregunta de voto ni de ideología en el perfil.

**Lo que sigue de esto, para D23:** a los agentes les falta lo que pasó en 2026. Las dos formas de dárselo están en D23:
- **un resumen neutral de la campaña:** quiénes son los candidatos y qué decían las encuestas publicadas en mayo;
- **el ajuste del total a la última encuesta.**

Cada una va con su propio pre-registro.
