"""
tests/test_voto_grupos.py

Pruebas de src/experiments/voto_grupos.py (`VOTO_GRUPOS_SPECIFICATION.md`). Solo funciones puras, con registros
inventados: no leen encuestas ni llaman a la API.
Se ejecuta directo:  python tests/test_voto_grupos.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.experiments import voto_grupos as vg

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def rec(sexo, estrato, edad, bases_estrato=None, edad26=False):
    eg = ["18-24", "25-34", "35-44", "45-54", "55+"] if edad26 else ["18-25", "26-40", "41-55", "56+"]
    return {"grupos": {"sexo": dict(zip(["Hombres", "Mujeres"], sexo)), "estrato": dict(zip(["1", "2", "3", "4", "5-6"], estrato)),
                       "edad": dict(zip(eg, edad))},
            "bases": {"sexo": {"Hombres": 150, "Mujeres": 150},
                      "estrato": dict(zip(["1", "2", "3", "4", "5-6"], bases_estrato or [30, 90, 120, 60, 30])),
                      "edad": dict(zip(eg, [60] * len(eg)))}}


def test_los_grupos_gruesos_se_ponderan_por_su_base():
    g = vg.gruesos(rec([40, 50], [60, 40, 30, 20, 10], [50, 40, 30, 20]))
    assert g["estrato"]["1-2"] == ((60 * 30 + 40 * 90) / 120, 120)
    assert g["estrato"]["4-6"] == ((20 * 60 + 10 * 30) / 90, 90)
    assert g["edad"]["media"] == (35.0, 120) and g["edad"]["joven"] == (50.0, 60) and g["edad"]["mayor"] == (20.0, 60)


def test_los_cortes_de_edad_de_2026_caen_en_los_mismos_grupos():
    g = vg.gruesos(rec([40, 50], [1] * 5, [50, 40, 30, 20, 10], edad26=True))
    assert g["edad"]["joven"] == (50.0, 60) and g["edad"]["media"] == (30.0, 180) and g["edad"]["mayor"] == (10.0, 60)


def test_un_grupo_sin_base_no_aparece():
    g = vg.gruesos(rec([40, 50], [60, 40, 30, 20, 10], [50, 40, 30, 20], bases_estrato=[30, 90, 120, 0, 0]))
    assert "4-6" not in g["estrato"]


def test_la_estimacion_promedia_las_elegidas_y_los_grupos_chicos_no_cuentan():
    cand = {"a": vg.gruesos(rec([40, 60], [70, 70, 50, 30, 30], [60, 50, 40, 30])),
            "b": vg.gruesos(rec([20, 40], [50, 50, 30, 10, 10], [40, 30, 20, 10]))}
    e = vg.estimar(["a", "b"], cand)
    assert e["sexo"] == {"Hombres": 30.0, "Mujeres": 50.0} and e["estrato"]["1-2"] == 60.0
    obj = {"q": vg.gruesos(rec([35, 45], [65, 65, 40, 20, 20], [50, 40, 30, 20], bases_estrato=[10, 10, 120, 60, 30]))}
    p = vg.pares([{"id": "q", "ids": ["a", "b"]}], obj, cand, {"a": 50.0, "b": 30.0})
    assert "1-2" not in set(p[p.corte == "estrato"].grupo)                   # base 20 < 30 (DI-VG2)
    assert (p.S_total == 40.0).all()


def test_la_diferencia_entre_extremos_y_la_regla():
    p = pd.DataFrame([{"id": f"q{i}", "corte": "sexo", "grupo": g, "real": r, "base": 100, "S": s, "S_total": 40}
                      for i in range(12) for g, r, s in (("Mujeres", 50, 48), ("Hombres", 35, 37))])
    m = vg.medir(p, "sexo", 10)
    assert m["diferencias_claras"] == 12 and m["acierto_sentido"] == 1.0
    assert vg.regla(m)["se_muestra"]                                        # 2,0 contra 7,5 del total
    assert not vg.regla({**m, "diferencias_claras": 9})["R2"]
    assert not vg.regla({**m, "eam_grupos": 7.0, "eam_referencia": 7.5})["R1"]


def test_los_umbrales_son_los_del_documento():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "VOTO_GRUPOS_SPECIFICATION.md").read_text(encoding="utf-8")
    assert vg.MIN_BASE == 30 and vg.UMBRAL_DIF == 10 and vg.MEJORA == 0.9 and vg.MIN_DIFS == 10 and vg.ACIERTO_DIF == 0.8
    assert "30 personas" in doc and "10 puntos" in doc and "0,9 ×" in doc and "≥ 80 %" in doc


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Voto por grupos — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
