# ¿PASA LO MISMO CON EXPECTED PARROT? — resultados

Corrido el **20 de octubre de 2026** contra `EXPECTED_PARROT_SPECIFICATION.md` y su enmienda 1 (solo modelos baratos), antes de
ver ningún dato. **Gasto: USD 0,355** (tope USD 0,50). Lo estimado eran USD 0,20; el exceso es casi todo de DeepSeek (USD 0,23).

**Dos intentos se cayeron antes, sin respuestas ni gasto real** (nota de ejecución del pre-registro):
- el primero, por la columna de costo;
- el segundo, porque a EDSL le faltaba el paquete `openai` para hablar con OpenRouter, así que las llamadas no salieron.

Se instaló `openai` en `venv_edsl` y se corrió.

## Resultados

| Corrida | Modelo | Válidas | Buena o muy buena | Error frente a 2025 | Costo |
|---|---|---|---|---|---|
| **A**, perfiles 2025 | gpt-6-luna (el nuestro) | 200 | **22,1** | — | 0,009 |
| B, perfiles 2024 | gpt-6-luna | 200 | 29,0 | 2,6 | 0,018 |
| B, perfiles 2024 | claude-haiku-5.5 | 200 | 31,1 | 4,7 | 0,017 |
| B, perfiles 2024 | gemini-3.5-flash-lite | 200 | 25,8 | 0,6 | 0,080 |
| B, perfiles 2024 | deepseek-v4.1-flash | 176 | 32,4 | 6,0 | 0,232 |

**Las referencias:**
- la página, con los perfiles de 2025, dio 27,2;
- nuestros agentes de la Fase B, con los perfiles de 2024, dijeron 29,3;
- repetir el dato de 2024 da 42,3, y lo real de 2025 fue 26,4.

## Lectura pre-registrada

| | Criterio | Resultado | |
|---|---|---|---|
| RA | EDSL equivale a la página: \|A − 27,2\| ≤ 7 | 22,1, a 5,1 | se cumple |
| RB | Cuántos modelos «ven la caída» (cifra < 34,35) | 4 de 4 | |
| RC | Otro modelo, al menos 3 puntos mejor que el nuestro | ninguno | no se cumple |

**Predicciones:** PX1 (equivalencia) y PX2 (al menos 2 ven la caída) se cumplen.

**La conclusión pre-registrada:** EDSL da lo mismo que la página, y ningún otro modelo es mejor que el nuestro. **La herramienta y el
modelo no cambian lo que sabemos.**

## Un hallazgo no pre-registrado, y más importante

Al leer B, se calculó cuánto calificaban bien a Galán, en 2024, las mismas 200 personas que usan los agentes. **No estaba en el
pre-registro: se hizo después de ver los resultados.**

| Año base | Toda la muestra de la EPC | Los 200 del panel | Diferencia |
|---|---|---|---|
| 2022 (López) | 33,1 | 34,9 | +1,8 |
| 2023 (López) | 31,1 | 33,2 | +2,1 |
| **2024 (Galán)** | **42,3** | **31,5** | **−10,8** |
| 2025 (Galán) | 26,4 | 25,8 | −0,6 |

**Por azar, el panel de 2024 quedó con menos gente que aprobaba a Galán.** De 165 personas con respuesta, el 31,5 % lo calificaba
bien, contra el 42,3 % de toda la encuesta. Es una diferencia de casi 3 errores estándar.

**Eso explica el «acierto» de 2025:**
- los agentes de 2024 no tenían que «ver la caída»: partían de 31,5, y bajaron un poco, a 29;
- los cuatro modelos de B hicieron lo mismo, y por eso los cuatro «la vieron»;
- **repetir el dato de esas mismas 200 personas** habría dicho 31,5, con un error de 5,1;
- frente a eso, los agentes (29,3; error de 2,9) mejoran unos 2 puntos, no 13.

**Lo mismo encaja con la réplica del alcalde:**
- en 2022 → 2023 los agentes bajaron a López de 34,9 (su panel) a 25,3;
- en 2023 → 2024 no vieron la subida, porque partían de 33,2.

En los tres años, los agentes dan una cifra algo **por debajo de lo que respondió su propio panel.**

## Qué se aprende

1. **Expected Parrot no cambia nada:** con su forma de preguntar y con otras tres empresas, la cifra es la misma.
2. **El caso de Galán 2025 fue sobre todo azar de la muestra de 200,** no una capacidad de ver los cambios. Se corrige lo dicho en
   `CONTEXTO_FASE3_RESULTS.md`, `REPLICA_ALCALDE_RESULTS.md` y en los resúmenes para la otra IA y para el jefe de Daniel.
3. **200 personas son pocas para una cifra de ciudad.** El azar de elegirlas puede mover la cifra 10 puntos. La otra IA lo señaló
   («±7 por azar»), y yo respondí que no estaba medido: este dato le da la razón.
4. **La mejora más clara a la vista no es de modelos, sino de muestra:** más agentes, o ajustar el panel para que su respuesta
   anterior a la misma pregunta coincida con la de toda la encuesta. Habría que pre-registrarlo antes de probarlo.
5. **La prueba de diciembre no se ve afectada en esto:** el panel de 2025 está cerca de toda la muestra (25,8 contra 26,4).
