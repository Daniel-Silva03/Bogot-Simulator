"""
src/experiments/peso_anio_reciente.py

¿Se acerca más el dato medido a lo que la gente respondió después si pesan más los años recientes?
Especificación: `docs/PESO_ANIO_RECIENTE_SPECIFICATION.md`. Con la población 2022-2024 (sin nadie de 2025) se adivina la
EPC 2025 en las preguntas que se repitieron, con tres reglas para juntar los años.

Uso:
    python src/experiments/peso_anio_reciente.py

Escribe `data/processed/peso_anio_reciente/resultado.json` (cifras agregadas por pregunta, ciudad y localidad). No
llama a ningún modelo.

DECISIONES DE IMPLEMENTACIÓN
============================

DI-PA1. **La escala es la que muestra la página** (`motor.vista`, DI-CO19): sin «no sabe» ni las categorías que no son
    una opinión, en la población y en 2025.
DI-PA2. **El peso dentro de la localidad (§2):** en cada pregunta, el agente pesa su peso por el factor del año de su
    donante, y la suma de la localidad se reescala a la de hoy (los agentes con respuesta válida). La media por
    localidad usa el factor solo, porque la página cuenta igual a cada agente de una localidad.
DI-PA3. **El valor de 2025** es la media con los pesos de la EPC 2025 (`armonizar_epc.cargar_ola`, que reescala
    `Factor1` a la muestra: la media no cambia), en la ciudad y en cada localidad. Su columna es la del inventario.
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from src.consulta import motor as mo                      # noqa: E402
from src.population import armonizar_epc as ae           # noqa: E402

POBLACION = RAIZ / "data" / "processed" / "poblacion_epc2022_2024"
SALIDA = RAIZ / "data" / "processed" / "peso_anio_reciente"
REGLAS = ("A", "B", "C")
MEJORA_CIUDAD = 0.5                                                              # R1
TOLERANCIA_LOCALIDAD = 0.5                                                       # R2


def factor(regla: str, anio: np.ndarray, ultimo: int) -> np.ndarray:
    """§2: el factor del año del donante."""
    anio = np.asarray(anio, float)
    if regla == "A":
        return np.ones(len(anio))
    if regla == "B":
        return 2.0 ** -(ultimo - anio)
    if regla == "C":
        return (anio == ultimo).astype(float)
    raise ValueError(regla)


def a_100(m: float, esc: list[int]) -> float:
    return 100 * (m - min(esc)) / (max(esc) - min(esc))


def medias(x: np.ndarray, peso: np.ndarray, loc: np.ndarray, anio: np.ndarray, esc: list[int], regla: str,
           ultimo: int) -> tuple[float, dict[int, float]]:
    """DI-PA2: (media de la ciudad, media por localidad) en 0-100."""
    ok = np.isin(x, esc)
    f = factor(regla, anio, ultimo) * ok
    w = np.zeros(len(x))
    por_loc = {}
    for l in np.unique(loc[ok]):
        m = (loc == l) & ok
        if f[m].sum() == 0:
            continue
        w[m] = peso[m] * f[m] * peso[m].sum() / (peso[m] * f[m]).sum()
        por_loc[int(l)] = a_100(np.sum(f[m] * x[m]) / f[m].sum(), esc)
    return a_100(np.sum(w[ok] * x[ok]) / w[ok].sum(), esc), por_loc


def main() -> int:
    cat = json.loads((POBLACION / "catalogo.json").read_text(encoding="utf-8"))["dentro"]
    cat = {f["variable"]: f for f in cat}
    arm = pd.read_csv(ae.SALIDA / "items.csv")
    con_2025 = [v for v, a in zip(arm.variable, arm.anios.astype(str)) if "2025" in a.split()]
    inv = pd.read_csv(ae.INVENTARIO)
    inv = inv[(inv.estado == "ok") & (inv.anio == 2025)].set_index("variable").codigo
    don = pd.read_parquet(POBLACION / "donantes.parquet")
    col = {c.upper(): c for c in don.columns}
    ag = pd.read_parquet(POBLACION / "agentes.parquet")
    ag = ag[ag.donante_id.notna()]
    idx = ag.donante_id.astype(int).to_numpy()
    peso, loc = ag.peso.to_numpy(float), ag.cod_loc.to_numpy()
    anio = don.anio.to_numpy()[idx]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        b25, o25 = ae.cargar_ola(2025)
    filas = []
    for v in con_2025:
        f = mo.vista(cat[v])                                                     # DI-PA1
        esc = list(f["escala"])
        anios = sorted(cat[v]["anios"])
        x = pd.to_numeric(don[col[str(f["codigo"]).upper()]], errors="coerce").to_numpy(float)[idx]
        x25 = pd.to_numeric(o25["datos"][o25["col"][str(inv[v]).upper()]], errors="coerce").to_numpy(float)
        ok25 = np.isin(x25, esc) & b25.cod_loc.between(1, 19).to_numpy()
        w25, l25 = b25.peso.to_numpy(float), b25.cod_loc.to_numpy()
        real = a_100(np.sum(w25[ok25] * x25[ok25]) / w25[ok25].sum(), esc)       # DI-PA3
        real_loc = {int(l): a_100(np.sum(w25[ok25 & (l25 == l)] * x25[ok25 & (l25 == l)]) / w25[ok25 & (l25 == l)].sum(), esc)
                    for l in np.unique(l25[ok25])}
        fila = {"variable": v, "nombre": f["nombre"], "anios": anios, "real_2025": round(real, 2)}
        for r in REGLAS:
            c, pl = medias(x, peso, loc, anio, esc, r, anios[-1])
            comunes = sorted(set(pl) & set(real_loc))
            fila[r] = round(c, 2)
            fila[f"error_{r}"] = round(abs(c - real), 2)
            fila[f"error_loc_{r}"] = round(float(np.mean([abs(pl[l] - real_loc[l]) for l in comunes])), 2)
        filas.append(fila)
    t = pd.DataFrame(filas)
    varios = t[t.anios.map(len) >= 2]

    def resumen(d):
        return {r: {"ciudad": round(float(d[f"error_{r}"].mean()), 2), "localidad": round(float(d[f"error_loc_{r}"].mean()), 2)}
                for r in REGLAS}
    dec, todas = resumen(varios), resumen(t)
    r1 = dec["A"]["ciudad"] - dec["B"]["ciudad"] >= MEJORA_CIUDAD
    r2 = dec["B"]["localidad"] - dec["A"]["localidad"] <= TOLERANCIA_LOCALIDAD
    out = {"preguntas": len(t), "con_2_o_mas_anios": len(varios), "decide": dec, "todas": todas,
           "R1": {"umbral": f"B al menos {MEJORA_CIUDAD} menor que A en la ciudad", "se_cumple": bool(r1)},
           "R2": {"umbral": f"B no sube más de {TOLERANCIA_LOCALIDAD} por localidad", "se_cumple": bool(r2)},
           "pasa_B": bool(r1 and r2), "por_pregunta": filas}
    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "resultado.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(t[["variable", "anios", "real_2025", "A", "B", "C", "error_A", "error_B", "error_C"]].to_string(index=False))
    print(f"\n{len(t)} preguntas; deciden las {len(varios)} con 2 o más años")
    for r in REGLAS:
        print(f"  {r}: ciudad {dec[r]['ciudad']:.2f} · localidad {dec[r]['localidad']:.2f}"
              f"   (todas: {todas[r]['ciudad']:.2f} · {todas[r]['localidad']:.2f})")
    print(f"R1 {'se cumple' if r1 else 'NO se cumple'} · R2 {'se cumple' if r2 else 'NO se cumple'} → "
          f"{'la página pasa a B' if r1 and r2 else 'la página sigue con A'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
