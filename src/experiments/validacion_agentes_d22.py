"""
Segunda validación de D22 (`docs/VALIDACION_AGENTES_D22_SPECIFICATION.md`): los agentes de la página con nueve mediciones
políticas del CNC de 2026 que ninguna prueba usó.

Uso:
    python src/experiments/validacion_agentes_d22.py --simulado    # sin gasto: prueba el circuito
    python src/experiments/validacion_agentes_d22.py               # con el modelo real (tope USD 1)

Necesita `BSS_CNC_POLITICA_DIR` (D21).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-VA1. **Los reales no se imprimen ni salen del equipo** (D21). Se calculan en `reales()` y se guardan en
    `data/processed/validacion_agentes_d22/`, que git ignora. Se imprime la cifra de los agentes, si acierta el lado y los
    errores medios.
DI-VA2. **La llamada es la de la página** (`agentes.Agentes`): el mismo panel, el mismo perfil, el mismo modelo, la misma
    instrucción. Solo cambian las opciones: las dos del cuestionario.
DI-VA3. **El simulado compara contra reales inventados** (40 % en todas). Lee los reales de verdad solo para comprobar que se
    pueden calcular, sin mostrarlos ni usarlos: así probar el circuito no deja ver nada de los resultados.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "validacion_agentes_d22"
TOPE_USD = 1.0
BOGOTA = "11001"
PETRO = "¿Usted tiene una imagen positiva o negativa del presidente Gustavo Petro?"
HABLO = "¿El día de ayer usted habló de política?"
#: §2: (id, estudio, variable, fecha, pregunta, opciones)
PREGUNTAS = (
    ("J1", "CC891901", "P20", "En enero de 2026", PETRO, ("Positiva", "Negativa")),
    ("J2", "CC892901", "P14", "A comienzos de 2026", PETRO, ("Positiva", "Negativa")),
    ("J3", "CC893201", "P15", "Entre marzo y abril de 2026", PETRO, ("Positiva", "Negativa")),
    ("J4", "CC893401", "P18", "A finales de abril de 2026", PETRO, ("Positiva", "Negativa")),
    ("J5", "CC893701", "P9", "En mayo de 2026", PETRO, ("Positiva", "Negativa")),
    ("H1", "CC892901", "P17", "A comienzos de 2026", HABLO, ("Sí", "No")),
    ("H2", "CC893201", "P16", "Entre marzo y abril de 2026", HABLO, ("Sí", "No")),
    ("H3", "CC893401", "P20", "A finales de abril de 2026", HABLO, ("Sí", "No")),
    ("H4", "CC893701", "P11", "En mayo de 2026", HABLO, ("Sí", "No")),
)


def texto(fecha: str, pregunta: str) -> str:
    return f"{fecha}: {pregunta}"


def reales() -> dict[str, float]:
    """DI-VA1: % de la opción 1 entre 1 y 2, ponderado, en Bogotá. No se imprime."""
    from src.experiments import banco_lote7 as b7
    d = os.environ.get("BSS_CNC_POLITICA_DIR")
    if not d or not Path(d).is_dir():
        raise RuntimeError("Falta BSS_CNC_POLITICA_DIR: la carpeta de las encuestas políticas del CNC (D21).")
    out = {}
    for i, est, var, *_ in PREGUNTAS:
        base = Path(d) / b7.ESTUDIOS[est][0]
        leer = ((lambda **k: pd.read_csv(base, encoding="latin-1", sep=None, engine="python", **k)) if base.suffix == ".csv"
                else (lambda **k: pd.read_excel(base, **k)))
        cols = list(leer(nrows=0).columns)
        fac = "FACTOR" if "FACTOR" in cols else "factor"
        b = leer(usecols=[var, "DANE", fac])
        b = b[b.DANE.astype(str).str.replace(r"\.0$", "", regex=True).str.strip() == BOGOTA]
        x = pd.to_numeric(b[var], errors="coerce")
        w = pd.to_numeric(b[fac].astype(str).str.replace(",", ".", regex=False), errors="coerce")
        m = x.isin([1, 2]) & w.notna()
        out[i] = float(100 * (w[m] * (x[m] == 1)).sum() / w[m].sum())
    return out


def estimar(panel, pregunta: str, opciones: tuple[str, str], llamar, cache, modelo: str) -> tuple[Optional[float], int]:
    """DI-VA2: (porcentaje de la opción 1, agentes que respondieron)."""
    from src.experiments import personas_pulidas as pp
    from src.consulta import agentes as ag
    sistema = pp.BASE + pp.SALIDA_PROB
    esc = [{"clave": "E1", "validos": [1, 2]}]
    ops = "; ".join(f"{i}={o}" for i, o in enumerate(opciones, 1))

    def uno(perfil):
        if e9.gasto_registrado(cache)["costo_usd"] >= TOPE_USD:
            raise RuntimeError(f"Se llegó al tope de USD {TOPE_USD}.")
        u = f"QUIÉN ES:\n{perfil}\n\nPREGUNTAS NUEVAS:\nE1. {pregunta} Opciones: {ops}"
        t, _ = e9.pedir(llamar, cache, modelo, ag.TEMPERATURA, sistema, u, 0)
        q = pp.leer_prob(t, esc)["E1"]
        return q.get(1, 0) / (q.get(1, 0) + q.get(2, 0)) if q and (q.get(1, 0) + q.get(2, 0)) > 0 else None
    with ThreadPoolExecutor(max_workers=ag.PARALELO) as ex:
        p = list(ex.map(uno, panel.perfiles))
    ok = np.array([x is not None for x in p])
    if not ok.any():
        return None, 0
    w = panel.peso
    return float(100 * np.sum(w[ok] * np.array([x for x in p if x is not None])) / w[ok].sum()), int(ok.sum())


def evaluar(est: dict[str, float], real: dict[str, float]) -> dict:
    """§5."""
    ids = [i for i, *_ in PREGUNTAS]
    err = {i: abs(est[i] - real[i]) for i in ids}
    lado = {i: (est[i] > 50) == (real[i] > 50) for i in ids}
    e9_, e50 = float(np.mean(list(err.values()))), float(np.mean([abs(50 - real[i]) for i in ids]))
    crit = {"RV1": {"umbral": "error medio ≤ 10", "valor": round(e9_, 1), "se_cumple": e9_ <= 10},
            "RV2": {"umbral": "menor que decir 50 %", "valor": [round(e9_, 1), round(e50, 1)], "se_cumple": e9_ < e50},
            "RV3": {"umbral": "lado correcto en ≥ 6 de 9", "valor": sum(lado.values()), "se_cumple": sum(lado.values()) >= 6}}
    petro = [est[i] for i in ids if i.startswith("J")]
    pred = {"PV1": all(c["se_cumple"] for c in crit.values()), "PV2": max(petro) - min(petro) < 5,
            "PV3": bool(np.mean([err[i] for i in ids if i.startswith("H")]) > np.mean([err[i] for i in ids if i.startswith("J")]))}
    return {"criterios": crit, "pasa": pred["PV1"], "predicciones": pred, "lado": lado,
            "error_medio": round(e9_, 1), "error_50": round(e50, 1),
            "error_petro": round(float(np.mean([err[i] for i in ids if i.startswith("J")])), 1),
            "error_hablo": round(float(np.mean([err[i] for i in ids if i.startswith("H")])), 1)}


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args(argv)
    from src.consulta import agentes as ag
    real = reales()
    assert len(real) == 9 and all(0 <= x <= 100 for x in real.values())
    if a.simulado:                     # DI-VA3: el simulado no compara contra los reales: nada de ellos se ve antes de correr
        real = {i: 40.0 for i, *_ in PREGUNTAS}
    panel = ag.Agentes()
    sal = SALIDA / ("simulado" if a.simulado else "")
    sal.mkdir(parents=True, exist_ok=True)
    cache = e9.Cache(sal / "cache.json")
    if a.simulado:
        rng = np.random.default_rng(0)

        def llamar(m, s, u, t):
            x = rng.dirichlet(np.ones(2))
            return json.dumps({"E1": {"1": float(x[0]), "2": float(x[1])}})
        modelo = e9.MODELO_SIMULADO
    else:
        llamar, modelo = e9.cliente_real(timeout=300, extra={"reasoning": {"effort": "low"}}), ag.MODELO
    est, resp = {}, {}
    for i, _, _, fecha, preg, ops in PREGUNTAS:
        est[i], resp[i] = estimar(panel, texto(fecha, preg), ops, llamar, cache, modelo)
        print(f"{i} {texto(fecha, preg)[:70]:70} | agentes {est[i]:.1f} % ({resp[i]} de {len(panel.perfiles)})", flush=True)
    v = evaluar(est, real)
    for i, *_ in PREGUNTAS:
        print(f"  {i}: lado {'acierta' if v['lado'][i] else 'falla'}")
    for k, c in v["criterios"].items():
        print(f"  {k} {'se cumple' if c['se_cumple'] else 'NO se cumple'} — {c['umbral']} (valor {c['valor']})")
    g = None if a.simulado else e9.gasto_registrado(cache)["costo_usd"]
    print(f"error Petro {v['error_petro']} | error habló {v['error_hablo']} | pasa: {v['pasa']} | predicciones: "
          f"{v['predicciones']} | gasto USD {g}")
    if not a.simulado:
        (sal / "reales.json").write_text(json.dumps(real, indent=1), encoding="utf-8")             # DI-VA1: no se sube
    (sal / "resultado.json").write_text(json.dumps({"agentes": est, "respondieron": resp, **v, "gasto": g},
                                                   ensure_ascii=False, indent=1, default=bool), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
