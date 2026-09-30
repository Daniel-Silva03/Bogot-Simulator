"""
tests/test_segunda_vuelta_2026.py

Pruebas de src/experiments/segunda_vuelta_2026.py antes de abrir la segunda vuelta
(`SEGUNDA_VUELTA_2026_SPECIFICATION.md` §8). Usan la primera vuelta real y
segundas vueltas INVENTADAS; ninguna llama a main().
Se ejecuta directo:  python tests/test_segunda_vuelta_2026.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.experiments import geografia_electoral as ge
from src.experiments import segunda_vuelta_2026 as sv

FALLOS = []
SEMILLAS = 200


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


V1 = pd.read_csv(ge.ELECTORAL / "presidente_1v_localidad.csv")
REGLAS, CIUDAD = sv.reglas_primera_vuelta(V1)

# §5 del pre-registro, en porcentaje con un decimal: (bloques, ingenua)
TABLA_S5 = {1: (27.0, 29.2), 2: (30.6, 36.2), 12: (36.9, 40.3), 11: (38.7, 42.6), 9: (41.7, 45.8),
            13: (42.1, 47.7), 16: (42.3, 45.9), 14: (42.4, 45.9), 10: (44.4, 48.9), 15: (45.3, 49.9),
            8: (50.2, 55.0), 6: (53.1, 58.2), 18: (56.8, 62.3), 17: (58.7, 65.8), 3: (59.7, 66.8),
            7: (61.4, 67.0), 4: (62.4, 68.7), 19: (62.7, 68.4), 5: (65.6, 71.5), 20: (78.6, 83.1)}


# --- la predicción está congelada en el pre-registro -------------------------

def test_la_tabla_del_pre_registro_sale_del_codigo():
    malas = {l: (round(100 * REGLAS.bloques[l], 1), round(100 * REGLAS.ingenua[l], 1), e)
             for l, e in TABLA_S5.items()
             if (round(100 * REGLAS.bloques[l], 1), round(100 * REGLAS.ingenua[l], 1)) != e}
    assert not malas and len(REGLAS) == 20, malas


def test_la_ciudad_del_pre_registro_sale_del_codigo():
    assert round(100 * CIUDAD["bloques"], 1) == 47.3 and round(100 * CIUDAD["ingenua"], 1) == 52.5, CIUDAD


def test_las_dos_reglas_dan_los_mismos_ganadores():
    """§2: por eso P3 no es informativa."""
    assert ((REGLAS.bloques > 0.5) == (REGLAS.ingenua > 0.5)).all()
    assert int((REGLAS.bloques > 0.5).sum()) == 10


def test_el_documento_trae_la_tabla():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "SEGUNDA_VUELTA_2026_SPECIFICATION.md").read_text(encoding="utf-8")
    for x in ("| Usaquén | 27,0 | 29,2 |", "| **Kennedy** | **50,2** | 55,0 |", "Cepeda 47,3 %"):
        assert x in doc, x


def test_un_candidato_sin_bloque_detiene():
    v = V1[V1.anio == 2026].copy()
    v.loc[v.clave == "botero", "clave"] = "alguien_nuevo"
    try:
        sv.reglas_primera_vuelta(v)
    except sv.SegundaVueltaError as e:
        assert "sin bloque" in str(e)
    else:
        raise AssertionError("debió detenerse")


# --- lo observado ------------------------------------------------------------

def _segunda(p_loc: pd.Series, extra=None):
    filas = []
    for l, p in p_loc.items():
        filas += [{"anio": 2026, "zona": l, "cod_loc": l, "clave": sv.CEPEDA, "tipo": "candidato", "votos": round(10000 * p)},
                  {"anio": 2026, "zona": l, "cod_loc": l, "clave": sv.ABELARDO, "tipo": "candidato", "votos": round(10000 * (1 - p))}]
    return pd.DataFrame(filas + (extra or []))


def test_lo_observado_se_lee_por_localidad_y_ciudad():
    p = pd.Series(0.4, index=range(1, 21))
    extra = [{"anio": 2026, "zona": 90, "cod_loc": np.nan, "clave": sv.CEPEDA, "tipo": "candidato", "votos": 20000},
             {"anio": 2026, "zona": 90, "cod_loc": np.nan, "clave": sv.ABELARDO, "tipo": "candidato", "votos": 0},
             {"anio": 2026, "zona": 1, "cod_loc": 1, "clave": "blanco", "tipo": "blanco", "votos": 999}]
    obs, ciudad = sv.observado_segunda_vuelta(_segunda(p, extra))
    assert np.allclose(obs, 0.4) and abs(ciudad - (80000 + 20000) / 220000) < 1e-12


def test_sin_segunda_vuelta_se_detiene():
    try:
        sv.observado_segunda_vuelta(V1[V1.anio < 2026])
    except sv.SegundaVueltaError as e:
        assert "todavía" in str(e)
    else:
        raise AssertionError("debió detenerse")


def test_una_segunda_vuelta_con_otro_candidato_se_detiene():
    s = _segunda(pd.Series(0.4, index=range(1, 21)))
    s.loc[0, "clave"] = "valencia"
    try:
        sv.observado_segunda_vuelta(s)
    except sv.SegundaVueltaError:
        pass
    else:
        raise AssertionError("debió detenerse")


# --- la regla (§7) y los mundos (§8) -----------------------------------------

def _mundo(base, ciudad, rng, ruido=0.015):
    obs = base + rng.normal(0, ruido, len(base))
    return sv.evaluar(sv.analizar(REGLAS, CIUDAD, obs, ciudad + rng.normal(0, 0.005)))


def test_mundo_de_bloques_da_A():
    rng = np.random.default_rng(1)
    lect = [_mundo(REGLAS.bloques, CIUDAD["bloques"], rng)["lectura"] for _ in range(SEMILLAS)]
    assert np.mean([x == "A" for x in lect]) >= 0.95, pd.Series(lect).value_counts().to_dict()


def test_mundo_ingenuo_da_C():
    rng = np.random.default_rng(2)
    lect = [_mundo(REGLAS.ingenua, CIUDAD["ingenua"], rng)["lectura"] for _ in range(SEMILLAS)]
    assert np.mean([x == "C" for x in lect]) >= 0.95, pd.Series(lect).value_counts().to_dict()


def test_mundo_a_mitad_de_camino_se_lee_por_sus_cifras():
    """Sin ruido: los dos errores son idénticos (P2 estricta no se cumple, DI-SV4) y la
    ciudad queda en 49,9 % (P1 se cumple): intermedio, calculado a mano."""
    mitad = (REGLAS.bloques + REGLAS.ingenua) / 2
    a = sv.analizar(REGLAS, CIUDAD, mitad, (CIUDAD["bloques"] + CIUDAD["ingenua"]) / 2)
    assert a["mae_bloques"] == a["mae_ingenua"]
    assert a["ciudad"]["observado"] < 0.5
    assert sv.evaluar(a)["lectura"] == "intermedio"


def test_la_regla_lee_cada_caso():
    base = {"ciudad": {"observado": 0.47}, "mae_bloques": 0.01, "mae_ingenua": 0.04,
            "ganadores_acertados": 20, "spearman": 0.99}
    assert sv.evaluar(base)["lectura"] == "A"
    assert sv.evaluar({**base, "ciudad": {"observado": 0.51}})["lectura"] == "B"
    assert sv.evaluar({**base, "ciudad": {"observado": 0.53}, "mae_bloques": 0.05})["lectura"] == "C"
    assert sv.evaluar({**base, "mae_bloques": 0.05})["lectura"] == "intermedio"


def test_el_resultado_se_puede_escribir():
    rng = np.random.default_rng(3)
    obs = REGLAS.bloques + rng.normal(0, 0.01, 20)
    a = sv.analizar(REGLAS, CIUDAD, obs, 0.48)
    json.dumps({**a, **sv.evaluar(a)}, ensure_ascii=False)


def main():
    print("Segunda vuelta 2026 — pruebas antes de abrir la segunda vuelta\n")
    for k, f in [(k, v) for k, v in list(globals().items()) if k.startswith("test_")]:
        check(k, f)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} prueba(s) fallaron")
        sys.exit(1)
    print("todas las pruebas pasaron")


if __name__ == "__main__":
    main()
