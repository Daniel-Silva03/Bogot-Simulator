"""
src/population/electoral.py

Resultados electorales de Bogotá por localidad, a partir de los archivos mesa a
mesa que entregó el CNC: primera vuelta presidencial (2014, 2018, 2022) por
candidato, y Senado y Cámara 2018 por partido (DI-EL8, DI-EL9, más abajo).

POR QUÉ EXISTE
--------------
El proyecto no tenía ninguna medición con geografía real dentro de Bogotá: la
opinión sintética no la trae (el donante no tiene localidad) y la composición no
reproduce la de la EPC (`A08_PASO0B_RESULTS.md`). Los resultados por mesa sí la
traen, y **las zonas 1-20 de la Registraduría son las localidades 1-20**
(verificado en `DATA_INVENTORY.md` §14.3). El voto es otro constructo que la
confianza o la evaluación del alcalde: entra como **referencia territorial**.

Régimen de los datos: D16. Sin datos de personas; se leen de la carpeta de
`BSS_ELECTORAL_DIR`, fuera del repositorio, y aquí solo se escriben agregados
por localidad de resultados públicos de la Registraduría.

Uso:
    $env:BSS_ELECTORAL_DIR = "C:\\Users\\User\\Desktop\\CNC_datos"
    python src/population/electoral.py                     # las dos tablas
    python src/population/electoral.py --solo congreso     # o --solo presidente

Escribe en `data/external/electoral/`:
    presidente_1v_localidad.csv   votos por año × zona × opción
    presidente_1v_zonas.csv       puestos, mesas y totales por año × zona
    presidente_1v_potencial_2018.csv   inscritos habilitados por zona (DIVIPOL 2018)
    presidente_1v_meta.json       fuentes con su huella, verificación, notas
    congreso_2018_localidad.csv   votos por corporación × circunscripción × zona × partido
    congreso_2018_zonas.csv       puestos, mesas, votos_total y votos_partidos
    congreso_2018_meta.json       fuentes, y la verificación de cada circunscripción

DECISIONES DE IMPLEMENTACIÓN
============================

DI-EL1. **Solo primera vuelta presidencial en esta versión.** Mismo cargo en los
    tres años y candidatos que se repiten (Petro y Fajardo en 2018 y 2022), así
    que se puede comparar en el tiempo. Senado y Cámara 2018 esperan: la Cámara de
    Bogotá trae 723 filas duplicadas exactas que hay que entender antes de sumar.
    *(Resuelto el 29/09/2026: no son duplicados, y Senado y Cámara 2018 entran por
    partido; ver DI-EL8 y DI-EL9 en la sección del Congreso.)*

DI-EL2. **Zona = localidad** (hecho verificado, §14.3). La zona 90 es un solo
    puesto, el puesto censo de Corferias (7,6 % del potencial en 2018), y la 98 son
    las cárceles: se conservan, con `cod_loc` vacío, en vez de repartirlas o
    borrarlas. Quien calcule proporciones por localidad decide qué hacer con ellas.
    **Supuesto que viaja con el dato:** la zona es dónde se está inscrito, no dónde
    se vive.

DI-EL3. **2018 sale de la hoja «MMV ESCRUTINIO FINAL».** Hecho: la hoja «antes de
    MOdif» del mismo archivo difiere en 27 votos (Petro −27, Duque +27 en la
    final), y el archivo por municipio (`2018_presidencia_primera_vuelta.dta`)
    coincide con la versión «antes». Decisión: se usa la que el propio archivo
    rotula como final, y la diferencia queda como **diferencia conocida** en la
    verificación. No cambia ninguna proporción en más de 0,001 %.

DI-EL4. **Los candidatos se identifican por lista explícita, no por parecido.**
    Cada nombre de cada año está en `OPCIONES`, con una clave estable entre años
    (`petro` es la misma en 2018 y 2022). Un nombre que no está en la lista
    detiene la construcción: un archivo nuevo o mal leído no puede entrar en
    silencio.

DI-EL5. **La tabla de zonas lleva dos bases: `votos_total` y `votos_candidatos`.**
    Las proporciones de candidato se calculan sobre la segunda (votos válidos por
    candidato), que no depende de cómo cada año codifique blancos, nulos y no
    marcados, ni de si «promotores del voto en blanco» cuenta como blanco (DI-EL6).
    *Corrección (29/09, antes del primer commit):* una primera exploración concluyó
    que 2014 no traía blancos ni nulos. Era falso: esas filas no tienen partido y un
    `groupby` las descartó en silencio. La lista explícita de DI-EL4 lo detectó.

DI-EL6. **«Promotores voto en blanco» (2018) es su propio tipo.** Fue un comité
    inscrito cuya casilla promovía el voto en blanco; si esos votos cuentan como
    blanco es una cuestión jurídica que este módulo no resuelve. Se deja aparte
    (`promotores_blanco`) para que cada análisis lo decida y lo diga.

DI-EL7. **Se verifica contra una fuente independiente.** El total de Bogotá por
    candidato se compara con los archivos por municipio (`.dta`) de 2018 y 2022.
    Cualquier diferencia que no esté en `DIFERENCIAS_CONOCIDAS` detiene la
    escritura. 2014 no tiene archivo municipal: su total se reporta sin
    contraste, y así lo dice el metadato.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import unicodedata
from datetime import date
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

SALIDA = RAIZ / "data" / "external" / "electoral"
MARGINAL = RAIZ / "data" / "external" / "marginal_localidad_18mas.csv"

DEP_BOGOTA_REGISTRADURIA = 16          # el 11 es el del DANE; aquí manda la Registraduría
MPIO_BOGOTA_DANE = 11001
ZONAS_ESPECIALES = {90: "Puesto censo (Corferias)", 98: "Cárceles"}

#: Archivo, lector y hoja de cada año. Los nombres son los que entregó el CNC.
FUENTES = {
    2014: {"archivo": "MMV_PRESIDENTE_2014_1ERA_VUELTA.xlsx", "hoja": "PRESIDENTE_1"},
    2018: {"archivo": "MMV_NACIONAL_PRESIDENTE_2018_1v.xlsx", "hoja": "MMV ESCRUTINIO FINAL"},
    2022: {"archivo": "MMV_NACIONAL_PRESIDENTE_2022_1v.csv", "hoja": None},
}
MUNICIPALES = {2018: "2018_presidencia_primera_vuelta.dta",
               2022: "2022_presidencia_primera_vuelta.dta"}

# (clave, nombre público, tipo, apellido con que aparece en el archivo municipal)
_B = ("blanco", "Voto en blanco", "blanco", "VOTOS EN BLANCO")
_N = ("nulo", "Votos nulos", "nulo", "VOTOS NULOS")
_M = ("no_marcado", "Tarjetas no marcadas", "no_marcado", "NO MARCADAS")

#: DI-EL4. Nombre normalizado en el archivo por mesa -> opción.
OPCIONES = {
    2014: {
        "CLARA LOPEZ": ("clara_lopez", "Clara López", "candidato", None),
        "MARTHA LUCIA RAMIREZ": ("ramirez", "Martha Lucía Ramírez", "candidato", None),
        "JUAN MANUEL SANTOS CALDERON": ("santos", "Juan Manuel Santos", "candidato", None),
        "ENRIQUE PENALOSA": ("penalosa", "Enrique Peñalosa", "candidato", None),
        "OSCAR IVAN ZULUAGA": ("zuluaga", "Óscar Iván Zuluaga", "candidato", None),
        "VOTO BLANCO": _B, "VOTO NULO": _N, "VOTO NO MARCADO": _M,
    },
    2018: {
        "SERGIO FAJARDO": ("fajardo", "Sergio Fajardo", "candidato", "FAJARDO"),
        "GUSTAVO PETRO": ("petro", "Gustavo Petro", "candidato", "PETRO"),
        "IVAN DUQUE": ("duque", "Iván Duque", "candidato", "DUQUE"),
        "GERMAN VARGAS LLERAS": ("vargas_lleras", "Germán Vargas Lleras", "candidato", "VARGAS"),
        "HUMBERTO DE LA CALLE": ("de_la_calle", "Humberto de la Calle", "candidato", "DE LA CALLE"),
        "JORGE ANTONIO TRUJILLO SARMIENTO": ("trujillo", "Jorge Antonio Trujillo", "candidato", "TRUJILLO"),
        "VIVIANE MORALES": ("morales", "Viviane Morales", "candidato", "MORALES"),
        "PROMOTORES VOTO EN BLANCO": ("promotores_blanco", "Promotores del voto en blanco",
                                      "promotores_blanco", "PROMOTORES VOTO EN BLANCO"),
        "VOTOS EN BLANCO": _B, "VOTOS NULOS": _N, "VOTOS NO MARCADOS": _M,
    },
    2022: {
        "GUSTAVO PETRO": ("petro", "Gustavo Petro", "candidato", "PETRO"),
        "RODOLFO HERNANDEZ": ("hernandez", "Rodolfo Hernández", "candidato", "HERNANDEZ"),
        "FEDERICO GUTIERREZ": ("gutierrez", "Federico Gutiérrez", "candidato", "GUTIERREZ"),
        "SERGIO FAJARDO": ("fajardo", "Sergio Fajardo", "candidato", "FAJARDO"),
        "JOHN MILTON RODRIGUEZ": ("rodriguez", "John Milton Rodríguez", "candidato", "RODRIGUEZ"),
        "ENRIQUE GOMEZ MARTINEZ": ("gomez", "Enrique Gómez", "candidato", "GOMEZ"),
        "INGRID BETANCOURT": ("betancourt", "Íngrid Betancourt", "candidato", "BETANCOURT"),
        "LUIS PEREZ": ("perez", "Luis Pérez", "candidato", "PEREZ"),
        "VOTOS EN BLANCO": _B, "VOTOS NULOS": _N, "VOTOS NO MARCADOS": _M,
    },
}

#: DI-EL3. Diferencias contra el archivo municipal que se conocen y se aceptan.
DIFERENCIAS_CONOCIDAS = {(2018, "petro"): -27, (2018, "duque"): +27}


class ElectoralError(RuntimeError):
    """Algo no cuadra en la construcción de la tabla electoral."""


# --------------------------------------------------------------------------
# Utilidades

def normalizar(s) -> str:
    """Mayúsculas, sin tildes, sin puntuación suelta ni espacios repetidos."""
    s = unicodedata.normalize("NFD", str(s)).encode("ascii", "ignore").decode()
    s = "".join(c if c.isalnum() or c.isspace() else " " for c in s)
    return " ".join(s.upper().split())


def resolver_dir(ruta: Optional[str | os.PathLike] = None) -> Path:
    """Carpeta de los archivos electorales: argumento o `BSS_ELECTORAL_DIR` (D16)."""
    ruta = ruta or os.environ.get("BSS_ELECTORAL_DIR")
    if not ruta:
        raise ElectoralError(
            "No sé dónde están los archivos electorales. Pasa --electoral <ruta> o define\n"
            '  PowerShell:  $env:BSS_ELECTORAL_DIR = "<carpeta fuera del repositorio>"')
    p = Path(ruta).expanduser().resolve()
    if not p.is_dir():
        raise ElectoralError(f"{p} no es una carpeta.")
    if p == RAIZ or RAIZ in p.parents:
        raise ElectoralError("La carpeta electoral está dentro del repositorio; debe vivir fuera (D16).")
    return p


def huella(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 24), b""):
            h.update(bloque)
    return h.hexdigest()


def localidades() -> dict[int, str]:
    m = pd.read_csv(MARGINAL)
    return dict(zip(m.COD_LOC.astype(int), m.localidad))


# --------------------------------------------------------------------------
# Lectores: cada uno devuelve las mesas de Bogotá con columnas estándar
#   zona (int), puesto (str), mesa (str), nombre (str, normalizado), votos (int)

def _estandar(df: pd.DataFrame, dep, zona, puesto, mesa, nombre, votos) -> pd.DataFrame:
    df = df[pd.to_numeric(df[dep], errors="coerce") == DEP_BOGOTA_REGISTRADURIA]
    out = pd.DataFrame({
        "zona": pd.to_numeric(df[zona], errors="raise").astype(int),
        "puesto": df[puesto].astype(str).str.strip(),
        "mesa": df[mesa].astype(str).str.strip(),
        "nombre": df[nombre].map(normalizar),
        "votos": pd.to_numeric(df[votos], errors="raise").astype(int),
    })
    if out.empty:
        raise ElectoralError("No hay filas de Bogotá (departamento 16 de la Registraduría).")
    return out


def leer_2014(carpeta: Path) -> pd.DataFrame:
    f = FUENTES[2014]
    df = pd.read_excel(carpeta / f["archivo"], sheet_name=f["hoja"],
                       usecols=["COD_DDE", "COD_ZZ", "COD_PP", "DES_MS", "DES_CAN", "NUM_VOT"])
    return _estandar(df, "COD_DDE", "COD_ZZ", "COD_PP", "DES_MS", "DES_CAN", "NUM_VOT")


def leer_2018(carpeta: Path) -> pd.DataFrame:
    f = FUENTES[2018]
    df = pd.read_excel(carpeta / f["archivo"], sheet_name=f["hoja"])
    df.columns = [str(c).strip() for c in df.columns]
    return _estandar(df, "DEP", "ZONA", "PSTO", "MESA", "CANDIDATO", "VOTOS")


def leer_2022(carpeta: Path) -> pd.DataFrame:
    df = pd.read_csv(carpeta / FUENTES[2022]["archivo"], sep=";", encoding="latin-1",
                     dtype=str, low_memory=False,
                     usecols=["DEP", "ZONA", "PUESTO", "MESA", "CANNOMBRE", "VOTOS"])
    return _estandar(df, "DEP", "ZONA", "PUESTO", "MESA", "CANNOMBRE", "VOTOS")


LECTORES = {2014: leer_2014, 2018: leer_2018, 2022: leer_2022}


def potencial_2018(carpeta: Path, nombres_loc: dict[int, str]) -> pd.DataFrame:
    """Potencial electoral 2018 por zona (hoja DIVIPOL): inscritos habilitados.

    Lo usa el control de inscripción de `GEOGRAFIA_ELECTORAL_SPECIFICATION.md`
    (enmienda 1): la zona es dónde se está inscrito, no dónde se vive.
    """
    df = pd.read_excel(carpeta / FUENTES[2018]["archivo"], sheet_name="DIVIPOL")
    df.columns = [str(c).strip() for c in df.columns]
    df = df[pd.to_numeric(df.DEP, errors="coerce") == DEP_BOGOTA_REGISTRADURIA]
    z = (df.assign(potencial=df.HOMBRE + df.MUJERES)
           .groupby("ZONA").agg(potencial=("potencial", "sum"), mesas_divipol=("MESAS", "sum"))
           .reset_index().rename(columns={"ZONA": "zona"}))
    z.insert(0, "anio", 2018)
    z.insert(2, "cod_loc", z.zona.where(z.zona.between(1, 20)).astype("Int64"))
    z.insert(3, "localidad", z.zona.map(lambda x: nombres_loc.get(x) or ZONAS_ESPECIALES[x]))
    return z


# --------------------------------------------------------------------------
# Agregación

def agregar(mesas: pd.DataFrame, anio: int, nombres_loc: dict[int, str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(votos por zona × opción, resumen por zona). DI-EL2, DI-EL4, DI-EL5."""
    tabla = OPCIONES[anio]
    desconocidos = sorted(set(mesas.nombre) - set(tabla))
    if desconocidos:
        raise ElectoralError(f"{anio}: opciones que no están en OPCIONES (DI-EL4): {desconocidos}")
    zonas_raras = sorted(set(mesas.zona) - set(range(1, 21)) - set(ZONAS_ESPECIALES))
    if zonas_raras:
        raise ElectoralError(f"{anio}: zonas que no son localidades ni especiales: {zonas_raras}")
    if (mesas.votos < 0).any():
        raise ElectoralError(f"{anio}: hay votos negativos.")

    m = mesas.assign(clave=mesas.nombre.map(lambda n: tabla[n][0]),
                     tipo=mesas.nombre.map(lambda n: tabla[n][2]))
    info = {c: (pub, tipo) for c, pub, tipo, _ in tabla.values()}
    votos = m.groupby(["zona", "clave"], as_index=False).votos.sum()
    votos["opcion"] = votos.clave.map(lambda c: info[c][0])
    votos["tipo"] = votos.clave.map(lambda c: info[c][1])

    zonas = m.groupby("zona").agg(puestos=("puesto", "nunique"), votos_total=("votos", "sum"))
    zonas["mesas"] = m.drop_duplicates(["zona", "puesto", "mesa"]).groupby("zona").size()
    zonas["votos_candidatos"] = m[m.tipo == "candidato"].groupby("zona").votos.sum()
    zonas = zonas[["puestos", "mesas", "votos_total", "votos_candidatos"]]
    zonas = zonas.reset_index()

    for df in (votos, zonas):
        df.insert(0, "anio", anio)
        df.insert(2, "cod_loc", df.zona.where(df.zona.between(1, 20)).astype("Int64"))
        df.insert(3, "localidad", df.zona.map(lambda z: nombres_loc.get(z) or ZONAS_ESPECIALES[z]))
    votos = votos[["anio", "zona", "cod_loc", "localidad", "clave", "opcion", "tipo", "votos"]]
    return votos, zonas


# --------------------------------------------------------------------------
# Verificación contra el archivo municipal (DI-EL7)

def totales_municipales(carpeta: Path, anio: int) -> dict[str, int]:
    """Total de Bogotá por clave, según el `.dta` por municipio."""
    x = pd.read_stata(carpeta / MUNICIPALES[anio], convert_categoricals=False)
    x = x[x.codmpio == MPIO_BOGOTA_DANE]
    salida = {}
    for _, fila in x.iterrows():
        texto = normalizar(f"{fila.nombres} {fila.primer_apellido}")
        claves = [c for c, _, _, ap in OPCIONES[anio].values() if ap and normalizar(ap) in texto]
        # «VOTOS EN BLANCO» también está dentro de «PROMOTORES VOTO EN BLANCO»: gana la más larga
        claves = sorted(set(claves), key=lambda c: -len(
            next(ap for cc, _, _, ap in OPCIONES[anio].values() if cc == c)))
        if not claves:
            raise ElectoralError(f"{anio}: fila municipal sin opción conocida: {texto!r}")
        salida[claves[0]] = salida.get(claves[0], 0) + int(fila.votos)
    return salida


def verificar(votos: pd.DataFrame, municipal: dict[str, int], anio: int) -> dict:
    propios = votos.groupby("clave").votos.sum().to_dict()
    filas = []
    for c in sorted(set(propios) | set(municipal)):
        dif = int(propios.get(c, 0)) - int(municipal.get(c, 0))
        esperada = DIFERENCIAS_CONOCIDAS.get((anio, c), 0)
        filas.append({"clave": c, "mesa_a_mesa": int(propios.get(c, 0)),
                      "municipal": int(municipal.get(c, 0)), "diferencia": dif,
                      "esperada": esperada})
    inesperadas = [f for f in filas if f["diferencia"] != f["esperada"]]
    if inesperadas:
        raise ElectoralError(f"{anio}: diferencias no explicadas contra el archivo municipal: {inesperadas}")
    return {"fuente": MUNICIPALES[anio], "coincide": True,
            "diferencias_conocidas": [f for f in filas if f["esperada"]], "por_opcion": filas}


# --------------------------------------------------------------------------

def construir(carpeta: Path, anios=(2014, 2018, 2022)) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    nombres_loc = localidades()
    todos_v, todos_z = [], []
    meta = {"generado": date.today().isoformat(), "regimen": "D16 (DATA_INVENTORY §14)",
            "fuentes": {}, "verificacion": {}, "notas": [
                "zona = localidad (DATA_INVENTORY §14.3); 90 = puesto censo Corferias, 98 = cárceles",
                "la zona es dónde se está inscrito, no dónde se vive",
                "proporciones de candidato: sobre votos_candidatos (DI-EL5)",
                "promotores_blanco (2018) va aparte del voto en blanco (DI-EL6)"]}
    for anio in anios:
        f = FUENTES[anio]
        print(f"  {anio}: leyendo {f['archivo']} ...", flush=True)
        v, z = agregar(LECTORES[anio](carpeta), anio, nombres_loc)
        meta["fuentes"][anio] = {**f, "sha256": huella(carpeta / f["archivo"])}
        if anio in MUNICIPALES:
            meta["verificacion"][anio] = verificar(v, totales_municipales(carpeta, anio), anio)
        else:
            meta["verificacion"][anio] = {"coincide": None,
                                          "nota": "sin archivo municipal para contrastar"}
        todos_v.append(v)
        todos_z.append(z)
    if 2018 in anios:
        meta["potencial_2018"] = {"hoja": "DIVIPOL", "archivo": FUENTES[2018]["archivo"]}
    return pd.concat(todos_v, ignore_index=True), pd.concat(todos_z, ignore_index=True), meta


# --------------------------------------------------------------------------
# Congreso 2018 (Senado y Cámara), por partido
#
# DI-EL8. **Una fila por partido, y ninguna fila del archivo se descarta.** La
#     Cámara de Bogotá trae 723 filas idénticas, todas en las circunscripciones
#     especiales y todas con el candidato vacío. *Hecho:* no son duplicados. Con
#     todas las filas, la circunscripción indígena suma 74.176 votos, exactamente
#     lo que dice el archivo municipal; sin ellas, 73.603. Son candidatos distintos
#     de una misma lista cuyo nombre no viene, y dos que sacan 1 voto en la misma
#     mesa producen filas iguales. Se suma por partido (votos de lista y de
#     candidato juntos), que es la unidad comparable entre localidades.
#
# DI-EL9. **Cada circunscripción se verifica con el criterio que sus fuentes
#     permiten, y el metadato dice cuál fue.**
#     - Cámara territorial: exacta, partido por partido, contra `2018 Camara.xlsx`.
#     - Cámara indígena: exacta en el total, contra `2018_camara.dta.csv`.
#     - Cámara afrodescendiente: diferencia conocida. El municipal suma 6.345 votos
#       más, casi exactamente los votos de lista sin candidato de esa
#       circunscripción (6.344): parece un doble conteo del archivo municipal. No se
#       corrige el dato mesa a mesa.
#     - Senado nacional: aproximada, contra `2018 Senado.xlsx`. Las diferencias van
#       en los dos sentidos, hasta 0,6 % por partido y 0,05 % en el total: las dos
#       fuentes son de cortes distintos del escrutinio. Tolerancia: 1 % por
#       partido, 0,1 % en el total; fuera de eso, se detiene.
#     - Senado indígena: sin fuente municipal para contrastar; se dice.
#     Los nombres se cruzan normalizados; uno truncado en el archivo por mesa (el de
#     la FARC) se reconoce como prefijo del completo.

CONGRESO = {
    "senado": "RESULTADOS_ELECTORALES_2018_SENADO_DE_LA_REPUBLICA_20250530.csv",
    "camara": "RESULTADOS_ELECTORALES_2018_CAMARA_DE_REPRESENTANTES_20250530.csv",
}
CIRCUNSCRIPCION = {"NACIONAL": "nacional", "INDIGENAS": "indigena",
                   "TERRITORIAL DEPARTAMENTAL": "territorial", "AFRO-DESCENDIENTES": "afro"}
ESPECIALES = {"VOTOS EN BLANCO": "blanco", "VOTO EN BLANCO": "blanco", "VOTOS NULOS": "nulo",
              "VOTOS NO MARCADOS": "no_marcado", "VOTO NO MARCADOS": "no_marcado"}
TOLERANCIA_SENADO = {"partido": 0.01, "total": 0.001}
DIFERENCIA_AFRO = 6345          # DI-EL9: votos de más en el archivo municipal


def leer_congreso(carpeta: Path, corporacion: str) -> pd.DataFrame:
    """Mesas de Bogotá de una corporación: circunscripcion, zona, puesto, mesa, partido, tipo, votos."""
    partes = [c[c.NDepto.str.contains("BOGOT", na=False)] for c in pd.read_csv(
        carpeta / CONGRESO[corporacion], chunksize=1_000_000,
        dtype={"partido": str, "candidato": str, "PP": str, "mesa": str},
        usecols=["NCircunscripcion", "NDepto", "ZZ", "PP", "mesa", "partido", "candidato", "votos"])]
    b = pd.concat(partes, ignore_index=True)
    if b.empty:
        raise ElectoralError(f"{corporacion}: no hay filas de Bogotá.")
    desconocidas = set(b.NCircunscripcion) - set(CIRCUNSCRIPCION)
    if desconocidas:
        raise ElectoralError(f"{corporacion}: circunscripciones desconocidas {sorted(desconocidas)}")
    especial = b.partido.isna()
    raros = set(b.loc[especial, "candidato"].map(normalizar)) - set(ESPECIALES)
    if raros:
        raise ElectoralError(f"{corporacion}: filas sin partido que no son blanco, nulo ni no marcado: {sorted(raros)}")
    return pd.DataFrame({
        "circunscripcion": b.NCircunscripcion.map(CIRCUNSCRIPCION),
        "zona": b.ZZ.astype(int), "puesto": b.PP.astype(str), "mesa": b.mesa.astype(str),
        "partido": b.partido.where(~especial, b.candidato).map(normalizar),
        "tipo": np.where(especial, b.candidato.map(normalizar).map(ESPECIALES), "partido"),
        "votos": b.votos.astype(int)})


def agregar_congreso(mesas: pd.DataFrame, corporacion: str,
                     nombres_loc: dict[int, str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    zonas_raras = sorted(set(mesas.zona) - set(range(1, 21)) - set(ZONAS_ESPECIALES))
    if zonas_raras:
        raise ElectoralError(f"{corporacion}: zonas que no son localidades ni especiales: {zonas_raras}")
    votos = mesas.groupby(["circunscripcion", "zona", "partido", "tipo"], as_index=False).votos.sum()
    zonas = mesas.groupby(["circunscripcion", "zona"]).agg(
        puestos=("puesto", "nunique"), votos_total=("votos", "sum"))
    zonas["mesas"] = mesas.drop_duplicates(["circunscripcion", "zona", "puesto", "mesa"]).groupby(
        ["circunscripcion", "zona"]).size()
    zonas["votos_partidos"] = mesas[mesas.tipo == "partido"].groupby(["circunscripcion", "zona"]).votos.sum()
    zonas = zonas.reset_index()
    for df in (votos, zonas):
        df.insert(0, "corporacion", corporacion)
        df.insert(0, "anio", 2018)
        pos = df.columns.get_loc("zona") + 1
        df.insert(pos, "cod_loc", df.zona.where(df.zona.between(1, 20)).astype("Int64"))
        df.insert(pos + 1, "localidad", df.zona.map(lambda z: nombres_loc.get(z) or ZONAS_ESPECIALES[z]))
    return votos, zonas


def _cruzar_nombres(a: dict[str, int], b: dict[str, int]) -> dict[str, tuple]:
    """Empareja claves normalizadas; una truncada se reconoce como prefijo (≥ 30 letras)."""
    pares, usadas = {}, set()
    for k, v in a.items():
        k2 = k if k in b else next((x for x in b if len(k) >= 30 and x.startswith(k)), None)
        pares[k] = (v, b.get(k2))
        if k2:
            usadas.add(k2)
    for x in set(b) - usadas:
        pares[x] = (None, b[x])
    return pares


def verificar_congreso(carpeta: Path, votos: pd.DataFrame, corporacion: str) -> dict:
    """DI-EL9: una verificación por circunscripción, con su criterio."""
    salida = {}
    por_circ = {c: g.groupby("partido").votos.sum().astype(int).to_dict() for c, g in votos.groupby("circunscripcion")}

    def contra_xlsx(archivo, circ, tolerancia):
        x = pd.read_excel(carpeta / archivo)
        x = x[pd.to_numeric(x.codmpio, errors="coerce") == MPIO_BOGOTA_DANE]
        muni = {normalizar(k): int(v) for k, v in x.groupby("nomparti").votos.sum().items()}
        muni = {("VOTOS EN BLANCO" if k == "VOTO EN BLANCO" else "VOTOS NO MARCADOS" if k == "VOTO NO MARCADOS" else k): v
                for k, v in muni.items()}
        pares = _cruzar_nombres(por_circ[circ], muni)
        sin_par = [k for k, (m, n) in pares.items() if m is None or n is None]
        if sin_par:
            raise ElectoralError(f"{corporacion} {circ}: partidos sin par en {archivo}: {sin_par}")
        rel = {k: abs(m - n) / n for k, (m, n) in pares.items() if n}
        tot_m, tot_n = sum(m for m, _ in pares.values()), sum(n for _, n in pares.values())
        if tolerancia is None:
            if any(m != n for m, n in pares.values()):
                raise ElectoralError(f"{corporacion} {circ}: no coincide exacto con {archivo}: "
                                     f"{[(k, m, n) for k, (m, n) in pares.items() if m != n]}")
            return {"fuente": archivo, "criterio": "exacto por partido", "coincide": True}
        peor = max(rel.values())
        if peor > tolerancia["partido"] or abs(tot_m - tot_n) / tot_n > tolerancia["total"]:
            raise ElectoralError(f"{corporacion} {circ}: fuera de tolerancia contra {archivo} "
                                 f"(peor partido {peor:.2%}, total {abs(tot_m - tot_n) / tot_n:.3%})")
        return {"fuente": archivo, "criterio": f"aproximado: ≤ {tolerancia['partido']:.0%} por partido, "
                f"≤ {tolerancia['total']:.1%} en el total", "coincide": "aproximado",
                "peor_partido": round(peor, 4), "total_mesa": tot_m, "total_municipal": tot_n}

    if corporacion == "camara":
        salida["territorial"] = contra_xlsx("2018 Camara.xlsx", "territorial", None)
        m = pd.read_csv(carpeta / "2018_camara.dta.csv")
        m = m[m.codmpio == MPIO_BOGOTA_DANE].groupby("circunscripcion").votos.sum().astype(int)
        ind, afro = sum(por_circ["indigena"].values()), sum(por_circ["afro"].values())
        if ind != int(m["Indígena"]):
            raise ElectoralError(f"camara indigena: {ind} contra {int(m['Indígena'])} en el municipal")
        salida["indigena"] = {"fuente": "2018_camara.dta.csv", "criterio": "exacto en el total", "coincide": True}
        if int(m["Afrodescendientes"]) - afro != DIFERENCIA_AFRO:
            raise ElectoralError(f"camara afro: la diferencia ya no es la conocida ({int(m['Afrodescendientes']) - afro})")
        salida["afro"] = {"fuente": "2018_camara.dta.csv", "criterio": "diferencia conocida (DI-EL9)",
                          "coincide": "diferencia conocida", "total_mesa": afro,
                          "total_municipal": int(m["Afrodescendientes"])}
    else:
        salida["nacional"] = contra_xlsx("2018 Senado.xlsx", "nacional", TOLERANCIA_SENADO)
        salida["indigena"] = {"coincide": None, "criterio": "sin archivo municipal para contrastar"}
    return salida


def construir_congreso(carpeta: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    nombres_loc = localidades()
    vs, zs, meta = [], [], {"generado": date.today().isoformat(), "regimen": "D16 (DATA_INVENTORY §14)",
                            "fuentes": {}, "verificacion": {}, "notas": [
                                "una fila por partido: votos de lista y de candidato juntos (DI-EL8)",
                                "ninguna fila se descarta: las 723 'duplicadas' de la Cámara son candidatos sin nombre",
                                "zona = localidad (DATA_INVENTORY §14.3); 90 = Corferias, 98 = cárceles",
                                "proporciones de partido: sobre votos_partidos"]}
    for corp in CONGRESO:
        print(f"  {corp} 2018: leyendo {CONGRESO[corp]} ...", flush=True)
        v, z = agregar_congreso(leer_congreso(carpeta, corp), corp, nombres_loc)
        meta["fuentes"][corp] = {"archivo": CONGRESO[corp], "sha256": huella(carpeta / CONGRESO[corp])}
        meta["verificacion"][corp] = verificar_congreso(carpeta, v, corp)
        vs.append(v)
        zs.append(z)
    return pd.concat(vs, ignore_index=True), pd.concat(zs, ignore_index=True), meta


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Resultados electorales por localidad (D16).")
    ap.add_argument("--electoral", default=None, help="carpeta de los archivos (o BSS_ELECTORAL_DIR)")
    ap.add_argument("--solo", choices=("presidente", "congreso"), default=None,
                    help="construir solo una de las dos tablas")
    args = ap.parse_args(argv)
    try:
        carpeta = resolver_dir(args.electoral)
        if args.solo != "presidente":
            cv, cz, cmeta = construir_congreso(carpeta)
            SALIDA.mkdir(parents=True, exist_ok=True)
            cv.to_csv(SALIDA / "congreso_2018_localidad.csv", index=False)
            cz.to_csv(SALIDA / "congreso_2018_zonas.csv", index=False)
            (SALIDA / "congreso_2018_meta.json").write_text(
                json.dumps(cmeta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
            for (corp, circ), g in cz.groupby(["corporacion", "circunscripcion"]):
                print(f"  {corp} {circ}: {g.mesas.sum():,} mesas, {g.votos_total.sum():,} votos, "
                      f"verificación: {cmeta['verificacion'][corp][circ].get('coincide')}")
            if args.solo == "congreso":
                return 0
        votos, zonas, meta = construir(carpeta)
    except ElectoralError as e:
        print(f"ERROR: {e}")
        return 1
    SALIDA.mkdir(parents=True, exist_ok=True)
    votos.to_csv(SALIDA / "presidente_1v_localidad.csv", index=False)
    zonas.to_csv(SALIDA / "presidente_1v_zonas.csv", index=False)
    potencial_2018(carpeta, localidades()).to_csv(
        SALIDA / "presidente_1v_potencial_2018.csv", index=False)
    (SALIDA / "presidente_1v_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    for anio, g in zonas.groupby("anio"):
        print(f"  {anio}: {g.mesas.sum():,} mesas, {g.votos_total.sum():,} votos, "
              f"verificación: {meta['verificacion'][anio].get('coincide')}")
    print(f"\n{SALIDA.relative_to(RAIZ).as_posix()}/presidente_1v_*.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
