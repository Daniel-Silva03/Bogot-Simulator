# EXPECTED PARROT CON TODA LA MUESTRA: ¿APORTAN LOS AGENTES SIN EL AZAR DE ELEGIR 200?

Pre-registro escrito el **20 de octubre de 2026**, antes de llamar al modelo. Lo pidió Daniel («sí, arma el pre-registro de la 1 y la
2»; después: «usa luna»). Gasto: **unos USD 0,40, con tope de USD 1.**

## 1. Por qué

En `EXPECTED_PARROT_RESULTS.md` apareció, sin pre-registro, que **el panel de 200 de 2024 calificaba bien a Galán en 31,5 %,
mientras toda la EPC daba 42,3 %.** El «acierto» de los agentes en 2025 (29 %, real 26,4) partía de ahí. Si cada persona de la
encuesta es un agente, ese azar desaparece. **¿Aportan algo los agentes cuando ya no tienen esa ayuda?**

## 2. Las corridas

Todas con **toda la muestra del año base** (las personas con localidad 1-19 y peso: 1.500, 1.501, 1.521 y 1.520), con el modelo
nuestro (`openai/gpt-6-luna`) y la pregunta de la gestión del alcalde.

| Corrida | Perfiles | Pregunta | Repetir el dato (P) | Real |
|---|---|---|---|---|
| **T0** | EPC 2022 | gestión de Claudia López, finales de 2023 | 33,1 | 31,1 |
| **T1** | EPC 2023 | gestión de Galán, finales de 2024 (recién llegado) | 31,1 (López) | 42,3 |
| **T2** | EPC 2024 | gestión de Galán, finales de 2025 | 42,3 | 26,4 |
| **F** | EPC 2025 | gestión de Galán, finales de 2026 | 26,4 | aún no existe |

**P y lo real** son los de toda la EPC (`serie_epc_bcv.csv`, «buena» más «muy buena» de 5 opciones), ya usados en las pruebas
anteriores.

**La opción 2, el promedio de modelos de tres empresas, no se hace:** Daniel pidió usar solo luna. Con un solo modelo no hay qué
promediar.

## 3. Cómo se pregunta

**Igual que en `EXPECTED_PARROT`:**
- EDSL 1.0.9 en local, con nuestra clave de OpenRouter;
- cada persona es un agente cuyo único rasgo es su perfil de la página, con la instrucción de la página;
- `QuestionMultipleChoice` sin comentario: cada agente elige una opción;
- temperatura 1;
- la cifra es el porcentaje ponderado de «buena» o «muy buena».

**Dos detalles:**
- **En 2022 y 2023,** el perfil lleva la calificación del alcalde y del Concejo de ese año, como en la réplica del alcalde. Los de
  2024 y 2025 ya la traen.
- **Todas las corridas llevan la nota:** «Lo que sabes de esta persona es de {año base}. Esta pregunta es de finales de {año
  objetivo}, casi un año después: la persona puede haber cambiado de opinión».

**Con 1.500 agentes, el azar de elegir una opción** mueve la cifra unos ±2,5 puntos, no ±6 como con 200.

## 4. Lo que se declara antes de correr

- **Lo real de T0, T1 y T2 ya se conoce,** y el modelo puede haberlo aprendido.
- **Ya se vio que los agentes repiten la respuesta de su persona** cuando el perfil trae la pregunta (`ALCALDE_SIN_NOMBRE`). Con
  toda la muestra, eso equivale a repetir el dato. Esta prueba mide si se mueven desde ahí y hacia dónde.
- **T2 ya se corrió con 200 agentes,** con el mismo modelo, y dio 29,0.
- **F se congela** para la EPC 2026 en `config/prospectiva_epc2026/parrot_muestra_completa.json`, junto a lo ya congelado. No se
  vuelve a correr.

## 5. Lectura (fijada antes de llamar)

**En T0, T1 y T2:**
- **RT1:** los agentes se equivocan menos que repetir el dato **en al menos 2 de las 3.**
- **RT2:** su error medio es **al menos 1 punto menor** que el de repetir el dato.
- **RT3** (descriptivo): en cuántas se mueven **en el sentido correcto** desde el dato anterior (bajan si la opinión bajó, suben si
  subió).

**Los agentes «aportan» si cumplen RT1 y RT2.**
- **Si aportan:** es la primera señal, sin el azar de la muestra, de que leen algo. Se informa como exploratorio, por la posible
  memoria del modelo (§4), y la prueba que lo confirma es F en diciembre.
- **Si no aportan:** queda demostrado que, sin el azar del panel de 200, los agentes no le ganan a repetir el dato en el alcalde.

**F se evalúa en diciembre** contra la EPC 2026, como una pregunta más, de forma descriptiva. Con un solo caso no se declara
victoria (la frase de `PROSPECTIVA_EPC2026_SPECIFICATION.md` §6).

## 6. Predicciones

- **PM1.** Los agentes no aportan: no cumplen RT1 y RT2.
- **PM2.** En T2, con toda la muestra, los agentes dicen 34,35 % o más: no ven la caída de Galán.

## 7. Gasto y código

- **Gasto:** unas 6.000 llamadas con luna, **unos USD 0,40**, con **tope de USD 1.** Se revisa cada 250 agentes con lo que OpenRouter
  dice que gastó nuestra clave.
- **Al modelo** van los perfiles de la EPC 2022 a 2025 (pública, anónima) y la pregunta. Nada de las encuestas propias.
- **Código:** `src/evaluacion/parrot_muestra_completa.py`, en los tres pasos de `expected_parrot.py`, con
  `tests/test_parrot_muestra_completa.py`. Resultados en `PARROT_MUESTRA_COMPLETA_RESULTS.md`.
