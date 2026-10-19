"""
Fase B del plan de mejoras (`docs/SELECTOR_FASE_B_SPECIFICATION.md`): ¿deben los agentes mover un dato ya medido, y cuánto?
Persistencia, agentes y la combinación P + λ·(G − P), con λ elegido en un par de años de la EPC y evaluado en el otro.

Uso:
    python src/evaluacion/selector_fase_b.py --simulado    # sin gasto: prueba el circuito
    python src/evaluacion/selector_fase_b.py               # con el modelo real (tope USD 2)

DECISIONES DE IMPLEMENTACIÓN
============================

DI-SB1. **La llamada es la de la página** (`agentes.Agentes` con los datos del año base), con las preguntas en tandas de hasta
    `TANDA` y la nota de `ACTUALIDAD_EPC` con los años de cada par.
DI-SB2. **Lo que se cuenta** es el lado de `motor.lado`, como en `persistencia_epc.py`: la probabilidad de esas opciones entre las
    de la escala, ponderada con el peso de la encuesta.
DI-SB3. **λ se elige en la rejilla 0-1 de 0,05** con el error medio del otro par. Si dos λ empatan, el menor: ante la duda, no
    mover el dato.
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "benchmark"
TOPE_USD = 2.0
TANDA = 20
PARES = (("P1", 2023, 2024), ("P2", 2024, 2025))
REJILLA = np.round(np.arange(0, 1.0001, 0.05), 2)
GOB = "gobierno e instituciones"
CONCEJO = "¿Usted cómo califica, en términos generales, la gestión del Concejo de Bogotá?"


def nota(base: int, obj: int) -> str:
    return (f"Las respuestas de arriba son de {base}. Estas preguntas son de finales de {obj}, casi un año después: la persona "
            "puede haber cambiado de opinión.")


def preguntas(vars_: list[str], catalogo: dict) -> list[dict]:
    from src.consulta import motor as mo
    out = []
    for k, v in enumerate(vars_, 1):
        f = catalogo[v]
        texto = mo.GALAN_SOLO_AGENTES.get(v) or (CONCEJO if v == "CC5A_GALAN" else f["pregunta"].strip())
        out.append({"clave": f"Q{k:02d}", "variable": v, "pregunta": texto, "validos": list(f["escala"]),
                    "cuenta": mo.lado(f)[0], "categorias": dict(zip(f["escala"], mo.escala_visible(f)))})
    return out


def estimar(panel, esc: list[dict], extra: str, llamar, cache, modelo: str) -> dict[str, Optional[float]]:
    """DI-SB1, DI-SB2: el porcentaje de los agentes por variable."""
    from src.consulta import agentes as ag
    from src.experiments import personas_pulidas as pp
    sistema = pp.BASE + pp.SALIDA_PROB
    tandas = [esc[i:i + TANDA] for i in range(0, len(esc), TANDA)]

    def uno(perfil):
        res = {}
        for t in tandas:
            if e9.gasto_registrado(cache)["costo_usd"] >= TOPE_USD:
                raise RuntimeError(f"Se llegó al tope de USD {TOPE_USD}.")
            preg = "\n".join(f'{e["clave"]}. {e["pregunta"]} Opciones: '
                             + "; ".join(f"{c}={x}" for c, x in e["categorias"].items()) for e in t)
            u = f"QUIÉN ES:\n{perfil}\n\n{extra}\n\nPREGUNTAS NUEVAS:\n{preg}"
            texto, _ = e9.pedir(llamar, cache, modelo, ag.TEMPERATURA, sistema, u, 0)
            res.update(pp.leer_prob(texto, t))
        return res
    with ThreadPoolExecutor(max_workers=ag.PARALELO) as ex:
        ps = list(ex.map(uno, panel.perfiles))
    w = panel.peso
    out = {}
    for e in esc:
        v = [(j, sum(p[e["clave"]].get(c, 0) for c in e["cuenta"])) for j, p in enumerate(ps) if p.get(e["clave"])]
        out[e["variable"]] = float(100 * sum(w[j] * x for j, x in v) / sum(w[j] for j, _ in v)) if v else None
    return out


def combinar(p: np.ndarray, g: np.ndarray, lam: float) -> np.ndarray:
    return p + lam * (g - p)


def elegir_lambda(t: pd.DataFrame) -> float:
    """DI-SB3."""
    errs = [np.mean(np.abs(combinar(t.P.to_numpy(), t.G.to_numpy(), l) - t.real.to_numpy())) for l in REJILLA]
    return float(REJILLA[int(np.argmin(np.round(errs, 6)))])


def evaluar(t: pd.DataFrame) -> dict:
    """§4 y §6. `t`: una fila por pregunta y par, con P, G, real, dominio y par."""
    t = t.copy()
    out = {"lambdas": {}, "por_par": {}}
    for par in ("P1", "P2"):
        otro = t[t.par != par]
        lam = elegir_lambda(otro)
        lam_g, lam_r = elegir_lambda(otro[otro.dominio == GOB]), elegir_lambda(otro[otro.dominio != GOB])
        m = t.par == par
        t.loc[m, "C"] = combinar(t.loc[m, "P"].to_numpy(), t.loc[m, "G"].to_numpy(), lam)
        lam_fila = np.where(t.loc[m, "dominio"] == GOB, lam_g, lam_r)
        t.loc[m, "Cd"] = t.loc[m, "P"] + lam_fila * (t.loc[m, "G"] - t.loc[m, "P"])
        out["lambdas"][par] = {"C": lam, "Cd_gobierno": lam_g, "Cd_resto": lam_r}
    for k in ("P", "G", "C", "Cd"):
        t[f"e_{k}"] = (t[k] - t.real).abs()
    for par in ("P1", "P2"):
        s = t[t.par == par]
        out["por_par"][par] = {k: round(float(s[f"e_{k}"].mean()), 2) for k in ("P", "G", "C", "Cd")}
    out["juntos"] = {k: round(float(t[f"e_{k}"].mean()), 2) for k in ("P", "G", "C", "Cd")}
    gob = t[t.dominio == GOB]
    out["gobierno"] = {k: round(float(gob[f"e_{k}"].mean()), 2) for k in ("P", "G", "C", "Cd")} if len(gob) else {}
    out["por_dominio"] = {d: {"n": int(len(s)), "P": round(float(s.e_P.mean()), 2), "G": round(float(s.e_G.mean()), 2)}
                          for d, s in t.groupby("dominio")}
    reglas = {}
    for k in ("C", "Cd"):
        rs1 = all(out["por_par"][p][k] < out["por_par"][p]["P"] for p in ("P1", "P2"))
        gana = (t.e_P - t[f"e_{k}"]).sort_values(ascending=False)
        resto = t.drop(gana.index[:2])
        rs2 = float(resto[f"e_{k}"].mean()) < float(resto.e_P.mean())
        rs3 = (not len(gob)) or float(gob[f"e_{k}"].mean()) <= float(gob.e_P.mean()) + 0.5
        reglas[k] = {"RS1": bool(rs1), "RS2": bool(rs2), "RS3": bool(rs3), "pasa": bool(rs1 and rs2 and rs3)}
    out["reglas"] = reglas
    lams = [out["lambdas"][p]["C"] for p in ("P1", "P2")]
    ganancia = out["juntos"]["P"] - out["juntos"]["C"]
    out["predicciones"] = {"PS1": all(l <= 0.2 for l in lams), "PS2": (not reglas["C"]["RS1"]) or ganancia < 0.3,
                           "PS3": all(v["G"] > v["P"] for v in out["por_dominio"].values() if v["n"] >= 5)}
    out["lambda_final"] = elegir_lambda(t)
    return out, t


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args(argv)
    from src.consulta import agentes as ag
    from src.consulta import reformular as rf
    from src.evaluacion import persistencia_epc as pe
    from src.experiments import personas_con_encuesta as pc
    catalogo = rf.cargar_catalogo(rf.CATALOGO_2025)
    sal = SALIDA / ("simulado" if a.simulado else "")
    sal.mkdir(parents=True, exist_ok=True)
    cache = e9.Cache(sal / "cache_selector.json")
    if a.simulado:
        rng = np.random.default_rng(0)

        def llamar(m, s, u, t):
            claves = [l.split(".")[0] for l in u.split("PREGUNTAS NUEVAS:\n")[1].splitlines()]
            return json.dumps({k: {str(c): float(x) for c, x in enumerate(rng.dirichlet(np.ones(5)), 1)} for k in claves})
        modelo = e9.MODELO_SIMULADO
    else:
        llamar, modelo = e9.cliente_real(timeout=300, extra={"reasoning": {"effort": "low"}}), ag.MODELO
    filas = []
    for par, base, obj in PARES:
        r_base, r_obj = pe.cifras(base), pe.cifras(obj)
        vars_ = sorted(set(r_base) & set(r_obj))
        esc = preguntas(vars_, catalogo)
        panel = ag.Agentes(datos=pc.datos(base))
        g = estimar(panel, esc, nota(base, obj), llamar, cache, modelo)
        for v in vars_:
            filas.append({"par": par, "variable": v, "dominio": pe.dominio(v), "P": r_base[v], "G": g[v], "real": r_obj[v]})
        print(f"{par}: {len(vars_)} preguntas, sin respuesta de los agentes en {sum(g[v] is None for v in vars_)}", flush=True)
    t = pd.DataFrame(filas).dropna(subset=["G"])
    res, t = evaluar(t)
    t.round(2).to_csv(sal / "selector_fase_b.csv", index=False, encoding="utf-8")
    g = None if a.simulado else e9.gasto_registrado(cache)["costo_usd"]
    print(json.dumps({k: res[k] for k in ("lambdas", "por_par", "juntos", "gobierno", "reglas", "predicciones",
                                          "lambda_final")}, ensure_ascii=False, indent=1))
    print("por dominio (P contra G):")
    for d, v in sorted(res["por_dominio"].items(), key=lambda x: -x[1]["n"]):
        print(f"  {d:26} n={v['n']:2}  P {v['P']:5.1f}  G {v['G']:5.1f}")
    print(f"gasto USD {g}")
    (sal / "selector_fase_b.json").write_text(json.dumps({**res, "gasto": g}, ensure_ascii=False, indent=1, default=float),
                                              encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
