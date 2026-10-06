"""
¿Estaría Bogotá de acuerdo?, con GPT-6 Luna (`docs/NIVEL_ACUERDO_LUNA_SPECIFICATION.md`): el método de D19 en
la práctica (92, como Sonnet y mimo) y en el guardado (95 con las 109 candidatas de la página, como la
configuración B de `nivel_acuerdo_lote5`), con `openai/gpt-6-luna` en lugar de Claude Sonnet. Mismas
funciones que las pruebas anteriores; solo cambia el modelo.

Uso:
    python src/experiments/nivel_acuerdo_luna.py --simulado     # sin gasto
    python src/experiments/nivel_acuerdo_luna.py --prueba       # 1 llamada, mide el costo
    python src/experiments/nivel_acuerdo_luna.py                # la corrida (tope USD 0,75)

Escribe `data/processed/banco/nivel_acuerdo_luna.json`; caché en `cache_nivel_acuerdo_luna.json` (no se sube).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-NLU1. **Un error del servicio detiene la corrida.** `nivel_parecidas_b.elegir` no atrapa los errores de
    red ni de HTTP (a diferencia de `Motor.estimar` antes de DI-CO24), así que un 402 o una caída cortan la
    corrida con su error; lo pagado queda en la caché y una nueva corrida sigue desde ahí.
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
from src.experiments import nivel_acuerdo_lote5 as nl     # noqa: E402
from src.experiments import nivel_acuerdo_sonnet as ns    # noqa: E402
from src.experiments import nivel_acuerdo_validacion as nv  # noqa: E402
from src.experiments import nivel_parecidas_b as nb       # noqa: E402

MODELO = "openai/gpt-6-luna"
TOPE_USD = 0.75
CACHE = ba.SALIDA / "cache_nivel_acuerdo_luna.json"
SALIDA = ba.SALIDA / "nivel_acuerdo_luna.json"
DECIDIR_MIN = 0.90
EAM_SONNET_GUARDADO = 11.9                                   # NIVEL_ACUERDO_LOTE5_RESULTS.md, configuración B
MARGEN_SONNET = 1.5


def regla(prac: dict, guar: dict) -> dict:
    """Pre-registro §3."""
    dec = prac["dice_si"] + prac["dice_no"] + guar["dice_si"] + guar["dice_no"]
    ac = prac["acierta_si"] + prac["acierta_no"] + guar["acierta_si"] + guar["acierta_no"]
    c = {"practica": prac["eam"] <= ns.EAM_MAX and prac["lado"] >= ns.LADO_MIN,
         "guardado": guar["pasa"],
         "al_decidir": (ac / dec >= DECIDIR_MIN) if dec else False,
         "cerca_de_sonnet": guar["eam"] <= EAM_SONNET_GUARDADO + MARGEN_SONNET}
    return {**c, "cumple": all(c.values()), "acierto_al_decidir_total": ac / dec if dec else None, "decisiones": dec}


def guardado() -> tuple[pd.DataFrame, pd.DataFrame]:
    """(las 95 guardadas, las 109 candidatas de la página)."""
    o74, o21 = nl.objetivos()
    return pd.concat([o74, o21], ignore_index=True), nl.candidatas()[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    ap.add_argument("--prueba", action="store_true")
    a = ap.parse_args()
    t = na.tabla()
    objetivo, cand = guardado()
    if a.simulado:
        cache, llamar = e9.Cache(Path(tempfile.gettempdir()) / "bss_luna_simulado.json"), nb.cliente_simulado(cand)
    else:
        cache, llamar = e9.Cache(CACHE), e9.cliente_real(timeout=300)
    if a.prueba:
        antes = nb.gastado(cache)
        nb.correr(t, llamar, cache, MODELO, tope=TOPE_USD, solo=1)
        c = nb.gastado(cache) - antes
        n = len(t) + len(objetivo)
        print(f"una llamada costó USD {c:.4f} → las {n} costarían ~USD {n * c:.2f} (tope USD {TOPE_USD})")
        return 0
    pp = nb.correr(t, llamar, cache, MODELO, tope=TOPE_USD)                   # práctica
    prac = ns.evaluar(t, pp)
    q = prac["por_pregunta"]
    h = float(np.quantile([abs(x["S"] - x["total"]) for x in q], 0.8))      # §2: fijado antes de evaluar el guardado
    pg = nv.elegir_todas(objetivo, cand, llamar, cache, TOPE_USD, modelo=MODELO)  # guardado
    guar = nv.evaluar(pg, cand, objetivo, h=h)
    r = regla(prac, guar)
    pred = {"P1": not r["cumple"], "P2": prac["eam"] > 13.9, "P3": prac["lado"] < 0.80,
            "P4": prac["fallos"] + guar["fallos"] >= 1}
    gasto = None if a.simulado else e9.gasto_registrado(cache)
    for nombre, x in (("práctica", prac), ("guardado", guar)):
        print(f"{nombre}: EAM {x['eam']:.1f} | lado {x['lado']:.0%} (referencia {x['referencia_lado']:.0%}) | decide "
              f"{x['decide']:.0%} («sí» {x['acierta_si']}/{x['dice_si']}, «no» {x['acierta_no']}/{x['dice_no']}) | fallos {x['fallos']}")
    print(f"h fijado con la práctica: {h:.1f} | regla: {r} | predicciones: {pred} | gasto: {gasto and round(gasto['costo_usd'], 4)}")
    if not a.simulado:
        SALIDA.write_text(json.dumps({"modelo": MODELO, "h": h, "practica": prac, "guardado": guar, "regla": r,
                                      "predicciones": pred, "gasto": gasto}, ensure_ascii=False, indent=1, default=str),
                          encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
