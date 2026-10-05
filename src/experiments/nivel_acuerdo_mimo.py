"""
¿Estaría Bogotá de acuerdo?, con mimo (`docs/NIVEL_ACUERDO_MIMO_SPECIFICATION.md`): el método de D19 en la
práctica (92) y en el guardado (74), con `xiaomi/mimo-v2.6-pro` en lugar de Claude Sonnet. Mismas funciones
que las pruebas de Sonnet (`nivel_acuerdo_sonnet`, `nivel_acuerdo_validacion`); solo cambia el modelo.

Uso:
    python src/experiments/nivel_acuerdo_mimo.py --simulado     # sin gasto
    python src/experiments/nivel_acuerdo_mimo.py --prueba       # 1 llamada, mide el costo
    python src/experiments/nivel_acuerdo_mimo.py                # la corrida (tope USD 1,50)

Escribe `data/processed/banco/nivel_acuerdo_mimo.json`; caché en `cache_nivel_acuerdo_mimo.json` (no se sube).
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import banco as ba                    # noqa: E402
from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import nivel_acuerdo as na           # noqa: E402
from src.experiments import nivel_acuerdo_sonnet as ns    # noqa: E402
from src.experiments import nivel_acuerdo_validacion as nv  # noqa: E402
from src.experiments import nivel_parecidas_b as nb       # noqa: E402

MODELO = e9.MODELO                                           # xiaomi/mimo-v2.6-pro, el de la página
TOPE_USD = 1.50
CACHE = ba.SALIDA / "cache_nivel_acuerdo_mimo.json"
SALIDA = ba.SALIDA / "nivel_acuerdo_mimo.json"
DECIDIR_MIN = 0.90


def regla(prac: dict, guar: dict) -> dict:
    """Pre-registro §3."""
    dec = prac["dice_si"] + prac["dice_no"] + guar["dice_si"] + guar["dice_no"]
    ac = prac["acierta_si"] + prac["acierta_no"] + guar["acierta_si"] + guar["acierta_no"]
    c = {"practica": prac["eam"] <= ns.EAM_MAX and prac["lado"] >= ns.LADO_MIN,
         "guardado": guar["pasa"],
         "al_decidir": (ac / dec >= DECIDIR_MIN) if dec else False}
    return {**c, "cumple": all(c.values()), "acierto_al_decidir_total": ac / dec if dec else None, "decisiones": dec}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    ap.add_argument("--prueba", action="store_true")
    a = ap.parse_args()
    t = na.tabla()
    objetivo = nv.tabla_objetivo(nv.objetivos(), json.loads(nv.REALES.read_text(encoding="utf-8")))
    if a.simulado:
        cache, llamar = e9.Cache(Path(tempfile.gettempdir()) / "bss_mimo_simulado.json"), nb.cliente_simulado(t)
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
    pg = nv.elegir_todas(objetivo, t, llamar, cache, TOPE_USD, modelo=MODELO)  # guardado
    guar = nv.evaluar(pg, t, objetivo, h=h)
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
