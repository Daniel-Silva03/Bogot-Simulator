"""Pruebas del paquete de serie temporal (Hito 2) y de su llegada a la página.

Lo que se protege acá no es que el gráfico se vea bien, es que **no afirme más
precisión de la que hay**: que cada punto lleve su intervalo, que el punto cuyo
margen viene de un DEFF prestado esté marcado como tal, y que un hueco de años
sin medición no se convierta en una línea continua.

    python3 tests/test_viz_serie.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.viz.preparar_serie import SALTO_ANIOS, construir  # noqa: E402

FALLOS: list[str] = []
Z = 1.959963984540054


def probar(nombre, condicion, detalle=""):
    if condicion:
        print(f"  ok   {nombre}")
    else:
        FALLOS.append(nombre)
        print(f"  FALLA {nombre} {detalle}")


def main():
    d = construir()
    series = d["series"]

    print("estructura")
    probar("hay dos series", len(series) == 2, f"hay {len(series)}")
    probar("cada serie se identifica y se nombra",
           all(s.get("clave") and s.get("nombre") and s.get("fuente") for s in series))
    probar("el paquete advierte que no es simulación",
           "no salidas del simulador" in d["advertencia"])
    # DI-V38: comparten la escala y no el concepto. Si alguien alguna vez
    # calcula una diferencia entre las dos, esta prueba no lo va a impedir,
    # pero el paquete no se la da hecha.
    probar("el paquete no precalcula ninguna comparación entre series",
           not any(k in d for k in ("diferencia", "brecha_series", "correlacion")))

    print("puntos")
    for s in series:
        nombre = s["nombre"]
        p = s["puntos"]
        probar(f"{nombre}: tiene puntos", len(p) > 0)
        probar(f"{nombre}: ningún año repetido",
               len({q['anio'] for q in p}) == len(p))
        probar(f"{nombre}: los años van en orden",
               [q["anio"] for q in p] == sorted(q["anio"] for q in p))
        probar(f"{nombre}: todas las medias caen en la escala",
               all(s["escala"][0] <= q["media"] <= s["escala"][1] for q in p),
               str([q["media"] for q in p]))
        probar(f"{nombre}: el intervalo contiene siempre a la media",
               all(q["ic95"][0] <= q["media"] <= q["ic95"][1] for q in p))
        # El intervalo tiene que ser el que declara el error estándar; si se
        # dibujara uno más angosto, el gráfico mentiría justo donde importa.
        peor = max(abs((q["ic95"][1] - q["ic95"][0]) - 2 * Z * q["ee"]) for q in p)
        probar(f"{nombre}: el intervalo es exactamente ±1,96 EE",
               peor < 0.01, f"peor desvío {peor:.4f}")
        probar(f"{nombre}: cada punto dice si su error se midió o se prestó",
               all("con_diseno" in q for q in p))
        probar(f"{nombre}: ningún n es cero", all(q["n"] > 0 for q in p))

    print("origen del margen (DI-V37)")
    ecp = next(s for s in series if s["clave"] == "ecp_confianza")
    epc = next(s for s in series if s["clave"].startswith("epc_"))
    # La ECP no publica variables de diseño: ni un solo punto suyo puede
    # declararse estimado con diseño, por buena que sea la muestra.
    probar("ningún punto de la ECP se declara estimado con diseño",
           not any(q["con_diseno"] for q in ecp["puntos"]))
    probar("la ECP explica que su DEFF es prestado",
           "PRESTADO" in ecp["nota_error"])
    probar("la EPC sí tiene olas con diseño real",
           any(q["con_diseno"] for q in epc["puntos"]))
    probar("y también olas sin él, marcadas",
           any(not q["con_diseno"] for q in epc["puntos"]))
    probar("los años con diseño de la EPC coinciden con los puntos marcados",
           set(epc["anios_con_diseno"]) == {q["anio"] for q in epc["puntos"] if q["con_diseno"]})

    print("huecos y exclusiones (DI-V39, DI-V40)")
    for s in series:
        t = s["tramos"]
        probar(f"{s['nombre']}: hay un tramo entre cada par de puntos",
               len(t) == len(s["puntos"]) - 1)
        probar(f"{s['nombre']}: el salto se marca exactamente cuando hay hueco",
               all(x["salto"] == (x["brecha"] > SALTO_ANIOS) for x in t))
    # 2015 existe en disco y se deja fuera a propósito (DI-C10). Que la
    # exclusión viaje con su motivo es lo que impide que alguien la "arregle".
    excl = {e["anio"]: e["motivo"] for e in ecp["excluidos"]}
    probar("la ECP declara 2015 como excluido, con motivo",
           2015 in excl and len(excl[2015]) > 20,
           f"excluidos: {sorted(excl)}")
    probar("y 2015 no está entre los puntos",
           2015 not in {q["anio"] for q in ecp["puntos"]})

    print("la página construida")
    pagina = (RAIZ / "data" / "processed" / "viz" / "mapa_bogota.html").read_text(encoding="utf-8")
    probar("no queda el marcador de la serie sin sustituir",
           "/*__SERIE__*/" not in pagina)
    for marca, que in [
        ("function dibujarSerie()", "la página dibuja la serie"),
        ("id=\"serieDatos\"", "el paquete va en su propio nodo, sin chocar con la sección"),
        ("--s-ecp:#14588a", "el color de la ECP es el validado en claro"),
        ("--s-epc:#b8531f", "el color de la EPC es el validado en claro"),
        ("--s-ecp:#3f92cc", "hay un paso propio para modo oscuro"),
        ("const GEO_S", "la geometría del gráfico vive en un solo lugar"),
        (".serie .marcador{pointer-events:none}", "el área de clic recibe el puntero, no el dibujo"),
        ("function tablaSerie()", "los valores se pueden leer sin el cursor"),
        ("margen aproximado", "la lectura distingue el margen prestado"),
        ("stroke-dasharray=\\\"5 4\\\"", "el tramo con hueco va punteado"),
    ]:
        probar(que, marca.replace('\\"', '"') in pagina)

    # Redundancia de forma: si el color falla, círculo y cuadrado siguen
    # distinguiendo las dos series.
    probar("cada serie tiene además su propia forma de marcador",
           "<circle" in pagina and "marcaPunto" in pagina)

    print()
    if FALLOS:
        print(f"{len(FALLOS)} prueba(s) fallaron: {', '.join(FALLOS)}")
        sys.exit(1)
    print("todas las pruebas pasaron")


if __name__ == "__main__":
    main()
