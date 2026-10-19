"""
tests/test_no_diluir.py

Pruebas de src/experiments/no_diluir.py (`NO_DILUIR_SPECIFICATION.md`). No llaman a la API ni leen datos.
Se ejecuta directo:  python tests/test_no_diluir.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from src.experiments import no_diluir as nd

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_la_calibracion_lleva_el_total_a_la_encuesta_y_conserva_las_diferencias():
    ps = [{"A": 0.6, "B": 0.2, "blanco": 0.2}, {"A": 0.2, "B": 0.6, "blanco": 0.2}]
    w = np.ones(2)
    k = nd.calibrar(ps, w, ["A", "B"], {"A": 30.0, "B": 70.0})
    t = nd.total(k, w, ["A", "B", "blanco"])
    assert abs(100 * t["A"] / (t["A"] + t["B"]) - 30) < 2                     # cerca de la meta
    assert k[0]["A"] > k[1]["A"]                                              # el primero sigue más inclinado a A
    assert abs(sum(k[0].values()) - 1) < 1e-9


def test_los_textos_son_los_del_preregistro_y_sin_bogota():
    doc = " ".join((Path(__file__).resolve().parents[1] / "docs" / "NO_DILUIR_SPECIFICATION.md").read_text(encoding="utf-8")
                   .replace("> ", "").split())
    for t in (nd.INSTRUCCION, nd.PRIMERA_VUELTA, nd.GUARUMO, nd.PREGUNTA_2V):
        assert " ".join(t.split()) in doc, t[:40]
    for t in (nd.INSTRUCCION, nd.PRIMERA_VUELTA, nd.GUARUMO):
        assert "Bogotá" not in t.replace("no solo de Bogotá", "")
    assert round(nd.REAL_2V, 1) == 53.6


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"No diluir — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
