"""
Plan v5, Paso 3 (`docs/ALCALDE_SIN_NOMBRE_SPECIFICATION.md`): ¿cambia la cifra de los agentes si no se nombra al alcalde? Diagnóstico
del modelo, no una predicción. Mismos 200 perfiles de la EPC 2025 y el método de la página.

Uso:
    python src/evaluacion/prospectiva_epc2026.py              # primero: la condición A sale de ahí (misma caché)
    python src/evaluacion/alcalde_sin_nombre.py [--simulado]

DECISIONES DE IMPLEMENTACIÓN
============================

DI-SN1. **A es la llamada de la página** con el texto de `motor.GALAN_SOLO_AGENTES["GG3_GALAN"]`; con la misma caché que la
    prospectiva, A no se vuelve a pagar. **B** cambia solo el texto de la pregunta.
DI-SN2. **Lo de cada agente** se lee como en `agentes.Agentes.estimar`: «buena» más «muy buena» de las probabilidades de 1-5,
    ponderado con el peso de la encuesta.
DI-SN3. **La respuesta anterior** es la que la persona dio en la EPC 2025 a la gestión del alcalde (`GOB_5`), que va en su perfil.
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402

TOPE_USD = 1.0
TEXTO_B = "¿Usted cómo califica la gestión del alcalde de Bogotá?"
COLUMNA_2025 = "GOB_5"
SALIDA = RAIZ / "data" / "processed" / "benchmark"


def por_agente(panel, texto: str, escala: list[str], llamar, cache, modelo: str) -> np.ndarray:
    """DI-SN2: la probabilidad de «buena» o «muy buena» de cada agente (NaN si no respondió)."""
    from src.consulta import agentes as ag
    from src.experiments import personas_pulidas as pp
    sistema = pp.BASE + pp.SALIDA_PROB
    esc = [{"clave": "E1", "validos": [1, 2, 3, 4, 5]}]

    def uno(perfil):
        if e9.gasto_registrado(cache)["costo_usd"] >= TOPE_USD:
            raise RuntimeError(f"Se llegó al tope de USD {TOPE_USD}.")
        t, _ = e9.pedir(llamar, cache, modelo, ag.TEMPERATURA, sistema, panel._usuario(perfil, texto, escala), 0)
        q = pp.leer_prob(t, esc)["E1"]
        return (q.get(4, 0) + q.get(5, 0)) if q else np.nan
    with ThreadPoolExecutor(max_workers=ag.PARALELO) as ex:
        return np.array(list(ex.map(uno, panel.perfiles)), float)


def media(x: np.ndarray, w: np.ndarray, m: Optional[np.ndarray] = None) -> Optional[float]:
    m = (np.ones(len(x), bool) if m is None else m) & ~np.isnan(x)
    return round(float(100 * np.sum(w[m] * x[m]) / np.sum(w[m])), 2) if m.any() else None


def medir(a: np.ndarray, b: np.ndarray, antes: np.ndarray, w: np.ndarray) -> dict:
    """§4: las tres medidas."""
    fav, nofav = np.isin(antes, [4, 5]), np.isin(antes, [1, 2, 3])
    out = {"A": media(a, w), "B": media(b, w), "panel_2025": media(fav.astype(float), w, fav | nofav)}
    out["A_menos_B"] = round(out["A"] - out["B"], 2)
    for k, x in (("A", a), ("B", b)):
        f, n = media(x, w, fav), media(x, w, nofav)
        out[f"seguimiento_{k}"] = {"antes_favorable": f, "antes_no_favorable": n,
                                   "diferencia": None if f is None or n is None else round(f - n, 2)}
    out["lectura"] = {"el_nombre_mueve": abs(out["A_menos_B"]) >= 5,
                      "siguen_su_respuesta": {k: _lectura(out[f"seguimiento_{k}"]["diferencia"]) for k in ("A", "B")}}
    return out


def _lectura(d: Optional[float]) -> str:
    """§5."""
    if d is None:
        return "sin dato"
    return "la siguen" if d >= 60 else "la siguen poco" if d < 40 else "no concluyente"


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args(argv)
    from src.consulta import agentes as ag
    from src.consulta import motor as mo
    from src.consulta import reformular as rf
    from src.evaluacion import prospectiva_epc2026 as pr
    cat = rf.cargar_catalogo(rf.CATALOGO_2025)
    escala = mo.escala_visible(cat["GG3_GALAN"])
    cache = e9.Cache(pr.CACHE.with_name("simulado_" + pr.CACHE.name) if a.simulado else pr.CACHE)
    llamar, modelo = pr.cliente(a.simulado)
    panel = ag.Agentes()
    xa = por_agente(panel, mo.GALAN_SOLO_AGENTES["GG3_GALAN"], escala, llamar, cache, modelo)
    xb = por_agente(panel, TEXTO_B, escala, llamar, cache, modelo)
    _, d, _ = panel.datos
    antes = pd.to_numeric(d[COLUMNA_2025], errors="coerce").to_numpy()[panel.personas]
    res = medir(xa, xb, antes, panel.peso)
    res["gasto_total_cache"] = None if a.simulado else e9.gasto_registrado(cache)["costo_usd"]
    sal = SALIDA / ("simulado" if a.simulado else "")
    sal.mkdir(parents=True, exist_ok=True)
    (sal / "alcalde_sin_nombre.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=bool), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1, default=bool))
    return 0


if __name__ == "__main__":
    sys.exit(main())
