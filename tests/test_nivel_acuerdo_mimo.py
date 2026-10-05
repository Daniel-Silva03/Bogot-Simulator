"""
tests/test_nivel_acuerdo_mimo.py

Pruebas de src/experiments/nivel_acuerdo_mimo.py: ninguna llama a la API.
Se ejecuta directo:  python tests/test_nivel_acuerdo_mimo.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import experimento9 as e9
from src.experiments import nivel_acuerdo_mimo as nm
from src.experiments import nivel_acuerdo_validacion as nv

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def _r(eam, lado, si, asi, no, ano, pasa=None):
    return {"eam": eam, "lado": lado, "dice_si": si, "acierta_si": asi, "dice_no": no, "acierta_no": ano, "pasa": pasa}


def test_es_el_modelo_de_la_pagina_y_no_toca_los_valores_de_sonnet():
    assert nm.MODELO == e9.MODELO == "xiaomi/mimo-v2.6-pro"
    assert nv.MODELO == "anthropic/claude-sonnet-5.5" and nv.H == 21.9


def test_la_regla_pide_las_tres_condiciones():
    ok = nm.regla(_r(13, 0.8, 5, 5, 3, 3), _r(12, 0.78, 4, 4, 2, 2, pasa=True))
    assert ok["cumple"] and ok["decisiones"] == 14
    assert not nm.regla(_r(16, 0.8, 5, 5, 3, 3), _r(12, 0.78, 4, 4, 2, 2, pasa=True))["cumple"]   # práctica
    assert not nm.regla(_r(13, 0.8, 5, 5, 3, 3), _r(12, 0.78, 4, 4, 2, 2, pasa=False))["cumple"]  # guardado
    assert not nm.regla(_r(13, 0.8, 5, 3, 3, 3), _r(12, 0.78, 4, 3, 2, 2, pasa=True))["cumple"]   # al decidir: 11/14
    assert not nm.regla(_r(13, 0.8, 0, 0, 0, 0), _r(12, 0.78, 0, 0, 0, 0, pasa=True))["cumple"]   # sin decisiones


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Nivel de acuerdo con mimo — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
