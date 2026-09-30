"""
tests/test_poblacion_epc.py

Pruebas de src/population/poblacion_epc.py (D17, `POBLACION_EPC2023_SPECIFICATION.md`).
Las de lógica usan datos inventados; las últimas usan la EPC 2023 real si está en
esta máquina.
Se ejecuta directo:  python tests/test_poblacion_epc.py
"""

import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
warnings.simplefilter("ignore")

import numpy as np
import pandas as pd

from src.population import epc_bcv as eb
from src.population import poblacion_epc as pe

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


# --- escalas (DI-PE4) ----------------------------------------------------------

def test_la_escala_separa_la_no_respuesta():
    e = {1: "Muy malo", 2: "Malo", 3: "Regular", 4: "Bueno", 5: "Muy bueno", 99: "No sabe / No responde"}
    assert pe.escala_de(e) == ([1, 2, 3, 4, 5], [99])


def test_una_escala_con_hueco_no_es_escala():
    """Así quedaba GG3 2023 antes de la corrección de DI-PE7."""
    assert pe.escala_de({1: "a", 2: "b", 3: "c", 4: "d", 6: "e"}) is None
    assert pe.escala_de({1: "solo una"}) is None


# --- educación (DI-PE1) --------------------------------------------------------

def test_la_educacion_armonizada_cubre_los_dos_lados():
    assert set(pe.EDU_RECEPTOR) == {0, 1, 2, 3, 4, 5}
    assert set(pe.EDU_EPC) == {1, 2, 3, 4, 5, 6, 8, 9}            # 0 = no sabe, fuera
    assert set(pe.EDU_RECEPTOR.values()) == set(pe.EDU_EPC.values()) == {0, 1, 2, 3}


# --- emparejamiento (DI-PE2, DI-PE6) --------------------------------------------

def _mundo(rng, n_rec=600, n_don=300, locs=(1, 2, 3)):
    def gente(n, loc_pool):
        return pd.DataFrame({"cod_loc": rng.choice(loc_pool, n), "sexo": rng.choice(["M", "F"], n),
                             "edad_tramo": rng.integers(0, 5, n), "estrato": rng.integers(1, 7, n).astype(float),
                             "educ_h": rng.integers(0, 4, n)})
    rec = gente(n_rec, list(locs) + [20]).assign(localidad="x", edad=40, factor_expansion=rng.uniform(1, 5, n_rec))
    don = gente(n_don, list(locs)).assign(peso=rng.uniform(1, 5, n_don), donante_id=np.arange(n_don))
    return rec, don


def test_nadie_hereda_a_alguien_de_otra_localidad_y_sumapaz_queda_sin_donante():
    rec, don = _mundo(np.random.default_rng(1))
    a = pe.construir(50, 7, receptor=rec, donante=don)
    con = a.donante_id.notna()
    assert (don.set_index("donante_id").loc[a.loc[con, "donante_id"].astype(int), "cod_loc"].to_numpy()
            == a.loc[con, "cod_loc"].to_numpy()).all()
    assert a.loc[a.cod_loc == 20, "donante_id"].isna().all() and a.loc[a.cod_loc != 20, "donante_id"].notna().all()


def test_mismo_numero_por_localidad_y_pesos_que_suman_la_poblacion():
    rec, don = _mundo(np.random.default_rng(2))
    a = pe.construir(50, 7, receptor=rec, donante=don)
    assert a.cod_loc.value_counts().eq(50).all()
    suma = a.groupby("cod_loc").peso.sum()
    real = rec.groupby("cod_loc").factor_expansion.sum()
    assert np.allclose(suma.to_numpy(), real.loc[suma.index].to_numpy())


def test_reproducible_con_la_misma_semilla():
    rec, don = _mundo(np.random.default_rng(3))
    assert pe.construir(40, 11, receptor=rec, donante=don).equals(pe.construir(40, 11, receptor=rec, donante=don))


def test_el_emparejamiento_exacto_se_marca_bien():
    rec, don = _mundo(np.random.default_rng(4))
    a = pe.construir(50, 7, receptor=rec, donante=don)
    d = don.set_index("donante_id")
    fila = a[a.donante_id.notna()].iloc[0]
    ref = d.loc[int(fila.donante_id)]
    esperado = (fila.sexo == ref.sexo and fila.edad_tramo == ref.edad_tramo
                and fila.estrato == ref.estrato and fila.educ_h == ref.educ_h)
    assert bool(fila.emparejamiento_exacto) == bool(esperado)


# --- datos reales ----------------------------------------------------------------

def _hay_epc():
    try:
        eb.archivo_del_anio(2023)
        return pe.INVENTARIO.exists()
    except eb.EPCError:
        print("         (sin la EPC 2023 en esta máquina: se omite)")
        return False


def test_el_catalogo_real_trae_gg3_corregida_y_deja_fuera_la_imagen():
    if not _hay_epc():
        return
    dentro, fuera = pe.catalogo()
    gg3 = next(c for c in dentro if c["variable"] == "GG3")
    assert gg3["escala"] == [1, 2, 3, 4, 5] and gg3["etiquetas"]["5"] == "Muy buena gestión"
    # GP1_* son las de imagen (invertidas); GP1N_* son otras (desempeño por sector, 2023) y sí entran
    assert not any(c["variable"].startswith("GP1_") or c["variable"] == "GG1" for c in dentro)
    assert len(dentro) == 102, len(dentro)


def test_el_donante_real_tiene_las_19_localidades():
    if not _hay_epc():
        return
    d = pe.cargar_donante()
    assert sorted(d.cod_loc.dropna().unique()) == list(range(1, 20))
    assert int(d.educ_h.isna().sum()) == 2                         # DI-PE1: los dos «no sabe»


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Población EPC 2023 — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
