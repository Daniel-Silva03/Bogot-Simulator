"""Pruebas de src/experiments/a08_paso0b.py con una EPC simulada.

Tres mundos donde la respuesta se conoce de antemano:

1. **Solo composición.** La opinión depende del estrato y nada más; las
   localidades difieren en su mezcla de estratos. La composición tiene que
   predecir la diferencia real: R ≈ 1, r alto.
2. **La composición exagera.** Además, un efecto de localidad que va **en contra**
   de la composición (las personas de un mismo perfil opinan distinto según
   dónde viven, y compensan). R tiene que salir claramente < 1.
3. **No hay territorio.** Todas las localidades con la misma mezcla y sin
   efecto propio. La dispersión corregida tiene que ser ~0, y la permutación
   no debe encontrar territorio más allá de lo esperado por azar.

Un n chico por localidad (~80, como la EPC) hace que cada ola sea ruidosa; por
eso se mira la mediana sobre varias olas simuladas.

    python tests/test_a08_paso0b.py      # ~1-2 min
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from src.experiments.a08_paso0b import Ola, analizar_ola

N_LOC, N_POR_LOC = 19, 80


def _assert(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"  OK: {msg}")


def ola_simulada(seed: int, efecto_estrato: float, contexto: float, mezcla: bool = True) -> Ola:
    """`contexto` multiplica un efecto de localidad proporcional (y de signo
    contrario, si es negativo) a la desviación compositiva de esa localidad."""
    r = np.random.default_rng(seed)
    loc = np.repeat(np.arange(1, N_LOC + 1), N_POR_LOC)
    centro = np.linspace(1.5, 5.0, N_LOC) if mezcla else np.full(N_LOC, 3.2)
    estrato = np.clip(np.round(centro[loc - 1] + r.normal(0, 1.0, len(loc))), 1, 6).astype(int)
    sexo = r.integers(1, 3, len(loc))
    edad = r.integers(1, 6, len(loc))
    comp_loc = efecto_estrato * (centro - centro.mean())
    y = 3 + efecto_estrato * (estrato - 3.3) + contexto * comp_loc[loc - 1] + r.normal(0, 1.1, len(loc))
    y = np.clip(np.round(y), 1, 5)
    w = r.gamma(3.0, 1.0, len(loc))
    s, e = sexo.astype(str), edad.astype(str)
    return Ola(anio=seed, loc=loc,
               celda=np.char.add(np.char.add(np.char.add(s, "|"), np.char.add(e, "|")), estrato.astype(str)),
               celda_gruesa=np.char.add(np.char.add(s, "|"), e),
               y=y.astype(float), w=w)


def _mediana(campo: str, olas: list[dict]) -> float:
    return float(np.median([o[campo] for o in olas if o[campo] is not None]))


def correr(efecto, contexto, mezcla=True, reps=12):
    return [analizar_ola(ola_simulada(100 + k, efecto, contexto, mezcla), 60, 99,
                         np.random.default_rng(k)) for k in range(reps)]


def test_solo_composicion():
    print("solo composición: la predicción coincide con lo medido")
    olas = correr(0.25, 0.0)
    R, r = _mediana("R", olas), _mediana("r", olas)
    print(f"     R mediana = {R:.2f}, r mediana = {r:.2f}")
    _assert(0.75 <= R <= 1.33, "R cerca de 1")
    _assert(r > 0.6, "la composición apunta a las mismas localidades")


def test_composicion_exagera():
    print("contexto opuesto: el script detecta que la composición exagera")
    olas = correr(0.25, -0.6)
    R = _mediana("R", olas)
    # No sale 0,4: las celdas se estiman con datos que ya traen el contexto
    # mezclado, así que la composición estimada también queda atenuada. El
    # pipeline real hace lo mismo con el donante, así que R mide justo la
    # discrepancia que tendría el mapa.
    print(f"     R mediana = {R:.2f} (el contexto por sí solo daría 0,4; ver comentario)")
    _assert(R < 0.67, "R claramente por debajo de 1")


def test_sin_territorio():
    print("sin territorio: la dispersión corregida se va a ~0 y la permutación calla")
    olas = correr(0.25, 0.0, mezcla=False)
    sd = _mediana("sd_obs", olas)
    crudo = _mediana("sd_obs_crudo", olas)
    rechazos = np.mean([o["p_territorio"] < 0.05 for o in olas])
    print(f"     sd corregida mediana = {sd:.3f} (cruda {crudo:.3f}); rechazos {100 * rechazos:.0f} %")
    _assert(sd < 0.5 * crudo, "la corrección quita el grueso de la dispersión cruda")
    _assert(rechazos <= 0.25, "la permutación no inventa territorio")


if __name__ == "__main__":
    test_solo_composicion()
    test_composicion_exagera()
    test_sin_territorio()
    print("\nTodos los tests pasaron.")
