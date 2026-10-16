"""
Intención de voto con agentes que conocen la campaña (`docs/VOTO_CAMPANA_SPECIFICATION.md`, D23): los 200 agentes de
`VOTO_AGENTES`, con un resumen de la campaña (C1) y además una encuesta publicada (C2).

Uso:
    python src/experiments/voto_campana.py --simulado
    python src/experiments/voto_campana.py

Necesita `BSS_ELECTORAL_DIR` (D16).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-VC1. **El contexto se agrega al final del perfil**, como un bloque más de «quién es», para que el resto del mensaje sea igual
    al de `VOTO_AGENTES`. Las llamadas sin contexto (A) no se repiten: se leen de `voto_agentes.json`.
DI-VC2. **Copiar la encuesta:** las cifras de Invamer de §2, normalizadas entre los 11; los candidatos que la nota no nombra
    («menos de 1 %») cuentan 0.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import voto_agentes as va            # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "voto_campana"
TOPE_USD = 1.0
RESUMEN = """Lo que se sabía de la campaña presidencial a mediados de mayo de 2026, antes de la primera vuelta del 31 de mayo:
- Iván Cepeda es el candidato del Pacto Histórico, el partido de izquierda del presidente Gustavo Petro. Ganó la consulta de su partido en octubre de 2025. Su fórmula es Aída Quilcué.
- Abelardo de la Espriella es abogado y candidato del movimiento Defensores de la Patria, de derecha. Su fórmula es José Manuel Restrepo.
- Paloma Valencia es senadora del Centro Democrático, de derecha. Su fórmula es Juan Daniel Oviedo.
- Sergio Fajardo es un candidato de centro.
- Claudia López, exalcaldesa de Bogotá, es candidata de centro. Su fórmula es Leonardo Huerta."""
ENCUESTA = ("Según la encuesta nacional de Invamer publicada el 21 de mayo de 2026 (trabajo de campo del 13 al 20 de mayo, 3.800 "
            "entrevistas en todo el país), la intención de voto era: Iván Cepeda 44,6 %, Abelardo de la Espriella 31,6 %, Paloma "
            "Valencia 14,0 %, Sergio Fajardo 2,4 %, Claudia López 2,2 %, Santiago Botero 1,4 %, y los demás, menos de 1 % cada "
            "uno. Es una encuesta nacional, no solo de Bogotá.")
INVAMER = {"CEPEDA": 44.6, "ESPRIELLA": 31.6, "VALENCIA": 14.0, "FAJARDO": 2.4, "LÓPEZ": 2.2, "BOTERO": 1.4}   # DI-VC2


def copiar_encuesta(cands: list[str]) -> dict[str, float]:
    """DI-VC2."""
    tot = {c: next((v for k, v in INVAMER.items() if k in c.upper()), 0.0) for c in cands}
    return va.normalizar(tot, cands)


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args(argv)
    from src.consulta import agentes as ag
    from src.experiments import voto_registraduria as vr
    reales = vr.reales("E3")
    ops = va.opciones(reales)
    cands = ops[:-2]
    real = va.normalizar({va._bonito(c): float(v) for c, v in reales.items()}, cands)
    sal = SALIDA / ("simulado" if a.simulado else "")
    sal.mkdir(parents=True, exist_ok=True)
    cache = e9.Cache(sal / "cache.json")
    if a.simulado:
        rng = np.random.default_rng(0)
        llamar = lambda m, s, u, t: json.dumps({"E1": {str(i): float(x) for i, x in enumerate(rng.dirichlet(np.ones(len(ops))), 1)}})  # noqa: E731
    else:
        llamar = e9.cliente_real(timeout=300, extra={"reasoning": {"effort": "low"}})
    va.TOPE_USD = TOPE_USD
    panel = ag.Agentes()
    res = {}
    prev = va.SALIDA / "resultado.json"
    if prev.exists() and not a.simulado:
        res["A"] = json.loads(prev.read_text(encoding="utf-8"))["brazos"]["A200"]                # DI-VC1
    for brazo, extra in (("C1", RESUMEN), ("C2", RESUMEN + "\n\n" + ENCUESTA)):
        perfiles = [p + "\n\n" + extra for p in panel.perfiles]
        tot = va.votar(perfiles, panel.peso, ops, llamar, cache)
        res[brazo] = {**va.medir(va.normalizar(tot, cands), real), "blanco": round(100 * tot["Votaría en blanco"], 1),
                      "no_votaria": round(100 * tot["No votaría"], 1)}
        print(f"{brazo}: {res[brazo]}", flush=True)
    copia = va.medir(copiar_encuesta(cands), real)
    print(f"copiar la encuesta: {copia}")
    mejor = min(("C1", "C2"), key=lambda k: res[k]["eam"])
    m = res[mejor]
    regla = {"R1": m["eam"] <= 5.4, "R2": m["primero"], "R3": m["dos_primeros"]}
    regla["sirven"] = all(regla.values())
    a_eam = res.get("A", {}).get("eam", 8.14)
    hip = {"H1": res["C1"]["eam"] <= a_eam - 1, "H2": res["C2"]["eam"] <= res["C1"]["eam"] - 1,
           "H3": res["C2"]["eam"] < copia["eam"]}
    pred = {"PC1": hip["H1"], "PC2": hip["H2"], "PC3": all([res["C2"]["eam"] <= 5.4, res["C2"]["primero"], res["C2"]["dos_primeros"]]),
            "PC4": not hip["H3"]}
    g = None if a.simulado else e9.gasto_registrado(cache)["costo_usd"]
    print(f"mejor: {mejor} | regla: {regla} | hipótesis: {hip} | predicciones: {pred} | gasto USD {g}")
    (sal / "resultado.json").write_text(json.dumps({"brazos": res, "copiar_encuesta": copia, "real": real, "mejor": mejor,
                                                    "regla": regla, "hipotesis": hip, "predicciones": pred, "gasto": g},
                                                   ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
