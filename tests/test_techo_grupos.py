"""
tests/test_techo_grupos.py

Pruebas de src/experiments/techo_grupos.py con datos inventados: ninguna lee el banco.
Se ejecuta directo:  python tests/test_techo_grupos.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from src.experiments import techo_grupos as tg

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def _pregunta(rng, n, efecto):
    """Una encuesta inventada: el estrato sube la probabilidad de responder favorable en `efecto` por nivel."""
    estrato = rng.choice(["1", "2", "3", "4", "5-6"], n)
    nivel = np.array([["1", "2", "3", "4", "5-6"].index(e) for e in estrato])
    fav = (rng.random(n) < 0.3 + efecto * nivel).astype(float)
    return {"id": "x", "fav": fav, "ok": np.ones(n, bool), "w": np.ones(n),
            "sexo": rng.choice(["Hombres", "Mujeres"], n), "edad": rng.choice(["18-25", "56+"], n), "estrato": estrato,
            "etq": {"sexo": ["Hombres", "Mujeres"], "edad": ["18-25", "56+"], "estrato": ["1", "2", "3", "4", "5-6"]}}


def test_la_probabilidad_del_oraculo_va_de_azar_a_certeza():
    assert tg.p_orden_real(0.0, 4.0, 1.0) == 0.5
    assert tg.p_orden_real(3.0, 0.0, 1.0) == 0.5                 # sin diferencias reales, el orden es azar
    assert tg.p_orden_real(3.0, 100.0, 1.0) > tg.p_orden_real(3.0, 1.0, 1.0) > 0.9
    assert tg.p_orden_real(2.0, 4.0, 2.03) < tg.p_orden_real(2.0, 4.0, 1.0)     # más ruido, menos certeza


def test_el_oraculo_da_casi_uno_con_diferencias_grandes_y_casi_azar_sin_ellas():
    def res(p, n=2000):
        g = {"1": p[0], "2": p[1], "3": p[2]}
        b = {k: n for k in g}
        r = {"grupos": {"sexo": {}, "edad": {}, "estrato": g}, "bases": {"sexo": {}, "edad": {}, "estrato": b}}
        r["pares_claros"] = [list(x) for x in tg.br.pares_claros(r)]
        return r
    grandes = {str(i): res([20 + i % 3, 50, 80 - i % 2]) for i in range(30)}
    assert tg.oraculo(grandes, 1.0)["techo"] > 0.99
    rng = np.random.default_rng(1)
    ruido = {str(i): res(list(50 + rng.normal(0, 1.1, 3))) for i in range(300)}       # solo ruido de muestra
    o = tg.oraculo(ruido, 1.0)
    assert o["pares"] > 0 and o["techo"] < 0.75, o


def test_la_mitad_respeta_los_conglomerados():
    psu = np.repeat(np.arange(50), 4)
    m = tg.sortear_mitad(psu, np.random.default_rng(0))
    assert all(len(set(m[psu == c])) == 1 for c in range(50)) and 0 < m.sum() < len(m)


def test_la_replica_acierta_casi_todo_con_efecto_fuerte_y_azar_sin_efecto():
    rng = np.random.default_rng(2)
    fuerte = [_pregunta(rng, 4000, 0.12) for _ in range(5)]
    mitad = tg.sortear_mitad(np.arange(4000), rng)
    ac, pa = tg.replica(fuerte, mitad)
    assert pa > 0 and ac / pa > 0.95, (ac, pa)
    nulo = [_pregunta(rng, 4000, 0.0) for _ in range(40)]
    ac, pa = tg.replica(nulo, mitad)
    assert pa > 0 and 0.25 < ac / pa < 0.75, (ac, pa)              # pares claros por azar: la otra mitad no los repite


def test_un_empate_en_la_otra_mitad_cuenta_como_fallo():
    q = {"id": "e", "fav": np.array([1., 1., 0., 0., 1., 0., 1., 0.] * 50), "ok": np.ones(400, bool), "w": np.ones(400),
         "sexo": np.array(["Hombres"] * 400), "edad": np.array(["18-25"] * 400),
         "estrato": np.array(["1", "1", "2", "2", "1", "2", "2", "1"] * 50),
         "etq": {"sexo": ["Hombres"], "edad": ["18-25"], "estrato": ["1", "2"]}}
    a = np.zeros(400, bool); a[:200] = True                           # en A: estrato 1 al 75 %, 2 al 25 % (claro)
    q["estrato"][200:] = np.repeat(["1", "2"], 100)                     # en B: los dos al 50 % (empate)
    q["fav"][200:] = np.tile([1., 0.], 100)
    ac, pa = tg.replica([q], a)
    assert pa == 1 and ac == 0, (ac, pa)


def test_la_lectura_es_la_pre_registrada():
    assert tg.lectura(0.80) == "A" and tg.lectura(0.7999) == "B" and tg.lectura(0.70) == "B" and tg.lectura(0.69) == "C"


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Techo de los grupos — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
