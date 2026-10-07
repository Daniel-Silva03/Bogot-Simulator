"""
Intención de voto simulada, nivel 3 de D21 (`docs/VOTO_SIMULADO_SPECIFICATION.md`), parte 1: las 215 guardadas del
lote 7, estimadas con el método de D19 (Luna elige preguntas de voto medidas; la estimación es su media real).

**Material electoral.** Nada de esto se muestra en la página antes de la revisión jurídica (D21). Los resultados de
las encuestas del CNC quedan en `data/processed/banco/`, ignorados por git; la salida impresa trae solo cifras de error.

Uso:
    python src/experiments/voto_simulado.py --reales     # resultados reales del guardado del lote 7 (sin API)
    python src/experiments/voto_simulado.py --simulado   # sin gasto
    python src/experiments/voto_simulado.py --prueba     # 1 llamada, mide el costo
    python src/experiments/voto_simulado.py              # la corrida (tope USD 1,50)

DECISIONES DE IMPLEMENTACIÓN
============================

DI-VS1. **«Sin su encuesta» se corre por estudio:** para las preguntas de cada estudio, las candidatas son las de
    práctica de los otros estudios. «Con su encuesta» usa todas las de práctica; el prompt ya quita la misma familia.
DI-VS2. **La opción de cada pregunta** es la etiqueta de su código favorable (`categorias`), normalizada (minúsculas,
    sin tildes, sin espacios dobles). El «último dato» busca en la práctica la misma opción y toma la del año más
    cercano. Si hay varias de ese año, su media. La probabilidad de votar es la opción «votaria».
DI-VS3. **Segundas vueltas:** las familias de tipo `segunda` del guardado con sus dos candidatos estimados. Va adelante el
    de mayor porcentaje. h₂ es el cuantil 80 % de |(S_A − S_B) − (T_A − T_B)| en las segundas vueltas de práctica.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import banco as ba                    # noqa: E402
from src.experiments import banco_lote7 as b7              # noqa: E402
from src.experiments import banco_reales as br             # noqa: E402
from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import nivel_acuerdo_luna as nlu     # noqa: E402
from src.experiments import nivel_acuerdo_validacion as nv  # noqa: E402
from src.experiments import nivel_parecidas_b as nb       # noqa: E402

MODELO = nlu.MODELO
TOPE_USD = 1.50
CACHE = ba.SALIDA / "cache_voto_simulado.json"
SALIDA = ba.SALIDA / "voto_simulado.json"
REALES_G7 = ba.SALIDA / "reales_guardado_lote7.json"
COLS = ["id", "familia", "ambito", "fuente", "pregunta_pagina", "categorias", "codigos_favorables", "total", "anio", "variable"]
EAM_MAX, LEADER_MIN, PROB_MIN, MEJORA = 6.0, 0.80, 0.90, 0.8


def reales_guardado() -> dict:
    s = pd.read_csv(b7.SORTEO)
    s = s[s.conjunto == "guardado"].assign(conjunto="practica")             # copia: el archivo no cambia
    return b7.reales(s)


def _tabla(conjunto: str, reales: dict) -> pd.DataFrame:
    s = pd.read_csv(b7.SORTEO)
    s = s[(s.conjunto == conjunto) & s.id.map(lambda i: i in reales and not reales[i]["excluida"])].copy()
    s = s.assign(total=s.id.map(lambda i: float(reales[i]["total"])))
    return s[COLS].reset_index(drop=True)


def practica() -> pd.DataFrame:
    return _tabla("practica", json.loads(b7.REALES.read_text(encoding="utf-8")))


def guardado() -> pd.DataFrame:
    return _tabla("guardado", json.loads(REALES_G7.read_text(encoding="utf-8")))


def estudio(i: str) -> str:
    return i[:8]


def tipo(fila) -> str:
    return b7.ESTUDIOS[estudio(fila["id"])][4][fila["variable"]]


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return " ".join(s.lower().split())


def opcion(fila) -> str:
    """DI-VS2."""
    if fila["id"].endswith("_votaria"):
        return "votaria"
    fav = json.loads(fila["codigos_favorables"])[0]
    return _norm(br.categorias(fila["categorias"]).get(fav, ""))


# ---------------------------------------------------------------- estimar
def estimar(objetivo: pd.DataFrame, cand: pd.DataFrame, llamar, cache, sin_su_encuesta: bool, solo=None) -> pd.DataFrame:
    """DI-VS1."""
    if not sin_su_encuesta:
        return nv.elegir_todas(objetivo, cand, llamar, cache, TOPE_USD, solo=solo, modelo=MODELO)
    partes = []
    for est in objetivo.id.map(estudio).unique():
        o = objetivo[objetivo.id.map(estudio) == est].reset_index(drop=True)
        c = cand[cand.id.map(estudio) != est].reset_index(drop=True)
        partes.append(nv.elegir_todas(o, c, llamar, cache, TOPE_USD, solo=solo, modelo=MODELO))
        if solo:
            break
    return pd.concat(partes, ignore_index=True)


# ---------------------------------------------------------------- referencias
def referencias(objetivo: pd.DataFrame, prac: pd.DataFrame, sin_su_encuesta: bool) -> pd.DataFrame:
    m0 = float(prac.total.mean())
    po = prac.assign(op=[opcion(r) for r in prac.to_dict("records")], est=prac.id.map(estudio))
    filas = []
    for r in objetivo.to_dict("records"):
        c = po[po.op == opcion(r)]
        if sin_su_encuesta:
            c = c[c.est != estudio(r["id"])]
        if len(c):
            d = (c.anio - r["anio"]).abs()
            ult = float(c[d == d.min()].total.mean())
        else:
            ult = m0
        filas.append({"id": r["id"], "M0": m0, "ultimo": ult})
    return pd.DataFrame(filas)


# ---------------------------------------------------------------- medidas
def pares_segunda(p: pd.DataFrame, tabla: pd.DataFrame, col: str = "S") -> pd.DataFrame:
    """DI-VS3: una fila por segunda vuelta con sus dos candidatos."""
    t = tabla.merge(p[["id", col]], on="id")
    t = t[[tipo(r) == "segunda" for r in t.to_dict("records")]]
    filas = []
    for fam, g in t.groupby("familia"):
        if len(g) == 2 and g[col].notna().all():
            a, b = g.iloc[0], g.iloc[1]
            filas.append({"familia": fam, "d_est": a[col] - b[col], "d_real": a.total - b.total})
    return pd.DataFrame(filas, columns=["familia", "d_est", "d_real"])


def h_dif(p_prac: pd.DataFrame, prac: pd.DataFrame) -> float:
    pr = pares_segunda(p_prac, prac)
    return float(np.quantile((pr.d_est - pr.d_real).abs(), 0.8)) if len(pr) else float("nan")


def medir(p: pd.DataFrame, tabla: pd.DataFrame, h: float, h2: float, col: str = "S") -> dict:
    t = tabla.merge(p[["id", col]], on="id")
    err = (t[col] - t.total).abs()
    pr = pares_segunda(p, tabla, col)
    adel = (np.sign(pr.d_est) == np.sign(pr.d_real)) if len(pr) else pd.Series(dtype=bool)
    prob = pr.d_est.abs() > h2 if len(pr) else pd.Series(dtype=bool)
    return {"n": int(len(t)), "eam": float(err.mean()), "cobertura": float((err <= h).mean()),
            "segundas": int(len(pr)), "adelante": float(adel.mean()) if len(pr) else None,
            "dice_probable": int(prob.sum()) if len(pr) else 0,
            "acierta_probable": float(adel[prob].mean()) if len(pr) and prob.any() else None}


def regla(m: dict, eam_m0: float, eam_ult: float) -> dict:
    """Pre-registro §3."""
    c = {"eam": m["eam"] <= EAM_MAX,
         "adelante": (m["adelante"] or 0) >= LEADER_MIN and
                     (m["dice_probable"] < 5 or (m["acierta_probable"] or 0) >= PROB_MIN),
         "mejora": m["eam"] <= MEJORA * min(eam_m0, eam_ult)}
    return {**c, "cumple": all(c.values())}


def evaluar(version: str, p_prac, p_guar, prac, guar) -> dict:
    pp = prac.merge(p_prac[["id", "S"]], on="id")
    h = float(np.quantile((pp.S - pp.total).abs(), 0.8))                      # §2: con la práctica
    h2 = h_dif(p_prac, prac)
    sin = version == "sin_su_encuesta"
    ref = referencias(guar, prac, sin)
    m = medir(p_guar, guar, h, h2)
    m_m0 = medir(ref.rename(columns={"M0": "S"}), guar, h, h2)
    m_ul = medir(ref.rename(columns={"ultimo": "S"}), guar, h, h2)
    return {"h": h, "h2": h2, "simulacion": m, "M0": m_m0, "ultimo": m_ul,
            "regla": regla(m, m_m0["eam"], m_ul["eam"]), "por_pregunta": p_guar.to_dict("records")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reales", action="store_true")
    ap.add_argument("--simulado", action="store_true")
    ap.add_argument("--prueba", action="store_true")
    a = ap.parse_args()
    if a.reales:
        r = reales_guardado()
        REALES_G7.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        exc = {k: v["excluida"] for k, v in r.items() if v["excluida"]}
        print(f"{len(r)} guardadas del lote 7; excluidas por estructura {len(exc)} {exc or ''}")
        return 0
    prac, guar = practica(), guardado()
    if a.simulado:
        cache, llamar = e9.Cache(Path(tempfile.gettempdir()) / "bss_voto_simulado.json"), nb.cliente_simulado(prac)
    else:
        cache, llamar = e9.Cache(CACHE), e9.cliente_real(timeout=300)
    if a.prueba:
        antes = nb.gastado(cache)
        estimar(guar, prac, llamar, cache, False, solo=1)
        c = nb.gastado(cache) - antes
        print(f"una llamada costó USD {c:.4f} → las ~746 costarían ~USD {746 * c:.2f} (tope USD {TOPE_USD})")
        return 0
    out = {}
    for version, sin in (("con_su_encuesta", False), ("sin_su_encuesta", True)):
        pp = estimar(prac, prac, llamar, cache, sin)
        pg = estimar(guar, prac, llamar, cache, sin)
        out[version] = evaluar(version, pp, pg, prac, guar)
        x = out[version]
        print(f"{version}: h {x['h']:.1f} h2 {x['h2']:.1f}")
        for k in ("simulacion", "M0", "ultimo"):
            m = x[k]
            print(f"  {k:10}: EAM {m['eam']:.1f} | cobertura {m['cobertura']:.0%} | segundas {m['segundas']}, adelante "
                  f"{m['adelante'] if m['adelante'] is None else round(m['adelante'], 2)} | probable {m['dice_probable']} "
                  f"(acierta {m['acierta_probable']})")
        print(f"  regla: {x['regla']}", flush=True)
    c, s = out["con_su_encuesta"], out["sin_su_encuesta"]
    pred = {"PV1": 4 <= c["simulacion"]["eam"] <= 8, "PV2": c["regla"]["cumple"],
            "PV3": s["simulacion"]["eam"] >= c["simulacion"]["eam"] + 3,
            "PV4": c["simulacion"]["adelante"] is not None and c["ultimo"]["adelante"] is not None
                   and c["simulacion"]["adelante"] - c["ultimo"]["adelante"] < 0.10}
    gasto = None if a.simulado else e9.gasto_registrado(cache)
    print(f"predicciones: {pred} | gasto: {gasto and round(gasto['costo_usd'], 4)}")
    if not a.simulado:
        SALIDA.write_text(json.dumps({**out, "predicciones": pred, "gasto": gasto}, ensure_ascii=False, indent=1,
                                     default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
