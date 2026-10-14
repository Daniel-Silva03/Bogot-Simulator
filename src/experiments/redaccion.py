"""
Efecto de la redacción (`docs/REDACCION_SPECIFICATION.md`): la misma pregunta escrita de tres formas, ¿cuánto cambia la
respuesta de la página?

Uso:
    python src/experiments/redaccion.py --simulado   # sin gasto
    python src/experiments/redaccion.py              # con el modelo real (tope USD 0,25)

DECISIONES DE IMPLEMENTACIÓN
============================

DI-RD1. **El mismo camino que la página**, con `validacion_2026.preguntar`, y caché propia.
DI-RD2. **El efecto de redacción** es la media de |B − A| y |C − A| sobre las preguntas nuevas con cifra en las dos
    redacciones que se comparan (§3).
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
from src.experiments import validacion_2026 as v26        # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "redaccion"
TOPE_USD = 0.25
REFERENCIA = 6.2                                            # el mejor modelo de lenguaje en el benchmark (R2)
#: §1: (id, código esperado o None, (A, B, C))
PREGUNTAS = (
    ("C1", "AG2", ("¿Qué tan orgullosos se sienten de Bogotá?", "¿La gente siente orgullo de vivir en Bogotá?",
                   "¿Los bogotanos están orgullosos de su ciudad?")),
    ("C2", "CV1", ("¿Qué tan satisfechos están con Bogotá como lugar para vivir?", "¿A la gente le gusta vivir en Bogotá?",
                   "¿Los bogotanos están contentos con la ciudad para vivir?")),
    ("C3", "GG3_GALAN", ("¿Cómo califica la gente la gestión del alcalde Galán?",
                         "¿Qué tan buena es la gestión de Carlos Fernando Galán según los bogotanos?",
                         "¿Los bogotanos creen que Galán lo está haciendo bien como alcalde?")),
    ("C4", "VS8", ("¿La gente se siente segura en su barrio?", "¿Qué tan seguros se sienten los bogotanos en el barrio donde viven?",
                   "¿Se siente seguridad en los barrios de Bogotá?")),
    ("N1", None, ("¿Cree que el metro mejorará la movilidad en Bogotá?", "¿El metro va a mejorar la movilidad de la ciudad?",
                  "¿Los bogotanos creen que con el metro se va a mover mejor la ciudad?")),
    ("N2", None, ("¿Confía en el proyecto del metro de Bogotá?", "¿La gente confía en que el metro de Bogotá salga bien?",
                  "¿Qué tanta confianza le tienen los bogotanos al proyecto del metro?")),
    ("N3", None, ("¿Tiene una imagen favorable del alcalde Galán?", "¿La gente tiene buena imagen de Carlos Fernando Galán?",
                  "¿Qué tan favorable es la opinión de los bogotanos sobre el alcalde Galán?")),
    ("N4", None, ("¿Galán ha manejado bien la seguridad?",
                  "¿Cómo ven los bogotanos el manejo de la seguridad por parte del alcalde Galán?",
                  "¿La gente aprueba lo que ha hecho Galán en seguridad?")),
    ("N5", None, ("¿Se debe persistir en los diálogos de paz con los grupos armados?",
                  "¿Los bogotanos apoyan seguir con los diálogos de paz con los grupos armados?",
                  "¿Hay que continuar las negociaciones de paz con los grupos armados?")),
    ("N6", None, ("¿Colombia debe tener relaciones cercanas con Estados Unidos?",
                  "¿Los bogotanos quieren que Colombia sea cercana a Estados Unidos?",
                  "¿Está de acuerdo con que Colombia mantenga una relación cercana con Estados Unidos?")),
)


def evaluar(res: dict[str, list[dict]]) -> dict:
    """§3 y §4. `res`: id -> las tres respuestas (A, B, C), con alcance, código, porcentaje y llamada."""
    al_codigo = sum(r["alcance"] == "catalogo" and r.get("codigo") == cod for i, cod, _ in PREGUNTAS if cod for r in res[i])
    difs, amplitudes, volteos, cambia_alcance = [], {}, [], []
    for i, cod, _ in PREGUNTAS:
        if cod:
            continue
        rs = res[i]
        if any(r["alcance"] != "nueva" for r in rs):
            cambia_alcance.append(i)
        pc = [r.get("porcentaje") if r["alcance"] == "nueva" else None for r in rs]
        for k in (1, 2):
            if pc[0] is not None and pc[k] is not None:
                difs.append(abs(pc[k] - pc[0]))
        vals = [p for p in pc if p is not None]
        amplitudes[i] = round(max(vals) - min(vals), 1) if len(vals) >= 2 else None
        ll = {r.get("llamada") for r in rs}
        if {"sí", "no"} <= ll:
            volteos.append(i)
    efecto = round(float(np.mean(difs)), 1) if difs else None
    crit = {"R1": {"umbral": "≥ 11 de 12 al código esperado", "valor": al_codigo, "se_cumple": al_codigo >= 11},
            "R2": {"umbral": f"efecto de redacción ≤ {REFERENCIA}", "valor": efecto,
                   "se_cumple": efecto is not None and efecto <= REFERENCIA},
            "R3": {"umbral": "ninguna voltea sí/no", "valor": volteos, "se_cumple": not volteos}}
    return {"criterios": crit, "robusta": all(c["se_cumple"] for c in crit.values()), "efecto": efecto,
            "amplitudes": amplitudes, "cambia_alcance": cambia_alcance, "n_diferencias": len(difs)}


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args(argv)
    from src.consulta import motor as mo
    llamar, modelo = mo.cliente(simulado=a.simulado)
    salida = SALIDA / ("simulado" if a.simulado else "")
    salida.mkdir(parents=True, exist_ok=True)
    cache = e9.Cache(salida / "cache.json")
    m = mo.Motor(llamar, modelo, cache=cache)
    res = {}
    for i, cod, textos in PREGUNTAS:
        res[i] = []
        for letra, t in zip("ABC", textos):
            if not a.simulado and e9.gasto_registrado(cache)["costo_usd"] >= TOPE_USD:
                print(f"Se llegó al tope de USD {TOPE_USD} en {i}{letra}.")
                return 1
            r = {"redaccion": letra, "texto": t, **v26.preguntar(m, t)}
            res[i].append(r)
            print(f"{i}{letra} {t}\n   → {r['alcance']} {r.get('codigo') or ''} | {r.get('porcentaje')} {r.get('rango') or ''} "
                  f"{r.get('llamada') or ''}", flush=True)
    ev = evaluar(res)
    pred = {"PR1": ev["criterios"]["R1"]["se_cumple"], "PR2": ev["efecto"] is not None and 4 <= ev["efecto"] <= 10,
            "PR3": ev["criterios"]["R3"]["se_cumple"], "PR4": ev["robusta"]}
    for k, c in ev["criterios"].items():
        print(f"  {k} {'se cumple' if c['se_cumple'] else 'NO se cumple'} — {c['umbral']} (valor {c['valor']})")
    gasto = e9.gasto_registrado(cache)
    print(f"robusta: {ev['robusta']} | amplitudes {ev['amplitudes']} | cambia de alcance {ev['cambia_alcance']} | "
          f"predicciones {pred} | gasto USD {gasto['costo_usd']:.4f}")
    (salida / "resultado.json").write_text(json.dumps({"respuestas": res, **ev, "predicciones": pred, "gasto": gasto},
                                                      ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
