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

## Parte A — estabilidad ante la reformulación (6/10/2026, con Luna; enmiendas 1 y 2)

**Veredicto: la cifra de la página no se sostiene.** Con la reformulación que hace la página, Luna estima peor que
con el texto original, y las tres condiciones de la regla fallan.

**La corrida:**
- reformulación con mimo, la de la página;
- estimación con GPT-6 Luna, con h = 23,4 (D20, enmienda 2);
- 84 de las 95 quedaron como `nueva` y las 84 tienen estimación. No hubo errores del servicio ni respuestas sin ids.
- **Gasto de la parte A:** USD 1,61 en total. De eso, USD 1,51 es la primera corrida con Sonnet, incompleta y sin evaluar
  (guardada como `A_sonnet_parcial`); unos USD 0,10 son las estimaciones con Luna.

| En las 84 | Texto reformulado (la página) | Texto original | Regla |
|---|---|---|---|
| Error (EAM) | **16,2** | 14,0 | ≤ 14,0 + 1,5: **no cumple** |
| Acierto del lado | **63 %** | 69 % | ≥ 69 % − 5: **no cumple** |
| Decide (acierta) | 6 (5, 83 %) | 10 (9, 90 %) | ≥ 90 %: **no cumple** |
| Real dentro del rango | 77 % | 79 % | |
| …en las extremas (37) | **54 %** | 70 % | |
| …en las intermedias (47) | 96 % | 85 % | |
| Error, extremas / intermedias | 22,4 / 11,3 | 16,7 / 12,0 | |

**Estabilidad:**
- |S reformulada − S original| es de 7,3 puntos en promedio y pasa de 20 en 10 de las 84;
- la llamada coincide en el 86 %;
- en 53 de 84 la estimación reformulada queda más cerca del 50 %.

**Predicciones:**

| | Predicción | Resultado | |
|---|---|---|---|
| PA1 | \|ΔS\| medio ≥ 4 puntos | 7,3 | se cumple |
| PA2 | La llamada coincide en ≥ 80 % | 86 % | se cumple |
| PA3 | El EAM con reformulación es mayor | 16,2 > 14,0 | se cumple |
| PA4 | La regla no se cumple | no se cumple | se cumple |
| PA5 | ≥ 90 % quedan como `nueva` | 84 de 95 (88 %) | **falla** |

**Dónde se pierde.**
- **Las intermedias no empeoran:** el error baja de 12,0 a 11,3.
- **Todo se pierde en las extremas:** el error sube de 16,7 a 22,4. La causa está en la reformulación, que a veces cambia el
  sentido de la pregunta, y no en Luna. Los cinco cambios mayores:
  - **invierte el sentido:** «da igual si se separan los residuos» pasa a «separar los residuos contribuye…» (de 23 a 61; real, 18);
  - **convierte una idea general en un juicio sobre Bogotá:** «la democracia se relaciona con el desarrollo» pasa a «contribuye al
    desarrollo económico de Bogotá» (de 70 a 43; real, 77);
  - **añade «en Bogotá»,** o cambia «tomar espacios públicos» por «utilizar espacios públicos».

**Qué dice el pre-registro (§2): no se sostiene.**
1. Se propone a Daniel cambiar el texto de la página por las cifras medidas con la reformulación: 63 % del lado de la mayoría;
   al decir «probablemente», 5 de 6.
2. Se propone, como siguiente prueba pre-registrada, darle al modelo el texto que escribió la persona en lugar del reformulado.
   La prueba de `LUNA_PAGINA` (parte 2) mide además si reformular con Luna cambia menos el sentido.

