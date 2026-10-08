"""
tests/test_banco_lote7.py

Pruebas de src/experiments/banco_lote7.py: ninguna llama a la API ni imprime datos de la encuesta.
Las que leen los diccionarios necesitan BSS_CNC_POLITICA_DIR; sin esa carpeta se saltan.
Se ejecuta directo:  python tests/test_banco_lote7.py
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import banco_lote7 as b7

FALLOS = []
HAY_DATOS = bool(os.environ.get("BSS_CNC_POLITICA_DIR")) and Path(os.environ.get("BSS_CNC_POLITICA_DIR", "")).is_dir()


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def test_lo_electoral_no_entra_a_las_candidatas_de_la_pagina():
    """D21: nada del lote 7 se usa en la página antes de la revisión jurídica."""
    # Por las preguntas del lote 7, no por el estudio: el lote 6 (opinión, sí permitido) comparte estudios con él.
    import pandas as pd
    from src.consulta import motor as mo
    c = mo._candidatas_estimacion()
    s7 = pd.read_csv(b7.SORTEO)
    assert c is not None and not set(c.id) & set(s7.id) and not set(c.familia) & set(s7.familia)


def test_las_opciones_que_no_son_un_nombre_quedan_fuera():
    for s in ("Voto en Blanco", "Ninguno", "NS/NR", "Otro", "No votaría por ninguno", "Ninguna"):
        assert b7.FUERA.search(s), s
    for s in ("Gustavo Petro", "la Coalición de la Esperanza", "Izquierda"):
        assert not b7.FUERA.search(s), s


def test_limpieza_de_opciones():
    assert b7.limpia_opcion("a)\xa0\xa0 Sergio Fajardo") == "Sergio Fajardo"
    assert b7.limpia_opcion("10.   Voto en Blanco <strong>(NO LEER)</strong>") == "Voto en Blanco"
    assert b7.limpia_opcion("a) Por la Coalición de la Esperanza conformada por Sergio Fajardo, Juan Manue") == "la Coalición de la Esperanza"


def test_la_tabla_con_los_diccionarios():
    if not HAY_DATOS:
        print("         (sin BSS_CNC_POLITICA_DIR: se salta)")
        return
    t = b7.tabla()
    assert t.id.is_unique and (t.ambito == "Bogotá").all() and t.tema.str.startswith("electoral").all()
    assert t.pregunta_pagina.str.match(r"^(En|A|Entre) ").all() and not t.pregunta_pagina.str.contains("la encuesta de 20").any()   # DI-BL19
    assert t.pregunta_pagina.str.match(r"^[^:,]*20\d\d[,:]").all() and not t.pregunta_pagina.str.contains(r"<|\(E:|por por|la Pacto", regex=True).any()
    f1 = t[t.id.str.endswith("_votaria")]
    assert len(f1) == 7 and all(json.loads(x) == [1, 2] for x in f1.codigos_favorables)


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Lote 7 del banco — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
