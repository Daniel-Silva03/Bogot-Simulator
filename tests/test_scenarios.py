"""
tests/test_scenarios.py

Pruebas del motor de escenarios (DI-E1..DI-E5, DI-M1s..DI-M4s).
Se ejecuta directo:  python tests/test_scenarios.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.opinion.forzamiento_categorico import ForzamientoInfactible
from src.scenarios.especificacion import EscenarioError, cargar
from src.scenarios.motor import (
    comparar_con_nulo, correr, descomponer, escenario_nulo,
)

RAIZ = Path(__file__).resolve().parents[1]
FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def escribir(yaml_txt, tmp):
    p = Path(tmp) / "esc.yaml"
    p.write_text(yaml_txt, encoding="utf-8")
    return p


BASE = """
nombre: prueba
poblacion: {pob}
corridas: 20
semilla: 1
periodos:
  - etiqueta: t1
    nivel:      {{cambio: {n}, incertidumbre: {iu}}}
    dispersion: {{cambio: 0.0, incertidumbre: 0.0}}
"""


def _poblacion(tmp, valores):
    p = Path(tmp) / "pob.csv"
    pd.DataFrame({"opinion_t0": valores}).to_csv(p, index=False)
    return p.relative_to(RAIZ) if str(p).startswith(str(RAIZ)) else p


def _esc(tmp, n=-0.1, iu=0.02, valores=None):
    valores = valores if valores is not None else np.repeat([1., 2, 3, 4, 5], 200)
    p = Path(tmp) / "pob.csv"
    pd.DataFrame({"opinion_t0": valores}).to_csv(p, index=False)
    y = escribir(BASE.format(pob=str(p), n=n, iu=iu), tmp)
    return cargar(y, raiz=Path("/"))


# --- especificación --------------------------------------------------------

def test_la_incertidumbre_es_obligatoria():
    """DI-E1: sin ella el escenario se lee como predicción."""
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "pob.csv"
        pd.DataFrame({"opinion_t0": np.repeat([1., 2, 3], 100)}).to_csv(p, index=False)
        y = escribir(f"""
nombre: sin incertidumbre
poblacion: {p}
periodos:
  - etiqueta: t1
    nivel:      {{cambio: -0.1}}
    dispersion: {{cambio: 0.0, incertidumbre: 0.0}}
""", tmp)
        try:
            cargar(y, raiz=Path("/"))
        except EscenarioError as e:
            assert "incertidumbre" in str(e) and "predicción" in str(e)
        else:
            raise AssertionError("debería exigir incertidumbre")


def test_la_poblacion_puede_venir_en_parquet():
    """DI-E5: las poblaciones reproducibles (DI-M2) se escriben en .parquet."""
    with tempfile.TemporaryDirectory() as tmp:
        valores = np.repeat([1., 2, 3, 4, 5], 100)
        p = Path(tmp) / "pob.parquet"
        pd.DataFrame({"opinion_t0": valores}).to_parquet(p, index=False)
        esc = cargar(escribir(BASE.format(pob=str(p), n=-0.1, iu=0.02), tmp), raiz=Path("/"))
        assert len(esc.poblacion) == 500 and list(esc.grilla) == [1., 2, 3, 4, 5]


def test_cambio_y_valor_son_excluyentes():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "pob.csv"
        pd.DataFrame({"opinion_t0": np.repeat([1., 2, 3], 100)}).to_csv(p, index=False)
        y = escribir(f"""
nombre: ambos
poblacion: {p}
periodos:
  - etiqueta: t1
    nivel:      {{cambio: -0.1, valor: 2.0, incertidumbre: 0.0}}
    dispersion: {{cambio: 0.0, incertidumbre: 0.0}}
""", tmp)
        try:
            cargar(y, raiz=Path("/"))
        except EscenarioError:
            pass
        else:
            raise AssertionError("cambio y valor a la vez no tiene sentido")


def test_un_escenario_imposible_se_rechaza_al_cargar():
    """DI-E3: mejor ahora que en la corrida 137 de 200."""
    with tempfile.TemporaryDirectory() as tmp:
        try:
            _esc(tmp, n=-5.0, iu=0.0)          # media por debajo de la escala
        except ForzamientoInfactible as e:
            assert "escala no admite" in str(e) or "fuera de la grilla" in str(e)
        else:
            raise AssertionError("una caída de 5 puntos en una escala 1-5 no existe")


def test_los_bordes_de_la_incertidumbre_tambien_se_verifican():
    """El centro factible no basta si media corrida se cae."""
    with tempfile.TemporaryDirectory() as tmp:
        try:
            _esc(tmp, n=-1.9, iu=0.5)          # centro cabe, borde bajo no
        except ForzamientoInfactible:
            pass
        else:
            raise AssertionError("el borde de la incertidumbre debería rechazarse")


def test_la_grilla_sale_de_la_poblacion():
    with tempfile.TemporaryDirectory() as tmp:
        e = _esc(tmp)
        assert list(e.grilla) == [1, 2, 3, 4, 5]


# --- motor -----------------------------------------------------------------

def test_la_salida_no_es_una_linea():
    """Lo esencial: cuantiles, no un número por periodo."""
    with tempfile.TemporaryDirectory() as tmp:
        r = correr(_esc(tmp))
        res = r.resumen()
        for c in ("p05", "p50", "p95"):
            assert c in res.columns
        assert res.p95.iloc[-1] > res.p05.iloc[-1], "el intervalo no puede ser degenerado"


def test_la_simulacion_no_se_sale_de_la_grilla():
    with tempfile.TemporaryDirectory() as tmp:
        e = _esc(tmp)
        r = correr(e)
        d = r.distribucion_media()
        assert set(d.categoria) == set(e.grilla)
        assert abs(d.proporcion.sum() - 1) < 1e-9


def test_el_escenario_nulo_no_se_mueve():
    """DI-M2s: la referencia obligatoria tiene que quedarse quieta."""
    with tempfile.TemporaryDirectory() as tmp:
        e = _esc(tmp)
        rn = correr(escenario_nulo(e), corridas=40)
        assert abs(rn.medias[:, -1].mean() - e.media_inicial) < 0.02


def test_el_nulo_conserva_incertidumbre_muestral():
    """Quieto no es determinista: mil agentes siguen siendo una muestra."""
    with tempfile.TemporaryDirectory() as tmp:
        rn = correr(escenario_nulo(_esc(tmp)), corridas=60)
        assert np.std(rn.medias[:, -1]) > 0, "el nulo no puede tener varianza cero"


def test_mas_incertidumbre_declarada_da_intervalos_mas_anchos():
    with tempfile.TemporaryDirectory() as tmp:
        a = correr(_esc(tmp, iu=0.01), corridas=80)
        b = correr(_esc(tmp, iu=0.10), corridas=80)
        assert np.std(b.medias[:, -1]) > np.std(a.medias[:, -1])


def test_la_descomposicion_separa_las_fuentes():
    """DI-M1s: si domina la muestral, la respuesta es subir N, no afinar el supuesto."""
    with tempfile.TemporaryDirectory() as tmp:
        t = descomponer(_esc(tmp, iu=0.08), corridas=60)
        det = t.loc[t.fuente == "ninguna (determinista)", "sd_de_la_media_final"].iloc[0]
        sup = t.loc[t.fuente == "solo del supuesto", "sd_de_la_media_final"].iloc[0]
        mue = t.loc[t.fuente == "solo muestral", "sd_de_la_media_final"].iloc[0]
        assert det == 0.0, "sin sorteos no puede haber dispersión"
        assert sup > mue, "con incertidumbre declarada alta debería dominar el supuesto"


def test_la_comparacion_con_el_nulo_trae_el_error():
    with tempfile.TemporaryDirectory() as tmp:
        c = comparar_con_nulo(_esc(tmp), corridas=40)
        assert "veces_el_error" in c.columns
        assert (c.diferencia < 0).all(), "un escenario de caída tiene que dar diferencias negativas"


def test_reproducible_con_la_misma_semilla():
    with tempfile.TemporaryDirectory() as tmp:
        e = _esc(tmp)
        a = correr(e, corridas=25).medias
        b = correr(e, corridas=25).medias
        assert np.array_equal(a, b), "misma semilla, mismo resultado"


# -------------------------------------------------------------------------

if __name__ == "__main__":
    pruebas = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"Motor de escenarios — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
