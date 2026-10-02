"""
Nivel por preguntas parecidas, parte A sin API (`docs/NIVEL_PARECIDAS_SPECIFICATION.md`): ¿se
puede estimar el porcentaje favorable de una pregunta nueva con el resultado real de preguntas
parecidas? Solo práctica: lee el banco con `banco.practica()`; las guardadas no se tocan.

    R0 promedio · R1 mismo tema · R2 vecinos por texto (TF-IDF de caracteres, k = 5)
    Siempre dejando fuera la familia de la pregunta.

Uso:
    python src/experiments/nivel_parecidas.py

Escribe `data/processed/banco/nivel_parecidas.json` (solo cifras agregadas).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-NP1. **El TF-IDF se ajusta una vez con los textos de todas las preguntas de práctica** y no en
    cada exclusión. Solo usa los textos, no los resultados, así que no filtra el `total` de la
    pregunta que se predice.

DI-NP2. **Empates en la similitud:** se ordena por similitud y, a igual similitud, por `id`, para
    que el resultado no dependa del orden del archivo.
"""

from __future__ import annotations

import json
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

SALIDA_NOMBRE = "nivel_parecidas.json"
K = 5
MEJORA = 0.20


def _norma(t: str) -> str:
    t = unicodedata.normalize("NFKD", str(t).lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def similitudes(textos: list[str]) -> np.ndarray:
    """DI-NP1: matriz de similitud coseno entre todos los textos."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    x = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5)).fit_transform([_norma(t) for t in textos])
    return cosine_similarity(x)


def predecir(t: pd.DataFrame, sim: np.ndarray, k: int = K, fuera_familia: bool = True) -> pd.DataFrame:
    """Predicciones de R0, R1 y R2 para cada fila de `t` (columnas id, familia, tema, total)."""
    ids, fam, tema, tot = t.id.to_numpy(), t.familia.to_numpy(), t.tema.to_numpy(), t.total.to_numpy(float)
    out = []
    for i in range(len(t)):
        otras = (fam != fam[i]) if fuera_familia else (np.arange(len(t)) != i)
        r0 = float(tot[otras].mean())
        mt = otras & (tema == tema[i])
        r1 = float(tot[mt].mean()) if mt.any() else r0
        cand = np.flatnonzero(otras)
        orden = sorted(cand, key=lambda j: (-sim[i, j], ids[j]))[:k]             # DI-NP2
        out.append({"id": ids[i], "total": tot[i], "R0": r0, "R1": r1, "R2": float(tot[orden].mean()),
                    "vecinos": [str(ids[j]) for j in orden]})
    return pd.DataFrame(out)


def eam(p: pd.DataFrame, col: str) -> float:
    return float(np.mean(np.abs(p[col] - p.total)))


def lectura(e: dict) -> dict:
    """Pre-registro §6."""
    vara = min(e["R0"], e["R1"], e["R2"])
    gratis = [m for m in ("R1", "R2") if e[m] <= (1 - MEJORA) * e["R0"]]
    return {"vara_parte_B": vara, "metodo_vara": min(("R0", "R1", "R2"), key=lambda m: e[m]),
            "metodo_gratis_que_sirve": gratis}


def tabla() -> pd.DataFrame:
    from src.experiments import banco as ba
    from src.experiments import banco_reales as br
    reales = json.loads(br.SALIDA.read_text(encoding="utf-8"))
    p = ba.practica()                                                       # nunca el guardado
    p = p[p.id.map(lambda i: i in reales and not reales[i]["excluida"] and reales[i]["total"] is not None)].copy()
    p["total"] = p.id.map(lambda i: reales[i]["total"])
    return p.sort_values("id").reset_index(drop=True)


def main() -> int:
    from src.experiments import banco as ba
    t = tabla()
    sim = similitudes(t.pregunta_pagina.tolist())
    p = predecir(t, sim)
    e = {m: eam(p, m) for m in ("R0", "R1", "R2")}
    dentro10 = {m: float(np.mean(np.abs(p[m] - p.total) <= 10)) for m in ("R0", "R1", "R2")}
    sec = {f"R2_k{k}": eam(predecir(t, sim, k=k), "R2") for k in (3, 10)}
    sec["R2_sin_dejar_familia"] = eam(predecir(t, sim, fuera_familia=False), "R2")
    lec = lectura(e)
    pred = {"P1": 12 <= e["R0"] <= 20, "P2": e["R1"] < e["R0"], "P3": e["R2"] > (1 - MEJORA) * e["R0"],
            "P4": sec["R2_sin_dejar_familia"] < e["R2"]}
    print(f"{len(t)} preguntas, {t.familia.nunique()} familias")
    print("EAM (puntos): " + ", ".join(f"{m} {v:.1f}" for m, v in e.items())
          + "   | error ≤ 10: " + ", ".join(f"{m} {v:.0%}" for m, v in dentro10.items()))
    print("secundarias: " + ", ".join(f"{m} {v:.1f}" for m, v in sec.items()))
    print(f"vara de la parte B: {lec['vara_parte_B']:.1f} ({lec['metodo_vara']}); método gratis que sirve: "
          f"{lec['metodo_gratis_que_sirve'] or 'ninguno'}; predicciones: {pred}")
    salida = ba.SALIDA / SALIDA_NOMBRE
    salida.write_text(json.dumps({"n": len(t), "eam": e, "dentro_10": dentro10, "secundarias": sec, "lectura": lec,
                                  "predicciones": pred, "por_pregunta": p.to_dict("records")},
                                 ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
