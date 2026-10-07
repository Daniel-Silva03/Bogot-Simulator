# INTENCIÓN DE VOTO SIMULADA, PARTE 2 — contra los resultados de la Registraduría en Bogotá

Pre-registro escrito el **7 de octubre de 2026**, antes de calcular ningún resultado de Bogotá y antes de llamar. Es la parte 2
de `VOTO_SIMULADO_SPECIFICATION.md` (§4), que Daniel eligió correr («con las 215 guardadas y la de la registraduría»).
Gasto: **~USD 0,03, con tope de USD 0,20**.

**Nada de esto se muestra en la página antes de la revisión jurídica (D21).**

## 1. Pregunta

La parte 1 comparó la simulación con lo que respondió la gente en encuestas. Aquí se compara con lo que la gente votó. **Si
alguien hubiera preguntado, antes de cada elección, «¿votaría por X?», ¿qué tan cerca habría quedado la simulación del
resultado real en Bogotá?** Y, como referencia, ¿qué tan cerca quedó la última encuesta?

## 2. Datos

**Resultados reales.** De la Registraduría (D16), en la carpeta de `BSS_ELECTORAL_DIR`, en este PC `Desktop\CNC_datos`:

| Elección | Archivo | Bogotá |
|---|---|---|
| E1: primera vuelta 2022 | `2022_presidencia_primera_vuelta.dta` (por municipio) | la fila de Bogotá |
| E2: segunda vuelta 2022 | `2022_presidencia_segunda_vuelta.dta` (por municipio) | la fila de Bogotá |
| E3: primera vuelta 2026 | `registraduria_2026/MMV_…_1009.csv` (mesa a mesa, Bogotá) | la suma de las mesas |

**La segunda vuelta de 2026 no se toca:** tiene su propio pre-registro. La columna de documento de los candidatos del archivo de
2026 (`CANCEDULA`) no se lee.

**Encuestas.** Las 373 preguntas del lote 7, práctica y guardado, con su resultado real de Bogotá. Para cada elección **solo
cuentan las encuestas anteriores a ella**:
- **E1 y E2:** CC871401 (mayo de 2021), CC871801 (junio de 2021), CC873501 (sin fecha, anterior a marzo de 2022 por su
  contenido) y CC875701 (abril de 2022).
- **E3:** las cinco de 2026. Las fechas de campo conocidas van del 15 de enero al 22 de mayo, y las otras dos son anteriores
  por su contenido.

## 3. Método

**Los candidatos de cada elección** son los del resultado de Bogotá que aparecen nombrados en al menos una pregunta de las
encuestas anteriores. Una opción nombra a un candidato si trae su primer nombre y su primer apellido, sin tildes ni mayúsculas.
- No entran el voto en blanco, los nulos ni los no marcados.
- **Los porcentajes reales** son los de cada candidato sobre la suma de los votos de ese conjunto.

**La simulación.** Para cada candidato X, una pregunta nueva escrita así:
- **E1:** «En mayo de 2022: si las elecciones presidenciales fueran mañana, ¿votaría por X?»;
- **E2:** «En junio de 2022: en una segunda vuelta entre Gustavo Petro y Rodolfo Hernández, ¿votaría por X?»;
- **E3:** «En mayo de 2026: si las elecciones presidenciales fueran mañana, ¿votaría por X?».

**Se estima con el método de la parte 1:**
- Luna elige entre las preguntas de las encuestas anteriores, y la estimación es la media de sus resultados reales;
- las candidatas van primero, con la marca de caché (DI-NB7 y DI-E11);
- las estimaciones de los candidatos de una elección se normalizan para que sumen 100.

**La referencia: la última encuesta.** Para cada candidato, la pregunta de la encuesta más reciente anterior a la elección
que lo mide en el mismo tipo de pregunta (primera vuelta o fórmula, para E1 y E3; la segunda vuelta Petro contra Hernández,
para E2), normalizada igual.

## 4. Medidas (se reportan, sin regla)

En cada elección, para la simulación y para la última encuesta:
- **EAM** de los porcentajes normalizados contra el resultado real;
- **si pone primero** al candidato que ganó en Bogotá;
- **en E2, el error en la diferencia** entre los dos candidatos.

**Sin regla:** son tres elecciones, y la distancia entre encuesta y resultado depende de más cosas que el simulador, como el
cambio de opinión entre la encuesta y la elección o quién vota.

## 5. Predicciones (escritas antes de calcular)

- **PR1.** La última encuesta queda más cerca del resultado que la simulación en al menos 2 de las 3 elecciones.
- **PR2.** La simulación pone primero al ganador de Bogotá en al menos 2 de las 3.
- **PR3.** El EAM promedio de la simulación en las tres elecciones es de 8 puntos o menos.

## 6. Gasto, código y lo que no se sube

- **Gasto:** una llamada por candidato y elección (unas 20), más la de escritura de la caché: unos USD 0,03, con tope de
  USD 0,20.
- **Código:** `src/experiments/voto_registraduria.py`.
- **Prueba:** `tests/test_voto_registraduria.py`.
- **Lo que no se sube:**
  - **los resultados de las encuestas del CNC (D21):** la salida queda en `data/processed/banco/`, ignorada;
  - **`VOTO_REGISTRADURIA_RESULTS.md`** da cifras de error y aciertos. Los resultados oficiales de la Registraduría son
    públicos y pueden citarse; los de las encuestas y la simulación, no.

## 7. Lo que se hizo antes de llamar (7/10)

**`--candidatos`** lista qué candidatos entran en cada elección. No lee resultados de la Registraduría, solo los nombres:
- **E1:** 8 de 8;
- **E2:** 2 de 2;
- **E3:** 11 de 11.

**El cruce de nombres se corrigió antes de ver nada** (DI-VR2). La primera versión dejaba fuera a Petro, porque tomaba
«Francisco» como apellido, y a Gutiérrez, por el apodo «Fico». **Gasto esperado:** 21 llamadas, unos USD 0,02.

**No se corre en modo simulado,** porque imprimiría el error de la última encuesta contra el resultado antes de la corrida.

