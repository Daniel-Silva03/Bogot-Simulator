"""
tests/test_temporal_fase_d.py

Pruebas de src/evaluacion/temporal_fase_d.py (`TEMPORAL_FASE_D_SPECIFICATION.md`). No leen la EPC.
Se ejecuta directo:  python tests/test_temporal_fase_d.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.evaluacion import temporal_fase_d as td

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_los_cuatro_metodos():
    p = td.predecir([40, 50])
    assert p == {"M0": 50, "M1": 45, "M2": 55, "M3": 47.5}


def test_cada_objetivo_usa_solo_lo_anterior():
    o = td.objetivos("S", [("a", 10), ("b", 20), ("c", 99), ("d", 30)])
    assert [f["fecha"] for f in o] == ["c", "d"] and o[0]["M0"] == 20 and o[1]["M0"] == 99


def test_las_series_son_las_del_preregistro():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "TEMPORAL_FASE_D_SPECIFICATION.md").read_text(encoding="utf-8")
    assert len(td.INVAMER) == 9 and len(td.CB) == 6
    for _, v in td.CB:
        assert f"{v:.1f}".replace(".", ",") in doc


def test_la_regla_pide_ganar_sin_los_dos_mejores():
    # M1 gana solo por dos objetivos: no pasa
    t = pd.DataFrame({"real": [50, 50, 50, 50], "M0": [60, 60, 50, 50], "M1": [50, 50, 52, 52], "M2": [70] * 4, "M3": [70] * 4})
    r = td.regla(t)
    assert r["error"]["M1"] < r["error"]["M0"] and "M1" not in r["pasan"] and r["elegido"] == "M0"


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Temporal Fase D — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
