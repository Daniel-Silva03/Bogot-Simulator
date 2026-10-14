"""
Rango según el acuerdo de las preguntas de apoyo (`docs/RANGO_ACUERDO_SPECIFICATION.md`): el rango de la estimación por
tercios de la desviación estándar de las elegidas, aprendido fuera de muestra. Sin API.

Uso:
    python src/experiments/rango_acuerdo.py

DECISIONES DE IMPLEMENTACIÓN
============================

DI-RA1. **El acuerdo** es la desviación estándar poblacional (ddof = 0) de los resultados reales de las elegidas; con una
    sola elegida, NaN y el rango de hoy para una.
DI-RA2. **Los cortes de los tercios** son los cuantiles 1/3 y 2/3 de la desviación estándar en el entrenamiento de cada
    pliegue; una pregunta de prueba cae en el tercio que le toca por esos cortes.
DI-RA3. **Solo cifras agregadas** (D21).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

SALIDA = RAIZ / "data" / "processed" / "banco" / "rango_acuerdo.json"
GRUPOS = 5
CUANTIL = 0.8


def acuerdo(ids: list, total: dict) -> float:
    """DI-RA1."""
    v = [total[i] for i in ids if i in total]
    return float(np.std(v)) if len(v) >= 2 else float("nan")


def rangos_por_tercio(sd: np.ndarray, err: np.ndarray) -> tuple[list[float], list[float]]:
    """DI-RA2: (cortes, rango de cada tercio) aprendidos de un entrenamiento."""
    m = ~np.isnan(sd)
    cortes = [float(np.quantile(sd[m], 1 / 3)), float(np.quantile(sd[m], 2 / 3))]
    t = np.digitize(sd[m], cortes)
    return cortes, [float(np.quantile(err[m][t == k], CUANTIL)) for k in range(3)]


def rango(sd: float, cortes: list[float], hs: list[float], h_una: float) -> float:
    return h_una if np.isnan(sd) else hs[int(np.digitize([sd], cortes)[0])]


def evaluar(s: np.ndarray, y: np.ndarray, h: np.ndarray) -> dict:
    from src.experiments import nivel_acuerdo as na
    ll = na.llamada(s, h)
    dec = ll != "dividida"
    ok = ((ll == "sí") & (y > 50)) | ((ll == "no") & (y <= 50))
    return {"decide": int(dec.sum()), "acierta": int((ok & dec).sum()),
            "acierto_al_decidir": round(float((ok & dec).sum() / dec.sum()), 3) if dec.any() else None,
            "cobertura": round(float(np.mean(np.abs(s - y) <= h)), 3), "rango_medio": round(float(h.mean()), 1)}


def main() -> int:
    from sklearn.model_selection import GroupKFold
    from scipy.stats import spearmanr
    from src.consulta import motor as mo
    from src.experiments import nivel_acuerdo_catalogo as nc
    d = json.loads(nc.SALIDA.read_text(encoding="utf-8"))
    p = pd.DataFrame(d["E"]["por_pregunta"]).dropna(subset=["S"]).reset_index(drop=True)
    total = dict(zip(nc.candidatas()[1].id, nc.candidatas()[1].total))
    s, y, fam = p.S.to_numpy(float), p.total.to_numpy(float), p.familia.to_numpy()
    k = p.ids.map(len).to_numpy()
    sd = np.array([acuerdo(i, total) for i in p.ids])
    err = np.abs(s - y)
    h_hoy = np.array([mo.H_ESTIMACION_K[min(int(x), 3)] for x in k])
    h_nuevo = np.empty(len(s))
    for tr, te in GroupKFold(n_splits=GRUPOS).split(s, y, fam):
        cortes, hs = rangos_por_tercio(sd[tr], err[tr])
        h_nuevo[te] = [rango(sd[i], cortes, hs, mo.H_ESTIMACION_K[1]) for i in te]
    hoy, nuevo = evaluar(s, y, h_hoy), evaluar(s, y, h_nuevo)
    m = ~np.isnan(sd)
    rho = float(spearmanr(sd[m], err[m])[0])
    cortes_all, hs_all = rangos_por_tercio(sd, err)
    regla = {"R1": nuevo["decide"] >= hoy["decide"] + 5, "R2": (nuevo["acierto_al_decidir"] or 0) >= 0.90,
             "R3": nuevo["cobertura"] >= 0.75}
    regla["pasa"] = all(regla.values())
    pred = {"PA1": rho >= 0.2, "PA2": hs_all[0] < 18, "PA3": regla["pasa"]}
    print(f"{len(p)} estimaciones; con 2 o más elegidas: {int(m.sum())}")
    print(f"Spearman acuerdo-error: {rho:.2f}")
    print(f"con las 139: cortes {[round(c, 1) for c in cortes_all]}, rangos por tercio {[round(h, 1) for h in hs_all]}")
    for n, r in (("hoy (DI-CO33)", hoy), ("según el acuerdo (fuera de muestra)", nuevo)):
        print(f"{n}: decide {r['decide']}, acierta {r['acierta']} ({r['acierto_al_decidir']}), cobertura {r['cobertura']}, "
              f"rango medio ±{r['rango_medio']}")
    print(f"regla: {regla} | predicciones: {pred}")
    SALIDA.write_text(json.dumps({"spearman": rho, "cortes": cortes_all, "rangos": hs_all, "hoy": hoy, "nuevo": nuevo,
                                  "regla": regla, "predicciones": pred}, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
