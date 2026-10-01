"""
Puente sin base: ¿el simulador reconoce cuándo una pregunta nueva no se parece a nada
de lo que la encuesta midió, y lo dice, sin estropear lo que ya funcionaba?

Pre-registro: `docs/PUENTE_SIN_BASE_SPECIFICATION.md` (clases revisadas por Daniel el
1/10, sin cambios). Este módulo lo ejecuta y no decide nada que el documento no haya
decidido.

    30 preguntas nuevas (10 con pariente directo, 10 solo del tema general, 10 sin
    pariente) con el prompt v2 y el catálogo de 102; y la regresión: las 12 escondidas
    del puente original con el prompt v2 y el catálogo de 91.

Uso:
    python src/experiments/puente_sin_base.py --simulado    # sin gasto, para probar
    python src/experiments/puente_sin_base.py               # 126 llamadas reales (pide confirmación)

Escribe `data/processed/puente_sin_base/resultado.json`; la caché en `cache.json` (no se sube).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-SB1. **El prompt v2 es el texto del pre-registro, letra por letra.** Una prueba lo
    compara con el bloque de código de §2 del documento.

DI-SB2. **Qué es una respuesta válida** (§2). Con `sin_base: true`: lista de preguntas
    vacía y nivel nulo o ausente. Con `sin_base: false` (o ausente): lo mismo que exige
    `puente.parsear` (1 a 5 preguntas del catálogo, sentido, peso 1-3, nivel en la
    escala) más una `fuerza` en {fuerte, media, debil}. Lo demás es una respuesta rota.

DI-SB3. **El veredicto de una pregunta es la mayoría de sus 3 llamadas** (§4): «sin
    base» si al menos 2 lo dicen. Una llamada rota cuenta como «no sin base, fuerza
    débil». Para P3, una A «tiene fuerza» si al menos 2 de sus llamadas dicen fuerte o
    media; una B «es débil» si al menos 2 dicen débil o sin base.

DI-SB4. **En la regresión, una respuesta «sin base» cuenta como un puente vacío**
    (ρ_ind = 0, r_loc = 0, como DI-PU3). Es lo conservador para R2: negar un puente que
    funcionaba no puede ayudar a pasar el umbral.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import puente as pu                   # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "puente_sin_base"
ESPECIFICACION = RAIZ / "docs" / "PUENTE_SIN_BASE_SPECIFICATION.md"
FUERZAS = ("fuerte", "media", "debil")
ESCALA = ["Totalmente en desacuerdo", "En desacuerdo", "Ni de acuerdo ni en desacuerdo", "De acuerdo",
          "Totalmente de acuerdo"]
INICIO = "¿Qué tan de acuerdo está con que "

SISTEMA_V2 = (
    "Eres un asistente de métodos de encuesta. Te doy una PREGUNTA NUEVA y un CATÁLOGO de preguntas\n"
    "que ya se hicieron a las mismas personas en Bogotá (Encuesta de Percepción Ciudadana 2023).\n"
    "Tu tarea es construir un PUENTE: elegir de 1 a 5 preguntas del catálogo cuyas respuestas\n"
    "permitan ordenar a las personas según cómo responderían la pregunta nueva, y proponer la\n"
    "media esperada de la pregunta nueva en Bogotá.\n"
    "Para cada pregunta elegida da: su código; el sentido, '+' si los códigos más altos de esa\n"
    "pregunta van con códigos más altos de la pregunta nueva, '-' si van con códigos más bajos;\n"
    "y un peso de 1 a 3 según qué tan relacionada está.\n"
    "Califica la FUERZA del puente: \"fuerte\" si el catálogo mide el mismo objeto o servicio que la\n"
    "pregunta nueva; \"media\" si mide algo muy cercano; \"debil\" si solo comparte el tema general\n"
    "(por ejemplo, la evaluación del gobierno en un sector frente a una medida concreta de ese sector).\n"
    "Si ninguna pregunta del catálogo permite razonablemente ordenar a las personas para la pregunta\n"
    "nueva, porque depende de gustos, valores o temas que el catálogo no mide, NO fuerces un puente:\n"
    "responde con \"preguntas\": [] y \"sin_base\": true, y explica por qué en la justificación.\n"
    "Responde SOLO con un JSON, sin texto alrededor, con esta forma:\n"
    "{\"preguntas\": [{\"codigo\": \"XX\", \"sentido\": \"+\", \"peso\": 2}], \"fuerza\": \"media\", \"sin_base\": false,\n"
    "\"nivel\": 3.1, \"justificacion\": \"una o dos frases\"}\n"
    "El nivel es la media esperada en la escala de códigos de la pregunta nueva; si sin_base es true,\n"
    "usa null."
)

#: §3: (id, clase, final de la pregunta). Todas empiezan por INICIO.
PREGUNTAS = [
    ("A1", "A", "se construyan más ciclorrutas en Bogotá?"),
    ("A2", "A", "se instalen más luminarias en calles y parques?"),
    ("A3", "A", "se aumente el número de policías que patrullan los barrios?"),
    ("A4", "A", "se siembren más árboles en las calles de la ciudad?"),
    ("A5", "A", "se instalen más baños públicos en la ciudad?"),
    ("A6", "A", "se pongan más canecas de basura en el espacio público?"),
    ("A7", "A", "se aumente la frecuencia de recolección de basuras en los barrios?"),
    ("A8", "A", "se controle con más rigor el ruido de bares y vecinos?"),
    ("A9", "A", "se cambien los buses por eléctricos para mejorar la calidad del aire?"),
    ("A10", "A", "haya más agentes de tránsito en las vías principales?"),
    ("B1", "B", "todos los colegios públicos tengan jornada única?"),
    ("B2", "B", "se prohíba la venta y el uso de pólvora en diciembre?"),
    ("B3", "B", "cada localidad tenga un hospital público abierto las 24 horas?"),
    ("B4", "B", "el Distrito subsidie el arriendo de los jóvenes?"),
    ("B5", "B", "el Distrito dé una renta básica a los hogares pobres?"),
    ("B6", "B", "se formalice a los vendedores ambulantes con puestos fijos?"),
    ("B7", "B", "el Distrito cree empleos temporales para jóvenes?"),
    ("B8", "B", "se cobre un impuesto a las viviendas desocupadas?"),
    ("B9", "B", "se cree un sistema público de cuidado para personas mayores?"),
    ("B10", "B", "haya un día sin carro particular cada semana en toda la ciudad?"),
    ("C1", "C", "vuelvan las corridas de toros a la Plaza de La Santamaría?"),
    ("C2", "C", "se cambie el himno de Bogotá?"),
    ("C3", "C", "Bogotá tenga un día festivo propio por su cumpleaños?"),
    ("C4", "C", "se permita tener gallinas en las casas de la ciudad?"),
    ("C5", "C", "suene reguetón en los eventos oficiales del Distrito?"),
    ("C6", "C", "la ciudad vuelva a llamarse oficialmente «Santa Fe de Bogotá»?"),
    ("C7", "C", "se permita entrar con perros a los restaurantes?"),
    ("C8", "C", "Bogotá adelante su hora oficial para aprovechar más la luz del día?"),
    ("C9", "C", "se construya un monumento a los deportistas olímpicos colombianos?"),
    ("C10", "C", "la ciudad adopte un animal símbolo oficial, como el oso de anteojos?"),
]


class PuenteSinBaseError(RuntimeError):
    """Algo impide correr la prueba como está pre-registrada."""


def ficha_nueva(texto: str) -> dict:
    return {"variable": "NUEVA", "codigo": "NUEVA", "pregunta": INICIO + texto, "escala": [1, 2, 3, 4, 5],
            "etiquetas": {str(i + 1): e for i, e in enumerate(ESCALA)}}


def parsear_v2(texto: Optional[str], f_esc: dict, fichas: dict) -> Optional[dict]:
    """DI-SB2: None si la respuesta está rota."""
    d = e9._json_de(texto)
    if not isinstance(d, dict):
        return None
    sb = d.get("sin_base", False)
    if not isinstance(sb, bool):
        return None
    if sb:
        if d.get("preguntas") not in ([], None) or d.get("nivel") is not None:
            return None
        return {"sin_base": True, "fuerza": None, "preguntas": [], "nivel": None,
                "justificacion": str(d.get("justificacion", ""))}
    fuerza = str(d.get("fuerza", "")).strip().lower().replace("é", "e")
    if fuerza not in FUERZAS:
        return None
    r = pu.parsear(texto, f_esc, fichas)
    if r is None:
        return None
    return {**r, "sin_base": False, "fuerza": fuerza}


def recolectar(fichas_esc: dict, fichas: dict, llamar, cache: e9.Cache, modelo: str) -> dict[str, list]:
    out = {}
    for v, f in fichas_esc.items():
        u = pu.prompt(f, fichas)
        out[v] = [parsear_v2(e9.pedir(llamar, cache, modelo, pu.TEMPERATURA, SISTEMA_V2, u, rep)[0], f, fichas)
                  for rep in range(pu.REPETICIONES)]
    return out


# --------------------------------------------------------------------------
# Veredictos y regla

def veredicto(llamadas: list[Optional[dict]]) -> dict:
    """DI-SB3."""
    sb = sum(bool(r and r["sin_base"]) for r in llamadas)
    fuerzas = [("sin_base" if r and r["sin_base"] else (r["fuerza"] if r else "debil")) for r in llamadas]
    return {"sin_base": sb >= 2, "llamadas_sin_base": sb, "rotas": sum(r is None for r in llamadas),
            "fuerzas": fuerzas,
            "fuerte_o_media": sum(f in ("fuerte", "media") for f in fuerzas) >= 2,
            "debil_o_sin_base": sum(f in ("debil", "sin_base") for f in fuerzas) >= 2}


def a_puente_original(r: Optional[dict]) -> Optional[dict]:
    """DI-SB4: para `puente.analizar`, «sin base» es un puente vacío (None)."""
    return None if r is None or r["sin_base"] else r


def evaluar(v30: dict[str, dict], regresion: dict) -> dict:
    """§5 y §6. `v30`: id -> veredicto; `regresion`: {'veredictos': {...}, 'p1_personas': {...}}."""
    clase = {i: c for i, c, _ in PREGUNTAS}
    cuenta = lambda c, campo: sum(v[campo] for i, v in v30.items() if clase[i] == c)   # noqa: E731
    sb_c, sb_a = cuenta("C", "sin_base"), cuenta("A", "sin_base")
    sb_reg = sum(v["sin_base"] for v in regresion["veredictos"].values())
    r2 = sum(regresion["p1_personas"].values())
    fa, db = cuenta("A", "fuerte_o_media"), cuenta("B", "debil_o_sin_base")
    p = {
        "P1": {"umbral": "sin_base en ≥ 7 de las 10 C", "cuenta": sb_c, "se_cumple": sb_c >= 7},
        "P2": {"umbral": "sin_base en ≤ 1 de las 10 A", "cuenta": sb_a, "se_cumple": sb_a <= 1},
        "R1": {"umbral": "sin_base en ≤ 1 de las 12 escondidas", "cuenta": sb_reg, "se_cumple": sb_reg <= 1},
        "R2": {"umbral": "ρ_ind > azar 95 y > demografía en ≥ 9 de 12", "cuenta": r2, "se_cumple": r2 >= 9},
        "P3": {"umbral": "fuerte o media en ≥ 8 de las 10 A, y débil o sin_base en ≥ 6 de las 10 B",
               "cuenta_A": fa, "cuenta_B": db, "se_cumple": fa >= 8 and db >= 6},
        "P4": {"umbral": "se reporta", "B_sin_base": cuenta("B", "sin_base")},
    }
    if not (p["R1"]["se_cumple"] and p["R2"]["se_cumple"]):
        lectura = ("no_adoptar", "No se adopta el prompt v2: rompe lo validado. La página sigue igual y añade un "
                                 "aviso general sobre preguntas que no se parecen a nada de la encuesta.")
        fuerza = False
    elif p["P1"]["se_cumple"] and p["P2"]["se_cumple"]:
        lectura = ("adoptar", "Se adopta el prompt v2: si el modelo dice sin_base, la página no responde y dice "
                              "«No hay en la encuesta con qué suponer esta pregunta» con su razón.")
        fuerza = p["P3"]["se_cumple"]
    else:
        lectura = ("sin_base_no_confiable", "No se usa sin_base en la página: no es confiable.")
        fuerza = p["P3"]["se_cumple"]
    return {"predicciones": p, "lectura": lectura[0], "regla": lectura[1], "mostrar_fuerza": bool(fuerza)}


# --------------------------------------------------------------------------
# Corrida

def modelo_simulado(fichas: dict, semilla: int = pu.SEMILLA):
    """Dice «sin base» a las C y un puente válido a las demás: prueba el circuito, no mide."""
    rng = np.random.default_rng(semilla)
    cods = list(fichas)
    sin = [INICIO + t for _, c, t in PREGUNTAS if c == "C"]

    def llamar(modelo, sistema, usuario, temp):
        if any(s in usuario for s in sin):
            return json.dumps({"preguntas": [], "sin_base": True, "nivel": None, "justificacion": "simulado"})
        ps = [{"codigo": str(c), "sentido": "+", "peso": 2} for c in rng.choice(cods, 2, replace=False)]
        return json.dumps({"preguntas": ps, "fuerza": "media", "sin_base": False, "nivel": 3.0,
                           "justificacion": "simulado"})
    return llamar


def main(argv=None, entrada=input) -> int:
    ap = argparse.ArgumentParser(description="Puente sin base (docs/PUENTE_SIN_BASE_SPECIFICATION.md).")
    ap.add_argument("--simulado", action="store_true", help="modelo simulado, sin gasto")
    args = ap.parse_args(argv)
    from src.consulta import reformular as rf
    from src.population import poblacion_epc as pe
    catalogo = rf.cargar_catalogo()                                                   # 102
    fichas_esc, fichas_91 = pu.cargar_fichas()                                       # 12 y 91
    if len(catalogo) != 102 or len(fichas_91) != 91:
        raise PuenteSinBaseError(f"Catálogos de {len(catalogo)} y {len(fichas_91)}; el pre-registro dice 102 y 91.")
    nuevas = {i: ficha_nueva(t) for i, _, t in PREGUNTAS}
    salida = SALIDA / ("simulado" if args.simulado else "")
    cache = e9.Cache(salida / "cache.json")
    if args.simulado:
        llamar, modelo = modelo_simulado(catalogo), e9.MODELO_SIMULADO
    else:
        llamar, modelo = e9.cliente_real(), pu.MODELO
        pend = [(SISTEMA_V2, u, 400) for fs, cat in ((nuevas, catalogo), (fichas_esc, fichas_91))
                for f in fs.values() for u in [pu.prompt(f, cat)] for rep in range(pu.REPETICIONES)
                if e9.Cache.clave(modelo, pu.TEMPERATURA, SISTEMA_V2, u, rep) not in cache]
        if not e9.confirmar_gasto(pend, entrada, e9.gasto_registrado(cache)):
            print("No se gastó nada.")
            return 1
    try:
        r30 = recolectar(nuevas, catalogo, llamar, cache, modelo)
        rreg = recolectar(fichas_esc, fichas_91, llamar, cache, modelo)
    except e9.Experimento9Error as e:
        g = e9.gasto_registrado(cache)
        print(f"\nERROR: {e}\nLas {g['llamadas']} llamadas que respondieron quedaron en la caché "
              f"(USD {g['costo_usd']:.3f}); al volver a correr solo se hacen las que faltan.")
        return 1
    v30 = {i: veredicto(r) for i, r in r30.items()}
    # regresión, medida como el puente original (DI-SB4)
    donante = pe.cargar_donante()
    datos = pu.Datos(donante, fichas_91, fichas_esc)
    col = {c.upper(): c for c in donante.columns}
    crudos = {}
    for v, f in fichas_91.items():
        x = pd.to_numeric(donante[col[str(f["codigo"]).upper()]], errors="coerce").to_numpy(float)
        crudos[v] = (x, np.isin(x, f["escala"]))
    a = pu.analizar(datos, fichas_esc, fichas_91, {v: [a_puente_original(x) for x in rs] for v, rs in rreg.items()},
                    crudos)
    p1 = {v: bool(p["rho_ind"] > p["azar"]["rho_ind_p95"] and p["rho_ind"] > p["demografia"]["rho_ind"])
          for v, p in a["por_pregunta"].items()}
    reg = {"veredictos": {v: veredicto(rs) for v, rs in rreg.items()}, "p1_personas": p1,
           "rho_ind": {v: p["rho_ind"] for v, p in a["por_pregunta"].items()}}
    ev = evaluar(v30, reg)
    justif = {i: [r["justificacion"] if r else None for r in rs] for i, rs in r30.items()}
    puentes = {i: [r["preguntas"] if r else None for r in rs] for i, rs in r30.items()}
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "resultado.json").write_text(json.dumps(
        {"preguntas": {i: {"clase": c, "texto": INICIO + t, **v30[i], "puentes": puentes[i], "justificaciones": justif[i]}
                       for i, c, t in PREGUNTAS},
         "regresion": reg, **ev, "modelo": modelo, "gasto": e9.gasto_registrado(cache)},
        ensure_ascii=False, indent=2, default=float), encoding="utf-8")
    print(f"{'id':4s} clase  sin_base  fuerzas")
    for i, c, _ in PREGUNTAS:
        v = v30[i]
        print(f"{i:4s} {c:5s}  {'SÍ' if v['sin_base'] else 'no':8s}  {' '.join(v['fuerzas'])}{'  (rotas: %d)' % v['rotas'] if v['rotas'] else ''}")
    print("\nregresión (12 escondidas):")
    for v, x in reg["veredictos"].items():
        print(f"  {v:6s} sin_base {'SÍ' if x['sin_base'] else 'no':3s}  ρ_ind {reg['rho_ind'][v]:5.2f}  "
              f"{'gana' if p1[v] else 'no gana'}  {' '.join(x['fuerzas'])}")
    for k, p in ev["predicciones"].items():
        estado = "" if "se_cumple" not in p else ("se cumple" if p["se_cumple"] else "NO se cumple")
        print(f"  {k} {estado} — {p['umbral']} {({x: y for x, y in p.items() if x not in ('umbral', 'se_cumple')})}")
    print(f"\nLectura: {ev['lectura']} — {ev['regla']}\nMostrar la fuerza: {'sí' if ev['mostrar_fuerza'] else 'no'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
