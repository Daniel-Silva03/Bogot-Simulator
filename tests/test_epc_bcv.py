"""
tests/test_epc_bcv.py

Pruebas del cargador de la Encuesta de Percepción Ciudadana de Bogotá Cómo
Vamos. Se ejecuta directo:  python3 tests/test_epc_bcv.py

Requiere el empaquetado en data/raw/bogota_como_vamos/empaquetado_2026-09/
o la variable de entorno BSS_EPC_DIR.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from src.population.epc_bcv import (
    ANIOS_BCV, FACTOR_POR_ANIO, ITEMS, ITEMS_BLOQUEADOS, TOLERANCIA_ANCLA,
    EPCError, ItemNoSoportado,
    anios_en_disco, cargar_bcv, resumen_ola_bcv, serie_bcv,
    verificar_anclas_bcv, robustez_transicion_bcv,
)

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


# -------------------------------------------------------------------------

def test_estan_las_diez_olas():
    hay = anios_en_disco()
    assert set(hay) == set(ANIOS_BCV), f"faltan olas: {set(ANIOS_BCV) - set(hay)}"


def test_todas_cargan_con_su_factor():
    for a in anios_en_disco():
        ola = cargar_bcv(a)
        assert ola.metadatos["factor"] == FACTOR_POR_ANIO[a]
        assert len(ola.datos) > 1000, f"{a}: solo {len(ola.datos)} filas"


def test_ningun_factor_es_constante():
    """El FACTOR1 ≡ 1,0 del empaquetado web de 2025 hacía inútil la ponderación."""
    for a in anios_en_disco():
        ola = cargar_bcv(a)
        assert ola.metadatos["valores_distintos_factor"] > 1, f"{a}: factor constante"
        assert (ola.datos["peso"].dropna() > 0).all(), f"{a}: hay pesos no positivos"


def test_los_items_quedan_dentro_de_la_escala():
    for a in anios_en_disco():
        ola = cargar_bcv(a)
        for item in ola.metadatos["items_disponibles"]:
            s = ola.datos[item].dropna()
            assert s.between(1, 5).all(), f"{a}/{item}: valores fuera de 1-5"
            assert s.isin([1, 2, 3, 4, 5]).all(), f"{a}/{item}: valores no enteros"


def test_el_90_no_entra_como_opinion():
    """DI-B1: el código 90 se cuenta, no se imputa ni se cuela en la escala."""
    ola = cargar_bcv(2025)
    assert ola.metadatos["no_respuesta"]["gestion_alcalde"] > 0, \
        "2025 debería tener códigos 90 en gestion_alcalde"
    assert ola.datos["gestion_alcalde"].max() <= 5


def test_la_cobertura_viaja_con_la_media():
    r = resumen_ola_bcv(cargar_bcv(2024), "gestion_alcalde")
    for clave in ("media", "sd", "cobertura", "n_valida"):
        assert clave in r, f"falta {clave} en el resumen"
    assert 0.5 < r["cobertura"] <= 1.0


def test_las_proporciones_suman_uno():
    r = resumen_ola_bcv(cargar_bcv(2019), "gestion_alcalde")
    total = sum(r[f"p{k}"] for k in range(1, 6))
    assert abs(total - 1.0) < 1e-9, f"las proporciones suman {total}"


def test_la_media_es_coherente_con_las_proporciones():
    r = resumen_ola_bcv(cargar_bcv(2022), "gestion_concejo")
    rearmada = sum(k * r[f"p{k}"] for k in range(1, 6))
    assert abs(rearmada - r["media"]) < 1e-9


def test_los_items_de_imagen_estan_bloqueados():
    """DI-B2: la inversión de códigos no se puede pisar por descuido."""
    for item in ITEMS_BLOQUEADOS:
        try:
            serie_bcv(item)
        except ItemNoSoportado as e:
            assert "invertid" in str(e).lower(), f"{item}: el mensaje no explica la inversión"
        else:
            raise AssertionError(f"{item} debería estar bloqueado")


def test_un_item_que_no_se_pregunto_ese_anio_falla_claro():
    try:
        resumen_ola_bcv(cargar_bcv(2016), "gestion_alcalde")   # GG3 no está en 2016
    except EPCError as e:
        assert "no se preguntó" in str(e)
    else:
        raise AssertionError("2016 no tiene gestion_alcalde; debería fallar")


def test_las_series_tienen_nueve_olas():
    for item in ITEMS:
        s = serie_bcv(item)
        assert len(s) == 9, f"{item}: {len(s)} olas, esperaba 9"
        assert s["anio"].is_monotonic_increasing


def test_las_anclas_publicadas_cuadran():
    """DI-B6: la lección de la ECP 2015. El diccionario es hipótesis; esto es evidencia."""
    v = verificar_anclas_bcv()
    malas = v[~v["pasa"]]
    assert malas.empty, (
        "el cargador no reproduce las cifras publicadas por BCV "
        f"(tolerancia {TOLERANCIA_ANCLA}):\n{malas.to_string(index=False)}"
    )


def test_la_direccion_de_la_escala_no_esta_invertida():
    """Si 1 y 5 estuvieran al revés, la media de 2023 caería del otro lado del ancla."""
    v = verificar_anclas_bcv().iloc[0]
    assert v["obs_1_2"] > v["obs_4_5"], \
        "en 2023 la gestión del Concejo se evalúa mal; si sale al revés, la escala está invertida"


def test_la_transicion_grande_es_robusta():
    """2019->2022 en gestión del alcalde: +0,41 puntos. DI-B7."""
    s = serie_bcv("gestion_alcalde")
    r = robustez_transicion_bcv(s, 2019, 2022)
    assert r["delta"] > 0.3, f"delta inesperado: {r['delta']}"
    assert r["robusto"], (
        "2019->2022 debería ser robusto: los excluidos tendrían que promediar "
        f"{r['media_requerida_excluidos']:.2f}, fuera de [1,5]"
    )


def test_la_transicion_pequena_no_es_robusta():
    """2022->2023 mueve -0,09 con 84 % de cobertura: no está establecida."""
    s = serie_bcv("gestion_alcalde")
    r = robustez_transicion_bcv(s, 2022, 2023)
    assert not r["robusto"], (
        "2022->2023 no debería declararse robusto; si lo hace, la prueba "
        "está siendo demasiado permisiva"
    )


def test_el_concejo_se_mueve_menos_que_el_alcalde():
    """El control tiene que comportarse como control."""
    a = serie_bcv("gestion_alcalde")["media"]
    c = serie_bcv("gestion_concejo")["media"]
    assert (a.max() - a.min()) > 2 * (c.max() - c.min()), (
        f"rango alcalde {a.max()-a.min():.3f} contra concejo {c.max()-c.min():.3f}: "
        "el control no está siendo más plano"
    )


def test_un_anio_que_no_existe_falla_con_su_motivo():
    for a in (2020, 2021):
        try:
            cargar_bcv(a)
        except EPCError as e:
            assert "pandemia" in str(e)
        else:
            raise AssertionError(f"{a} no existe; debería fallar")


# -------------------------------------------------------------------------

if __name__ == "__main__":
    pruebas = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    print(f"EPC (Bogotá Cómo Vamos) — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
