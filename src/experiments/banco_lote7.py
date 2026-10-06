"""
Séptimo lote del banco: intención de voto de las encuestas del CNC (D21, niveles 2 y 3;
`docs/BANCO_PREGUNTAS_NUEVAS.md` §16). Solo los encuestados de Bogotá. Sin API.

**Es material electoral.** Por D21, nada de este lote se muestra en la página ni entra a las candidatas de la
estimación hasta que lo revise el área jurídica del CNC (`test_banco_lote7` lo verifica). Las bases viven en
`BSS_CNC_POLITICA_DIR` y no se copian al repositorio.

Uso:
    python src/experiments/banco_lote7.py --tabla       # las preguntas y su texto, sin datos
    python src/experiments/banco_lote7.py --sorteo      # escribe sorteo_lote7.csv
    python src/experiments/banco_lote7.py --reales      # resultados reales de las de práctica

DECISIONES DE IMPLEMENTACIÓN
============================

DI-BL17. **Una pregunta del banco por cada opción con nombre** (candidato, fórmula, consulta, coalición o
    tendencia) de cada pregunta de voto. Lo favorable es esa opción. «Otro», el voto en blanco y «ninguno»
    son respuestas válidas que no son esa opción, y NS/NR es «no sabe». La probabilidad de votar (F1) es una
    sola pregunta: favorable, «definitivamente» o «probablemente» sí.
DI-BL18. **Las etiquetas de valor** salen de la sección «Valor/Etiqueta» del diccionario, en la hoja que la
    tenga: en los estudios de 2026 está en una segunda hoja (`Valores_variable`).
DI-BL19. **La fecha del texto** sale del nombre del estudio («mayo de 2021») o, si no lo trae, solo el año.
    El texto empieza siempre por la fecha, porque la intención de voto depende del momento.
DI-BL20. **Las coaliciones de CC873501 P20 se nombran sin sus integrantes.** Hecho: la etiqueta del
    diccionario corta la lista («…Juan Manue»). Se deja el nombre de la coalición («la Coalición de la
    Esperanza»), que es lo que identifica la opción.
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
from src.experiments import banco_lote6 as b6              # noqa: E402
from src.experiments import banco_reales as br             # noqa: E402

SORTEO = ba.SALIDA / "sorteo_lote7.csv"
REALES = ba.SALIDA / "reales_practica_lote7.json"
SEMILLA = 20261011
MIN_LOTE7 = 200
FUERA = re.compile(r"\botro\b|blanco|ningun|ns\s*/\s*nr|^nr$|no votar", re.I)
_seg = lambda a, b: [f"P{i}" for i in range(a, b + 1)]                         # noqa: E731

#: §16 (DI-BL17): estudio -> (base, diccionario, fuente, fecha, {variable: tipo})
ESTUDIOS = {
    "CC871401": ("CC871401_SEMANA_MAYO21_BaseCodigos.xlsx", "CC871401_SEMANA_MAYO21_DiccionariodeDatos.xlsx",
                 "CNC para Semana", "mayo de 2021", {"P1": "primera", **{v: "segunda" for v in _seg(2, 8)}}),
    "CC871801": ("CC871801_SEM_JUN1621_BaseCodigos.xlsx", "CC871801_SEM_JUN1621_DiccionariodeDatos.xlsx",
                 "CNC para Semana", "junio de 2021", {"P2": "primera", **{v: "segunda" for v in _seg(3, 8)}}),
    "CC873501": ("CC873501_SEMANA11_BaseCodigos.xlsx", "CC873501_SEMANA11_DiccionariodeDatos.xlsx",
                 "CNC para Semana", "2022", {"F1": "f1", "P5": "primera", **{v: "segunda" for v in _seg(6, 16)},
                                             "P20": "consulta", "P25": "tendencia"}),
    "CC875701": ("CC875701_SEMANA_Abril2022_BaseCodigos.xlsx", "CC875701_SEMANA_Abril2022_DiccionariodeDatos.xlsx",
                 "CNC para Semana", "abril de 2022", {"F1": "f1", "P1": "primera_votantes", **{v: "segunda" for v in _seg(2, 5)}}),
    "CC891901": ("CC891901_REVISTA_CAMBIO_Enero2026_BaseCodigos.xlsx", "CC891901_REVISTA_CAMBIO_Enero2026_DiccionariodeDatos.xlsx",
                 "CNC para Revista Cambio", "enero de 2026", {"F1": "f1", "P1": "primera", "P3": "consulta", "P4": "consulta_gran",
                                                              "P5": "consulta_pacto", **{v: "escenario" for v in _seg(6, 9)},
                                                              **{v: "segunda" for v in _seg(12, 19)}}),
    "CC892901": ("CC892901_BASE_REVISTA_CAMBIO.csv", "CC892901_DICCIONARIO_BASE_REVISTA_CAMBIO.xlsx",
                 "CNC para Revista Cambio", "2026", {"F1": "f1_marzo", "P1": "precandidato", "P1_CONSULTA": "consulta",
                                                     "P2": "primera", "P3": "nunca", **{v: "segunda" for v in _seg(5, 12)}}),
    "CC893201": ("CC893201_POLITICA_REVISTA_CAMBIO_CODIGOS.xlsx", "CC893201_DICCIONARIO_BASE_POLITICA_CAMBIO_RADICAL.xlsx",
                 "CNC para Revista Cambio", "2026", {"F1": "f1", "P1": "formula", **{v: "segunda" for v in _seg(7, 14)}}),
    "CC893401": ("CC893401_POLITICA_REVISTA_CAMBIO_CODIGOS.xlsx", "CC893401_DICCIONARIO_POLITICA_REVISTA_CAMBIO.xlsx",
                 "CNC para Revista Cambio", "2026", {"F1": "f1", "P1": "formula", "P2": "nunca_formula", **{v: "segunda" for v in _seg(5, 12)}}),
    "CC893701": ("CC893701_BASE_POLITICA_REVISTA_CAMBIO_CODIGOS.xlsx", "CC893701_DICCIONARIO_BASE_POLITICA_REVISTA_CAMBIO.xlsx",
                 "CNC para Revista Cambio", "2026", {"F1": "f1", "P1": "formula", "P2": "nunca_formula", **{v: "segunda" for v in _seg(5, 8)}}),
}
EDAD4 = {"1": "18-25", "2": "26-40", "3": "41-55", "4": "56+"}
EDAD5 = {"1": "18-24", "2": "25-34", "3": "35-44", "4": "45-54", "5": "55+"}


class Lote7Error(RuntimeError):
    """Algo no cuadra con lo pre-registrado en §16."""


def valores(dicc: Path) -> dict[str, dict[int, str]]:
    """DI-BL18: variable -> {código: etiqueta limpia}."""
    out: dict[str, dict[int, str]] = {}
    for hoja in pd.ExcelFile(dicc).sheet_names:
        df = pd.read_excel(dicc, sheet_name=hoja, header=None)
        c0 = df[0].astype(str).str.strip()
        i = df.index[c0 == "Valor"]
        if not len(i):
            continue
        cur = None
        for r in df.iloc[i[0] + 1:].itertuples(index=False):
            if str(r[0]) != "nan":
                cur = str(r[0]).strip()
            if cur and str(r[1]) != "nan":
                try:
                    cod = int(float(r[1]))
                except ValueError:
                    continue
                out.setdefault(cur, {})[cod] = limpia_opcion(str(r[2]))
    return out


def limpia_opcion(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s).replace("\xa0", " ")
    s = re.sub(r"\((E: ?)?NO LEER\)|\(E: ?NO LEER\)", "", s, flags=re.I)
    s = re.sub(r"^\s*([a-z]\)|\d+\.)\s*", "", s)
    s = " ".join(s.replace(";", ",").split()).strip(" –-")
    s = re.sub(r"^Por (la|el) ", r"\1 ", s)                                    # «Por la Coalición…» -> «la Coalición…»
    s = re.sub(r" conformad[oa] por .*$", "", s)                               # DI-BL20: etiquetas cortadas
    return re.sub(r"\bfajardo\b", "Fajardo", s)                                # errata del diccionario


def texto(tipo: str, fecha: str, op: str, ops: list[str]) -> str:
    f = f"En {fecha}" if not fecha.isdigit() else f"En la encuesta de {fecha}"
    return {
        "f1": f"{f}: si las elecciones presidenciales fueran el próximo domingo, ¿votaría (definitiva o probablemente)?",
        "f1_marzo": f"{f}: ¿votaría (definitiva o probablemente) en las elecciones de Congreso y las consultas del 8 de marzo?",
        "primera": f"{f}: si las elecciones presidenciales fueran mañana, ¿votaría por {op}?",
        "primera_votantes": f"{f}, entre quienes piensan votar: si las elecciones presidenciales fueran mañana, ¿votaría por {op}?",
        "formula": f"{f}: ¿votaría por la fórmula presidencial {op}?",
        "nunca": f"{f}: ¿nunca votaría por {op}?",
        "nunca_formula": f"{f}: ¿nunca votaría por la fórmula presidencial {op}?",
        "segunda": f"{f}: en una segunda vuelta entre {' y '.join(ops)}, ¿votaría por {op}?",
        "escenario": f"{f}: si en la primera vuelta se presentan {', '.join(ops[:-1])} y {ops[-1]}, ¿votaría por {op}?",
        "consulta": f"{f}: en las consultas interpartidistas, ¿votaría por {op if op.startswith(('la ', 'el ')) else '«' + op + '»'}?",
        "consulta_gran": f"{f}: en la Gran Consulta por Colombia, ¿votaría por {op}?",
        "consulta_pacto": f"{f}: en la consulta del Pacto Amplio, ¿votaría por {op}?",
        "precandidato": f"{f}: en las consultas interpartidistas, ¿votaría por {op}?",
        "tendencia": f"{f}: ¿votaría por un candidato de {op.lower()}?",
    }[tipo]


def tabla(d: Path | None = None) -> pd.DataFrame:
    d = d or b6.carpeta()
    filas = []
    for est, (base, dicc, fuente, fecha, vs) in ESTUDIOS.items():
        val = valores(d / dicc)
        anio = int(re.findall(r"20\d\d", fecha)[-1])
        for var, tipo in vs.items():
            if var not in val:
                raise Lote7Error(f"{est} {var} no tiene etiquetas de valor.")
            cats = val[var]
            nombres = [(c, e) for c, e in sorted(cats.items()) if not FUERA.search(e)]
            cat_txt = "; ".join(f"{c}={e}" for c, e in sorted(cats.items()))
            if tipo.startswith("f1"):
                items = [("votaria", [1, 2], None)]
            else:
                items = [(str(c), [c], e) for c, e in nombres]
            for suf, fav, op in items:
                filas.append({"id": f"{est}_{var}_{suf}", "familia": f"{est}_{var}", "ambito": "Bogotá", "fuente": fuente,
                              "anio": anio, "variable": var, "independiente": True,
                              "pregunta_pagina": texto(tipo, fecha, op or "", [e for _, e in nombres]),
                              "codigos_favorables": json.dumps(fav), "categorias": cat_txt, "tema": f"electoral {est}"})
    return pd.DataFrame(filas)


def base_estudio(est: str, d: Path | None = None):
    """(x de una fila del sorteo, peso, grupos, localidad vacía), solo Bogotá."""
    d = d or b6.carpeta()
    base = d / ESTUDIOS[est][0]
    leer = (lambda **k: pd.read_csv(base, encoding="latin-1", sep=None, engine="python", **k)) if base.suffix == ".csv" \
        else (lambda **k: pd.read_excel(base, **k))
    cols = list(leer(nrows=0).columns)
    peso = "FACTOR" if "FACTOR" in cols else "factor"
    edad = "REDAD" if "REDAD" in cols else "EDAD"
    usar = list(ESTUDIOS[est][4]) + ["DANE", "GENERO", "ESTRATO", peso, edad]
    b = leer(usecols=usar)
    b = b[b.DANE.astype(str).str.replace(r"\.0$", "", regex=True).str.strip() == b6.BOGOTA].reset_index(drop=True)
    num = lambda c: pd.to_numeric(b[c], errors="coerce")                       # noqa: E731
    e = num("ESTRATO")
    mapa = EDAD5 if int(re.findall(r"20\d\d", ESTUDIOS[est][3])[-1]) >= 2026 else EDAD4
    g = {"sexo": num("GENERO").map({1: "Hombres", 2: "Mujeres"}), "estrato": e.where(e.between(1, 6)).map(br.estrato_grupo),
         "edad": num(edad).astype("Int64").astype(str).map(mapa)}
    return (lambda f: num(f["variable"])), num(peso), g, pd.Series([None] * len(b), dtype=object)


def reales(sorteo: pd.DataFrame, d: Path | None = None) -> dict:
    out = {}
    for est in ESTUDIOS:
        s = sorteo[sorteo.id.str.startswith(est + "_")]
        if (s.conjunto == "practica").any():
            r = b3._calcular(s, *base_estudio(est, d))
            for v in r.values():
                if v["excluida"] and v["excluida"].startswith(f"menos de {br.MIN_VALIDAS}") and v["n"] >= MIN_LOTE7:
                    v["excluida"], v["bajo_300"] = None, True
                v["cortes_edad"] = "los de la encuesta"
                v["electoral"] = True
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
            print(f"{r.id:26} {r.codigos_favorables:7} | {r.pregunta_pagina}")
        print(len(t), "preguntas en", t.familia.nunique(), "familias;", t.groupby("tema").size().to_dict())
    if a.sorteo:
        if SORTEO.exists():
            raise Lote7Error(f"{SORTEO.name} ya existe: el sorteo se hace una sola vez.")
        s = b3.sortear(tabla(), SEMILLA)
        s.to_csv(SORTEO, index=False, encoding="utf-8")
        print(s.groupby("conjunto").agg(preguntas=("id", "size"), familias=("familia", "nunique")).to_dict())
    if a.reales:
        r = reales(pd.read_csv(SORTEO))
        REALES.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        exc = {k: v["excluida"] for k, v in r.items() if v["excluida"]}
        ns = [v["n"] for v in r.values() if not v["excluida"]]
        print(f"{len(r)} de práctica; excluidas por estructura {len(exc)} {exc or ''}; n válidas {min(ns)}-{max(ns)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
