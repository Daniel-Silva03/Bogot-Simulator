"""
tests/test_donante_fechas.py

Pruebas del parseo de `Marca temporal` del donante de opinión
(src/population/loader.py: parsear_marca_temporal).

La columna trae tres formatos mezclados por un round-trip de hoja de
cálculo, y uno de ellos tiene ambigüedad día/mes que no se puede resolver
fila por fila. Estos tests fijan la interpretación correcta para que nadie
la cambie por accidente: si alguien "arregla" el parser asumiendo d/m/Y,
el reparto por año se rompe y el test lo dice.

Ejecutar con:  python3 tests/test_donante_fechas.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.population.loader import (
    load_confianza_institucional_donante,
    parsear_marca_temporal,
)

RAIZ = Path(__file__).resolve().parents[1]
ARCHIVO = RAIZ / "data" / "raw" / "base_encuestaconfianza_2024-2025.csv"

# Tamaños de las dos "olas" según DATA_SPECIFICATION.md. El parser tiene
# que reproducirlos por un camino independiente.
N_2024_DOCUMENTADO = 2128
N_2025_DOCUMENTADO = 3159


def _assert(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"  OK: {msg}")


def test_los_tres_formatos():
    """Un caso de cada familia, escrito a mano."""
    print("\n[test_los_tres_formatos]")

    s = pd.Series([
        "2024/12/19 10:32:38 a.\x14\xffm. GMT-5",  # ISO/GMT, Y/m/d
        "12/13/2024 12:05:24",                      # con segundos, m/d/Y (día 13)
        "12/04/2024 11:07",                         # sin segundos, m/d/Y (día 4)
        "1/14/2025 4:52:20",                        # mes de un dígito
        "2/09/2025 8:30",                           # febrero, día 9
    ])
    f = parsear_marca_temporal(s)
    esperado = ["2024-12-19", "2024-12-13", "2024-12-04", "2025-01-14", "2025-02-09"]
    obtenido = [str(d.date()) for d in f]
    _assert(obtenido == esperado, f"las tres familias parsean bien: {obtenido}")


def test_la_ambiguedad_se_resuelve_como_mes_dia():
    """El caso que importa: '12/04/2024' es 4 de diciembre, no 12 de abril.

    No se puede decidir mirando esa fila sola. Se decide porque el primer
    componente de esa familia solo toma {1, 2, 12} —los meses del trabajo
    de campo— mientras el segundo se reparte por todo 1-12."""
    print("\n[test_la_ambiguedad_se_resuelve_como_mes_dia]")

    f = parsear_marca_temporal(pd.Series(["12/04/2024 11:07"]))
    _assert(f.iloc[0].month == 12 and f.iloc[0].day == 4,
            f"'12/04/2024 11:07' se lee como 4 de diciembre (obtuvo {f.iloc[0].date()})")


def test_reproduce_los_tamanos_documentados():
    """La verificación independiente: el reparto por año tiene que dar los
    mismos n que DATA_SPECIFICATION.md documenta para las dos olas."""
    print("\n[test_reproduce_los_tamanos_documentados]")

    if not ARCHIVO.exists():
        print(f"  SALTADO: no está {ARCHIVO.name} en data/raw/")
        return

    df = pd.read_csv(ARCHIVO, sep=";", encoding="latin-1")
    f = parsear_marca_temporal(df[df.columns[0]])

    _assert(f.notna().all(),
            f"las {len(f)} filas parsean, ninguna se descarta")

    por_anio = f.dt.year.value_counts().to_dict()
    _assert(por_anio.get(2024) == N_2024_DOCUMENTADO,
            f"2024: {por_anio.get(2024)} registros = los {N_2024_DOCUMENTADO} documentados")
    _assert(por_anio.get(2025) == N_2025_DOCUMENTADO,
            f"2025: {por_anio.get(2025)} registros = los {N_2025_DOCUMENTADO} documentados")


def test_el_trabajo_de_campo_es_continuo():
    """El hallazgo que invalidó el diseño original del Experimento 1: las
    'dos olas' son una sola recolección continua partida por el cambio de
    año, no dos mediciones separadas en el tiempo.

    Si algún día llega un archivo con olas de verdad separadas, este test
    falla — y eso sería una buena noticia que conviene no pasar por alto."""
    print("\n[test_el_trabajo_de_campo_es_continuo]")

    if not ARCHIVO.exists():
        print(f"  SALTADO: no está {ARCHIVO.name} en data/raw/")
        return

    df = pd.read_csv(ARCHIVO, sep=";", encoding="latin-1")
    f = parsear_marca_temporal(df[df.columns[0]]).dropna()

    print(f"    campo: {f.min().date()} -> {f.max().date()}")
    diario = f.dt.normalize().value_counts().sort_index()
    calendario = pd.date_range(f.min().normalize(), f.max().normalize(), freq="D")
    vacios = int((diario.reindex(calendario, fill_value=0) == 0).sum())

    _assert(vacios <= 5,
            f"solo {vacios} días sin respuestas en {len(calendario)} días de campo: "
            "la recolección es continua")

    frontera = f[(f >= "2024-12-28") & (f <= "2025-01-06")]
    _assert(len(frontera) > 50,
            f"hay {len(frontera)} respuestas a ambos lados del 1 de enero — "
            "el corte por año no separa dos olas, parte una sola recolección")


def test_filtro_por_fechas_en_el_loader():
    print("\n[test_filtro_por_fechas_en_el_loader]")

    if not ARCHIVO.exists():
        print(f"  SALTADO: no está {ARCHIVO.name} en data/raw/")
        return

    completo = load_confianza_institucional_donante(ARCHIVO)
    diciembre = load_confianza_institucional_donante(
        ARCHIVO, desde="2024-12-01", hasta="2024-12-31", incluir_fecha=True)

    _assert(0 < len(diciembre) < len(completo),
            f"el filtro recorta ({len(diciembre)} de {len(completo)} registros)")
    _assert(diciembre["fecha_respuesta"].dt.month.eq(12).all(),
            "y todo lo que devuelve cae en el rango pedido")
    _assert("fecha_respuesta" not in completo.columns,
            "sin incluir_fecha, el donante mantiene su esquema de siempre")

    try:
        load_confianza_institucional_donante(ARCHIVO, desde="2030-01-01")
        raise AssertionError("debería haber fallado con un rango vacío")
    except ValueError as e:
        print(f"  OK: un rango sin registros falla con un mensaje útil\n       ({str(e)[:90]})")


if __name__ == "__main__":
    test_los_tres_formatos()
    test_la_ambiguedad_se_resuelve_como_mes_dia()
    test_reproduce_los_tamanos_documentados()
    test_el_trabajo_de_campo_es_continuo()
    test_filtro_por_fechas_en_el_loader()
    print("\nTodos los tests pasaron.")
