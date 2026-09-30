"""
Polos 2026: ¿el polo de derecha de 2014–2022 anticipa el mapa de Abelardo de la
Espriella en Bogotá, primera vuelta de 2026?

Pre-registro: `docs/POLOS_2026_SPECIFICATION.md`. Este módulo lo ejecuta y no
decide nada que el documento no haya decidido.

    polo de derecha = promedio de los residuos estandarizados de Zuluaga 2014,
                      Duque 2018 y Gutiérrez 2022 (resultado.json, sin recalcular)
    residuo de Abelardo (M1, estrato medio)  vs  polo  → r_der, p de una cola
    R²_LOO de M1 + polo  menos  R²_LOO de M1  → ΔR²_LOO
    control de inscripción; comparación con Gutiérrez 2022 solo; Sumapaz aparte

Uso (después de que `tests/test_polos_2026.py` pase y exista la tabla de 2026):
    python src/experiments/polos_2026.py

Escribe `data/processed/polos_2026/resultado.json`.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-P26-1. **Se reutiliza sin cambios lo que ya se validó.** Residuo, R²_LOO,
    permutación de una cola (`persistencia`), composición, razón de inscripción
    y la exigencia de 19 localidades salen de `geografia_electoral.py`, que pasó
    los mundos simulados de su pre-registro.

DI-P26-2. **El polo se estandariza con la desviación poblacional (ddof = 0)**
    entre las 19 localidades, como se calculó la tabla de §4 del pre-registro.
    Hecho: r_der, r_izq y el ΔR²_LOO no cambian con la escala del polo, así que
    esta elección solo afecta las cifras de §4, y las pruebas verifican que el
    código las reproduce.

DI-P26-3. **El polo se lee de `resultado.json` y se congela en el
    pre-registro.** Las pruebas comparan el polo calculado con la tabla de §4
    escrita en el documento: si alguien regenerara `resultado.json` con otros
    residuos, el polo cambiaría después de ver 2026 y la prueba falla.

DI-P26-4. **Abelardo se identifica por nombre en la tabla de 2026** (`opcion`
    contiene «ABELARDO», sin tildes ni mayúsculas). Si no aparece, o aparece más
    de una opción, el análisis se detiene: no se elige a mano.

DI-P26-5. **Signos: una localidad con polo exactamente 0 no cuenta** ni a favor
    ni en contra (Barrios Unidos está en −0,003). Es descriptivo y no decide.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import unicodedata
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import geografia_electoral as ge      # noqa: E402

RESULTADO_PRESIDENCIAL = RAIZ / "data" / "processed" / "geografia_electoral" / "resultado.json"
RESULTADO_PARTIDOS = RAIZ / "data" / "processed" / "eje_partidos" / "resultado.json"
SALIDA = RAIZ / "data" / "processed" / "polos_2026"

ANIO = 2026
NOMBRE = "ABELARDO"
DERECHA = ("2014_zuluaga", "2018_duque", "2022_gutierrez")
IZQUIERDA = ("2014_clara_lopez", "2018_petro", "2022_petro")
ULTIMO = "2022_gutierrez"
CENTRO_DEMOCRATICO = "PARTIDO CENTRO DEMOCRATICO"
UMBRAL_R = 0.5
UMBRAL_DR2 = 0.05
UMBRAL_R2 = 0.5
UMBRAL_INSCRIPCION = 0.5
N_PERM = 10_000
SEMILLA = 20260930


class PolosError(RuntimeError):
    """Los datos no permiten correr el análisis como está pre-registrado."""


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return s.upper()


# --------------------------------------------------------------------------
# Referencias (todo lo de antes de 2026)

def residuos_presidenciales(ruta: Path = RESULTADO_PRESIDENCIAL) -> pd.DataFrame:
    """Residuos de M1 pre-registrados, por cod_loc × clave. Sin recalcular."""
    R = json.loads(ruta.read_text(encoding="utf-8"))["resultados"]
    df = pd.DataFrame({k: {int(l): float(v) for l, v in r["residuos"].items()} for k, r in R.items()})
    return df.sort_index()


def polo(claves, res: Optional[pd.DataFrame] = None) -> pd.Series:
    """DI-P26-2: promedio de los residuos estandarizados (ddof = 0)."""
    res = residuos_presidenciales() if res is None else res
    z = res[list(claves)]
    z = (z - z.mean()) / z.std(ddof=0)
    return z.mean(axis=1)


def polo_centro_democratico(ruta: Path = RESULTADO_PARTIDOS) -> Optional[pd.Series]:
    """Secundario (§3.2): el residuo del Centro Democrático en el Senado 2018."""
    if not ruta.exists():
        return None
    r = json.loads(ruta.read_text(encoding="utf-8"))["por_corporacion"]["senado_nacional"]
    return pd.Series({int(l): float(v) for l, v in r[CENTRO_DEMOCRATICO]["residuos"].items()}).sort_index()


# --------------------------------------------------------------------------
# El voto de 2026

def proporcion_abelardo(votos: pd.DataFrame, zonas: pd.DataFrame, anio: int = ANIO) -> pd.Series:
    """DI-P26-4. Proporción sobre votos_candidatos por cod_loc (incluye Sumapaz si está)."""
    v, z = votos[votos.anio == anio], zonas[zonas.anio == anio]
    if v.empty or z.empty:
        raise PolosError(f"La tabla electoral no trae {anio} todavía: hay que construirla primero.")
    claves = v[(v.tipo == "candidato") & v.opcion.map(lambda o: NOMBRE in _norm(o))].clave.unique()
    if len(claves) != 1:
        raise PolosError(f"Se esperaba una opción con «{NOMBRE}» en {anio} y hay {len(claves)}: {list(claves)}")
    prop = ge.proporciones(v, z)
    return prop[(anio, claves[0])].rename("abelardo")


# --------------------------------------------------------------------------
# El análisis

def analizar(prop: pd.Series, comp: pd.DataFrame, der: pd.Series, izq: pd.Series,
             ultimo: pd.Series, razon: Optional[pd.Series] = None,
             cd: Optional[pd.Series] = None, n_perm: int = N_PERM,
             rng: Optional[np.random.Generator] = None) -> dict:
    """§5 completo sobre las 19 localidades (sin Sumapaz)."""
    locs = sorted(set(prop.dropna().index) & set(comp.index) & set(der.index) - {ge.SUMAPAZ})
    if len(locs) != 19:
        raise PolosError(f"Se esperaban 19 localidades y hay {len(locs)}: {locs}")
    rng = rng or np.random.default_rng(SEMILLA)
    y = prop.loc[locs].to_numpy(float)
    x1 = comp.loc[locs, "x1"].to_numpy(float)
    d, i, u = (s.loc[locs].to_numpy(float) for s in (der, izq, ultimo))

    resid = ge.residuos(y, x1)
    r_der, p_der = ge.persistencia(resid, d, n_perm, rng)
    r2_m1 = ge.r2_loo(y, x1)
    r2_polo = ge.r2_loo(y, np.column_stack([x1, d]))
    con_signo = d != 0                                                   # DI-P26-5
    salida = {
        "localidades": locs,
        "r_der": round(r_der, 4), "p_der": round(p_der, 4),
        "r_izq": round(float(np.corrcoef(resid, i)[0, 1]), 4),
        "r_ultimo": round(float(np.corrcoef(resid, u)[0, 1]), 4),
        "r2_loo_m1": round(r2_m1, 4), "r2_loo_m1_polo": round(r2_polo, 4),
        "delta_r2_loo": round(r2_polo - r2_m1, 4),
        "sd_loc": round(float(y.std(ddof=1)), 4),
        "signos": {"aciertos": int(np.sum(np.sign(resid[con_signo]) == np.sign(d[con_signo]))),
                   "de": int(con_signo.sum())},
        "residuos": {int(l): round(float(v), 4) for l, v in zip(locs, resid)},
        "polo_derecha": {int(l): round(float(v), 4) for l, v in zip(locs, d)},
        "n_perm": n_perm,
    }
    if razon is not None:
        salida["r_inscripcion"] = round(float(np.corrcoef(resid, razon.loc[locs])[0, 1]), 4)
    if cd is not None:                                                   # secundario, sin umbral
        salida["r_centro_democratico_2018"] = round(float(np.corrcoef(resid, cd.loc[locs])[0, 1]), 4)
    if ge.SUMAPAZ in prop.dropna().index and ge.SUMAPAZ in comp.index:  # aparte, §3.3
        A = np.column_stack([np.ones(len(locs)), x1])
        beta, *_ = np.linalg.lstsq(A, y, rcond=None)
        salida["sumapaz"] = {"observado": round(float(prop.loc[ge.SUMAPAZ]), 4),
                             "predicho_m1": round(float(beta[0] + beta[1] * comp.loc[ge.SUMAPAZ, "x1"]), 4)}
    return salida


def evaluar(a: dict) -> dict:
    """P1-P6 (§6) y la regla de decisión (§7)."""
    p1 = a["r_der"] > UMBRAL_R and a["p_der"] < 0.05
    p2 = a["r_der"] > -a["r_izq"]
    p3 = a["delta_r2_loo"] >= UMBRAL_DR2
    p4 = a["r_der"] >= a["r_ultimo"]
    p5 = abs(a.get("r_inscripcion", 0.0)) < UMBRAL_INSCRIPCION
    p6 = a["r2_loo_m1"] >= UMBRAL_R2
    # bool() explícito: json no sabe escribir np.bool_
    p1, p2, p3, p4, p5, p6 = map(bool, (p1, p2, p3, p4, p5, p6))
    pred = {
        "P1": {"umbral": "r_der > 0,5 y p < 0,05", "valor": [a["r_der"], a["p_der"]], "se_cumple": p1},
        "P2": {"umbral": "r_der > −r_izq", "valor": [a["r_der"], a["r_izq"]], "se_cumple": p2},
        "P3": {"umbral": "ΔR²_LOO ≥ 0,05", "valor": a["delta_r2_loo"], "se_cumple": p3},
        "P4": {"umbral": "r_der ≥ r con Gutiérrez 2022", "valor": [a["r_der"], a["r_ultimo"]], "se_cumple": p4},
        "P5": {"umbral": "|r con la inscripción| < 0,50", "valor": a.get("r_inscripcion"), "se_cumple": p5},
        "P6": {"umbral": "R²_LOO(M1) ≥ 0,50 (no informativa)", "valor": a["r2_loo_m1"], "se_cumple": p6},
    }
    if not p5:
        lectura, regla = "intermedio", ("Intermedio: el patrón puede ser la inscripción. "
                                        "No se adopta lectura.")
    elif p1 and p3:
        lectura = "A"
        regla = ("A: el polo de derecha anticipa el mapa de un candidato nuevo, más allá de su "
                 "estrato. " + ("Con P2: se sostiene la lectura de dos polos. " if p2 else
                                "Sin P2: esta elección no distingue dos polos de un eje. ")
                 + ("" if p4 else "Sin P4: el último candidato predice igual o mejor que el promedio."))
    elif p1:
        lectura, regla = "B", ("B: el resto de Abelardo tiene la forma del polo, pero es pequeño "
                               "frente al estrato: para anticipar su mapa basta el estrato.")
    else:
        lectura, regla = "C", ("C: el polo no se transfiere a un candidato nuevo; la geografía de "
                               "la derecha de 2014–2022 era la de sus candidatos.")
    return {"predicciones": pred, "lectura": lectura, "regla": regla.strip()}


# --------------------------------------------------------------------------

def main(argv=None) -> int:
    argparse.ArgumentParser(description="Polos 2026 (pre-registro en docs/).").parse_args(argv)
    try:
        votos = pd.read_csv(ge.ELECTORAL / "presidente_1v_localidad.csv")
        zonas = pd.read_csv(ge.ELECTORAL / "presidente_1v_zonas.csv")
        prop = proporcion_abelardo(votos, zonas)
        res = residuos_presidenciales()
        logging.disable(logging.WARNING)
        comp = ge.composicion()
        logging.disable(logging.NOTSET)
        a = analizar(prop, comp, polo(DERECHA, res), polo(IZQUIERDA, res), res[ULTIMO],
                     ge.razon_inscripcion(), polo_centro_democratico())
    except (PolosError, ge.GeografiaError, FileNotFoundError) as e:
        print(f"ERROR: {e}")
        return 1
    v = evaluar(a)
    SALIDA.mkdir(parents=True, exist_ok=True)
    destino = SALIDA / "resultado.json"
    destino.write_text(json.dumps({**a, **v}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"r_der {a['r_der']:.2f} (p {a['p_der']:.4f})   r_izq {a['r_izq']:.2f}   "
          f"r Gutiérrez {a['r_ultimo']:.2f}   R²LOO M1 {a['r2_loo_m1']:.2f} → +polo "
          f"{a['r2_loo_m1_polo']:.2f}   signos {a['signos']['aciertos']}/{a['signos']['de']}")
    for k, p in v["predicciones"].items():
        print(f"  {k} {'se cumple' if p['se_cumple'] else 'NO se cumple'} — {p['umbral']} (valor {p['valor']})")
    print(f"\nRegla de decisión: {v['regla']}\n\n{destino.relative_to(RAIZ).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
