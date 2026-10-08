"""
Rango variable en la estimación de opinión (`docs/RANGO_VARIABLE_SPECIFICATION.md`). Hoy el rango es fijo, ±23,4
(D20). Aquí cada estimación lleva su propio rango, según cuántas preguntas eligió Luna o qué tanto coinciden entre sí.
La estimación (la media real de las elegidas) no cambia. **Sin API:** las elecciones de Luna se recuperan de las
cachés; si falta alguna, se detiene en vez de llamar.

Los resultados de las encuestas del CNC (lote 6) quedan en `data/processed/banco/`, ignorados por git (D21).

Uso:
    python src/experiments/rango_variable.py --recuperar    # guarda las elecciones de la práctica (solo ids), sin API
    python src/experiments/rango_variable.py                # la evaluación pre-registrada

DECISIONES DE IMPLEMENTACIÓN
============================

DI-RV1. **La práctica es la de Luna** (`nivel_acuerdo_luna`, 92 preguntas, candidatas las 109 de entonces), la misma
    con la que se fijó el ±23,4. **El guardado es el de la página:** las 129 con las 139 candidatas (`nivel_acuerdo_lote6`,
    configuración C). Hecho: las candidatas no son las mismas en los dos; se declara.
DI-RV2. **Las formas** (§2) se calibran para cubrir el 80 % en la práctica, como el rango fijo. La dispersión es la
    desviación estándar poblacional (ddof = 0) de los resultados reales de las elegidas; el recorrido, máximo menos
    mínimo. Con una sola elegida, las dos son 0 y vale el piso m.
DI-RV3. **«Probablemente sí»** si S − h > 50; **«probablemente no»** si S + h < 50; si no, «dividida». Es la regla de
    `nivel_acuerdo.llamada`, con h por pregunta.
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import banco as ba                         # noqa: E402
from src.experiments import experimento9 as e9                  # noqa: E402
from src.experiments import nivel_acuerdo as na                 # noqa: E402
from src.experiments import nivel_acuerdo_lote6 as n6           # noqa: E402
from src.experiments import nivel_acuerdo_luna as nlu           # noqa: E402
from src.experiments import nivel_parecidas_b as nb             # noqa: E402

FORMAS = ("F0", "F1", "F2", "F3")
CUANTIL = 0.80
EMPATE = 0.5                                                     # §2: a menos de 0,5 puntos de ancho medio, la más simple
MIN_GRUPO = 10                                                   # F1: un grupo con menos usa el h fijo
COBERTURA_MIN, ACIERTO_MIN = 0.75, 0.90                          # §4
ELEGIDAS = ba.SALIDA / "rango_variable_practica.json"
SALIDA = ba.SALIDA / "rango_variable.json"


class RangoError(RuntimeError):
    """Algo no cuadra con el pre-registro."""


# ---------------------------------------------------------------- rasgos de cada estimación
def rasgos(ids: list[str], tot: dict) -> dict:
    x = np.array([tot[i] for i in ids], float)
    return {"k": len(x), "sd": float(x.std()) if len(x) else 0.0, "rango": float(x.max() - x.min()) if len(x) else 0.0}


def grupo_k(k: int) -> str:
    return "1" if k <= 1 else ("2" if k == 2 else "3+")


# ---------------------------------------------------------------- calibrar en la práctica
def calibrar(forma: str, r: pd.DataFrame) -> dict:
    """§2. `r`: una fila por pregunta de práctica, con k, sd, rango y err = |S − T|."""
    h0 = float(np.quantile(r.err, CUANTIL))
    if forma == "F0":
        if round(h0, 1) != n6.H:
            raise RangoError("la práctica no reproduce el ±23,4 de la página")
        return {"h": n6.H}                                                    # la página usa el valor redondeado
    if forma == "F1":
        g = r.k.map(grupo_k)
        return {"h0": h0, "por_grupo": {x: (float(np.quantile(r.err[g == x], CUANTIL)) if (g == x).sum() >= MIN_GRUPO else h0)
                                        for x in ("1", "2", "3+")}}
    col = {"F2": "sd", "F3": "rango"}[forma]
    m = float(r[col][r.k >= 2].median())
    sig = r[col].clip(lower=m) if forma == "F2" else r[col] + m
    return {"m": m, "c": float(np.quantile(r.err / sig, CUANTIL))}


def ancho(forma: str, cal: dict, x: dict) -> float:
    """El h de una estimación con rasgos `x`."""
    if forma == "F0":
        return cal["h"]
    if forma == "F1":
        return cal["por_grupo"][grupo_k(x["k"])]
    sig = max(x["sd"], cal["m"]) if forma == "F2" else x["rango"] + cal["m"]
    return cal["c"] * sig


def elegir_forma(anchos: dict) -> str:
    """§2: la de menor ancho medio en la práctica; a menos de EMPATE de la mejor, la más simple (orden de FORMAS)."""
    mejor = min(anchos.values())
    return next(f for f in FORMAS if anchos[f] <= mejor + EMPATE)


# ---------------------------------------------------------------- medir
def llamada(s: float, h: float) -> str:
    """DI-RV3."""
    return "sí" if s - h > 50 else ("no" if s + h < 50 else "dividida")


def medir(t: pd.DataFrame) -> dict:
    """`t`: S, total, h por pregunta."""
    d = np.array([llamada(s, h) for s, h in zip(t.S, t.h)])
    real_si = t.total.to_numpy() > 50
    dec = d != "dividida"
    return {"n": int(len(t)), "ancho_medio": float(t.h.mean()),
            "cobertura": float(((t.S - t.total).abs() <= t.h).mean()),
            "decide": int(dec.sum()),
            "acierta_al_decidir": int(((d == "sí") == real_si)[dec].sum()),
            "acierto_al_decidir": float(((d == "sí") == real_si)[dec].mean()) if dec.any() else None}


def regla(m: dict, m0: dict, forma: str) -> dict:
    """§4."""
    c = {"R1": forma != "F0", "R2": m["cobertura"] >= COBERTURA_MIN, "R3": m["decide"] > m0["decide"],
         "R4": (m["acierto_al_decidir"] or 0) >= ACIERTO_MIN}
    return {**c, "cumple": all(c.values())}


# ---------------------------------------------------------------- recuperar (sin API)
def _no_llamar(*a, **k):
    raise RangoError("intentó llamar a la API: la elección no está en la caché")


def recuperar() -> list[dict]:
    t = na.tabla()
    p = nb.correr(t, _no_llamar, e9.Cache(nlu.CACHE), nlu.MODELO)
    guardada = {r["id"]: r["S"] for r in json.loads(nlu.SALIDA.read_text(encoding="utf-8"))["practica"]["por_pregunta"]}
    if not all(abs(r.pred - guardada[r.id]) < 1e-9 for r in p.itertuples()):
        raise RangoError("la práctica recuperada no coincide con la salida de nivel_acuerdo_luna")
    return p[["id", "ids"]].to_dict("records")


# ---------------------------------------------------------------- evaluar
def tabla_practica() -> pd.DataFrame:
    t = na.tabla()
    tot = dict(zip(t.id, t.total))
    el = {r["id"]: r["ids"] for r in json.loads(ELEGIDAS.read_text(encoding="utf-8"))}
    s = {r["id"]: r["S"] for r in json.loads(nlu.SALIDA.read_text(encoding="utf-8"))["practica"]["por_pregunta"]}
    filas = [{"id": i, "S": s[i], "total": float(tot[i]), **rasgos(el[i], tot)} for i in t.id]
    r = pd.DataFrame(filas)
    return r.assign(err=(r.S - r.total).abs())


def tabla_guardado() -> pd.DataFrame:
    _, cand = n6.candidatas()
    tot = dict(zip(cand.id, cand.total))
    g = json.loads(n6.SALIDA.read_text(encoding="utf-8"))["C"]["por_pregunta"]
    r = pd.DataFrame([{"id": x["id"], "S": x["S"], "total": x["total"], **rasgos(x["ids"], tot)} for x in g])
    return r.assign(err=(r.S - r.total).abs())


def evaluar() -> dict:
    pr, gu = tabla_practica(), tabla_guardado()
    cal = {f: calibrar(f, pr) for f in FORMAS}
    anchos_p = {f: float(np.mean([ancho(f, cal[f], x) for x in pr.to_dict("records")])) for f in FORMAS}
    forma = elegir_forma(anchos_p)
    out = {"calibracion": cal, "ancho_practica": anchos_p, "forma_elegida": forma,
           "practica_spearman_sd_error": float(pr[pr.k >= 2][["sd", "err"]].corr(method="spearman").iloc[0, 1])}
    for f in FORMAS:
        h = [ancho(f, cal[f], x) for x in gu.to_dict("records")]
        out[f] = medir(gu.assign(h=h))
    c = json.loads(n6.SALIDA.read_text(encoding="utf-8"))["C"]                 # control: F0 es la página de hoy
    if out["F0"]["decide"] != round(c["decide"] * c["n"]) or abs((out["F0"]["acierto_al_decidir"] or 0) - c["acierto_al_decidir"]) > 1e-9:
        raise RangoError("F0 no reproduce las decisiones del lote 6")
    out["regla"] = regla(out[forma], out["F0"], forma)
    out["predicciones"] = {"PA1": forma in ("F2", "F3"), "PA2": out["regla"]["cumple"], "PA3": out[forma]["decide"] >= 20,
                           "PA4": out["practica_spearman_sd_error"] > 0}
    return out


def main() -> int:
    warnings.simplefilter("ignore")
    ap = argparse.ArgumentParser()
    ap.add_argument("--recuperar", action="store_true")
    a = ap.parse_args()
    if a.recuperar:
        r = recuperar()
        ELEGIDAS.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"recuperadas sin API: {len(r)} de práctica")
        return 0
    out = evaluar()
    print("ancho medio en la práctica:", {k: round(v, 1) for k, v in out["ancho_practica"].items()}, "→", out["forma_elegida"])
    print("calibración:", json.dumps(out["calibracion"], default=lambda x: round(x, 2)))
    print(f"práctica, Spearman dispersión–error (k ≥ 2): {out['practica_spearman_sd_error']:.2f}")
    for f in FORMAS:
        m = out[f]
        print(f"  {f}: ancho medio {m['ancho_medio']:.1f} | cobertura {m['cobertura']:.0%} | decide {m['decide']} de {m['n']}"
              f" | acierta {m['acierta_al_decidir']} ({m['acierto_al_decidir']})")
    print("regla:", out["regla"])
    print("predicciones:", out["predicciones"])
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
