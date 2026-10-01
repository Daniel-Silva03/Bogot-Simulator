"""
tests/test_banco_reales.py

Pruebas de src/experiments/banco_reales.py con datos inventados.
Se ejecuta directo:  python tests/test_banco_reales.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.experiments import banco as ba
from src.experiments import banco_reales as br

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_los_validos_dejan_fuera_no_sabe():
    cats = br.categorias("1=Mucho; 2=Algo; 3=Nada; 99=No sabe/No informa; 0=No responde")
    assert sorted(br.validos(cats)) == [1, 2, 3]


def test_los_tramos_de_edad_son_los_de_la_poblacion():
    assert list(br.edad_grupo(pd.Series([18, 25, 26, 55, 56, 90]), False)) == ["18-25", "18-25", "26-35", "46-55", "56+", "56+"]
    g = list(br.edad_grupo(pd.Series([1, 3, 5, 9]), True))
    assert g[:3] == ["18-25", "36-45", "56+"] and pd.isna(g[3])
    assert [br.estrato_grupo(e) for e in (0, 1, 4, 5, 6, np.nan)] == [None, "1", "4", "5-6", "5-6", None]


def test_el_porcentaje_es_ponderado_y_sobre_respuestas_validas():
    x = pd.Series([1, 1, 2, 99, 2])
    w = pd.Series([1.0, 3.0, 1.0, 5.0, 1.0])
    g = {"sexo": pd.Series(["Hombres", "Hombres", "Mujeres", "Mujeres", "Mujeres"])}
    r = br.resultado(x, w, g, [1], [1, 2])
    assert r["total"] == round(100 * 4 / 6, 2) and r["n"] == 4
    assert r["grupos"]["sexo"] == {"Hombres": 100.0, "Mujeres": 0.0} and r["bases"]["sexo"] == {"Hombres": 2, "Mujeres": 2}


def test_la_regla_de_estructura():
    """DI-BR5."""
    assert br.estructura({"n": 299, "codigos_validos_presentes": 3}).startswith("menos de 300")
    assert br.estructura({"n": 2000, "codigos_validos_presentes": 1}) == "un solo código válido en los datos"
    assert br.estructura({"n": 2000, "codigos_validos_presentes": 2}) is None


def test_los_pares_claros_piden_diferencia_y_base():
    res = {"grupos": {"sexo": {"Hombres": 40.0, "Mujeres": 60.0}, "edad": {"18-25": 50.0, "56+": 51.0}},
           "bases": {"sexo": {"Hombres": 1000, "Mujeres": 1000}, "edad": {"18-25": 1000, "56+": 1000}}}
    assert br.pares_claros(res, dims=("sexo", "edad")) == [("sexo", "Mujeres", "Hombres")]


def test_solo_hay_resultados_de_practica():
    if not br.SALIDA.exists():
        print("         (sin el cálculo en esta máquina: se omite)")
        return
    r = json.loads(br.SALIDA.read_text(encoding="utf-8"))
    s = pd.read_csv(ba.SALIDA / "sorteo.csv")
    assert set(r) == set(s[s.conjunto == "practica"].id) and not set(r) & set(s[s.conjunto == "guardado"].id)


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Banco, resultados reales — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
