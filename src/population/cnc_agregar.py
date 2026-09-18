"""
src/population/cnc_agregar.py

Extrae de los estudios del CNC SOLO agregados por localidad, para poder
usarlos en el simulador sin que ningún registro individual salga del equipo.

POR QUÉ ESTE SCRIPT EXISTE
--------------------------
El `README.md` de `data/raw/cnc/` es explícito: `input/` es copia idéntica
a la del cliente, sustancias trae 50 columnas con nombres y direcciones,
SABE trae 30 incluidas 8 de GPS, y "no sacar estas carpetas del equipo ni
subirlas a ningún servicio".

Este script corre **en la máquina donde viven los datos** y escribe a
`data/external/cnc/` únicamente tablas agregadas: medias ponderadas por
localidad, errores estándar con diseño, y descomposiciones de varianza.
Nunca escribe una fila que corresponda a una persona.

QUÉ APORTAN ESTOS ESTUDIOS, Y QUÉ NO
------------------------------------
Ninguno mide confianza institucional, así que no reemplazan al donante de
D11. Lo que traen, y el proyecto no tenía, es **opinión con resolución de
localidad**: Salud Mental Bogotá 2023 son ~780 personas por localidad en
las 20, y Sustancias Bogotá 2022 unas 545. Más muestra por localidad que
agentes tiene la población sintética entera.

La pregunta que esto permite contestar es la misma que ya le hicimos a la
demografía —que explicó el 3 % de la varianza de confianza— pero ahora
sobre el eje territorial: **¿varía la opinión entre localidades más allá de
lo que explica su composición?** Si sí, el generador territorial tiene por
primera vez un objetivo real. Si no, es otro negativo que conviene saber
antes de seguir construyendo sobre territorio.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-N1. Se reutiliza `carga.py` del propio estudio en vez de leer el .sav
    directo. Ese módulo trae el filtro de PII que el CNC ya revisó, y
    prefiero su lista de patrones a una mía. Además se le pasa SIEMPRE una
    lista explícita de columnas: aunque el filtro fallara, una columna que
    no se pide no se lee.

DI-N2. Las medias se estiman con `estimacion.svy_prop` del estudio.
    A pesar del nombre, su punto y su error estándar valen para cualquier
    variable numérica: el estimador es \\(\\bar{y} = \\sum w y / \\sum w\\) y la
    varianza sale por linealización de Taylor sobre el residuo
    \\(z_i = w_i (y_i - \\bar{y}) / W\\), que no supone que `y` sea 0/1. Lo
    único que no sirve es su intervalo, calculado en escala logit. Acá se
    usa un intervalo normal sobre la escala de la respuesta y se dice.

DI-N3. Los códigos de no respuesta se sacan del propio diccionario
    (`codigos_nr`), no de una lista escrita a mano. Es la diferencia entre
    "9 es no contesta en esta variable" y "9 es no contesta en todas", que
    el propio estudio advierte que no es cierto.

DI-N4. Supresión de celdas chicas. Ninguna estimación con n < 30 se
    escribe, y ninguna celda de composición con n < 25. No es solo
    privacidad: con el DEFF de 7 a 10 que documenta salud mental, una
    media de localidad con 20 casos no significa nada.

DI-N5. La descomposición de varianza se reporta cruda **y** estandarizada
    a la composición de toda la ciudad, por celdas de sexo × edad ×
    educación × estrato. Sin eso, "las localidades difieren" puede ser
    simplemente "las localidades tienen gente distinta", que es lo que ya
    sabemos y no le sirve al generador territorial.

    La estandarización es **un techo, no una medida limpia**. Solo saca la
    composición que las celdas pueden ver: si dentro de una celda las
    localidades siguen difiriendo —por ejemplo en estrato dentro del tramo,
    o en edad dentro del grupo— esa parte se cuenta como territorio. En el
    peor montaje sintético que probé, con un gradiente de estrato mucho más
    extremo que el real y sin ningún efecto territorial, quedó un residuo de
    3,5 % que en realidad era composición. Leer la cifra estandarizada como
    "hasta esto puede ser territorio", nunca como "esto es territorio".

DI-N6. Las celdas de estandarización bajan por una escalera, como el
    hot-deck. Con 20 localidades y celdas finas, casi ninguna llega al
    mínimo y la estandarización no se puede calcular; se baja de nivel hasta
    cubrir el 60 % de la composición y se reporta en qué nivel se resolvió y
    con cuánta cobertura. Una estandarización por sexo × edad no controla lo
    mismo que una por las cuatro variables, y eso tiene que verse en la
    salida.

USO
---
    python src/population/cnc_agregar.py salud_mental
    python src/population/cnc_agregar.py sustancias
    python src/population/cnc_agregar.py            # los dos de Bogotá

Corre con el Python del repositorio. Si `pyreadstat` está instalado lee el
.sav original; si no, lee el `<estudio>_base.xlsx` que el propio CNC genera
sin datos personales. Las dos rutas piden exactamente las mismas columnas,
así que el resultado es el mismo.

Lo único que necesita sí o sí es `scipy` (lo usa `estimacion.py` del CNC) y,
para la ruta del xlsx, `openpyxl`.
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ_REPO = Path(__file__).resolve().parents[2]
DIR_CNC = RAIZ_REPO / "data" / "raw" / "cnc" / "estudios" / "estudios"
DIR_SALIDA = RAIZ_REPO / "data" / "external" / "cnc"

N_MIN_ESTIMACION = 30      # DI-N4
N_MIN_CELDA = 25

# --------------------------------------------------------------------------
# Qué pedirle a cada estudio. Solo estas columnas se leen del .sav.
# --------------------------------------------------------------------------

ESTUDIOS = {
    "salud_mental": dict(
        localidad="LOCALIDAD",
        peso="FACTOR",
        estrato_diseno="ESTRATO",
        upm="ID_MANZANA_OR",
        sexo="GENERO",
        edad="EDAD",
        educacion="P9",
        estrato_socio="ESTRATO",
        baterias={
            # Satisfacción con la vida, 1-5. Es la batería de opinión con
            # más muestra del estudio (adultos 18+).
            "M1": [f"M1_{i}" for i in range(1, 12)],
            # APGAR familiar, 0-4: apoyo social percibido dentro del hogar.
            "M41": [f"M41_{i}" for i in range(1, 6)],
        },
        universo="adultos 18+ (la batería M1 no se aplica a los módulos N y A)",
    ),
    "sustancias": dict(
        localidad="LOCALIDAD",
        peso="factor",
        estrato_diseno="LOCALIDAD",     # el diseño estratifica POR localidad
        upm="USM",
        sexo="SEXO",
        edad="EDAD_SELECC",
        educacion="P11",
        estrato_socio="ESTRATO_I",
        baterias={
            # Acuerdo con medidas de política pública, 1-5. Es lo más
            # parecido a "opinión pública" que hay con localidad.
            "T150": [f"T150_{i}" for i in range(1, 7)],
            # Percepción de riesgo, 1-4.
            "T29": [f"T29_{i}" for i in range(1, 21)],
        },
        universo="12 a 65 años",
    ),
}


# --------------------------------------------------------------------------
# Acceso al estudio (usa SUS módulos, no los reimplementa)
# --------------------------------------------------------------------------

class _PyreadstatAusente:
    """Relleno para poder importar `carga.py` sin pyreadstat instalado.

    `carga.py` hace `import pyreadstat` arriba del todo, así que sin ese
    paquete ni siquiera se puede leer su filtro de PII. Con este relleno el
    módulo importa, `is_pii` y `pii_cols` funcionan —que es lo que hace
    falta— y cualquier intento de leer un .sav falla con un mensaje claro en
    vez de un ImportError a mitad de camino.
    """

    def __getattr__(self, nombre):
        def _falla(*a, **kw):
            raise RuntimeError(
                "pyreadstat no está instalado: no se puede leer el .sav. "
                "Este script debería haber usado el .xlsx (ver _leer_base)."
            )
        return _falla


def _cargar_modulos(clave: str):
    """Importa `estudio`, `carga` y `estimacion` del estudio pedido.

    `carga.py` hace `import estudio` a secas, así que su `src/` tiene que
    estar primero en sys.path. Si ya se importó otro estudio en el mismo
    proceso, hay que sacar los módulos viejos o se mezclan las fichas.

    Devuelve también si pyreadstat está disponible, porque de eso depende
    si se puede leer el .sav o hay que ir al .xlsx.
    """
    src = DIR_CNC / clave / "src"
    if not src.is_dir():
        raise SystemExit(
            f"No está {src}.\nSe esperaba la carpeta del CNC en {DIR_CNC}."
        )
    try:
        importlib.import_module("pyreadstat")
        hay_pyreadstat = True
    except ImportError:
        hay_pyreadstat = False
        sys.modules.setdefault("pyreadstat", _PyreadstatAusente())

    for nombre in ("estudio", "carga", "estimacion", "diccionario"):
        sys.modules.pop(nombre, None)
    sys.path.insert(0, str(src))
    estudio = importlib.import_module("estudio")
    carga = importlib.import_module("carga")
    estimacion = importlib.import_module("estimacion")
    return estudio, carga, estimacion, hay_pyreadstat


def _leer_base(clave, estudio, carga, columnas, hay_pyreadstat) -> pd.DataFrame:
    """Lee SOLO las columnas pedidas, del .sav si se puede y del .xlsx si no.

    El .xlsx no es un atajo peor: el `preparar_input.py` del CNC lo genera
    **sin datos personales**, así que para lo que hace este script da lo
    mismo. La única advertencia de su README —que el filtro por nombre no
    atrapa las fechas de nacimiento del listado del hogar en sustancias
    (`EDAD_DD_*`, `EDAD_AAAA_*`, `FECHA_*`)— no aplica acá, porque esas
    columnas no están en la lista que se pide y lo que no se pide no se lee.
    De todos modos se le pasa el filtro de PII del propio estudio por encima.
    """
    if hay_pyreadstat:
        df, _ = carga.cargar(cols=columnas)       # DI-N1
        return df

    xlsx = estudio.INPUT / f"{clave}_base.xlsx"
    if not xlsx.exists():
        raise SystemExit(
            f"Falta pyreadstat para leer el .sav y tampoco está {xlsx.name}.\n"
            f"Opciones: instalar pyreadstat (pip install pyreadstat) o "
            f"regenerar el xlsx con el preparar_input.py del CNC."
        )
    print(f"  pyreadstat no está: se lee {xlsx.name}, que el CNC genera sin PII")
    quiero = set(columnas)
    try:
        df = pd.read_excel(xlsx, usecols=lambda c: str(c).strip() in quiero)
    except ImportError as e:
        raise SystemExit(
            f"Para leer el xlsx hace falta openpyxl (pip install openpyxl). [{e}]")
    df.columns = [str(c).strip() for c in df.columns]

    faltan = [c for c in columnas if c not in df.columns]
    if faltan:
        print(f"  aviso: {len(faltan)} columnas no están en el xlsx: {faltan[:8]}")
    sobran = carga.pii_cols(df.columns)           # cinturón y tirantes
    if sobran:
        print(f"  se descartan {len(sobran)} columnas que el filtro marca como PII")
        df = df.drop(columns=sobran)
    return df


def _diccionario(clave: str) -> dict:
    ruta = DIR_CNC / clave / "input" / f"{clave}_diccionario.json"
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def _limpiar(serie: pd.Series, entrada: dict | None) -> pd.Series:
    """A número, con los códigos de no respuesta del diccionario fuera (DI-N3)."""
    v = pd.to_numeric(serie, errors="coerce")
    nr = (entrada or {}).get("codigos_nr") or []
    if isinstance(nr, dict):
        nr = list(nr)
    codigos = []
    for c in nr:
        try:
            codigos.append(float(c))
        except (TypeError, ValueError):
            continue
    return v.where(~v.isin(codigos)) if codigos else v


# --------------------------------------------------------------------------
# Estimación
# --------------------------------------------------------------------------

def media_con_diseno(estimacion, y, w, estrato=None, upm=None) -> dict:
    """Media ponderada con error estándar de diseño (DI-N2).

    Reutiliza la linealización de `svy_prop`, que no supone que `y` sea
    binaria, y reemplaza su intervalo logit por uno normal sobre la escala
    de la respuesta.
    """
    r = estimacion.svy_prop(y, w, estrato, upm)
    media, se, n = r["p"], r["se"], r["n"]
    if not n:
        return dict(media=np.nan, se=np.nan, lo=np.nan, hi=np.nan, n=0, Nw=0.0, deff=np.nan)

    y_num = pd.to_numeric(pd.Series(y), errors="coerce")
    w_num = pd.to_numeric(pd.Series(w), errors="coerce")
    ok = y_num.notna() & w_num.notna() & (w_num > 0)
    var_pob = np.average((y_num[ok] - media) ** 2, weights=w_num[ok])
    var_mas = var_pob / n if n else np.nan          # muestreo aleatorio simple
    return dict(media=float(media), se=float(se),
                lo=float(media - 1.96 * se), hi=float(media + 1.96 * se),
                n=int(n), Nw=float(r["Nw"]),
                deff=float(se ** 2 / var_mas) if var_mas and var_mas > 0 else np.nan)


#: Escalera de estandarización, de la celda más fina a la más gruesa.
#: Con 20 localidades y ~780 casos en cada una, cruzar cuatro variables deja
#: casi todas las celdas por debajo del mínimo y la estandarización no se
#: puede calcular. Se baja de nivel hasta que la composición cubierta alcance
#: `COBERTURA_MINIMA`, y se reporta en qué nivel se resolvió: una
#: estandarización por sexo × edad no controla lo mismo que una por las
#: cuatro, y quien lea la salida tiene que poder verlo.
ESCALERA_CELDAS = [
    ("sexo x edad x educacion x estrato6", ["sexo", "edad", "educacion", "estrato6"]),
    ("sexo x edad x estrato6",             ["sexo", "edad", "estrato6"]),
    ("sexo x edad x educacion x estrato3", ["sexo", "edad", "educacion", "estrato"]),
    ("sexo x edad x estrato3",             ["sexo", "edad", "estrato"]),
    ("sexo x edad",                        ["sexo", "edad"]),
    ("edad",                               ["edad"]),
]
COBERTURA_MINIMA = 0.60
N_MIN_CELDA_ESTAND = 5


def _dimensiones(df, cfg) -> dict:
    """Las cuatro variables de estandarización, ya recortadas."""
    sexo = pd.to_numeric(df[cfg["sexo"]], errors="coerce")
    edad = pd.to_numeric(df[cfg["edad"]], errors="coerce")
    educ = pd.to_numeric(df["_educacion"], errors="coerce")
    estr = pd.to_numeric(df["_estrato"], errors="coerce")
    return {
        "sexo": sexo.astype("Int64").astype(str),
        "edad": pd.cut(edad, [-1, 17, 29, 44, 59, 200],
                       labels=["<18", "18-29", "30-44", "45-59", "60+"]).astype(str),
        "educacion": pd.cut(educ, [-1, 3, 5, 99],
                            labels=["bajo", "medio", "alto"]).astype(str),
        "estrato": pd.cut(estr, [-1, 2, 4, 6],
                          labels=["1-2", "3-4", "5-6"]).astype(str),
        # El estrato sin agrupar separa bastante mejor: con tramos de dos
        # estratos, el gradiente que queda DENTRO del tramo sigue
        # diferenciando localidades y la estandarización solo saca la mitad.
        # Medido sobre datos sintéticos con composición pura y sin efecto
        # territorial (n = 780 por localidad): 10,8 % crudo -> 5,7 %
        # estandarizando con tramos de tres, -> 3,5 % con el estrato
        # completo. En el mismo montaje, un efecto territorial real de
        # 4,9 % sobrevive la estandarización intacto (5,1 %).
        "estrato6": estr.round().astype("Int64").astype(str),
    }


def _celdas(df, cfg, dims=None) -> pd.Series:
    """Celda demográfica más fina (nivel 0 de la escalera)."""
    d = dims or _dimensiones(df, cfg)
    return d["sexo"] + "|" + d["edad"] + "|" + d["educacion"] + "|" + d["estrato"]


def descomponer_varianza(df, item, cfg) -> dict:
    """Cuánta varianza de un ítem está ENTRE localidades, cruda y neta de
    composición (DI-N5)."""
    dims = [c for c in df.columns if c.startswith("_dim_")]
    g = df[[item, "_localidad", "_peso"] + dims].dropna()
    if len(g) < N_MIN_ESTIMACION * 5:
        return {}
    w, y = g["_peso"], g[item]
    mu = np.average(y, weights=w)
    total = np.average((y - mu) ** 2, weights=w)

    por_loc = g.groupby("_localidad").apply(
        lambda x: pd.Series({"m": np.average(x[item], weights=x["_peso"]),
                             "w": x["_peso"].sum(), "n": len(x)}),
        include_groups=False)
    por_loc = por_loc[por_loc["n"] >= N_MIN_ESTIMACION]
    entre = float((por_loc["w"] * (por_loc["m"] - mu) ** 2).sum() / por_loc["w"].sum())

    # Estandarización directa a la composición de toda la ciudad, bajando por
    # la escalera hasta que la composición cubierta alcance el mínimo.
    entre_est, nivel_usado, cobertura = np.nan, None, np.nan
    for etiqueta, dims in ESCALERA_CELDAS:
        col = g[[f"_dim_{d}" for d in dims]].agg("|".join, axis=1)
        peso_celda = g["_peso"].groupby(col).sum()
        peso_celda /= peso_celda.sum()
        tmp = g.assign(_c=col)
        medias = tmp.groupby(["_localidad", "_c"]).apply(
            lambda x: (np.average(x[item], weights=x["_peso"])
                       if len(x) >= N_MIN_CELDA_ESTAND else np.nan),
            include_groups=False)
        est, cobs = {}, []
        for loc in por_loc.index:
            if loc not in medias.index.get_level_values(0):
                continue
            m = medias.loc[loc].dropna()
            if m.empty:
                continue
            pw = peso_celda.reindex(m.index).fillna(0)
            cobs.append(pw.sum())
            if pw.sum() >= COBERTURA_MINIMA:
                est[loc] = float((m * pw).sum() / pw.sum())
        if len(est) >= 0.8 * len(por_loc):
            e = pd.Series(est)
            wl = por_loc.loc[e.index, "w"]
            mu_e = float((e * wl).sum() / wl.sum())
            entre_est = float((wl * (e - mu_e) ** 2).sum() / wl.sum())
            nivel_usado, cobertura = etiqueta, float(np.mean(cobs))
            break

    return dict(item=item, n=int(len(g)), localidades=int(len(por_loc)),
                media=float(mu), var_total=float(total),
                var_entre=entre, var_dentro=float(total - entre),
                pct_entre=100 * entre / total if total else np.nan,
                var_entre_estandarizada=entre_est,
                pct_entre_estandarizado=(100 * entre_est / total
                                         if total and not np.isnan(entre_est) else np.nan),
                nivel_estandarizacion=nivel_usado,
                cobertura_composicion=cobertura)


# --------------------------------------------------------------------------

def procesar(clave: str) -> None:
    cfg = ESTUDIOS[clave]
    estudio, carga, estimacion, hay_pyreadstat = _cargar_modulos(clave)
    dicc = _diccionario(clave)

    items = [v for lista in cfg["baterias"].values() for v in lista]
    columnas = list(dict.fromkeys(
        [cfg["localidad"], cfg["peso"], cfg["estrato_diseno"], cfg["upm"],
         cfg["sexo"], cfg["edad"], cfg["educacion"], cfg["estrato_socio"]] + items))

    print(f"\n{'=' * 70}\n{estudio.NOMBRE}  (n esperado {estudio.N_ESPERADO:,})")
    print(f"  se piden {len(columnas)} columnas; ninguna de PII")
    df = _leer_base(clave, estudio, carga, columnas, hay_pyreadstat)
    print(f"  cargadas {len(df):,} filas × {df.shape[1]} columnas")
    if len(df) != estudio.N_ESPERADO:
        print(f"  AVISO: se esperaban {estudio.N_ESPERADO:,} filas. "
              "Revisar antes de usar los agregados.")

    df["_peso"] = pd.to_numeric(df[cfg["peso"]], errors="coerce")
    df["_localidad"] = pd.to_numeric(df[cfg["localidad"]], errors="coerce")
    df["_educacion"] = _limpiar(df[cfg["educacion"]], dicc.get(cfg["educacion"]))
    df["_estrato"] = _limpiar(df[cfg["estrato_socio"]], dicc.get(cfg["estrato_socio"]))
    for it in items:
        if it in df.columns:
            df[it] = _limpiar(df[it], dicc.get(it))
    presentes = [it for it in items if it in df.columns]
    _d = _dimensiones(df, cfg)
    for k, v in _d.items():
        df[f"_dim_{k}"] = v
    df["_celda"] = _celdas(df, cfg, _d)

    DIR_SALIDA.mkdir(parents=True, exist_ok=True)

    # --- 1. medias por localidad ---------------------------------------
    filas = []
    for it in presentes:
        nombre = (dicc.get(it) or {}).get("nombre", "")
        escala = (dicc.get(it) or {}).get("escala") or {}
        for loc, g in df.groupby("_localidad"):
            r = media_con_diseno(estimacion, g[it], g["_peso"],
                                 g[cfg["estrato_diseno"]], g[cfg["upm"]])
            if r["n"] < N_MIN_ESTIMACION:      # DI-N4
                continue
            filas.append(dict(estudio=clave, item=it, nombre=nombre[:90],
                              min_escala=min(map(int, escala)) if escala else None,
                              max_escala=max(map(int, escala)) if escala else None,
                              localidad=int(loc), **r))
    loc_df = pd.DataFrame(filas)
    loc_df.to_csv(DIR_SALIDA / f"{clave}_localidad.csv", index=False)
    print(f"  -> {clave}_localidad.csv  ({len(loc_df)} estimaciones, "
          f"{loc_df['localidad'].nunique()} localidades)")

    # --- 2. descomposición de varianza ---------------------------------
    var_df = pd.DataFrame([d for d in (descomponer_varianza(df, it, cfg)
                                       for it in presentes) if d])
    if not var_df.empty:
        var_df.insert(0, "estudio", clave)
        var_df["nombre"] = [(dicc.get(i) or {}).get("nombre", "")[:90] for i in var_df["item"]]
    var_df.to_csv(DIR_SALIDA / f"{clave}_varianza.csv", index=False)
    print(f"  -> {clave}_varianza.csv  ({len(var_df)} ítems)")

    # --- 3. composición por localidad ----------------------------------
    comp = (df.dropna(subset=["_localidad", "_peso"])
              .groupby(["_localidad", "_celda"])
              .agg(n=("_peso", "size"), Nw=("_peso", "sum")).reset_index())
    comp = comp[comp["n"] >= N_MIN_CELDA]      # DI-N4
    comp["share"] = comp["Nw"] / comp.groupby("_localidad")["Nw"].transform("sum")
    comp.insert(0, "estudio", clave)
    comp.to_csv(DIR_SALIDA / f"{clave}_composicion.csv", index=False)
    print(f"  -> {clave}_composicion.csv  ({len(comp)} celdas, "
          f"las de menos de {N_MIN_CELDA} casos suprimidas)")

    # --- 4. ficha ------------------------------------------------------
    tam = (df.dropna(subset=["_localidad"]).groupby("_localidad")
             .agg(n=("_peso", "size"), Nw=("_peso", "sum")))
    meta = dict(
        estudio=clave, nombre=estudio.NOMBRE, anio=estudio.ANIO,
        cliente=estudio.CLIENTE, universo=estudio.UNIVERSO,
        n=int(len(df)), n_esperado=int(estudio.N_ESPERADO),
        peso_expande=bool(estudio.PESO_EXPANDE),
        poblacion_expandida=float(df["_peso"].sum()),
        diseno=dict(peso=cfg["peso"], estrato=cfg["estrato_diseno"], upm=cfg["upm"]),
        localidades=int(tam.shape[0]),
        n_por_localidad=dict(minimo=int(tam["n"].min()), mediana=float(tam["n"].median()),
                             maximo=int(tam["n"].max())),
        baterias={k: len(v) for k, v in cfg["baterias"].items()},
        universo_baterias=cfg["universo"],
        advertencias_del_estudio=list(estudio.ADVERTENCIAS),
        nota_privacidad=("Solo agregados. Estimaciones con n < "
                         f"{N_MIN_ESTIMACION} y celdas con n < {N_MIN_CELDA} suprimidas. "
                         "Ningún registro individual sale de este archivo."),
    )
    with open(DIR_SALIDA / f"{clave}_meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"  -> {clave}_meta.json")

    if not var_df.empty:
        print("\n  varianza ENTRE localidades (cruda / neta de composición):")
        for r in var_df.sort_values("pct_entre", ascending=False).head(8).itertuples():
            est = (f"{r.pct_entre_estandarizado:5.2f}%"
                   if not np.isnan(r.pct_entre_estandarizado) else "  —  ")
            print(f"    {r.item:10s} {r.pct_entre:5.2f}% / {est}   {r.nombre[:48]}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Agregados por localidad de los estudios del CNC, sin datos personales.")
    p.add_argument("estudio", nargs="?", choices=sorted(ESTUDIOS),
                   help="por defecto corre los dos de Bogotá")
    args = p.parse_args(argv)

    if not DIR_CNC.is_dir():
        print(f"No está la carpeta del CNC en {DIR_CNC}")
        return 1
    for clave in ([args.estudio] if args.estudio else sorted(ESTUDIOS)):
        procesar(clave)
    print(f"\nTodo en {DIR_SALIDA}")
    print("Esos cuatro archivos por estudio son los únicos que hay que compartir.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
