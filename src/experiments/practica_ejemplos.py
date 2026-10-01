"""
Práctica del puente, último intento (`BANCO_PREGUNTAS_NUEVAS.md` §10.2): el modelo ve el
perfil por grupo de cada pregunta del catálogo y ejemplos resueltos de la práctica, con
validación cruzada por familia. Regla de salida escrita antes de correr: ≥ 0,67 de las 699
diferencias claras, o se para.

Uso:
    python src/experiments/practica_ejemplos.py --simulado
    python src/experiments/practica_ejemplos.py                # llamadas reales (pide confirmación)

Escribe `data/processed/practica_puente/ejemplos.json`; usa la misma caché que la práctica.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-PE1. **Perfil de una pregunta del catálogo**, con los agentes de la población y sus respuestas
    estandarizadas por año (DI-CO7): diferencia de medias entre estratos 5-6 y 1-2, entre 56+ y
    18-25, y entre mujeres y hombres, en desviaciones estándar. Se dice en palabras: «más alto en
    estratos altos / bajos» si pasa de 0,15; «más alto en mayores / jóvenes» si pasa de 0,15;
    «mujeres más alto / hombres más alto» si pasa de 0,10; si no, «parejo».

DI-PE2. **Perfil real de un ejemplo**, con sus porcentajes «de acuerdo»: estrato 5-6 frente a 1
    y 2 (promedio), los mayores frente a los más jóvenes, mujeres frente a hombres; umbrales de
    5, 5 y 3 puntos.

DI-PE3. ~~**El puente de un ejemplo** son las 2 preguntas del catálogo que más pares claros del
    ejemplo ordenan bien.~~ *Corrección (1/10, antes de la corrida real):* era ruido (para la
    confianza en el Congreso salió «respeto por los reinsertados +, respeto por la diversidad
    sexual −»): con pocos pares alguna pareja siempre acierta por azar, y enseñaría relaciones
    falsas. Los ejemplos llevan la pregunta y su perfil real, nada más. `puente_ejemplo` se
    conserva para que quede a la vista lo que se descartó.

DI-PE4. **Partes:** las familias de la práctica se reparten en 3 con semilla fija; cada pregunta
    recibe 8 ejemplos de las otras dos partes (sorteados con semilla, mitad de Bogotá si hay).
    El mensaje lleva el catálogo con perfiles y los ejemplos; las instrucciones son las del
    prompt v2 más un párrafo (`PARRAFO`).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import practica_puente as pp          # noqa: E402
from src.experiments import puente as pu                   # noqa: E402
from src.experiments import puente_sin_base as sb          # noqa: E402

SEMILLA = 20261001
K_PARTES = 3
N_EJEMPLOS = 8
SALIDA = pp.SALIDA / "ejemplos.json"
UMBRAL = 0.67

PARRAFO = (
    "Cada pregunta del catálogo trae su PERFIL: en qué estratos, edades y sexo se responde más alto en "
    "esta población. Al final hay EJEMPLOS RESUELTOS de otras preguntas nuevas, con su perfil REAL (en qué "
    "grupos se respondió de forma más favorable). Úsalos para "
    "aprender qué perfil suelen tener preguntas parecidas a la nueva, y elige preguntas del catálogo cuyo "
    "perfil se parezca al que esperas para la pregunta nueva. El tema importa menos que el perfil.\n"
)
SISTEMA = sb.SISTEMA_V2.replace("Califica la FUERZA del puente", PARRAFO + "Califica la FUERZA del puente", 1)


# --------------------------------------------------------------------------
# Perfiles (DI-PE1, DI-PE2)

def _palabras(d_est, d_edad, d_sexo, u_est, u_edad, u_sexo) -> str:
    est = "más alto en estratos altos" if d_est > u_est else ("más alto en estratos bajos" if d_est < -u_est else "parejo por estrato")
    edad = "más alto en mayores" if d_edad > u_edad else ("más alto en jóvenes" if d_edad < -u_edad else "parejo por edad")
    sexo = "mujeres más alto" if d_sexo > u_sexo else ("hombres más alto" if d_sexo < -u_sexo else "parejo por sexo")
    return f"{est}; {edad}; {sexo}"


def perfiles_catalogo(motor) -> dict[str, str]:
    g = pp.grupos_agentes(motor.agentes, False)
    w = motor.peso
    est = np.where(np.isin(g["estrato"], ["1", "2"]), "bajo", np.where(g["estrato"] == "5-6", "alto", ""))

    def media(z, m):
        return float(np.sum(z[m] * w[m]) / np.sum(w[m]))
    out = {}
    for v in motor.catalogo:
        z = motor.datos_puente.z[v][motor.idx]
        out[v] = _palabras(media(z, est == "alto") - media(z, est == "bajo"),
                           media(z, g["edad"] == "56+") - media(z, g["edad"] == "18-25"),
                           media(z, g["sexo"] == "Mujeres") - media(z, g["sexo"] == "Hombres"), 0.15, 0.15, 0.10)
    return out


def perfil_real(real: dict) -> str:
    gr = real["grupos"]
    e = gr.get("estrato", {})
    bajo = [e[k] for k in ("1", "2") if k in e]
    d_est = (e["5-6"] - np.mean(bajo)) if "5-6" in e and bajo else 0.0
    ed = list(gr.get("edad", {}).values())
    d_edad = (ed[-1] - ed[0]) if len(ed) >= 2 else 0.0
    s = gr.get("sexo", {})
    d_sexo = s.get("Mujeres", 0) - s.get("Hombres", 0) if len(s) == 2 else 0.0
    return _palabras(d_est, d_edad, d_sexo, 5, 5, 3)


def puente_ejemplo(motor, q: dict, grupos: dict) -> list[dict]:
    """DI-PE3."""
    real = q["real"]
    pares = [tuple(p) for p in real["pares_claros"]]
    labs = {d: list(real["grupos"][d]) for d in ("sexo", "edad", "estrato") if d in real["grupos"]}
    cand = []
    for i, v in enumerate(motor.catalogo):
        z = motor.datos_puente.z[v][motor.idx]
        for s in (1, -1):
            cand.append((pp.aciertos(pp.indices(s * z, motor.peso, grupos, labs), pares), -i, v, "+" if s > 0 else "-"))
    cand.sort(reverse=True)
    elegidos, vistos = [], set()
    for _, _, v, s in cand:
        if v not in vistos:
            elegidos.append({"codigo": v, "sentido": s, "peso": 2})
            vistos.add(v)
        if len(elegidos) == 2:
            break
    return elegidos


# --------------------------------------------------------------------------
# Partes y mensajes (DI-PE4)

def partes(qs: list[dict], k: int = K_PARTES, semilla: int = SEMILLA) -> dict[str, int]:
    fams = sorted({q["familia"] for q in qs})
    orden = list(np.random.default_rng(semilla).permutation(fams))
    a = {f: i % k for i, f in enumerate(orden)}
    return {q["id"]: a[q["familia"]] for q in qs}


def elegir_ejemplos(q: dict, qs: list[dict], parte: dict, n: int = N_EJEMPLOS, semilla: int = SEMILLA) -> list[dict]:
    otras = [x for x in qs if parte[x["id"]] != parte[q["id"]]]
    rng = np.random.default_rng(semilla + parte[q["id"]])
    bog = [x for x in otras if x["ambito"] == "Bogotá"]
    gen = [x for x in otras if x["ambito"] != "Bogotá"]
    nb = min(len(bog), n // 2)
    sel = list(rng.choice(len(bog), nb, replace=False)) if nb else []
    sg = list(rng.choice(len(gen), min(len(gen), n - nb), replace=False)) if gen else []
    return [bog[i] for i in sel] + [gen[i] for i in sg]


def catalogo_con_perfiles(catalogo: dict, perfiles: dict) -> dict:
    out = {}
    for v, f in catalogo.items():
        out[v] = {**f, "pregunta": f"{f['pregunta'].strip()} [PERFIL: {perfiles[v]}]"}
    return out


def mensaje(q: dict, catalogo_p: dict, ejemplos: list[dict], perfiles_ej: dict) -> str:
    base = pu.prompt(pp.ficha(q["pregunta_pagina"]), catalogo_p)
    lineas = ["\n\nEJEMPLOS RESUELTOS:"]
    for x in ejemplos:
        lineas.append(f"- «{x['pregunta_pagina']}» → perfil real: {perfiles_ej[x['id']]}.")
    return base + "\n".join(lineas)


# --------------------------------------------------------------------------

def main(argv=None, entrada=input) -> int:
    ap = argparse.ArgumentParser(description="Práctica: perfiles y ejemplos resueltos (§10.2).")
    ap.add_argument("--simulado", action="store_true")
    ap.add_argument("--paralelo", type=int, default=5)
    args = ap.parse_args(argv)
    from src.consulta import motor as mo
    from src.consulta import reformular as rf
    catalogo = rf.cargar_catalogo()
    qs = pp.preguntas()
    salida = pp.SALIDA / ("simulado" if args.simulado else "")
    cache = e9.Cache(salida / "cache.json")
    if args.simulado:
        llamar, modelo = pp.modelo_simulado(catalogo), e9.MODELO_SIMULADO
    else:
        llamar, modelo = e9.cliente_real(), pu.MODELO
    M = mo.Motor(llamar, modelo, cache=cache)
    perf = perfiles_catalogo(M)
    cat_p = catalogo_con_perfiles(catalogo, perf)
    g = {c: pp.grupos_agentes(M.agentes, c) for c in (False, True)}
    parte = partes(qs)
    perf_ej = {q["id"]: perfil_real(q["real"]) for q in qs}
    mensajes = {q["id"]: mensaje(q, cat_p, elegir_ejemplos(q, qs, parte), perf_ej) for q in qs}
    if not args.simulado:
        pend = [(SISTEMA, mensajes[q["id"]], 400) for q in qs for rep in range(pu.REPETICIONES)
                if e9.Cache.clave(modelo, pu.TEMPERATURA, SISTEMA, mensajes[q["id"]], rep) not in cache]
        if not e9.confirmar_gasto(pend, entrada, e9.gasto_registrado(cache)):
            print("No se gastó nada.")
            return 1
    from concurrent.futures import ThreadPoolExecutor
    tareas = [(q, rep) for q in qs for rep in range(pu.REPETICIONES)]

    def una(t):
        q, rep = t
        f = pp.ficha(q["pregunta_pagina"])
        r = sb.parsear_v2(e9.pedir(llamar, cache, modelo, pu.TEMPERATURA, SISTEMA, mensajes[q["id"]], rep)[0], f, catalogo)
        if r is not None and not r["sin_base"]:
            return r, False
        r = pu.parsear(e9.pedir(llamar, cache, modelo, pu.TEMPERATURA, pu.SISTEMA, pu.prompt(f, catalogo), rep)[0], f, catalogo)
        return ({**r, "fuerza": "debil", "sin_base": False} if r else None), True
    try:
        with ThreadPoolExecutor(max_workers=max(1, args.paralelo)) as ex:
            res = list(ex.map(una, tareas))
    except e9.Experimento9Error as e:
        print(f"\nERROR: {e}\nLo que respondió quedó en la caché; al volver a correr solo se hace lo que falta.")
        return 1
    respuestas, reint = {}, 0
    for (q, _), (r, x) in zip(tareas, res):
        respuestas.setdefault(q["id"], []).append(r)
        reint += int(x)
    a = pp.analizar(M, qs, respuestas)
    salida.mkdir(parents=True, exist_ok=True)
    destino = salida / "ejemplos.json"
    destino.write_text(json.dumps({**a, "version": "ejemplos", "sistema": SISTEMA, "partes": parte, "perfiles_catalogo": perf,
                                   "modelo": modelo, "gasto": e9.gasto_registrado(cache)},
                                  ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print("\nVersión «ejemplos» (validación cruzada): fracción de diferencias claras bien ordenadas")
    print(f"{'':10s} {'preguntas':>9s} {'pares':>6s} {'puente':>7s} {'azar':>6s} {'azar95':>7s} {'tono':>6s} {'r_loc':>6s}")
    for k, r in a["resumen"].items():
        rl = f"{r['r_localidad_mediana']:.2f}" if r["r_localidad_mediana"] is not None else "—"
        print(f"{k:10s} {r['preguntas']:9d} {r['pares']:6d} {r['puente']:7.2f} {r['azar_media']:6.2f} {r['azar_p95']:7.2f} "
              f"{r['tono_general']:6.2f} {rl:>6s}")
    t = a["resumen"]["todas"]["puente"]
    print(f"reintentos: {reint} de {len(tareas)}")
    print(f"\nRegla de salida (§10.2): {t:.3f} {'≥' if t >= UMBRAL else '<'} {UMBRAL} → "
          f"{'SIGUE al banco guardado, pre-registrado' if t >= UMBRAL else 'SE PARA: la página adopta el tono general'}")
    print(f"gasto acumulado de la caché: {e9.gasto_registrado(cache)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
