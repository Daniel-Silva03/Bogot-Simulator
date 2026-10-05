"""
¿Estaría Bogotá de acuerdo? (`docs/NIVEL_ACUERDO_SPECIFICATION.md`): el porcentaje y el lado de la mayoría
en las preguntas de PRÁCTICA de acuerdo o de sí/no de los lotes 1 a 3, sin API. Los guardados no se tocan.

    M0 promedio · M1 vecinos por texto (k = 5) · M2 forma (F1 + tipo + Bogotá)
    Cada pregunta sin su familia; el pozo es solo este subconjunto.

Uso:
    python src/experiments/nivel_acuerdo.py

Escribe `data/processed/banco/nivel_acuerdo.json` (solo cifras agregadas).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-NA1. **Tipo de pregunta, por sus categorías:** «acuerdo» si alguna etiqueta dice «acuerdo»; «sí/no» si
    trae `1=Sí` y una opción «No». Lo demás no entra (pre-registro §2).

DI-NA2. **El rango de una pregunta** usa los errores del mismo método en las preguntas de **otras**
    familias (sus predicciones también sin su propia familia), así que nunca ve su propio resultado.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import banco as ba                    # noqa: E402

SALIDA = ba.SALIDA / "nivel_acuerdo.json"
LOTES = ((1, "sorteo.csv", "reales_practica.json"), (2, "sorteo_lote2.csv", "reales_practica_lote2.json"),
         (3, "sorteo_lote3.csv", "reales_practica_lote3.json"))
K = 5
CUANTIL = 0.8
METODOS = ("M0", "M1", "M2")


def tipo(categorias: str):
    """DI-NA1."""
    c = str(categorias)
    if re.search(r"acuerdo", c, re.I):
        return "acuerdo"
    if re.search(r"(^|; )1=s[ií]\b", c, re.I) and re.search(r"=no\b", c, re.I):
        return "sí/no"
    return None


def tabla() -> pd.DataFrame:
    filas = []
    for n, sor, rea in LOTES:
        s = pd.read_csv(ba.SALIDA / sor)
        s = s[s.conjunto == "practica"]                                     # nunca el guardado
        r = json.loads((ba.SALIDA / rea).read_text(encoding="utf-8"))
        for f in s.to_dict("records"):
            t = tipo(f["categorias"])
            if t and f["id"] in r and not r[f["id"]]["excluida"] and r[f["id"]]["total"] is not None:
                filas.append({**{k: f[k] for k in ("id", "familia", "ambito", "pregunta_pagina", "categorias",
                                                   "codigos_favorables")}, "lote": n, "tipo": t, "total": float(r[f["id"]]["total"])})
    return pd.DataFrame(filas).sort_values("id").reset_index(drop=True)


def predecir(t: pd.DataFrame) -> pd.DataFrame:
    """M0, M1 y M2, cada pregunta sin su familia."""
    from src.experiments import nivel_forma as nf
    from src.experiments import nivel_parecidas as npar
    y, fam, ids = t.total.to_numpy(float), t.familia.to_numpy(), t.id.to_numpy()
    sim = npar.similitudes(t.pregunta_pagina.tolist())
    f = nf.rasgos(t)
    x = np.column_stack([np.ones(len(t)), f.F1.to_numpy(float), (t.tipo == "acuerdo").to_numpy(float), f.F4.to_numpy(float)])
    m2 = nf.predecir(x, y, fam)
    out = []
    for i in range(len(t)):
        otras = fam != fam[i]
        vec = sorted(np.flatnonzero(otras), key=lambda j: (-sim[i, j], ids[j]))[:K]
        out.append({"id": ids[i], "familia": fam[i], "total": y[i], "M0": float(y[otras].mean()),
                    "M1": float(y[vec].mean()), "M2": float(m2[i]),
                    "referencia_si": bool(np.mean(y[otras] > 50) > 0.5)})
    return pd.DataFrame(out)


def rangos(p: pd.DataFrame, m: str, q: float = CUANTIL) -> np.ndarray:
    """DI-NA2: h de cada pregunta con los errores del método en las otras familias."""
    err = (p[m] - p.total).abs().to_numpy()
    fam = p.familia.to_numpy()
    return np.array([np.quantile(err[fam != fam[i]], q) for i in range(len(p))])


def llamada(pred: np.ndarray, h: np.ndarray) -> np.ndarray:
    return np.where(pred - h > 50, "sí", np.where(pred + h < 50, "no", "dividida"))


def medir(p: pd.DataFrame) -> dict:
    real_si = p.total.to_numpy() > 50
    ref = float(np.mean(p.referencia_si.to_numpy() == real_si))
    out = {"n": len(p), "familias": int(p.familia.nunique()), "real_si": int(real_si.sum()), "referencia_lado": ref,
           "metodos": {}}
    for m in METODOS:
        pred = p[m].to_numpy()
        d = llamada(pred, rangos(p, m))
        dec = d != "dividida"
        out["metodos"][m] = {
            "eam": float(np.mean(np.abs(pred - p.total))), "lado": float(np.mean((pred > 50) == real_si)),
            "decide": float(dec.mean()),
            "acierto_al_decidir": float(np.mean((d[dec] == "sí") == real_si[dec])) if dec.any() else None,
            "dice_si": int((d == "sí").sum()), "acierta_si": int(((d == "sí") & real_si).sum()),
            "dice_no": int((d == "no").sum()), "acierta_no": int(((d == "no") & ~real_si).sum())}
    return out


def regla(r: dict) -> dict:
    """Pre-registro §6."""
    e0 = r["metodos"]["M0"]["eam"]
    return {m: bool(v["lado"] >= r["referencia_lado"] + 0.10 and v["eam"] <= 0.8 * e0) for m, v in r["metodos"].items()}


def main() -> int:
    t = tabla()
    p = predecir(t)
    r = medir(p)
    sirve = regla(r)
    mejor = min(METODOS, key=lambda m: r["metodos"][m]["eam"])
    pred = {"P1": 0.60 <= r["referencia_lado"] <= 0.80, "P2": not any(sirve.values()), "P3": mejor == "M2",
            "P4": r["metodos"][mejor]["decide"] < 0.30}
    print(f"{r['n']} preguntas, {r['familias']} familias; mayoría real «sí» en {r['real_si']}; "
          f"referencia fija acierta el lado {r['referencia_lado']:.0%}")
    for m, v in r["metodos"].items():
        print(f"  {m}: EAM {v['eam']:.1f} | lado {v['lado']:.0%} | decide {v['decide']:.0%} "
              f"(acierta {v['acierto_al_decidir'] if v['acierto_al_decidir'] is None else round(v['acierto_al_decidir'], 2)}; "
              f"«sí» {v['acierta_si']}/{v['dice_si']}, «no» {v['acierta_no']}/{v['dice_no']}) | sirve: {sirve[m]}")
    print(f"predicciones: {pred}")
    SALIDA.write_text(json.dumps({**r, "sirve": sirve, "predicciones": pred, "por_pregunta": p.to_dict("records")},
                                 ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
