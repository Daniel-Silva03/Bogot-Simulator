"""
src/viz/preparar_voto.py

Paquete de la capa de Voto del tablero: la primera vuelta presidencial de 2014,
2018 y 2022 por localidad, y lo que el estrato no explica de ese voto.

    data/external/electoral/presidente_1v_*        (D16, DATA_INVENTORY §14.4)
    data/processed/geografia_electoral/resultado.json   (GEOGRAFIA_ELECTORAL_RESULTS)
        -> data/processed/viz/voto_bogota.json

Uso:
    python src/viz/preparar_voto.py
    python src/viz/construir_pagina.py

DECISIONES DE IMPLEMENTACIÓN (continúan la numeración de VISUALIZATION_SPECIFICATION)
==================================================================================

DI-V53. **El voto es una capa que sí puede afirmar geografía**, como Crecimiento
    (DI-V51) y por la misma razón: es un conteo completo, sin error de muestreo
    que descontar. Pero trae dos salvedades propias, y el paquete las lleva como
    datos para que el aviso las diga con cifras y no con texto fijo: la zona de
    votación es dónde se está inscrito, no dónde se vive (razón inscritos /
    adultos), y el puesto censo de Corferias concentra votos que no tienen
    localidad.

DI-V54. **Las proporciones son sobre votos por candidato** (DI-EL5), las mismas
    que usa el análisis, y **el dominio de color es uno solo** para las nueve
    combinaciones de elección y candidato: de 0 al máximo observado en cualquier
    localidad. Reescalar por candidato haría que un candidato con 3 pp de
    diferencia entre localidades se viera tan partido como uno con 12 pp (DI-V49
    otra vez).

DI-V55. **Los residuos salen del resultado pre-registrado sin recalcularse**
    (M1, estrato medio). La versión que controla por participación **no estaba
    pre-registrada** (`GEOGRAFIA_ELECTORAL_RESULTS.md` §5): se calcula aquí con las
    mismas funciones del análisis, se marca como exploratoria en el paquete y en
    la página, y nunca es la vista por defecto.

DI-V56. **Sumapaz tiene voto, pero no residuo.** Quedó fuera del ajuste
    (§3.3 del pre-registro): en la vista de residuos se pinta como «sin dato» y la
    ficha dice por qué, en vez de extrapolarle una cifra.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import geografia_electoral as ge   # noqa: E402
from src.population.electoral import OPCIONES           # noqa: E402

ELECTORAL = RAIZ / "data" / "external" / "electoral"
RESULTADO = RAIZ / "data" / "processed" / "geografia_electoral" / "resultado.json"
SALIDA = RAIZ / "data" / "processed" / "viz" / "voto_bogota.json"

NOMBRE_PUBLICO = {(a, c): pub for a, op in OPCIONES.items() for c, pub, _, _ in op.values()}


def _pp(v) -> float | None:
    return None if v is None or (isinstance(v, float) and np.isnan(v)) else round(float(v), 4)


def residuos_con_participacion(prop: pd.DataFrame, comp: pd.DataFrame,
                               participacion: pd.Series) -> dict[str, dict[int, float]]:
    """DI-V55 — exploratorio: residuos de M1 + participación 2018, con las funciones del análisis."""
    locs = sorted(set(prop.index) & set(comp.index) - {ge.SUMAPAZ})
    X = np.column_stack([comp.loc[locs, "x1"], participacion.loc[locs]])
    return {f"{a}_{c}": dict(zip(locs, ge.residuos(prop.loc[locs, (a, c)].to_numpy(), X)))
            for a, c in ge.RESULTADOS}


def construir() -> dict:
    votos = pd.read_csv(ELECTORAL / "presidente_1v_localidad.csv")
    zonas = pd.read_csv(ELECTORAL / "presidente_1v_zonas.csv")
    pot = pd.read_csv(ELECTORAL / "presidente_1v_potencial_2018.csv")
    res = json.loads(RESULTADO.read_text(encoding="utf-8"))
    marg = pd.read_csv(ge.MARGINAL).set_index("COD_LOC")

    prop = ge.proporciones(votos, zonas)
    logging.disable(logging.WARNING)
    comp = ge.composicion()
    logging.disable(logging.NOTSET)

    z18 = zonas[(zonas.anio == 2018) & zonas.cod_loc.notna()].merge(pot[["zona", "potencial"]], on="zona")
    participacion = pd.Series((z18.votos_total / z18.potencial).to_numpy(), index=z18.cod_loc.astype(int))
    inscripcion = (pot.dropna(subset=["cod_loc"]).set_index(pot.dropna(subset=["cod_loc"]).cod_loc.astype(int))
                   .potencial / marg.poblacion)
    res_part = residuos_con_participacion(prop, comp, participacion)

    claves = [f"{a}_{c}" for a, c in ge.RESULTADOS]
    localidades = {}
    for cod in range(1, 21):
        l = {"votos": {}, "residuo": {}, "residuo_participacion": {}}
        for (a, c), k in zip(ge.RESULTADOS, claves):
            l["votos"][k] = _pp(prop.loc[cod, (a, c)]) if cod in prop.index else None
            r = res["resultados"][k]["residuos"].get(str(cod))
            l["residuo"][k] = _pp(r)                                   # DI-V56: Sumapaz -> None
            l["residuo_participacion"][k] = _pp(res_part[k].get(cod))
        l["estrato_medio"] = _pp(comp.loc[cod, "x1"])
        l["inscritos_sobre_adultos"] = _pp(inscripcion.get(cod))
        l["participacion_2018"] = _pp(participacion.get(cod))
        localidades[f"{cod:02d}"] = l

    # Votos que no tienen localidad (zonas 90 y 98), por año: DI-V53.
    especiales = zonas[zonas.cod_loc.isna()].groupby("anio").votos_total.sum()
    totales = zonas.groupby("anio").votos_total.sum()
    fuera = {str(a): {"votos": int(especiales.get(a, 0)),
                      "fraccion": round(float(especiales.get(a, 0) / totales[a]), 4)} for a in totales.index}

    todas = [v for l in localidades.values() for v in l["votos"].values() if v is not None]
    resid = [abs(v) for l in localidades.values() for v in l["residuo"].values() if v is not None]
    resid_p = [abs(v) for l in localidades.values() for v in l["residuo_participacion"].values() if v is not None]
    ciudad = votos[votos.tipo == "candidato"].groupby(["anio", "clave"]).votos.sum()
    base = zonas.groupby("anio").votos_candidatos.sum()

    return {
        "version": "0.1",
        "fuente": ("Registraduría Nacional, primera vuelta presidencial, mesa a mesa, entregada por el CNC "
                   "(D16). Agregada por localidad en src/population/electoral.py."),
        "elecciones": sorted({a for a, _ in ge.RESULTADOS}),
        "candidatos": [{"clave": k, "anio": a, "id": c, "nombre": NOMBRE_PUBLICO[(a, c)],
                        "bogota": round(float(ciudad[(a, c)] / base[a]), 4)}
                       for (a, c), k in zip(ge.RESULTADOS, claves)],
        "por_defecto": f"{ge.PRINCIPAL[0]}_{ge.PRINCIPAL[1]}",
        "dominio_voto": round(max(todas), 4),                              # DI-V54
        "dominio_residuo": round(max(resid), 4),
        "dominio_residuo_participacion": round(max(resid_p), 4),
        "votos_sin_localidad": fuera,
        "analisis": {                                                      # lo que el aviso cita
            "r2_loo_principal": res["resultados"][f"{ge.PRINCIPAL[0]}_{ge.PRINCIPAL[1]}"]["r2_loo_m1"],
            "persistencia_r": res["persistencia"]["r"],
            "persistencia_entre": res["persistencia"]["entre"],
            "inscripcion_r": res["inscripcion_r"],
            "regla": res["regla"],
            "r2_loo": {k: v["r2_loo_m1"] for k, v in res["resultados"].items()},
            "documento": "docs/GEOGRAFIA_ELECTORAL_RESULTS.md",
        },
        "participacion_exploratoria": True,                                # DI-V55
        "localidades": localidades,
    }


def main() -> None:
    datos = construir()
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{SALIDA.relative_to(RAIZ).as_posix()}  {SALIDA.stat().st_size / 1024:.1f} KB")
    print(f"  {len(datos['candidatos'])} combinaciones, dominio de voto 0–{datos['dominio_voto']:.2f}, "
          f"residuo ±{datos['dominio_residuo']:.3f}")


if __name__ == "__main__":
    main()
