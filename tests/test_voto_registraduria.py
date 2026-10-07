"""
tests/test_voto_registraduria.py

Pruebas de src/experiments/voto_registraduria.py: ninguna llama a la API ni lee resultados.
Se ejecuta directo:  python tests/test_voto_registraduria.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import voto_registraduria as vr

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_el_cruce_de_nombres():
    assert vr.nombra("Gustavo Petro", "GUSTAVO FRANCISCO|PETRO URREGO")                        # segundo nombre
    assert vr.nombra("Fico Gutiérrez", "FEDERICO ANDRES|GUTIERREZ ZULUAGA")                     # apodo
    assert vr.nombra("en una segunda vuelta entre Rodolfo Hernández y Gustavo Petro, ¿votaría", "GUSTAVO FRANCISCO|PETRO URREGO")
    assert vr.nombra("Abelardo Gabriel De La Espriella Otero - José Manuel Restrepo", "ABELARDO DE LA ESPRIELLA")   # partículas
    assert vr.nombra("Iván Cepeda", "IVÁN CEPEDA CASTRO")
    assert not vr.nombra("Gustavo Petro", "GUSTAVO MATAMOROS CAMACHO")
    assert not vr.nombra("Claudia López", "CLARA LÓPEZ OBREGÓN")


def test_medir_normaliza_y_mira_el_primero():
    m = vr.medir({"a": 30, "b": 10}, {"a": 60, "b": 40, "c": 99})
    assert m["n"] == 2 and m["primero"] and abs(m["eam"] - 15) < 1e-9 and abs(m["error_diferencia"] - 30) < 1e-9


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Voto contra la Registraduría — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
