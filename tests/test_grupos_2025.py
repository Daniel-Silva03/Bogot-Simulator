"""
tests/test_grupos_2025.py

Pruebas de src/experiments/grupos_2025.py (`GRUPOS_2025_SPECIFICATION.md`). No leen la EPC.
Se ejecuta directo:  python tests/test_grupos_2025.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.experiments import grupos_2025 as gr

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_los_grupos_de_2025_usan_los_cortes_de_la_pagina():
    d = pd.DataFrame({"DMO_1": [1, 2, 2], "DMO_3_1": [20, 40, 70], "DMO_4_1": [1, 4, 6]})
    g = gr.grupos_2025(None, d)
    assert list(g["sexo"]) == ["Hombres", "Mujeres", "Mujeres"]
    assert list(g["estrato"]) == ["1 y 2", "3 y 4", "5 y 6"] and list(g["edad"]) == ["18 a 25", "36 a 45", "56 o más"]


def test_medias_por_grupo_sin_no_sabe():
    m = gr.medias(np.array([1, 5, 9, 3.0]), np.ones(4), np.array(["a", "a", "a", "b"]), [1, 2, 3, 4, 5], ["a", "b"])
    assert m == {"a": 50.0, "b": 50.0}


def test_resumen_compara_con_la_ciudad():
    t = pd.DataFrame({"pagina": [40.0, 60.0], "real": [42.0, 58.0], "pagina_ciudad": [50.0, 50.0], "real_ciudad": [50.0, 50.0]})
    r = gr.resumir(t)
    assert r["E_grupo"] == 2.0 and r["E_ciudad"] == 8.0 and r["correlacion_brechas"] == 1.0


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Grupos 2025 — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
