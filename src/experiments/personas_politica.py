"""
Personas con su encuesta, en lo político (`docs/PERSONAS_POLITICA_SPECIFICATION.md`): el agente con probabilidades, con cuatro
perfiles (opiniones; más datos reales de su vida; más un resumen de la IA; más una vida inventada por la IA), en 10 preguntas
de gobierno y del alcalde, con 200 personas nuevas de la EPC 2025.

Uso:
    python src/experiments/personas_politica.py --simulado
    python src/experiments/personas_politica.py

DECISIONES DE IMPLEMENTACIÓN
============================

DI-PQ1. **Las preguntas escondidas del catálogo** usan su texto, la escala de la página (`motor.vista`, sin «no sabe») y su
    lado favorable (`motor.lado`); en las categorías que ve el agente, los códigos de «no sabe» de la ficha van como
    «No sabe». La columna es la de 2025 (`verificacion_2025.csv`).
DI-PQ2. **Los datos de su vida** se leen con las opciones del formulario (`verificar_epc2025.opciones_por_linea`), sin las
    instrucciones entre corchetes. `CUL_3` es un número; `CTI_2_1` a `CTI_2_3` son hasta tres usos de la IA. Un dato vacío
    no se escribe.
DI-PQ3. **La página sin su propia pregunta:** en P1 a P7, `Motor.estimar` corre con las candidatas sin `CAT_<código>`.
DI-PQ4. **Fuera de los datos de su vida, antes de correr:** el medio de transporte (`MOV_2`) y si el vehículo es eléctrico
    (`MOV_3`), porque los códigos de Bogotá no siguen la numeración del formulario (el código 1, «Metro», lo tienen 596
    personas, y el 10 no tiene etiqueta); y si conoce Bogotá Cómo Vamos (`GCV_1`), porque ya está en el catálogo. Las
    opciones de `CTI_2` van a mano: el PDF no deja leerlas con `opciones_por_linea`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import personas_con_encuesta as pc   # noqa: E402
from src.experiments import personas_pulidas as pp        # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "personas_politica"
SEMILLA = 20261016
TOPE_USD = 2.0
#: §2: (clave, columna de 2025, variable del catálogo o None si es del lote 8)
ESCONDIDAS = (("P1", "GOB_5", "GG3_GALAN"), ("P2", "GOB_6", "CC5A_GALAN"), ("P3", "GOB_8", "MICE1_GALAN"),
              ("P4", "GOB_10", "MICE2_GALAN"), ("P5", "GOB_9", "MICE3_GALAN"), ("P6", "GOB_1", "AG1"),
              ("P7", "CON_1", "GG7"), ("P8", "GOB_4", None), ("P9", "CON_4", None), ("P10", "CON_7", None))
VIDA = ("EDU_3", "HOG_4", "FIN_1", "CUL_3", "SEG_5", "CTI_2_1", "CTI_2_2", "CTI_2_3")
#: DI-PQ4: el PDF no deja leer las opciones de CTI_2; van a mano, con el texto del formulario
CTI_2 = {90: "No ha usado ninguna herramienta de inteligencia artificial el último mes", 1: "Redacción de textos",
         2: "Traducción de textos", 3: "Búsqueda de bibliografía", 4: "Generación o edición de fotos o videos",
         5: "Generación de ideas para su trabajo o estudio", 6: "Procesamiento de datos", 7: "Desarrollo de software",
         8: "Recomendaciones de salud", 9: "Consejos sentimentales o de relaciones sociales", 10: "Orientación en salud mental",
         11: "No conoce las herramientas"}
VARIANTES = ("A", "B", "C", "D")
SISTEMA = pp.BASE + pp.SALIDA_PROB
RESUMEN = ("Resume en 3 o 4 frases quién es esta persona según sus respuestas: qué piensa y cómo vive. No inventes nada que no "
           "esté en ellas. Responde solo con el resumen.")
INVENTA = ("Escribe una biografía breve (4 o 5 frases) de esta persona: su trabajo, su familia, su barrio y su día a día, "
           "coherente con sus respuestas. Puedes inventar los detalles. Responde solo con la biografía.")


def _limpia(s: str) -> str:
    return " ".join(re.split(r"\[", str(s))[0].split()).rstrip(" .:")


def escondidas() -> list[dict]:
    """§2 y DI-PQ1."""
    from src.consulta import motor as mo
    from src.population import poblacion_epc_olas as po
    cat = {f["variable"]: f for f in json.loads((po.SALIDA_2025 / "catalogo.json").read_text(encoding="utf-8"))["dentro"]}
    lote8 = {e["variable"]: e for e in pp.preguntas(tuple(c for _, c, v in ESCONDIDAS if v is None))}
    out = []
    for k, col, var in ESCONDIDAS:
        if var is None:
            e = dict(lote8[col]); e.update(clave=k, catalogo=None)
        else:
            f = mo.vista(cat[var])
            validos = list(f["escala"])
            cats = {int(c): (str(t).strip() if int(c) in validos else "No sabe") for c, t in cat[var]["etiquetas"].items()}
            e = {"clave": k, "variable": col, "catalogo": var, "pregunta": f["pregunta"].strip(), "categorias": cats,
                 "validos": validos, "fav": [int(c) for c in mo.lado(f)[0]]}
        out.append(e)
    return out


def opciones_vida() -> dict[str, dict[int, str]]:
    """DI-PQ2: las opciones del formulario de los datos de su vida."""
    from src.population import verificar_epc2025 as v
    bl = v.bloques(v.texto_formulario())
    out = {c: {k: _limpia(t) for k, t in v.opciones_por_linea(bl[c]).items()} for c in VIDA if c in bl}
    out["CTI_2"] = CTI_2                                                          # DI-PQ4
    return out


TEXTO_VIDA = {"EDU_3": "Estudiantes del hogar", "HOG_4": "Horas al día de cuidado de otros",
              "FIN_1": "De dónde sacó un préstamo el último año", "SEG_5": "Denunció el delito del que fue víctima"}


def vida_texto(fila: pd.Series, ops: dict) -> list[str]:
    """DI-PQ2."""
    out = []
    for c, nombre in TEXTO_VIDA.items():
        x = pd.to_numeric(fila.get(c), errors="coerce")
        if pd.notna(x) and int(x) in ops.get(c, {}):
            out.append(f"- {nombre}: {ops[c][int(x)]}")
    libros = pd.to_numeric(fila.get("CUL_3"), errors="coerce")
    if pd.notna(libros):
        out.append(f"- Libros leídos en el último año: {int(libros)}")
    usos = [ops["CTI_2"][int(x)] for c in ("CTI_2_1", "CTI_2_2", "CTI_2_3")
            for x in [pd.to_numeric(fila.get(c), errors="coerce")] if pd.notna(x) and int(x) in ops["CTI_2"]]
    if usos:
        out.append(f"- Para qué usa la inteligencia artificial: {'; '.join(dict.fromkeys(usos))}")
    return out


def perfil(i: int, datos, esc: list[dict], ops: dict, con_vida: bool) -> str:
    base, d, perf = datos
    ocultas = {e["variable"] for e in esc}
    resp = [(p, pc.etiqueta(f, d[c].iloc[i])) for p, c, f in perf if c not in ocultas]
    num = lambda c: pd.to_numeric(d[c].iloc[i], errors="coerce")                   # noqa: E731
    dm = {"sexo": {1: "hombre", 2: "mujer"}.get(num("DMO_1"), "sin dato"), "edad": int(num("DMO_3_1")),
          "estrato": int(num("DMO_4_1")), "localidad": pc.LOCALIDADES.get(int(base.cod_loc.iloc[i]), "sin dato")}
    t = pc.perfil_texto(dm, resp)
    if con_vida:
        v = vida_texto(d.iloc[i], ops)
        if v:
            t += "\n\nSobre su vida:\n" + "\n".join(v)
    return t


def preguntas_texto(esc: list[dict]) -> str:
    return "\n".join(f'{e["clave"]}. {e["pregunta"]} Opciones: ' + "; ".join(f"{c}={t}" for c, t in e["categorias"].items())
                     for e in esc)


def pagina_sin_si_misma(esc: list[dict], simulado: bool) -> dict[str, float]:
    """DI-PQ3."""
    if simulado:
        return {e["variable"]: 40.0 for e in esc}
    from src.consulta import motor as mo
    ruta = SALIDA / "pagina.json"
    previas = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}
    falta = [e for e in esc if e["variable"] not in previas]
    if falta:
        llamar, modelo = mo.cliente(simulado=False)
        m = mo.Motor(llamar, modelo, cache=e9.Cache(SALIDA / "cache_pagina.json"))
        todas = m._candidatas
        for e in falta:
            m._candidatas = todas[todas.id != f"CAT_{e['catalogo']}"] if e["catalogo"] else todas
            etq = pp.GOB4_CINCO if e["variable"] == "GOB_4" else [e["categorias"][c] for c in e["validos"]]
            if len(etq) != 5:
                etq = (etq + etq[-1:] * 5)[:5] if len(etq) < 5 else etq[:5]
            r = m.estimar(e["pregunta"], etq)
            previas[e["variable"]] = r["porcentaje"] if r else 50.0
        SALIDA.mkdir(parents=True, exist_ok=True)
        ruta.write_text(json.dumps(previas, ensure_ascii=False, indent=1), encoding="utf-8")
    return {e["variable"]: previas[e["variable"]] for e in esc}


def correr(variante: str, personas: np.ndarray, esc: list[dict], datos, ops: dict, llamar, cache) -> dict:
    out = {e["clave"]: {"valor": np.full(len(personas), np.nan), "pfav": np.full(len(personas), np.nan),
                        "dist": [None] * len(personas)} for e in esc}
    for j, i in enumerate(personas):
        if e9.gasto_registrado(cache)["costo_usd"] >= TOPE_USD:
            raise RuntimeError(f"Se llegó al tope de USD {TOPE_USD}.")
        t = perfil(i, datos, esc, ops, con_vida=variante in ("B", "C"))
        if variante == "C":
            r, _ = e9.pedir(llamar, cache, pc.MODELO, 0.0, RESUMEN, t, 0)
            t += "\n\nResumen de quién es:\n" + r.strip()
        if variante == "D":
            r, _ = e9.pedir(llamar, cache, pc.MODELO, pc.TEMPERATURA, INVENTA, t, 0)
            t += "\n\nSu vida:\n" + r.strip()
        u = f"QUIÉN ES:\n{t}\n\nPREGUNTAS NUEVAS:\n{preguntas_texto(esc)}"
        texto, _ = e9.pedir(llamar, cache, pc.MODELO, pc.TEMPERATURA, SISTEMA, u, 0)
        probs = pp.leer_prob(texto, esc)
        for e in esc:
            q = probs[e["clave"]]
            if q:
                o = out[e["clave"]]
                o["valor"][j] = sum(c * x for c, x in q.items())
                o["pfav"][j] = sum(q.get(c, 0) for c in e["fav"])
                o["dist"][j] = q
        if (j + 1) % 50 == 0:
            print(f"   {variante}: {j + 1} de {len(personas)}; gasto USD {e9.gasto_registrado(cache)['costo_usd']:.3f}", flush=True)
    return out


def mejora(m1: dict, m0: dict) -> bool:
    """§5: al menos 1 punto menos de error del total, sin más error individual."""
    return m1["error_total"] <= m0["error_total"] - 1.0 and m1["error_individual"] <= m0["error_individual"]


def cliente(simulado: bool):
    if simulado:
        rng = np.random.default_rng(0)

        def llamar(m, s, u, t):
            if "PREGUNTAS NUEVAS" not in u:
                return "Una persona de Bogotá."
            claves = [l.split(".")[0] for l in u.split("PREGUNTAS NUEVAS:\n")[1].split("\n")]
            return json.dumps({k: {str(c): float(x) for c, x in zip(range(1, 6), rng.dirichlet(np.ones(5)))} for k in claves})
        return llamar, e9.Cache(SALIDA / "simulado" / "cache.json")
    return e9.cliente_real(timeout=300, extra={"reasoning": {"effort": "low"}}), e9.Cache(SALIDA / "cache.json")


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args(argv)
    datos = pc.datos_2025()
    base = datos[0]
    elegibles = np.flatnonzero(base.cod_loc.between(1, 19).to_numpy())
    dev = np.random.default_rng(pc.SEMILLA).choice(elegibles, pc.N, replace=False)
    final = np.random.default_rng(pp.SEMILLA_FINAL).choice(np.setdiff1d(elegibles, np.sort(dev)), pc.N, replace=False)
    libres = np.setdiff1d(elegibles, np.concatenate([dev, final]))
    personas = np.sort(np.random.default_rng(SEMILLA).choice(libres, pc.N, replace=False))
    esc = escondidas()
    ops = opciones_vida()
    pagina = pagina_sin_si_misma(esc, a.simulado)
    llamar, cache = cliente(a.simulado)
    med = {}
    for v in VARIANTES:
        med[v] = pp.medir(correr(v, personas, esc, datos, ops, llamar, cache), personas, esc, datos, pagina)
        m = med[v]
        print(f"{v}: individual {m['error_individual']} (constante {m['error_constante']}) | total {m['error_total']} "
              f"(página {m['error_pagina']}) | TVD {m['tvd']} | sin respuesta {m['sin_respuesta']}", flush=True)
    hip = {"H1": mejora(med["B"], med["A"]), "H2": mejora(med["C"], med["B"]), "H3": not mejora(med["D"], med["A"])}
    mejor = min(VARIANTES, key=lambda v: med[v]["error_total"])
    mm = med[mejor]
    util = {"individual": mm["error_individual"] < mm["error_constante"], "total": mm["error_total"] < mm["error_pagina"],
            "tvd": mm["tvd"] <= 0.15}
    util["util"] = all(util.values())
    pred = {"PQ1": hip["H1"], "PQ2": not hip["H2"], "PQ3": hip["H3"] and med["D"]["error_total"] > med["A"]["error_total"],
            "PQ4": util["util"]}
    g = None if a.simulado else e9.gasto_registrado(cache)["costo_usd"]
    print(f"hipótesis: {hip} | mejor: {mejor} {util} | predicciones: {pred} | gasto USD {g}")
    sal = SALIDA / ("simulado" if a.simulado else "")
    sal.mkdir(parents=True, exist_ok=True)
    (sal / "resultado.json").write_text(json.dumps({"medidas": med, "hipotesis": hip, "mejor": mejor, "util": util,
                                                    "predicciones": pred, "gasto": g, "pagina": pagina},
                                                   ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
