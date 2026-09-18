"""
tests/test_experiments.py

Pruebas de la capa de experimentos: métricas, derivación de semillas,
carga de configuración y el runner de punta a punta.

Lo que importa verificar acá no es que el código corra, sino tres cosas de
las que depende que el Experimento 2 signifique algo:

  1. Los índices de polarización distinguen de verdad una población
     partida en dos de una dispersa — si no, "polarización" en los
     resultados sería una palabra sin contenido.
  2. Las semillas son estables: agregar una configuración al barrido no
     puede cambiar los resultados de las demás.
  3. El runner produce variabilidad entre corridas. Como los modelos de
     opinión son deterministas, si la semilla de red no variara, las 200
     corridas serían idénticas y la distribución de resultados que pide
     RESEARCH.md sección 32 no existiría.

Ejecutar con:  python3 tests/test_experiments.py
"""

import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.experiments.metrics import (
    UMBRAL_BIMODALIDAD,
    bimodalidad_sarle,
    esteban_ray,
    indices_polarizacion,
    ks,
    n_clusters_opinion,
    por_localidad,
    resumen_opinion,
    wasserstein1,
)
from src.experiments.runner import correr_experimento
from src.utils.config import ConfigError, cargar_config, expandir_barrido
from src.utils.seeds import semilla_para

RAIZ = Path(__file__).resolve().parents[1]


def _assert(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"  OK: {msg}")


# ----------------------------------------------------------------------
# métricas
# ----------------------------------------------------------------------


def test_los_indices_distinguen_polarizacion_de_dispersion():
    """El punto de calcular cuatro índices: la desviación estándar NO
    distingue una población repartida de forma pareja de una partida en
    dos bloques, y los otros tres sí."""
    print("\n[test_los_indices_distinguen_polarizacion_de_dispersion]")

    rng = np.random.default_rng(0)
    n = 2000
    # Dos poblaciones con desviación estándar casi idéntica y formas opuestas
    partida = np.concatenate([rng.normal(2.0, 0.25, n // 2), rng.normal(4.0, 0.25, n // 2)])
    dispersa = rng.uniform(partida.min(), partida.max(), n)
    dispersa = (dispersa - dispersa.mean()) / dispersa.std() * partida.std() + partida.mean()

    print(f"    sd partida  = {partida.std():.4f}   sd dispersa = {dispersa.std():.4f}")
    _assert(abs(partida.std() - dispersa.std()) < 0.05,
            "las dos poblaciones de prueba tienen prácticamente la misma desviación")

    bc_p, bc_d = bimodalidad_sarle(partida), bimodalidad_sarle(dispersa)
    print(f"    bimodalidad: partida {bc_p:.3f}   dispersa {bc_d:.3f}   (umbral {UMBRAL_BIMODALIDAD})")
    _assert(bc_p > UMBRAL_BIMODALIDAD,
            f"Sarle detecta la población partida como bimodal ({bc_p:.3f})")

    er_p = esteban_ray(partida, rango=(1, 5))
    er_d = esteban_ray(dispersa, rango=(1, 5))
    print(f"    esteban-ray: partida {er_p:.4f}   dispersa {er_d:.4f}")
    _assert(er_p > er_d,
            "Esteban-Ray asigna más polarización a la población partida que a la dispersa, "
            "con la misma desviación — que es exactamente lo que la desviación no capta")

    nc_p = n_clusters_opinion(partida, umbral=0.25)
    _assert(nc_p == 2, f"el conteo de clusters encuentra los dos grupos (obtuvo {nc_p})")


def test_metricas_en_casos_limite():
    print("\n[test_metricas_en_casos_limite]")

    consenso = np.full(500, 3.0)
    _assert(np.isnan(bimodalidad_sarle(consenso)),
            "con consenso total la bimodalidad es NaN, no un 0 inventado")
    _assert(esteban_ray(consenso, rango=(1, 5)) == 0.0,
            "y Esteban-Ray es exactamente 0: no hay grupos que alienar")
    _assert(n_clusters_opinion(consenso) == 1, "un solo cluster")
    _assert(indices_polarizacion(consenso, rango=(1, 5))["bimodal"] is False,
            "y 'bimodal' es False, no NaN, para que la columna sea booleana")

    # dos grupos separados exactamente en el umbral
    a = np.array([1.0, 1.1, 1.2, 3.0, 3.1])
    _assert(n_clusters_opinion(a, umbral=0.25) == 2,
            "dos grupos claros a mano -> 2 clusters")
    _assert(n_clusters_opinion(a, umbral=5.0) == 1,
            "con un umbral enorme todo es un solo cluster (el umbral es un parámetro libre)")


def test_distancia_entre_distribuciones():
    """Insumo del Experimento 1: comparar simulado contra observado."""
    print("\n[test_distancia_entre_distribuciones]")

    rng = np.random.default_rng(1)
    a = rng.normal(3, 0.5, 5000)
    _assert(wasserstein1(a, a) == 0.0, "W1 de una distribución consigo misma es 0")

    desplazada = a + 0.4
    w = wasserstein1(a, desplazada)
    _assert(abs(w - 0.4) < 0.01,
            f"W1 entre una distribución y la misma desplazada 0,4 vale 0,4 (obtuvo {w:.4f}) "
            "— está en unidades de la variable, que es lo que la hace interpretable")

    b = rng.normal(3, 0.5, 3000)   # tamaño distinto a propósito
    _assert(wasserstein1(a, b) < 0.05,
            "dos muestras de la misma distribución, con tamaños distintos, dan W1 ~ 0")
    _assert(0.0 <= ks(a, b) <= 1.0, "el estadístico KS queda en [0,1]")


def test_desagregacion_por_localidad():
    print("\n[test_desagregacion_por_localidad]")
    agentes = pd.DataFrame({"localidad": ["Suba"] * 5 + ["Sumapaz"] * 2})
    op = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 1.0, 5.0])
    t = por_localidad(agentes, op)
    suba = t[t.localidad == "Suba"].iloc[0]
    _assert(suba.n_agentes == 5 and abs(suba.media - 3.0) < 1e-12,
            "media y conteo por localidad correctos")
    _assert(t.iloc[0].localidad == "Suba",
            "ordenado por número de agentes: la localidad con muestra frágil queda visible al final")


# ----------------------------------------------------------------------
# semillas y configuración
# ----------------------------------------------------------------------


def test_semillas_estables_e_independientes():
    """La razón de no usar `seed_base + i`."""
    print("\n[test_semillas_estables_e_independientes]")

    s1 = semilla_para(42, "exp2", "territorial_h20_k10", 7)
    s2 = semilla_para(42, "exp2", "territorial_h20_k10", 7)
    _assert(s1 == s2, "la misma corrida da siempre la misma semilla")

    _assert(semilla_para(42, "exp2", "territorial_h20_k10", 8) != s1,
            "corridas distintas de la misma configuración usan semillas distintas")
    _assert(semilla_para(42, "exp2", "aleatoria_k10", 7) != s1,
            "configuraciones distintas no comparten semilla en el mismo número de corrida")
    _assert(semilla_para(43, "exp2", "territorial_h20_k10", 7) != s1,
            "cambiar seed_base cambia todo el experimento")

    # lo importante: agregar configuraciones no mueve las semillas de las demás
    antes = [semilla_para(42, "exp2", c, r) for c in ["aleatoria_k5", "homofilica_k5"] for r in range(3)]
    despues = [semilla_para(42, "exp2", c, r)
               for c in ["aleatoria_k5", "territorial_h5_k5", "homofilica_k5"] for r in range(3)]
    _assert(set(antes).issubset(set(despues)),
            "agregar una configuración al barrido NO cambia las semillas de las existentes "
            "— con `seed_base + i` sí cambiarían")


def test_expansion_del_barrido():
    print("\n[test_expansion_del_barrido]")

    sweep = [
        {"tipo": "aleatoria", "k_promedio": [5, 10, 15, 20]},
        {"tipo": "homofilica", "k_promedio": [5, 10, 15, 20]},
        {"tipo": "territorial", "k_promedio": [5, 10, 15, 20], "h": [5, 10, 20, 50]},
    ]
    redes = expandir_barrido(sweep)
    _assert(len(redes) == 24, f"4 + 4 + 4×4 = 24 configuraciones (obtuvo {len(redes)})")
    _assert(len({r.id for r in redes}) == 24, "todos los identificadores son únicos")

    terr = [r for r in redes if r.tipo == "territorial"]
    _assert(all(set(r.params) == {"k_promedio", "h"} for r in terr),
            "las territoriales llevan sus dos parámetros")

    # el identificador no depende del orden en que se escribieron los params
    a = expandir_barrido([{"tipo": "territorial", "k_promedio": 10, "h": 20}])[0]
    b = expandir_barrido([{"tipo": "territorial", "h": 20, "k_promedio": 10}])[0]
    _assert(a.id == b.id,
            f"el id es estable ante el orden de las claves del YAML ('{a.id}')")

    _assert(len(expandir_barrido([{"tipo": "aleatoria"}])) == 1,
            "una entrada sin parámetros produce una sola configuración")


def test_config_valida_y_falla_temprano():
    print("\n[test_config_valida_y_falla_temprano]")

    c = cargar_config(RAIZ / "config" / "experiment_2.yaml")
    _assert(c.n_corridas_totales == 24 * c.n_runs,
            f"la config real del Experimento 2 expande a {c.n_corridas_totales} corridas")
    _assert(c.opinion_model == "friedkin_johnsen" and c.opinion_model_params["phi"] == 0.7,
            "y trae el modelo y el phi declarados")
    _assert(c.rango_opinion == (1.0, 5.0),
            "el rango de la escala queda fijado, para que Esteban-Ray sea comparable "
            "entre configuraciones")

    with tempfile.TemporaryDirectory() as d:
        casos = [
            ("falta una clave requerida", "experiment_id: x\n"),
            ("n_runs no entero",
             'experiment_id: x\npoblacion: p\nopinion_model: degroot\nn_pasos: 10\n'
             'n_runs: "muchos"\nseed_base: 1\nnetwork_sweep: [{tipo: aleatoria}]\n'),
            ("n_pasos en cero",
             'experiment_id: x\npoblacion: p\nopinion_model: degroot\nn_pasos: 0\n'
             'n_runs: 5\nseed_base: 1\nnetwork_sweep: [{tipo: aleatoria}]\n'),
            ("falta network_sweep",
             'experiment_id: x\npoblacion: p\nopinion_model: degroot\nn_pasos: 10\n'
             'n_runs: 5\nseed_base: 1\n'),
            ("entrada del barrido sin 'tipo'",
             'experiment_id: x\npoblacion: p\nopinion_model: degroot\nn_pasos: 10\n'
             'n_runs: 5\nseed_base: 1\nnetwork_sweep: [{k_promedio: 10}]\n'),
        ]
        for descripcion, contenido in casos:
            p = Path(d) / "c.yaml"
            p.write_text(contenido, encoding="utf-8")
            try:
                cargar_config(p)
                raise AssertionError(f"debería haber fallado: {descripcion}")
            except ConfigError as e:
                print(f"  OK: falló como se esperaba — {descripcion}\n       ({str(e)[:85]})")

        try:
            cargar_config(Path(d) / "no_existe.yaml")
            raise AssertionError("debería haber fallado con archivo inexistente")
        except ConfigError:
            print("  OK: falló como se esperaba — archivo de configuración inexistente")


# ----------------------------------------------------------------------
# runner de punta a punta
# ----------------------------------------------------------------------


def test_runner_end_to_end():
    print("\n[test_runner_end_to_end]")

    config = cargar_config(RAIZ / "config" / "experiment_2.yaml")
    config.n_runs = 4
    config.redes = [r for r in config.redes if r.params.get("k_promedio") == 10][:3]
    config.experiment_id = "test_runner"
    config.guardar_series = True

    with tempfile.TemporaryDirectory() as d:
        salida = correr_experimento(config, dir_salida=Path(d), progreso_cada=0)
        res, resumen = salida["resultados"], salida["resumen"]

        _assert(len(res) == len(config.redes) * 4,
                f"una fila por corrida ({len(res)} filas)")
        _assert(res["seed"].nunique() == len(res),
                "cada corrida usó una semilla distinta")

        # LA verificación central: hay variabilidad, y viene de la red
        por_config = res.groupby("config_red")["final_desviacion"].nunique()
        _assert((por_config > 1).all(),
                "dentro de cada configuración, las corridas dan resultados distintos "
                "— la variabilidad viene de la realización de la red")

        _assert(set(["media_final_p05", "media_final_p95"]).issubset(resumen.columns),
                "el resumen reporta un rango entre corridas, no solo un promedio "
                "(RESEARCH.md sección 32)")

        d_salida = salida["dir_salida"]
        for archivo in ("resultados.csv", "series.csv", "run_metadata.json"):
            _assert((d_salida / archivo).exists(), f"escribió {archivo}")

        series = pd.read_csv(d_salida / "series.csv")
        _assert(len(series) == len(res) * (config.n_pasos + 1),
                "la serie por paso tiene todos los pasos de todas las corridas")

        meta = json.loads((d_salida / "run_metadata.json").read_text(encoding="utf-8"))
        for clave in ("experiment_id", "timestamp", "seed_base", "opinion_model",
                      "n_pasos", "n_corridas_totales", "poblacion",
                      "parametros_polarizacion", "config_yaml_original"):
            _assert(clave in meta, f"la metadata registra '{clave}' (sección 35)")
        _assert("fuente_de_variabilidad" in meta,
                "y deja escrito de dónde sale la variabilidad entre corridas")


def test_runner_es_reproducible():
    """Sección 26 del prompt maestro: la misma configuración tiene que dar
    exactamente los mismos números."""
    print("\n[test_runner_es_reproducible]")

    def correr():
        config = cargar_config(RAIZ / "config" / "experiment_2.yaml")
        config.n_runs = 3
        config.redes = config.redes[:2]
        config.experiment_id = "test_repro"
        config.guardar_series = False
        with tempfile.TemporaryDirectory() as d:
            return correr_experimento(config, dir_salida=Path(d), progreso_cada=0)["resultados"]

    a, b = correr(), correr()
    numericas = [c for c in a.columns if pd.api.types.is_numeric_dtype(a[c])]
    texto = [c for c in a.columns if c not in numericas]
    _assert(np.allclose(a[numericas].to_numpy(dtype=float), b[numericas].to_numpy(dtype=float)),
            f"las {len(numericas)} columnas numéricas coinciden exactamente entre ejecuciones")
    _assert(a[texto].equals(b[texto]),
            f"y también las de texto ({texto})")


if __name__ == "__main__":
    test_los_indices_distinguen_polarizacion_de_dispersion()
    test_metricas_en_casos_limite()
    test_distancia_entre_distribuciones()
    test_desagregacion_por_localidad()
    test_semillas_estables_e_independientes()
    test_expansion_del_barrido()
    test_config_valida_y_falla_temprano()
    test_runner_end_to_end()
    test_runner_es_reproducible()
    print("\nTodos los tests pasaron.")
