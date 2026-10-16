"""
tests/test_voto_agentes.py

Pruebas de src/experiments/voto_agentes.py (`VOTO_AGENTES_SPECIFICATION.md`). No llaman a la API ni leen datos.
Se ejecuta directo:  python tests/test_voto_agentes.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.experiments import voto_agentes as va

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_las_opciones_por_apellido_y_sin_partido():
    r = pd.Series({"IVÁN CEPEDA CASTRO": 5, "ABELARDO DE LA ESPRIELLA": 4, "CLAUDIA LÓPEZ": 1})
    ops = va.opciones(r)
    assert ops == ["Iván Cepeda Castro", "Abelardo de la Espriella", "Claudia López", "Votaría en blanco", "No votaría"]


def test_normalizar_y_medir():
    real = va.normalizar({"A": 60.0, "B": 30.0, "C": 10.0}, ["A", "B", "C"])
    assert abs(real["A"] - 60) < 1e-9
    m = va.medir({"A": 50.0, "B": 40.0, "C": 10.0}, real)
    assert m["eam"] == round(20 / 3, 2) and m["primero"] and m["dos_primeros"]
    assert not va.medir({"A": 30.0, "B": 60.0, "C": 10.0}, real)["primero"]


def test_el_documento():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "VOTO_AGENTES_SPECIFICATION.md").read_text(encoding="utf-8")
    assert va.PREGUNTA in doc and "5,4" in doc and "tope de USD 2" in doc and va.TOPE_USD == 2.0
    ctx = (Path(__file__).resolve().parents[1] / "docs" / "PROJECT_CONTEXT.md").read_text(encoding="utf-8")
    assert "### D23" in ctx


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Voto con agentes — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
