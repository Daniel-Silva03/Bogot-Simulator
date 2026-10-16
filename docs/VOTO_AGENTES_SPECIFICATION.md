# INTENCIÓN DE VOTO CON AGENTES — ¿se acercan los agentes de la EPC a la primera vuelta de 2026 en Bogotá?

Pre-registro escrito el **16 de octubre de 2026**, antes de llamar al modelo. Primera pieza de D23. Gasto: **unos USD 0,90, con
tope de USD 2**. Falta el visto bueno de Daniel y que se recargue la cuenta de OpenRouter, que tiene unos USD 0,24.

## 1. Pregunta

**La intención de voto de la página** (D21, nivel 3) sale de las encuestas del CNC. En la primera vuelta de 2026 en Bogotá se
equivocó **3,4 puntos** entre los 11 candidatos; la última encuesta, 2,6 (`VOTO_REGISTRADURIA_RESULTS.md`).

**¿Se acercan los agentes de D22?** Son encuestados de la EPC 2025, que no preguntó por el voto, y cada uno vota según sus otras
respuestas. ¿Llegan cerca de lo que votó Bogotá? ¿Mejoran con más agentes?

## 2. Datos

**Lo real:** el resultado oficial de la primera vuelta del 31 de mayo de 2026 en Bogotá, de la Registraduría
(`voto_registraduria.reales("E3")`, D16). Se normaliza entre los 11 candidatos, como en `VOTO_REGISTRADURIA`.

| Candidato | % entre los 11 |
|---|---|
| Iván Cepeda | 42,4 |
| Abelardo de la Espriella | 38,4 |
| Paloma Valencia | 9,3 |
| Sergio Fajardo | 6,4 |
| Claudia López | 2,5 |
| Los otros 6 | menos de 1 cada uno (0,02 a 0,55) |

**Los agentes:**
- **A200:** el panel de la página (`agentes.Agentes`, semilla 20261018, 200 personas).
- **A1520:** **todos** los encuestados de la EPC 2025 de las localidades 1 a 19.

Cada uno con su perfil de 40 respuestas del catálogo y sus 4 datos demográficos, ponderados con `Factor1`.

**La pregunta al agente:**
- **El texto:** «Si la primera vuelta de las elecciones presidenciales de 2026 fuera hoy, ¿por quién votaría?».
- **Las opciones:** los 11 candidatos por orden alfabético del apellido, con su nombre completo y sin partido, más «Votaría en
  blanco» y «No votaría».
- **Cómo responde:** con la probabilidad de cada opción, con Luna (temperatura 1 y razonamiento bajo), la forma de
  `PERSONAS_PULIDAS`.

**La cifra de cada candidato:** la suma ponderada de su probabilidad, normalizada entre los 11. El voto en blanco y el «no
votaría» no cuentan, como en lo real.

**Lo que se declara antes de correr:**
- **Ya se conoce el resultado.** Es público desde el 31 de mayo.
- **El modelo podría saberlo** si se entrenó después de esa fecha. Por eso hay un control de memoria (§3).
- **La EPC no tiene ninguna pregunta sobre ideología ni voto.** El agente infiere su voto de lo que opina de Bogotá y de su
  gobierno, y de sus datos demográficos.

## 3. Control de memoria (antes de los agentes)

**Una llamada a Luna, sin perfil:** «¿Qué porcentaje de los votos sacó cada candidato en Bogotá en la primera vuelta
presidencial del 31 de mayo de 2026?».
- **Si acierta a los dos primeros** con menos de 3 puntos de error cada uno, la prueba se reporta pero **no decide**: el modelo
  sabría la respuesta.
- **Si no lo sabe o falla,** la prueba vale.

## 4. Regla (escrita antes de calcular)

**La medida es la de `VOTO_REGISTRADURIA`:**
- **el error medio (EAM) entre los 11 candidatos;**
- **si el primero es el correcto;**
- **si los dos primeros quedan en el orden correcto.**

**Los agentes sirven para la intención de voto si el mejor de A200 y A1520 cumple las tres:**
- **R1:** EAM ≤ **5,4**. Son dos puntos más que la página: los agentes no tienen encuestas de voto detrás, así que se les pide
  quedar cerca, no ganar.
- **R2:** Iván Cepeda queda primero.
- **R3:** Cepeda y De la Espriella quedan primero y segundo.

**La hipótesis de más agentes:** A1520 mejora a A200 si su EAM es al menos 0,5 menor.

## 5. Predicciones

- **PV1.** No sirven: el EAM pasa de 5,4. La EPC no tiene ideología, y los dos primeros están a 4 puntos.
- **PV2.** Cepeda queda primero (R2), porque en el perfil pesan el estrato y la opinión sobre el gobierno.
- **PV3.** A1520 no mejora a A200 en más de 0,5: el error es sobre todo sesgo, no azar.
- **PV4.** El control de memoria no encuentra que el modelo sepa el resultado.

## 6. Gasto y código

- **Llamadas:** 1 de control, 200 de A200 y 1.520 de A1520. A1520 incluye a la mayoría de los 200, pero sus llamadas se piden
  aparte, porque el perfil es el mismo y la caché las reutiliza.
- **Costo:** unas 1.520 llamadas nuevas, cerca de USD 0,90, con tope de USD 2.
- **Datos:**
  - al modelo van los perfiles de la EPC (pública, anónima) y los nombres de los candidatos;
  - ningún dato del CNC;
  - los resultados de la Registraduría son públicos.
- **Código:** `src/experiments/voto_agentes.py`, con su prueba. Resultados en `VOTO_AGENTES_RESULTS.md`.

---

## Enmienda 1 (16/10/2026, antes de correr): solo 200 agentes

**Decisión de Daniel:** usar solo los 200 agentes del panel para ahorrar («usemos 200 agentes para ahorrar»).

**Qué cambia:**
- **Sale el brazo A1520.** Era casi todo el gasto: 1.520 de las 1.721 llamadas.
- **La regla se aplica a A200,** sin cambios: R1, EAM ≤ 5,4; R2, Cepeda primero; R3, los dos primeros en orden.
- **La hipótesis de más agentes y PV3 no se evalúan.** Si más adelante interesa, irá con su propio pre-registro.

**El gasto** baja de unos USD 0,90 a unos **USD 0,10** (201 llamadas, con el control de memoria). El tope sigue en USD 2.
