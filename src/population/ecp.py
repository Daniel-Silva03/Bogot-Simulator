"""
src/population/ecp.py

Carga de la Encuesta de Cultura Política (ECP) del DANE para Bogotá,
2017 / 2019 / 2021 / 2023.

PARA QUÉ
--------
El donante de opinión que usa el proyecto —la encuesta de confianza de la
Veeduría Distrital— resultó ser una sola recolección continua
(2024-12-04 → 2025-02-09), no dos olas. Eso deja el modelo sin ningún
"antes y después" contra el cual comparar, y bloquea la validación de
nivel 3 (dinámica) del Experimento 1.

La ECP es la salida: la misma pregunta de confianza institucional, con el
mismo código de variable y la misma escala 1–5, medida cuatro veces en
seis años, con Bogotá identificable y factores de expansión. No sustituye
al donante —no llega a localidad— pero da la serie temporal agregada que
hacía falta.

LO QUE ESTE MÓDULO RESUELVE, Y POR QUÉ NO ES TRIVIAL
----------------------------------------------------
Los cuatro años vienen del mismo formulario pero NO del mismo empaquetado.
Cambian entre años: el identificador interno del archivo (Democracia es F6,
F20, F12 y F20 según el año), el nombre de la carpeta ("Tabla viviendas",
"Viviendas", "Tabla de viviendas"), el nombre del archivo (incluida una
errata de DANE: "Caracteríasticas generales.csv" en 2023), el formato
(2017 sale en .txt separado por tabuladores; el resto en .csv por comas) y
la ubicación del factor de expansión. Cualquier ruta escrita a mano se
rompe con el año siguiente.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-C1. Los módulos se localizan por NOMBRE NORMALIZADO, no por ruta ni por
    identificador de archivo. Se normaliza quitando tildes, mayúsculas y
    todo lo que no sea letra, y se busca una raíz ("vivienda",
    "caracteri", "democracia") dentro del nombre. Eso absorbe los tres
    nombres de la tabla de viviendas, la errata de 2023 y la variación de
    mayúsculas, sin una tabla de excepciones por año que habría que
    mantener.

DI-C2. El factor de expansión se toma de VIVIENDAS (`FEX_P`), no del
    archivo de personas. Verificado sobre los cuatro años: `FEX_P` está en
    Viviendas siempre, mientras que en el archivo de personas aparece en
    2017 (los tres módulos lo traen), solo como `FEX_P_CENSO_2018` en
    2019, y en ninguno en 2021 y 2023. En 2017, donde se puede comparar,
    el `FEX_P` de personas y el de viviendas coinciden exactamente en las
    38.761 filas — así que no se pierde nada tomándolo de viviendas, y se
    gana una regla única para los cuatro años.

    2019 trae además `FEX_P_CENSO_2018`, reponderado contra el Censo 2018.
    Da un total distinto para Bogotá (5.810.318 contra 6.088.233). Se
    expone como columna aparte y NO se usa por defecto: mezclar dos bases
    censales dentro de una misma serie introduce un salto que no es
    cambio de opinión. Quien quiera la serie en base 2018 tiene que
    pedirla explícitamente y asumir que solo 2019 la tiene.

DI-C3. `P5263S6` y `P5263S12` se excluyen, y la razón importa más que la
    exclusión. Vienen completamente vacías en Bogotá en los cuatro años —
    cero respuestas, no "pocas"— pero **están llenas en las otras cuatro
    regiones** (entre 8.000 y 11.000 respuestas cada una en 2023). No es un
    hueco de datos: son `f. Asamblea departamental` y `l. Gobernación`, y
    **Bogotá D.C. no tiene ni asamblea departamental ni gobernación**. La
    pregunta no aplica y el encuestador la salta.

    Consecuencia: la serie de Bogotá tiene 13 ítems y eso no se arregla
    consiguiendo mejores datos. Se dejan las 15 en `ITEMS_CONFIANZA` porque
    el módulo también sirve para leer el país entero, donde sí están.

DI-C4. El código 99 ("No sabe / No informa") se convierte a NaN antes de
    promediar. No es un punto de la escala: tratarlo como 99 destrozaría
    cualquier media, y tratarlo como 3 ("ni mucho ni poco") inventaría una
    opinión neutra que la persona no expresó. Se reporta aparte cuánta
    no-respuesta hubo, porque su variación entre años es en sí misma un
    dato.

DI-C5. El merge se valida, no se confía. Personas se une a Democracia por
    las cuatro claves y a Viviendas por `DIRECTORIO`; ambas uniones tienen
    que conservar exactamente las filas de Democracia y no dejar ninguna
    sin `REGION`. Verificado en los cuatro años: 27.841 / 43.156 / 50.987 /
    46.392 filas, cero pérdidas, cero huérfanas. Si algún día deja de
    cumplirse, `ECPError` lo dice en vez de devolver un panel con agujeros.

DE DÓNDE SALEN LOS NOMBRES DE LOS ÍTEMS
---------------------------------------
No del microdato: ni el DDI ni las etiquetas de los .sav nombran las 15
instituciones —las 15 comparten la misma etiqueta genérica—. Salen del
`Formulario_ECP_2023 _VF.pdf` que DANE publica aparte, en dane.gov.co y no
en el portal de microdatos. Como el formulario numera con letras (a…o) y el
microdato con códigos (S1…S15), la correspondencia tampoco está publicada;
se estableció y se verificó por tres vías independientes, documentadas en
`ETIQUETAS_ITEMS`.

Las 11 descripciones de `P2051S*` —la composición del círculo cercano, que
es lo que permite calibrar la homofilia en vez de suponerla— salieron por
otro lado todavía: los rótulos de fila del Cuadro 9 del anexo
`anex-ECP-CapitalSocial-2023.xls`, porque el formulario publicado termina en
Democracia y no incluye Capital Social. Ver `ETIQUETAS_COMPOSICION_RED`.
"""

from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

#: Años cuyo instrumento de confianza institucional es EL MISMO, verificado
#: **contra los datos**, no solo contra los metadatos: mismos códigos
#: `P5263S1`…`S15`, misma escala 1–5, y —lo que de verdad importa— el mismo
#: código apuntando a la misma institución (ver ANCLAS_ITEMS y DI-C10).
ANIOS_COMPARABLES = (2013, 2017, 2019, 2021, 2023)

#: Años de la ECP que EXISTEN pero cuyo instrumento es otro. No se apilan sin
#: un crosswalk explícito, y apilarlos sin él fabricaría una tendencia que
#: sería un cambio de cuestionario (DI-C8).
ANIOS_NO_COMPARABLES = {
    2015: ("mismos códigos y misma escala, pero el CÓDIGO APUNTA A OTRA "
           "INSTITUCIÓN: S4 viene vacío y S6 poblado, al revés que en todos los "
           "demás años, y las anclas se rompen (el mínimo cae en S2 y el máximo "
           "en S9). Requiere crosswalk de códigos — DI-C10"),
    2011: "I46_A…I46_S — 19 instituciones en vez de 15, escala sin verificar",
    2008: "E35A_EPP… — otra familia de nombres y otro formato de pregunta",
    2007: "instrumento temprano, sin verificar",
}

#: Alias histórico. Se conserva porque hay código que lo importa por nombre.
ANIOS_DISPONIBLES = ANIOS_COMPARABLES

#: Los 15 ítems tal como los declara el DDI.
ITEMS_CONFIANZA = tuple(f"P5263S{i}" for i in range(1, 16))

#: Vacíos en Bogotá porque la institución NO EXISTE acá (DI-C3).
ITEMS_SIN_DATOS = ("P5263S6", "P5263S12")

#: Los que sí forman serie en los cuatro años.
ITEMS_UTILES = tuple(i for i in ITEMS_CONFIANZA if i not in ITEMS_SIN_DATOS)

#: Los 15 actores, del `Formulario_ECP_2023 _VF.pdf` (pregunta 17 del
#: capítulo Democracia), en el orden a…o que corresponde a S1…S15.
#:
#: El orden está confirmado por tres vías independientes, porque el
#: cuestionario da las letras y el microdato da los códigos, y nadie
#: publica la correspondencia:
#:   1. `f` (Asamblea departamental) y `l` (Gobernación) son las dos
#:      posiciones vacías en Bogotá — y son exactamente S6 y S12.
#:   2. S10 es el más desconfiado de los cuatro años (1,95–2,02), y `j` es
#:      "Partidos o movimientos políticos".
#:   3. S3 y S14 son los más confiados, y `c` y `n` son Fuerzas Militares y
#:      Registraduría.
ETIQUETAS_ITEMS: dict[str, str] = {
    "P5263S1":  "Procuraduría General de la Nación",
    "P5263S2":  "Alcaldía Municipal/Distrital",
    "P5263S3":  "Fuerzas Militares (Ejército, Armada y Fuerza Aérea)",
    "P5263S4":  "Congreso de la República",
    "P5263S5":  "Jueces y magistrados",
    "P5263S6":  "Asamblea departamental",          # no aplica a Bogotá D.C.
    "P5263S7":  "Contraloría (nacional, departamental o municipal)",
    "P5263S8":  "Concejos municipales/distritales",
    "P5263S9":  "Policía",
    "P5263S10": "Partidos o movimientos políticos",
    "P5263S11": "Defensoría del Pueblo",
    "P5263S12": "Gobernación",                      # no aplica a Bogotá D.C.
    "P5263S13": "Fiscalía General de la Nación",
    "P5263S14": "Registraduría Nacional del Estado Civil",
    "P5263S15": "Presidencia de la República",
}

#: Los 6 grupos de `P2025S*` (confianza interpersonal), del boletín técnico
#: de la ECP 2023. Las columnas del microdato son S1, S2, S4, S5, S6, S7 —
#: sin S3, que DANE dejó vacía en el esquema.
GRUPOS_CONFIANZA_INTERPERSONAL = (
    "familia", "amistades", "compañeros de trabajo",
    "vecinos", "extranjeros", "desconocidos",
)

CODIGO_NO_SABE = 99
REGION_BOGOTA = 1

#: DI-C10. Invariantes del instrumento, verificadas en 2013 y 2017-2023. Son
#: la prueba barata de que un año nuevo mide lo mismo: los metadatos de DANE
#: NO alcanzan, porque los 15 ítems comparten una sola etiqueta genérica
#: (§10.4 de DATA_INVENTORY) y por tanto un cambio en qué institución hay
#: detrás de cada código es invisible en el DDI. Solo se ve en los datos.
#:
#: Así se detectó que 2015 no era apilable pese a tener los mismos nombres de
#: variable y la misma escala.
ANCLAS_ITEMS = {
    "vacios_en_bogota": ("P5263S6", "P5263S12"),   # Asamblea y Gobernación: no existen acá
    "minimo": "P5263S10",                          # Partidos políticos, en todos los años
    "maximos_admisibles": ("P5263S3", "P5263S14"),  # Fuerzas Militares / Registraduría
}

CLAVES_PERSONA = ["DIRECTORIO", "NRO_ENCUESTA", "HOGAR_NUMERO", "PERSONA_NUMERO"]

#: DI-C9. En 2013 las dos últimas claves se llaman `V3` y `V4` — nombres
#: genéricos de export antiguo, sin etiqueta. De 2015 en adelante son
#: `HOGAR_NUMERO` y `PERSONA_NUMERO`. Es la misma clase de variación que ya
#: obligó a resolver los MÓDULOS por nombre normalizado, ahora una capa más
#: adentro. Se renombran al nombre canónico y se verifica —no se supone— que
#: la tupla resultante identifique a cada persona una sola vez.
ALIAS_CLAVES_PERSONA = {
    "HOGAR_NUMERO": ("HOGAR_NUMERO", "V3"),
    "PERSONA_NUMERO": ("PERSONA_NUMERO", "V4"),
}

#: raíz normalizada -> rol. El orden importa: "caracteri" antes que nada
#: más porque es el único prefijo que comparte letras con otros módulos.
RAICES_MODULO = {
    "vivienda": "viviendas",
    "caracteri": "caracteristicas",
    "democracia": "democracia",
}

#: Módulos que no hacen falta para la serie de confianza pero traen las
#: variables con las que se puede CALIBRAR la red en vez de suponerla
#: (A07). Se cargan si están y se ignoran si no, porque `Capital Social`
#: no existe en 2017 y no tiene sentido que su ausencia rompa la carga de
#: un año que sí tiene todo lo demás.
RAICES_MODULO_OPCIONAL = {
    "participacion": "participacion",
    "capitalsocial": "capital_social",
}

#: Variables del módulo Capital Social que importan para la red. No están
#: en 2017 (ese año no tiene el módulo).
#:
#: `P2047` y `P2051S*` son, hasta donde llega el microdato público, lo más
#: parecido a datos de red que va a tener este proyecto: P2047 es el TAMAÑO
#: de la red personal de contacto frecuente, y cada P2051S* es CUÁNTAS de
#: esas personas cumplen una descripción dada. El cociente entre las dos da,
#: por persona, la fracción de su círculo cercano que comparte cada
#: atributo — que es exactamente el parámetro que
#: `NETWORK SPECIFICATION.md` fija hoy por supuesto.
CAPITAL_SOCIAL = {
    "P2047": "red_visitas",         # cuántas personas visita / lo visitan seguido
    "P2049": "red_apoyo",           # cuántas lo ayudarían a buscar empleo
    "P2043": "confianza_extrano",   # el ítem del desconocido que da indicaciones
}

#: La "red cercana de apoyo y confianza" tal como la define DANE: la suma de
#: las dos. Verificado reproduciendo el Cuadro 9 publicado (ver
#: ETIQUETAS_COMPOSICION_RED). Es el denominador de las fracciones de
#: composición, y el tamaño de red que hay que usar para calibrar el grado.
COLUMNA_RED_CERCANA = "red_cercana"
PREFIJO_COMPOSICION_RED = "P2051S"   # composición del círculo cercano

#: Las 11 descripciones de `P2051S*`, del Cuadro 9 del anexo
#: `anex-ECP-CapitalSocial-2023.xls` ("Caracterización de las redes cercanas
#: de apoyo y confianza"). No están en el DDI, ni en las etiquetas de los
#: .sav, ni en el formulario publicado —que termina en el capítulo
#: Democracia—: solo en los rótulos de fila de ese anexo.
#:
#: CÓMO SE ESTABLECIÓ LA CORRESPONDENCIA, que tampoco está publicada:
#: reproduciendo los porcentajes del propio Cuadro 9. Para cada columna se
#: calculó el cociente agregado ponderado contra los tres dominios que el
#: anexo publica (total nacional, cabeceras, centros poblados y rural
#: disperso) y se buscó la descripción más cercana. La asignación resultante
#: es biyectiva y la peor discrepancia sobre 33 comparaciones es de **0,1
#: puntos porcentuales**. No es una interpretación: es el mismo número.
#:
#: Dos cosas que ese ejercicio destrabó y que no se podían adivinar:
#:   - La descripción que faltaba es **"Hombres"** (qué parte del círculo
#:     cercano son hombres). Se había perdido al leer el anexo porque
#:     "Hombres" también es encabezado de columna.
#:   - El denominador de DANE **no es `P2047`** sino `P2047 + P2049`: la
#:     "red cercana de apoyo y confianza" son las personas que uno visita
#:     con frecuencia MÁS las que lo ayudarían a buscar empleo. Con `P2047`
#:     solo, los porcentajes salen ~1,4 veces más altos y no coinciden con
#:     nada.
ETIQUETAS_COMPOSICION_RED: dict[str, str] = {
    "P2051S1":  "Miembros de su familia",
    "P2051S2":  "Hombres",
    "P2051S3":  "Se graduaron de bachillerato",
    "P2051S4":  "Asisten a su grupo u organización religiosa",
    "P2051S5":  "Son extranjeros",
    "P2051S6":  "Viven en su misma cuadra",
    "P2051S7":  "Tienen un empleo",
    "P2051S8":  "Usted les ha prestado dinero o ellos le han prestado en los últimos 12 meses",
    "P2051S9":  "Tienen opiniones políticas parecidas a las suyas",
    "P2051S10": "Son de su grupo étnico",
    "P2051S11": ("Sienten que han perdido oportunidades económicas por culpa "
                 "de trabajadores extranjeros"),
}

#: Porcentajes publicados (Cuadro 9, ECP 2023) contra los que se verificó la
#: asignación: total nacional, cabeceras, centros poblados y rural disperso.
#: Se conservan para que el test pueda volver a comprobarla.
CUADRO9_PUBLICADO_2023 = {
    "P2051S1": (51.6, 51.8, 51.0), "P2051S2": (40.2, 39.8, 41.7),
    "P2051S3": (58.9, 64.7, 36.7), "P2051S4": (33.5, 33.6, 33.1),
    "P2051S5": (2.7, 2.8, 2.4),    "P2051S6": (20.3, 16.4, 35.6),
    "P2051S7": (58.9, 62.3, 45.7), "P2051S8": (15.6, 16.1, 13.9),
    "P2051S9": (35.0, 35.5, 33.1), "P2051S10": (41.3, 41.1, 42.0),
    "P2051S11": (11.8, 12.7, 8.3),
}
PREFIJO_CONFIANZA_INTERPERSONAL = "P2025S"
PREFIJO_PERTENENCIA_ORG = "P2001S"   # cruza con el capítulo J de Multipropósito
PREFIJO_CONTACTO_ORG = "P2003S"

#: Formatos legibles sin dependencias extra, en orden de preferencia.
#: .sav queda fuera a propósito: leerlo necesita pyreadstat, que no está
#: en requirements.txt, y DANE publica el mismo contenido en texto.
EXTENSIONES = (".csv", ".txt", ".dta")

COLUMNAS_DEMOGRAFICAS = {
    "P220": "sexo",
    "P5785": "edad",
    "P6210": "educacion",
    "P4031S1A1": "estrato",
}


class ECPError(Exception):
    """Los archivos de la ECP no están donde o como se esperaba."""


@dataclass
class ModulosECP:
    """Las tres rutas de un año, ya resueltas."""

    anio: int
    viviendas: Path
    caracteristicas: Path
    democracia: Path
    participacion: Optional[Path] = None
    capital_social: Optional[Path] = None

    def __str__(self) -> str:
        base = (f"ECP {self.anio}: {self.viviendas.name} | "
                f"{self.caracteristicas.name} | {self.democracia.name}")
        extra = [p.name for p in (self.participacion, self.capital_social) if p]
        return base + (" | + " + " | ".join(extra) if extra else "")


# --------------------------------------------------------------------------
# Localización de archivos
# --------------------------------------------------------------------------

def _normalizar(texto: str) -> str:
    """Quita tildes, mayúsculas y todo lo que no sea letra (DI-C1)."""
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", sin_tildes.lower())


def localizar_modulos(raiz: str | Path, anio: int) -> ModulosECP:
    """
    Encuentra los tres módulos de un año bajo `raiz/<anio>/`, sin importar
    cómo se llamen las carpetas ni los archivos.

    Busca recursivamente, así que da igual si los archivos quedaron
    sueltos, en subcarpetas por módulo, o en subcarpetas por módulo con
    otro nivel adentro.
    """
    carpeta = Path(raiz) / str(anio)
    if not carpeta.is_dir():
        raise ECPError(
            f"No existe la carpeta {carpeta}. Se esperaba {raiz}/<año>/ con los "
            f"módulos del año. Años comparables: {ANIOS_COMPARABLES}."
        )

    candidatos = [p for p in carpeta.rglob("*")
                  if p.is_file() and p.suffix.lower() in EXTENSIONES]
    if not candidatos:
        sav = list(carpeta.rglob("*.sav"))
        pista = (f" Hay {len(sav)} archivo(s) .sav, que este módulo no lee: "
                 f"descargá también el .csv o el .dta." if sav else "")
        raise ECPError(f"No hay archivos legibles ({', '.join(EXTENSIONES)}) "
                       f"bajo {carpeta}.{pista}")

    def _elegir(raiz_nombre: str) -> Optional[Path]:
        coincidencias = [p for p in candidatos if raiz_nombre in _normalizar(p.name)]
        if not coincidencias:
            return None
        # Preferencia por formato, y a igualdad de formato el más grande
        # (los .csv parciales de una descarga interrumpida quedan chicos).
        coincidencias.sort(key=lambda p: (EXTENSIONES.index(p.suffix.lower()),
                                          -p.stat().st_size))
        return coincidencias[0]

    encontrados: dict[str, Path] = {}
    for raiz_nombre, rol in RAICES_MODULO.items():
        elegido = _elegir(raiz_nombre)
        if elegido is None:
            raise ECPError(
                f"ECP {anio}: no encontré el módulo '{rol}'. Busqué archivos cuyo "
                f"nombre contenga '{raiz_nombre}' (ignorando tildes y mayúsculas) "
                f"bajo {carpeta}. Hay: {sorted(p.name for p in candidatos)}"
            )
        encontrados[rol] = elegido

    # Opcionales: si no están, se siguen. 2017 no tiene Capital Social y eso
    # no puede impedir cargar la serie de confianza de ese año.
    for raiz_nombre, rol in RAICES_MODULO_OPCIONAL.items():
        elegido = _elegir(raiz_nombre)
        if elegido is not None:
            encontrados[rol] = elegido

    return ModulosECP(anio=anio, **encontrados)


def leer_tabla(path: Path) -> pd.DataFrame:
    """
    Lee un módulo de la ECP detectando el separador.

    2017 sale en .txt separado por tabuladores y el resto en .csv por
    comas, pero DANE no garantiza eso, así que se decide leyendo el
    encabezado en vez de mirar la extensión. Encoding latin-1 en todos.
    """
    if path.suffix.lower() == ".dta":
        return pd.read_stata(path, convert_categoricals=False)

    with open(path, "rb") as f:
        encabezado = f.readline().decode("latin-1")
    separador = "\t" if encabezado.count("\t") > encabezado.count(",") else ","
    tabla = pd.read_csv(path, sep=separador, encoding="latin-1", low_memory=False)
    if tabla.shape[1] < 2:
        raise ECPError(
            f"{path.name} se leyó como {tabla.shape[1]} columna(s) con "
            f"separador {separador!r}. Es casi seguro que el separador está mal."
        )
    return tabla


# --------------------------------------------------------------------------
# Carga
# --------------------------------------------------------------------------

def _canonizar_claves(tabla: pd.DataFrame, anio: int, modulo: str) -> pd.DataFrame:
    """Lleva las claves de persona a su nombre canónico y comprueba que sirvan.

    DI-C9. Acepta los alias de `ALIAS_CLAVES_PERSONA` y **verifica** el
    resultado en vez de confiar en él: si la tupla no identifica a cada
    persona una sola vez, el alias elegido no era la variable que se creía y
    el merge posterior duplicaría filas en silencio. Preferimos fallar acá,
    donde el mensaje dice qué columna se usó.
    """
    renombres = {}
    for canonico, alias in ALIAS_CLAVES_PERSONA.items():
        if canonico in tabla.columns:
            continue
        encontrado = next((a for a in alias if a in tabla.columns), None)
        if encontrado is None:
            raise ECPError(
                f"ECP {anio}: a {modulo} le falta {canonico} y ninguno de sus "
                f"alias conocidos {alias}. Columnas presentes: "
                f"{sorted(tabla.columns)[:12]}…")
        renombres[encontrado] = canonico
    if renombres:
        tabla = tabla.rename(columns=renombres)
        logger.info("ECP %d: %s -> claves renombradas %s", anio, modulo, renombres)

    faltan = [c for c in CLAVES_PERSONA if c not in tabla.columns]
    if faltan:
        raise ECPError(f"ECP {anio}: a {modulo} le faltan claves {faltan}.")

    duplicados = int(tabla.duplicated(CLAVES_PERSONA).sum())
    if duplicados:
        raise ECPError(
            f"ECP {anio}: en {modulo}, {CLAVES_PERSONA} no identifica a cada "
            f"persona una sola vez ({duplicados} duplicados)"
            + (f" usando {renombres}" if renombres else "")
            + ". El alias elegido no es la variable que se creía (DI-C9).")
    return tabla


def _sin_fex(tabla: pd.DataFrame) -> pd.DataFrame:
    """Quita los ponderadores de un archivo de personas (DI-C2)."""
    return tabla.drop(columns=[c for c in tabla.columns if c.startswith("FEX")])


def cargar_anio(
    raiz: str | Path,
    anio: int,
    region: Optional[int] = REGION_BOGOTA,
) -> pd.DataFrame:
    """
    Devuelve el panel de personas de un año: demografía, estrato,
    ponderador y los 15 ítems de confianza.

    `region=None` devuelve el país entero; por defecto filtra Bogotá.
    """
    modulos = localizar_modulos(raiz, anio)
    logger.info("%s", modulos)

    viviendas = leer_tabla(modulos.viviendas)
    caracteristicas = leer_tabla(modulos.caracteristicas)
    democracia = leer_tabla(modulos.democracia)

    caracteristicas = _canonizar_claves(caracteristicas, anio, "Características Generales")
    democracia = _canonizar_claves(democracia, anio, "Democracia")
    if "REGION" not in viviendas.columns:
        raise ECPError(
            f"ECP {anio}: {modulos.viviendas.name} no tiene REGION, que es la "
            "única variable que permite aislar Bogotá."
        )
    if "FEX_P" not in viviendas.columns:
        raise ECPError(
            f"ECP {anio}: {modulos.viviendas.name} no tiene FEX_P. Ver DI-C2: es "
            "el ponderador que este módulo usa para los cuatro años."
        )
    if viviendas["DIRECTORIO"].duplicated().any():
        raise ECPError(
            f"ECP {anio}: DIRECTORIO se repite en viviendas; el merge duplicaría "
            "personas y el ponderador dejaría de sumar la población real."
        )

    n_democracia = len(democracia)
    panel = _sin_fex(caracteristicas).merge(
        _sin_fex(democracia), on=CLAVES_PERSONA, how="inner")
    if len(panel) != n_democracia:
        raise ECPError(
            f"ECP {anio}: el cruce personas × Democracia dio {len(panel)} filas y "
            f"Democracia tiene {n_democracia}. Las cuatro claves deberían casar "
            "exactamente (DI-C5)."
        )

    columnas_vivienda = ["DIRECTORIO", "REGION", "FEX_P"]
    if "P4031S1A1" in viviendas.columns:
        columnas_vivienda.append("P4031S1A1")
    if "P3" in viviendas.columns:
        columnas_vivienda.append("P3")
    alternativos = [c for c in viviendas.columns
                    if c.startswith("FEX_P_")]  # FEX_P_CENSO_2018, FEX_P_PDET
    columnas_vivienda += alternativos

    panel = panel.merge(viviendas[columnas_vivienda], on="DIRECTORIO", how="left")
    if len(panel) != n_democracia or panel["REGION"].isna().any():
        raise ECPError(
            f"ECP {anio}: el cruce con viviendas dejó {len(panel)} filas y "
            f"{int(panel['REGION'].isna().sum())} sin REGION (DI-C5)."
        )

    if region is not None:
        panel = panel[panel["REGION"] == region].copy()
        if panel.empty:
            raise ECPError(f"ECP {anio}: no hay filas con REGION == {region}.")

    panel.insert(0, "anio", anio)
    panel = panel.rename(columns={"FEX_P": "fex", **COLUMNAS_DEMOGRAFICAS})
    for col in ("fex", "edad", "sexo", "educacion", "estrato"):
        if col in panel.columns:
            panel[col] = pd.to_numeric(panel[col], errors="coerce")

    presentes = [i for i in ITEMS_CONFIANZA if i in panel.columns]
    for item in presentes:
        panel[item] = pd.to_numeric(panel[item], errors="coerce")
    ausentes = [i for i in ITEMS_CONFIANZA if i not in panel.columns]
    if ausentes:
        logger.warning("ECP %s: no están los ítems %s", anio, ausentes)

    return panel.reset_index(drop=True)


def anios_en_disco(raiz: str | Path) -> tuple[int, ...]:
    """Qué años comparables hay efectivamente descargados bajo `raiz`.

    DI-C8. La lista de años dejó de estar escrita a mano. Antes era una
    constante que decía (2017, 2019, 2021, 2023) y había que acordarse de
    editarla al bajar una ola nueva — el mismo modo de fallo que
    `claude/DATA_INVENTORY.md` registra en su nota de la v0.6, donde un
    documento afirmaba que faltaba un archivo que llevaba meses en disco.
    Ahora se mira el disco.

    Avisa —sin fallar— si encuentra carpetas de años que existen en la ECP
    pero cuyo instrumento es otro (2011 y anteriores): que estén bajados no
    los vuelve apilables.
    """
    raiz = Path(raiz)
    presentes = {int(p.name) for p in raiz.iterdir()
                 if p.is_dir() and p.name.isdigit()}
    for anio in sorted(presentes & set(ANIOS_NO_COMPARABLES)):
        logger.warning(
            "Hay datos de %d en disco pero NO se apilan: %s. "
            "Requiere crosswalk explícito (ANIOS_NO_COMPARABLES).",
            anio, ANIOS_NO_COMPARABLES[anio])
    encontrados = tuple(sorted(presentes & set(ANIOS_COMPARABLES)))
    if not encontrados:
        raise FileNotFoundError(
            f"No hay ningún año comparable de la ECP bajo {raiz}. "
            f"Se esperaba al menos una carpeta de {ANIOS_COMPARABLES}.")
    return encontrados


def cargar_panel(
    raiz: str | Path,
    anios: Optional[Iterable[int]] = None,
    region: Optional[int] = REGION_BOGOTA,
) -> pd.DataFrame:
    """Apila varios años en un solo panel, con `anio` como discriminante.

    Por defecto usa los años comparables que estén en disco (DI-C8), no una
    lista fija.
    """
    anios = anios_en_disco(raiz) if anios is None else anios
    partes = [cargar_anio(raiz, a, region=region) for a in anios]
    panel = pd.concat(partes, ignore_index=True, sort=False)
    logger.info("Panel ECP: %d personas, años %s",
                len(panel), sorted(panel["anio"].unique()))
    return panel


# --------------------------------------------------------------------------
# Serie de confianza
# --------------------------------------------------------------------------

def _media_ponderada(valores: pd.Series, pesos: pd.Series) -> float:
    validos = valores.between(1, 5) & pesos.notna() & (pesos > 0)
    if not validos.any():
        return float("nan")
    return float(np.average(valores[validos], weights=pesos[validos]))


def serie_confianza(
    panel: pd.DataFrame,
    items: Iterable[str] = ITEMS_UTILES,
    ponderar: bool = True,
) -> pd.DataFrame:
    """
    Media de cada ítem por año, en la escala 1–5, con el 99 fuera (DI-C4).

    Devuelve un formato largo con `anio`, `item`, `media`, `n_validos`,
    `n_no_sabe` y `pct_no_sabe`. Ese último no es relleno: la no-respuesta
    a una pregunta de confianza institucional se mueve con el clima
    político, y si se mueve mucho entre años, la media de los que sí
    contestaron ya no es comparable.
    """
    filas = []
    for anio, grupo in panel.groupby("anio", sort=True):
        pesos = grupo["fex"] if ponderar else pd.Series(1.0, index=grupo.index)
        for item in items:
            if item not in grupo.columns:
                continue
            valores = grupo[item]
            n_validos = int(valores.between(1, 5).sum())
            n_no_sabe = int((valores == CODIGO_NO_SABE).sum())
            denominador = n_validos + n_no_sabe
            filas.append({
                "anio": int(anio),
                "item": item,
                "etiqueta": ETIQUETAS_ITEMS.get(item, ""),
                "media": _media_ponderada(valores, pesos) if n_validos else float("nan"),
                "n_validos": n_validos,
                "n_no_sabe": n_no_sabe,
                "pct_no_sabe": 100.0 * n_no_sabe / denominador if denominador else float("nan"),
            })
    return pd.DataFrame(filas)


def cobertura_items(panel: pd.DataFrame) -> pd.DataFrame:
    """
    Cuántas respuestas válidas tiene cada ítem en cada año.

    Es el chequeo que hay que correr antes de construir cualquier serie:
    un ítem vacío en un año corta la serie ahí, y el conjunto utilizable es
    la INTERSECCIÓN de los ítems poblados en todos los años, no la unión de
    los declarados (DI-C3).
    """
    tabla = (serie_confianza(panel, items=ITEMS_CONFIANZA)
             .pivot(index="item", columns="anio", values="n_validos")
             .reindex(list(ITEMS_CONFIANZA)))
    tabla["utilizable"] = (tabla.fillna(0) > 0).all(axis=1)
    return tabla


def verificar_anclas(panel: pd.DataFrame) -> pd.DataFrame:
    """¿Cada código apunta a la misma institución en todos los años? (DI-C10)

    Devuelve una fila por año con las tres anclas y si las cumple. Un año que
    falle NO se apila: tiene los mismos nombres de variable pero mide otra
    cosa, y promediarlo con el resto fabricaría una tendencia que en realidad
    es un cambio de cuestionario.

    Es la prueba que faltaba cuando se verificó 2015 solo contra el DDI.
    """
    filas = []
    for anio, g in panel.groupby("anio"):
        medias = {i: _media_ponderada(g[i], g["fex"])
                  for i in ITEMS_CONFIANZA if i in g.columns}
        con_datos = {i: m for i, m in medias.items() if pd.notna(m)}
        vacios_ok = all(pd.isna(medias.get(i, float("nan")))
                        for i in ANCLAS_ITEMS["vacios_en_bogota"])
        minimo = min(con_datos, key=con_datos.get) if con_datos else None
        maximo = max(con_datos, key=con_datos.get) if con_datos else None
        filas.append({
            "anio": int(anio),
            "vacios_correctos": vacios_ok,
            "minimo": minimo,
            "minimo_ok": minimo == ANCLAS_ITEMS["minimo"],
            "maximo": maximo,
            "maximo_ok": maximo in ANCLAS_ITEMS["maximos_admisibles"],
        })
    t = pd.DataFrame(filas)
    t["apilable"] = t.vacios_correctos & t.minimo_ok & t.maximo_ok
    return t


def describir_items(solo_bogota: bool = True) -> str:
    """Los 15 actores, marcando los que no aplican a Bogotá."""
    orden = sorted(ETIQUETAS_ITEMS, key=lambda k: int(k.replace("P5263S", "")))
    lineas = []
    for k in orden:
        if solo_bogota and k in ITEMS_SIN_DATOS:
            lineas.append(f"{k:9s} {ETIQUETAS_ITEMS[k]}  (no aplica a Bogotá D.C.)")
        else:
            lineas.append(f"{k:9s} {ETIQUETAS_ITEMS[k]}")
    return "\n".join(lineas)


# --------------------------------------------------------------------------
# La ECP como donante de opinión del hot-deck (Experimento 3A)
# --------------------------------------------------------------------------
#
# DI-C6. Mínimo de ítems para el índice. El índice de confianza de una
#     persona es la media de sus ítems válidos, y eso solo es comparable
#     entre personas si todas promedian una cantidad parecida de ítems.
#     `POPULATION_SPECIFICATION.md` 8.4 dejó abierto exactamente este punto
#     para el donante de la Veeduría, donde el índice promedia entre 1 y 8
#     actores sin piso. Acá se fija un piso de 7 de 13: quien contestó menos
#     queda fuera en vez de entrar con un índice construido sobre otra cosa.
#     Cuesta poco —la no-respuesta por ítem va del 1,5 % al 8,5 %— y hace
#     que el índice signifique lo mismo para todos.
#
# DI-C7. Escala de educación armonizada. La ECP colapsa en una sola
#     categoría lo que el proyecto separa en dos: `P6210 = 6` es "Superior
#     (técnica, tecnológica, universitaria-pregrado)", mientras que la
#     escala 0-5 de NETWORK_SPECIFICATION distingue técnica/tecnológica (3)
#     de universitaria (4). La ECP no permite deshacer esa mezcla.
#
#     Se resuelve armonizando AMBOS lados a la escala común más fina
#     posible, de 5 niveles (0-4), y usando ESA para emparejar. El agente
#     conserva su `nivel_educativo` fino de Multipropósito para la red
#     homofílica: no se pierde información, solo se deja de fingir una
#     precisión que el donante no tiene.
#
#     Mapear `P6210 = 6` a "universitaria" habría sido lo cómodo, y habría
#     movido a todos los técnicos y tecnólogos un escalón hacia arriba en la
#     variable que alimenta la distancia del matching.

INDICE_MIN_ITEMS = 7

#: P6210 de la ECP -> escala armonizada 0-4.
MAPA_EDUCACION_ECP = {
    1: 0,   # Ninguno
    2: 0,   # Preescolar
    3: 1,   # Básica primaria
    4: 2,   # Básica secundaria
    5: 2,   # Media
    6: 3,   # Superior (técnica + tecnológica + universitaria-pregrado)
    7: 4,   # Posgrado
    8: None, 99: None,   # No sabe / no informa (8 en los .sav, 99 en el DDI)
}

#: Escala 0-5 del proyecto -> la misma escala armonizada 0-4.
MAPA_EDUCACION_PROYECTO = {0: 0, 1: 1, 2: 2, 3: 3, 4: 3, 5: 4}

COLUMNA_EDUCACION_MATCH = "educacion_match"
COLUMNA_OPINION_ECP = "confianza_institucional"


def indice_confianza(panel: pd.DataFrame, min_items: int = INDICE_MIN_ITEMS) -> pd.Series:
    """
    Índice de confianza por persona: media de los ítems válidos en 1-5.

    El 99 ya viene fuera por construcción (no cae en `between(1, 5)`), y
    quien tenga menos de `min_items` respuestas queda en NaN (DI-C6).
    """
    presentes = [i for i in ITEMS_UTILES if i in panel.columns]
    X = panel[presentes].where(panel[presentes].apply(lambda c: c.between(1, 5)))
    return X.mean(axis=1).where(X.notna().sum(axis=1) >= min_items)


def armonizar_educacion_proyecto(nivel: pd.Series) -> pd.Series:
    """Escala 0-5 del proyecto -> escala armonizada 0-4 (DI-C7)."""
    return pd.to_numeric(nivel, errors="coerce").map(MAPA_EDUCACION_PROYECTO)


def donante_ecp(
    raiz: str | Path,
    anio: int = 2017,
    min_items: int = INDICE_MIN_ITEMS,
) -> pd.DataFrame:
    """
    Lleva un año de la ECP al esquema estándar del donante que espera
    `hot_deck_match`.

    Devuelve: sexo, edad, estrato, nivel_educativo_ecp, educacion_match,
    confianza_institucional, factor_expansion.

    **No trae `localidad`**: la ECP solo identifica Bogotá como región. Quien
    llame tiene que sacar `localidad` de `exact_match_vars` — el hot-deck
    fallaría con un error claro si no, pero conviene saberlo antes.
    """
    panel = cargar_anio(raiz, anio)

    d = pd.DataFrame({
        "sexo": panel["sexo"].map({1: "M", 2: "F"}),
        "edad": pd.to_numeric(panel["edad"], errors="coerce"),
        "estrato": pd.to_numeric(panel["estrato"], errors="coerce"),
        "nivel_educativo_ecp": pd.to_numeric(panel["educacion"], errors="coerce"),
        "factor_expansion": pd.to_numeric(panel["fex"], errors="coerce"),
        COLUMNA_OPINION_ECP: indice_confianza(panel, min_items=min_items),
    })
    d[COLUMNA_EDUCACION_MATCH] = d["nivel_educativo_ecp"].map(MAPA_EDUCACION_ECP)

    antes = len(d)
    d = d.dropna(subset=["sexo", "edad", "estrato", COLUMNA_EDUCACION_MATCH,
                         COLUMNA_OPINION_ECP, "factor_expansion"]).reset_index(drop=True)
    if d.empty:
        raise ECPError(f"ECP {anio}: no quedó ningún donante válido.")

    logger.info(
        "Donante ECP %s: %d de %d registros completos (%.1f%%). "
        "Índice de confianza: media %.4f, sd %.4f.",
        anio, len(d), antes, 100 * len(d) / antes,
        float(np.average(d[COLUMNA_OPINION_ECP], weights=d["factor_expansion"])),
        float(d[COLUMNA_OPINION_ECP].std()),
    )
    return d


def cargar_capital_social(raiz: str | Path, anio: int) -> pd.DataFrame:
    """
    Carga los módulos Participación y Capital Social y los cruza con la
    confianza institucional y la demografía del mismo año.

    PARA QUÉ
    --------
    `claude/ANALISIS_HOMOFILIA.md` estableció que la demografía explica el
    3 % de la varianza de confianza y que ningún atributo observable
    estable la explica mejor de forma reproducible. Estos módulos son la
    única vía que queda, y traen dos cosas que el proyecto venía suponiendo:

    - **El tamaño de la red personal** (`P2047`): cuántas personas visita o
      lo visitan con frecuencia. Es la distribución empírica de grado —
      exactamente el \\(\\bar{k}\\) que `NETWORK SPECIFICATION.md` fija a
      dedo en 4, 8 o 16.
    - **La composición de esa red** (`P2051S1`…`S11`): cuántas de esas
      personas cumplen cada descripción. Dividido por `P2047` da, por
      persona, la fracción de su círculo cercano que comparte cada
      atributo. Es la homofilia medida, no supuesta.

    Más `P2025S*` (confianza interpersonal, 1–5), `P2043` (el ítem del
    desconocido) y `P2001S*` (pertenencia a organizaciones, que cruza con
    el capítulo J de Multipropósito y por lo tanto puede llegar a ser
    atributo del agente, no solo del donante).

    LÍMITES, PORQUE IMPORTAN
    ------------------------
    `P2047` pregunta por visitas mutuas frecuentes: son lazos fuertes de
    sociabilidad doméstica, no "quién influye en tu opinión política". Es
    una rebanada estrecha de la red real y hay que decirlo cada vez que se
    use para calibrar. Sigue siendo infinitamente mejor que nada.

    **No existe en 2017**: ese año la ECP no tenía módulo de Capital
    Social. Se levanta `ECPError` con ese dato en vez de devolver vacío.
    """
    modulos = localizar_modulos(raiz, anio)
    if modulos.capital_social is None and modulos.participacion is None:
        raise ECPError(
            f"ECP {anio}: no están los módulos Participación ni Capital Social "
            f"bajo {Path(raiz) / str(anio)}. La ECP 2017 no tiene Capital Social; "
            "para los demás años hay que descargarlos del catálogo."
        )

    base = cargar_anio(raiz, anio)
    base = base.set_index(CLAVES_PERSONA)

    partes = []
    for ruta in (modulos.participacion, modulos.capital_social):
        if ruta is None:
            continue
        t = leer_tabla(ruta)
        faltan = [c for c in CLAVES_PERSONA if c not in t.columns]
        if faltan:
            raise ECPError(f"ECP {anio}: a {ruta.name} le faltan claves {faltan}.")
        t = t.drop(columns=[c for c in t.columns if c.startswith("FEX")])
        partes.append(t.set_index(CLAVES_PERSONA))

    extra = pd.concat(partes, axis=1)
    extra = extra.loc[:, ~extra.columns.duplicated()]
    d = base.join(extra, how="left").reset_index().copy()

    derivadas = {}
    for viejo, nuevo in CAPITAL_SOCIAL.items():
        if viejo in d.columns:
            v = pd.to_numeric(d[viejo], errors="coerce")
            derivadas[nuevo] = v.where(~v.isin([98, 99]))

    conf = [c for c in d.columns if c.startswith(PREFIJO_CONFIANZA_INTERPERSONAL)]
    if conf:
        X = d[conf].apply(pd.to_numeric, errors="coerce")
        X = X.where((X >= 1) & (X <= 5))     # deja fuera el 99 de no-respuesta
        derivadas["confianza_interpersonal"] = X.mean(axis=1)

    orgs = [c for c in d.columns if c.startswith(PREFIJO_PERTENENCIA_ORG)]
    if orgs:
        derivadas["n_organizaciones"] = (
            d[orgs].apply(pd.to_numeric, errors="coerce") == 1).sum(axis=1)

    # Fracción del círculo cercano que cumple cada descripción. Las
    # descripciones no son excluyentes, así que las fracciones NO suman 1.
    if "red_visitas" in derivadas or "red_apoyo" in derivadas:
        derivadas[COLUMNA_RED_CERCANA] = (
            derivadas.get("red_visitas", pd.Series(0.0, index=d.index)).fillna(0)
            + derivadas.get("red_apoyo", pd.Series(0.0, index=d.index)).fillna(0))

    comp = sorted((c for c in d.columns if c.startswith(PREFIJO_COMPOSICION_RED)),
                  key=lambda c: int(c[len(PREFIJO_COMPOSICION_RED):]))
    if comp and COLUMNA_RED_CERCANA in derivadas:
        tam = derivadas[COLUMNA_RED_CERCANA].where(derivadas[COLUMNA_RED_CERCANA] > 0)
        for c in comp:
            n = pd.to_numeric(d[c], errors="coerce")
            n = n.where(~n.isin([98, 99]))
            derivadas[f"frac_{c[len(PREFIJO_COMPOSICION_RED):]}"] = (n / tam).clip(upper=1.0)

    d = pd.concat([d, pd.DataFrame(derivadas, index=d.index)], axis=1)

    logger.info("ECP %s capital social: %d personas, %d ítems de composición de red.",
                anio, len(d), len(comp))
    return d


def distribucion_observada(
    raiz: str | Path,
    anios: Optional[Iterable[int]] = None,
    min_items: int = INDICE_MIN_ITEMS,
) -> pd.DataFrame:
    """
    El objetivo del Experimento 3: el índice de confianza por persona y su
    ponderador, año por año. Es contra esto que se compara la simulación.
    """
    panel = cargar_panel(raiz, anios)   # anios=None -> lo que haya en disco
    salida = pd.DataFrame({
        "anio": panel["anio"],
        "fex": pd.to_numeric(panel["fex"], errors="coerce"),
        "indice": indice_confianza(panel, min_items=min_items),
    })
    return salida.dropna().reset_index(drop=True)


# --------------------------------------------------------------------------

def _resumen_consola(raiz: str | Path) -> None:
    panel = cargar_panel(raiz)

    print("\nPersonas de Bogotá por año")
    for anio, g in panel.groupby("anio"):
        print(f"  {anio}: n = {len(g):,}   población expandida = {g['fex'].sum():,.0f}")

    print("\nCobertura por ítem (respuestas válidas 1-5)")
    cob = cobertura_items(panel)
    print(cob.to_string())
    utiles = cob.index[cob["utilizable"]].tolist()
    print(f"\nIntersección utilizable: {len(utiles)} ítems")

    print("\nMedia ponderada por año")
    serie = serie_confianza(panel)
    medias = (serie.pivot(index="item", columns="anio", values="media")
              .reindex([i for i in ITEMS_UTILES if i in serie["item"].values]))
    print(medias.round(3).to_string())

    print(f"\n{describir_items()}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    _resumen_consola(Path(__file__).resolve().parents[2] / "data" / "raw" / "ecp")
