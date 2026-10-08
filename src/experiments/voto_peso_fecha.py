"""
Peso por fecha en la intención de voto simulada (`docs/VOTO_PESO_FECHA_SPECIFICATION.md`). Las preguntas que Luna
eligió en el nivel 3 se combinan con más peso para las encuestas cercanas en el tiempo, en vez de un promedio simple.
**Sin API:** las elecciones de Luna se recuperan de las cachés del nivel 3 y de la Registraduría; si falta alguna, se
detiene en vez de llamar.

**Material electoral (D21).** Los resultados de las encuestas del CNC quedan en `data/processed/banco/`, ignorados por
git; la salida impresa trae solo cifras de error y acierto.

Uso:
    python src/experiments/voto_peso_fecha.py --recuperar    # guarda las elecciones de Luna (solo ids), sin API
    python src/experiments/voto_peso_fecha.py                # la evaluación pre-registrada

DECISIONES DE IMPLEMENTACIÓN
============================

DI-PF1. **La fecha de cada encuesta** es la de `voto_registraduria.FECHAS` (DI-VR1). La distancia se mide en días
    entre la encuesta de la pregunta objetivo y la de cada elegida (en la Registraduría, hasta el día de la elección).
    Hecho: CC892901 y CC893201 llevan fechas supuestas por su contenido; CC873501, la de finales de 2021 (DI-BL13).
DI-PF2. **El peso** es w = exp(−(d − d_min)/τ), que da las mismas proporciones que exp(−d/τ) y no se desborda. τ = ∞ es
    el promedio simple de hoy; τ = 0 toma solo las elegidas más cercanas (y promedia si empatan).
DI-PF3. **Las elecciones de Luna se recuperan con el texto anterior a DI-BL19** (`sorteo_lote7.csv` en
    `TEXTO_DEL_NIVEL_3`), que es con el que se corrió el nivel 3: así las claves de la caché coinciden. El cliente que
    se pasa falla si se intenta llamar, de modo que nada se gasta. Se guardan solo las ids elegidas.
DI-PF4. **Si Luna no eligió nada** (fallo), la estimación queda como en el nivel 3, la media de las candidatas, para
    toda τ.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import banco as ba                         # noqa: E402
from src.experiments import banco_lote7 as b7                   # noqa: E402
from src.experiments import experimento9 as e9                  # noqa: E402
from src.experiments import nivel_acuerdo_validacion as nv      # noqa: E402
from src.experiments import voto_registraduria as vr            # noqa: E402
from src.experiments import voto_simulado as vs                 # noqa: E402

TAUS = [0, 15, 30, 60, 120, 240, 480, math.inf]                 # §2, en días
EMPATE = 0.05                                                    # §2: a menos de 0,05 puntos, la τ más grande
MEJORA_MIN = 0.3                                                 # §4, R2
PROB_MIN, PROB_VECES = 0.90, 5                                   # §4, R4
TEXTO_DEL_NIVEL_3 = "d106ff7~1"                                  # DI-PF3
ELEGIDAS = ba.SALIDA / "voto_peso_fecha_elegidas.json"
SALIDA = ba.SALIDA / "voto_peso_fecha.json"


class PesoFechaError(RuntimeError):
    """Algo no cuadra con el pre-registro."""


# ---------------------------------------------------------------- combinar
def fecha(i: str) -> pd.Timestamp:
    """DI-PF1: la fecha del estudio de una pregunta del lote 7."""
    return pd.Timestamp(vr.FECHAS[vs.estudio(i)])


def combinar(ids: list[str], tot: dict, t_obj: pd.Timestamp, tau: float) -> float:
    """DI-PF2: la media de las elegidas, con peso por cercanía en el tiempo."""
    x = np.array([tot[i] for i in ids], float)
    d = np.array([abs((fecha(i) - t_obj).days) for i in ids], float)
    if tau == math.inf:
        return float(x.mean())
    if tau == 0:
        return float(x[d == d.min()].mean())
    w = np.exp(-(d - d.min()) / tau)
    return float((w * x).sum() / w.sum())


def estimaciones(el: list[dict], objetivo: pd.DataFrame, cand: pd.DataFrame, tau: float) -> pd.DataFrame:
    """Una fila por pregunta objetivo, con S según τ (DI-PF4 si no hubo elegidas)."""
    tot = dict(zip(cand.id, cand.total))
    m0 = float(cand.total.mean())
    ids = {r["id"]: r["ids"] for r in el}
    filas = []
    for r in objetivo.to_dict("records"):
        e = ids[r["id"]]
        filas.append({"id": r["id"], "S": combinar(e, tot, fecha(r["id"]), tau) if e else m0})
    return pd.DataFrame(filas)


def elegir_tau(eam: dict) -> float:
    """§2: la τ de menor EAM en la práctica; a menos de EMPATE, la más grande."""
    mejor = min(eam.values())
    return max(t for t, v in eam.items() if v <= mejor + EMPATE)


def regla(m: dict, m_inf: dict, tau: float) -> dict:
    """§4."""
    c = {"R1": tau != math.inf,
         "R2": m["eam"] <= m_inf["eam"] - MEJORA_MIN,
         "R3": round(m["adelante"] * m["segundas"]) >= round(m_inf["adelante"] * m_inf["segundas"]),
         "R4": m["dice_probable"] < PROB_VECES or (m["acierta_probable"] or 0) >= PROB_MIN}
    return {**c, "cumple": all(c.values())}


# ---------------------------------------------------------------- recuperar (sin API)
def _no_llamar(*a, **k):
    raise PesoFechaError("intentó llamar a la API: la elección no está en la caché (DI-PF3)")


def recuperar() -> dict:
    """DI-PF3: las ids que eligió Luna en el nivel 3 y en la Registraduría, desde sus cachés."""
    viejo = subprocess.run(["git", "show", f"{TEXTO_DEL_NIVEL_3}:data/processed/banco/sorteo_lote7.csv"],
                           cwd=RAIZ, capture_output=True, check=True).stdout
    original = b7.SORTEO
    with tempfile.TemporaryDirectory() as tmp:
        b7.SORTEO = Path(tmp) / "sorteo_lote7.csv"
        b7.SORTEO.write_bytes(viejo)
        try:
            prac, guar = vs.practica(), vs.guardado()
            c = e9.Cache(vs.CACHE)
            out = {"practica": vs.estimar(prac, prac, _no_llamar, c, False)[["id", "ids"]].to_dict("records"),
                   "guardado": vs.estimar(guar, prac, _no_llamar, c, False)[["id", "ids"]].to_dict("records"),
                   "registraduria": {}}
            q, cr = vr.preguntas(), e9.Cache(vr.CACHE)
            for e, el in vr.ELECCIONES.items():
                cands = vr.candidatos(e, q, vr.reales(e))
                cand = q[q.fecha < el["fecha"]][vs.COLS].reset_index(drop=True)
                obj = pd.DataFrame([{"id": f"SIM_{e}_{i}", "familia": f"SIM_{e}_{i}", "ambito": "Bogotá",
                                     "fuente": "simulación", "pregunta_pagina": el["texto"].format(x=k.replace("|", " ").title()),
                                     "categorias": "1=Sí; 2=No; 9=NS/NR", "codigos_favorables": "[1]",
                                     "total": float("nan"), "anio": int(el["fecha"][:4]), "variable": ""}
                                    for i, k in enumerate(cands)])
                p = nv.elegir_todas(obj, cand, _no_llamar, cr, vr.TOPE_USD, modelo=vs.MODELO, orden="candidatas")
                out["registraduria"][e] = dict(zip(cands, p.ids))
        finally:
            b7.SORTEO = original
    return out


# ---------------------------------------------------------------- evaluar
def evaluar() -> dict:
    el = json.loads(ELEGIDAS.read_text(encoding="utf-8"))
    prac, guar = vs.practica(), vs.guardado()
    eam_p, pp = {}, {}
    for t in TAUS:
        pp[t] = estimaciones(el["practica"], prac, prac, t)
        x = prac.merge(pp[t], on="id")
        eam_p[t] = float((x.S - x.total).abs().mean())
    tau = elegir_tau(eam_p)
    out = {"eam_practica": {str(t): v for t, v in eam_p.items()}, "tau": tau}
    for nombre, t in (("tau", tau), ("inf", math.inf)):
        x = prac.merge(pp[t], on="id")
        h = float(np.quantile((x.S - x.total).abs(), 0.8))
        h2 = vs.h_dif(pp[t], prac)
        pg = estimaciones(el["guardado"], guar, prac, t)
        m = vs.medir(pg, guar, h, h2)
        g = guar.merge(pg, on="id")
        m["eam_2021_2022"] = float((g.S - g.total).abs()[g.anio < 2026].mean())
        m["eam_2026"] = float((g.S - g.total).abs()[g.anio == 2026].mean())
        out[nombre] = {"h": h, "h2": h2, **m}
    # control: con τ = ∞ debe salir lo mismo que el nivel 3
    n3 = json.loads(vs.SALIDA.read_text(encoding="utf-8"))["con_su_encuesta"]
    if abs(out["inf"]["eam"] - n3["simulacion"]["eam"]) > 1e-6 or abs(out["inf"]["h"] - n3["h"]) > 1e-6:
        raise PesoFechaError("con τ = ∞ no se reproduce el nivel 3")
    out["regla"] = regla(out["tau"], out["inf"], tau)
    # Registraduría (§5, se reporta)
    q = vr.preguntas()
    tot = dict(zip(q.id, q.total))
    out["registraduria"] = {}
    for e, ids in el["registraduria"].items():
        real = vr.reales(e)
        t_el = pd.Timestamp(vr.ELECCIONES[e]["fecha"])
        r = {k: float(real[k]) for k in ids}
        out["registraduria"][e] = {n: vr.medir({k: combinar(v, tot, t_el, t) for k, v in ids.items() if v}, r)
                                   for n, t in (("tau", tau), ("inf", math.inf))}
    s = out["registraduria"]
    out["predicciones"] = {
        "PF1": tau != math.inf and tau <= 120,
        "PF2": out["regla"]["cumple"],
        "PF3": (out["inf"]["eam_2026"] - out["tau"]["eam_2026"]) > (out["inf"]["eam_2021_2022"] - out["tau"]["eam_2021_2022"]),
        "PF4": "E3" in s and s["E3"]["tau"].get("eam", 99) < s["E3"]["inf"].get("eam", 99)}
    return out


def main() -> int:
    warnings.simplefilter("ignore")
    ap = argparse.ArgumentParser()
    ap.add_argument("--recuperar", action="store_true")
    a = ap.parse_args()
    if a.recuperar:
        r = recuperar()
        ELEGIDAS.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"recuperadas sin API: {len(r['practica'])} de práctica, {len(r['guardado'])} guardadas, "
              f"{sum(len(v) for v in r['registraduria'].values())} candidatos de la Registraduría")
        return 0
    out = evaluar()
    print("EAM en la práctica por τ:", {k: round(v, 2) for k, v in out["eam_practica"].items()}, "→ τ* =", out["tau"])
    for n in ("tau", "inf"):
        m = out[n]
        print(f"  {n:4}: h {m['h']:.1f} h2 {m['h2']:.1f} | EAM {m['eam']:.2f} (2021-22 {m['eam_2021_2022']:.2f}, "
              f"2026 {m['eam_2026']:.2f}) | cobertura {m['cobertura']:.0%} | adelante {m['adelante']:.2f} de "
              f"{m['segundas']} | probable {m['dice_probable']} (acierta {m['acierta_probable']})")
    for e, v in out["registraduria"].items():
        print(f"  Registraduría {e}: τ* {v['tau']} | ∞ {v['inf']}")
    print("regla:", out["regla"])
    print("predicciones:", out["predicciones"])
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
