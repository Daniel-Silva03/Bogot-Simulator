"""
src/population/poblacion_epc.py

Población EPC 2023 (D17, pieza 1): cada agente hereda a una persona real de la
Encuesta de Percepción Ciudadana 2023, emparejada **dentro de su localidad**, y
con ella todas sus respuestas. Especificación: `docs/POBLACION_EPC2023_SPECIFICATION.md`.

Uso:
    python src/population/poblacion_epc.py              # construye y verifica
    python src/population/poblacion_epc.py --n 20000 --semilla 20260930

Escribe en `data/processed/poblacion_epc2023/`:
    agentes.parquet (o .csv)   un agente por fila, con el identificador de su donante
    catalogo.json              las preguntas que la población puede responder, con su escala
    verificacion.json          §6 de la especificación
    metadata.json

DECISIONES DE IMPLEMENTACIÓN
============================

DI-PE1. **Educación en cuatro niveles, no los de §3.1 de la especificación.**
    Hecho: el receptor (Multipropósito) junta secundaria y media en un mismo
    código (`nivel_educativo` = 2), así que la separación «básica / media» que
    escribió la especificación no se puede hacer del lado del receptor.
    Decisión: 0 = primaria o menos (receptor 0-1; EPC 1-3), 1 = secundaria o media
    (receptor 2; EPC 4-5), 2 = técnica o tecnológica (receptor 3; EPC 8),
    3 = universitaria o posgrado (receptor 4-5; EPC 6 y 9). `CS4 = 0` («no sabe»)
    son 2 de 1.501 donantes: quedan fuera del grupo de donantes y se dice.

DI-PE2. **Se empareja localidad por localidad.** La escalera de
    `hot_deck_match` suelta primero la última variable exacta y termina sin
    ninguna: con la localidad en la lista, el último escalón la soltaría. Se
    llama una vez por localidad, con el sexo como único bloque exacto y la
    distancia sobre tramo de edad, estrato y educación. Así la localidad no se
    suelta nunca (§3 de la especificación), y la «escalera» de §3.3 la hace el
    vecino más cercano: cada agente registra si quedó a distancia 0 de su
    donante (las cuatro variables iguales) o no.

DI-PE3. **Lo que se copia es el identificador del donante**, no sus respuestas
    (§3.5). `hot_deck_match` copia una columna: se le pasa `donante_id`.

DI-PE4. **La escala de cada pregunta sale de las etiquetas de valor del
    archivo de 2023**, no del diccionario (§4). Códigos cuyas etiquetas dicen
    «no sabe», «no responde» o «no aplica» son no respuesta; el resto, entre 1
    y 10, es la escala, y tiene que ser contigua desde 1. Si no, la pregunta
    queda fuera, con su razón.

DI-PE5. **Margen de la encuesta por bootstrap de conglomerados dentro de cada
    localidad** (§5): se remuestrean manzanas (localidad × manzana, DI-D7) con
    reemplazo dentro de cada localidad, 200 veces.

DI-PE6. **1.000 agentes por localidad, no 20.000 repartidos según la población**
    (cambia §3.1 de la especificación). Hecho, en la primera construcción: con el
    reparto proporcional La Candelaria recibía 40 agentes y Sumapaz 8, y la
    demografía de La Candelaria se desviaba hasta 16 puntos de la del receptor
    por puro sorteo. Un mapa por localidad necesita el mismo detalle en todas.
    Decisión: 1.000 por localidad (20.000 en total), cada uno por PPS dentro de su
    localidad, y cada agente con `peso` = población adulta de su localidad /
    1.000, para que las cifras de la ciudad no sobrerrepresenten a las pequeñas.

DI-PE7. **Las etiquetas del archivo también se verifican contra los datos.**
    Hecho: en 2023, `GG3` (gestión del alcalde) etiqueta «Muy buena gestión» con
    el código 6 y no tiene 5; los datos usan 1-5, y 2022 y 2024 etiquetan el 5.
    Es el tercer error de documentación de BCV (después de la inversión de
    códigos y el diccionario de §13.8). Se corrige en `CORRECCIONES_ETIQUETAS`,
    y el código comprueba que los datos tengan el código corregido y no el
    original. Además, una pregunta cuyos datos traigan códigos que sus
    etiquetas no nombran queda fuera del catálogo.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.population import epc_bcv as eb                   # noqa: E402
from src.population.matching import hot_deck_match          # noqa: E402
from src.population.muestreo import muestrear               # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "poblacion_epc2023"
INVENTARIO = RAIZ / "data" / "processed" / "epc_inventario" / "items.csv"
MARGINAL = RAIZ / "data" / "external" / "marginal_localidad_18mas.csv"
RECEPTOR = RAIZ / "data" / "raw" / "em2021_receptor_v2.csv"
ANIO = 2023
SUMAPAZ = 20
N_POR_DEFECTO = 20_000                                          # 1.000 × 20 localidades
SEMILLA = 20260930
UMBRAL_RESPUESTA = 0.80
N_BOOT = 200
EXCLUIDAS = re.compile(r"^(GG1|GP1_.*)$", re.I)                 # imagen: DI-B2
NSNR = re.compile(r"no\s*sabe|no\s*respond|no\s*aplica|ns\s*/?\s*nr|no\s*informa|no\s*contesta", re.I)
TRAMOS_EDAD = [18, 26, 36, 46, 56, 200]                          # los de CS2A
EDU_RECEPTOR = {0: 0, 1: 0, 2: 1, 3: 2, 4: 3, 5: 3}              # DI-PE1
EDU_EPC = {1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 8: 2, 6: 3, 9: 3}
VARS_DISTANCIA = ["edad_tramo", "estrato", "educ_h"]
N_POR_LOCALIDAD = 1_000                                          # DI-PE6
#: DI-PE7: (variable, año) -> (código que sobra en la etiqueta, código que falta, texto)
CORRECCIONES_ETIQUETAS = {("GG3", 2023): (6, 5, "Muy buena gestión")}


class PoblacionError(RuntimeError):
    """Algo no cuadra en la construcción de la población EPC."""


def _norm(s) -> str:
    import unicodedata
    s = unicodedata.normalize("NFD", str(s)).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^A-Za-z ]", " ", s).upper().split())


def tramo_edad(edad) -> pd.Series:
    return pd.cut(pd.Series(edad, dtype=float), TRAMOS_EDAD, right=False, labels=False).astype("Int64")


# --------------------------------------------------------------------------
# Donante y receptor

def cargar_donante(raiz=None) -> pd.DataFrame:
    """EPC 2023 completa, con las columnas de emparejamiento armonizadas."""
    d = pd.read_stata(eb.archivo_del_anio(ANIO, raiz), convert_categoricals=False)
    d = d.reset_index(drop=True)
    d["donante_id"] = np.arange(len(d))
    d["cod_loc"] = pd.to_numeric(d.CS0A, errors="coerce").astype("Int64")
    d["sexo"] = pd.to_numeric(d.CS1, errors="coerce").map({1: "M", 2: "F"})
    d["edad_tramo"] = tramo_edad(pd.to_numeric(d.CS2, errors="coerce"))
    d["estrato"] = pd.to_numeric(d.CS21, errors="coerce")
    d["educ_h"] = pd.to_numeric(d.CS4, errors="coerce").map(EDU_EPC)
    d["peso"] = pd.to_numeric(d.FEXP, errors="coerce")
    d["conglomerado"] = d.cod_loc.astype(str) + "|" + d.Manzana.astype(str)      # DI-D7
    return d


def cargar_receptor(ruta: Path = RECEPTOR) -> pd.DataFrame:
    from src.population.loader import load_multiproposito_receptor
    logging.disable(logging.WARNING)
    r = load_multiproposito_receptor(ruta)
    logging.disable(logging.NOTSET)
    codigo = {_norm(n): int(c) for c, n in pd.read_csv(MARGINAL).set_index("COD_LOC").localidad.items()}
    r["cod_loc"] = r.localidad.map(lambda n: codigo.get(_norm(n)))
    if r.cod_loc.isna().any():
        raise PoblacionError(f"Localidades del receptor sin código: {sorted(r[r.cod_loc.isna()].localidad.unique())}")
    r["cod_loc"] = r.cod_loc.astype(int)
    r["edad_tramo"] = tramo_edad(r.edad)
    r["educ_h"] = r.nivel_educativo.map(EDU_RECEPTOR)
    return r


# --------------------------------------------------------------------------
# Construcción

def emparejar(agentes: pd.DataFrame, donante: pd.DataFrame, semilla: int) -> pd.DataFrame:
    """DI-PE2: hot-deck localidad por localidad. Sumapaz (sin donantes) queda sin donante."""
    don = donante.dropna(subset=["cod_loc", "sexo", "edad_tramo", "estrato", "educ_h", "peso"])
    partes = []
    for loc, a in agentes.groupby("cod_loc", sort=True):
        d = don[don.cod_loc == loc]
        if d.empty:
            partes.append(a.assign(donante_id=pd.NA))
            continue
        m = hot_deck_match(a[["agent_id", "sexo"] + VARS_DISTANCIA].astype({"edad_tramo": float}),
                           d[["donante_id", "sexo", "peso"] + VARS_DISTANCIA].astype({"edad_tramo": float}),
                           opinion_col="donante_id", exact_match_vars=["sexo"],
                           distance_vars=VARS_DISTANCIA, random_state=semilla + int(loc), peso_col="peso")
        partes.append(a.assign(donante_id=m.agentes["donante_id"].to_numpy()))
    out = pd.concat(partes).sort_values("agent_id").reset_index(drop=True)
    out["donante_id"] = out.donante_id.astype("Int64")
    # ¿Quedó a distancia 0? (las cuatro variables iguales a las de su donante)
    dd = donante.set_index("donante_id")
    con = out.donante_id.notna()
    igual = pd.Series(False, index=out.index)
    ref = dd.loc[out.loc[con, "donante_id"].astype(int)]
    igual[con] = ((out.loc[con, "sexo"].to_numpy() == ref.sexo.to_numpy())
                  & (out.loc[con, "edad_tramo"].astype(float).to_numpy() == ref.edad_tramo.astype(float).to_numpy())
                  & (out.loc[con, "estrato"].to_numpy() == ref.estrato.to_numpy())
                  & (out.loc[con, "educ_h"].to_numpy() == ref.educ_h.to_numpy()))
    out["emparejamiento_exacto"] = igual
    if (dd.loc[out.loc[con, "donante_id"].astype(int), "cod_loc"].to_numpy() != out.loc[con, "cod_loc"].to_numpy()).any():
        raise PoblacionError("Un agente heredó a un donante de otra localidad (viola §3).")
    return out


def construir(n_por_localidad: int = N_POR_LOCALIDAD, semilla: int = SEMILLA, receptor=None,
              donante=None) -> pd.DataFrame:
    """DI-PE6: el mismo número de agentes en cada localidad, con su peso."""
    receptor = cargar_receptor() if receptor is None else receptor
    donante = cargar_donante() if donante is None else donante
    partes = []
    for loc, r in receptor.groupby("cod_loc", sort=True):
        m = muestrear(r, n_por_localidad, seed=semilla + int(loc), metodo="ponderado").agentes
        partes.append(m.assign(peso=float(r.factor_expansion.sum()) / n_por_localidad))
    muestra = pd.concat(partes, ignore_index=True)
    muestra["agent_id"] = np.arange(len(muestra))
    cols = ["agent_id", "cod_loc", "localidad", "sexo", "edad", "edad_tramo", "estrato", "educ_h", "peso"]
    return emparejar(muestra[cols], donante, semilla)


# --------------------------------------------------------------------------
# Catálogo (§4)

def _etiquetas(ruta: Path) -> dict[str, dict[int, str]]:
    """Etiquetas de valor por variable, leídas del .dta (DI-PE4)."""
    with pd.io.stata.StataReader(ruta) as r:
        r.read(nrows=1)
        por_nombre = r.value_labels()
        lbl = dict(zip(r._varlist, r._lbllist))          # variable -> nombre de su etiqueta
    return {v: {int(k): str(t) for k, t in por_nombre[l].items()} for v, l in lbl.items() if l in por_nombre}


def escala_de(etq: dict[int, str]) -> tuple[list[int], list[int]] | None:
    """(códigos de la escala, códigos de no respuesta), o None si no es una escala 1..k."""
    nsnr = sorted(k for k, t in etq.items() if NSNR.search(t))
    escala = sorted(k for k in etq if k not in nsnr and 1 <= k <= 10)
    if len(escala) < 2 or escala != list(range(1, len(escala) + 1)):
        return None
    return escala, nsnr


def catalogo(raiz=None) -> tuple[list[dict], list[dict]]:
    """(preguntas que entran, preguntas que quedan fuera con su razón)."""
    inv = pd.read_csv(INVENTARIO)
    inv = inv[(inv.anio == ANIO) & (inv.estado == "ok") & (inv.n_valido >= UMBRAL_RESPUESTA * inv.n)]
    dic = pd.read_excel(eb.resolver_dir_bcv(raiz) / "EPC Suprema.xlsx", "VARIABLES", header=1)
    dic = dic.set_index("VARIABLE_cod")
    etq = _etiquetas(eb.archivo_del_anio(ANIO, raiz))
    etq_up = {k.upper(): v for k, v in etq.items()}
    datos = pd.read_stata(eb.archivo_del_anio(ANIO, raiz), convert_categoricals=False)
    col = {c.upper(): c for c in datos.columns}
    for (var, anio), (sobra, falta, texto) in CORRECCIONES_ETIQUETAS.items():   # DI-PE7
        if anio != ANIO or var.upper() not in etq_up:
            continue
        presentes = set(pd.to_numeric(datos[col[var.upper()]], errors="coerce").dropna().astype(int))
        if falta not in presentes or sobra in presentes:
            raise PoblacionError(f"La corrección de etiquetas de {var} {anio} ya no corresponde a los datos: {sorted(presentes)}")
        e = dict(etq_up[var.upper()]); e.pop(sobra, None); e[falta] = texto
        etq_up[var.upper()] = e
    dentro, fuera = [], []
    for _, it in inv.iterrows():
        base = {"variable": it.variable, "codigo": it.codigo,
                "nombre": str(dic.loc[it.variable, "VARIABLE_tag"]), "pregunta": str(dic.loc[it.variable, "PREGUNTA_tag"])}
        if dic.loc[it.variable, "Tipo"] != "RU":
            fuera.append({**base, "razon": "no es de respuesta única"})
        elif EXCLUIDAS.match(str(it.variable)):
            fuera.append({**base, "razon": "imagen: códigos invertidos en 2023 (DI-B2)"})
        elif str(it.codigo).upper() not in etq_up:
            fuera.append({**base, "razon": "sin etiquetas de valor en el archivo"})
        else:
            e = etq_up[str(it.codigo).upper()]
            s = escala_de(e)
            presentes = set(pd.to_numeric(datos[col[str(it.codigo).upper()]], errors="coerce").dropna().astype(int))
            if s is None:
                fuera.append({**base, "razon": "las etiquetas no forman una escala 1..k"})
            elif presentes - set(e):
                fuera.append({**base, "razon": f"los datos traen códigos sin etiqueta: {sorted(presentes - set(e))}"})
            else:
                dentro.append({**base, "escala": s[0], "no_respuesta": s[1],
                               "etiquetas": {str(k): v for k, v in sorted(e.items())}})
    return dentro, fuera


# --------------------------------------------------------------------------
# Verificación (§6)

def _medias_ponderadas(X: np.ndarray, validos: np.ndarray, w: np.ndarray) -> np.ndarray:
    ww = validos * w[:, None]
    return np.nansum(np.where(validos, X, 0) * ww, axis=0) / ww.sum(axis=0)


def verificar(agentes: pd.DataFrame, donante: pd.DataFrame, cat: list[dict], receptor: pd.DataFrame,
              n_boot: int = N_BOOT, semilla: int = SEMILLA) -> dict:
    rng = np.random.default_rng(semilla)
    col = {c.upper(): c for c in donante.columns}
    X = np.column_stack([pd.to_numeric(donante[col[str(c["codigo"]).upper()]], errors="coerce").to_numpy(float)
                         for c in cat])
    validos = np.column_stack([np.isin(X[:, j], c["escala"]) for j, c in enumerate(cat)])
    w = donante.peso.to_numpy(float)
    loc_d = donante.cod_loc.to_numpy()
    locs = sorted(int(x) for x in pd.unique(agentes.cod_loc) if x != SUMAPAZ and (loc_d == x).any())

    # 1. Demografía: agentes contra el receptor ponderado, por localidad
    dif_demo = {}
    for v in ["sexo", "edad_tramo", "estrato", "educ_h"]:
        peor = 0.0
        for l in locs:
            a = agentes[agentes.cod_loc == l][v].value_counts(normalize=True)
            rr = receptor[receptor.cod_loc == l]
            r_ = rr.groupby(v).factor_expansion.sum() / rr.factor_expansion.sum()
            peor = max(peor, float((a.reindex(r_.index, fill_value=0) - r_).abs().max()))
        dif_demo[v] = round(peor, 4)

    # 2. Opinión: media de los agentes contra la media ponderada de la EPC, con margen
    idx = agentes.donante_id.dropna().astype(int).to_numpy()
    loc_a = agentes.loc[agentes.donante_id.notna(), "cod_loc"].to_numpy()
    fuera_margen, total, detalle = 0, 0, []
    conglo = donante.conglomerado.to_numpy()
    grupos = {l: pd.factorize(conglo[loc_d == l])[0] for l in locs}
    for l in locs:
        m_d = loc_d == l
        Xl, Vl, wl = X[m_d], validos[m_d], w[m_d]
        g = grupos[l]; k = g.max() + 1
        boot = np.empty((n_boot, X.shape[1]))
        for b in range(n_boot):
            mult = np.bincount(rng.integers(0, k, k), minlength=k)[g]
            boot[b] = _medias_ponderadas(Xl, Vl, wl * mult)
        lo, hi = np.nanpercentile(boot, 2.5, axis=0), np.nanpercentile(boot, 97.5, axis=0)
        Xa, Va = X[idx[loc_a == l]], validos[idx[loc_a == l]]
        med_a = _medias_ponderadas(Xa, Va, np.ones(len(Xa)))
        fuera = (med_a < lo) | (med_a > hi)
        fuera_margen += int(np.nansum(fuera)); total += int(np.isfinite(med_a).sum())
        for j, c in enumerate(cat):
            if fuera[j]:
                detalle.append({"variable": c["variable"], "cod_loc": l, "agentes": round(float(med_a[j]), 3),
                                "margen": [round(float(lo[j]), 3), round(float(hi[j]), 3)]})
    # ciudad
    pa = agentes.loc[agentes.donante_id.notna(), "peso"].to_numpy(float)          # DI-PE6
    med_ciudad_a = _medias_ponderadas(X[idx], validos[idx], pa)
    med_ciudad_d = _medias_ponderadas(X, validos, w)
    exacto = agentes[agentes.donante_id.notna()].groupby("cod_loc").emparejamiento_exacto.mean()
    return {
        "demografia_peor_diferencia_por_localidad": dif_demo,
        "opinion": {"pares_pregunta_localidad": total, "fuera_del_margen_95": fuera_margen,
                    "fraccion_fuera": round(fuera_margen / total, 4), "umbral": 0.10,
                    "pasa": bool(fuera_margen / total <= 0.10), "detalle_fuera": detalle,
                    "ciudad_max_dif_media": round(float(np.nanmax(np.abs(med_ciudad_a - med_ciudad_d))), 4)},
        "emparejamiento_exacto_por_localidad": {int(k): round(float(v), 3) for k, v in exacto.items()},
        "emparejamiento_exacto_total": round(float(agentes.loc[agentes.donante_id.notna(), "emparejamiento_exacto"].mean()), 4),
        "sin_donante": {"agentes": int(agentes.donante_id.isna().sum()),
                        "localidades": sorted(int(x) for x in agentes.loc[agentes.donante_id.isna(), "cod_loc"].unique())},
        "n_boot": n_boot,
    }


# --------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Población EPC 2023 (D17).")
    ap.add_argument("--n", type=int, default=N_POR_LOCALIDAD, help="agentes por localidad")
    ap.add_argument("--semilla", type=int, default=SEMILLA)
    args = ap.parse_args(argv)
    receptor, donante = cargar_receptor(), cargar_donante()
    agentes = construir(args.n, args.semilla, receptor, donante)
    otra = construir(args.n, args.semilla, receptor, donante)                     # §6.4
    reproducible = bool(agentes.equals(otra))
    dentro, fuera = catalogo()
    ver = verificar(agentes, donante, dentro, receptor)
    ver["reproducible_misma_semilla"] = reproducible
    SALIDA.mkdir(parents=True, exist_ok=True)
    try:
        agentes.to_parquet(SALIDA / "agentes.parquet", index=False); archivo = "agentes.parquet"
    except ImportError:
        agentes.to_csv(SALIDA / "agentes.csv", index=False); archivo = "agentes.csv"
    (SALIDA / "catalogo.json").write_text(json.dumps({"dentro": dentro, "fuera": fuera}, ensure_ascii=False, indent=1), encoding="utf-8")
    (SALIDA / "verificacion.json").write_text(json.dumps(ver, ensure_ascii=False, indent=1), encoding="utf-8")
    (SALIDA / "metadata.json").write_text(json.dumps({
        "generado": date.today().isoformat(), "especificacion": "docs/POBLACION_EPC2023_SPECIFICATION.md",
        "donante": f"EPC {ANIO} (Bogotá Cómo Vamos)", "receptor": "Multipropósito 2021",
        "n_agentes": len(agentes), "semilla": args.semilla, "archivo_datos": archivo,
        "donantes_excluidos_por_educacion": int(donante.educ_h.isna().sum()),
        "preguntas_en_catalogo": len(dentro), "preguntas_fuera": len(fuera)}, ensure_ascii=False, indent=1), encoding="utf-8")
    o = ver["opinion"]
    print(f"{len(agentes):,} agentes; sin donante: {ver['sin_donante']}")
    print(f"catálogo: {len(dentro)} preguntas dentro, {len(fuera)} fuera")
    print(f"demografía, peor diferencia por localidad: {ver['demografia_peor_diferencia_por_localidad']}")
    print(f"opinión: {o['fuera_del_margen_95']} de {o['pares_pregunta_localidad']} pares pregunta×localidad fuera del "
          f"margen ({o['fraccion_fuera']:.1%}; umbral 10 %) → {'pasa' if o['pasa'] else 'NO pasa'}; "
          f"ciudad, mayor diferencia de media {o['ciudad_max_dif_media']}")
    print(f"emparejamiento exacto en las cuatro variables: {ver['emparejamiento_exacto_total']:.1%}")
    print(f"reproducible con la misma semilla: {reproducible}")
    print(f"\n{SALIDA.relative_to(RAIZ).as_posix()}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
