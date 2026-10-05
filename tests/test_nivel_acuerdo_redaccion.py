"""
tests/test_nivel_acuerdo_redaccion.py

Pruebas de src/experiments/nivel_acuerdo_redaccion.py: ninguna llama a la API.
Se ejecuta directo:  python tests/test_nivel_acuerdo_redaccion.py
"""

import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import nivel_acuerdo_redaccion as nr

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_las_originales_son_las_95_guardadas_y_la_practica_las_92():
    g, p = nr.originales(), nr.practica()
    assert len(g) == 95 and len(p) == 92 and not set(g.id) & set(p.id)


def test_el_h_de_s_en_la_practica_es_el_21_9_de_la_pagina():
    p = nr.practica()
    assert abs(nr.ajustar(p.S, p.total)["h"]["S"] - nr.H) < 0.05


def test_e1_iguala_la_dispersion_y_e2_es_la_recta():
    rng = np.random.default_rng(1)
    t = rng.uniform(5, 95, 200)
    S = 50 + 0.6 * (t - 50) + rng.normal(0, 5, 200)
    p = nr.ajustar(S, t)
    assert abs(nr.transformar("E1", S, p).std() - t.std()) < 0.5
    b, a = np.polyfit(S, t, 1)
    assert np.allclose(nr.transformar("E2", S, p), np.clip(a + b * S, 0, 100))
    assert nr.transformar("E1", np.array([-500.0, 500.0]), p).tolist() == [0.0, 100.0]


def test_medir_cuenta_la_cobertura_por_extremas():
    m = nr.medir([10, 50, 80], [5, 52, 99], 10)
    assert m["n_extremas"] == 2 and m["cobertura_extremas"] == 0.5 and m["cobertura_intermedias"] == 1.0


def test_la_regla_b_pide_los_dos_lugares():
    s = {"eam": 12, "lado": 0.7, "n_decide": 10, "acierto_al_decidir": 1.0, "cobertura_extremas": 0.6}
    bueno = {"S": s, "E1": {**s, "eam": 12.3, "cobertura_extremas": 0.75}, "E2": {**s, "eam": 11.4}}
    malo = {"S": s, "E1": {**s, "eam": 13.0, "cobertura_extremas": 0.75}, "E2": {**s, "eam": 11.8}}
    assert nr.regla_b(bueno, bueno) == {"E1_se_propone": True, "E2_se_propone": True}
    assert nr.regla_b(bueno, malo) == {"E1_se_propone": False, "E2_se_propone": False}


def test_la_parte_a_simulada_reformula_y_estima_con_la_funcion_de_la_pagina():
    from src.consulta import motor as mo
    from src.experiments import experimento9 as e9
    llamar, _ = mo.cliente(simulado=True)
    o74, o21 = nr.nl.objetivos()
    o = pd.concat([o74, o21], ignore_index=True).head(4)
    cache = e9.Cache(Path(tempfile.mkdtemp()) / "c.json")
    res = nr.correr_a(o, llamar, llamar, cache, nr.TOPE_USD)
    assert len(res) == 4 and set(res.alcance) <= {"nueva", "catalogo", "fuera", "invalida"}
    assert res[res.alcance == "nueva"].S.notna().all()
    r = nr.evaluar_a(res, nr.originales())
    assert r["estabilidad"]["n"] == 4 and set(r["regla"]) == {"eam", "lado", "al_decidir", "se_sostiene"}


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"La estimación ante la redacción — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
