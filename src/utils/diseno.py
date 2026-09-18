"""
src/utils/diseno.py

Estimación con diseño muestral complejo — medias, diferencias y efecto de
diseño. Resuelve A19.

POR QUÉ EXISTE
--------------
El proyecto venía calculando **medias ponderadas ingenuas** en todas partes
y reportando diferencias entre olas sin intervalo. Con un diseño por
conglomerados eso subestima el error estándar por un factor del orden de
sqrt(DEFF), y con el DEFF medido aquí —1,4 a 2,7 en la EPC— el error real
es entre 1,2 y 1,6 veces el que se venía usando.

Importa porque el proyecto **decide cosas** con esas diferencias: qué
transiciones son "movimientos reales" que un modelo tiene que reproducir y
cuáles son ruido. Una transición de −0,093 con un error estándar de 0,07 no
es un fenómeno; es una lectura.

QUÉ SE PUEDE Y QUÉ NO, CON LOS DATOS DE ESTE PROYECTO
------------------------------------------------------
**ECP (DANE) — no se puede.** Los microdatos publican `FEX_P` y `REGION` y
nada más: ni estrato de muestreo, ni UPM, ni pesos replicados. Verificado en
las cinco olas (2013, 2017, 2019, 2021, 2023). Sin identificador de
conglomerado no hay linealización posible, y eso es una limitación de la
fuente, no del código. Para la ECP lo único honesto es inflar el error por
un DEFF **prestado** y decir que es prestado (ver `deff_prestado`).

**EPC (Bogotá Cómo Vamos) — se puede en seis olas.** Ver
`CONGLOMERADO_POR_ANIO`. 2016, 2017, 2022 y 2025 no traen identificador de
conglomerado y caen al mismo camino que la ECP.

*(Corrección del 18/09/2026: la primera versión de este módulo decía cuatro
olas. Eran seis — 2015 y 2018 también traen `MANZANA` y no los revisé, los
señaló el equipo técnico de BCV. El escaneo original cubrió una muestra de
años, no todos.)*

DECISIONES DE IMPLEMENTACIÓN
============================

DI-D1. **Se implementa aparte y no se copia `svy_prop` del CNC.** Tres
    razones, en orden de peso: (1) la librería del CNC estima
    **proporciones** y lo que este proyecto necesita son **medias y
    diferencias de medias**, que es otra linealización; (2) la ECP, que es
    la serie principal de validación, no trae variables de diseño, así que
    la librería no se le podría aplicar de todos modos; (3) meter código
    interno del CNC en un repositorio que puede compartirse es una decisión
    de atribución que no corresponde tomar aquí. La librería del CNC sigue
    siendo la referencia contra la cual comparar si alguna vez hace falta
    una proporción.

DI-D2. **Linealización de Taylor sobre el estimador de razón.** La media
    ponderada es una razón, y su residuo linealizado es
    z_i = w_i (y_i − ȳ_w) / Σw. La varianza se acumula **entre UPM dentro
    de cada estrato**, con el factor n_h/(n_h−1). Es el estimador estándar
    con reemplazo: ignora la corrección por población finita, lo que lo
    hace **conservador** — sobreestima levemente el error. Preferible al
    revés.

DI-D3. **Los estratos con una sola UPM ("lonely PSU") no se descartan en
    silencio.** Por defecto se centran en la media global de los residuos
    en vez de omitirse, que es la opción conservadora de Stata
    (`singleunit(centered)`), y el resultado reporta cuántos hubo. Omitirlos
    subestima la varianza; abortar sería inútil porque es una situación
    normal en diseños con muchos estratos.

DI-D4. **El DEFF se calcula contra la varianza de la media ponderada bajo
    muestreo aleatorio simple con los mismos pesos**, `s²_w / n`. Hay otras
    definiciones (la de Kish separa el efecto de los pesos del efecto del
    conglomerado); esta es la que responde la pregunta que importa aquí —
    *¿cuánto me estoy equivocando al reportar el error como si la muestra
    fuera aleatoria simple?*— y es la que hay que usar para inflar los
    errores de la ECP.

DI-D6. **Un proxy de conglomerado armado con localidad × estrato NO sirve, y
    está medido.** Es la salida natural para las olas sin identificador, y la
    que propuso el propio equipo de BCV. Se validó donde se puede validar: en
    las seis olas que SÍ traen manzana, se calculó el DEFF con la manzana y
    con el proxy. El proxy **infla el DEFF por un factor mediano de 1,94**
    (rango 0,87 a 3,16).

    La razón es estructural, no de ajuste: localidad × estrato es mucho más
    plausiblemente la **estratificación** que la conglomeración, y tratar un
    estrato como conglomerado cuenta como variabilidad de muestreo lo que en
    realidad son diferencias sistemáticas entre estratos — que un diseño
    estratificado precisamente elimina. El error es conservador pero grande y
    errático, así que no es aceptable.

    Lo mismo pasa con `Zona + SEG_1` en 2025: da DEFF 4,94, casi el doble del
    techo observado en las olas con manzana. Para las olas sin identificador
    la salida honesta es el **DEFF prestado**, no un proxy inventado.

    Evidencia en `data/processed/validacion_proxy_conglomerado.csv`.

DI-D5. **Las diferencias entre olas se tratan como independientes.** La EPC
    y la ECP son cortes transversales distintos, sin panel: no hay
    covarianza que restar. Var(a − b) = Var(a) + Var(b).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence

import numpy as np
import pandas as pd

Z_95 = 1.959963984540054

#: Identificador de conglomerado y de estrato por ola de la EPC. Confirmado
#: contra los microdatos; los años ausentes no traen ninguno (DI-D6).
CONGLOMERADO_POR_ANIO = {
    2014: ("MANZANA", "GRUPO_ESTRATOS"),
    2015: ("MANZANA", "D1_ORIGINAL"),
    2018: ("MANZANA", "NSE"),
    2019: ("MANZANA", "LOCALIDAD_COMUNA"),
    2023: ("Manzana", "CS0A"),
    2024: ("Manzana", "Localidad"),
}

#: Años de la EPC sin identificador de conglomerado, con lo que hay en su lugar.
SIN_CONGLOMERADO = {
    2016: "no hay identificador; la firma de campo cambió ese año",
    2017: "no hay identificador; misma firma que 2016",
    2022: "solo `BARRIO_ENC`, demasiado fino para ser la unidad de muestreo",
    2025: "hay `SEG_*`, pero ninguna combinación reproduce el rango de DEFF de las olas con manzana",
}

#: DEFF medido sobre la EPC (§DI-D1) para los ítems de evaluación
#: institucional. Es el que hay que usar como factor prestado cuando la
#: fuente no trae variables de diseño — diciendo que es prestado.
#: 11 mediciones sobre 6 olas (antes: 8 sobre 4; la mediana se movió de 1,95
#: a 1,86, lo que da cierta confianza en el factor).
DEFF_MEDIDO_EPC = {
    "minimo": 1.39, "mediana": 1.86, "maximo": 2.69,
    "olas": tuple(sorted(CONGLOMERADO_POR_ANIO)),
    "items": ("gestion_alcalde", "gestion_concejo"),
    "mediciones": 11,
}


class DisenoError(ValueError):
    """Los insumos no permiten una estimación con diseño."""


@dataclass
class Estimacion:
    media: float
    ee: float                  # error estándar con diseño (o SRS si no hay UPM)
    ee_srs: float              # el que el proyecto venía usando
    deff: float
    n: int
    n_psu: Optional[int] = None
    n_estratos: Optional[int] = None
    psu_solitarias: int = 0
    con_diseno: bool = True
    notas: list[str] = field(default_factory=list)

    @property
    def ic95(self) -> tuple[float, float]:
        return (self.media - Z_95 * self.ee, self.media + Z_95 * self.ee)

    def __str__(self) -> str:
        lo, hi = self.ic95
        marca = "" if self.con_diseno else "  [SIN diseño: es el error SRS]"
        return (f"{self.media:.4f}  ee {self.ee:.4f}  IC95 [{lo:.4f}, {hi:.4f}]  "
                f"DEFF {self.deff:.2f}  n {self.n}{marca}")


def _limpiar(y, w, psu, estrato):
    y = pd.to_numeric(pd.Series(y), errors="coerce").to_numpy(float)
    w = pd.to_numeric(pd.Series(w), errors="coerce").to_numpy(float)
    ok = np.isfinite(y) & np.isfinite(w) & (w > 0)
    if ok.sum() == 0:
        raise DisenoError("No queda ninguna observación con valor y peso válidos.")
    psu = None if psu is None else pd.Series(psu).astype(str).to_numpy()[ok]
    estrato = (np.full(ok.sum(), "_todo") if estrato is None
               else pd.Series(estrato).astype(str).to_numpy()[ok])
    return y[ok], w[ok], psu, estrato


def media_disenio(y: Sequence, w: Sequence,
                  psu: Optional[Sequence] = None,
                  estrato: Optional[Sequence] = None,
                  solitarias: str = "centrado") -> Estimacion:
    """Media ponderada con su error estándar por linealización de Taylor.

    Sin `psu` devuelve el error SRS ponderado y lo marca (`con_diseno=False`):
    es lo que se puede hacer con la ECP, y el resultado lo dice en vez de
    aparentar una estimación con diseño.
    """
    y, w, psu, estrato = _limpiar(y, w, psu, estrato)
    n = int(len(y))
    W = float(w.sum())
    media = float((w * y).sum() / W)

    var_w = float((w * (y - media) ** 2).sum() / W)
    v_srs = var_w / n
    ee_srs = float(np.sqrt(v_srs))

    if psu is None:
        return Estimacion(media=media, ee=ee_srs, ee_srs=ee_srs, deff=1.0, n=n,
                          con_diseno=False,
                          notas=["Sin identificador de UPM: no hay estimación con "
                                 "diseño posible. El error reportado es el de SRS "
                                 "ponderado y está subestimado (DI-D1)."])

    z = w * (y - media) / W
    d = pd.DataFrame({"z": z, "psu": psu, "h": estrato})
    v_total, solit, n_psu = 0.0, 0, 0
    totales_solitarios = []

    for _, g in d.groupby("h", sort=False):
        t = g.groupby("psu", sort=False).z.sum()
        n_psu += len(t)
        if len(t) < 2:
            solit += 1
            totales_solitarios.append(float(t.iloc[0]))
            continue
        v_total += len(t) / (len(t) - 1) * float(((t - t.mean()) ** 2).sum())

    notas = []
    if solit:
        if solitarias == "centrado":
            # DI-D3: se centran en 0 (la media global de los residuos), que es
            # lo que hace Stata con singleunit(centered).
            v_total += float(np.sum(np.asarray(totales_solitarios) ** 2))
            notas.append(f"{solit} estrato(s) con una sola UPM, centrados en 0 (DI-D3).")
        elif solitarias == "omitir":
            notas.append(f"{solit} estrato(s) con una sola UPM, OMITIDOS: "
                         "la varianza queda subestimada (DI-D3).")
        else:
            raise DisenoError("solitarias debe ser 'centrado' u 'omitir'.")

    ee = float(np.sqrt(v_total))
    return Estimacion(media=media, ee=ee, ee_srs=ee_srs,
                      deff=float(v_total / v_srs) if v_srs > 0 else float("nan"),
                      n=n, n_psu=n_psu, n_estratos=int(d.h.nunique()),
                      psu_solitarias=solit, notas=notas)


@dataclass
class Diferencia:
    delta: float
    ee: float
    z: float
    significativa: bool
    a: Estimacion
    b: Estimacion

    @property
    def ic95(self) -> tuple[float, float]:
        return (self.delta - Z_95 * self.ee, self.delta + Z_95 * self.ee)

    def __str__(self) -> str:
        lo, hi = self.ic95
        return (f"{self.delta:+.4f}  ee {self.ee:.4f}  IC95 [{lo:+.4f}, {hi:+.4f}]  "
                f"z {self.z:+.2f}  {'SIGNIFICATIVA' if self.significativa else 'no distinguible de 0'}")


def diferencia(a: Estimacion, b: Estimacion) -> Diferencia:
    """b − a entre dos olas independientes (DI-D5)."""
    delta = b.media - a.media
    ee = float(np.sqrt(a.ee ** 2 + b.ee ** 2))
    z = delta / ee if ee > 0 else float("nan")
    return Diferencia(delta=delta, ee=ee, z=float(z),
                      significativa=bool(abs(z) > Z_95), a=a, b=b)


def deff_prestado(est: Estimacion, deff: float = DEFF_MEDIDO_EPC["mediana"]) -> Estimacion:
    """Infla el error de una estimación sin diseño por un DEFF de otra fuente.

    Es la única salida para la ECP (DI-D1). Devuelve una estimación nueva que
    **deja constancia en `notas` de que el factor es prestado**: un intervalo
    construido así no es una estimación con diseño, es una corrección
    aproximada, y confundirlas sería peor que no corregir.
    """
    if est.con_diseno:
        raise DisenoError("Esta estimación ya tiene diseño; no hay nada que prestar.")
    if deff <= 0:
        raise DisenoError("El DEFF prestado tiene que ser positivo.")
    return Estimacion(
        media=est.media, ee=est.ee_srs * float(np.sqrt(deff)), ee_srs=est.ee_srs,
        deff=float(deff), n=est.n, con_diseno=False,
        notas=est.notas + [f"Error inflado por un DEFF PRESTADO de {deff:.2f} "
                           f"(medido en la EPC, no en esta fuente). No es una "
                           f"estimación con diseño."])
