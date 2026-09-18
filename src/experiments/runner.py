"""
src/experiments/runner.py

Ejecuta un experimento: barre configuraciones de red × N corridas, y deja
los resultados con la trazabilidad que exige la sección 35 de
PROJECT_CONTEXT.md.

    población fija  ×  red (varía por corrida)  ×  modelo de opinión
                              ↓
            experiments_output/{experiment_id}/

DE DÓNDE SALE LA VARIABILIDAD ENTRE CORRIDAS
---------------------------------------------
DeGroot y Friedkin-Johnsen son deterministas: dada la red y a(0), la
trayectoria es única (verificado en tests/test_opinion_models.py). La
población también es fija dentro de un experimento. Por lo tanto la única
fuente de variación entre las N corridas de una configuración es la
REALIZACIÓN DE LA RED.

Eso no es un detalle de implementación, es lo que hace que "200 runs por
escenario" signifique algo: sin variar la semilla de la red, las 200
corridas serían idénticas y la distribución de resultados que pide
RESEARCH.md sección 32 no existiría. El runner deriva una semilla distinta
por corrida y la registra.

DECISIÓN DE IMPLEMENTACIÓN
--------------------------
    DI-E1 — Sin capa Mesa por ahora.
        ARCHITECTURE.md preveía `src/model/` con `BogotaAgent` y
        `BogotaSocialModel`. Al quedar los modelos de opinión
        vectorizados, Mesa no aporta nada al Experimento 2: agregaría mil
        objetos Python y un par de órdenes de magnitud de lentitud para
        envolver una multiplicación de matrices, y la preocupación
        original por el scheduler (sesgo de orden en la actualización) ya
        está resuelta por construcción. Mesa entra cuando haga falta de
        verdad —heterogeneidad de comportamiento por agente, scheduling no
        trivial, eventos de la Fase 8—, no antes. Principio 5.

QUÉ SE GUARDA
-------------
    resultados.csv      una fila por corrida, con las métricas finales
    series.csv          media y desviación por paso, por corrida
                        (opcional: `guardar_series: false` lo desactiva)
    run_metadata.json   configuración completa, versiones, semillas,
                        tiempos, y el resumen agregado por configuración

Uso:

    python src/experiments/runner.py config/experiment_2.yaml
    python src/experiments/runner.py config/experiment_2.yaml --n-runs 5   # prueba rápida
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

RAIZ_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ_REPO))

from src.experiments.metrics import (  # noqa: E402
    indices_polarizacion,
    por_localidad,
    resumen_opinion,
    wasserstein1,
)
from src.network import crear_generador  # noqa: E402
from src.network.base import diagnosticos_red  # noqa: E402
from src.opinion import crear_modelo  # noqa: E402
from src.utils.config import ConfiguracionExperimento, ConfiguracionRed, cargar_config  # noqa: E402
from src.utils.seeds import semilla_para  # noqa: E402

logger = logging.getLogger("runner")

DIR_SALIDA = RAIZ_REPO / "experiments_output"
VERSION_RUNNER = "runner_v0.1"


def correr_experimento(
    config: ConfiguracionExperimento,
    dir_salida: Path | None = None,
    progreso_cada: int = 200,
) -> dict[str, Any]:
    """Corre el experimento completo y escribe los resultados a disco."""
    dir_salida = Path(dir_salida or DIR_SALIDA) / config.experiment_id
    dir_salida.mkdir(parents=True, exist_ok=True)

    agentes = _cargar_poblacion(config)
    a0 = agentes["opinion_t0"].to_numpy(dtype=float)
    rango = config.rango_opinion or (float(a0.min()), float(a0.max()))

    # Una instancia por tipo de generador, reutilizada en todas las
    # corridas: los generadores memoizan lo que no depende de la semilla
    # (distancias, beta, máscara de localidad). Crear uno por corrida
    # tiraría esa caché y multiplicaría el costo por diez.
    generadores = {r.tipo: crear_generador(r.tipo) for r in config.redes}

    filas: list[dict[str, Any]] = []
    series: list[pd.DataFrame] = []
    t_inicio = time.perf_counter()
    total = config.n_corridas_totales

    logger.info("Experimento '%s': %d configuraciones × %d corridas = %d corridas.",
                config.experiment_id, len(config.redes), config.n_runs, total)

    hecho = 0
    for cfg_red in config.redes:
        for run in range(config.n_runs):
            fila, serie = _una_corrida(
                agentes=agentes, a0=a0, rango=rango,
                generador=generadores[cfg_red.tipo], cfg_red=cfg_red,
                run=run, config=config,
            )
            filas.append(fila)
            if config.guardar_series:
                series.append(serie)
            hecho += 1
            if progreso_cada and hecho % progreso_cada == 0:
                transcurrido = time.perf_counter() - t_inicio
                logger.info("  %d/%d corridas (%.0f%%, %.1fs, ~%.0fs restantes)",
                            hecho, total, 100 * hecho / total, transcurrido,
                            transcurrido * (total - hecho) / hecho)

    duracion = time.perf_counter() - t_inicio
    resultados = pd.DataFrame(filas)
    resultados.to_csv(dir_salida / "resultados.csv", index=False)
    if series:
        pd.concat(series, ignore_index=True).to_csv(dir_salida / "series.csv", index=False)

    resumen = _resumen_por_configuracion(resultados)
    metadata = _metadata(config, agentes, resultados, resumen, duracion, rango)
    with open(dir_salida / "run_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    logger.info("Listo en %.1fs. Resultados en %s", duracion, dir_salida)
    return {"resultados": resultados, "resumen": resumen,
            "metadata": metadata, "dir_salida": dir_salida}


# ----------------------------------------------------------------------


def _cargar_poblacion(config: ConfiguracionExperimento) -> pd.DataFrame:
    path = RAIZ_REPO / config.poblacion
    if not path.exists():
        path = Path(config.poblacion)
    if not path.exists():
        raise FileNotFoundError(
            f"No se encontró la población en '{config.poblacion}'. "
            "Generarla con: python src/population/construir_poblacion.py")
    agentes = pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)

    if "opinion_t0" not in agentes.columns:
        raise ValueError(f"{path.name} no tiene la columna 'opinion_t0' (D12).")
    if config.n_agentes and len(agentes) != config.n_agentes:
        raise ValueError(
            f"La config declara n_agentes={config.n_agentes} pero {path.name} tiene "
            f"{len(agentes)}. Corregir la config o regenerar la población — no se "
            "recorta en silencio.")
    return agentes


def _una_corrida(
    agentes: pd.DataFrame,
    a0: np.ndarray,
    rango: tuple[float, float],
    generador: Any,
    cfg_red: ConfiguracionRed,
    run: int,
    config: ConfiguracionExperimento,
) -> tuple[dict[str, Any], pd.DataFrame]:
    # La semilla depende solo de la identidad de esta corrida, así que
    # agregar configuraciones al barrido no mueve las semillas de las demás.
    seed = semilla_para(config.seed_base, config.experiment_id, cfg_red.id, run)

    red = generador.generar(agentes, seed=seed, **cfg_red.params)
    modelo = crear_modelo(config.opinion_model, red.W, **config.opinion_model_params)
    tray = modelo.simular(a0, n_pasos=config.n_pasos)

    resumen = resumen_opinion(tray.opinion_final)
    polarizacion = indices_polarizacion(tray.opinion_final, rango=rango)
    polarizacion.pop("_params", None)   # van una sola vez, en el metadata

    fila: dict[str, Any] = {
        "config_red": cfg_red.id,
        "tipo_red": cfg_red.tipo,
        "run": run,
        "seed": seed,
        **{f"red_{k}": v for k, v in cfg_red.params.items()},
        "grado_promedio_efectivo": red.grado_promedio,
        "n_aislados": red.n_aislados,
        "pasos_efectivos": tray.pasos_efectivos,
        "convergio": tray.convergio,
        **{f"final_{k}": v for k, v in resumen.items()},
        **{f"pol_{k}": v for k, v in polarizacion.items()},
        "desplazamiento_medio": float(np.abs(tray.opinion_final - a0).mean()),
        "w1_vs_inicial": wasserstein1(tray.opinion_final, a0),
    }
    if "beta_calibrado" in red.parametros:
        fila["red_beta"] = red.parametros["beta_calibrado"]
    if "p_intra" in red.parametros:
        fila["red_p_intra"] = red.parametros["p_intra"]
        fila["red_saturacion_h"] = red.parametros["saturacion_h"]

    serie = pd.DataFrame({
        "config_red": cfg_red.id,
        "run": run,
        "paso": np.arange(len(tray.media)),
        "media": tray.media,
        "desviacion": tray.desviacion,
    })
    return fila, serie


def _resumen_por_configuracion(resultados: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega las corridas de cada configuración a una distribución, que es lo
    que pide RESEARCH.md sección 32: un escenario devuelve un rango de
    resultados, no un número.
    """
    g = resultados.groupby("config_red")
    resumen = pd.DataFrame({
        "tipo_red": g["tipo_red"].first(),
        "n_runs": g.size(),
        "grado_efectivo": g["grado_promedio_efectivo"].mean().round(3),
        "media_final": g["final_media"].mean().round(4),
        "media_final_p05": g["final_media"].quantile(0.05).round(4),
        "media_final_p95": g["final_media"].quantile(0.95).round(4),
        "sd_final": g["final_desviacion"].mean().round(4),
        "sd_final_p05": g["final_desviacion"].quantile(0.05).round(4),
        "sd_final_p95": g["final_desviacion"].quantile(0.95).round(4),
        "esteban_ray": g["pol_esteban_ray"].mean().round(4),
        "n_clusters": g["pol_n_clusters"].mean().round(2),
        "frac_bimodal": g["pol_bimodal"].mean().round(3),
        "frac_convergio": g["convergio"].mean().round(3),
    }).reset_index()
    return resumen


def _metadata(config, agentes, resultados, resumen, duracion, rango) -> dict[str, Any]:
    """Los campos de la sección 35 de PROJECT_CONTEXT.md, más lo que hace
    falta para volver a correr esto exactamente igual."""
    params_pol = indices_polarizacion(agentes["opinion_t0"].to_numpy(float), rango=rango)["_params"]
    return {
        "experiment_id": config.experiment_id,
        "timestamp": pd.Timestamp.now(tz="UTC").isoformat(),
        "runner_version": VERSION_RUNNER,
        "duracion_segundos": round(duracion, 2),
        "poblacion": {
            "archivo": config.poblacion,
            "n_agentes": len(agentes),
            "opinion_t0": resumen_opinion(agentes["opinion_t0"].to_numpy(float)),
        },
        "opinion_model": config.opinion_model,
        "opinion_model_params": config.opinion_model_params,
        "n_pasos": config.n_pasos,
        "n_runs_por_configuracion": config.n_runs,
        "n_configuraciones": len(config.redes),
        "n_corridas_totales": int(len(resultados)),
        "seed_base": config.seed_base,
        "derivacion_de_semillas": (
            "blake2b(seed_base|experiment_id|config_red|run) — ver src/utils/seeds.py. "
            "Agregar configuraciones al barrido no cambia las semillas de las demás."),
        "fuente_de_variabilidad": (
            "La red, y solo la red. Los modelos de opinión son deterministas y la "
            "población es fija dentro del experimento."),
        "configuraciones_red": [{"id": r.id, "tipo": r.tipo, **r.params} for r in config.redes],
        "parametros_polarizacion": params_pol,
        "rango_opinion_usado": list(rango),
        "capa_mesa": "no usada en esta versión — ver DI-E1 en runner.py",
        "resumen_por_configuracion": json.loads(resumen.to_json(orient="records")),
        "config_yaml_original": config.crudo,
    }


# ----------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Ejecuta un experimento del Bogotá Social Simulator.")
    p.add_argument("config", help="ruta al YAML, ej. config/experiment_2.yaml")
    p.add_argument("--n-runs", type=int, default=None, dest="n_runs",
                   help="sobrescribe n_runs (útil para una prueba rápida)")
    p.add_argument("--sin-series", action="store_true",
                   help="no guardar la serie por paso de cada corrida")
    args = p.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")
    # Los generadores de red loguean una línea por corrida: con miles de
    # corridas eso ahoga el progreso del experimento y no aporta nada.
    for modulo in ("src.network", "src.opinion", "src.population"):
        logging.getLogger(modulo).setLevel(logging.WARNING)

    config = cargar_config(args.config)
    if args.n_runs:
        config.n_runs = args.n_runs
        config.experiment_id = f"{config.experiment_id}_prueba{args.n_runs}"
        logger.warning("n_runs sobrescrito a %d; los resultados se guardan como '%s' "
                       "para no pisar la corrida completa.", args.n_runs, config.experiment_id)
    if args.sin_series:
        config.guardar_series = False

    salida = correr_experimento(config)
    print()
    print(salida["resumen"].to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
