"""
tests/test_poblacion_epc_olas.py

Pruebas de src/population/poblacion_epc_olas.py con olas INVENTADAS.
Se ejecuta directo:  python tests/test_poblacion_epc_olas.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.population import poblacion_epc as pe
from src.population import poblacion_epc_olas as po

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


CAT = [{"variable": "A", "codigo": "A23", "escala": [1, 2, 3, 4, 5]},
       {"variable": "B", "codigo": "B23", "escala": [1, 2, 3, 4, 5]}]
ANIOS = {"A": (2022, 2023, 2024), "B": (2023,)}
COD = {("A", 2022): "A_22", ("A", 2023): "A23", ("A", 2024): "A_24", ("B", 2023): "B23"}


def olas(n=300, semilla=0):
    rng = np.random.default_rng(semilla)
    out = {}
    for a in po.ANIOS:
        loc = rng.integers(1, 4, n)
        d = pd.DataFrame({"peso": rng.uniform(0.5, 2, n), "cod_loc": loc,
                          "sexo": rng.choice(["M", "F"], n), "edad_tramo": rng.integers(0, 5, n),
                          "estrato": rng.integers(1, 7, n), "conglomerado": [f"{a}|{l}|{i % 20}" for i, l in enumerate(loc)],
                          # la misma pregunta con otro nombre cada año; el valor delata el año
                          {2022: "A_22", 2023: "A23", 2024: "A_24"}[a]: np.full(n, a - 2021)})
        if a == 2023:
            d["B23"] = 5
        out[a] = d
    return out


def armar(**kw):
    return po.armonizar_donantes(olas(**kw), CAT, ANIOS, lambda v, a: COD.get((v, a)))


def test_cada_anio_aporta_su_columna_bajo_el_nombre_de_2023():
    d = armar()
    for a in po.ANIOS:
        assert (d[d.anio == a].A23 == a - 2021).all()


def test_una_pregunta_que_no_se_junta_queda_vacia_en_los_otros_anios():
    d = armar()
    assert d[d.anio != 2023].B23.isna().all() and (d[d.anio == 2023].B23 == 5).all()


def test_los_ids_de_donante_son_unicos_entre_anios():
    d = armar()
    assert d.donante_id.is_unique and len(d) == 900


def test_si_falta_una_columna_que_deberia_estar_se_detiene():
    o = olas()
    o[2024] = o[2024].drop(columns="A_24")
    try:
        po.armonizar_donantes(o, CAT, ANIOS, lambda v, a: COD.get((v, a)))
    except po.PoblacionOlasError:
        return
    raise AssertionError("debió detenerse")


def test_el_emparejamiento_sin_educacion_respeta_la_localidad_y_mezcla_los_anios():
    d = armar()
    rng = np.random.default_rng(1)
    n = 600
    ag = pd.DataFrame({"agent_id": np.arange(n), "cod_loc": rng.integers(1, 4, n), "sexo": rng.choice(["M", "F"], n),
                       "edad_tramo": rng.integers(0, 5, n), "estrato": rng.integers(1, 7, n),
                       "educ_h": np.nan, "peso": 1.0})
    m = pe.emparejar(ag, d, 7, po.VARS_DISTANCIA)
    assert m.donante_id.notna().all()
    loc_don = d.set_index("donante_id").cod_loc.loc[m.donante_id.astype(int)].to_numpy()
    assert (loc_don == m.cod_loc.to_numpy()).all()
    v = po.verificar_olas(m, d)
    assert set(v["emparejamiento_exacto_por_anio_del_donante"]) == set(po.ANIOS)
    assert v["mayor_fraccion_de_un_anio_en_agentes"] < 0.6


def test_los_pesos_de_cada_ola_suman_sus_encuestados_en_cada_localidad():
    """DI-PO5: un año con pesos planos no se come a los demás dentro de una localidad."""
    d = pd.DataFrame({"cod_loc": [1, 1, 1, 2, 2], "peso": [10.0, 30.0, 20.0, 5.0, 5.0]})
    r = po.reescalar_por_localidad(d)
    assert r.groupby("cod_loc").peso.sum().to_dict() == {1: 3.0, 2: 2.0}
    assert np.isclose(r.peso[1] / r.peso[0], 3.0)


def test_el_2023_sigue_emparejando_con_educacion():
    """DI-PO1: el valor por defecto no cambió."""
    assert pe.VARS_DISTANCIA == ["edad_tramo", "estrato", "educ_h"]
    import inspect
    assert inspect.signature(pe.emparejar).parameters["vars_distancia"].default is pe.VARS_DISTANCIA


def test_la_armonizacion_real_cubre_el_catalogo():
    """Solo metadatos (años por pregunta), ninguna respuesta."""
    if not po.ARMONIZADO.exists():
        print("         (sin la armonización en esta máquina: se omite)")
        return
    a = po.anios_por_pregunta()
    assert len(a) == 102 and all(2023 in x for x in a.values())
    assert a["GG3"] == (2022, 2023)


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Población 2022-2024 — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
