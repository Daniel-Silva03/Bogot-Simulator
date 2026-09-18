"""
src/network/base.py

Interfaz común de los generadores de red de interacción especificados en
NETWORK_SPECIFICATION.md, y estructura de salida compartida.

Los tres generadores (aleatoria, homofílica, territorial) son variantes
intercambiables del mismo prototipo: el modelo de opinión no sabe cuál se
usó, solo recibe la matriz de pesos de influencia (ARCHITECTURE.md
sección 5.2, A07 de PROJECT_CONTEXT.md).

DECISIONES DE IMPLEMENTACIÓN no cubiertas por NETWORK_SPECIFICATION.md
(documentadas aquí porque hubo que tomarlas para poder escribir código —
Regla 3 del prompt maestro: separar hecho / supuesto / decisión):

    DI-N1 — Qué devuelve `generar()`.
        La especificación llama "p_ij" a dos objetos distintos: la
        PROBABILIDAD de que exista una arista, y el PESO DE INFLUENCIA que
        consumen DeGroot y Friedkin-Johnsen. No son lo mismo: la primera
        genera la red, el segundo se deriva de la red ya realizada.
        `generar()` devuelve un `NetworkResult` que contiene ambos:
            - `adjacency`: la red realizada (booleana, simétrica, sin
              autolazos) — necesaria para medir propiedades de red en el
              Experimento 2 (grado, segregación territorial, homofilia
              observada);
            - `W`: la adyacencia normalizada por filas, que es lo que
              entra en las ecuaciones de MODEL_SPECIFICATION.md.
        Mantener la normalización en un solo lugar (aquí) evita que cada
        modelo de opinión la reimplemente de forma distinta.

    DI-N2 — Representación densa (numpy).
        A N=1.000 una matriz float64 pesa 8 MB: trivial, y deja el código
        legible y verificable por inspección. La red real es muy dispersa
        (k̄ ∈ [5,20] de 999 vecinos posibles), así que al abordar A08
        (escalamiento a 100.000) habrá que pasar a representación sparse.
        Queda anotado aquí para que no se descubra tarde, igual que la
        advertencia de costo O(N²) de NETWORK_SPECIFICATION.md sección 4.

    DI-N3 — Agentes aislados.
        Con k̄=5 y N=1.000, una fracción no despreciable de agentes queda
        con grado 0 (en Erdős–Rényi, ~e^-5 ≈ 0,7%). Una fila de ceros no
        se puede normalizar, y ponerla en cero haría que la opinión de ese
        agente colapsara a 0 — un artefacto de implementación, no del
        modelo. Decisión: un agente sin vecinos recibe peso propio
        w_ii = 1, es decir conserva su opinión. La red NO se modifica
        (no se le inventan aristas) y el número de aislados queda
        registrado en la metadata de la corrida para que sea visible.
        Nótese que w_ii=1 solo aparece en filas aisladas: en el resto de
        la matriz la diagonal es 0, tal como la definen las fórmulas de
        MODEL_SPECIFICATION.md.

    DI-N4 — Redes no dirigidas.
        NETWORK_SPECIFICATION.md define p_ij simétricamente en los tres
        generadores (la distancia d(i,j) es simétrica, la pertenencia a
        una localidad también). Se muestrea por lo tanto el triángulo
        superior y se simetriza. La matriz de pesos W resultante NO es
        simétrica, porque cada fila se normaliza por el grado de ese
        agente: dos agentes conectados se influyen mutuamente, pero no
        con la misma intensidad si tienen distinto número de vecinos.
        Esto es lo esperado en DeGroot/Friedkin-Johnsen, no un error.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class RedInvalidaError(Exception):
    """Se lanza cuando los parámetros pedidos no pueden producir una red
    válida (ej. k̄ ≥ N-1, o p_intra > 1 en el generador territorial).
    Mejor fallar aquí que devolver una red que no cumple lo que se pidió
    y contaminar silenciosamente el Experimento 2 (Regla 2 del prompt
    maestro)."""


@dataclass
class NetworkResult:
    """
    Salida común de los tres generadores.

    Attributes
    ----------
    adjacency : np.ndarray (N, N), dtype=bool
        Red realizada. Simétrica, diagonal en False.
    W : np.ndarray (N, N), dtype=float64
        Matriz de pesos de influencia: adyacencia normalizada por filas.
        Cada fila suma exactamente 1. Filas de agentes aislados tienen
        w_ii = 1 (ver DI-N3).
    generador : str
        "aleatoria" | "homofilica" | "territorial".
    parametros : dict
        Parámetros efectivamente usados, incluidos los derivados por
        calibración (beta, p_intra, p_inter). Se serializa tal cual en
        run_metadata.json (ARCHITECTURE.md sección 5.5).
    seed : int | None
        Semilla usada. Sin ella la corrida no es reproducible.
    """

    adjacency: np.ndarray
    W: np.ndarray
    generador: str
    parametros: dict = field(default_factory=dict)
    seed: Optional[int] = None

    @property
    def n_agentes(self) -> int:
        return self.adjacency.shape[0]

    @property
    def grados(self) -> np.ndarray:
        return self.adjacency.sum(axis=1).astype(int)

    @property
    def n_aristas(self) -> int:
        return int(self.adjacency.sum() // 2)

    @property
    def grado_promedio(self) -> float:
        return float(self.grados.mean())

    @property
    def n_aislados(self) -> int:
        return int((self.grados == 0).sum())

    def metadata(self) -> dict[str, Any]:
        """Bloque listo para volcar en run_metadata.json."""
        return {
            "network_generator": self.generador,
            "parametros_red": self.parametros,
            "seed_red": self.seed,
            "n_agentes": self.n_agentes,
            "n_aristas": self.n_aristas,
            "grado_promedio_efectivo": round(self.grado_promedio, 4),
            "grado_min": int(self.grados.min()),
            "grado_max": int(self.grados.max()),
            "grado_std": round(float(self.grados.std()), 4),
            "n_aislados": self.n_aislados,
            "densidad": round(2 * self.n_aristas / (self.n_agentes * (self.n_agentes - 1)), 6),
        }

    def reporte(self) -> str:
        m = self.metadata()
        lineas = [
            f"Red '{self.generador}' — {m['n_agentes']} agentes, {m['n_aristas']} aristas.",
            f"  grado promedio efectivo: {m['grado_promedio_efectivo']} "
            f"(min {m['grado_min']}, max {m['grado_max']}, sd {m['grado_std']})",
            f"  densidad: {m['densidad']}",
            f"  parámetros: {self.parametros}",
        ]
        if self.n_aislados:
            pct = 100 * self.n_aislados / self.n_agentes
            lineas.append(
                f"  NOTA: {self.n_aislados} agentes aislados ({pct:.1f}%) — conservan su "
                f"opinión (w_ii=1, ver DI-N3 en src/network/base.py)."
            )
        return "\n".join(lineas)


class NetworkGenerator(ABC):
    """
    Interfaz común (ARCHITECTURE.md sección 5.2).

    Contrato: dado un DataFrame de agentes y un grado promedio objetivo
    k̄, devolver un `NetworkResult`. Cada generador añade sus propios
    parámetros como keyword arguments, y es responsable de que el grado
    promedio EFECTIVO de la red producida se aproxime a k̄ — esa es la
    condición que hace comparables los tres generadores en el
    Experimento 2 (si no, cualquier diferencia en el resultado podría
    deberse simplemente a que una red es más densa que otra).
    """

    nombre: str = "base"
    #: columnas de D12 que este generador necesita además de agent_id
    columnas_requeridas: list[str] = []

    @abstractmethod
    def generar(
        self,
        agentes: pd.DataFrame,
        k_promedio: float,
        seed: Optional[int] = None,
        **params: Any,
    ) -> NetworkResult:
        ...

    # ------------------------------------------------------------------
    # utilidades compartidas por los tres generadores
    # ------------------------------------------------------------------

    def _validar(self, agentes: pd.DataFrame, k_promedio: float) -> int:
        n = len(agentes)
        if n < 2:
            raise RedInvalidaError(f"Se necesitan al menos 2 agentes, se recibieron {n}.")
        if k_promedio <= 0:
            raise RedInvalidaError(f"k_promedio debe ser > 0, se recibió {k_promedio}.")
        if k_promedio >= n - 1:
            raise RedInvalidaError(
                f"k_promedio={k_promedio} es imposible con N={n}: el grado máximo "
                f"alcanzable es {n - 1} (red completa)."
            )
        faltantes = set(self.columnas_requeridas) - set(agentes.columns)
        if faltantes:
            raise RedInvalidaError(
                f"Al generador '{self.nombre}' le faltan columnas del agente: {faltantes}. "
                "Deben venir de la población sintética (D12)."
            )
        return n


# ----------------------------------------------------------------------
# funciones compartidas — muestreo y normalización
# ----------------------------------------------------------------------


@lru_cache(maxsize=4)
def indices_pares(n: int) -> tuple[np.ndarray, np.ndarray]:
    """
    Índices (i, j) del triángulo superior, i < j: los N(N-1)/2 pares
    posibles.

    Memoizado: los tres generadores lo piden en cada run del Experimento 2
    con el mismo N, y construirlo cuesta ~8 MB de asignación cada vez. Los
    arrays se devuelven como solo-lectura para que ningún llamador pueda
    mutar por accidente la copia compartida.

    ADVERTENCIA A08: esto materializa ~500.000 pares a N=1.000 (unos
    8 MB), pero ~5.000 millones a N=100.000 (~80 GB). Es el punto exacto
    donde el enfoque de fuerza bruta deja de servir y hay que pasar a
    muestreo directo del número de aristas (ER), k-d tree o blocking
    (homofílica) y agrupación por bloques (territorial), tal como
    advierte NETWORK_SPECIFICATION.md secciones 3-5.
    """
    i_idx, j_idx = np.triu_indices(n, k=1)
    i_idx.flags.writeable = False
    j_idx.flags.writeable = False
    return i_idx, j_idx


def muestrear_aristas(
    p_pares: np.ndarray,
    i_idx: np.ndarray,
    j_idx: np.ndarray,
    n: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """
    Convierte un vector de probabilidades por par en una matriz de
    adyacencia booleana simétrica.

    `p_pares` puede ser un escalar (caso Erdős–Rényi) o un array con una
    probabilidad por par, en el mismo orden que (i_idx, j_idx).
    """
    u = rng.random(len(i_idx))
    conectados = u < p_pares

    adjacency = np.zeros((n, n), dtype=bool)
    adjacency[i_idx[conectados], j_idx[conectados]] = True
    adjacency |= adjacency.T
    return adjacency


def normalizar_pesos(adjacency: np.ndarray) -> np.ndarray:
    """
    Convierte la adyacencia en la matriz de pesos de influencia W:
    cada fila se divide por el grado del agente, de modo que suma 1.

    Un agente aislado recibe w_ii = 1 — conserva su opinión (DI-N3).
    """
    W = adjacency.astype(np.float64)
    aislados = np.where(~adjacency.any(axis=1))[0]
    if len(aislados):
        W[aislados, aislados] = 1.0
    W /= W.sum(axis=1, keepdims=True)
    return W


# ----------------------------------------------------------------------
# diagnósticos — insumo del Experimento 2
# ----------------------------------------------------------------------


def diagnosticos_red(resultado: NetworkResult, agentes: pd.DataFrame) -> dict[str, Any]:
    """
    Métricas que describen QUÉ tipo de estructura produjo el generador,
    independientemente del modelo de opinión.

    Son el insumo del Experimento 2 (RESEARCH.md sección 50): permiten
    afirmar que la red homofílica efectivamente conecta gente parecida y
    que la territorial efectivamente concentra aristas dentro de la
    localidad, en vez de suponerlo. Se comparan contra la línea base de
    "todos los pares posibles" — si la razón es ≈1, el generador no está
    induciendo ninguna estructura.

    Devuelve un dict serializable, pensado para acompañar a
    `NetworkResult.metadata()` en run_metadata.json.
    """
    n = resultado.n_agentes
    if len(agentes) != n:
        raise ValueError(
            f"El DataFrame de agentes tiene {len(agentes)} filas pero la red {n} nodos."
        )

    i_idx, j_idx = indices_pares(n)
    hay_arista = resultado.adjacency[i_idx, j_idx]

    diag: dict[str, Any] = dict(resultado.metadata())

    if "localidad" in agentes.columns:
        loc = agentes["localidad"].to_numpy()
        misma_loc = loc[i_idx] == loc[j_idx]
        frac_aristas = float(misma_loc[hay_arista].mean()) if hay_arista.any() else float("nan")
        frac_base = float(misma_loc.mean())
        diag["frac_aristas_intra_localidad"] = round(frac_aristas, 4)
        diag["frac_pares_intra_localidad_base"] = round(frac_base, 4)
        diag["segregacion_territorial"] = (
            round(frac_aristas / frac_base, 4) if frac_base > 0 else float("nan")
        )

    for var in ("edad", "estrato", "nivel_educativo"):
        if var not in agentes.columns:
            continue
        v = agentes[var].to_numpy(dtype=float)
        dif = np.abs(v[i_idx] - v[j_idx])
        media_aristas = float(dif[hay_arista].mean()) if hay_arista.any() else float("nan")
        media_base = float(dif.mean())
        diag[f"dif_media_{var}_aristas"] = round(media_aristas, 4)
        diag[f"dif_media_{var}_base"] = round(media_base, 4)
        # < 1 significa que las aristas conectan gente más parecida que el azar
        diag[f"homofilia_{var}"] = (
            round(media_aristas / media_base, 4) if media_base > 0 else float("nan")
        )

    return diag
