"""
Plan v3, Fase 3 (`docs/CONTEXTO_FASE3_SPECIFICATION.md`): ¿mejora a los agentes un contexto numérico estructurado? Las preguntas de
gobierno de la Fase B, con el dato de la ciudad del año base y la serie de Invamer hasta la fecha de corte.

Uso:
    python src/evaluacion/contexto_fase3.py --simulado    # sin gasto: prueba el circuito
    python src/evaluacion/contexto_fase3.py               # con el modelo real (tope USD 1)

DECISIONES DE IMPLEMENTACIÓN
============================

DI-CF1. **G y P salen de la Fase B** (`selector_fase_b.csv`); GC usa la misma llamada que G (`selector_fase_b.estimar`) con el
    contexto después de la nota.
DI-CF2. **La serie de Invamer entra si su campo terminó antes del corte;** si el campo está pendiente, si su mes es anterior al
    corte.
DI-CF3. **El texto corto de cada pregunta** es el que ven los agentes, sin las opciones.
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
EXCLUIDAS = ("CC9",)
PARES = {"P1": (2023, 2024), "P2": (2024, 2025)}
MESES = {1: "ene.", 2: "feb.", 3: "mar.", 4: "abr.", 5: "may.", 6: "jun.", 7: "jul.", 8: "ago.", 9: "sep.", 10: "oct.",
         11: "nov.", 12: "dic."}


def invamer_hasta(corte: str) -> list[tuple[str, float]]:
    """DI-CF2."""
    t = pd.read_csv(RAIZ / "config" / "mediciones_publicadas.csv", dtype=str)
    t = t[t.serie == "invamer_aprobacion"].sort_values("mes")
    out = []
    for r in t.itertuples():
        fin = r.campo_fin if r.campo_fin != "pendiente" else r.mes + "-01"
        if fin < corte:
            a, m = r.mes.split("-")
            out.append((f"{MESES[int(m)]} {a}", float(r.valor)))
    return out


def contexto(base: int, obj: int, esc: list[dict], dato_ciudad: dict[str, float]) -> str:
    """§4."""
    from src.consulta import motor as mo
    lineas = ["DATOS PÚBLICOS DISPONIBLES ANTES DE ESTAS PREGUNTAS (cifras de toda la ciudad, no de esta persona):"]
    for e in esc:
        lado = mo.lado(_ficha(e["variable"]))[1]
        lineas.append(f"- En la Encuesta de Percepción Ciudadana de {base}, en Bogotá: «{e['pregunta']}» → "
                      f"{dato_ciudad[e['variable']]:.0f} % respondió «{lado}».")
    serie = invamer_hasta(f"{obj}-09-01")
    if serie:
        lineas.append("- Aprobación de la gestión del alcalde Carlos Fernando Galán en las encuestas de Invamer en Bogotá: "
                      + "; ".join(f"{m}, {v:.0f} %" for m, v in serie) + ".")
    lineas.append("Estas cifras son de toda la ciudad: esta persona puede pensar distinto. Responde como ella.")
    return "\n".join(lineas)


def _ficha(var: str) -> dict:
    from src.consulta import reformular as rf
    return rf.cargar_catalogo(rf.CATALOGO_2025)[var]


def evaluar(t: pd.DataFrame) -> dict:
    """§6."""
    e = {k: (t[k] - t.real).abs() for k in ("P", "G", "GC")}
    gana = (e["P"] - e["GC"]).sort_values(ascending=False)
    resto = gana.index[2:]
    reglas = {"RC1": bool(e["GC"].mean() < e["P"].mean()),
              "RC2": bool(e["GC"][resto].mean() < e["P"][resto].mean()),
              "RC3": bool(e["GC"].mean() < e["G"].mean())}
    reglas["se_conserva"] = all(reglas.values())
    sesgo = {k: round(float((t[k] - t.real).mean()), 2) for k in ("P", "G", "GC")}
    err = {k: round(float(v.mean()), 2) for k, v in e.items()}
    pred = {"PC1": err["GC"] < err["G"], "PC2": not reglas["RC1"], "PC3": -3 <= sesgo["GC"] <= 3}
    return {"n": int(len(t)), "error": err, "sesgo": sesgo, "reglas": reglas, "predicciones": pred}


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args(argv)
    from src.consulta import agentes as ag
    from src.consulta import reformular as rf
    from src.evaluacion import selector_fase_b as sb
    from src.experiments import personas_con_encuesta as pc
    fb = pd.read_csv(B / "selector_fase_b.csv")
    fb = fb[(fb.dominio == sb.GOB) & ~fb.variable.isin(EXCLUIDAS)]
    catalogo = rf.cargar_catalogo(rf.CATALOGO_2025)
    sal = B / ("simulado" if a.simulado else "")
    sal.mkdir(parents=True, exist_ok=True)
    cache = e9.Cache(sal / "cache_contexto_fase3.json")
    if a.simulado:
        rng = np.random.default_rng(0)

        def llamar(m, s, u, t):
            claves = [l.split(".")[0] for l in u.split("PREGUNTAS NUEVAS:\n")[1].splitlines()]
            return json.dumps({k: {str(c): float(x) for c, x in enumerate(rng.dirichlet(np.ones(5)), 1)} for k in claves})
        modelo = e9.MODELO_SIMULADO
    else:
        llamar, modelo = e9.cliente_real(timeout=300, extra={"reasoning": {"effort": "low"}}), ag.MODELO
    filas, contextos = [], {}
    for par, (base, obj) in PARES.items():
        s = fb[fb.par == par]
        esc = sb.preguntas(list(s.variable), catalogo)
        ctx = contexto(base, obj, esc, dict(zip(s.variable, s.P)))
        contextos[par] = ctx
        panel = ag.Agentes(datos=pc.datos(base))
        gc = sb.estimar(panel, esc, sb.nota(base, obj) + "\n\n" + ctx, llamar, cache, modelo)
        for r in s.itertuples():
            filas.append({"par": par, "variable": r.variable, "P": r.P, "G": r.G, "GC": gc[r.variable], "real": r.real})
        print(f"{par}: {len(s)} preguntas", flush=True)
    t = pd.DataFrame(filas)
    res = evaluar(t.dropna())
    t.round(2).to_csv(sal / "contexto_fase3.csv", index=False, encoding="utf-8")
    g = None if a.simulado else e9.gasto_registrado(cache)["costo_usd"]
    print(t.round(1).to_string(index=False))
    print(json.dumps({**res, "gasto": g}, ensure_ascii=False, indent=1))
    (sal / "contexto_fase3.json").write_text(json.dumps({**res, "contextos": contextos, "gasto": g}, ensure_ascii=False, indent=1),
                                             encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
