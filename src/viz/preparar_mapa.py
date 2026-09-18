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
POBLACION = RAIZ / "data" / "processed" / "poblacion_ecp2013.csv"
SALIDA = RAIZ / "data" / "processed" / "viz" / "mapa_bogota.json"

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


def construir() -> dict:
    geo = json.loads(GEOJSON.read_text(encoding="utf-8"))
    marg = pd.read_csv(MARGINAL)
    marg["codigo"] = marg["COD_LOC"].astype(int).astype(str).str.zfill(2)
    nombres = dict(zip(marg["codigo"], marg["localidad"]))

    pob = pd.read_csv(POBLACION)
    rng = np.random.default_rng(SEMILLA)

    # --- estadísticos de ciudad -------------------------------------------
    media_ciudad = float(pob["opinion_t0"].mean())
    sd_dentro = float(pob.groupby("localidad")["opinion_t0"].std().mean())

    localidades = []
    puntos = []
    for f in sorted(geo["features"], key=lambda f: f["properties"]["codigo"]):
        cod = f["properties"]["codigo"]
        nombre = nombres.get(cod, f["properties"]["nombre"])
        fila_marg = marg[marg["codigo"] == cod]
        sub = pob[pob["localidad"] == nombre]
        n = len(sub)

        if n > 0:
            media = float(sub["opinion_t0"].mean())
            sd = float(sub["opinion_t0"].std(ddof=1)) if n > 1 else float("nan")
            ee = float(sd / math.sqrt(n) * math.sqrt(DEFF)) if n > 1 else float("nan")
        else:
            media = sd = ee = float("nan")

        comp = {}
        if n > 0:
            comp["sexo"] = {k: int(v) for k, v in sub["sexo"].value_counts().items()}
            bandas = {}
            for (lo, hi), et in zip(BANDAS_EDAD, ETIQUETA_EDAD):
                bandas[et] = int(((sub["edad"] >= lo) & (sub["edad"] <= hi)).sum())
            comp["edad"] = bandas
            comp["estrato"] = {
                str(int(k)): int(v) for k, v in sorted(sub["estrato"].dropna().value_counts().items())
            }
            comp["educacion"] = {
                ETIQUETA_EDUC.get(int(k), str(k)): int(v)
                for k, v in sorted(sub["nivel_educativo"].dropna().value_counts().items())
            }

        pts = puntos_en_poligono(f["geometry"], n, rng) if n > 0 else []
        base = len(puntos)
        for (x, y), (_, ag) in zip(pts, sub.iterrows()):
            puntos.append(
                [x, y, cod, round(float(ag["opinion_t0"]), 2), int(ag["edad"]),
                 ag["sexo"], None if pd.isna(ag["estrato"]) else int(ag["estrato"])]
            )

        localidades.append(
            {
                "codigo": cod,
                "nombre": nombre,
                "geometry": f["geometry"],
                "centroide": centroide(f["geometry"]),
                "poblacion_18mas": int(fila_marg["poblacion"].iloc[0]) if len(fila_marg) else None,
                "share": float(fila_marg["share"].iloc[0]) if len(fila_marg) else None,
                "n_agentes": n,
                "esperado": round(float(fila_marg["share"].iloc[0]) * len(pob), 1) if len(fila_marg) else None,
                "opinion_media": None if math.isnan(media) else round(media, 3),
                "opinion_sd": None if n < 2 or math.isnan(sd) else round(sd, 3),
                "opinion_ee": None if n < 2 or math.isnan(ee) else round(ee, 3),
                "composicion": comp,
                "indice_puntos": [base, base + len(pts)],
            }
        )

    medias = [l["opinion_media"] for l in localidades if l["opinion_media"] is not None]
    sd_entre = float(np.std(medias, ddof=1))

    # Cuánto de la dispersión observada entre localidades es ruido de muestreo.
    # Bajo la hipótesis nula de que todas las localidades tienen la misma media,
    # la varianza esperada de las medias observadas es el promedio de los errores
    # estándar al cuadrado (ya corregidos por efecto de diseño, DI-V4).
    ees = [l["opinion_ee"] for l in localidades if l["opinion_ee"] is not None]
    var_ruido = float(np.mean([e ** 2 for e in ees]))
    var_obs = float(sd_entre ** 2)
    frac_ruido = min(1.0, var_ruido / var_obs) if var_obs > 0 else None
    sd_real = math.sqrt(max(0.0, var_obs - var_ruido))

    return {
        "version": "0.1",
        "fuente_geometria": "UAECD — Catastro Distrital, capa Localidad (MapServer), simplificada",
        "fuente_poblacion": "poblacion_ecp2013.csv v0.3-DI-M1 (1.000 agentes)",
        "deff": DEFF,
        "semilla": SEMILLA,
        "ciudad": {
            "opinion_media": round(media_ciudad, 3),
            "sd_dentro": round(sd_dentro, 3),
            "sd_entre": round(sd_entre, 3),
            "sd_entre_ruido": round(math.sqrt(var_ruido), 3),
            "sd_entre_real": round(sd_real, 3),
            "fraccion_ruido": None if frac_ruido is None else round(frac_ruido, 3),
            "n_agentes": int(len(pob)),
            "escala": [1, 5],
        },
        "localidades": localidades,
        "agentes": puntos,
    }


def main() -> None:
    datos = construir()
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{SALIDA}  {SALIDA.stat().st_size/1024:.1f} KB")
    print(f"  {len(datos['localidades'])} localidades, {len(datos['agentes'])} agentes")
    c = datos["ciudad"]
    print(f"  media ciudad {c['opinion_media']}  sd dentro {c['sd_dentro']}  sd entre {c['sd_entre']}")
    print(f"  de esa dispersión entre localidades, {c['fraccion_ruido']:.0%} es ruido muestral "
          f"(sd ruido {c['sd_entre_ruido']}, sd real estimada {c['sd_entre_real']})")


if __name__ == "__main__":
    main()
