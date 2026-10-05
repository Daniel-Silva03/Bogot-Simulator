# ¿ESTARÍA BOGOTÁ DE ACUERDO? — resultados de la validación en el guardado

Corrido el **5 de octubre de 2026** contra `NIVEL_ACUERDO_VALIDACION_SPECIFICATION.md`.
- Pre-registro en `c9463c1`, código en `9816c9f` y resultados reales del guardado en `e6f3568`, todo
  antes de llamar.
- `python src/experiments/nivel_acuerdo_validacion.py` → `data/processed/banco/nivel_acuerdo_validacion.json`.

**Gasto: USD 1,47 en 75 llamadas** (74 más la de prueba), dentro del tope de USD 2,50. Sin respuestas
inválidas.

## 1. Resultado

74 preguntas guardadas de acuerdo o sí/no, en 19 familias:
- `ECP23_P5366` salió por la regla de estructura, porque solo tenía 114 respuestas válidas;
- en 36 de las 74 la mayoría dijo «sí».

| | práctica (paso 2) | **guardado** | regla |
|---|---|---|---|
| error (EAM) | 13,9 | **12,5** | ≤ 15,8 |
| acierta el lado de la mayoría | 80 % | **77 %** | ≥ 67 % y ≥ referencia + 10 |
| referencia fija (siempre «no») | 57 % | 51 % | |
| decide con el rango de ±21,9 | 17 % | 16 % (12 preguntas) | |
| al decidir | 16 de 16 | **12 de 12** («sí» 8/8, «no» 4/4) | |

Por fuente:

| fuente | preguntas | EAM | lado |
|---|---|---|---|
| ECP del DANE | 30 | 12,7 | 87 % |
| Bienal de Culturas | 37 | 12,2 | 68 % |
| Cultura Ambiental | 5 | 13,4 | 100 % |
| EPC de coyuntura | 1 | 8,9 | acierta |
| CNC, metro en 10 años | 1 | 19,2 | falla |

## 2. Contra el pre-registro

| | predicción | resultado | |
|---|---|---|---|
| P1 | pasa la validación | pasa | se cumple |
| P2 | EAM mayor que en la práctica (13,9) | 12,5 | **falla**: fue menor |
| P3 | al decidir, acierta ≥ 85 % | 12 de 12 | se cumple |
| P4 | EAM de la ECP mayor que el de Bogotá | 12,7 > 12,4 | se cumple, por poco |

**Regla (§4): Sonnet pasa la validación.** Por lo escrito, se propone a Daniel cómo mostrarlo en la
página. Es una decisión de proyecto (D19).

## 3. Qué quiere decir

- **Se repite con preguntas que nadie había mirado:**
  - el error del porcentaje es de unos 12-14 puntos;
  - acierta el lado de la mayoría en ~4 de cada 5 preguntas, contra ~1 de cada 2 de la referencia;
  - cuando se atreve a decir «probablemente sí» o «probablemente no», lo que pasa en 1 de cada 6
    preguntas, ha acertado las 28 veces (16 en práctica y 12 aquí).
- **Lo que no hace:** en ~5 de cada 6 preguntas el rango cruza el 50 % y la respuesta honesta es
  «dividida», con un porcentaje estimado y un rango de ±22 puntos.
- **En las preguntas de la Bienal, de Bogotá, acierta menos el lado (68 %) que en las de la ECP (87 %).**
- **El metro, en las tres preguntas guardadas que tocan el tema, quedó «dividido»:**
  - metro en 10 años: real 43,8 %, estimado 62,9 %;
  - usaría el metro: real 70,8 %, estimado 62,9 %;
  - P105.1: real 74,9 %, estimado 57,2 %.

  Tres casos no dicen mucho, pero recuerdan que, en temas de proyectos, el rango importa.
- **Cómo funciona, para que no se lea como magia:** Sonnet no responde por nadie ni pone cifras. Elige
  cuáles de 92 preguntas ya medidas en Bogotá y Colombia se parecen a la nueva, y el porcentaje sale de
  lo que la gente respondió de verdad a esas preguntas.

## 4. Límites

1. 19 familias. Las 28 decisiones acertadas son una muestra pequeña: la tasa real puede ser menor
   que 100 %.
2. Las candidatas son 92 preguntas fijas. Una pregunta nueva sin ninguna parecida entre ellas recibirá
   una estimación pobre, y el rango no lo sabe.
3. La validación usa el formato del banco (acuerdo o sí/no), no el «¿qué tan de acuerdo…?» de cinco
   puntos que reformula la página. Llevarlo a la página exige definir esa equivalencia (§D19).
4. El costo por pregunta en la página sería ~USD 0,02 con Sonnet, contra ~USD 0,004 de hoy.
