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


def test_la_variante_b_usa_la_demografia_de_bogota_y_cuenta_sin_ponderar():
    """Enmienda 1."""
    d = tt.DEMOGRAFIA_BOGOTA["content"]["Demografía"]
    for k in ("Sexo", "Edad", "Estrato socioeconómico de la vivienda"):
        assert abs(sum(float(v.rstrip("%")) for v in d[k].values()) - 100) < 0.6, k
    assert tt.N_B == 24 and tt.MIN_B == 18
    assert tt.porcentaje_simple({str(i): "si" for i in range(18)}) == 100.0
    assert tt.porcentaje_simple({str(i): ("si" if i < 6 else "no") for i in range(24)}) == 25.0
    assert tt.porcentaje_simple({str(i): "si" for i in range(17)}) is None
    assert tt.porcentaje_simple({**{str(i): "no" for i in range(20)}, "x": None}) == 0.0


def test_se_recupera_el_texto_que_la_primera_corrida_unio_con_espacios():
    """DI-TT5."""
    assert tt.desespaciar("N O ,   p o r q u e   e l   t r a n s p o r t e .") == "NO, porque el transporte."
    assert tt.desespaciar("Sí, aunque hay problemas") == "Sí, aunque hay problemas"         # el texto normal no cambia
    assert tt.texto_de("SÍ, claro") == "SÍ, claro" and tt.texto_de(["SÍ.", "Me gusta"]) == "SÍ. Me gusta"
    assert mf.leer_si_no(tt.desespaciar("S Í .   A u n q u e")) == "si"


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
