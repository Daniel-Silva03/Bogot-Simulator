"""
¿Pasa lo mismo con Expected Parrot? (`docs/EXPECTED_PARROT_SPECIFICATION.md`). Los mismos perfiles de la EPC, como agentes de EDSL,
con la pregunta de la gestión de Galán: A, equivalencia con la página (perfiles 2025); B, la caída de 2025 con perfiles de 2024 y
tres modelos.

EDSL va en su propio ambiente (`venv_edsl`, `pip install edsl==1.0.9`), así que esto corre en tres pasos:
    python src/evaluacion/expected_parrot.py exportar                   # con el venv del proyecto
    .\\venv_edsl\\Scripts\\python.exe src/evaluacion/expected_parrot.py correr [--simulado]
    python src/evaluacion/expected_parrot.py evaluar [--simulado]       # con el venv del proyecto

DECISIONES DE IMPLEMENTACIÓN
============================

DI-EP1. **Todo en local:** EDSL llama a OpenRouter con nuestra clave (`OPEN_ROUTER_API_KEY`, copiada en el proceso desde
    `OPENROUTER_API_KEY`), con `disable_remote_inference` y `disable_remote_cache`. Nada pasa por los servidores de Expected Parrot.
DI-EP2. **El agente de EDSL** lleva el perfil completo de la página como su único rasgo, y la instrucción de la página
    (`personas_pulidas.BASE`, sin la salida de probabilidades). La pregunta es `QuestionMultipleChoice`, la forma propia de EDSL:
    cada agente elige una opción, sin comentario.
DI-EP3. **La cifra** es el porcentaje ponderado (peso de la encuesta) de «Buena gestión» o «Muy buena gestión» entre los agentes que
    eligieron una opción válida.
DI-EP4. **El tope** se revisa cada 50 agentes, con el costo que reporta EDSL; si se llega a él, la corrida queda incompleta y no
    se empieza otra.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "data" / "processed" / "benchmark" / "expected_parrot"
TOPE_USD = 2.0
TANDA = 50
OPCIONES = ["Muy mala gestión", "Mala gestión", "Regular gestión", "Buena gestión", "Muy buena gestión"]
FAVORABLES = {"Buena gestión", "Muy buena gestión"}
NOTA_B = ("Lo que sabes de esta persona es de 2024. Esta pregunta es de finales de 2025, casi un año después: la persona puede haber "
          "cambiado de opinión.")
CORRIDAS = [  # (nombre, panel, modelo)
    ("A_luna_2025", 2025, "openai/gpt-6-luna"),
    ("B_luna_2024", 2024, "openai/gpt-6-luna"),
    ("B_sonnet_2024", 2024, "anthropic/claude-sonnet-5.5"),
    ("B_gemini_2024", 2024, "google/gemini-4-argon"),
]
#: Las referencias, ya medidas antes de este pre-registro
PAGINA_2025 = 27.21          # ALCALDE_SIN_NOMBRE, condición A
G_2025 = 29.3                # Fase B: agentes de 2024 para Galán 2025
P_2025, REAL_2025 = 42.3, 26.4
UMBRAL_CAIDA = (P_2025 + REAL_2025) / 2


def exportar() -> int:
    """Con el venv del proyecto: los perfiles y pesos de los 200 agentes de 2025 y de 2024, y los textos."""
    sys.path.insert(0, str(RAIZ))
    from src.consulta import agentes as ag
    from src.consulta import motor as mo
    from src.experiments import personas_con_encuesta as pc
    from src.experiments import personas_pulidas as pp
    paneles = {}
    for anio in (2025, 2024):
        p = ag.Agentes() if anio == 2025 else ag.Agentes(datos=pc.datos(anio))
        paneles[str(anio)] = [{"persona": int(i), "perfil": t, "peso": float(w)}
                              for i, t, w in zip(p.personas, p.perfiles, p.peso)]
    texto = mo.GALAN_SOLO_AGENTES["GG3_GALAN"]
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "paneles.json").write_text(json.dumps({"instruccion": pp.BASE.strip(), "pregunta": texto,
                                                     "pregunta_b": f"{NOTA_B}\n\n{texto}", "paneles": paneles},
                                                    ensure_ascii=False), encoding="utf-8")
    print({k: len(v) for k, v in paneles.items()})
    return 0


def correr(simulado: bool) -> int:
    """Con `venv_edsl`: DI-EP1 a DI-EP4."""
    from edsl import Agent, AgentList, Model, QuestionMultipleChoice
    d = json.loads((SALIDA / "paneles.json").read_text(encoding="utf-8"))
    if not simulado:
        os.environ["OPEN_ROUTER_API_KEY"] = os.environ["OPENROUTER_API_KEY"]
    destino = SALIDA / ("simulado" if simulado else "")
    destino.mkdir(parents=True, exist_ok=True)
    ruta = destino / "respuestas.json"
    hechas = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}
    gasto = sum(c["costo_usd"] or 0 for c in hechas.values())
    for nombre, anio, modelo in CORRIDAS:
        if nombre in hechas:
            continue
        if gasto >= TOPE_USD:
            print(f"Se llegó al tope de USD {TOPE_USD}: no se corre {nombre}.")
            break
        texto = d["pregunta"] if anio == 2025 else d["pregunta_b"]
        q = QuestionMultipleChoice(question_name="alcalde", question_text=texto, question_options=OPCIONES, include_comment=False)
        m = Model("test", service_name="test", canned_response="Buena gestión") if simulado else Model(modelo, service_name="open_router", temperature=1.0)
        perfiles = d["paneles"][str(anio)]
        resp, costo, ejemplo = [], 0.0, None
        for i in range(0, len(perfiles), TANDA):                                              # DI-EP4
            if not simulado and gasto + costo >= TOPE_USD:
                print(f"Se llegó al tope de USD {TOPE_USD} en {nombre}: queda incompleta.")
                break
            agentes = AgentList([Agent(traits={"perfil": x["perfil"]}, traits_presentation_template="{{perfil}}",
                                       instruction=d["instruccion"]) for x in perfiles[i:i + TANDA]])
            r = q.by(agentes).by(m).run(disable_remote_inference=True, disable_remote_cache=True, cache=False, verbose=False,
                                        print_exceptions=False)
            resp += r.select("answer.alcalde").to_list()
            costo += float(sum(c or 0 for c in r.select("raw_model_response.alcalde_cost").to_list()))
            ejemplo = ejemplo or (r.select("prompt.alcalde_system_prompt").to_list()[0],
                                  r.select("prompt.alcalde_user_prompt").to_list()[0])
        costo = None if simulado else costo
        hechas[nombre] = {"panel": anio, "modelo": modelo, "respuestas": resp, "costo_usd": costo,
                          "completa": len(resp) == len(perfiles), "sistema_ejemplo": ejemplo[0], "usuario_ejemplo": ejemplo[1]}
        gasto += costo or 0
        ruta.write_text(json.dumps(hechas, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{nombre}: {sum(x is not None for x in resp)} de {len(resp)} respondieron; USD {costo}", flush=True)
    print(f"gasto total USD {round(gasto, 4)}")
    return 0


def cifra(respuestas: list, pesos: list[float]) -> Optional[float]:
    """DI-EP3."""
    v = [(w, x in FAVORABLES) for x, w in zip(respuestas, pesos) if x in OPCIONES]
    return round(100 * sum(w for w, f in v if f) / sum(w for w, _ in v), 2) if v else None


def leer(res: dict, d: dict) -> dict:
    """§6 del pre-registro."""
    out = {}
    for nombre, c in res.items():
        pesos = [x["peso"] for x in d["paneles"][str(c["panel"])]]
        out[nombre] = {"modelo": c["modelo"], "cifra": cifra(c["respuestas"], pesos),
                       "validas": sum(x in OPCIONES for x in c["respuestas"]), "costo_usd": c["costo_usd"]}
    a = out.get("A_luna_2025", {}).get("cifra")
    lectura = {"RA_equivalente": None if a is None else abs(a - PAGINA_2025) <= 7}
    for nombre, v in out.items():
        if nombre.startswith("B_") and v["cifra"] is not None:
            v["error"] = round(abs(v["cifra"] - REAL_2025), 2)
            v["ve_la_caida"] = v["cifra"] < UMBRAL_CAIDA
            v["le_gana_a_P"] = v["error"] < abs(P_2025 - REAL_2025)
    b = [v for k, v in out.items() if k.startswith("B_") and "ve_la_caida" in v]
    luna = out.get("B_luna_2024", {}).get("error")
    lectura["RB_ven_la_caida"] = sum(v["ve_la_caida"] for v in b)
    lectura["RC_modelo_fuerte_mejor_que_luna"] = [k for k, v in out.items() if k in ("B_sonnet_2024", "B_gemini_2024")
                                                  and luna is not None and v.get("error") is not None
                                                  and v["error"] <= luna - 3]
    lectura["predicciones"] = {"PX1": lectura["RA_equivalente"], "PX2": lectura["RB_ven_la_caida"] >= 2}
    return {"corridas": out, "lectura": lectura}


def evaluar(simulado: bool) -> int:
    d = json.loads((SALIDA / "paneles.json").read_text(encoding="utf-8"))
    destino = SALIDA / ("simulado" if simulado else "")
    res = leer(json.loads((destino / "respuestas.json").read_text(encoding="utf-8")), d)
    (destino / "evaluacion.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=bool), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=1, default=bool))
    return 0


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paso", choices=["exportar", "correr", "evaluar"])
    ap.add_argument("--simulado", action="store_true")
    a = ap.parse_args(argv)
    return exportar() if a.paso == "exportar" else correr(a.simulado) if a.paso == "correr" else evaluar(a.simulado)


if __name__ == "__main__":
    sys.exit(main())
