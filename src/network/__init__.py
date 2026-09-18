"""
src/network — generadores de red de interacción (NETWORK_SPECIFICATION.md).

Los tres generadores son variantes intercambiables: reciben los mismos
agentes y el mismo k̄, y devuelven el mismo objeto (`NetworkResult`). Eso
es lo que permite que el Experimento 2 aísle la estructura de red como
único factor que cambia (RESEARCH.md sección 50).

El registro `GENERADORES` mapea el string del YAML de configuración
(`network_sweep: [{tipo: "territorial", ...}]`, ARCHITECTURE.md sección
5.6) a la clase correspondiente, para no hardcodear la selección en el
runner.

Uso típico:

    from src.network import crear_generador

    gen = crear_generador("territorial")
    red = gen.generar(agentes, k_promedio=10, seed=42, h=20)
    red.W          # matriz de pesos para DeGroot / Friedkin-Johnsen
    red.metadata() # bloque para run_metadata.json
"""

from __future__ import annotations

from src.network.base import (
    NetworkGenerator,
    NetworkResult,
    RedInvalidaError,
    diagnosticos_red,
    normalizar_pesos,
)
from src.network.homophilic_network import HomophilicNetworkGenerator
from src.network.random_network import RandomNetworkGenerator
from src.network.territorial_network import TerritorialNetworkGenerator

GENERADORES: dict[str, type[NetworkGenerator]] = {
    RandomNetworkGenerator.nombre: RandomNetworkGenerator,
    HomophilicNetworkGenerator.nombre: HomophilicNetworkGenerator,
    TerritorialNetworkGenerator.nombre: TerritorialNetworkGenerator,
}


def crear_generador(tipo: str) -> NetworkGenerator:
    """Instancia el generador pedido por nombre ("aleatoria",
    "homofilica", "territorial"). Falla con la lista de opciones válidas
    en vez de un KeyError pelado."""
    if tipo not in GENERADORES:
        raise ValueError(
            f"Generador de red desconocido: '{tipo}'. Opciones: {sorted(GENERADORES)}."
        )
    return GENERADORES[tipo]()


__all__ = [
    "GENERADORES",
    "crear_generador",
    "NetworkGenerator",
    "NetworkResult",
    "RedInvalidaError",
    "RandomNetworkGenerator",
    "HomophilicNetworkGenerator",
    "TerritorialNetworkGenerator",
    "diagnosticos_red",
    "normalizar_pesos",
]
