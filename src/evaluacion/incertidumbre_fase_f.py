"""
Fase F del plan de mejoras (`PLAN_MEJORAS_PREDICTOR_BOGOTA.md` §11 y §13): cuánto se equivoca cada tipo de evidencia, con los
errores reales de las pruebas, y si su intervalo cubre lo que debe en un año reservado.

Uso:
    python src/evaluacion/persistencia_epc.py && python src/evaluacion/temporal_fase_d.py && python src/evaluacion/benchmark.py
    python src/evaluacion/incertidumbre_fase_f.py

Sale en `config/incertidumbre.json`, que sí se sube: solo trae errores, ninguna cifra real (D21). La página lo lee.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-IF1. **Las clases de evidencia** son las de la página: el último dato medido según su antigüedad (un mes, dos meses, un año)
    y su dominio (gobierno e instituciones o lo demás); los agentes sin dato; y la estimación sin dato.
DI-IF2. **El intervalo es el percentil 80 del error** de la clase: en 8 de cada 10 casos pasados, el real quedó a esa distancia o
    menos. Con menos de 8 casos no se calcula percentil: se da solo el error medio, marcado como «pocos casos».
DI-IF3. **La cobertura se comprueba con un año reservado:** en la EPC, el percentil 80 de 2022 → 2023 y 2023 → 2024 se pone a
    prueba en 2024 → 2025. Con los agentes, el de `ACTUALIDAD_EPC` y `SELECTOR_FASE_B` (problema A) no sirve para lo que no tiene
    dato, así que se usan las pruebas con preguntas nunca usadas.
DI-IF4. **Los agentes de la página son Luna:** de `AGENTES_2026` entra solo el brazo L; los otros modelos no son los de la página.
DI-IF5. **Política y ciudad, por separado:** la página manda solas a los agentes las políticas, y con el botón, las de ciudad. Sus
    errores son muy distintos (el metro fue lo peor), así que cada una lleva el suyo. La validación de 74 preguntas de la
    estimación mezcla temas: entra en la de ciudad, que es su uso principal.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

B = RAIZ / "data" / "processed" / "benchmark"
SALIDA = RAIZ / "config" / "incertidumbre.json"
GOB = "gobierno e instituciones"
MINIMO = 8


def clase(nombre: str, errores, texto: str, agregados: tuple = ()) -> dict:
    """DI-IF2. `agregados`: (error medio, preguntas) de pruebas que solo guardaron su total; entran al error medio, no al p80."""
    e = np.asarray([x for x in errores if x is not None and not np.isnan(x)], float)
    n_ag = sum(n for _, n in agregados)
    suma = float(e.sum()) + sum(m * n for m, n in agregados)
    d = {"clase": nombre, "texto": texto, "n": int(len(e) + n_ag),
         "error_medio": round(suma / (len(e) + n_ag), 1) if len(e) + n_ag else None}
    d["p80"] = round(float(np.quantile(e, 0.8)), 1) if len(e) >= MINIMO else None
    d["pocos_casos"] = len(e) < MINIMO
    return d


def main() -> int:
    pe = pd.read_csv(B / "persistencia_epc.csv")
    td = pd.read_csv(B / "temporal_fase_d.csv")
    bm = pd.read_csv(B / "predicciones.csv")
    td["e0"] = (td.M0 - td.real).abs()
    nuevas = bm[(bm.problema == "B") & ~bm.agregado.astype(bool)]
    agregadas = bm[(bm.problema == "B") & bm.agregado.astype(bool)]
    pol = nuevas.dominio.isin([GOB, "política nacional", "conducta política"])                          # DI-IF5
    clases = [
        clase("mes", td[td.serie == "CB"].e0, "el dato es del mes anterior (CB, imagen de Galán, 2026)"),
        clase("dos_meses", td[td.serie == "Invamer"].e0, "el dato es de dos meses antes (Invamer, aprobación de Galán)"),
        clase("anio_gobierno", pe[pe.dominio == GOB].error_persistencia, "el dato es de un año antes, gobierno e instituciones (EPC)"),
        clase("anio_resto", pe[pe.dominio != GOB].error_persistencia, "el dato es de un año antes, lo demás (EPC)"),
        clase("agentes_politica", nuevas[nuevas.metodo.isin(["agentes (L)", "agentes"]) & pol].error,    # DI-IF4: solo Luna
              "agentes, pregunta política nunca medida (Galán y CNC de 2026)",
              tuple((float(r.error), int(r.n)) for r in agregadas[(agregadas.metodo == "agentes (L)")].itertuples())),
        clase("agentes_ciudad", nuevas[nuevas.metodo.isin(["agentes (L)", "agentes"]) & ~pol].error,
              "agentes, pregunta de ciudad nunca medida (el metro, 2026)"),
        clase("estimacion_politica", nuevas[(nuevas.metodo == "estimación de la página") & pol].error,
              "estimación de la página, pregunta política nunca medida"),
        clase("estimacion_ciudad", nuevas[(nuevas.metodo == "estimación de la página") & ~pol].error,
              "estimación de la página, pregunta de ciudad nunca medida",
              tuple((float(r.error), int(r.n)) for r in agregadas[agregadas.metodo == "estimación de la página"].itertuples())),
    ]
    # DI-IF3: la cobertura con un año reservado en la EPC
    cobertura = {}
    for nombre, filtro in (("anio_gobierno", pe.dominio == GOB), ("anio_resto", pe.dominio != GOB)):
        aj = pe[filtro & (pe.anio_objetivo < 2025)].error_persistencia
        ev = pe[filtro & (pe.anio_objetivo == 2025)].error_persistencia
        p80 = float(np.quantile(aj, 0.8))
        cobertura[nombre] = {"p80_ajustado_hasta_2024": round(p80, 1), "objetivos_2025": int(len(ev)),
                             "cubre_2025": round(float((ev <= p80).mean()), 2)}
    out = {"fecha": "2026-10-19", "metodo": "percentil 80 del error de las pruebas (DI-IF2)", "clases": clases,
           "cobertura_2025": cobertura}
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for c in clases:
        print(f"{c['clase']:20} n={c['n']:3}  error medio {c['error_medio']}  p80 {c['p80']}{'  (pocos casos)' if c['pocos_casos'] else ''}")
    print("cobertura en 2025:", json.dumps(cobertura, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
