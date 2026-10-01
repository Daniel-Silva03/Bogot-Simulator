"""
Resultados reales por grupo de las preguntas de PRÁCTICA del banco
(`docs/BANCO_PREGUNTAS_NUEVAS.md` §8). Solo cálculo local, sin API.

Para cada pregunta: porcentaje ponderado que responde de forma favorable (los
`codigos_favorables` de la clasificación, DI-BA3), en la ciudad y por sexo, edad, estrato y,
si la fuente la trae, localidad; las bases sin ponderar; y los pares de grupos con una
diferencia clara (z > 1,96), como en `preguntas_reales.py`.

**Solo práctica:** lee el banco con `banco.practica()`. Las preguntas guardadas no se calculan:
sus resultados reales tampoco se miran hasta la prueba final.

Uso:
    python src/experiments/banco_reales.py

Escribe `data/processed/banco/reales_practica.json` (solo cifras agregadas).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-BR1. **Respuestas válidas:** las categorías de la pregunta que no son «no sabe», «no
    responde» ni «no aplica» (`poblacion_epc.NSNR` sobre la etiqueta). El porcentaje es sobre
    ellas; las bases cuentan solo personas con respuesta válida.

DI-BR2. **Grupos.** Sexo; edad en los tramos de la población (18-25, 26-35, 36-45, 46-55, 56+;
    en 2017 y 2019 la EPC solo trae esos tramos); estrato 1, 2, 3, 4 y 5-6 (0 no entra);
    localidad 1-19 solo en la EPC (la ECP no la trae). El metro y el Corredor conservan los
    cortes de su encuesta (`preguntas_reales.py`).

DI-BR3. **Pesos:** el factor de cada año de la EPC (`epc_bcv.FACTOR_POR_ANIO`) y `FEX_P` en la
    ECP. Los pares claros usan las bases sin ponderar y sin efecto de diseño, como en
    `PREGUNTAS_REALES_NUEVAS_SPECIFICATION.md` §4.

DI-BR5. **Regla de estructura (1/10, al ver la primera corrida):** una pregunta no entra a la
    práctica si tiene menos de 300 respuestas válidas o si en los datos aparece un solo código
    válido. Hecho: la serie «a quién no quisiera tener de vecino» (`P2041`) registra solo a
    quien marcó la casilla (100 % en todas); «quién debe cuidarlo en la vejez» (`VE3_*`) es de
    respuesta múltiple (bases de 1 a 223); la confianza en la Asamblea y la Gobernación sale
    vacía en Bogotá (`DATA_INVENTORY.md` §10.3). Es una regla de estructura, no de resultado:
    se puede aplicar al banco guardado mirando solo bases y códigos, sin calcular porcentajes.

DI-BR4. **ECP: Bogotá es `REGION == 1`**, y los módulos de participación y capital social se
    unen a la persona por sus cuatro claves (`ecp.CLAVES_PERSONA`); si una unión pierde o
    duplica personas, se detiene.
"""

from __future__ import annotations

import itertools
import json
import math
import re
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import banco as ba                    # noqa: E402

SALIDA = ba.SALIDA / "reales_practica.json"
RAIZ_ECP = RAIZ / "data" / "raw" / "ecp"
TRAMOS = [18, 26, 36, 46, 56, 200]
MIN_VALIDAS = 300
ETQ_TRAMOS = ["18-25", "26-35", "36-45", "46-55", "56+"]
ESTRATOS = ["1", "2", "3", "4", "5-6"]
Z = 1.96


class BancoRealesError(RuntimeError):
    """Algo no cuadra al calcular los resultados reales."""


# --------------------------------------------------------------------------
# Piezas

def categorias(texto: str) -> dict[int, str]:
    return {int(k): v.strip() for k, v in re.findall(r"(-?\d+)=([^;]*)", texto)}


def validos(cats: dict[int, str]) -> list[int]:
    """DI-BR1."""
    from src.population import poblacion_epc as pe
    return [c for c, t in cats.items() if not pe.NSNR.search(t)]


def estrato_grupo(e) -> object:
    if pd.isna(e) or e < 1 or e > 6:
        return None
    return "5-6" if e >= 5 else str(int(e))


def edad_grupo(edad: pd.Series, en_tramos: bool) -> pd.Series:
    if en_tramos:                                    # 2017 y 2019: 1..5 son los mismos tramos
        return edad.map(lambda x: ETQ_TRAMOS[int(x) - 1] if pd.notna(x) and 1 <= x <= 5 else None)
    return pd.cut(edad.astype(float), TRAMOS, right=False, labels=ETQ_TRAMOS).astype(object)


def resultado(x: pd.Series, w: pd.Series, grupos: dict[str, pd.Series], favorables: list[int],
              validas: list[int]) -> dict:
    """Porcentaje favorable ponderado, por grupo, con bases sin ponderar (DI-BR1, DI-BR3)."""
    ok = x.isin(validas) & w.notna() & (w > 0)
    fav = x.isin(favorables).astype(float)

    def pct(m):
        m = m & ok
        return (round(float(100 * np.sum(fav[m] * w[m]) / np.sum(w[m])), 2), int(m.sum())) if m.sum() else (None, 0)

    out = {"total": pct(pd.Series(True, index=x.index))[0], "n": int(ok.sum()), "grupos": {}, "bases": {},
           "codigos_validos_presentes": int(x[ok].nunique())}
    for dim, g in grupos.items():
        orden = {"sexo": ["Hombres", "Mujeres"], "edad": None, "estrato": ESTRATOS}.get(dim)
        etiquetas = orden or sorted(v for v in g.dropna().unique())
        out["grupos"][dim], out["bases"][dim] = {}, {}
        for e in etiquetas:
            p, n = pct(g == e)
            if p is not None:
                out["grupos"][dim][str(e)] = p
                out["bases"][dim][str(e)] = n
    return out


def estructura(res: dict) -> str | None:
    """DI-BR5: por qué la pregunta no sirve por su estructura, o None."""
    if res.get("n", 0) < MIN_VALIDAS:
        return f"menos de {MIN_VALIDAS} respuestas válidas ({res.get('n', 0)})"
    if res.get("codigos_validos_presentes", 2) < 2:
        return "un solo código válido en los datos"
    return None


def pares_claros(res: dict, dims=("sexo", "edad", "estrato")) -> list[tuple[str, str, str]]:
    out = []
    for dim in dims:
        g, b = res["grupos"].get(dim, {}), res["bases"].get(dim, {})
        for a, c in itertools.combinations(g, 2):
            pa, pc = g[a] / 100, g[c] / 100
            se = math.sqrt(pa * (1 - pa) / b[a] + pc * (1 - pc) / b[c]) if b[a] and b[c] else 0
            if se > 0 and abs(pa - pc) / se > Z:
                out.append((dim, a, c) if pa > pc else (dim, c, a))
    return out


# --------------------------------------------------------------------------
# Fuentes

def _epc(anio: int) -> pd.DataFrame:
    from src.population import epc_bcv as eb
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        d = pd.read_stata(eb.archivo_del_anio(anio), convert_categoricals=False)
    d.columns = [c.upper() for c in d.columns]
    num = lambda n: pd.to_numeric(d[eb.DEMOGRAFICAS[n][anio].upper()], errors="coerce")   # noqa: E731
    return pd.DataFrame({
        "w": pd.to_numeric(d[eb.FACTOR_POR_ANIO[anio].upper()], errors="coerce"),
        "sexo": num("sexo").map({1: "Hombres", 2: "Mujeres"}),
        "edad": edad_grupo(num("edad"), en_tramos=anio in (2017, 2019)),
        "estrato": num("estrato").map(estrato_grupo),
        "localidad": num("localidad").where(num("localidad").between(1, 19)).astype("Int64").astype(str).replace("<NA>", None),
    }).join(d.drop(columns=[c for c in ("W",) if c in d.columns]))


def _ecp() -> pd.DataFrame:
    from src.population import ecp
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        panel = ecp.cargar_anio(RAIZ_ECP, 2023)                              # Bogotá, con Democracia
        mods = ecp.localizar_modulos(RAIZ_ECP, 2023)
        for nombre, ruta in (("Participación", mods.participacion), ("Capital social", mods.capital_social)):
            if ruta is None:
                raise BancoRealesError(f"ECP 2023: falta el módulo de {nombre}.")
            t = ecp._canonizar_claves(ecp.leer_tabla(ruta), 2023, nombre)
            t = ecp._sin_fex(t)
            nuevas = [c for c in t.columns if c not in panel.columns]
            n = len(panel)
            panel = panel.merge(t[ecp.CLAVES_PERSONA + nuevas], on=ecp.CLAVES_PERSONA, how="left")
            if len(panel) != n:
                raise BancoRealesError(f"ECP 2023: unir {nombre} cambió el número de personas ({n} → {len(panel)}).")
    edad = pd.to_numeric(panel.edad, errors="coerce")
    out = pd.DataFrame({"w": pd.to_numeric(panel.fex, errors="coerce"),
                        "sexo": pd.to_numeric(panel.sexo, errors="coerce").map({1: "Hombres", 2: "Mujeres"}),
                        "edad": edad_grupo(edad.where(edad >= 18), en_tramos=False),
                        "estrato": pd.to_numeric(panel.estrato, errors="coerce").map(estrato_grupo)})
    return out.join(panel.drop(columns=[c for c in ("w", "sexo", "edad", "estrato") if c in panel.columns]))[edad >= 18].reset_index(drop=True)


def _cnc(id_: str) -> dict:
    from src.experiments import preguntas_reales as pr
    q = {"CNC_METRO": "metro", "CNC_CORREDOR": "corredor"}[id_]
    r = pr.REAL[q]
    res = {"total": r["total"], "n": 4275, "grupos": {d: dict(r[d]) for d in ("sexo", "edad", "estrato")},
           "bases": {d: dict(pr.BASES[d]) for d in ("sexo", "edad", "estrato")},
           "localidad": {str(c): v for c, v in pr.REAL_LOC[q].items()}, "cortes_edad": "18-24, 25-34, 35-54, 55+"}
    return res


# --------------------------------------------------------------------------

def calcular() -> dict:
    p = ba.practica()                                                         # nunca el guardado
    out, datos = {}, {}
    for f in p.to_dict("records"):
        if f["fuente"] == "Biblioteca CNC":
            res = _cnc(f["id"])
        else:
            clave = ("ECP", 2023) if f["fuente"] == "ECP DANE" else ("EPC", int(f["anio"]))
            if clave not in datos:
                datos[clave] = _ecp() if clave[0] == "ECP" else _epc(clave[1])
            d = datos[clave]
            var = str(f["variable"]).upper()
            if var not in d.columns:
                raise BancoRealesError(f"{f['id']}: no está la columna {var}.")
            cats = categorias(f["categorias"])
            fav = json.loads(f["codigos_favorables"])
            x = pd.to_numeric(d[var], errors="coerce")
            dims = {"sexo": d.sexo, "edad": d.edad, "estrato": d.estrato}
            res = resultado(x, d.w, dims, fav, validos(cats))
            if clave[0] == "EPC":
                loc = resultado(x, d.w, {"localidad": d.localidad}, fav, validos(cats))
                res["localidad"] = loc["grupos"]["localidad"]
                res["bases_localidad"] = loc["bases"]["localidad"]
            res["cortes_edad"] = "18-25, 26-35, 36-45, 46-55, 56+"
        res["pares_claros"] = pares_claros(res)
        res["excluida"] = estructura(res)                                         # DI-BR5
        out[f["id"]] = {"familia": f["familia"], "ambito": f["ambito"], "fuente": f["fuente"], "anio": int(f["anio"]),
                        "pregunta_pagina": f["pregunta_pagina"], **res}
    return out


def main() -> int:
    r = calcular()
    SALIDA.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    exc = {k: v["excluida"] for k, v in r.items() if v["excluida"]}
    usa = {k: v for k, v in r.items() if not v["excluida"]}
    n_pares = [len(v["pares_claros"]) for v in usa.values()]
    print(f"{len(r)} preguntas de práctica; excluidas por estructura {len(exc)}; quedan {len(usa)} "
          f"({sum(v['ambito'] == 'Bogotá' for v in usa.values())} de Bogotá)")
    print(f"pares claros: total {sum(n_pares)}, mediana {int(np.median(n_pares))} por pregunta; "
          f"sin ninguno: {sum(1 for x in n_pares if x == 0)}; con localidad: {sum('localidad' in v for v in usa.values())}")
    for k, m in exc.items():
        print(f"   excluida {k}: {m}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
