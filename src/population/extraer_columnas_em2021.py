"""
src/population/extraer_columnas_em2021.py

Preparación de los archivos crudos de `data/raw/` para el hot-deck
(`src/population/loader.py` -> `matching.py` -> `build_agents.py`).

Dos fuentes, dos trabajos distintos:

    multiproposito  em2021.csv (~1,25 GB) es demasiado grande para cargarlo
                    entero en cada corrida. Se extraen por chunks solo las
                    columnas que el receptor necesita, a
                    em2021_receptor_v2.csv.

    confianza       el export de la Encuesta de Confianza Institucional
                    (Veeduría Distrital) es chico y `loader.py` lo lee
                    directo: NO hace falta extraer nada. Lo que sí hace
                    falta es VERIFICAR que ese archivo tiene las columnas
                    que el loader busca, porque sus encabezados vienen con
                    tildes corruptas (cp850 mal decodificado) y cambian
                    entre reexportaciones del formulario. Este modo hace
                    esa verificación y deja un reporte en disco.

    inspeccionar    vuelca los nombres de columna de cualquier archivo de
                    data/raw/ a un .txt, para poder revisarlos sin abrir un
                    archivo de 1,25 GB.

Uso (desde la raíz del repositorio):

    python src/population/extraer_columnas_em2021.py multiproposito
    python src/population/extraer_columnas_em2021.py confianza
    python src/population/extraer_columnas_em2021.py inspeccionar em2021.csv

------------------------------------------------------------------------
CAMBIOS RESPECTO A LA PRIMERA VERSIÓN DE ESTE SCRIPT
------------------------------------------------------------------------

1. Rutas. Antes el script exigía "colócalo en la misma carpeta que
   em2021.csv" y leía "em2021.csv" como ruta relativa al directorio de
   trabajo. Ahora que vive en src/population/ y los datos están en
   data/raw/, eso no funcionaba. Las rutas se resuelven desde la raíz del
   repositorio, deducida de la ubicación de este archivo.

2. Factor de expansión. La versión anterior extraía cinco columnas, y
   ninguna era el ponderador de la encuesta. Multipropósito sobre-muestrea
   localidades pequeñas a propósito (para poder estimar a nivel de
   localidad), así que una muestra sin ponderar hereda esa distorsión: en
   la corrida de septiembre, Bosa quedó con 38 agentes de 1.000 y
   Teusaquillo con 56, al revés de sus tamaños reales. Este script ahora
   BUSCA la columna de factor de expansión y la incluye en el extracto.
   No decide cómo usarla — eso es A16 — pero sin extraerla no se puede
   decidir nada.

3. Escritura incremental. Antes se acumulaban todos los chunks en memoria
   y se concatenaban al final, lo que en la práctica significa tener el
   extracto completo en RAM. Ahora cada chunk se escribe a disco.

4. Ya no dice "sube el archivo resultante a la conversación": los datos
   viven en el repositorio, ese paso no existe.

Se conserva la corrección que motivó la versión v2 y que sigue siendo el
control más importante de este script: ESTRATO2021 NO es el estrato
socioeconómico, es un código interno de unidad de muestreo (valores de 8
dígitos tipo 11001202). La variable correcta es NVCBP11AA ("Estrato para
tarifa"), la clasificación 1-6 de la factura de servicios públicos.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

RAIZ_REPO = Path(__file__).resolve().parents[2]
DIR_RAW = RAIZ_REPO / "data" / "raw"
# data/external/ sí se versiona: son tablas de referencia chicas y derivadas,
# no descargas. Que el marginal territorial esté en git es lo que permite
# auditar contra qué se ponderó una corrida.
DIR_EXTERNAL = RAIZ_REPO / "data" / "external"

# Ejecutado como script, sys.path[0] es src/population/, no la raíz del
# repo, así que "from src.population..." fallaría. Mismo patrón que usan
# los tests.
sys.path.insert(0, str(RAIZ_REPO))

from src.population.build_agents import LOCALIDADES_VALIDAS_BOGOTA  # noqa: E402
from src.population.loader import (  # noqa: E402
    CONFIANZA_ENCODING,
    CONFIANZA_SEPARADOR,
    FRAGMENTOS_ID_CONFIANZA,
    PATRON_FACTOR_EXPANSION,
    _buscar_columna,
    _FRAGMENTOS_ACTORES_CONFIANZA,
)

# --- Multipropósito (receptor) -------------------------------------------

EM_ENTRADA = "em2021.csv"
EM_SALIDA = "em2021_receptor_v2.csv"

COLUMNAS_EM = [
    "NOMBRE_LOCALIDAD",  # localidad
    "SEXO",              # sexo imputado (1=Hombre, 2=Mujer)
    "NPCEP4",            # edad (años cumplidos)
    "NVCBP11AA",         # estrato para tarifa (1-6) — NO usar ESTRATO2021
    "NPCHP4",            # nivel educativo más alto alcanzado (1-15)
]

# El patrón que identifica al ponderador se importa de loader.py (arriba),
# que es quien lo consume: si cambia allá, este script sigue extrayendo la
# columna que el loader va a buscar.

CHUNK = 200_000

# Cómo se invoca este script, para los mensajes de ayuda.
ATAJO = "src/population/extraer_columnas_em2021.py"

# --- Confianza institucional (donante) -----------------------------------

CONFIANZA_PATRON_ARCHIVO = re.compile(r"confianza", re.IGNORECASE)

# Los fragmentos de identificación y de actores se IMPORTAN de loader.py,
# no se copian. El punto de este modo es predecir si el loader va a poder
# leer el archivo: un verificador más estricto daría falsas alarmas y uno
# más laxo, falsa tranquilidad.
#
# Una primera versión de este script los tenía duplicados y abreviados
# ("Secretar", "Polic", "Alcald"...) pensando que así aguantaban mejor los
# cambios de codificación. Contra el archivo real de 144 columnas resultó
# al revés: "Secretar" matchea 4 columnas, "Polic" 3 y "Alcald" 3, así que
# el verificador reportaba AMBIGUO donde el loader —con los nombres
# completos— encuentra exactamente una. Importar es la única forma de que
# los dos no se separen.
CONFIANZA_COLUMNAS_ID = [
    ("localidad", FRAGMENTOS_ID_CONFIANZA["localidad"]),
    ("rango de edad", FRAGMENTOS_ID_CONFIANZA["edad"]),
    ("género", FRAGMENTOS_ID_CONFIANZA["genero"]),
    ("nivel educativo", FRAGMENTOS_ID_CONFIANZA["nivel_educativo"]),
]
CONFIANZA_ACTORES = list(_FRAGMENTOS_ACTORES_CONFIANZA)

# --- Proyecciones DANE-SDP (marginal territorial) ------------------------

# Dos publicaciones oficiales distintas, las dos válidas:
#   - anexo .xlsx de DANE, nov-2021, base Censo 2018 ("proyeccion" en el nombre)
#   - .csv de Datos Abiertos, ago-2025, Contrato 500 de 2025 DANE+SDP+RMBC
#     (el archivo se llama osb_demografia-poblacion-localidad.csv, sin la
#     palabra "proyeccion", de ahí las dos alternativas del patrón)
PROYECCIONES_PATRON_ARCHIVO = re.compile(r"proyeccion|demografia-poblacion", re.IGNORECASE)
PROYECCIONES_HOJA = "Localidades"
PROYECCIONES_FILA_ENCABEZADO = 11   # las 11 primeras son título y notas
PROYECCIONES_ANIO_POR_DEFECTO = 2025
PROYECCIONES_CSV_SEPARADOR = ";"
PROYECCIONES_CSV_ENCODING = "utf-8"
PROYECCIONES_COD_BOGOTA = 0         # fila agregada; excluirla o se cuenta doble
MARGINAL_SALIDA = "marginal_localidad_18mas.csv"

ENCODINGS_CANDIDATOS = ["latin-1", "cp850", "utf-8", "utf-8-sig"]
SEPARADORES_CANDIDATOS = [";", ",", "\t", "|"]


# =========================================================================
# utilidades compartidas
# =========================================================================


def detectar_formato(path: Path) -> tuple[str, str]:
    """
    Devuelve (encoding, separador) probando combinaciones y quedándose con
    la que produce más columnas.

    Una primera versión contaba apariciones del separador en la primera
    línea con `str.count()`. Contra el archivo real de confianza eso elige
    la coma, porque los enunciados de las preguntas están llenos de comas
    ("En una escala del 1 al 5, donde 1 significa...") y van entre
    comillas: 54 comas contra 30 punto y comas en los primeros 6 KB. El
    archivo se parseaba entonces como UNA sola columna gigante, y —peor—
    la verificación de abajo daba OK, porque todos los fragmentos estaban
    dentro de ese nombre de columna monstruoso.

    La cuenta ahora la hace el propio parser de pandas, que respeta las
    comillas, así que un separador que aparece solo dentro de campos
    citados ya no gana.
    """
    mejor = None
    for encoding in ENCODINGS_CANDIDATOS:
        for sep in SEPARADORES_CANDIDATOS:
            try:
                n_columnas = len(pd.read_csv(
                    path, sep=sep, encoding=encoding, nrows=5, engine="python"
                ).columns)
            except (UnicodeDecodeError, LookupError, ValueError, pd.errors.ParserError):
                continue
            if mejor is None or n_columnas > mejor[2]:
                mejor = (encoding, sep, n_columnas)
        if mejor and mejor[2] > 1:
            # latin-1 decodifica cualquier byte, así que si ya funcionó no
            # tiene sentido seguir probando encodings más estrictos.
            break

    if mejor is None or mejor[2] <= 1:
        raise SystemExit(
            f"No se pudo determinar el formato de {path.name}: con ningún "
            f"encoding/separador probado aparece más de una columna."
        )
    return mejor[0], mejor[1]


def leer_encabezado(path: Path) -> tuple[list[str], str, str]:
    """Nombres de columna sin cargar el archivo completo."""
    encoding, sep = detectar_formato(path)
    header = pd.read_csv(path, sep=sep, encoding=encoding, nrows=0)
    return list(header.columns), encoding, sep


def resolver_entrada(nombre: str) -> Path:
    path = DIR_RAW / nombre
    if not path.exists():
        raise SystemExit(
            f"No existe {path}.\n"
            f"Colocá el archivo en {DIR_RAW} (esa carpeta va en .gitignore, "
            "así que no se versiona: por eso este script sí tiene que estarlo)."
        )
    return path


# =========================================================================
# modo: inspeccionar
# =========================================================================


def cmd_inspeccionar(nombre: str) -> int:
    path = resolver_entrada(nombre)
    columnas, encoding, sep = leer_encabezado(path)

    destino = DIR_RAW / f"_columnas_{path.stem}.txt"
    with open(destino, "w", encoding="utf-8") as f:
        f.write(f"# {path.name}\n# encoding={encoding} separador={sep!r}\n")
        f.write(f"# {len(columnas)} columnas\n\n")
        for i, c in enumerate(columnas):
            f.write(f"{i}\t{c}\n")

    print(f"{path.name}: {len(columnas)} columnas (encoding={encoding}, sep={sep!r})")
    print(f"Lista completa escrita en {destino}")
    candidatas = [c for c in columnas if PATRON_FACTOR_EXPANSION.search(c)]
    if candidatas:
        print(f"Posibles factores de expansión: {candidatas}")
    return 0


# =========================================================================
# modo: multiproposito
# =========================================================================


def cmd_multiproposito(columna_factor: str | None) -> int:
    path = resolver_entrada(EM_ENTRADA)
    columnas_disponibles, encoding, sep = leer_encabezado(path)
    print(f"Leyendo {path.name} (encoding={encoding}, separador={sep!r}, "
          f"{len(columnas_disponibles)} columnas)")

    faltantes = [c for c in COLUMNAS_EM if c not in columnas_disponibles]
    if faltantes:
        print(f"ERROR: no se encontraron estas columnas: {faltantes}")
        print("Corré 'inspeccionar em2021.csv' para ver la lista completa.")
        return 1

    columnas_a_extraer = list(COLUMNAS_EM)

    # --- factor de expansión ---
    if columna_factor:
        if columna_factor not in columnas_disponibles:
            print(f"ERROR: la columna '{columna_factor}' no existe en {path.name}.")
            return 1
        columnas_a_extraer.append(columna_factor)
        print(f"Factor de expansión: usando '{columna_factor}' (indicado a mano)")
    else:
        candidatas = [c for c in columnas_disponibles if PATRON_FACTOR_EXPANSION.search(c)]
        if len(candidatas) == 1:
            columna_factor = candidatas[0]
            columnas_a_extraer.append(columna_factor)
            print(f"Factor de expansión: detectado '{columna_factor}'")
        elif len(candidatas) > 1:
            print(f"ERROR: hay varias columnas candidatas a factor de expansión: {candidatas}")
            print("Elegí una con --factor NOMBRE. No se adivina: usar el ponderador "
                  "equivocado sesga la población entera.")
            return 1
        else:
            print()
            print("=" * 70)
            print("ADVERTENCIA: no se encontró ninguna columna de factor de expansión.")
            print("El extracto se genera igual, pero SIN ponderador, y la muestra")
            print("heredará el sobre-muestreo de localidades pequeñas propio del")
            print("diseño de Multipropósito (ver DATA_INVENTORY.md sección 4).")
            print("Corré 'inspeccionar em2021.csv' y revisá la lista de columnas:")
            print("el ponderador puede llamarse distinto de lo que busca el patrón.")
            print("=" * 70)
            print()

    # --- extracción por chunks, escribiendo incrementalmente ---
    destino = DIR_RAW / EM_SALIDA
    filas = 0
    valores_estrato: set = set()

    with open(destino, "w", encoding="utf-8", newline="") as salida:
        for i, chunk in enumerate(pd.read_csv(
            path, sep=sep, encoding=encoding, usecols=columnas_a_extraer,
            chunksize=CHUNK, low_memory=False,
        )):
            chunk = chunk[columnas_a_extraer]  # orden estable entre chunks
            chunk.to_csv(salida, index=False, header=(i == 0))
            filas += len(chunk)
            valores_estrato.update(float(v) for v in chunk["NVCBP11AA"].dropna().unique())
            print(f"  {filas:,} filas...", end="\r", flush=True)

    print(f"  {filas:,} filas procesadas." + " " * 20)

    # --- chequeo de sanidad: el control que originó la versión v2 ---
    if valores_estrato and max(valores_estrato) > 20:
        print()
        print(f"ADVERTENCIA: NVCBP11AA tiene valores fuera de rango "
              f"(máximo {max(valores_estrato)}). Eso es la firma de haber tomado "
              f"un código de muestreo en vez del estrato socioeconómico. "
              f"NO usar este extracto sin revisar.")
    else:
        legibles = sorted(int(v) if float(v).is_integer() else v for v in valores_estrato)
        print(f"Chequeo de estrato OK: valores en {legibles}")
        codigos_no_respuesta = [v for v in legibles if v > 6]
        if codigos_no_respuesta:
            print(f"  Nota: {codigos_no_respuesta} son códigos de no-respuesta de "
                  "Multipropósito, no estratos. Hoy el pipeline los deja pasar como "
                  "si fueran ordinales (ver POPULATION_SPECIFICATION.md 8.6).")

    print(f"\nListo: {destino} ({filas:,} filas, {len(columnas_a_extraer)} columnas)")
    if columna_factor is None:
        print("Recordá: este extracto NO trae factor de expansión.")
    return 0


# =========================================================================
# modo: confianza
# =========================================================================


def cmd_confianza(nombre: str | None) -> int:
    if nombre:
        path = resolver_entrada(nombre)
    else:
        # Se excluyen los archivos que este mismo script escribe (prefijo "_"):
        # el reporte de una corrida anterior se llama igual que el dato y
        # aparecía como segundo candidato.
        candidatos = [p for p in DIR_RAW.glob("*")
                      if p.is_file()
                      and not p.name.startswith("_")
                      and p.suffix.lower() in {".csv", ".xlsx", ".xls", ".tsv"}
                      and CONFIANZA_PATRON_ARCHIVO.search(p.name)]
        if not candidatos:
            print(f"No se encontró ningún archivo con 'confianza' en el nombre "
                  f"dentro de {DIR_RAW}.")
            print(f"Archivos presentes: {[p.name for p in DIR_RAW.iterdir() if p.is_file()]}")
            print("Pasá el nombre a mano con --archivo NOMBRE.csv")
            return 1
        if len(candidatos) > 1:
            print(f"Hay varios candidatos: {[p.name for p in candidatos]}. "
                  "Elegí uno con --archivo.")
            return 1
        path = candidatos[0]

    # Se lee con los parámetros que usa loader.py, NO con autodetección:
    # el objetivo es predecir qué va a ver el loader, y si el verificador
    # abre el archivo de otra forma puede llegar a otra conclusión.
    encoding, sep = CONFIANZA_ENCODING, CONFIANZA_SEPARADOR
    df = pd.read_csv(path, sep=sep, encoding=encoding)
    columnas = list(df.columns)
    print(f"{path.name}: {len(columnas)} columnas, {len(df):,} filas "
          f"(leído como lo lee loader.py: encoding={encoding}, sep={sep!r})")

    if len(columnas) <= 1:
        print(f"\nERROR: con sep={sep!r} el archivo queda en una sola columna. "
              "El separador real es otro, y loader.py fallaría igual.")
        detectado = detectar_formato(path)
        print(f"La autodetección sugiere encoding={detectado[0]}, sep={detectado[1]!r}. "
              "Ajustar CONFIANZA_SEPARADOR/CONFIANZA_ENCODING en loader.py, o "
              "reexportar el archivo.")
        return 1

    # Deliberadamente NO se compara contra la autodetección. Con sep=','
    # este archivo produce 232 "columnas" (parte los enunciados por sus
    # comas internas) contra las 144 reales, así que un chequeo del tipo
    # "más columnas = mejor formato" avisaría sobre un archivo que está
    # perfectamente bien. Un verificador que grita en falso desgasta igual
    # que uno que calla: la única señal que importa acá es la de arriba,
    # que el archivo no quede en una sola columna.
    print()

    problemas = []
    lineas_reporte = [
        f"# Verificación del donante de opinión",
        f"archivo: {path.name}",
        f"encoding detectado: {encoding}",
        f"separador detectado: {sep!r}",
        f"filas: {len(df)}",
        f"columnas: {len(columnas)}",
        "",
        "## Columnas de identificación que busca loader.py",
    ]

    for etiqueta, fragmentos in CONFIANZA_COLUMNAS_ID:
        halladas = _buscar_columna(columnas, fragmentos)
        if len(halladas) == 1:
            estado = "OK"
        elif halladas:
            # loader.py toma col[0] sin avisar: no lo rompe, pero puede
            # estar leyendo la columna equivocada.
            estado = "AMBIGUA"
            problemas.append(f"{etiqueta}: {len(halladas)} columnas coinciden; "
                             f"loader.py tomaría '{halladas[0][:60]}'")
        else:
            estado = "NO ENCONTRADA"
            problemas.append(f"{etiqueta}: sin columna — loader.py lanzaría ValueError")
        print(f"  [{estado:14s}] {etiqueta}: {[c[:60] for c in halladas] if halladas else '-'}")
        lineas_reporte.append(f"- {etiqueta}: [{estado}] {halladas}")

    print("\n## Actores del núcleo de confianza")
    lineas_reporte += ["", "## Actores del núcleo de confianza"]
    encontrados = 0
    for fragmento in CONFIANZA_ACTORES:
        halladas = [c for c in columnas if fragmento in c]
        if len(halladas) == 1:
            encontrados += 1
            estado = "OK"
        elif halladas:
            estado = "AMBIGUO"
            problemas.append(f"actor '{fragmento}': matchea {len(halladas)} columnas")
        else:
            estado = "NO ENCONTRADO"
            problemas.append(f"actor '{fragmento}': sin columna")
        etiqueta_corta = halladas[0][-45:] if halladas else "-"
        print(f"  [{estado:14s}] {fragmento!r} -> {etiqueta_corta}")
        lineas_reporte.append(f"- {fragmento!r}: [{estado}] {halladas}")

    print(f"\nActores localizados: {encontrados} de {len(CONFIANZA_ACTORES)}")
    lineas_reporte += ["", f"actores_localizados: {encontrados}/{len(CONFIANZA_ACTORES)}"]

    if encontrados and encontrados < len(CONFIANZA_ACTORES):
        print("ATENCIÓN: loader.py promediaría solo los actores localizados y seguiría "
              "adelante con un warning. El índice de confianza resultante NO sería "
              "comparable con el de una corrida donde se localicen todos "
              "(ver POPULATION_SPECIFICATION.md 8.4).")

    destino = DIR_RAW / f"_verificacion_{path.stem}.txt"
    destino.write_text("\n".join(lineas_reporte), encoding="utf-8")
    print(f"\nReporte escrito en {destino}")

    if problemas:
        print(f"\n{len(problemas)} problema(s) a resolver antes de correr el hot-deck:")
        for p in problemas:
            print(f"  - {p}")
        return 1

    print("\nTodo en orden: loader.py debería leer este archivo sin ajustes.")
    return 0


# =========================================================================


def _normalizar(s: str) -> str:
    """Minúsculas sin tildes, para cruzar nombres de localidad entre fuentes."""
    import unicodedata
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower().strip()


def _cruzar_nombres_localidad(nombres: pd.Series) -> tuple[pd.Series, list[str]]:
    """
    Lleva los nombres de localidad de una fuente externa a los nombres
    canónicos que usan el receptor y `validar_agentes`.

    Hace falta porque las fuentes no se ponen de acuerdo: el anexo de 2021
    escribe "Ciudad Bolivar" sin tilde. Sin normalizar, el marginal no cruza
    con la población y el error no aparece acá sino después, al ponderar,
    disfrazado de localidades con peso 0.
    """
    canon = {_normalizar(n): n for n in LOCALIDADES_VALIDAS_BOGOTA}
    cruzados = nombres.map(lambda n: canon.get(_normalizar(n)))
    return cruzados, nombres[cruzados.isna()].tolist()


def _marginal_desde_anexo_2021(path: Path, anio: int, edad_minima: int) -> pd.DataFrame:
    """
    Anexo DANE de noviembre de 2021 (.xlsx), base Censo 2018.

    Hoja `Localidades`, 11 filas de título antes del encabezado, una columna
    por sexo y edad simple (`Hombres_0` … `Total_100 y más`).
    """
    df = pd.read_excel(path, sheet_name=PROYECCIONES_HOJA, header=PROYECCIONES_FILA_ENCABEZADO)
    df = df[df["COD_LOC"].notna()]

    anios = sorted(int(a) for a in df["AÑO"].unique())
    if anio not in anios:
        raise ValueError(f"El año {anio} no está en el anexo. Disponibles: {anios[0]}-{anios[-1]}.")

    # AREA="Total" suma cabecera urbana + centros poblados y rural disperso.
    # Importa para Sumapaz, que es casi enteramente rural: con "Cabecera
    # Municipal" quedaría en cero.
    d = df[(df["AÑO"] == anio) & (df["AREA"] == "Total")].copy()
    if len(d) != 20:
        raise ValueError(f"Se esperaban 20 localidades para {anio}, se encontraron {len(d)}.")

    cols_edad = [c for c in d.columns
                 if str(c).startswith("Total_")
                 and (str(c).split("_", 1)[1].isdigit() and int(str(c).split("_", 1)[1]) >= edad_minima
                      or str(c) == "Total_100 y más")]
    d["poblacion"] = d[cols_edad].sum(axis=1)
    d["localidad"], sin_cruce = _cruzar_nombres_localidad(d["NOM_LOC"])
    if sin_cruce:
        raise ValueError(f"Localidades que no cruzan con las de D12: {sin_cruce}")
    return d[["COD_LOC", "localidad", "poblacion"]]


def _marginal_desde_csv_2025(path: Path, anio: int, edad_minima: int) -> pd.DataFrame:
    """
    Revisión de agosto de 2025 (.csv de Datos Abiertos Bogotá): Contrato
    Interadministrativo 500 de 2025 — DANE, SDP y Región Metropolitana
    Bogotá Cundinamarca.

    Formato largo: una fila por año × localidad × sexo × edad simple.
    `CODIGO_LOCALIDAD = 0` es la fila agregada de Bogotá y hay que
    excluirla, o cada persona se cuenta dos veces.
    """
    d = pd.read_csv(path, sep=PROYECCIONES_CSV_SEPARADOR,
                    encoding=PROYECCIONES_CSV_ENCODING, low_memory=False)

    faltan = {"ANO", "CODIGO_LOCALIDAD", "NOMBRE_LOCALIDAD", "EDAD", "POBLACION"} - set(d.columns)
    if faltan:
        raise ValueError(f"A {path.name} le faltan las columnas {sorted(faltan)}.")

    anios = sorted(int(a) for a in d["ANO"].unique())
    if anio not in anios:
        raise ValueError(f"El año {anio} no está en el archivo. Disponibles: {anios[0]}-{anios[-1]}.")

    sel = d[(d["ANO"] == anio) & (d["EDAD"] >= edad_minima)]
    agregado = int(sel.loc[sel["CODIGO_LOCALIDAD"] == PROYECCIONES_COD_BOGOTA, "POBLACION"].sum())
    sel = sel[sel["CODIGO_LOCALIDAD"] != PROYECCIONES_COD_BOGOTA]

    marg = (sel.groupby(["CODIGO_LOCALIDAD", "NOMBRE_LOCALIDAD"], as_index=False)["POBLACION"].sum()
               .rename(columns={"CODIGO_LOCALIDAD": "COD_LOC",
                                "NOMBRE_LOCALIDAD": "localidad",
                                "POBLACION": "poblacion"}))
    if len(marg) != 20:
        raise ValueError(f"Se esperaban 20 localidades para {anio}, se encontraron {len(marg)}.")

    # El archivo trae su propio total de Bogotá. Que cuadre con la suma de
    # las 20 localidades es la comprobación más barata de que el filtro de
    # edad y la exclusión del agregado están bien.
    if agregado and abs(int(marg["poblacion"].sum()) - agregado) > 0:
        raise ValueError(
            f"La suma de localidades ({marg['poblacion'].sum():,}) no coincide con la fila "
            f"agregada de Bogotá ({agregado:,}). Revisar el filtro de edad y el código 0."
        )

    marg["localidad"], sin_cruce = _cruzar_nombres_localidad(marg["localidad"])
    if sin_cruce:
        raise ValueError(f"Localidades que no cruzan con las de D12: {sin_cruce}")
    return marg


def _elegir_fuente_proyecciones(nombre: str | None) -> tuple[Path, str] | None:
    """
    Devuelve (ruta, vintage) de la fuente de proyecciones a usar.

    Hay dos vintages en circulación y NO son intercambiables: la revisión de
    2025 mueve las participaciones por localidad 0,037 en distancia L1
    respecto de la proyección de 2021 —del orden del sesgo muestral que D14
    dejó— y lo hace de forma sistemática, quitándole peso al norte y
    dándoselo al sur. Como esa dirección está correlacionada con estrato, la
    elección de vintage cambia la composición de la población sintética, no
    solo su reparto territorial. Por eso se prefiere la más reciente y se
    deja dicho cuál se usó.
    """
    if nombre:
        path = resolver_entrada(nombre)
        return path, ("2025" if path.suffix.lower() == ".csv" else "2021")

    candidatos = [p for p in DIR_RAW.glob("*")
                  if p.is_file() and not p.name.startswith("_")
                  and PROYECCIONES_PATRON_ARCHIVO.search(p.name)]
    csv_2025 = [p for p in candidatos if p.suffix.lower() == ".csv"]
    xlsx_2021 = [p for p in candidatos if p.suffix.lower() in {".xlsx", ".xls"}]

    if len(csv_2025) == 1:
        return csv_2025[0], "2025"
    if len(csv_2025) > 1:
        print(f"Hay {len(csv_2025)} CSV de proyecciones en {DIR_RAW}: "
              f"{[p.name for p in csv_2025]}. Usá --archivo.")
        return None
    if len(xlsx_2021) == 1:
        return xlsx_2021[0], "2021"
    print(f"Se esperaba un archivo de proyecciones en {DIR_RAW}, hay "
          f"{len(candidatos)}: {[p.name for p in candidatos]}. Usá --archivo.")
    return None


def cmd_proyecciones(nombre: str | None, anio: int, edad_minima: int) -> int:
    """
    Construye el marginal territorial: población adulta por localidad.

    Es el objetivo contra el cual se mide el muestreo PPS de D14. Sin él, la
    muestra hereda el sobre-muestreo de localidades pequeñas propio del
    diseño de Multipropósito.

    Lee cualquiera de las dos publicaciones oficiales —el anexo .xlsx de
    2021 o el .csv de la revisión de 2025— y prefiere la segunda cuando
    están las dos.
    """
    elegida = _elegir_fuente_proyecciones(nombre)
    if elegida is None:
        return 1
    path, vintage = elegida

    lector = _marginal_desde_csv_2025 if vintage == "2025" else _marginal_desde_anexo_2021
    try:
        marg = lector(path, anio, edad_minima)
    except ValueError as e:
        print(f"ERROR leyendo {path.name}: {e}")
        if "no cruzan" in str(e):
            print(f"Nombres esperados: {sorted(LOCALIDADES_VALIDAS_BOGOTA)}")
        return 1

    marg = marg.copy()
    marg["COD_LOC"] = marg["COD_LOC"].astype(int)
    marg["poblacion"] = marg["poblacion"].astype(int)
    marg["share"] = marg["poblacion"] / marg["poblacion"].sum()
    marg = marg.sort_values("poblacion", ascending=False).reset_index(drop=True)

    DIR_EXTERNAL.mkdir(parents=True, exist_ok=True)
    destino = DIR_EXTERNAL / MARGINAL_SALIDA

    # Si ya había un marginal, decir cuánto se mueve. Un marginal que cambia
    # en silencio invalida cualquier comparación con corridas anteriores.
    previo = None
    if destino.exists():
        try:
            previo = pd.read_csv(destino)
        except Exception:
            previo = None

    marg.to_csv(destino, index=False)

    origen = (f"{path.name} (revisión 2025)" if vintage == "2025"
              else f"{path.name}, hoja '{PROYECCIONES_HOJA}', AREA=Total (anexo 2021)")
    print(f"Fuente: {origen}, año {anio}")
    print(f"Población {edad_minima}+ de Bogotá: {marg.poblacion.sum():,}\n")
    print(marg.assign(share=(marg["share"]*100).round(3)).to_string(index=False))

    if previo is not None and {"COD_LOC", "share"} <= set(previo.columns):
        c = previo[["COD_LOC", "share"]].merge(marg[["COD_LOC", "share"]],
                                               on="COD_LOC", suffixes=("_antes", "_ahora"))
        l1 = float((c["share_ahora"] - c["share_antes"]).abs().sum())
        print(f"\nCambio respecto del marginal anterior: distancia L1 = {l1:.4f}")
        if l1 > 0.01:
            print("  Es un cambio material: las corridas hechas contra el marginal anterior "
                  "no son directamente comparables con las que vengan ahora.")

    print(f"\nMarginal escrito en {destino}")
    return 0


def cmd_estado() -> int:
    """
    Qué hay en data/raw/ y qué corresponde correr. Es lo que pasa si se
    ejecuta el script sin argumentos — por ejemplo con el botón Run de
    VS Code, que no pasa ninguno. Antes eso daba un error de argparse que
    no ayudaba en nada; mostrar el estado es más útil y, sobre todo, no
    dispara por accidente una extracción de 1,25 GB.
    """
    print(f"data/raw/  ({DIR_RAW})\n")
    if not DIR_RAW.exists():
        print("  (la carpeta no existe)")
        return 1

    archivos = sorted(p for p in DIR_RAW.iterdir() if p.is_file() and not p.name.startswith("_"))
    if not archivos:
        print("  (vacía)")

    hay_em = hay_extracto = hay_confianza = hay_proy = False
    for p in archivos:
        mb = p.stat().st_size / 1e6
        if p.name == EM_ENTRADA:
            etiqueta, hay_em = "microdato Multipropósito (receptor, origen)", True
        elif p.name == EM_SALIDA:
            etiqueta, hay_extracto = "extracto del receptor", True
        elif CONFIANZA_PATRON_ARCHIVO.search(p.name):
            etiqueta, hay_confianza = "donante de opinión (confianza institucional)", True
        elif PROYECCIONES_PATRON_ARCHIVO.search(p.name):
            etiqueta, hay_proy = "proyecciones DANE-SDP (marginal territorial)", True
        else:
            etiqueta = "-"
        print(f"  {p.name[:52]:54s} {mb:8.1f} MB   {etiqueta}")

    print("\nQué corresponde correr:")
    if hay_em:
        estado = "regenera el extracto (incluye el factor de expansión)" if hay_extracto \
            else "genera el extracto del receptor"
        print(f"  python {ATAJO} multiproposito     -> {estado}")
    else:
        print(f"  falta {EM_ENTRADA} para poder extraer el receptor")
    if hay_confianza:
        print(f"  python {ATAJO} confianza          -> verifica que loader.py pueda leer el donante")
    else:
        print("  falta el archivo de confianza institucional (donante de opinión)")
    if hay_proy:
        marginal = DIR_EXTERNAL / MARGINAL_SALIDA
        estado = "ya generado" if marginal.exists() else "PENDIENTE"
        print(f"  python {ATAJO} proyecciones       -> marginal territorial 18+ por localidad ({estado})")
    else:
        print("  falta el anexo de proyecciones DANE-SDP (marginal territorial)")
    print(f"  python {ATAJO} inspeccionar ARCHIVO  -> vuelca los nombres de columna a un .txt")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Prepara y verifica los archivos crudos de data/raw/. "
                    "Sin argumentos, muestra el estado de esa carpeta.")
    sub = parser.add_subparsers(dest="modo")

    p_em = sub.add_parser("multiproposito", help="extrae las columnas del receptor de em2021.csv")
    p_em.add_argument("--factor", default=None,
                      help="nombre de la columna de factor de expansión, si la detección automática falla o es ambigua")

    p_conf = sub.add_parser("confianza", help="verifica el archivo donante de confianza institucional")
    p_conf.add_argument("--archivo", default=None, help="nombre del archivo dentro de data/raw/")

    p_proy = sub.add_parser("proyecciones",
                            help="construye el marginal territorial (población adulta por localidad)")
    p_proy.add_argument("--archivo", default=None, help="nombre del anexo dentro de data/raw/")
    p_proy.add_argument("--anio", type=int, default=PROYECCIONES_ANIO_POR_DEFECTO)
    p_proy.add_argument("--edad-minima", type=int, default=18, dest="edad_minima")

    p_ins = sub.add_parser("inspeccionar", help="vuelca los nombres de columna de un archivo de data/raw/")
    p_ins.add_argument("archivo")

    args = parser.parse_args(argv)

    if args.modo is None:
        return cmd_estado()
    if args.modo == "multiproposito":
        return cmd_multiproposito(args.factor)
    if args.modo == "confianza":
        return cmd_confianza(args.archivo)
    if args.modo == "proyecciones":
        return cmd_proyecciones(args.archivo, args.anio, args.edad_minima)
    return cmd_inspeccionar(args.archivo)


if __name__ == "__main__":
    sys.exit(main())
