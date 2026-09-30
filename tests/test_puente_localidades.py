"""
tests/test_puente_localidades.py

Pruebas de src/experiments/puente_localidades.py antes de la corrida real
(`PUENTE_LOCALIDADES_SPECIFICATION.md` §8). Todo con encuestados INVENTADOS de tres
años: ninguna prueba calcula nada sobre las respuestas reales de la EPC ni llama a la API.
Se ejecuta directo:  python tests/test_puente_localidades.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.experiments import puente_localidades as pl

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


ESCALA = [1, 2, 3, 4, 5]
ETQ = {"1": "Muy insatisfecho", "2": "Algo insatisfecho", "3": "Ni lo uno ni lo otro",
       "4": "Algo satisfecho", "5": "Muy satisfecho", "99": "No sabe / No responde"}
N_CAT = 8


def ficha(v):
    return {"variable": v, "codigo": v, "nombre": v, "pregunta": f"¿{v}?", "escala": ESCALA,
            "no_respuesta": [99], "etiquetas": ETQ}


def mundo(semilla, transmite=True, n=1500, salto_2024=0.0, anios_y=pl.ANIOS, anios_c1=pl.ANIOS):
    """Tres olas inventadas. Cada localidad tiene un efecto g en las preguntas del
    catálogo. La escondida Y es C0 − C1 a nivel de persona; su geografía es g
    (transmite=True: el puente la hereda) o sale del estrato, que la demografía ve
    (transmite=False: el puente no la hereda). `salto_2024` sube C0 en 2024 a todos."""
    rng = np.random.default_rng(semilla)
    g = rng.normal(0, 0.8, 20)
    estrato_loc = rng.integers(1, 7, 20)
    olas = {}
    for a in pl.ANIOS:
        loc = rng.integers(1, 20, n)
        estrato = np.clip(estrato_loc[loc] + rng.integers(-1, 2, n), 1, 6)
        ind = rng.normal(0, 1, (n, N_CAT))
        geo = g[loc][:, None] * (np.arange(N_CAT) < 2)[None, :] if transmite else 0 * ind
        lat = ind + geo
        cat = {f"C{i}": np.clip(np.round(3 + lat[:, i] + (salto_2024 if (a == 2024 and i == 0) else 0)), 1, 5)
               for i in range(N_CAT)}
        geo_y = (g[loc] - 0) if transmite else 0.9 * (estrato - 3.5)
        y = np.clip(np.round(3 + 0.7 * (ind[:, 0] - ind[:, 1]) / 1.4 + geo_y + rng.normal(0, 0.5, n)), 1, 5)
        if transmite:   # que C0 − C1 no se cancele la geografía: C1 va sin ella
            cat["C1"] = np.clip(np.round(3 + ind[:, 1]), 1, 5)
        olas[a] = pd.DataFrame({**cat, "Y": y, "peso": rng.uniform(0.5, 2, n), "cod_loc": loc,
                                "sexo": rng.choice(["M", "F"], n), "edad_tramo": rng.integers(0, 5, n),
                                "estrato": estrato})
    fp = {f"C{i}": ficha(f"C{i}") for i in range(N_CAT)}
    fe = {"Y": ficha("Y")}
    anios = {**{v: pl.ANIOS for v in fp}, "C1": tuple(anios_c1), "Y": tuple(anios_y)}
    datos = pl.DatosOlas(olas, lambda v, a: v, anios, fp, fe)
    return datos, fp, fe, anios, olas


BUENO = {"preguntas": [{"codigo": "C0", "sentido": "+", "peso": 3}, {"codigo": "C1", "sentido": "-", "peso": 3}],
         "nivel": 3.0, "justificacion": ""}


def correr(datos, fe, anios, puentes, conf=0.8):
    return pl.analizar(datos, fe, {"Y": puentes}, {"Y": conf}, anios)["por_pregunta"]["Y"]


# --- los dos mundos del pre-registro (§8) ---------------------------------------

def test_donde_la_geografia_se_transmite_el_puente_gana_por_localidad():
    d, fp, fe, anios, _ = mundo(1, transmite=True)
    p = correr(d, fe, anios, [BUENO] * 3)
    assert p["r_loc"] > p["demografia"]["r_loc"] and p["r_loc"] > 0.6, p
    assert p["rho_ind"] > p["demografia"]["rho_ind"], p


def test_donde_no_se_transmite_gana_la_demografia():
    d, fp, fe, anios, _ = mundo(2, transmite=False)
    p = correr(d, fe, anios, [BUENO] * 3)
    assert p["demografia"]["r_loc"] > p["r_loc"], p


# --- cómo se juntan los años (§4, DI-PL2, DI-PL3) --------------------------------

def test_cada_pregunta_se_estandariza_dentro_de_cada_anio():
    d, *_ = mundo(3, salto_2024=1.5)
    for a in pl.ANIOS:
        m = d.anio == a
        assert abs(np.sum(d.z["C0"][m] * d.w[m]) / np.sum(d.w[m])) < 1e-9


def test_un_salto_de_nivel_entre_anios_no_se_vuelve_geografia():
    """Sin estandarizar por año, subir C0 en 2024 cambiaría el puntaje de quien respondió en 2024."""
    d, *_ = mundo(4, salto_2024=1.5)
    s = d.puntaje([{"codigo": "C0", "sentido": "+", "peso": 1}])
    assert abs(s[d.anio == 2024].mean() - s[d.anio == 2022].mean()) < 0.15


def test_una_pregunta_del_puente_que_no_existe_ese_anio_cuenta_como_cero():
    d, *_ = mundo(5, anios_c1=(2022, 2023))
    assert np.all(d.z["C1"][d.anio == 2024] == 0) and d.disponible["C1"] == (2022, 2023)
    assert d.peso_disponible(BUENO["preguntas"]) == {2022: 1.0, 2023: 1.0, 2024: 0.5}


def test_la_escondida_solo_cuenta_en_sus_anios():
    d, fp, fe, anios, _ = mundo(6, anios_y=(2022, 2023))
    x, ok = d.y["Y"]
    assert not ok[d.anio == 2024].any() and ok[d.anio != 2024].all()
    p = correr(d, fe, anios, [BUENO] * 3)
    assert p["anios"] == [2022, 2023] and p["n"] == int((d.anio != 2024).sum())


def test_una_pregunta_que_deberia_estar_y_no_esta_detiene_todo():
    _, fp, fe, anios, olas = mundo(7)
    olas[2024] = olas[2024].drop(columns="C3")
    try:
        pl.DatosOlas(olas, lambda v, a: v, anios, fp, fe)
    except pl.PuenteLocalidadesError:
        return
    raise AssertionError("debió detenerse")


# --- la regla (§5, §6) y la regla de no gastar (DI-PL1) -------------------------

def _a(c1, c2, geo=7, r_geo=0.6):
    P = {}
    for i in range(11):
        P[f"V{i}"] = {"r_loc": 0.9 if i < c1 else 0.1, "rho_ind": 0.5 if i < c2 else 0.0,
                      "demografia": {"r_loc": 0.5, "rho_ind": 0.2},
                      "confiabilidad_sb": 0.7 if i < geo else 0.1}
        if i < geo and i >= c1:
            P[f"V{i}"]["r_loc"] = r_geo
    return {"por_pregunta": P}


def test_la_regla_lee_cada_caso():
    assert pl.evaluar(_a(8, 11))["lectura"] == "A"
    assert pl.evaluar(_a(7, 11))["lectura"] == "B"
    assert pl.evaluar(_a(11, 7))["lectura"] == "—"
    assert pl.evaluar(_a(8, 8))["predicciones"]["P1"]["cuenta"] == 8


def test_p3_usa_la_mediana_de_las_siete_con_geografia():
    assert pl.evaluar(_a(3, 11, r_geo=0.6))["predicciones"]["P3"]["se_cumple"]
    assert not pl.evaluar(_a(3, 11, r_geo=0.4))["predicciones"]["P3"]["se_cumple"]
    try:
        pl.evaluar(_a(8, 11, geo=6))
    except pl.PuenteLocalidadesError:
        return
    raise AssertionError("con 6 preguntas de geografía debió detenerse")


def test_sin_la_cache_no_se_llama_al_modelo():
    import tempfile
    from src.experiments import experimento9 as e9
    from src.experiments import puente as pu
    _, fp, fe, *_ = mundo(8)
    with tempfile.TemporaryDirectory() as tmp:
        cache = e9.Cache(Path(tmp) / "cache.json")
        try:
            pu.recolectar(fe, fp, pl.sin_llamadas, cache, "modelo")
        except pl.PuenteLocalidadesError:
            return
    raise AssertionError("debió negarse a llamar")


def test_las_escondidas_son_las_once_del_preregistro():
    assert len(pl.ESCONDIDAS) == 11 and "SA4" not in pl.ESCONDIDAS


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Puente por localidades — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
