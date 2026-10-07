"""
tests/test_voto_simulado.py

Pruebas de src/experiments/voto_simulado.py: ninguna llama a la API ni imprime porcentajes de las encuestas.
Las que necesitan los resultados del lote 7 se saltan si no están en este computador.
Se ejecuta directo:  python tests/test_voto_simulado.py
"""

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import banco_lote7 as b7
from src.experiments import voto_simulado as vs

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_la_regla_pide_las_tres_condiciones():
    m = {"eam": 5.0, "adelante": 0.85, "dice_probable": 6, "acierta_probable": 0.95}
    assert vs.regla(m, 10, 8)["cumple"]
    assert not vs.regla({**m, "eam": 6.5}, 10, 9)["cumple"]                          # error
    assert not vs.regla({**m, "adelante": 0.7}, 10, 8)["cumple"]                     # quién va adelante
    assert not vs.regla({**m, "acierta_probable": 0.8}, 10, 8)["cumple"]             # al decir «probablemente»
    assert vs.regla({**m, "dice_probable": 3, "acierta_probable": 0.5}, 10, 8)["cumple"]   # menos de 5: no cuenta
    assert not vs.regla(m, 10, 6)["cumple"]                                          # no mejora el último dato


def test_la_opcion_se_normaliza():
    f = {"id": "X_P5_2", "codigos_favorables": json.dumps([2]), "categorias": "1=Iván Cepeda; 2=Sergio  Fajardo; 9=NS/NR"}
    assert vs.opcion(f) == "sergio fajardo"
    assert vs.opcion({"id": "X_F1_votaria", "codigos_favorables": "[1, 2]", "categorias": ""}) == "votaria"


def test_pares_de_segunda_vuelta_y_quien_va_adelante():
    tabla = pd.DataFrame({"id": ["CC871401_P3_1", "CC871401_P3_2"], "familia": ["CC871401_P3"] * 2,
                          "total": [30.0, 50.0], "variable": ["P3", "P3"]})
    p = pd.DataFrame({"id": ["CC871401_P3_1", "CC871401_P3_2"], "S": [35.0, 45.0]})
    pr = vs.pares_segunda(p, tabla)
    assert len(pr) == 1 and pr.d_est.iloc[0] == -10 and pr.d_real.iloc[0] == -20
    m = vs.medir(p, tabla, h=10, h2=5)
    assert m["adelante"] == 1.0 and m["dice_probable"] == 1 and m["eam"] == 5.0


def test_las_tablas_no_cruzan_practica_y_guardado():
    if not (b7.REALES.exists() and vs.REALES_G7.exists()):
        print("         (sin los resultados del lote 7: se salta)")
        return
    p, g = vs.practica(), vs.guardado()
    assert not set(p.familia) & set(g.familia) and len(p) == 158


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Voto simulado — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
