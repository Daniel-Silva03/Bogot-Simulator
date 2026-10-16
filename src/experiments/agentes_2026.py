"""
Agentes con su encuesta en preguntas de 2026 (`docs/AGENTES_2026_SPECIFICATION.md`): 200 encuestados de la EPC 2025, con
probabilidades, responden las 13 preguntas de las validaciones de 2026, con Luna, con DeepSeek y con los dos promediados.
Contra la página.

Uso:
    python src/experiments/agentes_2026.py --simulado
    python src/experiments/agentes_2026.py

Necesita `BSS_CNC_POLITICA_DIR` para los resultados reales de K1 a K7 (D21).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-AG1. **El texto de K1 a K7** es el del cuestionario del CNC, sin el número de la pregunta y sin la instrucción final al
    encuestador, que el inventario trae cortada. Las escalas de 1 a 5 rotulan sus dos puntas con las frases del cuestionario
    y dejan 2, 3 y 4 en número.
DI-AG2. **M es la media de las probabilidades** de Luna y DeepSeek por persona y pregunta, renormalizada. Si uno de los dos no
    respondió esa pregunta, se usa el otro.
DI-AG3. **Lo que se imprime** de K1 a K7 es solo el error medio y cuántas aciertan el lado (D21).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import personas_con_encuesta as pc   # noqa: E402
from src.experiments import personas_pulidas as pp        # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "agentes_2026"
SEMILLA = 20261017
TOPE_USD = 1.0
MODELOS = {"L": ("openai/gpt-6-luna", {"reasoning": {"effort": "low"}}),
           "S": ("deepseek/deepseek-v4-pro", {"reasoning": {"enabled": False}})}
PAGINA = {"V1": 62.2, "V2": 59.5, "V3": 56.0, "V4": 56.4, "V5": 54.8, "V6": 28.6,
          "K1": 27.8, "K2": 28.9, "K3": 37.6, "K4": 44.8, "K5": 50.7, "K6": 36.9, "K7": 45.8}       # §3
REAL_PUBLICO = {"V1": 93.0, "V2": 70.0, "V3": 80.0, "V4": 88.0, "V5": 56.0, "V6": 26.0}
SI_NO = {1: "Sí", 2: "No"}


def _dos_frases(a: str, b: str) -> dict[int, str]:
    return {1: f"1 = {a}", 2: "2", 3: "3", 4: "4", 5: f"5 = {b}", 9: "No sabe"}


#: §2: (id, texto, categorías, favorables)
PREGUNTAS = (
    ("V1", "¿Cree que el metro mejorará la movilidad en Bogotá?", SI_NO, [1]),
    ("V2", "¿Usaría el metro como su principal medio de transporte?", SI_NO, [1]),
    ("V3", "¿Confía en el proyecto del metro de Bogotá?", SI_NO, [1]),
    ("V4", "¿El metro es un motivo de orgullo para Bogotá?", SI_NO, [1]),
    ("V5", "¿Cree que el metro empezará a funcionar en 2028?", SI_NO, [1]),
    ("V6", "¿Tiene una imagen favorable del alcalde Galán?", {1: "Desfavorable", 2: "Favorable"}, [2]),
    ("K1", "Pensando en los últimos 3 años y medio, en términos generales, ¿cree usted que Colombia está progresando o está "
           "retrocediendo?", {1: "Está progresando", 2: "Está igual", 3: "Está retrocediendo", 9: "No sabe"}, [1]),
    ("K2", "¿A usted personalmente el aumento del 23 % del salario mínimo lo beneficia o lo perjudica?",
     {1: "Lo beneficia", 2: "Lo perjudica", 9: "No sabe"}, [1]),
    ("K3", "Sobre la exploración de petróleo, en una escala de 1 a 5, ¿en qué punto se ubica usted?",
     _dos_frases("Se debe frenar la exploración de petróleo", "Se debe incrementar la exploración de petróleo"), [4, 5]),
    ("K4", "Sobre los diálogos de paz, en una escala de 1 a 5, ¿en qué punto se ubica usted?",
     _dos_frases("Persistir en los diálogos de paz con los grupos armados", "Frenar los diálogos de paz con los grupos armados"),
     [1, 2]),
    ("K5", "Sobre el manejo del Estado, en una escala de 1 a 5, ¿en qué punto se ubica usted?",
     _dos_frases("Tener un Estado más grande que realice más inversión social",
                 "Tener un Estado más pequeño que controle el gasto público"), [1, 2]),
    ("K6", "Sobre las relaciones de Colombia con Estados Unidos, en una escala de 1 a 5, ¿en qué punto se ubica usted?",
     _dos_frases("Debemos tener relaciones distantes con Estados Unidos", "Debemos tener relaciones cercanas con Estados Unidos"),
     [4, 5]),
    ("K7", "Sobre el sistema de salud, en una escala de 1 a 5, ¿en qué punto se ubica usted?",
     _dos_frases("El sistema de salud lo debe manejar el Estado",
                 "El sistema de salud lo debe manejar el Estado con colaboración de los privados"), [1, 2]),
)


def esc() -> list[dict]:
    return [{"clave": i, "variable": i, "pregunta": t, "categorias": c, "fav": f,
             "validos": [k for k in c if k != 9]} for i, t, c, f in PREGUNTAS]


def promediar(a: Optional[dict], b: Optional[dict]) -> Optional[dict]:
    """DI-AG2."""
    if not a or not b:
        return a or b
    ks = set(a) | set(b)
    q = {k: (a.get(k, 0) + b.get(k, 0)) / 2 for k in ks}
    s = sum(q.values())
    return {k: v / s for k, v in q.items()} if s > 0 else None


def total(probs: list[Optional[dict]], fav: list[int], w: np.ndarray) -> Optional[float]:
    ok = [j for j, q in enumerate(probs) if q]
    if not ok:
        return None
    return float(100 * sum(w[j] * sum(probs[j].get(c, 0) for c in fav) for j in ok) / sum(w[j] for j in ok))


def resumen(tot: dict[str, Optional[float]], real: dict[str, float]) -> dict:
    ids = [i for i in tot if tot[i] is not None]
    err = {i: abs(tot[i] - real[i]) for i in ids}
    lado = sum((tot[i] > 50) == (real[i] > 50) for i in ids)
    def media(f):
        v = [err[i] for i in ids if f(i)]
        return round(float(np.mean(v)), 1) if v else None
    return {"error_13": media(lambda i: True), "error_sin_V5": media(lambda i: i != "V5"),
            "error_publicas": media(lambda i: i.startswith("V")), "error_cnc": media(lambda i: i.startswith("K")),
            "lado": lado, "lado_cnc": sum((tot[i] > 50) == (real[i] > 50) for i in ids if i.startswith("K")), "n": len(ids)}


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args(argv)
    from src.experiments import personas_politica as pq
    from src.experiments import validacion_cnc_2026 as vk
    datos = pc.datos_2025()
    base, d, perf = datos
    elegibles = np.flatnonzero(base.cod_loc.between(1, 19).to_numpy())
    dev = np.random.default_rng(pc.SEMILLA).choice(elegibles, pc.N, replace=False)
    fin = np.random.default_rng(pp.SEMILLA_FINAL).choice(np.setdiff1d(elegibles, np.sort(dev)), pc.N, replace=False)
    libres = np.setdiff1d(elegibles, np.concatenate([dev, fin]))
    pol = np.random.default_rng(pq.SEMILLA).choice(libres, pc.N, replace=False)
    personas = np.sort(np.random.default_rng(SEMILLA).choice(np.setdiff1d(libres, pol), pc.N, replace=False))
    e = esc()
    real = dict(REAL_PUBLICO)
    real.update({k: (40.0 if a.simulado else v) for k, v in (vk.reales() if not a.simulado else {f"K{i}": 0 for i in range(1, 8)}).items()})
    w = base.peso.to_numpy(float)[personas]
    sistema = pp.BASE + pp.SALIDA_PROB
    cache = e9.Cache(SALIDA / ("simulado" if a.simulado else "") / "cache.json")
    rng = np.random.default_rng(0)
    probs = {m: [] for m in MODELOS}
    for m, (modelo, extra) in MODELOS.items():
        if a.simulado:
            llamar = lambda mo, s, u, t: json.dumps({x["clave"]: {str(c): float(p) for c, p in zip(x["validos"], rng.dirichlet(np.ones(len(x["validos"]))))} for x in e})  # noqa: E731
        else:
            llamar = e9.cliente_real(timeout=300, extra=extra)
        for j, i in enumerate(personas):
            if e9.gasto_registrado(cache)["costo_usd"] >= TOPE_USD:
                raise RuntimeError(f"Se llegó al tope de USD {TOPE_USD}.")
            t = pq.perfil(i, datos, [], {}, con_vida=False)
            u = f"QUIÉN ES:\n{t}\n\nPREGUNTAS NUEVAS:\n{pq.preguntas_texto(e)}"
            texto, _ = e9.pedir(llamar, cache, modelo, pc.TEMPERATURA, sistema, u, 0)
            probs[m].append(pp.leer_prob(texto, e))
            if (j + 1) % 50 == 0:
                print(f"   {m}: {j + 1} de {len(personas)}; gasto USD {e9.gasto_registrado(cache)['costo_usd']:.3f}", flush=True)
    res, por_v = {}, {}
    for brazo in ("L", "S", "M"):
        tot = {}
        for x in e:
            ps = ([p[x["clave"]] for p in probs[brazo]] if brazo != "M"
                  else [promediar(pl[x["clave"]], ps_[x["clave"]]) for pl, ps_ in zip(probs["L"], probs["S"])])
            tot[x["clave"]] = total(ps, x["fav"], w)
        res[brazo] = resumen(tot, real)
        por_v[brazo] = {i: (round(tot[i], 1) if tot[i] is not None else None) for i in tot if i.startswith("V")}
    pag = resumen(dict(PAGINA), real)
    mitad = resumen({i: 50.0 for i in PAGINA}, real)
    mejor = min(("L", "M"), key=lambda b: res[b]["error_13"])
    regla = {"R1": res[mejor]["error_13"] < pag["error_13"] and res[mejor]["error_sin_V5"] < pag["error_sin_V5"],
             "R2": res[mejor]["lado"] >= pag["lado"]}
    regla["ganan"] = all(regla.values())
    metro = ("V1", "V2", "V3", "V4")
    pred = {"PA1": res["L"]["error_13"] < pag["error_13"], "PA2": res["M"]["error_13"] <= res["L"]["error_13"] - 1,
            "PA3": all(abs(por_v["L"][v] - real[v]) < abs(PAGINA[v] - real[v]) for v in metro if por_v["L"][v] is not None),
            "PA4": not (res["L"]["error_cnc"] < mitad["error_cnc"])}
    for b in ("L", "S", "M"):
        print(f"{b}: {res[b]} | públicas: {por_v[b]}")
    print(f"página: {pag} | 50 %: {mitad}")
    g = None if a.simulado else e9.gasto_registrado(cache)["costo_usd"]
    print(f"mejor: {mejor} | regla: {regla} | predicciones: {pred} | gasto USD {g}")
    sal = SALIDA / ("simulado" if a.simulado else "")
    sal.mkdir(parents=True, exist_ok=True)
    (sal / "resultado.json").write_text(json.dumps({"brazos": res, "publicas": por_v, "pagina": pag, "mitad": mitad,
                                                    "mejor": mejor, "regla": regla, "predicciones": pred, "gasto": g},
                                                   ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
