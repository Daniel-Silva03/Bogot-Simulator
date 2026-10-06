"""
¿Mejora la estimación con las candidatas del lote 6? (`docs/NIVEL_ACUERDO_LOTE6_SPECIFICATION.md`).
Configuración B: las 109 candidatas de la página. C: esas más las 30 de práctica del lote 6. Modelo: GPT-6 Luna
(D20). Objetivos: las 95 guardadas de siempre y las guardadas del lote 6.

Uso:
    python src/experiments/nivel_acuerdo_lote6.py --reales     # resultados reales del guardado del lote 6 (sin API)
    python src/experiments/nivel_acuerdo_lote6.py --simulado   # sin gasto
    python src/experiments/nivel_acuerdo_lote6.py --prueba     # 1 llamada de C, mide el costo
    python src/experiments/nivel_acuerdo_lote6.py              # la corrida (tope USD 0,60)

DECISIONES DE IMPLEMENTACIÓN
============================

DI-NL6a. **B en las 95 se reutiliza** de `nivel_acuerdo_luna.json` (guardado): es exactamente la configuración B con
    Luna sobre esos objetivos, y volver a pedirla daría lo mismo (temperatura 0).
DI-NL6b. **Nada de las encuestas del CNC se sube.** Los resultados reales del guardado del lote 6 y la salida, que
    trae los porcentajes de cada pregunta, quedan en `data/processed/banco/`, ignorados por git (D21).
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
from src.experiments import banco_lote6 as b6              # noqa: E402
from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import nivel_acuerdo_lote5 as nl     # noqa: E402
from src.experiments import nivel_acuerdo_luna as nlu     # noqa: E402
from src.experiments import nivel_acuerdo_validacion as nv  # noqa: E402
from src.experiments import nivel_parecidas_b as nb       # noqa: E402

MODELO = nlu.MODELO
H = 23.4                                                    # el de Luna (D20)
TOPE_USD = 0.60
CACHE = ba.SALIDA / "cache_nivel_acuerdo_lote6.json"
SALIDA = ba.SALIDA / "nivel_acuerdo_lote6.json"
REALES_G6 = ba.SALIDA / "reales_guardado_lote6.json"
COLS = nl.COLS


def reales_guardado() -> dict:
    s = pd.read_csv(b6.SORTEO)
    s = s[s.conjunto == "guardado"].assign(conjunto="practica")             # copia: el archivo no cambia
    return b6.reales(s)


def _lote6(conjunto: str, reales: dict) -> pd.DataFrame:
    s = pd.read_csv(b6.SORTEO)
    s = s[(s.conjunto == conjunto) & s.id.map(lambda i: i in reales and not reales[i]["excluida"])].copy()
    return s.assign(total=s.id.map(lambda i: float(reales[i]["total"])))[COLS]


def candidatas() -> tuple[pd.DataFrame, pd.DataFrame]:
    """(B, C)."""
    b = nl.candidatas()[1]
    p6 = _lote6("practica", json.loads(b6.REALES.read_text(encoding="utf-8")))
    return b, pd.concat([b[COLS], p6], ignore_index=True)


def objetivos() -> tuple[pd.DataFrame, pd.DataFrame]:
    """(las 95, las guardadas del lote 6)."""
    o74, o21 = nl.objetivos()
    g6 = _lote6("guardado", json.loads(REALES_G6.read_text(encoding="utf-8")))
    return pd.concat([o74, o21], ignore_index=True), g6


def regla(rb: dict, rc: dict) -> dict:
    """Pre-registro §4."""
    c = {"c_pasa_validacion": rc["pasa"], "c_no_peor": rc["eam"] <= rb["eam"],
         "c_al_decidir": (rc["acierto_al_decidir"] or 0) >= 0.90 if rc["decide"] > 0 else False}
    return {**c, "c_reemplaza_a_b": all(c.values())}


def _cifras(r: dict) -> dict:
    """Solo error y acierto: nada de porcentajes de las preguntas (DI-NL6b)."""
    return {k: r[k] for k in ("n", "eam", "lado", "referencia_lado", "decide", "acierto_al_decidir", "dice_si", "acierta_si",
                              "dice_no", "acierta_no", "fallos", "pasa")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reales", action="store_true")
    ap.add_argument("--simulado", action="store_true")
    ap.add_argument("--prueba", action="store_true")
    a = ap.parse_args()
    if a.reales:
        r = reales_guardado()
        REALES_G6.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        exc = {k: v["excluida"] for k, v in r.items() if v["excluida"]}
        print(f"{len(r)} guardadas del lote 6; excluidas por estructura {len(exc)} {exc or ''}")
        return 0
    cand_b, cand_c = candidatas()
    o95, o6 = objetivos()
    o129 = pd.concat([o95, o6], ignore_index=True)
    if a.simulado:
        cache, llamar = e9.Cache(Path(tempfile.gettempdir()) / "bss_lote6_simulado.json"), nb.cliente_simulado(cand_c)
    else:
        cache, llamar = e9.Cache(CACHE), e9.cliente_real(timeout=300)
    if a.prueba:
        antes = nb.gastado(cache)
        nv.elegir_todas(o129, cand_c, llamar, cache, TOPE_USD, solo=1, modelo=MODELO)
        c = nb.gastado(cache) - antes
        print(f"una llamada de C costó USD {c:.4f} → las ~163 costarían ~USD {163 * c:.2f} (tope USD {TOPE_USD})")
        return 0
    prev = pd.DataFrame(json.loads(nlu.SALIDA.read_text(encoding="utf-8"))["guardado"]["por_pregunta"])
    b95 = prev[["id", "familia", "total", "S", "fallo"]]                    # DI-NL6a
    b6_ = nv.elegir_todas(o6, cand_b, llamar, cache, TOPE_USD, modelo=MODELO)
    pb = pd.concat([b95, b6_[["id", "familia", "total", "S", "fallo"]]], ignore_index=True)
    pc = nv.elegir_todas(o129, cand_c, llamar, cache, TOPE_USD, modelo=MODELO)
    rb, rc = nv.evaluar(pb, cand_b, o129, h=H), nv.evaluar(pc, cand_c, o129, h=H)
    sub6 = {k: nv.evaluar(p[p.id.isin(o6.id)], c, o6, h=H) for k, p, c in (("B", pb, cand_b), ("C", pc, cand_c))}
    sub95 = {k: nv.evaluar(p[p.id.isin(o95.id)], c, o95, h=H) for k, p, c in (("B", pb, cand_b), ("C", pc, cand_c))}
    r = regla(rb, rc)
    pred = {"P1": r["c_reemplaza_a_b"], "P2": sub6["C"]["eam"] <= sub6["B"]["eam"] - 2,
            "P3": abs(sub95["C"]["eam"] - sub95["B"]["eam"]) < 1, "P4": rc["decide"] > rb["decide"]}
    for n, x in (("B", rb), ("C", rc)):
        print(f"{n} ({x['n']}): EAM {x['eam']:.1f} | lado {x['lado']:.0%} (ref {x['referencia_lado']:.0%}) | decide {x['decide']:.0%} "
              f"(«sí» {x['acierta_si']}/{x['dice_si']}, «no» {x['acierta_no']}/{x['dice_no']}) | pasa {x['pasa']}")
    for n in ("B", "C"):
        print(f"  {n} solo lote 6 ({sub6[n]['n']}): EAM {sub6[n]['eam']:.1f} lado {sub6[n]['lado']:.0%} | las 95: EAM {sub95[n]['eam']:.1f}")
    gasto = None if a.simulado else e9.gasto_registrado(cache)
    print(f"regla: {r} | predicciones: {pred} | gasto: {gasto and round(gasto['costo_usd'], 4)}")
    if not a.simulado:
        SALIDA.write_text(json.dumps({"B": rb, "C": rc, "lote6": {k: _cifras(v) for k, v in sub6.items()},
                                      "las95": {k: _cifras(v) for k, v in sub95.items()}, "regla": r, "predicciones": pred,
                                      "gasto": gasto}, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
