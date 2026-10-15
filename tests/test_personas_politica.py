"""
tests/test_personas_politica.py

Pruebas de src/experiments/personas_politica.py (`PERSONAS_POLITICA_SPECIFICATION.md`). No llaman a la API ni leen la EPC.
Se ejecuta directo:  python tests/test_personas_politica.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.experiments import personas_politica as pq

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_las_diez_escondidas_son_politicas_y_sin_transporte():
    assert [c for _, c, _ in pq.ESCONDIDAS] == ["GOB_5", "GOB_6", "GOB_8", "GOB_10", "GOB_9", "GOB_1", "CON_1", "GOB_4",
                                                 "CON_4", "CON_7"]
    assert not {"MOV_2", "MOV_3", "GCV_1"} & set(pq.VIDA)


def test_la_vida_se_escribe_con_sus_etiquetas_y_sin_vacios():
    ops = {"EDU_3": {1: "La mayoría estudia en colegio público"}, "HOG_4": {90: "Ninguna"}, "FIN_1": {}, "SEG_5": {},
           "CTI_2": pq.CTI_2}
    fila = pd.Series({"EDU_3": 1, "HOG_4": 90, "FIN_1": None, "SEG_5": None, "CUL_3": 4, "CTI_2_1": 1, "CTI_2_2": 5,
                      "CTI_2_3": None})
    v = pq.vida_texto(fila, ops)
    assert v[0] == "- Estudiantes del hogar: La mayoría estudia en colegio público" and "Libros leídos en el último año: 4" in v[2]
    assert v[-1] == "- Para qué usa la inteligencia artificial: Redacción de textos; Generación de ideas para su trabajo o estudio"


def test_la_regla_de_mejora():
    a = {"error_total": 10.0, "error_individual": 25.0}
    assert pq.mejora({"error_total": 9.0, "error_individual": 25.0}, a)
    assert not pq.mejora({"error_total": 9.5, "error_individual": 24.0}, a)
    assert not pq.mejora({"error_total": 8.0, "error_individual": 25.5}, a)


def test_el_documento():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "PERSONAS_POLITICA_SPECIFICATION.md").read_text(encoding="utf-8")
    for _, c, v in pq.ESCONDIDAS:
        assert f"`{c}`" in doc, c
    assert str(pq.SEMILLA) in doc and "tope de USD 2" in doc and "No inventes nada" in doc and "Puedes inventar" in doc


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Personas en lo político — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
