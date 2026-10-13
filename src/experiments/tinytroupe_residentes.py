"""
TinyTroupe con los doce residentes de Bogotá (`docs/TINYTROUPE_RESIDENTES_SPECIFICATION.md`). La misma prueba que
`MIROFISH_RESIDENTES`, con otra herramienta: cada residente es una `TinyPerson` de Microsoft TinyTroupe, que primero
escucha el mismo resumen de la gestión de Galán y luego responde las cinco preguntas de sí o no.

**Se corre con el Python de la instalación de TinyTroupe** (`Desktop\\TinyTroupe\\venv`), desde la carpeta de trabajo con su
`config.ini` (`CONFIG_INI`, que este script escribe). Nada del CNC ni de la EPC sale hacia el modelo.

Uso:
    <venv de TinyTroupe>\\Scripts\\python.exe src/experiments/tinytroupe_residentes.py

DECISIONES DE IMPLEMENTACIÓN
============================

DI-TT1. **Lo mismo que MiroFish, para comparar** (§2). Residentes, semilla, preguntas, prefijo, lectura del «sí» o el
    «no» y ponderación por estrato salen de `mirofish_segunda_vuelta`. La tabla de residentes se lee de la semilla.
DI-TT2. **La configuración de TinyTroupe** va en `config.ini` de la carpeta de trabajo: Luna por OpenRouter
    (`OPENAI_BASE_URL`), razonamiento `low`, caché de llamadas en disco, y sin memoria semántica ni consolidación, que
    usan embeddings y no hacen falta para cinco preguntas.
DI-TT3. **La respuesta** es el texto de las acciones TALK que siguen a cada pregunta, juntas. Si no hay TALK, cuenta como
    sin respuesta.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import mirofish_segunda_vuelta as mf   # noqa: E402  (solo biblioteca estándar)

TRABAJO = Path(os.environ.get("BSS_TINYTROUPE_DIR", Path.home() / "Desktop" / "TinyTroupe")) / "trabajo"
SALIDA = RAIZ / "data" / "processed" / "tinytroupe" / "residentes"
TOPE_USD = 1.00
CONFIG_INI = """[OpenAI]
API_TYPE=openai
MODEL=openai/gpt-6-luna
REASONING_MODEL=openai/gpt-6-luna
REASONING_EFFORT=low
MAX_COMPLETION_TOKENS=4000
TIMEOUT=600
MAX_ATTEMPTS=3
CACHE_API_CALLS=True
CACHE_FILE_NAME=cache_tinytroupe.json

[Simulation]
PARALLEL_AGENT_GENERATION=False
PARALLEL_AGENT_ACTIONS=False

[Cognition]
ENABLE_MEMORY_CONSOLIDATION=False
ENABLE_CONTINUOUS_CONTEXTUAL_SEMANTIC_MEMORY_RETRIEVAL=False

[ActionGenerator]
ENABLE_QUALITY_CHECKS=False
ENABLE_REGENERATION=False
"""


def perfiles() -> list[dict]:
    """DI-TT1: los residentes de la tabla de la semilla."""
    s = mf.SEMILLA_RESIDENTES.read_text(encoding="utf-8")
    tabla = s[s.index("## Doce residentes"):s.index("## El alcalde")]
    out = []
    for fila in tabla.splitlines():
        c = [x.strip() for x in fila.strip().strip("|").split("|")]
        if len(c) == 5 and c[0] in mf.RESIDENTES:
            out.append({"nombre": c[0], "edad": int(c[1]), "localidad": c[2], "estrato": c[3], "oficio": c[4]})
    return out


def contexto() -> str:
    """El mismo resumen de la gestión que vio MiroFish, sin la tabla de residentes ni las fuentes."""
    s = mf.SEMILLA_RESIDENTES.read_text(encoding="utf-8")
    return s[s.index("## El alcalde"):s.index("## Fuentes")].strip()


def correr() -> dict:
    TRABAJO.mkdir(parents=True, exist_ok=True)
    (TRABAJO / "config.ini").write_text(CONFIG_INI, encoding="utf-8")
    os.chdir(TRABAJO)
    os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"
    os.environ["OPENAI_API_KEY"] = os.environ["OPENROUTER_API_KEY"]
    from tinytroupe.agent import TinyPerson                      # después del config.ini
    inicio = mf.usado_usd()
    print(f"uso de la clave al empezar: USD {inicio:.4f}", flush=True)
    crudo = {clave: {} for clave, _, _ in mf.PREGUNTAS_RESIDENTES}
    for p in perfiles():
        if mf.excede(inicio, mf.usado_usd(), TOPE_USD):
            raise mf.MiroFishError(f"se pasó del tope de USD {TOPE_USD} antes de {p['nombre']}")
        a = TinyPerson(p["nombre"])
        a.define("age", p["edad"])
        a.define("nationality", "colombiana")
        a.define("residence", f"Bogotá, localidad de {p['localidad']}, estrato {p['estrato']}")
        a.define("occupation", p["oficio"])
        a.listen("Esto es lo que se sabe de la ciudad y de la Alcaldía en 2025:\n\n" + contexto())
        for clave, pregunta, _ in mf.PREGUNTAS_RESIDENTES:
            a.listen_and_act(mf.PREFIJO_ENTREVISTA + pregunta)
            habla = a.pop_actions_and_get_contents_for("TALK", only_last_action=False) or []
            crudo[clave][p["nombre"]] = " ".join(str(x) for x in habla)
        print(f"   {p['nombre']}: listo (gastado USD {mf.usado_usd() - inicio:.4f})", flush=True)
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "respuestas.json").write_text(json.dumps(crudo, ensure_ascii=False, indent=1), encoding="utf-8")
    porc = {c: mf.porcentaje_residentes({n: mf.leer_si_no(t) for n, t in r.items()}) for c, r in crudo.items()}
    reg = {"inicio_usd": inicio, "porcentajes": porc, "gasto_usd": round(mf.usado_usd() - inicio, 4)}
    (SALIDA / "registro.json").write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"porcentajes: {porc}\ngasto: USD {reg['gasto_usd']}", flush=True)
    return reg


# ---------------------------------------------------------------- variante B (enmienda 1)
N_B = 24
MIN_B = 18                                                       # como 9 de 12: tres cuartos
#: Enmienda 1: los adultos de Bogotá en la población sintética (Multipropósito 2021), por sexo, edad y estrato.
DEMOGRAFIA_BOGOTA = {
    "title": "Adultos de Bogotá, Colombia",
    "description": "Distribución de la población adulta (18 años o más) de Bogotá, según la Encuesta Multipropósito 2021 "
                   "del DANE.",
    "source": "Población sintética del proyecto, construida con la Encuesta Multipropósito 2021 (DANE).",
    "content": {"Demografía": {
        "Ciudad": "Bogotá, Colombia",
        "Sexo": {"Mujeres": "53.6%", "Hombres": "46.4%"},
        "Edad": {"18-29": "21.1%", "30-44": "32.1%", "45-59": "26.0%", "60 o más": "20.9%"},
        "Estrato socioeconómico de la vivienda": {"1": "8.7%", "2": "40.3%", "3": "34.7%", "4": "10.6%", "5": "3.5%",
                                                  "6": "2.3%"},
    }},
}


def porcentaje_simple(respuestas: dict[str, str | None], minimo: int = MIN_B) -> float | None:
    """Enmienda 1: % de «sí» entre quienes respondieron, sin ponderar (la fábrica ya muestrea según la demografía)."""
    ok = [r for r in respuestas.values() if r in ("si", "no")]
    return None if len(ok) < minimo else round(100 * sum(r == "si" for r in ok) / len(ok), 1)


def correr_b() -> dict:
    """Enmienda 1: la población la genera la fábrica de TinyTroupe con la demografía de Bogotá."""
    TRABAJO.mkdir(parents=True, exist_ok=True)
    (TRABAJO / "config.ini").write_text(CONFIG_INI, encoding="utf-8")
    os.chdir(TRABAJO)
    os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"
    os.environ["OPENAI_API_KEY"] = os.environ["OPENROUTER_API_KEY"]
    from tinytroupe.factory import TinyPersonFactory
    inicio = mf.usado_usd()
    print(f"uso de la clave al empezar (B): USD {inicio:.4f}", flush=True)
    fabrica = TinyPersonFactory.create_factory_from_demography(
        DEMOGRAFIA_BOGOTA, population_size=N_B, context="Adultos que viven en Bogotá, Colombia, en 2025.")
    gente = fabrica.generate_people(number_of_people=N_B, parallelize=False)
    print(f"   generadas {len(gente)} personas (gastado USD {mf.usado_usd() - inicio:.4f})", flush=True)
    salida = SALIDA.parent / "fabrica"
    salida.mkdir(parents=True, exist_ok=True)
    (salida / "personas.json").write_text(json.dumps([g._persona for g in gente], ensure_ascii=False, indent=1,
                                                     default=str), encoding="utf-8")
    crudo = {clave: {} for clave, _, _ in mf.PREGUNTAS_RESIDENTES}
    for a in gente:
        if mf.excede(inicio, mf.usado_usd(), TOPE_USD):
            raise mf.MiroFishError(f"se pasó del tope de USD {TOPE_USD} antes de {a.name}")
        a.listen("Esto es lo que se sabe de la ciudad y de la Alcaldía en 2025:\n\n" + contexto())
        for clave, pregunta, _ in mf.PREGUNTAS_RESIDENTES:
            a.listen_and_act(mf.PREFIJO_ENTREVISTA + pregunta)
            habla = a.pop_actions_and_get_contents_for("TALK", only_last_action=False) or []
            crudo[clave][a.name] = " ".join(str(x) for x in habla)
        print(f"   {a.name}: listo (gastado USD {mf.usado_usd() - inicio:.4f})", flush=True)
    (salida / "respuestas.json").write_text(json.dumps(crudo, ensure_ascii=False, indent=1), encoding="utf-8")
    porc = {c: porcentaje_simple({n: mf.leer_si_no(t) for n, t in r.items()}) for c, r in crudo.items()}
    reg = {"variante": "B", "inicio_usd": inicio, "porcentajes": porc, "gasto_usd": round(mf.usado_usd() - inicio, 4)}
    (salida / "registro.json").write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"porcentajes (B): {porc}\ngasto (B): USD {reg['gasto_usd']}", flush=True)
    return reg


if __name__ == "__main__":
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("falta la variable de entorno OPENROUTER_API_KEY")
        sys.exit(1)
    if "--b" in sys.argv:
        correr_b()
    else:
        correr()
