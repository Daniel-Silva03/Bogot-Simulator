"""
tests/test_nivel_parecidas.py

Pruebas de src/experiments/nivel_parecidas.py con datos inventados: ninguna lee el banco.
Se ejecuta directo:  python tests/test_nivel_parecidas.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from src.experiments import nivel_parecidas as npar

FALLOS = []


def check(nombre, cuerpo):
    try:
        cuerpo()
    except Exception as e:                       # noqa: BLE001
        FALLOS.append((nombre, repr(e)))
        print(f"  FALLA  {nombre}\n         {e!r}")
    else:
        print(f"  ok     {nombre}")


def _t():
    """Dos temas con niveles muy distintos; textos que se parecen dentro de cada tema."""
    filas = []
    for i in range(6):
        filas.append({"id": f"c{i}", "familia": f"fc{i // 2}", "tema": "confianza",
                      "pregunta_pagina": f"¿Confía usted en la institución número {i}?", "total": 30 + i})
        filas.append({"id": f"s{i}", "familia": f"fs{i // 2}", "tema": "satisfaccion",
                      "pregunta_pagina": f"¿Está satisfecho con el servicio de parques {i}?", "total": 80 + i})
    return pd.DataFrame(filas)


def test_nunca_usa_la_propia_familia():
    t = _t()
    p = npar.predecir(t, npar.similitudes(t.pregunta_pagina.tolist()))
    fam = dict(zip(t.id, t.familia))
    for _, r in p.iterrows():
        assert all(fam[v] != fam[r.id] for v in r.vecinos), r.id
        otras = t[t.familia != fam[r.id]]
        assert abs(r.R0 - otras.total.mean()) < 1e-9


def test_el_tema_y_el_texto_aciertan_cuando_el_nivel_depende_del_tema():
    t = _t()
    p = npar.predecir(t, npar.similitudes(t.pregunta_pagina.tolist()), k=3)
    assert npar.eam(p, "R1") < 5 and npar.eam(p, "R2") < 5 < npar.eam(p, "R0")


def test_sin_tema_compartido_R1_es_el_promedio():
    t = _t()
    t.loc[0, "tema"] = "unico"
    p = npar.predecir(t, npar.similitudes(t.pregunta_pagina.tolist()))
    r = p[p.id == "c0"].iloc[0]
    assert r.R1 == r.R0


def test_los_empates_se_resuelven_por_id():
    t = pd.DataFrame([{"id": x, "familia": x, "tema": "a", "pregunta_pagina": "igual", "total": v}
                      for x, v in (("b", 10), ("a", 20), ("c", 30), ("d", 40))])
    p = npar.predecir(t, npar.similitudes(t.pregunta_pagina.tolist()), k=2)
    assert p[p.id == "d"].iloc[0].vecinos == ["a", "b"]


def test_la_lectura_es_la_pre_registrada():
    assert npar.lectura({"R0": 15, "R1": 12, "R2": 14}) == {"vara_parte_B": 12, "metodo_vara": "R1",
                                                           "metodo_gratis_que_sirve": ["R1"]}
    assert npar.lectura({"R0": 15, "R1": 12.1, "R2": 16})["metodo_gratis_que_sirve"] == []


if __name__ == "__main__":
    pruebas = [v for k, v in list(globals().items()) if k.startswith("test_")]
    print(f"Nivel por preguntas parecidas — {len(pruebas)} pruebas\n")
    for p in pruebas:
        check(p.__name__, p)
    print()
    if FALLOS:
        print(f"{len(FALLOS)} fallan de {len(pruebas)}")
        sys.exit(1)
    print(f"las {len(pruebas)} pasan")
