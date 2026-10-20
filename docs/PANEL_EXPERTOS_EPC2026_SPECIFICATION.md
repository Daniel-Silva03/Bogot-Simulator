# PRUEBA HACIA ADELANTE CON LA EPC 2026: TERCER MÉTODO, UN PANEL DE EXPERTOS SINTÉTICOS

Pre-registro escrito el **20 de octubre de 2026**, antes de llamar al modelo y antes de que exista la EPC 2026. Suma un método a
`PROSPECTIVA_EPC2026_SPECIFICATION.md`, **sin tocar lo ya congelado** (P, G y la página). La propuesta es de otra IA
(`PLAN_MEJORAS_ALTERNATIVA.md`, módulo 4, y su respuesta), con las correcciones de §3. Lo pidió Daniel. Gasto: **unos USD 0,02, con
tope de USD 1.**

## 1. La idea

Los agentes imitan ciudadanos y, en lo ya medido, repiten la respuesta de su persona (`ALCALDE_SIN_NOMBRE_RESULTS.md`). **El panel
no imita a nadie:** 5 expertos sintéticos leen las cifras públicas y estiman directamente el porcentaje de la EPC 2026. Si alguien
puede leer la tendencia, es esto.

## 2. El método (E)

- **5 roles**, uno por llamada: analista de tendencias, sociólogo urbano, politólogo de coyuntura, experto en instituciones y
  economista comportamental. Sus textos están en `src/evaluacion/panel_expertos_epc2026.py` (`EXPERTOS`).
- **La misma instrucción para todos:** estimar el porcentaje que publicará la EPC 2026 de Bogotá Cómo Vamos (presencial en hogares,
  probabilística, adultos de Bogotá) para la pregunta. La fecha es el 20 de octubre de 2026, y la encuesta no se ha publicado. Salida:
  `{"porcentaje": n}`.
- **Una llamada por experto y por pregunta:** 35 en total.
- **El modelo de los agentes:** `openai/gpt-6-luna`, temperatura 1, razonamiento bajo.
- **Las 7 preguntas y «lo que se cuenta»** son las mismas de la prospectiva.
- **La cifra del panel:**
  - con las 5 respuestas, la media de las 3 del medio (sin el máximo ni el mínimo);
  - con 3 o 4, la mediana;
  - con menos de 3, no hay cifra.

## 3. Correcciones a la propuesta (hechas antes de correr)

- **Los datos del ejemplo de la propuesta no se usan.** Traía cifras que no están verificadas, o que no coinciden con lo medido:
  - una Invamer de octubre de 2026;
  - una encuesta CNC de septiembre de 2026;
  - cifras del DANE;
  - una serie de la EPC con 3 opciones y valores que no son los reales.
- **Solo datos verificados, publicados antes del corte (20/10/2026):**
  - **la serie de la EPC de cada pregunta:**
    - alcalde y Concejo, 2014-2025, con el nombre del alcalde de cada año;
    - rumbo y corrupción, 2022-2025;
    - transparencia, respuesta y participación, 2024-2025;
  - **para el alcalde, las 17 mediciones del registro público** (`config/mediciones_publicadas.csv`), sin las de gestión de la EPC
    que ya van en la serie. Cada una lleva su población, su método y su muestra, si se conocen, y su nota de comparabilidad, con el
    aviso de que no son la misma serie.
- **Sin DANE ni cifras del CNC** (decisión de Daniel, 20/10). El rol del sociólogo se queda: trabaja con lo que sabe y con estos
  datos.
- **Se quitaron dos afirmaciones de los roles que los datos desmienten:**
  - «el Concejo, la participación y la respuesta rara vez cambian más de 1 o 2 puntos por año»: en 2025, transparencia pasó de 22 a
    10 %, y respuesta de 17 a 7 %;
  - «la percepción de corrupción es un sesgo casi inamovible»: entre 2022 y 2025 subió casi 10 puntos (de 41 a 51 %).

  Quedan el rol y su enfoque, sin la cifra.
- **La salida es el porcentaje que se cuenta,** con la escala real de la EPC, no «buena/regular/mala».

## 4. Lo que se congela

En `config/prospectiva_epc2026/`, el mismo día y junto a lo ya congelado:
- **`panel_expertos.csv`:** por pregunta, la cifra de cada experto y la del panel.
- **`panel_expertos.json`:** fecha y hora, modelo, los 5 mensajes de sistema completos, el bloque de datos de cada pregunta, la regla
  de agregación y el gasto.

El código se niega a correr si ya existe.

## 5. Evaluación en diciembre

**Igual que la prospectiva:**
- las mismas preguntas comparables (§5 de ese pre-registro);
- el mismo dato real;
- las mismas reglas, aplicadas a E contra P con `prospectiva_epc2026.evaluar(t, metodo="E")`:
  - **RV1:** al menos 1 punto mejor que la persistencia;
  - **RV2:** lo mismo, también sin el alcalde;
  - la frase textual si gana solo en el alcalde.

**También se informa** E contra G, por pregunta, de forma descriptiva.

**La lectura que propuso la otra IA** (que el panel gane en lo de mucha saliencia y pierda en lo institucional) se informa por
pregunta. **No cambia la regla:** si E no cumple RV1 y RV2, no gana.

## 6. Predicciones

**Las de la otra IA,** registradas como suyas:
- **PE1:** E le gana a P en la gestión del alcalde.
- **PE2:** en el rumbo, empate.
- **PE3:** P le gana a E en corrupción, Concejo, transparencia, respuesta y participación.

**La mía:**
- **PE4:** E no cumple RV1 y RV2.

## 7. Lo que se declara

- **El modelo sabe cosas de 2026** hasta su fecha de corte, y los expertos pueden usarlas. No sabe la EPC 2026.
- **El panel ve la serie de la EPC que los agentes no ven,** y la persistencia es justo su último valor. Si los expertos se limitan a
  repetirlo, E se parecerá a P.
- **Son 7 preguntas y un año:** si gana, hará falta replicarlo.

## 8. Gasto y código

- **Gasto:** 35 llamadas, unos **USD 0,02**, con **tope de USD 1.**
- **Al modelo** van cifras públicas y el texto de las preguntas. Nada de las encuestas propias.
- **Código:** `src/evaluacion/panel_expertos_epc2026.py`, con `tests/test_prospectiva_epc2026.py`. Resultados en
  `PROSPECTIVA_EPC2026_RESULTS.md` cuando salga la EPC 2026.
