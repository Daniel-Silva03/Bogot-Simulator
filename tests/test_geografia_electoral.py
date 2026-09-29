"""
tests/test_geografia_electoral.py

Pruebas de src/experiments/geografia_electoral.py, y los tres mundos simulados
que el pre-registro (§4.1) exige ANTES de correr sobre el voto real. Ninguna
prueba cruza el voto real con la composición: usan la composición real (si está
en esta máquina) con votos inventados.
Se ejecuta directo:  python tests/test_geografia_electoral.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.experiments import geografia_electoral as ge

FALLOS = []
SEMILLAS = 200


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


# --- la composición: la real si está, una inventada si no --------------------

def _composicion():
    if ge.RECEPTOR.exists():
        import logging
        logging.disable(logging.WARNING)
        return ge.composicion(), "real"
    rng = np.random.default_rng(0)
    idx = range(1, 21)
    return pd.DataFrame({"x1": rng.uniform(1.3, 4.6, 20), "x2": rng.uniform(0.05, 0.6, 20),
                         "x3": rng.uniform(38, 48, 20)}, index=idx), "inventada"


COMP, ORIGEN = _composicion()
LOCS = sorted(set(COMP.index) - {ge.SUMAPAZ})
X1 = COMP.loc[LOCS, ["x1"]].to_numpy()


def mundo(rng, territorio_sd=0.0, pendiente=-0.15, ruido_sd=0.02, u=None):
    """Proporciones de voto por (año, clave) para los nueve resultados, 19 localidades.

    `territorio_sd` > 0 agrega un efecto de localidad FIJO entre elecciones (el mismo
    `u` para todos los resultados): es la persistencia que P4 busca.
    """
    u = rng.normal(0, territorio_sd, len(LOCS)) if u is None else u
    x = X1[:, 0]
    cols = {}
    for k, (anio, clave) in enumerate(ge.RESULTADOS):
        signo = 1 if k % 2 == 0 else -1             # unos suben con el estrato, otros bajan
        cols[(anio, clave)] = 0.35 + signo * pendiente * (x - x.mean()) + signo * u \
            + rng.normal(0, ruido_sd, len(LOCS))
    df = pd.DataFrame(cols, index=LOCS)
    df.columns = pd.MultiIndex.from_tuples(df.columns)
    return df


# --- estadística -------------------------------------------------------------

def test_composicion_con_sentido():
    assert len(COMP) == 20 and set(COMP.columns) == {"x1", "x2", "x3"}
    assert COMP.x1.between(0, 6).all() and COMP.x2.between(0, 1).all() and COMP.x3.between(18, 90).all()
    if ORIGEN == "real":
        # estrato medio: Chapinero (2) sobre Usme (5), como en cualquier fuente oficial
        assert COMP.loc[2, "x1"] > COMP.loc[5, "x1"] + 1


def test_r2_loo_cerrado_igual_al_bucle():
    rng = np.random.default_rng(1)
    y = rng.normal(size=19)
    X = np.column_stack([X1[:, 0], rng.normal(size=19)])
    press = 0.0
    for i in range(19):
        m = np.arange(19) != i
        A = np.column_stack([np.ones(18), X[m]])
        b, *_ = np.linalg.lstsq(A, y[m], rcond=None)
        press += (y[i] - np.r_[1, X[i]] @ b) ** 2
    assert abs(ge.r2_loo(y, X) - (1 - press / np.sum((y - y.mean()) ** 2))) < 1e-10


def test_residuos_ortogonales():
    y = np.random.default_rng(2).normal(size=19)
    e = ge.residuos(y, X1)
    assert abs(e.sum()) < 1e-10 and abs(e @ X1[:, 0]) < 1e-9


def test_p_de_permutacion_nunca_es_cero():
    y = 2 * X1[:, 0]                                  # relación perfecta
    p = ge.p_perm_r2(y, X1, n=99, rng=np.random.default_rng(3))
    assert p == 1 / 100
    r, pr = ge.persistencia(y, y, n=99, rng=np.random.default_rng(3))
    assert abs(r - 1) < 1e-12 and pr == 1 / 100


# --- los tres mundos de §4.1 --------------------------------------------------

def test_mundo_1_solo_composicion():
    """R²_LOO alto y persistencia cercana a 0."""
    r2, rs = [], []
    for s in range(SEMILLAS):
        rng = np.random.default_rng(100 + s)
        m = mundo(rng)
        r2.append(ge.r2_loo(m[ge.PRINCIPAL], X1))
        a, b = ge.PERSISTENCIA
        rs.append(np.corrcoef(ge.residuos(m[a], X1), ge.residuos(m[b], X1))[0, 1])
    rs = np.array(rs)
    assert np.median(r2) > 0.80, np.median(r2)
    assert abs(rs.mean()) < 0.10 and (rs > 0.5).mean() < 0.05, (rs.mean(), (rs > 0.5).mean())


def test_mundo_2_territorio_estable():
    """Un efecto de localidad fijo entre elecciones: la persistencia lo encuentra."""
    rs = []
    for s in range(SEMILLAS):
        rng = np.random.default_rng(300 + s)
        m = mundo(rng, territorio_sd=0.05)
        a, b = ge.PERSISTENCIA
        rs.append(np.corrcoef(ge.residuos(m[a], X1), ge.residuos(m[b], X1))[0, 1])
    assert (np.array(rs) > 0.5).mean() > 0.85, (np.array(rs) > 0.5).mean()


def test_mundo_3_sin_relacion():
    """El voto no depende de la composición: la permutación se equivoca ~5 %, no más."""
    falsos, r2 = 0, []
    for s in range(SEMILLAS):
        rng = np.random.default_rng(500 + s)
        y = rng.normal(0.35, 0.1, len(LOCS))
        r2.append(ge.r2_loo(y, X1))
        falsos += ge.p_perm_r2(y, X1, n=199, rng=rng) < 0.05
    tasa = falsos / SEMILLAS
    assert 0.01 <= tasa <= 0.10, tasa
    assert np.median(r2) <= 0, np.median(r2)


# --- el análisis completo y la regla ------------------------------------------

def _analisis(m, razon=None):
    return ge.analizar(m, COMP, razon, n_perm=199)


def test_regla_a_en_el_mundo_de_composicion():
    v = ge.evaluar(_analisis(mundo(np.random.default_rng(7), ruido_sd=0.01)))
    assert v["regla"].startswith("A"), v["regla"]
    assert v["predicciones"]["P1"]["se_cumple"] and not v["predicciones"]["P4"]["se_cumple"]


def test_regla_b_con_territorio_estable():
    rng = np.random.default_rng(8)
    razon = pd.Series(rng.uniform(0.7, 1.5, 20), index=range(1, 21))   # sin relación
    v = ge.evaluar(_analisis(mundo(rng, territorio_sd=0.06, ruido_sd=0.01), razon))
    assert v["regla"].startswith("B"), v["regla"]
    assert v["predicciones"]["P4"]["interpretable_como_territorio"]


def test_la_inscripcion_bloquea_la_lectura_b():
    """Enmienda 1: si el 'territorio' es el patrón de inscripción, no es territorio."""
    rng = np.random.default_rng(9)
    u = rng.normal(0, 0.06, len(LOCS))
    razon = pd.Series(1.0, index=range(1, 21))
    razon.loc[LOCS] = 1 + u                            # la inscripción ES el efecto
    v = ge.evaluar(_analisis(mundo(rng, u=u, ruido_sd=0.01), razon))
    assert v["inscripcion_fuerte"] and v["regla"].startswith("Intermedio (enmienda 1)"), v["regla"]
    assert not v["predicciones"]["P4"]["interpretable_como_territorio"]


def test_regla_c_sin_relacion():
    rng = np.random.default_rng(10)
    m = mundo(rng, pendiente=0.0, ruido_sd=0.1)
    v = ge.evaluar(_analisis(m))
    assert v["regla"].startswith("C"), v["regla"]
    assert not v["predicciones"]["P5"]["se_cumple"]


def test_se_exigen_19_localidades():
    m = mundo(np.random.default_rng(11)).drop(index=LOCS[0])
    try:
        _analisis(m)
    except ge.GeografiaError:
        return
    raise AssertionError("corrió con 18 localidades")


def test_sumapaz_se_predice_sin_ajustarse():
    m = mundo(np.random.default_rng(12))
    m.loc[ge.SUMAPAZ] = 0.99                             # valor extremo: no debe mover el ajuste
    a = ge.analizar(m, COMP, None, n_perm=19, sumapaz=COMP.loc[ge.SUMAPAZ])
    b = ge.analizar(m.drop(index=ge.SUMAPAZ), COMP, None, n_perm=19)
    assert a["resultados"] == b["resultados"] and a["sumapaz"]["observado"] == 0.99


# --- datos: preparación, sin cruzar ------------------------------------------

def test_proporciones_sin_zonas_especiales_y_sobre_votos_candidatos():
    votos = pd.DataFrame({
        "anio": 2022, "zona": [1, 1, 1, 90], "cod_loc": [1, 1, 1, None],
        "clave": ["petro", "gutierrez", "blanco", "petro"],
        "tipo": ["candidato", "candidato", "blanco", "candidato"], "votos": [60, 40, 10, 5]})
    zonas = pd.DataFrame({"anio": 2022, "zona": [1, 90], "votos_candidatos": [100, 5]})
    p = ge.proporciones(votos, zonas)
    assert list(p.index) == [1] and p.loc[1, (2022, "petro")] == 0.6


def test_los_nueve_resultados_son_los_tres_primeros_de_cada_anio():
    ruta = ge.ELECTORAL / "presidente_1v_localidad.csv"
    if not ruta.exists():
        print("         (sin la tabla electoral: se omite)")
        return
    votos = pd.read_csv(ruta)
    ge.verificar_resultados(votos)
    otro = votos.copy()
    otro.loc[(otro.anio == 2014) & (otro.clave == "penalosa"), "votos"] *= 10
    try:
        ge.verificar_resultados(otro)
    except ge.GeografiaError:
        return
    raise AssertionError("no detectó que los tres primeros cambiaron")


# -------------------------------------------------------------------------

if __name__ == "__main__":
    pruebas = [v for k, v in globals().items() if k.startswith("test_")]
    print(f"Geografía electoral — {len(pruebas)} pruebas (composición {ORIGEN})\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
