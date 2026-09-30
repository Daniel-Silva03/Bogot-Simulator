"""
src/population/armonizar_epc.py

Opción 1 para el mapa (PUENTE_RESULTS.md §7): ¿qué preguntas del catálogo de la
EPC 2023 se pueden juntar con 2022, 2024 y 2025, y cuánto mejora la confiabilidad
de las medias por localidad al juntarlas?

Uso:
    python src/population/armonizar_epc.py

Escribe `data/processed/epc_armonizado/items.csv` (una fila por pregunta) y
`resumen.json`. Solo metadatos, conteos y confiabilidades: ningún microdato.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-AR1. **Un año se puede juntar con 2023 solo si la pregunta es la misma escala
    con las mismas etiquetas.** Se comparan las etiquetas de valor de cada año,
    normalizadas (sin tildes, mayúsculas, números ni puntuación: «1. Muy mala
    gestión» = «Muy mala gestión»), y además los datos no pueden traer códigos
    que las etiquetas no nombran. Si un año no trae etiquetas para la pregunta,
    **no entra**: no hay cómo verificar en el archivo que la escala sea la misma.
    *Corrección (30/09, antes del primer commit):* una primera versión aceptaba
    2025 sin etiquetas si los códigos cabían en la escala y «el texto de la
    pregunta en el diccionario» coincidía. Esa comparación no verificaba nada: el
    diccionario tiene un solo texto por pregunta, no uno por año. El archivo de
    2025 tampoco trae los textos de sus variables, y BCV dijo que el formulario
    cambió en esos años (DATA_INVENTORY §13.7). 2025 queda fuera hasta verificarlo
    contra su formulario en PDF.

DI-AR2. **Los pesos de cada ola se reescalan para sumar su tamaño de muestra**
    antes de juntar: cada ola pesa por las personas que encuestó, no por la
    población a la que expande (2022-2025 expanden todas a ~6 millones, así que
    en la práctica cambia poco, pero deja explícita la regla).
    *Corrección (30/09, después): «cambia poco» es falso dentro de las localidades
    pequeñas.* El `PONDERA` de 2022 casi no varía (DI-B5) y no corrige el
    sobremuestreo: en La Candelaria un encuestado de 2022 pesa 0,99 y uno de 2023,
    0,11, así que en las medias por localidad juntadas domina 2022. La población
    2022-2024 reescala por ola × localidad (`poblacion_epc_olas.py`, DI-PO5). Las
    confiabilidades de `items.csv` no se recalcularon.

DI-AR3. **La confiabilidad es la del paso del puente** (§8 de su pre-registro):
    correlación entre las medias por localidad de dos mitades al azar de los
    encuestados, mediana de 200 repeticiones, en las localidades que existen en
    todas las olas que se juntan (sin La Candelaria si entra 2025). Se reporta
    también la corrección de Spearman-Brown (la confiabilidad de la muestra
    entera).

DI-AR4. **Localidad:** los códigos 1-19 son los del DANE en los cuatro años
    (verificado en las etiquetas de 2022-2024; 2025 no las trae y se verificó
    contra el marginal territorial, `epc_bcv.LOCALIDADES_EPC`). 2025 no tiene La
    Candelaria.

DI-AR5. **Una pregunta que evalúa al gobierno de turno no se junta entre
    administraciones.** La gestión del alcalde (`GG3`) de 2022-2023 es la de
    Claudia López y la de 2024 la de Carlos Fernando Galán; el Concejo también
    cambió en 2024. Juntarlas promediaría dos gobiernos. `GG3`, `CC5A` (gestión
    del Concejo) y `CV5` (inversión de los recursos públicos) solo juntan 2022 y
    2023. Las demás preguntas evalúan la ciudad o la propia vida, no a un
    gobierno, y se juntan en los tres años; el mapa que salga describe «Bogotá
    2022-2024».
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.population import epc_bcv as eb                   # noqa: E402
from src.population import poblacion_epc as pe            # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "epc_armonizado"
INVENTARIO = RAIZ / "data" / "processed" / "epc_inventario" / "items.csv"
BASE = 2023
OTRAS = (2022, 2024, 2025)
#: DI-AR5: evaluaciones del gobierno de turno -> años de la misma administración que 2023
MISMA_ADMINISTRACION = {"GG3": (2022,), "CC5A": (2022,), "CV5": (2022,)}
N_MITADES = 200
SEMILLA = 20260930


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", str(s)).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^A-Za-z ]", " ", s).upper().split())


def _etiquetas_escala(etq: dict, escala: list[int]) -> list[str]:
    return [_norm(etq.get(k, "")) for k in escala]


def cargar_ola(anio: int) -> tuple[pd.DataFrame, dict]:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        d = pd.read_stata(eb.archivo_del_anio(anio), convert_categoricals=False)
    col = {c.upper(): c for c in d.columns}
    w = pd.to_numeric(d[col[eb.FACTOR_POR_ANIO[anio].upper()]], errors="coerce").to_numpy(float)
    out = pd.DataFrame({"anio": anio, "peso": w * len(d) / np.nansum(w),                  # DI-AR2
                        "cod_loc": pd.to_numeric(d[col[eb.DEMOGRAFICAS["localidad"][anio].upper()]], errors="coerce")})
    etq = {k.upper(): v for k, v in pe._etiquetas(eb.archivo_del_anio(anio)).items()}
    for (var, a), (sobra, falta, texto) in pe.CORRECCIONES_ETIQUETAS.items():          # DI-PE7
        if a == anio and var.upper() in etq:
            e = dict(etq[var.upper()]); e.pop(sobra, None); e[falta] = texto
            etq[var.upper()] = e
    return out, {"datos": d, "col": col, "etq": etq}


def compatibilidad(ficha: dict, codigo: str | None, ola: dict, pregunta_2023: str, pregunta_anio: str) -> tuple[bool, str]:
    """DI-AR1: (¿se puede juntar?, por qué)."""
    if codigo is None or codigo.upper() not in ola["col"]:
        return False, "no está en el archivo"
    presentes = set(pd.to_numeric(ola["datos"][ola["col"][codigo.upper()]], errors="coerce").dropna().astype(int))
    esc = ficha["escala"]
    e = ola["etq"].get(codigo.upper())
    if e:
        s = pe.escala_de(e)
        if s is None:
            return False, "sus etiquetas no forman una escala"
        if s[0] != esc:
            return False, f"otra escala ({min(s[0])}-{max(s[0])})"
        if _etiquetas_escala(e, esc) != _etiquetas_escala({int(k): v for k, v in ficha["etiquetas"].items()}, esc):
            return False, "otras etiquetas"
        if presentes - set(e):
            return False, "códigos sin etiqueta"
        return True, "mismas etiquetas"
    return False, "sin etiquetas: no se puede verificar"        # DI-AR1


def confiabilidad(x: np.ndarray, w: np.ndarray, loc: np.ndarray, locs: list[int], rng) -> float:
    """DI-AR3: mediana de la correlación entre medias por localidad de dos mitades."""
    rs = []
    for _ in range(N_MITADES):
        m = rng.random(len(x)) < 0.5
        a = [np.sum(x[m & (loc == l)] * w[m & (loc == l)]) / np.sum(w[m & (loc == l)]) for l in locs]
        b = [np.sum(x[~m & (loc == l)] * w[~m & (loc == l)]) / np.sum(w[~m & (loc == l)]) for l in locs]
        rs.append(np.corrcoef(a, b)[0, 1])
    return float(np.median(rs))


def spearman_brown(r: float) -> float:
    return 2 * r / (1 + r) if r > -1 else float("nan")


def armonizar() -> tuple[pd.DataFrame, dict]:
    inv = pd.read_csv(INVENTARIO)
    dic = pd.read_excel(eb.resolver_dir_bcv() / "EPC Suprema.xlsx", "VARIABLES", header=1).set_index("VARIABLE_cod")
    cat, _ = pe.catalogo()
    olas = {a: cargar_ola(a) for a in (BASE,) + OTRAS}
    rng = np.random.default_rng(SEMILLA)
    filas = []
    for f in cat:
        v, esc = f["variable"], f["escala"]
        compat = {BASE: (True, "base")}
        for a in OTRAS:
            fila = inv[(inv.variable == v) & (inv.anio == a) & (inv.estado == "ok")]
            cod = str(fila.codigo.iloc[0]) if len(fila) else None
            preg_a = str(dic.loc[v, "PREGUNTA_tag"]) if v in dic.index else ""
            compat[a] = compatibilidad(f, cod, olas[a][1], f["pregunta"], preg_a)
            if compat[a][0] and v in MISMA_ADMINISTRACION and a not in MISMA_ADMINISTRACION[v]:
                compat[a] = (False, "otra administración (DI-AR5)")
            compat[a] = (*compat[a], cod)
        anios = [a for a in (BASE,) + OTRAS if compat[a][0]]
        partes = []
        for a in anios:
            base, ola = olas[a]
            cod = f["codigo"] if a == BASE else compat[a][2]
            x = pd.to_numeric(ola["datos"][ola["col"][str(cod).upper()]], errors="coerce").to_numpy(float)
            partes.append(base.assign(x=x))
        j = pd.concat(partes, ignore_index=True)
        j = j[np.isin(j.x, esc) & j.cod_loc.between(1, 19)]
        locs = sorted(set.intersection(*[set(j[j.anio == a].cod_loc.astype(int)) for a in anios]))
        solo = j[j.anio == BASE]
        n_loc = j[j.cod_loc.isin(locs)].groupby("cod_loc").size()
        r23 = confiabilidad(solo.x.to_numpy(), solo.peso.to_numpy(), solo.cod_loc.to_numpy(), locs, rng)
        rjunto = confiabilidad(j.x.to_numpy(), j.peso.to_numpy(), j.cod_loc.to_numpy(), locs, rng) if len(anios) > 1 else r23
        filas.append({"variable": v, "nombre": f["nombre"], "anios": " ".join(map(str, anios)), "olas": len(anios),
                      **{f"motivo_{a}": compat[a][1] for a in OTRAS},
                      "n_2023": int(len(solo)), "n_junto": int(len(j)), "localidades": len(locs),
                      "n_loc_mediana_junto": float(n_loc.median()), "n_loc_min_junto": int(n_loc.min()),
                      "conf_2023": round(r23, 3), "conf_junto": round(rjunto, 3),
                      "conf_2023_sb": round(spearman_brown(r23), 3), "conf_junto_sb": round(spearman_brown(rjunto), 3)})
    items = pd.DataFrame(filas)
    varias = items[items.olas >= 2]
    resumen = {
        "preguntas_catalogo": len(items),
        "por_numero_de_olas": {int(k): int(v) for k, v in items.olas.value_counts().sort_index().items()},
        "motivos_de_exclusion": {str(a): items[f"motivo_{a}"].value_counts().to_dict() for a in OTRAS},
        "con_2_o_mas_olas": {"preguntas": len(varias),
                             "conf_2023_mediana": round(float(varias.conf_2023.median()), 3),
                             "conf_junto_mediana": round(float(varias.conf_junto.median()), 3),
                             "conf_2023_sb_mediana": round(float(varias.conf_2023_sb.median()), 3),
                             "conf_junto_sb_mediana": round(float(varias.conf_junto_sb.median()), 3),
                             "n_loc_mediana": float(varias.n_loc_mediana_junto.median())},
    }
    return items, resumen


def main() -> int:
    items, resumen = armonizar()
    SALIDA.mkdir(parents=True, exist_ok=True)
    items.to_csv(SALIDA / "items.csv", index=False)
    (SALIDA / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False, indent=1))
    print(f"\n{SALIDA.relative_to(RAIZ).as_posix()}/items.csv, resumen.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
