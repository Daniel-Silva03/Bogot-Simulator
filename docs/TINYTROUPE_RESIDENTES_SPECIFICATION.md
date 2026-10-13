# TINYTROUPE CON RESIDENTES DE BOGOTÁ

Pre-registro escrito el **13 de octubre de 2026**, antes de correr nada. Lo pidió Daniel, tras revisar un blog de
herramientas de simulación de personas. **Gasto: unos USD 0,20, con tope de USD 1.**

## 1. La pregunta

Con MiroFish, los residentes simulados se negaron a opinar o respondieron todos igual: error de 30,8 puntos en cinco
preguntas de la EPC 2025 (`MIROFISH_RESIDENTES_RESULTS.md`).

[TinyTroupe](https://github.com/microsoft/TinyTroupe) es la librería de Microsoft para simular personas con modelos de
lenguaje. Es gratuita, de código abierto (MIT) y corre en local. Está pensada para entrevistar a personas simuladas, no para
simular una red social.

**La pregunta:** con los mismos residentes, el mismo contexto y las mismas preguntas, ¿le va mejor a TinyTroupe?

**Se espera lo mismo:** usa el mismo tipo de agentes, el modelo contestando por personas inventadas (Experimento 8). La
prueba sirve para descartarlo con evidencia.

## 2. Método

**Todo igual que en `MIROFISH_RESIDENTES`, salvo la herramienta (DI-TT1):**
- **los doce residentes** de `mirofish_semilla_bogota_residentes.md`, con nombre, edad, localidad, estrato y oficio, sin
  opiniones;
- **el contexto:** cada residente escucha primero el mismo resumen de la gestión de Galán;
- **las cinco preguntas,** con el mismo prefijo («Responda empezando con una sola palabra, SÍ o NO…»);
- **la lectura del «sí» o el «no»** y la ponderación por estrato (`leer_si_no`, `porcentaje_residentes`).

**Cada residente es una `TinyPerson`** (DI-TT2, DI-TT3):
- se le definen edad, nacionalidad, residencia (localidad y estrato) y oficio;
- escucha el contexto y luego cada pregunta (`listen_and_act`);
- su respuesta es el texto de sus acciones TALK.

**La configuración** (`config.ini` de la carpeta de trabajo):
- `MODEL=openai/gpt-6-luna` por OpenRouter;
- `REASONING_EFFORT=low`;
- caché de llamadas en disco;
- sin memoria semántica ni consolidación, que usan embeddings y no hacen falta para cinco preguntas;
- sin chequeos de calidad ni regeneración.

**La instalación** está en `Desktop\TinyTroupe`, fuera del repositorio: versión 0.7.0, código de marzo de 2026. El lector
web de llama-index que trae como dependencia no se usa.

## 3. Con qué se compara

| Clave | Pregunta | EPC 2025 |
|---|---|---|
| satisfaccion | ¿Está usted satisfecho(a) con Bogotá como un lugar para vivir? | 61 % |
| orgullo | ¿Se siente usted orgulloso(a) de Bogotá? | 57 % |
| buen_camino | ¿Cree usted que las cosas en Bogotá van por buen camino? | 59 % |
| aprobacion | ¿Aprueba usted la gestión del alcalde Carlos Fernando Galán? | 26 % |
| victima | Durante el último año, ¿fue usted víctima de algún delito en Bogotá? | 15 % |

**Las referencias de `MIROFISH_RESIDENTES_RESULTS.md`:**
- el simulador: error medio 15,1, Spearman 0,70;
- MiroFish con residentes: error 30,8, Spearman 0,45;
- decir 50 % para todo: error 17,2.

## 4. Regla y predicciones

**La misma regla de `MIROFISH_RESIDENTES` §5. TinyTroupe distingue si se cumplen las tres condiciones:**
1. **R1:** Spearman con la EPC 2025 ≥ 0,7;
2. **R2:** separación entre su cifra más alta y la más baja ≥ 20 puntos;
3. **R3:** error medio < 17,2.

**Si responden menos de 9 residentes,** esa pregunta queda sin cifra y cuenta como fallo.

**Predicciones:**
- **PT1.** TinyTroupe no cumple la regla.
- **PT2.** Se equivoca más que el simulador (15,1).
- **PT3.** En la aprobación de Galán, la mayoría de los residentes se niega a opinar («no tengo información»).

## 5. Lo que ya se sabe, y se declara

Los resultados de la EPC 2025, del simulador y de MiroFish con residentes, incluidas sus respuestas textuales.

## 6. Gasto, datos y código

- **Gasto:** 12 residentes × (1 contexto + 5 preguntas), con varias llamadas por respuesta: unas 150 a 200 llamadas, unos
  USD 0,20. **Tope de USD 1:** antes de cada residente se revisa lo gastado.
- **Nada del CNC ni de la EPC** sale hacia el modelo.
- **Las salidas** quedan en `data/processed/tinytroupe/residentes/`, ignoradas por git.
- **Código:** `src/experiments/tinytroupe_residentes.py`. Se corre con el Python de la instalación de TinyTroupe.
- **Pruebas:** `tests/test_tinytroupe_residentes.py`.
- **Resultados:** `TINYTROUPE_RESIDENTES_RESULTS.md`.
