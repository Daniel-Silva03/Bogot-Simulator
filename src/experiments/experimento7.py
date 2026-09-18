"""
src/experiments/experimento7.py

EXPERIMENTO 7 — Con ocho transiciones en vez de cuatro, ¿hay mecanismo?

Especificación pre-registrada: `claude/EXPERIMENT_7_SPECIFICATION.md`.

Los Experimentos 3 a 6 concluyeron que no hay mecanismo de dinámica de
opinión identificable, pero el veredicto descansaba en cuatro transiciones
de la ECP. Con cuatro puntos, "ningún mecanismo gana" y "no hay poder para
distinguir" son casi indistinguibles — y de hecho el Experimento 5, al
re-correrse con la población corregida (DI-M1), cambió de veredicto.

La EPC de Bogotá Cómo Vamos da ocho transiciones anuales y, además, dos
ítems contestados por la misma persona, lo que permite un segundo objetivo
limpio de estilo de respuesta.

DECISIONES DE IMPLEMENTACIÓN
----------------------------
DI-X1. **Pasos proporcionales al tiempo real.** La serie está espaciada de
    forma irregular (1-2-1-1-3-1-1-1 años en el objetivo A). S pasos por
    año; el tramo 2019->2022 lleva 3S. Con pasos iguales el reloj del
    modelo correría al triple de velocidad en ese tramo.

DI-X2. **Dos objetivos, y los dos se reportan.** A = la serie cruda de
    gestión del alcalde. B = la diferencia individual GG3_i - CC5_i, que
    elimina el estilo de respuesta individual además de cualquier efecto
    aditivo de periodo. Correr solo A y declarar veredicto sería repetir el
    error del Experimento 4 —ajustar un fenómeno y llamarlo *el* fenómeno—;
    correr solo B sería elegir el objetivo que más conviene después de
    haberlo visto.

DI-X3. **En el objetivo B la escala es -4 a +4 y está centrada en 0.**
    Cognición motivada usa `centro=0`; en el objetivo A, `centro=3`.
    Las columnas de cola (`cola_baja`, `cola_alta`) se calculan con los
    umbrales de la escala 1-5 y **no tienen sentido en el objetivo B**: se
    conservan por compatibilidad de formato y no se usan en el veredicto.

DI-X4. **El piso de ruido se calcula por objetivo y por año**, remuestreando
    la distribución observada. T4 compara los dos objetivos en unidades de
    su propio piso, porque sus escalas y sus amplitudes son distintas y
    compararlos en W1 crudo no diría nada.
"""

from __future__ import annotations

import itertools
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.experiments.experimento3 import (            # noqa: E402
    EstadoObservado, UMBRAL_COLA_ALTA, UMBRAL_COLA_BAJA,
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
from src.population.epc_bcv import (                                 # noqa: E402
    ITEM_DIFERENCIA, cargar_bcv, diferencia_individual,
)

ANIO_BASE = 2014
PASOS_POR_ANIO = [3, 8]
REDES = [("aleatoria", {}), ("homofilica", {}), ("territorial", {"h": 20})]
K_MEDIO = 5
N_SEMILLAS = 3
SEED_BASE = 20260917
N_MUESTRA_OBSERVADA = 200_000
PROPORCION_MINIMA = 0.05
TRAMOS_MINIMOS_PERFIL = 6          # T1: aciertos de signo exigidos de 8


@dataclass(frozen=True)
class Objetivo:
    clave: str
    item: str
    anios: tuple[int, ...]
    poblacion: str
    centro: float


OBJETIVOS = (
    Objetivo("A_gestion_alcalde", "gestion_alcalde",
             (2015, 2017, 2018, 2019, 2022, 2023, 2024, 2025),
             "poblacion_epc2014.csv", 3.0),
    Objetivo("B_diferencia", ITEM_DIFERENCIA,
             (2015, 2017, 2019, 2022, 2023, 2024, 2025),
             "poblacion_epc2014_dif.csv", 0.0),
)


# --------------------------------------------------------------------------
# Lo observado
# --------------------------------------------------------------------------

def _valores_y_pesos(anio: int, item: str, raiz_epc=None):
    ola = cargar_bcv(anio, raiz_epc)
    v = diferencia_individual(ola) if item == ITEM_DIFERENCIA else ola.datos[item]
    w = ola.datos["peso"]
    ok = v.notna() & w.notna() & (w > 0)
    return v[ok].to_numpy(float), w[ok].to_numpy(float), float(w[ok].sum() / w.sum())


def cargar_observado_epc(obj: Objetivo, raiz_epc=None, seed: int = 0):
    """EstadoObservado del objetivo, más la cobertura de cada año (DI-B1)."""
    rng = np.random.default_rng(seed)
    muestras, media, sd, cb, ca, cobertura = {}, {}, {}, {}, {}, {}
    for anio in (ANIO_BASE,) + obj.anios:
        v, w, cob = _valores_y_pesos(anio, obj.item, raiz_epc)
        p = w / w.sum()
        muestras[anio] = rng.choice(v, size=N_MUESTRA_OBSERVADA, p=p)
        m = float(np.average(v, weights=w))
        media[anio] = m
        sd[anio] = float(np.sqrt(np.average((v - m) ** 2, weights=w)))
        cb[anio] = float(np.average(v < UMBRAL_COLA_BAJA, weights=w))
        ca[anio] = float(np.average(v > UMBRAL_COLA_ALTA, weights=w))
        cobertura[anio] = cob
    return EstadoObservado(muestras, media, sd, cb, ca), cobertura


def piso_de_ruido(obj: Objetivo, n: int = 1000, reps: int = 200,
                  raiz_epc=None, seed: int = 0) -> dict[int, float]:
    """W1 entre dos muestras de n de la MISMA distribución observada (DI-X4)."""
    rng = np.random.default_rng(seed)
    salida = {}
    for anio in obj.anios:
        v, w, _ = _valores_y_pesos(anio, obj.item, raiz_epc)
        p = w / w.sum()
        salida[anio] = float(np.mean([
            wasserstein1(rng.choice(v, n, p=p), rng.choice(v, n, p=p)) for _ in range(reps)]))
    return salida


# --------------------------------------------------------------------------
# Malla
# --------------------------------------------------------------------------

def tramos(obj: Objetivo, pasos_por_anio: int) -> list[tuple[int, int]]:
    salida, previo = [], ANIO_BASE
    for anio in obj.anios:
        salida.append((anio, int(round(pasos_por_anio * (anio - previo)))))
        previo = anio
    return salida


def corrida_u_gamma(a0, obs: EstadoObservado, W, t: list[tuple[int, int]]) -> dict:
    """El baseline duro: gamma a la sd y u a la media, tramo por tramo."""
    fila: dict = {}
    estado = np.asarray(a0, dtype=np.float64).copy()
    w1_total = 0.0
    for anio, pasos in t:
        def avanzar_con_gamma(a, g, n, _W=W):
            m = ContraccionModel(_W, gamma=float(g))
            v = np.asarray(a, dtype=np.float64).copy()
            for _ in range(n):
                v = m.paso(v)
            return v
        gamma, estado, err_sd = ajustar_gamma_por_tramo(
            avanzar_con_gamma, estado, obs.sd[anio], pasos)
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


def _modelos(centro: float):
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
                       W, alpha=a, rho=rho, lam=lam, k=k, theta=0.0,
                       centro=centro, seed=s))(a, lam, k, rho),
                   False, {"alpha": a, "lam": lam, "k": k, "rho": rho}))
    return ms


def correr(obj: Objetivo, agentes: pd.DataFrame, obs: EstadoObservado,
           progreso: bool = True) -> pd.DataFrame:
    a0 = agentes["opinion_t0"].to_numpy(dtype=float)
    n = len(a0)
    modelos = _modelos(obj.centro)
    filas = []
    combos = list(itertools.product(REDES, range(N_SEMILLAS), PASOS_POR_ANIO))
    total = len(combos) * (len(modelos) + 1)
    hecho = 0

    for (tipo, kw), s, pasos in combos:
        semilla = SEED_BASE + 1000 * s
        red = crear_generador(tipo).generar(agentes, k_promedio=K_MEDIO, seed=semilla, **kw)
        t = tramos(obj, pasos)
        for etiqueta, familia, construir, lineal, params in modelos:
            fila = corrida(lambda W=red.W, n=n, s=semilla, c=construir: c(W, n, s),
                           a0, obs, pasos, lineal, None,
                           ajustador_no_lineal=ajustar_u_secante, tramos=t)
            fila.update(modelo=etiqueta, familia=familia, red=tipo, semilla=s,
                        pasos_por_anio=pasos, objetivo=obj.clave, **params)
            filas.append(fila)
            hecho += 1
        fila = corrida_u_gamma(a0, obs, red.W, t)
        fila.update(modelo="traslacion_u_gamma", familia="u_gamma", red=tipo, semilla=s,
                    pasos_por_anio=pasos, objetivo=obj.clave)
        filas.append(fila)
        hecho += 1
        if progreso:
            print(f"\r  {obj.clave}  {hecho}/{total}", end="", flush=True)
    if progreso:
        print()
    return pd.DataFrame(filas)


# --------------------------------------------------------------------------
# Veredicto
# --------------------------------------------------------------------------

def signos_observados(obj: Objetivo, obs: EstadoObservado) -> np.ndarray:
    prev = obs.sd[ANIO_BASE]
    out = []
    for a in obj.anios:
        out.append(np.sign(obs.sd[a] - prev))
        prev = obs.sd[a]
    return np.array(out)


def aciertos_de_perfil(res: pd.DataFrame, obj: Objetivo, obs: EstadoObservado) -> pd.Series:
    """Cuántos de los 8 tramos aciertan el SIGNO del cambio de dispersión (T1)."""
    sds = [res["sd_inicial"]] + [res[f"sd_{a}"] for a in obj.anios]
    signo_obs = signos_observados(obj, obs)
    aciertos = pd.Series(0, index=res.index)
    for i in range(len(obj.anios)):
        aciertos += (np.sign(sds[i + 1] - sds[i]) == signo_obs[i]).astype(int)
    return aciertos


def evaluar_objetivo(res: pd.DataFrame, obj: Objetivo, obs: EstadoObservado,
                     piso: dict[int, float], cobertura: dict[int, float]) -> dict:
    res = res.copy()
    res["aciertos_perfil"] = aciertos_de_perfil(res, obj, obs)
    base = res[res.familia == "u_gamma"]
    mecanismos = res[~res.familia.isin(("u_gamma", "traslacion"))]

    cols_m = [f"err_media_{a}" for a in obj.anios]
    cols_s = [f"err_sd_{a}" for a in obj.anios]
    piso_total = float(sum(piso.values()))

    por_familia = (mecanismos.aciertos_perfil >= TRAMOS_MINIMOS_PERFIL).groupby(
        mecanismos.familia).mean()

    return {
        "objetivo": obj.clave,
        "n_transiciones": len(obj.anios),
        "piso_de_ruido_total": round(piso_total, 4),
        "cobertura_por_anio": {a: round(cobertura[a], 3) for a in (ANIO_BASE,) + obj.anios},
        "T1_algun_mecanismo_reproduce_el_perfil": {
            "pasa": bool((por_familia >= PROPORCION_MINIMA).any()),
            "proporcion_por_familia": {k: round(float(v), 4) for k, v in por_familia.items()},
            "umbral_aciertos": TRAMOS_MINIMOS_PERFIL,
            "de_tramos": len(obj.anios),
            "mejor_aciertos_con_mecanismo": int(mecanismos.aciertos_perfil.max()),
            "signos_observados": [int(x) for x in signos_observados(obj, obs)],
        },
        "T2_el_baseline_acierta_media_y_sd": {
            "pasa": bool(base[cols_m].abs().max().max() < 1e-3
                         and base[cols_s].abs().max().max() < 1e-3),
            "max_error_media": float(base[cols_m].abs().max().max()),
            "max_error_sd": float(base[cols_s].abs().max().max()),
        },
        "T3_ningun_mecanismo_le_gana_al_baseline": {
            "pasa": bool(mecanismos.w1_total.min() >= base.w1_total.min()),
            "mejor_mecanismo": round(float(mecanismos.w1_total.min()), 4),
            "mejor_baseline_u_gamma": round(float(base.w1_total.min()), 4),
            "margen_pct": round(100 * (base.w1_total.min() - mecanismos.w1_total.min())
                                / base.w1_total.min(), 1),
            "mejor_modelo_con_mecanismo": str(
                mecanismos.loc[mecanismos.w1_total.idxmin(), "modelo"]),
            "veces_el_piso_mejor_mecanismo": round(
                float(mecanismos.w1_total.min() / piso_total), 2),
            "veces_el_piso_baseline": round(float(base.w1_total.min() / piso_total), 2),
        },
        "orden_de_merito": {
            k: round(float(v), 4)
            for k, v in res.groupby("familia").w1_total.min().sort_values().items()
        },
    }


def evaluar_conjunto(vers: dict, res_por_obj: dict) -> dict:
    """T4 y T5, que solo existen comparando los dos objetivos."""
    a, b = OBJETIVOS[0].clave, OBJETIVOS[1].clave
    va = vers[a]["T3_ningun_mecanismo_le_gana_al_baseline"]["veces_el_piso_mejor_mecanismo"]
    vb = vers[b]["T3_ningun_mecanismo_le_gana_al_baseline"]["veces_el_piso_mejor_mecanismo"]

    fa = res_por_obj[a].groupby("familia").w1_total.min()
    fb = res_por_obj[b].groupby("familia").w1_total.min()
    comunes = sorted(set(fa.index) & set(fb.index))
    rho = float(fa[comunes].rank().corr(fb[comunes].rank(), method="spearman"))

    return {
        "T4_el_objetivo_B_es_mas_dificil": {
            "pasa": bool(vb > va),
            "veces_el_piso_A": va,
            "veces_el_piso_B": vb,
        },
        "T5_el_orden_de_merito_coincide": {
            "pasa_prediccion_de_que_NO_coincide": bool(rho < 0.7),
            "spearman": round(rho, 3),
            "orden_A": list(fa.sort_values().index),
            "orden_B": list(fb.sort_values().index),
        },
    }


def main() -> int:
    raiz = Path(__file__).resolve().parents[2]
    salida = raiz / "data" / "processed" / "exp7"
    salida.mkdir(parents=True, exist_ok=True)

    vers, res_por_obj = {}, {}
    for obj in OBJETIVOS:
        agentes = pd.read_csv(raiz / "data" / "processed" / obj.poblacion)
        obs, cobertura = cargar_observado_epc(obj)
        piso = piso_de_ruido(obj, n=len(agentes))
        res = correr(obj, agentes, obs)
        res.to_csv(salida / f"resultados_{obj.clave}.csv", index=False)
        vers[obj.clave] = evaluar_objetivo(res, obj, obs, piso, cobertura)
        res_por_obj[obj.clave] = res

    vers["conjunto"] = evaluar_conjunto(vers, res_por_obj)
    with open(salida / "veredicto.json", "w", encoding="utf-8") as f:
        json.dump(vers, f, indent=2, ensure_ascii=False)
    print(json.dumps(vers, indent=2, ensure_ascii=False))
    for k, r in res_por_obj.items():
        print(f"\n== {k}: mejor y mediana por familia ==")
        print(r.groupby("familia")["w1_total"].agg(["min", "median", "size"])
              .sort_values("min").round(4).to_string())
    print(f"\nTodo en {salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
