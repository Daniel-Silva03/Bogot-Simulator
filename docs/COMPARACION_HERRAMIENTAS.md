# COMPARACIÓN: MIROFISH, TINYTROUPE Y EL SIMULADOR

**Tres formas de simular la opinión de Bogotá, probadas con las mismas preguntas.**

Proyecto: Bogotá Social Simulator
Fecha: 13 de octubre de 2026
Fuentes: `MIROFISH_*_RESULTS.md`, `TINYTROUPE_RESIDENTES_RESULTS.md` y `REFORMULACION_2025_RESULTS.md` §2. Cada prueba se
pre-registró antes de correrla.

---

## 1. Cómo funciona cada una

| | **MiroFish** | **TinyTroupe (Microsoft)** | **Nuestro simulador** |
|---|---|---|---|
| Qué es | Una red social simulada, con agentes que publican y conversan | Personas inventadas, con biografía, a las que se entrevista | Una población sintética de Bogotá, hecha con bogotanos reales encuestados |
| De dónde salen los agentes | Los crea un modelo de lenguaje a partir de documentos | Se escriben a mano, o los genera su «fábrica» de personas | 19.000 personas con las proporciones de la Encuesta Multipropósito del DANE; cada una hereda a un encuestado real de la EPC 2022-2025 parecido a ella |
| Quién responde | El modelo, en el papel de cada agente | El modelo, en el papel de cada persona | **La gente real:** cada agente responde con las respuestas de su encuestado |
| Qué hace el modelo de lenguaje | Todo: crea, opina y resume | Todo: crea y opina | Solo entiende la pregunta y elige qué preguntas medidas se relacionan. Nunca contesta por nadie |
| Por localidad | No | No | Sí, con su margen de error |
| Pregunta nueva | La «opina» el modelo | La «opina» el modelo | Estimación con un rango de unos ±22 puntos, a partir de preguntas reales parecidas |

## 2. Resultados en las mismas cinco preguntas

Las cinco preguntas, con la cifra real de la EPC 2025:

| Pregunta | EPC 2025 |
|---|---|
| Satisfecho con Bogotá | 61,4 % |
| Orgulloso de Bogotá | 56,6 % |
| Las cosas van por buen camino | 48,2 % |
| Aprueba la gestión de Galán | 26,4 % |
| Víctima de un delito | 14,6 % |

| | Error medio (puntos) | Orden de las preguntas (Spearman) | Qué se vio |
|---|---|---|---|
| MiroFish con residentes | 28,7 | 0,78 | Orgullo 100 %; buen camino, Galán y víctima 0 % |
| TinyTroupe, 12 residentes | 25,2 | 0,87 | Opinan, pero casi todos igual |
| TinyTroupe, 24 de su fábrica | 27,1 | 0,78 | Con biografías más ricas, aún más uniformes |
| Decir 50 % para todo | 15,8 | — | La referencia que hay que superar |
| **Nuestro simulador, 2022-2024** | **12,9** | **0,90** | El único que le gana a «decir 50 %» |
| **Nuestro simulador, hoy (2022-2025)** | **8,3** | **1,00** | No es a ciegas: 2025 ya está en los datos |

## 3. Otras pruebas de MiroFish

| Prueba | Resultado |
|---|---|
| Aprobación de Galán | 46 %, cuando el real era 26 % |
| Tres alcaldes (Medellín 79 %, Bogotá 42 %, Cali 30 %) | Dio 50, 45 y 51: la mitad a todos |
| Segunda vuelta 2026 | Solo acertó reescalando la primera vuelta; no aportó nada propio |

## 4. Conclusión

MiroFish y TinyTroupe hacen que el modelo opine como imagina que opina Bogotá, y eso da cifras peores que decir 50 % para
todo. El nuestro hace que respondan bogotanos reales, repartidos como la ciudad. El propio Microsoft advierte que
TinyTroupe «HAS NOT been shown to match real human behavior».

**Dos aclaraciones:**
- **La comparación justa es la de 12,9**, porque se hizo con la misma prueba y sin 2025. El 8,3 de hoy no es a ciegas.
- **Las cifras de las herramientas usan los valores corregidos de 2025.** «Buen camino» es 48,2 %, no el 59 % de la nota de
  prensa que se usó al principio (`DATA_INVENTORY.md` §13.10).
