"""
tests/test_texto_persona.py

Pruebas de src/experiments/texto_persona.py: ninguna llama a la API.
Se ejecuta directo:  python tests/test_texto_persona.py
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.consulta import reformular as rf
from src.experiments import experimento9 as e9
from src.experiments import texto_persona as tp

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_el_brazo_r_son_las_90_de_luna_pagina_y_sus_escalas_estan_en_cache():
    r = tp.brazo_r()
    o = tp.objetivos(r)
    assert len(r) == 90 and list(o.id) == list(r.id)
    cache = e9.Cache(tp.lp.CACHE)
    cat = rf.cargar_catalogo()
    assert all(len(tp.escala_reformulada(t, cat, cache)) == 5 for t in o.pregunta_pagina)   # DI-TP1: sin llamar


def test_la_regla():
    r = pd.DataFrame({"id": list("abcdef"), "total": [10.0, 80, 50, 30, 70, 20], "S": [40.0, 50, 50, 50, 50, 50]})
    t = pd.DataFrame({"id": list("abcdef"), "S": [15.0, 75, 50, 35, 68, 22]})
    ev = tp.evaluar(r, t, 23.4)
    assert ev["regla"]["cumple"] and ev["T"]["eam"] < ev["R"]["eam"] and ev["regla"]["al_decidir"] is None
    peor = tp.evaluar(r, r.copy(), 23.4)
    assert not peor["regla"]["cumple"]


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Texto de la persona — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
