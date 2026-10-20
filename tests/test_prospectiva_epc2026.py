"""
tests/test_prospectiva_epc2026.py

Pruebas de src/evaluacion/prospectiva_epc2026.py y alcalde_sin_nombre.py (plan v5, pasos 2 y 3). No llaman a la API.
Se ejecuta directo:  python tests/test_prospectiva_epc2026.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.evaluacion import alcalde_sin_nombre as sn
from src.evaluacion import prospectiva_epc2026 as pr

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def _t(g_alcalde, g_resto):
    filas = [{"variable": v, "P": 40.0, "G": g_alcalde if v == pr.ALCALDE else g_resto, "real": 30.0} for v in pr.VARIABLES]
    return pd.DataFrame(filas)


def test_victoria_solo_si_gana_sin_el_alcalde():
    r = pr.evaluar(_t(30.0, 32.0))
    assert r["reglas"]["victoria"] and r["informe"] is None


def test_si_gana_solo_el_alcalde_se_dice_con_la_frase():
    r = pr.evaluar(_t(30.0, 40.0))
    assert not r["reglas"]["victoria"] and r["informe"] == pr.FRASE_SOLO_ALCALDE
    assert r["gana_por_pregunta"][pr.ALCALDE] == "G" and r["ganadas"]["empate"] == 6


def test_la_condicion_b_solo_quita_el_nombre():
    from src.consulta import motor as mo
    a = mo.GALAN_SOLO_AGENTES["GG3_GALAN"]
    assert sn.TEXTO_B == a.replace(", Carlos Fernando Galán", "")


def test_las_medidas_del_diagnostico():
    a = np.array([0.9, 0.8, 0.1, 0.2]); b = np.array([0.5, 0.5, 0.4, 0.4])
    r = sn.medir(a, b, np.array([5, 4, 1, 2]), np.ones(4))
    assert r["A"] == 50.0 and r["B"] == 45.0 and r["panel_2025"] == 50.0
    assert r["seguimiento_A"]["diferencia"] == 70.0 and r["lectura"]["siguen_su_respuesta"]["A"] == "la siguen"
    assert r["lectura"]["siguen_su_respuesta"]["B"] == "la siguen poco" and r["lectura"]["el_nombre_mueve"]


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Prospectiva EPC 2026 y alcalde sin nombre — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
