"""Mide el piso de ruido de la dispersión territorial, rehaciendo el pipeline.

POR QUÉ EXISTE
--------------
El mapa por año (Hito 2) invita a leer diferencias entre localidades. Para que
esa lectura sea honesta hace falta saber cuánta dispersión produce el propio
método cuando NO hay ningún fenómeno territorial. El proyecto venía estimando
eso analíticamente: `sd_ruido² = promedio(ee²)`, con el `ee` de cada localidad
calculado como `sd/√n · √DEFF` (DI-V4).

**Esa estimación se queda corta, y se puede demostrar.** El error estándar
analítico supone que las 1.000 opiniones son extracciones independientes. No lo
son: el hot-deck empareja por celda demográfica y, con el desempate ponderado
de DI-M1, **dos agentes de la misma celda pueden recibir el valor del mismo
donante**. Los agentes de una localidad comparten celdas más que dos agentes
cualesquiera, así que la opinión queda agrupada por localidad por construcción.
Ese agrupamiento no aparece en `ee` y sí infla `sd_entre`.

Consecuencia medida sobre la ECP 2021: la descomposición analítica atribuía
solo el 52 % de la dispersión a ruido y dejaba una «dispersión real» de 0,236.
Rehaciendo el pipeline con otras semillas —mismo año, mismos datos, mismo
método— `sd_entre` recorre 0,194 a 0,515. La corrida que estaba en el paquete
(0,341) cae en el percentil 87 de su propia variación por semilla: **está
dentro del ruido, no por encima**.

QUÉ HACE
--------
Rehace la población sintética con N semillas por año y reporta la distribución
de `sd_entre`. Ese es el piso correcto: conserva el vínculo
localidad→demografía→donante y conserva el agrupamiento del hot-deck; lo único
que cambia es el sorteo.

Una prueba de permutación NO sirve acá —se intentó— porque rompe las dos cosas
a la vez y produce p ≈ 0,0005 para un efecto que no existe.

    python src/viz/piso_territorial.py              # 20 semillas por año
    python src/viz/piso_territorial.py --semillas 5 # borrador rápido
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "data" / "processed" / "viz" / "piso_territorial.json"
TMP = RAIZ / "data" / "processed" / "_piso"

ANIOS = (2013, 2017, 2019, 2021, 2023)

#: La primera es la semilla del paquete publicado; las demás son el null.
SEMILLAS = (42, 101, 202, 303, 404, 505, 606, 707, 808, 909,
            111, 222, 333, 444, 555, 666, 777, 888, 121, 232)


def sd_entre_de(csv: Path) -> float:
    d = pd.read_csv(csv)
    return float(d.groupby("localidad")["opinion_t0"].mean().std(ddof=1))


def medir(anio: int, semillas) -> list[float]:
    TMP.mkdir(parents=True, exist_ok=True)
    vals = []
    for s in semillas:
        base = TMP / f"p_{anio}_{s}"
        subprocess.run(
            [sys.executable, str(RAIZ / "src/population/construir_poblacion.py"),
             "--donante", f"ecp:{anio}", "--n", "1000", "--seed", str(s),
             "--nombre-base", str(base)],
            capture_output=True, check=True, cwd=RAIZ)
        vals.append(sd_entre_de(base.with_suffix(".csv")))
        for ext in (".csv", "_metadata.json"):
            try:
                os.remove(str(base) + ext)
            except OSError:
                pass
    return vals


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--semillas", type=int, default=len(SEMILLAS),
                    help=f"cuántas semillas por año (máx {len(SEMILLAS)})")
    args = ap.parse_args(argv)
    semillas = SEMILLAS[:max(2, min(args.semillas, len(SEMILLAS)))]

    print(f"Rehaciendo la población con {len(semillas)} semillas por año. "
          f"Esto tarda ~{2.5 * len(semillas) * len(ANIOS):.0f} s.\n")
    print(f"{'año':>6} {'publicada':>10} {'mediana':>8} {'p95':>7} "
          f"{'rango':>15} {'percentil':>10}")

    salida = {"semillas": list(semillas), "n_agentes": 1000, "por_anio": {}}
    for anio in ANIOS:
        vals = np.array(medir(anio, semillas))
        pub = float(vals[0])                       # semilla 42
        pct = 100 * float((vals <= pub).mean())
        salida["por_anio"][str(anio)] = {
            "sd_entre_publicada": round(pub, 4),
            "piso_mediana": round(float(np.median(vals)), 4),
            "piso_p95": round(float(np.percentile(vals, 95)), 4),
            "piso_min": round(float(vals.min()), 4),
            "piso_max": round(float(vals.max()), 4),
            "percentil_publicada": round(pct, 1),
            # Lo único que el mapa necesita saber: ¿la corrida publicada se
            # sale del piso que produce el propio método?
            "sale_del_piso": bool(pub > float(np.percentile(vals, 95))),
        }
        print(f"{anio:>6} {pub:>10.3f} {np.median(vals):>8.3f} "
              f"{np.percentile(vals, 95):>7.3f} "
              f"{vals.min():.3f}–{vals.max():.3f}".rjust(6) + f" {pct:>9.0f}%")

    salida["conclusion"] = (
        "Ningún año supera el percentil 95 de su propio piso de ruido."
        if not any(v["sale_del_piso"] for v in salida["por_anio"].values())
        else "Hay al menos un año por encima de su piso; revisar antes de publicarlo.")

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{salida['conclusion']}")
    print(f"{SALIDA.relative_to(RAIZ).as_posix()}")
    try:
        TMP.rmdir()
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
