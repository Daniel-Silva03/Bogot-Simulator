# ¿ESTARÍA BOGOTÁ DE ACUERDO? — ¿mejora la estimación si el catálogo entra a las candidatas?: resultados

Corrido el **14 de octubre de 2026** contra `NIVEL_ACUERDO_CATALOGO_SPECIFICATION.md`:
- pre-registro y código en `704f1be`, antes de llamar;
- **comando:** `python src/experiments/nivel_acuerdo_catalogo.py`;
- **gasto:** USD 0,277 con la llamada de prueba, dentro del tope de USD 0,80.

En el total solo van cifras de error y acierto, porque incluye preguntas del CNC (D21). Las del lote 8 son públicas y van
pregunta por pregunta en §3.

## 1. Resultado

| En los 139 objetivos | C: 139 candidatas (la página hasta hoy) | **E: 223, con las 84 del catálogo** | Regla |
|---|---|---|---|
| Error (EAM) | 15,6 | **15,3** | E ≤ 15,8 y E ≤ C: **cumple** |
| Acierto del lado | 70 % | **73 %** | ≥ 67 % y ≥ 49 % + 10: **cumple** |
| Decide («probablemente») | 11 (8 %) | **14 (10 %)** | |
| Acierta al decidir | 10 de 11 (91 %) | **13 de 14 (93 %)** | ≥ 90 %: **cumple** |

| Por grupo | C | E |
|---|---|---|
| Las 10 del lote 8 (EPC 2025): EAM / lado | 25,9 / 60 % | **14,2 / 70 %** |
| Las 129 de siempre: EAM / lado | 14,8 / 71 % | 15,4 / 73 % |
| Los 139 sin las 3 cercanas al catálogo: EAM | 15,7 | 15,4 |

**Por la regla (§4), E reemplaza a C.** La página estima con las 223 candidatas (DI-CO39).

## 2. Contra el pre-registro

| | Predicción | Resultado | |
|---|---|---|---|
| P1 | E reemplaza a C (las tres condiciones) | se cumplen las tres | se cumple |
| P2 | En las del lote 8, el EAM de E baja de 20 | 14,2 | se cumple |
| P3 | En las 129, E a menos de 1 punto de C | 15,4 contra 14,8 (0,6) | se cumple |
| P4 | E decide en más preguntas que C | 14 contra 11 | se cumple |

## 3. Las 10 de la EPC 2025, pregunta por pregunta

Porcentaje del lado favorable:

| Pregunta | Real | C | E | E se apoyó en |
|---|---|---|---|---|
| Confía en la Alcaldía | 19,1 | 53,2 | **31,6** | gestión de Galán, respuesta a la ciudadanía, una de la Encuesta Distrital |
| Confía en el Concejo | 13,4 | 53,2 | **19,6** | imagen y gestión del Concejo |
| Confía en el Congreso | 9,8 | 53,2 | **30,5** | gestión del Concejo y de Galán, imagen del Concejo |
| Confía en el Gobierno Nacional | 18,3 | 49,0 | **31,6** | gestión de Galán, respuesta a la ciudadanía |
| Buena gestión del Congreso | 11,8 | 38,0 | **24,8** | gestión del Concejo y de Galán |
| Satisfecho con la justicia | 19,4 | 47,3 | 51,3 | satisfacción con servicios y cultura |
| Satisfecho con el estado de las vías | 22,4 | 39,9 | **35,6** | satisfacción con andenes y semáforos |
| Confía en los servicios financieros digitales | 36,0 | 53,4 | 50,9 | Encuesta Distrital, internet |
| Confía en la inteligencia artificial | 51,5 | 53,2 | 53,4 | Encuesta Distrital, Cultura Ambiental |
| Satisfecho con el servicio de salud | 49,9 | 30,1 | 63,9 | satisfacción con los servicios públicos |

**Lo que funcionó:** en las preguntas de instituciones, Luna eligió la imagen y la gestión del Concejo y de Galán, y la cifra
bajó de unos 53 % a entre 20 % y 32 %. Siguen por encima de lo real, pero el error pasó de 30-44 a 6-21 puntos.

**Lo que no:** la justicia y la salud se apoyaron en la satisfacción con los servicios públicos, que es alta. Una
pregunta de satisfacción con algo que funciona mal sigue saliendo alta.

## 4. Lo que hay que tener en cuenta

1. **La mejora está en las preguntas de la ciudad.** En las 129 de siempre, E es 0,6 peor que C (15,4 contra 14,8). La
   regla mira las 139 juntas, y en conjunto gana E por 0,3. Es el mismo patrón de los lotes 6 y 8, pero ahora a favor.
2. **Las 10 del lote 8 tienen una ventaja que se declaró antes** (§2 del pre-registro): sus encuestados son también
   donantes de la población. Una pregunta de confianza en instituciones que venga de otra encuesta podría mejorar menos.
3. **Luna usa poco el catálogo:** eligió al menos una pregunta del catálogo en 49 de las 139, y en promedio 0,6 de sus
   hasta 5. Lo usa cuando hay una del mismo tema, que es lo que se buscaba.

## 5. Control no pre-registrado: con el rango de la página

**Se calculó después de ver §1 y no decide nada.** La prueba usó un rango fijo de ±23,4, pero la página usa uno que depende
de cuántas preguntas eligió Luna (DI-CO33). Con ese rango, en los 139:
- acierta el lado en el **73 %**;
- dice «probablemente» en **19** y acierta **17** (89 %).

Es apenas menos del 90 % de la regla, que se fijó con el rango fijo. Con la configuración anterior y el mismo rango, el
texto de la página citaba 12 de 13 en 129 preguntas. **El texto de la página cita ahora 73 % y 17 de 19**, porque son las
cifras del rango que usa.
