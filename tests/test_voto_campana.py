"""
tests/test_voto_campana.py

Pruebas de src/experiments/voto_campana.py (`VOTO_CAMPANA_SPECIFICATION.md`). No llaman a la API ni leen datos.
Se ejecuta directo:  python tests/test_voto_campana.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import voto_campana as vc

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_los_textos_son_los_del_preregistro_y_no_dicen_el_resultado():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "VOTO_CAMPANA_SPECIFICATION.md").read_text(encoding="utf-8")
    plano = " ".join(doc.replace("> ", "").split())
    for linea in vc.RESUMEN.split("\n"):
        assert " ".join(linea.split()) in plano, linea
    assert " ".join(vc.ENCUESTA.split()) in plano
    for prohibido in ("ganó la primera", "segunda vuelta", "polariz", "42,4", "38,4"):
        assert prohibido not in (vc.RESUMEN + vc.ENCUESTA).lower()


def test_copiar_la_encuesta():
    c = vc.copiar_encuesta(["Iván Cepeda Castro", "Abelardo de la Espriella", "Miguel Uribe Londoño"])
    assert abs(c["Iván Cepeda Castro"] - 100 * 44.6 / 76.2) < 1e-9 and c["Miguel Uribe Londoño"] == 0.0


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Voto con la campaña — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
