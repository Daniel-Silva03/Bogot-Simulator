"""Prepara el paquete de datos que alimenta el mapa interactivo de Bogotá.

Toma la geometría oficial de las 20 localidades (Catastro Distrital) y la
población sintética ya validada, y produce un único JSON con todo lo que el
mapa necesita. El mapa no consulta nada más: se publica como una página
autocontenida.

Decisiones de implementación
----------------------------
DI-V1  La geometría es la capa ``Localidad`` del MapServer de la Unidad
       Administrativa Especial de Catastro Distrital, simplificada en el
       servidor (``maxAllowableOffset = 0,0007`` ≈ 70 m) y redondeada a cuatro
       decimales (≈ 11 m). Es resolución de pantalla, no de análisis: sirve
       para dibujar, no para calcular áreas ni para asignar manzanas.

DI-V2  Los nombres de localidad se toman del marginal del proyecto
       (``data/external/marginal_localidad_18mas.csv``), no del servicio
       geográfico, y se unen por ``COD_LOC``. El servicio devuelve los nombres
       en mayúsculas y sin tildes; usar los suyos rompería el join con toda la
       tubería de población.

DI-V3  La posición de cada agente DENTRO de su localidad es arbitraria. El
       modelo no tiene geografía sub-localidad: un agente sabe en qué
       localidad vive y nada más. Los puntos se sortean uniformemente dentro
       del polígono con semilla fija para que el dibujo sea reproducible, y la
       página lo dice explícitamente. No representan domicilios.

DI-V4  El error estándar de la media por localidad se calcula con el efecto de
       diseño medido en la EPC (mediana 1,86; ver claude/ANALISIS_DISENO_MUESTRAL.md),
       no asumiendo muestreo aleatorio simple. Sin esa corrección las bandas
       saldrían ~40 % más angostas de lo que son.

DI-V34 La ficha de la escala (`escala_opinion`) NO se escribe acá: se copia
       tal cual del metadata de la población. El mapa no puede describir la
       variable de otra forma que como la describió el pipeline que la
       produjo; si se dejara escrita a mano en dos lugares, el día que cambie
       el donante la página seguiría diciendo lo de antes (A05).

DI-V43 El paquete trae **las cinco olas**, no una. Y la razón por la que eso
       es barato es también la razón por la que el mapa por año significa algo:
       las cinco poblaciones se construyen con la MISMA muestra del receptor
       (misma semilla, mismo método), así que los 1.000 agentes son las mismas
       1.000 personas sintéticas en los cinco años y lo único que cambia entre
       años es `opinion_t0`.

       Consecuencias, las tres:
         · La geometría, las posiciones de los puntos y la composición
           demográfica por localidad se guardan **una sola vez**. Lo único que
           se repite por año son 1.000 opiniones y 20 medias.
         · Cualquier diferencia que el lector vea entre dos años es del dato,
           no del muestreo. Si cada año hubiera sorteado su propia muestra, una
           parte del cambio sería el sorteo y no habría forma de separarlos.
         · El script **verifica** esa identidad en vez de confiarse: si las
           demografías no coinciden entre años, falla. Compartir posiciones
           entre poblaciones distintas dibujaría a una persona de Suba en
           Kennedy sin que nada avisara.

DI-V44 El ruido se recalcula por año, no se hereda, y **se mide en vez de
       derivarse**. El mapa por año es exactamente el gráfico que §31 advierte:
       cinco cortes que parpadean y parecen movimiento territorial. Cada año
       trae por tanto su propia descomposición, y la página la muestra al
       cambiar de año.

DI-V45 **El `ee` analítico subestima el ruido territorial, y eso se descubrió
       construyendo este paquete.** `sd_ruido² = promedio(ee²)` supone que las
       1.000 opiniones son extracciones independientes. No lo son: el hot-deck
       empareja por celda demográfica y el desempate ponderado de DI-M1 permite
       que **dos agentes de la misma celda reciban el valor del mismo donante**.
       Los agentes de una localidad comparten celdas más que dos agentes
       cualesquiera, así que la opinión queda agrupada por localidad **por
       construcción**, y ese agrupamiento no entra en `ee`.

       Se vio en la ECP 2021: la descomposición analítica atribuía solo el 52 %
       de la dispersión a ruido y dejaba una «dispersión real» de 0,236 — el
       único año de los cinco que parecía tener señal territorial. Rehaciendo el
       pipeline con veinte semillas, `sd_entre` de 2021 recorre 0,148 a 0,515 y
       la corrida publicada (0,341) cae en el **percentil 85 de su propia
       variación por semilla**. No hay señal: hay una semilla afortunada.

       *Corrección DI-V52 (25/09/2026):* la primera mitad se sostiene (una sola
       corrida no es estable); «no hay señal» no, porque la corrida publicada
       sale del mismo proceso que las semillas y su percentil es uniforme haya
       o no efecto. La razón válida para no leer geografía es que el donante no
       trae localidad. Ver DI-V52 en VISUALIZATION_SPECIFICATION.md.

       El piso correcto lo mide `src/viz/piso_territorial.py` y llega acá en
       `piso_territorial.json`. La página usa ESE, no el analítico, para
       afirmar cuánto es ruido. El analítico se conserva en el paquete porque
       sigue siendo el que corresponde a las barras del inspector, pero ya no
       es el que sostiene ninguna afirmación territorial.

       *Una prueba de permutación no sirve para esto, y se intentó:* rompe a la
       vez el vínculo localidad→demografía y el agrupamiento del hot-deck, y da
       p = 0,0005 para un efecto que no existe. El null correcto conserva las
       dos cosas y solo cambia la semilla.

DI-V48 La coropleta de población también es por año, y **los dos marginales
       viven separados a propósito**.

       `marginal_localidad_18mas.csv` es el objetivo del muestreo PPS (D14):
       uno solo, la revisión DANE-SDP de 2025, y es contra ese que se sortearon
       los 1.000 agentes. La columna «esperados» del inspector sigue siendo de
       ese marginal y de ningún otro, porque describe el muestreo, no la ciudad.

       `marginal_localidad_18mas_serie.csv` es población 18+ por localidad y por
       año, y existe solo para dibujar. Si la serie reemplazara al marginal de
       muestreo, cada corrida de la población tendría que elegir un año y
       «esperados» dejaría de significar lo mismo entre corridas.

       El paquete trae los dos, y cada número dice de qué año es.

DI-V49 La rampa de población se ancla al máximo de TODOS los años, no al del
       año en pantalla. La razón está medida: entre 2013 y 2023 Bogotá 18+ crece
       16,4 %, pero el reparto entre localidades casi no se mueve (distancia L1
       de 0,0201). Con la rampa reescalada año a año, el mapa se vería casi
       idéntico en los cinco y el crecimiento —que es lo único que de verdad
       cambia— quedaría invisible. Con la rampa fija, el mapa se oscurece, que
       es exactamente lo que pasó.

DI-V50 **Y aun con la rampa fija, la coropleta de población casi no se mueve.**
       Medido después de construirla: la diferencia máxima de color entre 2013
       y 2023 es de 13 sobre 255 por canal. Lado a lado los dos mapas se ven
       iguales.

       No es un defecto de implementación, es el dato: Bogotá 18+ crece 16,4 %,
       el reparto entre localidades se mueve 0,0201 en distancia L1, y la raíz
       cuadrada de DI-V36 comprime lo que queda (√1,164 = 1,08, un 8 % de
       recorrido sobre la rampa). Las localidades grandes, además, ya están
       cerca del extremo oscuro y no tienen a dónde oscurecerse.

       Lo que sí cambia de forma legible son las **cifras**: 5.221.648 en 2013
       contra 6.077.736 en 2023, en el panel y en el encabezado. Así que el
       paquete transporta `poblacion_resumen` y la página **dice** que el color
       apenas se mueve, en vez de dejar que el lector concluya que el botón está
       roto. Un control que hace algo invisible no es mucho mejor que uno que no
       hace nada; lo que lo salva es nombrar lo invisible.

DI-V5  La escala de color de la capa de opinión se ancla al rango real de
       variación entre localidades, no al rango observado en la muestra. Es la
       advertencia de PROJECT_CONTEXT §31: un mapa de Bogotá coloreado por
       opinión con escala estirada es el gráfico más vendedor del tablero y el
       más engañoso.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
GEOJSON = RAIZ / "data" / "external" / "geo" / "localidades_bogota.geojson"
MARGINAL = RAIZ / "data" / "external" / "marginal_localidad_18mas.csv"
MARGINAL_SERIE = RAIZ / "data" / "external" / "marginal_localidad_18mas_serie.csv"
#: Las olas de la ECP que el proyecto sabe apilar (ver ecp.ANIOS_COMPARABLES).
#: 2015 no está y no es un olvido: sus códigos apuntan a otras instituciones.
ANIOS = (2013, 2017, 2019, 2021, 2023)

DIR_POB = RAIZ / "data" / "processed"
POBLACION_DE = lambda a: DIR_POB / f"poblacion_ecp{a}.csv"          # noqa: E731
METADATA_DE = lambda a: DIR_POB / f"poblacion_ecp{a}_metadata.json"  # noqa: E731


def _leer_poblacion(a: int):
    """La población del año, leída del archivo que su metadata dice que se escribió.

    `build_agents` escribe `.parquet` si la máquina tiene motor de parquet y
    `.csv` si no. Leer siempre `.csv` hacía que, en una máquina con pyarrow, el
    mapa tomara en silencio un CSV viejo en vez de la población recién
    construida (corregido el 29/09/2026). Sin metadata, se cae al CSV de siempre.
    """
    meta = METADATA_DE(a)
    if meta.exists():
        archivo = json.loads(meta.read_text(encoding="utf-8")).get("archivo_datos")
        ruta = DIR_POB / archivo if archivo else None
        if ruta is not None and ruta.exists():
            return pd.read_parquet(ruta) if ruta.suffix == ".parquet" else pd.read_csv(ruta)
    ruta = POBLACION_DE(a)
    return pd.read_csv(ruta) if ruta.exists() else None

#: Las columnas que TIENEN que ser idénticas entre años (DI-V43).
DEMOGRAFICAS = ["agent_id", "edad", "sexo", "localidad", "estrato", "nivel_educativo"]
SALIDA = RAIZ / "data" / "processed" / "viz" / "mapa_bogota.json"

#: Piso de ruido medido (DI-V45). Lo produce src/viz/piso_territorial.py, que
#: tarda ~4 minutos; por eso no se recalcula acá, se lee.
PISO = RAIZ / "data" / "processed" / "viz" / "piso_territorial.json"

DEFF = 1.86  # mediana medida en la EPC sobre 11 mediciones (DI-V4)
SEMILLA = 42

BANDAS_EDAD = [(18, 29), (30, 44), (45, 59), (60, 200)]
ETIQUETA_EDAD = ["18-29", "30-44", "45-59", "60+"]
ETIQUETA_EDUC = {0: "Ninguno/primaria", 1: "Secundaria", 2: "Técnico/tecnológico", 3: "Universitario o más"}


def _anillos(geom: dict) -> list[list]:
    """Devuelve la lista de anillos (exterior primero) de un Polygon o MultiPolygon."""
    if geom["type"] == "Polygon":
        return geom["coordinates"]
    anillos: list[list] = []
    for poly in geom["coordinates"]:
        anillos.extend(poly)
    return anillos


def _dentro(x: float, y: float, anillo: list) -> bool:
    """Ray casting sobre un anillo cerrado."""
    dentro = False
    n = len(anillo)
    j = n - 1
    for i in range(n):
        xi, yi = anillo[i]
        xj, yj = anillo[j]
        if (yi > y) != (yj > y):
            xc = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < xc:
                dentro = not dentro
        j = i
    return dentro


def puntos_en_poligono(geom: dict, n: int, rng: np.random.Generator) -> list[tuple[float, float]]:
    """Sortea n puntos uniformes dentro del polígono (DI-V3). Rechaza los huecos.

    El reparto entre partes de un MultiPolygon es proporcional al área del
    anillo exterior. Se sortea por rechazo dentro de la caja envolvente de cada
    parte; el bucle tiene tope de intentos para no colgarse con geometrías muy
    delgadas, y lo que falte se completa con la parte de mayor área.
    """
    partes = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]

    def area(anillo):
        s = 0.0
        for i in range(len(anillo) - 1):
            s += anillo[i][0] * anillo[i + 1][1] - anillo[i + 1][0] * anillo[i][1]
        return abs(s) / 2

    areas = np.array([area(p[0]) for p in partes], dtype=float)
    pesos = areas / areas.sum()
    cupos = np.floor(pesos * n).astype(int)
    while cupos.sum() < n:  # reparte el resto a la parte más grande
        cupos[int(np.argmax(pesos))] += 1

    salida: list[tuple[float, float]] = []
    for parte, cupo in zip(partes, cupos):
        if cupo == 0:
            continue
        ext, huecos = parte[0], parte[1:]
        xs = [c[0] for c in ext]
        ys = [c[1] for c in ext]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        obtenidos = 0
        intentos = 0
        while obtenidos < cupo and intentos < 500 * cupo + 5000:
            intentos += 1
            # se redondea ANTES de probar: el redondeo a 4 decimales mueve el
            # punto hasta ~5 m y podría sacarlo del polígono cerca del borde
            x = round(rng.uniform(x0, x1), 4)
            y = round(rng.uniform(y0, y1), 4)
            if not _dentro(x, y, ext):
                continue
            if any(_dentro(x, y, h) for h in huecos):
                continue
            salida.append((x, y))
            obtenidos += 1
        if obtenidos < cupo:
            raise RuntimeError(
                f"no se pudieron sortear {cupo} puntos dentro de la parte "
                f"(obtenidos {obtenidos}); geometría demasiado delgada"
            )
    return salida


def centroide(geom: dict) -> tuple[float, float]:
    """Centroide del anillo exterior más grande (para colocar la etiqueta)."""
    partes = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
    mejor, mejor_area = None, -1.0
    for parte in partes:
        anillo = parte[0]
        s = cx = cy = 0.0
        for i in range(len(anillo) - 1):
            x0, y0 = anillo[i]
            x1, y1 = anillo[i + 1]
            cruz = x0 * y1 - x1 * y0
            s += cruz
            cx += (x0 + x1) * cruz
            cy += (y0 + y1) * cruz
        if abs(s) < 1e-12:
            continue
        a = abs(s) / 2
        if a > mejor_area:
            mejor_area = a
            mejor = (cx / (3 * s), cy / (3 * s))
    return (round(mejor[0], 4), round(mejor[1], 4))


def ficha_escala(anios) -> dict:
    """La ficha de la variable, copiada del metadata de la población (DI-V34).

    Se lee del PRIMER año disponible y se comprueba contra los demás: si dos
    olas describieran la variable distinto, el mapa estaría mezclando dos
    mediciones bajo una sola etiqueta.
    """
    fichas = {}
    for a in anios:
        ruta = METADATA_DE(a)
        if not ruta.exists():
            raise FileNotFoundError(
                f"Falta {ruta.name}: el mapa no puede publicar una escala 1-5 sin "
                f"decir qué mide. Regenerar con 'python src/population/"
                f"construir_poblacion.py --donante ecp:{a} --nombre-base poblacion_ecp{a}'.")
        meta = json.loads(ruta.read_text(encoding="utf-8"))
        if not meta.get("escala_opinion"):
            raise KeyError(f"{ruta.name} no trae 'escala_opinion'; viene de una corrida "
                           f"anterior a A05. Hay que regenerar esa población.")
        fichas[a] = meta

    base = dict(fichas[anios[0]]["escala_opinion"])
    for a in anios[1:]:
        otra = fichas[a]["escala_opinion"]
        for campo in ("concepto", "rango", "anclas", "direccion", "construccion"):
            if base.get(campo) != otra.get(campo):
                raise ValueError(
                    f"La ficha de la escala difiere entre {anios[0]} y {a} en «{campo}». "
                    f"Dos mediciones distintas no pueden compartir una sola etiqueta.")

    # La fuente sí cambia por año: es el único campo que se guarda por ola.
    base["fuente_por_anio"] = {str(a): fichas[a].get("donante_fuente", "") for a in anios}
    base["fuente"] = ("Encuesta de Cultura Política (DANE), submuestra de Bogotá — "
                      f"olas {anios[0]}–{anios[-1]}")
    base["n_items_por_anio"] = {
        str(a): fichas[a]["escala_opinion"].get("n_items", {}) for a in anios}
    return base


def cargar_poblaciones() -> dict:
    """Las cinco olas, verificando que sean la misma gente (DI-V43).

    La verificación no es ceremonia: el paquete guarda una sola posición por
    agente y una sola composición por localidad para los cinco años. Si las
    demografías no fueran idénticas, esa economía dibujaría a la persona
    equivocada en el sitio equivocado, en silencio.
    """
    pobs = {}
    for a in ANIOS:
        pob = _leer_poblacion(a)
        if pob is not None:
            pobs[a] = pob
    if not pobs:
        raise FileNotFoundError(
            f"No hay ninguna población en {DIR_POB.relative_to(RAIZ).as_posix()}. "
            f"Se esperaba poblacion_ecp<año>.csv para alguno de {list(ANIOS)}.")

    anios = sorted(pobs)
    base = pobs[anios[0]]
    for a in anios[1:]:
        if not base[DEMOGRAFICAS].equals(pobs[a][DEMOGRAFICAS]):
            raise ValueError(
                f"La población de {a} no es la misma muestra que la de {anios[0]}: las "
                f"columnas demográficas difieren. Las cinco olas tienen que construirse "
                f"con la misma semilla y el mismo método, o el mapa por año mezclaría "
                f"cambio de opinión con cambio de muestra (DI-V43).")
    return pobs


def _resumen_ciudad(pob: pd.DataFrame, localidades: list[dict], anio: int) -> dict:
    """La descomposición ruido/real de un año (DI-V44)."""
    medias = [l["por_anio"][str(anio)]["opinion_media"] for l in localidades
              if l["por_anio"][str(anio)]["opinion_media"] is not None]
    ees = [l["por_anio"][str(anio)]["opinion_ee"] for l in localidades
           if l["por_anio"][str(anio)]["opinion_ee"] is not None]
    sd_entre = float(np.std(medias, ddof=1))
    var_ruido = float(np.mean([e ** 2 for e in ees]))
    var_obs = float(sd_entre ** 2)
    frac = min(1.0, var_ruido / var_obs) if var_obs > 0 else None
    return {
        "opinion_media": round(float(pob["opinion_t0"].mean()), 3),
        "sd_dentro": round(float(pob.groupby("localidad")["opinion_t0"].std().mean()), 3),
        "sd_entre": round(sd_entre, 3),
        "sd_entre_ruido": round(math.sqrt(var_ruido), 3),
        "sd_entre_real": round(math.sqrt(max(0.0, var_obs - var_ruido)), 3),
        "fraccion_ruido": None if frac is None else round(frac, 3),
        "n_agentes": int(len(pob)),
        "escala": [1, 5],
    }


def cargar_marginal_serie(anios) -> dict | None:
    """Población 18+ por localidad y año, para la coropleta (DI-V48).

    Si falta, el mapa sigue funcionando con el marginal único y la página lo
    dice: una capa que no cambia es un defecto menor; una capa que cambia con
    números inventados sería otra cosa.
    """
    if not MARGINAL_SERIE.exists():
        print(f"AVISO: falta {MARGINAL_SERIE.name}. La coropleta de población no "
              f"podrá cambiar con el año. Generarlo con 'python "
              f"src/population/extraer_columnas_em2021.py marginal-serie'.")
        return None
    d = pd.read_csv(MARGINAL_SERIE)
    d["codigo"] = d["COD_LOC"].astype(int).astype(str).str.zfill(2)
    faltan = [a for a in anios if a not in set(d["anio"])]
    if faltan:
        print(f"AVISO: {MARGINAL_SERIE.name} no cubre {faltan}; esos años usarán el "
              f"marginal único.")
    return {int(a): dict(zip(g["codigo"], g["poblacion"].astype(int)))
            for a, g in d.groupby("anio")}


def _resumen_poblacion(serie_pob, anios) -> dict | None:
    """Cuánto crece la ciudad y cuánto se mueve el reparto (DI-V50).

    Las dos cifras juntas son la explicación de por qué el mapa casi no cambia:
    crece el total, no el reparto, y la rampa dibuja el reparto.
    """
    if not serie_pob or len(anios) < 2:
        return None
    a0, a1 = anios[0], anios[-1]
    t0 = sum(serie_pob[a0].values())
    t1 = sum(serie_pob[a1].values())
    sh0 = {k: v / t0 for k, v in serie_pob[a0].items()}
    sh1 = {k: v / t1 for k, v in serie_pob[a1].items()}
    l1 = sum(abs(sh1[k] - sh0.get(k, 0)) for k in sh1) / 2

    # Quién crece y quién no: eso sí es un patrón territorial real, aunque la
    # coropleta de NIVEL no lo pueda mostrar.
    crec = {k: (serie_pob[a1][k] / serie_pob[a0][k] - 1) for k in serie_pob[a1]
            if serie_pob[a0].get(k)}
    orden = sorted(crec, key=crec.get)
    return {
        "anio_min": a0, "anio_max": a1,
        "total_min": int(t0), "total_max": int(t1),
        "crecimiento_pct": round(100 * (t1 / t0 - 1), 1),
        "l1_reparto": round(l1, 4),
        "crecimiento_por_localidad": {k: round(100 * v, 1) for k, v in crec.items()},
        "menos_crece": orden[0], "mas_crece": orden[-1],
        "rango_crecimiento_pct": [round(100 * crec[orden[0]], 1),
                                  round(100 * crec[orden[-1]], 1)],
    }


def cargar_piso() -> dict | None:
    """El piso de ruido medido, si está. Si no, se avisa y el mapa lo dice."""
    if not PISO.exists():
        print(f"AVISO: falta {PISO.name}. El paquete saldrá sin piso medido y la "
              f"página tendrá que usar el ruido analítico, que lo SUBESTIMA "
              f"(DI-V45). Generarlo con 'python src/viz/piso_territorial.py'.")
        return None
    return json.loads(PISO.read_text(encoding="utf-8"))


def construir() -> dict:
    geo = json.loads(GEOJSON.read_text(encoding="utf-8"))
    marg = pd.read_csv(MARGINAL)
    marg["codigo"] = marg["COD_LOC"].astype(int).astype(str).str.zfill(2)
    nombres = dict(zip(marg["codigo"], marg["localidad"]))

    pobs = cargar_poblaciones()
    anios = sorted(pobs)
    serie_pob = cargar_marginal_serie(anios)
    base = pobs[anios[0]]          # la demografía, idéntica en los cinco
    rng = np.random.default_rng(SEMILLA)

    localidades = []
    puntos = []
    orden_agentes = []             # el orden en que los agentes entran a `puntos`

    for f in sorted(geo["features"], key=lambda f: f["properties"]["codigo"]):
        cod = f["properties"]["codigo"]
        nombre = nombres.get(cod, f["properties"]["nombre"])
        fila_marg = marg[marg["codigo"] == cod]
        sub = base[base["localidad"] == nombre]
        n = len(sub)

        # La composición es de la muestra, no del año: las cinco olas son las
        # mismas personas (DI-V43), así que se guarda una vez.
        comp = {}
        if n > 0:
            comp["sexo"] = {k: int(v) for k, v in sub["sexo"].value_counts().items()}
            comp["edad"] = {
                et: int(((sub["edad"] >= lo) & (sub["edad"] <= hi)).sum())
                for (lo, hi), et in zip(BANDAS_EDAD, ETIQUETA_EDAD)}
            comp["estrato"] = {
                str(int(k)): int(v)
                for k, v in sorted(sub["estrato"].dropna().value_counts().items())}
            comp["educacion"] = {
                ETIQUETA_EDUC.get(int(k), str(k)): int(v)
                for k, v in sorted(sub["nivel_educativo"].dropna().value_counts().items())}

        pts = puntos_en_poligono(f["geometry"], n, rng) if n > 0 else []
        inicio = len(puntos)
        for (x, y), (_, ag) in zip(pts, sub.iterrows()):
            puntos.append([x, y, cod, int(ag["edad"]), ag["sexo"],
                           None if pd.isna(ag["estrato"]) else int(ag["estrato"])])
            orden_agentes.append(int(ag["agent_id"]))

        por_anio = {}
        for a in anios:
            s_a = pobs[a].loc[sub.index, "opinion_t0"]
            # Población del AÑO para la coropleta; el marginal de muestreo
            # queda aparte, en `poblacion_18mas` (DI-V48).
            pob_anio = (serie_pob.get(a, {}).get(cod) if serie_pob else None)
            if n > 0:
                media = float(s_a.mean())
                sd = float(s_a.std(ddof=1)) if n > 1 else float("nan")
                ee = float(sd / math.sqrt(n) * math.sqrt(DEFF)) if n > 1 else float("nan")
            else:
                media = sd = ee = float("nan")
            por_anio[str(a)] = {
                "poblacion_18mas": pob_anio,
                "opinion_media": None if math.isnan(media) else round(media, 3),
                "opinion_sd": None if n < 2 or math.isnan(sd) else round(sd, 3),
                "opinion_ee": None if n < 2 or math.isnan(ee) else round(ee, 3),
            }

        localidades.append({
            "codigo": cod,
            "nombre": nombre,
            "geometry": f["geometry"],
            "centroide": centroide(f["geometry"]),
            # El marginal DE MUESTREO (revisión 2025). Sostiene «esperados» y
            # no cambia con el año: describe el sorteo, no la ciudad (DI-V48).
            "poblacion_18mas": int(fila_marg["poblacion"].iloc[0]) if len(fila_marg) else None,
            "share": float(fila_marg["share"].iloc[0]) if len(fila_marg) else None,
            "n_agentes": n,
            "esperado": round(float(fila_marg["share"].iloc[0]) * len(base), 1) if len(fila_marg) else None,
            "composicion": comp,
            "por_anio": por_anio,
            "indice_puntos": [inicio, inicio + len(pts)],
        })

    # Las opiniones, en el mismo orden que `puntos`. Una lista por año.
    idx = {int(i): k for k, i in enumerate(base["agent_id"])}
    opiniones = {
        str(a): [round(float(pobs[a]["opinion_t0"].iloc[idx[i]]), 2) for i in orden_agentes]
        for a in anios
    }

    piso = cargar_piso()
    ciudad = {str(a): _resumen_ciudad(pobs[a], localidades, a) for a in anios}
    if piso:
        for a in anios:
            p = piso["por_anio"].get(str(a))
            if not p:
                continue
            # El piso medido reemplaza al analítico para CUALQUIER afirmación
            # territorial. El analítico se conserva, renombrado, porque sigue
            # siendo el que corresponde a las barras por localidad.
            c = ciudad[str(a)]
            c["fraccion_ruido_analitica"] = c.pop("fraccion_ruido")
            c["sd_entre_real_analitica"] = c.pop("sd_entre_real")
            c["piso_medido"] = {
                "mediana": p["piso_mediana"],
                "p95": p["piso_p95"],
                "min": p["piso_min"],
                "max": p["piso_max"],
                "percentil_publicada": p["percentil_publicada"],
                "sale_del_piso": p["sale_del_piso"],
                "semillas": len(piso["semillas"]),
            }
            # Con el piso medido, «cuánto es ruido» deja de ser una fracción
            # derivada y pasa a ser una pregunta de sí o no: ¿esta corrida se
            # sale de lo que el método produce sin fenómeno alguno?
            # CORRECCIÓN DI-V52: no lo es. Las semillas salen del mismo proceso
            # que la corrida publicada, así que superar su p95 pasa ~5 % de las
            # veces haya o no efecto. El campo conserva su nombre para no romper
            # el paquete, pero la página ya no lo lee.
            c["hay_senal_territorial"] = p["sale_del_piso"]

    return {
        "version": "0.3",
        "fuente_geometria": "UAECD — Catastro Distrital, capa Localidad (MapServer), simplificada",
        "fuente_poblacion": (f"poblacion_ecp<año>.csv, {len(anios)} olas "
                             f"({anios[0]}–{anios[-1]}), 1.000 agentes, misma muestra"),
        "deff": DEFF,
        "semilla": SEMILLA,
        "anios": anios,
        "anio_base": anios[0],
        "marginal_muestreo": {
            "fuente": "Proyecciones DANE-SDP, revisión 2025 (18+)",
            "para": ("objetivo del muestreo PPS (D14) y base de la columna «esperados». "
                     "Es uno solo y no cambia con el año."),
        },
        "poblacion_por_anio": bool(serie_pob),
        # La rampa se ancla al máximo de TODOS los años (DI-V49): reescalarla
        # por año escondería el crecimiento, que es lo único que cambia.
        "poblacion_max": (
            max(v for m in serie_pob.values() for v in m.values()) if serie_pob
            else max((l["poblacion_18mas"] or 0) for l in localidades)),
        "poblacion_resumen": _resumen_poblacion(serie_pob, anios),
        "misma_muestra": True,
        "ciudad_por_anio": ciudad,
        "piso_territorial": (
            {"semillas": len(piso["semillas"]), "conclusion": piso["conclusion"]}
            if piso else None),
        "localidades": localidades,
        "agentes": puntos,
        "opiniones": opiniones,
        "escala_opinion": ficha_escala(anios),
    }


def main() -> None:
    datos = construir()
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{SALIDA}  {SALIDA.stat().st_size/1024:.1f} KB")
    print(f"  {len(datos['localidades'])} localidades, {len(datos['agentes'])} agentes, "
          f"{len(datos['anios'])} olas {datos['anios']}")
    print(f"  {'año':>6}  {'media':>6}  {'sd entre':>8}  {'piso p95':>8}  {'pct':>5}  señal")
    for a in datos["anios"]:
        c = datos["ciudad_por_anio"][str(a)]
        piso = c.get("piso_medido")
        if piso:
            print(f"  {a:>6}  {c['opinion_media']:>6.3f}  {c['sd_entre']:>8.3f}  "
                  f"{piso['p95']:>8.3f}  {piso['percentil_publicada']:>4.0f}%  "
                  f"{'SÍ' if c['hay_senal_territorial'] else 'no'}")
        else:
            print(f"  {a:>6}  {c['opinion_media']:>6.3f}  {c['sd_entre']:>8.3f}  "
                  f"{'—':>8}  {'—':>5}  sin piso medido")
    if datos.get("piso_territorial"):
        print(f"  {datos['piso_territorial']['conclusion']}")
        print("  («piso p95» es la dispersión que el propio método produce solo cambiando "
              "la semilla — DI-V45)")


if __name__ == "__main__":
    main()
