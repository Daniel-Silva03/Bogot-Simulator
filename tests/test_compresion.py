"""
tests/test_compresion.py

Pruebas de src/experiments/compresion.py (`COMPRESION_SPECIFICATION.md`). No leen datos.
Se ejecuta directo:  python tests/test_compresion.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from src.experiments import compresion as cm

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_una_estimacion_aplanada_tiene_pendiente_mayor_que_1():
    y = np.array([10.0, 30, 50, 70, 90])
    s = 50 + (y - 50) / 2                                       # la mitad de la amplitud
    c = cm.compresion(s, y)
    assert c["pendiente"] == 2.0 and c["sd_estimacion"] < c["sd_real"]
    a, b = cm.ajustar(s, y)
    assert np.allclose(cm.estirar(s, a, b), y)


def test_estirar_recorta_a_0_100():
    assert list(cm.estirar(np.array([0.0, 100.0]), -50, 3)) == [0.0, 100.0]


def test_fuera_de_muestra_no_usa_su_familia():
    y = np.array([10.0, 30, 50, 70, 90] * 4); s = 50 + (y - 50) / 2
    fam = np.repeat(np.arange(5), 4)
    assert np.allclose(cm.fuera_de_muestra(s, y, fam), y)        # la relación es la misma en todas las familias


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Compresión — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
