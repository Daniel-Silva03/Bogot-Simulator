"""
src/scenarios/especificacion.py

Un escenario, declarado en YAML, verificado antes de correr.

QUÉ ES UN ESCENARIO EN ESTE PROYECTO
------------------------------------
Siete experimentos pre-registrados dicen que **no hay mecanismo de dinámica
de opinión identificable** con los datos disponibles, y que dos números
exógenos por periodo —nivel y dispersión— llevan el ajuste al piso de ruido
muestral (`claude/FORZAMIENTO_CATEGORICO.md`).

Eso decide qué es un escenario aquí: **no una predicción que el modelo
genera, sino un supuesto que alguien declara y cuyas consecuencias
distribucionales el motor calcula.** El usuario dice "la confianza cae 0,15
puntos por año durante tres años"; el motor responde con la distribución
completa que eso implica, con su incertidumbre. No al revés.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-E1. **Los supuestos se declaran con incertidumbre, y es obligatorio.** Un
    escenario sin incertidumbre produce una línea determinista, y una línea
    determinista se lee como predicción — el riesgo R05 del proyecto, que
    está marcado como elevado. `incertidumbre` puede ser 0, pero hay que
    escribirlo: la decisión queda en el archivo, no en el olvido.

DI-E2. **El cambio se declara relativo al periodo anterior por defecto.** Un
    escenario es una historia sobre lo que pasa, no una lista de destinos.
    `valor:` absoluto existe para replicar una serie observada.

DI-E3. **La factibilidad se verifica al cargar, no al correr.** En una escala
    acotada no todo par (media, sd) existe. El motor podría descubrirlo en
    la corrida 137 de 200; es mejor que el archivo se rechace antes de
    empezar, nombrando el periodo y el rango alcanzable.

DI-E4. **La grilla sale de la población, no del archivo.** Es una propiedad
    de la variable medida, y dejar que un YAML la declare invita a
    inventarse una escala que los datos no tienen. Se puede sobrescribir,
    pero entonces se verifica que la población quepa en ella.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import yaml

from src.opinion.forzamiento_categorico import (
    ForzamientoInfactible, distribucion_de, momentos, rango_de_sd,
)


class EscenarioError(ValueError):
    """El escenario no está bien declarado."""


@dataclass
class Perilla:
    """Un supuesto: cuánto cambia algo, y cuánto no lo sabemos."""
    cambio: Optional[float] = None
    valor: Optional[float] = None
    incertidumbre: float = 0.0

    def __post_init__(self):
        if (self.cambio is None) == (self.valor is None):
            raise EscenarioError("Cada perilla declara 'cambio' o 'valor', exactamente uno.")
        if self.incertidumbre < 0:
            raise EscenarioError("La incertidumbre no puede ser negativa.")

    def objetivo(self, previo: float, rng: np.random.Generator, sortear: bool) -> float:
        base = previo + self.cambio if self.cambio is not None else self.valor
        if sortear and self.incertidumbre > 0:
            base = base + rng.normal(0.0, self.incertidumbre)
        return float(base)


@dataclass
class Periodo:
    etiqueta: str
    nivel: Perilla
    dispersion: Perilla


@dataclass
class Escenario:
    nombre: str
    descripcion: str
    periodos: list[Periodo]
    poblacion: np.ndarray
    grilla: np.ndarray
    etiqueta_variable: str
    corridas: int
    semilla: int
    ruta_poblacion: str
    notas: list[str] = field(default_factory=list)

    @property
    def media_inicial(self) -> float:
        return float(np.mean(self.poblacion))

    @property
    def sd_inicial(self) -> float:
        return float(np.std(self.poblacion))

    def trayectoria_central(self) -> list[tuple[str, float, float]]:
        """Los objetivos sin sortear incertidumbre: la historia que se declaró."""
        m, s = self.media_inicial, self.sd_inicial
        rng = np.random.default_rng(0)
        out = []
        for p in self.periodos:
            m = p.nivel.objetivo(m, rng, sortear=False)
            s = p.dispersion.objetivo(s, rng, sortear=False)
            out.append((p.etiqueta, m, s))
        return out


def _perilla(d, nombre, periodo) -> Perilla:
    if nombre not in d:
        raise EscenarioError(f"Al periodo '{periodo}' le falta '{nombre}'.")
    v = d[nombre]
    if not isinstance(v, dict):
        raise EscenarioError(
            f"'{nombre}' del periodo '{periodo}' tiene que ser un bloque con "
            f"'cambio' o 'valor' e 'incertidumbre' (DI-E1), no {v!r}.")
    if "incertidumbre" not in v:
        raise EscenarioError(
            f"'{nombre}' del periodo '{periodo}' no declara 'incertidumbre'. "
            "Es obligatorio, aunque sea 0: un escenario sin incertidumbre "
            "declarada se lee como predicción (DI-E1).")
    try:
        return Perilla(cambio=v.get("cambio"), valor=v.get("valor"),
                       incertidumbre=float(v["incertidumbre"]))
    except EscenarioError as e:
        raise EscenarioError(f"En '{nombre}' del periodo '{periodo}': {e}") from None


def cargar(ruta: str | Path, raiz: Optional[Path] = None) -> Escenario:
    """Lee el YAML, carga la población y verifica que el escenario sea posible."""
    ruta = Path(ruta)
    raiz = raiz or Path(__file__).resolve().parents[2]
    try:
        d = yaml.safe_load(ruta.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise EscenarioError(f"No existe el escenario {ruta}.") from None
    if not isinstance(d, dict):
        raise EscenarioError(f"{ruta} no contiene un escenario.")

    for clave in ("nombre", "poblacion", "periodos"):
        if clave not in d:
            raise EscenarioError(f"Al escenario le falta '{clave}'.")
    if not d["periodos"]:
        raise EscenarioError("El escenario no tiene periodos.")

    rp = raiz / d["poblacion"]
    if not rp.exists():
        raise EscenarioError(f"No existe la población {rp}.")
    col = d.get("columna", "opinion_t0")
    tabla = pd.read_csv(rp)
    if col not in tabla.columns:
        raise EscenarioError(f"La población {rp.name} no tiene la columna '{col}'.")
    poblacion = tabla[col].to_numpy(float)

    # DI-E4: la grilla sale de la población salvo que se declare
    if "grilla" in d:
        grilla = np.asarray(d["grilla"], dtype=float)
        fuera = np.setdiff1d(np.unique(poblacion), grilla)
        if fuera.size:
            raise EscenarioError(
                f"La población tiene valores que no están en la grilla declarada: "
                f"{list(fuera[:8])}.")
    else:
        grilla = np.unique(poblacion)
    if len(grilla) < 2:
        raise EscenarioError("La variable tiene una sola categoría; no hay nada que simular.")

    periodos = [Periodo(etiqueta=str(p.get("etiqueta", f"t{i+1}")),
                        nivel=_perilla(p, "nivel", p.get("etiqueta", f"t{i+1}")),
                        dispersion=_perilla(p, "dispersion", p.get("etiqueta", f"t{i+1}")))
                for i, p in enumerate(d["periodos"])]

    esc = Escenario(
        nombre=str(d["nombre"]),
        descripcion=str(d.get("descripcion", "")),
        periodos=periodos, poblacion=poblacion, grilla=grilla,
        etiqueta_variable=str(d.get("etiqueta_variable", col)),
        corridas=int(d.get("corridas", 200)),
        semilla=int(d.get("semilla", 42)),
        ruta_poblacion=str(d["poblacion"]),
    )
    verificar_factibilidad(esc)
    return esc


def verificar_factibilidad(esc: Escenario) -> None:
    """DI-E3: si algún periodo pide lo imposible, el archivo se rechaza ahora.

    Se verifica la trayectoria central **y** los bordes de la incertidumbre
    declarada (±2 desviaciones): de nada sirve que el centro sea factible si
    la mitad de las corridas va a caerse.
    """
    m, s = esc.media_inicial, esc.sd_inicial
    rng = np.random.default_rng(0)
    problemas = []
    for p in esc.periodos:
        m = p.nivel.objetivo(m, rng, sortear=False)
        s = p.dispersion.objetivo(s, rng, sortear=False)
        for etiqueta, mm, ss in (("central", m, s),
                                 ("borde bajo", m - 2 * p.nivel.incertidumbre,
                                  s - 2 * p.dispersion.incertidumbre),
                                 ("borde alto", m + 2 * p.nivel.incertidumbre,
                                  s + 2 * p.dispersion.incertidumbre)):
            try:
                lo, hi = rango_de_sd(esc.grilla, mm)
            except ForzamientoInfactible as e:
                problemas.append(f"periodo '{p.etiqueta}' ({etiqueta}): {e}")
                continue
            if not (lo - 1e-9 <= ss <= hi + 1e-9):
                problemas.append(
                    f"periodo '{p.etiqueta}' ({etiqueta}): con media {mm:.3f} la "
                    f"desviación alcanzable va de {lo:.3f} a {hi:.3f}, y el escenario "
                    f"pide {ss:.3f}")
    if problemas:
        raise ForzamientoInfactible(
            "El escenario pide combinaciones que la escala no admite:\n  - "
            + "\n  - ".join(problemas)
            + "\n\nEn una escala acotada, fijada la media, la desviación estándar "
              "tiene un máximo (masa en los extremos) y un mínimo (masa en las "
              "categorías vecinas). Hay que ajustar el escenario, no el motor.")
