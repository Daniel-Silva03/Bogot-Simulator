"""
tests/test_rango_acuerdo.py

Pruebas de src/experiments/rango_acuerdo.py (`RANGO_ACUERDO_SPECIFICATION.md`). No leen datos.
Se ejecuta directo:  python tests/test_rango_acuerdo.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from src.experiments import rango_acuerdo as ra

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_el_acuerdo_es_la_desviacion_de_las_elegidas():
    t = {"a": 10.0, "b": 20.0, "c": 30.0}
    assert abs(ra.acuerdo(["a", "b", "c"], t) - np.std([10, 20, 30])) < 1e-9
    assert math.isnan(ra.acuerdo(["a"], t)) and math.isnan(ra.acuerdo(["a", "zz"], t))


def test_los_tercios_y_el_rango_de_cada_uno():
    sd = np.array([1.0, 2, 3, 10, 11, 12, 20, 21, 22, np.nan])
    err = np.array([1.0, 1, 1, 5, 5, 5, 20, 20, 20, 99])
    cortes, hs = ra.rangos_por_tercio(sd, err)
    assert hs == [1.0, 5.0, 20.0]
    assert ra.rango(2.0, cortes, hs, 23.9) == 1.0 and ra.rango(21.5, cortes, hs, 23.9) == 20.0
    assert ra.rango(float("nan"), cortes, hs, 23.9) == 23.9


def test_evaluar_cuenta_decisiones_y_cobertura():
    r = ra.evaluar(np.array([20.0, 80.0, 50.0]), np.array([30.0, 40.0, 52.0]), np.array([10.0, 10.0, 10.0]))
    assert r["decide"] == 2 and r["acierta"] == 1 and r["cobertura"] == round(2 / 3, 3)


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Rango según el acuerdo — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
