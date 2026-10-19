"""
tests/test_selector_fase_b.py

Pruebas de src/evaluacion/selector_fase_b.py (`SELECTOR_FASE_B_SPECIFICATION.md`). No llaman a la API ni leen la EPC.
Se ejecuta directo:  python tests/test_selector_fase_b.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.evaluacion import selector_fase_b as sb

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def _tabla(g_util: bool):
    rng = np.random.default_rng(1)
    filas = []
    for par in ("P1", "P2"):
        for i in range(30):
            p = rng.uniform(20, 70)
            cambio = rng.normal(0, 6)
            real = p + cambio
            g = p + (cambio if g_util else rng.normal(0, 6)) + rng.normal(0, 1)
            filas.append({"par": par, "variable": f"V{i}", "dominio": sb.GOB if i < 8 else "movilidad", "P": p, "G": g,
                          "real": real})
    return pd.DataFrame(filas)


def test_si_los_agentes_traen_el_cambio_lambda_sube_y_pasa():
    r, _ = sb.evaluar(_tabla(True))
    assert all(r["lambdas"][p]["C"] >= 0.7 for p in ("P1", "P2")) and r["reglas"]["C"]["pasa"]


def test_si_los_agentes_son_ruido_lambda_queda_cerca_de_cero_y_no_pasa():
    r, _ = sb.evaluar(_tabla(False))
    assert all(r["lambdas"][p]["C"] <= 0.3 for p in ("P1", "P2")) and not r["reglas"]["C"]["pasa"]


def test_ante_empate_el_menor_lambda():
    t = pd.DataFrame({"P": [50.0, 50.0], "G": [50.0, 50.0], "real": [52.0, 48.0]})
    assert sb.elegir_lambda(t) == 0.0


def test_la_nota_es_la_del_preregistro():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "SELECTOR_FASE_B_SPECIFICATION.md").read_text(encoding="utf-8")
    plantilla = sb.nota(2023, 2024).replace("2023", "{año base}").replace("2024", "{año objetivo}")
    assert " ".join(plantilla.split()) in " ".join(doc.replace("> ", "").split())


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Selector Fase B — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
