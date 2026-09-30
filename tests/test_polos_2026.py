"""
tests/test_polos_2026.py

Pruebas de src/experiments/polos_2026.py antes de abrir 2026
(`POLOS_2026_SPECIFICATION.md` §8). Usan la composición real y los polos reales
(2014–2022, ya publicados) con votos de Abelardo INVENTADOS: ninguna prueba toca
datos de 2026.
Se ejecuta directo:  python tests/test_polos_2026.py
"""

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.experiments import geografia_electoral as ge
from src.experiments import polos_2026 as pz

FALLOS = []
SEMILLAS = 200
N_PERM_MUNDOS = 500


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


logging.disable(logging.WARNING)
COMP = ge.composicion()
logging.disable(logging.NOTSET)
RES = pz.residuos_presidenciales()
LOCS = sorted(set(RES.index) - {ge.SUMAPAZ})
DER, IZQ, ULT = pz.polo(pz.DERECHA, RES), pz.polo(pz.IZQUIERDA, RES), RES[pz.ULTIMO]
RAZON = ge.razon_inscripcion()
X1 = COMP.loc[LOCS, "x1"].to_numpy()

# El tamaño del ruido de los mundos es el de los residuos reales de la derecha (§8).
S = float(np.median([RES.loc[LOCS, k].std(ddof=1) for k in pz.DERECHA]))
# La parte del estrato, la de Gutiérrez 2022 real (ajuste de M1): una derecha con
# un gradiente realista, sin tocar 2026.
_v = pd.read_csv(ge.ELECTORAL / "presidente_1v_localidad.csv")
_z = pd.read_csv(ge.ELECTORAL / "presidente_1v_zonas.csv")
_g = ge.proporciones(_v, _z).loc[LOCS, (2022, "gutierrez")].to_numpy()
BASE = _g - ge.residuos(_g, X1)

z = lambda s: ((s - s.mean()) / s.std(ddof=0)).loc[LOCS].to_numpy()   # noqa: E731
DZ, IZ, RZ = z(DER), z(IZQ), z(RAZON)


def mundo(rng, senal, peso=0.85):
    """Voto de Abelardo inventado: estrato + S·(peso·señal + ruido)."""
    e = rng.standard_normal(len(LOCS))
    resto = S * (peso * senal + np.sqrt(1 - peso ** 2) * e) if senal is not None else S * e
    return pd.Series(BASE + resto, index=LOCS)


def correr(prop, rng, n_perm=N_PERM_MUNDOS):
    a = pz.analizar(prop, COMP, DER, IZQ, ULT, RAZON, n_perm=n_perm, rng=rng)
    return a, pz.evaluar(a)


def tasas(senal, peso=0.85):
    rng = np.random.default_rng(1)
    out = [correr(mundo(rng, senal, peso), rng)[1] for _ in range(SEMILLAS)]
    lect = pd.Series([o["lectura"] for o in out]).value_counts(normalize=True)
    p2 = np.mean([o["predicciones"]["P2"]["se_cumple"] for o in out])
    return lect, p2


# --- el polo está congelado en el pre-registro (DI-P26-3) -------------------

TABLA_S4 = {1: 1.99, 19: 1.25, 14: 1.00, 11: 0.90, 5: 0.88, 2: 0.57, 7: 0.22, 12: 0.00,
            8: -0.13, 6: -0.19, 15: -0.22, 16: -0.25, 17: -0.46, 18: -0.48, 10: -0.59,
            9: -0.85, 4: -0.89, 3: -1.02, 13: -1.72}


def test_el_polo_es_el_de_la_tabla_del_pre_registro():
    malas = {l: (round(DER[l], 2), v) for l, v in TABLA_S4.items() if abs(round(DER[l], 2) - v) > 1e-9}
    assert not malas, malas


def test_la_tabla_del_documento_es_la_de_la_prueba():
    doc = (Path(__file__).resolve().parents[1] / "docs" / "POLOS_2026_SPECIFICATION.md").read_text(encoding="utf-8")
    for v in ("+1,99", "+1,25", "−1,72", "−1,02", "+0,57"):
        assert v in doc, v


def test_los_polos_son_los_descritos():
    """§3.2: cada residuo de derecha se parece a su promedio; los polos, a −0,70."""
    rs = [round(float(np.corrcoef(z(RES[k]), DZ)[0, 1]), 2) for k in pz.DERECHA]
    assert rs == [0.86, 0.96, 0.84], rs
    assert round(float(np.corrcoef(DZ, IZ)[0, 1]), 2) == -0.70


def test_la_escala_del_polo_no_cambia_las_cifras():
    """DI-P26-2."""
    rng = np.random.default_rng(3)
    prop = mundo(rng, DZ)
    a1 = pz.analizar(prop, COMP, DER, IZQ, ULT, RAZON, n_perm=50)
    a2 = pz.analizar(prop, COMP, DER * 7.3, IZQ * 0.2, ULT, RAZON, n_perm=50)
    for k in ("r_der", "r_izq", "delta_r2_loo"):
        assert a1[k] == a2[k], k


# --- el voto de 2026 (DI-P26-4) ---------------------------------------------

def _tabla(opciones):
    filas, zonas = [], []
    for c in range(1, 21):
        for i, o in enumerate(opciones):
            filas.append({"anio": 2026, "zona": c, "cod_loc": c, "clave": f"c{i}", "opcion": o,
                          "tipo": "candidato", "votos": 100 + 10 * i + c})
        zonas.append({"anio": 2026, "zona": c, "cod_loc": c,
                      "votos_candidatos": sum(100 + 10 * i + c for i in range(len(opciones)))})
    return pd.DataFrame(filas), pd.DataFrame(zonas)


def test_abelardo_se_encuentra_por_nombre():
    v, zz = _tabla(["Iván Pérez", "Abelardo de la Espriella", "Otra Persona"])
    p = pz.proporcion_abelardo(v, zz)
    assert len(p) == 20 and abs(p[1] - 111 / (101 + 111 + 121)) < 1e-12


def test_sin_abelardo_o_con_dos_se_detiene():
    for ops in (["Iván Pérez", "Otra Persona"], ["ABELARDO uno", "Abelardo dos"]):
        v, zz = _tabla(ops)
        try:
            pz.proporcion_abelardo(v, zz)
        except pz.PolosError:
            continue
        raise AssertionError(f"debió detenerse con {ops}")


def test_sin_2026_en_la_tabla_se_detiene():
    """Sin filas de 2026 no se calcula nada. *Corrección (30/09):* esta prueba
    llamaba a main() con la tabla real; cuando la tabla recibió 2026, la prueba
    corrió el análisis entero y escribió el resultado. Ahora usa la tabla real
    sin 2026, y ninguna prueba llama a main()."""
    try:
        pz.proporcion_abelardo(_v[_v.anio < 2026], _z[_z.anio < 2026])
    except pz.PolosError as e:
        assert "todavía" in str(e)
    else:
        raise AssertionError("debió detenerse")


def test_sumapaz_se_reporta_aparte():
    rng = np.random.default_rng(4)
    prop = pd.concat([mundo(rng, DZ), pd.Series({ge.SUMAPAZ: 0.1})])
    a = pz.analizar(prop, COMP, DER, IZQ, ULT, RAZON, n_perm=50)
    assert "sumapaz" in a and ge.SUMAPAZ not in a["localidades"] and len(a["localidades"]) == 19


def test_el_resultado_se_puede_escribir():
    rng = np.random.default_rng(5)
    a, v = correr(mundo(rng, DZ), rng, 50)
    json.dumps({**a, **v}, ensure_ascii=False)


def test_signos_cuenta_bien():
    prop = pd.Series(BASE, index=LOCS) + pd.Series(S * DZ, index=LOCS)
    a = pz.analizar(prop, COMP, DER, IZQ, ULT, RAZON, n_perm=50)
    assert a["signos"]["de"] == 19 and a["signos"]["aciertos"] >= 17, a["signos"]


# --- la regla (§7) -------------------------------------------------------------

def test_la_regla_lee_cada_caso():
    base = dict(r_der=0.8, p_der=0.001, r_izq=-0.5, r_ultimo=0.7, delta_r2_loo=0.1,
                r2_loo_m1=0.7, r_inscripcion=0.1)
    assert pz.evaluar(base)["lectura"] == "A"
    assert pz.evaluar({**base, "delta_r2_loo": 0.01})["lectura"] == "B"
    assert pz.evaluar({**base, "r_der": 0.3})["lectura"] == "C"
    assert pz.evaluar({**base, "r_inscripcion": -0.6})["lectura"] == "intermedio"
    assert "Sin P2" in pz.evaluar({**base, "r_izq": -0.9})["regla"]
    assert "Sin P4" in pz.evaluar({**base, "r_ultimo": 0.9})["regla"]


# --- los mundos simulados (§8) ----------------------------------------------

RESUMEN = {}


def test_mundo_con_polo_da_A():
    lect, p2 = tasas(DZ)
    RESUMEN["polo"] = (lect.to_dict(), p2)
    assert lect.get("A", 0) >= 0.80, lect.to_dict()


def test_mundo_sin_polo_da_C_y_casi_nunca_A():
    lect, _ = tasas(None)
    RESUMEN["sin polo"] = (lect.to_dict(), None)
    assert lect.get("C", 0) >= 0.80 and lect.get("A", 0) <= 0.05, lect.to_dict()


def test_mundo_espejo_falla_P2_mas_que_el_de_polo():
    _, p2_espejo = tasas(-IZ)
    _, p2_polo = tasas(DZ)
    RESUMEN["espejo"] = (None, p2_espejo)
    assert p2_espejo < p2_polo, (p2_espejo, p2_polo)


def test_mundo_de_inscripcion_da_intermedio():
    lect, _ = tasas(RZ, peso=0.95)
    RESUMEN["inscripción"] = (lect.to_dict(), None)
    assert lect.get("intermedio", 0) >= 0.95, lect.to_dict()


def main():
    print("Polos 2026 — pruebas antes de abrir 2026\n")
    for k, f in [(k, v) for k, v in list(globals().items()) if k.startswith("test_")]:
        check(k, f)
    print()
    for k, (lect, p2) in RESUMEN.items():
        print(f"  mundo {k:12s} lecturas {lect}  P2 {p2}")
    print()
    if FALLOS:
        print(f"{len(FALLOS)} prueba(s) fallaron")
        sys.exit(1)
    print("todas las pruebas pasaron")


if __name__ == "__main__":
    main()
