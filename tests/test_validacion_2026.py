"""
tests/test_validacion_2026.py

Pruebas de src/experiments/validacion_2026.py (`VALIDACION_2026_SPECIFICATION.md`). No llaman a la API.
Se ejecuta directo:  python tests/test_validacion_2026.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import validacion_2026 as v

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def _f(i, real, **kw):
    return {"id": i, "real": real, "alcance": "nueva", **kw}


def test_la_regla_del_preregistro():
    buenas = [_f(f"V{i}", r, porcentaje=r - 5, rango=[r - 25, min(100, r + 20)], llamada="sí" if r > 50 else "no")
              for i, r in zip(range(1, 7), (93, 70, 80, 88, 56, 26))]
    ev = v.evaluar(buenas)
    assert ev["pasa"] and ev["eam_50"] == 26.8 and ev["eam"] == 5.0
    fuera = buenas[:5] + [{"id": "V6", "real": 26, "alcance": "fuera"}]
    assert v.evaluar(fuera)["criterios"]["R2"]["valor"] == [5, 6]                         # «fuera» es una llamada fallida
    malas = [{**f, "llamada": "no" if f["real"] > 50 else "sí"} for f in buenas]
    assert not v.evaluar(malas)["criterios"]["R2"]["se_cumple"]


def test_el_catalogo_cuenta_su_error_pero_no_el_rango():
    filas = [_f("V1", 93, porcentaje=60, rango=[38, 82], llamada="dividida"),
             {"id": "V2", "real": 70, "alcance": "catalogo", "porcentaje": 65.0}]
    ev = v.evaluar(filas)
    assert ev["criterios"]["R1"]["valor"] == 0 and ev["criterios"]["R2"]["valor"] == [0, 0] and ev["eam"] == 19.0


def test_las_preguntas_son_las_del_documento():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "VALIDACION_2026_SPECIFICATION.md").read_text(encoding="utf-8")
    for i, texto, real in v.PREGUNTAS:
        assert f"| {i} | {texto} |" in doc, i
    assert v.TOPE_USD == 0.20 and "tope de USD 0,20" in doc and "26,8" in doc


if __name__ == "__main__":
    pruebas = [x for k, x in list(globals().items()) if k.startswith("test_")]
    print(f"Validación 2026 — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
