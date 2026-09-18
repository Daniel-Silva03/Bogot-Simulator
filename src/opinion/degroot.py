"""
src/opinion/degroot.py

DeGroot — consenso por promediado repetido de opiniones vecinas
(MODEL_SPECIFICATION.md sección 2).

    a_i(t+1) = Σ_j p_ij · a_j(t),     con Σ_j p_ij = 1

QUÉ REPRESENTA: influencia social pura. Cada agente reemplaza su opinión
por el promedio ponderado de sus vecinos, sin ninguna resistencia al
cambio.

POR QUÉ ESTÁ ACÁ: es el **baseline obligatorio** (A11), no un candidato a
modelo final. Su defecto conocido —converge casi siempre a consenso, y las
encuestas reales casi nunca muestran consenso— es justamente lo que lo
hace útil como vara de comparación: el Experimento 4 de RESEARCH.md
pregunta si el ABM aporta algo frente a algo mucho más simple, y esta es
la versión más simple posible de "los agentes se influyen".

Nótese que el agente no conserva peso propio salvo que esté aislado: la
diagonal de W es 0 excepto en las filas de agentes sin vecinos, que
reciben w_ii = 1 y por lo tanto conservan su opinión para siempre (DI-N3
de src/network/base.py). Esos agentes son la única razón por la que esta
dinámica puede no alcanzar consenso global.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

from src.opinion.base import OpinionModel

logger = logging.getLogger(__name__)


class DeGrootModel(OpinionModel):
    """Promediado puro. No tiene parámetros libres: la red lo determina todo."""

    nombre = "degroot"

    def paso(self, a: np.ndarray) -> np.ndarray:
        return self.W @ a

    def calcular_agente(self, i: int, a: np.ndarray) -> float:
        # La ecuación tal cual aparece en el documento, para un solo agente.
        # Referencia de verificación de `paso()`, no código de producción.
        return float(sum(self.W[i, j] * a[j] for j in range(self.n)))

    def parametros(self) -> dict[str, Any]:
        return {"modelo": self.nombre, "parametros_libres": "ninguno"}
