"""
Lotes 3 y 4 del banco de preguntas nuevas (`docs/BANCO_PREGUNTAS_NUEVAS.md` §12 y §13). Sin API.

    Lote 3: Encuesta Bienal de Culturas 2025 (SCRD), 52 familias, 190 preguntas.
    Lote 4: Barrios Vivos 2025 (SCRD), 2 preguntas; no representa a Bogotá.

Uso:
    python src/experiments/banco_lote3.py --sorteo      # sorteo_lote3.csv y sorteo_lote4.csv
    python src/experiments/banco_lote3.py --reales      # resultados reales de las de práctica

Lee solo las copias reducidas de `data/raw/scrd/`, que no traen datos personales (§12, §13).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-BL3. **El texto en la página** de una subpregunta es el enunciado de la pregunta seguido de la
    etiqueta de la subpregunta («Dígame que tanto confía en... — a. El Concejo de Bogotá»). No se
    reescribe a mano: así la lista sale de la documentación de la encuesta y no de una elección.

DI-BL4. **«No sabe»** es lo que `poblacion_epc.NSNR` reconoce en la etiqueta, como en los lotes 1 y 2.
    Lo que no tiene etiqueta en la documentación tampoco cuenta como respuesta válida.

DI-BL5. **Barrios Vivos trae texto en lugar de códigos.** Se codifican sus respuestas con el orden de
    `6_orgullo_ordenado` (a = 1 … e = 5, f = 99) y «Menos de la mitad» = 1, «Más de la mitad» = 2.
    «Sin información» es vacío. El estrato llega como «Estrato 1 »; la edad, en años.

DI-BL6. **La localidad de la Bienal se toma por su código**, que sigue la numeración oficial de 1 a 20
    (se revisó contra sus etiquetas el 5/10); los nombres traen variantes sin tilde («San Cristobal»).
    La edad (`D3`) es la edad en años (13 a 93), y cuadra con los rangos de `D3_1`.
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

BIENAL = RAIZ / "data" / "raw" / "scrd" / "bienal_culturas_2025_reducida.xlsx"
BARRIOS = RAIZ / "data" / "raw" / "scrd" / "barrios_vivos_2025_reducida.xlsx"
SEMILLAS = {3: 20261006, 4: 20261007}

A2, A4, MEDIO = [2], [3, 4], [3]
#: §12: pregunta de la Bienal (indice_pregunta) → códigos favorables.
INCLUIR = {26: A2, 28: A2, 29: A4, 30: [1], 31: [1], 36: A2, 38: A2, 39: A2, 48: A4, 50: A4, 51: A2, 52: A4, 54: A4,
           55: A4, 56: A4, 58: [1], 59: A4, 60: A4, 61: [2], 62: [2], 63: [2], 64: [2], 65: [2], 68: A4, 69: [1],
           70: A4, 75: [1], 77: [1], 79: A4, 80: [1], 83: A2, 85: [1], 86: A4, 87: [1], 88: list(range(6, 11)),
           90: A4, 91: [1], 93: A4, 95: A4, 109: [1], 111: list(range(6, 11)), 112: [1], 113: A4, 124: MEDIO,
           125: MEDIO, 126: A4, 128: A4, 136: A4, 137: A2, 138: A4, 139: A4, 140: [1]}
#: §12, regla 3: subpreguntas que repiten el catálogo, y el resumen de los vecinos.
EXCLUIR_SUB = {"P61.1", "P61.3", "P66.8", "P5.17"}

#: §13: las dos de Barrios Vivos.
BV = [("BV25_P3", "3. ¿En cuántas personas que viven en Bogotá cree que podría confiar?",
       "¿Cree que podría confiar en más de la mitad de las personas que viven en Bogotá?",
       {"Menos de la mitad": 1, "Más de la mitad": 2}, "1=Menos de la mitad; 2=Más de la mitad", [2]),
      ("BV25_P6", "6_orgullo_ordenado", "¿Qué tan orgulloso/a se siente de vivir en su barrio?",
       {"a. Muy orgulloso/a": 1, "b. Orgulloso/a": 2, "c. Indiferente": 3, "d. Poco orgulloso/a": 4,
        "e. Nada orgulloso/a": 5, "f. Ns/Nr": 99},
       "1=Muy orgulloso/a; 2=Orgulloso/a; 3=Indiferente; 4=Poco orgulloso/a; 5=Nada orgulloso/a; 99=Ns/Nr", [1, 2])]
LOCALIDADES = {"USAQUÉN": 1, "CHAPINERO": 2, "SANTA FE": 3, "SAN CRISTÓBAL": 4, "USME": 5, "TUNJUELITO": 6, "BOSA": 7,
               "KENNEDY": 8, "FONTIBÓN": 9, "ENGATIVÁ": 10, "SUBA": 11, "BARRIOS UNIDOS": 12, "TEUSAQUILLO": 13,
               "LOS MÁRTIRES": 14, "ANTONIO NARIÑO": 15, "PUENTE ARANDA": 16, "LA CANDELARIA": 17,
               "RAFAEL URIBE URIBE": 18, "CIUDAD BOLÍVAR": 19, "SUMAPAZ": 20}
COLUMNAS_SORTEO = ["id", "familia", "conjunto", "motivo", "ambito", "fuente", "anio", "variable", "independiente",
                   "pregunta_pagina", "codigos_favorables", "categorias", "tema"]


class Lote3Error(RuntimeError):
    """Algo no cuadra con lo pre-registrado en §12 o §13."""


def _txt(x) -> str:
    return "" if pd.isna(x) else " ".join(str(x).split())


def tabla_bienal(ruta: Path = BIENAL) -> pd.DataFrame:
    """Las preguntas del lote 3 como filas del banco (DI-BL3)."""
    x = pd.ExcelFile(ruta)
    p = x.parse("preguntas").set_index("indice_pregunta")
    v = x.parse("variables")
    e = x.parse("etiquetas_respuestas")
    v = v[v.indice_pregunta.isin(INCLUIR) & ~v.codigo_variable.isin(EXCLUIR_SUB)]
    filas = []
    for r in v.itertuples():
        q = p.loc[r.indice_pregunta]
        sub = _txt(r.etiqueta_enunciado) or _txt(r.enunciado_2)
        texto = _txt(q.enunciado_1) + (f" — {sub}" if sub and len(v[v.indice_pregunta == r.indice_pregunta]) > 1 else "")
        et = e[e.indice_pregunta == r.indice_pregunta]
        cats = "; ".join(f"{int(c)}={_txt(t)}" for c, t in zip(et.codigo_respuesta, et.etiqueta_respuesta))
        filas.append({"id": f"EBC25_{r.codigo_variable}", "familia": f"EBC25_Q{r.indice_pregunta}", "ambito": "Bogotá",
                      "fuente": "SCRD Bienal de Culturas", "anio": 2025, "variable": r.codigo_variable,
                      "independiente": True, "pregunta_pagina": texto,
                      "codigos_favorables": json.dumps(INCLUIR[r.indice_pregunta]), "categorias": cats,
                      "tema": _txt(q.nombre)})
    return pd.DataFrame(filas)


def tabla_barrios() -> pd.DataFrame:
    return pd.DataFrame([{"id": i, "familia": i, "ambito": "Bogotá (no representativa)", "fuente": "SCRD Barrios Vivos",
                          "anio": 2025, "variable": col, "independiente": True, "pregunta_pagina": texto,
                          "codigos_favorables": json.dumps(fav), "categorias": cats, "tema": "orgullo y confianza"}
                         for i, col, texto, _, cats, fav in BV])


def sortear(t: pd.DataFrame, semilla: int) -> pd.DataFrame:
    """Regla 3 de DI-BA5: por familia, la mitad redondeando hacia arriba al guardado."""
    fams = sorted(t.familia.unique())
    orden = list(np.random.default_rng(semilla).permutation(fams))
    guardadas = set(orden[: (len(orden) + 1) // 2])
    t = t.assign(conjunto=np.where(t.familia.isin(guardadas), "guardado", "practica"), motivo="sorteo")
    return t[COLUMNAS_SORTEO].sort_values(["conjunto", "familia", "id"])


def _grupos(sexo, edad, estrato) -> dict:
    return {"sexo": sexo, "edad": br.edad_grupo(edad, en_tramos=False), "estrato": estrato.map(br.estrato_grupo)}


def _calcular(sorteo: pd.DataFrame, x_de, w, grupos, loc) -> dict:
    out = {}
    for f in sorteo[sorteo.conjunto == "practica"].to_dict("records"):
        x = x_de(f)
        cats = br.categorias(f["categorias"])
        fav = json.loads(f["codigos_favorables"])
        res = br.resultado(x, w, grupos, fav, br.validos(cats))
        lres = br.resultado(x, w, {"localidad": loc}, fav, br.validos(cats))
        res["localidad"], res["bases_localidad"] = lres["grupos"]["localidad"], lres["bases"]["localidad"]
        res["cortes_edad"] = "18-25, 26-35, 36-45, 46-55, 56+"
        res["pares_claros"] = br.pares_claros(res)
        res["excluida"] = br.estructura(res)
        out[f["id"]] = {"familia": f["familia"], "ambito": f["ambito"], "fuente": f["fuente"], "anio": int(f["anio"]),
                        "pregunta_pagina": f["pregunta_pagina"], **res}
    return out


def _variable(v: pd.DataFrame, nombre: str) -> str:
    """El código de columna de una variable sociodemográfica de la Bienal, por su `variable_nombre` o `titulo`."""
    m = v[(v.variable_nombre.astype(str) == nombre) | (v.titulo.astype(str) == nombre)]
    if len(m) != 1:
        raise Lote3Error(f"No encuentro una sola variable «{nombre}» ({len(m)}).")
    return m.codigo_variable.iloc[0]


def reales_bienal(sorteo: pd.DataFrame, ruta: Path = BIENAL) -> dict:
    x = pd.ExcelFile(ruta)
    d, v, e = x.parse("datos"), x.parse("variables"), x.parse("etiquetas_respuestas")
    p = x.parse("preguntas").set_index("indice_pregunta")
    soc = {}
    for n in ("Sexo", "Edad", "Estrato", "Localidad", "Factor"):
        idx = p.index[p.nombre.astype(str) == n]
        if len(idx) != 1:
            raise Lote3Error(f"No encuentro una sola pregunta «{n}».")
        cod = v.loc[v.indice_pregunta == idx[0], "codigo_variable"]
        if len(cod) != 1:
            raise Lote3Error(f"«{n}» no tiene una sola variable.")
        soc[n] = cod.iloc[0]
    num = lambda c: pd.to_numeric(d[c], errors="coerce")                       # noqa: E731
    etq_sexo = e[e.indice_pregunta == p.index[p.nombre.astype(str) == "Sexo"][0]]
    etq_sexo = dict(zip(etq_sexo.codigo_respuesta, etq_sexo.etiqueta_respuesta.astype(str)))
    sexo = num(soc["Sexo"]).map(lambda c: {"hombre": "Hombres", "mujer": "Mujeres"}.get(str(etq_sexo.get(c, "")).strip().lower()))
    loc = num(soc["Localidad"])                     # DI-BL6: los códigos 1-20 de la Bienal son los oficiales
    loc = loc.where(loc.between(1, 19)).astype("Int64").astype(str).replace("<NA>", None)
    adultos = num(soc["Edad"]) >= 18
    g = {k: s[adultos] for k, s in _grupos(sexo, num(soc["Edad"]), num(soc["Estrato"])).items()}
    return _calcular(sorteo, lambda f: num(f["variable"])[adultos], num(soc["Factor"])[adultos], g, loc[adultos])


def reales_barrios(sorteo: pd.DataFrame, ruta: Path = BARRIOS) -> dict:
    d = pd.read_excel(ruta, sheet_name="base")
    w = pd.to_numeric(d["Fexp"], errors="coerce")
    edad = pd.to_numeric(d["A6. Edad"], errors="coerce")
    ok = (edad >= 18) & w.notna()
    estrato = pd.to_numeric(d["A3. Estrato vivienda de residencia"].astype(str).str.extract(r"(\d)")[0], errors="coerce")
    sexo = d["A4. Sexo"].map({"Hombre": "Hombres", "Mujer": "Mujeres"})
    loc = d["localidad_norm"].map(LOCALIDADES).astype("Int64").astype(str).replace("<NA>", None)
    cod = {i: (col, mapa) for i, col, _, mapa, _, _ in BV}
    g = {k: s[ok] for k, s in _grupos(sexo, edad, estrato).items()}
    return _calcular(sorteo, lambda f: d[cod[f["id"]][0]].map(cod[f["id"]][1])[ok], w[ok], g, loc[ok])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sorteo", action="store_true")
    ap.add_argument("--reales", action="store_true")
    a = ap.parse_args(argv)
    lotes = {3: tabla_bienal, 4: tabla_barrios}
    if a.sorteo:
        for n, tabla in lotes.items():
            ruta = ba.SALIDA / f"sorteo_lote{n}.csv"
            if ruta.exists():
                raise Lote3Error(f"{ruta.name} ya existe: el sorteo se hace una sola vez.")
            s = sortear(tabla(), SEMILLAS[n])
            s.to_csv(ruta, index=False, encoding="utf-8")
            print(f"lote {n}:", s.groupby("conjunto").agg(preguntas=("id", "size"), familias=("familia", "nunique")).to_dict())
    if a.reales:
        for n, fn in ((3, reales_bienal), (4, reales_barrios)):
            r = fn(pd.read_csv(ba.SALIDA / f"sorteo_lote{n}.csv"))
            (ba.SALIDA / f"reales_practica_lote{n}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
            exc = {k: v["excluida"] for k, v in r.items() if v["excluida"]}
            print(f"lote {n}: {len(r)} de práctica; excluidas por estructura {len(exc)}; pares claros "
                  f"{sum(len(v['pares_claros']) for v in r.values() if not v['excluida'])}; n válidas min-máx "
                  f"{min(v['n'] for v in r.values())}-{max(v['n'] for v in r.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
