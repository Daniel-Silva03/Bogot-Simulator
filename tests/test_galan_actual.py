"""
tests/test_galan_actual.py

Pruebas de src/experiments/galan_actual.py (`GALAN_ACTUAL_SPECIFICATION.md`). No llaman a la API ni leen datos.
Se ejecuta directo:  python tests/test_galan_actual.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from src.experiments import galan_actual as ga

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_la_mezcla_promedia_y_conserva_al_que_falta():
    m = ga.mezclar([{3: 1.0}, None, {1: 1.0}], [{1: 1.0}, {4: 1.0}, None])
    assert m[0] == {1: 0.5, 3: 0.5} and m[1] == {4: 1.0} and m[2] == {1: 1.0}


def test_positiva_suma_positiva_y_muy_positiva():
    assert abs(ga.positiva([{3: 0.5, 4: 0.25, 1: 0.25}, None], np.ones(2)) - 75) < 1e-9


def test_la_nota_es_la_del_preregistro_y_sin_direccion():
    doc = " ".join((Path(__file__).resolve().parents[1] / "docs" / "GALAN_ACTUAL_SPECIFICATION.md").read_text(encoding="utf-8")
                   .replace("> ", "").split())
    assert " ".join(ga.NOTA.split()) in doc
    for palabra in ("mejor", "peor", "subió", "bajó", "cayó", "%"):
        assert palabra not in ga.NOTA


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Galán hoy — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
