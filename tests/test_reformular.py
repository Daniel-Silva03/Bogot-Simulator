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


def test_la_version_2_lee_el_voto_y_exige_sus_candidatos():
    """REFORMULACION_VOTO §1."""
    cat = rf.cargar_catalogo()
    ok = rf.parsear_v2('{"alcance":"voto","tipo":"segunda","candidatos":["Iván Cepeda","Paloma Valencia"],'
                       '"reformulada":"¿Por quién votaría en una segunda vuelta?"}', cat)
    assert ok["alcance"] == "voto" and ok["tipo"] == "segunda" and len(ok["candidatos"]) == 2
    assert rf.parsear_v2('{"alcance":"voto","tipo":"segunda","candidatos":["Iván Cepeda"],"reformulada":"¿x?"}', cat) is None
    assert rf.parsear_v2('{"alcance":"voto","tipo":"consulta","candidatos":["X"],"reformulada":"¿x?"}', cat) is None
    assert rf.parsear_v2('{"alcance":"fuera","codigo":null,"reformulada":"","razon":"x"}', cat)["alcance"] == "fuera"


def test_la_prueba_de_voto_y_su_regla():
    pv = rf.PRUEBA_VOTO
    assert len(pv) == 40 and sum(x[1] == "voto" for x in pv) == 13 and sum(x[1] == "fuera" for x in pv) == 9
    perfecto = [None if a == "fuera" and False else
                {"alcance": a, "codigo": c, "tipo": t, "candidatos": cs or []} for _, a, c, t, cs in pv]
    assert rf.evaluar_voto(perfecto)["pasa"]
    un_falso = list(perfecto)
    un_falso[0] = {**un_falso[0], "alcance": "voto", "tipo": "primera", "candidatos": ["X"]}   # una de opinión como voto
    assert not rf.evaluar_voto(un_falso)["criterios"]["R6"]["se_cumple"]
    assert rf.nombra(["Abelardo De La Espriella Otero"], "Abelardo de la Espriella")


def test_la_version_4_solo_agrega_el_matiz_y_su_prueba_es_la_del_documento():
    """REFORMULACION_MATIZ §1 y §2."""
    assert rf.SISTEMA_V4.replace(rf.SISTEMA_V3, "") != "" and len(rf.SISTEMA_V4) > len(rf.SISTEMA_V3)
    i = rf.SISTEMA_V4.index("También es \"catalogo\"")
    assert rf.SISTEMA_V4[:i].rstrip() in rf.SISTEMA_V3 and rf.SISTEMA_V4.replace(rf.SISTEMA_V4[i:].split("\n")[0], "").replace(
        "Da su código. \n", "Da su código.\n") == rf.SISTEMA_V3 and "caminando" not in rf.SISTEMA_V4         # el ejemplo no es de la prueba
    doc = (Path(__file__).resolve().parents[1] / "docs" / "REFORMULACION_MATIZ_SPECIFICATION.md").read_text(encoding="utf-8")
    cat = rf.cargar_catalogo()
    assert len(rf.PRUEBA_MATIZ) == 14 and sum(a == "catalogo" for _, a, _ in rf.PRUEBA_MATIZ) == 8
    for p, _, c in rf.PRUEBA_MATIZ:
        assert p in doc, p
        assert c is None or (c in cat and f"`{c}`" in doc)
    assert not {p for p, *_ in rf.PRUEBA_MATIZ} & {p for p, *_ in rf.PRUEBA_VOTO_V3}


def test_la_regla_del_matiz():
    perfecto = [{"alcance": a, "codigo": c} for _, a, c in rf.PRUEBA_MATIZ]
    assert rf.evaluar_matiz(perfecto)["pasa"]
    una_cercana_al_catalogo = list(perfecto)
    una_cercana_al_catalogo[8] = {"alcance": "catalogo", "codigo": "VS10"}            # TransMilenio como VS10
    assert not rf.evaluar_matiz(una_cercana_al_catalogo)["criterios"]["R8"]["se_cumple"]
    dos_fallan = list(perfecto)
    dos_fallan[0] = dos_fallan[1] = {"alcance": "nueva", "codigo": None}
    assert not rf.evaluar_matiz(dos_fallan)["criterios"]["R7"]["se_cumple"]


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
