"""
¿Estaría Bogotá de acuerdo?, paso 2 (`docs/NIVEL_ACUERDO_SONNET_SPECIFICATION.md`): Claude Sonnet elige
preguntas parecidas entre las de acuerdo o de sí/no de práctica; la predicción es la media real de las
elegidas. La tarea es la de `nivel_parecidas_b`; los datos y la medida, los de `nivel_acuerdo`.

Uso:
    python src/experiments/nivel_acuerdo_sonnet.py --simulado     # sin gasto
    python src/experiments/nivel_acuerdo_sonnet.py --prueba       # 1 llamada, mide el costo
    python src/experiments/nivel_acuerdo_sonnet.py                # la corrida (tope USD 3)

Escribe `data/processed/banco/nivel_acuerdo_sonnet.json`; caché en `cache_nivel_acuerdo.json` (no se sube).
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
from src.experiments import nivel_parecidas_b as nb       # noqa: E402

MODELO = nb.MODELOS["sonnet"]
TOPE_USD = 3.0
CACHE = ba.SALIDA / "cache_nivel_acuerdo.json"
SALIDA = ba.SALIDA / "nivel_acuerdo_sonnet.json"
LADO_MIN = 0.67                        # §3: 0,57 + 0,10
EAM_MAX = 15.8                         # §3: 0,8 × 19,7


def evaluar(t: pd.DataFrame, p: pd.DataFrame) -> dict:
    """Las medidas de `nivel_acuerdo` para la columna de Sonnet."""
    q = na.predecir(t)[["id", "familia", "total", "M0", "M1", "referencia_si"]].merge(p[["id", "pred", "fallo"]], on="id")
    q = q.rename(columns={"pred": "S"})
    real_si = q.total.to_numpy() > 50
    h = na.rangos(q, "S")
    d = na.llamada(q.S.to_numpy(), h)
    dec = d != "dividida"
    r = {"n": len(q), "eam": float(np.mean(np.abs(q.S - q.total))), "lado": float(np.mean((q.S > 50) == real_si)),
         "decide": float(dec.mean()), "acierto_al_decidir": float(np.mean((d[dec] == "sí") == real_si[dec])) if dec.any() else None,
         "dice_si": int((d == "sí").sum()), "acierta_si": int(((d == "sí") & real_si).sum()),
         "dice_no": int((d == "no").sum()), "acierta_no": int(((d == "no") & ~real_si).sum()),
         "fallos": int(q.fallo.sum()), "referencia_lado": float(np.mean(q.referencia_si.to_numpy() == real_si))}
    r["sirve"] = bool(r["lado"] >= LADO_MIN and r["eam"] <= EAM_MAX)
    r["predicciones"] = {"P1": not r["sirve"], "P2": r["eam"] < 18.2, "P3": r["lado"] > 0.63, "P4": r["decide"] < 0.30}
    r["por_pregunta"] = q.assign(llamada=d, h=h).to_dict("records")
    return r


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    ap.add_argument("--prueba", action="store_true")
    a = ap.parse_args()
    t = na.tabla()
    if a.simulado:
        cache, llamar = e9.Cache(Path(tempfile.gettempdir()) / "bss_acuerdo_simulado.json"), nb.cliente_simulado(t)
    else:
        cache, llamar = e9.Cache(CACHE), e9.cliente_real(timeout=300)
    if a.prueba:
        antes = nb.gastado(cache)
        nb.correr(t, llamar, cache, MODELO, tope=TOPE_USD, solo=1)
        c = nb.gastado(cache) - antes
        print(f"una llamada costó USD {c:.4f} → las {len(t)} costarían ~USD {len(t) * c:.2f} (tope USD {TOPE_USD})")
        return 0
    p = nb.correr(t, llamar, cache, MODELO, tope=TOPE_USD)
    r = evaluar(t, p)
    r["gasto"] = None if a.simulado else e9.gasto_registrado(cache)
    print(f"Sonnet: EAM {r['eam']:.1f} (máx {EAM_MAX}) | lado {r['lado']:.0%} (mín {LADO_MIN:.0%}; referencia "
          f"{r['referencia_lado']:.0%}) | decide {r['decide']:.0%} («sí» {r['acierta_si']}/{r['dice_si']}, «no» "
          f"{r['acierta_no']}/{r['dice_no']}) | fallos {r['fallos']} | sirve: {r['sirve']}")
    print(f"predicciones: {r['predicciones']}; gasto: {r['gasto'] and round(r['gasto']['costo_usd'], 4)}")
    if not a.simulado:
        SALIDA.write_text(json.dumps(r, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
