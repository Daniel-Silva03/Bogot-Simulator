"""
Intención de voto simulada por grupos (`docs/VOTO_GRUPOS_SPECIFICATION.md`): sexo, estrato y edad en Bogotá. Con las
mismas preguntas que eligió Luna en el nivel 3, la estimación de un grupo es la media del resultado real de ese grupo en
las elegidas. **Sin API:** usa las elecciones ya recuperadas (`voto_peso_fecha --recuperar`).

**Material electoral (D21).** Los resultados de las encuestas del CNC quedan en `data/processed/banco/`, ignorados por
git; la salida impresa trae solo cifras de error y acierto.

Uso:
    python src/experiments/voto_grupos.py

DECISIONES DE IMPLEMENTACIÓN
============================

DI-VG1. **Grupos gruesos**, para que las bases alcancen. Hecho: en el lote 7, estrato 1 y 5-6 tienen una base mediana de
    unas 33 personas, y estrato 4 llega a 3; los cortes de edad de 2021-2022 (18-25, 26-40, 41-55, 56+) y de 2026
    (18-24, 25-34, 35-44, 45-54, 55+) no coinciden. Decisión:
    - **estrato:** 1-2, 3 y 4-6;
    - **edad:** joven (18-25 o 18-24), media (26-55 o 25-54) y mayor (56+ o 55+). Supuesto: un año de diferencia en
      los bordes no cambia la lectura.
    Un grupo grueso es la media de sus partes ponderada por su base.
DI-VG2. **Un grupo real cuenta** si su base es de 30 personas o más (`MIN_BASE`). Debajo, el resultado de la encuesta es
    demasiado ruidoso para medir contra él.
DI-VG3. **La estimación de un grupo** es la media de ese grupo en las elegidas que lo traen. Si ninguna lo trae, no hay
    estimación. Una pregunta sin elegidas (fallo de Luna) no entra.
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

from src.experiments import banco as ba                         # noqa: E402
from src.experiments import banco_lote7 as b7                   # noqa: E402
from src.experiments import voto_peso_fecha as pf               # noqa: E402
from src.experiments import voto_simulado as vs                 # noqa: E402

MIN_BASE = 30                                                    # DI-VG2
UMBRAL_DIF = 10.0                                                # §3: diferencia real clara, en puntos
MEJORA = 0.9                                                     # §4, R1
MIN_DIFS, ACIERTO_DIF = 10, 0.80                                 # §4, R2
CUANTIL = 0.80
SALIDA = ba.SALIDA / "voto_grupos.json"

GRUESOS = {
    "sexo": {"Hombres": ["Hombres"], "Mujeres": ["Mujeres"]},
    "estrato": {"1-2": ["1", "2"], "3": ["3"], "4-6": ["4", "5-6"]},
    "edad": {"joven": ["18-25", "18-24"], "media": ["26-40", "41-55", "25-34", "35-44", "45-54"], "mayor": ["56+", "55+"]},
}
EXTREMOS = {"sexo": ("Mujeres", "Hombres"), "estrato": ("1-2", "4-6"), "edad": ("joven", "mayor")}


# ---------------------------------------------------------------- grupos
def gruesos(rec: dict) -> dict:
    """DI-VG1: corte -> {grupo: (porcentaje, base)}, solo los grupos con base > 0."""
    out = {}
    for corte, grupos in GRUESOS.items():
        g, b = rec["grupos"].get(corte, {}), rec["bases"].get(corte, {})
        out[corte] = {}
        for nombre, partes in grupos.items():
            p = [(float(g[x]), float(b[x])) for x in partes if x in g and g[x] is not None and b.get(x)]
            base = sum(n for _, n in p)
            if base > 0:
                out[corte][nombre] = (sum(v * n for v, n in p) / base, base)
    return out


def estimar(ids: list[str], g_cand: dict) -> dict:
    """DI-VG3: corte -> {grupo: media en las elegidas que lo traen}."""
    out = {}
    for corte, grupos in GRUESOS.items():
        out[corte] = {}
        for nombre in grupos:
            v = [g_cand[i][corte][nombre][0] for i in ids if nombre in g_cand[i][corte]]
            if v:
                out[corte][nombre] = float(np.mean(v))
    return out


def pares(objetivos: list[dict], g_obj: dict, g_cand: dict, tot_cand: dict) -> pd.DataFrame:
    """Una fila por (pregunta, corte, grupo) con real de base suficiente y estimación."""
    filas = []
    for r in objetivos:
        if not r["ids"]:
            continue
        est = estimar(r["ids"], g_cand)
        s_total = float(np.mean([tot_cand[i] for i in r["ids"]]))
        for corte, grupos in g_obj[r["id"]].items():
            for nombre, (real, base) in grupos.items():
                if base >= MIN_BASE and nombre in est[corte]:
                    filas.append({"id": r["id"], "corte": corte, "grupo": nombre, "real": real, "base": base,
                                  "S": est[corte][nombre], "S_total": s_total})
    return pd.DataFrame(filas, columns=["id", "corte", "grupo", "real", "base", "S", "S_total"])


def diferencias(p: pd.DataFrame, corte: str) -> pd.DataFrame:
    """La diferencia entre los dos grupos extremos de un corte, real y estimada, por pregunta."""
    a, b = EXTREMOS[corte]
    x = p[p.corte == corte].pivot_table(index="id", columns="grupo", values=["real", "S"])
    if ("real", a) not in x or ("real", b) not in x:
        return pd.DataFrame(columns=["d_real", "d_est"])
    d = pd.DataFrame({"d_real": x[("real", a)] - x[("real", b)], "d_est": x[("S", a)] - x[("S", b)]}).dropna()
    return d


def medir(p: pd.DataFrame, corte: str, h: float) -> dict:
    q = p[p.corte == corte]
    d = diferencias(p, corte)
    claras = d[d.d_real.abs() >= UMBRAL_DIF]
    return {"pares": int(len(q)), "preguntas": int(q.id.nunique()), "base_mediana": float(q.base.median()) if len(q) else None,
            "eam_grupos": float((q.S - q.real).abs().mean()) if len(q) else None,
            "eam_referencia": float((q.S_total - q.real).abs().mean()) if len(q) else None,
            "cobertura": float(((q.S - q.real).abs() <= h).mean()) if len(q) else None,
            "diferencias_claras": int(len(claras)),
            "acierto_sentido": float((np.sign(claras.d_est) == np.sign(claras.d_real)).mean()) if len(claras) else None}


def regla(m: dict) -> dict:
    """§4, para un corte."""
    c = {"R1": m["eam_grupos"] is not None and m["eam_grupos"] <= MEJORA * m["eam_referencia"],
         "R2": m["diferencias_claras"] >= MIN_DIFS and (m["acierto_sentido"] or 0) >= ACIERTO_DIF}
    return {**c, "se_muestra": all(c.values())}


# ---------------------------------------------------------------- evaluar
def evaluar() -> dict:
    el = json.loads(pf.ELEGIDAS.read_text(encoding="utf-8"))
    rp = json.loads(b7.REALES.read_text(encoding="utf-8"))
    rg = json.loads(vs.REALES_G7.read_text(encoding="utf-8"))
    prac = vs.practica()
    tot = dict(zip(prac.id, prac.total))
    g_prac = {i: gruesos(rp[i]) for i in prac.id}
    g_guar = {i: gruesos(rg[i]) for i in vs.guardado().id}
    pp = pares(el["practica"], g_prac, g_prac, tot)
    pg = pares(el["guardado"], g_guar, g_prac, tot)
    out = {}
    for corte in GRUESOS:
        q = pp[pp.corte == corte]
        h = float(np.quantile((q.S - q.real).abs(), CUANTIL))                # §2: con la práctica
        m = medir(pg, corte, h)
        out[corte] = {"h": h, "practica": medir(pp, corte, h), "guardado": m, "regla": regla(m)}
    out["predicciones"] = {"PG1": out["estrato"]["regla"]["se_muestra"], "PG2": not out["sexo"]["regla"]["se_muestra"],
                           "PG3": out["edad"]["regla"]["se_muestra"]}
    return out


def main() -> int:
    warnings.simplefilter("ignore")
    out = evaluar()
    for corte in GRUESOS:
        x = out[corte]
        for n in ("practica", "guardado"):
            m = x[n]
            print(f"{corte:8} {n:9}: {m['pares']} pares en {m['preguntas']} preguntas (base mediana {m['base_mediana']}) | "
                  f"EAM grupos {m['eam_grupos']:.1f} contra el total {m['eam_referencia']:.1f} | cobertura ±{x['h']:.1f}: "
                  f"{m['cobertura']:.0%} | diferencias claras {m['diferencias_claras']}, sentido {m['acierto_sentido']}")
        print(f"         regla: {x['regla']}")
    print("predicciones:", out["predicciones"])
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
