"""
Validación CNC 2026 (`docs/VALIDACION_CNC_2026_SPECIFICATION.md`): la página frente a siete preguntas de opinión de las
encuestas del CNC para Revista Cambio de 2026, que no están en el banco ni en el catálogo.

Uso:
    python src/experiments/validacion_cnc_2026.py --simulado   # sin gasto: prueba el circuito
    python src/experiments/validacion_cnc_2026.py              # con el modelo real (tope USD 0,15)

Necesita `BSS_CNC_POLITICA_DIR` (D21).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-VK1. **Los resultados reales no se imprimen ni salen del equipo** (D21). Se calculan en `reales()` y se guardan en
    `data/processed/validacion_cnc_2026/`, que git ignora. Lo que se imprime y se reporta es, por pregunta, la
    estimación de la página, si el real cae en el rango y si la llamada acertó; y el error medio solo de las siete juntas.
DI-VK2. **El mismo camino que la página**, con `validacion_2026.preguntar`.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import validacion_2026 as v26        # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "validacion_cnc_2026"
TOPE_USD = 0.15
BOGOTA = "11001"
#: §1: (id, estudio, variable, texto exacto, códigos válidos, códigos que se cuentan)
PREGUNTAS = (
    ("K1", "CC891901", "P21", "¿Cree que Colombia está progresando?", [1, 2, 3], [1]),
    ("K2", "CC891901", "P22", "¿A usted personalmente el aumento del 23 % del salario mínimo lo beneficia?", [1, 2], [1]),
    ("K3", "CC893401", "P13", "¿Se debe incrementar la exploración de petróleo en Colombia?", [1, 2, 3, 4, 5], [4, 5]),
    ("K4", "CC893401", "P14", "¿Se debe persistir en los diálogos de paz con los grupos armados?", [1, 2, 3, 4, 5], [1, 2]),
    ("K5", "CC893401", "P15", "¿Colombia debería tener un Estado más grande que haga más inversión social?", [1, 2, 3, 4, 5],
     [1, 2]),
    ("K6", "CC893401", "P16", "¿Colombia debe tener relaciones cercanas con Estados Unidos?", [1, 2, 3, 4, 5], [4, 5]),
    ("K7", "CC893401", "P17", "¿El sistema de salud lo debe manejar solo el Estado?", [1, 2, 3, 4, 5], [1, 2]),
)


def porcentaje(x: pd.Series, w: pd.Series, validos: list[int], cuenta: list[int]) -> tuple[float, int]:
    """§1: el porcentaje que se cuenta, sin «no sabe», ponderado. (porcentaje, respuestas válidas)."""
    m = x.isin(validos)
    return float(100 * (w[m] * x[m].isin(cuenta)).sum() / w[m].sum()), int(m.sum())


def reales() -> dict[str, float]:
    """DI-VK1: se calculan en el equipo y no se imprimen."""
    from src.experiments import banco_lote7 as b7
    d = os.environ.get("BSS_CNC_POLITICA_DIR")
    if not d or not Path(d).is_dir():
        raise RuntimeError("Falta BSS_CNC_POLITICA_DIR: la carpeta de las encuestas políticas del CNC (D21).")
    out = {}
    for i, est, var, _, validos, cuenta in PREGUNTAS:
        base = Path(d) / b7.ESTUDIOS[est][0]
        cols = pd.read_excel(base, nrows=0).columns
        fac = "factor" if "factor" in cols else "FACTOR"
        b = pd.read_excel(base, usecols=[var, "DANE", fac])
        b = b[b.DANE.astype(str).str.replace(r"\.0$", "", regex=True).str.strip() == BOGOTA]
        out[i] = porcentaje(pd.to_numeric(b[var], errors="coerce"), pd.to_numeric(b[fac], errors="coerce"), validos, cuenta)[0]
    return out


def evaluar(filas: list[dict]) -> dict:
    """§3, con `validacion_2026.evaluar` y el umbral de R1 de este pre-registro."""
    ev = v26.evaluar(filas)
    dentro = ev["criterios"]["R1"]["valor"]
    ev["criterios"]["R1"] = {"umbral": "dentro del rango en ≥ 5 de 7", "valor": dentro, "se_cumple": dentro >= 5}
    ev["pasa"] = all(c["se_cumple"] for c in ev["criterios"].values())
    return ev


def publicable(f: dict) -> dict:
    """DI-VK1: lo que se puede mostrar de una pregunta."""
    p = {k: f.get(k) for k in ("id", "pregunta", "alcance", "codigo", "reformulada", "porcentaje", "rango", "llamada")}
    if f.get("rango"):
        p["dentro_del_rango"] = f["rango"][0] <= f["real"] <= f["rango"][1]
    if f.get("llamada") and f["llamada"] != "dividida":
        p["llamada_acierta"] = (f["llamada"] == "sí") == (f["real"] > 50)
    return p


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args(argv)
    from src.consulta import motor as mo
    real = reales()
    llamar, modelo = mo.cliente(simulado=a.simulado)
    salida = SALIDA / ("simulado" if a.simulado else "")
    salida.mkdir(parents=True, exist_ok=True)
    cache = e9.Cache(salida / "cache.json")
    m = mo.Motor(llamar, modelo, cache=cache)
    filas = []
    for i, _, _, texto, _, _ in PREGUNTAS:
        if not a.simulado and e9.gasto_registrado(cache)["costo_usd"] >= TOPE_USD:
            print(f"Se llegó al tope de USD {TOPE_USD} antes de {i}.")
            return 1
        f = {"id": i, "pregunta": texto, "real": real[i], **v26.preguntar(m, texto)}
        filas.append(f)
        p = publicable(f)
        print(f"{i} {texto}\n   → {p['alcance']} {p.get('codigo') or ''} | página {p.get('porcentaje')} {p.get('rango') or ''} "
              f"{p.get('llamada') or ''} | dentro del rango: {p.get('dentro_del_rango')} | llamada acierta: "
              f"{p.get('llamada_acierta')}", flush=True)
    ev = evaluar(filas)
    pred = {"PK1": not ev["pasa"], "PK2": any(f["alcance"] == "fuera" for f in filas),
            "PK3": sum(f.get("llamada") not in (None, "dividida") for f in filas) <= 2,
            "PK4": ev["criterios"]["R3"]["se_cumple"]}
    for k, c in ev["criterios"].items():
        print(f"  {k} {'se cumple' if c['se_cumple'] else 'NO se cumple'} — {c['umbral']} (valor {c['valor']})")
    gasto = e9.gasto_registrado(cache)
    print(f"pasa: {ev['pasa']} | predicciones: {pred} | gasto USD {gasto['costo_usd']:.4f}")
    (salida / "resultado.json").write_text(json.dumps({"preguntas": filas, **ev, "predicciones": pred, "gasto": gasto},
                                                      ensure_ascii=False, indent=1), encoding="utf-8")
    (salida / "publicable.json").write_text(json.dumps({"preguntas": [publicable(f) for f in filas], **ev,
                                                        "predicciones": pred, "gasto": gasto}, ensure_ascii=False, indent=1),
                                            encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
