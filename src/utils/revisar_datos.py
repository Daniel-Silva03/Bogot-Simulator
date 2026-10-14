"""Dice qué datos tiene esta máquina, qué le falta y exactamente dónde va cada cosa.

`data/raw/` está en `.gitignore` a propósito (confidencialidad, terceros y
tamaño — ver el encabezado del propio `.gitignore`), así que un `git clone`
trae el código sin los datos. Eso es correcto y es la causa de que un
preparador falle en una máquina recién clonada.

Este script existe para que esa situación se diagnostique en diez segundos en
vez de leyendo tres documentos: imprime, fuente por fuente, si está o no, la
ruta exacta donde el código la busca, y de dónde se baja.

    python src/utils/revisar_datos.py            # el estado
    python src/utils/revisar_datos.py --arbol    # además, las carpetas a crear

Desde el 1/10/2026 revisa también lo que necesita la página actual (D17): las poblaciones
EPC, las librerías, la clave de OpenRouter y las cachés de la API. Para pasar a otro
computador: `docs/TRASLADO.md`.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

OK, NO, OPC = "OK ", "FALTA", "opc"

#: (clave, para qué sirve, ruta relativa, cómo comprobar, de dónde se baja)
#: El orden es el de utilidad: lo de arriba desbloquea más cosas.
FUENTES = [
    ("geo",
     "Geometría de las 20 localidades — sin esto no hay mapa",
     "data/external/geo/localidades_bogota.geojson", "archivo", True,
     "Va versionada en el repo; si falta, es que el clone quedó incompleto."),
    ("marginal",
     "Marginal territorial (población 18+ por localidad)",
     "data/external/marginal_localidad_18mas.csv", "archivo", True,
     "Va versionado en el repo. Se regenera con "
     "'extraer_columnas_em2021.py proyecciones' desde el anexo DANE-SDP."),
    ("osm",
     "Capa base urbana del mapa (vías, verde, agua)",
     "data/external/geo/osm", "carpeta", False,
     "Extractos de Overpass/OpenStreetMap. Son solo dibujo: sin ellos el mapa "
     "funciona, se ve sin calles ni parques."),
    ("ecp",
     "ECP DANE — la serie de confianza y el donante de opinión",
     "data/raw/ecp", "ecp", True,
     "microdatos.dane.gov.co/index.php/catalog/<cat>/get-microdata — "
     "catálogos 283 (2013), 515 (2017), 644 (2019), 730 (2021), 822 (2023)."),
    ("epc",
     "EPC Bogotá Cómo Vamos — la serie de gestión",
     "data/raw/bogota_como_vamos/empaquetado_2026-09/"
     "Encuesta de Percepción Ciudadana/Microdatos 2014 - 2025", "carpeta", False,
     "Entrega de BCV (no es descarga pública). Si la tienes en otra ruta, "
     "exporta BSS_EPC_DIR en vez de moverla."),
    ("receptor",
     "Extracto de Multipropósito 2021 — receptor del hot-deck",
     "data/raw/em2021_receptor_v2.csv", "archivo", False,
     "Se genera con 'extraer_columnas_em2021.py multiproposito' desde "
     "em2021.csv (1,25 GB, catálogo 743 de DANE)."),
    ("veeduria",
     "Encuesta de Confianza Institucional (Veeduría) — donante alterno",
     "data/raw/base_encuestaconfianza_2024-2025.csv", "archivo", False,
     "datosabiertos.bogota.gov.co, «Base de Datos Encuesta Confianza "
     "Entidades Distritales». CC BY-SA 4.0."),
    ("poblacion",
     "Población sintética ya construida (la que alimenta el mapa)",
     "data/processed/poblacion_ecp2013.csv", "archivo", False,
     "La produce construir_poblacion.py, o llega en el entregable junto con "
     "su _metadata.json — los dos, o preparar_mapa.py no puede etiquetar la "
     "escala."),
]

#: La página actual (D17) y sus experimentos: (para qué, ruta, en el repo, cómo se rehace).
PAGINA = [
    ("Inventario de preguntas de la EPC", "data/processed/epc_inventario/items.csv", True,
     "python src/population/inventario_epc.py"),
    ("Armonización 2022-2025", "data/processed/epc_armonizado/items.csv", True,
     "python src/population/armonizar_epc.py"),
    ("Catálogo de 102 preguntas", "data/processed/poblacion_epc2023/catalogo.json", True,
     "python src/population/poblacion_epc.py"),
    ("Catálogo de la página (84 preguntas)", "data/processed/poblacion_epc2022_2025/catalogo.json", True,
     "python src/population/poblacion_epc_olas.py --con-2025"),
    ("Población 2022-2025: agentes (la de la página)", "data/processed/poblacion_epc2022_2025/agentes.parquet", False,
     "python src/population/poblacion_epc_olas.py --con-2025  (unos minutos; necesita EPC y receptor)"),
    ("Población 2022-2025: donantes", "data/processed/poblacion_epc2022_2025/donantes.parquet", False,
     "python src/population/poblacion_epc_olas.py --con-2025"),
    ("Resultados de las encuestas electorales del CNC (intención de voto)", "data/processed/banco/reales_guardado_lote7.json",
     False, "se llevan con el traslado; nunca van a GitHub (D21)"),
    ("Población 2023: agentes", "data/processed/poblacion_epc2023/agentes.parquet", False,
     "python src/population/poblacion_epc.py"),
    ("Diccionario de la ECP 2023 (banco de preguntas)", "data/raw/ecp/2023/DANE-DIMPE-ECP-2023.xml", False,
     "microdatos.dane.gov.co/index.php/metadata/export/822/ddi (982 KB)"),
]

#: Respuestas ya pagadas a la API. Sin ellas el código corre igual, pero rehacer un análisis
#: vuelve a gastar y el modelo no responde idéntico dos veces.
CACHES = [
    ("página (reformulación y puente)", "data/processed/consulta/cache.json"),
    ("validación de la reformulación", "data/processed/reformulacion/cache.json"),
    ("puente (12 escondidas)", "data/processed/puente/cache.json"),
    ("puente sin base", "data/processed/puente_sin_base/cache.json"),
    ("preguntas reales (metro, Corredor)", "data/processed/preguntas_reales/cache.json"),
    ("banco: clasificación", "data/processed/banco/cache.json"),
    ("práctica del puente (USD 2,33)", "data/processed/practica_puente/cache.json"),
    ("Experimento 9", "data/processed/exp9/cache.json"),
]

LIBRERIAS = ["pandas", "numpy", "sklearn", "scipy", "pyarrow", "yaml", "openpyxl"]

#: Años de la ECP que el proyecto sabe leer (2015 se detecta y se excluye sola).
ANIOS_ECP = (2013, 2017, 2019, 2021, 2023)

#: Lo que produce cada preparador, para decir qué se puede correr y qué no.
PREPARADORES = [
    ("src/viz/preparar_base.py", ("osm",), "la capa base urbana"),
    ("src/population/construir_poblacion.py", ("receptor", "ecp"), "la población sintética"),
    # No basta la geometría: preparar_mapa.py lee la población y su metadata.
    ("src/viz/preparar_mapa.py", ("geo", "marginal", "poblacion"), "el paquete del mapa"),
    ("src/viz/preparar_serie.py", ("ecp",), "la serie temporal del Hito 2"),
    ("src/viz/construir_pagina.py", (), "la página final"),
]

#: Lo que la página necesita ya construido si no se corren los preparadores.
PAQUETES = [
    "data/processed/viz/mapa_bogota.json",
    "data/processed/viz/base_bogota.json",
    "data/processed/viz/serie_bogota.json",
]


def _existe(clave: str, rel: str, modo: str) -> bool:
    if clave == "epc" and os.environ.get("BSS_EPC_DIR"):
        return Path(os.environ["BSS_EPC_DIR"]).exists()
    p = RAIZ / rel
    if modo == "archivo":
        return p.is_file()
    if modo == "carpeta":
        return p.is_dir() and any(p.iterdir())
    if modo == "ecp":
        return any((p / str(a)).is_dir() for a in ANIOS_ECP)
    return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--arbol", action="store_true",
                    help="imprime el árbol de carpetas a crear")
    args = ap.parse_args(argv)

    print(f"Repositorio: {RAIZ}\n")
    estado = {}
    print("FUENTES")
    for clave, para, rel, modo, necesaria, donde in FUENTES:
        hay = _existe(clave, rel, modo)
        estado[clave] = hay
        marca = OK if hay else (NO if necesaria else OPC)
        print(f"  [{marca}] {para}")
        print(f"          {rel}")
        if clave == "ecp":
            presentes = [a for a in ANIOS_ECP if (RAIZ / rel / str(a)).is_dir()]
            print(f"          años en disco: {presentes or 'ninguno'} "
                  f"(de {list(ANIOS_ECP)})")
        if clave == "epc" and os.environ.get("BSS_EPC_DIR"):
            print(f"          BSS_EPC_DIR = {os.environ['BSS_EPC_DIR']}")
        if not hay:
            print(f"          → {donde}")

    print("\nQUÉ PUEDES CORRER")
    for script, necesita, produce in PREPARADORES:
        faltan = [c for c in necesita if not estado.get(c)]
        if faltan:
            print(f"  [{NO}] {script}")
            print(f"          le falta: {', '.join(faltan)} — usa el entregable ya construido")
        else:
            print(f"  [{OK}] {script}  → {produce}")

    print("\nPAQUETES YA CONSTRUIDOS (lo que la página necesita si no corres los preparadores)")
    for rel in PAQUETES:
        print(f"  [{OK if (RAIZ / rel).is_file() else NO}] {rel}")

    print("\nLA PÁGINA ACTUAL (D17)")
    import importlib.util
    faltan_lib = [m for m in LIBRERIAS if importlib.util.find_spec(m) is None]
    print(f"  [{OK if not faltan_lib else NO}] librerías de requirements.txt"
          + (f" — faltan: {', '.join(faltan_lib)} → pip install -r requirements.txt" if faltan_lib else ""))
    for para, rel, en_repo, como in PAGINA:
        hay = (RAIZ / rel).is_file()
        print(f"  [{OK if hay else NO}] {para}{'' if en_repo else '  (no está en GitHub)'}")
        if not hay:
            print(f"          {rel}\n          → {como}")
    clave = bool((os.environ.get("OPENROUTER_API_KEY") or "").strip())
    print(f"  [{OK if clave else OPC}] clave de OpenRouter en OPENROUTER_API_KEY"
          + ("" if clave else " — sin ella: servidor.py --simulado"))
    elec = os.environ.get("BSS_ELECTORAL_DIR")
    print(f"  [{OK if elec and Path(elec).exists() else OPC}] carpeta electoral del CNC en BSS_ELECTORAL_DIR"
          + ("" if elec else " — solo para Polos 2026 y la segunda vuelta"))
    print("\nCACHÉS DE LA API (no están en GitHub; se copian con src/utils/empacar_traslado.py)")
    for para, rel in CACHES:
        print(f"  [{OK if (RAIZ / rel).is_file() else OPC}] {para}")

    if args.arbol:
        print("\nÁRBOL — crea estas carpetas y deja los archivos tal como vienen")
        print("""
data/
├── external/                          ← esto SÍ viene en el repo
│   ├── marginal_localidad_18mas.csv
│   └── geo/
│       ├── localidades_bogota.geojson
│       └── osm/{vias,verde,agua}.geojson
└── raw/                               ← esto NO viene: se baja aparte
    ├── ecp/
    │   ├── 2013/{Tabla viviendas,Caracteristicas generales,Democracia}/
    │   ├── 2017/...
    │   ├── 2019/...   (+ Participacion, Capital social)
    │   ├── 2021/...
    │   └── 2023/...
    ├── bogota_como_vamos/empaquetado_2026-09/
    │   └── Encuesta de Percepción Ciudadana/
    │       └── Microdatos 2014 - 2025/EPC_<año>_microdatos.dta
    ├── em2021_receptor_v2.csv
    └── base_encuestaconfianza_2024-2025.csv

La ECP se descomprime tal cual viene del DANE: el cargador localiza los
módulos por nombre normalizado (sin tildes ni mayúsculas), así que no hay
que renombrar nada — ni siquiera la errata de DANE
«Caracteríasticas generales.csv» de 2023.""")

    faltan_necesarias = [c for c, _, _, _, n, _ in FUENTES if n and not estado[c]]
    if faltan_necesarias:
        print(f"\nFaltan fuentes necesarias: {', '.join(faltan_necesarias)}. "
              f"Con los paquetes ya construidos la página igual se arma.")
        return 1
    print("\nTodo lo necesario está en disco.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
