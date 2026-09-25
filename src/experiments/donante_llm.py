"""
Brazo LLM del Experimento 8 — pide los 13 ítems de confianza, persona por persona.

QUÉ HACE
--------
Para cada persona del conjunto retenido, le da al modelo **solo las cuatro
variables puente** (sexo, edad, estrato, educación) y le pide las 13 respuestas
de la batería de confianza institucional de la ECP, en la escala 1-5. Guarda
las respuestas crudas en JSON; quien las promedia y las evalúa es
`experimento8.py`.

TRES DECISIONES QUE IMPORTAN
----------------------------
**1. Se piden los 13 ítems, no el índice.** Pedir directamente «el índice de
confianza de esta persona» invita al modelo a poner un 3 —el centro de la
escala— y a que la varianza colapse por construcción. Pidiendo los ítems, el
promedio se arma igual que en el dato real y la dispersión sale de las
respuestas. Es, además, lo único que hace comparable el resultado con la forma
en que se construye `confianza_institucional`.

**2. El modelo recibe exactamente lo que recibe el hot-deck, ni un dato más.**
Si se le diera localidad, ocupación o cualquier otra cosa, ya no estaríamos
comparando dos métodos sobre el mismo problema, sino dos problemas distintos.

**3. Temperatura alta, no baja.** Es contraintuitivo y es deliberado: a
temperatura 0 el modelo da la misma respuesta modal a todas las personas
parecidas y la distribución se aplana —el defecto de DI-M1 y la falla número
uno documentada de los LLM en simulación de encuestas—. Como el donante tiene
que producir una *población*, no una predicción puntual, se muestrea. La
temperatura queda registrada en el JSON de salida.

LO QUE ESTE SCRIPT NO HACE
--------------------------
No manda nada del CNC a ninguna parte. La ECP es pública (microdatos DANE), y
lo único que sale de esta máquina son cuatro variables demográficas por
persona, sin identificador. **No usar este script con los estudios del CNC**:
eso violaría R10 / DATA_INVENTORY §12.4.

Uso:
    set ANTHROPIC_API_KEY=...        (o OPENAI_API_KEY)
    python src/experiments/donante_llm.py --anio 2023 --n 400
    python src/experiments/donante_llm.py --anio 2023 --n 400 --reanudar

La caché hace que reanudar sea gratis: una persona ya respondida no se vuelve
a pedir.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments.experimento8 import cargar  # noqa: E402
from src.population.ecp import (  # noqa: E402
    COLUMNA_EDUCACION_MATCH,
    ETIQUETAS_ITEMS,
    ITEMS_UTILES,
    donante_ecp,
)

SALIDA = RAIZ / "data" / "processed" / "exp8"

EDUCACION = {0: "ninguna o primaria", 1: "secundaria incompleta",
             2: "secundaria completa", 3: "técnica o tecnológica",
             4: "universitaria o posgrado"}

PROMPT_SISTEMA = (
    "Responde como una persona adulta residente en Bogotá, Colombia, con las "
    "características que se te den. No expliques, no razones en voz alta, no "
    "añadas texto: devuelve únicamente un objeto JSON.\n\n"
    "La pregunta es la de la Encuesta de Cultura Política del DANE: «¿Cuánta "
    "confianza tiene usted en cada una de las siguientes instituciones?», en "
    "escala de 1 a 5, donde 1 significa que no confía y 5 que confía mucho.\n\n"
    "Responde con tu opinión como esa persona concreta, no con un promedio "
    "nacional ni con lo que sería socialmente correcto. Personas distintas "
    "responden muy distinto: si esta persona desconfía de todo, dilo."
)


def perfil(fila) -> str:
    sexo = "Hombre" if fila.sexo == "M" else "Mujer"
    est = int(fila.estrato)
    edu = EDUCACION.get(int(getattr(fila, COLUMNA_EDUCACION_MATCH)), "sin dato")
    return (f"{sexo}, {int(fila.edad)} años, estrato {est}, "
            f"educación {edu}.")


def prompt_usuario(fila) -> str:
    items = "\n".join(f'  "{k}": <1-5>,   // {ETIQUETAS_ITEMS[k]}' for k in ITEMS_UTILES)
    return (f"{perfil(fila)}\n\n"
            f"Devuelve exactamente este JSON, con un entero de 1 a 5 en cada campo:\n"
            f"{{\n{items}\n}}")


# --------------------------------------------------------------------------
# Proveedores. Se usa urllib para no depender de ningún SDK: este script tiene
# que correr en una máquina donde quizá no se pueda instalar nada.

#: Una corrida de 1.269 llamadas cruza varios minutos de red. Un corte, un 429
#: o una respuesta truncada son normales y NO son datos: se reintentan. Sin esto
#: la corrida entera se cae por una llamada, que fue exactamente lo que pasó.
REINTENTOS = 4


def _post(url: str, cuerpo: dict, cabeceras: dict, timeout: int = 90) -> dict:
    ultimo = None
    for intento in range(REINTENTOS):
        try:
            req = urllib.request.Request(
                url, data=json.dumps(cuerpo).encode("utf-8"),
                headers={"content-type": "application/json", **cabeceras})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            # 4xx que no sea 408/429 es culpa de la petición: reintentar no
            # arregla una clave mala ni un modelo que no existe.
            if e.code not in (408, 429) and 400 <= e.code < 500:
                raise
            ultimo = e
        except Exception as e:                      # noqa: BLE001
            # IncompleteRead, ConnectionReset, timeouts, JSON truncado. Son de
            # red, no del experimento, y se reintentan sin contarlos como fallo.
            ultimo = e
        if intento < REINTENTOS - 1:
            time.sleep(2 ** intento)                # 1s, 2s, 4s
    raise ultimo


def llamar_anthropic(modelo: str, sistema: str, usuario: str, temp: float) -> str:
    clave = os.environ["ANTHROPIC_API_KEY"].strip()
    base = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com").strip().rstrip("/")
    r = _post(f"{base}/v1/messages",
              {"model": modelo, "max_tokens": 600, "temperature": temp,
               "system": sistema, "messages": [{"role": "user", "content": usuario}]},
              {"x-api-key": clave, "anthropic-version": "2023-06-01"})
    return "".join(b.get("text", "") for b in r.get("content", []))


def _chat_compatible(base_def: str, var_clave: str, var_base: str):
    """Cualquier API con el formato de OpenAI: OpenAI, OpenRouter, y varias más.

    Se comparte el cuerpo porque el formato es el mismo; lo único que cambia es
    de dónde salen la clave y la URL.
    """
    def llamar(modelo: str, sistema: str, usuario: str, temp: float) -> str:
        # .strip() no es cosmético: una clave pegada desde un correo o un PDF
        # llega con salto de línea o espacios, y el servidor devuelve 401 sin
        # decir por qué.
        clave = os.environ[var_clave].strip()
        base = os.environ.get(var_base, base_def).strip().rstrip("/")
        r = _post(f"{base}/chat/completions",
                  {"model": modelo, "temperature": temp,
                   "messages": [{"role": "system", "content": sistema},
                                {"role": "user", "content": usuario}]},
                  {"authorization": f"Bearer {clave}"})
        return r["choices"][0]["message"]["content"]
    return llamar


llamar_openai = _chat_compatible("https://api.openai.com/v1", "OPENAI_API_KEY", "OPENAI_BASE_URL")
llamar_openrouter = _chat_compatible("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY", "OPENROUTER_BASE_URL")

PROVEEDORES = {"anthropic": llamar_anthropic,
               "openai": llamar_openai,
               "openrouter": llamar_openrouter}

#: Qué variable de entorno necesita cada proveedor, para avisar antes de
#: empezar en vez de fallar en la llamada 1.
CLAVE_DE = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY",
            "openrouter": "OPENROUTER_API_KEY"}


def extraer(texto: str) -> dict | None:
    """Saca el JSON aunque venga con texto alrededor o en un bloque de código."""
    m = re.search(r"\{.*\}", texto, re.S)
    if not m:
        return None
    try:
        crudo = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    salida = {}
    for k in ITEMS_UTILES:
        v = crudo.get(k)
        if isinstance(v, (int, float)) and 1 <= v <= 5:
            salida[k] = int(round(v))
    return salida or None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--anio", type=int, default=2023)
    ap.add_argument("--n", type=int, default=400,
                    help="cuántas personas del retenido consultar (default 400)")
    ap.add_argument("--proveedor", choices=sorted(PROVEEDORES), default="anthropic")
    ap.add_argument("--modelo", default=None,
                    help="id del modelo; en OpenRouter lleva prefijo, p.ej. anthropic/claude-opus-5.5")
    ap.add_argument("--temperatura", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--reanudar", action="store_true", help="no repetir lo ya guardado")
    ap.add_argument("--pausa", type=float, default=0.0, help="segundos entre llamadas")
    args = ap.parse_args(argv)
    if not args.modelo:
        args.modelo = {"anthropic": "claude-sonnet-4-5",
                       "openai": "gpt-4o-mini",
                       "openrouter": "anthropic/claude-opus-5.5"}[args.proveedor]

    var = CLAVE_DE[args.proveedor]
    clave = (os.environ.get(var) or "").strip()
    if not clave:
        print(f"Falta {var} en el entorno.\n"
              f"  PowerShell:  $env:{var} = \"...\"")
        return 1
    # Diagnóstico antes de gastar una llamada: el 90 % de los problemas son la
    # clave mal pegada, y el servidor solo responde 401 sin explicar.
    print(f"{var}: {len(clave)} caracteres, empieza por «{clave[:8]}»")
    if any(c.isspace() for c in os.environ[var].strip("\r\n \t")):
        print("  AVISO: la clave trae espacios o saltos de línea en medio. "
              "Vuelve a pegarla en una sola línea.")
        return 1

    _, te = cargar(args.anio, seed=args.seed)
    # Submuestra estable: los primeros n del retenido, que ya viene barajado
    # con la semilla. Así --n 100 es un prefijo de --n 400 y los resultados de
    # una corrida chica siguen valiendo cuando se amplía.
    objetivo = te.head(args.n)

    SALIDA.mkdir(parents=True, exist_ok=True)
    # El nombre lleva el modelo: correr un segundo modelo NO puede borrar el
    # primero, que fue lo que estuvo a punto de pasar.
    slug = re.sub(r"[^a-z0-9]+", "-", args.modelo.lower()).strip("-")
    destino = SALIDA / f"llm_{args.anio}_{slug}.json"
    viejo = SALIDA / f"llm_respuestas_{args.anio}.json"
    if viejo.exists() and not destino.exists():
        print(f"(hay un {viejo.name} de antes; este modelo escribe en "
              f"{destino.name} y no lo toca)")
    estado = {"anio": args.anio, "proveedor": args.proveedor, "modelo": args.modelo,
              "temperatura": args.temperatura, "seed": args.seed, "n_pedidas": args.n,
              "items": list(ITEMS_UTILES), "respuestas": {}, "fallos": []}
    if args.reanudar and destino.exists():
        estado = json.loads(destino.read_text(encoding="utf-8"))
        estado["respuestas"] = {str(k): v for k, v in estado["respuestas"].items()}
        # Los fallos anteriores se borran para que se reintenten: un corte de
        # red no puede dejar a esa persona fuera del experimento para siempre.
        estado["fallos"] = []

    llamar = PROVEEDORES[args.proveedor]
    hechos = len(estado["respuestas"])
    print(f"ECP {args.anio} · retenido {len(te)} · a consultar {len(objetivo)} "
          f"· ya hechos {hechos}\n{args.proveedor}/{args.modelo} temp={args.temperatura}\n")

    for i, fila in enumerate(objetivo.itertuples(), 1):
        cid = str(int(fila.caso_id))
        if cid in estado["respuestas"]:
            continue
        try:
            texto = llamar(args.modelo, PROMPT_SISTEMA, prompt_usuario(fila), args.temperatura)
            r = extraer(texto)
            if r and len(r) >= 7:
                estado["respuestas"][cid] = r
            else:
                estado["fallos"].append({"caso_id": cid, "motivo": "respuesta no parseable",
                                         "texto": (texto or "")[:200]})
        except KeyboardInterrupt:
            destino.write_text(json.dumps(estado, ensure_ascii=False), encoding="utf-8")
            print(f"\nInterrumpido. Guardado en {destino.name} "
                  f"({len(estado['respuestas'])} respuestas). Reanuda con --reanudar.")
            return 1
        except Exception as e:                      # noqa: BLE001
            # NINGUNA excepción puede tumbar la corrida: se anota y se sigue.
            # La versión anterior solo atrapaba las de urllib, y un
            # http.client.IncompleteRead —que no hereda de URLError— se llevó
            # una corrida de 1.075 llamadas.
            estado["fallos"].append({"caso_id": cid, "motivo": f"{type(e).__name__}: {e}"})
            # Guardar de inmediato tras un fallo: si el siguiente es fatal, no
            # se pierden las respuestas buenas de este bloque de 25.
            destino.write_text(json.dumps(estado, ensure_ascii=False), encoding="utf-8")
        if i % 25 == 0 or i == len(objetivo):
            destino.write_text(json.dumps(estado, ensure_ascii=False), encoding="utf-8")
            print(f"  {i}/{len(objetivo)}  ok={len(estado['respuestas'])} "
                  f"fallos={len(estado['fallos'])}")
        if args.pausa:
            time.sleep(args.pausa)

    destino.write_text(json.dumps(estado, ensure_ascii=False), encoding="utf-8")
    print(f"\n{destino.relative_to(RAIZ).as_posix()}  "
          f"{len(estado['respuestas'])} respuestas, {len(estado['fallos'])} fallos")
    if estado["fallos"]:
        from collections import Counter
        tipos = Counter(f["motivo"].split(":")[0] for f in estado["fallos"])
        print("  fallos por tipo: " + ", ".join(f"{k} ×{v}" for k, v in tipos.most_common()))
        pend = [f["caso_id"] for f in estado["fallos"]
                if f["caso_id"] not in estado["respuestas"]]
        if pend:
            print(f"  {len(pend)} casos siguen sin respuesta; --reanudar los reintenta.")
    print(f"\nAhora:\n  python src/experiments/experimento8.py --anio {args.anio} "
          f"--llm {destino.relative_to(RAIZ).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
