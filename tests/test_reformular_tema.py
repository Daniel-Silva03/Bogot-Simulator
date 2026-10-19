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
