"""
tests/test_puente.py

Pruebas de src/experiments/puente.py antes de la corrida real
(`PUENTE_SPECIFICATION.md` §9). Todo con encuestados INVENTADOS y un modelo de
lenguaje simulado: ninguna prueba calcula nada sobre las respuestas reales de la
EPC ni llama a la API.
Se ejecuta directo:  python tests/test_puente.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.experiments import puente as pu

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


ESCALA = [1, 2, 3, 4, 5]
ETQ = {"1": "Muy insatisfecho", "2": "Algo insatisfecho", "3": "Ni lo uno ni lo otro",
       "4": "Algo satisfecho", "5": "Muy satisfecho", "99": "No sabe / No responde"}


def ficha(v):
    return {"variable": v, "codigo": v, "nombre": v, "pregunta": f"¿{v}?", "escala": ESCALA,
            "no_respuesta": [99], "etiquetas": ETQ}


def mundo(semilla, n=1500, n_cat=20, objetivo="suma"):
    """Encuestados inventados: 20 preguntas de catálogo con un factor común y una
    escondida que es la suma de C0 y −C1 (objetivo='suma') o ruido (objetivo='ruido')."""
    rng = np.random.default_rng(semilla)
    loc = rng.integers(1, 20, n)
    efecto_loc = rng.normal(0, 0.6, 20)[loc]
    lat = rng.normal(0, 1, (n, n_cat)) + 0.3 * rng.normal(0, 1, (n, 1)) + efecto_loc[:, None]
    cat = {f"C{i}": np.clip(np.round(3 + lat[:, i]), 1, 5) for i in range(n_cat)}
    if objetivo == "suma":
        y = np.clip(np.round(3 + 0.8 * (lat[:, 0] - lat[:, 1]) / 1.4 + rng.normal(0, 0.5, n)), 1, 5)
    else:
        y = np.clip(np.round(3 + rng.normal(0, 1, n)), 1, 5)
    df = pd.DataFrame({**cat, "Y": y, "peso": rng.uniform(0.5, 2, n), "cod_loc": loc,
                       "sexo": rng.choice(["M", "F"], n), "edad_tramo": rng.integers(0, 5, n),
                       "estrato": rng.integers(1, 7, n), "educ_h": rng.integers(0, 4, n)})
    fp = {f"C{i}": ficha(f"C{i}") for i in range(n_cat)}
    fe = {"Y": ficha("Y")}
    return df, fp, fe


def correr(df, fp, fe, puentes, n_azar=100):
    datos = pu.Datos(df, fp, fe)
    crudos = {v: (df[v].to_numpy(float), df[v].isin(ESCALA).to_numpy()) for v in fp}
    a = pu.analizar(datos, fe, fp, {"Y": puentes}, crudos, n_azar=n_azar)
    return a["por_pregunta"]["Y"]


BUENO = {"preguntas": [{"codigo": "C0", "sentido": "+", "peso": 3}, {"codigo": "C1", "sentido": "-", "peso": 3}],
         "nivel": 3.0, "justificacion": ""}


# --- el mundo donde el puente correcto existe ------------------------------------

def test_el_puente_correcto_le_gana_a_la_demografia_y_al_azar():
    df, fp, fe = mundo(1)
    p = correr(df, fp, fe, [BUENO] * 3)
    assert p["rho_ind"] > p["azar"]["rho_ind_p95"] and p["rho_ind"] > p["demografia"]["rho_ind"], p
    assert p["r_loc"] > p["demografia"]["r_loc"], p


def test_en_el_mundo_de_ruido_nada_gana():
    df, fp, fe = mundo(2, objetivo="ruido")
    p = correr(df, fp, fe, [BUENO] * 3)
    assert not (p["rho_ind"] > p["azar"]["rho_ind_p95"] and p["rho_ind"] > 0.1), p


def test_el_sentido_equivocado_da_rho_negativo():
    df, fp, fe = mundo(3)
    malo = {**BUENO, "preguntas": [{"codigo": "C0", "sentido": "-", "peso": 3}, {"codigo": "C1", "sentido": "+", "peso": 3}]}
    assert correr(df, fp, fe, [malo] * 3)["rho_ind"] < 0


def test_una_respuesta_rota_cuenta_como_puente_vacio():
    """DI-PU3."""
    df, fp, fe = mundo(4)
    p = correr(df, fp, fe, [None, None, None])
    assert p["rho_ind"] == 0 and p["r_loc"] == 0 and p["e_nivel"] == 1 and p["respuestas_validas"] == 0


def test_la_mediana_de_tres_llamadas():
    df, fp, fe = mundo(5)
    p = correr(df, fp, fe, [BUENO, BUENO, None])
    assert p["respuestas_validas"] == 2 and p["rho_ind"] > 0


# --- parsear (DI-PU3) ----------------------------------------------------------------

def test_parsear_acepta_lo_valido_y_rechaza_lo_demas():
    fe, fp = ficha("Y"), {"C0": ficha("C0"), "C1": ficha("C1")}
    ok = json.dumps({"preguntas": [{"codigo": "C0", "sentido": "−", "peso": 2}], "nivel": 2.5})
    assert pu.parsear(ok, fe, fp)["preguntas"][0]["sentido"] == "-"
    malos = [
        "esto no es json",
        json.dumps({"preguntas": [], "nivel": 3}),
        json.dumps({"preguntas": [{"codigo": "C0", "sentido": "+", "peso": 1}] * 6, "nivel": 3}),
        json.dumps({"preguntas": [{"codigo": "Y", "sentido": "+", "peso": 1}], "nivel": 3}),       # la escondida
        json.dumps({"preguntas": [{"codigo": "C9", "sentido": "+", "peso": 1}], "nivel": 3}),
        json.dumps({"preguntas": [{"codigo": "C0", "sentido": "x", "peso": 1}], "nivel": 3}),
        json.dumps({"preguntas": [{"codigo": "C0", "sentido": "+", "peso": 4}], "nivel": 3}),
        json.dumps({"preguntas": [{"codigo": "C0", "sentido": "+", "peso": 1}], "nivel": 7}),
    ]
    assert all(pu.parsear(m, fe, fp) is None for m in malos)


# --- nivel y dirección (DI-PU4) ------------------------------------------------------

def test_la_direccion_sale_de_las_etiquetas():
    assert pu.direccion(ficha("x")) == 1
    inv = {**ficha("x"), "etiquetas": {"1": "Buen camino", "2": "Mal camino"}, "escala": [1, 2]}
    assert pu.direccion(inv) == -1
    assert pu.direccion({**ficha("x"), "etiquetas": {"1": "Desmejoró", "2": "Mejoró"}, "escala": [1, 2]}) == 1
    assert pu.direccion({**ficha("x"), "etiquetas": {"1": "Sí", "2": "No"}, "escala": [1, 2]}) is None


def test_el_nivel_ingenuo_respeta_la_direccion():
    assert pu.nivel_ingenuo(ficha("x"), 0.25) == 2.0
    inv = {**ficha("x"), "etiquetas": {**ETQ, "1": "Muy satisfecho", "5": "Muy insatisfecho"}}
    assert pu.nivel_ingenuo(inv, 0.25) == 4.0
    sin = {**ficha("x"), "etiquetas": {**ETQ, "1": "Sí", "5": "No"}}
    assert pu.nivel_ingenuo(sin, 0.25) == 3.0


# --- la regla (§7) ---------------------------------------------------------------

def _a(c1, c2, c3, c4):
    P = {}
    for i in range(12):
        P[f"V{i}"] = {"rho_ind": 0.5 if i < c1 else 0.0, "azar": {"rho_ind_p95": 0.1},
                      "demografia": {"rho_ind": 0.2, "r_loc": 0.5}, "r_loc": 0.9 if i < c2 else 0.1,
                      "e_nivel": 0.05 if i < c4 else 0.3, "nivel": {"e_ingenuo": 0.1}}
        if i >= c3:
            P[f"V{i}"]["rho_ind"] = -0.1
    return {"por_pregunta": P}


def test_la_regla_lee_cada_caso():
    assert pu.evaluar(_a(12, 12, 12, 12))["lectura_orden"] == "A"
    assert pu.evaluar(_a(9, 7, 12, 12))["lectura_orden"] == "B"
    assert pu.evaluar(_a(8, 12, 12, 12))["lectura_orden"] == "C"
    assert "modelo" in pu.evaluar(_a(12, 12, 12, 8))["regla_nivel"]
    assert "quien pregunta" in pu.evaluar(_a(12, 12, 12, 7))["regla_nivel"]


def test_el_circuito_con_el_modelo_simulado_y_la_cache():
    """recolectar → parsear → caché: la segunda vez no se vuelve a llamar."""
    import tempfile
    from src.experiments import experimento9 as e9
    df, fp, fe = mundo(6)
    llamadas = {"n": 0}
    sim = pu.modelo_simulado(fp)

    def contar(*a):
        llamadas["n"] += 1
        return sim(*a)
    with tempfile.TemporaryDirectory() as tmp:
        cache = e9.Cache(Path(tmp) / "cache.json")
        r, crudas = pu.recolectar(fe, fp, contar, cache, "simulado")
        assert llamadas["n"] == 3 and all(x is not None for x in r["Y"])
        pu.recolectar(fe, fp, contar, cache, "simulado")
        assert llamadas["n"] == 3


def test_el_catalogo_real_tiene_91_preguntas_y_las_12_escondidas():
    """Solo las fichas (metadatos del archivo), ninguna respuesta."""
    if not pu.CATALOGO.exists():
        print("         (sin el catálogo en esta máquina: se omite)")
        return
    e, p = pu.cargar_fichas()
    assert len(p) == 91 and set(e) == set(pu.ESCONDIDAS) and not set(e) & set(p)


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Puente — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
