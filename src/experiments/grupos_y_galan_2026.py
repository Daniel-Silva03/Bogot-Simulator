"""
Agentes 2026: el voto por grupos (parte A) y la aprobación de Galán (parte B). `docs/GRUPOS_Y_GALAN_2026_SPECIFICATION.md`.

Uso:
    python src/experiments/grupos_y_galan_2026.py grupos            # sin gasto: caché de voto_campana
    python src/experiments/grupos_y_galan_2026.py galan --simulado
    python src/experiments/grupos_y_galan_2026.py galan             # tope USD 1

La parte A necesita `BSS_ELECTORAL_DIR` y `BSS_CNC_POLITICA_DIR` no hace falta: lee los resultados guardados del lote 7.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-GG1. **Parte A sin llamadas:** se reconstruye el mensaje de C2 de cada agente y se lee su respuesta de la caché de
    `voto_campana`. Si alguno no está, queda fuera y se cuenta.
DI-GG2. **La parte de Cepeda entre los dos**, c / (c + a), en porcentaje. En el CNC, con el voto por cada fórmula en el grupo
    (`voto_grupos.gruesos`).
DI-GG3. **Nada del CNC se imprime** (D21): de la parte A salen solo los errores y los signos.
DI-GG4. **El perfil sin opiniones de gobierno** (P) quita las siete columnas de 2025 de `personas_politica.ESCONDIDAS` que son del
    catálogo.
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

SALIDA = RAIZ / "data" / "processed" / "grupos_y_galan_2026"
TOPE_USD = 1.0
CORTES = {"sexo": ("Hombres", "Mujeres"), "estrato": ("1-2", "3", "4-6"), "edad": ("joven", "media", "mayor")}
BRECHAS = {"sexo": ("Mujeres", "Hombres"), "estrato": ("1-2", "4-6"), "edad": ("joven", "mayor")}
G = (("G1", "¿Usted aprueba o desaprueba la gestión del alcalde de Bogotá, Carlos Fernando Galán?",
      {1: "Aprueba", 2: "Desaprueba", 9: "No sabe"}, [1], 53.3),
     ("G2", "¿Qué imagen tiene usted del alcalde de Bogotá, Carlos Fernando Galán?",
      {1: "Muy negativa", 2: "Negativa", 3: "Positiva", 4: "Muy positiva", 9: "No sabe"}, [3, 4], 44.3))
EPC_2025 = 45.0


def grupos_agentes(d: pd.DataFrame) -> dict[str, np.ndarray]:
    """A2: los cortes gruesos para los agentes."""
    num = lambda c: pd.to_numeric(d[c], errors="coerce")                         # noqa: E731
    est, edad = num("DMO_4_1"), num("DMO_3_1")
    return {"sexo": num("DMO_1").map({1: "Hombres", 2: "Mujeres"}).to_numpy(),
            "estrato": np.where(est <= 2, "1-2", np.where(est == 3, "3", np.where(est >= 4, "4-6", None))),
            "edad": np.where(edad <= 25, "joven", np.where(edad <= 55, "media", "mayor"))}


def parte_cepeda(c: float, a: float) -> Optional[float]:
    """DI-GG2."""
    return 100 * c / (c + a) if (c + a) > 0 else None


def medir_grupos(ag: dict[str, dict[str, float]], cnc: dict[str, dict[str, float]], ciudad: float) -> dict:
    """A3: errores y signos."""
    errs, unif = [], []
    for corte, gs in CORTES.items():
        for g in gs:
            if g in ag.get(corte, {}) and g in cnc.get(corte, {}):
                errs.append(abs(ag[corte][g] - cnc[corte][g])); unif.append(abs(ciudad - cnc[corte][g]))
    signos = {}
    for corte, (x, y) in BRECHAS.items():
        if all(k in ag[corte] and k in cnc[corte] for k in (x, y)):
            signos[corte] = (ag[corte][x] - ag[corte][y] > 0) == (cnc[corte][x] - cnc[corte][y] > 0)
    return {"error_grupos": round(float(np.mean(errs)), 1), "error_ciudad_para_todos": round(float(np.mean(unif)), 1),
            "grupos": len(errs), "signos": signos, "signos_correctos": sum(signos.values())}


def parte_a() -> dict:
    from src.consulta import agentes as ag
    from src.experiments import banco_lote7 as b7, personas_pulidas as pp, voto_agentes as va, voto_campana as vc
    from src.experiments import voto_grupos as vg, voto_registraduria as vr, voto_simulado as vs
    reales = vr.reales("E3")
    ops = va.opciones(reales)
    panel = ag.Agentes()
    cache = e9.Cache(vc.SALIDA / "cache.json")
    sistema = pp.BASE + pp.SALIDA_PROB
    lineas = "; ".join(f"{i}={o}" for i, o in enumerate(ops, 1))
    esc = [{"clave": "E1", "validos": list(range(1, len(ops) + 1))}]
    extra = vc.RESUMEN + "\n\n" + vc.ENCUESTA
    i_c = next(i for i, o in enumerate(ops, 1) if "Cepeda" in o)
    i_a = next(i for i, o in enumerate(ops, 1) if "Espriella" in o)
    pc_, pa_, falta = [], [], 0
    for p in panel.perfiles:                                                         # DI-GG1
        u = f"QUIÉN ES:\n{p}\n\n{extra}\n\nPREGUNTAS NUEVAS:\nE1. {va.PREGUNTA} Opciones: {lineas}"
        t = cache.get(e9.Cache.clave(va.MODELO, va.TEMPERATURA, sistema, u, 0))
        q = pp.leer_prob(t or "", esc)["E1"]
        if q is None:
            falta += 1; pc_.append(np.nan); pa_.append(np.nan); continue
        pc_.append(q.get(i_c, 0)); pa_.append(q.get(i_a, 0))
    pc_, pa_, w = np.array(pc_), np.array(pa_), panel.peso
    ok = ~np.isnan(pc_)
    gr = grupos_agentes(panel.datos[1].iloc[panel.personas])
    def parte(m):
        m = m & ok
        return parte_cepeda(float(np.sum(w[m] * pc_[m])), float(np.sum(w[m] * pa_[m])))
    agentes = {c: {g: parte(gr[c] == g) for g in gs if ((gr[c] == g) & ok).any()} for c, gs in CORTES.items()}
    ciudad = parte(np.ones(len(w), bool))
    r = {**json.loads(b7.REALES.read_text(encoding="utf-8")), **json.loads(vs.REALES_G7.read_text(encoding="utf-8"))}
    gc, ga = vg.gruesos(r["CC893701_P1_1"]), vg.gruesos(r["CC893701_P1_2"])
    cnc = {c: {g: parte_cepeda(gc[c][g][0], ga[c][g][0]) for g in gs if g in gc.get(c, {}) and g in ga.get(c, {})}
           for c, gs in CORTES.items()}
    m = medir_grupos(agentes, cnc, ciudad)
    regla = {"RA1": m["error_grupos"] <= m["error_ciudad_para_todos"] - 1, "RA2": m["signos_correctos"] >= 2}
    regla["reparten_bien"] = all(regla.values())
    pred = {"PA1": regla["RA2"], "PA2": not regla["RA1"]}
    return {**m, "agentes_sin_cache": falta, "regla": regla, "predicciones": pred}                   # DI-GG3


def parte_b(simulado: bool) -> dict:
    from src.consulta import agentes as ag
    from src.experiments import personas_politica as pq, personas_pulidas as pp
    panel = ag.Agentes()
    base, d, perf = panel.datos
    ocultas = [{"variable": c} for _, c, v in pq.ESCONDIDAS if v]                                    # DI-GG4
    sistema = pp.BASE + pp.SALIDA_PROB
    esc = [{"clave": k, "pregunta": t, "categorias": c, "validos": [x for x in c if x != 9]} for k, t, c, _, _ in G]
    preg = "\n".join(f'{e["clave"]}. {e["pregunta"]} Opciones: ' + "; ".join(f"{c}={t}" for c, t in e["categorias"].items())
                     for e in esc)
    sal = SALIDA / ("simulado" if simulado else "")
    sal.mkdir(parents=True, exist_ok=True)
    cache = e9.Cache(sal / "cache.json")
    if simulado:
        rng = np.random.default_rng(0)
        llamar = lambda m, s, u, t: json.dumps({e["clave"]: {str(c): float(x) for c, x in zip(e["validos"], rng.dirichlet(np.ones(len(e["validos"]))))} for e in esc})  # noqa: E731
    else:
        llamar = e9.cliente_real(timeout=300, extra={"reasoning": {"effort": "low"}})
    out = {}
    for brazo, ocult in (("P", ocultas), ("F", [])):
        def uno(i):
            if e9.gasto_registrado(cache)["costo_usd"] >= TOPE_USD:
                raise RuntimeError(f"Se llegó al tope de USD {TOPE_USD}.")
            u = f"QUIÉN ES:\n{pq.perfil(i, panel.datos, ocult, {}, con_vida=False)}\n\nPREGUNTAS NUEVAS:\n{preg}"
            texto, _ = e9.pedir(llamar, cache, va_modelo(), 1.0, sistema, u, 0)
            return pp.leer_prob(texto, esc)
        with ThreadPoolExecutor(max_workers=16) as ex:
            probs = list(ex.map(uno, panel.personas))
        res = {}
        for k, _, _, fav, real in G:
            ok = [j for j, p in enumerate(probs) if p[k]]
            w = panel.peso
            v = 100 * sum(w[j] * sum(probs[j][k].get(c, 0) for c in fav) for j in ok) / sum(w[j] for j in ok)
            v = float(v)
            res[k] = {"agentes": round(v, 1), "real": real, "error": round(abs(v - real), 1)}
        res["error_medio"] = round(float(np.mean([res[k]["error"] for k, *_ in G])), 1)
        out[brazo] = res
        print(f"{brazo}: {res}", flush=True)
    epc = round(float(np.mean([abs(EPC_2025 - real) for *_, real in G])), 1)
    mejor = min(("P", "F"), key=lambda b: out[b]["error_medio"])
    regla = {"RB1": out[mejor]["error_medio"] <= 7, "RB2": out[mejor]["error_medio"] < epc}
    regla["se_acercan"] = all(regla.values())
    pred = {"PB1": out["F"]["error_medio"] < out["P"]["error_medio"], "PB2": not (out[mejor]["G2"]["error"] < abs(EPC_2025 - 44.3)),
            "PB3": out[mejor]["G1"]["agentes"] < 53.3}
    g = None if simulado else e9.gasto_registrado(cache)["costo_usd"]
    return {"brazos": out, "error_epc_2025": epc, "error_50": round(float(np.mean([abs(50 - r) for *_, r in G])), 1),
            "mejor": mejor, "regla": regla, "predicciones": pred, "gasto": g}


def va_modelo() -> str:
    from src.consulta import agentes as ag
    return ag.MODELO


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("parte", choices=("grupos", "galan"))
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args(argv)
    r = parte_a() if a.parte == "grupos" else parte_b(a.simulado)
    print(json.dumps(r, ensure_ascii=False, indent=1))
    sal = SALIDA / ("simulado" if a.simulado else "")
    sal.mkdir(parents=True, exist_ok=True)
    (sal / f"{a.parte}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
