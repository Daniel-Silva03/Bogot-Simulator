"""
Nivel por la forma de la pregunta, alternativa 1 sin API (`docs/NIVEL_FORMA_SPECIFICATION.md`):
¿una regresión con la estructura de la pregunta estima su porcentaje favorable mejor que el
promedio? Solo práctica, con la tabla de `nivel_parecidas.tabla()`; las guardadas no se tocan.

Uso:
    python src/experiments/nivel_forma.py

Escribe `data/processed/banco/nivel_forma.json` (solo cifras agregadas).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-NF1. **Las columnas del modelo se fijan con todas las preguntas** (los seis tipos), no en cada
    exclusión. Si al dejar fuera una familia un tipo queda sin preguntas, su columna es toda cero
    y la solución de norma mínima (`numpy.linalg.lstsq`) le da coeficiente 0: la pregunta de ese
    tipo se predice como «otro» (pre-registro §4).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

SALIDA_NOMBRE = "nivel_forma.json"
TIPOS = [("corrupcion", r"corrup"), ("confianza", r"conf[ií]a"), ("imagen", r"imagen|favorable"),
         ("satisfaccion", r"satisf"), ("acuerdo", r"acuerdo")]
NO_CONOCE = re.compile(r"no (lo )?conoce", re.I)
UMBRAL = 18.4                                                # 0,8 × R0 de la parte A
REFERENCIAS = {"R0": 23.0, "R2": 22.0}


def tipo(texto: str) -> str:
    """F3: la primera expresión que coincide, en el orden pre-registrado."""
    for nombre, rx in TIPOS:
        if re.search(rx, str(texto), re.I):
            return nombre
    return "otro"


def rasgos(t: pd.DataFrame) -> pd.DataFrame:
    """F1 a F4 a partir de categorías, códigos favorables, texto y ámbito."""
    from src.experiments import banco_reales as br
    filas = []
    for _, r in t.iterrows():
        cats = br.categorias(r.categorias)
        val = br.validos(cats)
        fav = json.loads(r.codigos_favorables)
        filas.append({"F1": len([c for c in fav if c in val]) / len(val),
                      "F2": float(any(NO_CONOCE.search(cats[c]) for c in val)),
                      "tipo": tipo(r.pregunta_pagina),
                      "F4": float(r.ambito == "Bogotá")})
    return pd.DataFrame(filas, index=t.index)


def matriz(f: pd.DataFrame, usar=("F1", "F2", "F3", "F4")) -> np.ndarray:
    """DI-NF1: columnas fijas; constante + los rasgos pedidos."""
    cols = [np.ones(len(f))]
    for u in usar:
        if u == "F3":
            cols += [(f.tipo == n).to_numpy(float) for n, _ in TIPOS]
        else:
            cols.append(f[u].to_numpy(float))
    return np.column_stack(cols)


def predecir(x: np.ndarray, y: np.ndarray, grupo: np.ndarray) -> np.ndarray:
    """Cada fila con un modelo ajustado sin las filas de su grupo; recortado a [0, 100]."""
    out = np.empty(len(y))
    for g in np.unique(grupo):
        m = grupo == g
        b = np.linalg.lstsq(x[~m], y[~m], rcond=None)[0]
        out[m] = x[m] @ b
    return np.clip(out, 0, 100)


def eam(p: np.ndarray, y: np.ndarray) -> float:
    return float(np.mean(np.abs(p - y)))


def main() -> int:
    from src.experiments import banco as ba
    from src.experiments import nivel_parecidas as npar
    t = npar.tabla()
    f = rasgos(t)
    y, fam = t.total.to_numpy(float), t.familia.to_numpy()
    completo = eam(predecir(matriz(f), y, fam), y)
    sec = {"solo_F1": eam(predecir(matriz(f, ("F1",)), y, fam), y)}
    for quitar in ("F1", "F2", "F3", "F4"):
        sec[f"sin_{quitar}"] = eam(predecir(matriz(f, [u for u in ("F1", "F2", "F3", "F4") if u != quitar]), y, fam), y)
    sec["dejando_solo_la_pregunta"] = eam(predecir(matriz(f), y, np.arange(len(y))), y)
    coef = np.linalg.lstsq(matriz(f), y, rcond=None)[0]
    nombres = ["constante", "F1", "F2"] + [f"tipo_{n}" for n, _ in TIPOS] + ["F4"]
    pred = {"P1": sec["solo_F1"] < REFERENCIAS["R0"], "P2": completo < REFERENCIAS["R2"],
            "P3": completo <= UMBRAL, "P4": bool(coef[1] > 0)}
    print(f"{len(t)} preguntas, {len(set(fam))} familias; tipos: {f.tipo.value_counts().to_dict()}; "
          f"F2=1 en {int(f.F2.sum())}")
    print(f"EAM modelo completo: {completo:.1f}  (R0 {REFERENCIAS['R0']}, R2 {REFERENCIAS['R2']}, umbral {UMBRAL})")
    print("secundarias: " + ", ".join(f"{k} {v:.1f}" for k, v in sec.items()))
    print("coeficientes (96): " + ", ".join(f"{n} {c:+.1f}" for n, c in zip(nombres, coef)))
    print(f"predicciones: {pred}; pasa: {completo <= UMBRAL}")
    (ba.SALIDA / SALIDA_NOMBRE).write_text(json.dumps(
        {"n": len(t), "eam_completo": completo, "secundarias": sec, "coeficientes": dict(zip(nombres, map(float, coef))),
         "predicciones": pred, "pasa": completo <= UMBRAL, "rasgos": f.assign(id=t.id, total=y).to_dict("records")},
        ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
