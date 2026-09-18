"""
src/population/muestreo.py

Selección de los N agentes del prototipo a partir del receptor completo
(168.200 personas de Multipropósito 2021). Cierra A16.

EL PROBLEMA
-----------
Multipropósito sobre-muestrea localidades pequeñas a propósito, para poder
estimar a nivel de localidad. Tomar una muestra aleatoria simple del
microdato hereda esa distorsión entera. Medido contra el marginal DANE-SDP
2025, la corrida de septiembre tenía a Santa Fe con 45 agentes donde le
correspondían 13, y a Bosa con 38 donde le correspondían 87: un factor de
17 entre la localidad más sobre-representada y la más sub-representada.

Eso no es un detalle cosmético para este proyecto. Los \\(n_l\\) por localidad
alimentan el despeje de \\(p_{intra}\\) y \\(p_{inter}\\) del generador
territorial (NETWORK_SPECIFICATION.md sección 5), así que una muestra
desbalanceada produce una estructura de red desbalanceada, y el
Experimento 2 mediría en parte el sesgo muestral en vez de la estructura
social.

DECISIÓN (A16, Septiembre 2026)
-------------------------------
Muestreo con probabilidad proporcional al FACTOR DE EXPANSIÓN de la
encuesta. Es lo que corrige TODAS las dimensiones a la vez —localidad,
edad, sexo, educación, estrato— porque el ponderador es exactamente el
objeto que la propia encuesta diseñó para que la muestra represente a
Bogotá. Estratificar solo por localidad arreglaría la dimensión que más
nos preocupa hoy y dejaría las otras cuatro sesgadas.

Si el extracto no trae el ponderador, el método cae a estratificación por
localidad contra el marginal DANE-SDP, y lo dice. Nunca cae en silencio.

CÓMO SE MUESTREA (decisión de implementación)
---------------------------------------------
PPS sistemático: se acumulan los pesos, se toma un arranque aleatorio en
[0, W/n) y se selecciona cada W/n a lo largo del acumulado. Esto da
probabilidades de inclusión exactamente proporcionales al peso,
\\(\\pi_i = n \\cdot w_i / W\\), sin reemplazo.

Se prefiere sobre `numpy.random.choice(..., replace=False, p=pesos)`, que
es lo primero que uno escribiría: esa función hace muestreo sucesivo, y
sus probabilidades de inclusión NO son proporcionales a los pesos (las
unidades pesadas quedan sub-representadas respecto de su peso nominal).
La diferencia es chica con pesos parejos y grande con pesos dispersos,
que es justamente el caso acá.

Las filas se barajan antes de acumular, para que el orden del archivo
—que en Multipropósito viene agrupado por conglomerado— no introduzca
estructura en la selección sistemática.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

RAIZ_REPO = Path(__file__).resolve().parents[2]
MARGINAL_POR_DEFECTO = RAIZ_REPO / "data" / "external" / "marginal_localidad_18mas.csv"

COLUMNA_PESO = "factor_expansion"
METODOS = ("ponderado", "estratificado", "aleatorio")


class MuestreoError(Exception):
    """Parámetros o insumos que no permiten producir la muestra pedida."""


@dataclass
class ResultadoMuestreo:
    """La muestra más la trazabilidad de cómo se obtuvo."""

    agentes: pd.DataFrame
    metodo: str
    metadata: dict = field(default_factory=dict)

    def reporte(self) -> str:
        lineas = [f"Muestreo '{self.metodo}' — {len(self.agentes)} agentes "
                  f"de {self.metadata.get('n_receptor', '?')}."]
        for k in ("razon_metodo", "peso_min", "peso_max", "unidades_certeza",
                  "localidades_sin_cupo", "marginal_fuente"):
            if k in self.metadata:
                lineas.append(f"  {k}: {self.metadata[k]}")
        return "\n".join(lineas)


def cargar_marginal(path: str | Path | None = None) -> Optional[pd.DataFrame]:
    """Marginal territorial generado por
    `extraer_columnas_em2021.py proyecciones`. Devuelve None si no existe."""
    path = Path(path) if path else MARGINAL_POR_DEFECTO
    if not path.exists():
        return None
    marg = pd.read_csv(path)
    faltantes = {"localidad", "poblacion"} - set(marg.columns)
    if faltantes:
        raise MuestreoError(f"El marginal {path} no tiene las columnas {faltantes}.")
    return marg


def muestrear(
    receptor: pd.DataFrame,
    n: int,
    seed: Optional[int] = None,
    metodo: str = "auto",
    marginal: Optional[pd.DataFrame] = None,
) -> ResultadoMuestreo:
    """
    Selecciona `n` agentes del receptor.

    metodo : "auto" (default) elige `ponderado` si el receptor trae
        `factor_expansion`; si no, `estratificado` cuando hay marginal
        disponible; y `aleatorio` como último recurso, avisando. También
        se puede forzar uno de METODOS.
    """
    if n <= 0:
        raise MuestreoError(f"n debe ser positivo, se recibió {n}.")
    if n > len(receptor):
        raise MuestreoError(
            f"Se piden {n} agentes pero el receptor tiene {len(receptor)} filas.")
    if metodo not in METODOS + ("auto",):
        raise MuestreoError(f"Método desconocido: '{metodo}'. Opciones: {METODOS + ('auto',)}.")

    rng = np.random.default_rng(seed)
    receptor = receptor.reset_index(drop=True)
    tiene_peso = COLUMNA_PESO in receptor.columns
    if marginal is None:
        marginal = cargar_marginal()

    metodo_elegido, razon = _resolver_metodo(metodo, tiene_peso, marginal is not None)

    metadata = {
        "n_receptor": len(receptor),
        "n_muestra": n,
        "seed_muestreo": seed,
        "razon_metodo": razon,
    }

    if metodo_elegido == "ponderado":
        idx, extra = _pps_sistematico(receptor[COLUMNA_PESO].to_numpy(dtype=float), n, rng)
    elif metodo_elegido == "estratificado":
        if marginal is None:
            raise MuestreoError(
                "El método 'estratificado' necesita el marginal territorial. "
                "Generarlo con: python src/population/extraer_columnas_em2021.py proyecciones")
        idx, extra = _estratificado_por_localidad(receptor, n, marginal, rng)
        extra["marginal_fuente"] = str(MARGINAL_POR_DEFECTO.name)
    else:
        idx, extra = np.sort(rng.choice(len(receptor), size=n, replace=False)), {}

    metadata.update(extra)
    muestra = receptor.iloc[idx].reset_index(drop=True)

    logger.info("Muestreo '%s': %d agentes. %s", metodo_elegido, len(muestra), razon)
    return ResultadoMuestreo(agentes=muestra, metodo=metodo_elegido, metadata=metadata)


def _resolver_metodo(metodo: str, tiene_peso: bool, hay_marginal: bool) -> tuple[str, str]:
    if metodo != "auto":
        if metodo == "ponderado" and not tiene_peso:
            raise MuestreoError(
                f"Se pidió muestreo ponderado pero el receptor no trae '{COLUMNA_PESO}'. "
                "Regenerar el extracto con: "
                "python src/population/extraer_columnas_em2021.py multiproposito")
        return metodo, "elegido explícitamente"

    if tiene_peso:
        return "ponderado", f"'{COLUMNA_PESO}' presente en el receptor (A16)"
    if hay_marginal:
        logger.warning(
            "El receptor no trae factor de expansión; se usa estratificación por "
            "localidad, que corrige el territorio pero NO edad, sexo ni educación.")
        return "estratificado", f"sin '{COLUMNA_PESO}'; se usa el marginal territorial"
    logger.warning(
        "Sin factor de expansión y sin marginal territorial: muestreo aleatorio "
        "simple. La muestra hereda el sobre-muestreo de localidades pequeñas de "
        "Multipropósito (ver DATA_INVENTORY.md sección 4).")
    return "aleatorio", "sin ponderador ni marginal — muestra NO representativa"


def _pps_sistematico(pesos: np.ndarray, n: int, rng: np.random.Generator) -> tuple[np.ndarray, dict]:
    """
    PPS sistemático. Devuelve (índices seleccionados, metadata).

    Las unidades cuyo peso es tan grande que \\(n w_i / W > 1\\) ("unidades
    de certeza") se seleccionan de oficio y se muestrea el resto sobre el
    peso remanente; si no se tratan aparte, el método las seleccionaría más
    de una vez.
    """
    if np.isnan(pesos).any():
        raise MuestreoError(
            f"Hay {int(np.isnan(pesos).sum())} filas con '{COLUMNA_PESO}' nulo. "
            "El muestreo ponderado no puede continuar sin inventar un peso.")
    if (pesos <= 0).any():
        raise MuestreoError(
            f"Hay {int((pesos <= 0).sum())} filas con '{COLUMNA_PESO}' <= 0.")

    n_total = len(pesos)
    certeza: list[int] = []
    restantes = np.arange(n_total)

    # Iterativo: al sacar una unidad de certeza baja W, lo que puede
    # empujar a otra por encima del umbral.
    while True:
        w = pesos[restantes]
        cupo = n - len(certeza)
        if cupo <= 0:
            break
        umbral = w.sum() / cupo
        nuevas = restantes[w > umbral]
        if len(nuevas) == 0:
            break
        certeza.extend(nuevas.tolist())
        restantes = restantes[w <= umbral]

    cupo = n - len(certeza)
    seleccion = list(certeza)

    if cupo > 0:
        orden = rng.permutation(restantes)        # rompe el orden del archivo
        w = pesos[orden]
        acumulado = np.cumsum(w)
        paso = acumulado[-1] / cupo
        arranque = rng.uniform(0, paso)
        puntos = arranque + paso * np.arange(cupo)
        posiciones = np.searchsorted(acumulado, puntos, side="left")
        posiciones = np.clip(posiciones, 0, len(orden) - 1)
        seleccion.extend(orden[posiciones].tolist())

    idx = np.unique(np.array(seleccion, dtype=int))
    if len(idx) != n:  # defensivo: no debería pasar tras el tratamiento de certeza
        raise MuestreoError(
            f"El PPS sistemático produjo {len(idx)} unidades distintas en vez de {n}.")

    return idx, {
        "peso_min": round(float(pesos.min()), 3),
        "peso_max": round(float(pesos.max()), 3),
        "peso_total": round(float(pesos.sum()), 1),
        "unidades_certeza": len(certeza),
    }


def _estratificado_por_localidad(
    receptor: pd.DataFrame, n: int, marginal: pd.DataFrame, rng: np.random.Generator
) -> tuple[np.ndarray, dict]:
    """Cuotas por localidad proporcionales al marginal, repartidas por
    restos mayores para que sumen exactamente n."""
    if "localidad" not in receptor.columns:
        raise MuestreoError("El receptor no trae 'localidad'.")

    share = marginal.set_index("localidad")["poblacion"]
    share = share / share.sum()
    exacto = share * n
    cuotas = np.floor(exacto).astype(int)
    resto = n - cuotas.sum()
    if resto > 0:  # restos mayores (Hare)
        orden = (exacto - cuotas).sort_values(ascending=False).index[:resto]
        cuotas[orden] += 1

    disponibles = receptor.groupby("localidad").indices
    sin_cupo, elegidos = [], []
    deficit = 0
    for loc, cuota in cuotas.items():
        pool = disponibles.get(loc, np.array([], dtype=int))
        if len(pool) < cuota:
            deficit += cuota - len(pool)
            sin_cupo.append(f"{loc}({len(pool)}/{cuota})")
            elegidos.extend(pool.tolist())
        elif cuota > 0:
            elegidos.extend(rng.choice(pool, size=int(cuota), replace=False).tolist())

    # El déficit de las localidades sin suficientes personas se reparte
    # entre el resto, en vez de devolver una muestra más chica de la pedida.
    if deficit:
        restantes = np.setdiff1d(np.arange(len(receptor)), np.array(elegidos, dtype=int))
        elegidos.extend(rng.choice(restantes, size=deficit, replace=False).tolist())

    idx = np.unique(np.array(elegidos, dtype=int))
    return idx, {
        "localidades_sin_cupo": sin_cupo or "ninguna",
        "deficit_redistribuido": deficit,
    }


def diagnostico_territorial(
    muestra: pd.DataFrame, marginal: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Compara la composición territorial de la muestra contra el marginal
    real. `sesgo` = observado / esperado: <1 sub-representada, >1
    sobre-representada, 1 en el blanco.

    Es la verificación de que el muestreo hizo lo que dice hacer, y el
    número que hay que reportar junto a cualquier resultado territorial
    del Experimento 2.
    """
    marginal = marginal if marginal is not None else cargar_marginal()
    if marginal is None:
        raise MuestreoError("No hay marginal territorial contra el cual comparar.")

    n = len(muestra)
    obs = muestra["localidad"].value_counts()
    d = marginal.copy()
    d["share"] = d["poblacion"] / d["poblacion"].sum()
    d["esperado"] = (d["share"] * n).round(1)
    d["observado"] = d["localidad"].map(obs).fillna(0).astype(int)
    d["sesgo"] = (d["observado"] / d["esperado"].replace(0, np.nan)).round(2)
    return d[["localidad", "poblacion", "esperado", "observado", "sesgo"]] \
        .sort_values("poblacion", ascending=False).reset_index(drop=True)
