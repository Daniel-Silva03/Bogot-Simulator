"""Prepara la serie temporal que alimenta el Hito 2 del tablero.

Produce `data/processed/viz/serie_bogota.json`: las mediciones reales que el
proyecto ya cargó, año por año, cada una con su media ponderada, su error
estándar y el tamaño de muestra que la sostiene.

**No hay simulación acá.** Son datos de encuesta, puestos en una línea de
tiempo para poder leerlos. Es el paso que convierte el mapa en un instrumento
de lectura antes de que el modelo tenga nada que decir.

Decisiones de implementación
----------------------------
DI-V37 Las dos series NO tienen el mismo estatus estadístico y el paquete lo
       dice por punto, no en una nota al pie.

       La EPC de Bogotá Cómo Vamos trae identificador de manzana en seis de
       sus diez olas, así que ahí el error estándar se estima **con el diseño
       real** (linealización de Taylor sobre conglomerados, `media_disenio`).
       La ECP del DANE no publica variables de diseño en el microdato
       distribuido, así que su error solo puede calcularse como muestreo
       aleatorio simple e inflarse por un DEFF **prestado** de la EPC
       (`deff_prestado`, DI-D1).

       Cada punto lleva `con_diseno: true|false`. La página dibuja las bandas
       aproximadas con otro tratamiento visual que las medidas. Pintar las dos
       iguales sería afirmar una precisión que solo una de las dos fuentes
       respalda.

DI-V38 Las dos series comparten la escala 1–5 y **no se dibujan como una sola
       línea**. Miden cosas distintas: la ECP mide confianza en trece
       instituciones nacionales y distritales; la EPC mide evaluación de la
       gestión del alcalde. Que coincidan en el rango es una coincidencia del
       instrumento, no una equivalencia de concepto. Van como dos series
       separadas, cada una con su nombre y su pregunta, y el paquete no
       calcula ninguna diferencia entre ellas.

DI-V39 Un punto sin medición es un hueco, no una interpolación. La ECP no se
       levantó en 2014, 2016, 2018, 2020 ni 2022; la EPC no tiene 2020 ni
       2021. El JSON trae solo los años medidos y la página dibuja el
       segmento entre dos años consecutivos **marcado como salto** cuando
       median más de dos años. Unir 2013 con 2017 en una recta limpia
       insinúa cuatro años de evolución que nadie observó.

DI-V40 El año 2015 de la ECP queda fuera, con su motivo en el paquete. Los
       códigos apuntan a otras instituciones ese año (DI-C10): incluirlo
       fabricaría un salto que sería un cambio de cuestionario. Se declara en
       `excluidos` en vez de desaparecer en silencio, porque un hueco sin
       explicación invita a que alguien lo "arregle" más adelante.

Uso:
    python src/viz/preparar_serie.py
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.population.ecp import (  # noqa: E402
    ANIOS_COMPARABLES,
    ANIOS_NO_COMPARABLES,
    INDICE_MIN_ITEMS,
    ITEMS_UTILES,
    cargar_anio,
    indice_confianza,
    n_items_confianza,
)
from src.population.epc_bcv import (  # noqa: E402
    EPCError,
    FACTOR_POR_ANIO,
    ITEMS as ITEMS_EPC,
    anios_en_disco as anios_epc,
    cargar_bcv,
)
from src.utils.diseno import (  # noqa: E402
    CONGLOMERADO_POR_ANIO,
    DEFF_MEDIDO_EPC,
    DisenoError,
    deff_prestado,
    media_disenio,
)

DIR_ECP = RAIZ / "data" / "raw" / "ecp"
SALIDA = RAIZ / "data" / "processed" / "viz" / "serie_bogota.json"

#: Salida de respaldo cuando el empaquetado de la EPC no está en disco. Los dos
#: los produce este mismo proyecto; ver `_epc_desde_procesado`.
SERIE_EPC_CSV = RAIZ / "data" / "processed" / "serie_epc_bcv.csv"
DEFF_EPC_CSV = RAIZ / "data" / "processed" / "deff_epc_seis_olas.csv"

#: Más de este número de años entre dos mediciones y el tramo se marca como
#: salto: la línea se dibuja punteada porque no hay nada observado en medio.
SALTO_ANIOS = 2

logger = logging.getLogger("preparar_serie")


def _punto(est, anio: int, extra: dict | None = None) -> dict:
    lo, hi = est.ic95
    return {
        "anio": anio,
        "media": round(float(est.media), 4),
        "ee": round(float(est.ee), 4),
        "ic95": [round(float(lo), 4), round(float(hi), 4)],
        "n": int(est.n),
        "deff": round(float(est.deff), 3),
        "con_diseno": bool(est.con_diseno),
        **(extra or {}),
    }


def serie_ecp() -> dict:
    """Confianza institucional por año, escala 1–5, ponderada por FEX_P.

    El error es SRS ponderado inflado por el DEFF prestado de la EPC: la ECP
    no publica conglomerado ni estrato (DI-V37).
    """
    puntos = []
    for anio in ANIOS_COMPARABLES:
        if not (DIR_ECP / str(anio)).is_dir():
            logger.warning("ECP %s no está en disco; queda fuera de la serie.", anio)
            continue
        panel = cargar_anio(DIR_ECP, anio)
        indice = indice_confianza(panel)
        n_items = n_items_confianza(panel)
        peso = panel["fex"].astype(float)

        ok = indice.notna() & peso.notna() & (peso > 0)
        est = deff_prestado(
            media_disenio(indice[ok], peso[ok]),
            deff=DEFF_MEDIDO_EPC["mediana"],
        )
        puntos.append(_punto(est, anio, {
            "poblacion_expandida": int(round(float(peso[ok].sum()))),
            "items_completos_pct": round(
                100 * float((n_items[ok] == len(ITEMS_UTILES)).mean()), 1),
        }))
        logger.info("ECP %s: media %.4f ± %.4f (n=%d)", anio, est.media, est.ee, est.n)

    # Una serie vacía no es una serie: sin esto el paquete salía con cero
    # puntos y el fallo aparecía mucho después, en la página.
    if not puntos:
        raise SinInsumos(
            f"Ningún año de la ECP está en {DIR_ECP.relative_to(RAIZ).as_posix()}. "
            f"Se esperaba alguno de {list(ANIOS_COMPARABLES)}.")

    return {
        "clave": "ecp_confianza",
        "nombre": "Confianza institucional",
        "fuente": "Encuesta de Cultura Política (DANE), submuestra de Bogotá",
        "pregunta": ("¿Cuánta confianza tiene usted en cada una de las siguientes "
                     "instituciones? — capítulo Democracia"),
        "unidad": f"promedio de hasta {len(ITEMS_UTILES)} instituciones, escala 1–5",
        "escala": [1, 5],
        "anclas": {"1": "no confía", "5": "confía mucho"},
        "direccion": "mayor = más confianza",
        "min_items": INDICE_MIN_ITEMS,
        "con_diseno": False,
        "nota_error": (
            f"La ECP no publica conglomerado ni estrato en el microdato, así que el "
            f"error estándar es el de muestreo aleatorio simple inflado por un DEFF "
            f"PRESTADO de {DEFF_MEDIDO_EPC['mediana']}, medido en la EPC sobre "
            f"{DEFF_MEDIDO_EPC['mediciones']} mediciones. Es una corrección aproximada, "
            f"no una estimación con diseño."),
        "excluidos": [
            {"anio": anio, "motivo": motivo}
            for anio, motivo in sorted(ANIOS_NO_COMPARABLES.items())
            if (DIR_ECP / str(anio)).is_dir()
        ],
        "puntos": puntos,
    }


def _epc_desde_microdato(item: str) -> tuple[list[dict], list[int]]:
    """Recalcula la serie EPC desde los .dta originales. Requiere el empaquetado."""
    puntos, con_diseno_en = [], []
    for anio in anios_epc():
        if anio not in ITEMS_EPC[item]["columnas"]:
            continue
        ola = cargar_bcv(anio)
        d = ola.datos
        if item not in d.columns:
            continue
        peso = d["peso"].astype(float)
        ok = d[item].notna() & peso.notna() & (peso > 0)
        if not ok.any():
            continue

        # El identificador de manzana existe en seis olas; donde está, el error
        # se estima con el diseño real en vez de con un factor prestado.
        col_psu, col_estrato = CONGLOMERADO_POR_ANIO.get(anio, (None, None))
        hay_psu = bool(col_psu) and col_psu in d.columns
        try:
            if hay_psu:
                est = media_disenio(
                    d[item][ok], peso[ok], psu=d[col_psu][ok],
                    estrato=d[col_estrato][ok] if col_estrato in d.columns else None)
            else:
                est = deff_prestado(media_disenio(d[item][ok], peso[ok]))
        except DisenoError as e:
            logger.warning("EPC %s: %s — se cae a SRS con DEFF prestado.", anio, e)
            est = deff_prestado(media_disenio(d[item][ok], peso[ok]))

        if est.con_diseno:
            con_diseno_en.append(anio)
        puntos.append(_punto(est, anio, {
            "factor": FACTOR_POR_ANIO.get(anio),
            "origen": "microdato",
        }))
        logger.info("EPC %s: media %.4f ± %.4f (n=%d, diseño=%s)",
                    anio, est.media, est.ee, est.n, est.con_diseno)
    return puntos, con_diseno_en


def _epc_desde_procesado(item: str) -> tuple[list[dict], list[int]]:
    """Reconstruye la serie EPC desde los CSV ya calculados del proyecto.

    Es la salida cuando el empaquetado de Bogotá Cómo Vamos no está en disco
    —por ejemplo en un entorno donde el microdato no puede estar—. **No inventa
    nada**: la media y el n salen de `serie_epc_bcv.csv` y el error con diseño
    de `deff_epc_seis_olas.csv`, los dos producidos por este mismo proyecto.
    Los años sin DEFF medido caen al prestado y el punto lo dice, igual que en
    el camino del microdato.
    """
    import pandas as pd

    if not (SERIE_EPC_CSV.exists() and DEFF_EPC_CSV.exists()):
        raise SinInsumos(
            f"Sin el empaquetado de la EPC y sin {SERIE_EPC_CSV.name}: no hay de dónde "
            f"sacar la serie de la EPC en esta máquina.")

    serie = pd.read_csv(SERIE_EPC_CSV).query("item == @item")
    deffs = pd.read_csv(DEFF_EPC_CSV).query("item == @item").set_index("anio")

    puntos, con_diseno_en = [], []
    for r in serie.sort_values("anio").itertuples():
        n = int(r.n_valida)
        ee_srs = float(r.sd) / np.sqrt(n)
        if r.anio in deffs.index:
            fila = deffs.loc[r.anio]
            ee, deff, con_diseno = float(fila["ee"]), float(fila["deff"]), True
            con_diseno_en.append(int(r.anio))
        else:
            deff = DEFF_MEDIDO_EPC["mediana"]
            ee, con_diseno = ee_srs * np.sqrt(deff), False
        media = float(r.media)
        puntos.append({
            "anio": int(r.anio),
            "media": round(media, 4),
            "ee": round(float(ee), 4),
            "ic95": [round(media - 1.96 * ee, 4), round(media + 1.96 * ee, 4)],
            "n": n,
            "deff": round(deff, 3),
            "con_diseno": con_diseno,
            "factor": FACTOR_POR_ANIO.get(int(r.anio)),
            "origen": "serie_precalculada",
        })
        logger.info("EPC %s: media %.4f ± %.4f (n=%d, diseño=%s) [precalculada]",
                    r.anio, media, ee, n, con_diseno)
    return puntos, con_diseno_en


def serie_epc(item: str = "gestion_alcalde") -> dict:
    """Evaluación de gestión por año, escala 1–5, con diseño donde lo hay."""
    try:
        puntos, con_diseno_en = _epc_desde_microdato(item)
        origen = "microdato"
    except EPCError as e:
        logger.warning("EPC: %s", e)
        logger.warning("Se reconstruye desde los CSV procesados del proyecto.")
        puntos, con_diseno_en = _epc_desde_procesado(item)
        origen = "serie_precalculada"

    return {
        "clave": f"epc_{item}",
        "nombre": ITEMS_EPC[item]["etiqueta"],
        "fuente": "Encuesta de Percepción Ciudadana (Bogotá Cómo Vamos)",
        "pregunta": ITEMS_EPC[item]["etiqueta"],
        "unidad": "ítem único, escala 1–5",
        "escala": [1, 5],
        "anclas": {"1": "muy mala gestión", "5": "muy buena gestión"},
        "direccion": "mayor = mejor evaluación",
        "con_diseno": True,
        "anios_con_diseno": con_diseno_en,
        "origen": origen,
        "nota_error": (
            "Donde la ola trae identificador de manzana, el error estándar se estima "
            "con el diseño real (linealización de Taylor sobre conglomerados). En las "
            "olas sin identificador se usa el DEFF prestado, y el punto lo dice."),
        "excluidos": [],
        "puntos": puntos,
    }


def tramos(puntos: list[dict]) -> list[dict]:
    """Los segmentos entre mediciones consecutivas, con el salto marcado (DI-V39)."""
    salida = []
    for a, b in zip(puntos, puntos[1:]):
        brecha = b["anio"] - a["anio"]
        salida.append({
            "de": a["anio"], "a": b["anio"], "brecha": brecha,
            "salto": brecha > SALTO_ANIOS,
        })
    return salida


class SinInsumos(RuntimeError):
    """Esta máquina no tiene con qué construir la serie."""


def revisar_insumos() -> None:
    """Falla temprano y con instrucciones si no hay de dónde sacar la serie.

    DI-V42 — El repositorio y los microdatos viven en máquinas distintas: el
    código se edita donde se edita, y la ECP y la EPC solo pueden estar donde
    esté permitido tenerlas. Un preparador que empieza a trabajar y se cae
    quinientas líneas más tarde con `FileNotFoundError` hace creer que algo se
    rompió, cuando lo único que pasa es que este script no es para esta
    máquina. La comprobación va ANTES de leer nada, y el mensaje dice qué
    hacer en vez de qué faltó.
    """
    anios_ecp = [a for a in ANIOS_COMPARABLES if (DIR_ECP / str(a)).is_dir()]
    hay_epc_micro = True
    try:
        anios_epc()
    except EPCError:
        hay_epc_micro = False
    hay_epc_csv = SERIE_EPC_CSV.exists() and DEFF_EPC_CSV.exists()

    if anios_ecp and (hay_epc_micro or hay_epc_csv):
        return

    faltan = []
    if not anios_ecp:
        faltan.append(f"la ECP en {DIR_ECP.relative_to(RAIZ).as_posix()}/<año>")
    if not (hay_epc_micro or hay_epc_csv):
        faltan.append("la EPC (ni el empaquetado de Bogotá Cómo Vamos ni "
                      f"{SERIE_EPC_CSV.relative_to(RAIZ).as_posix()})")

    raise SinInsumos(
        "Esta máquina no tiene los microdatos, así que este script no es para ella.\n"
        f"  Falta: {'; '.join(faltan)}.\n\n"
        f"  NO hace falta correrlo: el paquete ya viene construido. Copia\n"
        f"  {SALIDA.relative_to(RAIZ).as_posix()} del entregable y sigue con:\n"
        f"      python src/viz/construir_pagina.py\n\n"
        "  Si esta SÍ es la máquina de los microdatos, revisa las rutas de\n"
        "  DATA_INVENTORY.md §10 o exporta BSS_EPC_DIR.")


def construir() -> dict:
    revisar_insumos()
    series = [serie_ecp(), serie_epc()]
    for s in series:
        s["tramos"] = tramos(s["puntos"])

    anios = sorted({p["anio"] for s in series for p in s["puntos"]})
    return {
        "version": "0.1",
        "escala": [1, 5],
        "rango_anios": [anios[0], anios[-1]] if anios else None,
        "advertencia": (
            "Estas son mediciones de encuesta, no salidas del simulador. Las dos series "
            "comparten la escala 1–5 pero miden conceptos distintos y no son comparables "
            "entre sí punto a punto."),
        "series": series,
    }


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")
    try:
        datos = construir()
    except SinInsumos as e:
        # Sin traza: no es un error del programa, es que falta el insumo, y una
        # traza de veinte líneas esconde la instrucción que sí sirve.
        print(f"\n{e}\n")
        return 1
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, separators=(",", ":")),
                      encoding="utf-8")
    print(f"\n{SALIDA}  {SALIDA.stat().st_size/1024:.1f} KB")
    for s in datos["series"]:
        anios = [p["anio"] for p in s["puntos"]]
        saltos = sum(1 for t in s["tramos"] if t["salto"])
        print(f"  {s['nombre']:34s} {len(anios)} puntos {anios[0]}–{anios[-1]}, "
              f"{saltos} salto(s), diseño real: {s['con_diseno']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
