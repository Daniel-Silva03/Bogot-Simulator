# SEGUNDA VALIDACIÓN DE D22: LOS AGENTES CON PREGUNTAS POLÍTICAS QUE NUNCA SE USARON

Pre-registro escrito el **19 de octubre de 2026**, antes de llamar al modelo y antes de calcular ningún resultado real. Es la
**segunda validación de la condición 1 de D22**: si pasa, se propone encender los agentes con el modelo real en la página
(`AGENTES_CON_MODELO_REAL = True`). Lo pidió Daniel. Gasto: **unos USD 0,40, con tope de USD 1.**

## 1. Pregunta

Los agentes de la página (200 encuestados reales de la EPC 2025, respondidos por un modelo de lenguaje) ¿se acercan a lo que
respondió Bogotá en 2026, en preguntas políticas que **ninguna prueba ha usado**?

## 2. Las preguntas

De las encuestas políticas del CNC para Revista Cambio de 2026 (D21). Se revisó el diccionario de los cinco estudios de 2026:
son las únicas preguntas de opinión o conducta política que no están en el banco, en el catálogo ni en otra prueba.

| # | Estudio | Variable | Texto para los agentes | Opciones | Se cuenta |
|---|---|---|---|---|---|
| J1 | CC891901 | P20 | En enero de 2026: ¿Usted tiene una imagen positiva o negativa del presidente Gustavo Petro? | 1=Positiva; 2=Negativa | Positiva |
| J2 | CC892901 | P14 | A comienzos de 2026: (la misma) | igual | Positiva |
| J3 | CC893201 | P15 | Entre marzo y abril de 2026: (la misma) | igual | Positiva |
| J4 | CC893401 | P18 | A finales de abril de 2026: (la misma) | igual | Positiva |
| J5 | CC893701 | P9 | En mayo de 2026: (la misma) | igual | Positiva |
| H1 | CC892901 | P17 | A comienzos de 2026: ¿El día de ayer usted habló de política? | 1=Sí; 2=No | Sí |
| H2 | CC893201 | P16 | Entre marzo y abril de 2026: (la misma) | igual | Sí |
| H3 | CC893401 | P20 | A finales de abril de 2026: (la misma) | igual | Sí |
| H4 | CC893701 | P11 | En mayo de 2026: (la misma) | igual | Sí |

**Las fechas:** las del campo de cada estudio (enero, 15-21; abril, 23-30; mayo, 16-22). Dos estudios no traen la fecha en la
base: se usa la que ya tiene el banco.

**Lo real:** el porcentaje de «Positiva» o «Sí» entre los encuestados de Bogotá (`DANE` = 11001), con el factor de expansión,
**sin NS/NR** (el 9). Unos 285 a 545 encuestados por estudio: un margen propio de ±4 a ±6 puntos.

## 3. Lo que se declara antes de correr

- **Nadie vio los resultados.** Se revisó solo la estructura: los textos de las preguntas, las opciones y el rango de fechas.
  Por D21, los porcentajes del CNC se calculan en el equipo, no se imprimen y no van a un modelo de lenguaje. Al modelo va
  solo el texto de la pregunta y sus opciones.
- **Lo que se imprime y se reporta:** la cifra de los agentes en cada pregunta, si acierta el lado (por encima o por debajo de
  50 %) y los errores medios (de las 9, de las cinco de Petro y de las cuatro de «habló de política»). No el real de cada una.
- **Son dos preguntas, medidas varias veces.** J1-J5 son la misma pregunta en cinco fechas; H1-H4, la otra en cuatro. Es una
  prueba angosta: dice si los agentes aciertan el nivel de estas dos, no de lo político en general.
- **La fecha va en el texto,** como en el banco. Los agentes no saben qué pasó entre una fecha y otra.
- **Se prueba el método, no la escala de la página.** La página reformula con cinco puntos; aquí van las dos opciones del
  cuestionario, como en `AGENTES_2026`.
- **«Habló de política ayer» es conducta, no opinión.** Entra porque es política y no se ha usado.

## 4. Cómo se corre

El mismo panel y la misma llamada de la página (`src/consulta/agentes.py`): los 200 agentes, el perfil de cada uno,
`openai/gpt-6-luna`, temperatura 1, razonamiento bajo, la instrucción con probabilidades de `personas_pulidas`. La cifra de
Bogotá es el promedio ponderado de la probabilidad de «Positiva» o «Sí».

## 5. Reglas (escritas antes de llamar y de calcular)

**Los agentes pasan la segunda validación si se cumplen las tres:**
- **RV1:** el error medio en las 9 es de **10 puntos o menos.**
- **RV2:** el error medio es **menor que el de decir 50 %** en las 9.
- **RV3:** aciertan el lado (por encima o por debajo de 50 %) en **al menos 6 de las 9.**

## 6. Predicciones

- **PV1.** Pasan.
- **PV2.** Las cinco cifras de Petro de los agentes quedan a menos de 5 puntos entre sí: no siguen los cambios de un mes a otro.
- **PV3.** El error en «habló de política» es mayor que en la imagen de Petro: es conducta de un día, no una opinión.

## 7. Qué pasa después

- **Si pasa:** se le propone a Daniel encender los agentes con el modelo real (`AGENTES_CON_MODELO_REAL = True`), con su DI-CO.
  No se enciende sin su visto bueno.
- **Si no pasa:** siguen apagados con el modelo real, y se anota qué falló.

## 8. Gasto y código

- **Gasto:** 1.800 llamadas (9 preguntas por 200 agentes), unos USD 0,40, con tope de USD 1.
- **Código:** `src/experiments/validacion_agentes_d22.py`, con su prueba. Necesita `BSS_CNC_POLITICA_DIR`. Los reales quedan en
  `data/processed/validacion_agentes_d22/`, que git ignora. Resultados en `VALIDACION_AGENTES_D22_RESULTS.md`.
