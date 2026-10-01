"""
Práctica del puente: sobre las preguntas de PRÁCTICA del banco (`BANCO_PREGUNTAS_NUEVAS.md`
§9), ¿qué versión del puente acierta mejor qué grupos están más de acuerdo?

No es un pre-registro: es la fase de práctica, para probar y comparar versiones todas las
veces que haga falta. Lo que se aprenda aquí se lleva después, pre-registrado, al banco
guardado. Este módulo solo lee el banco con `banco.practica()`.

    Versiones (VERSIONES): «actual» (el prompt v2 de la página) y «afectados» (el v2 más
    un párrafo que pide pensar en a quién afecta, quién lo propone y qué valores lo sostienen).
    Referencias, sin API: el azar (200 puentes por pregunta) y el «tono general».

Uso:
    python src/experiments/practica_puente.py --version actual --simulado
    python src/experiments/practica_puente.py --version actual            # llamadas reales (pide confirmación)
    python src/experiments/practica_puente.py --version afectados

Escribe `data/processed/practica_puente/<version>.json`; la caché en `cache.json` (no se sube).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-PP1. **La pregunta se le da al puente con una escala genérica de 5 puntos**, de «nada o
    totalmente en desacuerdo» a «mucho o totalmente de acuerdo», con el texto de la página
    (`pregunta_pagina`). Arriba es «de acuerdo» en el sentido de la clasificación (DI-BA3),
    que es lo que mide el resultado real. El nivel que propone el modelo no se usa.

DI-PP2. **Como en la página** (DI-CO12): si la versión responde «sin base» o algo roto, se
    pide el puente con el prompt de siempre. Si tampoco hay puente, esa llamada no acierta
    ningún par (concordancia 0).

DI-PP3. **Grupos de los agentes con los cortes de cada fuente**: edad en los tramos de la
    población (18-25 … 56+) o los de la encuesta del CNC (18-24 … 55+) según la pregunta;
    estrato 1, 2, 3, 4 y 5-6; sexo. El índice de un grupo es el de la página (DI-CO2).

DI-PP4. **El tono general** es la referencia sin API que reemplaza a «estrato, edad y sexo
    solos» (que en una pregunta nueva no se puede ajustar: no hay datos de ella). Por agente:
    el promedio de sus respuestas estandarizadas por año (DI-CO7) en las preguntas del
    catálogo con dirección conocida (DI-PU4), orientadas para que arriba sea lo favorable. Supone
    que los grupos que suelen responder de forma favorable lo harán también aquí.

DI-PP6. **Llamadas en paralelo** (`--paralelo`, 5 por defecto; 1/10, a pedido de Daniel: la
    primera corrida, una por una, tardaba más de una hora). Cambia solo el tiempo: cada llamada
    es la misma, con su misma clave de caché, y el orden de las respuestas no cambia.

DI-PP5. **La medida conjunta** es aciertos / pares sobre todas las preguntas (cada par pesa
    igual), mediana de las tres llamadas. Para el azar: la media y el p95 de la medida conjunta
    de 200 repeticiones, juntando el puente al azar k de cada pregunta.
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

from src.experiments import banco as ba                    # noqa: E402
from src.experiments import banco_reales as br             # noqa: E402
from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import puente as pu                   # noqa: E402
from src.experiments import puente_sin_base as sb          # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "practica_puente"
N_AZAR = 200
ESCALA = ["Nada / totalmente en desacuerdo", "Poco / en desacuerdo", "Algo / ni de acuerdo ni en desacuerdo",
          "Bastante / de acuerdo", "Mucho / totalmente de acuerdo"]

AFECTADOS = (
    "Antes de elegir, piensa en QUIÉN tendería a responder de forma favorable a la pregunta nueva y por qué: "
    "a quién afecta o beneficia (según su estrato, su edad, la zona donde vive o los servicios que usa); "
    "quién la propone o a quién se refiere (si es una medida o una institución de un gobierno, la aprobación "
    "de ese gobierno suele ordenar a las personas); y qué valores, experiencias o confianza la sostienen. "
    "Elige las preguntas del catálogo que mejor capturen esas diferencias entre personas, aunque sean de otro "
    "tema. Parecerse en el tema no basta: estar satisfecho con algo no predice estar de acuerdo con una "
    "medida sobre eso.\n"
)
SISTEMA_AFECTADOS = sb.SISTEMA_V2.replace("Califica la FUERZA del puente", AFECTADOS + "Califica la FUERZA del puente", 1)
VERSIONES = {"actual": sb.SISTEMA_V2, "afectados": SISTEMA_AFECTADOS}


class PracticaError(RuntimeError):
    """Algo impide correr la práctica como está descrita."""


# --------------------------------------------------------------------------
# Preguntas y grupos

def preguntas(reales: Optional[dict] = None) -> list[dict]:
    """Las de práctica sin exclusión de estructura (DI-BR5) y con al menos un par claro."""
    reales = reales if reales is not None else json.loads(br.SALIDA.read_text(encoding="utf-8"))
    p = ba.practica()
    out = []
    for f in p.to_dict("records"):
        r = reales.get(f["id"])
        if r is None or r.get("excluida") or not r["pares_claros"]:
            continue
        out.append({**f, "real": r})
    return out


def ficha(pregunta: str) -> dict:
    """DI-PP1."""
    return {"variable": "NUEVA", "codigo": "NUEVA", "pregunta": pregunta, "escala": [1, 2, 3, 4, 5],
            "etiquetas": {str(i + 1): e for i, e in enumerate(ESCALA)}}


def grupos_agentes(agentes: pd.DataFrame, cortes_cnc: bool) -> dict[str, np.ndarray]:
    """DI-PP3."""
    if cortes_cnc:
        from src.experiments import preguntas_reales as pr
        g = pr.grupos(agentes)
        return {"sexo": g["sexo"], "edad": g["edad"], "estrato": g["estrato"]}
    return {"sexo": agentes.sexo.map({"M": "Hombres", "F": "Mujeres"}).to_numpy(),
            "edad": br.edad_grupo(agentes.edad.astype(float), en_tramos=False).to_numpy(),
            "estrato": agentes.estrato.map(br.estrato_grupo).to_numpy()}


def indices(puntaje: np.ndarray, peso: np.ndarray, grupos: dict[str, np.ndarray], etiquetas: dict) -> dict:
    m = np.sum(puntaje * peso) / np.sum(peso)
    sd = float(np.sqrt(np.sum(peso * (puntaje - m) ** 2) / np.sum(peso))) or 1.0
    z = (puntaje - m) / sd
    out = {}
    for dim, labs in etiquetas.items():
        e = grupos[dim]
        out[dim] = {g: float(np.sum(z[e == g] * peso[e == g]) / np.sum(peso[e == g])) for g in labs if (e == g).any()}
    return out


def aciertos(ix: dict, pares: list) -> int:
    return int(sum(ix.get(d, {}).get(hi, np.nan) > ix.get(d, {}).get(lo, np.nan) for d, hi, lo in pares))


def r_localidad(puntaje: np.ndarray, peso: np.ndarray, loc: np.ndarray, real_loc: dict) -> Optional[float]:
    cs = [int(c) for c in real_loc if (loc == int(c)).any()]
    if len(cs) < 5:
        return None
    a = [np.sum(puntaje[loc == c] * peso[loc == c]) / np.sum(peso[loc == c]) for c in cs]
    return float(np.corrcoef(a, [real_loc[str(c)] for c in cs])[0, 1])


def tono_general(motor) -> np.ndarray:
    """DI-PP4: por agente."""
    z = motor.datos_puente.z
    cols = [d * z[v] for v, f in motor.catalogo.items() for d in [pu.direccion(f)] if d is not None]
    return np.mean(cols, axis=0)[motor.idx]


# --------------------------------------------------------------------------
# El puente (DI-PP2)

def pedir(llamar, cache, modelo, sistema, f_esc, catalogo, rep) -> tuple[Optional[dict], bool]:
    u = pu.prompt(f_esc, catalogo)
    r = sb.parsear_v2(e9.pedir(llamar, cache, modelo, pu.TEMPERATURA, sistema, u, rep)[0], f_esc, catalogo)
    if r is not None and not r["sin_base"]:
        return r, False
    r = pu.parsear(e9.pedir(llamar, cache, modelo, pu.TEMPERATURA, pu.SISTEMA, u, rep)[0], f_esc, catalogo)
    return ({**r, "fuerza": "debil", "sin_base": False} if r else None), True


def recolectar(qs: list[dict], llamar, cache, modelo: str, sistema: str, catalogo: dict,
               paralelo: int = 1) -> tuple[dict, dict]:
    """DI-PP6: las mismas llamadas, varias a la vez; el resultado no depende del orden."""
    from concurrent.futures import ThreadPoolExecutor
    tareas = [(q["id"], q["pregunta_pagina"], rep) for q in qs for rep in range(pu.REPETICIONES)]

    def una(t):
        return pedir(llamar, cache, modelo, sistema, ficha(t[1]), catalogo, t[2])
    with ThreadPoolExecutor(max_workers=max(1, paralelo)) as ex:
        res = []
        for i, r in enumerate(ex.map(una, tareas), 1):
            res.append(r)
            if i % 30 == 0:
                print(f"  {i} de {len(tareas)} llamadas", flush=True)
    respuestas, reintentos = {}, {}
    for (qid, _, rep), (r, x) in zip(tareas, res):
        respuestas.setdefault(qid, []).append(r)
        reintentos[qid] = reintentos.get(qid, 0) + int(x)
    return respuestas, reintentos


# --------------------------------------------------------------------------
# Análisis

def analizar(motor, qs: list[dict], respuestas: dict[str, list], n_azar: int = N_AZAR, semilla: int = pu.SEMILLA) -> dict:
    rng = np.random.default_rng(semilla)
    cods = list(motor.catalogo)
    peso, loc = motor.peso, motor.loc
    tono = tono_general(motor)
    G = {c: grupos_agentes(motor.agentes, c) for c in (False, True)}
    por = {}
    for q in qs:
        real = q["real"]
        pares = [tuple(p) for p in real["pares_claros"]]
        cnc = q["fuente"] == "Biblioteca CNC"
        g = G[cnc]
        labs = {d: list(real["grupos"][d]) for d in ("sexo", "edad", "estrato") if d in real["grupos"]}
        ac, rl = [], []
        for r in respuestas[q["id"]]:
            if r is None:
                ac.append(0); rl.append(None)
                continue
            s = motor.datos_puente.puntaje(r["preguntas"])[motor.idx]
            ac.append(aciertos(indices(s, peso, g, labs), pares))
            rl.append(r_localidad(s, peso, loc, real["localidad"]) if "localidad" in real else None)
        az = []
        for _ in range(n_azar):
            k = int(rng.integers(1, pu.MAX_PREGUNTAS + 1))
            p = [{"codigo": str(c), "sentido": str(rng.choice(["+", "-"])), "peso": int(rng.integers(1, 4))}
                 for c in rng.choice(cods, k, replace=False)]
            az.append(aciertos(indices(motor.datos_puente.puntaje(p)[motor.idx], peso, g, labs), pares))
        por[q["id"]] = {"ambito": q["ambito"], "fuente": q["fuente"], "pregunta": q["pregunta_pagina"],
                        "pares": len(pares), "aciertos": ac, "azar": az,
                        "tono": aciertos(indices(tono, peso, g, labs), pares),
                        "r_localidad": rl,
                        "puentes": [[(x["codigo"], x["sentido"], x["peso"]) for x in r["preguntas"]] if r else None
                                    for r in respuestas[q["id"]]],
                        "fuerzas": [r["fuerza"] if r else None for r in respuestas[q["id"]]]}
    return {"por_pregunta": por, "resumen": resumen(por)}


def resumen(por: dict) -> dict:
    """DI-PP5."""
    out = {}
    for nombre, filtro in (("todas", lambda a: True), ("Bogotá", lambda a: a == "Bogotá"), ("general", lambda a: a == "general")):
        P = [p for p in por.values() if filtro(p["ambito"])]
        if not P:
            continue
        n = sum(p["pares"] for p in P)
        llamadas = [sum(p["aciertos"][k] for p in P) / n for k in range(len(P[0]["aciertos"]))]
        azar = [sum(p["azar"][k] for p in P) / n for k in range(len(P[0]["azar"]))]
        rl = [np.median([x for x in p["r_localidad"] if x is not None]) for p in P if any(x is not None for x in p["r_localidad"])]
        out[nombre] = {"preguntas": len(P), "pares": n, "puente": float(np.median(llamadas)),
                       "azar_media": float(np.mean(azar)), "azar_p95": float(np.percentile(azar, 95)),
                       "tono_general": sum(p["tono"] for p in P) / n,
                       "r_localidad_mediana": float(np.median(rl)) if rl else None, "n_localidad": len(rl)}
    return out


# --------------------------------------------------------------------------

def modelo_simulado(catalogo: dict):
    cods = list(catalogo)

    def llamar(modelo, sistema, usuario, temp):
        h = sum(map(ord, usuario)) % (len(cods) - 1)
        return json.dumps({"preguntas": [{"codigo": cods[h], "sentido": "+", "peso": 2},
                                         {"codigo": cods[h + 1], "sentido": "-", "peso": 1}],
                           "fuerza": "media", "sin_base": False, "nivel": 3.0, "justificacion": "simulado"})
    return llamar


def main(argv=None, entrada=input) -> int:
    ap = argparse.ArgumentParser(description="Práctica del puente sobre el banco.")
    ap.add_argument("--version", choices=sorted(VERSIONES), required=True)
    ap.add_argument("--simulado", action="store_true", help="modelo simulado, sin gasto")
    ap.add_argument("--paralelo", type=int, default=5, help="llamadas a la vez (DI-PP6)")
    args = ap.parse_args(argv)
    from src.consulta import motor as mo
    from src.consulta import reformular as rf
    catalogo = rf.cargar_catalogo()
    sistema = VERSIONES[args.version]
    qs = preguntas()
    salida = SALIDA / ("simulado" if args.simulado else "")
    cache = e9.Cache(salida / "cache.json")
    if args.simulado:
        llamar, modelo = modelo_simulado(catalogo), e9.MODELO_SIMULADO
    else:
        llamar, modelo = e9.cliente_real(), pu.MODELO
        pend = [(sistema, pu.prompt(ficha(q["pregunta_pagina"]), catalogo), 400) for q in qs for rep in range(pu.REPETICIONES)
                if e9.Cache.clave(modelo, pu.TEMPERATURA, sistema, pu.prompt(ficha(q["pregunta_pagina"]), catalogo), rep) not in cache]
        if not e9.confirmar_gasto(pend, entrada, e9.gasto_registrado(cache)):
            print("No se gastó nada.")
            return 1
    try:
        respuestas, reintentos = recolectar(qs, llamar, cache, modelo, sistema, catalogo, args.paralelo)
    except e9.Experimento9Error as e:
        print(f"\nERROR: {e}\nLo que respondió quedó en la caché; al volver a correr solo se hace lo que falta.")
        return 1
    M = mo.Motor(llamar, modelo, cache=cache)
    a = analizar(M, qs, respuestas)
    for k, v in reintentos.items():
        a["por_pregunta"][k]["reintentos"] = v
    salida.mkdir(parents=True, exist_ok=True)
    (salida / f"{args.version}.json").write_text(json.dumps({**a, "version": args.version, "sistema": sistema, "modelo": modelo,
                                                             "gasto": e9.gasto_registrado(cache)},
                                                            ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print(f"\nVersión «{args.version}»: fracción de diferencias claras entre grupos bien ordenadas")
    print(f"{'':10s} {'preguntas':>9s} {'pares':>6s} {'puente':>7s} {'azar':>6s} {'azar95':>7s} {'tono':>6s} {'r_loc':>6s}")
    for k, r in a["resumen"].items():
        rl = f"{r['r_localidad_mediana']:.2f}" if r["r_localidad_mediana"] is not None else "—"
        print(f"{k:10s} {r['preguntas']:9d} {r['pares']:6d} {r['puente']:7.2f} {r['azar_media']:6.2f} {r['azar_p95']:7.2f} "
              f"{r['tono_general']:6.2f} {rl:>6s}")
    print(f"reintentos con el prompt de siempre: {sum(reintentos.values())} de {3 * len(qs)} llamadas")
    print(f"gasto acumulado de la caché: {e9.gasto_registrado(cache)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
