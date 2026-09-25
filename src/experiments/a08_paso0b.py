"""A08, paso 0b — ¿la composición demográfica exagera la diferencia entre localidades?

POR QUÉ EXISTE
--------------
El paso 0 (A08_PASO0_RESULTS.md) mostró que la composición demográfica separa
las localidades de la población sintética con una dispersión de 0,07 a 0,12
en la escala 1-5. Antes de dibujar eso con 100.000 agentes hay que saber si la
composición predice **bien** la diferencia territorial que existe, o la
exagera. Los estudios del CNC midieron diferencias reales entre localidades de
0,05 a 0,07 para otras variables (D15), del mismo orden o menores.

La ECP no trae localidad y no puede responder esto. La EPC de Bogotá Cómo
Vamos sí: tiene, **en las mismas personas**, localidad, sexo, edad (en bandas),
estrato y la opinión. Se puede comparar directamente lo que la localidad mide
con lo que la composición sola predice.

QUÉ CALCULA, POR OLA
--------------------
- `m_obs[l]`: media ponderada de la opinión en la localidad l (lo medido).
- `m_comp[l]`: lo que la composición predice para l. A cada persona de l se le
  asigna la media ponderada de su celda (sexo × banda de edad × estrato)
  **calculada con las otras 18 localidades** (dejando l fuera), y se promedia
  con los pesos de l. Dejarla fuera importa: si no, el ruido de la propia
  localidad entra en las dos cifras y las hace parecer más iguales de lo que
  son. Si una celda no tiene nadie fuera de l, se usa sexo × edad; si tampoco,
  la media de la ciudad (se cuenta cuántas veces pasa).
- Ruido por localidad de las dos cifras, con bootstrap de personas dentro de
  cada localidad (remuestreo simple: el diseño de la EPC solo se conoce en
  algunas olas, A19; el ruido queda subestimado del orden de √DEFF ≈ 1,4).
- `sd_obs`, `sd_comp`: dispersión entre localidades **corregida por ruido**:
  √(var entre medias − promedio de var de muestreo), en 0 si sale negativa.
- `R = sd_obs / sd_comp`: < 1, la composición exagera; > 1, se queda corta.
- `r`: correlación entre `m_obs` y `m_comp` (¿apunta hacia las mismas
  localidades?) y la pendiente de `m_obs` sobre `m_comp`.
- `p_territorio`: permutación de la etiqueta de localidad entre personas: ¿la
  EPC mide diferencias entre localidades más allá del azar?

La regla de decisión está pre-registrada en claude/A08_PASO0B_SPECIFICATION.md.

    python src/experiments/a08_paso0b.py                         # gestión del alcalde, todas las olas
    python src/experiments/a08_paso0b.py --item gestion_concejo

Necesita la EPC (entrega de Bogotá Cómo Vamos). Si no está en la ruta de
revisar_datos.py, exportar BSS_EPC_DIR. Salida: data/processed/a08/paso0b_<item>.json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

SALIDA_DIR = RAIZ / "data" / "processed" / "a08"


@dataclass
class Ola:
    anio: int
    loc: np.ndarray       # código de localidad (int)
    celda: np.ndarray     # clave sexo|edad|estrato
    celda_gruesa: np.ndarray  # clave sexo|edad (respaldo)
    y: np.ndarray
    w: np.ndarray


# ---------------------------------------------------------------------------
# Las cifras
# ---------------------------------------------------------------------------

def _sumas(clave: np.ndarray, y: np.ndarray, w: np.ndarray) -> tuple[pd.Series, pd.Series]:
    df = pd.DataFrame({"k": clave, "wy": w * y, "w": w})
    g = df.groupby("k")[["wy", "w"]].sum()
    return g["wy"], g["w"]


def medias_observadas(o: Ola, locs: np.ndarray) -> np.ndarray:
    return np.array([np.average(o.y[o.loc == l], weights=o.w[o.loc == l]) for l in locs])


def medias_composicion(o: Ola, locs: np.ndarray) -> tuple[np.ndarray, int]:
    """Predicción por composición, con las celdas estimadas fuera de cada localidad."""
    wy_c, w_c = _sumas(o.celda, o.y, o.w)
    wy_g, w_g = _sumas(o.celda_gruesa, o.y, o.w)
    total_wy, total_w = float((o.w * o.y).sum()), float(o.w.sum())
    out, respaldos = np.empty(len(locs)), 0
    for i, l in enumerate(locs):
        en = o.loc == l
        # sumas de la propia localidad, para restarlas
        wy_cl, w_cl = _sumas(o.celda[en], o.y[en], o.w[en])
        wy_gl, w_gl = _sumas(o.celda_gruesa[en], o.y[en], o.w[en])
        fuera_wy_c = wy_c.sub(wy_cl, fill_value=0)
        fuera_w_c = w_c.sub(w_cl, fill_value=0)
        fuera_wy_g = wy_g.sub(wy_gl, fill_value=0)
        fuera_w_g = w_g.sub(w_gl, fill_value=0)
        media_ciudad_fuera = (total_wy - float((o.w[en] * o.y[en]).sum())) / (total_w - float(o.w[en].sum()))

        c, cg = o.celda[en], o.celda_gruesa[en]
        num_c = fuera_wy_c.reindex(c).to_numpy()
        den_c = fuera_w_c.reindex(c).to_numpy()
        pred = np.where(den_c > 0, num_c / np.where(den_c > 0, den_c, 1), np.nan)
        falta = ~np.isfinite(pred)
        if falta.any():
            num_g = fuera_wy_g.reindex(cg[falta]).to_numpy()
            den_g = fuera_w_g.reindex(cg[falta]).to_numpy()
            pred[falta] = np.where(den_g > 0, num_g / np.where(den_g > 0, den_g, 1), media_ciudad_fuera)
            respaldos += int(falta.sum())
        out[i] = np.average(pred, weights=o.w[en])
    return out, respaldos


def _var_corregida(medias: np.ndarray, var_ruido: np.ndarray) -> float:
    return float(np.var(medias, ddof=1) - np.mean(var_ruido))


def analizar_ola(o: Ola, n_boot: int, n_perm: int, rng) -> dict:
    locs = np.array(sorted(np.unique(o.loc)))
    m_obs = medias_observadas(o, locs)
    m_comp, respaldos = medias_composicion(o, locs)

    # bootstrap de personas dentro de cada localidad (conserva el n por localidad)
    idx_loc = [np.where(o.loc == l)[0] for l in locs]
    b_obs, b_comp = np.empty((n_boot, len(locs))), np.empty((n_boot, len(locs)))
    for b in range(n_boot):
        sel = np.concatenate([rng.choice(ix, len(ix)) for ix in idx_loc])
        ob = Ola(o.anio, o.loc[sel], o.celda[sel], o.celda_gruesa[sel], o.y[sel], o.w[sel])
        b_obs[b] = medias_observadas(ob, locs)
        b_comp[b], _ = medias_composicion(ob, locs)

    v_obs = _var_corregida(m_obs, b_obs.var(axis=0, ddof=1))
    v_comp = _var_corregida(m_comp, b_comp.var(axis=0, ddof=1))
    sd_obs, sd_comp = float(np.sqrt(max(v_obs, 0))), float(np.sqrt(max(v_comp, 0)))

    # ¿la EPC mide territorio más allá del azar? permutar la localidad
    sd_crudo = float(np.std(m_obs, ddof=1))
    nulo = np.empty(n_perm)
    for k in range(n_perm):
        lp = rng.permutation(o.loc)
        nulo[k] = np.std([np.average(o.y[lp == l], weights=o.w[lp == l]) for l in locs], ddof=1)

    r = float(np.corrcoef(m_obs, m_comp)[0, 1])
    pendiente = float(np.polyfit(m_comp, m_obs, 1)[0])
    # atenuación por ruido en m_comp (errores en variables)
    fiab = v_comp / np.var(m_comp, ddof=1) if np.var(m_comp, ddof=1) > 0 else np.nan
    return {
        "anio": o.anio, "n": int(len(o.y)), "n_localidades": int(len(locs)),
        "sd_obs_crudo": round(sd_crudo, 4),
        "sd_obs": round(sd_obs, 4),
        "sd_comp": round(sd_comp, 4),
        "R": round(sd_obs / sd_comp, 3) if sd_comp > 0 else None,
        "r": round(r, 3),
        "pendiente": round(pendiente, 3),
        "pendiente_corregida": round(pendiente / fiab, 3) if fiab and fiab > 0 else None,
        "p_territorio": round(float((1 + (nulo >= sd_crudo).sum()) / (1 + n_perm)), 4),
        "celdas_con_respaldo": respaldos,
        "por_localidad": {int(l): {"m_obs": round(float(m_obs[i]), 4),
                                   "m_comp": round(float(m_comp[i]), 4)}
                          for i, l in enumerate(locs)},
    }


def resumir(filas: list[dict]) -> dict:
    Rs = [f["R"] for f in filas if f["R"] is not None]
    return {
        "R_mediana": round(float(np.median(Rs)), 3) if Rs else None,
        "r_mediana": round(float(np.median([f["r"] for f in filas])), 3),
        "olas_con_territorio_p05": int(sum(f["p_territorio"] < 0.05 for f in filas)),
        "n_olas": len(filas),
    }


# ---------------------------------------------------------------------------
# Datos reales
# ---------------------------------------------------------------------------

def cargar_ola(anio: int, item: str) -> Ola | None:
    from src.population.epc_bcv import (BANDAS_EDAD, EPCError, LOCALIDADES_EPC,
                                        cargar_bcv)
    ola = cargar_bcv(anio)
    d = ola.datos
    if item not in d.columns or "localidad" not in d.columns:
        return None
    df = pd.DataFrame({
        "loc": pd.to_numeric(d["localidad"], errors="coerce"),
        "sexo": pd.to_numeric(d.get("sexo"), errors="coerce"),
        "edad": pd.to_numeric(d.get("edad"), errors="coerce"),
        "estrato": pd.to_numeric(d.get("estrato"), errors="coerce"),
        "y": pd.to_numeric(d[item], errors="coerce"),
        "w": pd.to_numeric(d["peso"], errors="coerce"),
    }).dropna()
    df = df[df["loc"].isin(LOCALIDADES_EPC) & (df["w"] > 0)]
    if not df["edad"].between(1, len(BANDAS_EDAD)).all():
        raise EPCError(f"EPC {anio}: la edad no viene en bandas (DI-B9).")
    s = df["sexo"].astype(int).astype(str)
    e = df["edad"].astype(int).astype(str)
    return Ola(anio=anio, loc=df["loc"].astype(int).to_numpy(),
               celda=(s + "|" + e + "|" + df["estrato"].astype(int).astype(str)).to_numpy(),
               celda_gruesa=(s + "|" + e).to_numpy(),
               y=df["y"].to_numpy(float), w=df["w"].to_numpy(float))


def main(argv=None) -> int:
    from src.population.epc_bcv import ITEMS, LOCALIDADES_EPC, anios_en_disco
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--item", default="gestion_alcalde", choices=list(ITEMS))
    ap.add_argument("--boot", type=int, default=200)
    ap.add_argument("--perm", type=int, default=500)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args(argv)

    try:
        anios = anios_en_disco()
    except Exception as ex:   # la EPC no está donde se la busca
        print(f"No encuentro la EPC: {ex}\nVer 'python src/utils/revisar_datos.py' o exportar BSS_EPC_DIR.")
        return 1

    filas = []
    print(f"EPC · {ITEMS[args.item]['etiqueta']}\n")
    print(f"{'año':>5} {'n':>6} {'sd obs':>7} {'sd comp':>8} {'R':>6} {'r':>6} "
          f"{'pend.':>6} {'p terr.':>8}")
    for anio in anios:
        o = cargar_ola(anio, args.item)
        if o is None:
            continue
        f = analizar_ola(o, args.boot, args.perm, np.random.default_rng(args.seed + anio))
        filas.append(f)
        R = f"{f['R']:.2f}" if f["R"] is not None else "—"
        print(f"{anio:>5} {f['n']:>6} {f['sd_obs']:>7.3f} {f['sd_comp']:>8.3f} {R:>6} "
              f"{f['r']:>6.2f} {f['pendiente']:>6.2f} {f['p_territorio']:>8.3f}")

    res = resumir(filas)
    print(f"\nR mediana = {res['R_mediana']}   r mediana = {res['r_mediana']}   "
          f"olas con territorio (p<0,05): {res['olas_con_territorio_p05']} de {res['n_olas']}")
    print("sd obs / sd comp: dispersión entre localidades medida / predicha por composición, "
          "ambas corregidas por ruido.")
    print("R < 1: la composición exagera. R > 1: se queda corta.")

    SALIDA_DIR.mkdir(parents=True, exist_ok=True)
    salida = SALIDA_DIR / f"paso0b_{args.item}.json"
    salida.write_text(json.dumps({"item": args.item, "localidades": LOCALIDADES_EPC,
                                  "resumen": res, "por_ola": filas},
                                 ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{salida.relative_to(RAIZ).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
