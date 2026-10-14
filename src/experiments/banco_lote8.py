"""
Octavo lote del banco de preguntas nuevas: las preguntas de opinión de la EPC 2025 que no están en el catálogo
(`docs/BANCO_PREGUNTAS_NUEVAS.md` §17). Sin API.

Uso:
    python src/experiments/banco_lote8.py --tabla       # las 26 preguntas (no lee datos)
    python src/experiments/banco_lote8.py --sorteo      # escribe sorteo_lote8.csv
    python src/experiments/banco_lote8.py --reales      # resultados reales de las de práctica

DECISIONES DE IMPLEMENTACIÓN
============================

DI-BL20. **«No sabe» y «no aplica» con una etiqueta que la regla reconoce.** El formulario llama al 90 «No recibió», «No he
    usado este servicio», «No uso servicios financieros digitales»… y la regla del banco (DI-BR1, `poblacion_epc.NSNR`) solo
    reconoce «no sabe», «no aplica» y parecidas. En `categorias`, el 90 y el 91 van como «No sabe» o «No aplica: …», con el
    texto del formulario después de los dos puntos.

DI-BL21. **El texto de cada pregunta va escrito a mano** a partir del formulario: la pregunta de la batería con el ítem
    dentro de la frase, y «Bogotá» donde el formulario dice «[ciudad/territorio]». Las etiquetas de la escala son las del
    formulario.

DI-BL22. **Mismo cálculo que los lotes 3 y 5** (`banco_lote3._calcular`): solo cambian las columnas y el peso.
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import banco as ba                    # noqa: E402
from src.experiments import banco_lote3 as b3              # noqa: E402

SORTEO = ba.SALIDA / "sorteo_lote8.csv"
REALES = ba.SALIDA / "reales_practica_lote8.json"
SEMILLA = 20261014
FUENTE = "EPC 2025"
COLS = {"w": "FACTOR1", "sexo": "DMO_1", "edad": "DMO_3_1", "estrato": "DMO_4_1", "localidad": "LOCALIDAD"}


def _escala(etiquetas: list[str], no: str = "No sabe", no2: str | None = None) -> str:
    """DI-BL20: «1=…; …; 90=…» (y 91 si hace falta)."""
    s = "; ".join(f"{i}={e}" for i, e in enumerate(etiquetas, 1)) + f"; 90={no}"
    return s + (f"; 91={no2}" if no2 else "")


SAT = ["Muy insatisfecho", "Algo insatisfecho", "Ni satisfecho ni insatisfecho", "Algo satisfecho", "Muy satisfecho"]
CONF = ["No confío nada", "Desconfío", "Ni confío ni desconfío", "Confío", "Confío plenamente"]
GRADO = ["Nada", "Poco", "Algo", "Mucho", "Totalmente"]
PROB = ["Nada probable", "Poco probable", "Algo probable", "Muy probable", "Totalmente probable"]
COMP = ["Muy mal", "Mal", "Ni bueno ni malo", "Bien", "Muy bien"]
GEST = ["Muy mala gestión", "Mala gestión", "Regular gestión", "Buena gestión", "Muy buena gestión"]
COLEGIO = "Pensando en los estudiantes de colegio de su hogar, ¿qué tan satisfecho(a) está con {} del colegio?"
SANCION = ("¿Qué tan probable considera que sería recibir un castigo o amonestación de las autoridades si {} en Bogotá?")
CONFIA = "¿Qué tanto confía en {}?"
F45 = [4, 5]

#: §17: (variable, familia, texto en la página, categorías, favorables)
PREGUNTAS = [
    ("FIN_3", "FIN3", "¿Qué tanto confía en los servicios financieros digitales (pagos, transferencias, ahorros e inversiones "
     "en plataformas digitales)?",
     _escala(["Desconfío mucho", "Desconfío", "Ni confío ni desconfío", "Confío algo", "Confío mucho"],
             "No aplica: no usa servicios financieros digitales"), F45),
    ("CTI_3", "CTI3", "¿Qué tanto confía en los resultados que le dan las herramientas de inteligencia artificial que usa?",
     _escala(CONF, "No aplica: no usa herramientas de inteligencia artificial"), F45),
    ("CTI_4", "CTI_IMPACTO", "¿Qué tan de acuerdo está con que la inteligencia artificial lo hará más productivo en su trabajo "
     "en el futuro?", _escala(GRADO, "No sabe / no tiene opinión"), F45),
    ("CTI_5", "CTI_IMPACTO", "¿Qué tan de acuerdo está con que la inteligencia artificial le dificultará conseguir trabajo en el "
     "futuro?", _escala(GRADO, "No sabe / no tiene opinión"), F45),
    ("EDU_4", "EDU_COLEGIO", COLEGIO.format("el desempeño de los profesores"), _escala(SAT), F45),
    ("EDU_5", "EDU_COLEGIO", COLEGIO.format("la infraestructura física"), _escala(SAT), F45),
    ("EDU_6", "EDU_COLEGIO", COLEGIO.format("la infraestructura tecnológica"), _escala(SAT), F45),
    ("EDU_7", "EDU_COLEGIO", COLEGIO.format("el material de apoyo para la enseñanza"), _escala(SAT), F45),
    ("EDU_8", "EDU_COLEGIO", COLEGIO.format("el Plan de Alimentación Escolar (PAE)"), _escala(SAT), F45),
    ("EDU_9", "EDU_COLEGIO", COLEGIO.format("los procesos académicos"), _escala(SAT), F45),
    ("EDU_10", "EDU_COLEGIO", COLEGIO.format("el transporte escolar"), _escala(SAT), F45),
    ("SAL_1", "SAL1", "Si usó algún servicio de salud en el último año, ¿qué tan satisfecho(a) estuvo en general con el "
     "servicio recibido?", _escala(SAT, "No aplica: no recibió"), F45),
    ("BOG_3", "BOG3", "¿Qué tan satisfecho(a) está en general con los servicios de salud a la primera infancia (controles "
     "prenatales, vacunación, pediatría, crecimiento y desarrollo) en el último año?",
     _escala(SAT, "No aplica: no ha usado este servicio"), F45),
    ("JUS_1", "JUS1", "Si requirió del sistema de justicia en el último año, ¿qué tan satisfecho(a) está con el sistema de "
     "justicia en Colombia (juzgados, Defensoría del Pueblo, Fiscalía, entre otros)?",
     _escala(["Muy insatisfecho", "Insatisfecho", "Ni satisfecho ni insatisfecho", "Satisfecho", "Muy satisfecho"],
             "No aplica: no requirió el sistema de justicia"), F45),
    ("MOV_6", "MOV_SATISFACCION", "¿Qué tan satisfecho(a) está con el estado de las vías vehiculares de Bogotá?", _escala(SAT),
     F45),
    ("CON_4", "CON_CONFIANZA", CONFIA.format("la Alcaldía de Bogotá"), _escala(CONF), F45),
    ("CON_5", "CON_CONFIANZA", CONFIA.format("el Concejo de Bogotá"), _escala(CONF), F45),
    ("CON_6", "CON_CONFIANZA", CONFIA.format("el Congreso de la República"), _escala(CONF), F45),
    ("CON_7", "CON_CONFIANZA", CONFIA.format("el Gobierno Nacional (la Presidencia)"), _escala(CONF), F45),
    ("CCC_1", "CCC_COMPORTAMIENTO", "¿Cómo cree que se comportan los habitantes de Bogotá en general frente al cumplimiento de "
     "las normas de convivencia?", _escala(COMP), F45),
    ("CCC_16", "CCC_SANCION", SANCION.format("infringiera las normas y señales de tránsito"), _escala(PROB), F45),
    ("CCC_18", "CCC_SANCION", SANCION.format("dañara el espacio público"), _escala(PROB), F45),
    ("CCC_20", "CCC_SANCION", SANCION.format("arrojara basura, desperdicios o escombros en la vía pública"), _escala(PROB), F45),
    ("CCC_22", "CCC_SANCION", SANCION.format("incumpliera sus obligaciones de créditos con bancos"), _escala(PROB), F45),
    ("GOB_4", "GOB4", "¿La imagen que usted tiene del alcalde Carlos Fernando Galán es favorable o desfavorable?",
     "1=Desfavorable; 2=Favorable; 90=No sabe / no tiene opinión; 91=No sabe: no lo conoce", [2]),
    ("GOB_7", "GOB_GESTION", "¿Cómo califica la gestión del Congreso?", _escala(GEST, "No sabe: no lo conoce o no tiene opinión"),
     F45),
]


class Lote8Error(RuntimeError):
    """Algo no cuadra con lo pre-registrado en §17."""


def tabla() -> pd.DataFrame:
    """Las 26 preguntas como filas del banco (DI-BL21). No lee datos."""
    filas = [{"id": f"EPC25_{v}", "familia": f"EPC25_{fam}", "ambito": "Bogotá", "fuente": FUENTE, "anio": 2025,
              "variable": v, "independiente": False, "pregunta_pagina": txt, "codigos_favorables": json.dumps(fav),
              "categorias": cats, "tema": f"EPC 2025 {fam}"} for v, fam, txt, cats, fav in PREGUNTAS]
    return pd.DataFrame(filas)


def base_epc25():
    """(x de una fila del sorteo, peso, grupos, localidad) — DI-BL22."""
    from src.population import epc_bcv as eb
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        d = pd.read_stata(eb.archivo_del_anio(2025), convert_categoricals=False, preserve_dtypes=False)
    d.columns = [c.upper() for c in d.columns]
    faltan = [v for v, *_ in PREGUNTAS if v not in d.columns] + [c for c in COLS.values() if c not in d.columns]
    if faltan:
        raise Lote8Error(f"No están en la EPC 2025: {faltan}")
    num = lambda c: pd.to_numeric(d[c], errors="coerce")                       # noqa: E731
    sexo = num(COLS["sexo"]).map({1: "Hombres", 2: "Mujeres"})
    estrato = num(COLS["estrato"]).where(num(COLS["estrato"]).between(1, 6))
    loc = num(COLS["localidad"])
    loc = loc.where(loc.between(1, 19)).astype("Int64").astype(str).replace("<NA>", None)
    g = b3._grupos(sexo, num(COLS["edad"]), estrato)
    return (lambda f: num(str(f["variable"]).upper())), num(COLS["w"]), g, loc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tabla", action="store_true")
    ap.add_argument("--sorteo", action="store_true")
    ap.add_argument("--reales", action="store_true")
    a = ap.parse_args(argv)
    if a.tabla:
        t = tabla()
        print(f"{len(t)} preguntas en {t.familia.nunique()} familias")
        print(t[["id", "familia", "pregunta_pagina"]].to_string(index=False))
    if a.sorteo:
        if SORTEO.exists():
            raise Lote8Error(f"{SORTEO.name} ya existe: el sorteo se hace una sola vez.")
        s = b3.sortear(tabla(), SEMILLA)
        s.to_csv(SORTEO, index=False, encoding="utf-8")
        print(s.groupby("conjunto").agg(preguntas=("id", "size"), familias=("familia", "nunique")).to_dict())
        print(s.groupby("conjunto").familia.unique().to_dict())
    if a.reales:
        r = b3._calcular(pd.read_csv(SORTEO), *base_epc25())
        REALES.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        exc = {k: v["excluida"] for k, v in r.items() if v["excluida"]}
        ns = [v["n"] for v in r.values() if not v["excluida"]]
        print(f"{len(r)} de práctica; excluidas por estructura {len(exc)} {exc or ''}; pares claros "
              f"{sum(len(v['pares_claros']) for v in r.values() if not v['excluida'])}; "
              f"n válidas {min(ns) if ns else '-'}-{max(ns) if ns else '-'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
