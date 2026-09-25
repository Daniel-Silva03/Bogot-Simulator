"""Arma la página del mapa: plantilla + paquete de datos, en un solo archivo.

La página es autocontenida a propósito (DI-V6): no pide nada a la red salvo las
tipografías, así que se puede abrir desde el disco, publicar como artefacto o
servir desde cualquier parte sin montar un backend. El paquete de datos se
inyecta en el marcador ``/*__DATOS__*/``, la capa base urbana en
``/*__BASE__*/`` y la serie temporal del Hito 2 en ``/*__SERIE__*/``.

Van en dos marcadores y no en uno porque son cosas distintas: ``mapa_bogota.json``
es el dato del proyecto y ``base_bogota.json`` es decorado de orientación tomado
de OpenStreetMap (DI-V8). Mezclarlos invitaría a tratar la capa base como si
fuera una medición más.

Uso:
    python3 src/viz/preparar_mapa.py
    python3 src/viz/preparar_base.py
    python3 src/viz/preparar_serie.py
    python3 src/viz/construir_pagina.py
"""

from __future__ import annotations

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PLANTILLA = RAIZ / "src" / "viz" / "plantilla_mapa.html"
DATOS = RAIZ / "data" / "processed" / "viz" / "mapa_bogota.json"
BASE = RAIZ / "data" / "processed" / "viz" / "base_bogota.json"
SERIE = RAIZ / "data" / "processed" / "viz" / "serie_bogota.json"
SALIDA = RAIZ / "data" / "processed" / "viz" / "mapa_bogota.html"

PIEZAS = {"/*__DATOS__*/": DATOS, "/*__BASE__*/": BASE, "/*__SERIE__*/": SERIE}


def construir() -> Path:
    pagina = PLANTILLA.read_text(encoding="utf-8")
    for marcador, ruta in PIEZAS.items():
        if marcador not in pagina:
            raise RuntimeError(f"la plantilla no contiene el marcador {marcador}")
        if not ruta.exists():
            raise RuntimeError(f"falta {ruta.relative_to(RAIZ)}; corre antes el preparador que lo produce")
        pagina = pagina.replace(marcador, ruta.read_text(encoding="utf-8"))
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(pagina, encoding="utf-8")
    return SALIDA


def main() -> None:
    salida = construir()
    print(f"{salida}  {salida.stat().st_size/1024:.1f} KB")


if __name__ == "__main__":
    main()
