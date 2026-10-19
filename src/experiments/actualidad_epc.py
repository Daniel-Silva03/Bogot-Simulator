"""
Un resumen de actualidad para los agentes (`docs/ACTUALIDAD_EPC_SPECIFICATION.md`): la gente de la EPC 2024, con y sin un
resumen de lo que pasó en Bogotá en 2025, frente a lo que respondió la EPC 2025.

Uso:
    python src/experiments/actualidad_epc.py --simulado    # sin gasto: prueba el circuito
    python src/experiments/actualidad_epc.py               # con el modelo real (tope USD 1)

DECISIONES DE IMPLEMENTACIÓN
============================

DI-AE1. **La llamada es la de la página** (`agentes.Agentes` con los datos de 2024): el mismo panel, el mismo modelo, la misma
    instrucción con probabilidades. Las siete preguntas van juntas en una llamada por agente.
DI-AE2. **Lo que se cuenta** es el lado de §3 entre quienes eligieron una opción de la escala, con el peso de la encuesta. Lo
    mismo para los agentes: la probabilidad de esas opciones entre las de la escala.
DI-AE3. **El simulado compara contra reales inventados** (40 % en 2024 y 45 % en 2025). Calcula los de verdad solo para
    comprobar que salen, sin mostrarlos: probar el circuito no deja ver nada.
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "actualidad_epc"
TOPE_USD = 1.0
NOTA = ("Las respuestas de arriba son de 2024. Estas preguntas son de finales de 2025, casi un año después: la persona puede "
        "haber cambiado de opinión.")
RESUMEN_2025 = (
    "Lo que pasó en Bogotá entre enero y agosto de 2025. El alcalde es Carlos Fernando Galán, en su segundo año de gobierno, y "
    "el presidente es Gustavo Petro.\n"
    "- El 12 de abril terminó el racionamiento de agua que la ciudad tuvo durante un año por la sequía del sistema Chingaza.\n"
    "- Siguen las obras de la primera línea del metro: en abril se probó el primer tren, y se anunció su llegada a Bogotá para "
    "septiembre.\n"
    "- En el primer trimestre subieron los homicidios frente al mismo periodo de 2024 y aumentaron los secuestros extorsivos; la "
    "seguridad es el tema más discutido de la ciudad.\n"
    "- El 7 de junio, el senador y precandidato presidencial Miguel Uribe Turbay fue atacado a tiros en un acto político en el "
    "barrio Modelia, en Bogotá; murió el 11 de agosto.\n"
    "- El alcalde y el presidente tuvieron choques públicos por el metro y por el agua.")
#: §3: (id, variable del catálogo, se cuenta, ¿decide?)
PREGUNTAS = (("A1", "GG7", (4, 5), True), ("A2", "CC5A_GALAN", (4, 5), True), ("A3", "MICE1_GALAN", (4, 5), True),
             ("A4", "MICE2_GALAN", (4, 5), True), ("A5", "MICE3_GALAN", (4, 5), True), ("A6", "GG3_GALAN", (4, 5), False),
             ("A7", "AG1", (1,), False))
CONCEJO = "¿Usted cómo califica, en términos generales, la gestión del Concejo de Bogotá?"


def escalas(catalogo: dict) -> list[dict]:
    """El texto y la escala de cada pregunta, como en la página."""
    from src.consulta import motor as mo
    out = []
    for i, var, cuenta, decide in PREGUNTAS:
        f = catalogo[var]
        texto = mo.GALAN_SOLO_AGENTES.get(var) or (CONCEJO if var == "CC5A_GALAN" else f["pregunta"].strip())
        etq = mo.escala_visible(f)
        out.append({"clave": i, "variable": var, "pregunta": texto, "validos": list(f["escala"]), "cuenta": cuenta,
                    "decide": decide, "categorias": dict(zip(f["escala"], etq))})
    return out


def reales(anio: int, esc: list[dict]) -> dict[str, float]:
    """DI-AE2: el porcentaje de lo que se cuenta en la EPC de ese año."""
    from src.experiments import personas_con_encuesta as pc
    base, d, perf = pc.datos(anio)
    col = {f["variable"]: c for _, c, f in perf}
    w = base.peso.to_numpy(float)
    out = {}
    for e in esc:
        x = pd.to_numeric(d[col[e["variable"]]], errors="coerce").to_numpy()
        m = np.isin(x, e["validos"]) & ~np.isnan(w)
        out[e["clave"]] = float(100 * np.sum(w[m] * np.isin(x[m], e["cuenta"])) / np.sum(w[m]))
    return out


def estimar(panel, esc: list[dict], extra: str, llamar, cache, modelo: str) -> dict[str, Optional[float]]:
    """DI-AE1, DI-AE2."""
    from src.consulta import agentes as ag
    from src.experiments import personas_pulidas as pp
    sistema = pp.BASE + pp.SALIDA_PROB
    preg = "\n".join(f'{e["clave"]}. {e["pregunta"]} Opciones: ' + "; ".join(f"{c}={t}" for c, t in e["categorias"].items())
                     for e in esc)

    def uno(perfil):
        if e9.gasto_registrado(cache)["costo_usd"] >= TOPE_USD:
            raise RuntimeError(f"Se llegó al tope de USD {TOPE_USD}.")
        u = f"QUIÉN ES:\n{perfil}\n\n{extra}\n\nPREGUNTAS NUEVAS:\n{preg}"
        t, _ = e9.pedir(llamar, cache, modelo, ag.TEMPERATURA, sistema, u, 0)
        return pp.leer_prob(t, esc)
    with ThreadPoolExecutor(max_workers=ag.PARALELO) as ex:
        ps = list(ex.map(uno, panel.perfiles))
    w = panel.peso
    out = {}
    for e in esc:
        v = [(j, sum(p[e["clave"]].get(c, 0) for c in e["cuenta"])) for j, p in enumerate(ps) if p[e["clave"]]]
        out[e["clave"]] = (float(100 * sum(w[j] * x for j, x in v) / sum(w[j] for j, _ in v)) if v else None)
    out["sin_respuesta"] = sum(1 for p in ps if not any(p.values()))
    return out


def evaluar(a: dict, b: dict, r24: dict, r25: dict, ids: list[str]) -> dict:
    """§6 y §7, en las que deciden."""
    def em(x):
        return float(np.mean([abs(x[i] - r25[i]) for i in ids]))
    e_a, e_b, e_rep = em(a), em(b), em(r24)
    dirb = {i: np.sign(b[i] - r24[i]) == np.sign(r25[i] - r24[i]) for i in ids}
    crit = {"RA1": {"umbral": "B menor que repetir 2024", "valor": [round(e_b, 1), round(e_rep, 1)], "se_cumple": e_b < e_rep},
            "RA2": {"umbral": "B menor que A", "valor": [round(e_b, 1), round(e_a, 1)], "se_cumple": e_b < e_a},
            "RA3": {"umbral": "dirección del cambio en ≥ 3 de 5", "valor": int(sum(dirb.values())),
                    "se_cumple": sum(dirb.values()) >= 3}}
    pes = sum((b[i] > a[i]) if i == "A1" else (b[i] < a[i]) for i in ids)
    pred = {"PA1": abs(e_a - e_rep) < 3, "PA2": not crit["RA1"]["se_cumple"], "PA3": bool(pes >= 4)}
    return {"criterios": crit, "pasa": all(c["se_cumple"] for c in crit.values()), "predicciones": pred,
            "direccion_b": {k: bool(v) for k, v in dirb.items()}, "error_a": round(e_a, 1), "error_b": round(e_b, 1),
            "error_repetir_2024": round(e_rep, 1), "b_mas_pesimista": int(pes)}


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args(argv)
    from src.consulta import agentes as ag
    from src.consulta import reformular as rf
    from src.experiments import personas_con_encuesta as pc
    catalogo = rf.cargar_catalogo(rf.CATALOGO_2025)
    esc = escalas(catalogo)
    r24, r25 = reales(2024, esc), reales(2025, esc)
    assert all(0 <= x <= 100 for x in list(r24.values()) + list(r25.values()))
    if a.simulado:                                                                                    # DI-AE3
        r24, r25 = {e["clave"]: 40.0 for e in esc}, {e["clave"]: 45.0 for e in esc}
    panel = ag.Agentes(datos=pc.datos(2024))
    sal = SALIDA / ("simulado" if a.simulado else "")
    sal.mkdir(parents=True, exist_ok=True)
    cache = e9.Cache(sal / "cache.json")
    if a.simulado:
        rng = np.random.default_rng(0)

        def llamar(m, s, u, t):
            return json.dumps({e["clave"]: {str(c): float(x) for c, x in zip(e["validos"], rng.dirichlet(np.ones(len(e["validos"]))))}
                               for e in esc})
        modelo = e9.MODELO_SIMULADO
    else:
        llamar, modelo = e9.cliente_real(timeout=300, extra={"reasoning": {"effort": "low"}}), ag.MODELO
    est_a = estimar(panel, esc, NOTA, llamar, cache, modelo)
    est_b = estimar(panel, esc, NOTA + "\n\n" + RESUMEN_2025, llamar, cache, modelo)
    ids = [e["clave"] for e in esc if e["decide"]]
    v = evaluar(est_a, est_b, r24, r25, ids)
    for e in esc:
        k = e["clave"]
        print(f"{k} {e['variable']:12} | 2024 {r24[k]:5.1f} | 2025 {r25[k]:5.1f} | A {est_a[k]:5.1f} | B {est_b[k]:5.1f}"
              f"{'' if e['decide'] else '   (no decide: ya vista)'}")
    for k, c in v["criterios"].items():
        print(f"  {k} {'se cumple' if c['se_cumple'] else 'NO se cumple'} — {c['umbral']} (valor {c['valor']})")
    g = None if a.simulado else e9.gasto_registrado(cache)["costo_usd"]
    print(f"pasa: {v['pasa']} | predicciones: {v['predicciones']} | sin respuesta A {est_a['sin_respuesta']}, "
          f"B {est_b['sin_respuesta']} | gasto USD {g}")
    (sal / "resultado.json").write_text(json.dumps({"a": est_a, "b": est_b, "real_2024": r24, "real_2025": r25, **v, "gasto": g},
                                                   ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)),
                                        encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
