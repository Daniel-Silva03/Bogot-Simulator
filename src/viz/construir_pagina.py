"""Arma la página del mapa: plantilla + paquete de datos, en un solo archivo.

La página es autocontenida a propósito (DI-V6): no pide nada a la red salvo las
tipografías, así que se puede abrir desde el disco, publicar como artefacto o
servir desde cualquier parte sin montar un backend. El paquete de datos se
inyecta en el marcador ``/*__DATOS__*/``.

Uso:
    python3 src/viz/construir_pagina.py
"""

from __future__ import annotations

from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PLANTILLA = RAIZ / "src" / "viz" / "plantilla_mapa.html"
DATOS = RAIZ / "data" / "processed" / "viz" / "mapa_bogota.json"
SALIDA = RAIZ / "data" / "processed" / "viz" / "mapa_bogota.html"

MARCADOR = "/*__DATOS__*/"


def construir() -> Path:
    plantilla = PLANTILLA.read_text(encoding="utf-8")
    if MARCADOR not in plantilla:
        raise RuntimeError(f"la plantilla no contiene el marcador {MARCADOR}")
    datos = DATOS.read_text(encoding="utf-8")
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(plantilla.replace(MARCADOR, datos), encoding="utf-8")
    return SALIDA


def main() -> None:
    salida = construir()
    print(f"{salida}  {salida.stat().st_size/1024:.1f} KB")


if __name__ == "__main__":
    main()
