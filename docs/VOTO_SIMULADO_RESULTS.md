# INTENCIÓN DE VOTO SIMULADA — nivel 3 de D21: resultados de la parte 1

Corrido el **7 de octubre de 2026** contra `VOTO_SIMULADO_SPECIFICATION.md`:
- pre-registro en `a8899e6`;
- enmiendas 1 (`4cdd628`), 2 (`3a66640`) y 3 (`38d85bb`).

**Comando y salida:**
- `python src/experiments/voto_simulado.py`;
- `data/processed/banco/voto_simulado.json`, que no se sube.

**Gasto:**
- **la corrida:** USD 0,386 en unas 750 llamadas;
- **antes, unos USD 0,024:** las llamadas de prueba y el diagnóstico de la caché.

**Total: unos USD 0,41,** dentro del tope de USD 1,50. Con la caché (DI-E11), casi todas las llamadas leyeron la lista de
candidatas desde la caché.

**Sin porcentajes de ningún candidato:** aquí solo hay cifras de error y acierto (D21). **Nada se muestra en la página antes
de la revisión jurídica.**

**Dos cosas que se declaran:**
- **El push de la enmienda 3** llegó a GitHub unos segundos después de empezar la corrida. El commit local es anterior,
  porque el primer push falló por la red.
- **Lo visto antes de correr:** la corrida en modo simulado imprimió las referencias simples de «sin su encuesta»
  (enmienda 1, §9).

## 1. Resultado, contra la regla (§3)

| En las 215 guardadas | «Con su encuesta» | «Sin su encuesta» | Último dato (con / sin) | M0 |
|---|---|---|---|---|
| EAM | **3,7** | **4,3** | 9,4 / 11,4 | 20,0 |
| Rango (h) | 7,1 | 8,8 | | |
| Real dentro de ±h | 83 % | 86 % | | |
| Segundas vueltas: acierta quién va adelante | **94 %** (de 32) | **94 %** | 94 % / 94 % | — |
| «Probablemente gana»: acierta | **25 de 27** (93 %) | **25 de 27** | 29 de 31 / 28 de 30 | — |

| Regla, en «con su encuesta» | Resultado | |
|---|---|---|
| 1. EAM ≤ 6 | 3,7 | cumple |
| 2. Adelante ≥ 80 % y «probablemente» ≥ 90 % | 94 % y 93 % | cumple |
| 3. EAM ≤ 0,8 × el menor de M0 y el último dato (≤ 7,5) | 3,7 | cumple |

**La simulación cumple la regla, y «sin su encuesta» también la cumpliría.**

| | Predicción | Resultado | |
|---|---|---|---|
| PV1 | En «con su encuesta», EAM entre 4 y 8 | 3,7 | **falla** (mejor de lo predicho) |
| PV2 | «Con su encuesta» cumple la regla | cumple | se cumple |
| PV3 | «Sin su encuesta» al menos 3 puntos peor | 4,3 contra 3,7 (0,6) | **falla** |
| PV4 | En quién va adelante, el último dato a menos de 10 puntos | 94 % y 94 % | se cumple |

## 2. Lo que la regla no ve (análisis no pre-registrado)

**El promedio está inflado por los candidatos pequeños.** De las 215 preguntas, 101 son de candidatos con menos del 5 % real,
y en ellas el error es de 1,4 puntos: estimar un número pequeño para un candidato pequeño es fácil. Por tamaño del resultado
real:

| Resultado real | Preguntas | EAM «con» | EAM «sin» | Último dato «con» |
|---|---|---|---|---|
| menos del 5 % | 101 | 1,4 | 1,4 | 9,1 |
| 5 a 15 % | 28 | 5,4 | 6,1 | 13,9 |
| 15 a 35 % | 38 | 5,9 | 7,1 | 8,3 |
| más del 35 % | 48 | 6,1 | 7,1 | 8,4 |

| Tipo de pregunta | Preguntas | EAM «con» | EAM «sin» |
|---|---|---|---|
| primera vuelta | 57 | 2,5 | 2,5 |
| segunda vuelta | 64 | 5,2 | 6,5 |
| fórmulas (2026) | 25 | 2,7 | 2,7 |
| «nunca votaría» | 35 | 2,6 | 2,7 |
| precandidatos | 16 | 2,0 | 2,1 |
| consultas | 3 | 20,3 | 23,2 |
| tendencia (izquierda, derecha…) | 4 | 11,0 | 11,0 |
| probabilidad de votar | 3 | 8,3 | 8,3 |

**Lectura:**
- **Para los candidatos que importan,** los que tienen más del 15 % real, el error es de unos **6 puntos con su encuesta** y
  **7 sin ella**. Es el límite de la regla, o algo más, y parecido al margen de una encuesta de Bogotá con 300 personas.
- **Quién va adelante en una segunda vuelta,** lo acierta el 94 % de las veces, igual que el último dato.
- **Donde falla de verdad:** las consultas y la tendencia, con muy pocas preguntas.
- **La simulación mejora mucho al último dato** donde hay muchos candidatos (primera vuelta, precandidatos). En las segundas
  vueltas lo mejora poco.

## 3. Qué sigue

1. **La parte 2, contra la Registraduría,** en el PC personal de Daniel (§4): primera y segunda vuelta de 2022 y primera
   vuelta de 2026.
2. **Si la revisión jurídica permite mostrarla,** la página debería decir el error por tamaño: unos ±6 a 7 puntos para un
   candidato grande, no el 3,7 del promedio. Y no debería ofrecer simulación de consultas ni de tendencias.
3. **Una regla futura** debería medir el error en los candidatos con más del 5 %, no en todos. Iría en un pre-registro nuevo,
   no como cambio de este.
