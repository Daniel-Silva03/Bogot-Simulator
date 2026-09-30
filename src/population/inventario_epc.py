"""
src/population/inventario_epc.py

Inventario de las preguntas de la Encuesta de Percepción Ciudadana (Bogotá Cómo
Vamos, 2014-2025): qué pregunta existe en qué año, con cuántas respuestas y con
cuántas personas por localidad. Es el primer paso de la reestructuración de
D17 (población con la persona completa de la EPC, consultas por «puente»).

Uso:
    python src/population/inventario_epc.py

Escribe `data/processed/epc_inventario/items.csv` (una fila por pregunta × año) y
`data/processed/epc_inventario/resumen.csv` (una fila por pregunta).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-IN1. **El diccionario no se cree: se contrasta con el microdato.** Es la regla
    de `DATA_INVENTORY.md` §13.6 (el diccionario de BCV ya invirtió códigos). Para
    cada pregunta y año, el código que dice la EPC Suprema se busca en el `.dta`
    de ese año, sin distinguir mayúsculas. `estado` dice qué pasó: `ok`, `falta`
    (el diccionario da un código que el archivo no tiene) o `sin_codigo` (el
    diccionario dice que ese año no se preguntó).

DI-IN2. **Respuesta válida = valor numérico entre 1 y 10.** Los códigos de «no
    sabe / no responde» de la EPC cambian por año (9, 90, 98, 99) y por pregunta;
    este inventario no los interpreta uno a uno. Contar 1-10 es una cota: sirve
    para saber cuánta información hay, no para calcular proporciones. Las escalas
    reales se fijan pregunta por pregunta cuando una entre al catálogo.

DI-IN3. **Las de respuesta múltiple (RM) se inventarían por prefijo.** Su código
    en el diccionario es la raíz de varias columnas (`CR1_1`, `CR1_2`...). Se
    cuenta cuántas columnas hay y se marca `rm`; no se cuentan respuestas.

DI-IN4. **No se usan los años 2010-2013.** El diccionario los mapea, pero los
    microdatos entregados empiezan en 2014 (§13.6).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.population import epc_bcv as eb                   # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "epc_inventario"
ANIOS = (2014, 2015, 2016, 2017, 2018, 2019, 2022, 2023, 2024, 2025)


def diccionario(raiz=None) -> pd.DataFrame:
    f = eb.resolver_dir_bcv(raiz) / "EPC Suprema.xlsx"
    v = pd.read_excel(f, "VARIABLES", header=1)
    v.columns = [str(c).strip() for c in v.columns]
    mod = next(c for c in v.columns if c.upper().startswith("M") and c.upper().endswith("DULO"))
    grp = next(c for c in v.columns if c.upper().endswith("DULO_GRUPO"))
    v = v.rename(columns={mod: "modulo", grp: "modulo_grupo"})
    return v[v.modulo != "Filtros"].reset_index(drop=True)


def _codigo(x) -> str | None:
    s = str(x).strip()
    return None if s in ("", "-", "nan", "None") else s


def inventariar(raiz=None) -> tuple[pd.DataFrame, pd.DataFrame]:
    dic = diccionario(raiz)
    filas = []
    for anio in ANIOS:
        df = pd.read_stata(eb.archivo_del_anio(anio, raiz), convert_categoricals=False)
        col = {c.upper(): c for c in df.columns}
        loc = eb._columna(df, eb.DEMOGRAFICAS["localidad"][anio])
        for _, d in dic.iterrows():
            cod = _codigo(d.get(f"COD_{anio}"))
            base = {"variable": d.VARIABLE_cod, "anio": anio, "codigo": cod}
            if cod is None:
                filas.append({**base, "estado": "sin_codigo"})
                continue
            if d.Tipo == "RM":                                                   # DI-IN3
                cols = [c for c in df.columns if re.fullmatch(rf"{re.escape(cod)}(_\w+)?", c, re.I)]
                filas.append({**base, "estado": "rm" if cols else "falta", "columnas_rm": len(cols)})
                continue
            real = col.get(cod.upper())
            if real is None:
                filas.append({**base, "estado": "falta"})
                continue
            x = pd.to_numeric(df[real], errors="coerce")
            valida = x.between(1, 10)                                          # DI-IN2
            por_loc = loc[valida].value_counts() if loc is not None else pd.Series(dtype=int)
            por_loc = por_loc[por_loc.index.isin(range(1, 21))]
            filas.append({**base, "estado": "ok", "n": int(len(x)), "n_valido": int(valida.sum()),
                          "valores_distintos": int(x[valida].nunique()),
                          "max_valido": float(x[valida].max()) if valida.any() else np.nan,
                          "localidades": int(len(por_loc)),
                          "n_loc_min": int(por_loc.min()) if len(por_loc) else 0,
                          "n_loc_mediana": float(por_loc.median()) if len(por_loc) else 0.0})
    items = pd.DataFrame(filas)
    ok = items[items.estado == "ok"]
    resumen = dic[["VARIABLE_cod", "VARIABLE_tag", "PREGUNTA_tag", "Tipo", "modulo", "modulo_grupo"]].rename(
        columns={"VARIABLE_cod": "variable", "VARIABLE_tag": "nombre", "PREGUNTA_tag": "pregunta", "Tipo": "tipo"})
    g = ok.groupby("variable")
    resumen = resumen.merge(pd.DataFrame({
        "olas_ok": g.anio.nunique(),
        "anios_ok": g.anio.apply(lambda s: " ".join(map(str, sorted(s)))),
        "n_valido_mediano": g.n_valido.median(),
        "n_loc_mediana": g.n_loc_mediana.median(),
        "escala_max": g.max_valido.max()}).reset_index(), on="variable", how="left")
    falta = items[items.estado == "falta"].groupby("variable").anio.apply(lambda s: " ".join(map(str, sorted(s))))
    resumen["anios_falta_en_archivo"] = resumen.variable.map(falta).fillna("")
    resumen["olas_rm"] = resumen.variable.map(items[items.estado == "rm"].groupby("variable").anio.nunique()).fillna(0).astype(int)
    resumen["olas_ok"] = resumen.olas_ok.fillna(0).astype(int)
    return items, resumen.sort_values(["olas_ok", "modulo"], ascending=[False, True])


def main() -> int:
    items, resumen = inventariar()
    SALIDA.mkdir(parents=True, exist_ok=True)
    items.to_csv(SALIDA / "items.csv", index=False)
    resumen.to_csv(SALIDA / "resumen.csv", index=False)
    ru = resumen[resumen.tipo == "RU"]
    print(f"{len(resumen)} preguntas en el diccionario (sin filtros): {len(ru)} de respuesta única, "
          f"{len(resumen) - len(ru)} múltiple")
    print("olas con datos (respuesta única):", ru.olas_ok.value_counts().sort_index(ascending=False).to_dict())
    print(f"pregunta×año que el diccionario da y el archivo no tiene: {int((items.estado == 'falta').sum())}")
    print(f"\n{SALIDA.relative_to(RAIZ).as_posix()}/items.csv, resumen.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
