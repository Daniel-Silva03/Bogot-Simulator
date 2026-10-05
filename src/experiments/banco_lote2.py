"""
Segundo lote del banco de preguntas nuevas: Encuesta de Cultura Ambiental (ECA) 2021 de la SCRD
(`docs/BANCO_PREGUNTAS_NUEVAS.md` §11). Sin API.

Uso:
    python src/experiments/banco_lote2.py --sorteo      # escribe sorteo_lote2.csv
    python src/experiments/banco_lote2.py --reales      # resultados reales de las de práctica

Escribe en `data/processed/banco/`: `sorteo_lote2.csv` y `reales_practica_lote2.json` (cifras
agregadas; se suben). No toca `sorteo.csv` ni `reales_practica.json` del primer lote.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-BL1. **Las columnas se leen por posición** en la hoja `NUM` (contadas desde 0, como en §11), porque
    sus encabezados ocupan dos filas y varias columnas quedan sin nombre. Antes de calcular se
    comprueba que el encabezado de cada una contenga el fragmento de texto esperado; si no, se
    detiene.

DI-BL2. **Mismo cálculo que el primer lote:** `banco_reales.resultado`, `pares_claros` y
    `estructura`, con los grupos de §11. Solo cambian las columnas y el peso (`FACTOR PERSONAS`).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import banco as ba                    # noqa: E402
from src.experiments import banco_reales as br             # noqa: E402

ARCHIVO = RAIZ / "data" / "raw" / "scrd" / "eca_2021_scrd.xlsx"
SORTEO = ba.SALIDA / "sorteo_lote2.csv"
REALES = ba.SALIDA / "reales_practica_lote2.json"
SEMILLA = 20261005
FUENTE = "SCRD Cultura Ambiental"

ACUERDO2 = "1=De acuerdo; 2=En desacuerdo; 99=NS/NR"
ACUERDO4 = "1=Totalmente en desacuerdo; 2=En desacuerdo; 3=De acuerdo; 4=Totalmente de acuerdo; 99=NS/NR"
MUCHO3 = "1=Mucho; 2=Poco; 3=Nada; 99=NS/NR"

#: §11: (id, familia, columna, fragmento del encabezado, pregunta en la página, categorías, favorables, tema)
PREGUNTAS = [
    ("ECA21_P13A", "ECA21_P13", 47, "todo termina revuelto",
     "¿Está de acuerdo con que «da igual si se separan o no los residuos porque al final todo termina revuelto»?", ACUERDO2, [1], "separación de residuos"),
    ("ECA21_P13B", "ECA21_P13", 48, "lo hacen los recicladore",
     "¿Está de acuerdo con que «da igual si se separan o no los residuos porque eso lo hacen los recicladores»?", ACUERDO2, [1], "separación de residuos"),
    ("ECA21_P14AA", "ECA21_P14A", 53, "Confía en las personas recicladoras",
     "¿Está de acuerdo con que confía en las personas recicladoras de oficio?", ACUERDO2, [1], "recicladores"),
    ("ECA21_P14AB", "ECA21_P14A", 54, "es fundamental",
     "¿Está de acuerdo con que la población recicladora de oficio es fundamental para el aprovechamiento de residuos en Bogotá?", ACUERDO2, [1], "recicladores"),
    ("ECA21_P14AC", "ECA21_P14A", 55, "son peligrosas",
     "¿Está de acuerdo con que las personas recicladoras de oficio son peligrosas?", ACUERDO2, [1], "recicladores"),
    ("ECA21_P15", "ECA21_P15", 56, "15. ¿Usted cree que la mayoría",
     "¿Cree que la mayoría de las personas en Bogotá separa los residuos en sus hogares?", "1=Sí; 2=No; 99=NS/NR", [1], "separación de residuos"),
    ("ECA21_P19A", "ECA21_P19", 70, "Río Bogotá está tan sucio",
     "¿Está de acuerdo con que «el río Bogotá está tan sucio que da igual si le tiran más residuos»?", ACUERDO4, [3, 4], "cuidado ambiental"),
    ("ECA21_P19B", "ECA21_P19", 71, "no existen sistemas de reciclaje",
     "¿Está de acuerdo con que «como no existen sistemas de reciclaje en toda la ciudad, da igual si separo o no los residuos en mi casa»?", ACUERDO4, [3, 4], "cuidado ambiental"),
    ("ECA21_P19C", "ECA21_P19", 72, "industrias son las que más contaminan",
     "¿Está de acuerdo con que «como las industrias son las que más contaminan, los esfuerzos que haga por cuidar el ambiente son insignificantes»?", ACUERDO4, [3, 4], "cuidado ambiental"),
    ("ECA21_P22", "ECA21_P22", 76, "22. En su opinión",
     "¿Qué tanto cuidan las personas en Bogotá a los animales silvestres que viven en la ciudad?", "1=Mucho; 2=Poco; 3=Nada; 99=Ns/Nr", [1], "fauna silvestre"),
    ("ECA21_P32", "ECA21_P32", 103, "32. En general",
     "¿El estado de la mayoría de los ríos, humedales y espacios naturales de Bogotá es bueno?",
     "1=Muy bueno; 2=Bueno; 3=Malo; 4=Muy malo; 99=NS/NR", [1, 2], "estructura ecológica"),
    ("ECA21_P33A", "ECA21_P33", 104, "usted mismo",
     "¿Qué tanto puede hacer usted mismo para cuidar el ambiente?", MUCHO3, [1], "responsabilidad ambiental"),
    ("ECA21_P33B", "ECA21_P33", 105, "el resto de la ciudadanía",
     "¿Qué tanto puede hacer el resto de la ciudadanía para cuidar el ambiente?", MUCHO3, [1], "responsabilidad ambiental"),
    ("ECA21_P33C", "ECA21_P33", 106, "el gobierno de la ciudad",
     "¿Qué tanto puede hacer el gobierno de la ciudad para cuidar el ambiente?", MUCHO3, [1], "responsabilidad ambiental"),
    ("ECA21_P33D", "ECA21_P33", 107, "el gobierno nacional",
     "¿Qué tanto puede hacer el gobierno nacional para cuidar el ambiente?", MUCHO3, [1], "responsabilidad ambiental"),
    ("ECA21_P33E", "ECA21_P33", 108, "fábricas y empresas",
     "¿Qué tanto pueden hacer las fábricas y empresas en general para cuidar el ambiente?", MUCHO3, [1], "responsabilidad ambiental"),
]
#: §11: columnas de los grupos y el peso, con su fragmento de encabezado (DI-BL1).
COLUMNAS = {"localidad": (5, "LOCALIDAD"), "estrato": (6, "estrato"), "sexo": (7, "género"),
            "edad": (10, "años cumplidos tiene usted? (Mayor)"), "w": (114, "FACTOR PERSONAS")}


class Lote2Error(RuntimeError):
    """Algo no cuadra con lo pre-registrado en §11."""


def tabla() -> pd.DataFrame:
    """Las 16 preguntas como filas del banco (mismas columnas que `sorteo.csv`)."""
    return pd.DataFrame([{"id": i, "familia": f, "ambito": "Bogotá", "fuente": FUENTE, "anio": 2021,
                          "variable": f"NUM:{c}", "independiente": True, "pregunta_pagina": p, "codigos_favorables": json.dumps(fav),
                          "categorias": cats, "tema": tema} for i, f, c, _, p, cats, fav, tema in PREGUNTAS])


def sortear(t: pd.DataFrame, semilla: int = SEMILLA) -> pd.DataFrame:
    """§11: regla 3 de DI-BA5, por familia; la mitad redondeando hacia arriba al guardado."""
    fams = sorted(t.familia.unique())
    orden = list(np.random.default_rng(semilla).permutation(fams))
    guardadas = set(orden[: (len(orden) + 1) // 2])
    t = t.assign(conjunto=np.where(t.familia.isin(guardadas), "guardado", "practica"), motivo="sorteo")
    return t[["id", "familia", "conjunto", "motivo", "ambito", "fuente", "anio", "variable", "independiente",
              "pregunta_pagina", "codigos_favorables", "categorias", "tema"]].sort_values(["conjunto", "familia", "id"])


def cargar(ruta: Path = ARCHIVO) -> pd.DataFrame:
    """Hoja NUM con encabezado de dos filas; comprueba cada columna por su fragmento (DI-BL1)."""
    d = pd.read_excel(ruta, sheet_name="NUM", header=None)
    enc = [f"{d.iat[0, i]} {d.iat[1, i]}" for i in range(d.shape[1])]
    revisar = [(c, frag) for _, _, c, frag, *_ in PREGUNTAS] + list(COLUMNAS.values())
    for c, frag in revisar:
        if frag.lower() not in enc[c].lower():
            raise Lote2Error(f"La columna {c} no dice «{frag}»: {enc[c][:120]!r}")
    return d.iloc[2:].reset_index(drop=True)


def grupos(d: pd.DataFrame) -> dict[str, pd.Series]:
    num = lambda k: pd.to_numeric(d[COLUMNAS[k][0]], errors="coerce")      # noqa: E731
    return {"sexo": num("sexo").map({1: "Hombres", 2: "Mujeres"}),
            "edad": br.edad_grupo(num("edad"), en_tramos=False),
            "estrato": num("estrato").map(br.estrato_grupo)}


def reales(sorteo: pd.DataFrame, d: pd.DataFrame) -> dict:
    """Resultados de las preguntas de PRÁCTICA del lote 2 (DI-BL2). Las guardadas no se calculan."""
    adultos = pd.to_numeric(d[COLUMNAS["edad"][0]], errors="coerce") >= 18
    d = d[adultos].reset_index(drop=True)
    w = pd.to_numeric(d[COLUMNAS["w"][0]], errors="coerce")
    g = grupos(d)
    loc = pd.to_numeric(d[COLUMNAS["localidad"][0]], errors="coerce")
    loc = loc.where(loc.between(1, 19)).astype("Int64").astype(str).replace("<NA>", None)
    col = {i: c for i, _, c, *_ in PREGUNTAS}
    out = {}
    for f in sorteo[sorteo.conjunto == "practica"].to_dict("records"):
        x = pd.to_numeric(d[col[f["id"]]], errors="coerce")
        cats = br.categorias(f["categorias"])
        fav = json.loads(f["codigos_favorables"])
        res = br.resultado(x, w, g, fav, br.validos(cats))
        lres = br.resultado(x, w, {"localidad": loc}, fav, br.validos(cats))
        res["localidad"], res["bases_localidad"] = lres["grupos"]["localidad"], lres["bases"]["localidad"]
        res["cortes_edad"] = "18-25, 26-35, 36-45, 46-55, 56+"
        res["pares_claros"] = br.pares_claros(res)
        res["excluida"] = br.estructura(res)
        out[f["id"]] = {"familia": f["familia"], "ambito": f["ambito"], "fuente": f["fuente"], "anio": int(f["anio"]),
                        "pregunta_pagina": f["pregunta_pagina"], **res}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sorteo", action="store_true")
    ap.add_argument("--reales", action="store_true")
    a = ap.parse_args(argv)
    if a.sorteo:
        if SORTEO.exists():
            raise Lote2Error(f"{SORTEO.name} ya existe: el sorteo se hace una sola vez.")
        s = sortear(tabla())
        s.to_csv(SORTEO, index=False, encoding="utf-8")
        print(s.groupby("conjunto").agg(preguntas=("id", "size"), familias=("familia", "nunique")))
        print(s.groupby("conjunto").familia.unique().to_dict())
    if a.reales:
        r = reales(pd.read_csv(SORTEO), cargar())
        REALES.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        exc = {k: v["excluida"] for k, v in r.items() if v["excluida"]}
        print(f"{len(r)} de práctica; excluidas por estructura {len(exc)} {exc or ''}; "
              f"pares claros {sum(len(v['pares_claros']) for v in r.values() if not v['excluida'])}; "
              f"n válidas {[v['n'] for v in r.values()]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
