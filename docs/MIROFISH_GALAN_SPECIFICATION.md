# MIROFISH ANTE LA APROBACIÓN DE GALÁN

Pre-registro escrito el **9 de octubre de 2026**, antes de correr nada. Es la segunda prueba de MiroFish, que la regla de
`MIROFISH_SEGUNDA_VUELTA_RESULTS.md` habilitó. Lo pidió el jefe de Daniel.
**Gasto: unos USD 0,07, con tope de USD 1.**

## 1. La pregunta

En la segunda vuelta, MiroFish acertó en Bogotá, pero porque su informe reescaló la primera vuelta que traía el documento.
Aquí el documento no trae ninguna cifra que reescalar.

**La pregunta:** con un documento de hechos públicos de la gestión de Carlos Fernando Galán hasta agosto de 2025, ¿estima
MiroFish qué porcentaje de bogotanos aprueba su gestión? ¿Lo hace mejor que nuestro simulador y que una referencia simple?

**Nuestro simulador no tiene con qué:** la EPC 2022-2024 no mide a Galán (DI-CO36). Si MiroFish aporta algo, se vería aquí.

## 2. Método

**MiroFish,** con la misma instalación, modelo y topes de la primera prueba: Luna, 10 rondas, tope de USD 1.
- **Se corre con** `python src/experiments/mirofish_segunda_vuelta.py --caso galan`.
- **Documento semilla:** `docs/anexos/mirofish_semilla_galan.md`. Trae el racionamiento de agua, el alza de TransMilenio
  y el choque con Petro, el metro y la seguridad. **No trae encuestas de aprobación ni de percepción, ni datos del CNC.**
- **La petición** (`REQUERIMIENTO_GALAN`): simular la conversación de los bogotanos adultos sobre su gestión en el segundo
  semestre de 2025 y estimar qué porcentaje la aprueba, con una sola cifra.

**Nuestro simulador,** con la página tal como está hoy (versión 5, DI-CO37; rango DI-CO33). La pregunta es
«¿Los bogotanos aprueban la gestión del alcalde Carlos Fernando Galán?».
- Se espera que la tome como nueva y dé un porcentaje de acuerdo con su rango.
- Si la manda al catálogo, se anota y se usa lo que dé.

**Paso 0, antes de todo:** preguntarle a Luna si conoce la aprobación de Galán en la Encuesta de Percepción Ciudadana 2025.
Si la conoce y da la cifra, la prueba de MiroFish no sirve, y se anota sin correrla.

## 3. Con qué se compara

**El resultado real:** la aprobación de la gestión del alcalde en la **Encuesta de Percepción Ciudadana 2025 de Bogotá
Cómo Vamos**, publicada el 5 de diciembre de 2025: **26 %**
([Radio Nacional](https://radionacional.co/noticias-colombia/aprobacion-de-carlos-fernando-galan-se-desploma-al-26-en-bogota)).
- **Es la misma encuesta de la que sale nuestro simulador,** aunque de otro año.
- **Se reporta también, sin que decida,** Invamer de junio de 2025: 42 %, con otra pregunta y otro método.

**Cómo se lee la cifra de MiroFish:** la que dé el informe, copiada textualmente. Si es un rango, el punto medio. Si no da
cifra, «no da cifra».

**Las referencias:**
1. **el simulador:** su porcentaje estimado;
2. **el dato anterior:** la calificación positiva («buena» o «muy buena») de la gestión de la alcaldesa Claudia López en la
   EPC 2022-2023 (`GG3`), tal como la muestra la página. Es lo que diría alguien que solo conoce la medición anterior.

**Si la estimación del simulador se apoya en preguntas de las encuestas del CNC,** su cifra queda en local (D21) y en los
resultados va solo su error.

## 4. Predicciones y regla

- **PG1.** MiroFish da una cifra.
- **PG2.** MiroFish se equivoca más de 10 puntos.
- **PG3.** El rango del simulador incluye el 26 %. Es ancho, ±21,7 a ±23,9.
- **PG4.** Luna no conoce la cifra (paso 0).

**Regla:** MiroFish sirve para estimar aprobación si da cifra y se equivoca menos que el simulador y que el dato anterior.
Si no, se anota como herramienta para explorar narrativas, no para estimar porcentajes. Así lo sugirió la primera prueba.

## 5. Lo que ya se sabe, y se declara

- **La cifra real (26 %)** y las de Invamer: 44 % en febrero de 2025 y 42 % en junio de 2025. Las vi al buscar la
  referencia.
- **La calificación de Claudia López en `GG3`:** positiva 33 %, vista en la página el 8/10.
- **El documento semilla lo escribí yo,** sabiendo la cifra. Para no sesgarlo, solo trae hechos hasta agosto de 2025, con su
  fuente. Una frase de las fuentes («cerró su segundo año con una imagen favorable de solo 26 %») quedó fuera a propósito.

## 6. Gasto, datos y código

- **Gasto:**
  - MiroFish, unos USD 0,06 (la primera prueba costó 0,0585);
  - el simulador, 2 a 3 llamadas;
  - el paso 0, 1 llamada.

  **Tope de USD 1.**
- **Nada del CNC ni de la EPC** sale hacia MiroFish, Zep ni el modelo, salvo lo que la página ya manda (el texto de las
  preguntas, D21).
- **Las salidas** quedan en `data/processed/mirofish/galan/`, ignoradas por git.
- **Código:** `src/experiments/mirofish_segunda_vuelta.py` (`--caso galan`, DI-MF5).
- **Pruebas:** `tests/test_mirofish_segunda_vuelta.py`.
- **Resultados:** `MIROFISH_GALAN_RESULTS.md`.
