"""
tests/test_verificar_epc2025.py

Pruebas de src/population/verificar_epc2025.py con textos inventados en el formato del formulario 2025. No leen el
formulario ni los microdatos.
Se ejecuta directo:  python tests/test_verificar_epc2025.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.population import verificar_epc2025 as v

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


FORM = """| PRIORITARIA | ANUAL | OPTIMISMO
GOB_1: ¿Las cosas van por buen camino o por mal camino? [RU]
o 1: Buen camino
o 2: Mal camino
| PRIORITARIA | ANUAL | ORGULLO
GOB_2: ¿Qué tan orgulloso(a) se siente? [RU] [ENC: tarjeta]
Nada orgulloso Poco orgulloso Ni orgulloso ni no orgulloso Orgulloso Muy orgulloso
1 2 3 4 5
| PRIORITARIA | ANUAL | TIEMPOS
MOV_1: ¿Más tiempo o menos? [RU]
Más tiempo  Lo mismo  Menos tiempo
1 2 3
"""
ORGULLO = {"escala": [1, 2, 3, 4, 5], "etiquetas": {"1": "Nada orgulloso", "2": "Poco orgulloso",
                                                    "3": "Ni orgulloso ni no orgulloso", "4": "Orgulloso", "5": "Muy orgulloso"}}


def test_cada_codigo_tiene_su_bloque():
    b = v.bloques(FORM)
    assert set(b) == {"GOB_1", "GOB_2", "MOV_1"} and "Buen camino" in b["GOB_1"] and "Buen camino" not in b["GOB_2"]


def test_las_opciones_por_linea_y_en_fila():
    b = v.bloques(FORM)
    assert v.opciones_por_linea(b["GOB_1"]) == {1: "Buen camino", 2: "Mal camino"}
    etq, nums = v.fila_de_numeros(b["GOB_2"])
    assert nums == [1, 2, 3, 4, 5] and "Muy orgulloso" in etq


def test_coincide_si_es_la_misma_escala_y_no_si_cambia_el_orden():
    b = v.bloques(FORM)
    assert v.comparar(ORGULLO, b["GOB_2"], FORM, "GOB_2")["coincide"]
    camino = {"escala": [1, 2], "etiquetas": {"1": "Buen camino", "2": "Mal camino"}}
    assert v.comparar(camino, b["GOB_1"], FORM, "GOB_1")["coincide"]
    al_reves = {"escala": [1, 2, 3], "etiquetas": {"1": "Lo mismo", "2": "Más tiempo", "3": "Menos tiempo"}}
    assert not v.comparar(al_reves, b["MOV_1"], FORM, "MOV_1")["coincide"]                # otro orden: no se junta


def test_la_revision_manual_explica_cada_decision():
    assert all(isinstance(r, str) and len(r) > 10 for _, r in v.REVISION_MANUAL.values())
    assert not v.REVISION_MANUAL["CV5"][0] and not v.REVISION_MANUAL["RC5_6"][0] and v.REVISION_MANUAL["GG3"][0]


if __name__ == "__main__":
    pruebas = [x for k, x in list(globals().items()) if k.startswith("test_")]
    print(f"Verificación EPC 2025 — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
