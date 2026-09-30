"""
tests/test_reformular.py

Pruebas de src/consulta/reformular.py (`REFORMULACION_SPECIFICATION.md`). Con un
modelo simulado: ninguna llama a la API.
Se ejecuta directo:  python tests/test_reformular.py
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.consulta import reformular as rf
from src.experiments import experimento9 as e9

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


CAT = {"VS8": {"variable": "VS8", "pregunta": "¿Qué tan seguro se siente en su barrio?", "escala": [1, 2, 3, 4, 5],
               "etiquetas": {"1": "Nada seguro", "5": "Muy seguro", "99": "No sabe"}}}
ESC = ["Muy en desacuerdo", "En desacuerdo", "Ni lo uno ni lo otro", "De acuerdo", "Muy de acuerdo"]


def j(**d):
    return json.dumps(d)


def test_parsear_acepta_los_tres_alcances():
    assert rf.parsear(j(alcance="catalogo", codigo="VS8", reformulada="", escala=None, razon="x"), CAT)["codigo"] == "VS8"
    assert rf.parsear(j(alcance="nueva", codigo=None, reformulada="¿Qué tan de acuerdo…?", escala=ESC), CAT)["alcance"] == "nueva"
    assert rf.parsear(j(alcance="fuera", codigo=None, reformulada="", razon="un dato"), CAT)["alcance"] == "fuera"


def test_parsear_rechaza_lo_que_no_cumple():
    """DI-RF2."""
    malos = ["no es json",
             j(alcance="otra", codigo=None),
             j(alcance="catalogo", codigo="ZZ9"),
             j(alcance="catalogo", codigo=None),
             j(alcance="nueva", reformulada="", escala=ESC),
             j(alcance="nueva", reformulada="x" * 301, escala=ESC),
             j(alcance="nueva", reformulada="¿x?", escala=ESC[:4]),
             j(alcance="nueva", reformulada="¿x?", escala=ESC[:4] + [""])]
    assert all(rf.parsear(m, CAT) is None for m in malos)


def test_una_nueva_no_arrastra_codigo():
    r = rf.parsear(j(alcance="nueva", codigo="VS8", reformulada="¿x?", escala=ESC), CAT)
    assert r["codigo"] is None


def test_el_prompt_lleva_la_pregunta_y_el_catalogo_sin_datos():
    u = rf.prompt("  ¿Cobrar por entrar al centro?  ", CAT)
    assert u.split("\n")[1] == "¿Cobrar por entrar al centro?" and "VS8 |" in u and "No sabe" not in u


def test_la_prueba_es_la_del_documento():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "REFORMULACION_SPECIFICATION.md").read_text(encoding="utf-8")
    assert len(rf.PRUEBA) == 24
    assert [a for _, a, _ in rf.PRUEBA].count("catalogo") == 8 and [a for _, a, _ in rf.PRUEBA].count("fuera") == 6
    for p, _, c in rf.PRUEBA:
        assert p in doc, p
        if c:
            assert f"`{c}`" in doc, c


def test_la_regla_lee_los_criterios():
    perfecto = [{"alcance": a, "codigo": c} for _, a, c in rf.PRUEBA]
    assert rf.evaluar(perfecto)["pasa"]
    # una fuera clasificada como catálogo rompe R3 aunque el resto esté bien
    malo = list(perfecto)
    malo[18] = {"alcance": "catalogo", "codigo": "VS8"}
    assert not rf.evaluar(malo)["criterios"]["R3"]["se_cumple"]
    # dos inválidas rompen R4
    assert not rf.evaluar([None, None] + perfecto[2:])["criterios"]["R4"]["se_cumple"]


def test_el_circuito_simulado_pasa_y_usa_la_cache():
    if not rf.CATALOGO.exists():
        print("         (sin el catálogo en esta máquina: se omite)")
        return
    cat = rf.cargar_catalogo()
    llamadas = {"n": 0}
    sim = rf.modelo_simulado(cat)

    def contar(*a):
        llamadas["n"] += 1
        return sim(*a)
    with tempfile.TemporaryDirectory() as tmp:
        cache = e9.Cache(Path(tmp) / "c.json")
        rs = [rf.reformular(p, cat, contar, cache, "simulado")[0] for p, _, _ in rf.PRUEBA]
        assert rf.evaluar(rs)["pasa"] and llamadas["n"] == 24
        rf.reformular(rf.PRUEBA[0][0], cat, contar, cache, "simulado")
        assert llamadas["n"] == 24


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Reformulación — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
