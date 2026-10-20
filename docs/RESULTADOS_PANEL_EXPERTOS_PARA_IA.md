# El panel de expertos sintéticos, congelado para la EPC 2026 — para la IA que lo propuso

**Fecha:** 20 de octubre de 2026
**Contexto:** de tu propuesta (`PLAN_MEJORAS_ALTERNATIVA.md`) y tu respuesta sobre el módulo 4, se implementó el **panel de 5
expertos sintéticos** como tercer método de la prueba hacia adelante con la EPC 2026. Las predicciones quedaron congeladas y
subidas a GitHub con fecha, antes de que exista la encuesta. Los módulos 1, 2 y 3 no se hicieron, por las razones que ya te dimos.

No trae cifras de las encuestas políticas propias. Todo es de la Encuesta de Percepción Ciudadana (EPC), pública, y de encuestas de
prensa publicadas.

---

## 1. Resumen en cuatro líneas

1. **Tu diseño se usó casi entero:** los 5 roles, una llamada por experto y por pregunta, y la media de los 3 del medio.
2. **Se corrigieron tres cosas antes de correr:**
   - solo datos verificados;
   - sin dos afirmaciones de los roles que nuestros datos desmienten;
   - la salida en la escala real de la EPC.
3. **Costó USD 0,006** (35 llamadas). Respondieron los 5 expertos en las 7 preguntas.
4. **El panel casi repite el dato de 2025,** salvo dos apuestas: Galán se recupera a 31 % y el rumbo empeora a 45 %.

---

## 2. Lo que se cambió de tu propuesta, y por qué

**Los datos de tu ejemplo no se usaron:**
- **la Invamer de octubre de 2026 (38 %)** no está en nuestro registro, donde Invamer llega a junio de 2025;
- **la encuesta CNC de septiembre de 2026** tampoco: por regla, las cifras del CNC no entran;
- **las cifras del DANE** no estaban verificadas;
- **la serie de la EPC** tenía 3 opciones y valores que no son los medidos (en 2024 decía 35 % de «buena»; lo medido fue 42,3 %).

**Lo que vieron los expertos** (todo publicado antes del 20/10/2026):
- **la serie de la EPC de cada pregunta,** en el porcentaje que se cuenta:
  - alcalde y Concejo, 2014-2025, con el nombre del alcalde de cada año;
  - rumbo y corrupción, 2022-2025;
  - transparencia, respuesta y participación, 2024-2025;
- **para el alcalde, 17 mediciones públicas** con su ficha:
  - Invamer, 9, de febrero de 2024 a junio de 2025;
  - Guarumo, 1, en abril de 2026;
  - CB Global Data, 6, de marzo a septiembre de 2026;
  - la imagen favorable de la EPC 2025.

  Van con el aviso de que no son la misma serie.

**Sin DANE ni cifras del CNC,** por decisión del responsable. El sociólogo trabajó con lo que sabe y con estos datos.

**Dos afirmaciones de los roles se quitaron,** porque los datos las desmienten:
- **del experto en instituciones,** «el Concejo, la participación y la respuesta rara vez cambian más de 1 o 2 puntos por año»: en
  2025, transparencia pasó de 22 a 10 % y respuesta de 17 a 7 %;
- **del economista comportamental,** «la corrupción es un sesgo casi inamovible»: entre 2022 y 2025 subió de 41 a 51 %.

Quedaron el rol y su enfoque; sin esas cifras, los expertos no dirían «persistencia» por instrucción.

**La salida es el porcentaje que se cuenta,** con la escala real (por ejemplo, «buena o muy buena», de 5 opciones), no
«buena/regular/mala».

**Mismo modelo que los agentes:** `openai/gpt-6-luna`, temperatura 1, razonamiento bajo.

---

## 3. Lo congelado

| Pregunta | P, 2025 medido | G, agentes | E, panel |
|---|---|---|---|
| Gestión de Galán | 26,4 | 27,3 | **31,3** |
| Buen camino | 48,2 | 40,9 | 44,8 |
| Corrupción aumentó | 50,6 | 53,8 | 52,7 |
| Concejo | 14,9 | 19,6 | 14,8 |
| Transparencia | 9,9 | 19,9 | 11,2 |
| Respuesta a la ciudadanía | 6,9 | 18,6 | 8,3 |
| Participación | 10,6 | 17,8 | 10,6 |

**Cada experto:**

| Pregunta | Tendencias | Sociólogo | Politólogo | Instituciones | Comportamental |
|---|---|---|---|---|---|
| Galán | 27,0 | 30,0 | 35,0 | 34,0 | 30,0 |
| Buen camino | 51,5 | 44,0 | 44,5 | 46,0 | 44,0 |
| Corrupción | 54,0 | 52,0 | 53,0 | 50,0 | 53,0 |
| Concejo | 14,3 | 15,0 | 14,5 | 15,2 | 15,0 |
| Transparencia | 8,0 | 12,5 | 11,0 | 11,5 | 11,2 |
| Respuesta | 4,8 | 9,5 | 7,0 | 8,5 | 9,5 |
| Participación | 1,8 | 12,0 | 9,0 | 11,5 | 11,2 |

**Lo que se ve:**
- **Los 5 expertos casi no discrepan:** como mucho 8 puntos (Galán), salvo en participación, por el 1,8 del analista de
  tendencias; en el Concejo, menos de 1. La diversidad de roles que
  esperabas no produjo errores en direcciones distintas.
- **En las institucionales el panel repite el dato de 2025,** mientras los agentes van 5 a 12 puntos arriba.
- **En Galán, el panel apuesta a una recuperación** (31 %). El politólogo, que mira la prensa, es el más alto (35 %). Las encuestas
  de 2026 que vio dan 43 a 53 %, pero con otra escala y otro método.
- **El analista de tendencias da 1,8 % en participación,** muy lejos de los demás. La media sin extremos lo descarta, como
  proponías.

---

## 4. Cómo se evalúa en diciembre

Con las reglas ya registradas para la prueba hacia adelante:
- **RV1:** el panel se equivoca al menos 1 punto menos que la persistencia en las preguntas que sigan siendo comparables;
- **RV2:** lo mismo, también sin la pregunta del alcalde;
- **si gana solo en el alcalde,** el informe lo dice con una frase ya escrita.

**Tu lectura** (que gane en lo de mucha saliencia y pierda en lo institucional) se informa por pregunta, pero no cambia la regla.

**Las predicciones registradas:**
- **las tuyas:** el panel le gana a la persistencia en Galán, empata en el rumbo y pierde en las otras cinco;
- **la nuestra:** el panel no cumple RV1 y RV2.

**Una nota sobre tus predicciones:** en Concejo, transparencia, respuesta y participación, el panel quedó casi igual a la
persistencia (a menos de 1,5 puntos), y en corrupción a 2,1. Allí va a ser difícil que alguien gane por mucho.

---

## 5. Lo que te pido ahora

1. **La poca diferencia entre los 5 expertos:** ¿la ves como un problema del diseño (el mismo modelo con otro sombrero) o como señal
   de que los datos dominan? ¿Cambiarías algo para la próxima ronda, sin tocar lo congelado?
2. **La recuperación de Galán a 31 %:** es la única apuesta fuerte del panel. ¿Cómo leerías en diciembre un acierto o un fallo ahí,
   sabiendo que es una sola pregunta y un solo año?
3. **¿Hay algo que valga la pena hacer antes de diciembre,** con presupuesto chico, que no contamine esta prueba?

**Restricciones que siguen:**
- pre-registro antes de correr;
- la persistencia como vara;
- ninguna respuesta individual de nuestras encuestas propias va a un modelo de lenguaje;
- ni cifras del CNC ni datos sin verificar;
- unos USD 0,05 por pregunta;
- lo congelado para 2026 no se toca.
