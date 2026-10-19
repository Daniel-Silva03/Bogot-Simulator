"""
tests/test_intervalos_fase1.py

Pruebas de src/evaluacion/intervalos_fase1.py (`INTERVALOS_FASE1_SPECIFICATION.md`). No leen la EPC.
Se ejecuta directo:  python tests/test_intervalos_fase1.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.evaluacion import intervalos_fase1 as iv

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def _t():
    filas = []
    for anio in range(2014, 2020):
        for k in range(4):
            filas.append({"serie": f"S{k}", "dominio": iv.GOB if k < 2 else "lo demás", "anio_base": anio - 1, "anio": anio,
                          "base": 50.0, "real": 50.0 + (anio - 2010) * (1 if k % 2 else -1), "salto": False, "cambio": anio == 2016})
    t = pd.DataFrame(filas)
    t["error"] = (t.real - t.base).abs()
    return t


def test_el_rango_solo_usa_anios_anteriores():
    t = iv.anchos(_t())
    # 2014 tiene 0 previos y 2015 tiene 4: no entran; 2016 usa solo los errores de 2014 y 2015
    assert t[t.anio <= 2015].R1.isna().all()
    prev = _t()[_t().anio < 2016].error
    assert abs(t[t.anio == 2016].R1.iloc[0] - np.quantile(prev, 0.8)) < 1e-9


def test_r3_ensancha_con_cambio_de_gobierno_o_pocos_casos():
    t = iv.anchos(_t())
    f = t[(t.anio == 2016)].iloc[0]
    assert abs(f.R3 - 1.5 * f.R2) < 1e-9


def test_los_gobiernos():
    assert [iv.gobierno(a) for a in (2015, 2016, 2019, 2022, 2023, 2024)] == ["Petro", "Peñalosa", "Peñalosa", "López", "López",
                                                                                "Galán"]


def test_la_regla_de_decision():
    cob = {"R1": {"total": 0.80, "gobierno": 0.60, "ancho_medio": 10}, "R2": {"total": 0.78, "gobierno": 0.72, "ancho_medio": 14},
           "R3": {"total": 0.90, "gobierno": 0.85, "ancho_medio": 20}}
    assert iv.decidir(cob) == ("R2", True)
    cob["R2"]["gobierno"] = 0.5
    cob["R3"]["gobierno"] = 0.6
    assert iv.decidir(cob) == ("R1", False) or iv.decidir(cob) == ("R3", False)


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Intervalos Fase 1 — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
