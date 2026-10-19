"""
Fase D del plan de mejoras (`docs/TEMPORAL_FASE_D_SPECIFICATION.md`): ¿le gana algún método sencillo a repetir el último dato?
Persistencia, promedio de las dos últimas, tendencia amortiguada y encogimiento a la media, en las series de Galán (Invamer y
CB) y en la EPC por año. No llama a ningún modelo.

Uso:
    python src/evaluacion/temporal_fase_d.py

DECISIONES DE IMPLEMENTACIÓN
============================

DI-TD1. **Cada objetivo se predice solo con las mediciones anteriores de su serie** (al menos dos).
DI-TD2. **En la EPC,** la serie de una pregunta son sus olas en el catálogo, en orden; si le falta una ola, la serie sigue con las
    que tiene (por ejemplo, 2022, 2023 y 2025).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

SALIDA = RAIZ / "data" / "processed" / "benchmark"
#: §2
INVAMER = (("2024-02", 54), ("2024-04", 59), ("2024-06", 47), ("2024-08", 50), ("2024-10", 52), ("2024-12", 47),
           ("2025-02", 44), ("2025-04", 42), ("2025-06", 42))
CB = (("2026-03", 43.2), ("2026-04", 46.5), ("2026-06", 44.3), ("2026-07", 45.3), ("2026-08", 49.0), ("2026-09", 45.5))
METODOS = ("M0", "M1", "M2", "M3")


def predecir(x: list[float]) -> dict[str, float]:
    """§4: las cuatro predicciones con las mediciones anteriores x (al menos dos)."""
    u, p = x[-1], x[-2]
    return {"M0": u, "M1": (u + p) / 2, "M2": u + 0.5 * (u - p), "M3": 0.5 * u + 0.5 * float(np.mean(x))}


def objetivos(serie_id: str, valores: list[tuple[str, float]], dominio: str = "gobierno e instituciones") -> list[dict]:
    """DI-TD1."""
    out = []
    for k in range(2, len(valores)):
        prev = [v for _, v in valores[:k]]
        fila = {"serie": serie_id, "fecha": valores[k][0], "dominio": dominio, "real": valores[k][1]}
        fila.update(predecir(prev))
        out.append(fila)
    return out


def regla(t: pd.DataFrame) -> dict:
    """§6: errores medios y quién pasa (menor que M0, y sin los dos objetivos en que más le gana)."""
    e = {m: (t[m] - t.real).abs() for m in METODOS}
    out = {"n": int(len(t)), "error": {m: round(float(e[m].mean()), 2) for m in METODOS}, "pasan": []}
    for m in METODOS[1:]:
        gana = (e["M0"] - e[m]).sort_values(ascending=False)
        resto = gana.index[2:]
        if e[m].mean() < e["M0"].mean() and e[m][resto].mean() < e["M0"][resto].mean():
            out["pasan"].append(m)
    out["elegido"] = min(out["pasan"], key=lambda m: out["error"][m]) if out["pasan"] else "M0"
    return out


def serie_epc() -> list[dict]:
    """DI-TD2."""
    from src.evaluacion import persistencia_epc as pe
    por_anio = {a: pe.cifras(a) for a in pe.ANIOS}
    out = []
    for var in sorted(set().union(*por_anio.values())):
        vals = [(str(a), por_anio[a][var]) for a in pe.ANIOS if var in por_anio[a]]
        for f in objetivos(f"EPC:{var}", vals, pe.dominio(var)):
            if f["fecha"] in ("2024", "2025"):
                out.append(f)
    return out


def main() -> int:
    galan = pd.DataFrame(objetivos("Invamer", list(INVAMER)) + objetivos("CB", list(CB)))
    epc = pd.DataFrame(serie_epc())
    SALIDA.mkdir(parents=True, exist_ok=True)
    pd.concat([galan, epc]).round(2).to_csv(SALIDA / "temporal_fase_d.csv", index=False, encoding="utf-8")
    r1, r2 = regla(epc), regla(galan)
    print(f"RD1, EPC ({r1['n']} objetivos): {r1['error']} | pasan {r1['pasan'] or 'ninguno'} | queda {r1['elegido']}")
    for anio in ("2024", "2025"):
        print(f"   EPC {anio}: {regla(epc[epc.fecha == anio])['error']}")
    print(f"   EPC gobierno: {regla(epc[epc.dominio == 'gobierno e instituciones'])['error']}")
    print(f"RD2, Galán ({r2['n']} objetivos): {r2['error']} | pasan {r2['pasan'] or 'ninguno'} | queda {r2['elegido']}")
    for s in ("Invamer", "CB"):
        print(f"   {s}: {regla(galan[galan.serie == s])['error']}")
    e1 = r1["error"]
    pred = {"PD1": r2["error"]["M3"] < r2["error"]["M0"],
            "PD2": all(e1[m] >= e1["M0"] for m in METODOS[1:]) and e1["M2"] == max(e1.values()),
            "PD3": (r1["elegido"] == "M0") and (r2["elegido"] == "M3")}
    print(f"predicciones: {pred}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
