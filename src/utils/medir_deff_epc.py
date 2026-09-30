"""
src/utils/medir_deff_epc.py

Mide el efecto de diseño de la EPC y deja los dos archivos de los que depende la
serie cuando el microdato no está en disco (el PC del CNC):

    data/processed/deff_epc_seis_olas.csv   error con diseño por ola e ítem
    data/processed/serie_epc_bcv.csv        media, sd, n y proporciones por ola e ítem

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
    for ruta in (SALIDA_DEFF, SALIDA_SERIE):
        print(ruta.relative_to(RAIZ).as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
