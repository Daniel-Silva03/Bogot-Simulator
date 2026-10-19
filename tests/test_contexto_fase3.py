"""
tests/test_contexto_fase3.py

Pruebas de src/evaluacion/contexto_fase3.py (`CONTEXTO_FASE3_SPECIFICATION.md`). No llaman a la API.
Se ejecuta directo:  python tests/test_contexto_fase3.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.evaluacion import contexto_fase3 as cf

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_invamer_solo_hasta_el_corte():
    p1 = cf.invamer_hasta("2024-09-01")
    p2 = cf.invamer_hasta("2025-09-01")
    assert [m for m, _ in p1] == ["feb. 2024", "abr. 2024", "jun. 2024", "ago. 2024"]
    assert len(p2) == 9 and p2[-1] == ("jun. 2025", 42.0)


def test_el_contexto_es_el_del_preregistro_y_no_interpreta():
    esc = [{"variable": "AG1", "pregunta": "Las cosas en Bogotá ¿van por buen camino o por mal camino?"}]
    c = cf.contexto(2024, 2025, esc, {"AG1": 37.1})
    assert c.startswith("DATOS PÚBLICOS DISPONIBLES ANTES DE ESTAS PREGUNTAS (cifras de toda la ciudad, no de esta persona):")
    assert "37 % respondió «Buen camino»" in c and "jun. 2025, 42 %" in c
    assert c.endswith("Estas cifras son de toda la ciudad: esta persona puede pensar distinto. Responde como ella.")
    for palabra in ("subió", "bajó", "cayó", "mejor", "peor", "tendencia"):
        assert palabra not in c


def test_la_regla():
    t = pd.DataFrame({"P": [50.0] * 9, "G": [60.0] * 9, "GC": [51.0] * 9, "real": [52.0] * 9})
    r = cf.evaluar(t)
    assert r["reglas"]["RC1"] and r["reglas"]["RC3"] and r["predicciones"]["PC1"]


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Contexto Fase 3 — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
