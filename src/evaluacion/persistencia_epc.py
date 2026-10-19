"""
Fase A del plan de mejoras (`docs/PLAN_MEJORAS_PREDICTOR_BOGOTA.md`, §13): la vara de la persistencia en la EPC.

Para cada pregunta del catálogo medida dos años seguidos, cuánto se equivoca **repetir el dato del año anterior**. Es el problema
A del plan (pregunta ya medida). Es descriptivo: no pone a prueba ningún método, mide la referencia contra la que compiten todos.

Uso:
    python src/evaluacion/persistencia_epc.py

Sale en `data/processed/benchmark/persistencia_epc.csv` (una fila por pregunta y par de años) y se resume en
`docs/BENCHMARK_FASE_A.md`.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-BA1. **Lo que se cuenta** es el lado de la escala que muestra la página (`motor.lado`), entre quienes eligieron una opción de
    la escala, con el peso de la encuesta. Es la misma cifra que la página y las pruebas.
DI-BA2. **Solo pares de años seguidos** en que la pregunta está en el catálogo de la población 2022-2025 en los dos. Si la EPC
    cambió la pregunta entre años, el catálogo la trata como la misma: eso queda dentro del error de la persistencia, como en la
    página.
DI-BA3. **El dominio** sale del código: gobierno e instituciones (la lista política de la reformulación), seguridad, movilidad,
    servicios, espacio público, ambiente, cultura ciudadana, economía y hogar, y ciudad en general.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

SALIDA = RAIZ / "data" / "processed" / "benchmark"
ANIOS = (2022, 2023, 2024, 2025)
DOMINIOS = (("VS", "seguridad"), ("MV", "movilidad"), ("SP", "servicios"), ("EP", "espacio público"), ("MA", "ambiente"),
            ("RC", "cultura ciudadana"), ("CO", "economía y hogar"), ("AL", "economía y hogar"), ("SA", "economía y hogar"),
            ("VS7", "economía y hogar"), ("CR", "cultura y recreación"))


def dominio(var: str) -> str:
    """DI-BA3."""
    from src.consulta import reformular as rf
    if var in rf.TEMA_POLITICO_CATALOGO or var.startswith(("GG", "CC", "MICE", "GOB", "PE_")):
        return "gobierno e instituciones"
    for pref, nombre in sorted(DOMINIOS, key=lambda x: -len(x[0])):
        if var.startswith(pref):
            return nombre
    return "ciudad en general"


def cifras(anio: int) -> dict[str, float]:
    """DI-BA1: el porcentaje del lado que se cuenta, por pregunta, en la EPC de ese año."""
    from src.consulta import motor as mo
    from src.experiments import personas_con_encuesta as pc
    base, d, perf = pc.datos(anio)
    w = base.peso.to_numpy(float)
    out = {}
    for _, col, f in perf:
        cods, _ = mo.lado(f)
        x = pd.to_numeric(d[col], errors="coerce").to_numpy()
        m = np.isin(x, f["escala"]) & ~np.isnan(w)
        if m.sum() >= 100:
            out[f["variable"]] = float(100 * np.sum(w[m] * np.isin(x[m], cods)) / np.sum(w[m]))
    return out


def main() -> int:
    por_anio = {a: cifras(a) for a in ANIOS}
    filas = []
    for a, b in zip(ANIOS, ANIOS[1:]):
        for var in sorted(set(por_anio[a]) & set(por_anio[b])):                                    # DI-BA2
            filas.append({"variable": var, "dominio": dominio(var), "anio_base": a, "anio_objetivo": b,
                          "dato_base": round(por_anio[a][var], 2), "real": round(por_anio[b][var], 2),
                          "error_persistencia": round(abs(por_anio[b][var] - por_anio[a][var]), 2),
                          "cambio": round(por_anio[b][var] - por_anio[a][var], 2)})
    t = pd.DataFrame(filas)
    SALIDA.mkdir(parents=True, exist_ok=True)
    t.to_csv(SALIDA / "persistencia_epc.csv", index=False, encoding="utf-8")
    print(f"{len(t)} pares pregunta-año, {t.variable.nunique()} preguntas\n")
    print("Por par de años:")
    print(t.groupby(["anio_base", "anio_objetivo"]).error_persistencia.agg(["count", "mean", "median"]).round(1).to_string())
    print("\nPor dominio:")
    print(t.groupby("dominio").error_persistencia.agg(["count", "mean", "median", "max"]).round(1)
          .sort_values("mean").to_string())
    print(f"\nTotal: error medio {t.error_persistencia.mean():.1f}, mediana {t.error_persistencia.median():.1f}, "
          f"percentil 80 {t.error_persistencia.quantile(.8):.1f}")
    print("\nLos 8 cambios más grandes:")
    print(t.reindex(t.cambio.abs().sort_values(ascending=False).index).head(8)
          [["variable", "dominio", "anio_base", "anio_objetivo", "dato_base", "real", "cambio"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
