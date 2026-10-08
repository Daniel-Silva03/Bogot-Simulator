"""
Intención de voto simulada, parte 2: contra los resultados de la Registraduría en Bogotá
(`docs/VOTO_REGISTRADURIA_SPECIFICATION.md`).

Material electoral (D21): nada se muestra en la página. Los resultados de las encuestas del CNC y de la simulación quedan
en `data/processed/banco/`, ignorados; lo impreso son errores y aciertos.

Uso:
    python src/experiments/voto_registraduria.py --candidatos   # qué candidatos entran en cada elección (sin API, sin resultados)
    python src/experiments/voto_registraduria.py --simulado     # el circuito, sin gasto
    python src/experiments/voto_registraduria.py                # la corrida (tope USD 0,20)

DECISIONES DE IMPLEMENTACIÓN
============================

DI-VR1. **El orden de las encuestas** (para «anteriores» y «la más reciente») es el de `FECHAS`. Hechos: las fechas de
    campo leídas de las bases (CC871401, CC871801, CC891901, CC893401 y CC893701) y los nombres de los archivos
    (CC875701, abril de 2022). Supuestos, por el contenido: CC873501 es de finales de 2021 («en marzo del próximo año
    serán las consultas»; Daniel lo confirmó el 8/10); CC892901 es anterior al 8 de marzo de 2026, y CC893201 queda entre marzo y abril de 2026,
    antes de CC893401.
DI-VR2. **Un nombre de opción nombra a un candidato** si trae su primer nombre y el primer apellido que no es partícula
    («de», «la», «del», «los»), sin tildes, mayúsculas ni puntuación. En 2022 el apellido sale de la columna
    `primer_apellido`, no de los nombres: así «Gustavo Francisco Petro» es Gustavo + Petro. Apodos: «Fico» = Federico
    (`ALIAS`). Arreglado el 7/10 antes de ver ningún resultado: la primera versión dejaba fuera a Petro y a
    Gutiérrez. El documento de los candidatos de 2026 (`CANCEDULA`) no se lee.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import banco as ba                    # noqa: E402
from src.experiments import banco_lote7 as b7              # noqa: E402
from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import nivel_acuerdo_validacion as nv  # noqa: E402
from src.experiments import nivel_parecidas_b as nb       # noqa: E402
from src.experiments import voto_simulado as vs           # noqa: E402

TOPE_USD = 0.20
CACHE = ba.SALIDA / "cache_voto_registraduria.json"
SALIDA = ba.SALIDA / "voto_registraduria.json"
FECHAS = {"CC871401": "2021-05-13", "CC871801": "2021-06-20", "CC873501": "2021-12-01", "CC875701": "2022-04-15",
          "CC891901": "2026-01-18", "CC892901": "2026-02-15", "CC893201": "2026-03-31", "CC893401": "2026-04-26",
          "CC893701": "2026-05-19"}                       # DI-VR1
ELECCIONES = {
    "E1": {"nombre": "primera vuelta 2022", "fecha": "2022-05-29", "tipos": ("primera", "primera_votantes", "formula"),
           "texto": "En mayo de 2022: si las elecciones presidenciales fueran mañana, ¿votaría por {x}?"},
    "E2": {"nombre": "segunda vuelta 2022", "fecha": "2022-06-19", "tipos": ("segunda",),
           "texto": "En junio de 2022: en una segunda vuelta entre Gustavo Petro y Rodolfo Hernández, ¿votaría por {x}?"},
    "E3": {"nombre": "primera vuelta 2026", "fecha": "2026-05-31", "tipos": ("primera", "primera_votantes", "formula"),
           "texto": "En mayo de 2026: si las elecciones presidenciales fueran mañana, ¿votaría por {x}?"},
}
PARTICULAS = {"de", "la", "del", "los", "las"}
ALIAS = {"fico": "federico"}                                # DI-VR2: apodos en las encuestas
FUERA = ("BLANCO", "NULO", "NO MARCAD")


def carpeta() -> Path:
    d = os.environ.get("BSS_ELECTORAL_DIR")
    if not d or not Path(d).is_dir():
        raise RuntimeError("Falta BSS_ELECTORAL_DIR: la carpeta de los resultados electorales (D16).")
    return Path(d)


def _palabras(s: str) -> list[str]:
    return [ALIAS.get(w, w) for w in re.findall(r"[a-z]+", vs._norm(s))]


def clave(nombre: str) -> tuple[str, str]:
    """DI-VR2: (primer nombre, primer apellido). Los nombres de 2022 llegan como «NOMBRE|APELLIDOS»."""
    if "|" in nombre:
        n, ap = nombre.split("|", 1)
        return (_palabras(n) or [""])[0], next((w for w in _palabras(ap) if w not in PARTICULAS), "")
    t = _palabras(nombre)
    return (t[0] if t else ""), next((w for w in t[1:] if w not in PARTICULAS), "")


def nombra(opcion: str, cand: str) -> bool:
    n, a = clave(cand)
    o = _palabras(opcion)
    return bool(n and a) and n in o and a in o


def reales(e: str, d: Path | None = None) -> pd.Series:
    """Votos de cada candidato en Bogotá (sin blanco, nulos ni no marcados)."""
    d = d or carpeta()
    if e in ("E1", "E2"):
        f = "2022_presidencia_primera_vuelta.dta" if e == "E1" else "2022_presidencia_segunda_vuelta.dta"
        t = pd.read_stata(d / f, convert_categoricals=False)
        t = t[t.municipio.astype(str).str.upper().str.contains("BOGOT")]
        nom = (t.nombres.astype(str).str.strip() + "|" + t.primer_apellido.astype(str).str.strip() + " " +
               t.segundo_apellido.astype(str).str.strip()).str.strip()
        v = pd.to_numeric(t.votos, errors="coerce").groupby(nom.values).sum()
    else:
        t = pd.read_csv(d / "registraduria_2026" / "MMV_XXX_16_000_XXX_XX_XX_XXX_1009.csv", sep=";",
                        usecols=["CANNOMBRE", "VOTOS"])                       # DI-VR2: sin CANCEDULA
        v = pd.to_numeric(t.VOTOS, errors="coerce").groupby(t.CANNOMBRE.astype(str)).sum()
    return v[[not any(x in k.upper() for x in FUERA) and k.strip() not in ("", "nan") for k in v.index]]


def preguntas() -> pd.DataFrame:
    """Las 373 del lote 7 con su resultado real, su tipo, su opción y su fecha."""
    rp = json.loads(b7.REALES.read_text(encoding="utf-8"))
    rg = json.loads(vs.REALES_G7.read_text(encoding="utf-8"))
    t = pd.concat([vs._tabla("practica", rp), vs._tabla("guardado", rg)], ignore_index=True)
    r = t.to_dict("records")
    return t.assign(tipo=[vs.tipo(x) for x in r], op=[vs.opcion(x) for x in r], est=t.id.map(vs.estudio),
                    fecha=t.id.map(vs.estudio).map(FECHAS))


def candidatos(e: str, q: pd.DataFrame, votos: pd.Series) -> list[str]:
    antes = q[q.fecha < ELECCIONES[e]["fecha"]]
    return [c for c in votos.index if antes.op.map(lambda o: nombra(o, c)).any()]


def ultima(e: str, q: pd.DataFrame, cands: list[str]) -> dict:
    """La referencia: la pregunta más reciente del mismo tipo que mide a cada candidato."""
    el = ELECCIONES[e]
    a = q[(q.fecha < el["fecha"]) & q.tipo.isin(el["tipos"])]
    if e == "E2":
        a = a[a.pregunta_pagina.map(lambda s: nombra(s, "Gustavo Petro") and nombra(s, "Rodolfo Hernández"))]
    out = {}
    for c in cands:
        m = a[a.op.map(lambda o: nombra(o, c))]
        if len(m):
            out[c] = float(m[m.fecha == m.fecha.max()].total.mean())
    return out


def normalizar(x: dict) -> dict:
    s = sum(x.values())
    return {k: 100 * v / s for k, v in x.items()} if s else {}


def medir(est: dict, real: dict) -> dict:
    est, real = normalizar(est), normalizar({k: real[k] for k in est})
    if not est:
        return {"n": 0}
    err = [abs(est[k] - real[k]) for k in est]
    out = {"n": len(est), "eam": float(np.mean(err)), "primero": max(est, key=est.get) == max(real, key=real.get)}
    if len(est) == 2:
        a, b = sorted(est)
        out["error_diferencia"] = float(abs((est[a] - est[b]) - (real[a] - real[b])))
    return out


def simular(e: str, q: pd.DataFrame, cands: list[str], llamar, cache, sin_llamar=False) -> dict:
    el = ELECCIONES[e]
    cand = q[q.fecha < el["fecha"]][vs.COLS].reset_index(drop=True)
    obj = pd.DataFrame([{"id": f"SIM_{e}_{i}", "familia": f"SIM_{e}_{i}", "ambito": "Bogotá", "fuente": "simulación",
                         "pregunta_pagina": el["texto"].format(x=c.replace("|", " ").title()), "categorias": "1=Sí; 2=No; 9=NS/NR",
                         "codigos_favorables": "[1]", "total": float("nan"), "anio": int(el["fecha"][:4]), "variable": ""}
                        for i, c in enumerate(cands)])
    p = nv.elegir_todas(obj, cand, llamar, cache, TOPE_USD, modelo=vs.MODELO, orden="candidatas")
    return {c: float(s) for c, s in zip(cands, p.S)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidatos", action="store_true")
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args()
    q = preguntas()
    if a.candidatos:
        for e in ELECCIONES:
            v = reales(e)
            c = candidatos(e, q, v)
            print(f"{e} ({ELECCIONES[e]['nombre']}): {len(c)} de {len(v)} candidatos con pregunta anterior: "
                  f"{[x.replace('|', ' ').title() for x in c]} | sin pregunta: {[x.replace('|', ' ').title() for x in v.index if x not in c]}")
            print(f"   con referencia de la última encuesta: {len(ultima(e, q, c))}")
        return 0
    if a.simulado:
        cache, llamar = e9.Cache(Path(tempfile.gettempdir()) / "bss_voto_reg.json"), nb.cliente_simulado(q[vs.COLS])
    else:
        cache, llamar = e9.Cache(CACHE), e9.cliente_real(timeout=300, corte_cache="PREGUNTA NUEVA")
    out = {}
    for e in ELECCIONES:
        v = reales(e)
        c = candidatos(e, q, v)
        real = {k: float(v[k]) for k in c}
        sim, ult = simular(e, q, c, llamar, cache), ultima(e, q, c)
        out[e] = {"candidatos": len(c), "simulacion": medir(sim, real), "ultima_encuesta": medir(ult, real)}
        print(f"{e} ({ELECCIONES[e]['nombre']}): simulación {out[e]['simulacion']} | última encuesta {out[e]['ultima_encuesta']}",
              flush=True)
        out[e]["detalle"] = {"simulacion": sim, "ultima": ult}                 # queda local, no se imprime
    s = [out[e]["simulacion"] for e in ELECCIONES]
    u = [out[e]["ultima_encuesta"] for e in ELECCIONES]
    pred = {"PR1": sum(x.get("eam", 99) < y.get("eam", 99) for x, y in zip(u, s)) >= 2,
            "PR2": sum(bool(x.get("primero")) for x in s) >= 2,
            "PR3": float(np.mean([x["eam"] for x in s if "eam" in x])) <= 8}
    gasto = None if a.simulado else e9.gasto_registrado(cache)
    print(f"predicciones: {pred} | gasto: {gasto and round(gasto['costo_usd'], 4)}")
    if not a.simulado:
        SALIDA.write_text(json.dumps({**out, "predicciones": pred, "gasto": gasto}, ensure_ascii=False, indent=1,
                                     default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
