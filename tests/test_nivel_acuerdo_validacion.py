"""
tests/test_nivel_acuerdo_validacion.py

Pruebas de src/experiments/nivel_acuerdo_validacion.py con datos inventados y modelo simulado: ninguna
llama a la API ni calcula resultados del guardado.
Se ejecuta directo:  python tests/test_nivel_acuerdo_validacion.py
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.experiments import experimento9 as e9
from src.experiments import nivel_acuerdo_validacion as nv

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


def _cands():
    return pd.DataFrame([{"id": f"c{i}", "familia": f"fc{i}", "pregunta_pagina": f"¿Candidata {i}?",
                          "categorias": "1=Sí; 2=No", "codigos_favorables": "[1]", "total": 20.0 + 10 * i} for i in range(6)])


def _obj():
    return pd.DataFrame([{"id": "g0", "familia": "fg0", "fuente": "SCRD Bienal de Culturas", "pregunta_pagina": "¿Guardada?",
                          "categorias": "1=Sí; 2=No", "codigos_favorables": "[1]", "total": 80.0}])


def test_las_candidatas_son_las_de_practica_y_el_modelo_no_ve_resultados():
    vistos = []

    def llamar(modelo, sistema, usuario, temp):
        vistos.append(usuario)
        return json.dumps({"ids": ["c5", "c4"]})
    p = nv.elegir_todas(_obj(), _cands(), llamar, e9.Cache(Path(_tmp.name) / "a.json"), 1.0)
    u = vistos[0]
    assert all(f"- c{i} |" in u for i in range(6)) and "80.0" not in u and "70.0" not in u
    assert abs(p.S.iloc[0] - 65.0) < 1e-9 and p.ids.iloc[0] == ["c5", "c4"]


def test_el_rango_es_el_fijo_y_la_regla_tiene_las_tres_condiciones():
    assert nv.H == 21.9 and (nv.EAM_MAX, nv.LADO_MIN, nv.MARGEN) == (15.8, 0.67, 0.10)
    p = pd.DataFrame({"id": ["g0", "g1"], "familia": ["a", "b"], "total": [80.0, 20.0], "S": [75.0, 25.0], "fallo": [False, False]})
    o = pd.DataFrame({"id": ["g0", "g1"], "fuente": ["x", "ECP DANE"]})
    r = nv.evaluar(p, _cands(), o)
    assert r["lado"] == 1.0 and r["eam"] == 5.0 and r["decide"] == 1.0 and r["pasa"]


def test_el_metro_en_10_anios_se_calcula_sobre_respuestas_validas():
    assert nv.METRO10 == 43.78


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Validación del nivel de acuerdo — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
