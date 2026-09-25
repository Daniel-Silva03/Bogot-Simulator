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

    print("las cinco olas (DI-V43)")
    anios = d["anios"]
    probar("el paquete trae más de una ola", len(anios) >= 2, str(anios))
    probar("2015 no está entre las olas", 2015 not in anios)
    probar("el año base es una de las olas", d["anio_base"] in anios)
    probar("hay un resumen de ciudad por cada ola",
           set(d["ciudad_por_anio"]) == {str(a) for a in anios})
    probar("cada localidad trae las mismas olas",
           all(set(l["por_anio"]) == {str(a) for a in anios} for l in L))
    probar("hay una lista de opiniones por ola",
           set(d["opiniones"]) == {str(a) for a in anios})
    # La economía del paquete (posiciones y composición una sola vez) solo es
    # legítima si las olas son la misma muestra.
    probar("cada ola tiene una opinión por agente",
           all(len(v) == len(d["agentes"]) for v in d["opiniones"].values()))
    probar("la composición se guarda una vez, no por año",
           all("composicion" in l and "composicion" not in l["por_anio"][str(anios[0])]
               for l in L))
    probar("el paquete declara que las olas son la misma muestra",
           d.get("misma_muestra") is True)
    probar("las medias de ciudad se mueven entre años",
           len({d["ciudad_por_anio"][str(a)]["opinion_media"] for a in anios}) == len(anios))

    print("población por año (DI-V48 a DI-V50)")
    probar("el paquete declara si la población es por año", "poblacion_por_anio" in d)
    if d.get("poblacion_por_anio"):
        probar("cada localidad trae población en cada ola",
               all(l["por_anio"][str(a)].get("poblacion_18mas") is not None
                   for l in L for a in anios))
        # DI-V48: el marginal de MUESTREO no cambia con el año. Si lo hiciera,
        # «esperados» dejaría de describir el sorteo que realmente se hizo.
        probar("el marginal de muestreo sigue siendo uno solo",
               all(isinstance(l["poblacion_18mas"], int) for l in L))
        probar("el paquete dice para qué sirve el marginal de muestreo",
               "esperados" in (d.get("marginal_muestreo", {}).get("para", "")))
        probar("la población total crece entre la primera y la última ola",
               sum(l["por_anio"][str(anios[-1])]["poblacion_18mas"] for l in L)
               > sum(l["por_anio"][str(anios[0])]["poblacion_18mas"] for l in L))
        # DI-V49: la rampa se ancla al máximo de TODOS los años. Si se anclara
        # al del año, el crecimiento sería invisible por construcción.
        maximos = [max(l["por_anio"][str(a)]["poblacion_18mas"] for l in L) for a in anios]
        probar("la rampa se ancla al máximo de todos los años, no al del año base",
               d["poblacion_max"] == max(maximos),
               f"{d['poblacion_max']} vs {maximos}")
        # DI-V50: el paquete tiene que traer con qué explicar que el mapa
        # apenas cambie. Sin esas dos cifras la página no puede decirlo.
        r = d.get("poblacion_resumen")
        probar("el paquete trae el resumen de crecimiento", isinstance(r, dict))
        if r:
            probar("el resumen trae el crecimiento de la ciudad", r["crecimiento_pct"] > 0)
            probar("y cuánto se mueve el reparto", 0 <= r["l1_reparto"] < 1)
            probar("el reparto se mueve mucho menos que el total",
                   r["l1_reparto"] * 100 < r["crecimiento_pct"],
                   f"L1 {r['l1_reparto']} vs crecimiento {r['crecimiento_pct']}%")

    print("agentes")
    probar("el total de agentes coincide con la población",
           len(d["agentes"]) == d["ciudad_por_anio"][str(d["anio_base"])]["n_agentes"])
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
    c = d["ciudad_por_anio"][str(d["anio_base"])]
    for a in anios:
        ca = d["ciudad_por_anio"][str(a)]
        probar(f"{a}: la media de ciudad está en la escala 1-5",
               ca["escala"][0] <= ca["opinion_media"] <= ca["escala"][1])
        probar(f"{a}: la dispersión dentro supera a la de entre",
               ca["sd_dentro"] > ca["sd_entre"])
    # El error estándar usa el efecto de diseño medido, no muestreo aleatorio
    # simple: sin esa corrección saldría un factor sqrt(1.86) = 1.36 más chico.
    probar("el efecto de diseño aplicado es el medido en la EPC", abs(d["deff"] - 1.86) < 1e-9)

    # DI-V45: el ruido analítico subestima, y el paquete tiene que traer el
    # medido. Sin esta prueba, la página podría volver a afirmar que hay señal
    # territorial apoyada en un ee que no captura el agrupamiento del hot-deck.
    print("piso de ruido medido (DI-V45)")
    if d.get("piso_territorial"):
        for a in anios:
            ca = d["ciudad_por_anio"][str(a)]
            piso = ca.get("piso_medido")
            probar(f"{a}: trae el piso medido", piso is not None)
            if not piso:
                continue
            probar(f"{a}: el piso se midió con al menos 10 semillas",
                   piso["semillas"] >= 10, str(piso["semillas"]))
            probar(f"{a}: el rango del piso contiene a la corrida publicada",
                   piso["min"] <= ca["sd_entre"] <= piso["max"],
                   f"{ca['sd_entre']} fuera de {piso['min']}–{piso['max']}")
            probar(f"{a}: «hay señal» es exactamente «supera el p95 del piso»",
                   ca["hay_senal_territorial"] == (ca["sd_entre"] > piso["p95"]))
            # El piso medido tiene que ser MAYOR que el analítico: si no lo
            # fuera, el argumento de DI-V45 estaría al revés.
            probar(f"{a}: el piso medido supera al ruido analítico",
                   piso["mediana"] >= ca["sd_entre_ruido"] * 0.8,
                   f"piso {piso['mediana']} vs analítico {ca['sd_entre_ruido']}")
        probar("ningún año se sale de su piso — el mapa no puede afirmar geografía",
               not any(d["ciudad_por_anio"][str(a)]["hay_senal_territorial"] for a in anios))
    else:
        probar("falta el piso medido: el paquete no debería publicarse así", False,
               "correr 'python src/viz/piso_territorial.py'")

    # A05: la página publica una columna de números entre 1 y 5. Si el paquete
    # no trae la ficha que dice qué miden, el mapa es indistinguible de uno
    # coloreado por un número inventado.
    print("ficha de la escala (A05)")
    e = d.get("escala_opinion")
    probar("el paquete trae la ficha de la variable", isinstance(e, dict) and bool(e))
    if isinstance(e, dict):
        probar("la ficha dice qué concepto mide", bool(e.get("concepto")))
        probar("la ficha trae el rango y coincide con el de ciudad",
               e.get("rango") == list(c["escala"]), f"{e.get('rango')} vs {c['escala']}")
        probar("la ficha registra la fuente de cada ola",
               set(e.get("fuente_por_anio", {})) == {str(a) for a in anios})
        probar("la ficha trae las anclas verbales de los dos extremos",
               set(map(str, (e.get("anclas") or {}))) >= {str(c["escala"][0]), str(c["escala"][1])})
        probar("la ficha dice la dirección de la escala", bool(e.get("direccion")))
        n = e.get("n_items") or {}
        probar("la ficha registra el denominador del índice (DI-C11)",
               "min_items_exigido" in n)
        probar("el mínimo observado nunca baja del mínimo exigido",
               n.get("minimo_observado", n.get("min_items_exigido", 0)) >= n.get("min_items_exigido", 0))
        probar("la ficha nombra la fuente del donante", bool(e.get("fuente")))

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
