"""
¿Estima la página igual con las candidatas primero y la caché? (`docs/CACHE_PAGINA_SPECIFICATION.md`).
La configuración C de `NIVEL_ACUERDO_LOTE6` (139 candidatas, Luna, 129 guardadas) con el orden de DI-NB7 y la marca
de DI-E11, contra la misma C con el orden de siempre, que ya está corrida.

Uso:
    python src/experiments/cache_pagina.py --prueba     # 2 llamadas: mide la escritura y la lectura de la caché
    python src/experiments/cache_pagina.py              # la corrida (tope USD 0,30)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import banco as ba                    # noqa: E402
from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import nivel_acuerdo as na           # noqa: E402
from src.experiments import nivel_acuerdo_lote6 as n6     # noqa: E402
from src.experiments import nivel_acuerdo_validacion as nv  # noqa: E402
from src.experiments import nivel_parecidas_b as nb       # noqa: E402

TOPE_USD = 0.30
CACHE = ba.SALIDA / "cache_cache_pagina.json"
SALIDA = ba.SALIDA / "cache_pagina.json"
CORTE = "PREGUNTA NUEVA"


def regla(nuevo: dict, viejo: dict) -> dict:
    """Pre-registro §3."""
    c = {"eam": nuevo["eam"] <= viejo["eam"] + 0.5, "lado": nuevo["lado"] >= viejo["lado"] - 0.05,
         "al_decidir": (nuevo["acierto_al_decidir"] or 0) >= 0.90 if (nuevo["dice_si"] + nuevo["dice_no"]) >= 5 else None}
    c["cumple"] = bool(c["eam"] and c["lado"] and c["al_decidir"] is not False)
    return c


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prueba", action="store_true")
    a = ap.parse_args()
    _, cand = n6.candidatas()
    o95, o6 = n6.objetivos()
    o = pd.concat([o95, o6], ignore_index=True)
    cache, llamar = e9.Cache(CACHE), e9.cliente_real(timeout=300, corte_cache=CORTE)
    if a.prueba:
        antes = nb.gastado(cache)
        nv.elegir_todas(o, cand, llamar, cache, TOPE_USD, solo=2, modelo=n6.MODELO, orden="candidatas")
        u = [v["uso"] for v in list(cache.datos.values())[-2:]]
        print(f"dos llamadas: USD {nb.gastado(cache) - antes:.4f} | costos {[x['costo_usd'] for x in u]} | "
              f"en caché {[x.get('cached_tokens') for x in u]}")
        return 0
    p = nv.elegir_todas(o, cand, llamar, cache, TOPE_USD, modelo=n6.MODELO, orden="candidatas")
    nuevo = nv.evaluar(p, cand, o, h=n6.H)
    viejo = json.loads(n6.SALIDA.read_text(encoding="utf-8"))["C"]
    r = regla(nuevo, viejo)
    vp = pd.DataFrame(viejo["por_pregunta"])[["id", "S"]].rename(columns={"S": "S_viejo"})
    j = p.merge(vp, on="id")
    misma = float(np.mean(na.llamada(j.S.to_numpy(float), np.full(len(j), n6.H)) ==
                          na.llamada(j.S_viejo.to_numpy(float), np.full(len(j), n6.H))))
    usos = [v["uso"] for v in cache.datos.values() if isinstance(v.get("uso"), dict)]
    c_nuevo = float(np.mean([x["costo_usd"] for x in usos[1:]])) if len(usos) > 1 else None
    vc = e9.Cache(n6.CACHE)
    c_viejo = float(np.mean([v["uso"]["costo_usd"] for v in vc.datos.values() if isinstance(v.get("uso"), dict)
                             and v.get("uso", {}).get("costo_usd")]))
    pred = {"PC1": r["cumple"], "PC2": misma >= 0.85, "PC3": c_nuevo is not None and c_nuevo <= 0.30 * c_viejo}
    for n, x in (("orden nuevo", nuevo), ("orden de siempre", viejo)):
        print(f"{n:16}: EAM {x['eam']:.1f} | lado {x['lado']:.0%} | decide {x['dice_si'] + x['dice_no']} "
              f"(acierta {x['acierto_al_decidir']})")
    print(f"misma llamada {misma:.0%} | costo por llamada {c_nuevo:.5f} contra {c_viejo:.5f} | regla {r} | predicciones {pred}")
    gasto = e9.gasto_registrado(cache)
    SALIDA.write_text(json.dumps({"nuevo": {k: v for k, v in nuevo.items() if k != "por_pregunta"}, "regla": r,
                                  "misma_llamada": misma, "costo_nuevo": c_nuevo, "costo_viejo": c_viejo,
                                  "predicciones": pred, "gasto": gasto}, ensure_ascii=False, indent=1, default=str),
                      encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
