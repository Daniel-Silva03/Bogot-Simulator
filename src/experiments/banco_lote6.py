"""
Sexto lote del banco de preguntas nuevas: encuestas políticas del CNC para Semana, nivel 1 de D21
(`docs/BANCO_PREGUNTAS_NUEVAS.md` §15). Solo los encuestados de Bogotá. Sin API.

Las bases viven fuera del repositorio, en la carpeta de `BSS_CNC_POLITICA_DIR` (D21). Este módulo nunca
escribe en ella ni copia nada al repositorio; los resultados de práctica son agregados.

Uso:
    python src/experiments/banco_lote6.py --tabla       # muestra las preguntas y su texto, sin datos
    python src/experiments/banco_lote6.py --sorteo      # escribe sorteo_lote6.csv
    python src/experiments/banco_lote6.py --reales      # resultados reales de las de práctica

DECISIONES DE IMPLEMENTACIÓN
============================

DI-BL9. **Las preguntas van en una lista explícita** (`PREGUNTAS`), copiada de §15, y no se eligen por
    patrón: así lo pre-registrado es exactamente lo que entra.
DI-BL10. **El texto de la página sale de la etiqueta del diccionario**, sin el número de la pregunta, sin las
    instrucciones al encuestador y con la subpregunta dentro de la frase (`texto`).
DI-BL11. **La edad va en los grupos de cada encuesta** (18-25, 26-40, 41-55, 56+), no en los de la
    población, y `cortes_edad` lo dice. CC355801 no trae edad: va sin ese grupo.
DI-BL13. **El año de CC873501 es un supuesto: 2022.** Hecho: ni la base ni el diccionario traen fecha. Supuesto,
    por el contenido: pregunta por la gestión de Duque (presidente hasta agosto de 2022), por la Coalición de
    la Experiencia y por candidatos a 2022, y por el carné de vacunación. Es de finales de 2021 o
    comienzos de 2022. Daniel puede confirmarlo con el CNC.
DI-BL14. **Nueve textos van escritos a mano** (`TEXTO_MANUAL`). Hecho: en el diccionario, tres etiquetas de
    CC355801 están cortadas y terminan en un resto de formato («colF8», «F8.2»); otras traen dos signos de
    apertura («¿Dígame por favor ¿está…»), una errata («continué») o el nombre en mayúsculas. Se escriben
    como en el cuestionario, sin cambiar el sentido. En P5_SEM_3 se completa «no ingresen más migrantes»:
    es un supuesto razonable, y la etiqueta lo deja cortado.
DI-BL12. **Sin localidad:** se pasa una serie vacía a `banco_lote3._calcular`, así que `localidad` sale
    vacía y no hay pares claros de localidades.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import banco as ba                    # noqa: E402
from src.experiments import banco_lote3 as b3              # noqa: E402
from src.experiments import banco_reales as br             # noqa: E402

SORTEO = ba.SALIDA / "sorteo_lote6.csv"
REALES = ba.SALIDA / "reales_practica_lote6.json"
SEMILLA = 20261010
FUENTE = "CNC para Semana"
BOGOTA = "11001"
ACUERDO5 = "1=Totalmente de acuerdo; 2=De acuerdo; 3=Ni de acuerdo ni en desacuerdo; 4=En desacuerdo; 5=Totalmente en desacuerdo; 9=NS/NR"
ESCALAS = {"acuerdo5": (ACUERDO5, [1, 2]), "acuerdo2": ("1=De acuerdo; 2=En desacuerdo; 9=NS/NR", [1]),
           "si_no": ("1=Sí; 2=No; 9=NS/NR", [1]), "aprueba": ("1=Aprueba; 2=Desaprueba; 9=NS/NR", [1])}

#: §15 (DI-BL9): estudio -> (base, diccionario, [(variable, escala)])
_r = lambda p, n, e: [(f"{p}_{i}", e) for i in range(1, n + 1)]                 # noqa: E731
PREGUNTAS = {
    "CC355801": ("CC355801_SemanaFebrero2021_BaseCodigos.xlsx", "CC355801_SemanaFebrero2021_DiccionariodeDatos.xlsx",
                 _r("P1_SEM", 7, "acuerdo5") + _r("P2_SEM", 7, "acuerdo5") + _r("P4_SEM", 7, "acuerdo5") + _r("P5_SEM", 9, "acuerdo5")),
    "CC871401": ("CC871401_SEMANA_MAYO21_BaseCodigos.xlsx", "CC871401_SEMANA_MAYO21_DiccionariodeDatos.xlsx",
                 [("P9", "si_no"), ("P10", "acuerdo2"), ("P11", "acuerdo2"), ("P12", "si_no"), ("P14", "si_no"),
                  ("T19_1", "si_no"), ("T19_2", "si_no"), ("P20", "si_no")] + _r("T24", 16, "si_no")),
    "CC871801": ("CC871801_SEM_JUN1621_BaseCodigos.xlsx", "CC871801_SEM_JUN1621_DiccionariodeDatos.xlsx",
                 [("P13", "si_no"), ("P16", "si_no"), ("P17", "si_no"), ("P23", "aprueba")]),
    "CC873501": ("CC873501_SEMANA11_BaseCodigos.xlsx", "CC873501_SEMANA11_DiccionariodeDatos.xlsx",
                 [("P3", "si_no"), ("P4", "si_no"), ("P19", "aprueba"), ("P28", "acuerdo2"), ("P29", "acuerdo2"), ("P30", "acuerdo2")]),
}
#: DI-BL13: CC873501 no trae fecha ni en la base ni en el diccionario.
ANIO_SUPUESTO = {"CC873501": 2022}
EDAD = {"1": "18-25", "2": "26-40", "3": "41-55", "4": "56+"}


class Lote6Error(RuntimeError):
    """Algo no cuadra con lo pre-registrado en §15."""


def carpeta() -> Path:
    d = os.environ.get("BSS_CNC_POLITICA_DIR")
    if not d or not Path(d).is_dir():
        raise Lote6Error("Falta BSS_CNC_POLITICA_DIR: la carpeta de las encuestas políticas del CNC (D21).")
    return Path(d)


def etiquetas(dicc: Path) -> dict[str, str]:
    """Variable -> etiqueta (la pregunta), de la primera sección del diccionario."""
    df = pd.read_excel(dicc, header=None)
    c0 = df[0].astype(str).str.strip()
    i0 = df.index[c0 == "Variable"][0]
    fin = df.index[(c0 == "Valor") & (df.index > i0)]
    v = df.iloc[i0 + 1:(fin[0] if len(fin) else len(df)), [0, 2]].dropna(subset=[0])
    return {str(a).strip(): " ".join(str(b).split()) for a, b in v.itertuples(index=False)}


def _limpia(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"\((E:|ENTREGAR|LEER)[^)]*\)|\bLEA\b|\bR\.U\.|\(?E: ?LEER[^)]*\)?", "", s)
    s = re.sub(r"^\s*[A-Z]?\d+[a-z]?\.\s*", "", s)
    return " ".join(s.split()).strip(" .")


#: DI-BL14: etiquetas del diccionario cortadas o con erratas; el sentido es el de la pregunta original.
TEXTO_MANUAL = {
    "CC355801_P2_SEM_3": "¿Está de acuerdo con esta medida para apoyar la integración de los migrantes: «Brindar documentos "
                         "legales a todos los migrantes para que puedan trabajar y acceder a servicios, en igualdad de "
                         "condiciones, que los colombianos»?",
    "CC355801_P5_SEM_3": "Luego de que finalice la emergencia sanitaria causada por el coronavirus, ¿estaría de acuerdo con que "
                         "la frontera con Venezuela permanezca cerrada para que no ingresen más migrantes?",
    "CC355801_P5_SEM_7": "¿Está de acuerdo con que «Los migrantes venezolanos son más vulnerables a delitos (son más propensos a "
                         "ser víctimas) cuando están en condición migratoria irregular (no tienen permiso para estar en el país)»?",
    "CC871401_P9": "¿Está usted de acuerdo con el paro?",
    "CC871401_P10": "¿Está usted de acuerdo o en desacuerdo con que el paro continúe?",
    "CC871401_P14": "En su opinión, ¿hay políticos promoviendo el paro?",
    "CC871801_P17": "En su opinión, ¿hubo políticos promoviendo el paro?",
    "CC871801_P23": "¿Usted aprueba o desaprueba la gestión de Iván Duque?",
    "CC873501_P19": "¿Usted aprueba o desaprueba la gestión del presidente Iván Duque?",
}


def texto(estudio: str, var: str, etq: str) -> str:
    """DI-BL10 y DI-BL14."""
    if f"{estudio}_{var}" in TEXTO_MANUAL:
        return TEXTO_MANUAL[f"{estudio}_{var}"]
    if " - " in etq:
        cab, sub = etq.split(" - ", 1)
    else:
        cab, sub = etq, ""
    cab, sub = _limpia(cab), re.sub(r"^\s*[A-Za-z0-9]{1,2}\.?\s+", "", _limpia(sub))
    sub = sub[:1].lower() + sub[1:] if sub else sub
    if var.startswith(("P1_SEM", "P5_SEM")):
        return f"¿Está de acuerdo con que «{sub[:1].upper() + sub[1:]}»?"
    if var.startswith("P4_SEM"):
        return f"¿Está de acuerdo con que «los migrantes {sub}»?"
    if var.startswith("P2_SEM"):
        return f"¿Está de acuerdo con esta medida para apoyar la integración de los migrantes: «{sub[:1].upper() + sub[1:]}»?"
    if var.startswith("T19"):
        return f"¿Está de acuerdo con el papel que han jugado en el paro {sub}?"
    if var.startswith("T24"):
        return f"¿Cree que la presencia de «{sub[:1].upper() + sub[1:]}» es importante para la solución del paro?"
    cab = re.sub(r"^(\d+\.\s*)+", "", cab)
    cab = cab.split("?")[0] + "?" if "?" in cab else cab
    return cab if cab.startswith("¿") else "¿" + cab.lstrip("¿")


def _anio(etq: dict[str, str], est: str) -> int:
    """El año, de la etiqueta de `ESTUDIO` en el diccionario (por ejemplo, «CC355801_SEMANA_FEBRERO_2021»)."""
    if est in ANIO_SUPUESTO:                                                    # DI-BL13
        return ANIO_SUPUESTO[est]
    m = re.findall(r"(20\d\d)", etq.get("ESTUDIO", ""))
    if not m:
        raise Lote6Error(f"{est}: la etiqueta de ESTUDIO no trae el año ({etq.get('ESTUDIO')!r}).")
    return int(m[-1])


def tabla(d: Path | None = None) -> pd.DataFrame:
    d = d or carpeta()
    filas = []
    for est, (base, dicc, vs) in PREGUNTAS.items():
        etq = etiquetas(d / dicc)
        anio = _anio(etq, est)
        for var, esc in vs:
            if var not in etq:
                raise Lote6Error(f"{est} {var} no está en el diccionario.")
            cats, fav = ESCALAS[esc]
            num = re.match(r"[PT](\d+)", var).group(1)
            filas.append({"id": f"{est}_{var}", "familia": f"{est}_P{num}", "ambito": "Bogotá", "fuente": FUENTE, "anio": anio,
                          "variable": var, "independiente": True, "pregunta_pagina": texto(est, var, etq[var]),
                          "codigos_favorables": json.dumps(fav), "categorias": cats, "tema": f"CNC {est}"})
    return pd.DataFrame(filas)


def base_estudio(est: str, d: Path | None = None):
    """(x de una fila del sorteo, peso, grupos, localidad vacía), solo Bogotá (DI-BL11, DI-BL12)."""
    d = d or carpeta()
    base = d / PREGUNTAS[est][0]
    cols = pd.read_excel(base, nrows=0).columns
    edad = next((c for c in ("EDAD", "REDAD") if c in cols), None)
    usar = [v for v, _ in PREGUNTAS[est][2]] + ["DANE", "GENERO", "ESTRATO", "factor"] + ([edad] if edad else [])
    b = pd.read_excel(base, usecols=usar)
    b = b[b.DANE.astype(str).str.replace(r"\.0$", "", regex=True).str.strip() == BOGOTA].reset_index(drop=True)
    num = lambda c: pd.to_numeric(b[c], errors="coerce")                       # noqa: E731
    est_ = num("ESTRATO")
    g = {"sexo": num("GENERO").map({1: "Hombres", 2: "Mujeres"}), "estrato": est_.where(est_.between(1, 6)).map(br.estrato_grupo)}
    if edad:
        g["edad"] = num(edad).astype("Int64").astype(str).map(EDAD)
    loc = pd.Series([None] * len(b), dtype=object)
    return (lambda f: num(f["variable"])), num("factor"), g, loc


def reales(sorteo: pd.DataFrame, d: Path | None = None) -> dict:
    out = {}
    for est in PREGUNTAS:
        s = sorteo[sorteo.id.str.startswith(est + "_")]
        if (s.conjunto == "practica").any():
            r = b3._calcular(s, *base_estudio(est, d))
            for v in r.values():
                v["cortes_edad"] = "18-25, 26-40, 41-55, 56+ (los de la encuesta)" if est != "CC355801" else "sin edad"
            out.update(r)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tabla", action="store_true")
    ap.add_argument("--sorteo", action="store_true")
    ap.add_argument("--reales", action="store_true")
    a = ap.parse_args(argv)
    if a.tabla:
        t = tabla()
        for r in t.itertuples():
            print(f"{r.id:22} {r.familia:16} {r.anio} | {r.pregunta_pagina}")
        print(len(t), "preguntas en", t.familia.nunique(), "familias")
    if a.sorteo:
        if SORTEO.exists():
            raise Lote6Error(f"{SORTEO.name} ya existe: el sorteo se hace una sola vez.")
        s = b3.sortear(tabla(), SEMILLA)
        s.to_csv(SORTEO, index=False, encoding="utf-8")
        print(s.groupby("conjunto").agg(preguntas=("id", "size"), familias=("familia", "nunique")).to_dict())
        print(s.groupby("conjunto").familia.unique().to_dict())
    if a.reales:
        r = reales(pd.read_csv(SORTEO))
        REALES.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        exc = {k: v["excluida"] for k, v in r.items() if v["excluida"]}
        ns = [v["n"] for v in r.values() if not v["excluida"]]
        print(f"{len(r)} de práctica; excluidas por estructura {len(exc)} {exc or ''}; pares claros "
              f"{sum(len(v['pares_claros']) for v in r.values() if not v['excluida'])}; n válidas {min(ns)}-{max(ns)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
