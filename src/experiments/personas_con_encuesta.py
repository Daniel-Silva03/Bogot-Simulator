"""
Personas con su encuesta (`docs/PERSONAS_CON_ENCUESTA_SPECIFICATION.md`): un modelo de lenguaje responde 6 preguntas
escondidas como cada uno de 200 encuestados reales de la EPC 2025, conociendo sus otras respuestas. Contra una constante, una
regresión y la estimación de la página.

Uso:
    python src/experiments/personas_con_encuesta.py --simulado   # sin gasto
    python src/experiments/personas_con_encuesta.py --prueba     # 1 llamada, mide el costo
    python src/experiments/personas_con_encuesta.py              # la corrida (tope USD 1)

DECISIONES DE IMPLEMENTACIÓN
============================

DI-PC1. **El perfil** son las respuestas de la persona a las preguntas del catálogo 2022-2025 que se miden en 2025, con el
    texto de la pregunta y la etiqueta de su respuesta («No sabe» para los códigos sin etiqueta en la escala), más sexo,
    edad, estrato y localidad. La columna de 2025 de cada pregunta es la del inventario; para las de Galán, la de su pregunta
    base (DI-PO6).
DI-PC2. **Una llamada por persona** con las 6 preguntas, como en una encuesta: responde todas a la vez. Si la respuesta no se
    puede leer o trae un código que no está en la escala, ese par queda sin respuesta y se reporta cuántos.
DI-PC3. **La regresión** usa las respuestas del perfil como números (código de 2025; los «no sabe», con la media) y las cuatro
    demográficas; para el total, una regresión lineal del indicador del lado favorable. Es la referencia de §3.
DI-PC4. **Nada individual se imprime ni se sube.** Se reportan cifras agregadas y, por pregunta, el total de Bogotá (la EPC es
    pública).
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.experiments import experimento9 as e9            # noqa: E402

SALIDA = RAIZ / "data" / "processed" / "personas_con_encuesta"
SEMILLA = 20261014
N = 200
MODELO = "openai/gpt-6-luna"
TEMPERATURA = 1.0
TOPE_USD = 1.0
ESCONDIDAS = ("CON_4", "CON_5", "CON_7", "GOB_7", "MOV_6", "FIN_3")
#: ACTUALIDAD_EPC: sexo (1=hombre), edad y estrato de 2024, con los nombres de 2025 (revisado en las etiquetas del .dta)
ALIAS_DEMOGRAFIA = {2024: {"DMO_1": "SEXO", "DMO_3_1": "CS2", "DMO_4_1": "CS2_1"}}
PAGINA_ERROR = 12.2                                          # §2: el error de la página en estas 6
LOCALIDADES = {1: "Usaquén", 2: "Chapinero", 3: "Santa Fe", 4: "San Cristóbal", 5: "Usme", 6: "Tunjuelito", 7: "Bosa",
               8: "Kennedy", 9: "Fontibón", 10: "Engativá", 11: "Suba", 12: "Barrios Unidos", 13: "Teusaquillo",
               14: "Los Mártires", 15: "Antonio Nariño", 16: "Puente Aranda", 17: "La Candelaria", 18: "Rafael Uribe Uribe",
               19: "Ciudad Bolívar"}
SISTEMA = (
    "Vas a responder una encuesta como una persona real de Bogotá. Te doy quién es y lo que respondió a otras preguntas de la "
    "misma encuesta, en 2025. Responde como respondería ELLA, no como crees que debería responder la gente en general: usa "
    "lo que dicen sus respuestas sobre lo que piensa y cómo vive. Para cada pregunta nueva elige UN código de su escala.\n"
    "Responde SOLO con un JSON, sin texto alrededor, con las claves de las preguntas y el código elegido, por ejemplo "
    '{"E1": 2, "E2": 4}.')


def escondidas() -> list[dict]:
    """§2: las 6, con el texto, las categorías y los favorables de `banco_lote8`."""
    from src.experiments import banco_lote8 as b8
    from src.experiments import banco_reales as br
    por_var = {v: (txt, cats, fav) for v, _, txt, cats, fav in b8.PREGUNTAS}
    out = []
    for k, v in enumerate(ESCONDIDAS, 1):
        txt, cats, fav = por_var[v]
        c = br.categorias(cats)
        out.append({"clave": f"E{k}", "variable": v, "pregunta": txt, "categorias": c, "validos": br.validos(c), "fav": fav})
    return out


def perfil_texto(demo: dict, respuestas: list[tuple[str, str]]) -> str:
    """DI-PC1."""
    lineas = [f"Sexo: {demo['sexo']}. Edad: {demo['edad']} años. Estrato: {demo['estrato']}. Localidad: {demo['localidad']}.",
              "", "Lo que respondió:"]
    lineas += [f"- {p} → {r}" for p, r in respuestas]
    return "\n".join(lineas)


def usuario(perfil: str, esc: list[dict]) -> str:
    preg = "\n".join(f'{e["clave"]}. {e["pregunta"]} Opciones: ' + "; ".join(f"{c}={t}" for c, t in e["categorias"].items())
                     for e in esc)
    return f"QUIÉN ES:\n{perfil}\n\nPREGUNTAS NUEVAS:\n{preg}"


def leer(texto: str, esc: list[dict]) -> dict[str, Optional[int]]:
    """DI-PC2."""
    d = e9._json_de(texto) or {}
    out = {}
    for e in esc:
        try:
            c = int(d.get(e["clave"]))
        except (TypeError, ValueError):
            c = None
        out[e["clave"]] = c if c in e["categorias"] else None
    return out


def a_100(c: float, validos: list[int]) -> float:
    return 100 * (c - min(validos)) / (max(validos) - min(validos))


def datos_2025():
    """(base con peso y localidad, datos con columnas en mayúsculas, el perfil por pregunta: [(texto, columna, ficha)])."""
    return datos(2025)


def datos(anio: int = 2025):
    """Lo mismo que `datos_2025` para la ola de otro año (ACTUALIDAD_EPC: los agentes de 2024)."""
    from src.population import armonizar_epc as ae
    from src.population import poblacion_epc_olas as po
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        base, ola = ae.cargar_ola(anio)
    d = ola["datos"].copy()
    d.columns = [c.upper() for c in d.columns]
    for nuevo, viejo in ALIAS_DEMOGRAFIA.get(anio, {}).items():          # ACTUALIDAD_EPC: los mismos nombres que en 2025
        if nuevo not in d.columns and viejo in d.columns:
            d[nuevo] = d[viejo]
    cat = json.loads((po.SALIDA_2025 / "catalogo.json").read_text(encoding="utf-8"))["dentro"]
    inv = pd.read_csv(ae.INVENTARIO)
    inv = inv[(inv.estado == "ok") & (inv.anio == anio)].set_index("variable").codigo
    perfil = []
    for f in cat:
        if anio not in f["anios"]:
            continue
        base_v = po.GALAN[f["variable"]][0] if f["variable"] in po.GALAN else f["variable"]
        c = str(inv[base_v]).upper()
        if c in d.columns and c not in ESCONDIDAS:
            perfil.append((f["pregunta"].strip(), c, f))
    return base.reset_index(drop=True), d.reset_index(drop=True), perfil


def etiqueta(f: dict, codigo) -> str:
    try:
        return str(f["etiquetas"][str(int(codigo))]).strip()
    except (KeyError, TypeError, ValueError):
        return "No sabe / no responde"


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simulado", action="store_true")
    ap.add_argument("--prueba", action="store_true")
    a = ap.parse_args(argv)
    esc = escondidas()
    base, d, perfil = datos_2025()
    ok_loc = base.cod_loc.between(1, 19).to_numpy()
    elegibles = np.flatnonzero(ok_loc)
    muestra = np.sort(np.random.default_rng(SEMILLA).choice(elegibles, N, replace=False))
    resto = np.setdiff1d(elegibles, muestra)
    w = base.peso.to_numpy(float)
    num = lambda c: pd.to_numeric(d[c], errors="coerce").to_numpy(float)          # noqa: E731
    demo = {"sexo": pd.Series(num("DMO_1")).map({1: "hombre", 2: "mujer"}).to_numpy(), "edad": num("DMO_3_1"),
            "estrato": num("DMO_4_1"), "localidad": base.cod_loc.map(LOCALIDADES).to_numpy()}
    if a.simulado:
        rng = np.random.default_rng(0)
        llamar = lambda m, s, u, t: json.dumps({e["clave"]: int(rng.choice(e["validos"])) for e in esc})   # noqa: E731
        cache = e9.Cache(SALIDA / "simulado" / "cache.json")
    else:
        llamar = e9.cliente_real(timeout=300, extra={"reasoning": {"effort": "low"}})
        cache = e9.Cache(SALIDA / "cache.json")
    agente = {e["clave"]: np.full(N, np.nan) for e in esc}
    for j, i in enumerate(muestra):
        if not a.simulado and e9.gasto_registrado(cache)["costo_usd"] >= TOPE_USD:
            print(f"Se llegó al tope de USD {TOPE_USD} en la persona {j}.")
            return 1
        resp = [(p, etiqueta(f, d[c].iloc[i])) for p, c, f in perfil]
        dm = {k: (int(v[i]) if isinstance(v[i], (float, np.floating)) and not np.isnan(v[i]) else v[i]) for k, v in demo.items()}
        texto, _ = e9.pedir(llamar, cache, MODELO, TEMPERATURA, SISTEMA, usuario(perfil_texto(dm, resp), esc), 0)
        for k, c in leer(texto, esc).items():
            agente[k][j] = np.nan if c is None else c
        if a.prueba:
            g = e9.gasto_registrado(cache)
            print(f"una llamada costó USD {g['costo_usd']:.4f} → las {N} costarían ~USD {N * g['costo_usd']:.2f} (tope {TOPE_USD})")
            return 0
        if (j + 1) % 25 == 0:
            print(f"   {j + 1} de {N} personas; gasto USD {e9.gasto_registrado(cache)['costo_usd']:.3f}", flush=True)
    # la regresión (DI-PC3)
    X = np.column_stack([num(c) for _, c, _ in perfil] + [num("DMO_1"), num("DMO_3_1"), num("DMO_4_1")])
    X = np.where(np.isnan(X), np.nanmean(X[resto], axis=0), X)
    from sklearn.linear_model import LinearRegression
    from src.experiments import nivel_acuerdo_catalogo as nc
    pag = pd.DataFrame(json.loads(nc.SALIDA.read_text(encoding="utf-8"))["E"]["por_pregunta"]).set_index("id").S
    filas, ind = [], {"agente": [], "constante": [], "regresion": []}
    sd_razon, sin_resp = [], 0
    for e in esc:
        y = num(e["variable"]); v = e["validos"]
        okr = np.isin(y[resto], v)
        tr = resto[okr]
        reg = LinearRegression().fit(X[tr], y[tr]).predict(X[muestra])
        regf = LinearRegression().fit(X[tr], np.isin(y[tr], e["fav"]).astype(float)).predict(X[muestra])
        const = float(np.sum(w[tr] * y[tr]) / np.sum(w[tr]))
        ym = y[muestra]; okm = np.isin(ym, v)
        ag = agente[e["clave"]]
        par = okm & ~np.isnan(ag) & np.isin(ag, v)
        sin_resp += int((okm & ~par).sum())
        r100 = np.array([a_100(c, v) for c in ym[par]])
        ind["agente"] += list(np.abs(np.array([a_100(c, v) for c in ag[par]]) - r100))
        ind["constante"] += list(np.abs(a_100(const, v) - r100))
        ind["regresion"] += list(np.abs(np.array([a_100(c, v) for c in np.clip(reg[par], min(v), max(v))]) - r100))
        sd_razon.append(float(np.std([a_100(c, v) for c in ag[par]]) / np.std(r100)))
        todos = np.flatnonzero(ok_loc & np.isin(y, v))
        real = 100 * np.sum(w[todos] * np.isin(y[todos], e["fav"])) / np.sum(w[todos])
        wm = w[muestra]
        ag_ok = ~np.isnan(ag) & np.isin(ag, v)
        tot_ag = 100 * np.sum(wm[ag_ok] * np.isin(ag[ag_ok], e["fav"])) / np.sum(wm[ag_ok])
        tot_reg = 100 * np.sum(wm * np.clip(regf, 0, 1)) / np.sum(wm)
        filas.append({"variable": e["variable"], "real_bogota": round(float(real), 1), "agente": round(float(tot_ag), 1),
                      "regresion": round(float(tot_reg), 1), "pagina": round(float(pag.get(f"EPC25_{e['variable']}", np.nan)), 1),
                      "sd_razon": round(sd_razon[-1], 2)})
    t = pd.DataFrame(filas)
    error_ind = {k: round(float(np.mean(v)), 1) for k, v in ind.items()}
    error_tot = {k: round(float((t[k] - t.real_bogota).abs().mean()), 1) for k in ("agente", "regresion", "pagina")}
    razon = round(float(np.mean(sd_razon)), 2)
    regla = {"R1": error_ind["agente"] < error_ind["constante"], "R2": error_tot["agente"] < PAGINA_ERROR, "R3": razon >= 0.6}
    regla["pasa"] = all(regla.values())
    pred = {"PP1": regla["R1"], "PP2": error_ind["regresion"] < error_ind["agente"], "PP3": not regla["R3"],
            "PP4": not regla["pasa"]}
    print(t.to_string(index=False))
    print(f"error individual: {error_ind} | error del total: {error_tot} | razón de desviaciones del agente: {razon} | "
          f"pares sin respuesta del agente: {sin_resp}")
    gasto = None if a.simulado else e9.gasto_registrado(cache)
    print(f"regla: {regla} | predicciones: {pred} | gasto: {gasto and round(gasto['costo_usd'], 4)}")
    sal = SALIDA / ("simulado" if a.simulado else "")
    sal.mkdir(parents=True, exist_ok=True)
    (sal / "resultado.json").write_text(json.dumps({"por_pregunta": filas, "error_individual": error_ind,
                                                    "error_total": error_tot, "razon_sd": razon, "sin_respuesta": sin_resp,
                                                    "regla": regla, "predicciones": pred, "gasto": gasto,
                                                    "n_perfil": len(perfil)}, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
