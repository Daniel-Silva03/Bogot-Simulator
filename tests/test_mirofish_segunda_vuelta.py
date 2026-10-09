"""
tests/test_mirofish_segunda_vuelta.py

Pruebas de src/experiments/mirofish_segunda_vuelta.py (`MIROFISH_SEGUNDA_VUELTA_SPECIFICATION.md`). No arrancan
MiroFish ni llaman a ninguna API.
Se ejecuta directo:  python tests/test_mirofish_segunda_vuelta.py
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import mirofish_segunda_vuelta as mf

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_el_tope_y_las_rondas_son_los_del_documento():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "MIROFISH_SEGUNDA_VUELTA_SPECIFICATION.md").read_text(encoding="utf-8")
    assert mf.TOPE_USD == 1.0 and mf.MAX_RONDAS == 10 and mf.MODELO == "openai/gpt-6-luna"
    assert "tope de USD 1" in doc and "máximo de 10 rondas" in doc
    assert mf.excede(16.0, 17.01) and not mf.excede(16.0, 16.99)


def test_la_semilla_es_publica_y_no_trae_encuestas_ni_el_resultado():
    s = mf.SEMILLA.read_text(encoding="utf-8")
    assert "41,70" in s and "37,74" in s                                      # primera vuelta en Bogotá
    assert s.count("CNC") == 1 and not re.search(r"encuesta del|Invamer|Guarumo|AtlasIntel|Datexco", s)   # ninguna encuesta
    assert "53,14" not in s and "52 %" not in s and "presidente electo" not in s.lower()
    assert "dato del CNC" in s                                                # lo dice


def test_el_backend_solo_escucha_en_localhost_y_sin_archivo_de_claves():
    import inspect
    src = inspect.getsource(mf.arrancar_backend)
    assert '"FLASK_HOST": "127.0.0.1"' in src and '".env"' not in src and mf.BASE.startswith("http://127.0.0.1")


def test_la_simulacion_termina_cuando_paran_las_dos_redes():
    """DI-MF4: MiroFish deja la simulación en «running», esperando entrevistas."""
    assert mf.simulacion_terminada({"runner_status": "running", "current_round": 10, "twitter_running": False,
                                    "reddit_running": False})
    assert not mf.simulacion_terminada({"runner_status": "running", "current_round": 4, "twitter_running": True,
                                        "reddit_running": False})
    assert not mf.simulacion_terminada({"runner_status": "starting", "current_round": 0})
    assert mf.simulacion_terminada({"runner_status": "stopped"})


def test_la_semilla_de_galan_no_trae_la_cifra_ni_encuestas():
    """MIROFISH_GALAN §2 y §5."""
    s = mf.SEMILLA_GALAN.read_text(encoding="utf-8")
    assert "racionamiento" in s and "TransMilenio" in s
    assert not re.search(r"26 ?%|aprobaci[oó]n de|imagen favorable|Invamer|Cómo Vamos|percepci[oó]n ciudadana", s, re.I)
    assert s.count("CNC") == 1                                                # solo la aclaración
    assert set(mf.CASOS) == {"segunda_vuelta", "galan"} and mf.CASOS["segunda_vuelta"][1] == mf.REQUERIMIENTO
    doc = (Path(__file__).resolve().parents[1] / "docs" / "MIROFISH_GALAN_SPECIFICATION.md").read_text(encoding="utf-8")
    assert "--caso galan" in doc and "**26 %**" in doc


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"MiroFish — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
