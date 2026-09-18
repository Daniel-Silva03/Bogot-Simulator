"""
src/experiments/experimento6.py

EXPERIMENTO 6 — Con la serie desde 2013, ¿algún mecanismo produce la joroba
de dispersión, o también hay que ponerla a mano?

Especificación pre-registrada: `claude/EXPERIMENT_6_SPECIFICATION.md`.

Los Experimentos 4 y 5 arrancaban en 2017 y trataban la contracción de sd
como el fenómeno. Con 2013 adentro se ve que 2017 era **la cima de una
joroba**: sd 0,754 -> 0,934 -> 0,764. Ningún modelo capaz solo de contraer
puede producir la subida.

DECISIONES DE IMPLEMENTACIÓN
----------------------------
DI-W1. **Los tramos duran distinto.** La serie queda espaciada 4-2-2-2
    años. Los pasos son proporcionales al tiempo real (S por cada 2 años,
    2S en el primer tramo); con pasos iguales el reloj del modelo correría
    al doble de velocidad entre 2013 y 2017.

DI-W2. **Entra `traslacion+u+gamma`, el baseline duro.** Un escalar de
    nivel y otro de dispersión por periodo, ambos ajustados a lo observado.
    Acierta los dos primeros momentos por construcción y no tiene ninguna
    dinámica social. Como la contracción hacia la media conserva la media
    exactamente, los dos ajustes son independientes: gamma primero (fija la
    sd), u después (fija la media sin tocar la sd).

DI-W3. Cognición motivada entra con **rho = 0,9** además de 1,0 y 1,1. Es
    el régimen de refuerzo, el único de esa familia que expande la
    dispersión, y sin él la familia no tendría ninguna chance de producir
    el primer tramo.
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
    EstadoObservado, UMBRAL_COLA_ALTA, UMBRAL_COLA_BAJA, cargar_observado,
)
from src.experiments.experimento4 import _avanzar_factory, corrida   # noqa: E402
from src.experiments.metrics import bimodalidad_sarle, wasserstein1  # noqa: E402
from src.network import crear_generador                             # noqa: E402
from src.opinion import FriedkinJohnsenModel                        # noqa: E402
from src.opinion.cognicion_motivada import CognicionMotivadaModel    # noqa: E402
from src.opinion.forzamiento import (                                # noqa: E402
    ContraccionModel, TraslacionModel, ajustar_gamma_por_tramo,
    ajustar_u_lineal, ajustar_u_secante,
)

ANIO_BASE = 2013
ANIOS = (2017, 2019, 2021, 2023)
ANIOS_TODOS = (ANIO_BASE,) + ANIOS
PASOS_POR_BIENIO = [5, 15]
REDES = [("aleatoria", {}), ("homofilica", {}), ("territorial", {"h": 20})]
K_MEDIO = 5
N_SEMILLAS = 3
SEED_BASE = 20260916
PROPORCION_MINIMA = 0.05


def tramos(pasos_por_bienio: int) -> list[tuple[int, int]]:
    """[(año, pasos), ...] con pasos proporcionales al tiempo real (DI-W1)."""
    salida, previo = [], ANIO_BASE
    for anio in ANIOS:
        salida.append((anio, int(round(pasos_por_bienio * (anio - previo) / 2))))
        previo = anio
    return salida


# --------------------------------------------------------------------------
# El baseline duro: dos números exógenos por periodo (DI-W2)
# --------------------------------------------------------------------------

def corrida_u_gamma(a0: np.ndarray, obs: EstadoObservado, W: np.ndarray,
                    pasos_por_bienio: int) -> dict:
    """Ajusta gamma a la sd y u a la media, tramo por tramo. Sin mecanismo."""
    fila: dict = {}
    estado = np.asarray(a0, dtype=np.float64).copy()
    w1_total = 0.0

    for anio, pasos in tramos(pasos_por_bienio):
        def avanzar_con_gamma(a, g, n, _W=W):
            m = ContraccionModel(_W, gamma=float(g))
            v = np.asarray(a, dtype=np.float64).copy()
            for _ in range(n):
                v = m.paso(v)
            return v

        gamma, estado, err_sd = ajustar_gamma_por_tramo(
            avanzar_con_gamma, estado, obs.sd[anio], pasos)
        # La contracción conserva la media, así que u se ajusta después sin
        # deshacer lo anterior: una traslación pura no toca la sd.
        avanzar_u = _avanzar_factory(lambda: TraslacionModel(W), None)
        u, estado, err_media = ajustar_u_lineal(avanzar_u, estado, obs.media[anio], pasos)

        w1 = wasserstein1(estado, obs.muestras[anio])
        w1_total += w1
        fila.update({
            f"gamma_{anio}": round(float(gamma), 8), f"u_{anio}": round(float(u), 8),
            f"err_media_{anio}": float(err_media), f"err_sd_{anio}": float(err_sd),
            f"w1_{anio}": float(w1), f"sd_{anio}": float(estado.std()),
            f"cola_baja_{anio}": float((estado < UMBRAL_COLA_BAJA).mean()),
            f"cola_alta_{anio}": float((estado > UMBRAL_COLA_ALTA).mean()),
            f"bimodalidad_{anio}": float(bimodalidad_sarle(estado)),
        })
    fila["w1_total"] = float(w1_total)
    fila["sd_inicial"] = float(np.asarray(a0).std())
    return fila


# --------------------------------------------------------------------------
# Malla
# --------------------------------------------------------------------------

def _modelos():
    ms = [("traslacion", "traslacion", lambda W, n, s: TraslacionModel(W), True, {})]
    for g in (0.02, 0.05, -0.02, -0.05):
        ms.append((f"contraccion_g{g}", "contraccion",
                   (lambda g: lambda W, n, s: ContraccionModel(W, gamma=g))(g), True, {"gamma": g}))
    for p in (0.08, 0.1, 0.2, 0.3):
        ms.append((f"fj_phi{p}", "friedkin_johnsen",
                   (lambda p: lambda W, n, s: FriedkinJohnsenModel(W, phi=p))(p), True, {"phi": p}))
    for a, lam, k, rho in itertools.product((0.1, 0.3), (0.3, 0.5), (2.0, 3.0), (0.9, 1.0, 1.1)):
        ms.append((f"cm_a{a}_l{lam}_k{k}_r{rho}", "cognicion_motivada",
                   (lambda a, lam, k, rho: lambda W, n, s: CognicionMotivadaModel(
                       W, alpha=a, rho=rho, lam=lam, k=k, theta=0.0, seed=s))(a, lam, k, rho),
                   False, {"alpha": a, "lam": lam, "k": k, "rho": rho}))
    return ms


def correr(agentes: pd.DataFrame, obs: EstadoObservado, progreso: bool = True) -> pd.DataFrame:
    a0 = agentes["opinion_t0"].to_numpy(dtype=float)
    n = len(a0)
    modelos = _modelos()
    filas = []
    combos = list(itertools.product(REDES, range(N_SEMILLAS), PASOS_POR_BIENIO))
    total = len(combos) * (len(modelos) + 1)
    hecho = 0

    for (tipo, kw), s, pasos in combos:
        semilla = SEED_BASE + 1000 * s
        red = crear_generador(tipo).generar(agentes, k_promedio=K_MEDIO, seed=semilla, **kw)
        t = tramos(pasos)
        for etiqueta, familia, construir, lineal, params in modelos:
            fila = corrida(lambda W=red.W, n=n, s=semilla, c=construir: c(W, n, s),
                           a0, obs, pasos, lineal, None,
                           ajustador_no_lineal=ajustar_u_secante, tramos=t)
            fila.update(modelo=etiqueta, familia=familia, red=tipo, semilla=s,
                        pasos_por_bienio=pasos, **params)
            filas.append(fila)
            hecho += 1
        fila = corrida_u_gamma(a0, obs, red.W, pasos)
        fila.update(modelo="traslacion_u_gamma", familia="u_gamma", red=tipo, semilla=s,
                    pasos_por_bienio=pasos)
        filas.append(fila)
        hecho += 1
        if progreso:
            print(f"\r  {hecho}/{total}", end="", flush=True)
    if progreso:
        print()
    return pd.DataFrame(filas)


# --------------------------------------------------------------------------
# Veredicto
# --------------------------------------------------------------------------

def perfil(res: pd.DataFrame) -> pd.DataFrame:
    """Variación de sd por tramo y si hay joroba (sube primero, baja al final)."""
    sds = [res["sd_inicial"]] + [res[f"sd_{a}"] for a in ANIOS]
    cols = {f"var_sd_{ANIOS[i]}": sds[i + 1] / sds[i] - 1 for i in range(len(ANIOS))}
    t = pd.DataFrame(cols)
    t["joroba"] = (t[f"var_sd_{ANIOS[0]}"] > 0) & (t[f"var_sd_{ANIOS[-1]}"] < 0)
    return t


def evaluar(res: pd.DataFrame, obs: EstadoObservado) -> dict:
    res = res.drop(columns=[c for c in res.columns if c.startswith("var_sd_")]
                   + ["joroba"], errors="ignore").join(perfil(res))
    base = res[res.familia == "u_gamma"]
    mecanismos = res[~res.familia.isin(("u_gamma", "traslacion"))]
    solo_u = res[res.familia != "u_gamma"]

    cols_m = [f"err_media_{a}" for a in ANIOS]
    cols_s = [f"err_sd_{a}" for a in ANIOS]
    obs_var = [obs.sd[ANIOS[0]] / obs.sd[ANIO_BASE] - 1] + [
        obs.sd[ANIOS[i]] / obs.sd[ANIOS[i - 1]] - 1 for i in range(1, len(ANIOS))]

    por_familia = mecanismos.groupby("familia").joroba.mean()
    gammas = base[[f"gamma_{a}" for a in ANIOS]].median()

    return {
        "S1_algun_mecanismo_hace_la_joroba": {
            "pasa": bool((por_familia >= PROPORCION_MINIMA).any()),
            "proporcion_por_familia": {k: round(float(v), 4) for k, v in por_familia.items()},
            "umbral": PROPORCION_MINIMA,
            "variacion_sd_observada": [round(x, 4) for x in obs_var],
        },
        "S2_el_baseline_acierta_media_y_sd": {
            "pasa": bool(base[cols_m].abs().max().max() < 1e-3
                         and base[cols_s].abs().max().max() < 1e-3),
            "max_error_media": float(base[cols_m].abs().max().max()),
            "max_error_sd": float(base[cols_s].abs().max().max()),
        },
        "S3_los_de_solo_u_ajustan_peor_que_en_exp4": {
            "pasa": bool(solo_u.w1_total.min() / len(ANIOS) > 0.2650 / 3),
            "mejor_w1_por_anio": round(float(solo_u.w1_total.min() / len(ANIOS)), 4),
            "referencia_exp4_por_anio": round(0.2650 / 3, 4),
        },
        "S4_gamma_negativo_primero_positivo_despues": {
            "pasa": bool(gammas.iloc[0] < 0 and (gammas.iloc[1:] > 0).all()),
            "gamma_mediano_por_tramo": {a: round(float(gammas[f"gamma_{a}"]), 5) for a in ANIOS},
        },
        "S5_ningun_mecanismo_le_gana_al_baseline": {
            "pasa": bool(mecanismos.w1_total.min() >= base.w1_total.min()),
            "mejor_mecanismo": round(float(mecanismos.w1_total.min()), 4),
            "mejor_baseline_u_gamma": round(float(base.w1_total.min()), 4),
            "margen_pct": round(100 * (base.w1_total.min() - mecanismos.w1_total.min())
                                / base.w1_total.min(), 1),
            "mejor_modelo_con_mecanismo": str(
                mecanismos.loc[mecanismos.w1_total.idxmin(), "modelo"]),
        },
    }


def main() -> int:
    raiz = Path(__file__).resolve().parents[2]
    agentes = pd.read_csv(raiz / "data" / "processed" / "poblacion_ecp2013.csv")
    obs = cargar_observado(raiz / "data" / "raw" / "ecp", anios=ANIOS_TODOS)
    res = correr(agentes, obs)
    res = res.join(perfil(res))

    salida = raiz / "data" / "processed" / "exp6"
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
