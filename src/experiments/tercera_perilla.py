"""
src/experiments/tercera_perilla.py

¿Es una sola la tercera perilla? — `claude/ANALISIS_TERCERA_PERILLA_SPEC.md`.

Dos análisis independientes concluyeron que hacen falta tres parámetros y no
dos, pero describen el tercero distinto: `ANALISIS_RESIDUO.md` como forma
derivada del nivel (ECP, índice casi continuo con 150 valores distintos) y
`EXPERIMENT_7_RESULTS.md` como un ancho de difuminado sigma (EPC, cinco
categorías enteras). Este módulo prueba si son lo mismo.

DECISIONES DE IMPLEMENTACIÓN
----------------------------
DI-T1. **El modelo categórico usa números aleatorios comunes.** Los saltos
    de cada agente se deciden con un vector uniforme sorteado UNA vez por
    tramo: subir si u_i < a, bajar si u_i > 1-b. Así la función objetivo es
    determinista y continua en (a, b), y el ajuste no persigue ruido del
    generador. Sin esto el optimizador no converge de forma reproducible.

DI-T2. **El modelo categórico tiene exactamente dos parámetros por tramo**,
    igual que el baseline afín (u, gamma). La comparación de P2 es
    apples-to-apples: si gana, gana sin el tercer parámetro.

DI-T3. **En la ECP se trabaja por reconstrucción, no por simulación**, para
    que P4 sea comparable con `ANALISIS_RESIDUO.md` §4, que se hizo así. En
    la EPC se simula desde a0, para que P1 y P2 sean comparables con el
    Experimento 7. Son dos marcos distintos a propósito y no se mezclan
    dentro de una misma predicción.

DI-T4. **El sigma se ajusta por búsqueda en malla, no por optimizador.** El
    objetivo es ruidoso en sigma (cada evaluación sortea) y una malla con
    promedio sobre semillas es más honesta que un óptimo local encontrado
    por descenso. La malla se reporta entera.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.experiments.metrics import wasserstein1          # noqa: E402

ESCALA_EPC = (1.0, 5.0)
MALLA_SIGMA = (0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.7)
N_SEMILLAS_RUIDO = 5


# --------------------------------------------------------------------------
# Forzamiento afín (el baseline del Experimento 7) y su versión con ruido
# --------------------------------------------------------------------------

def afin(a: np.ndarray, media_obj: float, sd_obj: float) -> np.ndarray:
    """Lleva `a` a la media y la sd objetivo. Preserva la forma exactamente."""
    m, s = float(a.mean()), float(a.std())
    if s <= 0:
        return np.full_like(a, media_obj)
    return media_obj + (sd_obj / s) * (a - m)


def afin_con_ruido(a: np.ndarray, media_obj: float, sd_obj: float,
                   sigma: float, rng: np.random.Generator) -> np.ndarray:
    """Afín, más ruido gaussiano, re-ajustando después para no perder momentos."""
    if sigma <= 0:
        return afin(a, media_obj, sd_obj)
    v = afin(a, media_obj, sd_obj) + rng.normal(0.0, sigma, size=a.shape)
    return afin(v, media_obj, sd_obj)      # el ruido infla la sd; se corrige


# --------------------------------------------------------------------------
# Forzamiento categórico: el soporte nunca sale de la grilla (P2)
# --------------------------------------------------------------------------

def _mover(a: np.ndarray, u: np.ndarray, sube: float, baja: float,
           lo: float, hi: float) -> np.ndarray:
    """Cada agente sube o baja UN escalón según el uniforme común (DI-T1)."""
    v = a.copy()
    v = np.where(u < sube, v + 1.0, v)
    v = np.where(u > 1.0 - baja, v - 1.0, v)
    return np.clip(v, lo, hi)


def categorico(a: np.ndarray, media_obj: float, sd_obj: float,
               rng: np.random.Generator, lo: float = 1.0, hi: float = 5.0,
               reintentos: int = 3) -> tuple[np.ndarray, float, float]:
    """Ajusta (sube, baja) para acertar media y sd sin salir de la grilla.

    Dos parámetros y dos momentos, igual que el baseline afín (DI-T2).
    Devuelve (estado, sube, baja).
    """
    u = rng.random(size=a.shape)          # números comunes: el objetivo es determinista

    def error(p):
        s, b = float(np.clip(p[0], 0, 1)), float(np.clip(p[1], 0, 1))
        if s + b > 1:
            s, b = s / (s + b), b / (s + b)
        v = _mover(a, u, s, b, lo, hi)
        return (v.mean() - media_obj) ** 2 + (v.std() - sd_obj) ** 2

    from scipy.optimize import minimize
    mejor, mejor_err = None, np.inf
    arranques = [(0.2, 0.2), (0.4, 0.05), (0.05, 0.4), (0.3, 0.3)][:1 + reintentos]
    for p0 in arranques:
        r = minimize(error, x0=np.array(p0), method="Nelder-Mead",
                     options={"xatol": 1e-4, "fatol": 1e-8, "maxiter": 400})
        if r.fun < mejor_err:
            mejor, mejor_err = r.x, r.fun
    s, b = float(np.clip(mejor[0], 0, 1)), float(np.clip(mejor[1], 0, 1))
    if s + b > 1:
        s, b = s / (s + b), b / (s + b)
    return _mover(a, u, s, b, lo, hi), s, b


# --------------------------------------------------------------------------
# Forma derivada del nivel (la tercera perilla de ANALISIS_RESIDUO)
# --------------------------------------------------------------------------

def curvas_cuantil(muestras: dict[int, np.ndarray], pesos: dict[int, np.ndarray],
                   n_puntos: int = 200) -> tuple[np.ndarray, dict[int, np.ndarray]]:
    """Función cuantil estandarizada (media 0, sd 1) de cada año: la 'forma'."""
    p = (np.arange(n_puntos) + 0.5) / n_puntos
    curvas = {}
    for anio, v in muestras.items():
        w = pesos[anio]
        orden = np.argsort(v)
        vs, ws = v[orden], w[orden]
        acum = np.cumsum(ws) / ws.sum()
        q = np.interp(p, acum, vs)
        m = float(np.average(v, weights=w))
        s = float(np.sqrt(np.average((v - m) ** 2, weights=w)))
        curvas[anio] = (q - m) / s
    return p, curvas


def ajustar_forma_desde_nivel(curvas: dict[int, np.ndarray],
                              medias: dict[int, float]):
    """PCA sobre las curvas de forma y regresión del PC1 sobre el nivel.

    Devuelve (curva_media, carga_pc1, coeficientes de la recta pc1 ~ media).
    """
    anios = sorted(curvas)
    X = np.vstack([curvas[a] for a in anios])
    media_curva = X.mean(axis=0)
    Xc = X - media_curva
    U, S, Vt = np.linalg.svd(Xc, full_matrices=False)
    carga = Vt[0]
    puntajes = Xc @ carga
    m = np.array([medias[a] for a in anios])
    coef = np.polyfit(m, puntajes, 1)
    varianza = (S ** 2) / (S ** 2).sum()
    return media_curva, carga, coef, dict(zip(anios, puntajes)), varianza


def reconstruir(media_obj: float, sd_obj: float, media_curva: np.ndarray,
                carga: np.ndarray | None = None, coef=None) -> np.ndarray:
    """Distribución reconstruida a partir de sus momentos y (opcional) la forma."""
    z = media_curva.copy()
    if carga is not None and coef is not None:
        z = z + np.polyval(coef, media_obj) * carga
    return media_obj + sd_obj * z
