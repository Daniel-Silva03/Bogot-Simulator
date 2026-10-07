"""
Nivel por preguntas parecidas, parte B (`docs/NIVEL_PARECIDAS_B_SPECIFICATION.md`): un modelo de
lenguaje más fuerte elige, entre preguntas de práctica de OTRAS familias, las que probablemente
tengan un porcentaje favorable parecido al de una pregunta nueva. La predicción es la media real
de las elegidas: el modelo nunca ve resultados ni pone cifras. Solo práctica.

Uso:
    python src/experiments/nivel_parecidas_b.py --simulado            # sin gasto
    python src/experiments/nivel_parecidas_b.py --prueba               # 1 llamada por modelo, mide el costo
    python src/experiments/nivel_parecidas_b.py                        # la corrida (tope USD 4)

Escribe `data/processed/banco/nivel_parecidas_b.json`; caché en `cache_nivel_b.json` (no se sube).

DECISIONES DE IMPLEMENTACIÓN
============================

DI-NB1. **La forma de cada pregunta se muestra con sus categorías válidas** (`banco_reales.validos`)
    y un asterisco en las favorables, por ejemplo «1=Favorable*; 2=Desfavorable; 3=No conoce».

DI-NB2. **El tope se revisa antes de cada llamada** con lo que la caché registra como costo de
    los dos modelos (`experimento9.gasto_registrado`). Una llamada en curso puede pasarlo por
    centavos; la siguiente ya no se hace.

DI-NB3. **Se aceptan ids repetidos o de más:** se quitan los repetidos, se descartan los que no
    son candidatas válidas y se toman los primeros 5. Si no queda ninguno, es respuesta inválida.

DI-NB4. **Tiempo de espera de 300 s por intento y un modelo a la vez** (2/10, tras la primera
    corrida). Hecho: DeepSeek razona unos 2.000 tokens antes de responder; con los 90 s del cliente
    tardaba ~8 minutos por respuesta guardada, probablemente por intentos cortados y repetidos, que
    OpenRouter podría cobrar sin que la respuesta llegue. Decisión: 300 s por intento; `--modelo`
    para correr uno por vez, y el uso de la clave (`/api/v1/key`) se mide antes y después de cada
    modelo para comparar con lo registrado. La clave es compartida, así que la diferencia también
    puede incluir uso ajeno. No cambia nada del diseño pre-registrado.

DI-NB5. **DeepSeek sin razonamiento** (5/10, enmienda 1 del pre-registro, pedida por Daniel). Aun con
    300 s, DeepSeek tardaba ~5 minutos por respuesta (≥ 6 horas para la corrida). Se pide con
    `"reasoning": {"enabled": false}` (el modelo lo permite: `mandatory: false` en `/api/v1/models`).
    En la caché va con la etiqueta `deepseek/deepseek-v4-pro#sin-razonar`, para no mezclarse con las
    respuestas que sí razonaron; el cliente quita la etiqueta antes de llamar. Esas respuestas previas
    quedan en la caché pero no entran en la evaluación.

DI-NB6. **Si la respuesta trae varios JSON, vale el último que tenga ids válidos** (5/10, pedido por
    Daniel). Hecho: en la parte A de `NIVEL_ACUERDO_REDACCION`, Sonnet a veces se corrige en la misma
    respuesta («Corrección: el último id no existe; la respuesta válida es: {…}»); la lectura anterior
    tomaba todo entre la primera `{` y la última `}`, no era JSON y la daba por inválida. Antes, la
    página caía al texto de DI-CO20 en esos casos. Efecto en lo ya guardado (medido el 5/10): rescata 1 de
    93 respuestas en `cache_nivel_acuerdo`, 2 de 75 en `cache_nivel_acuerdo_validacion`, 0 de 116 en
    `cache_nivel_acuerdo_lote5` y 2 de 48 en `cache_nivel_redaccion`. Los resultados ya escritos de
    esos experimentos no se recalculan: se evaluaron con la lectura de su pre-registro.

DI-NB7. **Variante del mensaje con las candidatas primero** (`orden="candidatas"`, 7/10, pedida por Daniel para bajar el
    costo). La información es la misma; cambia el orden. La lista de candidatas, completa y en el mismo orden, va
    al comienzo, y al final la pregunta nueva y las ids de su misma familia que no puede elegir. Como el comienzo
    es idéntico en todas las llamadas, el proveedor (OpenAI) lo cobra desde su caché. Por defecto sigue el orden
    de siempre: ningún experimento anterior cambia. La usa `VOTO_SIMULADO` desde su enmienda 1.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402

MODELOS = {"deepseek": "deepseek/deepseek-v4-pro#sin-razonar", "sonnet": "anthropic/claude-sonnet-5.5"}   # DI-NB5
SIN_RAZONAR = "#sin-razonar"
TEMPERATURA = 0.0
TOPE_USD = 4.0
VARA = 17.6
MAX_ELEGIDAS = 5
SALIDA_NOMBRE = "nivel_parecidas_b.json"
CACHE_NOMBRE = "cache_nivel_b.json"

SISTEMA = (
    "Eres un analista de encuestas de opinión. Te doy una pregunta de encuesta (la NUEVA) y una lista de "
    "preguntas CANDIDATAS que sí se midieron en encuestas a población adulta de Bogotá o de Colombia. No "
    "conoces sus resultados. Elige entre 1 y 5 candidatas cuyo PORCENTAJE DE RESPUESTAS FAVORABLES "
    "probablemente se parezca más al de la pregunta nueva. Ten en cuenta el tema, a qué o a quién se "
    "refiere, quién responde y, sobre todo, la forma de la escala: cuántas opciones hay y cuáles cuentan "
    "como favorables (marcadas con *). Responde SOLO con JSON: "
    '{"ids": ["id1", "id2"], "razon": "una frase"}'
)


class NivelBError(RuntimeError):
    """Algo impide correr la parte B como está pre-registrada."""


class TopeAlcanzado(NivelBError):
    """DI-NB2."""


def forma(categorias: str, favorables: str) -> str:
    """DI-NB1."""
    from src.experiments import banco_reales as br
    cats = br.categorias(categorias)
    fav = set(json.loads(favorables))
    return "; ".join(f"{c}={cats[c]}{'*' if c in fav else ''}" for c in br.validos(cats))


def prompt(t: pd.DataFrame, i: int) -> tuple[str, list[str]]:
    """(texto del usuario, ids válidos) para la pregunta i, con candidatas de otras familias."""
    q = t.iloc[i]
    cand = t[t.familia != q.familia].sort_values("id")
    lineas = [f"- {r.id} | {r.pregunta_pagina} | {forma(r.categorias, r.codigos_favorables)}" for r in cand.itertuples()]
    u = (f"PREGUNTA NUEVA:\n{q.pregunta_pagina}\nEscala: {forma(q.categorias, q.codigos_favorables)}\n\n"
         f"CANDIDATAS (id | pregunta | escala):\n" + "\n".join(lineas))
    return u, cand.id.tolist()


def _objetos(texto: str) -> list:
    """Los objetos JSON que aparecen en el texto, en orden."""
    dec, out, i = json.JSONDecoder(), [], 0
    while (j := texto.find("{", i)) >= 0:
        try:
            o, i = dec.raw_decode(texto, j)
            out.append(o)
        except json.JSONDecodeError:
            i = j + 1
    return out


def prompt_fijo(t: pd.DataFrame, i: int) -> tuple[str, list[str]]:
    """DI-NB7: la misma información que `prompt`, con las candidatas primero y completas, para que el comienzo del
    mensaje sea idéntico en todas las llamadas y el proveedor lo cobre desde su caché."""
    q = t.iloc[i]
    cand = t.drop(index=t.index[i]).sort_values("id")
    lineas = [f"- {r.id} | {r.pregunta_pagina} | {forma(r.categorias, r.codigos_favorables)}" for r in cand.itertuples()]
    misma = sorted(cand[cand.familia == q.familia].id)
    u = ("CANDIDATAS (id | pregunta | escala):\n" + "\n".join(lineas) +
         f"\n\nPREGUNTA NUEVA:\n{q.pregunta_pagina}\nEscala: {forma(q.categorias, q.codigos_favorables)}" +
         (f"\nNo elijas estas candidatas, que son de la misma pregunta: {', '.join(misma)}" if misma else ""))
    return u, cand[cand.familia != q.familia].id.tolist()


def parsear(texto: str, validos: list[str]) -> Optional[list[str]]:
    """DI-NB3 y DI-NB6: los ids válidos elegidos, o None."""
    for o in reversed(_objetos(texto or "")):                               # DI-NB6: el último que sirve
        ids = o.get("ids") if isinstance(o, dict) else None
        if not isinstance(ids, list):
            continue
        ok, vistos = [], set()
        for x in ids:
            x = str(x).strip()
            if x in validos and x not in vistos:
                ok.append(x)
                vistos.add(x)
        if ok:
            return ok[:MAX_ELEGIDAS]
    return None


def uso_clave() -> Optional[float]:
    """DI-NB4: el uso acumulado de la clave según OpenRouter (USD), o None si no se puede leer."""
    import os
    import urllib.request
    try:
        r = urllib.request.Request("https://openrouter.ai/api/v1/key",
                                   headers={"Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"].strip()})
        return float(json.loads(urllib.request.urlopen(r, timeout=30).read())["data"]["usage"])
    except Exception:                                                   # noqa: BLE001
        return None


def gastado(cache: e9.Cache) -> float:
    return e9.gasto_registrado(cache)["costo_usd"]


def elegir(t: pd.DataFrame, i: int, llamar, cache: e9.Cache, modelo: str, tope: float,
           orden: str = "pregunta") -> tuple[Optional[list[str]], int]:
    """(ids elegidos o None, llamadas nuevas). Un reintento si la respuesta no sirve (§3). `orden`: DI-NB7."""
    u, validos = prompt_fijo(t, i) if orden == "candidatas" else prompt(t, i)
    nuevas = 0
    for rep, extra in ((0, ""), (1, "\n\nNOTA: tu respuesta anterior no traía ids válidos de la lista. Responde solo con el JSON pedido.")):
        k = e9.Cache.clave(modelo, TEMPERATURA, SISTEMA, u + extra, rep)
        if k not in cache and gastado(cache) >= tope:                       # DI-NB2
            raise TopeAlcanzado(f"Gasto registrado USD {gastado(cache):.3f} ≥ tope USD {tope}.")
        texto, nueva = e9.pedir(llamar, cache, modelo, TEMPERATURA, SISTEMA, u + extra, rep)
        nuevas += int(nueva)
        ids = parsear(texto, validos)
        if ids:
            return ids, nuevas
    return None, nuevas


def correr(t: pd.DataFrame, llamar, cache: e9.Cache, modelo: str, tope: float = TOPE_USD,
           solo: Optional[int] = None) -> pd.DataFrame:
    tot = dict(zip(t.id, t.total))
    filas = []
    for i in range(len(t) if solo is None else solo):
        ids, nuevas = elegir(t, i, llamar, cache, modelo, tope)
        q = t.iloc[i]
        r0 = float(t[t.familia != q.familia].total.mean())
        pred = float(np.mean([tot[x] for x in ids])) if ids else r0
        filas.append({"id": q.id, "total": float(q.total), "pred": pred, "ids": ids or [], "fallo": ids is None,
                      "llamadas_nuevas": nuevas})
        if (i + 1) % 10 == 0:
            print(f"  {modelo}: {i + 1} preguntas, gasto registrado USD {gastado(cache):.3f}", flush=True)
    return pd.DataFrame(filas)


def resumen(p: pd.DataFrame, t: pd.DataFrame) -> dict:
    err = (p.pred - p.total).abs()
    bog = p.id.isin(t[t.ambito == "Bogotá"].id)
    return {"eam": float(err.mean()), "pasa": bool(err.mean() <= VARA), "fallos": int(p.fallo.sum()),
            "dentro_10": float((err <= 10).mean()), "eam_bogota": float(err[bog].mean()),
            "cnc": {r.id: {"real": r.total, "pred": round(r.pred, 1), "ids": r.ids}
                    for r in p[p.id.str.startswith("CNC")].itertuples()}}


def enrutar(base, sin_razonar):
    """DI-NB5: los modelos con la etiqueta `#sin-razonar` van al cliente sin razonamiento, sin la etiqueta."""
    def llamar(modelo, sistema, usuario, temp):
        if modelo.endswith(SIN_RAZONAR):
            return sin_razonar(modelo[: -len(SIN_RAZONAR)], sistema, usuario, temp)
        return base(modelo, sistema, usuario, temp)
    return llamar


def cliente_simulado(t: pd.DataFrame):
    """Elige las tres primeras candidatas de la lista; sin gasto."""
    def llamar(modelo, sistema, usuario, temp):
        ids = re.findall(r"^- (\S+) \|", usuario, re.M)[:3]
        return json.dumps({"ids": ids, "razon": "simulado"})
    return llamar


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    ap.add_argument("--prueba", action="store_true", help="una llamada por modelo, para medir el costo")
    ap.add_argument("--modelo", choices=list(MODELOS), help="correr solo este modelo (DI-NB4)")
    a = ap.parse_args()
    from src.experiments import banco as ba
    from src.experiments import nivel_parecidas as npar
    t = npar.tabla()
    if a.simulado:
        import tempfile
        cache = e9.Cache(Path(tempfile.gettempdir()) / "bss_nivel_b_simulado.json")
        llamar = cliente_simulado(t)
    else:
        cache = e9.Cache(ba.SALIDA / CACHE_NOMBRE)
        llamar = enrutar(e9.cliente_real(timeout=300),                       # DI-NB4
                         e9.cliente_real(timeout=300, extra={"reasoning": {"enabled": False}}))
    if a.prueba:
        for nombre, modelo in MODELOS.items():
            if a.modelo and nombre != a.modelo:
                continue
            antes = gastado(cache)
            correr(t, llamar, cache, modelo, solo=1)
            print(f"{nombre}: una llamada costó USD {gastado(cache) - antes:.4f} → la corrida (96) costaría "
                  f"~USD {96 * (gastado(cache) - antes):.2f}")
        print(f"gasto registrado total: USD {gastado(cache):.4f}")
        return 0
    if a.modelo:                                                            # DI-NB4
        modelo = MODELOS[a.modelo]
        u0, g0 = (None if a.simulado else uso_clave()), gastado(cache)
        p = correr(t, llamar, cache, modelo)
        u1, g1 = (None if a.simulado else uso_clave()), gastado(cache)
        print(f"{a.modelo}: EAM {resumen(p, t)['eam']:.1f}; registrado en este bloque USD {g1 - g0:.4f}; "
              f"uso de la clave antes {u0} y después {u1}"
              + (f" (diferencia USD {u1 - u0:.4f})" if u0 is not None and u1 is not None else ""))
        return 0
    out = {"n": len(t), "vara": VARA, "modelos": {}}
    for nombre, modelo in MODELOS.items():
        p = correr(t, llamar, cache, modelo)
        out["modelos"][nombre] = {"modelo": modelo, **resumen(p, t), "por_pregunta": p.to_dict("records")}
        r = out["modelos"][nombre]
        print(f"{nombre}: EAM {r['eam']:.1f} (vara {VARA}) pasa={r['pasa']} fallos={r['fallos']} "
              f"≤10: {r['dentro_10']:.0%} Bogotá {r['eam_bogota']:.1f}")
    e = {k: v["eam"] for k, v in out["modelos"].items()}
    out["predicciones"] = {"P1": e["deepseek"] > VARA, "P2": e["sonnet"] > VARA,
                           "P3": all(v < 23.0 for v in e.values()), "P4": e["sonnet"] < e["deepseek"]}
    out["gasto"] = e9.gasto_registrado(cache) if not a.simulado else None
    print(f"predicciones: {out['predicciones']}; gasto: {out['gasto'] and round(out['gasto']['costo_usd'], 4)}")
    if not a.simulado:
        (ba.SALIDA / SALIDA_NOMBRE).write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
