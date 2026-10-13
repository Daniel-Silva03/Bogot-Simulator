"""
tests/test_tinytroupe_residentes.py

Pruebas de src/experiments/tinytroupe_residentes.py (`TINYTROUPE_RESIDENTES_SPECIFICATION.md`). No importan TinyTroupe ni
llaman a ninguna API.
Se ejecuta directo:  python tests/test_tinytroupe_residentes.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import mirofish_segunda_vuelta as mf
from src.experiments import tinytroupe_residentes as tt

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_son_los_mismos_doce_residentes_de_mirofish():
    p = tt.perfiles()
    assert [x["nombre"] for x in p] == list(mf.RESIDENTES)
    assert all(x["estrato"] in "123456" and 18 <= x["edad"] <= 80 for x in p)


def test_el_contexto_es_la_gestion_sin_la_tabla_ni_las_fuentes():
    c = tt.contexto()
    assert c.startswith("## El alcalde") and "racionamiento" in c
    assert "Marlene" not in c and "Fuentes" not in c and "http" not in c


def test_la_configuracion_usa_luna_y_apaga_la_memoria():
    c = tt.CONFIG_INI
    assert "MODEL=openai/gpt-6-luna" in c and "REASONING_EFFORT=low" in c and "CACHE_API_CALLS=True" in c
    assert "ENABLE_MEMORY_CONSOLIDATION=False" in c and "ENABLE_CONTINUOUS_CONTEXTUAL_SEMANTIC_MEMORY_RETRIEVAL=False" in c
    assert tt.TOPE_USD == 1.0


def test_el_documento_es_el_pre_registro():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "TINYTROUPE_RESIDENTES_SPECIFICATION.md").read_text(encoding="utf-8")
    assert "REASONING_EFFORT=low" in doc and "tope de USD 1" in doc
    for _, pregunta, real in mf.PREGUNTAS_RESIDENTES:
        assert pregunta in doc and f"{real:.0f} %" in doc


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"TinyTroupe — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
