"""
La estimación de D19 tal como la sirve la página, y si conviene estirarla
(`docs/NIVEL_ACUERDO_REDACCION_SPECIFICATION.md`).

Parte A: las 95 guardadas pasan por la reformulación de la página y, si quedan como `nueva`, por
`Motor.estimar`, la misma función que usa la página. Se comparan con la S original (prueba del lote 5, B).
Parte B: estirar (E1) o corregir con una recta (E2) la S ya guardada, con parámetros de la práctica.

Uso:
    python src/experiments/nivel_acuerdo_redaccion.py --estirar    # parte B, sin gasto
    python src/experiments/nivel_acuerdo_redaccion.py --simulado   # parte A sin gasto
    python src/experiments/nivel_acuerdo_redaccion.py --prueba     # parte A: 1 reformulación y 1 estimación, mide el costo
    python src/experiments/nivel_acuerdo_redaccion.py              # parte A, la corrida (tope USD 3,50)

DECISIONES DE IMPLEMENTACIÓN
============================

DI-NR1. **La estimación usa `Motor.estimar` sin construir el motor** (que carga la población): se le pasa un
    objeto con las tres cosas que lee, `_candidatas`, `llamar` y `cache`. Así no hay una copia de la lógica
    de la página que pueda separarse de ella. Hecho: `estimar` no lee nada más de `self`.
DI-NR2. **El tope se revisa antes de cada llamada**, porque `Motor.estimar` llama sin tope (la página no lo
    necesita). Si lo registrado llega al tope, la corrida se detiene sin evaluar (el pre-registro pide las 95);
    lo pagado queda en la caché, y una corrida con más tope, aprobada por Daniel, no lo vuelve a pagar.
    Hecho (llamada de prueba, 5/10): cuando Sonnet devuelve un id que no es candidata, `nb.elegir` reintenta,
    igual que en la página; esa pregunta cuesta el doble (USD 0,056 contra ~0,030).
DI-NR4. **Si el servicio no responde, la corrida se detiene** (5/10, enmienda 1). Hecho: en la primera
    corrida la cuenta se quedó sin saldo (HTTP 402) y `Motor.estimar`, que entonces atrapaba todo, dejó 37
    preguntas sin estimar sin avisar. Con DI-CO24 el error sube como `ServicioNoDisponible` y se detiene; lo
    pagado queda en la caché y la corrida se retoma desde ahí.
DI-NR3. **Las extremas** son las de real < 25 o > 65, como dice el pre-registro (§1: umbral elegido después
    de mirar las guardadas).
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.consulta import motor as mo                       # noqa: E402
from src.consulta import reformular as rf                  # noqa: E402
from src.experiments import banco as ba                    # noqa: E402
from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import nivel_acuerdo as na           # noqa: E402
from src.experiments import nivel_acuerdo_lote5 as nl     # noqa: E402
from src.experiments import nivel_acuerdo_validacion as nv  # noqa: E402
from src.experiments import nivel_parecidas_b as nb       # noqa: E402

TOPE_USD = 3.50
H = nv.H
CACHE = ba.SALIDA / "cache_nivel_redaccion.json"
SALIDA = ba.SALIDA / "nivel_acuerdo_redaccion.json"
EXTREMO = (25.0, 65.0)                                     # DI-NR3
CUANTIL = 0.80


class TopeAlcanzado(Exception):
    pass


def _por_pregunta(ruta: Path, *claves) -> pd.DataFrame:
    d = json.loads(ruta.read_text(encoding="utf-8"))
    for k in claves:
        d = d[k]
    p = pd.DataFrame(d["por_pregunta"])
    return p[~p.fallo].reset_index(drop=True)


def originales() -> pd.DataFrame:
    """La S de la prueba del lote 5 (configuración B) en las 95 guardadas."""
    return _por_pregunta(ba.SALIDA / "nivel_acuerdo_lote5.json", "B")


def practica() -> pd.DataFrame:
    return _por_pregunta(ba.SALIDA / "nivel_acuerdo_sonnet.json")


# ---------------------------------------------------------------- medidas comunes
def extremas(total) -> np.ndarray:
    t = np.asarray(total, dtype=float)
    return (t < EXTREMO[0]) | (t > EXTREMO[1])


def medir(S, total, h) -> dict:
    S, t = np.asarray(S, dtype=float), np.asarray(total, dtype=float)
    h = np.broadcast_to(np.asarray(h, dtype=float), S.shape)
    real_si = t > 50
    d = na.llamada(S, h)
    dec = d != "dividida"
    dentro = np.abs(S - t) <= h
    ex = extremas(t)
    return {"n": int(len(S)), "eam": float(np.mean(np.abs(S - t))), "lado": float(np.mean((S > 50) == real_si)),
            "decide": float(dec.mean()), "n_decide": int(dec.sum()),
            "acierto_al_decidir": float(np.mean((d[dec] == "sí") == real_si[dec])) if dec.any() else None,
            "cobertura": float(dentro.mean()),
            "cobertura_extremas": float(dentro[ex].mean()) if ex.any() else None,
            "cobertura_intermedias": float(dentro[~ex].mean()) if (~ex).any() else None,
            "n_extremas": int(ex.sum())}


# ---------------------------------------------------------------- parte B
def ajustar(S, total) -> dict:
    """Parámetros de E1 y E2, y el h (cuantil 80 %) de cada método, con datos de práctica."""
    S, t = np.asarray(S, dtype=float), np.asarray(total, dtype=float)
    b, a = np.polyfit(S, t, 1)
    p = {"m": float(S.mean()), "k": float(t.std() / S.std()), "a": float(a), "b": float(b)}
    p["h"] = {m: float(np.quantile(np.abs(transformar(m, S, p) - t), CUANTIL)) for m in ("S", "E1", "E2")}
    return p


def transformar(m: str, S, p: dict) -> np.ndarray:
    S = np.asarray(S, dtype=float)
    if m == "S":
        out = S
    elif m == "E1":
        out = p["m"] + p["k"] * (S - p["m"])
    else:
        out = p["a"] + p["b"] * S
    return np.clip(out, 0, 100)


def validacion_cruzada(pr: pd.DataFrame) -> dict:
    """Práctica, dejando fuera una familia a la vez (parámetros y h de las otras)."""
    pred = {m: np.zeros(len(pr)) for m in ("S", "E1", "E2")}
    h = {m: np.zeros(len(pr)) for m in ("S", "E1", "E2")}
    for f in pr.familia.unique():
        fuera = (pr.familia == f).to_numpy()
        p = ajustar(pr.S[~fuera], pr.total[~fuera])
        for m in pred:
            pred[m][fuera] = transformar(m, pr.S[fuera], p)
            h[m][fuera] = p["h"][m]
    return {m: medir(pred[m], pr.total, h[m]) for m in pred}


def en_guardadas(pr: pd.DataFrame, g: pd.DataFrame) -> tuple[dict, dict]:
    p = ajustar(pr.S, pr.total)
    return {m: medir(transformar(m, g.S, p), g.total, p["h"][m]) for m in ("S", "E1", "E2")}, p


def regla_b(cv: dict, gu: dict) -> dict:
    """Pre-registro §3."""
    def e1(r):
        s, e = r["S"], r["E1"]
        return bool(e["eam"] <= s["eam"] + 0.5 and (e["cobertura_extremas"] or 0) >= (s["cobertura_extremas"] or 0) + 0.10
                    and (e["acierto_al_decidir"] if e["n_decide"] else 0) >= 0.90)

    def e2(r):
        s, e = r["S"], r["E2"]
        return bool(e["eam"] <= s["eam"] - 0.5 and e["lado"] >= s["lado"]
                    and (e["acierto_al_decidir"] if e["n_decide"] else 0) >= 0.90)
    return {"E1_se_propone": e1(cv) and e1(gu), "E2_se_propone": e2(cv) and e2(gu)}


def parte_b() -> dict:
    pr, g = practica(), originales()
    cv = validacion_cruzada(pr)
    gu, p = en_guardadas(pr, g)
    r = regla_b(cv, gu)
    pred = {"PB1": not r["E1_se_propone"] and any(x["E1"]["eam"] > x["S"]["eam"] + 0.5 for x in (cv, gu)),
            "PB2": all((x["E1"]["cobertura_extremas"] or 0) > (x["S"]["cobertura_extremas"] or 0)
                       and (x["E1"]["cobertura_intermedias"] or 0) < (x["S"]["cobertura_intermedias"] or 0) for x in (cv, gu)),
            "PB3": not r["E2_se_propone"] and any(x["E2"]["eam"] > x["S"]["eam"] - 0.5 for x in (cv, gu)),
            "PB4": not r["E1_se_propone"] and not r["E2_se_propone"]}
    return {"parametros": p, "practica_cv": cv, "guardadas": gu, "regla": r, "predicciones": pred,
            "n_practica": len(pr), "n_guardadas": len(g)}


# ---------------------------------------------------------------- parte A
def estimador(llamar, cache) -> SimpleNamespace:
    """DI-NR1."""
    return SimpleNamespace(_candidatas=mo._candidatas_estimacion(), llamar=llamar, cache=cache)


def correr_a(objetivo: pd.DataFrame, llamar_ref, llamar_est, cache, tope: float, solo=None) -> pd.DataFrame:
    cat = rf.cargar_catalogo()
    est = estimador(llamar_est, cache)
    filas = []
    for i in range(len(objetivo) if solo is None else solo):
        q = objetivo.iloc[i]
        if nb.gastado(cache) >= tope:                                          # DI-NR2
            raise TopeAlcanzado(f"tope de USD {tope} alcanzado en la pregunta {i}")
        r, _ = rf.reformular(q.pregunta_pagina[:500], cat, llamar_ref, cache, rf.MODELO)
        fila = {"id": q.id, "familia": q.familia, "total": float(q.total), "alcance": r["alcance"] if r else "invalida",
                "reformulada": (r or {}).get("reformulada"), "S": None, "ids": None, "porcentaje": None}
        if r and r["alcance"] == "nueva":
            if nb.gastado(cache) >= tope:
                raise TopeAlcanzado(f"tope de USD {tope} alcanzado en la pregunta {i}")
            e = mo.Motor.estimar(est, r["reformulada"], r["escala"])
            if e:
                fila.update(S=e["porcentaje"], porcentaje=e["porcentaje"], llamada=e["llamada"],
                            ids=[p["pregunta"] for p in e["preguntas"]])
        filas.append(fila)
        if (i + 1) % 10 == 0:
            print(f"  {i + 1} preguntas, gasto registrado USD {nb.gastado(cache):.3f}", flush=True)
    return pd.DataFrame(filas)


def evaluar_a(a: pd.DataFrame, orig: pd.DataFrame) -> dict:
    j = a.merge(orig[["id", "S"]].rename(columns={"S": "S_orig"}), on="id")
    nuevas = j[(j.alcance == "nueva") & j.S.notna()]
    ref = medir(nuevas.S, nuevas.total, H)
    org = medir(nuevas.S_orig, nuevas.total, H)
    lr = na.llamada(nuevas.S.to_numpy(float), np.full(len(nuevas), H))
    lo = na.llamada(nuevas.S_orig.to_numpy(float), np.full(len(nuevas), H))
    est = {"dif_media": float(np.mean(np.abs(nuevas.S - nuevas.S_orig))), "misma_llamada": float(np.mean(lr == lo)),
           "alcances": j.alcance.value_counts().to_dict(), "n": int(len(j)), "n_nuevas_con_S": int(len(nuevas))}
    regla = {"eam": ref["eam"] <= org["eam"] + 1.5, "lado": ref["lado"] >= org["lado"] - 0.05,
             "al_decidir": (ref["acierto_al_decidir"] >= 0.90) if ref["n_decide"] else True}
    regla["se_sostiene"] = all(regla.values())
    pred = {"PA1": est["dif_media"] >= 4, "PA2": est["misma_llamada"] >= 0.80, "PA3": ref["eam"] > org["eam"],
            "PA4": not regla["se_sostiene"], "PA5": est["alcances"].get("nueva", 0) >= 0.90 * est["n"]}
    return {"estabilidad": est, "reformulada": ref, "original": org, "regla": regla, "predicciones": pred,
            "por_pregunta": j.to_dict("records")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--estirar", action="store_true")
    ap.add_argument("--simulado", action="store_true")
    ap.add_argument("--prueba", action="store_true")
    a = ap.parse_args()
    if a.estirar:
        r = parte_b()
        for lugar in ("practica_cv", "guardadas"):
            for m, x in r[lugar].items():
                print(f"{lugar:12} {m}: EAM {x['eam']:.1f} | lado {x['lado']:.0%} | decide {x['n_decide']} "
                      f"(acierta {x['acierto_al_decidir'] if x['acierto_al_decidir'] is None else round(x['acierto_al_decidir'], 2)}) | "
                      f"cobertura {x['cobertura']:.0%}, extremas {x['cobertura_extremas']:.0%}, intermedias {x['cobertura_intermedias']:.0%}")
        print(f"parámetros: {r['parametros']}\nregla: {r['regla']} | predicciones: {r['predicciones']}")
        previo = json.loads(SALIDA.read_text(encoding="utf-8")) if SALIDA.exists() else {}
        SALIDA.write_text(json.dumps({**previo, "B": r}, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        return 0
    o74, o21 = nl.objetivos()
    o95 = pd.concat([o74, o21], ignore_index=True)
    if a.simulado:
        cache = e9.Cache(Path(tempfile.gettempdir()) / "bss_redaccion_simulado.json")
        llamar, _ = mo.cliente(simulado=True)
        ref_llamar, est_llamar = llamar, llamar
    else:
        cache = e9.Cache(CACHE)
        ref_llamar = est_llamar = e9.cliente_real(timeout=300)
    if a.prueba:
        antes = nb.gastado(cache)
        correr_a(o95, ref_llamar, est_llamar, cache, TOPE_USD, solo=1)
        c = nb.gastado(cache) - antes
        print(f"una pregunta (reformulación y estimación) costó USD {c:.4f} → las 95 costarían ~USD {95 * c:.2f} (tope USD {TOPE_USD})")
        return 0
    try:
        res = correr_a(o95, ref_llamar, est_llamar, cache, TOPE_USD)
    except (TopeAlcanzado, mo.ServicioNoDisponible) as e:                    # DI-NR4
        print(e)
        return 1
    r = evaluar_a(res, originales())
    x, y = r["reformulada"], r["original"]
    print(f"alcances: {r['estabilidad']['alcances']} | |ΔS| medio {r['estabilidad']['dif_media']:.1f} | "
          f"misma llamada {r['estabilidad']['misma_llamada']:.0%}")
    for n, m in (("reformulada", x), ("original", y)):
        print(f"  {n}: EAM {m['eam']:.1f} | lado {m['lado']:.0%} | decide {m['n_decide']} (acierta {m['acierto_al_decidir']}) | "
              f"cobertura {m['cobertura']:.0%}, extremas {m['cobertura_extremas']}")
    gasto = None if a.simulado else e9.gasto_registrado(cache)
    print(f"regla: {r['regla']} | predicciones: {r['predicciones']} | gasto: {gasto and round(gasto['costo_usd'], 4)}")
    if not a.simulado:
        previo = json.loads(SALIDA.read_text(encoding="utf-8")) if SALIDA.exists() else {}
        SALIDA.write_text(json.dumps({**previo, "A": {**r, "gasto": gasto}}, ensure_ascii=False, indent=1, default=str),
                          encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
