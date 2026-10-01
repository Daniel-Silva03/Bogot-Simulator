"""
Preguntas reales nuevas: en el metro elevado y el Corredor Verde, que la EPC nunca
preguntó, ¿el puente acierta qué grupos estarían más de acuerdo?

Pre-registro: `docs/PREGUNTAS_REALES_NUEVAS_SPECIFICATION.md`. Este módulo lo ejecuta y no
decide nada que el documento no haya decidido. Las cifras reales son las publicadas por el
CNC (encuesta para Red+ y Caracol Radio, 15/08/2023; `DATA_INVENTORY.md` §15), copiadas aquí
y comprobadas contra el pre-registro por una prueba.

Uso:
    python src/experiments/preguntas_reales.py --simulado    # sin gasto, para probar
    python src/experiments/preguntas_reales.py               # 6 llamadas reales (pide confirmación)

Escribe `data/processed/preguntas_reales/resultado.json`; la caché en `cache.json` (no se sube).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-PR1. **El puente se pide como en la página** (DI-CO12): prompt v2; si dice «sin base» o
    la respuesta está rota, el prompt de siempre, y la fuerza queda «débil». Si tampoco
    así hay puente, esa llamada cuenta como concordancia 0 (lo conservador, como DI-PU3).

DI-PR2. **El índice de un grupo es el de la página** (DI-CO2): puntaje del puente de cada
    agente (cada pregunta estandarizada por año, DI-CO7), estandarizado con los pesos de
    todos los agentes con donante, y promediado con los pesos del grupo.

DI-PR3. **Grupos con los datos del propio agente**, en los cortes de la encuesta real:
    edad 18-24, 25-34, 35-54, 55+ (con su edad, no con los tramos de la página); estrato
    1, 2, 3, 4 y 5-6; estrato 0 no entra (§5).

DI-PR4. **El azar pareado:** cada uno de los 200 puentes al azar se arma para una pregunta;
    la concordancia conjunta de la repetición k junta el puente k del metro y el puente k
    del Corredor, ponderados por sus pares (11 y 13), igual que la del puente real.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import puente as pu                   # noqa: E402
from src.experiments import puente_sin_base as sb          # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "preguntas_reales"
ESPECIFICACION = RAIZ / "docs" / "PREGUNTAS_REALES_NUEVAS_SPECIFICATION.md"
N_AZAR = 200
UMBRAL_P1 = 0.70
Z_CLARO = 1.96

PREGUNTAS = {
    "metro": "mantener el metro elevado para Bogotá?",
    "corredor": "el Corredor Verde por la carrera séptima?",
}

#: §4: bases sin ponderar de cada grupo.
BASES = {"sexo": {"Hombres": 2465, "Mujeres": 1810},
         "edad": {"18-24": 406, "25-34": 872, "35-54": 1955, "55+": 1042},
         "estrato": {"1": 435, "2": 1571, "3": 1765, "4": 381, "5-6": 123}}

#: §4: porcentaje que respondió «sí». Estrato 5-6 = 5 y 6 ponderados por sus bases (97 y 26).
REAL = {
    "metro": {"total": 65.7,
              "sexo": {"Hombres": 61.5, "Mujeres": 69.4},
              "edad": {"18-24": 61.5, "25-34": 56.8, "35-54": 69.8, "55+": 70.9},
              "estrato": {"1": 69.7, "2": 64.2, "3": 63.0, "4": 69.4, "5-6": round((75.0 * 97 + 73.1 * 26) / 123, 1)}},
    "corredor": {"total": 58.8,
                 "sexo": {"Hombres": 53.7, "Mujeres": 63.3},
                 "edad": {"18-24": 67.7, "25-34": 63.7, "35-54": 59.0, "55+": 49.2},
                 "estrato": {"1": 69.0, "2": 65.2, "3": 57.1, "4": 45.9, "5-6": round((50.9 * 97 + 53.8 * 26) / 123, 1)}},
}

#: §4: por localidad, con su código DANE. «Otra» (seis localidades juntas) no entra.
LOCALIDADES = {3: "Santa Fe", 5: "Usme", 6: "Tunjuelito", 7: "Bosa", 8: "Kennedy", 9: "Fontibón",
               10: "Engativá", 11: "Suba", 12: "Barrios Unidos", 14: "Los Mártires", 16: "Puente Aranda",
               18: "Rafael Uribe Uribe", 19: "Ciudad Bolívar"}
REAL_LOC = {
    "metro": {3: 61.6, 5: 53.0, 6: 68.6, 7: 71.0, 8: 50.9, 9: 72.9, 10: 53.6, 11: 76.2, 12: 70.9, 14: 55.1,
              16: 64.9, 18: 71.6, 19: 74.1},
    "corredor": {3: 65.2, 5: 59.9, 6: 66.1, 7: 63.8, 8: 61.4, 9: 55.3, 10: 63.3, 11: 58.0, 12: 59.2, 14: 62.9,
                 16: 45.8, 18: 58.2, 19: 66.0},
}


class PreguntasRealesError(RuntimeError):
    """Algo impide correr la prueba como está pre-registrada."""


# --------------------------------------------------------------------------
# Pares claros y concordancia

def pares_claros(real: dict, bases: dict = BASES) -> list[tuple[str, str, str]]:
    """§4: (dimensión, grupo mayor, grupo menor) de las diferencias con z > 1,96."""
    out = []
    for dim in ("sexo", "edad", "estrato"):
        g = real[dim]
        for a, b in itertools.combinations(g, 2):
            pa, pb = g[a] / 100, g[b] / 100
            se = math.sqrt(pa * (1 - pa) / bases[dim][a] + pb * (1 - pb) / bases[dim][b])
            if abs(pa - pb) / se > Z_CLARO:
                out.append((dim, a, b) if pa > pb else (dim, b, a))
    return out


def concordancia(indices: dict[str, dict[str, float]], pares: list[tuple[str, str, str]]) -> float:
    """§5: fracción de pares claros en los que el índice del grupo mayor es mayor (empate = fallo)."""
    if not pares:
        return float("nan")
    return float(np.mean([indices[d][hi] > indices[d][lo] for d, hi, lo in pares]))


# --------------------------------------------------------------------------
# Grupos e índices (DI-PR2, DI-PR3)

def grupos(agentes: pd.DataFrame) -> dict[str, np.ndarray]:
    edad = pd.cut(agentes.edad.astype(float), [18, 25, 35, 55, 200], right=False,
                  labels=["18-24", "25-34", "35-54", "55+"]).astype(object).to_numpy()
    est = agentes.estrato.map(lambda e: None if pd.isna(e) or e < 1 else ("5-6" if e >= 5 else str(int(e)))).to_numpy()
    sexo = agentes.sexo.map({"M": "Hombres", "F": "Mujeres"}).to_numpy()
    return {"sexo": sexo, "edad": edad, "estrato": est}


def indices(puntaje: np.ndarray, peso: np.ndarray, etq: dict[str, np.ndarray]) -> dict[str, dict[str, float]]:
    m = np.sum(puntaje * peso) / np.sum(peso)
    sd = math.sqrt(np.sum(peso * (puntaje - m) ** 2) / np.sum(peso)) or 1.0
    z = (puntaje - m) / sd
    out = {}
    for dim, e in etq.items():
        out[dim] = {g: float(np.sum(z[e == g] * peso[e == g]) / np.sum(peso[e == g]))
                    for g in BASES[dim] if (e == g).any()}
    return out


def indice_localidad(puntaje: np.ndarray, peso: np.ndarray, loc: np.ndarray) -> dict[int, float]:
    return {c: float(np.sum(puntaje[loc == c] * peso[loc == c]) / np.sum(peso[loc == c])) for c in LOCALIDADES}


def r_localidades(idx_loc: dict[int, float], real_loc: dict[int, float]) -> float:
    cs = sorted(real_loc)
    return float(np.corrcoef([idx_loc[c] for c in cs], [real_loc[c] for c in cs])[0, 1])


# --------------------------------------------------------------------------
# El puente (DI-PR1)

def pedir_puente(llamar, cache: e9.Cache, modelo: str, f_esc: dict, catalogo: dict, rep: int) -> tuple[Optional[dict], bool]:
    u = pu.prompt(f_esc, catalogo)
    r = sb.parsear_v2(e9.pedir(llamar, cache, modelo, pu.TEMPERATURA, sb.SISTEMA_V2, u, rep)[0], f_esc, catalogo)
    if r is not None and not r["sin_base"]:
        return r, False
    r = pu.parsear(e9.pedir(llamar, cache, modelo, pu.TEMPERATURA, pu.SISTEMA, u, rep)[0], f_esc, catalogo)
    return ({**r, "fuerza": "debil", "sin_base": False} if r else None), True


def azar(datos_puente, idx: np.ndarray, peso: np.ndarray, etq: dict, pares: list, catalogo: dict,
         n: int = N_AZAR, semilla: int = pu.SEMILLA) -> list[float]:
    rng = np.random.default_rng(semilla)
    cods = list(catalogo)
    out = []
    for _ in range(n):
        k = int(rng.integers(1, pu.MAX_PREGUNTAS + 1))
        p = [{"codigo": str(c), "sentido": str(rng.choice(["+", "-"])), "peso": int(rng.integers(1, 4))}
             for c in rng.choice(cods, k, replace=False)]
        out.append(concordancia(indices(datos_puente.puntaje(p)[idx], peso, etq), pares))
    return out


# --------------------------------------------------------------------------
# Regla

def evaluar(por: dict) -> dict:
    """§6 y §7. `por[q]`: concordancias por llamada, n de pares, azar, niveles y r de localidades."""
    m, c = por["metro"], por["corredor"]
    n_m, n_c = m["n_pares"], c["n_pares"]
    conj = [(a * n_m + b * n_c) / (n_m + n_c) for a, b in zip(m["concordancias"], c["concordancias"])]
    azar_conj = [(a * n_m + b * n_c) / (n_m + n_c) for a, b in zip(m["azar"], c["azar"])]
    p95 = float(np.percentile(azar_conj, 95))
    med = float(np.median(conj))
    med_m, med_c = float(np.median(m["concordancias"])), float(np.median(c["concordancias"]))
    niv_m, niv_c = m["nivel"], c["nivel"]
    p = {
        "P1": {"umbral": f"concordancia en los {n_m + n_c} pares ≥ {UMBRAL_P1} y > p95 del azar",
               "concordancia": med, "aciertos": round(med * (n_m + n_c), 1), "azar_p95": p95,
               "se_cumple": bool(med >= UMBRAL_P1 and med > p95)},
        "P2": {"umbral": "≥ 0,60 en cada pregunta (se reporta)", "metro": med_m, "corredor": med_c,
               "se_cumple": bool(med_m >= 0.6 and med_c >= 0.6)},
        "P3": {"umbral": "nivel > 3 en las dos y mayor en el metro (se reporta)", "metro": niv_m, "corredor": niv_c,
               "se_cumple": bool(niv_m is not None and niv_c is not None and niv_m > 3 and niv_c > 3 and niv_m > niv_c)},
        "P4": {"umbral": "Pearson por localidad, 13 localidades (se reporta)", "metro": m["r_loc"], "corredor": c["r_loc"],
               "ambas_mayores_a_0_5": bool(m["r_loc"] >= 0.5 and c["r_loc"] >= 0.5)},
    }
    if p["P1"]["se_cumple"]:
        regla = (f"La página puede decir que en dos preguntas reales que la encuesta no hizo, el puente acertó el "
                 f"orden de los grupos en {p['P1']['aciertos']:g} de {n_m + n_c} diferencias claras.")
    else:
        regla = ("En las preguntas nuevas, la página deja de mostrar las barras por grupo de entrada: solo si la "
                 "persona lo pide, con el aviso de que en una prueba con preguntas reales el orden no se sostuvo.")
    return {"predicciones": p, "concordancia_conjunta_por_llamada": conj, "regla": regla}


# --------------------------------------------------------------------------
# Corrida

def modelo_simulado(catalogo: dict):
    cods = list(catalogo)

    def llamar(modelo, sistema, usuario, temp):
        return json.dumps({"preguntas": [{"codigo": cods[0], "sentido": "+", "peso": 2},
                                         {"codigo": cods[5], "sentido": "-", "peso": 1}],
                           "fuerza": "media", "sin_base": False, "nivel": 3.4, "justificacion": "simulado"})
    return llamar


def main(argv=None, entrada=input) -> int:
    ap = argparse.ArgumentParser(description="Preguntas reales nuevas (docs/PREGUNTAS_REALES_NUEVAS_SPECIFICATION.md).")
    ap.add_argument("--simulado", action="store_true", help="modelo simulado, sin gasto")
    args = ap.parse_args(argv)
    from src.consulta import motor as mo
    from src.consulta import reformular as rf
    catalogo = rf.cargar_catalogo()
    salida = SALIDA / ("simulado" if args.simulado else "")
    cache = e9.Cache(salida / "cache.json")
    if args.simulado:
        llamar, modelo = modelo_simulado(catalogo), e9.MODELO_SIMULADO
    else:
        llamar, modelo = e9.cliente_real(), pu.MODELO
        pend = [(sb.SISTEMA_V2, pu.prompt(sb.ficha_nueva(t), catalogo), 400) for t in PREGUNTAS.values()
                for rep in range(pu.REPETICIONES)
                if e9.Cache.clave(modelo, pu.TEMPERATURA, sb.SISTEMA_V2, pu.prompt(sb.ficha_nueva(t), catalogo), rep) not in cache]
        if not e9.confirmar_gasto(pend, entrada, e9.gasto_registrado(cache)):
            print("No se gastó nada.")
            return 1
    M = mo.Motor(llamar, modelo, cache=cache)                                    # población y puntajes de la página
    peso, loc = M.peso, M.loc
    etq = grupos(M.agentes)
    por = {}
    try:
        for q, t in PREGUNTAS.items():
            f = sb.ficha_nueva(t)
            pares = pares_claros(REAL[q])
            llamadas = [pedir_puente(llamar, cache, modelo, f, catalogo, rep) for rep in range(pu.REPETICIONES)]
            conc, idxs, locs = [], [], []
            for r, _ in llamadas:
                if r is None:                                                    # DI-PR1
                    conc.append(0.0); idxs.append(None); locs.append(None)
                    continue
                s = M.datos_puente.puntaje(r["preguntas"])[M.idx]
                ix = indices(s, peso, etq)
                conc.append(concordancia(ix, pares)); idxs.append(ix)
                locs.append(r_localidades(indice_localidad(s, peso, loc), REAL_LOC[q]))
            niveles = [r["nivel"] for r, _ in llamadas if r]
            por[q] = {"pares": pares, "n_pares": len(pares), "concordancias": conc,
                      "azar": azar(M.datos_puente, M.idx, peso, etq, pares, catalogo),
                      "nivel": float(np.median(niveles)) if niveles else None,
                      "r_loc": float(np.median([x if x is not None else 0.0 for x in locs])),
                      "r_loc_por_llamada": locs, "indices": idxs,
                      "puentes": [r["preguntas"] if r else None for r, _ in llamadas],
                      "fuerzas": [r["fuerza"] if r else None for r, _ in llamadas],
                      "reintentos": [x for _, x in llamadas],
                      "justificaciones": [r["justificacion"] if r else None for r, _ in llamadas]}
    except e9.Experimento9Error as e:
        print(f"\nERROR: {e}\nLo que respondió quedó en la caché; al volver a correr solo se hace lo que falta.")
        return 1
    ev = evaluar(por)
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "resultado.json").write_text(json.dumps({"por_pregunta": por, **ev, "modelo": modelo,
                                                       "gasto": e9.gasto_registrado(cache)},
                                                      ensure_ascii=False, indent=2, default=float), encoding="utf-8")
    for q, x in por.items():
        print(f"\n{q}: puentes {[[p['codigo'] for p in b] if b else None for b in x['puentes']]}; fuerza {x['fuerzas']}; "
              f"reintentos {x['reintentos']}")
        print(f"  concordancia por llamada {[round(c, 2) for c in x['concordancias']]} de {x['n_pares']} pares; "
              f"nivel {x['nivel']}; r_loc {x['r_loc']:.2f}")
        if x["indices"][0]:
            for d, g in x["indices"][0].items():
                print(f"  {d:8s} simulador " + "  ".join(f"{k} {v:+.2f}" for k, v in g.items()))
                print(f"  {'':8s} real      " + "  ".join(f"{k} {REAL[q][d][k]:.1f}" for k in g))
    for k, p in ev["predicciones"].items():
        estado = "se cumple" if p.get("se_cumple") else ("NO se cumple" if "se_cumple" in p else "")
        print(f"  {k} {estado} — {p['umbral']} {({a: b for a, b in p.items() if a not in ('umbral', 'se_cumple')})}")
    print(f"\nRegla: {ev['regla']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
