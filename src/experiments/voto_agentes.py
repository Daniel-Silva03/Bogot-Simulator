"""
Intención de voto con agentes (`docs/VOTO_AGENTES_SPECIFICATION.md`, D23): los agentes de la EPC 2025 «votan» en la primera
vuelta de 2026 y se comparan con la Registraduría en Bogotá.

Uso:
    python src/experiments/voto_agentes.py --simulado
    python src/experiments/voto_agentes.py --memoria      # solo el control de memoria (1 llamada)
    python src/experiments/voto_agentes.py                # la corrida (tope USD 2)

Necesita `BSS_ELECTORAL_DIR` (D16).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-VA1. **Los candidatos van por orden alfabético del apellido**, con el nombre como lo escribe la Registraduría, pasado a
    mayúscula inicial. Así el orden no favorece a nadie.
DI-VA2. **La cifra de cada candidato** es la suma ponderada (`Factor1`) de su probabilidad, normalizada entre los 11; «en
    blanco» y «no votaría» no entran, como en el resultado oficial.
DI-VA3. **A1520** son todos los encuestados de la EPC 2025 de las localidades 1 a 19; A200, el panel de `agentes.Agentes`.
    Las llamadas de una misma persona se reutilizan de la caché.
DI-VA4. **El control de memoria** se lee a mano. El script guarda la respuesta del modelo y la imprime; quien la lee decide si
    sabe el resultado con la regla de §3 y lo anota en los resultados.
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

SALIDA = RAIZ / "data" / "processed" / "voto_agentes"
TOPE_USD = 2.0
MODELO = "openai/gpt-6-luna"
TEMPERATURA = 1.0
PARALELO = 16
BRAZOS = ("A200",)                                         # enmienda 1: sin A1520, para ahorrar
PREGUNTA = "Si la primera vuelta de las elecciones presidenciales de 2026 fuera hoy, ¿por quién votaría?"
MEMORIA = ("¿Qué porcentaje de los votos sacó cada candidato en Bogotá en la primera vuelta presidencial del 31 de mayo de "
           "2026? Responde con la lista de candidatos y sus porcentajes, o di que no lo sabes.")
SISTEMA_MEMORIA = "Responde con lo que sabes, en español."


def _bonito(nombre: str) -> str:
    return " ".join(p.capitalize() if p.lower() not in ("de", "la", "del") else p.lower() for p in nombre.split())


def opciones(reales) -> list[str]:
    """DI-VA1: los 11, por apellido, más «en blanco» y «no votaría»."""
    from src.experiments import voto_registraduria as vr
    cands = sorted(reales.index, key=lambda n: vr.clave(n)[1] if vr.clave(n)[1] else n)
    return [_bonito(c) for c in cands] + ["Votaría en blanco", "No votaría"]


def normalizar(tot: dict[str, float], cands: list[str]) -> dict[str, float]:
    s = sum(tot[c] for c in cands)
    return {c: 100 * tot[c] / s for c in cands} if s > 0 else {c: 0.0 for c in cands}


def medir(est: dict[str, float], real: dict[str, float]) -> dict:
    """§4: EAM entre los candidatos, el primero y los dos primeros."""
    eam = float(np.mean([abs(est[c] - real[c]) for c in real]))
    orden_e = sorted(est, key=est.get, reverse=True)
    orden_r = sorted(real, key=real.get, reverse=True)
    return {"eam": round(eam, 2), "primero": orden_e[0] == orden_r[0], "dos_primeros": orden_e[:2] == orden_r[:2],
            "estimado": {c: round(est[c], 1) for c in orden_e[:6]}}


def votar(perfiles: list[str], peso: np.ndarray, ops: list[str], llamar, cache) -> dict[str, float]:
    """DI-VA2: el total ponderado de cada opción."""
    from src.experiments import personas_pulidas as pp
    sistema = pp.BASE + pp.SALIDA_PROB
    lineas = "; ".join(f"{i}={o}" for i, o in enumerate(ops, 1))
    esc = [{"clave": "E1", "validos": list(range(1, len(ops) + 1))}]

    def uno(perfil):
        if e9.gasto_registrado(cache)["costo_usd"] >= TOPE_USD:
            raise RuntimeError(f"Se llegó al tope de USD {TOPE_USD}.")
        u = f"QUIÉN ES:\n{perfil}\n\nPREGUNTAS NUEVAS:\nE1. {PREGUNTA} Opciones: {lineas}"
        texto, _ = e9.pedir(llamar, cache, MODELO, TEMPERATURA, sistema, u, 0)
        return pp.leer_prob(texto, esc)["E1"]
    with ThreadPoolExecutor(max_workers=PARALELO) as ex:
        probs = list(ex.map(uno, perfiles))
    ok = [j for j, q in enumerate(probs) if q]
    return {o: float(sum(peso[j] * probs[j].get(i, 0) for j in ok) / sum(peso[j] for j in ok)) for i, o in enumerate(ops, 1)}


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    ap.add_argument("--memoria", action="store_true")
    a = ap.parse_args(argv)
    from src.consulta import agentes as ag
    from src.experiments import personas_politica as pq
    from src.experiments import voto_registraduria as vr
    reales = vr.reales("E3")
    ops = opciones(reales)
    cands = ops[:-2]
    nombre = {_bonito(c): c for c in reales.index}
    real = normalizar({_bonito(c): float(v) for c, v in reales.items()}, cands)
    sal = SALIDA / ("simulado" if a.simulado else "")
    sal.mkdir(parents=True, exist_ok=True)
    cache = e9.Cache(sal / "cache.json")
    if a.simulado:
        rng = np.random.default_rng(0)
        llamar = lambda m, s, u, t: json.dumps({"E1": {str(i): float(x) for i, x in enumerate(rng.dirichlet(np.ones(len(ops))), 1)}})  # noqa: E731
    else:
        llamar = e9.cliente_real(timeout=300, extra={"reasoning": {"effort": "low"}})
    if a.memoria or not a.simulado:
        texto, _ = e9.pedir(llamar, cache, MODELO, 0.0, SISTEMA_MEMORIA, MEMORIA, 0)
        (sal / "memoria.txt").write_text(texto, encoding="utf-8")
        print(f"CONTROL DE MEMORIA (DI-VA4):\n{texto}\n")
        if a.memoria:
            return 0
    panel = ag.Agentes()
    base, d, _ = panel.datos
    todos = np.flatnonzero(base.cod_loc.between(1, 19).to_numpy())
    perf_todos = lambda: [pq.perfil(i, panel.datos, [], {}, con_vida=False) for i in todos]   # noqa: E731
    res = {}
    brazos = {"A200": (panel.perfiles, panel.peso)}
    if "A1520" in BRAZOS:
        brazos["A1520"] = (perf_todos(), base.peso.to_numpy(float)[todos])
    for nombre_brazo, (perfiles, peso) in brazos.items():
        tot = votar(perfiles, peso, ops, llamar, cache)
        res[nombre_brazo] = {**medir(normalizar(tot, cands), real), "blanco": round(100 * tot["Votaría en blanco"], 1),
                             "no_votaria": round(100 * tot["No votaría"], 1), "n": len(perfiles)}
        print(f"{nombre_brazo}: {res[nombre_brazo]}", flush=True)
    mejor = min(res, key=lambda k: res[k]["eam"])
    m = res[mejor]
    regla = {"R1": m["eam"] <= 5.4, "R2": m["primero"], "R3": m["dos_primeros"]}
    regla["sirven"] = all(regla.values())
    pred = {"PV1": not regla["sirven"], "PV2": m["primero"],
            "PV3": (not (res["A1520"]["eam"] <= res["A200"]["eam"] - 0.5)) if "A1520" in res else "no se evalúa (enmienda 1)"}
    g = None if a.simulado else e9.gasto_registrado(cache)["costo_usd"]
    print(f"real: { {c: round(v, 1) for c, v in sorted(real.items(), key=lambda x: -x[1])[:6]} }")
    print(f"mejor: {mejor} | regla: {regla} | predicciones (PV4 se lee a mano): {pred} | gasto USD {g}")
    (sal / "resultado.json").write_text(json.dumps({"brazos": res, "real": real, "mejor": mejor, "regla": regla,
                                                    "predicciones": pred, "gasto": g, "nombres": nombre},
                                                   ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
