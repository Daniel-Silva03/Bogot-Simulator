# PESO POR FECHA EN LA INTENCIÓN DE VOTO SIMULADA

Pre-registro escrito el **8 de octubre de 2026**, antes de calcular nada con el peso por fecha. Lo pidió Daniel.
**Gasto: USD 0.** Las elecciones de Luna se recuperan de las cachés del nivel 3; si falta alguna, el código se detiene en vez
de llamar.

## 1. Por qué

Hoy la intención de voto (nivel 3, `VOTO_SIMULADO_RESULTS.md`; página, DI-CO30) es el **promedio simple** de las preguntas
que elige Luna, y pesa igual una encuesta de enero que una de mayo.

En la prueba de la página del 8/10, la segunda vuelta Cepeda contra De la Espriella se apoyó en las cinco encuestas de 2026.
- **El promedio** dio una diferencia de 16,5 puntos, «probablemente gana», apenas sobre el umbral de 16.
- **La de mayo** era mucho más cerrada; la diferencia la sostenían las de enero y febrero.

La intención de voto cambia con la campaña, así que una encuesta cercana en el tiempo debería pesar más.

## 2. Método

**Luna no cambia, y tampoco lo que elige.** Se usan las mismas preguntas elegidas en el nivel 3. Cambia solo cómo se combinan
sus resultados reales:

S = Σ wᵢ Tᵢ / Σ wᵢ, con wᵢ = exp(−dᵢ / τ)

- **dᵢ:** los días entre la encuesta de la pregunta objetivo y la de cada elegida. En la página, hasta hoy; en la
  Registraduría, hasta el día de la elección. Las fechas son las de `voto_registraduria.FECHAS` (DI-VR1).
- **La rejilla de τ:** 0, 15, 30, 60, 120, 240 y 480 días, más τ = ∞.
  - **τ = ∞** es el promedio simple de hoy.
  - **τ = 0** toma solo las elegidas más cercanas.
- **τ\* se elige solo con la práctica:** las 158 preguntas de práctica del lote 7, cada una estimada con las otras familias,
  como en el nivel 3. Se toma la τ de menor EAM. Si otra queda a menos de 0,05 puntos, gana la más grande, la más cercana al
  método de hoy.
- **h y h₂ se recalculan en la práctica con τ\***, igual que en el nivel 3: el cuantil 80 % del error y el de la diferencia
  en segundas vueltas.

**Control:** con τ = ∞ debe reproducirse exactamente el nivel 3 (EAM y h). Si no, el código se detiene.

## 3. La prueba

**Objetivos:** las 215 guardadas del lote 7, versión «con su encuesta», la que decide en el nivel 3. Se compara τ\* contra
τ = ∞ con las medidas del nivel 3:
- EAM;
- quién va adelante en las 32 segundas vueltas;
- «probablemente gana», con su h₂;
- cobertura de ±h.

**Se reporta además** el EAM por separado en las preguntas de 2021-2022 y en las de 2026.

## 4. Regla

**El peso por fecha entra a la página, con su τ\*, su h y su h₂, si se cumplen las cuatro condiciones:**
1. **R1:** τ\* no es ∞;
2. **R2:** en las guardadas, el EAM con τ\* es al menos **0,3 puntos** menor que con τ = ∞;
3. **R3:** acierta quién va adelante en al menos tantas segundas vueltas como con τ = ∞;
4. **R4:** si dice «probablemente gana» 5 veces o más, acierta en ≥ 90 %.

**Si no se cumplen,** la página sigue con el promedio simple, y se anota.

## 5. Registraduría (se reporta, sin regla)

Las tres elecciones del nivel 3, parte 2 (`VOTO_REGISTRADURIA_SPECIFICATION.md`), con las mismas elegidas: EAM y acierto
del primero, con τ\* y con τ = ∞. La distancia se mide hasta el día de la elección. Son pocas elecciones para decidir.

## 6. Predicciones

- **PF1.** τ\* es finita y no pasa de 120 días.
- **PF2.** El peso por fecha cumple la regla.
- **PF3.** La mejora en EAM es mayor en las preguntas de 2026 que en las de 2021-2022, porque en 2026 hay más encuestas
  cercanas entre sí.
- **PF4.** En la primera vuelta de 2026 (E3), el EAM contra la Registraduría baja con τ\*.

## 7. Lo que ya se vio, y se declara

- **Los resultados del nivel 3 con τ = ∞:** en las guardadas, EAM de 3,7 y 30 de 32 segundas vueltas; contra la
  Registraduría, 4,2 puntos y el ganador en 3 de 3.
- **Las guardadas ya se usaron una vez** para validar el nivel 3. Esta prueba las reusa. τ\* se elige sin mirarlas, pero no
  son un conjunto virgen.
- **Lo que motivó la prueba:** el ejemplo de Cepeda y De la Espriella en la página (§1). Algunas de sus encuestas están
  entre las guardadas.
- **Para comprobar que la recuperación funcionaba,** se reconstruyeron sin gasto las elecciones de la práctica y del
  guardado. Las del guardado coinciden con la salida del nivel 3. No se calculó ningún error con peso por fecha.

## 8. Lo que no se sube

Por D21:
- **Las elecciones recuperadas y la salida** quedan en `data/processed/banco/`, ignoradas por git.
- **`VOTO_PESO_FECHA_RESULTS.md`** da solo cifras de error y acierto, sin porcentajes de ningún candidato.

## 9. Código

- **Código:** `src/experiments/voto_peso_fecha.py`. `--recuperar` guarda las elecciones, sin API; sin argumentos, corre la
  evaluación.
- **Pruebas:** `tests/test_voto_peso_fecha.py`.
- **Resultados:** `VOTO_PESO_FECHA_RESULTS.md`.
