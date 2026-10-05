"""
tests/test_nivel_acuerdo.py

Pruebas de src/experiments/nivel_acuerdo.py con datos inventados: ninguna lee el banco.
Se ejecuta directo:  python tests/test_nivel_acuerdo.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.experiments import nivel_acuerdo as na

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_el_tipo_sale_de_las_categorias():
    assert na.tipo("1=En desacuerdo; 2=De acuerdo") == "acuerdo"
    assert na.tipo("1=Sí; 2=No; 99=NS/NR") == "sí/no"
    assert na.tipo("1=Mucho; 2=Poco; 3=Nada") is None
    assert na.tipo("1=Siempre; 2=Nunca") is None                               # «Si» dentro de otra palabra no cuenta


def _t():
    filas = []
    for i in range(20):
        sino = i % 2 == 0
        filas.append({"id": f"q{i:02d}", "familia": f"f{i // 2}", "ambito": "Bogotá",
                      "pregunta_pagina": f"¿Pregunta {'de sí' if sino else 'de acuerdo'} {i}?",
                      "categorias": "1=Sí; 2=No" if sino else "1=En desacuerdo; 2=De acuerdo",
                      "codigos_favorables": "[1]" if sino else "[2]", "lote": 1,
                      "tipo": "sí/no" if sino else "acuerdo", "total": 70.0 if sino else 30.0})
    return pd.DataFrame(filas)


def test_la_forma_aprende_el_nivel_por_tipo_y_nunca_usa_la_familia():
    p = na.predecir(_t())
    assert np.abs(p.M2 - p.total).max() < 1e-6                               # el tipo explica todo el nivel
    assert (p.M0.between(30, 70)).all()


def test_el_rango_no_usa_su_propia_familia_y_la_llamada_decide_bien():
    p = na.predecir(_t())
    h = na.rangos(p, "M2")
    assert np.allclose(h, 0, atol=1e-6)
    d = na.llamada(p.M2.to_numpy(), h)
    assert set(d) == {"sí", "no"}
    r = na.medir(p)
    assert r["metodos"]["M2"]["lado"] == 1.0 and r["metodos"]["M2"]["acierto_al_decidir"] == 1.0


def test_la_regla_es_la_pre_registrada():
    r = {"referencia_lado": 0.70, "metodos": {"M0": {"eam": 20, "lado": 0.70}, "M1": {"eam": 16, "lado": 0.80},
                                               "M2": {"eam": 15.9, "lado": 0.79}}}
    assert na.regla(r) == {"M0": False, "M1": True, "M2": False}


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Nivel de acuerdo — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
