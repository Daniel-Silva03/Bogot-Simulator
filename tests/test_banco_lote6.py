"""
tests/test_banco_lote6.py

Pruebas de src/experiments/banco_lote6.py: ninguna llama a la API ni imprime datos de la encuesta.
Las que leen las bases necesitan BSS_CNC_POLITICA_DIR; sin esa carpeta se saltan.
Se ejecuta directo:  python tests/test_banco_lote6.py
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import banco_lote6 as b6
from src.experiments import banco_reales as br

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


def test_la_lista_es_la_del_pre_registro_y_no_trae_voto_ni_personajes():
    vs = {f"{e}_{v}" for e, (_, _, l) in b6.PREGUNTAS.items() for v, _ in l}
    assert len(vs) == 64
    for prohibida in ("CC873501_P2", "CC871801_P1", "CC873501_P1", "CC873501_P26", "CC871401_T22_1", "CC871801_T9_1",
                      "CC871801_T11_1", "CC873501_P17_1"):
        assert prohibida not in vs, prohibida


def test_las_escalas_tienen_lado_favorable_y_el_9_es_no_sabe():
    for cats, fav in b6.ESCALAS.values():
        c = br.categorias(cats)
        assert 9 not in br.validos(c) and set(fav) <= set(br.validos(c))


def test_la_limpieza_del_texto():
    assert b6.texto("X", "T24_3", "24. ¿Usted cree que la presencia de _______ REEMPLAZAR es importante? (E: LEER ROTAR). - 3. Fiscalía") \
        == "¿Cree que la presencia de «Fiscalía» es importante para la solución del paro?"
    assert b6.texto("X", "P4_SEM_1", "4. Está usted de acuerdo… Los migrantes… - A. Son una oportunidad") \
        == "¿Está de acuerdo con que «los migrantes son una oportunidad»?"
    assert b6.texto("CC871401", "P9", "9. Dígame por favor ¿está usted de acuerdo con el paro? LEA") == "¿Está usted de acuerdo con el paro?"


def test_la_tabla_con_los_diccionarios():
    if not HAY_DATOS:
        print("         (sin BSS_CNC_POLITICA_DIR: se salta)")
        return
    t = b6.tabla()
    assert len(t) == 64 and t.familia.nunique() == 22 and t.id.is_unique
    assert not t.pregunta_pagina.str.contains(r"F8|REEMPLAZAR|\(E:|<|¿.*¿", regex=True).any()
    assert set(t.anio) == {2021, 2022} and (t.ambito == "Bogotá").all()
    assert all(json.loads(f) in ([1], [1, 2]) for f in t.codigos_favorables)


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Lote 6 del banco — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
