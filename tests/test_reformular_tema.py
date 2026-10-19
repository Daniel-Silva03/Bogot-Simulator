"""
tests/test_reformular_tema.py

Pruebas de la versión 6 de la reformulación (`REFORMULACION_TEMA_SPECIFICATION.md`). No llaman a la API.
Se ejecuta directo:  python tests/test_reformular_tema.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.consulta import reformular as rf

FALLOS = []
CAT = {"GG3_GALAN": {"variable": "GG3_GALAN"}}
#: sha256 de SISTEMA_V5 en 1788634, antes de la versión 6 y de la llamada aparte
HUELLA_V5 = "3adfce3e69f46fb2"


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_la_v6_es_la_v5_mas_el_tema():
    assert rf.SISTEMA_V6.startswith(rf.SISTEMA_V5.split("Responde SOLO")[0])
    doc = " ".join((Path(__file__).resolve().parents[1] / "docs" / "REFORMULACION_TEMA_SPECIFICATION.md")
                   .read_text(encoding="utf-8").replace("> ", "").replace("\\", "").split())
    parrafo = rf.SISTEMA_V6.split("Responde SOLO")[0][len(rf.SISTEMA_V5.split("Responde SOLO")[0]):]
    for linea in parrafo.strip().splitlines():
        assert " ".join(linea.split()) in doc, linea[:50]


def test_sin_tema_una_nueva_es_invalida():
    base = {"alcance": "nueva", "codigo": None, "reformulada": "¿x?", "escala": ["a", "b", "c", "d", "e"], "razon": ""}
    assert rf.parsear_v3(json.dumps(base), CAT) is None
    assert rf.parsear_v3(json.dumps({**base, "tema": "otra"}), CAT) is None
    assert rf.parsear_v3(json.dumps({**base, "tema": "Politica"}), CAT)["tema"] == "politica"


def test_catalogo_lleva_tema_y_fuera_no():
    r = rf.parsear_v3(json.dumps({"alcance": "catalogo", "codigo": "GG3_GALAN", "tema": "politica", "reformulada": ""}), CAT)
    assert r["codigo"] == "GG3_GALAN" and r["tema"] == "politica"
    f = rf.parsear_v3(json.dumps({"alcance": "fuera", "codigo": None, "tema": "politica", "reformulada": ""}), CAT)
    assert f["tema"] is None


def test_la_prueba_tiene_16_y_14_y_la_regla():
    assert sum(t == "politica" for _, t in rf.PRUEBA_TEMA) == 16 and sum(t == "ciudad" for _, t in rf.PRUEBA_TEMA) == 14
    bien = [{"tema": t} for _, t in rf.PRUEBA_TEMA]
    assert rf.evaluar_tema(bien)["pasa"]
    mal = bien[:]
    mal[0] = mal[1] = mal[2] = None
    v = rf.evaluar_tema(mal)
    assert not v["criterios"]["RP1"]["se_cumple"] and v["criterios"]["RP3"]["valor"] == 27


def test_aparte_no_toca_la_v5_y_usa_las_definiciones_de_la_v6():
    import hashlib
    # la versión 5 tal como pasó REFORMULACION_2025 (huella tomada el 19/10, antes de la llamada aparte)
    assert hashlib.sha256(rf.SISTEMA_V5.encode("utf-8")).hexdigest()[:16] == HUELLA_V5
    defs = rf.SISTEMA_V6.split("di también su \"tema\":\n")[1].split("Si el alcance es \"voto\"")[0]
    assert defs in rf.SISTEMA_TEMA and "politica|ciudad" in rf.SISTEMA_TEMA


def test_aparte_catalogo_por_lista_y_nueva_por_llamada():
    llamadas = []

    def llamar(m, s, u, t):
        llamadas.append(s)
        return json.dumps({"tema": "politica"})
    ruta = Path(__file__).resolve().parent / "_cache_tema_aparte.json"
    cache = rf.e9.Cache(ruta)
    try:
        cat = rf.tema_de({"alcance": "catalogo", "codigo": "AG1", "reformulada": ""}, "p", llamar, cache, "simulado")
        ciu = rf.tema_de({"alcance": "catalogo", "codigo": "SP1", "reformulada": ""}, "p", llamar, cache, "simulado")
        assert cat["tema"] == "politica" and ciu["tema"] == "ciudad" and not llamadas
        nue = rf.tema_de({"alcance": "nueva", "codigo": None, "reformulada": "¿x?"}, "¿confían en la Fiscalía?", llamar,
                         cache, "simulado")
        assert nue["tema"] == "politica" and llamadas == [rf.SISTEMA_TEMA]
        assert rf.tema_de({"alcance": "fuera", "codigo": None, "reformulada": ""}, "p", llamar, cache, "x")["tema"] is None
    finally:
        ruta.unlink(missing_ok=True)


def test_aparte_son_30_nuevas():
    p = [x for x, _ in rf.PRUEBA_TEMA_APARTE]
    viejas = {x for x, _ in rf.PRUEBA_TEMA} | {x[0] for x in rf.PRUEBA_VOTO_V3 + rf.PRUEBA_MATIZ + rf.PRUEBA_GOBIERNO_2025}
    assert len(p) == len(set(p)) == 30 and not set(p) & viejas
    assert sum(t == "politica" for _, t in rf.PRUEBA_TEMA_APARTE) == 16


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Reformulación v6 — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
