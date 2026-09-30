# EJE POR PARTIDOS — RESULTS

**El resto territorial no es de un candidato: aparece en el voto por partido al Congreso, en los dos extremos. Pero son dos polos con geografía propia, no un solo eje simétrico.**

Proyecto: Bogotá Social Simulator
Versión: 0.1
Fecha: 30 de septiembre de 2026
Pre-registro: `docs/EJE_PARTIDOS_SPECIFICATION.md` (código y mundos simulados subidos antes de la corrida, commit `4208e6c`)
Código: `src/experiments/eje_partidos.py` · Pruebas: `tests/test_eje_partidos.py` (13)
Salida: `data/processed/eje_partidos/resultado.json`

---

## 1. Resultado, en una línea

Lo que el estrato no explica del voto al Senado 2018 sigue al eje presidencial de Petro
2022 en la Lista de la Decencia (**r = 0,77**) y va en contra en el Centro Democrático
(**r = −0,56**), y la Cámara lo replica (0,80 y −0,55). Se cumplen las cinco
predicciones y la regla da la **lectura A**. La predicción que decidía, la del Centro
Democrático, pasa **por poco**; lo que la explica está en §4.

---

## 2. La tabla

19 localidades; proporción sobre votos por partido; residuo del estrato medio (M1).
«r eje» es la correlación con el residuo de Petro 2022 (pre-registrado); «r 2018», con el
de Petro 2018 (secundario); «r insc», con la razón inscritos / adultos.

**Senado, circunscripción nacional**

| Partido | R²_LOO | r eje | p (dos colas) | r 2018 | r insc |
|---|---|---|---|---|---|
| **Lista de la Decencia** | 0,83 | **+0,77** | 0,0002 | +0,70 | +0,31 |
| **Centro Democrático** | 0,64 | **−0,56** | 0,011 | −0,16 | −0,31 |
| Alianza Verde | 0,85 | −0,22 | 0,36 | −0,50 | −0,19 |
| Cambio Radical | 0,76 | +0,29 | 0,24 | +0,35 | +0,40 |
| Polo Democrático | −0,26 | +0,66 | 0,002 | +0,36 | **+0,62** |
| Liberal | 0,28 | +0,38 | 0,10 | +0,35 | **+0,64** |

**Cámara, circunscripción territorial (réplica)**

| Partido | R²_LOO | r eje | p (dos colas) | r insc |
|---|---|---|---|---|
| **Lista de la Decencia** | 0,73 | **+0,80** | 0,0002 | +0,37 |
| **Centro Democrático** | 0,63 | **−0,55** | 0,013 | −0,28 |
| Alianza Verde | 0,85 | −0,07 | 0,77 | −0,18 |
| Cambio Radical | 0,66 | +0,21 | 0,37 | +0,37 |
| Polo Democrático | −0,27 | +0,59 | 0,008 | +0,56 |
| Liberal | 0,08 | +0,36 | 0,13 | +0,64 |

---

## 3. Contra el pre-registro

| # | Predicción | Umbral | Resultado | |
|---|---|---|---|---|
| P1 | La Lista de la Decencia sigue al eje (Senado) | r > 0,5, p < 0,05 | +0,77, p = 0,0002 | se cumple |
| **P2** | **El Centro Democrático va en contra (Senado)** | r < −0,5, p < 0,05 | **−0,56**, p = 0,011 | **se cumple, por poco** |
| P3 | Las dos se replican en la Cámara | mismo signo, \|r\| > 0,5 | +0,80 y −0,55 | se cumple |
| P4 | El estrato explica buena parte (Senado) | R²_LOO ≥ 0,50 | 0,83 y 0,64 | se cumple *(no informativa)* |
| P5 | La inscripción no bloquea (Senado) | \|r\| < 0,50 | 0,31 y −0,31 | se cumple |

**Regla de decisión: A.** Tal como quedó escrita: el eje no es de un candidato; es una
geografía política estable de Bogotá, visible en el voto por partido y en el
presidencial, que la composición no ve.

Dos salvedades que el pre-registro ya anticipaba y conviene repetir:
- **P1 es en parte mecánica**: la Lista de la Decencia fue la lista de Petro.
- **P3 no es una prueba independiente**: Senado y Cámara se votaron el mismo día, en la
  misma mesa. Muestra que el resultado no depende de la boleta.

---

## 4. Lo que el resultado precisa: dos polos, no un eje

**Descriptivo, no pre-registrado.** P2 pasó por 0,06, y contra el eje secundario (Petro
2018) el Centro Democrático da solo −0,16. Para entender por qué, se correlacionó su
residuo con los de todos los candidatos del análisis presidencial:

| Residuo del Senado 2018 contra el residuo de… | Centro Democrático | Lista de la Decencia |
|---|---|---|
| Zuluaga 2014 | **+0,81** | −0,15 |
| Clara López 2014 | **−0,86** | **+0,76** |
| Duque 2018 | **+0,86** | −0,56 |
| Petro 2018 | −0,15 | **+0,70** |
| Fajardo 2018 | −0,37 | −0,34 |
| Petro 2022 | −0,56 | **+0,77** |
| Gutiérrez 2022 | **+0,83** | −0,56 |

**Lo que muestra:** el resto territorial del Centro Democrático es, casi exactamente, el
de la derecha en las tres presidenciales (Zuluaga, Duque, Gutiérrez: de 0,81 a 0,86). El
de la Lista de la Decencia es el de la izquierda (Clara López, Petro 2018 y 2022: de
0,70 a 0,77). Los dos polos van en sentidos opuestos (−0,42 entre sí en el Senado), pero
**no son espejo uno del otro**. P2 pasó justo porque el eje pre-registrado, Petro 2022,
recoge los dos polos a medias.

**Dónde está cada polo** (Senado, en puntos porcentuales sobre lo que predice el estrato):
- **Centro Democrático, más de lo esperado:** Usaquén +6,6, Suba +3,9, Ciudad Bolívar
  +3,2, Chapinero +2,5; **menos:** Teusaquillo −5,1, Fontibón −2,8, La Candelaria −2,1.
- **Lista de la Decencia:** el mismo patrón que Petro presidencial: el centro y el
  suroriente por encima, el noroccidente por debajo.

**Dos cosas más de la tabla, también descriptivas:**
- **La Alianza Verde no sigue ningún polo** (−0,22 con el eje). Lo que el estrato no
  explica de la izquierda no incluye al centro verde: no es un eje «progresista contra
  conservador», es petrismo y uribismo.
- **El Polo y el Liberal siguen la inscripción** (0,62 y 0,64), y su R²_LOO es bajo o
  negativo. Su resto territorial está en el centro de la ciudad por dónde se inscribe la
  gente, no por cómo vota. Por eso no eran partidos decisivos, y por eso su correlación
  con el eje no se interpreta.

---

## 5. Lo que este resultado NO dice

- **Nada sobre personas** (ecológico, como el análisis anterior).
- **No dice que el eje sea el mismo en otras elecciones al Congreso**: es una sola, 2018.
- **No dice qué produce el resto territorial.** Puede ser contexto (barrio, redes,
  historia local) o composición que el estrato medio no mide. Lo que sí dice es que es
  estable, que tiene dos polos y que no es un artefacto de la inscripción en los dos
  partidos que decidían.
- **La lectura de dos polos no estaba pre-registrada.** Es la descripción más fiel de la
  tabla, pero una prueba de ella tendría que pre-registrarse aparte.

---

## 6. Consecuencias

1. **La lectura B de la geografía electoral se refuerza.** Ya no es solo que el resto
   presidencial se repite: aparece en el voto por partido, con otra boleta y otra
   unidad. Bogotá tiene una geografía política propia que la composición no ve.
2. **Para el tablero:** la capa de Voto puede decir que lo que el estrato no explica no
   es de un candidato, y que tiene dos polos. Conviene que la vista de residuos de un
   candidato de derecha (Duque, Gutiérrez) se lea como el polo de derecha, y no como el
   negativo del de Petro.
3. **Para DI-B10** (reabrir un donante con localidad): la evidencia es ahora más fuerte
   que con el voto presidencial solo. La decisión sigue siendo de proyecto.
4. **Si se quiere probar la lectura de dos polos**, el diseño es inmediato: pre-registrar
   la correlación del Centro Democrático con el residuo de la derecha presidencial
   (Duque 2018, Gutiérrez 2022) y la de la Lista con el de la izquierda, sobre una
   elección que todavía no se haya mirado.
