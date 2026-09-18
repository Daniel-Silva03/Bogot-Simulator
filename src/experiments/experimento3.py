"""
src/experiments/experimento3.py

Experimento 3B — validación de la dinámica (nivel 3) contra la ECP.
Especificación: claude/EXPERIMENT_3_SPECIFICATION.md.

QUÉ PRUEBA
----------
La población arranca en la distribución de confianza institucional de 2017
y se la deja evolucionar. Se compara contra lo observado en 2019, 2021 y
2023. Las cinco predicciones (P1..P5) están escritas en la especificación
ANTES de esta corrida; este módulo solo las evalúa.

EL PROBLEMA DEL RELOJ, Y CÓMO SE TRATA ACÁ
------------------------------------------
Un paso del modelo no es un año. El mapeo pasos → años es un parámetro
libre, y ajustarlo hasta que la curva calce sería validación circular.

Dos decisiones para que no lo sea:

DI-X1. Se le da al modelo su MEJOR caso, no uno cualquiera. La trayectoria
    se muestrea en una grilla de checkpoints, y se buscan los tres
    checkpoints crecientes \\(t_1 < t_2 < t_3\\) que minimizan el error total
    contra 2019/2021/2023. Eso es un techo del ajuste alcanzable bajo
    cualquier reparametrización monótona del tiempo. Si el modelo falla en
    su mejor caso, el resultado no depende de haber elegido mal el reloj.

DI-X2. La prueba central (P3) no usa el reloj para nada. Una
    reparametrización monótona puede estirar o comprimir una trayectoria
    pero no puede cambiar su forma: si la media simulada es monótona en el
    tiempo, ningún mapeo la vuelve no monótona. La media observada tiene un
    mínimo interior en 2021. Así que P3 se decide mirando si la trayectoria
    simulada tiene o no un mínimo interior, sin ajustar nada.

DI-X3. No se guardan los vectores de opinión de cada checkpoint —serían
    cientos de MB— sino las métricas ya calculadas contra los tres años
    objetivo. La búsqueda de DI-X1 opera después sobre esa matriz chica.
    Consecuencia: si más adelante se quiere una métrica nueva hay que
    volver a correr. Es el precio de que la corrida entre en memoria.

DI-X4. El observado se representa como una muestra grande extraída con
    probabilidad proporcional al factor de expansión, no como los registros
    crudos. Las métricas de distribución de `metrics.py` no reciben pesos, y
    comparar contra la muestra sin ponderar mediría el diseño muestral de la
    ECP en vez de la opinión de Bogotá.

LOS CUATRO COMPETIDORES
-----------------------
`PROJECT_CONTEXT.md` A11 exige DeGroot como baseline. Se agregan dos más:

    congelado  la opinión de 2017 sin tocar. El modelo tiene que ganarle a
               NO HACER NADA. Es el baseline que más incomoda y el que más
               informa: si la dinámica no mejora sobre quedarse quieto, la
               dinámica no está aportando.
    ruido      perturbación gaussiana de la misma magnitud que el cambio
               observado. Controla que un ajuste no venga simplemente de
               mover las cosas.
"""

from __future__ import annotations

import itertools
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd

RAIZ_REPO = Path(__file__).resolve().parents[2]

from src.experiments.metrics import ks, wasserstein1          # noqa: E402
from src.network import crear_generador                        # noqa: E402
from src.opinion import crear_modelo                           # noqa: E402
from src.population.ecp import distribucion_observada          # noqa: E402
from src.utils.seeds import semilla_para                       # noqa: E402

logger = logging.getLogger(__name__)

ANIO_BASE = 2017
ANIOS_OBJETIVO = (2019, 2021, 2023)

#: Checkpoints donde se mide la trayectoria. Densos al principio, porque es
#: donde Friedkin-Johnsen se mueve, y espaciados después para cubrir la
#: convergencia sin gastar 500 evaluaciones por corrida.
CHECKPOINTS = tuple(list(range(0, 21)) + [25, 30, 40, 50, 75, 100, 150, 200, 300, 500])

N_MUESTRA_OBSERVADA = 200_000   # DI-X4
UMBRAL_COLA_BAJA = 2.0
UMBRAL_COLA_ALTA = 3.5

# Criterios de la especificación, sección 4.
UMBRAL_P1_MEDIA = 0.05      # movimiento mínimo de la media para no fallar P1
UMBRAL_P2_SD = 0.05         # error máximo de sd para pasar P2

# ENMIENDA A LA ESPECIFICACIÓN — 16/09/2026, antes de correr 3B completo.
#
# La especificación redactó P3 y P4 como "¿hay un mínimo (o máximo) interior
# en la trayectoria?", sin umbral de magnitud. Al probar el código apareció
# el problema: la media de Friedkin-Johnsen se mueve ~0,004 en total, y
# dentro de ese recorrido hay repuntes de orden 1e-5 que son aritmética de
# punto flotante en la convergencia, no una V. Con tolerancia puramente
# numérica, P3 daba "pasa" para corridas cuya media es plana.
#
# Se agrega el umbral de magnitud, igual al de P1 (0,05): un mínimo interior
# cuenta solo si el rebote posterior supera ese valor. Lo observado rebota
# 0,185, casi cuatro veces el umbral, así que el criterio no se está
# ablandando para el modelo — se está exigiendo que la V sea una V.
#
# Queda anotado acá y en la especificación porque cambiar un criterio
# después de correr sería exactamente lo que ese documento intenta evitar.
UMBRAL_P3_REBOTE = 0.05

# El baseline de ruido se escala para que su caminata aleatoria alcance la
# magnitud del cambio observado alrededor de este checkpoint. Sin un
# anclaje así, el paso queda dimensionado contra el primer checkpoint y a
# los 500 pasos el ruido acumulado multiplica por 20 la dispersión inicial:
# deja de ser un control y pasa a ser un generador de basura.
PASO_REFERENCIA_RUIDO = 50


@dataclass
class EstadoObservado:
    """Lo que hay que reproducir, ya listo para comparar."""

    muestras: dict[int, np.ndarray]          # año -> muestra ponderada
    media: dict[int, float]
    sd: dict[int, float]
    cola_baja: dict[int, float]
    cola_alta: dict[int, float]

    @property
    def anios(self) -> list[int]:
        return sorted(self.muestras)

    def hay_minimo_interior(self) -> bool:
        m = [self.media[a] for a in self.anios]
        return any(m[i] < m[i - 1] and m[i] < m[i + 1] for i in range(1, len(m) - 1))


def cargar_observado(
    raiz_ecp: str | Path,
    anios: Iterable[int] = (ANIO_BASE,) + ANIOS_OBJETIVO,
    n_muestra: int = N_MUESTRA_OBSERVADA,
    seed: int = 0,
) -> EstadoObservado:
    obs = distribucion_observada(raiz_ecp, anios)
    rng = np.random.default_rng(seed)
    muestras, media, sd, cb, ca = {}, {}, {}, {}, {}
    for anio, g in obs.groupby("anio"):
        w = g["fex"].to_numpy(dtype=float)
        v = g["indice"].to_numpy(dtype=float)
        muestras[int(anio)] = rng.choice(v, size=n_muestra, p=w / w.sum())
        m = float(np.average(v, weights=w))
        media[int(anio)] = m
        sd[int(anio)] = float(np.sqrt(np.average((v - m) ** 2, weights=w)))
        cb[int(anio)] = float(np.average(v < UMBRAL_COLA_BAJA, weights=w))
        ca[int(anio)] = float(np.average(v > UMBRAL_COLA_ALTA, weights=w))
    return EstadoObservado(muestras, media, sd, cb, ca)


# --------------------------------------------------------------------------
# Trayectorias
# --------------------------------------------------------------------------

def _resumir(v: np.ndarray) -> tuple[float, float, float, float]:
    return (float(v.mean()), float(v.std()),
            float((v < UMBRAL_COLA_BAJA).mean()), float((v > UMBRAL_COLA_ALTA).mean()))


def trayectoria_checkpoints(
    modelo_nombre: str,
    W: Optional[np.ndarray],
    a0: np.ndarray,
    obs: EstadoObservado,
    checkpoints: tuple[int, ...] = CHECKPOINTS,
    seed: int = 0,
    **kwargs,
) -> dict:
    """
    Corre un modelo y mide en cada checkpoint, sin guardar los vectores
    (DI-X3).

    Devuelve las series de media / sd / colas y la matriz de W1 y KS contra
    cada año objetivo, con forma (checkpoints × años).
    """
    rng = np.random.default_rng(seed)
    anios = list(ANIOS_OBJETIVO)

    if modelo_nombre == "congelado":
        avanzar = lambda a: a                                    # noqa: E731
    elif modelo_nombre == "ruido":
        # Magnitud calibrada al cambio observado por tramo, repartida en los
        # pasos que separan checkpoints consecutivos. No pretende ser un
        # modelo: es el control de "mover cosas al azar también mueve métricas".
        escala = (abs(obs.media[anios[0]] - obs.media[ANIO_BASE])
                  / np.sqrt(PASO_REFERENCIA_RUIDO))
        avanzar = lambda a: a + rng.normal(0.0, escala, size=a.shape)   # noqa: E731
    else:
        modelo = crear_modelo(modelo_nombre, W, **kwargs)
        modelo.preparar(a0)
        avanzar = modelo.paso

    media, sd, cbaja, calta = [], [], [], []
    w1 = np.empty((len(checkpoints), len(anios)))
    kss = np.empty((len(checkpoints), len(anios)))

    a = a0.copy()
    paso_actual = 0
    for fila, t in enumerate(checkpoints):
        while paso_actual < t:
            a = avanzar(a)
            paso_actual += 1
        m, s, cb, ca = _resumir(a)
        media.append(m); sd.append(s); cbaja.append(cb); calta.append(ca)
        for col, anio in enumerate(anios):
            w1[fila, col] = wasserstein1(a, obs.muestras[anio])
            kss[fila, col] = ks(a, obs.muestras[anio])

    return {
        "checkpoints": np.array(checkpoints),
        "media": np.array(media), "sd": np.array(sd),
        "cola_baja": np.array(cbaja), "cola_alta": np.array(calta),
        "w1": w1, "ks": kss,
    }


def mejor_mapeo_temporal(w1: np.ndarray) -> tuple[tuple[int, int, int], float]:
    """
    El mejor mapeo monótono pasos → años (DI-X1).

    Busca los tres índices de checkpoint estrictamente crecientes que
    minimizan la suma de W1 contra 2019, 2021 y 2023. Fuerza \\(t_1 < t_2 <
    t_3\\) porque el tiempo no retrocede; permitir empates o inversiones
    dejaría de ser una reparametrización.
    """
    n = w1.shape[0]
    mejor, mejor_costo = None, np.inf
    for i, j, k in itertools.combinations(range(n), 3):
        c = w1[i, 0] + w1[j, 1] + w1[k, 2]
        if c < mejor_costo:
            mejor, mejor_costo = (i, j, k), c
    return mejor, float(mejor_costo)


def tiene_minimo_interior(serie: np.ndarray, umbral: float = UMBRAL_P3_REBOTE) -> bool:
    """
    ¿La trayectoria baja y después vuelve a subir de forma material? (P3)

    `umbral` no es una tolerancia numérica sino un criterio sustantivo: un
    repunte menor que eso no es una V, es ruido de convergencia. Ver la
    enmienda documentada arriba.
    """
    minimo = int(np.argmin(serie))
    if minimo in (0, len(serie) - 1):
        return False
    return bool(serie[minimo:].max() - serie[minimo] > umbral)


def tiene_maximo_interior(serie: np.ndarray, umbral: float = UMBRAL_P3_REBOTE) -> bool:
    """Lo mismo al revés, para la masa de cola baja (P4). El umbral está en
    puntos de proporción: un máximo interior de la cola cuenta si la caída
    posterior supera 5 puntos porcentuales, que es el orden de lo observado
    (37,1 % -> 23,2 %)."""
    maximo = int(np.argmax(serie))
    if maximo in (0, len(serie) - 1):
        return False
    return bool(serie[maximo] - serie[maximo:].min() > umbral)


# --------------------------------------------------------------------------
# Barrido
# --------------------------------------------------------------------------

REDES = [("aleatoria", {}), ("homofilica", {}), ("territorial", {"h": 20})]
# D15 (16/09/2026): el grado promedio dejó de ser un parámetro barrido a
# ciegas. La ECP (Capital Social, P2047 + P2049) mide en Bogotá 2023 una red
# cercana de media 5,35 y mediana 4, con 26 % sin red. El barrido se centra
# en 5 y conserva 4 y 8 como sensibilidad. Antes: [4, 8, 16].
K_MEDIOS = [4, 5, 8]
MODELOS = (
    [("friedkin_johnsen", {"phi": p}) for p in (0.3, 0.5, 0.7, 0.9)]
    + [("degroot", {}), ("congelado", {}), ("ruido", {})]
)


def correr(
    agentes: pd.DataFrame,
    obs: EstadoObservado,
    n_semillas: int = 20,
    seed_base: int = 20260916,
    redes: list = REDES,
    k_medios: list = K_MEDIOS,
    modelos: list = MODELOS,
) -> pd.DataFrame:
    a0 = agentes["opinion_t0"].to_numpy(dtype=float)
    anios = list(ANIOS_OBJETIVO)
    filas = []

    total = len(redes) * len(k_medios) * n_semillas
    hecho = 0
    for (tipo, kw_red), k, s in itertools.product(redes, k_medios, range(n_semillas)):
        semilla_red = semilla_para(seed_base, tipo, k, s, "red")
        red = crear_generador(tipo).generar(agentes, k_promedio=k, seed=semilla_red, **kw_red)
        hecho += 1
        if hecho % 20 == 0:
            logger.info("redes generadas: %d/%d", hecho, total)

        for nombre, kw in modelos:
            tr = trayectoria_checkpoints(
                nombre, red.W, a0, obs,
                seed=semilla_para(seed_base, tipo, k, s, nombre, *map(str, kw.values())),
                **kw,
            )
            idx, costo = mejor_mapeo_temporal(tr["w1"])
            fila = {
                "red": tipo, "k_medio": k, "semilla": s,
                "modelo": nombre, **{f"param_{a}": b for a, b in kw.items()},
                "w1_total": costo,
                "pasos_elegidos": [int(tr["checkpoints"][i]) for i in idx],
                "media_inicial": tr["media"][0],
                "sd_inicial": tr["sd"][0],
                "media_final": tr["media"][-1],
                "sd_final": tr["sd"][-1],
                "delta_media_max": float(np.abs(tr["media"] - tr["media"][0]).max()),
                "contraccion_sd": float(1 - tr["sd"][-1] / tr["sd"][0]),
                "minimo_interior_media": tiene_minimo_interior(tr["media"]),
                "maximo_interior_cola_baja": tiene_maximo_interior(tr["cola_baja"]),
            }
            for col, anio in enumerate(anios):
                i = idx[col]
                fila[f"w1_{anio}"] = float(tr["w1"][i, col])
                fila[f"err_media_{anio}"] = float(tr["media"][i] - obs.media[anio])
                fila[f"err_sd_{anio}"] = float(tr["sd"][i] - obs.sd[anio])
            filas.append(fila)

    return pd.DataFrame(filas)


# --------------------------------------------------------------------------
# Veredictos
# --------------------------------------------------------------------------

def evaluar_predicciones(res: pd.DataFrame, obs: EstadoObservado) -> dict:
    """Aplica los criterios de la sección 4 de la especificación."""
    fj = res[res.modelo == "friedkin_johnsen"]
    recorrido_obs = max(abs(obs.media[a] - obs.media[ANIO_BASE]) for a in ANIOS_OBJETIVO)

    p1_mov = float(fj["delta_media_max"].max())
    err_sd = fj[[f"err_sd_{a}" for a in ANIOS_OBJETIVO]].abs().max(axis=1)
    p2_mejor = float(err_sd.min())

    return {
        "P1_nivel": {
            "pasa": p1_mov >= UMBRAL_P1_MEDIA,
            "movimiento_max_simulado": round(p1_mov, 4),
            "recorrido_observado": round(recorrido_obs, 4),
            "razon": round(recorrido_obs / p1_mov, 1) if p1_mov > 0 else None,
        },
        "P2_dispersion": {
            "pasa": p2_mejor < UMBRAL_P2_SD,
            "mejor_error_sd": round(p2_mejor, 4),
        },
        "P3_no_monotonia": {
            "pasa": bool(fj["minimo_interior_media"].any()),
            "observado_tiene_minimo_interior": obs.hay_minimo_interior(),
            "corridas_con_minimo_interior": int(fj["minimo_interior_media"].sum()),
            "corridas_totales": int(len(fj)),
        },
        "P4_colas": {
            "pasa": bool(fj["maximo_interior_cola_baja"].any()),
            "corridas_con_maximo_interior_cola_baja": int(fj["maximo_interior_cola_baja"].sum()),
        },
    }


def comparar_baselines(res: pd.DataFrame) -> pd.DataFrame:
    """Mediana e intervalo intercuartílico del ajuste, por modelo."""
    g = res.groupby([c for c in ["modelo", "param_phi"] if c in res.columns], dropna=False)
    tabla = g["w1_total"].agg(mediana="median",
                              q1=lambda x: x.quantile(0.25),
                              q3=lambda x: x.quantile(0.75),
                              n="size").reset_index()
    return tabla.sort_values("mediana").reset_index(drop=True)
