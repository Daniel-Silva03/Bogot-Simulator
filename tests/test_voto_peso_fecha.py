"""
tests/test_voto_peso_fecha.py

Pruebas de src/experiments/voto_peso_fecha.py (`VOTO_PESO_FECHA_SPECIFICATION.md`). Solo las funciones puras: no
leen datos del CNC ni llaman a la API.
Se ejecuta directo:  python tests/test_voto_peso_fecha.py
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.experiments import voto_peso_fecha as pf

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


# enero, abril y mayo de 2026 (DI-VR1)
IDS = ["CC891901_P12_1", "CC893401_P5_1", "CC893701_P5_1"]
TOT = {"CC891901_P12_1": 60.0, "CC893401_P5_1": 50.0, "CC893701_P5_1": 40.0}
MAYO = pd.Timestamp("2026-05-31")


def test_con_tau_infinita_es_el_promedio_del_nivel_3():
    assert pf.combinar(IDS, TOT, MAYO, math.inf) == 50.0


def test_con_tau_cero_toma_solo_la_mas_cercana():
    assert pf.combinar(IDS, TOT, MAYO, 0) == 40.0
    assert pf.combinar(IDS, TOT, pd.Timestamp("2026-01-18"), 0) == 60.0          # la distancia es en los dos sentidos


def test_el_peso_baja_con_la_distancia_y_no_depende_del_dia_de_hoy():
    a = pf.combinar(IDS, TOT, MAYO, 60)
    assert 40 < a < 50
    assert abs(a - pf.combinar(IDS, TOT, pd.Timestamp("2026-10-08"), 60)) < 1e-9     # DI-PF2: todas antes
    assert pf.combinar(IDS, TOT, MAYO, 30) < a < pf.combinar(IDS, TOT, MAYO, 480)


def test_la_tau_se_elige_por_la_practica_y_el_empate_va_a_la_mas_grande():
    assert pf.elegir_tau({0: 5.0, 60: 4.0, math.inf: 4.5}) == 60
    assert pf.elegir_tau({0: 5.0, 60: 4.0, math.inf: 4.04}) == math.inf


def test_la_regla():
    base = {"eam": 3.7, "adelante": 30 / 32, "segundas": 32, "dice_probable": 10, "acierta_probable": 1.0}
    mejor = {**base, "eam": 3.3}
    assert pf.regla(mejor, base, 60)["cumple"]
    assert not pf.regla(mejor, base, math.inf)["R1"]
    assert not pf.regla({**base, "eam": 3.5}, base, 60)["R2"]
    assert not pf.regla({**mejor, "adelante": 29 / 32}, base, 60)["R3"]
    assert not pf.regla({**mejor, "acierta_probable": 0.8}, base, 60)["R4"]
    assert pf.regla({**mejor, "dice_probable": 4, "acierta_probable": 0.5}, base, 60)["R4"]


def test_la_rejilla_es_la_del_documento():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "VOTO_PESO_FECHA_SPECIFICATION.md").read_text(encoding="utf-8")
    assert pf.TAUS == [0, 15, 30, 60, 120, 240, 480, math.inf]
    assert "0, 15, 30, 60, 120, 240 y 480 días" in doc and "0,3 puntos" in doc and "0,05 puntos" in doc


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Peso por fecha — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
