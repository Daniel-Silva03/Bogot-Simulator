"""
Expected Parrot con toda la muestra (`docs/PARROT_MUESTRA_COMPLETA_SPECIFICATION.md`): cada persona de la EPC es un agente, para
quitar el azar de elegir 200. Solo el modelo nuestro (Daniel: «usa luna»), en la gestión del alcalde de tres transiciones y hacia
la EPC 2026.

Tres pasos, como `expected_parrot.py`:
    python src/evaluacion/parrot_muestra_completa.py exportar
    .\\venv_edsl\\Scripts\\python.exe src/evaluacion/parrot_muestra_completa.py correr [--simulado]
    python src/evaluacion/parrot_muestra_completa.py evaluar [--simulado]

DECISIONES DE IMPLEMENTACIÓN
============================

DI-PM1. **La forma de preguntar es la de `expected_parrot.py`** (DI-EP1 a DI-EP3): EDSL en local, `QuestionMultipleChoice` sin
    comentario, la instrucción de la página y el perfil como único rasgo. Se cuenta «buena» o «muy buena», ponderado.
DI-PM2. **Los perfiles** son los de la página para cada persona de la ola (`personas_politica.perfil`); en 2022 y 2023, con la
    calificación del alcalde y del Concejo de ese año (`replica_alcalde.datos_con_gobierno`), como ya trae el de 2024 y 2025.
DI-PM3. **La nota de fecha** va en todas las corridas, con los años de cada una.
DI-PM4. **El tope** se revisa cada `TANDA` agentes con lo que OpenRouter dice que gastó la clave (`expected_parrot.usado`).
DI-PM5. **Lo de 2026 se congela** en `config/prospectiva_epc2026/parrot_muestra_completa.json`; no se vuelve a correr.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Optional

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.evaluacion import expected_parrot as ep           # noqa: E402  (solo biblioteca estándar)

SALIDA = RAIZ / "data" / "processed" / "benchmark" / "parrot_muestra_completa"
CONGELADO = RAIZ / "config" / "prospectiva_epc2026" / "parrot_muestra_completa.json"
TOPE_USD = 1.0
TANDA = 250
LUNA = "openai/gpt-6-luna"
TEXTO = {2023: "¿Usted cómo califica la gestión de la alcaldesa de Bogotá, Claudia López?",
         2024: "¿Usted cómo califica la gestión del alcalde de Bogotá, Carlos Fernando Galán?",
         2025: "¿Usted cómo califica la gestión del alcalde de Bogotá, Carlos Fernando Galán?",
         2026: "¿Usted cómo califica la gestión del alcalde de Bogotá, Carlos Fernando Galán?"}
CORRIDAS = [  # (nombre, año base, año objetivo, modelo)
    ("T0_luna", 2022, 2023, LUNA), ("T1_luna", 2023, 2024, LUNA), ("T2_luna", 2024, 2025, LUNA), ("F_luna", 2025, 2026, LUNA),
]
#: Gestión del alcalde, buena o muy buena, en toda la EPC (`serie_epc_bcv.csv`); 2026 aún no existe
EPC = {2022: 33.1, 2023: 31.1, 2024: 42.3, 2025: 26.4}


def nota(base: int, obj: int) -> str:
    return (f"Lo que sabes de esta persona es de {base}. Esta pregunta es de finales de {obj}, casi un año después: la persona "
            "puede haber cambiado de opinión.")


def exportar() -> int:
    """Con el venv del proyecto: los perfiles y pesos de toda la muestra de cada año base (DI-PM2)."""
    import numpy as np
    from src.evaluacion import replica_alcalde as ra
    from src.experiments import personas_con_encuesta as pc
    from src.experiments import personas_politica as pq
    from src.experiments import personas_pulidas as pp
    paneles = {}
    for anio in (2022, 2023, 2024, 2025):
        datos = ra.datos_con_gobierno(anio) if anio in (2022, 2023) else pc.datos(anio)
        base = datos[0]
        idx = np.flatnonzero(base.cod_loc.between(1, 19).to_numpy() & base.peso.notna().to_numpy())
        paneles[str(anio)] = [{"persona": int(i), "perfil": pq.perfil(int(i), datos, [], {}, con_vida=False),
                               "peso": float(base.peso.iloc[i])} for i in idx]
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "paneles.json").write_text(json.dumps({"instruccion": pp.BASE.strip(), "paneles": paneles}, ensure_ascii=False),
                                         encoding="utf-8")
    print({k: len(v) for k, v in paneles.items()})
    return 0


def correr(simulado: bool) -> int:
    from edsl import Agent, AgentList, Model, QuestionMultipleChoice
    d = json.loads((SALIDA / "paneles.json").read_text(encoding="utf-8"))
    if not simulado:
        os.environ["OPEN_ROUTER_API_KEY"] = os.environ["OPENROUTER_API_KEY"]
    destino = SALIDA / ("simulado" if simulado else "")
    destino.mkdir(parents=True, exist_ok=True)
    ruta = destino / "respuestas.json"
    hechas = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}
    inicio_total = 0.0 if simulado else ep.usado() - sum(c["costo_usd"] or 0 for c in hechas.values())
    for nombre, base, obj, modelo in CORRIDAS:
        if nombre in hechas and hechas[nombre]["completa"]:
            continue
        q = QuestionMultipleChoice(question_name="alcalde", question_text=f"{nota(base, obj)}\n\n{TEXTO[obj]}",
                                   question_options=ep.OPCIONES, include_comment=False)
        m = (Model("test", service_name="test", canned_response="Regular gestión") if simulado
             else Model(modelo, service_name="open_router", temperature=1.0))
        perfiles = d["paneles"][str(base)]
        resp, inicio, completa = [], (0.0 if simulado else ep.usado()), True
        for i in range(0, len(perfiles), TANDA):                                               # DI-PM4
            if not simulado and ep.usado() - inicio_total >= TOPE_USD:
                print(f"Se llegó al tope de USD {TOPE_USD} en {nombre}: queda incompleta.")
                completa = False
                break
            agentes = AgentList([Agent(traits={"perfil": x["perfil"]}, traits_presentation_template="{{perfil}}",
                                       instruction=d["instruccion"]) for x in perfiles[i:i + TANDA]])
            r = q.by(agentes).by(m).run(disable_remote_inference=True, disable_remote_cache=True, cache=False, verbose=False,
                                        print_exceptions=False)
            resp += r.select("answer.alcalde").to_list()
        costo = None if simulado else round(ep.usado() - inicio, 4)
        hechas[nombre] = {"base": base, "objetivo": obj, "modelo": modelo, "respuestas": resp, "costo_usd": costo,
                          "completa": completa, "fecha": time.strftime("%Y-%m-%d %H:%M")}
        ruta.write_text(json.dumps(hechas, ensure_ascii=False), encoding="utf-8")
        print(f"{nombre}: {sum(x in ep.OPCIONES for x in resp)} de {len(perfiles)} válidas; USD {costo}", flush=True)
        if not completa:
            break
    return 0


def leer(res: dict, d: dict) -> dict:
    """§6 del pre-registro."""
    out = {}
    for nombre, c in res.items():
        pesos = [x["peso"] for x in d["paneles"][str(c["base"])]][:len(c["respuestas"])]
        out[nombre] = {"base": c["base"], "objetivo": c["objetivo"], "modelo": c["modelo"], "completa": c["completa"],
                       "cifra": ep.cifra(c["respuestas"], pesos), "costo_usd": c["costo_usd"],
                       "validas": sum(x in ep.OPCIONES for x in c["respuestas"])}
    for v in out.values():
        if v["objetivo"] in EPC and v["cifra"] is not None:
            p, r = EPC[v["base"]], EPC[v["objetivo"]]
            v.update({"P": p, "real": r, "error": round(abs(v["cifra"] - r), 2), "error_P": round(abs(p - r), 2),
                      "sentido_correcto": (v["cifra"] - p) * (r - p) > 0})
    luna = [out[f"T{k}_luna"] for k in range(3) if "error" in out.get(f"T{k}_luna", {})]
    lectura = {}
    if len(luna) == 3:
        lectura["RT1_gana_en_2_de_3"] = sum(v["error"] < v["error_P"] for v in luna) >= 2
        lectura["RT2_un_punto_mejor"] = (sum(v["error"] for v in luna) / 3) <= (sum(v["error_P"] for v in luna) / 3) - 1
        lectura["RT3_sentido_correcto"] = sum(v["sentido_correcto"] for v in luna)
        lectura["se_reproduce"] = lectura["RT1_gana_en_2_de_3"] and lectura["RT2_un_punto_mejor"]
    t2 = out.get("T2_luna", {}).get("cifra")
    lectura["predicciones"] = {"PM1": None if not lectura else not lectura.get("se_reproduce"),
                               "PM2": None if t2 is None else t2 >= ep.UMBRAL_CAIDA}
    return {"corridas": out, "lectura": lectura}


def evaluar(simulado: bool) -> int:
    d = json.loads((SALIDA / "paneles.json").read_text(encoding="utf-8"))
    destino = SALIDA / ("simulado" if simulado else "")
    res = leer(json.loads((destino / "respuestas.json").read_text(encoding="utf-8")), d)
    (destino / "evaluacion.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=bool), encoding="utf-8")
    f = {k: v for k, v in res["corridas"].items() if k.startswith("F_")}
    if f and not simulado:                                                                     # DI-PM5
        if CONGELADO.exists():
            print("Lo de 2026 ya estaba congelado: no se reescribe.")
        else:
            CONGELADO.write_text(json.dumps({"fecha": time.strftime("%Y-%m-%d %H:%M"), "pregunta": TEXTO[2026],
                                             "nota": nota(2025, 2026), "predicciones": f}, ensure_ascii=False, indent=1),
                                 encoding="utf-8")
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
