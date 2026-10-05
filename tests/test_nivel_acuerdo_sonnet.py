"""
tests/test_nivel_acuerdo_sonnet.py

Pruebas de src/experiments/nivel_acuerdo_sonnet.py con modelo simulado: ninguna llama a la API.
Se ejecuta directo:  python tests/test_nivel_acuerdo_sonnet.py
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.experiments import experimento9 as e9
from src.experiments import nivel_acuerdo_sonnet as ns
from src.experiments import nivel_parecidas_b as nb

FALLOS = []
_tmp = tempfile.TemporaryDirectory()


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def _t():
    filas = []
    for i in range(12):
        sino = i % 2 == 0
        filas.append({"id": f"q{i:02d}", "familia": f"f{i // 2}", "ambito": "Bogotá", "pregunta_pagina": f"¿Pregunta {i}?",
                      "categorias": "1=Sí; 2=No" if sino else "1=En desacuerdo; 2=De acuerdo",
                      "codigos_favorables": "[1]" if sino else "[2]", "lote": 1, "tipo": "sí/no" if sino else "acuerdo",
                      "total": 70.0 if sino else 30.0})
    return pd.DataFrame(filas)


def test_el_modelo_no_ve_resultados_ni_su_familia():
    t = _t()
    u, val = nb.prompt(t, 0)
    assert "q01" not in val and "q00" not in val and "70.0" not in u and "30.0" not in u


def test_elegir_bien_da_error_cero_y_cumple_la_regla():
    t = _t()

    def oraculo(modelo, sistema, usuario, temp):                             # elige las del mismo tipo
        nueva_si = "Escala: 1=Sí*" in usuario
        ids = [r.id for r in t.itertuples() if (r.tipo == "sí/no") == nueva_si and f"- {r.id} |" in usuario][:3]
        return json.dumps({"ids": ids})
    p = nb.correr(t, oraculo, e9.Cache(Path(_tmp.name) / "o.json"), "m", tope=1.0)
    r = ns.evaluar(t, p)
    assert r["eam"] < 1e-9 and r["lado"] == 1.0 and r["sirve"]


def test_la_regla_usa_las_cifras_del_paso_1():
    assert ns.LADO_MIN == 0.67 and ns.EAM_MAX == 15.8 and ns.TOPE_USD == 3.0


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Nivel de acuerdo con Sonnet — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
