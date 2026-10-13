"""
tests/test_peso_anio_reciente.py

Pruebas de src/experiments/peso_anio_reciente.py con datos inventados. No leen la EPC.
Se ejecuta directo:  python tests/test_peso_anio_reciente.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from src.experiments import peso_anio_reciente as pa

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_los_factores_de_las_tres_reglas():
    a = np.array([2022, 2023, 2024])
    assert list(pa.factor("A", a, 2024)) == [1, 1, 1]
    assert list(pa.factor("B", a, 2024)) == [0.25, 0.5, 1]
    assert list(pa.factor("C", a, 2024)) == [0, 0, 1]
    assert list(pa.factor("B", np.array([2022, 2023]), 2023)) == [0.5, 1]          # «último» es el de la pregunta


def test_la_escala_va_de_0_a_100():
    assert pa.a_100(1, [1, 2, 3, 4, 5]) == 0 and pa.a_100(5, [1, 2, 3, 4, 5]) == 100 and pa.a_100(3, [1, 2, 3, 4, 5]) == 50


def test_pesar_el_ultimo_anio_acerca_a_su_valor_y_no_cambia_el_peso_de_la_localidad():
    # localidad 1: 2023 responde 1 y 2024 responde 5; localidad 2: todos 3, con más peso
    x = np.array([1, 1, 5, 5, 3, 3, 3, 3.])
    anio = np.array([2023, 2023, 2024, 2024, 2023, 2023, 2024, 2024])
    loc = np.array([1, 1, 1, 1, 2, 2, 2, 2])
    peso = np.array([1, 1, 1, 1, 2, 2, 2, 2.])
    ca, la = pa.medias(x, peso, loc, anio, [1, 2, 3, 4, 5], "A", 2024)
    cc, lc = pa.medias(x, peso, loc, anio, [1, 2, 3, 4, 5], "C", 2024)
    assert la[1] == 50 and lc[1] == 100 and la[2] == lc[2] == 50
    assert abs(ca - 50) < 1e-9 and abs(cc - (4 * 100 + 8 * 50) / 12) < 1e-9          # la localidad 2 sigue pesando 8 de 12


def test_no_sabe_no_entra():
    x = np.array([1, 5, 99.])
    c, _ = pa.medias(x, np.ones(3), np.ones(3), np.array([2024] * 3), [1, 2, 3, 4, 5], "A", 2024)
    assert c == 50


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Peso por año reciente — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
