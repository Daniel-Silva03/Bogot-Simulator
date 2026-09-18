"""
src/utils/config.py

Carga y validación de los YAML de `config/` (ARCHITECTURE.md sección 5.6:
config-driven, no hardcoded).

La validación es deliberadamente estricta y falla temprano. Un experimento
son miles de corridas: descubrir a los veinte minutos que `n_runs` venía
como texto, o que el nombre del generador está mal escrito, es peor que
fallar en el primer segundo.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml

CLAVES_REQUERIDAS = ["experiment_id", "poblacion", "opinion_model", "n_pasos", "n_runs", "seed_base"]


class ConfigError(Exception):
    """El YAML no describe un experimento ejecutable."""


@dataclass
class ConfiguracionRed:
    """Una combinación concreta de parámetros de red del barrido."""

    tipo: str
    params: dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        """Identificador estable y legible, usado para derivar semillas y
        para nombrar las filas de resultados. Estable = no depende del
        orden en que se expandió el barrido."""
        partes = [self.tipo] + [f"{k}{v}" for k, v in sorted(self.params.items())]
        return "_".join(partes)


@dataclass
class ConfiguracionExperimento:
    experiment_id: str
    poblacion: str
    opinion_model: str
    opinion_model_params: dict[str, Any]
    n_pasos: int
    n_runs: int
    seed_base: int
    redes: list[ConfiguracionRed]
    n_agentes: Optional[int] = None
    guardar_series: bool = True
    rango_opinion: Optional[tuple[float, float]] = None
    crudo: dict[str, Any] = field(default_factory=dict)

    @property
    def n_corridas_totales(self) -> int:
        return len(self.redes) * self.n_runs


def expandir_barrido(network_sweep: list[dict]) -> list[ConfiguracionRed]:
    """
    Convierte el bloque `network_sweep` del YAML en la lista de
    combinaciones concretas.

    Cada entrada declara un tipo y, para cada parámetro, un valor o una
    lista de valores; las listas se combinan en producto cartesiano. El
    ejemplo de ARCHITECTURE.md —4 valores de k̄ para aleatoria y
    homofílica, 4×4 para territorial— da 24 configuraciones.
    """
    combinaciones: list[ConfiguracionRed] = []
    for i, entrada in enumerate(network_sweep):
        if not isinstance(entrada, dict) or "tipo" not in entrada:
            raise ConfigError(f"network_sweep[{i}] debe ser un diccionario con clave 'tipo'.")
        tipo = entrada["tipo"]
        params_listas = {
            k: (v if isinstance(v, list) else [v])
            for k, v in entrada.items() if k != "tipo"
        }
        if not params_listas:
            combinaciones.append(ConfiguracionRed(tipo=tipo))
            continue
        claves = sorted(params_listas)
        for valores in itertools.product(*(params_listas[k] for k in claves)):
            combinaciones.append(ConfiguracionRed(tipo=tipo, params=dict(zip(claves, valores))))
    if not combinaciones:
        raise ConfigError("El barrido de redes quedó vacío.")
    return combinaciones


def cargar_config(path: str | Path) -> ConfiguracionExperimento:
    path = Path(path)
    if not path.exists():
        raise ConfigError(f"No existe el archivo de configuración {path}.")

    with open(path, encoding="utf-8") as f:
        crudo = yaml.safe_load(f)
    if not isinstance(crudo, dict):
        raise ConfigError(f"{path} no contiene un diccionario YAML.")

    faltantes = [c for c in CLAVES_REQUERIDAS if c not in crudo]
    if faltantes:
        raise ConfigError(f"Faltan claves en {path.name}: {faltantes}")

    for clave in ("n_pasos", "n_runs", "seed_base"):
        if not isinstance(crudo[clave], int) or isinstance(crudo[clave], bool):
            raise ConfigError(f"'{clave}' debe ser un entero, se recibió {crudo[clave]!r}.")
    if crudo["n_runs"] < 1 or crudo["n_pasos"] < 1:
        raise ConfigError("n_runs y n_pasos deben ser >= 1.")

    if "network_sweep" not in crudo:
        raise ConfigError("Falta 'network_sweep': sin él no hay nada que barrer.")
    redes = expandir_barrido(crudo["network_sweep"])

    rango = crudo.get("rango_opinion")
    if rango is not None:
        if not (isinstance(rango, list) and len(rango) == 2):
            raise ConfigError("'rango_opinion' debe ser una lista de dos números, ej. [1, 5].")
        rango = (float(rango[0]), float(rango[1]))

    return ConfiguracionExperimento(
        experiment_id=str(crudo["experiment_id"]),
        poblacion=str(crudo["poblacion"]),
        opinion_model=str(crudo["opinion_model"]),
        opinion_model_params=dict(crudo.get("opinion_model_params") or {}),
        n_pasos=int(crudo["n_pasos"]),
        n_runs=int(crudo["n_runs"]),
        seed_base=int(crudo["seed_base"]),
        redes=redes,
        n_agentes=crudo.get("n_agentes"),
        guardar_series=bool(crudo.get("guardar_series", True)),
        rango_opinion=rango,
        crudo=crudo,
    )
