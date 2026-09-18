# SCENARIO SPECIFICATION — el motor de escenarios (Fase 8)

Proyecto: Bogotá Social Simulator
Versión: 1.0
Fecha: 17 de septiembre de 2026
Código: `src/scenarios/` (`especificacion.py`, `motor.py`, `informe.py`) · `tests/test_scenarios.py`, 13 pruebas
Escenarios de ejemplo: `config/escenarios/`

---

## 1. Qué es un escenario en este proyecto

Siete experimentos pre-registrados establecieron que **no hay mecanismo de dinámica de opinión identificable** con los datos públicos disponibles, y que dos números exógenos por periodo llevan el ajuste al piso de ruido muestral (`claude/FORZAMIENTO_CATEGORICO.md`).

Eso no es una limitación que el motor tenga que disimular: **es lo que define qué es un escenario aquí.**

> Un escenario no es una predicción que el modelo genera. Es un **supuesto que alguien declara**, y cuyas consecuencias distribucionales el motor calcula.

El usuario dice *"la confianza cae 0,10 puntos por año durante tres años"*; el motor responde con la distribución completa que eso implica, con su incertidumbre, y con la comparación contra no hacer nada. No al revés.

## 2. Cómo se declara

Un archivo YAML. El del ejemplo de polarización, entero:

```yaml
nombre: "Polarización sin cambio de nivel"
descripcion: >
  La confianza promedio no se mueve, pero la población se separa.
poblacion: data/processed/poblacion_epc2014.csv
columna: opinion_t0
etiqueta_variable: "Gestión del alcalde (escala 1-5)"
corridas: 200
semilla: 7
periodos:
  - etiqueta: "Año 1"
    nivel:      {cambio: 0.0,   incertidumbre: 0.05}
    dispersion: {cambio: +0.10, incertidumbre: 0.03}
  - etiqueta: "Año 2"
    nivel:      {cambio: 0.0,   incertidumbre: 0.06}
    dispersion: {cambio: +0.10, incertidumbre: 0.04}
```

**La incertidumbre es obligatoria** (DI-E1). Puede ser 0, pero hay que escribirlo. Un escenario sin incertidumbre declarada produce una línea, y una línea se lee como predicción — el riesgo R05, que el proyecto tiene marcado como elevado. Que la decisión quede en el archivo y no en el olvido.

**El cambio es relativo al periodo anterior** por defecto (DI-E2): un escenario es una historia sobre lo que pasa, no una lista de destinos. `valor:` absoluto existe para replicar una serie observada.

**La grilla sale de la población, no del archivo** (DI-E4). Es una propiedad de la variable medida, y dejar que un YAML la declare invita a inventarse una escala que los datos no tienen.

## 3. Qué calcula

Cada corrida sortea **tres cosas independientes** (DI-M1s):

1. **La población** — se remuestrean N agentes con reemplazo de la base. Es el error muestral, el mismo que fija el piso de ruido contra el que se validó todo.
2. **Los supuestos** — de las incertidumbres declaradas.
3. **El reparto** de agentes dentro de las categorías.

El forzamiento es el **ladeo categórico** (DI-M4s), no el afín: la distribución se mueve sobre el soporte real de la variable. Usar el afín aquí produciría escenarios en los que la gente responde 2,37 en una escala de cinco opciones.

### Tres cosas que el motor hace y que no son opcionales

**El escenario nulo se corre siempre** (DI-M2s). Es el mismo escenario con todos los cambios en cero: la población quieta, con su propia incertidumbre muestral. Ninguna cifra significa nada sin él al lado, porque la pregunta útil nunca es *"¿cuánto da?"* sino ***"¿cuánto más que no hacer nada?"***.

**La incertidumbre se descompone.** `descomponer()` corre el escenario apagando una fuente a la vez. En el ejemplo de la caída sostenida, el 91 % del margen viene del supuesto y el 26 % de la muestra. Eso cambia qué hacer: **si domina la muestral, la respuesta no es afinar el supuesto, es subir N** — y al revés.

**Los escenarios imposibles se rechazan al cargar, no al correr** (DI-E3). En una escala acotada no todo par (media, sd) existe: fijada la media, la desviación tiene un máximo (masa en los extremos) y un mínimo (masa en las categorías vecinas). Se verifica la trayectoria central **y los bordes de la incertidumbre declarada**, porque de nada sirve que el centro sea factible si la mitad de las corridas se va a caer. El error nombra el periodo y el rango alcanzable.

## 4. El informe

`src/scenarios/informe.py` produce un HTML autocontenido. **Es parte del producto, no un adorno**: el sitio donde el riesgo R05 se materializa es exactamente el gráfico que alguien va a poner en una presentación.

- **Nunca se dibuja una línea sola** (DI-I1). Toda trayectoria va con banda p05-p95 y p25-p75, y con el escenario nulo al lado.
- **El supuesto declarado se imprime completo**, con sus incertidumbres, **arriba** de los resultados (DI-I2).
- **La descomposición de la incertidumbre es visible**, con una frase que dice qué hacer con ella (DI-I3).
- **El gráfico de distribución se adapta a la escala** (DI-I4): barras con pocas categorías, área con muchas.
- **Las advertencias van al pie de cada informe**, no en la documentación (DI-I5): que esto no predice, que la red no aporta, que la incertidumbre mostrada no cubre el error de que el supuesto esté equivocado.

El aviso de la cabecera es literal y no se quita:

> **Esto no es una predicción.** El nivel y la dispersión de cada periodo son supuestos declarados, no resultados del modelo.

## 5. Lo que el motor deja ver, y que un promedio esconde

El escenario de polarización es el argumento de por qué existe el simulador. El nivel **no se mueve** —2,88 al principio y 2,88 al final, diferencia de 0,1 veces el error— y sin embargo la distribución se transforma: las categorías 1 y 5 crecen de 19 % a 32 % y de 12 % a 25 %, mientras las centrales se vacían.

Un informe de encuesta que reportara la media no vería nada. Es exactamente el tipo de pregunta para el que un laboratorio de escenarios sirve, y no requiere ningún mecanismo social para responderla.

## 6. Qué NO hace, y es deliberado

- **No predice los supuestos.** Alguien los declara. Si esa persona se equivoca, el informe está equivocado, y la incertidumbre mostrada **no** cubre ese error — lo dice el pie del informe.
- **No usa la red.** No aporta nada medible al ajuste (Experimentos 4-7). Sigue disponible como sensibilidad, nunca como mecanismo.
- **No desagrega por localidad.** El territorio explica ~1 % de la varianza de opinión y más de la mitad de eso es ruido muestral (D15). Un mapa de Bogotá coloreado por opinión simulada sería el gráfico más vendedor y el más engañoso del proyecto (§31 de `PROJECT_CONTEXT.md`).
- **No guarda estado en una base de datos ni expone una API.** `ARCHITECTURE.md` preveía PostgreSQL + PostGIS + FastAPI + React. Hoy no hay nada en el modelo que necesite una base de datos espacial: un escenario es un YAML, una corrida son segundos, y la salida es un archivo. Se agrega cuando haga falta de verdad — Principio 5, la misma razón por la que no hay capa Mesa.

---

*13 pruebas en `tests/test_scenarios.py`, entre ellas que la incertidumbre es obligatoria, que un escenario imposible se rechaza al cargar mirando también los bordes, que el nulo conserva incertidumbre muestral, que la salida nunca es una línea, y que la descomposición separa las fuentes.*
