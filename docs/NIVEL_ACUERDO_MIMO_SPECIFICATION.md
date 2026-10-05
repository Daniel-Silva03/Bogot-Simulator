# ¿ESTARÍA BOGOTÁ DE ACUERDO? — ¿alcanza con mimo, el modelo de la página?

Pre-registro escrito el **5 de octubre de 2026**, antes de hacer ninguna llamada. Gasto: **~USD 0,85,
con tope de USD 1,50**, aprobado por Daniel.

## 1. Pregunta

La estimación de D19 usa Claude Sonnet 5.5 (~USD 0,02 por pregunta). **¿Logra lo mismo
`xiaomi/mimo-v2.6-pro`**, el modelo que ya usa la página para la reformulación y el puente (~USD 0,005)?
- Si sí, la página queda con un solo modelo y unas 4 veces más barata.
- Si no, sigue Sonnet.

## 2. Datos y método

**Los mismos dos conjuntos de Sonnet, con el mismo método.** Solo cambia el modelo.
- **Práctica:** las 92 preguntas de acuerdo o sí/no (`nivel_acuerdo.tabla()`). Cada una con candidatas
  de otras familias, como en `NIVEL_ACUERDO_SONNET_SPECIFICATION.md`.
- **Guardado:** las 74 de `NIVEL_ACUERDO_VALIDACION_SPECIFICATION.md`. Las candidatas son las 92 de
  práctica.
- **Igual que con Sonnet:** `nivel_parecidas_b.SISTEMA`, `prompt`, `parsear`, el reintento y el fallo;
  temperatura 0; una llamada por pregunta.
- **Caché:** `data/processed/banco/cache_nivel_acuerdo_mimo.json`, que no se sube.

**El rango de mimo se fija como se fijó el de Sonnet:**
- en la práctica, con los errores de mimo en las otras familias;
- en el guardado, **h fijo = cuantil 80 % del error de mimo en las 92 de práctica**, calculado al
  terminar la práctica y antes de evaluar el guardado.

## 3. Regla (escrita antes de llamar)

**mimo puede reemplazar a Sonnet en la página si cumple, en los dos conjuntos, las mismas condiciones
que cumplió Sonnet:**
- **práctica:** EAM ≤ 15,8 y acierto del lado ≥ 67 %;
- **guardado:** EAM ≤ 15,8, acierto del lado ≥ 67 % y ≥ la referencia fija + 10 puntos;
- **las dos juntas:** al decidir («probablemente sí/no»), acierta al menos el 90 %.

**Si cumple:** se le propone a Daniel el cambio, con las cifras de los dos modelos lado a lado.
**Si no cumple:** sigue Sonnet, y se puede probar otro modelo barato (Gemini 3.8 Flash), también
pre-registrado.

**Un límite que se declara antes de correr:** los dos conjuntos ya se usaron para validar a Sonnet.
Aunque no se usaron para ajustar nada de mimo, que pase en ellos es algo menos fuerte que la validación
de Sonnet.

## 4. Predicciones (escritas antes de llamar)

- **P1.** mimo **no** cumple la regla.
- **P2.** Su EAM en la práctica es mayor que el de Sonnet (13,9).
- **P3.** Acierta el lado en la práctica menos que Sonnet (80 %).
- **P4.** Tiene al menos una respuesta inválida (fallo) en los 166 casos.

## 5. Gasto

166 llamadas a ~USD 0,005: **~USD 0,85**. Antes, una llamada de prueba, cuyo costo se le confirma a
Daniel. **Tope: USD 1,50**; el código se detiene solo.

## 6. Código

`src/experiments/nivel_acuerdo_mimo.py`, con pruebas en `tests/test_nivel_acuerdo_mimo.py`. Los
resultados van a `NIVEL_ACUERDO_MIMO_RESULTS.md`, contra este pre-registro.
