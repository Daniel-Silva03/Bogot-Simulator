"""Pruebas de src/experiments/a08_paso0.py con datos simulados.

No necesita data/raw/: arma un receptor y un donante falsos con la misma forma
que los reales (sexo exacto; edad, estrato y educación como distancia; factores
de expansión desiguales) y verifica las tres cosas de las que depende el paso 0:

1. **El límite es el del hot-deck real.** Se compara contra el promedio de
   varias corridas de `hot_deck_match` —la función del proyecto, no una copia—
   sobre todo el receptor. Si el paso 0 reprodujera mal los empates o los pesos,
   estaría calculando el límite de otro método.
2. **El nulo de permutación puede fallar** y no falla de más: sin relación
   opinión-demografía rechaza cerca del 5 %; con relación, casi siempre. Es la
   propiedad que el piso por semillas de DI-V45 no tenía (DI-V52).
3. **La simulación con N finito converge al límite**, y con N chico está
   dominada por ruido.

    python tests/test_a08_paso0.py      # ~1 min
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.experiments.a08_paso0 import (construir_estructura, limite,
                                       nulo_permutacion, sd_entre,
                                       simular_n_finito)
from src.population.matching import hot_deck_match

EXACT = ["sexo"]
DIST = ["edad", "estrato", "educacion_match"]
N_LOC = 12


def _assert(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"  OK: {msg}")


def receptor_falso(n=6000, seed=0) -> pd.DataFrame:
    """Localidades con composición distinta: el estrato medio sube con el índice."""
    r = np.random.default_rng(seed)
    loc = r.integers(0, N_LOC, n)
    estrato = np.clip(np.round(1 + 4 * loc / (N_LOC - 1) + r.normal(0, 1, n)), 1, 6)
    return pd.DataFrame({
        "agent_id": np.arange(n),
        "localidad": [f"L{l:02d}" for l in loc],
        "sexo": r.choice(["F", "M"], n),
        "edad": r.integers(18, 80, n),
        "estrato": estrato,
        "educacion_match": np.clip(np.round(estrato / 1.5 + r.normal(0, 1, n)), 0, 4),
        "factor_expansion": r.gamma(2.0, 50.0, n),
    })


def donante_falso(n=900, efecto=0.25, seed=1) -> pd.DataFrame:
    """Opinión 1-5 que depende del estrato con fuerza `efecto` (0 = nada)."""
    r = np.random.default_rng(seed)
    estrato = r.integers(1, 7, n).astype(float)
    op = np.clip(np.round(3 - efecto * (estrato - 3.5) + r.normal(0, 0.9, n), 2), 1, 5)
    return pd.DataFrame({
        "sexo": r.choice(["F", "M"], n),
        # edad en bandas de 5 años: produce empates, como la EPC (DI-M1)
        "edad": 20 + 5 * r.integers(0, 12, n),
        "estrato": estrato,
        "educacion_match": r.integers(0, 5, n).astype(float),
        "opinion": op,
        "factor_expansion": r.gamma(1.5, 100.0, n),
    })


def test_limite_es_el_del_hot_deck_real():
    print("el límite coincide con el promedio de corridas de hot_deck_match")
    rec, don = receptor_falso(), donante_falso(efecto=0.4)
    e = construir_estructura(rec, don, "opinion", EXACT, DIST)
    mu = limite(e)
    corridas = []
    for s in range(30):
        m = hot_deck_match(rec, don, "opinion", exact_match_vars=EXACT,
                           distance_vars=DIST, random_state=s,
                           peso_col="factor_expansion").agentes
        m["w"] = rec["factor_expansion"].to_numpy()
        g = m.groupby("localidad").apply(lambda d: np.average(d["opinion"], weights=d["w"]))
        corridas.append(g.reindex(e.localidades).to_numpy())
    media = np.mean(corridas, axis=0)
    ee = np.std(corridas, axis=0, ddof=1) / np.sqrt(len(corridas))
    z = np.abs(media - mu) / ee
    _assert(np.max(z) < 4.5,
            f"todas las localidades dentro de 4,5 errores estándar (máx z = {np.max(z):.2f})")
    _assert(np.max(np.abs(media - mu)) < 0.02,
            f"diferencia máxima {np.max(np.abs(media - mu)):.4f} < 0,02 en escala 1-5")


def test_nulo_rechaza_lo_justo():
    print("el nulo de permutación puede fallar y no falla de más")
    rec = receptor_falso(seed=3)
    rechazos = {}
    for efecto in (0.0, 0.4):
        r = []
        for s in range(40):
            e = construir_estructura(rec, donante_falso(efecto=efecto, seed=100 + s),
                                     "opinion", EXACT, DIST)
            perm = nulo_permutacion(e, 99, np.random.default_rng(s))
            r.append(sd_entre(limite(e)) > np.percentile(perm, 95))
        rechazos[efecto] = float(np.mean(r))
    _assert(rechazos[0.0] <= 0.15,
            f"sin efecto rechaza {100 * rechazos[0.0]:.0f} % (esperado ~5 %, tope 15 %)")
    _assert(rechazos[0.4] >= 0.8,
            f"con efecto rechaza {100 * rechazos[0.4]:.0f} % (tiene que poder fallar)")


def test_n_finito_converge_al_limite():
    print("sd_entre con N finito baja hacia el límite")
    # Efecto chico, del orden del real (R² ≈ 0,02): con uno grande el límite
    # domina incluso a N chico y la prueba no distingue nada.
    e = construir_estructura(receptor_falso(n=8000, seed=5), donante_falso(efecto=0.08, seed=6),
                             "opinion", EXACT, DIST)
    s_lim = sd_entre(limite(e))
    rng = np.random.default_rng(0)
    med = {n: float(np.median(simular_n_finito(e, n, 30, rng))) for n in (500, 5_000, 200_000)}
    print(f"     S_lim = {s_lim:.3f}; " + ", ".join(f"N={n}: {v:.3f}" for n, v in med.items()))
    _assert(med[500] > med[5_000] > med[200_000], "la dispersión baja al crecer N")
    _assert(abs(med[200_000] - s_lim) < 0.2 * s_lim + 0.01,
            "con N grande la dispersión está en el límite (±20 %)")
    # sd_entre² ≈ S_lim² + ruido²: el exceso sobre el límite es el ruido de
    # la corrida, y tiene que ser grande con N chico y casi nulo con N grande.
    exceso = {n: v ** 2 - s_lim ** 2 for n, v in med.items()}
    _assert(exceso[500] > 5 * max(exceso[200_000], 0.0) and exceso[500] > 0.005,
            f"el ruido de la corrida (exceso de varianza) cae con N: "
            f"{exceso[500]:.4f} con N=500 contra {exceso[200_000]:.4f} con N=200.000")


if __name__ == "__main__":
    test_limite_es_el_del_hot_deck_real()
    test_nulo_rechaza_lo_justo()
    test_n_finito_converge_al_limite()
    print("\nTodos los tests pasaron.")
