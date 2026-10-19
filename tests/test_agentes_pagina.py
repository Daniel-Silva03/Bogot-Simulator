"""
tests/test_agentes_pagina.py

Pruebas de src/consulta/agentes.py y de `Motor.responder_agentes` (D22, DI-CO40). No llaman a la API. Usan la EPC 2025 si está
en esta máquina.
Se ejecuta directo:  python tests/test_agentes_pagina.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.consulta import agentes as ag
from src.consulta import motor as mo
from src.experiments import experimento9 as e9

FALLOS = []
ESC = ["No confío nada", "Desconfío", "Ni confío ni desconfío", "Confío", "Confío plenamente"]


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_el_panel_y_la_estimacion_simulada():
    a = ag.Agentes()
    assert len(a.perfiles) == ag.N == 200 and all("Lo que respondió:" in p for p in a.perfiles)
    c = e9.Cache(Path(tempfile.gettempdir()) / "bss_test_agentes.json")
    r = a.estimar("¿Confía usted en la Policía?", ESC, ag.cliente_simulado(), c, e9.MODELO_SIMULADO)
    assert r["tipo"] == "agentes" and r["respondieron"] == 200 and abs(sum(r["distribucion"]) - 1) < 1e-3
    assert r["rango"][1] - r["rango"][0] <= 2 * ag.H + 0.1 and set(r["grupos"]) == {"estrato", "edad", "sexo"}
    assert sum(g["n"] for g in r["grupos"]["sexo"]) == 200 and "no una medición" in r["texto"]


def test_encendidos_con_el_error_a_la_vista():
    """DI-CO42 y DI-AG-P6: encendidos con el modelo real, como experimento, y el error medido junto a la cifra."""
    assert mo.AGENTES_CON_MODELO_REAL is True
    assert "entre 10 y 12 puntos" in ag.ERROR_MEDIDO and "repetir el último dato medido acertó más" in ag.ERROR_MEDIDO
    c = e9.Cache(Path(tempfile.gettempdir()) / "bss_test_agentes.json")
    r = ag.Agentes().estimar("¿Confía usted en la Policía?", ESC, ag.cliente_simulado(), c, e9.MODELO_SIMULADO)
    assert r["error_medido"] == ag.ERROR_MEDIDO
    html = (Path(__file__).resolve().parents[1] / "src" / "consulta" / "pagina.html").read_text(encoding="utf-8")
    assert "<b>Error medido:</b> ${esc(a.error_medido)}" in html and "Experimental · con agentes" in html
    assert "La mayoría no respondería ${op}" in html and "<p class=\"est-titulo\">${titulo}</p>" in html


def test_la_decision_esta_escrita():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "PROJECT_CONTEXT.md").read_text(encoding="utf-8")
    assert "### D22" in doc and "APPROVED para construir en modo simulado" in doc
    html = (Path(__file__).resolve().parents[1] / "src" / "consulta" / "pagina.html").read_text(encoding="utf-8")
    assert "pedirAgentes" in html and "/api/agentes" in html and "Experimental" in html


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Agentes en la página — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
