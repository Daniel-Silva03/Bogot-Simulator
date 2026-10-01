"""
tests/test_practica_puente.py

Pruebas de src/experiments/practica_puente.py con datos inventados. Ninguna llama a la API.
Se ejecuta directo:  python tests/test_practica_puente.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.experiments import practica_puente as pp
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


def test_la_version_afectados_es_la_actual_mas_un_parrafo():
    a, b = pp.VERSIONES["actual"], pp.VERSIONES["afectados"]
    assert a == sb.SISTEMA_V2 and b.replace(pp.AFECTADOS, "") == a and "QUIÉN" in b


def test_la_ficha_tiene_arriba_lo_de_acuerdo():
    f = pp.ficha("¿Qué tanto confía en X?")
    assert f["escala"] == [1, 2, 3, 4, 5] and "de acuerdo" in f["etiquetas"]["5"] and "desacuerdo" in f["etiquetas"]["1"]


def test_aciertos_e_indices():
    ag = pd.DataFrame({"sexo": ["M", "F"] * 50, "edad": [20, 60] * 50, "estrato": [1, 6] * 50})
    g = pp.grupos_agentes(ag, cortes_cnc=False)
    s = (ag.sexo == "F").to_numpy(float)                                     # las mujeres más de acuerdo
    ix = pp.indices(s, np.ones(100), g, {"sexo": ["Hombres", "Mujeres"], "edad": ["18-25", "56+"]})
    assert pp.aciertos(ix, [("sexo", "Mujeres", "Hombres")]) == 1
    assert pp.aciertos(ix, [("sexo", "Hombres", "Mujeres"), ("estrato", "1", "5-6")]) == 0   # grupo ausente: fallo


def test_el_resumen_junta_todos_los_pares():
    por = {"a": {"ambito": "Bogotá", "pares": 10, "aciertos": [8, 6, 7], "azar": [5, 5], "tono": 6, "r_localidad": [0.5, None, 0.3]},
           "b": {"ambito": "general", "pares": 30, "aciertos": [15, 15, 15], "azar": [15, 15], "tono": 18, "r_localidad": [None] * 3}}
    r = pp.resumen(por)
    assert r["todas"]["pares"] == 40 and r["todas"]["puente"] == 22 / 40 and r["todas"]["tono_general"] == 24 / 40
    assert r["Bogotá"]["r_localidad_mediana"] == 0.4 and r["general"]["r_localidad_mediana"] is None


def test_las_preguntas_son_de_practica_sin_excluidas_y_con_pares():
    if not pp.br.SALIDA.exists():
        print("         (sin los resultados reales en esta máquina: se omite)")
        return
    qs = pp.preguntas()
    s = pd.read_csv(pp.ba.SALIDA / "sorteo.csv")
    ids = {q["id"] for q in qs}
    assert ids <= set(s[s.conjunto == "practica"].id) and not ids & set(s[s.conjunto == "guardado"].id)
    assert all(not q["real"].get("excluida") and q["real"]["pares_claros"] for q in qs)


def test_en_paralelo_da_lo_mismo_que_una_por_una_y_la_cache_no_se_pisa():
    """DI-PP6."""
    import json, tempfile, time
    from src.experiments import experimento9 as e9
    cat = {f"C{i}": {"variable": f"C{i}", "codigo": f"C{i}", "pregunta": f"¿C{i}?", "escala": [1, 2, 3, 4, 5],
                     "etiquetas": {str(k): f"e{k}" for k in range(1, 6)}} for i in range(4)}
    sim = pp.modelo_simulado(cat)

    def lento(*a):
        time.sleep(0.01)
        return sim(*a)
    qs = [{"id": f"Q{i}", "pregunta_pagina": f"¿Pregunta {i}?"} for i in range(12)]
    with tempfile.TemporaryDirectory() as tmp:
        c1, c5 = e9.Cache(Path(tmp) / "a.json"), e9.Cache(Path(tmp) / "b.json")
        r1, _ = pp.recolectar(qs, lento, c1, "m", pp.VERSIONES["actual"], cat, 1)
        r5, _ = pp.recolectar(qs, lento, c5, "m", pp.VERSIONES["actual"], cat, 5)
        assert r1 == r5
        assert len(json.loads((Path(tmp) / "b.json").read_text(encoding="utf-8"))) == 36   # 12 × 3, nada pisado


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Práctica del puente — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
