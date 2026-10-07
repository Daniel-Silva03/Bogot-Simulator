"""
tests/test_nivel_parecidas_b.py

Pruebas de src/experiments/nivel_parecidas_b.py con modelo simulado: ninguna llama a la API.
Se ejecuta directo:  python tests/test_nivel_parecidas_b.py
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.experiments import experimento9 as e9
from src.experiments import nivel_parecidas_b as nb

FALLOS = []
_tmp = tempfile.TemporaryDirectory()


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def _t():
    filas = []
    for i in range(6):
        filas.append({"id": f"q{i}", "familia": f"f{i // 2}", "ambito": "Bogotá" if i < 2 else "general",
                      "pregunta_pagina": f"¿Pregunta {i}?", "categorias": "1=Sí; 2=No; 99=No sabe",
                      "codigos_favorables": "[1]", "total": 10.0 * (i + 1)})
    return pd.DataFrame(filas)


def _cache(nombre):
    return e9.Cache(Path(_tmp.name) / nombre)


def test_el_prompt_no_trae_resultados_ni_la_propia_familia():
    t = _t()
    u, val = nb.prompt(t, 0)
    assert val == ["q2", "q3", "q4", "q5"] and "q1 |" not in u and "q0 |" not in u
    for x in ("10.0", "30.0", "60.0", "total"):
        assert x not in u, x
    assert "1=Sí*; 2=No" in u and "No sabe" not in u                    # DI-NB1


def test_con_las_candidatas_primero_el_comienzo_es_identico():
    """DI-NB7: mismo comienzo en todas las llamadas; la propia familia no se puede elegir."""
    import pandas as pd
    cand = pd.DataFrame({"id": ["a1", "a2", "b1", "c1"], "familia": ["A", "A", "B", "C"],
                         "pregunta_pagina": ["pa1", "pa2", "pb1", "pc1"],
                         "categorias": ["1=Sí; 2=No"] * 4, "codigos_favorables": ["[1]"] * 4, "total": [1.0] * 4})
    def t(fila):
        return pd.concat([cand[cand.id == fila], cand], ignore_index=True)
    u1, v1 = nb.prompt_fijo(t("a1"), 0)
    u2, v2 = nb.prompt_fijo(t("b1"), 0)
    corte = u1.index("PREGUNTA NUEVA")
    assert u1[:corte] == u2[:corte] and u1.startswith("CANDIDATAS")
    assert set(v1) == {"b1", "c1"} and set(v2) == {"a1", "a2", "c1"}
    assert "No elijas estas candidatas, que son de la misma pregunta: a1, a2" in u1


def test_el_parseo_limpia_ids():
    val = ["a", "b", "c", "d", "e", "f"]
    assert nb.parsear('```json\n{"ids": ["b", "b", "zz", "a"], "razon": "x"}\n```', val) == ["b", "a"]
    assert nb.parsear('{"ids": ["a","b","c","d","e","f"]}', val) == ["a", "b", "c", "d", "e"]
    assert nb.parsear('{"ids": ["zz"]}', val) is None and nb.parsear("no es json", val) is None
    # DI-NB6: si se corrige en la misma respuesta, vale el último JSON con ids válidos
    doble = '{"ids": ["a", "zz"], "razon": "x"}\n\nCorrección: la válida es:\n\n{"ids": ["b", "c"], "razon": "y"}'
    assert nb.parsear(doble, val) == ["b", "c"]
    assert nb.parsear('{"ids": ["a"]} y luego {"ids": ["zz"]}', val) == ["a"]
    assert nb.parsear('{"razon": "sin ids"} {"ids": "a"}', val) is None


def test_la_prediccion_es_la_media_real_de_las_elegidas():
    t = _t()
    p = nb.correr(t, nb.cliente_simulado(t), _cache("sim.json"), "simulado")
    r = p[p.id == "q0"].iloc[0]
    assert r.ids == ["q2", "q3", "q4"] and abs(r.pred - 40.0) < 1e-9 and not r.fallo


def test_si_falla_dos_veces_usa_el_promedio_y_cuenta_fallo():
    t = _t()
    vistos = []

    def roto(modelo, sistema, usuario, temp):
        vistos.append(usuario)
        return "no sé"
    p = nb.correr(t, roto, _cache("roto.json"), "roto", solo=1)
    r = p.iloc[0]
    assert r.fallo and abs(r.pred - t[t.familia != "f0"].total.mean()) < 1e-9
    assert len(vistos) == 2 and "NOTA" in vistos[1]


def test_el_tope_detiene_antes_de_llamar():
    t = _t()
    cache = _cache("tope.json")
    llamadas = []

    def caro(modelo, sistema, usuario, temp):
        llamadas.append(1)
        return {"texto": json.dumps({"ids": ["q2"]}), "uso": {"costo_usd": 0.6}}
    try:
        nb.correr(t, caro, cache, "caro", tope=1.0)
    except nb.TopeAlcanzado:
        pass
    else:
        raise AssertionError("debió detenerse")
    assert len(llamadas) == 2                                            # 0,6 + 0,6 ≥ 1,0: la tercera no se hace


def test_la_cache_evita_volver_a_pagar():
    t = _t()
    cache = _cache("rep.json")
    n = []

    def llamar(modelo, sistema, usuario, temp):
        n.append(1)
        return json.dumps({"ids": ["q2"]})
    nb.correr(t, llamar, cache, "m", solo=2)
    nb.correr(t, llamar, cache, "m", solo=2)
    assert len(n) == 2


def test_deepseek_va_sin_razonar_y_sin_la_etiqueta():
    """DI-NB5."""
    vistos = []
    llamar = nb.enrutar(lambda m, *a: vistos.append(("base", m)) or "{}",
                        lambda m, *a: vistos.append(("sin_razonar", m)) or "{}")
    llamar(nb.MODELOS["deepseek"], "s", "u", 0.0)
    llamar(nb.MODELOS["sonnet"], "s", "u", 0.0)
    assert vistos == [("sin_razonar", "deepseek/deepseek-v4-pro"), ("base", "anthropic/claude-sonnet-5.5")]


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Nivel por preguntas parecidas, parte B — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
