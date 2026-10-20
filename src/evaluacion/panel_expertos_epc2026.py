"""
Prueba hacia adelante con la EPC 2026, tercer método (`docs/PANEL_EXPERTOS_EPC2026_SPECIFICATION.md`): un panel de 5 expertos
sintéticos que lee las cifras públicas y da el porcentaje de cada pregunta. Se congela junto a G y P en `config/prospectiva_epc2026/`.

Uso:
    python src/evaluacion/panel_expertos_epc2026.py --simulado    # sin gasto: prueba el circuito
    python src/evaluacion/panel_expertos_epc2026.py               # congela (tope USD 1)

DECISIONES DE IMPLEMENTACIÓN
============================

DI-PE1. **Los datos** son solo cifras verificadas y publicadas antes del corte (20/10/2026): la serie de la EPC de la pregunta
    (`serie_epc_bcv.csv` para alcalde y Concejo, 2014-2025; `persistencia_epc.cifras` para las demás) y, para el alcalde, el
    registro de mediciones públicas (`config/mediciones_publicadas.csv`) con su ficha, sin las filas de la EPC que ya van en la serie.
    Sin DANE ni cifras del CNC (decisión de Daniel, 20/10).
DI-PE2. **Una llamada por experto y por pregunta:** 35. Mismo modelo, temperatura y razonamiento que los agentes.
DI-PE3. **La cifra del panel** es la media de los 3 del medio (sin el máximo ni el mínimo) si responden los 5; con 3 o 4, la
    mediana; con menos de 3, no hay cifra.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402
from src.evaluacion import prospectiva_epc2026 as pr      # noqa: E402

TOPE_USD = 1.0
CORTE = "2026-10-20"
ARCHIVO = pr.CONGELADO / "panel_expertos.csv"
#: Los roles de la propuesta, sin las afirmaciones que los datos desmienten (§3 del pre-registro)
EXPERTOS = {
    "tendencias": ("Eres un analista de tendencias, un estadístico. Das mucho peso a la inercia y a la pendiente de la serie "
                   "histórica de la encuesta, y poco peso a lo coyuntural."),
    "sociologo": ("Eres un sociólogo urbano. Evalúas el clima de opinión por las condiciones de vida en Bogotá: empleo, costo de "
                  "vida, seguridad y movilidad."),
    "politologo": ("Eres un politólogo de coyuntura. Mides el desgaste del capital político del gobierno. Te fijas en las "
                   "encuestas de prensa recientes para captar el momento, y en cómo la opinión sobre el alcalde arrastra a otros "
                   "indicadores."),
    "instituciones": ("Eres un experto en las instituciones de Bogotá. Sabes que el Concejo, la transparencia, la participación y "
                      "la respuesta a la ciudadanía tienen poca saliencia en la vida diaria del ciudadano."),
    "comportamental": ("Eres un economista comportamental. Modelas sesgos cognitivos de la opinión, como el sesgo de negatividad y "
                       "la asimetría entre buenas y malas noticias."),
}
INSTRUCCION = (
    "\n\nTu tarea: estimar el porcentaje que publicará la Encuesta de Percepción Ciudadana 2026 de Bogotá Cómo Vamos (presencial "
    "en hogares, muestra probabilística de adultos de Bogotá, campo hacia el final de 2026) para una pregunta. Usa los datos que "
    "te doy y tu criterio de experto. Hoy es 20 de octubre de 2026 y esa encuesta no se ha publicado.\n"
    'Responde SOLO con un JSON, sin texto alrededor: {"porcentaje": <número entre 0 y 100>}.')
GOBIERNO = {"Petro": "Gustavo Petro", "Peñalosa": "Enrique Peñalosa", "López": "Claudia López", "Galán": "Carlos Fernando Galán"}


def series_epc() -> dict[str, list[tuple[int, float]]]:
    """DI-PE1: la serie de cada pregunta, en el porcentaje que se cuenta."""
    from src.evaluacion import persistencia_epc as pe
    s = pd.read_csv(RAIZ / "data" / "processed" / "serie_epc_bcv.csv")
    out = {v: [(int(r.anio), 100 * (r.p4 + r.p5)) for r in s[s.item == it].sort_values("anio").itertuples()]
           for v, it in (("GG3_GALAN", "gestion_alcalde"), ("CC5A_GALAN", "gestion_concejo"))}
    por_anio = {a: pe.cifras(a) for a in (2022, 2023, 2024, 2025)}
    for v in pr.VARIABLES:
        if v not in out:
            out[v] = [(a, c[v]) for a, c in por_anio.items() if v in c]
    return out


def prensa() -> list[str]:
    """DI-PE1: las mediciones públicas del alcalde publicadas antes del corte, sin la EPC."""
    t = pd.read_csv(RAIZ / "config" / "mediciones_publicadas.csv", dtype=str)
    t = t[~t.serie.str.startswith("epc_gestion") & (t.fecha_publicacion.fillna("9999") <= CORTE)].sort_values("mes")
    out = []
    for r in t.itertuples():
        ficha = "; ".join(f"{k}: {v}" for k, v in (("población", r.poblacion), ("método", r.metodo),
                                                     ("muestra en Bogotá", r.muestra_bogota)) if v != "pendiente")
        out.append(f"- {r.encuestadora}, {r.mes}: {r.lo_que_se_cuenta} {float(r.valor):.1f} %"
                   + (f" ({ficha})" if ficha else "") + f". Comparabilidad: {r.comparabilidad}.")
    return out


def datos(var: str, ficha: dict, serie: list[tuple[int, float]], prensa_: list[str]) -> str:
    from src.consulta import motor as mo
    from src.evaluacion import intervalos_fase1 as iv
    from src.evaluacion import selector_fase_b as sb
    texto = sb.preguntas([var], {var: ficha})[0]["pregunta"]
    lineas = [f"PREGUNTA: «{texto}»",
              "Opciones: " + "; ".join(mo.escala_visible(ficha)) + f". Se cuenta: «{mo.lado(ficha)[1]}».", "",
              "SERIE DE LA ENCUESTA DE PERCEPCIÓN CIUDADANA (Bogotá, presencial en hogares), porcentaje que se cuenta:"]
    for a, x in serie:
        quien = f" (alcalde/sa: {GOBIERNO[iv.gobierno(a)]})" if var in ("GG3_GALAN", "CC5A_GALAN") else ""
        lineas.append(f"- {a}: {x:.1f} %{quien}")
    if var == "GG3_GALAN" and prensa_:
        lineas += ["", "OTRAS MEDICIONES PÚBLICAS DEL ALCALDE (otro concepto, escala, población o método; no son la misma serie):"] + prensa_
    return "\n".join(lineas)


def combinar(xs: list[Optional[float]]) -> Optional[float]:
    """DI-PE3."""
    v = sorted(x for x in xs if x is not None)
    if len(v) == 5:
        return float(np.mean(v[1:4]))
    return float(np.median(v)) if len(v) >= 3 else None


def leer(texto: str) -> Optional[float]:
    d = e9._json_de(texto) or {}
    try:
        x = float(d.get("porcentaje"))
    except (TypeError, ValueError):
        return None
    return x if 0 <= x <= 100 else None


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args(argv)
    from src.consulta import agentes as ag
    from src.consulta import reformular as rf
    destino = (pr.CACHE.parent / "simulado" / "prospectiva_epc2026") if a.simulado else pr.CONGELADO
    if not a.simulado and (destino / ARCHIVO.name).exists():
        raise SystemExit("El panel ya está congelado: no se vuelve a correr.")
    destino.mkdir(parents=True, exist_ok=True)
    cache = e9.Cache(pr.CACHE.with_name(("simulado_" if a.simulado else "") + "cache_panel_expertos.json"))
    if a.simulado:
        rng = np.random.default_rng(0)
        llamar, modelo = (lambda m, s, u, t: json.dumps({"porcentaje": float(rng.uniform(5, 60))})), e9.MODELO_SIMULADO
    else:
        llamar, modelo = e9.cliente_real(timeout=300, extra={"reasoning": {"effort": "low"}}), ag.MODELO
    cat = rf.cargar_catalogo(rf.CATALOGO_2025)
    ser, pre = series_epc(), prensa()
    filas, bloques = [], {}
    for v in pr.VARIABLES:
        bloques[v] = datos(v, cat[v], ser[v], pre)
        xs = {}
        for nombre, rol in EXPERTOS.items():
            if not a.simulado and e9.gasto_registrado(cache)["costo_usd"] >= TOPE_USD:
                raise RuntimeError(f"Se llegó al tope de USD {TOPE_USD}.")
            texto, _ = e9.pedir(llamar, cache, modelo, ag.TEMPERATURA, rol + INSTRUCCION, bloques[v], 0)
            xs[nombre] = leer(texto)
        filas.append({"variable": v, **{f"x_{k}": x for k, x in xs.items()}, "E": combinar(list(xs.values()))})
    t = pd.DataFrame(filas).round(2)
    gasto = None if a.simulado else e9.gasto_registrado(cache)["costo_usd"]
    meta = {"fecha": time.strftime("%Y-%m-%d %H:%M"), "modelo": modelo, "temperatura": ag.TEMPERATURA, "razonamiento": "low",
            "expertos": {k: v + INSTRUCCION for k, v in EXPERTOS.items()}, "datos": bloques, "agregacion": DI_PE3,
            "gasto_usd": gasto}
    t.to_csv(destino / ARCHIVO.name, index=False, encoding="utf-8")
    (destino / "panel_expertos.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(t.to_string(index=False))
    print(f"gasto USD {gasto}")
    return 0


DI_PE3 = "media de los 3 del medio con 5 respuestas; mediana con 3 o 4; sin cifra con menos de 3"

if __name__ == "__main__":
    sys.exit(main())
