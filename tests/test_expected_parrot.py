"""
tests/test_expected_parrot.py

Pruebas de src/evaluacion/expected_parrot.py (`EXPECTED_PARROT_SPECIFICATION.md`). No llaman a la API ni necesitan EDSL.
Se ejecuta directo:  python tests/test_expected_parrot.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.evaluacion import expected_parrot as ep

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_la_cifra_es_ponderada_y_sin_invalidas():
    r = ["Buena gestión", "Mala gestión", None, "Muy buena gestión", "otra cosa"]
    assert ep.cifra(r, [1, 3, 5, 1, 9]) == 40.0


def test_la_lectura():
    d = {"paneles": {"2025": [{"peso": 1}] * 4, "2024": [{"peso": 1}] * 4}}
    res = {"A_luna_2025": {"panel": 2025, "modelo": "m", "respuestas": ["Buena gestión", "Mala gestión", "Mala gestión",
                                                                       "Regular gestión"], "costo_usd": 0},
           "B_luna_2024": {"panel": 2024, "modelo": "m", "respuestas": ["Buena gestión"] + ["Mala gestión"] * 3, "costo_usd": 0},
           "B_sonnet_2024": {"panel": 2024, "modelo": "m", "respuestas": ["Buena gestión"] * 4, "costo_usd": 0}}
    out = ep.leer(res, d)
    assert out["corridas"]["A_luna_2025"]["cifra"] == 25.0 and out["lectura"]["RA_equivalente"]
    assert out["corridas"]["B_luna_2024"]["ve_la_caida"] and not out["corridas"]["B_sonnet_2024"]["ve_la_caida"]
    assert out["lectura"]["RB_ven_la_caida"] == 1 and out["lectura"]["RC_modelo_fuerte_mejor_que_luna"] == []


def test_el_umbral_es_el_punto_medio():
    assert round(ep.UMBRAL_CAIDA, 2) == 34.35


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Expected Parrot — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
