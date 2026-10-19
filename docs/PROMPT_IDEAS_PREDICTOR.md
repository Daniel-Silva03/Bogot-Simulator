# Prompt para pedirle ideas a otra IA (19/10/2026)

Texto para pegar tal cual. No trae cifras de las encuestas del CNC (D21): solo errores medidos y datos públicos.

---

Eres un experto en encuestas, modelos de opinión pública y simulación con modelos de lenguaje. Te pido ideas concretas para
mejorar un simulador. Lee todo el contexto antes de proponer.

## El objetivo

Trabajo en una firma de encuestas en Colombia. Construimos un simulador de opinión pública de Bogotá. Queremos que se acerque lo
más posible a un **predictor**: que ante una pregunta **nueva sobre la actualidad** (sobre todo política local: el alcalde Carlos
Fernando Galán, el gobierno de la ciudad, las instituciones), dé una cifra cercana a lo que respondería Bogotá **hoy**, con su
error medido. No buscamos una cifra exacta, sino una buena idea de por dónde iría el resultado. Tiene que servir **siempre**:
no podemos esperar a que salgan encuestas nuevas para mejorar.

## Los datos que tenemos

- **La Encuesta de Percepción Ciudadana (EPC) de Bogotá Cómo Vamos**, pública y anónima: unos 1.520 encuestados por año, de 2022
  a 2025. Trae unas 80 preguntas de opinión de la ciudad (servicios, seguridad, movilidad, gestión del alcalde y del Concejo,
  transparencia, rumbo de la ciudad, corrupción) y datos demográficos (sexo, edad, estrato, localidad). El cuestionario cambia
  algo de un año a otro. Se hace entre septiembre y noviembre y se publica en diciembre.
- **Una población sintética** de unos 20.000 agentes, emparejados con encuestados reales de la EPC por demografía y localidad.
- **Encuestas políticas propias, 2021-2026 (nacionales, con submuestra de Bogotá de 285 a 545 casos):** intención de voto,
  imagen del presidente, algunas preguntas de opinión. **Restricción:** sus respuestas individuales no pueden ir a ningún modelo
  de lenguaje; solo el texto de las preguntas. Sus cifras se usan dentro del equipo.
- **Resultados electorales oficiales por mesa** (Registraduría), incluida la primera vuelta presidencial de 2026 en Bogotá.
- **Encuestas publicadas en medios** (Invamer, Guarumo, CB, AtlasIntel…). Para Bogotá en 2026 hay pocas preguntas de política
  local: casi solo la aprobación o imagen del alcalde.

## Cómo funciona hoy

Una página local donde alguien escribe una pregunta:
1. **Un modelo de lenguaje la reformula** y la clasifica:
   - ya medida en la EPC;
   - nueva;
   - intención de voto;
   - fuera de alcance.

   Una llamada aparte marca si el tema es político o de ciudad; acertó en 60 de 60 preguntas de prueba.
2. **Si ya está medida:** muestra el dato real de la EPC, por localidad, con su margen.
3. **Si es nueva y de ciudad:** el modelo elige preguntas medidas parecidas, y se estima el porcentaje de acuerdo con una
   regresión sobre los resultados de esas preguntas. Error medio de unos 15 puntos en 139 preguntas de prueba.
4. **Si es nueva y política, o es sobre Galán: «agentes».**
   - Son 200 encuestados reales de la EPC 2025, cada uno con sus unas 40 respuestas y su demografía.
   - Un modelo de lenguaje (GPT, temperatura 1, razonamiento bajo) responde como cada persona y da la probabilidad de cada
     opción.
   - Se pondera con el peso de la encuesta y se muestra la cifra de Bogotá, con un rango de ±13 y el error medido.
   - **El modelo nunca contesta «por la gente» en general:** responde persona por persona, con sus respuestas reales.
5. **Intención de voto:** una estimación sobre preguntas de voto de las encuestas propias, por regresión.

Trabajamos con **pre-registro:** cada prueba deja escritas sus predicciones y su regla antes de correr, y se reporta contra eso.

## Lo que ya probamos (todo pre-registrado)

| Prueba | Resultado |
|---|---|
| Agentes en 10 preguntas de gobierno de la EPC, ocultándoles esa respuesta | error 7,4-7,8 (la estimación por regresión: 14,3) |
| Agentes en 7 preguntas de opinión nacional de 2026 de las encuestas propias | error 9,0 (decir 50 %: 10,6) |
| Agentes con preguntas políticas nunca usadas: imagen del presidente en 5 fechas de 2026 y «¿habló de política ayer?» en 4 | error 12,2 (decir 50 %: 9,1). La imagen del presidente quedó en unos 39 % en las cinco fechas: **no siguen el tiempo** |
| **Prueba hacia atrás:** gente de la EPC 2024 más un resumen neutral de noticias de 2025, frente a la EPC 2025 (5 preguntas de gobierno) | agentes 10,1 con resumen y 10,9 sin él; **repetir el dato de 2024: 7,7**. El resumen los movió poco y siempre hacia el pesimismo; en 2025 Bogotá se movió en las dos direcciones |
| Imagen de Galán en septiembre de 2026 (CB) | perfil completo, error 1,4; con aviso de «tu opinión es de 2024», 2,6; mezcla de perfiles, 6,9; **repetir la EPC 2025: 0,5** |
| Voto presidencial, 1.ª vuelta 2026, Bogotá (11 candidatos) | agentes solos: 8,1. Con resumen neutral de campaña y la última encuesta: **3,5**. Copiar la encuesta: 1,8 (los agentes la diluyen hacia el centro) |
| 2.ª vuelta 2026 en Bogotá, con solo la encuesta **nacional** | agentes: Cepeda 50,2 % (real 53,6 %), **le ganan a copiar la encuesta nacional (46,1 %)**. Una instrucción de «no te alejes de la encuesta» empeoró a 38,4 % |
| Calibrar las probabilidades al total de la encuesta | iguala el total, pero no mejora el reparto por grupos y empeora fuera de muestra |
| Voto por grupos (sexo, estrato, edad) | peor que dar a todos los grupos la cifra de la ciudad; solo el estrato va en la dirección correcta |
| Más contexto en el perfil (vida, resumen inventado, mezcla de dos modelos) | no mejora en lo político |
| Mapa por localidad: ¿el orden de las localidades se sostiene de un año al siguiente? | casi no |

## Lo que creemos que pasa

- **Repetir el último dato medido les gana a los agentes** cuando ese dato existe. La opinión cambia poco de un año a otro, y
  los agentes añaden ruido.
- **Los agentes no saben qué pasó después de su encuesta.** Un resumen de noticias en texto los mueve poco, y hacia lo negativo.
- **El perfil es todo de Bogotá:** para lo nacional (el presidente), el modelo adivina desde la demografía.
- **Solo aportaron cuando el dato disponible era de otra población:** corrigieron una encuesta nacional hacia Bogotá.
- Con 200 agentes, el azar de la muestra ya da unos ±7 puntos.

## Lo que te pido

Propón de **5 a 10 ideas concretas** para acercarnos al objetivo. Para cada una:
1. **Qué es y por qué debería funcionar,** con la evidencia o la literatura que lo respalda si la hay (por ejemplo, trabajos
   sobre «silicon samples», digital twins, calibración con datos agregados, modelos de nowcasting).
2. **Cómo la pondríamos a prueba con lo que ya tenemos,** sin esperar datos nuevos, con una regla escrita antes y una vara
   difícil: repetir el último dato medido.
3. **Qué tanto creerías que mejora y qué la haría fallar.**
4. **Su costo aproximado** en llamadas al modelo: cada pregunta con 200 agentes son unos USD 0,05, y el presupuesto es chico.

**Condiciones:**
- No propongas lo que ya probamos, salvo que digas qué cambiarías y por qué esa vez sería distinto.
- Respeta las restricciones: no podemos mandar respuestas individuales de nuestras encuestas propias a un modelo de lenguaje.
- Prefiere ideas que sirvan para **cualquier pregunta nueva de hoy**, no solo para una que ya conozcamos.
- Si crees que algo del objetivo no es alcanzable con estos datos, dilo, y propón la versión alcanzable más útil.

Ordénalas de la que más esperas que ayude a la que menos.
