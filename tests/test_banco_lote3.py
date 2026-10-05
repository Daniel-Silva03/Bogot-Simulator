"""
tests/test_banco_lote3.py

Pruebas de src/experiments/banco_lote3.py (lotes 3 y 4 del banco). El sorteo y el cálculo usan datos
inventados; las que leen las copias reducidas reales solo revisan su estructura (no calculan porcentajes).
Se ejecuta directo:  python tests/test_banco_lote3.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.experiments import banco_lote3 as bl

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_el_lote_3_son_190_preguntas_en_52_familias_sin_las_que_repiten_el_catalogo():
    if not bl.BIENAL.exists():
        print("         (sin la copia reducida de la Bienal en esta máquina)")
        return
    t = bl.tabla_bienal()
    assert len(t) == 190 and t.familia.nunique() == 52 and t.id.is_unique
    assert not t.variable.isin(bl.EXCLUIR_SUB).any()
    assert all(json.loads(f) for f in t.codigos_favorables)


def test_la_copia_reducida_no_trae_columnas_sensibles():
    for ruta, hoja in ((bl.BIENAL, "datos"), (bl.BARRIOS, "base")):
        if not ruta.exists():
            continue
        cols = [str(c).lower() for c in pd.read_excel(ruta, sheet_name=hoja, nrows=0).columns]
        for s in ("direccion", "cx", "cy", "manzana", "telef", "nombre", "coordenadas", "_submitted_by"):
            assert not any(c == s or c.startswith(s) for c in cols), (ruta.name, s)


def test_el_sorteo_es_por_familia_y_reproducible():
    t = pd.DataFrame({"id": [f"q{i}" for i in range(12)], "familia": [f"f{i // 3}" for i in range(12)]})
    t = t.assign(**{c: "x" for c in bl.COLUMNAS_SORTEO if c not in t})
    a, b = bl.sortear(t, 1), bl.sortear(t, 1)
    assert a.equals(b) and (a.groupby("familia").conjunto.nunique() == 1).all()
    assert a.groupby("conjunto").familia.nunique().to_dict() == {"guardado": 2, "practica": 2}


def test_barrios_vivos_va_aparte_como_no_representativo():
    t = bl.tabla_barrios()
    assert list(t.id) == ["BV25_P3", "BV25_P6"] and set(t.ambito) == {"Bogotá (no representativa)"}
    s = bl.sortear(t, bl.SEMILLAS[4])
    assert s.conjunto.value_counts().to_dict() == {"guardado": 1, "practica": 1}


def test_el_calculo_solo_toca_practica_adultos_y_filas_con_peso():
    rng = np.random.default_rng(0)
    n = 400
    sorteo = pd.DataFrame([{"id": "a", "familia": "fa", "conjunto": "practica", "ambito": "Bogotá", "fuente": "f", "anio": 2025,
                            "pregunta_pagina": "¿a?", "categorias": "1=No; 2=Sí; 99=NS/NR", "codigos_favorables": "[2]"},
                           {"id": "b", "familia": "fb", "conjunto": "guardado", "ambito": "Bogotá", "fuente": "f", "anio": 2025,
                            "pregunta_pagina": "¿b?", "categorias": "1=No; 2=Sí", "codigos_favorables": "[2]"}])
    edad = pd.Series(np.where(np.arange(n) < 40, 15, rng.integers(18, 80, n)))
    x = pd.Series(rng.choice([1, 2, 99], n))
    adultos = edad >= 18
    g = {k: s[adultos] for k, s in bl._grupos(pd.Series(rng.choice(["Hombres", "Mujeres"], n)), edad,
                                              pd.Series(rng.integers(1, 7, n))).items()}
    r = bl._calcular(sorteo, lambda f: x[adultos], pd.Series(np.ones(n))[adultos], g,
                     pd.Series(rng.integers(1, 20, n)).astype(str)[adultos])
    assert set(r) == {"a"} and r["a"]["n"] <= n - 40


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Banco, lotes 3 y 4 — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
