"""Genera pósters de Bogotá con prettymaps.

Esto NO es parte del tablero. El mapa interactivo (``plantilla_mapa.html``) y
este generador son dos productos distintos que comparten fuente de datos y
paleta: uno sirve para explorar y el otro para mirar. Un póster no lleva
ninguna cifra del modelo y no puede llevarla — si alguna vez aparece un dato de
opinión sobre una imagen bonita, hay que releer la sección 2 de
``VISUALIZATION_SPECIFICATION.md`` antes de publicarla.

ADVERTENCIA DE LICENCIA
-----------------------
prettymaps es **AGPL-3.0**. Es una licencia con copyleft de red: obliga a
publicar el código fuente de cualquier obra derivada, incluso cuando el
software solo se ofrece por red en vez de distribuirse. Este archivo importa
prettymaps, así que el alcance de esa obligación sobre el resto del proyecto
es una decisión que le corresponde al CNC. Si la respuesta es que no, la
alternativa es ``poster_matplotlib.py``, que dibuja desde los mismos extractos
sin depender de prettymaps.

ESTADO DE VERIFICACIÓN
----------------------
**Este archivo no se ha ejecutado.** Se escribió contra la firma pública de
``prettymaps.plot()`` de la rama principal del repositorio, pero el entorno
donde se redactó no tiene acceso a PyPI ni a Overpass, así que no hay forma de
probarlo aquí. La primera corrida puede pedir ajustes — sobre todo en los
nombres de las capas y en el diccionario de anchos de vía, que son lo más
propenso a cambiar entre versiones. Si algo falla, el error casi siempre
apunta a la capa culpable.

INSTALACIÓN — no desde PyPI
---------------------------
El paquete publicado en PyPI (1.4.2, marzo de 2025) fija ``numpy<1.25``, y
numpy 1.24 no publica ruedas para Python 3.12: pip intenta compilarlo, el
sdist usa un setuptools que llama a ``pkgutil.ImpImporter`` —eliminado en
3.12— y la instalación muere con un AttributeError que no tiene nada que ver
con prettymaps. La rama principal del repositorio ya corrigió esos pines
(``numpy>=1.26.4``, ``osmnx>=2.0.5``, ``python>=3.12``), así que hay que
instalar desde ahí:

    pip install git+https://github.com/marceloprates/prettymaps.git

No sirve instalar 1.4.2 con ``--no-deps`` y poner numpy moderno a mano: esa
versión espera la API de osmnx 1.x y osmnx 2.x le renombró las funciones de
descarga de geometrías. Rompería en la primera capa.

Decisiones de implementación
----------------------------
DI-P1  Las zonas se definen por coordenada y radio, no por nombre de lugar.
       Buscar "Bogotá" por nombre devuelve el polígono del Distrito entero,
       que incluye Sumapaz: el 78 % del área y el 0,04 % de la población
       (DI-V7). Un póster de eso es una mancha rural con la ciudad en una
       esquina.

DI-P2  La paleta es la misma del tablero. No es coquetería: que el póster de
       la portada y el mapa navegable se reconozcan como la misma cosa es
       más barato de mantener que dos identidades visuales.

DI-P3  prettymaps consulta Overpass en vivo a través de osmnx, así que NO usa
       los extractos de ``data/external/geo/osm/``. Son caminos separados a la
       misma fuente. Consecuencia práctica: esto necesita salida a internet, y
       una corrida con radio grande puede tardar varios minutos y a veces
       falla por límite de tasa del servidor. Si pasa, esperar y reintentar.

DI-P4  Sin argumentos genera todas las zonas. El proyecto se corre desde el
       botón Run de VS Code, que no pasa argumentos: un script que falle con
       error de argparse en ese caso es un script que estorba.

DI-P11  Los presets de prettymaps se usan TAL CUAL. La paleta del proyecto
        —verde páramo sobre crema— se queda en el tablero, que es donde el
        color lleva información; el póster adopta el lenguaje de la librería,
        que es de donde viene el aspecto que se reconoce. Son dos identidades
        visuales a propósito: una para leer y otra para mirar.

DI-P12  La zona «ciudad» es la única que no puede usar un preset sin tocarlo.
        Con 11 km de radio, pedir las huellas de edificios son cientos de
        miles de polígonos: Overpass se cae por tiempo de espera, y aunque
        respondiera, a esa escala un edificio mide menos de un píxel. Se
        dibuja sin edificios y con el agua añadida, que a esa escala es lo que
        de verdad estructura la ciudad — el río Bogotá como borde occidental.

Uso
---
    python src/viz/poster.py                 # todas las zonas
    python src/viz/poster.py centro          # una sola
    python src/viz/poster.py --listar
    python src/viz/poster.py --presets       # los presets que trae la librería
    python src/viz/poster.py centro --preset macao

Instalación (una vez, dentro del venv) — ver arriba por qué NO es "pip
install prettymaps":
    pip install git+https://github.com/marceloprates/prettymaps.git
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "data" / "processed" / "viz" / "posters"

# El preset de la librería que se usa por defecto (DI-P11). `--presets` lista
# los que trae instalados; `--preset X` cambia este valor en una corrida.
PRESET = "barcelona"

# --------------------------------------------------------------------------- #
# Zonas (DI-P1)
# --------------------------------------------------------------------------- #
ZONAS = {
    "centro": {
        "punto": (4.5981, -74.0758),
        "radio": 1100,
        "titulo": "Centro histórico",
        "nota": "Plaza de Bolívar · La Candelaria",
    },
    "chapinero": {
        "punto": (4.6465, -74.0629),
        "radio": 1300,
        "titulo": "Chapinero",
        "nota": "Lourdes · carrera Séptima",
    },
    "kennedy": {
        "punto": (4.6285, -74.1497),
        "radio": 1600,
        "titulo": "Kennedy",
        "nota": "Plaza de las Américas",
    },
    "usaquen": {
        "punto": (4.6947, -74.0306),
        "radio": 1200,
        "titulo": "Usaquén",
        "nota": "Plaza fundacional",
    },
    "ciudad": {
        "punto": (4.6500, -74.0950),
        "radio": 11000,
        "titulo": "Bogotá",
        "nota": "La ciudad construida, sin Sumapaz",
        "circular": False,
        # DI-P12: sin edificios, con agua. Estas capas sustituyen a las del
        # preset; el estilo (los colores) sí sigue siendo el del preset.
        "capas": {
            "perimeter": {},
            "streets": {"width": {"motorway": 5, "trunk": 5, "primary": 3,
                                  "secondary": 1.8, "tertiary": 1}},
            "water": {"tags": {"natural": ["water", "bay"], "waterway": "river"}},
            "green": {"tags": {"leisure": ["park", "nature_reserve"],
                               "landuse": ["grass", "forest"], "natural": "wood"}},
        },
    },
}

# --------------------------------------------------------------------------- #
# Paleta — la misma del tablero (DI-P2)
# --------------------------------------------------------------------------- #
PAPEL = "#e9ece7"
TINTA = "#16211c"
PARAMO = "#2f6b5e"
AGUA = "#3d6f8c"
TEJA = "#b2452c"
MURO = "#dfe4dd"

CAPAS = {
    "perimeter": {},
    # DI-P8. Los anchos de la primera corrida (trunk 6, primary 4,5) convertían
    # la Caracas y la Décima en bandas que se comían la retícula. La jerarquía
    # tiene que notarse sin que las troncales tapen la trama del centro, que es
    # lo que hace reconocible a Bogotá.
    "streets": {
        "width": {
            "motorway": 4.5,
            "trunk": 4.5,
            "primary": 3.2,
            "secondary": 2.4,
            "tertiary": 1.8,
            "residential": 1.1,
            "unclassified": 1.1,
            "pedestrian": 0.8,
            "footway": 0.6,
        }
    },
    "building": {"tags": {"building": True, "landuse": "construction"}},
    "water": {"tags": {"natural": ["water", "bay"]}},
    "green": {"tags": {"leisure": ["park", "garden", "pitch"], "landuse": "grass"}},
    "forest": {"tags": {"landuse": "forest", "natural": "wood"}},
}

ESTILO = {
    # DI-P9. El perímetro se rellena con un crema más claro que el papel y se
    # remata con un anillo de tinta. Sin eso el recorte circular solo se nota
    # donde hay edificios, y el póster parece un mapa recortado con tijeras en
    # vez de una pieza.
    "perimeter": {"fill": True, "fc": "#f4f6f2", "ec": TINTA, "lw": 2.5, "zorder": 0},
    "streets": {"fc": TINTA, "ec": TINTA, "lw": 0, "zorder": 4},
    "building": {
        "palette": [MURO, "#cfd6ce", "#bcc5bb"],
        "ec": TINTA,
        "lw": 0.35,
        "zorder": 5,
    },
    "water": {"fc": AGUA, "ec": TINTA, "lw": 0.4, "hatch": "ooo...", "zorder": 3},
    "green": {"fc": PARAMO, "ec": TINTA, "lw": 0.4, "hatch": "ooo...", "alpha": 0.72, "zorder": 2},
    "forest": {"fc": PARAMO, "ec": TINTA, "lw": 0.4, "alpha": 0.9, "zorder": 1},
}

# DI-P10. El crédito de prettymaps se dibuja por defecto arriba a la izquierda
# dentro de una caja con borde, donde choca con el título. Se apaga con
# ``credit=False`` y se rotulan las dos líneas abajo, centradas: el título
# grande y la atribución —que es obligación de la ODbL, no adorno— debajo.
CREDITO = "© colaboradores de OpenStreetMap · ODbL  ·  Bogotá Social Simulator · CNC"


def dibujar(clave: str, preset: str = PRESET):
    import matplotlib.pyplot as plt
    import prettymaps

    z = ZONAS[clave]
    SALIDA.mkdir(parents=True, exist_ok=True)
    destino = SALIDA / f"{clave}_{preset}.png"

    fig, ax = plt.subplots(figsize=(12, 12.9))
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.085)
    fig.patch.set_facecolor(PAPEL)
    ax.set_facecolor(PAPEL)

    extra = {"layers": z["capas"]} if "capas" in z else {}
    prettymaps.plot(
        z["punto"],
        preset=preset,
        radius=z["radio"],
        circle=z.get("circular", True),
        credit=False,
        fig=fig,
        ax=ax,
        show=False,
        **extra,
    )

    fig.text(0.5, 0.050, z["titulo"], ha="center", va="center",
             fontsize=30, color=TINTA)
    fig.text(0.5, 0.020, CREDITO, ha="center", va="center",
             fontsize=9, color="#48564f")
    fig.savefig(destino, dpi=300, facecolor=PAPEL)
    fig.savefig(destino.with_suffix(".svg"), facecolor=PAPEL)
    plt.close(fig)
    print(f"  {clave:<10} {preset:<12} -> {destino.relative_to(RAIZ)}  ({z['radio']} m)")
    return destino


def main() -> None:
    argv = sys.argv[1:]
    preset = PRESET
    if "--preset" in argv:
        i = argv.index("--preset")
        if i + 1 < len(argv):
            preset = argv[i + 1]
            argv = argv[:i] + argv[i + 2:]

    if "--presets" in argv:
        try:
            import prettymaps
            print("presets disponibles:")
            for nombre in prettymaps.presets():
                print(f"  {nombre}")
        except Exception as e:
            print(f"no se pudo listar: {type(e).__name__}: {e}")
        return

    args = [a for a in argv if not a.startswith("-")]
    if "--listar" in sys.argv:
        for k, z in ZONAS.items():
            print(f"  {k:<10} {z['titulo']:<20} radio {z['radio']:>6} m   {z['nota']}")
        return

    claves = args or list(ZONAS)
    desconocidas = [c for c in claves if c not in ZONAS]
    if desconocidas:
        print(f"zona desconocida: {', '.join(desconocidas)}")
        print(f"disponibles: {', '.join(ZONAS)}")
        return

    try:
        import prettymaps  # noqa: F401
    except ImportError:
        print("Falta prettymaps. Dentro del venv, y NO desde PyPI:")
        print("  pip install git+https://github.com/marceloprates/prettymaps.git")
        print("Si no se puede instalar, usa src/viz/poster_matplotlib.py")
        return

    print(f"generando {len(claves)} póster(s) con el preset «{preset}»; "
          f"cada uno consulta Overpass y puede tardar")
    for c in claves:
        try:
            dibujar(c, preset)
        except Exception as e:  # una zona que falle no debe tumbar el resto
            print(f"  {c:<10} FALLÓ: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
