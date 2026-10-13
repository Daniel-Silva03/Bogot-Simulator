# TINYTROUPE CON RESIDENTES DE BOGOTÁ — resultados

Corrido el **13 de octubre de 2026** contra `TINYTROUPE_RESIDENTES_SPECIFICATION.md` (pre-registro en `7f53ca7` y enmienda 1
en `728963e`, antes de llamar).
- **Gasto: USD 0,46**, dentro del tope de USD 1: A, USD 0,053; B, USD 0,397; dos intentos fallidos de B, USD 0,005.
- **Las respuestas** quedan en `data/processed/tinytroupe/`, sin subir.

**Una advertencia antes de las cifras (DI-TT5):** un error mío unió con espacios las letras de cada respuesta, y el script
dejó las cinco preguntas sin cifra. Lo dicho por cada agente se guardó completo y se recuperó sin volver a llamar al modelo.
Las cifras de abajo salen de esa lectura corregida.

## 1. Resultados

| Pregunta | EPC 2025 | TinyTroupe A (12 residentes) | TinyTroupe B (24 de la fábrica) | MiroFish | Simulador |
|---|---|---|---|---|---|
| Satisfecho con Bogotá | 61 % | 50,5 % (6 sí, 6 no) | 58,3 % (14 sí, 10 no) | 72,1 % | 51,2 % |
| Orgulloso | 57 % | 100 % | 100 % | 100 % | 48,7 % |
| Buen camino | 59 % | 8,7 % (1 sí) | 0 % | 0 % | 33,3 % |
| Aprueba a Galán | 26 % | 8,7 % (1 sí) | 0 % | 0 % | 47,3 % |
| Víctima de delito | 15 % | 0 % | 0 % | 0 % | 25,3 % |
| **Error medio** | | **27,2** | **29,1** | 30,8 | **15,1** |
| **Spearman** | | 0,62 | 0,45 | 0,45 | 0,70 |
| **Separación** | | 100 | 100 | 100 | 25,9 |

Todos respondieron con un «sí» o un «no» legible.

## 2. Contra la regla (§4)

| | Criterio | A | B |
|---|---|---|---|
| R1 | Spearman ≥ 0,7 | 0,62: **no** | 0,45: **no** |
| R2 | Separación ≥ 20 | 100: sí | 100: sí |
| R3 | Error < 17,2 | 27,2: **no** | 29,1: **no** |

**Ninguna variante de TinyTroupe distingue.**

| | Predicción | Resultado | |
|---|---|---|---|
| PT1 | No cumple la regla | no la cumple (A ni B) | se cumple |
| PT2 | Se equivoca más que el simulador | 27,2 y 29,1 contra 15,1 | se cumple |
| PT3 | Sobre Galán, la mayoría se niega a opinar | nadie se negó: 11 de 12 y 24 de 24 dijeron «no» | **falla** |
| PT4 | B se equivoca menos que A | 29,1 contra 27,2 | **falla** |

## 3. Qué se aprende

1. **TinyTroupe sí hace de encuestado, a diferencia de MiroFish.** Nadie dijo «no tengo información». Los residentes dan
   razones concretas: «el transporte está caro y la inseguridad preocupa». Ahí falla PT3.
2. **Pero opinan en bloque.** Casi todos están orgullosos y casi ninguno aprueba al alcalde ni cree que la ciudad vaya bien.
   Es la queja «de sentido común» de un bogotano imaginado, no la distribución real. En 2025, el 59 % dijo que Bogotá iba
   por buen camino, y TinyTroupe dio 0 % a 9 %.
3. **Nadie fue víctima de un delito,** en ninguna herramienta. El modelo no se inventa un robo si el perfil no lo trae; en
   la realidad es el 15 %.
4. **Lo único que varió fue la satisfacción, y con el estereotipo.** En A dicen «no» los de estrato 1 y 2, salvo uno, y
   «sí» los de estrato 3 a 6, salvo uno. Esa pregunta es la que más se acerca al real: 50,5 % y 58,3 % contra 61 %.
5. **La fábrica no ayudó.** Siguió la demografía (14 mujeres y 10 hombres; estratos 2 y 3 en mayoría), pero inventó oficios
   casi iguales para todos: auxiliares administrativas, contadores, coordinadores de bodega. Ningún vendedor informal,
   estudiante ni conductor. Con biografías más ricas, las respuestas fueron aún más uniformes: 24 de 24 en cuatro de las
   cinco preguntas.
6. **El veredicto de las cinco pruebas es el mismo:** las herramientas de personas sintéticas no reproducen la opinión de
   Bogotá. El propio Microsoft lo advierte: TinyTroupe «HAS NOT been shown to match real human behavior». Lo que ordena
   bien las preguntas es lo medido: el simulador, con respuestas reales de 2022-2024.

## 4. Lo que pasó en las corridas (DI-TT4, DI-TT5)

- **Faltaba `IPython`:** A falló sin gastar al primer intento.
- **La fábrica se cortaba** con un tope de 4.000 tokens. Se subió a 16.000, cifra que el pre-registro no fijaba.
- **El error de lectura (DI-TT5)** se corrigió en el código, con su prueba.
