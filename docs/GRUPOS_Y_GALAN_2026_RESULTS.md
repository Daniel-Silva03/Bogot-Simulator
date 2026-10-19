# AGENTES 2026: EL VOTO POR GRUPOS Y LA APROBACIÓN DE GALÁN — resultados

Corrido el **16 de octubre de 2026** contra `GRUPOS_Y_GALAN_2026_SPECIFICATION.md` (pre-registro y código en `b9f0631`, antes
de calcular).

**Gasto:**
- **parte A:** USD 0, desde la caché;
- **parte B:** USD 0,092.

## Parte A. El voto por grupos

Los 200 agentes con la campaña y la encuesta (C2), en la parte de Cepeda entre los dos primeros, contra el CNC de mayo de 2026 en
Bogotá. Por D21, sin cifras del CNC.

| | Resultado |
|---|---|
| Error por grupo de los agentes (8 grupos) | 6,6 |
| Error de «la ciudad para todos» | 5,5 |
| Brechas en la dirección correcta | 1 de 3: el estrato sí; el sexo y la edad, no |
| Agentes sin respuesta en la caché | 2 de 200 |

| | Criterio | Resultado | |
|---|---|---|---|
| RA1 | error por grupo al menos 1 punto menor que la ciudad para todos | 6,6 contra 5,5: mayor | **no se cumple** |
| RA2 | signo correcto en al menos 2 de 3 brechas | 1 | **no se cumple** |

**Los agentes no reparten bien el voto por grupos.**

| | Predicción | Resultado | |
|---|---|---|---|
| PA1 | Estrato y edad en la dirección esperada | solo el estrato | **falla** |
| PA2 | RA1 no se cumple | no se cumple | se cumple |

**El límite de la vara:** con unos 305 encuestados del CNC en Bogotá, cada grupo tiene un margen de ±8 a ±14 puntos. Parte de la
diferencia es ruido del CNC, pero los agentes quedan peor que no distinguir grupos.

## Parte B. La aprobación de Galán en 2026

| | Real | P, sin opiniones de gobierno | F, con todo el perfil |
|---|---|---|---|
| G1, aprueba la gestión (Guarumo, abril de 2026) | 53,3 | **54,9** | 42,6 |
| G2, imagen positiva (Global CB, junio de 2026) | 44,3 | 57,9 | **46,9** |
| **Error medio** | | 7,6 | **6,6** |

**Las referencias:**
- **la imagen favorable en la EPC 2025 (45,0):** error medio de 4,5;
- **decir 50 %:** error medio de 4,5.

| | Criterio, en F | Resultado | |
|---|---|---|---|
| RB1 | error medio ≤ 7 | 6,6 | se cumple |
| RB2 | error medio menor que el de la EPC 2025 (4,5) | 6,6 | **no se cumple** |

**Por la regla, los agentes no se acercan más a Galán en 2026 que el dato de 2025.**

| | Predicción | Resultado | |
|---|---|---|---|
| PB1 | F se acerca más que P | 6,6 contra 7,6 | se cumple |
| PB2 | No le gana a la EPC 2025 en G2 | 2,6 contra 0,7 | se cumple |
| PB3 | En G1 los agentes quedan por debajo de 53,3 | F da 42,6 | se cumple |

## Qué se aprende

1. **Cada variante acierta una de las dos.**
   - **Sin opiniones de gobierno (P),** la aprobación de Guarumo sale casi exacta: 54,9 contra 53,3.
   - **Con su opinión de 2025 (F),** la imagen de Global CB sale cerca: 46,9 contra 44,3.

   En promedio ninguna baja de 4,5. Con dos cifras, de dos encuestadoras con preguntas y muestras distintas, la prueba es frágil.
2. **Las dos encuestas de 2026 no cuadran entre sí:** 53 % aprueba en abril y 44 % de imagen positiva en junio. Puede ser una caída
   de Galán o la forma de preguntar, y los agentes no pueden saber cuál.
3. **Por grupos, los agentes todavía no sirven:** el reparto por sexo y edad sale en la dirección equivocada.

**En corto:** los agentes llegan cerca de Galán en 2026 (a 2 puntos en una medición o en la otra, según cómo se arme el perfil),
pero no le ganan al dato de 2025. No reparten bien el voto por grupos. Para avanzar en lo político hacen falta más mediciones de
2026 contra las cuales comparar. La EPC 2026, en diciembre, sería la prueba más limpia.
