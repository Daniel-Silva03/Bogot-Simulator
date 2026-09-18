"""
src/network/homophilic_network.py

Generador 2 de NETWORK_SPECIFICATION.md (sección 4) — red homofílica.

QUÉ REPRESENTA: los agentes interactúan con mayor probabilidad con otros
que se les parecen demográficamente (homofilia documentada en
RESEARCH.md sección 22 a partir de Jiang et al., 2022).

Distancia entre agentes, sobre las tres variables numéricas de D12
(localidad se trata aparte, en el generador territorial):

    d(i,j) = sqrt( w_e (z_edad_i - z_edad_j)^2
                 + w_s (z_estrato_i - z_estrato_j)^2
                 + w_v (z_educ_i - z_educ_j)^2 )

Probabilidad de conexión: kernel exponencial p_ij ∝ exp(-β d(i,j)).

SUPUESTO EXPLÍCITO (no hecho), heredado de NETWORK_SPECIFICATION.md
sección 8: pesos iguales w_e = w_s = w_v = 1 por defecto. No hay todavía
evidencia para preferir una variable sobre otra; revisarlo pertenece al
Experimento 3 (heterogeneidad individual), no a esta etapa.

DECISIÓN DE IMPLEMENTACIÓN (Regla 3 del prompt maestro):

    DI-N5 — Qué significa "normalizar(p_ij)" en el pseudocódigo.
        La especificación escribe p_ij ∝ exp(-β d) y luego
        "si random() < normalizar(p_ij)", sin fijar la normalización.
        Se toma la lectura directa: p_ij = exp(-β d(i,j)) sin constante
        adicional. Como d ≥ 0, esto ya es una probabilidad válida en
        (0, 1]: el par idéntico (d=0) se conecta con probabilidad 1 y la
        probabilidad decae con la distancia. La constante que faltaba es
        exactamente β, que se calibra para que el grado promedio
        resultante iguale a k̄ — tal como pide la especificación. Añadir
        una segunda constante multiplicativa la volvería no identificable
        (infinitas combinaciones darían el mismo k̄) sin ganar nada.

        Consecuencia operativa: β NO se interpreta por sí solo (la propia
        especificación lo advierte). Solo tiene sentido comparado entre
        corridas con el mismo k̄ y los mismos pesos.

    DI-N6 — Límite del kernel exponencial con variables discretas.
        `estrato` (1-6) y `nivel_educativo` (0-5) son discretas. Si la
        distancia se calcula SOLO sobre ellas (pesos como (0,1,0)),
        muchísimos pares quedan a distancia exactamente 0, y esos pares
        se conectan con probabilidad exp(0)=1 por grande que sea β.
        Existe entonces un GRADO MÍNIMO ALCANZABLE por debajo del cual la
        calibración no puede bajar. Con los pesos por defecto (1,1,1) no
        ocurre, porque `edad` es prácticamente continua y rompe los
        empates.
        Decisión: cuando eso pasa, `generar()` lanza RedInvalidaError en
        vez de devolver una red mucho más densa de la pedida. Una red con
        k̄ efectivo de 233 cuando se pidió 10 arruinaría el Experimento 2
        sin avisar: las diferencias entre generadores dejarían de ser
        atribuibles a la estructura, que es justo lo que el experimento
        quiere medir. Se puede degradar a advertencia con
        `estricto=False` para explorar el caso deliberadamente.

ADVERTENCIA A08 (escalamiento), literal de la especificación: este
generador es O(N²). A N=1.000 son ~500.000 distancias — manejable. A
N=100.000 serían ~5.000 millones, 10.000 veces más caro, y haría falta
una aproximación (k-d tree, blocking por rangos de variables). No es un
problema del prototipo, pero queda anotado para que no se repita al
escalar un diseño que "funciona en el prototipo".
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any, Optional, Sequence

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

# Orden fijo: (edad, estrato, nivel_educativo) — el mismo de la fórmula
# de NETWORK_SPECIFICATION.md sección 4.
VARS_DISTANCIA = ["edad", "estrato", "nivel_educativo"]

#: DI-N7 (cierra A17). En Multipropósito, `NVCBP11AA` toma 0-6 pero también
#: 8 y 9, que son códigos de NO RESPUESTA, no estratos. Sin tratarlos, un
#: agente con estrato 9 entra a la distancia como "más extremo que estrato
#: 6" y arrastra la red: queda lejos de todo el mundo y termina aislado por
#: un código administrativo, no por su posición social.
#:
#: **No se arreglan acá: se rechazan.** Se probaron las dos formas de
#: neutralizarlos en la distancia y las dos introducen un sesgo propio:
#: omitir la componente y reescalar les SUBE el grado (más varianza en la
#: distancia y el kernel exponencial es convexo: 10,1 contra 4,9 en la
#: prueba); imputar la media se lo BAJA (0,6 contra 5,2), porque `estrato`
#: es discreta y su media cae entre dos niveles, así que el agente imputado
#: nunca queda a distancia 0 de nadie mientras que un estrato 3 coincide
#: exacto con todos los estratos 3.
#:
#: El lugar correcto es el origen: `loader.py` los descarta al construir el
#: receptor (DI-P3). Acá solo se comprueba que no hayan llegado.
#:
#: El 0 NO se trata como faltante: la ECP lo etiqueta como "conexión ilegal
#: - pirata", que es una categoría real y socioeconómicamente interpretable
#: como por debajo de estrato 1. Son 39 agentes de 168.200 en el receptor.
CODIGOS_NO_RESPUESTA_ESTRATO = (8, 9)
PESOS_POR_DEFECTO = (1.0, 1.0, 1.0)

# Tolerancias de la calibración de beta
TOL_GRADO_RELATIVA = 1e-4
MAX_ITER_BISECCION = 200
MAX_DUPLICACIONES_COTA = 60


class HomophilicNetworkGenerator(NetworkGenerator):
    """
    Nota de rendimiento: la matriz de distancias depende solo de los
    agentes y de los pesos, y β solo de las distancias y de k̄ — ninguno
    de los dos depende de la semilla. En el Experimento 2 se generan
    cientos de redes con los MISMOS agentes y el mismo k̄, cambiando solo
    la semilla, así que recalcularlos cada vez sería gastar la mayor
    parte del tiempo de cómputo en repetir un resultado idéntico. La
    instancia memoiza ambos; basta con reutilizar el mismo generador a lo
    largo de la corrida (`crear_generador` una vez, no una por run).
    El resultado numérico es idéntico con o sin caché.
    """

    nombre = "homofilica"
    columnas_requeridas = VARS_DISTANCIA

    def __init__(self) -> None:
        self._cache_d: dict[tuple, np.ndarray] = {}
        self._cache_beta: dict[tuple, tuple[float, float, bool]] = {}

    def generar(
        self,
        agentes: pd.DataFrame,
        k_promedio: float,
        seed: Optional[int] = None,
        pesos: Sequence[float] = PESOS_POR_DEFECTO,
        estricto: bool = True,
        **params: Any,
    ) -> NetworkResult:
        if params:
            raise TypeError(
                f"Parámetros no reconocidos por el generador homofílico: {list(params)}. "
                "Acepta k_promedio, seed, pesos y estricto."
            )

        n = self._validar(agentes, k_promedio)
        rng = np.random.default_rng(seed)

        pesos = tuple(float(w) for w in pesos)
        if len(pesos) != 3:
            raise RedInvalidaError(
                f"'pesos' debe tener 3 elementos (edad, estrato, nivel_educativo), recibió {len(pesos)}."
            )
        if any(w < 0 for w in pesos):
            raise RedInvalidaError(f"Los pesos no pueden ser negativos: {pesos}.")
        if sum(pesos) == 0:
            raise RedInvalidaError(
                "Todos los pesos son 0: la distancia sería idénticamente 0 y la red "
                "resultante sería completa, no homofílica."
            )

        i_idx, j_idx = indices_pares(n)

        clave = (_huella(agentes), pesos)
        if clave not in self._cache_d:
            self._cache_d[clave] = self._distancias(agentes, pesos, i_idx, j_idx)
        d = self._cache_d[clave]

        clave_beta = (clave, float(k_promedio))
        if clave_beta not in self._cache_beta:
            self._cache_beta[clave_beta] = calibrar_beta(d, n, k_promedio)
        beta, grado_calibrado, convergio = self._cache_beta[clave_beta]
        if not convergio:
            n_empates = int((d == 0).sum())
            mensaje = (
                f"No existe beta que produzca k̄={k_promedio} con estos pesos {pesos}: "
                f"el grado mínimo alcanzable es ~{grado_calibrado:.2f}. "
                f"Hay {n_empates} pares de agentes a distancia exactamente 0 "
                f"({100 * n_empates / len(d):.1f}% de los pares), y esos se conectan con "
                "probabilidad 1 sin importar beta (ver DI-N6 en este módulo). "
                "Causa habitual: pesos que dejan fuera 'edad' y dejan la distancia "
                "sobre variables discretas. Soluciones: dar peso > 0 a 'edad', o pedir "
                "un k_promedio por encima de ese mínimo."
            )
            if estricto:
                raise RedInvalidaError(mensaje)
            logger.warning("%s (estricto=False: se continúa con la red más densa)", mensaje)

        p_pares = np.exp(-beta * d)
        adjacency = muestrear_aristas(p_pares, i_idx, j_idx, n, rng)
        W = normalizar_pesos(adjacency)

        resultado = NetworkResult(
            adjacency=adjacency,
            W=W,
            generador=self.nombre,
            parametros={
                "k_promedio_objetivo": k_promedio,
                "pesos": {"edad": pesos[0], "estrato": pesos[1], "nivel_educativo": pesos[2]},
                "beta_calibrado": round(float(beta), 6),
                "grado_esperado_calibracion": round(float(grado_calibrado), 4),
                "calibracion_convergio": bool(convergio),
                "distancia_media_pares": round(float(d.mean()), 4),
            },
            seed=seed,
        )
        logger.info(
            "Red homofílica generada: beta=%.4f, k̄ objetivo=%.2f, efectivo=%.2f",
            beta, k_promedio, resultado.grado_promedio,
        )
        return resultado

    # ------------------------------------------------------------------

    @staticmethod
    def _distancias(
        agentes: pd.DataFrame,
        pesos: tuple[float, ...],
        i_idx: np.ndarray,
        j_idx: np.ndarray,
    ) -> np.ndarray:
        """
        Distancia ponderada por par, sobre las variables estandarizadas.

        La estandarización (z-score sobre la propia población de agentes)
        es lo que impide que `edad`, con rango ~[18, 100], domine a
        `estrato` (1-6) y `nivel_educativo` (0-5) por puro efecto de
        escala — la razón explícita que da la especificación en su
        sección 2.
        """
        X = agentes[VARS_DISTANCIA].to_numpy(dtype=float)
        # DI-N7: los códigos de no-respuesta no se parchean, se rechazan
        i_estrato = VARS_DISTANCIA.index("estrato")
        sin_estrato = np.isin(X[:, i_estrato], CODIGOS_NO_RESPUESTA_ESTRATO)
        if sin_estrato.any():
            raise RedInvalidaError(
                f"{int(sin_estrato.sum())} agentes traen estrato en "
                f"{CODIGOS_NO_RESPUESTA_ESTRATO}, que son códigos de no-respuesta de "
                "Multipropósito y no estratos. Se descartan en loader.py (DI-P3); "
                "esta población se construyó antes de esa corrección y hay que "
                "regenerarla.")
        if np.isnan(X).any():
            raise RedInvalidaError(
                "Hay valores nulos en edad/estrato/nivel_educativo. La población "
                "sintética no debería tenerlos (ver validar_agentes en "
                "src/population/build_agents.py)."
            )

        mu = X.mean(axis=0)
        sd = X.std(axis=0)
        # Una variable constante en la muestra no aporta información de
        # distancia; se neutraliza en vez de producir división por cero.
        sd_seguro = np.where(sd == 0, 1.0, sd)
        Z = (X - mu) / sd_seguro
        Z[:, sd == 0] = 0.0

        dif = Z[i_idx] - Z[j_idx]
        w = np.asarray(pesos, dtype=float)
        return np.sqrt((w * dif**2).sum(axis=1))


def _huella(agentes: pd.DataFrame) -> bytes:
    """Huella de las variables de distancia, para saber si la caché sigue
    siendo válida. Cambiar un solo valor de un agente invalida la entrada,
    así que la caché nunca puede devolver distancias de otra población."""
    X = np.ascontiguousarray(agentes[VARS_DISTANCIA].to_numpy(dtype=float))
    return hashlib.blake2b(X.tobytes(), digest_size=16).digest()


def grado_esperado(d: np.ndarray, n: int, beta: float) -> float:
    """
    Grado promedio esperado de la red bajo p_ij = exp(-β d_ij).

    Cada par contribuye a dos grados (la red no es dirigida), de ahí el
    factor 2/N sobre la suma del triángulo superior.
    """
    return 2.0 * float(np.exp(-beta * d).sum()) / n


def calibrar_beta(
    d: np.ndarray,
    n: int,
    k_objetivo: float,
    tol_relativa: float = TOL_GRADO_RELATIVA,
) -> tuple[float, float, bool]:
    """
    Busca β tal que el grado promedio esperado iguale a k̄.

    `grado_esperado(β)` es estrictamente decreciente en β:
      - β = 0    -> todas las p_ij = 1 -> grado N-1 (red completa)
      - β -> ∞   -> solo sobreviven los pares con d = 0
    por lo que una bisección es suficiente y siempre converge, salvo en
    el caso degenerado en que ni con β enorme el grado baja hasta k̄
    (ocurre si hay muchos agentes idénticos en las tres variables). Ese
    caso se reporta con `convergio=False` en vez de quedarse en un bucle
    o devolver silenciosamente una red más densa de la pedida.

    Returns
    -------
    (beta, grado_esperado_en_beta, convergio)
    """
    lo, hi = 0.0, 1.0

    duplicaciones = 0
    g_hi = grado_esperado(d, n, hi)
    while g_hi > k_objetivo:
        hi *= 2.0
        g_hi = grado_esperado(d, n, hi)
        duplicaciones += 1
        if duplicaciones > MAX_DUPLICACIONES_COTA:
            return hi, g_hi, False

    for _ in range(MAX_ITER_BISECCION):
        mid = 0.5 * (lo + hi)
        g = grado_esperado(d, n, mid)
        if abs(g - k_objetivo) <= tol_relativa * k_objetivo:
            return mid, g, True
        if g > k_objetivo:
            lo = mid
        else:
            hi = mid

    mid = 0.5 * (lo + hi)
    g = grado_esperado(d, n, mid)
    return mid, g, abs(g - k_objetivo) <= 1e-2 * k_objetivo
