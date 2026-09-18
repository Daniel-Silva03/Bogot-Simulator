"""
src/scenarios/motor.py

Ejecuta un escenario: supuestos declarados -> distribuciones con incertidumbre.

Cada corrida repite tres sorteos independientes y la salida son **cuantiles
entre corridas**, nunca una línea. El proyecto tiene marcado como riesgo
elevado (R05) que los escenarios se lean como predicciones, y una línea
determinista es exactamente eso.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-M1s. **Tres fuentes de incertidumbre, y se separan.** Una corrida sortea:
    (a) la **población**, remuestreando N agentes con reemplazo de la base —
    es el error muestral, el mismo que fija el piso de ruido contra el que
    se validó todo; (b) los **supuestos**, de las incertidumbres declaradas
    en el YAML; (c) el **reparto** de agentes dentro de las categorías.
    `descomponer()` corre el escenario apagando una a la vez, para poder
    decir cuánta de la incertidumbre total viene de no saber el supuesto y
    cuánta de tener mil agentes y no un millón. Si domina la muestral, la
    respuesta no es afinar el supuesto: es subir N.

DI-M2s. **El escenario nulo se corre siempre.** Es el mismo escenario con
    todos los cambios en cero: la población se queda quieta, con su propia
    incertidumbre muestral. Ninguna cifra de un escenario significa nada sin
    él al lado, porque la pregunta útil nunca es "¿cuánto da?" sino "¿cuánto
    más que no hacer nada?".

DI-M3s. **Una corrida que pide lo imposible no se descarta en silencio.** Si
    el sorteo de supuestos cae fuera de lo que la escala admite, se proyecta
    al borde alcanzable y **se cuenta**. `Resultado.corridas_proyectadas` va
    en el informe: si es alto, el escenario está pegado al techo de la
    escala y las colas de los cuantiles están comprimidas artificialmente.

DI-M4s. **El forzamiento es el ladeo categórico**, no el afín. La razón está
    medida en `claude/FORZAMIENTO_CATEGORICO.md`: el afín saca la
    distribución del soporte de la variable y multiplica el error por tres a
    seis veces. Usar el afín aquí produciría escenarios en los que la gente
    responde 2,37 en una escala de cinco opciones.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from src.opinion.forzamiento_categorico import (
    ForzamientoInfactible, distribucion_de, forzar, momentos,
)
from src.scenarios.especificacion import Escenario

CUANTILES = (0.05, 0.25, 0.50, 0.75, 0.95)


@dataclass
class Resultado:
    escenario: str
    etiquetas: list[str]
    medias: np.ndarray          # corridas x periodos
    desviaciones: np.ndarray
    distribuciones: np.ndarray  # corridas x periodos x categorías
    grilla: np.ndarray
    media_inicial: float
    sd_inicial: float
    corridas_proyectadas: int = 0
    notas: list[str] = field(default_factory=list)

    def resumen(self) -> pd.DataFrame:
        filas = []
        for j, et in enumerate(self.etiquetas):
            f = {"periodo": et, "media": float(np.mean(self.medias[:, j])),
                 "sd_entre_corridas": float(np.std(self.medias[:, j])),
                 "dispersion": float(np.mean(self.desviaciones[:, j]))}
            for q in CUANTILES:
                f[f"p{int(q*100):02d}"] = float(np.quantile(self.medias[:, j], q))
            filas.append(f)
        return pd.DataFrame(filas)

    def distribucion_media(self, periodo: int = -1) -> pd.DataFrame:
        d = self.distribuciones[:, periodo, :]
        return pd.DataFrame({
            "categoria": self.grilla,
            "proporcion": d.mean(axis=0),
            "p05": np.quantile(d, 0.05, axis=0),
            "p95": np.quantile(d, 0.95, axis=0),
        })


def _una_corrida(esc: Escenario, rng, sortear_poblacion: bool,
                 sortear_supuestos: bool) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    a = (rng.choice(esc.poblacion, size=len(esc.poblacion), replace=True)
         if sortear_poblacion else esc.poblacion.copy())
    m, s = float(a.mean()), float(a.std())
    medias, sds, dists, proyectadas = [], [], [], 0
    for p in esc.periodos:
        m = p.nivel.objetivo(m, rng, sortear=sortear_supuestos)
        s = p.dispersion.objetivo(s, rng, sortear=sortear_supuestos)
        try:
            a, res = forzar(a, esc.grilla, m, s, metodo="ladeo",
                            modo="rango", proyectar=True, rng=rng)
        except ForzamientoInfactible:
            # DI-M3s: ni proyectando se puede; la corrida se detiene aquí.
            break
        if res.notas:
            proyectadas += 1
        m, s = float(a.mean()), float(a.std())
        medias.append(m)
        sds.append(s)
        dists.append(distribucion_de(a, esc.grilla))
    return np.array(medias), np.array(sds), np.array(dists), proyectadas


def correr(esc: Escenario, sortear_poblacion: bool = True,
           sortear_supuestos: bool = True, corridas: Optional[int] = None,
           progreso: bool = False) -> Resultado:
    n = corridas or esc.corridas
    M, S, D, proy = [], [], [], 0
    esperado = len(esc.periodos)
    descartadas = 0
    for i in range(n):
        rng = np.random.default_rng(esc.semilla + 7919 * i)
        m, s, d, p = _una_corrida(esc, rng, sortear_poblacion, sortear_supuestos)
        if len(m) < esperado:
            descartadas += 1
            continue
        M.append(m); S.append(s); D.append(d); proy += p
        if progreso and (i + 1) % 25 == 0:
            print(f"\r  {i+1}/{n}", end="", flush=True)
    if progreso:
        print()
    if not M:
        raise ForzamientoInfactible(
            "Ninguna corrida completó todos los periodos: el escenario pide "
            "combinaciones que la escala no admite ni proyectando.")
    notas = []
    if descartadas:
        notas.append(f"{descartadas} de {n} corridas no completaron todos los "
                     "periodos y se descartaron (DI-M3s).")
    return Resultado(
        escenario=esc.nombre, etiquetas=[p.etiqueta for p in esc.periodos],
        medias=np.vstack(M), desviaciones=np.vstack(S), distribuciones=np.stack(D),
        grilla=esc.grilla, media_inicial=esc.media_inicial, sd_inicial=esc.sd_inicial,
        corridas_proyectadas=proy, notas=notas)


def escenario_nulo(esc: Escenario) -> Escenario:
    """El mismo escenario sin ningún cambio: la referencia obligatoria (DI-M2s)."""
    import copy
    nulo = copy.deepcopy(esc)
    nulo.nombre = "Sin cambios (referencia)"
    nulo.descripcion = ("La población se queda quieta. Solo incertidumbre muestral. "
                        "Es contra esto que se lee cualquier escenario.")
    for p in nulo.periodos:
        p.nivel.cambio, p.nivel.valor, p.nivel.incertidumbre = 0.0, None, 0.0
        p.dispersion.cambio, p.dispersion.valor, p.dispersion.incertidumbre = 0.0, None, 0.0
    return nulo


def descomponer(esc: Escenario, corridas: Optional[int] = None) -> pd.DataFrame:
    """¿Cuánta incertidumbre viene del supuesto y cuánta de la muestra? (DI-M1s)"""
    n = corridas or min(esc.corridas, 120)
    filas = []
    for etiqueta, sp, ss in (("total", True, True),
                             ("solo muestral", True, False),
                             ("solo del supuesto", False, True),
                             ("ninguna (determinista)", False, False)):
        r = correr(esc, sortear_poblacion=sp, sortear_supuestos=ss, corridas=n)
        filas.append({"fuente": etiqueta,
                      "sd_de_la_media_final": float(np.std(r.medias[:, -1])),
                      "media_final": float(np.mean(r.medias[:, -1]))})
    t = pd.DataFrame(filas)
    total = t.loc[t.fuente == "total", "sd_de_la_media_final"].iloc[0]
    t["porcentaje_de_la_total"] = (t.sd_de_la_media_final / total * 100).round(1) if total > 0 else np.nan
    return t


def comparar_con_nulo(esc: Escenario, corridas: Optional[int] = None) -> pd.DataFrame:
    """La tabla que el informe pone primero: cuánto más que no hacer nada."""
    r = correr(esc, corridas=corridas)
    rn = correr(escenario_nulo(esc), corridas=corridas)
    filas = []
    for j, et in enumerate(r.etiquetas):
        a, b = rn.medias[:, j], r.medias[:, j]
        dif = b.mean() - a.mean()
        ee = float(np.sqrt(np.var(a) + np.var(b)))
        filas.append({"periodo": et, "escenario": float(b.mean()),
                      "sin_cambios": float(a.mean()), "diferencia": float(dif),
                      "ee_de_la_diferencia": ee,
                      "veces_el_error": float(abs(dif) / ee) if ee > 0 else np.nan})
    return pd.DataFrame(filas)
