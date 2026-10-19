"""
tests/test_actualidad_epc.py

Pruebas de src/experiments/actualidad_epc.py (`ACTUALIDAD_EPC_SPECIFICATION.md`). No llaman a la API ni leen la EPC.
Se ejecuta directo:  python tests/test_actualidad_epc.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import actualidad_epc as ae

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def _doc():
    return " ".join((Path(__file__).resolve().parents[1] / "docs" / "ACTUALIDAD_EPC_SPECIFICATION.md").read_text(encoding="utf-8")
                    .replace("> ", "").split())


def test_la_nota_y_el_resumen_son_los_del_preregistro():
    doc = _doc()
    assert " ".join(ae.NOTA.split()) in doc
    for linea in ae.RESUMEN_2025.splitlines():
        assert " ".join(linea.split()) in doc, linea[:40]


def test_el_resumen_no_trae_encuestas_ni_opiniones():
    t = ae.RESUMEN_2025.lower()
    for palabra in ("encuesta", "%", "aprueba", "percep", "opinión", "imagen", "la gente piensa"):
        assert palabra not in t, palabra


def test_deciden_cinco_y_dos_ya_vistas_no():
    assert [i for i, _, _, d in ae.PREGUNTAS if d] == ["A1", "A2", "A3", "A4", "A5"]
    assert {v for _, v, _, d in ae.PREGUNTAS if not d} == {"GG3_GALAN", "AG1"}


def test_la_regla():
    ids = ["A1", "A2", "A3", "A4", "A5"]
    r24 = dict(zip(ids, [40, 30, 30, 30, 30]))
    r25 = dict(zip(ids, [50, 25, 25, 25, 25]))
    b = dict(zip(ids, [48, 26, 26, 26, 26]))
    a = dict(zip(ids, [41, 30, 30, 30, 30]))
    v = ae.evaluar(a, b, r24, r25, ids)
    assert v["pasa"] and v["criterios"]["RA3"]["valor"] == 5 and v["predicciones"]["PA3"]
    assert not ae.evaluar(a, r24, r24, r25, ids)["pasa"]                       # repetir 2024 no le gana a sí mismo


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Actualidad EPC — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
