"""
tests/test_validacion_cnc_2026.py

Pruebas de src/experiments/validacion_cnc_2026.py (`VALIDACION_CNC_2026_SPECIFICATION.md`). No llaman a la API ni leen
las encuestas del CNC.
Se ejecuta directo:  python tests/test_validacion_cnc_2026.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.experiments import validacion_cnc_2026 as vk

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_el_porcentaje_sin_no_sabe_y_con_el_3_como_no():
    x = pd.Series([1, 2, 3, 4, 5, 9]); w = pd.Series([1.0] * 6)
    assert vk.porcentaje(x, w, [1, 2, 3, 4, 5], [4, 5]) == (40.0, 5)
    assert vk.porcentaje(pd.Series([1, 2, 9]), pd.Series([3.0, 1.0, 5.0]), [1, 2], [1]) == (75.0, 2)


def test_lo_publicable_no_trae_el_real():
    f = {"id": "K1", "pregunta": "x", "alcance": "nueva", "porcentaje": 40.0, "rango": [18.0, 62.0], "llamada": "dividida",
         "real": 55.0}
    p = vk.publicable(f)
    assert "real" not in p and p["dentro_del_rango"] and "llamada_acierta" not in p
    assert vk.publicable({**f, "llamada": "no"})["llamada_acierta"] is False


def test_la_regla_pide_5_de_7():
    filas = [{"id": f"K{i}", "real": 60.0, "alcance": "nueva", "porcentaje": 55.0, "rango": ([30, 80] if i <= 4 else [70, 90]),
              "llamada": "dividida"} for i in range(1, 8)]
    assert vk.evaluar(filas)["criterios"]["R1"] == {"umbral": "dentro del rango en ≥ 5 de 7", "valor": 4, "se_cumple": False}


def test_las_preguntas_son_las_del_documento():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "VALIDACION_CNC_2026_SPECIFICATION.md").read_text(encoding="utf-8")
    for i, est, var, texto, *_ in vk.PREGUNTAS:
        assert f"| {i} | {texto} | {est} {var}," in doc, i
    assert vk.TOPE_USD == 0.15 and "tope de USD 0,15" in doc


if __name__ == "__main__":
    pruebas = [x for k, x in list(globals().items()) if k.startswith("test_")]
    print(f"Validación CNC 2026 — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
