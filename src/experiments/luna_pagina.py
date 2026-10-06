"""
La reformulación y el puente con GPT-6 Luna (`docs/LUNA_PAGINA_SPECIFICATION.md`).

Parte 1: las 24 de `reformular.PRUEBA` con Luna, contra R1-R4. Parte 2: las 95 guardadas reformuladas con Luna
y estimadas con `Motor.estimar` (Luna), contra la parte A de `NIVEL_ACUERDO_REDACCION` (reformuladas con mimo).
Parte 3: `puente_sin_base` con Luna, contra R1, R2 y P2.

Uso:
    python src/experiments/luna_pagina.py --simulado     # partes 1 y 2 sin gasto
    python src/experiments/luna_pagina.py --prueba       # 1 reformulación con Luna, mide el costo
    python src/experiments/luna_pagina.py                # las tres partes (tope USD 0,75)

DECISIONES DE IMPLEMENTACIÓN
============================

DI-LP1. **Una caché para las partes 1 y 2** (`data/processed/banco/cache_luna_pagina.json`) y la del puente en
    su propia carpeta (`data/processed/puente_sin_base/luna/`), como hace `puente_sin_base`. El tope cuenta las
    dos.
DI-LP2. **La parte 3 confirma el gasto sola**, porque Daniel ya aprobó la corrida completa: se le pasa a
    `puente_sin_base.main` una entrada que contesta «si».
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

from src.consulta import motor as mo                       # noqa: E402
from src.consulta import reformular as rf                  # noqa: E402
from src.experiments import banco as ba                    # noqa: E402
from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import nivel_acuerdo as na           # noqa: E402
from src.experiments import nivel_acuerdo_redaccion as nr  # noqa: E402
from src.experiments import nivel_parecidas_b as nb       # noqa: E402
from src.experiments import puente_sin_base as ps         # noqa: E402

LUNA = "openai/gpt-6-luna"
TOPE_USD = 0.75
CACHE = ba.SALIDA / "cache_luna_pagina.json"
SALIDA = ba.SALIDA / "luna_pagina.json"
CARPETA_PUENTE = "luna"


def gasto_total(cache: e9.Cache) -> float:
    c = ps.SALIDA / CARPETA_PUENTE / "cache.json"
    return nb.gastado(cache) + (nb.gastado(e9.Cache(c)) if c.exists() else 0.0)


# ---------------------------------------------------------------- parte 1
def parte1(llamar, cache, modelo: str = LUNA) -> dict:
    cat = rf.cargar_catalogo()
    resp = [rf.reformular(p, cat, llamar, cache, modelo)[0] for p, _, _ in rf.PRUEBA]
    ev = rf.evaluar(resp)
    ev["por_pregunta"] = [{"pregunta": p, "esperado": [a, c], "obtenido": [r["alcance"], r.get("codigo")] if r else None,
                           "reformulada": (r or {}).get("reformulada")} for (p, a, c), r in zip(rf.PRUEBA, resp)]
    return ev


# ---------------------------------------------------------------- parte 2
def comparar(luna: pd.DataFrame, mimo: pd.DataFrame, h: float) -> dict:
    """§3: sobre las que quedan `nueva` con estimación en los dos flujos."""
    j = luna.merge(mimo[["id", "alcance", "S"]].rename(columns={"alcance": "alcance_mimo", "S": "S_mimo"}), on="id")
    ambos = j[(j.alcance == "nueva") & (j.alcance_mimo == "nueva") & j.S.notna() & j.S_mimo.notna()]
    ml, mm = nr.medir(ambos.S, ambos.total, h), nr.medir(ambos.S_mimo, ambos.total, h)
    ll = na.llamada(ambos.S.to_numpy(float), np.full(len(ambos), h))
    lm = na.llamada(ambos.S_mimo.to_numpy(float), np.full(len(ambos), h))
    regla = {"eam": ml["eam"] <= mm["eam"] + 0.5, "lado": ml["lado"] >= mm["lado"] - 0.05}
    regla["cumple"] = all(regla.values())
    return {"n_ambos": int(len(ambos)), "luna": ml, "mimo": mm, "misma_llamada": float(np.mean(ll == lm)) if len(ambos) else None,
            "alcances_luna": j.alcance.value_counts().to_dict(), "alcances_mimo": j.alcance_mimo.value_counts().to_dict(),
            "regla": regla, "por_pregunta": j.to_dict("records")}


def parte2(llamar, cache, mimo: pd.DataFrame, tope: float) -> dict:
    o74, o21 = nr.nl.objetivos()
    o95 = pd.concat([o74, o21], ignore_index=True)
    res = nr.correr_a(o95, llamar, llamar, cache, tope, modelo_ref=LUNA)
    return comparar(res, mimo, mo.H_ESTIMACION)


def mimo_parte_a() -> pd.DataFrame:
    """La parte A con Luna en la estimación (enmienda 2 de NIVEL_ACUERDO_REDACCION)."""
    d = json.loads(nr.SALIDA.read_text(encoding="utf-8"))["A"]
    if d.get("modelo") != LUNA:
        raise RuntimeError("La parte A con Luna no ha terminado: falta la columna con mimo de la parte 2.")
    return pd.DataFrame(d["por_pregunta"])


# ---------------------------------------------------------------- parte 3
def parte3() -> dict:
    codigo = ps.main(["--modelo", LUNA, "--salida", CARPETA_PUENTE], entrada=lambda _: "si")   # DI-LP2
    if codigo != 0:
        raise RuntimeError("La prueba del puente con Luna no terminó.")
    r = json.loads((ps.SALIDA / CARPETA_PUENTE / "resultado.json").read_text(encoding="utf-8"))
    p = r["predicciones"]
    regla = {k: p[k]["se_cumple"] for k in ("R1", "R2", "P2")}
    regla["cumple"] = all(regla.values())
    return {"predicciones": p, "regla": regla, "gasto": r.get("gasto")}


def predicciones(p1: dict, p2: dict, p3: dict) -> dict:
    return {"PL1": p1["pasa"], "PL2": p2["regla"]["cumple"], "PL3": p3["regla"]["cumple"],
            "PL4": p3["predicciones"]["P1"]["cuenta"] > 5}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    ap.add_argument("--prueba", action="store_true")
    a = ap.parse_args()
    if a.simulado:
        cache = e9.Cache(Path(tempfile.gettempdir()) / "bss_luna_pagina_simulado.json")
        llamar, _ = mo.cliente(simulado=True)
        p1 = parte1(llamar, cache, modelo=e9.MODELO_SIMULADO)
        print(f"parte 1 (simulada): pasa {p1['pasa']}")
        return 0
    cache, llamar = e9.Cache(CACHE), e9.cliente_real(timeout=300)
    if a.prueba:
        antes = nb.gastado(cache)
        rf.reformular(rf.PRUEBA[0][0], rf.cargar_catalogo(), llamar, cache, LUNA)
        c = nb.gastado(cache) - antes
        print(f"una reformulación con Luna costó USD {c:.4f}")
        return 0
    mimo = mimo_parte_a()
    p1 = parte1(llamar, cache)
    print(f"parte 1: {({k: v['valor'] for k, v in p1['criterios'].items()})} → pasa {p1['pasa']}", flush=True)
    try:
        p2 = parte2(llamar, cache, mimo, TOPE_USD)
    except (nr.TopeAlcanzado, mo.ServicioNoDisponible) as e:
        print(e)
        return 1
    print(f"parte 2: {p2['n_ambos']} en los dos | EAM Luna {p2['luna']['eam']:.1f} contra mimo {p2['mimo']['eam']:.1f} | "
          f"lado {p2['luna']['lado']:.0%} contra {p2['mimo']['lado']:.0%} | misma llamada {p2['misma_llamada']:.0%} | "
          f"alcances Luna {p2['alcances_luna']} mimo {p2['alcances_mimo']} → cumple {p2['regla']['cumple']}", flush=True)
    if gasto_total(cache) >= TOPE_USD:
        print(f"tope de USD {TOPE_USD} alcanzado antes de la parte 3")
        return 1
    p3 = parte3()
    print(f"parte 3: {p3['regla']}")
    pred = predicciones(p1, p2, p3)
    gasto = round(gasto_total(cache), 4)
    print(f"reformulación a Luna: {p1['pasa'] and p2['regla']['cumple']} | puente a Luna: {p3['regla']['cumple']} | "
          f"predicciones {pred} | gasto USD {gasto}")
    SALIDA.write_text(json.dumps({"parte1": p1, "parte2": p2, "parte3": p3, "predicciones": pred,
                                  "reformulacion_a_luna": p1["pasa"] and p2["regla"]["cumple"],
                                  "puente_a_luna": p3["regla"]["cumple"], "gasto_usd": gasto},
                                 ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
