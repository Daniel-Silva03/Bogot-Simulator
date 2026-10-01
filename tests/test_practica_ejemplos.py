"""
tests/test_practica_ejemplos.py

Pruebas de src/experiments/practica_ejemplos.py con datos inventados. Ninguna llama a la API.
Se ejecuta directo:  python tests/test_practica_ejemplos.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.experiments import practica_ejemplos as pe
from src.experiments import puente_sin_base as sb

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def _q(i, fam, amb="general"):
    return {"id": f"Q{i}", "familia": fam, "ambito": amb, "pregunta_pagina": f"¿P{i}?",
            "real": {"grupos": {"sexo": {"Hombres": 40, "Mujeres": 50}, "edad": {"18-25": 60, "56+": 40},
                                "estrato": {"1": 70, "2": 66, "3": 55, "4": 45, "5-6": 40}}}}


QS = [_q(i, f"F{i // 3}", "Bogotá" if i % 4 == 0 else "general") for i in range(30)]


def test_las_familias_no_se_parten_y_los_ejemplos_son_de_otras_partes():
    parte = pe.partes(QS)
    for f in {q["familia"] for q in QS}:
        assert len({parte[q["id"]] for q in QS if q["familia"] == f}) == 1
    for q in QS:
        ej = pe.elegir_ejemplos(q, QS, parte)
        assert ej and all(parte[e["id"]] != parte[q["id"]] for e in ej)


def test_el_perfil_real_en_palabras():
    assert pe.perfil_real(QS[0]["real"]) == "más alto en estratos bajos; más alto en jóvenes; mujeres más alto"
    plano = {"grupos": {"sexo": {"Hombres": 50, "Mujeres": 51}, "edad": {"18-25": 50, "56+": 52},
                        "estrato": {"1": 50, "2": 50, "5-6": 53}}}
    assert pe.perfil_real(plano) == "parejo por estrato; parejo por edad; parejo por sexo"


def test_el_mensaje_lleva_perfiles_reales_y_ningun_puente_de_ejemplo():
    """DI-PE3, corregido antes de la corrida."""
    cat = {"C0": {"variable": "C0", "codigo": "C0", "pregunta": "¿C0?", "escala": [1, 2], "etiquetas": {"1": "a", "2": "b"}}}
    cp = pe.catalogo_con_perfiles(cat, {"C0": "parejo por estrato; parejo por edad; parejo por sexo"})
    m = pe.mensaje(QS[0], cp, QS[1:3], {q["id"]: pe.perfil_real(q["real"]) for q in QS})
    assert "[PERFIL: parejo por estrato" in m and "EJEMPLOS RESUELTOS" in m and "perfil real:" in m
    assert "Puente que ordenó" not in m and "ordenó bien" not in pe.SISTEMA


def test_las_instrucciones_son_el_v2_mas_un_parrafo():
    assert pe.SISTEMA.replace(pe.PARRAFO, "") == sb.SISTEMA_V2


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Práctica con ejemplos — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
