"""
tests/test_personas_con_encuesta.py

Pruebas de src/experiments/personas_con_encuesta.py (`PERSONAS_CON_ENCUESTA_SPECIFICATION.md`). No llaman a la API ni
leen la EPC.
Se ejecuta directo:  python tests/test_personas_con_encuesta.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import personas_con_encuesta as pc

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_las_seis_escondidas_con_su_escala():
    esc = pc.escondidas()
    assert [e["variable"] for e in esc] == list(pc.ESCONDIDAS) and [e["clave"] for e in esc] == [f"E{i}" for i in range(1, 7)]
    assert all(e["validos"] == [1, 2, 3, 4, 5] and 90 in e["categorias"] for e in esc)


def test_leer_acepta_solo_codigos_de_la_escala():
    esc = pc.escondidas()
    r = pc.leer('{"E1": 2, "E2": "4", "E3": 7, "E4": null, "E5": 90}', esc)
    assert r == {"E1": 2, "E2": 4, "E3": None, "E4": None, "E5": 90, "E6": None}
    assert pc.leer("no es json", esc)["E1"] is None


def test_el_perfil_no_trae_identificador_y_si_las_respuestas():
    t = pc.perfil_texto({"sexo": "mujer", "edad": 34, "estrato": 2, "localidad": "Kennedy"},
                        [("¿Qué tan orgulloso se siente?", "Orgulloso")])
    assert "Kennedy" in t and "→ Orgulloso" in t and "id" not in t.lower().split()
    u = pc.usuario(t, pc.escondidas())
    assert u.startswith("QUIÉN ES:") and "E6." in u and "Confío mucho" in u


def test_el_documento():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "PERSONAS_CON_ENCUESTA_SPECIFICATION.md").read_text(encoding="utf-8")
    for v in pc.ESCONDIDAS:
        assert f"`{v}`" in doc
    assert str(pc.SEMILLA) in doc and "tope de USD 1" in doc and "12,2" in doc and pc.N == 200


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Personas con su encuesta — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
