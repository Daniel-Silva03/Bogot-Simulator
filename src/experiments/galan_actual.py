"""
Galán hoy (`docs/GALAN_ACTUAL_SPECIFICATION.md`): la combinación de los perfiles P y F, y un aviso de que la opinión es de
2025, contra la imagen de Galán en el ranking de CB de septiembre de 2026.

Uso:
    python src/experiments/galan_actual.py --simulado
    python src/experiments/galan_actual.py                       # corre FT; tope USD 1
    python src/experiments/galan_actual.py --real 41.0 --agosto 44.5

Sin `--real`, solo calcula los brazos; con las cifras de CB, mide contra la regla.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-GA1. **P y F salen de la caché** de `grupos_y_galan_2026`: el mismo mensaje, sin llamadas.
DI-GA2. **M promedia, agente por agente,** las distribuciones de P y F; un agente sin una de las dos queda con la que tenga.
DI-GA3. **La nota de FT va después del perfil**, antes de las preguntas.
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
from src.experiments import grupos_y_galan_2026 as gg     # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "galan_actual"
TOPE_USD = 1.0
NOTA = ("Las respuestas de arriba son de 2025. Estas preguntas son de septiembre de 2026, casi un año después: la persona puede "
        "haber cambiado de opinión sobre el alcalde.")
EPC_2025 = 45.0
CB_JUNIO = 44.3


def escalas():
    return [{"clave": k, "pregunta": t, "categorias": c, "validos": [x for x in c if x != 9]} for k, t, c, _, _ in gg.G]


def distribuciones(panel, ocultas, nota: str, llamar, cache) -> list:
    """La respuesta de cada agente a G2 (dict código → probabilidad) o None. DI-GA3."""
    from src.experiments import personas_politica as pq, personas_pulidas as pp
    sistema = pp.BASE + pp.SALIDA_PROB
    esc = escalas()
    preg = "\n".join(f'{e["clave"]}. {e["pregunta"]} Opciones: ' + "; ".join(f"{c}={t}" for c, t in e["categorias"].items())
                     for e in esc)

    def uno(i):
        if e9.gasto_registrado(cache)["costo_usd"] >= TOPE_USD:
            raise RuntimeError(f"Se llegó al tope de USD {TOPE_USD}.")
        quien = pq.perfil(i, panel.datos, ocultas, {}, con_vida=False)
        cuerpo = f"QUIÉN ES:\n{quien}\n\n{nota}\n\n" if nota else f"QUIÉN ES:\n{quien}\n\n"
        texto, _ = e9.pedir(llamar, cache, gg.va_modelo(), 1.0, sistema, cuerpo + f"PREGUNTAS NUEVAS:\n{preg}", 0)
        return pp.leer_prob(texto, esc)["G2"]
    with ThreadPoolExecutor(max_workers=16) as ex:
        return list(ex.map(uno, panel.personas))


def mezclar(a: list, b: list) -> list:
    """DI-GA2."""
    out = []
    for x, y in zip(a, b):
        if x and y:
            out.append({k: (x.get(k, 0) + y.get(k, 0)) / 2 for k in set(x) | set(y)})
        else:
            out.append(x or y or None)
    return out


def positiva(ps: list, peso: np.ndarray, fav=(3, 4)) -> float:
    ok = [j for j, q in enumerate(ps) if q]
    return float(100 * sum(peso[j] * sum(ps[j].get(c, 0) for c in fav) for j in ok) / sum(peso[j] for j in ok))


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    ap.add_argument("--real", type=float, help="CB, septiembre de 2026: imagen positiva de Galán")
    ap.add_argument("--agosto", type=float, help="CB, agosto de 2026")
    a = ap.parse_args(argv)
    from src.consulta import agentes as ag
    from src.experiments import personas_politica as pq
    panel = ag.Agentes()
    ocultas = [{"variable": c} for _, c, v in pq.ESCONDIDAS if v]
    sal = SALIDA / ("simulado" if a.simulado else "")
    sal.mkdir(parents=True, exist_ok=True)
    if a.simulado:
        rng = np.random.default_rng(0)
        esc = escalas()

        def llamar(m, s, u, t):
            return json.dumps({e["clave"]: {str(c): float(x) for c, x in zip(e["validos"], rng.dirichlet(np.ones(len(e["validos"]))))}
                               for e in esc})
        cache_pf = cache = e9.Cache(sal / "cache.json")
    else:
        llamar = e9.cliente_real(timeout=300, extra={"reasoning": {"effort": "low"}})
        cache_pf, cache = e9.Cache(gg.SALIDA / "cache.json"), e9.Cache(sal / "cache.json")
    d = {"P": distribuciones(panel, ocultas, "", llamar, cache_pf), "F": distribuciones(panel, [], "", llamar, cache_pf)}
    d["M"] = mezclar(d["P"], d["F"])
    d["FT"] = distribuciones(panel, [], NOTA, llamar, cache)
    brazos = {k: {"positiva": round(positiva(v, panel.peso), 1), "sin_respuesta": sum(q is None for q in v)} for k, v in d.items()}
    print(f"brazos: {brazos}", flush=True)
    out = {"brazos": brazos, "gasto": None if a.simulado else e9.gasto_registrado(cache)["costo_usd"]}
    if a.real is not None:
        def err(x):
            return round(abs(x - a.real), 1)
        ref = {"epc_2025": err(EPC_2025), "cb_junio": err(CB_JUNIO), "cb_agosto": err(a.agosto) if a.agosto is not None else None}
        for k in brazos:
            brazos[k]["error"] = err(brazos[k]["positiva"])

        def regla(k, p):
            r = {f"{p}1": brazos[k]["error"] <= 4, f"{p}2": brazos[k]["error"] < ref["epc_2025"],
                 f"{p}3": ref["cb_agosto"] is not None and brazos[k]["error"] < ref["cb_agosto"]}
            r["se_acerca"] = all(r.values())
            return r
        reglas = {"M": regla("M", "RG"), "FT": regla("FT", "RT")}
        pred = {"PG1": 38 <= a.real <= 46, "PG2": not reglas["M"]["RG1"],
                "PG3": brazos["FT"]["positiva"] < brazos["F"]["positiva"],
                "PG4": not reglas["M"]["RG3"] and not reglas["FT"]["RT3"]}
        out.update({"real": a.real, "cb_agosto": a.agosto, "referencias_error": ref, "reglas": reglas, "predicciones": pred})
        print(json.dumps({k: out[k] for k in ("referencias_error", "reglas", "predicciones")}, ensure_ascii=False))
    print(f"gasto USD {out['gasto']}")
    (sal / "resultado.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
