"""Pruebas de la capa visual. Se corren solas: python3 tests/test_viz_mapa.py"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.viz.preparar_mapa import _dentro, construir  # noqa: E402

FALLOS: list[str] = []


def probar(nombre, condicion, detalle=""):
    if condicion:
        print(f"  ok   {nombre}")
    else:
        print(f"  FALLA {nombre} {detalle}")
        FALLOS.append(nombre)


def anillos_de(geom):
    return [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]


def main():
    d = construir()
    L = d["localidades"]

    print("estructura")
    probar("hay 20 localidades", len(L) == 20, f"hay {len(L)}")
    probar("códigos 01..20 sin huecos",
           sorted(l["codigo"] for l in L) == [f"{i:02d}" for i in range(1, 21)])
    probar("todas tienen nombre del marginal del proyecto",
           all(l["poblacion_18mas"] is not None for l in L))

    print("agentes")
    probar("el total de agentes coincide con la población",
           len(d["agentes"]) == d["ciudad"]["n_agentes"])
    probar("los agentes por localidad coinciden con n_agentes",
           all(l["indice_puntos"][1] - l["indice_puntos"][0] == l["n_agentes"] for l in L))

    # DI-V3: cada punto debe caer dentro de su propio polígono, incluso después
    # de redondear a cuatro decimales. Si esto falla, el mapa dibuja gente fuera
    # de su localidad y el dibujo deja de ser verificable.
    geo = {l["codigo"]: l["geometry"] for l in L}
    fuera = 0
    for x, y, cod, *_ in d["agentes"]:
        partes = anillos_de(geo[cod])
        if not any(_dentro(x, y, p[0]) and not any(_dentro(x, y, h) for h in p[1:]) for p in partes):
            fuera += 1
    probar("ningún agente cae fuera de su localidad", fuera == 0, f"{fuera} fuera")

    print("estadística")
    c = d["ciudad"]
    probar("la media de ciudad está en la escala 1-5", c["escala"][0] <= c["opinion_media"] <= c["escala"][1])
    probar("la dispersión dentro supera a la dispersión entre", c["sd_dentro"] > c["sd_entre"])
    # El error estándar usa el efecto de diseño medido, no muestreo aleatorio
    # simple: sin esa corrección saldría un factor sqrt(1.86) = 1.36 más chico.
    probar("el efecto de diseño aplicado es el medido en la EPC", abs(d["deff"] - 1.86) < 1e-9)
    probar("la fracción de ruido está entre 0 y 1", 0 <= c["fraccion_ruido"] <= 1)
    probar("sd_entre^2 = ruido^2 + real^2 (hasta redondeo)",
           abs(c["sd_entre"] ** 2 - (c["sd_entre_ruido"] ** 2 + c["sd_entre_real"] ** 2)) < 0.02,
           f"{c['sd_entre']} {c['sd_entre_ruido']} {c['sd_entre_real']}")

    print("reproducibilidad")
    d2 = construir()
    probar("la misma semilla produce los mismos puntos", d["agentes"] == d2["agentes"])

    print()
    if FALLOS:
        print(f"{len(FALLOS)} prueba(s) fallaron: {', '.join(FALLOS)}")
        sys.exit(1)
    print("todas las pruebas pasaron")


if __name__ == "__main__":
    main()
