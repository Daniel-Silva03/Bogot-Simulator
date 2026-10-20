# ¿PASA LO MISMO CON EXPECTED PARROT?

Pre-registro escrito el **20 de octubre de 2026**, antes de llamar a ningún modelo con EDSL. Lo pidió Daniel, por sugerencia de su
jefe: «usémoslo porque no hay de otra, es demostrar qué pasa». Gasto: **unos USD 1,5, con tope de USD 2.**

## 1. La pregunta

Expected Parrot (EDSL, su librería de Python de código abierto) arma encuestas que responden agentes simulados con modelos de
lenguaje. Es lo mismo que hace nuestra página, con otra infraestructura. **¿Da lo mismo? ¿Y un modelo más fuerte ve lo que el
nuestro no ve?**

## 2. Las corridas

| Corrida | Perfiles | Modelo | Pregunta |
|---|---|---|---|
| **A** | los 200 de la página, EPC 2025 | `openai/gpt-6-luna` (el nuestro) | gestión de Galán, con el texto de la página |
| **B-luna** | los 200 de 2024 | `openai/gpt-6-luna` | la misma, con una nota de fecha |
| **B-sonnet** | los 200 de 2024 | `anthropic/claude-sonnet-5.5` | la misma, con la nota |
| **B-gemini** | los 200 de 2024 | `google/gemini-4-argon` | la misma, con la nota |

- **A busca equivalencia:** la página, con los mismos perfiles y el mismo modelo, dio **27,2 %** (`ALCALDE_SIN_NOMBRE`, condición A).
- **B es el caso que más importa:** con los perfiles de 2024, predecir Galán 2025, cuando cayó de **42,3 % a 26,4 %**.
  - Repetir el dato dijo 42,3 (error de 15,9).
  - Nuestros agentes, en la Fase B, dijeron 29,3 (error de 2,9).
- **La nota de B:** «Lo que sabes de esta persona es de 2024. Esta pregunta es de finales de 2025, casi un año después: la persona
  puede haber cambiado de opinión». Es la misma idea que la nota de la Fase B, adaptada a EDSL, donde el perfil no va «arriba» sino
  en el mensaje de sistema.
- **Los modelos fuertes** son los más recientes de Anthropic y de Google en OpenRouter el 20/10/2026, de precio parecido (USD 2 por
  millón de tokens de entrada y USD 10 de salida). El nuestro cuesta 20 veces menos.

## 3. Cómo se usa EDSL

**Todo en local:**
- EDSL 1.0.9, en un ambiente aparte (`venv_edsl`, fuera de Git).
- Llama a OpenRouter con nuestra clave, con la inferencia y la caché remotas desactivadas.
- **Nada pasa por los servidores de Expected Parrot.**

**A la manera de EDSL, no copiando la página:**
- **Cada agente** es un `Agent` cuyo único rasgo es el perfil completo de la página: sexo, edad, estrato, localidad y sus unas 40
  respuestas a la EPC. Lleva la misma instrucción que la página («Vas a responder una encuesta como una persona real de Bogotá…»).
- **La pregunta** es `QuestionMultipleChoice`, sin comentario: **cada agente elige una opción**, que es la forma propia de EDSL. La
  página, en cambio, pide la probabilidad de cada opción.
- **EDSL agrega al mensaje su propia instrucción, en inglés:** «Only 1 option may be selected. Respond only with a string
  corresponding to one of the options.».
- **Temperatura 1;** el razonamiento es el que EDSL use por defecto para cada modelo.

**La cifra:** el porcentaje ponderado (peso de la encuesta) de «Buena gestión» o «Muy buena gestión» entre los agentes que eligieron
una opción válida.

## 4. Lo que se declara antes de correr

- **Elegir una opción tiene más ruido que dar probabilidades.** Con 200 personas, el azar de elegir mueve la cifra unos ±6 puntos.
  Por eso la tolerancia de A es de 7.
- **B es un solo caso y ya se conoce el resultado:** el 26,4 % de 2025 se publicó en diciembre de 2025, y los modelos pueden haberlo
  aprendido. **Un modelo fuerte que «vea la caída» puede estar recordándola,** no deduciéndola del perfil. Esto pesa más en los
  modelos más recientes.
- **El perfil de 2024 trae lo que cada persona respondió sobre Galán en 2024.**

## 5. Lectura (fijada antes de llamar)

- **RA, equivalencia:** EDSL da lo mismo que la página si |A − 27,2| ≤ 7.
- **RB, la caída:** un modelo «ve la caída» si su cifra queda **por debajo de 34,35**, el punto medio entre la persistencia (42,3) y
  lo real (26,4). Se informa su error, y si le gana a repetir el dato.
- **RC, ¿un modelo mejor?:** un modelo fuerte es mejor que el nuestro si su error en B es **al menos 3 puntos menor** que el de
  B-luna.

**Qué se concluye:**
- **Si RA se cumple y ningún modelo fuerte cumple RC,** la herramienta y el modelo no cambian lo que sabemos: el límite es la
  información que les falta a los agentes, no la infraestructura.
- **Si un modelo fuerte cumple RC,** se informa como hallazgo exploratorio de un solo caso, con el aviso de §4. No cambia el modelo
  de la página ni las predicciones congeladas para la EPC 2026.
- **Si RA no se cumple,** EDSL y la página no son equivalentes. Se informa en qué difieren: elegir contra probabilidades, la
  instrucción en inglés y dónde va el perfil.

## 6. Predicciones

- **PX1.** RA se cumple: EDSL da lo mismo que la página.
- **PX2.** Al menos 2 de los 3 modelos ven la caída en B.

## 7. Gasto y código

- **Gasto:** 800 llamadas.
  - las dos de luna, unos USD 0,05;
  - cada modelo fuerte, unos USD 0,70.

  En total, **unos USD 1,5, con tope de USD 2**, revisado cada 50 agentes; si se llega a él, la corrida queda incompleta y se informa así.
- **Al modelo** van los perfiles de la EPC 2024 y 2025 (pública, anónima) y la pregunta. Nada de las encuestas propias.
- **Código:** `src/evaluacion/expected_parrot.py`, en tres pasos:
  - `exportar`, con el venv del proyecto;
  - `correr`, con `venv_edsl`;
  - `evaluar`, con el venv del proyecto.

  Las pruebas están en `tests/test_expected_parrot.py`. Resultados en `EXPECTED_PARROT_RESULTS.md`.

## Enmienda 1 (20 de octubre de 2026, antes de correr nada): solo modelos baratos

Daniel pidió usar modelos baratos. **Se cambia antes de llamar a ningún modelo:**
- **En B, los modelos fuertes** (Claude Sonnet 5.5 y Gemini 4 Argon) **se reemplazan por tres baratos de otras empresas:**

  | Modelo | Empresa | Entrada / salida, USD por millón de tokens |
  |---|---|---|
  | `anthropic/claude-haiku-5.5` | Anthropic | 0,10 / 0,50 (igual que el nuestro) |
  | `google/gemini-3.5-flash-lite` | Google | 0,30 / 2,50 |
  | `deepseek/deepseek-v4.1-flash` | DeepSeek | 0,03 / 0,12 |

  B queda con 4 corridas: la nuestra y estas tres.
- **RC** pasa a ser: otro modelo es mejor que el nuestro si su error en B es al menos 3 puntos menor que el de B-luna.
- **PX2** queda igual: al menos 2 de los modelos ven la caída (ahora de 4).
- **Gasto:** 1.000 llamadas, **unos USD 0,20, con tope de USD 0,50.**

**Lo que se pierde:** la prueba ya no responde si un modelo **más capaz** ve lo que el nuestro no ve. Solo responde si otras
empresas, con modelos del mismo nivel, dan lo mismo.
