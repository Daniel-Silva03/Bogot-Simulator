"""
src/utils/medir_deff_epc.py

Mide el efecto de diseño de la EPC y deja los dos archivos de los que depende la
serie cuando el microdato no está en disco (el PC del CNC):

    data/processed/deff_epc_seis_olas.csv   error con diseño por ola e ítem
    data/processed/serie_epc_bcv.csv        media, sd, n y proporciones por ola e ítem
    data/processed/transiciones_epc_con_diseno.csv   las transiciones entre olas, con z
    data/processed/validacion_proxy_conglomerado.csv el §4.bis: ¿sirve un proxy donde no hay manzana?

Uso (necesita el microdato de la EPC):
    python src/utils/medir_deff_epc.py

POR QUÉ EXISTE (29/09/2026)
---------------------------
Los dos CSV existían sin script y sin versionar: cada máquina tenía su copia, y
la del error con diseño no se podía reproducir (2018: 0,0407 en el CSV, 0,0423
con el diseño documentado). Al buscar por qué apareció DI-D7 en `diseno.py`: la
manzana se numera dentro de cada localidad y el conglomerado correcto es
localidad|manzana. Este script es ahora la única fuente de los dos archivos, que
se versionan, y **se niega a escribir** si la mediana medida no coincide con
`DEFF_MEDIDO_EPC`: la constante que usan la ECP y el mapa no puede volver a
separarse de la medición que la justifica.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.population.epc_bcv import ITEMS, cargar_bcv, serie_bcv   # noqa: E402
from src.utils.diseno import (                                     # noqa: E402
    CONGLOMERADO_POR_ANIO, DEFF_MEDIDO_EPC, media_disenio,
)

SALIDA_DEFF = RAIZ / "data" / "processed" / "deff_epc_seis_olas.csv"
SALIDA_SERIE = RAIZ / "data" / "processed" / "serie_epc_bcv.csv"
ITEMS_MEDIDOS = ("gestion_alcalde", "gestion_concejo")
TOLERANCIA_MEDIANA = 0.005


def medir() -> pd.DataFrame:
    filas = []
    for anio in sorted(CONGLOMERADO_POR_ANIO):
        d = cargar_bcv(anio).datos
        if "diseno_psu" not in d.columns:
            raise RuntimeError(f"EPC {anio}: debería traer manzana y localidad y no las trae.")
        for item in ITEMS_MEDIDOS:
            if item not in d.columns:
                continue
            ok = d[item].notna() & (d["peso"] > 0)
            y, w = d.loc[ok, item].astype(float), d.loc[ok, "peso"].astype(float)
            srs = media_disenio(y, w)
            dis = media_disenio(y, w, psu=d.loc[ok, "diseno_psu"], estrato=d.loc[ok, "diseno_estrato"])
            filas.append({"anio": anio, "item": item, "deff": round((dis.ee / srs.ee) ** 2, 3),
                          "ee": round(dis.ee, 4), "ee_srs": round(srs.ee, 4), "n": dis.n,
                          "n_psu": dis.n_psu, "n_estratos": dis.n_estratos,
                          "psu_solitarias": dis.psu_solitarias})
    return pd.DataFrame(filas)


def transiciones(t: pd.DataFrame, serie: pd.DataFrame) -> pd.DataFrame:
    """Las transiciones entre olas consecutivas, con el error con diseño donde lo hay.

    Donde la ola no trae manzana, el error SRS (sd/√n, el mismo de la serie) se
    infla por el DEFF prestado. 2022 va siempre prestado: su `BARRIO_ENC` es texto
    libre y está vacío para un tercio de la muestra, así que no es un conglomerado.
    """
    diseno = t.set_index(["item", "anio"]).ee
    filas = []
    for item, s in serie.groupby("item"):
        s = s.sort_values("anio").set_index("anio")
        def ee_de(a):
            if (item, a) in diseno.index:
                return float(diseno[(item, a)]), "diseño"
            return float(s.loc[a, "sd"] / np.sqrt(s.loc[a, "n_valida"])
                         * np.sqrt(DEFF_MEDIDO_EPC["mediana"])), "prest."
        anios = list(s.index)
        for a, b in zip(anios, anios[1:]):
            (ea, fa), (eb, fb) = ee_de(a), ee_de(b)
            delta = float(s.loc[b, "media"] - s.loc[a, "media"])
            ee = float(np.hypot(ea, eb))                                  # DI-D5
            filas.append({"item": item, "transicion": f"{a}->{b}", "delta": round(delta, 4),
                          "ee": round(ee, 4), "z": round(delta / ee, 2),
                          "significativa": bool(abs(delta / ee) > 1.96), "fuente": f"{fa}/{fb}"})
    return pd.DataFrame(filas)


def validar_proxy() -> pd.DataFrame:
    """§4.bis: ¿sirve localidad × estrato como conglomerado donde no hay manzana?

    Se valida en las seis olas que sí traen manzana, sobre los mismos casos y con el
    mismo estimador: el diseño real (DI-D7) contra el proxy (conglomerado =
    localidad|estrato socioeconómico, estrato = localidad). Para 2025, sin manzana,
    se reportan las dos hipótesis de BCV sin nada contra qué validarlas.
    """
    filas = []
    for anio in sorted(CONGLOMERADO_POR_ANIO):
        d = cargar_bcv(anio).datos
        ok = d.gestion_alcalde.notna() & (d.peso > 0) & d.estrato.notna()
        y, w, d = d.loc[ok, "gestion_alcalde"].astype(float), d.loc[ok, "peso"].astype(float), d[ok]
        srs = media_disenio(y, w).ee
        real = media_disenio(y, w, psu=d.diseno_psu, estrato=d.diseno_estrato)
        proxy_psu = d.localidad.astype(str) + "|" + d.estrato.astype(str)
        proxy = media_disenio(y, w, psu=proxy_psu, estrato=d.localidad)
        filas.append({"anio": anio, "hipotesis": "localidad|estrato",
                      "deff_manzana": round((real.ee / srs) ** 2, 3),
                      "deff_proxy": round((proxy.ee / srs) ** 2, 3),
                      "razon": round((proxy.ee / real.ee) ** 2, 3),
                      "psu_manzana": real.n_psu, "psu_proxy": proxy.n_psu})

    from src.population.epc_bcv import archivo_del_anio, _columna, ITEMS as IT, DEMOGRAFICAS
    crudo = pd.read_stata(archivo_del_anio(2025), convert_categoricals=False)
    d = cargar_bcv(2025).datos
    ok = (d.gestion_alcalde.notna() & (d.peso > 0)).to_numpy()
    y, w = d.gestion_alcalde[ok].astype(float), d.peso[ok].astype(float)
    srs = media_disenio(y, w).ee
    seg = _columna(crudo, "SEG_1")[ok].astype(str)
    for nombre, base in (("Zona|SEG_1", _columna(crudo, "Zona")[ok].astype(str)),
                         ("Localidad|SEG_1", d.localidad[ok].astype(str))):
        e = media_disenio(y, w, psu=base + "|" + seg, estrato=base)
        filas.append({"anio": 2025, "hipotesis": nombre, "deff_manzana": np.nan,
                      "deff_proxy": round((e.ee / srs) ** 2, 3), "razon": np.nan,
                      "psu_manzana": np.nan, "psu_proxy": e.n_psu})
    return pd.DataFrame(filas)


SALIDA_TRANS = RAIZ / "data" / "processed" / "transiciones_epc_con_diseno.csv"
SALIDA_PROXY = RAIZ / "data" / "processed" / "validacion_proxy_conglomerado.csv"


def main() -> int:
    t = medir()
    mediana = float(np.median(t.deff))
    print(t.to_string(index=False))
    print(f"\n{len(t)} mediciones · DEFF mediano {mediana:.3f} · rango {t.deff.min():.2f}–{t.deff.max():.2f}")
    if abs(mediana - DEFF_MEDIDO_EPC["mediana"]) > TOLERANCIA_MEDIANA or len(t) != DEFF_MEDIDO_EPC["mediciones"]:
        print(f"ERROR: DEFF_MEDIDO_EPC dice mediana {DEFF_MEDIDO_EPC['mediana']} sobre "
              f"{DEFF_MEDIDO_EPC['mediciones']} mediciones. Actualizar la constante (y su nota) "
              "antes de escribir: no se deja que se separen.")
        return 1
    t.to_csv(SALIDA_DEFF, index=False)
    serie = pd.concat([serie_bcv(i) for i in ITEMS_MEDIDOS], ignore_index=True)
    serie.to_csv(SALIDA_SERIE, index=False)
    tr = transiciones(t, serie)
    tr.to_csv(SALIDA_TRANS, index=False)
    px = validar_proxy()
    px.to_csv(SALIDA_PROXY, index=False)
    print("\n" + tr.to_string(index=False) + "\n\n" + px.to_string(index=False) + "\n")
    for ruta in (SALIDA_DEFF, SALIDA_SERIE, SALIDA_TRANS, SALIDA_PROXY):
        print(ruta.relative_to(RAIZ).as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
