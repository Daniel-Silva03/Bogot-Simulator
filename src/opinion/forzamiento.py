"""
src/opinion/forzamiento.py

Forzamiento exógeno: envuelve cualquier modelo de opinión y le suma, en
cada paso, un desplazamiento común a todos los agentes.

    a(t+1) = M(a(t)) + u(t) · 1

donde M es la dinámica del modelo base (Friedkin-Johnsen, DeGroot,
traslación pura, ruido) y u(t) es un escalar por periodo.

POR QUÉ EXISTE
--------------
El Experimento 3 midió que Friedkin-Johnsen no reproduce la trayectoria de
confianza institucional de Bogotá: 4 de 5 predicciones fallidas. El
diagnóstico de `claude/DIAGNOSTICO_Y_ALTERNATIVAS.md` §1 mostró que las
cuatro son la misma ausencia. Friedkin-Johnsen es

    a(t+1) = Φ W a(t) + (I − Φ) a(0)

y todo lo que aparece a la derecha existía en t = 0: el punto fijo es una
combinación convexa de las opiniones iniciales. Un sistema cerrado que
promedia no puede mover el nivel, ni producir una V, ni vaciar una cola.
Pedirle esas tres cosas es pedirle que gane masa.

Este módulo añade el único término que faltaba. No es un parche: la
formulación conceptual de `PROJECT_CONTEXT.md` §14 siempre tuvo un término
de "exposición a eventos / contexto" que nunca se implementó.

UN DETALLE QUE NO ES OBVIO
--------------------------
Un desplazamiento uniforme **no se conserva** bajo Friedkin-Johnsen. Si se
suma c a todas las opiniones, como las filas de W suman 1:

    M(a + c·1) = Φ W a + c Φ W 1 + (I − Φ) a(0) = M(a) + c Φ 1

es decir, el desplazamiento sobrevive multiplicado por φ y se desvanece
geométricamente, porque el anclaje a a(0) lo tira hacia atrás. Por eso el
forzamiento tiene que inyectarse **en cada paso** y no puede aplicarse una
sola vez al final: u no es el desplazamiento que se observa, es el que hay
que empujar para sostenerlo.

DECISIONES DE IMPLEMENTACIÓN
----------------------------
DI-F1. El forzamiento es **común a todos los agentes**, no heterogéneo.
    Es la forma mínima que corrige el diagnóstico, y la que corresponde a
    lo medido: el Experimento 3 mostró que un solo escalar por año reduce
    el error de nivel un 32 %, contra 16 % del ABM completo. Un
    forzamiento heterogéneo tendría más poder explicativo y también más
    grados de libertad; no se justifica hasta que el homogéneo se quede
    corto.

DI-F2. `limites` recorta las opiniones a la escala real de la pregunta
    (1 a 5 en la ECP). Está **apagado por defecto**, porque no es
    inocuo: recortar contra un tope comprime la distribución y podría
    reproducir por sí solo la contracción de dispersión que el modelo no
    logra explicar. Se ofrece como variante a comparar explícitamente, no
    como comportamiento base, para que no se cuele un mecanismo por la
    puerta de atrás. Cuando está activo queda registrado en
    `parametros()` junto con cuántas opiniones tocó el borde.

DI-F3. El modelo envuelto conserva su propio `preparar()`. Friedkin-Johnsen
    se ancla a la a(0) de la simulación, no a la opinión desplazada: el
    anclaje representa "de dónde viene cada quien", y el forzamiento es
    algo que le pasa encima, no un cambio de su punto de partida.
"""

from __future__ import annotations

from typing import Any, Optional, Sequence

import numpy as np

from src.opinion.base import ModeloOpinionError, OpinionModel


class TraslacionModel(OpinionModel):
    """Dinámica nula: cada agente conserva su opinión.

    Existe para que "todos se desplazan igual, sin ningún mecanismo
    social" sea un modelo de primera clase y no un caso especial escrito
    aparte. Envuelto en `ModeloForzado` es el baseline más exigente que
    tiene el proyecto: la distribución entera se traslada en bloque, así
    que **conserva la desviación estándar exactamente**. Cualquier cambio
    de forma que el modelo observado exija tiene que venir de un
    mecanismo, y este baseline es el que lo demuestra.
    """

    nombre = "traslacion"

    def paso(self, a: np.ndarray) -> np.ndarray:
        return a

    def calcular_agente(self, i: int, a: np.ndarray) -> float:
        return float(a[i])


class RuidoModel(OpinionModel):
    """Caminata aleatoria por agente, sin influencia social.

    Control de "mover cosas al azar también mueve métricas". La escala es
    la desviación por paso.
    """

    nombre = "ruido"

    def __init__(self, W: np.ndarray, escala: float = 0.01, seed: int = 0) -> None:
        super().__init__(W)
        if escala < 0:
            raise ModeloOpinionError(f"La escala del ruido debe ser >= 0, se recibió {escala}.")
        self.escala = float(escala)
        self._rng = np.random.default_rng(seed)

    def paso(self, a: np.ndarray) -> np.ndarray:
        return a + self._rng.normal(0.0, self.escala, size=a.shape)

    def calcular_agente(self, i: int, a: np.ndarray) -> float:
        raise ModeloOpinionError(
            "RuidoModel no tiene ecuación por agente verificable: es estocástico.")

    def parametros(self) -> dict[str, Any]:
        return {"modelo": self.nombre, "escala": round(self.escala, 8)}


class ContraccionModel(OpinionModel):
    """Contracción uniforme hacia la media, sin red y sin vecinos.

        a(t+1) = a(t) + gamma * (media(a(t)) - a(t))

    POR QUÉ EXISTE: control añadido **después** de ver los resultados del
    Experimento 4, y por eso mismo etiquetado como post-hoc.

    Friedkin-Johnsen con phi bajo resultó ganarle a la traslación pura en
    las 360 configuraciones. Pero con phi pequeño su punto fijo es
    aproximadamente a(0) + phi (W a(0) - a(0)): cada agente se mueve un
    poco hacia el promedio de sus vecinos, y en agregado eso es,
    simplemente, encoger la dispersión hacia la media. La pregunta que
    queda es si hacía falta la red para eso.

    Este modelo hace lo mismo **sin ninguna estructura social**: todos se
    acercan a la media global en la misma proporción. Si empata con
    Friedkin-Johnsen, lo que los datos piden no es un mecanismo social sino
    traslación más encogimiento, y la red sigue sin aportar. Es un control
    más exigente que la traslación, y se añade precisamente porque el
    resultado favorable lo exige: un hallazgo a favor del modelo obliga a
    buscarle un baseline mejor, no a darlo por bueno.

    **gamma puede ser negativo** (DI-F4). Con gamma < 0 el modelo separa a
    los agentes de la media en vez de acercarlos: expande la dispersión. Se
    habilitó al descubrir que la serie 2013-2023 no se contrae de forma
    monótona sino que hace una joroba —sd 0,754 -> 0,934 -> 0,764—, y que
    ningún modelo capaz solo de contraer puede producir la subida. Conserva
    la media exactamente en los dos signos, que es lo que permite ajustar
    nivel y dispersión por separado.
    """

    nombre = "contraccion"

    def __init__(self, W: np.ndarray, gamma: float = 0.1) -> None:
        super().__init__(W)
        if not -1.0 <= gamma <= 1.0:
            raise ModeloOpinionError(
                f"gamma debe estar en [-1,1], se recibió {gamma}. "
                "Positivo contrae hacia la media, negativo expande (DI-F4).")
        self.gamma = float(gamma)

    def paso(self, a: np.ndarray) -> np.ndarray:
        return a + self.gamma * (a.mean() - a)

    def calcular_agente(self, i: int, a: np.ndarray) -> float:
        return float(a[i] + self.gamma * (float(np.mean(a)) - a[i]))

    def parametros(self) -> dict[str, Any]:
        return {"modelo": self.nombre, "gamma": round(self.gamma, 6)}


class ModeloForzado(OpinionModel):
    """Un modelo base más un desplazamiento exógeno por paso.

    `u_por_paso[t]` es el forzamiento que se aplica al avanzar del paso t
    al t+1. Si se agota, se repite el último valor — así una simulación
    más larga que el plan de forzamiento no falla en silencio con ceros.
    """

    nombre = "forzado"

    def __init__(
        self,
        base: OpinionModel,
        u_por_paso: Sequence[float] | np.ndarray,
        limites: Optional[tuple[float, float]] = None,   # DI-F2
    ) -> None:
        if not isinstance(base, OpinionModel):
            raise ModeloOpinionError("El modelo base debe implementar OpinionModel.")
        super().__init__(base.W)
        self.base = base
        self.u = np.asarray(u_por_paso, dtype=np.float64).ravel()
        if self.u.size == 0:
            raise ModeloOpinionError("u_por_paso no puede estar vacío.")
        if not np.isfinite(self.u).all():
            raise ModeloOpinionError("u_por_paso tiene valores no finitos.")
        if limites is not None:
            lo, hi = float(limites[0]), float(limites[1])
            if not lo < hi:
                raise ModeloOpinionError(f"limites debe cumplir lo < hi, se recibió {limites}.")
            limites = (lo, hi)
        self.limites = limites
        self._t = 0
        self._recortes = 0

    # ------------------------------------------------------------------

    def preparar(self, a0: np.ndarray) -> None:
        self.base.preparar(a0)          # DI-F3
        self._t = 0
        self._recortes = 0

    @property
    def nombre_completo(self) -> str:
        return f"{self.base.nombre}+u"

    def paso(self, a: np.ndarray) -> np.ndarray:
        u = float(self.u[min(self._t, self.u.size - 1)])
        self._t += 1
        siguiente = self.base.paso(a) + u
        if self.limites is not None:
            lo, hi = self.limites
            fuera = int(np.count_nonzero((siguiente < lo) | (siguiente > hi)))
            self._recortes += fuera
            siguiente = np.clip(siguiente, lo, hi)
        return siguiente

    def calcular_agente(self, i: int, a: np.ndarray) -> float:
        """La misma ecuación para un agente, como referencia de los tests.

        No consume el reloj interno: usa el forzamiento del paso actual sin
        avanzarlo, para poder compararse contra `paso()` sobre el mismo t.
        """
        u = float(self.u[min(self._t, self.u.size - 1)])
        v = self.base.calcular_agente(i, a) + u
        if self.limites is not None:
            v = float(np.clip(v, self.limites[0], self.limites[1]))
        return float(v)

    def parametros(self) -> dict[str, Any]:
        p = {
            "modelo": self.nombre_completo,
            "u_min": round(float(self.u.min()), 8),
            "u_max": round(float(self.u.max()), 8),
            "u_cambia_de_signo": bool((self.u > 0).any() and (self.u < 0).any()),
            "limites": list(self.limites) if self.limites else None,
            "opiniones_recortadas": self._recortes,     # DI-F2
        }
        p.update({f"base_{k}": v for k, v in self.base.parametros().items()})
        return p


# --------------------------------------------------------------------------
# Ajuste del forzamiento
# --------------------------------------------------------------------------

def ajustar_u_por_tramo(
    avanzar_con_u,
    a_inicial: np.ndarray,
    media_objetivo: float,
    n_pasos: int,
    u_lo: float = -1.0,
    u_hi: float = 1.0,
    tol: float = 1e-6,
    max_iter: int = 60,
) -> tuple[float, np.ndarray, float]:
    """Busca el u constante que lleva la media simulada a `media_objetivo`.

    `avanzar_con_u(a, u, n_pasos)` debe devolver el estado tras n_pasos con
    forzamiento constante u. La media final es **monótona creciente en u**
    para todos los modelos de este proyecto —empujar a todos hacia arriba
    no puede bajar el promedio—, así que una bisección basta y no hace
    falta un optimizador.

    Devuelve (u, estado_final, error_de_media). Si el objetivo queda fuera
    del intervalo de búsqueda, amplía el intervalo hasta 10 veces antes de
    rendirse, y en ese caso devuelve el extremo más cercano informando el
    error — es preferible a fallar, porque un tramo inalcanzable es en sí
    un resultado que hay que poder reportar.
    """
    a_inicial = np.asarray(a_inicial, dtype=np.float64)

    def media_con(u: float) -> float:
        return float(avanzar_con_u(a_inicial, u, n_pasos).mean())

    for _ in range(10):
        if media_con(u_lo) <= media_objetivo <= media_con(u_hi):
            break
        u_lo, u_hi = u_lo * 2.0, u_hi * 2.0
    else:
        extremo = u_lo if abs(media_con(u_lo) - media_objetivo) < abs(
            media_con(u_hi) - media_objetivo) else u_hi
        final = avanzar_con_u(a_inicial, extremo, n_pasos)
        return extremo, final, float(final.mean() - media_objetivo)

    for _ in range(max_iter):
        u_med = 0.5 * (u_lo + u_hi)
        m = media_con(u_med)
        if abs(m - media_objetivo) < tol:
            break
        if m < media_objetivo:
            u_lo = u_med
        else:
            u_hi = u_med
    u_med = 0.5 * (u_lo + u_hi)
    final = avanzar_con_u(a_inicial, u_med, n_pasos)
    return float(u_med), final, float(final.mean() - media_objetivo)


def ajustar_u_lineal(
    avanzar_con_u,
    a_inicial: np.ndarray,
    media_objetivo: float,
    n_pasos: int,
) -> tuple[float, np.ndarray, float]:
    """Igual que `ajustar_u_por_tramo`, pero exacto y en dos evaluaciones.

    Para Friedkin-Johnsen, DeGroot, traslación y ruido —todos lineales en
    la opinión— la media final tras n pasos con forzamiento constante u es
    una función **afín** de u:

        media(u) = media(0) + g · u

    donde g depende solo del modelo y de n_pasos, no de u. Basta evaluar en
    u = 0 y u = 1 para despejar g y resolver de una. La bisección hace 40 o
    60 evaluaciones para llegar al mismo número con menos precisión.

    **No sirve con recorte de escala** (DI-F2): recortar es no lineal y
    rompe la afinidad. Para esa variante hay que usar la bisección.

    Si g ≈ 0 el forzamiento no mueve la media —caso degenerado, por ejemplo
    n_pasos = 0— y se devuelve u = 0 informando el error resultante.
    """
    a_inicial = np.asarray(a_inicial, dtype=np.float64)
    m0 = float(avanzar_con_u(a_inicial, 0.0, n_pasos).mean())
    m1 = float(avanzar_con_u(a_inicial, 1.0, n_pasos).mean())
    g = m1 - m0
    if abs(g) < 1e-12:
        final = avanzar_con_u(a_inicial, 0.0, n_pasos)
        return 0.0, final, float(final.mean() - media_objetivo)
    u = (media_objetivo - m0) / g
    final = avanzar_con_u(a_inicial, u, n_pasos)
    return float(u), final, float(final.mean() - media_objetivo)


def ajustar_u_secante(
    avanzar_con_u,
    a_inicial: np.ndarray,
    media_objetivo: float,
    n_pasos: int,
    tol: float = 1e-4,
    max_iter: int = 12,
) -> tuple[float, np.ndarray, float]:
    """Ajuste de u para modelos NO lineales, en ~10 evaluaciones.

    La bisección necesita 40-60 evaluaciones para la misma precisión, y con
    cognición motivada cada evaluación es una simulación completa del tramo:
    ahí la diferencia entre 10 y 50 es la diferencia entre correr el
    experimento en veinte minutos o en dos horas.

    La media final sigue siendo monótona creciente en u, así que la secante
    converge rápido; si se sale del intervalo razonable o se estanca, cae a
    la bisección, que es lenta pero no falla.
    """
    a_inicial = np.asarray(a_inicial, dtype=np.float64)

    def err(u: float) -> float:
        return float(avanzar_con_u(a_inicial, u, n_pasos).mean()) - media_objetivo

    u0, u1 = 0.0, 0.05
    f0, f1 = err(u0), err(u1)
    for _ in range(max_iter):
        if abs(f1) < tol:
            break
        if abs(f1 - f0) < 1e-15:
            return ajustar_u_por_tramo(avanzar_con_u, a_inicial, media_objetivo, n_pasos)
        u2 = u1 - f1 * (u1 - u0) / (f1 - f0)
        if not np.isfinite(u2) or abs(u2) > 10.0:
            return ajustar_u_por_tramo(avanzar_con_u, a_inicial, media_objetivo, n_pasos)
        u0, f0, u1 = u1, f1, u2
        f1 = err(u1)
    if abs(f1) >= tol:
        return ajustar_u_por_tramo(avanzar_con_u, a_inicial, media_objetivo, n_pasos)
    final = avanzar_con_u(a_inicial, u1, n_pasos)
    return float(u1), final, float(final.mean() - media_objetivo)


def phi_heterogeneo(
    n: int,
    media: float,
    dispersion: float,
    seed: int = 0,
) -> np.ndarray:
    """φ_i sorteado de una Beta con la media pedida.

    `dispersion` va de 0 a 1: 0 devuelve el escalar (todos iguales) y
    valores altos acercan la Beta a una distribución en forma de U, con
    mucha gente muy tozuda y mucha muy influenciable.

    La ecuación de `MODEL_SPECIFICATION.md` §2 escribe φ con subíndice por
    agente desde el principio; la implementación del prototipo lo aplanó a
    un escalar. Esto recupera lo que la especificación ya decía.
    """
    if not 0.0 < media < 1.0:
        raise ModeloOpinionError(f"La media de phi debe estar en (0,1), se recibió {media}.")
    if not 0.0 <= dispersion < 1.0:
        raise ModeloOpinionError(
            f"dispersion debe estar en [0,1), se recibió {dispersion}.")
    if dispersion == 0.0:
        return np.full(n, float(media))
    # concentración: dispersion -> 0 da una Beta muy picuda; -> 1, muy plana
    concentracion = (1.0 - dispersion) / dispersion
    rng = np.random.default_rng(seed)
    phi = rng.beta(media * concentracion, (1.0 - media) * concentracion, size=n)
    return np.clip(phi, 1e-6, 1.0 - 1e-6)


def ajustar_gamma_por_tramo(
    avanzar_con_gamma,
    a_inicial: np.ndarray,
    sd_objetivo: float,
    n_pasos: int,
    lo: float = -0.9,
    hi: float = 0.9,
    tol: float = 1e-6,
    max_iter: int = 60,
) -> tuple[float, np.ndarray, float]:
    """Busca el gamma constante que lleva la sd simulada a `sd_objetivo`.

    Es el gemelo de `ajustar_u_por_tramo` para la DISPERSIÓN. La sd final es
    monótona DECRECIENTE en gamma —contraer más deja menos dispersión—, así
    que la bisección va al revés que la de u.

    Juntos, u y gamma son el modelo "dos números exógenos por periodo": el
    nivel y la dispersión puestos a mano, sin ningún mecanismo social. Es el
    baseline más duro que puede construirse con estos datos, y existe para
    que cualquier mecanismo tenga que ganarle en la FORMA de la distribución
    y no en sus dos primeros momentos.
    """
    a_inicial = np.asarray(a_inicial, dtype=np.float64)

    def sd_con(g: float) -> float:
        return float(avanzar_con_gamma(a_inicial, g, n_pasos).std())

    if sd_con(hi) > sd_objetivo:       # ni contrayendo al máximo se llega
        final = avanzar_con_gamma(a_inicial, hi, n_pasos)
        return hi, final, float(final.std() - sd_objetivo)
    if sd_con(lo) < sd_objetivo:       # ni expandiendo al máximo se llega
        final = avanzar_con_gamma(a_inicial, lo, n_pasos)
        return lo, final, float(final.std() - sd_objetivo)

    for _ in range(max_iter):
        med = 0.5 * (lo + hi)
        s = sd_con(med)
        if abs(s - sd_objetivo) < tol:
            break
        if s > sd_objetivo:
            lo = med
        else:
            hi = med
    med = 0.5 * (lo + hi)
    final = avanzar_con_gamma(a_inicial, med, n_pasos)
    return float(med), final, float(final.std() - sd_objetivo)


__all__ = [
    "ModeloForzado",
    "ajustar_gamma_por_tramo",
    "TraslacionModel",
    "ContraccionModel",
    "RuidoModel",
    "ajustar_u_por_tramo",
    "ajustar_u_lineal",
    "ajustar_u_secante",
    "phi_heterogeneo",
]
