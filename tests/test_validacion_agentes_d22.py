"""
tests/test_validacion_agentes_d22.py

Pruebas de src/experiments/validacion_agentes_d22.py (`VALIDACION_AGENTES_D22_SPECIFICATION.md`). No llaman a la API ni
leen datos del CNC.
Se ejecuta directo:  python tests/test_validacion_agentes_d22.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import validacion_agentes_d22 as va

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_las_nueve_son_las_del_preregistro():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "VALIDACION_AGENTES_D22_SPECIFICATION.md").read_text(encoding="utf-8")
    assert len(va.PREGUNTAS) == 9
    for i, est, var, fecha, preg, ops in va.PREGUNTAS:
        assert f"| {i} | {est} | {var} | {fecha}:" in doc, i
    assert va.PETRO in doc and va.HABLO in doc


def test_la_regla():
    ids = [i for i, *_ in va.PREGUNTAS]
    real = dict(zip(ids, [35, 36, 37, 38, 39, 40, 41, 42, 43]))
    bien = va.evaluar({i: real[i] + 3 for i in ids}, real)
    assert bien["pasa"] and bien["error_medio"] == 3
    mal = va.evaluar({i: 70 for i in ids}, real)
    assert not mal["criterios"]["RV1"]["se_cumple"] and mal["criterios"]["RV3"]["valor"] == 0
    assert bien["predicciones"]["PV2"] and not mal["predicciones"]["PV3"]


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Validación D22 — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
