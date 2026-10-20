# PLAN V5, PASO 3: ¿CAMBIA LA CIFRA DE LOS AGENTES SI NO SE NOMBRA AL ALCALDE?

Pre-registro escrito el **20 de octubre de 2026**, antes de llamar al modelo. Sigue `PLAN_SIGUIENTE_PREDICTOR_BOGOTA_V5.md` §3. Lo
pidió Daniel. Gasto: **unos USD 0,05, con tope de USD 1.**

**Es un diagnóstico del modelo, no una predicción.** No dice cuál es la opinión de Bogotá ni elige una variante para la página.

## 1. Las dos hipótesis

En la réplica del alcalde, los agentes dijeron 25, 31 y 29 % mientras lo real fue 31, 42 y 26 %.
- **Pesimismo con el gobernante:** el modelo le baja la nota al alcalde aunque el perfil no lo justifique. Así lo leí en
  `REPLICA_ALCALDE_RESULTS.md`; el plan v5 lo corrigió.
- **Valor central:** el modelo da una cifra cercana a un porcentaje típico, alrededor del 30 %, sin seguir los cambios.

## 2. Las dos condiciones

| | Qué recibe el modelo |
|---|---|
| **A, página** | «¿Usted cómo califica la gestión del alcalde de Bogotá, Carlos Fernando Galán?» (el texto de la página) |
| **B, sin nombre** | «¿Usted cómo califica la gestión del alcalde de Bogotá?» |

**Todo lo demás es igual:**
- los 200 agentes de la página (EPC 2025), con sus pesos;
- el modelo, la temperatura, el razonamiento y el mensaje de sistema de la página;
- la escala de 5 opciones;
- sin nota de fecha, como en la página.

**A sale de la prueba hacia adelante** (`PROSPECTIVA_EPC2026`), con la misma caché: no se vuelve a pagar. Solo se paga B.

**Lo que se declara:** el perfil de 2025 ya trae la respuesta de la persona a «¿Usted cómo califica la gestión del alcalde/sa?», sin
nombre. B pregunta casi lo mismo que el perfil. Una diferencia entre A y B solo puede venir del nombre.

## 3. Las medidas

1. **A − B:** la diferencia entre las dos cifras de Bogotá.
2. **Seguimiento:** entre los agentes cuya persona calificó bien al alcalde en 2025 («buena» o «muy buena») y los que no, la
   diferencia en su probabilidad media de «buena» o «muy buena». Se calcula en A y en B.
3. **El panel en 2025:** el porcentaje ponderado de «buena» o «muy buena» de esas 200 personas en la EPC 2025, para comparar con A y
   B.

## 4. Lectura (fijada antes de llamar)

- **El nombre mueve la cifra** si |A − B| es de **5 puntos o más.** Sería evidencia de que la identidad del alcalde o lo que el modelo
  sabe de él pesa en la simulación.
- **Los agentes siguen su propia respuesta** si el seguimiento es de **60 puntos o más.** Es **poco** si es **menor de 40.** Entre
  40 y 60, no concluyente.
- **Valor central:** más plausible si el seguimiento es poco en A y B, y las dos cifras quedan lejos de la del panel en 2025.
- **Pesimismo con el gobernante:** más plausible si A queda por debajo de B y de la del panel en 2025.

**Nada de esto cambia la página.** B no reemplaza a A, aunque se acerque más a algún dato.

## 5. Predicciones

- **PN1.** El nombre no mueve la cifra: |A − B| < 5.
- **PN2.** Los agentes no siguen con fuerza su propia respuesta: el seguimiento en A es menor de 60.

## 6. Gasto y código

- **Gasto:** 200 llamadas de B, unos **USD 0,05**, con **tope de USD 1.**
- **Al modelo** van los perfiles de la EPC 2025 (pública, anónima) y la pregunta.
- **Código:** `src/evaluacion/alcalde_sin_nombre.py`, con `tests/test_prospectiva_epc2026.py`. Se corre después de
  `prospectiva_epc2026.py`. Resultados en `ALCALDE_SIN_NOMBRE_RESULTS.md`.
