"""
¿Mejora la estimación si el catálogo de la página entra a las candidatas? (`docs/NIVEL_ACUERDO_CATALOGO_SPECIFICATION.md`).
Configuración C: las 139 candidatas de la página. E: esas más las 84 preguntas medidas del catálogo de la población
2022-2025. Modelo: GPT-6 Luna (D20). Objetivos: los 139 de la prueba del lote 8.

Uso:
    python src/experiments/nivel_acuerdo_catalogo.py --simulado   # sin gasto
    python src/experiments/nivel_acuerdo_catalogo.py --prueba     # 1 llamada de E, mide el costo
    python src/experiments/nivel_acuerdo_catalogo.py              # la corrida (tope USD 0,80)

DECISIONES DE IMPLEMENTACIÓN
============================

DI-NC1. **Cada pregunta del catálogo como candidata** (§2): el texto de la encuesta; las categorías de la escala que
    muestra la página (`motor.vista`), sin «no sabe»; el lado favorable de la página (`motor.lado`); y como resultado
    real el porcentaje de ese lado en la ciudad que da `responder_catalogo`. La cifra se calcula con el motor en modo
    simulado: responder una pregunta del catálogo no llama a ningún modelo.
DI-NC2. **C en los 139 se reutiliza** de `nivel_acuerdo_lote8.json`, como en DI-NL8a.
DI-NC3. **Nada se sube:** la salida trae porcentajes de las preguntas del CNC (D21).
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import banco as ba                    # noqa: E402
from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import nivel_acuerdo_lote6 as n6     # noqa: E402
from src.experiments import nivel_acuerdo_lote8 as n8     # noqa: E402
from src.experiments import nivel_acuerdo_validacion as nv  # noqa: E402
from src.experiments import nivel_parecidas_b as nb       # noqa: E402

MODELO = n8.MODELO
H = n8.H
TOPE_USD = 0.80
CACHE = ba.SALIDA / "cache_nivel_acuerdo_catalogo.json"
SALIDA = ba.SALIDA / "nivel_acuerdo_catalogo.json"
CANDIDATAS_CATALOGO = ba.SALIDA / "candidatas_catalogo.csv"
COLS = n8.COLS
CERCANAS = ("EDP25_Gx503", "EDP25_Hx503", "EDP25_Ix503")                  # §2


def fila_catalogo(f: dict, alto: float) -> dict:
    """DI-NC1: una pregunta del catálogo (ya en su vista) como candidata."""
    from src.consulta import motor as mo
    fav, _ = mo.lado(f)
    cats = "; ".join(f"{c}={f['etiquetas'][str(c)]}" for c in f["escala"])
    return {"id": f"CAT_{f['variable']}", "familia": f"CAT_{f['variable']}", "ambito": "Bogotá",
            "fuente": "Catálogo de la página (EPC 2022-2025)", "pregunta_pagina": f["pregunta"], "categorias": cats,
            "codigos_favorables": json.dumps([int(c) for c in fav]), "total": round(100 * alto, 2)}


def candidatas_catalogo() -> pd.DataFrame:
    """DI-NC1: las 84, con la cifra de la ciudad que da hoy la página."""
    from src.consulta import motor as mo
    m = mo.Motor(*mo.cliente(simulado=True))
    filas = [fila_catalogo(m._vista[v], m.responder_catalogo(v)["ciudad"]["alto"]) for v in m.catalogo]
    t = pd.DataFrame(filas)[COLS]
    t.to_csv(CANDIDATAS_CATALOGO, index=False, encoding="utf-8")
    return t


def candidatas() -> tuple[pd.DataFrame, pd.DataFrame]:
    """(C, E)."""
    c = n6.candidatas()[1]
    return c, pd.concat([c[COLS], candidatas_catalogo()], ignore_index=True)


def regla(rc: dict, re_: dict) -> dict:
    """Pre-registro §4."""
    c = {"e_pasa_validacion": re_["pasa"], "e_no_peor": re_["eam"] <= rc["eam"],
         "e_al_decidir": (re_["acierto_al_decidir"] or 0) >= 0.90 if re_["decide"] > 0 else False}
    return {**c, "e_reemplaza_a_c": all(c.values())}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    ap.add_argument("--prueba", action="store_true")
    a = ap.parse_args()
    cand_c, cand_e = candidatas()
    o129, o8 = n8.objetivos()
    todos = pd.concat([o129, o8], ignore_index=True)
    if set(todos.familia) & set(cand_e.familia[~cand_e.id.isin(cand_c.id)]):
        raise RuntimeError("Un objetivo comparte familia con una candidata del catálogo.")
    if a.simulado:
        cache, llamar = e9.Cache(Path(tempfile.gettempdir()) / "bss_catalogo_simulado.json"), nb.cliente_simulado(cand_e)
    else:
        cache, llamar = e9.Cache(CACHE), e9.cliente_real(timeout=300)
    if a.prueba:
        antes = nb.gastado(cache)
        nv.elegir_todas(todos, cand_e, llamar, cache, TOPE_USD, solo=1, modelo=MODELO)
        c = nb.gastado(cache) - antes
        print(f"una llamada de E costó USD {c:.4f} → las {len(todos)} costarían ~USD {len(todos) * c:.2f} (tope USD {TOPE_USD})")
        return 0
    prev = pd.DataFrame(json.loads(n8.SALIDA.read_text(encoding="utf-8"))["C"]["por_pregunta"])
    pc = prev[["id", "familia", "total", "S", "fallo"]]                       # DI-NC2
    pe_ = nv.elegir_todas(todos, cand_e, llamar, cache, TOPE_USD, modelo=MODELO)
    rc, re_ = nv.evaluar(pc, cand_c, todos, h=H), nv.evaluar(pe_, cand_e, todos, h=H)
    sub = {}
    for nombre, obj in (("lote8", o8), ("las129", o129), ("sin_cercanas", todos[~todos.id.isin(CERCANAS)])):
        sub[nombre] = {k: n6._cifras(nv.evaluar(p[p.id.isin(obj.id)], c, obj, h=H))
                       for k, p, c in (("C", pc, cand_c), ("E", pe_, cand_e))}
    r = regla(rc, re_)
    pred = {"P1": r["e_reemplaza_a_c"], "P2": sub["lote8"]["E"]["eam"] < 20,
            "P3": abs(sub["las129"]["E"]["eam"] - sub["las129"]["C"]["eam"]) < 1, "P4": re_["decide"] > rc["decide"]}
    for n, x in (("C", rc), ("E", re_)):
        print(f"{n} ({x['n']}): EAM {x['eam']:.1f} | lado {x['lado']:.0%} (ref {x['referencia_lado']:.0%}) | decide {x['decide']:.0%} "
              f"(«sí» {x['acierta_si']}/{x['dice_si']}, «no» {x['acierta_no']}/{x['dice_no']}) | pasa {x['pasa']}")
    for s, v in sub.items():
        print(f"  {s}: C EAM {v['C']['eam']:.1f} lado {v['C']['lado']:.0%} | E EAM {v['E']['eam']:.1f} lado {v['E']['lado']:.0%}")
    elegidas = pe_.ids.map(lambda x: sum(str(i).startswith("CAT_") for i in (x or [])))
    print(f"  E eligió al menos una del catálogo en {(elegidas > 0).sum()} de {len(pe_)}; en promedio {elegidas.mean():.1f} de 5")
    gasto = None if a.simulado else e9.gasto_registrado(cache)
    print(f"regla: {r} | predicciones: {pred} | gasto: {gasto and round(gasto['costo_usd'], 4)}")
    if not a.simulado:
        SALIDA.write_text(json.dumps({"C": rc, "E": re_, "sub": sub, "regla": r, "predicciones": pred, "gasto": gasto,
                                      "catalogo_elegidas": elegidas.tolist()}, ensure_ascii=False, indent=1, default=str),
                          encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
