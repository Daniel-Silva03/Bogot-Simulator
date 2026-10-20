"""
Plan v4, Paso 1 (`docs/REPLICA_ALCALDE_SPECIFICATION.md`): ¿se repite el acierto de los agentes en la gestión de Galán 2025? Las
preguntas de gobierno en las tres transiciones con perfiles (EPC 2022 → 2023 → 2024 → 2025), agentes contra persistencia.

Uso:
    python src/evaluacion/replica_alcalde.py --simulado    # sin gasto: prueba el circuito
    python src/evaluacion/replica_alcalde.py               # con el modelo real (tope USD 1)

DECISIONES DE IMPLEMENTACIÓN
============================

DI-RA1. **La llamada es la de la Fase B** (`selector_fase_b.estimar`, con su nota), con los mismos 200 agentes del año base.
DI-RA2. **En 2022 y 2023 el perfil lleva la calificación del alcalde y del Concejo de ese año** (`GG3` y `CC5`), con la escala de
    `GG3_GALAN` y `CC5A_GALAN`, como ya la lleva el perfil de 2024. Supuesto: los códigos 1-5 son los mismos en los tres años
    (`epc_bcv.ITEMS` los trata así).
DI-RA3. **El dato del alcalde y del Concejo** (base y real) sale de `serie_epc_bcv.csv`, p4 + p5. En 2024 y 2025 coincide con el
    catálogo (diferencia 0,0, revisado el 20/10 antes de llamar).
DI-RA4. **La transición 2024 → 2025 no se vuelve a llamar:** P y G salen de `selector_fase_b.csv`, sin `CC9`.
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

B = RAIZ / "data" / "processed" / "benchmark"
TOPE_USD = 1.0
ALCALDE = {2023: "¿Usted cómo califica la gestión de la alcaldesa de Bogotá, Claudia López?",
           2024: "¿Usted cómo califica la gestión del alcalde de Bogotá, Carlos Fernando Galán?"}
LOPEZ_PERFIL = "¿Usted cómo califica la gestión de la alcaldesa de Bogotá, Claudia López?"
NUEVAS = {"T0": (2022, 2023), "T1": (2023, 2024)}
MICE = ("MICE1_GALAN", "MICE2_GALAN", "MICE3_GALAN")
SERIE = {"ALCALDE": "gestion_alcalde", "CONCEJO": "gestion_concejo"}


def serie() -> dict[tuple[str, int], float]:
    """DI-RA3."""
    s = pd.read_csv(RAIZ / "data" / "processed" / "serie_epc_bcv.csv")
    return {(r.item, int(r.anio)): 100 * (r.p4 + r.p5) for r in s.itertuples()}


def datos_con_gobierno(anio: int):
    """DI-RA2: los datos de `personas_con_encuesta` con la calificación del alcalde y del Concejo del año base en el perfil."""
    from src.consulta import reformular as rf
    from src.evaluacion import selector_fase_b as sb
    from src.experiments import personas_con_encuesta as pc
    base, d, perfil = pc.datos(anio)
    cat = rf.cargar_catalogo(rf.CATALOGO_2025)
    ya = {c for _, c, _ in perfil}
    extra = [(LOPEZ_PERFIL, "GG3", cat["GG3_GALAN"]), (sb.CONCEJO, "CC5", cat["CC5A_GALAN"])]
    return base, d, perfil + [x for x in extra if x[1] in d.columns and x[1] not in ya]


def preguntas(base: int, obj: int) -> list[dict]:
    """§3: rumbo, corrupción, alcalde y Concejo del año objetivo."""
    from src.consulta import motor as mo
    from src.consulta import reformular as rf
    from src.evaluacion import selector_fase_b as sb
    cat = rf.cargar_catalogo(rf.CATALOGO_2025)
    esc = sb.preguntas(["AG1", "GG7"], cat)
    for k, (var, texto, ficha) in enumerate((("ALCALDE", ALCALDE[obj], cat["GG3_GALAN"]),
                                             ("CONCEJO", sb.CONCEJO, cat["CC5A_GALAN"])), 3):
        esc.append({"clave": f"Q{k:02d}", "variable": var, "pregunta": texto, "validos": list(ficha["escala"]),
                    "cuenta": mo.lado(ficha)[0], "categorias": dict(zip(ficha["escala"], mo.escala_visible(ficha)))})
    return esc


def objetivos_fase_b() -> pd.DataFrame:
    """DI-RA4."""
    fb = pd.read_csv(B / "selector_fase_b.csv")
    fb = fb[(fb.par == "P2") & (fb.dominio == "gobierno e instituciones") & (fb.variable != "CC9")]
    t = fb[["variable", "P", "G", "real"]].copy()
    t["variable"] = t.variable.replace({"GG3_GALAN": "ALCALDE", "CC5A_GALAN": "CONCEJO"})
    t.insert(0, "transicion", "T2")
    return t


def evaluar(t: pd.DataFrame) -> dict:
    """§6 y §7. `t`: una fila por objetivo, con transicion, variable, P, G y real."""
    t = t.copy()
    t["eP"], t["eG"] = (t.P - t.real).abs(), (t.G - t.real).abs()
    err = {"P": round(float(t.eP.mean()), 2), "G": round(float(t.eG.mean()), 2)}
    sesgo = {"P": round(float((t.P - t.real).mean()), 2), "G": round(float((t.G - t.real).mean()), 2)}
    por_t = {k: {"n": int(len(s)), "P": round(float(s.eP.mean()), 2), "G": round(float(s.eG.mean()), 2),
                 "sesgo_G": round(float((s.G - s.real).mean()), 2)} for k, s in t.groupby("transicion")}
    gana = (t.eP - t.eG).sort_values(ascending=False)
    resto = t.drop(gana.index[:2])
    alc = t[t.variable == "ALCALDE"]
    alc_gana = int((alc.eG < alc.eP).sum())
    reglas = {"RP1": bool(err["G"] <= err["P"] - 1),
              "RP2": bool(sum(v["G"] < v["P"] for v in por_t.values()) >= 2),
              "RP3": bool(resto.eG.mean() < resto.eP.mean())}
    reglas["se_reproduce"] = all(reglas.values())
    reglas["RA"] = bool(alc_gana >= 2)
    sin_mice = t[~t.variable.isin(MICE)]
    sens = {"sin_MICE": {"n": int(len(sin_mice)), "P": round(float(sin_mice.eP.mean()), 2),
                         "G": round(float(sin_mice.eG.mean()), 2)}}
    pred = {"PR1": not reglas["RP1"], "PR2": alc_gana <= 1, "PR3": sesgo["G"] > 0}
    return {"n": int(len(t)), "error": err, "sesgo": sesgo, "por_transicion": por_t, "alcalde_gana_G": alc_gana,
            "reglas": reglas, "sensibilidad": sens, "predicciones": pred}


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args(argv)
    from src.consulta import agentes as ag
    from src.evaluacion import persistencia_epc as pe
    from src.evaluacion import selector_fase_b as sb
    sal = B / ("simulado" if a.simulado else "")
    sal.mkdir(parents=True, exist_ok=True)
    cache = e9.Cache(sal / "cache_replica_alcalde.json")
    if a.simulado:
        rng = np.random.default_rng(0)

        def llamar(m, s, u, t):
            claves = [l.split(".")[0] for l in u.split("PREGUNTAS NUEVAS:\n")[1].splitlines()]
            return json.dumps({k: {str(c): float(x) for c, x in enumerate(rng.dirichlet(np.ones(5)), 1)} for k in claves})
        modelo = e9.MODELO_SIMULADO
    else:
        llamar, modelo = e9.cliente_real(timeout=300, extra={"reasoning": {"effort": "low"}}), ag.MODELO
    sb.TOPE_USD = TOPE_USD
    s = serie()
    filas = []
    for tr, (base, obj) in NUEVAS.items():
        esc = preguntas(base, obj)
        panel = ag.Agentes(datos=datos_con_gobierno(base))
        g = sb.estimar(panel, esc, sb.nota(base, obj), llamar, cache, modelo)
        rb, ro = pe.cifras(base), pe.cifras(obj)
        for e in esc:
            v = e["variable"]
            p, r = (s[(SERIE[v], base)], s[(SERIE[v], obj)]) if v in SERIE else (rb[v], ro[v])
            filas.append({"transicion": tr, "variable": v, "P": p, "G": g[v], "real": r})
        print(f"{tr}: {len(esc)} preguntas", flush=True)
    t = pd.concat([pd.DataFrame(filas), objetivos_fase_b()], ignore_index=True)
    t = t.dropna(subset=["G"])
    res = evaluar(t)
    t.round(2).to_csv(sal / "replica_alcalde.csv", index=False, encoding="utf-8")
    gasto = None if a.simulado else e9.gasto_registrado(cache)["costo_usd"]
    print(t.round(1).to_string(index=False))
    print(json.dumps({**res, "gasto": gasto}, ensure_ascii=False, indent=1))
    (sal / "replica_alcalde.json").write_text(json.dumps({**res, "gasto": gasto}, ensure_ascii=False, indent=1),
                                              encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
