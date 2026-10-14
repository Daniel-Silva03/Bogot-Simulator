"""
tests/test_estimacion_aprendida.py

Pruebas de src/experiments/estimacion_aprendida.py (`ESTIMACION_APRENDIDA_SPECIFICATION.md`). No llaman a la API.
Se ejecuta directo:  python tests/test_estimacion_aprendida.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from src.experiments import estimacion_aprendida as ea

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_el_texto_lleva_las_categorias_validas_y_la_favorable():
    t = ea.texto_emb("¿Está de acuerdo con X?", "1=De acuerdo; 2=En desacuerdo; 9=NS/NR", "[1]")
    assert t == "query: ¿Está de acuerdo con X? | 1=De acuerdo*; 2=En desacuerdo"


def test_vecinos_y_ridge():
    xe = np.eye(4); y = np.array([10.0, 20.0, 30.0, 90.0])
    assert ea.vecinos(xe, y, np.array([[0, 0, 0, 1.0]]), 1)[0] == 90.0
    assert ea.vecinos(xe, y, np.array([[1.0, 0, 0, 0]]), 2)[0] in (15.0, 20.0, 50.0)
    p = ea.ridge(xe, y, xe, 0.001)
    assert np.allclose(p, y, atol=0.5) and (ea.ridge(xe, y * 3, xe, 0.001) <= 100).all()        # recorta a 0-100


def test_la_regla_pide_un_punto_menos_que_e():
    e = {"eam": 15.3}
    bien = {"eam": 14.2, "lado": 0.72, "decide": 0.1, "acierto_al_decidir": 0.92, "pasa": True}
    assert ea.regla(e, bien)["reemplaza"]
    assert not ea.regla(e, {**bien, "eam": 14.4})["reemplaza"]
    assert not ea.regla(e, {**bien, "lado": 0.69})["reemplaza"]


def test_el_documento_y_los_parametros():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "ESTIMACION_APRENDIDA_SPECIFICATION.md").read_text(encoding="utf-8")
    assert ea.ALFAS == (1, 10, 100, 1000) and ea.KS == (5, 10, 20) and ea.CUANTIL == 0.8
    assert "{1, 10, 100, 1000}" in doc and "{5, 10, 20}" in doc and "≤ 14,3" in doc and ea.MODELO_EMB in doc


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Estimación aprendida — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
