"""
Techo del orden entre grupos (`docs/TECHO_GRUPOS_SPECIFICATION.md`): ¿cuánto es lo máximo que se
puede acertar de las diferencias claras entre grupos de las preguntas de PRÁCTICA del banco?
Solo cálculo local, sin API. Lee el banco con `banco.practica()`; las guardadas no se tocan.

    Medida 1 — réplica por mitades: pares claros en una mitad, ¿mismo orden en la otra?
    Medida 2 — oráculo por Bayes empírico: ¿cuántos pares claros tienen el orden real?

Uso:
    python src/experiments/techo_grupos.py

Escribe `data/processed/banco/techo_grupos.json` (solo cifras agregadas).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-TG1. **La partición se sortea una vez por fuente y partición**, no por pregunta: todas las
    preguntas de una misma encuesta usan las mismas mitades, como pasaría si la encuesta se
    hubiera hecho dos veces.

DI-TG2. **Conglomerado** (pre-registro §3): EPC 2019, 2023 y 2024, localidad × manzana; ECP, el
    hogar (`DIRECTORIO`); EPC 2017 y 2022, la persona. Si a una fuente le falta la columna
    esperada, se detiene: no cae a la persona sin avisar.

DI-TG3. **El oráculo agrupa los pares por dimensión** (sexo, edad, estrato) a través de todas las
    preguntas para estimar τ², porque el tamaño típico de las diferencias depende mucho de la
    dimensión (el estrato separa más que el sexo). Las CNC entran: solo necesita agregados.
"""

from __future__ import annotations

import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import banco as ba                    # noqa: E402
from src.experiments import banco_reales as br             # noqa: E402

SALIDA = ba.SALIDA / "techo_grupos.json"
N_PARTICIONES = 200
SEMILLA = 20261002
DEFF = 2.03                                                  # DI-D7, mediana de la EPC
DIMS = ("sexo", "edad", "estrato")


class TechoError(RuntimeError):
    """Algo impide calcular el techo como está pre-registrado."""


# --------------------------------------------------------------------------
# Medida 2: oráculo por Bayes empírico

def z_pares(res: dict, dim: str) -> list[float]:
    """z de todos los pares de grupos de una dimensión (no solo los claros), con el error de la regla."""
    g, b = res["grupos"].get(dim, {}), res["bases"].get(dim, {})
    out = []
    for a, c in itertools.combinations(g, 2):
        pa, pc = g[a] / 100, g[c] / 100
        se = math.sqrt(pa * (1 - pa) / b[a] + pc * (1 - pc) / b[c]) if b[a] and b[c] else 0
        if se > 0:
            out.append((pa - pc) / se)
    return out


def tau2(zs: list[float], d: float) -> float:
    return max(0.0, float(np.var(zs)) - d) if len(zs) > 1 else 0.0


def p_orden_real(z: float, t2: float, d: float) -> float:
    """Probabilidad de que el orden real sea el observado (pre-registro §3, medida 2)."""
    if t2 <= 0:
        return 0.5
    return float(_phi(abs(z) * math.sqrt(t2) / math.sqrt(d * (t2 + d))))


def _phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def oraculo(reales: dict, d: float) -> dict:
    """Techo del oráculo sobre los pares claros de todas las preguntas (DI-TG3)."""
    t2 = {dim: tau2([z for r in reales.values() for z in z_pares(r, dim)], d) for dim in DIMS}
    ps = []
    for r in reales.values():
        for dim, hi, lo in r["pares_claros"]:
            g, b = r["grupos"][dim], r["bases"][dim]
            pa, pc = g[hi] / 100, g[lo] / 100
            z = (pa - pc) / math.sqrt(pa * (1 - pa) / b[hi] + pc * (1 - pc) / b[lo])
            ps.append(p_orden_real(z, t2[dim], d))
    return {"techo": float(np.mean(ps)), "pares": len(ps), "tau2": t2}


# --------------------------------------------------------------------------
# Medida 1: réplica por mitades

def porcentajes(fav, ok, w, grupo, etiquetas) -> tuple[dict, dict]:
    """% favorable ponderado y base sin ponderar por grupo (como `banco_reales.resultado`)."""
    g, b = {}, {}
    for e in etiquetas:
        m = ok & (grupo == e)
        if m.sum():
            g[e] = 100 * float(np.sum(fav[m] * w[m]) / np.sum(w[m]))
            b[e] = int(m.sum())
    return g, b


def replica(preguntas: list[dict], mitad_a: np.ndarray) -> tuple[int, int]:
    """(aciertos, pares): pares claros en la mitad A y su orden en la B. Un empate es fallo."""
    ac = pa = 0
    for q in preguntas:
        res_a = {"grupos": {}, "bases": {}}
        res_b = {"grupos": {}, "bases": {}}
        for dim in DIMS:
            res_a["grupos"][dim], res_a["bases"][dim] = porcentajes(q["fav"], q["ok"] & mitad_a, q["w"], q[dim], q["etq"][dim])
            res_b["grupos"][dim], res_b["bases"][dim] = porcentajes(q["fav"], q["ok"] & ~mitad_a, q["w"], q[dim], q["etq"][dim])
        for dim, hi, lo in br.pares_claros(res_a):
            gb = res_b["grupos"][dim]
            pa += 1
            ac += int(hi in gb and lo in gb and gb[hi] > gb[lo])
    return ac, pa


def sortear_mitad(psu: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """DI-TG1: cada conglomerado entero a la mitad A o a la B."""
    cods, inv = np.unique(psu, return_inverse=True)
    return (rng.random(len(cods)) < 0.5)[inv]


# --------------------------------------------------------------------------
# Datos

def _psu(fuente: str, anio: int, d: pd.DataFrame) -> np.ndarray:
    """DI-TG2."""
    from src.utils.diseno import CONGLOMERADO_POR_ANIO
    if fuente == "ECP DANE":
        if "DIRECTORIO" not in d.columns:
            raise TechoError("ECP: falta DIRECTORIO para partir por hogar.")
        return d["DIRECTORIO"].astype(str).to_numpy()
    if anio in CONGLOMERADO_POR_ANIO:
        col = CONGLOMERADO_POR_ANIO[anio][0].upper()
        if col not in d.columns:
            raise TechoError(f"EPC {anio}: falta {col}.")
        return (d["localidad"].astype(str) + "|" + d[col].astype(str)).to_numpy()
    if anio in (2017, 2022):
        return np.arange(len(d)).astype(str)
    raise TechoError(f"EPC {anio}: no hay regla de conglomerado pre-registrada.")


def cargar(reales: dict) -> dict[tuple, dict]:
    """Por fuente: (psu, preguntas con sus arreglos). Solo las preguntas con pares claros."""
    p = ba.practica().set_index("id")
    fuentes = {}
    for qid, r in reales.items():
        if r["fuente"] == "Biblioteca CNC":
            continue
        f = p.loc[qid]
        clave = ("ECP DANE", 2023) if f["fuente"] == "ECP DANE" else ("EPC", int(f["anio"]))
        if clave not in fuentes:
            d = br._ecp() if clave[0] == "ECP DANE" else br._epc(clave[1])
            fuentes[clave] = {"d": d, "psu": _psu(clave[0], clave[1], d), "preguntas": []}
        d = fuentes[clave]["d"]
        x = pd.to_numeric(d[str(f["variable"]).upper()], errors="coerce")
        w = pd.to_numeric(d.w, errors="coerce")
        ok = (x.isin(br.validos(br.categorias(f["categorias"]))) & w.notna() & (w > 0)).to_numpy()
        fav = x.isin(json.loads(f["codigos_favorables"])).astype(float).to_numpy()
        q = {"id": qid, "fav": fav, "ok": ok, "w": w.fillna(0).to_numpy(float), "etq": {}}
        for dim in DIMS:
            q[dim] = d[dim].to_numpy(object)
            q["etq"][dim] = list(r["grupos"][dim])
        fuentes[clave]["preguntas"].append(q)
    for v in fuentes.values():
        del v["d"]
    return fuentes


def medida_replica(fuentes: dict, n: int = N_PARTICIONES, semilla: int = SEMILLA) -> dict:
    rng = np.random.default_rng(semilla)
    tasas, pares = [], []
    for _ in range(n):
        ac = pa = 0
        for clave in sorted(fuentes):
            a, p = replica(fuentes[clave]["preguntas"], sortear_mitad(fuentes[clave]["psu"], rng))
            ac, pa = ac + a, pa + p
        tasas.append(ac / pa)
        pares.append(pa)
    return {"media": float(np.mean(tasas)), "p5": float(np.percentile(tasas, 5)),
            "p95": float(np.percentile(tasas, 95)), "pares_mediana": int(np.median(pares)), "particiones": n}


# --------------------------------------------------------------------------

def lectura(techo: float) -> str:
    """Pre-registro §5."""
    return "A" if techo >= 0.80 else ("B" if techo >= 0.70 else "C")


def main() -> int:
    todas = json.loads(br.SALIDA.read_text(encoding="utf-8"))
    reales = {k: v for k, v in todas.items() if not v["excluida"] and v["pares_claros"]}
    print(f"{len(reales)} preguntas, {sum(len(v['pares_claros']) for v in reales.values())} pares claros")
    o1, o2 = oraculo(reales, 1.0), oraculo(reales, DEFF)
    print(f"oráculo D=1: {o1['techo']:.3f}   D={DEFF}: {o2['techo']:.3f}   τ² (D={DEFF}): "
          + ", ".join(f"{k} {v:.2f}" for k, v in o2["tau2"].items()))
    fuentes = cargar(reales)
    print("fuentes: " + ", ".join(f"{k[0]} {k[1]} ({len(v['preguntas'])}, {len(set(v['psu']))} conglomerados)"
                                  for k, v in sorted(fuentes.items())))
    rep = medida_replica(fuentes)
    print(f"réplica por mitades: {rep['media']:.3f} (p5 {rep['p5']:.3f}, p95 {rep['p95']:.3f}; "
          f"~{rep['pares_mediana']} pares por partición)")
    out = {"oraculo_D1": o1, f"oraculo_D{DEFF}": o2, "replica": rep, "lectura": lectura(o2["techo"]),
           "referencias": {"tono_general": 0.619, "puente_mejor": 0.627, "azar": 0.503},
           "predicciones": {"P1": 0.70 <= rep["media"] <= 0.85, "P2": o1["techo"] >= 0.85,
                            "P3": 0.75 <= o2["techo"] <= 0.90, "P4": rep["media"] < o2["techo"]}}
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"lectura: {out['lectura']}; predicciones: {out['predicciones']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
