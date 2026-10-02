"""Empaca lo pequeño que solo existe en este computador, para llevarlo a otro (`docs/TRASLADO.md`).

GitHub trae el código, los documentos y los resultados publicables. No trae, por regla, lo que
está en `.gitignore`: los datos fuente (`data/raw/`, ~1,3 GB, y la carpeta del CNC, ~1,8 GB),
que se copian aparte, y lo pequeño que se produjo aquí y que este script junta en un zip:

- las **cachés de la API**: las respuestas ya pagadas (sin ellas, rehacer un análisis vuelve a
  gastar y el modelo no responde idéntico dos veces);
- las **poblaciones ya construidas** (`.parquet`), que se pueden regenerar pero tardan;
- los resultados locales de experimentos anteriores;
- el diccionario de la ECP 2023 (`data/raw/ecp/2023/DANE-DIMPE-ECP-2023.xml`).

No entra nada de `*/simulado/` (se rehace sin gasto) ni ejecutables.

    python src/utils/empacar_traslado.py                         # crea el zip en el Escritorio
    python src/utils/empacar_traslado.py --extraer ZIP           # en el otro computador, dentro del repo
    python src/utils/empacar_traslado.py --extraer ZIP --sobrescribir
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
EXTRA = ["data/raw/ecp/2023/DANE-DIMPE-ECP-2023.xml"]
FUERA = ("/simulado/",)
EXTENSIONES_FUERA = (".exe", ".tmp")


def archivos() -> list[str]:
    """Lo que git ignora dentro de data/processed, menos lo simulado y los ejecutables, más EXTRA."""
    r = subprocess.run(["git", "ls-files", "--others", "--ignored", "--exclude-standard", "data/processed"],
                       cwd=RAIZ, capture_output=True, text=True, check=True)
    lista = [f for f in r.stdout.splitlines()
             if f and not any(x in f for x in FUERA) and not f.lower().endswith(EXTENSIONES_FUERA)]
    return sorted(lista + [e for e in EXTRA if (RAIZ / e).is_file()])


def empacar(destino: Path) -> list[str]:
    lista = archivos()
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for f in lista:
            z.write(RAIZ / f, f)
    return lista


def extraer(zip_: Path, sobrescribir: bool = False) -> tuple[list[str], list[str]]:
    puestos, saltados = [], []
    with zipfile.ZipFile(zip_) as z:
        for n in z.namelist():
            destino = (RAIZ / n).resolve()
            if RAIZ.resolve() not in destino.parents:
                raise ValueError(f"Ruta fuera del repositorio en el zip: {n}")
            if destino.exists() and not sobrescribir:
                saltados.append(n)
                continue
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(z.read(n))
            puestos.append(n)
    return puestos, saltados


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--destino", type=Path, default=Path.home() / "Desktop" / f"bss_traslado_{date.today().isoformat()}.zip")
    ap.add_argument("--extraer", type=Path, help="zip a desempacar dentro del repositorio")
    ap.add_argument("--sobrescribir", action="store_true", help="al extraer, reemplaza lo que ya exista")
    args = ap.parse_args(argv)
    if args.extraer:
        puestos, saltados = extraer(args.extraer, args.sobrescribir)
        print(f"{len(puestos)} archivos puestos en el repositorio; {len(saltados)} ya existían y no se tocaron"
              + (" (usa --sobrescribir para reemplazarlos)" if saltados else ""))
        print("Ahora: python src/utils/revisar_datos.py")
        return 0
    lista = empacar(args.destino)
    peso = args.destino.stat().st_size / 1e6
    print(f"{len(lista)} archivos en {args.destino} ({peso:.1f} MB).")
    print("Cópialo al otro computador junto con data/raw/ y la carpeta del CNC; ver docs/TRASLADO.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
