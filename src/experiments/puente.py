"""
Puente: ¿puede la población EPC 2023 «responder» una pregunta que no conoce, a
partir de las respuestas reales que sí tiene, mejor que la demografía y que el azar?

Pre-registro: `docs/PUENTE_SPECIFICATION.md` (con su enmienda 1). Este módulo lo
ejecuta y no decide nada que el documento no haya decidido.

    12 preguntas escondidas a la vez; el modelo ve cada una como nueva, con el
    catálogo de las otras 91, y elige de 1 a 5 con sentido y peso, más un nivel.
    Cada persona responde con la suma de sus respuestas estandarizadas.
    Se mide contra la respuesta real: ρ_ind, r_loc, e_nivel.

Uso:
    python src/experiments/puente.py --simulado          # sin gasto, para probar
    python src/experiments/puente.py                     # 36 llamadas reales (pide confirmación)

Escribe `data/processed/puente/resultado.json`; la caché de respuestas en
`data/processed/puente/cache.json` (no se sube).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-PU1. **Se mide sobre los 1.501 encuestados, no sobre los agentes** (§5): los
    agentes son copias y no agregan información.

DI-PU2. **Spearman ponderado = Pearson ponderado (FEXP) de los rangos.** Los
    rangos se calculan sin ponderar, con empates promediados, sobre las personas
    con respuesta válida a la pregunta escondida.

DI-PU3. **Una respuesta del modelo que no se puede usar cuenta como un puente
    vacío:** ρ_ind = 0, r_loc = 0 y, para el nivel, el error máximo (1). Es lo
    conservador: una respuesta rota no puede ayudar a pasar el umbral. Inválida
    es: JSON que no se lee; ninguna pregunta; más de 5; un código que no está en
    el catálogo del puente (incluida una de las escondidas); un sentido que no sea
    «+» o «−»; un peso fuera de 1-3; un nivel fuera de la escala.

DI-PU4. **Qué extremo de cada escala es el favorable** (lo necesita el nivel
    ingenuo de §5) se decide por palabras en las etiquetas del primer y el último
    código: si el último suena favorable y el primero desfavorable, lo favorable
    está arriba; al revés, abajo. Si no se puede decidir, la pregunta no entra al
    promedio del tono, y si es una escondida, su nivel ingenuo es el punto medio de
    la escala. Las listas de palabras están aquí, escritas antes de ver ningún
    dato, y el resultado dice qué preguntas quedaron sin dirección.

DI-PU5. **La línea base demográfica** es una regresión lineal ponderada sobre
    variables indicadoras de sexo, tramo de edad, estrato y educación armonizada
    (con una categoría «sin dato»), con validación cruzada de 5 partes y
    semilla fija.

DI-PU6. **Modelo y temperatura:** `xiaomi/mimo-v2.6-pro` (el de los Experimentos
    8 y 9) a temperatura 0, tres llamadas por pregunta (`rep` 0, 1, 2). Con
    temperatura 0 las tres pueden salir iguales; se hacen igual, como dice §4.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "puente"
CATALOGO = RAIZ / "data" / "processed" / "poblacion_epc2023" / "catalogo.json"
ESCONDIDAS = ("CV1", "AG2", "VS8", "VS10", "GG7", "GG3", "MV4", "SA4", "MA3_1", "MA3_3", "CR2", "CO2")
MODELO = e9.MODELO
TEMPERATURA = 0.0
REPETICIONES = 3
MAX_PREGUNTAS = 5
N_AZAR = 200
N_FOLDS = 5
N_MITADES = 200
SEMILLA = 20260930
SUMAPAZ = 20

FAVORABLE = re.compile(r"muy bien|buen|bien|satisfech|segur|orgullos|mejor|excelente|de acuerdo|confí|confi|"
                       r"favorable|alt[oa] calidad|limpi|suficiente|fácil|facil|optimis|mucho respeto|respet", re.I)
DESFAVORABLE = re.compile(r"mal|insatisf|insegur|peor|pésim|pesim|nada|desacuerdo|desfavorable|sucio|desmejor|empeor|"
                          r"insuficiente|difícil|dificil|no orgullos|irrespet|poco respeto|ningún respeto|ningun respeto", re.I)

SISTEMA = (
    "Eres un asistente de métodos de encuesta. Te doy una PREGUNTA NUEVA y un CATÁLOGO de preguntas "
    "que ya se hicieron a las mismas personas en Bogotá (Encuesta de Percepción Ciudadana 2023). "
    "Tu tarea es construir un PUENTE: elegir de 1 a 5 preguntas del catálogo cuyas respuestas "
    "permitan ordenar a las personas según cómo responderían la pregunta nueva, y proponer la "
    "media esperada de la pregunta nueva en Bogotá.\n"
    "Para cada pregunta elegida da: su código; el sentido, '+' si los códigos más altos de esa "
    "pregunta van con códigos más altos de la pregunta nueva, '-' si van con códigos más bajos; "
    "y un peso de 1 a 3 según qué tan relacionada está.\n"
    "Responde SOLO con un JSON, sin texto alrededor, con esta forma:\n"
    '{"preguntas": [{"codigo": "XX", "sentido": "+", "peso": 2}], "nivel": 3.1, '
    '"justificacion": "una o dos frases"}\n'
    "El nivel es la media esperada en la escala de códigos de la pregunta nueva."
)

Llamar = Callable[[str, str, str, float], object]


class PuenteError(RuntimeError):
    """Algo impide correr el análisis como está pre-registrado."""


# --------------------------------------------------------------------------
# Fichas de preguntas

def _texto_ficha(f: dict) -> str:
    etq = "; ".join(f"{k}={v}" for k, v in f["etiquetas"].items() if int(k) in f["escala"])
    return f'{f["variable"]} | {f["pregunta"]} | {etq}'


def cargar_fichas(ruta: Path = CATALOGO) -> tuple[dict[str, dict], dict[str, dict]]:
    """(fichas de las 12 escondidas, catálogo del puente: las otras). Enmienda 1."""
    from src.population import epc_bcv as eb
    from src.population import poblacion_epc as pe
    cat = {c["variable"]: c for c in json.loads(ruta.read_text(encoding="utf-8"))["dentro"]}
    esc = {}
    etq = None
    for v in ESCONDIDAS:
        if v in cat:
            esc[v] = cat[v]
            continue
        # SA4 no está en el catálogo (78 % de respuesta): su ficha sale igual, del archivo
        if etq is None:
            etq = {k.upper(): x for k, x in pe._etiquetas(eb.archivo_del_anio(pe.ANIO)).items()}
        e = etq.get(v.upper())
        s = pe.escala_de(e) if e else None
        if s is None:
            raise PuenteError(f"La pregunta escondida {v} no tiene una escala legible.")
        dic = pd.read_excel(eb.resolver_dir_bcv() / "EPC Suprema.xlsx", "VARIABLES", header=1).set_index("VARIABLE_cod")
        esc[v] = {"variable": v, "codigo": v, "nombre": str(dic.loc[v, "VARIABLE_tag"]),
                  "pregunta": str(dic.loc[v, "PREGUNTA_tag"]), "escala": s[0], "no_respuesta": s[1],
                  "etiquetas": {str(k): t for k, t in sorted(e.items())}}
    puente = {k: c for k, c in cat.items() if k not in ESCONDIDAS}
    return esc, puente


def direccion(f: dict) -> Optional[int]:
    """DI-PU4: +1 si lo favorable está arriba, −1 si abajo, None si no se sabe."""
    lo, hi = f["etiquetas"][str(min(f["escala"]))], f["etiquetas"][str(max(f["escala"]))]
    def tono(t):
        d, fav = bool(DESFAVORABLE.search(t)), bool(FAVORABLE.search(t))
        return -1 if d else (1 if fav else 0)       # «muy mal» contiene «mal»: gana lo desfavorable
    a, b = tono(lo), tono(hi)
    if b > 0 and a < 0:
        return 1
    if b < 0 and a > 0:
        return -1
    return None


# --------------------------------------------------------------------------
# Estadística

def _wmean(x, w):
    return float(np.sum(x * w) / np.sum(w))


def _wpearson(x, y, w) -> float:
    mx, my = _wmean(x, w), _wmean(y, w)
    cov = np.sum(w * (x - mx) * (y - my))
    den = np.sqrt(np.sum(w * (x - mx) ** 2) * np.sum(w * (y - my) ** 2))
    return float(cov / den) if den > 0 else 0.0


def rho_ind(puntaje, y, w) -> float:
    """DI-PU2."""
    rx = pd.Series(puntaje).rank().to_numpy()
    ry = pd.Series(y).rank().to_numpy()
    return _wpearson(rx, ry, w)


def r_loc(puntaje, y, w, loc) -> float:
    locs = sorted(set(loc) - {SUMAPAZ})
    a = [_wmean(puntaje[loc == l], w[loc == l]) for l in locs]
    b = [_wmean(y[loc == l], w[loc == l]) for l in locs]
    return float(np.corrcoef(a, b)[0, 1])


class Datos:
    """Los encuestados de 2023, con las respuestas del catálogo estandarizadas."""

    def __init__(self, donante: pd.DataFrame, fichas_puente: dict, fichas_esc: dict):
        col = {c.upper(): c for c in donante.columns}
        self.w = donante.peso.to_numpy(float)
        self.loc = donante.cod_loc.to_numpy()
        self.demo = donante[["sexo", "edad_tramo", "estrato", "educ_h"]]
        self.z = {}
        for v, f in fichas_puente.items():
            x = pd.to_numeric(donante[col[str(f["codigo"]).upper()]], errors="coerce").to_numpy(float)
            ok = np.isin(x, f["escala"])
            m = _wmean(x[ok], self.w[ok])
            sd = np.sqrt(_wmean((x[ok] - m) ** 2, self.w[ok])) or 1.0
            self.z[v] = np.where(ok, (x - m) / sd, 0.0)                       # «no sabe» = 0
        self.y = {}
        for v, f in fichas_esc.items():
            x = pd.to_numeric(donante[col[str(f["codigo"]).upper()]], errors="coerce").to_numpy(float)
            self.y[v] = (x, np.isin(x, f["escala"]))

    def puntaje(self, puente: list[dict]) -> np.ndarray:
        s = np.zeros(len(self.w))
        for p in puente:
            s += (1 if p["sentido"] == "+" else -1) * p["peso"] * self.z[p["codigo"]]
        return s


# --------------------------------------------------------------------------
# El modelo de lenguaje

def prompt(f_esc: dict, fichas_puente: dict) -> str:
    cat = "\n".join(_texto_ficha(f) for f in fichas_puente.values())
    return f"PREGUNTA NUEVA:\n{_texto_ficha({**f_esc, 'variable': 'NUEVA'})}\n\nCATÁLOGO:\n{cat}"


def parsear(texto: Optional[str], f_esc: dict, fichas_puente: dict) -> Optional[dict]:
    """DI-PU3: None si la respuesta no se puede usar."""
    d = e9._json_de(texto)
    if not isinstance(d, dict):
        return None
    ps, nivel = d.get("preguntas"), e9._numero(d.get("nivel"))
    if not isinstance(ps, list) or not 1 <= len(ps) <= MAX_PREGUNTAS or nivel is None:
        return None
    if not min(f_esc["escala"]) <= nivel <= max(f_esc["escala"]):
        return None
    limpio = []
    for p in ps:
        if not isinstance(p, dict):
            return None
        c, s, w = str(p.get("codigo", "")).strip(), str(p.get("sentido", "")).strip(), e9._numero(p.get("peso"))
        s = {"−": "-", "–": "-"}.get(s, s)
        if c not in fichas_puente or s not in ("+", "-") or w not in (1, 2, 3):
            return None
        limpio.append({"codigo": c, "sentido": s, "peso": int(w)})
    return {"preguntas": limpio, "nivel": float(nivel), "justificacion": str(d.get("justificacion", ""))}


# --------------------------------------------------------------------------
# Líneas base

def base_demografia(datos: Datos, v: str, semilla: int = SEMILLA) -> np.ndarray:
    """DI-PU5: predicción con validación cruzada, para los que tienen respuesta válida."""
    x, ok = datos.y[v]
    X = pd.get_dummies(datos.demo.astype("object").fillna("NA").astype(str), drop_first=True).to_numpy(float)
    X = np.column_stack([np.ones(len(X)), X])[ok]
    y, w = x[ok], datos.w[ok]
    pred = np.empty(len(y))
    folds = np.random.default_rng(semilla).integers(0, N_FOLDS, len(y))
    for k in range(N_FOLDS):
        tr, te = folds != k, folds == k
        sw = np.sqrt(w[tr])
        beta, *_ = np.linalg.lstsq(X[tr] * sw[:, None], y[tr] * sw, rcond=None)
        pred[te] = X[te] @ beta
    return pred


def base_azar(datos: Datos, v: str, fichas_puente: dict, n: int = N_AZAR, semilla: int = SEMILLA) -> dict:
    rng = np.random.default_rng(semilla)
    x, ok = datos.y[v]
    cods = list(fichas_puente)
    rs, rl = [], []
    for _ in range(n):
        k = int(rng.integers(1, MAX_PREGUNTAS + 1))
        p = [{"codigo": c, "sentido": rng.choice(["+", "-"]), "peso": int(rng.integers(1, 4))}
             for c in rng.choice(cods, k, replace=False)]
        s = datos.puntaje(p)[ok]
        rs.append(rho_ind(s, x[ok], datos.w[ok]))
        rl.append(r_loc(s, x[ok], datos.w[ok], datos.loc[ok]))
    return {"rho_ind_p95": float(np.percentile(rs, 95)), "r_loc_p95": float(np.percentile(rl, 95))}


def tono_general(datos_crudos: dict[str, tuple[np.ndarray, np.ndarray]], w: np.ndarray,
                 fichas_puente: dict) -> tuple[float, list[str]]:
    """Nivel ingenuo de §5: posición media 0-1, lo favorable arriba (DI-PU4)."""
    pos, sin = [], []
    for v, f in fichas_puente.items():
        d = direccion(f)
        if d is None:
            sin.append(v)
            continue
        x, ok = datos_crudos[v]
        lo, hi = min(f["escala"]), max(f["escala"])
        p = (_wmean(x[ok], w[ok]) - lo) / (hi - lo)
        pos.append(p if d == 1 else 1 - p)
    return float(np.mean(pos)), sin


def nivel_ingenuo(f_esc: dict, tono: float) -> float:
    lo, hi = min(f_esc["escala"]), max(f_esc["escala"])
    d = direccion(f_esc)
    if d is None:
        return (lo + hi) / 2
    return lo + (tono if d == 1 else 1 - tono) * (hi - lo)


def confiabilidad_loc(datos: Datos, v: str, n: int = N_MITADES, semilla: int = SEMILLA) -> float:
    """§8: correlación de las medias por localidad entre dos mitades al azar (descriptivo)."""
    rng = np.random.default_rng(semilla)
    x, ok = datos.y[v]
    xs, w, loc = x[ok], datos.w[ok], datos.loc[ok]
    locs = sorted(set(loc) - {SUMAPAZ})
    rs = []
    for _ in range(n):
        m = rng.random(len(xs)) < 0.5
        a = [_wmean(xs[m & (loc == l)], w[m & (loc == l)]) for l in locs]
        b = [_wmean(xs[~m & (loc == l)], w[~m & (loc == l)]) for l in locs]
        rs.append(float(np.corrcoef(a, b)[0, 1]))
    return float(np.median(rs))


# --------------------------------------------------------------------------
# El análisis

def medir(datos: Datos, v: str, f_esc: dict, respuesta: Optional[dict]) -> dict:
    x, ok = datos.y[v]
    if respuesta is None:                                                       # DI-PU3
        return {"valida": False, "rho_ind": 0.0, "r_loc": 0.0, "e_nivel": 1.0}
    s = datos.puntaje(respuesta["preguntas"])[ok]
    lo, hi = min(f_esc["escala"]), max(f_esc["escala"])
    real = _wmean(x[ok], datos.w[ok])
    return {"valida": True, "rho_ind": rho_ind(s, x[ok], datos.w[ok]),
            "r_loc": r_loc(s, x[ok], datos.w[ok], datos.loc[ok]),
            "e_nivel": abs(respuesta["nivel"] - real) / (hi - lo)}


def analizar(datos: Datos, fichas_esc: dict, fichas_puente: dict, respuestas: dict[str, list[Optional[dict]]],
             crudos_puente: dict, n_azar: int = N_AZAR) -> dict:
    tono, sin_dir = tono_general(crudos_puente, datos.w, fichas_puente)
    por = {}
    for v, f in fichas_esc.items():
        x, ok = datos.y[v]
        med = [medir(datos, v, f, r) for r in respuestas[v]]
        dem = base_demografia(datos, v)
        az = base_azar(datos, v, fichas_puente, n_azar)
        lo, hi = min(f["escala"]), max(f["escala"])
        real = _wmean(x[ok], datos.w[ok])
        ing = nivel_ingenuo(f, tono)
        por[v] = {
            "rho_ind": float(np.median([m["rho_ind"] for m in med])),
            "r_loc": float(np.median([m["r_loc"] for m in med])),
            "e_nivel": float(np.median([m["e_nivel"] for m in med])),
            "respuestas_validas": int(sum(m["valida"] for m in med)),
            "demografia": {"rho_ind": rho_ind(dem, x[ok], datos.w[ok]),
                           "r_loc": r_loc(dem, x[ok], datos.w[ok], datos.loc[ok])},
            "azar": az,
            "nivel": {"real": real, "ingenuo": ing, "e_ingenuo": abs(ing - real) / (hi - lo),
                      "propuestos": [r["nivel"] if r else None for r in respuestas[v]]},
            "puentes": [r["preguntas"] if r else None for r in respuestas[v]],
            "confiabilidad_loc": confiabilidad_loc(datos, v),
            "direccion_favorable": direccion(f),
        }
    return {"por_pregunta": por, "tono_general": tono, "sin_direccion_en_catalogo": sin_dir,
            "n_catalogo_puente": len(fichas_puente)}


def evaluar(a: dict) -> dict:
    """P1-P4 (§6) y la regla de decisión (§7)."""
    P = a["por_pregunta"]
    c1 = {v: bool(p["rho_ind"] > p["azar"]["rho_ind_p95"] and p["rho_ind"] > p["demografia"]["rho_ind"]) for v, p in P.items()}
    c2 = {v: bool(p["r_loc"] > p["demografia"]["r_loc"]) for v, p in P.items()}
    c3 = {v: bool(p["rho_ind"] > 0) for v, p in P.items()}
    c4 = {v: bool(p["e_nivel"] < p["nivel"]["e_ingenuo"]) for v, p in P.items()}
    p1, p2, p3, p4 = sum(c1.values()) >= 9, sum(c2.values()) >= 8, sum(c3.values()) >= 11, sum(c4.values()) >= 8
    pred = {
        "P1": {"umbral": "ρ_ind > p95 del azar y > demografía, en ≥ 9 de 12", "cuenta": sum(c1.values()), "por_pregunta": c1, "se_cumple": p1},
        "P2": {"umbral": "r_loc > demografía, en ≥ 8 de 12", "cuenta": sum(c2.values()), "por_pregunta": c2, "se_cumple": p2},
        "P3": {"umbral": "ρ_ind > 0, en ≥ 11 de 12", "cuenta": sum(c3.values()), "por_pregunta": c3, "se_cumple": p3},
        "P4": {"umbral": "e_nivel < el del tono general, en ≥ 8 de 12", "cuenta": sum(c4.values()), "por_pregunta": c4, "se_cumple": p4},
    }
    if p1 and p2:
        orden = ("A", "Las preguntas nuevas se responden con el puente, con mapa por localidad, rotulado como suposición.")
    elif p1:
        orden = ("B", "El puente ordena personas pero no localidades: para preguntas nuevas, diferencias entre grupos; "
                      "el mapa, solo para preguntas del catálogo.")
    else:
        orden = ("C", "El puente no sirve: la página responde solo preguntas del catálogo.")
    nivel = ("El nivel por defecto es el que propone el modelo, rotulado y editable." if p4 else
             "El nivel lo fija quien pregunta (por defecto, el tono general).")
    return {"predicciones": pred, "lectura_orden": orden[0], "regla_orden": orden[1], "regla_nivel": nivel,
            "revisar_etiquetas": not p3 and 12 - sum(c3.values()) > 1}


# --------------------------------------------------------------------------
# Recolección y línea de comandos

def modelo_simulado(fichas_puente: dict, semilla: int = SEMILLA) -> Llamar:
    """Devuelve puentes válidos al azar: sirve para probar el circuito, no para medir."""
    rng = np.random.default_rng(semilla)
    cods = list(fichas_puente)

    def llamar(modelo, sistema, usuario, temp):
        k = int(rng.integers(1, 4))
        ps = [{"codigo": c, "sentido": str(rng.choice(["+", "-"])), "peso": int(rng.integers(1, 4))}
              for c in rng.choice(cods, k, replace=False)]
        return json.dumps({"preguntas": ps, "nivel": 3.0, "justificacion": "simulado"})
    return llamar


def recolectar(fichas_esc: dict, fichas_puente: dict, llamar: Llamar, cache: e9.Cache,
               modelo: str) -> tuple[dict, dict]:
    respuestas, crudas = {}, {}
    for v, f in fichas_esc.items():
        u = prompt(f, fichas_puente)
        respuestas[v], crudas[v] = [], []
        for rep in range(REPETICIONES):
            texto, _ = e9.pedir(llamar, cache, modelo, TEMPERATURA, SISTEMA, u, rep)
            crudas[v].append(texto)
            respuestas[v].append(parsear(texto, f, fichas_puente))
    return respuestas, crudas


def main(argv=None, entrada=input) -> int:
    ap = argparse.ArgumentParser(description="Puente (pre-registro en docs/PUENTE_SPECIFICATION.md).")
    ap.add_argument("--simulado", action="store_true", help="modelo simulado, sin gasto")
    args = ap.parse_args(argv)
    from src.population import poblacion_epc as pe
    fichas_esc, fichas_puente = cargar_fichas()
    if len(fichas_puente) != 91:
        raise PuenteError(f"El catálogo del puente tiene {len(fichas_puente)} preguntas; la enmienda 1 dice 91.")
    donante = pe.cargar_donante()
    datos = Datos(donante, fichas_puente, fichas_esc)
    col = {c.upper(): c for c in donante.columns}
    crudos_puente = {}
    for v, f in fichas_puente.items():
        x = pd.to_numeric(donante[col[str(f["codigo"]).upper()]], errors="coerce").to_numpy(float)
        crudos_puente[v] = (x, np.isin(x, f["escala"]))
    salida = SALIDA / ("simulado" if args.simulado else "")
    cache = e9.Cache(salida / "cache.json")
    if args.simulado:
        llamar, modelo = modelo_simulado(fichas_puente), e9.MODELO_SIMULADO
    else:
        llamar, modelo = e9.cliente_real(), MODELO
        pend = [(SISTEMA, prompt(f, fichas_puente), 400) for v, f in fichas_esc.items() for rep in range(REPETICIONES)
                if e9.Cache.clave(modelo, TEMPERATURA, SISTEMA, prompt(f, fichas_puente), rep) not in cache]
        if not e9.confirmar_gasto(pend, entrada, e9.gasto_registrado(cache)):
            print("No se gastó nada.")
            return 1
    try:
        respuestas, crudas = recolectar(fichas_esc, fichas_puente, llamar, cache, modelo)
    except e9.Experimento9Error as e:
        g = e9.gasto_registrado(cache)
        print(f"\nERROR: {e}\nLas {g['llamadas']} llamadas que sí respondieron quedaron en la caché "
              f"(USD {g['costo_usd']:.3f}); al volver a correr solo se hacen las que faltan.")
        return 1
    a = analizar(datos, fichas_esc, fichas_puente, respuestas, crudos_puente)
    v = evaluar(a)
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "resultado.json").write_text(json.dumps({**a, **v, "modelo": modelo, "gasto": e9.gasto_registrado(cache)},
                                                      ensure_ascii=False, indent=2, default=float), encoding="utf-8")
    print(f"{'pregunta':8s} {'ρ_ind':>6s} {'azar95':>6s} {'demo':>6s} │ {'r_loc':>6s} {'demo':>6s} │ {'e_niv':>6s} {'ingen':>6s}")
    for k, p in a["por_pregunta"].items():
        print(f"{k:8s} {p['rho_ind']:6.2f} {p['azar']['rho_ind_p95']:6.2f} {p['demografia']['rho_ind']:6.2f} │ "
              f"{p['r_loc']:6.2f} {p['demografia']['r_loc']:6.2f} │ {p['e_nivel']:6.3f} {p['nivel']['e_ingenuo']:6.3f}")
    for k, p in v["predicciones"].items():
        print(f"  {k} {'se cumple' if p['se_cumple'] else 'NO se cumple'} — {p['umbral']} ({p['cuenta']} de 12)")
    print(f"\nOrden: {v['lectura_orden']} — {v['regla_orden']}\nNivel: {v['regla_nivel']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
