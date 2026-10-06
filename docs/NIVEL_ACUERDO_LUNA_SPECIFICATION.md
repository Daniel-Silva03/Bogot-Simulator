# ¿ESTARÍA BOGOTÁ DE ACUERDO? — ¿alcanza con GPT-6 Luna?

Pre-registro escrito el **6 de octubre de 2026**, antes de hacer ninguna llamada. Gasto: **~USD 0,25,
con tope de USD 0,75**. Lo aprobó Daniel, a pedido de su jefe, para bajar el costo.

## 1. Pregunta

La estimación de D19 usa Claude Sonnet 5.5, a unos USD 0,024 por pregunta nueva. **¿Logra lo mismo
`openai/gpt-6-luna`?** Cuesta USD 0,10 por millón de tokens de entrada y USD 0,50 por millón de salida, unas 18 veces
menos (~USD 0,0013 por pregunta).
- **Si sí,** reemplaza a Sonnet en la página.
- **Si no,** sigue Sonnet, y la página sigue costando lo de hoy.

**Lo que ya se sabe.** mimo (`NIVEL_ACUERDO_MIMO_RESULTS.md`), seis veces más barato que Sonnet, no cumplió la regla:
- error de 16,2 en la práctica;
- 86 % al decidir.

## 2. Datos y método

**Solo cambia el modelo.** Las instrucciones, el prompt y la lectura de las respuestas son los mismos: `nivel_parecidas_b`
(`SISTEMA`, `prompt` y `parsear`, con DI-NB6), con un reintento y la misma regla de fallo. Temperatura 0 y una llamada
por pregunta (más el reintento).

**Los conjuntos:**
- **Práctica:** las 92 preguntas de acuerdo o sí/no (`nivel_acuerdo.tabla()`). Las candidatas de cada una son
  las de otras familias. Es la misma práctica de Sonnet (`NIVEL_ACUERDO_SONNET`) y de mimo.
- **Guardado:** las 95 de la prueba del lote 5 (`nivel_acuerdo_lote5.objetivos()`), con las **109 candidatas
  de la página** (configuración B). Es lo mismo que validó a Sonnet en su configuración actual:
  - EAM 11,9;
  - lado 72 %;
  - 17 de 17 al decidir;
  - referencia fija 54 %.

**Caché:** `data/processed/banco/cache_nivel_acuerdo_luna.json`, que no se sube.

**El rango de Luna se fija como se fijó el de Sonnet:**
- **en la práctica:** con los errores de Luna en las otras familias;
- **en el guardado:** h fijo, igual al cuantil 80 % del error de Luna en las 92 de práctica. Se calcula al terminar la
  práctica y antes de evaluar el guardado.

## 3. Regla (escrita antes de llamar)

**Luna puede reemplazar a Sonnet en la página si cumple las cuatro condiciones.** Las tres primeras son las que cumplió Sonnet:
1. **práctica:** EAM ≤ 15,8 y acierto del lado ≥ 67 %;
2. **guardado:** EAM ≤ 15,8, y acierto del lado ≥ 67 % y ≥ referencia fija + 10 puntos (`nivel_acuerdo_validacion.evaluar`);
3. **las dos juntas:** al decir «probablemente sí» o «no», acierta al menos el 90 %;
4. **condición nueva frente a la regla de mimo:** en el guardado, su EAM no supera en más de 1,5 al de Sonnet (11,9, así que
   ≤ 13,4).

La cuarta condición está porque la página no debe perder precisión de forma apreciable solo por ahorrar.
Con ella, mimo tampoco habría pasado (13,5 en su guardado de 74).

**Si cumple:** se le propone a Daniel el cambio, con las cifras de los dos modelos lado a lado.
- **Si lo aprueba,** cambian dos cosas de la página:
  - el texto, que citaría las cifras de Luna en el guardado;
  - el rango, que sería el h de Luna.
- **Además,** la parte A de `NIVEL_ACUERDO_REDACCION` se termina con Luna, que sería el modelo de la página. Ese cambio se
  pre-registra como enmienda.

**Si no cumple:** sigue Sonnet.

**Un límite que se declara antes de correr:** los dos conjuntos ya se usaron para validar a Sonnet y a mimo. No se
usaron para ajustar nada de Luna, pero que pase en ellos es algo menos fuerte que una validación con preguntas nuevas.

## 4. Predicciones (escritas antes de llamar)

- **P1.** Luna **no** cumple la regla.
- **P2.** Su EAM en la práctica es mayor que el de Sonnet (13,9).
- **P3.** Acierta el lado de la mayoría en la práctica menos que Sonnet (80 %).
- **P4.** Tiene al menos una respuesta inválida (fallo) en los 187 casos.

## 5. Gasto

**187 llamadas a ~USD 0,0013, más los reintentos: ~USD 0,25.**
- **Antes de correr,** una llamada de prueba, cuyo costo se le confirma a Daniel.
- **Tope: USD 0,75.** El código se detiene solo, y un error del servicio (sin saldo, sin red) también lo detiene.

## 6. Código

- **Código:** `src/experiments/nivel_acuerdo_luna.py`.
- **Pruebas:** `tests/test_nivel_acuerdo_luna.py`.
- **Resultados:** `NIVEL_ACUERDO_LUNA_RESULTS.md`, contra este pre-registro.
