"""
tests/test_rango_variable.py

Pruebas de src/experiments/rango_variable.py (`RANGO_VARIABLE_SPECIFICATION.md`). Solo las funciones puras, con
datos inventados: no leen encuestas ni llaman a la API.
Se ejecuta directo:  python tests/test_rango_variable.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.experiments import rango_variable as rv

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def _practica(n=60, semilla=1):
    rng = np.random.default_rng(semilla)
    k = rng.integers(1, 6, n)
    sd = np.where(k >= 2, rng.uniform(1, 20, n), 0.0)
    return pd.DataFrame({"k": k, "sd": sd, "rango": 2.5 * sd, "err": rng.uniform(0, 30, n)})


def test_los_rasgos_de_una_estimacion():
    tot = {"a": 40.0, "b": 60.0, "c": 50.0}
    assert rv.rasgos(["a", "b", "c"], tot) == {"k": 3, "sd": float(np.std([40, 60, 50])), "rango": 20.0}
    assert rv.rasgos(["a"], tot) == {"k": 1, "sd": 0.0, "rango": 0.0}


def test_cada_forma_cubre_el_80_por_ciento_de_la_practica():
    """DI-RV2: calibradas como el rango fijo."""
    r = _practica()
    for f in ("F2", "F3"):
        cal = rv.calibrar(f, r)
        h = np.array([rv.ancho(f, cal, x) for x in r.to_dict("records")])
        assert abs((r.err <= h + 1e-9).mean() - 0.8) < 0.05, f


def test_con_una_sola_elegida_vale_el_piso():
    r = _practica()
    cal = rv.calibrar("F2", r)
    assert rv.ancho("F2", cal, {"k": 1, "sd": 0.0, "rango": 0.0}) == cal["c"] * cal["m"]
    assert rv.ancho("F2", cal, {"k": 3, "sd": 2 * cal["m"], "rango": 0}) == 2 * cal["c"] * cal["m"]


def test_un_grupo_chico_usa_el_rango_fijo():
    r = pd.DataFrame({"k": [1] * 3 + [2] * 20 + [4] * 20, "sd": 0.0, "rango": 0.0, "err": np.arange(43, dtype=float)})
    cal = rv.calibrar("F1", r)
    assert cal["por_grupo"]["1"] == cal["h0"]


def test_la_forma_se_elige_por_el_ancho_y_el_empate_va_a_la_mas_simple():
    assert rv.elegir_forma({"F0": 23.4, "F1": 22.0, "F2": 19.0, "F3": 19.3}) == "F2"
    assert rv.elegir_forma({"F0": 24.0, "F1": 23.0, "F2": 22.95, "F3": 25}) == "F1"
    assert rv.elegir_forma({"F0": 23.4, "F1": 23.2, "F2": 23.0, "F3": 23.1}) == "F0"


def test_la_llamada_y_la_regla():
    assert rv.llamada(80, 20) == "sí" and rv.llamada(20, 20) == "no" and rv.llamada(60, 20) == "dividida"
    m0 = {"cobertura": 0.8, "decide": 11, "acierto_al_decidir": 10 / 11}
    assert rv.regla({"cobertura": 0.78, "decide": 25, "acierto_al_decidir": 0.92}, m0, "F2")["cumple"]
    assert not rv.regla({"cobertura": 0.70, "decide": 25, "acierto_al_decidir": 0.92}, m0, "F2")["R2"]
    assert not rv.regla({"cobertura": 0.8, "decide": 11, "acierto_al_decidir": 1.0}, m0, "F2")["R3"]
    assert not rv.regla({"cobertura": 0.8, "decide": 25, "acierto_al_decidir": 0.88}, m0, "F2")["R4"]
    assert not rv.regla({"cobertura": 0.8, "decide": 25, "acierto_al_decidir": 1.0}, m0, "F0")["R1"]


def test_los_umbrales_son_los_del_documento():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "RANGO_VARIABLE_SPECIFICATION.md").read_text(encoding="utf-8")
    assert rv.COBERTURA_MIN == 0.75 and rv.ACIERTO_MIN == 0.90 and rv.EMPATE == 0.5 and rv.MIN_GRUPO == 10
    assert "≥ 75 %" in doc and "≥ 90 %" in doc and "0,5 puntos" in doc and "menos de 10" in doc


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Rango variable — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
