"""
tests/test_grupos_y_galan_2026.py

Pruebas de src/experiments/grupos_y_galan_2026.py (`GRUPOS_Y_GALAN_2026_SPECIFICATION.md`). No llaman a la API ni leen datos.
Se ejecuta directo:  python tests/test_grupos_y_galan_2026.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.experiments import grupos_y_galan_2026 as gg

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_los_grupos_gruesos():
    d = pd.DataFrame({"DMO_1": [1, 2], "DMO_4_1": [2, 5], "DMO_3_1": [20, 60]})
    g = gg.grupos_agentes(d)
    assert list(g["sexo"]) == ["Hombres", "Mujeres"] and list(g["estrato"]) == ["1-2", "4-6"] and list(g["edad"]) == ["joven", "mayor"]


def test_parte_de_cepeda_y_medida():
    assert gg.parte_cepeda(30, 10) == 75.0 and gg.parte_cepeda(0, 0) is None
    ag = {"sexo": {"Hombres": 50, "Mujeres": 60}, "estrato": {"1-2": 70, "3": 55, "4-6": 30}, "edad": {"joven": 70, "media": 55, "mayor": 40}}
    cnc = {"sexo": {"Hombres": 48, "Mujeres": 62}, "estrato": {"1-2": 72, "3": 50, "4-6": 35}, "edad": {"joven": 60, "media": 52, "mayor": 45}}
    m = gg.medir_grupos(ag, cnc, 55.0)
    assert m["grupos"] == 8 and m["signos_correctos"] == 3 and m["error_grupos"] < m["error_ciudad_para_todos"]


def test_el_documento():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "GRUPOS_Y_GALAN_2026_SPECIFICATION.md").read_text(encoding="utf-8")
    for k, t, _, _, real in gg.G:
        assert t in doc and str(real).replace(".", ",") in doc
    assert "tope de USD 1" in doc and gg.TOPE_USD == 1.0


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Grupos y Galán 2026 — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
