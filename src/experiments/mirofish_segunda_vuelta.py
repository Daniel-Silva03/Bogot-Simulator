"""
MiroFish ante la segunda vuelta de 2026 en Bogotá (`docs/MIROFISH_SEGUNDA_VUELTA_SPECIFICATION.md`). Maneja una
instalación local de MiroFish por su API: documento semilla → grafo → agentes → simulación (tope de rondas) → informe.
El informe queda en `data/processed/mirofish/`, ignorado por git.

**Lo que sale de aquí:** solo el documento semilla público (a Zep y al modelo) y lo que MiroFish genera. Nada del CNC ni
de la EPC.

Uso:
    python src/experiments/mirofish_segunda_vuelta.py --saldo      # cuánto lleva gastado la clave (no gasta)
    python src/experiments/mirofish_segunda_vuelta.py              # la corrida (tope USD 1)
    python src/experiments/mirofish_segunda_vuelta.py --caso galan # la segunda prueba (MIROFISH_GALAN)

Variables de entorno: `OPENROUTER_API_KEY` (la del simulador, decisión de Daniel), `ZEP_API_KEY` y, opcional,
`BSS_MIROFISH_DIR` (por omisión, `Desktop\\MiroFish`).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-MF1. **El tope de gasto** se controla con el uso de la clave en OpenRouter (`/api/v1/key`, no cuesta): se lee antes de
    empezar y cada vez que se consulta el estado. Si lo gastado desde el comienzo pasa de `TOPE_USD`, se detiene la
    simulación y el script termina. Hecho: la clave es la misma de la página, así que otro uso simultáneo también
    contaría; durante la corrida la página queda cerrada.
DI-MF2. **El backend de MiroFish se arranca desde aquí,** solo en 127.0.0.1 (por omisión escucha en 0.0.0.0), con la
    configuración por variables de entorno: sin archivo `.env` y sin escribir claves en disco.
DI-MF3. **Las rondas se cortan en `MAX_RONDAS`** al iniciar la simulación (`max_rounds`).
DI-MF4. **Dos arreglos tras la primera corrida (9/10).** Hecho: al terminar las rondas, MiroFish deja la simulación abierta
    esperando entrevistas, y su estado sigue en «running»; el script esperaba «completed» y se quedó trabado. Luego, al
    pedir el informe por simulación, guardó una versión vieja. Decisión: (1) la simulación termina cuando las dos redes
    pararon (`simulacion_terminada`) y se cierra con `/stop`, que el informe exige; (2) el informe se sigue y se guarda por
    el `report_id` que devuelve su propia petición. En esa corrida, el informe válido es `report_d8133f7341eb`, copiado a
    mano a `informe.md`.
DI-MF5. **Un mismo script para las dos pruebas** (`--caso`): cada una con su semilla, su petición y su carpeta. La
    segunda vuelta sigue igual, por omisión.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SEMILLA = RAIZ / "docs" / "anexos" / "mirofish_semilla_segunda_vuelta.md"
SALIDA = RAIZ / "data" / "processed" / "mirofish" / "segunda_vuelta"
MIROFISH = Path(os.environ.get("BSS_MIROFISH_DIR", Path.home() / "Desktop" / "MiroFish"))
BASE = "http://127.0.0.1:5001"
MODELO = "openai/gpt-6-luna"
TOPE_USD = 1.00                                                 # §6
MAX_RONDAS = 10                                                 # §2
ESPERA = 15                                                     # segundos entre consultas de estado
#: §2: la petición a MiroFish, fija antes de correr.
REQUERIMIENTO = (
    "Simula la conversación pública de los votantes de Bogotá en las dos semanas antes de la segunda vuelta "
    "presidencial de Colombia del 21 de junio de 2026, entre Iván Cepeda y Abelardo de la Espriella. Al final, estima "
    "qué porcentaje de los votos por los dos candidatos obtendrá cada uno en Bogotá: da una sola cifra para cada uno, "
    "que sumen 100, y explica en qué te basas.")
#: MIROFISH_GALAN §2: la segunda prueba.
SEMILLA_GALAN = RAIZ / "docs" / "anexos" / "mirofish_semilla_galan.md"
REQUERIMIENTO_GALAN = (
    "Simula la conversación pública de los bogotanos adultos sobre la gestión del alcalde Carlos Fernando Galán en el "
    "segundo semestre de 2025. Al final, estima qué porcentaje de los bogotanos adultos aprueba la gestión del alcalde: "
    "da una sola cifra, y explica en qué te basas.")
#: DI-MF5: cada prueba con su semilla, su petición y su carpeta.
CASOS = {"segunda_vuelta": (SEMILLA, REQUERIMIENTO, SALIDA, "BSS segunda vuelta 2026"),
         "galan": (SEMILLA_GALAN, REQUERIMIENTO_GALAN, RAIZ / "data" / "processed" / "mirofish" / "galan", "BSS Galán 2025")}


class MiroFishError(RuntimeError):
    pass


# ---------------------------------------------------------------- gasto (DI-MF1)
def usado_usd() -> float:
    """Lo gastado por la clave según OpenRouter. No hace ninguna llamada al modelo."""
    req = urllib.request.Request("https://openrouter.ai/api/v1/key",
                                 headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return float(json.loads(r.read())["data"]["usage"])


def excede(inicio: float, ahora: float, tope: float = TOPE_USD) -> bool:
    return ahora - inicio > tope


# ---------------------------------------------------------------- API de MiroFish
def _api(metodo: str, ruta: str, cuerpo: dict | None = None) -> dict:
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(BASE + ruta, data=datos, method=metodo, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        d = json.loads(r.read())
    if not d.get("success", True):
        raise MiroFishError(f"{ruta}: {d.get('error')}")
    return d.get("data", d)


def _subir_semilla(texto: str, nombre: str, requerimiento: str = REQUERIMIENTO) -> dict:
    """POST multipart a /api/graph/ontology/generate, con el documento y el requerimiento."""
    limite = "----bss" + str(int(time.time()))
    partes = []
    for k, v in (("simulation_requirement", requerimiento), ("project_name", nombre)):
        partes.append(f'--{limite}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    partes.append(f'--{limite}\r\nContent-Disposition: form-data; name="files"; filename="semilla.md"\r\n'
                  f'Content-Type: text/markdown\r\n\r\n'.encode() + texto.encode() + b"\r\n")
    partes.append(f"--{limite}--\r\n".encode())
    req = urllib.request.Request(BASE + "/api/graph/ontology/generate", data=b"".join(partes), method="POST",
                                 headers={"Content-Type": f"multipart/form-data; boundary={limite}"})
    with urllib.request.urlopen(req, timeout=600) as r:
        d = json.loads(r.read())
    if not d.get("success", True):
        raise MiroFishError(f"ontología: {d.get('error')}")
    return d.get("data", d)


def _esperar(consulta, terminado, inicio: float, al_exceder=None) -> dict:
    while True:
        d = consulta()
        if terminado(d):
            return d
        if excede(inicio, usado_usd()):
            if al_exceder:
                al_exceder()
            raise MiroFishError(f"se pasó del tope de USD {TOPE_USD}: se detuvo")
        time.sleep(ESPERA)


def _estado_tarea(d: dict) -> bool:
    s = str(d.get("status", "")).lower()
    if s == "failed":
        raise MiroFishError(f"tarea fallida: {d.get('error') or d.get('message')}")
    return s == "completed"


def simulacion_terminada(d: dict) -> bool:
    """DI-MF4: terminada si el estado es final o si las dos redes ya pararon con alguna ronda hecha."""
    if d.get("runner_status") in ("completed", "stopped", "failed"):
        return True
    return (d.get("current_round") or 0) > 0 and not d.get("twitter_running") and not d.get("reddit_running")


def arrancar_backend(salida: Path = SALIDA) -> subprocess.Popen:
    """DI-MF2."""
    env = {**os.environ, "LLM_API_KEY": os.environ["OPENROUTER_API_KEY"], "LLM_BASE_URL": "https://openrouter.ai/api/v1",
           "LLM_MODEL_NAME": MODELO, "FLASK_HOST": "127.0.0.1", "FLASK_PORT": "5001",
           "OASIS_DEFAULT_MAX_ROUNDS": str(MAX_RONDAS), "PYTHONIOENCODING": "utf-8", "UV_PYTHON_DOWNLOADS": "never",
           "PATH": str(MIROFISH / "herramientas" / "venv_uv" / "Scripts") + os.pathsep + os.environ["PATH"]}
    salida.mkdir(parents=True, exist_ok=True)
    log = open(salida / "backend.log", "w", encoding="utf-8")
    uv = str(MIROFISH / "herramientas" / "venv_uv" / "Scripts" / "uv.exe")       # Popen no usa el PATH de env
    p = subprocess.Popen([uv, "run", "--python", "3.12", "python", "run.py"], cwd=MIROFISH / "codigo" / "backend",
                         env=env, stdout=log, stderr=subprocess.STDOUT)
    for _ in range(60):
        try:
            urllib.request.urlopen(BASE + "/api/graph/project/list", timeout=5)
            return p
        except OSError:
            time.sleep(2)
    p.terminate()
    raise MiroFishError("el backend de MiroFish no arrancó: ver backend.log")


def correr(caso: str = "segunda_vuelta") -> dict:
    semilla, requerimiento, salida, nombre = CASOS[caso]
    inicio = usado_usd()
    print(f"uso de la clave al empezar: USD {inicio:.4f}", flush=True)
    back = arrancar_backend(salida)
    reg = {"caso": caso, "inicio_usd": inicio}
    try:
        p = _subir_semilla(semilla.read_text(encoding="utf-8"), nombre, requerimiento)
        reg["project_id"] = p["project_id"]
        print("1/5 ontología lista", flush=True)
        t = _api("POST", "/api/graph/build", {"project_id": reg["project_id"]})
        _esperar(lambda: _api("GET", f"/api/graph/task/{t['task_id']}"), _estado_tarea, inicio)
        print("2/5 grafo listo", flush=True)
        s = _api("POST", "/api/simulation/create", {"project_id": reg["project_id"]})
        sim = reg["simulation_id"] = s["simulation_id"]
        t = _api("POST", "/api/simulation/prepare", {"simulation_id": sim})
        _esperar(lambda: _api("POST", "/api/simulation/prepare/status", {"task_id": t.get("task_id"), "simulation_id": sim}),
                 lambda d: _estado_tarea(d) or bool(d.get("already_prepared")), inicio)
        print("3/5 agentes y configuración listos", flush=True)
        _api("POST", "/api/simulation/start", {"simulation_id": sim, "platform": "parallel", "max_rounds": MAX_RONDAS})
        fin = _esperar(lambda: _api("GET", f"/api/simulation/{sim}/run-status"), simulacion_terminada, inicio,
                       al_exceder=lambda: _api("POST", "/api/simulation/stop", {"simulation_id": sim}))
        if fin.get("runner_status") == "running":                               # DI-MF4: queda esperando entrevistas
            _api("POST", "/api/simulation/stop", {"simulation_id": sim})
        reg["simulacion"] = {k: fin.get(k) for k in ("runner_status", "current_round", "total_rounds", "total_actions_count")}
        print(f"4/5 simulación: {reg['simulacion']}", flush=True)
        t = _api("POST", "/api/report/generate", {"simulation_id": sim})
        reg["report_id"] = t["report_id"]                                       # DI-MF4: este informe, no otro
        _esperar(lambda: _api("GET", f"/api/report/{reg['report_id']}/progress"),
                 lambda d: _estado_tarea(d), inicio)
        rep = _api("GET", f"/api/report/{reg['report_id']}")
        (salida / "informe.md").write_text(rep.get("markdown_content") or json.dumps(rep, ensure_ascii=False, indent=1),
                                           encoding="utf-8")
        print(f"5/5 informe guardado en {salida.relative_to(RAIZ)}/informe.md", flush=True)
    finally:
        reg["gasto_usd"] = round(usado_usd() - inicio, 4)
        (salida / "registro.json").write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
        # DI-MF4: `uv` lanza el backend como hijo; terminate() cierra solo a `uv`
        subprocess.run(["taskkill", "/PID", str(back.pid), "/T", "/F"], capture_output=True)
        print(f"gasto de la corrida: USD {reg['gasto_usd']}", flush=True)
    return reg


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--saldo", action="store_true")
    ap.add_argument("--caso", choices=sorted(CASOS), default="segunda_vuelta")
    a = ap.parse_args()
    if a.saldo:
        print(f"uso acumulado de la clave: USD {usado_usd():.4f}")
        return 0
    for k in ("OPENROUTER_API_KEY", "ZEP_API_KEY"):
        if not os.environ.get(k):
            print(f"falta la variable de entorno {k}")
            return 1
    correr(a.caso)
    return 0


if __name__ == "__main__":
    sys.exit(main())
