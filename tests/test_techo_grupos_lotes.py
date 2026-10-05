"""
tests/test_techo_grupos_lotes.py

Pruebas de src/experiments/techo_grupos_lotes.py con datos inventados: ninguna lee el banco.
Se ejecuta directo:  python tests/test_techo_grupos_lotes.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.experiments import techo_grupos as tg
from src.experiments import techo_grupos_lotes as tl

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def _caso(n=3000, efecto=0.12, seed=0):
    rng = np.random.default_rng(seed)
    est = pd.Series(rng.choice(["1", "2", "3", "4", "5-6"], n))
    nivel = est.map({"1": 0, "2": 1, "3": 2, "4": 3, "5-6": 4})
    x = pd.Series(np.where(rng.random(n) < 0.3 + efecto * nivel, 2, 1))
    g = {"sexo": pd.Series(rng.choice(["Hombres", "Mujeres"], n)), "edad": pd.Series(rng.choice(["18-25", "56+"], n)),
         "estrato": est}
    sorteo = pd.DataFrame([{"id": "q", "categorias": "1=No; 2=Sí; 99=NS/NR", "codigos_favorables": "[2]"}])
    reales = {"q": {"grupos": {"sexo": {"Hombres": 0, "Mujeres": 0}, "edad": {"18-25": 0, "56+": 0},
                               "estrato": {k: 0 for k in ["1", "2", "3", "4", "5-6"]}}}}
    return sorteo, reales, x, pd.Series(np.ones(n)), g


def test_los_arreglos_de_la_replica_salen_de_la_misma_lectura():
    sorteo, reales, x, w, g = _caso()
    qs = tl.preguntas_replica(reales, sorteo, lambda f: x, w, g)
    assert len(qs) == 1 and qs[0]["ok"].all() and set(qs[0]["fav"]) <= {0.0, 1.0}
    assert qs[0]["etq"]["estrato"] == ["1", "2", "3", "4", "5-6"]


def test_con_efecto_fuerte_la_replica_por_persona_acierta_casi_todo():
    sorteo, reales, x, w, g = _caso()
    qs = tl.preguntas_replica(reales, sorteo, lambda f: x, w, g)
    rep = tg.medida_replica({("x", 1): {"psu": np.arange(len(x)).astype(str), "preguntas": qs}}, n=20, semilla=1)
    assert rep["media"] > 0.95, rep


def test_un_no_sabe_o_un_peso_vacio_no_cuentan():
    sorteo, reales, x, w, g = _caso(n=200)
    x.iloc[:10] = 99
    w.iloc[10:20] = np.nan
    qs = tl.preguntas_replica(reales, sorteo, lambda f: x, w, g)
    assert qs[0]["ok"].sum() == 180


def test_la_lectura_es_la_del_lote_1():
    assert tl.lectura(0.80) == "A" and tl.lectura(0.75) == "B" and tl.lectura(0.6) == "C"


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Techo en el banco ampliado — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
