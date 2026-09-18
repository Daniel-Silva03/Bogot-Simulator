"""
src/population/loader.py

Carga las dos fuentes que necesita el hot-deck (src/population/matching.py):

    - RECEPTOR: Encuesta Multipropósito 2021 (esqueleto demográfico completo)
    - DONANTE: Encuesta de Percepción de Confianza Institucional en Bogotá
      (Veeduría Distrital, 2024-2025) — fuente de la variable de opinión
      fijada en D11 (confianza institucional)

Ambos loaders devuelven un DataFrame en el mismo ESQUEMA ESTÁNDAR que espera
`hot_deck_match`:

    localidad, sexo, edad, estrato, nivel_educativo  [+ opinion_col en el donante]

con `sexo` codificado como "F"/"M" y `nivel_educativo` en la escala 0-5 fijada
en NETWORK_SPECIFICATION.md sección 2 (sin educación formal=0 ... posgrado=5).

------------------------------------------------------------------------
DATA REQUIRED / SUPUESTOS QUE QUEDAN EXPLÍCITOS EN ESTE MÓDULO
(Regla 2 y Principio 3 del prompt maestro — no ocultar, no inventar)
------------------------------------------------------------------------

1. El donante de confianza institucional NO TRAE ESTRATO (ver
   DATA_SPECIFICATION.md, entrada de este dataset — usa ingresos mensuales
   como proxy, con categorización propia no homologable directamente).
   `load_confianza_institucional_donante` devuelve la columna `estrato` con
   NaN en todas las filas, y lo declara explícitamente en el log — NO
   inventa un valor. Quien llame a `hot_deck_match` con este donante debe
   decidir conscientemente: (a) excluir `estrato` de `distance_vars` para
   este donante específico, o (b) usar un donante alternativo que sí lo
   traiga (Bogotá Cómo Vamos, si se consigue microdato), o (c) mapear
   ingresos→estrato con una tabla de homologación — NINGUNA de estas tres
   opciones está decidida todavía; es una A0X nueva que debe registrarse en
   PROJECT_CONTEXT.md si se llega a resolver.

2. El donante trae `edad` en RANGOS (18-25, 26-35, 36-45, 46-55, 56+), no
   continua. Este loader la convierte al PUNTO MEDIO de cada rango (56+ se
   trata como 65, punto medio asumido de la cola abierta) para poder
   calcular distancia euclidiana contra la edad continua del receptor. Esto
   es un SUPUESTO DE IMPLEMENTACIÓN, no un hecho — introduce error de
   redondeo en el emparejamiento por edad que no existía en el diseño
   original de POPULATION_SPECIFICATION.md (que asumía variables puente
   comparables directamente). Alternativa no implementada: convertir la
   edad continua del receptor a los mismos rangos y tratar edad como
   variable de emparejamiento EXACTO en vez de distancia — pendiente de
   decidir con Daniel.

3. La pregunta núcleo de confianza institucional mide 8 actores por
   separado. (DATA_SPECIFICATION.md dice "7" pero enumera 8; verificado el
   15/09/2026 contra Base_EncuestaConfianza_2024-2025.csv, publicado por la
   Veeduría en Datos Abiertos Bogotá: son 8, y los 8 fragmentos de
   `_FRAGMENTOS_ACTORES_CONFIANZA` localizan exactamente una columna cada
   uno.) Este loader devuelve, por defecto, el PROMEDIO de los 8 como
   índice compuesto (`confianza_institucional`),
   consistente con la nota "pendiente dentro de esta decisión" de D11 en
   PROJECT_CONTEXT.md — sigue sin resolverse si debería modelarse por
   institución en vez de un índice compuesto.

4. Filtro de adultos: ambas fuentes se filtran a población adulta (18+),
   consistente con que la encuesta de confianza institucional solo
   encuestó adultos.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Multipropósito 2021 — receptor
# ---------------------------------------------------------------------------

# Mapa de recodificación de NPCHP4 (15 categorías del diccionario EM2021) a
# la escala 0-5 fijada en NETWORK_SPECIFICATION.md sección 2.
MAPA_NIVEL_EDUCATIVO_MULTIPROPOSITO = {
    1: 0, 2: 0,           # ninguno, preescolar -> sin educación formal
    3: 1,                  # básica primaria
    4: 2, 5: 2,            # básica secundaria, media -> secundaria
    6: 3, 7: 3,            # técnico, tecnológico
    8: 4, 9: 4,             # universitaria incompleta/completa
    10: 5, 11: 5, 12: 5, 13: 5, 14: 5, 15: 5,  # especialización..doctorado -> posgrado
}

MAPA_SEXO_MULTIPROPOSITO = {1: "M", 2: "F"}

# El nombre del ponderador cambia entre operaciones estadísticas del DANE
# (FEX_C, F_EXP, FACTOR_EXPANSION...). Se busca por patrón. Definido aquí
# porque este es el módulo que lo consume; `extraer_columnas_em2021.py` lo
# importa de acá para que haya una sola fuente de verdad.
PATRON_FACTOR_EXPANSION = re.compile(
    r"(fex|f_?exp|factor.*expan|expansion|ponderad|peso)", re.IGNORECASE
)
NOMBRE_FACTOR_ESTANDAR = "factor_expansion"


def load_multiproposito_receptor(
    path: str | Path,
    encoding: str = "latin-1",
    solo_bogota: bool = True,
    edad_minima: int = 18,
) -> pd.DataFrame:
    """
    Carga el extracto de Multipropósito 2021 (columnas: NOMBRE_LOCALIDAD,
    SEXO, NPCEP4, ESTRATO2021, NPCHP4 — ver extraer_columnas_em2021_completo.py)
    y lo lleva al esquema estándar del receptor.

    Parameters
    ----------
    path : ruta al CSV extraído (NO al em2021.csv completo de 1.25 GB).
    solo_bogota : si True (default), descarta registros de municipios de
        Cundinamarca (localidad nula/no aplica en Multipropósito).
    edad_minima : filtro de población adulta, consistente con el donante.

    Returns
    -------
    DataFrame con columnas: agent_id, localidad, sexo, edad, estrato,
    nivel_educativo — listo para pasar como `receptor` a hot_deck_match.
    """
    df = pd.read_csv(path, encoding=encoding, low_memory=False)

    columnas_esperadas = ["NOMBRE_LOCALIDAD", "SEXO", "NPCEP4", "NVCBP11AA", "NPCHP4"]
    faltantes = [c for c in columnas_esperadas if c not in df.columns]
    if faltantes:
        raise ValueError(
            f"Faltan columnas en {path}: {faltantes}. "
            "Regenerar con: python src/population/extraer_columnas_em2021.py multiproposito "
            "(NOTA: una versión temprana del extracto usaba ESTRATO2021, que es un "
            "código de muestreo, no el estrato socioeconómico — la variable correcta "
            "es NVCBP11AA)"
        )

    # NOMBRE_LOCALIDAD puede venir con mojibake UTF-8-leído-como-latin-1
    # (mismo patrón encontrado al procesar este archivo la primera vez)
    def _fix_mojibake(s):
        if pd.isna(s):
            return None
        try:
            return s.encode("latin-1").decode("utf-8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            return s

    df["localidad"] = df["NOMBRE_LOCALIDAD"].apply(_fix_mojibake)

    n_total = len(df)
    if solo_bogota:
        df = df[df["localidad"].notna()].copy()
    n_bogota = len(df)
    logger.info("Multipropósito: %d de %d registros son de Bogotá D.C.", n_bogota, n_total)

    df = df[df["NPCEP4"] >= edad_minima].copy()
    logger.info("Multipropósito: %d registros adultos (%d+)", len(df), edad_minima)

    df["sexo"] = df["SEXO"].map(MAPA_SEXO_MULTIPROPOSITO)
    n_sexo_nulo = df["sexo"].isna().sum()
    if n_sexo_nulo:
        logger.warning("%d registros sin sexo válido, se descartan.", n_sexo_nulo)
        df = df[df["sexo"].notna()]

    df["nivel_educativo"] = df["NPCHP4"].map(MAPA_NIVEL_EDUCATIVO_MULTIPROPOSITO)
    n_edu_nulo = df["nivel_educativo"].isna().sum()
    if n_edu_nulo:
        logger.warning(
            "%d registros sin nivel educativo válido (posible no informa), se descartan.",
            n_edu_nulo,
        )
        df = df[df["nivel_educativo"].notna()]

    # DI-P3 (cierra A17). NVCBP11AA toma 0-6 pero también 8 y 9, que en
    # Multipropósito son códigos de NO RESPUESTA, no estratos. Se descartan
    # acá, en el origen, y no se parchean aguas abajo.
    #
    # Se intentó primero neutralizarlos en la distancia homofílica y las dos
    # formas de hacerlo introducen un sesgo propio: omitir la componente y
    # reescalar les SUBE el grado (la distancia tiene más varianza y el
    # kernel exponencial es convexo: grado 10,1 contra 4,9 en la prueba);
    # imputar la media se lo BAJA (grado 0,6 contra 5,2), porque `estrato`
    # es discreta y la media cae entre dos niveles, así que el agente nunca
    # queda a distancia 0 de nadie y el kernel premia a los vecinos exactos.
    #
    # El 0 SÍ se conserva: la ECP lo etiqueta "conexión ilegal - pirata",
    # que es una categoría real y no una no-respuesta.
    CODIGOS_NO_RESPUESTA_ESTRATO = (8, 9)
    sin_estrato = df["NVCBP11AA"].isin(CODIGOS_NO_RESPUESTA_ESTRATO)
    if sin_estrato.any():
        logger.warning(
            "%d registros con estrato %s (códigos de no-respuesta de "
            "Multipropósito, no estratos), se descartan — A17/DI-P3.",
            int(sin_estrato.sum()), sorted(df.loc[sin_estrato, "NVCBP11AA"].unique()))
        df = df[~sin_estrato]

    n_estrato_nulo = df["NVCBP11AA"].isna().sum()
    if n_estrato_nulo:
        logger.warning(
            "%d registros sin estrato válido (posible no informa/no aplica), se descartan.",
            n_estrato_nulo,
        )
        df = df[df["NVCBP11AA"].notna()]

    df = df.rename(columns={"NPCEP4": "edad", "NVCBP11AA": "estrato"})
    df = df.reset_index(drop=True)
    df["agent_id"] = df.index

    columnas_salida = ["agent_id", "localidad", "sexo", "edad", "estrato", "nivel_educativo"]

    # Factor de expansión, si el extracto lo trae. No se usa aquí: se
    # arrastra para que quien muestree los N agentes del prototipo pueda
    # hacerlo con probabilidad proporcional al peso en vez de uniformemente.
    # Sin esto, el extracto puede traer el ponderador y el receptor lo
    # descartaría en silencio, que es justo lo que pasaba antes.
    # Cómo se usa (o si se usa) sigue siendo A16, sin decidir.
    candidatas_factor = [c for c in df.columns if PATRON_FACTOR_EXPANSION.search(str(c))]
    if len(candidatas_factor) == 1:
        df = df.rename(columns={candidatas_factor[0]: NOMBRE_FACTOR_ESTANDAR})
        columnas_salida.append(NOMBRE_FACTOR_ESTANDAR)
        logger.info(
            "Factor de expansión '%s' encontrado y arrastrado como '%s'.",
            candidatas_factor[0], NOMBRE_FACTOR_ESTANDAR,
        )
    elif len(candidatas_factor) > 1:
        logger.warning(
            "Hay varias columnas candidatas a factor de expansión (%s). No se "
            "arrastra ninguna: usar el ponderador equivocado sesgaría la "
            "población entera. Dejar en el extracto solo la correcta.",
            candidatas_factor,
        )
    else:
        logger.warning(
            "El extracto NO trae factor de expansión. La muestra heredará el "
            "sobre-muestreo de localidades pequeñas propio del diseño de "
            "Multipropósito (ver DATA_INVENTORY.md sección 4). Re-extraer con "
            "'python src/population/extraer_columnas_em2021.py multiproposito'."
        )

    resultado = df[columnas_salida].copy()
    resultado["nivel_educativo"] = resultado["nivel_educativo"].astype(int)

    # Chequeo de sanidad: el estrato real de Bogotá está en el rango 1-6
    # (excepcionalmente hasta 9 en zonas rurales/sin estratificar). Un valor
    # fuera de ese rango es señal de haber tomado la variable equivocada
    # (ver el error real detectado en esta conversación con ESTRATO2021,
    # que era un código de muestreo de 8 dígitos, no el estrato).
    estratos_validos = resultado["estrato"].dropna()
    if len(estratos_validos) and estratos_validos.max() > 9:
        logger.warning(
            "Los valores de 'estrato' exceden el rango esperado (máx=%s). "
            "Verificar que la columna fuente sea la correcta (NVCBP11AA, "
            "no ESTRATO2021 u otra).",
            estratos_validos.max(),
        )

    logger.info("Receptor final: %d personas listas para matching.", len(resultado))
    return resultado


# ---------------------------------------------------------------------------
# Encuesta de Confianza Institucional (Veeduría Distrital) — donante
# ---------------------------------------------------------------------------

# Crosswalk de localidad: nombres corruptos (cp850 mal decodificado) -> nombre
# normalizado. Confirmado contra el archivo real subido en esta conversación.
CROSSWALK_LOCALIDAD_CONFIANZA = {
    "suba": "Suba", "kennedy": "Kennedy", "engativ": "Engativá", "bosa": "Bosa",
    "ciudad bol\xa1var": "Ciudad Bolívar", "usaqu\x82n": "Usaquén",
    "fontib\xa2n": "Fontibón", "san crist\xa2bal": "San Cristóbal", "usme": "Usme",
    "rafael uribe uribe": "Rafael Uribe Uribe", "puente aranda": "Puente Aranda",
    "tunjuelito": "Tunjuelito", "chapinero": "Chapinero", "teusaquillo": "Teusaquillo",
    "barrios unidos": "Barrios Unidos", "santa fe": "Santa Fe",
    "los m\xa0rtires": "Los Mártires", "antonio nari\xa4o": "Antonio Nariño",
    "la candelaria": "La Candelaria", "sumapaz": "Sumapaz",
}

MAPA_NIVEL_EDUCATIVO_CONFIANZA = {
    "Postgrado (especializaci\xa2n, maestr\xa1a, doctorado)": 5,
    "Educaci\xa2n t\x82cnica o tecnol\xa2gica": 3,
    "Educaci\xa2n universitaria": 4,
    "Educaci\xa2n secundaria": 2,
    "Educaci\xa2n primaria": 1,
    "Sin educaci\xa2n formal": 0,
}


def _mapear_nivel_educativo_confianza(valor: str) -> Optional[int]:
    """Coincidencia por subcadena en vez de texto exacto — más robusta ante
    variaciones de codificación entre exportaciones del formulario (el byte
    exacto de las tildes corruptas cambió incluso entre dos columnas del
    mismo archivo real usado en esta conversación)."""
    if pd.isna(valor):
        return None
    v = str(valor).lower()
    if "primaria" in v:
        return 1
    if "secundaria" in v:
        return 2
    if "cnica" in v or "tecnol" in v:
        return 3
    if "universitaria" in v:
        return 4
    if "postgrado" in v:
        return 5
    if "sin educaci" in v:
        return 0
    return None


def _mapear_edad_media(valor: str) -> Optional[float]:
    """Punto medio del rango, detectado por los dígitos presentes en el
    texto (ver supuesto #2 del docstring del módulo) — robusto ante
    variaciones de redacción/codificación del rango."""
    if pd.isna(valor):
        return None
    v = str(valor)
    if "18" in v and "25" in v:
        return 21.5
    if "26" in v and "35" in v:
        return 30.5
    if "36" in v and "45" in v:
        return 40.5
    if "46" in v and "55" in v:
        return 50.5
    if "56" in v:
        return 65.0
    return None

# Las 8 columnas de confianza institucional por actor (columnas 54-61 del
# CSV real subido en esta conversación, pregunta 9 del cuestionario). Los
# nombres completos son largos (repiten el enunciado de la pregunta); se
# identifican aquí por el fragmento final entre corchetes, que es la parte
# estable ante reexportaciones del formulario. Ver DATA_SPECIFICATION.md
# para la lista de actores institucionales medidos.
_FRAGMENTOS_ACTORES_CONFIANZA = [
    "Secretar\xa1as Distritales",
    "Servidores P\xa3blicos",
    "Alcald\xa1as Locales",
    "Polic\xa1a Metropolitana",
    "Organismos Distritales de Control",
    "Entidades adscritas e institutos",
    "\xc7?rganos de justicia distritales",
    "Comisar\xa1as de Familia",
]


# Fragmentos con los que se localizan las columnas de identificación del
# donante. Verificados el 15/09/2026 contra el archivo publicado
# (Base_EncuestaConfianza_2024-2025.csv, 144 columnas): cada uno matchea
# exactamente una columna.
# Formato del export publicado por la Veeduría. Expuestos como constantes
# para que el verificador de `extraer_columnas_em2021.py confianza` lea el
# archivo con EXACTAMENTE los mismos parámetros que este módulo, en vez de
# autodetectarlos por su cuenta y llegar a otra conclusión.
CONFIANZA_ENCODING = "latin-1"
CONFIANZA_SEPARADOR = ";"

FRAGMENTOS_ID_CONFIANZA: dict[str, list[str]] = {
    "localidad": ["localidad reside"],
    "edad": ["rango de edad"],
    # dos variantes: el byte de la tilde cambia entre exportaciones
    "genero": ["g\x82nero", "genero"],
    "nivel_educativo": ["nivel educativo"],
}


def parsear_marca_temporal(serie: pd.Series) -> pd.Series:
    """
    Convierte la columna `Marca temporal` del export de la Veeduría a
    fechas. Recupera las 5.287 filas, sin descartar ninguna.

    POR QUÉ HACE FALTA ESTO
    -----------------------
    La columna trae tres formatos mezclados, y el patrón de la mezcla
    delata qué le pasó al archivo:

        familia          n      formato              días presentes
        ISO/GMT        649   Y/m/d h:M:S a.m. GMT-5   1-31
        con segundos  2888   m/d/Y H:M:S             13-31  ← solo > 12
        sin segundos  1750   m/d/Y H:M                1-12  ← solo <= 12

    Que la partición entre las dos últimas familias sea exactamente
    "día > 12" contra "día <= 12" es la firma de un round-trip por hoja de
    cálculo: al abrir el CSV, las filas cuyo día cabía como mes fueron
    reinterpretadas como fecha y reescritas sin segundos, y las que no
    cabían quedaron como texto. No es un archivo con dos convenciones:
    es un archivo dañado de forma sistemática.

    La ambigüedad día/mes de la familia "sin segundos" NO se puede
    resolver mirando fila por fila —ningún componente pasa de 12—, pero sí
    en conjunto: su primer componente solo toma los valores {1, 2, 12},
    que son exactamente los meses del trabajo de campo confirmados por las
    otras dos familias, mientras el segundo se reparte por todo 1-12. Por
    lo tanto es m/d/Y, igual que la familia con segundos.

    VERIFICACIÓN INDEPENDIENTE: el reparto por año que produce esta
    función da 2.128 en 2024 y 3.159 en 2025, que son exactamente los
    tamaños que DATA_SPECIFICATION.md documenta para las dos "olas". Dos
    caminos independientes al mismo número.

    Se conserva solo la fecha: la familia "sin segundos" perdió los
    segundos en el round-trip y la hora no se usa para nada.
    """
    s = serie.astype(str).str.strip()
    fecha = s.str.split(" ").str[0]
    es_iso = s.str.contains("GMT", na=False)

    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")
    out[es_iso] = pd.to_datetime(fecha[es_iso], format="%Y/%m/%d", errors="coerce")
    out[~es_iso] = pd.to_datetime(fecha[~es_iso], format="%m/%d/%Y", errors="coerce")

    n_fallos = int(out.isna().sum())
    if n_fallos:
        ejemplos = s[out.isna()].head(3).to_list()
        logger.warning(
            "%d de %d marcas temporales no se pudieron parsear (ej. %s). Si son "
            "muchas, revisar si apareció un cuarto formato.", n_fallos, len(s), ejemplos)
    return out


def _buscar_columna(columnas, fragmentos: list[str]) -> list[str]:
    """Columnas cuyo nombre (en minúsculas) contiene alguno de los
    fragmentos. Expuesto como función para que
    `extraer_columnas_em2021.py confianza` verifique con exactamente el
    mismo criterio que usa este módulo — un verificador más estricto daría
    falsas alarmas y uno más laxo, falsa tranquilidad."""
    return [c for c in columnas if any(f in str(c).lower() for f in fragmentos)]


def _identificar_columnas_confianza(columnas: list[str]) -> list[str]:
    """Encuentra las columnas de confianza por actor buscando el fragmento
    estable dentro del nombre completo de columna (que es largo y repite el
    enunciado de la pregunta en cada una)."""
    encontradas = []
    for fragmento in _FRAGMENTOS_ACTORES_CONFIANZA:
        candidatas = [c for c in columnas if fragmento in c]
        if len(candidatas) == 1:
            encontradas.append(candidatas[0])
        elif len(candidatas) > 1:
            raise ValueError(f"Fragmento '{fragmento}' matchea más de una columna: {candidatas}")
        else:
            logger.warning("No se encontró columna de confianza para: %s", fragmento)
    return encontradas


def load_confianza_institucional_donante(
    path: str | Path,
    encoding: str = CONFIANZA_ENCODING,
    columnas_confianza: Optional[list[str]] = None,
    sep: str = CONFIANZA_SEPARADOR,
    desde: Optional[str] = None,
    hasta: Optional[str] = None,
    incluir_fecha: bool = False,
) -> pd.DataFrame:
    """
    Carga la Encuesta de Confianza Institucional (Veeduría Distrital) y la
    lleva al esquema estándar del donante.

    ADVERTENCIA (ver supuesto #1 del docstring del módulo): la columna
    `estrato` del resultado queda en NaN — este dataset no la trae. No debe
    usarse como variable de distancia sin que quien llama lo decida
    explícitamente (ver hot_deck_match, parámetro distance_vars).

    Parameters
    ----------
    path : ruta al CSV real (delimitado por ';', encoding cp850/latin-1).
    columnas_confianza : lista de nombres de columna a promediar para el
        índice compuesto de confianza institucional. Si no se especifica,
        se usa `COLUMNAS_CONFIANZA_POR_ACTOR` — debe confirmarse contra el
        encabezado real del archivo antes de usar en producción (ver nota
        en el código: los nombres de columna con tildes corruptas son
        frágiles ante cualquier cambio de exportación del formulario).

    Returns
    -------
    DataFrame con columnas: localidad, sexo, edad, estrato (NaN),
    nivel_educativo, confianza_institucional.
    """
    df = pd.read_csv(path, encoding=encoding, sep=sep)
    if len(df.columns) <= 1:
        raise ValueError(
            f"{path} se parseó como {len(df.columns)} columna(s) con sep={sep!r} y "
            f"encoding={encoding!r}. Casi seguro el separador es otro. No se sigue: "
            "con una sola columna, las búsquedas por fragmento darían falsos "
            "positivos (el fragmento aparece dentro del nombre de columna gigante)."
        )

    # Fecha de respuesta. El trabajo de campo de este archivo va del
    # 4-dic-2024 al 9-feb-2025 de forma continua, así que `desde`/`hasta`
    # recortan un tramo de UNA recolección, no seleccionan olas distintas
    # (ver parsear_marca_temporal y EXPERIMENT_1_SPECIFICATION.md).
    df["_fecha_respuesta"] = parsear_marca_temporal(df[df.columns[0]])
    if desde is not None:
        df = df[df["_fecha_respuesta"] >= pd.Timestamp(desde)]
    if hasta is not None:
        df = df[df["_fecha_respuesta"] <= pd.Timestamp(hasta)]
    if desde is not None or hasta is not None:
        logger.info("Confianza institucional: %d registros en el rango de fechas pedido.", len(df))
        if len(df) == 0:
            raise ValueError(
                f"Ningún registro entre {desde} y {hasta}. El trabajo de campo de este "
                "archivo va del 2024-12-04 al 2025-02-09.")

    col_localidad = _buscar_columna(df.columns, FRAGMENTOS_ID_CONFIANZA["localidad"])
    col_edad = _buscar_columna(df.columns, FRAGMENTOS_ID_CONFIANZA["edad"])
    col_genero = _buscar_columna(df.columns, FRAGMENTOS_ID_CONFIANZA["genero"])
    col_niveledu = _buscar_columna(df.columns, FRAGMENTOS_ID_CONFIANZA["nivel_educativo"])

    if not (col_localidad and col_edad and col_genero and col_niveledu):
        raise ValueError(
            "No se pudieron identificar automáticamente las columnas de "
            "localidad/edad/género/nivel educativo. Revisar encabezados: "
            f"{list(df.columns)[:20]}"
        )

    df = df.rename(columns={
        col_localidad[0]: "_localidad_raw",
        col_edad[0]: "_edad_raw",
        col_genero[0]: "_genero_raw",
        col_niveledu[0]: "_niveledu_raw",
    })

    df["localidad"] = df["_localidad_raw"].str.strip().str.lower().map(CROSSWALK_LOCALIDAD_CONFIANZA)
    n_sin_localidad = df["localidad"].isna().sum()
    logger.info(
        "Confianza institucional: %d de %d registros con localidad válida de Bogotá.",
        len(df) - n_sin_localidad, len(df),
    )
    df = df[df["localidad"].notna()].copy()

    # sexo: el dataset trae 7 categorías (incluye no binario/trans). Se
    # homologa a F/M solo para las dos categorías binarias; el resto queda
    # NaN y se descarta del receptor de este hot-deck, lo cual es una
    # limitación real (no cosmética) — ver DATA REQUIRED en
    # DATA_SPECIFICATION.md sobre homologar la variable de género completa.
    genero_raw_lower = df["_genero_raw"].astype(str).str.strip().str.lower()
    df["sexo"] = np.select(
        [genero_raw_lower.str.contains("hombre|masculino"), genero_raw_lower.str.contains("mujer|femenino")],
        ["M", "F"],
        default="",
    )
    df.loc[df["sexo"] == "", "sexo"] = np.nan
    n_sin_sexo = df["sexo"].isna().sum()
    if n_sin_sexo:
        logger.warning(
            "%d registros con género no binario/no homologable a F/M se "
            "descartan de este hot-deck (limitación documentada, no un bug).",
            n_sin_sexo,
        )
    df = df[df["sexo"].notna()].copy()

    df["edad"] = df["_edad_raw"].apply(_mapear_edad_media)

    df["nivel_educativo"] = df["_niveledu_raw"].apply(_mapear_nivel_educativo_confianza)

    df["estrato"] = np.nan  # ver supuesto #1 — no disponible en esta fuente

    columnas_confianza = columnas_confianza or _identificar_columnas_confianza(list(df.columns))
    columnas_confianza_presentes = [c for c in columnas_confianza if c in df.columns]
    if not columnas_confianza_presentes:
        raise ValueError(
            "No se encontró ninguna columna de confianza institucional por "
            "actor. Revisar _FRAGMENTOS_ACTORES_CONFIANZA contra el "
            "encabezado real, o pasar `columnas_confianza` explícitamente."
        )
    logger.info(
        "Índice de confianza institucional calculado como promedio de %d actores: %s",
        len(columnas_confianza_presentes),
        [c[-40:] for c in columnas_confianza_presentes],
    )
    df["confianza_institucional"] = df[columnas_confianza_presentes].apply(
        pd.to_numeric, errors="coerce"
    ).mean(axis=1)

    columnas = ["localidad", "sexo", "edad", "estrato", "nivel_educativo", "confianza_institucional"]
    if incluir_fecha:
        df = df.rename(columns={"_fecha_respuesta": "fecha_respuesta"})
        columnas.append("fecha_respuesta")

    resultado = df[columnas].dropna(
        subset=["edad", "nivel_educativo", "confianza_institucional"]).reset_index(drop=True)

    logger.info("Donante final: %d personas listas para matching.", len(resultado))
    return resultado