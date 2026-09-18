"""
src/network/random_network.py

Generador 1 de NETWORK_SPECIFICATION.md (sección 3) — red aleatoria
Erdős–Rényi G(N, p).

QUÉ REPRESENTA: ausencia total de estructura social. Todos los pares
tienen la misma probabilidad de estar conectados, sin importar edad,
estrato, educación ni localidad.

Es el CONTROL EXPERIMENTAL del Experimento 2, en el mismo rol que
DeGroot juega como baseline de modelo: si la red homofílica o la
territorial no producen resultados distintos de esta, la conclusión del
Experimento 2 es que la estructura de interacción no importa para el
fenómeno estudiado — y eso es un hallazgo, no un fracaso.

    p_ij = k̄ / (N - 1)   para todo i ≠ j

Único parámetro libre: k̄.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import numpy as np
import pandas as pd

from src.network.base import (
    NetworkGenerator,
    NetworkResult,
    indices_pares,
    muestrear_aristas,
    normalizar_pesos,
)

logger = logging.getLogger(__name__)


class RandomNetworkGenerator(NetworkGenerator):
    """Erdős–Rényi. No necesita ninguna variable del agente: solo N."""

    nombre = "aleatoria"
    columnas_requeridas: list[str] = []

    def generar(
        self,
        agentes: pd.DataFrame,
        k_promedio: float,
        seed: Optional[int] = None,
        **params: Any,
    ) -> NetworkResult:
        if params:
            raise TypeError(
                f"El generador aleatorio no acepta parámetros adicionales, recibió: {list(params)}. "
                "Su único parámetro libre es k_promedio (NETWORK_SPECIFICATION.md sección 3)."
            )

        n = self._validar(agentes, k_promedio)
        rng = np.random.default_rng(seed)

        p = k_promedio / (n - 1)

        i_idx, j_idx = indices_pares(n)
        adjacency = muestrear_aristas(p, i_idx, j_idx, n, rng)
        W = normalizar_pesos(adjacency)

        resultado = NetworkResult(
            adjacency=adjacency,
            W=W,
            generador=self.nombre,
            parametros={"k_promedio_objetivo": k_promedio, "p": round(float(p), 8)},
            seed=seed,
        )
        logger.info(
            "Red aleatoria generada: k̄ objetivo=%.2f, efectivo=%.2f",
            k_promedio, resultado.grado_promedio,
        )
        return resultado
