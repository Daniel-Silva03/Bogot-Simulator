"""
src/network/territorial_network.py

Generador 3 de NETWORK_SPECIFICATION.md (sección 5) — red territorial.

QUÉ REPRESENTA: los agentes interactúan con mayor probabilidad dentro de
su propia localidad que fuera de ella. Es un *stochastic block model* con
las localidades de Bogotá como bloques — la operacionalización directa de
"proximidad territorial" (PROJECT_CONTEXT.md sección 16, RESEARCH.md
sección 22).

    p_ij = p_intra  si localidad_i == localidad_j
    p_ij = p_inter  si localidad_i != localidad_j

Parámetro de diseño: la razón de homofilia territorial h = p_intra / p_inter.
No existe dato Bogotá-específico que lo fije; la especificación recomienda
barrer h ∈ {5, 10, 20, 50} en el Experimento 2, igual que k̄.

Dados k̄ y h, los dos parámetros se despejan de una ecuación LINEAL (a
diferencia de β en el generador homofílico, que requiere búsqueda
numérica):

    k̄ = (1/N) Σ_l n_l [ p_intra (n_l - 1) + p_inter (N - n_l) ],  p_intra = h · p_inter

    =>  p_inter = k̄ N / Σ_l n_l [ h(n_l - 1) + (N - n_l) ]

donde n_l es el número de agentes de la localidad l DENTRO de la muestra
(no la población real de Bogotá): la muestra ya es proporcional a las
proyecciones DANE-SDP usadas en DATA_SPECIFICATION.md, y usar los conteos
reales aquí produciría un grado promedio distinto del pedido.

PROPIEDAD DEL MODELO que conviene tener presente al leer el Experimento 2
(no es un error de implementación, es lo que implica la fórmula de la
especificación): con p_intra constante para todas las localidades, el
grado esperado NO es igual para todos los agentes. Un agente de Suba
(~17% de la muestra) tiene muchos más vecinos potenciales intra-localidad
que uno de Sumapaz (~0,1%), así que termina con grado mayor. k̄ es el
promedio poblacional, no el grado de cada quien. La dispersión queda
registrada en `parametros["grado_esperado_por_localidad"]` para que el
efecto sea visible al interpretar resultados, y no se confunda con un
efecto de la dinámica de opinión.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any, Optional

import numpy as np
import pandas as pd

from src.network.base import (
    NetworkGenerator,
    NetworkResult,
    RedInvalidaError,
    indices_pares,
    muestrear_aristas,
    normalizar_pesos,
)

logger = logging.getLogger(__name__)

H_POR_DEFECTO = 10.0


class TerritorialNetworkGenerator(NetworkGenerator):
    """
    Nota de rendimiento (mismo criterio que en el generador homofílico):
    la máscara "este par comparte localidad" depende solo de los agentes,
    no de la semilla ni de los parámetros. En el Experimento 2 se generan
    cientos de redes sobre la misma población, así que la instancia la
    memoiza. Reutilizar el generador a lo largo de la corrida evita
    recalcular ~500.000 comparaciones por run. El resultado numérico es
    idéntico con o sin caché.
    """

    nombre = "territorial"
    columnas_requeridas = ["localidad"]

    def __init__(self) -> None:
        self._cache_mascara: dict[bytes, np.ndarray] = {}

    def generar(
        self,
        agentes: pd.DataFrame,
        k_promedio: float,
        seed: Optional[int] = None,
        h: float = H_POR_DEFECTO,
        **params: Any,
    ) -> NetworkResult:
        if params:
            raise TypeError(
                f"Parámetros no reconocidos por el generador territorial: {list(params)}. "
                "Acepta k_promedio, seed y h."
            )

        n = self._validar(agentes, k_promedio)
        rng = np.random.default_rng(seed)

        if h < 1:
            raise RedInvalidaError(
                f"h={h} implica p_intra < p_inter, es decir, agentes que prefieren "
                "conectarse FUERA de su localidad. Si es intencional, documentarlo "
                "como escenario aparte; h=1 equivale a la red aleatoria."
            )

        loc = agentes["localidad"].to_numpy()
        if pd.isna(loc).any():
            raise RedInvalidaError("Hay agentes sin 'localidad' asignada.")

        etiquetas, conteos = np.unique(loc, return_counts=True)
        p_intra, p_inter = resolver_probabilidades(k_promedio, h, conteos, n)

        # Valor al que tiende p_intra cuando h -> infinito (red de localidades
        # completamente cerradas). Si p_intra ya está cerca de este techo,
        # subir más h casi no cambia la red: dato útil para leer el barrido
        # h ∈ {5, 10, 20, 50} del Experimento 2 y no confundir "h grande" con
        # "segregación arbitrariamente alta".
        pares_intra_posibles = float((conteos * (conteos - 1)).sum())
        p_intra_techo = min(1.0, k_promedio * n / pares_intra_posibles)

        i_idx, j_idx = indices_pares(n)
        misma_localidad = self._mascara_misma_localidad(loc, i_idx, j_idx)
        p_pares = np.where(misma_localidad, p_intra, p_inter)

        adjacency = muestrear_aristas(p_pares, i_idx, j_idx, n, rng)
        W = normalizar_pesos(adjacency)

        grado_esperado_loc = {
            str(et): round(float(p_intra * (c - 1) + p_inter * (n - c)), 3)
            for et, c in zip(etiquetas, conteos)
        }

        resultado = NetworkResult(
            adjacency=adjacency,
            W=W,
            generador=self.nombre,
            parametros={
                "k_promedio_objetivo": k_promedio,
                "h": h,
                "p_intra": round(float(p_intra), 8),
                "p_inter": round(float(p_inter), 8),
                "p_intra_techo_h_infinito": round(float(p_intra_techo), 8),
                "saturacion_h": round(float(p_intra / p_intra_techo), 4),
                "n_localidades": int(len(etiquetas)),
                "agentes_por_localidad": {str(e): int(c) for e, c in zip(etiquetas, conteos)},
                "grado_esperado_por_localidad": grado_esperado_loc,
            },
            seed=seed,
        )
        logger.info(
            "Red territorial generada: h=%.1f, p_intra=%.5f, p_inter=%.5f, "
            "k̄ objetivo=%.2f, efectivo=%.2f",
            h, p_intra, p_inter, k_promedio, resultado.grado_promedio,
        )
        return resultado

    def _mascara_misma_localidad(
        self, loc: np.ndarray, i_idx: np.ndarray, j_idx: np.ndarray
    ) -> np.ndarray:
        """True en los pares que comparten localidad. Se comparan códigos
        enteros, no strings: comparar 500.000 pares de objetos de Python
        es un orden de magnitud más lento y el resultado es el mismo."""
        codigos = pd.factorize(loc, sort=True)[0].astype(np.int32)
        clave = hashlib.blake2b(codigos.tobytes(), digest_size=16).digest()
        if clave not in self._cache_mascara:
            self._cache_mascara[clave] = codigos[i_idx] == codigos[j_idx]
        return self._cache_mascara[clave]


def resolver_probabilidades(
    k_promedio: float,
    h: float,
    conteos: np.ndarray,
    n: int,
) -> tuple[float, float]:
    """
    Despeja (p_intra, p_inter) de la ecuación lineal de la sección 5 de
    NETWORK_SPECIFICATION.md.

    Falla explícitamente si la combinación pedida exige p_intra > 1 —
    matemáticamente imposible (una probabilidad no puede exceder 1) y
    señal de que h y k̄ son incompatibles con el tamaño de las
    localidades en la muestra. Truncar p_intra a 1 en silencio rompería
    la relación h = p_intra/p_inter que el Experimento 2 está midiendo,
    así que se prefiere el error a un resultado que parece válido y no
    lo es (Regla 2 del prompt maestro).
    """
    conteos = np.asarray(conteos, dtype=float)
    # denominador = h·A + B, separado porque A y B sirven para decir, en el
    # mensaje de error, exactamente qué combinaciones sí son alcanzables.
    A = float((conteos * (conteos - 1)).sum())      # pares posibles intra-localidad
    B = float((conteos * (n - conteos)).sum())      # pares posibles inter-localidad
    denominador = h * A + B
    if denominador <= 0:
        raise RedInvalidaError(
            "No se puede resolver la red territorial: el denominador es 0 "
            "(¿una sola localidad con un solo agente?)."
        )

    p_inter = k_promedio * n / denominador
    p_intra = h * p_inter

    if p_intra > 1.0:
        # p_intra es lineal en k̄ (a h fijo), así que el k̄ máximo sale directo.
        k_max = k_promedio / p_intra
        # En h NO es lineal: p_intra(h) = h·k̄·N / (h·A + B) y tiende a k̄·N/A.
        # Por eso, si k̄·N <= A, ningún h llega a p_intra=1 y el límite solo
        # existe cuando k̄ es suficientemente grande.
        if k_promedio * n > A:
            limite_h = f"con este k_promedio el h máximo es ~{B / (k_promedio * n - A):.2f}"
        else:
            limite_h = "con este k_promedio ningún h produce p_intra > 1 (no debería verse este error)"
        raise RedInvalidaError(
            f"h={h} y k_promedio={k_promedio} exigen p_intra={p_intra:.3f} > 1, "
            f"lo cual es imposible: las localidades de la muestra no tienen suficientes "
            f"pares internos para absorber ese grado. Con este h el k_promedio máximo "
            f"alcanzable es ~{k_max:.2f}; {limite_h}. "
            "Ajustar el barrido del Experimento 2 en consecuencia."
        )
    if p_inter > 1.0:  # defensivo: no debería ocurrir si p_intra <= 1 y h >= 1
        raise RedInvalidaError(f"p_inter={p_inter:.3f} > 1 con k_promedio={k_promedio}, h={h}.")

    return p_intra, p_inter
