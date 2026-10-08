# LA REFORMULACIÓN NO CONFUNDE A GALÁN CON CLAUDIA LÓPEZ — resultados

Corrido el **8 de octubre de 2026** contra `REFORMULACION_GOBIERNO_SPECIFICATION.md` (pre-registro y código en `23c72d8`,
antes de llamar).
- **Comando:** `reformular.validar_voto(5)`, con `openai/gpt-6-luna`.
- **Gasto:** USD 0,065 en 62 llamadas.

## 1. Contra la regla

| | Criterio | Umbral | Resultado | |
|---|---|---|---|---|
| R1 | Alcance correcto | ≥ 36 de 40 | 40 | se cumple |
| R2 | Código del catálogo | ≥ 6 de 8 | 8 | se cumple |
| R3 | «Fuera», ninguna como catálogo | ≥ 8 de 9, 0 | 9, 0 | se cumple |
| R4 | Respuesta válida | ≥ 39 de 40 | 40 | se cumple |
| R5 | «Voto»; tipo y candidatos | ≥ 12; ≥ 11 de 13 | 13; 13 | se cumple |
| R6 | Ninguna que no es de voto como «voto» | 0 | 0 | se cumple |
| R7 | Con matiz, catálogo con su código | ≥ 7 de 8 | 8 | se cumple |
| R8 | Cercanas: ninguna como catálogo; «nueva» | 0; ≥ 5 de 6 | 0; 6 | se cumple |
| R9 | «Caminando por su barrio» → `VS8` | sí | sí | se cumple |
| R10 | Galán: ninguna como catálogo; «nueva» | 0; ≥ 3 de 4 | 0; 4 | se cumple |
| R11 | Claudia López con su código | ≥ 2 de 3 | 3 | se cumple |
| R12 | Concejo → `CC5A` | sí | sí | se cumple |

**La versión 5 entra a la página** (`motor.py`, DI-CO37).

| | Predicción | Resultado | |
|---|---|---|---|
| PRG1 | La versión 5 cumple la regla | la cumple | se cumple |
| PRG2 | Ninguna de Galán va al catálogo | ninguna | se cumple |
| PRG3 | Las 3 de Claudia López van a su código | las 3 | se cumple |

## 2. Lo que hay que saber

- **De paso, R7 sube a 8 de 8:** «¿Qué tan seguros se sienten cuando andan por las calles de la ciudad?», que la versión 4
  mandaba a «nueva», ahora va a `VS10`. No era el objetivo, y puede ser variación del modelo.
- **No se probó qué hacía la versión 4 con las preguntas de Galán.** El pre-registro supuso que irían a `GG3`, sin
  comprobarlo. Lo que se sabe es que la versión 5 no las manda ahí.
- **Una pregunta sobre «el alcalde», sin nombre,** sigue yendo a `GG3`, y la página la muestra con su «Ojo» de Claudia López.
- **Para Galán no hay dato medido.** Una pregunta sobre él se estima como pregunta nueva, con preguntas parecidas, y lo
  más probable es que diga «dividida».
