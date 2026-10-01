"""
Banco de preguntas nuevas con respuesta real (`docs/BANCO_PREGUNTAS_NUEVAS.md`).

Paso 1, sin gasto: arma las candidatas de las cuatro fuentes, solo con metadatos (texto de
la pregunta y categorías; ninguna respuesta).
Paso 2, con la API: clasifica cada candidata (¿opinión?, ¿electoral?, ¿conducta o hecho?) y
la escribe como pregunta de la página, con qué categorías cuentan como «de acuerdo».
Paso 3, después de la revisión de Daniel: el sorteo de práctica y guardado (otro comando).

Uso:
    python src/experiments/banco.py --candidatas          # paso 1: escribe candidatas.csv
    python src/experiments/banco.py --simulado            # paso 2 sin gasto, para probar
    python src/experiments/banco.py                       # paso 2 real (pide confirmación)

Escribe en `data/processed/banco/`: `candidatas.csv` y `clasificadas.csv` (metadatos, se
suben) y `cache.json` (no se sube).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-BA1. **Una fila por pregunta y por año en que se evalúa.** Para la EPC armonizada se elige
    el año más reciente de 2014-2019 (independiente de la población); si no hay, el más
    reciente de 2022-2024 (no independiente, se marca). 2025 no entra: no trae etiquetas
    (DI-AR1).

DI-BA2. **Lo que el modelo ve es solo el texto de la pregunta y sus categorías.** Nunca una
    respuesta ni un resultado. No responde nada por nadie: clasifica y redacta.

DI-BA3. **«Codigos_favorables»** son las categorías que significan estar de acuerdo con la
    pregunta tal como queda en la página. Con eso, el resultado real de un grupo es el
    porcentaje que eligió una de ellas, como el «sí» del metro y el Corredor
    (`PREGUNTAS_REALES_NUEVAS_SPECIFICATION.md`).

DI-BA4. **Filtro mecánico antes del modelo:** sin texto de pregunta, sin categorías, o con
    más de 12 categorías (abiertas o numéricas) no entra. Variables administrativas y de
    identificación tampoco. El módulo de elecciones y partidos de la ECP no entra.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import warnings
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "banco"
DDI_ECP = RAIZ / "data" / "raw" / "ecp" / "2023" / "DANE-DIMPE-ECP-2023.xml"
INVENTARIO = RAIZ / "data" / "processed" / "epc_inventario" / "items.csv"
CATALOGO = RAIZ / "data" / "processed" / "poblacion_epc2023" / "catalogo.json"
NS = {"d": "http://www.icpsr.umich.edu/DDI"}
MODULOS_ECP = ("Democracia", "Capital Social", "Participacion")
ANIOS_INDEPENDIENTES = (2014, 2015, 2016, 2017, 2018, 2019)
ANIOS_POBLACION = (2022, 2023, 2024)
MAX_CATEGORIAS = 12
MODELO = e9.MODELO
TEMPERATURA = 0.0

#: Fuente B: preguntas de coyuntura de la EPC, por año (`BANCO_PREGUNTAS_NUEVAS.md` §3).
COYUNTURA_EPC = {2016: r"^COY1$|^COY6$", 2017: r"^PI[1345]$", 2018: r"^COY10$", 2019: r"^JCV4$",
                 2022: r"^JCV4B$|^VE2_[123]$|^VE3_[1-6]$|^PC20_[123]$"}

#: Fuente D: biblioteca del CNC (`DATA_INVENTORY.md` §15). Metro y Corredor ya se vieron.
CNC = [
    {"id": "CNC_METRO", "texto": "¿Estás de acuerdo con mantener el metro elevado para Bogotá?",
     "categorias": "1=Sí; 2=No", "anio": 2023, "visto": True},
    {"id": "CNC_CORREDOR", "texto": "¿Estás de acuerdo con el Corredor Verde por la carrera séptima?",
     "categorias": "1=Sí; 2=No", "anio": 2023, "visto": True},
    {"id": "CNC_METRO10", "texto": "¿Usted cree que Bogotá va a tener metro funcionando en los próximos 10 años?",
     "categorias": "1=Sí; 2=No; 9=Ns/Nr", "anio": 2023, "visto": False},
    {"id": "CNC_PARQUE", "texto": "¿Usted actualmente deja a sus hijos en el parque con la confianza de que nada les va a pasar?",
     "categorias": "1=Sí; 2=No", "anio": 2023, "visto": False},
]

SISTEMA = (
    "Ayudas a armar un banco de preguntas de encuesta para probar un simulador de opinión pública de "
    "Bogotá. Te doy UNA pregunta de una encuesta real y sus categorías de respuesta. No respondas la "
    "pregunta: clasifícala.\n"
    "- \"opinion\": true si pide una opinión, actitud, evaluación, confianza, acuerdo o preferencia de la "
    "persona; false si pide un hecho, una conducta, un conocimiento o un dato.\n"
    "- \"electoral\": true si trata de votar, candidatos, partidos o elecciones.\n"
    "- \"pregunta_pagina\": la pregunta reescrita como la haría una página que pregunta a la población de "
    "Bogotá en tercera persona del singular («usted»), una sola idea, neutral, empezando por «¿Qué tan de "
    "acuerdo está con…», «¿Qué tan…» o «¿Está de acuerdo con…».\n"
    "- \"codigos_favorables\": la lista de códigos de las categorías que significan responder de forma "
    "favorable o de acuerdo con pregunta_pagina (por ejemplo, en una escala de 1 a 5 de nada a mucho, "
    "[4, 5]; en Sí/No, el código del Sí). No incluyas «no sabe» ni «no responde».\n"
    "- \"tema\": dos o tres palabras.\n"
    "Si opinion es false o electoral es true, pregunta_pagina y codigos_favorables pueden ir vacíos.\n"
    "Responde SOLO con un JSON, sin texto alrededor:\n"
    "{\"opinion\": true, \"electoral\": false, \"pregunta_pagina\": \"...\", \"codigos_favorables\": [4, 5], "
    "\"tema\": \"...\"}"
)


class BancoError(RuntimeError):
    """Algo impide armar el banco como está descrito."""


# --------------------------------------------------------------------------
# Paso 1: candidatas

def _cats(etq: dict) -> str:
    return "; ".join(f"{int(k)}={str(v).strip()}" for k, v in sorted(etq.items()))


def _limpio(s: str) -> str:
    return " ".join(str(s).split())


def candidatas_ecp(ruta: Path = DDI_ECP) -> list[dict]:
    """Fuente C: módulos de opinión de la ECP 2023, del diccionario del DANE."""
    r = ET.parse(ruta).getroot()
    archivos = {f.get("ID"): _limpio(f.findtext("d:fileTxt/d:fileName", default="", namespaces=NS))
                for f in r.findall(".//d:fileDscr", NS)}
    out = []
    for v in r.findall(".//d:var", NS):
        mod = archivos.get(v.get("files"), "")
        if not mod.startswith(MODULOS_ECP):
            continue
        texto = _limpio(v.findtext("d:qstn/d:qstnLit", default="", namespaces=NS)
                        or v.findtext("d:labl", default="", namespaces=NS))
        cats = {_limpio(c.findtext("d:catValu", default="", namespaces=NS)): _limpio(c.findtext("d:labl", default="", namespaces=NS))
                for c in v.findall("d:catgry", NS)}
        cats = {int(k): t for k, t in cats.items() if re.fullmatch(r"-?\d+", k)}
        if not texto or not cats or len(cats) > MAX_CATEGORIAS:                     # DI-BA4
            continue
        out.append({"id": f"ECP23_{v.get('name')}", "fuente": "ECP DANE", "anio": 2023, "variable": v.get("name"),
                    "modulo": mod.replace(".NSDstat", ""), "texto": texto, "categorias": _cats(cats),
                    "independiente": True, "localidad": False, "texto_incompleto": False, "visto": False})
    return out


def candidatas_epc_armonizadas() -> list[dict]:
    """Fuente A (DI-BA1)."""
    from src.population import epc_bcv as eb
    from src.population import poblacion_epc as pe
    cat = {c["variable"] for c in json.loads(CATALOGO.read_text(encoding="utf-8"))["dentro"]}
    inv = pd.read_csv(INVENTARIO)
    inv = inv[(inv.estado == "ok") & (inv.n_valido >= 0.8 * inv.n) & ~inv.variable.isin(cat)]
    dic = pd.read_excel(eb.resolver_dir_bcv() / "EPC Suprema.xlsx", "VARIABLES", header=1).set_index("VARIABLE_cod")
    etiquetas = {}
    out = []
    for v, g in inv.groupby("variable"):
        if v not in dic.index or dic.loc[v, "Tipo"] != "RU":
            continue
        indep = sorted(a for a in g.anio if a in ANIOS_INDEPENDIENTES)
        pobl = sorted(a for a in g.anio if a in ANIOS_POBLACION)
        anio = indep[-1] if indep else (pobl[-1] if pobl else None)
        if anio is None:
            continue
        cod = str(g[g.anio == anio].codigo.iloc[0]).upper()
        if anio not in etiquetas:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                etiquetas[anio] = {k.upper(): x for k, x in pe._etiquetas(eb.archivo_del_anio(anio)).items()}
        e = etiquetas[anio].get(cod)
        if not e or len(e) > MAX_CATEGORIAS:
            continue
        out.append({"id": f"EPC{anio}_{v}", "fuente": "EPC armonizada", "anio": anio, "variable": cod,
                    "modulo": str(dic.loc[v, "VARIABLE_tag"]), "texto": _limpio(dic.loc[v, "PREGUNTA_tag"]),
                    "categorias": _cats(e), "independiente": bool(indep), "localidad": True,
                    "texto_incompleto": False, "visto": False})
    return out


def candidatas_epc_coyuntura() -> list[dict]:
    """Fuente B: etiquetas del .dta, cortadas a ~80 caracteres (se marca)."""
    from src.population import epc_bcv as eb
    from src.population import poblacion_epc as pe
    out = []
    for anio, patron in COYUNTURA_EPC.items():
        ruta = eb.archivo_del_anio(anio)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with pd.io.stata.StataReader(ruta) as r:
                lab = r.variable_labels()
            etq = pe._etiquetas(ruta)
        for v, l in lab.items():
            if not re.search(patron, v) or v not in etq or len(etq[v]) > MAX_CATEGORIAS:
                continue
            out.append({"id": f"EPC{anio}_{v}", "fuente": "EPC coyuntura", "anio": anio, "variable": v.upper(),
                        "modulo": "", "texto": _limpio(l), "categorias": _cats(etq[v]),
                        "independiente": anio in ANIOS_INDEPENDIENTES, "localidad": True,
                        "texto_incompleto": len(l) >= 78, "visto": False})
    return out


def candidatas_cnc() -> list[dict]:
    return [{**c, "fuente": "Biblioteca CNC", "variable": "", "modulo": "", "independiente": True,
             "localidad": True, "texto_incompleto": False} for c in CNC]


def candidatas() -> pd.DataFrame:
    filas = candidatas_epc_armonizadas() + candidatas_epc_coyuntura() + candidatas_ecp() + candidatas_cnc()
    df = pd.DataFrame(filas)
    if df.id.duplicated().any():
        raise BancoError(f"Identificadores repetidos: {sorted(df[df.id.duplicated()].id)}")
    return df


# --------------------------------------------------------------------------
# Paso 2: clasificación (DI-BA2, DI-BA3)

def prompt(fila: dict) -> str:
    extra = " (El texto puede venir cortado al final.)" if fila.get("texto_incompleto") else ""
    mod = f"Módulo o tema de la encuesta: {fila['modulo']}\n" if fila.get("modulo") else ""
    return f"{mod}PREGUNTA:{extra}\n{fila['texto']}\nCATEGORÍAS:\n{fila['categorias']}"


def parsear(texto: Optional[str], categorias: str) -> Optional[dict]:
    d = e9._json_de(texto)
    if not isinstance(d, dict) or not isinstance(d.get("opinion"), bool) or not isinstance(d.get("electoral"), bool):
        return None
    codigos = {int(m) for m in re.findall(r"(-?\d+)=", categorias)}
    fav = d.get("codigos_favorables") or []
    if not isinstance(fav, list):
        return None
    try:
        fav = [int(x) for x in fav]
    except (TypeError, ValueError):
        return None
    util = d["opinion"] and not d["electoral"]
    if util and (not fav or not set(fav) <= codigos or not str(d.get("pregunta_pagina", "")).strip()):
        return None
    return {"opinion": d["opinion"], "electoral": d["electoral"], "pregunta_pagina": str(d.get("pregunta_pagina", "")).strip(),
            "codigos_favorables": fav, "tema": str(d.get("tema", "")).strip(), "util": bool(util)}


def clasificar(df: pd.DataFrame, llamar, cache: e9.Cache, modelo: str) -> pd.DataFrame:
    filas = []
    for f in df.to_dict("records"):
        r = parsear(e9.pedir(llamar, cache, modelo, TEMPERATURA, SISTEMA, prompt(f), 0)[0], f["categorias"])
        filas.append({**f, "clasificacion_valida": r is not None,
                      **({k: (json.dumps(v) if isinstance(v, list) else v) for k, v in r.items()} if r else {"util": False})})
    return pd.DataFrame(filas)


def modelo_simulado():
    def llamar(modelo, sistema, usuario, temp):
        cods = [int(x) for x in re.findall(r"(-?\d+)=", usuario.split("CATEGORÍAS:")[-1])]
        pos = [c for c in cods if 0 < c < 90]
        return json.dumps({"opinion": True, "electoral": False, "pregunta_pagina": "¿Qué tan de acuerdo está con X?",
                           "codigos_favorables": pos[-1:] or cods[:1], "tema": "simulado"})
    return llamar


def main(argv=None, entrada=input) -> int:
    ap = argparse.ArgumentParser(description="Banco de preguntas nuevas (docs/BANCO_PREGUNTAS_NUEVAS.md).")
    ap.add_argument("--candidatas", action="store_true", help="solo el paso 1, sin gasto")
    ap.add_argument("--simulado", action="store_true", help="paso 2 con un modelo simulado, sin gasto")
    args = ap.parse_args(argv)
    SALIDA.mkdir(parents=True, exist_ok=True)
    df = candidatas()
    df.to_csv(SALIDA / "candidatas.csv", index=False, encoding="utf-8")
    print(f"{len(df)} candidatas: {df.fuente.value_counts().to_dict()}; independientes {int(df.independiente.sum())}; "
          f"con texto cortado {int(df.texto_incompleto.sum())}")
    if args.candidatas:
        return 0
    salida = SALIDA / ("simulado" if args.simulado else "")
    salida.mkdir(parents=True, exist_ok=True)
    cache = e9.Cache(salida / "cache.json")
    if args.simulado:
        llamar, modelo = modelo_simulado(), e9.MODELO_SIMULADO
    else:
        llamar, modelo = e9.cliente_real(), MODELO
        pend = [(SISTEMA, prompt(f), 300) for f in df.to_dict("records")
                if e9.Cache.clave(modelo, TEMPERATURA, SISTEMA, prompt(f), 0) not in cache]
        if not e9.confirmar_gasto(pend, entrada, e9.gasto_registrado(cache)):
            print("No se gastó nada.")
            return 1
    try:
        cl = clasificar(df, llamar, cache, modelo)
    except e9.Experimento9Error as e:
        print(f"\nERROR: {e}\nLo que respondió quedó en la caché; al volver a correr solo se hace lo que falta.")
        return 1
    cl.to_csv(salida / "clasificadas.csv", index=False, encoding="utf-8")
    u = cl[cl.util]
    print(f"clasificación válida {int(cl.clasificacion_valida.sum())} de {len(cl)}; útiles (opinión, no electoral) {len(u)}")
    print(u.groupby("fuente").size().to_dict(), f"independientes {int(u.independiente.sum())}")
    print(f"gasto: {e9.gasto_registrado(cache)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
