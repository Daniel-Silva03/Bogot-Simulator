# FASE A DEL PLAN DE MEJORAS: TODAS LAS PRUEBAS EN UN SOLO BENCHMARK

Hecho el **19 de octubre de 2026**, siguiendo `PLAN_MEJORAS_PREDICTOR_BOGOTA.md` §13 (Fase A). **Gasto: USD 0**: no llama a
ningún modelo, solo lee los resultados guardados y la EPC. Es descriptivo: no pone a prueba ningún método nuevo, así que no
lleva pre-registro ni regla.

**Código:**
- `src/evaluacion/persistencia_epc.py`: la vara de la persistencia en la EPC;
- `src/evaluacion/benchmark.py`: la tabla única.

**Salida:** `data/processed/benchmark/predicciones.csv` (290 filas, una por pregunta y método) y `resumen.csv`. Quedan fuera de
git porque traen cifras reales del CNC (D21). Aquí van solo errores; en las filas del CNC, sin el sesgo, que dejaría adivinar
el real.

## 1. Las dos clases de problema (plan §3.1)

- **A, pregunta ya medida:** hay un dato anterior comparable. La vara es **repetir el último dato**.
- **B, pregunta nunca medida:** no hay dato anterior de esa pregunta. Incluye «B escondida»: la pregunta se midió en la misma
  EPC, pero se escondió a los agentes.
- **Voto:** aparte, porque es multiclase.

## 2. La vara de la persistencia en la EPC (problema A)

Repetir el dato del año anterior, en 144 pares pregunta-año de la EPC (73 preguntas, 2022 a 2025).

| | Pares | Error medio | Mediana |
|---|---|---|---|
| 2022 → 2023 | 63 | 3,2 | 2,5 |
| 2023 → 2024 | 50 | 4,7 | 3,2 |
| 2024 → 2025 | 31 | 6,1 | 5,2 |
| **Total** | **144** | **4,3** | **3,2** |

**Por dominio:**

| Dominio | Pares | Error medio | Máximo |
|---|---|---|---|
| Espacio público | 14 | 2,7 | 6,9 |
| Servicios | 6 | 2,9 | 7,0 |
| Ambiente | 7 | 3,4 | 6,8 |
| Economía y hogar | 24 | 3,5 | 12,5 |
| Movilidad | 28 | 4,0 | 12,8 |
| Cultura y recreación | 6 | 4,1 | 7,7 |
| Seguridad | 9 | 4,2 | 8,9 |
| Cultura ciudadana | 30 | 4,9 | 17,1 |
| Ciudad en general | 6 | 6,4 | 18,3 |
| **Gobierno e instituciones** | **14** | **7,0** | **15,9** |

**Los cambios más grandes de un año a otro:**
- el orgullo por Bogotá (`AG2`), +18 en 2023;
- el respeto en la cultura ciudadana (`RC4_1` a `RC4_3`), +15 a +17 en 2024;
- **la gestión de Galán** (`GG3_GALAN`), **−16 en 2025**;
- **la transparencia de su gobierno** (`MICE1_GALAN`), **−13 en 2025**.

Varios de esos saltos coinciden con cambios de cuestionario. El error de la persistencia también los incluye, igual que en la
página.

## 3. Todos los métodos, por problema y dominio

Sin las dos preguntas ya vistas de `ACTUALIDAD_EPC`.

### Problema A: pregunta ya medida, gobierno e instituciones

| Método | Preguntas | Error medio | Sesgo |
|---|---|---|---|
| Persistencia (EPC 2025), Galán en CB y Guarumo | 3 | 3,2 | −2,7 |
| Persistencia (CB del mes anterior) | 1 | 3,5 | +3,5 |
| Agentes con aviso de «tu opinión es de 2024» | 1 | 2,6 | −2,6 |
| **Persistencia (EPC del año anterior)** | **19** | **7,2** | +2,7 |
| Agentes | 8 | 8,6 | +6,0 |
| Agentes sin opiniones de gobierno | 3 | 9,2 | +9,2 |
| Agentes + resumen de noticias | 5 | 10,1 | +10,1 |

### Problema B escondida: la misma EPC, la pregunta escondida a los agentes

| Método | Preguntas | Error medio |
|---|---|---|
| **Agentes** (cuatro perfiles) | 10 | **7,4 a 7,8** |
| Estimación de la página | 10 | 14,3 |

### Problema B: pregunta nunca medida

| Dominio | Método | Preguntas | Error medio |
|---|---|---|---|
| Movilidad (metro, 2026) | estimación de la página | 5 | 19,6 |
| | agentes (tres modelos) | 5 | 22,8 a 28,3 |
| Gobierno (Galán, 2026) | estimación de la página | 2 | 11,0 |
| | agentes | 1 | 15,5 a 20,6 |
| Política nacional (CNC 2026) | agentes (`AGENTES_2026`) | 7 | 9,0 a 11,6 |
| | estimación de la página | 7 | 12,7 |
| | agentes (`VALIDACION_AGENTES_D22`, imagen del presidente) | 5 | 14,8 |
| Conducta política (CNC 2026) | agentes | 4 | 8,9 |
| Varios (validación de la estimación) | estimación de la página | 74 | 12,5 |

En las nueve de `VALIDACION_AGENTES_D22`, decir 50 % se equivocó 9,1 en total (ya reportado). No se desagrega aquí: con las
cifras del CNC, el error de 50 % por subgrupo deja ver dónde está el real.

### Voto (multiclase)

| Prueba | Método | Error |
|---|---|---|
| 1.ª vuelta 2026, 11 candidatos | **copiar la encuesta** | **1,8** |
| | agentes + resumen + encuesta | 3,5 |
| | agentes + resumen de campaña | 7,4 |
| | agentes solos | 8,1 |
| 2.ª vuelta 2026, parte de Cepeda | **agentes + encuesta nacional** | **3,4** |
| | decir 50 % | 3,6 |
| | copiar la encuesta nacional | 7,5 |
| | agentes calibrados | 7,5 |
| | agentes + instrucción | 15,2 |

## 4. Lo que dice el benchmark

1. **En el problema A, la persistencia gana casi siempre.** En gobierno e instituciones se equivoca 7,2 en promedio, y los
   agentes, de 8,6 a 10,1, con sesgo hacia arriba (más favorables al gobierno que la gente).
2. **Gobierno e instituciones es lo más movedizo** (7,0 de persistencia contra 4,3 del total). Es también lo que más le importa al
   jefe de Daniel: es donde más vale la pena acertar el cambio, y donde más difícil es.
3. **Los agentes ganan en un solo caso claro: la pregunta escondida dentro de la misma ola** (7,4 contra 14,3 de la estimación).
   Ahí reconstruyen bien una respuesta desde las otras de la misma persona y del mismo momento.
4. **En preguntas de verdad nuevas,** nadie anda bien. El metro fue un fracaso de todos los métodos, todos muy por debajo del
   optimismo real. En lo político nacional, los agentes van de 9 a 15.
5. **En el voto, copiar la encuesta de la misma población es lo mejor.** Los agentes solo aportan cuando la encuesta es de otra
   población (nacional frente a Bogotá).
6. **Las cifras de un solo caso** (Galán en CB, la 2.ª vuelta) son evidencia provisional, como pide el plan (§3.4).

## 5. Lo que esto sugiere para la Fase B (el selector)

Una primera regla, que la Fase B tendría que poner a prueba con su pre-registro:
- **Pregunta ya medida:** la última medición comparable, no los agentes.
- **Pregunta escondida o muy ligada a otras medidas en la misma ola:** los agentes.
- **Pregunta de voto con encuesta de la misma población:** la encuesta; con encuesta de otra población, los agentes con esa
  encuesta.
- **Pregunta nueva sin nada parecido:** ningún método le gana con claridad a una cifra neutral. Se muestra como exploratoria, con
  un intervalo amplio (plan §11).

**El límite de la Fase B:** hay pocas preguntas por casilla (de 1 a 19 en lo político). Un selector aprendido con tan pocos casos
puede encontrar reglas falsas, como advierte el plan (§4).
