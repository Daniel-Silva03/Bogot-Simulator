# PERSONAS CON SU ENCUESTA, PULIDAS — ¿se corrige la exageración sin perder lo que ya funciona?

Pre-registro escrito el **14 de octubre de 2026**, antes de calcular nada y de llamar al modelo. Lo pidió Daniel: «pulir todo
lo que más se pueda esta idea». Gasto: **unos USD 0,60, con tope de USD 2**; falta el visto bueno de Daniel.

## 1. Pregunta

**El punto de partida** (`PERSONAS_CON_ENCUESTA_RESULTS.md`): un agente con las 40 respuestas reales de cada persona le gana a
la constante y a la página.
- **El defecto:** exagera. En tres preguntas dijo que nadie confía o está satisfecho (0 % contra 12 % a 22 % real).
- **Dos causas posibles:**
  1. **la extrapolación:** a una persona descontenta con la ciudad la vuelve descontenta con todo;
  2. **elegir una sola opción:** si cada persona tiene un 20 % de probabilidad de confiar, pero «desconfío» es su respuesta
     más probable, al elegir la más probable para todas el total da 0 %.

**¿Qué variante corrige eso, y se sostiene en personas y preguntas nuevas?**

## 2. Dos etapas, para no ajustar a la medida de los datos

**Desarrollo:**
- **Las mismas 200 personas** de la prueba anterior (semilla 20261014).
- **12 preguntas escondidas:** las 6 de la prueba anterior (`CON_4`, `CON_5`, `CON_7`, `GOB_7`, `MOV_6`, `FIN_3`) y 6 de la
  práctica del lote 8 (`CCC_1`, `CCC_16`, `CCC_20`, `CCC_22`, `GOB_4`, `CTI_4`).
- **Las variantes se comparan aquí, y aquí se elige una.**

**Prueba final, una sola vez:**
- **200 personas nuevas,** sorteadas con la semilla **20261015** entre las que no están en el desarrollo.
- **8 preguntas que no se usaron en el desarrollo:** `CON_6`, `JUS_1`, `SAL_1`, `CTI_3`, `CCC_18`, `CTI_5`, `EDU_4` y
  `EDU_9`.
- **Secundario, sin peso:** las 6 preguntas de la prueba anterior en las personas nuevas. Mide si lo elegido se sostiene con
  otras personas.

**Lo que se vio antes de subir este documento (14/10).** Al probar el circuito en modo simulado, con respuestas al azar y
una «página» que dice 40 % para todo, el script imprimió cifras agregadas de los reales:
- **en la prueba final,** el error de decir 40 % fue de 19,7 puntos; en el desarrollo, de 13,7;
- quiere decir que, en promedio, los resultados reales de las 8 preguntas finales están a unos 20 puntos del 40 %.

No se vio ningún porcentaje por pregunta. Las predicciones ya estaban escritas.

**Los perfiles:** los mismos de antes. Las 40 preguntas del catálogo y las 4 demográficas. Ninguna pregunta escondida está en el
perfil.

## 3. Las variantes (una llamada por persona, con todas sus preguntas escondidas)

| | Qué responde el modelo | Instrucción contra la exageración | Ancla de la página |
|---|---|---|---|
| **V0** | una opción por pregunta (como antes) | no | no |
| **V1** | una opción por pregunta | sí | no |
| **V2** | la probabilidad de cada opción | no | no |
| **V3** | la probabilidad de cada opción | sí | no |
| **V4** | la probabilidad de cada opción | sí | sí |

**La instrucción contra la exageración**, igual en V1, V3 y V4: *«Las personas no son coherentes en todo: alguien
descontento con la ciudad puede confiar en alguna institución o estar satisfecho con algún servicio. No extrapoles su
descontento o su entusiasmo a todo. Cuando sus respuestas no dicen nada directo sobre una pregunta, piensa en lo típico de
alguien como ella en Bogotá, no en la opción más extrema.»*

**Las probabilidades** (V2 a V4): el modelo da la probabilidad de cada opción, y se normaliza a 1 sin «no sabe».
- **La respuesta de la persona** es el valor esperado.
- **El total de Bogotá** es la media ponderada de la probabilidad del lado favorable.

**El ancla de la página** (V4): junto a cada pregunta, la frase «en toda Bogotá, se estima que cerca del X % responde
[el lado favorable]». X es la estimación que la página daría a esa pregunta como pregunta nueva (`Motor.estimar`, con el texto
de la encuesta). **No usa ningún dato de la pregunta escondida,** así que se podría usar con una pregunta de verdad nueva.

## 4. Lo que se mide

Como en la prueba anterior, en la escala de 0 a 100 y sin «no sabe», con `Factor1`:
- **error individual:** frente a la constante, la media ponderada de las otras personas de 2025;
- **error del total:** el porcentaje del lado favorable entre las 200, frente a la cifra de los 1.520;
- **la distribución:** la distancia de variación total (TVD) entre cómo reparte el brazo las 5 respuestas y cómo las reparte
  la realidad, por pregunta y en promedio. 0 es igual; 1, nada en común. Es la medida de Artificial Societies, y reemplaza a la
  razón de desviaciones, que no sirve con probabilidades.
- **la página:** su estimación de cada pregunta (`Motor.estimar`), calculada en la misma corrida.

## 5. Reglas (escritas antes de calcular)

**Elegir en el desarrollo:**
- **Candidatas:** las variantes cuyo error individual es menor que el de la constante.
- **Gana** la de menor error del total. Si hay empate a 0,5 puntos, la de menor TVD.

**La prueba final.** La variante elegida pasa si se cumplen las tres:
- **R1:** su error individual es menor que el de la constante.
- **R2:** su error del total es menor que el de la página en las mismas 8.
- **R3:** su TVD media es de **0,15 o menos**.

**Si pasa,** lo siguiente sería diseñar cómo entraría a la página, con su propia decisión. **Si no,** se reporta qué variante
estuvo más cerca y por qué.

**Secundario, sin peso:** V0 también se corre en la prueba final, para medir cuánto mejoró la elegida frente a lo de ayer.

## 6. Predicciones

- **PP1.** En el desarrollo, las variantes con probabilidades (V2 a V4) tienen menos error del total que las de una opción (V0
  y V1).
- **PP2.** Gana V4. El ancla le da el nivel de la ciudad, y las respuestas de la persona, cómo se aparta de él.
- **PP3.** En el desarrollo, la instrucción sola (V1) mejora poco frente a V0: menos de 2 puntos de error del total.
- **PP4.** La elegida pasa la prueba final.

## 7. Gasto y código

**Llamadas:**
- desarrollo: 5 variantes × 200 personas = 1.000 llamadas;
- prueba final: la elegida y V0, 400 llamadas;
- estimaciones de la página: unas 20 llamadas.

**Total:** unos USD 0,60, con tope de USD 2. El código se detiene solo si llega al tope.

**Datos:** al modelo van los perfiles de la EPC (pública, anónima), como en la prueba anterior. No se sube nada individual.

**Código:** `src/experiments/personas_pulidas.py`, con su prueba. Resultados en `PERSONAS_PULIDAS_RESULTS.md`.
