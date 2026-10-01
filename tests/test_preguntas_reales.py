"""
tests/test_preguntas_reales.py

Pruebas de src/experiments/preguntas_reales.py antes de la corrida real
(`PREGUNTAS_REALES_NUEVAS_SPECIFICATION.md` §9). Con agentes inventados y un modelo
simulado: ninguna llama a la API ni le hace las preguntas al simulador real.
Se ejecuta directo:  python tests/test_preguntas_reales.py
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.experiments import experimento9 as e9
from src.experiments import preguntas_reales as pr
from src.experiments import puente as pu
from src.experiments import puente_sin_base as sb

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


DOC = pr.ESPECIFICACION.read_text(encoding="utf-8")


def _num(x):
    return f"{x:.1f}".replace(".", ",")


# --- lo pre-registrado -------------------------------------------------------------

def test_los_pares_claros_son_los_24_del_preregistro():
    m, c = pr.pares_claros(pr.REAL["metro"]), pr.pares_claros(pr.REAL["corredor"])
    assert (len(m), len(c)) == (11, 13)
    assert ("sexo", "Mujeres", "Hombres") in m and ("estrato", "5-6", "3") in m and ("estrato", "1", "2") in m
    assert ("estrato", "1", "5-6") in c and ("edad", "35-54", "55+") in c and ("estrato", "3", "4") in c
    assert "son **24**" in DOC


def test_las_cifras_reales_son_las_del_preregistro():
    for q, col in (("metro", 0), ("corredor", 1)):
        r = pr.REAL[q]
        assert _num(r["total"]) in DOC
        fila = " / ".join(_num(r["estrato"][k]) for k in ("1", "2", "3", "4", "5-6"))
        assert fila in DOC, (q, fila)
        fila = " / ".join(_num(r["edad"][k]) for k in ("18-24", "25-34", "35-54", "55+"))
        assert fila in DOC, (q, fila)
    for c, nombre in pr.LOCALIDADES.items():
        assert f"| {nombre} | {_num(pr.REAL_LOC['metro'][c])} | {_num(pr.REAL_LOC['corredor'][c])} |" in DOC, nombre


def test_las_13_localidades_y_sus_codigos():
    assert len(pr.LOCALIDADES) == 13 and set(pr.LOCALIDADES) == set(pr.REAL_LOC["metro"]) == set(pr.REAL_LOC["corredor"])
    assert pr.LOCALIDADES[11] == "Suba" and pr.LOCALIDADES[19] == "Ciudad Bolívar" and pr.LOCALIDADES[16] == "Puente Aranda"


# --- grupos e índices (DI-PR2, DI-PR3) -------------------------------------------------

def test_los_grupos_usan_los_cortes_de_la_encuesta_real():
    ag = pd.DataFrame({"edad": [18, 24, 25, 34, 35, 54, 55, 90], "estrato": [0, 1, 2, 3, 4, 5, 6, 2],
                       "sexo": ["M", "F"] * 4})
    g = pr.grupos(ag)
    assert list(g["edad"]) == ["18-24", "18-24", "25-34", "25-34", "35-54", "35-54", "55+", "55+"]
    assert pd.isna(g["estrato"][0]) and list(g["estrato"][1:]) == ["1", "2", "3", "4", "5-6", "5-6", "2"]   # estrato 0 no entra
    assert list(g["sexo"][:2]) == ["Hombres", "Mujeres"]


def test_la_concordancia_cuenta_los_pares_bien_ordenados_y_el_empate_falla():
    ix = {"sexo": {"Hombres": 0.1, "Mujeres": -0.1}, "edad": {"18-24": 0.0, "55+": 0.0}}
    pares = [("sexo", "Hombres", "Mujeres"), ("sexo", "Mujeres", "Hombres"), ("edad", "18-24", "55+")]
    assert pr.concordancia(ix, pares) == 1 / 3


def test_un_puntaje_que_sigue_al_estrato_acierta_el_corredor():
    """Mundo inventado: más apoyo en estratos bajos, en jóvenes y en mujeres, como el Corredor real."""
    rng = np.random.default_rng(1)
    n = 20000
    ag = pd.DataFrame({"edad": rng.integers(18, 80, n), "estrato": rng.integers(1, 7, n), "sexo": rng.choice(["M", "F"], n)})
    s = -ag.estrato.to_numpy() - 0.05 * ag.edad.to_numpy() + 0.5 * (ag.sexo == "F").to_numpy() + rng.normal(0, 0.3, n)
    ix = pr.indices(s, np.ones(n), pr.grupos(ag))
    assert pr.concordancia(ix, pr.pares_claros(pr.REAL["corredor"])) == 1.0
    assert pr.concordancia(pr.indices(-s, np.ones(n), pr.grupos(ag)), pr.pares_claros(pr.REAL["corredor"])) == 0.0


# --- el puente como en la página (DI-PR1) -------------------------------------------------

CAT = {c: {"variable": c, "codigo": c, "pregunta": f"¿{c}?", "escala": [1, 2, 3, 4, 5],
           "etiquetas": {str(i): f"e{i}" for i in range(1, 6)}} for c in ("C0", "C1")}
PUENTE = {"preguntas": [{"codigo": "C0", "sentido": "+", "peso": 2}], "nivel": 3.5, "justificacion": "x"}


def test_con_sin_base_se_pide_el_puente_de_siempre_y_queda_debil():
    vistos = []

    def llamar(modelo, sistema, usuario, temp):
        vistos.append(sistema)
        if sistema == sb.SISTEMA_V2:
            return json.dumps({"preguntas": [], "sin_base": True, "nivel": None})
        return json.dumps(PUENTE)
    with tempfile.TemporaryDirectory() as tmp:
        r, re = pr.pedir_puente(llamar, e9.Cache(Path(tmp) / "c.json"), "m", sb.ficha_nueva("x?"), CAT, 0)
    assert vistos == [sb.SISTEMA_V2, pu.SISTEMA] and re and r["fuerza"] == "debil"


def test_con_un_puente_v2_valido_no_hay_reintento():
    def llamar(modelo, sistema, usuario, temp):
        return json.dumps({**PUENTE, "fuerza": "fuerte", "sin_base": False})
    with tempfile.TemporaryDirectory() as tmp:
        r, re = pr.pedir_puente(llamar, e9.Cache(Path(tmp) / "c.json"), "m", sb.ficha_nueva("x?"), CAT, 0)
    assert not re and r["fuerza"] == "fuerte"


# --- la regla (§6, §7) --------------------------------------------------------------------

def _por(cm, cc, azar=0.5, nm=3.4, nc=3.2, rm=0.2, rc=0.3):
    return {"metro": {"n_pares": 11, "concordancias": [cm] * 3, "azar": [azar] * 200, "nivel": nm, "r_loc": rm},
            "corredor": {"n_pares": 13, "concordancias": [cc] * 3, "azar": [azar] * 200, "nivel": nc, "r_loc": rc}}


def test_la_regla_lee_cada_caso():
    ok = pr.evaluar(_por(9 / 11, 10 / 13))
    assert ok["predicciones"]["P1"]["se_cumple"] and ok["predicciones"]["P1"]["aciertos"] == 19 and "acertó" in ok["regla"]
    assert not pr.evaluar(_por(7 / 11, 9 / 13))["predicciones"]["P1"]["se_cumple"]          # 16 de 24 < 0,70
    assert not pr.evaluar(_por(1.0, 1.0, azar=1.0))["predicciones"]["P1"]["se_cumple"]      # no le gana al azar
    assert "deja de mostrar" in pr.evaluar(_por(0.5, 0.5))["regla"]


def test_p3_y_p4_se_reportan():
    p = pr.evaluar(_por(1, 1))["predicciones"]
    assert p["P3"]["se_cumple"] and not p["P4"]["ambas_mayores_a_0_5"]
    assert not pr.evaluar(_por(1, 1, nm=3.1, nc=3.3))["predicciones"]["P3"]["se_cumple"]   # el metro debe ir arriba


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Preguntas reales nuevas — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
