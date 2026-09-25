"""
src/population/build_agents.py

Último paso del pipeline de población sintética (ver ARCHITECTURE.md sección 6):

    loader.py  ->  matching.py  ->  build_agents.py  ->  poblacion_sintetica.parquet

Toma el resultado de `hot_deck_match` (src/population/matching.py) y lo
convierte en la estructura EXACTA de 6 campos fijada en D12
(PROJECT_CONTEXT.md):

    agent_id, edad, sexo, localidad, estrato, nivel_educativo, opinion_t0

No agrega columnas nuevas al archivo final más allá de esas 6 (ninguna
variable "porque estaba disponible" — Regla de PROMPT_MAESTRO.md sección 10).
La trazabilidad del matching (nivel de relajación, qué donante se usó por
fila) se guarda aparte, en el metadata JSON de la corrida — no contamina la
tabla de agentes, pero tampoco se descarta (sección 26 del prompt maestro:
reproducibilidad obligatoria).
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import pandas as pd

from src.population.matching import MatchingResult

logger = logging.getLogger(__name__)

# Estructura exacta de D12 (PROJECT_CONTEXT.md)
CAMPOS_D12 = ["agent_id", "edad", "sexo", "localidad", "estrato", "nivel_educativo", "opinion_t0"]

LOCALIDADES_VALIDAS_BOGOTA = {
    "Suba", "Kennedy", "Engativá", "Bosa", "Ciudad Bolívar", "Usaquén", "Fontibón",
    "San Cristóbal", "Usme", "Rafael Uribe Uribe", "Puente Aranda", "Tunjuelito",
    "Chapinero", "Teusaquillo", "Barrios Unidos", "Santa Fe", "Los Mártires",
    "Antonio Nariño", "La Candelaria", "Sumapaz",
}


class ValidacionAgentesError(Exception):
    """Se lanza cuando la tabla de agentes no cumple los rangos/tipos
    esperados de D12 — mejor fallar aquí que dejar pasar un agente inválido
    al ABM (Regla 2 del prompt maestro: nunca seguir silenciosamente con
    datos que no se pueden confiar)."""


def build_agents(
    matching_result: MatchingResult,
    opinion_col: str,
    validar: bool = True,
) -> pd.DataFrame:
    """
    Convierte el resultado del hot-deck en la tabla final de agentes (D12).

    Parameters
    ----------
    matching_result : MatchingResult
        Salida de `hot_deck_match` (src/population/matching.py).
    opinion_col : str
        Nombre de la columna de opinión en `matching_result.agentes` que se
        renombra a `opinion_t0` (el nombre fijado en D12). Ej.
        "confianza_institucional".
    validar : bool
        Si True (default), corre `validar_agentes` antes de devolver — no
        silencia errores de rango/tipo.

    Returns
    -------
    DataFrame con exactamente las 7 columnas de D12, en ese orden.
    """
    df = matching_result.agentes.copy()

    if opinion_col not in df.columns:
        raise ValueError(f"'{opinion_col}' no está en matching_result.agentes")

    df = df.rename(columns={opinion_col: "opinion_t0"})

    faltantes = set(CAMPOS_D12) - set(df.columns)
    if faltantes:
        raise ValueError(
            f"Faltan campos de D12 en el resultado del matching: {faltantes}. "
            "Revisar que el receptor haya traído todas las variables puente."
        )

    agentes = df[CAMPOS_D12].copy()

    if validar:
        validar_agentes(agentes)

    logger.info("build_agents: %d agentes construidos con la estructura D12.", len(agentes))
    return agentes


def validar_agentes(agentes: pd.DataFrame) -> None:
    """
    Valida rangos y tipos de las 7 columnas de D12. Lanza
    ValidacionAgentesError con TODOS los problemas encontrados (no solo el
    primero), para que una corrida de validación diga de una vez todo lo
    que hay que corregir.
    """
    problemas = []

    if agentes["agent_id"].duplicated().any():
        n_dup = agentes["agent_id"].duplicated().sum()
        problemas.append(f"{n_dup} agent_id duplicados")

    if agentes["edad"].isna().any() or (agentes["edad"] < 18).any() or (agentes["edad"] > 110).any():
        problemas.append("valores de 'edad' fuera de rango [18, 110] o nulos")

    if not agentes["sexo"].isin(["F", "M"]).all():
        valores_invalidos = agentes.loc[~agentes["sexo"].isin(["F", "M"]), "sexo"].unique()
        problemas.append(f"'sexo' con valores fuera de {{F, M}}: {list(valores_invalidos)}")

    localidades_invalidas = set(agentes["localidad"].unique()) - LOCALIDADES_VALIDAS_BOGOTA
    if localidades_invalidas:
        problemas.append(f"'localidad' con valores no reconocidos: {localidades_invalidas}")

    if agentes["estrato"].isna().any():
        n_na = agentes["estrato"].isna().sum()
        problemas.append(f"{n_na} agentes sin 'estrato' (no debería pasar: viene del receptor)")
    elif not agentes["estrato"].between(0, 9).all():
        problemas.append("valores de 'estrato' fuera de rango [0, 9]")

    if not agentes["nivel_educativo"].between(0, 5).all():
        problemas.append("valores de 'nivel_educativo' fuera de rango [0, 5]")

    if agentes["opinion_t0"].isna().any():
        n_na = agentes["opinion_t0"].isna().sum()
        problemas.append(f"{n_na} agentes sin 'opinion_t0' asignada")

    if problemas:
        detalle = "\n  - ".join(problemas)
        raise ValidacionAgentesError(f"La población construida tiene {len(problemas)} problema(s):\n  - {detalle}")

    logger.info("validar_agentes: OK, sin problemas de rango/tipo/unicidad.")


def guardar_poblacion_sintetica(
    agentes: pd.DataFrame,
    matching_result: MatchingResult,
    output_dir: str | Path,
    dataset_version: str,
    receptor_fuente: str,
    donante_fuente: str,
    distance_vars_usadas: list[str],
    random_state: Optional[int],
    nombre_base: str = "poblacion_sintetica",
    muestreo_metadata: Optional[dict] = None,
    diagnostico_territorial: Optional[pd.DataFrame] = None,
    escala_opinion: Optional[dict] = None,
) -> Path:
    """
    Guarda la población sintética final + metadata de reproducibilidad
    (sección 26 del prompt maestro / sección 5.5 de ARCHITECTURE.md).

    Escribe dos archivos:
        {output_dir}/poblacion_sintetica.parquet  (o .csv si no hay motor parquet)
        {output_dir}/poblacion_sintetica_metadata.json

    El metadata incluye la distribución de niveles de relajación del
    hot-deck (ver matching.py) — así el supuesto de independencia
    condicional (POPULATION_SPECIFICATION.md sección 3) queda siempre
    trazable, no oculto detrás del archivo final de agentes.

    `escala_opinion` describe QUÉ mide `opinion_t0`: la pregunta, el rango,
    cuántos ítems se promediaron y con qué denominador. Sin eso, el CSV
    entrega una columna de números entre 1 y 5 que nadie puede interpretar
    sin abrir el código (A05).
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    ruta_datos = output_dir / f"{nombre_base}.parquet"
    try:
        agentes.to_parquet(ruta_datos, index=False)
    except ImportError:
        logger.warning(
            "No hay motor de parquet instalado (pyarrow/fastparquet). "
            "Guardando como CSV en su lugar — instalar pyarrow para producción."
        )
        ruta_datos = output_dir / f"{nombre_base}.csv"
        agentes.to_csv(ruta_datos, index=False)

    resumen_relajacion = {int(k): int(v) for k, v in matching_result.resumen_relajacion.items()}

    metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset_version": dataset_version,
        "n_agentes": len(agentes),
        "receptor_fuente": receptor_fuente,
        "donante_fuente": donante_fuente,
        "distance_vars_usadas": distance_vars_usadas,
        "random_state": random_state,
        "resumen_relajacion_hotdeck": resumen_relajacion,
        # Qué exigía cada nivel EN ESTA corrida. La escalera se deriva de
        # exact_match_vars, así que "nivel 1" no significa necesariamente lo
        # mismo entre corridas: sin esto, resumen_relajacion_hotdeck sería
        # ilegible a futuro.
        "escalera_relajacion_hotdeck": {
            str(i): vars_nivel for i, vars_nivel in enumerate(matching_result.escalera_relajacion)
        },
        "supuesto_independencia_condicional": (
            "No verificado — ver POPULATION_SPECIFICATION.md sección 3. "
            "La variable opinion_t0 se asignó por hot-deck nearest-neighbour "
            "sobre variables puente parciales; no implica que la opinión real "
            "dependa solo de esas variables."
        ),
        "archivo_datos": str(ruta_datos.name),
    }

    # Cómo se eligieron los N agentes del receptor completo (D14). Sin esto,
    # dos poblaciones del mismo tamaño y la misma semilla serían
    # indistinguibles aunque una esté ponderada y la otra no.
    if muestreo_metadata:
        metadata["muestreo"] = muestreo_metadata

    # Composición territorial contra el marginal real. Es la verificación de
    # que el muestreo hizo lo que dice hacer, y el número que hay que
    # reportar junto a cualquier resultado territorial (D14).
    # QUÉ mide opinion_t0. A05: el índice promedia un número variable de
    # ítems por persona; el número está en `n_items` y viaja con el dato.
    if escala_opinion:
        metadata["escala_opinion"] = escala_opinion

    if diagnostico_territorial is not None:
        d = diagnostico_territorial
        n = int(d["observado"].sum())
        metadata["diagnostico_territorial"] = {
            "distancia_al_marginal": round(
                float((d["observado"] / n - d["esperado"] / n).abs().sum() / 2), 4),
            "sesgo_min": round(float(d["sesgo"].min()), 2),
            "sesgo_max": round(float(d["sesgo"].max()), 2),
            "por_localidad": {
                str(r.localidad): {"esperado": float(r.esperado), "observado": int(r.observado)}
                for r in d.itertuples()
            },
        }

    ruta_metadata = output_dir / f"{nombre_base}_metadata.json"
    with open(ruta_metadata, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    logger.info("Población sintética guardada en %s (+ metadata en %s)", ruta_datos, ruta_metadata)
    return ruta_datos
