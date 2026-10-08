# LA REFORMULACIÓN RECONOCE UNA PREGUNTA DEL CATÁLOGO CON UN MATIZ — resultados

Corrido el **8 de octubre de 2026** contra `REFORMULACION_MATIZ_SPECIFICATION.md` (pre-registro y código en `fbc90f3`, antes
de llamar).
- **Comando:** `reformular.validar_voto(4)`, con `openai/gpt-6-luna`.
- **Gasto:** USD 0,052 en 54 llamadas.

## 1. Contra la regla

| | Criterio | Umbral | Resultado | |
|---|---|---|---|---|
| R1 | Alcance correcto | ≥ 36 de 40 | 40 | se cumple |
| R2 | Código del catálogo | ≥ 6 de 8 | 8 | se cumple |
| R3 | «Fuera», ninguna como catálogo | ≥ 8 de 9, 0 | 9, 0 | se cumple |
| R4 | Respuesta válida | ≥ 39 de 40 | 40 | se cumple |
| R5 | «Voto»; tipo y candidatos | ≥ 12; ≥ 11 de 13 | 13; 13 | se cumple |
| R6 | Ninguna que no es de voto como «voto» | 0 | 0 | se cumple |
| R7 | Con matiz, catálogo con su código | ≥ 7 de 8 | **7** | se cumple |
| R8 | Cercanas: ninguna como catálogo; «nueva» | 0; ≥ 5 de 6 | 0; 6 | se cumple |
| R9 | «Caminando por su barrio» → `VS8` | sí | sí | se cumple |

**La versión 4 entra a la página** (`motor.py`, DI-CO32).

| | Predicción | Resultado | |
|---|---|---|---|
| PRM1 | La versión 4 cumple la regla | la cumple | se cumple |
| PRM2 | La del barrio va a `VS8` | va a `VS8` | se cumple |
| PRM3 | Ninguna cercana va al catálogo | ninguna | se cumple |

## 2. Lo que hay que saber

- **La única que falló:** «¿Qué tan seguros se sienten los bogotanos cuando andan por las calles de la ciudad?» quedó como
  nueva, no como `VS10` («¿qué tan seguro en general se siente usted en Bogotá?»).
  - Es el mismo tipo de caso límite: el modelo leyó «las calles» como un lugar más preciso que «Bogotá en general».
  - La página no muestra nada falso: estima con preguntas parecidas, en vez de dar el dato medido.
- **R7 pasó justo en el umbral (7 de 8).** El modelo sigue siendo conservador con los matices. Para la página es el lado
  seguro del error: prefiere estimar a mostrar como medido lo que quizá no lo es.
- **Las 40 de la versión 3 siguen bien:** acierta también las de voto y las de «fuera».
