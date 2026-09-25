"""¿Puede el criterio del piso de ruido (DI-V45) detectar señal territorial?

Evidencia de DI-V52. No usa datos del proyecto: arma una ciudad simulada con 20
localidades y un efecto por localidad de tamaño conocido, y le aplica dos
criterios.

1. **El del piso (DI-V45):** rehacer la población con 20 semillas, tomar la
   primera como «publicada» y declarar señal si supera el p95 de las 20. Es
   exactamente lo que hace `piso_territorial.py`.
2. **Permutación:** barajar la opinión entre agentes y ver si la dispersión
   entre localidades observada supera la del barajado.

Resultado esperado, y el que da: el criterio del piso «detecta» ~5 % de las
veces sea cual sea el efecto, incluso uno enorme, porque la corrida publicada
sale del mismo proceso que las semillas y su percentil es uniforme. La
permutación sí crece con el efecto.

Lo que esta simulación NO dice: si la población sintética real tiene o no
diferencias entre localidades. Con un donante sin localidad, las que tenga son
composición demográfica por construcción.

    python src/viz/simular_prueba_piso.py        # ~1 min
"""

from __future__ import annotations

import numpy as np

N_LOC, N_AGENTES, SD_DENTRO = 20, 1000, 0.85
SEMILLAS_PISO = 20
REPS_PISO, REPS_PERM, B_PERM = 200, 60, 200
EFECTOS = (0.0, 0.1, 0.2, 0.4, 0.8)


def sd_entre(op: np.ndarray, loc: np.ndarray) -> float:
    medias = [op[loc == l].mean() for l in range(N_LOC) if (loc == l).any()]
    return float(np.std(medias, ddof=1))


def corrida(efecto: np.ndarray, pesos: np.ndarray, rng) -> tuple[np.ndarray, np.ndarray]:
    loc = rng.choice(N_LOC, N_AGENTES, p=pesos)
    return efecto[loc] + rng.normal(0, SD_DENTRO, N_AGENTES), loc


def main() -> None:
    rng = np.random.default_rng(0)
    pesos = rng.dirichlet(np.ones(N_LOC) * 3)
    print(f"{'efecto (sd entre localidades)':>30} {'criterio del piso':>18} {'permutación':>12}")
    for sd_real in EFECTOS:
        efecto = rng.normal(0, sd_real, N_LOC) if sd_real else np.zeros(N_LOC)

        sale = []
        for rep in range(REPS_PISO):
            vals = np.array([sd_entre(*corrida(efecto, pesos, np.random.default_rng(rep * 100 + s)))
                             for s in range(SEMILLAS_PISO)])
            sale.append(vals[0] > np.percentile(vals, 95))

        detecta = []
        for rep in range(REPS_PERM):
            r = np.random.default_rng(10**6 + rep)
            op, loc = corrida(efecto, pesos, r)
            obs = sd_entre(op, loc)
            nulo = [sd_entre(r.permutation(op), loc) for _ in range(B_PERM)]
            detecta.append(np.mean(np.array(nulo) >= obs) < 0.05)

        print(f"{sd_real:>30.1f} {100*np.mean(sale):>17.0f}% {100*np.mean(detecta):>11.0f}%")


if __name__ == "__main__":
    main()
