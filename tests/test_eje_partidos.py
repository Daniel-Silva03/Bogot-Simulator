"""
tests/test_eje_partidos.py

Pruebas de src/experiments/eje_partidos.py antes de la corrida real
(`EJE_PARTIDOS_SPECIFICATION.md` §4). Usan la composición real (si está en esta
máquina) con votos por partido INVENTADOS: ninguna prueba cruza el voto real.
Se ejecuta directo:  python tests/test_eje_partidos.py
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.experiments import eje_partidos as ep
from src.experiments import geografia_electoral as ge

FALLOS = []
SEMILLAS = 300


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


if ge.RECEPTOR.exists():
    logging.disable(logging.WARNING)
    COMP = ge.composicion()
else:
    _r = np.random.default_rng(0)
    COMP = pd.DataFrame({"x1": _r.uniform(1.3, 4.6, 20), "x2": 0.3, "x3": 44.0}, index=range(1, 21))
LOCS = sorted(set(COMP.index) - {ge.SUMAPAZ})
X = COMP.loc[LOCS, "x1"].to_numpy()
OTROS = ["PARTIDO ALIANZA VERDE", "PARTIDO CAMBIO RADICAL"]


def mundo(rng, dec=0.0, cd=0.0, u=None, ruido=0.005):
    """Proporciones por partido. `dec`/`cd` = cuánto sigue cada partido al eje u."""
    u = rng.normal(0, 0.04, len(LOCS)) if u is None else u
    base = {ep.DECENCIA: 0.10 - 0.03 * (X - X.mean()) + dec * u,
            ep.CENTRO_DEMOCRATICO: 0.20 + 0.05 * (X - X.mean()) + cd * u}
    for o in OTROS:
        base[o] = 0.15 + rng.normal(0, 0.02, len(LOCS))
    df = pd.DataFrame({k: v + rng.normal(0, ruido, len(LOCS)) for k, v in base.items()}, index=LOCS)
    eje = pd.Series(u, index=LOCS)
    return df, eje


def analisis(rng, dec, cd, razon=None, dec_c=None, cd_c=None):
    s, eje = mundo(rng, dec, cd)
    c, _ = mundo(rng, dec if dec_c is None else dec_c, cd if cd_c is None else cd_c, u=eje.to_numpy())
    props = {ep.PRINCIPAL: s, ep.REPLICA: c}
    return ep.analizar(props, COMP, eje, list(s.columns), razon, n_perm=199)


# --- la permutación de dos colas (DI-EP2) ------------------------------------

def test_dos_colas_detecta_los_dos_signos():
    a = np.arange(19.0)
    r, p = ep.correlacion_dos_colas(a, -a, n=199, rng=np.random.default_rng(1))
    assert r < -0.99 and p == 1 / 200, (r, p)
    r, p = ep.correlacion_dos_colas(a, a, n=199, rng=np.random.default_rng(1))
    assert r > 0.99 and p == 1 / 200


def test_dos_colas_no_se_equivoca_mas_del_5_por_ciento():
    rng = np.random.default_rng(2)
    falsos = sum(ep.correlacion_dos_colas(rng.normal(size=19), rng.normal(size=19), n=199, rng=rng)[1] < 0.05
                 for _ in range(SEMILLAS))
    assert 0.01 <= falsos / SEMILLAS <= 0.09, falsos / SEMILLAS


def test_dos_colas_es_mas_exigente_que_una_cola():
    rng = np.random.default_rng(3)
    a = rng.normal(size=19)
    b = a + rng.normal(0, 1.5, 19)
    _, p1 = ge.persistencia(a, b, n=2000, rng=np.random.default_rng(4))
    _, p2 = ep.correlacion_dos_colas(a, b, n=2000, rng=np.random.default_rng(4))
    assert p2 >= p1, (p1, p2)


# --- la regla, en mundos donde se sabe la respuesta ---------------------------

def test_lectura_a_cuando_los_dos_partidos_siguen_al_eje():
    v = ep.evaluar(analisis(np.random.default_rng(10), dec=1.0, cd=-1.0))
    assert v["regla"].startswith("A"), v["regla"]
    assert all(v["predicciones"][k]["se_cumple"] for k in ("P1", "P2", "P3"))


def test_lectura_b_cuando_solo_lo_sigue_la_lista_de_petro():
    v = ep.evaluar(analisis(np.random.default_rng(11), dec=1.0, cd=0.0))
    assert v["regla"].startswith("B"), v["regla"]


def test_lectura_c_cuando_ninguno_lo_sigue():
    """Sin eje, C casi siempre; B por azar solo con la tasa de un p < 0,05.

    Una sola semilla no sirve aquí: con 19 localidades, una de cada ~40 da
    |r| > 0,5 por azar (la semilla 12 lo hacía, y así se descubrió)."""
    reglas = [ep.evaluar(analisis(np.random.default_rng(1000 + s), dec=0.0, cd=0.0))["regla"][0]
              for s in range(100)]
    assert reglas.count("C") >= 90, reglas.count("C")
    assert reglas.count("A") == 0 and reglas.count("B") <= 6, (reglas.count("A"), reglas.count("B"))


def test_el_resultado_se_puede_escribir_en_json():
    import json
    json.dumps(ep.evaluar(analisis(np.random.default_rng(15), dec=1.0, cd=-1.0)))


def test_sin_replica_en_camara_es_intermedio():
    v = ep.evaluar(analisis(np.random.default_rng(13), dec=1.0, cd=-1.0, dec_c=0.0, cd_c=0.0))
    assert v["regla"].startswith("Intermedio: no se adopta"), v["regla"]
    assert not v["predicciones"]["P3"]["se_cumple"]


def test_la_inscripcion_bloquea_la_lectura():
    rng = np.random.default_rng(14)
    s, eje = mundo(rng, 1.0, -1.0)
    c, _ = mundo(rng, 1.0, -1.0, u=eje.to_numpy())
    razon = pd.Series(1.0, index=range(1, 21))
    razon.loc[LOCS] = 1 + eje.to_numpy()                 # la inscripción ES el eje
    a = ep.analizar({ep.PRINCIPAL: s, ep.REPLICA: c}, COMP, eje, list(s.columns), razon, n_perm=199)
    v = ep.evaluar(a)
    assert not v["predicciones"]["P5"]["se_cumple"] and v["regla"].startswith("Intermedio: el resto"), v["regla"]


def test_la_regla_acierta_en_la_mayoria_de_las_semillas():
    """No basta con una semilla afortunada: con un eje real de tamaño modesto, A sale casi siempre."""
    aciertos = sum(ep.evaluar(analisis(np.random.default_rng(100 + s), dec=1.0, cd=-1.0))["regla"].startswith("A")
                   for s in range(40))
    assert aciertos >= 36, aciertos


# --- datos: preparación, sin cruzar ------------------------------------------

def test_proporcion_por_partido_sobre_votos_partidos_y_sin_zonas_especiales():
    votos = pd.DataFrame({"corporacion": "senado", "circunscripcion": "nacional",
                          "zona": [1, 1, 1, 90], "cod_loc": [1, 1, 1, None],
                          "partido": ["A", "B", "VOTOS EN BLANCO", "A"],
                          "tipo": ["partido", "partido", "blanco", "partido"], "votos": [30, 70, 50, 9]})
    zonas = pd.DataFrame({"corporacion": "senado", "circunscripcion": "nacional",
                          "zona": [1, 90], "votos_partidos": [100, 9]})
    p = ep.proporciones_partido(votos, zonas, "senado", "nacional")
    assert list(p.index) == [1] and p.loc[1, "A"] == 0.3 and p.loc[1, "B"] == 0.7


def test_los_partidos_decisivos_cumplen_su_regla():
    ruta = ge.ELECTORAL / "congreso_2018_localidad.csv"
    if not ruta.exists():
        print("         (sin la tabla del Congreso: se omite)")
        return
    votos = pd.read_csv(ruta)
    seis = ep.verificar_decisivos(votos)
    assert len(seis) == 6 and set(ep.DECISIVOS) <= set(seis)
    otro = votos[votos.partido != ep.CENTRO_DEMOCRATICO]
    try:
        ep.verificar_decisivos(otro)
    except ep.EjeError:
        return
    raise AssertionError("no detectó que faltaba un partido decisivo")


def test_el_eje_es_el_del_resultado_presidencial_sin_recalcular():
    if not ep.RESULTADO_PRESIDENCIAL.exists():
        print("         (sin el resultado presidencial: se omite)")
        return
    import json
    r = json.loads(ep.RESULTADO_PRESIDENCIAL.read_text(encoding="utf-8"))["resultados"]["2022_petro"]["residuos"]
    e = ep.eje_presidencial()
    assert len(e) == 19 and all(abs(e[int(k)] - v) < 1e-12 for k, v in r.items())


# -------------------------------------------------------------------------

if __name__ == "__main__":
    pruebas = [v for k, v in globals().items() if k.startswith("test_")]
    print(f"Eje por partidos — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
