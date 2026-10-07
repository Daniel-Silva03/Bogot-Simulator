# LA REFORMULACIÓN RECONOCE LA INTENCIÓN DE VOTO — resultados

Corrido el **7 de octubre de 2026** contra `REFORMULACION_VOTO_SPECIFICATION.md` (pre-registro y código en `05a95d9`,
antes de llamar).
- **Comando:** `reformular.validar_voto()`, con `openai/gpt-6-luna`.
- **Gasto:** USD 0,037 en 40 llamadas.

## 1. Contra la regla

| | Criterio | Umbral | Resultado | |
|---|---|---|---|---|
| R1 | Alcance correcto | ≥ 36 de 40 | 38 | se cumple |
| R2 | Código del catálogo | ≥ 6 de 8 | 8 | se cumple |
| R3 | «Fuera», ninguna como catálogo | ≥ 8 de 9, 0 | 9, 0 | se cumple |
| R4 | Respuesta válida | ≥ 39 de 40 | 40 | se cumple |
| R5 | «Voto» en ≥ 12 de 13; tipo y candidatos en ≥ 11 | | **11**, 11 | **no se cumple** |
| R6 | Ninguna que no es de voto como «voto» | 0 | 0 | se cumple |

**Por la regla (§3), la página sigue con la versión 1 y la intención de voto no se muestra.**

| | Predicción | Resultado | |
|---|---|---|---|
| PRV1 | La versión 2 cumple la regla | no la cumple | **falla** |
| PRV2 | Falla a lo sumo en una de voto | falla en dos | **falla** |

## 2. Las dos que fallaron

1. **«¿Va a ganar Abelardo las elecciones?» → «fuera».** **El error está en la instrucción, no en el modelo.** `SISTEMA_V2` dice
   que «el resultado nacional de una elección» va fuera, y esa pregunta es justo eso. La expectativa del pre-registro («voto»)
   contradecía la instrucción.
2. **«¿Cuántos bogotanos votarían por Paloma Valencia?» → «fuera».** Lo más probable es que lo leyera como una cifra o un dato,
   que la instrucción también manda fuera.

**En las 11 que reconoció,** acertó el tipo y los candidatos en las 11, incluidas las cuatro segundas vueltas.

## 3. Qué sigue (§3)

Se ajusta la instrucción con una enmienda fechada:
- **«¿cuántos o qué porcentaje votarían por X?» es voto,** no una cifra;
- **«¿va a ganar X?»** se lee como intención de voto en Bogotá, y la página lo dice al reformular.

Se valida con preguntas de voto **nuevas**, más las 24 originales, para ver que nada se rompa.

## 4. Versión 3, enmienda 1 (7/10/2026): pasa

Corrida con `reformular.validar_voto(3)` contra la enmienda 1 del pre-registro (`a7563ef`, antes de llamar). **Gasto:** USD 0,038.

| | Criterio | Umbral | Resultado | |
|---|---|---|---|---|
| R1 | Alcance correcto | ≥ 36 de 40 | 39 | se cumple |
| R2 | Código del catálogo | ≥ 6 de 8 | 7 | se cumple |
| R3 | «Fuera», ninguna como catálogo | ≥ 8 de 9, 0 | 9, 0 | se cumple |
| R4 | Respuesta válida | ≥ 39 de 40 | 40 | se cumple |
| R5 | «Voto»; tipo y candidatos | ≥ 12; ≥ 11 de 13 | **13; 13** | se cumple |
| R6 | Ninguna que no es de voto como «voto» | 0 | 0 | se cumple |

**La versión 3 entra a la página.**
- **Las 12 preguntas de voto nuevas** las reconoció con su tipo y sus candidatos, incluidas las formas que fallaron en la
  versión 2 («cuántos», «va a ganar», «qué porcentaje»). Las 4 electorales que debían quedar fuera quedaron fuera.
- **El único error:** «¿La gente se siente segura caminando por su barrio?» la tomó como nueva en vez del catálogo (VS8).
  La reformulada es correcta, «¿Qué tan segura se siente usted al caminar por su barrio en Bogotá?», pero la página no
  mostraría el dato medido con su mapa. En la versión 1 sí acertaba.

**Gasto total de esta prueba:** USD 0,075, con las dos versiones, dentro del tope de USD 0,15.
