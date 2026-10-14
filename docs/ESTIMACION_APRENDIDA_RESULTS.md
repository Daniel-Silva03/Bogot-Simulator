# ESTIMACIÓN APRENDIDA — resultados

Corrido el **14 de octubre de 2026** contra `ESTIMACION_APRENDIDA_SPECIFICATION.md` (pre-registro y código en `98279e1`,
antes de pedir embeddings).
- **Gasto:** USD 0,0002: 390 textos con `intfloat/multilingual-e5-large`.
- **Aquí solo hay cifras de error y acierto** (D21).

## 1. Resultado

**Los parámetros, elegidos solo con el entrenamiento** (validación cruzada de 5 grupos por familia):

| Modelo | Parámetro | EAM en la validación cruzada | Rango (cuantil 80 %) |
|---|---|---|---|
| M1, ridge | α = 1 | 16,8 | ±25,5 |
| M2, vecinos | k = 5 | 16,6 | ±25,1 |

**En los 139 objetivos:**

| | E (la página hoy) | M1, regresión | M2, vecinos semánticos | M3, media de M1 y E |
|---|---|---|---|---|
| Error (EAM) | **15,3** | 18,0 | 18,1 | 16,1 |
| Acierto del lado | **73 %** | 71 % | 67 % | 73 % |
| Decide | 14 (10 %) | 0 | 0 | 0 |
| Acierta al decidir | **13 de 14** | — | — | — |
| Pasa la validación de siempre | sí | no | no | no |

**Ninguno cumple la regla: la página sigue con E.** Ninguno baja el error, y con su rango (±25) ninguno se compromete nunca.

| | Predicción | Resultado | |
|---|---|---|---|
| P1 | Ninguno reemplaza a E | ninguno | se cumple |
| P2 | M3 tiene el menor EAM de los tres | 16,1 | se cumple |
| P3 | M1 queda a menos de 1 punto de E (14,3 a 16,3) | 18,0 | **falla** |
| P4 | En las 5 públicas de 2026 sin V5, ninguno baja el error de la página (19,9) | 26,7 a 33,5 | se cumple |

**La prueba secundaria** (errores medios, sin peso en la decisión):

| | Página | M1 | M2 | M3 |
|---|---|---|---|---|
| Las 5 públicas de 2026, sin V5 | **19,9** | 33,5 | 30,7 | 26,7 |
| V5 (está en el banco) | 1,2 | 7,8 | 0,2 | 4,5 |
| Las 7 del CNC de 2026 (decir 50 %: 10,6) | 12,7 | **10,0** | 11,5 | 10,1 |

## 2. Qué se aprende

1. **Luna elige mejor que el parecido de significado.** Elegir preguntas «del mismo tema» con embeddings da 18 puntos de
   error. Luna, que elige las que cree que tendrán un porcentaje parecido, da 15. Su criterio aporta algo que la similitud
   del texto no tiene.
2. **Con 238 ejemplos no hay de dónde aprender.** La regresión queda 2,7 puntos peor que E. Los estudios que lo lograron
   (SubPOP) entrenaron con decenas de miles de preguntas.
3. **Mezclar no ayuda:** la media de M1 y E (16,1) queda entre las dos, peor que E.
4. **La única señal a favor** está en las 7 del CNC de 2026: la regresión da 10,0, contra 12,7 de la página, y apenas por
   debajo de decir 50 % (10,6). Son 7 preguntas, sin peso en la decisión, y en las 5 públicas pasa lo contrario.

**La conclusión de la opción A:** con el banco que tiene el proyecto, aprender del texto no mejora la estimación de hoy.
Para que sirviera haría falta un banco mucho mayor, de miles de preguntas de Bogotá con resultado. O la opción B: gemelos
hechos con entrevistas reales.
