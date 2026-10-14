"""
Validación 2026 (`docs/VALIDACION_2026_SPECIFICATION.md`): la página, tal como está, frente a seis preguntas de Bogotá con
resultado publicado en 2026 que la EPC no midió.

Uso:
    python src/experiments/validacion_2026.py --simulado   # sin gasto: prueba el circuito
    python src/experiments/validacion_2026.py              # con el modelo real (tope USD 0,20)

Escribe `data/processed/validacion_2026/resultado.json`; caché propia en la misma carpeta.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-V26-1. **El mismo camino que la página** (`pagina.html`, `preguntar`): reformular; si es nueva, `responder_nueva` con la
    reformulada, su escala y el texto original (DI-CO28); si va al catálogo, `responder_catalogo`.
DI-V26-2. **El tope se revisa antes de cada pregunta** con lo que registra la caché; una pregunta en curso puede pasarlo
    por centavos.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "validacion_2026"
TOPE_USD = 0.20
#: §1: (id, texto exacto, resultado conocido)
PREGUNTAS = (
    ("V1", "¿Cree que el metro mejorará la movilidad en Bogotá?", 93.0),
    ("V2", "¿Usaría el metro como su principal medio de transporte?", 70.0),
    ("V3", "¿Confía en el proyecto del metro de Bogotá?", 80.0),
    ("V4", "¿El metro es un motivo de orgullo para Bogotá?", 88.0),
    ("V5", "¿Cree que el metro empezará a funcionar en 2028?", 56.0),
    ("V6", "¿Tiene una imagen favorable del alcalde Galán?", 26.0),
)
COMPARACION = ("C1", "¿Aprueba la gestión del alcalde Galán?", 53.3)          # §5: sin regla


def preguntar(m, texto: str) -> dict:
    """DI-V26-1: lo que mostraría la página."""
    r = m.reformular(texto)
    out = {"alcance": r["alcance"], "codigo": r.get("codigo"), "reformulada": r.get("reformulada")}
    if r["alcance"] == "nueva":
        e = m.responder_nueva(r["reformulada"], r["escala"], original=texto)["estimacion"]
        if e:
            out.update(porcentaje=e["porcentaje"], rango=e["rango"], llamada=e["llamada"],
                       apoyo=[q["pregunta"] for q in e["preguntas"]])
    elif r["alcance"] == "catalogo":
        c = m.responder_catalogo(r["codigo"])
        out.update(porcentaje=round(100 * c["ciudad"]["alto"], 1), etiqueta=c["ciudad"]["etiqueta_alto"])
    return out


def evaluar(filas: list[dict]) -> dict:
    """§3."""
    dentro = acierta = decide = 0
    errores, ref = [], []
    for f in filas:
        real, p = f["real"], f.get("porcentaje")
        ref.append(abs(50 - real))
        if f["alcance"] == "fuera" or p is None:
            errores.append(abs(50 - real) if p is None and f["alcance"] != "fuera" else 100.0)
            if f["alcance"] == "fuera":
                decide += 1                                           # cuenta como una llamada fallida
            continue
        errores.append(abs(p - real))
        if f["alcance"] == "nueva" and "rango" in f:
            dentro += f["rango"][0] <= real <= f["rango"][1]
            if f["llamada"] != "dividida":
                decide += 1
                acierta += (f["llamada"] == "sí") == (real > 50)
    eam, eam50 = sum(errores) / len(errores), sum(ref) / len(ref)
    crit = {"R1": {"umbral": "dentro del rango en ≥ 4 de 6", "valor": dentro, "se_cumple": dentro >= 4},
            "R2": {"umbral": "al decidir, falla en 1 como máximo", "valor": [acierta, decide],
                   "se_cumple": decide - acierta <= 1},
            "R3": {"umbral": f"error medio menor que decir 50 % ({eam50:.1f})", "valor": round(eam, 1),
                   "se_cumple": eam < eam50}}
    return {"criterios": crit, "pasa": all(c["se_cumple"] for c in crit.values()), "eam": round(eam, 1),
            "eam_50": round(eam50, 1)}


def predicciones(filas: list[dict], ev: dict) -> dict:
    """§4."""
    metro = [f for f in filas if f["id"] in ("V1", "V2", "V3", "V4") and f.get("porcentaje") is not None]
    v6 = next(f for f in filas if f["id"] == "V6")
    return {"PV1": ev["pasa"], "PV2": bool(metro) and all(f["porcentaje"] < f["real"] for f in metro),
            "PV3": v6.get("llamada") != "sí", "PV4": all(f["alcance"] != "fuera" for f in filas)}


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
    filas = []
    for i, texto, real in PREGUNTAS + (COMPARACION,):
        if not a.simulado and e9.gasto_registrado(cache)["costo_usd"] >= TOPE_USD:   # DI-V26-2
            print(f"Se llegó al tope de USD {TOPE_USD} antes de {i}.")
            return 1
        f = {"id": i, "pregunta": texto, "real": real, **preguntar(m, texto)}
        filas.append(f)
        print(f"{i} {texto}\n   → {f['alcance']} {f.get('codigo') or ''} | página {f.get('porcentaje')} "
              f"{f.get('rango', '')} {f.get('llamada', '')} | real {real}", flush=True)
    ev = evaluar(filas[:6])
    pred = predicciones(filas[:6], ev)
    for k, c in ev["criterios"].items():
        print(f"  {k} {'se cumple' if c['se_cumple'] else 'NO se cumple'} — {c['umbral']} (valor {c['valor']})")
    gasto = e9.gasto_registrado(cache)
    print(f"pasa: {ev['pasa']} | predicciones: {pred} | gasto USD {gasto['costo_usd']:.4f}")
    (salida / "resultado.json").write_text(json.dumps({"preguntas": filas, **ev, "predicciones": pred, "gasto": gasto},
                                                      ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
