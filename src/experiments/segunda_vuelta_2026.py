"""
Segunda vuelta 2026: ¿la primera vuelta sumada por bloques anticipa en qué
localidades de Bogotá gana cada candidato, y por cuánto?

Pre-registro: `docs/SEGUNDA_VUELTA_2026_SPECIFICATION.md`. Este módulo lo ejecuta y
no decide nada que el documento no haya decidido.

    bloques:  Cepeda 2ª = izquierda + ½ · resto          (primera vuelta)
    ingenua:  Cepeda 2ª = Cepeda / (Cepeda + Abelardo)    (primera vuelta)
    se comparan con la proporción de Cepeda sobre los votos de los dos en la 2ª

Uso (después de que `tests/test_segunda_vuelta_2026.py` pase y exista la tabla de
la segunda vuelta):
    python src/experiments/segunda_vuelta_2026.py

Escribe `data/processed/segunda_vuelta_2026/resultado.json`.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-SV1. **Los bloques son listas explícitas** (§3.1 del pre-registro). Cualquier
    candidato de la primera vuelta que no esté en IZQUIERDA ni en DERECHA va al
    resto; si aparece uno que no está en ninguna de las tres listas, el análisis
    se detiene: la asignación no se decide viendo datos.

DI-SV2. **Localidades y ciudad se calculan con bases distintas, como dice §3.3.**
    Por localidad, las 20 (con Sumapaz, sin las zonas 90 y 98). Para la ciudad,
    todos los votos, incluidas 90 y 98. La regla de bloques de la ciudad se
    calcula con los votos de toda la ciudad, no promediando localidades.

DI-SV3. **La tabla de la segunda vuelta vive en archivos propios**
    (`presidente_2v_localidad.csv`, `presidente_2v_zonas.csv`), con el mismo
    formato que los de la primera: son otra elección, y mezclarlas en la misma
    tabla haría que cualquier análisis de primera vuelta la leyera sin querer.

DI-SV4. **P2 es estricta** (error de bloques < error ingenuo). Un empate exacto no
    la cumple.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import geografia_electoral as ge      # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "segunda_vuelta_2026"
ANIO = 2026
CEPEDA, ABELARDO = "cepeda", "de_la_espriella"
IZQUIERDA = ("cepeda",)
DERECHA = ("de_la_espriella", "valencia", "uribe_londono")
RESTO = ("fajardo", "claudia_lopez", "botero", "lizcano", "garvin", "barreras", "matamoros")
REPARTO_RESTO = 0.5
UMBRAL_CIUDAD = 0.5
UMBRAL_GANADORES = 18
UMBRAL_SPEARMAN = 0.90


class SegundaVueltaError(RuntimeError):
    """Los datos no permiten correr el análisis como está pre-registrado."""


# --------------------------------------------------------------------------
# Las dos reglas, desde la primera vuelta

def _bloques(votos_candidato: pd.DataFrame) -> pd.DataFrame:
    """Proporciones de izquierda, derecha y resto sobre votos por candidato, por fila."""
    desconocidos = set(votos_candidato.columns) - set(IZQUIERDA) - set(DERECHA) - set(RESTO)
    if desconocidos:
        raise SegundaVueltaError(f"Candidatos sin bloque (DI-SV1): {sorted(desconocidos)}")
    tot = votos_candidato.sum(axis=1)
    f = lambda cl: votos_candidato[[c for c in cl if c in votos_candidato]].sum(axis=1) / tot   # noqa: E731
    return pd.DataFrame({"izquierda": f(IZQUIERDA), "derecha": f(DERECHA), "resto": f(RESTO),
                         "cepeda": votos_candidato[CEPEDA] / tot, "abelardo": votos_candidato[ABELARDO] / tot})


def _reglas(b: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({"bloques": b.izquierda + REPARTO_RESTO * b.resto,
                         "ingenua": b.cepeda / (b.cepeda + b.abelardo)})


def reglas_primera_vuelta(votos: pd.DataFrame, anio: int = ANIO) -> tuple[pd.DataFrame, dict]:
    """(reglas por cod_loc, reglas de la ciudad). DI-SV2."""
    v = votos[(votos.anio == anio) & (votos.tipo == "candidato")]
    if v.empty:
        raise SegundaVueltaError(f"La tabla de primera vuelta no trae {anio}.")
    loc = v[v.cod_loc.notna()].assign(cod_loc=lambda d: d.cod_loc.astype(int)).pivot_table(
        index="cod_loc", columns="clave", values="votos", aggfunc="sum", fill_value=0)
    ciudad = v.groupby("clave").votos.sum().to_frame().T
    por_loc = _reglas(_bloques(loc))
    c = _reglas(_bloques(ciudad)).iloc[0]
    return por_loc, {"bloques": float(c.bloques), "ingenua": float(c.ingenua)}


# --------------------------------------------------------------------------
# Lo observado en la segunda vuelta

def observado_segunda_vuelta(votos2: pd.DataFrame, anio: int = ANIO) -> tuple[pd.Series, float]:
    """(proporción de Cepeda sobre los dos, por cod_loc; la misma para toda la ciudad)."""
    v = votos2[(votos2.anio == anio) & (votos2.tipo == "candidato")]
    if v.empty:
        raise SegundaVueltaError(f"La tabla de segunda vuelta no trae {anio} todavía.")
    if set(v.clave) != {CEPEDA, ABELARDO}:
        raise SegundaVueltaError(f"La segunda vuelta debería traer solo a {CEPEDA} y {ABELARDO}: {sorted(set(v.clave))}")
    loc = v[v.cod_loc.notna()].assign(cod_loc=lambda d: d.cod_loc.astype(int)).pivot_table(
        index="cod_loc", columns="clave", values="votos", aggfunc="sum")
    ciudad = v.groupby("clave").votos.sum()
    return (loc[CEPEDA] / (loc[CEPEDA] + loc[ABELARDO])).rename("cepeda_2v"), \
        float(ciudad[CEPEDA] / ciudad.sum())


# --------------------------------------------------------------------------
# El análisis

def analizar(reglas: pd.DataFrame, reglas_ciudad: dict, obs: pd.Series, obs_ciudad: float) -> dict:
    locs = sorted(set(reglas.index) & set(obs.index))
    if len(locs) != 20:
        raise SegundaVueltaError(f"Se esperaban 20 localidades y hay {len(locs)}: {locs}")
    r, o = reglas.loc[locs], obs.loc[locs]
    gana_pred, gana_obs = r.bloques > 0.5, o > 0.5
    return {
        "localidades": locs,
        "ciudad": {"observado": round(obs_ciudad, 4), "bloques": round(reglas_ciudad["bloques"], 4),
                   "ingenua": round(reglas_ciudad["ingenua"], 4)},
        "mae_bloques": round(float((r.bloques - o).abs().mean()), 4),
        "mae_ingenua": round(float((r.ingenua - o).abs().mean()), 4),
        "ganadores_acertados": int((gana_pred == gana_obs).sum()),
        "spearman": round(float(pd.Series(r.bloques.to_numpy()).corr(pd.Series(o.to_numpy()), method="spearman")), 4),
        "por_localidad": {int(l): {"bloques": round(float(r.bloques[l]), 4), "ingenua": round(float(r.ingenua[l]), 4),
                                   "observado": round(float(o[l]), 4)} for l in locs},
    }


def evaluar(a: dict) -> dict:
    """P1-P4 (§6) y la regla de decisión (§7)."""
    p1 = a["ciudad"]["observado"] < UMBRAL_CIUDAD
    p2 = a["mae_bloques"] < a["mae_ingenua"]                        # DI-SV4
    p3 = a["ganadores_acertados"] >= UMBRAL_GANADORES
    p4 = a["spearman"] >= UMBRAL_SPEARMAN
    p1, p2, p3, p4 = map(bool, (p1, p2, p3, p4))
    pred = {
        "P1": {"umbral": "Cepeda < 50 % en la ciudad", "valor": a["ciudad"]["observado"], "se_cumple": p1},
        "P2": {"umbral": "error medio: bloques < ingenua", "valor": [a["mae_bloques"], a["mae_ingenua"]], "se_cumple": p2},
        "P3": {"umbral": "≥ 18 de 20 ganadores (no informativa)", "valor": a["ganadores_acertados"], "se_cumple": p3},
        "P4": {"umbral": "Spearman ≥ 0,90 (no informativa)", "valor": a["spearman"], "se_cumple": p4},
    }
    if p1 and p2:
        lectura, regla = "A", ("A: el voto se movió por bloques; sumar la primera vuelta por bloques anticipa "
                               "la segunda mejor que suponer que cada candidato conserva lo suyo.")
    elif p2:
        lectura, regla = "B", ("B: la regla de bloques anticipa mejor los márgenes, pero la ciudad quedó del "
                               "lado de Cepeda: la derecha se juntó solo en parte.")
    elif not p1:
        lectura, regla = "C", ("C: la regla ingenua anticipa mejor; la derecha de la primera vuelta no se "
                               "juntó detrás de Abelardo en Bogotá.")
    else:
        lectura, regla = "intermedio", "Intermedio: P1 sin P2; no se adopta lectura."
    return {"predicciones": pred, "lectura": lectura, "regla": regla}


# --------------------------------------------------------------------------

def main(argv=None) -> int:
    argparse.ArgumentParser(description="Segunda vuelta 2026 (pre-registro en docs/).").parse_args(argv)
    try:
        v1 = pd.read_csv(ge.ELECTORAL / "presidente_1v_localidad.csv")
        ruta2 = ge.ELECTORAL / "presidente_2v_localidad.csv"
        if not ruta2.exists():
            raise SegundaVueltaError("La tabla de segunda vuelta no existe todavía: hay que construirla primero.")
        reglas, reglas_c = reglas_primera_vuelta(v1)
        obs, obs_c = observado_segunda_vuelta(pd.read_csv(ruta2))
        a = analizar(reglas, reglas_c, obs, obs_c)
    except SegundaVueltaError as e:
        print(f"ERROR: {e}")
        return 1
    v = evaluar(a)
    SALIDA.mkdir(parents=True, exist_ok=True)
    destino = SALIDA / "resultado.json"
    destino.write_text(json.dumps({**a, **v}, ensure_ascii=False, indent=2), encoding="utf-8")
    c = a["ciudad"]
    print(f"Ciudad: Cepeda {c['observado']:.1%} (bloques {c['bloques']:.1%}, ingenua {c['ingenua']:.1%})")
    print(f"Error medio por localidad: bloques {a['mae_bloques']:.4f}, ingenua {a['mae_ingenua']:.4f}")
    print(f"Ganadores acertados: {a['ganadores_acertados']} de 20 · Spearman {a['spearman']:.2f}")
    for k, p in v["predicciones"].items():
        print(f"  {k} {'se cumple' if p['se_cumple'] else 'NO se cumple'} — {p['umbral']} (valor {p['valor']})")
    print(f"\nRegla de decisión: {v['regla']}\n\n{destino.relative_to(RAIZ).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
