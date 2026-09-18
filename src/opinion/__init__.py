"""
src/opinion — modelos de dinámica de opinión (MODEL_SPECIFICATION.md).

DeGroot y Friedkin-Johnsen implementan la misma interfaz, así que el
código de simulación es idéntico para los dos. Eso es lo que permite el
Experimento 4 de RESEARCH.md (comparar el ABM contra su baseline) sin
escribir dos simuladores.

El registro `MODELOS` mapea el string del YAML de configuración
(`opinion_model: "friedkin_johnsen"`, ARCHITECTURE.md sección 5.6) a la
clase correspondiente.

Uso típico:

    from src.network import crear_generador
    from src.opinion import crear_modelo

    red = crear_generador("territorial").generar(agentes, k_promedio=10, seed=42, h=20)
    modelo = crear_modelo("friedkin_johnsen", red.W, phi=0.7)
    tray = modelo.simular(agentes["opinion_t0"].to_numpy(), n_pasos=100)

    tray.media[-1]     # opinión media de equilibrio
    tray.metadata()    # bloque para run_metadata.json
"""

from __future__ import annotations

from typing import Any

import numpy as np

from src.opinion.base import (
    ModeloOpinionError,
    OpinionModel,
    Trayectoria,
    validar_phi,
)
from src.opinion.cognicion_motivada import CognicionMotivadaModel
from src.opinion.degroot import DeGrootModel
from src.opinion.friedkin_johnsen import FriedkinJohnsenModel

MODELOS: dict[str, type[OpinionModel]] = {
    DeGrootModel.nombre: DeGrootModel,
    FriedkinJohnsenModel.nombre: FriedkinJohnsenModel,
    CognicionMotivadaModel.nombre: CognicionMotivadaModel,
}


def crear_modelo(tipo: str, W: np.ndarray, **params: Any) -> OpinionModel:
    """Instancia el modelo pedido por nombre ("degroot", "friedkin_johnsen").
    Falla con la lista de opciones válidas en vez de un KeyError pelado, y
    rechaza parámetros que el modelo no acepta en vez de ignorarlos."""
    if tipo not in MODELOS:
        raise ValueError(f"Modelo de opinión desconocido: '{tipo}'. Opciones: {sorted(MODELOS)}.")
    try:
        return MODELOS[tipo](W, **params)
    except TypeError as e:
        raise ModeloOpinionError(
            f"Parámetros no válidos para el modelo '{tipo}': {e}. "
            f"DeGroot no acepta ninguno; Friedkin-Johnsen acepta 'phi'; "
            f"cognicion_motivada acepta 'alpha', 'rho', 'lam', 'k', 'theta', "
            f"'centro' y 'seed'.") from e


__all__ = [
    "MODELOS",
    "crear_modelo",
    "OpinionModel",
    "Trayectoria",
    "ModeloOpinionError",
    "DeGrootModel",
    "FriedkinJohnsenModel",
    "CognicionMotivadaModel",
    "validar_phi",
]
