"""
Geografía electoral: ¿la composición de cada localidad explica cómo vota?

Pre-registro: `docs/GEOGRAFIA_ELECTORAL_SPECIFICATION.md` (con la enmienda 1).
Este módulo ejecuta lo pre-registrado; no decide nada que el documento no haya
decidido.

    proporción de voto por localidad  ~  composición (Multipropósito 2021)
    R² fuera de muestra (dejando una localidad fuera) + permutación
    residuos: ¿se repiten entre elecciones?  ¿siguen a la inscripción?

Uso (después de que `tests/test_geografia_electoral.py` pase, §4.1):
    python src/experiments/geografia_electoral.py

Escribe `data/processed/geografia_electoral/resultado.json`.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-GE1. **El R² fuera de muestra se calcula cerrado, con la matriz sombrero.**
    PRESS = Σ (e_i / (1 − h_ii))², que es exactamente lo que da reajustar 19
    veces dejando una localidad fuera, sin reajustar. La prueba lo compara con el
    bucle explícito.

DI-GE2. **La permutación es de una cola y con corrección +1.** p = (1 + #{R²_perm ≥
    R²_obs}) / (1 + n). Lo mismo para la persistencia, con r. Ninguna p sale 0.

DI-GE3. **Los nueve resultados se validan contra su definición.** El pre-registro
    los define como «los tres con más votos en Bogotá cada año», y la lista del
    código se comprueba contra la tabla en cada corrida: si no coincide, se detiene.

DI-GE4. **Sumapaz se predice, no se ajusta.** Sale del ajuste (§3.3) y se reporta
    cuánto se aleja de lo que M1 predice para ella con el ajuste de las otras 19.

DI-GE5. **Las localidades se cruzan por código**, no por nombre: el voto trae
    `cod_loc` y la composición se lleva a código con el marginal del proyecto,
    comparando nombres normalizados. Si alguna no cruza, se detiene.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.population.electoral import MARGINAL, SALIDA as ELECTORAL, normalizar   # noqa: E402

RECEPTOR = RAIZ / "data" / "raw" / "em2021_receptor_v2.csv"
SALIDA = RAIZ / "data" / "processed" / "geografia_electoral"

#: §3.1 — los tres más votados en Bogotá por año (DI-GE3 lo verifica).
RESULTADOS = ((2014, "zuluaga"), (2014, "clara_lopez"), (2014, "santos"),
              (2018, "fajardo"), (2018, "petro"), (2018, "duque"),
              (2022, "petro"), (2022, "hernandez"), (2022, "gutierrez"))
PRINCIPAL = (2022, "petro")
PERSISTENCIA = ((2018, "petro"), (2022, "petro"))
SUMAPAZ = 20
N_PERM = 10_000
SEMILLA = 20260929
UMBRAL_INSCRIPCION = 0.50           # enmienda 1


class GeografiaError(RuntimeError):
    """Los datos no permiten correr el análisis como está pre-registrado."""


# --------------------------------------------------------------------------
# Datos

def composicion(receptor: Path = RECEPTOR) -> pd.DataFrame:
    """x1 estrato medio, x2 proporción universitaria o más, x3 edad media, por cod_loc."""
    from src.population.loader import load_multiproposito_receptor
    r = load_multiproposito_receptor(receptor)
    if "factor_expansion" not in r.columns:
        raise GeografiaError("El receptor no trae factor de expansión (§3.2 exige FEX_C).")
    codigo = {normalizar(n): int(c) for c, n in
              pd.read_csv(MARGINAL).set_index("COD_LOC").localidad.items()}
    r["cod_loc"] = r.localidad.map(lambda n: codigo.get(normalizar(n)))
    if r.cod_loc.isna().any():
        raise GeografiaError(f"Localidades sin código (DI-GE5): {sorted(r[r.cod_loc.isna()].localidad.unique())}")
    w = r.factor_expansion
    r = r.assign(_w=w, _e=r.estrato * w, _u=(r.nivel_educativo >= 4) * w, _a=r.edad * w)
    g = r.groupby("cod_loc")[["_w", "_e", "_u", "_a"]].sum()
    return pd.DataFrame({"x1": g._e / g._w, "x2": g._u / g._w, "x3": g._a / g._w})


def proporciones(votos: pd.DataFrame, zonas: pd.DataFrame) -> pd.DataFrame:
    """Proporción sobre votos_candidatos, por cod_loc × (año, clave). Sin zonas 90 y 98."""
    v = votos[votos.cod_loc.notna() & (votos.tipo == "candidato")]
    v = v.merge(zonas[["anio", "zona", "votos_candidatos"]], on=["anio", "zona"])
    v = v.assign(p=v.votos / v.votos_candidatos, cod_loc=v.cod_loc.astype(int))
    return v.pivot_table(index="cod_loc", columns=["anio", "clave"], values="p")


def verificar_resultados(votos: pd.DataFrame) -> None:
    """DI-GE3: los nueve de RESULTADOS son de verdad los tres primeros de cada año."""
    c = votos[votos.tipo == "candidato"].groupby(["anio", "clave"]).votos.sum()
    for anio in sorted({a for a, _ in RESULTADOS}):
        top = set(c[anio].nlargest(3).index)
        fijados = {k for a, k in RESULTADOS if a == anio}
        if top != fijados:
            raise GeografiaError(f"{anio}: los tres primeros son {sorted(top)}, no {sorted(fijados)}.")


def razon_inscripcion() -> pd.Series:
    """Enmienda 1: potencial electoral 2018 / población 18+, por cod_loc."""
    pot = pd.read_csv(ELECTORAL / "presidente_1v_potencial_2018.csv").dropna(subset=["cod_loc"])
    pot = pot.set_index(pot.cod_loc.astype(int)).potencial
    pob = pd.read_csv(MARGINAL).set_index("COD_LOC").poblacion
    return (pot / pob).dropna()


# --------------------------------------------------------------------------
# Estadística

def _diseno(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, float)
    X = X.reshape(len(X), -1)
    return np.column_stack([np.ones(len(X)), X])


def residuos(y, X) -> np.ndarray:
    A = _diseno(X)
    beta, *_ = np.linalg.lstsq(A, np.asarray(y, float), rcond=None)
    return np.asarray(y, float) - A @ beta


def _sombrero(X) -> np.ndarray:
    A = _diseno(X)
    return A @ np.linalg.pinv(A)


def _r2_loo_con(y: np.ndarray, H: np.ndarray) -> float:
    e = y - H @ y
    press = float(np.sum((e / (1.0 - np.diag(H))) ** 2))
    return 1.0 - press / float(np.sum((y - y.mean()) ** 2))


def r2_loo(y, X) -> float:
    """DI-GE1: 1 − PRESS / SC_total, con PRESS por la matriz sombrero."""
    return _r2_loo_con(np.asarray(y, float), _sombrero(X))


def p_perm_r2(y, X, n: int = N_PERM, rng: Optional[np.random.Generator] = None) -> float:
    """DI-GE2. La matriz sombrero depende solo de X: se calcula una vez."""
    rng = rng or np.random.default_rng(SEMILLA)
    y, H = np.asarray(y, float), _sombrero(X)
    obs = _r2_loo_con(y, H)
    mayores = sum(_r2_loo_con(rng.permutation(y), H) >= obs for _ in range(n))
    return (1 + mayores) / (1 + n)


def persistencia(a, b, n: int = N_PERM, rng: Optional[np.random.Generator] = None) -> tuple[float, float]:
    """(r, p de una cola por permutación) entre dos vectores de residuos."""
    rng = rng or np.random.default_rng(SEMILLA)
    a, b = np.asarray(a, float), np.asarray(b, float)
    r = float(np.corrcoef(a, b)[0, 1])
    mayores = sum(np.corrcoef(a, rng.permutation(b))[0, 1] >= r for _ in range(n))
    return r, (1 + mayores) / (1 + n)


# --------------------------------------------------------------------------
# El análisis pre-registrado

def analizar(prop: pd.DataFrame, comp: pd.DataFrame, razon: Optional[pd.Series] = None,
             n_perm: int = N_PERM, sumapaz: Optional[pd.Series] = None) -> dict:
    """§4 completo sobre las localidades comunes (19, sin Sumapaz). `prop` por (año, clave)."""
    locs = sorted(set(prop.index) & set(comp.index) - {SUMAPAZ})
    if len(locs) != 19:
        raise GeografiaError(f"Se esperaban 19 localidades y hay {len(locs)}: {locs}")
    X1 = comp.loc[locs, ["x1"]].to_numpy()
    X2 = comp.loc[locs, ["x1", "x2", "x3"]].to_numpy()
    rng = np.random.default_rng(SEMILLA)

    por_resultado, res = {}, {}
    for anio, clave in RESULTADOS:
        y = prop.loc[locs, (anio, clave)].to_numpy()
        e = residuos(y, X1)
        res[(anio, clave)] = e
        por_resultado[f"{anio}_{clave}"] = {
            "sd_loc": round(float(y.std(ddof=1)), 4),
            "r2_loo_m1": round(r2_loo(y, X1), 4),
            "r2_loo_m2": round(r2_loo(y, X2), 4),
            "p_perm_m1": round(p_perm_r2(y, X1, n_perm, rng), 4),
            "residuos": {int(l): round(float(v), 4) for l, v in zip(locs, e)},
        }

    a, b = PERSISTENCIA
    r, p = persistencia(res[a], res[b], n_perm, rng)
    claves = [f"{x}_{k}" for x, k in RESULTADOS]
    matriz = np.corrcoef(np.vstack([res[k] for k in RESULTADOS]))

    inscripcion = None
    if razon is not None:
        z = razon.loc[locs].to_numpy()
        inscripcion = {f"{x}_{k}": round(float(np.corrcoef(z, res[(x, k)])[0, 1]), 4)
                       for x, k in PERSISTENCIA}

    salida = {
        "localidades": locs,
        "resultados": por_resultado,
        "persistencia": {"entre": [f"{x}_{k}" for x, k in PERSISTENCIA],
                         "r": round(r, 4), "p": round(p, 4)},
        "matriz_residuos": {c: {d: round(float(matriz[i, j]), 3) for j, d in enumerate(claves)}
                            for i, c in enumerate(claves)},
        "inscripcion_r": inscripcion,
        "n_perm": n_perm,
    }
    if sumapaz is not None:                                   # DI-GE4
        y = prop.loc[locs, PRINCIPAL].to_numpy()
        A = np.column_stack([np.ones(len(locs)), X1])
        beta, *_ = np.linalg.lstsq(A, y, rcond=None)
        pred = float(beta[0] + beta[1] * sumapaz["x1"])
        obs = float(prop.loc[SUMAPAZ, PRINCIPAL])
        salida["sumapaz"] = {"resultado": f"{PRINCIPAL[0]}_{PRINCIPAL[1]}",
                             "observado": round(obs, 4), "predicho_m1": round(pred, 4)}
    return salida


def evaluar(a: dict) -> dict:
    """P1-P5 (§5) y la regla de decisión (§6, con la enmienda 1)."""
    R = a["resultados"]
    principal = R[f"{PRINCIPAL[0]}_{PRINCIPAL[1]}"]
    r2s = [v["r2_loo_m1"] for v in R.values()]
    r = a["persistencia"]["r"]
    insc = a["inscripcion_r"] or {}
    inscripcion_fuerte = any(abs(v) >= UMBRAL_INSCRIPCION for v in insc.values())

    pred = {
        "P1": {"umbral": "R²_LOO(M1, Petro 2022) ≥ 0,70", "valor": principal["r2_loo_m1"],
               "se_cumple": principal["r2_loo_m1"] >= 0.70},
        "P2": {"umbral": "mediana de R²_LOO(M1) ≥ 0,50", "valor": round(float(np.median(r2s)), 4),
               "se_cumple": float(np.median(r2s)) >= 0.50},
        "P3": {"umbral": "R²_LOO(M2) − R²_LOO(M1) < 0,10 (Petro 2022)",
               "valor": round(principal["r2_loo_m2"] - principal["r2_loo_m1"], 4),
               "se_cumple": principal["r2_loo_m2"] - principal["r2_loo_m1"] < 0.10},
        "P4": {"umbral": "persistencia Petro 2018 → 2022: r > 0,5", "valor": r,
               "se_cumple": r > 0.5, "interpretable_como_territorio": not inscripcion_fuerte},
        "P5": {"umbral": "p_perm < 0,05 en al menos 6 de 9",
               "valor": sum(v["p_perm_m1"] < 0.05 for v in R.values()),
               "se_cumple": sum(v["p_perm_m1"] < 0.05 for v in R.values()) >= 6},
    }

    r2 = principal["r2_loo_m1"]
    if r2 >= 0.80 and r < 0.30:
        lectura = "A: a nivel de localidad, la geografía del voto es composición."
    elif r2 >= 0.50 and r >= 0.50 and not inscripcion_fuerte:
        lectura = "B: hay territorio estable que la composición no ve."
    elif r2 < 0.50:
        lectura = "C: la composición no explica la geografía del voto."
    elif r2 >= 0.50 and r >= 0.50 and inscripcion_fuerte:
        lectura = ("Intermedio (enmienda 1): la persistencia sigue a la inscripción "
                   "(|r| ≥ 0,50), así que no se puede leer como territorio.")
    else:
        lectura = "Intermedio: no se adopta ninguna de las tres lecturas."
    return {"predicciones": pred, "regla": lectura, "inscripcion_fuerte": inscripcion_fuerte}


# --------------------------------------------------------------------------

def main(argv=None) -> int:
    argparse.ArgumentParser(description="Geografía electoral (pre-registro en docs/).").parse_args(argv)
    try:
        votos = pd.read_csv(ELECTORAL / "presidente_1v_localidad.csv")
        zonas = pd.read_csv(ELECTORAL / "presidente_1v_zonas.csv")
        verificar_resultados(votos)
        comp = composicion()
        a = analizar(proporciones(votos, zonas), comp, razon_inscripcion(),
                     sumapaz=comp.loc[SUMAPAZ] if SUMAPAZ in comp.index else None)
    except GeografiaError as e:
        print(f"ERROR: {e}")
        return 1
    v = evaluar(a)
    SALIDA.mkdir(parents=True, exist_ok=True)
    destino = SALIDA / "resultado.json"
    destino.write_text(json.dumps({**a, **v}, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"{'resultado':18s} {'sd_loc':>7s} {'R²LOO M1':>9s} {'R²LOO M2':>9s} {'p_perm':>7s}")
    for k, r in a["resultados"].items():
        print(f"{k:18s} {r['sd_loc']:7.3f} {r['r2_loo_m1']:9.3f} {r['r2_loo_m2']:9.3f} {r['p_perm_m1']:7.4f}")
    print(f"\nPersistencia {' → '.join(a['persistencia']['entre'])}: "
          f"r = {a['persistencia']['r']:.3f} (p = {a['persistencia']['p']:.4f})")
    print(f"Residuo contra razón de inscripción: {a['inscripcion_r']}")
    if "sumapaz" in a:
        print(f"Sumapaz (fuera del ajuste): {a['sumapaz']}")
    print()
    for k, p in v["predicciones"].items():
        print(f"  {k} {'se cumple' if p['se_cumple'] else 'NO se cumple'} — {p['umbral']} (valor {p['valor']})")
    print(f"\nRegla de decisión: {v['regla']}")
    print(f"\n{destino.relative_to(RAIZ).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
