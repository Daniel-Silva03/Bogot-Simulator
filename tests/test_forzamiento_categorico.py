"""
tests/test_forzamiento_categorico.py

Pruebas del forzamiento categórico (DI-G1..DI-G5).
Se ejecuta directo:  python3 tests/test_forzamiento_categorico.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from src.opinion.forzamiento_categorico import (
    ForzamientoError, ForzamientoInfactible, distribucion_de, forzar, ladeo,
    momentos, rango_de_sd, repartir, transporte,
)

K = np.array([1.0, 2, 3, 4, 5])
P = np.array([0.20, 0.20, 0.25, 0.25, 0.10])
FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


# --- los dos métodos aciertan los momentos ---------------------------------

def test_el_ladeo_acierta_los_momentos():
    for m, s in ((2.5, 1.0), (3.5, 1.1), (2.0, 0.9), (4.0, 0.8)):
        r = ladeo(P, K, m, s)
        assert abs(r.err_media) < 1e-6, f"media {m},{s}: err {r.err_media:.2e}"
        assert abs(r.err_sd) < 1e-6, f"sd {m},{s}: err {r.err_sd:.2e}"


def test_el_transporte_acierta_los_momentos():
    for m, s in ((2.5, 1.0), (3.5, 1.1), (2.0, 0.9)):
        r = transporte(P, K, m, s)
        assert abs(r.err_media) < 1e-6
        assert abs(r.err_sd) < 1e-6


def test_no_se_sale_de_la_grilla():
    """Lo que motiva todo el módulo: el soporte no se mueve."""
    for metodo in ("ladeo", "transporte"):
        a = np.repeat(K, [200, 200, 250, 250, 100]).astype(float)
        nuevo, _ = forzar(a, K, 2.2, 1.0, metodo=metodo)
        assert set(np.unique(nuevo)) <= set(K), f"{metodo} salió de la grilla"


# --- propiedades que justifican elegir el ladeo (DI-G1) --------------------

def test_el_ladeo_preserva_los_ceros():
    p = np.array([0.0, 0.3, 0.4, 0.3, 0.0])
    r = ladeo(p, K, 3.2, 0.7)
    assert r.q[0] == 0.0 and r.q[-1] == 0.0, "una categoría vacía no puede llenarse sola"


def test_subir_el_nivel_no_engorda_la_categoria_mas_baja():
    """Orden estocástico: con lambda2 pequeño el ladeo es monótono."""
    m0, s0 = momentos(P, K)
    r = ladeo(P, K, m0 + 0.4, s0)
    assert r.q[0] < P[0], f"subió el nivel y la categoría 1 creció: {P[0]:.4f} -> {r.q[0]:.4f}"
    assert r.q[-1] > P[-1]


def test_si_los_momentos_no_cambian_la_distribucion_tampoco():
    m0, s0 = momentos(P, K)
    for metodo, f in (("ladeo", ladeo), ("transporte", transporte)):
        r = f(P, K, m0, s0)
        assert np.allclose(r.q, P, atol=1e-6), f"{metodo} movió una distribución que ya cumplía"


def test_el_transporte_mueve_menos_masa_que_el_ladeo():
    """Cada método optimiza lo suyo: esto verifica que hacen cosas distintas."""
    def w1(q):
        return float(np.abs(np.cumsum(P)[:-1] - np.cumsum(q)[:-1]).sum())
    t = transporte(P, K, 2.2, 1.05)
    l = ladeo(P, K, 2.2, 1.05)
    assert w1(t.q) <= w1(l.q) + 1e-9, "el transporte tiene que mover la menor masa posible"


# --- factibilidad (DI-G4) --------------------------------------------------

def test_la_sd_imposible_se_rechaza_con_el_rango():
    lo, hi = rango_de_sd(K, 3.0)
    try:
        ladeo(P, K, 3.0, hi + 0.5)
    except ForzamientoInfactible as e:
        assert "alcanzable" in str(e), "el mensaje tiene que decir el rango"
    else:
        raise AssertionError("debería ser infactible")


def test_proyectar_deja_constancia():
    lo, hi = rango_de_sd(K, 3.0)
    r = ladeo(P, K, 3.0, hi + 0.5, proyectar=True)
    assert r.notas and "infactible" in r.notas[0]
    assert abs(r.sd - hi) < 1e-3, f"debería quedar en el máximo alcanzable {hi:.4f}, dio {r.sd:.4f}"


def test_la_media_fuera_de_la_grilla_se_rechaza():
    try:
        ladeo(P, K, 6.0, 0.5)
    except ForzamientoInfactible:
        pass
    else:
        raise AssertionError("una media de 6 en una escala 1-5 no existe")


def test_el_rango_de_sd_es_coherente():
    for m in (1.5, 2.5, 3.0, 4.5):
        lo, hi = rango_de_sd(K, m)
        assert 0 <= lo <= hi, f"rango incoherente en media {m}"
    # en el extremo de la escala no cabe ninguna dispersión
    lo, hi = rango_de_sd(K, 1.0)
    assert hi < 1e-9, "con la media en el mínimo, la única distribución posible es degenerada"


# --- reparto de agentes (DI-G3) -------------------------------------------

def test_el_reparto_reproduce_la_distribucion():
    a = np.repeat(K, [200, 200, 250, 250, 100]).astype(float)
    r = ladeo(distribucion_de(a, K), K, 2.4, 1.05)
    nuevo = repartir(a, r)
    obtenida = distribucion_de(nuevo, K)
    assert np.abs(obtenida - r.q).max() < 1.5 / len(a), \
        f"el reparto se desvía más de un agente: {np.abs(obtenida - r.q).max():.4f}"


def test_el_reparto_por_rango_preserva_el_orden():
    rng = np.random.default_rng(0)
    a = rng.choice(K, 1000, p=P)
    r = ladeo(distribucion_de(a, K), K, 2.2, 1.05)
    nuevo = repartir(a, r, rng=np.random.default_rng(1))
    # nadie que empezara más abajo puede terminar más arriba que otro que empezó más arriba
    orden = np.argsort(a, kind="stable")
    assert np.all(np.diff(np.sort(nuevo[orden])) >= -1e-12)
    pares = rng.integers(0, len(a), (400, 2))
    for i, j in pares:
        if a[i] < a[j]:
            assert nuevo[i] <= nuevo[j], "el reparto por rango invirtió un par"


def test_el_reparto_no_pierde_ni_inventa_agentes():
    a = np.repeat(K, [10, 20, 30, 25, 15]).astype(float)
    r = ladeo(distribucion_de(a, K), K, 3.1, 1.0)
    assert len(repartir(a, r)) == len(a)


# --- higiene ---------------------------------------------------------------

def test_un_valor_fuera_de_la_grilla_falla_con_un_mensaje_util():
    try:
        distribucion_de([1.0, 2.5, 3.0], K)
    except ForzamientoError as e:
        assert "fuera de la grilla" in str(e) and "forzamiento.py" in str(e), \
            "el mensaje tiene que mandar al módulo continuo"
    else:
        raise AssertionError("2,5 no está en la grilla 1-5")


def test_la_escala_de_la_diferencia_tambien_funciona():
    """La diferencia individual va de -4 a +4 y tiene su propia grilla."""
    kd = np.arange(-4.0, 5.0)
    p = np.array([0.01, 0.02, 0.06, 0.15, 0.45, 0.20, 0.08, 0.02, 0.01])
    r = ladeo(p, kd, 0.30, 1.15)
    assert abs(r.err_media) < 1e-6 and abs(r.err_sd) < 1e-6


# -------------------------------------------------------------------------

if __name__ == "__main__":
    pruebas = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"Forzamiento categórico — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
