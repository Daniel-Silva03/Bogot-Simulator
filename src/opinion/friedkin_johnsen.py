"""
src/opinion/friedkin_johnsen.py

Friedkin-Johnsen — DeGroot más un anclaje a la opinión inicial
(MODEL_SPECIFICATION.md sección 2).

    a_i(t+1) = φ_i · Σ_j p_ij · a_j(t)  +  (1 − φ_i) · a_i(0)

φ_i es la susceptibilidad del agente a la influencia social: φ=1 lo vuelve
DeGroot puro, φ=0 lo deja clavado en su opinión inicial para siempre.

QUÉ REPRESENTA: que cada quien llega a la conversación con algo propio que
no se disuelve del todo por hablar con los demás. Es lo que permite
desacuerdo persistente, y por eso la recomendación de
MODEL_SPECIFICATION.md sección 4 para el primer prototipo: evita el
defecto más obvio de DeGroot sin pagar el costo de calibración de los
modelos de confianza acotada.

SUPUESTO EXPLÍCITO (no hecho): φ **no está estimado**. ARCHITECTURE.md lo
pone como 0,7 en su YAML de ejemplo con nota de "placeholder hasta que se
estime con datos". Para el prototipo es un parámetro a barrer, no un
valor conocido — y conviene que los resultados del Experimento 2 se lean
sabiendo eso.

ANCLAJE: la ecuación se refiere a a(0), el instante inicial de ESTA
simulación. El modelo lo guarda al llamar `preparar()`, que `simular()`
invoca automáticamente. Llamar `paso()` sin haber preparado es un error
explícito y no un cero silencioso: anclar a un vector equivocado produce
trayectorias plausibles pero falsas, que es el peor modo de fallo posible.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import numpy as np

from src.opinion.base import ModeloOpinionError, OpinionModel, validar_phi

logger = logging.getLogger(__name__)

PHI_POR_DEFECTO = 0.7   # placeholder de ARCHITECTURE.md, no un valor estimado


class FriedkinJohnsenModel(OpinionModel):
    nombre = "friedkin_johnsen"

    def __init__(self, W: np.ndarray, phi: Any = PHI_POR_DEFECTO) -> None:
        super().__init__(W)
        self.phi = validar_phi(phi, self.n)
        self._a0: Optional[np.ndarray] = None

    # ------------------------------------------------------------------

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
                "Friedkin-Johnsen necesita saber a qué opinión inicial anclarse. "
                "Usar simular(), que lo hace solo, o llamar preparar(a0) antes de paso().")
        return self._a0

    def paso(self, a: np.ndarray) -> np.ndarray:
        return self.phi * (self.W @ a) + (1.0 - self.phi) * self.opinion_inicial

    def calcular_agente(self, i: int, a: np.ndarray) -> float:
        # La ecuación tal cual aparece en el documento, para un solo agente.
        influencia = sum(self.W[i, j] * a[j] for j in range(self.n))
        return float(self.phi[i] * influencia + (1.0 - self.phi[i]) * self.opinion_inicial[i])

    # ------------------------------------------------------------------

    def punto_fijo(self) -> np.ndarray:
        """
        Equilibrio analítico: a* = (I − Φ W)^{-1} (I − Φ) a(0), con
        Φ = diag(φ).

        Existe y es único cuando el radio espectral de ΦW es menor que 1,
        lo que se cumple si algún φ_i < 1 (las filas de ΦW suman φ_i, así
        que ‖ΦW‖_∞ = max φ_i). Con todos los φ_i = 1 el modelo es DeGroot
        y el equilibrio depende de la estructura de la red, no de una
        fórmula cerrada — en ese caso se lanza un error explícito.

        Sirve para verificar la simulación contra la solución exacta, que
        es la ventaja de haber elegido un modelo lineal: no hay que creerle
        al bucle, se puede comprobar.
        """
        if np.all(self.phi >= 1.0):
            raise ModeloOpinionError(
                "Con phi = 1 en todos los agentes, Friedkin-Johnsen es DeGroot y no "
                "tiene punto fijo en forma cerrada: el equilibrio lo determina la "
                "estructura de la red.")
        Phi = self.phi[:, None]
        A = np.eye(self.n) - Phi * self.W
        b = (1.0 - self.phi) * self.opinion_inicial
        try:
            return np.linalg.solve(A, b)
        except np.linalg.LinAlgError as e:  # defensivo: no debería ocurrir si max(phi) < 1
            raise ModeloOpinionError(f"No se pudo resolver el punto fijo: {e}") from e

    def parametros(self) -> dict[str, Any]:
        homogeneo = bool(np.allclose(self.phi, self.phi[0]))
        p: dict[str, Any] = {
            "modelo": self.nombre,
            "phi_homogeneo": homogeneo,
            "phi_min": round(float(self.phi.min()), 6),
            "phi_max": round(float(self.phi.max()), 6),
            "phi_estimado_con_datos": False,  # ver supuesto explícito del docstring
        }
        if homogeneo:
            p["phi"] = round(float(self.phi[0]), 6)
        else:
            p["phi_media"] = round(float(self.phi.mean()), 6)
        return p
