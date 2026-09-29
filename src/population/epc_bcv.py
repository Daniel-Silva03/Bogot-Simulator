"""
src/population/epc_bcv.py

Carga de la Encuesta de Percepción Ciudadana (EPC) de Bogotá Cómo Vamos,
2014-2019 y 2022-2025.

CUIDADO CON EL NOMBRE
---------------------
En este proyecto conviven dos siglas casi idénticas:

    ECP  = Encuesta de Cultura Política          (DANE)   -> src/population/ecp.py
    EPC  = Encuesta de Percepción Ciudadana      (BCV)    -> este módulo

Se diferencian en dos letras transpuestas. Por eso este módulo se llama
`epc_bcv` y no `epc`: un import equivocado no debe poder escribirse sin
que salte a la vista. Todas las funciones públicas llevan el sufijo `_bcv`
por la misma razón.

PARA QUÉ
--------
La ECP del DANE da cinco olas (2013·2017·2019·2021·2023) y cuatro
transiciones. Los Experimentos 3 a 6 concluyeron que no hay mecanismo de
dinámica de opinión identificable, pero ese veredicto descansaba en esas
cuatro transiciones y era, honestamente, poco poder.

La EPC aporta **nueve olas anuales** de dos ítems de evaluación
institucional en escala 1-5, con factor de expansión en los diez años.
Ocho transiciones, y además un ítem de control medido en la misma muestra.

QUÉ NO APORTA: la batería de *confianza* institucional de la EPC existe
solo en 2024 y 2025 (ver `claude/ANALISIS_EPC_BCV.md` §2). La serie larga
es de *gestión*, que es otro constructo sobre la misma escala. Este módulo
no permite pedir la serie de confianza como si fuera anual.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-B1. El objetivo se define sobre quienes tienen opinión: solo respuestas
    1-5, ponderadas. Los códigos 90 y los faltantes NO se imputan. Quien
    no tiene opinión formada no esconde un valor, y rellenarlo inventaría
    parte del fenómeno. La cobertura viaja SIEMPRE junto a la media y la
    desviación —`serie_bcv()` no puede devolver una sin la otra— porque
    pasa de ~95 % a ~81 % entre 2019 y 2022 y ninguna comparación entre
    años es interpretable sin ese dato. Ver `claude/ANALISIS_NORESPUESTA_EPC.md`.

DI-B2. Los ítems de imagen favorable/desfavorable (`GP1_*`, `GG1`) tienen
    los códigos 1 y 2 INVERTIDOS en 2014-2023 respecto de su propio
    formulario y del diccionario "EPC Suprema": en esos años 1 = Favorable
    y 2 = Desfavorable; en 2024 siguen el formulario. Verificado contra la
    tabla de salida publicada por BCV para 2023 (CADEs: Favorable 64,8 %
    contra 62 % en el código 1 del microdato) y confirmado por el cambio
    de signo de la correlación con `GG3`.

    Este módulo NO expone esos ítems. Pedirlos levanta `ItemNoSoportado`
    con el texto de la inversión. Es deliberado: una serie de imagen
    armada sobre el diccionario produce un salto artificial de ~45 puntos
    en 2024, y prefiero que el proyecto no pueda cometer ese error por
    descuido a documentarlo y confiar en que alguien lo lea.

DI-B3. El nombre del factor de expansión cambia todos los años
    (`PON`, `FEXP`, `PONDERA`, `PONDERADOR`, `Factor1`). Se resuelve por
    tabla explícita y no por heurística de nombre: en varios años conviven
    otras columnas que contienen "PON". La tabla viene del correo del
    analista técnico de BCV del 17/09/2026 y está verificada contra los
    datos (ninguna constante, ninguna ausente).

DI-B4. 2014-2019 traen el factor normalizado a la muestra (suma = n) y
    2022-2025 expandido a población (suma ≈ 6,1-6,3 M). Para medias y
    proporciones ponderadas da exactamente lo mismo, así que NO se
    renormaliza: tocar los pesos entregados solo agrega una oportunidad de
    equivocarse. Quien necesite totales poblacionales debe usar 2022+.

DI-B5. El `PONDERA` de 2022 toma solo 10 valores distintos, contra 60-527
    en los demás años. Es una posestratificación mucho más gruesa.
    `cargar_bcv()` deja constancia en `metadatos["aviso"]` y `serie_bcv()`
    marca ese año en la columna `aviso`. No se corrige —no hay con qué—
    pero no debe pasar inadvertido.

DI-B6. La comparabilidad NO se acepta del diccionario. `ANCLAS_PUBLICADAS`
    guarda cifras de las tablas de salida que la propia BCV publicó, y
    `verificar_anclas_bcv()` las contrasta contra lo que produce el
    cargador. Es la lección de la ECP 2015 y de la inversión de DI-B2:
    dos veces seguidas el diccionario de una fuente mintió sobre sus
    propios códigos. Un diccionario es una hipótesis, no evidencia.

DI-B7. La robustez de cada transición frente a la no respuesta se calcula
    con `robustez_transicion_bcv()`: qué media tendrían que tener los
    excluidos para anular el cambio observado. Si cae fuera de [1,5] el
    cambio es robusto por aritmética. Se prefiere a las cotas de Manski
    porque estas salen siempre anchas y no deciden nada.
"""

from __future__ import annotations

import os
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# Qué años hay, y con qué

ANIOS_BCV = (2014, 2015, 2016, 2017, 2018, 2019, 2022, 2023, 2024, 2025)

ANIOS_AUSENTES = {
    2020: "no se levantó (pandemia)",
    2021: "no se levantó (pandemia)",
}

# DI-B3
FACTOR_POR_ANIO = {
    2014: "PON",        2015: "FEXP",       2016: "PON",
    2017: "PON",        2018: "PON",        2019: "PONDERA",
    2022: "PONDERA",    2023: "FEXP",       2024: "PONDERADOR",
    2025: "Factor1",
}

ANIOS_FACTOR_EXPANDIDO = (2022, 2023, 2024, 2025)   # DI-B4
ANIOS_CON_AVISO = {2022: "el factor de expansión toma solo 10 valores distintos (DI-B5)"}

ESCALA = (1, 2, 3, 4, 5)
CODIGO_NO_RESPUESTA = 90

# --------------------------------------------------------------------------
# Los ítems

#: Ítems de evaluación institucional en escala 1-5. La dirección está
#: enunciada en la propia pregunta ("1 muy mala gestión, 5 muy buena"),
#: así que no depende del diccionario.
ITEMS = {
    "gestion_alcalde": {
        "etiqueta": "Gestión del alcalde o alcaldesa",
        "columnas": {2014: "GG3", 2015: "GG3", 2017: "GG3", 2018: "GG3",
                     2019: "GG3", 2022: "GG3", 2023: "GG3", 2024: "GG3",
                     2025: "GOB_5"},
    },
    "gestion_concejo": {
        "etiqueta": "Gestión del Concejo de Bogotá",
        "columnas": {2014: "CC5", 2015: "CC5", 2016: "CC5", 2017: "CC5",
                     2019: "CC5", 2022: "CC5", 2023: "CC5", 2024: "CC5A",
                     2025: "GOB_6"},
    },
}

#: Ítems que este módulo se niega a servir, con el motivo. DI-B2.
ITEMS_BLOQUEADOS = {
    "imagen_alcalde": (
        "GG1 y los GP1_* tienen los códigos 1/2 invertidos en 2014-2023 "
        "respecto del formulario y del diccionario EPC Suprema. Armar la "
        "serie sobre el diccionario produce un salto artificial de ~45 "
        "puntos en 2024. Ver claude/ANALISIS_EPC_BCV.md §4."
    ),
    "imagen_entidades": (
        "Los GP1_* están invertidos igual que GG1: 1 = Favorable en "
        "2014-2023 y 1 = Desfavorable en 2024, al revés de lo que dicen "
        "el formulario y el diccionario. Ver claude/ANALISIS_EPC_BCV.md §4."
    ),
}

DEMOGRAFICAS = {
    "sexo":      {2014: "SEXO", 2015: "D3", 2016: "CS1", 2017: "SEXO", 2018: "SEXO",
                  2019: "CS1", 2022: "CS1", 2023: "CS1", 2024: "SEXO", 2025: "DMO_1"},
    "edad":      {2014: "EDAD", 2015: "D2", 2016: "EDAD_DEMO", 2017: "EDAD",
                  2018: "CS2_C_1", 2019: "EDAD", 2022: "CS2", 2023: "CS2",
                  2024: "CS2", 2025: "DMO_3_1"},
    "estrato":   {2014: "NSE", 2015: "D1_ORIGINAL", 2016: "NSE", 2017: "NSE",
                  2018: "NSE", 2019: "NSE", 2022: "CS21", 2023: "CS21",
                  2024: "CS2_1", 2025: "DMO_4_1"},
    "localidad": {2014: "LOCALIDAD", 2015: "D7", 2016: "LOCALIDAD",
                  2017: "LOCALIDAD_COMUNA", 2018: "LOCALIDAD_COMUNA",
                  2019: "LOCALIDAD_COMUNA", 2022: "CS0A", 2023: "CS0A",
                  2024: "LOCALIDAD", 2025: "LOCALIDAD"},
}

#: DI-B6. Cifras tomadas de las tablas de salida publicadas por BCV.
#: Formato: (año, item, proporción de 1-2, proporción de 3, proporción de 4-5).
ANCLAS_PUBLICADAS = (
    (2023, "gestion_concejo", 0.440533, 0.431697, 0.127770),
)

TOLERANCIA_ANCLA = 0.02


class EPCError(RuntimeError):
    """Algo no cuadra en la carga de la EPC."""


class ItemNoSoportado(EPCError):
    """Se pidió un ítem que este módulo se niega a servir (DI-B2)."""


# --------------------------------------------------------------------------
# Localización de los archivos

_SUBCARPETA = Path("Microdatos 2014 - 2025")


def resolver_dir_bcv(ruta: str | os.PathLike | None = None) -> Path:
    """Directorio del empaquetado de BCV.

    Orden: argumento explícito > variable de entorno BSS_EPC_DIR > ruta por
    defecto dentro del repo. Se sigue el mismo criterio que `cnc_agregar.py`
    (DI-N7): ninguna ruta absoluta de una máquina concreta queda escrita en
    el código.
    """
    if ruta is not None:
        base = Path(ruta)
    elif os.environ.get("BSS_EPC_DIR"):
        base = Path(os.environ["BSS_EPC_DIR"])
    else:
        base = (Path(__file__).resolve().parents[2] / "data" / "raw"
                / "bogota_como_vamos" / "empaquetado_2026-09"
                / "Encuesta de Percepción Ciudadana")
    if not base.exists():
        raise EPCError(
            f"No encuentro el empaquetado de la EPC en {base}. "
            "Pásalo con el argumento `raiz` o con la variable BSS_EPC_DIR."
        )
    return base


def archivo_del_anio(anio: int, raiz: str | os.PathLike | None = None) -> Path:
    if anio in ANIOS_AUSENTES:
        raise EPCError(f"EPC {anio}: {ANIOS_AUSENTES[anio]}")
    if anio not in ANIOS_BCV:
        raise EPCError(f"EPC {anio}: año fuera de la entrega ({ANIOS_BCV}).")
    f = resolver_dir_bcv(raiz) / _SUBCARPETA / f"EPC_{anio}_microdatos.dta"
    if not f.exists():
        raise EPCError(f"EPC {anio}: falta el microdato en {f}")
    return f


def anios_en_disco(raiz: str | os.PathLike | None = None) -> tuple[int, ...]:
    """Los años que realmente están, sin suponer que la entrega está completa."""
    d = resolver_dir_bcv(raiz) / _SUBCARPETA
    return tuple(a for a in ANIOS_BCV
                 if (d / f"EPC_{a}_microdatos.dta").exists())


# --------------------------------------------------------------------------
# Carga

def _columna(df: pd.DataFrame, nombre: str | None) -> pd.Series | None:
    """Busca sin distinguir mayúsculas: el mismo campo cambia de caja entre años."""
    if nombre is None:
        return None
    indice = {c.upper(): c for c in df.columns}
    real = indice.get(str(nombre).upper())
    return pd.to_numeric(df[real], errors="coerce") if real is not None else None


@dataclass
class Ola:
    """Una ola de la EPC, ya normalizada."""
    anio: int
    datos: pd.DataFrame
    metadatos: dict


def cargar_bcv(anio: int, raiz: str | os.PathLike | None = None) -> Ola:
    """Carga una ola y la deja con nombres de columna estables entre años.

    Devuelve `Ola`, cuyo `datos` tiene: `peso`, las demográficas presentes, y
    una columna por ítem de `ITEMS` con los valores fuera de 1-5 puestos en
    NaN (DI-B1). El original no se altera: los códigos 90 se cuentan aparte,
    en `metadatos["no_respuesta"]`.
    """
    # Varios .dta vienen en latin-1. pandas lo resuelve solo, pero avisa por
    # cada archivo; el aviso se captura y se guarda en los metadatos en vez
    # de ensuciar la salida de cada corrida.
    with warnings.catch_warnings(record=True) as avisos:
        warnings.simplefilter("always", UnicodeWarning)
        crudo = pd.read_stata(archivo_del_anio(anio, raiz),
                              convert_categoricals=False)
    codificacion_de_respaldo = any(
        issubclass(a.category, UnicodeWarning) for a in avisos)

    peso = _columna(crudo, FACTOR_POR_ANIO[anio])
    if peso is None:
        raise EPCError(
            f"EPC {anio}: no está el factor de expansión "
            f"«{FACTOR_POR_ANIO[anio]}» (DI-B3). Columnas parecidas: "
            f"{[c for c in crudo.columns if any(k in c.upper() for k in ('PON','FEX','FACTOR'))]}"
        )
    if peso.nunique(dropna=True) <= 1:
        raise EPCError(
            f"EPC {anio}: el factor «{FACTOR_POR_ANIO[anio]}» es constante. "
            "Eso fue el defecto del empaquetado web de 2025 y hace inútil la "
            "ponderación; no se sigue adelante en silencio."
        )

    salida = pd.DataFrame({"peso": peso.astype(float)})
    for nombre, por_anio in DEMOGRAFICAS.items():
        col = _columna(crudo, por_anio.get(anio))
        if col is not None:
            salida[nombre] = col

    no_respuesta = {}
    for nombre, spec in ITEMS.items():
        col = _columna(crudo, spec["columnas"].get(anio))
        if col is None:
            continue
        no_respuesta[nombre] = int((col == CODIGO_NO_RESPUESTA).sum())
        salida[nombre] = col.where(col.isin(ESCALA))

    # Variables de diseño (conglomerado y estrato de muestreo), con nombre
    # estable. Sin esto, quien estima el error con el diseño real no las
    # encuentra y cae en silencio al DEFF prestado en TODAS las olas: pasó en
    # `preparar_serie.py` con el microdato en disco (corregido el 29/09/2026).
    # Los nombres crudos cambian entre olas (MANZANA / Manzana); aquí no.
    from src.utils.diseno import CONGLOMERADO_POR_ANIO
    col_psu, col_estrato = CONGLOMERADO_POR_ANIO.get(anio, (None, None))
    psu = _columna(crudo, col_psu)
    if psu is not None:
        salida["diseno_psu"] = psu
        est = _columna(crudo, col_estrato)
        if est is not None:
            salida["diseno_estrato"] = est

    meta = {
        "anio": anio,
        "n": int(len(crudo)),
        "factor": FACTOR_POR_ANIO[anio],
        "factor_expandido": anio in ANIOS_FACTOR_EXPANDIDO,
        "suma_factor": float(peso.sum()),
        "valores_distintos_factor": int(peso.nunique(dropna=True)),
        "no_respuesta": no_respuesta,
        "items_disponibles": [k for k in ITEMS if k in salida.columns],
        "aviso": ANIOS_CON_AVISO.get(anio),
        "codificacion_de_respaldo": codificacion_de_respaldo,
        "diseno": {"psu": col_psu if psu is not None else None,
                   "estrato": col_estrato if "diseno_estrato" in salida.columns else None},
    }
    return Ola(anio=anio, datos=salida, metadatos=meta)


# --------------------------------------------------------------------------
# Estimación

def _media_sd_ponderadas(x: np.ndarray, w: np.ndarray) -> tuple[float, float]:
    media = float(np.average(x, weights=w))
    var = float(np.average((x - media) ** 2, weights=w))
    return media, float(np.sqrt(var))


def resumen_ola_bcv(ola: Ola, item: str) -> dict:
    """Media, desviación, cobertura y distribución de un ítem en una ola.

    La cobertura viaja con la media siempre (DI-B1): no hay forma de pedir
    una sin la otra.
    """
    if item in ITEMS_BLOQUEADOS:
        raise ItemNoSoportado(ITEMS_BLOQUEADOS[item])
    if item not in ITEMS:
        raise EPCError(f"Ítem desconocido: {item!r}. Disponibles: {sorted(ITEMS)}")
    if item not in ola.datos.columns:
        raise EPCError(
            f"EPC {ola.anio}: «{item}» no se preguntó ese año "
            f"(años con el ítem: {sorted(ITEMS[item]['columnas'])})."
        )

    s = ola.datos[item]
    w = ola.datos["peso"].fillna(0.0)
    valido = s.notna() & (w > 0)
    if not valido.any():
        raise EPCError(f"EPC {ola.anio}: «{item}» no tiene ninguna respuesta válida.")

    x = s[valido].to_numpy(float)
    ww = w[valido].to_numpy(float)
    media, sd = _media_sd_ponderadas(x, ww)
    props = {f"p{k}": float(np.average((x == k).astype(float), weights=ww))
             for k in ESCALA}
    return {
        "anio": ola.anio,
        "item": item,
        "n_valida": int(valido.sum()),
        "cobertura": float(ww.sum() / w.sum()),
        "media": media,
        "sd": sd,
        **props,
        "aviso": ola.metadatos.get("aviso"),
    }


def serie_bcv(item: str, raiz: str | os.PathLike | None = None,
              anios: tuple[int, ...] | None = None) -> pd.DataFrame:
    """La serie anual de un ítem, una fila por ola, ordenada por año."""
    if item in ITEMS_BLOQUEADOS:
        raise ItemNoSoportado(ITEMS_BLOQUEADOS[item])
    disponibles = anios if anios is not None else anios_en_disco(raiz)
    filas = []
    for a in disponibles:
        if a not in ITEMS[item]["columnas"]:
            continue
        filas.append(resumen_ola_bcv(cargar_bcv(a, raiz), item))
    if not filas:
        raise EPCError(f"No se pudo construir la serie de «{item}»: ninguna ola disponible.")
    return pd.DataFrame(filas).sort_values("anio").reset_index(drop=True)


# --------------------------------------------------------------------------
# Verificación

def verificar_anclas_bcv(raiz: str | os.PathLike | None = None) -> pd.DataFrame:
    """Contrasta el cargador contra cifras que BCV publicó (DI-B6).

    Un diccionario es una hipótesis. Esto es la evidencia.
    """
    filas = []
    for anio, item, esp_12, esp_3, esp_45 in ANCLAS_PUBLICADAS:
        r = resumen_ola_bcv(cargar_bcv(anio, raiz), item)
        obs = (r["p1"] + r["p2"], r["p3"], r["p4"] + r["p5"])
        esp = (esp_12, esp_3, esp_45)
        dif = max(abs(o - e) for o, e in zip(obs, esp))
        filas.append({"anio": anio, "item": item,
                      "obs_1_2": obs[0], "pub_1_2": esp[0],
                      "obs_3": obs[1], "pub_3": esp[1],
                      "obs_4_5": obs[2], "pub_4_5": esp[2],
                      "dif_max": dif, "pasa": dif <= TOLERANCIA_ANCLA})
    return pd.DataFrame(filas)


def robustez_transicion_bcv(serie: pd.DataFrame, anio_a: int, anio_b: int) -> dict:
    """¿Podría la no respuesta explicar el cambio entre dos olas? (DI-B7)

    Calcula qué media tendrían que tener los excluidos del segundo año para
    que el cambio observado desaparezca. Si cae fuera de [1,5] el cambio es
    robusto por aritmética, sin supuestos.
    """
    idx = serie.set_index("anio")
    for a in (anio_a, anio_b):
        if a not in idx.index:
            raise EPCError(f"La serie no tiene el año {a}.")
    ma = float(idx.loc[anio_a, "media"])
    mb = float(idx.loc[anio_b, "media"])
    cb = float(idx.loc[anio_b, "cobertura"])
    requerida = (ma - cb * mb) / (1.0 - cb) if cb < 1.0 else float("nan")
    return {
        "transicion": f"{anio_a}->{anio_b}",
        "delta": mb - ma,
        "cobertura_destino": cb,
        "media_requerida_excluidos": requerida,
        "robusto": not (ESCALA[0] <= requerida <= ESCALA[-1]),
    }


# --------------------------------------------------------------------------
# Donante para el hot-deck
#
# DI-B8. La EPC **no trae nivel educativo del informante**. Con este donante la
#     distancia del hot-deck es `edad_banda` + `estrato`, y se pierde educación.
#     Es una pérdida real pero acotada: las tres variables juntas explican ~3 %
#     de la varianza de opinión (D12, advertencia), así que quitar una de tres
#     no puede costar mucho. Se documenta en vez de disimularse.
#
# DI-B9. La edad viene en **cinco bandas**, no en años (1: 18-25, 2: 26-35,
#     3: 36-45, 4: 46-55, 5: 55+). El receptor, que sí trae años, se bandea con
#     esos mismos cortes. Bandear pierde resolución dentro de banda; emparejar
#     años del receptor contra códigos 1-5 del donante sería mucho peor —la
#     distancia estandarizada mezclaría dos escalas distintas sin avisar.
#
# DI-B10. **`localidad` NO se usa con este donante**, aunque la EPC la trae y la
#     ECP no. El mapa de códigos está verificado (los 19 códigos del formulario
#     reproducen el marginal territorial en 2024 con TVD 0,029 y r = 0,995),
#     pero en 2014 y 2019 los factores de expansión **no** reproducen ese
#     marginal: TVD 0,178 y 0,170, con Suba y Engativá sub-representadas y las
#     localidades pequeñas sobre-representadas. Usar localidad como variable de
#     emparejamiento exacto importaría esa distorsión de diseño al decidir quién
#     dona a quién. Y el premio sería pequeño: la localidad explica ~1 % de la
#     varianza de opinión, la mitad de eso ruido muestral (D15).
#
#     Decidido antes de construir la población, no después de ver el ajuste.

#: Cortes de las bandas de edad de la EPC, para bandear al receptor.
BANDAS_EDAD = ((18, 25), (26, 35), (36, 45), (46, 55), (56, 200))

#: Códigos de localidad del formulario. Verificados contra el marginal
#: territorial en 2024. Sumapaz no está en el marco muestral de la EPC.
LOCALIDADES_EPC = {
    1: "Usaquén", 2: "Chapinero", 3: "Santa Fe", 4: "San Cristóbal",
    5: "Usme", 6: "Tunjuelito", 7: "Bosa", 8: "Kennedy", 9: "Fontibón",
    10: "Engativá", 11: "Suba", 12: "Barrios Unidos", 13: "Teusaquillo",
    14: "Los Mártires", 15: "Antonio Nariño", 16: "Puente Aranda",
    17: "La Candelaria", 18: "Rafael Uribe Uribe", 19: "Ciudad Bolívar",
}

COLUMNA_EDAD_BANDA = "edad_banda"

#: Nombre del "ítem" sintético que sirve la diferencia individual.
ITEM_DIFERENCIA = "diferencia"


def bandear_edad(edad_en_anios) -> pd.Series:
    """Lleva edad en años a las cinco bandas de la EPC (DI-B9)."""
    x = pd.to_numeric(pd.Series(edad_en_anios), errors="coerce")
    salida = pd.Series(np.nan, index=x.index, dtype=float)
    for i, (lo, hi) in enumerate(BANDAS_EDAD, start=1):
        salida[(x >= lo) & (x <= hi)] = float(i)
    return salida


def donante_epc(anio: int, item: str = "gestion_alcalde",
                raiz: str | os.PathLike | None = None) -> pd.DataFrame:
    """Lleva una ola de la EPC al esquema que espera `hot_deck_match`.

    Devuelve: sexo, edad_banda, estrato, <item>, factor_expansion.

    **No trae `localidad` ni `nivel_educativo`** — ver DI-B8 y DI-B10. Quien
    llame debe usar `exact_match_vars = ["sexo"]` y
    `distance_vars = ["edad_banda", "estrato"]`.
    """
    ola = cargar_bcv(anio, raiz)

    # El objetivo B del Experimento 7 no es un ítem del cuestionario sino la
    # resta de dos. Se sirve por el mismo camino para que la población base se
    # construya con el pipeline de siempre y no con una variante aparte.
    if item == ITEM_DIFERENCIA:
        valores = diferencia_individual(ola)
    elif item in ola.datos.columns:
        valores = ola.datos[item]
    else:
        raise EPCError(f"EPC {anio}: «{item}» no se preguntó ese año.")

    d = pd.DataFrame({
        "sexo": ola.datos["sexo"].map({1: "M", 2: "F"}),
        COLUMNA_EDAD_BANDA: pd.to_numeric(ola.datos.get("edad"), errors="coerce"),
        "estrato": pd.to_numeric(ola.datos.get("estrato"), errors="coerce"),
        "factor_expansion": ola.datos["peso"],
        item: valores,
    })

    antes = len(d)
    d = d.dropna().reset_index(drop=True)
    if d.empty:
        raise EPCError(f"EPC {anio}: no quedó ningún donante válido para «{item}».")
    if item == ITEM_DIFERENCIA:
        if not d[item].between(-4, 4).all():
            raise EPCError(f"EPC {anio}: la diferencia salió fuera de [-4, 4].")
    elif not d[item].isin(ESCALA).all():
        raise EPCError(f"EPC {anio}: «{item}» trae valores fuera de 1-5.")
    if not d[COLUMNA_EDAD_BANDA].between(1, len(BANDAS_EDAD)).all():
        raise EPCError(
            f"EPC {anio}: la edad no viene en las {len(BANDAS_EDAD)} bandas esperadas "
            f"(valores: {sorted(d[COLUMNA_EDAD_BANDA].unique())}). Revisar DI-B9."
        )
    return d


def diferencia_individual(ola: Ola) -> pd.Series:
    """d_i = gestión del alcalde − gestión del Concejo, por persona.

    El objetivo B del Experimento 7. Al restar dos ítems contestados por la
    MISMA persona en el MISMO cuestionario desaparece no solo un efecto
    aditivo de periodo sino el estilo de respuesta individual (aquiescencia,
    uso de la escala, tendencia central). Escala −4 a +4, centrada en 0.

    Devuelve NaN donde falte cualquiera de los dos: la cobertura de esta
    serie es la intersección, y es más baja que la de cada ítem por separado.
    """
    faltan = [k for k in ("gestion_alcalde", "gestion_concejo")
              if k not in ola.datos.columns]
    if faltan:
        raise EPCError(
            f"EPC {ola.anio}: no se puede formar la diferencia individual; "
            f"falta {faltan}. Años con los dos ítems: "
            f"{sorted(set(ITEMS['gestion_alcalde']['columnas']) & set(ITEMS['gestion_concejo']['columnas']))}"
        )
    return ola.datos["gestion_alcalde"] - ola.datos["gestion_concejo"]
