"""
src/experiments/experimento4.py

EXPERIMENTO 4 — ¿Aporta algo el mecanismo social cuando el nivel ya está
explicado por un forzamiento exógeno?

Especificación pre-registrada: `claude/EXPERIMENT_4_SPECIFICATION.md`.

EL DISEÑO, EN UNA FRASE
-----------------------
Se ajusta un escalar u por periodo para que la media simulada **iguale
exactamente** la media observada de la ECP en 2019, 2021 y 2023. El nivel
deja de estar en disputa. Lo único que queda por explicar es la **forma**
de la distribución — dispersión, colas, bimodalidad — y eso el forzamiento
no lo puede tocar, porque es una traslación en bloque.

Así, el baseline `traslacion+u` es el más exigente que ha tenido este
proyecto: acierta el nivel por construcción y **conserva la desviación
estándar exactamente**. Todo lo que un modelo con mecanismo social gane
sobre él es atribuible al mecanismo y a nada más.

Es la respuesta al diagnóstico de `claude/DIAGNOSTICO_Y_ALTERNATIVAS.md`
§1: el Experimento 3 le pidió a Friedkin-Johnsen un movimiento de nivel
que no podía producir, y contó cuatro veces la misma ausencia.

DECISIONES DE IMPLEMENTACIÓN
----------------------------
DI-Y1. **El mapeo temporal se fija, no se busca.** El Experimento 3
    elegía los checkpoints que mejor le venían a cada corrida
    (`mejor_mapeo_temporal`), lo que era defendible entonces —el modelo no
    tenía escala de tiempo propia— pero aquí sería hacer trampa: con u
    ajustado por tramo, elegir además dónde termina cada tramo daría dos
    grados de libertad para el mismo dato. Se fija S pasos por periodo,
    iguales para los tres, y S se barre como parámetro. Es lo que hacen
    Gestefeld & Lorenz con su "número de pasos por periodo real".

DI-Y2. **u se ajusta de forma secuencial, no conjunta.** u₁ lleva de 2017
    a 2019, y el estado resultante —no la observación de 2019— es el
    punto de partida del tramo siguiente. Reiniciar cada tramo desde lo
    observado escondería el error acumulado, que es justamente lo que se
    quiere medir.

DI-Y3. **Tres parámetros ajustados, no más.** u₁, u₂, u₃ contra tres
    medias objetivo: el ajuste del nivel es exacto y sin holgura, así que
    no hay grados de libertad sobrantes que puedan derramarse sobre la
    forma. φ y S no se ajustan a los datos: se barren y se reporta el
    rango completo.

DI-Y4. **El recorte a la escala 1–5 es una variante, no el comportamiento
    base** (ver DI-F2 en `src/opinion/forzamiento.py`). Recortar contra un
    tope comprime la distribución por sí solo, y podría producir la
    contracción de dispersión observada sin ningún mecanismo social. Se
    corre aparte y se reporta aparte, precisamente para poder distinguir
    una cosa de la otra.

DI-Y5. El ruido usa escala fija (0,01 por paso) en vez de calibrarse al
    recorrido observado como en el Experimento 3. Aquí el recorrido lo
    pone u, así que calibrar la escala del ruido contra él sería
    contarlo dos veces.
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.experiments.experimento3 import (            # noqa: E402
    ANIO_BASE, ANIOS_OBJETIVO, EstadoObservado, UMBRAL_COLA_ALTA, UMBRAL_COLA_BAJA,
    cargar_observado,
)
from src.experiments.metrics import bimodalidad_sarle, ks, wasserstein1   # noqa: E402
from src.network import crear_generador                                   # noqa: E402
from src.opinion import DeGrootModel, FriedkinJohnsenModel                 # noqa: E402
from src.opinion.forzamiento import (                                      # noqa: E402
    ContraccionModel, ModeloForzado, RuidoModel, TraslacionModel, ajustar_u_lineal,
    ajustar_u_por_tramo, phi_heterogeneo,
)

# --------------------------------------------------------------------------
# Barrido
# --------------------------------------------------------------------------

# Incluye 1 y 2 a propósito: la prueba de humo mostró que Friedkin-Johnsen
# se contrae de más ya con 5 pasos por periodo, y un barrido que no llegue
# a la región donde el mecanismo es suave estaría condenando al modelo por
# no poder alcanzarla. Ver §3 de la especificación.
PASOS_POR_PERIODO = [1, 2, 5, 15, 40]       # DI-Y1
REDES = [("aleatoria", {}), ("homofilica", {}), ("territorial", {"h": 20})]
K_MEDIOS = [4, 5, 8]                        # D15
LIMITES_ESCALA = (1.0, 5.0)                 # DI-Y4
ESCALA_RUIDO = 0.01                         # DI-Y5

# (etiqueta, constructor(W, n, seed) -> OpinionModel, ¿es lineal?)
def _modelos_base():
    return [
        ("traslacion",      lambda W, n, s: TraslacionModel(W),                     True),
        # Controles post-hoc, añadidos tras ver los resultados (ver §6 de
        # EXPERIMENT_4_RESULTS.md). Son baselines más exigentes, no candidatos.
        ("contraccion_g0.05", lambda W, n, s: ContraccionModel(W, gamma=0.05),       True),
        ("contraccion_g0.10", lambda W, n, s: ContraccionModel(W, gamma=0.10),       True),
        ("contraccion_g0.20", lambda W, n, s: ContraccionModel(W, gamma=0.20),       True),
        ("fj_phi0.1",       lambda W, n, s: FriedkinJohnsenModel(W, phi=0.1),       True),
        ("fj_phi0.2",       lambda W, n, s: FriedkinJohnsenModel(W, phi=0.2),       True),
        ("fj_phi0.3",       lambda W, n, s: FriedkinJohnsenModel(W, phi=0.3),       True),
        ("fj_phi0.5",       lambda W, n, s: FriedkinJohnsenModel(W, phi=0.5),       True),
        ("fj_phi0.7",       lambda W, n, s: FriedkinJohnsenModel(W, phi=0.7),       True),
        ("fj_phi0.9",       lambda W, n, s: FriedkinJohnsenModel(W, phi=0.9),       True),
        ("fj_het_m0.5_d0.3", lambda W, n, s: FriedkinJohnsenModel(
            W, phi=phi_heterogeneo(n, 0.5, 0.3, seed=s)),                           True),
        ("fj_het_m0.5_d0.6", lambda W, n, s: FriedkinJohnsenModel(
            W, phi=phi_heterogeneo(n, 0.5, 0.6, seed=s)),                           True),
        ("fj_het_m0.7_d0.6", lambda W, n, s: FriedkinJohnsenModel(
            W, phi=phi_heterogeneo(n, 0.7, 0.6, seed=s)),                           True),
        ("degroot",         lambda W, n, s: DeGrootModel(W),                        True),
        ("ruido",           lambda W, n, s: RuidoModel(W, escala=ESCALA_RUIDO, seed=s), True),
    ]

# Con recorte solo estos dos: el baseline y el candidato central (DI-Y4).
MODELOS_CON_RECORTE = {"traslacion", "fj_phi0.5"}


# --------------------------------------------------------------------------
# Una corrida
# --------------------------------------------------------------------------

def _avanzar_factory(construir, limites):
    """Devuelve `avanzar(a, u, n)` -> estado tras n pasos con forzamiento u.

    Reconstruye el modelo base en cada llamada a propósito: el ajuste de u
    evalúa la misma trayectoria muchas veces, y un modelo con estado
    interno (el reloj del forzamiento, el anclaje de Friedkin-Johnsen, el
    generador del ruido) tiene que empezar de cero cada vez o las
    evaluaciones no serían comparables entre sí.
    """
    def avanzar(a, u, n):
        m = ModeloForzado(construir(), np.full(max(n, 1), float(u)), limites=limites)
        m.preparar(a)
        v = np.asarray(a, dtype=np.float64).copy()
        for _ in range(n):
            v = m.paso(v)
        return v
    return avanzar


def corrida(
    construir,
    a0: np.ndarray,
    obs: EstadoObservado,
    pasos: int,
    lineal: bool,
    limites: Optional[tuple[float, float]] = None,
    ajustador_no_lineal=None,
    tramos: Optional[list] = None,
) -> dict:
    """Ajusta u por tramo y mide la forma resultante en cada año objetivo.

    `ajustador_no_lineal` permite cambiar el buscador de u para los modelos
    que no son lineales. Por defecto es la bisección, que es lo que corrió
    el Experimento 4 y no se toca para no alterar sus resultados; el
    Experimento 5 le pasa la secante, que llega al mismo valor en una
    quinta parte de las evaluaciones (DI-Z2).
    """
    avanzar = _avanzar_factory(construir, limites)
    no_lineal = ajustador_no_lineal or ajustar_u_por_tramo
    ajustar = ajustar_u_lineal if (lineal and limites is None) else no_lineal
    # `tramos` = [(año, pasos), ...]. Permite periodos de distinta duración:
    # la serie que empieza en 2013 está espaciada 4-2-2-2 años, y darle a
    # todos los tramos los mismos pasos haría correr el reloj del modelo al
    # doble de velocidad en el primero (DI-W1 del Experimento 6).
    tramos = tramos or [(a, pasos) for a in ANIOS_OBJETIVO]

    fila: dict = {}
    estado = np.asarray(a0, dtype=np.float64).copy()
    w1_total = 0.0
    us = []

    for anio, pasos_tramo in tramos:
        u, estado, err = ajustar(avanzar, estado, obs.media[anio], pasos_tramo)
        us.append(u)
        w1 = wasserstein1(estado, obs.muestras[anio])
        w1_total += w1
        fila[f"u_{anio}"] = round(float(u), 8)
        fila[f"err_media_{anio}"] = float(err)
        fila[f"w1_{anio}"] = float(w1)
        fila[f"ks_{anio}"] = float(ks(estado, obs.muestras[anio]))
        fila[f"sd_{anio}"] = float(estado.std())
        fila[f"err_sd_{anio}"] = float(estado.std() - obs.sd[anio])
        fila[f"cola_baja_{anio}"] = float((estado < UMBRAL_COLA_BAJA).mean())
        fila[f"cola_alta_{anio}"] = float((estado > UMBRAL_COLA_ALTA).mean())
        fila[f"bimodalidad_{anio}"] = float(bimodalidad_sarle(estado))

    fila["w1_total"] = float(w1_total)
    fila["u_cambia_de_signo"] = bool(min(us) < 0 < max(us))
    fila["sd_inicial"] = float(np.asarray(a0).std())
    return fila


# --------------------------------------------------------------------------
# Barrido completo
# --------------------------------------------------------------------------

def correr(
    agentes: pd.DataFrame,
    obs: EstadoObservado,
    n_semillas: int = 8,
    seed_base: int = 20260916,
    redes: list = REDES,
    k_medios: list = K_MEDIOS,
    pasos_por_periodo: Iterable[int] = PASOS_POR_PERIODO,
    progreso: bool = True,
) -> pd.DataFrame:
    a0 = agentes["opinion_t0"].to_numpy(dtype=float)
    n = len(a0)
    modelos = _modelos_base()
    filas = []

    combos = list(itertools.product(redes, k_medios, range(n_semillas)))
    total = len(combos) * len(list(pasos_por_periodo)) * (
        len(modelos) + len(MODELOS_CON_RECORTE))
    hecho = 0

    for (tipo, kw_red), k, s in combos:
        semilla = seed_base + 1000 * s
        red = crear_generador(tipo).generar(agentes, k_promedio=k, seed=semilla, **kw_red)
        for pasos in pasos_por_periodo:
            for etiqueta, construir, lineal in modelos:
                variantes = [(None, "no")]
                if etiqueta in MODELOS_CON_RECORTE:
                    variantes.append((LIMITES_ESCALA, "si"))
                for limites, recorte in variantes:
                    fila = corrida(
                        lambda W=red.W, n=n, s=semilla, c=construir: c(W, n, s),
                        a0, obs, pasos, lineal, limites)
                    fila.update(red=tipo, k_medio=k, semilla=s, modelo=etiqueta,
                                pasos_por_periodo=pasos, recorte=recorte)
                    filas.append(fila)
                    hecho += 1
            if progreso:
                print(f"\r  {hecho}/{total}", end="", flush=True)
    if progreso:
        print()
    return pd.DataFrame(filas)


# --------------------------------------------------------------------------
# Veredictos
# --------------------------------------------------------------------------

def evaluar(res: pd.DataFrame, obs: EstadoObservado, umbral_sd: float = 0.05) -> dict:
    """Aplica los criterios pre-registrados de EXPERIMENT_4_SPECIFICATION.md."""
    sin_recorte = res[res.recorte == "no"]
    mecanismo = sin_recorte[sin_recorte.modelo != "traslacion"]
    nulo = sin_recorte[sin_recorte.modelo == "traslacion"]

    cols_sd = [f"err_sd_{a}" for a in ANIOS_OBJETIVO]
    err_sd_mec = mecanismo[cols_sd].abs().max(axis=1)
    err_sd_nulo = nulo[cols_sd].abs().max(axis=1)

    mejor_mec = float(mecanismo["w1_total"].min())
    mejor_nulo = float(nulo["w1_total"].min())

    # Perfil de contracción observado: tardío (-3,3 % / -0,7 % / -14,8 %)
    def perfil(row) -> tuple[float, float, float]:
        s0 = row["sd_inicial"]
        s = [row[f"sd_{a}"] for a in ANIOS_OBJETIVO]
        return (1 - s[0] / s0, 1 - s[1] / s[0], 1 - s[2] / s[1])

    obs_perfil = (1 - obs.sd[2019] / obs.sd[ANIO_BASE],
                  1 - obs.sd[2021] / obs.sd[2019],
                  1 - obs.sd[2023] / obs.sd[2021])
    p = mecanismo.apply(perfil, axis=1, result_type="expand")
    # "tardío" = la contracción del último tramo es la mayor de las tres
    tardio = (p[2] > p[0]) & (p[2] > p[1])

    return {
        "Q1_mecanismo_gana_al_nulo": {
            "pasa": mejor_mec < mejor_nulo,
            "mejor_w1_con_mecanismo": round(mejor_mec, 4),
            "mejor_w1_traslacion_pura": round(mejor_nulo, 4),
            "mejora_relativa_pct": round(100 * (mejor_nulo - mejor_mec) / mejor_nulo, 1),
        },
        "Q2_dispersion": {
            "pasa": bool(err_sd_mec.min() < umbral_sd),
            "mejor_error_sd_con_mecanismo": round(float(err_sd_mec.min()), 4),
            "mejor_error_sd_traslacion": round(float(err_sd_nulo.min()), 4),
            "umbral": umbral_sd,
        },
        "Q3_perfil_de_contraccion_tardio": {
            "pasa": bool(tardio.any()),
            "corridas_con_perfil_tardio": int(tardio.sum()),
            "corridas_totales": int(len(tardio)),
            "perfil_observado": [round(x, 4) for x in obs_perfil],
        },
        "Q4_bimodalidad": {
            "pasa": bool((sin_recorte[[f"bimodalidad_{a}" for a in ANIOS_OBJETIVO]]
                          .max().max()) < 0.555),
            "bimodalidad_max_simulada": round(float(
                sin_recorte[[f"bimodalidad_{a}" for a in ANIOS_OBJETIVO]].max().max()), 4),
        },
        "Q5_recorte_explica_la_contraccion": {
            "nota": "descriptivo, no pasa/falla — ver DI-Y4",
            "mejor_error_sd_traslacion_con_recorte": round(float(
                res[(res.modelo == "traslacion") & (res.recorte == "si")][cols_sd]
                .abs().max(axis=1).min()), 4) if (res.recorte == "si").any() else None,
        },
    }


def tabla_modelos(res: pd.DataFrame) -> pd.DataFrame:
    g = res.groupby(["modelo", "recorte"], dropna=False)
    t = g["w1_total"].agg(mediana="median", mejor="min", n="size").reset_index()
    return t.sort_values("mediana").reset_index(drop=True)


def main() -> int:
    raiz = Path(__file__).resolve().parents[2]
    agentes = pd.read_csv(raiz / "data" / "processed" / "poblacion_ecp2017.csv")
    obs = cargar_observado(raiz / "data" / "raw" / "ecp")
    res = correr(agentes, obs)

    salida = raiz / "data" / "processed" / "exp4"
    salida.mkdir(parents=True, exist_ok=True)
    res.to_csv(salida / "resultados.csv", index=False)
    tabla_modelos(res).to_csv(salida / "por_modelo.csv", index=False)
    import json
    veredicto = evaluar(res, obs)
    with open(salida / "veredicto.json", "w", encoding="utf-8") as f:
        json.dump(veredicto, f, indent=2, ensure_ascii=False)
    print(json.dumps(veredicto, indent=2, ensure_ascii=False))
    print(tabla_modelos(res).to_string(index=False))
    print(f"\nTodo en {salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
