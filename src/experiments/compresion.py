"""
Compresión hacia el medio (`docs/COMPRESION_SPECIFICATION.md`): cuánto aplana la estimación de preguntas nuevas, y si
mejora estirándola con a + b · estimación, aprendido fuera de muestra. Sin API.

Uso:
    python src/experiments/compresion.py

DECISIONES DE IMPLEMENTACIÓN
============================

DI-CM1. **La estimación es la de E** (`nivel_acuerdo_catalogo.json`), la que usa la página, en los 139 objetivos.
DI-CM2. **Fuera de muestra por familia:** `GroupKFold` de 5 grupos. La métrica de cada pliegue es la de
    `nivel_acuerdo_validacion.evaluar`, con el rango del cuantil 80 % del error fuera de muestra.
DI-CM3. **Solo cifras agregadas** (D21): nada por pregunta.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

SALIDA = RAIZ / "data" / "processed" / "banco" / "compresion.json"
GRUPOS = 5
CUANTIL = 0.8


def ajustar(s: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """(a, b) de y ≈ a + b · s por mínimos cuadrados."""
    b, a = np.polyfit(s, y, 1)
    return float(a), float(b)


def estirar(s: np.ndarray, a: float, b: float) -> np.ndarray:
    return np.clip(a + b * s, 0, 100)


def fuera_de_muestra(s: np.ndarray, y: np.ndarray, fam: np.ndarray) -> np.ndarray:
    """DI-CM2."""
    from sklearn.model_selection import GroupKFold
    out = np.empty(len(s))
    for tr, te in GroupKFold(n_splits=GRUPOS).split(s, y, fam):
        out[te] = estirar(s[te], *ajustar(s[tr], y[tr]))
    return out


def compresion(s: np.ndarray, y: np.ndarray) -> dict:
    a, b = ajustar(s, y)
    return {"sd_estimacion": round(float(s.std()), 1), "sd_real": round(float(y.std()), 1), "pendiente": round(b, 2),
            "intercepto": round(a, 1)}


def main() -> int:
    from src.experiments import nivel_acuerdo_catalogo as nc
    from src.experiments import nivel_acuerdo_lote6 as n6
    from src.experiments import nivel_acuerdo_lote8 as n8
    from src.experiments import nivel_acuerdo_validacion as nv
    from src.experiments import validacion_2026 as v26
    from src.experiments import validacion_cnc_2026 as vk
    d = json.loads(nc.SALIDA.read_text(encoding="utf-8"))
    p = pd.DataFrame(d["E"]["por_pregunta"])[["id", "familia", "total", "S"]].dropna()
    cand = nc.candidatas()[1]
    obj = pd.concat(n8.objetivos(), ignore_index=True)
    s, y, fam = p.S.to_numpy(float), p.total.to_numpy(float), p.familia.to_numpy()
    comp = compresion(s, y)
    hoy = n6._cifras(nv.evaluar(p.assign(fallo=False), cand, obj, h=nc.H))
    s2 = fuera_de_muestra(s, y, fam)
    h2 = float(np.quantile(np.abs(s2 - y), CUANTIL))
    est = n6._cifras(nv.evaluar(p.assign(S=s2, fallo=False), cand, obj, h=h2))
    a, b = ajustar(s, y)
    ext = {}
    for g, ruta, filtro in (("V_sin_V5", v26.SALIDA, lambda f: f["id"] != "V5"), ("V5", v26.SALIDA, lambda f: f["id"] == "V5"),
                            ("K", vk.SALIDA, lambda f: True)):
        r = ruta / "resultado.json"
        if not r.exists():
            continue
        filas = [f for f in json.loads(r.read_text(encoding="utf-8"))["preguntas"] if f["id"].startswith(("V", "K"))
                 and filtro(f) and f.get("porcentaje") is not None]
        pg = np.array([f["porcentaje"] for f in filas], float); rl = np.array([f["real"] for f in filas], float)
        ext[g] = {"hoy": round(float(np.abs(pg - rl).mean()), 1), "estirada": round(float(np.abs(estirar(pg, a, b) - rl).mean()), 1)}
    regla = {"error_baja_0_5": est["eam"] <= hoy["eam"] - 0.5, "lado_no_baja": est["lado"] >= hoy["lado"],
             "al_decidir_90": (est["acierto_al_decidir"] or 0) >= 0.90 if est["decide"] > 0 else False,
             "2026_no_sube": ext.get("V_sin_V5", {}).get("estirada", 99) <= ext.get("V_sin_V5", {}).get("hoy", 0)}
    regla["estirar"] = all(regla.values())
    pred = {"PC1": comp["sd_estimacion"] < comp["sd_real"] and comp["pendiente"] > 1,
            "PC2": hoy["eam"] - est["eam"] < 1, "PC3": est["decide"] > hoy["decide"], "PC4": not regla["estirar"]}
    print(f"compresión: {comp}")
    for n, r, h in (("hoy", hoy, nc.H), ("estirada (fuera de muestra)", est, round(h2, 1))):
        print(f"{n}: EAM {r['eam']:.1f} | lado {r['lado']:.0%} | decide {r['decide']:.0%} («sí» {r['acierta_si']}/{r['dice_si']}, "
              f"«no» {r['acierta_no']}/{r['dice_no']}) | rango ±{h}")
    print(f"a, b con las 139: {round(a, 1)}, {round(b, 2)} | externa: {ext}")
    print(f"regla: {regla} | predicciones: {pred}")
    SALIDA.write_text(json.dumps({"compresion": comp, "hoy": hoy, "estirada": est, "h_estirada": h2, "a": a, "b": b,
                                  "externa": ext, "regla": regla, "predicciones": pred}, ensure_ascii=False, indent=1,
                                 default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
