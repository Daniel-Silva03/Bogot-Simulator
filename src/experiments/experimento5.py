"""
src/experiments/experimento5.py

EXPERIMENTO 5 — ¿Reproduce cognición motivada la contracción tardía?

Especificación pre-registrada: `claude/EXPERIMENT_5_SPECIFICATION.md`.

Mismo diseño que el Experimento 4 —u ajustado por periodo para que la media
simulada iguale exactamente la observada, y toda la evaluación sobre la
FORMA de la distribución— con la familia de Lorenz/Gestefeld añadida y las
referencias de aquel experimento corridas de nuevo en la misma malla.

DECISIONES DE IMPLEMENTACIÓN
----------------------------
DI-Z1. **Criterios corregidos.** El Experimento 4 declaró "pasa" un
    criterio que se cumplía en 1 de 3.960 corridas, y falló otro por
    medirle bimodalidad a distribuciones colapsadas. Aquí el perfil tardío
    exige **magnitud** (3 puntos porcentuales sobre cada tramo anterior) y
    **proporción** (5 % de las corridas), y la bimodalidad solo se evalúa
    con sd final >= 0,3.

DI-Z2. **u se ajusta por secante, no por bisección.** Cognición motivada
    no es lineal, así que el atajo del Experimento 4 no aplica. La secante
    llega a la misma u con ~10 evaluaciones en vez de ~50 (verificado:
    diferencia 2e-8, 6,3x más rápido), y cada evaluación es una simulación
    completa del tramo.

DI-Z3. **Se reportan mejor y mediana por familia.** Cognición motivada
    barre cinco parámetros; sus competidores, uno. Quedarse solo con el
    mejor de cada malla favorece mecánicamente al que tiene más. El
    criterio decisivo del pre-registro es cualitativo por esta razón.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.experiments.experimento3 import (            # noqa: E402
    ANIOS_OBJETIVO, EstadoObservado, cargar_observado,
)
from src.experiments.experimento4 import corrida       # noqa: E402
from src.network import crear_generador                # noqa: E402
from src.opinion import FriedkinJohnsenModel           # noqa: E402
from src.opinion.cognicion_motivada import CognicionMotivadaModel   # noqa: E402
from src.opinion.forzamiento import (                               # noqa: E402
    ContraccionModel, TraslacionModel, ajustar_u_secante,
)

# ------------------------------------------------------------------ malla
ALPHAS = [0.1, 0.3, 0.5]
LAMBDAS = [0.3, 0.5, 0.8]
KS = [2.0, 3.0, 6.0]
RHOS = [1.0, 1.1]
THETAS = [0.0, 0.02]

PASOS_POR_PERIODO = [5, 15]
REDES = [("aleatoria", {}), ("homofilica", {}), ("territorial", {"h": 20})]
K_MEDIO = 5                      # D15: el valor medido
N_SEMILLAS = 3
SEED_BASE = 20260916

UMBRAL_PERFIL_TARDIO = 0.03      # DI-Z1: 3 puntos porcentuales
PROPORCION_MINIMA = 0.05         # DI-Z1: 5 % de las corridas
SD_MINIMA_BIMODALIDAD = 0.30     # DI-Z1
UMBRAL_SARLE = 0.555


def _modelos():
    """(etiqueta, familia, constructor(W, n, seed), ¿lineal?, params)."""
    ms = []
    for a, lam, k, rho, th in itertools.product(ALPHAS, LAMBDAS, KS, RHOS, THETAS):
        ms.append((
            f"cm_a{a}_l{lam}_k{k}_r{rho}_t{th}", "cognicion_motivada",
            (lambda a, lam, k, rho, th: lambda W, n, s: CognicionMotivadaModel(
                W, alpha=a, rho=rho, lam=lam, k=k, theta=th, seed=s))(a, lam, k, rho, th),
            False, {"alpha": a, "lam": lam, "k": k, "rho": rho, "theta": th}))
    ms.append(("traslacion", "traslacion", lambda W, n, s: TraslacionModel(W), True, {}))
    for g in (0.02, 0.05):
        ms.append((f"contraccion_g{g}", "contraccion",
                   (lambda g: lambda W, n, s: ContraccionModel(W, gamma=g))(g), True, {"gamma": g}))
    for p in (0.08, 0.1):
        ms.append((f"fj_phi{p}", "friedkin_johnsen",
                   (lambda p: lambda W, n, s: FriedkinJohnsenModel(W, phi=p))(p), True, {"phi": p}))
    return ms


def correr(agentes: pd.DataFrame, obs: EstadoObservado, progreso: bool = True) -> pd.DataFrame:
    a0 = agentes["opinion_t0"].to_numpy(dtype=float)
    n = len(a0)
    modelos = _modelos()
    filas = []
    combos = list(itertools.product(REDES, range(N_SEMILLAS), PASOS_POR_PERIODO))
    total = len(combos) * len(modelos)
    hecho = 0

    for (tipo, kw), s, pasos in combos:
        semilla = SEED_BASE + 1000 * s
        red = crear_generador(tipo).generar(agentes, k_promedio=K_MEDIO, seed=semilla, **kw)
        for etiqueta, familia, construir, lineal, params in modelos:
            fila = corrida(lambda W=red.W, n=n, s=semilla, c=construir: c(W, n, s),
                           a0, obs, pasos, lineal, None,
                           ajustador_no_lineal=ajustar_u_secante)    # DI-Z2
            fila.update(modelo=etiqueta, familia=familia, red=tipo, semilla=s,
                        pasos_por_periodo=pasos, **params)
            filas.append(fila)
            hecho += 1
        if progreso:
            print(f"\r  {hecho}/{total}", end="", flush=True)
    if progreso:
        print()
    return pd.DataFrame(filas)


# ------------------------------------------------------------------ veredicto

def perfil_contraccion(res: pd.DataFrame) -> pd.DataFrame:
    """Contracción de sd por tramo, y si el tercero domina (DI-Z1)."""
    s0 = res["sd_inicial"]
    s = [res[f"sd_{a}"] for a in ANIOS_OBJETIVO]
    t1, t2, t3 = 1 - s[0] / s0, 1 - s[1] / s[0], 1 - s[2] / s[1]
    return pd.DataFrame({
        "tramo1": t1, "tramo2": t2, "tramo3": t3,
        "tardio": (t3 > t1 + UMBRAL_PERFIL_TARDIO) & (t3 > t2 + UMBRAL_PERFIL_TARDIO),
    })


def evaluar(res: pd.DataFrame, obs: EstadoObservado) -> dict:
    # Se recalcula el perfil en vez de asumir que viene puesto: `evaluar`
    # tiene que poder llamarse sobre un CSV recién leído.
    res = res.drop(columns=["tramo1", "tramo2", "tramo3", "tardio"], errors="ignore")
    res = res.join(perfil_contraccion(res))
    cm = res[res.familia == "cognicion_motivada"]
    fj = res[res.familia == "friedkin_johnsen"]
    con = res[res.familia == "contraccion"]

    cols_sd = [f"err_sd_{a}" for a in ANIOS_OBJETIVO]
    cols_bim = [f"bimodalidad_{a}" for a in ANIOS_OBJETIVO]
    evaluables = cm[cm[f"sd_{ANIOS_OBJETIVO[-1]}"] >= SD_MINIMA_BIMODALIDAD]
    mejores5 = cm.nsmallest(5, "w1_total")

    obs_perfil = [1 - obs.sd[2019] / obs.sd[2017],
                  1 - obs.sd[2021] / obs.sd[2019],
                  1 - obs.sd[2023] / obs.sd[2021]]

    return {
        "R1_gana_a_friedkin_johnsen": {
            "pasa": bool(cm.w1_total.min() < fj.w1_total.min()),
            "mejor_cognicion_motivada": round(float(cm.w1_total.min()), 4),
            "mejor_friedkin_johnsen": round(float(fj.w1_total.min()), 4),
            "mediana_cognicion_motivada": round(float(cm.w1_total.median()), 4),
            "mediana_friedkin_johnsen": round(float(fj.w1_total.median()), 4),
        },
        "R2_contraccion_tardia": {
            "pasa": bool(cm.tardio.mean() >= PROPORCION_MINIMA),
            "proporcion_corridas_tardias": round(float(cm.tardio.mean()), 4),
            "umbral_proporcion": PROPORCION_MINIMA,
            "corridas_tardias": int(cm.tardio.sum()), "corridas": int(len(cm)),
            "tardias_en_friedkin_johnsen": int(fj.tardio.sum()),
            "tardias_en_contraccion": int(con.tardio.sum()),
            "perfil_observado": [round(x, 4) for x in obs_perfil],
        },
        "R3_gana_al_control_sin_red": {
            "pasa": bool(cm.w1_total.min() < con.w1_total.min()),
            "mejor_cognicion_motivada": round(float(cm.w1_total.min()), 4),
            "mejor_contraccion_sin_red": round(float(con.w1_total.min()), 4),
            "margen_pct": round(100 * (con.w1_total.min() - cm.w1_total.min())
                                / con.w1_total.min(), 1),
        },
        "R4_bimodalidad": {
            "pasa_en_las_mejores": bool(mejores5[cols_bim].max().max() < UMBRAL_SARLE),
            "bimodalidad_max_en_las_5_mejores": round(float(mejores5[cols_bim].max().max()), 4),
            "pct_malla_evaluable_que_fragmenta": round(100 * float(
                (evaluables[cols_bim].max(axis=1) > UMBRAL_SARLE).mean()), 1),
            "corridas_evaluables": int(len(evaluables)), "corridas": int(len(cm)),
        },
        "R5_error_de_dispersion": {
            "pasa": bool(cm[cols_sd].abs().max(axis=1).min() < 0.0453),
            "mejor_error_sd": round(float(cm[cols_sd].abs().max(axis=1).min()), 4),
            "referencia_experimento_4": 0.0453,
        },
    }


def main() -> int:
    raiz = Path(__file__).resolve().parents[2]
    agentes = pd.read_csv(raiz / "data" / "processed" / "poblacion_ecp2017.csv")
    obs = cargar_observado(raiz / "data" / "raw" / "ecp")
    res = correr(agentes, obs)
    res = res.join(perfil_contraccion(res))

    salida = raiz / "data" / "processed" / "exp5"
    salida.mkdir(parents=True, exist_ok=True)
    res.to_csv(salida / "resultados.csv", index=False)
    ver = evaluar(res, obs)
    with open(salida / "veredicto.json", "w", encoding="utf-8") as f:
        json.dump(ver, f, indent=2, ensure_ascii=False)
    print(json.dumps(ver, indent=2, ensure_ascii=False))
    print("\n== Mejor y mediana por familia ==")
    print(res.groupby("familia")["w1_total"].agg(["min", "median", "size"])
          .sort_values("min").round(4).to_string())
    print(f"\nTodo en {salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
