"""
Fase A del plan de mejoras (`docs/PLAN_MEJORAS_PREDICTOR_BOGOTA.md`, §13): todas las pruebas ya hechas, en un formato único.

Una fila por pregunta y método, con la predicción, lo real y el error, separando el problema A (pregunta ya medida: hay un dato
anterior comparable) del problema B (pregunta nunca medida, o escondida a los agentes). No llama a ningún modelo: lee los
resultados guardados.

Uso:
    python src/evaluacion/persistencia_epc.py      # primero: la persistencia de la EPC
    python src/evaluacion/benchmark.py

Sale en `data/processed/benchmark/predicciones.csv`, que git ignora: trae cifras reales de las encuestas del CNC (D21). Lo que se
publica, en `docs/BENCHMARK_FASE_A.md`, son solo errores.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-BB1. **Solo lo que quedó guardado por pregunta.** Las pruebas que guardaron solo su total (las 139 de la estimación, las 7 del
    CNC de `AGENTES_2026`) entran como una fila de resumen, marcada `agregado`, con su error medio y su número de preguntas.
DI-BB2. **El voto entra aparte:** es multiclase. Una fila por prueba y método, con el error medio entre candidatos (primera
    vuelta) o el error en la parte de Cepeda (segunda vuelta). No se mezcla con los porcentajes de opinión.
DI-BB3. **Las filas del CNC llevan `cnc = True`.** Su `real` no sale del equipo; el resumen público solo usa sus errores.
DI-BB4. **Las ya vistas** (la gestión de Galán y el rumbo en `ACTUALIDAD_EPC`) llevan `vista = True` y quedan fuera de los
    errores medios del resumen.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

P = RAIZ / "data" / "processed"
SALIDA = P / "benchmark"


def _leer(ruta: Path):
    return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else None


def fila(fuente, id_, dominio, problema, metodo, pred, real, cnc=False, vista=False, n=1, agregado=False, error=None):
    err = error if error is not None else (abs(pred - real) if pred is not None and real is not None else None)
    return {"fuente": fuente, "id": id_, "dominio": dominio, "problema": problema, "metodo": metodo,
            "prediccion": None if pred is None else round(float(pred), 2), "real": None if real is None else round(float(real), 2),
            "error": None if err is None else round(float(err), 2), "sesgo": None if pred is None or real is None
            else round(float(pred - real), 2), "cnc": cnc, "vista": vista, "n": n, "agregado": agregado}


def filas() -> list[dict]:
    out = []
    # 1. la persistencia de la EPC (problema A)
    t = pd.read_csv(SALIDA / "persistencia_epc.csv")
    for r in t.itertuples():
        out.append(fila("persistencia_epc", f"{r.variable}:{r.anio_base}>{r.anio_objetivo}", r.dominio, "A", "persistencia",
                        r.dato_base, r.real))
    # 2. ACTUALIDAD_EPC: la gente de 2024 frente a la EPC 2025 (problema A)
    if (a := _leer(P / "actualidad_epc" / "resultado.json")):
        from src.experiments import actualidad_epc as ae
        decide = {i: d for i, _, _, d in ae.PREGUNTAS}
        for i in decide:
            for met, x in (("agentes", a["a"][i]), ("agentes + resumen", a["b"][i]), ("persistencia", a["real_2024"][i])):
                out.append(fila("actualidad_epc", i, "gobierno e instituciones", "A", met, x, a["real_2025"][i],
                                vista=not decide[i]))
    # 3. GALAN_ACTUAL: imagen de Galán en CB, septiembre de 2026 (problema A, medición cercana)
    if (g := _leer(P / "galan_actual" / "resultado.json")):
        for k, met in (("P", "agentes sin opiniones de gobierno"), ("F", "agentes"), ("M", "agentes, mezcla P y F"),
                       ("FT", "agentes con aviso")):
            out.append(fila("galan_actual", "CB sep 2026", "gobierno e instituciones", "A", met, g["brazos"][k]["positiva"],
                            g["real"]))
        out.append(fila("galan_actual", "CB sep 2026", "gobierno e instituciones", "A", "persistencia (EPC 2025)", 45.0, g["real"]))
        out.append(fila("galan_actual", "CB sep 2026", "gobierno e instituciones", "A", "persistencia (CB del mes anterior)",
                        g["cb_agosto"], g["real"]))
    # 4. GRUPOS_Y_GALAN_2026, parte B (problema A, medición cercana)
    if (g := _leer(P / "grupos_y_galan_2026" / "galan.json")):
        for k, met in (("P", "agentes sin opiniones de gobierno"), ("F", "agentes")):
            for q in ("G1", "G2"):
                b = g["brazos"][k][q]
                out.append(fila("grupos_y_galan_2026", q, "gobierno e instituciones", "A", met, b["agentes"], b["real"]))
        for q, real in (("G1", 53.3), ("G2", 44.3)):
            out.append(fila("grupos_y_galan_2026", q, "gobierno e instituciones", "A", "persistencia (EPC 2025)", 45.0, real))
    # 5. PERSONAS_POLITICA: 10 preguntas de la EPC 2025 escondidas a los agentes (problema B)
    if (pp := _leer(P / "personas_politica" / "resultado.json")):
        for brazo, m in pp["medidas"].items():
            for q in m.get("por_pregunta", []):
                out.append(fila("personas_politica", q["variable"], "gobierno e instituciones", "B (escondida)",
                                f"agentes (perfil {brazo})", q["brazo"], q["real"]))
        for q in pp["medidas"]["A"].get("por_pregunta", []):
            out.append(fila("personas_politica", q["variable"], "gobierno e instituciones", "B (escondida)",
                            "estimación de la página", q["pagina"], q["real"]))
    # 6. VALIDACION_2026 y AGENTES_2026: metro y Galán, públicas (problema B)
    reales_v = {}
    if (v := _leer(P / "validacion_2026" / "resultado.json")):
        for q in v["preguntas"]:
            reales_v[q["id"]] = q["real"]
            dom = "gobierno e instituciones" if "Galán" in q["pregunta"] else "movilidad"
            out.append(fila("validacion_2026", q["id"], dom, "B", "estimación de la página", q.get("porcentaje"), q["real"]))
    if (ag := _leer(P / "agentes_2026" / "resultado.json")):
        for brazo, d in ag["publicas"].items():
            for i, x in d.items():
                if i in reales_v:
                    dom = "gobierno e instituciones" if i == "V6" else "movilidad"
                    out.append(fila("agentes_2026", i, dom, "B", f"agentes ({brazo})", x, reales_v[i]))
        for brazo, d in ag["brazos"].items():                                                          # DI-BB1
            out.append(fila("agentes_2026", "K1-K7", "política nacional", "B", f"agentes ({brazo})", None, None, cnc=True,
                            n=7, agregado=True, error=d["error_cnc"]))
    # 7. VALIDACION_CNC_2026: la página en 7 preguntas del CNC (problema B)
    if (k := _leer(P / "validacion_cnc_2026" / "resultado.json")):
        for q in k["preguntas"]:
            out.append(fila("validacion_cnc_2026", q["id"], "política nacional", "B", "estimación de la página",
                            q.get("porcentaje"), q.get("real"), cnc=True))
    # 8. VALIDACION_AGENTES_D22: 9 preguntas del CNC nunca usadas (problema B)
    if (d := _leer(P / "validacion_agentes_d22" / "resultado.json")) and (r := _leer(P / "validacion_agentes_d22" / "reales.json")):
        for i, x in d["agentes"].items():
            dom = "política nacional" if i.startswith("J") else "conducta política"
            out.append(fila("validacion_agentes_d22", i, dom, "B", "agentes", x, r[i], cnc=True))
            out.append(fila("validacion_agentes_d22", i, dom, "B", "decir 50 %", 50.0, r[i], cnc=True))
    # 9. la estimación de la página en las 139 preguntas (problema B, solo el total)
    if (e := _leer(P / "banco" / "nivel_acuerdo_validacion.json")):
        out.append(fila("nivel_acuerdo_validacion", f"{e['n']} preguntas", "varios", "B", "estimación de la página", None, None,
                        n=e["n"], agregado=True, error=e["eam"]))
    # 10. el voto (DI-BB2)
    if (vc := _leer(P / "voto_campana" / "resultado.json")):
        for k, met in (("A", "agentes solos"), ("C1", "agentes + resumen de campaña"), ("C2", "agentes + resumen + encuesta")):
            out.append(fila("voto_campana", "1.ª vuelta 2026", "intención de voto", "voto", met, None, None, n=11,
                            agregado=True, error=vc["brazos"][k]["eam"]))
        out.append(fila("voto_campana", "1.ª vuelta 2026", "intención de voto", "voto", "copiar la encuesta", None, None, n=11,
                        agregado=True, error=vc["copiar_encuesta"]["eam"]))
    if (nd := _leer(P / "no_diluir" / "resultado.json")):
        real = nd["referencias_2v"]["real"]
        for k, met in (("S", "agentes + encuesta nacional"), ("Si", "agentes + instrucción"), ("Sk", "agentes calibrados")):
            out.append(fila("no_diluir", "2.ª vuelta 2026", "intención de voto", "voto", met, nd["parte2"][k]["cepeda"], real))
        out.append(fila("no_diluir", "2.ª vuelta 2026", "intención de voto", "voto", "copiar la encuesta nacional",
                        nd["referencias_2v"]["copiar_encuesta"], real))
        out.append(fila("no_diluir", "2.ª vuelta 2026", "intención de voto", "voto", "decir 50 %", 50.0, real))
    return out


def resumen(t: pd.DataFrame) -> pd.DataFrame:
    """Error medio por problema, dominio y método, sin las ya vistas; las filas agregadas pesan por su número de preguntas."""
    u = t[~t.vista & t.error.notna()].copy()
    u["peso_error"] = u.error * u.n
    g = u.groupby(["problema", "dominio", "metodo"]).agg(preguntas=("n", "sum"), suma=("peso_error", "sum"),
                                                         sesgo=("sesgo", "mean"), fuentes=("fuente", lambda s: ", ".join(sorted(set(s)))))
    g["error_medio"] = (g.suma / g.preguntas).round(1)
    g["sesgo"] = g.sesgo.round(1)
    return g.drop(columns="suma").reset_index().sort_values(["problema", "dominio", "error_medio"])


def main() -> int:
    t = pd.DataFrame(filas())
    SALIDA.mkdir(parents=True, exist_ok=True)
    t.to_csv(SALIDA / "predicciones.csv", index=False, encoding="utf-8")                              # DI-BB3: no se sube
    r = resumen(t)
    r.to_csv(SALIDA / "resumen.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 220)
    print(f"{len(t)} filas, {t.fuente.nunique()} pruebas\n")
    print(r[["problema", "dominio", "metodo", "preguntas", "error_medio", "sesgo"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
