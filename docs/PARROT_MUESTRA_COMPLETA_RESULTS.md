# EXPECTED PARROT CON TODA LA MUESTRA — resultados (parciales: se llegó al tope)

Corrido el **20 de octubre de 2026** contra `PARROT_MUESTRA_COMPLETA_SPECIFICATION.md` (pre-registro y código en `d4a37ac`, antes de
llamar al modelo). **Gasto: USD 1,03.** Se llegó al tope de USD 1 a mitad de T2.

## Lo que corrió

| Corrida | Agentes | Predicción | Repetir el dato | Real | Error de los agentes | Error de repetir |
|---|---|---|---|---|---|---|
| **T0**, López 2023 (perfiles 2022) | 1.500 de 1.500 | 26,2 | 33,1 | 31,1 | 4,9 | **2,0** |
| **T1**, Galán 2024 (perfiles 2023) | 1.501 de 1.501 | 20,3 | 31,1 | 42,3 | 22,0 | **11,2** |
| **T2**, Galán 2025 (perfiles 2024) | **500 de 1.521** | 33,4 | 42,3 | 26,4 | **7,0** | 15,9 |
| **F**, Galán 2026 (perfiles 2025) | **no corrió** | — | 26,4 | — | — | — |

**T2 quedó incompleta:** son las primeras 500 personas del archivo, no una muestra al azar. Cubren las 19 localidades, pero su cifra
se lee con cuidado. **F no corrió, y no se congeló nada para 2026.**

## Por qué se pasó el costo

Se estimaron USD 0,40; se gastó el tope (USD 1,03) antes de terminar. Hay dos causas:
- **Los perfiles de 2022 y 2023 son mucho más largos** (6.900 y 8.700 caracteres en promedio) que los de 2025 (4.500), porque esas
  olas tienen más preguntas del catálogo.
- **La estimación salió del costo por corrida de `EXPECTED_PARROT`, que estaba mal medido.** OpenRouter registra el consumo con
  retraso, así que lo de una corrida se cargaba a la siguiente. El total de esa prueba sí era el real, pero no el reparto: por
  ejemplo, el costo alto que se atribuyó a DeepSeek no es confiable.

Con lo que costó T0 (USD 0,25 por cada 1.000 agentes), la prueba completa habría costado unos USD 1,6.

## Lectura pre-registrada

| | Criterio | Resultado | |
|---|---|---|---|
| RT1 | Los agentes ganan en al menos 2 de 3 | pierden en T0 y en T1 | **no se cumple** |
| RT2 | Su error medio, al menos 1 punto menor | 11,3 contra 9,7, con T2 parcial | **no se cumple** |
| RT3 | Cuántas se mueven en el sentido correcto | 2 de 3 (T0 y T2) | |

**El resultado no depende de T2.** Con T0 y T1 los agentes ya pierden dos veces, así que RT1 no se puede cumplir. Y para cumplir RT2
tendrían que acertar T2 con un error negativo, que no existe. **Los agentes no aportan.**

## Predicciones

| | Predicción | Resultado | |
|---|---|---|---|
| PM1 | Los agentes no aportan | no aportan | se cumple |
| PM2 | En T2 dicen 34,35 % o más | 33,4 (con 500) | **falla, por poco** |

## Lo que se ve, más allá de las reglas (no pre-registrado)

**Con toda la muestra, los agentes bajan al alcalde de turno** desde el dato anterior, sin importar lo que pasó:

| | Dato anterior | Agentes | Cambio de los agentes | Cambio real |
|---|---|---|---|---|
| López 2022 → 2023 | 33,1 | 26,2 | **−6,9** | −2,0 |
| Galán llega, 2023 → 2024 | 31,1 | 20,3 | **−10,8** | +11,2 |
| Galán 2024 → 2025 | 42,3 | 33,4 | **−8,9** | −15,9 |

- **Siempre bajan entre 7 y 11 puntos.** Cuando la opinión real bajó (2025), parece que «ven la caída»; cuando subió (2024), se
  equivocan el doble que repetir el dato.
- **Esto es la lectura de «pesimismo con el gobernante»** que el diagnóstico del alcalde sin nombre había descartado. La diferencia
  es la forma de preguntar: aquí cada agente elige una opción con EDSL, y lleva la nota de fecha; allá eran probabilidades, sin
  nota. No se sabe cuál de las dos cosas lo produce.
- **Con el panel de 200,** el azar de la muestra tapaba este patrón (`EXPECTED_PARROT_RESULTS.md`).

## Qué se aprende

1. **Sin el azar de la muestra, los agentes no le ganan a repetir el dato en el alcalde.** En los dos años completos pierden, y en
   2024 por mucho.
2. **El «acierto» de 2025 queda explicado dos veces:** con 200, por el azar del panel; con toda la muestra, por una tendencia
   general a bajar al alcalde que en 2025 coincidió con la caída real.
3. **Para la prueba de diciembre:** las cifras ya congeladas (agentes 27,3, panel de expertos 31,3, repetir el dato 26,4) siguen
   igual. Los agentes congelados usan probabilidades y no muestran esta bajada (27,3 contra 26,4): la tendencia aparece con la
   forma de preguntar de EDSL, y no se sabe todavía si es por elegir una opción o por otra cosa.
4. **Lo pendiente:** terminar T2 (unos USD 0,25) y correr F para congelarlo (unos USD 0,40). Necesita un nuevo visto bueno de
   Daniel, porque supera el tope.
