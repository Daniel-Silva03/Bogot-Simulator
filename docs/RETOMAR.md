# RETOMAR — dónde quedó la sesión del 2-5/10/2026 (PC del CNC)

**Para seguir en otro computador. Léelo después de `ESTADO_DEL_PROYECTO.md`.**

## Lo pendiente (lo primero al retomar)

**Actualización 5/10:** la parte B ya terminó (`NIVEL_PARECIDAS_B_RESULTS.md`). Lo que sigue de esta nota
sobre la pausa queda como registro.

**La parte B del nivel está en pausa porque la cuenta de OpenRouter no tiene saldo**
(`NIVEL_PARECIDAS_B_SPECIFICATION.md`; código `src/experiments/nivel_parecidas_b.py`).

- **Hecho:** 24 de 96 preguntas con Claude Sonnet 5.5 y 7 de 96 con DeepSeek V4 Pro, más las dos
  llamadas de prueba. Gasto registrado: **USD 0,548**, de un tope de USD 4 aprobado por Daniel.
- **El corte:** OpenRouter respondió 402 («Payment Required»). La cuenta, que es la del jefe de
  Daniel y compartida con otras claves, tenía USD 625 de crédito y ~USD 624,27 usados al 5/10. Esta
  clave lleva solo USD 4,38 de ese uso.
- **Para retomar** hacen falta al menos **USD 3 libres**; lo que falta cuesta ~USD 1,70. Antes de
  correr, revisa el saldo con `/api/v1/credits` (consulta gratuita) y avísale a Daniel. Después:

  ```
  python src/experiments/nivel_parecidas_b.py --modelo sonnet
  python src/experiments/nivel_parecidas_b.py --modelo deepseek
  python src/experiments/nivel_parecidas_b.py          # junta los dos desde la caché, sin llamadas nuevas
  ```

  La caché `data/processed/banco/cache_nivel_b.json` **no está en GitHub**. Sin ella, en otro
  computador se vuelven a pagar las 33 respuestas (~USD 0,55): llévala con `empacar_traslado.py` o a
  mano.
- **Los resultados parciales no se han mirado.** El pre-registro se evalúa con las 96 preguntas.

## Lo que se hizo del 2 al 4/10 (todo en GitHub)

1. **D18 en la página:** una pregunta nueva no tiene cifra propia. Empieza diciendo «No podemos decir
   si Bogotá estaría de acuerdo» (DI-CO20) y muestra preguntas parecidas con su dato real y el tono
   por grupo. También se arreglaron las escalas numéricas, el lado favorable y «no tiene opinión»
   (DI-CO17 a DI-CO19; `PAGINA_CONSULTA.md` §5.8-5.11).
2. **Tres pruebas pre-registradas, sin gasto:**
   - `TECHO_GRUPOS_RESULTS.md`: lectura A, hay espacio. El techo está en 86-95 % contra el 62 % del
     simulador; lo que falta es información.
   - `NIVEL_PARECIDAS_RESULTS.md`: ni el tema ni el texto acercan el nivel (22-23 puntos de error);
     con preguntas hermanas ya medidas, 16.
   - `NIVEL_FORMA_RESULTS.md`: la forma de la pregunta tampoco (22,3).
3. **Camino 3, propuesto a Daniel y sin respuesta:** pedir al CNC resultados agregados de preguntas
   de aprobación de medidas en Bogotá. Es lo único que las pruebas dicen que acercaría el nivel.

## Otras cosas abiertas

- En el PC del CNC falta el módulo de Democracia de la ECP 2013: `tests/test_experimento9.py` falla
  en 1 de 52 (`test_todo_simulado_sobre_los_datos_reales`). Ya fallaba antes; no es de esta sesión.
- `revisar_datos.py` no revisa todos los años de la EPC. En el PC del CNC faltaban 2015 y 2017, y
  Daniel los copió el 2/10.
- Segunda vuelta 2026 (`SEGUNDA_VUELTA_2026_SPECIFICATION.md`): esperando los datos mesa a mesa del CNC.
- El banco guardado (51 preguntas) sigue sin usarse.
- La memoria de Claude (`~/.claude/…`) no viaja con el repo. Lo que importa de ella: **antes de
  cualquier gasto en API, decirle a Daniel cuántas llamadas son y cuánto cuestan, y esperar su sí**
  (~USD 0,004 por llamada con el modelo de la página; Sonnet 5.5, ~USD 0,022).
