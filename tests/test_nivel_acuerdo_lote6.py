"""
tests/test_nivel_acuerdo_lote6.py

Pruebas de src/experiments/nivel_acuerdo_lote6.py: ninguna llama a la API.
Las que necesitan los resultados del lote 6 se saltan si no están en este computador.
Se ejecuta directo:  python tests/test_nivel_acuerdo_lote6.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import banco_lote6 as b6
from src.experiments import nivel_acuerdo_lote6 as n6

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_c_son_las_109_mas_las_30_de_practica_del_lote_6():
    if not b6.REALES.exists():
        print("         (sin los resultados del lote 6: se salta)")
        return
    b, c = n6.candidatas()
    assert len(b) == 109 and len(c) == 139 and set(b.id) <= set(c.id)
    nuevas = c[~c.id.isin(b.id)]
    assert len(nuevas) == 30 and nuevas.id.str.startswith(("CC355801", "CC871401", "CC871801", "CC873501")).all()


def test_ni_candidatas_ni_objetivos_traen_lo_electoral():
    if not (b6.REALES.exists() and n6.REALES_G6.exists()):
        print("         (sin los resultados del lote 6: se salta)")
        return
    from src.experiments import banco_lote7 as b7
    _, c = n6.candidatas()
    o95, o6 = n6.objetivos()
    ids7 = set(__import__("pandas").read_csv(b7.SORTEO).id)
    assert not (set(c.id) | set(o95.id) | set(o6.id)) & ids7
    assert not set(o6.familia) & set(c.familia)


def test_la_regla_pide_las_tres_condiciones():
    rb = {"eam": 14.0}
    assert n6.regla(rb, {"pasa": True, "eam": 13.9, "acierto_al_decidir": 0.95, "decide": 0.2})["c_reemplaza_a_b"]
    assert not n6.regla(rb, {"pasa": True, "eam": 14.1, "acierto_al_decidir": 0.95, "decide": 0.2})["c_reemplaza_a_b"]
    assert not n6.regla(rb, {"pasa": False, "eam": 13, "acierto_al_decidir": 0.95, "decide": 0.2})["c_reemplaza_a_b"]
    assert not n6.regla(rb, {"pasa": True, "eam": 13, "acierto_al_decidir": 0.85, "decide": 0.2})["c_reemplaza_a_b"]


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Estimación con el lote 6 — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
