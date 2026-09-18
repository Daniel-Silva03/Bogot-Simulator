"""
src/population/matching.py

Implementa el método de fusión estadística (statistical matching / data fusion)
especificado en POPULATION_SPECIFICATION.md, sección 3, método A:

    Hot-deck nearest-neighbour matching

Por cada persona de la fuente RECEPTORA (ej. Encuesta Multipropósito, que trae
el esqueleto demográfico completo pero no opinión), se busca la persona más
parecida en la fuente DONANTE (ej. Bogotá Cómo Vamos / Encuesta de Confianza
Institucional, que sí trae la variable de opinión) según las variables puente
fijadas en D12 (PROJECT_CONTEXT.md): edad, sexo, localidad, estrato,
nivel_educativo — y se le copia la variable de opinión del donante.

SUPUESTO DEL MODELO (no hecho, documentado explícitamente — Principio 3 del
proyecto): se asume independencia condicional. Es decir, dadas las variables
puente, la variable de opinión no depende de nada más que no esté en ambas
encuestas. Esta asunción no es verificable con los datos disponibles y debe
quedar señalada en cualquier resultado derivado de este módulo.

DECISIÓN DE IMPLEMENTACIÓN no cubierta explícitamente por
POPULATION_SPECIFICATION.md (documentada aquí porque hubo que tomarla para
poder escribir código, siguiendo la Regla 3 del prompt maestro — separar
hecho/supuesto/decisión):

    - `localidad` y `sexo` se tratan como variables de EMPAREJAMIENTO EXACTO
      (bloques): no tiene sentido metodológico asignarle a alguien la opinión
      de una persona de otra localidad o de otro sexo cuando SÍ tenemos esa
      información en ambas fuentes.
    - `edad`, `estrato`, `nivel_educativo` se tratan como variables de
      DISTANCIA (nearest-neighbour euclidiano, estandarizadas) dentro de cada
      bloque exacto de localidad × sexo.
    - Si un bloque exacto (localidad × sexo) no tiene NINGÚN donante
      disponible, se aplica una escalera de relajación documentada y
      registrada (ver `construir_escalera_relajacion` y el log de fallback
      que devuelve `hot_deck_match`), para que el porcentaje de receptores
      que tuvieron que usar una coincidencia relajada quede siempre
      visible, no oculto. La escalera se deriva de `exact_match_vars`
      soltando la última variable primero, así que el orden en que se
      pasan esas variables es significativo.

Esta escalera de relajación es una recomendación de implementación, no una
decisión D0X — debe revisarse junto con Daniel antes de darla por definitiva
para el prototipo (A05 sigue formalmente abierta).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

logger = logging.getLogger(__name__)

# Variables puente fijadas en D12 (PROJECT_CONTEXT.md)
EXACT_MATCH_VARS = ["localidad", "sexo"]
DISTANCE_VARS = ["edad", "estrato", "nivel_educativo"]


def construir_escalera_relajacion(exact_match_vars: list[str]) -> list[list[str]]:
    """
    Construye la escalera de relajación a partir de las variables de
    emparejamiento exacto pedidas, soltando la ÚLTIMA primero.

    Con el default D12 ["localidad", "sexo"] produce exactamente la
    escalera que este módulo tenía escrita a mano:

        nivel 0: ["localidad", "sexo"]  — exacto en ambas (preferido)
        nivel 1: ["localidad"]          — relaja sexo, mantiene localidad
        nivel 2: []                     — solo nearest-neighbour por distancia

    El orden de `exact_match_vars` es por lo tanto significativo: va de la
    variable que MÁS importa conservar a la que menos. Antes esta escalera
    era una constante fija, lo que hacía que el parámetro
    `exact_match_vars` de `hot_deck_match` se validara pero no tuviera
    ningún efecto — contradiciendo la regla de la sección 25 del prompt
    maestro (no hardcodear) que el propio docstring invocaba.

    La escalera sigue siendo una decisión de implementación, no una
    decisión D0X: qué variable se relaja primero es revisable.
    """
    return [list(exact_match_vars[:k]) for k in range(len(exact_match_vars), -1, -1)]


# Escalera por defecto (variables puente D12). Se conserva como constante
# pública porque tests y notebooks la importan por nombre.
NIVELES_RELAJACION = construir_escalera_relajacion(EXACT_MATCH_VARS)


@dataclass
class MatchingResult:
    """Resultado del hot-deck, con trazabilidad completa (no solo los valores)."""

    agentes: pd.DataFrame
    nivel_relajacion_usado: np.ndarray  # por fila del receptor: índice en la escalera
    donante_index: np.ndarray           # posición del donante usado, por fila
    resumen_relajacion: dict = field(default_factory=dict)
    # Qué exigía cada nivel. Se guarda con el resultado para que el
    # metadata de la corrida diga qué significó "nivel 1" en ESA corrida,
    # ahora que la escalera se deriva de exact_match_vars y ya no es fija.
    escalera_relajacion: list = field(default_factory=lambda: list(NIVELES_RELAJACION))

    def reporte(self) -> str:
        n = len(self.agentes)
        nivel_mas_laxo = len(self.escalera_relajacion) - 1
        exigencia_nivel_0 = "+".join(self.escalera_relajacion[0]) if self.escalera_relajacion[0] else "nada"
        lineas = [
            f"Hot-deck matching — {n} agentes construidos.",
            f"Distribución por nivel de relajación usado (0 = coincidencia exacta "
            f"en {exigencia_nivel_0}):",
        ]
        for nivel, count in sorted(self.resumen_relajacion.items()):
            pct = 100 * count / n
            exige = "+".join(self.escalera_relajacion[nivel]) or "nada (solo distancia)"
            lineas.append(f"  nivel {nivel} (exige {exige}): {count} ({pct:.1f}%)")
        if self.resumen_relajacion.get(nivel_mas_laxo, 0) > 0 and not self.escalera_relajacion[nivel_mas_laxo]:
            lineas.append(
                f"ADVERTENCIA: hubo receptores emparejados sin respetar ninguna "
                f"variable de bloque (nivel {nivel_mas_laxo}). Revisar antes de usar "
                "el resultado para validación territorial."
            )
        return "\n".join(lineas)


def _standardize(df: pd.DataFrame, cols: list[str], ref_mean: pd.Series, ref_std: pd.Series) -> np.ndarray:
    """Estandariza columnas usando media/desviación de referencia (del donante,
    para que receptor y donante queden en la misma escala)."""
    vals = df[cols].to_numpy(dtype=float)
    return (vals - ref_mean.to_numpy()) / ref_std.to_numpy()


def hot_deck_match(
    receptor: pd.DataFrame,
    donante: pd.DataFrame,
    opinion_col: str,
    exact_match_vars: Optional[list[str]] = None,
    distance_vars: Optional[list[str]] = None,
    random_state: Optional[int] = None,
    peso_col: Optional[str] = None,
    k_empates: int = 50,
) -> MatchingResult:
    """
    Ejecuta el hot-deck nearest-neighbour matching de POPULATION_SPECIFICATION.md.

    Parameters
    ----------
    receptor : DataFrame
        Fuente demográfica completa (ej. Encuesta Multipropósito). Debe traer
        las columnas de `exact_match_vars` + `distance_vars` + `agent_id`.
    donante : DataFrame
        Fuente de opinión (ej. Bogotá Cómo Vamos / Veeduría Distrital). Debe
        traer las mismas columnas puente + `opinion_col`.
    opinion_col : str
        Nombre de la columna de opinión en `donante` que se copiará al agente
        (ej. "confianza_institucional", la variable fijada en D11).
    exact_match_vars, distance_vars : list[str], opcional
        Por defecto usan D12: localidad+sexo (exacto), edad/estrato/nivel_educativo
        (distancia). Se dejan como parámetro para no hardcodear (regla de
        PROMPT_MAESTRO.md sección 25) y permitir variantes en experimentos futuros.
        `exact_match_vars` define además la escalera de relajación, que
        suelta la última variable primero: pasarlo en orden de importancia
        decreciente (ver `construir_escalera_relajacion`).
    random_state : int, opcional
        Para reproducibilidad cuando hay empates en la distancia (sección 26
        del prompt maestro: toda simulación debe poder reproducirse).
    peso_col : str, opcional
        Columna de factor de expansión del donante. Si se pasa, los empates se
        resuelven muestreando proporcional a ese peso; si no, uniformemente.
    k_empates : int
        Cuántos vecinos se consultan para detectar empates (DI-M1).

    DI-M1 — LOS EMPATES SE SORTEAN, NO SE TOMAN EN ORDEN
    ----------------------------------------------------
    Hasta septiembre de 2026 esta función tomaba `n_neighbors=1` y se quedaba
    con el primero que devolviera el índice. Con variables de distancia
    **discretas** eso es una degeneración, no un detalle: si edad viene en 5
    bandas y estrato en 7 niveles, un bloque de sexo tiene ~35 celdas, todos
    los receptores de una celda están a distancia 0 de los mismos donantes, y
    todos reciben **el mismo valor**. La opinión resultante deja de ser una
    muestra de la distribución del donante y pasa a ser una muestra de una
    docena de individuos replicada por el tamaño de cada celda.

    Se detectó al construir la población base del Experimento 7 con la EPC,
    cuyas edades vienen en bandas: la distribución sintética daba 20,4 % de
    valores 5 contra 9,8 % observado, y \(W_1\) contra lo observado quedaba en
    3,75 veces el piso de ruido. El control T6, pre-registrado, lo detuvo antes
    de correr el experimento. Era el defecto que A05 tenía anotado como "el
    desempate determinista aplana la variable de opinión".

    Ahora se consultan `k_empates` vecinos, se toman todos los que están a la
    distancia mínima (con tolerancia 1e-9) y se sortea entre ellos **con
    probabilidad proporcional al factor de expansión** cuando se pasa
    `peso_col`. Lo segundo importa tanto como lo primero: el objetivo contra el
    que se compara es la distribución **ponderada** del donante, así que donar
    uniformemente entre empatados introduciría un sesgo propio.

    Sin empates el resultado es idéntico al anterior.

    Returns
    -------
    MatchingResult
        `agentes`: el receptor original + la columna de opinión fusionada,
        con índice reiniciado a 0..N-1 (ver nota sobre posiciones en el
        cuerpo de la función). El ORDEN de las filas se conserva, así que
        `agentes.iloc[i]` sigue siendo el receptor que se pasó en la
        posición i.
        Incluye trazabilidad completa de qué nivel de relajación se usó por
        fila, y qué exigía cada nivel (`escalera_relajacion`), para que el
        supuesto de independencia condicional (documentado en
        POPULATION_SPECIFICATION.md sección 3) nunca quede oculto.
    """
    exact_match_vars = exact_match_vars or EXACT_MATCH_VARS
    distance_vars = distance_vars or DISTANCE_VARS
    escalera = construir_escalera_relajacion(exact_match_vars)
    rng = np.random.default_rng(random_state)

    # Todo lo que sigue trabaja con POSICIONES de fila (0..n-1), no con
    # etiquetas de índice. Un receptor con índice no trivial — por ejemplo
    # el resultado de `.sample(1000)` sin resetear — producía antes, en el
    # mejor caso, un IndexError, y en el peor, opiniones asignadas a la
    # persona equivocada sin que nada lo reportara: `resumen_relajacion`
    # seguía diciendo "100% en nivel 0" aunque el bloque exacto se hubiera
    # violado. Se normaliza aquí, y el bucle de abajo ya no depende del
    # índice para nada.
    receptor = receptor.reset_index(drop=True)
    donante = donante.reset_index(drop=True)

    faltantes_receptor = set(exact_match_vars + distance_vars) - set(receptor.columns)
    faltantes_donante = set(exact_match_vars + distance_vars + [opinion_col]) - set(donante.columns)
    if faltantes_receptor:
        raise ValueError(f"Faltan columnas en el receptor: {faltantes_receptor}")
    if faltantes_donante:
        raise ValueError(f"Faltan columnas en el donante: {faltantes_donante}")

    donante = donante.dropna(subset=distance_vars + [opinion_col]).reset_index(drop=True)
    if len(donante) == 0:
        raise ValueError("El donante no tiene registros válidos tras eliminar NaN.")

    ref_mean = donante[distance_vars].mean()
    ref_std = donante[distance_vars].std().replace(0, 1.0)  # evita división por cero

    n = len(receptor)
    opinion_asignada = np.full(n, np.nan, dtype=float)
    nivel_usado = np.full(n, -1, dtype=int)
    donante_idx_usado = np.full(n, -1, dtype=int)

    receptor_std = _standardize(receptor, distance_vars, ref_mean, ref_std)
    donante_std_full = _standardize(donante, distance_vars, ref_mean, ref_std)

    resumen_relajacion = {nivel: 0 for nivel in range(len(escalera))}
    opinion_donante = donante[opinion_col].to_numpy(dtype=float)

    # DI-M1: pesos del donante para sortear empates. Si la columna no está, se
    # avisa y se sortea uniformemente: es mejor que el desempate determinista,
    # pero no reproduce la distribución ponderada.
    pesos_donante = None
    if peso_col is not None:
        if peso_col not in donante.columns:
            logger.warning(
                "peso_col='%s' no está en el donante; los empates se sortean "
                "uniformemente (DI-M1).", peso_col)
        else:
            pesos_donante = pd.to_numeric(
                donante[peso_col], errors="coerce").fillna(0.0).to_numpy(float)

    for nivel_idx, vars_exactas_nivel in enumerate(escalera):
        pendientes = np.where(np.isnan(opinion_asignada))[0]
        if len(pendientes) == 0:
            break

        if vars_exactas_nivel:
            # .to_numpy() descarta el índice: quedan arrays alineados por
            # POSICIÓN con receptor_std / donante_std_full.
            claves_receptor = (
                receptor[vars_exactas_nivel].astype(str).agg("|".join, axis=1).to_numpy()
            )
            claves_donante = (
                donante[vars_exactas_nivel].astype(str).agg("|".join, axis=1).to_numpy()
            )
        else:
            # nivel sin restricción exacta: todos los donantes son candidatos
            claves_receptor = np.full(n, "__ALL__", dtype=object)
            claves_donante = np.full(len(donante), "__ALL__", dtype=object)

        claves_pendientes = claves_receptor[pendientes]

        for clave in pd.unique(claves_pendientes):
            donante_mask = claves_donante == clave
            if not donante_mask.any():
                continue  # este bloque no tiene donantes ni en este nivel; sigue al próximo nivel

            filas = pendientes[claves_pendientes == clave]  # posiciones, no etiquetas
            donante_std_bloque = donante_std_full[donante_mask]
            donante_pos_originales = np.where(donante_mask)[0]

            k = int(min(max(1, k_empates), len(donante_std_bloque)))
            nn = NearestNeighbors(n_neighbors=k)
            nn.fit(donante_std_bloque)
            dist, idx_local = nn.kneighbors(receptor_std[filas])

            # DI-M1: sortear entre los empatados a la distancia mínima.
            elegidos_local = np.empty(len(filas), dtype=int)
            for i in range(len(filas)):
                d_i = dist[i]
                empatados = idx_local[i][d_i <= d_i[0] + 1e-9]
                if len(empatados) == 1:
                    elegidos_local[i] = empatados[0]
                    continue
                if pesos_donante is None:
                    elegidos_local[i] = rng.choice(empatados)
                else:
                    pe = pesos_donante[donante_pos_originales[empatados]]
                    total = pe.sum()
                    elegidos_local[i] = (rng.choice(empatados, p=pe / total)
                                         if total > 0 else rng.choice(empatados))

            elegidos = donante_pos_originales[elegidos_local]
            opinion_asignada[filas] = opinion_donante[elegidos]
            nivel_usado[filas] = nivel_idx
            donante_idx_usado[filas] = elegidos
            resumen_relajacion[nivel_idx] += len(filas)

    n_sin_match = np.isnan(opinion_asignada).sum()
    if n_sin_match > 0:
        raise RuntimeError(
            f"{n_sin_match} receptores no encontraron ningún donante ni en el "
            "nivel más relajado. Revisar cobertura del donante."
        )

    agentes = receptor.copy()
    agentes[opinion_col] = opinion_asignada

    logger.info(
        "Hot-deck completado: %d agentes, distribución de relajación %s",
        n, resumen_relajacion,
    )

    return MatchingResult(
        agentes=agentes,
        nivel_relajacion_usado=nivel_usado,
        donante_index=donante_idx_usado,
        resumen_relajacion=resumen_relajacion,
        escalera_relajacion=escalera,
    )