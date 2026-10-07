"""
tests/test_cache_pagina.py

Pruebas de src/experiments/cache_pagina.py: ninguna llama a la API.
Se ejecuta directo:  python tests/test_cache_pagina.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import cache_pagina as cp

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def _r(eam, lado, si, no, acierto):
    return {"eam": eam, "lado": lado, "dice_si": si, "dice_no": no, "acierto_al_decidir": acierto}


def test_la_regla():
    viejo = _r(14.8, 0.71, 7, 4, 0.91)
    assert cp.regla(_r(15.2, 0.67, 6, 4, 0.9), viejo)["cumple"]
    assert not cp.regla(_r(15.4, 0.71, 6, 4, 0.9), viejo)["cumple"]                  # error
    assert not cp.regla(_r(14.0, 0.65, 6, 4, 0.9), viejo)["cumple"]                  # lado
    assert not cp.regla(_r(14.0, 0.71, 6, 4, 0.8), viejo)["cumple"]                  # al decidir
    assert cp.regla(_r(14.0, 0.71, 2, 1, 0.5), viejo)["cumple"]                      # menos de 5: no cuenta


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"La caché en la página — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
