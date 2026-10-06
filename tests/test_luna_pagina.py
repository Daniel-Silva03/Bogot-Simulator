"""
tests/test_luna_pagina.py

Pruebas de src/experiments/luna_pagina.py: ninguna llama a la API.
Se ejecuta directo:  python tests/test_luna_pagina.py
"""

import sys
import tempfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.consulta import motor as mo
from src.experiments import experimento9 as e9
from src.experiments import luna_pagina as lp

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_la_parte_1_simulada_usa_la_validacion_de_la_reformulacion():
    llamar, _ = mo.cliente(simulado=True)
    r = lp.parte1(llamar, e9.Cache(Path(tempfile.mkdtemp()) / "c.json"), modelo=e9.MODELO_SIMULADO)
    assert r["pasa"] and len(r["por_pregunta"]) == 24 and set(r["criterios"]) == {"R1", "R2", "R3", "R4"}


def test_la_parte_2_compara_solo_las_que_tienen_estimacion_en_los_dos():
    luna = pd.DataFrame({"id": list("abcd"), "familia": list("abcd"), "total": [10.0, 80, 50, 30],
                         "alcance": ["nueva", "nueva", "catalogo", "nueva"], "S": [20.0, 70, None, None]})
    mimo = pd.DataFrame({"id": list("abcd"), "alcance": ["nueva", "nueva", "nueva", "nueva"], "S": [40.0, 60, 50, 30]})
    r = lp.comparar(luna, mimo, 23.4)
    assert r["n_ambos"] == 2 and r["luna"]["eam"] == 10 and r["mimo"]["eam"] == 25 and r["regla"]["cumple"]
    peor = lp.comparar(luna.assign(S=[45.0, 45, None, None]), mimo.assign(S=[20.0, 70, 50, 30]), 23.4)
    assert not peor["regla"]["cumple"]


def test_el_puente_por_defecto_sigue_con_el_modelo_de_la_pagina():
    from src.experiments import puente as pu
    import inspect
    src = inspect.getsource(lp.ps.main)
    assert 'default=pu.MODELO' in src and pu.MODELO == e9.MODELO


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"La página con Luna — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
