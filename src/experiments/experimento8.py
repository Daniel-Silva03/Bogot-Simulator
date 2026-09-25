"""
Experimento 8 — ¿un LLM le gana al hot-deck como donante de opinión?

LA PREGUNTA
-----------
El pipeline necesita una sola cosa del donante: dadas las variables puente de
una persona (sexo, edad, estrato, educación), producir un valor de confianza
institucional en la escala 1-5. Hoy lo hace un hot-deck. La pregunta es si un
LLM lo hace mejor, medido sobre las MISMAS personas retenidas.

No es «¿sirven los agentes generativos?». Es la versión barata y falsable de
esa pregunta: el LLM entra donde ya hay un método, con la misma entrada y la
misma métrica, y o gana o no gana.

DOS CRITERIOS, NO UNO
---------------------
Un método puede ganar en error medio simplemente prediciendo la media a todo el
mundo. Eso no es un modelo mejor: es el defecto que este proyecto ya sufrió
—DI-M1 / POPULATION_SPECIFICATION §8.3, donde el desempate determinista aplanó
la opinión y los modelos de influencia cobraban crédito por repararlo— y es
también la falla número uno documentada de los LLM en simulación de encuestas
(Bisbee et al.: varianza *"far too low"*).

Así que se evalúa en dos ejes a la vez:

    1. ACIERTO   — MAE y RMSE por persona.
    2. FORMA     — sd de lo predicho contra sd de lo real, y W1 entre las dos
                   distribuciones.

Un método que gane en (1) y pierda en (2) **no gana**. El criterio combinado
está pre-registrado en `claude/EXPERIMENT_8_SPECIFICATION.md`.

BRAZOS
------
    media     el predictor trivial: la media ponderada del entrenamiento
    regresion regresión lineal sobre las variables puente
    hotdeck   el método actual del proyecto (matching.py), entrenamiento→retenido
    llm       el donante LLM (requiere clave; ver src/experiments/donante_llm.py)

Uso:
    python src/experiments/experimento8.py --anio 2023
    python src/experiments/experimento8.py --anio 2023 --llm data/processed/exp8/llm_respuestas.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.population.ecp import (  # noqa: E402
    COLUMNA_EDUCACION_MATCH,
    ETIQUETAS_ITEMS,
    ITEMS_UTILES,
    donante_ecp,
)

SALIDA = RAIZ / "data" / "processed" / "exp8"

#: Las mismas cuatro variables que usa el pipeline. El LLM no recibe ninguna
#: más: si recibiera algo extra, la comparación dejaría de ser sobre el mismo
#: problema.
PUENTE = ["sexo", "edad", "estrato", COLUMNA_EDUCACION_MATCH]

FRAC_RETENIDA = 0.30
SEMILLA = 42


def cargar(anio: int, seed: int = SEMILLA):
    """Entrenamiento y retenido, de la ECP si está, y si no de los CSV ya derivados.

    El repositorio y los microdatos viven en máquinas distintas (DI-V42). Este
    experimento tiene que poder correrse donde solo está el código, así que los
    dos conjuntos se exportan a `data/processed/exp8/` y se leen de ahí cuando
    la ECP no está. Son los MISMOS: la partición tiene semilla fija y los CSV
    salen de ella.
    """
    dir_ecp = RAIZ / "data" / "raw" / "ecp"
    if (dir_ecp / str(anio)).is_dir():
        d = donante_ecp(dir_ecp, anio).reset_index(drop=True)
        d["caso_id"] = np.arange(len(d))
        return partir(d, seed=seed)

    tr = SALIDA / f"entrenamiento_{anio}.csv"
    te = SALIDA / f"retenido_{anio}.csv"
    if not (tr.exists() and te.exists()):
        raise FileNotFoundError(
            f"Sin la ECP {anio} en disco y sin {tr.name}/{te.name}. Los CSV vienen en "
            f"el entregable; si esta es la máquina de los microdatos, revisa "
            f"data/raw/ecp/{anio}/.")
    print(f"(ECP {anio} no está en disco; se usan los conjuntos ya derivados de "
          f"{SALIDA.relative_to(RAIZ).as_posix()})")
    return pd.read_csv(tr), pd.read_csv(te)


def partir(d: pd.DataFrame, seed: int = SEMILLA, frac: float = FRAC_RETENIDA):
    """Entrenamiento / retenido, con semilla fija."""
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(d))
    corte = int(len(d) * (1 - frac))
    return d.iloc[idx[:corte]].reset_index(drop=True), d.iloc[idx[corte:]].reset_index(drop=True)


# --------------------------------------------------------------------------
# Métricas

def _w1(a: np.ndarray, b: np.ndarray) -> float:
    """Wasserstein-1 entre dos muestras, por cuantiles. La misma métrica de
    forma que usan los Experimentos 4 a 7."""
    q = np.linspace(0, 1, 501)
    return float(np.abs(np.quantile(a, q) - np.quantile(b, q)).mean())


def evaluar(nombre: str, y: np.ndarray, pred: np.ndarray, w: np.ndarray,
            grupos: dict[str, np.ndarray]) -> dict:
    ok = ~np.isnan(pred)
    y, pred, w = y[ok], pred[ok], w[ok]
    res = {
        "brazo": nombre,
        "n": int(len(y)),
        "mae": float(np.abs(y - pred).mean()),
        "rmse": float(np.sqrt(((y - pred) ** 2).mean())),
        # La forma. `sd_ratio` cerca de 1 = la predicción tiene la dispersión
        # de lo real; cerca de 0 = aplanamiento, el defecto de DI-M1.
        "sd_real": float(y.std(ddof=1)),
        "sd_pred": float(pred.std(ddof=1)),
        "sd_ratio": float(pred.std(ddof=1) / y.std(ddof=1)),
        "w1": _w1(y, pred),
        # El agregado: ¿reproduce la media ponderada de la ciudad?
        "media_real": float(np.average(y, weights=w)),
        "media_pred": float(np.average(pred, weights=w)),
        "sesgo": float(np.average(pred, weights=w) - np.average(y, weights=w)),
        "corr": float(np.corrcoef(y, pred)[0, 1]) if pred.std() > 1e-9 else float("nan"),
    }
    # Por subgrupo: el aplanamiento aparece acá antes que en el agregado.
    por = {}
    for g, v in grupos.items():
        v = v[ok]
        por[g] = {str(k): round(float(np.abs(y[v == k] - pred[v == k]).mean()), 4)
                  for k in sorted(pd.unique(v)) if (v == k).sum() >= 30}
    res["mae_por_subgrupo"] = por
    res["dpd"] = {g: round(max(m.values()) - min(m.values()), 4)
                  for g, m in por.items() if len(m) >= 2}
    return res


# --------------------------------------------------------------------------
# Brazos

def brazo_media(tr: pd.DataFrame, te: pd.DataFrame) -> np.ndarray:
    m = float(np.average(tr["confianza_institucional"], weights=tr["factor_expansion"]))
    return np.full(len(te), m)


def brazo_regresion(tr: pd.DataFrame, te: pd.DataFrame) -> np.ndarray:
    def X(d):
        m = np.column_stack([
            np.ones(len(d)),
            (d["sexo"] == "M").astype(float),
            d["edad"].astype(float),
            d["estrato"].astype(float),
            d[COLUMNA_EDUCACION_MATCH].astype(float),
        ])
        return m
    beta, *_ = np.linalg.lstsq(X(tr), tr["confianza_institucional"].astype(float), rcond=None)
    return np.clip(X(te) @ beta, 1, 5)


def brazo_hotdeck(tr: pd.DataFrame, te: pd.DataFrame, seed: int = SEMILLA) -> np.ndarray:
    """El método del proyecto: bloque exacto por sexo + vecino más cercano en
    edad/estrato/educación estandarizadas, con desempate ponderado (DI-M1)."""
    rng = np.random.default_rng(seed)
    cols = ["edad", "estrato", COLUMNA_EDUCACION_MATCH]
    mu = tr[cols].astype(float).mean()
    sd = tr[cols].astype(float).std().replace(0, 1)
    pred = np.full(len(te), np.nan)

    for sexo in te["sexo"].unique():
        pool = tr[tr["sexo"] == sexo]
        if pool.empty:
            pool = tr
        P = ((pool[cols].astype(float) - mu) / sd).to_numpy()
        vals = pool["confianza_institucional"].to_numpy(float)
        pesos = pool["factor_expansion"].to_numpy(float)
        objetivo = te["sexo"] == sexo
        Q = ((te.loc[objetivo, cols].astype(float) - mu) / sd).to_numpy()

        for j, q in zip(np.where(objetivo)[0], Q):
            dist = np.sqrt(((P - q) ** 2).sum(1))
            # DI-M1: con variables discretas los empates son masivos. Se
            # sortean proporcionales al factor de expansión, no se toma el
            # primero — tomarlo es lo que aplanaba la opinión.
            empatados = np.where(dist <= dist.min() + 1e-9)[0]
            p = pesos[empatados] / pesos[empatados].sum()
            pred[j] = vals[rng.choice(empatados, p=p)]
    return pred


def brazo_llm(te: pd.DataFrame, ruta: Path) -> np.ndarray:
    """Lee las respuestas que produjo `donante_llm.py` y las promedia.

    El LLM responde los 13 ítems, no el índice: así el promedio se construye
    igual que en el dato real y la varianza sale de las respuestas, no de una
    sola cifra que el modelo tiende a poner en el centro.
    """
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    respuestas = {int(k): v for k, v in datos["respuestas"].items()}
    pred = np.full(len(te), np.nan)
    for i, fila in enumerate(te.itertuples()):
        r = respuestas.get(int(fila.caso_id))
        if not r:
            continue
        vals = [v for v in r.values() if isinstance(v, (int, float)) and 1 <= v <= 5]
        if len(vals) >= 7:          # el mismo mínimo que INDICE_MIN_ITEMS
            pred[i] = float(np.mean(vals))
    return pred


def por_item(anio: int, te: pd.DataFrame, ruta_llm: Path) -> list[dict] | None:
    """Compara ítem por ítem: ¿de qué instituciones desconfía de más el modelo?

    El sesgo del índice es un promedio y esconde de dónde sale. Si el modelo
    califica bajo a TODAS por igual es un corrimiento global; si castiga a unas
    y no a otras, es otra cosa y se puede describir.
    """
    verdad = SALIDA / f"retenido_items_{anio}.csv"
    if not verdad.exists():
        return None
    V = pd.read_csv(verdad).set_index("caso_id")
    datos = json.loads(Path(ruta_llm).read_text(encoding="utf-8"))
    R = {int(k): v for k, v in datos["respuestas"].items()}
    comunes = [c for c in te["caso_id"].astype(int) if c in R and c in V.index]
    if not comunes:
        return None

    filas = []
    for it in [c for c in V.columns if c.startswith("P5263")]:
        real = V.loc[comunes, it].dropna()
        pred = pd.Series({c: R[c].get(it) for c in comunes}).dropna()
        j = real.index.intersection(pred.index)
        if len(j) < 5:
            continue
        filas.append({
            "item": it,
            "etiqueta": ETIQUETAS_ITEMS.get(it, it),
            "n": int(len(j)),
            "real": round(float(real[j].mean()), 3),
            "llm": round(float(pred[j].mean()), 3),
            "dif": round(float(pred[j].mean() - real[j].mean()), 3),
        })
    return sorted(filas, key=lambda r: r["dif"])


# --------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--anio", type=int, default=2023)
    ap.add_argument("--llm", default=None, help="JSON de respuestas del LLM")
    ap.add_argument("--seed", type=int, default=SEMILLA)
    args = ap.parse_args(argv)

    tr, te = cargar(args.anio, seed=args.seed)

    y = te["confianza_institucional"].to_numpy(float)
    w = te["factor_expansion"].to_numpy(float)
    grupos = {
        "sexo": te["sexo"].to_numpy(),
        "estrato": te["estrato"].astype(int).to_numpy(),
        "educacion": te[COLUMNA_EDUCACION_MATCH].astype(int).to_numpy(),
        "edad_banda": pd.cut(te["edad"], [17, 29, 44, 59, 200],
                             labels=["18-29", "30-44", "45-59", "60+"]).to_numpy(),
    }

    brazos = {
        "media": brazo_media(tr, te),
        "regresion": brazo_regresion(tr, te),
        "hotdeck": brazo_hotdeck(tr, te, seed=args.seed),
    }
    if args.llm:
        brazos["llm"] = brazo_llm(te, Path(args.llm))

    filas = [evaluar(n, y, p_, w, grupos) for n, p_ in brazos.items()]

    # --- comparación en el MISMO subconjunto (DI-E1) --------------------
    # El brazo LLM suele correrse sobre una submuestra (--n) mientras los
    # baselines cubren todo el retenido. Compararlos así es comparar cosas
    # distintas: si esas personas resultan más confiadas que el promedio, el
    # sesgo del LLM se infla por el subconjunto y no por el modelo. La tabla
    # que decide es la de las personas que TODOS los brazos respondieron.
    comun = None
    if "llm" in brazos:
        m = ~np.isnan(brazos["llm"])
        if m.sum() < len(te):
            gc = {k: v[m] for k, v in grupos.items()}
            comun = [evaluar(n, y[m], p_[m], w[m], gc) for n, p_ in brazos.items()]

    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / f"resultados_{args.anio}.json").write_text(
        json.dumps({"anio": args.anio, "seed": args.seed,
                    "n_entrenamiento": len(tr), "n_retenido": len(te),
                    "items": len(ITEMS_UTILES), "brazos": filas,
                    "brazos_subconjunto_comun": comun},
                   ensure_ascii=False, indent=2), encoding="utf-8")

    def tabla(titulo, rs):
        print(f"\n{titulo}\n")
        print(f"{'brazo':>10} {'n':>6} {'MAE':>7} {'RMSE':>7} {'corr':>7} {'sd pred':>8} "
              f"{'sd ratio':>9} {'W1':>7} {'sesgo':>8}")
        for r in rs:
            print(f"{r['brazo']:>10} {r['n']:>6} {r['mae']:>7.4f} {r['rmse']:>7.4f} "
                  f"{r['corr']:>7.3f} {r['sd_pred']:>8.4f} {r['sd_ratio']:>9.3f} "
                  f"{r['w1']:>7.4f} {r['sesgo']:>+8.4f}")
        print(f"\n  sd real: {rs[0]['sd_real']:.4f}   media real: {rs[0]['media_real']:.4f}")

    print(f"\nECP {args.anio} · entrenamiento {len(tr)} · retenido {len(te)}")
    if comun:
        tabla("SOBRE TODO EL RETENIDO  (el brazo LLM cubre solo una parte — no comparable)",
              filas)
        n_llm = comun[-1]["n"]
        tabla(f"SOBRE LAS MISMAS {n_llm} PERSONAS  <-- ESTA es la comparación válida",
              comun)
        if n_llm < 100:
            ee = comun[0]["sd_real"] / np.sqrt(n_llm)
            print(f"\n  AVISO: {n_llm} casos. El error estándar de la media es ±{ee:.3f}, "
                  f"así que un sesgo\n  menor que ~{2*ee:.2f} no se distingue de cero. "
                  f"No se lee nada de acá todavía: correr con --n 400.")
    else:
        tabla("resultados", filas)
    print("\n  sd ratio cerca de 1 = conserva la dispersión; cerca de 0 = la aplana (DI-M1).")

    if args.llm:
        items = por_item(args.anio, te, Path(args.llm))
        if items:
            print(f"\nPOR INSTITUCIÓN  (n={items[0]['n']})\n")
            print(f"{'real':>6} {'LLM':>6} {'dif':>7}  institución")
            for r in items:
                print(f"{r['real']:>6.2f} {r['llm']:>6.2f} {r['dif']:>+7.2f}  {r['etiqueta']}")
            difs = [r["dif"] for r in items]
            print(f"\n  corrimiento medio {np.mean(difs):+.2f}, "
                  f"rango {min(difs):+.2f} a {max(difs):+.2f}.")
            print("  Parejo = el modelo desconfía de todo por igual. Disparejo = "
                  "confunde unas instituciones con otras.")
        else:
            print(f"\n  (sin retenido_items_{args.anio}.csv no se puede comparar por institución)")
    print(f"\n  {(SALIDA / f'resultados_{args.anio}.json').relative_to(RAIZ).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
