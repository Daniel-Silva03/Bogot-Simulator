"""
tests/test_personas_pulidas.py

Pruebas de src/experiments/personas_pulidas.py (`PERSONAS_PULIDAS_SPECIFICATION.md`). No llaman a la API ni leen la EPC.
Se ejecuta directo:  python tests/test_personas_pulidas.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from src.experiments import personas_pulidas as pp

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_desarrollo_y_final_no_se_cruzan():
    assert not set(pp.DESARROLLO) & set(pp.FINAL) and len(pp.DESARROLLO) == 12 and len(pp.FINAL) == 8
    assert set(pp.SECUNDARIA) <= set(pp.DESARROLLO)


def test_las_variantes_y_sus_instrucciones():
    assert "probabilidad" not in pp.sistema("V0") and "coherentes" not in pp.sistema("V0")
    assert "coherentes" in pp.sistema("V1") and "probabilidad" in pp.sistema("V2") and "coherentes" not in pp.sistema("V2")
    assert pp.CONFIG["V4"] == (True, True, True)
    esc = pp.preguntas(("CON_4",))
    u = pp.usuario("perfil", esc, {"CON_4": 31.6})
    assert "se estima que cerca del 32 %" in u and "«Confío» o «Confío plenamente»" in u
    assert "se estima" not in pp.usuario("perfil", esc)


def test_leer_probabilidades_normaliza_sin_no_sabe():
    esc = pp.preguntas(("CON_4", "CON_5"))
    q = pp.leer_prob('{"E1": {"1": 0.2, "2": 0.2, "3": 0, "4": 0, "5": 0, "90": 0.6}, "E2": "nada"}', esc)
    assert q["E1"] == {1: 0.5, 2: 0.5, 3: 0.0, 4: 0.0, 5: 0.0} and q["E2"] is None


def test_tvd_y_eleccion():
    assert pp.tvd({1: 1.0}, {2: 1.0}) == 1.0 and pp.tvd({1: 0.5, 2: 0.5}, {1: 0.5, 2: 0.5}) == 0.0
    med = {"V0": {"error_individual": 20, "error_constante": 25, "error_total": 10, "tvd": 0.3},
           "V2": {"error_individual": 20, "error_constante": 25, "error_total": 10.4, "tvd": 0.1},
           "V3": {"error_individual": 30, "error_constante": 25, "error_total": 1, "tvd": 0.0}}
    assert pp.elegir(med) == "V2"                                   # V3 no le gana a la constante; empate a 0,5 → menor TVD
    assert pp.elegir({"V0": {"error_individual": 30, "error_constante": 25, "error_total": 1, "tvd": 0}}) is None


def test_el_documento():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "PERSONAS_PULIDAS_SPECIFICATION.md").read_text(encoding="utf-8")
    for v in pp.DESARROLLO + pp.FINAL:
        assert f"`{v}`" in doc, v
    assert str(pp.SEMILLA_FINAL) in doc and "tope de USD 2" in doc and pp.INSTRUCCION.strip()[:60] in doc.replace("\n", " ")


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Personas pulidas — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
