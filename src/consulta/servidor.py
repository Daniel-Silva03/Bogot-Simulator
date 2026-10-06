"""
src/consulta/servidor.py

Servidor local de la página de consulta (D17). Sirve la página y responde las
consultas; la clave de OpenRouter vive aquí, en la variable de entorno, y nunca
llega al navegador.

Uso (en la terminal de VS Code, con el entorno activado):
    $env:OPENROUTER_API_KEY = Read-Host "Clave de OpenRouter"
    python src/consulta/servidor.py              # http://127.0.0.1:8765
    python src/consulta/servidor.py --simulado   # sin clave ni gasto, para probar la página

Rutas:
    GET  /                 la página
    POST /api/reformular   {"pregunta": "..."}                    → sugerencia (paso 1)
    POST /api/responder    {"codigo": "VS8"}                      → dato del catálogo
                           {"pregunta": "...", "escala": [5 etiquetas]} → puente

DECISIONES DE IMPLEMENTACIÓN
============================

DI-SE1. **Solo escucha en 127.0.0.1.** Es una herramienta local: nadie fuera del
    computador puede usarla ni gastar la clave.

DI-SE2. **Sin librerías nuevas:** `http.server` de la biblioteca estándar. La página
    se arma una vez al arrancar, con la geometría, las capas base y la información
    general incrustadas, como el tablero (DI-V6): solo las tipografías vienen de
    fuera.

DI-SE3. **Cada consulta es independiente** (D17, pieza 4): el servidor no guarda
    nada entre consultas salvo la caché de respuestas del modelo, que evita pagar
    dos veces la misma pregunta.
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.consulta import motor as mo                       # noqa: E402

PLANTILLA = Path(__file__).with_name("pagina.html")
GEOJSON = RAIZ / "data" / "external" / "geo" / "localidades_bogota.geojson"
BASE = RAIZ / "data" / "processed" / "viz" / "base_bogota.json"
PUERTO = 8765
#: Los mismos textos de la validación (`reformular.PRUEBA`): así el modo simulado los
#: reconoce igual que el modelo real. Los tres del catálogo tienen mapa; los dos de
#: cambios en la ciudad son preguntas nuevas y no lo tienen (lectura B del puente).
EJEMPLOS = [
    "¿La gente se siente segura caminando por su barrio?",
    "¿Estarían de acuerdo con cobrar por entrar en carro al centro?",
    "¿Qué tan orgullosos se sienten de Bogotá?",
    "¿Les gustaría que el metro funcionara las 24 horas?",
    "¿Qué piensan de la calidad del aire en Bogotá?",
]


def _centroide(geom) -> list[float]:
    anillos = [geom["coordinates"][0]] if geom["type"] == "Polygon" else [p[0] for p in geom["coordinates"]]
    pts = [pt for a in anillos for pt in a]
    return [sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)]


def construir_pagina(general: dict, simulado: bool) -> str:
    geo = json.loads(GEOJSON.read_text(encoding="utf-8"))
    locs = [{"codigo": int(f["properties"]["codigo"]), "nombre": general[str(int(f["properties"]["codigo"]))]["nombre"],
             "geometry": f["geometry"], "centroide": _centroide(f["geometry"])} for f in geo["features"]]
    base = json.loads(BASE.read_text(encoding="utf-8"))
    base = {"meta": {"escala": base["meta"]["escala"], "licencia": base["meta"]["licencia"]},
            "verde": base["verde"], "vias": base["vias"]}
    datos = {"localidades": locs, "general": general, "ejemplos": EJEMPLOS, "simulado": simulado,
             "grupos": {k: v["titulo"] for k, v in mo.GRUPOS.items()}}
    html = PLANTILLA.read_text(encoding="utf-8")
    for marca, valor in (("/*__DATOS__*/", datos), ("/*__BASE__*/", base)):
        if marca not in html:
            raise RuntimeError(f"La plantilla no tiene {marca}")
        html = html.replace(marca, json.dumps(valor, ensure_ascii=False, separators=(",", ":")))
    return html


def crear_servidor(motor: mo.Motor, pagina, puerto: int = PUERTO) -> ThreadingHTTPServer:
    """`pagina` es el HTML o una función que lo arma (se llama en cada visita)."""
    candado = threading.Lock()                # el motor y la caché no son de varios hilos a la vez

    class Manejador(BaseHTTPRequestHandler):
        def _enviar(self, codigo: int, cuerpo: bytes, tipo: str):
            self.send_response(codigo)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(cuerpo)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(cuerpo)

        def _json(self, codigo: int, datos: dict):
            self._enviar(codigo, json.dumps(datos, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                html = pagina() if callable(pagina) else pagina
                self._enviar(200, html.encode("utf-8"), "text/html; charset=utf-8")
            else:
                self._json(404, {"error": "no existe"})

        def do_POST(self):
            try:
                n = int(self.headers.get("Content-Length") or 0)
                d = json.loads(self.rfile.read(min(n, 20_000)).decode("utf-8") or "{}")
                with candado:
                    if self.path == "/api/reformular":
                        r = motor.reformular(str(d.get("pregunta", "")))
                    elif self.path == "/api/responder":
                        if d.get("codigo"):
                            r = motor.responder_catalogo(str(d["codigo"]))
                        else:
                            r = motor.responder_nueva(str(d.get("pregunta", "")), [str(x) for x in d.get("escala") or []],
                                                      original=str(d.get("original") or "")[:500] or None)   # DI-CO28
                    else:
                        return self._json(404, {"error": "no existe"})
                self._json(200, r)
            except mo.ConsultaError as e:
                self._json(400, {"error": str(e)})
            except Exception as e:                                   # noqa: BLE001
                self._json(502, {"error": f"No se pudo completar la consulta: {e}"})

        def log_message(self, formato, *args):                       # sin ruido en la terminal
            pass

    return ThreadingHTTPServer(("127.0.0.1", puerto), Manejador)      # DI-SE1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Página de consulta de Bogotá Sintética (D17).")
    ap.add_argument("--simulado", action="store_true", help="sin clave ni gasto: respuestas del modelo simuladas")
    ap.add_argument("--puerto", type=int, default=PUERTO)
    args = ap.parse_args(argv)
    llamar, modelo = mo.cliente(args.simulado)
    print("Cargando la población…", flush=True)
    motor = mo.Motor(llamar, modelo)
    general = mo.informacion_general(motor.agentes, motor.donante)
    construir_pagina(general, args.simulado)                     # falla aquí si la plantilla está rota
    # La página se arma en cada visita (unos milisegundos): un cambio en la plantilla
    # se ve al recargar, sin reiniciar el servidor.
    srv = crear_servidor(motor, lambda: construir_pagina(general, args.simulado), args.puerto)
    print(f"Bogotá Sintética en http://127.0.0.1:{args.puerto}"
          f"{'  (modo simulado: sin gasto)' if args.simulado else ''}\nCtrl+C para cerrar.", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
