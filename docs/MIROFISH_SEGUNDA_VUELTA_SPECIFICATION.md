# MIROFISH ANTE LA SEGUNDA VUELTA DE 2026 EN BOGOTÁ

Pre-registro escrito el **9 de octubre de 2026**, antes de correr MiroFish. Lo pidió el jefe de Daniel; Daniel eligió el
tema. **Gasto: USD 0,10 a 0,30 esperados, con tope de USD 1.**

## 1. La pregunta

[MiroFish](https://github.com/666ghj/MiroFish) crea agentes con personalidad propia hechos con un modelo de lenguaje, los
pone a conversar en una red social simulada y escribe un informe.
- **Es lo contrario de nuestro simulador:** allí el modelo contesta por las personas, y nosotros lo descartamos tras el
  Experimento 8.
- **La pregunta:** con un documento público de antes de la elección, ¿estima MiroFish el resultado de Cepeda en Bogotá en
  la segunda vuelta del 21 de junio de 2026, y cómo le va frente a lo que ya tenemos?

**Es una prueba exploratoria, de una sola elección.** No decide nada de la página.

## 2. Método

- **Instalación local:** `Desktop\MiroFish`, código del 2 de octubre de 2026, versión `7657031`. Se maneja con
  `src/experiments/mirofish_segunda_vuelta.py`.
- **Modelo:** `openai/gpt-6-luna` por OpenRouter. La memoria de los agentes va en Zep Cloud, con la cuenta gratuita.
- **Documento semilla:** `docs/anexos/mirofish_semilla_segunda_vuelta.md`. Es un resumen de hechos públicos anteriores al
  21 de junio:
  - la primera vuelta en el país y en Bogotá (Registraduría);
  - quién apoya a quién;
  - el tono de la campaña.

  **No trae encuestas de segunda vuelta ni ningún dato del CNC.**
- **La petición a MiroFish** (`REQUERIMIENTO`): simular la conversación de los votantes de Bogotá en las dos semanas
  previas y estimar el porcentaje de los votos por los dos candidatos de cada uno, con una sola cifra que sumen 100.
- **Simulación:** las dos redes en paralelo (Twitter y Reddit), con un **máximo de 10 rondas**. El número de agentes lo
  decide MiroFish con las entidades del documento.
- **Una sola corrida.**

## 3. Con qué se compara

**El resultado real:** la proporción de Cepeda sobre los votos por los dos candidatos en Bogotá, según el preconteo final
de la Registraduría (el boletín con todas las mesas). Si no se consigue la cifra final, se reporta contra lo que ya se
sabe (§5), y se dice.

**Cómo se lee la cifra de MiroFish:**
- **Su cifra:** la de Cepeda en Bogotá que dé el informe, copiada textualmente.
- **Si incluye el voto en blanco u otras opciones,** se pasa a los votos por los dos.
- **Si es un rango,** se toma el punto medio.
- **Si no da cifra,** se anota «no da cifra», y PM1 falla.

**Las referencias, calculadas igual, sobre los votos por los dos:**
1. **el simulador** (la página, DI-CO30): la segunda vuelta Cepeda contra De la Espriella;
2. **la última encuesta del CNC** antes de la elección: mayo de 2026;
3. **la regla de bloques** de `SEGUNDA_VUELTA_2026_SPECIFICATION.md`: 47,3 %, hecha solo con la primera vuelta.

Las dos primeras salen de encuestas del CNC: sus cifras quedan en local (D21). En los resultados va solo su error.

## 4. Predicciones y regla

- **PM1.** MiroFish da una cifra para Cepeda en Bogotá.
- **PM2.** Acierta el ganador en Bogotá: Cepeda por encima del 50 %.
- **PM3.** Su error es mayor que el de la última encuesta del CNC.

**Regla:** MiroFish pasa a una segunda prueba (la percepción de Galán) si da cifra y su error no es mayor que el del
simulador. Si no, se anota como herramienta para explorar narrativas, no para estimar porcentajes.

## 5. Lo que ya se sabe, y se declara

- **Un resultado parcial de Bogotá:** con el 46 % de las mesas, Cepeda 53,14 % y De la Espriella 44,73 %
  ([Publimetro](https://www.publimetro.co/noticias/2026/06/21/en-vivoelecciones-2026-asi-vota-bogota-en-la-segunda-vuelta-presidencial-entre-ivan-cepeda-y-abelardo-de-la-espriella/)).
  Sobre los dos, unos 54,3 %.
- **El jefe de Daniel dijo 52 %.**
- **De la Espriella ganó en el país.**
- **Lo que dice el simulador** en esta segunda vuelta (DI-CO35).
- **Luna dice no conocer el resultado:** su conocimiento llega a junio de 2024, y se negó a dar porcentajes (chequeo del
  9/10, USD 0,0002). No es una garantía, pero el resultado no debería venir de su memoria.
- **El documento semilla lo escribí yo,** sabiendo el resultado. Para no sesgarlo, solo lleva hechos anteriores al 21 de
  junio, con su fuente, y ninguna encuesta de segunda vuelta.

## 6. Gasto, datos y código

- **Gasto:** unas 250 llamadas a Luna, USD 0,10 a 0,30. **Tope de USD 1**, controlado con el uso de la clave en OpenRouter;
  si se pasa, la simulación se detiene (DI-MF1). La clave es la de la página, y la página queda cerrada durante la
  corrida.
- **Zep** usa la cuota gratuita. Ve solo el documento semilla y lo que generan los agentes.
- **Nada del CNC ni de la EPC** sale hacia MiroFish, Zep ni el modelo.
- **Las salidas** (informe, registro, log) quedan en `data/processed/mirofish/`, ignoradas por git.
- **Código:** `src/experiments/mirofish_segunda_vuelta.py`.
- **Pruebas:** `tests/test_mirofish_segunda_vuelta.py`.
- **Resultados:** `MIROFISH_SEGUNDA_VUELTA_RESULTS.md`.
