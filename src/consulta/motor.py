"""
src/consulta/motor.py

La consulta de punta a punta (D17): de la pregunta que alguien escribe a la
respuesta que ve en la página. Une las tres piezas validadas:

    reformulación (`reformular.py`, 24 de 24)
        ├─ catálogo → el dato medido: población EPC 2022-2024, por ciudad, grupo y localidad
        ├─ nueva    → (D18) el tono general por grupo, rotulado como tal, y las
        │             preguntas medidas que el puente relaciona, con su dato real;
        │             SIN nivel y SIN mapa por localidad
        └─ fuera    → por qué no, y una alternativa que vuelve a pasar por aquí

Todo lo que devuelve lleva `suposicion: True` y el texto que la página muestra.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-CO1. **Una pregunta del catálogo se responde con los agentes, y su margen sale de
    los encuestados.** La media de una localidad es la de sus 1.000 agentes (que
    pesan a los encuestados según la composición del receptor); el margen del 95 %
    se obtiene remuestreando manzanas de la EPC dentro de la localidad (DI-PE5) y
    recalculando esa misma media de agentes. Así el margen es el de la encuesta, no
    el de los 20.000 agentes, que son copias.

DI-CO2. **Una pregunta nueva no tiene mapa** (`PUENTE_RESULTS.md`, lectura B: el
    puente ordena personas, no localidades). Se devuelven diferencias entre grupos
    en desviaciones estándar del puntaje del puente («más / menos de acuerdo que el
    promedio»), no porcentajes: el puente ordena, no fija cuántos están de acuerdo.
    El nivel de la ciudad es el que propone el modelo, y la página lo deja editar.
    *Cambio (2/10, D18): los grupos ya no salen del puente (DI-CO14) y no hay nivel
    (DI-CO16). Sigue sin mapa.*

DI-CO3. **En la página el puente usa el catálogo completo (102 preguntas)**, no el de
    la validación (91): ya no hay preguntas escondidas. Se valida y se puntúa igual.

DI-CO4. **Una alternativa sugerida para una pregunta fuera de alcance no se responde
    directamente** (`REFORMULACION_RESULTS.md` §3): la página la manda otra vez a
    `reformular`, como pregunta nueva.

DI-CO5. **Grupos:** estrato en tres niveles (1-2, 3-4, 5-6; el 0 va con 1-2), los
    cinco tramos de edad, sexo y los cuatro niveles de educación de DI-PE1.
    *Cambio (30/09, población 2022-2024): sin educación.* Esa población no empareja
    por educación (2024 no la pregunta), así que la educación del agente no dice
    nada de su donante: un grupo por educación solo repetiría estrato y edad.

DI-CO6. **La página usa la población 2022-2024** (`poblacion_epc_olas.py`, lectura B
    mantenida por Daniel el 30/09). Una pregunta del catálogo la responden los
    agentes cuyo donante es de un año que se puede juntar para esa pregunta (DI-PO2);
    los demás no cuentan, ni como «no sabe». La respuesta dice de qué años sale y
    cuántos encuestados hay por localidad. El margen remuestrea los conglomerados de
    DI-PO3.

DI-CO7. **En una pregunta nueva, cada pregunta del puente se estandariza dentro de su
    año** (como `puente_localidades.py`, DI-PL3), con los pesos de los donantes; si
    no existe ese año, vale 0. Así un cambio de nivel entre años no se vuelve una
    diferencia entre grupos.

DI-CO8. **El prompt de la reformulación no cambia** (sigue diciendo «EPC 2023»): es el
    que se validó 24 de 24, y el catálogo que ve el modelo es el mismo (102 preguntas).

DI-CO9. **La respuesta dice a cuántas personas sintéticas consultó**: las que tienen
    donante (Sumapaz no) y, en una pregunta del catálogo, cuyo donante es de un año de
    esa pregunta. Hecho, en la prueba con el modelo real (30/09): la página decía
    siempre «20.000», también en una pregunta solo de 2023, donde responden 6.492.

DI-CO10. **Las etiquetas se muestran sin el número del código** («4. Alta» → «Alta»).
    Algunas etiquetas de la EPC lo traen; en la página se leía «4. alta o 5. muy
    alta». Solo cambia lo que se muestra: el catálogo y lo que ve el modelo no cambian.

DI-CO11. **Si el puente usa preguntas que no se hicieron todos los años, la respuesta lo
    dice** (Daniel, 30/09: «déjalo así y dilo en la respuesta»). Hecho: en la prueba
    con el modelo real, el puente del metro usó dos preguntas que solo existen en
    2023; para los encuestados de 2022 y 2024 valen 0 (DI-CO7). No se restringe al
    modelo (eso cambiaría su prompt y habría que validarlo otra vez). Cada pregunta
    del puente lleva sus años, y la respuesta trae qué fracción del peso del puente
    queda en cada año y un texto que lo explica.
    *Cambio (2/10, D18): el texto sobre el peso por año se quita, porque hablaba de
    las diferencias entre grupos del puente, que ya no se muestran. Cada pregunta
    relacionada sigue diciendo sus años, junto a su dato real (DI-CO15).*

DI-CO12. **El puente de la página usa el prompt v2 y muestra su fuerza**
    (`PUENTE_SIN_BASE_RESULTS.md`: P3 se cumple; P1 no, así que no se usa «sin base»).
    Si el v2 responde «sin base» o una respuesta rota, se pide el puente otra vez con el
    prompt de siempre (`puente.SISTEMA`) y se muestra como **base débil** (opción 1 que
    eligió Daniel el 1/10; no contradice la regla escrita). Es una llamada más, solo en
    esos casos. Si tampoco hay puente con el prompt de siempre, la pregunta no se responde,
    como antes.
    *Cambio (2/10, D18): el reintento se conserva, pero la fuerza ya no se muestra.
    Decía qué tan bien sostenía el puente sus barras por grupo, y esas barras se
    quitan (DI-CO14).*

DI-CO13. **Las diferencias por grupo de una pregunta nueva no se muestran de entrada**
    (`PREGUNTAS_REALES_NUEVAS_RESULTS.md`, regla de §7: P1 falló, 8 de 24, y en el Corredor
    Verde el orden salió al revés). La respuesta las sigue trayendo, con `aviso_grupos`; la
    página las esconde tras «Ver de todos modos». El texto de la fuerza deja claro que
    mide qué tan cerca está el tema, no si la suposición acierta (las dos preguntas
    reales salieron «media» y fallaron).
    *Reemplazada el 2/10 por DI-CO14 (D18).*

DI-CO14. **Los grupos de una pregunta nueva muestran el tono general, a la vista**
    (D18; `BANCO_PREGUNTAS_NUEVAS.md` §10.3: el puente ordenó bien el 60-63 % de las
    diferencias entre grupos de la práctica, y el tono general, sin API, el 62 %; la
    regla escrita, 67 %, dijo parar). Hecho: el tono es el de DI-PP4, por agente el
    promedio de sus respuestas estandarizadas por año (DI-CO7) en las preguntas del
    catálogo con dirección conocida, orientadas para que arriba sea lo favorable; el
    índice de un grupo es su media en desviaciones estándar. Supuesto: los grupos que
    suelen responder de forma favorable también lo harán en la pregunta nueva.
    Decisión: se calcula una vez al cargar, **es el mismo para toda pregunta nueva**, y
    la página lo rotula «Así suelen responder estos grupos en la encuesta», no como una
    medida de la pregunta. Los cortes de la página (estrato 1-2, 3-4, 5-6) no son los de
    la práctica (1, 2, 3, 4, 5-6): el 62 % es de aquellos.
    *Corrección (5/10, DI-CO21): el 62 % no se generalizó; en el banco ampliado el tono acierta 0,466
    (`TECHO_GRUPOS_LOTES_RESULTS.md`). La página ya no lo cita ni lo presenta como predicción.*

DI-CO15. **Las preguntas en que se apoya el puente traen lo que la gente respondió de
    verdad** (D18): la distribución de la ciudad y el porcentaje en la parte alta de su
    escala, con los años de cada una (el mismo cálculo de ciudad que `responder_catalogo`,
    sin localidades ni bootstrap). La página enlaza a cada una completa, con su mapa.
    El puente sigue pidiéndose al modelo solo para elegirlas.

DI-CO16. **Sin nivel propuesto** (D18): en la prueba con dos preguntas reales
    (`PREGUNTAS_REALES_NUEVAS_RESULTS.md`) el modelo dio 3,7 a las dos y no distinguió
    cuál tenía más apoyo. El nivel que devuelve el modelo se descarta.
    *Añadido (2/10, prueba con el modelo real): la justificación del modelo tampoco se
    muestra.* Hecho: en las tres preguntas de la prueba, el texto citaba el nivel o la
    fuerza («se espera un apoyo mayoritario (media ≈ 3.8)», «la media esperada…»). El
    prompt validado los pide, así que no se cambia; se descarta el texto.

DI-CO17. **Escalas numéricas: se muestran como números con los extremos rotulados**
    (2/10, a pedido de Daniel). Hecho: 47 de las 102 preguntas usan escalas de 1 a 5 en
    que la EPC solo nombró los extremos («Muy insatisfecho», 2, 3, 4, «Muy satisfecho»);
    la página decía «4 o muy satisfecho». Decisión: no se inventan nombres para 2, 3 y 4;
    se muestran «1 · Muy insatisfecho», 2, 3, 4, «5 · Muy satisfecho», y la parte alta
    como «4 o 5 (muy satisfecho)». También «NADA» → «Nada», y «5 Muy satisfecho» (SP1)
    pierde el número cuando es el código de la respuesta. Como DI-CO10, solo cambia lo que
    se muestra: el catálogo y lo que ve el modelo no cambian.

DI-CO18. **El «% que respondería…» cuenta el lado favorable cuando se sabe cuál es**
    (2/10, a pedido de Daniel). Hecho: se contaba siempre la mitad alta de los códigos, y
    en `AG1` eso era «mal camino» y en `CC2` «no tiene opinión o no lo conoce». Decisión:
    (1) las categorías que no son una opinión («No tiene opinión», «No lo conoce»; en el
    catálogo solo `CC2`) no cuentan para elegir el lado; (2) si `puente.direccion` (DI-PU4)
    dice que lo favorable está abajo, se cuenta la mitad baja (`AG1` → «Buen camino»,
    `CC2` → «Favorable»); (3) si no se sabe (23 preguntas: probabilidad de sanción,
    corrupción, si vota…), sigue la mitad alta, que es cierta y no juzga. Aplica a la
    ciudad, los grupos, la ficha de cada localidad y las preguntas relacionadas. Los campos
    se siguen llamando `alto` y `etiqueta_alto`.

DI-CO19. **Las categorías que no son una opinión cuentan como «no sabe»** (2/10, a pedido de
    Daniel). Hecho: `CC2` (imagen del Concejo) traía en su escala «No tiene opinión» (3) y «No
    lo conoce» (4), y el mapa se coloreaba con la media de 1 a 4 (2,27), que no mide nada.
    Decisión: en lo que se muestra (media, margen, mapa, distribución, porcentaje), esas
    categorías salen, como el «no sabe»; la escala de `CC2` queda «Favorable», «Desfavorable».
    Para no esconder cuánta gente queda fuera, la página dice el porcentaje que no cuenta
    cuando pasa del 5 % (`respondieron`), en toda pregunta. Solo cambia lo que se muestra: el
    catálogo, lo que ve el modelo y el puente (que estandariza `CC2` con sus cuatro códigos,
    como se validó) no cambian.

DI-CO20. **Una pregunta nueva empieza diciendo que no se puede responder** (2/10, Daniel, al
    verla en la página: «no es claro si la población está o no de acuerdo»). Hecho: con D18 la
    respuesta no trae ninguna cifra propia, pero tampoco lo decía; se leía una lista de otras
    preguntas y unas barras sin saber qué contestaban. Decisión: arriba va `RESPUESTA_NUEVA`
    («No podemos decir si Bogotá estaría de acuerdo» y por qué), y debajo, rotulado como
    contexto, lo que ya había (preguntas parecidas con su dato real y el tono por grupo).

DI-CO21. **El tono por grupo queda como contexto descriptivo, sin cifra de acierto** (5/10, D18
    actualizada, opción 3 de Daniel). Hecho: en los lotes 2 y 3 del banco el tono acertó 0,466 de las
    diferencias claras, peor que el azar (`TECHO_GRUPOS_LOTES_RESULTS.md`); el 62 % del lote 1 no se
    generaliza. Decisión: se sigue mostrando, con el título «Así responden estos grupos en general» y un
    texto que dice que es contexto y que no sirvió para anticipar respuestas. Se descartaron quitarlo
    (opción 2, la que recomendó Claude) y mostrar las dos cifras de acierto (opción 1).

DI-CO22. **Una pregunta nueva trae una estimación de si Bogotá estaría de acuerdo** (5/10, D19). Hecho:
    Claude Sonnet eligiendo preguntas parecidas entre las 92 de práctica de acuerdo o sí/no del banco pasó
    la regla en la práctica y en el guardado (`NIVEL_ACUERDO_VALIDACION_RESULTS.md`: error 12,5, lado de
    la mayoría 77 %, 28 de 28 al decidir). Decisión, la configuración validada sin cambios:
    - mismo modelo (`anthropic/claude-sonnet-5.5`), instrucciones (`nivel_parecidas_b.SISTEMA`) y
      candidatas (`nivel_acuerdo.tabla()`, que se arma con archivos del repo, sin datos crudos);
    - la pregunta nueva va con su escala de cinco puntos y «de acuerdo» y «muy de acuerdo» marcados como
      favorables;
    - porcentaje = media real de las elegidas; rango = ± 21,9 (`nivel_acuerdo_validacion.H`), recortado
      a 0-100; «probablemente sí/no» solo si el rango no cruza el 50 %; si no, «dividida».

    La reformulación y el puente siguen con el modelo de siempre. Si la estimación falla, la respuesta
    trae `estimacion: None` y la página muestra el texto de DI-CO20.

DI-CO23. **Las candidatas de la estimación pasan a ser 109** (5/10, D19 actualizada): las 92 validadas más las
    17 preguntas de práctica del lote 5 (Encuesta Distrital de Percepción 2025, mismo formato que la página).
    Hecho: en 95 preguntas guardadas, con 109 candidatas el error baja de 12,8 a 11,9 y, al decir
    «probablemente», acierta 17 de 17 contra 12 de 12 (`NIVEL_ACUERDO_LOTE5_RESULTS.md`); la regla
    pre-registrada dice que reemplace a la de 92. El rango sigue en ±21,9. El texto de la página cita las
    cifras de esa prueba. Cuesta ~USD 0,024 por pregunta nueva, contra ~0,019.

DI-CO24. **Un error del servicio del modelo ya no se confunde con «no se pudo estimar»** (5/10, pedido por
    Daniel). Hecho: el 5/10 la cuenta de OpenRouter quedó sin saldo (HTTP 402) y `estimar`, que atrapaba
    toda excepción, devolvía None: la página decía «No podemos decir si Bogotá estaría de acuerdo»
    (DI-CO20) como si fuera un límite del método, y la parte A de `NIVEL_ACUERDO_REDACCION` siguió sin
    estimar 37 preguntas sin avisar. Decisión: los errores de red y de HTTP (`OSError`, que incluye
    `urllib.error.URLError` y los tiempos de espera, y `http.client.HTTPException`) se convierten en
    `ServicioNoDisponible`, una `ConsultaError`: el servidor responde con el mensaje y la página muestra su
    estado de error con «Intentar de nuevo». Cualquier otro error se escribe en la terminal y cae a
    DI-CO20, como antes. Una respuesta del modelo que no sirve (sin ids válidos) sigue siendo DI-CO20.

DI-CO25. **La estimación usa GPT-6 Luna** (6/10, D20). Hecho: en su prueba pre-registrada, Luna cumplió las tres
    condiciones de la regla de Sonnet, pero no la de no perder más de 1,5 puntos de error frente a él en el
    guardado (14,3 contra 11,9). Decisión de Daniel: cambiar por costo, unas 20 veces menos por pregunta nueva.
    Cambian el modelo (`MODELO_ESTIMACION`), el rango (`H_ESTIMACION` = 23,4, el h de Luna; antes,
    `nivel_acuerdo_validacion.H` = 21,9) y las cifras del texto (69 % del lado de la mayoría; 10 de 11 al
    decir «probablemente»; corregidas después por DI-CO27). El método y las 109 candidatas no cambian.

DI-CO26. **La reformulación y el puente también usan GPT-6 Luna** (6/10, pedido por Daniel con prueba). Hecho
    (`LUNA_PAGINA_RESULTS.md`): con Luna, la reformulación saca 24 de 24 en su validación, como mimo, y no
    empeora la estimación de las 95 guardadas (EAM 16,5 contra 16,2; lado 64 % y 64 %). El puente cumple
    R1, R2 y P2 de `PUENTE_SIN_BASE` (0 de 12, 12 de 12 y 0 de 10, como mimo). Las dos pasan su regla
    pre-registrada. Cuestan ~USD 0,0009 por llamada contra ~0,004. Una pregunta nueva pasa de ~USD 0,009 a
    ~0,003. Las instrucciones (`reformular.SISTEMA`, `puente_sin_base.SISTEMA_V2`) no cambian.

DI-CO27. **El texto cita lo medido con la página tal como funciona** (6/10, pedido por Daniel). Hecho: las cifras de
    DI-CO23 y DI-CO25 (72 % y 17 de 17 con Sonnet; 69 % y 10 de 11 con Luna) se midieron dándole al modelo el
    texto original de cada encuesta, pero la página primero reformula. Medido con la reformulación
    (`NIVEL_ACUERDO_REDACCION_RESULTS.md` parte A; `LUNA_PAGINA_RESULTS.md` parte 2): con Luna reformulando y
    estimando, en las 90 de las 95 guardadas que quedan como pregunta nueva, acierta el lado el 63 % y, al
    decir «probablemente», 3 de 4. La franja de la página pasa de «7 de cada 10» a «6 de cada 10».
"""

from __future__ import annotations

import http.client
import json
import re
import sys
import urllib.error
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.consulta import reformular as rf                  # noqa: E402
from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import puente as pu                  # noqa: E402

POBLACION = RAIZ / "data" / "processed" / "poblacion_epc2022_2024"
MARGINAL = RAIZ / "data" / "external" / "marginal_localidad_18mas.csv"
CACHE = RAIZ / "data" / "processed" / "consulta" / "cache.json"
N_BOOT = 200
SEMILLA = 20260930
SUMAPAZ = 20

GRUPOS = {
    "estrato": {"titulo": "Estrato", "orden": ["1 y 2", "3 y 4", "5 y 6"]},
    "edad": {"titulo": "Edad", "orden": ["18 a 25", "26 a 35", "36 a 45", "46 a 55", "56 o más"]},
    "sexo": {"titulo": "Sexo", "orden": ["Mujeres", "Hombres"]},
}
AVISO = ("Esto es una suposición, no una medición: muestra cómo respondería una población sintética "
         "construida con la Encuesta de Percepción Ciudadana 2022, 2023 y 2024 de Bogotá Cómo Vamos.")


#: DI-CO20: lo primero que dice una pregunta nueva es que no se puede responder.
RESPUESTA_NUEVA = {
    "titulo": "No podemos decir si Bogotá estaría de acuerdo.",
    "texto": ("La encuesta no hizo esta pregunta, y cuando probamos a suponerlo con preguntas reales que sí "
              "conocíamos, el simulador no acertó cuántos estarían de acuerdo ni qué grupos o localidades lo "
              "estarían más. Lo que sí hay es contexto medido: lo que la gente respondió a preguntas parecidas "
              "y cómo responde cada grupo en general."),
}
#: DI-CO22: la estimación de una pregunta nueva.
#: DI-CO26: la reformulación y el puente; antes, `reformular.MODELO` (xiaomi/mimo-v2.6-pro).
MODELO_PAGINA = "openai/gpt-6-luna"
MODELO_ESTIMACION = "openai/gpt-6-luna"                    # DI-CO25 (D20); antes, anthropic/claude-sonnet-5.5
#: DI-CO25: el rango de Luna, cuantil 80 % de su error en las 92 de práctica (NIVEL_ACUERDO_LUNA_RESULTS.md).
H_ESTIMACION = 23.4
LLAMADA_TITULO = {"sí": "Probablemente sí", "no": "Probablemente no", "dividida": "Dividida"}
ESTIMACION_TEXTO = ("Es una estimación, no una medición: sale de lo que la gente respondió de verdad a {n} preguntas "
                    "parecidas que sí se midieron, que eligió un modelo de lenguaje (aparecen debajo, con su resultado). "
                    "En una prueba con 90 preguntas reales que no se habían usado para armarla, pasadas por esta misma "
                    "página (reformuladas y estimadas), acertó si la mayoría estaba de acuerdo en el 63 % de los casos, "
                    "y de las 4 veces que dijo «probablemente» acertó 3.")   # DI-CO27
ESTIMACION_DIVIDIDA = (" El rango cruza el 50 %: con lo que hay medido no se puede decir de qué lado queda la "
                       "mayoría.")
#: DI-CO14: el rótulo y la explicación del tono general por grupo.
TONO_TITULO = "Así responden estos grupos en general"                       # DI-CO21
TONO_TEXTO = ("Es contexto, no una respuesta a esta pregunta: es igual para toda pregunta nueva. Resume cómo "
              "responde cada grupo, en promedio, las {n} preguntas de la encuesta con un lado favorable claro. En "
              "las pruebas con preguntas reales que la encuesta no hizo, no sirvió para anticipar qué grupos "
              "estarían más de acuerdo.")


class ConsultaError(RuntimeError):
    """La consulta no se puede responder como está especificada."""


class ServicioNoDisponible(ConsultaError):
    """DI-CO24: el servicio del modelo de lenguaje no respondió (sin saldo, red, tiempo de espera)."""


def _servicio(e: Exception) -> ServicioNoDisponible:
    if isinstance(e, urllib.error.HTTPError) and e.code == 402:
        motivo = "la cuenta del servicio no tiene saldo (error 402)"
    elif isinstance(e, urllib.error.HTTPError):
        motivo = f"error {e.code} del servicio"
    else:
        motivo = "no hubo conexión o tardó demasiado"
    return ServicioNoDisponible(f"El modelo de lenguaje no respondió: {motivo}. Inténtalo más tarde; "
                                "las preguntas que la encuesta ya hizo siguen funcionando.")


def _wmean(x, w):
    s = np.sum(w)
    return float(np.sum(x * w) / s) if s > 0 else float("nan")


def _grupos(ag: pd.DataFrame) -> dict[str, pd.Series]:
    """DI-CO5: la etiqueta de grupo de cada agente."""
    est = ag.estrato.map(lambda e: "1 y 2" if e <= 2 else ("3 y 4" if e <= 4 else "5 y 6"))
    edad = ag.edad_tramo.map(dict(enumerate(GRUPOS["edad"]["orden"])))
    sexo = ag.sexo.map({"F": "Mujeres", "M": "Hombres"})
    return {"estrato": est, "edad": edad, "sexo": sexo}                          # DI-CO5


def _etq(texto: str) -> str:
    """DI-CO10."""
    return re.sub(r"^\s*\d+\s*[.)-]\s*", "", str(texto)).strip()


def _texto(t: str) -> str:
    """DI-CO17: «NADA» → «Nada»; lo demás, igual."""
    return t.capitalize() if t.isupper() else t


def escala_visible(f: dict) -> list[str]:
    """DI-CO17: las etiquetas de una pregunta del catálogo como se muestran."""
    crudas = {k: str(f["etiquetas"][str(k)]) for k in f["escala"]}
    if not any(re.fullmatch(r"\s*\d+\s*", crudas[k]) for k in f["escala"][1:-1]):
        # «5 Muy satisfecho» (SP1): el número se quita solo si es el código de esa respuesta
        return [_texto(_etq(re.sub(rf"^\s*{k}\s+(?=\D)", "", crudas[k]))) for k in f["escala"]]
    out = []                                  # escala numérica: solo los extremos tienen nombre
    for k in f["escala"]:
        t = re.sub(r"^\s*\d+\s*[.)-]?\s*", "", crudas[k]).strip()
        out.append(f"{k} · {_texto(t)}" if t else str(k))
    return out


#: DI-CO18: categorías que no son una opinión dentro de la escala (en el catálogo, solo CC2).
NO_SUSTANTIVA = re.compile(r"no tiene opini|no lo conoce|no sabe|no responde", re.I)


def lado(f: dict) -> tuple[list, str]:
    """DI-CO18: (códigos, nombre) del lado de la escala que se cuenta en «% que respondería…».

    El favorable si se sabe (DI-PU4); si no, la mitad alta de los códigos. Las categorías
    que no son una opinión no cuentan para elegirlo.
    """
    vis = dict(zip(f["escala"], escala_visible(f)))
    sus = [c for c in f["escala"] if not NO_SUSTANTIVA.search(str(f["etiquetas"][str(c)]))]
    k = len(sus)
    bajo = pu.direccion({**f, "escala": sus}) == -1
    cods = [c for i, c in enumerate(sus) if (i < (k - 1) / 2 if bajo else i > (k - 1) / 2)]
    if len(cods) == 1:
        return cods, vis[cods[0]]
    ext, sig = (cods[0], cods[1]) if bajo else (cods[-1], cods[-2])   # el extremo y el que le sigue
    if " · " in vis[ext] and vis[sig] == str(sig):                    # escala numérica (DI-CO17)
        a, b = sorted((sig, ext))
        return cods, f"{a} o {b} ({vis[ext].split(' · ', 1)[1].lower()})"
    return cods, f"{vis[sig]} o {vis[ext].lower()}"


def vista(f: dict) -> dict:
    """DI-CO19: la pregunta como se muestra, sin las categorías que no son una opinión en su escala."""
    return {**f, "escala": [c for c in f["escala"] if not NO_SUSTANTIVA.search(str(f["etiquetas"][str(c)]))]}


def _candidatas_estimacion() -> Optional[pd.DataFrame]:
    """DI-CO23: las 109 candidatas (las 92 validadas más las 17 de práctica del lote 5), con su fuente legible;
    None si faltan los archivos del banco."""
    try:
        from src.experiments import nivel_acuerdo_lote5 as nl
        c = nl.candidatas()[1]
    except Exception:                                                           # noqa: BLE001
        return None
    s = pd.concat([pd.read_csv(f) for f in sorted((RAIZ / "data" / "processed" / "banco").glob("sorteo*.csv"))])
    nombres = {"ECP DANE": "Encuesta de Cultura Política, DANE", "EPC armonizada": "Encuesta de Percepción Ciudadana, Bogotá Cómo Vamos",
               "EPC coyuntura": "Encuesta de Percepción Ciudadana, Bogotá Cómo Vamos", "Biblioteca CNC": "Encuesta del CNC",
               "SCRD Cultura Ambiental": "Encuesta de Cultura Ambiental, Secretaría de Cultura",
               "SCRD Bienal de Culturas": "Encuesta Bienal de Culturas, Secretaría de Cultura",
               "SDP Percepción Distrital": "Encuesta Distrital de Percepción, Secretaría de Planeación"}
    fuente = dict(zip(s.id, s.fuente.map(lambda f: nombres.get(f, f)) + ", " + s.anio.astype(str)))
    return c.assign(fuente_txt=c.id.map(fuente))


def cargar_donantes() -> pd.DataFrame:
    return pd.read_parquet(POBLACION / "donantes.parquet")


def cargar_anios() -> dict[str, list[int]]:
    cat = json.loads((POBLACION / "catalogo.json").read_text(encoding="utf-8"))["dentro"]
    return {f["variable"]: f["anios"] for f in cat}


def _texto_anios(a: list[int]) -> str:
    a = sorted(a)
    return str(a[0]) if len(a) == 1 else ", ".join(map(str, a[:-1])) + f" y {a[-1]}"


class _PuenteOlas:
    """DI-CO7: la interfaz de `puente.Datos` con cada pregunta estandarizada por año."""

    def __init__(self, x: dict[str, np.ndarray], catalogo: dict, w: np.ndarray, anio: np.ndarray):
        self.w = w
        self.z = {}
        for v, f in catalogo.items():
            z = np.zeros(len(w))
            ok = np.isin(x[v], f["escala"])
            for a in np.unique(anio):
                m = ok & (anio == a)
                if m.any():
                    mu = _wmean(x[v][m], w[m])
                    sd = np.sqrt(_wmean((x[v][m] - mu) ** 2, w[m])) or 1.0
                    z[m] = (x[v][m] - mu) / sd
            self.z[v] = z

    def puntaje(self, puente: list[dict]) -> np.ndarray:
        return pu.Datos.puntaje(self, puente)


class Motor:
    """Carga una sola vez la población y el catálogo; cada consulta es independiente."""

    def __init__(self, llamar: rf.Llamar, modelo: str, donante: Optional[pd.DataFrame] = None,
                 agentes: Optional[pd.DataFrame] = None, catalogo: Optional[dict] = None,
                 cache: Optional[e9.Cache] = None, anios: Optional[dict] = None):
        self.llamar, self.modelo = llamar, modelo
        self.catalogo = catalogo if catalogo is not None else rf.cargar_catalogo()
        self._vista = {v: vista(f) for v, f in self.catalogo.items()}         # DI-CO19
        self._candidatas = _candidatas_estimacion()                              # DI-CO22
        self.donante = donante if donante is not None else cargar_donantes()
        self.anios = anios if anios is not None else cargar_anios()
        ag = agentes if agentes is not None else pd.read_parquet(POBLACION / "agentes.parquet")
        self.agentes = ag[ag.donante_id.notna()].reset_index(drop=True)
        self.idx = self.agentes.donante_id.astype(int).to_numpy()
        self.peso = self.agentes.peso.to_numpy(float)
        self.loc = self.agentes.cod_loc.to_numpy()
        self.grupos = _grupos(self.agentes)
        self.cache = cache if cache is not None else e9.Cache(CACHE)
        col = {c.upper(): c for c in self.donante.columns}
        self._x = {v: pd.to_numeric(self.donante[col[str(f["codigo"]).upper()]], errors="coerce").to_numpy(float)
                   for v, f in self.catalogo.items()}
        anio_d = (self.donante.anio.to_numpy() if "anio" in self.donante.columns
                  else np.full(len(self.donante), 2023))
        self.anio_agente = anio_d[self.idx]
        self.datos_puente = _PuenteOlas(self._x, self.catalogo, self.donante.peso.to_numpy(float), anio_d)   # DI-CO7
        self.tono, self.n_tono = self._tono_por_grupo()                         # DI-CO14
        self._conglo = {}
        loc_d = self.donante.cod_loc.to_numpy()
        for l in sorted(set(self.loc)):
            m = loc_d == l
            self._conglo[int(l)] = (np.flatnonzero(m), pd.factorize(self.donante.conglomerado.to_numpy()[m])[0])

    def _tono_por_grupo(self) -> tuple[dict, int]:
        """DI-CO14: (índice del tono general por grupo, cuántas preguntas lo forman)."""
        z = self.datos_puente.z
        cols = [d * z[v] for v, f in self.catalogo.items() for d in [pu.direccion(f)] if d is not None]
        t = np.mean(cols, axis=0)[self.idx]                    # el tono de DI-PP4, por agente
        m = _wmean(t, self.peso)
        t = (t - m) / (np.sqrt(_wmean((t - m) ** 2, self.peso)) or 1.0)
        grupos = {}
        for gname, etq in self.grupos.items():
            e = etq.to_numpy()
            grupos[gname] = [{"grupo": o, "indice": round(_wmean(t[e == o], self.peso[e == o]), 3)}
                             for o in GRUPOS[gname]["orden"] if (e == o).any()]
        return grupos, len(cols)

    def _ciudad(self, codigo: str) -> tuple[dict, np.ndarray, np.ndarray, np.ndarray]:
        """La respuesta de la ciudad a una pregunta del catálogo: (resumen, x, ok, cubre)."""
        f = self._vista[codigo]                                                  # DI-CO19
        esc = list(f["escala"])
        k = len(esc)
        x = self._x[codigo][self.idx]
        anios = sorted(self.anios.get(codigo, [2023]))
        cubre = np.isin(self.anio_agente, anios)                                  # DI-CO6
        ok = np.isin(x, esc) & cubre
        w = self.peso * ok
        dist = [_wmean((x == c).astype(float), w) for c in esc]
        alto, nombre = lado(f)                               # DI-CO18: el lado que se cuenta
        ciudad = {"media": round(_wmean(x[ok], self.peso[ok]), 3), "distribucion": [round(d, 4) for d in dist],
                  "alto": round(sum(d for c, d in zip(esc, dist) if c in alto), 4),
                  "etiqueta_alto": nombre,                                       # DI-CO17, DI-CO18
                  "respondieron": round(float(ok.sum() / cubre.sum()), 4)}
        return ciudad, x, ok, cubre

    # ---------------------------------------------------------------- paso 1
    def reformular(self, pregunta: str) -> dict:
        if not pregunta or not pregunta.strip():
            raise ConsultaError("La pregunta está vacía.")
        try:
            r, _ = rf.reformular(pregunta[:500], self.catalogo, self.llamar, self.cache, self.modelo)
        except (OSError, http.client.HTTPException) as e:                       # DI-CO24
            raise _servicio(e) from e
        if r is None:
            return {"alcance": "invalida", "mensaje": "No pude reformular esta pregunta. Prueba a escribirla de otra forma."}
        if r["alcance"] == "catalogo":
            f = self._vista[r["codigo"]]
            r["pregunta_catalogo"] = f["pregunta"].strip()
            r["escala"] = escala_visible(f)
        return r

    # ---------------------------------------------------------------- paso 2a
    def responder_catalogo(self, codigo: str) -> dict:
        if codigo not in self.catalogo:
            raise ConsultaError(f"{codigo} no está en el catálogo.")
        f = self._vista[codigo]                                                  # DI-CO19
        esc = list(f["escala"])
        k = len(esc)
        anios = sorted(self.anios.get(codigo, [2023]))
        ciudad, x, ok, cubre = self._ciudad(codigo)
        alto, _ = lado(f)                                    # DI-CO18
        rng = np.random.default_rng(SEMILLA)
        por_loc = {}
        xd = self._x[codigo]
        for l, (filas, g) in self._conglo.items():
            m = (self.loc == l) & ok
            if not m.any():
                continue
            # DI-CO1: cuántos agentes heredan a cada encuestado de la localidad
            cuenta = np.bincount(np.searchsorted(filas, self.idx[m]), minlength=len(filas)).astype(float)
            cuenta *= np.isin(xd[filas], esc)                   # «no sabe» no entra a la media (ni DI-CO19)
            vals = np.nan_to_num(xd[filas])
            media = float(np.sum(cuenta * vals) / cuenta.sum())
            nc = g.max() + 1
            boot = []
            for _ in range(N_BOOT):
                mult = np.bincount(rng.integers(0, nc, nc), minlength=nc)[g]
                c = cuenta * mult
                if c.sum() > 0:
                    boot.append(np.sum(c * vals) / c.sum())
            validos_d = np.isin(xd[filas], esc)
            por_loc[str(int(l))] = {
                "media": round(media, 3),
                "margen": [round(float(np.percentile(boot, 2.5)), 3), round(float(np.percentile(boot, 97.5)), 3)],
                "alto": round(_wmean(np.isin(x[m], alto).astype(float), self.peso[m]), 3),
                "encuestados": int(validos_d.sum())}
        n_loc = int(np.median([v["encuestados"] for v in por_loc.values()]))
        grupos = {}
        for gname, etq in self.grupos.items():
            e = etq.to_numpy()
            grupos[gname] = [{"grupo": o, "media": round(_wmean(x[(e == o) & ok], self.peso[(e == o) & ok]), 3),
                              "alto": round(_wmean(np.isin(x[(e == o) & ok], alto).astype(float), self.peso[(e == o) & ok]), 3)}
                             for o in GRUPOS[gname]["orden"] if ((e == o) & ok).any()]
        return {"tipo": "catalogo", "suposicion": True, "aviso": AVISO, "codigo": codigo,
                "pregunta": f["pregunta"].strip(), "escala": escala_visible(f),
                "consultados": int(cubre.sum()),                                    # DI-CO9
                "ciudad": ciudad,
                "localidades": por_loc, "grupos": grupos, "anios": anios,
                "encuestados_mediana_localidad": n_loc,
                "fuente": (f"Dato medido en la EPC {_texto_anios(anios)}, reponderado por la población sintética; "
                           f"unas {n_loc} personas encuestadas por localidad.")}

    # ---------------------------------------------------------------- paso 2b
    def estimar(self, pregunta: str, escala: list[str]) -> Optional[dict]:
        """DI-CO22: (porcentaje, rango, llamada y las preguntas medidas en que se apoya), o None."""
        from src.experiments import nivel_acuerdo as na
        from src.experiments import nivel_parecidas_b as nb
        c = self._candidatas
        if c is None or c.empty:
            return None
        nueva = pd.DataFrame([{"id": "NUEVA", "familia": "NUEVA", "pregunta_pagina": pregunta,
                               "categorias": "; ".join(f"{i + 1}={e}" for i, e in enumerate(escala)),
                               "codigos_favorables": "[4, 5]", "total": np.nan}])
        cols = ["id", "familia", "pregunta_pagina", "categorias", "codigos_favorables", "total"]
        t = pd.concat([nueva, c[cols]], ignore_index=True)
        try:
            ids, _ = nb.elegir(t, 0, self.llamar, self.cache, MODELO_ESTIMACION, float("inf"))
        except (OSError, http.client.HTTPException) as e:                       # DI-CO24
            raise _servicio(e) from e
        except Exception as e:                                                  # noqa: BLE001 — se cae al texto de DI-CO20
            print(f"[estimar] error inesperado, se muestra DI-CO20: {e!r}", file=sys.stderr, flush=True)
            return None
        if not ids:
            return None
        elegidas = c.set_index("id").loc[ids]
        pct = float(elegidas.total.mean())
        lo, hi = max(0.0, pct - H_ESTIMACION), min(100.0, pct + H_ESTIMACION)          # DI-CO25
        llam = str(na.llamada(np.array([pct]), np.array([H_ESTIMACION]))[0])
        return {"porcentaje": round(pct, 1), "rango": [round(lo, 1), round(hi, 1)], "llamada": llam,
                "titulo": LLAMADA_TITULO[llam],
                "texto": ESTIMACION_TEXTO.format(n=len(ids)) + (ESTIMACION_DIVIDIDA if llam == "dividida" else ""),
                "preguntas": [{"pregunta": r.pregunta_pagina, "fuente": r.fuente_txt, "porcentaje": round(float(r.total), 1)}
                              for r in elegidas.itertuples()]}

    def responder_nueva(self, pregunta: str, escala: list[str]) -> dict:
        if not pregunta or len(escala) != 5:
            raise ConsultaError("Una pregunta nueva necesita su texto y cinco etiquetas.")
        f_esc = {"variable": "NUEVA", "codigo": "NUEVA", "pregunta": pregunta.strip(), "escala": [1, 2, 3, 4, 5],
                 "etiquetas": {str(i + 1): e for i, e in enumerate(escala)}}
        from src.experiments import puente_sin_base as sb
        u = pu.prompt(f_esc, self.catalogo)
        try:
            texto, _ = e9.pedir(self.llamar, self.cache, self.modelo, pu.TEMPERATURA, sb.SISTEMA_V2, u, 0)
            r = sb.parsear_v2(texto, f_esc, self.catalogo)                      # DI-CO12
            reintento = r is None or r["sin_base"]
            if reintento:
                texto, _ = e9.pedir(self.llamar, self.cache, self.modelo, pu.TEMPERATURA, pu.SISTEMA, u, 0)
                r = pu.parsear(texto, f_esc, self.catalogo)                      # DI-CO3
                if r is not None:
                    r = {**r, "fuerza": "debil"}
        except (OSError, http.client.HTTPException) as e:                       # DI-CO24
            raise _servicio(e) from e
        if r is None:
            return {"tipo": "invalida", "mensaje": "No pude construir el puente para esta pregunta. Prueba a reformularla."}
        relacionadas = []                                                        # DI-CO15
        for p in r["preguntas"]:
            f = self._vista[p["codigo"]]
            ciudad, *_ = self._ciudad(p["codigo"])
            relacionadas.append({"codigo": p["codigo"], "sentido": p["sentido"], "pregunta": f["pregunta"].strip(),
                                 "escala": escala_visible(f),
                                 "anios": sorted(self.anios.get(p["codigo"], [2023])), "ciudad": ciudad})
        return {"tipo": "nueva", "suposicion": True, "aviso": AVISO, "pregunta": pregunta.strip(), "escala": escala,
                "consultados": len(self.agentes),                                   # DI-CO9
                "respuesta": RESPUESTA_NUEVA,                                        # DI-CO20
                "estimacion": self.estimar(pregunta.strip(), escala),               # DI-CO22
                "grupos": self.tono, "tono_titulo": TONO_TITULO,                     # DI-CO14
                "tono_texto": TONO_TEXTO.format(n=self.n_tono),
                "relacionadas": relacionadas,                                        # DI-CO16: sin justificación
                "reintento": reintento,                                              # DI-CO12
                "sin_mapa": ("Para preguntas nuevas el simulador no dibuja localidades: en las pruebas con preguntas "
                             "conocidas ordenó bien a las personas, pero no a las localidades "
                             "(PUENTE_RESULTS.md, PUENTE_LOCALIDADES_RESULTS.md)."),
                "fuente": ("Un modelo de lenguaje eligió qué preguntas medidas se relacionan con esta; lo que se "
                           "muestra de cada una es lo que la gente respondió de verdad. El modelo no fija ninguna "
                           "cifra.")}


# --------------------------------------------------------------------------
# Información general para el mapa (sin opinión)

def informacion_general(agentes: Optional[pd.DataFrame] = None, donante: Optional[pd.DataFrame] = None) -> dict:
    """Por localidad: nombre, adultos (proyección oficial), estrato medio de la población y
    cuántas personas de la EPC 2022-2024 viven ahí. Nada de opinión."""
    ag = agentes if agentes is not None else pd.read_parquet(POBLACION / "agentes.parquet")
    don = donante if donante is not None else cargar_donantes()
    m = pd.read_csv(MARGINAL).set_index("COD_LOC")
    enc = don.cod_loc.value_counts()
    out = {}
    for c, fila in m.iterrows():
        a = ag[ag.cod_loc == c]
        out[str(int(c))] = {"nombre": fila.localidad, "adultos": int(fila.poblacion),
                            "estrato_medio": round(float(a.estrato.mean()), 2) if len(a) else None,
                            "encuestados": int(enc.get(c, 0))}
    return out


def cliente(simulado: bool = False):
    """(llamar, modelo). El simulado contesta la reformulación y el puente sin gasto."""
    if not simulado:
        return e9.cliente_real(), MODELO_PAGINA                                  # DI-CO26
    cat = rf.cargar_catalogo()
    ref = rf.modelo_simulado(cat)
    cods = list(cat)

    def llamar(modelo, sistema, usuario, temp):
        if sistema == rf.SISTEMA:
            return ref(modelo, sistema, usuario, temp)
        from src.experiments import nivel_parecidas_b as nb
        if sistema == nb.SISTEMA:                                               # DI-CO22: las tres primeras candidatas
            return json.dumps({"ids": re.findall(r"^- (\S+) \|", usuario, re.M)[:3], "razon": "simulado"})
        return json.dumps({"preguntas": [{"codigo": cods[0], "sentido": "+", "peso": 2},
                                         {"codigo": cods[1], "sentido": "-", "peso": 1}],
                           "fuerza": "media", "sin_base": False, "nivel": 3.2, "justificacion": "simulado"})
    return llamar, e9.MODELO_SIMULADO
