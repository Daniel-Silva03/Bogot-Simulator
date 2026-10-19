# UN RESUMEN DE ACTUALIDAD PARA LOS AGENTES: ¿APRENDEN LO QUE CAMBIÓ? — prueba hacia atrás con la EPC

Pre-registro escrito el **19 de octubre de 2026**, antes de llamar al modelo y antes de calcular los resultados de la EPC 2025
en estas preguntas. Lo pidió Daniel: la página tiene que servir **siempre**, con preguntas nuevas sobre la actualidad, sin
esperar datos nuevos. Hace las veces de la **segunda validación de D22** que no pasó (`VALIDACION_AGENTES_D22_RESULTS.md`).
Gasto: **unos USD 0,15, con tope de USD 1.**

## 1. Pregunta

En la página, los agentes son la gente del último año con sus respuestas. Frente a una pregunta de hoy, responden como si nada
hubiera pasado desde entonces: en la imagen de Petro dijeron lo mismo en cinco fechas distintas. **Si les damos un resumen
neutral de lo que pasó en la ciudad desde su encuesta, ¿se acercan a lo que la gente responde después?**

Se prueba hacia atrás, porque ahí se sabe la respuesta: **la gente de la EPC 2024, con un resumen de lo que pasó en 2025,
frente a lo que respondió Bogotá en la EPC 2025.** Es el mismo uso de la página: la gente del último año, más la actualidad,
frente a una pregunta de hoy.

## 2. Los agentes

- **200 encuestados de la EPC 2024,** elegidos con la misma regla y semilla del panel de la página (`agentes.Agentes`).
- **Su perfil:** sus 55 respuestas de 2024 y sus datos demográficos, incluidas sus respuestas de 2024 a las preguntas de abajo.
  En la página es igual: el agente lleva su respuesta del último año.
- **La llamada:** la de la página (`openai/gpt-6-luna`, temperatura 1, razonamiento bajo, probabilidades), con las siete
  preguntas en una sola llamada por agente.

## 3. Las preguntas: las siete políticas que la EPC midió en 2024 y en 2025

| # | Variable | Pregunta para los agentes | Se cuenta | ¿Decide? |
|---|---|---|---|---|
| A1 | `GG7` | ¿Qué tanto cree usted que ha cambiado el nivel de corrupción en Bogotá durante el último año? | ha aumentado algo o mucho (4-5) | **sí** |
| A2 | `CC5A_GALAN` | ¿Usted cómo califica, en términos generales, la gestión del Concejo de Bogotá? | buena o muy buena (4-5) | **sí** |
| A3 | `MICE1_GALAN` | El gobierno de Bogotá, del alcalde Carlos Fernando Galán, está adelantando acciones que contribuyen a la transparencia… | 4 o 5 | **sí** |
| A4 | `MICE2_GALAN` | …atiende y responde de manera efectiva a las necesidades y solicitudes de la ciudadanía. | 4 o 5 | **sí** |
| A5 | `MICE3_GALAN` | …genera espacios de interacción y diálogo con la ciudadanía y promueve la participación… | 4 o 5 | **sí** |
| A6 | `GG3_GALAN` | ¿Usted cómo califica la gestión del alcalde de Bogotá, Carlos Fernando Galán? | buena o muy buena (4-5) | no: ya vista |
| A7 | `AG1` | Las cosas en Bogotá ¿van por buen camino o por mal camino? | buen camino | no: ya vista |

Las de Galán van con el texto de la página (`motor.GALAN_SOLO_AGENTES`). Las demás, con el del catálogo.

**Lo real:** el porcentaje de lo que se cuenta, entre quienes eligieron una opción de la escala (sin «no sabe»), con el peso de
la encuesta. En 2025 para medir; en 2024 para la referencia.

**Lo que se declara antes de correr:**
- **A6 y A7 ya se vieron.** La gestión de Galán en 2025 (26,4) salió en `PERSONAS_POLITICA`. El rumbo de la ciudad en 2025 (48 %,
  nueve puntos más que en 2024) lo mostró el buscador hoy, sin pedirlo, mientras buscaba las fechas de campo. Se reportan,
  pero no deciden.
- **Las cinco que deciden no se han visto** en 2024 ni en 2025.
- **El perfil de 2024 trae 55 preguntas** y el de 2025, 40: la EPC cambió de cuestionario.

## 4. Los brazos

Los dos llevan, después del perfil, esta nota:

> Las respuestas de arriba son de 2024. Estas preguntas son de finales de 2025, casi un año después: la persona puede haber
> cambiado de opinión.

- **A, sin resumen:** solo la nota.
- **B, con resumen:** la nota y el resumen de §5.

## 5. El resumen de actualidad (escrito antes de correr)

**La regla para escribirlo:** solo hechos, con fuente, ocurridos antes del campo de la EPC 2025. La EPC se presentó el 4 de
diciembre de 2025 y su campo suele ir de septiembre a noviembre, así que el resumen llega hasta agosto. Sin encuestas, sin
cifras de opinión, sin decir qué piensa la gente.

> Lo que pasó en Bogotá entre enero y agosto de 2025. El alcalde es Carlos Fernando Galán, en su segundo año de gobierno, y el
> presidente es Gustavo Petro.
> - El 12 de abril terminó el racionamiento de agua que la ciudad tuvo durante un año por la sequía del sistema Chingaza.
> - Siguen las obras de la primera línea del metro: en abril se probó el primer tren, y se anunció su llegada a Bogotá para
>   septiembre.
> - En el primer trimestre subieron los homicidios frente al mismo periodo de 2024 y aumentaron los secuestros extorsivos; la
>   seguridad es el tema más discutido de la ciudad.
> - El 7 de junio, el senador y precandidato presidencial Miguel Uribe Turbay fue atacado a tiros en un acto político en el
>   barrio Modelia, en Bogotá; murió el 11 de agosto.
> - El alcalde y el presidente tuvieron choques públicos por el metro y por el agua.

**Fuentes:** Alcaldía de Bogotá y El Espectador (fin del racionamiento); Publimetro, 14/4/2025 (prueba del tren); Concejo de
Bogotá, 30/4/2025, y Publimetro, 5/5/2025 (homicidios y extorsión en el primer trimestre); Los Tiempos y RCN (Miguel Uribe);
Valora Analitik (Petro y Galán).

**Lo que se declara del resumen:**
- **Lo escribí sabiendo que el rumbo de la ciudad subió nueve puntos en 2025** (§3). Trae hechos buenos (el fin del racionamiento,
  el metro) y malos (la violencia). No escogí los hechos por ese dato, pero no lo puedo demostrar.
- **Es la pieza que se probaría en la página:** un resumen con fecha, que se pone al día.

## 6. Lo que se mide

En las cinco que deciden:
- **el error** de cada brazo frente a la EPC 2025, y su media;
- **el error de repetir 2024:** dar como respuesta de 2025 lo que se midió en 2024. Es la vara difícil: en la imagen de Galán,
  repetir el dato le ganó a los agentes (`GALAN_ACTUAL_RESULTS.md`);
- **la dirección del cambio:** si el brazo se mueve desde el dato de 2024 hacia el mismo lado que se movió Bogotá.

## 7. Reglas (escritas antes de llamar y de calcular)

**El resumen sirve si B cumple las tres:**
- **RA1:** su error medio es **menor que el de repetir 2024.**
- **RA2:** su error medio es **menor que el de A.**
- **RA3:** acierta la dirección del cambio en **al menos 3 de las 5.**

## 8. Predicciones

- **PA1.** A queda cerca de repetir 2024: su error medio a menos de 3 puntos del de repetir 2024.
- **PA2.** RA1 no se cumple: repetir 2024 es muy difícil de superar.
- **PA3.** B es más pesimista que A en al menos 4 de las 5 (más corrupción, peor calificación del gobierno y del Concejo): el
  resumen trae más hechos malos que buenos.

## 9. Qué pasa después

- **Si pasa:** se propone a Daniel el resumen de actualidad como pieza fija de la página, con fecha y puesto al día, y encender los
  agentes con el modelo real. Va con su DI-CO y su visto bueno.
- **Si no pasa:** se anota qué falló, y los agentes siguen apagados con el modelo real.

## 10. Gasto y código

- **Gasto:** 400 llamadas (200 agentes, dos brazos, siete preguntas por llamada), unos USD 0,15, con tope de USD 1.
- **Al modelo** van los perfiles de la EPC 2024 (pública, anónima), las preguntas, la nota y el resumen.
- **Código:** `src/experiments/actualidad_epc.py`, con su prueba. Usa `personas_con_encuesta.datos(2024)`, que ahora arma los
  datos de cualquier año (los nombres de sexo, edad y estrato de 2024 se igualan a los de 2025). Resultados en
  `ACTUALIDAD_EPC_RESULTS.md`.
