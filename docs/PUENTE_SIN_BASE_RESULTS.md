# PUENTE SIN BASE — RESULTS

**El modelo nunca dijo «sin base» donde había base, pero solo lo dijo en 5 de las 10 preguntas sin pariente: P1 falla y la página no usará el «sin base». La fuerza del puente sí distingue bien los tres casos (P3 se cumple): la página la mostrará. Nada de lo validado se rompió.**

Proyecto: Bogotá Social Simulator
Fecha: 1 de octubre de 2026
Pre-registro: `PUENTE_SIN_BASE_SPECIFICATION.md` (commits c013f27 y 8139bc9; clases revisadas por Daniel sin cambios).
Código: `src/experiments/puente_sin_base.py` (cf6f60f), subido antes de correr. Corrida de Daniel en su terminal.
Gasto: **126 llamadas, USD 0,274** (905 mil tokens de entrada, 116 mil de salida, de ellos 88 mil de razonamiento).
Resultado: `data/processed/puente_sin_base/resultado.json`

---

## 1. Las 30 preguntas

Fuerza de cada una de las 3 llamadas; «sin base» es el veredicto por mayoría (DI-SB3).

| Clase | Sin base (mayoría) | Fuerza, por pregunta |
|---|---|---|
| **A, pariente directo** | **0 de 10** | todas «fuerte» o «media»; una llamada rota en A10 |
| **B, solo el tema general** | **0 de 10** | 8 de 10 «débil» por mayoría; B7 (empleo para jóvenes) y B10 (día sin carro) salieron «media» |
| **C, sin pariente** | **5 de 10**: toros, reguetón, nombre de la ciudad, perros en restaurantes, hora oficial | las otras 5 salieron «débil» por mayoría: himno, festivo de cumpleaños, gallinas, monumento olímpico, animal símbolo |

En las 5 C donde no dijo «sin base», armó puentes con el orgullo por Bogotá (`AG2`) y la satisfacción
con la ciudad (`CV1`) para el himno, el festivo y el animal símbolo; con la oferta deportiva para el
monumento; y con las sanciones por excrementos de mascotas y ruido para las gallinas. En todas su
propia justificación empieza reconociendo que el catálogo no mide el tema («El catálogo no mide
símbolos, monumentos ni orgullo deportivo…»), y las calificó «débil».

## 2. La regresión: las 12 escondidas

Con el prompt v2, ninguna de las 12 salió «sin base» (36 de 36 llamadas con puente), y el puente
le ganó al azar y a la demografía en ordenar a las personas en **las 12** (ρ_ind de 0,23 a 0,64).
En la primera prueba también fueron 12 de 12. La fuerza fue «media» o «fuerte» en 11 de 12; la
satisfacción con la salud (`SA4`) salió «débil».

## 3. Contra el pre-registro

| # | Predicción | Umbral | Resultado | |
|---|---|---|---|---|
| **P1** | Reconoce cuando no hay base | sin_base en ≥ 7 de las 10 C | **5 de 10** | **no se cumple** |
| **P2** | No la niega cuando sí hay | sin_base en ≤ 1 de las 10 A | 0 de 10 | se cumple |
| **R1** | No rompe lo validado | sin_base en ≤ 1 de las 12 escondidas | 0 de 12 | se cumple |
| **R2** | Sigue ordenando a las personas | ρ_ind > azar 95 y > demografía en ≥ 9 de 12 | 12 de 12 | se cumple |
| **P3** | La fuerza distingue A de B | fuerte/media en ≥ 8 de las A y débil/sin_base en ≥ 6 de las B | 10 de 10 y 8 de 10 | se cumple |
| P4 | Las B no se descartan en bloque | se reporta | 0 de 10 sin_base | — |

**Regla de decisión (§6):** R1 y R2 se cumplen, P1 no → **no se usa `sin_base` en la página**. P3 se
cumple → **la página muestra la fuerza del puente.**

## 4. Lo que el resultado precisa (descriptivo, no decide)

- **Cuando dice «sin base», acierta.** En 66 llamadas a preguntas con base (A, B y las 12 escondidas)
  lo dijo una sola vez (una de las tres llamadas de la jornada única, B1), nunca por
  mayoría. Lo que le falla es decirlo siempre que corresponde: con un
  catálogo amplio, prefiere armar un puente débil a negarse. Es la tendencia que anticipaba §5.
- **La fuerza separa los tres casos.** Contando «débil o sin base» por mayoría, las C salen 10 de
  10, las B 8 de 10 y las A 0 de 10. Para quien lee la página, «base débil» marca justo las
  preguntas que no tienen pariente directo en la encuesta.

## 5. Un caso que el pre-registro no previó

La fuerza solo existe en el prompt v2, y el prompt v2 a veces responde «sin base», sin puente. La
regla dice que la página no use ese veredicto, pero no dice qué hacer cuando llega, porque entonces
no hay con qué calcular los grupos. **Queda para que Daniel decida** (ver el informe de la sesión);
lo que decida se anota aquí con fecha.

## 6. Límites

- Las clases las puse yo y las revisó Daniel; la prueba mide coincidencia con ese criterio.
- No mide si las suposiciones aciertan: para estas 30 preguntas no hay dato real.
- Una sola formulación por pregunta; con otra redacción el modelo podría decidir distinto.
