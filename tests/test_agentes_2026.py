"""
tests/test_agentes_2026.py

Pruebas de src/experiments/agentes_2026.py (`AGENTES_2026_SPECIFICATION.md`). No llaman a la API ni leen datos.
Se ejecuta directo:  python tests/test_agentes_2026.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from src.experiments import agentes_2026 as ag

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_las_13_y_sus_escalas():
    e = ag.esc()
    assert [x["clave"] for x in e] == [f"V{i}" for i in range(1, 7)] + [f"K{i}" for i in range(1, 8)]
    k4 = next(x for x in e if x["clave"] == "K4")
    assert k4["validos"] == [1, 2, 3, 4, 5] and k4["fav"] == [1, 2] and "Persistir" in k4["categorias"][1]


def test_promediar_y_total():
    assert ag.promediar({1: 1.0, 2: 0.0}, {1: 0.0, 2: 1.0}) == {1: 0.5, 2: 0.5}
    assert ag.promediar(None, {1: 1.0}) == {1: 1.0}
    assert abs(ag.total([{1: 0.8, 2: 0.2}, None, {1: 0.4, 2: 0.6}], [1], np.array([1.0, 5.0, 1.0])) - 60.0) < 1e-9


def test_resumen_y_referencias():
    r = ag.resumen(dict(ag.PAGINA), {**ag.REAL_PUBLICO, **{f"K{i}": 50.0 for i in range(1, 8)}})
    assert r["n"] == 13 and r["error_publicas"] == 16.8
    doc = (Path(__file__).resolve().parents[1] / "docs" / "AGENTES_2026_SPECIFICATION.md").read_text(encoding="utf-8")
    assert "14,6" in doc and "18,1" in doc and str(ag.SEMILLA) in doc and "tope de\nUSD 1" in doc


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Agentes 2026 — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
