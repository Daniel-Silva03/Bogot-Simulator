# PÁGINA DE CONSULTA — Bogotá Sintética

**La página nueva del proyecto (D17): cualquiera le hace una pregunta de opinión a la población sintética y ve cómo respondería, en total, por grupos y, cuando hay con qué, por localidad. Todo rotulado como suposición.**

Proyecto: Bogotá Social Simulator
Versión: 0.2 (rediseño con `DESIGN.md`, 30/09/2026)
Fecha: 30 de septiembre de 2026
Código: `src/consulta/` (`motor.py`, `servidor.py`, `pagina.html`, `reformular.py`) · Pruebas: `tests/test_consulta.py` (8), `tests/test_reformular.py` (7)
Reemplaza, como cara del proyecto, al tablero de `src/viz/` (que se conserva, sin cambios)

---

## 1. Cómo se abre

Es un **servidor local**, no un HTML suelto: la página llama a un modelo de lenguaje y la
clave de OpenRouter no puede viajar al navegador. Solo escucha en `127.0.0.1`.

```
.\venv\Scripts\Activate.ps1
$env:OPENROUTER_API_KEY = Read-Host "Clave de OpenRouter"
python src/consulta/servidor.py              # http://127.0.0.1:8765
python src/consulta/servidor.py --simulado   # sin clave ni gasto, para mirar la página
```

Necesita la población EPC 2023 construida (`python src/population/poblacion_epc.py`) y el
microdato de la EPC en su ruta (`BSS_EPC_DIR`).

**Gasto:** una pregunta del catálogo cuesta una llamada (la reformulación, unos USD 0,003);
una nueva, dos (reformulación y puente, unos USD 0,006). Las respuestas se guardan en
`data/processed/consulta/cache.json`, que no se sube: repetir una pregunta no cuesta.

---

## 2. Qué tiene la página

1. **Portada:** qué es («¿Qué opinaría Bogotá si…?»), tres cifras (20.000 personas
   sintéticas, 1.501 encuestados reales, 19 localidades) y el aviso de que es un
   experimento, no una encuesta ni una predicción.
2. **Cómo funciona:** cuatro pasos ilustrados y los tres tipos de pregunta (ya medida,
   nueva, fuera de alcance), con un ejemplo de cada una.
3. **Pregúntale a Bogotá:** el campo de la pregunta con ejemplos; la sugerencia de
   reformulación (editable); el resultado; y el mapa grande al lado.
4. **Qué hay detrás:** la población, el puente y los límites.

**Lo que ya no está:** los botones de capas (opinión, población, crecimiento, voto) y la
línea de tiempo del tablero. El mapa muestra por defecto **información general**: adultos
por localidad (en color), estrato medio y cuántos encuestados de la EPC viven ahí.

---

## 3. Qué muestra cada tipo de respuesta

| Tipo | Resultado | Mapa |
|---|---|---|
| **Ya medida** (catálogo) | % en la mitad alta de la escala, la distribución completa y el mismo % por estrato, edad, sexo y educación | Promedio por localidad en la escala completa, con su margen del 95 % en la ficha |
| **Nueva** (puente) | Nivel de la ciudad propuesto por el modelo, **editable** con un deslizador; cuánto más o menos de acuerdo estaría cada grupo (en desviaciones estándar); las preguntas medidas en las que se apoya | **No se dibuja por localidad** (lectura B del puente), y la página dice por qué |
| **Fuera de alcance** | La razón, y una alternativa que, si se elige, vuelve a pasar por la reformulación (DI-CO4) | — |

En todas: una banda que dice que es una suposición, no una medición.

---

## 4. Decisiones (detalle en los docstrings)

- **DI-CO1:** el margen de una localidad es el de la encuesta (remuestreo de manzanas),
  no el de los 20.000 agentes.
- **DI-CO2:** una pregunta nueva no tiene mapa, y sus grupos van en desviaciones
  estándar, no en porcentajes: el puente ordena, no dice cuántos.
- **DI-CO3:** en la página el puente usa las 102 preguntas del catálogo.
- **DI-CO4:** una alternativa sugerida no se responde directo; se reformula.
- **DI-SE1 a DI-SE3:** solo localhost, sin librerías nuevas, cada consulta independiente.
- **La escala del mapa es la de la pregunta completa** (como DI-V34 del tablero), no la
  del mínimo al máximo observado.

---

## 5. Verificación (30/09/2026)

- `tests/test_consulta.py`, 8 pruebas con el modelo simulado: la respuesta del catálogo
  (distribución que suma 1, 19 localidades, cada media dentro de su margen, márgenes de
  más de 0,2 puntos), el «no sabe» fuera de la media, la pregunta nueva sin mapa y con
  grupos que promedian cero, un puente roto que se dice y no se responde, y el servidor
  con sus tres rutas, solo en `127.0.0.1` y sin los botones de antes.
- Revisada en el navegador en modo simulado: escritorio y celular (375 px, sin
  desplazamiento horizontal), claro y oscuro, los cuatro recorridos (catálogo, nueva,
  fuera de alcance con alternativa, respuesta inválida), sin errores en la consola.
- **No se ha abierto con el modelo real todavía.**

---

## 5.1 Rediseño con el sistema de Daniel (30/09/2026, v0.2)

Daniel entregó un `DESIGN.md` («bioluminescent control room»): oscuro, bicromático
(neutros casi negros + menta), titulares en peso 300 con tracking negativo, botones
siempre en píldora, tarjetas planas sin sombra, y un brillo verde radial solo detrás de la
«vitrina» (aquí, el espacio de preguntar). Se aplicó completo, con tres adaptaciones:

- **Tipografías:** Inter y JetBrains Mono, los sustitutos que nombra el propio documento
  (Euclid Circular A y Onsite SemiMono son de pago).
- **Colores del mapa:** el sistema no admite otros tonos, así que la rampa de datos va del
  pino a la menta pálida; la menta eléctrica queda para la acción principal y la
  localidad seleccionada.
- **Texto secundario más claro** que el gris del documento (#5e6262), que sobre #000a06 no
  se lee.

La página es ahora solo oscura. La portada va centrada, con dos botones (menta + fantasma).

**Tres defectos que se corrigieron en el camino:**
1. **El «amarillo» al tocar una localidad** (lo reportó Daniel): el foco del teclado dibuja
   un contorno, y en un SVG que mide en grados ese contorno se agranda miles de veces y
   tapa todo el mapa. Ahora la selección y el foco se marcan con el borde de la localidad.
2. **Los nombres de las localidades se veían como letras sueltas:** el tracking negativo
   del sistema, heredado dentro del SVG en grados, amontonaba las letras. El mapa usa
   tracking 0.
3. **La sección de preguntar se corría de lado** al saltar al mapa: su brillo de fondo es
   más ancho que la pantalla y `overflow:hidden` deja que el navegador la desplace. Se
   cambió a `overflow:clip`. De paso, parques y vías se recortan al contorno de la ciudad.

**El mapa con cada pregunta:** con una del catálogo se colorea con la respuesta; con una
nueva se apaga y dice en el centro por qué no se dibuja (lectura B del puente). Esto
último es a propósito.

## 6. Límites que la página dice

No predice ni reemplaza una encuesta; opina como Bogotá en 2023; unas 80 personas por
localidad dan márgenes anchos (la confiabilidad de las medias por localidad es baja,
`PUENTE_RESULTS.md` §4); Sumapaz no tiene encuestados; el nivel de una pregunta nueva lo
propone el modelo y se puede cambiar.
