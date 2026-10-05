"""
tests/test_banco_lote2.py

Pruebas de src/experiments/banco_lote2.py. Las del sorteo y el cálculo usan datos inventados; la
última solo revisa los encabezados del archivo real si está en esta máquina (no calcula porcentajes).
Se ejecuta directo:  python tests/test_banco_lote2.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.experiments import banco_lote2 as bl

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_son_las_16_preguntas_en_7_familias_de_11():
    t = bl.tabla()
    assert len(t) == 16 and t.familia.nunique() == 7 and t.id.is_unique
    assert set(t.ambito) == {"Bogotá"} and t.independiente.all()


def test_el_sorteo_es_por_familia_4_y_3_y_reproducible():
    t = bl.tabla()
    a, b = bl.sortear(t), bl.sortear(t)
    assert a.equals(b)
    fam = a.groupby("familia").conjunto.nunique()
    assert (fam == 1).all()                                                   # una familia no se parte
    n = a.groupby("conjunto").familia.nunique().to_dict()
    assert n == {"guardado": 4, "practica": 3}, n


def test_el_calculo_solo_toca_las_de_practica_y_solo_adultos():
    rng = np.random.default_rng(0)
    n = 600
    d = pd.DataFrame({i: np.full(n, np.nan) for i in range(117)})
    d[5] = rng.integers(1, 20, n)
    d[6] = rng.integers(1, 7, n)
    d[7] = rng.integers(1, 3, n)
    d[10] = np.where(np.arange(n) < 50, np.nan, rng.integers(18, 80, n))      # 50 menores, sin edad de adulto
    d[114] = 1.0
    for _, _, c, *_ in bl.PREGUNTAS:
        d[c] = rng.choice([1, 2, 99], n)
    s = bl.sortear(bl.tabla())
    r = bl.reales(s, d)
    assert set(r) == set(s[s.conjunto == "practica"].id)
    assert all(v["n"] <= n - 50 for v in r.values())
    assert all(set(v["grupos"]) == {"sexo", "edad", "estrato"} for v in r.values())


def test_los_encabezados_del_archivo_real_son_los_esperados():
    if not bl.ARCHIVO.exists():
        print("         (sin el archivo de la ECA en esta máquina)")
        return
    d = bl.cargar()                                                           # se detiene si alguna columna no cuadra
    assert len(d) > 2000


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Banco, lote 2 — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
