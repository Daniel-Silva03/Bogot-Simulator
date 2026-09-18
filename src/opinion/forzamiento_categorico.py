"""
src/opinion/forzamiento_categorico.py

Forzamiento exógeno para variables **ordinales de pocas categorías**, que es
lo que son casi todos los ítems de encuesta del proyecto.

POR QUÉ EXISTE
--------------
El forzamiento que el proyecto venía usando es **afín**: `a -> m + s(a - m0)`.
Contra una variable continua está bien. Contra una de cinco categorías es un
error de especificación: con `u != 0` saca los cinco picos enteros de la
grilla y los deja entre valores que la escala no puede tomar. Ninguna persona
respondió 2,37.

`claude/ANALISIS_TERCERA_PERILLA.md` midió lo que eso cuesta. Un forzamiento
que respeta la grilla —el más tosco posible, saltos de +-1— deja el error en
**1,2171** donde el afín daba 2,6590, el afín con ruido 2,3132 y el mejor de
los 33 modelos del Experimento 7 daba 2,4260. **La mitad**, con un parámetro
menos.

Este módulo es la versión bien hecha de eso.

QUÉ HACE
--------
Dada la distribución actual sobre las categorías y dos momentos objetivo,
encuentra la distribución sobre **las mismas categorías** que los acierta y
que es la más cercana a la actual, y reparte los agentes en ella.

    p (actual) + (media*, sd*)  ->  q (objetivo, en la grilla)  ->  agentes

DECISIONES DE IMPLEMENTACIÓN
============================

DI-G1. **El método por defecto es el ladeo exponencial** (*exponential
    tilting*): `q_k ∝ p_k · exp(λ1·k + λ2·k²)`. Dos parámetros para dos
    momentos, igual que el afín. Se elige por tres propiedades, no por
    conveniencia:

    - Es la distribución de **máxima entropía** entre las que cumplen las
      restricciones, es decir, la que menos información añade sobre la
      actual. Para un motor de escenarios eso es exactamente lo que se
      quiere: el escenario declara dos momentos y el resto no se inventa.
    - **Preserva los ceros.** Una categoría que nadie eligió sigue vacía.
    - Con λ2 = 0 es un cambio de razón de verosimilitud monótona, o sea
      **preserva el orden estocástico**: subir el nivel no puede aumentar la
      masa en la categoría más baja.

DI-G2. **Alternativa: transporte de mínimo movimiento**, un programa lineal
    que minimiza W1(p, q) sujeto a los momentos. El ladeo minimiza
    información; el transporte minimiza masa movida. No son lo mismo y
    ninguno domina: se exponen los dos y `comparar()` los mide sobre datos.
    La variante de transporte es un LP genuino —la restricción de varianza
    es lineal en q una vez fijada la media— y no una aproximación.

DI-G3. **Los agentes se reparten preservando el rango.** El agente que
    estaba más arriba sigue más arriba. Es la misma propiedad que tiene el
    forzamiento afín, así que la comparación entre los dos es limpia; y sin
    un mecanismo que justifique los cruces, inventarlos sería agregar
    dinámica social por la puerta de atrás — justo lo que siete experimentos
    dicen que no está identificado. `modo="aleatorio"` existe para quien
    quiera lo contrario, y hay que pedirlo.

DI-G4. **La factibilidad se verifica y se informa, no se fuerza en
    silencio.** En una grilla acotada no todo par (media, sd) es alcanzable:
    fijada la media, la varianza tiene un máximo (la distribución de dos
    puntos en los extremos) y un mínimo (concentrar en las categorías
    vecinas a la media). Si el objetivo cae fuera, se levanta
    `ForzamientoInfactible` con el rango alcanzable; con
    `proyectar=True` se usa la varianza alcanzable más cercana y se deja
    constancia. Un motor de escenarios tiene que poder decirle al usuario
    "esa combinación no existe en esta escala" en vez de devolver algo.

DI-G5. **Solo se piden dos momentos.** La tercera perilla del proyecto —la
    forma derivada del nivel— **no entra aquí**: este módulo mueve la
    distribución a los momentos pedidos, y quien los pide es el motor de
    escenarios. Mezclar las dos cosas haría imposible medir cuál aporta qué.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence

import numpy as np

TOL_MOMENTO = 1e-8


class ForzamientoError(ValueError):
    """Los insumos no permiten construir el forzamiento."""


class ForzamientoInfactible(ForzamientoError):
    """Los momentos pedidos no son alcanzables en esta grilla (DI-G4)."""


@dataclass
class Resultado:
    q: np.ndarray                    # distribución objetivo sobre la grilla
    categorias: np.ndarray
    media: float
    sd: float
    err_media: float
    err_sd: float
    metodo: str
    parametros: dict = field(default_factory=dict)
    notas: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        return (f"{self.metodo}: media {self.media:.4f} (err {self.err_media:+.2e}) "
                f"sd {self.sd:.4f} (err {self.err_sd:+.2e})")


# --------------------------------------------------------------------------
# Utilidades

def _normalizar(p: Sequence[float]) -> np.ndarray:
    p = np.asarray(p, dtype=float)
    if p.ndim != 1 or len(p) < 2:
        raise ForzamientoError("La distribución tiene que ser un vector de 2 o más categorías.")
    if np.any(p < -1e-12) or not np.isfinite(p).all():
        raise ForzamientoError("La distribución tiene valores negativos o no finitos.")
    p = np.clip(p, 0.0, None)
    total = p.sum()
    if total <= 0:
        raise ForzamientoError("La distribución suma cero.")
    return p / total


def momentos(q: np.ndarray, k: np.ndarray) -> tuple[float, float]:
    m = float(np.dot(q, k))
    return m, float(np.sqrt(max(np.dot(q, (k - m) ** 2), 0.0)))


def distribucion_de(a: Sequence[float], categorias: Sequence[float],
                    pesos: Optional[Sequence[float]] = None) -> np.ndarray:
    """Distribución empírica de un vector de agentes sobre la grilla."""
    a = np.asarray(a, dtype=float)
    k = np.asarray(categorias, dtype=float)
    w = np.ones_like(a) if pesos is None else np.asarray(pesos, dtype=float)
    idx = np.abs(a[:, None] - k[None, :]).argmin(axis=1)
    if not np.allclose(k[idx], a, atol=1e-9):
        fuera = np.unique(a[~np.isclose(k[idx], a, atol=1e-9)])
        raise ForzamientoError(
            f"Hay valores fuera de la grilla {list(k)}: {list(fuera[:8])}. "
            "Este forzamiento es para variables categóricas; para una continua "
            "usar src/opinion/forzamiento.py.")
    q = np.bincount(idx, weights=w, minlength=len(k)).astype(float)
    return q / q.sum()


# --------------------------------------------------------------------------
# Factibilidad (DI-G4)

def rango_de_sd(k: Sequence[float], media: float) -> tuple[float, float]:
    """Desviaciones estándar mínima y máxima alcanzables en la grilla, dada la media.

    El máximo es la distribución de dos puntos en los extremos que da esa
    media; el mínimo concentra en las dos categorías que la rodean.
    """
    k = np.asarray(k, dtype=float)
    lo, hi = float(k.min()), float(k.max())
    if not (lo - 1e-12 <= media <= hi + 1e-12):
        raise ForzamientoInfactible(
            f"La media {media:.4f} está fuera de la grilla [{lo}, {hi}].")
    media = float(np.clip(media, lo, hi))
    # máximo: masa en los extremos
    t = 0.0 if hi == lo else (media - lo) / (hi - lo)
    var_max = t * (hi - media) ** 2 + (1 - t) * (media - lo) ** 2
    # mínimo: masa en las dos categorías vecinas
    j = int(np.searchsorted(k, media))
    if j == 0 or j >= len(k):
        var_min = 0.0
    else:
        a_, b_ = k[j - 1], k[j]
        u = 0.0 if b_ == a_ else (media - a_) / (b_ - a_)
        var_min = u * (b_ - media) ** 2 + (1 - u) * (media - a_) ** 2
    return float(np.sqrt(max(var_min, 0.0))), float(np.sqrt(max(var_max, 0.0)))


def _verificar(k, media_obj, sd_obj, proyectar):
    lo, hi = rango_de_sd(k, media_obj)
    notas = []
    if sd_obj < lo - 1e-9 or sd_obj > hi + 1e-9:
        if not proyectar:
            raise ForzamientoInfactible(
                f"Con media {media_obj:.4f} en la grilla {list(np.asarray(k, float))}, "
                f"la desviación estándar alcanzable va de {lo:.4f} a {hi:.4f}; "
                f"se pidió {sd_obj:.4f}. Pasar proyectar=True para usar la más cercana.")
        nuevo = float(np.clip(sd_obj, lo, hi))
        notas.append(f"sd objetivo {sd_obj:.4f} infactible; proyectada a {nuevo:.4f} "
                     f"(rango alcanzable {lo:.4f}-{hi:.4f}).")
        sd_obj = nuevo
    return sd_obj, notas


# --------------------------------------------------------------------------
# Método 1 — ladeo exponencial (DI-G1)

def ladeo(p: Sequence[float], categorias: Sequence[float],
          media_obj: float, sd_obj: float, proyectar: bool = False) -> Resultado:
    """q_k ∝ p_k · exp(λ1·k + λ2·k²), con λ resuelto para acertar los momentos."""
    p = _normalizar(p)
    k = np.asarray(categorias, dtype=float)
    if len(k) != len(p):
        raise ForzamientoError("La grilla y la distribución no tienen el mismo largo.")
    sd_obj, notas = _verificar(k, media_obj, sd_obj, proyectar)

    activos = p > 0
    kc = k - k.mean()                     # centrar mejora el condicionamiento

    def q_de(lam):
        e = lam[0] * kc + lam[1] * kc ** 2
        e = e - e[activos].max()          # estabilidad numérica
        w = np.where(activos, p * np.exp(e), 0.0)
        return w / w.sum()

    def residuo(lam):
        q = q_de(lam)
        m, s = momentos(q, k)
        return np.array([m - media_obj, s ** 2 - sd_obj ** 2])

    from scipy.optimize import root
    mejor, mejor_err = None, np.inf
    for x0 in ((0.0, 0.0), (0.5, -0.1), (-0.5, 0.1), (0.0, 0.3), (0.0, -0.3)):
        try:
            r = root(residuo, x0=np.array(x0), method="hybr", tol=1e-12)
        except Exception:                                   # noqa: BLE001
            continue
        err = float(np.abs(residuo(r.x)).max())
        if err < mejor_err:
            mejor, mejor_err = r.x, err
        if mejor_err < TOL_MOMENTO:
            break

    if mejor is None:
        raise ForzamientoError("El ladeo no convergió desde ninguno de los arranques.")
    q = q_de(mejor)
    m, s = momentos(q, k)
    if mejor_err > 1e-6:
        notas.append(f"El ladeo convergió con error {mejor_err:.2e}: los momentos "
                     "pedidos están cerca del borde de lo alcanzable.")
    return Resultado(q=q, categorias=k, media=m, sd=s,
                     err_media=m - media_obj, err_sd=s - sd_obj,
                     metodo="ladeo", parametros={"lambda1": float(mejor[0]),
                                                 "lambda2": float(mejor[1])},
                     notas=notas)


# --------------------------------------------------------------------------
# Método 2 — transporte de mínimo movimiento (DI-G2)

def transporte(p: Sequence[float], categorias: Sequence[float],
               media_obj: float, sd_obj: float, proyectar: bool = False) -> Resultado:
    """q que minimiza W1(p, q) sujeto a los dos momentos. Es un LP exacto."""
    p = _normalizar(p)
    k = np.asarray(categorias, dtype=float)
    if len(k) != len(p):
        raise ForzamientoError("La grilla y la distribución no tienen el mismo largo.")
    sd_obj, notas = _verificar(k, media_obj, sd_obj, proyectar)
    n = len(k)
    anchos = np.diff(k)

    # Variables: q (n) y t (n-1) con t_j >= |P_j - Q_j|.
    # W1 = sum_j anchos_j * |P_j - Q_j|, con P, Q las acumuladas.
    from scipy.optimize import linprog
    c = np.concatenate([np.zeros(n), anchos])
    L = np.tril(np.ones((n - 1, n)), 0)[:, :n]      # Q_j = suma de q_0..q_j
    P_acum = np.cumsum(p)[:-1]
    A_ub = np.vstack([np.hstack([L, -np.eye(n - 1)]),
                      np.hstack([-L, -np.eye(n - 1)])])
    b_ub = np.concatenate([P_acum, -P_acum])
    A_eq = np.vstack([
        np.concatenate([np.ones(n), np.zeros(n - 1)]),
        np.concatenate([k, np.zeros(n - 1)]),
        np.concatenate([(k - media_obj) ** 2, np.zeros(n - 1)]),
    ])
    b_eq = np.array([1.0, media_obj, sd_obj ** 2])
    bounds = [(0, None)] * n + [(0, None)] * (n - 1)

    r = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                bounds=bounds, method="highs")
    if not r.success:
        raise ForzamientoInfactible(
            f"El transporte no encontró solución: {r.message}. "
            "Suele significar que los momentos no son alcanzables en la grilla.")
    q = np.clip(r.x[:n], 0, None)
    q = q / q.sum()
    m, s = momentos(q, k)
    return Resultado(q=q, categorias=k, media=m, sd=s,
                     err_media=m - media_obj, err_sd=s - sd_obj,
                     metodo="transporte", parametros={"w1": float(r.fun)},
                     notas=notas)


# --------------------------------------------------------------------------
# Repartir los agentes (DI-G3)

def repartir(a: Sequence[float], res: Resultado, modo: str = "rango",
             rng: Optional[np.random.Generator] = None) -> np.ndarray:
    """Asigna a cada agente su nueva categoría de modo que se cumpla `res.q`.

    `modo="rango"` (por defecto) preserva el orden: el agente que estaba más
    arriba queda más arriba. `modo="aleatorio"` reparte al azar.
    """
    a = np.asarray(a, dtype=float)
    n = len(a)
    k, q = res.categorias, res.q
    # Cuántos agentes van a cada categoría, con el reparto de restos más grande
    exacto = q * n
    cupos = np.floor(exacto).astype(int)
    faltan = n - cupos.sum()
    if faltan > 0:
        orden = np.argsort(-(exacto - cupos))
        cupos[orden[:faltan]] += 1

    salida = np.empty(n, dtype=float)
    if modo == "rango":
        if rng is None:
            rng = np.random.default_rng(0)
        # desempate estable entre agentes con el mismo valor
        orden = np.lexsort((rng.random(n), a))
        pos = 0
        for j, c in enumerate(cupos):
            if c:
                salida[orden[pos:pos + c]] = k[j]
                pos += c
    elif modo == "aleatorio":
        if rng is None:
            raise ForzamientoError("modo='aleatorio' necesita un rng explícito.")
        destinos = np.repeat(k, cupos)
        salida = rng.permutation(destinos)
    else:
        raise ForzamientoError("modo debe ser 'rango' o 'aleatorio'.")
    return salida


def forzar(a: Sequence[float], categorias: Sequence[float],
           media_obj: float, sd_obj: float, metodo: str = "ladeo",
           modo: str = "rango", proyectar: bool = False,
           pesos: Optional[Sequence[float]] = None,
           rng: Optional[np.random.Generator] = None) -> tuple[np.ndarray, Resultado]:
    """Camino completo: agentes -> distribución -> momentos objetivo -> agentes."""
    p = distribucion_de(a, categorias, pesos)
    f = {"ladeo": ladeo, "transporte": transporte}.get(metodo)
    if f is None:
        raise ForzamientoError("metodo debe ser 'ladeo' o 'transporte'.")
    res = f(p, categorias, media_obj, sd_obj, proyectar=proyectar)
    return repartir(a, res, modo=modo, rng=rng), res
