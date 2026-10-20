# PLAN V5, PASO 3: ¿CAMBIA LA CIFRA DE LOS AGENTES SI NO SE NOMBRA AL ALCALDE? — resultados

Corrido el **20 de octubre de 2026** contra `ALCALDE_SIN_NOMBRE_SPECIFICATION.md` (pre-registro y código en `5a56fd5`, antes de
llamar al modelo). **Gasto: USD 0,043** solo de B (A salió de la prueba hacia adelante; las dos juntas, USD 0,296).

Es un diagnóstico del modelo, no una predicción. La página no cambia.

## Resultados

| | Bogotá, buena o muy buena |
|---|---|
| **A, página** (con «Carlos Fernando Galán») | 27,2 % |
| **B, sin nombre** | 25,1 % |
| **El panel en la EPC 2025** (las mismas 200 personas) | 25,8 % |
| **A − B** | **+2,1** |

**Seguimiento** (probabilidad media de «buena» o «muy buena», según lo que la persona respondió en 2025):

| | Antes la calificó bien | Antes no | Diferencia |
|---|---|---|---|
| A | 80,2 | 8,6 | **71,6** |
| B | 85,2 | 4,6 | **80,6** |

## Lectura (la pre-registrada)

- **El nombre no mueve la cifra:** 2,1 puntos, por debajo de 5.
- **Los agentes siguen su propia respuesta:** el seguimiento es de 72 y 81, por encima de 60.
- **No hay valor central:** las dos cifras quedan cerca de la del panel en 2025, no lejos de ella.
- **No hay pesimismo con el gobernante:** A no queda por debajo de B ni del panel; queda 1 a 2 puntos arriba.

## Predicciones

| | Predicción | Resultado | |
|---|---|---|---|
| PN1 | El nombre no mueve la cifra | +2,1 | se cumple |
| PN2 | El seguimiento en A es menor de 60 | 71,6 | **falla** |

## Qué se aprende

1. **Cuando el perfil trae la misma pregunta, los agentes repiten la respuesta de la persona.** Ni pesimismo ni valor central: en
   esta pregunta los agentes hacen, en el fondo, una persistencia persona por persona.
2. **El nombre de Galán apenas pesa:** lo que el modelo sabe de él mueve la cifra 2 puntos, hacia arriba.
3. **Para el producto:** la cifra de Galán que hoy muestra la página (27 %) está muy cerca de la medición de la EPC 2025 (26,4 %).
   La página no dice que la cifra viene, sobre todo, de lo que respondieron esas personas en 2025.
4. **Esto no explica la réplica del alcalde.** Allí, los agentes se alejaron de la respuesta de su persona (con López en
   2023 la bajaron 8 puntos). No es por la nota de fecha: la prueba hacia adelante la lleva, y su cifra de Galán (27,3) también
   se queda en la de 2025. Queda sin explicar; no se prueba nada más sin un pre-registro nuevo.
