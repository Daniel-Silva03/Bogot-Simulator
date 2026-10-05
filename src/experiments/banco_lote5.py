"""
Quinto lote del banco de preguntas nuevas: Encuesta Distrital de Percepción (EDP) 2025 de la Secretaría
Distrital de Planeación (`docs/BANCO_PREGUNTAS_NUEVAS.md` §14). Sin API.

Uso:
    python src/experiments/banco_lote5.py --sorteo      # escribe sorteo_lote5.csv
    python src/experiments/banco_lote5.py --reales      # resultados reales de las de práctica

DECISIONES DE IMPLEMENTACIÓN
============================

DI-BL7. **El texto de cada afirmación sale del diccionario de la SDP** (columna de descripción, sin la
    letra inicial «a. »), igual que en el lote 3 sale de la documentación de la Bienal.

DI-BL8. **Mismo cálculo que los otros lotes** (`banco_lote3._calcular`): solo cambian las columnas y el
    peso. Se leen solo las columnas necesarias de la base.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import banco as ba                    # noqa: E402
from src.experiments import banco_lote3 as b3              # noqa: E402

BASE = RAIZ / "data" / "raw" / "sdp" / "base_ano_movil_2025.csv"
DICCIONARIO = RAIZ / "data" / "raw" / "sdp" / "20260331_diccionario_base_ano_movil_2025.xlsx"
SORTEO = ba.SALIDA / "sorteo_lote5.csv"
REALES = ba.SALIDA / "reales_practica_lote5.json"
SEMILLA = 20261009
FUENTE = "SDP Percepción Distrital"
BLOQUES = ("104", "105", "408", "503", "602", "603", "604", "704")
EXCLUIR = {"Hx704", "Ax602"}                                  # §14: repiten AG2 y MV4
ESCALA = "1=Totalmente en desacuerdo; 2=En desacuerdo; 3=Ni de acuerdo ni en desacuerdo; 4=De acuerdo; 5=Totalmente de acuerdo; 99=Ns/Nr"
COLS = {"w": "fexp_calp_anu", "sexo": "D1", "edad": "A6x3", "estrato": "H1", "localidad": "Cod_Locali"}


class Lote5Error(RuntimeError):
    """Algo no cuadra con lo pre-registrado en §14."""


def variables(columnas: list[str]) -> list[str]:
    v = [c for c in columnas if re.fullmatch(r"[A-J]x(" + "|".join(BLOQUES) + r")", c) and c not in EXCLUIR]
    return sorted(v, key=lambda c: (BLOQUES.index(c[2:]), c[0]))


def tabla(base: Path = BASE, diccionario: Path = DICCIONARIO) -> pd.DataFrame:
    """Las 38 afirmaciones como filas del banco (DI-BL7)."""
    v = variables(pd.read_csv(base, nrows=0).columns.tolist())
    d = pd.read_excel(diccionario, sheet_name="Diccionario de datos", header=1)
    desc = dict(zip(d.iloc[:, 4].astype(str), d.iloc[:, 5].astype(str)))
    filas = []
    for c in v:
        if c not in desc:
            raise Lote5Error(f"{c} no está en el diccionario.")
        frase = re.sub(r"^\s*[a-j]\.\s*", "", " ".join(desc[c].split())).rstrip(".")
        filas.append({"id": f"EDP25_{c}", "familia": f"EDP25_Q{c[2:]}", "ambito": "Bogotá", "fuente": FUENTE, "anio": 2025,
                      "variable": c, "independiente": True, "pregunta_pagina": f"¿Está de acuerdo con que «{frase}»?",
                      "codigos_favorables": json.dumps([4, 5]), "categorias": ESCALA, "tema": f"EDP bloque {c[2:]}"})
    return pd.DataFrame(filas)


def base_edp(base: Path = BASE):
    """(x de una fila del sorteo, peso, grupos, localidad) — DI-BL8."""
    v = variables(pd.read_csv(base, nrows=0).columns.tolist())
    d = pd.read_csv(base, usecols=v + list(COLS.values()) + ["DIRECTORIO_MZ"])
    num = lambda c: pd.to_numeric(d[c], errors="coerce")                       # noqa: E731
    sexo = num(COLS["sexo"]).map({1: "Hombres", 2: "Mujeres"})
    estrato = num(COLS["estrato"]).where(num(COLS["estrato"]).between(1, 6))
    loc = num(COLS["localidad"])
    loc = loc.where(loc.between(1, 19)).astype("Int64").astype(str).replace("<NA>", None)
    g = b3._grupos(sexo, num(COLS["edad"]), estrato)
    return (lambda f: num(f["variable"])), num(COLS["w"]), g, loc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sorteo", action="store_true")
    ap.add_argument("--reales", action="store_true")
    a = ap.parse_args(argv)
    if a.sorteo:
        if SORTEO.exists():
            raise Lote5Error(f"{SORTEO.name} ya existe: el sorteo se hace una sola vez.")
        s = b3.sortear(tabla(), SEMILLA)
        s.to_csv(SORTEO, index=False, encoding="utf-8")
        print(s.groupby("conjunto").agg(preguntas=("id", "size"), familias=("familia", "nunique")).to_dict())
        print(s.groupby("conjunto").familia.unique().to_dict())
    if a.reales:
        r = b3._calcular(pd.read_csv(SORTEO), *base_edp())
        REALES.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        exc = {k: v["excluida"] for k, v in r.items() if v["excluida"]}
        ns = [v["n"] for v in r.values() if not v["excluida"]]
        print(f"{len(r)} de práctica; excluidas por estructura {len(exc)} {exc or ''}; pares claros "
              f"{sum(len(v['pares_claros']) for v in r.values() if not v['excluida'])}; n válidas {min(ns)}-{max(ns)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
