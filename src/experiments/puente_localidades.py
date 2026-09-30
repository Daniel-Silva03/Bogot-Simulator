"""
Puente por localidades: con los encuestados de 2022, 2023 y 2024 juntos (~250 por
localidad), ¿las medias por localidad del puntaje del puente se parecen a las reales
más que las de la demografía?

Pre-registro: `docs/PUENTE_LOCALIDADES_SPECIFICATION.md`. Este módulo lo ejecuta y no
decide nada que el documento no haya decidido.

    11 preguntas escondidas (las de la primera prueba menos SA4), cada una con los
    años en que se puede juntar (`epc_armonizado/items.csv`). Los 36 puentes son los
    de la primera prueba, leídos de su caché: **no se llama al modelo**.

Uso:
    python src/experiments/puente_localidades.py

Escribe `data/processed/puente_localidades/resultado.json`. Solo cifras agregadas.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-PL1. **Los puentes salen de la caché de la primera prueba y de nada más.** El
    cliente que se le pasa a `puente.recolectar` levanta un error si se le llama:
    si falta un puente en la caché, la corrida se detiene en vez de gastar.

DI-PL2. **El código de cada pregunta en cada año** es el del catálogo en 2023 y, en
    2022 y 2024, el del inventario (`epc_inventario/items.csv`, estado «ok»). Una
    pregunta entra en un año solo si ese año está en `anios` de la armonización
    (DI-AR1, DI-AR5); si no, en ese año cuenta como 0 en el puente (§4) y como «sin
    dato» si es la escondida.

DI-PL3. **Estandarización dentro de cada año** (§4): media y desviación ponderadas con
    los pesos reescalados de la ola (DI-AR2), sobre los que respondieron dentro de
    la escala. «No sabe» y «no existe ese año» valen 0.

DI-PL4. **Demografía** (§4): sexo, tramo de edad y estrato, con los códigos de cada
    año (`epc_bcv.DEMOGRAFICAS`; las etiquetas son las mismas en los tres, verificado
    el 30/09). Misma regresión con validación cruzada de `puente.base_demografia`.
    Sin variable de año: el pre-registro no la nombra.

DI-PL5. **Las 7 preguntas de P3** son las de confiabilidad de la muestra entera
    (Spearman-Brown, `conf_junto_sb`) ≥ 0,5, como en §2. Si del archivo no salen 7, la
    corrida se detiene: algo cambió desde el pre-registro.

DI-PL6. **Control de mitades — NO PRE-REGISTRADO, añadido el 30/09 después de ver la
    primera corrida.** Hecho: el ruido (`MA3_3`), cuya confiabilidad por localidad es
    0,00, dio r_loc = 0,77. Eso no puede ser geografía. Supuesto: el puntaje y la
    respuesta real salen de las mismas personas; si el puente acierta por persona,
    el ruido de muestreo de las medias por localidad es el mismo en los dos lados y se
    correlaciona solo. La demografía, que acierta poco por persona, casi no lo tiene.
    Afectaba igual a la primera prueba (`PUENTE_RESULTS.md`). Control: medias del
    puntaje en una mitad al azar de las personas contra medias reales en la otra
    mitad, mediana de 200 particiones, para el puente y para la demografía. Se
    reporta al lado de P1; **no cambia la regla de decisión escrita**, pero la
    lectura se discute con él (RESULTS).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402
from src.experiments import puente as pu                   # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "puente_localidades"
CACHE_PUENTE = pu.SALIDA / "cache.json"
ARMONIZADO = RAIZ / "data" / "processed" / "epc_armonizado" / "items.csv"
INVENTARIO = RAIZ / "data" / "processed" / "epc_inventario" / "items.csv"
ANIOS = (2022, 2023, 2024)
FUERA = ("SA4",)                                         # §3: no está en el catálogo
ESCONDIDAS = tuple(v for v in pu.ESCONDIDAS if v not in FUERA)
UMBRAL_P1 = UMBRAL_P2 = 8
UMBRAL_CONF_P3 = 0.5
N_P3 = 7
N_MITADES = 200


class PuenteLocalidadesError(RuntimeError):
    """Algo impide correr la prueba como está pre-registrada."""


# --------------------------------------------------------------------------
# Datos de tres años

def _wz(x: np.ndarray, ok: np.ndarray, w: np.ndarray) -> np.ndarray:
    """DI-PL3."""
    if not ok.any():
        return np.zeros(len(x))
    m = pu._wmean(x[ok], w[ok])
    sd = np.sqrt(pu._wmean((x[ok] - m) ** 2, w[ok])) or 1.0
    return np.where(ok, (x - m) / sd, 0.0)


class DatosOlas:
    """Los encuestados de varios años, con la misma interfaz que `puente.Datos`.

    `olas`: {año: DataFrame con peso (ya reescalado), cod_loc, sexo, edad_tramo,
    estrato y las columnas crudas de las preguntas}. `codigo(v, año)` da la columna
    de la pregunta en ese año; `anios[v]` los años en que se puede juntar.
    """

    def __init__(self, olas: dict[int, pd.DataFrame], codigo, anios: dict[str, tuple],
                 fichas_puente: dict, fichas_esc: dict):
        orden = sorted(olas)
        self.anio = np.concatenate([np.full(len(olas[a]), a) for a in orden])
        self.w = np.concatenate([olas[a].peso.to_numpy(float) for a in orden])
        self.loc = np.concatenate([olas[a].cod_loc.to_numpy() for a in orden])
        self.demo = pd.concat([olas[a][["sexo", "edad_tramo", "estrato"]] for a in orden], ignore_index=True)
        self.disponible = {}                                   # v -> años en que entra al puente

        def crudo(v, f, a):
            d = olas[a]
            if a not in anios.get(v, ()):
                return None
            c = codigo(v, a)
            if c is None or c not in d.columns:
                raise PuenteLocalidadesError(f"{v} debería estar en {a} con la columna {c}.")
            x = pd.to_numeric(d[c], errors="coerce").to_numpy(float)
            return x, np.isin(x, f["escala"])

        self.z = {}
        for v, f in fichas_puente.items():
            partes, esta = [], []
            for a in orden:
                r = crudo(v, f, a)
                if r is None:
                    partes.append(np.zeros(len(olas[a])))
                else:
                    partes.append(_wz(r[0], r[1], olas[a].peso.to_numpy(float)))
                    esta.append(a)
            self.z[v] = np.concatenate(partes)
            self.disponible[v] = tuple(esta)
        self.y = {}
        for v, f in fichas_esc.items():
            xs, oks = [], []
            for a in orden:
                r = crudo(v, f, a)
                n = len(olas[a])
                xs.append(r[0] if r else np.full(n, np.nan))
                oks.append(r[1] if r else np.zeros(n, bool))
            self.y[v] = (np.concatenate(xs), np.concatenate(oks))

    def puntaje(self, puente: list[dict]) -> np.ndarray:
        return pu.Datos.puntaje(self, puente)

    def peso_disponible(self, puente: list[dict]) -> dict[int, float]:
        """§4: fracción del peso del puente cuyas preguntas existen en cada año."""
        tot = sum(p["peso"] for p in puente)
        return {int(a): sum(p["peso"] for p in puente if a in self.disponible[p["codigo"]]) / tot
                for a in sorted(set(self.anio))}


# --------------------------------------------------------------------------
# Análisis

def r_loc_cruzado(puntaje, y, w, loc, n: int = N_MITADES, semilla: int = pu.SEMILLA) -> float:
    """DI-PL6 (no pre-registrado): medias del puntaje en una mitad de las personas contra
    medias reales en la otra; mediana de `n` particiones. Quita el ruido de muestreo
    compartido, que no es geografía."""
    rng = np.random.default_rng(semilla)
    locs = sorted(set(loc) - {pu.SUMAPAZ})
    rs = []
    for _ in range(n):
        m = rng.random(len(y)) < 0.5
        a = [pu._wmean(puntaje[m & (loc == l)], w[m & (loc == l)]) for l in locs]
        b = [pu._wmean(y[~m & (loc == l)], w[~m & (loc == l)]) for l in locs]
        rs.append(float(np.corrcoef(a, b)[0, 1]))
    return float(np.median(rs))


def analizar(datos: DatosOlas, fichas_esc: dict, respuestas: dict, confiabilidad: dict[str, float],
             anios: dict[str, tuple], n_mitades: int = N_MITADES) -> dict:
    por = {}
    for v in fichas_esc:
        x, ok = datos.y[v]
        med = [pu.medir(datos, v, fichas_esc[v], r) for r in respuestas[v]]
        dem = pu.base_demografia(datos, v)
        cru = [r_loc_cruzado(datos.puntaje(r["preguntas"])[ok], x[ok], datos.w[ok], datos.loc[ok], n_mitades)
               if r else 0.0 for r in respuestas[v]]
        por[v] = {
            "anios": list(anios[v]),
            "n": int(ok.sum()),
            "n_loc_mediana": float(pd.Series(datos.loc[ok]).value_counts().median()),
            "r_loc": float(np.median([m["r_loc"] for m in med])),
            "rho_ind": float(np.median([m["rho_ind"] for m in med])),
            "r_loc_llamadas": [m["r_loc"] for m in med],
            "respuestas_validas": int(sum(m["valida"] for m in med)),
            "demografia": {"rho_ind": pu.rho_ind(dem, x[ok], datos.w[ok]),
                           "r_loc": pu.r_loc(dem, x[ok], datos.w[ok], datos.loc[ok])},
            "control_mitades_no_preregistrado": {                                     # DI-PL6
                "r_loc": float(np.median(cru)),
                "demografia": r_loc_cruzado(dem, x[ok], datos.w[ok], datos.loc[ok], n_mitades)},
            "confiabilidad_sb": confiabilidad[v],
            "peso_disponible": [datos.peso_disponible(r["preguntas"]) if r else None for r in respuestas[v]],
            "puentes": [r["preguntas"] if r else None for r in respuestas[v]],
        }
    return {"por_pregunta": por}


def evaluar(a: dict) -> dict:
    """§5 y §6."""
    P = a["por_pregunta"]
    n = len(P)
    c1 = {v: bool(p["r_loc"] > p["demografia"]["r_loc"]) for v, p in P.items()}
    c2 = {v: bool(p["rho_ind"] > p["demografia"]["rho_ind"]) for v, p in P.items()}
    geo = [v for v, p in P.items() if p["confiabilidad_sb"] >= UMBRAL_CONF_P3]
    if len(geo) != N_P3:
        raise PuenteLocalidadesError(f"P3 pide {N_P3} preguntas con confiabilidad ≥ {UMBRAL_CONF_P3}; hay {len(geo)}.")
    med3 = float(np.median([P[v]["r_loc"] for v in geo]))
    p1, p2 = sum(c1.values()) >= UMBRAL_P1, sum(c2.values()) >= UMBRAL_P2
    pred = {
        "P1": {"umbral": f"r_loc > demografía en ≥ {UMBRAL_P1} de {n}", "cuenta": sum(c1.values()),
               "por_pregunta": c1, "se_cumple": p1},
        "P2": {"umbral": f"ρ_ind > demografía en ≥ {UMBRAL_P2} de {n} (control)", "cuenta": sum(c2.values()),
               "por_pregunta": c2, "se_cumple": p2},
        "P3": {"umbral": f"mediana de r_loc ≥ 0,5 en las {N_P3} con confiabilidad ≥ 0,5 (se reporta)",
               "preguntas": geo, "mediana": med3, "se_cumple": med3 >= 0.5},
    }
    if not p2:
        lectura = ("—", "No se adopta ninguna lectura: hay que revisar cómo se juntaron los años.")
    elif p1:
        lectura = ("A", "Las preguntas nuevas pasan a tener mapa, con la población 2022-2024, rotulado como "
                        "suposición y con los filtros de margen de la página.")
    else:
        lectura = ("B", "Se mantiene la lectura B: las preguntas nuevas se responden por grupos, sin mapa. "
                        "Juntar años sigue sirviendo para el mapa de las preguntas del catálogo.")
    return {"predicciones": pred, "lectura": lectura[0], "regla": lectura[1]}


# --------------------------------------------------------------------------
# Carga real y línea de comandos

def sin_llamadas(*_):
    """DI-PL1."""
    raise PuenteLocalidadesError("Un puente no está en la caché de la primera prueba; esta prueba no llama al modelo.")


def cargar_olas() -> dict[int, pd.DataFrame]:
    from src.population import armonizar_epc as ae
    from src.population import epc_bcv as eb
    from src.population import poblacion_epc as pe
    olas = {}
    for a in ANIOS:
        base, ola = ae.cargar_ola(a)                                           # peso reescalado (DI-AR2)
        d, col = ola["datos"], ola["col"]
        num = lambda n: pd.to_numeric(d[col[eb.DEMOGRAFICAS[n][a].upper()]], errors="coerce")   # noqa: E731
        df = d.copy()
        df.columns = [c.upper() for c in df.columns]
        df = df.assign(peso=base.peso.to_numpy(), cod_loc=base.cod_loc.to_numpy(),
                       sexo=num("sexo").map({1: "M", 2: "F"}).to_numpy(),
                       edad_tramo=pe.tramo_edad(num("edad")).to_numpy(),
                       estrato=num("estrato").to_numpy())
        olas[a] = df[df.cod_loc.between(1, 19)].reset_index(drop=True)
    return olas


def main(argv=None) -> int:
    fichas_esc, fichas_puente = pu.cargar_fichas()
    fichas_esc = {v: fichas_esc[v] for v in ESCONDIDAS}
    arm = pd.read_csv(ARMONIZADO).set_index("variable")
    anios = {v: tuple(int(x) for x in str(arm.loc[v, "anios"]).split()) for v in arm.index}
    faltan = [v for v in list(fichas_esc) + list(fichas_puente) if v not in anios]
    if faltan:
        raise PuenteLocalidadesError(f"Sin armonización: {faltan}")
    inv = pd.read_csv(INVENTARIO)
    inv = inv[inv.estado == "ok"].set_index(["variable", "anio"]).codigo
    todas = {**fichas_puente, **fichas_esc}

    def codigo(v, a):
        return str(todas[v]["codigo"]).upper() if a == 2023 else str(inv.get((v, a))).upper()

    conf = {v: float(arm.loc[v, "conf_junto_sb"]) for v in fichas_esc}
    cache = e9.Cache(CACHE_PUENTE)
    respuestas, _ = pu.recolectar(fichas_esc, fichas_puente, sin_llamadas, cache, pu.MODELO)   # DI-PL1
    datos = DatosOlas(cargar_olas(), codigo, anios, fichas_puente, fichas_esc)
    a = analizar(datos, fichas_esc, respuestas, conf, anios)
    v = evaluar(a)
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "resultado.json").write_text(
        json.dumps({**a, **v, "n_por_anio": {int(k): int((datos.anio == k).sum()) for k in ANIOS},
                    "modelo": pu.MODELO, "llamadas_nuevas": 0},
                   ensure_ascii=False, indent=2, default=float), encoding="utf-8")
    print(f"{'pregunta':8s} {'años':>14s} {'n/loc':>5s} {'conf':>5s} │ {'r_loc':>6s} {'demo':>6s} │ {'ρ_ind':>6s} {'demo':>6s}"
          f" │ mitades (no pre-reg.) {'puente':>6s} {'demo':>6s}")
    for k, p in a["por_pregunta"].items():
        c = p["control_mitades_no_preregistrado"]
        print(f"{k:8s} {'-'.join(map(str, p['anios'])):>14s} {p['n_loc_mediana']:5.0f} {p['confiabilidad_sb']:5.2f} │ "
              f"{p['r_loc']:6.3f} {p['demografia']['r_loc']:6.3f} │ {p['rho_ind']:6.2f} {p['demografia']['rho_ind']:6.2f}"
              f" │ {'':21s} {c['r_loc']:6.2f} {c['demografia']:6.2f}")
    for k, p in v["predicciones"].items():
        c = f"{p['cuenta']} de {len(a['por_pregunta'])}" if "cuenta" in p else f"mediana {p['mediana']:.2f}"
        print(f"  {k} {'se cumple' if p['se_cumple'] else 'NO se cumple'} — {p['umbral']} ({c})")
    print(f"\nLectura: {v['lectura']} — {v['regla']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
