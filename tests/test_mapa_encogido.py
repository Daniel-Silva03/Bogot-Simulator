"""
tests/test_mapa_encogido.py

Pruebas de src/experiments/mapa_encogido.py (`MAPA_ENCOGIDO_SPECIFICATION.md`). No leen datos.
Se ejecuta directo:  python tests/test_mapa_encogido.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from src.experiments import mapa_encogido as me

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_sin_diferencia_real_todas_toman_el_ancla():
    m = np.array([49.0, 51.0]); v = np.array([10.0, 10.0])               # varianza entre (1) < ruido (10): τ² = 0
    assert np.allclose(me.encoger(m, v, np.array([50.0, 50.0])), 50.0)


def test_con_poco_ruido_casi_no_se_mueven_y_la_ruidosa_se_mueve_mas():
    m = np.array([20.0, 50.0, 80.0]); v = np.array([0.01, 0.01, 200.0])
    s = me.encoger(m, v, np.full(3, 50.0))
    assert abs(s[0] - 20) < 0.1 and abs(s[2] - 80) > abs(s[0] - 20) and 50 < s[2] < 80


def test_el_ancla_del_estrato_es_una_recta():
    a = me.ancla_estrato(np.array([10.0, 20.0, 30.0]), np.array([1.0, 2.0, 3.0]))
    assert np.allclose(a, [10, 20, 30])


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Mapa encogido — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
