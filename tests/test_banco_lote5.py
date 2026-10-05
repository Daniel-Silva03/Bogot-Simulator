"""
tests/test_banco_lote5.py

Pruebas de src/experiments/banco_lote5.py. Las de la lista usan nombres de columnas; la última solo revisa
la estructura de la base real si está en esta máquina (no calcula porcentajes).
Se ejecuta directo:  python tests/test_banco_lote5.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import banco_lote3 as b3
from src.experiments import banco_lote5 as b5

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_la_lista_toma_solo_los_bloques_y_saca_las_que_repiten_el_catalogo():
    cols = ["Ax104", "Bx104", "Ax602", "Bx602", "Hx704", "Gx704", "Ax102", "Kx103", "Ax401", "fexp_calp_anu"]
    assert b5.variables(cols) == ["Ax104", "Bx104", "Bx602", "Gx704"]


def test_son_38_en_8_familias_y_el_sorteo_reparte_4_y_4():
    if not b5.BASE.exists():
        print("         (sin la base de la EDP en esta máquina)")
        return
    t = b5.tabla()
    assert len(t) == 38 and t.familia.nunique() == 8 and t.id.is_unique
    assert all(q.startswith("¿Está de acuerdo con que «") for q in t.pregunta_pagina)
    s = b3.sortear(t, b5.SEMILLA)
    assert s.groupby("conjunto").familia.nunique().to_dict() == {"guardado": 4, "practica": 4}


def test_la_base_no_trae_columnas_personales():
    if not b5.BASE.exists():
        return
    import pandas as pd
    cols = [c.lower() for c in pd.read_csv(b5.BASE, nrows=0).columns]
    for s in ("documento", "nombre", "direccion", "telefono", "latitud", "longitud", "nacimiento", "correo"):
        assert not any(s in c for c in cols), s


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Banco, lote 5 — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
