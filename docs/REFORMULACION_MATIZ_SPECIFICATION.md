# LA REFORMULACIÓN RECONOCE UNA PREGUNTA DEL CATÁLOGO CON UN MATIZ

Pre-registro escrito el **8 de octubre de 2026**, antes de hacer ninguna llamada. Lo pidió Daniel.
**Gasto: ~USD 0,05, con tope de USD 0,15.**

## 1. Qué cambia

**El defecto.** La versión 3 (`SISTEMA_V3`, en la página) mandó a «nueva» «¿La gente se siente segura caminando por su
barrio?», que el catálogo mide como `VS8` («¿Qué tan seguro se siente usted en su barrio?»)
(`REFORMULACION_VOTO_RESULTS.md` §4). Su razón: el catálogo «no pregunta específicamente al caminar». Las versiones 1 y 2
sí la acertaban. Así, la página estima con preguntas parecidas lo que la encuesta ya midió, y no muestra el dato real con
su mapa.

**La versión 4 (`SISTEMA_V4`)** es la 3 más una frase en el alcance «catalogo»:

> También es "catalogo" si solo agrega un matiz que no cambia lo que se mide, como un momento o una actividad cotidiana
> dentro del mismo tema (por ejemplo, «el agua que le llega a la casa» es la satisfacción con el servicio de agua). Si
> cambia el tema, el lugar o lo que se evalúa, es "nueva".

- **El ejemplo es a propósito uno que no está en la prueba.**
- **El riesgo va en el otro sentido:** que mande al catálogo una pregunta distinta. Entonces la página mostraría como medido
  el dato de otra pregunta, con más seguridad de la que tiene. Por eso la prueba mide los dos sentidos.

**El modelo** es `openai/gpt-6-luna` (DI-CO26), a temperatura 0.

## 2. La prueba

**54 preguntas,** escritas antes de llamar:
- **las 40 de la validación de la versión 3** (`PRUEBA_VOTO_V3`), para ver que nada se rompa. Entre ellas está la del
  barrio;
- **14 nuevas** (`PRUEBA_MATIZ`), que no repiten ninguna.

**8 con un matiz que no cambia lo medido.** Deben ir al catálogo con este código:

| Pregunta | Código |
|---|---|
| ¿Qué tan seguros se sienten los bogotanos cuando andan por las calles de la ciudad? | `VS10` |
| ¿La gente está contenta con la casa o el apartamento donde vive? | `VS7` |
| ¿Qué tan satisfechos están con el servicio de luz en las noches? | `SP3` |
| ¿Les funciona bien el internet que tienen en la casa? | `SP6` |
| ¿Qué opinan del ruido que se oye en Bogotá durante el día? | `MA3_3` |
| ¿Los bogotanos se consideran pobres hoy en día? | `CO4` |
| ¿Qué tan probable creen que es que castiguen a alguien por no pagar sus impuestos? | `RC5_6` |
| ¿Cómo ven la economía de Bogotá para los próximos años? | `CO1_2` |

**6 cercanas pero distintas.** Deben ser «nuevas»:
- ¿Qué tan seguros se sienten dentro de TransMilenio?
- ¿Están satisfechos con lo que pagan en la factura del agua?
- ¿Cómo califican el trabajo de la policía en su barrio?
- ¿Les gusta el alumbrado navideño de la ciudad?
- ¿Qué tan satisfechos están con la seguridad en los colegios?
- ¿Qué tan satisfechos están con los parques para perros?

## 3. Regla

**La versión 4 entra a la página si se cumplen las nueve condiciones:**
- **R1 a R6,** iguales a las de `REFORMULACION_VOTO_SPECIFICATION.md` §3, sobre las 40;
- **R7:** de las 8 con matiz, catálogo con su código en ≥ 7;
- **R8:** ninguna de las 6 cercanas como catálogo, y «nueva» en ≥ 5. Que una pregunta distinta vaya al catálogo es el error
  que más engaña;
- **R9:** «¿La gente se siente segura caminando por su barrio?» va a `VS8`.

**Si no se cumplen,** la página sigue con la versión 3. El defecto queda anotado como límite conocido.

## 4. Predicciones

- **PRM1.** La versión 4 cumple la regla.
- **PRM2.** R9: la del barrio va a `VS8`.
- **PRM3.** Ninguna de las 6 cercanas va al catálogo.

## 5. Lo que ya se vio, y se declara

- **La respuesta de la versión 3** a la pregunta del barrio y su razón (§1), y las versiones 1 y 2, que la acertaban.
- **Los resultados de la versión 3** en las otras 39 de las 40.

## 6. Gasto y código

- **Gasto:** 54 llamadas a ~USD 0,0009, unos USD 0,05, con tope de USD 0,15.
- **Código:** `src/consulta/reformular.py` (`SISTEMA_V4`, `PRUEBA_MATIZ`, `evaluar_matiz`, `validar_voto(4)`).
- **Pruebas:** `tests/test_reformular.py`.
- **Resultados:** `REFORMULACION_MATIZ_RESULTS.md`.
