# COMPRESIÓN HACIA EL MEDIO — ¿cuánto aplana la estimación, y se corrige estirándola?

Pre-registro escrito el **14 de octubre de 2026**, antes de calcular nada. Lo pidió Daniel: es la prueba de «amplitud de
la opinión» del marco de validación de Artificial Societies (arXiv 2609.30030), aplicada a nuestra estimación. **Gasto: USD
0**, porque no llama a ningún modelo.

## 1. Pregunta

Las validaciones de 2026 mostraron que la estimación de preguntas nuevas se queda cerca del 50 %. Por ejemplo, en el metro,
con reales de 80 % a 93 %, dio de 56 % a 62 %.
- **¿Cuánto comprime?**
- **¿Mejora si se estira con una corrección lineal simple, aprendida de preguntas con resultado conocido?**

## 2. Datos

**Las 139 preguntas escondidas** de las pruebas del lote 8 y del catálogo, con la estimación de la página de hoy
(configuración E, `nivel_acuerdo_catalogo.json`) y su resultado real. No se llama a ningún modelo.

**Prueba externa, sin peso en la decisión:** las 13 de las validaciones 2026, con lo que dio la página.
- V5 va aparte, porque está en el banco.
- De las 7 del CNC solo se reporta el error medio (D21).

## 3. Lo que se mide

**La compresión (descriptiva):**
- la desviación estándar de las estimaciones y la de los reales;
- la pendiente de la regresión del real sobre la estimación. Si es mayor que 1, la estimación está aplanada.

**La corrección:** `estirada = a + b · estimación`, recortada a 0-100.
- **a y b** se aprenden por mínimos cuadrados.
- **Su error** se mide fuera de muestra: validación cruzada de 5 grupos por familia en las 139. Ninguna pregunta se corrige
  con a y b aprendidos de su misma familia.
- **El rango de la estirada:** el cuantil 80 % de su error fuera de muestra, igual que el ±23,4 de hoy. La llamada se calcula
  con ese rango.
- **La comparación** es contra la estimación sin estirar, con su rango de ±23,4.

## 4. Regla (escrita antes de calcular)

**La página estira la estimación si se cumplen las cuatro:**
1. **El error medio fuera de muestra baja al menos 0,5 puntos.** Hoy es 15,3.
2. **El acierto del lado no baja.** Es el mismo, porque estirar alrededor del 50 % no cambia el lado si a y b lo respetan;
   se verifica igual.
3. **Al decidir, acierta al menos el 90 %**, con su rango.
4. **En las 5 públicas de 2026 sin V5, el error medio no sube** (hoy, 19,9).

**Si se cumplen,** se aplica con a y b aprendidos de las 139, y el texto de la página cita las cifras fuera de muestra. Eso
va con su propia decisión (DI-CO40) y el visto bueno de Daniel.

## 5. Predicciones (escritas antes de calcular)

- **PC1.** La estimación está aplanada: la desviación estándar de las estimaciones es menor que la de los reales, y la
  pendiente es mayor que 1.
- **PC2.** Estirar baja el error fuera de muestra menos de 1 punto. Si lo que comprime es que no sabe, estirar también
  agranda los errores donde se equivoca de lado.
- **PC3.** La estirada se compromete («probablemente») en más preguntas que la de hoy (14 de 139).
- **PC4.** No se cumple la regla.

## 6. Datos y código

- **Nada sale del equipo:** las 139 incluyen preguntas del CNC (D21). Solo se reportan cifras agregadas.
- **Código:** `src/experiments/compresion.py`, con su prueba. Resultados en `COMPRESION_RESULTS.md`.
