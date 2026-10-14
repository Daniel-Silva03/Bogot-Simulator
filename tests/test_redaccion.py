"""
tests/test_redaccion.py

Pruebas de src/experiments/redaccion.py (`REDACCION_SPECIFICATION.md`). No llaman a la API.
Se ejecuta directo:  python tests/test_redaccion.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import redaccion as rd

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def _res(nuevas, cat_ok=True):
    out = {}
    for i, cod, _ in rd.PREGUNTAS:
        if cod:
            out[i] = [{"alcance": "catalogo", "codigo": cod if cat_ok else "OTRO"}] * 3
        else:
            out[i] = [{"alcance": "nueva", "porcentaje": p, "llamada": ll} for p, ll in nuevas]
    return out


def test_el_efecto_es_la_media_de_b_y_c_contra_a():
    ev = rd.evaluar(_res([(40, "dividida"), (44, "dividida"), (36, "dividida")]))
    assert ev["efecto"] == 4.0 and ev["robusta"] and ev["amplitudes"]["N1"] == 8
    assert ev["criterios"]["R1"]["valor"] == 12


def test_voltear_si_no_y_el_catalogo_inestable_fallan():
    ev = rd.evaluar(_res([(80, "sí"), (20, "no"), (50, "dividida")]))
    assert not ev["criterios"]["R3"]["se_cumple"] and not ev["criterios"]["R2"]["se_cumple"]
    assert not rd.evaluar(_res([(40, "dividida")] * 3, cat_ok=False))["criterios"]["R1"]["se_cumple"]


def test_las_redacciones_son_las_del_documento():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "REDACCION_SPECIFICATION.md").read_text(encoding="utf-8")
    for i, cod, textos in rd.PREGUNTAS:
        for t in textos:
            assert t in doc, (i, t)
        assert cod is None or f"`{cod}`" in doc
    assert rd.TOPE_USD == 0.25 and "tope de USD\n0,25" in doc or "tope de USD 0,25" in doc


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Redacción — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
