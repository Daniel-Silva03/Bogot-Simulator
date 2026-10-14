"""
tests/test_nivel_acuerdo_catalogo.py

Pruebas de src/experiments/nivel_acuerdo_catalogo.py (`NIVEL_ACUERDO_CATALOGO_SPECIFICATION.md`). No llaman a la API.
Se ejecuta directo:  python tests/test_nivel_acuerdo_catalogo.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import banco_reales as br
from src.experiments import nivel_acuerdo_catalogo as nc

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


FICHA = {"variable": "X1", "pregunta": "¿Qué tan satisfecho está con X?", "escala": [1, 2, 3, 4, 5],
         "etiquetas": {"1": "Muy insatisfecho", "2": "Insatisfecho", "3": "Ni satisfecho ni insatisfecho", "4": "Satisfecho",
                       "5": "Muy satisfecho", "9": "No sabe"}, "nombre": "X"}


def test_una_pregunta_del_catalogo_como_candidata():
    """DI-NC1: sin «no sabe», con su lado y su cifra en porcentaje."""
    f = nc.fila_catalogo(FICHA, 0.4123)
    assert f["id"] == "CAT_X1" == f["familia"] and f["total"] == 41.23
    cats = br.categorias(f["categorias"])
    assert sorted(cats) == [1, 2, 3, 4, 5] and json.loads(f["codigos_favorables"]) == [4, 5]


def test_la_regla_del_preregistro():
    base = {"pasa": True, "eam": 15.6, "decide": 0.08, "acierto_al_decidir": 0.91}
    assert nc.regla(base, {**base, "eam": 15.0})["e_reemplaza_a_c"]
    assert not nc.regla(base, {**base, "eam": 15.7})["e_reemplaza_a_c"]
    assert not nc.regla(base, {**base, "acierto_al_decidir": 0.85})["e_reemplaza_a_c"]


def test_el_tope_y_el_documento():
    assert nc.TOPE_USD == 0.80 and nc.H == 23.4
    doc = (Path(__file__).resolve().parents[1] / "docs" / "NIVEL_ACUERDO_CATALOGO_SPECIFICATION.md").read_text(encoding="utf-8")
    assert "tope de USD\n0,80" in doc or "tope de USD 0,80" in doc
    for i in nc.CERCANAS:
        assert f"`{i}`" in doc


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Nivel de acuerdo con el catálogo — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
