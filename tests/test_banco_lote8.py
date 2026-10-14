"""
tests/test_banco_lote8.py

Pruebas de src/experiments/banco_lote8.py (`BANCO_PREGUNTAS_NUEVAS.md` §17). No leen la EPC.
Se ejecuta directo:  python tests/test_banco_lote8.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import banco_lote8 as b8
from src.experiments import banco_reales as br

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_son_26_preguntas_en_13_familias():
    t = b8.tabla()
    assert len(t) == 26 and t.familia.nunique() == 13 and t.id.is_unique
    assert (t.anio == 2025).all() and not t.independiente.any()


def test_no_sabe_y_no_aplica_no_cuentan():
    """DI-BL20: el 90 y el 91 quedan fuera de los válidos; los de la escala, dentro."""
    for f in b8.tabla().to_dict("records"):
        v = br.validos(br.categorias(f["categorias"]))
        assert 90 not in v and 91 not in v, f["id"]
        assert set(json.loads(f["codigos_favorables"])) <= set(v), f["id"]
    gob = b8.tabla().set_index("variable").loc["GOB_4"]
    assert br.validos(br.categorias(gob.categorias)) == [1, 2] and json.loads(gob.codigos_favorables) == [2]


def test_no_entra_lo_que_el_preregistro_deja_fuera():
    ids = set(b8.tabla().variable)
    assert not ids & {"ENT_4", "EDU_11", "CCC_17", "CCC_19", "GOB_5", "GOB_6", "SEG_3", "BOG_5", "DMO_1"}


def test_el_documento_es_el_preregistro():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "BANCO_PREGUNTAS_NUEVAS.md").read_text(encoding="utf-8")
    s = doc[doc.index("## 17. Octavo lote"):]
    assert "20261014" in s and str(b8.SEMILLA) == "20261014"
    assert "`EDU_4` a `EDU_10`" in s
    for v in b8.tabla().variable:
        assert f"`{v}`" in s or v in {f"EDU_{i}" for i in range(5, 10)}, v


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Lote 8 — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
