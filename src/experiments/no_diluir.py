"""
Que los agentes no diluyan la encuesta (`docs/NO_DILUIR_SPECIFICATION.md`): una instrucción y una calibración, probadas en la
primera vuelta de 2026 (desarrollo) y confirmadas en la segunda vuelta en Bogotá.

Uso:
    python src/experiments/no_diluir.py --simulado
    python src/experiments/no_diluir.py

Necesita `BSS_ELECTORAL_DIR` (D16). Las cifras del CNC por grupo se usan dentro del equipo y no se imprimen (D21).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-ND1. **El mensaje** de cada agente es el de `voto_agentes.votar`: «QUIÉN ES» con el perfil y el contexto al final, y la
    pregunta. Así C2 se lee de la caché de `voto_campana` sin volver a llamar.
DI-ND2. **La calibración** (§3) multiplica la probabilidad de cada candidato por la razón entre la encuesta y el total de los
    agentes (los dos normalizados entre los candidatos), y renormaliza cada agente sobre todas sus opciones. Blanco y «no votaría»
    no se tocan. **Corrección del 19/10, antes de subir el pre-registro:** en un solo paso el total no queda en la encuesta
    (al renormalizar cada agente se mueve); por eso el ajuste se repite hasta que el total quede a 0,01 puntos.
DI-ND3. **El modo simulado no lee la caché real.** La primera prueba del código sí la leyó y mostró el error por grupos de C2k en un
    paso; se declara en el pre-registro (§3).
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import voto_agentes as va            # noqa: E402
from src.experiments import voto_campana as vc            # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "no_diluir"
TOPE_USD = 1.0
INSTRUCCION = ("Cuando tengas una encuesta, úsala como punto de partida para personas como esta. No corras su voto hacia los "
               "candidatos que la encuesta muestra con poca intención. Si sus respuestas no dicen claramente otra cosa, inclínate "
               "por los candidatos que la encuesta pone adelante.")
PRIMERA_VUELTA = ("En la primera vuelta del 31 de mayo, en todo el país, De la Espriella sacó 44,1 % y Cepeda 41,3 %; los dos "
                  "pasaron a la segunda vuelta del 21 de junio.")
GUARUMO = ("Según la encuesta nacional de Guarumo y Ecoanalítica para El Tiempo (trabajo de campo del 8 al 11 de junio de 2026, "
           "2.073 adultos en 54 municipios), la intención de voto para la segunda vuelta era: Abelardo de la Espriella 52,6 % e "
           "Iván Cepeda 45,0 %. Es una encuesta nacional, no solo de Bogotá.")
PREGUNTA_2V = ("Si la segunda vuelta presidencial de 2026 fuera hoy, entre Iván Cepeda y Abelardo de la Espriella, ¿por quién "
               "votaría?")
OPS_2V = ["Iván Cepeda Castro", "Abelardo de la Espriella", "Votaría en blanco", "No votaría"]
REAL_2V = 100 * 2235514 / (2235514 + 1933243)                      # §4: preconteo, Bogotá
ENCUESTA_2V = {"Iván Cepeda Castro": 45.0, "Abelardo de la Espriella": 52.6}


def probs(perfiles: list[str], extra: str, pregunta: str, ops: list[str], llamar, cache, solo_cache: bool = False):
    """DI-ND1: la distribución de cada agente (dict opción → probabilidad), o None."""
    from src.experiments import personas_pulidas as pp
    sistema = pp.BASE + pp.SALIDA_PROB
    lineas = "; ".join(f"{i}={o}" for i, o in enumerate(ops, 1))
    esc = [{"clave": "E1", "validos": list(range(1, len(ops) + 1))}]

    def uno(p):
        u = f"QUIÉN ES:\n{p}\n\n{extra}\n\nPREGUNTAS NUEVAS:\nE1. {pregunta} Opciones: {lineas}"
        if solo_cache:
            t = cache.get(e9.Cache.clave(va.MODELO, va.TEMPERATURA, sistema, u, 0))
        else:
            if e9.gasto_registrado(cache)["costo_usd"] >= TOPE_USD:
                raise RuntimeError(f"Se llegó al tope de USD {TOPE_USD}.")
            t, _ = e9.pedir(llamar, cache, va.MODELO, va.TEMPERATURA, sistema, u, 0)
        q = pp.leer_prob(t or "", esc)["E1"]
        return {ops[i - 1]: x for i, x in q.items()} if q else None
    with ThreadPoolExecutor(max_workers=16) as ex:
        return list(ex.map(uno, perfiles))


def total(ps: list, peso: np.ndarray, ops: list[str]) -> dict[str, float]:
    ok = [j for j, q in enumerate(ps) if q]
    return {o: float(sum(peso[j] * ps[j].get(o, 0) for j in ok) / sum(peso[j] for j in ok)) for o in ops}


def calibrar(ps: list, peso: np.ndarray, cands: list[str], meta: dict[str, float], vueltas: int = 200) -> list:
    """DI-ND2: el ajuste se repite hasta que el total entre los candidatos quede en la encuesta (a 0,01 puntos)."""
    m = va.normalizar({c: meta.get(c, 0.0) for c in cands}, cands)
    out = list(ps)
    for _ in range(vueltas):
        t = va.normalizar(total(out, peso, cands), cands)
        if max(abs(t[c] - m[c]) for c in cands) < 0.01:
            break
        factor = {c: (m[c] / t[c] if t[c] > 0 else 0.0) for c in cands}
        nuevo = []
        for q in out:
            if not q:
                nuevo.append(None); continue
            r = {o: x * factor.get(o, 1.0) for o, x in q.items()}
            s = sum(r.values())
            nuevo.append({o: x / s for o, x in r.items()} if s > 0 else None)
        out = nuevo
    return out


def error_grupos(ps: list, panel, ops: list[str]) -> dict:
    """§3: la parte A de `grupos_y_galan_2026` con estas distribuciones."""
    from src.experiments import banco_lote7 as b7, grupos_y_galan_2026 as gg, voto_grupos as vg, voto_simulado as vs
    c = next(o for o in ops if "Cepeda" in o); a_ = next(o for o in ops if "Espriella" in o)
    pc_ = np.array([q.get(c, 0) if q else np.nan for q in ps]); pa_ = np.array([q.get(a_, 0) if q else np.nan for q in ps])
    w = panel.peso; ok = ~np.isnan(pc_)
    gr = gg.grupos_agentes(panel.datos[1].iloc[panel.personas])
    def parte(m):
        m = m & ok
        return gg.parte_cepeda(float(np.sum(w[m] * pc_[m])), float(np.sum(w[m] * pa_[m])))
    ag = {k: {g: parte(gr[k] == g) for g in gs if ((gr[k] == g) & ok).any()} for k, gs in gg.CORTES.items()}
    r = {**json.loads(b7.REALES.read_text(encoding="utf-8")), **json.loads(vs.REALES_G7.read_text(encoding="utf-8"))}
    gc, ga = vg.gruesos(r["CC893701_P1_1"]), vg.gruesos(r["CC893701_P1_2"])
    cnc = {k: {g: gg.parte_cepeda(gc[k][g][0], ga[k][g][0]) for g in gs if g in gc.get(k, {}) and g in ga.get(k, {})}
           for k, gs in gg.CORTES.items()}
    return gg.medir_grupos(ag, cnc, parte(np.ones(len(w), bool)))


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args(argv)
    from src.consulta import agentes as ag
    from src.experiments import voto_registraduria as vr
    reales = vr.reales("E3")
    ops = va.opciones(reales)
    cands = ops[:-2]
    real = va.normalizar({va._bonito(c): float(v) for c, v in reales.items()}, cands)
    panel = ag.Agentes()
    sal = SALIDA / ("simulado" if a.simulado else "")
    sal.mkdir(parents=True, exist_ok=True)
    cache = e9.Cache(sal / "cache.json")
    if a.simulado:
        rng = np.random.default_rng(0)
        def llamar(m, s, u, t):
            n = u.split("Opciones: ")[-1].count("=")
            return json.dumps({"E1": {str(i): float(x) for i, x in enumerate(rng.dirichlet(np.ones(n)), 1)}})
    else:
        llamar = e9.cliente_real(timeout=300, extra={"reasoning": {"effort": "low"}})
    contexto = vc.RESUMEN + "\n\n" + vc.ENCUESTA
    # parte 1
    if a.simulado:                                         # DI-ND3: el simulado nunca lee la caché real
        p_c2 = probs(panel.perfiles, contexto, va.PREGUNTA, ops, llamar, cache)
    else:
        p_c2 = probs(panel.perfiles, contexto, va.PREGUNTA, ops, llamar, e9.Cache(vc.SALIDA / "cache.json"), solo_cache=True)
    p_c2i = probs(panel.perfiles, contexto + "\n\n" + INSTRUCCION, va.PREGUNTA, ops, llamar, cache)
    p_c2k = calibrar(p_c2, panel.peso, cands, vc.copiar_encuesta(cands))
    p1 = {}
    for k, ps in (("C2", p_c2), ("C2i", p_c2i), ("C2k", p_c2k)):
        p1[k] = va.medir(va.normalizar(total(ps, panel.peso, cands), cands), real)
        p1[k]["sin_respuesta"] = sum(q is None for q in ps)
        print(f"parte 1 · {k}: {p1[k]}", flush=True)
    g_c2, g_c2k = error_grupos(p_c2, panel, ops), error_grupos(p_c2k, panel, ops)
    print(f"parte 1 · grupos (sin cifras del CNC): C2 {g_c2['error_grupos']}, C2k {g_c2k['error_grupos']}", flush=True)
    # parte 2
    contexto2 = vc.RESUMEN + "\n" + PRIMERA_VUELTA + "\n\n" + GUARUMO
    p_s = probs(panel.perfiles, contexto2, PREGUNTA_2V, OPS_2V, llamar, cache)
    p_si = probs(panel.perfiles, contexto2 + "\n\n" + INSTRUCCION, PREGUNTA_2V, OPS_2V, llamar, cache)
    p_sk = calibrar(p_s, panel.peso, OPS_2V[:2], ENCUESTA_2V)
    p2 = {}
    for k, ps in (("S", p_s), ("Si", p_si), ("Sk", p_sk)):
        t = total(ps, panel.peso, OPS_2V)
        cep = 100 * t[OPS_2V[0]] / (t[OPS_2V[0]] + t[OPS_2V[1]])
        p2[k] = {"cepeda": round(cep, 1), "error": round(abs(cep - REAL_2V), 1), "gana_cepeda": cep > 50,
                 "sin_respuesta": sum(q is None for q in ps)}
        print(f"parte 2 · {k}: {p2[k]}", flush=True)
    copia = 100 * 45.0 / 97.6
    ref2 = {"real": round(REAL_2V, 1), "copiar_encuesta": round(copia, 1), "error_copiar": round(abs(copia - REAL_2V), 1),
            "error_50": round(abs(50 - REAL_2V), 1)}
    regla = {"RN1": p1["C2i"]["eam"] <= p1["C2"]["eam"] - 0.5, "RN2": p2["Si"]["error"] <= p2["S"]["error"],
             "RK1": g_c2k["error_grupos"] < g_c2["error_grupos"], "RK2": p2["Sk"]["error"] <= p2["S"]["error"]}
    regla["instruccion_sirve"] = regla["RN1"] and regla["RN2"]
    regla["calibracion_sirve"] = regla["RK2"]                       # §5: RK1 ya no es a ciegas
    importa = {k: p2[k]["error"] < ref2["error_copiar"] for k in ("S", "Si", "Sk")}
    pred = {"PN1": regla["RN1"], "PN2": not regla["RN2"], "PN3": importa["S"], "PN4": p2["S"]["gana_cepeda"]}
    g = None if a.simulado else e9.gasto_registrado(cache)["costo_usd"]
    print(f"segunda vuelta, referencias: {ref2}")
    print(f"regla: {regla} | le ganan a copiar la encuesta: {importa} | predicciones: {pred} | gasto USD {g}")
    (sal / "resultado.json").write_text(json.dumps({"parte1": p1, "grupos": {"C2": g_c2, "C2k": g_c2k}, "parte2": p2,
                                                    "referencias_2v": ref2, "regla": regla, "le_ganan_a_copiar": importa,
                                                    "predicciones": pred, "gasto": g}, ensure_ascii=False, indent=1,
                                                   default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
