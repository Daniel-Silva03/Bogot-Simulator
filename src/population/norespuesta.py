"""
src/population/norespuesta.py

¿El rebote de confianza de 2023 es opinión, o es no-respuesta?

Reproduce el análisis de `claude/ANALISIS_NORESPUESTA_2023.md`. Uso:

    python src/population/norespuesta.py [ruta_ecp]

POR QUÉ EXISTE
--------------
La no-respuesta a la batería de confianza es estable en 2017-2021
(1,8 % / 2,4 % / 1,8 % de personas sin índice válido) y salta a 4,8 % en
2023 — justo la ola donde la media rebota y la dispersión se contrae. Si
ese movimiento fuera composición y no opinión, el Experimento 4 estaría
ajustando un artefacto, porque la contracción de dispersión es lo único
que su modelo consigue reproducir.

Las cuatro pruebas, de menos a más exigente:

  (a) relajar el mínimo de ítems a 1, para usar a los parciales
  (b) peor caso: quien no contestó nada, al mínimo de la escala
  (c) SOLO CASOS COMPLETOS (13 de 13 ítems) — elimina de raíz la
      no-respuesta por ítem; es la prueba que decide
  (d) reponderar 2023 a la composición demográfica de 2021

LIMITACIÓN QUE NO SE PUEDE SALVAR DESDE AQUÍ: todo esto mide la
no-respuesta de quien aceptó la encuesta. La no-respuesta de UNIDAD —quien
nunca abrió la puerta— es invisible en el microdato, y el tamaño de
muestra sí cayó (5.137 -> 4.451). Corregirlo exigiría las tasas de
respuesta y el marco muestral de DANE.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.population.ecp import (          # noqa: E402
    INDICE_MIN_ITEMS, ITEMS_UTILES, cargar_panel,
)

TRAMOS_EDAD = ([17, 29, 44, 59, 200], ["18-29", "30-44", "45-59", "60+"])
TRAMOS_ESTRATO = ([0, 2, 3, 6], ["1-2", "3", "4-6"])
ANIO_REFERENCIA_COMPOSICION = 2021


def _wmedia(v: pd.Series, w: pd.Series) -> float:
    m = v.notna() & w.notna()
    return float(np.average(v[m], weights=w[m])) if m.any() else np.nan


def _wsd(v: pd.Series, w: pd.Series) -> float:
    m = v.notna() & w.notna()
    if not m.any():
        return np.nan
    mu = np.average(v[m], weights=w[m])
    return float(np.sqrt(np.average((v[m] - mu) ** 2, weights=w[m])))


def preparar(raiz) -> pd.DataFrame:
    """Panel con el número de ítems válidos y el índice parcial por persona.

    El índice *parcial* promedia los ítems válidos que haya, sin exigir el
    mínimo de 7: es lo que permite comparar a quien queda dentro con quien
    queda fuera, en vez de solo constatar que quedó fuera.
    """
    panel = cargar_panel(raiz)
    items = [i for i in ITEMS_UTILES if i in panel.columns]
    X = panel[items].where(panel[items].apply(lambda c: c.between(1, 5)))
    base = panel[["anio", "fex", "sexo", "edad", "estrato"]].reset_index(drop=True)
    return pd.concat([base, pd.DataFrame({
        "n_validos": X.notna().sum(axis=1).to_numpy(),
        "indice_parcial": X.mean(axis=1).to_numpy(),
    })], axis=1)


def cobertura(d: pd.DataFrame) -> pd.DataFrame:
    """Cuánta gente queda fuera del índice cada año, y con cuántos ítems."""
    filas = []
    for anio, g in d.groupby("anio"):
        n = len(g)
        filas.append({
            "anio": int(anio), "n": n,
            "con_indice": int((g.n_validos >= INDICE_MIN_ITEMS).sum()),
            "pct_excluidos": 100 * (g.n_validos < INDICE_MIN_ITEMS).mean(),
            "pct_13_de_13": 100 * (g.n_validos == 13).mean(),
            "pct_1_a_6": 100 * ((g.n_validos >= 1) & (g.n_validos < 7)).mean(),
            "pct_cero": 100 * (g.n_validos == 0).mean(),
        })
    return pd.DataFrame(filas)


def perfil_de_los_excluidos(d: pd.DataFrame) -> pd.DataFrame:
    """Índice parcial y composición de incluidos / parciales / sin respuesta."""
    est = pd.to_numeric(d.estrato, errors="coerce").where(lambda x: x.between(0, 6))
    d = d.assign(grupo=np.where(d.n_validos >= INDICE_MIN_ITEMS, "incluido",
                       np.where(d.n_validos > 0, "parcial_1_6", "cero")),
                 estrato_num=est)
    filas = []
    for (anio, grupo), g in d.groupby(["anio", "grupo"]):
        filas.append({
            "anio": int(anio), "grupo": grupo, "n": len(g),
            "indice": _wmedia(g.indice_parcial, g.fex),
            "edad": _wmedia(g.edad, g.fex),
            "estrato": _wmedia(g.estrato_num, g.fex),
            "pct_mujer": 100 * _wmedia((g.sexo == 2).astype(float), g.fex),
        })
    return pd.DataFrame(filas)


def cotas(d: pd.DataFrame) -> pd.DataFrame:
    """Media y sd por año bajo cuatro reglas de inclusión distintas."""
    filas = []
    for anio, g in d.groupby("anio"):
        con = g[g.n_validos >= INDICE_MIN_ITEMS]
        al_menos_uno = g[g.n_validos >= 1]
        cero = g[g.n_validos == 0]
        completos = g[g.n_validos == 13]

        def fila(nombre, v, w):
            return {"anio": int(anio), "regla": nombre,
                    "media": _wmedia(v, w), "sd": _wsd(v, w), "n": int(v.notna().sum())}

        filas.append(fila("publicada_min7", con.indice_parcial, con.fex))
        filas.append(fila("min1", al_menos_uno.indice_parcial, al_menos_uno.fex))
        # peor caso: los que no contestaron nada, en el mínimo de la escala
        v = pd.concat([al_menos_uno.indice_parcial, pd.Series(1.0, index=cero.index)])
        w = pd.concat([al_menos_uno.fex, cero.fex])
        filas.append(fila("peor_caso_ceros_en_1", v, w))
        filas.append(fila("solo_completos_13", completos.indice_parcial, completos.fex))
    return pd.DataFrame(filas)


def reponderar_a_composicion(d: pd.DataFrame, anio: int,
                             referencia: int = ANIO_REFERENCIA_COMPOSICION) -> dict:
    """Lleva `anio` a la composición sexo × edad × estrato de `referencia`.

    Si tras corregir la composición el fenómeno se mantiene, no es un
    efecto de que haya contestado gente distinta.
    """
    cortes_e, etiquetas_e = TRAMOS_EDAD
    cortes_s, etiquetas_s = TRAMOS_ESTRATO
    est = pd.to_numeric(d.estrato, errors="coerce").where(lambda x: x.between(1, 6))
    celda = pd.Series(list(zip(
        d.sexo.astype(str),
        pd.cut(d.edad, cortes_e, labels=etiquetas_e).astype(str),
        pd.cut(est, cortes_s, labels=etiquetas_s).astype(str),
    )), index=d.index)
    d = d.assign(celda=celda)

    ref = d[(d.anio == referencia) & (d.n_validos >= INDICE_MIN_ITEMS)]
    objetivo = ref.groupby("celda").fex.sum()
    objetivo /= objetivo.sum()

    g = d[(d.anio == anio) & (d.n_validos >= INDICE_MIN_ITEMS)]
    actual = g.groupby("celda").fex.sum()
    actual /= actual.sum()
    factor = (objetivo / actual).reindex(g.celda).to_numpy()
    w2 = pd.Series(g.fex.to_numpy() * np.where(np.isfinite(factor), factor, 1.0),
                   index=g.index)
    return {
        "anio": anio, "referencia": referencia,
        "media_original": _wmedia(g.indice_parcial, g.fex),
        "sd_original": _wsd(g.indice_parcial, g.fex),
        "media_reponderada": _wmedia(g.indice_parcial, w2),
        "sd_reponderada": _wsd(g.indice_parcial, w2),
    }


def main(argv=None) -> int:
    raiz = (argv or sys.argv[1:] or [None])[0] or (
        Path(__file__).resolve().parents[2] / "data" / "raw" / "ecp")
    d = preparar(raiz)

    print("\n== Cobertura por año ==")
    print(cobertura(d).round(2).to_string(index=False))
    print("\n== Quién queda fuera ==")
    print(perfil_de_los_excluidos(d).round(3).to_string(index=False))
    print("\n== Media y sd bajo cuatro reglas ==")
    c = cotas(d)
    print(c.round(4).to_string(index=False))

    print("\n== Rebote 2021 -> 2023 y contracción de sd, por regla ==")
    for regla, g in c.groupby("regla"):
        g = g.set_index("anio")
        if not {2021, 2023}.issubset(g.index):
            continue
        reb = g.loc[2023, "media"] - g.loc[2021, "media"]
        con = 100 * (1 - g.loc[2023, "sd"] / g.loc[2021, "sd"])
        print(f"  {regla:24s} rebote {reb:+.4f}   contracción sd {con:+.1f}%")

    print("\n== Reponderando a la composición de 2021 ==")
    for anio in (2021, 2023):
        r = reponderar_a_composicion(d, anio)
        print(f"  {anio}: media {r['media_original']:.3f} -> {r['media_reponderada']:.3f}"
              f"   sd {r['sd_original']:.3f} -> {r['sd_reponderada']:.3f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
