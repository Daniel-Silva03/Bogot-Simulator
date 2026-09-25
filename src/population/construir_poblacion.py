"""
src/population/construir_poblacion.py

Pipeline de punta a punta de la población sintética. Es el script que
produjo `data/processed/poblacion_sintetica_v2.csv`.

    data/raw/  ──> loader ──> muestreo ──> hot-deck ──> build_agents ──> data/processed/

Existe por la misma razón que existe el script de extracción: sin él, la
población sería un archivo que nadie puede rehacer ni auditar. La sección
35 de PROJECT_CONTEXT.md lo pide explícitamente.

Uso (desde la raíz del repositorio):

    python src/population/construir_poblacion.py
    python src/population/construir_poblacion.py --n 5000 --seed 7 --nombre-base poblacion_5k

Las decisiones metodológicas que aplica están todas registradas, no
escondidas acá:

    D11  la variable de opinión es confianza institucional
    D12  el agente tiene exactamente los 7 campos de CAMPOS_D12
    D14  el muestreo es proporcional al factor de expansión (PPS sistemático)
    A05  `opinion_t0` sale con su ficha de escala en el metadata
         (`escala_opinion`): qué pregunta la produjo, en qué rango, con
         qué dirección y sobre cuántos ítems. Antes el CSV entregaba una
         columna de números entre 1 y 5 que solo era interpretable
         leyendo el código.
    A15  `estrato` queda FUERA de las variables de distancia porque el
         donante no lo trae — decisión de esta corrida, registrada en el
         metadata, no una solución de fondo. La consecuencia (opinion_t0 es
         independiente de estrato por construcción) está en
         POPULATION_SPECIFICATION.md sección 8.5.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import numpy as np

RAIZ_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ_REPO))

from src.population.build_agents import (  # noqa: E402
    build_agents,
    guardar_poblacion_sintetica,
)
from src.population.ecp import (  # noqa: E402
    COLUMNA_EDUCACION_MATCH,
    ETIQUETAS_ITEMS,
    ITEMS_UTILES,
    armonizar_educacion_proyecto,
    donante_ecp,
    resumen_n_items,
)
from src.population.epc_bcv import (  # noqa: E402
    COLUMNA_EDAD_BANDA,
    FACTOR_POR_ANIO,
    ITEMS as ITEMS_EPC,
    bandear_edad,
    donante_epc,
)
from src.population.loader import (  # noqa: E402
    load_confianza_institucional_donante,
    load_multiproposito_receptor,
)
from src.population.matching import hot_deck_match  # noqa: E402
from src.population.muestreo import (  # noqa: E402
    cargar_marginal,
    diagnostico_territorial,
    muestrear,
)

DIR_RAW = RAIZ_REPO / "data" / "raw"
DIR_PROCESSED = RAIZ_REPO / "data" / "processed"

RECEPTOR = DIR_RAW / "em2021_receptor_v2.csv"
DONANTE = DIR_RAW / "base_encuestaconfianza_2024-2025.csv"

DIR_ECP = DIR_RAW / "ecp"

OPINION_COL = "confianza_institucional"   # D11

# A15: el donante de la Veeduría no trae estrato, así que no puede usarse
# como variable de distancia con ese donante.
DISTANCE_VARS = ["edad", "nivel_educativo"]

# Con el donante ECP sí hay estrato, y en cambio no hay localidad. Las dos
# diferencias tiran en direcciones opuestas y las dos son reales:
#   + cierra el vacío de A15 para esta corrida
#   - el emparejamiento exacto pierde localidad y queda solo con sexo
# La educación se empareja en la escala armonizada de 5 niveles, porque la
# ECP no distingue técnica/tecnológica de universitaria (ecp.py, DI-C7).
DISTANCE_VARS_ECP = ["edad", "estrato", COLUMNA_EDUCACION_MATCH]
EXACT_MATCH_VARS_ECP = ["sexo"]

# Con el donante EPC (Bogotá Cómo Vamos) no hay educación y la edad viene en
# bandas; localidad existe pero no se usa. Los tres porqués están en DI-B8,
# DI-B9 y DI-B10 de src/population/epc_bcv.py.
DISTANCE_VARS_EPC = [COLUMNA_EDAD_BANDA, "estrato"]
EXACT_MATCH_VARS_EPC = ["sexo"]

logger = logging.getLogger("construir_poblacion")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Construye la población sintética de punta a punta.")
    p.add_argument("--n", type=int, default=1000, help="número de agentes (default: 1000)")
    p.add_argument("--seed", type=int, default=42, help="semilla; sin ella la corrida no es reproducible")
    p.add_argument("--nombre-base", default="poblacion_sintetica_v2", dest="nombre_base")
    p.add_argument("--version", default="v0.2-prototipo-1000-ponderado", dest="dataset_version")
    p.add_argument("--metodo-muestreo", default="auto", dest="metodo",
                   help="auto | ponderado | estratificado | aleatorio (ver D14)")
    p.add_argument("--donante", default="veeduria",
                   help="veeduria (default) | ecp:<año> | epc:<año>[:<item>], "
                        "p.ej. ecp:2017 (Exp. 3A) o epc:2014 (Exp. 7)")
    args = p.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")

    usa_ecp = args.donante.startswith("ecp")
    usa_epc = args.donante.startswith("epc")
    anio_ecp = int(args.donante.split(":")[1]) if usa_ecp and ":" in args.donante else 2017
    partes_epc = args.donante.split(":")
    anio_epc = int(partes_epc[1]) if usa_epc and len(partes_epc) > 1 else 2014
    item_epc = partes_epc[2] if usa_epc and len(partes_epc) > 2 else "gestion_alcalde"

    if not RECEPTOR.exists():
        print(f"Falta el receptor: {RECEPTOR}\n"
              f"Generarlo con 'python src/population/extraer_columnas_em2021.py multiproposito'.")
        return 1
    if usa_ecp:
        if not (DIR_ECP / str(anio_ecp)).is_dir():
            print(f"Falta la ECP {anio_ecp}: {DIR_ECP / str(anio_ecp)}\n"
                  f"Ver DATA_INVENTORY.md sección 10.")
            return 1
    elif usa_epc:
        pass   # epc_bcv.resolver_dir_bcv da un error explícito si falta
    elif not DONANTE.exists():
        print(f"Falta el donante: {DONANTE}\nVer DATA_INVENTORY.md.")
        return 1

    # --- 1. receptor -----------------------------------------------------
    receptor = load_multiproposito_receptor(RECEPTOR)

    # --- 2. muestreo (D14) ----------------------------------------------
    muestra = muestrear(receptor, args.n, seed=args.seed, metodo=args.metodo)
    logger.info("%s", muestra.reporte())

    # agent_id secuencial 0..N-1: tras muestrear, los heredados son los de la
    # fila del receptor y quedan dispersos. Renumerar evita que alguien los
    # use como índice posicional más adelante. La trazabilidad no se pierde:
    # la muestra se reproduce con la semilla y el método, ambos en el metadata.
    agentes_muestra = muestra.agentes.copy()
    agentes_muestra["agent_id"] = np.arange(len(agentes_muestra))

    # --- 3. donante y hot-deck ------------------------------------------
    if usa_ecp:
        donante = donante_ecp(DIR_ECP, anio_ecp)
        # La escala armonizada tiene que existir en los DOS lados, o el
        # hot-deck empareja contra una columna que el receptor no tiene.
        agentes_muestra[COLUMNA_EDUCACION_MATCH] = armonizar_educacion_proyecto(
            agentes_muestra["nivel_educativo"])
        distance_vars = DISTANCE_VARS_ECP
        exact_match_vars = EXACT_MATCH_VARS_ECP
        items = resumen_n_items(donante)
        # El texto viejo decía "13 ítems" como si todos hubieran respondido
        # los 13. El 86,7 % sí; el resto promedia menos (A05 / DI-C11).
        donante_fuente = (
            f"Encuesta de Cultura Política {anio_ecp} (DANE), submuestra de "
            f"Bogotá (REGION=1), índice de confianza sobre hasta "
            f"{items['items_utiles']} ítems de P5263S* "
            f"(mínimo {items['min_items_exigido']} por persona; "
            f"{items['completos_pct']:.0f}% respondió los {items['items_utiles']}), "
            f"ponderada por FEX_P")
        escala_opinion = {
            "concepto": "Confianza institucional",
            "pregunta": (
                "¿Cuánta confianza tiene usted en cada una de las siguientes "
                "instituciones? — ECP, capítulo Democracia"),
            "rango": [1, 5],
            "anclas": {"1": "no confía", "5": "confía mucho"},
            "direccion": "mayor = más confianza",
            "construccion": (
                "promedio simple de los ítems que la persona respondió en la "
                "escala 1-5; el código 99 (no sabe/no responde) queda fuera del "
                "promedio, no se imputa"),
            "instituciones": [ETIQUETAS_ITEMS[i] for i in ITEMS_UTILES],
            "n_items": items,
            "no_es": (
                "No es un porcentaje ni una probabilidad. Un 3,0 es el punto "
                "medio de la escala, no «30 % de confianza»."),
        }
    elif usa_epc:
        # El ítem se renombra al hueco genérico de opinión del pipeline. No es
        # confianza institucional y el metadata lo dice: `donante_fuente` nombra
        # el ítem real. Se renombra en vez de propagar un nombre nuevo por todo
        # el pipeline porque el hueco ya es genérico; lo que no puede pasar es
        # que alguien lea el CSV y crea que es la variable de D11.
        donante = donante_epc(anio_epc, item=item_epc).rename(
            columns={item_epc: OPINION_COL})
        agentes_muestra[COLUMNA_EDAD_BANDA] = bandear_edad(agentes_muestra["edad"])
        distance_vars = DISTANCE_VARS_EPC
        exact_match_vars = EXACT_MATCH_VARS_EPC
        donante_fuente = (f"Encuesta de Percepción Ciudadana {anio_epc} "
                          f"(Bogotá Cómo Vamos), ítem «{item_epc}», escala 1-5, "
                          f"ponderada por {FACTOR_POR_ANIO[anio_epc]}")
        escala_opinion = {
            "concepto": ITEMS_EPC[item_epc]["etiqueta"],
            "pregunta": ITEMS_EPC[item_epc]["etiqueta"],
            "rango": [1, 5],
            "anclas": {"1": "muy mala gestión", "5": "muy buena gestión"},
            "direccion": "mayor = mejor evaluación",
            "construccion": "ítem único, sin promediar",
            "n_items": {"items_utiles": 1, "min_items_exigido": 1},
            "no_es": (
                "No es confianza institucional (D11): es evaluación de gestión. "
                "Ocupa el mismo hueco del pipeline, pero no es la misma variable."),
        }
    else:
        donante = load_confianza_institucional_donante(DONANTE)
        distance_vars = DISTANCE_VARS
        exact_match_vars = None      # usa el default de matching.py
        donante_fuente = "Encuesta de Confianza Institucional 2024-2025 (Veeduría Distrital)"
        escala_opinion = {
            "concepto": "Confianza institucional",
            "rango": [1, 5],
            "direccion": "mayor = más confianza",
            "construccion": (
                "promedio de los ítems de confianza del instrumento de la "
                "Veeduría; el denominador varía entre 1 y 8 ítems y ese número "
                "NO se registra por fila — ver POPULATION_SPECIFICATION.md "
                "§8.4. Es la parte de A05 que sigue abierta con este donante."),
            "n_items": {"min_items_exigido": 1, "advertencia": "denominador de 1 a 8, sin registrar"},
        }

    matching = hot_deck_match(
        agentes_muestra, donante, OPINION_COL,
        exact_match_vars=exact_match_vars,
        distance_vars=distance_vars, random_state=args.seed,
        # DI-M1: con variables de distancia discretas los empates son masivos.
        # Sortearlos proporcional al factor de expansión es lo que hace que la
        # opinión donada siga la distribución ponderada del donante.
        peso_col="factor_expansion",
    )
    logger.info("%s", matching.reporte())

    # --- 4. agentes D12 + validación ------------------------------------
    agentes = build_agents(matching, opinion_col=OPINION_COL)   # valida por dentro

    # --- 5. diagnóstico territorial -------------------------------------
    marginal = cargar_marginal()
    diag = None
    if marginal is None:
        logger.warning(
            "Sin marginal territorial: no se puede verificar la composición de la "
            "muestra. Generarlo con 'extraer_columnas_em2021.py proyecciones'.")
    else:
        diag = diagnostico_territorial(agentes, marginal)
        n = int(diag["observado"].sum())
        distancia = float((diag["observado"] / n - diag["esperado"] / n).abs().sum() / 2)
        logger.info("Distancia territorial al marginal real: %.4f (0 = perfecto)", distancia)
        peores = diag.reindex(diag["sesgo"].sub(1).abs().sort_values(ascending=False).index).head(3)
        for r in peores.itertuples():
            logger.info("  %-20s esperado %6.1f  observado %4d  sesgo %.2f",
                        r.localidad, r.esperado, r.observado, r.sesgo)

    # --- 6. guardar ------------------------------------------------------
    meta_muestreo = dict(muestra.metadata)
    meta_muestreo["metodo"] = muestra.metodo
    meta_muestreo["agent_id"] = (
        "reasignado 0..N-1 tras el muestreo; no corresponde a la fila del receptor. "
        "La muestra se reproduce con seed_muestreo + metodo.")

    ruta = guardar_poblacion_sintetica(
        agentes, matching,
        output_dir=DIR_PROCESSED,
        dataset_version=args.dataset_version,
        receptor_fuente="Encuesta Multipropósito 2021 (SDP/DANE), extracto con FEX_C",
        donante_fuente=donante_fuente,
        distance_vars_usadas=distance_vars,
        random_state=args.seed,
        nombre_base=args.nombre_base,
        muestreo_metadata=meta_muestreo,
        diagnostico_territorial=diag,
        escala_opinion=escala_opinion,
    )
    print(f"\nListo: {ruta} ({len(agentes)} agentes)")
    print(f"       {ruta.parent / (args.nombre_base + '_metadata.json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
