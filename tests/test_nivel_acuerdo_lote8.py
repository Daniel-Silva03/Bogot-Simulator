"""
tests/test_nivel_acuerdo_lote8.py

Pruebas de src/experiments/nivel_acuerdo_lote8.py (`NIVEL_ACUERDO_LOTE8_SPECIFICATION.md`). No llaman a la API.
Se ejecuta directo:  python tests/test_nivel_acuerdo_lote8.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import nivel_acuerdo_lote8 as n8

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_la_regla_del_preregistro():
    base = {"pasa": True, "eam": 14.8, "decide": 0.1, "acierto_al_decidir": 0.9}
    assert n8.regla(base, {**base, "eam": 14.5})["d_reemplaza_a_c"]
    assert not n8.regla(base, {**base, "eam": 14.9})["d_reemplaza_a_c"]                # estima peor
    assert not n8.regla(base, {**base, "acierto_al_decidir": 0.8})["d_reemplaza_a_c"]
    assert not n8.regla(base, {**base, "decide": 0})["d_reemplaza_a_c"]                 # no decide nunca
    assert not n8.regla(base, {**base, "pasa": False})["d_reemplaza_a_c"]


def test_d_son_las_de_c_mas_la_practica_del_lote_8_sin_familias_guardadas():
    """Necesita los resultados del banco en esta máquina."""
    try:
        c, d = n8.candidatas()
    except FileNotFoundError:
        print("         (sin los resultados del banco en esta máquina: se omite)")
        return
    nuevas = d[~d.id.isin(c.id)]
    assert len(c) == 139 and len(nuevas) == 15 and nuevas.id.str.startswith("EPC25_").all()
    import pandas as pd
    s = pd.read_csv(n8.b8.SORTEO)
    guardadas = set(s[s.conjunto == "guardado"].familia)
    assert not guardadas & set(d.familia)


def test_el_tope_y_el_documento():
    assert n8.TOPE_USD == 0.60 and n8.H == 23.4
    doc = (Path(__file__).resolve().parents[1] / "docs" / "NIVEL_ACUERDO_LOTE8_SPECIFICATION.md").read_text(encoding="utf-8")
    assert "tope de USD 0,60" in doc and "±23,4" in doc


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Nivel de acuerdo, lote 8 — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
