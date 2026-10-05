"""
tests/test_nivel_acuerdo_lote5.py

Pruebas de src/experiments/nivel_acuerdo_lote5.py: ninguna llama a la API.
Se ejecuta directo:  python tests/test_nivel_acuerdo_lote5.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import nivel_acuerdo_lote5 as nl

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_b_son_las_92_mas_las_17_de_practica_del_lote_5_y_no_toca_el_guardado():
    a, b = nl.candidatas()
    assert len(a) == 92 and len(b) == 109 and set(a.id) <= set(b.id)
    nuevas = b[~b.id.isin(a.id)]
    assert nuevas.id.str.startswith("EDP25_").all() and len(nuevas) == 17
    import pandas as pd
    s = pd.read_csv(nl.ba.SALIDA / "sorteo_lote5.csv")
    assert set(nuevas.id) == set(s[s.conjunto == "practica"].id)


def test_la_regla_pide_las_tres_condiciones():
    ra = {"eam": 13.0}
    assert nl.regla(ra, {"pasa": True, "eam": 12.9, "acierto_al_decidir": 0.95, "decide": 0.2})["b_reemplaza_a_a"]
    assert not nl.regla(ra, {"pasa": True, "eam": 13.1, "acierto_al_decidir": 0.95, "decide": 0.2})["b_reemplaza_a_a"]
    assert not nl.regla(ra, {"pasa": False, "eam": 12, "acierto_al_decidir": 0.95, "decide": 0.2})["b_reemplaza_a_a"]
    assert not nl.regla(ra, {"pasa": True, "eam": 12, "acierto_al_decidir": 0.85, "decide": 0.2})["b_reemplaza_a_a"]
    assert not nl.regla(ra, {"pasa": True, "eam": 12, "acierto_al_decidir": None, "decide": 0})["b_reemplaza_a_a"]


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Estimación con el lote 5 — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
