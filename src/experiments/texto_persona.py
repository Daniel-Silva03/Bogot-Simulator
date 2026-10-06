"""
¿Estimar con el texto de la persona o con el reformulado? (`docs/TEXTO_PERSONA_SPECIFICATION.md`).

Brazo R: lo de hoy (reformulada con Luna y estimada con Luna), leído de `luna_pagina.json`. Brazo T: el texto
original con la escala de la reformulación, estimado con `Motor.estimar`.

Uso:
    python src/experiments/texto_persona.py --simulado   # sin gasto
    python src/experiments/texto_persona.py --prueba     # 1 estimación, mide el costo
    python src/experiments/texto_persona.py              # la corrida (tope USD 0,40)

DECISIONES DE IMPLEMENTACIÓN
============================

DI-TP1. **La escala de la reformulación se lee de la caché de `LUNA_PAGINA`** con un cliente que falla si
    tuviera que llamar: así T usa exactamente la escala que la página habría mostrado, y no se paga dos veces.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.consulta import motor as mo                       # noqa: E402
from src.consulta import reformular as rf                  # noqa: E402
from src.experiments import banco as ba                    # noqa: E402
from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import luna_pagina as lp             # noqa: E402
from src.experiments import nivel_acuerdo_redaccion as nr  # noqa: E402
from src.experiments import nivel_parecidas_b as nb       # noqa: E402

TOPE_USD = 0.40
CACHE = ba.SALIDA / "cache_texto_persona.json"
SALIDA = ba.SALIDA / "texto_persona.json"
MIN_DECIDIR = 5


def _no_llamar(*_):
    raise RuntimeError("DI-TP1: la reformulación debía estar en la caché de LUNA_PAGINA")


def brazo_r() -> pd.DataFrame:
    p = pd.DataFrame(json.loads(lp.SALIDA.read_text(encoding="utf-8"))["parte2"]["por_pregunta"])
    return p[(p.alcance == "nueva") & p.S.notna()][["id", "familia", "total", "S"]].reset_index(drop=True)


def objetivos(r: pd.DataFrame) -> pd.DataFrame:
    o74, o21 = nr.nl.objetivos()
    o = pd.concat([o74, o21], ignore_index=True)
    return o[o.id.isin(r.id)].set_index("id").loc[r.id].reset_index()


def escala_reformulada(texto: str, cat: dict, cache_ref: e9.Cache) -> list[str]:
    r, _ = rf.reformular(texto[:500], cat, _no_llamar, cache_ref, lp.LUNA)
    return r["escala"]


def correr_t(o: pd.DataFrame, llamar, cache: e9.Cache, cache_ref: e9.Cache, tope: float, solo=None,
             escalas=None) -> pd.DataFrame:
    cat = rf.cargar_catalogo()
    est = nr.estimador(llamar, cache)
    filas = []
    for i in range(len(o) if solo is None else solo):
        q = o.iloc[i]
        if nb.gastado(cache) >= tope:
            raise nr.TopeAlcanzado(f"tope de USD {tope} alcanzado en la pregunta {i}")
        esc = escalas[i] if escalas is not None else escala_reformulada(q.pregunta_pagina, cat, cache_ref)
        e = mo.Motor.estimar(est, q.pregunta_pagina.strip(), esc)
        filas.append({"id": q.id, "total": float(q.total), "S": e["porcentaje"] if e else None})
        if (i + 1) % 10 == 0:
            print(f"  {i + 1} preguntas, gasto registrado USD {nb.gastado(cache):.3f}", flush=True)
    return pd.DataFrame(filas)


def evaluar(r: pd.DataFrame, t: pd.DataFrame, h: float) -> dict:
    j = r.merge(t.rename(columns={"S": "S_T"})[["id", "S_T"]], on="id")
    sin_t = int(j.S_T.isna().sum())
    j = j[j.S_T.notna()]
    mr, mt = nr.medir(j.S, j.total, h), nr.medir(j.S_T, j.total, h)
    ex = nr.extremas(j.total)
    e = lambda s, m: float((s - j.total).abs()[m].mean()) if m.any() else None    # noqa: E731
    por = {"extremas": {"R": e(j.S, ex), "T": e(j.S_T, ex)}, "intermedias": {"R": e(j.S, ~ex), "T": e(j.S_T, ~ex)}}
    regla = {"eam": mt["eam"] <= mr["eam"] - 1.0, "lado": mt["lado"] >= mr["lado"],
             "al_decidir": (mt["acierto_al_decidir"] >= 0.90) if mt["n_decide"] >= MIN_DECIDIR else None}
    regla["cumple"] = bool(regla["eam"] and regla["lado"] and regla["al_decidir"] is not False)
    pred = {"PT1": mt["eam"] < mr["eam"], "PT2": regla["cumple"], "PT3": mt["n_decide"] > mr["n_decide"],
            "PT4": (por["extremas"]["R"] - por["extremas"]["T"]) > (por["intermedias"]["R"] - por["intermedias"]["T"])}
    return {"n": int(len(j)), "sin_estimacion_T": sin_t, "R": mr, "T": mt, "por_tipo": por, "regla": regla,
            "predicciones": pred, "por_pregunta": j.to_dict("records")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    ap.add_argument("--prueba", action="store_true")
    a = ap.parse_args()
    r = brazo_r()
    o = objetivos(r)
    cache_ref = e9.Cache(lp.CACHE)
    if a.simulado:
        llamar, _ = mo.cliente(simulado=True)
        t = correr_t(o, llamar, e9.Cache(Path(tempfile.gettempdir()) / "bss_texto_persona.json"), cache_ref, TOPE_USD,
                     solo=5, escalas=[["a", "b", "c", "d", "e"]] * 5)
        print(evaluar(r.head(5), t, mo.H_ESTIMACION)["regla"])
        return 0
    cache, llamar = e9.Cache(CACHE), e9.cliente_real(timeout=300)
    if a.prueba:
        antes = nb.gastado(cache)
        correr_t(o, llamar, cache, cache_ref, TOPE_USD, solo=1)
        c = nb.gastado(cache) - antes
        print(f"una estimación costó USD {c:.4f} → las {len(o)} costarían ~USD {len(o) * c:.2f} (tope USD {TOPE_USD})")
        return 0
    try:
        t = correr_t(o, llamar, cache, cache_ref, TOPE_USD)
    except (nr.TopeAlcanzado, mo.ServicioNoDisponible) as e:
        print(e)
        return 1
    ev = evaluar(r, t, mo.H_ESTIMACION)
    for k in ("R", "T"):
        x = ev[k]
        print(f"{k}: EAM {x['eam']:.1f} | lado {x['lado']:.0%} | decide {x['n_decide']} (acierta {x['acierto_al_decidir']}) | "
              f"cobertura {x['cobertura']:.0%}, extremas {x['cobertura_extremas']}")
    gasto = e9.gasto_registrado(cache)
    print(f"por tipo {ev['por_tipo']} | regla {ev['regla']} | predicciones {ev['predicciones']} | gasto USD {gasto['costo_usd']:.4f}")
    SALIDA.write_text(json.dumps({**ev, "gasto": gasto}, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
