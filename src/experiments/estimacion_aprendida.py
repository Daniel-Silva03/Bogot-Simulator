"""
Estimación aprendida (`docs/ESTIMACION_APRENDIDA_SPECIFICATION.md`): un modelo estadístico entrenado con las 238 preguntas
del banco que tienen resultado real, sobre embeddings del texto, contra la configuración E de la página (Luna elige 5).

Uso:
    python src/experiments/estimacion_aprendida.py --simulado   # embeddings al azar, sin gasto: prueba el circuito
    python src/experiments/estimacion_aprendida.py              # con los embeddings reales (tope USD 0,05)

DECISIONES DE IMPLEMENTACIÓN
============================

DI-EA1. **Embeddings por OpenRouter** (`/embeddings`, compatible con OpenAI), en lotes de 64 textos y con caché por texto
    (`cache_embeddings.json`, no se sube). Al servicio va solo el texto de la pregunta y sus categorías (D21).
DI-EA2. **El rango es el cuantil 80 % del error absoluto en la validación cruzada** del entrenamiento (5 grupos por familia,
    `GroupKFold`), con los parámetros elegidos. Es el mismo criterio del ±23,4 de Luna.
DI-EA3. **La evaluación es `nivel_acuerdo_validacion.evaluar`,** la misma de E, con el rango de cada modelo.
DI-EA4. **Nada del CNC se imprime:** de los objetivos y del entrenamiento solo salen cifras de error y acierto (D21).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import banco as ba                    # noqa: E402

MODELO_EMB = "intfloat/multilingual-e5-large"
CACHE = ba.SALIDA / "cache_embeddings.json"
SALIDA = ba.SALIDA / "estimacion_aprendida.json"
ALFAS = (1, 10, 100, 1000)
KS = (5, 10, 20)
GRUPOS_CV = 5
CUANTIL = 0.8
TOPE_USD = 0.05


def texto_emb(pregunta: str, categorias: str, favorables: str) -> str:
    """§2: el texto que se convierte en vector."""
    from src.experiments import nivel_parecidas_b as nb
    return f"query: {pregunta} | {nb.forma(categorias, favorables)}"


def _clave(t: str) -> str:
    return hashlib.sha256((MODELO_EMB + "\n" + t).encode("utf-8")).hexdigest()


def embeddings(textos: list[str], simulado: bool = False) -> np.ndarray:
    """DI-EA1: una fila normalizada por texto."""
    if simulado:
        rng = np.random.default_rng(0)
        x = np.array([np.random.default_rng(int(_clave(t)[:8], 16)).normal(size=64) for t in textos])
        return x / np.linalg.norm(x, axis=1, keepdims=True)
    cache = json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    faltan = [t for t in dict.fromkeys(textos) if _clave(t) not in cache]
    clave = (os.environ.get("OPENROUTER_API_KEY") or "").strip()
    if faltan and not clave:
        raise RuntimeError("Falta OPENROUTER_API_KEY.")
    for i in range(0, len(faltan), 64):
        lote = faltan[i:i + 64]
        req = urllib.request.Request("https://openrouter.ai/api/v1/embeddings",
                                     data=json.dumps({"model": MODELO_EMB, "input": lote}).encode("utf-8"),
                                     headers={"Authorization": f"Bearer {clave}", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.loads(r.read().decode("utf-8"))
        for t, e in zip(lote, sorted(d["data"], key=lambda x: x["index"])):
            cache[_clave(t)] = e["embedding"]
        CACHE.write_text(json.dumps(cache), encoding="utf-8")
        print(f"   embeddings: {min(i + 64, len(faltan))} de {len(faltan)}; uso {d.get('usage')}", flush=True)
    x = np.array([cache[_clave(t)] for t in textos], dtype=float)
    return x / np.linalg.norm(x, axis=1, keepdims=True)


def ridge(xe: np.ndarray, y: np.ndarray, xp: np.ndarray, alfa: float) -> np.ndarray:
    from sklearn.linear_model import Ridge
    return np.clip(Ridge(alpha=alfa).fit(xe, y).predict(xp), 0, 100)


def vecinos(xe: np.ndarray, y: np.ndarray, xp: np.ndarray, k: int) -> np.ndarray:
    s = xp @ xe.T
    idx = np.argsort(-s, axis=1)[:, :k]
    return y[idx].mean(axis=1)


def cv(x: np.ndarray, y: np.ndarray, fam: np.ndarray, f, param) -> np.ndarray:
    """DI-EA2: predicciones fuera de muestra en el entrenamiento, por grupos de familia."""
    from sklearn.model_selection import GroupKFold
    pred = np.empty(len(y))
    for tr, te in GroupKFold(n_splits=GRUPOS_CV).split(x, y, fam):
        pred[te] = f(x[tr], y[tr], x[te], param)
    return pred


def elegir(x, y, fam) -> dict:
    """§3: los parámetros por validación cruzada, y el rango de cada modelo."""
    out = {}
    for nombre, f, grilla in (("M1", ridge, ALFAS), ("M2", vecinos, KS)):
        errs = {p: np.abs(cv(x, y, fam, f, p) - y) for p in grilla}
        mejor = min(grilla, key=lambda p: (errs[p].mean(), p))
        out[nombre] = {"param": mejor, "eam_cv": round(float(errs[mejor].mean()), 2),
                       "h": round(float(np.quantile(errs[mejor], CUANTIL)), 2),
                       "eam_cv_por_param": {str(p): round(float(e.mean()), 2) for p, e in errs.items()}}
    return out


ACUERDO = ("1=De acuerdo; 2=En desacuerdo", "[1]")                    # §2: la escala de la prueba secundaria


def secundaria(xe: np.ndarray, y: np.ndarray, par: dict, simulado: bool) -> dict | None:
    """§2: las 13 de 2026, solo errores medios (D21). V5 aparte. None si faltan sus resultados en esta máquina."""
    from src.experiments import validacion_2026 as v26
    from src.experiments import validacion_cnc_2026 as vk
    rv = v26.SALIDA / "resultado.json"
    rk = vk.SALIDA / "resultado.json"
    if not (rv.exists() and rk.exists()):
        return None
    grupos = {"V_sin_V5": [f for f in json.loads(rv.read_text(encoding="utf-8"))["preguntas"][:6] if f["id"] != "V5"],
              "V5": [f for f in json.loads(rv.read_text(encoding="utf-8"))["preguntas"] if f["id"] == "V5"],
              "K": json.loads(rk.read_text(encoding="utf-8"))["preguntas"]}
    out = {}
    for g, filas in grupos.items():
        x = embeddings([texto_emb(f["pregunta"], *ACUERDO) for f in filas], simulado)
        real = np.array([f["real"] for f in filas], float)
        pag = np.array([f.get("porcentaje", 50.0) for f in filas], float)
        s1, s2 = ridge(xe, y, x, par["M1"]["param"]), vecinos(xe, y, x, par["M2"]["param"])
        out[g] = {k: round(float(np.abs(s - real).mean()), 1)
                  for k, s in (("pagina", pag), ("M1", s1), ("M2", s2), ("M3", (s1 + pag) / 2))}
    return out


def regla(r_e: dict, r: dict) -> dict:
    """Pre-registro §4."""
    c = {"eam": r["eam"] <= r_e["eam"] - 1.0, "lado": r["lado"] >= 0.70,
         "al_decidir": (r["acierto_al_decidir"] or 0) >= 0.90 if r["decide"] > 0 else False, "validacion": r["pasa"]}
    return {**c, "reemplaza": all(c.values())}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args(argv)
    from src.experiments import banco_lote8 as b8
    from src.experiments import nivel_acuerdo_catalogo as nc
    from src.experiments import nivel_acuerdo_lote6 as n6
    from src.experiments import nivel_acuerdo_lote8 as n8
    from src.experiments import nivel_acuerdo_validacion as nv
    cand_e = nc.candidatas()[1]
    p8 = n8._lote8("practica", json.loads(b8.REALES.read_text(encoding="utf-8")))
    ent = pd.concat([cand_e[n8.COLS], p8], ignore_index=True)
    o129, o8 = n8.objetivos()
    obj = pd.concat([o129, o8], ignore_index=True)
    if set(ent.familia) & set(obj.familia):
        raise RuntimeError("Un objetivo comparte familia con el entrenamiento.")
    te = [texto_emb(r.pregunta_pagina, r.categorias, r.codigos_favorables) for r in ent.itertuples()]
    to = [texto_emb(r.pregunta_pagina, r.categorias, r.codigos_favorables) for r in obj.itertuples()]
    x = embeddings(te + to, a.simulado)
    xe, xo = x[:len(ent)], x[len(ent):]
    y, fam = ent.total.to_numpy(float), ent.familia.to_numpy()
    par = elegir(xe, y, fam)
    pe = pd.DataFrame(json.loads(nc.SALIDA.read_text(encoding="utf-8"))["E"]["por_pregunta"]).set_index("id").loc[obj.id]
    s1 = ridge(xe, y, xo, par["M1"]["param"])
    s2 = vecinos(xe, y, xo, par["M2"]["param"])
    preds = {"M1": (s1, par["M1"]["h"]), "M2": (s2, par["M2"]["h"]),
             "M3": ((s1 + pe.S.to_numpy(float)) / 2, par["M1"]["h"])}
    base = obj[["id", "familia", "total"]].reset_index(drop=True)
    r_e = nv.evaluar(base.assign(S=pe.S.to_numpy(float), fallo=False), cand_e, obj, h=n8.H)
    res = {"E": n6._cifras(r_e)}
    for k, (s, h) in preds.items():
        r = nv.evaluar(base.assign(S=s, fallo=False), ent, obj, h=h)
        res[k] = {**n6._cifras(r), "h": h, "regla": regla(r_e, r)}
    ganan = [k for k in preds if res[k]["regla"]["reemplaza"]]
    gana = min(ganan, key=lambda k: res[k]["eam"]) if ganan else None
    pred = {"P1": gana is None, "P2": min(preds, key=lambda k: res[k]["eam"]) == "M3",
            "P3": 14.3 <= res["M1"]["eam"] <= 16.3}
    print(f"entrenamiento {len(ent)} | objetivos {len(obj)} | parámetros {json.dumps(par, ensure_ascii=False)}")
    for k in ("E", "M1", "M2", "M3"):
        r = res[k]
        print(f"{k}: EAM {r['eam']:.1f} | lado {r['lado']:.0%} (ref {r['referencia_lado']:.0%}) | decide {r['decide']:.0%} "
              f"(«sí» {r['acierta_si']}/{r['dice_si']}, «no» {r['acierta_no']}/{r['dice_no']}) | pasa {r['pasa']}"
              + (f" | h {r['h']} | regla {r['regla']}" if k != "E" else ""))
    sec = secundaria(xe, y, par, a.simulado)
    pred["P4"] = all(sec["V_sin_V5"][k] >= sec["V_sin_V5"]["pagina"] for k in ("M1", "M2", "M3")) if sec else None
    print(f"secundaria (EAM): {sec}")
    print(f"gana: {gana} | predicciones: {pred}")
    if not a.simulado:
        SALIDA.write_text(json.dumps({"parametros": par, "resultados": res, "gana": gana, "predicciones": pred, "secundaria": sec},
                                     ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
