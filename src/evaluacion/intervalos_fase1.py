"""
Plan v3, Fase 1 (`docs/INTERVALOS_FASE1_SPECIFICATION.md`): qué regla de rango cubre año a año. Validación de origen móvil con
la serie larga de la EPC (gestión del alcalde y del Concejo, 2014-2025) y las preguntas del catálogo 2022-2025. No llama a ningún
modelo.

Uso:
    python src/evaluacion/persistencia_epc.py      # primero
    python src/evaluacion/intervalos_fase1.py

DECISIONES DE IMPLEMENTACIÓN
============================

DI-IV1. **Lo favorable de la serie larga** es p4 + p5 («buena» o «muy buena»), como `GG3_GALAN` en el catálogo.
DI-IV2. **Los gobiernos:** Petro 2012-2015, Peñalosa 2016-2019, López 2020-2023 y Galán 2024-2027; el Concejo cambia en los
    mismos años. Las preguntas del catálogo 2022-2025 marcan cambio de gobierno solo en 2023 → 2024.
DI-IV3. **El percentil** es el de numpy (interpolación lineal), sobre los errores absolutos de los objetivos de años anteriores.
DI-IV4. **El rango para la página** (§6): la regla elegida, con todos los errores hasta 2025, por dominio, se guarda en
    `config/incertidumbre.json` (`fase1`), con la cobertura que tuvo en la prueba y su número de casos.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

P = RAIZ / "data" / "processed"
GOB = "gobierno e instituciones"
MINIMO = 5
K = 8
REGLAS = ("R1", "R2", "R3")


def gobierno(anio: int) -> str:
    """DI-IV2."""
    return "Petro" if anio <= 2015 else "Peñalosa" if anio <= 2019 else "López" if anio <= 2023 else "Galán"


def objetivos() -> pd.DataFrame:
    filas = []
    s = pd.read_csv(P / "serie_epc_bcv.csv")
    s["v"] = 100 * (s.p4 + s.p5)                                                                          # DI-IV1
    for item, g in s.groupby("item"):
        g = g.sort_values("anio")
        for (a0, v0), (a1, v1) in zip(zip(g.anio, g.v), list(zip(g.anio, g.v))[1:]):
            filas.append({"serie": item, "dominio": GOB, "anio_base": int(a0), "anio": int(a1), "base": v0, "real": v1})
    c = pd.read_csv(P / "benchmark" / "persistencia_epc.csv")
    c = c[~c.variable.isin(["GG3_GALAN", "CC5A_GALAN"])]
    for r in c.itertuples():
        filas.append({"serie": r.variable, "dominio": r.dominio if r.dominio == GOB else "lo demás", "anio_base": int(r.anio_base),
                      "anio": int(r.anio_objetivo), "base": r.dato_base, "real": r.real})
    t = pd.DataFrame(filas)
    t["error"] = (t.real - t.base).abs()
    t["salto"] = (t.anio - t.anio_base) > 1
    t["cambio"] = [gobierno(a) != gobierno(b) for a, b in zip(t.anio_base, t.anio)]
    return t


def anchos(t: pd.DataFrame) -> pd.DataFrame:
    """§3: h de cada regla para cada objetivo, solo con los errores de años anteriores."""
    t = t.copy()
    for r in REGLAS:
        t[r] = np.nan
    t["n_previos"] = 0
    for anio in sorted(t.anio.unique()):
        prev = t[t.anio < anio]
        m = t.anio == anio
        t.loc[m, "n_previos"] = len(prev)
        if len(prev) < MINIMO:
            continue
        p_all = float(np.quantile(prev.error, 0.8))
        for i in t.index[m]:
            d = prev[prev.dominio == t.at[i, "dominio"]]
            n_d = len(d)
            p_d = float(np.quantile(d.error, 0.8)) if n_d >= 2 else p_all
            w = n_d / (n_d + K)
            r2 = w * p_d + (1 - w) * p_all
            t.at[i, "R1"] = p_all
            t.at[i, "R2"] = r2
            t.at[i, "R3"] = r2 * 1.5 if (t.at[i, "salto"] or t.at[i, "cambio"] or n_d < K) else r2
    return t


def cobertura(t: pd.DataFrame) -> dict:
    e = t.dropna(subset=["R1"])
    out = {}
    for r in REGLAS:
        dentro = e.error <= e[r]
        out[r] = {"total": round(float(dentro.mean()), 3), "gobierno": round(float(dentro[e.dominio == GOB].mean()), 3),
                  "lo_demas": round(float(dentro[e.dominio != GOB].mean()), 3),
                  "alcalde_concejo": round(float(dentro[e.serie.isin(["gestion_alcalde", "gestion_concejo"])].mean()), 3),
                  "ancho_medio": round(float(2 * e[r].mean()), 1)}
    return out


def decidir(cob: dict) -> tuple[str, bool]:
    """§6: (regla elegida, si cumple las dos condiciones)."""
    cumplen = [r for r in REGLAS if cob[r]["total"] >= 0.75 and cob[r]["gobierno"] >= 0.70]
    if cumplen:
        return min(cumplen, key=lambda r: cob[r]["ancho_medio"]), True
    return max(REGLAS, key=lambda r: cob[r]["gobierno"]), False


def main() -> int:
    t = anchos(objetivos())
    e = t.dropna(subset=["R1"])
    cob = cobertura(t)
    elegida, cumple = decidir(cob)
    sens = {int(a): {r: round(float((e[e.anio != a].error <= e[e.anio != a][r]).mean()), 3) for r in REGLAS}
            for a in sorted(e.anio.unique())}
    por_anio = {int(a): {"n": int(len(g)), **{r: round(float((g.error <= g[r]).mean()), 2) for r in REGLAS},
                         "error_medio": round(float(g.error.mean()), 1)} for a, g in e.groupby("anio")}
    marcas = {k: {"n": int(len(g)), "error_medio": round(float(g.error.mean()), 1),
                  **{r: round(float((g.error <= g[r]).mean()), 2) for r in REGLAS}}
              for k, g in (("con cambio de gobierno", e[e.cambio]), ("con salto", e[e.salto & ~e.cambio]),
                           ("sin salto ni cambio", e[~e.salto & ~e.cambio]))}
    pred = {"PI1": cob["R1"]["gobierno"] < 0.70, "PI2": cob["R3"]["total"] >= 0.75 and cob["R3"]["gobierno"] >= 0.70,
            "PI3": marcas["con cambio de gobierno"]["error_medio"] == max(v["error_medio"] for v in marcas.values())}
    out = {"objetivos_evaluados": int(len(e)), "fuera_por_pocos_previos": int(t.R1.isna().sum()), "cobertura": cob,
           "elegida": elegida, "cumple": cumple, "por_anio": por_anio, "marcas": marcas, "sensibilidad": sens, "predicciones": pred}
    (P / "benchmark").mkdir(parents=True, exist_ok=True)
    t.round(2).to_csv(P / "benchmark" / "intervalos_fase1.csv", index=False, encoding="utf-8")
    (P / "benchmark" / "intervalos_fase1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))
    # DI-IV4: el rango de hoy por dominio, con todos los errores, y lo que cubrió en la prueba
    p_all = float(np.quantile(t.error, 0.8))
    hoy = {}
    for dom, clave in ((GOB, "gobierno"), ("lo demás", "lo_demas")):
        d = t[t.dominio == dom]
        w = len(d) / (len(d) + K)
        r2 = w * float(np.quantile(d.error, 0.8)) + (1 - w) * p_all
        hoy[clave] = {"h": round(r2, 1), "h_con_cambio_de_gobierno": round(1.5 * r2, 1),
                      "cobertura_en_prueba": cob[elegida][clave], "casos_en_prueba": int((e.dominio == dom).sum())}
    ruta = RAIZ / "config" / "incertidumbre.json"
    inc = json.loads(ruta.read_text(encoding="utf-8"))
    inc["fase1"] = {"regla": elegida, "cumple_la_regla": cumple, "provisional": not cumple, "por_dominio": hoy,
                    "fuente": "INTERVALOS_FASE1_RESULTS.md"}
    ruta.write_text(json.dumps(inc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("rango de hoy:", json.dumps(hoy, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
