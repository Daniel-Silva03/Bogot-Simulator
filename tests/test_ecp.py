"""
tests/test_ecp.py

Pruebas del cargador de la Encuesta de Cultura Política (src/population/ecp.py).

Qué protegen, en concreto:

1. Que la localización por nombre siga funcionando cuando DANE renombre
   algo. Los cuatro años ya traen tres nombres distintos para el mismo
   módulo de viviendas y una errata ("Caracteríasticas"); el próximo año
   traerá otra cosa.
2. Que el panel siga siendo el mismo. Los n de Bogotá están escritos a
   mano acá: si un merge se rompe en silencio, o alguien cambia el filtro
   de región, o se re-descarga un archivo distinto, el número cambia y el
   test lo dice.
3. Que P5263S6 y P5263S12 sigan vacíos. Si algún día aparecen con datos,
   este test falla — y es una falla que conviene ver, porque agregaría dos
   ítems a la serie.

Ejecutar con:  python3 tests/test_ecp.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.population.ecp import (
    ANIOS_COMPARABLES,
    ANIOS_NO_COMPARABLES,
    anios_en_disco,
    verificar_anclas,
    ECPError,
    CUADRO9_PUBLICADO_2023,
    COLUMNA_RED_CERCANA,
    ETIQUETAS_COMPOSICION_RED,
    ETIQUETAS_ITEMS,
    ITEMS_CONFIANZA,
    ITEMS_SIN_DATOS,
    ITEMS_UTILES,
    cargar_anio,
    cargar_capital_social,
    cargar_panel,
    cobertura_items,
    describir_items,
    localizar_modulos,
    serie_confianza,
)

RAIZ = Path(__file__).resolve().parents[1]
ECP = RAIZ / "data" / "raw" / "ecp"

# Verificado contra los microdatos descargados el 15-16/09/2026.
N_BOGOTA = {2017: 5137, 2019: 5429, 2021: 4945, 2023: 4451}

# Población 18+ de Bogotá que expanden los ponderadores, en millones.
# Rango amplio a propósito: fija el orden de magnitud, no el valor.
RANGO_EXPANDIDO = (5.5e6, 6.5e6)


def _assert(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"  OK: {msg}")


def _hay_datos(anio=None):
    anios = [anio] if anio else anios_en_disco(ECP)
    return ECP.is_dir() and all((ECP / str(a)).is_dir() for a in anios)


def test_localiza_los_modulos_pese_a_los_nombres():
    """Tres nombres distintos para viviendas y una errata de DANE en 2023.
    Nada de eso debería importar."""
    print("\n[test_localiza_los_modulos_pese_a_los_nombres]")
    if not _hay_datos():
        print(f"  SALTADO: falta {ECP}")
        return

    for anio in anios_en_disco(ECP):
        m = localizar_modulos(ECP, anio)
        for ruta in (m.viviendas, m.caracteristicas, m.democracia):
            _assert(ruta.is_file(), f"{anio}: {ruta.name}")


def test_falla_claro_si_falta_un_anio():
    print("\n[test_falla_claro_si_falta_un_anio]")
    try:
        localizar_modulos(ECP, 1999)
        raise AssertionError("debería haber fallado con un año inexistente")
    except ECPError as e:
        _assert("1999" in str(e), f"el error nombra el año que falta ({str(e)[:70]})")


def test_el_panel_de_bogota_no_cambia():
    """Los n están escritos a mano: si un merge se rompe, se nota."""
    print("\n[test_el_panel_de_bogota_no_cambia]")
    if not _hay_datos():
        print(f"  SALTADO: falta {ECP}")
        return

    for anio, esperado in N_BOGOTA.items():
        p = cargar_anio(ECP, anio)
        _assert(len(p) == esperado, f"{anio}: {len(p):,} personas de Bogotá")

        expandido = p["fex"].sum()
        _assert(RANGO_EXPANDIDO[0] < expandido < RANGO_EXPANDIDO[1],
                f"{anio}: expande a {expandido:,.0f} personas 18+")
        _assert(p["fex"].notna().all() and (p["fex"] > 0).all(),
                f"{anio}: todos los ponderadores son positivos y no nulos")
        _assert(p["edad"].min() >= 18,
                f"{anio}: la edad mínima es {int(p['edad'].min())} — la ECP es 18+")


def test_los_items_estan_en_escala():
    """1-5 o 99. Cualquier otra cosa significa que se leyó mal el archivo."""
    print("\n[test_los_items_estan_en_escala]")
    if not _hay_datos():
        print(f"  SALTADO: falta {ECP}")
        return

    panel = cargar_panel(ECP)
    for item in ITEMS_UTILES:
        valores = panel[item].dropna().unique()
        fuera = sorted(v for v in valores if v not in (1, 2, 3, 4, 5, 99))
        _assert(not fuera, f"{item}: solo 1-5 y 99" if not fuera else str(fuera))


def test_seis_y_doce_siguen_vacios():
    """Declarados en el DDI, nunca levantados en campo (DI-C3).

    Si este test falla, NO lo 'arregles' borrando el ítem de
    ITEMS_SIN_DATOS sin mirar: significa que un año trae datos que antes no
    tenía, y hay que revisar si la serie puede crecer a 15 ítems."""
    print("\n[test_seis_y_doce_siguen_vacios]")
    if not _hay_datos():
        print(f"  SALTADO: falta {ECP}")
        return

    cob = cobertura_items(cargar_panel(ECP))
    for item in ITEMS_SIN_DATOS:
        n = int(cob.loc[item, list(anios_en_disco(ECP))].fillna(0).sum())
        _assert(n == 0, f"{item}: {n} respuestas en los cuatro años")
    utilizables = cob.index[cob["utilizable"]].tolist()
    _assert(utilizables == list(ITEMS_UTILES),
            f"la intersección son {len(utilizables)} ítems, los mismos de ITEMS_UTILES")


def test_la_serie_es_comparable_entre_anios():
    """El punto de todo esto: cuatro mediciones de lo mismo."""
    print("\n[test_la_serie_es_comparable_entre_anios]")
    if not _hay_datos():
        print(f"  SALTADO: falta {ECP}")
        return

    serie = serie_confianza(cargar_panel(ECP))
    _assert(len(serie) == len(ITEMS_UTILES) * len(anios_en_disco(ECP)),
            f"{len(serie)} filas = {len(ITEMS_UTILES)} ítems × {len(anios_en_disco(ECP))} años")
    _assert(serie["media"].between(1, 5).all(),
            f"todas las medias caen en la escala [{serie['media'].min():.2f}, "
            f"{serie['media'].max():.2f}]")
    _assert(serie["pct_no_sabe"].max() < 10,
            f"la no-respuesta nunca pasa del 10% (máx {serie['pct_no_sabe'].max():.1f}%)")

    # Sin esto la serie no sirve para validar dinámica: si nada se mueve
    # entre años, no hay nada que el modelo tenga que reproducir.
    rango = serie.pivot(index="item", columns="anio", values="media")
    amplitud = (rango.max(axis=1) - rango.min(axis=1))
    _assert(amplitud.max() > 0.2,
            f"hay movimiento real entre años (el ítem que más se mueve recorre "
            f"{amplitud.max():.2f} puntos de la escala)")


def test_la_ponderacion_cambia_el_resultado():
    """Si ponderar no cambiara nada, el ponderador estaría mal leído."""
    print("\n[test_la_ponderacion_cambia_el_resultado]")
    if not _hay_datos(2023):
        print(f"  SALTADO: falta {ECP}/2023")
        return

    p = cargar_anio(ECP, 2023)
    con = serie_confianza(p, ponderar=True).set_index("item")["media"]
    sin = serie_confianza(p, ponderar=False).set_index("item")["media"]
    dif = (con - sin).abs()
    _assert(dif.max() > 1e-6,
            f"ponderar mueve las medias (máx {dif.max():.4f} puntos)")
    _assert(dif.max() < 0.5,
            f"pero no las da vuelta (máx {dif.max():.4f}) — un salto grande sería "
            "señal de ponderadores mal cruzados")


def test_los_quince_actores_estan_nombrados():
    """Los nombres salieron del formulario de la ECP 2023, y la
    correspondencia letra -> código Sxx no la publica nadie.

    Este test fija las tres anclas que la confirman. Si alguien reordena
    ETIQUETAS_ITEMS, se rompe."""
    print("\n[test_los_quince_actores_estan_nombrados]")
    _assert(len(ETIQUETAS_ITEMS) == 15, f"están los 15 actores")
    _assert(ETIQUETAS_ITEMS["P5263S6"] == "Asamblea departamental"
            and ETIQUETAS_ITEMS["P5263S12"] == "Gobernación",
            "S6 y S12 son las dos instituciones departamentales — por eso Bogotá no las tiene")
    _assert("Partidos" in ETIQUETAS_ITEMS["P5263S10"],
            "S10, el más desconfiado de los cuatro años, es Partidos políticos")
    _assert("Militares" in ETIQUETAS_ITEMS["P5263S3"]
            and "Registradur" in ETIQUETAS_ITEMS["P5263S14"],
            "S3 y S14, los más confiados, son Fuerzas Militares y Registraduría")
    _assert("no aplica a Bogotá" in describir_items(),
            "describir_items() marca las dos que no aplican")


def test_cada_codigo_apunta_a_la_misma_institucion():
    """DI-C10. Los metadatos de DANE no alcanzan para decidir si un año se apila.

    Los 15 ítems comparten una sola etiqueta genérica, así que un cambio en
    qué institución hay detrás de cada código es INVISIBLE en el DDI. Solo se
    ve en los datos, por las anclas: S6 y S12 vacíos (Bogotá no tiene Asamblea
    ni Gobernación), S10 el más desconfiado (Partidos políticos), y el más
    confiado entre Fuerzas Militares y Registraduría.

    Así se descubrió que 2015 NO era apilable pese a traer los mismos nombres
    de variable y la misma escala. Este test existe para que el próximo año
    que llegue con los códigos corridos falle acá y no dentro de una serie.
    """
    print("\n[test_cada_codigo_apunta_a_la_misma_institucion]")
    t = verificar_anclas(cargar_panel(ECP)).set_index("anio")
    for anio, fila in t.iterrows():
        _assert(bool(fila.apilable),
                f"{anio}: anclas OK (vacíos {fila.vacios_correctos}, "
                f"mín {fila.minimo}, máx {fila.maximo})")
    _assert(2015 in ANIOS_NO_COMPARABLES,
            "2015 está registrado como no apilable, con su razón")
    _assert(2015 not in anios_en_disco(ECP),
            "anios_en_disco() no devuelve 2015 aunque esté descargado")


def test_los_dos_vacios_son_de_bogota_no_del_dataset():
    """La comprobación que convirtió 'faltan datos' en un hecho
    institucional: S6 y S12 están llenas en las otras cuatro regiones."""
    print("\n[test_los_dos_vacios_son_de_bogota_no_del_dataset]")
    if not _hay_datos(2023):
        print(f"  SALTADO: falta {ECP}/2023")
        return

    pais = cargar_anio(ECP, 2023, region=None)
    for item in ITEMS_SIN_DATOS:
        s = pd.to_numeric(pais[item], errors="coerce")
        en_bogota = int(s[pais["REGION"] == 1].between(1, 5).sum())
        fuera = int(s[pais["REGION"] != 1].between(1, 5).sum())
        _assert(en_bogota == 0 and fuera > 1000,
                f"{item} ({ETIQUETAS_ITEMS[item]}): 0 en Bogotá, {fuera:,} en el resto del país")

def test_la_composicion_de_red_reproduce_el_cuadro_publicado():
    """La prueba que convierte la asignación de P2051S* en un hecho.

    Las 11 descripciones no vienen etiquetadas en ningún metadato y su
    correspondencia con los códigos S1..S11 no está publicada. Se estableció
    reproduciendo los porcentajes del Cuadro 9 del anexo de DANE. Este test
    vuelve a calcularlos: si la asignación o el denominador se tocan, deja de
    coincidir y se nota.

    El denominador es P2047 + P2049 (visitas frecuentes + red de apoyo), que
    es como DANE define 'red cercana de apoyo y confianza'. Con P2047 solo,
    los porcentajes salen ~1,4 veces más altos."""
    print("\n[test_la_composicion_de_red_reproduce_el_cuadro_publicado]")
    if not _hay_datos(2023):
        print(f"  SALTADO: falta {ECP}/2023")
        return

    from src.population.ecp import localizar_modulos, leer_tabla
    m = localizar_modulos(ECP, 2023)
    if m.capital_social is None:
        print("  SALTADO: falta el módulo Capital Social de 2023")
        return

    viv = leer_tabla(m.viviendas)
    cs = leer_tabla(m.capital_social).merge(
        viv[["DIRECTORIO", "P3", "FEX_P"]], on="DIRECTORIO", how="left")
    w = pd.to_numeric(cs["FEX_P"], errors="coerce")
    limpio = lambda c: pd.to_numeric(cs[c], errors="coerce").where(
        lambda s: ~s.isin([98, 99]))
    tam = (limpio("P2047").fillna(0) + limpio("P2049").fillna(0)).where(lambda s: s > 0)
    clase = pd.to_numeric(cs["P3"], errors="coerce")
    dominios = [cs.index.notna(), clase == 1, clase == 2]

    peor = 0.0
    for col, publicado in CUADRO9_PUBLICADO_2023.items():
        v = limpio(col)
        for i, dom in enumerate(dominios):
            ok = dom & v.notna() & tam.notna() & w.notna()
            calc = 100 * np.sum(w[ok] * v[ok]) / np.sum(w[ok] * tam[ok])
            peor = max(peor, abs(calc - publicado[i]))
    _assert(peor <= 0.2,
            f"las 11 columnas reproducen el Cuadro 9 en los 3 dominios "
            f"(peor discrepancia {peor:.2f} pp sobre 33 comparaciones)")
    _assert(len(set(ETIQUETAS_COMPOSICION_RED.values())) == 11,
            "las 11 descripciones son distintas entre sí")


if __name__ == "__main__":
    test_localiza_los_modulos_pese_a_los_nombres()
    test_falla_claro_si_falta_un_anio()
    test_el_panel_de_bogota_no_cambia()
    test_los_items_estan_en_escala()
    test_seis_y_doce_siguen_vacios()
    test_la_serie_es_comparable_entre_anios()
    test_la_ponderacion_cambia_el_resultado()
    test_los_quince_actores_estan_nombrados()
    test_cada_codigo_apunta_a_la_misma_institucion()
    test_los_dos_vacios_son_de_bogota_no_del_dataset()
    test_la_composicion_de_red_reproduce_el_cuadro_publicado()
    print("\nTodos los tests pasaron.")

