"""
src/population/poblacion_epc_olas.py

Población EPC 2022-2024: la misma de `poblacion_epc.py`, pero con los encuestados de
2022, 2023 y 2024 como donantes (~250 por localidad en vez de 80). Especificación:
`docs/POBLACION_EPC2022_2024_SPECIFICATION.md`. La población 2023 no se toca.

Uso:
    python src/population/poblacion_epc_olas.py

Escribe en `data/processed/poblacion_epc2022_2024/`:
    agentes.parquet    un agente por fila, con su donante (no se sube)
    donantes.parquet   los donantes con sus respuestas armonizadas (no se sube)
    catalogo.json      las 102 preguntas, cada una con sus años
    verificacion.json  §5 de la especificación
    metadata.json

DECISIONES DE IMPLEMENTACIÓN
============================

DI-PO1. **Módulo aparte que usa las funciones de `poblacion_epc.py`**, en vez de
    meter las olas dentro de él (la especificación decía «extender»). Así la
    población 2023, que usa la página hoy, no cambia en nada. A `emparejar`,
    `construir` y `verificar` solo se les añadió un parámetro con las variables,
    con el valor de siempre por defecto.

DI-PO2. **Una respuesta armonizada por pregunta, con el nombre del código de 2023.**
    Para cada pregunta del catálogo y cada donante: el valor crudo de su año si ese
    año está en `anios` de la armonización (DI-AR1, DI-AR5) y vacío si no. Las
    etiquetas son las mismas en los años que se juntan, así que los códigos
    también. Con esos nombres, el motor de la página puede usar esta población sin
    cambios en cómo lee las respuestas.

DI-PO3. **Conglomerado en 2022: cada persona es el suyo.** Hecho: 2022 no trae
    identificador de manzana (`diseno.SIN_CONGLOMERADO`); la especificación (§2)
    suponía que sí. Decisión: año|localidad|manzana en 2023 y 2024, y año|localidad|
    persona en 2022. Costo: el margen del bootstrap subestima un poco la
    incertidumbre de los donantes de 2022 (no ve su efecto de diseño).

DI-PO4. **Pesos:** los de cada ola reescalados a su tamaño de muestra (DI-AR2), como
    en la armonización. Los encuestados fuera de las localidades 1-19 no entran.
    *Corrección (30/09, en la primera construcción): no basta; ver DI-PO5.*

DI-PO5. **Los pesos se reescalan por ola × localidad**: dentro de cada localidad, cada
    año suma el número de personas que encuestó ahí, y conserva sus pesos relativos
    dentro de la localidad. Hecho, en la primera construcción: el `PONDERA` de 2022
    casi no varía (DI-B5) y no corrige que la EPC sobremuestrea las localidades
    pequeñas; en La Candelaria un donante de 2022 pesaba 0,99 y uno de 2023, 0,11.
    Como el emparejamiento elige donantes según su peso, el 74 % de los agentes de La
    Candelaria heredaba a alguien de 2022 (64 % en Los Mártires, 50 % en Antonio
    Nariño), con los donantes repartidos por tercios. Lo que pesa cada localidad en
    la ciudad lo ponen los agentes (Multipropósito), no los donantes, así que esto
    no le quita nada a las cifras de la ciudad.
"""

from __future__ import annotations

import json
import sys
import warnings
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.population import epc_bcv as eb                   # noqa: E402
from src.population import poblacion_epc as pe            # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "poblacion_epc2022_2024"
ARMONIZADO = RAIZ / "data" / "processed" / "epc_armonizado" / "items.csv"
ANIOS = (2022, 2023, 2024)
VARS_DISTANCIA = ["edad_tramo", "estrato"]                     # §2: sin educación
VARS_DEMO = ("sexo", "edad_tramo", "estrato")
MANZANA = {2023: "MANZANA", 2024: "MANZANA"}                    # DI-PO3: 2022 no la trae


class PoblacionOlasError(RuntimeError):
    """Algo no cuadra al juntar las olas."""


def anios_por_pregunta(ruta: Path = ARMONIZADO) -> dict[str, tuple[int, ...]]:
    arm = pd.read_csv(ruta)
    return {r.variable: tuple(sorted(int(x) for x in str(r.anios).split())) for r in arm.itertuples()}


def armonizar_donantes(olas: dict[int, pd.DataFrame], cat: list[dict], anios: dict[str, tuple],
                       codigo) -> pd.DataFrame:
    """DI-PO2. `olas`: {año: DataFrame con columnas en mayúsculas, peso, cod_loc, sexo,
    edad_tramo, estrato, conglomerado}. `codigo(v, año)`: la columna de v en ese año."""
    partes = []
    for a in sorted(olas):
        d = olas[a]
        base = d[["peso", "cod_loc", "sexo", "edad_tramo", "estrato", "conglomerado"]].copy()
        base.insert(0, "anio", a)
        resp = {}
        for f in cat:
            v, c23 = f["variable"], str(f["codigo"]).upper()
            if v not in anios:
                raise PoblacionOlasError(f"{v} no está en la armonización.")
            if a not in anios[v]:
                resp[c23] = np.full(len(d), np.nan)
                continue
            c = codigo(v, a)
            if c is None or c not in d.columns:
                raise PoblacionOlasError(f"{v} debería estar en {a} con la columna {c}.")
            resp[c23] = pd.to_numeric(d[c], errors="coerce").to_numpy(float)
        partes.append(pd.concat([base.reset_index(drop=True), pd.DataFrame(resp)], axis=1))
    don = pd.concat(partes, ignore_index=True)
    don.insert(0, "donante_id", np.arange(len(don)))
    return don


def cargar_olas() -> dict[int, pd.DataFrame]:
    """Los tres años con demografía, peso reescalado (DI-PO4) y conglomerado (DI-PO3)."""
    from src.population import armonizar_epc as ae
    olas = {}
    for a in ANIOS:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            base, ola = ae.cargar_ola(a)
        d = ola["datos"].copy()
        d.columns = [c.upper() for c in d.columns]
        num = lambda n: pd.to_numeric(d[eb.DEMOGRAFICAS[n][a].upper()], errors="coerce")   # noqa: E731
        loc = base.cod_loc.to_numpy()
        manz = d[MANZANA[a]].astype(str).to_numpy() if a in MANZANA else np.arange(len(d)).astype(str)
        d = d.assign(peso=base.peso.to_numpy(), cod_loc=loc,
                     sexo=num("sexo").map({1: "M", 2: "F"}).to_numpy(),
                     edad_tramo=pe.tramo_edad(num("edad")).to_numpy(),
                     estrato=num("estrato").to_numpy(),
                     conglomerado=[f"{a}|{l}|{m}" for l, m in zip(loc, manz)])
        olas[a] = reescalar_por_localidad(d[pd.Series(loc).between(1, 19).to_numpy()].reset_index(drop=True))
    return olas


def reescalar_por_localidad(d: pd.DataFrame) -> pd.DataFrame:
    """DI-PO5: dentro de una ola, cada localidad suma su número de encuestados."""
    g = d.groupby("cod_loc").peso
    return d.assign(peso=d.peso * g.transform("size") / g.transform("sum"))


def verificar_olas(agentes: pd.DataFrame, donantes: pd.DataFrame) -> dict:
    """§5.3 por año del donante y §5.4 mezcla de años por localidad."""
    con = agentes[agentes.donante_id.notna()]
    anio = donantes.set_index("donante_id").anio.loc[con.donante_id.astype(int)].to_numpy()
    exacto_anio = con.assign(anio=anio).groupby("anio").emparejamiento_exacto.mean()
    mezcla_don = donantes.groupby(["cod_loc", "anio"]).size().unstack(fill_value=0)
    mezcla_don = mezcla_don.div(mezcla_don.sum(axis=1), axis=0)
    mezcla_ag = con.assign(anio=anio).groupby(["cod_loc", "anio"]).size().unstack(fill_value=0)
    mezcla_ag = mezcla_ag.div(mezcla_ag.sum(axis=1), axis=0)
    return {
        "emparejamiento_exacto_por_anio_del_donante": {int(k): round(float(v), 3) for k, v in exacto_anio.items()},
        "mezcla_de_anios_donantes": {int(l): {int(a): round(float(x), 3) for a, x in r.items()} for l, r in mezcla_don.iterrows()},
        "mezcla_de_anios_agentes": {int(l): {int(a): round(float(x), 3) for a, x in r.items()} for l, r in mezcla_ag.iterrows()},
        "mayor_fraccion_de_un_anio_en_agentes": round(float(mezcla_ag.max().max()), 3),
        "donantes_por_localidad": {int(k): int(v) for k, v in donantes.groupby("cod_loc").size().items()},
    }


def main(argv=None) -> int:
    cat, fuera = pe.catalogo()
    anios = anios_por_pregunta()
    from src.population.armonizar_epc import INVENTARIO as INV_EPC
    inv = pd.read_csv(INV_EPC)
    inv = inv[inv.estado == "ok"].set_index(["variable", "anio"]).codigo
    por_var = {f["variable"]: f for f in cat}

    def codigo(v, a):
        return str(por_var[v]["codigo"]).upper() if a == 2023 else str(inv.get((v, a))).upper()

    donantes = armonizar_donantes(cargar_olas(), cat, anios, codigo)
    receptor = pe.cargar_receptor()
    agentes = pe.construir(pe.N_POR_LOCALIDAD, pe.SEMILLA, receptor, donantes, VARS_DISTANCIA)
    otra = pe.construir(pe.N_POR_LOCALIDAD, pe.SEMILLA, receptor, donantes, VARS_DISTANCIA)
    ver = pe.verificar(agentes, donantes, cat, receptor, vars_demo=VARS_DEMO)
    ver.update(verificar_olas(agentes, donantes))
    ver["reproducible_misma_semilla"] = bool(agentes.equals(otra))
    cat_anios = [{**f, "anios": list(anios[f["variable"]])} for f in cat]
    SALIDA.mkdir(parents=True, exist_ok=True)
    agentes.to_parquet(SALIDA / "agentes.parquet", index=False)
    donantes.to_parquet(SALIDA / "donantes.parquet", index=False)
    (SALIDA / "catalogo.json").write_text(json.dumps({"dentro": cat_anios, "fuera": fuera}, ensure_ascii=False, indent=1), encoding="utf-8")
    (SALIDA / "verificacion.json").write_text(json.dumps(ver, ensure_ascii=False, indent=1), encoding="utf-8")
    (SALIDA / "metadata.json").write_text(json.dumps({
        "generado": date.today().isoformat(), "especificacion": "docs/POBLACION_EPC2022_2024_SPECIFICATION.md",
        "donante": "EPC 2022, 2023 y 2024 (Bogotá Cómo Vamos)", "receptor": "Multipropósito 2021",
        "n_agentes": len(agentes), "n_donantes": len(donantes),
        "donantes_por_anio": {int(k): int(v) for k, v in donantes.anio.value_counts().sort_index().items()},
        "semilla": pe.SEMILLA, "vars_distancia": VARS_DISTANCIA,
        "preguntas_por_numero_de_anios": {int(k): int(v) for k, v in
                                          pd.Series([len(f["anios"]) for f in cat_anios]).value_counts().sort_index().items()},
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    o = ver["opinion"]
    print(f"{len(agentes):,} agentes, {len(donantes):,} donantes; sin donante: {ver['sin_donante']}")
    print(f"demografía, peor diferencia por localidad: {ver['demografia_peor_diferencia_por_localidad']}")
    print(f"opinión: {o['fuera_del_margen_95']} de {o['pares_pregunta_localidad']} pares fuera del margen "
          f"({o['fraccion_fuera']:.1%}; umbral 10 %) → {'pasa' if o['pasa'] else 'NO pasa'}; "
          f"ciudad, mayor diferencia de media {o['ciudad_max_dif_media']}")
    print(f"emparejamiento exacto (sexo, edad, estrato): {ver['emparejamiento_exacto_total']:.1%}; "
          f"por año del donante {ver['emparejamiento_exacto_por_anio_del_donante']}")
    print(f"mayor fracción de un solo año en una localidad (agentes): {ver['mayor_fraccion_de_un_anio_en_agentes']}")
    print(f"donantes por localidad: mín {min(ver['donantes_por_localidad'].values())}, "
          f"máx {max(ver['donantes_por_localidad'].values())}")
    print(f"reproducible con la misma semilla: {ver['reproducible_misma_semilla']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
