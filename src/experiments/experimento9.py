"""
Experimento 9 — ¿un LLM puede proponer el escenario de un periodo?

Pre-registro: `docs/EXPERIMENT_9_SPECIFICATION.md`, con las enmiendas 1 a 5.
Este módulo no decide nada que el pre-registro no haya decidido: lo ejecuta.

QUÉ HACE
--------
Para cada una de las 12 transiciones medidas (ECP 4 + EPC 8):

    estado inicial (+ dossier, en el brazo B)  ->  LLM  ->  Δnivel, Δsd, intervalos
    ladeo categórico sobre la distribución inicial  ->  distribución predicha
    W1(predicha, observada final) / piso de ruido   ->  métrica principal

y lo mismo para los tres baselines («sin cambio», «tendencia», «oráculo»).
Después evalúa P1-P6 y la regla de decisión de §5, tal como están escritas, y
el control por permutación de la enmienda 5.

Tres subcomandos, en el orden del pre-registro:

    python src/experiments/experimento9.py sonda      # §3.6, antes de todo
    python src/experiments/experimento9.py brazos     # §3.2, 240 llamadas
    python src/experiments/experimento9.py evaluar    # §3.4-§5, sin red

**Sin `--real` todo corre con un modelo simulado**, sin red, y escribe en
`data/processed/exp9/simulado/`. Con `--real` usa OpenRouter, escribe en
`data/processed/exp9/`, estima el costo de lo que falta y pide confirmación
escrita antes de la primera llamada.

LO QUE ESTE SCRIPT NO HACE
--------------------------
No toca nada del CNC (R10). Al modelo solo viajan agregados de la ECP y la EPC,
que son públicas, y los dossiers de Wikipedia.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-E1. **Lo que se prueba no toca la red.** Construir mensajes, leer
    respuestas, agregar, ladear y medir son funciones puras. El modelo entra
    como parámetro `llamar(modelo, sistema, usuario, temperatura) -> str`, la
    misma firma de `donante_llm.PROVEEDORES`; el modelo simulado de las
    pruebas es cualquier función con esa firma.

DI-E2. **Caché por contenido.** `donante_llm.py` reanuda por `caso_id`, que
    aquí no existe. La clave es el sha256 de (modelo, temperatura, sistema,
    usuario, repetición): las 10 repeticiones son entradas distintas,
    reanudar no repite ninguna llamada, y cambiar un mensaje invalida sola
    la entrada que cambió. Se guarda el texto crudo, no lo parseado, para
    poder auditar lo que el modelo dijo. Un error de red **no** se guarda:
    no es una respuesta.

DI-E3. **El dossier se verifica antes de usarlo.** Se recalcula su huella
    (sha256 del archivo con finales LF, 16 caracteres, como
    `extraer_dossiers.js`) y se compara con `HUELLAS.txt`. Si no coincide, el
    script se detiene: un dossier editado invalida el pre-registro (enmienda
    3). Al modelo va solo la sección «Hechos».

DI-E4. **El modelo nunca ve el año final.** Los mensajes llevan el estado del
    año de inicio y solo el número del año final. Hay una prueba que lo
    verifica sobre los 24 mensajes.

DI-E5. **Un intervalo con los límites al revés se ordena**, no se descarta.
    Es un error de formato, no una propuesta distinta, y descartarlo
    castigaría el formato en vez del contenido. Un intervalo que falta sí
    invalida la repetición: sin él no hay cobertura (§3.4).

DI-E6. **Una media objetivo fuera de la escala se acerca al borde** (hasta
    `MARGEN_BORDE` de él) y la predicción se marca como proyectada, igual que
    una sd infactible (DI-M3s del motor). El ladeo no puede llegar a una
    distribución concentrada en un extremo; negarse a evaluar castigaría al
    modelo con un hueco en vez de con el error que cometió.

DI-E7. **Una sonda sin respuesta legible no marca memoria.** Se reintenta con
    otra repetición hasta `INTENTOS_SONDA` veces; si nunca responde, no hay
    evidencia de que recuerde, y se cuenta aparte en el veredicto.

DI-E8. **La estimación de costo es de orden de magnitud.** Tokens ≈
    caracteres / 3,5 y un precio combinado derivado del Experimento 8
    (USD 0,48 por 1.269 llamadas de ~550 tokens). El precio vigente se
    confirma en OpenRouter; la cifra sirve para decidir, no para facturar.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments.metrics import wasserstein1               # noqa: E402
from src.opinion.forzamiento_categorico import (               # noqa: E402
    ForzamientoError, distribucion_de, ladeo, momentos,
)
from src.population.ecp import ETIQUETAS_ITEMS, ITEMS_UTILES   # noqa: E402

DOSSIERS = RAIZ / "config" / "experimento9" / "dossiers"
SALIDA = RAIZ / "data" / "processed" / "exp9"

MODELO = "xiaomi/mimo-v2.6-pro"          # §6: el del Experimento 8
MODELO_SIMULADO = "simulado"
TEMPERATURA = 0.7                         # §3.1
TEMPERATURA_SONDA = 0.0                   # enmienda 4, punto 2
REPETICIONES = 10                         # §3.1
TOPE_INTENTOS = 20                        # enmienda 4, punto 6
INTENTOS_SONDA = 3                        # DI-E7
UMBRAL_MEMORIA = 0.10                     # §3.6
UMBRAL_MEMORIA_PCT = 5.0                  # enmienda 4, punto 2 (complementaria)
N_PISO, REPS_PISO, SEMILLA_PISO = 1000, 200, 20260929   # enmienda 4, punto 3
MARGEN_BORDE = 0.05                       # DI-E6
TRANSICION_SIN_SIGNO = "EPC_2022_2023"    # §2: no distinguible de cero
N_PERMUTACIONES, SEMILLA_PERMUTACION = 2000, 20260930   # enmienda 5
USD_POR_MILLON_TOKENS = 0.69              # DI-E8
TOKENS_SALIDA_BRAZO, TOKENS_SALIDA_SONDA = 350, 30

Llamar = Callable[[str, str, str, float], str]


class Experimento9Error(RuntimeError):
    """Algo impide correr el experimento como está pre-registrado."""


class DossierAlterado(Experimento9Error):
    """La huella de un dossier no coincide con HUELLAS.txt (DI-E3)."""


# --------------------------------------------------------------------------
# Las transiciones y las series (§2)

@dataclass(frozen=True)
class Transicion:
    serie: str
    inicio: int
    fin: int

    @property
    def clave(self) -> str:
        return f"{self.serie}_{self.inicio}_{self.fin}"


TRANSICIONES = tuple(Transicion(s, a, b) for s, a, b in (
    ("ECP", 2013, 2017), ("ECP", 2017, 2019), ("ECP", 2019, 2021), ("ECP", 2021, 2023),
    ("EPC", 2014, 2015), ("EPC", 2015, 2017), ("EPC", 2017, 2018), ("EPC", 2018, 2019),
    ("EPC", 2019, 2022), ("EPC", 2022, 2023), ("EPC", 2023, 2024), ("EPC", 2024, 2025),
))


def anios_de(serie: str) -> list[int]:
    ts = [t for t in TRANSICIONES if t.serie == serie]
    return [ts[0].inicio] + [t.fin for t in ts]


GRILLA_EPC = np.arange(1.0, 6.0)
#: Enmienda 4, punto 4: todas las medias de n ítems en 1-5, n de 7 a 13.
GRILLA_ECP = np.unique(np.round(
    [s / n for n in range(7, 14) for s in range(n, 5 * n + 1)], 12))

_INSTITUCIONES = "; ".join(ETIQUETAS_ITEMS[i] for i in ITEMS_UTILES)

SERIES = {
    "ECP": {
        "grilla": GRILLA_ECP,
        "fuente": "Encuesta de Cultura Política (ECP) del DANE, adultos de Bogotá",
        "variable": ("Índice de confianza institucional: para cada persona, el "
                     "promedio de su confianza en 13 instituciones (" + _INSTITUCIONES + ")."),
        "pregunta": "«¿Cuánta confianza tiene usted en cada una de las siguientes instituciones?»",
        "anclas": "1 significa que no confía y 5 que confía mucho",
    },
    "EPC": {
        "grilla": GRILLA_EPC,
        "fuente": "Encuesta de Percepción Ciudadana (EPC) de Bogotá Cómo Vamos",
        "variable": "Calificación de la gestión del alcalde o alcaldesa de Bogotá.",
        "pregunta": "«¿Cómo califica la gestión del alcalde o alcaldesa de Bogotá?»",
        "anclas": "1 es muy mala gestión y 5 muy buena gestión",
    },
}

#: §3.1, punto 3. (desde, hasta, nombre), años inclusive.
ALCALDES = ((2012, 2015, "Gustavo Petro"), (2016, 2019, "Enrique Peñalosa"),
            (2020, 2023, "Claudia López"), (2024, 2027, "Carlos Fernando Galán"))
PRESIDENTES = ((2010, 2018, "Juan Manuel Santos"), (2018, 2022, "Iván Duque"),
               (2022, 2026, "Gustavo Petro"))


def gobernantes(tabla, inicio: int, fin: int) -> str:
    return ", ".join(f"{n} ({a}–{b})" for a, b, n in tabla if a <= fin and b >= inicio)


# --------------------------------------------------------------------------
# El estado observado de cada año

@dataclass
class Estado:
    """Distribución ponderada de la variable en un año, sobre su grilla."""
    serie: str
    anio: int
    grilla: np.ndarray
    p: np.ndarray
    n: int = 0

    @property
    def media(self) -> float:
        return momentos(self.p, self.grilla)[0]

    @property
    def sd(self) -> float:
        return momentos(self.p, self.grilla)[1]

    def cuantil(self, q: float) -> float:
        return float(self.grilla[np.searchsorted(np.cumsum(self.p), q - 1e-12)])

    def proporcion_4_5(self) -> float:
        return float(self.p[self.grilla >= 4].sum())


def cargar_estados(raiz_ecp=None, raiz_epc=None) -> dict[tuple[str, int], Estado]:
    """Los 14 estados observados que usa el experimento. Lee microdatos públicos."""
    from src.population.ecp import distribucion_observada
    from src.population.epc_bcv import cargar_bcv

    estados = {}
    d = distribucion_observada(raiz_ecp or RAIZ / "data" / "raw" / "ecp", anios_de("ECP"))
    for anio, g in d.groupby("anio"):
        p = distribucion_de(g["indice"].to_numpy(float), GRILLA_ECP, g["fex"].to_numpy(float))
        estados[("ECP", int(anio))] = Estado("ECP", int(anio), GRILLA_ECP, p, len(g))
    for anio in anios_de("EPC"):
        datos = cargar_bcv(anio, raiz_epc).datos
        ok = datos["gestion_alcalde"].notna() & (datos["peso"] > 0)
        p = distribucion_de(datos.loc[ok, "gestion_alcalde"].to_numpy(float), GRILLA_EPC,
                            datos.loc[ok, "peso"].to_numpy(float))
        estados[("EPC", anio)] = Estado("EPC", anio, GRILLA_EPC, p, int(ok.sum()))
    faltan = [(t.serie, a) for t in TRANSICIONES for a in (t.inicio, t.fin)
              if (t.serie, a) not in estados]
    if faltan:
        raise Experimento9Error(f"Faltan estados observados: {sorted(set(faltan))}")
    return estados


# --------------------------------------------------------------------------
# Dossiers (DI-E3)

def huella(texto: str) -> str:
    return hashlib.sha256(texto.replace("\r\n", "\n").encode("utf-8")).hexdigest()[:16]


def hechos_del_dossier(clave: str, carpeta: Path = DOSSIERS) -> str:
    """La sección «Hechos» del dossier, después de verificar su huella."""
    esperadas = dict(linea.split() for linea in
                     (carpeta / "HUELLAS.txt").read_text(encoding="utf-8").splitlines()
                     if linea.strip())
    texto = (carpeta / f"{clave}.md").read_bytes().decode("utf-8")
    if huella(texto) != esperadas.get(clave):
        raise DossierAlterado(
            f"{clave}.md tiene huella {huella(texto)} y HUELLAS.txt dice "
            f"{esperadas.get(clave)}. El dossier no puede cambiar después del "
            "pre-registro (enmienda 3); no se sigue.")
    partes = texto.replace("\r\n", "\n").split("\n## Hechos\n", 1)
    if len(partes) != 2:
        raise Experimento9Error(f"{clave}.md no tiene sección «Hechos».")
    return partes[1].strip()


# --------------------------------------------------------------------------
# Mensajes (§3.1)

SISTEMA_BRAZO = (
    "Eres un analista de opinión pública que conoce Bogotá, Colombia. Se te da "
    "el estado de una variable de encuesta al inicio de un periodo y se te pide "
    "proponer cuánto cambió al final del periodo: su nivel (la media) y su "
    "dispersión (la desviación estándar). No se te dirá el resultado. Da tu "
    "mejor estimación y un intervalo del 90 % honesto para cada número. "
    "Devuelve únicamente un objeto JSON, sin texto alrededor."
)
SISTEMA_SONDA = "Responde únicamente con un objeto JSON, sin texto alrededor."


def _describir_estado(e: Estado) -> str:
    lineas = [f"- Media: {e.media:.2f}", f"- Desviación estándar: {e.sd:.2f}"]
    if e.serie == "EPC":
        cats = " · ".join(f"{int(k)}: {100 * q:.1f} %" for k, q in zip(e.grilla, e.p))
        lineas.append(f"- Distribución por categoría: {cats}")
    else:
        qs = " · ".join(f"P{int(100 * q)} = {e.cuantil(q):.2f}" for q in (0.2, 0.4, 0.6, 0.8))
        lineas.append(f"- Quintiles del índice: {qs}")
    return "\n".join(lineas)


def mensaje_brazo(t: Transicion, estados: dict, brazo: str,
                  hechos: Optional[str] = None) -> tuple[str, str]:
    """(sistema, usuario) para una transición y un brazo. B exige los hechos."""
    if brazo not in ("A", "B"):
        raise ValueError("brazo debe ser 'A' o 'B'")
    if brazo == "B" and not hechos:
        raise Experimento9Error("El brazo B necesita los hechos del dossier.")
    s = SERIES[t.serie]
    partes = [
        f"Encuesta: {s['fuente']}.",
        f"Variable: {s['variable']}",
        f"Pregunta: {s['pregunta']} Escala de 1 a 5, donde {s['anclas']}.",
        "",
        f"Estado en {t.inicio} (cifras ponderadas de la encuesta):",
        _describir_estado(estados[(t.serie, t.inicio)]),
        "",
        f"Periodo: de {t.inicio} a {t.fin}.",
        f"Alcaldía de Bogotá: {gobernantes(ALCALDES, t.inicio, t.fin)}.",
        f"Presidencia de Colombia: {gobernantes(PRESIDENTES, t.inicio, t.fin)}.",
    ]
    if brazo == "B":
        partes += ["", "Hechos del periodo (cronologías de Wikipedia en español):", hechos]
    partes += [
        "",
        f"Propón el cambio entre {t.inicio} y {t.fin}:",
        f"- delta_nivel: la media de {t.fin} menos la de {t.inicio}.",
        f"- delta_dispersion: la desviación estándar de {t.fin} menos la de {t.inicio}.",
        "- Un intervalo del 90 % para cada uno.",
        "",
        "Devuelve exactamente este JSON:",
        '{"delta_nivel": <número>, "intervalo_nivel": [<inferior>, <superior>], '
        '"delta_dispersion": <número>, "intervalo_dispersion": [<inferior>, <superior>], '
        '"justificacion": "<máximo 150 palabras>"}',
    ]
    return SISTEMA_BRAZO, "\n".join(partes)


def mensaje_sonda(t: Transicion) -> tuple[str, str]:
    """§3.6 / enmienda 4: la media ponderada del año final, en la escala 1-5."""
    s = SERIES[t.serie]
    return SISTEMA_SONDA, (
        f"Encuesta: {s['fuente']}, año {t.fin}.\n"
        f"Variable: {s['variable']}\n"
        f"Pregunta: {s['pregunta']} Escala de 1 a 5, donde {s['anclas']}.\n\n"
        f"¿Cuál fue la media ponderada de esta variable en Bogotá en {t.fin}, en la "
        "escala de 1 a 5? Si no la recuerdas con exactitud, da tu mejor estimación.\n"
        'Devuelve exactamente: {"media": <número>}')


def mensaje_sonda_complementaria(t: Transicion) -> tuple[str, str]:
    """Enmienda 4, no pre-registrada: el porcentaje 4-5 que publica BCV. Solo EPC."""
    if t.serie != "EPC":
        raise ValueError("La sonda complementaria solo existe para la EPC.")
    return SISTEMA_SONDA, (
        f"En la Encuesta de Percepción Ciudadana de Bogotá Cómo Vamos de {t.fin}, "
        "¿qué porcentaje de los bogotanos calificó la gestión del alcalde o "
        "alcaldesa como buena o muy buena (4 o 5 en la escala de 1 a 5)? Si no lo "
        "recuerdas con exactitud, da tu mejor estimación.\n"
        'Devuelve exactamente: {"porcentaje": <número de 0 a 100>}')


# --------------------------------------------------------------------------
# Lectura de respuestas

def _json_de(texto: Optional[str]) -> Optional[dict]:
    m = re.search(r"\{.*\}", texto or "", re.S)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    return d if isinstance(d, dict) else None


def _numero(v) -> Optional[float]:
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        x = float(v)
    elif isinstance(v, str):
        try:
            x = float(v.strip().replace(",", "."))
        except ValueError:
            return None
    else:
        return None
    return x if math.isfinite(x) else None


def _intervalo(v) -> Optional[tuple[float, float]]:
    if not isinstance(v, (list, tuple)) or len(v) != 2:
        return None
    a, b = _numero(v[0]), _numero(v[1])
    if a is None or b is None:
        return None
    return (min(a, b), max(a, b))                      # DI-E5


def parsear_propuesta(texto: Optional[str]) -> Optional[dict]:
    d = _json_de(texto)
    if d is None:
        return None
    dn, dsd = _numero(d.get("delta_nivel")), _numero(d.get("delta_dispersion"))
    icn, ics = _intervalo(d.get("intervalo_nivel")), _intervalo(d.get("intervalo_dispersion"))
    if None in (dn, dsd, icn, ics):
        return None
    just = d.get("justificacion")
    return {"delta_nivel": dn, "delta_dispersion": dsd,
            "intervalo_nivel": list(icn), "intervalo_dispersion": list(ics),
            "justificacion": just if isinstance(just, str) else ""}


def parsear_sonda(texto: Optional[str], campo: str) -> Optional[float]:
    d = _json_de(texto)
    return None if d is None else _numero(d.get(campo))


# --------------------------------------------------------------------------
# Caché y llamadas (DI-E2)

class Cache:
    def __init__(self, ruta: Path):
        self.ruta = Path(ruta)
        self.datos: dict = (json.loads(self.ruta.read_text(encoding="utf-8"))
                            if self.ruta.exists() else {})

    @staticmethod
    def clave(modelo: str, temp: float, sistema: str, usuario: str, rep: int) -> str:
        cuerpo = json.dumps([modelo, temp, sistema, usuario, rep], ensure_ascii=False)
        return hashlib.sha256(cuerpo.encode("utf-8")).hexdigest()

    def __contains__(self, clave: str) -> bool:
        return clave in self.datos

    def get(self, clave: str) -> Optional[str]:
        e = self.datos.get(clave)
        return None if e is None else e["texto"]

    def put(self, clave: str, texto: str, **meta) -> None:
        self.datos[clave] = {"texto": texto, **meta}
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.ruta.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.datos, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, self.ruta)       # un corte a medio escribir no la corrompe


def pedir(llamar: Llamar, cache: Cache, modelo: str, temp: float,
          sistema: str, usuario: str, rep: int) -> tuple[str, bool]:
    """(texto, si fue una llamada nueva). Una excepción de red se propaga sin cachear."""
    k = Cache.clave(modelo, temp, sistema, usuario, rep)
    if k in cache:
        return cache.get(k), False
    texto = llamar(modelo, sistema, usuario, temp) or ""
    cache.put(k, texto, modelo=modelo, temperatura=temp, rep=rep)
    return texto, True


def recolectar_brazo(t: Transicion, brazo: str, estados: dict, llamar: Llamar,
                     cache: Cache, modelo: str = MODELO,
                     hechos: Optional[str] = None) -> dict:
    """Pide repeticiones hasta tener REPETICIONES válidas o agotar TOPE_INTENTOS."""
    sistema, usuario = mensaje_brazo(t, estados, brazo, hechos)
    propuestas, fallos, nuevas = [], [], 0
    for rep in range(TOPE_INTENTOS):
        if len(propuestas) >= REPETICIONES:
            break
        try:
            texto, nueva = pedir(llamar, cache, modelo, TEMPERATURA, sistema, usuario, rep)
        except KeyboardInterrupt:
            raise
        except Exception as e:                           # noqa: BLE001
            fallos.append({"rep": rep, "motivo": f"{type(e).__name__}: {e}"})
            continue
        nuevas += nueva
        p = parsear_propuesta(texto)
        if p is None:
            fallos.append({"rep": rep, "motivo": "respuesta no legible", "texto": texto[:200]})
        else:
            propuestas.append({"rep": rep, **p})
    return {"clave": t.clave, "brazo": brazo, "propuestas": propuestas,
            "fallos": fallos, "llamadas_nuevas": nuevas}


def sondear(t: Transicion, estados: dict, llamar: Llamar, cache: Cache,
            modelo: str = MODELO) -> dict:
    """Sonda de memoria de una transición (§3.6, enmienda 4)."""
    def una(mensaje, campo):
        sistema, usuario = mensaje
        for rep in range(INTENTOS_SONDA):
            try:
                texto, _ = pedir(llamar, cache, modelo, TEMPERATURA_SONDA, sistema, usuario, rep)
            except KeyboardInterrupt:
                raise
            except Exception:                            # noqa: BLE001
                continue
            v = parsear_sonda(texto, campo)
            if v is not None:
                return v
        return None                                      # DI-E7

    obs = estados[(t.serie, t.fin)]
    r = una(mensaje_sonda(t), "media")
    salida = {"clave": t.clave, "respuesta_media": r, "observado_media": obs.media,
              "en_memoria": r is not None and abs(r - obs.media) < UMBRAL_MEMORIA,
              "sin_respuesta": r is None}
    if t.serie == "EPC":
        pct = una(mensaje_sonda_complementaria(t), "porcentaje")
        obs_pct = 100 * obs.proporcion_4_5()
        salida.update({"respuesta_pct_4_5": pct, "observado_pct_4_5": obs_pct,
                       "en_memoria_complementaria":
                           pct is not None and abs(pct - obs_pct) < UMBRAL_MEMORIA_PCT})
    return salida


# --------------------------------------------------------------------------
# Agregar, ladear, medir (§3.4)

def agregar(propuestas: list[dict]) -> Optional[dict]:
    """La propuesta del brazo es la mediana de las repeticiones válidas (§3.1)."""
    if not propuestas:
        return None
    col = lambda k: np.array([p[k] for p in propuestas], float)        # noqa: E731
    icn = np.array([p["intervalo_nivel"] for p in propuestas], float)
    ics = np.array([p["intervalo_dispersion"] for p in propuestas], float)
    return {
        "n_validas": len(propuestas),
        "delta_nivel": float(np.median(col("delta_nivel"))),
        "delta_dispersion": float(np.median(col("delta_dispersion"))),
        # Enmienda 4, punto 1: mediana de los límites.
        "intervalo_nivel": [float(np.median(icn[:, 0])), float(np.median(icn[:, 1]))],
        "intervalo_dispersion": [float(np.median(ics[:, 0])), float(np.median(ics[:, 1]))],
        "sd_entre_reps_nivel": float(col("delta_nivel").std()),
        "sd_entre_reps_dispersion": float(col("delta_dispersion").std()),
        "intervalos_nivel_reps": icn.tolist(),
    }


def predecir(e0: Estado, delta_nivel: float, delta_sd: float) -> tuple[np.ndarray, bool]:
    """Ladeo de la distribución inicial a los momentos propuestos. (q, proyectada)."""
    k = e0.grilla
    media = e0.media + delta_nivel
    lo, hi = float(k.min()) + MARGEN_BORDE, float(k.max()) - MARGEN_BORDE
    proyectada = not (lo <= media <= hi)
    media = float(np.clip(media, lo, hi))                # DI-E6
    sd = max(e0.sd + delta_sd, 0.0)
    try:
        res = ladeo(e0.p, k, media, sd, proyectar=True)
    except ForzamientoError as err:
        raise Experimento9Error(
            f"{e0.serie} {e0.anio}: el ladeo no pudo llegar a media {media:.3f}, "
            f"sd {sd:.3f}: {err}") from err
    return res.q, proyectada or bool(res.notas)


def w1_grilla(p: np.ndarray, q: np.ndarray, k: np.ndarray) -> float:
    """W1 exacto entre dos distribuciones sobre la misma grilla (enmienda 4, punto 3)."""
    return float(np.sum(np.abs(np.cumsum(p) - np.cumsum(q))[:-1] * np.diff(k)))


def piso_de_ruido(e: Estado, n: int = N_PISO, reps: int = REPS_PISO,
                  seed: int = SEMILLA_PISO) -> float:
    """DI-X4: W1 medio entre dos muestras de n de la misma distribución observada."""
    rng = np.random.default_rng(seed)
    return float(np.mean([wasserstein1(rng.choice(e.grilla, n, p=e.p),
                                       rng.choice(e.grilla, n, p=e.p))
                          for _ in range(reps)]))


def cambio_observado(t: Transicion, estados: dict) -> tuple[float, float]:
    a, b = estados[(t.serie, t.inicio)], estados[(t.serie, t.fin)]
    return b.media - a.media, b.sd - a.sd


def baselines(estados: dict) -> dict[str, dict[str, tuple[float, float]]]:
    """§3.5. «Tendencia» no existe para la primera transición de cada serie."""
    salida = {"sin_cambio": {}, "tendencia": {}, "oraculo": {}}
    previa: dict[str, Transicion] = {}
    for t in TRANSICIONES:
        salida["sin_cambio"][t.clave] = (0.0, 0.0)
        salida["oraculo"][t.clave] = cambio_observado(t, estados)
        if t.serie in previa:
            salida["tendencia"][t.clave] = cambio_observado(previa[t.serie], estados)
        previa[t.serie] = t
    return salida


def _fila(fuente: str, t: Transicion, estados: dict, pisos: dict, sonda: dict,
          dn: float, dsd: float, agregado: Optional[dict] = None) -> dict:
    """Una fila de evaluación. `agregado` (salida de `agregar`) solo para los brazos."""
    dn_obs, dsd_obs = cambio_observado(t, estados)
    e0, e1 = estados[(t.serie, t.inicio)], estados[(t.serie, t.fin)]
    q, proyectada = predecir(e0, dn, dsd)
    w1 = w1_grilla(q, e1.p, e0.grilla)
    s = sonda.get(t.clave, {})
    fila = {
        "fuente": fuente, "clave": t.clave, "serie": t.serie,
        "delta_nivel": dn, "delta_dispersion": dsd,
        "delta_nivel_obs": dn_obs, "delta_dispersion_obs": dsd_obs,
        "w1": w1, "piso": pisos[t.clave], "w1_piso": w1 / pisos[t.clave],
        "err_nivel": abs(dn - dn_obs), "err_dispersion": abs(dsd - dsd_obs),
        "signo_ok": (None if t.clave == TRANSICION_SIN_SIGNO
                     else bool(dn != 0 and np.sign(dn) == np.sign(dn_obs))),
        "proyectada": proyectada,
        "en_memoria": bool(s.get("en_memoria", False)),
        "en_memoria_sens": bool(s.get("en_memoria", False)
                                or s.get("en_memoria_complementaria", False)),
    }
    if agregado is not None:
        lo, hi = agregado["intervalo_nivel"]
        lo_s, hi_s = agregado["intervalo_dispersion"]
        reps = np.array(agregado["intervalos_nivel_reps"], float)
        fila.update({
            "n_validas": agregado["n_validas"],
            "cubre_nivel": bool(lo <= dn_obs <= hi),
            "cubre_dispersion": bool(lo_s <= dsd_obs <= hi_s),
            "cubiertos_reps_nivel": int(((reps[:, 0] <= dn_obs) & (dn_obs <= reps[:, 1])).sum()),
            "n_reps": len(reps),
        })
    return fila


def pisos_de(estados: dict) -> dict[str, float]:
    return {t.clave: piso_de_ruido(estados[(t.serie, t.fin)]) for t in TRANSICIONES}


def evaluar(estados: dict, brazos: dict[str, dict[str, dict]], sonda: dict[str, dict],
            pisos: Optional[dict[str, float]] = None) -> list[dict]:
    """Una fila por (fuente, transición). `brazos[brazo][clave]` es la salida de `agregar`."""
    pisos = pisos or pisos_de(estados)
    filas = []
    for b, props in brazos.items():
        for t in TRANSICIONES:
            a = props.get(t.clave)
            if a:
                filas.append(_fila(f"brazo_{b}", t, estados, pisos, sonda,
                                   a["delta_nivel"], a["delta_dispersion"], a))
    for fuente, props in baselines(estados).items():
        for t in TRANSICIONES:
            if t.clave in props:
                filas.append(_fila(fuente, t, estados, pisos, sonda, *props[t.clave]))
    return filas


def control_permutacion(estados: dict, agregados: dict[str, dict], sonda: dict,
                        pisos: dict, brazo: str, n: int = N_PERMUTACIONES,
                        seed: int = SEMILLA_PERMUTACION) -> dict:
    """Enmienda 5: las propuestas del brazo, reasignadas entre transiciones de la misma serie.

    Cada par (transición destino, propuesta de origen) se evalúa una sola vez;
    una permutación solo vuelve a armar filas ya calculadas.
    """
    fuente = f"brazo_{brazo}"
    claves = [t.clave for t in TRANSICIONES if agregados.get(t.clave)]
    por_serie = {s: [c for c in claves if c.startswith(s)] for s in SERIES}
    por_clave = {t.clave: t for t in TRANSICIONES}
    base = evaluar(estados, {}, sonda, pisos)          # los baselines no se permutan
    par = {}
    for s, cs in por_serie.items():
        for destino in cs:
            for origen in cs:
                a = agregados[origen]
                par[(destino, origen)] = _fila(fuente, por_clave[destino], estados, pisos, sonda,
                                               a["delta_nivel"], a["delta_dispersion"], a)
    observado = _mediana([par[(c, c)] for c in claves])
    rng = np.random.default_rng(seed)
    menores = c1 = adoptadas = 0
    for _ in range(n):
        filas = list(base)
        for cs in por_serie.values():
            for destino, origen in zip(cs, rng.permutation(cs)):
                filas.append(par[(destino, origen)])
        r = resumen(filas, fuente)
        menores += _mediana(_de(filas, fuente)) <= observado
        c1 += r["regla"]["c1"]
        adoptadas += r["regla"]["veredicto"].startswith("Pasa las tres")
    p = menores / n
    return {
        "n_permutaciones": n, "mediana_w1_piso_brazo": round(observado, 4),
        "p": round(p, 4),
        "fraccion_que_pasa_c1": round(c1 / n, 4),
        "fraccion_que_se_adoptaria": round(adoptadas / n, 4),
        "lectura": ("La ventaja del brazo no se distingue de proponer las mismas cifras en "
                    "otro periodo de la misma serie." if p > 0.05 else
                    "La propuesta del brazo depende del periodo: permutarla la empeora."),
    }


# --------------------------------------------------------------------------
# Predicciones y regla de decisión (§4, §5)

def _de(filas, fuente, claves=None, memoria=None, campo_memoria="en_memoria"):
    return [f for f in filas if f["fuente"] == fuente
            and (claves is None or f["clave"] in claves)
            and (memoria is None or f[campo_memoria] == memoria)]


def _mediana(filas, campo="w1_piso") -> Optional[float]:
    v = [f[campo] for f in filas]
    return float(np.median(v)) if v else None


def _rango(filas, campo="w1_piso") -> dict:
    v = [f[campo] for f in filas]
    if not v:
        return {"n": 0}
    return {"mediana": round(float(np.median(v)), 4), "min": round(float(min(v)), 4),
            "max": round(float(max(v)), 4), "n": len(v)}


def _memoria(filas, brazo, campo):
    """P6 y criterio 3 con una definición de memoria dada."""
    fuera_b = _de(filas, brazo, memoria=False, campo_memoria=campo)
    if not fuera_b:
        return {"n_fuera": 0, "P6_se_cumple": None, "c3": None}
    claves = {f["clave"] for f in fuera_b}
    mb, ms = _mediana(fuera_b), _mediana(_de(filas, "sin_cambio", claves))
    return {"n_fuera": len(claves), "w1_piso_brazo": round(mb, 4),
            "w1_piso_sin_cambio": round(ms, 4),
            "P6_se_cumple": bool(mb >= ms),        # «no le gana»
            "c3": bool(mb <= ms)}                  # «no es peor»


def resumen(filas: list[dict], brazo: str = "brazo_B") -> dict:
    """Evalúa P1-P6 y la regla de §5 para un brazo (el pre-registro juzga el B)."""
    b = _de(filas, brazo)
    if not b:
        raise Experimento9Error(f"No hay filas de {brazo}.")
    todas = {f["clave"] for f in b}
    comunes = todas & {f["clave"] for f in _de(filas, "tendencia")}

    signos = [f["signo_ok"] for f in b if f["signo_ok"] is not None]
    med_b, med_s = _mediana(b), _mediana(_de(filas, "sin_cambio", todas))
    med_b_c, med_t_c = _mediana(_de(filas, brazo, comunes)), _mediana(_de(filas, "tendencia", comunes))
    mejora_t = (med_t_c - med_b_c) / med_t_c
    err_sd_b, err_sd_s = (_mediana(b, "err_dispersion"),
                          _mediana(_de(filas, "sin_cambio", todas), "err_dispersion"))
    cob = float(np.mean([f["cubre_nivel"] for f in b]))
    mem = _memoria(filas, brazo, "en_memoria")

    pred = {
        "P1": {"umbral": f"signo correcto en ≥ 8 de {len(signos)}",
               "valor": sum(signos), "se_cumple": sum(signos) >= 8},
        "P2": {"umbral": "mediana W1/piso < la de «sin cambio»",
               "valor": [round(med_b, 4), round(med_s, 4)], "se_cumple": med_b < med_s},
        "P3": {"umbral": f"mejora sobre «tendencia» < 20 % ({len(comunes)} comunes)",
               "valor": round(mejora_t, 4), "se_cumple": mejora_t < 0.20},
        "P4": {"umbral": "error mediano de dispersión ≥ el de «sin cambio»",
               "valor": [round(err_sd_b, 4), round(err_sd_s, 4)], "se_cumple": err_sd_b >= err_sd_s},
        "P5": {"umbral": "cobertura del nivel < 70 %",
               "valor": round(cob, 4), "se_cumple": cob < 0.70},
        "P6": {"umbral": "fuera de memoria, no le gana a «sin cambio»",
               "valor": mem, "se_cumple": mem["P6_se_cumple"]},
    }

    c1 = bool(med_b <= 0.8 * med_s and med_b_c <= 0.9 * med_t_c)
    c2 = bool(cob >= 0.70)
    c3 = mem["c3"]
    if not c1:
        veredicto = ("Falla 1: el LLM no aporta números. Se puede usar para redactar la "
                     "descripción de un escenario, nunca para fijar sus cifras.")
    elif not c2:
        veredicto = ("Pasa 1, falla 2: puede proponer la dirección y el tamaño central; "
                     "la incertidumbre la fija una persona.")
    elif c3 is None:
        veredicto = ("Pasa 1 y 2, pero no queda ninguna transición fuera de memoria: el "
                     "experimento no puede distinguir lectura de memoria. No se adopta.")
    elif not c3:
        veredicto = ("Pasa 1 y 2, falla 3: el resultado es memoria. Sirve para reconstruir "
                     "el pasado, no para escenarios nuevos. No se adopta.")
    else:
        veredicto = ("Pasa las tres: se adopta como asistente para proponer escenarios; "
                     "la propuesta siempre la revisa una persona antes de correrla.")

    b_filas = [f for f in b if "n_reps" in f]
    return {
        "brazo": brazo,
        "predicciones": pred,
        "regla": {"c1": c1, "c1_detalle": {"mediana_brazo": round(med_b, 4),
                                           "mediana_sin_cambio": round(med_s, 4),
                                           "mediana_brazo_comunes": round(med_b_c, 4),
                                           "mediana_tendencia_comunes": round(med_t_c, 4)},
                  "c2": c2, "c3": c3, "veredicto": veredicto},
        "secundarias": {
            "cobertura_dispersion": round(float(np.mean([f["cubre_dispersion"] for f in b])), 4),
            "cobertura_por_repeticion": round(
                sum(f["cubiertos_reps_nivel"] for f in b_filas)
                / max(sum(f["n_reps"] for f in b_filas), 1), 4),
            "proyectadas": sum(f["proyectada"] for f in b),
            "repeticiones_validas_min": min(f["n_validas"] for f in b_filas) if b_filas else None,
        },
        "sensibilidad_memoria_no_preregistrada": _memoria(filas, brazo, "en_memoria_sens"),
    }


def veredicto_completo(filas: list[dict], sonda: dict, meta: dict,
                       control: Optional[dict] = None) -> dict:
    fuentes = sorted({f["fuente"] for f in filas})
    return {
        **meta,
        "memoria": {
            "en_memoria": sorted(c for c, s in sonda.items() if s.get("en_memoria")),
            "en_memoria_complementaria": sorted(
                c for c, s in sonda.items() if s.get("en_memoria_complementaria")),
            "sondas_sin_respuesta": sorted(c for c, s in sonda.items() if s.get("sin_respuesta")),
        },
        "w1_piso": {f: {"total": _rango(_de(filas, f)),
                        **{s: _rango([x for x in _de(filas, f) if x["serie"] == s])
                           for s in SERIES}}
                    for f in fuentes},
        "brazo_B": resumen(filas, "brazo_B") if _de(filas, "brazo_B") else None,
        "brazo_A": resumen(filas, "brazo_A") if _de(filas, "brazo_A") else None,
        "control_permutacion_enmienda_5": control or {},
    }


# --------------------------------------------------------------------------
# Modelo simulado y cliente real

def modelo_simulado(semilla: int = 0) -> Llamar:
    """Un modelo sin conocimiento: propone cambios al azar. Para correr sin red."""
    rng = np.random.default_rng(semilla)

    def llamar(modelo, sistema, usuario, temp):
        if sistema == SISTEMA_SONDA:
            return '{"porcentaje": 40}' if "porcentaje" in usuario else '{"media": 3.0}'
        dn, dsd = rng.normal(0, 0.2), rng.normal(0, 0.05)
        return json.dumps({"delta_nivel": dn, "intervalo_nivel": [dn - 0.3, dn + 0.3],
                           "delta_dispersion": dsd, "intervalo_dispersion": [dsd - 0.1, dsd + 0.1],
                           "justificacion": "simulado"})
    return llamar


def cliente_real() -> Llamar:
    clave = (os.environ.get("OPENROUTER_API_KEY") or "").strip()
    if not clave:
        raise Experimento9Error('Falta OPENROUTER_API_KEY.  PowerShell:  $env:OPENROUTER_API_KEY = "..."')
    from src.experiments.donante_llm import llamar_openrouter
    return llamar_openrouter


def estimar_costo(pendientes: list[tuple[str, str, int]]) -> tuple[int, float]:
    """(tokens, USD) de las llamadas pendientes: (sistema, usuario, tokens_salida). DI-E8."""
    tokens = sum(int((len(s) + len(u)) / 3.5) + salida for s, u, salida in pendientes)
    return tokens, tokens * USD_POR_MILLON_TOKENS / 1e6


def confirmar_gasto(pendientes: list[tuple[str, str, int]], entrada=input) -> bool:
    if not pendientes:
        return True
    tokens, usd = estimar_costo(pendientes)
    print(f"\nLlamadas reales pendientes: {len(pendientes)} (sin contar reintentos)\n"
          f"Tokens estimados: {tokens:,}  ·  costo estimado: USD {usd:.2f} "
          f"(orden de magnitud; precio del Exp. 8, confirmar en OpenRouter)")
    try:
        return entrada("¿Gastar estas llamadas? Escribe «si» para seguir: ").strip().lower() in ("si", "sí")
    except EOFError:
        return False


# --------------------------------------------------------------------------
# Línea de comandos

def _escribir(ruta: Path, datos) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")


def _mostrar(ruta: Path) -> str:
    return (ruta.relative_to(RAIZ) if ruta.is_relative_to(RAIZ) else ruta).as_posix()


def _leer(ruta: Path):
    if not ruta.exists():
        raise Experimento9Error(f"Falta {_mostrar(ruta)}: corre antes el paso que lo produce.")
    return json.loads(ruta.read_text(encoding="utf-8"))


def correr_sonda(estados, llamar, cache, modelo, salida: Path, entrada=input) -> Optional[dict]:
    pend = []
    for t in TRANSICIONES:
        mensajes = [mensaje_sonda(t)] + ([mensaje_sonda_complementaria(t)] if t.serie == "EPC" else [])
        pend += [(s, u, TOKENS_SALIDA_SONDA) for s, u in mensajes
                 if Cache.clave(modelo, TEMPERATURA_SONDA, s, u, 0) not in cache]
    if modelo != MODELO_SIMULADO and not confirmar_gasto(pend, entrada):
        print("Cancelado: no se hizo ninguna llamada.")
        return None
    sonda = {t.clave: sondear(t, estados, llamar, cache, modelo) for t in TRANSICIONES}
    _escribir(salida / "sonda.json", sonda)
    for c, s in sonda.items():
        marca = "EN MEMORIA" if s["en_memoria"] else ("sin respuesta" if s["sin_respuesta"] else "fuera")
        print(f"  {c:15s} {marca}")
    return sonda


def correr_brazos(estados, llamar, cache, modelo, salida: Path, brazos=("A", "B"),
                  entrada=input) -> Optional[dict]:
    if modelo != MODELO_SIMULADO:
        _leer(salida / "sonda.json")         # §3.6: la sonda va antes del experimento
    hechos = {t.clave: hechos_del_dossier(t.clave) for t in TRANSICIONES} if "B" in brazos else {}
    pend = []
    for t in TRANSICIONES:
        for b in brazos:
            s, u = mensaje_brazo(t, estados, b, hechos.get(t.clave))
            pend += [(s, u, TOKENS_SALIDA_BRAZO) for rep in range(REPETICIONES)
                     if Cache.clave(modelo, TEMPERATURA, s, u, rep) not in cache]
    if modelo != MODELO_SIMULADO and not confirmar_gasto(pend, entrada):
        print("Cancelado: no se hizo ninguna llamada.")
        return None
    previo = json.loads((salida / "brazos.json").read_text(encoding="utf-8")) \
        if (salida / "brazos.json").exists() else {}
    for b in brazos:
        previo[b] = {}
        for t in TRANSICIONES:
            r = recolectar_brazo(t, b, estados, llamar, cache, modelo, hechos.get(t.clave))
            previo[b][t.clave] = r
            _escribir(salida / "brazos.json", previo)
            print(f"  brazo {b} {t.clave:15s} válidas {len(r['propuestas'])}  "
                  f"fallos {len(r['fallos'])}  nuevas {r['llamadas_nuevas']}")
    return previo


def correr_evaluacion(estados, salida: Path, meta: dict) -> dict:
    sonda = _leer(salida / "sonda.json")
    crudo = _leer(salida / "brazos.json")
    brazos = {b: {c: agregar(r["propuestas"]) for c, r in por_t.items()}
              for b, por_t in crudo.items()}
    pisos = pisos_de(estados)
    filas = evaluar(estados, brazos, sonda, pisos)
    import pandas as pd
    pd.DataFrame(filas).to_csv(salida / "tabla.csv", index=False)
    control = {f"brazo_{b}": control_permutacion(estados, ag, sonda, pisos, b)
               for b, ag in brazos.items() if any(ag.values())}
    v = veredicto_completo(filas, sonda, meta, control)
    _escribir(salida / "veredicto.json", v)
    return v


def main(argv=None, entrada=input) -> int:
    ap = argparse.ArgumentParser(description="Experimento 9 (pre-registro en docs/).")
    ap.add_argument("paso", choices=("sonda", "brazos", "evaluar", "todo"))
    ap.add_argument("--real", action="store_true",
                    help="llamar a OpenRouter de verdad (pide confirmar el costo)")
    ap.add_argument("--brazo", choices=("A", "B"), help="solo un brazo")
    ap.add_argument("--salida", type=Path, default=None)
    args = ap.parse_args(argv)
    if args.real and args.paso == "todo":
        print("Con --real los pasos se corren uno a uno: sonda, brazos, evaluar.")
        return 1

    salida = args.salida or (SALIDA if args.real else SALIDA / "simulado")
    modelo = MODELO if args.real else MODELO_SIMULADO
    try:
        llamar = cliente_real() if args.real else modelo_simulado()
        cache = Cache(salida / "cache.json")
        print(f"Experimento 9 · {args.paso} · modelo {modelo} · salida {_mostrar(salida)}")
        estados = cargar_estados()
        if args.paso in ("sonda", "todo"):
            if correr_sonda(estados, llamar, cache, modelo, salida, entrada) is None:
                return 1
        if args.paso in ("brazos", "todo"):
            brazos = (args.brazo,) if args.brazo else ("A", "B")
            if correr_brazos(estados, llamar, cache, modelo, salida, brazos, entrada) is None:
                return 1
        if args.paso in ("evaluar", "todo"):
            v = correr_evaluacion(estados, salida, {"modelo": modelo, "simulado": not args.real})
            for b in ("brazo_B", "brazo_A"):
                if v[b]:
                    print(f"\n{b}: {v[b]['regla']['veredicto']}")
                    for k, p in v[b]["predicciones"].items():
                        estado = {True: "se cumple", False: "NO se cumple",
                                  None: "no evaluable"}[p["se_cumple"]]
                        print(f"  {k} {estado} — {p['umbral']}")
                    c = v["control_permutacion_enmienda_5"].get(b)
                    if c:
                        print(f"  Control por permutación (enmienda 5): p = {c['p']:.3f}. {c['lectura']}")
            print(f"\n{_mostrar(salida / 'veredicto.json')}")
    except Experimento9Error as e:
        print(f"ERROR: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
