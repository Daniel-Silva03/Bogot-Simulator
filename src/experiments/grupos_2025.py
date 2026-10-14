"""
Precisión por grupos (`docs/GRUPOS_2025_SPECIFICATION.md`): con la población 2022-2024 se adivina, por estrato, edad y sexo,
lo que respondió la EPC 2025 en las 35 preguntas que se repitieron. Sin API.

Uso:
    python src/experiments/grupos_2025.py

DECISIONES DE IMPLEMENTACIÓN
============================

DI-GR1. **Los grupos de la página** (`motor._grupos`) para los agentes, y los mismos cortes para los encuestados de 2025:
    estrato 1-2 / 3-4 / 5-6 (`DMO_4_1`), los tramos de edad de `poblacion_epc.tramo_edad` (`DMO_3_1`) y sexo (`DMO_1`).
DI-GR2. **La media de la página por grupo** es la de los agentes con su peso, entre los que heredan a alguien de un año que
    se junta para esa pregunta (DI-CO6), como en `motor._ciudad`.
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import peso_anio_reciente as pa      # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "grupos_2025"


def grupos_2025(base: pd.DataFrame, datos: pd.DataFrame) -> dict[str, np.ndarray]:
    """DI-GR1: las etiquetas de grupo de los encuestados de 2025."""
    from src.consulta import motor as mo
    from src.population import poblacion_epc as pe
    col = {c.upper(): c for c in datos.columns}
    num = lambda c: pd.to_numeric(datos[col[c]], errors="coerce")                # noqa: E731
    falso = pd.DataFrame({"estrato": num("DMO_4_1").to_numpy(), "edad_tramo": pe.tramo_edad(num("DMO_3_1")).to_numpy(),
                          "sexo": num("DMO_1").map({1: "M", 2: "F"}).to_numpy()})
    g = mo._grupos(falso.assign(estrato=falso.estrato.fillna(99)))
    g["estrato"] = g["estrato"].where(falso.estrato.between(1, 6))
    return {k: v.to_numpy() for k, v in g.items()}


def medias(x: np.ndarray, w: np.ndarray, etq: np.ndarray, esc: list[int], orden: list[str]) -> dict[str, float]:
    ok = np.isin(x, esc)
    return {o: pa.a_100(float(np.sum(w[ok & (etq == o)] * x[ok & (etq == o)]) / np.sum(w[ok & (etq == o)])), esc)
            for o in orden if (ok & (etq == o)).any()}


def resumir(filas: pd.DataFrame) -> dict:
    """§2: E_grupo, E_ciudad y la correlación de las brechas."""
    e_g = float((filas.pagina - filas.real).abs().mean())
    e_c = float((filas.pagina_ciudad - filas.real).abs().mean())
    br_p, br_r = filas.pagina - filas.pagina_ciudad, filas.real - filas.real_ciudad
    return {"E_grupo": round(e_g, 2), "E_ciudad": round(e_c, 2),
            "correlacion_brechas": round(float(np.corrcoef(br_p, br_r)[0, 1]), 2), "n": len(filas)}


def main() -> int:
    from src.consulta import motor as mo
    from src.population import armonizar_epc as ae
    cat = {f["variable"]: f for f in json.loads((pa.POBLACION / "catalogo.json").read_text(encoding="utf-8"))["dentro"]}
    arm = pd.read_csv(ae.SALIDA / "items.csv")
    con_2025 = [v for v, a in zip(arm.variable, arm.anios.astype(str)) if "2025" in a.split()]
    inv = pd.read_csv(ae.INVENTARIO)
    inv = inv[(inv.estado == "ok") & (inv.anio == 2025)].set_index("variable").codigo
    don = pd.read_parquet(pa.POBLACION / "donantes.parquet")
    col = {c.upper(): c for c in don.columns}
    ag = pd.read_parquet(pa.POBLACION / "agentes.parquet")
    ag = ag[ag.donante_id.notna()].reset_index(drop=True)
    idx = ag.donante_id.astype(int).to_numpy()
    peso, anio = ag.peso.to_numpy(float), don.anio.to_numpy()[idx]
    g_ag = {k: v.to_numpy() for k, v in mo._grupos(ag).items()}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        b25, o25 = ae.cargar_ola(2025)
    g_25 = grupos_2025(b25, o25["datos"])
    w25 = b25.peso.to_numpy(float)
    filas = []
    for v in con_2025:
        f = mo.vista(cat[v])
        esc = list(f["escala"])
        x = pd.to_numeric(don[col[str(f["codigo"]).upper()]], errors="coerce").to_numpy(float)[idx]
        x = np.where(np.isin(anio, cat[v]["anios"]), x, np.nan)                                     # DI-GR2
        x25 = pd.to_numeric(o25["datos"][o25["col"][str(inv[v]).upper()]], errors="coerce").to_numpy(float)
        ok_a, ok_25 = np.isin(x, esc), np.isin(x25, esc)
        ciudad_p = pa.a_100(float(np.sum(peso[ok_a] * x[ok_a]) / np.sum(peso[ok_a])), esc)
        ciudad_r = pa.a_100(float(np.sum(w25[ok_25] * x25[ok_25]) / np.sum(w25[ok_25])), esc)
        for dim, info in mo.GRUPOS.items():
            mp = medias(x, peso, g_ag[dim], esc, info["orden"])
            mr = medias(x25, w25, g_25[dim], esc, info["orden"])
            for o in info["orden"]:
                if o in mp and o in mr:
                    filas.append({"variable": v, "dimension": dim, "grupo": o, "pagina": mp[o], "real": mr[o],
                                  "pagina_ciudad": ciudad_p, "real_ciudad": ciudad_r,
                                  "n_2025": int((ok_25 & (g_25[dim] == o)).sum())})
    t = pd.DataFrame(filas)
    total = resumir(t)
    por_dim = {d: resumir(t[t.dimension == d]) for d in mo.GRUPOS}
    regla = {"R1": total["E_grupo"] <= total["E_ciudad"] - 0.5, "R2": total["correlacion_brechas"] >= 0.5}
    regla["aportan"] = all(regla.values())
    corr = {d: por_dim[d]["correlacion_brechas"] for d in por_dim}
    pred = {"PG1": regla["aportan"], "PG2": max(corr, key=corr.get) == "estrato" and min(corr, key=corr.get) == "sexo",
            "PG3": 5 <= total["E_grupo"] <= 8}
    print(f"{len(con_2025)} preguntas, {len(t)} pares pregunta × grupo")
    print(f"total: {total}")
    for d, r in por_dim.items():
        print(f"  {d}: {r} | encuestados 2025 por grupo, mediana {int(t[t.dimension == d].n_2025.median())}")
    print(f"regla: {regla} | predicciones: {pred}")
    SALIDA.mkdir(parents=True, exist_ok=True)
    t.to_csv(SALIDA / "por_pregunta_y_grupo.csv", index=False, encoding="utf-8")
    (SALIDA / "resultado.json").write_text(json.dumps({"total": total, "por_dimension": por_dim, "regla": regla,
                                                       "predicciones": pred}, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
