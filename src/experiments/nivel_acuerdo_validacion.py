"""
¿Estaría Bogotá de acuerdo?, validación en el guardado (`docs/NIVEL_ACUERDO_VALIDACION_SPECIFICATION.md`).
El método del paso 2 sin cambios: Claude Sonnet elige, entre las 92 preguntas de PRÁCTICA de acuerdo o
sí/no, las parecidas a cada pregunta GUARDADA de ese tipo; la predicción es la media real de las elegidas.

Uso:
    python src/experiments/nivel_acuerdo_validacion.py --reales     # resultados reales del guardado (sin API)
    python src/experiments/nivel_acuerdo_validacion.py --simulado   # sin gasto
    python src/experiments/nivel_acuerdo_validacion.py --prueba     # 1 llamada, mide el costo
    python src/experiments/nivel_acuerdo_validacion.py              # la corrida (tope USD 2,50)

Escribe en `data/processed/banco/`: `reales_guardado_acuerdo.json` (cifras agregadas, se sube),
`nivel_acuerdo_validacion.json` y la caché `cache_nivel_acuerdo_validacion.json` (no se sube).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-NV1. **Resultados del guardado con el mismo código de cada lote.**
    - Lote 1 (ECP, EPC): `banco_reales.resultado`, igual que `banco_reales.calcular`.
    - Lotes 2 y 3: `banco_lote2.reales` y `banco_lote3._calcular`, sobre las filas del guardado marcadas
      como objetivo. Esas funciones solo calculan lo que dice «practica», así que se les pasa una copia
      del sorteo con esas filas renombradas; el archivo del sorteo no cambia.

DI-NV2. **`CNC_METRO10`, del informe público** (p. 33 de `opinion_publica_2023-08-29.pdf`): «Sí» 38,7 %,
    «No» 49,7 %, Ns/Nr 11,6 %. Por DI-BR1, el total es sobre respuestas válidas:
    38,7 / (38,7 + 49,7) = 43,8 %. Se escribe a mano: el texto del informe no da una tabla legible por
    máquina.

DI-NV3. **Las candidatas son siempre las 92 de práctica:** a cada pregunta guardada se le arma una tabla con
    ella primero y las 92 después, y se usa `nivel_parecidas_b.elegir` sobre la fila 0. Como ninguna
    familia guardada está en la práctica, las 92 quedan como candidatas en todas.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import banco as ba                    # noqa: E402
from src.experiments import banco_reales as br             # noqa: E402
from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import nivel_acuerdo as na           # noqa: E402
from src.experiments import nivel_parecidas_b as nb       # noqa: E402

REALES = ba.SALIDA / "reales_guardado_acuerdo.json"
SALIDA = ba.SALIDA / "nivel_acuerdo_validacion.json"
CACHE = ba.SALIDA / "cache_nivel_acuerdo_validacion.json"
MODELO = nb.MODELOS["sonnet"]
TOPE_USD = 2.50
H = 21.9                                    # §3: fijado con la práctica, antes de ver el guardado
EAM_MAX, LADO_MIN, MARGEN = 15.8, 0.67, 0.10
METRO10 = round(100 * 38.7 / (38.7 + 49.7), 2)                                # DI-NV2


def objetivos() -> pd.DataFrame:
    """Las preguntas guardadas de acuerdo o sí/no de los lotes 1 a 3 (§2)."""
    filas = []
    for n, sor in ((1, "sorteo.csv"), (2, "sorteo_lote2.csv"), (3, "sorteo_lote3.csv")):
        s = pd.read_csv(ba.SALIDA / sor)
        for f in s[s.conjunto == "guardado"].to_dict("records"):
            t = na.tipo(f["categorias"])
            if t:
                filas.append({**f, "lote": n, "tipo": t})
    return pd.DataFrame(filas).sort_values("id").reset_index(drop=True)


def reales_guardado(o: pd.DataFrame) -> dict:
    """DI-NV1 y DI-NV2: {id: {total, excluida, ...}}."""
    out = {}
    datos = {}
    for f in o[o.lote == 1].to_dict("records"):
        if f["id"] == "CNC_METRO10":
            out[f["id"]] = {"total": METRO10, "n": 4575, "excluida": None, "fuente": f["fuente"]}
            continue
        clave = ("ECP", 2023) if f["fuente"] == "ECP DANE" else ("EPC", int(f["anio"]))
        if clave not in datos:
            datos[clave] = br._ecp() if clave[0] == "ECP" else br._epc(clave[1])
        d = datos[clave]
        x = pd.to_numeric(d[str(f["variable"]).upper()], errors="coerce")
        res = br.resultado(x, d.w, {"sexo": d.sexo, "edad": d.edad, "estrato": d.estrato},
                           json.loads(f["codigos_favorables"]), br.validos(br.categorias(f["categorias"])))
        out[f["id"]] = {"total": res["total"], "n": res["n"], "excluida": br.estructura(res), "fuente": f["fuente"]}
    from src.experiments import banco_lote2 as b2
    from src.experiments import banco_lote3 as b3
    for n, fn in ((2, lambda s: b2.reales(s, b2.cargar())), (3, b3.reales_bienal)):
        s = pd.read_csv(ba.SALIDA / ("sorteo_lote2.csv" if n == 2 else "sorteo_lote3.csv"))
        ids = set(o[o.lote == n].id)
        s = s[s.id.isin(ids)].assign(conjunto="practica")                    # DI-NV1: copia, el archivo no cambia
        for k, v in fn(s).items():
            out[k] = {"total": v["total"], "n": v["n"], "excluida": v["excluida"], "fuente": v["fuente"]}
    return out


def tabla_objetivo(o: pd.DataFrame, reales: dict) -> pd.DataFrame:
    o = o[o.id.map(lambda i: i in reales and not reales[i]["excluida"] and reales[i]["total"] is not None)].copy()
    o["total"] = o.id.map(lambda i: float(reales[i]["total"]))
    return o.reset_index(drop=True)


def elegir_todas(objetivo: pd.DataFrame, candidatas: pd.DataFrame, llamar, cache, tope: float, solo=None,
                 modelo: str = MODELO, orden: str = "pregunta") -> pd.DataFrame:
    """DI-NV3."""
    cols = ["id", "familia", "pregunta_pagina", "categorias", "codigos_favorables", "total"]
    tot = dict(zip(candidatas.id, candidatas.total))
    filas = []
    for i in range(len(objetivo) if solo is None else solo):
        q = objetivo.iloc[[i]][cols]
        t = pd.concat([q, candidatas[cols]], ignore_index=True)
        ids, _ = nb.elegir(t, 0, llamar, cache, modelo, tope, orden=orden)
        pred = float(np.mean([tot[x] for x in ids])) if ids else float(candidatas.total.mean())
        filas.append({"id": q.id.iloc[0], "familia": q.familia.iloc[0], "total": float(q.total.iloc[0]), "S": pred,
                      "ids": ids or [], "fallo": ids is None})
        if (i + 1) % 10 == 0:
            print(f"  {i + 1} preguntas, gasto registrado USD {nb.gastado(cache):.3f}", flush=True)
    return pd.DataFrame(filas)


def evaluar(p: pd.DataFrame, candidatas: pd.DataFrame, objetivo: pd.DataFrame, h: float = H) -> dict:
    real_si = p.total.to_numpy() > 50
    ref_si = bool(np.mean(candidatas.total > 50) > 0.5)
    ref = float(np.mean(real_si == ref_si))
    d = na.llamada(p.S.to_numpy(), np.full(len(p), h))
    dec = d != "dividida"
    err = (p.S - p.total).abs()
    general = p.id.isin(objetivo[objetivo.fuente == "ECP DANE"].id)
    r = {"n": len(p), "familias": int(p.familia.nunique()), "real_si": int(real_si.sum()), "referencia_lado": ref,
         "eam": float(err.mean()), "lado": float(np.mean((p.S > 50) == real_si)), "decide": float(dec.mean()),
         "acierto_al_decidir": float(np.mean((d[dec] == "sí") == real_si[dec])) if dec.any() else None,
         "dice_si": int((d == "sí").sum()), "acierta_si": int(((d == "sí") & real_si).sum()),
         "dice_no": int((d == "no").sum()), "acierta_no": int(((d == "no") & ~real_si).sum()),
         "fallos": int(p.fallo.sum()), "eam_ecp": float(err[general].mean()) if general.any() else None,
         "eam_bogota": float(err[~general].mean()) if (~general).any() else None}
    r["pasa"] = bool(r["eam"] <= EAM_MAX and r["lado"] >= LADO_MIN and r["lado"] >= ref + MARGEN)
    r["predicciones"] = {"P1": r["pasa"], "P2": r["eam"] > 13.9,
                         "P3": (r["acierto_al_decidir"] or 0) >= 0.85,
                         "P4": (r["eam_ecp"] or 0) > (r["eam_bogota"] or 0)}
    r["por_pregunta"] = p.assign(llamada=d).to_dict("records")
    return r


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reales", action="store_true")
    ap.add_argument("--simulado", action="store_true")
    ap.add_argument("--prueba", action="store_true")
    a = ap.parse_args()
    o = objetivos()
    if a.reales:
        r = reales_guardado(o)
        REALES.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        exc = {k: v["excluida"] for k, v in r.items() if v["excluida"]}
        print(f"{len(o)} objetivos; con resultado {len(r)}; excluidas por estructura {len(exc)} {exc or ''}")
        return 0
    objetivo = tabla_objetivo(o, json.loads(REALES.read_text(encoding="utf-8")))
    candidatas = na.tabla()
    if a.simulado:
        cache, llamar = e9.Cache(Path(tempfile.gettempdir()) / "bss_validacion_simulado.json"), nb.cliente_simulado(candidatas)
    else:
        cache, llamar = e9.Cache(CACHE), e9.cliente_real(timeout=300)
    if a.prueba:
        antes = nb.gastado(cache)
        elegir_todas(objetivo, candidatas, llamar, cache, TOPE_USD, solo=1)
        c = nb.gastado(cache) - antes
        print(f"una llamada costó USD {c:.4f} → las {len(objetivo)} costarían ~USD {len(objetivo) * c:.2f} (tope USD {TOPE_USD})")
        return 0
    p = elegir_todas(objetivo, candidatas, llamar, cache, TOPE_USD)
    r = evaluar(p, candidatas, objetivo)
    r["gasto"] = None if a.simulado else e9.gasto_registrado(cache)
    print(f"guardado: {r['n']} preguntas, {r['familias']} familias, mayoría «sí» en {r['real_si']} | EAM {r['eam']:.1f} "
          f"(máx {EAM_MAX}) | lado {r['lado']:.0%} (mín {LADO_MIN:.0%} y referencia {r['referencia_lado']:.0%} + 10) | "
          f"decide {r['decide']:.0%} («sí» {r['acierta_si']}/{r['dice_si']}, «no» {r['acierta_no']}/{r['dice_no']}) | "
          f"EAM ECP {r['eam_ecp']} Bogotá {r['eam_bogota']} | pasa: {r['pasa']}")
    print(f"predicciones: {r['predicciones']}; gasto: {r['gasto'] and round(r['gasto']['costo_usd'], 4)}")
    if not a.simulado:
        SALIDA.write_text(json.dumps(r, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
