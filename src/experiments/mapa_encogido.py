"""
Mapa por localidad apoyado en la ciudad (`docs/MAPA_ENCOGIDO_SPECIFICATION.md`): encogimiento de tipo Fay-Herriot de la
cifra de cada localidad hacia un ancla (S1: la ciudad; S2: la regresión sobre el estrato medio), con la población 2022-2024,
contra la EPC 2025 de cada localidad. Sin API.

Uso:
    python src/experiments/mapa_encogido.py

DECISIONES DE IMPLEMENTACIÓN
============================

DI-ME1. **El ruido de una localidad** es la varianza de las respuestas de sus donantes (escala 0-100) dividida por el número
    de donantes distintos con respuesta válida. Los agentes repiten donantes, así que se cuentan donantes, no agentes.
DI-ME2. **τ² por el método de momentos:** la varianza de las cifras de las localidades menos la media de sus ruidos, con
    mínimo 0. Si es 0, todas las localidades toman el ancla.
DI-ME3. **El estrato medio** de una localidad es el de sus agentes (estrato de la Multipropósito).
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import peso_anio_reciente as pa      # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "mapa_encogido"


def encoger(m: np.ndarray, v: np.ndarray, ancla: np.ndarray) -> np.ndarray:
    """DI-ME2: w·m + (1 − w)·ancla, con w = τ²/(τ² + v)."""
    tau2 = max(0.0, float(np.var(m)) - float(np.mean(v)))
    w = tau2 / (tau2 + v) if tau2 > 0 else np.zeros(len(m))
    return w * m + (1 - w) * ancla


def ancla_estrato(m: np.ndarray, estrato: np.ndarray) -> np.ndarray:
    """S2: lo que predice la regresión lineal de m sobre el estrato medio."""
    b, a = np.polyfit(estrato, m, 1)
    return a + b * estrato


def main() -> int:
    from scipy.stats import spearmanr
    from src.consulta import motor as mo
    from src.population import armonizar_epc as ae
    cat = {f["variable"]: f for f in json.loads((pa.POBLACION / "catalogo.json").read_text(encoding="utf-8"))["dentro"]}
    arm = pd.read_csv(ae.SALIDA / "items.csv")
    con_2025 = [v for v, a in zip(arm.variable, arm.anios.astype(str)) if "2025" in a.split()]
    inv = pd.read_csv(ae.INVENTARIO)
    inv = inv[(inv.estado == "ok") & (inv.anio == 2025)].set_index("variable").codigo
    don = pd.read_parquet(pa.POBLACION / "donantes.parquet")
    col = {c.upper(): c for c in don.columns}
    ag = pd.read_parquet(pa.POBLACION / "agentes.parquet")
    ag = ag[ag.donante_id.notna()].reset_index(drop=True)
    idx = ag.donante_id.astype(int).to_numpy()
    peso, loc, anio = ag.peso.to_numpy(float), ag.cod_loc.to_numpy(), don.anio.to_numpy()[idx]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        b25, o25 = ae.cargar_ola(2025)
    w25, l25 = b25.peso.to_numpy(float), b25.cod_loc.to_numpy()
    filas, ordenes = [], {"hoy": [], "S1": [], "S2": []}
    for v in con_2025:
        f = mo.vista(cat[v])
        esc = list(f["escala"])
        xd = pd.to_numeric(don[col[str(f["codigo"]).upper()]], errors="coerce").to_numpy(float)
        x = xd[idx]
        ciudad, por_loc = pa.medias(x, peso, loc, anio, esc, "A", sorted(cat[v]["anios"])[-1])
        x25 = pd.to_numeric(o25["datos"][o25["col"][str(inv[v]).upper()]], errors="coerce").to_numpy(float)
        ok25 = np.isin(x25, esc) & pd.Series(l25).between(1, 19).to_numpy()
        locs = sorted(l for l in por_loc if (ok25 & (l25 == l)).any())
        m = np.array([por_loc[l] for l in locs])
        vr, est = [], []
        for l in locs:
            dl = np.unique(idx[(loc == l) & np.isin(x, esc)])                       # DI-ME1
            vals = np.array([pa.a_100(xd[i], esc) for i in dl])
            vr.append(float(np.var(vals)) / len(vals))
            est.append(float(ag.estrato[loc == l].mean()))                          # DI-ME3
        vr, est = np.array(vr), np.array(est)
        s1 = encoger(m, vr, np.full(len(m), ciudad))
        s2 = encoger(m, vr, ancla_estrato(m, est))
        real = np.array([pa.a_100(np.sum(w25[ok25 & (l25 == l)] * x25[ok25 & (l25 == l)]) / np.sum(w25[ok25 & (l25 == l)]), esc)
                         for l in locs])
        for k, s in (("hoy", m), ("S1", s1), ("S2", s2)):
            ordenes[k].append(float(spearmanr(s, real)[0]))
        for i, l in enumerate(locs):
            filas.append({"variable": v, "cod_loc": int(l), "real": real[i], "hoy": m[i], "S1": s1[i], "S2": s2[i],
                          "ruido": vr[i]})
    t = pd.DataFrame(filas)
    res = {k: {"error_localidad": round(float((t[k] - t.real).abs().groupby(t.variable).mean().mean()), 2),
               "orden_medio": round(float(np.nanmean(ordenes[k])), 3)} for k in ("hoy", "S1", "S2")}
    regla = {k: {"R1": res[k]["error_localidad"] <= res["hoy"]["error_localidad"] - 0.5,
                 "R2": res[k]["orden_medio"] >= res["hoy"]["orden_medio"]} for k in ("S1", "S2")}
    ganan = [k for k in ("S1", "S2") if all(regla[k].values())]
    gana = min(ganan, key=lambda k: res[k]["error_localidad"]) if ganan else None
    baja = {k: res["hoy"]["error_localidad"] - res[k]["error_localidad"] for k in ("S1", "S2")}
    pred = {"PM1": 0.5 <= baja["S1"] <= 1.5, "PM2": baja["S2"] > baja["S1"],
            "PM3": all(res[k]["orden_medio"] >= res["hoy"]["orden_medio"] for k in ("S1", "S2"))}
    print(f"{len(con_2025)} preguntas, {t.cod_loc.nunique()} localidades, {len(t)} pares")
    for k, r in res.items():
        print(f"  {k}: error por localidad {r['error_localidad']} | orden medio {r['orden_medio']}")
    print(f"regla: {regla} | gana: {gana} | predicciones: {pred}")
    SALIDA.mkdir(parents=True, exist_ok=True)
    t.to_csv(SALIDA / "por_pregunta_y_localidad.csv", index=False, encoding="utf-8")
    (SALIDA / "resultado.json").write_text(json.dumps({"resultados": res, "regla": regla, "gana": gana, "predicciones": pred},
                                                      ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
