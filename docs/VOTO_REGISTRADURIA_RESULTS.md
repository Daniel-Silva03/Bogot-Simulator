# INTENCIÓN DE VOTO SIMULADA, PARTE 2 — contra la Registraduría en Bogotá: resultados

Corrido el **7 de octubre de 2026** contra `VOTO_REGISTRADURIA_SPECIFICATION.md` (pre-registro y código en `c29e662`, antes
de llamar y antes de calcular ningún resultado).
- **Comando:** `python src/experiments/voto_registraduria.py`, con `BSS_ELECTORAL_DIR` en `Desktop\CNC_datos`.
- **Gasto:** USD 0,024 en 21 llamadas.
- **Solo cifras de error y aciertos,** sin porcentajes de las encuestas ni de la simulación (D21).

## 1. Resultado

Porcentajes normalizados entre los candidatos de cada elección, contra el resultado oficial de Bogotá:

| Elección | Candidatos | EAM de la simulación | EAM de la última encuesta | ¿Primero correcto? (sim. / encuesta) |
|---|---|---|---|---|
| Primera vuelta 2022 | 8 | 3,8 | 3,2 | sí / sí |
| Segunda vuelta 2022 | 2 | 5,5 | 5,5 | sí / sí |
| Primera vuelta 2026 | 11 | 3,4 | 2,6 | sí / sí |
| **Promedio** | | **4,2** | **3,8** | 3 de 3 / 3 de 3 |

**En la segunda vuelta de 2022,** la simulación y la última encuesta dan exactamente lo mismo. Luna eligió la propia pregunta
medida de esa segunda vuelta («Rodolfo Hernández contra Gustavo Petro», abril de 2022). La diferencia entre los dos candidatos
se equivoca en 11 puntos en ambas.

## 2. Contra el pre-registro

| | Predicción | Resultado | |
|---|---|---|---|
| PR1 | La última encuesta queda más cerca que la simulación en ≥ 2 de 3 | más cerca en 2, empate en 1 | se cumple |
| PR2 | La simulación pone primero al ganador de Bogotá en ≥ 2 de 3 | 3 de 3 | se cumple |
| PR3 | EAM promedio de la simulación ≤ 8 | 4,2 | se cumple |

## 3. Lectura

- **Contra lo que votó Bogotá, la simulación se equivoca unos 4 puntos en promedio**, medio punto más que la última encuesta.
  En las tres elecciones acierta quién ganó en Bogotá.
- **Cuando existe una encuesta reciente que hace la misma pregunta,** la simulación la encuentra y la reproduce, o casi. No la
  supera. Su valor está en las preguntas que nadie hizo, como en la parte 1.
- **Lo que esto no prueba:**
  - son tres elecciones;
  - el resultado depende también de quién votó y de los cambios de última hora;
  - y el EAM normalizado mezcla candidatos grandes y pequeños, como en la parte 1.
- **Con las partes 1 y 2,** el nivel 3 queda validado para Bogotá en total. **Sigue sin mostrarse en la página hasta la revisión
  jurídica** (D21).
