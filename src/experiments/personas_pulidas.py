"""
Personas con su encuesta, pulidas (`docs/PERSONAS_PULIDAS_SPECIFICATION.md`): cinco variantes contra la exageración en un
desarrollo, y la elegida, una sola vez, en personas y preguntas nuevas.

Uso:
    python src/experiments/personas_pulidas.py desarrollo --simulado
    python src/experiments/personas_pulidas.py desarrollo          # las 5 variantes en las 200 de antes
    python src/experiments/personas_pulidas.py final               # la elegida y V0 en 200 nuevas

DECISIONES DE IMPLEMENTACIÓN
============================

DI-PP1. **Las probabilidades** se leen por código válido; se descartan las negativas, y se normalizan a 1 sin «no sabe». Si
    no hay ninguna válida, el par queda sin respuesta.
DI-PP2. **La estimación de la página** (el ancla de V4 y la referencia de R2) es `Motor.estimar` con el texto de la encuesta y
    sus 5 etiquetas, que cuenta como favorables las opciones 4 y 5. La imagen de Galán (`GOB_4`) tiene dos opciones; para la
    estimación se le pasa una escala de 5 equivalente, de «muy desfavorable» a «muy favorable».
DI-PP3. **La elección del desarrollo** se escribe en `desarrollo.json`, y la prueba final la lee de ahí: no se puede correr la
    final con otra variante sin cambiar el código.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import personas_con_encuesta as pc   # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "personas_pulidas"
TOPE_USD = 2.0
SEMILLA_FINAL = 20261015
DESARROLLO = ("CON_4", "CON_5", "CON_7", "GOB_7", "MOV_6", "FIN_3", "CCC_1", "CCC_16", "CCC_20", "CCC_22", "GOB_4", "CTI_4")
FINAL = ("CON_6", "JUS_1", "SAL_1", "CTI_3", "CCC_18", "CTI_5", "EDU_4", "EDU_9")
SECUNDARIA = DESARROLLO[:6]
VARIANTES = ("V0", "V1", "V2", "V3", "V4")
CONFIG = {"V0": (False, False, False), "V1": (False, True, False), "V2": (True, False, False), "V3": (True, True, False),
          "V4": (True, True, True)}                                         # (probabilidades, instrucción, ancla)
INSTRUCCION = ("Las personas no son coherentes en todo: alguien descontento con la ciudad puede confiar en alguna institución "
               "o estar satisfecho con algún servicio. No extrapoles su descontento o su entusiasmo a todo. Cuando sus "
               "respuestas no dicen nada directo sobre una pregunta, piensa en lo típico de alguien como ella en Bogotá, no en "
               "la opción más extrema.\n")
SALIDA_OPCION = ('Responde SOLO con un JSON, sin texto alrededor, con las claves de las preguntas y el código elegido, por '
                 'ejemplo {"E1": 2, "E2": 4}.')
SALIDA_PROB = ('Para cada pregunta, da la probabilidad de cada opción para ESTA persona (entre 0 y 1, que sumen 1). Responde '
               'SOLO con un JSON, sin texto alrededor, por ejemplo {"E1": {"1": 0.1, "2": 0.5, "3": 0.2, "4": 0.15, "5": 0.05}}.')
BASE = pc.SISTEMA.split("Responde SOLO")[0]
GOB4_CINCO = ["Muy desfavorable", "Desfavorable", "Ni favorable ni desfavorable", "Favorable", "Muy favorable"]


def preguntas(variables: tuple[str, ...]) -> list[dict]:
    from src.experiments import banco_lote8 as b8
    from src.experiments import banco_reales as br
    por_var = {v: (txt, cats, fav) for v, _, txt, cats, fav in b8.PREGUNTAS}
    out = []
    for k, v in enumerate(variables, 1):
        txt, cats, fav = por_var[v]
        c = br.categorias(cats)
        out.append({"clave": f"E{k}", "variable": v, "pregunta": txt, "categorias": c, "validos": br.validos(c), "fav": fav})
    return out


def sistema(variante: str) -> str:
    prob, instr, _ = CONFIG[variante]
    return BASE + (INSTRUCCION if instr else "") + (SALIDA_PROB if prob else SALIDA_OPCION)


def usuario(perfil: str, esc: list[dict], ancla: Optional[dict] = None) -> str:
    def linea(e):
        s = f'{e["clave"]}. {e["pregunta"]} Opciones: ' + "; ".join(f"{c}={t}" for c, t in e["categorias"].items())
        if ancla is not None:
            fav = " o ".join(f"«{e['categorias'][c]}»" for c in e["fav"])
            s += f" (En toda Bogotá, se estima que cerca del {ancla[e['variable']]:.0f} % responde {fav}.)"
        return s
    return f"QUIÉN ES:\n{perfil}\n\nPREGUNTAS NUEVAS:\n" + "\n".join(linea(e) for e in esc)


def leer_prob(texto: str, esc: list[dict]) -> dict[str, Optional[dict[int, float]]]:
    """DI-PP1."""
    d = e9._json_de(texto) or {}
    out = {}
    for e in esc:
        p = d.get(e["clave"]) if isinstance(d.get(e["clave"]), dict) else {}
        q = {}
        for c in e["validos"]:
            try:
                q[c] = max(0.0, float(p.get(str(c), p.get(c, 0)) or 0))
            except (TypeError, ValueError):
                q[c] = 0.0
        s = sum(q.values())
        out[e["clave"]] = {c: x / s for c, x in q.items()} if s > 0 else None
    return out


def tvd(p: dict[int, float], q: dict[int, float]) -> float:
    ks = set(p) | set(q)
    return 0.5 * sum(abs(p.get(k, 0) - q.get(k, 0)) for k in ks)


def distribucion(codigos: np.ndarray, w: np.ndarray, validos: list[int]) -> dict[int, float]:
    m = np.isin(codigos, validos)
    return {c: float(np.sum(w[m] * (codigos[m] == c)) / np.sum(w[m])) for c in validos}


def estimaciones_pagina(esc: list[dict], simulado: bool) -> dict[str, float]:
    """DI-PP2."""
    if simulado:
        return {e["variable"]: 40.0 for e in esc}
    from src.consulta import motor as mo
    ruta = SALIDA / "pagina.json"
    previas = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}
    falta = [e for e in esc if e["variable"] not in previas]
    if falta:
        llamar, modelo = mo.cliente(simulado=False)
        m = mo.Motor(llamar, modelo, cache=e9.Cache(SALIDA / "cache_pagina.json"))
        for e in falta:
            etq = GOB4_CINCO if e["variable"] == "GOB_4" else [e["categorias"][c] for c in e["validos"]]
            r = m.estimar(e["pregunta"], etq)
            previas[e["variable"]] = r["porcentaje"] if r else 50.0
        SALIDA.mkdir(parents=True, exist_ok=True)
        ruta.write_text(json.dumps(previas, ensure_ascii=False, indent=1), encoding="utf-8")
    return {e["variable"]: previas[e["variable"]] for e in esc}


def correr(variante: str, personas: np.ndarray, esc: list[dict], datos, pagina: dict, llamar, cache) -> dict:
    """Las respuestas de una variante: clave -> (valor esperado o código por persona, prob. favorable, distribución)."""
    base, d, perfil = datos
    prob, _, con_ancla = CONFIG[variante]
    num = lambda c: pd.to_numeric(d[c], errors="coerce").to_numpy(float)          # noqa: E731
    demo = {"sexo": pd.Series(num("DMO_1")).map({1: "hombre", 2: "mujer"}).to_numpy(), "edad": num("DMO_3_1"),
            "estrato": num("DMO_4_1"), "localidad": base.cod_loc.map(pc.LOCALIDADES).to_numpy()}
    out = {e["clave"]: {"valor": np.full(len(personas), np.nan), "pfav": np.full(len(personas), np.nan),
                        "dist": [None] * len(personas)} for e in esc}
    for j, i in enumerate(personas):
        if e9.gasto_registrado(cache)["costo_usd"] >= TOPE_USD:
            raise RuntimeError(f"Se llegó al tope de USD {TOPE_USD}.")
        resp = [(p, pc.etiqueta(f, d[c].iloc[i])) for p, c, f in perfil]
        dm = {k: (int(v[i]) if isinstance(v[i], (float, np.floating)) and not np.isnan(v[i]) else v[i]) for k, v in demo.items()}
        u = usuario(pc.perfil_texto(dm, resp), esc, pagina if con_ancla else None)
        texto, _ = e9.pedir(llamar, cache, pc.MODELO, pc.TEMPERATURA, sistema(variante), u, 0)
        if prob:
            probs = leer_prob(texto, esc)
            for e in esc:
                q = probs[e["clave"]]
                if q:
                    o = out[e["clave"]]
                    o["valor"][j] = sum(c * x for c, x in q.items())
                    o["pfav"][j] = sum(q.get(c, 0) for c in e["fav"])
                    o["dist"][j] = q
        else:
            for k, c in pc.leer(texto, esc).items():
                e = next(x for x in esc if x["clave"] == k)
                if c in e["validos"]:
                    o = out[k]
                    o["valor"][j] = c
                    o["pfav"][j] = float(c in e["fav"])
                    o["dist"][j] = {c: 1.0}
        if (j + 1) % 50 == 0:
            print(f"   {variante}: {j + 1} de {len(personas)}; gasto USD {e9.gasto_registrado(cache)['costo_usd']:.3f}", flush=True)
    return out


def medir(res: dict, personas: np.ndarray, esc: list[dict], datos, pagina: dict) -> dict:
    """§4."""
    base, d, _ = datos
    w = base.peso.to_numpy(float)
    ok_loc = base.cod_loc.between(1, 19).to_numpy()
    resto = np.setdiff1d(np.flatnonzero(ok_loc), personas)
    ind, cons, tot, tot_pag, tvds, sin = [], [], [], [], [], 0
    por = []
    for e in esc:
        y = pd.to_numeric(d[e["variable"]], errors="coerce").to_numpy(float)
        v = e["validos"]
        tr = resto[np.isin(y[resto], v)]
        const = float(np.sum(w[tr] * y[tr]) / np.sum(w[tr]))
        o = res[e["clave"]]
        ym = y[personas]
        par = np.isin(ym, v) & ~np.isnan(o["valor"])
        sin += int((np.isin(ym, v) & np.isnan(o["valor"])).sum())
        r100 = np.array([pc.a_100(c, v) for c in ym[par]])
        ind += list(np.abs(np.array([pc.a_100(c, v) for c in o["valor"][par]]) - r100))
        cons += list(np.abs(pc.a_100(const, v) - r100))
        todos = np.flatnonzero(ok_loc & np.isin(y, v))
        real = 100 * np.sum(w[todos] * np.isin(y[todos], e["fav"])) / np.sum(w[todos])
        wm = w[personas]; okp = ~np.isnan(o["pfav"])
        t_ag = 100 * np.sum(wm[okp] * o["pfav"][okp]) / np.sum(wm[okp])
        dist_ag = {c: float(sum(wm[j] * (o["dist"][j] or {}).get(c, 0) for j in np.flatnonzero(okp)) / np.sum(wm[okp]))
                   for c in v}
        t = tvd(dist_ag, distribucion(y[todos], w[todos], v))
        tot.append(abs(t_ag - real)); tot_pag.append(abs(pagina[e["variable"]] - real)); tvds.append(t)
        por.append({"variable": e["variable"], "real": round(float(real), 1), "brazo": round(float(t_ag), 1),
                    "pagina": round(float(pagina[e["variable"]]), 1), "tvd": round(t, 3)})
    return {"error_individual": round(float(np.mean(ind)), 1), "error_constante": round(float(np.mean(cons)), 1),
            "error_total": round(float(np.mean(tot)), 1), "error_pagina": round(float(np.mean(tot_pag)), 1),
            "tvd": round(float(np.mean(tvds)), 3), "sin_respuesta": sin, "por_pregunta": por}


def elegir(med: dict[str, dict]) -> Optional[str]:
    """§5: entre las que le ganan a la constante, la de menor error del total; empate a 0,5, la de menor TVD."""
    cand = [k for k, m in med.items() if m["error_individual"] < m["error_constante"]]
    if not cand:
        return None
    mejor = min(med[k]["error_total"] for k in cand)
    empatadas = [k for k in cand if med[k]["error_total"] <= mejor + 0.5]
    return min(empatadas, key=lambda k: (med[k]["tvd"], med[k]["error_total"]))


def cliente(simulado: bool):
    if simulado:
        rng = np.random.default_rng(0)

        def llamar(m, s, u, t):
            claves = [l.split(".")[0] for l in u.split("PREGUNTAS NUEVAS:\n")[1].split("\n")]
            if "probabilidad" in s:
                return json.dumps({k: {str(c): float(x) for c, x in zip(range(1, 6), rng.dirichlet(np.ones(5)))} for k in claves})
            return json.dumps({k: int(rng.integers(1, 6)) for k in claves})
        return llamar, e9.Cache(SALIDA / "simulado" / "cache.json")
    return e9.cliente_real(timeout=300, extra={"reasoning": {"effort": "low"}}), e9.Cache(SALIDA / "cache.json")


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("etapa", choices=("desarrollo", "final"))
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args(argv)
    datos = pc.datos_2025()
    base = datos[0]
    elegibles = np.flatnonzero(base.cod_loc.between(1, 19).to_numpy())
    dev = np.sort(np.random.default_rng(pc.SEMILLA).choice(elegibles, pc.N, replace=False))
    llamar, cache = cliente(a.simulado)
    sal = SALIDA / ("simulado" if a.simulado else "")
    sal.mkdir(parents=True, exist_ok=True)
    if a.etapa == "desarrollo":
        esc = preguntas(DESARROLLO)
        pagina = estimaciones_pagina(esc, a.simulado)
        med = {}
        for v in VARIANTES:
            med[v] = medir(correr(v, dev, esc, datos, pagina, llamar, cache), dev, esc, datos, pagina)
            m = med[v]
            print(f"{v}: individual {m['error_individual']} (constante {m['error_constante']}) | total {m['error_total']} "
                  f"(página {m['error_pagina']}) | TVD {m['tvd']} | sin respuesta {m['sin_respuesta']}", flush=True)
        gana = elegir(med)
        pred = {"PP1": min(med[v]["error_total"] for v in ("V2", "V3", "V4")) < min(med[v]["error_total"] for v in ("V0", "V1")),
                "PP2": gana == "V4", "PP3": med["V0"]["error_total"] - med["V1"]["error_total"] < 2}
        g = None if a.simulado else e9.gasto_registrado(cache)["costo_usd"]
        print(f"elegida: {gana} | predicciones: {pred} | gasto USD {g}")
        (sal / "desarrollo.json").write_text(json.dumps({"medidas": med, "elegida": gana, "predicciones": pred, "gasto": g},
                                                        ensure_ascii=False, indent=1), encoding="utf-8")
        return 0
    dj = sal / "desarrollo.json"
    if not dj.exists():
        raise RuntimeError("Falta el desarrollo: la prueba final usa la variante que eligió (DI-PP3).")
    gana = json.loads(dj.read_text(encoding="utf-8"))["elegida"]
    if gana is None:
        print("En el desarrollo ninguna variante le ganó a la constante: no hay prueba final.")
        return 0
    resto = np.setdiff1d(elegibles, dev)
    nuevas = np.sort(np.random.default_rng(SEMILLA_FINAL).choice(resto, pc.N, replace=False))
    out = {"elegida": gana}
    for nombre, vs in (("final", FINAL), ("secundaria", SECUNDARIA)):
        esc = preguntas(vs)
        pagina = estimaciones_pagina(esc, a.simulado)
        for v in dict.fromkeys((gana, "V0")):
            m = medir(correr(v, nuevas, esc, datos, pagina, llamar, cache), nuevas, esc, datos, pagina)
            out[f"{nombre}_{v}"] = m
            print(f"{nombre} {v}: individual {m['error_individual']} (constante {m['error_constante']}) | total "
                  f"{m['error_total']} (página {m['error_pagina']}) | TVD {m['tvd']} | sin respuesta {m['sin_respuesta']}",
                  flush=True)
    f = out[f"final_{gana}"]
    regla = {"R1": f["error_individual"] < f["error_constante"], "R2": f["error_total"] < f["error_pagina"], "R3": f["tvd"] <= 0.15}
    regla["pasa"] = all(regla.values())
    out.update(regla=regla, predicciones={"PP4": regla["pasa"]},
               gasto=None if a.simulado else e9.gasto_registrado(cache)["costo_usd"])
    print(f"regla: {regla} | gasto USD {out['gasto']}")
    (sal / "final.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
