"""
Eje por partidos: ¿el resto territorial del voto presidencial aparece en el voto
por partido al Congreso 2018?

Pre-registro: `docs/EJE_PARTIDOS_SPECIFICATION.md`. Este módulo lo ejecuta y no
decide nada que el documento no haya decidido.

    proporción de cada partido por localidad  ~  estrato medio (M1)
    residuo del partido  vs  residuo de Petro 2022 (resultado.json, sin recalcular)
    permutación de dos colas; control de inscripción; Senado y réplica en Cámara

Uso (después de que `tests/test_eje_partidos.py` pase):
    python src/experiments/eje_partidos.py

Escribe `data/processed/eje_partidos/resultado.json`.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-EP1. **Se reutiliza sin cambios lo que ya se validó.** Residuo, R² fuera de
    muestra, composición, razón de inscripción y la exigencia de 19 localidades
    salen de `geografia_electoral.py`, que pasó los tres mundos simulados de su
    pre-registro. Lo nuevo aquí es la proporción por partido y la permutación de
    dos colas.

DI-EP2. **La permutación es de dos colas** (§4 del pre-registro): hay una
    predicción positiva (Lista de la Decencia) y una negativa (Centro
    Democrático). p = (1 + #{|r_perm| ≥ |r|}) / (1 + n).

DI-EP3. **Los partidos decisivos se verifican contra su regla.** El
    pre-registro los fija como la lista de cada extremo de 2018 y dice que están
    entre los seis mayores del Senado; el código comprueba que existan con ese
    nombre en las dos corporaciones y que estén entre los seis mayores. Si no, se
    detiene.

DI-EP4. **El eje de referencia se lee de `resultado.json`**, tal como quedó
    pre-registrado en el análisis anterior, y no se recalcula aquí: así no hay
    ninguna decisión nueva sobre él.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import geografia_electoral as ge      # noqa: E402

RESULTADO_PRESIDENCIAL = RAIZ / "data" / "processed" / "geografia_electoral" / "resultado.json"
SALIDA = RAIZ / "data" / "processed" / "eje_partidos"

DECENCIA = "COALICION LISTA DE LA DECENCIA ASI UP MAIS"
CENTRO_DEMOCRATICO = "PARTIDO CENTRO DEMOCRATICO"
DECISIVOS = (DECENCIA, CENTRO_DEMOCRATICO)
PRINCIPAL = ("senado", "nacional")
REPLICA = ("camara", "territorial")
EJE = "2022_petro"
EJE_SECUNDARIO = "2018_petro"
N_MAYORES = 6
UMBRAL_R = 0.5
UMBRAL_INSCRIPCION = 0.5
N_PERM = 10_000
SEMILLA = 20260930


class EjeError(RuntimeError):
    """Los datos no permiten correr el análisis como está pre-registrado."""


# --------------------------------------------------------------------------
# Datos

def proporciones_partido(votos: pd.DataFrame, zonas: pd.DataFrame,
                         corporacion: str, circunscripcion: str) -> pd.DataFrame:
    """Proporción de cada partido sobre votos_partidos, por cod_loc. Sin zonas 90 y 98."""
    sel = lambda df: df[(df.corporacion == corporacion) & (df.circunscripcion == circunscripcion)]  # noqa: E731
    v = sel(votos)
    v = v[v.cod_loc.notna() & (v.tipo == "partido")]
    z = sel(zonas)[["zona", "votos_partidos"]]
    v = v.merge(z, on="zona").assign(cod_loc=lambda d: d.cod_loc.astype(int))
    v["p"] = v.votos / v.votos_partidos
    return v.pivot_table(index="cod_loc", columns="partido", values="p", fill_value=0.0)


def mayores(votos: pd.DataFrame, corporacion: str, circunscripcion: str, n: int = N_MAYORES) -> list[str]:
    v = votos[(votos.corporacion == corporacion) & (votos.circunscripcion == circunscripcion)
              & (votos.tipo == "partido")]
    return list(v.groupby("partido").votos.sum().sort_values(ascending=False).index[:n])


def verificar_decisivos(votos: pd.DataFrame) -> list[str]:
    """DI-EP3. Devuelve los seis mayores del Senado, que son los que se reportan."""
    seis = mayores(votos, *PRINCIPAL)
    for p in DECISIVOS:
        if p not in seis:
            raise EjeError(f"{p} no está entre los {N_MAYORES} mayores del Senado: {seis}")
        for corp, circ in (PRINCIPAL, REPLICA):
            v = votos[(votos.corporacion == corp) & (votos.circunscripcion == circ)]
            if p not in set(v.partido):
                raise EjeError(f"{p} no aparece en {corp} {circ}")
    return seis


def eje_presidencial(clave: str = EJE, ruta: Path = RESULTADO_PRESIDENCIAL) -> pd.Series:
    """DI-EP4: el residuo pre-registrado del análisis anterior, por cod_loc."""
    r = json.loads(ruta.read_text(encoding="utf-8"))["resultados"][clave]["residuos"]
    return pd.Series({int(k): float(v) for k, v in r.items()}).sort_index()


# --------------------------------------------------------------------------
# Estadística

def correlacion_dos_colas(a, b, n: int = N_PERM,
                          rng: Optional[np.random.Generator] = None) -> tuple[float, float]:
    """DI-EP2: (r, p de dos colas por permutación)."""
    rng = rng or np.random.default_rng(SEMILLA)
    a, b = np.asarray(a, float), np.asarray(b, float)
    r = float(np.corrcoef(a, b)[0, 1])
    mayores_ = sum(abs(np.corrcoef(a, rng.permutation(b))[0, 1]) >= abs(r) for _ in range(n))
    return r, (1 + mayores_) / (1 + n)


# --------------------------------------------------------------------------
# El análisis

def analizar(props: dict[tuple[str, str], pd.DataFrame], comp: pd.DataFrame,
             eje: pd.Series, partidos: list[str], razon: Optional[pd.Series] = None,
             eje_secundario: Optional[pd.Series] = None, n_perm: int = N_PERM) -> dict:
    """Para cada corporación y partido: residuo, R²_LOO, r con el eje, p, inscripción."""
    rng = np.random.default_rng(SEMILLA)
    salida = {}
    for (corp, circ), prop in props.items():
        locs = sorted(set(prop.index) & set(comp.index) & set(eje.index) - {ge.SUMAPAZ})
        if len(locs) != 19:
            raise EjeError(f"{corp} {circ}: se esperaban 19 localidades y hay {len(locs)}")
        X1 = comp.loc[locs, ["x1"]].to_numpy()
        e = eje.loc[locs].to_numpy()
        res = {}
        for p in partidos:
            if p not in prop.columns:
                continue
            y = prop.loc[locs, p].to_numpy()
            resid = ge.residuos(y, X1)
            r, pv = correlacion_dos_colas(resid, e, n_perm, rng)
            fila = {"r2_loo": round(ge.r2_loo(y, X1), 4), "sd_loc": round(float(y.std(ddof=1)), 4),
                    "r_eje": round(r, 4), "p": round(pv, 4),
                    "residuos": {int(l): round(float(v), 4) for l, v in zip(locs, resid)}}
            if eje_secundario is not None:
                fila["r_eje_secundario"] = round(float(np.corrcoef(resid, eje_secundario.loc[locs])[0, 1]), 4)
            if razon is not None:
                fila["r_inscripcion"] = round(float(np.corrcoef(resid, razon.loc[locs])[0, 1]), 4)
            res[p] = fila
        salida[f"{corp}_{circ}"] = res
    return {"por_corporacion": salida, "n_perm": n_perm, "eje": EJE}


def evaluar(a: dict) -> dict:
    """P1-P5 (§5) y la regla de decisión (§6)."""
    S = a["por_corporacion"][f"{PRINCIPAL[0]}_{PRINCIPAL[1]}"]
    C = a["por_corporacion"][f"{REPLICA[0]}_{REPLICA[1]}"]
    d, cd = S[DECENCIA], S[CENTRO_DEMOCRATICO]
    p1 = d["r_eje"] > UMBRAL_R and d["p"] < 0.05
    p2 = cd["r_eje"] < -UMBRAL_R and cd["p"] < 0.05
    p3 = C[DECENCIA]["r_eje"] > UMBRAL_R and C[CENTRO_DEMOCRATICO]["r_eje"] < -UMBRAL_R
    p4 = d["r2_loo"] >= 0.5 and cd["r2_loo"] >= 0.5
    insc = [abs(x.get("r_inscripcion", 0.0)) for x in (d, cd)]
    p5 = all(v < UMBRAL_INSCRIPCION for v in insc)
    # bool() explícito: los valores vienen de numpy y json no sabe escribir np.bool_
    p1, p2, p3, p4, p5 = map(bool, (p1, p2, p3, p4, p5))
    pred = {
        "P1": {"umbral": "Senado, Lista de la Decencia: r_eje > 0,5 y p < 0,05",
               "valor": [d["r_eje"], d["p"]], "se_cumple": p1},
        "P2": {"umbral": "Senado, Centro Democrático: r_eje < −0,5 y p < 0,05",
               "valor": [cd["r_eje"], cd["p"]], "se_cumple": p2},
        "P3": {"umbral": "Cámara: mismo signo y |r_eje| > 0,5 en los dos",
               "valor": [C[DECENCIA]["r_eje"], C[CENTRO_DEMOCRATICO]["r_eje"]], "se_cumple": p3},
        "P4": {"umbral": "Senado: R²_LOO ≥ 0,50 en los dos (no informativa)",
               "valor": [d["r2_loo"], cd["r2_loo"]], "se_cumple": p4},
        "P5": {"umbral": "|r con la inscripción| < 0,50 en los dos (Senado)",
               "valor": [d.get("r_inscripcion"), cd.get("r_inscripcion")], "se_cumple": p5},
    }
    if not p5:
        regla = ("Intermedio: el resto territorial sigue a la inscripción; puede ser el desajuste "
                 "entre dónde se inscribe y dónde vive la gente. No se adopta ninguna lectura.")
    elif p1 and p2 and p3:
        regla = ("A: el eje no es de un candidato; es una geografía política estable de Bogotá, "
                 "visible en el voto por partido y en el presidencial, que la composición no ve.")
    elif p1 and not p2:
        regla = ("B: el resto territorial acompaña al petrismo, no a la derecha: es el eje de un "
                 "movimiento, no izquierda–derecha.")
    elif not p1 and not p2:
        regla = "C: el eje es propio del voto presidencial; el voto por partido no lo comparte."
    else:
        regla = "Intermedio: no se adopta ninguna de las tres lecturas."
    return {"predicciones": pred, "regla": regla}


# --------------------------------------------------------------------------

def main(argv=None) -> int:
    argparse.ArgumentParser(description="Eje por partidos (pre-registro en docs/).").parse_args(argv)
    try:
        votos = pd.read_csv(ge.ELECTORAL / "congreso_2018_localidad.csv")
        zonas = pd.read_csv(ge.ELECTORAL / "congreso_2018_zonas.csv")
        partidos = verificar_decisivos(votos)
        logging.disable(logging.WARNING)
        comp = ge.composicion()
        logging.disable(logging.NOTSET)
        props = {c: proporciones_partido(votos, zonas, *c) for c in (PRINCIPAL, REPLICA)}
        a = analizar(props, comp, eje_presidencial(), partidos, ge.razon_inscripcion(),
                     eje_presidencial(EJE_SECUNDARIO))
    except (EjeError, ge.GeografiaError) as e:
        print(f"ERROR: {e}")
        return 1
    v = evaluar(a)
    SALIDA.mkdir(parents=True, exist_ok=True)
    destino = SALIDA / "resultado.json"
    destino.write_text(json.dumps({**a, **v, "partidos": partidos}, ensure_ascii=False, indent=2),
                       encoding="utf-8")
    for corp, res in a["por_corporacion"].items():
        print(f"\n{corp}")
        print(f"  {'partido':44s} {'R²LOO':>6s} {'r eje':>6s} {'p':>7s} {'r 2018':>7s} {'r insc':>7s}")
        for p, f in res.items():
            print(f"  {p[:44]:44s} {f['r2_loo']:6.2f} {f['r_eje']:6.2f} {f['p']:7.4f} "
                  f"{f.get('r_eje_secundario', float('nan')):7.2f} {f.get('r_inscripcion', float('nan')):7.2f}")
    print()
    for k, p in v["predicciones"].items():
        print(f"  {k} {'se cumple' if p['se_cumple'] else 'NO se cumple'} — {p['umbral']} (valor {p['valor']})")
    print(f"\nRegla de decisión: {v['regla']}\n\n{destino.relative_to(RAIZ).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
