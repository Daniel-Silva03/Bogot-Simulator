"""Pósters de Bogotá dibujados desde los extractos locales, sin prettymaps.

Es la alternativa a ``poster.py`` para dos casos concretos: cuando el CNC
decide que la AGPL-3.0 de prettymaps no entra al proyecto, y cuando la máquina
donde hay que generar el póster no puede instalar la pila de osmnx/geopandas o
no tiene salida a Overpass.

Dibuja con matplotlib y la librería estándar, leyendo los mismos GeoJSON que
alimentan la capa base del tablero. No consulta la red.

Lo que NO hace, y conviene saberlo antes de comparar resultados: prettymaps
saca su aspecto característico de las **huellas de edificios**, y este script
dibuja lo que haya en ``data/external/geo/osm/``. Con los extractos actuales
—vías arteriales, áreas verdes y agua— el resultado se parece a prettymaps en
paleta y tratamiento, pero no en textura. Para acercarlo hay que bajar un
extracto ``building`` de una zona y dejarlo como ``edificios.geojson``.

Decisiones de implementación
----------------------------
DI-P5  Sin shapely ni geopandas. Los anillos de cada polígono se pasan a un
       único ``Path`` de matplotlib, que resuelve los agujeros por regla
       par-impar. Es suficiente para dibujar y evita una pila de dependencias
       que en el equipo de destino puede no instalarse.

DI-P6  El recorte circular se hace con ``set_clip_path``, no filtrando
       geometrías: una vía que entra y sale del círculo se corta en el borde
       en vez de desaparecer entera.

DI-P7  La proyección es la misma del tablero —longitud escalada por el coseno
       de la latitud de referencia— para que los dos productos coincidan y
       para no arrastrar pyproj.

Uso
---
    python src/viz/poster_matplotlib.py            # todas las zonas
    python src/viz/poster_matplotlib.py ciudad
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, PathPatch
from matplotlib.path import Path as MPath

RAIZ = Path(__file__).resolve().parents[2]
OSM = RAIZ / "data" / "external" / "geo" / "osm"
LOCALIDADES = RAIZ / "data" / "external" / "geo" / "localidades_bogota.geojson"
SALIDA = RAIZ / "data" / "processed" / "viz" / "posters"

LAT0 = 4.6
K = math.cos(math.radians(LAT0))
M_POR_GRADO = 111320.0

PAPEL = "#e9ece7"
TINTA = "#16211c"
PARAMO = "#2f6b5e"
AGUA = "#3d6f8c"
MURO = "#cfd6ce"

ANCHO_VIA = {"motorway": 3.2, "trunk": 2.6, "primary": 1.5, "secondary": 1.0,
             "tertiary": 0.7, "residential": 0.35}

ZONAS = {
    "centro":    {"punto": (4.5981, -74.0758), "radio": 1100,  "titulo": "Centro histórico"},
    "chapinero": {"punto": (4.6465, -74.0629), "radio": 1300,  "titulo": "Chapinero"},
    "kennedy":   {"punto": (4.6285, -74.1497), "radio": 1600,  "titulo": "Kennedy"},
    "usaquen":   {"punto": (4.6947, -74.0306), "radio": 1200,  "titulo": "Usaquén"},
    "ciudad":    {"punto": (4.6480, -74.0980), "radio": 13000, "titulo": "Bogotá"},
}


def px(lon): return lon * K
def py(lat): return lat


def leer(nombre):
    ruta = OSM / nombre
    if not ruta.exists():
        return []
    return json.loads(ruta.read_text(encoding="utf-8"))["features"]


def anillos(geom):
    """Todos los anillos de un Polygon o MultiPolygon, exteriores e interiores."""
    if geom["type"] == "Polygon":
        return list(geom["coordinates"])
    if geom["type"] == "MultiPolygon":
        return [r for poly in geom["coordinates"] for r in poly]
    return []


def camino(lista_anillos):
    """Un solo Path con todos los anillos; matplotlib resuelve los agujeros (DI-P5)."""
    verts, codes = [], []
    for anillo in lista_anillos:
        pts = [(px(x), py(y)) for x, y, *_ in anillo]
        if len(pts) < 3:
            continue
        verts += pts + [pts[0]]
        codes += [MPath.MOVETO] + [MPath.LINETO] * (len(pts) - 1) + [MPath.CLOSEPOLY]
    return MPath(verts, codes) if verts else None


def dibujar(clave, recorte_circular=True):
    z = ZONAS[clave]
    lat, lon = z["punto"]
    cx, cy = px(lon), py(lat)
    r = z["radio"] / M_POR_GRADO          # radio en grados de latitud
    margen = r * 1.02

    fig, ax = plt.subplots(figsize=(12, 12))
    fig.patch.set_facecolor(PAPEL)
    ax.set_facecolor(PAPEL)
    ax.set_xlim(cx - margen, cx + margen)
    ax.set_ylim(cy - margen, cy + margen)
    ax.set_aspect(1 / K)
    ax.axis("off")

    recorte = Circle((cx, cy), r, transform=ax.transData)

    def clip(artista):
        if recorte_circular:
            artista.set_clip_path(recorte)

    # --- contorno de las localidades, como textura de fondo
    if LOCALIDADES.exists():
        for f in json.loads(LOCALIDADES.read_text(encoding="utf-8"))["features"]:
            c = camino(anillos(f["geometry"]))
            if c is None:
                continue
            p = PathPatch(c, fc=MURO, ec=TINTA, lw=0.5, zorder=1)
            ax.add_patch(p); clip(p)

    # --- edificios, si alguien bajó el extracto
    for f in leer("edificios.geojson"):
        c = camino(anillos(f["geometry"]))
        if c is None:
            continue
        p = PathPatch(c, fc="#bcc5bb", ec=TINTA, lw=0.25, zorder=5)
        ax.add_patch(p); clip(p)

    # --- verde y agua
    for nombre, color, z_ord, alpha, hatch in [
        ("verde.geojson", PARAMO, 2, 0.75, "...."),
        ("agua.geojson", AGUA, 3, 0.9, None),
    ]:
        for f in leer(nombre):
            c = camino(anillos(f["geometry"]))
            if c is None:
                continue
            p = PathPatch(c, fc=color, ec=TINTA, lw=0.3, alpha=alpha,
                          hatch=hatch, zorder=z_ord)
            ax.add_patch(p); clip(p)

    # --- cauces
    for f in leer("agua.geojson"):
        if f["geometry"]["type"] != "LineString":
            continue
        xs = [px(x) for x, y, *_ in f["geometry"]["coordinates"]]
        ys = [py(y) for x, y, *_ in f["geometry"]["coordinates"]]
        ln, = ax.plot(xs, ys, color=AGUA, lw=1.2, solid_capstyle="round", zorder=3.5)
        clip(ln)

    # --- vías
    for f in leer("vias.geojson"):
        g = f["geometry"]
        if g["type"] != "LineString":
            continue
        clase = f["properties"].get("highway", "residential")
        xs = [px(x) for x, y, *_ in g["coordinates"]]
        ys = [py(y) for x, y, *_ in g["coordinates"]]
        ln, = ax.plot(xs, ys, color=TINTA, lw=ANCHO_VIA.get(clase, 0.5),
                      solid_capstyle="round", solid_joinstyle="round", zorder=6)
        clip(ln)

    if recorte_circular:
        ax.add_patch(Circle((cx, cy), r, fc="none", ec=TINTA, lw=2.5, zorder=10))

    ax.text(0.5, -0.02, z["titulo"], transform=ax.transAxes, ha="center", va="top",
            fontsize=30, color=TINTA)
    ax.text(0.5, -0.06, "© colaboradores de OpenStreetMap · ODbL  ·  Bogotá Social Simulator",
            transform=ax.transAxes, ha="center", va="top", fontsize=9, color="#48564f")

    SALIDA.mkdir(parents=True, exist_ok=True)
    destino = SALIDA / f"{clave}_local.png"
    fig.savefig(destino, dpi=200, facecolor=PAPEL, bbox_inches="tight")
    plt.close(fig)
    print(f"  {clave:<10} -> {destino.relative_to(RAIZ)}")
    return destino


def main() -> None:
    claves = [a for a in sys.argv[1:] if not a.startswith("-")] or list(ZONAS)
    if not OSM.exists():
        print(f"falta {OSM.relative_to(RAIZ)}: deja ahí vias/verde/agua.geojson")
        return
    for c in claves:
        if c in ZONAS:
            dibujar(c, recorte_circular=(c != "ciudad"))
        else:
            print(f"zona desconocida: {c}; disponibles: {', '.join(ZONAS)}")


if __name__ == "__main__":
    main()
