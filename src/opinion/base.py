"""
src/opinion/base.py

Interfaz común de los modelos de dinámica de opinión especificados en
MODEL_SPECIFICATION.md, y estructura de salida compartida.

Igual que con los generadores de red, los modelos son variantes
intercambiables: `BogotaSocialModel` no necesita saber cuál está
corriendo, solo recibe una matriz de pesos y devuelve trayectorias. Eso es
lo que permite correr DeGroot y Friedkin-Johnsen con el mismo código de
simulación, que es exactamente lo que pide el Experimento 4 de RESEARCH.md
(comparar el ABM contra baselines).

DECISIONES DE IMPLEMENTACIÓN no cubiertas por MODEL_SPECIFICATION.md
(Regla 3 del prompt maestro — separar hecho / supuesto / decisión):

    DI-O1 — La interfaz es vectorizada, no agente por agente.
        ARCHITECTURE.md sección 5.3 define `calcular(agente, vecinos,
        pesos) -> nueva_opinion`. El Experimento 2 son ~4.800 corridas ×
        100 pasos × 1.000 agentes: 480 millones de llamadas en Python
        puro, inviable. Las dos ecuaciones son productos matriz-vector, y
        `paso(a) -> a'` las expresa exactamente con una sola operación de
        numpy por paso.
        Se conserva `calcular_agente(i, a)`, que calcula la opinión de un
        solo agente escribiendo la ecuación literalmente como aparece en
        el documento. No se usa en producción: existe para que los tests
        verifiquen, agente por agente, que la versión matricial computa lo
        mismo. Así la optimización queda auditada en vez de asumida.
        ARCHITECTURE.md debe actualizarse para reflejar esta interfaz.

    DI-O2 — Actualización síncrona, garantizada por construcción.
        ARCHITECTURE.md sección 2 advierte que DeGroot y Friedkin-Johnsen
        están definidos con actualización SÍNCRONA, y que el scheduler por
        defecto de Mesa introduciría un sesgo de orden que no está en la
        ecuación. Con la forma matricial ese error es imposible de
        cometer: `paso()` calcula el vector nuevo entero a partir del
        viejo, sin mutar nada en el camino. La decisión de usar
        `SimultaneousActivation` sigue siendo la correcta para cuando
        `src/model/` envuelva esto en Mesa, pero la fidelidad a la
        fórmula ya no depende de ella.

    DI-O3 — Qué se registra por paso.
        Guardar la trayectoria completa cuesta 800 KB por corrida
        (100 pasos × 1.000 agentes × 8 bytes); a 4.800 corridas son casi
        4 GB. Por defecto `simular()` registra solo un resumen por paso
        (media, desviación, mínimo, máximo) más el vector final completo,
        y acepta `registrar_opiniones=True` cuando se necesita la
        trayectoria entera de una corrida concreta para analizarla.
        Deliberadamente NO se calcula aquí ningún índice de polarización:
        ARCHITECTURE.md lo asigna a `src/experiments/metrics.py`, y cuál
        usar (varianza, bimodalidad, número de clusters) sigue sin
        decidirse — elegirlo acá en silencio sería cerrar por la puerta
        de atrás una decisión que afecta cómo se lee el Experimento 2.

    DI-O4 — Criterio de parada.
        `simular()` corre los pasos pedidos, pero se detiene antes si el
        cambio máximo entre pasos cae por debajo de `tol` (1e-9 por
        defecto). La trayectoria se completa repitiendo el último valor,
        de modo que todas las corridas de un barrido tengan la misma
        longitud y sean comparables entre sí. `pasos_efectivos` y
        `convergio` quedan en la metadata para no perder la información.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)

TOLERANCIA_FILAS_W = 1e-9
TOL_CONVERGENCIA = 1e-9


class ModeloOpinionError(Exception):
    """Insumos o parámetros que no permiten correr el modelo. Mejor fallar
    acá que producir una trayectoria que parece válida y no lo es."""


@dataclass
class Trayectoria:
    """
    Resultado de una simulación.

    Attributes
    ----------
    opinion_final : np.ndarray (N,)
        Estado en el último paso.
    media, desviacion, minimo, maximo : np.ndarray (n_pasos+1,)
        Resumen por paso, incluyendo t=0.
    opiniones : np.ndarray (n_pasos+1, N) | None
        Trayectoria completa, solo si se pidió (ver DI-O3).
    """

    opinion_final: np.ndarray
    media: np.ndarray
    desviacion: np.ndarray
    minimo: np.ndarray
    maximo: np.ndarray
    modelo: str
    parametros: dict = field(default_factory=dict)
    pasos_solicitados: int = 0
    pasos_efectivos: int = 0
    convergio: bool = False
    opiniones: Optional[np.ndarray] = None

    @property
    def n_agentes(self) -> int:
        return len(self.opinion_final)

    def metadata(self) -> dict[str, Any]:
        """Bloque listo para volcar en run_metadata.json."""
        return {
            "opinion_model": self.modelo,
            "parametros_opinion": self.parametros,
            "n_pasos_solicitados": self.pasos_solicitados,
            "n_pasos_efectivos": self.pasos_efectivos,
            "convergio": self.convergio,
            "media_inicial": round(float(self.media[0]), 6),
            "media_final": round(float(self.media[-1]), 6),
            "desviacion_inicial": round(float(self.desviacion[0]), 6),
            "desviacion_final": round(float(self.desviacion[-1]), 6),
            "rango_final": [round(float(self.minimo[-1]), 6), round(float(self.maximo[-1]), 6)],
        }

    def reporte(self) -> str:
        m = self.metadata()
        estado = (f"convergió en {self.pasos_efectivos} pasos"
                  if self.convergio else f"no convergió en {self.pasos_solicitados} pasos")
        return (
            f"Modelo '{self.modelo}' — {self.n_agentes} agentes, {estado}.\n"
            f"  media:      {m['media_inicial']:.4f} -> {m['media_final']:.4f}\n"
            f"  desviación: {m['desviacion_inicial']:.4f} -> {m['desviacion_final']:.4f}\n"
            f"  rango final: [{m['rango_final'][0]:.4f}, {m['rango_final'][1]:.4f}]\n"
            f"  parámetros: {self.parametros}"
        )


class OpinionModel(ABC):
    """
    Interfaz común (ARCHITECTURE.md sección 5.3, con la desviación de DI-O1).

    Contrato: dada una matriz de pesos de influencia W (la que producen los
    generadores de `src/network/`), avanzar un vector de opiniones un paso.
    """

    nombre: str = "base"

    def __init__(self, W: np.ndarray) -> None:
        self.W = self._validar_W(W)
        self.n = self.W.shape[0]

    # ------------------------------------------------------------------

    @abstractmethod
    def paso(self, a: np.ndarray) -> np.ndarray:
        """Un paso de la dinámica, sobre todos los agentes a la vez."""

    @abstractmethod
    def calcular_agente(self, i: int, a: np.ndarray) -> float:
        """
        La misma ecuación para un solo agente, escrita como aparece en
        MODEL_SPECIFICATION.md. No se usa en producción — es la referencia
        contra la que los tests verifican `paso()` (ver DI-O1).
        """

    def preparar(self, a0: np.ndarray) -> None:
        """Gancho para modelos con estado que dependa del instante inicial
        (Friedkin-Johnsen ancla a a(0)). Por defecto no hace nada."""

    def parametros(self) -> dict[str, Any]:
        return {}

    # ------------------------------------------------------------------

    def simular(
        self,
        a0: np.ndarray,
        n_pasos: int,
        registrar_opiniones: bool = False,
        tol: float = TOL_CONVERGENCIA,
    ) -> Trayectoria:
        """
        Corre `n_pasos` de la dinámica desde `a0`.

        Se detiene antes si el cambio máximo cae por debajo de `tol`, pero
        las series de resumen se completan hasta `n_pasos` repitiendo el
        último valor, para que todas las corridas de un barrido tengan la
        misma longitud (DI-O4).
        """
        if n_pasos < 0:
            raise ModeloOpinionError(f"n_pasos debe ser >= 0, se recibió {n_pasos}.")

        a = np.asarray(a0, dtype=np.float64).ravel()
        if a.shape[0] != self.n:
            raise ModeloOpinionError(
                f"El vector de opiniones tiene {a.shape[0]} elementos pero la matriz "
                f"de pesos es de {self.n} agentes.")
        if not np.isfinite(a).all():
            raise ModeloOpinionError("Hay opiniones iniciales no finitas (NaN o inf).")

        self.preparar(a)

        media = np.empty(n_pasos + 1)
        desviacion = np.empty(n_pasos + 1)
        minimo = np.empty(n_pasos + 1)
        maximo = np.empty(n_pasos + 1)
        opiniones = np.empty((n_pasos + 1, self.n)) if registrar_opiniones else None

        def registrar(t: int, v: np.ndarray) -> None:
            media[t], desviacion[t] = v.mean(), v.std()
            minimo[t], maximo[t] = v.min(), v.max()
            if opiniones is not None:
                opiniones[t] = v

        registrar(0, a)
        convergio, pasos_efectivos = False, n_pasos

        for t in range(1, n_pasos + 1):
            nueva = self.paso(a)
            cambio = float(np.abs(nueva - a).max())
            a = nueva
            registrar(t, a)
            if cambio < tol:
                convergio, pasos_efectivos = True, t
                # completar el resto repitiendo el estado de equilibrio
                if t < n_pasos:
                    media[t + 1:] = media[t]
                    desviacion[t + 1:] = desviacion[t]
                    minimo[t + 1:] = minimo[t]
                    maximo[t + 1:] = maximo[t]
                    if opiniones is not None:
                        opiniones[t + 1:] = a
                break

        return Trayectoria(
            opinion_final=a,
            media=media, desviacion=desviacion, minimo=minimo, maximo=maximo,
            modelo=self.nombre,
            parametros=self.parametros(),
            pasos_solicitados=n_pasos,
            pasos_efectivos=pasos_efectivos,
            convergio=convergio,
            opiniones=opiniones,
        )

    # ------------------------------------------------------------------

    @staticmethod
    def _validar_W(W: np.ndarray) -> np.ndarray:
        W = np.asarray(W, dtype=np.float64)
        if W.ndim != 2 or W.shape[0] != W.shape[1]:
            raise ModeloOpinionError(f"W debe ser cuadrada, tiene forma {W.shape}.")
        if W.shape[0] == 0:
            raise ModeloOpinionError("W está vacía.")
        if not np.isfinite(W).all():
            raise ModeloOpinionError("W tiene valores no finitos.")
        if (W < 0).any():
            raise ModeloOpinionError("W tiene pesos negativos.")
        sumas = W.sum(axis=1)
        if not np.allclose(sumas, 1.0, atol=TOLERANCIA_FILAS_W):
            peor = int(np.abs(sumas - 1.0).argmax())
            raise ModeloOpinionError(
                f"Las filas de W deben sumar 1 (la fila {peor} suma {sumas[peor]:.6f}). "
                "Usar la W que devuelven los generadores de src/network/, que ya está "
                "normalizada — incluidos los agentes aislados, que reciben w_ii=1.")
        return W


def validar_phi(phi: Any, n: int) -> np.ndarray:
    """
    Normaliza el parámetro de susceptibilidad de Friedkin-Johnsen a un
    vector de longitud n. Acepta un escalar (se difunde a todos) o un
    arreglo por agente — la especificación lo define por agente, el YAML de
    ARCHITECTURE.md lo usa como escalar mientras no esté estimado.
    """
    arr = np.asarray(phi, dtype=np.float64)
    if arr.ndim == 0:
        arr = np.full(n, float(arr))
    elif arr.ndim == 1:
        if arr.shape[0] != n:
            raise ModeloOpinionError(
                f"phi tiene {arr.shape[0]} elementos pero hay {n} agentes.")
        arr = arr.copy()
    else:
        raise ModeloOpinionError(f"phi debe ser escalar o vector, tiene forma {arr.shape}.")

    if not np.isfinite(arr).all():
        raise ModeloOpinionError("phi tiene valores no finitos.")
    if ((arr < 0) | (arr > 1)).any():
        raise ModeloOpinionError(
            "phi debe estar en [0, 1]: es la susceptibilidad a la influencia social "
            "(1 = DeGroot puro, 0 = el agente nunca cambia de opinión).")
    return arr
