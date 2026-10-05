# ¿ESTARÍA BOGOTÁ DE ACUERDO? — la redacción de la página y el estiramiento: resultados

Contra el pre-registro `NIVEL_ACUERDO_REDACCION_SPECIFICATION.md` (commit `c791ed0`).
- **Código:** `src/experiments/nivel_acuerdo_redaccion.py`.
- **Salida:** `data/processed/banco/nivel_acuerdo_redaccion.json`.

## Parte B — estirar o encoger la estimación (5/10/2026, sin gasto)

**Veredicto: no se propone ninguna de las dos correcciones.** La estimación actual (S) se queda como está.

| Dónde | Método | EAM | Lado | Decide (acierta) | Cobertura | Extremas | Intermedias |
|---|---|---|---|---|---|---|---|
| Práctica, 92 (validación cruzada por familia) | S | **13,9** | 80 % | 16 (100 %) | 79 % | 69 % | 87 % |
| | E1, estirar | 15,5 | 80 % | 24 (100 %) | 75 % | 64 % | 83 % |
| | E2, recta | 14,4 | 80 % | 11 (100 %) | 74 % | 54 % | 89 % |
| Guardadas, 95 | S | 11,9 | 72 % | 17 (100 %) | 84 % | 68 % | 96 % |
| | E1, estirar | **11,8** | 72 % | 22 (100 %) | 87 % | **78 %** | 95 % |
| | E2, recta | 13,0 | 72 % | 8 (100 %) | 82 % | 60 % | 98 % |

**Parámetros,** con toda la práctica:
- **E1:** S′ = 48,9 + 1,27 (S − 48,9), con h = 24,3;
- **E2:** S′ = 4,4 + 0,85 S, con h = 22,0;
- **S:** h = 21,9, el mismo de la página.

**La regla:**
- **E1 no se propone.** En las guardadas cumpliría las tres condiciones: EAM 11,8 contra 11,9, cobertura en las
  extremas +10 puntos y 22 de 22 al decidir. En la práctica, en cambio, empeora el error (15,5 contra 13,9) y
  *baja* la cobertura en las extremas (64 % contra 69 %). La regla pedía los dos lugares.
- **E2 no se propone.** Empeora el error en los dos lugares.

**Predicciones:**

| | Predicción | Resultado | |
|---|---|---|---|
| PB1 | E1 no se propone: su EAM sube más de 0,5 en algún lugar | sube 1,6 en la práctica | se cumple |
| PB2 | E1 sube la cobertura en las extremas y la baja en las intermedias | en las guardadas sí (+10 y −1); en la práctica baja las dos | **falla** |
| PB3 | E2 no se propone: su mejora es menor que 0,5 en algún lugar | empeora en los dos | se cumple |
| PB4 | S sigue siendo la mejor opción disponible | ni E1 ni E2 se proponen | se cumple |

**Lectura:**
- **Lo que falta es información, no una corrección.** La estimación se queda en el medio porque es
  imprecisa: la correlación con el real es de 0,67 en la práctica. Estirarla agranda también el error de las
  preguntas en que se equivoca. Que E1 se vea bien en las guardadas y mal en la práctica es lo que se espera de
  una diferencia que no es estable.
- **Lo que esto no prueba.** La parte B no es una validación independiente (pre-registro §1): las guardadas ya
  se habían usado y el umbral de «extremo» se fijó después de verlas.
- **El rango funciona como se diseñó:** 84 % de cobertura en las guardadas, para un rango del 80 %. Pero no es
  parejo: cubre el 96 % de las intermedias y el 68 % de las extremas. La página no lo dice.

## Parte A — estabilidad ante la reformulación

~~**Pendiente.** Espera el sí de Daniel al gasto (~USD 2,7, con tope de USD 3,50) y la llamada de prueba.~~

**En pausa (5/10):** la primera corrida quedó incompleta. La cuenta se quedó sin saldo y 37 preguntas no se
estimaron. No se evalúa; ver la enmienda 1 del pre-registro (§5).
- **Gasto:** USD 1,51.
- **Para retomar:**
  - recargar la cuenta (lo que falta cuesta ~USD 0,9);
  - correr `python src/experiments/nivel_acuerdo_redaccion.py`, que sigue desde la caché.
