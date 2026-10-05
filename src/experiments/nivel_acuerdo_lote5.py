"""
¿Mejora la estimación de D19 con las candidatas del lote 5? (`docs/NIVEL_ACUERDO_LOTE5_SPECIFICATION.md`).
Configuración A: las 92 candidatas validadas. B: esas más las 17 de práctica del lote 5. Objetivos: las 95
preguntas guardadas de acuerdo o sí/no (74 de los lotes 1 a 3 y 21 del lote 5).

Uso:
    python src/experiments/nivel_acuerdo_lote5.py --reales     # resultados reales del guardado del lote 5 (sin API)
    python src/experiments/nivel_acuerdo_lote5.py --simulado   # sin gasto
    python src/experiments/nivel_acuerdo_lote5.py --prueba     # 1 llamada de B, mide el costo
    python src/experiments/nivel_acuerdo_lote5.py              # la corrida (tope USD 3,50)

DECISIONES DE IMPLEMENTACIÓN
============================

DI-NL1. **A en los 74 se reutiliza** de `nivel_acuerdo_validacion.json`: es exactamente la configuración A
    sobre esos objetivos, y volver a pedirla daría lo mismo (temperatura 0, misma caché de prompt).
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import banco as ba                    # noqa: E402
from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import nivel_acuerdo as na           # noqa: E402
from src.experiments import nivel_acuerdo_validacion as nv  # noqa: E402
from src.experiments import nivel_parecidas_b as nb       # noqa: E402

TOPE_USD = 3.50
CACHE = ba.SALIDA / "cache_nivel_acuerdo_lote5.json"
SALIDA = ba.SALIDA / "nivel_acuerdo_lote5.json"
REALES5 = ba.SALIDA / "reales_guardado_lote5.json"
COLS = ["id", "familia", "ambito", "fuente", "pregunta_pagina", "categorias", "codigos_favorables", "total"]


def _lote5(conjunto: str, reales: dict) -> pd.DataFrame:
    s = pd.read_csv(ba.SALIDA / "sorteo_lote5.csv")
    s = s[s.conjunto == conjunto].copy()
    s = s[s.id.map(lambda i: i in reales and not reales[i]["excluida"] and reales[i]["total"] is not None)]
    return s.assign(total=s.id.map(lambda i: float(reales[i]["total"])))


def candidatas() -> tuple[pd.DataFrame, pd.DataFrame]:
    """(A, B)."""
    a = na.tabla()
    a = a.assign(fuente=a.id.map(_fuentes()))
    p5 = _lote5("practica", json.loads((ba.SALIDA / "reales_practica_lote5.json").read_text(encoding="utf-8")))
    b = pd.concat([a[COLS], p5[COLS]], ignore_index=True)
    return a[COLS], b


def _fuentes() -> dict:
    s = pd.concat([pd.read_csv(f) for f in sorted(ba.SALIDA.glob("sorteo*.csv"))])
    return dict(zip(s.id, s.fuente))


def objetivos() -> tuple[pd.DataFrame, pd.DataFrame]:
    """(74 de los lotes 1 a 3, 21 del lote 5)."""
    o = nv.tabla_objetivo(nv.objetivos(), json.loads(nv.REALES.read_text(encoding="utf-8")))
    g5 = _lote5("guardado", json.loads(REALES5.read_text(encoding="utf-8")))
    return o[COLS], g5[COLS]


def reales_guardado_lote5() -> dict:
    from src.experiments import banco_lote3 as b3
    from src.experiments import banco_lote5 as b5
    s = pd.read_csv(ba.SALIDA / "sorteo_lote5.csv")
    s = s[s.conjunto == "guardado"].assign(conjunto="practica")             # copia: el archivo no cambia
    r = b3._calcular(s, *b5.base_edp())
    return {k: {"total": v["total"], "n": v["n"], "excluida": v["excluida"], "fuente": v["fuente"]} for k, v in r.items()}


def regla(ra: dict, rb: dict) -> dict:
    """Pre-registro §4."""
    c = {"b_pasa_validacion": rb["pasa"], "b_no_peor": rb["eam"] <= ra["eam"],
         "b_al_decidir": (rb["acierto_al_decidir"] or 0) >= 0.90 if rb["decide"] > 0 else False}
    return {**c, "b_reemplaza_a_a": all(c.values())}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reales", action="store_true")
    ap.add_argument("--simulado", action="store_true")
    ap.add_argument("--prueba", action="store_true")
    a = ap.parse_args()
    if a.reales:
        r = reales_guardado_lote5()
        REALES5.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{len(r)} guardadas del lote 5; excluidas {[k for k, v in r.items() if v['excluida']]}")
        return 0
    cand_a, cand_b = candidatas()
    o74, o21 = objetivos()
    o95 = pd.concat([o74, o21], ignore_index=True)
    if a.simulado:
        cache, llamar = e9.Cache(Path(tempfile.gettempdir()) / "bss_lote5_simulado.json"), nb.cliente_simulado(cand_b)
    else:
        cache, llamar = e9.Cache(CACHE), e9.cliente_real(timeout=300)
    if a.prueba:
        antes = nb.gastado(cache)
        nv.elegir_todas(o95, cand_b, llamar, cache, TOPE_USD, solo=1)
        c = nb.gastado(cache) - antes
        print(f"una llamada de B costó USD {c:.4f} → las 116 costarían ~USD {116 * c:.2f} (tope USD {TOPE_USD})")
        return 0
    prev = pd.DataFrame(json.loads((ba.SALIDA / "nivel_acuerdo_validacion.json").read_text(encoding="utf-8"))["por_pregunta"])
    a74 = prev[["id", "familia", "total", "S", "fallo"]]                    # DI-NL1
    a21 = nv.elegir_todas(o21, cand_a, llamar, cache, TOPE_USD)
    pa = pd.concat([a74, a21[["id", "familia", "total", "S", "fallo"]]], ignore_index=True)
    pb = nv.elegir_todas(o95, cand_b, llamar, cache, TOPE_USD)
    ra, rb = nv.evaluar(pa, cand_a, o95), nv.evaluar(pb, cand_b, o95)
    sub = {k: nv.evaluar(p[p.id.isin(o21.id)], c, o21) for k, p, c in (("A", pa, cand_a), ("B", pb, cand_b))}
    sub74 = {k: nv.evaluar(p[p.id.isin(o74.id)], c, o74) for k, p, c in (("A", pa, cand_a), ("B", pb, cand_b))}
    r = regla(ra, rb)
    pred = {"P1": r["b_reemplaza_a_a"], "P2": sub["B"]["eam"] <= sub["A"]["eam"] - 2,
            "P3": abs(sub74["B"]["eam"] - sub74["A"]["eam"]) < 1, "P4": rb["decide"] > ra["decide"]}
    for n, x in (("A", ra), ("B", rb)):
        print(f"{n} (95): EAM {x['eam']:.1f} | lado {x['lado']:.0%} (ref {x['referencia_lado']:.0%}) | decide {x['decide']:.0%} "
              f"(«sí» {x['acierta_si']}/{x['dice_si']}, «no» {x['acierta_no']}/{x['dice_no']}) | pasa {x['pasa']}")
    for n in ("A", "B"):
        print(f"  {n} solo lote 5 (21): EAM {sub[n]['eam']:.1f} lado {sub[n]['lado']:.0%} | lotes 1-3 (74): EAM {sub74[n]['eam']:.1f}")
    gasto = None if a.simulado else e9.gasto_registrado(cache)
    print(f"regla: {r} | predicciones: {pred} | gasto: {gasto and round(gasto['costo_usd'], 4)}")
    if not a.simulado:
        SALIDA.write_text(json.dumps({"A": ra, "B": rb, "lote5": sub, "lotes1_3": sub74, "regla": r, "predicciones": pred,
                                      "gasto": gasto}, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
