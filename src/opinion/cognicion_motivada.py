"""
src/opinion/cognicion_motivada.py

Marco de cognición motivada — Lorenz, Neumann & Schröder (2021), calibrado
contra encuestas por Gestefeld & Lorenz (2023).

    Δa_i = ( λ^k / (λ^k + |a_j − a_i|^k) ) · α · (a_j − ρ · a_i)

más, con probabilidad θ por paso, un retorno idiosincrático a la opinión
de anclaje.

POR QUÉ EXISTE, Y POR QUÉ TARDÓ
-------------------------------
`MODEL_SPECIFICATION.md` §4 designó este marco como **modelo objetivo de
la fase de calibración**, desde antes de que existiera un solo experimento,
por una razón concreta: de los cinco modelos evaluados es el único con
evidencia publicada de ajuste contra datos reales — 1.235 distribuciones
de confianza institucional de la European Social Survey con mediana
R² > 0,8, y transiciones individuales del Swiss Household Panel.

El prototipo implementó DeGroot y Friedkin-Johnsen y nunca llegó aquí. El
diagnóstico de `claude/DIAGNOSTICO_Y_ALTERNATIVAS.md` §4 lo registró como
fallo 8: la afirmación "ninguna familia endógena reproduce estos datos" no
estaba respaldada, porque la familia con mejor evidencia no se había
probado.

QUÉ TIENE QUE FJ NO TIENE
-------------------------
Tres cosas, y la tercera es la que motiva el Experimento 5.

1. **Cognición motivada**: la influencia decae suavemente con la distancia
   de opinión. Con k grande se acerca al umbral duro de
   Hegselmann-Krause; con k pequeño es un decaimiento gradual. Nadie deja
   de escuchar de golpe.

2. **Grado de asimilación (ρ)**, que no es lo que parece a primera vista.
   Si dos agentes ya piensan igual (c_j = c_i = c), el término deja
   Δ = peso · α · c · (1 − ρ). Es decir:

       ρ < 1  ->  el agente se aleja del centro: REFUERZO, no moderación
       ρ = 1  ->  asimilación pura; dos iguales no se mueven
       ρ > 1  ->  el agente es arrastrado hacia el centro: moderación

   Lo escribí al revés en la primera versión de este módulo —"ρ < 1
   modera"— y lo atrapó una aserción del test antes de que llegara a
   ningún resultado. Queda anotado porque el signo de ρ decide si el
   modelo polariza o modera, que es la diferencia entre dos familias de
   dinámica, no un detalle de parametrización.

3. **Contracción que puede llegar tarde.** Esta es la propiedad que
   importa. Friedkin-Johnsen converge geométricamente, así que su
   dispersión cae rápido al principio y cada vez más lento — y lo
   observado en Bogotá es lo contrario: −4,2 % / 0,0 % / −13,8 % entre
   casos completos (`claude/ANALISIS_NORESPUESTA_2023.md`). Aquí el
   mecanismo puede invertir ese orden: mientras la distribución es ancha,
   la mayoría de los pares está lejos, el kernel los apaga y **casi no
   pasa nada**; a medida que el forzamiento exógeno desplaza la masa y
   algunos pares entran dentro de λ, la influencia se enciende y la
   contracción **acelera**. Es un mecanismo con realimentación positiva,
   no una exponencial decreciente.

   Eso es una hipótesis sobre la forma de la trayectoria, no una promesa:
   el Experimento 5 existe para ponerla a prueba.

DECISIONES DE IMPLEMENTACIÓN
----------------------------
DI-M1. **La escala se centra antes de aplicar ρ.** La ecuación publicada
    trabaja con opiniones centradas en cero, y el término (1 − ρ) empuja
    respecto de **ese cero**, que representa el punto neutral de la
    actitud. La ECP mide en 1–5, donde el cero no existe y ni siquiera
    está dentro del rango: aplicar la fórmula tal cual pondría el punto de
    referencia en "ninguna confianza en nada". El modelo opera
    internamente en c = a − centro con centro = 3,0 (punto medio de la
    escala) y devuelve a = c + centro. Sin esto, ρ no significa lo que
    dice significar.

DI-M2. **Interacción por pares sobre la red.** Cada paso, cada agente
    elige un vecino con probabilidad proporcional a su fila de W y se
    actualiza contra él. Es la forma en que se corre esta familia en la
    literatura (encuentro diádico, no promedio de vecindario), y mantiene
    la red como el objeto que los generadores de `src/network/` producen.

DI-M3. **Actualización simultánea**: todos los agentes se actualizan
    contra el estado del paso anterior, coherente con la decisión de
    `ARCHITECTURE.md` §2 y con el resto de `src/opinion/`. Evita el sesgo
    de orden que tendría una actualización secuencial.

DI-M4. **El retorno idiosincrático va a la opinión de anclaje a(0)**, no a
    un valor sorteado de nuevo. Es la lectura de `MODEL_SPECIFICATION.md`
    §2 ("el agente regresa con cierta probabilidad a su opinión inicial") y
    es la variante conservadora: un sorteo nuevo metería una fuente extra
    de dispersión que competiría con el mecanismo que se quiere medir.

DI-M5. **Los agentes aislados no interactúan.** Por DI-N3 de
    `NETWORK SPECIFICATION.md`, un agente sin vecinos tiene w_ii = 1, así
    que muestrear su fila lo devolvería a sí mismo. Un auto-encuentro
    daría distancia 0 —kernel al máximo— y con ρ ≠ 1 el término dejaría
    Δ = α·c·(1−ρ): una fuerza espuria sobre el agente aislado, que lo
    alejaría del centro (ρ<1) o lo moderaría (ρ>1) por el solo hecho de
    no tener con quién hablar. Se detecta el auto-encuentro y
    se omite el término social; al aislado solo le queda el retorno
    idiosincrático. No es un detalle marginal: el 26 % de los bogotanos
    declara red de tamaño cero (`NETWORK SPECIFICATION.md` §2.1).
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import numpy as np

from src.opinion.base import ModeloOpinionError, OpinionModel

logger = logging.getLogger(__name__)

CENTRO_ESCALA = 3.0        # DI-M1 — punto medio de la escala 1–5 de la ECP

# Valores de partida. NO son estimaciones: son el orden de magnitud con el
# que Lorenz et al. presentan el modelo, para que el barrido arranque en
# una región razonable. El Experimento 5 los barre.
ALPHA_POR_DEFECTO = 0.2    # fuerza de cambio
RHO_POR_DEFECTO = 1.0      # 1 = asimilación pura; <1 refuerza, >1 modera
RHO_MAXIMO = 2.0           # se permite el régimen moderador, no solo el original
LAMBDA_POR_DEFECTO = 1.0   # distancia a la que la influencia cae a la mitad
K_POR_DEFECTO = 2.0        # nitidez del kernel; k grande -> umbral duro
THETA_POR_DEFECTO = 0.0    # probabilidad de retorno al anclaje


class CognicionMotivadaModel(OpinionModel):
    nombre = "cognicion_motivada"

    def __init__(
        self,
        W: np.ndarray,
        alpha: float = ALPHA_POR_DEFECTO,
        rho: float = RHO_POR_DEFECTO,
        lam: float = LAMBDA_POR_DEFECTO,
        k: float = K_POR_DEFECTO,
        theta: float = THETA_POR_DEFECTO,
        centro: float = CENTRO_ESCALA,
        seed: int = 0,
    ) -> None:
        super().__init__(W)
        if not 0.0 <= alpha <= 1.0:
            raise ModeloOpinionError(f"alpha debe estar en [0,1], se recibió {alpha}.")
        if not 0.0 <= rho <= RHO_MAXIMO:
            raise ModeloOpinionError(
                f"rho debe estar en [0,{RHO_MAXIMO}], se recibió {rho}. "
                "Por debajo de 1 refuerza (aleja del centro), en 1 es asimilación pura, "
                "por encima de 1 modera (acerca al centro).")
        if lam <= 0:
            raise ModeloOpinionError(f"lambda debe ser > 0, se recibió {lam}.")
        if k <= 0:
            raise ModeloOpinionError(f"k debe ser > 0, se recibió {k}.")
        if not 0.0 <= theta <= 1.0:
            raise ModeloOpinionError(f"theta debe estar en [0,1], se recibió {theta}.")

        self.alpha, self.rho, self.lam, self.k = float(alpha), float(rho), float(lam), float(k)
        self.theta, self.centro = float(theta), float(centro)
        self._rng = np.random.default_rng(seed)
        self._a0: Optional[np.ndarray] = None
        self._acumulado = self._preparar_muestreo(self.W)
        self._aislado = np.isclose(np.diag(self.W), 1.0)     # DI-M5

    # ------------------------------------------------------------------

    @staticmethod
    def _preparar_muestreo(W: np.ndarray) -> np.ndarray:
        """Acumulada por filas, para muestrear un vecino por agente de una vez.

        Se calcula una sola vez: dentro del bucle, muestrear vecino por
        vecino con `rng.choice` por fila costaba dos órdenes de magnitud más
        que una búsqueda binaria sobre esta matriz.
        """
        filas = W.sum(axis=1, keepdims=True)
        filas[filas == 0] = 1.0
        return np.cumsum(W / filas, axis=1)

    def preparar(self, a0: np.ndarray) -> None:
        a0 = np.asarray(a0, dtype=np.float64).ravel()
        if a0.shape[0] != self.n:
            raise ModeloOpinionError(
                f"La opinión inicial tiene {a0.shape[0]} elementos pero hay {self.n} agentes.")
        self._a0 = a0.copy()

    @property
    def opinion_inicial(self) -> np.ndarray:
        if self._a0 is None:
            raise ModeloOpinionError(
                "Cognición motivada necesita el anclaje para el retorno idiosincrático. "
                "Usar simular(), que lo hace solo, o llamar preparar(a0) antes de paso().")
        return self._a0

    # ------------------------------------------------------------------

    def _vecinos(self) -> np.ndarray:
        """Un vecino por agente, con probabilidad proporcional a su fila de W.

        Vectorizado sobre la acumulada: `argmax` sobre la comparación
        devuelve el primer índice que la supera, que es lo que haría un
        `searchsorted` fila por fila. La versión con bucle de Python costaba
        dos órdenes de magnitud más, y este método está dentro del lazo de
        ajuste de u, que lo llama miles de veces.
        """
        r = self._rng.random(self.n)
        return (self._acumulado >= r[:, None]).argmax(axis=1)

    def peso_kernel(self, distancia: np.ndarray | float) -> np.ndarray | float:
        """λ^k / (λ^k + d^k) — 1 cuando la distancia es 0, →0 cuando es grande."""
        lk = self.lam ** self.k
        return lk / (lk + np.abs(distancia) ** self.k)

    def paso(self, a: np.ndarray) -> np.ndarray:
        c = np.asarray(a, dtype=np.float64) - self.centro          # DI-M1
        j = self._vecinos()                                        # DI-M2
        cj = c[j]

        peso = self.peso_kernel(cj - c)
        delta = peso * self.alpha * (cj - self.rho * c)
        delta[self._aislado | (j == np.arange(self.n))] = 0.0      # DI-M5

        nuevo = c + delta                                          # DI-M3
        if self.theta > 0.0:                                       # DI-M4
            revierte = self._rng.random(self.n) < self.theta
            nuevo[revierte] = self.opinion_inicial[revierte] - self.centro
        return nuevo + self.centro

    def calcular_agente(self, i: int, a: np.ndarray) -> float:
        raise ModeloOpinionError(
            "CognicionMotivadaModel es estocástico (elige vecino al azar y revierte con "
            "probabilidad theta), así que no tiene ecuación por agente reproducible fuera "
            "del paso. Los tests verifican el kernel y el término de cambio por separado.")

    def cambio_deterministico(self, ai: float, aj: float) -> float:
        """Δa_i para un encuentro dado, sin azar. Es la ecuación publicada.

        Existe para que los tests puedan verificar la fórmula contra valores
        calculados a mano, ya que `calcular_agente` no puede (DI-O1 de
        `src/opinion/base.py` pide una referencia comprobable).
        """
        ci, cj = ai - self.centro, aj - self.centro
        return float(self.peso_kernel(cj - ci) * self.alpha * (cj - self.rho * ci))

    def parametros(self) -> dict[str, Any]:
        return {
            "modelo": self.nombre,
            "alpha": round(self.alpha, 6), "rho": round(self.rho, 6),
            "lambda": round(self.lam, 6), "k": round(self.k, 6),
            "theta": round(self.theta, 6), "centro_escala": self.centro,
            "aislados": int(self._aislado.sum()),
            "parametros_estimados_con_datos": False,
        }


__all__ = ["CognicionMotivadaModel", "CENTRO_ESCALA"]
