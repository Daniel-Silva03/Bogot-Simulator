# EJE POR PARTIDOS — SPECIFICATION

**¿El territorio que el estrato no explica en el voto presidencial aparece también en el voto por partido?**

Proyecto: Bogotá Social Simulator
Versión: 0.1 — **pre-registro**
Fecha: 30 de septiembre de 2026
Estado: **sin código y sin ningún cruce entre el voto por partido y la composición o los residuos**
Datos: `data/external/electoral/congreso_2018_*` (DATA_INVENTORY §14.5), `data/processed/geografia_electoral/resultado.json`, receptor de Multipropósito 2021
Origen: `GEOGRAFIA_ELECTORAL_RESULTS.md` §4.2 y §8, punto 5

---

## 1. La pregunta

`GEOGRAFIA_ELECTORAL_RESULTS.md` encontró que el estrato explica el 84 % de la
geografía del voto por Petro, y que lo que no explica se repite (r = 0,87 entre 2018 y
2022) y sigue un eje izquierda–derecha que ya estaba en 2014. Pero todo eso es voto
**presidencial**, que es voto por una persona. Queda abierta una lectura más estrecha:
que el eje sea el de un candidato y no una geografía política de la ciudad.

El voto al Congreso de marzo de 2018 es otra elección, otra boleta y otra unidad: se
vota por un partido. Si el mismo resto territorial aparece ahí, y aparece **también en
un partido que no es el de Petro**, el eje no es de un candidato.

> **¿Lo que el estrato no explica del voto por partido en Senado y Cámara 2018 sigue
> el mismo patrón territorial que lo que no explica del voto presidencial por Petro en
> 2022?**

---

## 2. Lo que ya sé antes de empezar (declarado para que se pueda descontar)

- **Vi las proporciones por localidad de cinco partidos del Senado** (conversación del
  29/09, al construir la tabla): la Lista de la Decencia va del 4 % en Usaquén al 16 %
  en Ciudad Bolívar y el Centro Democrático del 33 % al 15 %. Es el gradiente
  norte–sur del estrato, así que **P4 es casi segura y no es informativa**.
- **Conozco el mapa de residuos presidencial**: el centro (Teusaquillo, Santa Fe,
  Chapinero) y el suroriente más a la izquierda de lo que dice su estrato; el
  noroccidente (Suba, Usaquén, Engativá) menos.
- **No he calculado ningún residuo del voto por partido** ni lo he cruzado con la
  composición.
- **La Lista de la Decencia fue la lista de Petro en 2018.** Que su residuo se parezca
  al de Petro es en parte mecánico —los mismos votantes votan la lista y el candidato—.
  Por eso **la predicción que más informa es P2**, sobre el Centro Democrático.

---

## 3. Datos

### 3.1 El voto por partido

`congreso_2018_localidad.csv` y `congreso_2018_zonas.csv`. Proporción de cada partido
sobre `votos_partidos` (sin blancos, nulos ni no marcados).

- **Principal: Senado, circunscripción nacional.** Es la misma boleta en toda la
  ciudad.
- **Réplica: Cámara, circunscripción territorial de Bogotá.** Mismo día, otra boleta.
- Las circunscripciones especiales (indígena, afro) no entran: son minoritarias y
  otras boletas.

**Los dos partidos que deciden**, fijados por la regla «la lista del candidato
presidencial de cada extremo en la primera vuelta de 2018»:

| Partido | Por qué |
|---|---|
| **Coalición Lista de la Decencia (ASI, UP, MAIS)** | la lista de Petro |
| **Partido Centro Democrático** | el partido de Duque |

Los otros cuatro de los seis mayores —Alianza Verde, Cambio Radical, Polo, Liberal— se
reportan con los mismos cálculos, **sin predicción**.

### 3.2 La referencia: el eje presidencial

El residuo de M1 de **Petro 2022**, tal como está en `resultado.json` (la cifra
pre-registrada del análisis anterior), sin recalcularlo. Es otra elección y cuatro años
después: no comparte ninguna boleta con el Congreso 2018. El residuo de Petro 2018 (mayo,
dos meses después) se reporta como secundario.

### 3.3 La composición y las unidades

Las mismas de `GEOGRAFIA_ELECTORAL_SPECIFICATION.md` §3.2 y §3.3: estrato medio de
Multipropósito 2021 (`x1`), **19 localidades** (sin Sumapaz; sin las zonas 90 y 98),
cada una con el mismo peso.

---

## 4. Método

Para cada partido y corporación:

| Cifra | Qué es |
|---|---|
| **Residuo** | Proporción observada menos la predicha por M1 (MCO sobre `x1`) |
| R²_LOO | R² dejando una localidad fuera, como en el análisis anterior |
| **r_eje** | Correlación de Pearson entre el residuo del partido y el de Petro 2022 |
| `p` | Permutación, 10.000 veces, **de dos colas** (hay predicciones de los dos signos) |

**Control de inscripción** (el mismo de la enmienda 1 del análisis anterior): correlación
del residuo con la razón inscritos 2018 / población 18+. Si |r| ≥ 0,50 para la Lista de
la Decencia **o** para el Centro Democrático en el Senado, las predicciones de eje se
reportan como **no interpretables como territorio**.

**Qué se reutiliza y qué no.** Las funciones de `geografia_electoral.py` (residuo, R²_LOO,
permutación) ya pasaron los tres mundos simulados de ese pre-registro, y se usan sin
cambios. Lo nuevo es solo cómo se arma la proporción por partido, y eso se prueba con
datos inventados antes de la corrida real. La permutación de dos colas se agrega como
función nueva y se prueba contra la de una cola.

---

## 5. Predicciones pre-registradas

| # | Predicción | Umbral |
|---|---|---|
| **P1** | El resto territorial de la Lista de la Decencia sigue al eje presidencial | Senado: r_eje > 0,5 y p < 0,05 |
| **P2** | **El del Centro Democrático va en contra del eje** | Senado: r_eje < −0,5 y p < 0,05 |
| **P3** | Las dos se replican en la Cámara | Cámara: mismo signo y \|r_eje\| > 0,5 en los dos partidos |
| **P4** | El estrato explica buena parte de la geografía de los dos partidos | Senado: R²_LOO ≥ 0,50 en los dos *(no informativa, §2)* |
| **P5** | El control de inscripción no bloquea la lectura | \|r\| < 0,50 para los dos partidos en el Senado |

**Por qué espero esto.** P1 porque la Lista de la Decencia es el petrismo con otra
boleta. P2 porque el eje del análisis anterior ya iba contra Duque (−0,80 con Petro
2022) y el Centro Democrático es su partido; es la que puede fallar de verdad. P3 porque
Senado y Cámara se votan el mismo día, en la misma mesa. P5 porque en el voto
presidencial la inscripción dio 0,21 y 0,23; si fuera distinto aquí, el eje estaría
contaminado de otra forma.

---

## 6. Regla de decisión

```
    A. P1, P2 y P3 se cumplen, y P5 también
         → El eje no es de un candidato: es una geografía política estable de
           Bogotá, visible en el voto por partido y en el presidencial, que la
           composición no ve. Refuerza la lectura B de GEOGRAFIA_ELECTORAL y la
           propuesta de reabrir DI-B10.

    B. P1 se cumple y P2 no (con P5)
         → El resto territorial acompaña al petrismo, no a la derecha: es un eje
           de un movimiento, no izquierda–derecha. El tablero debe describirlo así.

    C. Ni P1 ni P2
         → El eje es propio del voto presidencial. En el voto por partido, lo que
           el estrato no explica no sigue ese patrón.

    Si P5 falla (inscripción fuerte)
         → Intermedio: el patrón puede ser el desajuste entre dónde se inscribe y
           dónde vive la gente. No se adopta ninguna lectura.

    Cualquier otro caso (por ejemplo, P1 y P2 en el Senado pero no en la Cámara)
         → Intermedio: se reporta sin adoptar ninguna lectura.
```

---

## 7. Límites, dichos antes

- **Todo lo del análisis anterior vale aquí** (§7 de ese pre-registro): es ecológico,
  el voto está donde se está inscrito, la participación varía, la composición es de
  2021 y hay 19 puntos.
- **P1 no es independiente del voto presidencial** (§2). El peso lo lleva P2.
- **Senado y Cámara no son dos pruebas independientes**: mismos votantes, mismo día.
  P3 muestra que el resultado no depende de la boleta, no que se repita en otra
  población.
- **Una sola elección de Congreso.** Si el patrón se sostiene, dice que en 2018 el voto
  por partido lo compartía, no que siempre lo haga.
- **Los partidos cambian entre elecciones.** Por eso la referencia es un residuo
  presidencial y no un partido de otro año.

---

## 8. Qué se construye después de este documento

1. `src/experiments/eje_partidos.py` y `tests/test_eje_partidos.py`: proporción por
   partido y permutación de dos colas, probadas con datos inventados.
2. La corrida real.
3. `EJE_PARTIDOS_RESULTS.md`, **contra este pre-registro**.
