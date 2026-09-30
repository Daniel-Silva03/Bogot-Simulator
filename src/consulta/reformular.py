"""
src/consulta/reformular.py

Reformulación sugerida (D17, pieza 3): de la pregunta que alguien escribe a una que
el simulador pueda responder, o a un «no hay con qué». Especificación y pre-registro
de su validación: `docs/REFORMULACION_SPECIFICATION.md`.

Uso:
    python src/consulta/reformular.py "¿Apoyarían cobrar por entrar en carro al centro?"
    python src/consulta/reformular.py --validar             # las 24 de §3 (pide confirmación)
    python src/consulta/reformular.py --validar --simulado  # sin gasto

DECISIONES DE IMPLEMENTACIÓN
============================

DI-RF1. **El catálogo que ve el modelo es el completo (102 preguntas)**, no el del
    puente (91): en la página ninguna pregunta está escondida. Cada una va con su
    código, su texto y sus etiquetas, como en el puente.

DI-RF2. **La validación de §2 es estricta y no repara nada.** Un alcance distinto de
    los tres, un código que no existe, una reformulada vacía o de más de 300
    caracteres, o una escala que no tenga exactamente cinco etiquetas, dan una
    respuesta inválida. `fuera` no exige escala (no hay pregunta que responder).

DI-RF3. **La caché es la del Experimento 9** (por contenido: modelo, temperatura,
    instrucción, pregunta), en `data/processed/reformulacion/cache.json`, que no se
    sube: guarda las preguntas de quien use la página.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Callable, Optional

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "reformulacion"
CATALOGO = RAIZ / "data" / "processed" / "poblacion_epc2023" / "catalogo.json"
MODELO = e9.MODELO
TEMPERATURA = 0.0
ALCANCES = ("catalogo", "nueva", "fuera")
MAX_CARACTERES = 300

SISTEMA = (
    "Ayudas a una página que simula cómo respondería la población de Bogotá preguntas de OPINIÓN "
    "o de APROBACIÓN de un cambio en la ciudad, con datos de la Encuesta de Percepción Ciudadana 2023. "
    "Te doy la pregunta que escribió una persona y el CATÁLOGO de preguntas que la encuesta sí midió.\n"
    "Clasifícala en uno de tres alcances:\n"
    "- \"catalogo\": la pregunta ya está en el catálogo, aunque esté dicha con otras palabras. "
    "Da su código.\n"
    "- \"nueva\": es de opinión o de aprobación de un cambio en Bogotá y no está en el catálogo. "
    "Reescríbela como pregunta de encuesta: una sola idea, redacción neutral que no induzca la "
    "respuesta, en el contexto de Bogotá, y una escala de 5 puntos con sus etiquetas de menor a mayor.\n"
    "- \"fuera\": no se puede responder así: un dato o una cifra, una predicción electoral, intención "
    "de voto o preferencia por candidatos, lo que piensa una persona concreta, o información sensible "
    "de personas. Explica por qué y, si existe, sugiere en \"reformulada\" una pregunta cercana que sí "
    "sea de opinión.\n"
    "Responde SOLO con un JSON, sin texto alrededor:\n"
    '{"alcance": "catalogo|nueva|fuera", "codigo": "XX o null", "reformulada": "...", '
    '"escala": ["...", "...", "...", "...", "..."], "razon": "una frase"}'
)

Llamar = Callable[[str, str, str, float], object]


class ReformulacionError(RuntimeError):
    """Algo impide reformular como está especificado."""


def cargar_catalogo(ruta: Path = CATALOGO) -> dict[str, dict]:
    """DI-RF1: las 102 preguntas de la población EPC 2023."""
    return {c["variable"]: c for c in json.loads(ruta.read_text(encoding="utf-8"))["dentro"]}


def _ficha(f: dict) -> str:
    etq = "; ".join(f"{k}={v}" for k, v in f["etiquetas"].items() if int(k) in f["escala"])
    return f'{f["variable"]} | {f["pregunta"]} | {etq}'


def prompt(pregunta: str, catalogo: dict[str, dict]) -> str:
    cat = "\n".join(_ficha(f) for f in catalogo.values())
    return f"PREGUNTA DE LA PERSONA:\n{pregunta.strip()}\n\nCATÁLOGO:\n{cat}"


def parsear(texto: Optional[str], catalogo: dict[str, dict]) -> Optional[dict]:
    """DI-RF2: None si la respuesta no cumple §2."""
    d = e9._json_de(texto)
    if not isinstance(d, dict):
        return None
    alcance = str(d.get("alcance", "")).strip().lower()
    if alcance not in ALCANCES:
        return None
    codigo = d.get("codigo")
    codigo = None if codigo in (None, "", "null") else str(codigo).strip()
    reformulada = str(d.get("reformulada") or "").strip()
    escala = d.get("escala")
    if alcance == "catalogo" and codigo not in catalogo:
        return None
    if alcance == "nueva":
        if not 1 <= len(reformulada) <= MAX_CARACTERES:
            return None
        if not isinstance(escala, list) or len(escala) != 5 or not all(str(x).strip() for x in escala):
            return None
    return {"alcance": alcance, "codigo": codigo if alcance == "catalogo" else None,
            "reformulada": reformulada, "escala": [str(x).strip() for x in escala] if isinstance(escala, list) else None,
            "razon": str(d.get("razon") or "").strip()}


def reformular(pregunta: str, catalogo: dict[str, dict], llamar: Llamar, cache: e9.Cache,
               modelo: str = MODELO) -> tuple[Optional[dict], str]:
    """(respuesta validada o None, texto crudo del modelo)."""
    texto, _ = e9.pedir(llamar, cache, modelo, TEMPERATURA, SISTEMA, prompt(pregunta, catalogo), 0)
    return parsear(texto, catalogo), texto


# --------------------------------------------------------------------------
# La validación de §3 y §4

#: §3, tal como quedó escrito: (pregunta, alcance esperado, código esperado)
PRUEBA = (
    ("¿La gente se siente segura caminando por su barrio?", "catalogo", "VS8"),
    ("¿Qué tan contentos están los bogotanos de vivir en la ciudad?", "catalogo", "CV1"),
    ("¿La gente cree que la corrupción ha aumentado?", "catalogo", "GG7"),
    ("¿Cómo califica la gente la gestión del alcalde?", "catalogo", "GG3"),
    ("¿Están satisfechos con la recolección de basuras?", "catalogo", "SP4"),
    ("¿Qué piensan de la calidad del aire en Bogotá?", "catalogo", "MA3_1"),
    ("¿Las cosas en la ciudad van por buen camino?", "catalogo", "AG1"),
    ("¿Qué tan orgullosos se sienten de Bogotá?", "catalogo", "AG2"),
    ("¿Estarían de acuerdo con cobrar por entrar en carro al centro?", "nueva", None),
    ("¿Apoyarían extender el pico y placa a todo el día?", "nueva", None),
    ("¿Les gustaría que el metro funcionara las 24 horas?", "nueva", None),
    ("¿Aprobarían subir el predial para pagar más policías?", "nueva", None),
    ("¿Estarían de acuerdo con prohibir las motos en las ciclorrutas?", "nueva", None),
    ("¿Apoyarían volver peatonal toda la carrera séptima?", "nueva", None),
    ("¿Qué opinan de poner más cámaras de vigilancia en los parques?", "nueva", None),
    ("¿Estarían a favor de cerrar los bares a medianoche?", "nueva", None),
    ("¿Les parecería bien hacer más ciclorrutas aunque se quiten carriles a los carros?", "nueva", None),
    ("¿Apoyarían un toque de queda para menores de edad?", "nueva", None),
    ("¿Por quién van a votar para la alcaldía?", "fuera", None),
    ("¿Cuántos habitantes tiene Bogotá?", "fuera", None),
    ("¿Qué piensa mi vecino Carlos de la alcaldía?", "fuera", None),
    ("¿Cuánto cuesta el pasaje de TransMilenio?", "fuera", None),
    ("¿Cuántas personas en Suba tienen VIH?", "fuera", None),
    ("¿Va a ganar Abelardo las elecciones?", "fuera", None),
)


def evaluar(respuestas: list[Optional[dict]], prueba=PRUEBA) -> dict:
    """R1-R4 (§4) y la regla."""
    alc = [r["alcance"] if r else None for r in respuestas]
    r1 = sum(a == e for a, (_, e, _) in zip(alc, prueba))
    cat = [(r, c) for r, (_, e, c) in zip(respuestas, prueba) if e == "catalogo"]
    r2 = sum(bool(r) and r["alcance"] == "catalogo" and r["codigo"] == c for r, c in cat)
    fue = [r for r, (_, e, _) in zip(respuestas, prueba) if e == "fuera"]
    r3 = sum(bool(r) and r["alcance"] == "fuera" for r in fue)
    r3_cat = sum(bool(r) and r["alcance"] == "catalogo" for r in fue)
    r4 = sum(r is not None for r in respuestas)
    crit = {
        "R1": {"umbral": "alcance esperado en ≥ 20 de 24", "valor": r1, "se_cumple": r1 >= 20},
        "R2": {"umbral": "código esperado en ≥ 6 de 8", "valor": r2, "se_cumple": r2 >= 6},
        "R3": {"umbral": "fuera detectadas ≥ 5 de 6, ninguna como catálogo", "valor": [r3, r3_cat],
               "se_cumple": r3 >= 5 and r3_cat == 0},
        "R4": {"umbral": "respuesta válida en ≥ 23 de 24", "valor": r4, "se_cumple": r4 >= 23},
    }
    todos = all(c["se_cumple"] for c in crit.values())
    regla = ("La reformulación entra a la página como está." if todos else
             "Se ajusta la instrucción, con enmienda fechada, y se valida con otras 24 preguntas nuevas.")
    return {"criterios": crit, "pasa": todos, "regla": regla}


def modelo_simulado(catalogo: dict[str, dict]) -> Llamar:
    """Contesta según la tabla de §3: sirve para probar el circuito, no para medir."""
    esperado = {p: (a, c) for p, a, c in PRUEBA}

    def llamar(modelo, sistema, usuario, temp):
        preg = usuario.split("\n")[1]
        a, c = esperado.get(preg, ("nueva", None))
        return json.dumps({"alcance": a, "codigo": c, "reformulada": f"¿Qué tan de acuerdo está con: {preg}?",
                           "escala": ["Muy en desacuerdo", "En desacuerdo", "Ni de acuerdo ni en desacuerdo",
                                      "De acuerdo", "Muy de acuerdo"], "razon": "simulado"})
    return llamar


def main(argv=None, entrada=input) -> int:
    ap = argparse.ArgumentParser(description="Reformulación sugerida (D17, pieza 3).")
    ap.add_argument("pregunta", nargs="?", help="una pregunta para reformular")
    ap.add_argument("--validar", action="store_true", help="las 24 preguntas de §3")
    ap.add_argument("--simulado", action="store_true", help="modelo simulado, sin gasto")
    args = ap.parse_args(argv)
    if not args.validar and not args.pregunta:
        ap.error("pasa una pregunta o --validar")
    catalogo = cargar_catalogo()
    salida = SALIDA / ("simulado" if args.simulado else "")
    cache = e9.Cache(salida / "cache.json")
    preguntas = [p for p, _, _ in PRUEBA] if args.validar else [args.pregunta]
    if args.simulado:
        llamar, modelo = modelo_simulado(catalogo), e9.MODELO_SIMULADO
    else:
        llamar, modelo = e9.cliente_real(), MODELO
        pend = [(SISTEMA, prompt(p, catalogo), 300) for p in preguntas
                if e9.Cache.clave(modelo, TEMPERATURA, SISTEMA, prompt(p, catalogo), 0) not in cache]
        if not e9.confirmar_gasto(pend, entrada, e9.gasto_registrado(cache)):
            print("No se gastó nada.")
            return 1
    respuestas, crudas = [], []
    try:
        for p in preguntas:
            r, t = reformular(p, catalogo, llamar, cache, modelo)
            respuestas.append(r)
            crudas.append(t)
    except e9.Experimento9Error as e:
        print(f"\nERROR: {e}\nLo respondido quedó en la caché; al volver a correr solo se pide lo que falta.")
        return 1
    for p, r in zip(preguntas, respuestas):
        if r is None:
            print(f"\n{p}\n  → no pude reformular esta pregunta (respuesta inválida)")
            continue
        extra = f" [{r['codigo']}: {catalogo[r['codigo']]['pregunta']}]" if r["codigo"] else ""
        print(f"\n{p}\n  → {r['alcance']}{extra}\n    {r['reformulada']}")
        if r["alcance"] == "nueva":
            print(f"    escala: {' / '.join(r['escala'])}")
        print(f"    razón: {r['razon']}")
    if args.validar:
        v = evaluar(respuestas)
        salida.mkdir(parents=True, exist_ok=True)
        (salida / "resultado.json").write_text(json.dumps({
            "prueba": [{"pregunta": p, "esperado": [a, c], "respuesta": r}
                       for (p, a, c), r in zip(PRUEBA, respuestas)],
            **v, "modelo": modelo, "gasto": e9.gasto_registrado(cache)}, ensure_ascii=False, indent=2), encoding="utf-8")
        print()
        for k, c in v["criterios"].items():
            print(f"  {k} {'se cumple' if c['se_cumple'] else 'NO se cumple'} — {c['umbral']} (valor {c['valor']})")
        print(f"\n{v['regla']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
