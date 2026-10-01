# PREGUNTAS REALES NUEVAS — SPECIFICATION

**En dos preguntas que la EPC nunca hizo y cuya respuesta real conocemos, el metro elevado y el Corredor Verde por la séptima, ¿el puente acierta qué grupos estarían más de acuerdo?**

Proyecto: Bogotá Social Simulator
Versión: 0.1 — **pre-registro**
Fecha: 1 de octubre de 2026
Estado: **sin código; no se le ha hecho ninguna de las dos preguntas al simulador, ni simulado ni real**
Origen: `DATA_INVENTORY.md` §15 (biblioteca pública del CNC) y `PUENTE_SIN_BASE_SPECIFICATION.md` §7
(«no mide si la suposición acierta: para una pregunta de verdad nueva no hay dato real»)

---

## 1. La pregunta

Toda la validación del puente usó preguntas de la misma encuesta, escondidas. Una pregunta de verdad
nueva puede estar más lejos del catálogo, y hasta ahora no había con qué compararla. La encuesta de
opinión del CNC para Red+ y Caracol Radio del 15 de agosto de 2023 (4.275 personas en Bogotá) trae
dos preguntas de aprobación de cambios en la ciudad que la EPC no hizo, con resultados por sexo, edad,
estrato y localidad.

> **¿El orden de los grupos que da el puente coincide con el real?**

Es lo que la página muestra en una pregunta nueva («qué grupos estarían más o menos de acuerdo»), así
que es lo que más importa acertar.

## 2. Lo que ya sé antes de empezar

- **Conozco las cifras reales**: las leí al hacer el inventario y están en §4. No he visto ninguna
  respuesta del simulador a estas preguntas.
- **Los dos temas fueron noticia** en 2023: el metro elevado frente al subterráneo, y el Corredor
  Verde, que la administración siguiente frenó. El modelo de lenguaje puede saber, por la prensa, qué
  sectores apoyaban cada uno, y elegir el puente con ese conocimiento. Incluso podría conocer esta
  misma encuesta. Eso no invalida la prueba, porque el modelo elige preguntas y sentidos y las
  respuestas las ponen las personas de la EPC, pero el nivel que propone puede venir de ahí (§7).
- **De la prueba del puente sé** que ordena bien a las personas en preguntas de la misma encuesta
  (12 de 12) y no a las localidades.

## 3. Qué se le pregunta al simulador

Dos preguntas, con la redacción de la encuesta real llevada a la escala de acuerdo de la página:

- **Metro:** «¿Qué tan de acuerdo está con mantener el metro elevado para Bogotá?»
- **Corredor:** «¿Qué tan de acuerdo está con el Corredor Verde por la carrera séptima?»

Escala: Totalmente en desacuerdo, En desacuerdo, Ni de acuerdo ni en desacuerdo, De acuerdo,
Totalmente de acuerdo. **Se responden como en la página** (`motor.py`, DI-CO7 y DI-CO12): el prompt
v2 del puente, el catálogo de 102, la población 2022-2024 y, si el modelo dice «sin base», el puente de
siempre. Sin pasar por la reformulación, para que la redacción sea fija. **3 llamadas por pregunta**
(rep 0, 1, 2) a temperatura 0, con `xiaomi/mimo-v2.6-pro`: 6 llamadas, más las de reintento si las
hay. Menos de USD 0,05.

## 4. Contra qué se mide

Las cifras publicadas (porcentaje que respondió «sí»; base sin ponderar entre paréntesis). Estrato 5 y
6 se juntan, ponderando por sus bases (97 y 26), porque por separado son muy pocos.

| Grupo | Metro elevado | Corredor Verde |
|---|---|---|
| Total (4.275) | 65,7 | 58,8 |
| Hombres (2.465) / Mujeres (1.810) | 61,5 / 69,4 | 53,7 / 63,3 |
| 18-24 (406) / 25-34 (872) / 35-54 (1.955) / 55+ (1.042) | 61,5 / 56,8 / 69,8 / 70,9 | 67,7 / 63,7 / 59,0 / 49,2 |
| Estrato 1 (435) / 2 (1.571) / 3 (1.765) / 4 (381) / 5-6 (123) | 69,7 / 64,2 / 63,0 / 69,4 / 74,6 | 69,0 / 65,2 / 57,1 / 45,9 / 51,5 |

Por localidad (13; «Otra» agrupa seis y no se usa):

| Localidad | Metro | Corredor | | Localidad | Metro | Corredor |
|---|---|---|---|---|---|---|
| Santa Fe | 61,6 | 65,2 | | Barrios Unidos | 70,9 | 59,2 |
| Usme | 53,0 | 59,9 | | Los Mártires | 55,1 | 62,9 |
| Tunjuelito | 68,6 | 66,1 | | Puente Aranda | 64,9 | 45,8 |
| Bosa | 71,0 | 63,8 | | Rafael Uribe Uribe | 71,6 | 58,2 |
| Kennedy | 50,9 | 61,4 | | Ciudad Bolívar | 74,1 | 66,0 |
| Fontibón | 72,9 | 55,3 | | Suba | 76,2 | 58,0 |
| Engativá | 53,6 | 63,3 | | | | |

(La gráfica del metro por localidad, p. 14 del informe, lleva por error el título de la de
victimización; los valores son los del metro.)

**Diferencias claras.** Dentro de cada dimensión (sexo, edad, estrato) hay 17 pares de grupos por
pregunta. Cuenta como **clara** una diferencia cuyo valor z supera 1,96, con las bases sin ponderar y
sin efecto de diseño. Calculadas antes de correr nada, son **24**:

- **Metro (11):** mujeres > hombres; 35-54 y 55+ > 18-24 y > 25-34 (4 pares); estrato 1 > 2 y > 3;
  estrato 4 y 5-6 > 2 y > 3 (4 pares).
- **Corredor (13):** mujeres > hombres; 18-24 y 25-34 > 35-54 y > 55+ (4 pares); 35-54 > 55+; estrato
  1 > 3, > 4 y > 5-6; estrato 2 > 3, > 4 y > 5-6; estrato 3 > 4.

Ignorar el efecto de diseño hace pasar por claras algunas diferencias que no lo son. Por eso el umbral
de §5 no pide acertarlas todas.

## 5. Cómo se mide

**El índice de un grupo** es el de la página: el puntaje del puente de cada agente, estandarizado en
la ciudad, promediado con los pesos de los agentes del grupo (DI-CO2). Los grupos se arman con los
datos del propio agente: sexo; edad en los cuatro tramos de la encuesta real (no los cinco de la
página); estrato 1, 2, 3, 4 y 5-6. Los agentes de estrato 0 no entran.

**Concordancia:** un par claro está acertado si el signo de la diferencia de índices es el de la
diferencia real. Un empate cuenta como fallo. Se calcula en cada llamada y se toma la mediana de las
tres.

**Línea base, el azar:** 200 puentes al azar (de 1 a 5 preguntas del catálogo de 102, sentido y peso
al azar, semilla fija), con su concordancia en los mismos 24 pares; se usa el percentil 95.

## 6. Predicciones pre-registradas

| # | Predicción | Umbral |
|---|---|---|
| **P1** | **El puente acierta el orden de los grupos** | concordancia en los 24 pares claros **≥ 0,70** (17 de 24) **y** mayor que el p95 del azar |
| P2 | Lo acierta en cada pregunta por separado | concordancia ≥ 0,60 en el metro (7 de 11) y en el Corredor (8 de 13) *(se reporta)* |
| P3 | El nivel propuesto va en la dirección real | nivel > 3 en las dos, y mayor en el metro que en el Corredor *(se reporta)* |
| P4 | Las localidades | correlación de Pearson entre el índice por localidad y el real, en las 13 *(se reporta)* |

**P4 no reabre por sí sola la lectura B.** Pero esta es la primera comparación por localidad contra
una encuesta **independiente**: el artefacto del ruido compartido (`PUENTE_LOCALIDADES_RESULTS.md` §4)
no existe aquí, porque el simulador y la encuesta real no comparten personas. Si en las dos preguntas
sale ≥ 0,5, se anota como razón para pre-registrar una prueba más amplia.

**Por qué espero P1, con poca seguridad.** El puente ordenó bien a las personas en las preguntas
escondidas, y aquí las diferencias más grandes son de estrato y edad, que el catálogo refleja bien.
Pero el metro tiene un orden en U por estrato (los extremos lo apoyan más que el 2 y el 3), difícil
de reproducir con un puntaje lineal, y el puente se elige sin ver datos.

## 7. Regla de decisión

```
    P1 se cumple
      → La página puede decir, en «Lo que aprendimos probándolo», que en dos preguntas reales que
        la encuesta no hizo, el puente acertó el orden de los grupos en X de 24 diferencias claras.

    P1 no se cumple
      → En las preguntas nuevas, la página deja de mostrar las barras por grupo de entrada: las
        muestra solo si la persona lo pide («ver de todos modos»), con el aviso de que en una
        prueba con preguntas reales el orden de los grupos no se sostuvo. El nivel y en qué se
        apoya la suposición se siguen mostrando.
```

P2, P3 y P4 se reportan siempre y no deciden.

## 8. Límites, dichos antes

- **Métodos distintos.** La encuesta real se hizo en línea, autoaplicada en el celular, por invitación
  SMS a usuarios de Claro; la EPC, cara a cara. Las personas que contestan por SMS no son las mismas
  que abren la puerta, y eso puede mover los grupos, no solo el nivel.
- **«Sí/No» frente a una escala de 5.** Por eso no se compara el nivel con el porcentaje, solo su
  dirección (P3).
- **Dos preguntas, 24 pares.** Una muestra pequeña; un fallo o un acierto dice algo, no todo.
- **El modelo pudo leer sobre estos temas** (§2).
- **Agosto de 2023**, en plena campaña a la Alcaldía, cuando los dos temas eran de campaña.

## 9. Qué se construye después

1. `src/experiments/preguntas_reales.py` y sus pruebas, con un modelo simulado (sin gasto).
2. Con permiso, la corrida (6 llamadas o pocas más) y `PREGUNTAS_REALES_NUEVAS_RESULTS.md`, contra
   este documento.
