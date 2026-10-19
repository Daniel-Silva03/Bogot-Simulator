# REFORMULACIÓN, VERSIÓN 6: ¿RECONOCE CUÁNDO UNA PREGUNTA ES POLÍTICA O INSTITUCIONAL?

Pre-registro escrito el **19 de octubre de 2026**, antes de llamar al modelo. Es la **primera validación de la condición 1 de
D22**: antes de abrir los agentes en la página, la reformulación tiene que reconocer cuándo una pregunta es política o
institucional. Mejora 3 del daily. Gasto: **unos USD 0,08, con tope de USD 0,50.**

## 1. Pregunta

Hoy la reformulación (versión 5) clasifica la pregunta en cuatro alcances (catálogo, nueva, voto, fuera), pero no dice de qué
tema es. D22 manda a los agentes solo las nuevas de tema político o institucional, y D23 trata como nuevas también las de
percepción política que el catálogo ya midió. **¿Puede la reformulación marcar el tema sin dañar lo que ya hace bien?**

## 2. El cambio: la versión 6

Se agrega a la instrucción de la versión 5 un campo `tema`, obligatorio cuando el alcance es «catalogo» o «nueva»:

> Si el alcance es "catalogo" o "nueva", di también su "tema":
> - "politica": evalúa a gobernantes o gobiernos (el alcalde, el presidente, el Concejo, los ediles), a instituciones públicas
>   (la Policía, la justicia, la Registraduría, la Personería), a partidos, la democracia, la corrupción, el rumbo de la ciudad
>   o del país, la participación ciudadana, o si la próxima administración debería continuar o cambiar.
> - "ciudad": servicios, vida cotidiana, economía del hogar, seguridad que la persona vive, ambiente, cultura, y la aprobación
>   de una obra o una medida concreta en Bogotá, aunque la haya decidido un gobierno.
>
> Si el alcance es "voto" o "fuera", "tema" es null.

Y el JSON pide `"tema": "politica|ciudad o null"`. Lo demás de la versión 5 no cambia. La lectura es estricta: un «catalogo» o
una «nueva» sin un tema válido es una respuesta inválida.

## 3. La prueba

**A. Las 63 de la validación anterior** (`REFORMULACION_2025`), con sus mismos criterios R1 a R12. Comprueba que la versión 6 no
daña nada.

**B. 30 preguntas nuevas para el tema**, ninguna usada antes:

| # | Pregunta | Tema esperado |
|---|---|---|
| T1 | ¿Cómo califica la gente la gestión del alcalde Galán? | politica |
| T2 | ¿Las cosas en Bogotá van por buen camino? | politica |
| T3 | ¿Qué imagen tiene la gente del Concejo de Bogotá? | politica |
| T4 | ¿Qué tanto confía la gente en la Policía? | politica |
| T5 | ¿Cree la gente que hay mucha corrupción en la Alcaldía? | politica |
| T6 | ¿Aprueban los bogotanos la gestión del presidente de la República? | politica |
| T7 | ¿Cómo califican la gestión de Galán en movilidad? | politica |
| T8 | ¿La gente cree que la Alcaldía escucha a los ciudadanos? | politica |
| T9 | ¿Qué tan satisfechos están con la democracia en Colombia? | politica |
| T10 | ¿Confían los bogotanos en la Registraduría? | politica |
| T11 | Pensando en las próximas elecciones, ¿preferiría que el próximo alcalde continúe con las prioridades de la actual administración o que haga cambios en la gestión? | politica |
| T12 | ¿Qué imagen tiene la gente de Claudia López? | politica |
| T13 | ¿Confían los bogotanos en los partidos políticos? | politica |
| T14 | ¿Creen que la Personería defiende bien los derechos de los ciudadanos? | politica |
| T15 | ¿Cómo califican el trabajo de los ediles de su localidad? | politica |
| T16 | ¿Qué tan bien creen que funciona la justicia en Colombia? | politica |
| T17 | ¿Qué tan satisfechos están con el servicio de agua? | ciudad |
| T18 | ¿Se siente segura la gente caminando por su barrio? | ciudad |
| T19 | ¿Les gustan los parques de la ciudad? | ciudad |
| T20 | ¿Apoyarían cobrar por entrar en carro al centro? | ciudad |
| T21 | ¿Están de acuerdo con construir la segunda línea del metro? | ciudad |
| T22 | ¿Qué tan satisfechos están con TransMilenio? | ciudad |
| T23 | ¿Cómo creen que va a estar la economía de su hogar el próximo año? | ciudad |
| T24 | ¿Apoyarían prohibir la venta de pólvora en diciembre? | ciudad |
| T25 | ¿Qué tan contaminado creen que está el aire de Bogotá? | ciudad |
| T26 | ¿Les gustaría que hubiera más ciclorrutas? | ciudad |
| T27 | ¿Qué tan satisfechos están con los colegios públicos? | ciudad |
| T28 | ¿Les preocupa perder el empleo este año? | ciudad |
| T29 | ¿Estarían de acuerdo con ampliar el pico y placa a todo el día? | ciudad |
| T30 | ¿Qué opinan del alumbrado navideño? | ciudad |

**Lo que se declara:**
- **El alcance de las 30 no se juzga:** pueden ir al catálogo o ser nuevas. Solo se juzga el tema.
- **T11 es la pregunta del jefe de Daniel**, que ya se corrió con los agentes.
- **T20, T21, T24 y T29** son aprobaciones de una medida en Bogotá: la regla de §2 las pone en «ciudad». En D22, los agentes
  perdieron en las del metro.
- **Una política que el modelo mande a «fuera» o a «voto»** cuenta como error del tema.

## 4. Reglas (escritas antes de llamar al modelo)

**La versión 6 pasa si se cumplen las cuatro:**
- **RP1:** «politica» en **al menos 14 de las 16** políticas (T1-T16).
- **RP2:** «ciudad» en **al menos 12 de las 14** de ciudad (T17-T30).
- **RP3:** respuesta válida en **al menos 28 de las 30**.
- **RP4:** en las 63 de A, **se cumplen R1 a R12**, como con la versión 5.

## 5. Predicciones

- **PP1.** La versión 6 pasa.
- **PP2.** Los errores de RP2, si los hay, caen en las aprobaciones de una medida (T20, T21, T24, T29), marcadas «politica».
- **PP3.** T11, la pregunta del jefe, sale «politica».

## 6. Qué pasa después

- **Si pasa:** la página pasa a la versión 6, y el motor manda a los agentes las nuevas de tema político. Hoy los agentes siguen
  apagados con el modelo real (`AGENTES_CON_MODELO_REAL = False`), hasta la segunda validación de D22. Ese cambio va con su
  propio DI-CO y se le muestra a Daniel antes.
- **Si no pasa:** la página se queda en la versión 5, y se anota qué falló.

## 7. Gasto y código

- **Gasto:** 93 llamadas a `openai/gpt-6-luna` (63 de A y 30 de B), unos USD 0,08 (la validación anterior costó USD 0,053 por
  63), con tope de USD 0,50.
- **Al modelo** va lo de siempre: la pregunta y el catálogo de la población 2022-2025, sin datos de personas.
- **Código:** `SISTEMA_V6`, `parsear_v3`, `PRUEBA_TEMA` y `validar_tema` en `src/consulta/reformular.py`, con
  `python src/consulta/reformular.py --validar-tema`. Prueba en `tests/test_reformular_tema.py`. Resultados en
  `REFORMULACION_TEMA_RESULTS.md`.
