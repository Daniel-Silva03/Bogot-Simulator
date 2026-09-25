"""Prepara la capa base urbana del mapa: vías arteriales, áreas verdes y agua.

Toma tres extractos de OpenStreetMap descargados con Overpass (vías, verde,
agua), los recorta al encuadre urbano del Distrito, los simplifica a
resolución de pantalla y produce un único JSON compacto que se inyecta en la
página autocontenida del hito 1.

Esta capa es DECORADO DE ORIENTACIÓN. No entra en el modelo: ningún agente,
ninguna opinión y ningún estadístico de este proyecto se calcula con ella. Su
única función es que quien mire el mapa reconozca la ciudad —la Autopista
Norte, la Caracas, Simón Bolívar, los cerros— y pueda ubicar las localidades
sin saberse los límites de memoria.

Decisiones de implementación
----------------------------
DI-V8   Fuente: OpenStreetMap vía Overpass, extracto del 21/09/2026, bajo
        ODbL. La atribución va en el pie de la página; es obligación de la
        licencia, no cortesía. Los archivos crudos quedan versionados en
        ``data/external/geo/osm/`` para que el paquete sea reproducible sin
        volver a consultar Overpass.

DI-V9   Simplificación: Douglas-Peucker con tolerancia 0,0002° (~22 m) en
        vías y 0,00015° (~17 m) en polígonos, y redondeo final a cuatro
        decimales (~11 m), la misma resolución que la geometría de
        localidades (DI-V1). Es resolución de dibujo. Esta capa no sirve para
        medir distancias, áreas ni accesibilidad.

DI-V10  Las vías vienen de Overpass partidas en miles de tramos (5.429 en el
        extracto). Antes de simplificar se vuelven a unir por extremos
        compartidos: 5.429 tramos se convierten en 178 polilíneas. Sin ese
        paso el archivo pesa diez veces más y Douglas-Peucker no tiene nada
        que simplificar dentro de un tramo de dos puntos.

DI-V11  Recorte por caja envolvente de las 19 localidades urbanas más un
        margen de 0,01°, NO por el límite político del Distrito. Consecuencia
        deliberada y visible: dentro del encuadre aparecen vías y parques de
        Soacha, Mosquera, Funza y Chía. La ciudad no se acaba en el borde de
        Bogotá y fingir que sí lo hace es peor que mostrarlo; la página dice
        que la capa base es regional y que las localidades son lo único que
        delimita el Distrito.

DI-V12  Las áreas verdes salen en dos niveles de detalle: las de 2 ha o más
        se dibujan siempre y las de 0,5 a 2 ha solo al acercar. A la escala de
        la ciudad entera un parque de barrio mide menos de tres píxeles y solo
        aporta ruido visual; al acercarse a una localidad es justamente lo que
        permite reconocer el barrio. Por debajo de 0,5 ha se descarta todo: son
        separadores viales y antejardines, no orientación.

DI-V13  Codificación delta en décimas de milésima de grado y enteros. Un
        ``[-74.0721,4.6097]`` ocupa 18 caracteres; el mismo punto como delta
        entero ocupa 3. El paquete pasa de ~120 KB a ~35 KB sin perder un
        solo punto, y la página lo decodifica en una línea.

DI-V14  Si falta ``agua.geojson`` el script no falla: emite la capa vacía y
        lo declara en los metadatos. El agua es la capa que más ayuda a
        reconocer Bogotá (el Bogotá, el Fucha, el Tunjuelo, los humedales) y
        conviene tenerla, pero la página tiene que poder construirse sin ella.

DI-V15  Las vías también salen en dos niveles: ``trunk`` se dibuja siempre y
        ``primary`` aparece al acercar. No es solo peso de archivo: a escala de
        ciudad entera las 129 polilíneas de ``primary`` se cruzan unas con
        otras y tapan la coropleta, que es el dato. El detalle aparece cuando
        hay resolución para leerlo.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
OSM = RAIZ / "data" / "external" / "geo" / "osm"
LOCALIDADES = RAIZ / "data" / "external" / "geo" / "localidades_bogota.geojson"
SALIDA = RAIZ / "data" / "processed" / "viz" / "base_bogota.json"

MARGEN = 0.01           # grados alrededor de la caja urbana (DI-V11)
TOL_VIA = 0.0002        # ~22 m (DI-V9)
TOL_POLIGONO = 0.00015  # ~17 m (DI-V9)
DECIMALES = 4           # ~11 m, igual que DI-V1
ESCALA = 10 ** DECIMALES
AREA_MINIMA_M2 = 2 * 10_000       # verde de primer nivel: 2 ha (DI-V12)
AREA_MINIMA_DETALLE_M2 = 5_000    # verde de segundo nivel: 0,5 ha (DI-V12)
SUMAPAZ = "20"

# Grados cuadrados -> metros cuadrados, aproximación local a 4,6° de latitud.
M2_POR_GRADO2 = 111_320 * 111_320 * 0.9968


# --------------------------------------------------------------------------- #
# Geometría
# --------------------------------------------------------------------------- #
def douglas_peucker(puntos: list[list[float]], tol: float) -> list[list[float]]:
    """Simplifica una polilínea conservando sus extremos. Implementación iterativa."""
    if len(puntos) < 3:
        return puntos
    conservar = [False] * len(puntos)
    conservar[0] = conservar[-1] = True
    pila = [(0, len(puntos) - 1)]
    while pila:
        i, j = pila.pop()
        if j <= i + 1:
            continue
        ax, ay = puntos[i]
        bx, by = puntos[j]
        dx, dy = bx - ax, by - ay
        den = dx * dx + dy * dy
        peor, indice = -1.0, -1
        for k in range(i + 1, j):
            px, py = puntos[k]
            if den == 0:
                d = ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
            else:
                t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / den))
                d = ((px - (ax + t * dx)) ** 2 + (py - (ay + t * dy)) ** 2) ** 0.5
            if d > peor:
                peor, indice = d, k
        if peor > tol:
            conservar[indice] = True
            pila.append((i, indice))
            pila.append((indice, j))
    return [p for p, c in zip(puntos, conservar) if c]


def unir_tramos(tramos: list[list[list[float]]]) -> list[list[list[float]]]:
    """Encadena tramos que comparten extremo exacto (DI-V10).

    Overpass devuelve cada vía partida en los nodos donde cambia cualquier
    etiqueta. Encadenar por extremo idéntico recupera corredores continuos.
    """
    extremos: dict[tuple, list[int]] = defaultdict(list)
    for i, t in enumerate(tramos):
        extremos[tuple(t[0])].append(i)
        extremos[tuple(t[-1])].append(i)
    usado = [False] * len(tramos)
    lineas: list[list[list[float]]] = []
    for i in range(len(tramos)):
        if usado[i]:
            continue
        usado[i] = True
        linea = list(tramos[i])
        for _ in range(2):  # extender por la cola, dar la vuelta, extender de nuevo
            while True:
                cola = tuple(linea[-1])
                siguiente = next((j for j in extremos.get(cola, ()) if not usado[j]), None)
                if siguiente is None:
                    break
                usado[siguiente] = True
                t = tramos[siguiente]
                linea += t[1:] if tuple(t[0]) == cola else list(reversed(t))[1:]
            linea.reverse()
        lineas.append(linea)
    return lineas


def redondear(puntos: list[list[float]]) -> list[list[float]]:
    """Redondea a DECIMALES y elimina puntos consecutivos que colapsan."""
    salida: list[list[float]] = []
    for x, y in puntos:
        p = [round(x, DECIMALES), round(y, DECIMALES)]
        if not salida or p != salida[-1]:
            salida.append(p)
    return salida


def codificar(puntos: list[list[float]]) -> list[int]:
    """Aplana una polilínea a enteros delta en unidades de 1e-4 grados (DI-V13)."""
    salida: list[int] = []
    px = py = 0
    for x, y in puntos:
        ix, iy = round(x * ESCALA), round(y * ESCALA)
        salida.append(ix - px)
        salida.append(iy - py)
        px, py = ix, iy
    return salida


def area_anillo(anillo: list[list[float]]) -> float:
    """Área por fórmula del cordón, en grados cuadrados."""
    a = 0.0
    n = len(anillo)
    for i in range(n):
        x1, y1 = anillo[i]
        x2, y2 = anillo[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2


# --------------------------------------------------------------------------- #
# Recorte
# --------------------------------------------------------------------------- #
def caja_urbana() -> tuple[float, float, float, float]:
    """Caja envolvente de las 19 localidades urbanas, con margen (DI-V11)."""
    geo = json.loads(LOCALIDADES.read_text(encoding="utf-8"))
    xs: list[float] = []
    ys: list[float] = []

    def recorrer(c):
        if isinstance(c[0], (int, float)):
            xs.append(c[0])
            ys.append(c[1])
        else:
            for k in c:
                recorrer(k)

    for f in geo["features"]:
        if str(f["properties"]["codigo"]).zfill(2) == SUMAPAZ:
            continue
        recorrer(f["geometry"]["coordinates"])
    return (min(xs) - MARGEN, min(ys) - MARGEN, max(xs) + MARGEN, max(ys) + MARGEN)


def toca(puntos, caja) -> bool:
    x0, y0, x1, y1 = caja
    return any(x0 <= x <= x1 and y0 <= y <= y1 for x, y in puntos)


def leer(nombre: str) -> list[dict]:
    ruta = OSM / nombre
    if not ruta.exists():
        return []
    return json.loads(ruta.read_text(encoding="utf-8"))["features"]


# --------------------------------------------------------------------------- #
# Capas
# --------------------------------------------------------------------------- #
def capa_vias(caja) -> dict[str, list[list[int]]]:
    por_clase: dict[str, list] = defaultdict(list)
    for f in leer("vias.geojson"):
        if f["geometry"]["type"] != "LineString":
            continue
        pts = f["geometry"]["coordinates"]
        if len(pts) < 2 or not toca(pts, caja):
            continue
        clase = f["properties"].get("highway", "otra")
        por_clase[clase].append([[x, y] for x, y, *_ in pts])

    salida: dict[str, list[list[int]]] = {}
    for clase, tramos in sorted(por_clase.items()):
        lineas = []
        for linea in unir_tramos(tramos):
            simple = redondear(douglas_peucker(linea, TOL_VIA))
            if len(simple) >= 2:
                lineas.append(codificar(simple))
        salida[clase] = lineas
    return salida


def _anillos_exteriores(geom: dict) -> list[list[list[float]]]:
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    if geom["type"] == "MultiPolygon":
        return [poly[0] for poly in geom["coordinates"]]
    return []


def capa_poligonos(nombre: str, caja, area_grande: float, area_minima: float) -> dict[str, list[list[int]]]:
    """Devuelve los polígonos en dos niveles de detalle (DI-V12).

    ``g`` son los que se dibujan siempre; ``p`` los que solo aparecen al
    acercar. El corte es por área, no por importancia: un parque de barrio
    importa, pero no a la escala a la que cabe la ciudad entera.
    """
    salida: dict[str, list[list[int]]] = {"g": [], "p": []}
    for f in leer(nombre):
        for anillo in _anillos_exteriores(f["geometry"]):
            pts = [[x, y] for x, y, *_ in anillo]
            if len(pts) < 4 or not toca(pts, caja):
                continue
            area = area_anillo(pts) * M2_POR_GRADO2
            if area < area_minima:
                continue
            simple = redondear(douglas_peucker(pts, TOL_POLIGONO))
            if len(simple) >= 4:
                salida["g" if area >= area_grande else "p"].append(codificar(simple))
    return salida


def capa_lineas(nombre: str, caja, filtro) -> list[list[int]]:
    tramos = []
    for f in leer(nombre):
        if f["geometry"]["type"] != "LineString":
            continue
        if not filtro(f["properties"]):
            continue
        pts = [[x, y] for x, y, *_ in f["geometry"]["coordinates"]]
        if len(pts) < 2 or not toca(pts, caja):
            continue
        tramos.append(pts)
    lineas = []
    for linea in unir_tramos(tramos):
        simple = redondear(douglas_peucker(linea, TOL_VIA))
        if len(simple) >= 2:
            lineas.append(codificar(simple))
    return lineas


# --------------------------------------------------------------------------- #
def construir() -> dict:
    caja = caja_urbana()
    vias = capa_vias(caja)
    verde = capa_poligonos("verde.geojson", caja, AREA_MINIMA_M2, AREA_MINIMA_DETALLE_M2)
    # El agua se queda entera desde el primer nivel: un humedal pequeño ubica
    # mejor que un parque grande, y son muchos menos polígonos.
    agua_area = capa_poligonos("agua.geojson", caja, 0, AREA_MINIMA_DETALLE_M2)
    agua_linea = capa_lineas("agua.geojson", caja, lambda p: "waterway" in p)

    return {
        "meta": {
            "fuente": "OpenStreetMap (Overpass), extracto del 21/09/2026",
            "licencia": "ODbL — © colaboradores de OpenStreetMap",
            "escala": ESCALA,
            "caja": [round(v, 4) for v in caja],
            "decisiones": ["DI-V8", "DI-V9", "DI-V10", "DI-V11", "DI-V12", "DI-V13", "DI-V14", "DI-V15"],
            "uso": "orientación visual; no entra en ningún cálculo del modelo",
            "capas_presentes": {
                "vias": (OSM / "vias.geojson").exists(),
                "verde": (OSM / "verde.geojson").exists(),
                "agua": (OSM / "agua.geojson").exists(),
            },
            "area_minima_m2": AREA_MINIMA_M2,
            "area_minima_detalle_m2": AREA_MINIMA_DETALLE_M2,
            "tolerancia_via": TOL_VIA,
            "tolerancia_poligono": TOL_POLIGONO,
        },
        "vias": vias,
        "verde": verde,
        "agua": {"areas": agua_area, "cauces": agua_linea},
    }


def main() -> None:
    datos = construir()
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    m = datos["meta"]
    print(f"caja urbana: {m['caja']}")
    for clase, lineas in datos["vias"].items():
        print(f"  vías {clase:<10} {len(lineas):>5} polilíneas, {sum(len(l) for l in lineas)//2:>6} puntos")
    for nivel, etiqueta in (("g", "verde ≥2 ha"), ("p", "verde <2 ha")):
        capa = datos["verde"][nivel]
        print(f"  {etiqueta:<16} {len(capa):>5} polígonos, {sum(len(p) for p in capa)//2:>6} puntos")
    for nivel, etiqueta in (("g", "agua grande"), ("p", "agua chica")):
        capa = datos["agua"]["areas"][nivel]
        print(f"  {etiqueta:<16} {len(capa):>5} polígonos, {sum(len(p) for p in capa)//2:>6} puntos")
    print(f"  agua cauces      {len(datos['agua']['cauces']):>5} polilíneas, {sum(len(l) for l in datos['agua']['cauces'])//2:>6} puntos")
    if not m["capas_presentes"]["agua"]:
        print("  AVISO: falta data/external/geo/osm/agua.geojson; la capa de agua va vacía (DI-V14)")
    print(f"{SALIDA.relative_to(RAIZ)}  {SALIDA.stat().st_size/1024:.1f} KB")


if __name__ == "__main__":
    main()
