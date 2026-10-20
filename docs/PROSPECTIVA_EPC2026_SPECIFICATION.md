# PLAN V5, PASO 2: PRUEBA HACIA ADELANTE CON LA EPC 2026

Pre-registro escrito el **20 de octubre de 2026**, antes de llamar al modelo y antes de que exista la EPC 2026. Sigue
`PLAN_SIGUIENTE_PREDICTOR_BOGOTA_V5.md` §4. Lo pidió Daniel. Gasto: **unos USD 0,30, con tope de USD 1.**

## 1. Por qué esta prueba

Todas las pruebas anteriores fueron hacia atrás: el modelo podía saber qué pasó. **Esta es la primera hacia adelante:** las
predicciones se congelan hoy, se suben a GitHub con fecha y se comparan con la EPC 2026 cuando salga (se espera en diciembre). Es
la que puede decir si los agentes anticipan algo que nadie sabe todavía.

## 2. Las preguntas (7)

| Variable | Pregunta | Lo que se cuenta |
|---|---|---|
| `GG3_GALAN` | gestión del alcalde Galán | buena o muy buena |
| `AG1` | ¿Bogotá va por buen camino? | buen camino |
| `GG7` | la corrupción en la ciudad | ha aumentado algo o mucho |
| `CC5A_GALAN` | gestión del Concejo | buena o muy buena |
| `MICE1_GALAN` | transparencia del gobierno | 4 o 5 de 5 |
| `MICE2_GALAN` | respuesta a la ciudadanía | 4 o 5 de 5 |
| `MICE3_GALAN` | participación | 4 o 5 de 5 |

## 3. Los métodos

- **P, persistencia:** el porcentaje de la EPC 2025 (`persistencia_epc.cifras(2025)`), ponderado.
- **G, agentes (la principal):** el método de la Fase B y de la réplica del alcalde, para que lo de 2026 se pueda comparar con esas
  pruebas.
  - Los 200 agentes de la página (EPC 2025, semilla 20261018), con sus pesos.
  - `openai/gpt-6-luna`, temperatura 1, razonamiento bajo.
  - Una llamada por agente con las 7 preguntas y la nota «las respuestas de arriba son de 2025; estas preguntas son de finales de
    2026…».
  - Es el único método que sirve para las 7: el de la página solo acepta escalas de 5 opciones, y el rumbo tiene 2.
- **Página (secundaria):** lo que ve quien usa la página, en las 4 preguntas que la página responde solo con agentes (`GG3_GALAN`,
  `MICE1-3_GALAN`): `Agentes.estimar`, con el texto que nombra al alcalde y sin nota.

**Lo que se declara del perfil:** el perfil de 2025 ya lleva lo que cada persona respondió ese año a estas mismas preguntas. Lo que
se mide es si los agentes mueven esa respuesta en la dirección en que se mueve la opinión.

## 4. Lo que se congela

En `config/prospectiva_epc2026/`, subido en el mismo día:
- `predicciones.csv`: por pregunta, el texto que vieron los agentes, lo que se cuenta, P, G y la cifra de la página.
- `congelado.json`: fecha y hora, modelo, temperatura, razonamiento, semilla, las 200 personas, la nota, la huella (sha256) del
  mensaje de sistema y de los perfiles, y el gasto.

**No se vuelve a correr ni se edita.** El código se niega a correr si ya existe. No se añaden noticias, variantes ni se eligen
agentes. Estas predicciones son de un experimento: no cambian la regla de la página de no guardar las consultas.

## 5. Qué preguntas cuentan en diciembre

**Antes de calcular ningún porcentaje de 2026,** se revisa el cuestionario o el diccionario de la EPC 2026. Una pregunta entra si:
- está en la EPC 2026;
- pregunta lo mismo: se aceptan cambios de redacción menores, no de concepto. Para el alcalde y el gobierno, tiene que seguir siendo
  Galán;
- tiene las mismas opciones, con el mismo número y las mismas etiquetas, para que «lo que se cuenta» sea igual.

**Si una pregunta no cumple, sale, y se anota por qué.** Si quedan menos de 4, se informa por pregunta, sin aplicar las reglas.

**El dato real de 2026** se calcula con el mismo código que el de 2025 (`persistencia_epc.cifras`), ponderado, una vez que la EPC
2026 esté armonizada.

## 6. Reglas (escritas antes de llamar)

**Los agentes ganan solo si cumplen las dos:**
- **RV1, mejora general:** su error medio en las preguntas que cuentan es **al menos 1 punto menor que el de la persistencia.**
- **RV2, robustez:** la mejora de al menos 1 punto **se mantiene sin la pregunta del alcalde.**

**Siempre se publica:** el error y el sesgo de cada pregunta, cuántas gana cada método y cuáles salieron, sin escoger casos.

**Si los agentes ganan solo en el alcalde,** el informe dice, textual:

> Los agentes superaron a la persistencia en la pregunta sobre la gestión del alcalde, pero no demostraron una mejora general en
> las preguntas de gobierno evaluadas. El resultado es específico de esa pregunta y necesita replicación.

**Las mismas reglas** se aplican a la secundaria (la página) en sus preguntas que cuenten, solo de forma descriptiva.

**No se cambian las reglas después de ver el resultado,** aunque la cifra de Galán resulte llamativa.

## 7. Predicciones

- **PP1.** Los agentes no ganan: RV1 o RV2 no se cumplen.
- **PP2.** La cifra de los agentes para el alcalde queda entre 25 y 35 %, cerca del valor central de las pruebas anteriores (25, 31
  y 29).

## 8. Lo que esta prueba no elimina

- **El modelo sabe cosas de 2026** hasta su fecha de corte. No sabe el resultado de la EPC 2026, que no existe todavía: esa es la
  filtración que esta prueba evita.
- **Es un solo año** y unas 7 preguntas: si gana, hará falta replicarlo.

## 9. Gasto y código

- **Gasto:** 200 llamadas de G y 800 de la página, unos **USD 0,30**, con **tope de USD 1.**
- **Al modelo** van los perfiles de la EPC 2025 (pública, anónima) y las preguntas. Nada de las encuestas propias.
- **Código:** `src/evaluacion/prospectiva_epc2026.py` (congelar ahora y `evaluar` en diciembre), con
  `tests/test_prospectiva_epc2026.py`. Resultados en `PROSPECTIVA_EPC2026_RESULTS.md` cuando salga la EPC 2026.
