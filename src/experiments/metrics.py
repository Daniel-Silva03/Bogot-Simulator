"""
src/experiments/metrics.py

Métricas de la distribución de opinión: resumen, índices de polarización y
comparación entre distribuciones.

QUÉ ÍNDICE DE POLARIZACIÓN USAR — decisión deliberadamente NO tomada
---------------------------------------------------------------------
ARCHITECTURE.md sección 8 dejaba abierto cuál usar (varianza, bimodalidad,
número de clusters), y la elección no es cosmética: cambia qué se concluye
del Experimento 2. Este módulo calcula **cuatro** y los reporta todos; cuál
encabeza los resultados se decide después de ver el experimento, con
evidencia. Es el mismo criterio que se aplicó a los generadores de red
(A07): no cerrar una decisión metodológica antes de tener con qué.

    desviacion          dispersión pura. Simple y ya calculada, pero no
                        distingue una población repartida de forma pareja
                        de una partida en dos bloques — y "polarización"
                        normalmente quiere decir lo segundo.

    bimodalidad_sarle   detecta específicamente la aparición de dos modas.
                        BC > 0,555 es el umbral convencional (el valor de
                        una uniforme). Indefinido si no hay dispersión.

    n_clusters          cuántos grupos separados de opinión quedan.
                        Depende de un umbral de separación que es un
                        parámetro libre, no un dato.

    esteban_ray         el índice estándar de la literatura de polarización,
                        con fundamento teórico explícito (identificación
                        dentro del grupo × alienación entre grupos).
                        Depende de α y del número de bins, ninguno estimado.

Los tres últimos tienen parámetros libres. Se exponen con valores por
defecto razonables y se registran en la salida, para que ningún resultado
quede dependiendo de una constante escondida.

Todo se implementa con numpy solamente: `scipy` entra al proyecto por
dependencia indirecta de scikit-learn, y no conviene que un módulo de
métricas dependa de eso.
"""

from __future__ import annotations

from typing import Any, Optional

import numpy as np
import pandas as pd

# Umbral convencional del coeficiente de bimodalidad de Sarle: es el valor
# que toma una distribución uniforme. Por encima sugiere bimodalidad.
UMBRAL_BIMODALIDAD = 0.555

# Separación mínima entre opiniones consecutivas para considerarlas grupos
# distintos. PARÁMETRO LIBRE, no un hecho — con la escala 1-5 de confianza
# institucional, 0,25 es un cuarto de punto de escala.
UMBRAL_CLUSTER = 0.25

# Sensibilidad de Esteban-Ray: cuánto pesa el tamaño del grupo propio.
# α=0 reduce el índice a una medida de dispersión; la literatura usa
# típicamente entre 1,0 y 1,6. PARÁMETRO LIBRE.
ALPHA_ESTEBAN_RAY = 1.0
BINS_ESTEBAN_RAY = 10


def resumen_opinion(a: np.ndarray) -> dict[str, float]:
    """Estadísticos descriptivos de una distribución de opinión."""
    a = np.asarray(a, dtype=float)
    p10, p50, p90 = np.percentile(a, [10, 50, 90])
    return {
        "media": float(a.mean()),
        "mediana": float(p50),
        "desviacion": float(a.std()),
        "p10": float(p10),
        "p90": float(p90),
        "minimo": float(a.min()),
        "maximo": float(a.max()),
        "rango_intercuartil": float(np.subtract(*np.percentile(a, [75, 25]))),
    }


def bimodalidad_sarle(a: np.ndarray) -> float:
    """
    Coeficiente de bimodalidad de Sarle:

        BC = (g₁² + 1) / (g₂ + 3(n−1)² / ((n−2)(n−3)))

    con g₁ la asimetría muestral y g₂ la curtosis en exceso. Devuelve NaN
    cuando no hay dispersión (consenso total): con todas las opiniones
    iguales la pregunta "¿hay dos modas?" no tiene respuesta, y devolver
    0 ó 1 sería inventarla.
    """
    a = np.asarray(a, dtype=float)
    n = a.size
    if n < 4:
        return float("nan")
    m = a - a.mean()
    m2 = float((m**2).mean())
    if m2 <= 1e-15:
        return float("nan")
    g1 = float((m**3).mean()) / m2**1.5
    g2 = float((m**4).mean()) / m2**2 - 3.0
    denominador = g2 + 3.0 * (n - 1) ** 2 / ((n - 2) * (n - 3))
    if abs(denominador) < 1e-15:
        return float("nan")
    return (g1**2 + 1.0) / denominador


def n_clusters_opinion(a: np.ndarray, umbral: float = UMBRAL_CLUSTER) -> int:
    """
    Número de grupos separados de opinión: se ordenan las opiniones y se
    cuenta cuántos huecos entre valores consecutivos superan `umbral`.

    Es la lectura más literal de "fragmentación": cuántos bloques
    distinguibles quedan. Sensible al umbral, que es un parámetro libre.
    """
    a = np.sort(np.asarray(a, dtype=float))
    if a.size == 0:
        return 0
    return int(1 + (np.diff(a) > umbral).sum())


def esteban_ray(
    a: np.ndarray,
    alpha: float = ALPHA_ESTEBAN_RAY,
    bins: int = BINS_ESTEBAN_RAY,
    rango: Optional[tuple[float, float]] = None,
) -> float:
    """
    Índice de polarización de Esteban-Ray sobre la distribución
    discretizada en `bins` intervalos:

        P = Σ_i Σ_j π_i^(1+α) · π_j · |y_i − y_j|

    donde π_i es la proporción en el bin i y y_i su centro. Captura la
    intuición de que la polarización crece cuando hay pocos grupos, grandes
    y alejados entre sí — a diferencia de la varianza, que no distingue
    cuántos grupos hay.

    `rango` fija los extremos de la discretización. Conviene pasarlo
    explícitamente (la escala de la variable, p. ej. (1, 5)) para que el
    índice sea comparable entre corridas: si se deja en None se usa el
    rango observado, y una corrida que converge a consenso tendría bins
    mucho más finos que otra dispersa.
    """
    a = np.asarray(a, dtype=float)
    if a.size == 0:
        return float("nan")
    lo, hi = rango if rango is not None else (float(a.min()), float(a.max()))
    if hi - lo < 1e-15:
        return 0.0  # consenso total: no hay grupos que alienar
    conteo, bordes = np.histogram(a, bins=bins, range=(lo, hi))
    pi = conteo / conteo.sum()
    centros = (bordes[:-1] + bordes[1:]) / 2.0
    distancias = np.abs(centros[:, None] - centros[None, :])
    pesos = (pi ** (1.0 + alpha))[:, None] * pi[None, :]
    return float((pesos * distancias).sum())


def indices_polarizacion(
    a: np.ndarray,
    rango: Optional[tuple[float, float]] = None,
    umbral_cluster: float = UMBRAL_CLUSTER,
    alpha: float = ALPHA_ESTEBAN_RAY,
    bins: int = BINS_ESTEBAN_RAY,
) -> dict[str, Any]:
    """Los cuatro índices, más los parámetros libres con que se calcularon."""
    bc = bimodalidad_sarle(a)
    return {
        "desviacion": float(np.asarray(a, dtype=float).std()),
        "bimodalidad_sarle": bc,
        "bimodal": bool(bc > UMBRAL_BIMODALIDAD) if np.isfinite(bc) else False,
        "n_clusters": n_clusters_opinion(a, umbral_cluster),
        "esteban_ray": esteban_ray(a, alpha=alpha, bins=bins, rango=rango),
        "_params": {
            "umbral_cluster": umbral_cluster,
            "umbral_bimodalidad": UMBRAL_BIMODALIDAD,
            "alpha_esteban_ray": alpha,
            "bins_esteban_ray": bins,
            "rango": list(rango) if rango else None,
        },
    }


# ----------------------------------------------------------------------
# comparación entre distribuciones — insumo del Experimento 1
# ----------------------------------------------------------------------


def wasserstein1(a: np.ndarray, b: np.ndarray, n_cuantiles: int = 1000) -> float:
    """
    Distancia de Wasserstein-1 entre dos muestras, calculada sobre
    cuantiles para que funcione con muestras de tamaños distintos.

    Se prefiere sobre la distancia KS para el Experimento 1 porque está en
    las unidades de la variable: un valor de 0,3 significa "la distribución
    simulada está, en promedio, a 0,3 puntos de escala de la observada",
    que es interpretable. KS devuelve una diferencia máxima de proporciones
    acumuladas, que no lo es.
    """
    a = np.sort(np.asarray(a, dtype=float))
    b = np.sort(np.asarray(b, dtype=float))
    if a.size == 0 or b.size == 0:
        return float("nan")
    q = (np.arange(n_cuantiles) + 0.5) / n_cuantiles
    return float(np.abs(np.quantile(a, q) - np.quantile(b, q)).mean())


def ks(a: np.ndarray, b: np.ndarray) -> float:
    """Estadístico de Kolmogorov-Smirnov: máxima diferencia entre las dos
    funciones de distribución acumuladas. Se reporta como complemento de
    Wasserstein-1, no como métrica principal."""
    a = np.sort(np.asarray(a, dtype=float))
    b = np.sort(np.asarray(b, dtype=float))
    if a.size == 0 or b.size == 0:
        return float("nan")
    todos = np.concatenate([a, b])
    cdf_a = np.searchsorted(a, todos, side="right") / a.size
    cdf_b = np.searchsorted(b, todos, side="right") / b.size
    return float(np.abs(cdf_a - cdf_b).max())


# ----------------------------------------------------------------------
# desagregación territorial
# ----------------------------------------------------------------------


def por_localidad(agentes: pd.DataFrame, opiniones: np.ndarray) -> pd.DataFrame:
    """
    Opinión final por localidad. Es la salida que permite la validación
    territorial de la Fase 7, y la que hay que leer junto al diagnóstico
    de composición de la muestra (D14): una localidad con 3 agentes no
    dice nada, por más que su media aparezca en la tabla.
    """
    d = pd.DataFrame({"localidad": agentes["localidad"].to_numpy(),
                      "opinion": np.asarray(opiniones, dtype=float)})
    g = d.groupby("localidad")["opinion"]
    return pd.DataFrame({
        "n_agentes": g.size(),
        "media": g.mean(),
        "desviacion": g.std(ddof=0),
    }).reset_index().sort_values("n_agentes", ascending=False)
