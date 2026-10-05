"""
Techo de los grupos en el banco ampliado (`docs/TECHO_GRUPOS_LOTES_SPECIFICATION.md`): oráculo,
réplica por mitades y tono general del simulador en las preguntas de práctica de los lotes 2, 3 y 4.
Solo cálculo local, sin API. Los guardados no se tocan.

Uso:
    python src/experiments/techo_grupos_lotes.py

Escribe `data/processed/banco/techo_grupos_lotes.json` (solo cifras agregadas).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-TL1. **Las mismas funciones que el lote 1**, sin copiarlas: `techo_grupos.oraculo`, `replica` y
    `sortear_mitad`, y `practica_puente.tono_general`, `grupos_agentes`, `indices` y `aciertos`. Lo único
    nuevo es armar, para cada lote, los arreglos que `replica` espera, con las mismas lecturas de
    `banco_lote2` y `banco_lote3` que dieron sus resultados reales.

DI-TL2. **Partición por persona** (pre-registro §3): cada persona es su propio «conglomerado».
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import banco as ba                    # noqa: E402
from src.experiments import banco_reales as br             # noqa: E402
from src.experiments import techo_grupos as tg             # noqa: E402

SALIDA = ba.SALIDA / "techo_grupos_lotes.json"
SEMILLA = 20261008
PRINCIPAL = (2, 3)


def reales(lote: int) -> dict:
    r = json.loads((ba.SALIDA / f"reales_practica_lote{lote}.json").read_text(encoding="utf-8"))
    return {k: v for k, v in r.items() if not v["excluida"] and v["pares_claros"]}


def preguntas_replica(reales_lote: dict, sorteo: pd.DataFrame, x_de, w: pd.Series, grupos: dict) -> list[dict]:
    """Los arreglos de `techo_grupos.replica` para cada pregunta (DI-TL1)."""
    s = sorteo.set_index("id")
    w = pd.to_numeric(w, errors="coerce")
    out = []
    for qid, r in reales_lote.items():
        f = {"id": qid, **s.loc[qid].to_dict()}
        x = pd.to_numeric(x_de(f), errors="coerce")
        ok = (x.isin(br.validos(br.categorias(f["categorias"]))) & w.notna() & (w > 0)).to_numpy()
        q = {"id": qid, "fav": x.isin(json.loads(f["codigos_favorables"])).astype(float).to_numpy(), "ok": ok,
             "w": w.fillna(0).to_numpy(float), "etq": {d: list(r["grupos"][d]) for d in tg.DIMS}}
        for d in tg.DIMS:
            q[d] = grupos[d].to_numpy(object)
        out.append(q)
    return out


def base_lote(lote: int):
    """(x_de, w, grupos) con la lectura que dio los resultados reales de ese lote."""
    if lote == 2:
        from src.experiments import banco_lote2 as b2
        d = b2.cargar()
        adultos = pd.to_numeric(d[b2.COLUMNAS["edad"][0]], errors="coerce") >= 18
        d = d[adultos].reset_index(drop=True)
        col = {i: c for i, _, c, *_ in b2.PREGUNTAS}
        return (lambda f: d[col[f["id"]]]), d[b2.COLUMNAS["w"][0]], b2.grupos(d)
    from src.experiments import banco_lote3 as b3
    x_de, w, g, _ = b3.base_bienal() if lote == 3 else b3.base_barrios()
    return x_de, w, g


def tono_en_pares(motor, tono: np.ndarray, reales_lote: dict) -> tuple[int, int]:
    """(aciertos, pares) del tono general (DI-PP4, DI-PP5) en los pares claros reales."""
    from src.experiments import practica_puente as pp
    g = pp.grupos_agentes(motor.agentes, False)
    ac = pa = 0
    for r in reales_lote.values():
        pares = [tuple(p) for p in r["pares_claros"]]
        labs = {d: list(r["grupos"][d]) for d in tg.DIMS if d in r["grupos"]}
        ac += pp.aciertos(pp.indices(tono, motor.peso, g, labs), pares)
        pa += len(pares)
    return ac, pa


def lectura(techo: float) -> str:
    return tg.lectura(techo)


def main() -> int:
    from src.consulta import motor as mo
    from src.experiments import practica_puente as pp
    R = {n: reales(n) for n in (2, 3, 4)}
    principal = {k: v for n in PRINCIPAL for k, v in R[n].items()}
    print("preguntas / pares: " + ", ".join(f"lote {n} {len(R[n])} / {sum(len(v['pares_claros']) for v in R[n].values())}" for n in R))
    o1, o2 = tg.oraculo(principal, 1.0), tg.oraculo(principal, tg.DEFF)
    o4 = tg.oraculo(R[4], tg.DEFF) if R[4] else None
    print(f"oráculo lotes 2-3: D=1 {o1['techo']:.3f}, D={tg.DEFF} {o2['techo']:.3f}; τ² " +
          ", ".join(f"{k} {v:.2f}" for k, v in o2["tau2"].items()) + (f" | lote 4: {o4['techo']:.3f}" if o4 else ""))
    fuentes = {}
    for n in (2, 3, 4):
        sorteo = pd.read_csv(ba.SALIDA / f"sorteo_lote{n}.csv")
        x_de, w, g = base_lote(n)
        qs = preguntas_replica(R[n], sorteo, x_de, w, g)
        fuentes[(f"lote{n}", n)] = {"psu": np.arange(len(w)).astype(str), "preguntas": qs}       # DI-TL2
    rep = tg.medida_replica({k: v for k, v in fuentes.items() if k[1] in PRINCIPAL}, semilla=SEMILLA)
    rep4 = tg.medida_replica({k: v for k, v in fuentes.items() if k[1] == 4}, semilla=SEMILLA)
    print(f"réplica lotes 2-3: {rep['media']:.3f} (p5 {rep['p5']:.3f}, p95 {rep['p95']:.3f}) | lote 4: {rep4['media']:.3f}")
    llamar, modelo = mo.cliente(simulado=True)                                  # sin API: solo la población
    M = mo.Motor(llamar, modelo)
    tono = pp.tono_general(M)
    t23 = tono_en_pares(M, tono, principal)
    t_lote = {n: tono_en_pares(M, tono, R[n]) for n in (2, 3, 4)}
    tono_p = t23[0] / t23[1]
    print(f"tono general lotes 2-3: {tono_p:.3f} ({t23[0]}/{t23[1]}); por lote: " +
          ", ".join(f"{n} {a / p:.3f} ({a}/{p})" for n, (a, p) in t_lote.items()))
    pred = {"P1": o2["techo"] >= 0.90, "P2": rep["media"] >= 0.85, "P3": 0.55 <= tono_p <= 0.70,
            "P4": o2["techo"] - tono_p >= 0.20}
    out = {"oraculo_D1": o1, f"oraculo_D{tg.DEFF}": o2, "oraculo_lote4": o4, "replica": rep, "replica_lote4": rep4,
           "tono_lotes_2_3": {"aciertos": t23[0], "pares": t23[1], "tasa": tono_p},
           "tono_por_lote": {str(n): {"aciertos": a, "pares": p} for n, (a, p) in t_lote.items()},
           "lectura": lectura(o2["techo"]), "tono_generaliza_62": tono_p < 0.70, "predicciones": pred}
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"lectura: {out['lectura']}; predicciones: {pred}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
