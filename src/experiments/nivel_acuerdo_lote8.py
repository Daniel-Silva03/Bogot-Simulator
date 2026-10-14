"""
¿Mejora la estimación con las candidatas del lote 8? (`docs/NIVEL_ACUERDO_LOTE8_SPECIFICATION.md`).
Configuración C: las 139 candidatas de la página. D: esas más las 15 de práctica del lote 8 (EPC 2025). Modelo: GPT-6
Luna (D20). Objetivos: las 129 de la prueba del lote 6 y las guardadas del lote 8.

Uso:
    python src/experiments/nivel_acuerdo_lote8.py --reales     # resultados reales del guardado del lote 8 (sin API)
    python src/experiments/nivel_acuerdo_lote8.py --simulado   # sin gasto
    python src/experiments/nivel_acuerdo_lote8.py --prueba     # 1 llamada de D, mide el costo
    python src/experiments/nivel_acuerdo_lote8.py              # la corrida (tope USD 0,60)

DECISIONES DE IMPLEMENTACIÓN
============================

DI-NL8a. **C en las 129 se reutiliza** de `nivel_acuerdo_lote6.json`: es la configuración C con Luna sobre esos
    objetivos, y volver a pedirla daría lo mismo (temperatura 0).
DI-NL8b. **La salida no se sube:** trae los porcentajes de las preguntas del lote 6, que son del CNC (D21). Los resultados
    reales del guardado del lote 8 sí, porque la EPC es pública.
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
from src.experiments import banco_lote3 as b3              # noqa: E402
from src.experiments import banco_lote8 as b8              # noqa: E402
from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import nivel_acuerdo_lote6 as n6     # noqa: E402
from src.experiments import nivel_acuerdo_validacion as nv  # noqa: E402
from src.experiments import nivel_parecidas_b as nb       # noqa: E402

MODELO = n6.MODELO
H = n6.H
TOPE_USD = 0.60
CACHE = ba.SALIDA / "cache_nivel_acuerdo_lote8.json"
SALIDA = ba.SALIDA / "nivel_acuerdo_lote8.json"
REALES_G8 = ba.SALIDA / "reales_guardado_lote8.json"
COLS = n6.COLS


def reales_guardado() -> dict:
    s = pd.read_csv(b8.SORTEO)
    s = s[s.conjunto == "guardado"].assign(conjunto="practica")             # copia: el archivo no cambia
    return b3._calcular(s, *b8.base_epc25())


def _lote8(conjunto: str, reales: dict) -> pd.DataFrame:
    s = pd.read_csv(b8.SORTEO)
    s = s[(s.conjunto == conjunto) & s.id.map(lambda i: i in reales and not reales[i]["excluida"])].copy()
    return s.assign(total=s.id.map(lambda i: float(reales[i]["total"])))[COLS]


def candidatas() -> tuple[pd.DataFrame, pd.DataFrame]:
    """(C, D)."""
    c = n6.candidatas()[1]
    p8 = _lote8("practica", json.loads(b8.REALES.read_text(encoding="utf-8")))
    return c, pd.concat([c[COLS], p8], ignore_index=True)


def objetivos() -> tuple[pd.DataFrame, pd.DataFrame]:
    """(las 129, las guardadas del lote 8)."""
    o95, o6 = n6.objetivos()
    g8 = _lote8("guardado", json.loads(REALES_G8.read_text(encoding="utf-8")))
    return pd.concat([o95, o6], ignore_index=True), g8


def regla(rc: dict, rd: dict) -> dict:
    """Pre-registro §4."""
    c = {"d_pasa_validacion": rd["pasa"], "d_no_peor": rd["eam"] <= rc["eam"],
         "d_al_decidir": (rd["acierto_al_decidir"] or 0) >= 0.90 if rd["decide"] > 0 else False}
    return {**c, "d_reemplaza_a_c": all(c.values())}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reales", action="store_true")
    ap.add_argument("--simulado", action="store_true")
    ap.add_argument("--prueba", action="store_true")
    a = ap.parse_args()
    if a.reales:
        r = reales_guardado()
        REALES_G8.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        exc = {k: v["excluida"] for k, v in r.items() if v["excluida"]}
        print(f"{len(r)} guardadas del lote 8; excluidas por estructura {len(exc)} {exc or ''}")
        return 0
    cand_c, cand_d = candidatas()
    o129, o8 = objetivos()
    todos = pd.concat([o129, o8], ignore_index=True)
    if a.simulado:
        cache, llamar = e9.Cache(Path(tempfile.gettempdir()) / "bss_lote8_simulado.json"), nb.cliente_simulado(cand_d)
    else:
        cache, llamar = e9.Cache(CACHE), e9.cliente_real(timeout=300)
    if a.prueba:
        antes = nb.gastado(cache)
        nv.elegir_todas(todos, cand_d, llamar, cache, TOPE_USD, solo=1, modelo=MODELO)
        c = nb.gastado(cache) - antes
        n = len(o8) + len(todos)
        print(f"una llamada de D costó USD {c:.4f} → las ~{n} costarían ~USD {n * c:.2f} (tope USD {TOPE_USD})")
        return 0
    prev = pd.DataFrame(json.loads(n6.SALIDA.read_text(encoding="utf-8"))["C"]["por_pregunta"])
    c129 = prev[["id", "familia", "total", "S", "fallo"]]                   # DI-NL8a
    c8 = nv.elegir_todas(o8, cand_c, llamar, cache, TOPE_USD, modelo=MODELO)
    pc = pd.concat([c129, c8[["id", "familia", "total", "S", "fallo"]]], ignore_index=True)
    pd_ = nv.elegir_todas(todos, cand_d, llamar, cache, TOPE_USD, modelo=MODELO)
    rc, rd = nv.evaluar(pc, cand_c, todos, h=H), nv.evaluar(pd_, cand_d, todos, h=H)
    sub8 = {k: nv.evaluar(p[p.id.isin(o8.id)], c, o8, h=H) for k, p, c in (("C", pc, cand_c), ("D", pd_, cand_d))}
    sub129 = {k: nv.evaluar(p[p.id.isin(o129.id)], c, o129, h=H) for k, p, c in (("C", pc, cand_c), ("D", pd_, cand_d))}
    r = regla(rc, rd)
    pred = {"P1": r["d_reemplaza_a_c"], "P2": sub8["D"]["eam"] <= sub8["C"]["eam"] - 2,
            "P3": abs(sub129["D"]["eam"] - sub129["C"]["eam"]) < 1, "P4": rd["decide"] <= rc["decide"]}
    for n, x in (("C", rc), ("D", rd)):
        print(f"{n} ({x['n']}): EAM {x['eam']:.1f} | lado {x['lado']:.0%} (ref {x['referencia_lado']:.0%}) | decide {x['decide']:.0%} "
              f"(«sí» {x['acierta_si']}/{x['dice_si']}, «no» {x['acierta_no']}/{x['dice_no']}) | pasa {x['pasa']}")
    for n in ("C", "D"):
        print(f"  {n} solo lote 8 ({sub8[n]['n']}): EAM {sub8[n]['eam']:.1f} lado {sub8[n]['lado']:.0%} | "
              f"las 129: EAM {sub129[n]['eam']:.1f}")
    gasto = None if a.simulado else e9.gasto_registrado(cache)
    print(f"regla: {r} | predicciones: {pred} | gasto: {gasto and round(gasto['costo_usd'], 4)}")
    if not a.simulado:
        SALIDA.write_text(json.dumps({"C": rc, "D": rd, "lote8": {k: n6._cifras(v) for k, v in sub8.items()},
                                      "las129": {k: n6._cifras(v) for k, v in sub129.items()}, "regla": r,
                                      "predicciones": pred, "gasto": gasto}, ensure_ascii=False, indent=1, default=str),
                          encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
