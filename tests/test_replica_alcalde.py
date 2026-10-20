"""
tests/test_replica_alcalde.py

Pruebas de src/evaluacion/replica_alcalde.py (`REPLICA_ALCALDE_SPECIFICATION.md`). No llaman a la API.
Se ejecuta directo:  python tests/test_replica_alcalde.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.evaluacion import replica_alcalde as ra

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_el_perfil_de_2022_lleva_al_alcalde_y_al_concejo():
    _, d, perfil = ra.datos_con_gobierno(2022)
    cols = [c for _, c, _ in perfil]
    assert "GG3" in cols and "CC5" in cols and cols.count("GG3") == 1


def test_el_perfil_de_2024_no_se_duplica():
    from src.experiments import personas_con_encuesta as pc
    assert len(ra.datos_con_gobierno(2024)[2]) == len(pc.datos(2024)[2])


def test_las_preguntas_nombran_al_gobierno_del_anio_objetivo():
    p23, p24 = ra.preguntas(2022, 2023), ra.preguntas(2023, 2024)
    assert [e["variable"] for e in p23] == ["AG1", "GG7", "ALCALDE", "CONCEJO"]
    assert "Claudia López" in p23[2]["pregunta"] and "Galán" in p24[2]["pregunta"]
    assert p23[2]["cuenta"] == [4, 5]


def test_la_fase_b_entra_sin_cc9_y_con_siete():
    t = ra.objetivos_fase_b()
    assert len(t) == 7 and "CC9" not in set(t.variable) and {"ALCALDE", "CONCEJO"} <= set(t.variable)


def test_la_regla():
    filas = []
    for tr in ("T0", "T1", "T2"):
        for v in ("AG1", "GG7", "ALCALDE", "CONCEJO"):
            filas.append({"transicion": tr, "variable": v, "P": 40.0, "G": 33.0, "real": 30.0})
    r = ra.evaluar(pd.DataFrame(filas))
    assert r["reglas"]["se_reproduce"] and r["reglas"]["RA"] and r["alcalde_gana_G"] == 3
    filas[0]["G"] = filas[0]["P"] = 30.0
    assert ra.evaluar(pd.DataFrame(filas))["n"] == 12


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Réplica del alcalde — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
