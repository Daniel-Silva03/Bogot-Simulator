"""A08, paso 0 — ¿qué mostraría el mapa con 10.000 o 100.000 agentes?

Se responde sin construir ninguna población grande.

POR QUÉ EXISTE
--------------
A08 se venía justificando así: «con 1.000 agentes ninguna diferencia entre
localidades sobrevive al ruido; con 100.000 el error cae por √100». DI-V52
mostró dos cosas que cambian esa cuenta:

1. El donante (ECP) no registra la localidad. En la población sintética, la
   opinión solo puede diferir entre localidades por **composición
   demográfica**. Al escalar, cada localidad converge a un valor fijo —la
   mezcla de las opiniones del donante según su composición— y el mapa
   empezaría a verse «preciso» sobre algo que es construcción del método.
2. La incertidumbre de ese valor fijo viene del **donante** (unos pocos miles de
   encuestados) y no baja al escalar. El piso por semillas nunca la midió.

QUÉ CALCULA, POR AÑO
--------------------
- **El límite con N infinito.** El hot-deck (matching.py, DI-M1) asigna a cada
  receptor un donante sorteado entre los empatados a la distancia mínima dentro
  de su bloque de sexo, con probabilidad proporcional al factor de expansión
  del donante. Su esperanza por celda (sexo × edad × estrato × educación) es,
  entonces, una media ponderada exacta. Promediando esas esperanzas con los
  pesos FEX_C del receptor en cada localidad sale la media a la que converge
  cada localidad cuando N → ∞. `S_lim` es su dispersión entre localidades,
  medida igual que `sd_entre` en piso_territorial.py.
- **Nulo de permutación en el donante.** Se baraja la opinión entre donantes
  (se rompe opinión↔demografía, se conserva todo lo demás: composición del
  receptor, celdas, empates y pesos) y se recalcula `S_lim`. Responde: ¿la
  diferencia por composición supera la que produce el ruido del donante solo?
  A diferencia del piso por semillas, este nulo **sí puede fallar** (verificado
  en tests/test_a08_paso0.py).
- **Bootstrap del donante.** Intervalo de `S_lim` y de cada media de localidad
  por el hecho de que la encuesta entrevistó a esas personas y no a otras.
  Remuestreo simple: la ECP no publica variables de diseño (A19), así que este
  intervalo es **optimista** en un factor del orden de √DEFF.
- **Lo que se vería con N finito.** Se simula `sd_entre` con N = 1.000, 10.000
  y 100.000 agentes muestreando el receptor ∝ FEX_C y donando como el
  hot-deck. Muestra cuánto del mapa es ruido de una corrida y cuánto es el
  límite.

APROXIMACIONES, DICHAS
----------------------
- Muestreo del receptor con reemplazo ∝ FEX_C, no PPS sistemático (D14). En el
  límite dan lo mismo; con N finito la diferencia es de segundo orden.
- En el bootstrap, un donante repetido cuenta una vez como candidato con su peso
  multiplicado, en vez de ocupar varios de los `k_empates` puestos. Cambia algo
  solo cuando hay más de 50 empatados, y en el límite no cambia nada.

REGLA DE DECISIÓN — pre-registrada en claude/A08_PASO0_SPECIFICATION.md
---------------------------------------------------------------------
    python src/experiments/a08_paso0.py                 # los cinco años de la ECP
    python src/experiments/a08_paso0.py --anios 2021 --boot 50 --perm 50   # borrador

Necesita data/raw/ (receptor de Multipropósito y la ECP): corre en la máquina de
los microdatos, no en el PC del CNC. Salida: data/processed/a08/paso0.json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

DIR_RAW = RAIZ / "data" / "raw"
RECEPTOR = DIR_RAW / "em2021_receptor_v2.csv"
DIR_ECP = DIR_RAW / "ecp"
SALIDA = RAIZ / "data" / "processed" / "a08" / "paso0.json"

ANIOS = (2013, 2017, 2019, 2021, 2023)
TAMANOS = (1_000, 10_000, 100_000)
TOL_EMPATE = 1e-9          # la misma tolerancia que matching.py (DI-M1)
K_EMPATES = 50             # el mismo default que hot_deck_match

logger = logging.getLogger("a08_paso0")


# ---------------------------------------------------------------------------
# Estructura precalculada: celdas del receptor y sus vecinos en el donante
# ---------------------------------------------------------------------------

@dataclass
class Estructura:
    localidades: list[str]
    pesos_loc_celda: np.ndarray    # (L, C) suma de FEX_C del receptor
    vecinos_idx: np.ndarray        # (C, K) posiciones en el donante; -1 = hueco
    vecinos_dist: np.ndarray       # (C, K) distancia; inf en los huecos
    peso_donante: np.ndarray       # (D,) factor de expansión del donante
    opinion: np.ndarray            # (D,)

    @property
    def n_celdas(self) -> int:
        return self.vecinos_idx.shape[0]


def construir_estructura(
    receptor: pd.DataFrame,
    donante: pd.DataFrame,
    opinion_col: str,
    exact_vars: list[str],
    distance_vars: list[str],
    peso_receptor: str = "factor_expansion",
    peso_donante: str = "factor_expansion",
    k_empates: int = K_EMPATES,
) -> Estructura:
    """Reproduce la búsqueda de vecinos de `hot_deck_match` una vez por celda.

    Misma estandarización (media y sd del donante tras quitar faltantes), mismo
    bloque exacto, mismo `NearestNeighbors` ajustado sobre el bloque en el mismo
    orden de filas: así los `k` vecinos que se guardan son los mismos que vería
    el hot-deck. No implementa la escalera de relajación: con `sexo` como único
    bloque exacto, todo receptor tiene donantes en el nivel 0; si no los
    tuviera, falla con un error en vez de aproximar.
    """
    donante = donante.dropna(subset=distance_vars + [opinion_col]).reset_index(drop=True)
    receptor = receptor.dropna(subset=exact_vars + distance_vars + [peso_receptor, "localidad"])
    ref_mean = donante[distance_vars].mean()
    ref_std = donante[distance_vars].std().replace(0, 1.0)

    celda_vars = exact_vars + distance_vars
    celdas = receptor[celda_vars].drop_duplicates().reset_index(drop=True)
    celdas["_c"] = np.arange(len(celdas))
    rec = receptor.merge(celdas, on=celda_vars, how="left", validate="many_to_one")

    localidades = sorted(rec["localidad"].unique())
    loc_pos = {l: i for i, l in enumerate(localidades)}
    pesos = np.zeros((len(localidades), len(celdas)))
    np.add.at(pesos, (rec["localidad"].map(loc_pos).to_numpy(), rec["_c"].to_numpy()),
              rec[peso_receptor].to_numpy(float))

    k = int(k_empates)
    idx = np.full((len(celdas), k), -1, dtype=int)
    dist = np.full((len(celdas), k), np.inf)
    celdas_std = ((celdas[distance_vars] - ref_mean) / ref_std).to_numpy(float)
    donante_std = ((donante[distance_vars] - ref_mean) / ref_std).to_numpy(float)
    clave_d = donante[exact_vars].astype(str).agg("|".join, axis=1).to_numpy()
    clave_c = celdas[exact_vars].astype(str).agg("|".join, axis=1).to_numpy()
    for clave in pd.unique(clave_c):
        mask_d = clave_d == clave
        if not mask_d.any():
            raise RuntimeError(f"El bloque exacto {clave!r} no tiene donantes; "
                               "el paso 0 no implementa la relajación.")
        filas = np.where(clave_c == clave)[0]
        pos_d = np.where(mask_d)[0]
        kk = min(k, len(pos_d))
        nn = NearestNeighbors(n_neighbors=kk).fit(donante_std[mask_d])
        d_, i_ = nn.kneighbors(celdas_std[filas])
        idx[filas, :kk] = pos_d[i_]
        dist[filas, :kk] = d_

    return Estructura(
        localidades=localidades,
        pesos_loc_celda=pesos,
        vecinos_idx=idx,
        vecinos_dist=dist,
        peso_donante=pd.to_numeric(donante[peso_donante], errors="coerce").fillna(0).to_numpy(float),
        opinion=donante[opinion_col].to_numpy(float),
    )


# ---------------------------------------------------------------------------
# Esperanza del hot-deck y medias por localidad
# ---------------------------------------------------------------------------

def pesos_empatados(e: Estructura, multiplicidad: np.ndarray | None = None) -> np.ndarray:
    """(C, K): peso de cada vecino en el sorteo del hot-deck; 0 si no compite.

    Con `multiplicidad` (bootstrap), un donante ausente no compite y uno
    repetido pesa su FEX por el número de copias.
    """
    valido = e.vecinos_idx >= 0
    idx = np.where(valido, e.vecinos_idx, 0)
    m = np.ones(len(e.opinion)) if multiplicidad is None else multiplicidad
    presente = valido & (m[idx] > 0)
    dist = np.where(presente, e.vecinos_dist, np.inf)
    dmin = dist.min(axis=1, keepdims=True)
    if not np.isfinite(dmin).all():
        # los K vecinos quedaron fuera del remuestreo: probabilidad despreciable
        # con K = 50, pero se reporta en vez de esconderse
        raise RuntimeError("una celda se quedó sin vecinos en el remuestreo")
    empatado = presente & (dist <= dmin + TOL_EMPATE)
    w = np.where(empatado, e.peso_donante[idx] * m[idx], 0.0)
    # DI-M1: si los empatados suman peso 0, el hot-deck sortea uniforme
    sin_peso = w.sum(axis=1) == 0
    w[sin_peso] = empatado[sin_peso].astype(float)
    return w


def esperanza_por_celda(e: Estructura, w: np.ndarray, opinion: np.ndarray | None = None) -> np.ndarray:
    op = e.opinion if opinion is None else opinion
    idx = np.where(e.vecinos_idx >= 0, e.vecinos_idx, 0)
    return (w * op[idx]).sum(axis=1) / w.sum(axis=1)


def medias_localidad(e: Estructura, esperanza: np.ndarray) -> np.ndarray:
    return (e.pesos_loc_celda @ esperanza) / e.pesos_loc_celda.sum(axis=1)


def sd_entre(medias: np.ndarray) -> float:
    """La misma estadística que piso_territorial.sd_entre_de: sd sin ponderar."""
    m = medias[np.isfinite(medias)]
    return float(np.std(m, ddof=1))


# ---------------------------------------------------------------------------
# Las tres piezas
# ---------------------------------------------------------------------------

def limite(e: Estructura) -> np.ndarray:
    return medias_localidad(e, esperanza_por_celda(e, pesos_empatados(e)))


def nulo_permutacion(e: Estructura, n: int, rng) -> np.ndarray:
    """S_lim con la opinión barajada entre donantes. Empates y pesos intactos."""
    w = pesos_empatados(e)
    return np.array([sd_entre(medias_localidad(e, esperanza_por_celda(e, w, rng.permutation(e.opinion))))
                     for _ in range(n)])


def bootstrap_donante(e: Estructura, n: int, rng) -> np.ndarray:
    """(n, L): medias límite por localidad con el donante remuestreado."""
    D = len(e.opinion)
    out = np.empty((n, len(e.localidades)))
    for b in range(n):
        m = np.bincount(rng.integers(0, D, D), minlength=D).astype(float)
        out[b] = medias_localidad(e, esperanza_por_celda(e, pesos_empatados(e, m)))
    return out


def simular_n_finito(e: Estructura, n_agentes: int, reps: int, rng) -> np.ndarray:
    """sd_entre de `reps` corridas con N agentes, donando como el hot-deck."""
    w = pesos_empatados(e)
    # sorteo vectorizado del donante: cada celda ocupa el segmento [c, c+1)
    # de una acumulada global
    acum = np.cumsum(w / w.sum(axis=1, keepdims=True), axis=1)
    # No se fuerza el último a 1: los huecos y los no empatados repiten el
    # valor anterior, y un sorteo cerca de 1 caería en ellos. Se escala el
    # uniforme al total real de la fila y `side="right"` elige siempre el
    # primer vecino con peso positivo que lo supera.
    total_fila = acum[:, -1].copy()
    acum_global = (acum + np.arange(e.n_celdas)[:, None]).ravel()
    idx_plano = np.where(e.vecinos_idx >= 0, e.vecinos_idx, 0).ravel()

    p_cel = e.pesos_loc_celda.ravel() / e.pesos_loc_celda.sum()
    L, C = e.pesos_loc_celda.shape
    out = np.empty(reps)
    for r in range(reps):
        cel = rng.choice(L * C, size=n_agentes, p=p_cel)
        loc, c = np.divmod(cel, C)
        u = rng.random(n_agentes) * total_fila[c]
        pos = np.searchsorted(acum_global, c + u, side="right")
        op = e.opinion[idx_plano[pos]]
        suma = np.bincount(loc, weights=op, minlength=L)
        cuenta = np.bincount(loc, minlength=L)
        with np.errstate(invalid="ignore", divide="ignore"):
            out[r] = sd_entre(np.where(cuenta > 0, suma / cuenta, np.nan))
    return out


def analizar(e: Estructura, n_boot: int, n_perm: int, reps: int, tamanos, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    mu = limite(e)
    s_lim = sd_entre(mu)
    perm = nulo_permutacion(e, n_perm, rng)
    boot = bootstrap_donante(e, n_boot, rng)
    s_boot = np.array([sd_entre(b) for b in boot])
    ciudad = float((e.pesos_loc_celda.sum(axis=1) @ mu) / e.pesos_loc_celda.sum())
    finito = {int(n): simular_n_finito(e, int(n), reps, rng) for n in tamanos}
    p_perm = float((1 + (perm >= s_lim).sum()) / (1 + len(perm)))
    return {
        "n_celdas": int(e.n_celdas),
        "n_donantes": int(len(e.opinion)),
        "media_ciudad_limite": round(ciudad, 4),
        "S_lim": round(s_lim, 4),
        "S_lim_boot_ic95": [round(float(np.percentile(s_boot, 2.5)), 4),
                            round(float(np.percentile(s_boot, 97.5)), 4)],
        "nulo_perm_mediana": round(float(np.median(perm)), 4),
        "nulo_perm_p95": round(float(np.percentile(perm, 95)), 4),
        "p_perm": round(p_perm, 4),
        "supera_nulo": bool(s_lim > np.percentile(perm, 95)),
        "sd_entre_por_N": {str(n): {"mediana": round(float(np.median(v)), 4),
                                    "p05": round(float(np.percentile(v, 5)), 4),
                                    "p95": round(float(np.percentile(v, 95)), 4)}
                           for n, v in finito.items()},
        "por_localidad": {
            l: {"media_limite": round(float(mu[i]), 4),
                "dif_ciudad": round(float(mu[i] - ciudad), 4),
                "ic95_boot": [round(float(np.percentile(boot[:, i], 2.5)), 4),
                              round(float(np.percentile(boot[:, i], 97.5)), 4)]}
            for i, l in enumerate(e.localidades)},
        "n_boot": n_boot, "n_perm": n_perm, "reps_por_N": reps,
    }


# ---------------------------------------------------------------------------
# Datos reales
# ---------------------------------------------------------------------------

def cargar(anio: int) -> Estructura:
    from src.population.construir_poblacion import (DISTANCE_VARS_ECP,
                                                     EXACT_MATCH_VARS_ECP)
    from src.population.ecp import (COLUMNA_EDUCACION_MATCH, COLUMNA_OPINION_ECP,
                                    armonizar_educacion_proyecto, donante_ecp)
    from src.population.loader import load_multiproposito_receptor

    receptor = load_multiproposito_receptor(RECEPTOR)
    if "factor_expansion" not in receptor.columns:
        raise RuntimeError("el receptor no trae factor_expansion (FEX_C); ver D14")
    receptor[COLUMNA_EDUCACION_MATCH] = armonizar_educacion_proyecto(receptor["nivel_educativo"])
    donante = donante_ecp(DIR_ECP, anio)
    return construir_estructura(receptor, donante, COLUMNA_OPINION_ECP,
                                EXACT_MATCH_VARS_ECP, DISTANCE_VARS_ECP)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--anios", type=int, nargs="+", default=list(ANIOS))
    ap.add_argument("--boot", type=int, default=200)
    ap.add_argument("--perm", type=int, default=200)
    ap.add_argument("--reps", type=int, default=50, help="corridas simuladas por tamaño")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.WARNING, format="%(levelname)-8s %(message)s")

    faltan = [p for p in (RECEPTOR, DIR_ECP) if not p.exists()]
    if faltan:
        print("Faltan datos de data/raw/ — este script corre en la máquina de los microdatos:")
        for p in faltan:
            print(f"  {p.relative_to(RAIZ)}")
        print("Ver 'python src/utils/revisar_datos.py'.")
        return 1

    salida = {"descripcion": __doc__.splitlines()[0], "tamanos": list(TAMANOS), "por_anio": {}}
    print(f"{'año':>5} {'S_lim':>7} {'IC boot':>15} {'nulo p95':>9} {'p':>6} {'¿supera?':>9}   "
          + "  ".join(f"N={n:>7,}".replace(",", ".") for n in TAMANOS))
    for anio in args.anios:
        t0 = time.time()
        r = analizar(cargar(anio), args.boot, args.perm, args.reps, TAMANOS, args.seed + anio)
        salida["por_anio"][str(anio)] = r
        fin = "  ".join(f"{r['sd_entre_por_N'][str(n)]['mediana']:>9.3f}" for n in TAMANOS)
        print(f"{anio:>5} {r['S_lim']:>7.3f} "
              f"{r['S_lim_boot_ic95'][0]:>7.3f}–{r['S_lim_boot_ic95'][1]:.3f} "
              f"{r['nulo_perm_p95']:>9.3f} {r['p_perm']:>6.3f} "
              f"{'SÍ' if r['supera_nulo'] else 'no':>9}   {fin}   ({time.time() - t0:.0f} s)")

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nS_lim: dispersión entre localidades con N infinito (solo composición).")
    print(f"nulo p95: la que produce el ruido del donante sin relación opinión-demografía.")
    print(f"N=…: mediana de sd_entre que se vería en el mapa con ese número de agentes.")
    print(f"\n{SALIDA.relative_to(RAIZ).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
