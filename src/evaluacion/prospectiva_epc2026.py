"""
Plan v5, Paso 2 (`docs/PROSPECTIVA_EPC2026_SPECIFICATION.md`): las predicciones para la EPC 2026, congeladas antes de que salga.
Agentes con perfiles de la EPC 2025 contra la persistencia (el dato de 2025), en 7 preguntas de gobierno.

Uso:
    python src/evaluacion/prospectiva_epc2026.py --simulado    # sin gasto: prueba el circuito
    python src/evaluacion/prospectiva_epc2026.py               # congela las predicciones (tope USD 1)

La evaluación (`evaluar`) se corre cuando salga la EPC 2026, con el dato real de las preguntas comparables.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-PR1. **G, la principal,** es la llamada de la Fase B y de la réplica del alcalde (`selector_fase_b.estimar`): una llamada por
    agente con las 7 preguntas y la nota 2025 → 2026. Es la única que sirve para las 7: la de la página solo acepta escalas de 5
    opciones, y el rumbo tiene 2.
DI-PR2. **La página, la secundaria,** es `agentes.Agentes.estimar` en las 4 preguntas que la página responde solo con agentes
    (`motor.GALAN_SOLO_AGENTES`), con su texto. Es la cifra que ve quien usa la página.
DI-PR3. **Lo congelado** va a `config/prospectiva_epc2026/`: las predicciones, la persistencia, los textos, el modelo, la fecha, las
    200 personas y la huella (sha256) de los mensajes de sistema. No se vuelve a correr ni se edita.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402

TOPE_USD = 1.0
BASE, OBJ = 2025, 2026
VARIABLES = ("GG3_GALAN", "AG1", "GG7", "CC5A_GALAN", "MICE1_GALAN", "MICE2_GALAN", "MICE3_GALAN")
ALCALDE = "GG3_GALAN"
CONGELADO = RAIZ / "config" / "prospectiva_epc2026"
CACHE = RAIZ / "data" / "processed" / "benchmark" / "cache_prospectiva_epc2026.json"
FRASE_SOLO_ALCALDE = ("Los agentes superaron a la persistencia en la pregunta sobre la gestión del alcalde, pero no demostraron una "
                      "mejora general en las preguntas de gobierno evaluadas. El resultado es específico de esa pregunta y "
                      "necesita replicación.")


def cliente(simulado: bool):
    from src.consulta import agentes as ag
    if not simulado:
        return e9.cliente_real(timeout=300, extra={"reasoning": {"effort": "low"}}), ag.MODELO
    rng = np.random.default_rng(0)

    def llamar(m, s, u, t):
        claves = [l.split(".")[0] for l in u.split("PREGUNTAS NUEVAS:\n")[1].splitlines()]
        return json.dumps({k: {str(c): float(x) for c, x in enumerate(rng.dirichlet(np.ones(5)), 1)} for k in claves})
    return llamar, e9.MODELO_SIMULADO


def huella(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16]


def evaluar(t: pd.DataFrame, metodo: str = "G") -> dict:
    """§6. `t`: una fila por pregunta comparable, con variable, P, el método y real."""
    t = t.copy()
    t["eP"], t["eM"] = (t.P - t.real).abs(), (t[metodo] - t.real).abs()
    sin = t[t.variable != ALCALDE]
    err = {"P": round(float(t.eP.mean()), 2), metodo: round(float(t.eM.mean()), 2)}
    err_sin = {"P": round(float(sin.eP.mean()), 2), metodo: round(float(sin.eM.mean()), 2)} if len(sin) else {}
    reglas = {"RV1": bool(err[metodo] <= err["P"] - 1),
              "RV2": bool(len(sin) > 0 and err_sin[metodo] <= err_sin["P"] - 1)}
    reglas["victoria"] = reglas["RV1"] and reglas["RV2"]
    gana = dict(zip(t.variable, np.where(t.eM < t.eP, metodo, np.where(t.eM > t.eP, "P", "empate"))))
    solo_alcalde = (not reglas["victoria"]) and gana.get(ALCALDE) == metodo
    return {"n": int(len(t)), "error": err, "error_sin_alcalde": err_sin, "reglas": reglas,
            "sesgo": round(float((t[metodo] - t.real).mean()), 2), "gana_por_pregunta": gana,
            "ganadas": {k: int(sum(v == k for v in gana.values())) for k in (metodo, "P", "empate")},
            "informe": FRASE_SOLO_ALCALDE if solo_alcalde else None}


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args(argv)
    from src.consulta import agentes as ag
    from src.consulta import motor as mo
    from src.consulta import reformular as rf
    from src.evaluacion import persistencia_epc as pe
    from src.evaluacion import selector_fase_b as sb
    from src.experiments import personas_pulidas as pp
    destino = CACHE.parent / "simulado" / "prospectiva_epc2026" if a.simulado else CONGELADO
    if not a.simulado and (destino / "predicciones.csv").exists():
        raise SystemExit("Las predicciones ya están congeladas: no se vuelven a correr (DI-PR3).")
    destino.mkdir(parents=True, exist_ok=True)
    cache = e9.Cache(CACHE.with_name("simulado_" + CACHE.name) if a.simulado else CACHE)
    llamar, modelo = cliente(a.simulado)
    sb.TOPE_USD = TOPE_USD
    cat = rf.cargar_catalogo(rf.CATALOGO_2025)
    panel = ag.Agentes()
    p = pe.cifras(BASE)
    esc = sb.preguntas(list(VARIABLES), cat)
    g = sb.estimar(panel, esc, sb.nota(BASE, OBJ), llamar, cache, modelo)
    pag = {}
    for v, texto in mo.GALAN_SOLO_AGENTES.items():
        if not a.simulado and e9.gasto_registrado(cache)["costo_usd"] >= TOPE_USD:
            raise RuntimeError(f"Se llegó al tope de USD {TOPE_USD}.")
        r = panel.estimar(texto, mo.escala_visible(cat[v]), llamar, cache, modelo)
        pag[v] = r.get("porcentaje")
    filas = [{"variable": e["variable"], "pregunta_agentes": e["pregunta"], "lo_que_se_cuenta": mo.lado(cat[e["variable"]])[1],
              "P": round(p[e["variable"]], 2), "G": None if g[e["variable"]] is None else round(g[e["variable"]], 2),
              "pagina": pag.get(e["variable"])} for e in esc]
    t = pd.DataFrame(filas)
    gasto = None if a.simulado else e9.gasto_registrado(cache)["costo_usd"]
    meta = {"fecha": time.strftime("%Y-%m-%d %H:%M"), "modelo": modelo, "temperatura": ag.TEMPERATURA, "razonamiento": "low",
            "semilla_panel": ag.SEMILLA, "perfiles": "EPC 2025", "personas": [int(i) for i in panel.personas],
            "nota": sb.nota(BASE, OBJ), "huella_sistema": huella(pp.BASE + pp.SALIDA_PROB),
            "huella_perfiles": huella("\n\n".join(panel.perfiles)), "gasto_usd": gasto}
    t.to_csv(destino / "predicciones.csv", index=False, encoding="utf-8")
    (destino / "congelado.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(t[["variable", "P", "G", "pagina"]].to_string(index=False))
    print(json.dumps({k: v for k, v in meta.items() if k != "personas"}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
