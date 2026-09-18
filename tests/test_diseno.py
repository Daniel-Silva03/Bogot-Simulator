"""
tests/test_diseno.py

Pruebas de la estimación con diseño complejo (A19, DI-D1..DI-D5).
Se ejecuta directo:  python3 tests/test_diseno.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.utils.diseno import (
    DEFF_MEDIDO_EPC, DisenoError, deff_prestado, diferencia, media_disenio,
)

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


# -------------------------------------------------------------------------

def test_la_media_ponderada_es_la_de_siempre():
    y = np.array([1, 2, 3, 4, 5], float)
    w = np.array([1, 1, 2, 2, 4], float)
    e = media_disenio(y, w)
    assert abs(e.media - np.average(y, weights=w)) < 1e-12


def test_sin_upm_avisa_y_no_finge():
    e = media_disenio([1, 2, 3, 4], [1, 1, 1, 1])
    assert not e.con_diseno, "sin UPM no puede declararse estimación con diseño"
    assert e.deff == 1.0
    assert e.ee == e.ee_srs
    assert any("UPM" in n for n in e.notas), "tiene que decir por qué"


def test_una_observacion_por_upm_reproduce_casi_el_error_srs():
    """Sin conglomeración real el DEFF tiene que quedar cerca de 1."""
    rng = np.random.default_rng(0)
    n = 600
    y = rng.normal(3, 1, n)
    e = media_disenio(y, np.ones(n), psu=np.arange(n), estrato=np.zeros(n))
    assert 0.9 < e.deff < 1.2, f"DEFF {e.deff:.3f} lejos de 1 sin conglomeración"


def test_la_conglomeracion_sube_el_deff():
    """Conglomerados internamente homogéneos: el DEFF tiene que ser >> 1."""
    rng = np.random.default_rng(1)
    n_psu, por_psu = 40, 15
    efecto = rng.normal(0, 1.0, n_psu)                 # variación ENTRE manzanas
    y, psu = [], []
    for c in range(n_psu):
        y.append(efecto[c] + rng.normal(0, 0.25, por_psu))   # poca variación dentro
        psu.append(np.full(por_psu, c))
    y = np.concatenate(y); psu = np.concatenate(psu)
    e = media_disenio(y, np.ones(len(y)), psu=psu, estrato=np.zeros(len(y)))
    assert e.deff > 5, f"con conglomerados homogéneos el DEFF debería ser alto, dio {e.deff:.2f}"
    assert e.ee > e.ee_srs


def test_las_psu_solitarias_se_cuentan_y_no_se_esconden():
    y = np.array([1., 2, 3, 4, 5, 6])
    psu = ["a", "a", "b", "b", "solo", "otro"]
    est = ["h1", "h1", "h1", "h1", "h2", "h3"]
    e = media_disenio(y, np.ones(6), psu=psu, estrato=est)
    assert e.psu_solitarias == 2, f"esperaba 2 estratos solitarios, contó {e.psu_solitarias}"
    assert any("UPM" in n for n in e.notas)


def test_omitir_solitarias_da_menos_varianza_que_centrarlas():
    """Por eso 'centrado' es el default (DI-D3)."""
    y = np.array([1., 2, 3, 4, 9, 1])
    psu = ["a", "a", "b", "b", "solo", "otro"]
    est = ["h1", "h1", "h1", "h1", "h2", "h3"]
    c = media_disenio(y, np.ones(6), psu=psu, estrato=est, solitarias="centrado")
    o = media_disenio(y, np.ones(6), psu=psu, estrato=est, solitarias="omitir")
    assert o.ee < c.ee, "omitir tiene que subestimar frente a centrar"


def test_la_diferencia_suma_varianzas():
    a = media_disenio(np.array([1., 2, 3, 4]), np.ones(4), psu=np.arange(4), estrato=np.zeros(4))
    b = media_disenio(np.array([2., 3, 4, 5]), np.ones(4), psu=np.arange(4), estrato=np.zeros(4))
    d = diferencia(a, b)
    assert abs(d.delta - 1.0) < 1e-12
    assert abs(d.ee - np.sqrt(a.ee ** 2 + b.ee ** 2)) < 1e-12


def test_una_diferencia_chica_no_sale_significativa():
    """El caso que motiva todo esto: 2022->2023 movió -0,093 en la EPC.

    Construido determinista a propósito. La primera versión de esta prueba
    sorteaba las dos olas por separado y comprobaba que la diferencia no
    saliera significativa — es decir, medía el azar del generador, no el
    estimador. Falló, y con razón.
    """
    rng = np.random.default_rng(2)
    n = 1300
    base = rng.normal(2.60, 1.0, n)
    psu = rng.integers(0, 300, n)
    a = media_disenio(base, np.ones(n), psu=psu, estrato=np.zeros(n))
    b = media_disenio(base + 0.02, np.ones(n), psu=psu, estrato=np.zeros(n))
    d = diferencia(a, b)
    assert abs(d.delta - 0.02) < 1e-12
    assert not d.significativa, f"z = {d.z:.2f}: 0,02 puntos no puede ser detectable con n=1300"


def test_el_deff_prestado_deja_constancia():
    e = media_disenio([1., 2, 3, 4], [1, 1, 1, 1])
    p = deff_prestado(e, 2.0)
    assert abs(p.ee - e.ee_srs * np.sqrt(2.0)) < 1e-12
    assert not p.con_diseno, "un DEFF prestado no convierte esto en estimación con diseño"
    assert any("PRESTADO" in n for n in p.notas)


def test_no_se_presta_deff_a_algo_que_ya_tiene_diseno():
    e = media_disenio(np.array([1., 2, 3, 4]), np.ones(4),
                      psu=np.arange(4), estrato=np.zeros(4))
    try:
        deff_prestado(e)
    except DisenoError:
        pass
    else:
        raise AssertionError("debería negarse")


def test_los_nan_no_rompen_ni_se_cuelan():
    y = [1., np.nan, 3, 4]
    w = [1., 1, np.nan, 1]
    e = media_disenio(y, w)
    assert e.n == 2, f"debería quedarse con 2 observaciones, quedó con {e.n}"
    assert abs(e.media - 2.5) < 1e-12


def test_el_deff_medido_esta_registrado():
    assert DEFF_MEDIDO_EPC["minimo"] < DEFF_MEDIDO_EPC["mediana"] < DEFF_MEDIDO_EPC["maximo"]
    assert DEFF_MEDIDO_EPC["mediana"] > 1


# -------------------------------------------------------------------------

if __name__ == "__main__":
    pruebas = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"Diseño muestral complejo — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
