"""
tests/test_puente_sin_base.py

Pruebas de src/experiments/puente_sin_base.py antes de la corrida real
(`PUENTE_SIN_BASE_SPECIFICATION.md` §8). Con un modelo simulado: ninguna llama a la API.
Se ejecuta directo:  python tests/test_puente_sin_base.py
"""

import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import experimento9 as e9
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


ETQ = {str(i): f"e{i}" for i in range(1, 6)}
FICHAS = {c: {"variable": c, "codigo": c, "pregunta": f"¿{c}?", "escala": [1, 2, 3, 4, 5], "etiquetas": ETQ}
          for c in ("C0", "C1")}
FE = sb.ficha_nueva("algo?")


def j(**d):
    return json.dumps(d)


# --- lo pre-registrado -------------------------------------------------------------

def test_el_prompt_es_el_del_preregistro_letra_por_letra():
    """DI-SB1."""
    doc = sb.ESPECIFICACION.read_text(encoding="utf-8")
    bloque = re.search(r"## 2\..*?```\n(.*?)\n```", doc, re.S).group(1)
    assert bloque == sb.SISTEMA_V2, "el prompt del código no es el del pre-registro"


def test_las_30_preguntas_son_las_del_preregistro():
    doc = sb.ESPECIFICACION.read_text(encoding="utf-8")
    assert [c for _, c, _ in sb.PREGUNTAS] == ["A"] * 10 + ["B"] * 10 + ["C"] * 10
    assert len({i for i, _, _ in sb.PREGUNTAS}) == 30
    for i, c, t in sb.PREGUNTAS:
        assert f"| {i} | {c} | {t} |" in doc, i


# --- parsear_v2 (DI-SB2) ----------------------------------------------------------------

def test_acepta_sin_base_y_puentes_con_fuerza():
    r = sb.parsear_v2(j(preguntas=[], sin_base=True, nivel=None, justificacion="x"), FE, FICHAS)
    assert r["sin_base"] and r["preguntas"] == []
    r = sb.parsear_v2(j(preguntas=[{"codigo": "C0", "sentido": "+", "peso": 2}], fuerza="Débil",
                        sin_base=False, nivel=3), FE, FICHAS)
    assert not r["sin_base"] and r["fuerza"] == "debil"


def test_rechaza_lo_que_no_cumple():
    malos = [
        j(preguntas=[{"codigo": "C0", "sentido": "+", "peso": 2}], sin_base=True, nivel=None),    # sin_base con puente
        j(preguntas=[], sin_base=True, nivel=3),                                                  # sin_base con nivel
        j(preguntas=[{"codigo": "C0", "sentido": "+", "peso": 2}], sin_base=False, nivel=3),      # sin fuerza
        j(preguntas=[{"codigo": "C0", "sentido": "+", "peso": 2}], fuerza="enorme", nivel=3),
        j(preguntas=[], sin_base=False, fuerza="media", nivel=3),                                 # vacío sin decir sin_base
        j(preguntas=[], sin_base="sí", nivel=None),
        "no es json",
    ]
    assert all(sb.parsear_v2(m, FE, FICHAS) is None for m in malos)


# --- veredictos (DI-SB3) y regresión (DI-SB4) --------------------------------------------

SIN = {"sin_base": True, "fuerza": None, "preguntas": []}
FUERTE = {"sin_base": False, "fuerza": "fuerte", "preguntas": [{"codigo": "C0", "sentido": "+", "peso": 1}]}
DEBIL = {**FUERTE, "fuerza": "debil"}


def test_el_veredicto_es_la_mayoria_y_una_rota_cuenta_como_debil():
    assert sb.veredicto([SIN, SIN, FUERTE])["sin_base"]
    assert not sb.veredicto([SIN, None, FUERTE])["sin_base"]
    v = sb.veredicto([FUERTE, None, None])
    assert v["rotas"] == 2 and not v["fuerte_o_media"] and v["debil_o_sin_base"]
    assert sb.veredicto([SIN, DEBIL, FUERTE])["debil_o_sin_base"]


def test_en_la_regresion_sin_base_es_un_puente_vacio():
    assert sb.a_puente_original(SIN) is None and sb.a_puente_original(None) is None
    assert sb.a_puente_original(FUERTE) is FUERTE


# --- la regla (§6) ----------------------------------------------------------------------

def _caso(sb_c, sb_a, sb_reg=0, r2=12, fa=10, db=10):
    v30 = {}
    for i, c, _ in sb.PREGUNTAS:
        n = int(i[1:])
        v30[i] = {"sin_base": (c == "C" and n <= sb_c) or (c == "A" and n <= sb_a),
                  "fuerte_o_media": c == "A" and n <= fa, "debil_o_sin_base": c == "B" and n <= db}
    reg = {"veredictos": {f"E{k}": {"sin_base": k < sb_reg} for k in range(12)},
           "p1_personas": {f"E{k}": k < r2 for k in range(12)}}
    return sb.evaluar(v30, reg)


def test_la_regla_lee_cada_caso():
    assert _caso(7, 1)["lectura"] == "adoptar"
    assert _caso(6, 0)["lectura"] == "sin_base_no_confiable"
    assert _caso(10, 2)["lectura"] == "sin_base_no_confiable"
    assert _caso(10, 0, sb_reg=2)["lectura"] == "no_adoptar"
    assert _caso(10, 0, r2=8)["lectura"] == "no_adoptar"


def test_la_fuerza_se_muestra_solo_si_p3_y_no_se_rompio_nada():
    assert _caso(10, 0)["mostrar_fuerza"]
    assert not _caso(10, 0, fa=7)["mostrar_fuerza"]
    assert not _caso(10, 0, db=5)["mostrar_fuerza"]
    assert _caso(3, 0)["mostrar_fuerza"]                      # sin_base no confiable, pero la fuerza sí
    assert not _caso(10, 0, sb_reg=5)["mostrar_fuerza"]


# --- el circuito --------------------------------------------------------------------------

def test_el_circuito_con_el_modelo_simulado_y_la_cache():
    llamadas = {"n": 0}
    sim = sb.modelo_simulado(FICHAS)

    def contar(*a):
        llamadas["n"] += 1
        return sim(*a)
    nuevas = {i: sb.ficha_nueva(t) for i, _, t in sb.PREGUNTAS[:2] + sb.PREGUNTAS[-2:]}
    with tempfile.TemporaryDirectory() as tmp:
        cache = e9.Cache(Path(tmp) / "c.json")
        r = sb.recolectar(nuevas, FICHAS, contar, cache, "simulado")
        assert llamadas["n"] == 12
        assert all(x["sin_base"] for x in r["C10"]) and not any(x["sin_base"] for x in r["A1"])
        sb.recolectar(nuevas, FICHAS, contar, cache, "simulado")
        assert llamadas["n"] == 12


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Puente sin base — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
