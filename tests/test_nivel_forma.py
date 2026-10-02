"""
tests/test_nivel_forma.py

Pruebas de src/experiments/nivel_forma.py con datos inventados: ninguna lee el banco.
Se ejecuta directo:  python tests/test_nivel_forma.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.experiments import nivel_forma as nf

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_el_tipo_sigue_el_orden_pre_registrado():
    assert nf.tipo("¿Qué tanto confía en la corrupción del Congreso?") == "corrupcion"     # gana la primera
    assert nf.tipo("¿Qué tanto confía usted en la Policía?") == "confianza"
    assert nf.tipo("¿Qué tan favorable es la imagen del IDU?") == "imagen"
    assert nf.tipo("¿Qué tan satisfecho está con su vida?") == "satisfaccion"
    assert nf.tipo("¿Está de acuerdo con el metro elevado?") == "acuerdo"
    assert nf.tipo("¿Cuántas veces votó?") == "otro"


def test_los_rasgos_salen_de_la_estructura():
    t = pd.DataFrame([
        {"categorias": "1=Favorable; 2=Desfavorable; 3=No conoce; 99=No sabe", "codigos_favorables": "[1]",
         "pregunta_pagina": "¿Qué tan favorable es la imagen del IDU?", "ambito": "Bogotá"},
        {"categorias": "1=Nada; 2=Poco; 3=Algo; 4=Bastante; 5=Mucho", "codigos_favorables": "[4, 5]",
         "pregunta_pagina": "¿Qué tanto confía en los jueces?", "ambito": "general"}])
    from src.experiments import banco_reales as br
    if br.validos(br.categorias(t.categorias[0])) != [1, 2, 3]:
        raise AssertionError(f"formato de categorías inesperado: {br.categorias(t.categorias[0])}")
    f = nf.rasgos(t)
    assert abs(f.F1[0] - 1 / 3) < 1e-9 and f.F2[0] == 1 and f.tipo[0] == "imagen" and f.F4[0] == 1
    assert abs(f.F1[1] - 0.4) < 1e-9 and f.F2[1] == 0 and f.tipo[1] == "confianza" and f.F4[1] == 0


def test_la_validacion_no_usa_la_familia_propia():
    """Si cada familia tiene un nivel propio que ningún rasgo explica, la predicción no puede copiarlo."""
    rng = np.random.default_rng(0)
    fam = np.repeat(np.arange(10), 5)
    y = np.repeat(rng.uniform(0, 100, 10), 5)
    x = np.column_stack([np.ones(50), rng.normal(size=50)])
    p = nf.predecir(x, y, fam)
    assert nf.eam(p, y) > 10
    p_fuga = nf.predecir(np.column_stack([x, np.eye(10)[fam]]), y, np.arange(50))    # con la familia como rasgo y sin dejarla fuera
    assert nf.eam(p_fuga, y) < 1


def test_un_rasgo_que_explica_el_nivel_se_aprende():
    rng = np.random.default_rng(1)
    fam = np.repeat(np.arange(20), 4)
    f1 = rng.uniform(0.2, 0.6, 80)
    y = 100 * f1 + rng.normal(0, 2, 80)
    p = nf.predecir(np.column_stack([np.ones(80), f1]), y, fam)
    assert nf.eam(p, y) < 3


def test_un_tipo_ausente_al_dejar_fuera_su_familia_se_predice_como_otro():
    f = pd.DataFrame({"F1": [0.4] * 6, "F2": [0.0] * 6, "F4": [0.0] * 6,
                      "tipo": ["acuerdo", "acuerdo", "otro", "otro", "otro", "otro"]})
    y = np.array([90, 90, 30, 30, 30, 30], float)
    p = nf.predecir(nf.matriz(f), y, np.array([0, 0, 1, 1, 2, 2]))
    assert abs(p[0] - 30) < 1e-6 and abs(p[2] - 30) < 1e-6


def test_las_predicciones_se_recortan_a_0_100():
    x = np.column_stack([np.ones(4), [0, 1, 2, 10]])
    y = np.array([0, 50, 100, 0.0])
    p = nf.predecir(x, y, np.array([0, 1, 2, 3]))
    assert p.min() >= 0 and p.max() <= 100


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Nivel por la forma — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
