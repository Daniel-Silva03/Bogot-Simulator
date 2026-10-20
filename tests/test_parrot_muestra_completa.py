"""
tests/test_parrot_muestra_completa.py

Pruebas de src/evaluacion/parrot_muestra_completa.py (`PARROT_MUESTRA_COMPLETA_SPECIFICATION.md`). No llaman a la API ni necesitan
EDSL. Se ejecuta directo:  python tests/test_parrot_muestra_completa.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.evaluacion import parrot_muestra_completa as pm

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def _res(fav: dict[str, int]) -> tuple[dict, dict]:
    """10 agentes por año; `fav` dice cuántos eligen «Buena gestión»."""
    d = {"paneles": {str(a): [{"peso": 1.0}] * 10 for a in (2022, 2023, 2024, 2025)}}
    res = {}
    for nombre, base, obj, modelo in pm.CORRIDAS:
        k = fav[nombre]
        res[nombre] = {"base": base, "objetivo": obj, "modelo": modelo, "completa": True, "costo_usd": 0,
                       "respuestas": ["Buena gestión"] * k + ["Mala gestión"] * (10 - k)}
    return res, d


def test_solo_luna_y_cuatro_corridas():
    assert [c[0] for c in pm.CORRIDAS] == ["T0_luna", "T1_luna", "T2_luna", "F_luna"]
    assert all(c[3] == pm.LUNA for c in pm.CORRIDAS)


def test_si_repiten_el_dato_no_se_reproduce():
    res, d = _res({"T0_luna": 3, "T1_luna": 3, "T2_luna": 4, "F_luna": 3})
    out = pm.leer(res, d)
    assert out["corridas"]["T2_luna"]["cifra"] == 40.0 and not out["lectura"]["se_reproduce"]
    assert out["lectura"]["predicciones"] == {"PM1": True, "PM2": True}
    assert "error" not in out["corridas"]["F_luna"]


def test_si_aciertan_se_reproduce():
    res, d = _res({"T0_luna": 3, "T1_luna": 4, "T2_luna": 3, "F_luna": 3})
    out = pm.leer(res, d)
    assert out["lectura"]["se_reproduce"] and out["lectura"]["RT3_sentido_correcto"] == 3


def test_la_nota_lleva_los_anios():
    assert pm.nota(2024, 2025).startswith("Lo que sabes de esta persona es de 2024. Esta pregunta es de finales de 2025")


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Parrot con toda la muestra — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
